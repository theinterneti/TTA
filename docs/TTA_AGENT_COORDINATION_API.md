# TTA Agent Coordination API Specification

**Package:** `tta-agent-coordination`
**Version:** 0.1.0
**Date:** 2025-10-28
**Status:** 📋 SPECIFICATION

---

## Table of Contents

1. [Core Interfaces](#core-interfaces)
2. [Data Models](#data-models)
3. [Redis Coordinator](#redis-coordinator)
4. [Redis Registry](#redis-registry)
5. [Circuit Breaker](#circuit-breaker)
6. [Metrics Protocol](#metrics-protocol)
7. [Exceptions](#exceptions)

---

## Core Interfaces

### MessageCoordinator

Abstract base class for agent message coordination.

```python
from abc import ABC, abstractmethod
from tta_agent_coordination import AgentId, AgentMessage, MessageResult

class MessageCoordinator(ABC):
    """Abstract interface for agent message coordination."""

    @abstractmethod
    async def send_message(
        self,
        sender: AgentId,
        recipient: AgentId,
        message: AgentMessage
    ) -> MessageResult:
        """
        Send a message to a specific agent.

        Args:
            sender: Sending agent identifier
            recipient: Receiving agent identifier
            message: Message to send

        Returns:
            MessageResult with delivery status

        Raises:
            MessageCoordinatorError: If delivery fails
        """

    @abstractmethod
    async def broadcast_message(
        self,
        sender: AgentId,
        message: AgentMessage,
        recipients: list[AgentId]
    ) -> list[MessageResult]:
        """
        Broadcast a message to multiple agents.

        Args:
            sender: Sending agent identifier
            message: Message to broadcast
            recipients: List of recipient agent identifiers

        Returns:
            List of MessageResult (one per recipient)
        """

    @abstractmethod
    def subscribe_to_messages(
        self,
        agent_id: AgentId,
        message_types: list[MessageType]
    ) -> MessageSubscription:
        """
        Subscribe an agent to specific message types.

        Args:
            agent_id: Agent identifier
            message_types: List of message types to subscribe to

        Returns:
            MessageSubscription handle
        """

    @abstractmethod
    async def receive(
        self,
        agent_id: AgentId,
        visibility_timeout: int = 5
    ) -> ReceivedMessage | None:
        """
        Reserve the next available message with visibility timeout.

        Args:
            agent_id: Agent identifier
            visibility_timeout: Seconds before message becomes visible again

        Returns:
            ReceivedMessage if available, None otherwise
        """

    @abstractmethod
    async def ack(self, agent_id: AgentId, token: str) -> bool:
        """
        Acknowledge successful message processing.

        Args:
            agent_id: Agent identifier
            token: Reservation token from receive()

        Returns:
            True if acknowledged, False if token not found
        """

    @abstractmethod
    async def nack(
        self,
        agent_id: AgentId,
        token: str,
        failure: FailureType = FailureType.TRANSIENT,
        error: str | None = None
    ) -> bool:
        """
        Negative-acknowledge message with retry/DLQ logic.

        Args:
            agent_id: Agent identifier
            token: Reservation token from receive()
            failure: Failure type (TRANSIENT, PERMANENT, TIMEOUT)
            error: Optional error message

        Returns:
            True if processed, False if token not found
        """

    @abstractmethod
    async def recover_pending(self, agent_id: AgentId | None = None) -> int:
        """
        Recover expired reservations back to ready queues.

        Args:
            agent_id: Specific agent or None for all agents

        Returns:
            Number of messages recovered
        """

    @abstractmethod
    async def configure(
        self,
        *,
        queue_size: int | None = None,
        retry_attempts: int | None = None,
        backoff_base: float | None = None,
        backoff_factor: float | None = None,
        backoff_max: float | None = None
    ) -> None:
        """
        Update coordinator configuration at runtime.

        Args:
            queue_size: Maximum queue size (default: 10000)
            retry_attempts: Max retry attempts (default: 3)
            backoff_base: Base backoff delay in seconds (default: 1.0)
            backoff_factor: Backoff multiplier (default: 2.0)
            backoff_max: Max backoff delay in seconds (default: 30.0)
        """
```

### AgentRegistry

Abstract base class for agent registration and discovery.

```python
class AgentRegistry(ABC):
    """Abstract interface for agent registration and discovery."""

    @abstractmethod
    def register(self, agent: Agent) -> None:
        """Register an agent."""

    @abstractmethod
    def deregister(self, agent_id: AgentId) -> None:
        """Deregister an agent."""

    @abstractmethod
    async def list_registered(self) -> list[dict[str, Any]]:
        """
        List all registered agents with liveness status.

        Returns:
            List of agent info dictionaries with keys:
            - name: Agent name
            - agent_id: AgentId dict
            - status: Agent status
            - alive: Boolean liveness status
            - last_heartbeat: Timestamp
            - capabilities: Optional capability set
        """

    @abstractmethod
    def start_heartbeats(self) -> None:
        """Start background heartbeat task."""

    @abstractmethod
    def stop_heartbeats(self) -> None:
        """Stop background heartbeat task."""
```

---

## Data Models

### AgentId

Generic agent identifier (no TTA-specific types).

```python
from pydantic import BaseModel, Field

class AgentId(BaseModel):
    """Generic agent identifier."""

    type: str = Field(
        ...,
        description="Agent type identifier (e.g., 'input_processor', 'world_builder')"
    )
    instance: str | None = Field(
        default=None,
        description="Optional instance identifier for sharded/pooled agents"
    )

    # Usage
    agent = AgentId(type="input_processor", instance="worker-1")
```

### MessagePriority

```python
from enum import Enum

class MessagePriority(int, Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 9
```

### MessageType

```python
class MessageType(str, Enum):
    """Generic message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
```

### AgentMessage

```python
class AgentMessage(BaseModel):
    """Generic agent message."""

    message_id: str = Field(..., min_length=6)
    sender: AgentId
    recipient: AgentId
    message_type: MessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: str | None = None
```

### MessageResult

```python
class MessageResult(BaseModel):
    """Result of message delivery attempt."""

    message_id: str
    delivered: bool
    error: str | None = None
```

### ReceivedMessage

```python
class ReceivedMessage(BaseModel):
    """Message received with reservation token."""

    token: str
    queue_message: QueueMessage
    visibility_deadline: str | None = None
```

### FailureType

```python
class FailureType(str, Enum):
    """Message processing failure types."""
    TRANSIENT = "transient"  # Retry with backoff
    PERMANENT = "permanent"  # Send to DLQ
    TIMEOUT = "timeout"      # Retry with backoff
```

---

## Redis Coordinator

### RedisMessageCoordinator

Redis-backed implementation of MessageCoordinator.

```python
from redis.asyncio import Redis
from tta_agent_coordination import RedisMessageCoordinator

coordinator = RedisMessageCoordinator(
    redis=redis_client,
    key_prefix="myapp",  # Default: "ao"
    metrics=None  # Optional metrics implementation
)

# Configure
await coordinator.configure(
    queue_size=5000,
    retry_attempts=5,
    backoff_base=2.0,
    backoff_factor=2.0,
    backoff_max=60.0
)

# Send message
result = await coordinator.send_message(sender, recipient, message)

# Receive message
received = await coordinator.receive(agent_id, visibility_timeout=10)
if received:
    # Process message
    success = await process_message(received.queue_message.message)

    if success:
        await coordinator.ack(agent_id, received.token)
    else:
        await coordinator.nack(
            agent_id,
            received.token,
            failure=FailureType.TRANSIENT,
            error="Processing failed"
        )
```

**Redis Keys:**
- `{prefix}:queue:{type}:{instance}` - Audit list
- `{prefix}:sched:{type}:{instance}:prio:{level}` - Priority zset
- `{prefix}:reserved:{type}:{instance}` - Reserved messages hash
- `{prefix}:reserved_deadlines:{type}:{instance}` - Deadline zset
- `{prefix}:dlq:{type}:{instance}` - Dead-letter queue
- `{prefix}:subs:{type}:{instance}` - Subscriptions set

---

## Redis Registry

### RedisAgentRegistry

Redis-backed implementation of AgentRegistry.

```python
from tta_agent_coordination import RedisAgentRegistry

registry = RedisAgentRegistry(
    redis=redis_client,
    key_prefix="myapp",
    heartbeat_ttl_s=30.0,
    heartbeat_interval_s=10.0,
    enable_events=False
)

# Register agent
registry.register(agent)

# Start heartbeats
registry.start_heartbeats()

# List registered agents
agents = await registry.list_registered()
for agent_info in agents:
    print(f"{agent_info['name']}: alive={agent_info['alive']}")

# Stop heartbeats
registry.stop_heartbeats()

# Deregister
registry.deregister(agent_id)
```

**Redis Keys:**
- `{prefix}:agents:{type}:{instance}` - Agent data JSON
- `{prefix}:agents:index` - Agent keys set
- `{prefix}:capabilities:{type}:{instance}` - Capability JSON
- `{prefix}:capabilities:index` - Capability keys set

---

## Circuit Breaker

### CircuitBreaker

Fault tolerance with Redis-backed state persistence.

```python
from tta_agent_coordination import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    timeout_seconds=60,
    recovery_timeout_seconds=300,
    half_open_max_calls=3,
    success_threshold=2
)

breaker = CircuitBreaker(
    redis=redis_client,
    name="external_service",
    config=config,
    key_prefix="myapp"
)

# Use circuit breaker
try:
    result = await breaker.call(risky_operation, arg1, arg2)
except CircuitBreakerOpenError:
    # Circuit is open, use fallback
    result = fallback_operation()
```

---

## Metrics Protocol

Optional metrics interface for observability.

```python
from typing import Protocol

class MessageMetrics(Protocol):
    """Optional metrics protocol for message coordination."""

    def inc_delivered_ok(self, count: int) -> None:
        """Increment successful deliveries."""

    def inc_delivered_error(self, count: int) -> None:
        """Increment delivery errors."""

    def inc_retries_scheduled(
        self,
        count: int,
        last_backoff_seconds: float
    ) -> None:
        """Increment retry scheduling."""

    def inc_nacks(self, count: int) -> None:
        """Increment negative acknowledgments."""

    def inc_permanent(self, count: int) -> None:
        """Increment permanent failures (DLQ)."""
```

---

## Exceptions

```python
class MessageCoordinatorError(Exception):
    """Base exception for message coordination errors."""

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

class AgentRegistryError(Exception):
    """Base exception for agent registry errors."""
```

---

**Status:** 📋 SPECIFICATION COMPLETE
**Next:** Create extraction specification document



---
**Logseq:** [[TTA.dev/Docs/Tta_agent_coordination_api]]
