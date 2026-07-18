import logging
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time sensor data streaming.
    
    This manager handles:
    - Multiple concurrent WebSocket connections
    - Broadcasting sensor packets to all connected clients
    - Safe disconnection handling
    - Personal messages to specific clients
    
    Supported Client Types:
    - ESP32 Microcontrollers: Send sensor data as JSON packets
    - Angular Web Frontend: Receive and display sensor streams
    - Mobile Apps: Real-time vehicle health monitoring
    """

    def __init__(self) -> None:
        """Initialize the connection manager with an empty active connections list."""
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a WebSocket connection and add it to active connections.
        
        This method is called when a new client (ESP32, web client, etc.) 
        establishes a WebSocket connection to the /ws/live endpoint.
        
        Args:
            websocket: FastAPI WebSocket connection object
            
        Raises:
            Exception: If websocket acceptance fails
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket from active connections.
        
        This method is called when a client disconnects, either gracefully
        or due to a network error. It safely removes the connection without
        raising exceptions if the connection is already gone.
        
        Args:
            websocket: FastAPI WebSocket connection object to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")
        else:
            logger.warning("Attempted to disconnect a client that is not in active connections")

    async def send_personal_message(
        self,
        message: Dict[str, Any],
        websocket: WebSocket,
    ) -> None:
        """Send a message to a specific client (personal message).
        
        This method sends a message to only one connected client, useful for:
        - Sending acknowledgments to specific clients
        - Sending configuration updates to specific devices
        - Sending error messages to specific connections
        
        Args:
            message: Dictionary message to send (will be JSON serialized)
            websocket: Target WebSocket connection
            
        Raises:
            Exception: If sending fails (connection may have closed)
        """
        try:
            await websocket.send_json(message)
            logger.debug(f"Personal message sent to client: {message}")
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected clients.
        
        This is the main method for distributing sensor data from ESP32 
        microcontrollers to all connected Angular clients and other subscribers.
        
        The method safely handles disconnections during broadcast - if one client
        is no longer connected, it's removed and broadcasting continues to others.
        
        Args:
            message: Dictionary message to broadcast (will be JSON serialized)
                    Typically contains sensor data like:
                    {
                        "vehicleId": "VH001",
                        "rpm": 3000,
                        "temperature": 85,
                        "timestamp": "2026-07-17T21:48:48Z"
                    }
        """
        # Create a list of connections to remove (disconnected ones)
        disconnected_clients = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # Connection is no longer valid, mark for removal
                logger.warning(f"Error broadcasting to client: {e}. Removing connection.")
                disconnected_clients.append(connection)

        # Remove all disconnected clients in a batch
        for connection in disconnected_clients:
            self.disconnect(connection)

        if len(disconnected_clients) > 0:
            logger.info(f"Removed {len(disconnected_clients)} disconnected clients during broadcast")

    def get_active_connections_count(self) -> int:
        """Get the current number of active connections.
        
        Useful for monitoring and logging.
        
        Returns:
            Number of currently connected clients
        """
        return len(self.active_connections)

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about connected clients.
        
        Returns:
            Dictionary with connection statistics
        """
        return {
            "active_connections": len(self.active_connections),
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
