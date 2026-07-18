from pydantic import BaseModel, Field
from typing import Optional

class SmokeData(BaseModel):
    gas_level: float = Field(..., description="Gas level reading (ppm)")
    digital: int = Field(..., description="Digital smoke indicator (0 or 1)")

class GyroData(BaseModel):
    ax: float = Field(..., description="Acceleration along X axis")
    ay: float = Field(..., description="Acceleration along Y axis")
    az: float = Field(..., description="Acceleration along Z axis")

class BrakeData(BaseModel):
    pressure: float = Field(..., description="Brake fluid pressure (psi)")
    pad_wear: float = Field(..., description="Brake pad wear percentage (0-100)")

class SensorPacket(BaseModel):
    vehicle_id: str = Field(default="VH001", description="Vehicle identifier")
    temperature: float = Field(..., description="Engine temperature (Celsius)")
    battery_voltage: float = Field(..., description="Battery voltage (Volts)")
    smoke: SmokeData = Field(..., description="Smoke and gas level metrics")
    gyro: GyroData = Field(..., description="Accelerometer and gyroscopic metrics")
    brake: Optional[BrakeData] = Field(
        default=BrakeData(pressure=800.0, pad_wear=20.0), 
        description="Brake system telemetry"
    )
