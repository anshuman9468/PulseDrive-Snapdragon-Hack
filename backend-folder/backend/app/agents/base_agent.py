from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.prediction_models import AgentPredictionResult

class BaseAgent(ABC):
    """Abstract Base Class for all PulseDrive Diagnostic Agents.
    
    All diagnostic agents must inherit from this class and implement
    all the abstract methods. Agents are stateless.
    """

    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the agent."""
        pass

    @abstractmethod
    def can_handle(self, sensor_json: Dict[str, Any]) -> bool:
        """Determine if this agent can/should process the current sensor packet."""
        pass

    @abstractmethod
    async def predict(self, sensor_json: Dict[str, Any]) -> AgentPredictionResult:
        """Execute the agent prediction on the sensor packet.
        
        This method is async to allow concurrent execution of all agents in the orchestrator.
        """
        pass

    @abstractmethod
    def confidence(self) -> float:
        """Return the agent's base confidence level for its predictions."""
        pass

    @abstractmethod
    def health_metadata(self) -> Dict[str, Any]:
        """Return static or dynamic metadata about the agent's health and configuration."""
        pass
