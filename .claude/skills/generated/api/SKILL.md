---
name: api
description: "Skill for the Api area of TTA. 65 symbols across 19 files."
---

# Api

65 symbols | 19 files | Cohesion: 80%

## When to Use

- Working with code in `src/`
- Understanding how test_session_manager, run_diagnostics, create_session work
- Modifying api-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/player_experience/api/session_manager.py` | _session_key, _user_sessions_key, create_session, get_session, delete_session (+5) |
| `src/agent_orchestration/api/diagnostics.py` | _get_agents_diagnostics, _get_agent_diagnostics, _build_agent_diagnostic_info, _get_performance_metrics, _build_health_status (+2) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/api/diagnostics.py` | _get_agents_diagnostics, _get_agent_diagnostics, _build_agent_diagnostic_info, _get_performance_metrics, _build_health_status (+2) |
| `src/player_experience/api/test_sentry_integration.py` | test_sentry_configuration, test_error_capture, test_data_filtering, main, test_message_capture |
| `tests/unit/player_experience/api/test_websocket_chat_interactive.py` | _auth_token, _recv_json, _recv_assistant, test_interactive_buttons_suggested_on_anxiety, test_guided_exercise_flow_records_progress |
| `src/player_experience/api/sentry_config.py` | init_sentry, capture_therapeutic_error, _sanitize_therapeutic_content, capture_therapeutic_message |
| `src/player_experience/api/auth.py` | create_access_token, create_refresh_token, create_tokens_for_player, refresh_access_token |
| `src/player_experience/api/config.py` | get_settings, APISettings, DevelopmentSettings |
| `src/player_experience/api/app.py` | lifespan, _session_cleanup_loop, create_app |
| `src/player_experience/api/routers/openrouter_auth.py` | create_session, validate_api_key, oauth_callback |

## Entry Points

Start here when exploring this area:

- **`test_session_manager`** (Function) — `scripts/diagnose_agents.py:212`
- **`run_diagnostics`** (Function) — `scripts/diagnose_agents.py:262`
- **`create_session`** (Function) — `src/player_experience/api/session_manager.py:135`
- **`get_session`** (Function) — `src/player_experience/api/session_manager.py:180`
- **`delete_session`** (Function) — `src/player_experience/api/session_manager.py:218`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `APISettings` | Class | `src/player_experience/api/config.py` | 14 |
| `DevelopmentSettings` | Class | `src/player_experience/api/config.py` | 120 |
| `test_session_manager` | Function | `scripts/diagnose_agents.py` | 212 |
| `run_diagnostics` | Function | `scripts/diagnose_agents.py` | 262 |
| `create_session` | Function | `src/player_experience/api/session_manager.py` | 135 |
| `get_session` | Function | `src/player_experience/api/session_manager.py` | 180 |
| `delete_session` | Function | `src/player_experience/api/session_manager.py` | 218 |
| `get_user_sessions` | Function | `src/player_experience/api/session_manager.py` | 241 |
| `delete_user_sessions` | Function | `src/player_experience/api/session_manager.py` | 255 |
| `test_sentry_configuration` | Function | `src/player_experience/api/test_sentry_integration.py` | 25 |
| `init_sentry` | Function | `src/player_experience/api/sentry_config.py` | 23 |
| `run_server` | Function | `src/player_experience/api/main.py` | 14 |
| `get_settings` | Function | `src/player_experience/api/config.py` | 188 |
| `lifespan` | Function | `src/player_experience/api/app.py` | 127 |
| `test_async_functionality` | Function | `tests/unit/player_experience/api/test_api_integration.py` | 143 |
| `get_oauth_state` | Function | `src/player_experience/api/session_manager.py` | 302 |
| `delete_oauth_state` | Function | `src/player_experience/api/session_manager.py` | 334 |
| `create_session` | Function | `src/player_experience/api/routers/openrouter_auth.py` | 170 |
| `validate_api_key` | Function | `src/player_experience/api/routers/openrouter_auth.py` | 182 |
| `oauth_callback` | Function | `src/player_experience/api/routers/openrouter_auth.py` | 266 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_user_info → _user_sessions_key` | cross_community | 4 |
| `Get_user_info → _session_key` | cross_community | 4 |
| `Oauth_callback → _oauth_state_key` | intra_community | 4 |
| `Oauth_callback → _session_key` | cross_community | 4 |
| `Oauth_callback → To_dict` | cross_community | 4 |
| `Oauth_callback → _user_sessions_key` | cross_community | 4 |
| `Logout → _session_key` | cross_community | 4 |
| `Logout → From_dict` | cross_community | 4 |
| `Auth_status → _user_sessions_key` | cross_community | 4 |
| `Auth_status → _session_key` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Cluster_358 | 3 calls |
| Routers | 2 calls |
| Monitoring | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_session_manager"})` — see callers and callees
2. `gitnexus_query({query: "api"})` — find related execution flows
3. Read key files listed above for implementation details
