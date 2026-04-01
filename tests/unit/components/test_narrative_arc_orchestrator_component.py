"""Unit tests for the narrative arc orchestrator runtime slice."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.components.narrative_arc_orchestrator_component import (
    ImpactAssessment,
    NarrativeArcOrchestratorComponent,
    NarrativeResponse,
    NarrativeScale,
    PlayerChoice,
)

pytestmark = pytest.mark.unit


class FakeClosableDependency:
    """Simple dependency with a close hook."""

    def __init__(self, name: str):
        self.name = name
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeSessionPersistenceAdapter:
    """Async session persistence adapter for dependency injection tests."""

    def __init__(self):
        self.saved_states: dict[str, dict[str, object]] = {}
        self.loaded_states: dict[str, dict[str, object]] = {}

    async def save_session_state(
        self, session_id: str, session_data: dict[str, object]
    ) -> bool:
        self.saved_states[session_id] = session_data
        return True

    async def load_session_state(self, session_id: str) -> dict[str, object] | None:
        return self.loaded_states.get(session_id)


@pytest.fixture
def orchestrator() -> NarrativeArcOrchestratorComponent:
    """Create a narrative orchestrator with default test config."""
    config = {
        "tta.prototype.components.narrative_arc_orchestrator": {
            "emergent_generation": {"probability_threshold": 0.7}
        }
    }
    return NarrativeArcOrchestratorComponent(config)


@pytest.mark.asyncio
async def test_get_narrative_status_loads_persisted_session(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Persisted sessions should be loaded before building status."""
    # Arrange
    session_id = "session-status"
    timestamp = datetime(2026, 3, 23, tzinfo=UTC)
    orchestrator._save_session_state(
        session_id,
        {
            "session_id": session_id,
            "created_at": timestamp,
            "last_updated": timestamp,
            "current_scale": NarrativeScale.MEDIUM_TERM.value,
            "active_threads": ["character_arc_progression"],
            "character_arcs": {"guide": "opening_up"},
            "coherence_score": 0.91,
            "therapeutic_alignment": 0.88,
        },
    )

    # Act
    status = await orchestrator.get_narrative_status(session_id)

    # Assert
    assert status is not None
    assert status.current_scale is NarrativeScale.MEDIUM_TERM
    assert status.active_threads == ["character_arc_progression"]
    assert status.character_arcs == {"guide": "opening_up"}
    assert status.coherence_score == pytest.approx(0.91)
    assert status.therapeutic_alignment == pytest.approx(0.88)
    assert status.last_updated == timestamp


@pytest.mark.asyncio
async def test_advance_narrative_scales_updates_and_persists_progress(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Scale advancement should update in-memory and persisted session state."""
    # Arrange
    session_id = "session-advance"
    orchestrator.active_sessions[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now(UTC),
        "last_updated": datetime.now(UTC),
        "active_threads": [],
        "character_arcs": {},
        "coherence_score": 0.8,
        "therapeutic_alignment": 0.7,
        "interaction_count": 0,
        "scale_progression": {},
        "last_scale_advancement": {},
    }

    # Act
    result = await orchestrator.advance_narrative_scales(session_id)

    # Assert
    assert result is True
    session_data = orchestrator.active_sessions[session_id]
    assert session_data["scale_progression"] == {
        NarrativeScale.SHORT_TERM.value: 1,
        NarrativeScale.MEDIUM_TERM.value: 1,
        NarrativeScale.LONG_TERM.value: 1,
        NarrativeScale.EPIC_TERM.value: 1,
    }
    assert session_data["current_scale"] == NarrativeScale.EPIC_TERM.value
    assert session_data["active_threads"] == [
        "immediate_scene",
        "character_arc_progression",
        "world_consequence",
        "legacy_arc",
    ]

    persisted = orchestrator._session_store[session_id]
    assert persisted["scale_progression"] == session_data["scale_progression"]
    assert persisted["current_scale"] == NarrativeScale.EPIC_TERM.value
    assert set(persisted["last_scale_advancement"]) == {
        NarrativeScale.SHORT_TERM.value,
        NarrativeScale.MEDIUM_TERM.value,
        NarrativeScale.LONG_TERM.value,
        NarrativeScale.EPIC_TERM.value,
    }


@pytest.mark.asyncio
async def test_trigger_emergent_event_loads_and_persists_session(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Emergent events should work for persisted sessions and update storage."""
    # Arrange
    session_id = "session-emergent"
    orchestrator._save_session_state(
        session_id,
        {
            "session_id": session_id,
            "created_at": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
            "active_threads": [],
            "character_arcs": {},
            "coherence_score": 0.8,
            "therapeutic_alignment": 0.7,
        },
    )
    orchestrator._calculate_emergent_probability = AsyncMock(return_value=0.9)

    # Act
    event = await orchestrator.trigger_emergent_event(
        session_id, {"recent_events": ["discovery", "memory"]}
    )

    # Assert
    assert event is not None
    assert event.event_type == "character_revelation"
    session_data = orchestrator.active_sessions[session_id]
    assert session_data["active_threads"] == ["emergent:character_revelation"]
    assert session_data["scale_progression"][NarrativeScale.MEDIUM_TERM.value] == 1
    assert len(session_data["emergent_events"]) == 1
    assert session_data["emergent_events"][0]["event_id"] == event.event_id
    assert (
        orchestrator._session_store[session_id]["emergent_events"][0]["event_type"]
        == "character_revelation"
    )
    assert "recent_events" in event.metadata["triggers"]


@pytest.mark.asyncio
async def test_process_player_choice_updates_and_persists_session_state(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Processing a choice should hydrate, update, and persist session state."""
    # Arrange
    session_id = "session-choice"
    orchestrator._save_session_state(
        session_id,
        {
            "session_id": session_id,
            "created_at": datetime.now(UTC),
            "last_updated": datetime.now(UTC),
            "active_threads": [],
            "character_arcs": {},
            "coherence_score": 0.8,
            "therapeutic_alignment": 0.7,
            "interaction_count": 2,
            "engagement_score": 0.4,
        },
    )
    response = NarrativeResponse(
        content="The path opens ahead.",
        session_id=session_id,
        metadata={
            "impact_assessments": {
                NarrativeScale.MEDIUM_TERM.value: {"magnitude": 0.82},
                NarrativeScale.SHORT_TERM.value: {"magnitude": 0.35},
            }
        },
    )
    orchestrator._process_choice_through_systems = AsyncMock(return_value=response)
    choice = PlayerChoice(
        choice_id="choice-1",
        session_id=session_id,
        choice_text="Reach toward the memory shard",
    )

    # Act
    result = await orchestrator.process_player_choice(session_id, choice)

    # Assert
    assert result is response
    session_data = orchestrator.active_sessions[session_id]
    assert session_data["last_choice"] == "Reach toward the memory shard"
    assert session_data["last_response"] == "The path opens ahead."
    assert session_data["interaction_count"] == 3
    assert session_data["engagement_score"] == pytest.approx(0.45)
    assert session_data["current_scale"] == NarrativeScale.MEDIUM_TERM.value

    persisted = orchestrator._session_store[session_id]
    assert persisted["last_choice"] == session_data["last_choice"]
    assert persisted["last_response"] == session_data["last_response"]
    assert persisted["interaction_count"] == 3


def test_start_uses_injected_dependency_adapters_and_stop_closes_them() -> None:
    """Configured dependency adapters should replace placeholders and close cleanly."""
    # Arrange
    neo4j = FakeClosableDependency("neo4j")
    redis = FakeClosableDependency("redis")
    narrative_engine = FakeClosableDependency("narrative")
    orchestrator = NarrativeArcOrchestratorComponent(
        {
            "tta.prototype.components.narrative_arc_orchestrator": {
                "dependency_adapters": {
                    "neo4j": lambda: neo4j,
                    "redis": lambda: redis,
                    "interactive_narrative_engine": lambda: narrative_engine,
                }
            }
        }
    )

    # Act
    assert orchestrator.start() is True
    assert orchestrator.stop() is True

    # Assert
    assert orchestrator.neo4j_connection is None
    assert orchestrator.redis_connection is None
    assert orchestrator.interactive_narrative_engine is None
    assert neo4j.closed is True
    assert redis.closed is True
    assert narrative_engine.closed is True


@pytest.mark.asyncio
async def test_get_narrative_status_loads_from_session_persistence_adapter() -> None:
    """Configured session persistence should be used before in-memory fallback."""
    # Arrange
    adapter = FakeSessionPersistenceAdapter()
    session_id = "adapter-status"
    timestamp = datetime(2026, 3, 24, tzinfo=UTC)
    adapter.loaded_states[session_id] = {
        "session_id": session_id,
        "created_at": timestamp.isoformat(),
        "last_updated": timestamp.isoformat(),
        "current_scale": NarrativeScale.LONG_TERM.value,
        "active_threads": ["world_consequence"],
        "character_arcs": {"guide": "transformed"},
        "coherence_score": 0.93,
        "therapeutic_alignment": 0.81,
    }
    orchestrator = NarrativeArcOrchestratorComponent(
        {
            "tta.prototype.components.narrative_arc_orchestrator": {
                "dependency_adapters": {"session_persistence": adapter}
            }
        }
    )

    # Act
    status = await orchestrator.get_narrative_status(session_id)

    # Assert
    assert status is not None
    assert status.current_scale is NarrativeScale.LONG_TERM
    assert status.active_threads == ["world_consequence"]
    assert status.coherence_score == pytest.approx(0.93)
    assert status.therapeutic_alignment == pytest.approx(0.81)


@pytest.mark.asyncio
async def test_process_player_choice_persists_to_session_adapter() -> None:
    """Choice processing should persist through the configured session adapter."""
    # Arrange
    adapter = FakeSessionPersistenceAdapter()
    session_id = "adapter-choice"
    adapter.loaded_states[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now(UTC).isoformat(),
        "last_updated": datetime.now(UTC).isoformat(),
        "active_threads": [],
        "character_arcs": {},
        "coherence_score": 0.8,
        "therapeutic_alignment": 0.7,
        "interaction_count": 1,
        "engagement_score": 0.4,
    }
    orchestrator = NarrativeArcOrchestratorComponent(
        {
            "tta.prototype.components.narrative_arc_orchestrator": {
                "dependency_adapters": {"session_persistence": adapter}
            }
        }
    )
    response = NarrativeResponse(
        content="The guide steadies the scene.",
        session_id=session_id,
        metadata={
            "impact_assessments": {NarrativeScale.SHORT_TERM.value: {"magnitude": 0.9}}
        },
    )
    orchestrator._process_choice_through_systems = AsyncMock(return_value=response)
    choice = PlayerChoice(
        choice_id="choice-adapter",
        session_id=session_id,
        choice_text="Take a grounding breath",
    )

    # Act
    result = await orchestrator.process_player_choice(session_id, choice)

    # Assert
    assert result is response
    assert session_id in adapter.saved_states
    assert adapter.saved_states[session_id]["last_choice"] == "Take a grounding breath"
    assert adapter.saved_states[session_id]["interaction_count"] == 2


@pytest.mark.asyncio
async def test_process_player_choice_includes_player_signals_metadata(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Processed responses should expose player-facing coherence/safety signals."""
    # Arrange
    session_id = "session-signals"
    orchestrator.active_sessions[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now(UTC),
        "last_updated": datetime.now(UTC),
        "active_threads": [],
        "character_arcs": {},
        "coherence_score": 0.8,
        "therapeutic_alignment": 0.7,
    }

    async def fake_process(
        _session_id: str, _choice: PlayerChoice
    ) -> NarrativeResponse:
        return await NarrativeArcOrchestratorComponent._process_choice_through_systems(
            orchestrator, _session_id, _choice
        )

    orchestrator._generate_next_choices = AsyncMock(return_value=[])
    orchestrator.scale_manager.evaluate_choice_impact = AsyncMock(
        return_value={
            NarrativeScale.SHORT_TERM: type(
                "Assessment",
                (),
                {
                    "magnitude": 0.9,
                    "therapeutic_alignment": 0.25,
                    "confidence_score": 0.7,
                    "causal_strength": 0.4,
                },
            )(),
            NarrativeScale.MEDIUM_TERM: type(
                "Assessment",
                (),
                {
                    "magnitude": 0.4,
                    "therapeutic_alignment": 0.35,
                    "confidence_score": 0.6,
                    "causal_strength": 0.3,
                },
            )(),
        }
    )
    conflict = type(
        "Conflict",
        (),
        {
            "conflict_id": "c1",
            "conflict_type": "therapeutic",
            "resolution_priority": 1,
            "severity": 0.8,
        },
    )()
    orchestrator.scale_manager.detect_scale_conflicts = AsyncMock(
        return_value=[conflict]
    )
    resolution = type("Resolution", (), {"resolution_type": "safety_stabilization"})()
    orchestrator.scale_manager.resolve_scale_conflicts = AsyncMock(
        return_value=[resolution]
    )
    orchestrator.scale_manager.maintain_causal_relationships = AsyncMock(
        return_value=True
    )
    choice = PlayerChoice(
        choice_id="choice-signals",
        session_id=session_id,
        choice_text="Push deeper into the painful memory",
    )

    # Act
    response = await fake_process(session_id, choice)

    # Assert
    assert response.metadata["conflicts_resolved"] == 1
    assert response.metadata["coherence_maintained"] is False
    assert response.metadata["resolution_types"] == ["safety_stabilization"]
    assert response.metadata["player_signals"]["coherence_status"] == "strained"
    assert response.metadata["player_signals"]["warning_count"] == 2
    assert "emotionally unsettled" in response.metadata["player_signals"]["warnings"][1]


@pytest.mark.asyncio
async def test_generate_narrative_response_includes_supportive_warning_note(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """A warning note should appear in visible narrative content when needed."""
    # Arrange
    choice = PlayerChoice(
        choice_id="choice-warning",
        session_id="session-warning",
        choice_text="Force the confrontation",
    )
    assessment = ImpactAssessment(
        scale=NarrativeScale.SHORT_TERM,
        magnitude=0.85,
        therapeutic_alignment=0.2,
        causal_strength=0.2,
    )
    signals = {
        "therapeutic_alignment": 0.2,
        "coherence_status": "strained",
        "highest_impact_scale": NarrativeScale.SHORT_TERM.value,
        "warning_count": 1,
        "warnings": [
            "This moment may feel emotionally unsettled; proceed gently and take your time."
        ],
    }

    # Act
    content = await orchestrator._generate_narrative_response(
        choice,
        {NarrativeScale.SHORT_TERM: assessment},
        signals,
    )

    # Assert
    assert "emotionally unsettled" in content


@pytest.mark.asyncio
async def test_calculate_emergent_probability_uses_context_and_cooldown(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Probability should rise with tension and fall after recent emergent events."""
    # Arrange
    session_id = "emergent-probability"
    orchestrator.active_sessions[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now(UTC),
        "last_updated": datetime.now(UTC),
        "active_threads": ["trust", "memory"],
        "character_arcs": {},
        "coherence_score": 0.8,
        "therapeutic_alignment": 0.35,
        "engagement_score": 0.9,
        "emergent_events": [],
    }

    # Act
    high_probability = await orchestrator._calculate_emergent_probability(
        session_id,
        {
            "recent_events": ["memory fragment", "tense exchange", "world tremor"],
            "unresolved_threads": ["trust", "belonging"],
            "relationship_tension": True,
            "world_state_change": True,
        },
    )
    orchestrator.active_sessions[session_id]["emergent_events"] = [
        {"event_id": "old-1"},
        {"event_id": "old-2"},
    ]
    cooled_probability = await orchestrator._calculate_emergent_probability(
        session_id,
        {
            "recent_events": ["memory fragment", "tense exchange", "world tremor"],
            "unresolved_threads": ["trust", "belonging"],
            "relationship_tension": True,
            "world_state_change": True,
        },
    )

    # Assert
    assert high_probability == pytest.approx(0.87, abs=0.01)
    assert cooled_probability == pytest.approx(0.69, abs=0.01)
    assert cooled_probability < high_probability


@pytest.mark.asyncio
async def test_generate_emergent_event_uses_context_to_choose_type_scale_and_text(
    orchestrator: NarrativeArcOrchestratorComponent,
) -> None:
    """Generated events should reflect the current narrative context."""
    # Arrange
    session_id = "emergent-generation"
    orchestrator.active_sessions[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now(UTC),
        "last_updated": datetime.now(UTC),
        "active_threads": ["storm_front"],
        "character_arcs": {},
        "coherence_score": 0.8,
        "therapeutic_alignment": 0.6,
        "engagement_score": 0.8,
    }

    # Act
    event = await orchestrator._generate_emergent_event(
        session_id,
        {
            "world_state_change": True,
            "participants": ["player", "guide", "city"],
            "recent_events": ["storm warning"],
        },
        0.82,
    )

    # Assert
    assert event.event_type == "world_shift"
    assert event.scale is NarrativeScale.LONG_TERM
    assert event.participants == ["player", "guide", "city"]
    assert "world around you" in event.description
    assert "world_state_change" in event.metadata["triggers"]
