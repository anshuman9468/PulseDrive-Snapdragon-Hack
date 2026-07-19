import os
import re
import logging
import urllib.parse
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)

class OutboundCallService:
    def __init__(self):
        # Initialize using environment variables only
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.public_base_url = os.getenv("PUBLIC_BASE_URL")

        if not self.account_sid or not self.auth_token or not self.phone_number or not self.public_base_url:
            logger.warning("OutboundCallService: One or more Twilio/Public URL environment variables are missing.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio Client: {e}")
                self.client = None

    async def start_call(
        self,
        phone_number: str,
        vehicle_id: str,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiates an outbound Twilio call.
        """
        logger.info(
            f"Call Attempt - Destination: {phone_number}, Vehicle ID: {vehicle_id}, Booking ID: {booking_id}"
        )

        # Validate phone number using E.164 format. Reject invalid phone numbers.
        if not phone_number or not re.match(r"^\+[1-9]\d{1,14}$", phone_number):
            err_msg = f"Invalid phone number format: '{phone_number}'. Must be E.164 format (e.g., +91XXXXXXXXXX)."
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "status": "failed",
                "phone_number": phone_number
            }

        # Check configuration
        if not self.account_sid or not self.auth_token or not self.phone_number or not self.public_base_url:
            err_msg = "Twilio credentials or configuration missing in environment variables"
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "status": "failed",
                "phone_number": phone_number
            }

        try:
            if not self.client:
                # Attempt to initialize client if variables are present now
                self.client = Client(self.account_sid, self.auth_token)

            encoded_vehicle_id = urllib.parse.quote(vehicle_id)
            encoded_phone_number = urllib.parse.quote(phone_number)
            url = f"{self.public_base_url}/api/service/voice/twiml?vehicle_id={encoded_vehicle_id}&phone_number={encoded_phone_number}"
            
            logger.info(f"Creating call via Twilio: to={phone_number}, from={self.phone_number}, url={url}")
            
            call = self.client.calls.create(
                to=phone_number,
                from_=self.phone_number,
                url=url
            )
            
            logger.info(
                f"Call Started: Call SID={call.sid}, Destination={phone_number}, VehicleID={vehicle_id}, BookingID={booking_id}"
            )
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "phone_number": phone_number
            }
        except TwilioException as te:
            err_msg = f"Twilio API Exception: {te}"
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "status": "failed",
                "phone_number": phone_number
            }
        except Exception as e:
            err_msg = f"Unexpected exception in outbound call: {e}"
            logger.error(err_msg)
            return {
                "success": False,
                "error": err_msg,
                "status": "failed",
                "phone_number": phone_number
            }
