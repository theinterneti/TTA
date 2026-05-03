---
name: gameplay-loop
description: "Skill for the Gameplay_loop area of TTA. 220 symbols across 13 files."
---

# Gameplay_loop

220 symbols | 13 files | Cohesion: 83%

## When to Use

- Working with code in `tests/`
- Understanding how test_pause_returns_200_on_success, test_pause_returns_401_on_auth_error, test_pause_returns_404_on_session_not_found work
- Modifying gameplay_loop-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/components/gameplay_loop/test_gameplay_loop_consequence.py` | _make_user_choice, _make_session, test_falls_back_on_exception, test_returns_fallback_on_exception, test_returns_dict_with_expected_keys (+43) |
| `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | _build_test_app, _make_service_mock, test_pause_returns_200_on_success, test_pause_returns_401_on_auth_error, test_pause_returns_404_on_session_not_found (+42) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_validator.py` | _make_session, _make_choice, test_valid_choices_pass, test_choices_with_prohibited_content_are_filtered, test_returns_original_choices_on_exception (+30) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_outcome_generator.py` | _has_unfilled_placeholder, _make_scene, _make_session, _make_user_choice, test_returns_dict (+27) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_generator.py` | _make_scene, _make_session, _base_requirements, test_returns_up_to_max_choices, test_fills_max_choices_slots (+16) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_narrative_engine.py` | _make_session, _make_scene, test_returns_scene, test_adapted_scene_has_new_id, test_crisis_adapts_scene_type (+8) |
| `tests/unit/components/gameplay_loop/test_gameplay_loop_dolt_manager.py` | _make_session, _mock_connection, test_returns_true_on_success, test_returns_session_state_when_found, test_returns_true_when_row_updated (+4) |
| `src/components/gameplay_loop/base.py` | get_active_session_count, get_performance_metrics, health_check, Component, GameplayLoopComponent (+2) |
| `src/components/gameplay_loop/controller.py` | initialize, resume_session, end_session, process_user_choice |
| `src/components/gameplay_loop/consequence_system/system.py` | evaluate_consequence_impact |

## Entry Points

Start here when exploring this area:

- **`test_pause_returns_200_on_success`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py:219`
- **`test_pause_returns_401_on_auth_error`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py:239`
- **`test_pause_returns_404_on_session_not_found`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py:256`
- **`test_pause_returns_403_on_access_denied`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py:273`
- **`test_pause_calls_service_with_correct_session_id`** (Function) — `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py:290`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `Component` | Class | `src/components/gameplay_loop/base.py` | 26 |
| `GameplayLoopComponent` | Class | `src/components/gameplay_loop/base.py` | 104 |
| `test_pause_returns_200_on_success` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 219 |
| `test_pause_returns_401_on_auth_error` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 239 |
| `test_pause_returns_404_on_session_not_found` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 256 |
| `test_pause_returns_403_on_access_denied` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 273 |
| `test_pause_calls_service_with_correct_session_id` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 290 |
| `test_resume_returns_200_on_success` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 310 |
| `test_resume_returns_401_on_auth_error` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 336 |
| `test_resume_returns_404_on_session_not_found` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 353 |
| `test_resume_returns_403_on_access_denied` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 370 |
| `test_resume_returns_404_on_session_error` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 387 |
| `test_resume_calls_service_with_correct_session_id` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 404 |
| `test_resume_includes_session_data_in_response` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 423 |
| `test_create_returns_200_on_success` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 454 |
| `test_create_passes_therapeutic_context` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 477 |
| `test_create_returns_401_on_auth_error` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 499 |
| `test_create_returns_422_on_safety_error` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 517 |
| `test_create_accepts_empty_therapeutic_context` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 535 |
| `test_choice_returns_200_on_success` | Function | `tests/unit/components/gameplay_loop/test_gameplay_session_lifecycle.py` | 561 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Health_check → Get_active_session_count` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Consequence_system | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_pause_returns_200_on_success"})` — see callers and callees
2. `gitnexus_query({query: "gameplay_loop"})` — find related execution flows
3. Read key files listed above for implementation details
