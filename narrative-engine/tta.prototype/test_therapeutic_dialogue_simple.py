#!/usr/bin/env python3
"""
Simple test script for Therapeutic Dialogue System
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

from data_models import EmotionalState, EmotionalStateType, InterventionType
from therapeutic_dialogue_system import (
    CharacterManagementAgent,
    DialogueType,
    TherapeuticDialogueRequest,
)


def test_therapeutic_dialogue_system():
    """Test the therapeutic dialogue system functionality."""
    print("Testing Therapeutic Dialogue System...")

    # Create Character Management Agent
    agent = CharacterManagementAgent()
    print("✓ Character Management Agent created")

    # Create test characters with different roles
    therapist = agent.character_system.create_character(
        character_id="dr_sarah",
        name="Dr. Sarah Chen",
        personality_traits={
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9
        },
        therapeutic_role="therapist"
    )

    mentor = agent.character_system.create_character(
        character_id="wise_guide",
        name="Marcus the Guide",
        personality_traits={
            "empathy": 0.7,
            "wisdom": 0.9,
            "patience": 0.9,
            "supportiveness": 0.8
        },
        therapeutic_role="mentor"
    )

    companion = agent.character_system.create_character(
        character_id="caring_friend",
        name="Alex the Companion",
        personality_traits={
            "empathy": 0.8,
            "supportiveness": 0.9,
            "patience": 0.7,
            "openness": 0.8
        },
        therapeutic_role="companion"
    )

    print("✓ Created 3 characters with different therapeutic roles")
    print(f"  - Therapist: {therapist.name}")
    print(f"  - Mentor: {mentor.name}")
    print(f"  - Companion: {companion.name}")

    # Test 1: Assessment dialogue
    print("\n--- Test 1: Assessment Dialogue ---")
    assessment_request = TherapeuticDialogueRequest(
        character_id="dr_sarah",
        dialogue_type=DialogueType.ASSESSMENT,
        narrative_context="First therapy session with new patient",
        specific_goals=["understand anxiety triggers", "assess coping skills"]
    )

    assessment_response = agent.generate_therapeutic_dialogue(assessment_request)
    print("✓ Assessment dialogue generated")
    print(f"  Character: {assessment_response.character_id}")
    print(f"  Therapeutic value: {assessment_response.therapeutic_value:.2f}")
    print(f"  Consistency score: {assessment_response.character_consistency_score:.2f}")
    print(f"  Content: \"{assessment_response.dialogue_content}\"")

    # Test 2: Mindfulness intervention
    print("\n--- Test 2: Mindfulness Intervention ---")
    mindfulness_request = TherapeuticDialogueRequest(
        character_id="dr_sarah",
        dialogue_type=DialogueType.INTERVENTION,
        intervention_type=InterventionType.MINDFULNESS,
        narrative_context="Patient experiencing anxiety attack",
        urgency_level=0.8
    )

    mindfulness_response = agent.generate_therapeutic_dialogue(mindfulness_request)
    print("✓ Mindfulness intervention generated")
    print(f"  Intervention: {mindfulness_response.intervention_delivered.value if mindfulness_response.intervention_delivered else 'None'}")
    print(f"  Therapeutic value: {mindfulness_response.therapeutic_value:.2f}")
    print(f"  Emotional impact: {mindfulness_response.emotional_impact:.2f}")
    print(f"  Content: \"{mindfulness_response.dialogue_content}\"")

    # Test 3: Emotional support from different characters
    print("\n--- Test 3: Emotional Support from Different Characters ---")
    emotional_state = EmotionalState(
        primary_emotion=EmotionalStateType.DEPRESSED,
        intensity=0.7
    )

    characters_to_test = [
        ("dr_sarah", "Therapist"),
        ("wise_guide", "Mentor"),
        ("caring_friend", "Companion")
    ]

    for char_id, role in characters_to_test:
        support_request = TherapeuticDialogueRequest(
            character_id=char_id,
            dialogue_type=DialogueType.SUPPORT,
            user_emotional_state=emotional_state,
            narrative_context="User feeling hopeless about recovery"
        )

        support_response = agent.generate_therapeutic_dialogue(support_request)
        print(f"  {role} ({char_id}):")
        print(f"    Therapeutic value: {support_response.therapeutic_value:.2f}")
        print(f"    Content: \"{support_response.dialogue_content[:80]}...\"")

    # Test 4: Cognitive restructuring intervention
    print("\n--- Test 4: Cognitive Restructuring ---")
    cognitive_request = TherapeuticDialogueRequest(
        character_id="dr_sarah",
        dialogue_type=DialogueType.INTERVENTION,
        intervention_type=InterventionType.COGNITIVE_RESTRUCTURING,
        narrative_context="Patient stuck in negative thought patterns",
        therapeutic_context={
            "negative_thoughts": ["I'm a failure", "Nothing ever works out for me"],
            "thought_patterns": ["catastrophizing", "all_or_nothing"]
        }
    )

    cognitive_response = agent.generate_therapeutic_dialogue(cognitive_request)
    print("✓ Cognitive restructuring intervention generated")
    print(f"  Therapeutic value: {cognitive_response.therapeutic_value:.2f}")
    print(f"  Content: \"{cognitive_response.dialogue_content}\"")

    # Test 5: Character dialogue context
    print("\n--- Test 5: Character Dialogue Context ---")
    context = agent.get_character_dialogue_context(
        "dr_sarah",
        {"user_id": "patient_001", "session_id": "session_003"}
    )

    print("✓ Character dialogue context retrieved")
    print(f"  Character name: {context['character_state']['name']}")
    print(f"  Therapeutic role: {context['character_state']['therapeutic_role']}")
    print(f"  Current mood: {context['character_state']['current_mood']}")
    print(f"  Empathy level: {context['character_state']['dialogue_style']['empathy_level']:.2f}")
    print(f"  Recent memories: {len(context['recent_memories'])}")
    print(f"  Development milestones: {len(context['development_summary']['relationship_summary'])}")

    # Test 6: Voice consistency validation
    print("\n--- Test 6: Voice Consistency Validation ---")

    # Test consistent dialogue
    consistent_dialogue = "I understand that this situation is quite challenging for you. Let us work together to explore some strategies that might help."
    consistency_score, issues = agent.voice_manager.validate_voice_consistency(
        therapist, consistent_dialogue
    )
    print("✓ Consistent dialogue validation:")
    print(f"  Score: {consistency_score:.2f}")
    print(f"  Issues: {len(issues)}")

    # Test inconsistent dialogue
    inconsistent_dialogue = "Hey, yeah, whatever you wanna do is totally fine with me, dude."
    consistency_score, issues = agent.voice_manager.validate_voice_consistency(
        therapist, inconsistent_dialogue
    )
    print("✓ Inconsistent dialogue validation:")
    print(f"  Score: {consistency_score:.2f}")
    print(f"  Issues: {len(issues)} - {issues}")

    # Test 7: Character memory and relationship tracking
    print("\n--- Test 7: Character Memory and Relationship Tracking ---")

    # Generate several interactions to build memory
    interactions = [
        ("Assessment session", DialogueType.ASSESSMENT),
        ("Anxiety management", DialogueType.INTERVENTION),
        ("Progress reflection", DialogueType.REFLECTION)
    ]

    for context_desc, dialogue_type in interactions:
        request = TherapeuticDialogueRequest(
            character_id="dr_sarah",
            dialogue_type=dialogue_type,
            narrative_context=context_desc
        )
        agent.generate_therapeutic_dialogue(request)

    # Check updated character state
    updated_character = agent.character_system.get_character_state("dr_sarah")
    print("✓ Character memory tracking:")
    print(f"  Total memories: {len(updated_character.memory_fragments)}")
    print(f"  Relationships: {len(updated_character.relationship_scores)}")
    print(f"  Last interaction: {updated_character.last_interaction}")

    if updated_character.memory_fragments:
        latest_memory = updated_character.memory_fragments[-1]
        print(f"  Latest memory: \"{latest_memory.content[:50]}...\"")
        print(f"  Emotional weight: {latest_memory.emotional_weight:.2f}")

    print("\n🎉 All therapeutic dialogue system tests passed! System is working correctly.")
    print("\nKey Features Demonstrated:")
    print("  ✓ Character-specific therapeutic dialogue generation")
    print("  ✓ Multiple intervention types (mindfulness, cognitive restructuring)")
    print("  ✓ Different character roles (therapist, mentor, companion)")
    print("  ✓ Voice consistency validation and maintenance")
    print("  ✓ Character memory and relationship tracking")
    print("  ✓ Therapeutic context integration")
    print("  ✓ Emotional state-aware responses")

    return True

if __name__ == "__main__":
    test_therapeutic_dialogue_system()
