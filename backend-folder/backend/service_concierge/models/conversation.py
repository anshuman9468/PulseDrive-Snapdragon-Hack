from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., description="Role of the speaker (user, system, assistant)")
    content: str = Field(..., description="Text content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time message was sent")

class ConversationState(BaseModel):
    current_node: str = Field(default="START", description="Current node in dialogue tree")
    collected_data: Dict[str, Any] = Field(default_factory=dict, description="Collected slot values (e.g. location, date, time)")
    is_active: bool = Field(default=True, description="Whether conversation is ongoing")

class Conversation(BaseModel):
    id: str = Field(..., alias="_id", description="Unique conversation identifier")
    booking_id: Optional[str] = Field(default=None, description="Linked booking ID if any")
    vehicle_id: str = Field(..., description="Vehicle ID this conversation relates to")
    state: ConversationState = Field(default_factory=ConversationState, description="Dialog state")
    history: List[Message] = Field(default_factory=list, description="List of messages exchanged")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
