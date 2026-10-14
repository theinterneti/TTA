---
name: player-experience
description: "Skill for the Player_experience area of TTA. 81 symbols across 10 files."
---

# Player_experience

81 symbols | 10 files | Cohesion: 95%

## When to Use

- Working with code in `tests/`
- Understanding how setup_logging, main, run work
- Modifying player_experience-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/player_experience/test_session_management.py` | setUp, test_mgr_create_session_pytest, test_mgr_switch_context_new_session_pytest, test_mgr_switch_context_existing_session_pytest, test_mgr_pause_session_pytest (+10) |
| `tests/unit/player_experience/test_character_create_endpoint.py` | _make_character, _make_neo4j_session, _make_driver, _make_redis, _make_service (+8) |
| `tests/unit/player_experience/test_progress_tracking_service.py` | test_compute_progress_summary, run, test_detect_and_update_milestones, test_generate_progress_insights, test_get_visualization_data (+7) |
| `src/player_experience/test_deployment.py` | log_test_result, test_health_endpoint, test_api_documentation, test_player_management_endpoints, test_character_management_endpoints (+6) |
| `src/player_experience/production_readiness.py` | run_comprehensive_assessment, _run_performance_checks, _run_security_checks, _run_monitoring_checks, _run_deployment_checks (+5) |
| `tests/unit/player_experience/test_player_experience_manager.py` | test_dashboard_aggregation, run, test_recommendations_combined, test_feedback_processing, test_crisis_detection_integration (+5) |
| `src/player_experience/monitoring/benchmarking.py` | run_all, _generate_summary_report, create_load_test, run_comprehensive_benchmark |
| `tests/unit/player_experience/test_progress_tracking_highlights.py` | test_highlights_created_for_session_milestone, run, test_highlights_created_for_streak_milestone |
| `src/player_experience/monitoring/logging_config.py` | info, setup_logging |
| `src/player_experience/models/session.py` | add_progress_marker |

## Entry Points

Start here when exploring this area:

- **`setup_logging`** (Function) — `src/player_experience/monitoring/logging_config.py:424`
- **`main`** (Function) — `src/player_experience/production_readiness.py:1242`
- **`run`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:90`
- **`run`** (Function) — `tests/unit/player_experience/test_player_experience_manager.py:157`
- **`test_mgr_create_session_pytest`** (Function) — `tests/unit/player_experience/test_session_management.py:647`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `setup_logging` | Function | `src/player_experience/monitoring/logging_config.py` | 424 |
| `main` | Function | `src/player_experience/production_readiness.py` | 1242 |
| `run` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 90 |
| `run` | Function | `tests/unit/player_experience/test_player_experience_manager.py` | 157 |
| `test_mgr_create_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 647 |
| `test_mgr_switch_context_new_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 655 |
| `test_mgr_switch_context_existing_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 663 |
| `test_mgr_pause_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 671 |
| `test_mgr_resume_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 679 |
| `test_mgr_end_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 687 |
| `test_mgr_update_session_interaction_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 695 |
| `test_mgr_add_progress_marker_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 703 |
| `test_mgr_update_therapeutic_settings_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 711 |
| `test_repo_create_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 615 |
| `test_repo_get_session_from_cache_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 623 |
| `test_repo_pause_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 631 |
| `test_repo_end_session_pytest` | Function | `tests/unit/player_experience/test_session_management.py` | 639 |
| `main` | Function | `src/player_experience/test_deployment.py` | 485 |
| `test_highlights_created_for_session_milestone` | Function | `tests/unit/player_experience/test_progress_tracking_highlights.py` | 32 |
| `run` | Function | `tests/unit/player_experience/test_progress_tracking_highlights.py` | 57 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_comprehensive_assessment → _log` | cross_community | 4 |
| `Run_comprehensive_assessment → Create_load_test` | intra_community | 4 |
| `Run_comprehensive_assessment → Add_benchmark` | intra_community | 4 |
| `Dispatch → _log` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Monitoring | 7 calls |
| Security | 2 calls |
| Managers | 2 calls |

## How to Explore

1. `context({name: "setup_logging"})` — see callers and callees
2. `query({search_query: "player_experience"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
