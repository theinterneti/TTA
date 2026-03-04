"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Collaborative_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Collaborative_system]]
Collaborative System for Therapeutic Text Adventure

This module implements social and multi-player therapeutic scenarios,
enabling cooperative gameplay, peer support, and group therapy dynamics
within the narrative framework.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from ..models.core import DifficultyLevel, Scene, SceneType, SessionState
from ..models.interactions import UserChoice

logger = logging.getLogger(__name__)


class CollaborationType(StrEnum):
    """Types of collaborative therapeutic experiences."""

    COOPERATIVE = "cooperative"
    SUPPORTIVE = "supportive"
    MENTORING = "mentoring"
    GROUP_THERAPY = "group_therapy"
    PEER_SUPPORT = "peer_support"


class ParticipantRole(StrEnum):
    """Roles a participant can assume in a collaborative session."""

    LEADER = "leader"
    SUPPORTER = "supporter"
    OBSERVER = "observer"
    PARTICIPANT = "participant"
    FACILITATOR = "facilitator"


class CollaborativeSystem:
    """
    Manages collaborative therapeutic sessions where multiple players
    or roles interact within shared narrative experiences.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.collaboration_templates: dict[CollaborationType, dict[str, Any]] = {}

        logger.info("CollaborativeSystem initialized")

    async def initialize(self) -> bool:
        """Initialize collaboration templates and session structures."""
        try:
            self.collaboration_templates = {
                CollaborationType.COOPERATIVE: {
                    "description": "Work together toward a shared therapeutic goal",
                    "min_participants": 2,
                    "max_participants": 4,
                    "default_roles": [
                        ParticipantRole.PARTICIPANT,
                        ParticipantRole.SUPPORTER,
                    ],
                },
                CollaborationType.SUPPORTIVE: {
                    "description": "One participant supports another's journey",
                    "min_participants": 2,
                    "max_participants": 2,
                    "default_roles": [
                        ParticipantRole.PARTICIPANT,
                        ParticipantRole.SUPPORTER,
                    ],
                },
                CollaborationType.MENTORING: {
                    "description": "An experienced participant guides a newcomer",
                    "min_participants": 2,
                    "max_participants": 3,
                    "default_roles": [
                        ParticipantRole.LEADER,
                        ParticipantRole.PARTICIPANT,
                    ],
                },
                CollaborationType.GROUP_THERAPY: {
                    "description": "Facilitated group therapeutic experience",
                    "min_participants": 3,
                    "max_participants": 8,
                    "default_roles": [
                        ParticipantRole.FACILITATOR,
                        ParticipantRole.PARTICIPANT,
                    ],
                },
                CollaborationType.PEER_SUPPORT: {
                    "description": "Equal peers supporting each other",
                    "min_participants": 2,
                    "max_participants": 6,
                    "default_roles": [
                        ParticipantRole.PARTICIPANT,
                    ],
                },
            }

            logger.info("CollaborativeSystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"CollaborativeSystem initialization failed: {e}")
            return False

    async def create_collaborative_session(
        self,
        session_state: SessionState,
        collaboration_type: CollaborationType,
    ) -> dict[str, Any]:
        """
        Create a new collaborative session.

        Args:
            session_state: Initiator's session state
            collaboration_type: Type of collaboration

        Returns:
            Collaborative session descriptor
        """
        try:
            template = self.collaboration_templates.get(collaboration_type, {})
            collab_id = str(uuid4())

            collab_session: dict[str, Any] = {
                "collab_session_id": collab_id,
                "collaboration_type": str(collaboration_type),
                "initiator_session_id": session_state.session_id,
                "participants": {},
                "choices_log": [],
                "min_participants": template.get("min_participants", 2),
                "max_participants": template.get("max_participants", 4),
                "status": "waiting_for_participants",
                "created_at": datetime.now(UTC).isoformat(),
            }

            self.active_sessions[collab_id] = collab_session

            # Auto-add the initiator
            default_roles = template.get("default_roles", [ParticipantRole.PARTICIPANT])
            initiator_role = (
                default_roles[0] if default_roles else ParticipantRole.PARTICIPANT
            )
            await self.add_participant(collab_id, session_state.user_id, initiator_role)

            logger.info(
                f"Created collaborative session {collab_id} "
                f"({collaboration_type}) initiated by user "
                f"{session_state.user_id}"
            )
            return collab_session

        except Exception as e:
            logger.error(f"Collaborative session creation failed: {e}")
            return {"error": str(e)}

    async def add_participant(
        self,
        collab_session_id: str,
        user_id: str,
        role: ParticipantRole,
    ) -> bool:
        """
        Add a participant to a collaborative session.

        Args:
            collab_session_id: Collaborative session identifier
            user_id: User to add
            role: Role for the participant

        Returns:
            True if participant was added successfully
        """
        try:
            session = self.active_sessions.get(collab_session_id)
            if session is None:
                logger.warning(f"Collaborative session {collab_session_id} not found")
                return False

            max_p = session.get("max_participants", 4)
            if len(session["participants"]) >= max_p:
                logger.warning(f"Collaborative session {collab_session_id} is full")
                return False

            session["participants"][user_id] = {
                "role": str(role),
                "joined_at": datetime.now(UTC).isoformat(),
                "choices_made": 0,
            }

            # Transition to active if minimum reached
            min_p = session.get("min_participants", 2)
            if (
                len(session["participants"]) >= min_p
                and session["status"] == "waiting_for_participants"
            ):
                session["status"] = "active"

            logger.info(
                f"Added user {user_id} as {role} to session {collab_session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add participant: {e}")
            return False

    async def process_collaborative_choice(
        self,
        collab_session_id: str,
        user_id: str,
        choice: UserChoice,
    ) -> dict[str, Any]:
        """
        Process a choice within a collaborative session.

        Args:
            collab_session_id: Collaborative session identifier
            user_id: User who made the choice
            choice: The choice made

        Returns:
            Processing result with collaborative context
        """
        try:
            session = self.active_sessions.get(collab_session_id)
            if session is None:
                return {"error": "Session not found"}

            participant = session["participants"].get(user_id)
            if participant is None:
                return {"error": "User not a participant"}

            entry: dict[str, Any] = {
                "user_id": user_id,
                "role": participant["role"],
                "choice_id": choice.choice_id,
                "choice_text": choice.choice_text,
                "therapeutic_value": choice.therapeutic_value,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            session["choices_log"].append(entry)
            participant["choices_made"] = participant.get("choices_made", 0) + 1

            # Compute group consensus metrics
            recent_values = [
                c["therapeutic_value"] for c in session["choices_log"][-10:]
            ]
            avg_therapeutic = (
                sum(recent_values) / len(recent_values) if recent_values else 0.0
            )

            result: dict[str, Any] = {
                "collab_session_id": collab_session_id,
                "user_id": user_id,
                "choice_processed": True,
                "group_therapeutic_average": round(avg_therapeutic, 3),
                "total_group_choices": len(session["choices_log"]),
            }

            logger.info(
                f"Processed collaborative choice from {user_id} in "
                f"session {collab_session_id}"
            )
            return result

        except Exception as e:
            logger.error(f"Collaborative choice processing failed: {e}")
            return {"error": str(e)}

    async def generate_group_narrative(
        self,
        collab_session_id: str,
        session_state: SessionState,
    ) -> Scene | None:
        """
        Generate a narrative scene reflecting the group's collaborative actions.

        Args:
            collab_session_id: Collaborative session identifier
            session_state: Requesting user's session state

        Returns:
            A group narrative scene, or None if unavailable
        """
        try:
            session = self.active_sessions.get(collab_session_id)
            if session is None:
                logger.warning(f"Collaborative session {collab_session_id} not found")
                return None

            participants = session["participants"]
            collab_type = session.get("collaboration_type", "cooperative")
            choice_count = len(session["choices_log"])

            # Build a collective narrative based on recent choices
            recent_choices = session["choices_log"][-5:]
            choice_descriptions = [c["choice_text"] for c in recent_choices]
            narrative_body = (
                f"Together, the group of {len(participants)} has navigated "
                f"{choice_count} decisions. "
                f"Recent actions include: " + "; ".join(choice_descriptions[:3]) + "."
            )

            scene = Scene(
                title=f"Collaborative Moment — {collab_type.replace('_', ' ').title()}",
                description=f"A shared therapeutic narrative for {len(participants)} participants.",
                narrative_content=narrative_body,
                scene_type=SceneType.THERAPEUTIC,
                difficulty_level=DifficultyLevel.STANDARD,
                emotional_tone="supportive",
                therapeutic_focus=["collaboration", "peer_support"],
            )

            logger.info(f"Generated group narrative for session {collab_session_id}")
            return scene

        except Exception as e:
            logger.error(f"Group narrative generation failed: {e}")
            return None
