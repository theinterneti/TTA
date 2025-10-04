"""
Integration tests for Player Management API endpoints.

This module provides comprehensive tests for the player management REST API,
including authentication, authorization, CRUD operations, and error handling.
"""

from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.player_experience.api.app import create_app
from src.player_experience.api.auth import (
    ALGORITHM,
    SECRET_KEY,
)
from src.player_experience.managers.player_profile_manager import (
    DataAccessRestrictedError,
    PlayerProfileManagerError,
)
from src.player_experience.models.enums import IntensityLevel, TherapeuticApproach
from src.player_experience.models.player import (
    PlayerProfile,
    PrivacySettings,
    TherapeuticPreferences,
)


class TestPlayerManagementAPI:
    """Test suite for Player Management API endpoints."""

    @pytest.fixture
    def app(self):
        """Create FastAPI test application."""
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_player_manager(self):
        """Create mock player profile manager."""
        return Mock()

    @pytest.fixture
    def sample_player_profile(self):
        """Create sample player profile for testing."""
        return PlayerProfile(
            player_id="test-player-123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now(),
            therapeutic_preferences=TherapeuticPreferences(
                intensity_level=IntensityLevel.MEDIUM,
                preferred_approaches=[
                    TherapeuticApproach.CBT,
                    TherapeuticApproach.MINDFULNESS,
                ],
                trigger_warnings=["violence", "trauma"],
                comfort_topics=["nature", "music"],
                avoid_topics=["death", "loss"],
                session_duration_preference=45,
                reminder_frequency="weekly",
            ),
            privacy_settings=PrivacySettings(
                data_collection_consent=True,
                research_participation_consent=False,
                progress_sharing_enabled=True,
                anonymous_analytics_enabled=True,
                session_recording_enabled=False,
                data_retention_period_days=365,
            ),
        )

    @pytest.fixture
    def auth_headers(self, sample_player_profile):
        """Create authentication headers for testing."""
        token_data = {
            "sub": sample_player_profile.player_id,
            "username": sample_player_profile.username,
            "email": sample_player_profile.email,
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def invalid_auth_headers(self):
        """Create invalid authentication headers for testing."""
        return {"Authorization": "Bearer invalid-token"}

    def test_create_player_success(
        self, client, mock_player_manager, sample_player_profile
    ):
        """Test successful player profile creation."""
        # Mock manager response
        mock_player_manager.create_player_profile.return_value = sample_player_profile

        # Prepare request data
        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "therapeutic_preferences": {
                "intensity_level": "medium",
                "preferred_approaches": ["cognitive_behavioral_therapy", "mindfulness"],
                "trigger_warnings": ["violence", "trauma"],
                "comfort_topics": ["nature", "music"],
                "avoid_topics": ["death", "loss"],
                "session_duration_preference": 45,
                "reminder_frequency": "weekly",
            },
            "privacy_settings": {
                "data_collection_consent": True,
                "research_participation_consent": False,
                "progress_sharing_enabled": True,
                "anonymous_analytics_enabled": True,
                "session_recording_enabled": False,
                "data_retention_period_days": 365,
            },
        }

        # Mock both the repository and manager
        with (
            patch(
                "src.player_experience.database.player_profile_repository.PlayerProfileRepository"
            ),
            patch(
                "src.player_experience.api.routers.players.get_player_manager",
                return_value=mock_player_manager,
            ),
        ):
            response = client.post("/api/v1/players/", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["player_id"] == sample_player_profile.player_id
        assert data["username"] == sample_player_profile.username
        assert data["email"] == sample_player_profile.email
        assert data["therapeutic_preferences"]["intensity_level"] == "medium"
        assert len(data["therapeutic_preferences"]["preferred_approaches"]) == 2

        # Verify manager was called correctly
        mock_player_manager.create_player_profile.assert_called_once()

    def test_create_player_validation_error(self, client, mock_player_manager):
        """Test player creation with validation errors."""
        request_data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "123",  # Too short
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.post("/api/v1/players/", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Validation Error" in data["error"]

    def test_create_player_username_exists(self, client, mock_player_manager):
        """Test player creation with existing username."""
        mock_player_manager.create_player_profile.side_effect = (
            PlayerProfileManagerError("Username 'testuser' already exists")
        )

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.post("/api/v1/players/", json=request_data)

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    def test_get_player_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful player profile retrieval."""
        mock_player_manager.get_player_profile.return_value = sample_player_profile

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == sample_player_profile.player_id
        assert data["username"] == sample_player_profile.username
        assert data["email"] == sample_player_profile.email

        # Verify manager was called with correct parameters
        mock_player_manager.get_player_profile.assert_called_once_with(
            sample_player_profile.player_id, sample_player_profile.player_id
        )

    def test_get_player_not_found(self, client, mock_player_manager, auth_headers):
        """Test player retrieval when player doesn't exist."""
        mock_player_manager.get_player_profile.return_value = None

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.get(
                "/api/v1/players/nonexistent-player", headers=auth_headers
            )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_get_player_unauthorized(
        self, client, mock_player_manager, sample_player_profile
    ):
        """Test player retrieval without authentication."""
        response = client.get(f"/api/v1/players/{sample_player_profile.player_id}")

        assert response.status_code == 401
        data = response.json()
        assert "Authentication Required" in data["error"]

    def test_get_player_access_denied(self, client, mock_player_manager, auth_headers):
        """Test player retrieval with access denied."""
        mock_player_manager.get_player_profile.side_effect = DataAccessRestrictedError(
            "Access denied"
        )

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.get(
                "/api/v1/players/other-player-id", headers=auth_headers
            )

        assert response.status_code == 403
        data = response.json()
        assert "Access denied" in data["detail"]

    def test_update_player_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful player profile update."""
        mock_player_manager.update_player_profile.return_value = True
        mock_player_manager.get_player_profile.return_value = sample_player_profile

        request_data = {
            "username": "updateduser",
            "therapeutic_preferences": {
                "intensity_level": "high",
                "preferred_approaches": ["mindfulness"],
                "session_duration_preference": 60,
            },
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.put(
                f"/api/v1/players/{sample_player_profile.player_id}",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == sample_player_profile.player_id

        # Verify manager was called correctly
        mock_player_manager.update_player_profile.assert_called_once()
        call_args = mock_player_manager.update_player_profile.call_args
        assert call_args[0][0] == sample_player_profile.player_id  # player_id
        assert "username" in call_args[0][1]  # updates dict
        assert "therapeutic_preferences" in call_args[0][1]
        assert call_args[0][2] == sample_player_profile.player_id  # accessor_id

    def test_update_player_validation_error(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test player update with validation errors."""
        request_data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid format
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.put(
                f"/api/v1/players/{sample_player_profile.player_id}",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Validation Error" in data["error"]

    def test_update_player_username_conflict(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test player update with username conflict."""
        mock_player_manager.update_player_profile.side_effect = (
            PlayerProfileManagerError("Username 'existinguser' already exists")
        )

        request_data = {"username": "existinguser"}

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.put(
                f"/api/v1/players/{sample_player_profile.player_id}",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    def test_delete_player_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful player profile deletion."""
        mock_player_manager.delete_player_profile.return_value = True

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.delete(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 204

        # Verify manager was called correctly
        mock_player_manager.delete_player_profile.assert_called_once_with(
            sample_player_profile.player_id, sample_player_profile.player_id
        )

    def test_delete_player_not_found(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test player deletion when player doesn't exist."""
        mock_player_manager.delete_player_profile.return_value = False

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.delete(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_export_player_data_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful player data export."""
        export_data = {
            "player_profile": {
                "player_id": sample_player_profile.player_id,
                "username": sample_player_profile.username,
                "email": sample_player_profile.email,
            },
            "export_metadata": {
                "export_date": datetime.now().isoformat(),
                "export_requested_by": sample_player_profile.player_id,
                "data_format_version": "1.0",
            },
        }
        mock_player_manager.export_player_data.return_value = export_data

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}/export",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "export_data" in data
        assert "export_date" in data
        assert (
            data["export_data"]["player_profile"]["player_id"]
            == sample_player_profile.player_id
        )

        # Verify manager was called correctly
        mock_player_manager.export_player_data.assert_called_once_with(
            sample_player_profile.player_id, sample_player_profile.player_id
        )

    def test_update_therapeutic_preferences_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful therapeutic preferences update."""
        mock_player_manager.update_therapeutic_preferences.return_value = True
        mock_player_manager.get_player_profile.return_value = sample_player_profile

        request_data = {
            "intensity_level": "high",
            "preferred_approaches": ["mindfulness", "acceptance_commitment_therapy"],
            "trigger_warnings": ["violence"],
            "session_duration_preference": 60,
            "reminder_frequency": "daily",
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.patch(
                f"/api/v1/players/{sample_player_profile.player_id}/therapeutic-preferences",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == sample_player_profile.player_id

        # Verify manager was called correctly
        mock_player_manager.update_therapeutic_preferences.assert_called_once()

    def test_update_privacy_settings_success(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test successful privacy settings update."""
        mock_player_manager.update_privacy_settings.return_value = True
        mock_player_manager.get_player_profile.return_value = sample_player_profile

        request_data = {
            "data_collection_consent": False,
            "research_participation_consent": True,
            "progress_sharing_enabled": False,
            "data_retention_period_days": 180,
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.patch(
                f"/api/v1/players/{sample_player_profile.player_id}/privacy-settings",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == sample_player_profile.player_id

        # Verify manager was called correctly
        mock_player_manager.update_privacy_settings.assert_called_once()

    def test_privacy_settings_validation_error(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test privacy settings update with validation error."""
        request_data = {"data_retention_period_days": 10}  # Too short, minimum is 30

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.patch(
                f"/api/v1/players/{sample_player_profile.player_id}/privacy-settings",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Validation Error" in data["error"]

    def test_therapeutic_preferences_validation_error(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test therapeutic preferences update with validation error."""
        request_data = {
            "session_duration_preference": 200,  # Too long, maximum is 120
            "preferred_approaches": ["invalid_approach"],  # Invalid approach
        }

        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.patch(
                f"/api/v1/players/{sample_player_profile.player_id}/therapeutic-preferences",
                json=request_data,
                headers=auth_headers,
            )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Validation Error" in data["error"]

    def test_cross_player_access_denied(
        self, client, mock_player_manager, auth_headers
    ):
        """Test that players cannot access other players' profiles."""
        # Try to access a different player's profile
        other_player_id = "other-player-456"

        response = client.get(
            f"/api/v1/players/{other_player_id}", headers=auth_headers
        )

        # Should be denied by the require_player_access dependency
        assert response.status_code == 403
        data = response.json()
        assert "Access denied" in data["detail"]

    def test_invalid_token_authentication(
        self, client, mock_player_manager, sample_player_profile, invalid_auth_headers
    ):
        """Test API access with invalid authentication token."""
        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=invalid_auth_headers,
            )

        assert response.status_code == 401
        data = response.json()
        assert "Authentication Failed" in data["error"]

    def test_missing_authorization_header(
        self, client, mock_player_manager, sample_player_profile
    ):
        """Test API access without authorization header."""
        response = client.get(f"/api/v1/players/{sample_player_profile.player_id}")

        assert response.status_code == 401
        data = response.json()
        assert "Authentication Required" in data["error"]

    def test_malformed_authorization_header(
        self, client, mock_player_manager, sample_player_profile
    ):
        """Test API access with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}

        response = client.get(
            f"/api/v1/players/{sample_player_profile.player_id}", headers=headers
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid Authorization Header" in data["error"]

    def test_api_documentation_generation(self, client):
        """Test that API documentation is properly generated."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        openapi_spec = response.json()

        # Check that player endpoints are documented
        assert "/api/v1/players/" in openapi_spec["paths"]
        assert "/api/v1/players/{player_id}" in openapi_spec["paths"]
        assert "/api/v1/players/{player_id}/export" in openapi_spec["paths"]
        assert (
            "/api/v1/players/{player_id}/therapeutic-preferences"
            in openapi_spec["paths"]
        )
        assert "/api/v1/players/{player_id}/privacy-settings" in openapi_spec["paths"]

        # Check that request/response models are documented
        assert "CreatePlayerRequest" in openapi_spec["components"]["schemas"]
        assert "UpdatePlayerRequest" in openapi_spec["components"]["schemas"]
        assert "PlayerResponse" in openapi_spec["components"]["schemas"]
        assert "TherapeuticPreferencesRequest" in openapi_spec["components"]["schemas"]
        assert "PrivacySettingsRequest" in openapi_spec["components"]["schemas"]

    def test_cors_headers(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test that CORS headers are properly set."""
        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            mock_player_manager.get_player_profile.return_value = sample_player_profile

            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers

    def test_security_headers(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test that security headers are properly set."""
        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            mock_player_manager.get_player_profile.return_value = sample_player_profile

            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers
        assert "strict-transport-security" in response.headers
        assert "content-security-policy" in response.headers

    def test_rate_limiting_headers(
        self, client, mock_player_manager, sample_player_profile, auth_headers
    ):
        """Test that rate limiting headers are properly set."""
        with patch(
            "src.player_experience.api.routers.players.get_player_manager",
            return_value=mock_player_manager,
        ):
            mock_player_manager.get_player_profile.return_value = sample_player_profile

            response = client.get(
                f"/api/v1/players/{sample_player_profile.player_id}",
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "x-ratelimit-limit" in response.headers
        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-reset" in response.headers


# Additional test utilities


def create_test_player_data(
    username: str = "testuser",
    email: str = "test@example.com",
    intensity_level: str = "medium",
) -> dict[str, Any]:
    """Create test player data for API requests."""
    return {
        "username": username,
        "email": email,
        "password": "securepassword123",
        "therapeutic_preferences": {
            "intensity_level": intensity_level,
            "preferred_approaches": ["cognitive_behavioral_therapy"],
            "session_duration_preference": 30,
            "reminder_frequency": "weekly",
        },
        "privacy_settings": {
            "data_collection_consent": True,
            "research_participation_consent": False,
            "progress_sharing_enabled": False,
            "data_retention_period_days": 365,
        },
    }


def create_auth_token(player_id: str, username: str, email: str) -> str:
    """Create authentication token for testing."""
    token_data = {
        "sub": player_id,
        "username": username,
        "email": email,
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


if __name__ == "__main__":
    pytest.main([__file__])
