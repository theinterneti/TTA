from datetime import datetime

import pytest

from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.models.enums import SessionStatus, TherapeuticApproach
from src.player_experience.models.session import SessionContext, TherapeuticSettings


@pytest.mark.redis
@pytest.mark.asyncio
async def test_session_repository_redis_cache_roundtrip(redis_client):
    repo = SessionRepository(redis_client=redis_client, neo4j_driver=None)

    ctx = SessionContext(
        session_id="redis_it_session",
        player_id="playerA",
        character_id="char1",
        world_id="world1",
        status=SessionStatus.ACTIVE,
        created_at=datetime.utcnow(),
        last_interaction=datetime.utcnow(),
        interaction_count=0,
        total_duration_minutes=0,
        current_scene_id="scene1",
        session_variables={"mood": "calm"},
        therapeutic_interventions_used=[],
        therapeutic_settings=TherapeuticSettings(
            preferred_approaches=[TherapeuticApproach.CBT],
            intensity_level=0.5,
        ),
    )

    ok = await repo.create_session(ctx)
    assert ok is True

    got = await repo.get_session("redis_it_session")
    assert got is not None
    assert got.player_id == "playerA"

    # Update and re-get
    ctx.session_variables["mood"] = "energized"
    assert await repo.update_session(ctx) is True
    got2 = await repo.get_session("redis_it_session")
    assert got2.session_variables["mood"] == "energized"
