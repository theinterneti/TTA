---
name: orchestration
description: "Skill for the Orchestration area of TTA. 269 symbols across 53 files."
---

# Orchestration

269 symbols | 53 files | Cohesion: 87%

## When to Use

- Working with code in `packages/`
- Understanding how log_entry_exit, timing_decorator, require_config work
- Modifying orchestration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `packages/tta-ai-framework/src/tta_ai/orchestration/workflow_monitor.py` | _run_key, _metrics_key, start_step, end_step, complete_run (+13) |
| `packages/tta-narrative-engine/src/tta_narrative/orchestration/scale_manager.py` | detect_scale_conflicts, get_active_events, _detect_temporal_conflicts, _detect_character_conflicts, _detect_thematic_conflicts (+13) |
| `tests/unit/orchestration/test_orchestrator_decorators.py` | test_timing_decorator_logs_execution_time, test_log_entry_exit_with_exception, test_log_entry_exit_with_timing, test_retry_success_first_attempt, test_func (+10) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/capability_matcher.py` | match_capabilities, _exact_match, _weighted_score_match, _fuzzy_match, _priority_based_match (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker.py` | _metrics_key, _load_metrics, initialize, _persist_metrics, _transition_to_half_open (+8) |
| `src/orchestration/config.py` | TTAConfig, get, validate, _validate_dict, __init__ (+6) |
| `src/orchestration/orchestrator.py` | TTAOrchestrator, has_component, start_component, stop_component, start_all (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/agents.py` | _key, register, deregister, get, run_health_checks_once (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/enhanced_coordinator.py` | execute_workflow, _execute_workflow_steps, _execute_ipa_step, _execute_wba_step, _execute_nga_step (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/circuit_breaker_registry.py` | _registry_key, get_or_create, list_names, sync_registry_with_redis, _cleanup_key (+5) |

## Entry Points

Start here when exploring this area:

- **`log_entry_exit`** (Function) — `src/orchestration/decorators.py:24`
- **`timing_decorator`** (Function) — `src/orchestration/decorators.py:49`
- **`require_config`** (Function) — `src/orchestration/decorators.py:211`
- **`test_system_startup`** (Function) — `scripts/dev_setup.py:163`
- **`main`** (Function) — `scripts/start_with_gameplay.py:29`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ModelManagementComponent` | Class | `packages/tta-ai-framework/src/tta_ai/models/model_management_component.py` | 40 |
| `AgentOrchestrationComponent` | Class | `src/components/agent_orchestration_component.py` | 50 |
| `AppComponent` | Class | `src/components/app_component.py` | 49 |
| `CarbonComponent` | Class | `src/components/carbon_component.py` | 62 |
| `DockerComponent` | Class | `src/components/docker_component.py` | 60 |
| `GameplayLoopComponent` | Class | `src/components/gameplay_loop_component.py` | 26 |
| `LLMComponent` | Class | `src/components/llm_component.py` | 52 |
| `ModelManagementComponent` | Class | `src/components/model_management/model_management_component.py` | 40 |
| `Neo4jComponent` | Class | `src/components/neo4j_component.py` | 49 |
| `PlayerExperienceComponent` | Class | `src/components/player_experience_component.py` | 53 |
| `Component` | Class | `src/orchestration/component.py` | 60 |
| `TTAConfig` | Class | `src/orchestration/config.py` | 44 |
| `TTAOrchestrator` | Class | `src/orchestration/orchestrator.py` | 55 |
| `log_entry_exit` | Function | `src/orchestration/decorators.py` | 24 |
| `timing_decorator` | Function | `src/orchestration/decorators.py` | 49 |
| `require_config` | Function | `src/orchestration/decorators.py` | 211 |
| `test_system_startup` | Function | `scripts/dev_setup.py` | 163 |
| `main` | Function | `scripts/start_with_gameplay.py` | 29 |
| `main` | Function | `src/main.py` | 191 |
| `test_player_experience_lifecycle_via_orchestrator` | Function | `tests/unit/orchestration/test_orchestrator_lifecycle_validation.py` | 14 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Check_timeouts_once → _metrics_key` | cross_community | 6 |
| `Check_timeouts_once → _audit_key` | intra_community | 5 |
| `Main → Visit` | intra_community | 4 |
| `Execute_workflow_async → _utc_now` | intra_community | 4 |
| `Call → _state_key` | cross_community | 4 |
| `Call → _metrics_key` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Registries | 4 calls |

## How to Explore

1. `context({name: "log_entry_exit"})` — see callers and callees
2. `query({search_query: "orchestration"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
