#!/usr/bin/env python3
"""
Direct test runner for Narrative Branching system
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.narrative_branching import (
        BranchingPoint,
        ChoiceConsequence,
        ChoiceOption,
        ChoiceType,
        ConsequenceType,
        NarrativeBranchingChoice,
        StoryImpact,
    )

    print("✓ Successfully imported NarrativeBranchingChoice classes")
except ImportError as e:
    print(f"✗ Failed to import NarrativeBranchingChoice: {e}")
    sys.exit(1)


def test_choice_generation():
    """Test choice option generation."""
    print("\n=== Testing Choice Generation ===")

    branching_system = NarrativeBranchingChoice()
    print("✓ Created NarrativeBranchingChoice instance")

    # Test context with high anxiety
    test_context = {
        "session_id": "test_session",
        "location_id": "garden",
        "characters": ["therapist", "companion"],
        "emotional_state": {"primary_emotion": "anxious", "intensity": 0.8},
        "therapeutic_opportunities": ["anxiety_management"],
    }

    try:
        choices = branching_system.generate_choice_options(test_context)
        print(f"✓ Generated {len(choices)} choice options")

        # Display choices
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice.choice_text} ({choice.choice_type.value})")
            print(f"     Therapeutic weight: {choice.therapeutic_weight}")
            print(f"     Emotional tone: {choice.emotional_tone}")

        # Check for therapeutic choices
        therapeutic_choices = [
            c for c in choices if c.choice_type == ChoiceType.THERAPEUTIC
        ]
        if therapeutic_choices:
            print(
                f"✓ Found {len(therapeutic_choices)} therapeutic choices for high anxiety"
            )
        else:
            print("⚠ No therapeutic choices found for high anxiety")

        return True
    except Exception as e:
        print(f"✗ Error generating choices: {e}")
        return False


def test_choice_processing():
    """Test choice processing and consequence generation."""
    print("\n=== Testing Choice Processing ===")

    branching_system = NarrativeBranchingChoice()

    test_context = {
        "session_id": "test_session",
        "location_id": "garden",
        "characters": ["therapist"],
        "emotional_state": {"primary_emotion": "anxious", "intensity": 0.7},
    }

    try:
        # Test therapeutic choice
        therapeutic_choice = ChoiceOption(
            choice_id="breathing_exercise",
            choice_text="Take a moment to focus on your breathing",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_weight=0.8,
            emotional_tone="calming",
            consequences=["reduced_anxiety", "increased_mindfulness"],
        )

        consequence = branching_system.process_user_choice(
            therapeutic_choice, test_context
        )
        print("✓ Processed therapeutic choice")
        print(f"  - Consequence type: {consequence.consequence_type.value}")
        print(f"  - Impact level: {consequence.impact_level.value}")
        print(f"  - Therapeutic impact: {consequence.therapeutic_impact}")
        print(f"  - Narrative flags: {consequence.narrative_flags}")

        # Check emotional impact
        if consequence.emotional_impact:
            print(f"  - Emotional impact: {consequence.emotional_impact}")

        # Test dialogue choice
        dialogue_choice = ChoiceOption(
            choice_id="talk_to_therapist",
            choice_text="Talk to the therapist about your feelings",
            choice_type=ChoiceType.DIALOGUE,
            therapeutic_weight=0.5,
            consequences=["social_connection", "emotional_expression"],
        )

        consequence2 = branching_system.process_user_choice(
            dialogue_choice, test_context
        )
        print("✓ Processed dialogue choice")
        print(f"  - Affected entities: {consequence2.affected_entities}")
        print(f"  - Consequence type: {consequence2.consequence_type.value}")

        return True
    except Exception as e:
        print(f"✗ Error processing choices: {e}")
        return False


def test_story_impact_tracking():
    """Test story impact tracking."""
    print("\n=== Testing Story Impact Tracking ===")

    branching_system = NarrativeBranchingChoice()
    session_id = "test_session"

    test_context = {
        "session_id": session_id,
        "location_id": "therapy_room",
        "emotional_state": {"primary_emotion": "calm", "intensity": 0.3},
    }

    try:
        # Make several choices to build up story impact
        choices = [
            ChoiceOption(
                "choice1", "Practice mindfulness", ChoiceType.THERAPEUTIC, 0.7
            ),
            ChoiceOption("choice2", "Share your feelings", ChoiceType.DIALOGUE, 0.4),
            ChoiceOption(
                "choice3", "Try a coping strategy", ChoiceType.THERAPEUTIC, 0.8
            ),
            ChoiceOption("choice4", "Reflect on progress", ChoiceType.REFLECTION, 0.5),
        ]

        for i, choice in enumerate(choices, 1):
            branching_system.process_user_choice(choice, test_context)
            print(f"✓ Processed choice {i}: {choice.choice_text}")

        # Check story impact
        impact = branching_system.calculate_story_impact(session_id)
        if impact:
            print("✓ Retrieved story impact")
            print(
                f"  - Cumulative therapeutic score: {impact.cumulative_therapeutic_score:.2f}"
            )
            print(f"  - Emotional journey entries: {len(impact.emotional_journey)}")
            print(f"  - World state flags: {len(impact.world_state_flags)}")
        else:
            print("✗ Failed to retrieve story impact")
            return False

        return True
    except Exception as e:
        print(f"✗ Error tracking story impact: {e}")
        return False


def test_narrative_branching():
    """Test narrative branch creation."""
    print("\n=== Testing Narrative Branching ===")

    branching_system = NarrativeBranchingChoice()

    try:
        # Create choice history with therapeutic focus
        choice_history = [
            ChoiceConsequence(
                choice_id="therapeutic1",
                description="Used breathing technique",
                consequence_type=ConsequenceType.THERAPEUTIC,
                therapeutic_impact=0.7,
            ),
            ChoiceConsequence(
                choice_id="therapeutic2",
                description="Practiced mindfulness",
                consequence_type=ConsequenceType.THERAPEUTIC,
                therapeutic_impact=0.6,
            ),
            ChoiceConsequence(
                choice_id="dialogue1",
                description="Talked to therapist",
                consequence_type=ConsequenceType.RELATIONSHIP,
                therapeutic_impact=0.3,
            ),
        ]

        # Create branching point
        branching_point = BranchingPoint(
            narrative_position=5,
            location_id="therapy_room",
            available_branches=["intensive_therapy"],
        )

        # Create narrative branch
        branch = branching_system.create_narrative_branch(
            branching_point, choice_history
        )

        if branch:
            print("✓ Created narrative branch")
            print(f"  - Branch name: {branch.branch_name}")
            print(f"  - Therapeutic theme: {branch.therapeutic_theme}")
            print(f"  - Therapeutic opportunities: {branch.therapeutic_opportunities}")
            print(f"  - Required choices: {branch.required_choices}")
        else:
            print("✗ Failed to create narrative branch")
            return False

        return True
    except Exception as e:
        print(f"✗ Error creating narrative branch: {e}")
        return False


def test_session_management():
    """Test session data management."""
    print("\n=== Testing Session Management ===")

    branching_system = NarrativeBranchingChoice()
    session_id = "test_session"

    try:
        # Add some data
        test_context = {"session_id": session_id}
        choice = ChoiceOption("test_choice", "Test choice", ChoiceType.DIALOGUE)
        branching_system.process_user_choice(choice, test_context)

        # Check choice history
        history = branching_system.get_choice_history(session_id)
        print(f"✓ Retrieved choice history: {len(history)} entries")

        # Clear session data
        success = branching_system.clear_session_data(session_id)
        if success:
            print("✓ Cleared session data")

            # Verify data is cleared
            history_after = branching_system.get_choice_history(session_id)
            if len(history_after) == 0:
                print("✓ Confirmed data was cleared")
            else:
                print("✗ Data was not properly cleared")
                return False
        else:
            print("✗ Failed to clear session data")
            return False

        return True
    except Exception as e:
        print(f"✗ Error in session management: {e}")
        return False


def main():
    """Run all tests."""
    print("Narrative Branching System Test Suite")
    print("=" * 50)

    success = True

    # Run all test functions
    tests = [
        test_choice_generation,
        test_choice_processing,
        test_story_impact_tracking,
        test_narrative_branching,
        test_session_management,
    ]

    for test_func in tests:
        if not test_func():
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
