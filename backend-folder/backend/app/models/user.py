from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=5)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: Optional[str]
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "user123",
                "username": "pulse_user",
                "email": "user@example.com",
                "created_at": "2026-07-17T16:00:00Z",
            }
        }
    }


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
