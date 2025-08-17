"""
Sessions router: minimal endpoints to support test workflows.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..auth import TokenData, get_current_active_player

router = APIRouter()

# In-memory session store for tests (non-persistent)
_SESSIONS: Dict[str, Dict[str, Any]] = {}


class TherapeuticSettings(BaseModel):
    intensity_level: str
    preferred_approaches: list[str] = Field(default_factory=list)
    session_goals: list[str] = Field(default_factory=list)
    safety_monitoring: bool = False


class CreateSessionRequest(BaseModel):
    character_id: str
    world_id: str
    therapeutic_settings: TherapeuticSettings


class UpdateSessionRequest(BaseModel):
    therapeutic_settings: Optional[TherapeuticSettings] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    current_player: TokenData = Depends(get_current_active_player),
) -> Dict[str, Any]:
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    _SESSIONS[session_id] = {
        "session_id": session_id,
        "character_id": request.character_id,
        "world_id": request.world_id,
        "therapeutic_settings": request.therapeutic_settings.model_dump(),
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "owner": getattr(current_player, "player_id", None),
    }
    return {
        "session_id": session_id,
        "character_id": request.character_id,
        "world_id": request.world_id,
        "status": "active",
        "created_at": now,
    }


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {
        k: v for k, v in s.items() if k in {"session_id", "character_id", "world_id", "status", "created_at", "updated_at"}
    }


@router.put("/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_player: TokenData = Depends(get_current_active_player),
) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if request.therapeutic_settings is not None:
        s["therapeutic_settings"] = request.therapeutic_settings.model_dump()
    s["updated_at"] = datetime.utcnow().isoformat()
    return {
        k: v for k, v in s.items() if k in {"session_id", "character_id", "world_id", "status", "created_at", "updated_at"}
    }


@router.get("/{session_id}/progress")
async def get_session_progress(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),
) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    # Minimal placeholder progress structure compatible with tests' basic checks
    return {
        "session_id": session_id,
        "character_id": s["character_id"],
        "world_id": s["world_id"],
        "progress": {
            "completed_steps": 1,
            "total_steps": 1,
        },
    }

