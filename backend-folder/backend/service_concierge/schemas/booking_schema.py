from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from service_concierge.models.conversation import Message

class BookingCreateRequest(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle ID")
    phone_number: str = Field(..., description="Customer phone number")
    decision_severity: str = Field(..., description="Decision severity (WARNING, CRITICAL, EMERGENCY)")
    customer_name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    preferred_date: Optional[str] = Field(default=None)
    preferred_time: Optional[str] = Field(default=None)

class BookingUpdateRequest(BaseModel):
    customer_name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    assigned_service_center: Optional[str] = None
    booking_status: Optional[str] = None

class BookingResponse(BaseModel):
    id: str = Field(..., alias="_id")
    vehicle_id: str
    customer_name: Optional[str]
    phone_number: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    preferred_date: Optional[str]
    preferred_time: Optional[str]
    assigned_service_center: Optional[str]
    booking_status: str
    decision_severity: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
