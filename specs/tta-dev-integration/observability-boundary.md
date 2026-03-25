# Observability Boundary

- **Component:** Observability ownership split between TTA and TTA.dev-style primitives
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

TTA uses OpenTelemetry-style tracing and metrics through `src/observability_integration/apm_setup.py`, while `ARCHITECTURE.md` frames observability as a universal concern that conceptually belongs in TTA.dev. This spec defines the ownership boundary between generic telemetry plumbing and TTA-specific semantic instrumentation.

## Scope / Responsibilities

- Define what is generic observability infrastructure.
- Define what remains TTA-specific domain telemetry.
- Preserve graceful degradation when observability packages are unavailable.
- Keep the interface simple for orchestration, safety, and persistence components.

## Requirements

### TTA.dev-Style Responsibilities
- Initialize tracer and meter providers.
- Configure exporters/readers and resource metadata.
- Expose helpers such as `initialize_observability()`, `get_tracer()`, `get_meter()`, and `shutdown_observability()`.
- Gracefully degrade to no-op behavior when OpenTelemetry is unavailable.

### TTA Responsibilities
- Name spans and metrics with domain semantics such as workflow phase, agent type, safety level, session ID, and circuit-breaker name.
- Decide which therapeutic and gameplay events deserve instrumentation.
- Avoid putting therapeutic meaning into the generic provider/bootstrap layer.

### Non-Functional Requirements
- **NFR-1:** Observability must never be a hard runtime dependency for core gameplay paths.
- **NFR-2:** Service metadata should remain available through OpenTelemetry resource attributes.
- **NFR-3:** Domain telemetry should be rich enough to debug orchestration, safety, and degradation paths.

## Interfaces / Dependencies

### Primary Anchors
- `src/observability_integration/apm_setup.py`
- `ARCHITECTURE.md` Layer 1 (`observability/`) vs Layer 2 (`src/observability_integration/`)
- `src/agent_orchestration/circuit_breaker.py` logging/metrics hooks

### Expected Domain Emitters
- Unified orchestrator workflow spans and phase-level timing
- Safety-validation and crisis-intervention events
- Circuit-breaker state transitions and rejected calls
- Persistence/cache degradation paths

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_unified_orchestrator.py` for workflow milestones worth instrumenting.
- `tests/agent_orchestration/test_circuit_breaker.py` for breaker metrics/state events.
- `tests/agent_orchestration/test_therapeutic_safety_integration.py` for safety metrics and service status expectations.

Caveat: the code currently lives in the TTA repository rather than an extracted TTA.dev package. This spec documents the ownership boundary, not a completed extraction.

## Acceptance Criteria

- Generic telemetry bootstrap responsibilities are separated from TTA domain semantics.
- Graceful no-op behavior is documented.
- Core emitters across workflow, safety, breaker, and persistence are identified.
- The architecture-vs-current-location caveat is explicit.
