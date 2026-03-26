# NGA Narrative Generator Agent

- **Component:** Narrative Generator Agent (NGA)
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

The NGA is the final step in the core workflow. It receives the assembled prompt and execution context after IPA and WBA complete, then generates the player-facing narrative response.

Key anchors are `src/agent_orchestration/adapters.py` (`NGAAdapter.generate_narrative`), `src/agent_orchestration/unified_orchestrator.py` (`_build_narrative_prompt`, `_process_narrative_phase`), `src/components/gameplay_loop/narrative/emotional_safety_system.py`, and `src/components/gameplay_loop/narrative/therapeutic_integrator.py`.

## Scope / Responsibilities

- Convert orchestrated world and therapeutic context into a narrative response.
- Preserve a clear result contract: `story`, `raw`, `context_used`, and `source`.
- Maintain therapeutic tone and encourage continued engagement as required by the orchestrator prompt builder.
- Degrade gracefully to a mock narrative when the real NGA is unavailable.
- Remain compatible with downstream emotional-safety filtering and therapeutic integration.

## Requirements

### Functional Requirements
- **FR-1:** NGA must accept a `prompt` and optional `context` and return a `story` field suitable for player display.
- **FR-2:** The unified orchestrator must include world state, IPA intent/entities, WBA results, therapeutic context, and safety level in NGA context.
- **FR-3:** If the real generator fails, fallback behavior must still produce a safe, minimal story payload when enabled.
- **FR-4:** NGA output must stay compatible with `_translate_from_nga_format()` for protocol-bridge use.
- **FR-5:** Narrative content should remain compatible with `EmotionalSafetySystem.assess_content_safety()` and `TherapeuticIntegrator.integrate_therapeutic_context()`.

### Non-Functional Requirements
- **NFR-1:** NGA calls should use retry/backoff for transient failures.
- **NFR-2:** Narrative generation boundaries should support circuit-breaker wrapping at external-call edges.
- **NFR-3:** Degraded responses must remain explicit via the `source` field (`real_nga` vs `mock_fallback`).

## Interfaces / Dependencies

### Primary Interfaces
- `NGAAdapter.generate_narrative(prompt, context)`
- `UnifiedAgentOrchestrator._build_narrative_prompt()`
- `AgentType.NGA`, `AgentMessage`, `OrchestrationResponse`
- `ProtocolTranslator._translate_to_nga_format()` / `_translate_from_nga_format()`

### Safety and Therapeutic Dependencies
- `EmotionalSafetySystem` provides output-side safety assessment and intervention behavior.
- `TherapeuticIntegrator` defines how therapeutic goals are woven into scenes using integration modes and narrative techniques.
- The orchestrator already injects `safety_level` and `therapeutic_context`; richer output-side enforcement is still partly split across components.

### TTA.dev Primitive Dependencies
- **Retry with Backoff:** used directly in the adapter.
- **Circuit Breaker:** specified for external narrative/LLM boundaries; see `specs/tta-dev-integration/circuit-breaker-usage.md`.
- **Tracing/Observability:** should instrument generation latency and degraded/fallback paths.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_unified_orchestrator.py` validates narrative generation and complete workflow results.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` exercises NGA as the final stage in collaborative workflows.
- `tests/agent_orchestration/test_workflow_safety_integration.py` provides a safety-focused workflow lens for output handling.

Validation should confirm prompt/context assembly, fallback output, and compatibility with safety/therapeutic post-processing.

## Acceptance Criteria

- NGA is documented as the final player-facing generation stage.
- The adapter contract and orchestrator prompt-building inputs are captured.
- Safety and therapeutic integration boundaries are explicit.
- Fallback and future circuit-breaker use are called out without overstating current implementation.
