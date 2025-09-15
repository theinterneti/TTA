"""
Tests for the FastAPI application structure.

This module tests the basic FastAPI application setup, middleware,
and authentication structure.
"""

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import create_app
from src.player_experience.api.config import TestingSettings


@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    # Use test settings
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()

    app = create_app()
    return app


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Player Experience Interface API is running"}


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "player-experience-api"


def test_security_headers(client):
    """Test that security headers are added to responses."""
    response = client.get("/")

    # Check security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-XSS-Protection" in response.headers
    assert "Strict-Transport-Security" in response.headers


def test_cors_headers(client):
    """Test CORS headers on OPTIONS request."""
    response = client.options("/")
    assert response.status_code == 200


def test_rate_limiting_headers(client):
    """Test that rate limiting headers are present."""
    response = client.get("/")

    # Check rate limiting headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_processing_time_header(client):
    """Test that processing time header is added."""
    response = client.get("/")
    assert "X-Process-Time" in response.headers


def test_therapeutic_safety_headers(client):
    """Test that therapeutic safety headers are present."""
    response = client.get("/")
    assert "X-Therapeutic-Safety" in response.headers
    assert response.headers["X-Therapeutic-Safety"] == "monitored"
    assert "X-Crisis-Hotline" in response.headers
    assert response.headers["X-Crisis-Hotline"] == "988"


def test_auth_router_included(client):
    """Test that authentication router is included."""
    # Test a public auth endpoint
    response = client.post(
        "/api/v1/auth/login", json={"username": "test", "password": "test"}
    )
    # Should return 401 for invalid credentials, not 404
    assert response.status_code == 401


def test_players_router_included(client):
    """Test that players router is included."""
    response = client.get("/api/v1/players/")
    # Should return 401 for missing auth, not 404
    assert response.status_code == 401


def test_characters_router_included(client):
    """Test that characters router is included."""
    response = client.get("/api/v1/characters/")
    # Should return 401 for missing auth, not 404
    assert response.status_code == 401


def test_worlds_router_included(client):
    """Test that worlds router is included."""
    response = client.get("/api/v1/worlds/")
    # Should return 401 for missing auth, not 404
    assert response.status_code == 401


def test_openapi_docs_available(client):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_authentication_middleware_public_routes(client):
    """Test that public routes don't require authentication."""
    public_routes = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    for route in public_routes:
        response = client.get(route)
        # Should not return 401 for public routes
        assert response.status_code != 401


def test_authentication_middleware_protected_routes(client):
    """Test that protected routes require authentication."""
    protected_routes = [
        "/api/v1/players/",
        "/api/v1/characters/",
        "/api/v1/worlds/",
    ]

    for route in protected_routes:
        response = client.get(route)
        # Should return 401 for missing authentication
        assert response.status_code == 401
        assert "Authorization header is required" in response.json()["message"]


def test_invalid_authorization_header(client):
    """Test handling of invalid authorization headers."""
    # Test missing Bearer scheme
    response = client.get("/api/v1/players/", headers={"Authorization": "InvalidToken"})
    assert response.status_code == 401
    assert (
        "Authorization header must be in format: Bearer <token>"
        in response.json()["message"]
    )

    # Test invalid token
    response = client.get(
        "/api/v1/players/", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert "Authentication Failed" in response.json()["error"]
