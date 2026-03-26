# Emotional Safety System

- **Component:** Narrative emotional safety system
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

The Emotional Safety System evaluates generated narrative content for player-facing emotional risk. It uses a five-level scale (`SAFE`, `CAUTION`, `WARNING`, `UNSAFE`, `CRISIS`), content flags, and session emotional state to decide whether content should pass through, soften, or trigger an intervention scene.

Primary anchor: `src/components/gameplay_loop/narrative/emotional_safety_system.py`.

## Scope / Responsibilities

- Assess generated content for triggering, overwhelming, retraumatizing, inappropriate, or harmful themes.
- Incorporate current `SessionState.emotional_state` and accumulated safety alerts into severity.
- Filter or soften scenes when content crosses configured thresholds.
- Produce grounding/intervention scenes when the player’s emotional state indicates elevated risk.
- Fail safe to at least `CAUTION` when assessment errors occur.

## Requirements

### Functional Requirements
- **FR-1:** The safety model must expose levels `safe`, `caution`, `warning`, `unsafe`, and `crisis`.
- **FR-2:** `assess_content_safety()` must return `safety_level`, `flags`, `severity`, `recommendations`, and current emotional-state context.
- **FR-3:** Content flags must be driven by the current keyword map for `TRIGGERING`, `OVERWHELMING`, `INAPPROPRIATE`, `RETRAUMATIZING`, and `HARMFUL`.
- **FR-4:** `filter_unsafe_content()` must soften or replace content at `WARNING`, `UNSAFE`, and `CRISIS` levels, including difficulty downshifts where needed.
- **FR-5:** `check_emotional_boundaries()` must use emotional-state risk and `session_state.safety_alerts` to compute boundary status.
- **FR-6:** `trigger_safety_intervention()` must return `None` for `SAFE`/`CAUTION` and generate a dedicated intervention scene for higher-risk levels.

### Non-Functional Requirements
- **NFR-1:** Safety assessment should be lightweight enough to run inline with scene generation.
- **NFR-2:** Error paths should degrade conservatively rather than suppressing safety concerns.
- **NFR-3:** Thresholds such as `max_emotional_intensity` and `crisis_threshold` should remain configuration-driven.

## Interfaces / Dependencies

### Primary Interfaces
- `SafetyLevel`
- `ContentFlag`
- `EmotionalSafetySystem.initialize()`
- `assess_content_safety()`, `filter_unsafe_content()`, `check_emotional_boundaries()`, `trigger_safety_intervention()`

### Domain Dependencies
- `SessionState`, `Scene`, `DifficultyLevel`, and `EmotionalState` from gameplay-loop models.
- Safety interop with crisis detection is specified separately in `specs/therapeutic-safety/safety-interop.md`.

### TTA.dev Primitive Dependencies
- **Observability:** safety levels, intervention counts, and degradation paths should be measurable.
- **No direct primitive ownership:** the classification rules themselves are TTA-specific domain logic.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_workflow_safety_integration.py` demonstrates cross-workflow aggregation of warning/blocked outcomes.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` includes safety-centric scenarios that NGA/output layers must ultimately respect.

Additional dedicated unit coverage for `emotional_safety_system.py` is still desirable; this gap is one reason the spec remains Draft rather than Written.

## Acceptance Criteria

- Five emotional safety levels and content-flag categories are documented.
- Assessment, filtering, and intervention responsibilities match the current component.
- The spec explicitly notes fail-safe error handling and configuration thresholds.
- Current testing coverage and remaining validation gaps are transparent.
