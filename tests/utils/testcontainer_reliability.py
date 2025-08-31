"""
Enhanced reliability utilities for Testcontainers.

This module provides enhanced reliability features for Testcontainers including
retry mechanisms, health checks, and error handling improvements.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class ContainerHealthError(Exception):
    """Raised when container health checks fail."""

    pass


class ContainerTimeoutError(Exception):
    """Raised when container operations timeout."""

    pass


def retry_with_backoff(
    max_attempts: int = 10,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
):
    """
    Decorator for retrying operations with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each attempt
        exceptions: Tuple of exceptions to catch and retry on
        on_retry: Optional callback function called on each retry
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Last attempt failed, re-raise the exception
                        raise e

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor**attempt), max_delay)

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e)
                    else:
                        logger.debug(
                            f"Attempt {attempt + 1}/{max_attempts} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )

                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


async def async_retry_with_backoff(
    func: Callable,
    max_attempts: int = 10,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
    *args,
    **kwargs,
):
    """
    Async version of retry_with_backoff for async operations.
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e

            if attempt == max_attempts - 1:
                raise e

            delay = min(base_delay * (backoff_factor**attempt), max_delay)

            if on_retry:
                on_retry(attempt + 1, e)
            else:
                logger.debug(
                    f"Async attempt {attempt + 1}/{max_attempts} failed with {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )

            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception


class HealthChecker:
    """Enhanced health checking for containers."""

    def __init__(
        self,
        check_function: Callable,
        max_attempts: int = 20,
        check_interval: float = 1.0,
        timeout: float = 60.0,
        name: str = "container",
    ):
        self.check_function = check_function
        self.max_attempts = max_attempts
        self.check_interval = check_interval
        self.timeout = timeout
        self.name = name

    def wait_for_healthy(self, *args, **kwargs) -> bool:
        """
        Wait for container to become healthy.

        Returns:
            True if container becomes healthy, raises exception otherwise
        """
        start_time = time.time()

        for attempt in range(self.max_attempts):
            try:
                # Check if we've exceeded the timeout
                if time.time() - start_time > self.timeout:
                    raise ContainerTimeoutError(
                        f"{self.name} health check timed out after {self.timeout}s"
                    )

                # Perform health check
                result = self.check_function(*args, **kwargs)

                if result:
                    logger.info(f"{self.name} is healthy after {attempt + 1} attempts")
                    return True

            except Exception as e:
                logger.debug(
                    f"{self.name} health check attempt {attempt + 1}/{self.max_attempts} failed: {e}"
                )

                # If this is the last attempt, raise the exception
                if attempt == self.max_attempts - 1:
                    raise ContainerHealthError(
                        f"{self.name} failed health check after {self.max_attempts} attempts: {e}"
                    )

            # Wait before next attempt
            time.sleep(self.check_interval)

        raise ContainerHealthError(f"{self.name} never became healthy")


class Neo4jHealthChecker(HealthChecker):
    """Specialized health checker for Neo4j containers."""

    def __init__(self, **kwargs):
        super().__init__(
            check_function=self._neo4j_health_check,
            max_attempts=kwargs.get("max_attempts", 15),
            check_interval=kwargs.get("check_interval", 2.0),
            timeout=kwargs.get("timeout", 90.0),
            name="Neo4j",
        )

    def _neo4j_health_check(self, uri: str, username: str, password: str) -> bool:
        """Perform Neo4j-specific health check."""
        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import AuthError, ClientError, ServiceUnavailable

            driver = GraphDatabase.driver(uri, auth=(username, password))
            try:
                with driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    record = result.single()
                    return record and record["test"] == 1
            finally:
                driver.close()

        except (AuthError, ServiceUnavailable, ClientError) as e:
            # These are expected during startup, return False to retry
            logger.debug(f"Neo4j not ready: {type(e).__name__}: {e}")
            return False
        except Exception as e:
            # Unexpected error, log and return False
            logger.warning(f"Unexpected Neo4j health check error: {e}")
            return False


class RedisHealthChecker(HealthChecker):
    """Specialized health checker for Redis containers."""

    def __init__(self, **kwargs):
        super().__init__(
            check_function=self._redis_health_check,
            max_attempts=kwargs.get("max_attempts", 10),
            check_interval=kwargs.get("check_interval", 1.0),
            timeout=kwargs.get("timeout", 30.0),
            name="Redis",
        )

    def _redis_health_check(self, connection_url: str) -> bool:
        """Perform Redis-specific health check."""
        try:
            import redis

            client = redis.from_url(connection_url)
            try:
                # Perform ping and basic operations
                pong = client.ping()
                if not pong:
                    return False

                # Test basic set/get operations
                test_key = "health_check_test"
                test_value = "ok"
                client.set(test_key, test_value, ex=10)  # Expire in 10 seconds
                retrieved_value = client.get(test_key)
                client.delete(test_key)

                return retrieved_value and retrieved_value.decode() == test_value

            finally:
                client.close()

        except Exception as e:
            logger.debug(f"Redis not ready: {type(e).__name__}: {e}")
            return False


def enhanced_neo4j_container_setup(container_config: dict[str, Any]) -> dict[str, Any]:
    """
    Enhanced setup for Neo4j containers with improved reliability.

    Args:
        container_config: Basic container configuration

    Returns:
        Enhanced configuration with connection details
    """
    from testcontainers.neo4j import Neo4jContainer

    # Create container with enhanced configuration
    container = (
        Neo4jContainer(container_config.get("image", "neo4j:5-community"))
        .with_env("NEO4J_AUTH", container_config.get("auth", "neo4j/testpassword"))
        .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
        .with_env("NEO4J_dbms_memory_heap_initial__size", "512m")
        .with_env("NEO4J_dbms_memory_heap_max__size", "1G")
        .with_env("NEO4J_dbms_memory_pagecache_size", "512m")
        .with_env("NEO4J_dbms_logs_debug_level", "INFO")
    )

    # Add any additional environment variables
    for key, value in container_config.get("env", {}).items():
        container = container.with_env(key, value)

    with container as neo4j:
        uri = neo4j.get_connection_url()
        username, password = container_config.get("auth", "neo4j/testpassword").split(
            "/"
        )

        # Use enhanced health checker
        health_checker = Neo4jHealthChecker()
        health_checker.wait_for_healthy(uri, username, password)

        yield {
            "uri": uri,
            "username": username,
            "password": password,
            "container": neo4j,
        }


def enhanced_redis_container_setup(container_config: dict[str, Any]) -> dict[str, Any]:
    """
    Enhanced setup for Redis containers with improved reliability.

    Args:
        container_config: Basic container configuration

    Returns:
        Enhanced configuration with connection details
    """
    from testcontainers.redis import RedisContainer

    # Create container with enhanced configuration
    container = RedisContainer(container_config.get("image", "redis:7-alpine"))

    # Add any additional configuration
    if "password" in container_config:
        container = container.with_command(
            f"redis-server --requirepass {container_config['password']}"
        )

    with container as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)

        # Build connection URL
        password = container_config.get("password")
        if password:
            connection_url = f"redis://:{password}@{host}:{port}/0"
        else:
            connection_url = f"redis://{host}:{port}/0"

        # Use enhanced health checker
        health_checker = RedisHealthChecker()
        health_checker.wait_for_healthy(connection_url)

        yield {
            "connection_url": connection_url,
            "host": host,
            "port": port,
            "password": password,
            "container": redis,
        }


def container_logs_on_failure(container, max_lines: int = 100):
    """
    Decorator to capture and log container logs on test failure.

    Args:
        container: The container instance
        max_lines: Maximum number of log lines to capture
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                try:
                    # Capture container logs
                    logs = container.get_logs()
                    if isinstance(logs, tuple):
                        stdout, stderr = logs
                        log_output = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                    else:
                        log_output = str(logs)

                    # Limit log output
                    lines = log_output.split("\n")
                    if len(lines) > max_lines:
                        lines = lines[-max_lines:]
                        log_output = "\n".join(["..."] + lines)

                    logger.error(f"Container logs on failure:\n{log_output}")

                except Exception as log_error:
                    logger.warning(f"Failed to capture container logs: {log_error}")

                # Re-raise the original exception
                raise e

        return wrapper

    return decorator
