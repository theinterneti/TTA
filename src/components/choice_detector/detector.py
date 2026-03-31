"""
# Logseq: [[TTA/Components/Choice_detector/Detector]]
ChoiceSignificanceDetector — classifies player inputs by narrative impact level.

Two-stage pipeline:
  1. Rule-based heuristics (verb patterns, world-state markers) — fast, deterministic
  2. LLM classifier (optional) with FallbackPrimitive — used only when rule-based is
     inconclusive (future #292 enhancement)

Issue: #289
"""

from __future__ import annotations

import logging
import re
from enum import StrEnum

logger = logging.getLogger(__name__)


class SignificanceLevel(StrEnum):
    """Narrative impact level of a player choice."""

    LOW = "low"  # Exploration, observation, dialogue
    MEDIUM = "medium"  # Minor interaction with limited consequences
    HIGH = "high"  # Major decision with lasting consequences
    CRITICAL = "critical"  # Irreversible, world-altering


# ---------------------------------------------------------------------------
# Rule-based signal patterns (regex)
# ---------------------------------------------------------------------------

# Actions that are almost always LOW
_LOW_PATTERNS = [
    r"\b(look|examine|inspect|observe|watch|listen|smell|touch|check)\b",
    r"\b(go|walk|move|travel|head|wander)\b",
    r"\b(ask|say|tell|talk|speak|greet|whisper)\b",
    r"\b(wait|rest|sit|stand|pause)\b",
    r"\b(pick up|take|grab|collect)\b",
]

# Actions suggesting MEDIUM significance
_MEDIUM_PATTERNS = [
    r"\b(buy|sell|trade|exchange|barter)\b",
    r"\b(give|hand|offer|share)\b",
    r"\b(attack|fight|hit|push|threaten)\b",  # minor conflict
    r"\b(help|assist|support|aid)\b",
    r"\b(open|unlock|activate|use)\b",
]

# Actions suggesting HIGH significance
_HIGH_PATTERNS = [
    r"\b(join|pledge|swear|ally|side with|commit to)\b",
    r"\b(betray|abandon|leave behind|forsake)\b",
    r"\b(reveal|confess|expose|tell.*truth|admit)\b",
    r"\b(decide|choose|accept|refuse|reject)\b",
    r"\b(destroy|break|burn|shatter)\b",
    r"\b(marry|promise|vow|swear.*oath)\b",
]

# Markers suggesting CRITICAL significance
_CRITICAL_PATTERNS = [
    r"\b(kill|murder|execute|slay|end.*life)\b",
    r"\b(sacrifice|die|give.*life)\b",
    r"\b(never|forever|always|permanent|irreversible)\b",
    r"\b(declare war|start.*war|end.*war)\b",
    r"\b(destroy.*world|unmake|erase)\b",
    r"\bfinal\b.*\b(choice|decision|act)\b",
]

# World-state markers that escalate any action by one level
_ESCALATION_MARKERS = [
    r"\bforever\b",
    r"\bnever.*again\b",
    r"\bno.*turning back\b",
    r"\blast.*chance\b",
    r"\bno one.*ever\b",
]

_compiled_patterns: dict[str, list[re.Pattern[str]]] = {}


def _get_patterns() -> dict[str, list[re.Pattern[str]]]:
    """Compile patterns once (lazy)."""
    global _compiled_patterns  # noqa: PLW0603
    if not _compiled_patterns:
        _compiled_patterns = {
            "low": [re.compile(p, re.IGNORECASE) for p in _LOW_PATTERNS],
            "medium": [re.compile(p, re.IGNORECASE) for p in _MEDIUM_PATTERNS],
            "high": [re.compile(p, re.IGNORECASE) for p in _HIGH_PATTERNS],
            "critical": [re.compile(p, re.IGNORECASE) for p in _CRITICAL_PATTERNS],
            "escalation": [re.compile(p, re.IGNORECASE) for p in _ESCALATION_MARKERS],
        }
    return _compiled_patterns


def _rule_based_classify(text: str) -> tuple[SignificanceLevel, float]:
    """
    Rule-based classification. Returns (level, confidence).

    Confidence is high (0.85+) when a clear level is detected;
    lower (0.40) when only inconclusive signals are found.
    """
    patterns = _get_patterns()
    text_lower = text.lower()

    # Check escalation markers — bump level up if present
    has_escalation = any(p.search(text_lower) for p in patterns["escalation"])

    # Check from highest to lowest severity
    if any(p.search(text_lower) for p in patterns["critical"]):
        return SignificanceLevel.CRITICAL, 0.90

    if any(p.search(text_lower) for p in patterns["high"]):
        level = SignificanceLevel.CRITICAL if has_escalation else SignificanceLevel.HIGH
        return level, 0.85

    if any(p.search(text_lower) for p in patterns["medium"]):
        level = SignificanceLevel.HIGH if has_escalation else SignificanceLevel.MEDIUM
        return level, 0.80

    if any(p.search(text_lower) for p in patterns["low"]):
        level = SignificanceLevel.MEDIUM if has_escalation else SignificanceLevel.LOW
        return level, 0.85

    # Inconclusive — default to MEDIUM, low confidence
    return SignificanceLevel.MEDIUM, 0.40


class ChoiceSignificanceDetector:
    """
    Classifies player input text by narrative significance level.

    Uses rule-based heuristics (verb patterns + world-state escalation markers).
    Always non-raising — returns a safe default on any error.
    """

    INCONCLUSIVE_CONFIDENCE_THRESHOLD: float = 0.50

    def classify(
        self,
        player_text: str,
        narrative_context: str = "",
    ) -> tuple[SignificanceLevel, float]:
        """
        Classify player input by narrative significance.

        Args:
            player_text: Raw player input text.
            narrative_context: Optional surrounding context (recent turns) to
                improve accuracy.

        Returns:
            (SignificanceLevel, confidence) — confidence in [0.0, 1.0].
        """
        try:
            if not player_text or not player_text.strip():
                return SignificanceLevel.LOW, 0.90

            # Combine player text + limited context for pattern matching
            combined = player_text
            if narrative_context:
                combined = f"{narrative_context[-200:]} {player_text}"

            level, confidence = _rule_based_classify(combined)

            if level != SignificanceLevel.LOW:
                logger.info(
                    "choice: significance=%s confidence=%.2f text=%r",
                    level,
                    confidence,
                    player_text[:60],
                )

            return level, confidence

        except Exception as exc:
            logger.error("ChoiceSignificanceDetector.classify failed: %s", exc)
            return SignificanceLevel.MEDIUM, 0.10

    def is_dolt_commit_worthy(self, level: SignificanceLevel) -> bool:
        """Returns True if this significance level should trigger a Dolt snapshot."""
        return level in (SignificanceLevel.HIGH, SignificanceLevel.CRITICAL)

    def is_world_state_update_worthy(self, level: SignificanceLevel) -> bool:
        """Returns True if this level warrants a Neo4j world state update."""
        return level in (
            SignificanceLevel.MEDIUM,
            SignificanceLevel.HIGH,
            SignificanceLevel.CRITICAL,
        )
