---
name: openhands-integration
description: "Skill for the Openhands_integration area of TTA. 79 symbols across 25 files."
---

# Openhands_integration

79 symbols | 25 files | Cohesion: 79%

## When to Use

- Working with code in `src/`
- Understanding how main, main, test_execution_engine work
- Modifying openhands_integration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/agent_orchestration/openhands_integration/config.py` | from_env, get_hardcoded_fallback_models, get_model_registry, filter_models, get_fallback_model_chain (+5) |
| `src/agent_orchestration/openhands_integration/test_e2e.py` | test_execution_engine, test_task_queue, test_model_selector, test_integration, main (+1) |
| `src/agent_orchestration/openhands_integration/execution_engine.py` | start, stop, submit_task, get_queue_stats, _worker (+1) |
| `src/agent_orchestration/openhands_integration/cli.py` | metrics, submit_task, run, get_status, queue_stats (+1) |
| `src/agent_orchestration/openhands_integration/model_rotation.py` | get_current_model, get_next_model, on_success, on_failure, on_rate_limit (+1) |
| `tests/integration/openhands_integration/test_error_recovery.py` | test_classify_connection_error, test_classify_timeout_error, test_classify_authentication_error, test_classify_rate_limit_error, test_classify_validation_error (+1) |
| `src/agent_orchestration/openhands_integration/error_recovery.py` | classify_openhands_error, execute_with_recovery, execute_with_retry, _execute_with_circuit_breaker, _generate_mock_response |
| `src/agent_orchestration/openhands_integration/optimized_client.py` | _get_cache_key, _initialize_sdk, _initialize_agent, _reset_conversation, execute_task |
| `src/agent_orchestration/openhands_integration/test_result_validator.py` | validate_generated_tests, validate_test_conventions, _run_tests, _run_coverage, run_command |
| `src/agent_orchestration/openhands_integration/workflow_integration.py` | get_task_status, generate_tests, _execute_test_generation |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `scripts/phase7_batch_execution_final.py:103`
- **`main`** (Function) — `scripts/generate_tests_batch1.py:74`
- **`test_execution_engine`** (Function) — `src/agent_orchestration/openhands_integration/test_e2e.py:174`
- **`start`** (Function) — `src/agent_orchestration/openhands_integration/execution_engine.py:59`
- **`stop`** (Function) — `src/agent_orchestration/openhands_integration/execution_engine.py:75`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `scripts/phase7_batch_execution_final.py` | 103 |
| `main` | Function | `scripts/generate_tests_batch1.py` | 74 |
| `test_execution_engine` | Function | `src/agent_orchestration/openhands_integration/test_e2e.py` | 174 |
| `start` | Function | `src/agent_orchestration/openhands_integration/execution_engine.py` | 59 |
| `stop` | Function | `src/agent_orchestration/openhands_integration/execution_engine.py` | 75 |
| `submit_task` | Function | `src/agent_orchestration/openhands_integration/execution_engine.py` | 91 |
| `get_queue_stats` | Function | `src/agent_orchestration/openhands_integration/execution_engine.py` | 115 |
| `get_metrics_summary` | Function | `src/agent_orchestration/openhands_integration/execution_engine.py` | 226 |
| `metrics` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 164 |
| `test_model_with_rotation` | Function | `scripts/test_rotation_system.py` | 95 |
| `main` | Function | `scripts/test_rotation_system.py` | 192 |
| `get_current_model` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 174 |
| `get_next_model` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 178 |
| `on_success` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 201 |
| `on_failure` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 213 |
| `on_rate_limit` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 233 |
| `get_summary` | Function | `src/agent_orchestration/openhands_integration/model_rotation.py` | 281 |
| `test_classify_connection_error` | Function | `tests/integration/openhands_integration/test_error_recovery.py` | 28 |
| `test_classify_timeout_error` | Function | `tests/integration/openhands_integration/test_error_recovery.py` | 44 |
| `test_classify_authentication_error` | Function | `tests/integration/openhands_integration/test_error_recovery.py` | 58 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_status → _execute_task` | cross_community | 5 |
| `Main → _execute_task` | intra_community | 4 |
| `Get_status → Submit_task` | cross_community | 3 |
| `Get_status → Stop` | cross_community | 3 |
| `Get_status → Get_task_status` | intra_community | 3 |
| `Execute_task → _get_cache_key` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Scripts | 2 calls |

## How to Explore

1. `gitnexus_context({name: "main"})` — see callers and callees
2. `gitnexus_query({query: "openhands_integration"})` — find related execution flows
3. Read key files listed above for implementation details
