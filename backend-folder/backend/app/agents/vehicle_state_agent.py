import logging
import os
import time
from typing import Dict, Any, List
import joblib
import numpy as np

from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class VehicleStateAgent(BaseAgent):
    """Diagnoses overall vehicle status using MPU2 acceleration and rotational velocity via the central InferenceEngine."""

    def __init__(self):
        # Load the scaler if present
        scaler_path = "app/runtime/scalers/vehicle_state_scaler.pkl"
        self.scaler = None
        if os.path.exists(scaler_path):
            try:
                self.scaler = joblib.load(scaler_path)
                if hasattr(self.scaler, "feature_names_in_"):
                    del self.scaler.feature_names_in_
                logger.info("VehicleStateAgent loaded scaler successfully")
            except Exception as e:
                logger.warning(f"VehicleStateAgent failed to load scaler: {e}. Using manual scaling.")
        
        # Scaling defaults (StandardScaler mean and scale)
        self.means = [4040.316723549488, 597.782252559727, 13862.41023890785, 28.74880546075085, -2.2232081911262798, -151.2580204778157]
        self.scales = [5962.080758998431, 783.6060040931914, 3745.878475772209, 694.3374800619001, 3869.733831805192, 1476.3977979045874]

    def name(self) -> str:
        return "VehicleStateAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        # Check for gyro telemetry or specific MPU2 accelerometer/gyroscope keys
        return "gyro" in sensor_json or any(k in sensor_json for k in ["MPU2_Accel_X", "mpu2_ax"])

    def _extract_features(self, sensor_json: Dict[str, Any]) -> List[float]:
        gyro_data = sensor_json.get("gyro", {})
        mpu2_data = sensor_json.get("mpu2", {})
        
        def get_val(key_list, default=0.0):
            for k in key_list:
                if k in sensor_json:
                    return float(sensor_json[k])
                if k in gyro_data:
                    return float(gyro_data[k])
                if k in mpu2_data:
                    return float(mpu2_data[k])
            return default

        ax = get_val(["MPU2_Accel_X", "mpu2_ax", "ax2", "ax"], 4040.3)
        ay = get_val(["MPU2_Accel_Y", "mpu2_ay", "ay2", "ay"], 597.7)
        az = get_val(["MPU2_Accel_Z", "mpu2_az", "az2", "az"], 13862.4)
        gx = get_val(["MPU2_Gyro_X", "mpu2_gx", "gx2", "gx"], 28.7)
        gy = get_val(["MPU2_Gyro_Y", "mpu2_gy", "gy2", "gy"], -2.2)
        gz = get_val(["MPU2_Gyro_Z", "mpu2_gz", "gz2", "gz"], -151.2)
        
        return [ax, ay, az, gx, gy, gz]

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        start_time = time.perf_counter()
        try:
            raw_features = self._extract_features(sensor_json)
            
            # Apply scaling
            if self.scaler is not None:
                features_arr = np.array([raw_features])
                scaled_features = self.scaler.transform(features_arr)[0].tolist()
            else:
                scaled_features = [
                    (x - m) / s for x, m, s in zip(raw_features, self.means, self.scales)
                ]
            
            # Run inference
            inf_res = InferenceEngine.predict("vehicle_state", scaled_features)
            probs = inf_res["probabilities"]
            
            # Class mapping: [Normal, Friction Anomaly, Gyro Anomaly, Critical State]
            max_idx = probs.index(max(probs))
            
            if max_idx == 0:
                status = "safe"
                severity = probs[0] * 5.0
                reason = "Vehicle operation state is normal and stable"
                prediction = "normal"
            elif max_idx == 1:
                status = "warning"
                severity = 30.0 + probs[1] * 25.0
                reason = "Mild vehicle friction or stability anomaly detected"
                prediction = "friction anomaly"
            elif max_idx == 2:
                status = "critical"
                severity = 60.0 + probs[2] * 25.0
                reason = "Critical gyroscopic or acceleration anomaly detected"
                prediction = "gyro anomaly"
            else:
                status = "emergency"
                severity = 85.0 + probs[3] * 15.0
                reason = "Emergency vehicle state anomaly detected"
                prediction = "critical state"

            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=round(float(probs[max_idx]), 4),
                severity=round(severity, 1),
                reason=reason,
                prediction=prediction,
                evidence={
                    "raw_features": raw_features,
                    "scaled_features": [round(val, 4) for val in scaled_features]
                },
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={
                    "probabilities": probs,
                    "max_index": max_idx
                }
            )

        except Exception as e:
            logger.error(f"Error in {self.name()} execution: {e}")
            total_time_ms = (time.perf_counter() - start_time) * 1000.0
            return AgentPredictionResult(
                agent=self.name(),
                status="safe",
                confidence=0.0,
                severity=0.0,
                reason=f"Prediction error: {str(e)}",
                prediction="error",
                evidence={},
                execution_time_ms=round(total_time_ms, 2),
                runtime_used="CPU Fallback",
                device_used="CPU",
                metadata={}
            )

    def confidence(self) -> float:
        return 0.95

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "mechanical_health",
            "monitored_param": "vehicle_operation_state",
            "model": "vehicle_state"
        }
