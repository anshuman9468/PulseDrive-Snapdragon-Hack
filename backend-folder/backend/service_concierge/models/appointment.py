from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Appointment(BaseModel):
    id: str = Field(..., alias="_id", description="Unique appointment ID")
    booking_id: str = Field(..., description="Linked booking ID")
    service_center_id: str = Field(..., description="Service Center ID")
    scheduled_datetime: datetime = Field(..., description="Scheduled date and time")
    status: str = Field(default="SCHEDULED", description="Appointment status (SCHEDULED, COMPLETED, CANCELLED)")
    notes: Optional[str] = Field(default=None, description="Optional booking notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
