"""
Docker Container Management for TTA Comprehensive Test Battery

This module provides Docker container detection, health checking, and management
capabilities that integrate with our existing mock service architecture.
"""

import logging
from dataclasses import dataclass
from enum import Enum

import docker

logger = logging.getLogger(__name__)


class ContainerStatus(Enum):
    """Container status enumeration."""

    NOT_AVAILABLE = "not_available"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ContainerInfo:
    """Container information."""

    name: str
    image: str
    status: ContainerStatus
    ports: dict[str, str]
    health_status: str | None = None
    container_id: str | None = None
    error_message: str | None = None


class DockerManager:
    """
    Docker container manager for TTA test services.

    Provides container detection, health checking, and management
    while maintaining compatibility with mock fallback architecture.
    """

    def __init__(self):
        self.docker_client: docker.DockerClient | None = None
        self.docker_available = False
        self._initialize_docker()

    def _initialize_docker(self):
        """Initialize Docker client if available."""
        try:
            self.docker_client = docker.from_env()
            # Test Docker connectivity
            self.docker_client.ping()
            self.docker_available = True
            logger.info("✅ Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️  Docker not available: {e}")
            self.docker_available = False

    def is_docker_available(self) -> bool:
        """Check if Docker is available."""
        return self.docker_available

    def get_container_info(self, container_name: str) -> ContainerInfo:
        """Get information about a specific container."""
        if not self.docker_available:
            return ContainerInfo(
                name=container_name,
                image="unknown",
                status=ContainerStatus.NOT_AVAILABLE,
                ports={},
                error_message="Docker not available",
            )

        try:
            container = self.docker_client.containers.get(container_name)

            # Get container status
            container.reload()
            status_map = {
                "running": ContainerStatus.HEALTHY,
                "exited": ContainerStatus.STOPPED,
                "created": ContainerStatus.STOPPED,
                "restarting": ContainerStatus.STARTING,
                "removing": ContainerStatus.STOPPING,
                "paused": ContainerStatus.STOPPED,
                "dead": ContainerStatus.UNHEALTHY,
            }

            status = status_map.get(container.status, ContainerStatus.UNKNOWN)

            # Get port mappings
            ports = {}
            if container.ports:
                for container_port, host_bindings in container.ports.items():
                    if host_bindings:
                        host_port = host_bindings[0]["HostPort"]
                        ports[container_port] = host_port

            # Get health status if available
            health_status = None
            if (
                hasattr(container.attrs, "State")
                and "Health" in container.attrs["State"]
            ):
                health_status = container.attrs["State"]["Health"]["Status"]

            return ContainerInfo(
                name=container_name,
                image=container.image.tags[0] if container.image.tags else "unknown",
                status=status,
                ports=ports,
                health_status=health_status,
                container_id=container.id[:12],
            )

        except docker.errors.NotFound:
            return ContainerInfo(
                name=container_name,
                image="unknown",
                status=ContainerStatus.STOPPED,
                ports={},
                error_message="Container not found",
            )
        except Exception as e:
            logger.error(f"Error getting container info for {container_name}: {e}")
            return ContainerInfo(
                name=container_name,
                image="unknown",
                status=ContainerStatus.UNKNOWN,
                ports={},
                error_message=str(e),
            )

    def list_containers(self, filters: dict | None = None) -> list[ContainerInfo]:
        """List all containers matching filters."""
        if not self.docker_available:
            return []

        try:
            containers = self.docker_client.containers.list(all=True, filters=filters)
            container_infos = []

            for container in containers:
                info = self.get_container_info(container.name)
                container_infos.append(info)

            return container_infos

        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []

    def start_container(self, container_name: str) -> bool:
        """Start a container if it exists."""
        if not self.docker_available:
            logger.warning("Docker not available, cannot start container")
            return False

        try:
            container = self.docker_client.containers.get(container_name)
            if container.status != "running":
                container.start()
                logger.info(f"✅ Started container: {container_name}")
                return True
            logger.info(f"Container {container_name} already running")
            return True

        except docker.errors.NotFound:
            logger.error(f"Container {container_name} not found")
            return False
        except Exception as e:
            logger.error(f"Error starting container {container_name}: {e}")
            return False

    def stop_container(self, container_name: str) -> bool:
        """Stop a container if it's running."""
        if not self.docker_available:
            logger.warning("Docker not available, cannot stop container")
            return False

        try:
            container = self.docker_client.containers.get(container_name)
            if container.status == "running":
                container.stop()
                logger.info(f"✅ Stopped container: {container_name}")
                return True
            logger.info(f"Container {container_name} not running")
            return True

        except docker.errors.NotFound:
            logger.error(f"Container {container_name} not found")
            return False
        except Exception as e:
            logger.error(f"Error stopping container {container_name}: {e}")
            return False

    def get_container_logs(self, container_name: str, tail: int = 50) -> str:
        """Get recent logs from a container."""
        if not self.docker_available:
            return "Docker not available"

        try:
            container = self.docker_client.containers.get(container_name)
            logs = container.logs(tail=tail, timestamps=True)
            return logs.decode("utf-8")

        except docker.errors.NotFound:
            return f"Container {container_name} not found"
        except Exception as e:
            return f"Error getting logs: {e}"

    def execute_command(self, container_name: str, command: str) -> tuple[int, str]:
        """Execute a command in a running container."""
        if not self.docker_available:
            return 1, "Docker not available"

        try:
            container = self.docker_client.containers.get(container_name)
            if container.status != "running":
                return 1, "Container not running"

            result = container.exec_run(command)
            return result.exit_code, result.output.decode("utf-8")

        except docker.errors.NotFound:
            return 1, f"Container {container_name} not found"
        except Exception as e:
            return 1, f"Error executing command: {e}"
