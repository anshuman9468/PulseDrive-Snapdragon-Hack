from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GPSData(BaseModel):
    lat: float
    lng: float


class MPU6050Data(BaseModel):
    accX: float
    accY: float
    accZ: float
    gyroX: float
    gyroY: float
    gyroZ: float


class SensorData(BaseModel):
    vehicleId: str = Field(..., min_length=1)
    temperature: float
    voltage: float
    gps: GPSData
    mpu6050: MPU6050Data
    timestamp: datetime


class SensorDataResponse(BaseModel):
    message: str
    sensor_data: SensorData
