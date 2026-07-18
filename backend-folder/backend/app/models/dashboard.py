from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.sensor import GPS, MPUData, GasSensor


class AIDiagnosis(BaseModel):
    message: str = Field(..., description="AI diagnostic message")
    confidence: int = Field(
        ...,
        ge=0,
        le=100,
        description="AI confidence percentage (0-100)",
    )
    recommendation: str = Field(..., description="AI maintenance recommendation")


class EdgeAIStatus(BaseModel):
    runtime: str = Field(..., description="Edge AI runtime environment")
    latency: int = Field(..., description="Edge AI latency in milliseconds")
    status: str = Field(..., description="Edge AI operational status")


class ConnectivityStatus(BaseModel):
    esp32: bool = Field(..., description="ESP32 connectivity status")
    websocket: bool = Field(..., description="WebSocket connectivity status")


class DashboardData(BaseModel):
    vehicleId: str = Field(..., description="Vehicle identifier")
    timestamp: datetime = Field(..., description="Timestamp of the latest sensor reading")
    temperature: float = Field(..., description="Latest temperature reading")
    voltage: float = Field(..., description="Latest voltage reading")
    gasSensor: GasSensor = Field(..., description="Gas sensor reading")
    gps: GPS = Field(..., description="GPS location data")
    mpu1: MPUData = Field(..., description="MPU1 sensor data")
    mpu2: MPUData = Field(..., description="MPU2 sensor data")

    healthScore: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall vehicle health score",
    )
    status: str = Field(..., description="Overall health status")
    remainingUsefulLife: int = Field(
        ..., description="Estimated remaining useful life in days"
    )
    aiDiagnosis: AIDiagnosis = Field(..., description="AI diagnosis details")
    edgeAI: EdgeAIStatus = Field(..., description="Edge AI runtime status")
    connectivity: ConnectivityStatus = Field(..., description="Connectivity status")


class DashboardResponse(BaseModel):
    success: bool = Field(..., description="Whether dashboard data was retrieved successfully")
    data: DashboardData = Field(..., description="Dashboard payload")
