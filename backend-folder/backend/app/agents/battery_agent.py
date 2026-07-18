import logging
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult
from app.runtime.rule_runtime import RuleRuntime
from app.runtime.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

class BatteryAgent(BaseAgent):
    """Diagnoses electrical system and battery health conditions using the central InferenceEngine."""

    def __init__(self, rule_runtime: RuleRuntime = RuleRuntime()):
        self.runtime = rule_runtime

    def name(self) -> str:
        return "BatteryAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        return "battery_voltage" in sensor_json

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        try:
            voltage = float(sensor_json["battery_voltage"])
            
            # Execute decoupled model prediction
            inf_res = InferenceEngine.predict("battery_voltage", [voltage])
            
            # Heuristic rule-based fallback check
            status, severity, reason = self.runtime.evaluate_battery(voltage)
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=severity,
                reason=reason,
                prediction="battery anomaly" if status != "safe" else "safe",
                evidence={"battery_voltage": voltage},
                execution_time_ms=inf_res["execution_time_ms"],
                runtime_used=inf_res["runtime_used"],
                device_used=inf_res["device_used"],
                metadata={"raw_voltage": voltage}
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
        return 0.90

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "electrical",
            "monitored_param": "battery_voltage",
            "normal_range": "12.2V - 14.5V"
        }
