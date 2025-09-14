"""
Unit tests for Timeline Engine

This module contains comprehensive unit tests for the TimelineEngine class,
testing all functionality including event creation, storage, retrieval,
chronological consistency validation, and error handling.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from core.timeline_engine import TimelineEngine, TimeRange
    from models.living_worlds_models import (
        EntityType,
        EventType,
        Timeline,
        TimelineEvent,
        ValidationError,
    )
except ImportError:
    # Fallback for different import contexts
    from tta.prototype.core.timeline_engine import TimelineEngine, TimeRange
    from tta.prototype.models.living_worlds_models import (
        EntityType,
        EventType,
        Timeline,
        TimelineEvent,
        ValidationError,
    )


class TestTimeRange(unittest.TestCase):
    """Test cases for TimeRange helper class."""

    def test_time_range_creation(self):
        """Test creating a valid time range."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        time_range = TimeRange(start, end)

        self.assertEqual(time_range.start_time, start)
        self.assertEqual(time_range.end_time, end)

    def test_time_range_invalid(self):
        """Test creating an invalid time range."""
        start = datetime.now()
        end = start - timedelta(hours=1)  # End before start

        with self.assertRaises(ValidationError):
            TimeRange(start, end)

    def test_time_range_contains(self):
        """Test time range contains method."""
        start = datetime.now()
        end = start + timedelta(hours=2)
        time_range = TimeRange(start, end)

        # Test timestamp within range
        middle = start + timedelta(hours=1)
        self.assertTrue(time_range.contains(middle))

        # Test timestamp at boundaries
        self.assertTrue(time_range.contains(start))
        self.assertTrue(time_range.contains(end))

        # Test timestamp outside range
        before = start - timedelta(minutes=1)
        after = end + timedelta(minutes=1)
        self.assertFalse(time_range.contains(before))
        self.assertFalse(time_range.contains(after))

    def test_time_range_duration(self):
        """Test time range duration calculation."""
        start = datetime.now()
        end = start + timedelta(hours=3, minutes=30)
        time_range = TimeRange(start, end)

        expected_duration = timedelta(hours=3, minutes=30)
        self.assertEqual(time_range.duration(), expected_duration)


class TestTimelineEngine(unittest.TestCase):
    """Test cases for TimelineEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = TimelineEngine()
        self.test_entity_id = "test_character_001"
        self.test_location_id = "test_location_001"
        self.test_object_id = "test_object_001"

    def test_engine_initialization(self):
        """Test timeline engine initialization."""
        self.assertIsInstance(self.engine.timelines, dict)
        self.assertIsInstance(self.engine.entity_timeline_map, dict)
        self.assertEqual(len(self.engine.timelines), 0)
        self.assertEqual(len(self.engine.entity_timeline_map), 0)
        self.assertIsInstance(self.engine.created_at, datetime)

    def test_create_timeline(self):
        """Test creating a new timeline."""
        timeline = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        self.assertIsInstance(timeline, Timeline)
        self.assertEqual(timeline.entity_id, self.test_entity_id)
        self.assertEqual(timeline.entity_type, EntityType.CHARACTER)
        self.assertIn(timeline.timeline_id, self.engine.timelines)
        self.assertEqual(self.engine.entity_timeline_map[self.test_entity_id], timeline.timeline_id)

    def test_create_timeline_empty_entity_id(self):
        """Test creating timeline with empty entity ID."""
        with self.assertRaises(ValidationError):
            self.engine.create_timeline("", EntityType.CHARACTER)

        with self.assertRaises(ValidationError):
            self.engine.create_timeline("   ", EntityType.CHARACTER)

    def test_create_timeline_duplicate(self):
        """Test creating timeline for entity that already has one."""
        # Create first timeline
        timeline1 = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Attempt to create second timeline for same entity
        timeline2 = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Should return the existing timeline
        self.assertEqual(timeline1.timeline_id, timeline2.timeline_id)
        self.assertEqual(len(self.engine.timelines), 1)

    def test_get_timeline(self):
        """Test retrieving a timeline by entity ID."""
        # Test getting non-existent timeline
        timeline = self.engine.get_timeline(self.test_entity_id)
        self.assertIsNone(timeline)

        # Create timeline and test retrieval
        created_timeline = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)
        retrieved_timeline = self.engine.get_timeline(self.test_entity_id)

        self.assertEqual(created_timeline.timeline_id, retrieved_timeline.timeline_id)

    def test_get_timeline_by_id(self):
        """Test retrieving a timeline by timeline ID."""
        # Create timeline
        timeline = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Test retrieval by timeline ID
        retrieved = self.engine.get_timeline_by_id(timeline.timeline_id)
        self.assertEqual(timeline.timeline_id, retrieved.timeline_id)

        # Test non-existent timeline ID
        non_existent = self.engine.get_timeline_by_id("non_existent_id")
        self.assertIsNone(non_existent)

    def test_add_event(self):
        """Test adding an event to a timeline."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create event
        event = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Test Conversation",
            description="A test conversation event",
            participants=[self.test_entity_id],
            significance_level=5
        )

        # Add event
        success = self.engine.add_event(self.test_entity_id, event)
        self.assertTrue(success)

        # Verify event was added
        timeline = self.engine.get_timeline(self.test_entity_id)
        self.assertEqual(len(timeline.events), 1)
        self.assertEqual(timeline.events[0].event_id, event.event_id)

    def test_add_event_no_timeline(self):
        """Test adding event to non-existent timeline."""
        event = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Test Event",
            description="Test description"
        )

        success = self.engine.add_event("non_existent_entity", event)
        self.assertFalse(success)

    def test_create_and_add_event(self):
        """Test creating and adding an event in one operation."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create and add event
        event = self.engine.create_and_add_event(
            entity_id=self.test_entity_id,
            event_type=EventType.MEETING,
            title="Test Meeting",
            description="A test meeting event",
            participants=[self.test_entity_id, "other_character"],
            location_id=self.test_location_id,
            significance_level=7,
            emotional_impact=0.5,
            consequences=["Made new friend"],
            tags=["social", "positive"],
            metadata={"duration": "1 hour"}
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.title, "Test Meeting")
        self.assertEqual(event.significance_level, 7)
        self.assertEqual(event.emotional_impact, 0.5)

        # Verify event was added to timeline
        timeline = self.engine.get_timeline(self.test_entity_id)
        self.assertEqual(len(timeline.events), 1)

    def test_get_events_in_range(self):
        """Test retrieving events within a time range."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create events at different times
        now = datetime.now()
        event1_time = now - timedelta(hours=2)
        event2_time = now - timedelta(hours=1)
        event3_time = now + timedelta(hours=1)

        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Event 1", "Description 1",
            timestamp=event1_time
        )
        event2 = self.engine.create_and_add_event(
            self.test_entity_id, EventType.MEETING, "Event 2", "Description 2",
            timestamp=event2_time
        )
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.TRAVEL, "Event 3", "Description 3",
            timestamp=event3_time
        )

        # Test range that includes event2 only
        time_range = TimeRange(now - timedelta(hours=1, minutes=30), now - timedelta(minutes=30))
        events_in_range = self.engine.get_events_in_range(self.test_entity_id, time_range)

        self.assertEqual(len(events_in_range), 1)
        self.assertEqual(events_in_range[0].event_id, event2.event_id)

    def test_get_events_by_significance(self):
        """Test retrieving events by significance level."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create events with different significance levels
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Low Significance", "Description",
            significance_level=3
        )
        high_sig_event = self.engine.create_and_add_event(
            self.test_entity_id, EventType.ACHIEVEMENT, "High Significance", "Description",
            significance_level=8
        )

        # Test filtering by significance
        significant_events = self.engine.get_events_by_significance(self.test_entity_id, 5)

        self.assertEqual(len(significant_events), 1)
        self.assertEqual(significant_events[0].event_id, high_sig_event.event_id)

    def test_get_events_by_significance_invalid(self):
        """Test getting events by significance with invalid level."""
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        with self.assertRaises(ValidationError):
            self.engine.get_events_by_significance(self.test_entity_id, 0)

        with self.assertRaises(ValidationError):
            self.engine.get_events_by_significance(self.test_entity_id, 11)

    def test_get_events_by_type(self):
        """Test retrieving events by type."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create events of different types
        conversation_event = self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Conversation", "Description"
        )
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.MEETING, "Meeting", "Description"
        )
        another_conversation = self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Another Conversation", "Description"
        )

        # Test filtering by type
        conversation_events = self.engine.get_events_by_type(self.test_entity_id, EventType.CONVERSATION)

        self.assertEqual(len(conversation_events), 2)
        event_ids = [event.event_id for event in conversation_events]
        self.assertIn(conversation_event.event_id, event_ids)
        self.assertIn(another_conversation.event_id, event_ids)

    def test_get_recent_events(self):
        """Test retrieving recent events."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create events at different times
        now = datetime.now()
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Old Event", "Description",
            timestamp=now - timedelta(days=40)
        )
        recent_event = self.engine.create_and_add_event(
            self.test_entity_id, EventType.MEETING, "Recent Event", "Description",
            timestamp=now - timedelta(days=10)
        )

        # Test getting recent events (last 30 days)
        recent_events = self.engine.get_recent_events(self.test_entity_id, 30)

        self.assertEqual(len(recent_events), 1)
        self.assertEqual(recent_events[0].event_id, recent_event.event_id)

    def test_get_recent_events_invalid_days(self):
        """Test getting recent events with invalid days parameter."""
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        with self.assertRaises(ValidationError):
            self.engine.get_recent_events(self.test_entity_id, 0)

        with self.assertRaises(ValidationError):
            self.engine.get_recent_events(self.test_entity_id, -5)

    def test_get_most_significant_events(self):
        """Test retrieving most significant events."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Create events with different significance levels
        events = []
        for i in range(5):
            event = self.engine.create_and_add_event(
                self.test_entity_id, EventType.CUSTOM, f"Event {i}", "Description",
                significance_level=i + 1
            )
            events.append(event)

        # Test getting top 3 most significant events
        most_significant = self.engine.get_most_significant_events(self.test_entity_id, 3)

        self.assertEqual(len(most_significant), 3)
        # Should be in descending order of significance
        self.assertEqual(most_significant[0].significance_level, 5)
        self.assertEqual(most_significant[1].significance_level, 4)
        self.assertEqual(most_significant[2].significance_level, 3)

    def test_get_most_significant_events_invalid_count(self):
        """Test getting most significant events with invalid count."""
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        with self.assertRaises(ValidationError):
            self.engine.get_most_significant_events(self.test_entity_id, 0)

        with self.assertRaises(ValidationError):
            self.engine.get_most_significant_events(self.test_entity_id, -1)

    def test_validate_timeline_consistency(self):
        """Test timeline consistency validation."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add events in chronological order
        now = datetime.now()
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Event 1", "Description",
            timestamp=now - timedelta(hours=2)
        )
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.MEETING, "Event 2", "Description",
            timestamp=now - timedelta(hours=1)
        )

        # Validate consistency
        is_consistent, issues = self.engine.validate_timeline_consistency(self.test_entity_id)
        self.assertTrue(is_consistent)
        self.assertEqual(len(issues), 0)

    def test_validate_timeline_consistency_no_timeline(self):
        """Test consistency validation for non-existent timeline."""
        is_consistent, issues = self.engine.validate_timeline_consistency("non_existent")

        self.assertFalse(is_consistent)
        self.assertEqual(len(issues), 1)
        self.assertIn("No timeline found", issues[0])

    def test_chronological_consistency_validation(self):
        """Test chronological consistency validation during event addition."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add event with future timestamp (should be rejected)
        future_event = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Future Event",
            description="Event in the future",
            timestamp=datetime.now() + timedelta(days=2)  # More than 1 day in future
        )

        success = self.engine.add_event(self.test_entity_id, future_event)
        self.assertFalse(success)

    def test_duplicate_event_detection(self):
        """Test detection of duplicate events."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add first event
        timestamp = datetime.now()
        event1 = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Test Event",
            description="Test description",
            timestamp=timestamp
        )

        success1 = self.engine.add_event(self.test_entity_id, event1)
        self.assertTrue(success1)

        # Try to add duplicate event
        event2 = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Test Event",  # Same title
            description="Test description",  # Same description
            timestamp=timestamp  # Same timestamp
        )

        success2 = self.engine.add_event(self.test_entity_id, event2)
        self.assertFalse(success2)  # Should be rejected as duplicate

    def test_location_conflict_detection(self):
        """Test detection of location conflicts for characters."""
        # Create character timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add event at location A
        timestamp = datetime.now()
        event1 = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Event at Location A",
            description="Description",
            participants=[self.test_entity_id],
            location_id="location_a",
            timestamp=timestamp
        )

        success1 = self.engine.add_event(self.test_entity_id, event1)
        self.assertTrue(success1)

        # Try to add simultaneous event at different location
        event2 = TimelineEvent(
            event_type=EventType.MEETING,
            title="Event at Location B",
            description="Description",
            participants=[self.test_entity_id],
            location_id="location_b",
            timestamp=timestamp  # Same timestamp
        )

        success2 = self.engine.add_event(self.test_entity_id, event2)
        self.assertFalse(success2)  # Should be rejected due to location conflict

    def test_prune_old_events(self):
        """Test pruning old events from timeline."""
        # Create timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add old, low-significance event
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Old Event", "Description",
            timestamp=datetime.now() - timedelta(days=400),
            significance_level=3
        )

        # Add old, high-significance event
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.ACHIEVEMENT, "Important Old Event", "Description",
            timestamp=datetime.now() - timedelta(days=400),
            significance_level=9
        )

        # Add recent event
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.MEETING, "Recent Event", "Description",
            timestamp=datetime.now() - timedelta(days=10),
            significance_level=5
        )

        # Prune events (keep last 365 days, or significance >= 7)
        removed_count = self.engine.prune_old_events(self.test_entity_id, 365, 7)

        self.assertEqual(removed_count, 1)  # Only the old, low-significance event should be removed

        timeline = self.engine.get_timeline(self.test_entity_id)
        self.assertEqual(len(timeline.events), 2)  # Should have 2 events left

    def test_get_timeline_summary(self):
        """Test getting timeline summary."""
        # Test summary for non-existent timeline
        summary = self.engine.get_timeline_summary("non_existent")
        self.assertFalse(summary["timeline_exists"])
        self.assertIn("error", summary)

        # Create timeline with events
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        # Add events with different characteristics
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.CONVERSATION, "Event 1", "Description",
            significance_level=5, emotional_impact=0.3
        )
        self.engine.create_and_add_event(
            self.test_entity_id, EventType.ACHIEVEMENT, "Event 2", "Description",
            significance_level=8, emotional_impact=0.7
        )

        # Get summary
        summary = self.engine.get_timeline_summary(self.test_entity_id)

        self.assertTrue(summary["timeline_exists"])
        self.assertEqual(summary["entity_id"], self.test_entity_id)
        self.assertEqual(summary["entity_type"], "character")
        self.assertEqual(summary["event_count"], 2)
        self.assertEqual(summary["avg_significance"], 6.5)
        self.assertEqual(summary["max_significance"], 8)
        self.assertEqual(summary["avg_emotional_impact"], 0.5)
        self.assertIn("earliest_event", summary)
        self.assertIn("latest_event", summary)

    def test_get_timeline_summary_empty(self):
        """Test getting summary for empty timeline."""
        # Create empty timeline
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        summary = self.engine.get_timeline_summary(self.test_entity_id)

        self.assertTrue(summary["timeline_exists"])
        self.assertEqual(summary["event_count"], 0)
        self.assertNotIn("earliest_event", summary)
        self.assertNotIn("avg_significance", summary)

    def test_get_all_timelines(self):
        """Test getting all timelines."""
        # Initially empty
        timelines = self.engine.get_all_timelines()
        self.assertEqual(len(timelines), 0)

        # Create multiple timelines
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)
        self.engine.create_timeline(self.test_location_id, EntityType.LOCATION)
        self.engine.create_timeline(self.test_object_id, EntityType.OBJECT)

        timelines = self.engine.get_all_timelines()
        self.assertEqual(len(timelines), 3)

        entity_types = [timeline.entity_type for timeline in timelines]
        self.assertIn(EntityType.CHARACTER, entity_types)
        self.assertIn(EntityType.LOCATION, entity_types)
        self.assertIn(EntityType.OBJECT, entity_types)

    def test_get_timeline_count(self):
        """Test getting timeline count."""
        self.assertEqual(self.engine.get_timeline_count(), 0)

        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)
        self.assertEqual(self.engine.get_timeline_count(), 1)

        self.engine.create_timeline(self.test_location_id, EntityType.LOCATION)
        self.assertEqual(self.engine.get_timeline_count(), 2)

    def test_clear_all_timelines(self):
        """Test clearing all timelines."""
        # Create some timelines
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)
        self.engine.create_timeline(self.test_location_id, EntityType.LOCATION)

        self.assertEqual(self.engine.get_timeline_count(), 2)

        # Clear all timelines
        self.engine.clear_all_timelines()

        self.assertEqual(self.engine.get_timeline_count(), 0)
        self.assertEqual(len(self.engine.entity_timeline_map), 0)

    def test_methods_with_no_timeline(self):
        """Test various methods when timeline doesn't exist."""
        # All these methods should handle missing timelines gracefully

        time_range = TimeRange(datetime.now() - timedelta(hours=1), datetime.now())
        events = self.engine.get_events_in_range("non_existent", time_range)
        self.assertEqual(len(events), 0)

        events = self.engine.get_events_by_significance("non_existent", 5)
        self.assertEqual(len(events), 0)

        events = self.engine.get_events_by_type("non_existent", EventType.CONVERSATION)
        self.assertEqual(len(events), 0)

        events = self.engine.get_recent_events("non_existent", 30)
        self.assertEqual(len(events), 0)

        events = self.engine.get_most_significant_events("non_existent", 10)
        self.assertEqual(len(events), 0)

        removed = self.engine.prune_old_events("non_existent", 365, 7)
        self.assertEqual(removed, 0)


if __name__ == '__main__':
    unittest.main()
