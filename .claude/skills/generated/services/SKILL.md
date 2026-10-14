---
name: services
description: "Skill for the Services area of TTA. 311 symbols across 46 files."
---

# Services

311 symbols | 46 files | Cohesion: 83%

## When to Use

- Working with code in `src/`
- Understanding how get_session_store, create_session, get_session_messages work
- Modifying services-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/model_management/services/test_services_additional.py` | _make_model, _make_requirements, test_get_fallback_model_returns_none_when_no_healthy_providers, test_get_fallback_model_excludes_failed_model_from_results, test_get_fallback_model_returns_none_when_all_filtered (+29) |
| `tests/unit/model_management/services/test_model_selector_additional.py` | _make_model, _make_requirements, test_returns_true_for_compatible_model, test_rejects_model_exceeding_cost, test_rejects_model_below_quality (+15) |
| `src/player_experience/frontend/src/services/personalizedRecommendationEngine.ts` | generateProgressRecommendations, createGoalRecommendation, createProgressBoostRecommendation, formatGoalTitle, generateGoalDescription (+15) |
| `src/player_experience/frontend/src/services/progressTrackingService.ts` | generateProgressAnalytics, recordProgress, recordOutcomeMeasurement, generateTherapeuticInsights, generateProgressRecommendations (+15) |
| `src/player_experience/frontend/src/services/websocket.ts` | setupEventListeners, startHeartbeat, stopHeartbeat, handleCrisisAlert, disconnect (+9) |
| `tests/unit/model_management/services/test_model_selector_timeout.py` | _make_model, _make_requirements, test_execute_calls_run_selection, test_returns_model_on_success, test_timeout_value_from_criteria (+8) |
| `src/components/model_management/services/performance_monitor.py` | record_metrics, get_model_performance, get_system_performance, _calculate_aggregated_stats, _percentile (+6) |
| `src/player_experience/frontend/src/services/realAnalyticsService.ts` | fetchApi, generatePredictiveAnalytics, getSessionHistory, getEmotionalHistory, getRecommendationHistory (+6) |
| `src/player_experience/services/session_store.py` | _connect, _now, create_session, get_session, _touch_session (+5) |
| `tests/player_experience/services/test_narrative_session_enrichment.py` | _make_orchestrator, test_sessions_without_session_id_are_passed_through, test_stable_coherence_is_counted_and_attached, test_strained_coherence_is_counted, test_unknown_coherence_status_not_counted (+5) |

## Entry Points

Start here when exploring this area:

- **`get_session_store`** (Function) — `src/player_experience/api/routers/sessions.py:30`
- **`create_session`** (Function) — `src/player_experience/api/routers/sessions.py:114`
- **`get_session_messages`** (Function) — `src/player_experience/api/routers/sessions.py:252`
- **`copy_session`** (Function) — `src/player_experience/api/routers/sessions.py:278`
- **`clear_session_messages`** (Function) — `src/player_experience/api/routers/sessions.py:304`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_session_store` | Function | `src/player_experience/api/routers/sessions.py` | 30 |
| `create_session` | Function | `src/player_experience/api/routers/sessions.py` | 114 |
| `get_session_messages` | Function | `src/player_experience/api/routers/sessions.py` | 252 |
| `copy_session` | Function | `src/player_experience/api/routers/sessions.py` | 278 |
| `clear_session_messages` | Function | `src/player_experience/api/routers/sessions.py` | 304 |
| `enrich_session_payloads` | Function | `src/player_experience/services/narrative_session_enrichment.py` | 17 |
| `test_sessions_without_session_id_are_passed_through` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 40 |
| `test_stable_coherence_is_counted_and_attached` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 65 |
| `test_strained_coherence_is_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 94 |
| `test_unknown_coherence_status_not_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 118 |
| `test_orchestrator_error_is_handled_gracefully` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 139 |
| `test_empty_state_does_not_add_narrative_orchestration` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 163 |
| `test_non_dict_state_does_not_add_narrative_orchestration` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 184 |
| `test_non_dict_player_signals_not_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 205 |
| `test_original_session_keys_are_preserved` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 263 |
| `process_choice` | Function | `src/player_experience/api/routers/gameplay.py` | 241 |
| `end_session` | Function | `src/player_experience/api/routers/gameplay.py` | 328 |
| `pause_session` | Function | `src/player_experience/api/routers/gameplay.py` | 407 |
| `resume_session` | Function | `src/player_experience/api/routers/gameplay.py` | 448 |
| `generateGoalSuggestions` | Function | `src/player_experience/frontend/src/services/goalSuggestionEngine.ts` | 200 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Create_session → _key` | cross_community | 7 |
| `Get_session_messages → _key` | cross_community | 7 |
| `Clear_session_messages → _key` | cross_community | 7 |
| `Send_gameplay_message → _get_chat_openai` | cross_community | 7 |
| `Send_gameplay_message → _auto_detect_provider` | cross_community | 6 |
| `List_sessions → _get_narrative_orchestrator` | cross_community | 5 |
| `GeneratePredictiveAnalytics → CalculateVariance` | cross_community | 5 |
| `Export_user_data → Decrypt_therapeutic_content` | cross_community | 5 |
| `Create_session → _deserialize_token_data` | cross_community | 4 |
| `Get_player_dashboard → _connect` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Routers | 15 calls |
| Api_gateway | 5 calls |
| Cluster_1225 | 2 calls |
| Cluster_1226 | 2 calls |
| Managers | 1 calls |
| Ai_components | 1 calls |
| Monitoring | 1 calls |
| Integration | 1 calls |

## How to Explore

1. `context({name: "get_session_store"})` — see callers and callees
2. `query({search_query: "services"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
