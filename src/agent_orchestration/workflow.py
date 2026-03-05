"""

# Logseq: [[TTA.dev/Agent_orchestration/Workflow]]
Workflow definitions and orchestration responses (Task 2.1).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .models import AgentType


class WorkflowType(StrEnum):
    INPUT_PROCESSING = "input_processing"
    WORLD_BUILDING = "world_building"
    NARRATIVE_GENERATION = "narrative_generation"
    COLLABORATIVE = "collaborative"


class ErrorHandlingStrategy(StrEnum):
    FAIL_FAST = "fail_fast"
    RETRY = "retry"
    SKIP_ON_ERROR = "skip_on_error"


class AgentStep(BaseModel):
    agent: AgentType
    name: str | None = None
    timeout_seconds: int | None = None


class TimeoutConfiguration(BaseModel):
    per_step_seconds: int | None = None
    total_seconds: int | None = None


class WorkflowDefinition(BaseModel):
    workflow_type: WorkflowType
    agent_sequence: list[AgentStep] = Field(default_factory=list)
    parallel_steps: list[list[AgentStep]] = Field(default_factory=list)
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.FAIL_FAST
    timeout_config: TimeoutConfiguration = Field(default_factory=TimeoutConfiguration)


class OrchestrationResponse(BaseModel):
    response_text: str
    updated_context: dict[str, Any] = Field(default_factory=dict)
    workflow_metadata: dict[str, Any] = Field(default_factory=dict)
    performance_metrics: dict[str, Any] = Field(default_factory=dict)
    therapeutic_validation: dict[str, Any] | None = None
