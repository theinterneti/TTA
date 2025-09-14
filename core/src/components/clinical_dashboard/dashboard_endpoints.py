"""
Clinical Dashboard API Endpoints

FastAPI endpoints for the clinical dashboard providing real-time therapeutic
monitoring, analytics, and clinical data visualization.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .dashboard_controller import (
    ClinicalDashboardController,
    DashboardRequest,
    MetricCollectionRequest,
    OutcomeMeasurementRequest,
    get_dashboard_controller,
)
from .therapeutic_monitoring_service import utc_now

logger = logging.getLogger(__name__)

# Create router for clinical dashboard endpoints
router = APIRouter(prefix="/api/v1/clinical", tags=["clinical_dashboard"])


def get_current_user():
    """
    Authentication dependency for clinical dashboard endpoints.

    This is a local implementation to avoid circular imports.
    In production, this would integrate with the main auth system.
    """

    async def _get_current_user():
        # For now, return a mock user to avoid circular import
        # This will be properly integrated with JWT auth in production
        return {"user_id": "clinical_user", "role": "clinician"}

    return _get_current_user


class AuthenticationRequest(BaseModel):
    """Authentication request for clinical dashboard access."""

    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class DashboardResponse(BaseModel):
    """Dashboard data response model."""

    status: str = Field(..., description="Response status")
    data: dict[str, Any] = Field(..., description="Dashboard data")
    timestamp: str = Field(..., description="Response timestamp")


class MetricResponse(BaseModel):
    """Metric collection response model."""

    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    metric_id: str | None = Field(None, description="Metric identifier")


class ServiceStatusResponse(BaseModel):
    """Service status response model."""

    status: str = Field(..., description="Overall service status")
    services: dict[str, Any] = Field(..., description="Individual service statuses")
    timestamp: str = Field(..., description="Status check timestamp")


@router.post("/auth/login", response_model=dict[str, Any])
async def authenticate_user(
    request: AuthenticationRequest,
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
) -> dict[str, Any]:
    """
    Authenticate user for clinical dashboard access.

    Authenticates users against the TTA API and provides access tokens
    for clinical dashboard functionality.
    """
    try:
        logger.info(f"Authentication attempt for user: {request.username}")

        # Authenticate with API service
        auth_token = await controller.api_service.authenticate_user(
            request.username, request.password
        )

        if auth_token:
            return {
                "status": "success",
                "message": "Authentication successful",
                "user_id": request.username,
                "token_type": auth_token.token_type,
                "expires_in": auth_token.expires_in,
                # Note: Don't return actual tokens in response for security
                "authenticated": True,
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        raise HTTPException(
            status_code=500, detail="Authentication service error"
        ) from e


@router.get("/dashboard/{user_id}", response_model=DashboardResponse)
async def get_dashboard_data(
    user_id: str,
    timeframe: str = Query("weekly", description="Analytics timeframe"),
    include_real_time: bool = Query(True, description="Include real-time metrics"),
    include_analytics: bool = Query(True, description="Include analytics report"),
    include_outcomes: bool = Query(True, description="Include outcome measurements"),
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> DashboardResponse:
    """
    Get comprehensive clinical dashboard data for a user.

    Provides real-time metrics, analytics reports, outcome measurements,
    and service status for clinical monitoring and decision-making.
    """
    try:
        logger.info(f"Dashboard data request for user: {user_id}")

        # Create dashboard request
        dashboard_request = DashboardRequest(
            user_id=user_id,
            timeframe=timeframe,
            include_real_time=include_real_time,
            include_analytics=include_analytics,
            include_outcomes=include_outcomes,
        )

        # Get dashboard data
        dashboard_data = await controller.get_dashboard_data(dashboard_request)

        return DashboardResponse(
            status="success",
            data=dashboard_data,
            timestamp=dashboard_data.get("timestamp", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Dashboard service error") from e


@router.post("/metrics/collect", response_model=MetricResponse)
async def collect_metric(
    request: MetricCollectionRequest,
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> MetricResponse:
    """
    Collect a therapeutic metric data point.

    Records therapeutic metrics from various sources for clinical monitoring
    and analytics processing.
    """
    try:
        logger.info(
            f"Metric collection for user {request.user_id}: {request.metric_type}"
        )

        # Collect metric
        result = await controller.collect_metric(request)

        return MetricResponse(
            status=result["status"],
            message=result["message"],
            metric_id=result.get("timestamp"),  # Use timestamp as metric ID
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collecting metric: {e}")
        raise HTTPException(
            status_code=500, detail="Metric collection service error"
        ) from e


@router.post("/outcomes/record", response_model=dict[str, Any])
async def record_outcome_measurement(
    request: OutcomeMeasurementRequest,
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> dict[str, Any]:
    """
    Record a clinical outcome measurement.

    Records evidence-based outcome measurements for clinical assessment
    and treatment effectiveness tracking.
    """
    try:
        logger.info(
            f"Outcome measurement for user {request.user_id}: {request.measure_type}"
        )

        # Record outcome measurement
        result = await controller.record_outcome_measurement(request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording outcome measurement: {e}")
        raise HTTPException(
            status_code=500, detail="Outcome measurement service error"
        ) from e


@router.get("/metrics/real-time/{user_id}", response_model=dict[str, Any])
async def get_real_time_metrics(
    user_id: str,
    metric_types: list[str] | None = Query(
        None, description="Specific metric types to retrieve"
    ),
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> dict[str, Any]:
    """
    Get real-time therapeutic metrics for a user.

    Provides current metric values, trends, and contextual information
    for immediate clinical assessment.
    """
    try:
        logger.info(f"Real-time metrics request for user: {user_id}")

        # Get real-time metrics from monitoring service
        from .therapeutic_monitoring_service import MetricType

        # Parse metric types if provided
        parsed_metric_types = None
        if metric_types:
            try:
                parsed_metric_types = [MetricType(mt.lower()) for mt in metric_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid metric type: {e}"
                ) from e

        # Get metrics
        metrics = await controller.monitoring_service.get_real_time_metrics(
            user_id, parsed_metric_types
        )

        return {
            "status": "success",
            "user_id": user_id,
            "metrics": metrics,
            "timestamp": utc_now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Real-time metrics service error"
        ) from e


@router.get("/analytics/{user_id}", response_model=dict[str, Any])
async def get_analytics_report(
    user_id: str,
    timeframe: str = Query("weekly", description="Analytics timeframe"),
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> dict[str, Any]:
    """
    Get clinical analytics report for a user.

    Provides comprehensive analytics including trends, recommendations,
    risk factors, and protective factors for clinical decision-making.
    """
    try:
        logger.info(f"Analytics report request for user {user_id}: {timeframe}")

        # Parse timeframe
        from .therapeutic_monitoring_service import AnalyticsTimeframe

        try:
            parsed_timeframe = AnalyticsTimeframe(timeframe.lower())
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid timeframe: {timeframe}"
            ) from e

        # Generate analytics report
        report = await controller.monitoring_service.generate_analytics_report(
            user_id, parsed_timeframe
        )

        if report:
            return {
                "status": "success",
                "user_id": user_id,
                "report": report.__dict__,
                "timestamp": report.generated_at.isoformat(),
            }
        else:
            return {
                "status": "no_data",
                "user_id": user_id,
                "message": "No analytics data available for the specified timeframe",
                "timestamp": utc_now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics report: {e}")
        raise HTTPException(status_code=500, detail="Analytics service error") from e


@router.get("/outcomes/{user_id}", response_model=dict[str, Any])
async def get_outcome_progress(
    user_id: str,
    measure_type: str | None = Query(None, description="Specific outcome measure type"),
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
    current_user: dict = Depends(get_current_user()),
) -> dict[str, Any]:
    """
    Get outcome measurement progress for a user.

    Provides outcome measurement history, progress tracking, and
    improvement analysis for clinical assessment.
    """
    try:
        logger.info(f"Outcome progress request for user {user_id}")

        # Parse measure type if provided
        parsed_measure_type = None
        if measure_type:
            from .therapeutic_monitoring_service import OutcomeMeasure

            try:
                parsed_measure_type = OutcomeMeasure(measure_type.lower())
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid measure type: {measure_type}"
                ) from e

        # Get outcome progress
        progress = await controller.monitoring_service.get_outcome_progress(
            user_id, parsed_measure_type
        )

        return {
            "status": "success",
            "user_id": user_id,
            "progress": progress,
            "timestamp": utc_now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting outcome progress: {e}")
        raise HTTPException(
            status_code=500, detail="Outcome progress service error"
        ) from e


@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status(
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
) -> ServiceStatusResponse:
    """
    Get comprehensive clinical dashboard service status.

    Provides health status for all dashboard services including monitoring,
    API integration, and background tasks.
    """
    try:
        logger.info("Service status request")

        # Get service status
        status = await controller.get_service_status()

        return ServiceStatusResponse(
            status=status["status"],
            services=status,
            timestamp=utc_now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return ServiceStatusResponse(
            status="error",
            services={"error": str(e)},
            timestamp=utc_now().isoformat(),
        )


@router.get("/health", response_model=dict[str, Any])
async def health_check(
    controller: ClinicalDashboardController = Depends(get_dashboard_controller),
) -> dict[str, Any]:
    """
    Clinical dashboard health check endpoint.

    Provides basic health status for monitoring and load balancing.
    """
    try:
        status = await controller.get_service_status()

        return {
            "status": "healthy" if status["status"] == "healthy" else "unhealthy",
            "service": "clinical_dashboard",
            "timestamp": utc_now().isoformat(),
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "service": "clinical_dashboard",
            "error": str(e),
            "timestamp": utc_now().isoformat(),
        }
