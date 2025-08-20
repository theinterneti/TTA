"""
Message passing data structures for Agent Orchestration (Task 2.2, 4.2).

Adds reliability primitives used by MessageCoordinator implementations:
- FailureType to distinguish transient vs permanent failures
- ReceivedMessage reservation wrapper for ack/nack with visibility timeout
- QueueMessage extended with delivery_attempts and timestamps
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from .models import AgentId, AgentMessage, MessageType, MessagePriority


class MessageResult(BaseModel):
    message_id: str
    delivered: bool
    error: Optional[str] = None


class MessageSubscription(BaseModel):
    subscription_id: str
    agent_id: AgentId
    message_types: List[MessageType] = Field(default_factory=list)


class FailureType(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    TIMEOUT = "timeout"


class QueueMessage(BaseModel):
    message: AgentMessage
    priority: MessagePriority = MessagePriority.NORMAL
    enqueued_at: Optional[str] = None
    delivery_attempts: int = 0
    last_error: Optional[str] = None


class ReceivedMessage(BaseModel):
    token: str
    queue_message: QueueMessage
    visibility_deadline: Optional[str] = None
