import logging
from typing import Dict, Any, Optional

from service_concierge.services.booking_service import BookingService
from service_concierge.utils.constants import *

logger = logging.getLogger(__name__)

class AlertAgent:
    """Consumes Decision Engine risk and fault diagnostics to trigger Service Concierge workflows."""

    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    async def evaluate_decision_engine_output(self, decision_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Invoked when the Decision Engine publishes a new result.
        
        Evaluates risk score and triggers booking recommend.
        Expected schema in decision_payload:
        {
            "vehicleId": "ESP32-001",
            "risk_score": 85.2,
            "decision": "Emergency pull-over immediately",
            "severity": "EMERGENCY",
            "fault": "Engine Overheating"
        }
        """
        vehicle_id = decision_payload.get("vehicleId")
        risk_score = decision_payload.get("risk_score", 0.0)
        severity = decision_payload.get("severity", SEVERITY_SAFE)
        fault = decision_payload.get("fault", "Diagnostic Anomaly")

        if not vehicle_id:
            logger.warning("Decision payload missing vehicleId. Ignoring.")
            return None

        # Phone mapping logic (could retrieve from MongoDB user database, defaulting here)
        phone_number = "+919999988888"

        logger.info(f"AlertAgent evaluating vehicle {vehicle_id} (severity: {severity}, risk: {risk_score}%)")

        if severity == SEVERITY_SAFE:
            return {
                "action": "NONE",
                "booking_id": None
            }

        # Trigger booking service recommendations
        booking = await self.booking_service.recommend_service(
            vehicle_id=vehicle_id,
            severity=severity,
            phone_number=phone_number,
            fault=fault
        )

        return {
            "action": "BOOKING_RECOMMENDED" if booking else "NONE",
            "booking_id": booking.id if booking else None,
            "severity": severity
        }
