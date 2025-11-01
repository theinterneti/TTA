from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class RetryStats:
    total_nacks: int = 0
    total_permanent_failures: int = 0
    total_retries_scheduled: int = 0
    last_backoff_seconds: float = 0.0


@dataclass
class DeliveryStats:
    delivered_ok: int = 0
    delivered_error: int = 0


@dataclass
class QueueGauges:
    # Gauges keyed by (agent_key, priority)
    queue_lengths: dict[tuple[str, int], int] = field(default_factory=dict)
    # DLQ lengths per agent_key
    dlq_lengths: dict[str, int] = field(default_factory=dict)


class MessageMetrics:
    """In-memory metrics aggregation for message coordination.

    This is a lightweight, self-contained abstraction so we avoid external deps.
    """

    def __init__(self) -> None:
        self.retry = RetryStats()
        self.delivery = DeliveryStats()
        self.gauges = QueueGauges()
        self._last_update = time.time()

    # --- Counters ---
    def inc_delivered_ok(self, n: int = 1) -> None:
        self.delivery.delivered_ok += n

    def inc_delivered_error(self, n: int = 1) -> None:
        self.delivery.delivered_error += n

    def inc_nacks(self, n: int = 1) -> None:
        self.retry.total_nacks += n

    def inc_permanent(self, n: int = 1) -> None:
        self.retry.total_permanent_failures += n

    def inc_retries_scheduled(
        self, n: int = 1, last_backoff_seconds: float = 0.0
    ) -> None:
        self.retry.total_retries_scheduled += n
        self.retry.last_backoff_seconds = last_backoff_seconds

    # --- Gauges ---
    def set_queue_length(self, agent_key: str, priority: int, length: int) -> None:
        self.gauges.queue_lengths[(agent_key, priority)] = length

    def set_dlq_length(self, agent_key: str, length: int) -> None:
        self.gauges.dlq_lengths[agent_key] = length

    # --- Snapshot ---
    def snapshot(self) -> dict:
        self._last_update = time.time()
        return {
            "retry": self.retry.__dict__,
            "delivery": self.delivery.__dict__,
            "gauges": {
                "queue_lengths": {
                    f"{k[0]}|{k[1]}": v for k, v in self.gauges.queue_lengths.items()
                },
                "dlq_lengths": self.gauges.dlq_lengths,
            },
            "last_update": self._last_update,
        }
