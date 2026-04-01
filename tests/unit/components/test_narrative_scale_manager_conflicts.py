"""Unit tests for narrative scale manager therapeutic conflicts."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.components.narrative_arc_orchestrator.conflict_detection import (
    detect_therapeutic_conflicts,
)
from src.components.narrative_arc_orchestrator.models import (
    NarrativeEvent,
    NarrativeScale,
)
from src.components.narrative_arc_orchestrator.resolution_engine import (
    build_simple_resolution,
)
from src.components.narrative_arc_orchestrator.scale_manager import ScaleManager


def _event(
    event_id: str,
    scale: NarrativeScale,
    *,
    therapeutic_alignment: float,
    participants: list[str],
    therapeutic_goal: str,
    safety_level: str = "safe",
) -> NarrativeEvent:
    return NarrativeEvent(
        event_id=event_id,
        scale=scale,
        timestamp=datetime.now(UTC),
        participants=participants,
        description=f"Event {event_id}",
        metadata={
            "therapeutic_alignment": therapeutic_alignment,
            "therapeutic_goal": therapeutic_goal,
            "safety_level": safety_level,
        },
    )


def test_detect_therapeutic_conflicts_identifies_cross_scale_mismatch() -> None:
    """Large therapeutic divergence across linked events should surface a conflict."""
    # Arrange
    hopeful = _event(
        "e1",
        NarrativeScale.SHORT_TERM,
        therapeutic_alignment=0.92,
        participants=["player", "guide"],
        therapeutic_goal="trust",
    )
    destabilizing = _event(
        "e2",
        NarrativeScale.LONG_TERM,
        therapeutic_alignment=0.18,
        participants=["player", "guide"],
        therapeutic_goal="trust",
        safety_level="unsafe",
    )

    # Act
    conflicts = detect_therapeutic_conflicts([hopeful, destabilizing])

    # Assert
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.conflict_type == "therapeutic"
    assert conflict.affected_events == ["e1", "e2"]
    assert conflict.resolution_priority == 1
    assert conflict.metadata["contains_unsafe_content"] is True
    assert conflict.metadata["recommended_action"] == "safety_stabilization"


def test_detect_therapeutic_conflicts_ignores_unrelated_contexts() -> None:
    """Events without shared therapeutic context should not be paired."""
    # Arrange
    one = _event(
        "e1",
        NarrativeScale.SHORT_TERM,
        therapeutic_alignment=0.95,
        participants=["player"],
        therapeutic_goal="trust",
    )
    two = _event(
        "e2",
        NarrativeScale.LONG_TERM,
        therapeutic_alignment=0.05,
        participants=["mentor"],
        therapeutic_goal="belonging",
        safety_level="unsafe",
    )

    # Act / Assert
    assert detect_therapeutic_conflicts([one, two]) == []


def test_build_simple_resolution_specializes_therapeutic_conflicts() -> None:
    """Therapeutic conflicts should get therapeutic-aware resolution types."""
    # Arrange
    conflict = detect_therapeutic_conflicts(
        [
            _event(
                "e1",
                NarrativeScale.SHORT_TERM,
                therapeutic_alignment=0.85,
                participants=["player"],
                therapeutic_goal="trust",
            ),
            _event(
                "e2",
                NarrativeScale.MEDIUM_TERM,
                therapeutic_alignment=0.15,
                participants=["player"],
                therapeutic_goal="trust",
                safety_level="unsafe",
            ),
        ]
    )[0]

    # Act
    resolution = build_simple_resolution(conflict)

    # Assert
    assert resolution.resolution_type == "safety_stabilization"
    assert resolution.metadata["affected_events"] == ["e1", "e2"]
    assert resolution.effectiveness_score == pytest.approx(0.8)


@pytest.mark.asyncio
async def test_scale_manager_applies_resolution_to_affected_events() -> None:
    """Resolved therapeutic conflicts should annotate affected narrative events."""
    # Arrange
    manager = ScaleManager(config={})
    event_one = _event(
        "e1",
        NarrativeScale.SHORT_TERM,
        therapeutic_alignment=0.88,
        participants=["player", "guide"],
        therapeutic_goal="trust",
    )
    event_two = _event(
        "e2",
        NarrativeScale.EPIC_TERM,
        therapeutic_alignment=0.12,
        participants=["player", "guide"],
        therapeutic_goal="trust",
        safety_level="unsafe",
    )
    manager.active_events[NarrativeScale.SHORT_TERM].append(event_one)
    manager.active_events[NarrativeScale.EPIC_TERM].append(event_two)

    # Act
    conflicts = await manager.detect_scale_conflicts("session-1")
    resolutions = await manager.resolve_scale_conflicts(conflicts)

    # Assert
    assert len(conflicts) == 1
    assert len(resolutions) == 1
    assert manager.active_conflicts == []
    assert event_one.metadata["therapeutic_mitigation"] == "safety_stabilization"
    assert event_two.metadata["therapeutic_mitigation"] == "safety_stabilization"
    assert resolutions[0].resolution_id in event_one.metadata["resolution_ids"]
    assert conflicts[0].conflict_id in event_two.metadata["resolved_conflict_ids"]
