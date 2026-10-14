---
name: api
description: "Skill for the Api area of TTA. 77 symbols across 26 files."
---

# Api

77 symbols | 26 files | Cohesion: 69%

## When to Use

- Working with code in `src/`
- Understanding how test_session_manager, run_diagnostics, create_app work
- Modifying api-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/player_experience/api/test_end_to_end_workflows.py` | receive_message_with_role, test_complete_new_user_journey, test_network_interruption_recovery, create_auth_token, create_user_connection (+4) |
| `src/player_experience/api/session_manager.py` | to_dict, _session_key, _user_sessions_key, create_session, get_session (+3) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/api/diagnostics.py` | _get_agents_diagnostics, _get_agent_diagnostics, _build_agent_diagnostic_info, _build_health_status, _get_system_summary (+1) |
| `src/agent_orchestration/api/diagnostics.py` | _get_agents_diagnostics, _get_agent_diagnostics, _build_agent_diagnostic_info, _build_health_status, _get_system_summary (+1) |
| `src/player_experience/api/auth.py` | create_access_token, create_refresh_token, create_tokens_for_player, refresh_access_token, _get_token_cache |
| `tests/unit/player_experience/api/test_websocket_chat_interactive.py` | _auth_token, _recv_json, _recv_assistant, test_interactive_buttons_suggested_on_anxiety, test_guided_exercise_flow_records_progress |
| `src/player_experience/api/test_sentry_integration.py` | test_sentry_configuration, test_error_capture, test_data_filtering, main, test_message_capture |
| `src/player_experience/api/sentry_config.py` | init_sentry, capture_therapeutic_error, _sanitize_therapeutic_content, capture_therapeutic_message |
| `src/player_experience/api/app.py` | create_app, _session_cleanup_loop, lifespan |
| `src/player_experience/api/config.py` | APISettings, DevelopmentSettings, get_settings |

## Entry Points

Start here when exploring this area:

- **`test_session_manager`** (Function) — `scripts/diagnose_agents.py:212`
- **`run_diagnostics`** (Function) — `scripts/diagnose_agents.py:262`
- **`create_app`** (Function) — `src/player_experience/api/app.py:150`
- **`test_metrics_endpoint_hidden_in_production`** (Function) — `tests/unit/player_experience/api/test_metrics_endpoint.py:39`
- **`create_access_token`** (Function) — `src/player_experience/api/auth.py:130`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `APISettings` | Class | `src/player_experience/api/config.py` | 14 |
| `DevelopmentSettings` | Class | `src/player_experience/api/config.py` | 120 |
| `test_session_manager` | Function | `scripts/diagnose_agents.py` | 212 |
| `run_diagnostics` | Function | `scripts/diagnose_agents.py` | 262 |
| `create_app` | Function | `src/player_experience/api/app.py` | 150 |
| `test_metrics_endpoint_hidden_in_production` | Function | `tests/unit/player_experience/api/test_metrics_endpoint.py` | 39 |
| `create_access_token` | Function | `src/player_experience/api/auth.py` | 130 |
| `create_refresh_token` | Function | `src/player_experience/api/auth.py` | 154 |
| `create_tokens_for_player` | Function | `src/player_experience/api/auth.py` | 205 |
| `test_interactive_buttons_suggested_on_anxiety` | Function | `tests/unit/player_experience/api/test_websocket_chat_interactive.py` | 48 |
| `test_guided_exercise_flow_records_progress` | Function | `tests/unit/player_experience/api/test_websocket_chat_interactive.py` | 70 |
| `lifespan` | Function | `src/player_experience/api/app.py` | 127 |
| `init_sentry` | Function | `src/player_experience/api/sentry_config.py` | 23 |
| `test_sentry_configuration` | Function | `src/player_experience/api/test_sentry_integration.py` | 25 |
| `test_async_functionality` | Function | `tests/unit/player_experience/api/test_api_integration.py` | 143 |
| `get_performance_monitor` | Function | `src/player_experience/monitoring/performance_monitor.py` | 744 |
| `get_security_validator` | Function | `src/player_experience/security/input_validator.py` | 737 |
| `reset_metrics` | Function | `src/player_experience/api/routers/chat.py` | 63 |
| `test_typing_events_emitted_when_opt_in` | Function | `tests/unit/player_experience/api/test_websocket_chat_typing_and_metrics.py` | 36 |
| `test_metrics_incremented` | Function | `tests/unit/player_experience/api/test_websocket_chat_typing_and_metrics.py` | 60 |

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
| Monitoring | 6 calls |
| Cluster_1224 | 3 calls |
| Player_experience | 2 calls |
| Performance | 2 calls |
| Security | 1 calls |
| Routers | 1 calls |
| Database | 1 calls |

## How to Explore

1. `context({name: "test_session_manager"})` — see callers and callees
2. `query({search_query: "api"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
