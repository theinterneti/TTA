"""
Circuit breaker pattern implementation for the API Gateway.

This module provides circuit breaker functionality to protect backend services
from cascading failures and provide graceful degradation.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..models import ServiceInfo

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Number of failures to open circuit
    recovery_timeout: float = 60.0  # Seconds to wait before trying half-open
    success_threshold: int = 3  # Successful requests needed to close circuit
    timeout: float = 30.0  # Request timeout in seconds

    # Therapeutic-specific settings
    therapeutic_failure_threshold: int = 3  # Lower threshold for therapeutic services
    therapeutic_recovery_timeout: float = (
        30.0  # Faster recovery for therapeutic services
    )
    crisis_bypass: bool = True  # Allow crisis requests even when circuit is open


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    state_change_time: float = field(default_factory=time.time)


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    def __init__(self, service_name: str, state: CircuitBreakerState):
        self.service_name = service_name
        self.state = state
        super().__init__(f"Circuit breaker is {state.value} for service {service_name}")


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting backend services.

    The circuit breaker monitors service health and automatically opens
    when failure thresholds are exceeded, providing fail-fast behavior
    and automatic recovery testing.
    """

    def __init__(
        self, service_info: ServiceInfo, config: CircuitBreakerConfig | None = None
    ):
        """
        Initialize circuit breaker for a service.

        Args:
            service_info: Service information
            config: Circuit breaker configuration
        """
        self.service_info = service_info
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()

        # Adjust thresholds for therapeutic services
        if service_info.therapeutic_priority:
            self.config.failure_threshold = self.config.therapeutic_failure_threshold
            self.config.recovery_timeout = self.config.therapeutic_recovery_timeout

    @asynccontextmanager
    async def call(self, therapeutic_request: bool = False, crisis_mode: bool = False):
        """
        Context manager for making calls through the circuit breaker.

        Args:
            therapeutic_request: Whether this is a therapeutic request
            crisis_mode: Whether this is a crisis situation

        Yields:
            None if call is allowed

        Raises:
            CircuitBreakerError: If circuit is open and call is not allowed
        """
        async with self._lock:
            # Check if call is allowed
            if not await self._is_call_allowed(therapeutic_request, crisis_mode):
                raise CircuitBreakerError(self.service_info.name, self.state)

            # Record request attempt
            self.metrics.total_requests += 1

        start_time = time.time()
        success = False

        try:
            yield
            success = True

        except Exception:
            success = False
            raise

        finally:
            # Record result
            response_time = time.time() - start_time
            await self._record_result(success, response_time, therapeutic_request)

    async def _is_call_allowed(
        self, therapeutic_request: bool, crisis_mode: bool
    ) -> bool:
        """
        Check if a call is allowed based on circuit breaker state.

        Args:
            therapeutic_request: Whether this is a therapeutic request
            crisis_mode: Whether this is a crisis situation

        Returns:
            True if call is allowed
        """
        current_time = time.time()

        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Allow crisis requests to bypass circuit breaker
            if crisis_mode and self.config.crisis_bypass:
                logger.warning(
                    f"Allowing crisis request to bypass open circuit breaker for {self.service_info.name}"
                )
                return True

            # Check if recovery timeout has passed
            time_since_failure = current_time - self.metrics.last_failure_time
            if time_since_failure >= self.config.recovery_timeout:
                await self._transition_to_half_open()
                return True

            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited requests to test service recovery
            return True

        return False

    async def _record_result(
        self, success: bool, response_time: float, therapeutic_request: bool
    ):
        """
        Record the result of a service call.

        Args:
            success: Whether the call was successful
            response_time: Response time in seconds
            therapeutic_request: Whether this was a therapeutic request
        """
        async with self._lock:
            current_time = time.time()

            if success:
                self.metrics.successful_requests += 1
                self.metrics.consecutive_successes += 1
                self.metrics.consecutive_failures = 0
                self.metrics.last_success_time = current_time

                # Check if we should close the circuit
                if self.state == CircuitBreakerState.HALF_OPEN:
                    if (
                        self.metrics.consecutive_successes
                        >= self.config.success_threshold
                    ):
                        await self._transition_to_closed()

            else:
                self.metrics.failed_requests += 1
                self.metrics.consecutive_failures += 1
                self.metrics.consecutive_successes = 0
                self.metrics.last_failure_time = current_time

                # Check if we should open the circuit
                if self.state == CircuitBreakerState.CLOSED:
                    failure_threshold = self.config.failure_threshold

                    # Use lower threshold for therapeutic services
                    if therapeutic_request and self.service_info.therapeutic_priority:
                        failure_threshold = self.config.therapeutic_failure_threshold

                    if self.metrics.consecutive_failures >= failure_threshold:
                        await self._transition_to_open()

                elif self.state == CircuitBreakerState.HALF_OPEN:
                    # Any failure in half-open state opens the circuit
                    await self._transition_to_open()

    async def _transition_to_open(self):
        """Transition circuit breaker to open state."""
        if self.state != CircuitBreakerState.OPEN:
            logger.warning(
                f"Circuit breaker opening for service {self.service_info.name} "
                f"after {self.metrics.consecutive_failures} consecutive failures"
            )
            self.state = CircuitBreakerState.OPEN
            current_time = time.time()
            self.metrics.state_change_time = current_time
            # Ensure last_failure_time is set to prevent immediate recovery
            if self.metrics.last_failure_time == 0:
                self.metrics.last_failure_time = current_time

    async def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state."""
        if self.state != CircuitBreakerState.HALF_OPEN:
            logger.info(
                f"Circuit breaker transitioning to half-open for service {self.service_info.name}"
            )
            self.state = CircuitBreakerState.HALF_OPEN
            self.metrics.state_change_time = time.time()
            self.metrics.consecutive_successes = 0

    async def _transition_to_closed(self):
        """Transition circuit breaker to closed state."""
        if self.state != CircuitBreakerState.CLOSED:
            logger.info(
                f"Circuit breaker closing for service {self.service_info.name} "
                f"after {self.metrics.consecutive_successes} consecutive successes"
            )
            self.state = CircuitBreakerState.CLOSED
            self.metrics.state_change_time = time.time()
            self.metrics.consecutive_failures = 0

    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics."""
        return self.metrics

    def is_healthy(self) -> bool:
        """Check if the service is considered healthy."""
        if self.state == CircuitBreakerState.OPEN:
            return False

        # If circuit is closed, service is considered healthy (has recovered)
        if self.state == CircuitBreakerState.CLOSED:
            return True

        # For half-open state, check recent success rate
        if self.metrics.total_requests > 0:
            success_rate = (
                self.metrics.successful_requests / self.metrics.total_requests
            )
            return success_rate >= 0.7  # 70% success rate threshold

        return True

    async def force_open(self):
        """Force circuit breaker to open state (for testing/maintenance)."""
        async with self._lock:
            await self._transition_to_open()

    async def force_close(self):
        """Force circuit breaker to closed state (for testing/recovery)."""
        async with self._lock:
            await self._transition_to_closed()

    async def reset(self):
        """Reset circuit breaker metrics and state."""
        async with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.metrics = CircuitBreakerMetrics()


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.

    Manages circuit breakers for all services and provides
    centralized monitoring and control.
    """

    def __init__(self, default_config: CircuitBreakerConfig | None = None):
        """
        Initialize circuit breaker manager.

        Args:
            default_config: Default configuration for new circuit breakers
        """
        self.default_config = default_config or CircuitBreakerConfig()
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_circuit_breaker(self, service_info: ServiceInfo) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service.

        Args:
            service_info: Service information

        Returns:
            Circuit breaker for the service
        """
        service_id = str(service_info.id)

        if service_id not in self.circuit_breakers:
            async with self._lock:
                if service_id not in self.circuit_breakers:
                    self.circuit_breakers[service_id] = CircuitBreaker(
                        service_info, self.default_config
                    )

        return self.circuit_breakers[service_id]

    async def call_service(
        self,
        service_info: ServiceInfo,
        call_func: Callable,
        *args,
        therapeutic_request: bool = False,
        crisis_mode: bool = False,
        **kwargs,
    ) -> Any:
        """
        Make a call to a service through its circuit breaker.

        Args:
            service_info: Service information
            call_func: Function to call
            *args: Arguments for the function
            therapeutic_request: Whether this is a therapeutic request
            crisis_mode: Whether this is a crisis situation
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerError: If circuit breaker is open
        """
        circuit_breaker = await self.get_circuit_breaker(service_info)

        async with circuit_breaker.call(therapeutic_request, crisis_mode):
            if asyncio.iscoroutinefunction(call_func):
                return await call_func(*args, **kwargs)
            else:
                return call_func(*args, **kwargs)

    def get_all_circuit_breakers(self) -> dict[str, CircuitBreaker]:
        """Get all circuit breakers."""
        return self.circuit_breakers.copy()

    def get_healthy_services(self, services: list[ServiceInfo]) -> list[ServiceInfo]:
        """
        Filter services to only include those with healthy circuit breakers.

        Args:
            services: List of services to filter

        Returns:
            List of services with healthy circuit breakers
        """
        healthy_services = []

        for service in services:
            service_id = str(service.id)
            if service_id in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[service_id]
                if circuit_breaker.is_healthy():
                    healthy_services.append(service)
            else:
                # No circuit breaker means service hasn't been tested yet
                healthy_services.append(service)

        return healthy_services

    async def get_service_health_summary(self) -> dict[str, dict[str, Any]]:
        """
        Get health summary for all services.

        Returns:
            Dictionary with service health information
        """
        summary = {}

        for service_id, circuit_breaker in self.circuit_breakers.items():
            metrics = circuit_breaker.get_metrics()
            summary[service_id] = {
                "service_name": circuit_breaker.service_info.name,
                "state": circuit_breaker.get_state().value,
                "is_healthy": circuit_breaker.is_healthy(),
                "total_requests": metrics.total_requests,
                "success_rate": (
                    metrics.successful_requests / metrics.total_requests
                    if metrics.total_requests > 0
                    else 0
                ),
                "consecutive_failures": metrics.consecutive_failures,
                "consecutive_successes": metrics.consecutive_successes,
                "last_failure_time": metrics.last_failure_time,
                "last_success_time": metrics.last_success_time,
            }

        return summary


# Duplicate CircuitBreakerManager class removed - using the implementation above
