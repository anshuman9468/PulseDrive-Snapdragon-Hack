import asyncio
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.orchestrator.planner import Planner
from app.orchestrator.fusion_engine import FusionEngine
from app.orchestrator.decision_engine import DecisionEngine
from app.models.prediction_models import DecisionEngineResult, AgentPredictionResult

logger = logging.getLogger(__name__)

def parse_sensor_timestamp(ts_val) -> Optional[datetime]:
    """Parse sensor timestamp to a datetime object, supporting various formats."""
    if not ts_val:
        return None
    if isinstance(ts_val, (int, float)):
        return datetime.utcfromtimestamp(ts_val)
    if isinstance(ts_val, str):
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(ts_val, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
        except Exception:
            pass
    return None

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

    async def _emit_trace(self, prediction_id: str, vehicle_id: str, stage: str, details: Dict[str, Any]) -> None:
        """Helper to broadcast real-time agent execution traces over WebSocket."""
        try:
            from app.websocket.manager import manager
            payload = {
                "type": "execution_trace",
                "predictionId": prediction_id,
                "vehicleId": vehicle_id,
                "stage": stage,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "details": details
            }
            await manager.broadcast(payload)
            logger.debug(f"Emitted trace event: {stage}")
        except Exception as e:
            logger.warning(f"Failed to broadcast trace event for stage '{stage}': {e}")

    async def execute(self, sensor_json: Dict[str, Any], last_risk_score: Optional[float] = None) -> DecisionEngineResult:
        """Run the multi-agent orchestration pipeline.
        
        Args:
            sensor_json: Validated JSON input dictionary representing sensor telemetry.
            last_risk_score: Previous risk score from database context.
            
        Returns:
            DecisionEngineResult combining all agent outputs, fused classification, and execution context.
        """
        start_time_perf = time.perf_counter()
        prediction_id = uuid.uuid4().hex
        vehicle_id = sensor_json.get("vehicleId") or "VH001"

        logger.info(f"Initializing Agentic Diagnosis Pipeline for Prediction ID: {prediction_id}...")

        # 1. Emit Prediction Started Trace
        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Prediction Started",
            details={"input": {k: v for k, v in sensor_json.items() if k != "vehicleId"}}
        )
        
        # 2. Discover applicable agents
        applicable_agents = self.planner.plan(sensor_json)
        print("Planner selected agents", flush=True)
        logger.info(f"Planner selected agents: {[a.name() for a in applicable_agents]}")

        # Construct Planner Complete Trace details
        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Planner Complete",
            details={
                "selected_agents": [a.name() for a in applicable_agents],
                "reason": "Planner evaluated sensor values and triggered relevant agents based on domain rules."
            }
        )

        if not applicable_agents:
            print("Fusion complete", flush=True)
            print("Risk Assessment complete", flush=True)
            print("Decision complete", flush=True)
            print("Recommendation complete", flush=True)
            
            end_time = datetime.utcnow()
            exec_time_ms = (time.perf_counter() - start_time_perf) * 1000.0
            sensor_dt = parse_sensor_timestamp(sensor_json.get("timestamp"))
            if sensor_dt:
                if sensor_dt.tzinfo is not None:
                    sensor_dt = sensor_dt.replace(tzinfo=None)
                pipeline_latency_ms = (end_time - sensor_dt).total_seconds() * 1000.0
            else:
                pipeline_latency_ms = exec_time_ms

            execution_context = {
                "predictionId": prediction_id,
                "timestamp": end_time.isoformat() + "Z",
                "vehicleId": vehicle_id,
                "executionTimeMs": round(exec_time_ms, 2),
                "pipelineLatencyMs": round(pipeline_latency_ms, 2),
                "graph": {
                    "nodes": [
                        {
                            "id": "telemetry_ingest",
                            "label": "Telemetry Ingest",
                            "type": "input",
                            "dependencies": [],
                            "metadata": {"input": sensor_json, "output": sensor_json}
                        },
                        {
                            "id": "planner",
                            "label": "Agent Planner",
                            "type": "planner",
                            "dependencies": ["telemetry_ingest"],
                            "metadata": {"selected_agents": []}
                        }
                    ],
                    "edges": [{"from": "telemetry_ingest", "to": "planner"}]
                }
            }

            await self._emit_trace(
                prediction_id=prediction_id,
                vehicle_id=vehicle_id,
                stage="Prediction Finished",
                details={
                    "execution_time_ms": round(exec_time_ms, 2),
                    "pipeline_latency_ms": round(pipeline_latency_ms, 2)
                }
            )

            return DecisionEngineResult(
                vehicle_status="SAFE",
                health_score=100.0,
                risk_score=0.0,
                failure_probability=0.0,
                risk_trend="stable",
                risk_confidence=1.0,
                primary_fault="No active agents",
                secondary_faults=[],
                recommendations=["No active agents to evaluate systems. Sensor packet may be empty."],
                agent_results=[],
                execution_context=execution_context
            )

        # Separate RecommendationAgent from diagnostic agents
        diagnostic_agents = [a for a in applicable_agents if a.name() != "RecommendationAgent"]
        recommendation_agent_instance = next((a for a in applicable_agents if a.name() == "RecommendationAgent"), None)
        if not recommendation_agent_instance:
            from app.agents.recommendation_agent import RecommendationAgent
            recommendation_agent_instance = RecommendationAgent()

        # 3. Parallel execution of diagnostic agents using asyncio.gather
        async def run_agent(agent):
            agent_start = time.perf_counter()
            res = await agent.predict(sensor_json)
            agent_duration_ms = (time.perf_counter() - agent_start) * 1000.0
            
            # Populate execution runtime telemetry info if not already set
            res.execution_time_ms = round(res.execution_time_ms or agent_duration_ms, 2)
            
            print(f"{agent.name()} executed", flush=True)
            logger.info(f"{agent.name()} executed")
            
            # Emit Agent Complete Trace
            await self._emit_trace(
                prediction_id=prediction_id,
                vehicle_id=vehicle_id,
                stage=f"{agent.name()} Complete",
                details={
                    "model_name": res.metadata.get("model_name", agent.name()),
                    "version": res.metadata.get("model_version", "1.0.0"),
                    "backend": res.runtime_used,
                    "device": res.device_used,
                    "confidence": res.confidence,
                    "execution_time_ms": res.execution_time_ms,
                    "prediction": res.prediction,
                    "status": res.status,
                    "evidence": res.evidence,
                    "reason": res.reason
                }
            )
            return res

        agent_results: List[AgentPredictionResult] = []
        if diagnostic_agents:
            tasks = [run_agent(a) for a in diagnostic_agents]
            agent_results = list(await asyncio.gather(*tasks))

        # 4. Decision Fusion
        fused_data = self.fusion_engine.fuse(agent_results)
        print("Fusion complete", flush=True)
        logger.info("Fusion complete")

        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Fusion Complete",
            details={
                "health_score": fused_data["health_score"],
                "active_risks_count": len([r for r in agent_results if r.status != "safe"])
            }
        )

        # 5. Meta-agent Risk Assessment execution
        from app.agents.risk_assessment_agent import RiskAssessmentAgent
        risk_agent = RiskAssessmentAgent()
        risk_res = risk_agent.assess(agent_results, last_risk_score=last_risk_score)
        print("Risk Assessment complete", flush=True)
        logger.info("Risk Assessment complete")

        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Risk Assessment Complete",
            details={
                "health_score": fused_data["health_score"],
                "risk_score": risk_res["risk_score"],
                "failure_probability": risk_res["failure_probability"],
                "primary_fault": risk_res["primary_fault"],
                "secondary_faults": risk_res["secondary_faults"]
            }
        )

        # 6. Final safety status classification
        vehicle_status = self.decision_engine.classify(
            risk_res["risk_score"], 
            risk_res["failure_probability"], 
            agent_results
        )
        print("Decision complete", flush=True)
        logger.info("Decision complete")

        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Decision Complete",
            details={
                "vehicle_status": vehicle_status,
                "explanation": f"Decision Engine classified vehicle status as {vehicle_status} based on Risk Score ({risk_res['risk_score']}) and Failure Probability ({risk_res['failure_probability']})."
            }
        )

        # 7. Pass decision to Recommendation Agent to generate maintenance actions
        rec_result = await recommendation_agent_instance.predict(sensor_json, decision=vehicle_status)
        print("Recommendation complete", flush=True)
        logger.info("Recommendation complete")

        recommendations = rec_result.metadata.get("recommendations", [])

        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Recommendation Complete",
            details={
                "immediate_actions": [r for r in recommendations if any(kw in r.lower() for kw in ["immediate", "critical", "stop", "inspect"])][:2],
                "preventive_actions": recommendations,
                "priority": "HIGH" if vehicle_status in ["CRITICAL", "EMERGENCY"] else "MEDIUM" if vehicle_status == "WARNING" else "LOW"
            }
        )

        # Merge RecommendationAgent result into the agent_results list
        all_agent_results = agent_results + [rec_result]

        # Calculate timing and latency
        end_time = datetime.utcnow()
        exec_time_ms = (time.perf_counter() - start_time_perf) * 1000.0
        sensor_dt = parse_sensor_timestamp(sensor_json.get("timestamp"))
        if sensor_dt:
            if sensor_dt.tzinfo is not None:
                sensor_dt = sensor_dt.replace(tzinfo=None)
            pipeline_latency_ms = (end_time - sensor_dt).total_seconds() * 1000.0
        else:
            pipeline_latency_ms = exec_time_ms

        # Build Graph structure
        nodes = []
        edges = []

        # Add Ingestion Node
        nodes.append({
            "id": "telemetry_ingest",
            "label": "Telemetry Ingest",
            "type": "input",
            "dependencies": [],
            "metadata": {
                "input": {k: v for k, v in sensor_json.items() if k not in ["vehicleId", "timestamp"]},
                "output": {k: v for k, v in sensor_json.items() if k not in ["vehicleId", "timestamp"]}
            }
        })

        # Add Planner Node
        nodes.append({
            "id": "planner",
            "label": "Agent Planner",
            "type": "planner",
            "dependencies": ["telemetry_ingest"],
            "metadata": {
                "selected_agents": [a.name() for a in applicable_agents]
            }
        })
        edges.append({"from": "telemetry_ingest", "to": "planner"})

        # Add Agent Nodes and Edges
        agent_ids = []
        for agent in applicable_agents:
            if agent.name() == "RecommendationAgent":
                continue
            agent_id = agent.name()
            agent_ids.append(agent_id)
            
            res_val = next((r for r in agent_results if r.agent == agent.name()), None)
            res_dump = res_val.model_dump() if res_val else {}
            
            nodes.append({
                "id": agent_id,
                "label": agent_id.replace("Agent", " Agent"),
                "type": "agent",
                "dependencies": ["planner"],
                "metadata": {
                    "model_name": res_dump.get("metadata", {}).get("model_name", agent.name()),
                    "version": res_dump.get("metadata", {}).get("model_version", "1.0.0"),
                    "backend": res_dump.get("runtime_used", "CPU Fallback"),
                    "device": res_dump.get("device_used", "CPU"),
                    "execution_time_ms": res_dump.get("execution_time_ms", 0.0),
                    "output": res_dump
                }
            })
            edges.append({"from": "planner", "to": agent_id})

        # Add Fusion Node
        fusion_deps = agent_ids if agent_ids else ["planner"]
        nodes.append({
            "id": "fusion",
            "label": "Decision Fusion",
            "type": "fusion",
            "dependencies": fusion_deps,
            "metadata": {
                "output": fused_data
            }
        })
        for dep in fusion_deps:
            edges.append({"from": dep, "to": "fusion"})

        # Add Risk Node
        nodes.append({
            "id": "risk_assessment",
            "label": "Risk Assessment Agent",
            "type": "risk",
            "dependencies": fusion_deps,
            "metadata": {
                "output": risk_res
            }
        })
        for dep in fusion_deps:
            edges.append({"from": dep, "to": "risk_assessment"})

        # Add Decision Node
        nodes.append({
            "id": "decision",
            "label": "Decision Engine",
            "type": "decision",
            "dependencies": ["fusion", "risk_assessment"],
            "metadata": {
                "output": {"vehicle_status": vehicle_status}
            }
        })
        edges.append({"from": "fusion", "to": "decision"})
        edges.append({"from": "risk_assessment", "to": "decision"})

        # Add Recommendation Node
        nodes.append({
            "id": "recommendation",
            "label": "Recommendation Agent",
            "type": "recommendation",
            "dependencies": ["decision"],
            "metadata": {
                "output": rec_result.model_dump()
            }
        })
        edges.append({"from": "decision", "to": "recommendation"})

        # Build final execution context
        execution_context = {
            "predictionId": prediction_id,
            "timestamp": end_time.isoformat() + "Z",
            "vehicleId": vehicle_id,
            "executionTimeMs": round(exec_time_ms, 2),
            "pipelineLatencyMs": round(pipeline_latency_ms, 2),
            "graph": {
                "nodes": nodes,
                "edges": edges
            }
        }

        # 8. Emit Prediction Finished Trace
        await self._emit_trace(
            prediction_id=prediction_id,
            vehicle_id=vehicle_id,
            stage="Prediction Finished",
            details={
                "execution_time_ms": round(exec_time_ms, 2),
                "pipeline_latency_ms": round(pipeline_latency_ms, 2)
            }
        )

        # 7. Format and return DecisionEngineResult
        result = DecisionEngineResult(
            vehicle_status=vehicle_status,
            health_score=fused_data["health_score"],
            risk_score=risk_res["risk_score"],
            failure_probability=risk_res["failure_probability"],
            risk_trend=risk_res["risk_trend"],
            risk_confidence=risk_res["confidence"],
            primary_fault=risk_res["primary_fault"],
            secondary_faults=risk_res["secondary_faults"],
            recommendations=recommendations,
            agent_results=all_agent_results,
            execution_context=execution_context
        )

        logger.info(f"Diagnosis complete. Vehicle status: {result.vehicle_status}, Health Score: {result.health_score}")
        return result
