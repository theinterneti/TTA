"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Narrative_consequence_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Narrative_consequence_system]]
Narrative Consequence System for Therapeutic Text Adventure

This module tracks narrative-level consequences of player choices, managing
immediate through permanent consequence chains and applying them to
subsequent scenes for coherent, meaningful storytelling.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from ..models.core import Scene, SessionState
from ..models.interactions import UserChoice

logger = logging.getLogger(__name__)


class ConsequenceScope(StrEnum):
    """Temporal scope of a narrative consequence."""

    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    PERMANENT = "permanent"


class ConsequenceType(StrEnum):
    """Domain of a narrative consequence."""

    NARRATIVE = "narrative"
    EMOTIONAL = "emotional"
    RELATIONAL = "relational"
    SKILL = "skill"
    WORLD_STATE = "world_state"


# How many scenes each scope typically persists
_SCOPE_DURATION: dict[ConsequenceScope, int] = {
    ConsequenceScope.IMMEDIATE: 1,
    ConsequenceScope.SHORT_TERM: 3,
    ConsequenceScope.LONG_TERM: 10,
    ConsequenceScope.PERMANENT: 999,
}


class NarrativeConsequenceSystem:
    """
    Evaluates, tracks, and applies narrative-level consequences of player
    choices to maintain story coherence and therapeutic significance.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.consequence_chains: list[dict[str, Any]] = []
        self.active_consequences: dict[str, dict[str, Any]] = {}

        logger.info("NarrativeConsequenceSystem initialized")

    async def initialize(self) -> bool:
        """Initialize consequence tracking structures."""
        try:
            self.consequence_chains = []
            self.active_consequences = {}

            logger.info("NarrativeConsequenceSystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"NarrativeConsequenceSystem initialization failed: {e}")
            return False

    async def evaluate_consequences(
        self, choice: UserChoice, session_state: SessionState
    ) -> list[dict[str, Any]]:
        """
        Evaluate the narrative consequences of a player choice.

        Args:
            choice: The choice made by the player
            session_state: Current session state

        Returns:
            List of consequence descriptors
        """
        try:
            consequences: list[dict[str, Any]] = []

            # Narrative consequence based on choice therapeutic value
            scope = self._determine_scope(choice)
            consequences.append(
                self._build_consequence(
                    session_id=session_state.session_id,
                    scope=scope,
                    consequence_type=ConsequenceType.NARRATIVE,
                    description=(
                        f"Narrative shift from choice '{choice.choice_text[:40]}'"
                    ),
                    magnitude=choice.therapeutic_value,
                )
            )

            # Emotional consequence tied to state change
            if choice.emotional_state_after and (
                choice.emotional_state_after != choice.emotional_state_before
            ):
                consequences.append(
                    self._build_consequence(
                        session_id=session_state.session_id,
                        scope=ConsequenceScope.SHORT_TERM,
                        consequence_type=ConsequenceType.EMOTIONAL,
                        description=(
                            f"Emotional shift: {choice.emotional_state_before} "
                            f"-> {choice.emotional_state_after}"
                        ),
                        magnitude=0.5,
                    )
                )

            # Skill consequence if therapeutic tags present
            if choice.therapeutic_tags:
                consequences.append(
                    self._build_consequence(
                        session_id=session_state.session_id,
                        scope=ConsequenceScope.LONG_TERM,
                        consequence_type=ConsequenceType.SKILL,
                        description=(
                            f"Skill engagement: {', '.join(choice.therapeutic_tags[:3])}"
                        ),
                        magnitude=choice.therapeutic_value * 0.8,
                    )
                )

            logger.info(
                f"Evaluated {len(consequences)} consequences for choice "
                f"{choice.choice_id}"
            )
            return consequences

        except Exception as e:
            logger.error(f"Consequence evaluation failed: {e}")
            return []

    async def apply_consequences(
        self, scene: Scene, consequences: list[dict[str, Any]]
    ) -> Scene:
        """
        Modify a scene based on a set of active consequences.

        Args:
            scene: Scene to modify
            consequences: Consequence descriptors to apply

        Returns:
            Scene with consequences applied
        """
        try:
            for consequence in consequences:
                cid = consequence.get("consequence_id", "unknown")
                ctype = consequence.get("consequence_type", "")
                description = consequence.get("description", "")

                if ctype == ConsequenceType.NARRATIVE:
                    scene.narrative_content += (
                        f"\n\n[The echoes of past choices shape this moment: "
                        f"{description}]"
                    )
                elif ctype == ConsequenceType.EMOTIONAL:
                    scene.emotional_tone = "reflective"
                elif ctype == ConsequenceType.RELATIONAL:
                    scene.narrative_content += (
                        f"\n\n[Your relationships shift: {description}]"
                    )
                elif ctype == ConsequenceType.SKILL:
                    if description not in scene.learning_objectives:
                        scene.learning_objectives.append(description)

                # Register as active
                self.active_consequences[cid] = consequence

            # Decay remaining_scenes for all active consequences after application
            expired: list[str] = []
            for aid, ac in self.active_consequences.items():
                remaining = ac.get("remaining_scenes", 0)
                ac["remaining_scenes"] = max(remaining - 1, 0)
                if ac["remaining_scenes"] <= 0:
                    expired.append(aid)
            for aid in expired:
                del self.active_consequences[aid]

            logger.info(
                f"Applied {len(consequences)} consequences to scene {scene.scene_id}"
            )
            return scene

        except Exception as e:
            logger.error(
                f"Consequence application failed for scene {scene.scene_id}: {e}"
            )
            return scene

    async def track_consequence_chain(
        self, session_id: str, consequence: dict[str, Any]
    ) -> None:
        """
        Track a consequence and its cascading chain.

        Args:
            session_id: Session identifier
            consequence: The consequence to track
        """
        try:
            chain_entry: dict[str, Any] = {
                "session_id": session_id,
                "consequence_id": consequence.get("consequence_id", str(uuid4())),
                "parent_id": consequence.get("parent_id"),
                "scope": consequence.get("scope", ConsequenceScope.IMMEDIATE),
                "tracked_at": datetime.now(UTC).isoformat(),
            }
            self.consequence_chains.append(chain_entry)

            logger.info(f"Tracked consequence chain for session {session_id}")

        except Exception as e:
            logger.error(f"Consequence chain tracking failed: {e}")

    async def get_active_consequences(self, session_id: str) -> list[dict[str, Any]]:
        """
        Retrieve all active consequences for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of active consequence descriptors
        """
        try:
            active = [
                c
                for c in self.active_consequences.values()
                if c.get("session_id") == session_id
                and c.get("remaining_scenes", 1) > 0
            ]

            logger.info(
                f"Retrieved {len(active)} active consequences for session {session_id}"
            )
            return active

        except Exception as e:
            logger.error(f"Active consequence retrieval failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_scope(choice: UserChoice) -> ConsequenceScope:
        """Determine consequence scope from a player choice."""
        tv = choice.therapeutic_value
        if tv >= 0.8:
            return ConsequenceScope.PERMANENT
        if tv >= 0.5:
            return ConsequenceScope.LONG_TERM
        if tv >= 0.2:
            return ConsequenceScope.SHORT_TERM
        return ConsequenceScope.IMMEDIATE

    @staticmethod
    def _build_consequence(
        *,
        session_id: str,
        scope: ConsequenceScope,
        consequence_type: ConsequenceType,
        description: str,
        magnitude: float,
    ) -> dict[str, Any]:
        """Build a consequence descriptor dict."""
        return {
            "consequence_id": str(uuid4()),
            "session_id": session_id,
            "scope": str(scope),
            "consequence_type": str(consequence_type),
            "description": description,
            "magnitude": max(0.0, min(magnitude, 1.0)),
            "remaining_scenes": _SCOPE_DURATION.get(scope, 1),
            "created_at": datetime.now(UTC).isoformat(),
        }
