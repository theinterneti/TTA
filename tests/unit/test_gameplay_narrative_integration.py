"""Unit tests for gameplay status enrichment with narrative orchestration."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.components.narrative_arc_orchestrator_component import (
    NarrativeArcOrchestratorComponent,
)
from src.integration.gameplay_loop_integration import GameplayLoopIntegration


@pytest.fixture
def narrative_orchestrator() -> NarrativeArcOrchestratorComponent:
    return NarrativeArcOrchestratorComponent(
        {
            "tta.prototype.components.narrative_arc_orchestrator": {
                "emergent_generation": {"probability_threshold": 0.7}
            }
        }
    )


@pytest.fixture
def gameplay_component() -> Mock:
    component = Mock()
    component.create_gameplay_session = AsyncMock(return_value="session-123")
    component.get_user_sessions_for_player = AsyncMock(
        return_value=[
            {
                "session_id": "session-123",
                "user_id": "player-123",
                "is_active": True,
                "current_scene_id": "forest-clearing",
                "emotional_state": "CALM",
                "total_choices": 2,
                "available_choices_count": 2,
                "available_choices": [{"choice_id": "c1", "choice_text": "Breathe"}],
                "therapeutic_engagement": 0.78,
                "last_activity": "2026-03-24T02:00:00+00:00",
            },
            {
                "session_id": "session-456",
                "user_id": "player-123",
                "is_active": False,
                "current_scene_id": "storm-gate",
                "emotional_state": "DISTRESSED",
                "total_choices": 4,
                "available_choices_count": 0,
                "available_choices": [],
                "therapeutic_engagement": 0.32,
                "last_activity": "2026-03-24T01:30:00+00:00",
            },
        ]
    )
    component.pause_session = AsyncMock(return_value=True)
    component.end_session = AsyncMock(return_value=True)
    component.resume_session = AsyncMock(
        return_value={
            "session_id": "session-123",
            "current_scene": {"description": "The path resumes."},
            "available_choices": [{"choice_id": "c3", "choice_text": "Continue"}],
        }
    )
    component.process_user_choice = AsyncMock(
        return_value={
            "next_scene": {"description": "A calmer clearing opens ahead."},
            "available_choices": [{"choice_id": "c2", "choice_text": "Pause"}],
            "consequences": {"therapeutic_insight": "Notice the shift."},
        }
    )
    component.get_session_status = AsyncMock(
        return_value={
            "session_id": "session-123",
            "user_id": "player-123",
            "is_active": True,
            "current_scene_id": "forest-clearing",
            "emotional_state": "CALM",
            "total_choices": 2,
            "available_choices_count": 2,
            "available_choices": [{"choice_id": "c1", "choice_text": "Breathe"}],
            "therapeutic_engagement": 0.78,
            "last_activity": "2026-03-24T02:00:00+00:00",
        }
    )
    return component


@pytest.fixture
def integration(
    gameplay_component: Mock,
    narrative_orchestrator: NarrativeArcOrchestratorComponent,
) -> GameplayLoopIntegration:
    return GameplayLoopIntegration(
        gameplay_component=gameplay_component,
        narrative_orchestrator=narrative_orchestrator,
    )


@pytest.mark.asyncio
async def test_create_authenticated_session_includes_narrative_orchestration(
    integration: GameplayLoopIntegration,
) -> None:
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.create_authenticated_session(
            auth_token="valid-token",
            therapeutic_context={"goals": ["grounding", "self_trust"]},
        )

    assert result["success"] is True
    narrative = result["session_status"]["narrative_orchestration"]
    assert narrative["session_id"] == "session-123"
    assert narrative["interaction_count"] == 2
    assert "goal:grounding" in narrative["active_threads"]
    assert narrative["player_signals"]["coherence_status"] == "stable"


@pytest.mark.asyncio
async def test_get_session_with_auth_includes_narrative_orchestration(
    integration: GameplayLoopIntegration,
) -> None:
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.get_session_with_auth(
            session_id="session-123",
            auth_token="valid-token",
        )

    assert result["success"] is True
    narrative = result["session_status"]["narrative_orchestration"]
    assert narrative["current_scale"] == "short_term"
    assert narrative["therapeutic_alignment"] == 0.78
    assert "scene:forest-clearing" in narrative["active_threads"]


@pytest.mark.asyncio
async def test_get_user_sessions_includes_narrative_summary(
    integration: GameplayLoopIntegration,
) -> None:
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.get_user_sessions(auth_token="valid-token")

    assert result["success"] is True
    sessions = result["session_metrics"]["sessions"]
    assert len(sessions) == 2
    assert "narrative_orchestration" in sessions[0]
    assert result["session_metrics"]["narrative_summary"]["stable_sessions"] == 1
    assert result["session_metrics"]["narrative_summary"]["strained_sessions"] == 1


@pytest.mark.asyncio
async def test_pause_session_with_auth_includes_preserved_narrative_state(
    integration: GameplayLoopIntegration,
) -> None:
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.pause_session_with_auth(
            session_id="session-123",
            auth_token="valid-token",
        )

    assert result["success"] is True
    narrative = result["session_status"]["narrative_orchestration"]
    assert narrative["session_id"] == "session-123"
    assert narrative["player_signals"]["coherence_status"] == "stable"


@pytest.mark.asyncio
async def test_resume_session_with_auth_restores_narrative_state(
    integration: GameplayLoopIntegration,
) -> None:
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.resume_session_with_auth(
            session_id="session-123",
            auth_token="valid-token",
        )

    assert result["success"] is True
    narrative = result["session_data"]["narrative_orchestration"]
    assert narrative["session_id"] == "session-123"
    assert "scene:forest-clearing" in narrative["active_threads"]


@pytest.mark.asyncio
async def test_end_session_with_auth_finalizes_narrative_session(
    integration: GameplayLoopIntegration,
) -> None:
    integration.narrative_orchestrator.finalize_session = AsyncMock(  # type: ignore[method-assign]
        return_value=True
    )
    with patch("src.integration.gameplay_loop_integration.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")

        result = await integration.end_session_with_auth(
            session_id="session-123",
            auth_token="valid-token",
        )

    assert result["success"] is True
    integration.narrative_orchestrator.finalize_session.assert_awaited_once_with(  # type: ignore[union-attr]
        "session-123"
    )
