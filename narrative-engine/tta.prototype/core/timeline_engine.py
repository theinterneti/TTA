"""
Timeline Engine for TTA Living Worlds

This module implements the TimelineEngine class that manages event timelines
for all world elements including characters, locations, and objects. It provides
functionality for creating, storing, and querying timeline events while maintaining
chronological consistency and supporting various filtering and retrieval operations.

Classes:
    TimelineEngine: Core engine for managing timeline events and operations
    TimeRange: Helper class for defining time ranges for queries
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

# Import the data models
try:
    from tta.prototype.models.living_worlds_models import (
        EntityType,
        EventType,
        Timeline,
        TimelineEvent,
        ValidationError,
    )
except ImportError:
    try:
        from models.living_worlds_models import (
            EntityType,
            EventType,
            Timeline,
            TimelineEvent,
            ValidationError,
        )
    except ImportError:
        # Direct import for standalone testing
        import sys
        from pathlib import Path
        models_path = Path(__file__).parent.parent / "models"
        if str(models_path) not in sys.path:
            sys.path.insert(0, str(models_path))
        from living_worlds_models import (
            EntityType,
            EventType,
            Timeline,
            TimelineEvent,
            ValidationError,
        )

logger = logging.getLogger(__name__)


@dataclass
class TimeRange:
    """Helper class for defining time ranges for timeline queries."""
    start_time: datetime
    end_time: datetime

    def __post_init__(self):
        """Validate time range after initialization."""
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")

    def contains(self, timestamp: datetime) -> bool:
        """Check if a timestamp falls within this time range."""
        return self.start_time <= timestamp <= self.end_time

    def duration(self) -> timedelta:
        """Get the duration of this time range."""
        return self.end_time - self.start_time


class TimelineEngine:
    """
    Core engine for managing timeline events and operations.

    The TimelineEngine provides functionality for creating and managing timelines
    for characters, locations, and objects. It ensures chronological consistency,
    supports various query operations, and maintains timeline integrity.
    """

    def __init__(self):
        """Initialize the Timeline Engine."""
        self.timelines: dict[str, Timeline] = {}
        self.entity_timeline_map: dict[str, str] = {}  # entity_id -> timeline_id
        self.created_at = datetime.now()
        logger.info("TimelineEngine initialized")

    def create_timeline(self, entity_id: str, entity_type: EntityType) -> Timeline:
        """
        Create a new timeline for an entity.

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (character, location, object, world)

        Returns:
            Timeline: The created timeline

        Raises:
            ValidationError: If entity_id is empty or timeline already exists
        """
        if not entity_id.strip():
            raise ValidationError("Entity ID cannot be empty")

        if entity_id in self.entity_timeline_map:
            existing_timeline_id = self.entity_timeline_map[entity_id]
            logger.warning(f"Timeline already exists for entity {entity_id}: {existing_timeline_id}")
            return self.timelines[existing_timeline_id]

        timeline = Timeline(
            entity_id=entity_id,
            entity_type=entity_type
        )

        timeline.validate()

        self.timelines[timeline.timeline_id] = timeline
        self.entity_timeline_map[entity_id] = timeline.timeline_id

        logger.info(f"Created timeline {timeline.timeline_id} for {entity_type.value} {entity_id}")
        return timeline

    def get_timeline(self, entity_id: str) -> Timeline | None:
        """
        Get the timeline for a specific entity.

        Args:
            entity_id: Unique identifier for the entity

        Returns:
            Optional[Timeline]: The timeline if found, None otherwise
        """
        timeline_id = self.entity_timeline_map.get(entity_id)
        if timeline_id:
            return self.timelines.get(timeline_id)
        return None

    def get_timeline_by_id(self, timeline_id: str) -> Timeline | None:
        """
        Get a timeline by its ID.

        Args:
            timeline_id: Unique identifier for the timeline

        Returns:
            Optional[Timeline]: The timeline if found, None otherwise
        """
        return self.timelines.get(timeline_id)

    def add_event(self, entity_id: str, event: TimelineEvent) -> bool:
        """
        Add an event to an entity's timeline.

        Args:
            entity_id: Unique identifier for the entity
            event: The timeline event to add

        Returns:
            bool: True if event was added successfully, False otherwise
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.error(f"No timeline found for entity {entity_id}")
            return False

        try:
            # Apply content validation hook if present
            validated_event = event
            if hasattr(self, 'content_validation_hook') and callable(self.content_validation_hook):
                try:
                    validated_event, is_safe = self.content_validation_hook(event, entity_id)
                    if not is_safe:
                        logger.info(f"Content filtered for event {event.event_id}")
                except Exception as e:
                    logger.warning(f"Content validation hook failed: {e}")
                    # Continue with original event if validation fails
                    validated_event = event

            # Validate chronological consistency before adding
            if not self._validate_chronological_consistency(timeline, validated_event):
                logger.error(f"Event would break chronological consistency for entity {entity_id}")
                return False

            success = timeline.add_event(validated_event)
            if success:
                logger.debug(f"Added event {validated_event.event_id} to timeline for entity {entity_id}")
                # Notify cache invalidation hook if present
                if hasattr(self, 'on_event_added') and callable(self.on_event_added):
                    try:
                        self.on_event_added(entity_id, validated_event)
                    except Exception:
                        logger.debug("Timeline event added hook failed", exc_info=True)
            return success

        except Exception as e:
            logger.error(f"Failed to add event to timeline for entity {entity_id}: {e}")
            return False

    def create_and_add_event(self, entity_id: str, event_type: EventType,
                           title: str, description: str,
                           participants: list[str] = None,
                           location_id: str = None,
                           timestamp: datetime = None,
                           significance_level: int = 5,
                           emotional_impact: float = 0.0,
                           consequences: list[str] = None,
                           tags: list[str] = None,
                           metadata: dict[str, Any] = None) -> TimelineEvent | None:
        """
        Create and add a new event to an entity's timeline.

        Args:
            entity_id: Unique identifier for the entity
            event_type: Type of the event
            title: Event title
            description: Event description
            participants: List of participant entity IDs
            location_id: Location where event occurred
            timestamp: When the event occurred (defaults to now)
            significance_level: Significance level (1-10)
            emotional_impact: Emotional impact (-1.0 to 1.0)
            consequences: List of event consequences
            tags: List of event tags
            metadata: Additional event metadata

        Returns:
            Optional[TimelineEvent]: The created event if successful, None otherwise
        """
        try:
            event = TimelineEvent(
                event_type=event_type,
                title=title,
                description=description,
                participants=participants or [],
                location_id=location_id,
                timestamp=timestamp or datetime.now(),
                significance_level=significance_level,
                emotional_impact=emotional_impact,
                consequences=consequences or [],
                tags=tags or [],
                metadata=metadata or {}
            )

            if self.add_event(entity_id, event):
                return event
            return None

        except Exception as e:
            logger.error(f"Failed to create and add event for entity {entity_id}: {e}")
            return None

    def get_events_in_range(self, entity_id: str, time_range: TimeRange) -> list[TimelineEvent]:
        """
        Get events within a specific time range for an entity.

        Args:
            entity_id: Unique identifier for the entity
            time_range: Time range to query

        Returns:
            List[TimelineEvent]: Events within the time range
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return []

        return timeline.get_events_in_range(time_range.start_time, time_range.end_time)

    def get_events_by_significance(self, entity_id: str, min_significance: int) -> list[TimelineEvent]:
        """
        Get events above a certain significance level for an entity.

        Args:
            entity_id: Unique identifier for the entity
            min_significance: Minimum significance level (1-10)

        Returns:
            List[TimelineEvent]: Events meeting the significance criteria
        """
        if not 1 <= min_significance <= 10:
            raise ValidationError("Significance level must be between 1 and 10")

        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return []

        return timeline.get_events_by_significance(min_significance)

    def get_events_by_type(self, entity_id: str, event_type: EventType) -> list[TimelineEvent]:
        """
        Get events of a specific type for an entity.

        Args:
            entity_id: Unique identifier for the entity
            event_type: Type of events to retrieve

        Returns:
            List[TimelineEvent]: Events of the specified type
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return []

        return timeline.get_events_by_type(event_type)

    def get_recent_events(self, entity_id: str, days: int = 30) -> list[TimelineEvent]:
        """
        Get recent events for an entity.

        Args:
            entity_id: Unique identifier for the entity
            days: Number of days back to look

        Returns:
            List[TimelineEvent]: Recent events
        """
        if days <= 0:
            raise ValidationError("Days must be positive")

        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return []

        return timeline.get_recent_events(days)

    def get_most_significant_events(self, entity_id: str, count: int = 10) -> list[TimelineEvent]:
        """
        Get the most significant events for an entity.

        Args:
            entity_id: Unique identifier for the entity
            count: Number of events to return

        Returns:
            List[TimelineEvent]: Most significant events
        """
        if count <= 0:
            raise ValidationError("Count must be positive")

        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return []

        return timeline.get_most_significant_events(count)

    def validate_timeline_consistency(self, entity_id: str) -> tuple[bool, list[str]]:
        """
        Validate the chronological consistency of an entity's timeline.

        Args:
            entity_id: Unique identifier for the entity

        Returns:
            Tuple[bool, List[str]]: (is_consistent, list_of_issues)
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            return False, [f"No timeline found for entity {entity_id}"]

        issues = []

        try:
            timeline.validate()
        except ValidationError as e:
            issues.append(str(e))

        # Additional consistency checks
        events = timeline.events
        if len(events) > 1:
            for i in range(1, len(events)):
                current_event = events[i]
                previous_event = events[i-1]

                # Check chronological order
                if current_event.timestamp < previous_event.timestamp:
                    issues.append(f"Event {current_event.event_id} occurs before {previous_event.event_id} but appears later in timeline")

                # Check for duplicate events
                if (current_event.timestamp == previous_event.timestamp and
                    current_event.title == previous_event.title and
                    current_event.description == previous_event.description):
                    issues.append(f"Potential duplicate events: {current_event.event_id} and {previous_event.event_id}")

        return len(issues) == 0, issues

    def _validate_chronological_consistency(self, timeline: Timeline, new_event: TimelineEvent) -> bool:
        """
        Validate that adding a new event won't break chronological consistency.

        Args:
            timeline: The timeline to validate against
            new_event: The event to be added

        Returns:
            bool: True if adding the event maintains consistency
        """
        try:
            new_event.validate()
        except ValidationError:
            return False

        # Check if event timestamp is reasonable
        now = datetime.now()
        if new_event.timestamp > now + timedelta(days=1):
            logger.warning(f"Event timestamp is more than 1 day in the future: {new_event.timestamp}")
            return False

        # Check for conflicts with existing events
        for existing_event in timeline.events:
            # Check for exact duplicates
            if (existing_event.timestamp == new_event.timestamp and
                existing_event.title == new_event.title and
                existing_event.description == new_event.description):
                logger.warning("Potential duplicate event detected")
                return False

            # Check for logical conflicts (e.g., character can't be in two places at once)
            if (existing_event.timestamp == new_event.timestamp and
                existing_event.location_id and new_event.location_id and
                existing_event.location_id != new_event.location_id and
                timeline.entity_type == EntityType.CHARACTER):

                # Check if the character is a participant in both events
                entity_id = timeline.entity_id
                if (entity_id in existing_event.participants and
                    entity_id in new_event.participants):
                    logger.warning(f"Character {entity_id} cannot be in two locations at the same time")
                    return False

        return True

    def prune_old_events(self, entity_id: str, keep_days: int = 365,
                        min_significance: int = 7) -> int:
        """
        Remove old, low-significance events from an entity's timeline.

        Args:
            entity_id: Unique identifier for the entity
            keep_days: Keep events from the last N days
            min_significance: Always keep events above this significance level

        Returns:
            int: Number of events removed
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            logger.warning(f"No timeline found for entity {entity_id}")
            return 0

        removed_count = timeline.prune_old_events(keep_days, min_significance)
        if removed_count > 0:
            logger.info(f"Pruned {removed_count} old events from timeline for entity {entity_id}")

        return removed_count

    def get_timeline_summary(self, entity_id: str) -> dict[str, Any]:
        """
        Get a summary of an entity's timeline.

        Args:
            entity_id: Unique identifier for the entity

        Returns:
            Dict[str, Any]: Timeline summary information
        """
        timeline = self.get_timeline(entity_id)
        if not timeline:
            return {
                "entity_id": entity_id,
                "timeline_exists": False,
                "error": "No timeline found"
            }

        events = timeline.events
        if not events:
            return {
                "entity_id": entity_id,
                "timeline_id": timeline.timeline_id,
                "entity_type": timeline.entity_type.value,
                "timeline_exists": True,
                "event_count": 0,
                "created_at": timeline.created_at.isoformat(),
                "last_updated": timeline.last_updated.isoformat()
            }

        # Calculate summary statistics
        significance_levels = [event.significance_level for event in events]
        emotional_impacts = [event.emotional_impact for event in events]

        return {
            "entity_id": entity_id,
            "timeline_id": timeline.timeline_id,
            "entity_type": timeline.entity_type.value,
            "timeline_exists": True,
            "event_count": len(events),
            "earliest_event": events[0].timestamp.isoformat(),
            "latest_event": events[-1].timestamp.isoformat(),
            "avg_significance": sum(significance_levels) / len(significance_levels),
            "max_significance": max(significance_levels),
            "avg_emotional_impact": sum(emotional_impacts) / len(emotional_impacts),
            "created_at": timeline.created_at.isoformat(),
            "last_updated": timeline.last_updated.isoformat()
        }

    def get_all_timelines(self) -> list[Timeline]:
        """
        Get all timelines managed by this engine.

        Returns:
            List[Timeline]: All timelines
        """
        return list(self.timelines.values())

    def get_timeline_count(self) -> int:
        """
        Get the total number of timelines.

        Returns:
            int: Number of timelines
        """
        return len(self.timelines)

    def clear_all_timelines(self) -> None:
        """Clear all timelines (use with caution)."""
        self.timelines.clear()
        self.entity_timeline_map.clear()
        logger.warning("All timelines have been cleared")
