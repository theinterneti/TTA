"""
Test utilities package for TTA.

This package provides enhanced testing utilities including:
- Testcontainer reliability improvements
- Enhanced conftest fixtures
- Retry mechanisms and health checks
- Container diagnostics and logging
"""

from .enhanced_conftest import (
    skip_if_container_unavailable,
    wait_for_service_ready,
)
from .testcontainer_reliability import (
    ContainerHealthError,
    ContainerTimeoutError,
    HealthChecker,
    Neo4jHealthChecker,
    RedisHealthChecker,
    async_retry_with_backoff,
    container_logs_on_failure,
    enhanced_neo4j_container_setup,
    enhanced_redis_container_setup,
    retry_with_backoff,
)

__all__ = [
    # Retry mechanisms
    "retry_with_backoff",
    "async_retry_with_backoff",
    # Health checkers
    "HealthChecker",
    "Neo4jHealthChecker",
    "RedisHealthChecker",
    # Container setup
    "enhanced_neo4j_container_setup",
    "enhanced_redis_container_setup",
    # Utilities
    "container_logs_on_failure",
    "wait_for_service_ready",
    "skip_if_container_unavailable",
    # Exceptions
    "ContainerHealthError",
    "ContainerTimeoutError",
]
