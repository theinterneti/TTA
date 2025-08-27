"""
Integration tests for real external services (Neo4j and Redis).

This module provides comprehensive testing for real service connections,
health monitoring, and production-ready configuration management.
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import patch, AsyncMock

from src.player_experience.api.services.connection_manager import (
    ServiceConnectionManager,
    Neo4jConnectionManager,
    RedisConnectionManager,
    ServiceStatus
)
from src.player_experience.api.config import APISettings, ProductionSettings, TestingSettings


@pytest.fixture
def test_settings():
    """Create test settings for real service testing."""
    return TestingSettings(
        neo4j_url="bolt://localhost:7687",
        neo4j_username="neo4j",
        neo4j_password="testpassword",
        redis_url="redis://localhost:6379/1",
        use_mocks=False,
        use_neo4j=True,
        environment="test"
    )


@pytest.fixture
def production_settings():
    """Create production-like settings for testing."""
    return ProductionSettings(
        neo4j_url="bolt://localhost:7687",
        neo4j_username="neo4j",
        neo4j_password="strongpassword123",
        redis_url="redis://localhost:6379",
        jwt_secret_key="very-strong-production-secret-key-32-chars-long",
        environment="production"
    )


class TestNeo4jConnectionManager:
    """Test Neo4j connection manager with real service scenarios."""
    
    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self, test_settings):
        """Test Neo4j connection manager initialization."""
        manager = Neo4jConnectionManager(test_settings)
        
        assert manager.settings == test_settings
        assert manager.driver is None
        assert manager.health.service_name == "neo4j"
        assert manager.health.status == ServiceStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_connection_success_scenario(self, test_settings):
        """Test successful Neo4j connection scenario."""
        manager = Neo4jConnectionManager(test_settings)
        
        # Mock successful connection
        with patch('src.player_experience.api.services.connection_manager.AsyncGraphDatabase') as mock_graph:
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            
            mock_graph.driver.return_value = mock_driver
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            mock_session.run.return_value = mock_result
            mock_result.consume.return_value = None
            
            success = await manager.connect()
            
            assert success is True
            assert manager.health.status == ServiceStatus.CONNECTED
            assert manager.health.connection_attempts > 0
            assert manager.health.successful_operations > 0
    
    @pytest.mark.asyncio
    async def test_connection_retry_logic(self, test_settings):
        """Test Neo4j connection retry logic with failures."""
        manager = Neo4jConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.AsyncGraphDatabase') as mock_graph:
            # First two attempts fail, third succeeds
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    from neo4j.exceptions import ServiceUnavailable
                    raise ServiceUnavailable("Connection failed")
                return mock_driver
            
            mock_graph.driver.side_effect = side_effect
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            mock_session.run.return_value = AsyncMock()
            
            success = await manager.connect()
            
            assert success is True
            assert manager.health.connection_attempts >= 3
            assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_connection_failure_exhaustion(self, test_settings):
        """Test Neo4j connection failure after exhausting retries."""
        manager = Neo4jConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.AsyncGraphDatabase') as mock_graph:
            from neo4j.exceptions import ServiceUnavailable
            mock_graph.driver.side_effect = ServiceUnavailable("Service unavailable")
            
            success = await manager.connect()
            
            assert success is False
            assert manager.health.status == ServiceStatus.ERROR
            assert manager.health.connection_attempts == manager._max_retries
            assert "Service unavailable" in manager.health.last_error
    
    @pytest.mark.asyncio
    async def test_session_context_manager(self, test_settings):
        """Test Neo4j session context manager."""
        manager = Neo4jConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.AsyncGraphDatabase') as mock_graph:
            mock_driver = AsyncMock()
            mock_session = AsyncMock()
            
            mock_graph.driver.return_value = mock_driver
            mock_driver.session.return_value.__aenter__.return_value = mock_session
            mock_driver.session.return_value.__aexit__.return_value = None
            mock_session.run.return_value = AsyncMock()
            
            # First establish connection
            await manager.connect()
            
            # Test session context manager
            async with manager.session() as session:
                assert session == mock_session
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, test_settings):
        """Test Neo4j health monitoring and metrics."""
        manager = Neo4jConnectionManager(test_settings)
        
        # Test initial health
        health = manager.get_health()
        assert health["service"] == "neo4j"
        assert health["status"] == "disconnected"
        assert health["connection_attempts"] == 0
        
        # Simulate connection and operations
        manager.health.update_status(ServiceStatus.CONNECTED)
        manager.health.successful_operations = 10
        manager.health.failed_operations = 2
        manager.health.average_response_time = 15.5
        
        health = manager.get_health()
        assert health["status"] == "connected"
        assert health["successful_operations"] == 10
        assert health["failed_operations"] == 2
        assert health["success_rate"] == 10/12  # 10 success out of 12 total
        assert health["average_response_time_ms"] == 15.5


class TestRedisConnectionManager:
    """Test Redis connection manager with real service scenarios."""
    
    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self, test_settings):
        """Test Redis connection manager initialization."""
        manager = RedisConnectionManager(test_settings)
        
        assert manager.settings == test_settings
        assert manager.client is None
        assert manager.health.service_name == "redis"
        assert manager.health.status == ServiceStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_connection_success_scenario(self, test_settings):
        """Test successful Redis connection scenario."""
        manager = RedisConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client
            mock_client.ping.return_value = True
            
            success = await manager.connect()
            
            assert success is True
            assert manager.health.status == ServiceStatus.CONNECTED
            assert manager.health.connection_attempts > 0
    
    @pytest.mark.asyncio
    async def test_redis_operations(self, test_settings):
        """Test Redis operations with connection management."""
        manager = RedisConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.get.return_value = "test_value"
            mock_client.set.return_value = True
            mock_client.delete.return_value = 1
            
            # Establish connection
            await manager.connect()
            
            # Test operations
            value = await manager.get("test_key")
            assert value == "test_value"
            
            success = await manager.set("test_key", "new_value", ex=3600)
            assert success is True
            
            deleted = await manager.delete("test_key")
            assert deleted == 1
    
    @pytest.mark.asyncio
    async def test_connection_retry_with_timeout(self, test_settings):
        """Test Redis connection retry logic with timeout errors."""
        manager = RedisConnectionManager(test_settings)
        
        with patch('src.player_experience.api.services.connection_manager.redis') as mock_redis:
            import redis as redis_module
            
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise redis_module.TimeoutError("Connection timeout")
                
                mock_client = AsyncMock()
                mock_client.ping.return_value = True
                return mock_client
            
            mock_redis.from_url.side_effect = side_effect
            
            success = await manager.connect()
            
            assert success is True
            assert call_count == 3


class TestServiceConnectionManager:
    """Test centralized service connection manager."""
    
    @pytest.mark.asyncio
    async def test_service_manager_initialization_with_mocks(self, test_settings):
        """Test service manager initialization with mock services."""
        # Force mock usage
        test_settings.use_mocks = True
        test_settings.use_neo4j = False
        
        manager = ServiceConnectionManager(test_settings)
        
        assert manager.use_mocks is True
        assert hasattr(manager.neo4j, 'get_metrics')  # Mock service
        assert hasattr(manager.redis, 'get_metrics')  # Mock service
    
    @pytest.mark.asyncio
    async def test_service_manager_initialization_with_real_services(self, test_settings):
        """Test service manager initialization with real services."""
        # Force real service usage
        test_settings.use_mocks = False
        test_settings.use_neo4j = True
        
        manager = ServiceConnectionManager(test_settings)
        
        assert manager.use_mocks is False
        assert isinstance(manager.neo4j, Neo4jConnectionManager)
        assert isinstance(manager.redis, RedisConnectionManager)
    
    @pytest.mark.asyncio
    async def test_service_initialization_success(self, test_settings):
        """Test successful service initialization."""
        manager = ServiceConnectionManager(test_settings)
        
        # Mock the connect methods
        with patch.object(manager.neo4j, 'connect', return_value=True) if hasattr(manager.neo4j, 'connect') else patch('builtins.hasattr', return_value=False):
            with patch.object(manager.redis, 'connect', return_value=True) if hasattr(manager.redis, 'connect') else patch('builtins.hasattr', return_value=False):
                success = await manager.initialize()
                assert success is True
    
    @pytest.mark.asyncio
    async def test_service_initialization_partial_failure(self, test_settings):
        """Test service initialization with partial failures."""
        test_settings.use_mocks = False
        test_settings.use_neo4j = True
        manager = ServiceConnectionManager(test_settings)
        
        # Mock Neo4j success, Redis failure
        with patch.object(manager.neo4j, 'connect', return_value=True):
            with patch.object(manager.redis, 'connect', return_value=False):
                success = await manager.initialize()
                assert success is False  # Should fail if any service fails
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self, test_settings):
        """Test comprehensive health check functionality."""
        manager = ServiceConnectionManager(test_settings)
        
        health_info = await manager.health_check()
        
        assert "timestamp" in health_info
        assert "using_mocks" in health_info
        assert "services" in health_info
        assert "neo4j" in health_info["services"]
        assert "redis" in health_info["services"]
        
        # Check service health structure
        neo4j_health = health_info["services"]["neo4j"]
        assert "service" in neo4j_health
        assert "status" in neo4j_health
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, test_settings):
        """Test service cleanup and connection closing."""
        manager = ServiceConnectionManager(test_settings)
        
        # Initialize services
        await manager.initialize()
        
        # Test cleanup
        await manager.close()
        
        # Verify cleanup was called (this would be more detailed with real services)
        assert True  # Basic test that no exceptions were raised


class TestProductionConfiguration:
    """Test production-specific configuration and security."""
    
    def test_production_settings_validation(self):
        """Test production settings validation."""
        # Test that weak passwords are rejected
        with pytest.raises(ValueError, match="Must set a strong JWT secret key"):
            ProductionSettings(
                jwt_secret_key="your-secret-key-change-in-production",
                neo4j_password="strongpassword123"
            )
        
        with pytest.raises(ValueError, match="Must set a strong Neo4j password"):
            ProductionSettings(
                jwt_secret_key="very-strong-production-secret-key-32-chars-long",
                neo4j_password="password"
            )
    
    def test_production_security_defaults(self):
        """Test production security defaults."""
        settings = ProductionSettings(
            jwt_secret_key="very-strong-production-secret-key-32-chars-long",
            neo4j_password="strongpassword123"
        )
        
        assert settings.debug is False
        assert settings.mfa_enabled is True
        assert settings.max_login_attempts == 3
        assert settings.lockout_duration_minutes == 30
    
    def test_environment_detection(self, production_settings):
        """Test environment detection properties."""
        assert production_settings.is_production is True
        assert production_settings.is_development is False
        assert production_settings.is_testing is False
    
    def test_service_connection_settings(self, production_settings):
        """Test service connection configuration."""
        assert production_settings.service_connection_timeout == 30
        assert production_settings.service_retry_attempts == 5
        assert production_settings.service_retry_base_delay == 0.5
        assert production_settings.service_retry_max_delay == 8.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
