import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user
from app.config.settings import settings
from app.providers.groq_provider import GroqProvider
from app.schemas.ai_schema import AIErrorResponse, AskAIRequest, AskAIResponse
from app.services.ai_service import AIService, AIProviderError, AIProviderRateLimitError, AIProviderTimeoutError, AIServiceError
from app.services.sensor_service import SensorService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api", tags=["ask_ai"])


def _create_ai_service() -> AIService:
    provider = GroqProvider(
    api_key=settings.GROQ_API_KEY,
    model=settings.AI_MODEL,
)
    return AIService(provider=provider, sensor_service=SensorService())


@router.post(
    "/ask-ai",
    response_model=AskAIResponse,
    responses={
        400: {"model": AIErrorResponse},
        401: {"model": AIErrorResponse},
        429: {"model": AIErrorResponse},
        500: {"model": AIErrorResponse},
    },
)
async def ask_ai(
    request: AskAIRequest,
    _: dict = Depends(get_current_user),
) -> JSONResponse:
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is missing from environment configuration.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "AI provider is not configured.",
                "details": "Missing GROQ_API_KEY.",
            },
        )

    if not settings.AI_MODEL:
        logger.error("AI_MODEL is missing from environment configuration.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "AI model is not configured.",
                "details": "Missing AI_MODEL.",
            },
        )

    try:
        ai_service = _create_ai_service()
        answer = await ai_service.generate_answer(request.question)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "answer": answer},
        )
    except AIProviderRateLimitError as exc:
        logger.warning("AI rate limit error: %s", exc.details)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"success": False, "error": exc.message, "details": exc.details},
        )
    except AIProviderTimeoutError as exc:
        logger.warning("AI timeout error: %s", exc.details)
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"success": False, "error": exc.message, "details": exc.details},
        )
    except AIProviderError as exc:
        logger.error("AI provider error: %s", exc.details)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"success": False, "error": exc.message, "details": exc.details},
        )
    except AIServiceError as exc:
        logger.error("AI service error: %s", exc.details)
        return JSONResponse(
            status_code=exc.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": exc.message, "details": exc.details},
        )
    except Exception as exc:
        logger.exception("Unhandled exception in ask-ai endpoint")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error.",
                "details": str(exc),
            },
        )
