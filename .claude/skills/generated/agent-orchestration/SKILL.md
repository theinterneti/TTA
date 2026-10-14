---
name: agent-orchestration
description: "Skill for the Agent_orchestration area of TTA. 360 symbols across 50 files."
---

# Agent_orchestration

360 symbols | 50 files | Cohesion: 78%

## When to Use

- Working with code in `tests/`
- Understanding how test_dump_includes_step_warned_flag, test_start_step_appends_step, test_end_step_sets_ended_at work
- Modifying agent_orchestration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/agent_orchestration/test_agent_orchestration_service_src.py` | _service, test_process_user_input_raises_when_not_initialized, test_process_user_input_happy_path, test_process_user_input_increments_request_count, test_process_user_input_re_raises_therapeutic_safety_error (+32) |
| `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | _mock_redis, _run_record, test_dump_includes_step_warned_flag, test_start_step_appends_step, test_end_step_sets_ended_at (+26) |
| `src/agent_orchestration/workflow_monitor.py` | _run_key, start_step, end_step, complete_run, fail_run (+15) |
| `tests/unit/agent_orchestration/test_unified_orchestrator_src.py` | test_save_state_skips_without_redis, test_process_user_input_adapter_error_returns_failure_response, test_process_user_input_passes_world_context_to_wba, _mock_safety, _patched_orchestrator (+14) |
| `tests/unit/agent_orchestration/test_workflow_manager_src.py` | _simple_definition, _request, test_register_workflow_success, test_list_workflows_sorted, test_execute_workflow_unknown_name (+12) |
| `src/agent_orchestration/service.py` | process_user_input, _update_session_context, _determine_workflow_type, initialize, _validate_therapeutic_safety (+9) |
| `src/agent_orchestration/state_validator.py` | _decode, _extract_priority, _brute_force_pass, _reschedule_payload, _repair_hash_tokens (+9) |
| `src/agent_orchestration/capability_matcher.py` | match_capabilities, _exact_match, _weighted_score_match, _fuzzy_match, _priority_based_match (+8) |
| `tests/unit/agent_orchestration/test_crisis_detector.py` | _make_ipa_mock_llm, test_ipa_attaches_crisis_level_critical, test_ipa_attaches_crisis_level_high, test_ipa_attaches_crisis_level_moderate, test_ipa_safety_signal_bumps_low_to_moderate (+8) |
| `src/agent_orchestration/workflow_manager.py` | register_workflow, list_workflows, execute_workflow, get_run_state, update_run_metadata (+7) |

## Entry Points

Start here when exploring this area:

- **`test_dump_includes_step_warned_flag`** (Function) — `tests/integration/agent_orchestration/test_workflow_monitor_src.py:91`
- **`test_start_step_appends_step`** (Function) — `tests/integration/agent_orchestration/test_workflow_monitor_src.py:135`
- **`test_end_step_sets_ended_at`** (Function) — `tests/integration/agent_orchestration/test_workflow_monitor_src.py:148`
- **`test_end_step_with_error_sets_failed_status`** (Function) — `tests/integration/agent_orchestration/test_workflow_monitor_src.py:161`
- **`test_start_step_noop_on_missing_run`** (Function) — `tests/integration/agent_orchestration/test_workflow_monitor_src.py:174`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_dump_includes_step_warned_flag` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 91 |
| `test_start_step_appends_step` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 135 |
| `test_end_step_sets_ended_at` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 148 |
| `test_end_step_with_error_sets_failed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 161 |
| `test_start_step_noop_on_missing_run` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 174 |
| `test_complete_run_sets_completed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 188 |
| `test_fail_run_sets_failed_status` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 201 |
| `test_fail_run_closes_open_step` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 213 |
| `test_get_run_returns_none_on_miss` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 231 |
| `test_get_run_returns_dict` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 239 |
| `test_check_timeouts_once_skips_non_running_runs` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 319 |
| `test_check_timeouts_once_transitions_timed_out_run` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 334 |
| `test_check_timeouts_once_handles_parse_error_gracefully` | Function | `tests/integration/agent_orchestration/test_workflow_monitor_src.py` | 353 |
| `test_callable_registry_and_execute` | Function | `tests/integration/agent_orchestration/test_callable_registry_and_execute_endpoint.py` | 23 |
| `test_agents_endpoint_and_auto_register` | Function | `tests/integration/agent_orchestration/test_component_agents_endpoint_and_auto_register.py` | 10 |
| `test_poll_queue_metrics_once` | Function | `tests/integration/agent_orchestration/test_component_diagnostics_and_polling.py` | 16 |
| `test_diagnostics_gated_and_prometheus` | Function | `tests/integration/agent_orchestration/test_diagnostics_prometheus_and_admin.py` | 17 |
| `test_policy_snapshot_and_redaction` | Function | `tests/integration/agent_orchestration/test_policy_live_reload_and_diagnostics.py` | 15 |
| `test_manual_reload_and_status` | Function | `tests/integration/agent_orchestration/test_policy_live_reload_and_diagnostics.py` | 54 |
| `test_live_reload_applies_and_rollback` | Function | `tests/integration/agent_orchestration/test_policy_live_reload_and_diagnostics.py` | 113 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Session_turn → _minimal_world_context` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Components | 16 calls |
| Registries | 4 calls |
| Openhands_integration | 1 calls |

## How to Explore

1. `context({name: "test_dump_includes_step_warned_flag"})` — see callers and callees
2. `query({search_query: "agent_orchestration"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
