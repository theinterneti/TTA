---
name: components
description: "Skill for the Components area of TTA. 191 symbols across 32 files."
---

# Components

191 symbols | 32 files | Cohesion: 74%

## When to Use

- Working with code in `tests/`
- Understanding how test_returns_ollama_response, test_ollama_called_with_correct_model, test_system_message_included_when_provided work
- Modifying components-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/components/test_mode_runner.py` | _mock_ollama_response, _mock_openrouter_response, _async_client_ctx, test_returns_ollama_response, test_ollama_called_with_correct_model (+17) |
| `tests/unit/components/test_narrative_arc_orchestrator_helpers.py` | _event, test_detect_therapeutic_conflicts_skips_same_scale_events, test_detect_therapeutic_conflicts_no_conflict_when_gap_small, test_detect_therapeutic_conflicts_single_event_no_pairs, test_detect_therapeutic_conflicts_unsafe_via_low_alignment (+16) |
| `tests/unit/components/test_nga_agent.py` | _rich_world_context, _simple_processed_input, test_includes_location_name, test_includes_npc_names, test_includes_events (+11) |
| `tests/unit/components/test_default_character_world_service.py` | _make_service, test_skips_when_player_has_existing_characters, test_returns_none_triple_when_character_creation_fails, test_returns_char_and_none_when_world_not_found, test_full_success_returns_all_three_ids (+9) |
| `tests/unit/components/test_ipa_agent.py` | _make_llm, test_interact_intent_with_npc, test_unknown_intent_on_bad_value, test_malformed_entity_skipped, _ipa_json (+6) |
| `tests/unit/components/test_wba_agent.py` | _make_processed_input, _make_world_context, _make_builder, test_returns_stub_when_no_builder, test_returns_stub_when_no_location_id (+5) |
| `src/components/docker_component.py` | _start_impl, _check_docker_installed, ensure_consistency, _copy_template_files, _standardize_container_names (+5) |
| `src/components/player_experience_component.py` | PlayerExperienceComponent, _start_impl, _stop_impl, _run_docker_compose, _check_dependencies_health (+4) |
| `tests/unit/components/test_free_model_tracker.py` | _or_api_payload, test_returns_only_free_models, test_force_refresh_ignores_fresh_cache, _make_mock_client, test_sends_auth_header_when_api_key_provided (+4) |
| `src/components/narrative_arc_orchestrator/conflict_detection.py` | detect_therapeutic_conflicts, _shares_therapeutic_context, _get_therapeutic_topics, _get_therapeutic_alignment, _is_unsafe (+3) |

## Entry Points

Start here when exploring this area:

- **`test_returns_ollama_response`** (Function) — `tests/unit/components/test_mode_runner.py:131`
- **`test_ollama_called_with_correct_model`** (Function) — `tests/unit/components/test_mode_runner.py:140`
- **`test_system_message_included_when_provided`** (Function) — `tests/unit/components/test_mode_runner.py:152`
- **`test_no_system_message_when_not_provided`** (Function) — `tests/unit/components/test_mode_runner.py:167`
- **`test_falls_back_to_tier2_on_ollama_error`** (Function) — `tests/unit/components/test_mode_runner.py:188`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `Neo4jComponent` | Class | `src/components/neo4j_component.py` | 49 |
| `GameplayLoopComponent` | Class | `src/components/gameplay_loop_component.py` | 26 |
| `AppComponent` | Class | `src/components/app_component.py` | 49 |
| `Component` | Class | `src/orchestration/component.py` | 60 |
| `PlayerExperienceComponent` | Class | `src/components/player_experience_component.py` | 53 |
| `LLMComponent` | Class | `src/components/llm_component.py` | 52 |
| `DockerComponent` | Class | `src/components/docker_component.py` | 60 |
| `test_returns_ollama_response` | Function | `tests/unit/components/test_mode_runner.py` | 131 |
| `test_ollama_called_with_correct_model` | Function | `tests/unit/components/test_mode_runner.py` | 140 |
| `test_system_message_included_when_provided` | Function | `tests/unit/components/test_mode_runner.py` | 152 |
| `test_no_system_message_when_not_provided` | Function | `tests/unit/components/test_mode_runner.py` | 167 |
| `test_falls_back_to_tier2_on_ollama_error` | Function | `tests/unit/components/test_mode_runner.py` | 188 |
| `client_factory` | Function | `tests/unit/components/test_mode_runner.py` | 195 |
| `test_extraction_skips_null_tier1_and_calls_tier2` | Function | `tests/unit/components/test_mode_runner.py` | 212 |
| `test_tier2_called_with_correct_model` | Function | `tests/unit/components/test_mode_runner.py` | 224 |
| `test_falls_back_to_tier3_when_tier2_fails` | Function | `tests/unit/components/test_mode_runner.py` | 258 |
| `test_tier_override_1_calls_ollama` | Function | `tests/unit/components/test_mode_runner.py` | 319 |
| `test_tier_override_2_calls_openrouter` | Function | `tests/unit/components/test_mode_runner.py` | 328 |
| `test_tier_override_skips_other_tiers` | Function | `tests/unit/components/test_mode_runner.py` | 337 |
| `test_ollama_503_falls_back_to_tier2` | Function | `tests/unit/components/test_mode_runner.py` | 376 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Session_turn → Build_voice_fragment` | cross_community | 5 |
| `Session_turn → Build_intervention_fragment` | cross_community | 5 |
| `Session_turn → _minimal_world_context` | cross_community | 4 |
| `Session_turn → _build_user_message` | cross_community | 4 |
| `Ensure_consistency → _get_env_var_default` | intra_community | 4 |
| `Respond_to_genesis → Transition_to` | cross_community | 3 |
| `Respond_to_genesis → Record_turn` | cross_community | 3 |
| `Start_genesis_session → Transition_to` | cross_community | 3 |
| `Start_genesis_session → Record_turn` | cross_community | 3 |
| `Ensure_consistency → _create_env_example` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Agent_orchestration | 10 calls |
| Orchestration | 4 calls |
| Guide | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_returns_ollama_response"})` — see callers and callees
2. `gitnexus_query({query: "components"})` — find related execution flows
3. Read key files listed above for implementation details
