"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Messaging]]
Message passing data structures for Agent Orchestration (Task 2.2, 4.2).

Adds reliability primitives used by MessageCoordinator implementations:
- FailureType to distinguish transient vs permanent failures
- ReceivedMessage reservation wrapper for ack/nack with visibility timeout
- QueueMessage extended with delivery_attempts and timestamps
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .models import AgentId, AgentMessage, MessagePriority, MessageType


class MessageResult(BaseModel):
    message_id: str
    delivered: bool
    error: str | None = None


class MessageSubscription(BaseModel):
    subscription_id: str
    agent_id: AgentId
    message_types: list[MessageType] = Field(default_factory=list)


class FailureType(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    TIMEOUT = "timeout"


class QueueMessage(BaseModel):
    message: AgentMessage
    priority: MessagePriority = MessagePriority.NORMAL
    enqueued_at: str | None = None
    delivery_attempts: int = 0
    last_error: str | None = None


class ReceivedMessage(BaseModel):
    token: str
    queue_message: QueueMessage
    visibility_deadline: str | None = None
