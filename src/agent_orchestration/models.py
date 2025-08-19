"""
Core data models for Agent Orchestration.

These minimal pydantic models define the contract for agent communication and
orchestration requests/responses. They intentionally avoid implementation
specifics; richer models can be added in follow-up tasks.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    IPA = "input_processor"
    WBA = "world_builder"
    NGA = "narrative_generator"


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class MessagePriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 9


class RoutingKey(BaseModel):
    topic: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AgentId(BaseModel):
    type: AgentType = Field(..., description="Logical agent type")
    instance: Optional[str] = Field(
        default=None, description="Optional instance identifier (for sharded/pooled agents)"
    )


class AgentMessage(BaseModel):
    message_id: str = Field(..., min_length=6)
    sender: AgentId
    recipient: AgentId
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    routing: RoutingKey = Field(default_factory=RoutingKey)
    timestamp: Optional[str] = Field(
        default=None, description="ISO-8601 timestamp; may be set by coordinator"
    )


class OrchestrationRequest(BaseModel):
    session_id: Optional[str] = None
    entrypoint: AgentType = AgentType.IPA
    input: Dict[str, Any] = Field(default_factory=dict)


class OrchestrationResponse(BaseModel):
    response_text: str
    updated_context: Dict[str, Any] = Field(default_factory=dict)
    workflow_metadata: Dict[str, Any] = Field(default_factory=dict)

