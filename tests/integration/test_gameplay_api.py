"""
API integration tests for the Gameplay Loop endpoints.

These tests validate the REST API endpoints for gameplay functionality,
ensuring proper authentication, request/response handling, and error cases.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from src.player_experience.api.app import create_app


class TestGameplayAPI:
    """Test suite for Gameplay API endpoints."""
    
    @pytest.fixture
    def mock_gameplay_service(self):
        """Mock GameplayService for API testing."""
        service = Mock()
        
        # Mock successful responses
        service.create_authenticated_session = AsyncMock(return_value={
            "success": True,
            "session_id": "test-session-123",
            "user_id": "test-user",
            "session_status": {"status": "active"},
            "created_at": "2024-01-01T00:00:00Z"
        })
        
        service.process_validated_choice = AsyncMock(return_value={
            "success": True,
            "session_id": "test-session-123",
            "choice_result": {
                "next_scene": {"description": "Test scene"},
                "available_choices": [{"id": "choice-1", "text": "Test choice"}],
                "consequences": {"therapeutic_insight": "Test insight"}
            },
            "processed_at": "2024-01-01T00:00:00Z"
        })
        
        service.get_session_with_auth = AsyncMock(return_value={
            "success": True,
            "session_status": {
                "session_id": "test-session-123",
                "user_id": "test-user",
                "status": "active"
            },
            "retrieved_at": "2024-01-01T00:00:00Z"
        })
        
        service.end_session_with_auth = AsyncMock(return_value={
            "success": True,
            "session_id": "test-session-123",
            "ended_at": "2024-01-01T00:00:00Z"
        })
        
        service.get_user_sessions = AsyncMock(return_value={
            "success": True,
            "user_id": "test-user",
            "session_metrics": {"active_sessions": 1},
            "retrieved_at": "2024-01-01T00:00:00Z"
        })
        
        service.get_integration_status.return_value = {
            "gameplay_component": {"available": True, "status": "healthy"},
            "agent_orchestration": {"available": True},
            "safety_service": {"available": True}
        }
        
        return service
    
    @pytest.fixture
    def client(self, mock_gameplay_service):
        """Create test client with mocked dependencies."""
        app = create_app()

        # Mock the gameplay service dependency
        def mock_get_gameplay_service():
            return mock_gameplay_service

        # Override the dependency
        from src.player_experience.api.routers.gameplay import get_gameplay_service
        app.dependency_overrides[get_gameplay_service] = mock_get_gameplay_service

        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication for tests that need it."""
        with patch('src.player_experience.api.middleware.verify_token') as mock_verify:
            # Mock verify_token to return valid token data
            mock_verify.return_value = {"user_id": "test-user", "username": "testuser"}
            yield mock_verify
    
    def test_create_session_success(self, client, mock_gameplay_service, mock_auth):
        """Test successful session creation."""
        response = client.post(
            "/api/v1/gameplay/sessions",
            json={"therapeutic_context": {"goals": ["anxiety_management"]}},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-123"
        assert data["user_id"] == "test-user"
    
    def test_create_session_auth_failure(self, client, mock_gameplay_service):
        """Test session creation with authentication failure."""
        # Mock authentication failure at middleware level
        from src.player_experience.api.auth import AuthenticationError

        with patch('src.player_experience.api.middleware.verify_token') as mock_verify:
            mock_verify.side_effect = AuthenticationError("Invalid token")

            response = client.post(
                "/api/v1/gameplay/sessions",
                json={},
                headers={"Authorization": "Bearer invalid-token"}
            )

            assert response.status_code == 401
            data = response.json()
            assert "error" in data
            assert "Invalid token" in data["message"]
    
    def test_process_choice_success(self, client, mock_gameplay_service, mock_auth):
        """Test successful choice processing."""
        response = client.post(
            "/api/v1/gameplay/sessions/test-session-123/choices",
            json={"choice_id": "choice-1"},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-123"
        assert "choice_result" in data
    
    def test_process_choice_session_not_found(self, client, mock_gameplay_service, mock_auth):
        """Test choice processing with session not found."""
        # Mock session not found - must use AsyncMock for async methods
        mock_gameplay_service.process_validated_choice = AsyncMock(return_value={
            "success": False,
            "error": "Session not found",
            "code": "SESSION_NOT_FOUND"
        })

        response = client.post(
            "/api/v1/gameplay/sessions/nonexistent-session/choices",
            json={"choice_id": "choice-1"},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 404
        # Global exception handler transforms HTTPException to {"error": "...", "message": "...", "status_code": ...}
        assert "Session not found" in response.json()["message"]
    
    def test_get_session_status_success(self, client, mock_gameplay_service, mock_auth):
        """Test successful session status retrieval."""
        response = client.get(
            "/api/v1/gameplay/sessions/test-session-123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session_status" in data
    
    def test_get_session_status_access_denied(self, client, mock_gameplay_service, mock_auth):
        """Test session status retrieval with access denied."""
        # Mock access denied - must use AsyncMock for async methods
        mock_gameplay_service.get_session_with_auth = AsyncMock(return_value={
            "success": False,
            "error": "Session access denied",
            "code": "ACCESS_DENIED"
        })

        response = client.get(
            "/api/v1/gameplay/sessions/test-session-123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 403
        # Global exception handler transforms HTTPException to {"error": "...", "message": "...", "status_code": ...}
        assert "Session access denied" in response.json()["message"]
    
    def test_end_session_success(self, client, mock_gameplay_service, mock_auth):
        """Test successful session termination."""
        response = client.delete(
            "/api/v1/gameplay/sessions/test-session-123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-123"
    
    def test_get_user_sessions_success(self, client, mock_gameplay_service, mock_auth):
        """Test successful user sessions retrieval."""
        response = client.get(
            "/api/v1/gameplay/sessions",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "test-user"
        assert "session_metrics" in data
    
    def test_health_check_success(self, client, mock_gameplay_service):
        """Test gameplay health check endpoint."""
        response = client.get("/api/v1/gameplay/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "integration_status" in data
    
    def test_missing_authorization_header(self, client):
        """Test API calls without authorization header."""
        response = client.post(
            "/api/v1/gameplay/sessions",
            json={}
        )

        # Should return 401 Unauthorized due to missing authorization
        assert response.status_code == 401
    
    def test_invalid_request_body(self, client, mock_auth):
        """Test API calls with invalid request body."""
        response = client.post(
            "/api/v1/gameplay/sessions/test-session-123/choices",
            json={"invalid_field": "value"},  # Missing required choice_id
            headers={"Authorization": "Bearer valid-token"}
        )

        # Should return 422 Unprocessable Entity due to validation error
        assert response.status_code == 422
    
    def test_internal_server_error_handling(self, client, mock_gameplay_service, mock_auth):
        """Test handling of internal server errors."""
        # Mock service to raise an exception - must use AsyncMock for async methods
        mock_gameplay_service.create_authenticated_session = AsyncMock(side_effect=Exception("Internal error"))

        response = client.post(
            "/api/v1/gameplay/sessions",
            json={},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 500
        # Global exception handler transforms HTTPException to {"error": "...", "message": "...", "status_code": ...}
        assert "Internal server error" in response.json()["message"]


class TestGameplayAPIDocumentation:
    """Test suite for API documentation and OpenAPI schema."""
    
    def test_openapi_schema_includes_gameplay_endpoints(self):
        """Test that the OpenAPI schema includes gameplay endpoints."""
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        paths = schema.get("paths", {})
        
        # Check that gameplay endpoints are documented
        assert "/api/v1/gameplay/sessions" in paths
        assert "/api/v1/gameplay/sessions/{session_id}" in paths
        assert "/api/v1/gameplay/sessions/{session_id}/choices" in paths
        assert "/api/v1/gameplay/health" in paths
    
    def test_gameplay_endpoints_have_proper_tags(self):
        """Test that gameplay endpoints have proper tags for documentation."""
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        schema = response.json()
        paths = schema.get("paths", {})
        
        # Check that gameplay endpoints have the "gameplay" tag
        sessions_endpoint = paths.get("/api/v1/gameplay/sessions", {})
        post_method = sessions_endpoint.get("post", {})
        assert "gameplay" in post_method.get("tags", [])
