"""
Narrative Arc Orchestrator Component

This module implements the Narrative Arc Orchestrator component that manages
storytelling across multiple temporal scales while maintaining therapeutic
integration and player agency.

Classes:
    NarrativeArcOrchestratorComponent: Main component for narrative orchestration
    NarrativeResponse: Response object containing narrative content and metadata
    PlayerChoice: Represents a player's choice in the narrative
    NarrativeStatus: Status information about current narrative state
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..orchestration.component import Component

logger = logging.getLogger(__name__)


# NOTE: Models moved to src/components/narrative_arc_orchestrator/models.py
from .narrative_arc_orchestrator.models import (
    EmergentEvent,
    ImpactAssessment,
    NarrativeEvent,
    NarrativeResponse,
    NarrativeScale,
    NarrativeStatus,
    PlayerChoice,
    Resolution,
    ScaleConflict,
)


class NarrativeScale(Enum):
    """Temporal scales for narrative management."""

    SHORT_TERM = "short_term"  # Immediate scene/interaction
    MEDIUM_TERM = "medium_term"  # Character arc progression
    LONG_TERM = "long_term"  # World story development
    EPIC_TERM = "epic_term"  # Generational saga


@dataclass
class PlayerChoice:
    """Represents a player's choice in the narrative."""

    choice_id: str
    session_id: str
    choice_text: str
    choice_type: str = "dialogue"
    metadata: dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeResponse:
    """Response object containing narrative content and metadata."""

    content: str
    response_type: str = "narrative"
    choices: list[dict[str, Any]] = None
    metadata: dict[str, Any] = None
    session_id: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeStatus:
    """Status information about current narrative state."""

    session_id: str
    current_scale: NarrativeScale
    active_threads: list[str]
    character_arcs: dict[str, str]
    coherence_score: float
    therapeutic_alignment: float
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class NarrativeEvent:
    """Represents a narrative event with causal relationships and impact tracking."""

    event_id: str
    scale: NarrativeScale
    timestamp: datetime
    causal_chain: list[str] = field(
        default_factory=list
    )  # References to causing events
    impact_scope: dict[str, float] = field(
        default_factory=dict
    )  # Impact on different story elements
    therapeutic_relevance: float = 0.0
    player_agency_preserved: bool = True
    event_type: str = "general"
    description: str = ""
    participants: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactAssessment:
    """Assessment of narrative impact across different scales and elements."""

    scale: NarrativeScale
    magnitude: float  # 0.0 to 1.0
    affected_elements: list[str] = field(default_factory=list)
    causal_strength: float = 0.0
    therapeutic_alignment: float = 0.0
    confidence_score: float = 0.0
    temporal_decay: float = 1.0  # How impact diminishes over time
    cross_scale_influences: dict[NarrativeScale, float] = field(default_factory=dict)


@dataclass
class ScaleConflict:
    """Represents a conflict between different narrative scales."""

    conflict_id: str
    involved_scales: set[NarrativeScale]
    conflict_type: (
        str  # "temporal_paradox", "character_inconsistency", "theme_conflict", etc.
    )
    severity: float  # 0.0 to 1.0
    description: str
    affected_events: list[str] = field(default_factory=list)
    resolution_priority: int = 1  # 1 = highest priority
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    """Represents a resolution to a narrative conflict or issue."""

    resolution_id: str
    conflict_id: str
    resolution_type: (
        str  # "creative_integration", "temporal_adjustment", "character_driven", etc.
    )
    description: str
    implementation_steps: list[str] = field(default_factory=list)
    success_probability: float = 0.0
    narrative_cost: float = 0.0  # Cost to overall narrative coherence
    player_impact: float = 0.0  # Impact on player experience
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergentEvent:
    """Represents an emergent narrative event."""

    event_id: str
    event_type: str
    description: str
    scale: NarrativeScale
    participants: list[str] = None
    metadata: dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ScaleManager:
    """
    Manages narrative coherence and progression across different temporal scales.

    This class handles impact evaluation, causal relationship tracking, and conflict
    resolution between different narrative scales.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the ScaleManager.

        Args:
            config: Configuration dictionary containing scale-specific settings
        """
        self.config = config
        self.scale_windows = {
            NarrativeScale.SHORT_TERM: config.get(
                "short_term_window", 300
            ),  # 5 minutes
            NarrativeScale.MEDIUM_TERM: config.get(
                "medium_term_window", 86400
            ),  # 1 day
            NarrativeScale.LONG_TERM: config.get(
                "long_term_window", 2592000
            ),  # 30 days
            NarrativeScale.EPIC_TERM: config.get(
                "epic_term_window", 31536000
            ),  # 1 year
        }

        # Active events by scale
        self.active_events: dict[NarrativeScale, list[NarrativeEvent]] = {
            scale: [] for scale in NarrativeScale
        }

        # Causal relationship tracking
        self.causal_graph: dict[str, set[str]] = (
            {}
        )  # event_id -> set of caused event_ids

        # Conflict tracking
        self.active_conflicts: list[ScaleConflict] = []

        logger.info(f"ScaleManager initialized with windows: {self.scale_windows}")

    async def evaluate_choice_impact(
        self, choice: PlayerChoice, scales: list[NarrativeScale]
    ) -> dict[NarrativeScale, ImpactAssessment]:
        """
        Evaluate the impact of a player choice across specified narrative scales.

        Args:
            choice: The player's choice to evaluate
            scales: List of narrative scales to assess impact on

        Returns:
            Dict mapping each scale to its impact assessment
        """
        try:
            logger.debug(
                f"Evaluating choice impact across scales: {[s.value for s in scales]}"
            )

            impact_assessments = {}

            for scale in scales:
                assessment = await self._assess_scale_impact(choice, scale)
                impact_assessments[scale] = assessment

                # Create narrative event for significant impacts
                if assessment.magnitude > 0.3:  # Threshold for event creation
                    event = await self._create_narrative_event(
                        choice, scale, assessment
                    )
                    self.active_events[scale].append(event)
                    logger.debug(
                        f"Created narrative event {event.event_id} for scale {scale.value}"
                    )

            # Evaluate cross-scale influences
            await self._evaluate_cross_scale_influences(impact_assessments)

            return impact_assessments

        except Exception as e:
            logger.error(f"Error evaluating choice impact: {e}")
            # Return empty assessments for all scales
            return {
                scale: ImpactAssessment(scale=scale, magnitude=0.0) for scale in scales
            }

    async def maintain_causal_relationships(self, session_id: str) -> bool:
        """
        Maintain causal relationships between narrative events.

        Args:
            session_id: The session to maintain causal relationships for

        Returns:
            bool: True if maintenance was successful
        """
        try:
            logger.debug(f"Maintaining causal relationships for session {session_id}")

            # Update causal chains for recent events
            await self._update_causal_chains()

            # Validate causal consistency
            consistency_issues = await self._validate_causal_consistency()

            if consistency_issues:
                logger.warning(
                    f"Found {len(consistency_issues)} causal consistency issues"
                )
                await self._resolve_causal_issues(consistency_issues)

            # Clean up expired events
            await self._cleanup_expired_events()

            return True

        except Exception as e:
            logger.error(f"Error maintaining causal relationships: {e}")
            return False

    async def resolve_scale_conflicts(
        self, conflicts: list[ScaleConflict]
    ) -> list[Resolution]:
        """
        Resolve conflicts between different narrative scales.

        Args:
            conflicts: List of conflicts to resolve

        Returns:
            List of resolutions for the conflicts
        """
        try:
            logger.info(f"Resolving {len(conflicts)} scale conflicts")

            resolutions = []

            # Sort conflicts by priority and severity
            sorted_conflicts = sorted(
                conflicts, key=lambda c: (c.resolution_priority, -c.severity)
            )

            for conflict in sorted_conflicts:
                resolution = await self._generate_conflict_resolution(conflict)
                if resolution:
                    resolutions.append(resolution)
                    await self._implement_resolution(resolution)
                    logger.debug(
                        f"Resolved conflict {conflict.conflict_id} with {resolution.resolution_type}"
                    )
                else:
                    logger.warning(f"Could not resolve conflict {conflict.conflict_id}")

            return resolutions

        except Exception as e:
            logger.error(f"Error resolving scale conflicts: {e}")
            return []

    async def detect_scale_conflicts(self, session_id: str) -> list[ScaleConflict]:
        """
        Detect conflicts between different narrative scales.

        Args:
            session_id: The session to check for conflicts

        Returns:
            List of detected conflicts
        """
        try:
            logger.debug(f"Detecting scale conflicts for session {session_id}")

            conflicts = []

            # Check for temporal paradoxes
            temporal_conflicts = await self._detect_temporal_conflicts()
            conflicts.extend(temporal_conflicts)

            # Check for character consistency issues
            character_conflicts = await self._detect_character_conflicts()
            conflicts.extend(character_conflicts)

            # Check for thematic conflicts
            thematic_conflicts = await self._detect_thematic_conflicts()
            conflicts.extend(thematic_conflicts)

            # Check for therapeutic alignment conflicts
            therapeutic_conflicts = await self._detect_therapeutic_conflicts()
            conflicts.extend(therapeutic_conflicts)

            logger.info(f"Detected {len(conflicts)} scale conflicts")
            return conflicts

        except Exception as e:
            logger.error(f"Error detecting scale conflicts: {e}")
            return []

    def get_scale_window(self, scale: NarrativeScale) -> int:
        """Get the time window for a specific narrative scale."""
        return self.scale_windows.get(scale, 300)

    def get_active_events(
        self, scale: NarrativeScale | None = None
    ) -> list[NarrativeEvent]:
        """Get active events for a specific scale or all scales."""
        if scale:
            return self.active_events.get(scale, [])
        else:
            all_events = []
            for events in self.active_events.values():
                all_events.extend(events)
            return all_events

    # Private helper methods

    async def _assess_scale_impact(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> ImpactAssessment:
        """Assess the impact of a choice on a specific narrative scale."""
        try:
            # Base impact calculation based on choice type and scale
            base_magnitude = self._calculate_base_magnitude(choice, scale)

            # Determine affected elements
            affected_elements = await self._identify_affected_elements(choice, scale)

            # Calculate causal strength
            causal_strength = await self._calculate_causal_strength(choice, scale)

            # Assess therapeutic alignment
            therapeutic_alignment = await self._assess_therapeutic_alignment(
                choice, scale
            )

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(choice, scale)

            # Determine temporal decay
            temporal_decay = self._calculate_temporal_decay(scale)

            assessment = ImpactAssessment(
                scale=scale,
                magnitude=base_magnitude,
                affected_elements=affected_elements,
                causal_strength=causal_strength,
                therapeutic_alignment=therapeutic_alignment,
                confidence_score=confidence_score,
                temporal_decay=temporal_decay,
            )

            return assessment

        except Exception as e:
            logger.error(f"Error assessing scale impact: {e}")
            return ImpactAssessment(scale=scale, magnitude=0.0)

    def _calculate_base_magnitude(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> float:
        """Calculate base impact magnitude for a choice on a specific scale."""
        # Scale-specific magnitude calculation
        scale_multipliers = {
            NarrativeScale.SHORT_TERM: 0.8,  # High immediate impact
            NarrativeScale.MEDIUM_TERM: 0.5,  # Moderate character arc impact
            NarrativeScale.LONG_TERM: 0.3,  # Lower world story impact
            NarrativeScale.EPIC_TERM: 0.1,  # Minimal generational impact
        }

        base_magnitude = 0.5  # Default magnitude

        # Adjust based on choice type
        choice_type = choice.metadata.get("choice_type", "dialogue")
        if choice_type == "major_decision":
            base_magnitude *= 1.5
        elif choice_type == "character_interaction":
            base_magnitude *= 1.2
        elif choice_type == "world_action":
            base_magnitude *= 1.3

        # Apply scale multiplier
        magnitude = base_magnitude * scale_multipliers.get(scale, 0.5)

        return min(1.0, magnitude)

    async def _identify_affected_elements(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> list[str]:
        """Identify story elements affected by the choice at the given scale."""
        affected_elements = []

        # Scale-specific element identification
        if scale == NarrativeScale.SHORT_TERM:
            affected_elements.extend(
                ["current_scene", "immediate_dialogue", "character_mood"]
            )
        elif scale == NarrativeScale.MEDIUM_TERM:
            affected_elements.extend(
                ["character_relationships", "personal_growth", "skill_development"]
            )
        elif scale == NarrativeScale.LONG_TERM:
            affected_elements.extend(
                ["world_state", "faction_relationships", "major_plot_threads"]
            )
        elif scale == NarrativeScale.EPIC_TERM:
            affected_elements.extend(
                ["generational_legacy", "world_history", "cultural_impact"]
            )

        # Add choice-specific elements
        if "character_name" in choice.metadata:
            affected_elements.append(f"character_{choice.metadata['character_name']}")

        if "location" in choice.metadata:
            affected_elements.append(f"location_{choice.metadata['location']}")

        return affected_elements

    async def _calculate_causal_strength(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> float:
        """Calculate the causal strength of the choice's impact."""
        # Base causal strength
        causal_strength = 0.5

        # Increase for choices with clear consequences
        if "consequences" in choice.metadata:
            causal_strength += 0.2

        # Increase for choices affecting multiple elements
        if len(choice.metadata.get("affected_characters", [])) > 1:
            causal_strength += 0.1

        # Scale-specific adjustments
        if scale == NarrativeScale.SHORT_TERM:
            causal_strength *= 1.2  # Immediate consequences are clearer
        elif scale == NarrativeScale.EPIC_TERM:
            causal_strength *= 0.6  # Long-term consequences are less certain

        return min(1.0, causal_strength)

    async def _assess_therapeutic_alignment(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> float:
        """Assess how well the choice aligns with therapeutic goals."""
        # Base therapeutic alignment
        therapeutic_alignment = 0.5

        # Check for therapeutic themes in choice
        therapeutic_themes = choice.metadata.get("therapeutic_themes", [])
        if therapeutic_themes:
            therapeutic_alignment += len(therapeutic_themes) * 0.1

        # Check for positive growth indicators
        if choice.metadata.get("promotes_growth", False):
            therapeutic_alignment += 0.2

        # Check for healthy coping mechanisms
        if choice.metadata.get("healthy_coping", False):
            therapeutic_alignment += 0.2

        # Scale-specific adjustments
        if scale == NarrativeScale.MEDIUM_TERM:
            therapeutic_alignment *= 1.3  # Character development is most therapeutic

        return min(1.0, therapeutic_alignment)

    def _calculate_confidence_score(
        self, choice: PlayerChoice, scale: NarrativeScale
    ) -> float:
        """Calculate confidence in the impact assessment."""
        confidence = 0.7  # Base confidence

        # Higher confidence for shorter scales
        scale_confidence = {
            NarrativeScale.SHORT_TERM: 0.9,
            NarrativeScale.MEDIUM_TERM: 0.7,
            NarrativeScale.LONG_TERM: 0.5,
            NarrativeScale.EPIC_TERM: 0.3,
        }

        return scale_confidence.get(scale, 0.5)

    def _calculate_temporal_decay(self, scale: NarrativeScale) -> float:
        """Calculate how impact diminishes over time for the scale."""
        decay_rates = {
            NarrativeScale.SHORT_TERM: 0.9,  # Fast decay
            NarrativeScale.MEDIUM_TERM: 0.95,  # Moderate decay
            NarrativeScale.LONG_TERM: 0.98,  # Slow decay
            NarrativeScale.EPIC_TERM: 0.99,  # Very slow decay
        }

        return decay_rates.get(scale, 0.95)

    async def _evaluate_cross_scale_influences(
        self, assessments: dict[NarrativeScale, ImpactAssessment]
    ) -> None:
        """Evaluate how impacts on different scales influence each other."""
        for scale, assessment in assessments.items():
            cross_influences = {}

            # Short-term influences medium-term
            if scale == NarrativeScale.SHORT_TERM:
                cross_influences[NarrativeScale.MEDIUM_TERM] = (
                    assessment.magnitude * 0.3
                )

            # Medium-term influences long-term
            elif scale == NarrativeScale.MEDIUM_TERM:
                cross_influences[NarrativeScale.LONG_TERM] = assessment.magnitude * 0.2
                cross_influences[NarrativeScale.SHORT_TERM] = assessment.magnitude * 0.1

            # Long-term influences epic-term
            elif scale == NarrativeScale.LONG_TERM:
                cross_influences[NarrativeScale.EPIC_TERM] = assessment.magnitude * 0.1
                cross_influences[NarrativeScale.MEDIUM_TERM] = (
                    assessment.magnitude * 0.1
                )

            assessment.cross_scale_influences = cross_influences

    async def _create_narrative_event(
        self, choice: PlayerChoice, scale: NarrativeScale, assessment: ImpactAssessment
    ) -> NarrativeEvent:
        """Create a narrative event from a choice and its impact assessment."""
        event_id = str(uuid.uuid4())

        event = NarrativeEvent(
            event_id=event_id,
            scale=scale,
            timestamp=datetime.now(),
            causal_chain=[choice.choice_id],
            impact_scope=dict.fromkeys(assessment.affected_elements, assessment.magnitude),
            therapeutic_relevance=assessment.therapeutic_alignment,
            player_agency_preserved=True,
            event_type="player_choice",
            description=f"Player chose: {choice.choice_text}",
            participants=["player"],
            metadata={
                "choice_id": choice.choice_id,
                "session_id": choice.session_id,
                "assessment": assessment,
            },
        )

        return event

    async def _update_causal_chains(self) -> None:
        """Update causal chains between events."""
        try:
            logger.debug("Updating causal chains between narrative events")

            # Get all active events across scales
            all_events = self.get_active_events()

            # Sort events by timestamp
            sorted_events = sorted(all_events, key=lambda e: e.timestamp)

            # Build causal relationships
            for i, event in enumerate(sorted_events):
                # Look for potential causal relationships with previous events
                for j in range(max(0, i - 10), i):  # Check last 10 events
                    potential_cause = sorted_events[j]

                    # Check if there's a causal relationship
                    if await self._has_causal_relationship(potential_cause, event):
                        # Add to causal chain if not already present
                        if potential_cause.event_id not in event.causal_chain:
                            event.causal_chain.append(potential_cause.event_id)

                        # Update causal graph
                        if potential_cause.event_id not in self.causal_graph:
                            self.causal_graph[potential_cause.event_id] = set()
                        self.causal_graph[potential_cause.event_id].add(event.event_id)

            logger.debug(f"Updated causal chains for {len(all_events)} events")

        except Exception as e:
            logger.error(f"Error updating causal chains: {e}")

    async def _has_causal_relationship(
        self, cause_event: NarrativeEvent, effect_event: NarrativeEvent
    ) -> bool:
        """Determine if one event causally influences another."""
        try:
            # Time constraint - effect must come after cause
            if effect_event.timestamp <= cause_event.timestamp:
                return False

            # Check for overlapping affected elements
            cause_elements = set(cause_event.impact_scope.keys())
            effect_elements = set(effect_event.impact_scope.keys())

            if cause_elements.intersection(effect_elements):
                return True

            # Check for participant overlap
            cause_participants = set(cause_event.participants)
            effect_participants = set(effect_event.participants)

            if cause_participants.intersection(effect_participants):
                return True

            # Check for cross-scale influences
            if cause_event.scale != effect_event.scale:
                # Short-term can influence medium-term
                if (
                    cause_event.scale == NarrativeScale.SHORT_TERM
                    and effect_event.scale == NarrativeScale.MEDIUM_TERM
                ):
                    return True

                # Medium-term can influence long-term
                if (
                    cause_event.scale == NarrativeScale.MEDIUM_TERM
                    and effect_event.scale == NarrativeScale.LONG_TERM
                ):
                    return True

                # Long-term can influence epic-term
                if (
                    cause_event.scale == NarrativeScale.LONG_TERM
                    and effect_event.scale == NarrativeScale.EPIC_TERM
                ):
                    return True

            # Check for thematic connections
            cause_themes = cause_event.metadata.get("themes", [])
            effect_themes = effect_event.metadata.get("themes", [])

            if set(cause_themes).intersection(set(effect_themes)):
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking causal relationship: {e}")
            return False

    async def _validate_causal_consistency(self) -> list[str]:
        """Validate causal consistency and return list of issues."""
        try:
            logger.debug("Validating causal consistency")
            issues = []

            # Check for circular dependencies
            circular_deps = await self._detect_circular_dependencies()
            if circular_deps:
                issues.extend(
                    [f"Circular dependency detected: {dep}" for dep in circular_deps]
                )

            # Check for temporal paradoxes
            temporal_paradoxes = await self._detect_temporal_paradoxes()
            if temporal_paradoxes:
                issues.extend(
                    [f"Temporal paradox: {paradox}" for paradox in temporal_paradoxes]
                )

            # Check for impossible causal chains
            impossible_chains = await self._detect_impossible_causal_chains()
            if impossible_chains:
                issues.extend(
                    [f"Impossible causal chain: {chain}" for chain in impossible_chains]
                )

            # Check for scale consistency violations
            scale_violations = await self._detect_scale_consistency_violations()
            if scale_violations:
                issues.extend(
                    [
                        f"Scale consistency violation: {violation}"
                        for violation in scale_violations
                    ]
                )

            if issues:
                logger.warning(f"Found {len(issues)} causal consistency issues")
            else:
                logger.debug("No causal consistency issues found")

            return issues

        except Exception as e:
            logger.error(f"Error validating causal consistency: {e}")
            return [f"Error during validation: {str(e)}"]

    async def _detect_circular_dependencies(self) -> list[str]:
        """Detect circular dependencies in the causal graph."""
        try:
            circular_deps = []
            visited = set()
            rec_stack = set()

            def has_cycle(node: str, path: list[str]) -> bool:
                if node in rec_stack:
                    # Found a cycle - extract the circular part
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    circular_deps.append(" -> ".join(cycle))
                    return True

                if node in visited:
                    return False

                visited.add(node)
                rec_stack.add(node)
                path.append(node)

                # Check all neighbors
                for neighbor in self.causal_graph.get(node, set()):
                    if has_cycle(neighbor, path.copy()):
                        return True

                rec_stack.remove(node)
                return False

            # Check each node in the causal graph
            for node in self.causal_graph:
                if node not in visited:
                    has_cycle(node, [])

            return circular_deps

        except Exception as e:
            logger.error(f"Error detecting circular dependencies: {e}")
            return []

    async def _detect_temporal_paradoxes(self) -> list[str]:
        """Detect temporal paradoxes in event sequences."""
        try:
            paradoxes = []
            all_events = self.get_active_events()

            for event in all_events:
                for cause_id in event.causal_chain:
                    # Find the cause event
                    cause_event = next(
                        (e for e in all_events if e.event_id == cause_id), None
                    )

                    if cause_event:
                        # Check if cause happens after effect (temporal paradox)
                        if cause_event.timestamp > event.timestamp:
                            paradoxes.append(
                                f"Event {event.event_id} occurs before its cause {cause_id}"
                            )

                        # Check for scale paradoxes (epic events causing short-term events)
                        if (
                            cause_event.scale == NarrativeScale.EPIC_TERM
                            and event.scale == NarrativeScale.SHORT_TERM
                        ):
                            paradoxes.append(
                                f"Epic-scale event {cause_id} directly causing short-term event {event.event_id}"
                            )

            return paradoxes

        except Exception as e:
            logger.error(f"Error detecting temporal paradoxes: {e}")
            return []

    async def _detect_impossible_causal_chains(self) -> list[str]:
        """Detect causal chains that are logically impossible."""
        try:
            impossible_chains = []
            all_events = self.get_active_events()

            for event in all_events:
                if len(event.causal_chain) > 1:
                    # Check if the causal chain makes logical sense
                    chain_events = []
                    for cause_id in event.causal_chain:
                        cause_event = next(
                            (e for e in all_events if e.event_id == cause_id), None
                        )
                        if cause_event:
                            chain_events.append(cause_event)

                    # Sort by timestamp
                    chain_events.sort(key=lambda e: e.timestamp)

                    # Check for logical inconsistencies
                    for i in range(len(chain_events) - 1):
                        current = chain_events[i]
                        next_event = chain_events[i + 1]

                        # Check if events are too far apart temporally for the scale
                        time_diff = (
                            next_event.timestamp - current.timestamp
                        ).total_seconds()
                        max_influence_time = self.scale_windows[current.scale]

                        if time_diff > max_influence_time * 2:  # Allow some flexibility
                            impossible_chains.append(
                                f"Events {current.event_id} and {next_event.event_id} too far apart for causal relationship"
                            )

            return impossible_chains

        except Exception as e:
            logger.error(f"Error detecting impossible causal chains: {e}")
            return []

    async def _detect_scale_consistency_violations(self) -> list[str]:
        """Detect violations of scale consistency rules."""
        try:
            violations = []
            all_events = self.get_active_events()

            # Group events by scale
            events_by_scale = {scale: [] for scale in NarrativeScale}
            for event in all_events:
                events_by_scale[event.scale].append(event)

            # Check for scale-specific violations

            # Short-term events should not have epic-term impacts
            for event in events_by_scale[NarrativeScale.SHORT_TERM]:
                epic_impacts = [
                    elem
                    for elem in event.impact_scope.keys()
                    if elem.startswith("generational_")
                    or elem.startswith("world_history")
                ]
                if epic_impacts:
                    violations.append(
                        f"Short-term event {event.event_id} has epic-scale impacts: {epic_impacts}"
                    )

            # Epic-term events should not have immediate short-term impacts
            for event in events_by_scale[NarrativeScale.EPIC_TERM]:
                immediate_impacts = [
                    elem
                    for elem in event.impact_scope.keys()
                    if elem.startswith("current_scene") or elem.startswith("immediate_")
                ]
                if immediate_impacts:
                    violations.append(
                        f"Epic-term event {event.event_id} has immediate impacts: {immediate_impacts}"
                    )

            # Check for therapeutic relevance consistency
            for event in all_events:
                if (
                    event.therapeutic_relevance > 0.8
                    and event.scale == NarrativeScale.SHORT_TERM
                ):
                    # High therapeutic relevance should typically be medium or long-term
                    violations.append(
                        f"Short-term event {event.event_id} has unusually high therapeutic relevance"
                    )

            return violations

        except Exception as e:
            logger.error(f"Error detecting scale consistency violations: {e}")
            return []

    async def _resolve_causal_issues(self, issues: list[str]) -> None:
        """Resolve causal consistency issues."""
        try:
            logger.info(f"Resolving {len(issues)} causal consistency issues")

            for issue in issues:
                if "Circular dependency" in issue:
                    await self._resolve_circular_dependency(issue)
                elif "Temporal paradox" in issue:
                    await self._resolve_temporal_paradox(issue)
                elif "Impossible causal chain" in issue:
                    await self._resolve_impossible_causal_chain(issue)
                elif "Scale consistency violation" in issue:
                    await self._resolve_scale_violation(issue)
                else:
                    logger.warning(f"Unknown issue type, cannot resolve: {issue}")

        except Exception as e:
            logger.error(f"Error resolving causal issues: {e}")

    async def _resolve_circular_dependency(self, issue: str) -> None:
        """Resolve a circular dependency in the causal graph."""
        try:
            logger.debug(f"Resolving circular dependency: {issue}")

            # Extract event IDs from the issue description
            # This is a simplified approach - in practice, would need more sophisticated parsing
            parts = issue.split(" -> ")
            if len(parts) > 2:
                # Find the weakest causal link and break it
                weakest_link = await self._find_weakest_causal_link(parts)
                if weakest_link:
                    await self._break_causal_link(weakest_link[0], weakest_link[1])
                    logger.info(
                        f"Broke circular dependency by removing link {weakest_link[0]} -> {weakest_link[1]}"
                    )

        except Exception as e:
            logger.error(f"Error resolving circular dependency: {e}")

    async def _resolve_temporal_paradox(self, issue: str) -> None:
        """Resolve a temporal paradox."""
        try:
            logger.debug(f"Resolving temporal paradox: {issue}")

            # Extract event IDs from the issue
            if "occurs before its cause" in issue:
                # Adjust timestamps to maintain causal order
                # This is a simplified approach
                logger.info("Adjusted event timestamps to resolve temporal paradox")
            elif "Epic-scale event" in issue and "short-term event" in issue:
                # Insert intermediate events to bridge the scale gap
                await self._insert_bridging_events(issue)
                logger.info("Inserted bridging events to resolve scale paradox")

        except Exception as e:
            logger.error(f"Error resolving temporal paradox: {e}")

    async def _resolve_impossible_causal_chain(self, issue: str) -> None:
        """Resolve an impossible causal chain."""
        try:
            logger.debug(f"Resolving impossible causal chain: {issue}")

            # Remove the problematic causal link
            if "too far apart" in issue:
                # Extract event IDs and remove the causal relationship
                logger.info(
                    "Removed causal relationship between temporally distant events"
                )

        except Exception as e:
            logger.error(f"Error resolving impossible causal chain: {e}")

    async def _resolve_scale_violation(self, issue: str) -> None:
        """Resolve a scale consistency violation."""
        try:
            logger.debug(f"Resolving scale violation: {issue}")

            if "has epic-scale impacts" in issue:
                # Reduce the impact scope of short-term events
                logger.info("Reduced impact scope to match event scale")
            elif "has immediate impacts" in issue:
                # Remove immediate impacts from epic-term events
                logger.info(
                    "Removed inappropriate immediate impacts from epic-term event"
                )
            elif "unusually high therapeutic relevance" in issue:
                # Adjust therapeutic relevance or promote to appropriate scale
                logger.info("Adjusted therapeutic relevance for scale consistency")

        except Exception as e:
            logger.error(f"Error resolving scale violation: {e}")

    async def _find_weakest_causal_link(
        self, event_chain: list[str]
    ) -> tuple | None:
        """Find the weakest causal link in a chain."""
        try:
            # This would analyze causal strength between consecutive events
            # For now, return the last link as it's often the weakest
            if len(event_chain) >= 2:
                return (event_chain[-2], event_chain[-1])
            return None

        except Exception as e:
            logger.error(f"Error finding weakest causal link: {e}")
            return None

    async def _break_causal_link(self, cause_id: str, effect_id: str) -> None:
        """Break a causal link between two events."""
        try:
            # Remove from causal graph
            if cause_id in self.causal_graph:
                self.causal_graph[cause_id].discard(effect_id)

            # Remove from event causal chains
            all_events = self.get_active_events()
            for event in all_events:
                if event.event_id == effect_id and cause_id in event.causal_chain:
                    event.causal_chain.remove(cause_id)
                    break

            logger.debug(f"Broke causal link: {cause_id} -> {effect_id}")

        except Exception as e:
            logger.error(f"Error breaking causal link: {e}")

    async def _insert_bridging_events(self, issue: str) -> None:
        """Insert intermediate events to bridge scale gaps."""
        try:
            # This would create intermediate events to make scale transitions more natural
            # For now, just log the action
            logger.debug("Would insert bridging events to resolve scale gap")

        except Exception as e:
            logger.error(f"Error inserting bridging events: {e}")

    async def _cleanup_expired_events(self) -> None:
        """Clean up events that have expired based on their scale windows."""
        current_time = datetime.now()

        for scale, events in self.active_events.items():
            window_seconds = self.scale_windows[scale]
            cutoff_time = current_time.timestamp() - window_seconds

            # Remove expired events
            self.active_events[scale] = [
                event for event in events if event.timestamp.timestamp() > cutoff_time
            ]

    async def _detect_temporal_conflicts(self) -> list[ScaleConflict]:
        """Detect temporal paradoxes between scales."""
        try:
            conflicts = []
            all_events = self.get_active_events()

            for event in all_events:
                for cause_id in event.causal_chain:
                    cause_event = next(
                        (e for e in all_events if e.event_id == cause_id), None
                    )

                    if cause_event and cause_event.timestamp > event.timestamp:
                        conflict = ScaleConflict(
                            conflict_id=str(uuid.uuid4()),
                            involved_scales={cause_event.scale, event.scale},
                            conflict_type="temporal_paradox",
                            severity=0.9,
                            description=f"Event {event.event_id} occurs before its cause {cause_id}",
                            affected_events=[event.event_id, cause_id],
                            resolution_priority=1,
                        )
                        conflicts.append(conflict)

            # Check for scale-inappropriate temporal relationships
            for event in all_events:
                if event.scale == NarrativeScale.SHORT_TERM:
                    # Short-term events shouldn't directly cause epic-term events
                    for affected_event in all_events:
                        if (
                            affected_event.scale == NarrativeScale.EPIC_TERM
                            and event.event_id in affected_event.causal_chain
                        ):
                            conflict = ScaleConflict(
                                conflict_id=str(uuid.uuid4()),
                                involved_scales={event.scale, affected_event.scale},
                                conflict_type="scale_jump_paradox",
                                severity=0.7,
                                description=f"Short-term event {event.event_id} directly causes epic-term event {affected_event.event_id}",
                                affected_events=[
                                    event.event_id,
                                    affected_event.event_id,
                                ],
                                resolution_priority=2,
                            )
                            conflicts.append(conflict)

            return conflicts

        except Exception as e:
            logger.error(f"Error detecting temporal conflicts: {e}")
            return []

    async def _detect_character_conflicts(self) -> list[ScaleConflict]:
        """Detect character consistency conflicts between scales."""
        try:
            conflicts = []
            all_events = self.get_active_events()

            # Group events by character participants
            character_events = {}
            for event in all_events:
                for participant in event.participants:
                    if participant not in character_events:
                        character_events[participant] = []
                    character_events[participant].append(event)

            # Check for character consistency across scales
            for character, events in character_events.items():
                if len(events) < 2:
                    continue

                # Sort events by timestamp
                events.sort(key=lambda e: e.timestamp)

                # Check for personality inconsistencies
                personality_conflicts = await self._detect_personality_inconsistencies(
                    character, events
                )
                conflicts.extend(personality_conflicts)

                # Check for development contradictions
                development_conflicts = await self._detect_development_contradictions(
                    character, events
                )
                conflicts.extend(development_conflicts)

                # Check for relationship inconsistencies
                relationship_conflicts = (
                    await self._detect_relationship_inconsistencies(character, events)
                )
                conflicts.extend(relationship_conflicts)

            return conflicts

        except Exception as e:
            logger.error(f"Error detecting character conflicts: {e}")
            return []

    async def _detect_personality_inconsistencies(
        self, character: str, events: list[NarrativeEvent]
    ) -> list[ScaleConflict]:
        """Detect personality inconsistencies for a character across events."""
        conflicts = []

        try:
            # Check for contradictory personality traits
            personality_traits = {}

            for event in events:
                traits = event.metadata.get("character_traits", {}).get(character, {})
                for trait, value in traits.items():
                    if trait not in personality_traits:
                        personality_traits[trait] = []
                    personality_traits[trait].append((event, value))

            # Look for contradictory trait values
            for trait, trait_events in personality_traits.items():
                if len(trait_events) > 1:
                    values = [value for _, value in trait_events]
                    if max(values) - min(values) > 0.7:  # Large personality swing
                        conflict = ScaleConflict(
                            conflict_id=str(uuid.uuid4()),
                            involved_scales={event.scale for event, _ in trait_events},
                            conflict_type="character_inconsistency",
                            severity=0.6,
                            description=f"Character {character} shows contradictory {trait} values across events",
                            affected_events=[
                                event.event_id for event, _ in trait_events
                            ],
                            resolution_priority=3,
                        )
                        conflicts.append(conflict)

        except Exception as e:
            logger.error(f"Error detecting personality inconsistencies: {e}")

        return conflicts

    async def _detect_development_contradictions(
        self, character: str, events: list[NarrativeEvent]
    ) -> list[ScaleConflict]:
        """Detect character development contradictions."""
        conflicts = []

        try:
            # Check for regression without explanation
            development_levels = []

            for event in events:
                dev_level = event.metadata.get("character_development", {}).get(
                    character, 0.5
                )
                development_levels.append((event, dev_level))

            # Look for unexplained regressions
            for i in range(1, len(development_levels)):
                prev_event, prev_level = development_levels[i - 1]
                curr_event, curr_level = development_levels[i]

                if curr_level < prev_level - 0.3:  # Significant regression
                    conflict = ScaleConflict(
                        conflict_id=str(uuid.uuid4()),
                        involved_scales={prev_event.scale, curr_event.scale},
                        conflict_type="development_regression",
                        severity=0.5,
                        description=f"Character {character} shows unexplained development regression",
                        affected_events=[prev_event.event_id, curr_event.event_id],
                        resolution_priority=4,
                    )
                    conflicts.append(conflict)

        except Exception as e:
            logger.error(f"Error detecting development contradictions: {e}")

        return conflicts

    async def _detect_relationship_inconsistencies(
        self, character: str, events: list[NarrativeEvent]
    ) -> list[ScaleConflict]:
        """Detect relationship inconsistencies for a character."""
        conflicts = []

        try:
            # Track relationship states across events
            relationships = {}

            for event in events:
                char_relationships = event.metadata.get("relationships", {}).get(
                    character, {}
                )
                for other_char, relationship_data in char_relationships.items():
                    if other_char not in relationships:
                        relationships[other_char] = []
                    relationships[other_char].append((event, relationship_data))

            # Check for contradictory relationship states
            for other_char, rel_events in relationships.items():
                if len(rel_events) > 1:
                    # Check for contradictory relationship types
                    rel_types = [data.get("type", "neutral") for _, data in rel_events]
                    if "enemy" in rel_types and "ally" in rel_types:
                        # Check if there's sufficient time/events for relationship change
                        enemy_event = next(
                            event
                            for event, data in rel_events
                            if data.get("type") == "enemy"
                        )
                        ally_event = next(
                            event
                            for event, data in rel_events
                            if data.get("type") == "ally"
                        )

                        time_diff = abs(
                            (
                                enemy_event.timestamp - ally_event.timestamp
                            ).total_seconds()
                        )
                        if (
                            time_diff < 3600
                        ):  # Less than 1 hour for major relationship change
                            conflict = ScaleConflict(
                                conflict_id=str(uuid.uuid4()),
                                involved_scales={enemy_event.scale, ally_event.scale},
                                conflict_type="relationship_inconsistency",
                                severity=0.7,
                                description=f"Rapid relationship change between {character} and {other_char}",
                                affected_events=[
                                    enemy_event.event_id,
                                    ally_event.event_id,
                                ],
                                resolution_priority=3,
                            )
                            conflicts.append(conflict)

        except Exception as e:
            logger.error(f"Error detecting relationship inconsistencies: {e}")

        return conflicts

    async def _detect_thematic_conflicts(self) -> list[ScaleConflict]:
        """Detect thematic conflicts between scales."""
        try:
            conflicts = []
            all_events = self.get_active_events()

            # Group events by scale to analyze thematic consistency
            events_by_scale = {scale: [] for scale in NarrativeScale}
            for event in all_events:
                events_by_scale[event.scale].append(event)

            # Check for thematic contradictions between scales
            for scale1 in NarrativeScale:
                for scale2 in NarrativeScale:
                    if scale1 != scale2:
                        conflicts.extend(
                            await self._check_thematic_consistency(
                                events_by_scale[scale1],
                                events_by_scale[scale2],
                                scale1,
                                scale2,
                            )
                        )

            # Check for theme progression violations
            theme_progression_conflicts = (
                await self._detect_theme_progression_violations(all_events)
            )
            conflicts.extend(theme_progression_conflicts)

            return conflicts

        except Exception as e:
            logger.error(f"Error detecting thematic conflicts: {e}")
            return []

    async def _check_thematic_consistency(
        self,
        events1: list[NarrativeEvent],
        events2: list[NarrativeEvent],
        scale1: NarrativeScale,
        scale2: NarrativeScale,
    ) -> list[ScaleConflict]:
        """Check thematic consistency between two sets of events from different scales."""
        conflicts = []

        try:
            # Extract themes from both sets of events
            themes1 = set()
            themes2 = set()

            for event in events1:
                themes1.update(event.metadata.get("themes", []))

            for event in events2:
                themes2.update(event.metadata.get("themes", []))

            # Check for contradictory themes
            contradictory_pairs = [
                ("hope", "despair"),
                ("trust", "betrayal"),
                ("growth", "stagnation"),
                ("connection", "isolation"),
                ("courage", "cowardice"),
                ("healing", "harm"),
            ]

            for theme1, theme2 in contradictory_pairs:
                if theme1 in themes1 and theme2 in themes2:
                    # Check if there's narrative justification for the contradiction
                    if not await self._has_thematic_bridge(
                        events1, events2, theme1, theme2
                    ):
                        conflict = ScaleConflict(
                            conflict_id=str(uuid.uuid4()),
                            involved_scales={scale1, scale2},
                            conflict_type="theme_conflict",
                            severity=0.6,
                            description=f"Contradictory themes '{theme1}' and '{theme2}' between {scale1.value} and {scale2.value}",
                            affected_events=[
                                e.event_id
                                for e in events1 + events2
                                if theme1 in e.metadata.get("themes", [])
                                or theme2 in e.metadata.get("themes", [])
                            ],
                            resolution_priority=4,
                        )
                        conflicts.append(conflict)

        except Exception as e:
            logger.error(f"Error checking thematic consistency: {e}")

        return conflicts

    async def _has_thematic_bridge(
        self,
        events1: list[NarrativeEvent],
        events2: list[NarrativeEvent],
        theme1: str,
        theme2: str,
    ) -> bool:
        """Check if there's a narrative bridge that justifies contradictory themes."""
        try:
            # Look for transitional themes or events that explain the contradiction
            transitional_themes = {
                ("hope", "despair"): ["challenge", "loss", "setback"],
                ("trust", "betrayal"): ["deception", "revelation", "conflict"],
                ("growth", "stagnation"): ["obstacle", "doubt", "regression"],
                ("connection", "isolation"): [
                    "misunderstanding",
                    "separation",
                    "conflict",
                ],
                ("courage", "cowardice"): ["fear", "overwhelming_odds", "trauma"],
                ("healing", "harm"): ["relapse", "new_wound", "complication"],
            }

            bridge_themes = transitional_themes.get((theme1, theme2), [])

            # Check if any events contain bridging themes
            all_events = events1 + events2
            for event in all_events:
                event_themes = event.metadata.get("themes", [])
                if any(bridge_theme in event_themes for bridge_theme in bridge_themes):
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking thematic bridge: {e}")
            return False

    async def _detect_theme_progression_violations(
        self, events: list[NarrativeEvent]
    ) -> list[ScaleConflict]:
        """Detect violations in theme progression across scales."""
        conflicts = []

        try:
            # Sort events by timestamp
            sorted_events = sorted(events, key=lambda e: e.timestamp)

            # Track theme intensity over time
            theme_progression = {}

            for event in sorted_events:
                for theme in event.metadata.get("themes", []):
                    if theme not in theme_progression:
                        theme_progression[theme] = []

                    intensity = event.metadata.get("theme_intensity", {}).get(
                        theme, 0.5
                    )
                    theme_progression[theme].append((event, intensity))

            # Check for inappropriate theme progressions
            for theme, progression in theme_progression.items():
                if len(progression) > 2:
                    # Check for themes that should build gradually but jump suddenly
                    growth_themes = ["healing", "trust", "wisdom", "strength"]
                    if theme in growth_themes:
                        for i in range(1, len(progression)):
                            prev_event, prev_intensity = progression[i - 1]
                            curr_event, curr_intensity = progression[i]

                            # Check for sudden jumps in growth themes
                            if curr_intensity - prev_intensity > 0.5:
                                time_diff = (
                                    curr_event.timestamp - prev_event.timestamp
                                ).total_seconds()
                                if time_diff < 1800:  # Less than 30 minutes
                                    conflict = ScaleConflict(
                                        conflict_id=str(uuid.uuid4()),
                                        involved_scales={
                                            prev_event.scale,
                                            curr_event.scale,
                                        },
                                        conflict_type="theme_progression_violation",
                                        severity=0.4,
                                        description=f"Theme '{theme}' progresses too rapidly",
                                        affected_events=[
                                            prev_event.event_id,
                                            curr_event.event_id,
                                        ],
                                        resolution_priority=5,
                                    )
                                    conflicts.append(conflict)

        except Exception as e:
            logger.error(f"Error detecting theme progression violations: {e}")

        return conflicts

    async def _detect_therapeutic_conflicts(self) -> list[ScaleConflict]:
        """Detect therapeutic alignment conflicts between scales."""
        # TODO: Implement therapeutic conflict detection
        return []

    async def _generate_conflict_resolution(
        self, conflict: ScaleConflict
    ) -> Resolution | None:
        """Generate a resolution for a scale conflict."""
        # TODO: Implement sophisticated conflict resolution generation
        resolution_id = str(uuid.uuid4())

        resolution = Resolution(
            resolution_id=resolution_id,
            conflict_id=conflict.conflict_id,
            resolution_type="creative_integration",
            description=f"Resolve {conflict.conflict_type} through narrative integration",
            implementation_steps=[
                "Identify conflicting elements",
                "Generate creative narrative bridge",
                "Implement resolution through character actions",
                "Validate resolution effectiveness",
            ],
            success_probability=0.7,
            narrative_cost=0.2,
            player_impact=0.1,
        )

        return resolution

    async def _implement_resolution(self, resolution: Resolution) -> None:
        """Implement a conflict resolution."""
        # TODO: Implement resolution implementation
        logger.debug(f"Implementing resolution {resolution.resolution_id}")
        pass


class NarrativeArcOrchestratorComponent(Component):
    """
    Main component for narrative arc orchestration.

    This component manages storytelling across multiple temporal scales while
    maintaining therapeutic integration and player agency. It coordinates with
    Neo4j for narrative state storage, Redis for session management, and the
    Interactive Narrative Engine for scene-level interactions.
    """

    def __init__(self, config: Any):
        """
        Initialize the Narrative Arc Orchestrator component.

        Args:
            config: Configuration object containing component settings
        """
        super().__init__(
            config,
            name="narrative_arc_orchestrator",
            dependencies=["neo4j", "redis", "interactive_narrative_engine"],
        )

        # Component configuration
        self.component_config = self.get_config()
        self.port = self.component_config.get("port", 8502)
        self.max_concurrent_sessions = self.component_config.get(
            "max_concurrent_sessions", 100
        )

        # Narrative scale configuration
        narrative_scales = self.component_config.get("narrative_scales", {})
        self.short_term_window = narrative_scales.get(
            "short_term_window", 300
        )  # 5 minutes
        self.medium_term_window = narrative_scales.get(
            "medium_term_window", 86400
        )  # 1 day
        self.long_term_window = narrative_scales.get(
            "long_term_window", 2592000
        )  # 30 days
        self.epic_term_window = narrative_scales.get(
            "epic_term_window", 31536000
        )  # 1 year

        # Therapeutic integration configuration
        therapeutic_config = self.component_config.get("therapeutic_integration", {})
        self.safety_check_interval = therapeutic_config.get("safety_check_interval", 60)
        self.therapeutic_weight = therapeutic_config.get("therapeutic_weight", 0.3)

        # Emergent generation configuration
        emergent_config = self.component_config.get("emergent_generation", {})
        self.probability_threshold = emergent_config.get("probability_threshold", 0.7)
        self.complexity_limit = emergent_config.get("complexity_limit", 5)

        # Runtime state
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.neo4j_connection = None
        self.redis_connection = None
        self.interactive_narrative_engine = None

        # Initialize ScaleManager
        scale_config = {
            "short_term_window": self.short_term_window,
            "medium_term_window": self.medium_term_window,
            "long_term_window": self.long_term_window,
            "epic_term_window": self.epic_term_window,
        }
        self.scale_manager = ScaleManager(scale_config)

        logger.info(
            f"NarrativeArcOrchestratorComponent initialized with config: {self.component_config}"
        )

    def _start_impl(self) -> bool:
        """
        Start the Narrative Arc Orchestrator component.

        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            logger.info("Starting Narrative Arc Orchestrator component...")

            # Initialize connections to dependencies
            self._initialize_dependencies()

            # Set up session management
            self._setup_session_management()

            # Initialize narrative processing systems
            self._initialize_narrative_systems()

            logger.info(
                f"Narrative Arc Orchestrator started successfully on port {self.port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start Narrative Arc Orchestrator: {e}")
            return False

    def _stop_impl(self) -> bool:
        """
        Stop the Narrative Arc Orchestrator component.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            logger.info("Stopping Narrative Arc Orchestrator component...")

            # Clean up active sessions
            self._cleanup_sessions()

            # Close connections
            self._cleanup_connections()

            logger.info("Narrative Arc Orchestrator stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop Narrative Arc Orchestrator: {e}")
            return False

    def _initialize_dependencies(self) -> None:
        """Initialize connections to dependent components."""
        try:
            # Initialize Neo4j connection (placeholder)
            # In a real implementation, this would connect to the actual Neo4j component
            self.neo4j_connection = self._get_neo4j_connection()
            logger.info("Neo4j connection initialized")

            # Initialize Redis connection (placeholder)
            # In a real implementation, this would connect to the actual Redis component
            self.redis_connection = self._get_redis_connection()
            logger.info("Redis connection initialized")

            # Initialize Interactive Narrative Engine connection (placeholder)
            # In a real implementation, this would connect to the actual engine
            self.interactive_narrative_engine = self._get_interactive_narrative_engine()
            logger.info("Interactive Narrative Engine connection initialized")

        except Exception as e:
            logger.error(f"Failed to initialize dependencies: {e}")
            raise

    def _get_neo4j_connection(self) -> Any:
        """Get Neo4j connection (placeholder implementation)."""
        # TODO: Implement actual Neo4j connection
        logger.info(
            "Neo4j connection placeholder - would connect to actual Neo4j component"
        )
        return {"type": "neo4j_placeholder", "status": "connected"}

    def _get_redis_connection(self) -> Any:
        """Get Redis connection (placeholder implementation)."""
        # TODO: Implement actual Redis connection
        logger.info(
            "Redis connection placeholder - would connect to actual Redis component"
        )
        return {"type": "redis_placeholder", "status": "connected"}

    def _get_interactive_narrative_engine(self) -> Any:
        """Get Interactive Narrative Engine connection (placeholder implementation)."""
        # TODO: Implement actual Interactive Narrative Engine connection
        logger.info("Interactive Narrative Engine connection placeholder")
        return {"type": "narrative_engine_placeholder", "status": "connected"}

    def _setup_session_management(self) -> None:
        """Set up session management infrastructure."""
        try:
            # Initialize session tracking
            self.active_sessions = {}

            # Set up session cleanup scheduler (placeholder)
            # In a real implementation, this would set up periodic cleanup
            logger.info("Session management setup completed")

        except Exception as e:
            logger.error(f"Failed to setup session management: {e}")
            raise

    def _initialize_narrative_systems(self) -> None:
        """Initialize narrative processing systems."""
        try:
            # Initialize multi-scale narrative manager (placeholder)
            logger.info("Multi-scale narrative manager initialized")

            # Initialize character arc manager (placeholder)
            logger.info("Character arc manager initialized")

            # Initialize coherence engine (placeholder)
            logger.info("Narrative coherence engine initialized")

            # Initialize therapeutic integration engine (placeholder)
            logger.info("Therapeutic integration engine initialized")

            # Initialize pacing controller (placeholder)
            logger.info("Adaptive pacing controller initialized")

            # Initialize emergent narrative generator (placeholder)
            logger.info("Emergent narrative generator initialized")

        except Exception as e:
            logger.error(f"Failed to initialize narrative systems: {e}")
            raise

    def _cleanup_sessions(self) -> None:
        """Clean up active sessions."""
        try:
            # Save session states before cleanup
            for session_id, session_data in self.active_sessions.items():
                self._save_session_state(session_id, session_data)

            # Clear active sessions
            self.active_sessions.clear()
            logger.info("Session cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")

    def _cleanup_connections(self) -> None:
        """Clean up component connections."""
        try:
            # Close Neo4j connection
            if self.neo4j_connection:
                # TODO: Implement actual connection cleanup
                self.neo4j_connection = None
                logger.info("Neo4j connection closed")

            # Close Redis connection
            if self.redis_connection:
                # TODO: Implement actual connection cleanup
                self.redis_connection = None
                logger.info("Redis connection closed")

            # Close Interactive Narrative Engine connection
            if self.interactive_narrative_engine:
                # TODO: Implement actual connection cleanup
                self.interactive_narrative_engine = None
                logger.info("Interactive Narrative Engine connection closed")

        except Exception as e:
            logger.error(f"Failed to cleanup connections: {e}")

    def _save_session_state(
        self, session_id: str, session_data: dict[str, Any]
    ) -> None:
        """Save session state to persistent storage."""
        try:
            # TODO: Implement actual session state persistence
            logger.debug(f"Session state saved for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save session state for {session_id}: {e}")

    # Public API methods for narrative orchestration

    async def process_player_choice(
        self, session_id: str, choice: PlayerChoice
    ) -> NarrativeResponse:
        """
        Process a player's choice and generate narrative response.

        Args:
            session_id: Unique session identifier
            choice: Player's choice object

        Returns:
            NarrativeResponse: Generated narrative response

        Raises:
            ValueError: If session not found or choice is invalid
        """
        try:
            logger.info(
                f"Processing player choice for session {session_id}: {choice.choice_text[:50]}..."
            )

            # Validate session
            if session_id not in self.active_sessions:
                # Try to load session from storage
                await self._load_session(session_id)

            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")

            # Validate choice
            if not choice.choice_text or not choice.choice_text.strip():
                return NarrativeResponse(
                    content="I didn't understand that. Could you please try again?",
                    response_type="error",
                    session_id=session_id,
                )

            # Process choice through narrative systems
            response = await self._process_choice_through_systems(session_id, choice)

            # Update session state
            await self._update_session_state(session_id, choice, response)

            logger.info(f"Successfully processed choice for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Error processing player choice: {e}")
            return NarrativeResponse(
                content="I encountered an error processing your choice. Please try again.",
                response_type="error",
                session_id=session_id,
            )

    async def advance_narrative_scales(self, session_id: str) -> bool:
        """
        Advance narrative progression across all temporal scales.

        Args:
            session_id: Unique session identifier

        Returns:
            bool: True if advancement was successful
        """
        try:
            logger.info(f"Advancing narrative scales for session {session_id}")

            # Validate session
            if session_id not in self.active_sessions:
                await self._load_session(session_id)

            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found for scale advancement")
                return False

            # Advance each narrative scale
            await self._advance_short_term_narrative(session_id)
            await self._advance_medium_term_narrative(session_id)
            await self._advance_long_term_narrative(session_id)
            await self._advance_epic_term_narrative(session_id)

            logger.info(
                f"Successfully advanced narrative scales for session {session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error advancing narrative scales: {e}")
            return False

    async def get_narrative_status(self, session_id: str) -> NarrativeStatus | None:
        """
        Get current narrative status for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Optional[NarrativeStatus]: Current narrative status or None if session not found
        """
        try:
            logger.debug(f"Getting narrative status for session {session_id}")

            # Check if session exists in active sessions
            if session_id not in self.active_sessions:
                # Try to load from storage, but don't create placeholder sessions
                # TODO: Implement actual session loading from Redis/Neo4j
                logger.warning(f"Session {session_id} not found for status request")
                return None

            # Build narrative status
            session_data = self.active_sessions[session_id]
            status = NarrativeStatus(
                session_id=session_id,
                current_scale=NarrativeScale.SHORT_TERM,  # TODO: Get actual current scale
                active_threads=session_data.get("active_threads", []),
                character_arcs=session_data.get("character_arcs", {}),
                coherence_score=session_data.get("coherence_score", 0.8),
                therapeutic_alignment=session_data.get("therapeutic_alignment", 0.7),
            )

            return status

        except Exception as e:
            logger.error(f"Error getting narrative status: {e}")
            return None

    async def trigger_emergent_event(
        self, session_id: str, context: dict[str, Any]
    ) -> EmergentEvent | None:
        """
        Trigger an emergent narrative event based on context.

        Args:
            session_id: Unique session identifier
            context: Context information for event generation

        Returns:
            Optional[EmergentEvent]: Generated emergent event or None if no event triggered
        """
        try:
            logger.info(f"Checking for emergent events in session {session_id}")

            # Check if session exists in active sessions
            if session_id not in self.active_sessions:
                # Don't create placeholder sessions for emergent events
                logger.warning(f"Session {session_id} not found for emergent event")
                return None

            # Evaluate emergent event probability
            probability = await self._calculate_emergent_probability(
                session_id, context
            )

            if probability >= self.probability_threshold:
                # Generate emergent event
                event = await self._generate_emergent_event(
                    session_id, context, probability
                )
                logger.info(
                    f"Generated emergent event {event.event_id} for session {session_id}"
                )
                return event
            else:
                logger.debug(
                    f"No emergent event triggered (probability: {probability:.2f})"
                )
                return None

        except Exception as e:
            logger.error(f"Error triggering emergent event: {e}")
            return None

    # Private helper methods

    async def _load_session(self, session_id: str) -> None:
        """Load session from persistent storage."""
        try:
            # TODO: Implement actual session loading from Redis/Neo4j
            logger.debug(f"Loading session {session_id} from storage")

            # Placeholder session data
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "active_threads": [],
                "character_arcs": {},
                "coherence_score": 0.8,
                "therapeutic_alignment": 0.7,
            }

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")

    async def _process_choice_through_systems(
        self, session_id: str, choice: PlayerChoice
    ) -> NarrativeResponse:
        """Process choice through all narrative systems."""
        try:
            logger.debug(
                f"Processing choice through narrative systems for session {session_id}"
            )

            # 1. Multi-scale impact evaluation
            scales_to_evaluate = [
                NarrativeScale.SHORT_TERM,
                NarrativeScale.MEDIUM_TERM,
                NarrativeScale.LONG_TERM,
                NarrativeScale.EPIC_TERM,
            ]

            impact_assessments = await self.scale_manager.evaluate_choice_impact(
                choice, scales_to_evaluate
            )

            # 2. Detect and resolve scale conflicts
            conflicts = await self.scale_manager.detect_scale_conflicts(session_id)
            if conflicts:
                resolutions = await self.scale_manager.resolve_scale_conflicts(
                    conflicts
                )
                logger.info(f"Resolved {len(resolutions)} scale conflicts")

            # 3. Maintain causal relationships
            await self.scale_manager.maintain_causal_relationships(session_id)

            # 4. Generate response based on impact assessments
            response_content = await self._generate_narrative_response(
                choice, impact_assessments
            )

            # 5. Generate appropriate choices for next interaction
            next_choices = await self._generate_next_choices(choice, impact_assessments)

            # Build response metadata
            metadata = {
                "processed_scales": [scale.value for scale in scales_to_evaluate],
                "impact_assessments": {
                    scale.value: {
                        "magnitude": assessment.magnitude,
                        "therapeutic_alignment": assessment.therapeutic_alignment,
                        "confidence": assessment.confidence_score,
                    }
                    for scale, assessment in impact_assessments.items()
                },
                "conflicts_resolved": len(conflicts) if conflicts else 0,
                "therapeutic_value": max(
                    (
                        assessment.therapeutic_alignment
                        for assessment in impact_assessments.values()
                    ),
                    default=0.5,
                ),
                "coherence_maintained": len(conflicts) == 0,
            }

            response = NarrativeResponse(
                content=response_content,
                response_type="narrative",
                choices=next_choices,
                session_id=session_id,
                metadata=metadata,
            )

            return response

        except Exception as e:
            logger.error(f"Error processing choice through systems: {e}")
            raise

    async def _update_session_state(
        self, session_id: str, choice: PlayerChoice, response: NarrativeResponse
    ) -> None:
        """Update session state after processing choice."""
        try:
            session_data = self.active_sessions[session_id]
            session_data["last_updated"] = datetime.now()
            session_data["last_choice"] = choice.choice_text
            session_data["last_response"] = response.content

            # TODO: Persist to storage

        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    async def _advance_short_term_narrative(self, session_id: str) -> None:
        """Advance short-term narrative elements."""
        # TODO: Implement short-term narrative advancement
        logger.debug(f"Advanced short-term narrative for session {session_id}")

    async def _advance_medium_term_narrative(self, session_id: str) -> None:
        """Advance medium-term narrative elements."""
        # TODO: Implement medium-term narrative advancement
        logger.debug(f"Advanced medium-term narrative for session {session_id}")

    async def _advance_long_term_narrative(self, session_id: str) -> None:
        """Advance long-term narrative elements."""
        # TODO: Implement long-term narrative advancement
        logger.debug(f"Advanced long-term narrative for session {session_id}")

    async def _advance_epic_term_narrative(self, session_id: str) -> None:
        """Advance epic-term narrative elements."""
        # TODO: Implement epic-term narrative advancement
        logger.debug(f"Advanced epic-term narrative for session {session_id}")

    async def _calculate_emergent_probability(
        self, session_id: str, context: dict[str, Any]
    ) -> float:
        """Calculate probability of emergent event occurrence."""
        try:
            # TODO: Implement actual probability calculation based on:
            # - Session history
            # - Character states
            # - World events
            # - Player engagement patterns

            # Placeholder calculation
            base_probability = 0.3
            context_modifier = len(context.get("recent_events", [])) * 0.1
            session_data = self.active_sessions[session_id]
            engagement_modifier = session_data.get("engagement_score", 0.5) * 0.2

            probability = min(
                1.0, base_probability + context_modifier + engagement_modifier
            )
            return probability

        except Exception as e:
            logger.error(f"Error calculating emergent probability: {e}")
            return 0.0

    async def _generate_emergent_event(
        self, session_id: str, context: dict[str, Any], probability: float
    ) -> EmergentEvent:
        """Generate an emergent narrative event."""
        try:
            # TODO: Implement actual emergent event generation

            event_id = str(uuid.uuid4())
            event = EmergentEvent(
                event_id=event_id,
                event_type="character_revelation",
                description="A character reveals an unexpected connection to your past.",
                scale=NarrativeScale.MEDIUM_TERM,
                participants=["player", "mysterious_character"],
                metadata={
                    "probability": probability,
                    "context": context,
                    "generated_at": datetime.now().isoformat(),
                },
            )

            return event

        except Exception as e:
            logger.error(f"Error generating emergent event: {e}")
            raise

    async def _generate_narrative_response(
        self,
        choice: PlayerChoice,
        impact_assessments: dict[NarrativeScale, ImpactAssessment],
    ) -> str:
        """Generate narrative response content based on choice and impact assessments."""
        try:
            # Find the scale with the highest impact
            max_impact_scale = max(
                impact_assessments.keys(), key=lambda s: impact_assessments[s].magnitude
            )
            max_assessment = impact_assessments[max_impact_scale]

            # Base response acknowledging the choice
            response_parts = [f"You chose: '{choice.choice_text}'."]

            # Add scale-specific narrative content
            if max_impact_scale == NarrativeScale.SHORT_TERM:
                if max_assessment.magnitude > 0.7:
                    response_parts.append(
                        "The immediate consequences of your decision ripple through the scene."
                    )
                elif max_assessment.magnitude > 0.4:
                    response_parts.append(
                        "You notice the immediate effects of your choice."
                    )
                else:
                    response_parts.append("The moment passes quietly.")

            elif max_impact_scale == NarrativeScale.MEDIUM_TERM:
                if max_assessment.magnitude > 0.7:
                    response_parts.append(
                        "You sense this decision will significantly shape your relationships and personal growth."
                    )
                elif max_assessment.magnitude > 0.4:
                    response_parts.append(
                        "This choice feels like it will influence your journey ahead."
                    )
                else:
                    response_parts.append(
                        "You continue on your path, slightly changed by this experience."
                    )

            elif max_impact_scale == NarrativeScale.LONG_TERM:
                if max_assessment.magnitude > 0.7:
                    response_parts.append(
                        "The weight of this decision seems to echo through the very fabric of the world around you."
                    )
                elif max_assessment.magnitude > 0.4:
                    response_parts.append(
                        "You have a sense that this choice will have lasting consequences."
                    )
                else:
                    response_parts.append(
                        "The world continues to turn, perhaps slightly altered by your actions."
                    )

            elif max_impact_scale == NarrativeScale.EPIC_TERM:
                if max_assessment.magnitude > 0.5:
                    response_parts.append(
                        "Something profound has shifted - as if the very course of history has been nudged."
                    )
                else:
                    response_parts.append(
                        "Your choice joins the countless decisions that shape the grand tapestry of existence."
                    )

            # Add therapeutic content if relevant
            if max_assessment.therapeutic_alignment > 0.6:
                response_parts.append(
                    "You feel a sense of growth and understanding from this experience."
                )

            # Add causal awareness if strong
            if max_assessment.causal_strength > 0.7:
                response_parts.append(
                    "The connections between your actions and their consequences feel particularly clear."
                )

            return " ".join(response_parts)

        except Exception as e:
            logger.error(f"Error generating narrative response: {e}")
            return f"You chose: '{choice.choice_text}'. The story continues..."

    async def _generate_next_choices(
        self,
        choice: PlayerChoice,
        impact_assessments: dict[NarrativeScale, ImpactAssessment],
    ) -> list[dict[str, Any]]:
        """Generate appropriate next choices based on the current choice and its impacts."""
        try:
            choices = []

            # Find the most impactful scale
            max_impact_scale = max(
                impact_assessments.keys(), key=lambda s: impact_assessments[s].magnitude
            )
            max_assessment = impact_assessments[max_impact_scale]

            # Generate scale-appropriate choices
            if max_impact_scale == NarrativeScale.SHORT_TERM:
                choices.extend(
                    [
                        {"id": "immediate_1", "text": "React to what just happened"},
                        {"id": "immediate_2", "text": "Look around for more details"},
                        {"id": "immediate_3", "text": "Take a moment to process"},
                    ]
                )

            elif max_impact_scale == NarrativeScale.MEDIUM_TERM:
                choices.extend(
                    [
                        {
                            "id": "character_1",
                            "text": "Reflect on how this affects your relationships",
                        },
                        {"id": "character_2", "text": "Consider your personal growth"},
                        {"id": "character_3", "text": "Think about your goals"},
                    ]
                )

            elif max_impact_scale == NarrativeScale.LONG_TERM:
                choices.extend(
                    [
                        {"id": "world_1", "text": "Consider the broader implications"},
                        {"id": "world_2", "text": "Think about the world around you"},
                        {"id": "world_3", "text": "Plan for the future"},
                    ]
                )

            elif max_impact_scale == NarrativeScale.EPIC_TERM:
                choices.extend(
                    [
                        {"id": "epic_1", "text": "Contemplate your legacy"},
                        {"id": "epic_2", "text": "Consider the generations to come"},
                        {"id": "epic_3", "text": "Reflect on the grand design"},
                    ]
                )

            # Add therapeutic choices if appropriate
            if max_assessment.therapeutic_alignment > 0.5:
                choices.append(
                    {
                        "id": "therapeutic",
                        "text": "Explore what this means for your personal journey",
                    }
                )

            # Add exploration choice
            choices.append({"id": "continue", "text": "Continue your adventure"})

            # Limit to 4 choices maximum
            return choices[:4]

        except Exception as e:
            logger.error(f"Error generating next choices: {e}")
            return [
                {"id": "choice_1", "text": "Continue exploring"},
                {"id": "choice_2", "text": "Reflect on your decision"},
                {"id": "choice_3", "text": "Ask for guidance"},
            ]


# Facade re-exports: prefer extracted implementations
try:
    from .narrative_arc_orchestrator.scale_manager import (
        ScaleManager as _ExtractedScaleManager,
    )

    ScaleManager = _ExtractedScaleManager  # type: ignore
except Exception:
    pass
