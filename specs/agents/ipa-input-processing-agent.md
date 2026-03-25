# IPA Input Processing Agent

- **Component:** Input Processing Agent (IPA)
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

The IPA is the first agent in the unified workflow. It accepts raw player text, normalizes it, extracts routing intent and entities, and hands structured output to the orchestrator before world mutation or narrative generation begins.

Current code anchors are `src/agent_orchestration/adapters.py` (`IPAAdapter.process_input`), `src/agent_orchestration/models.py` (`AgentType.IPA`), and `src/agent_orchestration/unified_orchestrator.py` (`_process_input_phase`).

## Scope / Responsibilities

- Accept a single text input and return orchestration-ready routing data.
- Preserve the original player text as `normalized_text` when no richer normalization is available.
- Extract intent, confidence, and entities for downstream WBA/NGA steps.
- Degrade safely to a mock fallback when the real IPA implementation is unavailable.
- Participate in the common agent lifecycle when wrapped by `src/agent_orchestration/agents.py` (`send`, `receive_next`, `ack`, `nack`, `process_with_timeout`).

## Requirements

### Functional Requirements
- **FR-1:** IPA input must be text-first and return a dictionary containing `normalized_text`, `routing`, `raw_intent`, and `source`.
- **FR-2:** `routing` must support at least `intent`, `confidence`, and `entities`, with optional fields such as `direction`, `object`, and `npc`.
- **FR-3:** When the real IPA function cannot be imported or raises, the adapter must either surface `AgentCommunicationError` or fall back to `_mock_process_input()` depending on configuration.
- **FR-4:** The unified orchestrator must run safety validation before advancing from IPA to WBA, and it must persist the IPA result on workflow state.
- **FR-5:** IPA output must remain compatible with `ProtocolTranslator._translate_from_ipa_format()` for protocol-bridge routing.

### Non-Functional Requirements
- **NFR-1:** IPA calls should use `retry_with_backoff()` with shared `RetryConfig`.
- **NFR-2:** Failures must be observable through orchestrator logs and agent metrics.
- **NFR-3:** Fallback behavior must be deterministic enough for tests to assert `intent="unknown"` and reduced confidence.

## Interfaces / Dependencies

### Primary Interfaces
- `IPAAdapter.process_input(text: str) -> dict[str, Any]`
- `AgentType.IPA`, `AgentMessage`, `OrchestrationRequest`
- `UnifiedAgentOrchestrator._process_input_phase()`
- `ProtocolTranslator._translate_to_ipa_format()` and `_translate_from_ipa_format()`

### Safety and Domain Dependencies
- Input safety is checked in the orchestrator via `get_global_safety_service().validate_text(...)` before workflow progression.
- Safety models come from the compatibility shim in `src/agent_orchestration/therapeutic_safety.py` and the underlying `safety_validation` package.

### TTA.dev Primitive Dependencies
- **Retry with Backoff:** used directly by the adapter.
- **Timeout:** inherited when IPA is executed through the base `Agent.process_with_timeout()` contract.
- **Tracing/Observability:** expected at orchestration boundaries, not inside IPA domain logic.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_unified_orchestrator.py` validates IPA phase behavior and workflow completion.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` treats IPA as the first step in `IPA → WBA → NGA` workflows.
- `tests/agent_orchestration/test_workflow_safety_integration.py` confirms safety findings can short-circuit workflows before later stages.

Validation should confirm successful extraction, deterministic fallback behavior, and safety-gated progression.

## Acceptance Criteria

- IPA is documented as the required workflow entrypoint for player text.
- The output contract matches the adapter and translator code anchors.
- Retry, fallback, and safety-gating responsibilities are explicit.
- Test anchors for happy-path and safety-interrupted flows are identified.
