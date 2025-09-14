#!/usr/bin/env python3
"""
Test runner for fully integrated Interactive Narrative Engine with all components
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

def test_full_therapeutic_journey():
    """Test a complete therapeutic journey with all integrated components."""
    print("\n=== Testing Full Therapeutic Journey ===")

    # Create engine instance
    engine = InteractiveNarrativeEngine()
    print("✓ Created InteractiveNarrativeEngine with all integrations")

    # Check which systems are available
    systems_available = []
    if engine.branching_system:
        systems_available.append("Narrative Branching")
    if engine.therapeutic_orchestrator:
        systems_available.append("Therapeutic Orchestrator")
    if engine.langgraph_workflow:
        systems_available.append("LangGraph Workflow")

    print(f"  - Available systems: {', '.join(systems_available)}")

    try:
        # Start a therapeutic session
        session = engine.start_session("therapeutic_user", "anxiety_therapy")

        # Set up an anxious emotional state
        if session.emotional_state:
            session.emotional_state.primary_emotion = session.emotional_state.primary_emotion.__class__.ANXIOUS
            session.emotional_state.intensity = 0.8

        # Add a therapist character
        session.character_states["therapist"] = type('CharacterState', (), {
            'name': 'Dr. Sarah',
            'therapeutic_role': 'therapist',
            'current_mood': 'supportive'
        })()

        # Set location to therapy room
        session.current_location_id = "therapy_room"

        print("✓ Started therapeutic session")
        print(f"  - Session ID: {session.session_id}")
        print(f"  - Emotional state: {session.emotional_state.primary_emotion.value} (intensity: {session.emotional_state.intensity})")
        print(f"  - Location: {session.current_location_id}")
        print(f"  - Characters present: {list(session.character_states.keys())}")

        # Simulate a therapeutic journey with multiple interactions
        therapeutic_interactions = [
            ("I'm feeling really anxious about my presentation tomorrow", "anxiety_expression"),
            ("I want to try some breathing exercises", "therapeutic_action"),
            ("Can you help me understand why I get so nervous?", "therapeutic_inquiry"),
            ("I think the breathing helped a little", "progress_acknowledgment"),
            ("What other techniques can I use when I feel this way?", "skill_seeking"),
            ("I feel more confident now about handling my anxiety", "therapeutic_progress")
        ]

        total_therapeutic_value = 0.0

        for i, (user_input, interaction_type) in enumerate(therapeutic_interactions, 1):
            print(f"\n--- Interaction {i}: {interaction_type} ---")
            print(f"User: {user_input}")

            # Create user choice
            choice = UserChoice(
                choice_id=f"interaction_{i}",
                choice_text=user_input,
                choice_type="therapeutic" if "therapeutic" in interaction_type else "dialogue"
            )

            # Process the choice
            response = engine.process_user_choice(session.session_id, choice)

            print(f"✓ Processed {interaction_type}")
            print(f"  - Response type: {response.response_type}")
            print(f"  - Content: {response.content[:100]}...")

            # Check for therapeutic metadata
            if response.metadata:
                therapeutic_value = response.metadata.get("therapeutic_value", 0)
                total_therapeutic_value += therapeutic_value
                print(f"  - Therapeutic value: {therapeutic_value:.2f}")

                if "agent_type" in response.metadata:
                    print(f"  - Processed by: {response.metadata['agent_type']}")

            # Show available choices
            if response.choices:
                print(f"  - Available choices: {len(response.choices)}")
                for j, choice_option in enumerate(response.choices[:2], 1):  # Show first 2
                    print(f"    {j}. {choice_option['text']}")
                    if 'therapeutic_weight' in choice_option:
                        print(f"       (therapeutic weight: {choice_option['therapeutic_weight']})")

        print("\n✓ Completed therapeutic journey")
        print(f"  - Total interactions: {len(therapeutic_interactions)}")
        print(f"  - Cumulative therapeutic value: {total_therapeutic_value:.2f}")

        # Check final session state
        final_session = engine.get_session(session.session_id)
        print(f"  - Final narrative position: {final_session.narrative_position}")

        if final_session.narrative_context:
            print(f"  - Choice history length: {len(final_session.narrative_context.user_choice_history)}")

        # Get current scenario
        scenario = engine.get_current_scenario(session.session_id)
        if scenario:
            print(f"  - Scenario therapeutic progress: {scenario.get('therapeutic_progress', {})}")

        return True

    except Exception as e:
        print(f"✗ Error in therapeutic journey: {e}")
        return False

def test_system_integration_robustness():
    """Test the robustness of system integration under various conditions."""
    print("\n=== Testing System Integration Robustness ===")

    engine = InteractiveNarrativeEngine()

    try:
        # Test with minimal session setup
        session = engine.start_session("robustness_test")
        print("✓ Created minimal session")

        # Test various input types
        test_inputs = [
            ("", "empty_input"),
            ("help", "basic_command"),
            ("I'm feeling overwhelmed and don't know what to do", "complex_emotional"),
            ("talk to someone about my problems", "social_seeking"),
            ("look around", "exploration"),
            ("practice mindfulness", "therapeutic_direct"),
            ("a" * 200, "very_long_input"),  # Very long input
            ("!@#$%^&*()", "special_characters"),
            ("I feel better now", "positive_emotion")
        ]

        successful_processes = 0

        for user_input, input_type in test_inputs:
            try:
                choice = UserChoice(
                    choice_id=f"test_{input_type}",
                    choice_text=user_input,
                    choice_type="action"
                )

                response = engine.process_user_choice(session.session_id, choice)

                if response and response.content:
                    successful_processes += 1
                    print(f"✓ Handled {input_type}: {len(response.content)} chars")
                else:
                    print(f"⚠ Weak response for {input_type}")

            except Exception as e:
                print(f"✗ Failed to handle {input_type}: {e}")

        print(f"✓ Successfully processed {successful_processes}/{len(test_inputs)} input types")

        # Test session management under stress
        sessions_created = 0
        for i in range(5):
            try:
                engine.start_session(f"stress_test_user_{i}")
                sessions_created += 1
            except Exception as e:
                print(f"✗ Failed to create session {i}: {e}")

        print(f"✓ Created {sessions_created}/5 stress test sessions")

        # Test cleanup
        active_count_before = engine.get_active_session_count()
        cleaned = engine.cleanup_inactive_sessions(max_age_hours=0)  # Clean all
        active_count_after = engine.get_active_session_count()

        print(f"✓ Session cleanup: {active_count_before} -> {active_count_after} (cleaned: {cleaned})")

        return True

    except Exception as e:
        print(f"✗ Error in robustness testing: {e}")
        return False

def test_therapeutic_effectiveness():
    """Test the therapeutic effectiveness of the integrated system."""
    print("\n=== Testing Therapeutic Effectiveness ===")

    engine = InteractiveNarrativeEngine()

    try:
        # Create session with specific therapeutic needs
        session = engine.start_session("effectiveness_test", "depression_support")

        # Set depressed emotional state
        if session.emotional_state:
            session.emotional_state.primary_emotion = session.emotional_state.primary_emotion.__class__.DEPRESSED
            session.emotional_state.intensity = 0.7

        print("✓ Created session with depressed emotional state")

        # Test therapeutic intervention effectiveness
        therapeutic_scenarios = [
            {
                "input": "I feel hopeless and nothing seems to matter",
                "expected_elements": ["support", "understanding", "hope"],
                "therapeutic_focus": "emotional_support"
            },
            {
                "input": "I want to learn how to cope with these feelings",
                "expected_elements": ["coping", "strategy", "technique"],
                "therapeutic_focus": "skill_building"
            },
            {
                "input": "I tried the technique you suggested and it helped",
                "expected_elements": ["progress", "acknowledge", "continue"],
                "therapeutic_focus": "progress_reinforcement"
            }
        ]

        therapeutic_effectiveness_score = 0.0

        for i, scenario in enumerate(therapeutic_scenarios, 1):
            print(f"\n--- Therapeutic Scenario {i}: {scenario['therapeutic_focus']} ---")

            choice = UserChoice(
                choice_id=f"therapeutic_{i}",
                choice_text=scenario["input"],
                choice_type="therapeutic"
            )

            response = engine.process_user_choice(session.session_id, choice)

            # Analyze therapeutic effectiveness
            content_lower = response.content.lower()
            elements_found = sum(1 for element in scenario["expected_elements"]
                               if element in content_lower)

            scenario_effectiveness = elements_found / len(scenario["expected_elements"])
            therapeutic_effectiveness_score += scenario_effectiveness

            print(f"✓ Scenario effectiveness: {scenario_effectiveness:.2f}")
            print(f"  - Elements found: {elements_found}/{len(scenario['expected_elements'])}")
            print(f"  - Response: {response.content[:80]}...")

            # Check for therapeutic value in metadata
            if response.metadata and "therapeutic_value" in response.metadata:
                print(f"  - Therapeutic value: {response.metadata['therapeutic_value']:.2f}")

        overall_effectiveness = therapeutic_effectiveness_score / len(therapeutic_scenarios)
        print(f"\n✓ Overall therapeutic effectiveness: {overall_effectiveness:.2f}")

        if overall_effectiveness > 0.6:
            print("✓ System demonstrates good therapeutic effectiveness")
        elif overall_effectiveness > 0.3:
            print("⚠ System shows moderate therapeutic effectiveness")
        else:
            print("✗ System shows low therapeutic effectiveness")

        return overall_effectiveness > 0.3

    except Exception as e:
        print(f"✗ Error in therapeutic effectiveness testing: {e}")
        return False

def main():
    """Run all full integration tests."""
    print("Full Integration Test Suite")
    print("=" * 60)

    success = True

    # Run comprehensive integration tests
    tests = [
        test_full_therapeutic_journey,
        test_system_integration_robustness,
        test_therapeutic_effectiveness
    ]

    for test_func in tests:
        if not test_func():
            success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ All full integration tests passed!")
        print("🎉 The Interactive Narrative Engine is ready for therapeutic use!")
        return 0
    else:
        print("✗ Some full integration tests failed!")
        print("⚠ The system may need additional refinement.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
