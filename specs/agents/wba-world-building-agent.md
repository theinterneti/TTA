# WBA World Building Agent

- **Component:** World Building Agent (WBA)
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

The WBA is the second step in the unified workflow. It receives structured intent and entity data from IPA, applies world updates against a world identifier, and returns the updated world state for narrative generation.

Current anchors are `src/agent_orchestration/adapters.py` (`WBAAdapter.process_world_request`), `src/agent_orchestration/unified_orchestrator.py` (`_process_world_building_phase`), and the persistence repositories under `src/player_experience/database/`.

## Scope / Responsibilities

- Resolve the target `world_id` from session/world context.
- Convert IPA routing data into world updates.
- Return a normalized result containing `world_id`, `world_state`, `updated`, `cached`, and `source`.
- Prefer real Neo4j-backed behavior when available, but provide a mock fallback for testability and degraded operation.
- Keep world mutation separate from therapeutic and narrative phrasing concerns.

## Requirements

### Functional Requirements
- **FR-1:** WBA input must include a `world_id` and optional `updates` payload.
- **FR-2:** The unified orchestrator must populate WBA updates from IPA output: `intent`, `entities`, `player_id`, and `session_id`.
- **FR-3:** WBA output must merge returned `world_state` into `OrchestrationState.world_context` when present.
- **FR-4:** If no real `WorldBuildingAgent` instance is available, the adapter must fall back to `_mock_process_world()` unless explicitly disabled.
- **FR-5:** Protocol bridge routing must remain compatible with `_translate_to_wba_format()` and `_translate_from_wba_format()`.

### Non-Functional Requirements
- **NFR-1:** WBA calls should use the shared retry configuration for transient failures.
- **NFR-2:** The world layer must tolerate Neo4j unavailability through in-memory fallback at repository level.
- **NFR-3:** Returned world state must stay serialization-friendly for Redis-persisted orchestration state.

## Interfaces / Dependencies

### Primary Interfaces
- `WBAAdapter.process_world_request(world_id, updates)`
- `AgentType.WBA`, `AgentMessage`, `OrchestrationState.wba_result`
- `ProtocolTranslator._translate_to_wba_format()` / `_translate_from_wba_format()`

### Persistence Dependencies
- `src/player_experience/database/world_repository.py` for `World` persistence and fallback behavior.
- `src/player_experience/database/session_repository.py` for session-linked `world_id` access patterns.
- `src/player_experience/database/character_repository.py` where world changes may intersect with character context.

### TTA.dev Primitive Dependencies
- **Retry with Backoff:** used directly in the adapter.
- **Timeout:** applies when WBA is executed via the base agent abstraction.
- **Cache:** Redis session/world state acts as a TTA-layer consumer of generic cache patterns.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_unified_orchestrator.py` validates world-building phase transitions and context updates.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` validates WBA participation in end-to-end workflows.
- `tests/integration/test_persistence_integration.py` validates persistence patterns that WBA relies on indirectly.

Validation should confirm correct `world_id` selection, world-context merging, and graceful fallback when persistence or real agents are absent.

## Acceptance Criteria

- WBA is defined as the world-state mutation step between IPA and NGA.
- The request/response contract matches adapter and protocol-bridge anchors.
- Persistence and degraded-mode expectations are documented.
- Test anchors cover both orchestrated and persistence-backed behavior.
