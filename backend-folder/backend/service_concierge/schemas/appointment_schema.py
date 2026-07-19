from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AppointmentCreateRequest(BaseModel):
    booking_id: str = Field(..., description="Linked booking ID")
    service_center_id: str = Field(..., description="Service Center ID")
    scheduled_datetime: datetime = Field(..., description="Date and time of appointment")
    notes: Optional[str] = Field(default=None)

class AppointmentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    booking_id: str
    service_center_id: str
    scheduled_datetime: datetime
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
