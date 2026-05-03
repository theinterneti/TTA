---
name: scripts
description: "Skill for the Scripts area of TTA. 236 symbols across 72 files."
---

# Scripts

236 symbols | 72 files | Cohesion: 91%

## When to Use

- Working with code in `scripts/`
- Understanding how generate_tests_for_module, main, generate_for_module work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `scripts/todo-audit.py` | _write, _print_todos, _print_issues, _print_milestones, _print_report (+8) |
| `scripts/dev_with_recovery.py` | run_linting_fix, run_formatting, run_tests, cmd_quality_fix, cmd_dev_check (+6) |
| `scripts/validate_player_experience_deployment.py` | log_test_result, test_configuration_loading, test_orchestrator_initialization, test_component_configuration, test_component_dependencies (+5) |
| `src/player_experience/franchise_worlds/scripts/initialize-system.js` | runSystemValidation, testWorldRetrieval, testWorldValidation, testSystemIntegration, initializeSystem (+4) |
| `scripts/validate_manual_testing_guide.py` | log_validation, validate_phase1_initial_setup, validate_phase2_api_documentation, validate_phase3_authentication, validate_phase4_session_management (+4) |
| `tests/unit/scripts/test_check_agent_docs.py` | run_check, make_lines, test_passes_when_all_files_under_budget, test_fails_when_file_over_budget, test_reports_exact_line_count (+4) |
| `scripts/comprehensive_frontend_test.py` | log_test_result, test_server_accessibility, test_openapi_specification, test_health_endpoint, test_session_creation_endpoint (+3) |
| `scripts/migrate-to-kb.py` | convert, _add_frontmatter, _update_frontmatter, load_docs, _save_scan_results (+3) |
| `scripts/validate_internal_links.py` | extract_links_from_line, is_internal_link, validate_link, main, process_grep_output (+2) |
| `scripts/check-performance-budget.js` | checkBudgets, generateReport, groupViolationsBySeverity, generateMarkdownReport, main (+2) |

## Entry Points

Start here when exploring this area:

- **`generate_tests_for_module`** (Function) — `scripts/generate_tests_for_modules.py:69`
- **`main`** (Function) — `scripts/generate_tests_for_modules.py:126`
- **`generate_for_module`** (Function) — `scripts/generate_tests_batch.py:63`
- **`main`** (Function) — `scripts/generate_tests_batch.py:145`
- **`main`** (Function) — `scripts/generate_tests.py:105`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `generate_tests_for_module` | Function | `scripts/generate_tests_for_modules.py` | 69 |
| `main` | Function | `scripts/generate_tests_for_modules.py` | 126 |
| `generate_for_module` | Function | `scripts/generate_tests_batch.py` | 63 |
| `main` | Function | `scripts/generate_tests_batch.py` | 145 |
| `main` | Function | `scripts/generate_tests.py` | 105 |
| `execute_test_generation` | Function | `scripts/execute_test_generation.py` | 43 |
| `main` | Function | `scripts/execute_test_generation.py` | 144 |
| `create_test_generation_task` | Function | `src/agent_orchestration/openhands_integration/test_task_builder.py` | 13 |
| `generate_tests` | Function | `src/agent_orchestration/openhands_integration/test_generation_service.py` | 95 |
| `generate_package_tests` | Function | `src/agent_orchestration/openhands_integration/test_generation_service.py` | 350 |
| `extract_test_files_from_output` | Function | `src/agent_orchestration/openhands_integration/test_file_extractor.py` | 13 |
| `classify_error` | Function | `src/agent_orchestration/openhands_integration/test_error_handler.py` | 18 |
| `create_retry_feedback` | Function | `src/agent_orchestration/openhands_integration/test_error_handler.py` | 211 |
| `main` | Function | `_archive/openhands/scripts/test_openhands_workflow.py` | 41 |
| `simulate_test_generation` | Function | `_archive/openhands/scripts/test_openhands_integration.py` | 191 |
| `main` | Function | `_archive/openhands/scripts/test_openhands_integration.py` | 292 |
| `generate_test_for_module` | Function | `scripts/generate_batch1_tests_sdk.py` | 36 |
| `main` | Function | `scripts/generate_batch1_tests_sdk.py` | 78 |
| `generate_tests_for_module` | Function | `scripts/execute_batch_test_generation.py` | 92 |
| `execute_batch` | Function | `scripts/execute_batch_test_generation.py` | 146 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _run_command` | cross_community | 4 |
| `Generate_report → _run_command` | cross_community | 4 |
| `Main → _is_text_file` | cross_community | 3 |
| `Main → _categorize_todo` | cross_community | 3 |
| `Main → _prioritize_todo` | cross_community | 3 |
| `Generate_report → _is_text_file` | intra_community | 3 |
| `Generate_report → _categorize_todo` | intra_community | 3 |
| `Generate_report → _prioritize_todo` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Orchestration | 9 calls |
| Openhands_integration | 5 calls |
| Api_gateway | 2 calls |
| Simulation | 1 calls |
| Analysis | 1 calls |
| Workflow | 1 calls |
| Primitives | 1 calls |

## How to Explore

1. `gitnexus_context({name: "generate_tests_for_module"})` — see callers and callees
2. `gitnexus_query({query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
