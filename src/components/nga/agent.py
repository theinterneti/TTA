"""NGA — Narrative Generation Agent implementation.

Receives a ProcessedInput + WorldContext assembled by the WBA and generates
the narrative response that is streamed back to the player.

Architecture:
  NGAAgent.generate(processed_input, world_context, ...)
    └── _NGALLMCall — LLM call with assembled prompt
          wrapped in FallbackPrimitive(RetryPrimitive(...))

All LLM calls use TTA.dev primitives via the same import pattern as the
Genesis agent.
"""

from __future__ import annotations

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
    pass  # ttadev not available — real types provided by try branch above

from src.ai_components.llm_factory import get_llm
from src.components.guide.intervention import InterventionType
from src.components.guide.prompt import GuidePromptBuilder
from src.components.ipa.models import ProcessedInput
from src.components.world_context.models import WorldContext

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are the narrator of a therapeutic text adventure. Your role is to weave
an immersive, emotionally sensitive narrative that meets the player exactly
where they are.

Guidelines:
- Write 2–4 short paragraphs of vivid, present-tense narrative
- Honour the player's intent and emotional tone
- Ground the narrative in the world facts provided
- If NPCs are present, give them a brief moment of life
- Never lecture, diagnose, or break the fictional frame
- For safety_signal=true inputs, write with extra warmth and gentleness
- End with a subtle open invitation to continue
"""


def _build_user_message(
    processed_input: ProcessedInput,
    world_context: WorldContext,
    history: list[str] | None,
) -> str:
    """Assemble the user-turn message from IPA output + world context."""
    parts: list[str] = []

    # World grounding
    loc = world_context.location
    parts.append(
        f"## Current Location\n{loc.name}: {loc.description or '(no description)'}"
    )
    if world_context.zone:
        parts.append(f"Zone: {world_context.zone.name}")

    if world_context.npcs:
        npc_lines = [
            f"- {n.name} ({n.role or 'NPC'})"
            + (f" — {n.emotional_state}" if n.emotional_state else "")
            for n in world_context.npcs
            if n.is_active
        ]
        if npc_lines:
            parts.append("## Present NPCs\n" + "\n".join(npc_lines))

    if world_context.active_events:
        event_lines = [
            f"- {e.name}: {e.description or ''}"
            for e in world_context.active_events
            if e.is_active
        ]
        if event_lines:
            parts.append("## Active Events\n" + "\n".join(event_lines))

    if world_context.connected_locations:
        exits = [
            (f"{c.direction}: " if c.direction else "") + c.name
            for c in world_context.connected_locations
        ]
        parts.append("## Exits\n" + ", ".join(exits))

    # Player input
    parts.append(
        f"## Player Input\n"
        f"Intent: {processed_input.intent} (confidence {processed_input.intent_confidence:.2f})\n"
        f"Text: {processed_input.raw_text}"
    )

    if processed_input.entities:
        entity_names = ", ".join(e.name for e in processed_input.entities)
        parts.append(f"Referenced: {entity_names}")

    if processed_input.emotional_tone.primary != "neutral":
        parts.append(
            f"Emotional tone: {processed_input.emotional_tone.primary} "
            f"(intensity {processed_input.emotional_tone.intensity:.2f})"
        )

    if processed_input.needs_safety_check:
        parts.append("⚠ Safety signal detected — respond with warmth and extra care.")

    # Optional recent history
    if history:
        recent = history[-3:]
        parts.append("## Recent Turns\n" + "\n".join(recent))

    return "\n\n".join(parts)


_SAFE_FALLBACK = (
    "The world seems to pause, holding its breath. "
    "Take your time — the story will be here when you're ready."
)


# ---------------------------------------------------------------------------
# WorkflowPrimitive classes
# ---------------------------------------------------------------------------


class _NGALLMCall(WorkflowPrimitive):  # type: ignore[misc]
    """One LLM call to generate narrative text."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> str:
        system_prompt: str = input_data["system_prompt"]
        user_message: str = input_data["user_message"]

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        response = await self._llm.ainvoke(messages)
        return response.content.strip()


class _NGAFallback(WorkflowPrimitive):  # type: ignore[misc]
    """Safe fallback narrative when the LLM call fails."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> str:
        return _SAFE_FALLBACK


# ---------------------------------------------------------------------------
# NGAAgent
# ---------------------------------------------------------------------------


class NGAAgent:
    """Narrative Generation Agent — third stage of the IPA → WBA → NGA pipeline.

    Combines ProcessedInput + WorldContext to generate the player-facing
    narrative response.

    Usage::

        agent = NGAAgent()
        text = await agent.generate(processed_input, world_context)
        # Returns a 2–4 paragraph narrative string
    """

    def __init__(self, llm: Any | None = None) -> None:
        """
        Args:
            llm: LLM instance for narrative generation. Defaults to a
                 higher-temperature creative model via ``get_llm()``.
        """
        _llm = llm or get_llm(temperature=0.85, max_tokens=600)
        self._primitive = FallbackPrimitive(
            primary=RetryPrimitive(  # type: ignore[arg-type]
                _NGALLMCall(_llm),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.5),  # type: ignore[arg-type]
            ),
            fallback=_NGAFallback(),
        )

    async def generate(
        self,
        processed_input: ProcessedInput,
        world_context: WorldContext,
        history: list[str] | None = None,
        guide_voice_params: dict | None = None,
        intervention_type: InterventionType | None = None,
    ) -> str:
        """Generate a narrative response for the player.

        Args:
            processed_input: Structured IPA output (intent, entities, tone).
            world_context:   WBA-assembled world context (location, NPCs, etc.).
            history:         Optional list of recent turn strings for continuity.
            guide_voice_params: Optional Guide voice config dict (tone, formality,
                intervention_style, reflection_frequency).  When provided, Guide
                voice instructions are prepended to the system prompt.
            intervention_type: Optional intervention type from
                GuideInterventionDecider.  Defaults to NONE when guide params
                are supplied without an explicit type.

        Returns:
            Narrative text (2–4 paragraphs) ready to stream to the player.
        """
        session_id = processed_input.session_id
        ctx = WorkflowContext(workflow_id=session_id or f"nga-{id(self)}")

        user_message = _build_user_message(processed_input, world_context, history)

        # Build system prompt, optionally prepending Guide voice instructions
        system_prompt = _SYSTEM_PROMPT
        if guide_voice_params is not None:
            _builder = GuidePromptBuilder()
            _itype = (
                intervention_type
                if intervention_type is not None
                else InterventionType.NONE
            )
            guide_addition = _builder.build_full_system_addition(
                guide_voice_params, _itype
            )
            system_prompt = guide_addition + "\n\n" + _SYSTEM_PROMPT

        narrative = await self._primitive.execute(
            {
                "system_prompt": system_prompt,
                "user_message": user_message,
            },
            ctx,  # type: ignore[arg-type]
        )

        logger.info(
            "nga: session=%s intent=%s location=%s chars=%d guide=%s",
            session_id,
            processed_input.intent,
            world_context.location_id,
            len(narrative),
            intervention_type.value if intervention_type else "none",
        )

        return narrative
