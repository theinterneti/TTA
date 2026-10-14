---
name: gameplay-loop
description: "Skill for the Gameplay_loop area of TTA. 280 symbols across 15 files."
---

# Gameplay_loop

280 symbols | 15 files | Cohesion: 85%

## When to Use

- Working with code in `tests/`
- Understanding how run_basic_test, controller_with_fake_db, engine work
- Modifying gameplay_loop-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | _make_choice, _make_session, _make_scene, _make_outcomes, test_returns_dict_with_all_keys (+55) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence.py` | _make_user_choice, _make_session, test_falls_back_on_exception, test_returns_fallback_on_exception, test_returns_dict_with_expected_keys (+43) |
| `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | _build_test_app, _make_service_mock, test_pause_returns_200_on_success, test_pause_returns_401_on_auth_error, test_pause_returns_404_on_session_not_found (+42) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_validator.py` | _make_session, _make_choice, test_valid_choices_pass, test_choices_with_prohibited_content_are_filtered, test_returns_original_choices_on_exception (+30) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_outcome_generator.py` | _has_unfilled_placeholder, _make_scene, _make_session, _make_user_choice, test_returns_dict (+27) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_generator.py` | _make_scene, _make_session, _base_requirements, test_returns_up_to_max_choices, test_fills_max_choices_slots (+16) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py` | _make_session, _make_scene, test_returns_scene, test_adapted_scene_has_new_id, test_crisis_adapts_scene_type (+8) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_dolt_manager.py` | _make_session, _mock_connection, test_returns_true_on_success, test_returns_session_state_when_found, test_returns_true_when_row_updated (+4) |
| `src/components/gameplay_loop/base.py` | get_active_session_count, get_performance_metrics, health_check, stop, _cleanup_session_context |
| `src/components/gameplay_loop/controller.py` | initialize, resume_session, end_session, process_user_choice |

## Entry Points

Start here when exploring this area:

- **`run_basic_test`** (Function) — `tests/integration/test_core_gameplay_loop.py:331`
- **`controller_with_fake_db`** (Function) — `tests/integration/test_gameplay_e2e_smoke.py:151`
- **`engine`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py:97`
- **`engine_with_llm`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py:112`
- **`mock_controller`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_loop_controller.py:94`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `run_basic_test` | Function | `tests/integration/test_core_gameplay_loop.py` | 331 |
| `controller_with_fake_db` | Function | `tests/integration/test_gameplay_e2e_smoke.py` | 151 |
| `engine` | Function | `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py` | 97 |
| `engine_with_llm` | Function | `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py` | 112 |
| `mock_controller` | Function | `tests/unit/components/gameplay_loop/test_gameplay_loop_controller.py` | 94 |
| `test_returns_dict_with_all_keys` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 167 |
| `test_high_value_insight_content` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 180 |
| `test_medium_value_insight_content` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 186 |
| `test_low_value_insight_content` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 192 |
| `test_positive_emotion_adds_insight` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 200 |
| `test_known_tag_generates_learning_opportunity` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 207 |
| `test_unknown_tags_still_return_fallback_learning` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 213 |
| `test_therapeutic_value_in_range` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 219 |
| `test_positive_emotion_boosts_therapeutic_value` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 225 |
| `test_growth_aspects_include_resilience_tag` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 238 |
| `test_high_value_adds_therapeutic_engagement_aspect` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 247 |
| `test_positive_reframes_non_empty` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 253 |
| `test_returns_non_empty_string` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 383 |
| `test_calm_state_gives_direct_explanation` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 392 |
| `test_anxious_state_prefixes_naturally` | Method | `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence_components.py` | 401 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Consequence_system | 1 calls |

## How to Explore

1. `context({name: "run_basic_test"})` — see callers and callees
2. `query({search_query: "gameplay_loop"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
