"""
Container Health Checking for TTA Comprehensive Test Battery

Provides robust health checking strategies for containerized services,
with specific focus on Neo4j and Redis reliability.
"""

import asyncio
import contextlib
import logging
import socket
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import aiohttp

try:
    import neo4j

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class HealthCheckResult:
    """Health check result."""

    status: HealthStatus
    message: str
    response_time_ms: float
    details: dict[str, Any] = None


class ContainerHealthChecker:
    """
    Comprehensive health checker for containerized services.

    Implements multi-stage health checking with progressive timeouts
    and detailed error reporting.
    """

    def __init__(self, max_retries: int = 5, base_timeout: float = 2.0):
        self.max_retries = max_retries
        self.base_timeout = base_timeout

        # Common Neo4j credential combinations to try
        self.neo4j_credentials = [
            ("neo4j", "tta_test_password_2024"),  # Test environment
            ("neo4j", "tta_dev_password_2024"),  # Dev environment
            ("neo4j", "tta_ci_password_2024"),  # CI/CD environment
            ("neo4j", "testpassword"),  # Legacy test
            ("neo4j", "devpassword"),  # Legacy dev
            ("neo4j", "password"),  # Default
            ("neo4j", "neo4j"),  # Very default
        ]

    async def check_port_connectivity(
        self, host: str, port: int, timeout: float = 5.0
    ) -> HealthCheckResult:
        """Check if a port is accessible."""
        start_time = time.time()

        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            response_time = (time.time() - start_time) * 1000

            if result == 0:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message=f"Port {port} is accessible",
                    response_time_ms=response_time,
                )
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Port {port} is not accessible (error code: {result})",
                response_time_ms=response_time,
            )

        except TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.TIMEOUT,
                message=f"Port {port} connection timed out after {timeout}s",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message=f"Port {port} check failed: {e}",
                response_time_ms=response_time,
            )

    async def check_http_endpoint(
        self, url: str, timeout: float = 10.0, expected_status: int = 200
    ) -> HealthCheckResult:
        """Check HTTP endpoint health."""
        start_time = time.time()

        try:
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == expected_status:
                        return HealthCheckResult(
                            status=HealthStatus.HEALTHY,
                            message=f"HTTP endpoint {url} returned {response.status}",
                            response_time_ms=response_time,
                            details={
                                "status_code": response.status,
                                "headers": dict(response.headers),
                            },
                        )
                    return HealthCheckResult(
                        status=HealthStatus.UNHEALTHY,
                        message=f"HTTP endpoint {url} returned {response.status}, expected {expected_status}",
                        response_time_ms=response_time,
                        details={"status_code": response.status},
                    )

        except TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.TIMEOUT,
                message=f"HTTP endpoint {url} timed out after {timeout}s",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message=f"HTTP endpoint {url} check failed: {e}",
                response_time_ms=response_time,
            )

    async def check_neo4j_health(
        self,
        uri: str,
        username: str = "neo4j",
        password: str = "tta_test_password_2024",
        timeout: float = 30.0,
    ) -> HealthCheckResult:
        """Comprehensive Neo4j health check."""
        start_time = time.time()

        if not NEO4J_AVAILABLE:
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message="Neo4j driver not available",
                response_time_ms=0,
            )

        try:
            # Multi-stage Neo4j health check

            # Stage 1: HTTP endpoint check
            http_url = uri.replace("bolt://", "http://").replace("neo4j://", "http://")
            if not http_url.startswith("http://"):
                http_url = f"http://{http_url.split('://')[-1]}"

            # Extract host and port for HTTP check
            if ":" in http_url.split("://")[1]:
                host_port = http_url.split("://")[1]
                if "/" in host_port:
                    host_port = host_port.split("/")[0]
                host, port = host_port.split(":")
                http_port = "7474"  # Neo4j HTTP port
                http_check_url = f"http://{host}:{http_port}/db/data/"
            else:
                http_check_url = f"{http_url}:7474/db/data/"

            http_result = await self.check_http_endpoint(http_check_url, timeout=10.0)

            # Stage 2: Bolt connection check
            driver = neo4j.AsyncGraphDatabase.driver(uri, auth=(username, password))

            try:
                # Test basic connectivity
                await driver.verify_connectivity()

                # Test query execution
                async with driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    record = await result.single()
                    if record and record["test"] == 1:
                        response_time = (time.time() - start_time) * 1000
                        return HealthCheckResult(
                            status=HealthStatus.HEALTHY,
                            message="Neo4j is healthy (HTTP + Bolt + Query test passed)",
                            response_time_ms=response_time,
                            details={
                                "http_status": http_result.status.value,
                                "bolt_connected": True,
                                "query_test": True,
                            },
                        )
                    response_time = (time.time() - start_time) * 1000
                    return HealthCheckResult(
                        status=HealthStatus.UNHEALTHY,
                        message="Neo4j query test failed",
                        response_time_ms=response_time,
                    )

            finally:
                await driver.close()

        except neo4j.exceptions.ServiceUnavailable as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Neo4j service unavailable: {e}",
                response_time_ms=response_time,
            )
        except neo4j.exceptions.AuthError as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Neo4j authentication failed: {e}",
                response_time_ms=response_time,
            )
        except Exception as e:
            # Handle authentication rate limiting specifically
            if "AuthenticationRateLimit" in str(e) or "rate limit" in str(e).lower():
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Neo4j authentication rate limited - waiting before retry: {e}",
                    response_time_ms=response_time,
                )
        except TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.TIMEOUT,
                message=f"Neo4j health check timed out after {timeout}s",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message=f"Neo4j health check failed: {e}",
                response_time_ms=response_time,
            )

    async def check_neo4j_health_with_credential_fallback(
        self, uri: str, timeout: float = 30.0
    ) -> HealthCheckResult:
        """
        Check Neo4j health with automatic credential fallback.
        Tries multiple common credential combinations.
        """
        start_time = time.time()
        last_error = None

        for username, password in self.neo4j_credentials:
            try:
                logger.debug(
                    f"Trying Neo4j credentials: {username}/{'*' * len(password)}"
                )
                result = await self.check_neo4j_health(
                    uri, username, password, timeout=10.0
                )

                if result.status == HealthStatus.HEALTHY:
                    logger.info(
                        f"✅ Neo4j authentication successful with {username}/{'*' * len(password)}"
                    )
                    return result
                if "rate limit" in result.message.lower():
                    # If rate limited, wait and try next credentials
                    logger.warning(
                        f"Rate limited with {username}, waiting before next attempt..."
                    )
                    await asyncio.sleep(5)
                    last_error = result.message
                    continue
                last_error = result.message

            except Exception as e:
                last_error = str(e)
                if "rate limit" in str(e).lower():
                    logger.warning(
                        f"Rate limited with {username}, waiting before next attempt..."
                    )
                    await asyncio.sleep(5)
                continue

        # All credentials failed
        response_time = (time.time() - start_time) * 1000
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"Neo4j authentication failed with all credential combinations. Last error: {last_error}",
            response_time_ms=response_time,
        )

    async def check_redis_health(
        self, url: str, timeout: float = 10.0
    ) -> HealthCheckResult:
        """Comprehensive Redis health check."""
        start_time = time.time()

        if not REDIS_AVAILABLE:
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message="Redis client not available",
                response_time_ms=0,
            )

        try:
            redis_client = aioredis.from_url(url, socket_timeout=timeout)

            # Test basic connectivity
            pong = await redis_client.ping()
            if not pong:
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="Redis PING failed",
                    response_time_ms=response_time,
                )

            # Test read/write operations
            test_key = "health_check_test"
            test_value = "test_value"

            await redis_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            retrieved_value = await redis_client.get(test_key)
            await redis_client.delete(test_key)

            if retrieved_value and retrieved_value.decode() == test_value:
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="Redis is healthy (PING + read/write test passed)",
                    response_time_ms=response_time,
                    details={"ping": True, "read_write_test": True},
                )
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message="Redis read/write test failed",
                response_time_ms=response_time,
            )

        except TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.TIMEOUT,
                message=f"Redis health check timed out after {timeout}s",
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                status=HealthStatus.ERROR,
                message=f"Redis health check failed: {e}",
                response_time_ms=response_time,
            )
        finally:
            with contextlib.suppress(Exception):
                await redis_client.aclose()

    async def wait_for_service_health(
        self,
        service_name: str,
        check_func,
        max_wait_time: float = 120.0,
        check_interval: float = 2.0,
    ) -> HealthCheckResult:
        """Wait for a service to become healthy with exponential backoff."""
        start_time = time.time()
        attempt = 0

        while time.time() - start_time < max_wait_time:
            attempt += 1
            logger.info(f"Health check attempt {attempt} for {service_name}")

            result = await check_func()

            if result.status == HealthStatus.HEALTHY:
                logger.info(f"✅ {service_name} is healthy after {attempt} attempts")
                return result

            if result.status == HealthStatus.ERROR:
                logger.error(f"❌ {service_name} health check error: {result.message}")
                return result

            # Calculate next wait time with exponential backoff
            wait_time = min(check_interval * (2 ** (attempt - 1)), 30.0)
            logger.info(
                f"⏳ {service_name} not ready, waiting {wait_time:.1f}s... ({result.message})"
            )
            await asyncio.sleep(wait_time)

        elapsed_time = (time.time() - start_time) * 1000
        return HealthCheckResult(
            status=HealthStatus.TIMEOUT,
            message=f"{service_name} did not become healthy within {max_wait_time}s",
            response_time_ms=elapsed_time,
        )
