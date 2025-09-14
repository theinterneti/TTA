#!/usr/bin/env python3
"""
Direct test runner for Interactive Narrative Engine
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

def test_basic_functionality():
    """Test basic engine functionality."""
    print("\n=== Testing Basic Functionality ===")

    # Create engine instance
    engine = InteractiveNarrativeEngine()
    print("✓ Created InteractiveNarrativeEngine instance")

    # Test session creation
    try:
        session = engine.start_session("test_user", "test_scenario")
        print(f"✓ Created session: {session.session_id}")
        print(f"  - User ID: {session.user_id}")
        print(f"  - Scenario ID: {session.current_scenario_id}")
        print(f"  - Narrative position: {session.narrative_position}")
    except Exception as e:
        print(f"✗ Failed to create session: {e}")
        return False

    # Test session retrieval
    try:
        retrieved_session = engine.get_session(session.session_id)
        if retrieved_session and retrieved_session.session_id == session.session_id:
            print("✓ Successfully retrieved session")
        else:
            print("✗ Failed to retrieve session")
            return False
    except Exception as e:
        print(f"✗ Error retrieving session: {e}")
        return False

    # Test user choice processing
    try:
        choice = UserChoice(
            choice_id="test_choice",
            choice_text="look around",
            choice_type="action"
        )
        response = engine.process_user_choice(session.session_id, choice)
        print(f"✓ Processed user choice: {choice.choice_text}")
        print(f"  - Response type: {response.response_type}")
        print(f"  - Response content: {response.content[:100]}...")
        print(f"  - Number of choices: {len(response.choices)}")
    except Exception as e:
        print(f"✗ Failed to process user choice: {e}")
        return False

    # Test scenario retrieval
    try:
        scenario = engine.get_current_scenario(session.session_id)
        if scenario:
            print("✓ Retrieved current scenario")
            print(f"  - Narrative position: {scenario['narrative_position']}")
        else:
            print("✗ Failed to retrieve scenario")
            return False
    except Exception as e:
        print(f"✗ Error retrieving scenario: {e}")
        return False

    # Test narrative advancement
    try:
        event = NarrativeEvent(
            event_id="test_event",
            event_type="location_change",
            description="Player moved to garden",
            location_id="garden"
        )
        success = engine.advance_narrative(session.session_id, event)
        if success:
            print("✓ Advanced narrative successfully")
            updated_session = engine.get_session(session.session_id)
            print(f"  - New narrative position: {updated_session.narrative_position}")
            print(f"  - New location: {updated_session.current_location_id}")
        else:
            print("✗ Failed to advance narrative")
            return False
    except Exception as e:
        print(f"✗ Error advancing narrative: {e}")
        return False

    # Test session cleanup
    try:
        success = engine.end_session(session.session_id)
        if success:
            print("✓ Ended session successfully")
        else:
            print("✗ Failed to end session")
            return False
    except Exception as e:
        print(f"✗ Error ending session: {e}")
        return False

    return True

def test_error_handling():
    """Test error handling scenarios."""
    print("\n=== Testing Error Handling ===")

    engine = InteractiveNarrativeEngine()

    # Test invalid user ID
    try:
        engine.start_session("")
        print("✗ Should have failed with empty user ID")
        return False
    except ValueError:
        print("✓ Correctly rejected empty user ID")
    except Exception as e:
        print(f"✗ Unexpected error with empty user ID: {e}")
        return False

    # Test invalid session ID
    try:
        response = engine.process_user_choice("invalid_session", UserChoice("test", "test"))
        print("✗ Should have failed with invalid session ID")
        return False
    except ValueError:
        print("✓ Correctly rejected invalid session ID")
    except Exception as e:
        print(f"✗ Unexpected error with invalid session ID: {e}")
        return False

    # Test empty choice text
    try:
        session = engine.start_session("test_user")
        choice = UserChoice("test", "")
        response = engine.process_user_choice(session.session_id, choice)
        if response.response_type == "error":
            print("✓ Correctly handled empty choice text")
        else:
            print("✗ Should have returned error for empty choice")
            return False
    except Exception as e:
        print(f"✗ Unexpected error with empty choice: {e}")
        return False

    return True

def main():
    """Run all tests."""
    print("Interactive Narrative Engine Test Suite")
    print("=" * 50)

    success = True

    # Run basic functionality tests
    if not test_basic_functionality():
        success = False

    # Run error handling tests
    if not test_error_handling():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
