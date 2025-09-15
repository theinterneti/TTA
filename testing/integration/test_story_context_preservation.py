#!/usr/bin/env python3
"""
Test script for story context preservation and narrative element tracking.
Validates that narrative elements are properly detected, tracked, and preserved across conversation turns.
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
os.environ['PYTHONPATH'] = src_dir


from src.components.user_experience.therapeutic_chat_interface import (
    ChatMessage,
    MessageType,
    TherapeuticChatInterface,
    TherapeuticContext,
)


def test_story_context_preservation():
    """Test story context detection and preservation across multiple conversation turns."""

    # Initialize chat interface
    chat_interface = TherapeuticChatInterface()

    # Create test context
    TherapeuticContext(
        user_id="test_user",
        session_id="test_session_story"
    )

    # Simulate a multi-turn conversation with narrative elements
    conversation_turns = [
        {
            "content": "I want to tell you about my childhood story with my mother",
            "expected_elements": ["characters", "temporal_markers"],
            "expected_story_type": "personal_history"
        },
        {
            "content": "She always told me I was strong, but the anxiety keeps telling me I'm weak",
            "expected_elements": ["characters", "externalization_language"],
            "expected_story_type": "problem_externalization"
        },
        {
            "content": "There was this one time when I felt confident speaking up in class",
            "expected_elements": ["unique_outcomes", "temporal_markers"],
            "expected_story_type": "exception_story"
        },
        {
            "content": "I'm trying to figure out who I am beyond this struggle",
            "expected_elements": ["identity_statements"],
            "expected_story_type": "identity_narrative"
        }
    ]

    print("Testing Story Context Preservation")
    print("=" * 50)

    narrative_tracking_results = []

    for turn_num, turn_data in enumerate(conversation_turns, 1):
        print(f"\n--- Turn {turn_num} ---")
        print(f"Input: '{turn_data['content']}'")

        # Create message
        message = ChatMessage(
            session_id="test_session_story",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=turn_data["content"]
        )

        # Test story context detection
        story_context = chat_interface._detect_story_context(message)
        print(f"Story Context Detected: {story_context['has_narrative_elements']}")
        print(f"Story Type: {story_context.get('story_type', 'None')}")
        print(f"Story Indicators: {story_context['story_indicators']}")

        # Test narrative element extraction
        narrative_elements = chat_interface._extract_narrative_elements(message, story_context)
        print("Narrative Elements:")
        for element_type, elements in narrative_elements.items():
            if elements:
                print(f"  {element_type}: {elements}")

        # Test narrative progression tracking
        chat_interface._track_narrative_progression("test_session_story", narrative_elements)

        # Test story-engaged response generation
        if story_context["has_narrative_elements"]:
            story_response = chat_interface._generate_story_engaged_response(
                message, story_context, narrative_elements
            )
            print(f"Story-Engaged Response: '{story_response[:100]}...'")

        # Validate expected elements
        validation_results = []
        for expected_element in turn_data["expected_elements"]:
            found = False
            if expected_element in story_context.get("narrative_elements", {}):
                found = len(story_context["narrative_elements"][expected_element]) > 0
            validation_results.append((expected_element, found))

        print("Validation Results:")
        for element, found in validation_results:
            print(f"  {element}: {'✓' if found else '✗'}")

        # Check story type
        expected_story_type = turn_data["expected_story_type"]
        actual_story_type = story_context.get("story_type")
        story_type_correct = actual_story_type == expected_story_type
        print(f"Story Type: Expected '{expected_story_type}', Got '{actual_story_type}' {'✓' if story_type_correct else '✗'}")

        narrative_tracking_results.append({
            "turn": turn_num,
            "story_detected": story_context["has_narrative_elements"],
            "story_type_correct": story_type_correct,
            "elements_found": sum(1 for _, found in validation_results if found),
            "elements_expected": len(validation_results)
        })

    # Test narrative progression tracking across turns
    print("\n--- Narrative Progression Tracking ---")
    if hasattr(chat_interface, 'narrative_tracking') and "test_session_story" in chat_interface.narrative_tracking:
        session_narrative = chat_interface.narrative_tracking["test_session_story"]

        print(f"Character Mentions: {session_narrative['character_mentions']}")
        print(f"Recurring Themes: {session_narrative['recurring_themes']}")
        print(f"Emotional Journey Length: {len(session_narrative['emotional_journey'])}")
        print(f"Narrative Coherence Score: {session_narrative['narrative_coherence_score']:.2f}")

        # Validate progression tracking
        has_characters = len(session_narrative['character_mentions']) > 0
        has_themes = len(session_narrative['recurring_themes']) > 0
        has_emotional_journey = len(session_narrative['emotional_journey']) > 0

        print("Progression Tracking Validation:")
        print(f"  Characters Tracked: {'✓' if has_characters else '✗'}")
        print(f"  Themes Tracked: {'✓' if has_themes else '✗'}")
        print(f"  Emotional Journey: {'✓' if has_emotional_journey else '✗'}")
    else:
        print("✗ Narrative tracking not initialized or session not found")

    # Summary
    print("\n" + "=" * 50)
    print("STORY CONTEXT PRESERVATION RESULTS:")

    total_turns = len(narrative_tracking_results)
    successful_detections = sum(1 for result in narrative_tracking_results if result["story_detected"])
    correct_story_types = sum(1 for result in narrative_tracking_results if result["story_type_correct"])
    total_elements_found = sum(result["elements_found"] for result in narrative_tracking_results)
    total_elements_expected = sum(result["elements_expected"] for result in narrative_tracking_results)

    print(f"Story Detection Rate: {successful_detections}/{total_turns} ({successful_detections/total_turns*100:.1f}%)")
    print(f"Story Type Accuracy: {correct_story_types}/{total_turns} ({correct_story_types/total_turns*100:.1f}%)")
    print(f"Element Detection Rate: {total_elements_found}/{total_elements_expected} ({total_elements_found/total_elements_expected*100:.1f}%)")

    # Overall success criteria
    success_criteria = [
        successful_detections >= total_turns * 0.8,  # 80% story detection
        correct_story_types >= total_turns * 0.7,   # 70% story type accuracy
        total_elements_found >= total_elements_expected * 0.6,  # 60% element detection
        hasattr(chat_interface, 'narrative_tracking')  # Tracking system works
    ]

    overall_success = all(success_criteria)

    if overall_success:
        print("✓ STORY CONTEXT PRESERVATION: WORKING CORRECTLY")
    else:
        print("✗ STORY CONTEXT PRESERVATION: NEEDS IMPROVEMENT")

    return overall_success

if __name__ == "__main__":
    success = test_story_context_preservation()
    sys.exit(0 if success else 1)
