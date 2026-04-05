# Architecture Reference

## Multi-agent pipeline

```
User Input → IPA → WBA → NGA → SSE Stream → Player
```

- **IPA** (Input Processing Agent) — classifies intent, extracts entities, detects emotional tone and safety signals. System prompt at `src/components/ipa/agent.py:59`. Produces `ProcessedInput`.
- **WBA** (World Building Agent) — pure Neo4j context-assembly layer; no LLM calls. Produces `WorldContext`.
- **NGA** (Narrative Generation Agent) — generates therapeutic narrative from ProcessedInput + WorldContext. System prompt at `src/components/nga/agent.py:53`. Streams response to player.

All three wrapped in TTA.dev `FallbackPrimitive(RetryPrimitive(...))` for resilience.

## Data stores

| Store | Role | Status |
|---|---|---|
| Redis | Session cache, workflow state, circuit breaker state | Active |
| Neo4j | Story graph (`Scene -[:LEADS_TO]-> Scene`), character relationships | Active |
| Dolt | Branching universe state (one branch per timeline fork) | Future |

## Key source directories

```
src/
  agent_orchestration/      # Multi-agent coordination, circuit breakers, messaging
  ai_components/            # LLM clients, prompt engineering, prompt registry
  analytics/                # Player analytics, therapeutic metrics
  api_gateway/              # FastAPI + SSE endpoints
  common/                   # Shared utilities, config, database
  components/               # IPA, WBA, NGA, gameplay loop, narrative engine, genesis
  player_experience/        # Player profiles, sessions, frontend
  main.py                   # CLI entrypoint
packages/
  tta-ai-framework/         # Workspace package: AI orchestration
  tta-narrative-engine/     # Workspace package: narrative generation
tests/
  unit/                     # Fast, no external services
  integration/              # Require Redis + Neo4j
  e2e/                      # Require live deployment
```

## Key classes

| Class | Location | Purpose |
|---|---|---|
| `IPAAgent` | `src/components/ipa/agent.py` | Input processing |
| `NGAAgent` | `src/components/nga/agent.py` | Narrative generation |
| `WorldContextBuilder` | `src/components/world_context/` | Neo4j context assembly |
| `CircuitBreaker` | `src/agent_orchestration/circuit_breaker.py` | Redis-persisted error recovery |
| `UnifiedAgentOrchestrator` | `src/agent_orchestration/` | IPA/WBA/NGA coordination |
| `NarrativeEngine` | `src/components/gameplay_loop/narrative/engine.py` | Scene generation |
| `PlayerExperienceManager` | `src/player_experience/` | Player profiles + sessions |

## Circuit breaker pattern

States: `CLOSED → OPEN → HALF_OPEN` with configurable thresholds.
Redis-persisted at `src/agent_orchestration/circuit_breaker.py`.

```python
try:
    result = await circuit_breaker.call(agent_function)
except CircuitBreakerOpenError:
    return fallback_response()
```

## TTA.dev dependency

TTA consumes TTA.dev platform packages via local path sources (editable):
- `ttadev.primitives` — `FallbackPrimitive`, `RetryPrimitive`, `TimeoutPrimitive`, etc.
- `ttadev.observability` — metrics and tracing

Use `WorkflowPrimitive` composition — don't reinvent retry, timeout, or circuit breaker logic.
