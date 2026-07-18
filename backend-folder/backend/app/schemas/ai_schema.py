from typing import Optional

from pydantic import BaseModel, Field


class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question for AI analysis")


class AskAIResponse(BaseModel):
    success: bool = Field(..., description="Whether the AI request completed successfully")
    answer: str = Field(..., description="AI-generated answer to the provided question")


class AIErrorResponse(BaseModel):
    success: bool = Field(..., description="Whether the AI request failed")
    error: str = Field(..., description="Short error message")
    details: Optional[str] = Field(None, description="Additional error details")
