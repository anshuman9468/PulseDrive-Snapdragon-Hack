import logging
from typing import Dict, Any, List
from app.models.prediction_models import AgentPredictionResult

logger = logging.getLogger(__name__)

class DecisionEngine:
    """Classifies the overall vehicle state based on fused telemetry and agent severity scores."""

    def classify(self, risk_score: float, failure_probability: float, agent_results: List[AgentPredictionResult]) -> str:
        """Classify the vehicle safety status based on Risk Score and Failure Probability.
        
        Args:
            risk_score: Computed overall risk score (0-100) from RiskAssessmentAgent.
            failure_probability: Computed failure probability (0.0 to 1.0) from RiskAssessmentAgent.
            agent_results: Original prediction results from individual agents.
            
        Returns:
            Status string: "Safe", "Warning", "Critical", or "Emergency".
        """
        # Check if any agent reported "emergency" with high confidence
        has_emergency_agent = any(
            r.status == "emergency" and r.confidence >= 0.80 for r in agent_results
        )
        # Check if any agent reported "critical" with high confidence
        has_critical_agent = any(
            r.status == "critical" and r.confidence >= 0.80 for r in agent_results
        )

        # Safety-first classification thresholds using Risk & Failure Probability
        if has_emergency_agent or risk_score >= 85.0 or failure_probability >= 0.90:
            status = "EMERGENCY"
        elif has_critical_agent or risk_score >= 60.0 or failure_probability >= 0.50:
            status = "CRITICAL"
        elif risk_score >= 30.0 or failure_probability >= 0.15:
            status = "WARNING"
        else:
            status = "SAFE"

        logger.info(f"Decision Engine classified status as: {status} (Risk Score: {risk_score:.2f}, Fail Prob: {failure_probability:.3f})")
        return status
