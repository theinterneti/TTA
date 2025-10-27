"""
Integration tests for session engine.

Tests the complete session lifecycle:
- Session creation with character and world
- Session retrieval
- Session updates
- Session state persistence
- End-to-end user journey (character → session → conversation)
"""

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import app


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    # Create a test JWT token
    from src.player_experience.api.auth import create_access_token

    token_data = {
        "sub": "test_player_123",
        "player_id": "test_player_123",
        "username": "test_user",
    }
    token = create_access_token(data=token_data)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_character_request():
    """Create a sample character creation request."""
    return {
        "name": "Test Session Character",
        "appearance": {
            "age_range": "adult",
            "gender_identity": "non-binary",
            "physical_description": "A calm and supportive presence",
            "clothing_style": "casual",
            "distinctive_features": ["calm demeanor"],
            "avatar_image_url": None,
        },
        "background": {
            "name": "Test Session Character",
            "backstory": "A journey of therapeutic growth",
            "personality_traits": ["calm", "supportive", "empathetic"],
            "core_values": ["compassion", "growth"],
            "fears_and_anxieties": ["failure"],
            "strengths_and_skills": ["active listening"],
            "life_goals": ["help others"],
            "relationships": {},
        },
        "therapeutic_profile": {
            "primary_concerns": ["anxiety", "stress"],
            "therapeutic_goals": [
                {
                    "goal_id": "goal_001",
                    "description": "Manage anxiety effectively",
                    "therapeutic_approaches": ["cbt", "mindfulness"],
                    "progress_percentage": 0.0,
                    "is_active": True,
                }
            ],
            "preferred_intensity": "medium",
            "comfort_with_vulnerability": 0.5,
            "response_to_challenge": 0.5,
        },
    }


@pytest.fixture
def sample_session_request():
    """Create a sample session creation request."""
    return {
        "character_id": "placeholder",  # Will be replaced with actual character_id
        "world_id": "test_world_001",
        "therapeutic_settings": {
            "intensity_level": "medium",
            "preferred_approaches": ["cognitive_behavioral_therapy", "mindfulness"],
            "session_goals": ["reduce anxiety", "improve coping skills"],
            "safety_monitoring": True,
        },
    }


class TestSessionCreation:
    """Test session creation functionality."""

    def test_session_creation_requires_authentication(
        self, test_client, sample_session_request
    ):
        """Test that session creation requires authentication."""
        response = test_client.post("/api/v1/sessions", json=sample_session_request)
        assert response.status_code in [401, 403]

    def test_session_creation_with_valid_character(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test session creation with a valid character."""
        # First create a character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # Now create a session with that character
        sample_session_request["character_id"] = character_id
        response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["character_id"] == character_id
        assert data["world_id"] == "test_world_001"
        assert data["status"] == "active"
        assert "created_at" in data

    def test_session_creation_with_invalid_character(
        self, test_client, auth_headers, sample_session_request
    ):
        """Test session creation with an invalid character ID."""
        sample_session_request["character_id"] = "nonexistent_character_id"
        response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json().get("detail", "").lower()


class TestSessionRetrieval:
    """Test session retrieval functionality."""

    def test_get_session_by_id(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test retrieving a session by ID."""
        # Create character and session
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        character_id = char_response.json()["character_id"]

        sample_session_request["character_id"] = character_id
        session_response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        session_id = session_response.json()["session_id"]

        # Retrieve the session
        response = test_client.get(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["character_id"] == character_id
        assert data["world_id"] == "test_world_001"
        assert data["status"] == "active"
        assert "created_at" in data
        assert "last_interaction" in data

    def test_get_nonexistent_session(self, test_client, auth_headers):
        """Test retrieving a nonexistent session."""
        response = test_client.get(
            "/api/v1/sessions/nonexistent_session_id",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSessionUpdate:
    """Test session update functionality."""

    def test_update_session_therapeutic_settings(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test updating a session's therapeutic settings."""
        # Create character and session
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        character_id = char_response.json()["character_id"]

        sample_session_request["character_id"] = character_id
        session_response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        session_id = session_response.json()["session_id"]

        # Update the session
        update_request = {
            "therapeutic_settings": {
                "intensity_level": "high",
                "preferred_approaches": [
                    "dialectical_behavioral_therapy",
                    "acceptance_commitment_therapy",
                ],
                "session_goals": ["build resilience"],
                "safety_monitoring": False,
            }
        }
        response = test_client.put(
            f"/api/v1/sessions/{session_id}",
            json=update_request,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "last_interaction" in data


class TestSessionProgress:
    """Test session progress tracking."""

    def test_get_session_progress(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test retrieving session progress."""
        # Create character and session
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        character_id = char_response.json()["character_id"]

        sample_session_request["character_id"] = character_id
        session_response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        session_id = session_response.json()["session_id"]

        # Get session progress
        response = test_client.get(
            f"/api/v1/sessions/{session_id}/progress",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["character_id"] == character_id
        assert data["world_id"] == "test_world_001"
        assert "progress" in data
        assert "completed_steps" in data["progress"]
        assert "total_steps" in data["progress"]


class TestEndToEndUserJourney:
    """Test complete end-to-end user journey."""

    def test_complete_user_journey(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test complete user journey: character creation → session creation → session retrieval."""
        # Step 1: Create character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # Step 2: Create session with character
        sample_session_request["character_id"] = character_id
        session_response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["session_id"]

        # Step 3: Retrieve session
        get_response = test_client.get(
            f"/api/v1/sessions/{session_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["character_id"] == character_id

        # Step 4: Get session progress
        progress_response = test_client.get(
            f"/api/v1/sessions/{session_id}/progress",
            headers=auth_headers,
        )
        assert progress_response.status_code == 200
        assert progress_response.json()["session_id"] == session_id
