# Spring Cleaning: `tta-ai-framework` Infrastructure Overlap Audit

> **Date:** 2026-03-04
> **Scope:** `packages/tta-ai-framework/src/tta_ai/orchestration/`
> **Purpose:** Identify infrastructure-level logic that overlaps with `TTA.dev` primitives (`tta-dev-primitives`, `universal-agent-context`)

---

## Directories Removed (Migration Artifacts)

The following obsolete directories were permanently deleted. No active imports in `src/`, `packages/`, or `tests/` referenced them; all 1402 unit tests continue to pass.

| Directory | Contents |
|-----------|----------|
| `.archive/` | 9 subdirs (cicd, components, database, infrastructure, observability, packages, status-reports, testing, tooling) |
| `_archive/` | Legacy agent archives (openhands, kiro, gemini), Phase 1 summary |
| `archive/` | CI-CD fixes, integration notes, phase docs, recommendations, tasks, validation |
| `artifacts/` | Screenshots, test-results, test-scripts |
| `backups/` | Timestamped backups (2025-10-13), security-remediation phases |
| `obsolete/` | Docker-compose leftovers, subdirectories marked for deletion |
| `patches/stash_exports/` | 5 stash export patches (2025-10-04 through 2025-10-29) |
| `export/tta-observability-integration/` | Exportable observability integration package (src, tests, specs, manifest) |

---

## `tta-ai-framework` Infrastructure Overlap Summary

### HIGH Overlap — Belongs in `TTA.dev`

| Component | Files | What It Does | TTA.dev Equivalent |
|-----------|-------|-------------|-------------------|
| **Circuit Breaker** | `circuit_breaker.py`, `circuit_breaker_config.py`, `circuit_breaker_registry.py`, `circuit_breaker_metrics.py` | 3-state (CLOSED→OPEN→HALF_OPEN) pattern with Redis persistence, async locks, correlation IDs, configurable thresholds, env-var overrides | `tta-dev-primitives` v0.2.0 |
| **Retry / Backoff** | `adapters.py` (`RetryConfig`, `retry_with_backoff`) | Exponential backoff with jitter, circuit-breaker integration, configurable max retries/delays | `tta-dev-primitives` |
| **Message Coordination** | `messaging.py`, `interfaces.py`, `coordinators/redis_message_coordinator.py` | `QueueMessage` with delivery attempts, ack/nack semantics, visibility timeout, DLQ routing, `recover_pending()` | `tta-dev-primitives` |
| **Observability Utilities** | `monitoring.py`, `metrics.py`, `workflow_monitor.py` | `CircuitBreakerLogger`, `CircuitBreakerMetricsCollector`, correlation ID context managers, operation timing | `tta-dev-primitives` |
| **Resource Exhaustion Detection** | `resource_exhaustion_detector.py` | Memory/CPU/disk threshold monitoring with early warnings, sustained-duration checks | `tta-dev-primitives` |

### MEDIUM Overlap — Shared Concern

| Component | Files | What It Does | Notes |
|-----------|-------|-------------|-------|
| **Workflow Engine** | `workflow.py`, `workflow_manager.py`, `workflow_transaction.py` | Workflow types (INPUT_PROCESSING, WORLD_BUILDING, etc.), error handling strategies (FAIL_FAST, RETRY, SKIP_ON_ERROR), timeout configs | Domain-specific workflow types are TTA-game logic, but the engine primitives (type definitions, error strategies, transaction semantics) are infrastructure |
| **Orchestration State** | `unified_orchestrator.py` | 6-phase orchestration (INPUT_PROCESSING → COMPLETE/ERROR) with state tracking | Phase definitions are TTA-specific, but the state machine pattern is infrastructure |

### LOW Overlap — Stays in TTA

| Component | Files | What It Does | Notes |
|-----------|-------|-------------|-------|
| **LangGraph Integration** | `langgraph_orchestrator.py` | `StateGraph`-based workflow execution with LangChain message history | Deeply coupled to TTA's AI agent topology |
| **Crisis Detection** | `crisis_detection/` | Safety escalation protocols, crisis level assessment | TTA domain logic (therapeutic safety) |
| **Safety Validation** | `safety_validation/`, `safety_monitoring/` | Therapeutic content validation, safety scoring | TTA domain logic |
| **Agent Registry** | `agents.py`, `proxies.py` | Agent type definitions (IPA, WBA, NGA), proxy layer | TTA-specific agent types |
| **Real-time Streaming** | `realtime/` | WebSocket progressive feedback | Application-level concern |
| **Prompt Management** | `prompts/` | Prompt registry, template management | TTA domain logic |

---

## Recommendations

1. **Circuit Breaker extraction is highest priority** — it's a standalone, well-tested infrastructure primitive with zero domain coupling. Scheduled for `TTA.dev` v0.2.0.

2. **Retry/Backoff and Message Coordination should follow** — they are tightly coupled to the circuit breaker and form a coherent "reliability primitives" module.

3. **Observability utilities should migrate with the circuit breaker** — `CircuitBreakerLogger` and `CircuitBreakerMetricsCollector` are designed as companions to the circuit breaker.

4. **Workflow engine requires careful decomposition** — separate the generic state machine / error strategy primitives from the TTA-specific workflow type definitions before migrating.

5. **Do not migrate LangGraph integration, crisis detection, safety, or agent types** — these are firmly in TTA's domain layer.

---

## Total Infrastructure Code in `tta-ai-framework`

~2,500+ lines across circuit breaker, messaging, workflow, and monitoring modules that are candidates for extraction to `TTA.dev`.
