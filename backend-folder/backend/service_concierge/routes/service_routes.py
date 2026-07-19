import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Form, Response
from pydantic import BaseModel, Field

from service_concierge.container import container
from service_concierge.schemas.booking_schema import BookingResponse, BookingCreateRequest
from service_concierge.schemas.appointment_schema import AppointmentResponse
from service_concierge.utils.constants import *

logger = logging.getLogger(__name__)

router = APIRouter()

class RecommendRequest(BaseModel):
    vehicle_id: str
    severity: str
    phone_number: str
    fault: str

class StartFlowRequest(BaseModel):
    vehicle_id: str
    phone_number: str

class LocationSelectRequest(BaseModel):
    location: str
    latitude: float
    longitude: float

class DateSelectRequest(BaseModel):
    date: str

class TimeConfirmRequest(BaseModel):
    time: str

class CallTriggerRequest(BaseModel):
    vehicle_id: str
    phone_number: str
    webhook_host: str = Field(default="http://localhost:8000")

@router.post("/booking/recommend", response_model=Dict[str, Any])
async def recommend_booking(req: RecommendRequest):
    """Trigger alert evaluation logic (normally called internally by prediction pipeline)."""
    payload = {
        "vehicleId": req.vehicle_id,
        "severity": req.severity,
        "risk_score": 85.0 if req.severity in [SEVERITY_CRITICAL, SEVERITY_EMERGENCY] else 30.0,
        "fault": req.fault
    }
    result = await container.alert_agent.evaluate_decision_engine_output(payload)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to process recommendation")
    return result

@router.post("/booking/start", response_model=Dict[str, Any])
async def start_booking(req: StartFlowRequest):
    """Explicitly start a booking sequence for a vehicle."""
    booking = await container.booking_service.start_booking_flow(req.vehicle_id, req.phone_number)
    if not booking:
        raise HTTPException(status_code=400, detail="Could not initiate booking")
    return {
        "status": "success",
        "booking_id": booking.id,
        "state": booking.booking_status
    }

@router.post("/booking/{booking_id}/location", response_model=Dict[str, Any])
async def select_location(booking_id: str, req: LocationSelectRequest):
    """Update booking with customer coordinates and assign nearest service center."""
    booking = await container.booking_service.update_booking_location(
        booking_id, req.location, req.latitude, req.longitude
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {
        "status": "success",
        "booking_id": booking.id,
        "assigned_service_center": booking.assigned_service_center
    }

@router.post("/booking/{booking_id}/date", response_model=Dict[str, Any])
async def select_date(booking_id: str, req: DateSelectRequest):
    """Select preferred service date."""
    booking = await container.booking_service.select_date(booking_id, req.date)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {
        "status": "success",
        "booking_id": booking.id,
        "preferred_date": booking.preferred_date
    }

@router.post("/booking/{booking_id}/confirm", response_model=Dict[str, Any])
async def select_time_confirm(booking_id: str, req: TimeConfirmRequest):
    """Confirm a slot and finalize scheduling lock."""
    booking = await container.booking_service.select_time_and_confirm(booking_id, req.time)
    if not booking:
        raise HTTPException(status_code=400, detail="Failed to lock slot appointment or invalid booking")
    return {
        "status": "success",
        "booking_id": booking.id,
        "booking_status": booking.booking_status,
        "assigned_service_center": booking.assigned_service_center,
        "date": booking.preferred_date,
        "time": booking.preferred_time
    }

@router.post("/booking/{booking_id}/cancel", response_model=Dict[str, Any])
async def cancel_booking(booking_id: str):
    """Cancel booking and free allocated slots."""
    booking = await container.booking_service.cancel_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {
        "status": "success",
        "booking_id": booking.id,
        "booking_status": booking.booking_status
    }

@router.get("/booking/history", response_model=List[Dict[str, Any]])
async def booking_history(vehicle_id: Optional[str] = Query(None)):
    """Fetch history list of service bookings."""
    return container.booking_service.get_upcoming_appointments(vehicle_id)

@router.get("/centers", response_model=List[Dict[str, Any]])
async def get_service_centers():
    """Retrieve list of registered service centers."""
    return container.location_service.get_all_service_centers()

@router.get("/centers/nearby", response_model=List[Dict[str, Any]])
async def get_nearby_centers(lat: float = Query(...), lng: float = Query(...)):
    """Sort and query nearest service centers to coordinates."""
    return container.scheduler_service.get_nearby_centers(lat, lng)

# --- TWILIO VOICE INTEGRATION ENDPOINTS ---

@router.post("/voice/call", response_model=Dict[str, Any])
async def trigger_voice_call(req: CallTriggerRequest):
    """Start an interactive outbound telematics concierge call to driver."""
    webhook_url = f"{req.webhook_host}/api/service/voice/twiml?vehicle_id={req.vehicle_id}&phone_number={req.phone_number}"
    call_sid = await container.twilio_service.initiate_call(req.phone_number, webhook_url)
    if not call_sid:
        raise HTTPException(status_code=500, detail="Twilio failed to trigger outbound call")
    return {
        "status": "success",
        "call_sid": call_sid
    }

@router.post("/voice/twiml")
async def twilio_twiml_start(
    vehicle_id: str,
    phone_number: str,
    CallSid: str = Form(...)
):
    """TwiML XML builder responding to initial call pick-up event."""
    # Webhook URL for gathering input
    gather_url = f"/api/service/voice/twiml/gather?vehicle_id={vehicle_id}&phone_number={phone_number}"
    twiml_xml = await container.voice_service.handle_call_start(
        vehicle_id=vehicle_id,
        phone_number=phone_number,
        gather_url=gather_url
    )
    return Response(content=twiml_xml, media_type="application/xml")

@router.post("/voice/twiml/gather")
async def twilio_twiml_gather(
    vehicle_id: str,
    phone_number: str,
    SpeechResult: Optional[str] = Form(None),
    CallSid: str = Form(...)
):
    """Twilio Speech-to-Text webhook callback turn processing."""
    # Lookup active conversation
    conv = await container.voice_service.conversation_agent.get_or_create_conversation(vehicle_id, phone_number)
    gather_url = f"/api/service/voice/twiml/gather?vehicle_id={vehicle_id}&phone_number={phone_number}"
    
    transcript = SpeechResult or ""
    twiml_xml = await container.voice_service.handle_speech_input(
        conversation_id=conv.id,
        speech_result=transcript,
        gather_url=gather_url
    )
    return Response(content=twiml_xml, media_type="application/xml")
