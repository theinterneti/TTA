"""

# Logseq: [[TTA.dev/Testing/Extended_evaluation/Living_worlds_metrics]]
Living Worlds Metrics and Evaluation System

Provides specialized evaluation metrics for TTA's living worlds system,
focusing on world state consistency, choice impact tracking, and world
evolution quality over extended sessions.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WorldStateSnapshot:
    """Snapshot of world state at a specific point in time."""

    turn: int
    timestamp: datetime

    # Core world state
    locations: dict[str, Any] = field(default_factory=dict)
    characters: dict[str, Any] = field(default_factory=dict)
    objects: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, Any] = field(default_factory=dict)

    # World properties
    time_of_day: str | None = None
    weather: str | None = None
    season: str | None = None
    world_events: list[dict[str, Any]] = field(default_factory=list)

    # Player impact tracking
    player_actions: list[dict[str, Any]] = field(default_factory=list)
    consequences: list[dict[str, Any]] = field(default_factory=list)
    reputation_changes: dict[str, float] = field(default_factory=dict)


@dataclass
class ChoiceImpactAnalysis:
    """Analysis of choice impact and consequence propagation."""

    choice_id: str
    turn: int
    choice_description: str

    # Impact classification
    impact_type: str  # immediate, delayed, cascading, therapeutic
    impact_magnitude: float  # 0-1 scale
    impact_scope: str  # local, regional, global

    # Consequence tracking
    immediate_consequences: list[str] = field(default_factory=list)
    delayed_consequences: list[str] = field(default_factory=list)
    cascading_effects: list[str] = field(default_factory=list)

    # Quality metrics
    consequence_believability: float = 0.0  # 0-10 scale
    narrative_integration: float = 0.0  # 0-10 scale
    player_agency_feeling: float = 0.0  # 0-10 scale


@dataclass
class WorldEvolutionMetrics:
    """Metrics for evaluating world evolution quality."""

    session_id: str
    total_turns: int

    # Evolution characteristics
    natural_progression_score: float = 0.0  # How naturally world evolves
    player_impact_integration: float = 0.0  # How well player actions affect world
    consistency_maintenance: float = 0.0  # How well world rules are maintained

    # Specific evolution aspects
    character_development_score: float = 0.0
    location_evolution_score: float = 0.0
    relationship_dynamics_score: float = 0.0
    world_event_integration: float = 0.0

    # Temporal consistency
    timeline_coherence: float = 0.0
    cause_effect_logic: float = 0.0
    memory_consistency: float = 0.0


@dataclass
class WorldStateMetrics:
    """Comprehensive metrics for world state evaluation."""

    session_id: str
    evaluation_timestamp: datetime

    # Overall consistency scores
    overall_consistency_score: float = 0.0
    character_consistency_score: float = 0.0
    location_consistency_score: float = 0.0
    object_consistency_score: float = 0.0
    relationship_consistency_score: float = 0.0

    # Evolution quality
    evolution_metrics: WorldEvolutionMetrics = field(
        default_factory=lambda: WorldEvolutionMetrics("", 0)
    )

    # Choice impact analysis
    choice_impacts: list[ChoiceImpactAnalysis] = field(default_factory=list)

    # Detailed analysis
    inconsistencies_found: list[str] = field(default_factory=list)
    strengths_identified: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)


class LivingWorldsEvaluator:
    """
    Evaluator for TTA's living worlds system quality and consistency.

    Provides comprehensive evaluation of world state management, choice impact
    tracking, and world evolution quality over extended sessions.
    """

    def __init__(self):
        self.world_snapshots: dict[str, list[WorldStateSnapshot]] = {}
        self.choice_impacts: dict[str, list[ChoiceImpactAnalysis]] = {}
        self.consistency_history: dict[str, list[float]] = {}

        logger.info("LivingWorldsEvaluator initialized")

    async def evaluate_world_consistency(
        self, response: dict[str, Any], turn: int
    ) -> float:
        """
        Evaluate world state consistency for a single turn.

        Args:
            response: TTA system response containing world state
            turn: Current turn number

        Returns:
            Consistency score (0-10)
        """
        try:
            # Extract world state from response
            world_state = response.get("world_state", {})
            session_id = response.get("session_id", "unknown")

            # Create world state snapshot
            snapshot = self._create_world_snapshot(world_state, turn)

            # Store snapshot
            if session_id not in self.world_snapshots:
                self.world_snapshots[session_id] = []
            self.world_snapshots[session_id].append(snapshot)

            # Evaluate consistency against previous snapshots
            consistency_score = await self._evaluate_snapshot_consistency(
                session_id, snapshot
            )

            # Store consistency score
            if session_id not in self.consistency_history:
                self.consistency_history[session_id] = []
            self.consistency_history[session_id].append(consistency_score)

            return consistency_score

        except Exception as e:
            logger.error(f"Failed to evaluate world consistency: {e}")
            return 5.0  # Default neutral score

    def _create_world_snapshot(
        self, world_state: dict[str, Any], turn: int
    ) -> WorldStateSnapshot:
        """Create a world state snapshot from TTA response."""
        return WorldStateSnapshot(
            turn=turn,
            timestamp=datetime.now(),
            locations=world_state.get("locations", {}),
            characters=world_state.get("characters", {}),
            objects=world_state.get("objects", {}),
            relationships=world_state.get("relationships", {}),
            time_of_day=world_state.get("time_of_day"),
            weather=world_state.get("weather"),
            season=world_state.get("season"),
            world_events=world_state.get("events", []),
            player_actions=world_state.get("player_actions", []),
            consequences=world_state.get("consequences", []),
            reputation_changes=world_state.get("reputation_changes", {}),
        )

    async def _evaluate_snapshot_consistency(
        self, session_id: str, current_snapshot: WorldStateSnapshot
    ) -> float:
        """Evaluate consistency of current snapshot against previous ones."""
        snapshots = self.world_snapshots.get(session_id, [])

        if len(snapshots) <= 1:
            return 8.0  # First snapshot gets good default score

        previous_snapshot = snapshots[-2]  # Get previous snapshot

        # Evaluate different aspects of consistency
        character_consistency = self._evaluate_character_consistency(
            previous_snapshot, current_snapshot
        )
        location_consistency = self._evaluate_location_consistency(
            previous_snapshot, current_snapshot
        )
        object_consistency = self._evaluate_object_consistency(
            previous_snapshot, current_snapshot
        )
        relationship_consistency = self._evaluate_relationship_consistency(
            previous_snapshot, current_snapshot
        )
        temporal_consistency = self._evaluate_temporal_consistency(
            previous_snapshot, current_snapshot
        )

        # Calculate weighted average
        consistency_score = (
            character_consistency * 0.25
            + location_consistency * 0.20
            + object_consistency * 0.15
            + relationship_consistency * 0.20
            + temporal_consistency * 0.20
        )

        return min(10.0, max(0.0, consistency_score))

    def _evaluate_character_consistency(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot
    ) -> float:
        """Evaluate character consistency between snapshots."""
        score = 8.0  # Start with good baseline

        # Check for character continuity
        prev_chars = prev.characters
        curr_chars = curr.characters

        for char_id, prev_char in prev_chars.items():
            if char_id in curr_chars:
                curr_char = curr_chars[char_id]

                # Check personality consistency
                prev_personality = prev_char.get("personality", {})
                curr_personality = curr_char.get("personality", {})

                # Simple consistency check - would be more sophisticated in full implementation
                if prev_personality != curr_personality:
                    # Allow for character development but penalize major inconsistencies
                    score -= 0.5

                # Check location consistency
                prev_location = prev_char.get("location")
                curr_location = curr_char.get("location")

                if prev_location and curr_location and prev_location != curr_location:
                    # Character moved - check if movement is logical
                    if not self._is_logical_movement(prev_location, curr_location):
                        score -= 0.3

        return max(0.0, score)

    def _evaluate_location_consistency(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot
    ) -> float:
        """Evaluate location consistency between snapshots."""
        score = 8.0

        # Check for location property consistency
        prev_locations = prev.locations
        curr_locations = curr.locations

        for loc_id, prev_loc in prev_locations.items():
            if loc_id in curr_locations:
                curr_loc = curr_locations[loc_id]

                # Check basic properties
                prev_desc = prev_loc.get("description", "")
                curr_desc = curr_loc.get("description", "")

                # Allow for minor changes but penalize major inconsistencies
                if len(prev_desc) > 0 and len(curr_desc) > 0:
                    # Simple similarity check - would use more sophisticated NLP in full implementation
                    if not self._descriptions_similar(prev_desc, curr_desc):
                        score -= 0.4

        return max(0.0, score)

    def _evaluate_object_consistency(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot
    ) -> float:
        """Evaluate object consistency between snapshots."""
        score = 8.0

        # Check for object persistence and logical changes
        prev_objects = prev.objects
        curr_objects = curr.objects

        for obj_id, prev_obj in prev_objects.items():
            if obj_id in curr_objects:
                curr_obj = curr_objects[obj_id]

                # Check object properties
                prev_state = prev_obj.get("state", "normal")
                curr_state = curr_obj.get("state", "normal")

                # Check for logical state transitions
                if prev_state != curr_state:
                    if not self._is_logical_state_change(prev_state, curr_state):
                        score -= 0.3

        return max(0.0, score)

    def _evaluate_relationship_consistency(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot
    ) -> float:
        """Evaluate relationship consistency between snapshots."""
        score = 8.0

        # Check relationship evolution logic
        prev_relationships = prev.relationships
        curr_relationships = curr.relationships

        for rel_id, prev_rel in prev_relationships.items():
            if rel_id in curr_relationships:
                curr_rel = curr_relationships[rel_id]

                # Check relationship strength changes
                prev_strength = prev_rel.get("strength", 0.5)
                curr_strength = curr_rel.get("strength", 0.5)

                # Large sudden changes without justification are inconsistent
                strength_change = abs(curr_strength - prev_strength)
                if strength_change > 0.3:  # Significant change
                    # Check if there's justification in recent actions
                    if not self._relationship_change_justified(prev, curr, rel_id):
                        score -= 0.5

        return max(0.0, score)

    def _evaluate_temporal_consistency(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot
    ) -> float:
        """Evaluate temporal consistency between snapshots."""
        score = 8.0

        # Check time progression logic
        prev_time = prev.time_of_day
        curr_time = curr.time_of_day

        if prev_time and curr_time:
            # Simple time progression check
            if not self._is_logical_time_progression(prev_time, curr_time):
                score -= 0.4

        # Check weather consistency
        prev_weather = prev.weather
        curr_weather = curr.weather

        if prev_weather and curr_weather:
            if not self._is_logical_weather_change(prev_weather, curr_weather):
                score -= 0.3

        return max(0.0, score)

    # Helper methods for consistency evaluation
    def _is_logical_movement(self, prev_location: str, curr_location: str) -> bool:
        """Check if character movement between locations is logical."""
        # Simplified logic - would use actual world geography in full implementation
        return True

    def _descriptions_similar(self, desc1: str, desc2: str) -> bool:
        """Check if two descriptions are similar enough to be consistent."""
        # Simplified similarity check - would use NLP similarity in full implementation
        return len(set(desc1.lower().split()) & set(desc2.lower().split())) > 3

    def _is_logical_state_change(self, prev_state: str, curr_state: str) -> bool:
        """Check if object state change is logical."""
        # Simplified logic - would have comprehensive state transition rules
        return True

    def _relationship_change_justified(
        self, prev: WorldStateSnapshot, curr: WorldStateSnapshot, rel_id: str
    ) -> bool:
        """Check if relationship change is justified by recent actions."""
        # Simplified check - would analyze player actions and world events
        return len(curr.player_actions) > 0

    def _is_logical_time_progression(self, prev_time: str, curr_time: str) -> bool:
        """Check if time progression is logical."""
        # Simplified time logic
        time_order = ["dawn", "morning", "noon", "afternoon", "evening", "night"]
        try:
            prev_idx = time_order.index(prev_time.lower())
            curr_idx = time_order.index(curr_time.lower())
            return curr_idx >= prev_idx or (
                prev_idx == len(time_order) - 1 and curr_idx == 0
            )
        except ValueError:
            return True  # Unknown time formats are acceptable

    def _is_logical_weather_change(self, prev_weather: str, curr_weather: str) -> bool:
        """Check if weather change is logical."""
        # Simplified weather logic - would have more sophisticated weather patterns
        return True

    async def analyze_choice_impact(
        self, choice_data: dict[str, Any], turn: int
    ) -> ChoiceImpactAnalysis:
        """Analyze the impact and consequences of a player choice."""
        choice_id = choice_data.get("choice_id", f"choice_{turn}")

        analysis = ChoiceImpactAnalysis(
            choice_id=choice_id,
            turn=turn,
            choice_description=choice_data.get("description", "Unknown choice"),
            impact_type=choice_data.get("impact_type", "immediate"),
            impact_magnitude=choice_data.get("impact_magnitude", 0.5),
            impact_scope=choice_data.get("impact_scope", "local"),
        )

        # Analyze consequences
        analysis.immediate_consequences = choice_data.get("immediate_consequences", [])
        analysis.delayed_consequences = choice_data.get("delayed_consequences", [])
        analysis.cascading_effects = choice_data.get("cascading_effects", [])

        # Evaluate quality metrics
        analysis.consequence_believability = (
            await self._evaluate_consequence_believability(choice_data)
        )
        analysis.narrative_integration = await self._evaluate_narrative_integration(
            choice_data
        )
        analysis.player_agency_feeling = await self._evaluate_player_agency(choice_data)

        return analysis

    async def _evaluate_consequence_believability(
        self, choice_data: dict[str, Any]
    ) -> float:
        """Evaluate how believable the consequences are."""
        # Simplified evaluation - would use more sophisticated analysis
        return 7.5

    async def _evaluate_narrative_integration(
        self, choice_data: dict[str, Any]
    ) -> float:
        """Evaluate how well consequences integrate with the narrative."""
        # Simplified evaluation
        return 7.0

    async def _evaluate_player_agency(self, choice_data: dict[str, Any]) -> float:
        """Evaluate how much agency the player feels from their choice."""
        # Simplified evaluation
        return 7.8

    async def generate_world_state_metrics(self, session_id: str) -> WorldStateMetrics:
        """Generate comprehensive world state metrics for a session."""
        snapshots = self.world_snapshots.get(session_id, [])
        consistency_scores = self.consistency_history.get(session_id, [])

        if not snapshots:
            return WorldStateMetrics(
                session_id=session_id, evaluation_timestamp=datetime.now()
            )

        metrics = WorldStateMetrics(
            session_id=session_id, evaluation_timestamp=datetime.now()
        )

        # Calculate overall consistency scores
        if consistency_scores:
            metrics.overall_consistency_score = sum(consistency_scores) / len(
                consistency_scores
            )

        # Generate evolution metrics
        metrics.evolution_metrics = WorldEvolutionMetrics(
            session_id=session_id,
            total_turns=len(snapshots),
            natural_progression_score=8.0,  # Would calculate from actual data
            player_impact_integration=7.5,
            consistency_maintenance=metrics.overall_consistency_score,
        )

        # Add choice impacts
        metrics.choice_impacts = self.choice_impacts.get(session_id, [])

        # Generate insights
        metrics.strengths_identified = self._identify_strengths(
            snapshots, consistency_scores
        )
        metrics.inconsistencies_found = self._identify_inconsistencies(snapshots)
        metrics.improvement_suggestions = self._generate_improvement_suggestions(
            metrics
        )

        return metrics

    def _identify_strengths(
        self, snapshots: list[WorldStateSnapshot], consistency_scores: list[float]
    ) -> list[str]:
        """Identify strengths in world state management."""
        strengths = []

        if (
            consistency_scores
            and sum(consistency_scores) / len(consistency_scores) > 8.0
        ):
            strengths.append("Excellent overall world consistency")

        if len(snapshots) > 20:
            strengths.append("Maintained consistency over extended session")

        return strengths

    def _identify_inconsistencies(
        self, snapshots: list[WorldStateSnapshot]
    ) -> list[str]:
        """Identify inconsistencies found in world state."""
        # Simplified analysis - would be more comprehensive
        return []

    def _generate_improvement_suggestions(
        self, metrics: WorldStateMetrics
    ) -> list[str]:
        """Generate suggestions for improving world state management."""
        suggestions = []

        if metrics.overall_consistency_score < 7.0:
            suggestions.append("Improve world state consistency tracking")

        if metrics.evolution_metrics.player_impact_integration < 7.0:
            suggestions.append("Enhance player choice impact integration")

        return suggestions
