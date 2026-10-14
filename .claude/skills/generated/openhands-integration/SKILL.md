---
name: openhands-integration
description: "Skill for the Openhands_integration area of TTA. 83 symbols across 28 files."
---

# Openhands_integration

83 symbols | 28 files | Cohesion: 75%

## When to Use

- Working with code in `src/`
- Understanding how main, main, run work
- Modifying openhands_integration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/agent_orchestration/openhands_integration/config.py` | from_env, get_hardcoded_fallback_models, get_model_registry, filter_models, get_fallback_model_chain (+4) |
| `src/agent_orchestration/openhands_integration/test_e2e.py` | test_execution_engine, test_task_queue, test_model_selector, test_integration, main (+2) |
| `src/agent_orchestration/openhands_integration/cli.py` | run, metrics, submit_task, get_status, queue_stats (+1) |
| `src/agent_orchestration/openhands_integration/execution_engine.py` | start, stop, submit_task, get_queue_stats, _worker (+1) |
| `src/agent_orchestration/openhands_integration/model_rotation.py` | get_current_model, get_next_model, on_success, on_failure, on_rate_limit (+1) |
| `tests/integration/openhands_integration/test_error_recovery.py` | test_classify_connection_error, test_classify_timeout_error, test_classify_authentication_error, test_classify_rate_limit_error, test_classify_validation_error (+1) |
| `src/agent_orchestration/openhands_integration/error_recovery.py` | classify_openhands_error, execute_with_recovery, execute_with_retry, _execute_with_circuit_breaker, _generate_mock_response |
| `src/agent_orchestration/openhands_integration/optimized_client.py` | _get_cache_key, _initialize_sdk, _initialize_agent, _reset_conversation, execute_task |
| `src/agent_orchestration/openhands_integration/test_result_validator.py` | validate_generated_tests, validate_test_conventions, _run_tests, _run_coverage, run_command |
| `src/agent_orchestration/openhands_integration/workflow_integration.py` | get_task_status, generate_tests, _execute_test_generation |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `scripts/generate_tests_batch1.py:74`
- **`main`** (Function) — `scripts/phase7_batch_execution_final.py:103`
- **`run`** (Function) — `src/agent_orchestration/openhands_integration/cli.py:99`
- **`metrics`** (Function) — `src/agent_orchestration/openhands_integration/cli.py:164`
- **`test_execution_engine`** (Function) — `src/agent_orchestration/openhands_integration/test_e2e.py:174`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `scripts/generate_tests_batch1.py` | 74 |
| `main` | Function | `scripts/phase7_batch_execution_final.py` | 103 |
| `run` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 99 |
| `metrics` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 164 |
| `test_execution_engine` | Function | `src/agent_orchestration/openhands_integration/test_e2e.py` | 174 |
| `test_model_with_rotation` | Function | `scripts/test_rotation_system.py` | 95 |
| `main` | Function | `scripts/test_rotation_system.py` | 192 |
| `main` | Function | `_archive/openhands/scripts/diagnose_openhands.py` | 28 |
| `main` | Function | `scripts/generate_tier1_tests.py` | 138 |
| `submit_task` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 58 |
| `get_status` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 114 |
| `queue_stats` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 141 |
| `run_engine` | Function | `src/agent_orchestration/openhands_integration/cli.py` | 186 |
| `debug_conversation_structure` | Function | `_archive/openhands/scripts/debug_openhands_output.py` | 32 |
| `get_hardcoded_fallback_models` | Function | `src/agent_orchestration/openhands_integration/config.py` | 114 |
| `get_model_registry` | Function | `src/agent_orchestration/openhands_integration/config.py` | 164 |
| `filter_models` | Function | `src/agent_orchestration/openhands_integration/config.py` | 192 |
| `get_fallback_model_chain` | Function | `src/agent_orchestration/openhands_integration/config.py` | 351 |
| `get_model_by_preset` | Function | `src/agent_orchestration/openhands_integration/config.py` | 418 |
| `with_retry_async` | Function | `scripts/primitives/error_recovery.py` | 244 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_status → _execute_task` | cross_community | 5 |
| `Main → _execute_task` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Scripts | 4 calls |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "openhands_integration"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
