---
name: orchestration
description: "Skill for the Orchestration area of TTA. 242 symbols across 43 files."
---

# Orchestration

242 symbols | 43 files | Cohesion: 83%

## When to Use

- Working with code in `packages/`
- Understanding how get_active_capabilities, match_capabilities, retry work
- Modifying orchestration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `packages/tta-ai-framework/src/tta_ai/orchestration/workflow_monitor.py` | _run_key, _metrics_key, start_step, end_step, complete_run (+13) |
| `packages/tta-narrative-engine/src/tta_narrative/orchestration/scale_manager.py` | detect_scale_conflicts, get_active_events, _detect_temporal_conflicts, _detect_character_conflicts, _detect_thematic_conflicts (+13) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker.py` | _transition_to_half_open, call, execute, _state_key, _metrics_key (+9) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/capability_matcher.py` | match_capabilities, _exact_match, _weighted_score_match, _fuzzy_match, _priority_based_match (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/proxies.py` | InputProcessorAgentProxy, WorldBuilderAgentProxy, NarrativeGeneratorAgentProxy, __init__, __init__ (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/enhanced_coordinator.py` | execute_workflow, _execute_workflow_steps, _execute_ipa_step, _execute_wba_step, _execute_nga_step (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/agents.py` | _key, get, run_health_checks_once, _maybe_restart, _enforce_restart_policy (+5) |
| `src/orchestration/config.py` | get, validate, _validate_dict, __init__, _load_config (+5) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker_registry.py` | _registry_key, get_or_create, list_names, sync_registry_with_redis, _cleanup_key (+5) |
| `src/orchestration/orchestrator.py` | run_docker_command, run_docker_compose_command, stop_all, display_status, has_component (+5) |

## Entry Points

Start here when exploring this area:

- **`get_active_capabilities`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/models.py:204`
- **`match_capabilities`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/capability_matcher.py:49`
- **`retry`** (Function) — `src/orchestration/decorators.py:71`
- **`test_retry_success_first_attempt`** (Function) — `tests/unit/orchestration/test_orchestrator_decorators.py:28`
- **`test_func`** (Function) — `tests/unit/orchestration/test_orchestrator_decorators.py:33`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `InputProcessorAgentProxy` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/proxies.py` | 19 |
| `WorldBuilderAgentProxy` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/proxies.py` | 205 |
| `NarrativeGeneratorAgentProxy` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/proxies.py` | 412 |
| `AgentProxy` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/interfaces.py` | 79 |
| `Agent` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/agents.py` | 68 |
| `MessageCoordinator` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/interfaces.py` | 22 |
| `RedisMessageCoordinator` | Class | `packages/tta-ai-framework/src/tta_ai/orchestration/coordinators/redis_message_coordinator.py` | 53 |
| `get_active_capabilities` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/models.py` | 204 |
| `match_capabilities` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/capability_matcher.py` | 49 |
| `retry` | Function | `src/orchestration/decorators.py` | 71 |
| `test_retry_success_first_attempt` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 28 |
| `test_func` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 33 |
| `test_retry_success_after_failures` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 41 |
| `test_retry_max_attempts_exceeded` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 54 |
| `test_retry_with_backoff` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 67 |
| `test_retry_with_specific_exceptions` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 85 |
| `test_retry_with_different_exception_not_caught` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 98 |
| `test_retry_with_timing` | Function | `tests/unit/orchestration/test_orchestrator_decorators.py` | 289 |
| `start_step` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/workflow_monitor.py` | 91 |
| `end_step` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/workflow_monitor.py` | 98 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Check_timeouts_once → _metrics_key` | cross_community | 6 |
| `Detect_scale_conflicts → _normalize_topic_values` | cross_community | 6 |
| `Check_timeouts_once → _audit_key` | intra_community | 5 |
| `Call → _state_key` | cross_community | 5 |
| `Call → _metrics_key` | cross_community | 5 |
| `Detect_scale_conflicts → _get_therapeutic_alignment` | cross_community | 5 |
| `Main → Visit` | cross_community | 4 |
| `Execute_workflow_async → _utc_now` | intra_community | 4 |
| `Call → Record_state_transition` | cross_community | 4 |
| `Process_user_input → To_dict` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Components | 2 calls |

## How to Explore

1. `gitnexus_context({name: "get_active_capabilities"})` — see callers and callees
2. `gitnexus_query({query: "orchestration"})` — find related execution flows
3. Read key files listed above for implementation details
