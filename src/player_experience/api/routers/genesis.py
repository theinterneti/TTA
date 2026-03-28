"""
Genesis Session API router.

Endpoints:
    POST   /                       Start a new Genesis Session
    POST   /{session_id}/respond   Submit a player turn
    GET    /{session_id}           Inspect session state

These are the only public entry points into the Genesis Session.  The router
holds a module-level GenesisSessionStore (with Redis fallback) and a
module-level GenesisAgent (stateless — session state is loaded per-request).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.components.genesis.agent import AgentResponse, GenesisAgent
from src.components.genesis.session_state import GenesisSessionState
from src.components.genesis.session_store import GenesisSessionStore

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level singletons — created once, shared across requests
_store: GenesisSessionStore | None = None
_agent: GenesisAgent | None = None


def _get_store() -> GenesisSessionStore:
    global _store
    if _store is None:
        _store = GenesisSessionStore()
    return _store


def _get_agent() -> GenesisAgent:
    global _agent
    if _agent is None:
        _agent = GenesisAgent()
    return _agent


# ── Request / Response models ─────────────────────────────────────────────────


class StartSessionResponse(BaseModel):
    """Returned when a new Genesis Session is created."""

    session_id: str
    act: str
    narrator_text: str
    message: str = "Genesis Session started"


class RespondRequest(BaseModel):
    """Body for submitting a player turn."""

    player_input: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="What the player typed",
    )


class RespondResponse(BaseModel):
    """Returned after a player turn is processed."""

    session_id: str
    act: str
    act_changed: bool
    narrator_text: str
    new_fields: dict[str, Any]
    is_complete: bool
    world_seed: dict[str, Any] | None = None


class SessionStatusResponse(BaseModel):
    """Summary of current session state (read-only)."""

    session_id: str
    act: str
    total_turns: int
    turns_in_current_act: int
    seed_fields: dict[str, Any]
    guide_introduced: bool
    minimum_viable_seed_complete: bool
    is_complete: bool


# ── Helper ────────────────────────────────────────────────────────────────────


async def _load_or_404(session_id: str) -> GenesisSessionState:
    """Load session from store or raise 404."""
    state = await _get_store().load(session_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Genesis session '{session_id}' not found or expired",
        )
    return state


def _agent_response_to_dict(response: AgentResponse, session_id: str) -> dict[str, Any]:
    world_seed_data: dict[str, Any] | None = None
    if response.world_seed is not None:
        world_seed_data = response.world_seed.model_dump()

    return {
        "session_id": session_id,
        "act": response.act.value,
        "act_changed": response.act_changed,
        "narrator_text": response.text,
        "new_fields": response.new_fields,
        "is_complete": response.is_complete,
        "world_seed": world_seed_data,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new Genesis Session",
    description=(
        "Creates a fresh Genesis Session and returns the narrator's opening "
        "monologue.  The returned `session_id` must be included in all "
        "subsequent requests."
    ),
)
async def start_genesis_session() -> StartSessionResponse:
    """Start a new Genesis Session and receive the narrator's opening."""
    session_id = str(uuid.uuid4())
    state = GenesisSessionState(session_id=session_id)

    # Deliver the narrator's opening turn (no player input yet)
    agent = _get_agent()
    try:
        response = await agent.respond(state, player_input="")
    except Exception as exc:
        logger.exception("genesis_router: failed to start session %s", session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start Genesis Session",
        ) from exc

    await _get_store().save(state)

    logger.info("genesis_router: session started session_id=%s", session_id)
    return StartSessionResponse(
        session_id=session_id,
        act=response.act.value,
        narrator_text=response.text,
    )


@router.post(
    "/{session_id}/respond",
    response_model=RespondResponse,
    summary="Submit a player turn",
    description=(
        "Processes the player's input, advances the state machine if needed, "
        "and returns the narrator's response.  When `is_complete` is True, "
        "the `world_seed` field contains the assembled WorldSeed."
    ),
)
async def respond_to_genesis(
    session_id: str,
    body: RespondRequest,
) -> RespondResponse:
    """Submit player input and receive the next narrator response."""
    state = await _load_or_404(session_id)

    from src.components.genesis.session_state import Act

    if state.act == Act.SESSION_BEGUN:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Genesis Session is already complete",
        )

    agent = _get_agent()
    try:
        response = await agent.respond(state, player_input=body.player_input)
    except Exception as exc:
        logger.exception("genesis_router: respond failed session_id=%s", session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process player input",
        ) from exc

    await _get_store().save(state)

    if response.is_complete:
        logger.info(
            "genesis_router: session complete session_id=%s world_seed_assembled=%s",
            session_id,
            response.world_seed is not None,
        )
        await _publish_world_seed(session_id, response)

    return RespondResponse(**_agent_response_to_dict(response, session_id))


@router.get(
    "/{session_id}",
    response_model=SessionStatusResponse,
    summary="Get Genesis Session status",
    description="Returns the current act, seed fields, and turn counts for a session.",
)
async def get_genesis_session(session_id: str) -> SessionStatusResponse:
    """Return read-only status of the Genesis Session."""
    state = await _load_or_404(session_id)

    from src.components.genesis.session_state import Act

    return SessionStatusResponse(
        session_id=session_id,
        act=state.act.value,
        total_turns=state.total_turns,
        turns_in_current_act=state.turns_in_current_act,
        seed_fields=state.seed_fields,
        guide_introduced=state.guide_introduced,
        minimum_viable_seed_complete=state.minimum_viable_seed_complete,
        is_complete=state.act == Act.SESSION_BEGUN,
    )


# ── WorldSeed handoff ─────────────────────────────────────────────────────────


async def _publish_world_seed(session_id: str, response: AgentResponse) -> None:
    """
    Publish the completed WorldSeed to the world-generation pipeline.

    Emits a ``genesis:world_seed_ready`` message on the Redis pub/sub channel
    ``genesis:world_seed_ready`` so downstream world generators can pick it up.

    When Redis is unavailable the event is logged at WARNING level; a separate
    reconnect/retry mechanism can be added later.
    """
    if response.world_seed is None:
        logger.warning(
            "genesis_router: session %s complete but WorldSeed is None — skipping publish",
            session_id,
        )
        return

    payload = {
        "session_id": session_id,
        "world_seed": response.world_seed.model_dump(),
    }

    try:
        import json
        import os

        import redis.asyncio as aioredis  # type: ignore[import-untyped]

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        client = aioredis.from_url(redis_url, decode_responses=True)
        await client.publish("genesis:world_seed_ready", json.dumps(payload))
        await client.aclose()  # type: ignore[union-attr]
        logger.info(
            "genesis_router: WorldSeed published to genesis:world_seed_ready session_id=%s",
            session_id,
        )
    except Exception as exc:
        logger.warning(
            "genesis_router: failed to publish WorldSeed for session %s: %s",
            session_id,
            exc,
        )
