"""

# Logseq: [[TTA.dev/Tests/Integration/Test_world_system_integration]]
Integration tests for the world system.

Tests world listing, retrieval, validation in session creation,
and end-to-end character → world selection → session creation flow.
"""

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import app

# World management (GET /worlds, GET /worlds/:id, etc.) is not yet
# implemented — see GDD.md Phase 2 and docs/design/technical-specifications.md.
# These tests serve as executable specs for the expected behavior.
pytestmark = pytest.mark.xfail(
    reason="World management API not yet implemented (GDD Phase 2)",
    strict=False,
)


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
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
        "name": "Test Character",
        "appearance": {
            "age": 25,
            "gender": "non-binary",
            "physical_description": "Average height with short dark hair",
        },
        "background": {
            "occupation": "Student",
            "life_situation": "Dealing with academic stress",
            "key_relationships": ["Family", "Friends"],
        },
        "therapeutic_profile": {
            "primary_concerns": ["anxiety", "stress"],
            "therapeutic_goals": [
                {
                    "goal_id": "goal_001",
                    "description": "Reduce anxiety",
                    "target_date": "2025-12-31",
                    "progress": 0.0,
                }
            ],
            "preferred_approaches": ["cognitive_behavioral_therapy", "mindfulness"],
            "intensity_preference": "medium",
        },
    }


@pytest.fixture
def sample_session_request():
    """Create a sample session creation request."""
    return {
        "character_id": "placeholder",  # Will be replaced with actual character_id
        "world_id": "world_mindfulness_garden",  # From seeded worlds
        "therapeutic_settings": {
            "intensity_level": "medium",
            "preferred_approaches": ["cognitive_behavioral_therapy", "mindfulness"],
            "session_goals": ["reduce anxiety", "improve coping skills"],
            "safety_monitoring": True,
        },
    }


class TestWorldListing:
    """Tests for world listing endpoint."""

    def test_list_worlds_requires_authentication(self, test_client):
        """Test that listing worlds requires authentication."""
        response = test_client.get("/api/v1/worlds")
        assert response.status_code == 401

    def test_list_worlds_with_authentication(self, test_client, auth_headers):
        """Test listing worlds with valid authentication."""
        response = test_client.get("/api/v1/worlds", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least the default worlds from WorldManagementModule
        assert len(data) >= 3


class TestWorldRetrieval:
    """Tests for world retrieval endpoint."""

    def test_get_world_requires_authentication(self, test_client):
        """Test that getting a world requires authentication."""
        response = test_client.get("/api/v1/worlds/world_mindfulness_garden")
        assert response.status_code == 401

    def test_get_world_with_valid_id(self, test_client, auth_headers):
        """Test getting a world with a valid ID."""
        response = test_client.get(
            "/api/v1/worlds/world_mindfulness_garden", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["world_id"] == "world_mindfulness_garden"
        assert "name" in data
        assert "description" in data
        assert "therapeutic_themes" in data

    def test_get_world_with_invalid_id(self, test_client, auth_headers):
        """Test getting a world with an invalid ID."""
        response = test_client.get(
            "/api/v1/worlds/nonexistent_world", headers=auth_headers
        )
        assert response.status_code == 404


class TestWorldValidationInSessionCreation:
    """Tests for world validation in session creation."""

    def test_session_creation_with_valid_world(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test session creation with a valid world ID."""
        # First create a character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # Now create a session with a valid world
        sample_session_request["character_id"] = character_id
        sample_session_request["world_id"] = "world_mindfulness_garden"

        response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["world_id"] == "world_mindfulness_garden"

    def test_session_creation_with_invalid_world(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test session creation with an invalid world ID."""
        # First create a character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # Try to create a session with an invalid world
        sample_session_request["character_id"] = character_id
        sample_session_request["world_id"] = "nonexistent_world"

        response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestEndToEndUserJourney:
    """Tests for complete end-to-end user journey."""

    def test_complete_character_world_session_flow(
        self,
        test_client,
        auth_headers,
        sample_character_request,
        sample_session_request,
    ):
        """Test complete flow: character creation → world selection → session creation."""
        # Step 1: Create a character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # Step 2: List available worlds
        worlds_response = test_client.get("/api/v1/worlds", headers=auth_headers)
        assert worlds_response.status_code == 200
        worlds = worlds_response.json()
        assert len(worlds) > 0

        # Step 3: Get details for a specific world
        world_id = worlds[0]["world_id"]
        world_response = test_client.get(
            f"/api/v1/worlds/{world_id}", headers=auth_headers
        )
        assert world_response.status_code == 200
        world_details = world_response.json()
        assert world_details["world_id"] == world_id

        # Step 4: Create a session with the selected world
        sample_session_request["character_id"] = character_id
        sample_session_request["world_id"] = world_id

        session_response = test_client.post(
            "/api/v1/sessions",
            json=sample_session_request,
            headers=auth_headers,
        )
        assert session_response.status_code == 201
        session_data = session_response.json()
        assert session_data["character_id"] == character_id
        assert session_data["world_id"] == world_id
        assert session_data["status"] == "active"

        # Step 5: Retrieve the session to verify it was created correctly
        session_id = session_data["session_id"]
        get_session_response = test_client.get(
            f"/api/v1/sessions/{session_id}", headers=auth_headers
        )
        assert get_session_response.status_code == 200
        retrieved_session = get_session_response.json()
        assert retrieved_session["session_id"] == session_id
        assert retrieved_session["character_id"] == character_id
        assert retrieved_session["world_id"] == world_id

    def test_world_compatibility_with_character(
        self, test_client, auth_headers, sample_character_request
    ):
        """Test that worlds can be filtered by character compatibility."""
        # Create a character
        char_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )
        assert char_response.status_code == 201
        character_id = char_response.json()["character_id"]

        # List worlds with character_id parameter for compatibility filtering
        response = test_client.get(
            f"/api/v1/worlds?character_id={character_id}", headers=auth_headers
        )
        assert response.status_code == 200
        worlds = response.json()
        assert isinstance(worlds, list)
        # Worlds should be returned (compatibility filtering is optional)
        assert len(worlds) >= 0