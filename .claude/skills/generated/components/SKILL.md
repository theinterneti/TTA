---
name: components
description: "Skill for the Components area of TTA. 366 symbols across 51 files."
---

# Components

366 symbols | 51 files | Cohesion: 70%

## When to Use

- Working with code in `tests/`
- Understanding how client_factory, set_session_goals, health_check work
- Modifying components-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/components/narrative_arc_orchestrator_component.py` | _normalize_session_state, _coerce_datetime, _resolve_current_scale, _update_current_scale_from_response, initialize_session (+54) |
| `tests/unit/components/test_therapeutic_narrative_modules.py` | test_set_therapeutic_goals, test_set_therapeutic_goals_empty_list, test_track_goal_progress, test_log_therapeutic_evidence, test_generate_progress_report (+45) |
| `tests/unit/components/test_mode_runner.py` | _mock_ollama_response, _mock_openrouter_response, _async_client_ctx, test_returns_ollama_response, test_ollama_called_with_correct_model (+17) |
| `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | _event, test_detect_therapeutic_conflicts_skips_same_scale_events, test_detect_therapeutic_conflicts_no_conflict_when_gap_small, test_detect_therapeutic_conflicts_single_event_no_pairs, test_detect_therapeutic_conflicts_unsafe_via_low_alignment (+16) |
| `tests/unit/components/test_nga_agent.py` | _make_llm, _simple_world_context, _rich_world_context, _simple_processed_input, test_includes_location_name (+11) |
| `tests/unit/components/test_default_character_world_service.py` | _make_service, test_skips_when_player_has_existing_characters, test_returns_none_triple_when_character_creation_fails, test_returns_char_and_none_when_world_not_found, test_full_success_returns_all_three_ids (+9) |
| `src/components/character_arc_manager.py` | initialize_character_arc, initialize_integrated_character_arc, get_integrated_character_summary, __init__, resolve_character_arc_milestone (+9) |
| `src/components/narrative_coherence_engine.py` | resolve_narrative_conflicts, generate_creative_solutions, _implement_conflict_resolution, manage_retroactive_changes, _validate_retroactive_changes (+6) |
| `tests/unit/components/test_ipa_agent.py` | test_parses_clean_json, test_strips_markdown_fences, test_raises_on_invalid_json, _make_llm, test_interact_intent_with_npc (+6) |
| `tests/unit/components/test_wba_agent.py` | _make_processed_input, _make_world_context, _make_builder, test_returns_stub_when_no_builder, test_returns_stub_when_no_location_id (+5) |

## Entry Points

Start here when exploring this area:

- **`client_factory`** (Function) — `tests/unit/components/test_mode_runner.py:195`
- **`set_session_goals`** (Function) — `src/player_experience/api/routers/conversation.py:1122`
- **`health_check`** (Function) — `scripts/health_check_carbon.py:9`
- **`test_start_uses_injected_dependency_adapters_and_stop_closes_them`** (Function) — `tests/unit/components/test_narrative_arc_orchestrator_component.py:242`
- **`test_engine_start_stop`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:414`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `client_factory` | Function | `tests/unit/components/test_mode_runner.py` | 195 |
| `set_session_goals` | Function | `src/player_experience/api/routers/conversation.py` | 1122 |
| `health_check` | Function | `scripts/health_check_carbon.py` | 9 |
| `test_start_uses_injected_dependency_adapters_and_stop_closes_them` | Function | `tests/unit/components/test_narrative_arc_orchestrator_component.py` | 242 |
| `test_engine_start_stop` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 414 |
| `detect_therapeutic_conflicts` | Function | `src/components/narrative_arc_orchestrator/conflict_detection.py` | 31 |
| `test_detect_therapeutic_conflicts_skips_same_scale_events` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 123 |
| `test_detect_therapeutic_conflicts_no_conflict_when_gap_small` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 147 |
| `test_detect_therapeutic_conflicts_single_event_no_pairs` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 169 |
| `test_detect_therapeutic_conflicts_unsafe_via_low_alignment` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 174 |
| `test_detect_therapeutic_conflicts_therapeutic_reframe_when_no_safety` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 200 |
| `test_detect_therapeutic_conflicts_shared_topic_via_therapeutic_theme` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 226 |
| `test_detect_therapeutic_conflicts_severity_clamped_to_one` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 250 |
| `test_get_narrative_status_loads_persisted_session` | Function | `tests/unit/components/test_narrative_arc_orchestrator_component.py` | 60 |
| `test_trigger_emergent_event_loads_and_persists_session` | Function | `tests/unit/components/test_narrative_arc_orchestrator_component.py` | 146 |
| `test_calculate_emergent_probability_uses_context_and_cooldown` | Function | `tests/unit/components/test_narrative_arc_orchestrator_component.py` | 483 |
| `build_simple_resolution` | Function | `src/components/narrative_arc_orchestrator/resolution_engine.py` | 14 |
| `apply_resolution` | Function | `src/components/narrative_arc_orchestrator/resolution_engine.py` | 57 |
| `test_build_simple_resolution_non_therapeutic` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 279 |
| `test_build_simple_resolution_therapeutic_reframe` | Function | `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | 296 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Set_session_goals → _coerce_datetime` | intra_community | 5 |
| `Get_session_state → _coerce_datetime` | cross_community | 5 |
| `Get_session_state → _resolve_current_scale` | cross_community | 5 |
| `Set_session_goals → _get_session_persistence_adapter` | cross_community | 4 |
| `Set_session_goals → _invoke_async_adapter_method` | cross_community | 4 |
| `Set_session_goals → _merge_persisted_session_state` | cross_community | 4 |
| `Set_session_goals → _resolve_current_scale` | intra_community | 4 |
| `Set_session_goals → _deserialize_token_data` | cross_community | 4 |
| `Get_session_state → _get_session_persistence_adapter` | cross_community | 4 |
| `Get_session_state → _invoke_async_adapter_method` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Narrative | 35 calls |
| Agent_orchestration | 13 calls |
| Orchestration | 8 calls |
| Routers | 3 calls |
| Narrative_arc_orchestrator | 2 calls |
| Guide | 1 calls |

## How to Explore

1. `context({name: "client_factory"})` — see callers and callees
2. `query({search_query: "components"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
