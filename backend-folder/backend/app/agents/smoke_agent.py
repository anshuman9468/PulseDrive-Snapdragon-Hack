import logging
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.rule_runtime import RuleRuntime
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class SmokeAgent(BaseAgent):
    """Diagnoses cabin or engine smoke and fire risk conditions using the central InferenceEngine."""

    def __init__(self, rule_runtime: RuleRuntime = RuleRuntime()):
        self.runtime = rule_runtime

    def name(self) -> str:
        return "SmokeAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        return "smoke" in sensor_json

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        try:
            smoke_data = sensor_json["smoke"]
            gas_level = float(smoke_data.get("gas_level", 0.0))
            digital = int(smoke_data.get("digital", 0))
            
            # Map digital input to model Active Low expected input
            digital_model = 1.0 - float(digital)
            gas_level_scaled = gas_level / 1000.0
            
            # Execute decoupled model prediction
            inf_res = InferenceEngine.predict("smoke", [digital_model, gas_level_scaled])
            probs = inf_res["probabilities"]
            
            # Class mapping: Index 0 is Anomaly, Index 1 is Normal
            p_anomaly = probs[0]
            p_normal = probs[1]
            max_idx = 0 if p_anomaly > p_normal else 1
            
            # Heuristic rule-based fallback check for safety limits
            status, severity, reason = self.runtime.evaluate_smoke(gas_level, digital)
            
            prediction = "smoke or gas level anomaly" if status != "safe" else "safe"
            confidence = float(p_anomaly) if status != "safe" else float(p_normal)
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=round(confidence, 4),
                severity=severity,
                reason=reason,
                prediction=prediction,
                evidence={
                    "gas_level": gas_level,
                    "digital": digital,
                    "model_features": [digital_model, gas_level_scaled]
                },
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={
                    "gas_level": gas_level,
                    "digital": digital,
                    "probabilities": probs,
                    "max_index": max_idx
                }
            )
        except Exception as e:
            logger.error(f"Error in {self.name()} execution: {e}")
            return AgentPredictionResult(
                agent=self.name(),
                status="safe",
                confidence=0.0,
                severity=0.0,
                reason=f"Prediction error: {str(e)}",
                prediction="error",
                evidence={},
                execution_time_ms=0.0,
                runtime_used="CPU Fallback",
                device_used="CPU",
                metadata={}
            )

    def confidence(self) -> float:
        return 0.98

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "safety",
            "monitored_param": "smoke_gas_level",
            "warning_threshold": 300.0
        }
