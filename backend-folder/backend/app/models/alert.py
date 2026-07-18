from datetime import datetime
from pydantic import BaseModel, Field


class Alert(BaseModel):
    vehicleId: str = Field(..., min_length=1)
    level: str
    message: str
    timestamp: datetime
