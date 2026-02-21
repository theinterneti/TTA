"""

# Logseq: [[TTA.dev/Agent_orchestration/State]]
Agent state and context models for Orchestration (Task 2.1).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRuntimeStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


class AgentContext(BaseModel):
    user_id: str | None = None
    session_id: str | None = None
    memory: dict[str, Any] = Field(default_factory=dict)
    world_state: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    last_agent: str | None = None


class AgentState(BaseModel):
    agent_id: str = Field(..., description="Unique agent instance identifier")
    status: AgentRuntimeStatus = AgentRuntimeStatus.IDLE
    current_task: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    session_id: str
    user_id: str | None = None
    created_at: str | None = None
    context: AgentContext = Field(default_factory=AgentContext)
