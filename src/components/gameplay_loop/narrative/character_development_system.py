"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Character_development_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Character_development_system]]
Character Development System for Therapeutic Text Adventure

This module tracks therapeutic progress through character arcs, mapping
player choices to character growth across emotional, cognitive, social,
behavioural, and spiritual development domains.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from ..models.core import SessionState
from ..models.interactions import ChoiceOutcome
from ..models.progress import ProgressMarker, ProgressType

logger = logging.getLogger(__name__)


class ArcPhase(StrEnum):
    """Phases of a character's narrative arc."""

    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CRISIS = "crisis"
    TURNING_POINT = "turning_point"
    RESOLUTION = "resolution"
    GROWTH = "growth"


class DevelopmentDomain(StrEnum):
    """Domains of character development."""

    EMOTIONAL = "emotional"
    COGNITIVE = "cognitive"
    SOCIAL = "social"
    BEHAVIORAL = "behavioral"
    SPIRITUAL = "spiritual"


# Minimum choice count thresholds for each arc phase
_PHASE_THRESHOLDS: list[tuple[int, ArcPhase]] = [
    (20, ArcPhase.GROWTH),
    (15, ArcPhase.RESOLUTION),
    (10, ArcPhase.TURNING_POINT),
    (6, ArcPhase.CRISIS),
    (3, ArcPhase.RISING_ACTION),
    (0, ArcPhase.INTRODUCTION),
]


class CharacterDevelopmentSystem:
    """
    Tracks how player choices shape character growth through narrative
    arcs, generating development milestones that reflect therapeutic
    progress.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.character_arcs: dict[str, dict[str, Any]] = {}
        self.development_milestones: list[dict[str, Any]] = []

        logger.info("CharacterDevelopmentSystem initialized")

    async def initialize(self) -> bool:
        """Initialize character arc tracking structures."""
        try:
            self.character_arcs = {}
            self.development_milestones = []

            logger.info("CharacterDevelopmentSystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"CharacterDevelopmentSystem initialization failed: {e}")
            return False

    async def track_character_growth(
        self, session_state: SessionState, choice_outcome: ChoiceOutcome
    ) -> dict[str, Any]:
        """
        Track how a player choice affects character development.

        Args:
            session_state: Current session state
            choice_outcome: Outcome of the choice

        Returns:
            Growth summary with affected domains and deltas
        """
        try:
            session_id = session_state.session_id
            arc = self._ensure_arc(session_id)

            growth: dict[str, float] = {}

            # Map outcome fields to development domains
            if choice_outcome.character_changes:
                for attr, delta in choice_outcome.character_changes.items():
                    domain = self._attribute_to_domain(attr)
                    growth[str(domain)] = growth.get(str(domain), 0.0) + delta

            if choice_outcome.skills_developed:
                growth[str(DevelopmentDomain.COGNITIVE)] = (
                    growth.get(str(DevelopmentDomain.COGNITIVE), 0.0)
                    + len(choice_outcome.skills_developed) * 0.05
                )

            if choice_outcome.insights_gained:
                growth[str(DevelopmentDomain.EMOTIONAL)] = (
                    growth.get(str(DevelopmentDomain.EMOTIONAL), 0.0)
                    + len(choice_outcome.insights_gained) * 0.08
                )

            # Update the arc's cumulative growth
            for domain_str, delta in growth.items():
                arc["growth"][domain_str] = arc["growth"].get(domain_str, 0.0) + delta

            arc["choices_processed"] = arc.get("choices_processed", 0) + 1
            arc["current_phase"] = str(await self.assess_arc_phase(session_state))

            summary: dict[str, Any] = {
                "session_id": session_id,
                "growth_deltas": growth,
                "cumulative_growth": dict(arc["growth"]),
                "current_phase": arc["current_phase"],
            }

            logger.info(
                f"Tracked character growth for session {session_id}: "
                f"{len(growth)} domains affected"
            )
            return summary

        except Exception as e:
            logger.error(f"Character growth tracking failed: {e}")
            return {}

    async def assess_arc_phase(self, session_state: SessionState) -> ArcPhase:
        """
        Determine the current character arc phase.

        Args:
            session_state: Current session state

        Returns:
            Current arc phase
        """
        try:
            choices_made = session_state.metrics.total_choices_made
            effectiveness = session_state.metrics.therapeutic_effectiveness

            for threshold, phase in _PHASE_THRESHOLDS:
                if choices_made >= threshold:
                    # Require decent effectiveness for the later phases
                    if phase in (ArcPhase.RESOLUTION, ArcPhase.GROWTH):
                        if effectiveness < 0.5:
                            continue
                    return phase

            return ArcPhase.INTRODUCTION

        except Exception as e:
            logger.warning(f"Arc phase assessment failed: {e}")
            return ArcPhase.INTRODUCTION

    async def generate_development_milestone(
        self, session_state: SessionState, domain: DevelopmentDomain
    ) -> ProgressMarker | None:
        """
        Generate a development milestone for a specific domain.

        Args:
            session_state: Current session state
            domain: Development domain to assess

        Returns:
            A ProgressMarker if a milestone was earned, else None
        """
        try:
            session_id = session_state.session_id
            arc = self._ensure_arc(session_id)
            cumulative = arc["growth"].get(str(domain), 0.0)

            # Check if growth crosses a milestone boundary
            milestones_earned = int(cumulative / 0.25)
            existing = sum(
                1
                for m in self.development_milestones
                if m.get("session_id") == session_id and m.get("domain") == str(domain)
            )

            if milestones_earned <= existing:
                return None

            marker = ProgressMarker(
                marker_id=str(uuid4()),
                session_id=session_id,
                user_id=session_state.user_id,
                progress_type=ProgressType.MILESTONE_REACHED,
                title=f"{domain.value.capitalize()} Growth Milestone",
                description=(
                    f"Reached level {milestones_earned} in {domain.value} "
                    f"development (cumulative: {cumulative:.2f})"
                ),
                significance=f"Level {milestones_earned}",
                progress_value=min(cumulative, 1.0),
                therapeutic_domains=[str(domain)],
            )

            self.development_milestones.append(
                {
                    "session_id": session_id,
                    "domain": str(domain),
                    "level": milestones_earned,
                    "achieved_at": datetime.now(UTC).isoformat(),
                }
            )

            logger.info(
                f"Generated milestone: {domain} level {milestones_earned} "
                f"for session {session_id}"
            )
            return marker

        except Exception as e:
            logger.error(f"Milestone generation failed: {e}")
            return None

    async def get_character_arc_summary(self, session_id: str) -> dict[str, Any]:
        """
        Get a summary of the character arc for a session.

        Args:
            session_id: Session identifier

        Returns:
            Arc summary with phase, growth, and milestones
        """
        try:
            arc = self.character_arcs.get(session_id, {})
            milestones = [
                m
                for m in self.development_milestones
                if m.get("session_id") == session_id
            ]

            summary: dict[str, Any] = {
                "session_id": session_id,
                "current_phase": arc.get("current_phase", ArcPhase.INTRODUCTION),
                "choices_processed": arc.get("choices_processed", 0),
                "cumulative_growth": arc.get("growth", {}),
                "milestones": milestones,
            }

            logger.info(f"Retrieved arc summary for session {session_id}")
            return summary

        except Exception as e:
            logger.error(f"Arc summary retrieval failed: {e}")
            return {"session_id": session_id, "error": str(e)}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_arc(self, session_id: str) -> dict[str, Any]:
        """Ensure a character arc exists for the session."""
        if session_id not in self.character_arcs:
            self.character_arcs[session_id] = {
                "current_phase": str(ArcPhase.INTRODUCTION),
                "choices_processed": 0,
                "growth": {},
                "created_at": datetime.now(UTC).isoformat(),
            }
        return self.character_arcs[session_id]

    @staticmethod
    def _attribute_to_domain(attribute: str) -> DevelopmentDomain:
        """Map a character attribute name to a development domain."""
        mapping: dict[str, DevelopmentDomain] = {
            "confidence": DevelopmentDomain.EMOTIONAL,
            "empathy": DevelopmentDomain.SOCIAL,
            "resilience": DevelopmentDomain.BEHAVIORAL,
            "wisdom": DevelopmentDomain.COGNITIVE,
            "courage": DevelopmentDomain.BEHAVIORAL,
            "compassion": DevelopmentDomain.SOCIAL,
            "patience": DevelopmentDomain.EMOTIONAL,
            "creativity": DevelopmentDomain.COGNITIVE,
        }
        return mapping.get(attribute.lower(), DevelopmentDomain.EMOTIONAL)
