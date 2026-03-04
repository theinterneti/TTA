"""
# Logseq: [[TTA.dev/Player_experience/Managers/Player_experience_manager]]
Central orchestrator for all player experience functionality (Task 10).

Responsibilities:
- Player dashboard aggregation (characters, sessions, progress, recommendations)
- Recommendation system integration (via PersonalizationServiceManager and ProgressTrackingService)
- Adaptive experience management with feedback processing and crisis integration
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from ..models.session import PlayerDashboard, Recommendation
from ..uow.player_experience_uow import AbstractPlayerExperienceUnitOfWork
from .personalization_service_manager import (
    PersonalizationServiceManager,
    PlayerFeedback,
)
from .progress_tracking_service import ProgressTrackingService
from .session_integration_manager import SessionIntegrationManager

logger = logging.getLogger(__name__)


class PlayerExperienceManager:
    """Central orchestrator for all player experience functionality."""

    def __init__(
        self,
        uow: AbstractPlayerExperienceUnitOfWork,
        personalization_manager: PersonalizationServiceManager | None = None,
        progress_service: ProgressTrackingService | None = None,
        interactive_narrative_engine: Any = None,
    ) -> None:
        self.uow = uow
        self.personalization_manager = (
            personalization_manager or PersonalizationServiceManager()
        )
        self.progress_service = progress_service or ProgressTrackingService(uow.sessions)
        self.session_manager = SessionIntegrationManager(
            uow.sessions, interactive_narrative_engine
        )
        logger.info("PlayerExperienceManager initialized")

    async def get_player_dashboard(
        self, player_id: str, *, recent_limit: int = 10
    ) -> PlayerDashboard:
        """Aggregate data to build the player dashboard."""
        with self.uow:
            # Characters
            characters = self.uow.characters.get_characters_by_player(player_id)
            active_char_summaries: list[dict[str, Any]] = [
                {
                    "character_id": c.character_id,
                    "name": c.name,
                    "last_active": c.last_active,
                    "session_count": c.session_count,
                    "total_session_time": c.total_session_time,
                    "readiness": c.get_therapeutic_readiness(),
                }
                for c in characters
            ]

            # Recent sessions and quick stats
            recent_sessions = await self.uow.sessions.get_session_summaries(
                player_id, recent_limit
            )
            total_today = sum(
                s.duration_minutes
                for s in recent_sessions
                if s.start_time.date() == datetime.utcnow().date()
            )

            # Progress summary/highlights
            progress_summary = await self.progress_service.compute_progress_summary(
                player_id
            )
            highlights = [h.title for h in (progress_summary.recent_highlights or [])]

            # Recommendations
            recs = await self.get_recommendations(player_id)

            dashboard = PlayerDashboard(
                player_id=player_id,
                active_characters=active_char_summaries,
                recent_sessions=recent_sessions,
                progress_highlights=highlights,
                recommendations=recs,
                therapeutic_momentum=progress_summary.therapeutic_momentum,
            )
            dashboard.total_session_time_today = total_today
            dashboard.current_streak_days = (
                progress_summary.engagement_metrics.current_streak_days
            )
            dashboard.most_effective_approach = (
                None  # placeholder until analytics available
            )
            dashboard.next_recommended_session = datetime.utcnow() + timedelta(hours=12)
            return dashboard

    async def get_recommendations(
        self, player_id: str, context: dict[str, Any] | None = None
    ) -> list[Recommendation]:
        """Combine progress-driven and personalization-driven recommendations."""
        # Progress insights
        progress_recs = await self.progress_service.generate_progress_insights(
            player_id
        )
        # Personalization-based
        personal_recs = self.personalization_manager.get_adaptive_recommendations(
            player_id, context=context
        )

        combined = list(progress_recs) + list(personal_recs)
        # Deduplicate by title/type
        seen = set()
        unique: list[Recommendation] = []
        for r in combined:
            key = (r.title, r.recommendation_type)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        # Sort by priority (ascending)
        unique.sort(key=lambda r: r.priority)
        return unique[:8]

    async def process_player_feedback(
        self, player_id: str, feedback: PlayerFeedback
    ) -> dict[str, Any]:
        """Process feedback and adapt experience using personalization manager."""
        adaptation = self.personalization_manager.process_feedback(player_id, feedback)
        return {
            "adaptation_id": adaptation.adaptation_id,
            "changes_made": adaptation.changes_made,
            "confidence": adaptation.confidence_score,
            "requires_player_approval": adaptation.requires_player_approval,
            "reasoning": adaptation.reasoning,
        }

    async def detect_crisis_and_get_resources(
        self, player_id: str, text: str, context: dict[str, Any] | None = None
    ):
        """Proxy to personalization crisis detection and resources retrieval."""
        crisis_detected, crisis_types, resources = (
            self.personalization_manager.detect_crisis_situation(
                player_id, text, context
            )
        )
        return {
            "crisis_detected": crisis_detected,
            "crisis_types": [ct.value for ct in crisis_types],
            "resources": [
                {
                    "resource_id": r.resource_id,
                    "name": r.name,
                    "contact_method": r.contact_method,
                    "contact": r.contact_info,
                    "priority": r.priority,
                    "emergency": r.is_emergency,
                }
                for r in resources
            ],
        }

    # Convenience proxies to session manager (for integration in future tasks)
    async def create_session(self, *args, **kwargs):
        with self.uow:
            result = await self.session_manager.create_session(*args, **kwargs)
            self.uow.commit()
            return result

    async def add_progress_marker(self, *args, **kwargs):
        with self.uow:
            result = await self.session_manager.add_progress_marker(*args, **kwargs)
            self.uow.commit()
            return result

    async def update_therapeutic_settings(self, *args, **kwargs):
        with self.uow:
            result = await self.session_manager.update_therapeutic_settings(*args, **kwargs)
            self.uow.commit()
            return result
