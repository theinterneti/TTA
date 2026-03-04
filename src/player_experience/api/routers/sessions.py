"""Sessions router: minimal endpoints to support test workflows."""

# Logseq: [[TTA.dev/Player_experience/Api/Routers/Sessions]]

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...managers.world_management_module import WorldManagementModule
from ...services import session_service
from ...uow.session_unit_of_work import AbstractSessionUnitOfWork, DoltSessionUnitOfWork
from ..auth import TokenData, get_current_active_player

router = APIRouter()

# Global world manager instance
_world_manager: WorldManagementModule | None = None


async def get_world_manager() -> WorldManagementModule:
    """Get or create world manager (shared singleton)."""
    global _world_manager  # noqa: PLW0603
    if _world_manager is None:
        _world_manager = WorldManagementModule()
    return _world_manager


def get_session_uow() -> AbstractSessionUnitOfWork:
    """Dependency: provide the real UoW (Dolt → in-memory fallback)."""
    return DoltSessionUnitOfWork()


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
    therapeutic_settings: TherapeuticSettings | None = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    current_player: TokenData = Depends(get_current_active_player),
    world_manager: WorldManagementModule = Depends(get_world_manager),
    uow: AbstractSessionUnitOfWork = Depends(get_session_uow),
) -> dict[str, Any]:
    # Validate world exists
    world = world_manager.get_world_details(request.world_id)
    if world is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"World {request.world_id} not found",
        )

    player_id = getattr(current_player, "player_id", None) or ""
    result = session_service.create_session(
        uow,
        player_id=player_id,
        character_id=request.character_id,
        world_id=request.world_id,
        therapeutic_settings=request.therapeutic_settings.model_dump(),
    )
    return {
        "session_id": result["session_id"],
        "character_id": result["character_id"],
        "world_id": result["world_id"],
        "status": result["status"],
        "created_at": result["created_at"],
    }


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),  # noqa: ARG001
    uow: AbstractSessionUnitOfWork = Depends(get_session_uow),
) -> dict[str, Any]:
    s = session_service.get_session(uow, session_id)
    if s is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return {
        k: v
        for k, v in s.items()
        if k
        in {
            "session_id",
            "character_id",
            "world_id",
            "status",
            "created_at",
            "updated_at",
        }
    }


@router.put("/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_player: TokenData = Depends(get_current_active_player),  # noqa: ARG001
    uow: AbstractSessionUnitOfWork = Depends(get_session_uow),
) -> dict[str, Any]:
    s = session_service.get_session(uow, session_id)
    if s is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    if request.therapeutic_settings is not None:
        s["therapeutic_settings"] = request.therapeutic_settings.model_dump()
    s["updated_at"] = datetime.utcnow().isoformat()
    return {
        k: v
        for k, v in s.items()
        if k
        in {
            "session_id",
            "character_id",
            "world_id",
            "status",
            "created_at",
            "updated_at",
        }
    }


@router.get("/{session_id}/progress")
async def get_session_progress(
    session_id: str,
    current_player: TokenData = Depends(get_current_active_player),  # noqa: ARG001
    uow: AbstractSessionUnitOfWork = Depends(get_session_uow),
) -> dict[str, Any]:
    s = session_service.get_session(uow, session_id)
    if s is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return {
        "session_id": session_id,
        "character_id": s["character_id"],
        "world_id": s["world_id"],
        "progress": {
            "completed_steps": 1,
            "total_steps": 1,
        },
    }
