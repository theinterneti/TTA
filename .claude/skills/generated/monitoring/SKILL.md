---
name: monitoring
description: "Skill for the Monitoring area of TTA. 59 symbols across 9 files."
---

# Monitoring

59 symbols | 9 files | Cohesion: 81%

## When to Use

- Working with code in `src/`
- Understanding how record_counter, record_gauge, record_timer work
- Modifying monitoring-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/player_experience/monitoring/benchmarking.py` | generate_load, _constant_load, _ramp_up_load, _spike_load, _ramp_phase (+9) |
| `src/player_experience/monitoring/performance_monitor.py` | __init__, _finish_request, track_query, _finish_query, _finish_cache_operation (+5) |
| `src/player_experience/monitoring/metrics_collector.py` | _aggregate_metrics, record_counter, record_gauge, record_timer, _record_metric_point (+5) |
| `src/monitoring/prometheus_metrics.py` | record_http_request, get_metrics, get_metrics_collector, metrics_endpoint, wrapper |
| `src/monitoring/metrics_middleware.py` | __init__, _start_system_metrics_collection, metrics, get_monitoring_status, setup_monitoring_middleware |
| `src/monitoring/realtime_alerts.py` | _alert_check_loop, _check_all_rules, _check_rule, _send_notifications, handler |
| `src/monitoring/mock_monitoring.py` | get_status, get_mock_monitoring_environment, mock_health, should_use_mock_monitoring, auto_configure_monitoring |
| `src/player_experience/monitoring/logging_config.py` | debug, _log, info, warning |
| `src/player_experience/api/middleware.py` | dispatch |

## Entry Points

Start here when exploring this area:

- **`record_counter`** (Function) — `src/player_experience/monitoring/metrics_collector.py:272`
- **`record_gauge`** (Function) — `src/player_experience/monitoring/metrics_collector.py:280`
- **`record_timer`** (Function) — `src/player_experience/monitoring/metrics_collector.py:286`
- **`get_metrics_collector`** (Function) — `src/player_experience/monitoring/metrics_collector.py:489`
- **`record_request_metric`** (Function) — `src/player_experience/monitoring/metrics_collector.py:497`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `record_counter` | Function | `src/player_experience/monitoring/metrics_collector.py` | 272 |
| `record_gauge` | Function | `src/player_experience/monitoring/metrics_collector.py` | 280 |
| `record_timer` | Function | `src/player_experience/monitoring/metrics_collector.py` | 286 |
| `get_metrics_collector` | Function | `src/player_experience/monitoring/metrics_collector.py` | 489 |
| `record_request_metric` | Function | `src/player_experience/monitoring/metrics_collector.py` | 497 |
| `record_database_query_metric` | Function | `src/player_experience/monitoring/metrics_collector.py` | 523 |
| `record_cache_metric` | Function | `src/player_experience/monitoring/metrics_collector.py` | 540 |
| `record_therapeutic_interaction` | Function | `src/player_experience/monitoring/metrics_collector.py` | 552 |
| `record_http_request` | Function | `src/monitoring/prometheus_metrics.py` | 268 |
| `get_metrics` | Function | `src/monitoring/prometheus_metrics.py` | 421 |
| `get_metrics_collector` | Function | `src/monitoring/prometheus_metrics.py` | 430 |
| `metrics_endpoint` | Function | `src/monitoring/prometheus_metrics.py` | 438 |
| `wrapper` | Function | `src/monitoring/prometheus_metrics.py` | 449 |
| `metrics` | Function | `src/monitoring/metrics_middleware.py` | 131 |
| `track_query` | Function | `src/player_experience/monitoring/performance_monitor.py` | 186 |
| `get_performance_monitor` | Function | `src/player_experience/monitoring/performance_monitor.py` | 744 |
| `debug` | Function | `src/player_experience/monitoring/logging_config.py` | 295 |
| `dispatch` | Function | `src/player_experience/api/middleware.py` | 74 |
| `generate_load` | Function | `src/player_experience/monitoring/benchmarking.py` | 238 |
| `handler` | Function | `src/monitoring/realtime_alerts.py` | 376 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_all → _select_endpoint` | cross_community | 7 |
| `Dispatch → _record_metric_point` | cross_community | 4 |
| `Run_all → Meets_success_criteria` | cross_community | 4 |
| `Run_all → _log` | intra_community | 4 |
| `Dispatch → _log` | cross_community | 3 |
| `Run_all → _collect_system_metrics` | cross_community | 3 |
| `Record_database_query_metric → _record_metric_point` | intra_community | 3 |
| `Record_therapeutic_interaction → _record_metric_point` | intra_community | 3 |
| `Record_cache_metric → _record_metric_point` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Security | 4 calls |

## How to Explore

1. `gitnexus_context({name: "record_counter"})` — see callers and callees
2. `gitnexus_query({query: "monitoring"})` — find related execution flows
3. Read key files listed above for implementation details
