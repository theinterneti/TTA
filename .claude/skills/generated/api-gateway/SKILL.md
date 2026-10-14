---
name: api-gateway
description: "Skill for the Api_gateway area of TTA. 139 symbols across 8 files."
---

# Api_gateway

139 symbols | 8 files | Cohesion: 83%

## When to Use

- Working with code in `tests/`
- Understanding how test_empty_list_returns_200, test_returns_serialized_characters, test_no_player_id_in_token_returns_401 work
- Modifying api_gateway-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/api_gateway/test_auth_service.py` | _make_service, test_authenticate_demo_user_success, test_authenticate_demo_user_wrong_password_returns_none, test_authenticate_unknown_user_returns_none, test_authenticate_unknown_user_records_failed_attempt (+31) |
| `tests/unit/api_gateway/test_characters_router.py` | _make_character, _build_app, _mock_manager, test_empty_list_returns_200, test_returns_serialized_characters (+25) |
| `tests/unit/api_gateway/test_players_router.py` | _make_player, _build_app, _mock_manager, _mock_experience_manager, test_returns_200_with_message (+21) |
| `src/player_experience/services/auth_service.py` | authenticate_user, is_account_locked, record_failed_login, clear_failed_login_attempts, create_mfa_challenge (+10) |
| `tests/unit/api_gateway/test_sse_stream.py` | _drain, test_put_and_generate_single_token, test_event_ids_increment, test_multiple_tokens, test_crisis_signal_event (+8) |
| `tests/unit/api_gateway/test_worlds_router.py` | _build_app, test_empty_list_returns_200, test_character_id_filter_accepted, test_calls_manager_with_world_id, test_compatibility_check_failed_returns_400 (+7) |
| `src/api_gateway/sse/stream.py` | _next_event_id, put_token, put_crisis_signal, put_world_update, put_done (+1) |
| `src/api_gateway/endpoints/session_turn.py` | _run_pipeline |

## Entry Points

Start here when exploring this area:

- **`test_empty_list_returns_200`** (Method) — `tests/unit/api_gateway/test_characters_router.py:103`
- **`test_returns_serialized_characters`** (Method) — `tests/unit/api_gateway/test_characters_router.py:110`
- **`test_no_player_id_in_token_returns_401`** (Method) — `tests/unit/api_gateway/test_characters_router.py:124`
- **`test_manager_exception_returns_500`** (Method) — `tests/unit/api_gateway/test_characters_router.py:130`
- **`test_not_found_returns_404`** (Method) — `tests/unit/api_gateway/test_characters_router.py:145`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_empty_list_returns_200` | Method | `tests/unit/api_gateway/test_characters_router.py` | 103 |
| `test_returns_serialized_characters` | Method | `tests/unit/api_gateway/test_characters_router.py` | 110 |
| `test_no_player_id_in_token_returns_401` | Method | `tests/unit/api_gateway/test_characters_router.py` | 124 |
| `test_manager_exception_returns_500` | Method | `tests/unit/api_gateway/test_characters_router.py` | 130 |
| `test_not_found_returns_404` | Method | `tests/unit/api_gateway/test_characters_router.py` | 145 |
| `test_wrong_owner_returns_403` | Method | `tests/unit/api_gateway/test_characters_router.py` | 152 |
| `test_own_character_returns_200` | Method | `tests/unit/api_gateway/test_characters_router.py` | 161 |
| `test_exception_returns_500` | Method | `tests/unit/api_gateway/test_characters_router.py` | 171 |
| `test_character_limit_exceeded_returns_400` | Method | `tests/unit/api_gateway/test_characters_router.py` | 211 |
| `test_value_error_returns_400` | Method | `tests/unit/api_gateway/test_characters_router.py` | 222 |
| `test_unexpected_exception_returns_500` | Method | `tests/unit/api_gateway/test_characters_router.py` | 230 |
| `test_success_returns_201` | Method | `tests/unit/api_gateway/test_characters_router.py` | 238 |
| `test_no_player_id_in_token_returns_401` | Method | `tests/unit/api_gateway/test_characters_router.py` | 248 |
| `test_not_found_returns_404` | Method | `tests/unit/api_gateway/test_characters_router.py` | 261 |
| `test_wrong_owner_returns_403` | Method | `tests/unit/api_gateway/test_characters_router.py` | 269 |
| `test_character_not_found_error_from_update_returns_404` | Method | `tests/unit/api_gateway/test_characters_router.py` | 278 |
| `test_not_found_returns_404` | Method | `tests/unit/api_gateway/test_characters_router.py` | 295 |
| `test_wrong_owner_returns_403` | Method | `tests/unit/api_gateway/test_characters_router.py` | 303 |
| `test_success_returns_204` | Method | `tests/unit/api_gateway/test_characters_router.py` | 312 |
| `test_delete_returns_false_means_404` | Method | `tests/unit/api_gateway/test_characters_router.py` | 322 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Session_turn → _next_event_id` | cross_community | 4 |
| `Session_turn → _minimal_world_context` | cross_community | 4 |
| `Login → Is_account_locked` | cross_community | 3 |
| `Login → Log_security_event` | cross_community | 3 |
| `Login → _get_fallback_user_by_username` | cross_community | 3 |
| `Login → Record_failed_login` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Routers | 6 calls |
| Services | 2 calls |
| Components | 2 calls |
| Endpoints | 1 calls |
| Models | 1 calls |
| Agent_orchestration | 1 calls |
| Monitoring | 1 calls |

## How to Explore

1. `context({name: "test_empty_list_returns_200"})` — see callers and callees
2. `query({search_query: "api_gateway"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
