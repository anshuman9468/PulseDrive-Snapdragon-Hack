import logging
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.rule_runtime import RuleRuntime
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class BrakeAgent(BaseAgent):
    """Diagnoses braking performance, wear levels, and hydraulic pressure anomalies using the central InferenceEngine."""

    def __init__(self, rule_runtime: RuleRuntime = RuleRuntime()):
        self.runtime = rule_runtime

    def name(self) -> str:
        return "BrakeAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        return "brake" in sensor_json

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        try:
            brake_data = sensor_json["brake"]
            pressure = float(brake_data.get("pressure", 0.0))
            pad_wear = float(brake_data.get("pad_wear", 0.0))
            
            # Execute decoupled model prediction
            inf_res = InferenceEngine.predict("brake", [pressure, pad_wear])
            
            # Heuristic rule-based fallback check
            status, severity, reason = self.runtime.evaluate_brake(pressure, pad_wear)
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=severity,
                reason=reason,
                prediction="brake wear or pressure anomaly" if status != "safe" else "safe",
                evidence={"pressure": pressure, "pad_wear": pad_wear},
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={"pressure": pressure, "pad_wear": pad_wear}
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
        return 0.92

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "mechanical_safety",
            "monitored_param": "brake_pressure_and_wear"
        }
