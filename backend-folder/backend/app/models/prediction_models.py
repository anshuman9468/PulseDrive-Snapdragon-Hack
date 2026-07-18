from pydantic import BaseModel, Field
from typing import Dict, Any, List

class AgentPredictionResult(BaseModel):
    agent: str = Field(..., description="Name of the reporting agent")
    status: str = Field(..., description="Status reported by the agent (safe, warning, critical, emergency)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    severity: float = Field(..., ge=0.0, le=100.0, description="Severity score of the issue (0 to 100)")
    reason: str = Field(..., description="Explanation of why this prediction was made")
    prediction: str = Field(default="safe", description="Detailed prediction status description")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Key sensor evidence prompting the diagnosis")
    execution_time_ms: float = Field(default=0.0, description="Execution time of the inference in milliseconds")
    runtime_used: str = Field(default="CPU Fallback", description="The runtime execution engine used")
    device_used: str = Field(default="CPU", description="The physical execution unit")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata from the agent run")

class DecisionEngineResult(BaseModel):
    vehicle_status: str = Field(..., description="Overall vehicle status (Safe, Warning, Critical, Emergency)")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Overall health score (0 to 100)")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall risk score (0 to 100)")
    failure_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall failure probability (0.0 to 1.0)")
    risk_trend: str = Field(default="stable", description="Risk trend (increasing, stable, decreasing)")
    risk_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence of the risk assessment")
    primary_fault: str = Field(..., description="Dominant fault identified")
    secondary_faults: List[str] = Field(default_factory=list, description="Secondary faults identified")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    agent_results: List[AgentPredictionResult] = Field(default_factory=list, description="Raw results from individual agents")
