"""Production-ready WebSocket API for real-time sensor data streaming.

This module provides a WebSocket endpoint for:
1. ESP32 Microcontrollers: Send vehicle sensor data in JSON format
2. Angular Web Frontend: Receive live sensor streams
3. Mobile Applications: Real-time vehicle health monitoring

WebSocket Flow:
    ESP32 → /ws/live → PulseDrive Backend → All Connected Clients
    
Example Client Connections:
    - ESP32: ws://localhost:8000/ws/live?vehicleId=VH001
    - Angular: ws://localhost:8000/ws/live
    - React Native: ws://localhost:8000/ws/live
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.models.sensor import SensorData
from app.services.sensor_service import SensorService
from app.websocket.manager import manager
from app.models.prediction import PredictionRequest
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

sensor_service = SensorService()
prediction_service = PredictionService()

router = APIRouter(tags=["WebSocket"])



@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time vehicle sensor data streaming.
    
    This endpoint accepts connections from:
    1. **ESP32 Microcontrollers** - Send sensor packets
    2. **Web/Mobile Clients** - Receive sensor streams
    
    Connection Flow:
    1. Client (ESP32 or Web) connects to /ws/live
    2. Server accepts connection
    3. For ESP32: Send sensor data as JSON
    4. For Web Clients: Receive broadcasted data
    5. Server broadcasts to all connected clients
    6. Safe disconnection on errors
    
    Expected Sensor Packet Format (from ESP32):
    {
        "vehicleId": "VH001",          # Vehicle identifier (required)
        "rpm": 3000,                    # Engine RPM (sensor)
        "temperature": 85.5,            # Engine temperature (sensor)
        "mileage": 45000,               # Total mileage (sensor)
        "fuel_consumption": 8.5,        # Fuel consumption rate (sensor)
        "battery_voltage": 13.5,        # Battery voltage (sensor)
        "status": "active",             # Vehicle status (sensor)
        "timestamp": "2026-07-17T21:48:48Z"  # When data was collected
    }
    
    Response Broadcast (to all clients):
    {
        "source": "ESP32_VH001",        # Which device sent this
        "data": {...},                  # Original sensor data
        "received_at": "2026-07-17T21:48:48Z",  # When backend received it
        "type": "sensor_update"         # Message type for client filtering
    }
    
    Args:
        websocket: FastAPI WebSocket connection
        
    Raises:
        WebSocketDisconnect: When client disconnects (handled gracefully)
    """
    # Accept the WebSocket connection
    await manager.connect(websocket)

    logger.info(
        f"New WebSocket connection established. "
        f"Total connections: {manager.get_active_connections_count()}"
    )

    # Send a welcome message to the connecting client
    welcome_message = {
        "type": "connection_established",
        "message": "Connected to PulseDrive live sensor stream",
        "server_time": datetime.utcnow().isoformat(),
        "active_connections": manager.get_active_connections_count(),
    }
    await manager.send_personal_message(welcome_message, websocket)

    try:
        # Main loop: receive and broadcast sensor data
        while True:
            # Receive JSON data from the client
            # This can be:
            # - Sensor data from ESP32
            # - Commands from Web clients
            # - Heartbeat/ping messages
            data = await websocket.receive_json()

            # Log received data for debugging
            logger.debug(f"Received data: {data}")

            sensor_data, validation_errors = _validate_sensor_packet(data)
            if validation_errors is not None:
                await manager.send_personal_message(
                    _build_validation_error_message(validation_errors),
                    websocket,
                )
                continue

            try:
                await asyncio.to_thread(
                    sensor_service.save_sensor_data,
                    sensor_data,
                )
            except Exception as save_error:
                logger.warning(
                    f"MongoDB save failed (non-critical, pipeline continues): {save_error}"
                )
                # Do NOT continue — let the AI pipeline run even without DB persistence

            # Build the broadcast message with metadata
            broadcast_message = _build_broadcast_message(data)

            logger.info(
                f"Broadcasting sensor data from {broadcast_message.get('source', 'unknown')} "
                f"to {manager.get_active_connections_count()} clients"
            )

            # Broadcast to all connected clients
            # This includes other ESP32s, web clients, mobile apps, etc.
            await manager.broadcast(broadcast_message)

            # Trigger AI Prediction Pipeline asynchronously so it doesn't block the sensor stream
            try:
                pred_req = PredictionRequest(
                    vehicleId=sensor_data.vehicleId,
                    features=data
                )
                asyncio.create_task(prediction_service.predict(pred_req))
            except Exception as pred_err:
                logger.error(f"Failed to trigger AI prediction on websocket packet: {pred_err}")

    except WebSocketDisconnect:
        # Client disconnected gracefully or due to connection loss
        manager.disconnect(websocket)

        logger.info(
            f"WebSocket client disconnected. "
            f"Remaining connections: {manager.get_active_connections_count()}"
        )

        # Notify remaining clients about the disconnection
        disconnection_notice = {
            "type": "client_disconnected",
            "message": "A client has disconnected from the stream",
            "active_connections": manager.get_active_connections_count(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await manager.broadcast(disconnection_notice)

    except Exception as e:
        # Unexpected error
        logger.error(f"WebSocket error: {e}", exc_info=True)

        # Safely disconnect
        try:
            manager.disconnect(websocket)
        except Exception as disconnect_error:
            logger.error(f"Error during disconnect cleanup: {disconnect_error}")


@router.get("/ws/status", tags=["WebSocket"])
async def websocket_status() -> Dict[str, Any]:
    """Get the current WebSocket connection status.
    
    This endpoint is useful for monitoring and debugging:
    - How many clients are currently connected
    - Server health status
    - Last update time
    
    Example Response:
    {
        "status": "healthy",
        "active_connections": 5,
        "timestamp": "2026-07-17T21:48:48Z",
        "message": "WebSocket server is running with 5 active connections"
    }
    
    Returns:
        Dictionary with connection status information
    """
    connection_count = manager.get_active_connections_count()

    status_response = {
        "status": "healthy" if connection_count >= 0 else "unhealthy",
        "active_connections": connection_count,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"WebSocket server is running with {connection_count} active connection(s)",
    }

    logger.info(f"Status check: {status_response}")

    return status_response


def _validate_sensor_packet(
    raw_data: Any,
) -> tuple[SensorData | None, list[dict[str, Any]] | None]:
    """Validate incoming WebSocket payload against the SensorData schema."""
    if not isinstance(raw_data, dict):
        return None, [{"type": "type_error", "msg": "Sensor packet must be a JSON object"}]

    try:
        return SensorData.model_validate(raw_data), None
    except ValidationError as error:
        return None, error.errors()


def _build_validation_error_message(
    errors: list[dict[str, Any]],
) -> Dict[str, Any]:
    """Build a client-facing validation error payload."""
    return {
        "type": "validation_error",
        "message": "Invalid sensor packet",
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _build_broadcast_message(raw_data: Any) -> Dict[str, Any]:
    """Build a properly formatted broadcast message from raw sensor data.
    
    This helper function:
    1. Extracts source information
    2. Adds server timestamp
    3. Tags message type
    4. Handles various input formats
    
    Args:
        raw_data: Raw data received from client (typically dict or list)
        
    Returns:
        Properly formatted broadcast message with metadata
    """
    if not isinstance(raw_data, dict):
        logger.warning(f"Non-dict data received: {type(raw_data)}")
        raw_data = {"raw_data": raw_data}

    # Extract vehicle ID or source identifier
    source = raw_data.get("vehicleId", raw_data.get("source", "unknown"))

    # Build broadcast message with metadata
    broadcast_message = {
        "type": "sensor_update",
        "source": source,
        "data": raw_data,
        "received_at": datetime.utcnow().isoformat(),
    }

    return broadcast_message


# Export the connection manager for use in other modules
__all__ = ["router", "manager", "websocket_endpoint", "websocket_status"]
