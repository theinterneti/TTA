# Neo4j Story Graph

- **Component:** Neo4j-backed narrative and session graph persistence
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

Neo4j is the intended persistent graph layer for world, character, and session state. The current codebase already persists `World`, `Character`, and `Session` nodes through repository classes, while richer “story graph” relationships remain an evolving design target.

Primary anchors: `src/player_experience/database/world_repository.py`, `character_repository.py`, and `session_repository.py`, with WBA integration points in `src/agent_orchestration/adapters.py`.

## Scope / Responsibilities

- Persist durable world, character, and session records outside Redis.
- Provide lookup by graph-meaningful IDs such as `world_id`, `character_id`, `session_id`, and `player_id`.
- Support world-building operations through Neo4j-backed managers when available.
- Preserve a safe in-memory fallback when Neo4j is unavailable.
- Act as the long-lived counterpart to shorter-lived Redis cache/state entries.

## Requirements

### Functional Requirements
- **FR-1:** `WorldRepository` must support creation and retrieval of `World` nodes keyed by `world_id`.
- **FR-2:** `CharacterRepository` must support creation and retrieval of `Character` nodes keyed by `character_id` and grouped by `player_id`.
- **FR-3:** `SessionRepository` must support persistent session storage in Neo4j in addition to Redis caching.
- **FR-4:** Complex world and character structures may be serialized as JSON strings when direct graph modeling is not yet implemented.
- **FR-5:** WBA-facing orchestration must be able to run with a supplied `neo4j_manager`, but degrade when it is absent.
- **FR-6:** Repository classes must fall back to in-memory storage when Neo4j connectivity fails.

### Non-Functional Requirements
- **NFR-1:** Graph persistence should not block basic local development; fallback modes are part of the contract.
- **NFR-2:** Serialized payloads must be reversible into domain models.
- **NFR-3:** The spec must distinguish current implemented node storage from still-draft richer relationship schemas.

## Interfaces / Dependencies

### Current Graph Anchors
- `WorldRepository._create_world_neo4j()` / `_get_world_neo4j()`
- `CharacterRepository._create_character_neo4j()` / `_get_character_neo4j()`
- `SessionRepository._create_session_in_neo4j()` and related query helpers

### Workflow Dependencies
- `WBAAdapter` accepts `neo4j_manager` for real world-building behavior.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` includes Neo4j verification helpers for workflow execution/state.

### TTA.dev Primitive Dependencies
- The graph schema is TTA-specific.
- Generic timeout, retry, and observability patterns may wrap repository access but do not define graph meaning.

## Testing / Validation

Relevant anchors:
- `tests/integration/test_persistence_integration.py` for persistence patterns.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` for workflow state verification against Neo4j-backed data.

Caveat: today’s code anchors describe persistent nodes and some workflow records more strongly than a full narrative relationship graph. This spec therefore documents the current baseline plus the intended story-graph direction.

## Acceptance Criteria

- Implemented Neo4j-backed repositories are documented accurately.
- Fallback behavior is treated as part of the persistence contract.
- The gap between current node persistence and fuller story-graph modeling is explicit.
- Test anchors cover both persistence and workflow-state use cases.
