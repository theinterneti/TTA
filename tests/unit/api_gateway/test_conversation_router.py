"""Unit tests for conversation router narrative-orchestration integration."""

from __future__ import annotations

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers import conversation

pytestmark = pytest.mark.unit


def _make_client() -> TestClient:
    app = FastAPI()
    app.include_router(conversation.router, prefix="/api/v1/conversation")
    app.dependency_overrides[get_current_active_player] = lambda: TokenData(
        player_id="player-123"
    )
    return TestClient(app, raise_server_exceptions=False)


def _reset_conversation_state() -> None:
    conversation._CONVERSATIONS.clear()
    conversation._SESSION_STATES.clear()
    conversation._SESSION_PERSISTENCE = None
    conversation._narrative_orchestrator = None


class TestConversationRouterNarrativeIntegration:
    def setup_method(self) -> None:
        _reset_conversation_state()

    def teardown_method(self) -> None:
        _reset_conversation_state()

    def test_send_message_includes_narrative_orchestration_metadata(
        self, monkeypatch
    ) -> None:
        """Conversation Router Narrative Integration: send message includes narrative orchestration metadata."""
        client = _make_client()

        async def fake_generate_response(_message: str, _context: dict[str, object]):
            return "Take a breath and notice what shifts.", {"source": "test"}

        async def fake_progress_analysis(
            _session_id: str, _user_message: str, _ai_response: str
        ) -> dict[str, object]:
            return {
                "analysis_available": True,
                "engagement_level": 0.74,
                "emotional_progress_score": 0.79,
                "session_quality_score": 0.82,
                "therapeutic_insights": ["Grounding is helping."],
                "recommended_interventions": ["breathing"],
            }

        monkeypatch.setattr(
            conversation.ai_generator,
            "generate_response",
            fake_generate_response,
        )
        monkeypatch.setattr(
            conversation.ai_generator,
            "_analyze_therapeutic_progress",
            fake_progress_analysis,
        )

        response = client.post(
            "/api/v1/conversation/send",
            json={
                "session_id": "session-1",
                "message": "I feel stressed and anxious today",
                "context": {"world_id": "calm-room"},
            },
        )

        assert response.status_code == 200
        payload = response.json()
        narrative = payload["metadata"]["narrative_orchestration"]
        assert narrative["session_id"] == "session-1"
        assert narrative["current_scale"] == "short_term"
        assert narrative["player_signals"]["coherence_status"] == "stable"
        assert narrative["player_signals"]["warning_count"] == 1
        assert (
            "constructive and grounded direction"
            in narrative["player_signals"]["warnings"][0]
        )

    def test_get_session_state_surfaces_narrative_orchestration(
        self, monkeypatch
    ) -> None:
        """Conversation Router Narrative Integration: get session state surfaces narrative orchestration."""
        client = _make_client()

        async def fake_generate_response(_message: str, _context: dict[str, object]):
            return "Let's slow this down together.", {"source": "test"}

        async def fake_progress_analysis(
            _session_id: str, _user_message: str, _ai_response: str
        ) -> dict[str, object]:
            return {
                "analysis_available": True,
                "engagement_level": 0.61,
                "emotional_progress_score": 0.42,
                "session_quality_score": 0.58,
                "therapeutic_insights": [],
                "recommended_interventions": [],
            }

        monkeypatch.setattr(
            conversation.ai_generator,
            "generate_response",
            fake_generate_response,
        )
        monkeypatch.setattr(
            conversation.ai_generator,
            "_analyze_therapeutic_progress",
            fake_progress_analysis,
        )

        send_response = client.post(
            "/api/v1/conversation/send",
            json={
                "session_id": "session-2",
                "message": "I feel down and overwhelmed",
                "context": {"session_goals": ["grounding"]},
            },
        )
        assert send_response.status_code == 200

        state_response = client.get("/api/v1/conversation/session-2/state")
        assert state_response.status_code == 200
        payload = state_response.json()
        narrative = payload["narrative_orchestration"]
        assert narrative["therapeutic_alignment"] == 0.42
        assert narrative["coherence_score"] == 0.58
        assert narrative["player_signals"]["coherence_status"] == "strained"
        assert narrative["player_signals"]["warning_count"] == 2
