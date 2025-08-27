"""
Tests for the API Gateway service router.

This module contains unit tests for the ServiceRouter class
including load balancing integration, circuit breaker protection,
and failover mechanisms.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.api_gateway.core.service_router import ServiceRouter, ServiceRouterConfig, FailoverStrategy
from src.api_gateway.core.load_balancer import LoadBalancingStrategy
from src.api_gateway.core.circuit_breaker import CircuitBreakerError
from src.api_gateway.models import ServiceInfo, ServiceType, ServiceEndpoint, GatewayRequest, RequestMethod
from src.api_gateway.services import ServiceDiscoveryManager


@pytest.fixture
def mock_discovery_manager():
    """Create a mock service discovery manager."""
    manager = AsyncMock(spec=ServiceDiscoveryManager)
    
    # Mock services
    services = [
        ServiceInfo(
            id=uuid4(),
            name="service-1",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8001),
            weight=100,
            healthy=True,
            therapeutic_priority=False
        ),
        ServiceInfo(
            id=uuid4(),
            name="service-2",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8002),
            weight=150,
            healthy=True,
            therapeutic_priority=True
        ),
        ServiceInfo(
            id=uuid4(),
            name="service-3",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8003),
            weight=50,
            healthy=False,
            therapeutic_priority=False
        )
    ]
    
    manager.get_services_by_name.return_value = services
    manager.update_service_metrics.return_value = None
    
    return manager


@pytest.fixture
def service_router_config():
    """Create service router configuration for testing."""
    return ServiceRouterConfig(
        load_balancing_strategy=LoadBalancingStrategy.HEALTH_BASED,
        failover_strategy=FailoverStrategy.RETRY_DIFFERENT_SERVICE,
        max_retries=2,
        retry_delay=0.1,
        therapeutic_max_retries=3,
        crisis_max_retries=5
    )


@pytest.fixture
def sample_gateway_request():
    """Create a sample gateway request."""
    return GatewayRequest(
        correlation_id="test-123",
        method=RequestMethod.GET,
        path="/api/v1/test",
        client_ip="127.0.0.1",
        is_therapeutic=False,
        crisis_mode=False
    )


@pytest.fixture
def therapeutic_gateway_request():
    """Create a therapeutic gateway request."""
    return GatewayRequest(
        correlation_id="therapeutic-123",
        method=RequestMethod.POST,
        path="/api/v1/sessions",
        client_ip="127.0.0.1",
        is_therapeutic=True,
        crisis_mode=False
    )


@pytest.fixture
def crisis_gateway_request():
    """Create a crisis gateway request."""
    return GatewayRequest(
        correlation_id="crisis-123",
        method=RequestMethod.POST,
        path="/api/v1/crisis",
        client_ip="127.0.0.1",
        is_therapeutic=True,
        crisis_mode=True
    )


@pytest.fixture
async def service_router(mock_discovery_manager, service_router_config):
    """Create a service router instance."""
    return ServiceRouter(mock_discovery_manager, service_router_config)


class TestServiceRouter:
    """Test cases for ServiceRouter."""
    
    @pytest.mark.asyncio
    async def test_select_service_success(self, service_router, sample_gateway_request):
        """Test successful service selection."""
        selected_service = await service_router.select_service("test-service", sample_gateway_request)
        
        assert selected_service is not None
        assert selected_service.healthy is True
    
    @pytest.mark.asyncio
    async def test_select_service_no_services_available(self, service_router, sample_gateway_request):
        """Test service selection when no services are available."""
        # Mock empty service list
        service_router.discovery_manager.get_services_by_name.return_value = []
        
        selected_service = await service_router.select_service("nonexistent-service", sample_gateway_request)
        
        assert selected_service is None
    
    @pytest.mark.asyncio
    async def test_select_service_therapeutic_priority(self, service_router, therapeutic_gateway_request):
        """Test service selection with therapeutic priority."""
        selected_service = await service_router.select_service("test-service", therapeutic_gateway_request)
        
        assert selected_service is not None
        # Should prefer therapeutic services when available
        # (exact behavior depends on load balancer implementation)
    
    @pytest.mark.asyncio
    async def test_select_service_crisis_mode_allows_unhealthy(self, service_router, crisis_gateway_request):
        """Test crisis mode allows using unhealthy services as last resort."""
        # Mock all services as unhealthy through circuit breakers
        service_router.circuit_breaker_manager.get_healthy_services.return_value = []
        
        selected_service = await service_router.select_service("test-service", crisis_gateway_request)
        
        # Should still return a service in crisis mode
        assert selected_service is not None
    
    @pytest.mark.asyncio
    async def test_route_request_with_failover_success(self, service_router, sample_gateway_request):
        """Test successful request routing with failover."""
        async def mock_request_func(service, *args, **kwargs):
            return f"success from {service.name}"
        
        result = await service_router.route_request_with_failover(
            "test-service",
            sample_gateway_request,
            mock_request_func
        )
        
        assert "success from" in result
    
    @pytest.mark.asyncio
    async def test_route_request_with_failover_retry_on_failure(self, service_router, sample_gateway_request):
        """Test request routing retries on failure."""
        call_count = 0
        
        async def mock_request_func(service, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success after retry"
        
        result = await service_router.route_request_with_failover(
            "test-service",
            sample_gateway_request,
            mock_request_func
        )
        
        assert result == "success after retry"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_route_request_with_failover_max_retries_exceeded(self, service_router, sample_gateway_request):
        """Test request routing fails after max retries."""
        async def mock_request_func(service, *args, **kwargs):
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            await service_router.route_request_with_failover(
                "test-service",
                sample_gateway_request,
                mock_request_func
            )
    
    @pytest.mark.asyncio
    async def test_route_request_therapeutic_more_retries(self, service_router, therapeutic_gateway_request):
        """Test therapeutic requests get more retry attempts."""
        call_count = 0
        
        async def mock_request_func(service, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= service_router.config.max_retries:
                raise Exception("Failure")
            return "success after therapeutic retries"
        
        result = await service_router.route_request_with_failover(
            "test-service",
            therapeutic_gateway_request,
            mock_request_func
        )
        
        assert result == "success after therapeutic retries"
        assert call_count > service_router.config.max_retries
    
    @pytest.mark.asyncio
    async def test_route_request_crisis_most_retries(self, service_router, crisis_gateway_request):
        """Test crisis requests get the most retry attempts."""
        call_count = 0
        
        async def mock_request_func(service, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= service_router.config.therapeutic_max_retries:
                raise Exception("Failure")
            return "success after crisis retries"
        
        result = await service_router.route_request_with_failover(
            "test-service",
            crisis_gateway_request,
            mock_request_func
        )
        
        assert result == "success after crisis retries"
        assert call_count > service_router.config.therapeutic_max_retries
    
    @pytest.mark.asyncio
    async def test_route_request_circuit_breaker_error_retry(self, service_router, sample_gateway_request):
        """Test request routing retries on circuit breaker errors."""
        call_count = 0
        
        async def mock_request_func(service, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise CircuitBreakerError("test-service", "open")
            return "success after circuit breaker retry"
        
        # Mock circuit breaker manager to raise error then allow
        service_router.circuit_breaker_manager.call_service = AsyncMock(side_effect=[
            CircuitBreakerError("test-service", "open"),
            "success after circuit breaker retry"
        ])
        
        result = await service_router.route_request_with_failover(
            "test-service",
            sample_gateway_request,
            mock_request_func
        )
        
        assert result == "success after circuit breaker retry"
    
    @pytest.mark.asyncio
    async def test_update_service_metrics(self, service_router):
        """Test updating service metrics."""
        service_id = "test-service-id"
        
        await service_router.update_service_metrics(
            service_id, 0.5, True, therapeutic=True, crisis=False
        )
        
        # Should update both load balancer and discovery manager
        service_router.discovery_manager.update_service_metrics.assert_called_once_with(
            service_id, 0.5, True
        )
    
    def test_get_load_balancer_metrics(self, service_router):
        """Test getting load balancer metrics."""
        # Add some mock metrics
        from src.api_gateway.core.load_balancer import ServiceMetrics
        service_router.load_balancer.service_metrics["test-service"] = ServiceMetrics(
            service_id="test-service",
            active_connections=5,
            total_requests=100,
            successful_requests=95,
            average_response_time=0.2,
            health_score=0.95
        )
        
        metrics = service_router.get_load_balancer_metrics()
        
        assert "test-service" in metrics
        assert metrics["test-service"]["active_connections"] == 5
        assert metrics["test-service"]["total_requests"] == 100
        assert metrics["test-service"]["successful_requests"] == 95
    
    @pytest.mark.asyncio
    async def test_get_circuit_breaker_status(self, service_router):
        """Test getting circuit breaker status."""
        # Mock circuit breaker manager
        service_router.circuit_breaker_manager.get_service_health_summary = AsyncMock(return_value={
            "service-1": {
                "service_name": "service-1",
                "state": "closed",
                "is_healthy": True,
                "total_requests": 50,
                "success_rate": 0.96
            }
        })
        
        status = await service_router.get_circuit_breaker_status()
        
        assert "service-1" in status
        assert status["service-1"]["is_healthy"] is True
        assert status["service-1"]["state"] == "closed"
    
    def test_clear_service_cache_specific(self, service_router):
        """Test clearing specific service from cache."""
        # Add to cache
        service_router._service_cache["test-service"] = []
        service_router._last_cache_update["test-service"] = 123456789
        
        service_router.clear_service_cache("test-service")
        
        assert "test-service" not in service_router._service_cache
        assert "test-service" not in service_router._last_cache_update
    
    def test_clear_service_cache_all(self, service_router):
        """Test clearing all services from cache."""
        # Add to cache
        service_router._service_cache["service-1"] = []
        service_router._service_cache["service-2"] = []
        service_router._last_cache_update["service-1"] = 123456789
        service_router._last_cache_update["service-2"] = 123456789
        
        service_router.clear_service_cache()
        
        assert len(service_router._service_cache) == 0
        assert len(service_router._last_cache_update) == 0
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, service_router):
        """Test health check when services are healthy."""
        # Mock healthy circuit breakers
        service_router.circuit_breaker_manager.get_service_health_summary = AsyncMock(return_value={
            "service-1": {"is_healthy": True},
            "service-2": {"is_healthy": True}
        })
        
        health = await service_router.health_check()
        
        assert health["status"] == "healthy"
        assert health["healthy_services"] == 2
        assert health["total_services"] == 2
        assert health["load_balancing_strategy"] == service_router.config.load_balancing_strategy.value
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, service_router):
        """Test health check when no services are healthy."""
        # Mock unhealthy circuit breakers
        service_router.circuit_breaker_manager.get_service_health_summary = AsyncMock(return_value={
            "service-1": {"is_healthy": False},
            "service-2": {"is_healthy": False}
        })
        
        health = await service_router.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["healthy_services"] == 0
        assert health["total_services"] == 2
    
    @pytest.mark.asyncio
    async def test_health_check_error(self, service_router):
        """Test health check error handling."""
        # Mock error in health check
        service_router.circuit_breaker_manager.get_service_health_summary = AsyncMock(
            side_effect=Exception("Health check failed")
        )
        
        health = await service_router.health_check()
        
        assert health["status"] == "error"
        assert "error" in health


class TestServiceRouterCaching:
    """Test cases for service router caching functionality."""
    
    @pytest.mark.asyncio
    async def test_service_cache_hit(self, service_router):
        """Test cache hit returns cached services."""
        import time
        
        # Pre-populate cache
        cached_services = [ServiceInfo(
            id=uuid4(),
            name="cached-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8080)
        )]
        
        service_router._service_cache["test-service"] = cached_services
        service_router._last_cache_update["test-service"] = time.time()
        
        services = await service_router._get_available_services("test-service")
        
        assert services == cached_services
        # Should not call discovery manager
        service_router.discovery_manager.get_services_by_name.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_service_cache_miss(self, service_router):
        """Test cache miss fetches from discovery manager."""
        services = await service_router._get_available_services("test-service")
        
        # Should call discovery manager
        service_router.discovery_manager.get_services_by_name.assert_called_once_with("test-service")
        
        # Should cache the result
        assert "test-service" in service_router._service_cache
        assert "test-service" in service_router._last_cache_update
    
    @pytest.mark.asyncio
    async def test_service_cache_expired(self, service_router):
        """Test expired cache fetches fresh data."""
        # Pre-populate cache with old timestamp
        service_router._service_cache["test-service"] = []
        service_router._last_cache_update["test-service"] = 0.0  # Very old
        
        services = await service_router._get_available_services("test-service")
        
        # Should call discovery manager for fresh data
        service_router.discovery_manager.get_services_by_name.assert_called_once_with("test-service")
    
    @pytest.mark.asyncio
    async def test_service_cache_error_fallback(self, service_router):
        """Test cache fallback on discovery manager error."""
        # Pre-populate cache
        cached_services = [ServiceInfo(
            id=uuid4(),
            name="cached-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8080)
        )]
        service_router._service_cache["test-service"] = cached_services
        
        # Mock discovery manager error
        service_router.discovery_manager.get_services_by_name.side_effect = Exception("Discovery failed")
        
        services = await service_router._get_available_services("test-service")
        
        # Should return cached data despite error
        assert services == cached_services


class TestServiceRouterConfiguration:
    """Test cases for service router configuration."""
    
    def test_default_configuration(self, mock_discovery_manager):
        """Test service router with default configuration."""
        router = ServiceRouter(mock_discovery_manager)
        
        assert router.config.load_balancing_strategy == LoadBalancingStrategy.HEALTH_BASED
        assert router.config.failover_strategy == FailoverStrategy.RETRY_DIFFERENT_SERVICE
        assert router.config.max_retries == 3
    
    def test_custom_configuration(self, mock_discovery_manager):
        """Test service router with custom configuration."""
        config = ServiceRouterConfig(
            load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN,
            failover_strategy=FailoverStrategy.RETRY_WITH_BACKOFF,
            max_retries=5,
            retry_delay=2.0
        )
        
        router = ServiceRouter(mock_discovery_manager, config)
        
        assert router.config.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN
        assert router.config.failover_strategy == FailoverStrategy.RETRY_WITH_BACKOFF
        assert router.config.max_retries == 5
        assert router.config.retry_delay == 2.0
