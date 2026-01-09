"""

# Logseq: [[TTA.dev/Agent_orchestration/Performance/Step_aggregator]]
Step timing aggregation for agent orchestration performance monitoring.

This module provides thread-safe aggregation of step timing metrics per agent type,
enabling lightweight in-process performance tracking.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class StepStats:
    """Statistics for a single step type."""

    durations_ms: list[float] = field(default_factory=list)
    max_samples: int = 1000
    successes: int = 0
    errors: int = 0

    def record(self, duration_ms: float, success: bool) -> None:
        """Record a step execution."""
        self.durations_ms.append(float(duration_ms))
        if len(self.durations_ms) > self.max_samples:
            # Keep sliding window
            self.durations_ms = self.durations_ms[-self.max_samples :]
        if success:
            self.successes += 1
        else:
            self.errors += 1

    def snapshot(self) -> dict[str, float]:
        """Get current statistics snapshot."""
        arr = list(self.durations_ms)
        if not arr:
            return {"p50": 0.0, "p95": 0.0, "avg": 0.0}
        arr_sorted = sorted(arr)
        n = len(arr_sorted)
        p50 = arr_sorted[int(0.5 * (n - 1))]
        p95 = arr_sorted[int(0.95 * (n - 1))]
        avg = sum(arr_sorted) / n
        return {"p50": float(p50), "p95": float(p95), "avg": float(avg)}

    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.successes + self.errors
        return (self.errors / total) if total else 0.0


class StepTimingAggregator:
    """Aggregates step timing metrics per agent type.

    Thread-safe and lightweight for in-process aggregation.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._stats: dict[str, StepStats] = {}

    def record(self, agent_key: str, duration_ms: float, success: bool = True) -> None:
        """Record a step execution for an agent."""
        with self._lock:
            stats = self._stats.get(agent_key)
            if stats is None:
                stats = StepStats()
                self._stats[agent_key] = stats
            stats.record(duration_ms, success)

    def snapshot(self) -> dict[str, dict[str, float]]:
        """Get snapshot of all agent statistics."""
        with self._lock:
            snap: dict[str, dict[str, float]] = {}
            for k, stats in self._stats.items():
                s = stats.snapshot()
                s["error_rate"] = stats.error_rate()
                snap[k] = s
            return snap


# Global aggregator for orchestration
_AGGREGATOR = StepTimingAggregator()


def get_step_aggregator() -> StepTimingAggregator:
    """Get the global step timing aggregator instance."""
    return _AGGREGATOR
