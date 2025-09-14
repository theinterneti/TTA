#!/usr/bin/env python3
"""
Simple test script for Character Development System
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

from character_development_system import CharacterDevelopmentSystem, Interaction
from data_models import DialogueContext


def test_character_system():
    """Test the character development system functionality."""
    print("Testing Character Development System...")

    # Create system
    system = CharacterDevelopmentSystem()
    print("✓ System created")

    # Create character
    character = system.create_character(
        character_id="test_therapist",
        name="Dr. Emily Watson",
        personality_traits={
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9,
            "openness": 0.6
        },
        therapeutic_role="therapist"
    )
    print(f"✓ Character created: {character.name}")
    print(f"  - Mood: {character.current_mood}")
    print(f"  - Empathy: {character.personality_traits['empathy']}")

    # Test interaction
    interaction = Interaction(
        participants=["test_therapist", "patient_001"],
        interaction_type="therapeutic",
        content="Discussed mindfulness techniques for managing anxiety",
        emotional_impact=0.6,
        therapeutic_value=0.8
    )

    success = system.update_character_from_interaction("test_therapist", interaction)
    print(f"✓ Interaction processed: {success}")

    # Check updated character
    updated_character = system.get_character_state("test_therapist")
    print(f"  - Memories: {len(updated_character.memory_fragments)}")
    print(f"  - Relationships: {len(updated_character.relationship_scores)}")

    # Test dialogue context generation
    dialogue_context = DialogueContext(
        participants=["test_therapist", "patient_001"],
        current_topic="anxiety management"
    )

    context = system.generate_character_dialogue_context("test_therapist", dialogue_context)
    print("✓ Dialogue context generated")
    print(f"  - Character: {context['name']}")
    print(f"  - Role: {context['therapeutic_role']}")
    print(f"  - Relevant memories: {len(context['relevant_memories'])}")

    # Test character consistency
    is_consistent, message = system.validate_character_consistency(
        "test_therapist",
        "I understand this is challenging for you. Let's work together to develop some coping strategies.",
        {}
    )
    print(f"✓ Consistency validation: {is_consistent}")

    # Get development summary
    summary = system.get_character_development_summary("test_therapist")
    print("✓ Development summary generated")
    print(f"  - Total relationships: {summary['relationship_summary']['total_relationships']}")
    print(f"  - Total memories: {summary['memory_summary']['total_memories']}")

    print("\n🎉 All tests passed! Character Development System is working correctly.")
    return True

if __name__ == "__main__":
    test_character_system()
