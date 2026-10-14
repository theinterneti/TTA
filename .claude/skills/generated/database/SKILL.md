---
name: database
description: "Skill for the Database area of TTA. 71 symbols across 15 files."
---

# Database

71 symbols | 15 files | Cohesion: 78%

## When to Use

- Working with code in `src/`
- Understanding how create_player_profile_repository, test_repository_crud_parametrized, get_current_player work
- Modifying database-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/player_experience/database/session_repository.py` | get_character_active_session, get_session_summaries, _get_player_sessions_from_memory, _deserialize_session_context, _get_character_sessions_from_neo4j (+13) |
| `src/player_experience/database/player_profile_repository.py` | connect, disconnect, get_player_profile, create_player_profile_repository, _serialize_therapeutic_preferences (+4) |
| `src/player_experience/database/character_repository.py` | _get_character_neo4j, get_characters_by_player, _get_characters_by_player_neo4j, _get_characters_by_player_memory, _deserialize_character (+2) |
| `src/player_experience/database/redis_cache.py` | _key, get, set, delete, _serialize_token_data (+1) |
| `src/components/gameplay_loop/database/dolt_manager.py` | _connect, _write, _update, _ensure_tables, close (+1) |
| `tests/integration/test_persistence_integration.py` | test_set_and_get, test_get_miss_returns_none, test_delete_invalidates_entry, test_zero_ttl_not_cached, test_serialize_round_trip |
| `src/player_experience/database/world_repository.py` | create_world, _create_world_memory, _get_world_neo4j, _deserialize_world, _get_all_worlds_neo4j |
| `src/components/gameplay_loop/database/schema.py` | get_node_constraints, get_indexes, initialize_schema |
| `src/player_experience/database/player_profile_schema.py` | create_player_profile_constraints, create_player_profile_indexes, setup_player_profile_schema |
| `src/components/gameplay_loop/database/migrations.py` | up, down |

## Entry Points

Start here when exploring this area:

- **`create_player_profile_repository`** (Function) — `src/player_experience/database/player_profile_repository.py:964`
- **`test_repository_crud_parametrized`** (Function) — `tests/integration/player_experience/test_player_profile_database_param.py:49`
- **`get_current_player`** (Function) — `src/player_experience/api/auth.py:232`
- **`test_schema_manager_setup_parametrized`** (Function) — `tests/integration/player_experience/test_player_profile_database_param.py:18`
- **`test_session_repository_redis_cache_roundtrip`** (Function) — `tests/integration/player_experience/test_session_repository_redis_integration.py:12`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `create_player_profile_repository` | Function | `src/player_experience/database/player_profile_repository.py` | 964 |
| `test_repository_crud_parametrized` | Function | `tests/integration/player_experience/test_player_profile_database_param.py` | 49 |
| `get_current_player` | Function | `src/player_experience/api/auth.py` | 232 |
| `test_schema_manager_setup_parametrized` | Function | `tests/integration/player_experience/test_player_profile_database_param.py` | 18 |
| `test_session_repository_redis_cache_roundtrip` | Function | `tests/integration/player_experience/test_session_repository_redis_integration.py` | 12 |
| `main` | Function | `scripts/seed_worlds.py` | 271 |
| `get` | Method | `src/player_experience/database/redis_cache.py` | 63 |
| `set` | Method | `src/player_experience/database/redis_cache.py` | 73 |
| `delete` | Method | `src/player_experience/database/redis_cache.py` | 82 |
| `test_set_and_get` | Method | `tests/integration/test_persistence_integration.py` | 177 |
| `test_get_miss_returns_none` | Method | `tests/integration/test_persistence_integration.py` | 185 |
| `test_delete_invalidates_entry` | Method | `tests/integration/test_persistence_integration.py` | 189 |
| `test_zero_ttl_not_cached` | Method | `tests/integration/test_persistence_integration.py` | 196 |
| `up` | Method | `src/components/gameplay_loop/database/migrations.py` | 39 |
| `down` | Method | `src/components/gameplay_loop/database/migrations.py` | 70 |
| `get_node_constraints` | Method | `src/components/gameplay_loop/database/schema.py` | 48 |
| `get_indexes` | Method | `src/components/gameplay_loop/database/schema.py` | 68 |
| `initialize_schema` | Method | `src/components/gameplay_loop/database/schema.py` | 145 |
| `get_characters_by_player` | Method | `src/player_experience/database/character_repository.py` | 246 |
| `connect` | Method | `src/player_experience/database/player_profile_repository.py` | 82 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Create_character → _key` | cross_community | 7 |
| `Update_character → _key` | cross_community | 7 |
| `Create_session → _key` | cross_community | 7 |
| `Get_character_therapeutic_profile → _key` | cross_community | 7 |
| `Get_player_dashboard → _key` | cross_community | 7 |
| `Update_character_therapeutic_profile → _key` | cross_community | 7 |
| `Send_message → _key` | cross_community | 7 |
| `Get_character → _key` | cross_community | 7 |
| `Delete_character → _key` | cross_community | 7 |
| `Get_player → _key` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Integration | 6 calls |
| Api | 1 calls |

## How to Explore

1. `context({name: "create_player_profile_repository"})` — see callers and callees
2. `query({search_query: "database"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
