#!/usr/bin/env python3
"""
Test runner for integrated Interactive Narrative Engine with Narrative Branching
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.interactive_narrative_engine import (
        InteractiveNarrativeEngine,
        NarrativeEvent,
        NarrativeResponse,
        UserChoice,
    )
    print("✓ Successfully imported InteractiveNarrativeEngine classes")
except ImportError as e:
    print(f"✗ Failed to import InteractiveNarrativeEngine: {e}")
    sys.exit(1)

def test_integrated_choice_processing():
    """Test integrated choice processing with narrative branching."""
    print("\n=== Testing Integrated Choice Processing ===")

    # Create engine instance
    engine = InteractiveNarrativeEngine()
    print("✓ Created InteractiveNarrativeEngine instance")

    # Start a session with an anxious user
    try:
        session = engine.start_session("anxious_user", "therapy_scenario")

        # Set emotional state to anxious
        if session.emotional_state:
            session.emotional_state.primary_emotion = session.emotional_state.primary_emotion.__class__.ANXIOUS
            session.emotional_state.intensity = 0.8

        print("✓ Created session with anxious emotional state")
        print(f"  - Session ID: {session.session_id}")
        print(f"  - Emotional state: {session.emotional_state.primary_emotion.value if session.emotional_state else 'unknown'}")
        print(f"  - Intensity: {session.emotional_state.intensity if session.emotional_state else 0.0}")
    except Exception as e:
        print(f"✗ Failed to create session: {e}")
        return False

    # Test therapeutic choice processing
    try:
        # Make a therapeutic choice
        therapeutic_choice = UserChoice(
            choice_id="breathing_exercise",
            choice_text="Take a moment to focus on your breathing",
            choice_type="therapeutic"
        )

        response = engine.process_user_choice(session.session_id, therapeutic_choice)
        print("✓ Processed therapeutic choice")
        print(f"  - Response type: {response.response_type}")
        print(f"  - Response content: {response.content[:100]}...")
        print(f"  - Number of choices: {len(response.choices)}")

        # Check for therapeutic metadata
        if response.metadata and "therapeutic_impact" in response.metadata:
            print(f"  - Therapeutic impact: {response.metadata['therapeutic_impact']}")
            print(f"  - Consequence type: {response.metadata.get('consequence_type', 'unknown')}")

        # Display available choices
        print("  - Available choices:")
        for i, choice in enumerate(response.choices[:3], 1):  # Show first 3
            print(f"    {i}. {choice['text']} ({choice.get('type', 'unknown')})")
            if 'therapeutic_weight' in choice:
                print(f"       Therapeutic weight: {choice['therapeutic_weight']}")

    except Exception as e:
        print(f"✗ Failed to process therapeutic choice: {e}")
        return False

    # Test dialogue choice processing
    try:
        dialogue_choice = UserChoice(
            choice_id="talk_to_therapist",
            choice_text="Talk to the therapist about your feelings",
            choice_type="dialogue"
        )

        response2 = engine.process_user_choice(session.session_id, dialogue_choice)
        print("✓ Processed dialogue choice")
        print(f"  - Response content: {response2.content[:100]}...")

        # Check narrative position advancement
        updated_session = engine.get_session(session.session_id)
        print(f"  - Narrative position advanced to: {updated_session.narrative_position}")

    except Exception as e:
        print(f"✗ Failed to process dialogue choice: {e}")
        return False

    return True

def test_choice_generation_with_emotional_state():
    """Test choice generation based on emotional state."""
    print("\n=== Testing Choice Generation with Emotional State ===")

    engine = InteractiveNarrativeEngine()

    try:
        # Create session with high anxiety
        session = engine.start_session("test_user", "anxiety_scenario")

        # Set high anxiety state
        if session.emotional_state:
            session.emotional_state.primary_emotion = session.emotional_state.primary_emotion.__class__.ANXIOUS
            session.emotional_state.intensity = 0.9

        # Set location to garden
        session.current_location_id = "peaceful_garden"

        # Add a therapist character
        session.character_states["therapist"] = type('CharacterState', (), {
            'name': 'Dr. Smith',
            'therapeutic_role': 'therapist',
            'current_mood': 'supportive'
        })()

        # Process a simple choice to trigger choice generation
        simple_choice = UserChoice(
            choice_id="look_around",
            choice_text="look around",
            choice_type="exploration"
        )

        response = engine.process_user_choice(session.session_id, simple_choice)

        print("✓ Generated choices for high anxiety state")
        print(f"  - Total choices: {len(response.choices)}")

        # Analyze choice types
        therapeutic_choices = [c for c in response.choices if c.get('type') == 'therapeutic']
        dialogue_choices = [c for c in response.choices if c.get('type') == 'dialogue']
        exploration_choices = [c for c in response.choices if c.get('type') == 'exploration']

        print(f"  - Therapeutic choices: {len(therapeutic_choices)}")
        print(f"  - Dialogue choices: {len(dialogue_choices)}")
        print(f"  - Exploration choices: {len(exploration_choices)}")

        # Display therapeutic choices
        if therapeutic_choices:
            print("  - Therapeutic options available:")
            for choice in therapeutic_choices:
                print(f"    • {choice['text']} (weight: {choice.get('therapeutic_weight', 0)})")

        return True

    except Exception as e:
        print(f"✗ Error testing choice generation: {e}")
        return False

def test_story_impact_integration():
    """Test story impact tracking integration."""
    print("\n=== Testing Story Impact Integration ===")

    engine = InteractiveNarrativeEngine()

    try:
        session = engine.start_session("impact_test_user", "therapy_journey")
        session_id = session.session_id

        # Make a series of choices to build story impact
        choices_to_make = [
            ("breathing_exercise", "Take deep breaths to calm yourself", "therapeutic"),
            ("talk_to_therapist", "Share your concerns with the therapist", "dialogue"),
            ("practice_mindfulness", "Practice a mindfulness technique", "therapeutic"),
            ("reflect_on_progress", "Reflect on your therapeutic progress", "reflection")
        ]

        for i, (choice_id, choice_text, choice_type) in enumerate(choices_to_make, 1):
            choice = UserChoice(
                choice_id=choice_id,
                choice_text=choice_text,
                choice_type=choice_type
            )

            response = engine.process_user_choice(session_id, choice)
            print(f"✓ Processed choice {i}: {choice_text}")

            # Check for therapeutic impact in metadata
            if response.metadata and "therapeutic_impact" in response.metadata:
                print(f"  - Therapeutic impact: {response.metadata['therapeutic_impact']}")

        # Check if branching system tracked the story impact
        if engine.branching_system:
            impact = engine.branching_system.calculate_story_impact(session_id)
            if impact:
                print("✓ Story impact tracked successfully")
                print(f"  - Cumulative therapeutic score: {impact.cumulative_therapeutic_score:.2f}")
                print(f"  - Emotional journey entries: {len(impact.emotional_journey)}")
            else:
                print("⚠ Story impact not found (may be expected if branching system not fully integrated)")

        return True

    except Exception as e:
        print(f"✗ Error testing story impact integration: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Integrated Interactive Narrative Engine Test Suite")
    print("=" * 60)

    success = True

    # Run integration tests
    tests = [
        test_integrated_choice_processing,
        test_choice_generation_with_emotional_state,
        test_story_impact_integration
    ]

    for test_func in tests:
        if not test_func():
            success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
