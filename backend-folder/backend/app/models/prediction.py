from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.sensor import SensorData


class PredictionRequest(BaseModel):
    """Request model for vehicle health prediction.
    
    Attributes:
        vehicleId: Unique identifier for the vehicle
        features: Input features matching new SensorData schema
        timestamp: When the prediction was requested
    """
    vehicleId: str = Field(..., min_length=1, description="Vehicle identifier")
    features: Optional[SensorData] = Field(None, description="Input features matching new SensorData schema")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of prediction request")


class PredictionResponse(BaseModel):
    """Response model for vehicle health prediction.
    
    Attributes:
        vehicleId: The vehicle identifier
        healthScore: Overall vehicle health score (0-100)
        status: Prediction status (healthy, warning, critical)
        confidence: Model confidence level (0-1)
        recommendation: Recommended action based on prediction
        timestamp: When the prediction was generated
    """
    vehicleId: str = Field(..., description="Vehicle identifier")
    healthScore: float = Field(..., ge=0, le=100, description="Vehicle health score (0-100)")
    status: str = Field(..., description="Health status (healthy, warning, critical)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    recommendation: str = Field(..., description="Recommended action for user")
    timestamp: datetime = Field(..., description="Prediction timestamp")


class PredictionError(BaseModel):
    """Error response model for prediction failures."""
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
