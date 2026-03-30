"""

# Logseq: [[TTA.dev/Packages/Tta-narrative-engine/Src/Tta_narrative/Orchestration/Conflict_detection]]
Conflict detection helpers extracted from ScaleManager.
These are simple, testable utilities for finding cross-scale issues.
"""

from __future__ import annotations

import uuid

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
    all_events: list[NarrativeEvent],
) -> list[ScaleConflict]:
    conflicts: list[ScaleConflict] = []

    for index, left_event in enumerate(all_events):
        for right_event in all_events[index + 1 :]:
            if left_event.scale == right_event.scale:
                continue
            if not _shares_therapeutic_context(left_event, right_event):
                continue

            left_alignment = _get_therapeutic_alignment(left_event)
            right_alignment = _get_therapeutic_alignment(right_event)
            alignment_gap = abs(left_alignment - right_alignment)
            safety_escalation = _is_unsafe(left_event) or _is_unsafe(right_event)

            if alignment_gap < 0.45 and not safety_escalation:
                continue

            affected_events = [left_event.event_id, right_event.event_id]
            priority = 1 if safety_escalation else 2
            severity = min(1.0, max(alignment_gap, 0.7 if safety_escalation else 0.5))
            shared_participants = sorted(
                set(left_event.participants) & set(right_event.participants)
            )
            shared_topics = sorted(_get_therapeutic_topics(left_event, right_event))

            conflicts.append(
                ScaleConflict(
                    conflict_id=f"therapeutic-{uuid.uuid4()}",
                    involved_scales={left_event.scale, right_event.scale},
                    conflict_type="therapeutic",
                    summary=(
                        "Narrative events pull the player in conflicting therapeutic "
                        "directions across scales."
                    ),
                    affected_events=affected_events,
                    resolution_priority=priority,
                    severity=severity,
                    metadata={
                        "alignment_gap": alignment_gap,
                        "contains_unsafe_content": safety_escalation,
                        "shared_participants": shared_participants,
                        "shared_topics": shared_topics,
                        "recommended_action": (
                            "safety_stabilization"
                            if safety_escalation
                            else "therapeutic_reframe"
                        ),
                    },
                )
            )

    return conflicts


def _shares_therapeutic_context(
    left_event: NarrativeEvent, right_event: NarrativeEvent
) -> bool:
    shared_participants = set(left_event.participants) & set(right_event.participants)
    shared_topics = _get_therapeutic_topics(left_event, right_event)
    return bool(shared_participants or shared_topics)


def _get_therapeutic_topics(
    left_event: NarrativeEvent, right_event: NarrativeEvent
) -> set[str]:
    left_topics = _normalize_topic_values(left_event.metadata)
    right_topics = _normalize_topic_values(right_event.metadata)
    return left_topics & right_topics


def _normalize_topic_values(metadata: dict[str, object]) -> set[str]:
    values: set[str] = set()
    for key in ("therapeutic_goal", "therapeutic_theme", "emotional_need"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            values.add(value.strip().lower())
    return values


def _get_therapeutic_alignment(event: NarrativeEvent) -> float:
    alignment = event.metadata.get("therapeutic_alignment")
    if isinstance(alignment, (int, float)):
        return max(0.0, min(1.0, float(alignment)))
    return 0.5


def _is_unsafe(event: NarrativeEvent) -> bool:
    safety_level = event.metadata.get("safety_level")
    if isinstance(safety_level, str) and safety_level.lower() in {
        "unsafe",
        "warning",
        "crisis",
    }:
        return True

    alignment = _get_therapeutic_alignment(event)
    return alignment < 0.3


__all__ = [
    "ScaleConflict",
    "detect_temporal_conflicts",
    "detect_character_conflicts",
    "detect_thematic_conflicts",
    "detect_therapeutic_conflicts",
]
