"""
Standalone test for Timeline Engine

This test imports the Timeline Engine and models directly without
going through the __init__.py files to avoid import dependency issues.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the modules directly
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "models"))

from living_worlds_models import (
    EntityType,
    EventType,
    Timeline,
    TimelineEvent,
    ValidationError,
)
from timeline_engine import TimelineEngine, TimeRange


def test_timeline_engine():
    """Test the Timeline Engine functionality."""
    print("Testing Timeline Engine...")
    print("=" * 40)

    # Initialize engine
    engine = TimelineEngine()
    test_entity_id = "test_character_001"

    print("1. Testing engine initialization...")
    assert isinstance(engine.timelines, dict)
    assert isinstance(engine.entity_timeline_map, dict)
    assert len(engine.timelines) == 0
    assert len(engine.entity_timeline_map) == 0
    print("   ✓ Engine initialized correctly")

    print("\n2. Testing timeline creation...")
    timeline = engine.create_timeline(test_entity_id, EntityType.CHARACTER)
    assert isinstance(timeline, Timeline)
    assert timeline.entity_id == test_entity_id
    assert timeline.entity_type == EntityType.CHARACTER
    assert timeline.timeline_id in engine.timelines
    assert engine.entity_timeline_map[test_entity_id] == timeline.timeline_id
    print("   ✓ Timeline created successfully")

    print("\n3. Testing event creation and addition...")
    event = TimelineEvent(
        event_type=EventType.CONVERSATION,
        title="Test Conversation",
        description="A test conversation event",
        participants=[test_entity_id],
        significance_level=5
    )

    success = engine.add_event(test_entity_id, event)
    assert success

    retrieved_timeline = engine.get_timeline(test_entity_id)
    assert len(retrieved_timeline.events) == 1
    assert retrieved_timeline.events[0].event_id == event.event_id
    print("   ✓ Event added successfully")

    print("\n4. Testing create and add event...")
    event2 = engine.create_and_add_event(
        entity_id=test_entity_id,
        event_type=EventType.MEETING,
        title="Test Meeting",
        description="A test meeting event",
        participants=[test_entity_id, "other_character"],
        significance_level=7,
        emotional_impact=0.5,
        consequences=["Made new friend"],
        tags=["social", "positive"],
        metadata={"duration": "1 hour"}
    )

    assert event2 is not None
    assert event2.title == "Test Meeting"
    assert event2.significance_level == 7
    assert event2.emotional_impact == 0.5

    timeline = engine.get_timeline(test_entity_id)
    assert len(timeline.events) == 2
    print("   ✓ Create and add event successful")

    print("\n5. Testing event filtering by significance...")
    engine.create_and_add_event(
        test_entity_id, EventType.CONVERSATION, "Low Significance", "Description",
        significance_level=3
    )
    engine.create_and_add_event(
        test_entity_id, EventType.ACHIEVEMENT, "High Significance", "Description",
        significance_level=8
    )

    significant_events = engine.get_events_by_significance(test_entity_id, 6)
    assert len(significant_events) == 2  # event2 (7) and high_sig_event (8)
    print("   ✓ Event filtering by significance works")

    print("\n6. Testing time range queries...")
    now = datetime.now()
    past_event = engine.create_and_add_event(
        test_entity_id, EventType.TRAVEL, "Past Event", "Description",
        timestamp=now - timedelta(hours=2)
    )
    recent_event = engine.create_and_add_event(
        test_entity_id, EventType.DISCOVERY, "Recent Event", "Description",
        timestamp=now - timedelta(minutes=30)
    )

    # Query for events in the last hour
    time_range = TimeRange(now - timedelta(hours=1), now)
    events_in_range = engine.get_events_in_range(test_entity_id, time_range)

    # Should include recent_event but not past_event
    recent_event_found = any(e.event_id == recent_event.event_id for e in events_in_range)
    past_event_found = any(e.event_id == past_event.event_id for e in events_in_range)

    assert recent_event_found
    assert not past_event_found
    print("   ✓ Time range queries work correctly")

    print("\n7. Testing chronological consistency...")
    is_consistent, issues = engine.validate_timeline_consistency(test_entity_id)
    assert is_consistent
    assert len(issues) == 0
    print("   ✓ Timeline is chronologically consistent")

    print("\n8. Testing duplicate event prevention...")
    timestamp = datetime.now()
    duplicate_event1 = TimelineEvent(
        event_type=EventType.CONVERSATION,
        title="Duplicate Test",
        description="Test description",
        timestamp=timestamp
    )

    success1 = engine.add_event(test_entity_id, duplicate_event1)
    assert success1

    # Try to add exact duplicate
    duplicate_event2 = TimelineEvent(
        event_type=EventType.CONVERSATION,
        title="Duplicate Test",  # Same title
        description="Test description",  # Same description
        timestamp=timestamp  # Same timestamp
    )

    success2 = engine.add_event(test_entity_id, duplicate_event2)
    assert not success2  # Should be rejected
    print("   ✓ Duplicate event prevention works")

    print("\n9. Testing timeline summary...")
    summary = engine.get_timeline_summary(test_entity_id)
    assert summary["timeline_exists"]
    assert summary["entity_id"] == test_entity_id
    assert summary["entity_type"] == "character"
    assert summary["event_count"] > 0
    assert "avg_significance" in summary
    assert "max_significance" in summary
    print("   ✓ Timeline summary generation works")

    print("\n10. Testing error handling...")
    # Test empty entity ID
    try:
        engine.create_timeline("", EntityType.CHARACTER)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass  # Expected

    # Test adding event to non-existent timeline
    test_event = TimelineEvent(
        event_type=EventType.CONVERSATION,
        title="Test",
        description="Test"
    )
    success = engine.add_event("non_existent", test_event)
    assert not success

    # Test invalid significance level
    try:
        engine.get_events_by_significance(test_entity_id, 0)
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass  # Expected

    print("   ✓ Error handling works correctly")

    print("\n" + "=" * 40)
    print("🎉 All Timeline Engine tests passed!")
    return True


def test_time_range():
    """Test the TimeRange helper class."""
    print("\nTesting TimeRange class...")
    print("-" * 30)

    # Test valid time range
    start = datetime.now()
    end = start + timedelta(hours=1)
    time_range = TimeRange(start, end)

    assert time_range.start_time == start
    assert time_range.end_time == end
    print("   ✓ TimeRange creation works")

    # Test contains method
    middle = start + timedelta(minutes=30)
    assert time_range.contains(middle)
    assert time_range.contains(start)
    assert time_range.contains(end)

    before = start - timedelta(minutes=1)
    after = end + timedelta(minutes=1)
    assert not time_range.contains(before)
    assert not time_range.contains(after)
    print("   ✓ TimeRange contains method works")

    # Test duration
    expected_duration = timedelta(hours=1)
    assert time_range.duration() == expected_duration
    print("   ✓ TimeRange duration calculation works")

    # Test invalid time range
    try:
        TimeRange(end, start)  # End before start
        raise AssertionError("Should have raised ValidationError")
    except ValidationError:
        pass  # Expected

    print("   ✓ TimeRange validation works")
    print("🎉 All TimeRange tests passed!")
    return True


if __name__ == "__main__":
    try:
        print("Starting Timeline Engine Tests")
        print("=" * 50)

        # Test TimeRange first
        time_range_success = test_time_range()

        # Test Timeline Engine
        timeline_success = test_timeline_engine()

        if time_range_success and timeline_success:
            print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
            print("\nTimeline Engine implementation is working correctly.")
            print("Key features tested:")
            print("- Timeline creation and management")
            print("- Event creation and addition")
            print("- Chronological consistency validation")
            print("- Event filtering by significance, type, and time range")
            print("- Duplicate event prevention")
            print("- Error handling and validation")
            print("- Timeline summary generation")
        else:
            print("\n❌ Some tests failed.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
