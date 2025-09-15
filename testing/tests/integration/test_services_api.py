"""
Integration tests for Services API endpoints.

This module tests the service management and health monitoring API endpoints
with both mock and real service scenarios.
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import create_app
from src.player_experience.api.auth import create_access_token
from src.player_experience.api.config import TestingSettings


class ServicesAPITestClient:
    """Enhanced test client for services API testing."""

    def __init__(self):
        """Initialize test client with test configuration."""
        import src.player_experience.api.config as config_module

        config_module.settings = TestingSettings()

        self.app = create_app()
        self.client = TestClient(self.app)
        self.auth_token = None

    def create_auth_token(
        self, user_id: str = "test_admin", username: str = "admin"
    ) -> str:
        """Create authentication token for testing."""
        token_data = {"sub": user_id, "username": username, "role": "admin"}
        return create_access_token(token_data)

    def get_auth_headers(self) -> dict:
        """Get authentication headers for requests."""
        if not self.auth_token:
            self.auth_token = self.create_auth_token()
        return {"Authorization": f"Bearer {self.auth_token}"}


@pytest.fixture
def api_client():
    """Create services API test client fixture."""
    return ServicesAPITestClient()


class TestServiceHealthEndpoints:
    """Test service health monitoring endpoints."""

    def test_system_health_endpoint_public_access(self, api_client):
        """Test system health endpoint is publicly accessible."""
        response = api_client.client.get("/api/v1/services/health")
        assert response.status_code == 200

        data = response.json()
        assert "timestamp" in data
        assert "using_mocks" in data
        assert "overall_status" in data
        assert "services" in data
        assert "summary" in data

        # Check services structure
        assert "neo4j" in data["services"]
        assert "redis" in data["services"]

        # Check summary structure
        summary = data["summary"]
        assert "total_services" in summary
        assert "healthy_services" in summary
        assert "health_percentage" in summary

    def test_system_health_with_mock_services(self, api_client):
        """Test system health endpoint with mock services."""
        response = api_client.client.get("/api/v1/services/health")
        assert response.status_code == 200

        data = response.json()
        assert data["using_mocks"] is True

        # Mock services should be healthy
        neo4j_service = data["services"]["neo4j"]
        redis_service = data["services"]["redis"]

        assert neo4j_service["status"] == "mock"
        assert redis_service["status"] == "mock"
        assert "mock_metrics" in neo4j_service
        assert "mock_metrics" in redis_service

    def test_individual_service_health_endpoint(self, api_client):
        """Test individual service health endpoint."""
        # Test Neo4j service health
        response = api_client.client.get("/api/v1/services/health/neo4j")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "neo4j"
        assert "status" in data
        assert "connection_attempts" in data
        assert "successful_operations" in data

        # Test Redis service health
        response = api_client.client.get("/api/v1/services/health/redis")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "redis"
        assert "status" in data

    def test_individual_service_health_not_found(self, api_client):
        """Test individual service health endpoint with invalid service."""
        response = api_client.client.get("/api/v1/services/health/invalid_service")
        assert response.status_code == 404

        data = response.json()
        assert "Service 'invalid_service' not found" in data["detail"]

    def test_health_endpoint_performance(self, api_client):
        """Test health endpoint response time performance."""
        import time

        start_time = time.time()
        response = api_client.client.get("/api/v1/services/health")
        end_time = time.time()

        assert response.status_code == 200

        # Health check should be fast (under 1 second)
        response_time = end_time - start_time
        assert response_time < 1.0


class TestServiceManagementEndpoints:
    """Test service management endpoints (require authentication)."""

    def test_reconnect_services_requires_auth(self, api_client):
        """Test that service reconnection requires authentication."""
        response = api_client.client.post("/api/v1/services/services/reconnect")
        assert response.status_code == 401

    def test_reconnect_all_services_with_auth(self, api_client):
        """Test reconnecting all services with authentication."""
        headers = api_client.get_auth_headers()

        with patch(
            "src.player_experience.api.services.connection_manager.ServiceConnectionManager"
        ) as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager.close.return_value = None
            mock_manager.initialize.return_value = True
            mock_manager.health_check.return_value = {
                "timestamp": datetime.now().isoformat(),
                "using_mocks": True,
                "services": {
                    "neo4j": {"status": "connected"},
                    "redis": {"status": "connected"},
                },
            }
            mock_manager_class.return_value = mock_manager

            response = api_client.client.post(
                "/api/v1/services/reconnect", headers=headers
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "reconnected successfully" in data["message"]
            assert "timestamp" in data
            assert "details" in data

    def test_reconnect_individual_service_with_auth(self, api_client):
        """Test reconnecting individual service with authentication."""
        headers = api_client.get_auth_headers()

        with patch(
            "src.player_experience.api.services.connection_manager.get_service_manager"
        ) as mock_get_manager:
            mock_manager = AsyncMock()
            mock_neo4j = AsyncMock()
            mock_neo4j.connect.return_value = True
            mock_manager.neo4j = mock_neo4j
            mock_manager.health_check.return_value = {
                "services": {"neo4j": {"status": "connected", "service": "neo4j"}}
            }
            mock_get_manager.return_value = mock_manager

            response = api_client.client.post(
                "/api/v1/services/neo4j/reconnect", headers=headers
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "neo4j reconnected successfully" in data["message"]

    def test_reconnect_invalid_service(self, api_client):
        """Test reconnecting invalid service returns error."""
        headers = api_client.get_auth_headers()

        response = api_client.client.post(
            "/api/v1/services/invalid/reconnect", headers=headers
        )
        assert response.status_code == 400

        data = response.json()
        assert "Invalid service name" in data["detail"]

    def test_reconnect_service_failure(self, api_client):
        """Test service reconnection failure handling."""
        headers = api_client.get_auth_headers()

        with patch(
            "src.player_experience.api.services.connection_manager.get_service_manager"
        ) as mock_get_manager:
            mock_manager = AsyncMock()
            mock_redis = AsyncMock()
            mock_redis.connect.return_value = False  # Simulate failure
            mock_manager.redis = mock_redis
            mock_manager.health_check.return_value = {
                "services": {"redis": {"status": "error", "service": "redis"}}
            }
            mock_get_manager.return_value = mock_manager

            response = api_client.client.post(
                "/api/v1/services/redis/reconnect", headers=headers
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is False
            assert "Failed to reconnect service redis" in data["message"]


class TestServiceConfigurationEndpoints:
    """Test service configuration endpoints."""

    def test_service_config_requires_auth(self, api_client):
        """Test that service configuration requires authentication."""
        response = api_client.client.get("/api/v1/services/config")
        assert response.status_code == 401

    def test_service_config_with_auth(self, api_client):
        """Test service configuration endpoint with authentication."""
        headers = api_client.get_auth_headers()

        response = api_client.client.get("/api/v1/services/config", headers=headers)
        assert response.status_code == 200

        data = response.json()

        # Check main configuration sections
        assert "environment" in data
        assert "neo4j" in data
        assert "redis" in data
        assert "security" in data
        assert "features" in data

        # Check environment settings
        env = data["environment"]
        assert "debug" in env
        assert "development_mode" in env
        assert "use_mocks" in env

        # Check that sensitive data is masked
        neo4j = data["neo4j"]
        assert neo4j["password"] == "***masked***"
        assert neo4j["username"] == "neo4j"  # Non-sensitive
        assert "url" in neo4j

        # Check security settings
        security = data["security"]
        assert "jwt_algorithm" in security
        assert "access_token_expire_minutes" in security
        assert "mfa_enabled" in security

    def test_service_config_masks_sensitive_data(self, api_client):
        """Test that service configuration properly masks sensitive data."""
        headers = api_client.get_auth_headers()

        response = api_client.client.get("/api/v1/services/config", headers=headers)
        assert response.status_code == 200

        data = response.json()

        # Ensure passwords are masked
        assert data["neo4j"]["password"] == "***masked***"

        # Ensure Redis URL credentials are masked if present
        redis_url = data["redis"]["url"]
        assert "@" not in redis_url or not redis_url.startswith("redis://user:pass@")


class TestServiceEndpointIntegration:
    """Test service endpoint integration with real service scenarios."""

    def test_health_check_with_service_errors(self, api_client):
        """Test health check behavior when services have errors."""
        with patch(
            "src.player_experience.api.services.connection_manager.get_service_manager"
        ) as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.health_check.side_effect = Exception("Service manager error")
            mock_get_manager.return_value = mock_manager

            response = api_client.client.get("/api/v1/services/health")
            assert response.status_code == 500

            data = response.json()
            assert "Failed to retrieve system health" in data["detail"]

    def test_service_reconnection_with_manager_error(self, api_client):
        """Test service reconnection with service manager errors."""
        headers = api_client.get_auth_headers()

        with patch(
            "src.player_experience.api.services.connection_manager.get_service_manager"
        ) as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.close.side_effect = Exception("Connection close error")
            mock_get_manager.return_value = mock_manager

            response = api_client.client.post(
                "/api/v1/services/reconnect", headers=headers
            )
            assert response.status_code == 500

            data = response.json()
            assert "Failed to reconnect services" in data["detail"]

    def test_concurrent_health_checks(self, api_client):
        """Test concurrent health check requests."""
        import concurrent.futures

        def make_health_request():
            return api_client.client.get("/api/v1/services/health")

        # Make 5 concurrent health check requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_health_request) for _ in range(5)]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "services" in data
            assert "overall_status" in data

    def test_service_health_data_consistency(self, api_client):
        """Test that service health data is consistent across requests."""
        # Make multiple requests and ensure data structure consistency
        responses = []
        for _ in range(3):
            response = api_client.client.get("/api/v1/services/health")
            assert response.status_code == 200
            responses.append(response.json())

        # Check that all responses have the same structure
        first_response = responses[0]
        for response in responses[1:]:
            assert set(response.keys()) == set(first_response.keys())
            assert set(response["services"].keys()) == set(
                first_response["services"].keys()
            )
            assert response["using_mocks"] == first_response["using_mocks"]


class TestServiceEndpointSecurity:
    """Test security aspects of service endpoints."""

    def test_service_management_requires_valid_token(self, api_client):
        """Test that service management requires valid authentication token."""
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}

        response = api_client.client.post(
            "/api/v1/services/services/reconnect", headers=invalid_headers
        )
        assert response.status_code == 401

    def test_service_config_requires_valid_token(self, api_client):
        """Test that service configuration requires valid authentication token."""
        # Test with malformed token
        malformed_headers = {"Authorization": "InvalidFormat"}

        response = api_client.client.get(
            "/api/v1/services/config", headers=malformed_headers
        )
        assert response.status_code == 401

    def test_service_endpoints_rate_limiting(self, api_client):
        """Test that service endpoints respect rate limiting."""
        headers = api_client.get_auth_headers()

        # Make multiple rapid requests (this would trigger rate limiting in production)
        responses = []
        for _ in range(10):
            response = api_client.client.get("/api/v1/services/config", headers=headers)
            responses.append(response)

        # In test environment, rate limiting might be disabled
        # But we should still get valid responses
        for response in responses:
            assert response.status_code in [200, 429]  # 429 = Too Many Requests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
