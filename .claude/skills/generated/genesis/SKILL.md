---
name: genesis
description: "Skill for the Genesis area of TTA. 81 symbols across 9 files."
---

# Genesis

81 symbols | 9 files | Cohesion: 72%

## When to Use

- Working with code in `tests/`
- Understanding how get_system_prompt, derive_guide_character, respond work
- Modifying genesis-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/genesis/test_genesis_agent.py` | _fresh_state, _make_router, _make_agent, test_returns_agent_response, test_records_turn_in_state (+21) |
| `tests/unit/genesis/test_first_scene_synthesis.py` | _make_service, test_synthesize_no_driver_returns_first_scene, test_synthesize_no_driver_npc_ids_empty, test_synthesize_no_driver_location_id_is_uuid, test_synthesize_raw_synthesis_preserved (+14) |
| `tests/unit/genesis/test_genesis_router.py` | test_roundtrip_minimal_state, test_roundtrip_with_turns, test_roundtrip_with_guide_character, test_roundtrip_without_guide_character, test_roundtrip_surprise_me_flag (+10) |
| `src/components/genesis/session_store.py` | _state_to_dict, _state_from_dict, _get_client, _make_key, save (+3) |
| `src/components/genesis/agent.py` | _is_surprise_request, _check_first_light_response, respond, _should_transition |
| `src/components/genesis/first_scene_synthesis.py` | synthesize, _call_llm, _build_messages |
| `src/components/genesis/seed_extractor.py` | extract, _validate_fields, generate_surprise_seed |
| `src/components/genesis/guide_generator.py` | _derive_structural, derive_guide_character |
| `src/components/genesis/narrator_voice.py` | get_system_prompt |

## Entry Points

Start here when exploring this area:

- **`get_system_prompt`** (Function) — `src/components/genesis/narrator_voice.py:213`
- **`derive_guide_character`** (Function) — `src/components/genesis/guide_generator.py:221`
- **`respond`** (Method) — `src/components/genesis/agent.py:362`
- **`test_returns_agent_response`** (Method) — `tests/unit/genesis/test_genesis_agent.py:338`
- **`test_records_turn_in_state`** (Method) — `tests/unit/genesis/test_genesis_agent.py:348`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_system_prompt` | Function | `src/components/genesis/narrator_voice.py` | 213 |
| `derive_guide_character` | Function | `src/components/genesis/guide_generator.py` | 221 |
| `respond` | Method | `src/components/genesis/agent.py` | 362 |
| `test_returns_agent_response` | Method | `tests/unit/genesis/test_genesis_agent.py` | 338 |
| `test_records_turn_in_state` | Method | `tests/unit/genesis/test_genesis_agent.py` | 348 |
| `test_merges_extracted_fields` | Method | `tests/unit/genesis/test_genesis_agent.py` | 357 |
| `test_act_advances_in_void` | Method | `tests/unit/genesis/test_genesis_agent.py` | 367 |
| `test_surprise_me_sets_flag` | Method | `tests/unit/genesis/test_genesis_agent.py` | 379 |
| `test_is_not_complete_before_session_begun` | Method | `tests/unit/genesis/test_genesis_agent.py` | 394 |
| `test_guide_character_generated_in_becoming` | Method | `tests/unit/genesis/test_genesis_agent.py` | 403 |
| `test_narrator_fallback_on_llm_failure` | Method | `tests/unit/genesis/test_genesis_agent.py` | 433 |
| `test_reset_clears_guide` | Method | `tests/unit/genesis/test_genesis_agent.py` | 447 |
| `synthesize` | Method | `src/components/genesis/first_scene_synthesis.py` | 202 |
| `test_synthesize_no_driver_returns_first_scene` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 265 |
| `test_synthesize_no_driver_npc_ids_empty` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 279 |
| `test_synthesize_no_driver_location_id_is_uuid` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 291 |
| `test_synthesize_raw_synthesis_preserved` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 308 |
| `test_synthesize_llm_fallback_on_error` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 320 |
| `test_synthesize_calls_neo4j_session` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 358 |
| `test_synthesize_creates_location_node` | Method | `tests/unit/genesis/test_first_scene_synthesis.py` | 372 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Respond_to_genesis → _make_key` | cross_community | 4 |
| `Respond_to_genesis → _get_client` | cross_community | 4 |
| `Respond_to_genesis → _state_from_dict` | cross_community | 4 |
| `Respond_to_genesis → Transition_to` | cross_community | 3 |
| `Respond_to_genesis → Record_turn` | cross_community | 3 |
| `Respond_to_genesis → _is_surprise_request` | cross_community | 3 |
| `Respond_to_genesis → _check_first_light_response` | cross_community | 3 |
| `Respond_to_genesis → _state_to_dict` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Components | 3 calls |
| Ai_components | 1 calls |

## How to Explore

1. `context({name: "get_system_prompt"})` — see callers and callees
2. `query({search_query: "genesis"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
