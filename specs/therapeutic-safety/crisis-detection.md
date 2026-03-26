# Crisis Detection

- **Component:** Crisis detection and escalation
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

Crisis detection is the highest-severity therapeutic safety layer in TTA. It converts safety-validation findings into a four-level crisis assessment (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) and, when needed, triggers intervention and escalation workflows.

Primary anchors are `src/agent_orchestration/crisis_detection/enums.py`, `models.py`, `manager.py`, and `escalation.py`, plus the compatibility shim in `src/agent_orchestration/therapeutic_safety.py`.

## Scope / Responsibilities

- Classify crisis types such as self-harm, suicidal ideation, severe depression, panic attack, and domestic violence.
- Convert `ValidationResult` into a `CrisisAssessment` with confidence, risk factors, protective factors, and intervention recommendations.
- Start and track `CrisisIntervention` records.
- Escalate to human oversight or emergency services based on assessed severity.
- Preserve auditability through timestamps, intervention history, and escalation status.

## Requirements

### Functional Requirements
- **FR-1:** Crisis typing must use the enumerated `CrisisType` values defined in `enums.py`.
- **FR-2:** Severity must be expressed using `CrisisLevel` (`low`, `moderate`, `high`, `critical`).
- **FR-3:** `CrisisInterventionManager.assess_crisis()` must derive level, confidence, risk/protective factors, immediate risk, and recommended intervention from `ValidationResult` plus session context.
- **FR-4:** `initiate_intervention()` must create a `CrisisIntervention`, execute an immediate response, and trigger escalation when required.
- **FR-5:** Human escalation must support multiple channels, with more urgent channel sets for higher crisis levels.
- **FR-6:** Critical crises must support emergency-services escalation via `HumanOversightEscalation.escalate_to_emergency_services()`.

### Non-Functional Requirements
- **NFR-1:** Crisis assessment must be deterministic enough for automated tests to assert blocking/escalation behavior.
- **NFR-2:** All escalation actions must be timestamped and tracked for review.
- **NFR-3:** The system must default to non-crisis behavior when validation does not detect crisis indicators.

## Interfaces / Dependencies

### Primary Interfaces
- `CrisisAssessment`
- `CrisisIntervention`
- `CrisisInterventionManager`
- `HumanOversightEscalation`

### Upstream Dependencies
- `ValidationResult` from `src/agent_orchestration/safety_validation/models.py`
- `SafetyService` compatibility exports from `src/agent_orchestration/therapeutic_safety.py`

### TTA.dev Primitive Dependencies
- **Observability:** escalation, intervention counts, and critical paths should be instrumented.
- **Retry/Notification resilience:** applies to transport channels, not crisis-domain classification itself.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_therapeutic_safety_integration.py` validates crisis blocking, escalation flags, service compatibility, metrics, performance, and malformed-input handling.
- `tests/agent_orchestration/test_workflow_safety_integration.py` validates how aggregated safety findings can block workflows.

Validation should confirm that severe inputs are escalated, non-crisis inputs remain non-blocking, and performance stays within the current integration-test envelope.

## Acceptance Criteria

- Four crisis levels and supported crisis types are documented.
- Intervention and escalation flows map directly to the current manager and escalation classes.
- Test anchors cover both blocking behavior and observability/metrics concerns.
- The spec stays aligned with the present keyword/sentiment/context-driven implementation.
