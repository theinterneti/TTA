"""

# Logseq: [[TTA.dev/Packages/Tta-narrative-engine/Src/Tta_narrative/Orchestration/Resolution_engine]]
Resolution engine helpers.
Utilities to build and apply narrative conflict resolutions.
"""

from __future__ import annotations

import uuid

from .models import Resolution, ScaleConflict


def build_simple_resolution(conflict: ScaleConflict) -> Resolution:
    is_therapeutic_conflict = conflict.conflict_type == "therapeutic"
    recommended_action = conflict.metadata.get("recommended_action", "narrative_adjustment")
    if is_therapeutic_conflict:
        resolution_type = (
            "safety_stabilization"
            if recommended_action == "safety_stabilization"
            else "therapeutic_reframe"
        )
        description = (
            "Reframe the conflicting beats so player-facing content stays "
            "therapeutically aligned across narrative scales."
        )
        effectiveness_score = 0.8
        narrative_cost = 0.15
        player_impact = 0.2
    else:
        resolution_type = "narrative_adjustment"
        description = (
            f"Adjust cross-scale relationships to resolve {conflict.conflict_type}"
        )
        effectiveness_score = 0.5
        narrative_cost = 0.1
        player_impact = 0.1

    return Resolution(
        resolution_id=str(uuid.uuid4()),
        conflict_id=conflict.conflict_id,
        resolution_type=resolution_type,
        description=description,
        effectiveness_score=effectiveness_score,
        narrative_cost=narrative_cost,
        player_impact=player_impact,
        metadata={
            "affected_events": list(conflict.affected_events),
            "recommended_action": recommended_action,
            "conflict_type": conflict.conflict_type,
        },
    )


def apply_resolution(resolution: Resolution) -> dict[str, object]:
    return {
        "status": "applied",
        "conflict_id": resolution.conflict_id,
        "affected_events": list(resolution.metadata.get("affected_events", [])),
        "recommended_action": resolution.metadata.get(
            "recommended_action", resolution.resolution_type
        ),
    }


__all__ = ["Resolution", "build_simple_resolution", "apply_resolution"]
