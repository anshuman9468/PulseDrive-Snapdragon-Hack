import logging
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
# Explicitly import the agents package to trigger registrations of subclasses
import app.agents

logger = logging.getLogger(__name__)

class Planner:
    """Discovers and plans which diagnostic agents should execute for a given sensor packet."""

    def __init__(self) -> None:
        self._agents: List[BaseAgent] = self._discover_agents()

    def _discover_agents(self) -> List[BaseAgent]:
        """Dynamically discover all non-abstract BaseAgent implementations."""
        agents = []
        # Get all subclasses of BaseAgent recursively
        subclasses = self._get_all_subclasses(BaseAgent)
        
        for cls in subclasses:
            # Skip abstract classes if any (though python ABCs won't easily instantiate if abstract)
            try:
                # Instantiate the agent. Each agent must have a parameterless constructor
                agent_instance = cls()
                agents.append(agent_instance)
                logger.info(f"Discovered and initialized agent: {agent_instance.name()}")
            except Exception as e:
                logger.error(f"Failed to instantiate discovered agent class {cls.__name__}: {e}")
                
        return agents

    def _get_all_subclasses(self, cls: type) -> set[type]:
        """Recursively get all subclasses of a class."""
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(self._get_all_subclasses(subclass))
        return subclasses

    def plan(self, sensor_json: Dict[str, Any]) -> List[BaseAgent]:
        """Analyze the input JSON and select all applicable agents.
        
        Args:
            sensor_json: Raw or validated sensor packet.
            
        Returns:
            List of BaseAgent instances that can handle the packet.
        """
        applicable_agents = []
        for agent in self._agents:
            try:
                if agent.can_handle(sensor_json):
                    applicable_agents.append(agent)
                    logger.debug(f"Agent {agent.name()} selected for execution.")
            except Exception as e:
                logger.error(f"Error checking can_handle on agent {agent.name()}: {e}")

        return applicable_agents
