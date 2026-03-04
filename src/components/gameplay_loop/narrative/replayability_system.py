"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Replayability_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Replayability_system]]
Replayability System for Therapeutic Text Adventure

This module manages branching timeline replayability, tracking narrative
branch points, alternative paths, and content discovery to encourage
exploration of diverse therapeutic outcomes.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from ..models.core import Scene, SessionState

logger = logging.getLogger(__name__)


class BranchType(StrEnum):
    """Types of narrative branches."""

    NARRATIVE = "narrative"
    THERAPEUTIC = "therapeutic"
    CHALLENGE = "challenge"
    RELATIONSHIP = "relationship"
    EXPLORATION = "exploration"


class TimelineStatus(StrEnum):
    """Status of a timeline branch."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    LOCKED = "locked"
    DISCOVERED = "discovered"


class ReplayabilitySystem:
    """
    Tracks branch points, alternative paths, and discovery progress
    to support meaningful replayability of therapeutic narratives.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.branch_points: list[dict[str, Any]] = []
        self.timelines: dict[str, dict[str, Any]] = {}
        self.discovery_map: dict[str, bool] = {}

        logger.info("ReplayabilitySystem initialized")

    async def initialize(self) -> bool:
        """Initialize replayability tracking structures."""
        try:
            self.branch_points = []
            self.timelines = {}
            self.discovery_map = {}

            logger.info("ReplayabilitySystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"ReplayabilitySystem initialization failed: {e}")
            return False

    async def register_branch_point(
        self,
        session_state: SessionState,
        scene: Scene,
        choices: list[str],
    ) -> str:
        """
        Register a point where the timeline can branch.

        Args:
            session_state: Current session state
            scene: Scene containing the branch point
            choices: Available choice texts at this point

        Returns:
            Unique branch_id
        """
        try:
            branch_id = str(uuid4())
            branch_type = self._infer_branch_type(scene)

            branch: dict[str, Any] = {
                "branch_id": branch_id,
                "session_id": session_state.session_id,
                "scene_id": scene.scene_id,
                "branch_type": str(branch_type),
                "choices": choices,
                "chosen": None,
                "created_at": datetime.now(UTC).isoformat(),
            }
            self.branch_points.append(branch)

            # Register discovery entries for each choice
            for choice in choices:
                key = f"{branch_id}:{choice}"
                if key not in self.discovery_map:
                    self.discovery_map[key] = False

            logger.info(
                f"Registered branch point {branch_id} with "
                f"{len(choices)} choices in scene {scene.scene_id}"
            )
            return branch_id

        except Exception as e:
            logger.error(f"Branch point registration failed: {e}")
            return ""

    async def explore_alternative_path(
        self, branch_id: str, alternative_choice: str
    ) -> dict[str, Any] | None:
        """
        Explore an alternative path from a previously registered branch.

        Args:
            branch_id: The branch point to revisit
            alternative_choice: The alternative choice to explore

        Returns:
            Description of the alternative path, or None if unavailable
        """
        try:
            branch = next(
                (b for b in self.branch_points if b["branch_id"] == branch_id),
                None,
            )
            if branch is None:
                logger.warning(f"Branch point {branch_id} not found")
                return None

            if alternative_choice not in branch["choices"]:
                logger.warning(
                    f"Choice '{alternative_choice}' not available at branch {branch_id}"
                )
                return None

            # Mark as discovered
            key = f"{branch_id}:{alternative_choice}"
            self.discovery_map[key] = True

            # Create a timeline for this alternative
            timeline_id = str(uuid4())
            self.timelines[timeline_id] = {
                "timeline_id": timeline_id,
                "branch_id": branch_id,
                "choice": alternative_choice,
                "status": str(TimelineStatus.ACTIVE),
                "created_at": datetime.now(UTC).isoformat(),
            }

            logger.info(
                f"Exploring alternative path at branch {branch_id}: "
                f"'{alternative_choice}'"
            )

            return {
                "timeline_id": timeline_id,
                "branch_id": branch_id,
                "branch_type": branch["branch_type"],
                "choice": alternative_choice,
                "scene_id": branch["scene_id"],
                "status": TimelineStatus.ACTIVE,
            }

        except Exception as e:
            logger.error(f"Alternative path exploration failed: {e}")
            return None

    async def get_timeline_summary(self, session_id: str) -> dict[str, Any]:
        """
        Get a summary of all timelines for a session.

        Args:
            session_id: Session identifier

        Returns:
            Summary of timelines, branches, and statuses
        """
        try:
            session_branches = [
                b for b in self.branch_points if b.get("session_id") == session_id
            ]
            session_timeline_ids = {b["branch_id"] for b in session_branches}
            session_timelines = [
                t
                for t in self.timelines.values()
                if t.get("branch_id") in session_timeline_ids
            ]

            summary: dict[str, Any] = {
                "session_id": session_id,
                "total_branch_points": len(session_branches),
                "total_timelines": len(session_timelines),
                "active_timelines": sum(
                    1
                    for t in session_timelines
                    if t.get("status") == TimelineStatus.ACTIVE
                ),
                "completed_timelines": sum(
                    1
                    for t in session_timelines
                    if t.get("status") == TimelineStatus.COMPLETED
                ),
                "discovery_percentage": await self.calculate_discovery_percentage(
                    session_id
                ),
            }

            logger.info(f"Generated timeline summary for session {session_id}")
            return summary

        except Exception as e:
            logger.error(f"Timeline summary generation failed: {e}")
            return {"session_id": session_id, "error": str(e)}

    async def calculate_discovery_percentage(self, session_id: str) -> float:
        """
        Calculate the percentage of content discovered for a session.

        Args:
            session_id: Session identifier

        Returns:
            Discovery percentage (0.0 – 100.0)
        """
        try:
            session_branch_ids = {
                b["branch_id"]
                for b in self.branch_points
                if b.get("session_id") == session_id
            }

            relevant_keys = [
                k for k in self.discovery_map if k.split(":")[0] in session_branch_ids
            ]

            if not relevant_keys:
                return 0.0

            discovered = sum(1 for k in relevant_keys if self.discovery_map[k])
            percentage = (discovered / len(relevant_keys)) * 100.0

            logger.info(
                f"Discovery for session {session_id}: "
                f"{discovered}/{len(relevant_keys)} ({percentage:.1f}%)"
            )
            return round(percentage, 2)

        except Exception as e:
            logger.error(f"Discovery calculation failed: {e}")
            return 0.0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_branch_type(scene: Scene) -> BranchType:
        """Infer the branch type from the scene metadata."""
        if scene.therapeutic_focus:
            return BranchType.THERAPEUTIC
        scene_type_str = str(scene.scene_type)
        if "challenge" in scene_type_str:
            return BranchType.CHALLENGE
        if "exploration" in scene_type_str:
            return BranchType.EXPLORATION
        return BranchType.NARRATIVE
