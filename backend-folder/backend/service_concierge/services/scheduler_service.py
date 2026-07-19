import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from service_concierge.repository.booking_repository import BookingRepository
from service_concierge.services.location_service import LocationService
from service_concierge.services.calendar_service import CalendarService
from service_concierge.models.appointment import Appointment
import uuid

logger = logging.getLogger(__name__)

class SchedulerService:
    """Coordinates calendar scheduling, location proximity, and slot assignment."""

    def __init__(
        self,
        repository: BookingRepository,
        location_service: LocationService,
        calendar_service: CalendarService
    ):
        self.repository = repository
        self.location_service = location_service
        self.calendar_service = calendar_service

    def get_nearby_centers(self, lat: float, lng: float) -> List[Dict[str, Any]]:
        """Returns all service centers sorted by proximity to coordinate."""
        centers = self.location_service.get_all_service_centers()
        sorted_centers = []
        for c in centers:
            c_copy = c.copy()
            c_copy["distance_km"] = round(
                self.location_service.calculate_haversine_distance(
                    lat, lng, c["latitude"], c["longitude"]
                ), 2
            )
            sorted_centers.append(c_copy)
        
        return sorted(sorted_centers, key=lambda x: x["distance_km"])

    def get_available_slots_for_center(self, center_id: str, date_str: str) -> List[str]:
        """Finds open slots for a given date and service center."""
        # Retrieve service center definition
        centers = self.location_service.get_all_service_centers()
        center = next((c for c in centers if c["id"] == center_id), None)
        if not center:
            logger.warning(f"Service center {center_id} not found")
            return []

        # Return available slots
        return self.calendar_service.get_available_slots(date_str, center["available_slots"])

    def create_appointment(self, booking_id: str, center_id: str, date_str: str, time_str: str) -> Optional[Appointment]:
        """Validates slot availability and creates a locked calendar appointment."""
        centers = self.location_service.get_all_service_centers()
        center = next((c for c in centers if c["id"] == center_id), None)
        if not center:
            return None

        if not self.calendar_service.validate_slot(date_str, time_str, center["available_slots"]):
            logger.warning(f"Slot {date_str} {time_str} is invalid or closed")
            return None

        # Build datetime
        scheduled_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Check if booking already has appointment
        existing = self.repository.get_appointment_by_booking(booking_id)
        if existing:
            # Update appointment instead of creating a new one
            updates = {
                "service_center_id": center_id,
                "scheduled_datetime": scheduled_dt,
                "status": "SCHEDULED"
            }
            return self.repository.update_appointment(existing.id, updates)

        # Create new
        appt = Appointment(
            id="APT-" + uuid.uuid4().hex[:12].upper(),
            booking_id=booking_id,
            service_center_id=center_id,
            scheduled_datetime=scheduled_dt,
            status="SCHEDULED"
        )
        return self.repository.create_appointment(appt)

    def cancel_appointment(self, booking_id: str) -> bool:
        """Cancel the scheduled appointment for a booking."""
        appt = self.repository.get_appointment_by_booking(booking_id)
        if not appt:
            return False
        
        self.repository.update_appointment(appt.id, {"status": "CANCELLED"})
        return True
