import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.config.database import get_database
from service_concierge.models.booking import Booking
from service_concierge.models.appointment import Appointment
from service_concierge.models.conversation import Conversation, ConversationState

logger = logging.getLogger(__name__)

class BookingRepository:
    """Manages persistence for bookings, appointments, and conversations."""

    def __init__(self):
        self._mem_bookings: Dict[str, Dict[str, Any]] = {}
        self._mem_appointments: Dict[str, Dict[str, Any]] = {}
        self._mem_conversations: Dict[str, Dict[str, Any]] = {}
        try:
            self.db = get_database()
            # Perform a fast ping check to ensure MongoDB server is active
            self.db.command("ping", serverSelectionTimeoutMS=1000)
            self.bookings_col = self.db["bookings"]
            self.appointments_col = self.db["appointments"]
            self.conversations_col = self.db["conversations"]
            self.is_connected = True
            logger.info("Connected to MongoDB for Service Concierge collections")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Falling back to in-memory store.")
            self.is_connected = False


    def create_booking(self, booking: Booking) -> Booking:
        doc = booking.model_dump(by_alias=True, mode="json")
        doc["created_at"] = booking.created_at
        doc["updated_at"] = booking.updated_at
        if self.is_connected:
            try:
                self.bookings_col.insert_one(doc)
            except Exception as e:
                logger.error(f"MongoDB write failed: {e}")
        else:
            self._mem_bookings[booking.id] = doc
        return booking

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        if self.is_connected:
            try:
                doc = self.bookings_col.find_one({"_id": booking_id})
                if doc:
                    return Booking(**doc)
            except Exception as e:
                logger.error(f"MongoDB fetch failed: {e}")
        else:
            doc = self._mem_bookings.get(booking_id)
            if doc:
                return Booking(**doc)
        return None

    def get_latest_booking_for_vehicle(self, vehicle_id: str) -> Optional[Booking]:
        if self.is_connected:
            try:
                doc = self.bookings_col.find_one({"vehicle_id": vehicle_id}, sort=[("created_at", -1)])
                if doc:
                    return Booking(**doc)
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
        else:
            vehicle_bookings = [b for b in self._mem_bookings.values() if b.get("vehicle_id") == vehicle_id]
            if vehicle_bookings:
                # Sort by created_at desc
                latest = max(vehicle_bookings, key=lambda x: x.get("created_at") or datetime.min)
                return Booking(**latest)
        return None

    def update_booking(self, booking_id: str, updates: Dict[str, Any]) -> Optional[Booking]:
        updates["updated_at"] = datetime.utcnow()
        if self.is_connected:
            try:
                self.bookings_col.update_one({"_id": booking_id}, {"$set": updates})
                return self.get_booking(booking_id)
            except Exception as e:
                logger.error(f"MongoDB update failed: {e}")
        else:
            doc = self._mem_bookings.get(booking_id)
            if doc:
                doc.update(updates)
                self._mem_bookings[booking_id] = doc
                return Booking(**doc)
        return None

    def get_booking_history(self, vehicle_id: Optional[str] = None) -> List[Booking]:
        bookings = []
        if self.is_connected:
            try:
                query = {"vehicle_id": vehicle_id} if vehicle_id else {}
                cursor = self.bookings_col.find(query).sort("created_at", -1)
                for doc in cursor:
                    bookings.append(Booking(**doc))
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
        else:
            docs = self._mem_bookings.values()
            if vehicle_id:
                docs = [d for d in docs if d.get("vehicle_id") == vehicle_id]
            # sort by created_at desc
            sorted_docs = sorted(docs, key=lambda x: x.get("created_at") or datetime.min, reverse=True)
            for doc in sorted_docs:
                bookings.append(Booking(**doc))
        return bookings

    def create_appointment(self, appt: Appointment) -> Appointment:
        doc = appt.model_dump(by_alias=True, mode="json")
        doc["scheduled_datetime"] = appt.scheduled_datetime
        doc["created_at"] = appt.created_at
        doc["updated_at"] = appt.updated_at
        if self.is_connected:
            try:
                self.appointments_col.insert_one(doc)
            except Exception as e:
                logger.error(f"MongoDB write failed: {e}")
        else:
            self._mem_appointments[appt.id] = doc
        return appt

    def get_appointment(self, appt_id: str) -> Optional[Appointment]:
        if self.is_connected:
            try:
                doc = self.appointments_col.find_one({"_id": appt_id})
                if doc:
                    return Appointment(**doc)
            except Exception as e:
                logger.error(f"MongoDB fetch failed: {e}")
        else:
            doc = self._mem_appointments.get(appt_id)
            if doc:
                return Appointment(**doc)
        return None

    def get_appointment_by_booking(self, booking_id: str) -> Optional[Appointment]:
        if self.is_connected:
            try:
                doc = self.appointments_col.find_one({"booking_id": booking_id})
                if doc:
                    return Appointment(**doc)
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
        else:
            for appt in self._mem_appointments.values():
                if appt.get("booking_id") == booking_id:
                    return Appointment(**appt)
        return None

    def update_appointment(self, appt_id: str, updates: Dict[str, Any]) -> Optional[Appointment]:
        updates["updated_at"] = datetime.utcnow()
        if self.is_connected:
            try:
                self.appointments_col.update_one({"_id": appt_id}, {"$set": updates})
                return self.get_appointment(appt_id)
            except Exception as e:
                logger.error(f"MongoDB update failed: {e}")
        else:
            doc = self._mem_appointments.get(appt_id)
            if doc:
                doc.update(updates)
                self._mem_appointments[appt_id] = doc
                return Appointment(**doc)
        return None

    def create_conversation(self, conv: Conversation) -> Conversation:
        doc = conv.model_dump(by_alias=True, mode="json")
        doc["created_at"] = conv.created_at
        doc["updated_at"] = conv.updated_at
        # Make sure messages timestamps are serialized properly or handled
        if self.is_connected:
            try:
                self.conversations_col.insert_one(doc)
            except Exception as e:
                logger.error(f"MongoDB write failed: {e}")
        else:
            self._mem_conversations[conv.id] = doc
        return conv

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        if self.is_connected:
            try:
                doc = self.conversations_col.find_one({"_id": conv_id})
                if doc:
                    return Conversation(**doc)
            except Exception as e:
                logger.error(f"MongoDB fetch failed: {e}")
        else:
            doc = self._mem_conversations.get(conv_id)
            if doc:
                return Conversation(**doc)
        return None

    def get_conversation_by_vehicle(self, vehicle_id: str) -> Optional[Conversation]:
        if self.is_connected:
            try:
                doc = self.conversations_col.find_one({"vehicle_id": vehicle_id, "state.is_active": True})
                if not doc:
                    doc = self.conversations_col.find_one({"vehicle_id": vehicle_id}, sort=[("updated_at", -1)])
                if doc:
                    return Conversation(**doc)
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
        else:
            actives = [c for c in self._mem_conversations.values() if c.get("vehicle_id") == vehicle_id and c.get("state", {}).get("is_active")]
            if actives:
                return Conversation(**actives[0])
            all_v = [c for c in self._mem_conversations.values() if c.get("vehicle_id") == vehicle_id]
            if all_v:
                latest = max(all_v, key=lambda x: x.get("updated_at") or datetime.min)
                return Conversation(**latest)
        return None

    def update_conversation(self, conv_id: str, updates: Dict[str, Any]) -> Optional[Conversation]:
        updates["updated_at"] = datetime.utcnow()
        if self.is_connected:
            try:
                self.conversations_col.update_one({"_id": conv_id}, {"$set": updates})
                return self.get_conversation(conv_id)
            except Exception as e:
                logger.error(f"MongoDB update failed: {e}")
        else:
            doc = self._mem_conversations.get(conv_id)
            if doc:
                doc.update(updates)
                self._mem_conversations[conv_id] = doc
                return Conversation(**doc)
        return None
