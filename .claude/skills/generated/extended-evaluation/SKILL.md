---
name: extended-evaluation
description: "Skill for the Extended_evaluation area of TTA. 75 symbols across 14 files."
---

# Extended_evaluation

75 symbols | 14 files | Cohesion: 94%

## When to Use

- Working with code in `testing/`
- Understanding how example_data_analysis, main, run_comprehensive_evaluation work
- Modifying extended_evaluation-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `testing/extended_evaluation/extended_session_framework.py` | run_extended_evaluation, run_extended_session, _run_extended_session_tests, _run_single_extended_test, run_ultra_extended_session (+10) |
| `testing/extended_evaluation/performance_optimization.py` | set, _evict_lru, _remove_entry, start_optimization, _performance_monitoring_loop (+5) |
| `testing/extended_evaluation/living_worlds_metrics.py` | evaluate_world_consistency, _evaluate_snapshot_consistency, _evaluate_character_consistency, _evaluate_location_consistency, _evaluate_object_consistency (+2) |
| `testing/extended_evaluation/analysis_reporting.py` | load_evaluation_data, generate_comprehensive_report, generate_visualizations, _analyze_model_performance, _analyze_single_model (+1) |
| `testing/extended_evaluation/narrative_analysis.py` | evaluate_turn_coherence, _evaluate_character_coherence, _evaluate_plot_coherence, _evaluate_language_quality, _evaluate_consistency_with_history (+1) |
| `testing/extended_evaluation/data_collection.py` | start_session_collection, collect_turn_data, start_performance_monitoring, end_session_collection, _close_session_log_files (+1) |
| `testing/extended_evaluation/real_user_testing.py` | end_user_session, _schedule_data_cleanup, withdraw_participant_consent, __init__, _load_config |
| `testing/run_extended_evaluation.py` | run_comprehensive_evaluation, run_analysis_only, main, run_quick_sample |
| `testing/extended_evaluation/multi_model_comparison.py` | run_model_comparison, _perform_comparative_analysis, _perform_statistical_tests, _get_metric_scores |
| `testing/extended_evaluation/example_usage.py` | example_data_analysis, main, example_single_extended_test |

## Entry Points

Start here when exploring this area:

- **`example_data_analysis`** (Function) — `testing/extended_evaluation/example_usage.py:132`
- **`main`** (Function) — `testing/extended_evaluation/example_usage.py:230`
- **`run_comprehensive_evaluation`** (Function) — `testing/run_extended_evaluation.py:131`
- **`run_analysis_only`** (Function) — `testing/run_extended_evaluation.py:171`
- **`main`** (Function) — `testing/run_extended_evaluation.py:198`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `example_data_analysis` | Function | `testing/extended_evaluation/example_usage.py` | 132 |
| `main` | Function | `testing/extended_evaluation/example_usage.py` | 230 |
| `run_comprehensive_evaluation` | Function | `testing/run_extended_evaluation.py` | 131 |
| `run_analysis_only` | Function | `testing/run_extended_evaluation.py` | 171 |
| `main` | Function | `testing/run_extended_evaluation.py` | 198 |
| `example_single_extended_test` | Function | `testing/extended_evaluation/example_usage.py` | 35 |
| `run_quick_sample` | Function | `testing/run_extended_evaluation.py` | 84 |
| `run_quick_test` | Function | `testing/run_single_player_tests.py` | 80 |
| `load_evaluation_data` | Method | `testing/extended_evaluation/analysis_reporting.py` | 154 |
| `generate_comprehensive_report` | Method | `testing/extended_evaluation/analysis_reporting.py` | 207 |
| `generate_visualizations` | Method | `testing/extended_evaluation/analysis_reporting.py` | 672 |
| `run_extended_evaluation` | Method | `testing/extended_evaluation/extended_session_framework.py` | 491 |
| `run_extended_session` | Method | `testing/extended_evaluation/extended_session_framework.py` | 437 |
| `initialize_connections` | Method | `testing/single_player_test_framework.py` | 177 |
| `cleanup_connections` | Method | `testing/single_player_test_framework.py` | 196 |
| `evaluate_world_consistency` | Method | `testing/extended_evaluation/living_worlds_metrics.py` | 133 |
| `evaluate_turn_coherence` | Method | `testing/extended_evaluation/narrative_analysis.py` | 133 |
| `run_ultra_extended_session` | Method | `testing/extended_evaluation/extended_session_framework.py` | 592 |
| `run_model_comparison` | Method | `testing/extended_evaluation/multi_model_comparison.py` | 117 |
| `start_session_collection` | Method | `testing/extended_evaluation/data_collection.py` | 139 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Testing | 1 calls |

## How to Explore

1. `context({name: "example_data_analysis"})` — see callers and callees
2. `query({search_query: "extended_evaluation"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
