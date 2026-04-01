"""
Unit tests for FirstSceneSpec models and FirstSceneSpecBuilder.

Covers:
- SceneLocation, SceneHook, FirstSceneSpec model construction and validation
- FirstSceneSpec.to_nga_prompt() renders correct fields
- FirstSceneSpecBuilder.build() selects correct location prefix by world scale
- FirstSceneSpecBuilder.build() selects correct atmosphere by world tone
- FirstSceneSpecBuilder.build() selects correct time_of_day by power_source
- FirstSceneSpecBuilder.build() selects correct hook by player_position
- FirstSceneSpecBuilder.build() includes guide fields when guide dict present
- FirstSceneSpecBuilder.build() gracefully falls back on bad input
- FirstSceneSpec rejects target_word_count ≤ 0 (Pydantic validation)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.components.first_scene.builder import FirstSceneSpecBuilder
from src.components.first_scene.models import FirstSceneSpec, SceneHook, SceneLocation

pytestmark = pytest.mark.unit


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def builder() -> FirstSceneSpecBuilder:
    """Return a fresh FirstSceneSpecBuilder."""
    return FirstSceneSpecBuilder()


@pytest.fixture()
def minimal_world_seed() -> dict:
    """Minimal WorldSeed-compatible dict for builder tests."""
    return {
        "tone": "holding_on",
        "power_source": "nature",
        "scale": "village",
        "player_position": "observer",
        "one_specific_detail": "the old mill",
        "world_tagline": "A world holding its breath.",
    }


@pytest.fixture()
def minimal_player_character() -> dict:
    """Minimal PlayerCharacter-compatible dict for builder tests."""
    return {
        "name": "Seren",
        "background": "She came from the mountains.",
        "traits": ["quiet", "observant"],
    }


# ── SceneLocation model ───────────────────────────────────────────────────────


def test_scene_location_requires_name_description_atmosphere() -> None:
    """SceneLocation requires name, description, and atmosphere fields."""
    # Arrange & Act
    location = SceneLocation(
        name="The Crossroads",
        description="Where two old roads meet under a lone oak.",
        atmosphere="quiet tension",
    )

    # Assert
    assert location.name == "The Crossroads"
    assert location.time_of_day == "dawn"  # default


def test_scene_location_custom_time_of_day() -> None:
    """SceneLocation accepts a custom time_of_day value."""
    # Arrange & Act
    location = SceneLocation(
        name="The Gate",
        description="Ancient iron doors half-open.",
        atmosphere="cold dread",
        time_of_day="midnight",
    )

    # Assert
    assert location.time_of_day == "midnight"


# ── SceneHook model ───────────────────────────────────────────────────────────


def test_scene_hook_defaults_to_open_type() -> None:
    """SceneHook hook_type defaults to 'open'."""
    # Arrange & Act
    hook = SceneHook(hook_text="What will you do?")

    # Assert
    assert hook.hook_type == "open"


def test_scene_hook_decision_type() -> None:
    """SceneHook accepts 'decision' hook_type."""
    # Arrange & Act
    hook = SceneHook(hook_text="Do you go left or right?", hook_type="decision")

    # Assert
    assert hook.hook_type == "decision"


# ── FirstSceneSpec model ──────────────────────────────────────────────────────


def test_first_scene_spec_basic_construction() -> None:
    """FirstSceneSpec constructs with required fields and sensible defaults."""
    # Arrange
    location = SceneLocation(
        name="The Square", description="Open cobblestones.", atmosphere="expectant"
    )
    hook = SceneHook(hook_text="What draws your eye?")

    # Act
    spec = FirstSceneSpec(
        world_tone="getting_better",
        power_source="magic",
        location=location,
        protagonist_intro="A scholar on the run.",
        hook=hook,
    )

    # Assert
    assert spec.target_word_count == 300  # default
    assert spec.pov == "second_person"  # default
    assert spec.guide_name == ""  # default


def test_first_scene_spec_rejects_nonpositive_word_count() -> None:
    """FirstSceneSpec raises ValidationError when target_word_count ≤ 0."""
    # Arrange
    location = SceneLocation(name="X", description="Y", atmosphere="Z")
    hook = SceneHook(hook_text="Act?")

    # Act & Assert
    with pytest.raises(ValidationError):
        FirstSceneSpec(
            world_tone="holding_on",
            power_source="nature",
            location=location,
            protagonist_intro="Hero",
            hook=hook,
            target_word_count=0,
        )


def test_to_nga_prompt_contains_key_fields() -> None:
    """FirstSceneSpec.to_nga_prompt() renders world tone, location, and hook."""
    # Arrange
    location = SceneLocation(
        name="The Mill",
        description="A crumbling watermill on the edge of town.",
        atmosphere="quiet dread",
        time_of_day="dusk",
    )
    hook = SceneHook(hook_text="Something moves in the shadows.")
    spec = FirstSceneSpec(
        world_tone="getting_worse",
        power_source="politics",
        world_tagline="Power is the only currency.",
        location=location,
        protagonist_intro="A former councillor's aide.",
        hook=hook,
        guide_name="The Watcher",
        guide_entity_type="spirit",
        guide_intro_line="I've been waiting for you.",
    )

    # Act
    prompt = spec.to_nga_prompt()

    # Assert
    assert "getting_worse" in prompt
    assert "The Mill" in prompt
    assert "Something moves in the shadows." in prompt
    assert "The Watcher" in prompt
    assert "Power is the only currency." in prompt


def test_to_nga_prompt_omits_guide_when_absent() -> None:
    """FirstSceneSpec.to_nga_prompt() omits guide section when guide_name is empty."""
    # Arrange
    location = SceneLocation(name="X", description="Y", atmosphere="Z")
    hook = SceneHook(hook_text="Now what?")
    spec = FirstSceneSpec(
        world_tone="holding_on",
        power_source="nature",
        location=location,
        protagonist_intro="A wanderer.",
        hook=hook,
    )

    # Act
    prompt = spec.to_nga_prompt()

    # Assert
    assert "Guide" not in prompt


# ── FirstSceneSpecBuilder ─────────────────────────────────────────────────────


def test_builder_returns_first_scene_spec(
    builder: FirstSceneSpecBuilder,
    minimal_world_seed: dict,
    minimal_player_character: dict,
) -> None:
    """FirstSceneSpecBuilder.build() returns a valid FirstSceneSpec."""
    # Act
    spec = builder.build(minimal_world_seed, minimal_player_character)

    # Assert
    assert isinstance(spec, FirstSceneSpec)
    assert spec.world_tone == "holding_on"
    assert spec.power_source == "nature"


def test_builder_atmosphere_by_tone(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder selects atmosphere from world tone mapping."""
    # Arrange
    seed = {
        "tone": "getting_better",
        "power_source": "nature",
        "scale": "village",
        "player_position": "observer",
        "one_specific_detail": "the fountain",
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.location.atmosphere == "cautious hope"


def test_builder_time_of_day_by_power_source(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder selects time_of_day from power_source mapping."""
    # Arrange
    seed = {
        "tone": "holding_on",
        "power_source": "magic",
        "scale": "city",
        "player_position": "observer",
        "one_specific_detail": "the tower",
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.location.time_of_day == "dusk"


def test_builder_hook_by_player_position_insider(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder selects 'decision' hook for insider player position."""
    # Arrange
    seed = {
        "tone": "holding_on",
        "power_source": "politics",
        "scale": "city",
        "player_position": "insider",
        "one_specific_detail": "the council chamber",
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.hook.hook_type == "decision"


def test_builder_hook_by_player_position_outsider(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder selects 'observation' hook for outsider player position."""
    # Arrange
    seed = {
        "tone": "getting_worse",
        "power_source": "belief",
        "scale": "village",
        "player_position": "outsider",
        "one_specific_detail": "the shrine gate",
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.hook.hook_type == "observation"


def test_builder_includes_guide_fields(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder injects guide name and intro from guide sub-dict in world_seed."""
    # Arrange
    seed = {
        "tone": "cyclical",
        "power_source": "lineage",
        "scale": "region",
        "player_position": "descending",
        "one_specific_detail": "the old bridge",
        "guide": {
            "name": "The Keeper",
            "entity_type": "ancestor spirit",
            "intro_line": "You carry more than you know.",
        },
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.guide_name == "The Keeper"
    assert spec.guide_entity_type == "ancestor spirit"
    assert spec.guide_intro_line == "You carry more than you know."


def test_builder_fallback_on_missing_required_fields(
    builder: FirstSceneSpecBuilder,
) -> None:
    """Builder returns a safe fallback FirstSceneSpec when input is missing keys."""
    # Arrange — completely empty dicts
    world_seed: dict = {}
    player_character: dict = {}

    # Act — should not raise
    spec = builder.build(world_seed, player_character)

    # Assert — fallback spec is valid
    assert isinstance(spec, FirstSceneSpec)
    assert spec.location.name  # non-empty fallback location name
    assert spec.hook.hook_text  # non-empty fallback hook


def test_builder_world_tagline_propagated(
    builder: FirstSceneSpecBuilder,
    minimal_player_character: dict,
) -> None:
    """Builder passes world_tagline through to the FirstSceneSpec."""
    # Arrange
    seed = {
        "tone": "holding_on",
        "power_source": "technology",
        "scale": "city",
        "player_position": "ascending",
        "one_specific_detail": "the foundry",
        "world_tagline": "Progress at any price.",
    }

    # Act
    spec = builder.build(seed, minimal_player_character)

    # Assert
    assert spec.world_tagline == "Progress at any price."
