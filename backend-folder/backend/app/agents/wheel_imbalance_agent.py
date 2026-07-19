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

class WheelImbalanceAgent(BaseAgent):
    """Diagnoses wheel imbalance issues using MPU1 gyroscope telemetry via the central InferenceEngine."""

    def __init__(self):
        # Load the scaler if present
        scaler_path = "app/runtime/scalers/wheel_imbalance_scaler.pkl"
        self.scaler = None
        if os.path.exists(scaler_path):
            try:
                self.scaler = joblib.load(scaler_path)
                if hasattr(self.scaler, "feature_names_in_"):
                    del self.scaler.feature_names_in_
                logger.info("WheelImbalanceAgent loaded scaler successfully")
            except Exception as e:
                logger.warning(f"WheelImbalanceAgent failed to load scaler: {e}. Using manual scaling.")
        
        # Scaling defaults (StandardScaler mean and scale)
        self.means = [1693.9138321995465, 67.84693877551021, -207.75283446712018]
        self.scales = [2019.415658126098, 5490.372119810026, 2917.857333278522]

    def name(self) -> str:
        return "WheelImbalanceAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        # Check for gyro telemetry or specific MPU1 gyroscope keys
        return "gyro" in sensor_json or any(k in sensor_json for k in ["MPU1_Gyro_X", "mpu1_gx"])

    def _extract_features(self, sensor_json: Dict[str, Any]) -> List[float]:
        gyro_data = sensor_json.get("gyro", {})
        mpu1_data = sensor_json.get("mpu1", {})
        
        def get_val(key_list, default=0.0):
            for k in key_list:
                if k in sensor_json:
                    return float(sensor_json[k])
                if k in gyro_data:
                    return float(gyro_data[k])
                if k in mpu1_data:
                    return float(mpu1_data[k])
            return default

        gx = get_val(["MPU1_Gyro_X", "mpu1_gx", "gx1", "gx"], 1693.9)
        gy = get_val(["MPU1_Gyro_Y", "mpu1_gy", "gy1", "gy"], 67.8)
        gz = get_val(["MPU1_Gyro_Z", "mpu1_gz", "gz1", "gz"], -207.7)
        
        return [gx, gy, gz]

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
            inf_res = InferenceEngine.predict("wheel_imbalance", scaled_features)
            probs = inf_res["probabilities"]
            
            # Class mapping: [Normal, Imbalanced]
            max_idx = probs.index(max(probs))
            
            if max_idx == 0:
                status = "safe"
                severity = probs[0] * 5.0
                reason = "Wheel balance and rotation levels normal"
                prediction = "normal"
            else:
                # Class 1 is imbalanced
                if probs[1] > 0.8:
                    status = "critical"
                else:
                    status = "warning"
                severity = 40.0 + probs[1] * 50.0
                reason = f"Wheel imbalance detected: probability {round(probs[1] * 100, 1)}%"
                prediction = "imbalanced"

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
            "monitored_param": "wheel_balance",
            "model": "wheel_imbalance"
        }
