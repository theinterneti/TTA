---
name: scripts
description: "Skill for the Scripts area of TTA. 265 symbols across 72 files."
---

# Scripts

265 symbols | 72 files | Cohesion: 84%

## When to Use

- Working with code in `scripts/`
- Understanding how simulate_test_generation, main, main work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/play.py` | _parse_state_block, _call_ollama, _extract_state_ollama, _normalize_state, _lc_to_dicts (+11) |
| `scripts/todo-audit.py` | _write, _print_todos, _print_issues, _print_milestones, _print_report (+8) |
| `src/player_experience/franchise_worlds/scripts/initialize-system.js` | initializeValidationSystem, testWorldValidation, initializeArchetypeSystem, testSystemIntegration, initializeSystem (+6) |
| `scripts/dev_with_recovery.py` | run_linting_fix, run_formatting, run_tests, cmd_quality_fix, cmd_dev_check (+6) |
| `scripts/validate_player_experience_deployment.py` | log_test_result, test_configuration_loading, test_orchestrator_initialization, test_component_configuration, test_component_dependencies (+5) |
| `scripts/check-performance-budget.js` | checkBudgets, analyzeResults, analyzeSuite, main, analyzeSpec (+5) |
| `scripts/validate_manual_testing_guide.py` | log_validation, validate_phase1_initial_setup, validate_phase2_api_documentation, validate_phase3_authentication, validate_phase4_session_management (+4) |
| `tests/unit/scripts/test_check_agent_docs.py` | run_check, make_lines, test_passes_when_all_files_under_budget, test_fails_when_file_over_budget, test_reports_exact_line_count (+4) |
| `scripts/comprehensive_frontend_test.py` | log_test_result, test_server_accessibility, test_openapi_specification, test_health_endpoint, test_session_creation_endpoint (+3) |
| `scripts/migrate-to-kb.py` | convert, _add_frontmatter, _update_frontmatter, load_docs, _save_scan_results (+3) |

## Entry Points

Start here when exploring this area:

- **`simulate_test_generation`** (Function) — `_archive/openhands/scripts/test_openhands_integration.py:191`
- **`main`** (Function) — `_archive/openhands/scripts/test_openhands_integration.py:292`
- **`main`** (Function) — `_archive/openhands/scripts/test_openhands_workflow.py:41`
- **`execute_test_generation`** (Function) — `scripts/execute_test_generation.py:43`
- **`main`** (Function) — `scripts/execute_test_generation.py:144`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `simulate_test_generation` | Function | `_archive/openhands/scripts/test_openhands_integration.py` | 191 |
| `main` | Function | `_archive/openhands/scripts/test_openhands_integration.py` | 292 |
| `main` | Function | `_archive/openhands/scripts/test_openhands_workflow.py` | 41 |
| `execute_test_generation` | Function | `scripts/execute_test_generation.py` | 43 |
| `main` | Function | `scripts/execute_test_generation.py` | 144 |
| `main` | Function | `scripts/generate_tests.py` | 105 |
| `generate_for_module` | Function | `scripts/generate_tests_batch.py` | 63 |
| `main` | Function | `scripts/generate_tests_batch.py` | 145 |
| `generate_tests_for_module` | Function | `scripts/generate_tests_for_modules.py` | 69 |
| `main` | Function | `scripts/generate_tests_for_modules.py` | 126 |
| `classify_error` | Function | `src/agent_orchestration/openhands_integration/test_error_handler.py` | 18 |
| `create_retry_feedback` | Function | `src/agent_orchestration/openhands_integration/test_error_handler.py` | 211 |
| `extract_test_files_from_output` | Function | `src/agent_orchestration/openhands_integration/test_file_extractor.py` | 13 |
| `create_test_generation_task` | Function | `src/agent_orchestration/openhands_integration/test_task_builder.py` | 13 |
| `demo_simple_task` | Function | `_archive/openhands/scripts/demo_openhands_subagent.py` | 38 |
| `main` | Function | `_archive/openhands/scripts/demo_openhands_subagent.py` | 108 |
| `build_redis_pool_manager` | Function | `_archive/openhands/scripts/openhands_build_component.py` | 42 |
| `main` | Function | `_archive/openhands/scripts/openhands_build_component.py` | 221 |
| `test_simple_file_creation` | Function | `_archive/openhands/scripts/test_openhands_e2e.py` | 41 |
| `main` | Function | `_archive/openhands/scripts/test_openhands_e2e.py` | 105 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _run_command` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Openhands_integration | 20 calls |
| Components | 5 calls |
| Orchestration | 3 calls |
| Genesis | 3 calls |
| Api_gateway | 2 calls |
| Workflow | 1 calls |
| Primitives | 1 calls |
| Analysis | 1 calls |

## How to Explore

1. `context({name: "simulate_test_generation"})` — see callers and callees
2. `query({search_query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
