"""
Service Management and Health Monitoring API endpoints.

This module provides endpoints for monitoring service health, connection status,
and performing service management operations.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..auth import TokenData, get_current_active_player
from ..config import APISettings, get_settings
from ..services.connection_manager import ServiceConnectionManager, get_service_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceHealthResponse(BaseModel):
    """Service health response model."""

    service: str
    status: str
    last_check: str | None = None
    last_error: str | None = None
    connection_attempts: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    success_rate: float = 0.0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    mock_metrics: dict[str, Any] | None = None


class SystemHealthResponse(BaseModel):
    """System health response model."""

    timestamp: str
    using_mocks: bool
    overall_status: str
    services: dict[str, ServiceHealthResponse]
    summary: dict[str, Any]


class ServiceOperationResponse(BaseModel):
    """Service operation response model."""

    success: bool
    message: str
    timestamp: str
    details: dict[str, Any] | None = None


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    service_manager: ServiceConnectionManager = Depends(get_service_manager),
) -> SystemHealthResponse:
    """
    Get comprehensive system health information.

    Returns detailed health status for all services including connection status,
    performance metrics, and error information.
    """
    try:
        health_data = await service_manager.health_check()

        # Process service health data
        services = {}
        all_healthy = True
        total_services = 0
        healthy_services = 0

        for service_name, service_data in health_data["services"].items():
            service_health = ServiceHealthResponse(
                service=service_data.get("service", service_name),
                status=service_data.get("status", "unknown"),
                last_check=service_data.get("last_check"),
                last_error=service_data.get("last_error"),
                connection_attempts=service_data.get("connection_attempts", 0),
                successful_operations=service_data.get("successful_operations", 0),
                failed_operations=service_data.get("failed_operations", 0),
                success_rate=service_data.get("success_rate", 0.0),
                average_response_time_ms=service_data.get(
                    "average_response_time_ms", 0.0
                ),
                uptime_seconds=service_data.get("uptime_seconds", 0.0),
                mock_metrics=service_data.get("mock_metrics"),
            )

            services[service_name] = service_health
            total_services += 1

            if service_health.status in ["connected", "mock"]:
                healthy_services += 1
            else:
                all_healthy = False

        # Determine overall status
        if all_healthy:
            overall_status = "healthy"
        elif healthy_services > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # Create summary
        summary = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": total_services - healthy_services,
            "health_percentage": (
                (healthy_services / total_services * 100) if total_services > 0 else 0
            ),
        }

        return SystemHealthResponse(
            timestamp=health_data["timestamp"],
            using_mocks=health_data["using_mocks"],
            overall_status=overall_status,
            services=services,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system health: {str(e)}",
        ) from None


@router.get("/health/{service_name}", response_model=ServiceHealthResponse)
async def get_service_health(
    service_name: str,
    service_manager: ServiceConnectionManager = Depends(get_service_manager),
) -> ServiceHealthResponse:
    """
    Get health information for a specific service.

    Args:
        service_name: Name of the service (neo4j, redis)

    Returns:
        ServiceHealthResponse: Detailed health information for the service
    """
    try:
        health_data = await service_manager.health_check()

        if service_name not in health_data["services"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found",
            )

        service_data = health_data["services"][service_name]

        return ServiceHealthResponse(
            service=service_data.get("service", service_name),
            status=service_data.get("status", "unknown"),
            last_check=service_data.get("last_check"),
            last_error=service_data.get("last_error"),
            connection_attempts=service_data.get("connection_attempts", 0),
            successful_operations=service_data.get("successful_operations", 0),
            failed_operations=service_data.get("failed_operations", 0),
            success_rate=service_data.get("success_rate", 0.0),
            average_response_time_ms=service_data.get("average_response_time_ms", 0.0),
            uptime_seconds=service_data.get("uptime_seconds", 0.0),
            mock_metrics=service_data.get("mock_metrics"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service health for {service_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service health: {str(e)}",
        ) from None


@router.post("/reconnect", response_model=ServiceOperationResponse)
async def reconnect_services(
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: ServiceConnectionManager = Depends(get_service_manager),
) -> ServiceOperationResponse:
    """
    Reconnect all services.

    This endpoint requires authentication and will attempt to reconnect
    all services that are currently disconnected or in error state.
    """
    try:
        logger.info(f"Player {current_player.username} requested service reconnection")

        # Close existing connections
        await service_manager.close()

        # Reinitialize connections
        success = await service_manager.initialize()

        if success:
            message = "All services reconnected successfully"
            logger.info(message)
        else:
            message = (
                "Some services failed to reconnect - check service health for details"
            )
            logger.warning(message)

        return ServiceOperationResponse(
            success=success,
            message=message,
            timestamp=datetime.now().isoformat(),
            details=await service_manager.health_check(),
        )

    except Exception as e:
        error_msg = f"Failed to reconnect services: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg
        ) from None


@router.post("/{service_name}/reconnect", response_model=ServiceOperationResponse)
async def reconnect_service(
    service_name: str,
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: ServiceConnectionManager = Depends(get_service_manager),
) -> ServiceOperationResponse:
    """
    Reconnect a specific service.

    Args:
        service_name: Name of the service to reconnect (neo4j, redis)

    This endpoint requires authentication and will attempt to reconnect
    the specified service.
    """
    try:
        logger.info(
            f"Player {current_player.username} requested reconnection for service {service_name}"
        )

        if service_name not in ["neo4j", "redis"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service name: {service_name}. Must be 'neo4j' or 'redis'",
            )

        # Get the specific service manager
        if service_name == "neo4j":
            service = service_manager.neo4j
        else:  # redis
            service = service_manager.redis

        # Attempt reconnection
        if hasattr(service, "connect"):
            success = await service.connect()
        else:
            # Mock service - always successful
            success = True

        if success:
            message = f"Service {service_name} reconnected successfully"
            logger.info(message)
        else:
            message = f"Failed to reconnect service {service_name}"
            logger.warning(message)

        # Get updated health info
        health_data = await service_manager.health_check()
        service_health = health_data["services"].get(service_name, {})

        return ServiceOperationResponse(
            success=success,
            message=message,
            timestamp=datetime.now().isoformat(),
            details=service_health,
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to reconnect service {service_name}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg
        ) from None


@router.get("/config", response_model=dict[str, Any])
async def get_service_configuration(
    current_player: TokenData = Depends(get_current_active_player),
    settings: APISettings = Depends(get_settings),
) -> dict[str, Any]:
    """
    Get current service configuration.

    This endpoint requires authentication and returns the current
    configuration for all services (with sensitive data masked).
    """
    try:
        config = {
            "environment": {
                "debug": settings.debug,
                "development_mode": settings.development_mode,
                "use_mocks": settings.use_mocks,
                "use_neo4j": settings.use_neo4j,
            },
            "neo4j": {
                "url": settings.neo4j_url,
                "username": settings.neo4j_username,
                "password": "***masked***" if settings.neo4j_password else None,
            },
            "redis": {
                "url": (
                    settings.redis_url.split("@")[-1]
                    if "@" in settings.redis_url
                    else settings.redis_url
                )  # Mask credentials
            },
            "security": {
                "jwt_algorithm": settings.jwt_algorithm,
                "access_token_expire_minutes": settings.access_token_expire_minutes,
                "max_login_attempts": settings.max_login_attempts,
                "mfa_enabled": settings.mfa_enabled,
            },
            "features": {
                "crisis_detection_enabled": settings.crisis_detection_enabled,
                "enable_docs": settings.enable_docs,
                "enable_redoc": settings.enable_redoc,
            },
        }

        return config

    except Exception as e:
        logger.error(f"Failed to get service configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service configuration: {str(e)}",
        ) from None
