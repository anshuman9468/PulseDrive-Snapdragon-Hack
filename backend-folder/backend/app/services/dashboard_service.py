from typing import Any, Optional

from pymongo import DESCENDING
from pymongo.collection import Collection

from app.config.database import get_database
from app.models.dashboard import DashboardData


class DashboardService:
    """Service layer for dashboard data retrieval."""

    def __init__(self) -> None:
        self.collection: Collection = get_database()["sensor_data"]

    def get_latest_dashboard(self) -> Optional[DashboardData]:
        """Read latest sensor document and generate dashboard dynamically."""

        document: dict[str, Any] | None = self.collection.find_one(
            sort=[("timestamp", DESCENDING)]
        )

        if document is None:
            return None

        # Fetch the latest prediction to populate AI fields
        predictions_collection = get_database()["predictions"]
        latest_pred = predictions_collection.find_one(
            {"vehicleId": document.get("vehicleId")},
            sort=[("timestamp", DESCENDING)]
        )

        health_score = 92
        status = "Healthy"
        ai_msg = "No active issues detected"
        ai_conf = 100
        ai_rec = "Continue regular maintenance schedule"
        ai_runtime = "CPU Fallback"
        ai_latency = 12

        if latest_pred:
            health_score = int(latest_pred.get("healthScore", 92))
            status = latest_pred.get("status", "Healthy").capitalize()
            ai_msg = latest_pred.get("primaryFault") or "No active issues detected"
            ai_conf = int(latest_pred.get("confidence", 1.0) * 100)
            ai_rec = latest_pred.get("recommendation") or "Continue regular maintenance schedule"
            
            # Extract runtime and latency from execution context
            exec_ctx = latest_pred.get("executionContext") or {}
            ai_latency = int(exec_ctx.get("executionTimeMs") or exec_ctx.get("pipelineLatencyMs") or 12)
            
            # Find a non-CPU backend if used by any agent
            agent_results = latest_pred.get("agentResults") or []
            backends = [r.get("runtime_used") for r in agent_results if r.get("runtime_used") and r.get("runtime_used") != "CPU Fallback"]
            if backends:
                ai_runtime = backends[0]
            elif latest_pred.get("deviceUsed") == "Snapdragon NPU":
                ai_runtime = "Qualcomm QNN"
            else:
                ai_runtime = "ONNX / TFLite (CPU)"

        # Calculate remaining useful life based on health score
        rul = max(10, int(health_score * 0.9))

        dashboard_payload: dict[str, Any] = {
            "vehicleId": document.get("vehicleId"),
            "temperature": document.get("temperature", 0.0),
            "voltage": document.get("voltage", document.get("battery_voltage", 0.0)),
            "gps": document.get("gps", {"latitude": 0.0, "longitude": 0.0}),
            "mpu6050": document.get("mpu6050", {"ax": 0.0, "ay": 0.0, "az": 0.0, "gx": 0.0, "gy": 0.0, "gz": 0.0}),
            "timestamp": document.get("timestamp"),
            "healthScore": health_score,
            "status": status,
            "remainingUsefulLife": rul,
            "aiDiagnosis": {
                "message": ai_msg,
                "confidence": ai_conf,
                "recommendation": ai_rec,
            },
            "edgeAI": {
                "runtime": ai_runtime,
                "latency": ai_latency,
                "status": "Active",
            },
            "connectivity": document.get("connectivity") or {
                "esp32": True,
                "websocket": True,
            },
        }

        return DashboardData(**dashboard_payload)