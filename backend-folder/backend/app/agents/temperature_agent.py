import logging
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.rule_runtime import RuleRuntime
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class TemperatureAgent(BaseAgent):
    """Diagnoses engine overheating or abnormal temperature conditions using the central InferenceEngine."""

    def __init__(self, rule_runtime: RuleRuntime = RuleRuntime()):
        self.runtime = rule_runtime

    def name(self) -> str:
        return "TemperatureAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        return "temperature" in sensor_json

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        try:
            temp = float(sensor_json["temperature"])
            
            # Execute decoupled model prediction
            inf_res = InferenceEngine.predict("temperature", [temp])
            
            # Heuristic rule-based fallback check
            status, severity, reason = self.runtime.evaluate_temperature(temp)
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=severity,
                reason=reason,
                prediction="temperature anomaly" if status != "safe" else "safe",
                evidence={"temperature": temp},
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={"raw_temperature": temp}
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
        return 0.95

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "diagnostic",
            "monitored_param": "engine_temperature",
            "critical_threshold": 90.0,
            "emergency_threshold": 105.0
        }
