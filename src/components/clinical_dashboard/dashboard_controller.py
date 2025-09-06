"""
Clinical Dashboard Controller

Main controller for the clinical dashboard that orchestrates therapeutic monitoring,
API integration, and real-time clinical data visualization.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel

from .api_integration_service import APIConfig, ClinicalDashboardAPIService
from .therapeutic_monitoring_service import (
    AnalyticsTimeframe,
    MetricType,
    OutcomeMeasure,
    TherapeuticMonitoringService,
)

logger = logging.getLogger(__name__)


class DashboardRequest(BaseModel):
    """Dashboard data request model."""

    user_id: str
    timeframe: str = "weekly"
    include_real_time: bool = True
    include_analytics: bool = True
    include_outcomes: bool = True


class MetricCollectionRequest(BaseModel):
    """Metric collection request model."""

    user_id: str
    session_id: str
    metric_type: str
    value: float
    context: dict[str, Any] | None = None


class OutcomeMeasurementRequest(BaseModel):
    """Outcome measurement request model."""

    user_id: str
    measure_type: str
    current_score: float
    baseline_score: float | None = None
    target_score: float | None = None
    clinician_notes: str = ""


class ClinicalDashboardController:
    """
    Clinical Dashboard Controller

    Orchestrates therapeutic monitoring, API integration, and clinical data visualization
    for production-ready clinical dashboard functionality.
    """

    def __init__(self, api_config: APIConfig | None = None):
        """Initialize the clinical dashboard controller."""
        # Initialize services
        self.monitoring_service = TherapeuticMonitoringService()
        self.api_service = ClinicalDashboardAPIService(
            monitoring_service=self.monitoring_service, api_config=api_config
        )

        # Service state
        self.initialized = False
        self.background_tasks: list[asyncio.Task] = []

        # Controller metrics
        self.controller_metrics = {
            "dashboard_requests": 0,
            "metric_collections": 0,
            "outcome_measurements": 0,
            "errors": 0,
            "uptime_start": datetime.now(timezone.utc),
        }

        logger.info("ClinicalDashboardController initialized")

    async def initialize(self) -> None:
        """Initialize the clinical dashboard controller."""
        try:
            logger.info("Initializing ClinicalDashboardController")

            # Initialize monitoring service
            await self.monitoring_service.initialize()

            # Initialize API service
            await self.api_service.initialize()

            # Start background data collection
            collection_task = asyncio.create_task(self._background_data_collection())
            self.background_tasks.append(collection_task)

            self.initialized = True
            logger.info("ClinicalDashboardController initialization complete")

        except Exception as e:
            logger.error(f"Error initializing ClinicalDashboardController: {e}")
            raise

    async def get_dashboard_data(self, request: DashboardRequest) -> dict[str, Any]:
        """Get comprehensive dashboard data for a user."""
        try:
            if not self.initialized:
                raise HTTPException(status_code=503, detail="Dashboard not initialized")

            self.controller_metrics["dashboard_requests"] += 1

            # Parse timeframe
            try:
                timeframe = AnalyticsTimeframe(request.timeframe.lower())
            except ValueError:
                timeframe = AnalyticsTimeframe.WEEKLY

            dashboard_data = {
                "user_id": request.user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timeframe": timeframe.value,
            }

            # Get real-time metrics if requested
            if request.include_real_time:
                real_time_metrics = await self.monitoring_service.get_real_time_metrics(
                    request.user_id
                )
                dashboard_data["real_time_metrics"] = real_time_metrics

            # Get analytics report if requested
            if request.include_analytics:
                analytics_report = (
                    await self.monitoring_service.generate_analytics_report(
                        request.user_id, timeframe
                    )
                )
                dashboard_data["analytics_report"] = (
                    analytics_report.__dict__ if analytics_report else None
                )

            # Get outcome progress if requested
            if request.include_outcomes:
                outcome_progress = await self.monitoring_service.get_outcome_progress(
                    request.user_id
                )
                dashboard_data["outcome_progress"] = outcome_progress

            # Get API integration data
            api_data = await self.api_service.get_dashboard_data(request.user_id)
            dashboard_data["api_integration"] = api_data

            # Add service status
            dashboard_data["service_status"] = await self.get_service_status()

            return dashboard_data

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            self.controller_metrics["errors"] += 1
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def collect_metric(self, request: MetricCollectionRequest) -> dict[str, Any]:
        """Collect a therapeutic metric."""
        try:
            if not self.initialized:
                raise HTTPException(status_code=503, detail="Dashboard not initialized")

            self.controller_metrics["metric_collections"] += 1

            # Parse metric type
            try:
                metric_type = MetricType(request.metric_type.lower())
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid metric type: {request.metric_type}",
                ) from e

            # Collect metric
            success = await self.monitoring_service.collect_metric(
                user_id=request.user_id,
                session_id=request.session_id,
                metric_type=metric_type,
                value=request.value,
                context=request.context,
            )

            if success:
                return {
                    "status": "success",
                    "message": "Metric collected successfully",
                    "user_id": request.user_id,
                    "metric_type": metric_type.value,
                    "value": request.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to collect metric")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error collecting metric: {e}")
            self.controller_metrics["errors"] += 1
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def record_outcome_measurement(
        self, request: OutcomeMeasurementRequest
    ) -> dict[str, Any]:
        """Record a clinical outcome measurement."""
        try:
            if not self.initialized:
                raise HTTPException(status_code=503, detail="Dashboard not initialized")

            self.controller_metrics["outcome_measurements"] += 1

            # Parse outcome measure type
            try:
                measure_type = OutcomeMeasure(request.measure_type.lower())
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid outcome measure type: {request.measure_type}",
                ) from e

            # Record outcome measurement
            outcome_id = await self.monitoring_service.record_outcome_measure(
                user_id=request.user_id,
                measure_type=measure_type,
                current_score=request.current_score,
                baseline_score=request.baseline_score,
                target_score=request.target_score,
                clinician_notes=request.clinician_notes,
            )

            if outcome_id:
                return {
                    "status": "success",
                    "message": "Outcome measurement recorded successfully",
                    "outcome_id": outcome_id,
                    "user_id": request.user_id,
                    "measure_type": measure_type.value,
                    "current_score": request.current_score,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to record outcome measurement"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error recording outcome measurement: {e}")
            self.controller_metrics["errors"] += 1
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def get_service_status(self) -> dict[str, Any]:
        """Get comprehensive service status."""
        try:
            # Get monitoring service health
            monitoring_health = await self.monitoring_service.health_check()

            # Get API service health
            api_health = await self.api_service.health_check()

            # Calculate uptime
            uptime = (
                datetime.now(timezone.utc) - self.controller_metrics["uptime_start"]
            )

            return {
                "status": "healthy" if self.initialized else "initializing",
                "controller": {
                    "initialized": self.initialized,
                    "uptime_seconds": uptime.total_seconds(),
                    "background_tasks_running": len(
                        [task for task in self.background_tasks if not task.done()]
                    ),
                    "metrics": self.controller_metrics,
                },
                "monitoring_service": monitoring_health,
                "api_service": api_health,
            }

        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _background_data_collection(self) -> None:
        """Background task for continuous data collection."""
        try:
            logger.info("Starting background data collection")

            while True:
                try:
                    # Get authenticated users from API service
                    authenticated_users = list(
                        self.api_service.authenticated_users.keys()
                    )

                    # Collect metrics for each authenticated user
                    for user_id in authenticated_users:
                        try:
                            # Get user sessions
                            sessions = await self.api_service.get_user_sessions(user_id)

                            # Collect metrics from recent sessions
                            for session in sessions[-5:]:  # Last 5 sessions
                                session_id = session.get("session_id", "")
                                if session_id:
                                    await self.api_service.collect_session_metrics(
                                        user_id, session_id
                                    )

                        except Exception as e:
                            logger.error(
                                f"Error collecting data for user {user_id}: {e}"
                            )

                    # Wait before next collection cycle (5 minutes)
                    await asyncio.sleep(300)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in background data collection: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying

        except asyncio.CancelledError:
            logger.info("Background data collection cancelled")

    async def shutdown(self) -> None:
        """Shutdown the clinical dashboard controller."""
        try:
            logger.info("Shutting down ClinicalDashboardController")

            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            # Shutdown services
            await self.api_service.shutdown()
            await self.monitoring_service.shutdown()

            self.initialized = False
            logger.info("ClinicalDashboardController shutdown complete")

        except Exception as e:
            logger.error(f"Error during dashboard controller shutdown: {e}")
            raise


# Global controller instance
dashboard_controller: ClinicalDashboardController | None = None


async def get_dashboard_controller() -> ClinicalDashboardController:
    """Dependency to get the dashboard controller instance."""
    global dashboard_controller

    if dashboard_controller is None:
        dashboard_controller = ClinicalDashboardController()
        await dashboard_controller.initialize()

    return dashboard_controller
