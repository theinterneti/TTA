# Circuit Breaker Usage

- **Component:** Circuit breaker delegation and usage contract
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

The circuit breaker protects expensive or failure-prone workflow boundaries by failing fast after repeated errors and cautiously probing for recovery. In TTA, the current implementation is in `src/agent_orchestration/circuit_breaker.py` and is intended for use around external workflow dependencies such as agent/LLM calls.

## Scope / Responsibilities

- Define the supported circuit states and transitions.
- Define the persisted Redis shape and TTLs.
- Define which boundaries are appropriate for circuit-breaker wrapping.
- Keep therapeutic and narrative policy outside the breaker itself.
- Surface usage caveats where implementation and intent differ.

## Requirements

### Functional Requirements
- **FR-1:** Circuit states must be `CLOSED`, `OPEN`, and `HALF_OPEN`.
- **FR-2:** Configuration must expose at least `failure_threshold`, `timeout_seconds`, `recovery_timeout_seconds`, `half_open_max_calls`, and `success_threshold`.
- **FR-3:** State persistence must use `{prefix}:cb:state:{name}` with a 24-hour TTL and metrics persistence must use `{prefix}:cb:metrics:{name}` with a 7-day TTL.
- **FR-4:** `call()` must reject requests immediately while the circuit is `OPEN` unless the open timeout has elapsed.
- **FR-5:** Successful HALF_OPEN calls must contribute toward a return to `CLOSED`; repeated failures must reopen the circuit.
- **FR-6:** State transitions should emit metrics/logging hooks via the circuit-breaker metrics helpers.

### Intended Usage Boundaries
- Wrap external agent/LLM/network calls, not pure domain transformations.
- Prefer placement around adapter boundaries (`IPAAdapter`, `WBAAdapter`, `NGAAdapter`) or similar external integrations.
- Do not use circuit breakers to encode therapeutic escalation policy.

### Caveat
- The current `call()` path transitions from `OPEN` to `HALF_OPEN` using `timeout_seconds`; `recovery_timeout_seconds` exists in config but is not the field currently used for that transition. This is documented as a draft mismatch rather than hidden.

### Non-Functional Requirements
- **NFR-1:** Breaker behavior must survive process restarts through Redis persistence.
- **NFR-2:** Metrics must make failure rate and state changes inspectable.
- **NFR-3:** Concurrency control must prevent inconsistent local state transitions.

## Interfaces / Dependencies

- `CircuitBreakerState`
- `CircuitBreakerConfig`
- `CircuitBreakerMetrics`
- `CircuitBreaker.initialize()`, `call()`, and state-persistence helpers
- Redis cache/persistence documented in `specs/persistence/redis-session-cache.md`

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_circuit_breaker.py` validates state values, success/failure accounting, opening after threshold, fail-fast behavior, HALF_OPEN behavior, reset behavior, and custom configuration.

Validation should verify both runtime state transitions and persisted Redis state/metrics behavior.

## Acceptance Criteria

- State machine, Redis keys, and metrics are documented from current code.
- Appropriate usage boundaries are named clearly.
- The `recovery_timeout_seconds` vs `timeout_seconds` caveat is explicit.
- Test anchors cover the documented behavior.
