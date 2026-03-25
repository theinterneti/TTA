# Primitive Mapping

- **Component:** TTA ↔ TTA.dev primitive dependency map
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

This spec records how TTA components consume TTA.dev-style primitives without collapsing domain logic into infrastructure. It is grounded in `ARCHITECTURE.md` and the current orchestration, persistence, and observability code anchors.

## Scope / Responsibilities

- Apply the repository decision rule: “Could it work for a recipe app?”
- Identify which concerns belong in TTA.dev primitives versus TTA domain code.
- Give each major TTA area a short primitive map that later specs can reuse.
- Prevent therapeutic/narrative semantics from leaking into universal infrastructure packages.

## Requirements

### Mapping Rules
- **Rule-1:** If a pattern is domain-agnostic (`retry`, `timeout`, `circuit breaker`, generic tracing), it belongs conceptually to TTA.dev.
- **Rule-2:** If a pattern is narrative-, therapeutic-, or gameplay-specific, it remains in TTA.
- **Rule-3:** TTA may wrap TTA.dev primitives with domain-specific policy, naming, and semantics.

### Current Mapping
| TTA area | Current anchors | Primitive dependency | Ownership |
|---|---|---|---|
| IPA / WBA / NGA adapters | `src/agent_orchestration/adapters.py` | Retry with backoff, timeout | Shared primitive, TTA-owned usage |
| Unified workflow | `src/agent_orchestration/unified_orchestrator.py` | State persistence, coordination, tracing | TTA orchestration on top of primitives |
| Circuit breaker | `src/agent_orchestration/circuit_breaker.py` | Circuit breaker pattern | Conceptually TTA.dev, currently implemented in TTA |
| Observability setup | `src/observability_integration/apm_setup.py` | OpenTelemetry tracing and metrics | Conceptually TTA.dev, TTA-owned integration |
| Therapeutic safety | `src/agent_orchestration/therapeutic_safety.py` and subpackages | None beyond generic telemetry | TTA |
| Emotional safety / therapeutic integration | `src/components/gameplay_loop/narrative/` | None beyond generic telemetry | TTA |
| Session/world persistence | `src/player_experience/database/` | Cache/timeouts around storage | TTA domain persistence |

### Non-Functional Requirements
- **NFR-1:** Primitive mapping should reduce duplication across specs.
- **NFR-2:** The map must describe current ownership honestly even where the architecture points to eventual extraction.
- **NFR-3:** Specs should name primitive dependencies without implying that every primitive already lives in a separate repository package.

## Interfaces / Dependencies

- `ARCHITECTURE.md` decision tree and dependency sections.
- `RetryConfig` / `retry_with_backoff()`.
- `CircuitBreaker`, `CircuitBreakerConfig`.
- `initialize_observability()`, `get_tracer()`, `get_meter()`.
- Agent workflow/persistence specs in this directory tree.

## Testing / Validation

Validation is primarily architectural: check that new specs and new code continue to place retry/timeout/circuit-breaker/observability in the infrastructure bucket and keep therapeutic/narrative rules in TTA.

Relevant anchors include `tests/agent_orchestration/test_unified_orchestrator.py`, `test_circuit_breaker.py`, and `tests/integration/test_persistence_integration.py`.

## Acceptance Criteria

- The recipe-app decision rule is reflected in a concrete mapping table.
- Core TTA domains have named primitive dependencies.
- The difference between conceptual TTA.dev ownership and current TTA implementation location is explicit.
- Future specs can reference this file instead of re-explaining the boundary each time.
