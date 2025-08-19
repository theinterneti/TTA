"""
Message passing data structures for Agent Orchestration (Task 2.2).
"""
from __future__ import annotations

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


class QueueMessage(BaseModel):
    message: AgentMessage
    priority: MessagePriority = MessagePriority.NORMAL
    enqueued_at: Optional[str] = None
    delivery_attempts: int = 0

