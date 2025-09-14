"""
Interfaces for Agent Orchestration components.

These define contracts to be implemented by concrete backends (e.g., Redis-backed
MessageCoordinator, specific AgentProxy implementations, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .messaging import (
    FailureType,
    MessageResult,
    MessageSubscription,
    ReceivedMessage,
)
from .models import AgentId, AgentMessage, MessageType


class MessageCoordinator(ABC):
    @abstractmethod
    async def send_message(
        self, sender: AgentId, recipient: AgentId, message: AgentMessage
    ) -> MessageResult:
        """Send a message to a specific agent and return delivery result."""

    @abstractmethod
    async def broadcast_message(
        self, sender: AgentId, message: AgentMessage, recipients: list[AgentId]
    ) -> list[MessageResult]:
        """Broadcast a message to multiple agents and return per-recipient results."""

    @abstractmethod
    def subscribe_to_messages(
        self, agent_id: AgentId, message_types: list[MessageType]
    ) -> MessageSubscription:
        """Subscribe an agent to message types and return a subscription handle."""

    # --- Reliability extensions (Task 4.2) ---
    @abstractmethod
    async def receive(
        self, agent_id: AgentId, visibility_timeout: int = 5
    ) -> ReceivedMessage | None:
        """Reserve the next available message (by priority then FIFO) with a visibility timeout."""

    @abstractmethod
    async def ack(self, agent_id: AgentId, token: str) -> bool:
        """Acknowledge successful processing; permanently removes the reserved message."""

    @abstractmethod
    async def nack(
        self,
        agent_id: AgentId,
        token: str,
        failure: FailureType = FailureType.TRANSIENT,
        error: str | None = None,
    ) -> bool:
        """Negative-acknowledge a reserved message. Transient failures are retried with backoff; permanent go to DLQ."""

    @abstractmethod
    async def recover_pending(self, agent_id: AgentId | None = None) -> int:
        """Recover in-flight or scheduled messages back to ready queues. Returns count recovered."""

    @abstractmethod
    async def configure(
        self,
        *,
        queue_size: int | None = None,
        retry_attempts: int | None = None,
        backoff_base: float | None = None,
        backoff_factor: float | None = None,
        backoff_max: float | None = None,
    ) -> None:
        """Update coordinator limits and backoff parameters at runtime."""


class AgentProxy(ABC):
    @abstractmethod
    async def process(self, input_payload: dict) -> dict:
        """Invoke the underlying agent with an input payload and return a structured result."""
