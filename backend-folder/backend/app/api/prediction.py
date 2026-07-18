import logging
from fastapi import APIRouter, HTTPException, status

from app.models.prediction import PredictionRequest, PredictionResponse, PredictionError
from app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

# Initialize the prediction service
# To use a real ML model, pass model_path: prediction_service = PredictionService(model_path="path/to/model.pkl")
prediction_service = PredictionService()

router = APIRouter(prefix="/api", tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        200: {"description": "Prediction successful"},
        400: {"model": PredictionError, "description": "Invalid request"},
        500: {"model": PredictionError, "description": "Prediction service error"},
    },
)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Generate a health prediction for a vehicle.
    
    This endpoint uses the prediction service to analyze vehicle health
    and return a comprehensive health report with recommendations.
    
    Args:
        request: PredictionRequest with vehicleId and optional features
        
    Returns:
        PredictionResponse with healthScore, status, confidence, and recommendation
        
    Raises:
        HTTPException: If prediction fails
        
    Example:
        POST /api/predict
        {
            "vehicleId": "VH123456",
            "features": {
                "rpm": 3000,
                "temperature": 85,
                "mileage": 45000,
                "fuel_consumption": 8.5,
                "battery_voltage": 13.5
            }
        }
        
        Response:
        {
            "vehicleId": "VH123456",
            "healthScore": 85.5,
            "status": "healthy",
            "confidence": 0.92,
            "recommendation": "Continue regular maintenance schedule",
            "timestamp": "2026-07-17T21:16:32.856000"
        }
    """
    try:
        # Validate vehicleId
        if not request.vehicleId or not request.vehicleId.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vehicleId cannot be empty",
            )

        # Call prediction service
        prediction_response = prediction_service.predict(request)

        logger.info(
            f"Prediction generated for vehicle {request.vehicleId}: "
            f"score={prediction_response.healthScore}, status={prediction_response.status}"
        )

        return prediction_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for vehicle {request.vehicleId}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate prediction",
        ) from e


@router.get(
    "/predict/health",
    response_model=dict,
    tags=["health"],
)
async def prediction_health() -> dict:
    """Check prediction service health status.
    
    Returns:
        Service status and model information
        
    Example response:
        {
            "status": "healthy",
            "model_loaded": false,
            "using_mock": true
        }
    """
    return {
        "status": "healthy",
        "model_loaded": prediction_service.model is not None,
        "using_mock": prediction_service.use_mock,
    }
