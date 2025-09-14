#!/usr/bin/env python3
"""
Integration test for Therapeutic Technique Demonstration System

This script tests the integration of the therapeutic technique demonstration
system with the existing TTA prototype infrastructure.
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

from core.therapeutic_technique_demonstration import (
    TechniqueType,
    TherapeuticTechniqueDemo,
)
from models.data_models import (
    EmotionalState,
    EmotionalStateType,
    NarrativeContext,
    SessionState,
    TherapeuticProgress,
)


def test_basic_integration():
    """Test basic integration of technique demonstration system."""
    print("🧪 Testing Therapeutic Technique Demonstration Integration")
    print("=" * 60)

    # Initialize the system
    print("1. Initializing TherapeuticTechniqueDemo system...")
    demo_system = TherapeuticTechniqueDemo()
    print("   ✅ System initialized successfully")

    # Create test context
    print("\n2. Creating test narrative context...")
    context = NarrativeContext(
        session_id="test_session_001",
        current_location_id="peaceful_garden",
        recent_events=[
            "User expressed feeling anxious about upcoming challenges",
            "Character offered support and guidance",
            "User showed interest in learning coping techniques"
        ],
        user_choice_history=[
            {
                "choice_id": "seek_help",
                "choice_text": "I'd like to learn some techniques to help with anxiety",
                "timestamp": "2025-01-08T10:30:00"
            }
        ]
    )
    print("   ✅ Narrative context created")

    # Create test session state
    print("\n3. Creating test session state...")
    session_state = SessionState(
        session_id="test_session_001",
        user_id="test_user_001",
        current_scenario_id="anxiety_support_scenario",
        current_location_id="peaceful_garden"
    )

    # Add emotional state
    session_state.emotional_state = EmotionalState(
        primary_emotion=EmotionalStateType.ANXIOUS,
        intensity=0.7,
        secondary_emotions=[EmotionalStateType.OVERWHELMED],
        triggers=["upcoming challenges", "uncertainty"],
        confidence_level=0.6
    )

    # Add therapeutic progress
    session_state.therapeutic_progress = TherapeuticProgress(
        user_id="test_user_001"
    )
    session_state.therapeutic_progress.add_goal(
        title="Learn anxiety management techniques",
        description="Develop practical skills for managing anxiety in daily life",
        target_behaviors=["practice breathing exercises", "use grounding techniques"]
    )

    print("   ✅ Session state created with emotional state and therapeutic goals")

    # Test technique demonstration creation
    print("\n4. Creating deep breathing technique demonstration...")
    demonstration = demo_system.create_technique_demonstration(
        technique_type=TechniqueType.DEEP_BREATHING,
        context=context,
        session_state=session_state,
        user_preferences={
            'learning_style': 'guided',
            'experience_level': 'beginner',
            'confidence_level': 0.4
        }
    )

    print("   ✅ Technique demonstration created successfully")
    print(f"   📋 Scenario: {demonstration['scenario'].title}")
    print(f"   🎯 Technique: {demonstration['scenario'].technique_type.value}")
    print(f"   📚 Learning objectives: {len(demonstration['scenario'].learning_objectives)}")
    print(f"   🔢 Steps: {len(demonstration['scenario'].technique_steps)}")
    print(f"   ⏱️  Duration: {demonstration['scenario'].estimated_duration} minutes")

    # Test step execution
    print("\n5. Testing step execution...")
    step_1 = demo_system.execute_technique_step(
        demonstration_package=demonstration,
        step_number=1,
        user_response={}
    )

    print("   ✅ Step 1 executed successfully")
    print(f"   📝 Instruction: {step_1['step_instruction']}")
    print(f"   🎭 Character guidance: {step_1['character_guidance'][:100]}...")
    print(f"   🎯 Expected outcome: {step_1['expected_outcome']}")

    # Test with user response
    if len(demonstration['scenario'].technique_steps) > 1:
        print("\n6. Testing step execution with user response...")
        step_2 = demo_system.execute_technique_step(
            demonstration_package=demonstration,
            step_number=2,
            user_response={
                'engagement_level': 'high',
                'step_completed': True,
                'questions_answered': 1,
                'user_feedback': 'This feels calming'
            }
        )

        print("   ✅ Step 2 executed with user response")
        print(f"   📝 Instruction: {step_2['step_instruction']}")

    # Test reflection opportunity generation
    print("\n7. Testing reflection opportunity generation...")
    user_experience = {
        'engagement_level': 'high',
        'completed_all_steps': True,
        'found_challenging': False,
        'found_easy': False,
        'emotional_response': True,
        'first_time': True,
        'wants_more_practice': True
    }

    reflection = demo_system.generate_reflection_opportunity(
        demonstration_package=demonstration,
        user_experience=user_experience,
        context=context
    )

    print("   ✅ Reflection opportunity generated")
    print(f"   🤔 Questions: {len(reflection.guiding_questions)}")
    print(f"   📚 Learning points: {len(reflection.learning_points)}")
    print(f"   💡 Expected insights: {len(reflection.expected_insights)}")
    print(f"   🎯 Follow-up actions: {len(reflection.follow_up_actions)}")

    # Display sample reflection questions
    print("\n   Sample reflection questions:")
    for i, question in enumerate(reflection.guiding_questions[:3], 1):
        print(f"   {i}. {question}")

    print("\n8. Testing different technique types...")

    # Test grounding technique
    grounding_demo = demo_system.create_technique_demonstration(
        technique_type=TechniqueType.GROUNDING_5_4_3_2_1,
        context=context,
        session_state=session_state
    )
    print(f"   ✅ Grounding technique demo: {grounding_demo['scenario'].title}")

    # Test cognitive reframing
    reframing_demo = demo_system.create_technique_demonstration(
        technique_type=TechniqueType.COGNITIVE_REFRAMING,
        context=context,
        session_state=session_state
    )
    print(f"   ✅ Cognitive reframing demo: {reframing_demo['scenario'].title}")

    print("\n" + "=" * 60)
    print("🎉 All integration tests passed successfully!")
    print("\n📊 Test Summary:")
    print("   • System initialization: ✅")
    print("   • Context and state creation: ✅")
    print("   • Technique demonstration creation: ✅")
    print("   • Step execution: ✅")
    print("   • User response processing: ✅")
    print("   • Reflection opportunity generation: ✅")
    print("   • Multiple technique types: ✅")

    return True

def test_narrative_integration():
    """Test narrative integration aspects."""
    print("\n🎭 Testing Narrative Integration Features")
    print("=" * 60)

    demo_system = TherapeuticTechniqueDemo()

    # Create context with rich narrative elements
    context = NarrativeContext(
        session_id="narrative_test",
        current_location_id="enchanted_forest_clearing",
        active_characters=["wise_mentor", "forest_spirit"],
        recent_events=[
            "You discovered a hidden clearing in the enchanted forest",
            "The wise mentor appeared and sensed your inner turmoil",
            "A gentle forest spirit offered to teach you ancient calming techniques"
        ],
        world_state_flags={
            "time_of_day": "golden_hour",
            "weather": "gentle_breeze",
            "atmosphere": "mystical_and_peaceful"
        }
    )

    session_state = SessionState(
        session_id="narrative_test",
        user_id="narrative_user",
        current_scenario_id="forest_wisdom_scenario"
    )

    # Create demonstration with rich narrative context
    demonstration = demo_system.create_technique_demonstration(
        technique_type=TechniqueType.MINDFUL_OBSERVATION,
        context=context,
        session_state=session_state,
        user_preferences={'learning_style': 'observational'}
    )

    print("✅ Narrative-rich demonstration created")
    print(f"📖 Narrative setup: {demonstration['scenario'].narrative_setup[:150]}...")

    # Check integration plan
    integration_plan = demonstration['integration_plan']
    print(f"🔗 Integration approach: {integration_plan['integration_approach']}")
    print(f"🎬 Story transitions: {len(integration_plan['story_transitions'])} defined")
    print(f"🎭 Character interactions: {len(integration_plan['character_interactions'])} planned")

    print("✅ Narrative integration test completed")

    return True

if __name__ == "__main__":
    try:
        # Run basic integration test
        test_basic_integration()

        # Run narrative integration test
        test_narrative_integration()

        print("\n🏆 All integration tests completed successfully!")
        print("The Therapeutic Technique Demonstration system is ready for use.")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
