"""
Progress router exposing minimal endpoints for progress visualization and summaries.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import TokenData, get_current_active_player
from ...database.session_repository import SessionRepository
from ...managers.progress_tracking_service import ProgressTrackingService

router = APIRouter()


# Dependency providers

def get_session_repository() -> SessionRepository:
    # For tests, return a fresh repository instance (no external DB by default)
    return SessionRepository()


def get_progress_service(repo: SessionRepository = Depends(get_session_repository)) -> ProgressTrackingService:
    return ProgressTrackingService(repo)


@router.get("/players/{player_id}/progress/viz")
async def get_player_progress_viz(
    player_id: str,
    days: int = Query(14, ge=1, le=60),
    current_player: TokenData = Depends(get_current_active_player),
    service: ProgressTrackingService = Depends(get_progress_service),
) -> Dict[str, Any]:
    # Future: authorize player_id matches current_player.player_id
    viz = await service.get_visualization_data(player_id, days=days)
    return {
        "time_buckets": viz.time_buckets,
        "series": viz.series,
        "meta": viz.meta,
    }

