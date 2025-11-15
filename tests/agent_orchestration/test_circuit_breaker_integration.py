"""
Integration tests for circuit breaker functionality.

Tests the complete circuit breaker system including state transitions,
metrics collection, and integration with workflow error handling.
"""

import asyncio

import pytest
from tta_ai.orchestration.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)
from tta_ai.orchestration.circuit_breaker_metrics import get_circuit_breaker_metrics
from tta_ai.orchestration.circuit_breaker_registry import CircuitBreakerRegistry
from tta_ai.orchestration.resource_exhaustion_detector import (
    ResourceExhaustionDetector,
    ResourceExhaustionEvent,
    ResourceThresholds,
)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_basic_functionality(redis_client):
    """Test basic circuit breaker functionality."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        timeout_seconds=1,
        recovery_timeout_seconds=2,
        half_open_max_calls=1,
        success_threshold=1,
    )

    cb = CircuitBreaker(redis_client, "test_cb", config, key_prefix="test")
    await cb.initialize()

    # Test successful call
    async def success_func():
        return "success"

    result = await cb.call(success_func)
    assert result == "success"

    # Test failure leading to open state
    async def failure_func():
        raise Exception("test failure")

    # First failure
    with pytest.raises(Exception, match="test failure"):
        await cb.call(failure_func)

    # Second failure should open circuit
    with pytest.raises(Exception, match="test failure"):
        await cb.call(failure_func)

    # Circuit should now be open
    state = await cb.get_state()
    assert state == CircuitBreakerState.OPEN

    # Calls should be rejected
    with pytest.raises(CircuitBreakerOpenError):
        await cb.call(success_func)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_registry(redis_client):
    """Test circuit breaker registry functionality."""
    registry = CircuitBreakerRegistry(redis_client, key_prefix="test_registry")

    # Create circuit breakers
    cb1 = await registry.get_or_create("test_cb1")
    cb2 = await registry.get_or_create("test_cb2")

    assert cb1 is not None
    assert cb2 is not None

    # Test listing
    names = await registry.list_names()
    assert "test_cb1" in names
    assert "test_cb2" in names

    # Test metrics
    metrics = await registry.get_all_metrics()
    assert "test_cb1" in metrics
    assert "test_cb2" in metrics

    # Test removal
    removed = await registry.remove("test_cb1")
    assert removed is True

    names_after = await registry.list_names()
    assert "test_cb1" not in names_after
    assert "test_cb2" in names_after


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions(redis_client):
    """Test circuit breaker state transitions and recovery."""
    config = CircuitBreakerConfig(
        failure_threshold=1,
        timeout_seconds=0.1,  # Very short timeout for testing
        recovery_timeout_seconds=0.2,
        half_open_max_calls=1,
        success_threshold=1,
    )

    cb = CircuitBreaker(redis_client, "state_test", config, key_prefix="test")
    await cb.initialize()

    # Start in CLOSED state
    assert await cb.get_state() == CircuitBreakerState.CLOSED

    # Trigger failure to open circuit
    async def failure_func():
        raise Exception("test failure")

    with pytest.raises(Exception):
        await cb.call(failure_func)

    # Should be OPEN now
    assert await cb.get_state() == CircuitBreakerState.OPEN

    # Wait for timeout to allow transition to HALF_OPEN
    await asyncio.sleep(0.15)

    # Next call should transition to HALF_OPEN
    async def success_func():
        return "success"

    result = await cb.call(success_func)
    assert result == "success"

    # Should be CLOSED now after successful call in HALF_OPEN
    assert await cb.get_state() == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_resource_exhaustion_detector():
    """Test resource exhaustion detector functionality."""
    thresholds = ResourceThresholds(
        memory_warning_percent=50.0,
        memory_critical_percent=60.0,
        memory_exhaustion_percent=70.0,
        cpu_warning_percent=50.0,
        cpu_critical_percent=60.0,
        cpu_exhaustion_percent=70.0,
        sustained_duration_seconds=0.1,
    )

    detector = ResourceExhaustionDetector(thresholds, check_interval_seconds=0.05)

    # Test callback registration
    events_received = []

    async def test_callback(event: ResourceExhaustionEvent):
        events_received.append(event)

    detector.register_warning_callback(test_callback)
    detector.register_exhaustion_callback(test_callback)

    # Get current status
    status = detector.get_current_status()
    assert "monitoring_active" in status
    assert "current_usage" in status
    assert "thresholds" in status

    # Test manual check (this will depend on actual system resources)
    events = await detector.check_resource_exhaustion()
    # Events list may be empty if system resources are below thresholds
    assert isinstance(events, list)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_metrics_integration(redis_client):
    """Test circuit breaker metrics collection."""
    config = CircuitBreakerConfig(failure_threshold=1)
    cb = CircuitBreaker(redis_client, "metrics_test", config, key_prefix="test")
    await cb.initialize()

    # Get initial metrics
    metrics_collector = get_circuit_breaker_metrics()
    initial_snapshot = metrics_collector.get_snapshot()

    # Perform operations
    async def success_func():
        return "success"

    async def failure_func():
        raise Exception("test failure")

    # Successful call
    await cb.call(success_func, correlation_id="test-correlation-1")

    # Failed call
    with pytest.raises(Exception):
        await cb.call(failure_func, correlation_id="test-correlation-2")

    # Check metrics were updated
    final_snapshot = metrics_collector.get_snapshot()
    assert final_snapshot["successful_calls"] > initial_snapshot["successful_calls"]
    assert final_snapshot["failed_calls"] > initial_snapshot["failed_calls"]


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_persistence(redis_client):
    """Test circuit breaker state persistence across instances."""
    config = CircuitBreakerConfig(failure_threshold=1)

    # Create first instance and trigger failure
    cb1 = CircuitBreaker(redis_client, "persistence_test", config, key_prefix="test")
    await cb1.initialize()

    async def failure_func():
        raise Exception("test failure")

    with pytest.raises(Exception):
        await cb1.call(failure_func)

    # Circuit should be open
    assert await cb1.get_state() == CircuitBreakerState.OPEN

    # Create second instance with same name
    cb2 = CircuitBreaker(redis_client, "persistence_test", config, key_prefix="test")
    await cb2.initialize()

    # Should load the open state from Redis
    assert await cb2.get_state() == CircuitBreakerState.OPEN

    # Should reject calls
    async def success_func():
        return "success"

    with pytest.raises(CircuitBreakerOpenError):
        await cb2.call(success_func)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_cleanup(redis_client):
    """Test circuit breaker cleanup functionality."""
    registry = CircuitBreakerRegistry(redis_client, key_prefix="test_cleanup")

    # Create some circuit breakers
    await registry.get_or_create("cleanup_test1")
    await registry.get_or_create("cleanup_test2")

    # Verify they exist
    names = await registry.list_names()
    assert "cleanup_test1" in names
    assert "cleanup_test2" in names

    # Test cleanup
    cleaned = await registry.cleanup_expired_states()
    # Should be 0 since states are fresh
    assert cleaned >= 0

    # Test registry stats
    stats = await registry.get_registry_stats()
    assert "total_circuit_breakers" in stats
    assert "state_counts" in stats
    assert stats["total_circuit_breakers"] >= 2


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_execute_method(redis_client):
    """Test circuit breaker execute method with arguments."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        timeout_seconds=1,
        recovery_timeout_seconds=2,
        half_open_max_calls=1,
        success_threshold=1,
    )

    cb = CircuitBreaker(redis_client, "execute_test", config, key_prefix="test")
    await cb.initialize()

    # Test execute with arguments
    async def add_func(a, b):
        return a + b

    result = await cb.execute(add_func, 2, 3)
    assert result == 5

    # Test execute with keyword arguments
    async def greet_func(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    result = await cb.execute(greet_func, "World", greeting="Hi")
    assert result == "Hi, World!"

    # Test execute with failure
    async def failure_func(msg):
        raise ValueError(msg)

    with pytest.raises(ValueError, match="test error"):
        await cb.execute(failure_func, "test error")


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_execute_state_transitions(redis_client):
    """Test circuit breaker execute method with state transitions."""
    config = CircuitBreakerConfig(
        failure_threshold=1,
        timeout_seconds=0.1,
        recovery_timeout_seconds=0.2,
        half_open_max_calls=1,
        success_threshold=1,
    )

    cb = CircuitBreaker(redis_client, "execute_state_test", config, key_prefix="test")
    await cb.initialize()

    # Start in CLOSED state
    assert await cb.get_state() == CircuitBreakerState.CLOSED

    # Trigger failure to open circuit
    async def failure_func(msg):
        raise Exception(msg)

    with pytest.raises(Exception, match="test failure"):
        await cb.execute(failure_func, "test failure")

    # Should be OPEN now
    assert await cb.get_state() == CircuitBreakerState.OPEN

    # Calls should be rejected
    async def success_func(value):
        return value

    with pytest.raises(CircuitBreakerOpenError):
        await cb.execute(success_func, "test")

    # Wait for timeout to allow transition to HALF_OPEN
    await asyncio.sleep(0.15)

    # Next call should transition to HALF_OPEN and succeed
    result = await cb.execute(success_func, "recovered")
    assert result == "recovered"

    # Should be CLOSED now after successful call in HALF_OPEN
    assert await cb.get_state() == CircuitBreakerState.CLOSED


@pytest.mark.redis
@pytest.mark.asyncio
async def test_circuit_breaker_execute_with_metrics(redis_client):
    """Test circuit breaker execute method metrics collection."""
    config = CircuitBreakerConfig(failure_threshold=2)
    cb = CircuitBreaker(redis_client, "execute_metrics_test", config, key_prefix="test")
    await cb.initialize()

    # Get initial metrics
    metrics_collector = get_circuit_breaker_metrics()
    initial_snapshot = metrics_collector.get_snapshot()

    # Perform operations with execute
    async def success_func(value):
        return value * 2

    async def failure_func(msg):
        raise Exception(msg)

    # Successful calls
    result1 = await cb.execute(success_func, 5)
    assert result1 == 10

    result2 = await cb.execute(success_func, 10)
    assert result2 == 20

    # Failed call
    with pytest.raises(Exception):
        await cb.execute(failure_func, "test error")

    # Check metrics were updated
    final_snapshot = metrics_collector.get_snapshot()
    assert final_snapshot["successful_calls"] > initial_snapshot["successful_calls"]
    assert final_snapshot["failed_calls"] > initial_snapshot["failed_calls"]


if __name__ == "__main__":
    # Run a simple test if executed directly
    import redis.asyncio as aioredis

    async def simple_test():
        redis_client = aioredis.from_url("redis://localhost:6379/0")

        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(redis_client, "simple_test", config)
        await cb.initialize()

        async def test_func():
            return "Hello, Circuit Breaker!"

        await cb.call(test_func)

        await cb.get_metrics()

        await redis_client.close()

    asyncio.run(simple_test())
