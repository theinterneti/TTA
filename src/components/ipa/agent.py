"""IPA — Input Processing Agent implementation.

Classifies player intent, extracts named entities, and detects emotional tone
from raw player text. Produces a structured ProcessedInput fed into the WBA.

Architecture:
  IPAAgent.process(raw_text, ...)
    └── _IPACall — LLM call to extract IntentClassification JSON
          wrapped in FallbackPrimitive(RetryPrimitive(...))

All LLM calls use TTA.dev primitives via the same import pattern as the
Genesis agent.
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
    from tta_dev_primitives import (  # type: ignore[no-redef]
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )

from src.ai_components.llm_factory import get_llm

from .models import (
    EmotionalTone,
    ExtractedEntity,
    Intent,
    ProcessedInput,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an input processing agent for a therapeutic text adventure.
Given the player's message, respond with a JSON object containing:

{
  "intent": "<one of: explore, interact, query, action, journal, unknown>",
  "intent_confidence": <float 0.0–1.0>,
  "entities": [
    {"name": "<entity name>", "entity_type": "<npc|location|item|concept>", "confidence": <float>}
  ],
  "emotional_tone": {
    "primary": "<neutral|anxious|curious|sad|angry|joyful|fearful|hopeful>",
    "intensity": <float 0.0–1.0>,
    "safety_signal": <true if crisis/distress indicators present>
  },
  "normalized_text": "<cleaned, lowercased version of the input>"
}

Rules:
- intent_confidence should be high (>0.8) only when clearly evident
- safety_signal=true if text contains self-harm, crisis, or severe distress language
- entities should only include things explicitly mentioned in the text
- Return valid JSON only — no additional text
"""

_FALLBACK_RESULT = {
    "intent": "unknown",
    "intent_confidence": 0.5,
    "entities": [],
    "emotional_tone": {"primary": "neutral", "intensity": 0.0, "safety_signal": False},
    "normalized_text": "",
}


# ---------------------------------------------------------------------------
# WorkflowPrimitive classes
# ---------------------------------------------------------------------------


class _IPALLMCall(WorkflowPrimitive):  # type: ignore[misc]
    """One LLM call to extract IntentClassification JSON."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        raw_text: str = input_data["raw_text"]
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=raw_text),
        ]
        response = await self._llm.ainvoke(messages)
        content = response.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        parsed: dict[str, Any] = json.loads(content)
        return parsed


class _IPAFallback(WorkflowPrimitive):  # type: ignore[misc]
    """Safe fallback when the LLM call fails."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        raw_text: str = input_data["raw_text"]
        result = dict(_FALLBACK_RESULT)
        result["normalized_text"] = raw_text.lower().strip()
        return result


# ---------------------------------------------------------------------------
# IPAAgent
# ---------------------------------------------------------------------------


class IPAAgent:
    """Input Processing Agent — first stage of the IPA → WBA → NGA pipeline.

    Converts raw player text into a structured ProcessedInput.

    Usage::

        agent = IPAAgent()
        result = await agent.process(
            raw_text="I want to talk to the blacksmith",
            session_id="sess-123",
            player_id="player-456",
            location_id="loc-789",
        )
        # result.intent == Intent.INTERACT
        # result.npc_names == ["blacksmith"]
    """

    def __init__(self, llm: Any | None = None) -> None:
        """
        Args:
            llm: LLM instance for intent classification. Defaults to
                 a low-temperature model via ``get_llm()``.
        """
        _llm = llm or get_llm(temperature=0.1, max_tokens=400)
        self._primitive = FallbackPrimitive(
            primary=RetryPrimitive(  # type: ignore[arg-type]
                _IPALLMCall(_llm),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.0),  # type: ignore[arg-type]
            ),
            fallback=_IPAFallback(),
        )

    async def process(
        self,
        raw_text: str,
        session_id: str = "",
        player_id: str = "",
        location_id: str | None = None,
    ) -> ProcessedInput:
        """Classify intent and extract entities from raw player text.

        Args:
            raw_text:   The player's raw input.
            session_id: Session identifier for observability.
            player_id:  Player identifier for observability.
            location_id: Current location ID (attached to output for WBA).

        Returns:
            Structured ProcessedInput with intent, entities, and tone.
        """
        ctx = WorkflowContext(workflow_id=session_id or f"ipa-{id(self)}")
        result = await self._primitive.execute({"raw_text": raw_text}, ctx)  # type: ignore[arg-type]

        # Parse entities
        entities: list[ExtractedEntity] = []
        for ent in result.get("entities", []):
            try:
                entities.append(
                    ExtractedEntity(
                        name=ent.get("name", ""),
                        entity_type=ent.get("entity_type", "concept"),
                        confidence=float(ent.get("confidence", 0.7)),
                    )
                )
            except Exception as exc:
                logger.debug("IPA: skipping malformed entity %r: %s", ent, exc)

        # Parse emotional tone
        tone_raw: dict[str, Any] = result.get("emotional_tone", {})
        tone = EmotionalTone(
            primary=tone_raw.get("primary", "neutral"),
            intensity=float(tone_raw.get("intensity", 0.0)),
            safety_signal=bool(tone_raw.get("safety_signal", False)),
        )

        # Map intent string to enum safely
        intent_str: str = result.get("intent", "unknown")
        try:
            intent = Intent(intent_str)
        except ValueError:
            logger.debug("IPA: unknown intent value %r — using UNKNOWN", intent_str)
            intent = Intent.UNKNOWN

        normalized_text: str = result.get("normalized_text", raw_text.lower().strip())
        intent_confidence: float = float(result.get("intent_confidence", 0.5))

        logger.info(
            "ipa: session=%s intent=%s confidence=%.2f entities=%d safety=%s",
            session_id,
            intent,
            intent_confidence,
            len(entities),
            tone.safety_signal,
        )

        return ProcessedInput(
            raw_text=raw_text,
            normalized_text=normalized_text,
            intent=intent,
            intent_confidence=intent_confidence,
            entities=entities,
            emotional_tone=tone,
            session_id=session_id,
            player_id=player_id,
            location_id=location_id,
        )
