---
name: optimization
description: "Skill for the Optimization area of TTA. 50 symbols across 8 files."
---

# Optimization

50 symbols | 8 files | Cohesion: 80%

## When to Use

- Working with code in `src/`
- Understanding how request_workflow_resources, create, end_timing work
- Modifying optimization-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/agent_orchestration/optimization/performance_analytics.py` | start, _calculate_system_health, _analytics_loop, _effectiveness_analysis_loop, get_performance_dashboard (+5) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/performance_analytics.py` | start, _calculate_system_health, _analytics_loop, _effectiveness_analysis_loop, get_performance_dashboard (+5) |
| `src/agent_orchestration/optimization/workflow_resource_manager.py` | request_workflow_resources, _can_allocate_resources, _allocate_workflow_resources, _scheduling_loop, start (+2) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/workflow_resource_manager.py` | request_workflow_resources, _can_allocate_resources, _allocate_workflow_resources, _scheduling_loop, start (+2) |
| `src/agent_orchestration/optimization/response_time_monitor.py` | create, end_timing, record_metric, record_duration, get_stats (+1) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/response_time_monitor.py` | create, end_timing, record_metric, record_duration, get_stats (+1) |
| `src/agent_orchestration/optimization/optimization_engine.py` | run_optimization_cycle, _optimization_loop |
| `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/optimization_engine.py` | run_optimization_cycle, _optimization_loop |

## Entry Points

Start here when exploring this area:

- **`request_workflow_resources`** (Function) — `src/agent_orchestration/optimization/workflow_resource_manager.py:296`
- **`create`** (Function) — `src/agent_orchestration/optimization/response_time_monitor.py:53`
- **`end_timing`** (Function) — `src/agent_orchestration/optimization/response_time_monitor.py:206`
- **`record_metric`** (Function) — `src/agent_orchestration/optimization/response_time_monitor.py:242`
- **`record_duration`** (Function) — `src/agent_orchestration/optimization/response_time_monitor.py:258`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `request_workflow_resources` | Function | `src/agent_orchestration/optimization/workflow_resource_manager.py` | 296 |
| `create` | Function | `src/agent_orchestration/optimization/response_time_monitor.py` | 53 |
| `end_timing` | Function | `src/agent_orchestration/optimization/response_time_monitor.py` | 206 |
| `record_metric` | Function | `src/agent_orchestration/optimization/response_time_monitor.py` | 242 |
| `record_duration` | Function | `src/agent_orchestration/optimization/response_time_monitor.py` | 258 |
| `start` | Function | `src/agent_orchestration/optimization/performance_analytics.py` | 135 |
| `request_workflow_resources` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/workflow_resource_manager.py` | 284 |
| `create` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/response_time_monitor.py` | 53 |
| `end_timing` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/response_time_monitor.py` | 204 |
| `record_metric` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/response_time_monitor.py` | 240 |
| `record_duration` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/response_time_monitor.py` | 256 |
| `start` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/performance_analytics.py` | 133 |
| `start` | Function | `src/agent_orchestration/optimization/workflow_resource_manager.py` | 270 |
| `get_performance_dashboard` | Function | `src/agent_orchestration/optimization/performance_analytics.py` | 163 |
| `get_statistics` | Function | `src/agent_orchestration/optimization/performance_analytics.py` | 676 |
| `start` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/workflow_resource_manager.py` | 258 |
| `get_performance_dashboard` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/performance_analytics.py` | 159 |
| `get_statistics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/optimization/performance_analytics.py` | 637 |
| `get_stats` | Function | `src/agent_orchestration/optimization/response_time_monitor.py` | 282 |
| `run_optimization_cycle` | Function | `src/agent_orchestration/optimization/optimization_engine.py` | 384 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Get_performance_dashboard → Get_statistics` | cross_community | 3 |
| `Get_performance_dashboard → Get_statistics` | cross_community | 3 |

## How to Explore

1. `gitnexus_context({name: "request_workflow_resources"})` — see callers and callees
2. `gitnexus_query({query: "optimization"})` — find related execution flows
3. Read key files listed above for implementation details
