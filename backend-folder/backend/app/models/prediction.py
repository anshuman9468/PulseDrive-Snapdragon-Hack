from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request model for vehicle health prediction.
    
    Attributes:
        vehicleId: Unique identifier for the vehicle
        features: Input features for prediction (e.g., sensor data, metrics)
        timestamp: When the prediction was requested
    """
    vehicleId: str = Field(..., min_length=1, description="Vehicle identifier")
    features: Optional[dict] = Field(default_factory=dict, description="Input features for prediction")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of prediction request")


class PredictionResponse(BaseModel):
    """Response model for vehicle health prediction.
    
    Attributes:
        vehicleId: The vehicle identifier
        healthScore: Overall vehicle health score (0-100)
        status: Prediction status (healthy, warning, critical, emergency)
        confidence: Model confidence level (0-1)
        recommendation: Recommended action based on prediction
        timestamp: When the prediction was generated
        riskScore: Optional overall risk score (0-100)
        primaryFault: Optional primary fault description
        secondaryFaults: Optional list of secondary faults
        agentResults: Optional detailed outputs from individual diagnostic agents
    """
    vehicleId: str = Field(..., description="Vehicle identifier")
    healthScore: float = Field(..., ge=0, le=100, description="Vehicle health score (0-100)")
    status: str = Field(..., description="Health status (healthy, warning, critical, emergency)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    recommendation: str = Field(..., description="Recommended action for user")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    riskScore: Optional[float] = Field(None, description="Fused overall risk score")
    failureProbability: Optional[float] = Field(None, description="Overall failure probability (0.0 to 1.0)")
    riskTrend: Optional[str] = Field(None, description="Risk trend (increasing, stable, decreasing)")
    riskConfidence: Optional[float] = Field(None, description="Confidence of the risk assessment")
    primaryFault: Optional[str] = Field(None, description="Dominant fault identified")
    secondaryFaults: Optional[List[str]] = Field(default_factory=list, description="Secondary faults identified")
    agentResults: Optional[List[Any]] = Field(default_factory=list, description="Detailed agent diagnostics")
    executionContext: Optional[dict] = Field(None, description="Detailed execution context of the agentic run")



class PredictionError(BaseModel):
    """Error response model for prediction failures."""
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

