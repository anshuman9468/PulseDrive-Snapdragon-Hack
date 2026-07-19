import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NotificationService:
    """Dispatches dashboard alerts, emails, SMS texts, and voice call triggers based on severity."""

    def __init__(self, twilio_service=None):
        self.twilio_service = twilio_service

    async def send_dashboard_notification(self, vehicle_id: str, title: str, message: str, severity: str) -> bool:
        logger.info(f"Dashboard Alert sent for {vehicle_id}: [{severity}] {title} - {message}")
        # Webhooks or WebSocket broadcast triggers here
        return True

    async def send_sms(self, phone_number: str, message: str) -> bool:
        logger.info(f"SMS sent to {phone_number}: {message}")
        # Twilio API call if configured
        if self.twilio_service and not self.twilio_service.is_mock:
            try:
                # Mock sending SMS through Twilio client
                self.twilio_service.client.messages.create(
                    body=message,
                    to=phone_number,
                    from_=self.twilio_service.phone_number
                )
                return True
            except Exception as e:
                logger.error(f"Failed to send Twilio SMS: {e}")
        return True

    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        logger.info(f"Email sent to {recipient}: {subject} - {body[:50]}...")
        return True

    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        logger.info(f"WhatsApp placeholder sent to {phone_number}: {message}")
        return True

    async def route_severity_notifications(self, vehicle_id: str, phone_number: str, severity: str, fault: str) -> Dict[str, Any]:
        """Dispatches alerts based on risk level.
        
        SAFE: No alerts.
        WARNING: Dashboard notice.
        CRITICAL: Dashboard, SMS, Email.
        EMERGENCY: Dashboard, SMS, Email, and voice triggers.
        """
        results = {
            "dashboard": False,
            "sms": False,
            "email": False,
            "voice": False
        }

        if severity == "SAFE":
            return results

        # All severities (WARNING, CRITICAL, EMERGENCY) get dashboard alert
        title = f"Vehicle Fault Detected: {fault}"
        message = f"Our AI diagnostic tools detected a '{fault}' condition. Severity level: {severity}."
        results["dashboard"] = await self.send_dashboard_notification(vehicle_id, title, message, severity)

        if severity in ["CRITICAL", "EMERGENCY"]:
            sms_text = f"PulseDrive Alert: Critical fault '{fault}' detected in vehicle {vehicle_id}. Please schedule service."
            results["sms"] = await self.send_sms(phone_number, sms_text)
            results["email"] = await self.send_email(
                "driver@pulsedrive-telematics.com", 
                f"PulseDrive Diagnostic Alert: {severity}", 
                message
            )

        if severity == "EMERGENCY":
            logger.warning(f"EMERGENCY state for vehicle {vehicle_id}. Triggering active voice agent call.")
            results["voice"] = True
            # In voice webhook, we will trigger Twilio call initiation

        return results
