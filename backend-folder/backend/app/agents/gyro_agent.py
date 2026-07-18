import logging
import time
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.rule_runtime import RuleRuntime
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class GyroAgent(BaseAgent):
    """Diagnoses mechanical vibration, roll, pitch, and stability anomalies using the abstract InferenceEngine."""

    def __init__(self, rule_runtime: RuleRuntime = RuleRuntime()):
        self.runtime = rule_runtime

    def name(self) -> str:
        return "GyroAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        return "gyro" in sensor_json

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        start_time = time.perf_counter()
        try:
            gyro_data = sensor_json["gyro"]
            ax = float(gyro_data.get("ax", 0.0))
            ay = float(gyro_data.get("ay", 0.0))
            az = float(gyro_data.get("az", 9.81))  # Default gravity
            
            # Key sensor evidence
            evidence = {"ax": ax, "ay": ay, "az": az}
            
            # Execute predictions via the decoupled InferenceEngine
            incline_res = InferenceEngine.predict("gyro_incline", [ax, ay, az])
            vibration_res = InferenceEngine.predict("vibration", [ax, ay, az])
            
            incline_probs = incline_res["probabilities"]
            vibration_probs = vibration_res["probabilities"]
            
            # Probs mapping: [Safe, Warning, Critical/Emergency]
            incline_idx = incline_probs.index(max(incline_probs))
            vibration_idx = vibration_probs.index(max(vibration_probs))
            
            # Compute severities dynamically
            incline_severity = incline_probs[1] * 45.0 + incline_probs[2] * 85.0
            vibration_severity = vibration_probs[1] * 40.0 + vibration_probs[2] * 80.0
            
            severity = max(incline_severity, vibration_severity)
            max_idx = max(incline_idx, vibration_idx)
            
            if max_idx == 2:
                status = "critical" if severity < 85.0 else "emergency"
            elif max_idx == 1:
                status = "warning"
            else:
                status = "safe"
                
            # Construct combined diagnostic reasons
            reasons = []
            if incline_idx == 2:
                reasons.append("Dangerous tilt or rollover risk detected")
            elif incline_idx == 1:
                reasons.append("Moderate incline warning")
            
            if vibration_idx == 2:
                reasons.append("Critical mechanical vibration anomaly detected")
            elif vibration_idx == 1:
                reasons.append("Mild vibration warning")
            
            reason = "; ".join(reasons) if reasons else "Gyro stability and mechanical vibration levels normal"
            prediction = "tilt/vibration anomaly detected" if reasons else "safe"
            
            # Gather model execution details
            runtime_used = incline_res["runtime_used"] if incline_res["runtime_used"] != "CPU Fallback" else vibration_res["runtime_used"]
            device_used = incline_res["device_used"] if incline_res["device_used"] != "CPU" else vibration_res["device_used"]
            execution_time_ms = incline_res["execution_time_ms"] + vibration_res["execution_time_ms"]
            
            # Map execution mode for backward compatible tests (fallback is CPU Fallback)
            exec_mode = "onnx" if runtime_used in ["ONNX Runtime", "Qualcomm QNN Runtime"] else "rule_fallback"
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=round(severity, 1),
                reason=reason,
                prediction=prediction,
                evidence=evidence,
                execution_time_ms=round(execution_time_ms, 2),
                runtime_used=runtime_used,
                device_used=device_used,
                metadata={
                    "ax": ax,
                    "ay": ay,
                    "az": az,
                    "incline_probabilities": incline_probs,
                    "vibration_probabilities": vibration_probs,
                    "execution_mode": exec_mode
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
        return 0.94

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "mechanical_stability",
            "monitored_param": "vibration_and_orientation",
            "models": ["gyro_incline", "vibration"]
        }
