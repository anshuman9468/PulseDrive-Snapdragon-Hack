import logging
from datetime import datetime
from typing import Any, Dict, Optional
import asyncio

from app.models.prediction import PredictionRequest, PredictionResponse
from app.orchestrator.orchestrator import AgentOrchestrator
from app.config.database import get_database

logger = logging.getLogger(__name__)

class PredictionService:
    """Service layer coordinating AgentOrchestrator runs, persistence, and live WebSocket streams."""

    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None):
        """Initialize the prediction service with an AgentOrchestrator instance."""
        self.orchestrator = orchestrator or AgentOrchestrator()
        try:
            self.db = get_database()
            self.predictions_collection = self.db["predictions"]
            logger.info("Connected to MongoDB predictions collection")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self.predictions_collection = None

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Generate a health prediction using the multi-agent orchestration pipeline.
        
        Args:
            request: PredictionRequest containing vehicleId and features (sensor telemetry).
            
        Returns:
            PredictionResponse with healthScore, status, confidence, recommendations, and agent details.
        """
        vehicle_id = request.vehicleId
        features = request.features or {}
        
        # Add vehicle context to features dictionary if not present
        if "vehicleId" not in features:
            features["vehicleId"] = vehicle_id

        # Retrieve previous risk score from MongoDB for trend calculation
        last_risk_score = None
        if self.predictions_collection is not None:
            try:
                # Retrieve the latest prediction document sorted by timestamp descending
                last_doc = await asyncio.to_thread(
                    lambda: self.predictions_collection.find_one(
                        {"vehicleId": vehicle_id},
                        sort=[("timestamp", -1)]
                    )
                )
                if last_doc and "riskScore" in last_doc:
                    last_risk_score = float(last_doc["riskScore"])
                    logger.info(f"Retrieved previous risk score of {last_risk_score} for vehicle {vehicle_id}")
            except Exception as e:
                logger.error(f"Error fetching historical risk score for vehicle {vehicle_id}: {e}")

        # 1. Run multi-agent orchestrator with historical context
        orchestrator_result = await self.orchestrator.execute(features, last_risk_score=last_risk_score)

        # Map DecisionEngineResult to PredictionResponse
        status_map = {
            "Safe": "healthy",
            "Warning": "warning",
            "Critical": "critical",
            "Emergency": "emergency"
        }
        status_str = status_map.get(orchestrator_result.vehicle_status, "healthy")
        
        # Calculate overall confidence as average confidence of executed agents
        conf = 1.0
        if orchestrator_result.agent_results:
            conf = sum(r.confidence for r in orchestrator_result.agent_results) / len(orchestrator_result.agent_results)

        primary_rec = (
            orchestrator_result.recommendations[0]
            if orchestrator_result.recommendations
            else "Continue regular maintenance schedule"
        )

        response = PredictionResponse(
            vehicleId=vehicle_id,
            healthScore=orchestrator_result.health_score,
            status=status_str,
            confidence=round(conf, 2),
            recommendation=primary_rec,
            timestamp=datetime.utcnow(),
            riskScore=orchestrator_result.risk_score,
            failureProbability=orchestrator_result.failure_probability,
            riskTrend=orchestrator_result.risk_trend,
            riskConfidence=orchestrator_result.risk_confidence,
            primaryFault=orchestrator_result.primary_fault,
            secondaryFaults=orchestrator_result.secondary_faults,
            agentResults=[r.model_dump() for r in orchestrator_result.agent_results]
        )

        # 2. Persist prediction output to MongoDB
        if self.predictions_collection is not None:
            try:
                # Run DB write in thread pool to prevent blocking event loop
                document = response.model_dump(mode="python")
                await asyncio.to_thread(self.predictions_collection.insert_one, document)
                logger.info(f"Saved health prediction to MongoDB for vehicle {vehicle_id}")
            except Exception as e:
                logger.error(f"Failed to persist prediction to MongoDB: {e}")

        # 3. Stream telemetry and final decision through WebSocket
        try:
            # Local import to avoid any potential circular dependencies at module level
            from app.api.websocket import manager
            
            # Broadcast message structure representing the new analysis
            broadcast_payload = {
                "type": "prediction_update",
                "vehicleId": vehicle_id,
                "healthScore": response.healthScore,
                "status": response.status,
                "riskScore": response.riskScore,
                "failureProbability": response.failureProbability,
                "riskTrend": response.riskTrend,
                "riskConfidence": response.riskConfidence,
                "primaryFault": response.primaryFault,
                "secondaryFaults": response.secondaryFaults,
                "recommendation": response.recommendation,
                "agentResults": response.agentResults,
                "timestamp": response.timestamp.isoformat()
            }
            
            # Non-blocking async broadcast
            await manager.broadcast(broadcast_payload)
            logger.info(f"Streamed prediction update via WebSocket for vehicle {vehicle_id}")
        except Exception as e:
            logger.warning(f"Failed to stream prediction update via WebSocket: {e}")

        return response
