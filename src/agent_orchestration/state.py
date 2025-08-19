"""
Agent state and context models for Orchestration (Task 2.1).
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentRuntimeStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


class AgentContext(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    memory: Dict[str, Any] = Field(default_factory=dict)
    world_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_agent: Optional[str] = None


class AgentState(BaseModel):
    agent_id: str = Field(..., description="Unique agent instance identifier")
    status: AgentRuntimeStatus = AgentRuntimeStatus.IDLE
    current_task: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    context: AgentContext = Field(default_factory=AgentContext)

