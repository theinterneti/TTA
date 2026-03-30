"""
Guide Generator — derives the in-world guide character from the WorldSeed.

This runs once, near the end of BUILDING_CHARACTER, to generate the character
who will transition the narrator from a disembodied voice into an in-world
presence.

Uses rule-based mapping for structural properties (entity type, social position)
and a single LLM call for the evocative elements (name, intro line, speech register).

Uses TTA.dev's RetryPrimitive + FallbackPrimitive for resilience.
"""

from __future__ import annotations

import json
import logging
import re
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
    from tta_dev_primitives import (  # type: ignore[no-redef]
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )

from src.ai_components.llm_factory import get_llm
from src.components.gameplay_loop.models.world_seed import (
    GuideCharacter,
    MagicPresence,
    TechLevel,
)

logger = logging.getLogger(__name__)

# ── Rule tables ───────────────────────────────────────────────────────────────

_ENTITY_TYPE_RULES: dict[tuple[str, str], str] = {
    # (tech_level_group, magic_presence_group): entity_type
    # magic groups: "no_magic" | "low_magic" | "high_magic"
    ("high_tech", "no_magic"): "AI construct",
    ("high_tech", "low_magic"): "augmented human",
    ("high_tech", "high_magic"): "techno-mage",
    ("low_tech", "no_magic"): "wandering scholar",
    ("low_tech", "low_magic"): "spirit-touched elder",
    ("low_tech", "high_magic"): "ancient mage",
    ("mid_tech", "no_magic"): "guild master",
    ("mid_tech", "low_magic"): "hedge wizard",
    ("mid_tech", "high_magic"): "court enchanter",
}

_SOCIAL_POSITION_RULES: dict[str, str] = {
    "magic": "keeper of arcane secrets",
    "technology": "architect of systems",
    "politics": "voice at the council table",
    "belief": "speaker of the old ways",
    "nature": "walker between worlds",
    "lineage": "last of an honoured line",
    "combination": "broker of competing powers",
}

_RELATIONSHIP_RULES: dict[str, str] = {
    "insider": "trusted elder",
    "outsider": "fellow wanderer",
    "ascending": "mentor",
    "descending": "cautionary mirror",
    "observer": "neutral chronicler",
}

_TONE_REGISTER: dict[str, str] = {
    "getting_better": "warm and encouraging",
    "getting_worse": "measured and grave",
    "holding_on": "pragmatic and direct",
    "cyclical": "philosophical and patient",
}


def _tech_group(level: TechLevel | str) -> str:
    _level = level.value if isinstance(level, TechLevel) else level
    HIGH = {"information", "post_scarcity", "electric"}
    LOW = {"stone", "bronze", "iron", "medieval"}
    return (
        "high_tech" if _level in HIGH else ("low_tech" if _level in LOW else "mid_tech")
    )


def _magic_group(presence: MagicPresence | str) -> str:
    _pres = presence.value if isinstance(presence, MagicPresence) else presence
    if _pres == "none":
        return "no_magic"
    if _pres in {"common", "pervasive"}:
        return "high_magic"
    return "low_magic"  # rumoured, rare


def _derive_structural(fields: dict[str, Any]) -> dict[str, str]:
    """Derive entity_type, social_position, relationship_to_player from rules."""
    tech = fields.get("era_tech_level", "medieval")
    magic = fields.get("magic_presence", "rare")
    power = fields.get("power_source", "magic")
    position = fields.get("player_position", "outsider")
    tone = fields.get("tone", "holding_on")

    entity_key = (_tech_group(tech), _magic_group(magic))
    entity_type = _ENTITY_TYPE_RULES.get(entity_key, "mysterious figure")
    social_position = _SOCIAL_POSITION_RULES.get(str(power), "keeper of old secrets")
    relationship = _RELATIONSHIP_RULES.get(str(position), "neutral guide")
    speech_register = _TONE_REGISTER.get(str(tone), "calm and deliberate")

    return {
        "entity_type": entity_type,
        "social_position": social_position,
        "relationship_to_player": relationship,
        "speech_register": speech_register,
    }


# ── LLM call for evocative elements ──────────────────────────────────────────

_GUIDE_SYSTEM = """\
You are crafting an in-world guide character for a text adventure. Given world context, \
generate a name and first spoken line that feel rooted in that specific world.

Output ONLY valid JSON, no markdown fences:
{
  "name": "<single name, one or two words, culturally appropriate>",
  "intro_line": "<their first spoken words to the player — 1-2 sentences, completely in character>"
}

Rules:
- The name should feel like it belongs to this world, not generic fantasy.
- The intro_line must be mysterious, intriguing, never expository.
- The guide already knows the player is important — but does not say so directly.
- No grand proclamations. No "chosen one" language.
- The intro_line should end with a small, concrete question or action that draws the player in.
"""


class _GuideNameCall(WorkflowPrimitive):
    """LLM call to generate guide name + intro line."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, str]:
        structural = input_data["structural"]
        fields = input_data["fields"]

        detail = fields.get("one_specific_detail", "")
        detail_hint = f"\nThe world contains: {detail}" if detail else ""
        char_name = fields.get("character_name", "")
        name_hint = (
            f"\nThe player's character name is: {char_name}" if char_name else ""
        )

        prompt = (
            f"World tone: {fields.get('tone', 'unknown')}\n"
            f"Guide is: {structural['entity_type']}, {structural['social_position']}\n"
            f"Guide's relationship to player: {structural['relationship_to_player']}\n"
            f"Speech register: {structural['speech_register']}"
            f"{detail_hint}{name_hint}\n\n"
            f"JSON output:"
        )

        messages = [
            SystemMessage(content=_GUIDE_SYSTEM),
            HumanMessage(content=prompt),
        ]
        response = await self._llm.ainvoke(messages)
        raw = response.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()

        try:
            result = json.loads(raw)
            return {
                "name": str(result.get("name", _GUIDE_FALLBACK["name"])),
                "intro_line": str(
                    result.get("intro_line", _GUIDE_FALLBACK["intro_line"])
                ),
            }
        except json.JSONDecodeError:
            logger.warning("guide_generator: LLM JSON parse failed: %r", raw[:200])
            return _GUIDE_FALLBACK


_GUIDE_FALLBACK = {
    "name": "Meridian",
    "intro_line": (
        "The dust settles in a pattern I haven't seen in some time. "
        "You'd better come with me — there are things moving that won't wait."
    ),
}


class _GuideFallback(WorkflowPrimitive):
    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, str]:
        return _GUIDE_FALLBACK


# ── Public API ────────────────────────────────────────────────────────────────


async def derive_guide_character(
    seed_fields: dict[str, Any],
    llm: Any | None = None,
    session_id: str = "genesis",
) -> GuideCharacter:
    """
    Derive a GuideCharacter from the accumulated WorldSeed fields.

    Structural properties (entity_type, social_position, relationship) are
    determined by rule tables.  Name and intro_line come from a single LLM call
    wrapped in RetryPrimitive + FallbackPrimitive.

    Args:
        seed_fields: Dict of extracted WorldSeed fields (may include enums as strings).
        llm: Optional pre-built LLM client; created with get_llm() if None.
        session_id: Session ID for WorkflowContext tracing.

    Returns:
        A fully populated GuideCharacter instance.
    """
    _llm = llm or get_llm(temperature=0.8, max_tokens=200)
    structural = _derive_structural(seed_fields)

    name_gen = FallbackPrimitive(
        primary=RetryPrimitive(
            _GuideNameCall(_llm),
            strategy=RetryStrategy(max_retries=2, backoff_base=1.0),
        ),
        fallback=_GuideFallback(),
    )

    context = WorkflowContext(workflow_id=session_id)
    evocative = await name_gen.execute(
        {"structural": structural, "fields": seed_fields},
        context,
    )

    return GuideCharacter(
        name=evocative["name"],
        entity_type=structural["entity_type"],
        social_position=structural["social_position"],
        relationship_to_player=structural["relationship_to_player"],
        speech_register=structural["speech_register"],
        intro_line=evocative["intro_line"],
    )
