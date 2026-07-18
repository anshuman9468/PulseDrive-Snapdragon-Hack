from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["ask_ai"])


class AskAIRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: Optional[str] = None


@router.post("/ask-ai")
async def ask_ai(request: AskAIRequest) -> dict:
    return {
        "question": request.question,
        "context": request.context,
        "response": "This endpoint is ready for AI integration.",
    }
