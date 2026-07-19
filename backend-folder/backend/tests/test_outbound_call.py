import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Adjust paths to match package structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from service_concierge.services.outbound_call_service import OutboundCallService

class TestOutboundCall(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "TWILIO_ACCOUNT_SID": "ACtestaccount",
            "TWILIO_AUTH_TOKEN": "testauthtoken",
            "TWILIO_PHONE_NUMBER": "+18027888954",
            "PUBLIC_BASE_URL": "https://difficult-breach-sadness.ngrok-free.dev"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("service_concierge.services.outbound_call_service.Client")
    async def test_start_call_success(self, mock_twilio_client):
        # Setup mock Twilio call response
        mock_call = MagicMock()
        mock_call.sid = "CA1234567890abcdef"
        mock_call.status = "queued"
        
        mock_client_instance = MagicMock()
        mock_client_instance.calls.create.return_value = mock_call
        mock_twilio_client.return_value = mock_client_instance

        # Instantiate service (will load from mocked env)
        service = OutboundCallService()
        
        # Trigger call
        response = await service.start_call(
            phone_number="+919876543210",
            vehicle_id="ESP32-DEV-100",
            booking_id="booking-123"
        )
        
        self.assertTrue(response["success"])
        self.assertEqual(response["call_sid"], "CA1234567890abcdef")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(response["phone_number"], "+919876543210")
        
        # Verify twilio call creation parameters
        mock_client_instance.calls.create.assert_called_once_with(
            to="+919876543210",
            from_="+18027888954",
            url="https://difficult-breach-sadness.ngrok-free.dev/api/service/voice/twiml?vehicle_id=ESP32-DEV-100&phone_number=%2B919876543210"
        )

    async def test_start_call_invalid_phone(self):
        service = OutboundCallService()
        
        # Test invalid phone format
        response = await service.start_call(
            phone_number="9876543210", # Missing +
            vehicle_id="ESP32-DEV-100"
        )
        self.assertFalse(response["success"])
        self.assertIn("Invalid phone number format", response["error"])

    @patch("service_concierge.services.outbound_call_service.Client")
    async def test_start_call_twilio_exception(self, mock_twilio_client):
        from twilio.base.exceptions import TwilioException
        
        mock_client_instance = MagicMock()
        mock_client_instance.calls.create.side_effect = TwilioException("Twilio error message")
        mock_twilio_client.return_value = mock_client_instance

        service = OutboundCallService()
        response = await service.start_call(
            phone_number="+919876543210",
            vehicle_id="ESP32-DEV-100"
        )
        self.assertFalse(response["success"])
        self.assertIn("Twilio API Exception", response["error"])

    @patch("service_concierge.services.outbound_call_service.OutboundCallService.start_call")
    def test_api_endpoint_success(self, mock_start_call):
        # Mock start_call async method response
        async def mock_start_call_coro(phone_number, vehicle_id, booking_id=None):
            return {
                "success": True,
                "call_sid": "CAmockedapi123",
                "status": "queued",
                "phone_number": phone_number
            }
        mock_start_call.side_effect = mock_start_call_coro

        # Test POST API request
        response = self.client.post(
            "/api/service/voice/start-call",
            json={
                "vehicle_id": "ESP32-DEV-100",
                "phone_number": "+919876543210"
            }
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "success")
        self.assertEqual(json_data["call_sid"], "CAmockedapi123")
        self.assertEqual(json_data["phone_number"], "+919876543210")

    def test_api_endpoint_invalid_phone(self):
        # Test validation error at endpoint level
        response = self.client.post(
            "/api/service/voice/start-call",
            json={
                "vehicle_id": "ESP32-DEV-100",
                "phone_number": "12345"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid phone number format", response.json()["detail"])

    @patch("service_concierge.services.outbound_call_service.OutboundCallService.start_call")
    def test_api_endpoint_internal_error(self, mock_start_call):
        # Mock start_call failure
        async def mock_start_call_coro(phone_number, vehicle_id, booking_id=None):
            return {
                "success": False,
                "error": "Twilio account suspended",
                "status": "failed",
                "phone_number": phone_number
            }
        mock_start_call.side_effect = mock_start_call_coro

        response = self.client.post(
            "/api/service/voice/start-call",
            json={
                "vehicle_id": "ESP32-DEV-100",
                "phone_number": "+919876543210"
            }
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Twilio account suspended", response.json()["detail"])

if __name__ == '__main__':
    unittest.main()
