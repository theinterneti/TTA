# Circuit Breaker Migration — Logseq TODOs

> Copy these blocks into your Logseq journal to track the Circuit Breaker extraction from `TTA` → `TTA.dev` (v0.2.0).

---

- TODO Write extraction spec for Circuit Breaker migration to TTA.dev #dev-todo
  type:: spec
  priority:: high
  package:: tta-dev-primitives
  - Define the public API surface for the circuit breaker in `tta-dev-primitives`
  - Document the 3-state model (CLOSED → OPEN → HALF_OPEN), Redis persistence contract, and configuration schema
  - Specify which modules migrate: `circuit_breaker.py`, `circuit_breaker_config.py`, `circuit_breaker_registry.py`, `circuit_breaker_metrics.py`
  - Specify the companion modules that must co-migrate: `adapters.py` (RetryConfig, retry_with_backoff), observability utilities from `monitoring.py`
  - Define the backward-compatibility shim for TTA consumers during transition

- TODO Design TTA.dev architecture for circuit breaker primitives #dev-todo
  type:: architecture
  priority:: high
  package:: tta-dev-primitives
  - Plan the package layout under `tta-dev-primitives` (e.g., `resilience/circuit_breaker/`, `resilience/retry/`, `observability/`)
  - Define the Redis persistence interface as an abstract backend (allow non-Redis implementations)
  - Design the configuration system (env vars, Pydantic schema, sensible defaults)
  - Plan the metrics/observability integration points (correlation IDs, structured logging)
  - Ensure async-first API with `asyncio.Lock` thread safety

- TODO Implement circuit breaker in TTA.dev tta-dev-primitives v0.2.0 #dev-todo
  type:: implementation
  priority:: medium
  package:: tta-dev-primitives
  - Port `circuit_breaker.py` with full 3-state pattern and Redis persistence
  - Port `circuit_breaker_config.py` with Pydantic validation and env-var overrides
  - Port `circuit_breaker_registry.py` for central management and cleanup
  - Port `circuit_breaker_metrics.py` for metrics collection
  - Port `adapters.py` RetryConfig and `retry_with_backoff()` with circuit breaker integration
  - Add comprehensive unit tests (target ≥85% coverage, ≥85% mutation score)
  - Publish as part of `tta-dev-primitives` v0.2.0

- TODO Migrate TTA consumers to use TTA.dev circuit breaker #dev-todo
  type:: migration
  priority:: medium
  package:: tta-ai-framework
  - Replace `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker*.py` with imports from `tta-dev-primitives`
  - Replace `src/agent_orchestration/circuit_breaker*.py` with imports from `tta-dev-primitives`
  - Update `RetryConfig` and `retry_with_backoff` imports in all consumers
  - Update `pyproject.toml` to add `tta-dev-primitives>=0.2.0` dependency
  - Run full test suite to validate no regressions

- TODO Remove circuit breaker source from TTA after migration #dev-todo
  type:: cleanup
  priority:: low
  package:: tta-ai-framework
  - Delete `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker.py`
  - Delete `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker_config.py`
  - Delete `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker_registry.py`
  - Delete `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker_metrics.py`
  - Delete `src/agent_orchestration/circuit_breaker.py`, `circuit_breaker_config.py`, `circuit_breaker_registry.py`, `circuit_breaker_metrics.py`
  - Remove companion observability code that migrated (monitoring.py circuit breaker logger/metrics collector)
  - Verify no remaining references to deleted modules
  - Run full test suite to confirm clean removal

- TODO Migrate message coordination primitives to TTA.dev #dev-todo
  type:: spec
  priority:: medium
  package:: tta-dev-primitives
  - Evaluate `messaging.py` (QueueMessage, ack/nack, DLQ), `interfaces.py` (MessageCoordinator), and `coordinators/redis_message_coordinator.py` for extraction
  - These are tightly coupled to the circuit breaker and should follow in a subsequent TTA.dev release
  - Write spec for the reliability primitives module (circuit breaker + retry + messaging as a coherent unit)
