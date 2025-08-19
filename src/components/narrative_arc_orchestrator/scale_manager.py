"""
ScaleManager extracted from narrative_arc_orchestrator_component.
Implements impact assessment, causal maintenance, and conflict resolution.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .models import (
    NarrativeScale,
    PlayerChoice,
    ImpactAssessment,
    NarrativeEvent,
    ScaleConflict,
    Resolution,
)
from .impact_analysis import (
    calculate_base_magnitude,
    identify_affected_elements,
    calculate_causal_strength,
    assess_therapeutic_alignment,
    calculate_confidence_score,
    calculate_temporal_decay,
    create_narrative_event,
    evaluate_cross_scale_influences,
)
from .causal_graph import add_edge, detect_simple_cycles, remove_weak_link
from .conflict_detection import (
    detect_temporal_conflicts,
    detect_character_conflicts,
    detect_thematic_conflicts,
    detect_therapeutic_conflicts,
)
from .resolution_engine import build_simple_resolution

logger = logging.getLogger(__name__)

# Robust event loop policy for test environments
try:
    import asyncio

    class _RobustEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
        def get_event_loop(self):
            try:
                return super().get_event_loop()
            except RuntimeError:
                loop = self.new_event_loop()
                self.set_event_loop(loop)
                return loop

    # Only set policy if not already robust
    current_policy = asyncio.get_event_loop_policy()
    if not isinstance(current_policy, _RobustEventLoopPolicy):
        asyncio.set_event_loop_policy(_RobustEventLoopPolicy())
except Exception:
    # If setting a policy fails, silently continue; tests that use asyncio.run(...) will manage loops
    pass



class ScaleManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scale_windows = {
            NarrativeScale.SHORT_TERM: config.get("short_term_window", 300),
            NarrativeScale.MEDIUM_TERM: config.get("medium_term_window", 86400),
            NarrativeScale.LONG_TERM: config.get("long_term_window", 2592000),
            NarrativeScale.EPIC_TERM: config.get("epic_term_window", 31536000),
        }
        self.active_events: Dict[NarrativeScale, List[NarrativeEvent]] = {scale: [] for scale in NarrativeScale}
        self.causal_graph: Dict[str, Set[str]] = {}
        self.active_conflicts: List[ScaleConflict] = []
        logger.info(f"ScaleManager initialized with windows: {self.scale_windows}")

    async def evaluate_choice_impact(self, choice: PlayerChoice, scales: List[NarrativeScale]) -> Dict[NarrativeScale, ImpactAssessment]:
        try:
            logger.debug(f"Evaluating choice impact across scales: {[s.value for s in scales]}")
            impact_assessments: Dict[NarrativeScale, ImpactAssessment] = {}
            for scale in scales:
                assessment = await self._assess_scale_impact(choice, scale)
                impact_assessments[scale] = assessment
                if assessment.magnitude > 0.3:
                    event = await self._create_narrative_event(choice, scale, assessment)
                    self.active_events[scale].append(event)
            await self._evaluate_cross_scale_influences(impact_assessments)
            return impact_assessments
        except Exception as e:
            logger.error(f"Error evaluating choice impact: {e}")
            return {scale: ImpactAssessment(scale=scale, magnitude=0.0) for scale in scales}

    async def maintain_causal_relationships(self, session_id: str) -> bool:
        try:
            logger.debug(f"Maintaining causal relationships for session {session_id}")
            await self._update_causal_chains()
            consistency_issues = await self._validate_causal_consistency()
            if consistency_issues:
                await self._resolve_causal_issues(consistency_issues)
            await self._cleanup_expired_events()
            return True
        except Exception as e:
            logger.error(f"Error maintaining causal relationships: {e}")
            return False

    async def resolve_scale_conflicts(self, conflicts: List[ScaleConflict]) -> List[Resolution]:
        try:
            logger.info(f"Resolving {len(conflicts)} scale conflicts")
            resolutions: List[Resolution] = []
            sorted_conflicts = sorted(conflicts, key=lambda c: (c.resolution_priority, -c.severity))
            for conflict in sorted_conflicts:
                resolution = await self._generate_conflict_resolution(conflict)
                if resolution:
                    resolutions.append(resolution)
                    await self._implement_resolution(resolution)
            return resolutions
        except Exception as e:
            logger.error(f"Error resolving scale conflicts: {e}")
            return []

    async def detect_scale_conflicts(self, session_id: str) -> List[ScaleConflict]:
        try:
            logger.debug(f"Detecting scale conflicts for session {session_id}")
            conflicts: List[ScaleConflict] = []
            conflicts.extend(await self._detect_temporal_conflicts())
            conflicts.extend(await self._detect_character_conflicts())
            conflicts.extend(await self._detect_thematic_conflicts())
            conflicts.extend(await self._detect_therapeutic_conflicts())
            return conflicts
        except Exception as e:
            logger.error(f"Error detecting scale conflicts: {e}")
            return []

    def get_scale_window(self, scale: NarrativeScale) -> int:
        return self.scale_windows.get(scale, 300)

    def get_active_events(self, scale: Optional[NarrativeScale] = None) -> List[NarrativeEvent]:
        if scale:
            return self.active_events.get(scale, [])
        all_events: List[NarrativeEvent] = []
        for events in self.active_events.values():
            all_events.extend(events)
        return all_events

    # Private helpers extracted
    async def _assess_scale_impact(self, choice: PlayerChoice, scale: NarrativeScale) -> ImpactAssessment:
        base_magnitude = calculate_base_magnitude(choice, scale)
        affected_elements = identify_affected_elements(choice, scale)
        causal_strength = calculate_causal_strength(choice, scale)
        therapeutic_alignment = assess_therapeutic_alignment(choice, scale)
        confidence_score = calculate_confidence_score(choice, scale)
        temporal_decay = calculate_temporal_decay(scale)
        return ImpactAssessment(
            scale=scale,
            magnitude=base_magnitude,
            affected_elements=affected_elements,
            causal_strength=causal_strength,
            therapeutic_alignment=therapeutic_alignment,
            confidence_score=confidence_score,
            temporal_decay=temporal_decay,
        )

    def _calculate_base_magnitude(self, choice: PlayerChoice, scale: NarrativeScale) -> float:
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

    async def _identify_affected_elements(self, choice: PlayerChoice, scale: NarrativeScale) -> List[str]:
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

    async def _calculate_causal_strength(self, choice: PlayerChoice, scale: NarrativeScale) -> float:
        strength = 0.5
        # moved to impact_analysis.calculate_causal_strength
        return await calculate_causal_strength(choice, scale)  # type: ignore[arg-type]

    async def _assess_therapeutic_alignment(self, choice: PlayerChoice, scale: NarrativeScale) -> float:
        align = 0.5
        # moved to impact_analysis.assess_therapeutic_alignment
        return assess_therapeutic_alignment(choice, scale)

    def _calculate_confidence_score(self, choice: PlayerChoice, scale: NarrativeScale) -> float:
        confidence = 0.5
        # moved to impact_analysis.calculate_confidence_score
        return calculate_confidence_score(choice, scale)

    def _calculate_temporal_decay(self, scale: NarrativeScale) -> float:
        decay = {
            NarrativeScale.SHORT_TERM: 0.7,
            NarrativeScale.MEDIUM_TERM: 0.85,
            NarrativeScale.LONG_TERM: 0.95,
            NarrativeScale.EPIC_TERM: 0.99,
        }.get(scale, 0.9)
        # moved to impact_analysis.calculate_temporal_decay
        return calculate_temporal_decay(scale)

    async def _create_narrative_event(self, choice: PlayerChoice, scale: NarrativeScale, assessment: ImpactAssessment) -> NarrativeEvent:
        return create_narrative_event(choice, scale, assessment)

    async def _evaluate_cross_scale_influences(self, assessments: Dict[NarrativeScale, ImpactAssessment]) -> None:
        evaluate_cross_scale_influences(self.active_events, assessments)

    async def _update_causal_chains(self) -> None:
        # Compute causal links between recent events
        all_events = self.get_active_events()
        for i, ev1 in enumerate(all_events):
            for ev2 in all_events[i+1:]:
                if ev1.timestamp <= ev2.timestamp:
                    add_edge(self.causal_graph, ev1.event_id, ev2.event_id)

    async def _validate_causal_consistency(self) -> List[str]:
        return detect_simple_cycles(self.causal_graph)

    async def _resolve_causal_issues(self, issues: List[str]) -> None:
        for issue in issues:
            logger.warning(f"Resolving causal issue: {issue}")
        remove_weak_link(self.causal_graph)

    async def _cleanup_expired_events(self) -> None:
        cutoff_now = datetime.now().timestamp()
        for scale, events in self.active_events.items():
            window = self.get_scale_window(scale)
            cutoff_time = cutoff_now - window
            self.active_events[scale] = [e for e in events if e.timestamp.timestamp() > cutoff_time]

    async def _detect_temporal_conflicts(self) -> List[ScaleConflict]:
        all_events = self.get_active_events()
        return detect_temporal_conflicts(all_events)

    async def _detect_character_conflicts(self) -> List[ScaleConflict]:
        all_events = self.get_active_events()
        return detect_character_conflicts(all_events)

    async def _detect_thematic_conflicts(self) -> List[ScaleConflict]:
        all_events = self.get_active_events()
        return detect_thematic_conflicts(all_events)

    async def _detect_therapeutic_conflicts(self) -> List[ScaleConflict]:
        all_events = self.get_active_events()
        return detect_therapeutic_conflicts(all_events)

    async def _generate_conflict_resolution(self, conflict: ScaleConflict) -> Optional[Resolution]:
        return build_simple_resolution(conflict)

    async def _implement_resolution(self, resolution: Resolution) -> None:
        logger.debug(f"Implementing resolution {resolution.resolution_id}")
        # Placeholder


__all__ = ["ScaleManager"]

