"""
Clinical Dashboard API Integration Service

Integrates the TherapeuticMonitoringService with the validated TTA API endpoints
to provide real-time clinical data collection and dashboard functionality.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import aiohttp

from .therapeutic_monitoring_service import (
    AnalyticsTimeframe,
    MetricType,
    TherapeuticMonitoringService,
)

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API configuration for clinical dashboard integration."""

    base_url: str = "http://0.0.0.0:8080"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class AuthToken:
    """Authentication token data."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str = ""


class ClinicalDashboardAPIService:
    """
    API Integration Service for Clinical Dashboard

    Connects TherapeuticMonitoringService with validated TTA API endpoints
    to provide real-time clinical data collection and dashboard functionality.
    """

    def __init__(
        self,
        monitoring_service: TherapeuticMonitoringService,
        api_config: APIConfig | None = None,
    ):
        """Initialize the clinical dashboard API service."""
        self.monitoring_service = monitoring_service
        self.api_config = api_config or APIConfig()

        # HTTP session for API calls
        self.session: aiohttp.ClientSession | None = None

        # Authentication state
        self.auth_token: AuthToken | None = None
        self.authenticated_users: dict[str, AuthToken] = {}

        # Service metrics
        self.service_metrics = {
            "api_calls_made": 0,
            "api_calls_successful": 0,
            "api_calls_failed": 0,
            "data_points_collected": 0,
            "dashboard_requests_served": 0,
            "authentication_attempts": 0,
            "authentication_successes": 0,
        }

        logger.info("ClinicalDashboardAPIService initialized")

    async def initialize(self) -> None:
        """Initialize the API service."""
        try:
            logger.info("Initializing ClinicalDashboardAPIService")

            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.api_config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

            # Test API connectivity
            await self._test_api_connectivity()

            logger.info("ClinicalDashboardAPIService initialization complete")

        except Exception as e:
            logger.error(f"Error initializing ClinicalDashboardAPIService: {e}")
            raise

    async def _test_api_connectivity(self) -> bool:
        """Test connectivity to the TTA API."""
        try:
            url = f"{self.api_config.base_url}/api/v1/health"

            async with self.session.get(url) as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"API connectivity confirmed: {health_data.get('status')}")
                    return True
                else:
                    logger.error(f"API health check failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"API connectivity test failed: {e}")
            return False

    async def authenticate_user(self, username: str, password: str) -> AuthToken | None:
        """Authenticate user with the TTA API."""
        try:
            self.service_metrics["authentication_attempts"] += 1

            url = f"{self.api_config.base_url}/api/v1/auth/login"
            payload = {
                "username": username,
                "password": password
            }

            async with self.session.post(url, json=payload) as response:
                self.service_metrics["api_calls_made"] += 1

                if response.status == 200:
                    auth_data = await response.json()

                    token = AuthToken(
                        access_token=auth_data["access_token"],
                        refresh_token=auth_data["refresh_token"],
                        token_type=auth_data.get("token_type", "bearer"),
                        expires_in=auth_data.get("expires_in", 3600),
                        user_id=username  # Store username as user_id for now
                    )

                    # Store token for user
                    self.authenticated_users[username] = token
                    self.service_metrics["authentication_successes"] += 1
                    self.service_metrics["api_calls_successful"] += 1

                    logger.info(f"User {username} authenticated successfully")
                    return token

                else:
                    error_data = await response.json()
                    logger.warning(f"Authentication failed for {username}: {error_data}")
                    self.service_metrics["api_calls_failed"] += 1
                    return None

        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            self.service_metrics["api_calls_failed"] += 1
            return None

    async def get_user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """Get user sessions from the API."""
        try:
            if user_id not in self.authenticated_users:
                logger.warning(f"User {user_id} not authenticated")
                return []

            token = self.authenticated_users[user_id]
            headers = {"Authorization": f"{token.token_type} {token.access_token}"}

            url = f"{self.api_config.base_url}/api/v1/sessions"

            async with self.session.get(url, headers=headers) as response:
                self.service_metrics["api_calls_made"] += 1

                if response.status == 200:
                    sessions_data = await response.json()
                    self.service_metrics["api_calls_successful"] += 1
                    return sessions_data.get("sessions", [])
                else:
                    logger.error(f"Failed to get sessions for {user_id}: {response.status}")
                    self.service_metrics["api_calls_failed"] += 1
                    return []

        except Exception as e:
            logger.error(f"Error getting sessions for {user_id}: {e}")
            self.service_metrics["api_calls_failed"] += 1
            return []

    async def collect_session_metrics(self, user_id: str, session_id: str) -> bool:
        """Collect metrics from a user session."""
        try:
            if user_id not in self.authenticated_users:
                logger.warning(f"User {user_id} not authenticated")
                return False

            token = self.authenticated_users[user_id]
            headers = {"Authorization": f"{token.token_type} {token.access_token}"}

            url = f"{self.api_config.base_url}/api/v1/sessions/{session_id}"

            async with self.session.get(url, headers=headers) as response:
                self.service_metrics["api_calls_made"] += 1

                if response.status == 200:
                    session_data = await response.json()

                    # Extract metrics from session data and feed to monitoring service
                    await self._process_session_metrics(user_id, session_id, session_data)

                    self.service_metrics["api_calls_successful"] += 1
                    self.service_metrics["data_points_collected"] += 1
                    return True
                else:
                    logger.error(f"Failed to get session {session_id}: {response.status}")
                    self.service_metrics["api_calls_failed"] += 1
                    return False

        except Exception as e:
            logger.error(f"Error collecting metrics for session {session_id}: {e}")
            self.service_metrics["api_calls_failed"] += 1
            return False

    async def _process_session_metrics(
        self, user_id: str, session_id: str, session_data: dict[str, Any]
    ) -> None:
        """Process session data and extract metrics for monitoring service."""
        try:
            # Extract engagement metrics
            if "engagement_score" in session_data:
                await self.monitoring_service.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=MetricType.ENGAGEMENT,
                    value=float(session_data["engagement_score"]),
                    context={"source": "session_data"}
                )

            # Extract progress metrics
            if "progress_score" in session_data:
                await self.monitoring_service.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=MetricType.PROGRESS,
                    value=float(session_data["progress_score"]),
                    context={"source": "session_data"}
                )

            # Extract safety metrics
            if "safety_score" in session_data:
                await self.monitoring_service.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=MetricType.SAFETY,
                    value=float(session_data["safety_score"]),
                    context={"source": "session_data"}
                )

            # Extract therapeutic value metrics
            if "therapeutic_value" in session_data:
                await self.monitoring_service.collect_metric(
                    user_id=user_id,
                    session_id=session_id,
                    metric_type=MetricType.THERAPEUTIC_VALUE,
                    value=float(session_data["therapeutic_value"]),
                    context={"source": "session_data"}
                )

            logger.debug(f"Processed metrics for session {session_id}")

        except Exception as e:
            logger.error(f"Error processing session metrics: {e}")

    async def get_dashboard_data(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive dashboard data for a user."""
        try:
            self.service_metrics["dashboard_requests_served"] += 1

            # Get real-time metrics from monitoring service
            real_time_metrics = await self.monitoring_service.get_real_time_metrics(user_id)

            # Get analytics report
            analytics_report = await self.monitoring_service.generate_analytics_report(
                user_id, AnalyticsTimeframe.WEEKLY
            )

            # Get outcome progress
            outcome_progress = await self.monitoring_service.get_outcome_progress(user_id)

            # Get user sessions from API
            sessions = await self.get_user_sessions(user_id)

            dashboard_data = {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "real_time_metrics": real_time_metrics,
                "analytics_report": analytics_report.__dict__ if analytics_report else None,
                "outcome_progress": outcome_progress,
                "recent_sessions": sessions[-10:] if sessions else [],  # Last 10 sessions
                "service_status": await self._get_service_status(),
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Error getting dashboard data for {user_id}: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _get_service_status(self) -> dict[str, Any]:
        """Get overall service status."""
        try:
            # Get monitoring service health
            monitoring_health = await self.monitoring_service.health_check()

            # Get API health
            api_healthy = await self._test_api_connectivity()

            return {
                "monitoring_service": monitoring_health,
                "api_connectivity": "healthy" if api_healthy else "unhealthy",
                "authenticated_users": len(self.authenticated_users),
                "service_metrics": self.service_metrics,
            }

        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the API integration service."""
        try:
            return {
                "status": "healthy",
                "service": "clinical_dashboard_api",
                "api_connectivity": await self._test_api_connectivity(),
                "authenticated_users": len(self.authenticated_users),
                "metrics": self.service_metrics,
                "session_active": self.session is not None and not self.session.closed,
            }
        except Exception as e:
            logger.error(f"Error in API integration health check: {e}")
            return {
                "status": "unhealthy",
                "service": "clinical_dashboard_api",
                "error": str(e),
            }

    async def shutdown(self) -> None:
        """Shutdown the API integration service."""
        try:
            logger.info("Shutting down ClinicalDashboardAPIService")

            # Close HTTP session
            if self.session and not self.session.closed:
                await self.session.close()

            # Clear authentication data
            self.authenticated_users.clear()

            logger.info("ClinicalDashboardAPIService shutdown complete")

        except Exception as e:
            logger.error(f"Error during API integration shutdown: {e}")
            raise
