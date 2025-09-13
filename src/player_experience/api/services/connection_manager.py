"""
Service Connection Manager for Real External Services.

This module provides centralized connection management for Neo4j and Redis
with proper retry logic, health monitoring, and environment-specific configuration.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import AuthError, ClientError, ServiceUnavailable

from ..config import APISettings
from ..mock_services import (
    MockNeo4jDriver,
    MockRedisClient,
    MockServiceConfig,
    should_use_mocks,
)

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service connection status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DEGRADED = "degraded"


class ConnectionHealth:
    """Health monitoring for service connections."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.status = ServiceStatus.DISCONNECTED
        self.last_check = None
        self.last_error = None
        self.connection_attempts = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.average_response_time = 0.0
        self.created_at = datetime.now()

    def update_status(self, status: ServiceStatus, error: str | None = None):
        """Update service status."""
        self.status = status
        self.last_check = datetime.now()
        if error:
            self.last_error = error
            self.failed_operations += 1
        else:
            self.successful_operations += 1

    def get_health_info(self) -> dict[str, Any]:
        """Get comprehensive health information."""
        uptime = (datetime.now() - self.created_at).total_seconds()
        success_rate = 0.0
        if self.connection_attempts > 0:
            success_rate = self.successful_operations / (
                self.successful_operations + self.failed_operations
            )

        return {
            "service": self.service_name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_error": self.last_error,
            "connection_attempts": self.connection_attempts,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": success_rate,
            "average_response_time_ms": self.average_response_time,
            "uptime_seconds": uptime,
        }


class Neo4jConnectionManager:
    """Enhanced Neo4j connection manager with health monitoring."""

    def __init__(self, settings: APISettings):
        self.settings = settings
        self.driver = None
        self.health = ConnectionHealth("neo4j")
        self._connection_lock = asyncio.Lock()
        self._max_retries = 5
        self._base_delay = 0.5
        self._max_delay = 8.0

    async def connect(self) -> bool:
        """Connect to Neo4j with enhanced retry logic."""
        async with self._connection_lock:
            if self.driver and await self._test_connection():
                return True

            self.health.update_status(ServiceStatus.CONNECTING)

            for attempt in range(self._max_retries):
                try:
                    self.health.connection_attempts += 1
                    logger.debug(
                        f"Neo4j connection attempt {attempt + 1}/{self._max_retries}"
                    )

                    # Close existing driver if any
                    if self.driver:
                        await self.driver.close()

                    # Create new driver with production-ready settings
                    self.driver = AsyncGraphDatabase.driver(
                        self.settings.neo4j_url,
                        auth=(
                            self.settings.neo4j_username,
                            self.settings.neo4j_password,
                        ),
                        max_connection_lifetime=3600,  # 1 hour
                        max_connection_pool_size=50,
                        connection_acquisition_timeout=60,
                        encrypted=self.settings.neo4j_url.startswith("neo4j+s://"),
                        trust=(
                            "TRUST_ALL_CERTIFICATES"
                            if not self.settings.neo4j_url.startswith("neo4j+s://")
                            else "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
                        ),
                    )

                    # Test connection
                    if await self._test_connection():
                        self.health.update_status(ServiceStatus.CONNECTED)
                        logger.info(
                            f"Successfully connected to Neo4j at {self.settings.neo4j_url}"
                        )
                        return True

                except (ServiceUnavailable, AuthError, ClientError) as e:
                    error_msg = f"Neo4j connection attempt {attempt + 1} failed: {e}"
                    logger.debug(error_msg)

                    if attempt == self._max_retries - 1:
                        self.health.update_status(ServiceStatus.ERROR, str(e))
                        logger.error(
                            f"Failed to connect to Neo4j after {self._max_retries} attempts: {e}"
                        )
                        return False

                    # Exponential backoff
                    delay = min(self._base_delay * (2**attempt), self._max_delay)
                    await asyncio.sleep(delay)

                except Exception as e:
                    error_msg = f"Unexpected Neo4j connection error: {e}"
                    logger.error(error_msg)
                    self.health.update_status(ServiceStatus.ERROR, str(e))
                    return False

            return False

    async def _test_connection(self) -> bool:
        """Test Neo4j connection health."""
        if not self.driver:
            return False

        try:
            start_time = time.time()
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.consume()

            response_time = (time.time() - start_time) * 1000
            self.health.average_response_time = (
                (self.health.average_response_time + response_time) / 2
                if self.health.average_response_time > 0
                else response_time
            )
            return True
        except Exception as e:
            logger.debug(f"Neo4j connection test failed: {e}")
            return False

    @asynccontextmanager
    async def session(self, **kwargs):
        """Get Neo4j session with automatic connection management."""
        if not self.driver or not await self._test_connection():
            if not await self.connect():
                raise ConnectionError("Failed to establish Neo4j connection")

        async with self.driver.session(**kwargs) as session:
            yield session

    async def close(self):
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
            self.health.update_status(ServiceStatus.DISCONNECTED)
            logger.info("Neo4j connection closed")

    def get_health(self) -> dict[str, Any]:
        """Get Neo4j connection health information."""
        return self.health.get_health_info()


class RedisConnectionManager:
    """Enhanced Redis connection manager with health monitoring."""

    def __init__(self, settings: APISettings):
        self.settings = settings
        self.client = None
        self.health = ConnectionHealth("redis")
        self._connection_lock = asyncio.Lock()
        self._max_retries = 5
        self._base_delay = 0.5
        self._max_delay = 8.0

    async def connect(self) -> bool:
        """Connect to Redis with enhanced retry logic."""
        async with self._connection_lock:
            if self.client and await self._test_connection():
                return True

            self.health.update_status(ServiceStatus.CONNECTING)

            for attempt in range(self._max_retries):
                try:
                    self.health.connection_attempts += 1
                    logger.debug(
                        f"Redis connection attempt {attempt + 1}/{self._max_retries}"
                    )

                    # Close existing client if any
                    if self.client:
                        await self.client.close()

                    # Create new Redis client with production-ready settings
                    # For Redis 7.2+, we need to specify both username and password for ACL authentication
                    redis_kwargs = {
                        "decode_responses": True,
                        "retry_on_timeout": True,
                        "socket_connect_timeout": 5,
                        "socket_timeout": 5,
                        "max_connections": 20,
                    }

                    # Add authentication if password is configured
                    if (
                        self.settings.redis_password
                        and self.settings.redis_password.strip()
                    ):
                        redis_kwargs["username"] = (
                            "default"  # Use default user for Redis 7.2+ ACL
                        )
                        redis_kwargs["password"] = self.settings.redis_password

                    # Parse host and port from URL
                    from urllib.parse import urlparse

                    parsed = urlparse(self.settings.redis_url)
                    redis_kwargs["host"] = parsed.hostname or "localhost"
                    redis_kwargs["port"] = parsed.port or 6379

                    self.client = redis.Redis(**redis_kwargs)

                    # Test connection
                    if await self._test_connection():
                        self.health.update_status(ServiceStatus.CONNECTED)
                        logger.info(
                            f"Successfully connected to Redis at {self.settings.redis_url}"
                        )
                        return True

                except (redis.ConnectionError, redis.TimeoutError) as e:
                    error_msg = f"Redis connection attempt {attempt + 1} failed: {e}"
                    logger.debug(error_msg)

                    if attempt == self._max_retries - 1:
                        self.health.update_status(ServiceStatus.ERROR, str(e))
                        logger.error(
                            f"Failed to connect to Redis after {self._max_retries} attempts: {e}"
                        )
                        return False

                    # Exponential backoff
                    delay = min(self._base_delay * (2**attempt), self._max_delay)
                    await asyncio.sleep(delay)

                except Exception as e:
                    error_msg = f"Unexpected Redis connection error: {e}"
                    logger.error(error_msg)
                    self.health.update_status(ServiceStatus.ERROR, str(e))
                    return False

            return False

    async def _test_connection(self) -> bool:
        """Test Redis connection health."""
        if not self.client:
            return False

        try:
            start_time = time.time()
            await self.client.ping()

            response_time = (time.time() - start_time) * 1000
            self.health.average_response_time = (
                (self.health.average_response_time + response_time) / 2
                if self.health.average_response_time > 0
                else response_time
            )
            return True
        except Exception as e:
            logger.debug(f"Redis connection test failed: {e}")
            return False

    async def get(self, key: str) -> str | None:
        """Get value from Redis with automatic connection management."""
        if not await self._ensure_connected():
            raise ConnectionError("Failed to establish Redis connection")

        try:
            return await self.client.get(key)
        except Exception as e:
            self.health.update_status(ServiceStatus.ERROR, str(e))
            raise

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        """Set value in Redis with automatic connection management."""
        if not await self._ensure_connected():
            raise ConnectionError("Failed to establish Redis connection")

        try:
            return await self.client.set(key, value, ex=ex)
        except Exception as e:
            self.health.update_status(ServiceStatus.ERROR, str(e))
            raise

    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis with automatic connection management."""
        if not await self._ensure_connected():
            raise ConnectionError("Failed to establish Redis connection")

        try:
            return await self.client.delete(*keys)
        except Exception as e:
            self.health.update_status(ServiceStatus.ERROR, str(e))
            raise

    async def _ensure_connected(self) -> bool:
        """Ensure Redis connection is active."""
        if not self.client or not await self._test_connection():
            return await self.connect()
        return True

    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None
            self.health.update_status(ServiceStatus.DISCONNECTED)
            logger.info("Redis connection closed")

    def get_health(self) -> dict[str, Any]:
        """Get Redis connection health information."""
        return self.health.get_health_info()


class ServiceConnectionManager:
    """Centralized service connection manager."""

    def __init__(self, settings: APISettings):
        self.settings = settings
        self.use_mocks = should_use_mocks() or not settings.use_neo4j

        if self.use_mocks:
            logger.info("Using mock services for development/testing")
            mock_config = MockServiceConfig(
                base_latency_ms=1.0, log_operations=settings.debug
            )
            self.neo4j = MockNeo4jDriver(
                settings.neo4j_url,
                (settings.neo4j_username, settings.neo4j_password),
                mock_config,
            )
            self.redis = MockRedisClient(mock_config)
        else:
            logger.info("Using real external services")
            self.neo4j = Neo4jConnectionManager(settings)
            self.redis = RedisConnectionManager(settings)

    async def initialize(self) -> bool:
        """Initialize all service connections."""
        logger.info("Initializing service connections...")

        neo4j_connected = False
        redis_connected = False

        # Connect to Neo4j
        try:
            if hasattr(self.neo4j, "connect"):
                neo4j_connected = await self.neo4j.connect()
            else:
                # Mock service - always connected
                neo4j_connected = True
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")

        # Connect to Redis
        try:
            if hasattr(self.redis, "connect"):
                redis_connected = await self.redis.connect()
            else:
                # Mock service - always connected
                redis_connected = True
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")

        success = neo4j_connected and redis_connected
        if success:
            logger.info("All service connections initialized successfully")
        else:
            logger.warning(
                f"Service initialization partial: Neo4j={neo4j_connected}, Redis={redis_connected}"
            )

        return success

    async def health_check(self) -> dict[str, Any]:
        """Get comprehensive health check for all services."""
        health_info = {
            "timestamp": datetime.now().isoformat(),
            "using_mocks": self.use_mocks,
            "services": {},
        }

        # Neo4j health
        if hasattr(self.neo4j, "get_health"):
            health_info["services"]["neo4j"] = self.neo4j.get_health()
        else:
            health_info["services"]["neo4j"] = {
                "service": "neo4j",
                "status": "mock",
                "mock_metrics": (
                    self.neo4j.get_metrics()
                    if hasattr(self.neo4j, "get_metrics")
                    else {}
                ),
            }

        # Redis health
        if hasattr(self.redis, "get_health"):
            health_info["services"]["redis"] = self.redis.get_health()
        else:
            health_info["services"]["redis"] = {
                "service": "redis",
                "status": "mock",
                "mock_metrics": (
                    self.redis.get_metrics()
                    if hasattr(self.redis, "get_metrics")
                    else {}
                ),
            }

        return health_info

    async def close(self):
        """Close all service connections."""
        logger.info("Closing service connections...")

        if hasattr(self.neo4j, "close"):
            await self.neo4j.close()

        if hasattr(self.redis, "close"):
            await self.redis.close()

        logger.info("All service connections closed")


# Global service manager instance
_service_manager: ServiceConnectionManager | None = None


def get_service_manager(
    settings: APISettings | None = None,
) -> ServiceConnectionManager:
    """Get global service manager instance."""
    global _service_manager

    if _service_manager is None:
        if settings is None:
            from ..config import settings as default_settings

            settings = default_settings
        _service_manager = ServiceConnectionManager(settings)

    return _service_manager


async def initialize_services(settings: APISettings | None = None) -> bool:
    """Initialize all services."""
    manager = get_service_manager(settings)
    return await manager.initialize()


async def close_services():
    """Close all services."""
    global _service_manager
    if _service_manager:
        await _service_manager.close()
        _service_manager = None
