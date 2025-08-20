# Diagnostics and Monitoring for Agent Orchestration

## Diagnostics Endpoint

A lightweight FastAPI-based server is started by the Agent Orchestration component (on 127.0.0.1 and the configured port).

Endpoints:

- GET /health: basic status for the component
- GET /metrics: returns `MessageMetrics.snapshot()` from the RedisMessageCoordinator
- GET /metrics-prom: Prometheus metrics export (requires prometheus_client)

Notes:

- If FastAPI or uvicorn are not available, the diagnostics server is skipped gracefully.
- Diagnostics server is gated by `agent_orchestration.diagnostics.enabled` (default: false). When disabled, server startup is skipped and a log entry is emitted.

## Auto-Recovery Logging

On startup, the component invokes `recover_pending(None)` and logs a total recovered count and per-agent recovery counts (type:instance) for observability.

## Periodic Metrics Polling

The component runs a background task that:

- Every 5 seconds, scans Redis for queue (audit) and per-priority ready zset keys
- Updates gauges: queue lengths by priority and DLQ lengths for each agent instance

## Threshold-Based Warning Foundation

Basic thresholds (configurable via config):

- `agent_orchestration.metrics.dlq_warn_threshold` (default: 10)
- `agent_orchestration.metrics.retry_spike_warn_threshold` (default: 20)

If DLQ length exceeds the threshold for an agent, a warning is logged.
If retry activity between two polling intervals exceeds the retry spike threshold, a warning is logged.
