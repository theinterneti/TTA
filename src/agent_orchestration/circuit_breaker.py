"""
Circuit breaker implementation for workflow error handling and graceful degradation.

Provides configurable failure detection, state management, and recovery mechanisms
for workflow components with Redis persistence for consistency across restarts.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Callable, Awaitable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states following the standard pattern."""
    CLOSED = "closed"      # Normal operation, failures counted
    OPEN = "open"          # Failing fast, not executing operations
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5
    timeout_seconds: int = 60
    recovery_timeout_seconds: int = 300
    half_open_max_calls: int = 3
    success_threshold: int = 2  # Successes needed in half-open to close


@dataclass
class CircuitBreakerMetrics:
    """Metrics tracking for circuit breaker operations."""
    total_calls: int = 0
    failed_calls: int = 0
    successful_calls: int = 0
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None


class CircuitBreaker:
    """
    Circuit breaker implementation with Redis persistence and configurable behavior.
    
    Follows the standard circuit breaker pattern with three states:
    - CLOSED: Normal operation, counting failures
    - OPEN: Failing fast, not executing operations
    - HALF_OPEN: Testing recovery with limited calls
    
    Redis keys (prefix pfx=ao by default):
      - {pfx}:cb:state:{name} -> JSON state record
      - {pfx}:cb:metrics:{name} -> JSON metrics record
    """
    
    def __init__(
        self,
        redis,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        key_prefix: str = "ao"
    ) -> None:
        self._redis = redis
        self._name = name
        self._config = config or CircuitBreakerConfig()
        self._pfx = key_prefix.rstrip(":")
        
        # Local state cache
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._last_failure_time: Optional[float] = None
        self._state_changed_at = time.time()
        
        # Metrics
        self._metrics = CircuitBreakerMetrics()
        
        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Metrics and logging integration
        self._correlation_id: Optional[str] = None
    
    # ---- Redis key helpers ----
    def _state_key(self) -> str:
        return f"{self._pfx}:cb:state:{self._name}"
    
    def _metrics_key(self) -> str:
        return f"{self._pfx}:cb:metrics:{self._name}"
    
    # ---- State persistence ----
    async def _load_state(self) -> None:
        """Load circuit breaker state from Redis."""
        try:
            data = await self._redis.get(self._state_key())
            if data:
                state_data = json.loads(data if isinstance(data, str) else data.decode())
                self._state = CircuitBreakerState(state_data.get("state", "closed"))
                self._failure_count = int(state_data.get("failure_count", 0))
                self._half_open_calls = int(state_data.get("half_open_calls", 0))
                self._half_open_successes = int(state_data.get("half_open_successes", 0))
                self._last_failure_time = state_data.get("last_failure_time")
                self._state_changed_at = float(state_data.get("state_changed_at", time.time()))
        except Exception as e:
            logger.debug(f"Failed to load circuit breaker state for {self._name}: {e}")
    
    async def _persist_state(self) -> None:
        """Persist circuit breaker state to Redis with TTL."""
        try:
            state_data = {
                "state": self._state.value,
                "failure_count": self._failure_count,
                "half_open_calls": self._half_open_calls,
                "half_open_successes": self._half_open_successes,
                "last_failure_time": self._last_failure_time,
                "state_changed_at": self._state_changed_at,
                "updated_at": time.time()
            }
            # TTL of 24 hours for state cleanup
            await self._redis.setex(
                self._state_key(),
                86400,
                json.dumps(state_data)
            )
        except Exception as e:
            logger.warning(f"Failed to persist circuit breaker state for {self._name}: {e}")
    
    async def _load_metrics(self) -> None:
        """Load metrics from Redis."""
        try:
            data = await self._redis.get(self._metrics_key())
            if data:
                metrics_data = json.loads(data if isinstance(data, str) else data.decode())
                self._metrics = CircuitBreakerMetrics(
                    total_calls=int(metrics_data.get("total_calls", 0)),
                    failed_calls=int(metrics_data.get("failed_calls", 0)),
                    successful_calls=int(metrics_data.get("successful_calls", 0)),
                    state_changes=int(metrics_data.get("state_changes", 0)),
                    last_failure_time=metrics_data.get("last_failure_time"),
                    last_success_time=metrics_data.get("last_success_time")
                )
        except Exception as e:
            logger.debug(f"Failed to load circuit breaker metrics for {self._name}: {e}")
    
    async def _persist_metrics(self) -> None:
        """Persist metrics to Redis with TTL."""
        try:
            metrics_data = {
                "total_calls": self._metrics.total_calls,
                "failed_calls": self._metrics.failed_calls,
                "successful_calls": self._metrics.successful_calls,
                "state_changes": self._metrics.state_changes,
                "last_failure_time": self._metrics.last_failure_time,
                "last_success_time": self._metrics.last_success_time,
                "updated_at": time.time()
            }
            # TTL of 7 days for metrics
            await self._redis.setex(
                self._metrics_key(),
                604800,
                json.dumps(metrics_data)
            )
        except Exception as e:
            logger.warning(f"Failed to persist circuit breaker metrics for {self._name}: {e}")
    
    # ---- State management ----
    async def _transition_to_open(self) -> None:
        """Transition circuit breaker to OPEN state."""
        if self._state != CircuitBreakerState.OPEN:
            old_state = self._state
            self._state = CircuitBreakerState.OPEN
            self._state_changed_at = time.time()
            self._metrics.state_changes += 1

            # Record metrics and log transition
            from .circuit_breaker_metrics import record_state_transition
            record_state_transition(self._name, old_state, self._state, self._correlation_id)

            logger.warning(
                f"Circuit breaker {self._name} transitioning to OPEN state",
                extra={
                    "circuit_breaker_name": self._name,
                    "from_state": old_state.value,
                    "to_state": self._state.value,
                    "correlation_id": self._correlation_id,
                    "failure_count": self._failure_count,
                    "event_type": "circuit_breaker_opened"
                }
            )

            await self._persist_state()
            await self._persist_metrics()
    
    async def _transition_to_half_open(self) -> None:
        """Transition circuit breaker to HALF_OPEN state."""
        if self._state != CircuitBreakerState.HALF_OPEN:
            old_state = self._state
            self._state = CircuitBreakerState.HALF_OPEN
            self._half_open_calls = 0
            self._half_open_successes = 0
            self._state_changed_at = time.time()
            self._metrics.state_changes += 1

            # Record metrics and log transition
            from .circuit_breaker_metrics import record_state_transition
            record_state_transition(self._name, old_state, self._state, self._correlation_id)

            logger.info(
                f"Circuit breaker {self._name} transitioning to HALF_OPEN state",
                extra={
                    "circuit_breaker_name": self._name,
                    "from_state": old_state.value,
                    "to_state": self._state.value,
                    "correlation_id": self._correlation_id,
                    "event_type": "circuit_breaker_half_opened"
                }
            )

            await self._persist_state()
            await self._persist_metrics()
    
    async def _transition_to_closed(self) -> None:
        """Transition circuit breaker to CLOSED state."""
        if self._state != CircuitBreakerState.CLOSED:
            old_state = self._state
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0
            self._half_open_successes = 0
            self._state_changed_at = time.time()
            self._metrics.state_changes += 1

            # Record metrics and log transition
            from .circuit_breaker_metrics import record_state_transition
            record_state_transition(self._name, old_state, self._state, self._correlation_id)

            logger.info(
                f"Circuit breaker {self._name} transitioning to CLOSED state",
                extra={
                    "circuit_breaker_name": self._name,
                    "from_state": old_state.value,
                    "to_state": self._state.value,
                    "correlation_id": self._correlation_id,
                    "event_type": "circuit_breaker_closed"
                }
            )

            await self._persist_state()
            await self._persist_metrics()
    
    # ---- Public API ----
    async def initialize(self) -> None:
        """Initialize circuit breaker by loading state from Redis."""
        async with self._lock:
            await self._load_state()
            await self._load_metrics()
    
    async def call(self, func: Callable[[], Awaitable[Any]], correlation_id: Optional[str] = None) -> Any:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to execute
            correlation_id: Optional correlation ID for logging

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerOpenError: When circuit breaker is open
            Exception: Any exception raised by the function
        """
        # Set correlation ID for this operation
        self._correlation_id = correlation_id or str(uuid.uuid4())
        start_time = time.time()

        from .circuit_breaker_metrics import get_circuit_breaker_metrics
        metrics_collector = get_circuit_breaker_metrics()

        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitBreakerState.OPEN:
                if time.time() - self._state_changed_at >= self._config.timeout_seconds:
                    await self._transition_to_half_open()
                else:
                    self._metrics.total_calls += 1
                    await self._persist_metrics()
                    metrics_collector.record_call_rejected(
                        self._name, "circuit_breaker_open", self._correlation_id
                    )
                    raise CircuitBreakerOpenError(f"Circuit breaker {self._name} is OPEN")

            # Check if we should limit calls in HALF_OPEN state
            if self._state == CircuitBreakerState.HALF_OPEN:
                if self._half_open_calls >= self._config.half_open_max_calls:
                    self._metrics.total_calls += 1
                    await self._persist_metrics()
                    metrics_collector.record_call_rejected(
                        self._name, "half_open_max_calls_reached", self._correlation_id
                    )
                    raise CircuitBreakerOpenError(f"Circuit breaker {self._name} is HALF_OPEN with max calls reached")
                self._half_open_calls += 1

            # Record call permitted
            metrics_collector.record_call_permitted(self._name, self._correlation_id)

        # Execute the function
        self._metrics.total_calls += 1
        try:
            result = await func()
            duration_ms = (time.time() - start_time) * 1000
            await self._record_success()
            metrics_collector.record_successful_call(self._name, duration_ms, self._correlation_id)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            await self._record_failure()
            metrics_collector.record_failed_call(self._name, str(e), duration_ms, self._correlation_id)
            raise
    
    async def _record_success(self) -> None:
        """Record a successful operation."""
        async with self._lock:
            self._metrics.successful_calls += 1
            self._metrics.last_success_time = time.time()
            
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self._config.success_threshold:
                    await self._transition_to_closed()
            
            await self._persist_metrics()
    
    async def _record_failure(self) -> None:
        """Record a failed operation."""
        async with self._lock:
            self._metrics.failed_calls += 1
            self._metrics.last_failure_time = time.time()
            self._last_failure_time = time.time()
            
            if self._state == CircuitBreakerState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self._config.failure_threshold:
                    await self._transition_to_open()
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open state transitions back to open
                await self._transition_to_open()
            
            await self._persist_state()
            await self._persist_metrics()
    
    # ---- Status and metrics ----
    async def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        async with self._lock:
            return self._state
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        async with self._lock:
            return {
                "name": self._name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "total_calls": self._metrics.total_calls,
                "failed_calls": self._metrics.failed_calls,
                "successful_calls": self._metrics.successful_calls,
                "state_changes": self._metrics.state_changes,
                "last_failure_time": self._metrics.last_failure_time,
                "last_success_time": self._metrics.last_success_time,
                "state_changed_at": self._state_changed_at,
                "config": {
                    "failure_threshold": self._config.failure_threshold,
                    "timeout_seconds": self._config.timeout_seconds,
                    "recovery_timeout_seconds": self._config.recovery_timeout_seconds
                }
            }
    
    async def is_call_permitted(self) -> bool:
        """Check if a call would be permitted without executing it."""
        async with self._lock:
            if self._state == CircuitBreakerState.CLOSED:
                return True
            elif self._state == CircuitBreakerState.OPEN:
                return time.time() - self._state_changed_at >= self._config.timeout_seconds
            elif self._state == CircuitBreakerState.HALF_OPEN:
                return self._half_open_calls < self._config.half_open_max_calls
            return False
    
    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            logger.info(f"Manually resetting circuit breaker {self._name}")
            await self._transition_to_closed()


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass
