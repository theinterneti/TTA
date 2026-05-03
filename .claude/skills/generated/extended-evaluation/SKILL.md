---
name: extended-evaluation
description: "Skill for the Extended_evaluation area of TTA. 54 symbols across 11 files."
---

# Extended_evaluation

54 symbols | 11 files | Cohesion: 98%

## When to Use

- Working with code in `testing/`
- Understanding how run_comprehensive_evaluation, run_analysis_only, main work
- Modifying extended_evaluation-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `testing/extended_evaluation/performance_optimization.py` | set, _evict_lru, _remove_entry, start_optimization, _performance_monitoring_loop (+5) |
| `testing/extended_evaluation/living_worlds_metrics.py` | evaluate_world_consistency, _evaluate_snapshot_consistency, _evaluate_character_consistency, _evaluate_location_consistency, _evaluate_object_consistency (+2) |
| `testing/extended_evaluation/analysis_reporting.py` | load_evaluation_data, generate_comprehensive_report, generate_visualizations, _analyze_model_performance, _analyze_single_model (+1) |
| `testing/extended_evaluation/narrative_analysis.py` | evaluate_turn_coherence, _evaluate_character_coherence, _evaluate_plot_coherence, _evaluate_language_quality, _evaluate_consistency_with_history (+1) |
| `testing/extended_evaluation/data_collection.py` | start_session_collection, collect_turn_data, start_performance_monitoring, end_session_collection, _close_session_log_files (+1) |
| `testing/extended_evaluation/real_user_testing.py` | end_user_session, _schedule_data_cleanup, withdraw_participant_consent, __init__, _load_config |
| `testing/extended_evaluation/multi_model_comparison.py` | run_model_comparison, _perform_comparative_analysis, _perform_statistical_tests, _get_metric_scores |
| `testing/run_extended_evaluation.py` | run_comprehensive_evaluation, run_analysis_only, main |
| `testing/extended_evaluation/simulated_user_profiles.py` | generate_response, _fill_template, _add_creative_elements |
| `testing/extended_evaluation/example_usage.py` | example_data_analysis, main |

## Entry Points

Start here when exploring this area:

- **`run_comprehensive_evaluation`** (Function) — `testing/run_extended_evaluation.py:131`
- **`run_analysis_only`** (Function) — `testing/run_extended_evaluation.py:171`
- **`main`** (Function) — `testing/run_extended_evaluation.py:198`
- **`example_data_analysis`** (Function) — `testing/extended_evaluation/example_usage.py:132`
- **`main`** (Function) — `testing/extended_evaluation/example_usage.py:230`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `run_comprehensive_evaluation` | Function | `testing/run_extended_evaluation.py` | 131 |
| `run_analysis_only` | Function | `testing/run_extended_evaluation.py` | 171 |
| `main` | Function | `testing/run_extended_evaluation.py` | 198 |
| `example_data_analysis` | Function | `testing/extended_evaluation/example_usage.py` | 132 |
| `main` | Function | `testing/extended_evaluation/example_usage.py` | 230 |
| `load_evaluation_data` | Function | `testing/extended_evaluation/analysis_reporting.py` | 154 |
| `generate_comprehensive_report` | Function | `testing/extended_evaluation/analysis_reporting.py` | 207 |
| `generate_visualizations` | Function | `testing/extended_evaluation/analysis_reporting.py` | 672 |
| `evaluate_world_consistency` | Function | `testing/extended_evaluation/living_worlds_metrics.py` | 133 |
| `evaluate_turn_coherence` | Function | `testing/extended_evaluation/narrative_analysis.py` | 133 |
| `run_model_comparison` | Function | `testing/extended_evaluation/multi_model_comparison.py` | 117 |
| `generate_response` | Function | `testing/extended_evaluation/simulated_user_profiles.py` | 243 |
| `end_user_session` | Function | `testing/extended_evaluation/real_user_testing.py` | 414 |
| `withdraw_participant_consent` | Function | `testing/extended_evaluation/real_user_testing.py` | 473 |
| `set` | Function | `testing/extended_evaluation/performance_optimization.py` | 130 |
| `start_optimization` | Function | `testing/extended_evaluation/performance_optimization.py` | 475 |
| `start_session_collection` | Function | `testing/extended_evaluation/data_collection.py` | 139 |
| `collect_turn_data` | Function | `testing/extended_evaluation/data_collection.py` | 168 |
| `start_performance_monitoring` | Function | `testing/extended_evaluation/data_collection.py` | 322 |
| `end_session_collection` | Function | `testing/extended_evaluation/data_collection.py` | 296 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _analyze_quality_trend` | cross_community | 6 |
| `Main → _create_model_rankings` | cross_community | 5 |
| `Run_model_comparison → _get_metric_scores` | intra_community | 4 |
| `Main → _load_session_data` | intra_community | 4 |
| `Main → _organize_data_by_model_and_profile` | intra_community | 4 |
| `Main → _calculate_summary_statistics` | intra_community | 4 |
| `Main → _analyze_profile_performance` | intra_community | 4 |
| `Main → _generate_insights` | intra_community | 4 |
| `Main → _create_model_comparison_chart` | intra_community | 4 |
| `Main → _create_quality_trends_chart` | intra_community | 4 |

## How to Explore

1. `gitnexus_context({name: "run_comprehensive_evaluation"})` — see callers and callees
2. `gitnexus_query({query: "extended_evaluation"})` — find related execution flows
3. Read key files listed above for implementation details
