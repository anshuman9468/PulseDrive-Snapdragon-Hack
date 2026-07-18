import logging
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult

logger = logging.getLogger(__name__)

class RecommendationAgent(BaseAgent):
    """Analyzes overall vehicle telemetry to generate proactive maintenance advice."""

    def name(self) -> str:
        return "RecommendationAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        # Recommendation agent is general and can process any sensor JSON that contains any standard parameters
        return any(k in sensor_json for k in ["temperature", "battery_voltage", "smoke", "gyro", "brake"])

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        try:
            recs = []
            status = "safe"
            severity = 0.0

            # 1. Temperature checks
            temp = float(sensor_json.get("temperature", 0.0))
            if temp >= 105.0:
                recs.append("CRITICAL: Pull over and turn off the engine immediately. High risk of engine failure.")
                status = "emergency"
                severity = max(severity, 95.0)
            elif temp >= 90.0:
                recs.append("WARNING: Engine running hot. Check coolant levels and inspect the radiator fan.")
                status = "critical"
                severity = max(severity, 80.0)
            elif temp >= 75.0:
                recs.append("ADVISORY: Engine temperature slightly elevated. Avoid aggressive driving.")
                status = "warning"
                severity = max(severity, 40.0)

            # 2. Battery checks
            voltage = float(sensor_json.get("battery_voltage", 13.0))
            if voltage < 11.5 or voltage > 15.0:
                recs.append("CRITICAL: Severe battery voltage anomaly detected. Inspect alternator and battery connections.")
                status = "critical"
                severity = max(severity, 85.0)
            elif voltage < 12.2:
                recs.append("WARNING: Battery voltage is low. Avoid using high-load electrical accessories.")
                status = "warning"
                severity = max(severity, 50.0)

            # 3. Smoke/Gas checks
            smoke_data = sensor_json.get("smoke", {})
            gas_level = float(smoke_data.get("gas_level", 0.0))
            digital = int(smoke_data.get("digital", 0))
            if digital == 1 or gas_level >= 800.0:
                recs.append("EMERGENCY: Smoke or combustion gas detected in the engine bay! Evacuate immediately.")
                status = "emergency"
                severity = max(severity, 99.0)
            elif gas_level >= 500.0:
                recs.append("CRITICAL: High concentration of volatile gases detected. Check for exhaust leaks.")
                status = "critical"
                severity = max(severity, 80.0)

            # 4. Gyro/Stability checks
            gyro_data = sensor_json.get("gyro", {})
            ax = float(gyro_data.get("ax", 0.0))
            ay = float(gyro_data.get("ay", 0.0))
            az = float(gyro_data.get("az", 9.81))
            import math
            acc_dev = abs(math.sqrt(ax**2 + ay**2 + az**2) - 9.81)
            if acc_dev >= 6.0:
                recs.append("CRITICAL: Significant shock or impact detected. Perform suspension and chassis inspection.")
                status = "critical"
                severity = max(severity, 75.0)
            elif acc_dev >= 2.0:
                recs.append("ADVISORY: Moderate vibrations detected. Check wheel balancing and alignment.")

            # 5. Brake checks
            brake_data = sensor_json.get("brake", {})
            pad_wear = float(brake_data.get("pad_wear", 0.0))
            pressure = float(brake_data.get("pressure", 800.0))
            if pad_wear >= 90.0:
                recs.append("CRITICAL: Brake pads almost fully worn. Replace brake pads immediately.")
                status = "emergency"
                severity = max(severity, 90.0)
            elif pad_wear >= 75.0:
                recs.append("WARNING: Brake pads severely worn. Schedule replacement soon.")
                status = "critical"
                severity = max(severity, 70.0)
            elif pressure > 1800.0:
                recs.append("WARNING: Excessive brake system pressure detected. Inspect master cylinder.")

            if not recs:
                recs.append("All vehicle systems operating within nominal ranges. No action required.")

            reason = f"Generated {len(recs)} recommendation(s) based on live telemetry."
            
            return AgentPredictionResult(
                agent=self.name(),
                status=status,
                confidence=self.confidence(),
                severity=severity,
                reason=reason,
                metadata={"recommendations": recs}
            )
        except Exception as e:
            logger.error(f"Error in {self.name()} execution: {e}")
            return AgentPredictionResult(
                agent=self.name(),
                status="safe",
                confidence=0.0,
                severity=0.0,
                reason=f"Prediction error: {str(e)}",
                metadata={"recommendations": ["Error generating recommendations. Contact support."]}
            )

    def confidence(self) -> float:
        return 0.95

    def health_metadata(self) -> Dict[str, Any]:
        return {
            "type": "advisory",
            "monitored_param": "all_telemetry"
        }
