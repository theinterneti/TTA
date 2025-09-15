"""
Tests for Clinical Dashboard API Integration

Comprehensive tests for the clinical dashboard API integration service,
controller, and endpoints with validated TTA API connectivity.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.components.clinical_dashboard import (
    APIConfig,
    AuthToken,
    ClinicalDashboardAPIService,
    ClinicalDashboardController,
    TherapeuticMonitoringService,
)


@pytest.fixture
def api_config():
    """Test API configuration."""
    return APIConfig(
        base_url="http://test-api:8080",
        timeout=10,
        max_retries=2,
        retry_delay=0.1,
    )


@pytest.fixture
def mock_monitoring_service():
    """Mock therapeutic monitoring service."""
    service = AsyncMock(spec=TherapeuticMonitoringService)
    service.health_check.return_value = {"status": "healthy"}
    service.get_real_time_metrics.return_value = {
        "engagement": 0.85,
        "progress": 0.72,
        "safety": 0.95,
        "therapeutic_value": 0.78,
    }
    service.utc_now.return_value = datetime.now(timezone.utc)
    return service


@pytest.fixture
def auth_token():
    """Test authentication token."""
    return AuthToken(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_type="bearer",
        expires_in=3600,
        user_id="test_user",
    )


class TestClinicalDashboardAPIService:
    """Test cases for ClinicalDashboardAPIService."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_monitoring_service, api_config):
        """Test API service initialization."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        assert service.monitoring_service == mock_monitoring_service
        assert service.api_config == api_config
        assert service.session is None
        assert service.auth_token is None
        assert len(service.authenticated_users) == 0

    @pytest.mark.asyncio
    async def test_api_connectivity_success(self, mock_monitoring_service, api_config):
        """Test successful API connectivity check."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Mock successful HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"status": "healthy"}

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test connectivity
        result = await service._test_api_connectivity()

        assert result is True
        mock_session.get.assert_called_once_with(f"{api_config.base_url}/api/v1/health")

    @pytest.mark.asyncio
    async def test_api_connectivity_failure(self, mock_monitoring_service, api_config):
        """Test failed API connectivity check."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Mock failed HTTP response
        mock_response = AsyncMock()
        mock_response.status = 500

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test connectivity
        result = await service._test_api_connectivity()

        assert result is False

    @pytest.mark.asyncio
    async def test_user_authentication_success(
        self, mock_monitoring_service, api_config, auth_token
    ):
        """Test successful user authentication."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Mock successful authentication response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "access_token": auth_token.access_token,
            "refresh_token": auth_token.refresh_token,
            "token_type": auth_token.token_type,
            "expires_in": auth_token.expires_in,
        }

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test authentication
        result = await service.authenticate_user("test_user", "test_password")

        assert result is not None
        assert result.access_token == auth_token.access_token
        assert result.user_id == "test_user"
        assert "test_user" in service.authenticated_users
        assert service.service_metrics["authentication_successes"] == 1

    @pytest.mark.asyncio
    async def test_user_authentication_failure(self, mock_monitoring_service, api_config):
        """Test failed user authentication."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Mock failed authentication response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json.return_value = {"error": "Invalid credentials"}

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test authentication
        result = await service.authenticate_user("test_user", "wrong_password")

        assert result is None
        assert "test_user" not in service.authenticated_users
        assert service.service_metrics["authentication_attempts"] == 1
        assert service.service_metrics["authentication_successes"] == 0

    @pytest.mark.asyncio
    async def test_get_user_sessions(
        self, mock_monitoring_service, api_config, auth_token
    ):
        """Test getting user sessions."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Set up authenticated user
        service.authenticated_users["test_user"] = auth_token

        # Mock sessions response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "sessions": [
                {"session_id": "session_1", "status": "active"},
                {"session_id": "session_2", "status": "completed"},
            ]
        }

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test getting sessions
        sessions = await service.get_user_sessions("test_user")

        assert len(sessions) == 2
        assert sessions[0]["session_id"] == "session_1"
        assert sessions[1]["session_id"] == "session_2"

    @pytest.mark.asyncio
    async def test_collect_session_metrics(
        self, mock_monitoring_service, api_config, auth_token
    ):
        """Test collecting session metrics."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Set up authenticated user
        service.authenticated_users["test_user"] = auth_token

        # Mock session data response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "session_id": "test_session",
            "engagement_score": 0.85,
            "progress_score": 0.72,
            "safety_score": 0.95,
            "therapeutic_value": 0.78,
        }

        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        service.session = mock_session

        # Test collecting metrics
        result = await service.collect_session_metrics("test_user", "test_session")

        assert result is True
        assert service.service_metrics["data_points_collected"] == 1

        # Verify monitoring service was called
        mock_monitoring_service.collect_metric.assert_called()

    @pytest.mark.asyncio
    async def test_health_check(self, mock_monitoring_service, api_config):
        """Test API service health check."""
        service = ClinicalDashboardAPIService(
            monitoring_service=mock_monitoring_service,
            api_config=api_config,
        )

        # Mock session
        mock_session = AsyncMock()
        mock_session.closed = False
        service.session = mock_session

        # Test health check
        health = await service.health_check()

        assert health["status"] == "healthy"
        assert health["service"] == "clinical_dashboard_api"
        assert "metrics" in health
        assert "session_active" in health


class TestClinicalDashboardController:
    """Test cases for ClinicalDashboardController."""

    @pytest.fixture
    def mock_api_service(self):
        """Mock API service."""
        service = AsyncMock(spec=ClinicalDashboardAPIService)
        service.health_check.return_value = {"status": "healthy"}
        service.get_dashboard_data.return_value = {
            "user_id": "test_user",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return service

    @pytest.mark.asyncio
    async def test_controller_initialization(self, api_config):
        """Test controller initialization."""
        controller = ClinicalDashboardController(api_config=api_config)

        assert controller.monitoring_service is not None
        assert controller.api_service is not None
        assert controller.initialized is False
        assert len(controller.background_tasks) == 0

    @pytest.mark.asyncio
    async def test_get_dashboard_data_success(self, api_config, mock_api_service):
        """Test successful dashboard data retrieval."""
        controller = ClinicalDashboardController(api_config=api_config)
        controller.api_service = mock_api_service
        controller.initialized = True

        # Mock monitoring service
        controller.monitoring_service = AsyncMock()
        controller.monitoring_service.get_real_time_metrics.return_value = {
            "engagement": 0.85
        }
        controller.monitoring_service.generate_analytics_report.return_value = None
        controller.monitoring_service.get_outcome_progress.return_value = []

        from src.components.clinical_dashboard.dashboard_controller import (
            DashboardRequest,
        )

        request = DashboardRequest(
            user_id="test_user",
            timeframe="weekly",
            include_real_time=True,
            include_analytics=True,
            include_outcomes=True,
        )

        # Test getting dashboard data
        result = await controller.get_dashboard_data(request)

        assert result["user_id"] == "test_user"
        assert "timestamp" in result
        assert "real_time_metrics" in result
        assert controller.controller_metrics["dashboard_requests"] == 1

    @pytest.mark.asyncio
    async def test_collect_metric_success(self, api_config):
        """Test successful metric collection."""
        controller = ClinicalDashboardController(api_config=api_config)
        controller.initialized = True

        # Mock monitoring service
        controller.monitoring_service = AsyncMock()
        controller.monitoring_service.collect_metric.return_value = True

        from src.components.clinical_dashboard.dashboard_controller import (
            MetricCollectionRequest,
        )

        request = MetricCollectionRequest(
            user_id="test_user",
            session_id="test_session",
            metric_type="engagement",
            value=0.85,
            context={"source": "test"},
        )

        # Test collecting metric
        result = await controller.collect_metric(request)

        assert result["status"] == "success"
        assert result["user_id"] == "test_user"
        assert result["value"] == 0.85
        assert controller.controller_metrics["metric_collections"] == 1

    @pytest.mark.asyncio
    async def test_service_status(self, api_config):
        """Test service status retrieval."""
        controller = ClinicalDashboardController(api_config=api_config)
        controller.initialized = True

        # Mock services
        controller.monitoring_service = AsyncMock()
        controller.monitoring_service.health_check.return_value = {"status": "healthy"}

        controller.api_service = AsyncMock()
        controller.api_service.health_check.return_value = {"status": "healthy"}

        # Test service status
        status = await controller.get_service_status()

        assert status["status"] == "healthy"
        assert "controller" in status
        assert "monitoring_service" in status
        assert "api_service" in status
        assert status["controller"]["initialized"] is True


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    # This test simulates the complete workflow from API authentication
    # through data collection to dashboard display

    api_config = APIConfig(base_url="http://test-api:8080")
    controller = ClinicalDashboardController(api_config=api_config)

    # Mock all dependencies
    controller.monitoring_service = AsyncMock()
    controller.api_service = AsyncMock()
    controller.initialized = True

    # Mock authentication
    auth_token = AuthToken(
        access_token="test_token",
        refresh_token="refresh_token",
        user_id="test_user",
    )
    controller.api_service.authenticate_user.return_value = auth_token

    # Mock data collection
    controller.api_service.get_user_sessions.return_value = [
        {"session_id": "session_1", "status": "active"}
    ]
    controller.api_service.collect_session_metrics.return_value = True

    # Mock monitoring service responses
    controller.monitoring_service.get_real_time_metrics.return_value = {
        "engagement": 0.85,
        "progress": 0.72,
    }
    controller.monitoring_service.generate_analytics_report.return_value = None
    controller.monitoring_service.get_outcome_progress.return_value = []

    # Mock API service dashboard data
    controller.api_service.get_dashboard_data.return_value = {
        "user_id": "test_user",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recent_sessions": [{"session_id": "session_1"}],
    }

    # Test complete workflow
    from src.components.clinical_dashboard.dashboard_controller import DashboardRequest

    dashboard_request = DashboardRequest(
        user_id="test_user",
        timeframe="weekly",
        include_real_time=True,
        include_analytics=True,
        include_outcomes=True,
    )

    # Get dashboard data
    result = await controller.get_dashboard_data(dashboard_request)

    # Verify workflow completion
    assert result["user_id"] == "test_user"
    assert "real_time_metrics" in result
    assert "api_integration" in result
    assert "service_status" in result

    # Verify service calls
    controller.monitoring_service.get_real_time_metrics.assert_called_once()
    controller.api_service.get_dashboard_data.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
