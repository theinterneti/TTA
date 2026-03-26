# Safety Interop

- **Component:** Crisis detection ↔ emotional safety interoperability
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

TTA currently has two distinct safety layers:

1. **Input-side therapeutic safety** in `src/agent_orchestration/therapeutic_safety.py` and the `safety_validation` / `crisis_detection` packages.
2. **Output-side emotional safety** in `src/components/gameplay_loop/narrative/emotional_safety_system.py`.

This spec defines how those layers should interoperate so that harmful input is intercepted early and risky generated output is softened or halted before display.

## Scope / Responsibilities

- Define precedence between input crisis signals and output emotional-safety classification.
- Keep shared session context available across both safety layers.
- Ensure safety interventions can interrupt the normal gameplay loop.
- Provide a simple mapping between the two severity scales for orchestration and UI purposes.
- Avoid duplicating domain logic where one layer already owns a decision.

## Requirements

### Functional Requirements
- **FR-1:** Input safety validation must run before the workflow advances beyond IPA.
- **FR-2:** `SafetyLevel.WARNING` or `SafetyLevel.BLOCKED` from the orchestrator-side validator must be able to short-circuit the IPA → WBA → NGA flow.
- **FR-3:** Output content must be eligible for `EmotionalSafetySystem.assess_content_safety()` and optional filtering/intervention before player display.
- **FR-4:** The proposed severity bridge from `specs/therapeutic-safety/README.md` should be treated as the default mapping:
  - `SAFE` ↔ no crisis
  - `CAUTION` ↔ `LOW`
  - `WARNING` ↔ `MODERATE`
  - `UNSAFE` ↔ `HIGH`
  - `CRISIS` ↔ `CRITICAL`
- **FR-5:** When the two systems disagree, the more severe outcome must win.
- **FR-6:** Crisis escalation metadata should remain available to higher-level monitoring and observability systems.

### Non-Functional Requirements
- **NFR-1:** Interop rules should be simple enough for workflow code to enforce deterministically.
- **NFR-2:** Safety context should remain serializable on orchestration state and session objects.
- **NFR-3:** Gaps between input-side and output-side enforcement must be documented rather than hidden.

## Interfaces / Dependencies

### Input-Side Anchors
- `UnifiedAgentOrchestrator._process_input_phase()`
- `UnifiedAgentOrchestrator._handle_safety_concern()`
- `SafetyService`, `SafetyRuleEngine`, `CrisisInterventionManager`

### Output-Side Anchors
- `EmotionalSafetySystem.assess_content_safety()`
- `filter_unsafe_content()`
- `trigger_safety_intervention()`

### TTA.dev Primitive Dependencies
- **Observability:** cross-layer safety decisions should emit compatible traces/metrics.
- **State management:** shared workflow/session state should carry the minimum safety context needed across boundaries.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_therapeutic_safety_integration.py`
- `tests/agent_orchestration/test_workflow_safety_integration.py`
- `tests/agent_orchestration/test_unified_orchestrator.py`

Current caveat: the input-side safety short-circuit is implemented in the unified orchestrator, while output-side emotional safety exists in a separate gameplay component. This spec therefore documents the required boundary more completely than the current wiring implements.

## Acceptance Criteria

- Both safety layers and their ownership boundaries are clear.
- The default severity mapping is recorded.
- Conflict-resolution rules prefer the stricter decision.
- Current implementation gaps are explicitly acknowledged.
