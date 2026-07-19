from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from service_concierge.models.conversation import Message

class Booking(BaseModel):
    id: str = Field(..., alias="_id", description="Unique booking ID")
    vehicle_id: str = Field(..., description="Vehicle ID")
    customer_name: Optional[str] = Field(default=None, description="Name of the customer")
    phone_number: str = Field(..., description="Customer phone number")
    location: Optional[str] = Field(default=None, description="Preferred location name")
    latitude: Optional[float] = Field(default=None, description="Latitude of location / service center")
    longitude: Optional[float] = Field(default=None, description="Longitude of location / service center")
    preferred_date: Optional[str] = Field(default=None, description="Preferred date (YYYY-MM-DD)")
    preferred_time: Optional[str] = Field(default=None, description="Preferred time (HH:MM)")
    assigned_service_center: Optional[str] = Field(default=None, description="Assigned Service Center name/ID")
    booking_status: str = Field(default="PENDING", description="Booking status (PENDING, CONFIRMED, CANCELLED)")
    conversation_history: List[Message] = Field(default_factory=list, description="Exchanged messages")
    decision_severity: str = Field(..., description="Decision severity at booking creation (WARNING, CRITICAL, EMERGENCY)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
