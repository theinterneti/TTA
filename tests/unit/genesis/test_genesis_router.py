"""
Unit tests for src/player_experience/api/routers/genesis.py
and src/components/genesis/session_store.py.

Coverage:
  Router — start session: success, agent failure
  Router — respond:       success, not found, already complete, agent failure, is_complete
  Router — get status:    success, not found
  Store  — serialisation: roundtrip for all fields (with guide, without guide)
  Store  — persistence:   save/load/delete/exists with in-memory fallback
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.components.gameplay_loop.models.world_seed import (
    GuideCharacter,
    PlayerPosition,
    PowerSource,
    WorldSeed,
    WorldTone,
)
from src.components.genesis.agent import AgentResponse
from src.components.genesis.session_state import Act, GenesisSessionState, Turn
from src.components.genesis.session_store import (
    GenesisSessionStore,
    _state_from_dict,
    _state_to_dict,
)
from src.player_experience.api.routers.genesis import router

pytestmark = pytest.mark.unit

# ── Test fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def app() -> FastAPI:
    """Minimal FastAPI app with the genesis router mounted."""
    application = FastAPI()
    application.include_router(router, prefix="/api/v1/genesis")
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def session_id() -> str:
    return "test-session-123"


@pytest.fixture
def blank_state(session_id: str) -> GenesisSessionState:
    return GenesisSessionState(session_id=session_id)


@pytest.fixture
def guide() -> GuideCharacter:
    return GuideCharacter(
        name="Mira",
        entity_type="human",
        intro_line="Hello, traveller.",
        social_position="edge-dweller",
        relationship_to_player="old friend",
        speech_register="formal",
    )


@pytest.fixture
def world_seed() -> WorldSeed:
    return WorldSeed(
        tone=WorldTone.GETTING_BETTER,
        power_source=PowerSource.NATURE,
        player_position=PlayerPosition.OUTSIDER,
        one_specific_detail="a lighthouse that moves",
    )


@pytest.fixture
def open_agent_response() -> AgentResponse:
    """A mid-session (not complete) AgentResponse."""
    return AgentResponse(
        text="Welcome to the void...",
        act=Act.VOID,
        act_changed=False,
        new_fields={"tone": "hopeful"},
        is_complete=False,
        world_seed=None,
        guide=None,
    )


@pytest.fixture
def complete_agent_response(world_seed: WorldSeed, guide: GuideCharacter) -> AgentResponse:
    """A final (SESSION_BEGUN) AgentResponse."""
    return AgentResponse(
        text="Your world awaits.",
        act=Act.SESSION_BEGUN,
        act_changed=True,
        new_fields={},
        is_complete=True,
        world_seed=world_seed,
        guide=guide,
    )


def _make_mocks(
    state: GenesisSessionState,
    agent_response: AgentResponse,
) -> tuple[MagicMock, MagicMock]:
    """Return (mock_store, mock_agent) pair configured for a test."""
    mock_store = MagicMock()
    mock_store.load = AsyncMock(return_value=state)
    mock_store.save = AsyncMock()

    mock_agent = MagicMock()
    mock_agent.respond = AsyncMock(return_value=agent_response)

    return mock_store, mock_agent


# ── POST / — start session ────────────────────────────────────────────────────


class TestStartGenesisSession:
    def test_start_returns_201_with_session_id(
        self,
        client: TestClient,
        open_agent_response: AgentResponse,
    ) -> None:
        # Arrange
        """Start Genesis Session: start returns 201 with session id."""
        mock_store = MagicMock()
        mock_store.save = AsyncMock()
        mock_agent = MagicMock()
        mock_agent.respond = AsyncMock(return_value=open_agent_response)

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            # Act
            resp = client.post("/api/v1/genesis/")

        # Assert
        assert resp.status_code == 201
        body = resp.json()
        assert "session_id" in body
        assert body["act"] == Act.VOID.value
        assert body["narrator_text"] == open_agent_response.text

    def test_start_stores_session(
        self,
        client: TestClient,
        open_agent_response: AgentResponse,
    ) -> None:
        """Start Genesis Session: start stores session."""
        mock_store = MagicMock()
        mock_store.save = AsyncMock()
        mock_agent = MagicMock()
        mock_agent.respond = AsyncMock(return_value=open_agent_response)

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            client.post("/api/v1/genesis/")

        mock_store.save.assert_awaited_once()

    def test_start_returns_500_on_agent_failure(
        self,
        client: TestClient,
    ) -> None:
        """Start Genesis Session: start returns 500 on agent failure."""
        mock_store = MagicMock()
        mock_store.save = AsyncMock()
        mock_agent = MagicMock()
        mock_agent.respond = AsyncMock(side_effect=RuntimeError("LLM down"))

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            resp = client.post("/api/v1/genesis/")

        assert resp.status_code == 500


# ── POST /{session_id}/respond ────────────────────────────────────────────────


class TestRespondToGenesis:
    def test_respond_success(
        self,
        client: TestClient,
        blank_state: GenesisSessionState,
        open_agent_response: AgentResponse,
    ) -> None:
        """Respond To Genesis: respond success."""
        mock_store, mock_agent = _make_mocks(blank_state, open_agent_response)

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            resp = client.post(
                f"/api/v1/genesis/{blank_state.session_id}/respond",
                json={"player_input": "I want to explore the forest"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["narrator_text"] == open_agent_response.text
        assert body["act"] == Act.VOID.value
        assert body["act_changed"] is False
        assert body["is_complete"] is False
        assert body["world_seed"] is None

    def test_respond_saves_updated_state(
        self,
        client: TestClient,
        blank_state: GenesisSessionState,
        open_agent_response: AgentResponse,
    ) -> None:
        """Respond To Genesis: respond saves updated state."""
        mock_store, mock_agent = _make_mocks(blank_state, open_agent_response)

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            client.post(
                f"/api/v1/genesis/{blank_state.session_id}/respond",
                json={"player_input": "hello"},
            )

        mock_store.save.assert_awaited_once()

    def test_respond_unknown_session_returns_404(
        self,
        client: TestClient,
    ) -> None:
        """Respond To Genesis: respond unknown session returns 404."""
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=None)

        with patch(
            "src.player_experience.api.routers.genesis._get_store", return_value=mock_store
        ):
            resp = client.post(
                "/api/v1/genesis/does-not-exist/respond",
                json={"player_input": "hi"},
            )

        assert resp.status_code == 404

    def test_respond_already_complete_returns_409(
        self,
        client: TestClient,
        session_id: str,
    ) -> None:
        """Respond To Genesis: respond already complete returns 409."""
        complete_state = GenesisSessionState(
            session_id=session_id, act=Act.SESSION_BEGUN
        )
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=complete_state)

        with patch(
            "src.player_experience.api.routers.genesis._get_store", return_value=mock_store
        ):
            resp = client.post(
                f"/api/v1/genesis/{session_id}/respond",
                json={"player_input": "can I still play?"},
            )

        assert resp.status_code == 409

    def test_respond_agent_failure_returns_500(
        self,
        client: TestClient,
        blank_state: GenesisSessionState,
    ) -> None:
        """Respond To Genesis: respond agent failure returns 500."""
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=blank_state)
        mock_store.save = AsyncMock()
        mock_agent = MagicMock()
        mock_agent.respond = AsyncMock(side_effect=RuntimeError("GPU on fire"))

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
        ):
            resp = client.post(
                f"/api/v1/genesis/{blank_state.session_id}/respond",
                json={"player_input": "hello"},
            )

        assert resp.status_code == 500

    def test_respond_complete_includes_world_seed(
        self,
        client: TestClient,
        blank_state: GenesisSessionState,
        complete_agent_response: AgentResponse,
    ) -> None:
        """Respond To Genesis: respond complete includes world seed."""
        mock_store, mock_agent = _make_mocks(blank_state, complete_agent_response)

        with (
            patch("src.player_experience.api.routers.genesis._get_store", return_value=mock_store),
            patch("src.player_experience.api.routers.genesis._get_agent", return_value=mock_agent),
            patch(
                "src.player_experience.api.routers.genesis._publish_world_seed",
                new=AsyncMock(),
            ),
        ):
            resp = client.post(
                f"/api/v1/genesis/{blank_state.session_id}/respond",
                json={"player_input": "let's begin"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_complete"] is True
        assert body["world_seed"] is not None
        assert body["world_seed"]["tone"] == WorldTone.GETTING_BETTER.value

    def test_respond_empty_input_returns_422(
        self,
        client: TestClient,
        session_id: str,
    ) -> None:
        """Respond To Genesis: respond empty input returns 422."""
        resp = client.post(
            f"/api/v1/genesis/{session_id}/respond",
            json={"player_input": ""},
        )
        assert resp.status_code == 422


# ── GET /{session_id} ─────────────────────────────────────────────────────────


class TestGetGenesisSession:
    def test_get_returns_200_with_status(
        self,
        client: TestClient,
        session_id: str,
    ) -> None:
        """Get Genesis Session: get returns 200 with status."""
        state = GenesisSessionState(
            session_id=session_id,
            seed_fields={"tone": "hopeful"},
        )
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=state)

        with patch(
            "src.player_experience.api.routers.genesis._get_store", return_value=mock_store
        ):
            resp = client.get(f"/api/v1/genesis/{session_id}")

        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == session_id
        assert body["act"] == Act.VOID.value
        assert body["total_turns"] == 0
        assert body["seed_fields"]["tone"] == "hopeful"
        assert body["is_complete"] is False
        assert body["guide_introduced"] is False
        assert body["minimum_viable_seed_complete"] is False

    def test_get_unknown_session_returns_404(
        self,
        client: TestClient,
    ) -> None:
        """Get Genesis Session: get unknown session returns 404."""
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=None)

        with patch(
            "src.player_experience.api.routers.genesis._get_store", return_value=mock_store
        ):
            resp = client.get("/api/v1/genesis/ghost-session")

        assert resp.status_code == 404

    def test_get_complete_session_shows_is_complete(
        self,
        client: TestClient,
        session_id: str,
    ) -> None:
        """Get Genesis Session: get complete session shows is complete."""
        state = GenesisSessionState(session_id=session_id, act=Act.SESSION_BEGUN)
        mock_store = MagicMock()
        mock_store.load = AsyncMock(return_value=state)

        with patch(
            "src.player_experience.api.routers.genesis._get_store", return_value=mock_store
        ):
            resp = client.get(f"/api/v1/genesis/{session_id}")

        assert resp.status_code == 200
        assert resp.json()["is_complete"] is True


# ── Session store — serialisation roundtrip ───────────────────────────────────


class TestSessionStoreSerialization:
    def test_roundtrip_minimal_state(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip minimal state."""
        state = GenesisSessionState(session_id=session_id)
        restored = _state_from_dict(_state_to_dict(state))
        assert restored.session_id == session_id
        assert restored.act == Act.VOID
        assert restored.turns == []
        assert restored.seed_fields == {}

    def test_roundtrip_with_turns(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip with turns."""
        state = GenesisSessionState(
            session_id=session_id,
            act=Act.BUILDING_WORLD,
            seed_fields={"tone": "hopeful", "power_source": "natural_forces"},
        )
        turn = Turn(
            turn_number=1,
            act=Act.VOID,
            player_input="Hello",
            agent_response="Welcome...",
            seed_fields_established=["tone"],
            timestamp=datetime.now(UTC),
        )
        state.turns.append(turn)

        restored = _state_from_dict(_state_to_dict(state))
        assert restored.act == Act.BUILDING_WORLD
        assert len(restored.turns) == 1
        assert restored.turns[0].player_input == "Hello"
        assert restored.turns[0].act == Act.VOID

    def test_roundtrip_with_guide_character(
        self, session_id: str, guide: GuideCharacter
    ) -> None:
        """Session Store Serialization: roundtrip with guide character."""
        state = GenesisSessionState(
            session_id=session_id,
            guide_introduced=True,
            guide_character=guide,
        )
        restored = _state_from_dict(_state_to_dict(state))
        assert restored.guide_introduced is True
        assert restored.guide_character is not None
        assert restored.guide_character.name == guide.name
        assert restored.guide_character.entity_type == guide.entity_type

    def test_roundtrip_without_guide_character(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip without guide character."""
        state = GenesisSessionState(session_id=session_id)
        restored = _state_from_dict(_state_to_dict(state))
        assert restored.guide_character is None

    def test_roundtrip_surprise_me_flag(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip surprise me flag."""
        state = GenesisSessionState(session_id=session_id, surprise_me=True)
        restored = _state_from_dict(_state_to_dict(state))
        assert restored.surprise_me is True

    def test_roundtrip_first_light_paragraph(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip first light paragraph."""
        paragraph = "The sky turned amber as you stepped through."
        state = GenesisSessionState(
            session_id=session_id,
            first_light_paragraph=paragraph,
            first_light_confirmed=True,
        )
        restored = _state_from_dict(_state_to_dict(state))
        assert restored.first_light_paragraph == paragraph
        assert restored.first_light_confirmed is True

    def test_roundtrip_preserves_timestamps(self, session_id: str) -> None:
        """Session Store Serialization: roundtrip preserves timestamps."""
        state = GenesisSessionState(session_id=session_id)
        original_created = state.created_at
        restored = _state_from_dict(_state_to_dict(state))
        # Timestamps are timezone-aware; roundtrip must preserve value
        assert restored.created_at == original_created


# ── Session store — in-memory persistence ────────────────────────────────────


class TestGenesisSessionStoreMemory:
    """Tests that exercise the in-memory fallback (no Redis required)."""

    def _force_fallback_store(self) -> GenesisSessionStore:
        store = GenesisSessionStore()
        store._use_fallback = True  # skip Redis connection attempt
        return store

    @pytest.mark.asyncio
    async def test_save_and_load(self, session_id: str) -> None:
        """Genesis Session Store Memory: save and load."""
        store = self._force_fallback_store()
        state = GenesisSessionState(session_id=session_id, surprise_me=True)
        await store.save(state)

        loaded = await store.load(session_id)
        assert loaded is not None
        assert loaded.session_id == session_id
        assert loaded.surprise_me is True

    @pytest.mark.asyncio
    async def test_load_missing_returns_none(self) -> None:
        """Genesis Session Store Memory: load missing returns none."""
        store = self._force_fallback_store()
        result = await store.load("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_removes_session(self, session_id: str) -> None:
        """Genesis Session Store Memory: delete removes session."""
        store = self._force_fallback_store()
        state = GenesisSessionState(session_id=session_id)
        await store.save(state)
        await store.delete(session_id)
        assert await store.load(session_id) is None

    @pytest.mark.asyncio
    async def test_exists_true_after_save(self, session_id: str) -> None:
        """Genesis Session Store Memory: exists true after save."""
        store = self._force_fallback_store()
        state = GenesisSessionState(session_id=session_id)
        await store.save(state)
        assert await store.exists(session_id) is True

    @pytest.mark.asyncio
    async def test_exists_false_before_save(self) -> None:
        """Genesis Session Store Memory: exists false before save."""
        store = self._force_fallback_store()
        assert await store.exists("never-saved") is False

    @pytest.mark.asyncio
    async def test_save_updates_updated_at(self, session_id: str) -> None:
        """Genesis Session Store Memory: save updates updated at."""
        store = self._force_fallback_store()
        state = GenesisSessionState(session_id=session_id)
        original_ts = state.updated_at
        await store.save(state)
        loaded = await store.load(session_id)
        assert loaded is not None
        assert loaded.updated_at >= original_ts

    @pytest.mark.asyncio
    async def test_save_with_guide_character(
        self, session_id: str, guide: GuideCharacter
    ) -> None:
        """Genesis Session Store Memory: save with guide character."""
        store = self._force_fallback_store()
        state = GenesisSessionState(
            session_id=session_id, guide_character=guide, guide_introduced=True
        )
        await store.save(state)
        loaded = await store.load(session_id)
        assert loaded is not None
        assert loaded.guide_character is not None
        assert loaded.guide_character.name == guide.name
