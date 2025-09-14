#!/usr/bin/env python3
"""
Integration Test for Object Lifecycle Manager

This script demonstrates the ObjectLifecycleManager working with the timeline engine
and other living worlds components.
"""

import sys
from datetime import timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
sys.path.extend([str(core_path), str(models_path)])

from living_worlds_models import EventType, TimelineEvent
from object_lifecycle_manager import Interaction, ObjectData, ObjectLifecycleManager
from timeline_engine import TimelineEngine


def main():
    """Run integration test for Object Lifecycle Manager."""
    print("=== Object Lifecycle Manager Integration Test ===\n")

    # Create timeline engine
    timeline_engine = TimelineEngine()
    print("✓ Timeline engine created")

    # Create object lifecycle manager with timeline integration
    manager = ObjectLifecycleManager(timeline_engine=timeline_engine)
    print("✓ Object lifecycle manager created with timeline integration")

    # Create a sample object
    sword_data = ObjectData(
        name="Legendary Sword",
        object_type="weapon",
        description="A legendary sword forged by ancient masters",
        initial_condition=1.0,
        properties={
            "material": "enchanted_steel",
            "weight": 3.2,
            "sharpness": 0.95,
            "magic_level": 0.8
        },
        tags=["weapon", "sword", "legendary", "enchanted"],
        location_id="armory",
        owner_id="hero_character",
        creation_context="Forged in the fires of Mount Doom by the legendary blacksmith Thorin"
    )

    print(f"\n--- Creating Object: {sword_data.name} ---")
    object_history = manager.create_object_with_history(sword_data)
    print(f"✓ Object created with ID: {object_history.object_id}")
    print(f"  - Initial condition: {object_history.object_state.current_condition}")
    print(f"  - Initial wear level: {object_history.object_state.wear_level}")
    print(f"  - Location: {object_history.object_state.current_location_id}")
    print(f"  - Owner: {object_history.object_state.current_owner_id}")

    # Simulate some interactions
    print("\n--- Simulating Interactions ---")

    interactions = [
        Interaction(
            object_id=sword_data.object_id,
            character_id="hero_character",
            interaction_type="use",
            description="Hero uses the legendary sword in battle against orcs",
            intensity=0.8,
            duration_minutes=45,
            location_id="battlefield",
            consequences=["Sword becomes slightly duller", "Orcs defeated"]
        ),
        Interaction(
            object_id=sword_data.object_id,
            character_id="blacksmith_npc",
            interaction_type="examine",
            description="Blacksmith examines the sword for maintenance needs",
            intensity=0.2,
            duration_minutes=15,
            location_id="forge",
            consequences=["Minor wear detected"]
        ),
        Interaction(
            object_id=sword_data.object_id,
            character_id="hero_character",
            interaction_type="use",
            description="Intense battle with dragon, sword takes heavy damage",
            intensity=1.0,
            duration_minutes=90,
            location_id="dragon_lair",
            consequences=["Significant wear from dragon scales", "Dragon defeated"]
        ),
        Interaction(
            object_id=sword_data.object_id,
            character_id="blacksmith_npc",
            interaction_type="repair",
            description="Master blacksmith repairs and sharpens the legendary sword",
            intensity=0.9,
            duration_minutes=120,
            location_id="forge",
            consequences=["Sword condition improved", "Sharpness restored"]
        )
    ]

    for i, interaction in enumerate(interactions, 1):
        print(f"\n{i}. {interaction.interaction_type.title()} Interaction:")
        print(f"   Description: {interaction.description}")
        print(f"   Intensity: {interaction.intensity}, Duration: {interaction.duration_minutes} min")

        success = manager.handle_object_interaction(sword_data.object_id, interaction)
        if success:
            updated_history = manager.get_object_history(sword_data.object_id)
            print("   ✓ Interaction handled successfully")
            print(f"   - New condition: {updated_history.object_state.current_condition:.3f}")
            print(f"   - New wear level: {updated_history.object_state.wear_level:.3f}")
            print(f"   - Still functional: {updated_history.object_state.is_functional}")
        else:
            print("   ✗ Interaction failed")

    # Simulate aging over time
    print("\n--- Simulating Aging ---")
    print("Aging sword over 6 months...")

    initial_condition = manager.get_object_history(sword_data.object_id).object_state.current_condition
    manager.age_object(sword_data.object_id, timedelta(days=180))

    aged_history = manager.get_object_history(sword_data.object_id)
    print("✓ Aging completed")
    print(f"  - Condition before aging: {initial_condition:.3f}")
    print(f"  - Condition after aging: {aged_history.object_state.current_condition:.3f}")
    print(f"  - Wear level after aging: {aged_history.object_state.wear_level:.3f}")

    # Add some relationships
    print("\n--- Managing Relationships ---")
    relationships = {
        'add': [
            {
                'to_entity_id': 'hero_character',
                'to_entity_type': 'character',
                'relationship_type': 'ownership',
                'strength': 1.0
            },
            {
                'to_entity_id': 'legendary_scabbard',
                'to_entity_type': 'object',
                'relationship_type': 'component',
                'strength': 0.9
            },
            {
                'to_entity_id': 'armory',
                'to_entity_type': 'location',
                'relationship_type': 'storage',
                'strength': 0.7
            }
        ]
    }

    success = manager.update_object_relationships(sword_data.object_id, relationships)
    if success:
        print("✓ Relationships added successfully")
        updated_history = manager.get_object_history(sword_data.object_id)
        print(f"  - Total active relationships: {len([r for r in updated_history.relationships if r.is_active])}")

        for rel in updated_history.relationships:
            if rel.is_active:
                print(f"    • {rel.relationship_type} with {rel.to_entity_id} ({rel.to_entity_type}) - strength: {rel.strength}")

    # Simulate wear from usage events
    print("\n--- Simulating Wear from Timeline Events ---")

    usage_events = [
        TimelineEvent(
            event_type=EventType.CONFLICT,
            title="Epic Battle",
            description="Sword used in epic battle against demon lord",
            participants=[sword_data.object_id, "hero_character", "demon_lord"],
            significance_level=9,
            emotional_impact=-0.3
        ),
        TimelineEvent(
            event_type=EventType.PLAYER_INTERACTION,
            title="Training Session",
            description="Hero practices sword techniques",
            participants=[sword_data.object_id, "hero_character"],
            significance_level=4,
            emotional_impact=0.1
        ),
        TimelineEvent(
            event_type=EventType.ENVIRONMENTAL_CHANGE,
            title="Harsh Weather",
            description="Sword exposed to acid rain during journey",
            participants=[sword_data.object_id],
            significance_level=3,
            emotional_impact=-0.2
        )
    ]

    wear_state = manager.simulate_object_wear(sword_data.object_id, usage_events)

    if wear_state.simulation_successful:
        print("✓ Wear simulation completed successfully")
        print(f"  - Wear applied: {wear_state.wear_applied:.3f}")
        print(f"  - Events processed: {wear_state.wear_events_applied}")
        print(f"  - Condition change: {wear_state.previous_condition:.3f} → {wear_state.new_condition:.3f}")
        print(f"  - Wear level change: {wear_state.previous_wear_level:.3f} → {wear_state.new_wear_level:.3f}")
        print(f"  - Functionality changed: {wear_state.functionality_changed}")
    else:
        print(f"✗ Wear simulation failed: {wear_state.error_message}")

    # Get comprehensive object summary
    print("\n--- Final Object Summary ---")
    summary = manager.get_object_summary(sword_data.object_id)

    if summary:
        print(f"Object: {summary['name']} ({summary['type']})")
        print(f"Condition: {summary['condition']:.3f} (Wear: {summary['wear_level']:.3f})")
        print(f"Functional: {summary['is_functional']}")
        print(f"Location: {summary['current_location']}")
        print(f"Owner: {summary['current_owner']}")
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"Total Modifications: {summary['total_modifications']}")
        print(f"Total Wear Events: {summary['total_wear_events']}")
        print(f"Active Relationships: {summary['active_relationships']}")
        print(f"Recent Interactions: {summary['recent_interactions']}")
        print(f"Last Updated: {summary['last_updated']}")

    # Get manager statistics
    print("\n--- Manager Statistics ---")
    stats = manager.get_manager_statistics()

    print(f"Total Objects: {stats['total_objects']}")
    print(f"Functional Objects: {stats['functional_objects']}")
    print(f"Broken Objects: {stats['broken_objects']}")
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Total Modifications: {stats['total_modifications']}")
    print(f"Total Wear Events: {stats['total_wear_events']}")
    print(f"Total Relationships: {stats['total_relationships']}")
    print(f"Average Condition: {stats['average_condition']:.3f}")
    print(f"Average Wear Level: {stats['average_wear_level']:.3f}")

    # Test timeline integration
    print("\n--- Timeline Integration Test ---")
    object_timeline = timeline_engine.get_timeline(sword_data.object_id)

    if object_timeline:
        print(f"✓ Object timeline found with {len(object_timeline.events)} events")
        print("Recent timeline events:")

        recent_events = object_timeline.get_recent_events(days=1)
        for event in recent_events[-3:]:  # Show last 3 events
            print(f"  - {event.title}: {event.description[:60]}...")
    else:
        print("✗ Object timeline not found")

    print("\n=== Integration Test Completed Successfully ===")
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
