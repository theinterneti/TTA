"""
Unit tests for src/components/first_scene — FirstSceneSpec, SceneLocation,
SceneHook, and FirstSceneSpecBuilder.

Issue: #286
"""

from __future__ import annotations

import pytest

from src.components.first_scene import (
    FirstSceneSpec,
    FirstSceneSpecBuilder,
    SceneHook,
    SceneLocation,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def builder() -> FirstSceneSpecBuilder:
    return FirstSceneSpecBuilder()


@pytest.fixture
def sample_seed() -> dict:
    return {
        "tone": "getting_better",
        "power_source": "nature",
        "scale": "village",
        "player_position": "outsider",
        "one_specific_detail": "the whispering grove",
        "world_tagline": "A world where the forest remembers.",
    }


@pytest.fixture
def sample_character() -> dict:
    return {
        "name": "Kira",
        "background": "A healer from the northern forests who lost her home to fire.",
        "traits": ["empathetic", "stubborn"],
        "skills": ["foraging", "community trust"],
    }


# ---------------------------------------------------------------------------
# TestFirstSceneSpecBuilder
# ---------------------------------------------------------------------------


class TestFirstSceneSpecBuilder:
    def test_build_returns_first_scene_spec(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert isinstance(spec, FirstSceneSpec)

    def test_world_tone_carried_through(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.world_tone == "getting_better"

    def test_power_source_carried_through(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.power_source == "nature"

    def test_world_tagline_carried_through(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.world_tagline == "A world where the forest remembers."

    def test_location_name_uses_detail(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        # "whispering grove" → last two words → "Whispering Grove"
        assert "Grove" in spec.location.name or "Whispering" in spec.location.name

    def test_location_atmosphere_matches_tone(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.location.atmosphere == "cautious hope"

    def test_location_time_matches_power_source(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        # nature → dawn
        spec = builder.build(sample_seed, sample_character)
        assert spec.location.time_of_day == "dawn"

    def test_protagonist_intro_contains_name(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert "Kira" in spec.protagonist_intro

    def test_protagonist_intro_includes_background_snippet(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        # background is short enough to appear verbatim
        assert "healer" in spec.protagonist_intro

    def test_hook_reflects_player_position(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        # outsider position → observation hook type
        spec = builder.build(sample_seed, sample_character)
        assert spec.hook.hook_type == "observation"

    def test_hook_type_is_valid(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.hook.hook_type in {"open", "decision", "observation"}

    def test_hook_text_non_empty(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert len(spec.hook.hook_text) > 0

    def test_guide_fields_empty_when_no_guide(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict, sample_character: dict
    ) -> None:
        spec = builder.build(sample_seed, sample_character)
        assert spec.guide_name == ""
        assert spec.guide_intro_line == ""
        assert spec.guide_entity_type == ""

    def test_guide_fields_populated_when_guide_present(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed_with_guide = {
            "tone": "holding_on",
            "power_source": "politics",
            "scale": "city",
            "player_position": "insider",
            "one_specific_detail": "the census bureau",
            "guide": {
                "name": "The Archivist",
                "intro_line": "Long time, friend.",
                "entity_type": "archivist",
            },
        }
        spec = builder.build(seed_with_guide, sample_character)
        assert spec.guide_name == "The Archivist"
        assert spec.guide_intro_line == "Long time, friend."
        assert spec.guide_entity_type == "archivist"

    def test_insider_position_gives_decision_hook(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "holding_on",
            "power_source": "politics",
            "scale": "city",
            "player_position": "insider",
            "one_specific_detail": "the census bureau",
        }
        spec = builder.build(seed, sample_character)
        assert spec.hook.hook_type == "decision"

    def test_ascending_position_gives_decision_hook(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "getting_better",
            "power_source": "magic",
            "scale": "region",
            "player_position": "ascending",
            "one_specific_detail": "the academy spire",
        }
        spec = builder.build(seed, sample_character)
        assert spec.hook.hook_type == "decision"

    def test_observer_position_gives_open_hook(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "cyclical",
            "power_source": "belief",
            "scale": "continent",
            "player_position": "observer",
            "one_specific_detail": "the silent pilgrimage",
        }
        spec = builder.build(seed, sample_character)
        assert spec.hook.hook_type == "open"

    def test_never_raises_on_empty_inputs(
        self, builder: FirstSceneSpecBuilder
    ) -> None:
        spec = builder.build({}, {})
        assert isinstance(spec, FirstSceneSpec)

    def test_never_raises_on_malformed_inputs(
        self, builder: FirstSceneSpecBuilder
    ) -> None:
        spec = builder.build(
            {"tone": 12345, "power_source": None, "scale": [], "guide": "not-a-dict"},
            {"name": object(), "background": 999},
        )
        assert isinstance(spec, FirstSceneSpec)

    def test_long_background_is_truncated(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict
    ) -> None:
        long_bg = "x" * 200
        char = {"name": "Ren", "background": long_bg}
        spec = builder.build(sample_seed, char)
        assert len(spec.protagonist_intro) < len(long_bg) + 20

    def test_missing_background_uses_arrives_fallback(
        self, builder: FirstSceneSpecBuilder, sample_seed: dict
    ) -> None:
        char = {"name": "Solo"}
        spec = builder.build(sample_seed, char)
        assert "Solo" in spec.protagonist_intro
        assert "arrives" in spec.protagonist_intro

    def test_unknown_scale_falls_back_to_village_prefix(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "holding_on",
            "power_source": "nature",
            "scale": "UNKNOWN_SCALE",
            "player_position": "observer",
            "one_specific_detail": "the old mill",
        }
        spec = builder.build(seed, sample_character)
        # Should not raise and should produce a valid spec
        assert isinstance(spec, FirstSceneSpec)
        assert "Crossroads" in spec.location.name or "Edge" in spec.location.name

    def test_power_source_lineage_gives_night(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "getting_worse",
            "power_source": "lineage",
            "scale": "city",
            "player_position": "descending",
            "one_specific_detail": "the bloodline registry",
        }
        spec = builder.build(seed, sample_character)
        assert spec.location.time_of_day == "night"

    def test_getting_worse_tone_gives_quiet_dread(
        self, builder: FirstSceneSpecBuilder, sample_character: dict
    ) -> None:
        seed = {
            "tone": "getting_worse",
            "power_source": "magic",
            "scale": "city",
            "player_position": "outsider",
            "one_specific_detail": "the crumbling tower",
        }
        spec = builder.build(seed, sample_character)
        assert spec.location.atmosphere == "quiet dread"


# ---------------------------------------------------------------------------
# TestFirstSceneSpecNgaPrompt
# ---------------------------------------------------------------------------


class TestFirstSceneSpecNgaPrompt:
    def _make_spec(self, **overrides) -> FirstSceneSpec:
        defaults: dict = {
            "world_tone": "getting_better",
            "power_source": "nature",
            "world_tagline": "A forest that remembers.",
            "location": SceneLocation(
                name="The Grove Crossroads",
                description="A meeting point under ancient trees.",
                atmosphere="cautious hope",
                time_of_day="dawn",
            ),
            "protagonist_intro": "Kira: a healer in search of purpose.",
            "hook": SceneHook(
                hook_text="What draws your eye?", hook_type="observation"
            ),
            "guide_name": "The Archivist",
            "guide_intro_line": "Long time, friend.",
            "guide_entity_type": "archivist",
        }
        defaults.update(overrides)
        return FirstSceneSpec(**defaults)

    def test_to_nga_prompt_contains_tone(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "getting_better" in prompt

    def test_to_nga_prompt_contains_power_source(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "nature" in prompt

    def test_to_nga_prompt_contains_location(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "The Grove Crossroads" in prompt

    def test_to_nga_prompt_contains_hook(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "What draws your eye?" in prompt

    def test_to_nga_prompt_contains_guide_when_present(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "The Archivist" in prompt
        assert "Long time, friend." in prompt

    def test_to_nga_prompt_omits_guide_when_empty(self) -> None:
        spec = self._make_spec(guide_name="", guide_intro_line="", guide_entity_type="")
        prompt = spec.to_nga_prompt()
        assert "Guide" not in prompt

    def test_to_nga_prompt_contains_tagline(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "A forest that remembers." in prompt

    def test_to_nga_prompt_omits_tagline_when_empty(self) -> None:
        spec = self._make_spec(world_tagline="")
        prompt = spec.to_nga_prompt()
        assert "World:" not in prompt

    def test_to_nga_prompt_contains_word_count(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "300" in prompt

    def test_to_nga_prompt_contains_pov(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert "second_person" in prompt

    def test_to_nga_prompt_is_string(self) -> None:
        prompt = self._make_spec().to_nga_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0


# ---------------------------------------------------------------------------
# TestSceneLocation
# ---------------------------------------------------------------------------


class TestSceneLocation:
    def test_all_required_fields_present(self) -> None:
        loc = SceneLocation(
            name="The Crossing",
            description="A tense border between two lands.",
            atmosphere="tense stillness",
        )
        assert loc.name == "The Crossing"
        assert loc.description == "A tense border between two lands."
        assert loc.atmosphere == "tense stillness"

    def test_default_time_of_day(self) -> None:
        loc = SceneLocation(
            name="Anywhere",
            description="A place.",
            atmosphere="quiet",
        )
        assert loc.time_of_day == "dawn"

    def test_custom_time_of_day(self) -> None:
        loc = SceneLocation(
            name="Night Market",
            description="Lanterns sway.",
            atmosphere="electric",
            time_of_day="night",
        )
        assert loc.time_of_day == "night"


# ---------------------------------------------------------------------------
# TestSceneHook
# ---------------------------------------------------------------------------


class TestSceneHook:
    def test_default_hook_type(self) -> None:
        hook = SceneHook(hook_text="What do you do?")
        assert hook.hook_type == "open"

    def test_custom_hook_type_decision(self) -> None:
        hook = SceneHook(hook_text="Left or right?", hook_type="decision")
        assert hook.hook_type == "decision"

    def test_custom_hook_type_observation(self) -> None:
        hook = SceneHook(hook_text="You notice something.", hook_type="observation")
        assert hook.hook_type == "observation"

    def test_hook_text_stored_verbatim(self) -> None:
        text = "Is there anything left worth reaching for?"
        hook = SceneHook(hook_text=text)
        assert hook.hook_text == text
