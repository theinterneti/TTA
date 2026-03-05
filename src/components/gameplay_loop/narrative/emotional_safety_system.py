"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Emotional_safety_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Emotional_safety_system]]
Emotional Safety System for Therapeutic Text Adventure

This module implements emotional safety detection and intervention, ensuring
narrative content remains within safe therapeutic boundaries and providing
crisis-level responses when player distress is detected.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

from ..models.core import (
    DifficultyLevel,
    EmotionalState,
    Scene,
    SceneType,
    SessionState,
)

logger = logging.getLogger(__name__)


class SafetyLevel(StrEnum):
    """Levels of emotional safety assessment."""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    UNSAFE = "unsafe"
    CRISIS = "crisis"


class ContentFlag(StrEnum):
    """Flags for problematic content categories."""

    TRIGGERING = "triggering"
    OVERWHELMING = "overwhelming"
    INAPPROPRIATE = "inappropriate"
    RETRAUMATIZING = "retraumatizing"
    HARMFUL = "harmful"


# Keywords associated with emotional risk categories
_RISK_KEYWORDS: dict[ContentFlag, list[str]] = {
    ContentFlag.TRIGGERING: [
        "self-harm",
        "suicide",
        "abuse",
        "violence",
        "trauma",
    ],
    ContentFlag.OVERWHELMING: [
        "hopeless",
        "unbearable",
        "can't cope",
        "too much",
        "breaking down",
    ],
    ContentFlag.INAPPROPRIATE: [
        "explicit",
        "graphic violence",
        "sexual content",
    ],
    ContentFlag.RETRAUMATIZING: [
        "flashback",
        "reliving",
        "nightmare",
        "ptsd trigger",
    ],
    ContentFlag.HARMFUL: [
        "self-destruct",
        "give up",
        "end it all",
        "no reason to live",
    ],
}


class EmotionalSafetySystem:
    """
    Detects and mitigates emotionally unsafe narrative content,
    enforcing therapeutic boundaries and crisis protocols.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.safety_rules: dict[str, Any] = {}
        self.content_filters: list[str] = []
        self.crisis_protocols: dict[SafetyLevel, list[str]] = {}

        logger.info("EmotionalSafetySystem initialized")

    async def initialize(self) -> bool:
        """Initialize safety rules, content filters, and crisis protocols."""
        try:
            self.safety_rules = {
                "max_emotional_intensity": self.config.get(
                    "max_emotional_intensity", 0.8
                ),
                "crisis_threshold": self.config.get("crisis_threshold", 0.9),
                "cool_down_scenes": self.config.get("cool_down_scenes", 2),
            }

            self.content_filters = list(ContentFlag)

            self.crisis_protocols = {
                SafetyLevel.SAFE: [],
                SafetyLevel.CAUTION: ["log_event", "monitor"],
                SafetyLevel.WARNING: ["log_event", "reduce_intensity", "offer_break"],
                SafetyLevel.UNSAFE: [
                    "log_event",
                    "halt_content",
                    "provide_grounding",
                    "offer_exit",
                ],
                SafetyLevel.CRISIS: [
                    "log_event",
                    "immediate_intervention",
                    "display_resources",
                    "notify_support",
                ],
            }

            logger.info("EmotionalSafetySystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"EmotionalSafetySystem initialization failed: {e}")
            return False

    async def assess_content_safety(
        self, content: str, session_state: SessionState
    ) -> dict[str, Any]:
        """
        Assess the emotional safety of narrative content.

        Args:
            content: Text content to evaluate
            session_state: Current session state for context

        Returns:
            Safety assessment with level, flags, and recommendations
        """
        try:
            flags: list[ContentFlag] = []
            content_lower = content.lower()

            for flag, keywords in _RISK_KEYWORDS.items():
                if any(kw in content_lower for kw in keywords):
                    flags.append(flag)

            # Factor in current emotional state
            emotional_risk = self._emotional_state_risk(session_state.emotional_state)
            severity = len(flags) * 0.25 + emotional_risk

            if severity >= 0.9 or ContentFlag.HARMFUL in flags:
                level = SafetyLevel.CRISIS
            elif severity >= 0.7 or ContentFlag.RETRAUMATIZING in flags:
                level = SafetyLevel.UNSAFE
            elif severity >= 0.5:
                level = SafetyLevel.WARNING
            elif severity >= 0.25:
                level = SafetyLevel.CAUTION
            else:
                level = SafetyLevel.SAFE

            recommendations = self.crisis_protocols.get(level, [])

            logger.info(
                f"Content safety assessment: level={level}, flags={flags}, "
                f"severity={severity:.2f}"
            )

            return {
                "safety_level": level,
                "flags": [str(f) for f in flags],
                "severity": severity,
                "recommendations": recommendations,
                "emotional_state": str(session_state.emotional_state),
            }

        except Exception as e:
            logger.error(f"Content safety assessment failed: {e}")
            return {
                "safety_level": SafetyLevel.CAUTION,
                "flags": [],
                "severity": 0.0,
                "recommendations": ["log_event", "monitor"],
                "error": str(e),
            }

    async def filter_unsafe_content(
        self, scene: Scene, session_state: SessionState
    ) -> Scene:
        """
        Filter or modify a scene to remove emotionally unsafe content.

        Args:
            scene: Scene to filter
            session_state: Current session state

        Returns:
            Scene with unsafe content removed or softened
        """
        try:
            assessment = await self.assess_content_safety(
                scene.narrative_content, session_state
            )
            level = SafetyLevel(assessment["safety_level"])

            if level in (SafetyLevel.SAFE, SafetyLevel.CAUTION):
                return scene

            logger.warning(
                f"Filtering unsafe content in scene {scene.scene_id}: level={level}"
            )

            if level == SafetyLevel.CRISIS:
                scene.narrative_content = (
                    "You pause and take a deep breath. The world around you feels "
                    "supportive and grounding. Remember, you are safe here."
                )
                scene.emotional_tone = "supportive"
                scene.difficulty_level = DifficultyLevel.GENTLE
            elif level == SafetyLevel.UNSAFE:
                scene.narrative_content = (
                    "The scene softens around you, offering a moment of calm. "
                    "Take a moment to notice your surroundings and breathe."
                )
                scene.emotional_tone = "calming"
                scene.difficulty_level = DifficultyLevel.GENTLE
            else:
                scene.emotional_tone = "gentle"
                if scene.difficulty_level in (
                    DifficultyLevel.CHALLENGING,
                    DifficultyLevel.INTENSIVE,
                ):
                    scene.difficulty_level = DifficultyLevel.STANDARD

            return scene

        except Exception as e:
            logger.error(f"Content filtering failed for scene {scene.scene_id}: {e}")
            return scene

    async def check_emotional_boundaries(
        self, session_state: SessionState
    ) -> SafetyLevel:
        """
        Check whether emotional boundaries are being respected.

        Args:
            session_state: Current session state

        Returns:
            Current safety level based on emotional boundary analysis
        """
        try:
            emotional_risk = self._emotional_state_risk(session_state.emotional_state)
            safety_alerts_count = len(session_state.safety_alerts)

            crisis_threshold = float(self.safety_rules.get("crisis_threshold", 0.9))

            if emotional_risk >= crisis_threshold or safety_alerts_count >= 3:
                return SafetyLevel.CRISIS
            if emotional_risk >= 0.7 or safety_alerts_count >= 2:
                return SafetyLevel.UNSAFE
            if emotional_risk >= 0.5 or safety_alerts_count >= 1:
                return SafetyLevel.WARNING
            if emotional_risk >= 0.25:
                return SafetyLevel.CAUTION
            return SafetyLevel.SAFE

        except Exception as e:
            logger.error(f"Emotional boundary check failed: {e}")
            return SafetyLevel.CAUTION

    async def trigger_safety_intervention(
        self, session_state: SessionState, safety_level: SafetyLevel
    ) -> Scene | None:
        """
        Create an intervention scene when emotional safety is at risk.

        Args:
            session_state: Current session state
            safety_level: Detected safety level

        Returns:
            An intervention scene, or None if no intervention is needed
        """
        try:
            if safety_level in (SafetyLevel.SAFE, SafetyLevel.CAUTION):
                return None

            logger.warning(
                f"Triggering safety intervention at level {safety_level} "
                f"for session {session_state.session_id}"
            )

            intervention_content = {
                SafetyLevel.WARNING: (
                    "A gentle breeze brings a sense of peace. Your companion "
                    "turns to you and asks, 'Would you like to take a moment "
                    "to rest before we continue?'"
                ),
                SafetyLevel.UNSAFE: (
                    "The world around you shifts to a warm, safe space. "
                    "A calming presence reminds you that you can take all the "
                    "time you need. Would you like to talk about how you're "
                    "feeling, or would you prefer a quiet moment?"
                ),
                SafetyLevel.CRISIS: (
                    "Everything pauses. You are in a safe space. "
                    "If you are in crisis, please reach out to a crisis "
                    "helpline. You are not alone, and support is available. "
                    "Take a deep breath — we are here with you."
                ),
            }

            content = intervention_content.get(
                safety_level,
                "Take a moment to breathe. You are safe here.",
            )

            return Scene(
                title="A Moment of Safety",
                description="An intervention scene providing emotional grounding.",
                narrative_content=content,
                scene_type=SceneType.THERAPEUTIC,
                difficulty_level=DifficultyLevel.GENTLE,
                emotional_tone="supportive",
                therapeutic_focus=["grounding", "emotional_safety"],
            )

        except Exception as e:
            logger.error(f"Safety intervention creation failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _emotional_state_risk(state: EmotionalState) -> float:
        """Map an emotional state to a numeric risk value."""
        risk_map: dict[EmotionalState, float] = {
            EmotionalState.CALM: 0.0,
            EmotionalState.ENGAGED: 0.1,
            EmotionalState.ANXIOUS: 0.5,
            EmotionalState.OVERWHELMED: 0.7,
            EmotionalState.DISTRESSED: 0.85,
            EmotionalState.CRISIS: 1.0,
        }
        return risk_map.get(state, 0.3)
