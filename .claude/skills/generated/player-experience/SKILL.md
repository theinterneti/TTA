---
name: player-experience
description: "Skill for the Player_experience area of TTA. 71 symbols across 10 files."
---

# Player_experience

71 symbols | 10 files | Cohesion: 98%

## When to Use

- Working with code in `tests/`
- Understanding how test_compute_progress_summary, run, test_detect_and_update_milestones work
- Modifying player_experience-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/player_experience/test_session_management.py` | setUp, test_mgr_create_session_pytest, test_mgr_switch_context_new_session_pytest, test_mgr_switch_context_existing_session_pytest, test_mgr_pause_session_pytest (+10) |
| `tests/unit/player_experience/test_character_create_endpoint.py` | _make_character, _make_neo4j_session, _make_driver, _make_redis, _make_service (+8) |
| `tests/unit/player_experience/test_progress_tracking_service.py` | test_compute_progress_summary, run, test_detect_and_update_milestones, test_generate_progress_insights, test_get_visualization_data (+7) |
| `src/player_experience/test_deployment.py` | log_test_result, test_health_endpoint, test_api_documentation, test_player_management_endpoints, test_character_management_endpoints (+6) |
| `tests/unit/player_experience/test_player_experience_manager.py` | test_dashboard_aggregation, run, test_recommendations_combined, test_feedback_processing, test_crisis_detection_integration (+5) |
| `src/player_experience/models/player.py` | add_character, remove_character, get_active_session |
| `tests/unit/player_experience/test_progress_tracking_highlights.py` | test_highlights_created_for_session_milestone, run, test_highlights_created_for_streak_milestone |
| `tests/unit/player_experience/test_player_profile_database.py` | test_player_profile_character_limit, test_player_profile_character_management |
| `src/player_experience/models/session.py` | add_progress_marker |
| `tests/unit/player_experience/test_player_experience_models.py` | test_player_character_management |

## Entry Points

Start here when exploring this area:

- **`test_compute_progress_summary`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:88`
- **`run`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:90`
- **`test_detect_and_update_milestones`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:99`
- **`test_generate_progress_insights`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:112`
- **`test_get_visualization_data`** (Function) — `tests/unit/player_experience/test_progress_tracking_service.py:122`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_compute_progress_summary` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 88 |
| `run` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 90 |
| `test_detect_and_update_milestones` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 99 |
| `test_generate_progress_insights` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 112 |
| `test_get_visualization_data` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 122 |
| `test_therapeutic_effectiveness_report` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 133 |
| `test_milestone_celebration` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 148 |
| `test_enhanced_progress_summary_with_therapeutic_integration` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 167 |
| `test_comprehensive_milestone_detection` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 217 |
| `test_enhanced_progress_insights_generation` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 258 |
| `test_dropout_risk_calculation` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 299 |
| `test_visualization_data_accuracy` | Function | `tests/unit/player_experience/test_progress_tracking_service.py` | 408 |
| `add_progress_marker` | Function | `src/player_experience/models/session.py` | 95 |
| `test_happy_path_returns_character_id_and_summary` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 193 |
| `test_world_not_found_returns_404` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 217 |
| `test_player_prefs_passed_to_service` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 232 |
| `test_character_persisted_to_neo4j` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 253 |
| `test_redis_session_state_initialized` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 289 |
| `test_service_failure_returns_500` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 318 |
| `test_no_neo4j_driver_falls_back_gracefully` | Function | `tests/unit/player_experience/test_character_create_endpoint.py` | 346 |

## How to Explore

1. `gitnexus_context({name: "test_compute_progress_summary"})` — see callers and callees
2. `gitnexus_query({query: "player_experience"})` — find related execution flows
3. Read key files listed above for implementation details
