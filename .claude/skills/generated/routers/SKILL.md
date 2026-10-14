---
name: routers
description: "Skill for the Routers area of TTA. 141 symbols across 30 files."
---

# Routers

141 symbols | 30 files | Cohesion: 64%

## When to Use

- Working with code in `src/`
- Understanding how get_current_active_player, login, get_player_character_service_dep work
- Modifying routers-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/player_experience/api/routers/players.py` | get_player_manager_dep, convert_player_to_response, convert_request_to_therapeutic_preferences, convert_request_to_privacy_settings, create_player (+10) |
| `src/player_experience/api/routers/characters.py` | get_player_character_service_dep, create_player_character, _character_to_response, _schema_to_appearance, _schema_to_background (+7) |
| `src/player_experience/api/routers/auth.py` | login, get_current_authenticated_user, check_permission, check_mfa, get_player_manager (+5) |
| `src/player_experience/managers/player_profile_manager.py` | create_player_profile, get_player_profile, update_player_profile, delete_player_profile, update_therapeutic_preferences (+5) |
| `src/player_experience/api/routers/conversation.py` | clear_conversation, get_player_session_analytics, get_session_statistics, _load_conversation_from_redis, generate_response (+4) |
| `src/player_experience/api/routers/openrouter_auth.py` | create_session, validate_api_key, initiate_oauth, oauth_callback, get_session_manager (+4) |
| `src/player_experience/api/routers/settings.py` | get_player_settings, get_settings, update_privacy_settings, export_player_data, update_player_settings (+3) |
| `src/player_experience/api/routers/health.py` | get_redis_client, redis_health, startup_probe, get_neo4j_driver, neo4j_health (+2) |
| `src/player_experience/api/routers/gameplay.py` | get_gameplay_service, create_session, get_session_status, get_user_sessions, gameplay_health_check |
| `src/player_experience/api/routers/worlds.py` | get_world_manager_dep, get_world, check_world_compatibility, customize_world, list_worlds |

## Entry Points

Start here when exploring this area:

- **`get_current_active_player`** (Function) — `src/player_experience/api/auth.py:277`
- **`login`** (Function) — `src/player_experience/api/routers/auth.py:354`
- **`get_player_character_service_dep`** (Function) — `src/player_experience/api/routers/characters.py:900`
- **`create_player_character`** (Function) — `src/player_experience/api/routers/characters.py:915`
- **`clear_conversation`** (Function) — `src/player_experience/api/routers/conversation.py:931`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_current_active_player` | Function | `src/player_experience/api/auth.py` | 277 |
| `login` | Function | `src/player_experience/api/routers/auth.py` | 354 |
| `get_player_character_service_dep` | Function | `src/player_experience/api/routers/characters.py` | 900 |
| `create_player_character` | Function | `src/player_experience/api/routers/characters.py` | 915 |
| `clear_conversation` | Function | `src/player_experience/api/routers/conversation.py` | 931 |
| `get_player_session_analytics` | Function | `src/player_experience/api/routers/conversation.py` | 1187 |
| `get_session_statistics` | Function | `src/player_experience/api/routers/conversation.py` | 1250 |
| `get_player_manager_dep` | Function | `src/player_experience/api/routers/players.py` | 84 |
| `convert_player_to_response` | Function | `src/player_experience/api/routers/players.py` | 366 |
| `convert_request_to_therapeutic_preferences` | Function | `src/player_experience/api/routers/players.py` | 463 |
| `convert_request_to_privacy_settings` | Function | `src/player_experience/api/routers/players.py` | 490 |
| `create_player` | Function | `src/player_experience/api/routers/players.py` | 536 |
| `get_player` | Function | `src/player_experience/api/routers/players.py` | 639 |
| `update_player` | Function | `src/player_experience/api/routers/players.py` | 713 |
| `delete_player` | Function | `src/player_experience/api/routers/players.py` | 826 |
| `export_player_data` | Function | `src/player_experience/api/routers/players.py` | 936 |
| `update_therapeutic_preferences` | Function | `src/player_experience/api/routers/players.py` | 1008 |
| `update_privacy_settings` | Function | `src/player_experience/api/routers/players.py` | 1093 |
| `get_progress_service` | Function | `src/player_experience/api/routers/progress.py` | 27 |
| `get_player_progress_viz` | Function | `src/player_experience/api/routers/progress.py` | 34 |

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
| Managers | 12 calls |
| Api | 12 calls |
| Api_gateway | 9 calls |
| Services | 6 calls |
| Genesis | 5 calls |
| Cluster_495 | 4 calls |
| Components | 4 calls |
| Database | 3 calls |

## How to Explore

1. `context({name: "get_current_active_player"})` — see callers and callees
2. `query({search_query: "routers"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
