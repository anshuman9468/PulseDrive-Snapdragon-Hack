import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TwilioService:
    """Service wrapper for Twilio Outbound Voice Call integration."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not self.account_sid or not self.auth_token or not self.phone_number:
            logger.warning("Twilio configuration is missing. TwilioService will run in MOCK mode.")
            self.is_mock = True
        else:
            self.is_mock = False
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.warning("Twilio python library not installed. TwilioService will run in MOCK mode.")
                self.is_mock = True

    async def initiate_call(self, to_phone: str, webhook_url: str) -> Optional[str]:
        """Trigger an outbound call using Twilio Voice API.
        
        Args:
            to_phone: The recipient E.164 phone number
            webhook_url: TwiML response voice handler endpoint
            
        Returns:
            The call SID string if successful, else None
        """
        if self.is_mock:
            mock_sid = "CA" + os.urandom(16).hex()
            logger.info(f"Twilio Outbound call (mock) initiated: to {to_phone}, webhook {webhook_url}, SID: {mock_sid}")
            return mock_sid

        try:
            call = self.client.calls.create(
                to=to_phone,
                from_=self.phone_number,
                url=webhook_url
            )
            logger.info(f"Twilio Outbound call initiated successfully: SID {call.sid}")
            return call.sid
        except Exception as e:
            logger.error(f"Twilio call initiation failed: {e}")
            return None

    def generate_twiml_response(self, prompt_text: str, gather_webhook_url: str) -> str:
        """Helper to generate TwiML XML markup for Twilio voice interaction.
        
        It says the prompt_text and gathers speech input from the user.
        """
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{prompt_text}</Say>
    <Gather input="speech" action="{gather_webhook_url}" method="POST" speechTimeout="auto">
        <Say voice="alice">Please speak after the tone.</Say>
    </Gather>
</Response>"""
        return twiml

    def generate_twiml_stream(self, stream_url: str) -> str:
        """TwiML for bi-directional WebSocket audio streaming (advanced Qualcomm Snapdragon/Twilio setup)."""
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="{stream_url}" />
    </Start>
    <Say>Connecting audio stream...</Say>
    <Pause length="30" />
</Response>"""
        return twiml
