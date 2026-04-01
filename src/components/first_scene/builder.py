"""
# Logseq: [[TTA/Components/First_scene/Builder]]
FirstSceneSpecBuilder — assembles a FirstSceneSpec from WorldSeed + PlayerCharacter dict.

Rule-based assembly. No LLM — deterministic from world parameters.

Issue: #286
"""

from __future__ import annotations

import logging
from typing import Any

from .models import FirstSceneSpec, SceneHook, SceneLocation

logger = logging.getLogger(__name__)


# Location name templates by world scale
_SCALE_LOCATION_PREFIXES: dict[str, list[str]] = {
    "village": ["The {detail} Crossroads", "The Edge of {detail}", "{detail} Square"],
    "city": ["The {detail} District", "Lower {detail}", "{detail} Gate"],
    "region": ["The {detail} Road", "{detail} Borderlands", "The {detail} Way"],
    "continent": [
        "The {detail} Frontier",
        "{detail} Passage",
        "The Far {detail}",
    ],
}

# Atmosphere by world tone
_TONE_ATMOSPHERE: dict[str, str] = {
    "getting_better": "cautious hope",
    "getting_worse": "quiet dread",
    "holding_on": "tense stillness",
    "cyclical": "familiar uncertainty",
}

# Time of day by power source
_POWER_TIME: dict[str, str] = {
    "magic": "dusk",
    "technology": "midday",
    "politics": "dawn",
    "belief": "dawn",
    "nature": "dawn",
    "lineage": "night",
    "combination": "dusk",
}

# Hook templates by player position
_POSITION_HOOKS: dict[str, tuple[str, str]] = {
    "insider": (
        "Something is wrong with a system you know intimately. What do you do first?",
        "decision",
    ),
    "outsider": (
        "You don't belong here — but something in this place recognises you."
        " What draws your eye?",
        "observation",
    ),
    "ascending": (
        "You've been waiting for this moment. What's the first move?",
        "decision",
    ),
    "descending": (
        "You know what you've lost. Is there anything left worth reaching for?",
        "open",
    ),
    "observer": (
        "You've seen enough to ask the right question. What is it?",
        "open",
    ),
}


class FirstSceneSpecBuilder:
    """Builds a FirstSceneSpec from WorldSeed dict + PlayerCharacter dict."""

    def build(
        self,
        world_seed: dict[str, Any],
        player_character: dict[str, Any],
    ) -> FirstSceneSpec:
        """
        Assemble a FirstSceneSpec rule-based from world + character properties.

        Args:
            world_seed: WorldSeed model_dump() dict or compatible dict.
            player_character: PlayerCharacter.character_sheet dict or compatible.

        Returns:
            FirstSceneSpec ready for NGA prompt injection.
        """
        try:
            return self._build_internal(world_seed, player_character)
        except Exception as exc:
            logger.error("FirstSceneSpecBuilder.build failed: %s", exc)
            return self._fallback_spec(world_seed, player_character)

    def _build_internal(
        self,
        world_seed: dict[str, Any],
        player_character: dict[str, Any],
    ) -> FirstSceneSpec:
        tone = str(world_seed.get("tone", "holding_on"))
        power = str(world_seed.get("power_source", "nature"))
        scale = str(world_seed.get("scale", world_seed.get("world_scale", "village")))
        position = str(world_seed.get("player_position", "observer"))
        detail = str(world_seed.get("one_specific_detail", "the crossroads"))
        tagline = str(world_seed.get("world_tagline", ""))

        # Location
        prefixes = _SCALE_LOCATION_PREFIXES.get(
            scale, _SCALE_LOCATION_PREFIXES["village"]
        )
        loc_name = prefixes[0].format(detail=_extract_noun(detail))
        atmosphere = _TONE_ATMOSPHERE.get(tone, "uncertain")
        time_of_day = _POWER_TIME.get(power, "dawn")
        location = SceneLocation(
            name=loc_name,
            description=(
                f"A place shaped by {power}, where {detail} defines what's possible."
            ),
            atmosphere=atmosphere,
            time_of_day=time_of_day,
        )

        # Protagonist intro
        char_name = player_character.get("name", "you")
        char_background = str(player_character.get("background", ""))
        bg_snippet = (
            char_background[:80].rstrip() + "..."
            if len(char_background) > 80
            else char_background
        )
        protagonist_intro = (
            f"{char_name}: {bg_snippet}" if bg_snippet else f"{char_name} arrives."
        )

        # Hook
        hook_text, hook_type = _POSITION_HOOKS.get(
            position, ("What happens next is yours to decide.", "open")
        )
        hook = SceneHook(hook_text=hook_text, hook_type=hook_type)

        # Guide — normalise to plain dict regardless of source type
        raw_guide = world_seed.get("guide") or {}
        guide: dict[str, Any]
        if hasattr(raw_guide, "model_dump"):
            guide = raw_guide.model_dump()  # type: ignore[union-attr]
        elif hasattr(raw_guide, "__dict__"):
            guide = raw_guide.__dict__
        elif isinstance(raw_guide, dict):
            guide = raw_guide
        else:
            guide = {}

        return FirstSceneSpec(
            world_tone=tone,
            power_source=power,
            world_tagline=tagline,
            location=location,
            protagonist_intro=protagonist_intro,
            hook=hook,
            guide_name=str(guide.get("name", "")),
            guide_intro_line=str(guide.get("intro_line", "")),
            guide_entity_type=str(guide.get("entity_type", "")),
        )

    def _fallback_spec(
        self,
        world_seed: dict[str, Any],
        player_character: dict[str, Any],
    ) -> FirstSceneSpec:
        char_name = "A traveller"
        with __import__("contextlib").suppress(Exception):
            char_name = (
                str(player_character.get("name", "A traveller")) or "A traveller"
            )
        return FirstSceneSpec(
            world_tone="holding_on",
            power_source="nature",
            location=SceneLocation(
                name="The Threshold",
                description="A place between what was and what might be.",
                atmosphere="quiet expectation",
                time_of_day="dawn",
            ),
            protagonist_intro=f"{char_name} stands at the edge.",
            hook=SceneHook(hook_text="What do you do?", hook_type="open"),
        )


def _extract_noun(detail: str) -> str:
    """Extract a 1-2 word noun from a detail string for use in location names."""
    words = detail.strip().split()
    noun_words = [w.capitalize() for w in words[-2:] if len(w) > 2]
    return " ".join(noun_words) if noun_words else "Ancient"
