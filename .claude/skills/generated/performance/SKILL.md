---
name: performance
description: "Skill for the Performance area of TTA. 74 symbols across 11 files."
---

# Performance

74 symbols | 11 files | Cohesion: 87%

## When to Use

- Working with code in `packages/`
- Understanding how get_response_time_monitor, get_response_time_monitor, run_standard_load_test work
- Modifying performance-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | start, schedule_workflow, _reserve_agents, _scheduler_loop, _profile_update_loop (+8) |
| `src/agent_orchestration/performance/optimization.py` | start, schedule_workflow, _reserve_agents, _scheduler_loop, _profile_update_loop (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | get_statistics, _calculate_statistics, _percentile, get_performance_summary, get_response_time_monitor (+5) |
| `src/agent_orchestration/performance/response_time_monitor.py` | get_statistics, _calculate_statistics, _percentile, get_performance_summary, get_response_time_monitor (+5) |
| `tests/performance/load_test_suite.py` | initialize, run_load_test, _generate_test_report, run_standard_load_test, run_stress_test (+5) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/alerting.py` | start, _escalation_loop, _check_escalation, evaluate_thresholds, _process_alert |
| `src/agent_orchestration/performance/alerting.py` | start, _escalation_loop, _check_escalation, evaluate_thresholds, _process_alert |
| `packages/tta-ai-framework/src/tta_ai/orchestration/performance/analytics.py` | analyze_performance, _identify_bottlenecks, _analyze_trends |
| `src/agent_orchestration/performance/analytics.py` | analyze_performance, _identify_bottlenecks, _analyze_trends |
| `packages/tta-ai-framework/src/tta_ai/orchestration/api/diagnostics.py` | _get_performance_metrics |

## Entry Points

Start here when exploring this area:

- **`get_response_time_monitor`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py:500`
- **`get_response_time_monitor`** (Function) — `src/agent_orchestration/performance/response_time_monitor.py:514`
- **`run_standard_load_test`** (Function) — `tests/performance/load_test_suite.py:623`
- **`run_stress_test`** (Function) — `tests/performance/load_test_suite.py:635`
- **`get_statistics`** (Method) — `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py:272`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_response_time_monitor` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 500 |
| `get_response_time_monitor` | Function | `src/agent_orchestration/performance/response_time_monitor.py` | 514 |
| `run_standard_load_test` | Function | `tests/performance/load_test_suite.py` | 623 |
| `run_stress_test` | Function | `tests/performance/load_test_suite.py` | 635 |
| `get_statistics` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 272 |
| `get_performance_summary` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 447 |
| `get_statistics` | Method | `src/agent_orchestration/performance/response_time_monitor.py` | 274 |
| `get_performance_summary` | Method | `src/agent_orchestration/performance/response_time_monitor.py` | 460 |
| `start` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 147 |
| `schedule_workflow` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 193 |
| `start` | Method | `src/agent_orchestration/performance/optimization.py` | 147 |
| `schedule_workflow` | Method | `src/agent_orchestration/performance/optimization.py` | 195 |
| `initialize` | Method | `tests/performance/load_test_suite.py` | 63 |
| `run_load_test` | Method | `tests/performance/load_test_suite.py` | 97 |
| `start` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/alerting.py` | 146 |
| `analyze_performance` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/analytics.py` | 117 |
| `get_optimization_statistics` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/optimization.py` | 502 |
| `start` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/performance/response_time_monitor.py` | 137 |
| `start` | Method | `src/agent_orchestration/performance/alerting.py` | 148 |
| `analyze_performance` | Method | `src/agent_orchestration/performance/analytics.py` | 117 |

## How to Explore

1. `context({name: "get_response_time_monitor"})` — see callers and callees
2. `query({search_query: "performance"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
