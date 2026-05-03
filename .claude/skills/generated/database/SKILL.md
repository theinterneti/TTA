---
name: database
description: "Skill for the Database area of TTA. 55 symbols across 14 files."
---

# Database

55 symbols | 14 files | Cohesion: 78%

## When to Use

- Working with code in `src/`
- Understanding how test_serialize_round_trip, from_env, get_current_player work
- Modifying database-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/player_experience/database/session_repository.py` | get_character_active_session, get_session_summaries, _get_player_sessions_from_memory, _deserialize_session_context, _get_character_sessions_from_neo4j (+13) |
| `src/player_experience/database/character_repository.py` | _get_character_neo4j, get_characters_by_player, _get_characters_by_player_neo4j, _get_characters_by_player_memory, _deserialize_character (+2) |
| `src/components/gameplay_loop/database/dolt_manager.py` | _connect, _write, _update, _ensure_tables, close (+1) |
| `src/player_experience/database/world_repository.py` | create_world, _create_world_memory, _get_world_neo4j, _deserialize_world, _get_all_worlds_neo4j |
| `src/player_experience/database/redis_cache.py` | from_env, _serialize_token_data, _deserialize_token_data |
| `src/components/gameplay_loop/database/schema.py` | get_node_constraints, get_indexes, initialize_schema |
| `src/player_experience/database/player_profile_schema.py` | create_player_profile_constraints, create_player_profile_indexes, setup_player_profile_schema |
| `src/player_experience/api/auth.py` | _get_token_cache, get_current_player |
| `src/components/gameplay_loop/database/migrations.py` | up, down |
| `src/components/gameplay_loop/database/neo4j_manager.py` | get_session, _cache_session_state |

## Entry Points

Start here when exploring this area:

- **`test_serialize_round_trip`** (Function) — `tests/integration/test_persistence_integration.py:202`
- **`from_env`** (Function) — `src/player_experience/database/redis_cache.py:49`
- **`get_current_player`** (Function) — `src/player_experience/api/auth.py:232`
- **`get_character_active_session`** (Function) — `src/player_experience/database/session_repository.py:229`
- **`get_session_summaries`** (Function) — `src/player_experience/database/session_repository.py:262`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_serialize_round_trip` | Function | `tests/integration/test_persistence_integration.py` | 202 |
| `from_env` | Function | `src/player_experience/database/redis_cache.py` | 49 |
| `get_current_player` | Function | `src/player_experience/api/auth.py` | 232 |
| `get_character_active_session` | Function | `src/player_experience/database/session_repository.py` | 229 |
| `get_session_summaries` | Function | `src/player_experience/database/session_repository.py` | 262 |
| `get_characters_by_player` | Function | `src/player_experience/database/character_repository.py` | 246 |
| `get_node_constraints` | Function | `src/components/gameplay_loop/database/schema.py` | 48 |
| `get_indexes` | Function | `src/components/gameplay_loop/database/schema.py` | 68 |
| `initialize_schema` | Function | `src/components/gameplay_loop/database/schema.py` | 145 |
| `up` | Function | `src/components/gameplay_loop/database/migrations.py` | 39 |
| `down` | Function | `src/components/gameplay_loop/database/migrations.py` | 70 |
| `test_session_repository_redis_cache_roundtrip` | Function | `tests/integration/player_experience/test_session_repository_redis_integration.py` | 12 |
| `create_session` | Function | `src/player_experience/database/session_repository.py` | 44 |
| `test_schema_manager_setup_parametrized` | Function | `tests/integration/player_experience/test_player_profile_database_param.py` | 18 |
| `create_player_profile_constraints` | Function | `src/player_experience/database/player_profile_schema.py` | 196 |
| `create_player_profile_indexes` | Function | `src/player_experience/database/player_profile_schema.py` | 245 |
| `setup_player_profile_schema` | Function | `src/player_experience/database/player_profile_schema.py` | 302 |
| `get_player_active_sessions` | Function | `src/player_experience/database/session_repository.py` | 206 |
| `main` | Function | `scripts/seed_worlds.py` | 271 |
| `create_world` | Function | `src/player_experience/database/world_repository.py` | 70 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_current_player → _key` | cross_community | 5 |
| `Get_session_summaries → _deserialize_session_context` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Integration | 4 calls |

## How to Explore

1. `gitnexus_context({name: "test_serialize_round_trip"})` — see callers and callees
2. `gitnexus_query({query: "database"})` — find related execution flows
3. Read key files listed above for implementation details
