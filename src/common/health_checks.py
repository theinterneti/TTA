"""

# Logseq: [[TTA.dev/Common/Health_checks]]
System health check utilities for TTA production readiness.

Provides unified health check interface for all system components:
- Database connections (Redis, Neo4j)
- Agent orchestration system
- External services (OpenRouter)
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(StrEnum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    component: str
    status: HealthStatus
    message: str
    details: dict[str, Any] | None = None
    checked_at: datetime | None = None
    response_time_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details or {},
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
            "response_time_ms": self.response_time_ms,
        }


class HealthChecker:
    """Unified health checker for TTA system components."""

    def __init__(self):
        """Initialize health checker."""
        self._checks: dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable) -> None:
        """
        Register a health check function.

        Args:
            name: Component name
            check_func: Async function that returns HealthCheckResult
        """
        self._checks[name] = check_func
        logger.debug(f"Registered health check: {name}")

    async def check_component(self, name: str) -> HealthCheckResult:
        """
        Run health check for a specific component.

        Args:
            name: Component name

        Returns:
            HealthCheckResult
        """
        if name not in self._checks:
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNKNOWN,
                message=f"No health check registered for {name}",
                checked_at=datetime.now(UTC),
            )

        start_time = asyncio.get_running_loop().time()
        try:
            result = await self._checks[name]()
            end_time = asyncio.get_running_loop().time()
            result.response_time_ms = (end_time - start_time) * 1000
            result.checked_at = datetime.now(UTC)
            return result
        except Exception as e:
            end_time = asyncio.get_running_loop().time()
            logger.error(f"Health check failed for {name}: {e}")
            return HealthCheckResult(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                checked_at=datetime.now(UTC),
                response_time_ms=(end_time - start_time) * 1000,
            )

    async def check_all(self) -> dict[str, HealthCheckResult]:
        """
        Run all registered health checks.

        Returns:
            Dictionary of component name to HealthCheckResult
        """
        results = {}
        for name in self._checks:
            results[name] = await self.check_component(name)
        return results

    async def get_system_status(self) -> tuple[HealthStatus, dict[str, Any]]:
        """
        Get overall system health status.

        Returns:
            Tuple of (overall_status, detailed_results)
        """
        results = await self.check_all()

        # Determine overall status
        statuses = [r.status for r in results.values()]
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall = HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        return overall, {name: result.to_dict() for name, result in results.items()}


# Global health checker instance
_health_checker: HealthChecker | None = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# ---- Standard Health Check Functions ----


async def check_redis_health(redis_client) -> HealthCheckResult:
    """
    Check Redis connection health.

    Args:
        redis_client: Redis client instance

    Returns:
        HealthCheckResult
    """
    try:
        await redis_client.ping()
        info = await redis_client.info("server")
        return HealthCheckResult(
            component="redis",
            status=HealthStatus.HEALTHY,
            message="Redis connection healthy",
            details={
                "version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
            },
        )
    except Exception as e:
        return HealthCheckResult(
            component="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}",
        )


async def check_neo4j_health(neo4j_driver) -> HealthCheckResult:
    """
    Check Neo4j connection health.

    Args:
        neo4j_driver: Neo4j driver instance

    Returns:
        HealthCheckResult
    """
    try:
        await neo4j_driver.verify_connectivity()

        # Get database info
        async with neo4j_driver.session() as session:
            result = await session.run("CALL dbms.components() YIELD name, versions")
            record = await result.single()
            version = record["versions"][0] if record else "unknown"

        return HealthCheckResult(
            component="neo4j",
            status=HealthStatus.HEALTHY,
            message="Neo4j connection healthy",
            details={"version": version},
        )
    except Exception as e:
        return HealthCheckResult(
            component="neo4j",
            status=HealthStatus.UNHEALTHY,
            message=f"Neo4j connection failed: {str(e)}",
        )


async def check_agent_orchestration_health(
    agent_registry=None, workflow_manager=None
) -> HealthCheckResult:
    """
    Check agent orchestration system health.

    Args:
        agent_registry: Agent registry instance
        workflow_manager: Workflow manager instance

    Returns:
        HealthCheckResult
    """
    try:
        details = {}

        if agent_registry:
            # Check registered agents
            # Note: Actual implementation depends on agent registry interface
            details["agents_registered"] = "available"

        if workflow_manager:
            # Check workflow manager
            details["workflow_manager"] = "available"

        if not agent_registry and not workflow_manager:
            return HealthCheckResult(
                component="agent_orchestration",
                status=HealthStatus.DEGRADED,
                message="Agent orchestration not fully initialized",
                details=details,
            )

        return HealthCheckResult(
            component="agent_orchestration",
            status=HealthStatus.HEALTHY,
            message="Agent orchestration system healthy",
            details=details,
        )
    except Exception as e:
        return HealthCheckResult(
            component="agent_orchestration",
            status=HealthStatus.UNHEALTHY,
            message=f"Agent orchestration check failed: {str(e)}",
        )


async def check_dolt_health(database_url: str | None = None) -> HealthCheckResult:
    """Check Dolt SQL server connection health.

    Attempts a lightweight connection using aiomysql. Degrades gracefully
    when Dolt is not configured or the aiomysql driver is not installed.

    Args:
        database_url: mysql+aiomysql:// connection string (falls back to
                      DOLT_DATABASE_URL env var).

    Returns:
        HealthCheckResult
    """
    import os

    url = database_url or os.getenv("DOLT_DATABASE_URL")
    if not url:
        return HealthCheckResult(
            component="dolt",
            status=HealthStatus.DEGRADED,
            message="Dolt not configured (DOLT_DATABASE_URL not set)",
        )

    try:
        # Parse host/port/password from the URL for a raw ping
        # mysql+aiomysql://root:<pw>@<host>:<port>/<db>
        from urllib.parse import urlparse

        import aiomysql  # type: ignore[import-not-found]

        parsed = urlparse(url.replace("mysql+aiomysql://", "mysql://"))
        conn = await aiomysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
            db=parsed.path.lstrip("/") or "tta",
            connect_timeout=5,
        )
        async with conn.cursor() as cur:
            await cur.execute("SELECT @@version, dolt_version()")
            row = await cur.fetchone()
            mysql_version = row[0] if row else "unknown"
            dolt_version = row[1] if row else "unknown"
        conn.close()
        return HealthCheckResult(
            component="dolt",
            status=HealthStatus.HEALTHY,
            message="Dolt SQL server connection healthy",
            details={"mysql_version": mysql_version, "dolt_version": dolt_version},
        )
    except ImportError:
        return HealthCheckResult(
            component="dolt",
            status=HealthStatus.DEGRADED,
            message="aiomysql not installed; Dolt health check skipped",
        )
    except Exception as e:
        return HealthCheckResult(
            component="dolt",
            status=HealthStatus.UNHEALTHY,
            message=f"Dolt connection failed: {str(e)}",
        )


async def check_openrouter_health(api_key: str | None = None) -> HealthCheckResult:
    """
    Check OpenRouter API connectivity.

    Args:
        api_key: OpenRouter API key (optional)

    Returns:
        HealthCheckResult
    """
    if not api_key:
        return HealthCheckResult(
            component="openrouter",
            status=HealthStatus.DEGRADED,
            message="OpenRouter API key not configured",
        )

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0,
            )

            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    component="openrouter",
                    status=HealthStatus.HEALTHY,
                    message="OpenRouter API accessible",
                    details={"models_available": len(data.get("data", []))},
                )
            return HealthCheckResult(
                component="openrouter",
                status=HealthStatus.DEGRADED,
                message=f"OpenRouter API returned status {response.status_code}",
            )
    except Exception as e:
        return HealthCheckResult(
            component="openrouter",
            status=HealthStatus.UNHEALTHY,
            message=f"OpenRouter API check failed: {str(e)}",
        )
