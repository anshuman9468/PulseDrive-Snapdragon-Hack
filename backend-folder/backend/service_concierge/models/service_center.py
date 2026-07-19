from pydantic import BaseModel, Field
from typing import Optional, List

class ServiceCenter(BaseModel):
    id: str = Field(..., alias="_id", description="Unique identifier for the service center")
    name: str = Field(..., description="Name of the service center")
    address: str = Field(..., description="Full address of the service center")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    phone_number: str = Field(..., description="Contact phone number")
    operating_hours: str = Field(default="09:00 - 18:00", description="Operating hours")
    available_slots: List[str] = Field(default_factory=list, description="List of available HH:MM slots")

    class Config:
        populate_by_name = True
