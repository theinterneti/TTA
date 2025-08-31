# Messaging Metrics for Agent Orchestration

## Overview
This document describes basic metrics exposed by the message coordination layer.

## Metrics

- Queue lengths per agent and priority
  - Gauge: messaging.queue_length{agent="<type:inst>", priority=<1|5|9>}
- Dead Letter Queue counts
  - Gauge: messaging.dlq_length{agent="<type:inst>"}
- Retry statistics
  - Counter: messaging.nacks.total
  - Counter: messaging.retries.scheduled.total
  - Counter: messaging.permanent_failures.total
  - Gauge: messaging.retries.last_backoff_seconds
- Delivery success/failure
  - Counter: messaging.delivered.ok
  - Counter: messaging.delivered.error

## Access

The RedisMessageCoordinator maintains an in-memory MessageMetrics instance.
Call `coord.metrics.snapshot()` to retrieve a dict snapshot of current values.

## Future Work

- Export metrics via Prometheus/OpenTelemetry exporters
- Emit events on threshold breaches (e.g., DLQ growth)
- Persist rolling aggregates to Redis for multi-process visibility
