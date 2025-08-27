"""
Tests for the API Gateway service discovery system.

This module contains unit tests for service discovery, registration,
and health monitoring functionality.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.api_gateway.models import ServiceInfo, ServiceType, ServiceEndpoint, ServiceHealthCheck
from src.api_gateway.services import ServiceDiscoveryManager, RedisServiceRegistry, AutoRegistrationService


@pytest.fixture
def sample_service():
    """Create a sample service for testing."""
    return ServiceInfo(
        id=uuid4(),
        name="test-service",
        version="1.0.0",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(
            host="localhost",
            port=8080,
            path="/api/v1",
            scheme="http"
        ),
        weight=100,
        priority=100,
        tags=["test", "api"],
        metadata={"description": "Test service"},
        health_check=ServiceHealthCheck(
            enabled=True,
            endpoint="/health",
            interval=30,
            timeout=5,
            retries=3
        ),
        therapeutic_priority=False,
        safety_validated=True
    )


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.hset.return_value = True
    mock_redis.hget.return_value = None
    mock_redis.hgetall.return_value = {}
    mock_redis.hdel.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.get.return_value = "healthy"
    mock_redis.delete.return_value = True
    mock_redis.sadd.return_value = True
    mock_redis.srem.return_value = True
    mock_redis.smembers.return_value = set()
    mock_redis.close.return_value = None
    return mock_redis


class TestRedisServiceRegistry:
    """Test cases for RedisServiceRegistry."""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_redis):
        """Test successful registry initialization."""
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        mock_redis.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_service_success(self, mock_redis, sample_service):
        """Test successful service registration."""
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        result = await registry.register_service(sample_service)
        
        assert result is True
        mock_redis.hset.assert_called()
        mock_redis.setex.assert_called()
        mock_redis.sadd.assert_called()
    
    @pytest.mark.asyncio
    async def test_deregister_service_success(self, mock_redis, sample_service):
        """Test successful service deregistration."""
        # Mock service exists
        mock_redis.hget.return_value = sample_service.json()
        
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        result = await registry.deregister_service(sample_service.id)
        
        assert result is True
        mock_redis.hdel.assert_called()
        mock_redis.delete.assert_called()
        mock_redis.srem.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_service_success(self, mock_redis, sample_service):
        """Test successful service retrieval."""
        mock_redis.hget.return_value = sample_service.json()
        
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        result = await registry.get_service(sample_service.id)
        
        assert result is not None
        assert result.id == sample_service.id
        assert result.name == sample_service.name
    
    @pytest.mark.asyncio
    async def test_get_healthy_services(self, mock_redis, sample_service):
        """Test getting healthy services."""
        mock_redis.hgetall.return_value = {str(sample_service.id): sample_service.json()}
        mock_redis.get.return_value = "healthy"
        
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        result = await registry.get_healthy_services()
        
        assert len(result) == 1
        assert result[0].id == sample_service.id
    
    @pytest.mark.asyncio
    async def test_update_service_health(self, mock_redis, sample_service):
        """Test updating service health status."""
        registry = RedisServiceRegistry(mock_redis)
        await registry.initialize()
        
        result = await registry.update_service_health(sample_service.id, True)
        
        assert result is True
        mock_redis.setex.assert_called()


class TestServiceDiscoveryManager:
    """Test cases for ServiceDiscoveryManager."""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_redis):
        """Test successful manager initialization."""
        with patch('src.api_gateway.services.discovery_manager.RedisServiceRegistry') as mock_registry_class:
            mock_registry = AsyncMock()
            mock_registry_class.return_value = mock_registry
            
            manager = ServiceDiscoveryManager()
            await manager.initialize()
            
            mock_registry.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_service_success(self, mock_redis, sample_service):
        """Test successful service registration through manager."""
        with patch('src.api_gateway.services.discovery_manager.RedisServiceRegistry') as mock_registry_class:
            mock_registry = AsyncMock()
            mock_registry.register_service.return_value = True
            mock_registry_class.return_value = mock_registry
            
            manager = ServiceDiscoveryManager()
            await manager.initialize()
            
            result = await manager.register_service(sample_service, start_health_monitoring=False)
            
            assert result is True
            mock_registry.register_service.assert_called_once_with(sample_service)
    
    @pytest.mark.asyncio
    async def test_get_service_for_request_round_robin(self, mock_redis):
        """Test service selection with round-robin load balancing."""
        service1 = ServiceInfo(
            id=uuid4(),
            name="service-1",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8081)
        )
        service2 = ServiceInfo(
            id=uuid4(),
            name="service-2",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8082)
        )
        
        with patch('src.api_gateway.services.discovery_manager.RedisServiceRegistry') as mock_registry_class:
            mock_registry = AsyncMock()
            mock_registry.get_healthy_services.return_value = [service1, service2]
            mock_registry_class.return_value = mock_registry
            
            manager = ServiceDiscoveryManager()
            await manager.initialize()
            
            # Test round-robin selection
            result1 = await manager.get_service_for_request(ServiceType.API)
            result2 = await manager.get_service_for_request(ServiceType.API)
            
            assert result1 is not None
            assert result2 is not None
            # Should alternate between services
            assert result1.id != result2.id or len([service1, service2]) == 1


class TestAutoRegistrationService:
    """Test cases for AutoRegistrationService."""
    
    @pytest.mark.asyncio
    async def test_register_tta_services(self):
        """Test automatic registration of TTA services."""
        mock_discovery_manager = AsyncMock()
        mock_discovery_manager.register_service.return_value = True
        
        auto_registration = AutoRegistrationService(mock_discovery_manager)
        
        await auto_registration.register_tta_services()
        
        # Should register multiple services
        assert mock_discovery_manager.register_service.call_count >= 4
    
    @pytest.mark.asyncio
    async def test_deregister_all_services(self):
        """Test deregistration of all auto-registered services."""
        mock_discovery_manager = AsyncMock()
        mock_discovery_manager.register_service.return_value = True
        mock_discovery_manager.deregister_service.return_value = True
        
        auto_registration = AutoRegistrationService(mock_discovery_manager)
        
        # Register services first
        await auto_registration.register_tta_services()
        
        # Then deregister all
        await auto_registration.deregister_all_services()
        
        # Should have called deregister for each registered service
        assert mock_discovery_manager.deregister_service.call_count > 0
    
    def test_get_registered_services(self):
        """Test getting registered services."""
        mock_discovery_manager = MagicMock()
        auto_registration = AutoRegistrationService(mock_discovery_manager)
        
        services = auto_registration.get_registered_services()
        
        assert isinstance(services, dict)


@pytest.mark.asyncio
async def test_service_discovery_integration():
    """Integration test for service discovery components."""
    # This test would require a real Redis instance
    # For now, we'll just test that components can be instantiated together
    
    with patch('redis.asyncio.from_url') as mock_redis_from_url:
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis_from_url.return_value = mock_redis
        
        # Create components
        manager = ServiceDiscoveryManager()
        auto_registration = AutoRegistrationService(manager)
        
        # Initialize
        await manager.initialize()
        
        # Test that they work together
        services = auto_registration.get_registered_services()
        assert isinstance(services, dict)
        
        # Cleanup
        await manager.close()
