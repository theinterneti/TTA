# Therapeutic Integration

- **Component:** Narrative therapeutic integration
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

Therapeutic integration defines how TTA weaves therapeutic goals into scenes without turning gameplay into a purely clinical script. The current implementation chooses an integration intensity and a narrative technique based on player readiness and emotional state.

Primary anchor: `src/components/gameplay_loop/narrative/therapeutic_integrator.py`.

## Scope / Responsibilities

- Select a therapeutic integration mode for the current session.
- Choose a narrative technique suitable for the current emotional state.
- Apply therapeutic framing to an existing scene rather than replacing the scene generator wholesale.
- Attach therapeutic metadata such as goals and learning objectives to scenes.
- Back off intensity when the player is distressed or overwhelmed.

## Requirements

### Functional Requirements
- **FR-1:** Integration mode must be one of `SUBTLE`, `MODERATE`, `DIRECT`, or `INTENSIVE`.
- **FR-2:** Narrative techniques must be one of `MODELING`, `SCAFFOLDING`, `REFLECTION`, `PSYCHOEDUCATION`, or `EXPERIENTIAL`.
- **FR-3:** `select_integration_mode()` must consider at least `emotional_state`, `therapeutic_effectiveness`, and `total_choices_made`.
- **FR-4:** `integrate_therapeutic_context()` must preserve the base scene while appending therapeutic emphasis and metadata.
- **FR-5:** `apply_narrative_technique()` must add technique-specific language and ensure `scene.therapeutic_focus` reflects the applied technique and goals.
- **FR-6:** Technique selection must default safely when no direct emotional-state match exists.

### Non-Functional Requirements
- **NFR-1:** Distressed, overwhelmed, or crisis states must bias the system toward `SUBTLE` integration.
- **NFR-2:** Integration behavior should remain explainable from code, not opaque model prompting alone.
- **NFR-3:** Errors should leave the original scene intact.

## Interfaces / Dependencies

### Primary Interfaces
- `IntegrationMode`
- `NarrativeTechnique`
- `TherapeuticIntegrator.initialize()`
- `integrate_therapeutic_context()`, `select_integration_mode()`, `apply_narrative_technique()`

### Domain Dependencies
- `TherapeuticContext`, `SessionState`, `Scene`, and `EmotionalState`
- Output safety constraints from `EmotionalSafetySystem`

### TTA.dev Primitive Dependencies
- Therapeutic integration itself is TTA-specific.
- Only generic support primitives such as tracing or timeout may be imported around the boundary.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` contains therapeutic-content scenarios that rely on consistent integration semantics.
- `tests/agent_orchestration/test_workflow_safety_integration.py` is relevant where therapeutic integration must yield to safety aggregation.

Direct automated tests for `therapeutic_integrator.py` are not part of the cited suite, so this spec remains Draft and should be used as a contract for future unit coverage.

## Acceptance Criteria

- Integration modes and narrative techniques are documented from the current enums.
- Mode-selection heuristics and safety backoff behavior are explicit.
- Scene mutation and metadata responsibilities are captured.
- The spec clearly marks the current testing gap.
