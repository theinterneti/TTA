"""
Workflow definitions and orchestration responses (Task 2.1).
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .models import AgentType


class WorkflowType(str, Enum):
    INPUT_PROCESSING = "input_processing"
    WORLD_BUILDING = "world_building"
    NARRATIVE_GENERATION = "narrative_generation"
    COLLABORATIVE = "collaborative"


class ErrorHandlingStrategy(str, Enum):
    FAIL_FAST = "fail_fast"
    RETRY = "retry"
    SKIP_ON_ERROR = "skip_on_error"


class AgentStep(BaseModel):
    agent: AgentType
    name: Optional[str] = None
    timeout_seconds: Optional[int] = None


class TimeoutConfiguration(BaseModel):
    per_step_seconds: Optional[int] = None
    total_seconds: Optional[int] = None


class WorkflowDefinition(BaseModel):
    workflow_type: WorkflowType
    agent_sequence: List[AgentStep] = Field(default_factory=list)
    parallel_steps: List[List[AgentStep]] = Field(default_factory=list)
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.FAIL_FAST
    timeout_config: TimeoutConfiguration = Field(default_factory=TimeoutConfiguration)


class OrchestrationResponse(BaseModel):
    response_text: str
    updated_context: Dict[str, Any] = Field(default_factory=dict)
    workflow_metadata: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    therapeutic_validation: Optional[Dict[str, Any]] = None

