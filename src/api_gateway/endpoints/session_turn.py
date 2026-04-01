"""

# Logseq: [[TTA.dev/Api_gateway/Endpoints/Session_turn]]
POST /api/session/{session_id}/turn — SSE streaming turn endpoint.

Runs the IPA → WBA → NGA pipeline for one player turn and streams the
narrative response as Server-Sent Events. Reconnection is supported via
the Last-Event-ID header.
"""

from __future__ import annotations

import asyncio
import logging
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..sse import TurnStream

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/session", tags=["session"])
security = HTTPBearer()


class TurnRequest(BaseModel):
    input: str


async def _verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify JWT Bearer token. Returns decoded payload."""
    import jwt  # PyJWT

    try:
        try:
            from src.player_experience.api.config import get_settings

            secret = get_settings().jwt_secret_key
        except Exception:
            secret = os.getenv("SECRET_KEY", "dev-secret")

        payload: dict = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
        )
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


@router.post("/{session_id}/turn")
async def session_turn(
    session_id: str,
    body: TurnRequest,
    request: Request,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    _token_payload: dict = Depends(_verify_jwt),
) -> StreamingResponse:
    """Stream a player turn as Server-Sent Events.

    Event types: token | guide_voice | world_update | crisis_signal | done | error

    Reconnection: pass Last-Event-ID header to replay from that token.
    """
    turn_id = str(uuid4())
    player_id: str = _token_payload.get("player_id", "")
    stream = TurnStream(turn_id=turn_id, session_id=session_id)

    async def _run_pipeline() -> None:
        """Run IPA → WBA → NGA pipeline and enqueue SSE events."""
        try:
            from src.components.ipa.agent import IPAAgent
            from src.components.nga.agent import NGAAgent
            from src.components.wba.agent import WBAAgent

            # Stage 1 — IPA: classify intent and detect emotional tone
            ipa = IPAAgent()
            processed = await ipa.process(
                raw_text=body.input,
                session_id=session_id,
                player_id=player_id,
            )

            # Crisis signal — interrupt stream with safety resources
            if processed.emotional_tone.safety_signal:
                resource_url = "https://988lifeline.org"
                await stream.put_crisis_signal("high", resource_url)
                await stream.put_done(tension_level=1.0)
                return

            # Stage 2 — WBA: assemble world context (degrades to stub without Neo4j)
            wba = WBAAgent()
            world_context = await wba.build(processed)

            # Stage 3 — NGA: generate narrative, stream word by word
            nga = NGAAgent()
            narrative = await nga.generate(
                processed_input=processed,
                world_context=world_context,
            )

            words = narrative.split()
            for i, word in enumerate(words):
                content = word if i == len(words) - 1 else word + " "
                await stream.put_token(content)

            await stream.put_done(tension_level=0.0)

        except Exception as exc:
            logger.exception("Pipeline error for session=%s: %s", session_id, exc)
            await stream.put_error("PIPELINE_ERROR", str(exc))

    # Start pipeline concurrently — client starts receiving tokens immediately
    asyncio.create_task(_run_pipeline())

    return StreamingResponse(
        stream.generate(last_event_id=last_event_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
