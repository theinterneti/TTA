"""Unit tests for narrative session enrichment service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.player_experience.services.narrative_session_enrichment import (
    enrich_session_payloads,
)


def _make_orchestrator(state: object = None, raises: Exception | None = None):
    orchestrator = MagicMock()
    if raises is not None:
        orchestrator.get_session_state = AsyncMock(side_effect=raises)
    else:
        orchestrator.get_session_state = AsyncMock(return_value=state)
    return orchestrator


@pytest.fixture
def _patch_orchestrator(request):
    """Patch the orchestrator factory; parameterise via indirect fixture."""
    orchestrator = request.param
    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        yield orchestrator


# ---------------------------------------------------------------------------
# Happy-path: sessions without a session_id pass through unchanged
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sessions_without_session_id_are_passed_through():
    # Arrange
    orchestrator = _make_orchestrator(state={})
    sessions = [{"player_id": "p1"}, {"player_id": "p2"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        # Act
        enriched, stats = await enrich_session_payloads(sessions)

    # Assert
    assert enriched == sessions
    assert stats == {"stable_sessions": 0, "strained_sessions": 0}
    orchestrator.get_session_state.assert_not_called()


# ---------------------------------------------------------------------------
# Happy-path: narrative state attached; stable coherence counted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stable_coherence_is_counted_and_attached():
    # Arrange
    state = {
        "arc": "rising",
        "player_signals": {"coherence_status": "stable"},
    }
    orchestrator = _make_orchestrator(state=state)
    sessions = [{"session_id": "s1", "player_id": "p1"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        # Act
        enriched, stats = await enrich_session_payloads(sessions)

    # Assert
    assert enriched[0]["narrative_orchestration"] == state
    assert stats["stable_sessions"] == 1
    assert stats["strained_sessions"] == 0


# ---------------------------------------------------------------------------
# Happy-path: strained coherence counted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_strained_coherence_is_counted():
    # Arrange
    state = {"player_signals": {"coherence_status": "strained"}}
    orchestrator = _make_orchestrator(state=state)
    sessions = [{"session_id": "s2"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        enriched, stats = await enrich_session_payloads(sessions)

    assert enriched[0]["narrative_orchestration"] == state
    assert stats["strained_sessions"] == 1
    assert stats["stable_sessions"] == 0


# ---------------------------------------------------------------------------
# Edge: unknown coherence_status is ignored (neither stable nor strained)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unknown_coherence_status_not_counted():
    # Arrange
    state = {"player_signals": {"coherence_status": "undefined"}}
    orchestrator = _make_orchestrator(state=state)

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        _, stats = await enrich_session_payloads([{"session_id": "s3"}])

    assert stats == {"stable_sessions": 0, "strained_sessions": 0}


# ---------------------------------------------------------------------------
# Edge: orchestrator error → session passed through without enrichment
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_orchestrator_error_is_handled_gracefully():
    # Arrange
    orchestrator = _make_orchestrator(raises=RuntimeError("unavailable"))
    sessions = [{"session_id": "s4", "player_id": "p4"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        enriched, stats = await enrich_session_payloads(sessions)

    # Assert: session present but no narrative_orchestration key
    assert len(enriched) == 1
    assert "narrative_orchestration" not in enriched[0]
    assert stats == {"stable_sessions": 0, "strained_sessions": 0}


# ---------------------------------------------------------------------------
# Edge: empty dict state → no narrative_orchestration key added
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_state_does_not_add_narrative_orchestration():
    # Arrange
    orchestrator = _make_orchestrator(state={})
    sessions = [{"session_id": "s5"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        enriched, _ = await enrich_session_payloads(sessions)

    assert "narrative_orchestration" not in enriched[0]


# ---------------------------------------------------------------------------
# Edge: non-dict state (e.g. None) → no narrative_orchestration key added
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_dict_state_does_not_add_narrative_orchestration():
    # Arrange
    orchestrator = _make_orchestrator(state=None)
    sessions = [{"session_id": "s6"}]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        enriched, _ = await enrich_session_payloads(sessions)

    assert "narrative_orchestration" not in enriched[0]


# ---------------------------------------------------------------------------
# Edge: player_signals is not a dict → coherence not counted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_dict_player_signals_not_counted():
    # Arrange
    state = {"player_signals": "stable"}  # string, not dict
    orchestrator = _make_orchestrator(state=state)

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        _, stats = await enrich_session_payloads([{"session_id": "s7"}])

    assert stats == {"stable_sessions": 0, "strained_sessions": 0}


# ---------------------------------------------------------------------------
# Multi-session: counts accumulate correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multiple_sessions_accumulate_counts():
    # Arrange – two stable, one strained, one no-state
    states = [
        {"player_signals": {"coherence_status": "stable"}},
        {"player_signals": {"coherence_status": "stable"}},
        {"player_signals": {"coherence_status": "strained"}},
        {},
    ]
    call_count = 0

    async def _fake_get_state(_sid: str) -> dict:
        nonlocal call_count
        result = states[call_count]
        call_count += 1
        return result

    orchestrator = MagicMock()
    orchestrator.get_session_state = _fake_get_state
    sessions = [{"session_id": f"s{i}"} for i in range(4)]

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        _, stats = await enrich_session_payloads(sessions)

    assert stats["stable_sessions"] == 2
    assert stats["strained_sessions"] == 1


# ---------------------------------------------------------------------------
# Output: enriched list preserves original keys
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_original_session_keys_are_preserved():
    # Arrange
    state = {"player_signals": {"coherence_status": "stable"}}
    orchestrator = _make_orchestrator(state=state)
    original = {"session_id": "s8", "player_id": "p8", "level": 3}

    with patch(
        "src.player_experience.services.narrative_session_enrichment"
        "._get_narrative_orchestrator",
        return_value=orchestrator,
    ):
        enriched, _ = await enrich_session_payloads([original])

    assert enriched[0]["session_id"] == "s8"
    assert enriched[0]["player_id"] == "p8"
    assert enriched[0]["level"] == 3
