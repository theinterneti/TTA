"""Unit tests for gameplay router narrative-status passthrough."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.player_experience.api.routers.gameplay import (
    get_gameplay_service,
    router,
)


def _make_client(service: Mock) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/gameplay")
    app.dependency_overrides[get_gameplay_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


def test_get_session_status_preserves_narrative_orchestration() -> None:
    service = Mock()
    service.get_session_with_auth = AsyncMock(
        return_value={
            "success": True,
            "session_status": {
                "session_id": "session-123",
                "user_id": "player-123",
                "narrative_orchestration": {
                    "current_scale": "medium_term",
                    "player_signals": {
                        "coherence_status": "stable",
                        "warning_count": 1,
                    },
                },
            },
            "retrieved_at": "2026-03-24T02:00:00+00:00",
        }
    )

    client = _make_client(service)

    with patch("src.player_experience.api.routers.gameplay.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")
        response = client.get(
            "/api/v1/gameplay/sessions/session-123",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["session_status"]["narrative_orchestration"]["current_scale"]
        == "medium_term"
    )
    assert (
        payload["session_status"]["narrative_orchestration"]["player_signals"][
            "coherence_status"
        ]
        == "stable"
    )


def test_get_user_sessions_preserves_narrative_summary() -> None:
    service = Mock()
    service.get_user_sessions = AsyncMock(
        return_value={
            "success": True,
            "user_id": "player-123",
            "session_metrics": {
                "sessions": [
                    {
                        "session_id": "session-123",
                        "narrative_orchestration": {
                            "player_signals": {"coherence_status": "stable"}
                        },
                    }
                ],
                "total_count": 1,
                "narrative_summary": {
                    "stable_sessions": 1,
                    "strained_sessions": 0,
                },
            },
            "retrieved_at": "2026-03-24T02:00:00+00:00",
        }
    )

    client = _make_client(service)

    with patch("src.player_experience.api.routers.gameplay.verify_token") as mock_auth:
        mock_auth.return_value = Mock(player_id="player-123", username="player")
        response = client.get(
            "/api/v1/gameplay/sessions",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_metrics"]["narrative_summary"]["stable_sessions"] == 1
    assert (
        payload["session_metrics"]["sessions"][0]["narrative_orchestration"][
            "player_signals"
        ]["coherence_status"]
        == "stable"
    )
