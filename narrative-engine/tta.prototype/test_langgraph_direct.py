#!/usr/bin/env python3
"""
Direct test runner for LangGraph Integration
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.langgraph_integration import (
        AgentResponse,
        TherapeuticAgentOrchestrator,
        TherapeuticContext,
        TherapeuticIPA,
        TherapeuticNGA,
    )
    print("✓ Successfully imported LangGraph integration classes")
except ImportError as e:
    print(f"✗ Failed to import LangGraph integration: {e}")
    sys.exit(1)

def test_therapeutic_ipa():
    """Test TherapeuticIPA functionality."""
    print("\n=== Testing Therapeutic IPA ===")

    try:
        ipa = TherapeuticIPA()
        print("✓ Created TherapeuticIPA instance")

        # Test context
        context = TherapeuticContext(
            session_id="test_session",
            therapeutic_goals=["anxiety_management"],
            current_location="therapy_room",
            character_relationships={"therapist": 0.8}
        )

        # Test anxiety-related input
        anxiety_input = "I'm feeling really anxious and need to calm down"
        result = ipa.process_input(anxiety_input, context)

        print("✓ Processed anxiety-related input")
        print(f"  - Intent: {result.get('intent', 'unknown')}")
        print(f"  - Therapeutic intents: {result.get('therapeutic_intent', [])}")
        print(f"  - Detected emotions: {list(result.get('detected_emotions', {}).keys())}")
        print(f"  - Therapeutic priority: {result.get('therapeutic_priority', 0):.2f}")

        # Verify anxiety management was detected
        if "anxiety_management" in result.get("therapeutic_intent", []):
            print("✓ Correctly identified anxiety management intent")
        else:
            print("⚠ Did not identify anxiety management intent")

        # Test social interaction input
        social_input = "talk to therapist about my feelings"
        result2 = ipa.process_input(social_input, context)

        print("✓ Processed social interaction input")
        print(f"  - Intent: {result2.get('intent', 'unknown')}")
        print(f"  - Character: {result2.get('character_name', 'none')}")
        print(f"  - Character relationship: {result2.get('character_relationship_score', 'none')}")

        return True

    except Exception as e:
        print(f"✗ Error testing TherapeuticIPA: {e}")
        return False

def test_therapeutic_nga():
    """Test TherapeuticNGA functionality."""
    print("\n=== Testing Therapeutic NGA ===")

    try:
        nga = TherapeuticNGA()
        print("✓ Created TherapeuticNGA instance")

        # Test context
        context = TherapeuticContext(
            session_id="test_session",
            user_emotional_state={"anxious": 0.7},
            therapeutic_goals=["anxiety_management"],
            user_progress={"anxiety_management": 0.3}
        )

        # Test therapeutic narrative generation
        parsed_input = {
            "intent": "look",
            "therapeutic_intent": ["anxiety_management"],
            "detected_emotions": {"anxious": 0.6},
            "therapeutic_priority": 0.7,
            "original_input": "look around while feeling anxious"
        }

        response = nga.generate_narrative(parsed_input, context)

        print("✓ Generated therapeutic narrative")
        print(f"  - Success: {response.success}")
        print(f"  - Agent type: {response.agent_type}")
        print(f"  - Therapeutic value: {response.therapeutic_value:.2f}")
        print(f"  - Content: {response.content[:100]}...")

        # Check metadata
        if response.metadata:
            print(f"  - Narrative type: {response.metadata.get('narrative_type', 'unknown')}")
            print(f"  - Emotional tone: {response.metadata.get('emotional_tone', 'unknown')}")

        # Test different narrative types
        emotional_input = {
            "intent": "talk",
            "therapeutic_intent": ["emotional_regulation"],
            "detected_emotions": {"angry": 0.8},
            "therapeutic_priority": 0.8,
            "character_name": "therapist"
        }

        response2 = nga.generate_narrative(emotional_input, context)
        print("✓ Generated emotional regulation narrative")
        print(f"  - Content: {response2.content[:100]}...")

        return True

    except Exception as e:
        print(f"✗ Error testing TherapeuticNGA: {e}")
        return False

def test_agent_orchestrator():
    """Test TherapeuticAgentOrchestrator functionality."""
    print("\n=== Testing Therapeutic Agent Orchestrator ===")

    try:
        orchestrator = TherapeuticAgentOrchestrator()
        print("✓ Created TherapeuticAgentOrchestrator instance")

        # Test context
        context = TherapeuticContext(
            session_id="test_session",
            therapeutic_goals=["anxiety_management", "social_connection"],
            current_location="peaceful_garden",
            available_characters=["therapist", "companion"]
        )

        # Test complete interaction processing
        user_inputs = [
            "I'm feeling anxious and want to practice breathing",
            "talk to the therapist about my worries",
            "look around the garden mindfully",
            "I feel a bit better now"
        ]

        for i, user_input in enumerate(user_inputs, 1):
            print(f"\n--- Processing interaction {i}: {user_input} ---")

            response, updated_context = orchestrator.process_user_interaction(
                user_input, context
            )

            print(f"✓ Processed interaction {i}")
            print(f"  - Response success: {response.success}")
            print(f"  - Therapeutic value: {response.therapeutic_value:.2f}")
            print(f"  - Content: {response.content[:80]}...")

            # Check context updates
            print(f"  - Narrative history entries: {len(updated_context.narrative_history)}")
            print(f"  - Emotional state keys: {list(updated_context.user_emotional_state.keys())}")
            print(f"  - Progress tracking: {list(updated_context.user_progress.keys())}")

            # Update context for next iteration
            context = updated_context

        # Test agent status
        status = orchestrator.get_agent_status()
        print(f"\n✓ Agent status: {status['health']}")
        print(f"  - Error count: {status['error_count']}")

        return True

    except Exception as e:
        print(f"✗ Error testing TherapeuticAgentOrchestrator: {e}")
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    print("\n=== Testing Error Handling ===")

    try:
        orchestrator = TherapeuticAgentOrchestrator()
        context = TherapeuticContext(session_id="error_test")

        # Test with empty input
        response, updated_context = orchestrator.process_user_interaction("", context)
        print("✓ Handled empty input")
        print(f"  - Response success: {response.success}")
        print(f"  - Content: {response.content[:60]}...")

        # Test with very long input
        long_input = "a" * 1000
        response, updated_context = orchestrator.process_user_interaction(long_input, context)
        print("✓ Handled very long input")
        print(f"  - Response success: {response.success}")

        # Test with special characters
        special_input = "!@#$%^&*()_+ test input with symbols"
        response, updated_context = orchestrator.process_user_interaction(special_input, context)
        print("✓ Handled special characters")
        print(f"  - Response success: {response.success}")

        # Test error count reset
        orchestrator.error_count = 2
        orchestrator.reset_error_count()
        if orchestrator.error_count == 0:
            print("✓ Error count reset successfully")
        else:
            print("✗ Error count reset failed")
            return False

        return True

    except Exception as e:
        print(f"✗ Error testing error handling: {e}")
        return False

def test_therapeutic_context_management():
    """Test therapeutic context management and updates."""
    print("\n=== Testing Therapeutic Context Management ===")

    try:
        # Create initial context
        context = TherapeuticContext(
            session_id="context_test",
            therapeutic_goals=["anxiety_management"],
            user_emotional_state={"baseline_anxiety": 0.5}
        )

        print("✓ Created initial therapeutic context")
        print(f"  - Session ID: {context.session_id}")
        print(f"  - Goals: {context.therapeutic_goals}")
        print(f"  - Initial emotional state: {context.user_emotional_state}")

        # Test context dictionary conversion
        context_dict = context.to_dict()
        print("✓ Converted context to dictionary")
        print(f"  - Keys: {list(context_dict.keys())}")

        # Simulate context updates through orchestrator
        orchestrator = TherapeuticAgentOrchestrator()

        # Process multiple interactions to build context
        interactions = [
            "I'm feeling anxious about tomorrow",
            "Let me try some breathing exercises",
            "I think I'm getting better at managing this"
        ]

        for interaction in interactions:
            response, context = orchestrator.process_user_interaction(interaction, context)
            print(f"✓ Updated context with: {interaction[:30]}...")

        print("✓ Final context state:")
        print(f"  - Narrative history length: {len(context.narrative_history)}")
        print(f"  - Emotional states tracked: {len(context.user_emotional_state)}")
        print(f"  - Progress areas: {list(context.user_progress.keys())}")

        # Show progress values
        for area, progress in context.user_progress.items():
            print(f"    - {area}: {progress:.2f}")

        return True

    except Exception as e:
        print(f"✗ Error testing context management: {e}")
        return False

def main():
    """Run all LangGraph integration tests."""
    print("LangGraph Integration Test Suite")
    print("=" * 50)

    success = True

    # Run all test functions
    tests = [
        test_therapeutic_ipa,
        test_therapeutic_nga,
        test_agent_orchestrator,
        test_error_handling,
        test_therapeutic_context_management
    ]

    for test_func in tests:
        if not test_func():
            success = False

    print("\n" + "=" * 50)
    if success:
        print("✓ All LangGraph integration tests passed!")
        return 0
    else:
        print("✗ Some LangGraph integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
