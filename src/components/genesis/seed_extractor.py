"""
Seed Extractor — parses player input and extracts WorldSeed fields.

Runs a lightweight structured LLM call alongside the main narrator response to
identify which WorldSeed fields the player just established.  Does NOT ask the
player questions; it only extracts what was already given.

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

from .session_state import Act

logger = logging.getLogger(__name__)

# ── Enum value sets (for parsing and validation) ──────────────────────────────

_TONES = {"getting_better", "getting_worse", "holding_on", "cyclical"}
_POWER_SOURCES = {
    "magic",
    "technology",
    "politics",
    "belief",
    "nature",
    "lineage",
    "combination",
}
_POSITIONS = {"insider", "outsider", "ascending", "descending", "observer"}
_SCALES = {"village", "city", "region", "continent", "world", "cosmic"}
_TECH_LEVELS = {
    "stone",
    "bronze",
    "iron",
    "medieval",
    "renaissance",
    "industrial",
    "electric",
    "information",
    "post_scarcity",
}
_MAGIC_PRESENCES = {"none", "rumoured", "rare", "common", "pervasive"}
_MOTIVATIONS = {
    "curiosity",
    "belonging",
    "justice",
    "survival",
    "discovery",
    "freedom",
    "redemption",
    "power",
    "love",
    "duty",
    "revenge",
    "creation",
}

_EXTRACTION_SYSTEM = """\
You extract structured world-building data from player messages in a text adventure setup conversation.

Your job: identify which world/character fields the player just established.

EXTRACTABLE FIELDS:
- tone: one of [getting_better, getting_worse, holding_on, cyclical]
- power_source: one of [magic, technology, politics, belief, nature, lineage, combination]
- player_position: one of [insider, outsider, ascending, descending, observer]
- one_specific_detail: any concrete thing that exists in this world (string)
- scale: one of [village, city, region, continent, world, cosmic]
- era_tech_level: one of [stone, bronze, iron, medieval, renaissance, industrial, electric, information, post_scarcity]
- magic_presence: one of [none, rumoured, rare, common, pervasive]
- character_name: string (name the player chose for their character)
- character_motivation: one of [curiosity, belonging, justice, survival, discovery, freedom, redemption, power, love, duty, revenge, creation]
- character_trait: string (what they're known for)
- character_background: string (their history)
- character_secret: string (the unresolved question)

RULES:
- Only extract what the player clearly stated or unambiguously implied.
- Cultural references: "Han Solo in cyberpunk" → power_source=technology, player_position=outsider, era_tech_level=information, tone=getting_worse
- Dystopian/declining worlds → tone=getting_worse. Hopeful/rebuilding → tone=getting_better.
- Fantasy worlds with visible magic → magic_presence=common or pervasive, power_source=magic
- Modern realistic settings → era_tech_level=information, magic_presence=none
- "I want to be a rogue/thief" → character_trait="skilled thief, moves in shadow"
- Vague or evasive answers yield nothing extractable. Output {}.
- Output ONLY valid JSON with the fields found. No explanation. No markdown fences.
"""


class _ExtractionCall(WorkflowPrimitive):
    """Single LLM extraction call — wrapped by RetryPrimitive."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, Any]:
        player_input: str = input_data["player_input"]
        current_fields: dict = input_data.get("current_fields", {})

        context_note = ""
        if current_fields:
            established = ", ".join(
                f"{k}={v}" for k, v in current_fields.items() if v is not None
            )
            context_note = (
                f"\nAlready established: {established}\nDo NOT re-extract these."
            )

        messages = [
            SystemMessage(content=_EXTRACTION_SYSTEM + context_note),
            HumanMessage(content=f'Player said: "{player_input}"\n\nJSON output:'),
        ]
        response = await self._llm.ainvoke(messages)
        raw = response.content.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()

        try:
            return json.loads(raw) if raw and raw != "{}" else {}
        except json.JSONDecodeError:
            logger.warning("seed_extractor: could not parse JSON: %r", raw[:200])
            return {}


class _ExtractionFallback(WorkflowPrimitive):
    """Returns empty dict — extraction is best-effort, never blocking."""

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, Any]:
        return {}


class _SurpriseCall(WorkflowPrimitive):
    """Generates a complete WorldSeed for 'surprise me' requests."""

    _SURPRISE_SYSTEM = """\
Generate a complete, surprising WorldSeed for a text adventure. Be creative and specific.

Output ONLY valid JSON with these exact fields:
{
  "tone": "<one of: getting_better|getting_worse|holding_on|cyclical>",
  "power_source": "<one of: magic|technology|politics|belief|nature|lineage|combination>",
  "player_position": "<one of: insider|outsider|ascending|descending|observer>",
  "one_specific_detail": "<a concrete, specific, evocative thing that exists in this world>",
  "scale": "<one of: village|city|region|continent|world|cosmic>",
  "era_tech_level": "<one of: stone|bronze|iron|medieval|renaissance|industrial|electric|information|post_scarcity>",
  "magic_presence": "<one of: none|rumoured|rare|common|pervasive>"
}

Make it feel like it belongs to a real, lived-in world — not a genre template.
No markdown fences. Only JSON.
"""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, Any]:
        messages = [
            SystemMessage(content=self._SURPRISE_SYSTEM),
            HumanMessage(content="Generate a surprising WorldSeed now."),
        ]
        response = await self._llm.ainvoke(messages)
        raw = response.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("seed_extractor: surprise JSON parse failed: %r", raw[:200])
            return _SURPRISE_FALLBACK


_SURPRISE_FALLBACK: dict[str, Any] = {
    "tone": "getting_worse",
    "power_source": "magic",
    "player_position": "outsider",
    "one_specific_detail": "A library that burns every book it receives, yet the ash tells fortunes",
    "scale": "city",
    "era_tech_level": "renaissance",
    "magic_presence": "rare",
}

_ENUM_VALIDATORS: dict[str, set[str]] = {
    "tone": _TONES,
    "power_source": _POWER_SOURCES,
    "player_position": _POSITIONS,
    "scale": _SCALES,
    "era_tech_level": _TECH_LEVELS,
    "magic_presence": _MAGIC_PRESENCES,
    "character_motivation": _MOTIVATIONS,
}


def _validate_fields(raw: dict[str, Any]) -> dict[str, Any]:
    """Drop any fields with invalid enum values; pass strings through."""
    clean: dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _ENUM_VALIDATORS:
            if isinstance(value, str) and value.strip():
                clean[key] = value.strip()
        elif isinstance(value, str) and value.lower() in _ENUM_VALIDATORS[key]:
            clean[key] = value.lower()
        else:
            logger.debug("seed_extractor: dropped invalid value %s=%r", key, value)
    return clean


# ── Public API ────────────────────────────────────────────────────────────────


class SeedExtractor:
    """
    Extracts WorldSeed fields from player input using a lightweight LLM call.

    Wrapped in RetryPrimitive + FallbackPrimitive from tta_dev_primitives so
    extraction failures never block the main narrator response.
    """

    def __init__(self, llm: Any | None = None) -> None:
        _llm = llm or get_llm(temperature=0.1, max_tokens=300)
        self._extractor = FallbackPrimitive(
            primary=RetryPrimitive(
                _ExtractionCall(_llm),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.0),
            ),
            fallback=_ExtractionFallback(),
        )
        self._surprise = FallbackPrimitive(
            primary=RetryPrimitive(
                _SurpriseCall(_llm),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.0),
            ),
            fallback=_ExtractionFallback(),
        )

    async def extract(
        self,
        player_input: str,
        current_fields: dict[str, Any],
        act: Act,
        session_id: str = "genesis",
    ) -> dict[str, Any]:
        """
        Extract WorldSeed fields from player input.

        Args:
            player_input: What the player just said.
            current_fields: Fields already established (to avoid re-extraction).
            act: Current act (used to scope which fields are relevant).
            session_id: Session ID for WorkflowContext tracing.

        Returns:
            Dict of newly extracted fields (may be empty).
        """
        context = WorkflowContext(workflow_id=session_id)
        raw = await self._extractor.execute(
            {"player_input": player_input, "current_fields": current_fields},
            context,
        )
        # Drop already-established fields; validate enum values
        new_only = {k: v for k, v in raw.items() if k not in current_fields}
        return _validate_fields(new_only)

    async def generate_surprise_seed(
        self, session_id: str = "genesis"
    ) -> dict[str, Any]:
        """Generate a complete WorldSeed for 'surprise me' requests."""
        context = WorkflowContext(workflow_id=session_id)
        raw = await self._surprise.execute({}, context)
        return _validate_fields(raw)
