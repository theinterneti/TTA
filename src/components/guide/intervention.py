"""
# Logseq: [[TTA/Components/Guide/Intervention]]
Guide intervention trigger logic.

The Guide decides when to step from narrator into companion voice.
Decisions are based on safety level, crisis level, pacing signals, and
explicit player commands.
"""

from __future__ import annotations

import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class InterventionType(StrEnum):
    """The four intervention types in ascending intensity."""

    NONE = "none"  # Normal narration
    SENSORY_PAUSE = "sensory_pause"  # Describe something beautiful/restful mid-scene
    SOFT_PROMPT = "soft_prompt"  # One gentle question at scene end
    COMPANION_SHIFT = "companion_shift"  # Explicit companion voice
    BREAK_CHARACTER = "break_character"  # Last resort — CRITICAL crisis only


# Map SafetyLevel string values to minimum InterventionType
_SAFETY_INTERVENTION_MAP: dict[str, InterventionType] = {
    "safe": InterventionType.NONE,
    "caution": InterventionType.SENSORY_PAUSE,
    "warning": InterventionType.SOFT_PROMPT,
    "unsafe": InterventionType.COMPANION_SHIFT,
    "crisis": InterventionType.BREAK_CHARACTER,
}

# Map CrisisLevel string values to minimum InterventionType
_CRISIS_INTERVENTION_MAP: dict[str, InterventionType] = {
    "low": InterventionType.NONE,
    "moderate": InterventionType.SENSORY_PAUSE,
    "high": InterventionType.SOFT_PROMPT,
    "critical": InterventionType.BREAK_CHARACTER,
}

# Explicit player command triggers
_EXPLICIT_COMMANDS = {"/reflect", "/journal", "/pause", "/breathe"}


class GuideInterventionDecider:
    """
    Decides whether and how the Guide should intervene on a given turn.

    All inputs are strings (not enums) to avoid import coupling with
    the safety/crisis modules. Callers pass `.value` of the enum.
    """

    def decide(
        self,
        *,
        safety_level: str = "safe",
        crisis_level: str = "low",
        pacing_signal: bool = False,
        player_text: str = "",
        intervention_style: str = "gentle",
    ) -> InterventionType:
        """
        Determine the appropriate intervention type.

        Highest-intensity trigger wins. Never raises.

        Args:
            safety_level: SafetyLevel.value string
            crisis_level: CrisisLevel.value string
            pacing_signal: True when pacing engine requests a breathing space
            player_text: Raw player input (checked for explicit commands)
            intervention_style: Guide's configured style ('mostly-silent'
                suppresses SENSORY_PAUSE)

        Returns:
            The highest-intensity InterventionType triggered.
        """
        try:
            candidates: list[InterventionType] = [InterventionType.NONE]

            # Explicit player commands always trigger SOFT_PROMPT minimum
            if any(cmd in player_text.lower() for cmd in _EXPLICIT_COMMANDS):
                candidates.append(InterventionType.SOFT_PROMPT)

            # Pacing engine signal → at least SENSORY_PAUSE
            if pacing_signal:
                candidates.append(InterventionType.SENSORY_PAUSE)

            # Safety level
            safety_trigger = _SAFETY_INTERVENTION_MAP.get(
                safety_level.lower(), InterventionType.NONE
            )
            candidates.append(safety_trigger)

            # Crisis level
            crisis_trigger = _CRISIS_INTERVENTION_MAP.get(
                crisis_level.lower(), InterventionType.NONE
            )
            candidates.append(crisis_trigger)

            # Highest intensity wins (enum order matters — use list order)
            intensity_order = list(InterventionType)

            def _intensity(t: InterventionType) -> int:
                return intensity_order.index(t)

            best = max(candidates, key=_intensity)

            # 'mostly-silent' style: suppress SENSORY_PAUSE and SOFT_PROMPT
            # unless explicitly commanded or crisis/critical
            if intervention_style == "mostly-silent" and best in (
                InterventionType.SENSORY_PAUSE,
                InterventionType.SOFT_PROMPT,
            ):
                if not any(cmd in player_text.lower() for cmd in _EXPLICIT_COMMANDS):
                    best = InterventionType.NONE

            if best != InterventionType.NONE:
                logger.info(
                    "guide: intervention=%s safety=%s crisis=%s pacing=%s",
                    best,
                    safety_level,
                    crisis_level,
                    pacing_signal,
                )

            return best

        except Exception as exc:
            logger.error("GuideInterventionDecider.decide failed: %s", exc)
            return InterventionType.NONE
