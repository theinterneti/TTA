"""
Circuit Breaker Types Module

This module defines shared types and enums for circuit breaker functionality,
breaking circular dependencies between circuit_breaker and circuit_breaker_metrics modules.

Classes:
    CircuitBreakerState: Enum for circuit breaker states
    CircuitBreakerMetrics: Data structure for metrics
    CircuitBreakerConfig: Configuration data structure
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CircuitBreakerState(Enum):
    """States of a circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""

    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # State metrics
    state_changes: int = 0
    time_in_open_state: float = 0.0
    time_in_half_open_state: float = 0.0
    time_in_closed_state: float = 0.0

    # Performance metrics
    average_response_time: float = 0.0
    last_failure_time: float | None = None
    last_success_time: float | None = None

    # Threshold metrics
    failure_rate: float = 0.0
    success_rate: float = 0.0

    # Additional metadata
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_success(self, response_time: float = 0.0) -> None:
        """Update metrics for successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success_time = time.time()
        self.last_updated = time.time()

        # Update average response time
        if response_time > 0:
            if self.average_response_time == 0:
                self.average_response_time = response_time
            else:
                # Simple moving average
                self.average_response_time = (self.average_response_time + response_time) / 2

        # Update rates
        self._update_rates()

    def update_failure(self) -> None:
        """Update metrics for failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure_time = time.time()
        self.last_updated = time.time()

        # Update rates
        self._update_rates()

    def _update_rates(self) -> None:
        """Update success and failure rates."""
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests
            self.failure_rate = self.failed_requests / self.total_requests
        else:
            self.success_rate = 0.0
            self.failure_rate = 0.0


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    # Failure thresholds
    failure_threshold: int = 5  # Number of failures to open circuit
    failure_rate_threshold: float = 0.5  # Failure rate (0.0-1.0) to open circuit

    # Timing configuration
    timeout: float = 60.0  # Timeout in seconds for open state
    half_open_max_calls: int = 3  # Max calls in half-open state

    # Monitoring configuration
    monitoring_window: float = 300.0  # Time window for failure rate calculation (seconds)
    min_requests_for_rate: int = 10  # Minimum requests before considering failure rate

    # Recovery configuration
    recovery_timeout: float = 30.0  # Time to wait before attempting recovery
    max_recovery_attempts: int = 3  # Maximum recovery attempts

    # Metadata
    name: str = "default"
    description: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.failure_threshold <= 0:
            return False
        if not (0.0 <= self.failure_rate_threshold <= 1.0):
            return False
        if self.timeout <= 0:
            return False
        if self.half_open_max_calls <= 0:
            return False
        if self.monitoring_window <= 0:
            return False
        if self.min_requests_for_rate <= 0:
            return False
        if self.recovery_timeout <= 0:
            return False
        if self.max_recovery_attempts <= 0:
            return False

        return True


@dataclass
class StateTransitionEvent:
    """Event data for circuit breaker state transitions."""

    circuit_breaker_name: str
    old_state: CircuitBreakerState
    new_state: CircuitBreakerState
    correlation_id: str
    timestamp: float = field(default_factory=time.time)
    reason: str = ""
    metrics_snapshot: CircuitBreakerMetrics | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Utility functions
def calculate_failure_rate(successful: int, failed: int) -> float:
    """Calculate failure rate from success and failure counts."""
    total = successful + failed
    if total == 0:
        return 0.0
    return failed / total


def should_open_circuit(
    metrics: CircuitBreakerMetrics,
    config: CircuitBreakerConfig
) -> bool:
    """Determine if circuit should be opened based on metrics and config."""
    # Check failure count threshold
    if metrics.failed_requests >= config.failure_threshold:
        return True

    # Check failure rate threshold (only if we have enough requests)
    if (metrics.total_requests >= config.min_requests_for_rate and
        metrics.failure_rate >= config.failure_rate_threshold):
        return True

    return False


def should_attempt_reset(
    current_state: CircuitBreakerState,
    state_changed_at: float,
    config: CircuitBreakerConfig
) -> bool:
    """Determine if circuit breaker should attempt to reset."""
    if current_state != CircuitBreakerState.OPEN:
        return False

    time_in_open = time.time() - state_changed_at
    return time_in_open >= config.timeout


# Export all types and utilities
__all__ = [
    "CircuitBreakerState",
    "CircuitBreakerMetrics",
    "CircuitBreakerConfig",
    "StateTransitionEvent",
    "calculate_failure_rate",
    "should_open_circuit",
    "should_attempt_reset",
]
