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
        """Read the latest sensor document and build dashboard payload."""
        document: dict[str, Any] | None = self.collection.find_one(
            sort=[("timestamp", DESCENDING)]
        )
        if document is None:
            return None

        dashboard_payload: dict[str, Any] = {
            "vehicleId": document.get("vehicleId"),
            "temperature": document.get("temperature"),
            "voltage": document.get("voltage"),
            "gps": document.get("gps", {}),
            "mpu6050": document.get("mpu6050", {}),
            "timestamp": document.get("timestamp"),
            "healthScore": 92,
            "status": "Healthy",
            "remainingUsefulLife": 84,
            "aiDiagnosis": {
                "message": "Bearing wear detected",
                "confidence": 96,
                "recommendation": "Schedule maintenance within 48 hours",
            },
            "edgeAI": {
                "runtime": "Local",
                "latency": 12,
                "status": "Active",
            },
            "connectivity": {
                "esp32": True,
                "websocket": True,
            },
        }

        return DashboardData(**dashboard_payload)
