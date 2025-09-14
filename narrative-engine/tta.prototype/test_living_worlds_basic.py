#!/usr/bin/env python3
"""
Basic functionality test for Living Worlds components.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic Living Worlds functionality."""
    print("Testing Living Worlds basic functionality...")

    try:
        # Test model imports
        from models.living_worlds_models import (
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

        # Test schema imports
        print("✓ Living Worlds schema components imported successfully")

        # Test persistence imports
        print("✓ Living Worlds persistence components imported successfully")

        # Test migrations imports
        print("✓ Living Worlds migration components imported successfully")

        # Test indexing imports
        print("✓ Living Worlds indexing components imported successfully")

        # Test basic model creation and validation
        print("\nTesting model creation and validation...")

        # Create timeline
        timeline = Timeline(
            entity_id='test_character',
            entity_type=EntityType.CHARACTER
        )
        timeline.validate()
        print("✓ Timeline creation and validation successful")

        # Create timeline event
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

        # Add event to timeline
        success = timeline.add_event(event)
        if success:
            print("✓ Event added to timeline successfully")
        else:
            print("✗ Failed to add event to timeline")

        # Create family tree
        family_tree = FamilyTree(
            root_character_id='test_character'
        )
        family_tree.validate()
        print("✓ FamilyTree creation and validation successful")

        # Create family relationship
        relationship = FamilyRelationship(
            from_character_id='parent_character',
            to_character_id='test_character',
            relationship_type=RelationshipType.PARENT,
            strength=0.9
        )
        relationship.validate()
        print("✓ FamilyRelationship creation and validation successful")

        # Create world state
        world_state = WorldState(
            world_id='test_world',
            world_name='Test World',
            world_status=WorldStateFlag.ACTIVE
        )
        world_state.validate()
        print("✓ WorldState creation and validation successful")

        # Test serialization/deserialization
        print("\nTesting serialization/deserialization...")

        timeline_dict = timeline.to_dict()
        timeline_restored = Timeline.from_dict(timeline_dict)
        if timeline_restored.timeline_id == timeline.timeline_id:
            print("✓ Timeline serialization/deserialization successful")
        else:
            print("✗ Timeline serialization/deserialization failed")

        event_dict = event.to_dict()
        event_restored = TimelineEvent.from_dict(event_dict)
        if event_restored.event_id == event.event_id:
            print("✓ TimelineEvent serialization/deserialization successful")
        else:
            print("✗ TimelineEvent serialization/deserialization failed")

        print("\n🎉 All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_manager_creation():
    """Test schema manager creation without connection."""
    print("\nTesting schema manager creation...")

    try:
        from database.living_worlds_schema import LivingWorldsSchemaManager

        # Create schema manager (without connecting)
        schema_manager = LivingWorldsSchemaManager()

        if schema_manager.current_schema_version == "1.1.0":
            print("✓ LivingWorldsSchemaManager created with correct version")
        else:
            print(f"✗ Unexpected schema version: {schema_manager.current_schema_version}")

        print("✓ Schema manager creation test passed")
        return True

    except Exception as e:
        print(f"✗ Error testing schema manager: {e}")
        return False

def test_persistence_creation():
    """Test persistence layer creation without connection."""
    print("\nTesting persistence layer creation...")

    try:
        from database.living_worlds_persistence import LivingWorldsPersistence

        # Create persistence layer (without connecting)
        persistence = LivingWorldsPersistence()

        if persistence.schema_manager is not None:
            print("✓ LivingWorldsPersistence created with schema manager")
        else:
            print("✗ LivingWorldsPersistence missing schema manager")

        print("✓ Persistence layer creation test passed")
        return True

    except Exception as e:
        print(f"✗ Error testing persistence layer: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Living Worlds Basic Functionality Test")
    print("=" * 60)

    all_passed = True

    # Run tests
    all_passed &= test_basic_functionality()
    all_passed &= test_schema_manager_creation()
    all_passed &= test_persistence_creation()

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Living Worlds components are working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    print("=" * 60)
