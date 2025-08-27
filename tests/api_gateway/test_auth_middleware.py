"""
Tests for the API Gateway authentication middleware.

This module contains unit tests for JWT authentication, role-based access control,
and integration with the TTA authentication system.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request, Response
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from src.api_gateway.middleware.auth import AuthenticationMiddleware
from src.api_gateway.models import AuthContext, UserRole, UserPermissions, PermissionLevel, TherapeuticPermission


@pytest.fixture
def mock_tta_auth_service():
    """Create a mock TTA authentication service."""
    mock_service = MagicMock()
    
    # Mock authenticated user
    mock_user = MagicMock()
    mock_user.user_id = str(uuid4())
    mock_user.username = "test_user"
    mock_user.email = "test@example.com"
    mock_user.role = MagicMock()
    mock_user.role.value = "player"
    mock_user.permissions = []
    mock_user.session_id = "test_session"
    mock_user.mfa_verified = False
    
    mock_service.verify_access_token.return_value = mock_user
    
    return mock_service


@pytest.fixture
def auth_middleware():
    """Create authentication middleware instance."""
    app = Starlette()
    return AuthenticationMiddleware(app)


@pytest.fixture
def mock_request():
    """Create a mock request."""
    request = MagicMock(spec=Request)
    request.url.path = "/api/v1/test"
    request.method = "GET"
    request.headers = {"authorization": "Bearer test_token"}
    request.query_params = {}
    request.client.host = "127.0.0.1"
    request.state = MagicMock()
    return request


class TestAuthenticationMiddleware:
    """Test cases for AuthenticationMiddleware."""
    
    @pytest.mark.asyncio
    async def test_public_path_bypass(self, auth_middleware, mock_request):
        """Test that public paths bypass authentication."""
        mock_request.url.path = "/health"
        
        call_next = AsyncMock(return_value=Response())
        
        response = await auth_middleware.dispatch(mock_request, call_next)
        
        assert isinstance(response, Response)
        call_next.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_missing_token_auth_required(self, auth_middleware, mock_request):
        """Test authentication failure when token is missing."""
        mock_request.headers = {}  # No authorization header
        
        call_next = AsyncMock()
        
        response = await auth_middleware.dispatch(mock_request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        call_next.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('src.api_gateway.middleware.auth.AuthService')
    async def test_successful_authentication(self, mock_auth_service_class, auth_middleware, mock_request, mock_tta_auth_service):
        """Test successful authentication with valid token."""
        mock_auth_service_class.return_value = mock_tta_auth_service
        
        call_next = AsyncMock(return_value=Response())
        
        response = await auth_middleware.dispatch(mock_request, call_next)
        
        assert isinstance(response, Response)
        call_next.assert_called_once()
        
        # Check that auth context was set
        assert hasattr(mock_request.state, 'auth_context')
        assert hasattr(mock_request.state, 'user_id')
        assert hasattr(mock_request.state, 'username')
    
    @pytest.mark.asyncio
    @patch('src.api_gateway.middleware.auth.AuthService')
    async def test_invalid_token(self, mock_auth_service_class, auth_middleware, mock_request):
        """Test authentication failure with invalid token."""
        mock_auth_service = MagicMock()
        mock_auth_service.verify_access_token.side_effect = Exception("Invalid token")
        mock_auth_service_class.return_value = mock_auth_service
        
        call_next = AsyncMock()
        
        response = await auth_middleware.dispatch(mock_request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        call_next.assert_not_called()
    
    def test_extract_token_from_header(self, auth_middleware, mock_request):
        """Test token extraction from Authorization header."""
        mock_request.headers = {"authorization": "Bearer test_token_123"}
        
        token = auth_middleware._extract_token(mock_request)
        
        assert token == "test_token_123"
    
    def test_extract_token_from_query_param(self, auth_middleware, mock_request):
        """Test token extraction from query parameter."""
        mock_request.headers = {}
        mock_request.query_params = {"token": "query_token_123"}
        
        token = auth_middleware._extract_token(mock_request)
        
        assert token == "query_token_123"
    
    def test_no_token_found(self, auth_middleware, mock_request):
        """Test when no token is found."""
        mock_request.headers = {}
        mock_request.query_params = {}
        
        token = auth_middleware._extract_token(mock_request)
        
        assert token is None
    
    def test_is_public_path(self, auth_middleware):
        """Test public path detection."""
        assert auth_middleware._is_public_path("/")
        assert auth_middleware._is_public_path("/health")
        assert auth_middleware._is_public_path("/health/live")
        assert auth_middleware._is_public_path("/metrics")
        assert auth_middleware._is_public_path("/docs")
        
        assert not auth_middleware._is_public_path("/api/v1/test")
        assert not auth_middleware._is_public_path("/private")
    
    def test_is_auth_optional_path(self, auth_middleware):
        """Test auth optional path detection."""
        assert auth_middleware._is_auth_optional_path("/api/v1/auth/login")
        assert auth_middleware._is_auth_optional_path("/api/v1/auth/register")
        assert auth_middleware._is_auth_optional_path("/auth/refresh")
        
        assert not auth_middleware._is_auth_optional_path("/api/v1/users")
        assert not auth_middleware._is_auth_optional_path("/api/v1/characters")
    
    def test_get_client_ip_forwarded(self, auth_middleware, mock_request):
        """Test client IP extraction from forwarded headers."""
        mock_request.headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1"}
        
        ip = auth_middleware._get_client_ip(mock_request)
        
        assert ip == "192.168.1.1"
    
    def test_get_client_ip_real_ip(self, auth_middleware, mock_request):
        """Test client IP extraction from real IP header."""
        mock_request.headers = {"x-real-ip": "192.168.1.2"}
        
        ip = auth_middleware._get_client_ip(mock_request)
        
        assert ip == "192.168.1.2"
    
    def test_get_client_ip_direct(self, auth_middleware, mock_request):
        """Test client IP extraction from direct connection."""
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.3"
        
        ip = auth_middleware._get_client_ip(mock_request)
        
        assert ip == "192.168.1.3"
    
    def test_convert_tta_role_to_gateway_role(self, auth_middleware):
        """Test TTA role to gateway role conversion."""
        from src.player_experience.models.auth import UserRole as TTAUserRole
        
        assert auth_middleware._convert_tta_role_to_gateway_role(TTAUserRole.PLAYER) == UserRole.PATIENT
        assert auth_middleware._convert_tta_role_to_gateway_role(TTAUserRole.THERAPIST) == UserRole.THERAPIST
        assert auth_middleware._convert_tta_role_to_gateway_role(TTAUserRole.ADMIN) == UserRole.ADMIN
    
    def test_determine_safety_level(self, auth_middleware):
        """Test safety level determination."""
        assert auth_middleware._determine_safety_level(UserRole.PATIENT, True) == 4
        assert auth_middleware._determine_safety_level(UserRole.PATIENT, False) == 3
        assert auth_middleware._determine_safety_level(UserRole.THERAPIST, True) == 2
        assert auth_middleware._determine_safety_level(UserRole.ADMIN, False) == 1
    
    def test_create_auth_error_response(self, auth_middleware):
        """Test authentication error response creation."""
        response = auth_middleware._create_auth_error_response("Test error")
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers


class TestAuthContextCreation:
    """Test cases for authentication context creation."""
    
    @pytest.fixture
    def sample_user_data(self):
        """Create sample user data."""
        return {
            "user_id": str(uuid4()),
            "username": "test_user",
            "email": "test@example.com",
            "role": MagicMock(),
            "permissions": [],
            "session_id": "test_session",
            "mfa_verified": False
        }
    
    def test_create_auth_context(self, auth_middleware, mock_request, sample_user_data):
        """Test authentication context creation."""
        from src.player_experience.models.auth import UserRole as TTAUserRole
        sample_user_data["role"] = TTAUserRole.PLAYER
        
        auth_context = auth_middleware._create_auth_context(mock_request, sample_user_data, "test_token")
        
        assert isinstance(auth_context, AuthContext)
        assert auth_context.username == "test_user"
        assert auth_context.authenticated is True
        assert auth_context.permissions.role == UserRole.PATIENT
        assert auth_context.client_ip == "127.0.0.1"


@pytest.mark.asyncio
async def test_middleware_integration():
    """Integration test for authentication middleware."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware)
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/protected")
    async def protected():
        return {"message": "Protected"}
    
    client = TestClient(app)
    
    # Test public endpoint
    response = client.get("/")
    assert response.status_code == 200
    
    # Test protected endpoint without auth
    response = client.get("/protected")
    assert response.status_code == 401
