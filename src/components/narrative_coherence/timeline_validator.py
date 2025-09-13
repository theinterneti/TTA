"""
Timeline Validator for Enhanced Narrative Coherence

Provides advanced story timeline coherence validation, character trait consistency
tracking, and temporal narrative consistency validation for the TTA platform.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    ValidationResult,
    ValidationSeverity,
)

logger = logging.getLogger(__name__)


@dataclass
class TimelineEvent:
    """Represents an event in the narrative timeline."""

    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    characters_involved: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)  # Events this depends on
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterTraitSnapshot:
    """Snapshot of character traits at a specific point in time."""

    character_id: str
    timestamp: datetime
    traits: dict[str, Any]
    emotional_state: str
    relationships: dict[str, float]  # character_id -> relationship_strength
    knowledge: set[str]  # Things the character knows
    capabilities: set[str]  # Things the character can do
    location: str | None = None


@dataclass
class NarrativeTimeline:
    """Complete narrative timeline with events and character states."""

    timeline_id: str
    session_id: str
    events: list[TimelineEvent] = field(default_factory=list)
    character_snapshots: dict[str, list[CharacterTraitSnapshot]] = field(
        default_factory=dict
    )
    world_state_changes: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class TimelineValidator:
    """
    Advanced timeline validation for narrative coherence.

    Validates story timeline coherence, tracks character trait consistency,
    and ensures temporal narrative consistency across all story elements.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

        # Timeline tracking
        self.active_timelines: dict[str, NarrativeTimeline] = {}
        self.character_trait_history: dict[str, list[CharacterTraitSnapshot]] = {}

        # Validation configuration
        self.max_timeline_gap = config.get("max_timeline_gap_minutes", 60)
        self.trait_consistency_threshold = config.get(
            "trait_consistency_threshold", 0.8
        )
        self.temporal_consistency_window = config.get(
            "temporal_consistency_window_hours", 24
        )

        # Metrics
        self.metrics = {
            "timelines_validated": 0,
            "timeline_inconsistencies": 0,
            "character_trait_violations": 0,
            "temporal_paradoxes": 0,
            "causality_violations": 0,
        }

        logger.info("TimelineValidator initialized")

    async def validate_timeline_coherence(
        self, timeline: NarrativeTimeline, new_event: TimelineEvent | None = None
    ) -> ValidationResult:
        """
        Validate timeline coherence including new events.

        Args:
            timeline: Narrative timeline to validate
            new_event: Optional new event to validate against timeline

        Returns:
            ValidationResult with timeline coherence assessment
        """
        try:
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                validation_timestamp=datetime.utcnow(),
            )

            # Validate event sequence
            sequence_issues = await self._validate_event_sequence(timeline, new_event)
            result.detected_issues.extend(sequence_issues)

            # Validate temporal consistency
            temporal_issues = await self._validate_temporal_consistency(
                timeline, new_event
            )
            result.detected_issues.extend(temporal_issues)

            # Validate causality
            causality_issues = await self._validate_causality(timeline, new_event)
            result.detected_issues.extend(causality_issues)

            # Validate character presence consistency
            presence_issues = await self._validate_character_presence(
                timeline, new_event
            )
            result.detected_issues.extend(presence_issues)

            # Calculate overall timeline coherence score
            result.consistency_score = self._calculate_timeline_coherence_score(
                result.detected_issues
            )
            result.is_valid = (
                result.consistency_score >= self.trait_consistency_threshold
            )

            # Update metrics
            self.metrics["timelines_validated"] += 1
            if not result.is_valid:
                self.metrics["timeline_inconsistencies"] += 1

            logger.debug(
                f"Timeline validation completed: score={result.consistency_score:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to validate timeline coherence: {e}")
            return ValidationResult(
                is_valid=False,
                consistency_score=0.0,
                detected_issues=[
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.TEMPORAL_PARADOX,
                        severity=ValidationSeverity.ERROR,
                        description=f"Timeline validation error: {str(e)}",
                    )
                ],
                validation_timestamp=datetime.utcnow(),
            )

    async def validate_character_trait_consistency(
        self,
        character_id: str,
        current_traits: dict[str, Any],
        timeline: NarrativeTimeline,
    ) -> ValidationResult:
        """
        Validate character trait consistency over time.

        Args:
            character_id: Character identifier
            current_traits: Current character traits
            timeline: Narrative timeline for context

        Returns:
            ValidationResult with trait consistency assessment
        """
        try:
            result = ValidationResult(
                is_valid=True,
                consistency_score=1.0,
                validation_timestamp=datetime.utcnow(),
            )

            # Get character's trait history
            trait_history = self.character_trait_history.get(character_id, [])

            if not trait_history:
                # No history to compare against - create initial snapshot
                snapshot = CharacterTraitSnapshot(
                    character_id=character_id,
                    timestamp=datetime.utcnow(),
                    traits=current_traits.copy(),
                    emotional_state=current_traits.get("emotional_state", "neutral"),
                    relationships=current_traits.get("relationships", {}),
                    knowledge=set(current_traits.get("knowledge", [])),
                    capabilities=set(current_traits.get("capabilities", [])),
                )

                if character_id not in self.character_trait_history:
                    self.character_trait_history[character_id] = []
                self.character_trait_history[character_id].append(snapshot)

                return result

            # Validate trait consistency against history
            consistency_issues = await self._validate_trait_evolution(
                character_id, current_traits, trait_history, timeline
            )
            result.detected_issues.extend(consistency_issues)

            # Validate personality consistency
            personality_issues = await self._validate_personality_consistency(
                character_id, current_traits, trait_history
            )
            result.detected_issues.extend(personality_issues)

            # Validate knowledge consistency
            knowledge_issues = await self._validate_knowledge_consistency(
                character_id, current_traits, trait_history, timeline
            )
            result.detected_issues.extend(knowledge_issues)

            # Calculate trait consistency score
            result.character_consistency = self._calculate_trait_consistency_score(
                result.detected_issues
            )
            result.consistency_score = result.character_consistency
            result.is_valid = (
                result.consistency_score >= self.trait_consistency_threshold
            )

            # Update character trait history
            await self._update_character_trait_history(character_id, current_traits)

            # Update metrics
            if result.detected_issues:
                self.metrics["character_trait_violations"] += len(
                    result.detected_issues
                )

            logger.debug(
                f"Character trait validation completed: score={result.consistency_score:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to validate character trait consistency: {e}")
            return ValidationResult(
                is_valid=False,
                consistency_score=0.0,
                detected_issues=[
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                        severity=ValidationSeverity.ERROR,
                        description=f"Character trait validation error: {str(e)}",
                    )
                ],
                validation_timestamp=datetime.utcnow(),
            )

    async def create_timeline(self, session_id: str) -> str:
        """Create a new narrative timeline."""
        timeline_id = str(uuid.uuid4())
        timeline = NarrativeTimeline(
            timeline_id=timeline_id,
            session_id=session_id,
        )
        self.active_timelines[timeline_id] = timeline
        return timeline_id

    async def add_timeline_event(self, timeline_id: str, event: TimelineEvent) -> bool:
        """Add an event to a timeline."""
        try:
            if timeline_id not in self.active_timelines:
                logger.error(f"Timeline {timeline_id} not found")
                return False

            timeline = self.active_timelines[timeline_id]

            # Validate event before adding
            validation_result = await self.validate_timeline_coherence(timeline, event)

            if validation_result.is_valid:
                timeline.events.append(event)
                timeline.events.sort(
                    key=lambda e: e.timestamp
                )  # Keep chronological order
                timeline.last_updated = datetime.utcnow()
                return True
            else:
                logger.warning(
                    f"Event validation failed: {len(validation_result.detected_issues)} issues"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to add timeline event: {e}")
            return False

    async def get_timeline(self, timeline_id: str) -> NarrativeTimeline | None:
        """Get timeline by ID."""
        return self.active_timelines.get(timeline_id)

    async def get_character_trait_history(
        self, character_id: str
    ) -> list[CharacterTraitSnapshot]:
        """Get character trait history."""
        return self.character_trait_history.get(character_id, [])

    async def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        return {
            **self.metrics,
            "active_timelines": len(self.active_timelines),
            "tracked_characters": len(self.character_trait_history),
        }

    # Private validation methods

    async def _validate_event_sequence(
        self, timeline: NarrativeTimeline, new_event: TimelineEvent | None
    ) -> list[ConsistencyIssue]:
        """Validate the sequence of events in the timeline."""
        issues = []

        events = timeline.events.copy()
        if new_event:
            events.append(new_event)

        # Sort events by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Check for temporal gaps
        for i in range(1, len(events)):
            prev_event = events[i - 1]
            curr_event = events[i]

            time_gap = (
                curr_event.timestamp - prev_event.timestamp
            ).total_seconds() / 60

            if time_gap > self.max_timeline_gap:
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.TEMPORAL_PARADOX,
                        severity=ValidationSeverity.WARNING,
                        description=f"Large time gap ({time_gap:.1f} minutes) between events",
                        related_content_ids=[prev_event.event_id, curr_event.event_id],
                    )
                )

        return issues

    async def _validate_temporal_consistency(
        self, timeline: NarrativeTimeline, new_event: TimelineEvent | None
    ) -> list[ConsistencyIssue]:
        """Validate temporal consistency of events."""
        issues = []

        events = timeline.events.copy()
        if new_event:
            events.append(new_event)

        # Check for temporal paradoxes
        for event in events:
            for dependency_id in event.dependencies:
                dependency_event = next(
                    (e for e in events if e.event_id == dependency_id), None
                )

                if dependency_event and dependency_event.timestamp > event.timestamp:
                    issues.append(
                        ConsistencyIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=ConsistencyIssueType.TEMPORAL_PARADOX,
                            severity=ValidationSeverity.ERROR,
                            description=f"Event {event.event_id} depends on future event {dependency_id}",
                            related_content_ids=[event.event_id, dependency_id],
                        )
                    )
                    self.metrics["temporal_paradoxes"] += 1

        return issues

    async def _validate_causality(
        self, timeline: NarrativeTimeline, new_event: TimelineEvent | None
    ) -> list[ConsistencyIssue]:
        """Validate cause-and-effect relationships."""
        issues = []

        events = timeline.events.copy()
        if new_event:
            events.append(new_event)

        # Check causality violations
        for event in events:
            for consequence in event.consequences:
                # Find events that should be consequences
                consequence_events = [
                    e for e in events if consequence in e.description.lower()
                ]

                for cons_event in consequence_events:
                    if cons_event.timestamp <= event.timestamp:
                        issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
                                severity=ValidationSeverity.WARNING,
                                description=f"Consequence event {cons_event.event_id} occurs before cause {event.event_id}",
                                related_content_ids=[
                                    event.event_id,
                                    cons_event.event_id,
                                ],
                            )
                        )
                        self.metrics["causality_violations"] += 1

        return issues

    async def _validate_character_presence(
        self, timeline: NarrativeTimeline, new_event: TimelineEvent | None
    ) -> list[ConsistencyIssue]:
        """Validate character presence consistency."""
        issues = []

        events = timeline.events.copy()
        if new_event:
            events.append(new_event)

        # Track character locations over time
        character_locations: dict[str, list[tuple[datetime, str]]] = {}

        for event in sorted(events, key=lambda e: e.timestamp):
            for character in event.characters_involved:
                if character not in character_locations:
                    character_locations[character] = []

                for location in event.locations:
                    character_locations[character].append((event.timestamp, location))

        # Check for impossible character movements
        for character, location_history in character_locations.items():
            for i in range(1, len(location_history)):
                prev_time, prev_location = location_history[i - 1]
                curr_time, curr_location = location_history[i]

                if prev_location != curr_location:
                    time_diff = (curr_time - prev_time).total_seconds() / 60  # minutes

                    # Check if movement time is reasonable (placeholder logic)
                    if time_diff < 1:  # Less than 1 minute to change locations
                        issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                                severity=ValidationSeverity.WARNING,
                                description=f"Character {character} moved too quickly from {prev_location} to {curr_location}",
                                related_content_ids=[character],
                            )
                        )

        return issues

    async def _validate_trait_evolution(
        self,
        character_id: str,
        current_traits: dict[str, Any],
        trait_history: list[CharacterTraitSnapshot],
        timeline: NarrativeTimeline,
    ) -> list[ConsistencyIssue]:
        """Validate character trait evolution over time."""
        issues: list[ConsistencyIssue] = []

        if not trait_history:
            return issues

        latest_snapshot = trait_history[-1]

        # Check for sudden personality changes
        core_traits = ["personality", "values", "beliefs", "fears"]

        for trait in core_traits:
            if trait in current_traits and trait in latest_snapshot.traits:
                current_value = current_traits[trait]
                previous_value = latest_snapshot.traits[trait]

                # Check for dramatic changes without justification
                if self._traits_differ_significantly(current_value, previous_value):
                    # Look for justifying events in timeline
                    justifying_events = self._find_trait_change_justification(
                        character_id, trait, timeline, latest_snapshot.timestamp
                    )

                    if not justifying_events:
                        issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                                severity=ValidationSeverity.WARNING,
                                description=f"Character {character_id} trait '{trait}' changed significantly without justification",
                                related_content_ids=[character_id],
                            )
                        )

        return issues

    async def _validate_personality_consistency(
        self,
        character_id: str,
        current_traits: dict[str, Any],
        trait_history: list[CharacterTraitSnapshot],
    ) -> list[ConsistencyIssue]:
        """Validate personality consistency."""
        issues: list[ConsistencyIssue] = []

        if not trait_history:
            return issues

        # Check personality stability
        personality_traits = current_traits.get("personality", {})

        for snapshot in trait_history[-3:]:  # Check last 3 snapshots
            historical_personality = snapshot.traits.get("personality", {})

            for trait_name, trait_value in personality_traits.items():
                if trait_name in historical_personality:
                    historical_value = historical_personality[trait_name]

                    # Check for contradictory personality traits
                    if self._personality_traits_contradict(
                        trait_value, historical_value
                    ):
                        issues.append(
                            ConsistencyIssue(
                                issue_id=str(uuid.uuid4()),
                                issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                                severity=ValidationSeverity.ERROR,
                                description=f"Character {character_id} personality trait '{trait_name}' contradicts previous behavior",
                                related_content_ids=[character_id],
                            )
                        )

        return issues

    async def _validate_knowledge_consistency(
        self,
        character_id: str,
        current_traits: dict[str, Any],
        trait_history: list[CharacterTraitSnapshot],
        timeline: NarrativeTimeline,
    ) -> list[ConsistencyIssue]:
        """Validate character knowledge consistency."""
        issues: list[ConsistencyIssue] = []

        if not trait_history:
            return issues

        current_knowledge = set(current_traits.get("knowledge", []))
        latest_snapshot = trait_history[-1]
        previous_knowledge = latest_snapshot.knowledge

        # Check for lost knowledge without justification
        lost_knowledge = previous_knowledge - current_knowledge

        for lost_item in lost_knowledge:
            # Look for events that could justify knowledge loss
            justifying_events = self._find_knowledge_loss_justification(
                character_id, lost_item, timeline, latest_snapshot.timestamp
            )

            if not justifying_events:
                issues.append(
                    ConsistencyIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
                        severity=ValidationSeverity.WARNING,
                        description=f"Character {character_id} lost knowledge '{lost_item}' without justification",
                        related_content_ids=[character_id],
                    )
                )

        return issues

    async def _update_character_trait_history(
        self, character_id: str, current_traits: dict[str, Any]
    ) -> None:
        """Update character trait history with current traits."""
        snapshot = CharacterTraitSnapshot(
            character_id=character_id,
            timestamp=datetime.utcnow(),
            traits=current_traits.copy(),
            emotional_state=current_traits.get("emotional_state", "neutral"),
            relationships=current_traits.get("relationships", {}),
            knowledge=set(current_traits.get("knowledge", [])),
            capabilities=set(current_traits.get("capabilities", [])),
            location=current_traits.get("current_location"),
        )

        if character_id not in self.character_trait_history:
            self.character_trait_history[character_id] = []

        self.character_trait_history[character_id].append(snapshot)

        # Keep only recent history (last 50 snapshots)
        if len(self.character_trait_history[character_id]) > 50:
            self.character_trait_history[character_id] = self.character_trait_history[
                character_id
            ][-50:]

    # Helper methods

    def _calculate_timeline_coherence_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        """Calculate timeline coherence score based on issues."""
        if not issues:
            return 1.0

        severity_weights = {
            ValidationSeverity.INFO: 0.05,
            ValidationSeverity.WARNING: 0.15,
            ValidationSeverity.ERROR: 0.3,
            ValidationSeverity.CRITICAL: 0.5,
        }

        total_penalty = sum(
            severity_weights.get(issue.severity, 0.1) for issue in issues
        )
        return max(0.0, 1.0 - total_penalty)

    def _calculate_trait_consistency_score(
        self, issues: list[ConsistencyIssue]
    ) -> float:
        """Calculate trait consistency score based on issues."""
        return self._calculate_timeline_coherence_score(issues)

    def _traits_differ_significantly(
        self, current_value: Any, previous_value: Any
    ) -> bool:
        """Check if traits differ significantly."""
        if isinstance(current_value, (int, float)) and isinstance(
            previous_value, (int, float)
        ):
            return abs(current_value - previous_value) > 0.5
        elif isinstance(current_value, str) and isinstance(previous_value, str):
            return current_value.lower() != previous_value.lower()
        else:
            return current_value != previous_value

    def _find_trait_change_justification(
        self,
        character_id: str,
        trait: str,
        timeline: NarrativeTimeline,
        since_timestamp: datetime,
    ) -> list[TimelineEvent]:
        """Find events that could justify a trait change."""
        justifying_events = []

        for event in timeline.events:
            if (
                event.timestamp > since_timestamp
                and character_id in event.characters_involved
                and any(
                    keyword in event.description.lower()
                    for keyword in [
                        "trauma",
                        "revelation",
                        "growth",
                        "change",
                        "learn",
                        "realize",
                    ]
                )
            ):
                justifying_events.append(event)

        return justifying_events

    def _personality_traits_contradict(
        self, current_value: Any, historical_value: Any
    ) -> bool:
        """Check if personality traits contradict each other."""
        # Simple contradiction check - can be enhanced
        contradictory_pairs = [
            ("introverted", "extroverted"),
            ("aggressive", "peaceful"),
            ("optimistic", "pessimistic"),
            ("trusting", "suspicious"),
        ]

        current_str = str(current_value).lower()
        historical_str = str(historical_value).lower()

        for trait1, trait2 in contradictory_pairs:
            if (trait1 in current_str and trait2 in historical_str) or (
                trait2 in current_str and trait1 in historical_str
            ):
                return True

        return False

    def _find_knowledge_loss_justification(
        self,
        character_id: str,
        lost_knowledge: str,
        timeline: NarrativeTimeline,
        since_timestamp: datetime,
    ) -> list[TimelineEvent]:
        """Find events that could justify knowledge loss."""
        justifying_events = []

        for event in timeline.events:
            if (
                event.timestamp > since_timestamp
                and character_id in event.characters_involved
                and any(
                    keyword in event.description.lower()
                    for keyword in ["forget", "amnesia", "memory", "confusion", "mind"]
                )
            ):
                justifying_events.append(event)

        return justifying_events
