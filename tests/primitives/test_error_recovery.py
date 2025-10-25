"""
Tests for Error Recovery Framework

Tests cover:
- Retry decorator with various configurations
- Error classification (network, rate limit, transient, permanent)
- Exponential backoff calculation with jitter
- Circuit breaker state transitions
- Fallback function execution
- Async retry decorator
"""

# Import from scripts/primitives/
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "primitives"))

from error_recovery import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
    ErrorCategory,
    RetryConfig,
    calculate_delay,
    classify_error,
    should_retry,
    with_retry,
    with_retry_async,
)


class TestErrorClassification:
    """Test error classification logic."""

    def test_classify_network_error(self):
        """Test classification of network errors."""
        error = ConnectionError("Connection timeout")
        category, severity = classify_error(error)

        assert category == ErrorCategory.NETWORK

    def test_classify_rate_limit_error(self):
        """Test classification of rate limit errors."""
        error = Exception("Rate limit exceeded")
        category, severity = classify_error(error)

        assert category == ErrorCategory.RATE_LIMIT

    def test_classify_transient_error(self):
        """Test classification of transient errors."""
        error = Exception("Service temporarily unavailable")
        category, severity = classify_error(error)

        assert category == ErrorCategory.TRANSIENT

    def test_classify_permanent_error(self):
        """Test classification of permanent errors."""
        error = ValueError("Invalid input")
        category, severity = classify_error(error)

        assert category == ErrorCategory.PERMANENT


class TestShouldRetry:
    """Test retry decision logic."""

    def test_should_retry_network_error(self):
        """Test that network errors should be retried."""
        error = ConnectionError("Connection timeout")

        assert should_retry(error, attempt=0, max_retries=3) is True

    def test_should_retry_permanent_error(self):
        """Test that permanent errors should not be retried."""
        error = ValueError("Invalid input")

        assert should_retry(error, attempt=0, max_retries=3) is False

    def test_should_not_retry_after_max_attempts(self):
        """Test that retries stop after max attempts."""
        error = ConnectionError("Connection timeout")

        assert should_retry(error, attempt=3, max_retries=3) is False


class TestDelayCalculation:
    """Test exponential backoff delay calculation."""

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)

        delay0 = calculate_delay(0, config)
        delay1 = calculate_delay(1, config)
        delay2 = calculate_delay(2, config)

        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(
            base_delay=1.0, max_delay=5.0, exponential_base=2.0, jitter=False
        )

        delay10 = calculate_delay(10, config)

        assert delay10 == 5.0

    def test_jitter_adds_randomness(self):
        """Test that jitter adds randomness to delay."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=True)

        delays = [calculate_delay(1, config) for _ in range(10)]

        # With jitter, delays should vary
        assert len(set(delays)) > 1

        # All delays should be in range [1.0, 3.0] (2.0 * [0.5, 1.5])
        assert all(1.0 <= d <= 3.0 for d in delays)


class TestRetryDecorator:
    """Test retry decorator functionality."""

    def test_retry_success_on_first_attempt(self):
        """Test successful execution on first attempt."""
        call_count = 0

        @with_retry()
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()

        assert result == "success"
        assert call_count == 1

    def test_retry_success_on_second_attempt(self):
        """Test successful execution on second attempt."""
        call_count = 0

        @with_retry(RetryConfig(max_retries=3, base_delay=0.01))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient failure")
            return "success"

        result = flaky_function()

        assert result == "success"
        assert call_count == 2

    def test_retry_exhausted(self):
        """Test that exception is raised after max retries."""
        call_count = 0

        @with_retry(RetryConfig(max_retries=3, base_delay=0.01))
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_fails()

        assert call_count == 4  # Initial + 3 retries

    def test_retry_permanent_error_no_retry(self):
        """Test that permanent errors are not retried."""
        call_count = 0

        @with_retry(RetryConfig(max_retries=3, base_delay=0.01))
        def permanent_failure():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent error")

        with pytest.raises(ValueError):
            permanent_failure()

        assert call_count == 1  # No retries for permanent errors

    def test_retry_with_fallback(self):
        """Test retry with fallback function."""
        call_count = 0

        def fallback_function():
            return "fallback"

        @with_retry(
            RetryConfig(max_retries=2, base_delay=0.01), fallback=fallback_function
        )
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        result = always_fails()

        assert result == "fallback"
        assert call_count == 3  # Initial + 2 retries

    def test_retry_custom_config(self):
        """Test retry with custom configuration."""
        call_count = 0

        @with_retry(RetryConfig(max_retries=5, base_delay=0.01))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise ConnectionError("Transient failure")
            return "success"

        result = flaky_function()

        assert result == "success"
        assert call_count == 4


class TestAsyncRetryDecorator:
    """Test async retry decorator functionality."""

    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Test async retry with successful execution."""
        call_count = 0

        @with_retry_async(RetryConfig(max_retries=3, base_delay=0.01))
        async def async_flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient failure")
            return "success"

        result = await async_flaky_function()

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retry_exhausted(self):
        """Test async retry with exhausted retries."""
        call_count = 0

        @with_retry_async(RetryConfig(max_retries=2, base_delay=0.01))
        async def async_always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            await async_always_fails()

        assert call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_async_retry_with_fallback(self):
        """Test async retry with fallback function."""
        call_count = 0

        async def async_fallback():
            return "fallback"

        @with_retry_async(
            RetryConfig(max_retries=2, base_delay=0.01), fallback=async_fallback
        )
        async def async_always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        result = await async_always_fails()

        assert result == "fallback"
        assert call_count == 3


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

        def successful_function():
            return "success"

        result = circuit_breaker.call(successful_function)

        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

        def failing_function():
            raise Exception("Failure")

        # Trigger failures to open circuit
        for _ in range(3):
            try:
                circuit_breaker.call(failing_function)
            except Exception:
                pass

        assert circuit_breaker.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_rejects_when_open(self):
        """Test circuit breaker rejects calls when open."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)

        def failing_function():
            raise Exception("Failure")

        # Open the circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_function)
            except Exception:
                pass

        # Should reject next call
        with pytest.raises(CircuitBreakerOpenError):
            circuit_breaker.call(failing_function)

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker enters half-open state after timeout."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        def failing_function():
            raise Exception("Failure")

        # Open the circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_function)
            except Exception:
                pass

        # Wait for recovery timeout
        time.sleep(0.2)

        # Should be in half-open state (allows one test call)
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_breaker_closes_on_success(self):
        """Test circuit breaker closes on successful call in half-open state."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        def failing_function():
            raise Exception("Failure")

        def successful_function():
            return "success"

        # Open the circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_function)
            except Exception:
                pass

        # Wait for recovery timeout
        time.sleep(0.2)

        # Successful call should close circuit
        result = circuit_breaker.call(successful_function)

        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
