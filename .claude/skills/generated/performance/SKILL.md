---
name: performance
description: "Skill for the Performance area of TTA. 68 symbols across 9 files."
---

# Performance

68 symbols | 9 files | Cohesion: 90%

## When to Use

- Working with code in `src/`
- Understanding how start, get_statistics, start work
- Modifying performance-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/agent_orchestration/performance/optimization.py` | start, schedule_workflow, _reserve_agents, _scheduler_loop, _profile_update_loop (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | start, schedule_workflow, _reserve_agents, _scheduler_loop, _profile_update_loop (+8) |
| `tests/performance/load_test_suite.py` | initialize, run_load_test, _generate_test_report, run_standard_load_test, run_stress_test (+5) |
| `src/agent_orchestration/performance/response_time_monitor.py` | start, get_statistics, _calculate_statistics, _percentile, _analysis_loop (+3) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | start, get_statistics, _calculate_statistics, _percentile, _analysis_loop (+3) |
| `src/agent_orchestration/performance/alerting.py` | start, _escalation_loop, _check_escalation, evaluate_thresholds, _process_alert |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/alerting.py` | start, _escalation_loop, _check_escalation, evaluate_thresholds, _process_alert |
| `src/agent_orchestration/performance/analytics.py` | analyze_performance, _identify_bottlenecks, _analyze_trends |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/analytics.py` | analyze_performance, _identify_bottlenecks, _analyze_trends |

## Entry Points

Start here when exploring this area:

- **`start`** (Function) — `src/agent_orchestration/performance/response_time_monitor.py:139`
- **`get_statistics`** (Function) — `src/agent_orchestration/performance/response_time_monitor.py:274`
- **`start`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py:137`
- **`get_statistics`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py:272`
- **`initialize`** (Function) — `tests/performance/load_test_suite.py:63`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `start` | Function | `src/agent_orchestration/performance/response_time_monitor.py` | 139 |
| `get_statistics` | Function | `src/agent_orchestration/performance/response_time_monitor.py` | 274 |
| `start` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 137 |
| `get_statistics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 272 |
| `initialize` | Function | `tests/performance/load_test_suite.py` | 63 |
| `run_load_test` | Function | `tests/performance/load_test_suite.py` | 97 |
| `run_standard_load_test` | Function | `tests/performance/load_test_suite.py` | 623 |
| `run_stress_test` | Function | `tests/performance/load_test_suite.py` | 635 |
| `start` | Function | `src/agent_orchestration/performance/optimization.py` | 147 |
| `schedule_workflow` | Function | `src/agent_orchestration/performance/optimization.py` | 195 |
| `start` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 147 |
| `schedule_workflow` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 193 |
| `get_optimization_statistics` | Function | `src/agent_orchestration/performance/optimization.py` | 526 |
| `analyze_performance` | Function | `src/agent_orchestration/performance/analytics.py` | 117 |
| `start` | Function | `src/agent_orchestration/performance/alerting.py` | 148 |
| `get_optimization_statistics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 502 |
| `analyze_performance` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/analytics.py` | 117 |
| `start` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/alerting.py` | 146 |
| `track_operation` | Function | `src/agent_orchestration/performance/response_time_monitor.py` | 170 |
| `evaluate_thresholds` | Function | `src/agent_orchestration/performance/alerting.py` | 177 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Analyze_performance → _check_agent_overload` | intra_community | 3 |
| `Analyze_performance → _check_workflow_congestion` | intra_community | 3 |
| `Analyze_performance → _check_database_latency` | intra_community | 3 |
| `Analyze_performance → _check_resource_contention` | intra_community | 3 |
| `Analyze_performance → _calculate_trend` | intra_community | 3 |
| `Analyze_performance → _check_agent_overload` | intra_community | 3 |
| `Analyze_performance → _check_workflow_congestion` | intra_community | 3 |
| `Analyze_performance → _check_database_latency` | intra_community | 3 |
| `Analyze_performance → _check_resource_contention` | intra_community | 3 |
| `Analyze_performance → _calculate_trend` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "start"})` — see callers and callees
2. `gitnexus_query({query: "performance"})` — find related execution flows
3. Read key files listed above for implementation details
