"""
Model rotation manager for OpenHands integration.

Provides:
- ModelRotationManager: Manages model rotation for rate limiting
- RotationState: Tracks rotation state and metrics
- Exponential backoff retry logic
- Comprehensive logging

Usage:
------

```python
from src.agent_orchestration.openhands_integration.model_rotation import ModelRotationManager

# Create rotation manager
rotation_manager = ModelRotationManager()

# Get next model (primary or fallback)
model = rotation_manager.get_current_model()

# On rate limit error
rotation_manager.on_rate_limit()
next_model = rotation_manager.get_next_model()

# On success
rotation_manager.on_success()

# Get metrics
metrics = rotation_manager.get_metrics()
```
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RotationMetrics:
    """Metrics for model rotation tracking."""

    model: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    last_used: Optional[float] = None
    rotations_to_this_model: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    def update_success(self, execution_time: float) -> None:
        """Record successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_time += execution_time
        self.avg_time = self.total_time / self.total_requests
        self.last_used = time.time()

    def update_failure(self, execution_time: float, is_rate_limited: bool = False) -> None:
        """Record failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        if is_rate_limited:
            self.rate_limited_requests += 1
        self.total_time += execution_time
        self.avg_time = self.total_time / self.total_requests
        self.last_used = time.time()


@dataclass
class RotationState:
    """State of model rotation system."""

    current_model_index: int = 0
    rotation_count: int = 0
    last_rotation_time: Optional[float] = None
    consecutive_failures: int = 0
    circuit_breaker_open: bool = False
    metrics: dict[str, RotationMetrics] = field(default_factory=dict)

    def reset_consecutive_failures(self) -> None:
        """Reset consecutive failure counter."""
        self.consecutive_failures = 0

    def increment_consecutive_failures(self) -> None:
        """Increment consecutive failure counter."""
        self.consecutive_failures += 1

    def open_circuit_breaker(self) -> None:
        """Open circuit breaker to prevent cascading failures."""
        self.circuit_breaker_open = True
        logger.warning("Circuit breaker opened - too many consecutive failures")

    def close_circuit_breaker(self) -> None:
        """Close circuit breaker after recovery."""
        self.circuit_breaker_open = False
        logger.info("Circuit breaker closed - resuming normal operation")


class ModelRotationManager:
    """
    Manages model rotation for handling rate limiting.

    Maintains rotation order and tracks metrics for each model.
    """

    # Rotation order: Primary → Fallback 1 → Fallback 2 → Fallback 3
    DEFAULT_ROTATION_ORDER = [
        "mistralai/mistral-small-3.2-24b-instruct:free",  # Primary (fastest)
        "deepseek/deepseek-r1-0528-qwen3-8b:free",  # Fallback 1 (best quality)
        "deepseek/deepseek-chat-v3.1:free",  # Fallback 2 (balanced)
        "deepseek/deepseek-chat",  # Fallback 3 (legacy)
    ]

    def __init__(
        self,
        rotation_order: Optional[list[str]] = None,
        max_consecutive_failures: int = 3,
        circuit_breaker_threshold: int = 5,
    ) -> None:
        """
        Initialize model rotation manager.

        Args:
            rotation_order: List of models in rotation order
            max_consecutive_failures: Max failures before rotating
            circuit_breaker_threshold: Failures before opening circuit breaker
        """
        self.rotation_order = rotation_order or self.DEFAULT_ROTATION_ORDER
        self.max_consecutive_failures = max_consecutive_failures
        self.circuit_breaker_threshold = circuit_breaker_threshold

        # Initialize state
        self.state = RotationState()

        # Initialize metrics for each model
        for model in self.rotation_order:
            self.state.metrics[model] = RotationMetrics(model=model)

        logger.info(
            f"ModelRotationManager initialized with {len(self.rotation_order)} models"
        )
        logger.info(f"Rotation order: {' → '.join(self.rotation_order)}")

    def get_current_model(self) -> str:
        """Get current model in rotation."""
        return self.rotation_order[self.state.current_model_index]

    def get_next_model(self) -> str:
        """Get next model in rotation (for fallback)."""
        if self.state.current_model_index < len(self.rotation_order) - 1:
            self.state.current_model_index += 1
            self.state.rotation_count += 1
            self.state.last_rotation_time = time.time()
            current = self.get_current_model()
            self.state.metrics[current].rotations_to_this_model += 1
            logger.warning(
                f"Rotating to fallback model: {current} "
                f"(rotation #{self.state.rotation_count})"
            )
            return current
        else:
            # Already at last model, stay there
            logger.warning("Already at last fallback model, cannot rotate further")
            return self.get_current_model()

    def reset_to_primary(self) -> None:
        """Reset rotation to primary model."""
        if self.state.current_model_index != 0:
            self.state.current_model_index = 0
            logger.info("Reset rotation to primary model")

    def on_success(self, execution_time: float = 0.0) -> None:
        """Record successful request."""
        current = self.get_current_model()
        self.state.metrics[current].update_success(execution_time)
        self.state.reset_consecutive_failures()

        # Close circuit breaker on success
        if self.state.circuit_breaker_open:
            self.state.close_circuit_breaker()

        logger.debug(f"Success with {current} ({execution_time:.2f}s)")

    def on_failure(
        self,
        execution_time: float = 0.0,
        is_rate_limited: bool = False,
    ) -> None:
        """Record failed request."""
        current = self.get_current_model()
        self.state.metrics[current].update_failure(execution_time, is_rate_limited)
        self.state.increment_consecutive_failures()

        error_type = "rate limited" if is_rate_limited else "failed"
        logger.warning(
            f"Request {error_type} with {current} "
            f"(consecutive failures: {self.state.consecutive_failures})"
        )

        # Check if circuit breaker should open
        if self.state.consecutive_failures >= self.circuit_breaker_threshold:
            self.state.open_circuit_breaker()

    def on_rate_limit(self, execution_time: float = 0.0) -> None:
        """Record rate limit error and prepare for rotation."""
        self.on_failure(execution_time, is_rate_limited=True)

    def should_rotate(self) -> bool:
        """Determine if rotation is needed."""
        if self.state.circuit_breaker_open:
            return True
        return self.state.consecutive_failures >= self.max_consecutive_failures

    def get_metrics(self) -> dict[str, RotationMetrics]:
        """Get metrics for all models."""
        return self.state.metrics

    def get_current_metrics(self) -> RotationMetrics:
        """Get metrics for current model."""
        current = self.get_current_model()
        return self.state.metrics[current]

    def print_metrics(self) -> None:
        """Print metrics summary."""
        logger.info("=" * 80)
        logger.info("MODEL ROTATION METRICS")
        logger.info("=" * 80)

        for model, metrics in self.state.metrics.items():
            status = "✅" if metrics.success_rate >= 90 else "⚠️" if metrics.success_rate >= 70 else "❌"
            logger.info(
                f"{status} {model:50} | "
                f"Success: {metrics.successful_requests}/{metrics.total_requests} "
                f"({metrics.success_rate:5.1f}%) | "
                f"Avg Time: {metrics.avg_time:6.2f}s | "
                f"Rate Limited: {metrics.rate_limited_requests}"
            )

        logger.info("=" * 80)
        logger.info(f"Total Rotations: {self.state.rotation_count}")
        logger.info(f"Circuit Breaker: {'OPEN' if self.state.circuit_breaker_open else 'CLOSED'}")
        logger.info("=" * 80)

    def get_summary(self) -> dict:
        """Get summary of rotation state and metrics."""
        return {
            "current_model": self.get_current_model(),
            "current_model_index": self.state.current_model_index,
            "total_rotations": self.state.rotation_count,
            "consecutive_failures": self.state.consecutive_failures,
            "circuit_breaker_open": self.state.circuit_breaker_open,
            "metrics": {
                model: {
                    "total_requests": m.total_requests,
                    "successful_requests": m.successful_requests,
                    "failed_requests": m.failed_requests,
                    "rate_limited_requests": m.rate_limited_requests,
                    "success_rate": m.success_rate,
                    "avg_time": m.avg_time,
                }
                for model, m in self.state.metrics.items()
            },
        }

