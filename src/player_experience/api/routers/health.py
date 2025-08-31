"""
Health check endpoints for the Player Experience API.

This module provides health check endpoints for monitoring the authentication
system, database connections, and overall service health.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...database.player_profile_repository import PlayerProfileRepository
from ...database.user_auth_schema import UserAuthSchemaManager
from ...database.user_repository import UserRepository
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""

    status: str
    timestamp: str
    version: str
    uptime_seconds: float | None = None


class DetailedHealthStatus(BaseModel):
    """Detailed health status with component checks."""

    status: str
    timestamp: str
    version: str
    uptime_seconds: float | None = None
    components: dict[str, dict[str, Any]]


class DatabaseHealthCheck(BaseModel):
    """Database health check result."""

    status: str
    response_time_ms: float | None = None
    error: str | None = None
    details: dict[str, Any] | None = None


# Global variables for tracking service start time
_service_start_time = datetime.now(timezone.utc)


def get_uptime_seconds() -> float:
    """Calculate service uptime in seconds."""
    return (datetime.now(timezone.utc) - _service_start_time).total_seconds()


async def check_user_database_health() -> DatabaseHealthCheck:
    """Check user authentication database health."""
    try:
        start_time = datetime.now(timezone.utc)

        settings = get_settings()

        # Test user repository connection
        user_repo = UserRepository(
            uri=settings.neo4j_url,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
        )

        user_repo.connect()

        # Test basic query
        exists = user_repo.username_exists("__health_check_user__")

        user_repo.disconnect()

        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds() * 1000

        return DatabaseHealthCheck(
            status="healthy",
            response_time_ms=response_time,
            details={"connection": "successful", "query_test": "passed"},
        )

    except Exception as e:
        logger.error(f"User database health check failed: {e}")
        return DatabaseHealthCheck(
            status="unhealthy", error=str(e), details={"connection": "failed"}
        )


async def check_player_database_health() -> DatabaseHealthCheck:
    """Check player profile database health."""
    try:
        start_time = datetime.now(timezone.utc)

        settings = get_settings()

        # Test player repository connection
        player_repo = PlayerProfileRepository(
            uri=settings.neo4j_url,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
        )

        player_repo.connect()

        # Test basic query
        exists = player_repo.username_exists("__health_check_player__")

        player_repo.disconnect()

        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds() * 1000

        return DatabaseHealthCheck(
            status="healthy",
            response_time_ms=response_time,
            details={"connection": "successful", "query_test": "passed"},
        )

    except Exception as e:
        logger.error(f"Player database health check failed: {e}")
        return DatabaseHealthCheck(
            status="unhealthy", error=str(e), details={"connection": "failed"}
        )


async def check_auth_schema_health() -> DatabaseHealthCheck:
    """Check authentication schema health."""
    try:
        start_time = datetime.now(timezone.utc)

        settings = get_settings()

        # Test schema manager connection
        schema_manager = UserAuthSchemaManager(
            uri=settings.neo4j_url,
            username=settings.neo4j_username,
            password=settings.neo4j_password,
        )

        schema_manager.connect()

        # Verify schema
        verification_results = schema_manager.verify_schema()

        schema_manager.disconnect()

        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds() * 1000

        status = "healthy" if verification_results["schema_valid"] else "degraded"

        return DatabaseHealthCheck(
            status=status,
            response_time_ms=response_time,
            details={
                "schema_valid": verification_results["schema_valid"],
                "constraints_count": len(verification_results["constraints"]),
                "indexes_count": len(verification_results["indexes"]),
            },
        )

    except Exception as e:
        logger.error(f"Auth schema health check failed: {e}")
        return DatabaseHealthCheck(
            status="unhealthy", error=str(e), details={"schema_check": "failed"}
        )


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Basic health check endpoint.

    Returns:
        HealthStatus: Basic service health information
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        uptime_seconds=get_uptime_seconds(),
    )


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check() -> DetailedHealthStatus:
    """
    Detailed health check endpoint with component status.

    Returns:
        DetailedHealthStatus: Detailed service and component health information
    """
    components = {}
    overall_status = "healthy"

    # Check user database
    user_db_health = await check_user_database_health()
    components["user_database"] = user_db_health.dict()
    if user_db_health.status != "healthy":
        overall_status = "degraded" if overall_status == "healthy" else "unhealthy"

    # Check player database
    player_db_health = await check_player_database_health()
    components["player_database"] = player_db_health.dict()
    if player_db_health.status != "healthy":
        overall_status = "degraded" if overall_status == "healthy" else "unhealthy"

    # Check authentication schema
    auth_schema_health = await check_auth_schema_health()
    components["auth_schema"] = auth_schema_health.dict()
    if auth_schema_health.status not in ["healthy", "degraded"]:
        overall_status = "unhealthy"
    elif auth_schema_health.status == "degraded" and overall_status == "healthy":
        overall_status = "degraded"

    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        uptime_seconds=get_uptime_seconds(),
        components=components,
    )


@router.get("/health/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes/container orchestration.

    Returns:
        Dict: Readiness status

    Raises:
        HTTPException: If service is not ready
    """
    try:
        # Check critical components
        user_db_health = await check_user_database_health()
        auth_schema_health = await check_auth_schema_health()

        if (
            user_db_health.status == "unhealthy"
            or auth_schema_health.status == "unhealthy"
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "not_ready",
                    "reason": "Critical components unhealthy",
                    "user_database": user_db_health.status,
                    "auth_schema": auth_schema_health.status,
                },
            )

        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "user_database": user_db_health.status,
                "auth_schema": auth_schema_health.status,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "reason": f"Readiness check error: {str(e)}",
            },
        )


@router.get("/health/live")
async def liveness_check() -> dict[str, Any]:
    """
    Liveness check endpoint for Kubernetes/container orchestration.

    Returns:
        Dict: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": get_uptime_seconds(),
    }
