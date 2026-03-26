"""Unit tests for narrative arc orchestrator helper functions.

Covers paths not exercised by test_narrative_scale_manager_conflicts.py:
- detect_temporal_conflicts / detect_character_conflicts / detect_thematic_conflicts
- apply_resolution
- build_simple_resolution (non-therapeutic branch; therapeutic-reframe branch)
- _is_unsafe / _normalize_topic_values / _get_therapeutic_alignment (via public API)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from src.components.narrative_arc_orchestrator.conflict_detection import (
    detect_character_conflicts,
    detect_temporal_conflicts,
    detect_thematic_conflicts,
    detect_therapeutic_conflicts,
)
from src.components.narrative_arc_orchestrator.models import (
    NarrativeEvent,
    NarrativeScale,
    ScaleConflict,
)
from src.components.narrative_arc_orchestrator.resolution_engine import (
    apply_resolution,
    build_simple_resolution,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event(
    event_id: str,
    scale: NarrativeScale = NarrativeScale.SHORT_TERM,
    *,
    therapeutic_alignment: float = 0.5,
    participants: list[str] | None = None,
    therapeutic_goal: str = "trust",
    safety_level: str = "safe",
    extra_meta: dict | None = None,
) -> NarrativeEvent:
    meta: dict = {
        "therapeutic_alignment": therapeutic_alignment,
        "therapeutic_goal": therapeutic_goal,
        "safety_level": safety_level,
    }
    if extra_meta:
        meta.update(extra_meta)
    return NarrativeEvent(
        event_id=event_id,
        scale=scale,
        timestamp=datetime.now(UTC),
        participants=participants or [],
        description=f"Event {event_id}",
        metadata=meta,
    )


def _conflict(
    conflict_type: str = "temporal",
    recommended_action: str = "narrative_adjustment",
    severity: float = 0.5,
) -> ScaleConflict:
    return ScaleConflict(
        conflict_id=f"c-{uuid.uuid4()}",
        involved_scales={NarrativeScale.SHORT_TERM, NarrativeScale.LONG_TERM},
        conflict_type=conflict_type,
        summary="A test conflict",
        affected_events=["e1", "e2"],
        resolution_priority=2,
        severity=severity,
        metadata={"recommended_action": recommended_action},
    )


# ---------------------------------------------------------------------------
# Placeholder detectors always return []
# ---------------------------------------------------------------------------


def test_detect_temporal_conflicts_returns_empty():
    # Arrange
    events = [
        _event("e1", NarrativeScale.SHORT_TERM),
        _event("e2", NarrativeScale.LONG_TERM),
    ]
    # Act / Assert
    assert detect_temporal_conflicts(events) == []


def test_detect_character_conflicts_returns_empty():
    events = [_event("e1"), _event("e2")]
    assert detect_character_conflicts(events) == []


def test_detect_thematic_conflicts_returns_empty():
    events = [_event("e1"), _event("e2")]
    assert detect_thematic_conflicts(events) == []


def test_placeholder_detectors_accept_empty_list():
    assert detect_temporal_conflicts([]) == []
    assert detect_character_conflicts([]) == []
    assert detect_thematic_conflicts([]) == []


# ---------------------------------------------------------------------------
# detect_therapeutic_conflicts – same-scale events skipped
# ---------------------------------------------------------------------------


def test_detect_therapeutic_conflicts_skips_same_scale_events():
    # Arrange – two events on the same scale; large alignment gap but same scale
    same_scale_events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.95,
            participants=["player"],
            therapeutic_goal="trust",
        ),
        _event(
            "e2",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.05,
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="unsafe",
        ),
    ]
    # Act / Assert – same scale → no conflicts
    assert detect_therapeutic_conflicts(same_scale_events) == []


def test_detect_therapeutic_conflicts_no_conflict_when_gap_small():
    # Arrange – events on different scales, small alignment gap, no unsafe
    events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.7,
            participants=["player"],
            therapeutic_goal="trust",
        ),
        _event(
            "e2",
            NarrativeScale.LONG_TERM,
            therapeutic_alignment=0.6,
            participants=["player"],
            therapeutic_goal="trust",
        ),
    ]
    assert detect_therapeutic_conflicts(events) == []


def test_detect_therapeutic_conflicts_single_event_no_pairs():
    assert detect_therapeutic_conflicts([_event("solo")]) == []


def test_detect_therapeutic_conflicts_unsafe_via_low_alignment():
    """An event with alignment < 0.3 is treated as unsafe even without safety_level."""
    events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.85,
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="safe",
        ),
        _event(
            "e2",
            NarrativeScale.LONG_TERM,
            therapeutic_alignment=0.2,  # < 0.3 → unsafe
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="safe",  # explicit safe but alignment triggers _is_unsafe
        ),
    ]
    conflicts = detect_therapeutic_conflicts(events)
    assert len(conflicts) == 1
    assert conflicts[0].metadata["contains_unsafe_content"] is True
    assert conflicts[0].metadata["recommended_action"] == "safety_stabilization"


def test_detect_therapeutic_conflicts_therapeutic_reframe_when_no_safety():
    """Large gap without unsafe content → therapeutic_reframe action."""
    events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.95,
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="safe",
        ),
        _event(
            "e2",
            NarrativeScale.LONG_TERM,
            therapeutic_alignment=0.4,  # gap = 0.55 ≥ 0.45, but both safe
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="safe",
        ),
    ]
    conflicts = detect_therapeutic_conflicts(events)
    assert len(conflicts) == 1
    assert conflicts[0].metadata["recommended_action"] == "therapeutic_reframe"
    assert conflicts[0].resolution_priority == 2


def test_detect_therapeutic_conflicts_shared_topic_via_therapeutic_theme():
    """Events linked by therapeutic_theme (not goal) should pair."""
    events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=0.9,
            participants=[],
            therapeutic_goal="",
            extra_meta={"therapeutic_theme": "grief"},
        ),
        _event(
            "e2",
            NarrativeScale.MEDIUM_TERM,
            therapeutic_alignment=0.2,
            participants=[],
            therapeutic_goal="",
            extra_meta={"therapeutic_theme": "grief"},
        ),
    ]
    conflicts = detect_therapeutic_conflicts(events)
    assert len(conflicts) == 1


def test_detect_therapeutic_conflicts_severity_clamped_to_one():
    """severity must not exceed 1.0."""
    events = [
        _event(
            "e1",
            NarrativeScale.SHORT_TERM,
            therapeutic_alignment=1.0,
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="unsafe",
        ),
        _event(
            "e2",
            NarrativeScale.LONG_TERM,
            therapeutic_alignment=0.0,
            participants=["player"],
            therapeutic_goal="trust",
            safety_level="unsafe",
        ),
    ]
    conflicts = detect_therapeutic_conflicts(events)
    assert all(c.severity <= 1.0 for c in conflicts)


# ---------------------------------------------------------------------------
# build_simple_resolution – non-therapeutic branch
# ---------------------------------------------------------------------------


def test_build_simple_resolution_non_therapeutic():
    # Arrange
    conflict = _conflict(conflict_type="temporal")

    # Act
    resolution = build_simple_resolution(conflict)

    # Assert
    assert resolution.resolution_type == "narrative_adjustment"
    assert resolution.effectiveness_score == pytest.approx(0.5)
    assert resolution.narrative_cost == pytest.approx(0.1)
    assert resolution.player_impact == pytest.approx(0.1)
    assert resolution.conflict_id == conflict.conflict_id
    assert resolution.metadata["conflict_type"] == "temporal"


def test_build_simple_resolution_therapeutic_reframe():
    # Arrange
    conflict = _conflict(
        conflict_type="therapeutic",
        recommended_action="therapeutic_reframe",
    )

    # Act
    resolution = build_simple_resolution(conflict)

    # Assert
    assert resolution.resolution_type == "therapeutic_reframe"
    assert resolution.effectiveness_score == pytest.approx(0.8)


def test_build_simple_resolution_assigns_unique_ids():
    conflict = _conflict()
    r1 = build_simple_resolution(conflict)
    r2 = build_simple_resolution(conflict)
    assert r1.resolution_id != r2.resolution_id


def test_build_simple_resolution_metadata_contains_affected_events():
    conflict = _conflict()
    resolution = build_simple_resolution(conflict)
    assert resolution.metadata["affected_events"] == list(conflict.affected_events)


# ---------------------------------------------------------------------------
# apply_resolution
# ---------------------------------------------------------------------------


def test_apply_resolution_returns_applied_status():
    # Arrange
    conflict = _conflict(conflict_type="temporal")
    resolution = build_simple_resolution(conflict)

    # Act
    result = apply_resolution(resolution)

    # Assert
    assert result["status"] == "applied"
    assert result["conflict_id"] == resolution.conflict_id


def test_apply_resolution_includes_affected_events():
    conflict = _conflict()
    resolution = build_simple_resolution(conflict)
    result = apply_resolution(resolution)
    assert result["affected_events"] == ["e1", "e2"]


def test_apply_resolution_falls_back_to_resolution_type_when_no_action():
    # Arrange – resolution with no recommended_action in metadata
    conflict = _conflict()
    resolution = build_simple_resolution(conflict)
    del resolution.metadata["recommended_action"]

    # Act
    result = apply_resolution(resolution)

    # Assert: falls back to resolution.resolution_type
    assert result["recommended_action"] == resolution.resolution_type


def test_apply_resolution_uses_recommended_action_from_metadata():
    conflict = _conflict(
        conflict_type="therapeutic",
        recommended_action="safety_stabilization",
    )
    resolution = build_simple_resolution(conflict)
    result = apply_resolution(resolution)
    assert result["recommended_action"] == "safety_stabilization"
