import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from service_concierge.repository.booking_repository import BookingRepository
from service_concierge.services.booking_service import BookingService
from service_concierge.services.sarvam_service import SarvamService
from service_concierge.models.conversation import Conversation, ConversationState, Message
from service_concierge.utils.constants import *

logger = logging.getLogger(__name__)

class ConversationAgent:
    """Dialogue agent that manages booking slot-filling and conversation state flow."""

    def __init__(
        self,
        repository: BookingRepository,
        booking_service: BookingService,
        sarvam_service: SarvamService
    ):
        self.repository = repository
        self.booking_service = booking_service
        self.sarvam_service = sarvam_service

    async def get_or_create_conversation(self, vehicle_id: str, phone_number: str) -> Conversation:
        """Fetch active conversation or initialize a new dialog flow."""
        conv = self.repository.get_conversation_by_vehicle(vehicle_id)
        if conv and conv.state.is_active:
            return conv

        # Initialize conversation state
        state = ConversationState(
            current_node="INIT",
            collected_data={},
            is_active=True
        )
        # Ensure a booking exists
        booking = await self.booking_service.recommend_service(
            vehicle_id=vehicle_id,
            severity=SEVERITY_WARNING,
            phone_number=phone_number,
            fault="Diagnostic Scheduled Service"
        )
        booking_id = booking.id if booking else None
        
        conv = Conversation(
            id="CONV-" + vehicle_id + "-" + datetime.utcnow().strftime("%y%m%d%H%M%S"),
            vehicle_id=vehicle_id,
            booking_id=booking_id,
            state=state,
            history=[
                Message(
                    role="assistant",
                    content="Hello! This is PulseDrive Concierge. We detected a vehicle diagnostic alert. Would you like to schedule an inspection?",
                    timestamp=datetime.utcnow()
                )
            ]
        )
        self.repository.create_conversation(conv)
        return conv

    async def process_turn(self, conversation_id: str, user_message: str) -> str:
        """Processes a single conversational dialogue turn, returning assistant's response.
        
        Updates slots and advances nodes: INIT -> ASK_LOCATION -> ASK_DATE -> ASK_TIME -> ASK_CONFIRM -> CONFIRMED/CANCELLED
        """
        conv = self.repository.get_conversation(conversation_id)
        if not conv or not conv.state.is_active:
            return "This conversation is no longer active. Drive safe!"

        # Record user message in history
        conv.history.append(Message(role="user", content=user_message, timestamp=datetime.utcnow()))
        
        # Analyze slot elements with Sarvam service
        nlu = await self.sarvam_service.extract_intent_and_entities(user_message)
        
        node = conv.state.current_node
        collected = conv.state.collected_data
        booking_id = conv.booking_id
        
        response_text = ""

        # Step 1: State Machine Navigation
        if node == "INIT":
            if nlu.get("confirmation") is True or "yes" in user_message.lower():
                node = "ASK_LOCATION"
                response_text = "Great. Please provide your city or current address so we can find the nearest service center."
            elif nlu.get("confirmation") is False or "no" in user_message.lower():
                node = "CANCELLED"
                conv.state.is_active = False
                response_text = "Understood. The diagnostic code is recorded. If you change your mind, let us know. Safe driving!"
                if booking_id:
                    await self.booking_service.cancel_booking(booking_id)
            else:
                response_text = "I'm sorry, I didn't quite catch that. Would you like us to schedule a vehicle inspection?"

        elif node == "ASK_LOCATION":
            location = nlu.get("location") or user_message
            # Perform location mapping & nearest center finding
            lat, lng = 28.6304, 77.2177  # default to Delhi coordinates
            loc_lower = location.lower()
            if "noida" in loc_lower:
                lat, lng = 28.6273, 77.3725
            elif "gurgaon" in loc_lower or "gurugram" in loc_lower:
                lat, lng = 28.4735, 77.0402
            nearest = self.booking_service.scheduler_service.location_service.find_nearest_service_center(lat, lng)
            collected["location"] = location
            collected["service_center"] = nearest["name"]
            
            if booking_id:
                await self.booking_service.update_booking_location(
                    booking_id=booking_id,
                    location_name=location,
                    lat=nearest["latitude"],
                    lng=nearest["longitude"]
                )

            node = "ASK_DATE"
            response_text = f"The nearest center is {nearest['name']}. What date would you like to schedule the service?"

        elif node == "ASK_DATE":
            date_val = nlu.get("date") or user_message
            # Default to tomorrow if raw value
            if "tomorrow" in date_val.lower():
                date_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                date_str = datetime.utcnow().strftime("%Y-%m-%d") # Today
                
            collected["date"] = date_str
            if booking_id:
                await self.booking_service.select_date(booking_id, date_str)

            node = "ASK_TIME"
            # Get available slots
            slots = self.booking_service.scheduler_service.get_available_slots_for_center("SC-001", date_str)
            slots_str = ", ".join(slots[:3]) if slots else "10:00, 14:00"
            response_text = f"We have slots at {slots_str}. Which slot would you prefer?"

        elif node == "ASK_TIME":
            time_val = nlu.get("time") or "10:00"
            collected["time"] = time_val
            
            node = "ASK_CONFIRM"
            response_text = f"Confirming booking at {collected.get('service_center')} on {collected.get('date')} at {collected.get('time')}. Say yes to lock it in."

        elif node == "ASK_CONFIRM":
            if nlu.get("confirmation") is True or "yes" in user_message.lower():
                node = "CONFIRMED"
                conv.state.is_active = False
                response_text = "Fantastic. Your appointment is scheduled. We've locked in your slot. Drive safe!"
                if booking_id:
                    await self.booking_service.select_time_and_confirm(booking_id, collected.get("time", "10:00"))
            else:
                node = "CANCELLED"
                conv.state.is_active = False
                response_text = "No problem. Booking has been cancelled. Drive safely!"
                if booking_id:
                    await self.booking_service.cancel_booking(booking_id)

        # Update and save conversation turn
        conv.state.current_node = node
        conv.state.collected_data = collected
        conv.history.append(Message(role="assistant", content=response_text, timestamp=datetime.utcnow()))
        
        self.repository.update_conversation(
            conv_id=conversation_id,
            updates={
                "state": conv.state.model_dump(mode="json"),
                "history": [msg.model_dump(mode="json") for msg in conv.history]
            }
        )

        return response_text
