---
name: realtime
description: "Skill for the Realtime area of TTA. 244 symbols across 28 files."
---

# Realtime

244 symbols | 28 files | Cohesion: 84%

## When to Use

- Working with code in `src/`
- Understanding how get_realtime_config, get_realtime_config, create_progressive_feedback_event work
- Modifying realtime-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/websocket_manager.py` | handle_connection, _authenticate_connection, _authenticate_with_token, _handle_messages, _handle_subscription (+17) |
| `src/agent_orchestration/realtime/websocket_manager.py` | handle_connection, _authenticate_connection, _authenticate_with_token, _handle_messages, _handle_subscription (+17) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/client_utils.js` | connect, setupEventHandlers, handleMessage, handleConnectionStatus, handleReconnect (+10) |
| `src/agent_orchestration/realtime/client_utils.js` | connect, setupEventHandlers, handleMessage, handleConnectionStatus, handleReconnect (+10) |
| `src/agent_orchestration/realtime/dashboard.py` | start, _update_loop, _update_dashboard_data, _update_system_health_data, _update_agent_performance_data (+8) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/dashboard.py` | start, _update_loop, _update_dashboard_data, _update_workflow_status_data, _update_resource_usage_data (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | start_workflow, update_workflow_progress, complete_milestone, complete_workflow, fail_workflow (+5) |
| `src/agent_orchestration/realtime/workflow_progress.py` | start_workflow, update_workflow_progress, complete_milestone, complete_workflow, fail_workflow (+5) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | load_config, _get_default_enabled, _load_websocket_config, _load_event_config, _load_progressive_feedback_config (+4) |
| `src/agent_orchestration/realtime/config_manager.py` | load_config, _get_default_enabled, _load_websocket_config, _load_event_config, _load_progressive_feedback_config (+4) |

## Entry Points

Start here when exploring this area:

- **`get_realtime_config`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py:342`
- **`get_realtime_config`** (Function) — `src/agent_orchestration/realtime/config_manager.py:375`
- **`create_progressive_feedback_event`** (Function) — `src/agent_orchestration/realtime/models.py:333`
- **`create_error_event`** (Function) — `src/agent_orchestration/realtime/models.py:358`
- **`create_progressive_feedback_event`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py:262`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_realtime_config` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 342 |
| `get_realtime_config` | Function | `src/agent_orchestration/realtime/config_manager.py` | 375 |
| `create_progressive_feedback_event` | Function | `src/agent_orchestration/realtime/models.py` | 333 |
| `create_error_event` | Function | `src/agent_orchestration/realtime/models.py` | 358 |
| `create_progressive_feedback_event` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py` | 262 |
| `create_workflow_progress_event` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py` | 235 |
| `create_workflow_progress_event` | Function | `src/agent_orchestration/realtime/models.py` | 306 |
| `create_agent_status_event` | Function | `src/agent_orchestration/realtime/models.py` | 283 |
| `create_system_metrics_event` | Function | `src/agent_orchestration/realtime/models.py` | 377 |
| `create_agent_status_event` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py` | 212 |
| `create_error_event` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/models.py` | 287 |
| `handle_connection` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/websocket_manager.py` | 181 |
| `handle_connection` | Method | `src/agent_orchestration/realtime/websocket_manager.py` | 188 |
| `load_config` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 123 |
| `get_config` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/config_manager.py` | 298 |
| `load_config` | Method | `src/agent_orchestration/realtime/config_manager.py` | 127 |
| `get_config` | Method | `src/agent_orchestration/realtime/config_manager.py` | 331 |
| `start` | Method | `src/agent_orchestration/realtime/dashboard.py` | 113 |
| `start_workflow` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 288 |
| `update_workflow_progress` | Method | `packages/tta-ai-framework/src/tta_ai/orchestration/realtime/workflow_progress.py` | 334 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Handle_connection → _mark_connection_disconnected` | cross_community | 5 |
| `Handle_connection → _mark_connection_disconnected` | cross_community | 5 |
| `Track_workflow → _publish_event` | intra_community | 4 |
| `Track_workflow → Create_workflow_progress_event` | intra_community | 4 |
| `Handle_connection → _send_to_connection` | cross_community | 4 |
| `Track_workflow → _publish_event` | intra_community | 4 |
| `Track_workflow → Create_workflow_progress_event` | intra_community | 4 |
| `Handle_connection → _send_to_connection` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Integration | 2 calls |

## How to Explore

1. `context({name: "get_realtime_config"})` — see callers and callees
2. `query({search_query: "realtime"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
