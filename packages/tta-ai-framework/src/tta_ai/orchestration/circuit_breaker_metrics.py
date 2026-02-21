"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Circuit_breaker_metrics]]
Circuit breaker metrics integration with existing metrics system.

Provides structured logging with correlation IDs and metrics collection
for circuit breaker state changes and operations.
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from .circuit_breaker import CircuitBreakerState

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerMetricsCollector:
    """Collects and aggregates circuit breaker metrics."""

    # State transition counters
    state_transitions: dict[str, int] = field(default_factory=dict)

    # Operation counters
    calls_permitted: int = 0
    calls_rejected: int = 0
    successful_calls: int = 0
    failed_calls: int = 0

    # State duration tracking
    state_durations: dict[str, float] = field(default_factory=dict)

    # Last update timestamp
    last_update: float = field(default_factory=time.time)

    def record_state_transition(
        self,
        circuit_breaker_name: str,
        from_state: CircuitBreakerState,
        to_state: CircuitBreakerState,
        correlation_id: str | None = None,
    ) -> None:
        """Record a circuit breaker state transition."""
        transition_key = f"{from_state.value}_to_{to_state.value}"
        self.state_transitions[transition_key] = self.state_transitions.get(transition_key, 0) + 1
        self.last_update = time.time()

        # Structured logging with correlation ID
        logger.info(
            "Circuit breaker state transition",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "from_state": from_state.value,
                "to_state": to_state.value,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "timestamp": self.last_update,
                "event_type": "circuit_breaker_state_transition",
            },
        )

    def record_call_permitted(
        self, circuit_breaker_name: str, correlation_id: str | None = None
    ) -> None:
        """Record a permitted call through circuit breaker."""
        self.calls_permitted += 1
        self.last_update = time.time()

        logger.debug(
            "Circuit breaker call permitted",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "correlation_id": correlation_id,
                "timestamp": self.last_update,
                "event_type": "circuit_breaker_call_permitted",
            },
        )

    def record_call_rejected(
        self,
        circuit_breaker_name: str,
        reason: str,
        correlation_id: str | None = None,
    ) -> None:
        """Record a rejected call by circuit breaker."""
        self.calls_rejected += 1
        self.last_update = time.time()

        logger.warning(
            "Circuit breaker call rejected",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "reason": reason,
                "correlation_id": correlation_id,
                "timestamp": self.last_update,
                "event_type": "circuit_breaker_call_rejected",
            },
        )

    def record_successful_call(
        self,
        circuit_breaker_name: str,
        duration_ms: float,
        correlation_id: str | None = None,
    ) -> None:
        """Record a successful call through circuit breaker."""
        self.successful_calls += 1
        self.last_update = time.time()

        logger.debug(
            "Circuit breaker successful call",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id,
                "timestamp": self.last_update,
                "event_type": "circuit_breaker_successful_call",
            },
        )

    def record_failed_call(
        self,
        circuit_breaker_name: str,
        error: str,
        duration_ms: float,
        correlation_id: str | None = None,
    ) -> None:
        """Record a failed call through circuit breaker."""
        self.failed_calls += 1
        self.last_update = time.time()

        logger.warning(
            "Circuit breaker failed call",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "error": error,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id,
                "timestamp": self.last_update,
                "event_type": "circuit_breaker_failed_call",
            },
        )

    def record_state_duration(
        self,
        circuit_breaker_name: str,
        state: CircuitBreakerState,
        duration_seconds: float,
    ) -> None:
        """Record how long a circuit breaker spent in a particular state."""
        state_key = f"{circuit_breaker_name}_{state.value}"
        current_duration = self.state_durations.get(state_key, 0.0)
        self.state_durations[state_key] = current_duration + duration_seconds
        self.last_update = time.time()

    def get_snapshot(self) -> dict[str, Any]:
        """Get a snapshot of current metrics."""
        return {
            "state_transitions": self.state_transitions.copy(),
            "calls_permitted": self.calls_permitted,
            "calls_rejected": self.calls_rejected,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "state_durations": self.state_durations.copy(),
            "last_update": self.last_update,
            "success_rate": (
                self.successful_calls / (self.successful_calls + self.failed_calls)
                if (self.successful_calls + self.failed_calls) > 0
                else 0.0
            ),
            "rejection_rate": (
                self.calls_rejected / (self.calls_permitted + self.calls_rejected)
                if (self.calls_permitted + self.calls_rejected) > 0
                else 0.0
            ),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.state_transitions.clear()
        self.calls_permitted = 0
        self.calls_rejected = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.state_durations.clear()
        self.last_update = time.time()


class CircuitBreakerLogger:
    """Enhanced logging for circuit breaker operations with correlation IDs."""

    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.metrics_collector = CircuitBreakerMetricsCollector()

    @contextmanager
    def operation_context(
        self,
        circuit_breaker_name: str,
        operation: str,
        correlation_id: str | None = None,
    ):
        """Context manager for circuit breaker operations with timing and correlation."""
        correlation_id = correlation_id or str(uuid.uuid4())
        start_time = time.time()

        self.logger.debug(
            f"Starting circuit breaker operation: {operation}",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "operation": operation,
                "correlation_id": correlation_id,
                "timestamp": start_time,
                "event_type": "circuit_breaker_operation_start",
            },
        )

        try:
            yield correlation_id
            duration_ms = (time.time() - start_time) * 1000

            self.logger.debug(
                f"Completed circuit breaker operation: {operation}",
                extra={
                    "circuit_breaker_name": circuit_breaker_name,
                    "operation": operation,
                    "correlation_id": correlation_id,
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "event_type": "circuit_breaker_operation_complete",
                },
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                f"Failed circuit breaker operation: {operation}",
                extra={
                    "circuit_breaker_name": circuit_breaker_name,
                    "operation": operation,
                    "correlation_id": correlation_id,
                    "error": str(e),
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "event_type": "circuit_breaker_operation_error",
                },
            )
            raise

    def log_circuit_breaker_created(
        self,
        circuit_breaker_name: str,
        config: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None:
        """Log circuit breaker creation."""
        self.logger.info(
            "Circuit breaker created",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "config": config,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "timestamp": time.time(),
                "event_type": "circuit_breaker_created",
            },
        )

    def log_circuit_breaker_reset(
        self, circuit_breaker_name: str, correlation_id: str | None = None
    ) -> None:
        """Log circuit breaker manual reset."""
        self.logger.info(
            "Circuit breaker manually reset",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "timestamp": time.time(),
                "event_type": "circuit_breaker_reset",
            },
        )

    def log_degraded_mode_activation(
        self,
        circuit_breaker_name: str,
        reason: str,
        correlation_id: str | None = None,
    ) -> None:
        """Log activation of degraded mode."""
        self.logger.warning(
            "Degraded mode activated",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "reason": reason,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "timestamp": time.time(),
                "event_type": "degraded_mode_activation",
            },
        )

    def log_degraded_mode_deactivation(
        self, circuit_breaker_name: str, correlation_id: str | None = None
    ) -> None:
        """Log deactivation of degraded mode."""
        self.logger.info(
            "Degraded mode deactivated",
            extra={
                "circuit_breaker_name": circuit_breaker_name,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "timestamp": time.time(),
                "event_type": "degraded_mode_deactivation",
            },
        )

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        return self.metrics_collector.get_snapshot()

    def reset_metrics(self) -> None:
        """Reset metrics collector."""
        self.metrics_collector.reset()


# Global metrics collector instance
_global_metrics_collector = CircuitBreakerMetricsCollector()
_global_logger = CircuitBreakerLogger()


def get_circuit_breaker_metrics() -> CircuitBreakerMetricsCollector:
    """Get global circuit breaker metrics collector."""
    return _global_metrics_collector


def get_circuit_breaker_logger() -> CircuitBreakerLogger:
    """Get global circuit breaker logger."""
    return _global_logger


def record_state_transition(
    circuit_breaker_name: str,
    from_state: CircuitBreakerState,
    to_state: CircuitBreakerState,
    correlation_id: str | None = None,
) -> None:
    """Convenience function to record state transition."""
    _global_metrics_collector.record_state_transition(
        circuit_breaker_name, from_state, to_state, correlation_id
    )


def record_degraded_mode_activation(
    circuit_breaker_name: str, reason: str, correlation_id: str | None = None
) -> None:
    """Convenience function to record degraded mode activation."""
    _global_logger.log_degraded_mode_activation(circuit_breaker_name, reason, correlation_id)
