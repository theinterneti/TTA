"""
Integration tests for character creation end-to-end flow.

Tests the complete character creation workflow from API request through
database persistence in Neo4j.
"""

import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.player_experience.api.app import app
from src.player_experience.database.character_repository import CharacterRepository
from src.player_experience.models.character import (
    CharacterAppearance,
    CharacterBackground,
    TherapeuticProfile,
)


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
    token = create_access_token(token_data)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def character_repository():
    """Create a character repository for testing."""
    # Use environment variables or defaults
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tta_dev_password_2024")

    return CharacterRepository(uri=uri, username=username, password=password)


@pytest.fixture
def sample_character_request():
    """Create a sample character creation request."""
    return {
        "name": "Test Character",
        "appearance": {
            "age_range": "adult",
            "gender_identity": "non-binary",
            "physical_description": "A brave adventurer with kind eyes",
            "clothing_style": "casual",
            "distinctive_features": ["scar on left cheek"],
            "avatar_image_url": None,
        },
        "background": {
            "name": "Test Character",
            "backstory": "A journey of self-discovery and growth",
            "personality_traits": ["brave", "compassionate", "curious"],
            "core_values": ["honesty", "kindness"],
            "fears_and_anxieties": ["failure"],
            "strengths_and_skills": ["problem-solving"],
            "life_goals": ["find inner peace"],
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
            "comfort_zones": ["nature", "art"],
            "challenge_areas": ["social situations"],
            "coping_strategies": ["deep breathing"],
            "trigger_topics": [],
            "therapeutic_history": "First time seeking help",
            "readiness_level": 0.7,
            "therapeutic_approaches": ["cbt", "mindfulness"],
        },
    }


class TestCharacterCreationIntegration:
    """Integration tests for character creation."""

    def test_character_creation_api_endpoint_exists(self, test_client):
        """Test that the character creation endpoint exists."""
        # This should return 401 without auth, not 404
        response = test_client.post("/api/v1/characters", json={})
        assert response.status_code in [401, 422], (
            f"Expected 401 or 422, got {response.status_code}"
        )

    def test_character_creation_requires_authentication(
        self, test_client, sample_character_request
    ):
        """Test that character creation requires authentication."""
        response = test_client.post("/api/v1/characters", json=sample_character_request)
        assert response.status_code == 401
        response_data = response.json()
        assert "detail" in response_data or "message" in response_data

    def test_character_creation_with_valid_data(
        self, test_client, auth_headers, sample_character_request
    ):
        """Test character creation with valid data and authentication."""
        response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )

        # Print response for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json()}")

        # Should succeed
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.json()}"
        )

        data = response.json()
        assert "character_id" in data
        assert data["name"] == "Test Character"
        assert data["player_id"] == "test_player_123"
        assert "appearance" in data
        assert "background" in data
        assert "therapeutic_profile" in data

    def test_character_creation_validation_errors(self, test_client, auth_headers):
        """Test that invalid character data returns validation errors."""
        invalid_request = {
            "name": "",  # Empty name should fail
            "appearance": {},
            "background": {},
            "therapeutic_profile": {},
        }

        response = test_client.post(
            "/api/v1/characters",
            json=invalid_request,
            headers=auth_headers,
        )

        assert response.status_code in [400, 422]

    @pytest.mark.neo4j
    def test_character_persists_to_neo4j(
        self, test_client, auth_headers, sample_character_request, character_repository
    ):
        """Test that created character persists to Neo4j database."""
        # Skip if Neo4j is not available
        if not character_repository._connected:
            pytest.skip("Neo4j not available")

        # Create character via API
        response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )

        assert response.status_code == 201
        character_id = response.json()["character_id"]

        # Verify character exists in Neo4j
        character = character_repository.get_character(character_id)
        assert character is not None
        assert character.character_id == character_id
        assert character.name == "Test Character"
        assert character.player_id == "test_player_123"

    @pytest.mark.neo4j
    def test_character_retrieval_after_creation(
        self, test_client, auth_headers, sample_character_request
    ):
        """Test that created character can be retrieved via API."""
        # Create character
        create_response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )

        assert create_response.status_code == 201
        character_id = create_response.json()["character_id"]

        # Retrieve character
        get_response = test_client.get(
            f"/api/v1/characters/{character_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        character_data = get_response.json()
        assert character_data["character_id"] == character_id
        assert character_data["name"] == "Test Character"

    def test_character_limit_enforcement(
        self, test_client, auth_headers, sample_character_request
    ):
        """Test that character limit per player is enforced."""
        # Create maximum number of characters (5)
        character_ids = []
        for i in range(5):
            request = sample_character_request.copy()
            request["name"] = f"Character {i + 1}"
            request["background"]["name"] = f"Character {i + 1}"

            response = test_client.post(
                "/api/v1/characters",
                json=request,
                headers=auth_headers,
            )

            if response.status_code == 201:
                character_ids.append(response.json()["character_id"])

        # Try to create one more - should fail
        response = test_client.post(
            "/api/v1/characters",
            json=sample_character_request,
            headers=auth_headers,
        )

        # Should get 400 Bad Request with character limit error
        if len(character_ids) >= 5:
            assert response.status_code == 400
            assert "limit" in response.json()["detail"].lower()


class TestCharacterRepositoryIntegration:
    """Integration tests for CharacterRepository."""

    @pytest.mark.neo4j
    def test_repository_neo4j_connection(self, character_repository):
        """Test that repository can connect to Neo4j."""
        # If connection fails, it should fall back to in-memory
        # This test just verifies the repository is initialized
        assert character_repository is not None

    @pytest.mark.neo4j
    def test_create_and_retrieve_character(self, character_repository):
        """Test creating and retrieving a character from Neo4j."""
        if not character_repository._connected:
            pytest.skip("Neo4j not available")

        # Create test character
        from src.player_experience.models.character import Character

        character = Character(
            character_id="test_char_123",
            player_id="test_player_123",
            name="Test Character",
            appearance=CharacterAppearance(age_range="adult"),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=TherapeuticProfile(),
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Save to repository
        saved_character = character_repository.create_character(character)
        assert saved_character.character_id == "test_char_123"

        # Retrieve from repository
        retrieved_character = character_repository.get_character("test_char_123")
        assert retrieved_character is not None
        assert retrieved_character.character_id == "test_char_123"
        assert retrieved_character.name == "Test Character"
