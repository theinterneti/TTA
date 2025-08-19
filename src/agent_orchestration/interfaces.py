"""
Interfaces for Agent Orchestration components.

These define contracts to be implemented by concrete backends (e.g., Redis-backed
MessageCoordinator, specific AgentProxy implementations, etc.).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import AgentId, AgentMessage, MessageType
from .messaging import MessageResult, MessageSubscription


class MessageCoordinator(ABC):
    @abstractmethod
    async def send_message(self, sender: AgentId, recipient: AgentId, message: AgentMessage) -> MessageResult:
        """Send a message to a specific agent and return delivery result."""

    @abstractmethod
    async def broadcast_message(self, sender: AgentId, message: AgentMessage, recipients: List[AgentId]) -> List[MessageResult]:
        """Broadcast a message to multiple agents and return per-recipient results."""

    @abstractmethod
    def subscribe_to_messages(self, agent_id: AgentId, message_types: List[MessageType]) -> MessageSubscription:
        """Subscribe an agent to message types and return a subscription handle."""


class AgentProxy(ABC):
    @abstractmethod
    async def process(self, input_payload: dict) -> dict:
        """Invoke the underlying agent with an input payload and return a structured result."""

