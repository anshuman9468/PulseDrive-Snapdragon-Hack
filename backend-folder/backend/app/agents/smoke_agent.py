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
            
            # Execute decoupled model prediction
            inf_res = InferenceEngine.predict("smoke", [gas_level, float(digital)])
            
            # Heuristic rule-based fallback check
            status, severity, reason = self.runtime.evaluate_smoke(gas_level, digital)
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=severity,
                reason=reason,
                prediction="smoke or gas level anomaly" if status != "safe" else "safe",
                evidence={"gas_level": gas_level, "digital": digital},
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={"gas_level": gas_level, "digital": digital}
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
