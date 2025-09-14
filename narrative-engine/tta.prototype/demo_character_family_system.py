#!/usr/bin/env python3
"""
Demonstration of Character Development System with Family Relationships

This script demonstrates the new family functionality including:
- Family tree generation
- Character backstory creation
- Personality evolution based on family history
- Integration with existing character development features
"""

import sys
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

from character_development_system import CharacterDevelopmentSystem
from living_worlds_models import EventType, TimelineEvent


def demonstrate_family_system():
    """Demonstrate the family system functionality."""
    print("🏠 Character Development System with Family Relationships Demo")
    print("=" * 60)

    # Create the system
    system = CharacterDevelopmentSystem()
    print("✓ Character Development System initialized")

    # Create a character with full family history
    character_id = "demo_therapist_001"
    character_name = "Dr. Sarah Martinez"

    print(f"\n👤 Creating character: {character_name}")
    character_state, family_tree, backstory = system.create_character_with_history(
        character_id=character_id,
        name=character_name,
        personality_traits={
            "empathy": 0.7,
            "patience": 0.6,
            "wisdom": 0.5,
            "supportiveness": 0.8,
            "openness": 0.6
        },
        therapeutic_role="therapist"
    )

    print("✓ Character created with family history")
    print(f"  - Initial mood: {character_state.current_mood}")
    print(f"  - Therapeutic role: {character_state.therapeutic_role}")

    # Display family information
    print("\n👨‍👩‍👧‍👦 Family Tree Information:")
    family_members = system.get_family_members(character_id)

    print(f"  - Parents: {len(family_members['parents'])}")
    for parent in family_members['parents']:
        print(f"    • {parent}")

    print(f"  - Siblings: {len(family_members['siblings'])}")
    for sibling in family_members['siblings']:
        print(f"    • {sibling}")

    extended = family_members['extended_family']
    if any(extended.values()):
        print("  - Extended family:")
        for relation_type, relatives in extended.items():
            if relatives:
                print(f"    • {relation_type}: {len(relatives)} members")

    print(f"  - Total family relationships: {len(family_tree.relationships)}")

    # Display backstory information
    print("\n📖 Character Backstory:")
    print(f"  - Childhood events: {len(backstory.childhood_events)}")
    print(f"  - Formative experiences: {len(backstory.formative_experiences)}")
    print(f"  - Life themes: {', '.join(backstory.life_themes)}")

    if backstory.family_influences:
        print("  - Family influences on personality:")
        for trait, influence in backstory.family_influences.items():
            direction = "increased" if influence > 0 else "decreased"
            print(f"    • {trait}: {direction} by {abs(influence):.2f}")

    if backstory.personality_origins:
        print("  - Personality trait origins:")
        for trait, origin in backstory.personality_origins.items():
            print(f"    • {trait}: {origin}")

    # Demonstrate personality evolution
    print("\n🌱 Personality Evolution Demonstration:")
    print("Initial personality traits:")
    for trait, value in character_state.personality_traits.items():
        print(f"  - {trait}: {value:.3f}")

    # Create some life events
    life_events = [
        TimelineEvent(
            event_type=EventType.FAMILY_EVENT,
            title="Family Reunion",
            description="Attended a large family gathering with extended relatives",
            participants=[character_id] + family_members['parents'][:1],
            significance_level=7,
            emotional_impact=0.6,
            tags=['family', 'bonding', 'positive']
        ),
        TimelineEvent(
            event_type=EventType.LEARNING,
            title="Professional Development",
            description="Completed advanced training in therapeutic techniques",
            participants=[character_id],
            significance_level=8,
            emotional_impact=0.4,
            tags=['learning', 'professional', 'growth']
        ),
        TimelineEvent(
            event_type=EventType.ACHIEVEMENT,
            title="Career Milestone",
            description="Received recognition for outstanding therapeutic work",
            participants=[character_id],
            significance_level=9,
            emotional_impact=0.8,
            tags=['achievement', 'recognition', 'career']
        )
    ]

    # Apply personality evolution
    personality_changes = system.evolve_character_personality(character_id, life_events)

    print("\nAfter life events, personality changes:")
    updated_character = system.get_character_state(character_id)
    for trait, value in updated_character.personality_traits.items():
        change = personality_changes.get(trait, 0)
        if abs(change) > 0.001:
            direction = "↑" if change > 0 else "↓"
            print(f"  - {trait}: {value:.3f} {direction} (changed by {abs(change):.3f})")
        else:
            print(f"  - {trait}: {value:.3f}")

    print(f"  - Updated mood: {updated_character.current_mood}")

    # Show comprehensive character summary
    print("\n📊 Character Development Summary:")
    summary = system.get_character_development_summary(character_id)

    print(f"  - Character: {summary['name']}")
    print(f"  - Current mood: {summary['current_mood']}")
    print(f"  - Therapeutic role: {summary['therapeutic_role']}")

    print(f"  - Relationships: {summary['relationship_summary']['total_relationships']}")
    print(f"  - Memories: {summary['memory_summary']['total_memories']}")

    family_summary = summary['family_summary']
    print(f"  - Family tree: {'Yes' if family_summary['has_family_tree'] else 'No'}")
    print(f"  - Family relationships: {family_summary['family_relationships']}")
    print(f"  - Family events: {family_summary['family_events']}")

    # Demonstrate adding a new family member
    print("\n👥 Adding New Family Member:")
    from living_worlds_models import RelationshipType

    success = system.add_family_member(
        character_id, "cousin_maria", RelationshipType.COUSIN, strength=0.8
    )

    if success:
        print("✓ Successfully added cousin Maria to family tree")
        updated_family = system.get_family_members(character_id)
        print(f"  - Updated extended family cousins: {len(updated_family['extended_family']['cousins'])}")

    print("\n🎉 Family system demonstration complete!")
    print("The character now has a rich family history that influences their personality,")
    print("relationships, and therapeutic approach. This creates more realistic and")
    print("engaging character interactions in the living world environment.")


if __name__ == "__main__":
    demonstrate_family_system()
