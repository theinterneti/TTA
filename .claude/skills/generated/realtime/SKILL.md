---
name: realtime
description: "Skill for the Realtime area of TTA. 196 symbols across 26 files."
---

# Realtime

196 symbols | 26 files | Cohesion: 85%

## When to Use

- Working with code in `src/`
- Understanding how start, load_config, get_config work
- Modifying realtime-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/agent_orchestration/realtime/client_utils.js` | connect, setupEventHandlers, handleMessage, handleConnectionStatus, handleReconnect (+9) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/client_utils.js` | connect, setupEventHandlers, handleMessage, handleConnectionStatus, handleReconnect (+9) |
| `src/agent_orchestration/realtime/dashboard.py` | start, _update_loop, _update_dashboard_data, _update_system_health_data, _update_agent_performance_data (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/dashboard.py` | start, _update_loop, _update_dashboard_data, _update_workflow_status_data, _update_resource_usage_data (+6) |
| `src/agent_orchestration/realtime/workflow_progress.py` | start_workflow, update_workflow_progress, complete_milestone, complete_workflow, fail_workflow (+5) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | start_workflow, update_workflow_progress, complete_milestone, complete_workflow, fail_workflow (+5) |
| `src/agent_orchestration/realtime/config_manager.py` | load_config, _get_default_enabled, _load_websocket_config, _load_event_config, _load_progressive_feedback_config (+4) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | load_config, _get_default_enabled, _load_websocket_config, _load_event_config, _load_progressive_feedback_config (+4) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/agent_event_integration.py` | publish_status_change, _publish_event, track_workflow, _advance_workflow_step, _update_workflow_progress (+4) |
| `src/agent_orchestration/realtime/agent_event_integration.py` | _publish_event, track_operation, _publish_progress, _publish_feedback, publish_status_change (+4) |

## Entry Points

Start here when exploring this area:

- **`start`** (Function) — `src/agent_orchestration/realtime/dashboard.py:113`
- **`load_config`** (Function) — `src/agent_orchestration/realtime/config_manager.py:127`
- **`get_config`** (Function) — `src/agent_orchestration/realtime/config_manager.py:331`
- **`get_realtime_config`** (Function) — `src/agent_orchestration/realtime/config_manager.py:375`
- **`load_config`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py:123`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `start` | Function | `src/agent_orchestration/realtime/dashboard.py` | 113 |
| `load_config` | Function | `src/agent_orchestration/realtime/config_manager.py` | 127 |
| `get_config` | Function | `src/agent_orchestration/realtime/config_manager.py` | 331 |
| `get_realtime_config` | Function | `src/agent_orchestration/realtime/config_manager.py` | 375 |
| `load_config` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 123 |
| `get_config` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 298 |
| `get_realtime_config` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 342 |
| `start_workflow` | Function | `src/agent_orchestration/realtime/workflow_progress.py` | 290 |
| `update_workflow_progress` | Function | `src/agent_orchestration/realtime/workflow_progress.py` | 338 |
| `complete_milestone` | Function | `src/agent_orchestration/realtime/workflow_progress.py` | 381 |
| `complete_workflow` | Function | `src/agent_orchestration/realtime/workflow_progress.py` | 401 |
| `fail_workflow` | Function | `src/agent_orchestration/realtime/workflow_progress.py` | 442 |
| `start_workflow` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 288 |
| `update_workflow_progress` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 334 |
| `complete_milestone` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 377 |
| `complete_workflow` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 397 |
| `fail_workflow` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 432 |
| `create_agent_status_event` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py` | 212 |
| `report_error` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/error_reporting.py` | 146 |
| `report_recovery_attempt` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/error_reporting.py` | 196 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Track_workflow → _publish_event` | intra_community | 4 |
| `Track_workflow → Create_workflow_progress_event` | intra_community | 4 |
| `Track_workflow → _publish_event` | intra_community | 4 |
| `Track_workflow → Create_workflow_progress_event` | intra_community | 4 |
| `Start → _determine_agent_status_from_metrics` | intra_community | 4 |
| `Start → Create_agent_status_event` | cross_community | 4 |
| `Start → Create_system_metrics_event` | cross_community | 4 |
| `Track_operation → _publish_event` | intra_community | 3 |
| `Track_operation → Create_progressive_feedback_event` | intra_community | 3 |
| `Track_operation → _publish_event` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Monitoring | 2 calls |

## How to Explore

1. `gitnexus_context({name: "start"})` — see callers and callees
2. `gitnexus_query({query: "realtime"})` — find related execution flows
3. Read key files listed above for implementation details
