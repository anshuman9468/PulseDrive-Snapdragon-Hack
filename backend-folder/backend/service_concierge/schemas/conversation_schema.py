from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class MessageSchema(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationResponse(BaseModel):
    id: str = Field(..., alias="_id")
    vehicle_id: str
    booking_id: Optional[str]
    current_node: str
    collected_data: Dict[str, Any]
    is_active: bool
    history: List[MessageSchema]

    class Config:
        populate_by_name = True

class ConversationMessageRequest(BaseModel):
    text: str = Field(..., description="The transcript/text from the user")
    phone_number: Optional[str] = Field(default=None, description="Twilio phone number of speaker")
