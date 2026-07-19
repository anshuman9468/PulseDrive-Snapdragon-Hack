import asyncio
import unittest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service_concierge.container import container
from service_concierge.utils.constants import *

class TestServiceConcierge(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Reset container or repository state if in-memory
        container.repository.is_connected = False
        container.repository._mem_bookings.clear()
        container.repository._mem_appointments.clear()
        container.repository._mem_conversations.clear()

    def test_location_distance_calculation(self):
        # Test Noida to Delhi coords distance
        # Noida Sector 62: 28.6273, 77.3725
        # Delhi Connaught Place: 28.6304, 77.2177
        dist = container.location_service.calculate_haversine_distance(
            28.6273, 77.3725, 28.6304, 77.2177
        )
        self.assertGreater(dist, 10.0) # > 10 km
        self.assertLess(dist, 20.0)    # < 20 km

    def test_find_nearest_service_center(self):
        # Coordinate close to Noida Sector 62
        nearest = container.location_service.find_nearest_service_center(28.627, 77.37)
        self.assertEqual(nearest["id"], "SC-001")
        self.assertTrue("Noida" in nearest["name"])

    def test_calendar_service(self):
        # Validate holiday day vs normal weekday
        is_normal = container.calendar_service.is_working_day("2026-07-20") # Monday
        self.assertTrue(is_normal)
        
        is_xmas = container.calendar_service.is_working_day("2026-12-25") # Christmas
        self.assertFalse(is_xmas)

    async def test_end_to_end_booking_flow(self):
        vehicle_id = "ESP32-TEST"
        phone = "+919999988888"
        
        # 1. Trigger Booking Service Recommendation
        booking = await container.booking_service.recommend_service(
            vehicle_id=vehicle_id,
            severity=SEVERITY_WARNING,
            phone_number=phone,
            fault="Battery Overheating"
        )
        
        self.assertIsNotNone(booking)
        self.assertEqual(booking.vehicle_id, vehicle_id)
        self.assertEqual(booking.booking_status, STATUS_PENDING)
        self.assertEqual(booking.decision_severity, SEVERITY_WARNING)

        # 2. Select Location
        updated = await container.booking_service.update_booking_location(
            booking_id=booking.id,
            location_name="Noida Center Area",
            lat=28.6273,
            lng=77.3725
        )
        self.assertEqual(updated.assigned_service_center, "PulseDrive Care - Noida Sector 62")

        # 3. Select Date
        tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        updated = await container.booking_service.select_date(booking.id, tomorrow_str)
        self.assertEqual(updated.preferred_date, tomorrow_str)

        # 4. Confirm Time slot
        confirmed = await container.booking_service.select_time_and_confirm(booking.id, "10:00")
        self.assertIsNotNone(confirmed)
        self.assertEqual(confirmed.booking_status, STATUS_CONFIRMED)
        self.assertEqual(confirmed.preferred_time, "10:00")
        
        # 5. Check appointment persistence
        appt = container.repository.get_appointment_by_booking(booking.id)
        self.assertIsNotNone(appt)
        self.assertEqual(appt.status, "SCHEDULED")

    async def test_conversation_agent_dialogue_flow(self):
        vehicle_id = "ESP32-CONV-TEST"
        phone = "+918888877777"

        # 1. Start flow/get conversation
        conv = await container.conversation_agent.get_or_create_conversation(vehicle_id, phone)
        self.assertEqual(conv.state.current_node, "INIT")
        self.assertTrue(conv.state.is_active)
        self.assertGreater(len(conv.history), 0)

        # 2. Say Yes to initiate slot filling
        reply = await container.conversation_agent.process_turn(conv.id, "Yes, please schedule it.")
        updated_conv = container.repository.get_conversation(conv.id)
        self.assertEqual(updated_conv.state.current_node, "ASK_LOCATION")
        self.assertTrue(any(word in reply.lower() for word in ["location", "city", "address", "center"]))


        # 3. Provide location Noida
        reply = await container.conversation_agent.process_turn(conv.id, "I am in Noida Sector 62")
        updated_conv = container.repository.get_conversation(conv.id)
        self.assertEqual(updated_conv.state.current_node, "ASK_DATE")
        self.assertTrue("noida sector 62" in updated_conv.state.collected_data.get("service_center", "").lower())

        # 4. Provide date tomorrow
        reply = await container.conversation_agent.process_turn(conv.id, "Tomorrow please")
        updated_conv = container.repository.get_conversation(conv.id)
        self.assertEqual(updated_conv.state.current_node, "ASK_TIME")

        # 5. Select time slot 10 AM
        reply = await container.conversation_agent.process_turn(conv.id, "10 AM is perfect")
        updated_conv = container.repository.get_conversation(conv.id)
        self.assertEqual(updated_conv.state.current_node, "ASK_CONFIRM")

        # 6. Say Yes to confirm booking
        reply = await container.conversation_agent.process_turn(conv.id, "Yes, confirm it")
        updated_conv = container.repository.get_conversation(conv.id)
        self.assertEqual(updated_conv.state.current_node, "CONFIRMED")
        self.assertFalse(updated_conv.state.is_active)
        
        # Verify booking confirmed in repository
        booking = container.repository.get_booking(updated_conv.booking_id)
        self.assertEqual(booking.booking_status, STATUS_CONFIRMED)

    async def test_alert_agent_evaluates_correctly(self):
        # Emergency fault scenario
        payload = {
            "vehicleId": "ESP32-ALERT-TEST",
            "risk_score": 98.5,
            "decision": "Emergency pull-over immediately",
            "severity": "EMERGENCY",
            "fault": "Engine Overheating"
        }
        
        result = await container.alert_agent.evaluate_decision_engine_output(payload)
        self.assertEqual(result["action"], "BOOKING_RECOMMENDED")
        self.assertEqual(result["severity"], "EMERGENCY")
        
        # Safe scenario
        payload_safe = {
            "vehicleId": "ESP32-ALERT-TEST-2",
            "risk_score": 5.0,
            "decision": "Vehicle operates normally",
            "severity": "SAFE",
            "fault": "None"
        }
        result_safe = await container.alert_agent.evaluate_decision_engine_output(payload_safe)
        self.assertEqual(result_safe["action"], "NONE")

if __name__ == "__main__":
    unittest.main()
