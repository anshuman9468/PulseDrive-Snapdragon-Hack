import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from service_concierge.repository.booking_repository import BookingRepository
from service_concierge.services.scheduler_service import SchedulerService
from service_concierge.services.notification_service import NotificationService
from service_concierge.models.booking import Booking
from service_concierge.utils.constants import *
from app.websocket.manager import manager

logger = logging.getLogger(__name__)

class BookingService:
    """Manages the lifecycle of service bookings, triggering notifications and WebSocket updates."""

    def __init__(
        self,
        repository: BookingRepository,
        scheduler_service: SchedulerService,
        notification_service: NotificationService
    ):
        self.repository = repository
        self.scheduler_service = scheduler_service
        self.notification_service = notification_service

    async def recommend_service(self, vehicle_id: str, severity: str, phone_number: str, fault: str) -> Optional[Booking]:
        """Examines severity, creates a booking if required, and dispatches alerts."""
        if severity == SEVERITY_SAFE:
            logger.info(f"Vehicle {vehicle_id} is SAFE. No booking action.")
            return None

        # Check if active booking exists
        existing = self.repository.get_latest_booking_for_vehicle(vehicle_id)
        if existing and existing.booking_status in [STATUS_PENDING, STATUS_CONFIRMED]:
            logger.info(f"Active booking already exists for vehicle {vehicle_id}: {existing.id}")
            return existing

        # Create new booking
        booking = Booking(
            id="BKG-" + uuid.uuid4().hex[:12].upper(),
            vehicle_id=vehicle_id,
            phone_number=phone_number,
            booking_status=STATUS_PENDING,
            decision_severity=severity
        )
        self.repository.create_booking(booking)
        logger.info(f"Created new pending booking {booking.id} for vehicle {vehicle_id}")

        # Broadcast event
        await manager.broadcast({
            "type": EVENT_SERVICE_RECOMMENDED,
            "vehicleId": vehicle_id,
            "bookingId": booking.id,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Route notifications
        await self.notification_service.route_severity_notifications(
            vehicle_id=vehicle_id,
            phone_number=phone_number,
            severity=severity,
            fault=fault
        )

        return booking

    async def start_booking_flow(self, vehicle_id: str, phone_number: str) -> Optional[Booking]:
        """Explicitly starts the scheduling flow from driver/user request."""
        booking = await self.recommend_service(
            vehicle_id=vehicle_id, 
            severity=SEVERITY_WARNING, 
            phone_number=phone_number, 
            fault="User Initiated Inspection"
        )
        if booking:
            await manager.broadcast({
                "type": EVENT_BOOKING_STARTED,
                "vehicleId": vehicle_id,
                "bookingId": booking.id,
                "timestamp": datetime.utcnow().isoformat()
            })
        return booking

    async def update_booking_location(self, booking_id: str, location_name: str, lat: float, lng: float) -> Optional[Booking]:
        """Associate location coordinates with booking and find nearest service center."""
        nearest = self.scheduler_service.location_service.find_nearest_service_center(lat, lng)
        center_name = nearest.get("name", location_name)
        
        updates = {
            "location": location_name,
            "latitude": lat,
            "longitude": lng,
            "assigned_service_center": center_name
        }
        booking = self.repository.update_booking(booking_id, updates)
        if booking:
            await manager.broadcast({
                "type": EVENT_LOCATION_SELECTED,
                "vehicleId": booking.vehicle_id,
                "bookingId": booking_id,
                "location": location_name,
                "assignedServiceCenter": center_name,
                "timestamp": datetime.utcnow().isoformat()
            })
        return booking

    async def select_date(self, booking_id: str, date_str: str) -> Optional[Booking]:
        """Save date slots of interest."""
        updates = {"preferred_date": date_str}
        booking = self.repository.update_booking(booking_id, updates)
        if booking:
            await manager.broadcast({
                "type": EVENT_DATE_SELECTED,
                "vehicleId": booking.vehicle_id,
                "bookingId": booking_id,
                "preferredDate": date_str,
                "timestamp": datetime.utcnow().isoformat()
            })
        return booking

    async def select_time_and_confirm(self, booking_id: str, time_str: str) -> Optional[Booking]:
        """Finalize preferred slot time, allocate appointment calendar lock, and mark status confirmed."""
        booking = self.repository.get_booking(booking_id)
        if not booking:
            return None

        date_str = booking.preferred_date or datetime.utcnow().strftime("%Y-%m-%d")
        
        # We need a service center assignment
        centers = self.scheduler_service.location_service.get_all_service_centers()
        # Find SC by assigned name, default to first SC
        center = next((c for c in centers if c["name"] == booking.assigned_service_center), centers[0])
        
        # Create calendar appointment lock
        appt = self.scheduler_service.create_appointment(
            booking_id=booking_id,
            center_id=center["id"],
            date_str=date_str,
            time_str=time_str
        )
        
        if not appt:
            logger.warning(f"Could not allocate slot appointment lock for booking {booking_id}")
            return None

        updates = {
            "preferred_time": time_str,
            "preferred_date": date_str,
            "booking_status": STATUS_CONFIRMED,
            "assigned_service_center": center["name"]
        }
        updated_booking = self.repository.update_booking(booking_id, updates)
        if updated_booking:
            await manager.broadcast({
                "type": EVENT_BOOKING_CONFIRMED,
                "vehicleId": updated_booking.vehicle_id,
                "bookingId": booking_id,
                "assignedServiceCenter": center["name"],
                "preferredDate": date_str,
                "preferredTime": time_str,
                "timestamp": datetime.utcnow().isoformat()
            })
        return updated_booking

    async def cancel_booking(self, booking_id: str) -> Optional[Booking]:
        """Cancel booking status and free calendar slots."""
        self.scheduler_service.cancel_appointment(booking_id)
        updates = {"booking_status": STATUS_CANCELLED}
        booking = self.repository.update_booking(booking_id, updates)
        if booking:
            await manager.broadcast({
                "type": EVENT_BOOKING_CANCELLED,
                "vehicleId": booking.vehicle_id,
                "bookingId": booking_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        return booking

    def get_upcoming_appointments(self, vehicle_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns details on pending/confirmed bookings for frontend display."""
        bookings = self.repository.get_booking_history(vehicle_id)
        active_bookings = [b for b in bookings if b.booking_status in [STATUS_PENDING, STATUS_CONFIRMED]]
        
        results = []
        for b in active_bookings:
            appt = self.repository.get_appointment_by_booking(b.id)
            results.append({
                "booking_id": b.id,
                "vehicle_id": b.vehicle_id,
                "customer_name": b.customer_name,
                "phone_number": b.phone_number,
                "location": b.location,
                "assigned_service_center": b.assigned_service_center,
                "preferred_date": b.preferred_date,
                "preferred_time": b.preferred_time,
                "status": b.booking_status,
                "appointment_status": appt.status if appt else "UNSCHEDULED",
                "created_at": b.created_at.isoformat()
            })
        return results
