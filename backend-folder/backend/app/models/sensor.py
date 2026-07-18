from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GasSensor(BaseModel):
    value: float = Field(..., description="Gas sensor reading value")
    unit: str = Field("ppm", description="Gas sensor reading unit")


class GPS(BaseModel):
    lat: float = Field(..., description="GPS Latitude")
    lng: float = Field(..., description="GPS Longitude")


class MPUData(BaseModel):
    accX: float = Field(..., description="Accelerometer X-axis value")
    accY: float = Field(..., description="Accelerometer Y-axis value")
    accZ: float = Field(..., description="Accelerometer Z-axis value")
    gyroX: float = Field(..., description="Gyroscope X-axis value")
    gyroY: float = Field(..., description="Gyroscope Y-axis value")
    gyroZ: float = Field(..., description="Gyroscope Z-axis value")


class SensorData(BaseModel):
    vehicleId: str = Field(..., min_length=1, description="Unique vehicle identifier")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the reading, auto-generated if missing"
    )
    temperature: float = Field(..., description="Vehicle temperature reading")
    voltage: float = Field(..., description="Vehicle voltage reading")
    gasSensor: GasSensor = Field(..., description="Gas sensor readings")
    gps: GPS = Field(..., description="GPS coordinates")
    mpu1: MPUData = Field(..., description="First MPU sensor reading")
    mpu2: MPUData = Field(..., description="Second MPU sensor reading")


class SensorResponse(BaseModel):
    success: bool = Field(..., description="Indicates if operation succeeded")
    message: str = Field(..., description="Status message")
    inserted_id: Optional[str] = Field(None, description="Inserted document identifier in DB")
    data: Optional[SensorData] = Field(None, description="Returned sensor data payload")


class HistoryResponse(BaseModel):
    success: bool = Field(..., description="Indicates if operation succeeded")
    count: int = Field(..., description="Number of items returned")
    data: list[SensorData] = Field(..., description="Historical sensor data records")
