# Redis Session Cache

- **Component:** Redis-backed cache and short-lived orchestration state
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

Redis is used in TTA for short-lived, high-value state rather than as the sole source of truth. Current anchors include orchestration workflow persistence, session caching, token caching, and circuit-breaker durability.

Primary anchors: `src/agent_orchestration/unified_orchestrator.py`, `src/agent_orchestration/circuit_breaker.py`, `src/player_experience/database/redis_cache.py`, and `src/player_experience/database/session_repository.py`.

## Scope / Responsibilities

- Persist active workflow state for retrieval across requests.
- Cache session context for low-latency session lookups.
- Cache verified authentication tokens without storing raw tokens as keys.
- Persist circuit-breaker state and metrics across process restarts.
- Support other Redis-backed orchestration services such as registry heartbeats and message coordination.

## Requirements

### Functional Requirements
- **FR-1:** Workflow state must be stored under `orchestration:workflow:{workflow_id}` with a 1-hour TTL.
- **FR-2:** Latest workflow lookup per session must be stored under `orchestration:session:{session_id}:latest` with a 1-hour TTL.
- **FR-3:** SessionRepository cache entries must use `session:{session_id}` with a 1-hour TTL.
- **FR-4:** Token cache entries must use `auth:tok:{sha256-prefix}` and expire with the token’s remaining lifetime.
- **FR-5:** Circuit-breaker state must use `{prefix}:cb:state:{name}` with a 24-hour TTL; metrics must use `{prefix}:cb:metrics:{name}` with a 7-day TTL.
- **FR-6:** Redis failures must degrade gracefully: orchestrator skips persistence, token cache ignores errors, and repositories may fall back to Neo4j/in-memory state.

### Non-Functional Requirements
- **NFR-1:** Cached values must be JSON-serializable and compatible with `decode_responses=True` clients where configured.
- **NFR-2:** Raw auth tokens must never be used directly as Redis keys.
- **NFR-3:** Redis should remain a cache and coordination layer, not the only long-term persistence store.

## Interfaces / Dependencies

### Primary Interfaces
- `UnifiedAgentOrchestrator._save_state()` / `get_workflow_state()`
- `TokenCache.get()`, `set()`, `delete()`, `ping()`
- `SessionRepository.create_session()`, `get_session()`, `update_session()`
- `CircuitBreaker.initialize()` and state/metrics persistence methods

### Related Tests and Services
- `tests/agent_orchestration/test_unified_orchestrator.py`
- `tests/agent_orchestration/test_circuit_breaker.py`
- `tests/agent_orchestration/test_redis_agent_registry.py`
- `tests/integration/test_persistence_integration.py`

### TTA.dev Primitive Dependencies
- **Cache / State:** Redis is the concrete TTA use of generic caching/state primitives.
- **Timeout / Retry:** transport resilience belongs at the client boundary, not in the cached payload schema.

## Testing / Validation

Validation should confirm TTL-backed storage, key naming, graceful degradation, and compatibility with integration tests for token caching and persisted workflows.

## Acceptance Criteria

- Key patterns and TTLs reflect the current code.
- Cache-versus-source-of-truth boundaries are documented.
- Graceful degradation expectations are explicit.
- Redis-backed tests are linked for workflow, cache, and breaker behavior.
