# Agent Orchestration Protocol

- **Component:** IPA → WBA → NGA coordination protocol
- **Status:** Draft
- **Last Updated:** 2026-03-23

## Overview

This spec defines the message, state, and workflow contract for TTA agent orchestration. It covers the shared models, lifecycle helpers, routing translation, and the canonical execution order `IPA → WBA → NGA`.

Primary anchors are `src/agent_orchestration/models.py`, `src/agent_orchestration/agents.py`, `src/agent_orchestration/protocol_bridge.py`, `src/agent_orchestration/messaging.py`, and `src/agent_orchestration/unified_orchestrator.py`.

## Scope / Responsibilities

- Define the agent identity and message envelope used across orchestration.
- Define queue-facing delivery semantics such as `ack`, `nack`, visibility deadlines, and failure typing.
- Define workflow-state progression and persistence for unified orchestration.
- Translate between orchestration-native messages and real-agent adapter payloads.
- Allow safety checks to interrupt the normal pipeline without breaking state tracking.

## Requirements

### Functional Requirements
- **FR-1:** Agent identities must use `AgentId(type, instance?)`, with core types at least `IPA`, `WBA`, and `NGA`.
- **FR-2:** `AgentMessage` must carry `message_id`, `sender`, `recipient`, `message_type`, `payload`, `priority`, `routing`, and optional timestamp.
- **FR-3:** Queue delivery must support `MessageResult`, `QueueMessage`, `ReceivedMessage`, and `FailureType` (`transient`, `permanent`, `timeout`).
- **FR-4:** Base agents must expose lifecycle and transport helpers: `start`, `stop`, `health_check`, `send`, `receive_next`, `ack`, `nack`, and `process_with_timeout`.
- **FR-5:** Unified orchestration must progress through `INPUT_PROCESSING`, `WORLD_BUILDING`, `NARRATIVE_GENERATION`, then either `COMPLETE` or `ERROR`.
- **FR-6:** Workflow state must persist to Redis under `orchestration:workflow:{workflow_id}` and `orchestration:session:{session_id}:latest`.
- **FR-7:** Protocol translation must normalize IPA/WBA/NGA request and response shapes when routing through `MessageRouter`.
- **FR-8:** Safety findings may short-circuit the workflow after IPA, returning a safety intervention instead of continuing to WBA/NGA.

### Non-Functional Requirements
- **NFR-1:** Message and state models must remain JSON-serializable.
- **NFR-2:** Timeout and retry policies should be applied at agent-call boundaries rather than embedded in domain models.
- **NFR-3:** Agent metrics should track request/error counts and recent success rate for health reporting.

## Interfaces / Dependencies

### Core Models
- `AgentType`, `AgentId`, `AgentMessage`, `OrchestrationRequest`, `OrchestrationResponse`
- `MessageType`, `MessagePriority`, `RoutingKey`
- `MessageResult`, `QueueMessage`, `ReceivedMessage`, `FailureType`

### Workflow State
- `OrchestrationPhase`
- `OrchestrationState.to_dict()` / `from_dict()`
- `UnifiedAgentOrchestrator.process_user_input()`

### Translation Layer
- `ProtocolType`, `ProtocolTranslator`, `MessageRouter`
- IPA/WBA/NGA translation helpers in `protocol_bridge.py`

### TTA.dev Primitive Dependencies
- **Retry / Timeout:** agent adapters and base-agent execution boundaries.
- **Cache / State:** Redis-backed workflow persistence.
- **Tracing:** end-to-end workflow instrumentation across message boundaries.

## Testing / Validation

Relevant anchors:
- `tests/agent_orchestration/test_messaging.py` validates message and queue model contracts.
- `tests/agent_orchestration/test_unified_orchestrator.py` validates phase transitions and Redis persistence.
- `tests/agent_orchestration/test_multi_agent_workflow_integration.py` validates end-to-end multi-agent order and state continuity.
- `tests/agent_orchestration/test_redis_agent_registry.py` validates Redis-backed registry/heartbeat discovery around the broader orchestration ecosystem.

## Acceptance Criteria

- Message, queue, and workflow-state contracts are defined in one place.
- IPA/WBA/NGA ordering and safety interruption are explicit.
- Redis keys and protocol translation responsibilities are documented.
- The spec stays grounded in current models, adapters, and tests rather than aspirational transport details.
