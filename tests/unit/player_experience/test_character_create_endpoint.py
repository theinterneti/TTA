"""
# Logseq: [[TTA/Player_experience/Api/Characters/Create]]
Unit tests for POST /api/v1/characters/create endpoint.

Tests cover:
- Happy path: returns character_id + summary
- World not found → 404
- Missing world_id → 422
- player_prefs forwarded to service
- PlayerCharacter persisted to Neo4j (CREATE called with props)
- Redis session state initialised
- Service failure → 500
- Unauthenticated → 401
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.components.player_character.models import (
    PlayerCharacter,
    PlayerCharacterStatus,
)
from src.player_experience.api.auth import TokenData, get_current_active_player
from src.player_experience.api.routers.characters import (
    get_neo4j_driver,
    get_player_character_service_dep,
    get_redis_client,
    router,
)

# ── Helpers ──────────────────────────────────────────────────────────────────

_PLAYER_ID = "player-test-1"
_WORLD_ID = "world-test-42"
_CHAR_ID = "char-test-99"


class _FakeNode:
    """Minimal Neo4j Node-like object supporting dict() conversion."""

    def __init__(self, props: dict) -> None:
        self._props = props

    def keys(self):
        return list(self._props.keys())

    def __getitem__(self, k: str):
        return self._props[k]

    def __iter__(self):
        return iter(self._props)


class _FakeRecord:
    """Minimal Neo4j Record supporting record["alias"] access."""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __getitem__(self, k: str):
        return self._data[k]


def _make_character(
    player_id: str = _PLAYER_ID,
    world_id: str = _WORLD_ID,
    char_id: str = _CHAR_ID,
) -> PlayerCharacter:
    return PlayerCharacter(
        id=char_id,
        name="Elara",
        world_id=world_id,
        background="A wanderer from the eastern hills.",
        traits=["curious", "adaptable"],
        skills=["foraging", "weather reading"],
        starting_location="The Crossroads",
        status=PlayerCharacterStatus.DRAFT,
        player_id=player_id,
    )


def _make_neo4j_session(*, world_found: bool = True, seed_found: bool = False):
    """Build an async-context Neo4j session mock."""
    world_node = _FakeNode({"id": _WORLD_ID, "name": "Test World"})
    world_record = _FakeRecord({"w": world_node}) if world_found else None

    seed_node = _FakeNode({"id": _WORLD_ID, "world_id": _WORLD_ID, "tone": "hopeful"})
    seed_record = _FakeRecord({"ws": seed_node}) if seed_found else None

    async def _run(query: str, **_kwargs):
        result = AsyncMock()
        if "WorldSeed" in query:
            result.single = AsyncMock(return_value=seed_record)
        elif "MATCH (w:World" in query and "CREATE" not in query:
            result.single = AsyncMock(return_value=world_record)
        else:
            result.single = AsyncMock(return_value=None)
        return result

    session_mock = AsyncMock()
    session_mock.run = _run
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=False)
    return session_mock


def _make_driver(session_mock):
    driver = MagicMock()
    driver.session = MagicMock(return_value=session_mock)
    driver.close = AsyncMock()
    return driver


def _make_redis():
    redis = AsyncMock()
    redis.set = AsyncMock()
    redis.aclose = AsyncMock()
    return redis


def _make_service(character: PlayerCharacter | None = None, *, raise_exc: bool = False):
    svc = MagicMock()
    if raise_exc:
        svc.create_from_seed = AsyncMock(side_effect=RuntimeError("LLM failed"))
    else:
        char = character or _make_character()
        svc.create_from_seed = AsyncMock(return_value=char)
    return svc


def _build_app(
    *,
    player_id: str | None = _PLAYER_ID,
    neo4j_driver=None,
    redis_client=None,
    character_service=None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    if player_id is not None:
        app.dependency_overrides[get_current_active_player] = lambda: TokenData(
            player_id=player_id, username="testuser"
        )
    # else: leave auth to return 401 naturally

    if neo4j_driver is not None:

        async def _neo4j_override():
            yield neo4j_driver

        app.dependency_overrides[get_neo4j_driver] = _neo4j_override
    else:

        async def _no_driver():
            yield None

        app.dependency_overrides[get_neo4j_driver] = _no_driver

    if redis_client is not None:

        async def _redis_override():
            yield redis_client

        app.dependency_overrides[get_redis_client] = _redis_override
    else:

        async def _no_redis():
            yield None

        app.dependency_overrides[get_redis_client] = _no_redis

    if character_service is not None:
        app.dependency_overrides[get_player_character_service_dep] = lambda: (
            character_service
        )

    return TestClient(app, raise_server_exceptions=False)


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestCharacterCreateEndpoint:
    """POST /create endpoint unit tests (all external deps mocked)."""

    def test_happy_path_returns_character_id_and_summary(self):
        char = _make_character()
        session = _make_neo4j_session(world_found=True)
        driver = _make_driver(session)
        redis = _make_redis()
        svc = _make_service(char)

        client = _build_app(
            neo4j_driver=driver,
            redis_client=redis,
            character_service=svc,
        )
        resp = client.post("/create", json={"world_id": _WORLD_ID})

        assert resp.status_code == 201
        body = resp.json()
        assert body["character_id"] == _CHAR_ID
        summary = body["character_summary"]
        assert summary["name"] == "Elara"
        assert "background" in summary
        assert "traits" in summary
        assert "skills" in summary
        assert "starting_location" in summary

    def test_world_not_found_returns_404(self):
        session = _make_neo4j_session(world_found=False)
        driver = _make_driver(session)
        svc = _make_service()

        client = _build_app(neo4j_driver=driver, character_service=svc)
        resp = client.post("/create", json={"world_id": "nonexistent-world"})

        assert resp.status_code == 404

    def test_missing_world_id_returns_422(self):
        client = _build_app()
        resp = client.post("/create", json={})
        assert resp.status_code == 422

    def test_player_prefs_passed_to_service(self):
        char = _make_character()
        session = _make_neo4j_session(world_found=True)
        driver = _make_driver(session)
        redis = _make_redis()
        svc = _make_service(char)

        client = _build_app(
            neo4j_driver=driver, redis_client=redis, character_service=svc
        )
        prefs: dict[str, Any] = {"preferred_name": "Mira", "background_hint": "healer"}
        resp = client.post(
            "/create", json={"world_id": _WORLD_ID, "player_prefs": prefs}
        )

        assert resp.status_code == 201
        call_args = svc.create_from_seed.call_args
        assert call_args is not None
        called_prefs = call_args.kwargs.get("player_prefs") or call_args.args[1]
        assert called_prefs == prefs

    def test_character_persisted_to_neo4j(self):
        char = _make_character()
        queries: list[str] = []

        world_node = _FakeNode({"id": _WORLD_ID, "name": "Test World"})
        world_record = _FakeRecord({"w": world_node})

        async def _tracking_run(query: str, **_kwargs):
            queries.append(query)
            result = AsyncMock()
            if "WorldSeed" in query:
                result.single = AsyncMock(return_value=None)
            elif "MATCH (w:World" in query and "CREATE" not in query:
                result.single = AsyncMock(return_value=world_record)
            else:
                result.single = AsyncMock(return_value=None)
            return result

        session_mock = AsyncMock()
        session_mock.run = _tracking_run
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=False)

        driver = _make_driver(session_mock)
        redis = _make_redis()
        svc = _make_service(char)

        client = _build_app(
            neo4j_driver=driver, redis_client=redis, character_service=svc
        )
        resp = client.post("/create", json={"world_id": _WORLD_ID})

        assert resp.status_code == 201
        create_queries = [q for q in queries if "CREATE (pc:PlayerCharacter" in q]
        assert len(create_queries) >= 1

    def test_redis_session_state_initialized(self):
        char = _make_character()
        session = _make_neo4j_session(world_found=True)
        driver = _make_driver(session)
        redis = _make_redis()
        svc = _make_service(char)

        client = _build_app(
            neo4j_driver=driver, redis_client=redis, character_service=svc
        )
        resp = client.post("/create", json={"world_id": _WORLD_ID})

        assert resp.status_code == 201
        assert redis.set.called
        call_args = redis.set.call_args
        key = call_args.args[0]
        raw_value = call_args.args[1]
        assert key == f"session:init:{_CHAR_ID}"
        state = json.loads(raw_value)
        assert state["player_id"] == _PLAYER_ID
        assert state["world_id"] == _WORLD_ID
        assert state["character_id"] == _CHAR_ID
        assert state["character_name"] == "Elara"
        assert state["tension_level"] == 0.0
        assert state["crisis_level"] == "low"
        assert state["turn_count"] == 0
        # TTL of 3600 expected
        assert call_args.kwargs.get("ex") == 3600

    def test_service_failure_returns_500(self):
        session = _make_neo4j_session(world_found=True)
        driver = _make_driver(session)
        svc = _make_service(raise_exc=True)

        client = _build_app(neo4j_driver=driver, character_service=svc)
        resp = client.post("/create", json={"world_id": _WORLD_ID})

        assert resp.status_code == 500

    def test_unauthenticated_returns_401(self):
        """Endpoint must require authentication."""
        app = FastAPI()
        app.include_router(router)

        async def _no_driver():
            yield None

        async def _no_redis():
            yield None

        app.dependency_overrides[get_neo4j_driver] = _no_driver
        app.dependency_overrides[get_redis_client] = _no_redis
        # Do NOT override get_current_active_player → HTTPBearer returns 403/401
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/create", json={"world_id": _WORLD_ID})
        assert resp.status_code in (401, 403)

    def test_no_neo4j_driver_falls_back_gracefully(self):
        """When Neo4j is unavailable the endpoint still calls the service
        with a minimal seed and does not crash."""
        char = _make_character()
        redis = _make_redis()
        svc = _make_service(char)

        client = _build_app(
            neo4j_driver=None,
            redis_client=redis,
            character_service=svc,
        )
        resp = client.post("/create", json={"world_id": _WORLD_ID})

        # Service is called; Redis state is initialised; response is 201
        assert resp.status_code == 201
        svc.create_from_seed.assert_called_once()
