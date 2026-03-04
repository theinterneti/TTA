"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Therapeutic_integration_system]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Therapeutic_integration_system]]
Therapeutic Integration System for Therapeutic Text Adventure

This module implements evidence-based therapeutic goal tracking, logging
therapeutic evidence, and generating progress reports to support clinical
outcomes throughout narrative gameplay.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from ..models.core import SessionState
from ..models.interactions import ChoiceOutcome

logger = logging.getLogger(__name__)


class TherapeuticGoalStatus(StrEnum):
    """Status of a therapeutic goal."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIALLY_MET = "partially_met"
    FULLY_MET = "fully_met"
    EXCEEDED = "exceeded"


class EvidenceType(StrEnum):
    """Categories of therapeutic evidence."""

    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    SOCIAL = "social"
    SKILL_BASED = "skill_based"


# Thresholds for status transitions
_STATUS_THRESHOLDS: dict[str, float] = {
    "in_progress": 0.1,
    "partially_met": 0.4,
    "fully_met": 0.8,
    "exceeded": 1.0,
}


class TherapeuticIntegrationSystem:
    """
    Tracks therapeutic goals, logs evidence of progress, and generates
    reports to support evidence-based therapeutic outcomes.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.active_goals: dict[str, dict[str, Any]] = {}
        self.evidence_log: list[dict[str, Any]] = []
        self.therapeutic_frameworks: dict[str, list[str]] = {}

        logger.info("TherapeuticIntegrationSystem initialized")

    async def initialize(self) -> bool:
        """Initialize therapeutic frameworks and default configurations."""
        try:
            self.therapeutic_frameworks = {
                "cbt": [
                    "cognitive_restructuring",
                    "behavioral_activation",
                    "thought_challenging",
                ],
                "dbt": [
                    "distress_tolerance",
                    "emotional_regulation",
                    "interpersonal_effectiveness",
                    "mindfulness",
                ],
                "act": [
                    "acceptance",
                    "cognitive_defusion",
                    "values_clarification",
                    "committed_action",
                ],
                "mindfulness": [
                    "present_awareness",
                    "non_judgmental_observation",
                    "compassion",
                ],
            }

            logger.info("TherapeuticIntegrationSystem initialization completed")
            return True

        except Exception as e:
            logger.error(f"TherapeuticIntegrationSystem initialization failed: {e}")
            return False

    async def set_therapeutic_goals(
        self, session_state: SessionState, goals: list[str]
    ) -> bool:
        """
        Set therapeutic goals for a session.

        Args:
            session_state: Current session state
            goals: List of goal descriptions

        Returns:
            True if goals were set successfully
        """
        try:
            for goal in goals:
                goal_id = f"{session_state.session_id}_{goal[:32].replace(' ', '_')}_{hash(goal) & 0xFFFF:04x}"
                self.active_goals[goal_id] = {
                    "description": goal,
                    "session_id": session_state.session_id,
                    "status": TherapeuticGoalStatus.NOT_STARTED,
                    "progress": 0.0,
                    "evidence_count": 0,
                    "created_at": datetime.now(UTC).isoformat(),
                }

            logger.info(
                f"Set {len(goals)} therapeutic goals for session "
                f"{session_state.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to set therapeutic goals: {e}")
            return False

    async def track_goal_progress(
        self, session_state: SessionState, choice_outcome: ChoiceOutcome
    ) -> dict[str, TherapeuticGoalStatus]:
        """
        Evaluate progress toward therapeutic goals based on a choice outcome.

        Args:
            session_state: Current session state
            choice_outcome: The outcome to evaluate

        Returns:
            Mapping of goal_id to updated status
        """
        try:
            results: dict[str, TherapeuticGoalStatus] = {}
            session_id = session_state.session_id

            for goal_id, goal in self.active_goals.items():
                if goal["session_id"] != session_id:
                    continue

                progress_delta = self._calculate_progress_delta(goal, choice_outcome)
                goal["progress"] = min(goal["progress"] + progress_delta, 1.2)
                goal["status"] = self._status_from_progress(goal["progress"])
                results[goal_id] = TherapeuticGoalStatus(goal["status"])

            logger.info(
                f"Tracked goal progress for session {session_id}: "
                f"{len(results)} goals updated"
            )
            return results

        except Exception as e:
            logger.error(f"Goal progress tracking failed: {e}")
            return {}

    async def log_therapeutic_evidence(
        self,
        session_id: str,
        evidence_type: EvidenceType,
        description: str,
        significance: float,
    ) -> None:
        """
        Log a piece of therapeutic evidence.

        Args:
            session_id: Session identifier
            evidence_type: Category of evidence
            description: What was observed
            significance: How significant (0.0–1.0)
        """
        try:
            entry: dict[str, Any] = {
                "session_id": session_id,
                "evidence_type": str(evidence_type),
                "description": description,
                "significance": max(0.0, min(significance, 1.0)),
                "logged_at": datetime.now(UTC).isoformat(),
            }
            self.evidence_log.append(entry)

            # Increment evidence count for related goals
            for goal in self.active_goals.values():
                if goal["session_id"] == session_id:
                    goal["evidence_count"] = goal.get("evidence_count", 0) + 1

            logger.info(
                f"Logged {evidence_type} evidence for session {session_id}: "
                f"{description[:60]}"
            )

        except Exception as e:
            logger.error(f"Failed to log therapeutic evidence: {e}")

    async def generate_progress_report(
        self, session_state: SessionState
    ) -> dict[str, Any]:
        """
        Generate a comprehensive therapeutic progress report.

        Args:
            session_state: Current session state

        Returns:
            Report with goal statuses, evidence summary, and recommendations
        """
        try:
            session_id = session_state.session_id
            session_goals = {
                gid: g
                for gid, g in self.active_goals.items()
                if g["session_id"] == session_id
            }
            session_evidence = [
                e for e in self.evidence_log if e["session_id"] == session_id
            ]

            goal_summaries: list[dict[str, Any]] = []
            for gid, g in session_goals.items():
                goal_summaries.append(
                    {
                        "goal_id": gid,
                        "description": g["description"],
                        "status": g["status"],
                        "progress": g["progress"],
                        "evidence_count": g["evidence_count"],
                    }
                )

            evidence_by_type: dict[str, int] = {}
            for ev in session_evidence:
                t = ev["evidence_type"]
                evidence_by_type[t] = evidence_by_type.get(t, 0) + 1

            fully_met = sum(
                1
                for g in session_goals.values()
                if g["status"]
                in (TherapeuticGoalStatus.FULLY_MET, TherapeuticGoalStatus.EXCEEDED)
            )
            total = len(session_goals)

            report: dict[str, Any] = {
                "session_id": session_id,
                "goals": goal_summaries,
                "evidence_summary": evidence_by_type,
                "total_evidence_entries": len(session_evidence),
                "goals_met": fully_met,
                "goals_total": total,
                "completion_rate": fully_met / total if total > 0 else 0.0,
                "generated_at": datetime.now(UTC).isoformat(),
            }

            logger.info(
                f"Generated progress report for session {session_id}: "
                f"{fully_met}/{total} goals met"
            )
            return report

        except Exception as e:
            logger.error(f"Progress report generation failed: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_progress_delta(
        goal: dict[str, Any], outcome: ChoiceOutcome
    ) -> float:
        """Derive a progress increment from a choice outcome."""
        delta = 0.0

        if outcome.therapeutic_progress:
            delta += sum(outcome.therapeutic_progress.values()) * 0.15

        if outcome.skills_developed:
            delta += len(outcome.skills_developed) * 0.05

        if outcome.insights_gained:
            delta += len(outcome.insights_gained) * 0.08

        if outcome.outcome_type in ("success", "therapeutic_opportunity"):
            delta += 0.1
        elif outcome.outcome_type == "partial_success":
            delta += 0.05

        return delta

    @staticmethod
    def _status_from_progress(progress: float) -> TherapeuticGoalStatus:
        """Map a numeric progress value to a goal status."""
        if progress >= _STATUS_THRESHOLDS["exceeded"]:
            return TherapeuticGoalStatus.EXCEEDED
        if progress >= _STATUS_THRESHOLDS["fully_met"]:
            return TherapeuticGoalStatus.FULLY_MET
        if progress >= _STATUS_THRESHOLDS["partially_met"]:
            return TherapeuticGoalStatus.PARTIALLY_MET
        if progress >= _STATUS_THRESHOLDS["in_progress"]:
            return TherapeuticGoalStatus.IN_PROGRESS
        return TherapeuticGoalStatus.NOT_STARTED
