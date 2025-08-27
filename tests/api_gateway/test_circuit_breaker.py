"""
Tests for the API Gateway circuit breaker implementation.

This module contains unit tests for circuit breaker functionality
including state transitions, failure detection, and recovery logic.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.api_gateway.core.circuit_breaker import (
    CircuitBreaker, CircuitBreakerManager, CircuitBreakerState,
    CircuitBreakerConfig, CircuitBreakerError
)
from src.api_gateway.models import ServiceInfo, ServiceType, ServiceEndpoint


@pytest.fixture
def sample_service():
    """Create a sample service for testing."""
    return ServiceInfo(
        id=uuid4(),
        name="test-service",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8080),
        therapeutic_priority=False
    )


@pytest.fixture
def therapeutic_service():
    """Create a therapeutic service for testing."""
    return ServiceInfo(
        id=uuid4(),
        name="therapeutic-service",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8081),
        therapeutic_priority=True
    )


@pytest.fixture
def circuit_breaker_config():
    """Create circuit breaker configuration for testing."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=5.0,
        success_threshold=2,
        therapeutic_failure_threshold=2,
        therapeutic_recovery_timeout=2.0
    )


class TestCircuitBreaker:
    """Test cases for CircuitBreaker."""
    
    @pytest.mark.asyncio
    async def test_initial_state_closed(self, sample_service, circuit_breaker_config):
        """Test circuit breaker starts in closed state."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        assert cb.get_state() == CircuitBreakerState.CLOSED
        assert cb.is_healthy() is True
    
    @pytest.mark.asyncio
    async def test_successful_call(self, sample_service, circuit_breaker_config):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        async with cb.call():
            # Simulate successful operation
            pass
        
        metrics = cb.get_metrics()
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert cb.get_state() == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_failed_call(self, sample_service, circuit_breaker_config):
        """Test failed call through circuit breaker."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        with pytest.raises(Exception):
            async with cb.call():
                raise Exception("Test failure")
        
        metrics = cb.get_metrics()
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.consecutive_failures == 1
        assert cb.get_state() == CircuitBreakerState.CLOSED  # Still closed after 1 failure
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, sample_service, circuit_breaker_config):
        """Test circuit breaker opens after failure threshold."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Cause failures up to threshold
        for i in range(circuit_breaker_config.failure_threshold):
            with pytest.raises(Exception):
                async with cb.call():
                    raise Exception(f"Test failure {i+1}")
        
        assert cb.get_state() == CircuitBreakerState.OPEN
        assert cb.is_healthy() is False
    
    @pytest.mark.asyncio
    async def test_open_circuit_blocks_calls(self, sample_service, circuit_breaker_config):
        """Test open circuit breaker blocks calls."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Force circuit to open
        await cb.force_open()
        
        # Attempt to make call
        with pytest.raises(CircuitBreakerError):
            async with cb.call():
                pass
    
    @pytest.mark.asyncio
    async def test_crisis_bypass_open_circuit(self, sample_service, circuit_breaker_config):
        """Test crisis requests can bypass open circuit."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Force circuit to open
        await cb.force_open()
        
        # Crisis request should be allowed
        async with cb.call(crisis_mode=True):
            # Should not raise CircuitBreakerError
            pass
    
    @pytest.mark.asyncio
    async def test_half_open_transition(self, sample_service, circuit_breaker_config):
        """Test transition to half-open state after recovery timeout."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Force circuit to open
        await cb.force_open()
        
        # Simulate recovery timeout by manipulating last failure time
        cb.metrics.last_failure_time = 0.0  # Long time ago
        
        # Next call should transition to half-open
        async with cb.call():
            pass
        
        assert cb.get_state() == CircuitBreakerState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_half_open_to_closed_transition(self, sample_service, circuit_breaker_config):
        """Test transition from half-open to closed after successful calls."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Set to half-open state
        cb.state = CircuitBreakerState.HALF_OPEN
        
        # Make successful calls up to success threshold
        for i in range(circuit_breaker_config.success_threshold):
            async with cb.call():
                pass
        
        assert cb.get_state() == CircuitBreakerState.CLOSED
        assert cb.is_healthy() is True
    
    @pytest.mark.asyncio
    async def test_half_open_to_open_on_failure(self, sample_service, circuit_breaker_config):
        """Test transition from half-open to open on any failure."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Set to half-open state
        cb.state = CircuitBreakerState.HALF_OPEN
        
        # Any failure in half-open should open circuit
        with pytest.raises(Exception):
            async with cb.call():
                raise Exception("Test failure")
        
        assert cb.get_state() == CircuitBreakerState.OPEN
    
    @pytest.mark.asyncio
    async def test_therapeutic_service_lower_threshold(self, therapeutic_service, circuit_breaker_config):
        """Test therapeutic services use lower failure threshold."""
        cb = CircuitBreaker(therapeutic_service, circuit_breaker_config)
        
        # Should use therapeutic_failure_threshold (2) instead of regular threshold (3)
        for i in range(circuit_breaker_config.therapeutic_failure_threshold):
            with pytest.raises(Exception):
                async with cb.call(therapeutic_request=True):
                    raise Exception(f"Test failure {i+1}")
        
        assert cb.get_state() == CircuitBreakerState.OPEN
    
    @pytest.mark.asyncio
    async def test_reset_circuit_breaker(self, sample_service, circuit_breaker_config):
        """Test resetting circuit breaker."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Force some failures and open state
        await cb.force_open()
        
        # Reset
        await cb.reset()
        
        assert cb.get_state() == CircuitBreakerState.CLOSED
        metrics = cb.get_metrics()
        assert metrics.total_requests == 0
        assert metrics.consecutive_failures == 0


class TestCircuitBreakerManager:
    """Test cases for CircuitBreakerManager."""
    
    @pytest.mark.asyncio
    async def test_get_circuit_breaker_creates_new(self, sample_service):
        """Test getting circuit breaker creates new one if not exists."""
        manager = CircuitBreakerManager()
        
        cb = await manager.get_circuit_breaker(sample_service)
        
        assert isinstance(cb, CircuitBreaker)
        assert cb.service_info == sample_service
    
    @pytest.mark.asyncio
    async def test_get_circuit_breaker_returns_existing(self, sample_service):
        """Test getting circuit breaker returns existing one."""
        manager = CircuitBreakerManager()
        
        cb1 = await manager.get_circuit_breaker(sample_service)
        cb2 = await manager.get_circuit_breaker(sample_service)
        
        assert cb1 is cb2
    
    @pytest.mark.asyncio
    async def test_call_service_success(self, sample_service):
        """Test successful service call through manager."""
        manager = CircuitBreakerManager()
        
        async def test_func():
            return "success"
        
        result = await manager.call_service(
            sample_service, test_func
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_call_service_failure(self, sample_service):
        """Test failed service call through manager."""
        manager = CircuitBreakerManager()
        
        async def test_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            await manager.call_service(
                sample_service, test_func
            )
    
    @pytest.mark.asyncio
    async def test_call_service_with_therapeutic_context(self, therapeutic_service):
        """Test service call with therapeutic context."""
        manager = CircuitBreakerManager()
        
        async def test_func():
            return "therapeutic_success"
        
        result = await manager.call_service(
            therapeutic_service, test_func,
            therapeutic_request=True
        )
        
        assert result == "therapeutic_success"
    
    @pytest.mark.asyncio
    async def test_call_service_with_crisis_mode(self, therapeutic_service):
        """Test service call with crisis mode."""
        manager = CircuitBreakerManager()
        
        async def test_func():
            return "crisis_success"
        
        result = await manager.call_service(
            therapeutic_service, test_func,
            therapeutic_request=True,
            crisis_mode=True
        )
        
        assert result == "crisis_success"
    
    def test_get_healthy_services_filters_unhealthy(self, sample_service, therapeutic_service):
        """Test filtering of unhealthy services."""
        manager = CircuitBreakerManager()
        services = [sample_service, therapeutic_service]
        
        # Create circuit breakers with different health states
        manager.circuit_breakers[str(sample_service.id)] = MagicMock()
        manager.circuit_breakers[str(sample_service.id)].is_healthy.return_value = True
        
        manager.circuit_breakers[str(therapeutic_service.id)] = MagicMock()
        manager.circuit_breakers[str(therapeutic_service.id)].is_healthy.return_value = False
        
        healthy_services = manager.get_healthy_services(services)
        
        assert len(healthy_services) == 1
        assert healthy_services[0] == sample_service
    
    def test_get_healthy_services_includes_untested(self, sample_service):
        """Test that services without circuit breakers are considered healthy."""
        manager = CircuitBreakerManager()
        services = [sample_service]
        
        # No circuit breaker exists for the service
        healthy_services = manager.get_healthy_services(services)
        
        assert len(healthy_services) == 1
        assert healthy_services[0] == sample_service
    
    @pytest.mark.asyncio
    async def test_get_service_health_summary(self, sample_service, therapeutic_service):
        """Test getting service health summary."""
        manager = CircuitBreakerManager()
        
        # Create circuit breakers
        cb1 = await manager.get_circuit_breaker(sample_service)
        cb2 = await manager.get_circuit_breaker(therapeutic_service)
        
        # Simulate some metrics
        cb1.metrics.total_requests = 10
        cb1.metrics.successful_requests = 8
        cb2.metrics.total_requests = 5
        cb2.metrics.successful_requests = 5
        
        summary = await manager.get_service_health_summary()
        
        assert len(summary) == 2
        assert str(sample_service.id) in summary
        assert str(therapeutic_service.id) in summary
        
        # Check summary structure
        service_summary = summary[str(sample_service.id)]
        assert service_summary["service_name"] == sample_service.name
        assert service_summary["total_requests"] == 10
        assert service_summary["success_rate"] == 0.8


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_full_cycle(self, sample_service, circuit_breaker_config):
        """Test full circuit breaker cycle: closed -> open -> half-open -> closed."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        # Start in closed state
        assert cb.get_state() == CircuitBreakerState.CLOSED
        
        # Cause failures to open circuit
        for i in range(circuit_breaker_config.failure_threshold):
            with pytest.raises(Exception):
                async with cb.call():
                    raise Exception(f"Failure {i+1}")
        
        # Should be open now
        assert cb.get_state() == CircuitBreakerState.OPEN
        
        # Simulate recovery timeout
        cb.metrics.last_failure_time = 0.0
        
        # Next call should transition to half-open
        async with cb.call():
            pass
        
        assert cb.get_state() == CircuitBreakerState.HALF_OPEN
        
        # Make enough successful calls to close circuit
        for i in range(circuit_breaker_config.success_threshold - 1):  # -1 because we already made one
            async with cb.call():
                pass
        
        # Should be closed now
        assert cb.get_state() == CircuitBreakerState.CLOSED
        assert cb.is_healthy() is True
    
    @pytest.mark.asyncio
    async def test_concurrent_circuit_breaker_calls(self, sample_service, circuit_breaker_config):
        """Test concurrent calls through circuit breaker."""
        cb = CircuitBreaker(sample_service, circuit_breaker_config)
        
        async def successful_call():
            async with cb.call():
                await asyncio.sleep(0.01)  # Simulate work
                return "success"
        
        # Make concurrent calls
        tasks = [successful_call() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert all(result == "success" for result in results)
        
        metrics = cb.get_metrics()
        assert metrics.total_requests == 10
        assert metrics.successful_requests == 10
        assert metrics.failed_requests == 0
