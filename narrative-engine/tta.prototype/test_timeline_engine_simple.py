"""
Simple unit tests for Timeline Engine

This module contains unit tests for the TimelineEngine class that avoid
complex import dependencies and focus on testing the core functionality.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import directly without going through __init__.py
from core.timeline_engine import TimelineEngine, TimeRange
from models.living_worlds_models import (
    EntityType,
    EventType,
    Timeline,
    TimelineEvent,
    ValidationError,
)


class TestTimelineEngineSimple(unittest.TestCase):
    """Simple test cases for TimelineEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = TimelineEngine()
        self.test_entity_id = "test_character_001"

    def test_engine_initialization(self):
        """Test timeline engine initialization."""
        self.assertIsInstance(self.engine.timelines, dict)
        self.assertIsInstance(self.engine.entity_timeline_map, dict)
        self.assertEqual(len(self.engine.timelines), 0)
        self.assertEqual(len(self.engine.entity_timeline_map), 0)
        self.assertIsInstance(self.engine.created_at, datetime)
        print("✓ Engine initialization test passed")

    def test_create_timeline(self):
        """Test creating a new timeline."""
        timeline = self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)

        self.assertIsInstance(timeline, Timeline)
        self.assertEqual(timeline.entity_id, self.test_entity_id)
        self.assertEqual(timeline.entity_type, EntityType.CHARACTER)
        self.assertIn(timeline.timeline_id, self.engine.timelines)
        self.assertEqual(self.engine.entity_timeline_map[self.test_entity_id], timeline.timeline_id)
        print("✓ Create timeline test passed")

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
        print("✓ Add event test passed")

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
        print("✓ Create and add event test passed")

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
        print("✓ Get events by significance test passed")

    def test_chronological_consistency(self):
        """Test chronological consistency validation."""
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
        print("✓ Chronological consistency test passed")

    def test_time_range_queries(self):
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
        print("✓ Time range queries test passed")

    def test_timeline_summary(self):
        """Test getting timeline summary."""
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
        print("✓ Timeline summary test passed")

    def test_duplicate_event_prevention(self):
        """Test prevention of duplicate events."""
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
        print("✓ Duplicate event prevention test passed")

    def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Test creating timeline with empty entity ID
        with self.assertRaises(ValidationError):
            self.engine.create_timeline("", EntityType.CHARACTER)

        # Test adding event to non-existent timeline
        event = TimelineEvent(
            event_type=EventType.CONVERSATION,
            title="Test Event",
            description="Test description"
        )
        success = self.engine.add_event("non_existent_entity", event)
        self.assertFalse(success)

        # Test invalid significance level
        self.engine.create_timeline(self.test_entity_id, EntityType.CHARACTER)
        with self.assertRaises(ValidationError):
            self.engine.get_events_by_significance(self.test_entity_id, 0)

        print("✓ Error handling test passed")


def run_tests():
    """Run all tests and provide a summary."""
    print("Running Timeline Engine Tests...")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTimelineEngineSimple)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
    result = runner.run(suite)

    # Print summary
    print("\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    if result.wasSuccessful():
        print("\n🎉 All tests passed successfully!")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
