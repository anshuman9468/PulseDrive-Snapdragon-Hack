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

        temperature = float(document.get("temperature", 0))
        voltage = float(document.get("voltage", 12.5))

        # -------------------------
        # Health Calculation
        # -------------------------

        if temperature >= 90 or voltage < 10.5:
            health_score = 35
            status = "Critical"
            rul = 10

            diagnosis = {
                "message": "Critical engine condition detected.",
                "confidence": 99,
                "recommendation": "Stop the vehicle immediately and inspect the engine & battery.",
            }

        elif temperature >= 75 or voltage < 11.5:
            health_score = 68
            status = "Warning"
            rul = 35

            diagnosis = {
                "message": "Vehicle health is degrading.",
                "confidence": 95,
                "recommendation": "Schedule maintenance within 48 hours.",
            }

        else:
            health_score = 95
            status = "Healthy"
            rul = 90

            diagnosis = {
                "message": "Vehicle is operating normally.",
                "confidence": 98,
                "recommendation": "No maintenance required.",
            }

        dashboard_payload: dict[str, Any] = {
            "vehicleId": document.get("vehicleId"),
            "temperature": temperature,
            "voltage": voltage,
            "gasSensor": document.get("gasSensor", {}),
            "gps": document.get("gps", {}),
            "mpu1": document.get("mpu1", {}),
            "mpu2": document.get("mpu2", {}),
            "timestamp": document.get("timestamp"),

            "healthScore": health_score,
            "status": status,
            "remainingUsefulLife": rul,
            "aiDiagnosis": diagnosis,

            "edgeAI": document.get("edgeAI") or {
                "runtime": "Local",
                "latency": 12,
                "status": "Active",
            },

            "connectivity": document.get("connectivity") or {
                "esp32": True,
                "websocket": True,
            },
        }

        return DashboardData(**dashboard_payload)