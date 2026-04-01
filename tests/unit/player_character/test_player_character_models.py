"""
Unit tests for PlayerCharacter model (Pydantic) and related utilities.

Tests cover:
- PlayerCharacter construction with required fields
- Default values: id auto-generated as UUID, status=DRAFT, empty lists
- PlayerCharacter.to_neo4j_properties() returns correct flat dict
- PlayerCharacter.from_neo4j_properties() round-trips through dict
- PlayerCharacterStatus enum values are lowercase strings
- Validation: name must be 1-100 characters
- Validation: name empty string raises ValidationError
- Validation: name > 100 chars raises ValidationError
- traits and skills accept arbitrary lists
- player_id defaults to empty string (auth id optional at creation)
- metadata dict is preserved
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from src.components.player_character.models import (
    PlayerCharacter,
    PlayerCharacterStatus,
)

pytestmark = pytest.mark.unit


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def minimal_character() -> PlayerCharacter:
    """Return a minimal valid PlayerCharacter."""
    return PlayerCharacter(name="Seren", world_id="world-abc-123")


@pytest.fixture()
def full_character() -> PlayerCharacter:
    """Return a fully-populated PlayerCharacter for serialization tests."""
    return PlayerCharacter(
        id="char-001",
        name="Aldric",
        world_id="world-xyz",
        background="A former scribe who fled the capital.",
        traits=["quietly stubborn", "deeply curious"],
        skills=["negotiation", "arcane reading"],
        faction_eligibility=["merchant guilds", "resistance movements"],
        starting_location="The Lower Gate",
        status=PlayerCharacterStatus.ACTIVE,
        player_id="player-999",
        metadata={"session_count": 3},
    )


# ── PlayerCharacterStatus enum ────────────────────────────────────────────────


def test_player_character_status_values() -> None:
    """PlayerCharacterStatus is a StrEnum with expected lowercase values."""
    assert PlayerCharacterStatus.DRAFT == "draft"
    assert PlayerCharacterStatus.ACTIVE == "active"
    assert PlayerCharacterStatus.PAUSED == "paused"
    assert PlayerCharacterStatus.RETIRED == "retired"


# ── Construction and defaults ─────────────────────────────────────────────────


def test_minimal_construction_succeeds(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter constructs with only name and world_id."""
    # Assert
    assert minimal_character.name == "Seren"
    assert minimal_character.world_id == "world-abc-123"


def test_default_status_is_draft(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter.status defaults to DRAFT."""
    assert minimal_character.status == PlayerCharacterStatus.DRAFT


def test_default_id_is_valid_uuid(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter.id is auto-generated as a valid UUID string."""
    # Act — parse id as UUID (raises ValueError if invalid)
    parsed = uuid.UUID(minimal_character.id)

    # Assert
    assert str(parsed) == minimal_character.id


def test_default_lists_are_empty(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter traits, skills, and faction_eligibility default to empty lists."""
    assert minimal_character.traits == []
    assert minimal_character.skills == []
    assert minimal_character.faction_eligibility == []


def test_default_player_id_empty(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter.player_id defaults to empty string."""
    assert minimal_character.player_id == ""


def test_default_background_empty(minimal_character: PlayerCharacter) -> None:
    """PlayerCharacter.background defaults to empty string."""
    assert minimal_character.background == ""


def test_full_construction_preserves_all_fields(
    full_character: PlayerCharacter,
) -> None:
    """PlayerCharacter stores all provided field values correctly."""
    assert full_character.id == "char-001"
    assert full_character.name == "Aldric"
    assert full_character.background == "A former scribe who fled the capital."
    assert full_character.traits == ["quietly stubborn", "deeply curious"]
    assert full_character.skills == ["negotiation", "arcane reading"]
    assert full_character.starting_location == "The Lower Gate"
    assert full_character.status == PlayerCharacterStatus.ACTIVE
    assert full_character.player_id == "player-999"
    assert full_character.metadata == {"session_count": 3}


# ── Validation ────────────────────────────────────────────────────────────────


def test_name_cannot_be_empty_string() -> None:
    """PlayerCharacter raises ValidationError when name is an empty string."""
    # Act & Assert
    with pytest.raises(ValidationError):
        PlayerCharacter(name="", world_id="world-1")


def test_name_cannot_exceed_100_chars() -> None:
    """PlayerCharacter raises ValidationError when name exceeds 100 characters."""
    # Arrange
    long_name = "A" * 101

    # Act & Assert
    with pytest.raises(ValidationError):
        PlayerCharacter(name=long_name, world_id="world-1")


def test_name_exactly_100_chars_is_valid() -> None:
    """PlayerCharacter accepts a name of exactly 100 characters."""
    # Arrange
    name_100 = "B" * 100

    # Act
    char = PlayerCharacter(name=name_100, world_id="world-1")

    # Assert
    assert len(char.name) == 100


# ── to_neo4j_properties ───────────────────────────────────────────────────────


def test_to_neo4j_properties_returns_dict(full_character: PlayerCharacter) -> None:
    """to_neo4j_properties() returns a plain dict with expected keys."""
    # Act
    props = full_character.to_neo4j_properties()

    # Assert — is a plain dict
    assert isinstance(props, dict)

    # Assert — has all expected keys
    for key in ("id", "name", "world_id", "background", "traits", "skills",
                 "faction_eligibility", "starting_location", "status", "player_id"):
        assert key in props


def test_to_neo4j_properties_status_is_string(full_character: PlayerCharacter) -> None:
    """to_neo4j_properties() serializes status as a plain string, not enum."""
    # Act
    props = full_character.to_neo4j_properties()

    # Assert
    assert props["status"] == "active"
    assert isinstance(props["status"], str)


def test_to_neo4j_properties_does_not_include_metadata(
    full_character: PlayerCharacter,
) -> None:
    """to_neo4j_properties() excludes the metadata dict (not a Neo4j property)."""
    # Act
    props = full_character.to_neo4j_properties()

    # Assert — metadata is not a Neo4j flat property
    assert "metadata" not in props


# ── from_neo4j_properties round-trip ─────────────────────────────────────────


def test_from_neo4j_properties_round_trip(full_character: PlayerCharacter) -> None:
    """PlayerCharacter round-trips through to_neo4j_properties/from_neo4j_properties."""
    # Act
    props = full_character.to_neo4j_properties()
    restored = PlayerCharacter.from_neo4j_properties(props)

    # Assert key fields survive round-trip
    assert restored.id == full_character.id
    assert restored.name == full_character.name
    assert restored.world_id == full_character.world_id
    assert restored.traits == full_character.traits
    assert restored.skills == full_character.skills
    assert restored.status == full_character.status
    assert restored.player_id == full_character.player_id


def test_from_neo4j_properties_uses_defaults_for_missing_keys() -> None:
    """from_neo4j_properties fills in defaults for optional missing keys."""
    # Arrange — minimal props dict as Neo4j might return
    props = {
        "id": "char-min",
        "name": "Ghost",
        "world_id": "world-min",
        "status": "draft",
    }

    # Act
    char = PlayerCharacter.from_neo4j_properties(props)

    # Assert — optional fields default correctly
    assert char.traits == []
    assert char.skills == []
    assert char.background == ""
    assert char.starting_location == ""


# ── unique ids per instance ───────────────────────────────────────────────────


def test_each_instance_gets_unique_id() -> None:
    """Two PlayerCharacter instances without explicit id receive different UUIDs."""
    # Act
    char_a = PlayerCharacter(name="A", world_id="w1")
    char_b = PlayerCharacter(name="B", world_id="w1")

    # Assert
    assert char_a.id != char_b.id
