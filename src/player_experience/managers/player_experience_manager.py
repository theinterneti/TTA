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
from datetime import UTC, datetime, timedelta
from typing import Any

from ..database.character_repository import CharacterRepository
from ..database.session_repository import SessionRepository
from ..models.session import PlayerDashboard, Recommendation
from ..services.narrative_session_enrichment import enrich_session_payloads
from ..services.session_store import SessionStore
from .character_avatar_manager import CharacterAvatarManager
from .personalization_service_manager import (
    PersonalizationServiceManager,
    PlayerFeedback,
)
from .progress_tracking_service import ProgressTrackingService
from .session_integration_manager import SessionIntegrationManager

logger = logging.getLogger(__name__)


"""
Central orchestrator for all player experience functionality.

This module will be implemented in Task 10.
"""


class PlayerExperienceManager:
    """Central orchestrator for all player experience functionality."""

    def __init__(
        self,
        session_repository: SessionRepository,
        character_repository: CharacterRepository | None = None,
        personalization_manager: PersonalizationServiceManager | None = None,
        progress_service: ProgressTrackingService | None = None,
        interactive_narrative_engine: Any = None,
    ) -> None:
        self.session_repository = session_repository
        self.character_repository = character_repository or CharacterRepository()
        self.personalization_manager = (
            personalization_manager or PersonalizationServiceManager()
        )
        self.progress_service = progress_service or ProgressTrackingService(
            session_repository
        )
        self.session_manager = SessionIntegrationManager(
            session_repository, interactive_narrative_engine
        )
        logger.info("PlayerExperienceManager initialized")

    async def get_player_dashboard(
        self, player_id: str, *, recent_limit: int = 10
    ) -> PlayerDashboard:
        """Aggregate data to build the player dashboard."""
        # Characters
        characters = self.character_repository.get_characters_by_player(player_id)
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
        recent_sessions = await self.session_repository.get_session_summaries(
            player_id, recent_limit
        )
        total_today = sum(
            s.duration_minutes
            for s in recent_sessions
            if s.start_time.date() == datetime.now(UTC).date()
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
        dashboard.next_recommended_session = datetime.now(UTC) + timedelta(hours=12)
        return dashboard

    async def get_dashboard_api_payload(
        self,
        player_id: str,
        *,
        session_store: SessionStore | None = None,
        character_manager: CharacterAvatarManager | None = None,
        recent_limit: int = 10,
    ) -> dict[str, Any]:
        """Build the API-facing dashboard payload from shared manager logic."""
        try:
            characters = (
                character_manager.get_player_characters(player_id)
                if character_manager is not None
                else []
            )
            active_character_ids = [character.character_id for character in characters]
        except Exception:
            active_character_ids = []

        try:
            recent_sessions = (
                session_store.list_sessions(player_id)[:recent_limit]
                if session_store is not None
                else []
            )
        except Exception:
            recent_sessions = []

        try:
            enriched_sessions, narrative_summary = await enrich_session_payloads(
                recent_sessions
            )
        except Exception:
            enriched_sessions = recent_sessions
            narrative_summary = {"stable_sessions": 0, "strained_sessions": 0}

        try:
            recommendations = [
                self._serialize_recommendation(recommendation)
                for recommendation in await self.get_recommendations(player_id)
            ]
        except Exception:
            recommendations = []

        return {
            "player_id": player_id,
            "active_characters": active_character_ids,
            "recent_sessions": enriched_sessions,
            "session_metrics": {
                "total_count": len(enriched_sessions),
                "narrative_summary": narrative_summary,
            },
            "recommendations": recommendations,
        }

    async def get_session_list_api_payload(
        self,
        player_id: str,
        *,
        session_store: SessionStore | None = None,
        include_narrative: bool = False,
    ) -> dict[str, Any]:
        """Build the API-facing session-list payload from shared manager logic."""
        try:
            sessions = (
                session_store.list_sessions(player_id)
                if session_store is not None
                else []
            )
        except Exception:
            sessions = []

        if not include_narrative:
            return {"sessions": sessions, "count": len(sessions)}

        try:
            enriched_sessions, narrative_summary = await enrich_session_payloads(
                sessions
            )
        except Exception:
            enriched_sessions = sessions
            narrative_summary = {"stable_sessions": 0, "strained_sessions": 0}

        return {
            "sessions": enriched_sessions,
            "count": len(enriched_sessions),
            "narrative_summary": narrative_summary,
        }

    async def get_progress_api_payload(self, player_id: str) -> dict[str, Any]:
        """Build the API-facing progress payload from shared manager logic."""
        summary = await self.progress_service.compute_progress_summary(player_id)
        return {
            "player_id": player_id,
            "total_sessions": summary.engagement_metrics.total_sessions,
            "total_time_minutes": summary.engagement_metrics.total_time_minutes,
            "milestones_achieved": len(summary.milestones_achieved),
            "current_streak_days": summary.engagement_metrics.current_streak_days,
            "therapeutic_momentum": summary.therapeutic_momentum,
            "progress_trend": summary.progress_trend,
            "engagement_trend": summary.engagement_trend,
            "last_updated": summary.last_updated.isoformat(),
        }

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

    def _serialize_recommendation(
        self, recommendation: Recommendation
    ) -> dict[str, Any]:
        """Convert a Recommendation dataclass into a JSON-safe API payload."""
        expires_at = (
            recommendation.expires_at.isoformat()
            if recommendation.expires_at is not None
            else None
        )
        created_at = recommendation.created_at.isoformat()
        return {
            "recommendation_id": recommendation.recommendation_id,
            "title": recommendation.title,
            "description": recommendation.description,
            "recommendation_type": recommendation.recommendation_type,
            "priority": recommendation.priority,
            "target_entity_id": recommendation.target_entity_id,
            "reasoning": recommendation.reasoning,
            "created_at": created_at,
            "expires_at": expires_at,
            "is_dismissed": recommendation.is_dismissed,
        }

    async def process_player_feedback(
        self, player_id: str, feedback: PlayerFeedback
    ) -> dict[str, Any]:
        """Process feedback and adapt experience using personalization manager."""
        adaptation = self.personalization_manager.process_feedback(player_id, feedback)
        # Future: feed adaptation outcomes back into progress markers if needed
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
        return await self.session_manager.create_session(*args, **kwargs)

    async def add_progress_marker(self, *args, **kwargs):
        return await self.session_manager.add_progress_marker(*args, **kwargs)

    async def update_therapeutic_settings(self, *args, **kwargs):
        return await self.session_manager.update_therapeutic_settings(*args, **kwargs)
