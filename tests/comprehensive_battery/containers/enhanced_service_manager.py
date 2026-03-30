"""

# Logseq: [[TTA.dev/Tests/Comprehensive_battery/Containers/Enhanced_service_manager]]
Enhanced Service Manager for TTA Comprehensive Test Battery

Integrates Docker container support with existing mock service architecture,
providing seamless fallback between containerized services and mocks.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..mocks.mock_services import MockServiceManager
from .docker_manager import ContainerStatus, DockerManager
from .health_checker import ContainerHealthChecker, HealthStatus

logger = logging.getLogger(__name__)


class ServiceBackend(Enum):
    """Service backend type enumeration."""

    CONTAINER = "container"
    MOCK = "mock"
    DIRECT = "direct"  # Direct connection without container


@dataclass
class ServiceConfig:
    """Service configuration."""

    name: str
    container_name: str | None = None
    direct_uri: str | None = None
    mock_enabled: bool = True
    health_check_timeout: float = 30.0
    max_startup_wait: float = 120.0


@dataclass
class ServiceStatus:
    """Service status information."""

    name: str
    backend: ServiceBackend
    status: str
    uri: str | None = None
    container_id: str | None = None
    health_check_result: Any | None = None
    error_message: str | None = None


class EnhancedServiceManager:
    """
    Enhanced service manager that integrates Docker containers with mock services.

    Provides automatic service detection and fallback:
    1. Try direct connection to specified URI
    2. Try Docker container if available
    3. Fall back to mock implementation
    """

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.docker_manager = DockerManager()
        self.health_checker = ContainerHealthChecker()
        self.mock_manager = MockServiceManager()
        self.services: dict[str, ServiceStatus] = {}

        # Service configurations - try multiple container name patterns
        self.service_configs = {
            "neo4j": ServiceConfig(
                name="neo4j",
                container_name="tta-test-neo4j",  # Updated to match compose file
                health_check_timeout=30.0,
                max_startup_wait=120.0,
            ),
            "redis": ServiceConfig(
                name="redis",
                container_name="tta-test-redis",  # Updated to match compose file
                health_check_timeout=10.0,
                max_startup_wait=60.0,
            ),
        }

    async def initialize_services(
        self, neo4j_uri: str | None = None, redis_url: str | None = None
    ) -> dict[str, ServiceStatus]:
        """Initialize all services with fallback strategy."""
        logger.info("🔧 Initializing enhanced service manager...")

        if self.force_mock:
            logger.info("🎭 Force mock mode enabled - using mock implementations")
            return await self._initialize_mock_services()

        # Update service configurations with provided URIs
        if neo4j_uri:
            self.service_configs["neo4j"].direct_uri = neo4j_uri
        if redis_url:
            self.service_configs["redis"].direct_uri = redis_url

        # Initialize each service
        for service_name, config in self.service_configs.items():
            status = await self._initialize_service(config)
            self.services[service_name] = status

        # Log service status summary
        self._log_service_summary()

        return self.services

    async def _initialize_service(self, config: ServiceConfig) -> ServiceStatus:
        """Initialize a single service with fallback strategy."""
        logger.info(f"🔧 Initializing {config.name} service...")

        # Strategy 1: Try direct connection if URI provided
        if config.direct_uri:
            status = await self._try_direct_connection(config)
            if status.backend != ServiceBackend.MOCK:
                return status

        # Strategy 2: Try Docker container
        if self.docker_manager.is_docker_available() and config.container_name:
            status = await self._try_container_connection(config)
            if status.backend != ServiceBackend.MOCK:
                return status

        # Strategy 3: Fall back to mock
        logger.info(f"🎭 Falling back to mock implementation for {config.name}")
        return await self._initialize_mock_service(config)

    async def _try_direct_connection(self, config: ServiceConfig) -> ServiceStatus:
        """Try direct connection to service."""
        logger.info(
            f"🔗 Trying direct connection to {config.name} at {config.direct_uri}"
        )

        try:
            if config.name == "neo4j":
                # Use credential fallback for Neo4j
                health_result = await self.health_checker.check_neo4j_health_with_credential_fallback(
                    config.direct_uri, timeout=config.health_check_timeout
                )
            elif config.name == "redis":
                health_result = await self.health_checker.check_redis_health(
                    config.direct_uri, timeout=config.health_check_timeout
                )
            else:
                raise ValueError(f"Unknown service: {config.name}")

            if health_result.status == HealthStatus.HEALTHY:
                logger.info(f"✅ Direct connection to {config.name} successful")
                return ServiceStatus(
                    name=config.name,
                    backend=ServiceBackend.DIRECT,
                    status="healthy",
                    uri=config.direct_uri,
                    health_check_result=health_result,
                )
            logger.warning(
                f"⚠️  Direct connection to {config.name} failed: {health_result.message}"
            )
            return ServiceStatus(
                name=config.name,
                backend=ServiceBackend.MOCK,
                status="unhealthy",
                error_message=health_result.message,
            )

        except Exception as e:
            logger.warning(f"⚠️  Direct connection to {config.name} error: {e}")
            return ServiceStatus(
                name=config.name,
                backend=ServiceBackend.MOCK,
                status="error",
                error_message=str(e),
            )

    async def _try_container_connection(self, config: ServiceConfig) -> ServiceStatus:
        """Try Docker container connection."""
        logger.info(f"🐳 Trying container connection to {config.name}")

        try:
            # Try multiple container name patterns
            container_names_to_try = [
                config.container_name,  # Primary name from config
                f"tta-test-{config.name}",  # Test environment pattern
                f"tta-dev-{config.name}",  # Dev environment pattern
                f"tta-{config.name}",  # Legacy pattern
                config.name,  # Simple name
            ]

            container_info = None
            for container_name in container_names_to_try:
                logger.debug(f"Trying container name: {container_name}")
                info = self.docker_manager.get_container_info(container_name)
                if (
                    info.status != ContainerStatus.STOPPED
                    or info.error_message != "Container not found"
                ):
                    container_info = info
                    logger.info(f"Found container: {container_name}")
                    break

            if (
                not container_info
                or container_info.error_message == "Container not found"
            ):
                logger.warning(
                    f"⚠️  No container found for {config.name} with any naming pattern"
                )
                return await self._initialize_mock_service(config)

            if container_info.status == ContainerStatus.STOPPED:
                logger.info(f"🚀 Starting container {container_info.name}")
                if not self.docker_manager.start_container(container_info.name):
                    logger.warning(
                        f"⚠️  Failed to start container {container_info.name}"
                    )
                    return await self._initialize_mock_service(config)

                # Wait for container to start
                await asyncio.sleep(2)
                container_info = self.docker_manager.get_container_info(
                    container_info.name
                )

            if container_info.status not in [
                ContainerStatus.HEALTHY,
                ContainerStatus.UNKNOWN,
            ]:
                logger.warning(
                    f"⚠️  Container {config.container_name} not healthy: {container_info.status}"
                )
                return await self._initialize_mock_service(config)

            # Determine service URI from container ports
            service_uri = self._get_container_service_uri(config, container_info)
            if not service_uri:
                logger.warning(
                    f"⚠️  Could not determine service URI for container {config.container_name}"
                )
                return await self._initialize_mock_service(config)

            # Health check the containerized service
            if config.name == "neo4j":

                def health_check_func():
                    return (
                        self.health_checker.check_neo4j_health_with_credential_fallback(
                            service_uri
                        )
                    )

            elif config.name == "redis":

                def health_check_func():
                    return self.health_checker.check_redis_health(service_uri)

            else:
                raise ValueError(f"Unknown service: {config.name}")

            health_result = await self.health_checker.wait_for_service_health(
                config.name, health_check_func, max_wait_time=config.max_startup_wait
            )

            if health_result.status == HealthStatus.HEALTHY:
                logger.info(f"✅ Container connection to {config.name} successful")
                return ServiceStatus(
                    name=config.name,
                    backend=ServiceBackend.CONTAINER,
                    status="healthy",
                    uri=service_uri,
                    container_id=container_info.container_id,
                    health_check_result=health_result,
                )
            logger.warning(
                f"⚠️  Container {config.name} health check failed: {health_result.message}"
            )
            return await self._initialize_mock_service(config)

        except Exception as e:
            logger.warning(f"⚠️  Container connection to {config.name} error: {e}")
            return await self._initialize_mock_service(config)

    def _get_container_service_uri(
        self, config: ServiceConfig, container_info
    ) -> str | None:
        """Get service URI from container port mappings."""
        try:
            if config.name == "neo4j":
                # Look for Neo4j Bolt port (7687)
                for container_port, host_port in container_info.ports.items():
                    if container_port.startswith("7687"):
                        return f"bolt://localhost:{host_port}"
                return "bolt://localhost:7687"  # Default

            if config.name == "redis":
                # Look for Redis port (6379)
                for container_port, host_port in container_info.ports.items():
                    if container_port.startswith("6379"):
                        return f"redis://localhost:{host_port}"
                return "redis://localhost:6379"  # Default

        except Exception as e:
            logger.error(f"Error determining service URI: {e}")
            return None

    async def _initialize_mock_service(self, config: ServiceConfig) -> ServiceStatus:
        """Initialize mock service."""
        logger.info(f"🎭 Initializing mock {config.name} service")

        try:
            if config.name == "neo4j":
                # Use a dummy URI for mock initialization
                await self.mock_manager.get_neo4j_driver("bolt://mock:7687")
                return ServiceStatus(
                    name=config.name,
                    backend=ServiceBackend.MOCK,
                    status="mock_ready",
                    uri="mock://neo4j",
                )
            if config.name == "redis":
                await self.mock_manager.get_redis_client("redis://mock:6379")
                return ServiceStatus(
                    name=config.name,
                    backend=ServiceBackend.MOCK,
                    status="mock_ready",
                    uri="mock://redis",
                )
            raise ValueError(f"Unknown service: {config.name}")

        except Exception as e:
            logger.error(f"Failed to initialize mock {config.name}: {e}")
            return ServiceStatus(
                name=config.name,
                backend=ServiceBackend.MOCK,
                status="error",
                error_message=str(e),
            )

    async def _initialize_mock_services(self) -> dict[str, ServiceStatus]:
        """Initialize all services in mock mode."""
        services = {}
        for service_name, config in self.service_configs.items():
            services[service_name] = await self._initialize_mock_service(config)
        return services

    def _log_service_summary(self):
        """Log summary of service initialization."""
        logger.info("🔍 Service initialization summary:")
        for name, status in self.services.items():
            backend_icon = {"container": "🐳", "mock": "🎭", "direct": "🔗"}
            icon = backend_icon.get(status.backend.value, "❓")
            logger.info(f"  {icon} {name}: {status.backend.value} ({status.status})")
            if status.uri:
                logger.info(f"    URI: {status.uri}")
            if status.error_message:
                logger.info(f"    Error: {status.error_message}")

    async def get_neo4j_driver(self):
        """Get Neo4j driver (real or mock)."""
        neo4j_status = self.services.get("neo4j")
        if not neo4j_status or neo4j_status.backend == ServiceBackend.MOCK:
            return await self.mock_manager.get_neo4j_driver("bolt://mock:7687")
        # Return real Neo4j driver
        import neo4j

        return neo4j.AsyncGraphDatabase.driver(
            neo4j_status.uri, auth=("neo4j", "password")
        )

    async def get_redis_client(self):
        """Get Redis client (real or mock)."""
        redis_status = self.services.get("redis")
        if not redis_status or redis_status.backend == ServiceBackend.MOCK:
            return await self.mock_manager.get_redis_client("redis://mock:6379")
        # Return real Redis client
        import redis.asyncio as aioredis

        return aioredis.from_url(redis_status.uri)

    async def cleanup(self):
        """Clean up all services."""
        logger.info("🧹 Cleaning up enhanced service manager...")
        await self.mock_manager.cleanup()

        # Optionally stop containers that we started
        # (This could be configurable)
        for name, status in self.services.items():
            if status.backend == ServiceBackend.CONTAINER and status.container_id:
                logger.info(f"Container {name} ({status.container_id}) left running")

    def get_service_status(self) -> dict[str, dict[str, Any]]:
        """Get current status of all services."""
        status_dict = {}
        for name, status in self.services.items():
            status_dict[name] = {
                "backend": status.backend.value,
                "status": status.status,
                "uri": status.uri,
                "container_id": status.container_id,
                "error": status.error_message,
            }
        return status_dict
