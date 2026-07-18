import logging
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.models.prediction_models import AgentPredictionResult

logger = logging.getLogger(__name__)

class RiskAssessmentAgent(BaseAgent):
    """Aggregates all diagnostic agent results and performs safety-first risk assessment."""

    def name(self) -> str:
        return "RiskAssessmentAgent"

    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        # Never triggered by standard parallel planning; runs as a meta-agent
        return False

    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        # Standard predict implementation returning default safe status
        return AgentPredictionResult(
            agent=self.name(),
            status="safe",
            confidence=1.0,
            severity=0.0,
            reason="Meta-agent executed via assess interface.",
            prediction="safe",
            execution_time_ms=0.0,
            runtime_used="CPU Fallback",
            device_used="CPU"
        )

    def confidence(self) -> float:
        """Return the agent's base confidence level."""
        return 1.0

    def health_metadata(self) -> Dict[str, Any]:
        """Return metadata about the agent's health and configuration."""
        return {
            "status": "healthy",
            "type": "meta-agent",
            "description": "Calculates composite risk score and failure probability across all subsystem diagnostics."
        }

    def assess(
        self, 
        agent_results: List[AgentPredictionResult], 
        last_risk_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Assess overall vehicle risk metrics based on individual agent diagnostics and history.
        
        Args:
            agent_results: Results from all active diagnostic agents.
            last_risk_score: The previous risk score from MongoDB (if any).
            
        Returns:
            Dict containing:
                - risk_score: float (0.0 to 100.0)
                - failure_probability: float (0.0 to 1.0)
                - primary_fault: str
                - secondary_faults: List[str]
                - confidence: float (0.0 to 1.0)
                - risk_trend: str ("increasing", "stable", "decreasing")
        """
        logger.info("Executing Risk Assessment Agent...")
        
        if not agent_results:
            return {
                "risk_score": 0.0,
                "failure_probability": 0.0,
                "primary_fault": "No faults detected",
                "secondary_faults": [],
                "confidence": 1.0,
                "risk_trend": "stable"
            }

        anomalies = [r for r in agent_results if r.status != "safe"]
        
        if not anomalies:
            # All systems are safe
            trend = "stable"
            if last_risk_score is not None and last_risk_score > 5.0:
                trend = "decreasing"
                
            return {
                "risk_score": 0.0,
                "failure_probability": 0.0,
                "primary_fault": "No faults detected",
                "secondary_faults": [],
                "confidence": 0.95,
                "risk_trend": trend
            }

        # Sort anomalies by severity * confidence to get the dominant fault
        anomalies.sort(key=lambda x: x.severity * x.confidence, reverse=True)
        dominant = anomalies[0]
        
        # 1. Primary and Secondary Faults
        primary_fault = dominant.reason
        secondary_faults = []
        for a in anomalies[1:]:
            if a.reason not in secondary_faults and a.reason != primary_fault:
                secondary_faults.append(a.reason)

        # 2. Risk Score (0-100)
        # Combine severities using a safety-first scaling method
        max_severity = dominant.severity
        other_severities_sum = sum(a.severity * a.confidence for a in anomalies[1:])
        risk_score = min(100.0, max_severity + (other_severities_sum * 0.15))
        risk_score = round(risk_score, 1)

        # 3. Failure Probability (0.0 to 1.0)
        # Map risk score exponentially to probability of total failure
        if risk_score >= 85.0:
            failure_probability = 0.90 + (risk_score - 85.0) * 0.006  # Caps near 0.99
        elif risk_score >= 50.0:
            failure_probability = 0.50 + (risk_score - 50.0) * 0.011  # 0.50 to 0.885
        elif risk_score >= 20.0:
            failure_probability = 0.10 + (risk_score - 20.0) * 0.013  # 0.10 to 0.49
        else:
            failure_probability = (risk_score / 20.0) * 0.10
            
        failure_probability = min(0.99, max(0.0, round(failure_probability, 3)))

        # 4. Confidence (0.0 to 1.0)
        # Fused confidence is the confidence of the dominant anomaly weighted by its severity
        confidence = dominant.confidence

        # 5. Risk Trend ("increasing", "stable", "decreasing")
        trend = "stable"
        if last_risk_score is not None:
            diff = risk_score - last_risk_score
            if diff > 2.0:
                trend = "increasing"
            elif diff < -2.0:
                trend = "decreasing"
        
        logger.info(f"Risk Assessment Complete: Risk Score={risk_score}, Trend={trend}, Failure Prob={failure_probability}")

        return {
            "risk_score": risk_score,
            "failure_probability": failure_probability,
            "primary_fault": primary_fault,
            "secondary_faults": secondary_faults,
            "confidence": confidence,
            "risk_trend": trend
        }
