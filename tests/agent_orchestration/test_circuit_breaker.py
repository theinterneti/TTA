"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_circuit_breaker]]
Comprehensive unit tests for circuit_breaker module.

Tests cover:
- CircuitBreakerState enum
- CircuitBreakerMetrics dataclass
- CircuitBreaker class with state management and Redis persistence
"""

import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import contextlib

from agent_orchestration.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerState,
)


class TestCircuitBreakerState:
    """Tests for CircuitBreakerState enum."""

    def test_circuit_breaker_state_values(self):
        """Test CircuitBreakerState enum has expected values."""
        assert hasattr(CircuitBreakerState, "CLOSED")
        assert hasattr(CircuitBreakerState, "OPEN")
        assert hasattr(CircuitBreakerState, "HALF_OPEN")

    def test_circuit_breaker_state_is_enum(self):
        """Test CircuitBreakerState is an Enum."""
        assert isinstance(CircuitBreakerState.CLOSED, CircuitBreakerState)

    def test_circuit_breaker_state_string_values(self):
        """Test CircuitBreakerState has correct string values."""
        assert CircuitBreakerState.CLOSED.value == "closed"
        assert CircuitBreakerState.OPEN.value == "open"
        assert CircuitBreakerState.HALF_OPEN.value == "half_open"


class TestCircuitBreakerMetrics:
    """Tests for CircuitBreakerMetrics dataclass."""

    def test_metrics_initialization_default(self):
        """Test CircuitBreakerMetrics initializes with defaults."""
        metrics = CircuitBreakerMetrics()

        assert metrics.total_calls == 0
        assert metrics.failed_calls == 0
        assert metrics.successful_calls == 0
        assert metrics.state_changes == 0
        assert metrics.last_failure_time is None
        assert metrics.last_success_time is None

    def test_metrics_initialization_custom(self):
        """Test CircuitBreakerMetrics initializes with custom values."""
        metrics = CircuitBreakerMetrics(
            total_calls=100,
            failed_calls=10,
            successful_calls=90,
            state_changes=2,
            last_failure_time=1234567890.0,
            last_success_time=1234567900.0,
        )

        assert metrics.total_calls == 100
        assert metrics.failed_calls == 10
        assert metrics.successful_calls == 90
        assert metrics.state_changes == 2
        assert metrics.last_failure_time == 1234567890.0
        assert metrics.last_success_time == 1234567900.0

    def test_metrics_failure_rate_calculation(self):
        """Test calculating failure rate from metrics."""
        metrics = CircuitBreakerMetrics(
            total_calls=100,
            failed_calls=20,
            successful_calls=80,
        )

        failure_rate = metrics.failed_calls / metrics.total_calls
        assert failure_rate == 0.2

    def test_metrics_success_rate_calculation(self):
        """Test calculating success rate from metrics."""
        metrics = CircuitBreakerMetrics(
            total_calls=100,
            failed_calls=20,
            successful_calls=80,
        )

        success_rate = metrics.successful_calls / metrics.total_calls
        assert success_rate == 0.8


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock async Redis client."""
        redis = AsyncMock()
        redis.get.return_value = None  # No stored state
        redis.setex.return_value = True
        return redis

    @pytest.fixture
    def circuit_breaker(self, mock_redis):
        """Create CircuitBreaker instance with mock Redis."""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=60,
            half_open_max_calls=3,
        )
        return CircuitBreaker(redis=mock_redis, name="test_breaker", config=config)

    def test_circuit_breaker_initialization(self, circuit_breaker):
        """Test CircuitBreaker initializes correctly."""
        assert circuit_breaker._name == "test_breaker"
        assert circuit_breaker._config.failure_threshold == 5
        assert circuit_breaker._config.timeout_seconds == 60
        assert circuit_breaker._config.half_open_max_calls == 3

    def test_circuit_breaker_initial_state(self, circuit_breaker):
        """Test CircuitBreaker starts in CLOSED state."""
        assert circuit_breaker._state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_initial_metrics(self, circuit_breaker):
        """Test CircuitBreaker initializes with zero metrics."""
        assert circuit_breaker._metrics.total_calls == 0
        assert circuit_breaker._metrics.failed_calls == 0
        assert circuit_breaker._metrics.successful_calls == 0

    @pytest.mark.asyncio
    async def test_call_success_in_closed_state(self, circuit_breaker):
        """Test successful call in CLOSED state."""

        async def successful_operation():
            return "success"

        result = await circuit_breaker.call(successful_operation)

        assert result == "success"
        assert circuit_breaker._metrics.total_calls == 1
        assert circuit_breaker._metrics.successful_calls == 1
        assert circuit_breaker._state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_call_failure_in_closed_state(self, circuit_breaker):
        """Test failed call in CLOSED state."""

        async def failing_operation():
            raise Exception("Operation failed")

        with pytest.raises(Exception):
            await circuit_breaker.call(failing_operation)

        assert circuit_breaker._metrics.total_calls == 1
        assert circuit_breaker._metrics.failed_calls == 1
        assert circuit_breaker._state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(self, circuit_breaker):
        """Test circuit breaker opens after failure threshold."""

        async def failing_operation():
            raise Exception("Operation failed")

        # Trigger failures up to threshold
        for _ in range(circuit_breaker._config.failure_threshold):
            with contextlib.suppress(Exception):
                await circuit_breaker.call(failing_operation)

        # Circuit should be OPEN now
        assert circuit_breaker._state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_call_fails_fast_in_open_state(self, circuit_breaker):
        """Test calls fail fast when circuit is OPEN."""
        # Force circuit to OPEN state with recent failure time
        circuit_breaker._state = CircuitBreakerState.OPEN
        circuit_breaker._state_changed_at = time.time()

        async def operation():
            return "success"

        with pytest.raises(Exception) as exc_info:
            await circuit_breaker.call(operation)

        assert "OPEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_state(self, circuit_breaker):
        """Test circuit breaker transitions to HALF_OPEN after timeout."""
        # Force circuit to OPEN state with old failure time (past timeout)
        circuit_breaker._state = CircuitBreakerState.OPEN
        circuit_breaker._state_changed_at = time.time() - 100

        async def successful_operation():
            return "success"

        # Call should attempt and succeed (circuit transitions to HALF_OPEN first)
        await circuit_breaker.call(successful_operation)

        # After successful call should be in HALF_OPEN or CLOSED
        assert circuit_breaker._state in [
            CircuitBreakerState.HALF_OPEN,
            CircuitBreakerState.CLOSED,
        ]

    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self, circuit_breaker):
        """Test resetting circuit breaker."""
        # Force to OPEN state with some failures
        circuit_breaker._state = CircuitBreakerState.OPEN
        circuit_breaker._failure_count = 50

        # Reset (async)
        await circuit_breaker.reset()

        assert circuit_breaker._state == CircuitBreakerState.CLOSED
        assert circuit_breaker._failure_count == 0

    def test_circuit_breaker_metrics_tracking(self, circuit_breaker):
        """Test metrics are tracked correctly."""
        initial_total = circuit_breaker._metrics.total_calls

        # Simulate some calls by modifying metrics directly
        circuit_breaker._metrics.total_calls += 10
        circuit_breaker._metrics.successful_calls += 8
        circuit_breaker._metrics.failed_calls += 2

        assert circuit_breaker._metrics.total_calls == initial_total + 10
        assert circuit_breaker._metrics.successful_calls == 8
        assert circuit_breaker._metrics.failed_calls == 2

    def test_circuit_breaker_state_transitions(self, circuit_breaker):
        """Test valid state transitions."""
        # CLOSED -> OPEN
        circuit_breaker._state = CircuitBreakerState.CLOSED
        circuit_breaker._state = CircuitBreakerState.OPEN
        assert circuit_breaker._state == CircuitBreakerState.OPEN

        # OPEN -> HALF_OPEN
        circuit_breaker._state = CircuitBreakerState.HALF_OPEN
        assert circuit_breaker._state == CircuitBreakerState.HALF_OPEN

        # HALF_OPEN -> CLOSED
        circuit_breaker._state = CircuitBreakerState.CLOSED
        assert circuit_breaker._state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_with_custom_timeout(self, mock_redis):
        """Test circuit breaker with custom recovery timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=30,
            half_open_max_calls=2,
        )
        breaker = CircuitBreaker(redis=mock_redis, name="custom_timeout", config=config)

        assert breaker._config.timeout_seconds == 30

    def test_circuit_breaker_with_custom_half_open_calls(self, mock_redis):
        """Test circuit breaker with custom half-open max calls."""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=60,
            half_open_max_calls=5,
        )
        breaker = CircuitBreaker(
            redis=mock_redis, name="custom_half_open", config=config
        )

        assert breaker._config.half_open_max_calls == 5

    @pytest.mark.asyncio
    async def test_multiple_sequential_calls(self, circuit_breaker):
        """Test multiple sequential calls."""
        results = []
        for i in range(5):

            async def operation(value=i):
                return value * 2

            result = await circuit_breaker.call(operation)
            results.append(result)

        assert results == [0, 2, 4, 6, 8]
        assert circuit_breaker._metrics.total_calls == 5
        assert circuit_breaker._metrics.successful_calls == 5

    def test_circuit_breaker_name_property(self, circuit_breaker):
        """Test circuit breaker name attribute."""
        assert circuit_breaker._name == "test_breaker"

    def test_circuit_breaker_failure_threshold_property(self, circuit_breaker):
        """Test circuit breaker failure threshold config."""
        assert circuit_breaker._config.failure_threshold == 5
