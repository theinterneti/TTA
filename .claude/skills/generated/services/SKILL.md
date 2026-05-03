---
name: services
description: "Skill for the Services area of TTA. 242 symbols across 41 files."
---

# Services

242 symbols | 41 files | Cohesion: 82%

## When to Use

- Working with code in `src/`
- Understanding how test_returns_true_for_compatible_model, test_rejects_model_exceeding_cost, test_rejects_model_below_quality work
- Modifying services-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/model_management/services/test_model_selector_additional.py` | _make_model, _make_requirements, test_returns_true_for_compatible_model, test_rejects_model_exceeding_cost, test_rejects_model_below_quality (+15) |
| `src/player_experience/frontend/src/services/progressTrackingService.ts` | analyzeGoalProgress, calculateProgressTrend, calculateVelocityScore, calculateConsistencyScore, calculateTherapeuticEffectiveness (+14) |
| `src/player_experience/frontend/src/services/personalizedRecommendationEngine.ts` | generatePersonalizedRecommendations, generateGoalRecommendations, generateApproachRecommendations, generateIntegrationRecommendations, analyzePersonalizationProfile (+14) |
| `tests/unit/model_management/services/test_model_selector_timeout.py` | _make_model, _make_requirements, test_execute_calls_run_selection, test_returns_model_on_success, test_timeout_value_from_criteria (+8) |
| `src/player_experience/frontend/src/services/websocket.ts` | validateConnectionPrerequisites, isConnected, getConnectionStatus, handleVisibilityChange, initializeVisibilityListener (+8) |
| `src/player_experience/services/privacy_service.py` | decrypt_therapeutic_content, delete_user_data, anonymize_user_data, _delete_therapeutic_content, _get_user_therapeutic_content (+7) |
| `src/player_experience/frontend/src/services/realAnalyticsService.ts` | setAuthToken, getSessionHistory, getRecommendationHistory, fetchApi, generatePredictiveAnalytics (+6) |
| `tests/player_experience/services/test_narrative_session_enrichment.py` | _make_orchestrator, test_sessions_without_session_id_are_passed_through, test_stable_coherence_is_counted_and_attached, test_strained_coherence_is_counted, test_unknown_coherence_status_not_counted (+5) |
| `src/player_experience/services/session_store.py` | _connect, _now, create_session, _touch_session, save_message (+5) |
| `src/player_experience/frontend/src/services/predictiveAnalyticsService.ts` | generatePredictiveAnalytics, generateRiskPredictions, analyzePlateauRisk, generateOutcomePredictions, predictGoalOutcome (+5) |

## Entry Points

Start here when exploring this area:

- **`test_returns_true_for_compatible_model`** (Function) — `tests/unit/model_management/services/test_model_selector_additional.py:89`
- **`test_rejects_model_exceeding_cost`** (Function) — `tests/unit/model_management/services/test_model_selector_additional.py:96`
- **`test_rejects_model_below_quality`** (Function) — `tests/unit/model_management/services/test_model_selector_additional.py:103`
- **`test_rejects_model_with_insufficient_context`** (Function) — `tests/unit/model_management/services/test_model_selector_additional.py:110`
- **`test_rejects_model_missing_capabilities`** (Function) — `tests/unit/model_management/services/test_model_selector_additional.py:117`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_returns_true_for_compatible_model` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 89 |
| `test_rejects_model_exceeding_cost` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 96 |
| `test_rejects_model_below_quality` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 103 |
| `test_rejects_model_with_insufficient_context` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 110 |
| `test_rejects_model_missing_capabilities` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 117 |
| `test_accepts_model_with_all_required_capabilities` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 124 |
| `test_therapeutic_safety_unknown_score_openrouter_allowed` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 131 |
| `test_therapeutic_safety_unknown_score_custom_api_allowed` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 141 |
| `test_therapeutic_safety_unknown_score_local_rejected` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 151 |
| `test_therapeutic_safety_below_threshold_rejected` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 161 |
| `test_latency_constraint_rejects_slow_model` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 174 |
| `test_latency_constraint_accepts_fast_model` | Function | `tests/unit/model_management/services/test_model_selector_additional.py` | 182 |
| `test_sessions_without_session_id_are_passed_through` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 40 |
| `test_stable_coherence_is_counted_and_attached` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 65 |
| `test_strained_coherence_is_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 94 |
| `test_unknown_coherence_status_not_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 118 |
| `test_orchestrator_error_is_handled_gracefully` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 139 |
| `test_empty_state_does_not_add_narrative_orchestration` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 163 |
| `test_non_dict_state_does_not_add_narrative_orchestration` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 184 |
| `test_non_dict_player_signals_not_counted` | Function | `tests/player_experience/services/test_narrative_session_enrichment.py` | 205 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Chat → ClearToken` | cross_community | 8 |
| `Chat → StopHeartbeat` | cross_community | 8 |
| `Send_gameplay_message → _get_chat_openai` | cross_community | 7 |
| `Chat → FlushMessageQueue` | cross_community | 7 |
| `Send_gameplay_message → _auto_detect_provider` | cross_community | 6 |
| `GeneratePredictiveAnalytics → CalculateVariance` | cross_community | 5 |
| `SessionManagementInterface → CalculateOverallProgress` | cross_community | 5 |
| `GeneratePredictiveAnalytics → CalculateLinearRegression` | cross_community | 4 |
| `GeneratePredictiveAnalytics → CalculateCorrelation` | cross_community | 4 |
| `GeneratePredictiveAnalytics → ProjectOutcome` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Slices | 3 calls |
| Settings | 2 calls |
| Cluster_354 | 2 calls |
| Cluster_355 | 2 calls |
| PlayerPreferences | 1 calls |
| Cluster_1016 | 1 calls |
| Ai_components | 1 calls |
| Integration | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_returns_true_for_compatible_model"})` — see callers and callees
2. `gitnexus_query({query: "services"})` — find related execution flows
3. Read key files listed above for implementation details
