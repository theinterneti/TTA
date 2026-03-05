# agent_orchestration

Multi-agent coordination layer for the Therapeutic Text Adventure. Manages agent lifecycle, capability discovery, message routing, real-time communication, tool invocation, and therapeutic safety enforcement.

## Sub-modules

| Directory | Responsibility |
|---|---|
| `capabilities/` | Auto-discovery and registration of agent capabilities |
| `config/` | Agent and environment configuration schemas |
| `coordinators/` | Redis-backed message coordination between agents |
| `crisis_detection/` | Crisis assessment, escalation, and intervention protocols |
| `openhands_integration/` | OpenHands AI agent client, task queue, result validation |
| `performance/` | Response time monitoring, alerting, analytics, optimization |
| `realtime/` | WebSocket manager, event streaming, progressive feedback, dashboard |
| `registries/` | Redis-backed agent registry with heartbeat tracking |
| `safety_monitoring/` | Global safety service and rule provider |
| `safety_validation/` | Therapeutic content validation engine and models |
| `therapeutic_scoring/` | Scoring rubrics for therapeutic appropriateness |
| `tools/` | Tool registry, invocation service, policy enforcement |

## Key Classes

### `GameplayLoopController` (via `service.py`)
Top-level orchestration service — starts/stops agents, routes messages, aggregates health.

### `RedisAgentRegistry` (`registries/redis_agent_registry.py`)
Registers agents in Redis with TTL-based heartbeats. Used for capability-based routing.

### `CapabilityMatcher` (`capability_matcher.py`)
Selects the best available agent for a task based on declared capabilities and current load.

### `WebSocketManager` (`realtime/websocket_manager.py`)
Manages authenticated WebSocket connections, fan-out event broadcasting, and per-connection filters.

### `TherapeuticSafetyService` (`safety_monitoring/service.py`)
Process-wide singleton that validates messages against therapeutic safety rules before delivery.

### `CrisisInterventionManager` (`crisis_detection/manager.py`)
Detects crisis signals in player messages and triggers escalation protocols.

### `ToolInvocationService` (`tools/`)
Registry-backed tool execution with policy enforcement, timeouts, and Prometheus metrics.

### `OpenHandsClient` (`openhands_integration/client.py`)
Async client for the OpenHands AI agent API — task submission, result polling, model selection.

## Quick Usage

```python
from src.agent_orchestration.service import AgentOrchestrationService

svc = AgentOrchestrationService(config={
    "redis_url": "redis://localhost:6379",
    "agents": [...],
})
await svc.start()

# Route a message to the best capable agent
response = await svc.route_message(
    agent_type="therapeutic",
    message={"role": "user", "content": "I'm feeling anxious today."},
)

await svc.stop()
```

## Circuit Breaker

Every external call is wrapped with a circuit breaker (`circuit_breaker.py`). Configuration is loaded from environment variables or `circuit_breaker_config.py`. Metrics are exposed via Prometheus.

## Real-time Events

```python
from src.agent_orchestration.realtime.event_publisher import EventPublisher

publisher = EventPublisher(redis_url="redis://localhost:6379")
await publisher.publish("agent.started", {"agent_id": "abc123"})
```

WebSocket clients subscribe via `/ws/events` and receive filtered event streams.

## Running Tests

```bash
# Unit tests (no external services)
uv run pytest tests/agent_orchestration/ -m "not redis and not integration" -q

# With Redis
RUN_REDIS_TESTS=1 uv run pytest tests/agent_orchestration/ -q
```
