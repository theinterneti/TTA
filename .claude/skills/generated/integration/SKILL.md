---
name: integration
description: "Skill for the Integration area of TTA. 61 symbols across 9 files."
---

# Integration

61 symbols | 9 files | Cohesion: 85%

## When to Use

- Working with code in `src/`
- Understanding how sid, pid, test_create_and_get_session work
- Modifying integration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/integration/test_persistence_integration.py` | sid, pid, test_create_and_get_session, test_list_sessions_for_player, test_list_sessions_message_count (+11) |
| `src/player_experience/database/dolt_session_store.py` | _ping, _connect, _now, create_session, get_session (+6) |
| `src/integration/gameplay_loop_integration.py` | _enrich_session_status, _build_therapeutic_settings, _build_narrative_session_payload, process_validated_choice, pause_session_with_auth (+5) |
| `src/player_experience/franchise_worlds/integration/TTAIntegration.ts` | convertToWorldDetails, mapDifficultyLevel, calculateTherapeuticReadiness, createWorldParameters, calculateTherapeuticIntensity (+4) |
| `src/player_experience/franchise_worlds/integration/PlayerExperienceIntegration.py` | get_franchise_worlds, convert_franchise_world_to_tta, register_franchise_worlds_with_tta, create_customized_world_parameters, _run_node_script (+2) |
| `src/player_experience/database/redis_cache.py` | _key, get, set, delete |
| `src/player_experience/api/routers/franchise_worlds.py` | list_franchise_worlds, get_franchise_world_stats |
| `src/player_experience/api/auth.py` | verify_token |
| `src/player_experience/franchise_worlds/examples/FranchiseWorldDemo.ts` | demoWorldListing |

## Entry Points

Start here when exploring this area:

- **`sid`** (Function) — `tests/integration/test_persistence_integration.py:21`
- **`pid`** (Function) — `tests/integration/test_persistence_integration.py:25`
- **`test_create_and_get_session`** (Function) — `tests/integration/test_persistence_integration.py:43`
- **`test_list_sessions_for_player`** (Function) — `tests/integration/test_persistence_integration.py:57`
- **`test_list_sessions_message_count`** (Function) — `tests/integration/test_persistence_integration.py:66`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `sid` | Function | `tests/integration/test_persistence_integration.py` | 21 |
| `pid` | Function | `tests/integration/test_persistence_integration.py` | 25 |
| `test_create_and_get_session` | Function | `tests/integration/test_persistence_integration.py` | 43 |
| `test_list_sessions_for_player` | Function | `tests/integration/test_persistence_integration.py` | 57 |
| `test_list_sessions_message_count` | Function | `tests/integration/test_persistence_integration.py` | 66 |
| `test_save_and_load_messages` | Function | `tests/integration/test_persistence_integration.py` | 75 |
| `test_load_messages_full_includes_metadata` | Function | `tests/integration/test_persistence_integration.py` | 86 |
| `test_clear_messages` | Function | `tests/integration/test_persistence_integration.py` | 95 |
| `test_session_metadata_preserved_after_clear` | Function | `tests/integration/test_persistence_integration.py` | 105 |
| `test_copy_session` | Function | `tests/integration/test_persistence_integration.py` | 115 |
| `test_copy_session_is_independent` | Function | `tests/integration/test_persistence_integration.py` | 133 |
| `test_copy_accepts_explicit_new_id` | Function | `tests/integration/test_persistence_integration.py` | 149 |
| `create_session` | Function | `src/player_experience/database/dolt_session_store.py` | 88 |
| `get_session` | Function | `src/player_experience/database/dolt_session_store.py` | 138 |
| `list_sessions` | Function | `src/player_experience/database/dolt_session_store.py` | 155 |
| `save_message` | Function | `src/player_experience/database/dolt_session_store.py` | 179 |
| `load_messages` | Function | `src/player_experience/database/dolt_session_store.py` | 213 |
| `load_messages_full` | Function | `src/player_experience/database/dolt_session_store.py` | 230 |
| `clear_messages` | Function | `src/player_experience/database/dolt_session_store.py` | 248 |
| `copy_session` | Function | `src/player_experience/database/dolt_session_store.py` | 273 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_current_player → _key` | cross_community | 5 |

## How to Explore

1. `gitnexus_context({name: "sid"})` — see callers and callees
2. `gitnexus_query({query: "integration"})` — find related execution flows
3. Read key files listed above for implementation details
