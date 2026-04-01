"""
# Logseq: [[TTA/Components/Player_character/Service]]
PlayerCharacterService — derives a PlayerCharacter from a WorldSeed.

Issue: #284
"""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

try:
    from ttadev.primitives import (
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )
except ImportError:
    # ttadev not available — minimal stubs for type checking
    class FallbackPrimitive:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None: ...
        async def execute(self, data: object, ctx: object) -> object: ...
    class RetryPrimitive:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None: ...
        async def execute(self, data: object, ctx: object) -> object: ...
    class RetryStrategy:  # type: ignore[no-redef]
        def __init__(self, **kwargs: object) -> None: ...
    class WorkflowContext:  # type: ignore[no-redef]
        def __init__(self, **kwargs: object) -> None: ...
    class WorkflowPrimitive:  # type: ignore[no-redef]
        async def execute(self, data: object, ctx: object) -> object: ...

from src.ai_components.llm_factory import get_llm

from .models import PlayerCharacter, PlayerCharacterStatus

logger = logging.getLogger(__name__)


# ── Prompt ──────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are creating a player character for a therapeutic text adventure world.
Given the world description and player preferences, return a JSON object:

{
  "name": "<character name fitting the world>",
  "background": "<2-3 sentence backstory paragraph>",
  "traits": ["<trait1>", "<trait2>", "<trait3>"],
  "starting_location": "<a location name fitting the world>"
}

Rules:
- Name should fit the world's tone and culture
- Background should reference the world's power source and the player's stated position
- Traits should be emotionally grounded and 1-3 words each (e.g. "quietly stubborn", "deeply curious")
- Return valid JSON only — no extra text
"""

_FALLBACK_CHARACTER_SUFFIX = " (Traveller)"


# ── Skill derivation ──────────────────────────────────────────────────────────


def _derive_skills(world_seed_dict: dict[str, Any]) -> list[str]:
    """
    Rule-based skill derivation from world properties.

    Derives starting skills based on world's power_source and world_scale.
    No LLM needed — deterministic from world parameters.
    """
    power_source = str(world_seed_dict.get("power_source", "")).lower()
    world_scale = str(world_seed_dict.get("world_scale", "")).lower()
    # WorldSeed uses 'scale' not 'world_scale' — check both
    if not world_scale:
        world_scale = str(world_seed_dict.get("scale", "village")).lower()

    skill_map: dict[str, list[str]] = {
        "magic": ["arcane reading", "ritual preparation", "magical intuition"],
        "technology": [
            "mechanical repair",
            "engineering basics",
            "resource assessment",
        ],
        "politics": ["negotiation", "social reading", "faction knowledge"],
        "belief": ["spiritual practice", "community ritual", "symbol interpretation"],
        "nature": ["foraging", "weather reading", "animal handling"],
        "lineage": ["genealogy knowledge", "inheritance protocols", "heraldry"],
        "combination": [
            "pattern recognition",
            "adaptive thinking",
            "cross-domain knowledge",
        ],
    }

    base_skills = skill_map.get(power_source, ["observation", "adaptability"])

    scale_bonus: dict[str, str] = {
        "village": "community trust",
        "city": "urban navigation",
        "region": "geography",
        "continent": "languages",
    }
    bonus = scale_bonus.get(world_scale, "survival basics")

    return base_skills[:2] + [bonus]


def _derive_faction_eligibility(
    world_seed_dict: dict[str, Any], player_position: str
) -> list[str]:
    """Rule-based faction eligibility from player position."""
    position_map: dict[str, list[str]] = {
        "insider": ["ruling faction", "merchant guilds", "civic institutions"],
        "outsider": [
            "resistance movements",
            "wanderer collectives",
            "underground networks",
        ],
        "ascending": [
            "newly established guilds",
            "reform movements",
            "meritocratic institutions",
        ],
        "descending": ["exile communities", "fallen nobility", "redemption seekers"],
        "observer": ["scholars", "neutral arbiters", "historical societies"],
    }
    return position_map.get(player_position.lower(), ["independent"])


# ── Primitives ─────────────────────────────────────────────────────────────────


class _CharacterLLMCall(WorkflowPrimitive):  # type: ignore[misc]
    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        world_desc = input_data["world_desc"]
        player_prefs = input_data.get("player_prefs", {})

        user_msg = (
            f"World: {world_desc}\nPlayer preferences: {json.dumps(player_prefs)}"
        )
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ]
        response = await self._llm.ainvoke(messages)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)  # type: ignore[no-any-return]


class _CharacterFallback(WorkflowPrimitive):  # type: ignore[misc]
    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        return {
            "name": "The Wanderer",
            "background": (
                "A traveller from distant lands, carrying little but a sharp eye"
                " and an open mind."
            ),
            "traits": ["observant", "adaptable", "quietly determined"],
            "starting_location": "the road's edge",
        }


# ── Service ──────────────────────────────────────────────────────────────────


class PlayerCharacterService:
    """Creates PlayerCharacter instances from WorldSeed + player preferences."""

    def __init__(self, llm: Any | None = None) -> None:
        _llm = llm or get_llm(temperature=0.7, max_tokens=600)
        self._primitive = FallbackPrimitive(
            primary=RetryPrimitive(
                _CharacterLLMCall(_llm),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.0),  # type: ignore[arg-type]
            ),
            fallback=_CharacterFallback(),
        )

    async def create_from_seed(
        self,
        world_seed: Any,
        player_prefs: dict[str, Any] | None = None,
        player_id: str = "",
    ) -> PlayerCharacter:
        """
        Derive a PlayerCharacter from a WorldSeed.

        Args:
            world_seed: WorldSeed model instance or dict of seed properties.
            player_prefs: Optional dict with player preference hints
                          (e.g. {'preferred_name': 'Kira', 'background_hint': 'healer'})
            player_id: Auth player ID to attach to character.

        Returns:
            Validated PlayerCharacter instance.
        """
        prefs = player_prefs or {}

        if hasattr(world_seed, "model_dump"):
            seed_dict = world_seed.model_dump()
            world_id = str(world_seed.id) if hasattr(world_seed, "id") else ""
            if not world_id and "session_id" in seed_dict:
                world_id = str(seed_dict["session_id"])
        else:
            seed_dict = dict(world_seed)
            world_id = str(seed_dict.get("id", ""))

        world_desc = _build_world_description(seed_dict, prefs)

        ctx = WorkflowContext(workflow_id=f"char-creation-{world_id}")
        llm_result = await self._primitive.execute(  # type: ignore[arg-type]
            {"world_desc": world_desc, "player_prefs": prefs}, ctx  # type: ignore[arg-type]
        )

        skills = _derive_skills(seed_dict)
        player_position = str(seed_dict.get("player_position", "observer"))
        faction_eligibility = _derive_faction_eligibility(seed_dict, player_position)

        character = PlayerCharacter(
            name=llm_result.get("name", "The Wanderer"),
            world_id=world_id,
            background=llm_result.get("background", ""),
            traits=llm_result.get("traits", []),
            skills=skills,
            faction_eligibility=faction_eligibility,
            starting_location=llm_result.get("starting_location", ""),
            player_id=player_id,
            status=PlayerCharacterStatus.DRAFT,
        )

        logger.info(
            "player_character: created name=%r world_id=%s player_id=%s",
            character.name,
            world_id,
            player_id,
        )
        return character


def _build_world_description(seed_dict: dict[str, Any], prefs: dict[str, Any]) -> str:
    """Compact world description string for the LLM prompt."""
    parts = []

    if tone := seed_dict.get("tone"):
        parts.append(f"Tone: {tone}")
    if power := seed_dict.get("power_source"):
        parts.append(f"Power source: {power}")
    # WorldSeed uses 'scale'; some dicts may use 'world_scale'
    scale = seed_dict.get("world_scale") or seed_dict.get("scale")
    if scale:
        parts.append(f"Scale: {scale}")
    if position := seed_dict.get("player_position"):
        parts.append(f"Player position: {position}")
    if tagline := seed_dict.get("world_tagline"):
        parts.append(f"World: {tagline}")

    if hint := prefs.get("background_hint"):
        parts.append(f"Player hint: {hint}")
    if pref_name := prefs.get("preferred_name"):
        parts.append(f"Preferred name: {pref_name}")

    return "; ".join(parts) if parts else "A mysterious world of untold stories."
