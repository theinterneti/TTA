#!/usr/bin/env python3
"""
Core functionality test for Living Worlds components (no external dependencies).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def test_core_models():
    """Test core Living Worlds models without external dependencies."""
    print("Testing Living Worlds core models...")

    try:
        # Direct import of models

        # Import the core model classes directly
        sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
        from living_worlds_models import (
            EntityType,
            EventType,
            FamilyRelationship,
            FamilyTree,
            RelationshipType,
            Timeline,
            TimelineEvent,
            WorldState,
            WorldStateFlag,
        )
        print("✓ Living Worlds models imported successfully")

        # Test Timeline creation
        timeline = Timeline(
            entity_id='test_character',
            entity_type=EntityType.CHARACTER
        )
        timeline.validate()
        print("✓ Timeline creation and validation successful")

        # Test TimelineEvent creation
        event = TimelineEvent(
            event_type=EventType.MEETING,
            title='Test Meeting',
            description='A test meeting event',
            participants=['test_character', 'other_character'],
            significance_level=7,
            emotional_impact=0.5
        )
        event.validate()
        print("✓ TimelineEvent creation and validation successful")

        # Test adding event to timeline
        success = timeline.add_event(event)
        if success:
            print("✓ Event added to timeline successfully")
        else:
            print("✗ Failed to add event to timeline")
            return False

        # Test timeline queries
        recent_events = timeline.get_recent_events(days=30)
        if len(recent_events) == 1:
            print("✓ Timeline recent events query successful")
        else:
            print(f"✗ Expected 1 recent event, got {len(recent_events)}")
            return False

        significant_events = timeline.get_events_by_significance(min_significance=5)
        if len(significant_events) == 1:
            print("✓ Timeline significance query successful")
        else:
            print(f"✗ Expected 1 significant event, got {len(significant_events)}")
            return False

        # Test FamilyTree creation
        family_tree = FamilyTree(
            root_character_id='test_character'
        )
        family_tree.validate()
        print("✓ FamilyTree creation and validation successful")

        # Test FamilyRelationship creation
        relationship = FamilyRelationship(
            from_character_id='parent_character',
            to_character_id='test_character',
            relationship_type=RelationshipType.PARENT,
            strength=0.9
        )
        relationship.validate()
        print("✓ FamilyRelationship creation and validation successful")

        # Test adding relationship to family tree
        success = family_tree.add_relationship(
            'parent_character',
            'test_character',
            RelationshipType.PARENT,
            0.9
        )
        if success:
            print("✓ Relationship added to family tree successfully")
        else:
            print("✗ Failed to add relationship to family tree")
            return False

        # Test family tree queries
        parents = family_tree.get_parents('test_character')
        if len(parents) == 1 and parents[0] == 'parent_character':
            print("✓ Family tree parent query successful")
        else:
            print(f"✗ Expected 1 parent, got {parents}")
            return False

        # Test WorldState creation
        world_state = WorldState(
            world_id='test_world',
            world_name='Test World',
            world_status=WorldStateFlag.ACTIVE
        )
        world_state.validate()
        print("✓ WorldState creation and validation successful")

        # Test world state operations
        world_state.add_character('test_character', {'status': 'active'})
        world_state.add_location('test_location', {'status': 'accessible'})
        world_state.set_flag('test_flag', 'test_value')

        if 'test_character' in world_state.active_characters:
            print("✓ Character added to world state successfully")
        else:
            print("✗ Failed to add character to world state")
            return False

        if world_state.get_flag('test_flag') == 'test_value':
            print("✓ World state flag operations successful")
        else:
            print("✗ World state flag operations failed")
            return False

        # Test serialization/deserialization
        print("\nTesting serialization/deserialization...")

        timeline_dict = timeline.to_dict()
        timeline_restored = Timeline.from_dict(timeline_dict)
        if timeline_restored.timeline_id == timeline.timeline_id:
            print("✓ Timeline serialization/deserialization successful")
        else:
            print("✗ Timeline serialization/deserialization failed")
            return False

        event_dict = event.to_dict()
        event_restored = TimelineEvent.from_dict(event_dict)
        if event_restored.event_id == event.event_id:
            print("✓ TimelineEvent serialization/deserialization successful")
        else:
            print("✗ TimelineEvent serialization/deserialization failed")
            return False

        family_tree_dict = family_tree.to_dict()
        family_tree_restored = FamilyTree.from_dict(family_tree_dict)
        if family_tree_restored.tree_id == family_tree.tree_id:
            print("✓ FamilyTree serialization/deserialization successful")
        else:
            print("✗ FamilyTree serialization/deserialization failed")
            return False

        world_state_dict = world_state.to_dict()
        world_state_restored = WorldState.from_dict(world_state_dict)
        if world_state_restored.world_id == world_state.world_id:
            print("✓ WorldState serialization/deserialization successful")
        else:
            print("✗ WorldState serialization/deserialization failed")
            return False

        print("\n🎉 All core model tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during core model testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_timeline_engine():
    """Test Timeline Engine functionality."""
    print("\nTesting Timeline Engine...")

    try:
        # Import Timeline Engine
        sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
        from timeline_engine import TimelineEngine

        sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
        from living_worlds_models import EntityType, EventType

        print("✓ Timeline Engine imported successfully")

        # Create timeline engine
        engine = TimelineEngine()

        # Create timeline
        timeline = engine.create_timeline('test_character', EntityType.CHARACTER)
        if timeline:
            print("✓ Timeline created through engine successfully")
        else:
            print("✗ Failed to create timeline through engine")
            return False

        # Add event through engine
        event = engine.create_and_add_event(
            'test_character',
            EventType.MEETING,
            'Test Meeting',
            'A test meeting event',
            participants=['test_character', 'other_character'],
            significance_level=7,
            emotional_impact=0.5
        )

        if event:
            print("✓ Event created and added through engine successfully")
        else:
            print("✗ Failed to create and add event through engine")
            return False

        # Test timeline queries through engine
        recent_events = engine.get_recent_events('test_character', days=30)
        if len(recent_events) == 1:
            print("✓ Engine recent events query successful")
        else:
            print(f"✗ Expected 1 recent event, got {len(recent_events)}")
            return False

        significant_events = engine.get_events_by_significance('test_character', min_significance=5)
        if len(significant_events) == 1:
            print("✓ Engine significance query successful")
        else:
            print(f"✗ Expected 1 significant event, got {len(significant_events)}")
            return False

        # Test timeline validation
        is_consistent, issues = engine.validate_timeline_consistency('test_character')
        if is_consistent:
            print("✓ Timeline consistency validation successful")
        else:
            print(f"✗ Timeline consistency validation failed: {issues}")
            return False

        # Test timeline summary
        summary = engine.get_timeline_summary('test_character')
        if summary.get('timeline_exists') and summary.get('event_count') == 1:
            print("✓ Timeline summary generation successful")
        else:
            print(f"✗ Timeline summary generation failed: {summary}")
            return False

        print("✓ Timeline Engine tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during Timeline Engine testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_errors():
    """Test validation error handling."""
    print("\nTesting validation error handling...")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
        from living_worlds_models import (
            EntityType,
            EventType,
            Timeline,
            TimelineEvent,
            ValidationError,
        )

        # Test invalid timeline
        try:
            invalid_timeline = Timeline(
                timeline_id="",  # Invalid empty ID
                entity_id="test",
                entity_type=EntityType.CHARACTER
            )
            invalid_timeline.validate()
            print("✗ Expected validation error for empty timeline ID")
            return False
        except ValidationError:
            print("✓ Timeline validation error handling successful")

        # Test invalid event
        try:
            invalid_event = TimelineEvent(
                event_type=EventType.MEETING,
                title="",  # Invalid empty title
                description="Test"
            )
            invalid_event.validate()
            print("✗ Expected validation error for empty event title")
            return False
        except ValidationError:
            print("✓ Event validation error handling successful")

        # Test invalid significance level
        try:
            invalid_event = TimelineEvent(
                event_type=EventType.MEETING,
                title="Test",
                description="Test",
                significance_level=15  # Invalid level > 10
            )
            invalid_event.validate()
            print("✗ Expected validation error for invalid significance level")
            return False
        except ValidationError:
            print("✓ Significance level validation error handling successful")

        print("✓ Validation error handling tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during validation testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Living Worlds Core Functionality Test")
    print("=" * 60)

    all_passed = True

    # Run tests
    all_passed &= test_core_models()
    all_passed &= test_timeline_engine()
    all_passed &= test_validation_errors()

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CORE TESTS PASSED! Living Worlds core functionality is working correctly.")
        print("\nNote: Database persistence tests require Neo4j and Redis to be running.")
        print("The core models, Timeline Engine, and validation are all functional.")
    else:
        print("❌ SOME CORE TESTS FAILED! Please check the errors above.")
    print("=" * 60)
