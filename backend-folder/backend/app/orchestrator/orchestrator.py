import asyncio
import logging
from typing import Dict, Any, List, Optional
from app.orchestrator.planner import Planner
from app.orchestrator.fusion_engine import FusionEngine
from app.orchestrator.decision_engine import DecisionEngine
from app.models.prediction_models import DecisionEngineResult, AgentPredictionResult

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Enterprise-grade agent coordinator executing multi-agent vehicle diagnosis in parallel."""

    def __init__(
        self,
        planner: Planner = Planner(),
        fusion_engine: FusionEngine = FusionEngine(),
        decision_engine: DecisionEngine = DecisionEngine()
    ) -> None:
        self.planner = planner
        self.fusion_engine = fusion_engine
        self.decision_engine = decision_engine

    async def execute(self, sensor_json: Dict[str, Any], last_risk_score: Optional[float] = None) -> DecisionEngineResult:
        """Run the multi-agent orchestration pipeline.
        
        Args:
            sensor_json: Validated JSON input dictionary representing sensor telemetry.
            last_risk_score: Previous risk score from database context.
            
        Returns:
            DecisionEngineResult combining all agent outputs and fused classification.
        """
        logger.info("Initializing Agentic Diagnosis Pipeline...")
        
        # 1. Discover applicable agents
        applicable_agents = self.planner.plan(sensor_json)
        if not applicable_agents:
            logger.warning("No diagnostic agents found that can handle this sensor packet.")
            return DecisionEngineResult(
                vehicle_status="Safe",
                health_score=100.0,
                risk_score=0.0,
                failure_probability=0.0,
                risk_trend="stable",
                risk_confidence=1.0,
                primary_fault="No active agents",
                secondary_faults=[],
                recommendations=["No active agents to evaluate systems. Sensor packet may be empty."],
                agent_results=[]
            )

        logger.info(f"Discovered {len(applicable_agents)} applicable agent(s). Executing concurrently...")

        # 2. Parallel execution using asyncio.gather
        tasks = [agent.predict(sensor_json) for agent in applicable_agents]
        agent_results: List[AgentPredictionResult] = await asyncio.gather(*tasks)

        logger.info("Agent execution completed. Passing results to Fusion Engine...")

        # 3. Decision Fusion
        fused_data = self.fusion_engine.fuse(agent_results)

        # 4. Meta-agent Risk Assessment execution
        from app.agents.risk_assessment_agent import RiskAssessmentAgent
        risk_agent = RiskAssessmentAgent()
        risk_res = risk_agent.assess(agent_results, last_risk_score=last_risk_score)

        # 5. Final safety status classification
        vehicle_status = self.decision_engine.classify(
            risk_res["risk_score"], 
            risk_res["failure_probability"], 
            agent_results
        )

        # Clean/Format recommendations
        recommendations = fused_data.get("recommendations", [])
        # De-duplicate recommendations
        seen = set()
        unique_recs = []
        for r in recommendations:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)

        # 6. Format and return DecisionEngineResult
        result = DecisionEngineResult(
            vehicle_status=vehicle_status,
            health_score=fused_data["health_score"],
            risk_score=risk_res["risk_score"],
            failure_probability=risk_res["failure_probability"],
            risk_trend=risk_res["risk_trend"],
            risk_confidence=risk_res["confidence"],
            primary_fault=risk_res["primary_fault"],
            secondary_faults=risk_res["secondary_faults"],
            recommendations=unique_recs,
            agent_results=agent_results
        )

        logger.info(f"Diagnosis complete. Vehicle status: {result.vehicle_status}, Health Score: {result.health_score}")
        return result
