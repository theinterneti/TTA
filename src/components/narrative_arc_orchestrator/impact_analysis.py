"""
Impact analysis helpers extracted to a dedicated module.
These functions are used by ScaleManager; they are designed to be pure where possible.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List

from .models import (
    NarrativeScale,
    PlayerChoice,
    ImpactAssessment,
    NarrativeEvent,
)


def calculate_base_magnitude(choice: PlayerChoice, scale: NarrativeScale) -> float:
    scale_multipliers = {
        NarrativeScale.SHORT_TERM: 0.8,
        NarrativeScale.MEDIUM_TERM: 0.5,
        NarrativeScale.LONG_TERM: 0.3,
        NarrativeScale.EPIC_TERM: 0.1,
    }
    base = 0.5
    choice_type = choice.metadata.get("choice_type", "dialogue")
    if choice_type == "major_decision":
        base *= 1.5
    elif choice_type == "character_interaction":
        base *= 1.2
    elif choice_type == "world_action":
        base *= 1.3
    return min(1.0, base * scale_multipliers.get(scale, 0.5))


def identify_affected_elements(choice: PlayerChoice, scale: NarrativeScale) -> List[str]:
    elements: List[str] = []
    if scale == NarrativeScale.SHORT_TERM:
        elements.extend(["current_scene", "immediate_dialogue", "character_mood"])
    elif scale == NarrativeScale.MEDIUM_TERM:
        elements.extend(["character_relationships", "personal_growth", "skill_development"])
    elif scale == NarrativeScale.LONG_TERM:
        elements.extend(["world_state", "faction_relationships", "major_plot_threads"])
    elif scale == NarrativeScale.EPIC_TERM:
        elements.extend(["generational_legacy", "world_history", "cultural_impact"])
    if "character_name" in choice.metadata:
        elements.append(f"character_{choice.metadata['character_name']}")
    if "location" in choice.metadata:
        elements.append(f"location_{choice.metadata['location']}")
    return elements


def calculate_causal_strength(choice: PlayerChoice, scale: NarrativeScale) -> float:
    strength = 0.5
    if "consequences" in choice.metadata:
        strength *= 1.2
    if "risk_level" in choice.metadata:
        try:
            strength *= 1.1 + 0.1 * min(1.0, max(0.0, float(choice.metadata["risk_level"])) )
        except Exception:
            pass
    if scale == NarrativeScale.SHORT_TERM:
        strength *= 1.3
    elif scale == NarrativeScale.MEDIUM_TERM:
        strength *= 1.1
    elif scale == NarrativeScale.LONG_TERM:
        strength *= 0.9
    elif scale == NarrativeScale.EPIC_TERM:
        strength *= 0.6
    return min(1.0, strength)


def assess_therapeutic_alignment(choice: PlayerChoice, scale: NarrativeScale) -> float:
    align = 0.5
    if "therapeutic_theme" in choice.metadata:
        theme = str(choice.metadata["therapeutic_theme"]).lower()
        if theme in {"empathy", "self_reflection", "growth", "healing"}:
            align *= 1.2
        elif theme in {"harm", "trauma", "despair"}:
            align *= 0.8
    if scale in (NarrativeScale.MEDIUM_TERM, NarrativeScale.LONG_TERM):
        align *= 1.1
    return min(1.0, align)


def calculate_confidence_score(choice: PlayerChoice, scale: NarrativeScale) -> float:
    confidence = 0.5
    if "evidence" in choice.metadata:
        confidence *= 1.2
    if "ambiguity" in choice.metadata:
        try:
            confidence *= 1.0 - min(1.0, max(0.0, float(choice.metadata["ambiguity"])) ) * 0.5
        except Exception:
            pass
    return min(1.0, max(0.0, confidence))


def calculate_temporal_decay(scale: NarrativeScale) -> float:
    return {
        NarrativeScale.SHORT_TERM: 0.7,
        NarrativeScale.MEDIUM_TERM: 0.85,
        NarrativeScale.LONG_TERM: 0.95,
        NarrativeScale.EPIC_TERM: 0.99,
    }.get(scale, 0.9)


def create_narrative_event(choice: PlayerChoice, scale: NarrativeScale, assessment: ImpactAssessment) -> NarrativeEvent:
    return NarrativeEvent(
        event_id=str(uuid.uuid4()),
        scale=scale,
        timestamp=datetime.now(),
        causal_links={},
        description=f"Event from choice {choice.choice_id}",
        participants=[choice.metadata.get("character_name", "player")],
        metadata={
            "choice_id": choice.choice_id,
            "impact": assessment.magnitude,
            "affected": assessment.affected_elements,
            "therapeutic_alignment": assessment.therapeutic_alignment,
        },
    )


def evaluate_cross_scale_influences(active_events: Dict[NarrativeScale, List[NarrativeEvent]], assessments: Dict[NarrativeScale, ImpactAssessment]) -> None:
    for scale, assessment in assessments.items():
        if assessment.magnitude > 0.6:
            for other in active_events:
                if other != scale:
                    for ev in active_events[other]:
                        ev.causal_links.setdefault("cross_scale", 0.0)
                        ev.causal_links["cross_scale"] = max(ev.causal_links["cross_scale"], 0.2)


__all__ = [
    "ImpactAssessment",
    "calculate_base_magnitude",
    "identify_affected_elements",
    "calculate_causal_strength",
    "assess_therapeutic_alignment",
    "calculate_confidence_score",
    "calculate_temporal_decay",
    "create_narrative_event",
    "evaluate_cross_scale_influences",
]

