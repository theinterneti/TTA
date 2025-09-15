"""
Enhanced conftest utilities with improved Testcontainers reliability.

This module provides enhanced fixtures that can be used alongside or as replacements
for the existing conftest.py fixtures, with improved error handling and reliability.
"""

import logging
import os
from functools import wraps

import pytest

from .testcontainer_reliability import (
    ContainerHealthError,
    ContainerTimeoutError,
    Neo4jHealthChecker,
    RedisHealthChecker,
    enhanced_neo4j_container_setup,
    enhanced_redis_container_setup,
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def enhanced_neo4j_container(pytestconfig):
    """
    Enhanced Neo4j container with improved reliability and error handling.

    This fixture provides the same interface as the original neo4j_container
    but with enhanced health checks, retry mechanisms, and error handling.
    """
    if not (
        pytestconfig.getoption("--neo4j")
        or os.environ.get("RUN_NEO4J_TESTS") in {"1", "true", "True"}
    ):
        pytest.skip("Neo4j not requested; use --neo4j or RUN_NEO4J_TESTS=1")

    # If CI provides a service, prefer it to avoid nested containers
    svc_uri = os.environ.get("TEST_NEO4J_URI")
    if svc_uri:
        # Even for CI services, verify connectivity with enhanced health check
        username = os.environ.get("TEST_NEO4J_USERNAME", "neo4j")
        password = os.environ.get("TEST_NEO4J_PASSWORD", "testpassword")

        health_checker = Neo4jHealthChecker(max_attempts=10, timeout=30.0)
        try:
            health_checker.wait_for_healthy(svc_uri, username, password)
            yield {
                "uri": svc_uri,
                "username": username,
                "password": password,
            }
            return
        except (ContainerHealthError, ContainerTimeoutError) as e:
            logger.warning(f"CI Neo4j service health check failed: {e}")
            pytest.skip(f"CI Neo4j service not healthy: {e}")

    # Use enhanced container setup
    container_config = {
        "image": "neo4j:5-community",
        "auth": "neo4j/testpassword",
        "env": {
            "NEO4J_ACCEPT_LICENSE_AGREEMENT": "yes",
            # Performance optimizations for testing
            "NEO4J_dbms_memory_heap_initial__size": "512m",
            "NEO4J_dbms_memory_heap_max__size": "1G",
            "NEO4J_dbms_memory_pagecache_size": "512m",
            # Reduce startup time
            "NEO4J_dbms_logs_debug_level": "WARN",
            "NEO4J_dbms_security_procedures_unrestricted": "apoc.*",
        },
    }

    try:
        yield from enhanced_neo4j_container_setup(container_config)
    except Exception as e:
        logger.error(f"Enhanced Neo4j container setup failed: {e}")
        # Fall back to skip if container setup fails
        pytest.skip(f"Neo4j container setup failed: {e}")


@pytest.fixture(scope="session")
def enhanced_redis_container(pytestconfig):
    """
    Enhanced Redis container with improved reliability and error handling.

    This fixture provides the same interface as the original redis_container
    but with enhanced health checks, retry mechanisms, and error handling.
    """
    if not (
        pytestconfig.getoption("--redis")
        or os.environ.get("RUN_REDIS_TESTS") in {"1", "true", "True"}
    ):
        pytest.skip("Redis container not requested; use --redis or RUN_REDIS_TESTS=1")

    # Prefer CI-provided service if available
    svc_uri = os.environ.get("TEST_REDIS_URI")
    if svc_uri:
        # Verify CI service connectivity
        health_checker = RedisHealthChecker(max_attempts=5, timeout=15.0)
        try:
            health_checker.wait_for_healthy(svc_uri)
            yield svc_uri
            return
        except (ContainerHealthError, ContainerTimeoutError) as e:
            logger.warning(f"CI Redis service health check failed: {e}")
            pytest.skip(f"CI Redis service not healthy: {e}")

    # Use enhanced container setup
    container_config = {
        "image": "redis:7-alpine",
        # Add password for testing authentication
        "password": "testpassword123",
    }

    prev_env = os.environ.get("TEST_REDIS_URI")
    try:
        for container_info in enhanced_redis_container_setup(container_config):
            connection_url = container_info["connection_url"]
            # Export for tests that read from env
            os.environ["TEST_REDIS_URI"] = connection_url
            yield connection_url
            break
    except Exception as e:
        logger.error(f"Enhanced Redis container setup failed: {e}")
        pytest.skip(f"Redis container setup failed: {e}")
    finally:
        # Restore previous value
        if prev_env is None:
            os.environ.pop("TEST_REDIS_URI", None)
        else:
            os.environ["TEST_REDIS_URI"] = prev_env


@pytest.fixture(scope="session")
def enhanced_neo4j_driver(enhanced_neo4j_container):
    """
    Enhanced Neo4j driver with improved connection reliability.

    This fixture provides a Neo4j driver with enhanced retry logic
    and connection validation.
    """
    from neo4j import GraphDatabase
    from neo4j.exceptions import AuthError, ClientError, ServiceUnavailable

    uri = enhanced_neo4j_container["uri"]
    username = enhanced_neo4j_container["username"]
    password = enhanced_neo4j_container["password"]

    @retry_with_backoff(
        max_attempts=5,
        base_delay=1.0,
        max_delay=5.0,
        exceptions=(AuthError, ServiceUnavailable, ClientError),
        on_retry=lambda attempt, exc: logger.debug(
            f"Neo4j driver connection attempt {attempt} failed: {type(exc).__name__}: {exc}"
        ),
    )
    def create_driver():
        driver = GraphDatabase.driver(uri, auth=(username, password))
        # Verify connectivity
        with driver.session() as session:
            session.run("RETURN 1").single()
        return driver

    try:
        driver = create_driver()
        yield driver
    finally:
        try:
            driver.close()
        except Exception as e:
            logger.warning(f"Error closing Neo4j driver: {e}")


@pytest.fixture(scope="session")
def enhanced_redis_client_sync(enhanced_redis_container):
    """
    Enhanced synchronous Redis client with improved connection reliability.
    """
    import redis

    @retry_with_backoff(
        max_attempts=5,
        base_delay=0.5,
        max_delay=3.0,
        exceptions=(redis.ConnectionError, redis.TimeoutError),
        on_retry=lambda attempt, exc: logger.debug(
            f"Redis client connection attempt {attempt} failed: {type(exc).__name__}: {exc}"
        ),
    )
    def create_client():
        client = redis.from_url(enhanced_redis_container)
        # Verify connectivity with ping
        client.ping()
        return client

    try:
        client = create_client()
        yield client
    finally:
        try:
            client.close()
        except Exception as e:
            logger.warning(f"Error closing Redis client: {e}")


@pytest.fixture()
async def enhanced_redis_client_async(enhanced_redis_container):
    """
    Enhanced asynchronous Redis client with improved connection reliability.
    """
    import redis.asyncio as aioredis

    async def create_async_client():
        client = aioredis.from_url(enhanced_redis_container)
        # Verify connectivity with ping
        await client.ping()
        return client

    from .testcontainer_reliability import async_retry_with_backoff

    try:
        client = await async_retry_with_backoff(
            create_async_client,
            max_attempts=5,
            base_delay=0.5,
            max_delay=3.0,
            exceptions=(aioredis.ConnectionError, aioredis.TimeoutError),
            on_retry=lambda attempt, exc: logger.debug(
                f"Async Redis client connection attempt {attempt} failed: {type(exc).__name__}: {exc}"
            ),
        )
        yield client
    finally:
        try:
            await client.aclose()
        except Exception as e:
            logger.warning(f"Error closing async Redis client: {e}")


@pytest.fixture(autouse=True)
def container_failure_diagnostics(request):
    """
    Automatically capture container diagnostics on test failures.

    This fixture runs automatically and captures container logs and status
    information when tests fail, helping with debugging.
    """
    yield  # Run the test

    # Check if test failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        # Try to capture container information
        try:
            # Look for container fixtures in the test
            container_fixtures = []
            for fixture_name in request.fixturenames:
                if "container" in fixture_name.lower():
                    try:
                        fixture_value = request.getfixturevalue(fixture_name)
                        if hasattr(fixture_value, "get_logs"):
                            container_fixtures.append((fixture_name, fixture_value))
                    except Exception:
                        pass  # Fixture might not be available or failed

            # Capture logs from any containers found
            for fixture_name, container in container_fixtures:
                try:
                    logs = container.get_logs()
                    logger.error(f"Container logs for {fixture_name}:\n{logs}")
                except Exception as e:
                    logger.warning(f"Failed to capture logs for {fixture_name}: {e}")

        except Exception as e:
            logger.warning(f"Failed to capture container diagnostics: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results for container diagnostics.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Utility functions for test reliability
def wait_for_service_ready(
    check_function: callable,
    service_name: str = "service",
    max_attempts: int = 30,
    delay: float = 1.0,
    timeout: float = 60.0,
) -> bool:
    """
    Wait for a service to become ready with configurable parameters.

    Args:
        check_function: Function that returns True when service is ready
        service_name: Name of the service for logging
        max_attempts: Maximum number of check attempts
        delay: Delay between attempts in seconds
        timeout: Maximum total time to wait in seconds

    Returns:
        True if service becomes ready, False otherwise
    """
    import time

    start_time = time.time()

    for attempt in range(max_attempts):
        if time.time() - start_time > timeout:
            logger.error(f"{service_name} readiness check timed out after {timeout}s")
            return False

        try:
            if check_function():
                logger.info(f"{service_name} is ready after {attempt + 1} attempts")
                return True
        except Exception as e:
            logger.debug(
                f"{service_name} readiness check attempt {attempt + 1} failed: {e}"
            )

        time.sleep(delay)

    logger.error(f"{service_name} never became ready after {max_attempts} attempts")
    return False


def skip_if_container_unavailable(container_type: str):
    """
    Decorator to skip tests if container type is not available.

    Args:
        container_type: Type of container ('neo4j', 'redis', etc.)
    """

    def decorator(func):
        @pytest.mark.skipif(
            os.environ.get(f"RUN_{container_type.upper()}_TESTS")
            not in {"1", "true", "True"},
            reason=f"{container_type} container tests not enabled",
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
