#!/usr/bin/env python3
"""
Simple test runner for TTA Prototype data models.
"""

import os
import sys

# Add the models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

from data_models import (
    CharacterState,
    EmotionalState,
    EmotionalStateType,
    InterventionType,
    NarrativeContext,
    SessionState,
    TherapeuticGoal,
    TherapeuticProgress,
    ValidationError,
    validate_all_models,
)


def test_basic_functionality():
    """Test basic functionality of all data models."""
    print("Testing basic data model functionality...")

    try:
        # Test SessionState
        print("  Testing SessionState...")
        session = SessionState(session_id="test_session", user_id="test_user")
        session.validate()

        # Test serialization
        json_str = session.to_json()
        restored_session = SessionState.from_json(json_str)
        assert restored_session.session_id == session.session_id
        print("    ✓ SessionState creation, validation, and serialization")

        # Test CharacterState
        print("  Testing CharacterState...")
        character = CharacterState(character_id="char_1", name="Alice")
        character.add_memory("First meeting", 0.8, ["positive"])
        character.update_relationship("user", 0.5)
        character.validate()
        print("    ✓ CharacterState creation, memory, and relationships")

        # Test TherapeuticProgress
        print("  Testing TherapeuticProgress...")
        progress = TherapeuticProgress(user_id="test_user")
        progress.add_goal("Reduce Anxiety", "Learn coping strategies")
        progress.complete_intervention(
            InterventionType.MINDFULNESS,
            "Practiced meditation",
            8.0,
            "Very helpful"
        )
        progress.validate()
        print("    ✓ TherapeuticProgress with goals and interventions")

        # Test NarrativeContext
        print("  Testing NarrativeContext...")
        narrative = NarrativeContext(session_id="test_session")
        narrative.add_choice("Go left", "choice_1", ["entered forest"])
        narrative.validate()
        print("    ✓ NarrativeContext with choices")

        # Test complex SessionState
        print("  Testing complex SessionState...")
        complex_session = SessionState(
            session_id="complex_session",
            user_id="test_user",
            character_states={"char_1": character},
            therapeutic_progress=progress,
            emotional_state=EmotionalState(primary_emotion=EmotionalStateType.CALM),
            narrative_context=narrative
        )
        complex_session.validate()

        # Test complex serialization
        complex_json = complex_session.to_json()
        restored_complex = SessionState.from_json(complex_json)
        assert restored_complex.session_id == complex_session.session_id
        print("    ✓ Complex SessionState with nested objects")

        print("✅ All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_validation_errors():
    """Test that validation errors are properly raised."""
    print("Testing validation error handling...")

    try:
        # Test empty session ID
        try:
            session = SessionState(session_id="", user_id="test_user")
            session.validate()
            print("❌ Should have raised ValidationError for empty session ID")
            return False
        except ValidationError:
            print("    ✓ Empty session ID validation error")

        # Test invalid personality trait
        try:
            character = CharacterState(
                character_id="char_1",
                name="Alice",
                personality_traits={"openness": 2.0}
            )
            character.validate()
            print("❌ Should have raised ValidationError for invalid personality trait")
            return False
        except ValidationError:
            print("    ✓ Invalid personality trait validation error")

        # Test invalid progress percentage
        try:
            goal = TherapeuticGoal(
                title="Test Goal",
                description="Test Description",
                progress_percentage=150.0
            )
            goal.validate()
            print("❌ Should have raised ValidationError for invalid progress percentage")
            return False
        except ValidationError:
            print("    ✓ Invalid progress percentage validation error")

        print("✅ All validation error tests passed!")
        return True

    except Exception as e:
        print(f"❌ Validation error test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("TTA Prototype Data Models Test Runner")
    print("=" * 50)

    # Run validation utility
    print("Running validate_all_models utility...")
    if validate_all_models():
        print("✅ validate_all_models passed!")
    else:
        print("❌ validate_all_models failed!")
        return False

    print()

    # Run basic functionality tests
    if not test_basic_functionality():
        return False

    print()

    # Run validation error tests
    if not test_validation_errors():
        return False

    print()
    print("=" * 50)
    print("🎉 All tests passed! Data models are working correctly.")
    print("=" * 50)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
