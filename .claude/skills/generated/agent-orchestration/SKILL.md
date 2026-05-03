---
name: agent-orchestration
description: "Skill for the Agent_orchestration area of TTA. 302 symbols across 39 files."
---

# Agent_orchestration

302 symbols | 39 files | Cohesion: 80%

## When to Use

- Working with code in `src/`
- Understanding how start_step, end_step, complete_run work
- Modifying agent_orchestration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | _mock_redis, _run_record, test_dump_includes_step_warned_flag, test_start_step_appends_step, test_end_step_sets_ended_at (+26) |
| `src/agent_orchestration/workflow_monitor.py` | _run_key, start_step, end_step, complete_run, fail_run (+15) |
| `tests/unit/agent_orchestration/test_unified_orchestrator_src.py` | test_save_state_skips_without_redis, test_process_user_input_adapter_error_returns_failure_response, test_process_user_input_passes_world_context_to_wba, _mock_safety, _patched_orchestrator (+14) |
| `tests/unit/agent_orchestration/test_workflow_manager_src.py` | _simple_definition, _request, test_register_workflow_success, test_list_workflows_sorted, test_execute_workflow_unknown_name (+12) |
| `tests/unit/agent_orchestration/test_agent_orchestration_service_src.py` | _session, _service, test_process_user_input_raises_when_not_initialized, test_shutdown_clears_state, test_determine_workflow_type_simple_command (+11) |
| `src/agent_orchestration/state_validator.py` | _decode, _extract_priority, _brute_force_pass, _reschedule_payload, _repair_hash_tokens (+9) |
| `src/agent_orchestration/capability_matcher.py` | match_capabilities, _exact_match, _weighted_score_match, _fuzzy_match, _priority_based_match (+8) |
| `tests/unit/agent_orchestration/test_crisis_detector.py` | _make_ipa_mock_llm, test_ipa_attaches_crisis_level_critical, test_ipa_attaches_crisis_level_high, test_ipa_attaches_crisis_level_moderate, test_ipa_safety_signal_bumps_low_to_moderate (+8) |
| `src/agent_orchestration/workflow_manager.py` | register_workflow, list_workflows, execute_workflow, get_run_state, update_run_metadata (+7) |
| `tests/unit/agent_orchestration/test_wba_retry_migration.py` | _make_world_context, _make_processed_input, test_populates_all_fields, test_updated_true_when_updates_provided, test_world_state_contains_location (+6) |

## Entry Points

Start here when exploring this area:

- **`start_step`** (Function) — `src/agent_orchestration/workflow_monitor.py:91`
- **`end_step`** (Function) — `src/agent_orchestration/workflow_monitor.py:98`
- **`complete_run`** (Function) — `src/agent_orchestration/workflow_monitor.py:111`
- **`fail_run`** (Function) — `src/agent_orchestration/workflow_monitor.py:119`
- **`get_run`** (Function) — `src/agent_orchestration/workflow_monitor.py:131`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `MessageCoordinator` | Class | `src/agent_orchestration/interfaces.py` | 22 |
| `RedisMessageCoordinator` | Class | `src/agent_orchestration/coordinators/redis_message_coordinator.py` | 53 |
| `AgentProxy` | Class | `src/agent_orchestration/interfaces.py` | 79 |
| `Agent` | Class | `src/agent_orchestration/agents.py` | 68 |
| `start_step` | Function | `src/agent_orchestration/workflow_monitor.py` | 91 |
| `end_step` | Function | `src/agent_orchestration/workflow_monitor.py` | 98 |
| `complete_run` | Function | `src/agent_orchestration/workflow_monitor.py` | 111 |
| `fail_run` | Function | `src/agent_orchestration/workflow_monitor.py` | 119 |
| `get_run` | Function | `src/agent_orchestration/workflow_monitor.py` | 131 |
| `record_rollback_audit` | Function | `src/agent_orchestration/workflow_monitor.py` | 135 |
| `check_timeouts_once` | Function | `src/agent_orchestration/workflow_monitor.py` | 155 |
| `test_dump_includes_step_warned_flag` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 91 |
| `test_start_step_appends_step` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 135 |
| `test_end_step_sets_ended_at` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 148 |
| `test_end_step_with_error_sets_failed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 161 |
| `test_start_step_noop_on_missing_run` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 174 |
| `test_complete_run_sets_completed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 188 |
| `test_fail_run_sets_failed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 201 |
| `test_fail_run_closes_open_step` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 213 |
| `test_get_run_returns_none_on_miss` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 231 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Session_turn → _minimal_world_context` | cross_community | 4 |
| `Match_capabilities → _check_agent_availability` | intra_community | 3 |
| `Match_capabilities → Get_active_capabilities` | intra_community | 3 |
| `Match_capabilities → _check_performance_match` | intra_community | 3 |
| `Match_capabilities → _calculate_weighted_score` | intra_community | 3 |
| `Match_capabilities → _check_version_match` | intra_community | 3 |
| `Match_capabilities → _meets_basic_criteria` | intra_community | 3 |
| `Session_turn → Process` | cross_community | 3 |
| `Process → _extract_themes` | intra_community | 3 |
| `Preview → _measure_queue_length` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Registries | 2 calls |
| Openhands_integration | 1 calls |

## How to Explore

1. `gitnexus_context({name: "start_step"})` — see callers and callees
2. `gitnexus_query({query: "agent_orchestration"})` — find related execution flows
3. Read key files listed above for implementation details
