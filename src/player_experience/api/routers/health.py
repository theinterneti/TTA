"""
Health check API endpoints for TTA system monitoring.

Provides endpoints for checking system health and component status.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.common.health_checks import (
    HealthStatus,
    check_agent_orchestration_health,
    check_neo4j_health,
    check_openrouter_health,
    check_redis_health,
    get_health_checker,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    components: dict[str, Any]
    timestamp: str | None = None


class ComponentHealthResponse(BaseModel):
    """Individual component health response."""

    component: str
    status: str
    message: str
    details: dict[str, Any] | None = None
    response_time_ms: float | None = None


# ---- Dependency Injection ----


async def get_redis_client():
    """Get Redis client for health checks."""
    try:
        import redis.asyncio as aioredis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        client = aioredis.from_url(redis_url, decode_responses=True)
        yield client
        await client.close()
    except Exception as e:
        logger.error(f"Failed to create Redis client: {e}")
        yield None


async def get_neo4j_driver():
    """Get Neo4j driver for health checks."""
    try:
        from neo4j import AsyncGraphDatabase

        from ..config import get_settings

        settings = get_settings()
        driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password)
        )
        yield driver
        await driver.close()
    except Exception as e:
        logger.error(f"Failed to create Neo4j driver: {e}")
        yield None


# ---- Health Check Endpoints ----


@router.get("/", response_model=HealthResponse)
async def system_health(
    redis_client=Depends(get_redis_client), neo4j_driver=Depends(get_neo4j_driver)
):
    """
    Get overall system health status.

    Checks all critical components and returns aggregated health status.
    """
    health_checker = get_health_checker()

    # Register checks
    if redis_client:
        health_checker.register_check("redis", lambda: check_redis_health(redis_client))

    if neo4j_driver:
        health_checker.register_check("neo4j", lambda: check_neo4j_health(neo4j_driver))

    health_checker.register_check(
        "agent_orchestration", lambda: check_agent_orchestration_health()
    )

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        health_checker.register_check(
            "openrouter", lambda: check_openrouter_health(openrouter_key)
        )

    # Run all checks
    overall_status, components = await health_checker.get_system_status()

    return HealthResponse(status=overall_status.value, components=components)


@router.get("/redis", response_model=ComponentHealthResponse)
async def redis_health(redis_client=Depends(get_redis_client)):
    """Check Redis connection health."""
    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis client not available",
        )

    result = await check_redis_health(redis_client)
    return ComponentHealthResponse(**result.to_dict())


@router.get("/neo4j", response_model=ComponentHealthResponse)
async def neo4j_health(neo4j_driver=Depends(get_neo4j_driver)):
    """Check Neo4j connection health."""
    if not neo4j_driver:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Neo4j driver not available",
        )

    result = await check_neo4j_health(neo4j_driver)
    return ComponentHealthResponse(**result.to_dict())


@router.get("/agents", response_model=ComponentHealthResponse)
async def agent_orchestration_health():
    """Check agent orchestration system health."""
    result = await check_agent_orchestration_health()
    return ComponentHealthResponse(**result.to_dict())


@router.get("/openrouter", response_model=ComponentHealthResponse)
async def openrouter_health():
    """Check OpenRouter API connectivity."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    result = await check_openrouter_health(api_key)
    return ComponentHealthResponse(**result.to_dict())


@router.get("/liveness")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the service is running (even if degraded).
    """
    return {"status": "alive"}


@router.get("/readiness")
async def readiness_probe(
    redis_client=Depends(get_redis_client), neo4j_driver=Depends(get_neo4j_driver)
):
    """
    Kubernetes readiness probe endpoint.

    Returns 200 only if critical services are healthy.
    """
    # Check critical services
    critical_checks = []

    if redis_client:
        redis_result = await check_redis_health(redis_client)
        critical_checks.append(redis_result.status == HealthStatus.HEALTHY)

    if neo4j_driver:
        neo4j_result = await check_neo4j_health(neo4j_driver)
        critical_checks.append(neo4j_result.status == HealthStatus.HEALTHY)

    # Service is ready if all critical checks pass
    if all(critical_checks):
        return {"status": "ready"}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Service not ready",
    )


@router.get("/startup")
async def startup_probe(
    redis_client=Depends(get_redis_client), neo4j_driver=Depends(get_neo4j_driver)
):
    """
    Kubernetes startup probe endpoint.

    Returns 200 once the service has completed initialization.
    """
    # Similar to readiness but with more lenient checks
    checks = []

    if redis_client:
        try:
            await redis_client.ping()
            checks.append(True)
        except Exception:
            checks.append(False)

    if neo4j_driver:
        try:
            await neo4j_driver.verify_connectivity()
            checks.append(True)
        except Exception:
            checks.append(False)

    if any(checks):  # At least one service is up
        return {"status": "started"}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Service still starting",
    )
