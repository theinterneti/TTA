# Circuit Breaker Migration TODOs

**Status:** In progress
**Created:** 2026-03-04

---

## Overview

TTA contains a production-grade async circuit breaker with Redis-backed state persistence, a
metrics collector, a Pydantic config schema, and a multi-breaker registry. These are generic
resilience primitives with no TTA-specific domain logic — good candidates for extraction to
`tta-dev-primitives` so other projects built on TTA.dev can reuse them.

**TTA.dev already has** a `recovery/circuit_breaker.py`, but it is dev-tooling only (sync,
in-memory, no metrics, "Error Recovery Framework for Development Scripts"). The TTA production
CB is a completely separate, more capable implementation that supersedes it.

---

## Source files (TTA)

| File | Lines | Responsibility |
|---|---|---|
| `src/agent_orchestration/circuit_breaker.py` | 473 | Core state machine (CLOSED/OPEN/HALF_OPEN), Redis persistence, async lock, `CircuitBreakerOpenError` |
| `src/agent_orchestration/circuit_breaker_metrics.py` | 366 | `CircuitBreakerMetricsCollector`, `CircuitBreakerLogger`, correlation-ID structured logging |
| `src/agent_orchestration/circuit_breaker_config.py` | 330 | `CircuitBreakerConfigSchema` (Pydantic v2), env-var loader, `CircuitBreakerConfigManager` |
| `src/agent_orchestration/circuit_breaker_registry.py` | 294 | `CircuitBreakerRegistry` — manages N breakers, background cleanup, Redis sync |

**TTA consumers (files that import from the above):**

| File | Import | Usage |
|---|---|---|
| `src/agent_orchestration/__init__.py` | All 4 CB symbols | Re-exports in package public API |
| `src/agent_orchestration/openhands_integration/workflow_integration.py` | `CircuitBreakerOpenError` | `except CircuitBreakerOpenError` in step execution |
| `src/agent_orchestration/workflow_manager.py` | `CircuitBreakerOpenError` | `except CircuitBreakerOpenError` in workflow runner |

---

## TODO 1 — Spec (high priority)

**Write extraction spec for circuit breaker migration**

Decisions to nail down before writing any code:

### 1.1 Redis coupling strategy

The TTA circuit breaker requires an async Redis client (`self._redis`) for state persistence
across restarts. To be a useful platform primitive the persistence layer must be **optional and
pluggable**:

```
Option A — Abstract backend (preferred)
  CircuitBreaker accepts a StateBackend protocol:
    class StateBackend(Protocol):
        async def load(self, key: str) -> dict | None: ...
        async def save(self, key: str, value: dict, ttl: int) -> None: ...

  Concrete backends:
    InMemoryBackend  — no deps, default, suitable for single-process use
    RedisBackend     — wraps aioredis/redis.asyncio, state survives restarts

Option B — Optional redis dep, None = in-memory fallback
  Keep current constructor signature but make redis=None the default;
  in-memory dict replaces Redis calls when redis is None.

  Pro: minimal refactor.
  Con: redis and in-memory behaviour slightly different (TTL, scan_iter, sadd).
```

**Recommendation:** Option A. Produces cleaner code and makes the backend testable without Redis.

### 1.2 Relationship to existing TTA.dev `recovery/circuit_breaker.py`

The existing file is dev-tooling (retry decorators + a sync in-memory CB). It should be:
- Renamed to `recovery/dev_scripts.py` or kept as-is with a deprecation notice, **or**
- Merged: keep the `with_retry` / `with_retry_async` decorators there; replace the simple
  `CircuitBreaker` class with a thin alias to the new `CircuitBreakerPrimitive`

**Recommendation:** Keep retry decorators in `recovery/circuit_breaker.py`, replace the old
`CircuitBreaker` class (move it to `_legacy.py` or delete), introduce the new
`CircuitBreakerPrimitive` as the canonical export.

### 1.3 Versioning

The TTA.dev `tta-dev-primitives` is currently at v1.3.1. Adding the circuit breaker is additive
(no breaking changes to existing exports) — bump to **v1.3.2**.

### 1.4 Naming

| TTA name | TTA.dev primitive name | Rationale |
|---|---|---|
| `CircuitBreaker` | `CircuitBreakerPrimitive` | Consistent with `RetryPrimitive`, `FallbackPrimitive` naming |
| `CircuitBreakerConfig` | `CircuitBreakerConfig` | Keep — it's a config object, not a primitive |
| `CircuitBreakerState` | `CircuitBreakerState` | Keep |
| `CircuitBreakerOpenError` | `CircuitBreakerOpenError` | Keep |
| `CircuitBreakerRegistry` | `CircuitBreakerRegistry` | Keep |
| `CircuitBreakerMetricsCollector` | `CircuitBreakerMetricsCollector` | Keep |
| `CircuitBreakerLogger` | `CircuitBreakerLogger` | Keep |

### 1.5 Spec deliverable

Produce a spec doc (similar to `docs/REDIS_MESSAGE_COORDINATOR_ANALYSIS.md`) covering:
- Generic vs. TTA-specific analysis (same format as the RMC analysis)
- API surface to export from `tta_dev_primitives.recovery`
- Migration path for TTA consumers
- Test plan (unit: InMemoryBackend; integration: RedisBackend)

---

## TODO 2 — Architecture (high priority)

**Design TTA.dev package layout for circuit breaker primitives**

### Target layout in `tta-dev-primitives`

```
platform/primitives/src/tta_dev_primitives/recovery/
  __init__.py          ← add CircuitBreakerPrimitive, CircuitBreakerRegistry, etc. to exports
  circuit_breaker.py   ← NEW: production circuit breaker (ported from TTA, pluggable backend)
  backends/
    __init__.py
    base.py            ← StateBackend protocol
    memory.py          ← InMemoryBackend (no deps)
    redis.py           ← RedisBackend (requires redis-asyncio, optional dep)
  circuit_breaker_metrics.py  ← ported from TTA
  circuit_breaker_config.py   ← ported from TTA (Pydantic v2)
  circuit_breaker_registry.py ← ported from TTA
  compensation.py      ← existing
  fallback.py          ← existing
  retry.py             ← existing
  timeout.py           ← existing
```

### `pyproject.toml` changes

Add an optional `resilience` extra for redis-backed state:

```toml
[project.optional-dependencies]
resilience = [
    "redis[asyncio]>=5.0.0",
]
```

The `InMemoryBackend` must work with zero extra deps so the circuit breaker is usable without
installing redis.

### `recovery/__init__.py` additions

```python
from .circuit_breaker import CircuitBreakerPrimitive
from .circuit_breaker_config import CircuitBreakerConfig, CircuitBreakerConfigManager
from .circuit_breaker_metrics import CircuitBreakerMetricsCollector, CircuitBreakerLogger
from .circuit_breaker_registry import CircuitBreakerRegistry
from .backends import InMemoryBackend, RedisBackend, StateBackend
```

Top-level `tta_dev_primitives/__init__.py` should also re-export `CircuitBreakerPrimitive` and
`CircuitBreakerOpenError` for discoverability.

---

## TODO 3 — Implementation (medium priority)

**Port to tta-dev-primitives v1.3.2**

### Steps

1. Create `recovery/backends/base.py` — `StateBackend` Protocol
2. Create `recovery/backends/memory.py` — `InMemoryBackend`
3. Create `recovery/backends/redis.py` — `RedisBackend` (thin wrapper around the Redis calls
   currently inside `CircuitBreaker._load_state`, `_persist_state`, etc.)
4. Port `circuit_breaker.py` → replace raw Redis calls with `self._backend: StateBackend`
5. Port `circuit_breaker_metrics.py` — no Redis dependency, minimal changes
6. Port `circuit_breaker_config.py` — Pydantic v2, no Redis dependency, minimal changes
7. Port `circuit_breaker_registry.py` → update to use `StateBackend`; remove raw Redis scan calls
   (delegate to `RedisBackend.scan_states()` or similar)
8. Write tests:
   - `tests/recovery/test_circuit_breaker.py` — pure unit tests using `InMemoryBackend`
   - `tests/recovery/test_circuit_breaker_redis.py` — integration tests (marked
     `@pytest.mark.integration`), require Redis
9. Update `recovery/__init__.py` and top-level `__init__.py`
10. Bump version to `1.3.2` in `pyproject.toml` and `__version__`

### What changes vs. what stays the same

| Aspect | Change? | Notes |
|---|---|---|
| State machine logic (CLOSED/OPEN/HALF_OPEN) | No | Port verbatim |
| Redis key format | No | Keep `{pfx}:cb:state:{name}` etc. in RedisBackend |
| Metrics collection | No | Port verbatim |
| Config schema (Pydantic) | Minor | Already v2; check `model.dict()` → `model.model_dump()` |
| `CircuitBreaker.__init__` signature | Yes | Replace `redis` param with `backend: StateBackend \| None = None` |
| Global singleton instances | Minimal | Keep `get_circuit_breaker_metrics()` pattern |

---

## TODO 4 — Migration (medium priority)

**Update TTA consumers to import from TTA.dev**

### Steps

1. After v1.3.2 is tagged and installed, update TTA imports in three places:

```python
# BEFORE (in TTA consumer files)
from src.agent_orchestration.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenError, CircuitBreakerState,
)
from src.agent_orchestration.circuit_breaker_metrics import ...
from src.agent_orchestration.circuit_breaker_config import ...
from src.agent_orchestration.circuit_breaker_registry import ...

# AFTER
from tta_dev_primitives.recovery import (
    CircuitBreakerPrimitive as CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerState,
    CircuitBreakerMetricsCollector,
    CircuitBreakerLogger,
    CircuitBreakerRegistry,
    RedisBackend,
)
```

2. Update `src/agent_orchestration/__init__.py` — change `from .circuit_breaker import ...`
   to forward from `tta_dev_primitives.recovery` so downstream code that imports from
   `agent_orchestration` keeps working unchanged.

3. Update the `CircuitBreaker` instantiation sites to pass a `RedisBackend`:

```python
# BEFORE
cb = CircuitBreaker(redis=redis_client, name="my-cb")

# AFTER
from tta_dev_primitives.recovery.backends import RedisBackend
cb = CircuitBreakerPrimitive(name="my-cb", backend=RedisBackend(redis_client))
```

4. Run the quality gate and tests:
   ```bash
   uv run pytest -q -m "not integration and not neo4j and not redis" tests/
   DOLT_PASSWORD=doltpass uv run pytest -m integration tests/
   ```

---

## TODO 5 — Cleanup (low priority)

**Remove source from TTA after migration**

Only after TODO 4 is merged and CI passes:

1. Delete the four source files:
   - `src/agent_orchestration/circuit_breaker.py`
   - `src/agent_orchestration/circuit_breaker_metrics.py`
   - `src/agent_orchestration/circuit_breaker_config.py`
   - `src/agent_orchestration/circuit_breaker_registry.py`

2. Update `src/agent_orchestration/__init__.py` — remove the now-dead internal imports; keep the
   re-exports (they now forward from `tta_dev_primitives.recovery`).

3. Update any test files that import directly from `src.agent_orchestration.circuit_breaker*`.

4. Final quality gate run.

---

## TODO 6 — Follow-up spec (medium priority)

**Evaluate message coordination primitives for subsequent extraction**

The `RedisMessageCoordinator` has already been partially analysed in
`docs/REDIS_MESSAGE_COORDINATOR_ANALYSIS.md`. Key findings from that analysis:

- **95% generic** — all message coordination logic (priority queues, reservation semantics, DLQ,
  backpressure, retry) is reusable
- **5% TTA-specific** — only the `AgentType` enum values (IPA, WBA, NGA)
- Target package: `tta-agent-coordination` (already exists as a platform package in TTA.dev)

Next steps for this follow-up:

1. Read `packages/tta-ai-framework/src/tta_ai/orchestration/coordinators/redis_message_coordinator.py`
   in full (346 lines)
2. Compare with the duplicate at `src/agent_orchestration/coordinators/redis_message_coordinator.py`
   — decide which is canonical; delete the other
3. Write a full extraction spec (same format as the circuit breaker spec above), covering:
   - Abstract `MessageCoordinator` interface
   - Concrete `RedisMessageCoordinator` implementation
   - Replacement `AgentType` abstraction (generic string IDs vs. enum)
   - Target location in `tta-agent-coordination` package
   - Migration plan for TTA consumers

---

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-04 | Use pluggable StateBackend (Option A) over redis=None fallback | Cleaner separation; InMemoryBackend is independently testable |
| 2026-03-04 | Bump to v1.3.2 (not 1.4.0) | CB addition is additive; no existing exports change |
| 2026-03-04 | Rename to `CircuitBreakerPrimitive` in TTA.dev | Naming consistency with existing `RetryPrimitive` etc. |
| 2026-03-04 | TTA re-exports unchanged | Avoids breaking TTA code that imports from `agent_orchestration` |


---