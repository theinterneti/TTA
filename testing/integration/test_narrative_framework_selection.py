#!/usr/bin/env python3
"""
Test script for narrative therapy framework selection functionality.
Validates that the enhanced framework selection properly detects narrative content.
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = src_dir


from src.components.user_experience.therapeutic_chat_interface import (
    ChatMessage,
    MessageType,
    TherapeuticChatInterface,
    TherapeuticContext,
    TherapeuticFramework,
)


def test_narrative_framework_selection():
    """Test narrative therapy framework selection with various story-related inputs."""

    # Initialize chat interface
    chat_interface = TherapeuticChatInterface()

    # Create test context
    context = TherapeuticContext(
        user_id="test_user",
        session_id="test_session"
    )

    # Test cases for narrative therapy detection
    narrative_test_cases = [
        "I want to tell you my story about overcoming anxiety",
        "This chapter of my life has been really difficult",
        "I feel like the problem defines who I am",
        "I need to rewrite the narrative of my life",
        "There was an exception when I felt confident",
        "My identity seems tied to this struggle",
        "I want to externalize this depression",
        "What would others say about my journey?",
        "I'm at a crossroads in my story",
        "The character I play in relationships is exhausting"
    ]

    # Test cases for other frameworks (should not trigger narrative)
    other_framework_cases = [
        ("I keep having negative thoughts", TherapeuticFramework.CBT),
        ("I feel overwhelmed by intense emotions", TherapeuticFramework.DBT),
        ("I want to be more mindful and present", TherapeuticFramework.MINDFULNESS),
        ("What are my strengths and what works for me?", TherapeuticFramework.SOLUTION_FOCUSED)
    ]

    print("Testing Narrative Therapy Framework Selection")
    print("=" * 50)

    # Test narrative therapy detection
    print("\n1. Testing Narrative Therapy Detection:")
    narrative_success = 0
    for i, test_content in enumerate(narrative_test_cases, 1):
        message = ChatMessage(
            session_id="test_session",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=test_content
        )

        selected_framework = chat_interface._select_therapeutic_framework(message, context)
        is_narrative = selected_framework == TherapeuticFramework.NARRATIVE

        print(f"  {i:2d}. '{test_content[:50]}...' -> {selected_framework.value}")
        print(f"      Expected: NARRATIVE, Got: {selected_framework.value}, {'✓' if is_narrative else '✗'}")

        if is_narrative:
            narrative_success += 1

    print(f"\nNarrative Detection Success Rate: {narrative_success}/{len(narrative_test_cases)} ({narrative_success/len(narrative_test_cases)*100:.1f}%)")

    # Test other framework detection (ensure they still work)
    print("\n2. Testing Other Framework Detection:")
    other_success = 0
    for i, (test_content, expected_framework) in enumerate(other_framework_cases, 1):
        message = ChatMessage(
            session_id="test_session",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=test_content
        )

        selected_framework = chat_interface._select_therapeutic_framework(message, context)
        is_correct = selected_framework == expected_framework

        print(f"  {i}. '{test_content}' -> {selected_framework.value}")
        print(f"     Expected: {expected_framework.value}, Got: {selected_framework.value}, {'✓' if is_correct else '✗'}")

        if is_correct:
            other_success += 1

    print(f"\nOther Framework Detection Success Rate: {other_success}/{len(other_framework_cases)} ({other_success/len(other_framework_cases)*100:.1f}%)")

    # Test edge cases
    print("\n3. Testing Edge Cases:")
    edge_cases = [
        ("", "Empty message"),
        ("Hello", "Generic greeting"),
        ("I think my story feels overwhelming", "Mixed keywords - should prioritize narrative")
    ]

    for test_content, description in edge_cases:
        message = ChatMessage(
            session_id="test_session",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=test_content
        )

        selected_framework = chat_interface._select_therapeutic_framework(message, context)
        print(f"  '{test_content}' ({description}) -> {selected_framework.value}")

    # Summary
    total_success = narrative_success + other_success
    total_tests = len(narrative_test_cases) + len(other_framework_cases)

    print("\n" + "=" * 50)
    print("OVERALL RESULTS:")
    print(f"Total Success Rate: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")

    if narrative_success == len(narrative_test_cases):
        print("✓ NARRATIVE THERAPY DETECTION: WORKING CORRECTLY")
    else:
        print("✗ NARRATIVE THERAPY DETECTION: NEEDS IMPROVEMENT")

    if other_success == len(other_framework_cases):
        print("✓ OTHER FRAMEWORK DETECTION: WORKING CORRECTLY")
    else:
        print("✗ OTHER FRAMEWORK DETECTION: REGRESSION DETECTED")

    return total_success == total_tests

if __name__ == "__main__":
    success = test_narrative_framework_selection()
    sys.exit(0 if success else 1)
