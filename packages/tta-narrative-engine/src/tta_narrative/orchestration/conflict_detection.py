"""
Conflict detection helpers extracted from ScaleManager.
These are simple, testable utilities for finding cross-scale issues.
"""

from __future__ import annotations

from .models import NarrativeEvent, ScaleConflict


def detect_temporal_conflicts(_all_events: list[NarrativeEvent]) -> list[ScaleConflict]:
    # Placeholder: real logic could compare timestamps and sequences across scales
    return []


def detect_character_conflicts(
    _all_events: list[NarrativeEvent],
) -> list[ScaleConflict]:
    # Placeholder: real logic would group by character and analyze trajectories
    return []


def detect_thematic_conflicts(_all_events: list[NarrativeEvent]) -> list[ScaleConflict]:
    # Placeholder: real logic would inspect metadata/themes
    return []


def detect_therapeutic_conflicts(
    _all_events: list[NarrativeEvent],
) -> list[ScaleConflict]:
    return []


__all__ = [
    "ScaleConflict",
    "detect_temporal_conflicts",
    "detect_character_conflicts",
    "detect_thematic_conflicts",
    "detect_therapeutic_conflicts",
]
