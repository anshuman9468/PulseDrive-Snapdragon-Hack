import logging
from typing import List, Dict, Any, Tuple
from app.models.prediction_models import AgentPredictionResult

logger = logging.getLogger(__name__)

class FusionEngine:
    """Merges evidence from multiple diagnostic agents, resolves conflicts, and computes health scores."""

    def fuse(self, agent_results: List[AgentPredictionResult]) -> Dict[str, Any]:
        """Fuse results from all executed agents.
        
        Args:
            agent_results: List of prediction results from individual agents.
            
        Returns:
            Dict containing:
                - health_score: float (0-100)
                - risk_score: float (0-100)
                - primary_fault: str
                - secondary_faults: List[str]
                - severity: float (0-100)
                - recommendations: List[str]
        """
        if not agent_results:
            return {
                "health_score": 100.0,
                "risk_score": 0.0,
                "primary_fault": "No faults detected",
                "secondary_faults": [],
                "severity": 0.0,
                "recommendations": ["No actions required."]
            }

        # Group by status to separate safe and anomalous inputs
        anomalies = [r for r in agent_results if r.status != "safe"]
        
        # Recommendations aggregator
        recommendations = []
        for result in agent_results:
            # If the agent has recommendations in metadata, extract them
            if result.metadata and "recommendations" in result.metadata:
                recommendations.extend(result.metadata["recommendations"])

        # Default values if all systems are safe
        if not anomalies:
            return {
                "health_score": 100.0,
                "risk_score": 0.0,
                "primary_fault": "No faults detected",
                "secondary_faults": [],
                "severity": 0.0,
                "recommendations": recommendations if recommendations else ["All systems safe. Continue regular maintenance."]
            }

        # Resolve conflicts & find dominant fault
        # We sort anomalies by severity * confidence to get the most significant verified fault
        anomalies.sort(key=lambda x: x.severity * x.confidence, reverse=True)
        
        dominant = anomalies[0]
        primary_fault = dominant.reason
        
        secondary_faults = []
        for a in anomalies[1:]:
            # Avoid duplicate fault reasons
            if a.reason not in secondary_faults and a.reason != primary_fault:
                secondary_faults.append(a.reason)

        # Compute overall severity using a conservative safety-first formula:
        # We take the maximum severity and add a fraction of secondary severities
        max_severity = dominant.severity
        other_severities_sum = sum(a.severity * a.confidence for a in anomalies[1:])
        
        # Combine severities, capping at 100
        overall_severity = min(100.0, max_severity + (other_severities_sum * 0.15))
        
        # Health score is the inverse of overall severity
        health_score = max(0.0, 100.0 - overall_severity)
        risk_score = overall_severity

        return {
            "health_score": round(health_score, 1),
            "risk_score": round(risk_score, 1),
            "primary_fault": primary_fault,
            "secondary_faults": secondary_faults,
            "severity": round(overall_severity, 1),
            "recommendations": recommendations
        }
