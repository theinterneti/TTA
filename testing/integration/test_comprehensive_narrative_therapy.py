#!/usr/bin/env python3
"""
Comprehensive test script for narrative therapy functionality.
Tests framework selection, response diversity, story engagement, and interactive storytelling.
"""

import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)
os.environ["PYTHONPATH"] = src_dir


from src.components.user_experience.therapeutic_chat_interface import (
    ChatMessage,
    MessageType,
    TherapeuticChatInterface,
    TherapeuticContext,
    TherapeuticFramework,
)


async def test_comprehensive_narrative_therapy():
    """Comprehensive test of all narrative therapy enhancements."""

    # Initialize chat interface
    chat_interface = TherapeuticChatInterface()

    # Initialize therapeutic templates
    await chat_interface._initialize_therapeutic_templates()

    # Create test context
    context = TherapeuticContext(
        user_id="test_user", session_id="comprehensive_test_session"
    )

    print("Comprehensive Narrative Therapy Testing")
    print("=" * 60)

    # Test 1: Framework Selection Scenarios
    print("\n1. FRAMEWORK SELECTION TESTING")
    print("-" * 40)

    framework_test_cases = [
        # Narrative therapy triggers
        (
            "I want to tell you my story about overcoming depression",
            TherapeuticFramework.NARRATIVE,
        ),
        ("This chapter of my life has been difficult", TherapeuticFramework.NARRATIVE),
        ("I need to externalize this anxiety", TherapeuticFramework.NARRATIVE),
        ("What would others say about my journey?", TherapeuticFramework.NARRATIVE),
        ("I'm trying to rewrite my narrative", TherapeuticFramework.NARRATIVE),
        # Other frameworks should still work
        ("I keep having negative thoughts", TherapeuticFramework.CBT),
        ("I feel overwhelmed by emotions", TherapeuticFramework.DBT),
        ("I want to be more mindful", TherapeuticFramework.MINDFULNESS),
        ("What are my strengths?", TherapeuticFramework.SOLUTION_FOCUSED),
        # Mixed keywords - narrative should take priority
        ("I think my story feels overwhelming", TherapeuticFramework.NARRATIVE),
        ("My identity and thoughts are confusing", TherapeuticFramework.NARRATIVE),
    ]

    framework_success = 0
    for i, (test_input, expected_framework) in enumerate(framework_test_cases, 1):
        message = ChatMessage(
            session_id="comprehensive_test_session",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=test_input,
        )

        selected_framework = chat_interface._select_therapeutic_framework(
            message, context
        )
        is_correct = selected_framework == expected_framework

        print(f"  {i:2d}. '{test_input[:50]}...' -> {selected_framework.value}")
        print(
            f"      Expected: {expected_framework.value}, {'✓' if is_correct else '✗'}"
        )

        if is_correct:
            framework_success += 1

    framework_success_rate = framework_success / len(framework_test_cases) * 100
    print(
        f"\nFramework Selection Success Rate: {framework_success}/{len(framework_test_cases)} ({framework_success_rate:.1f}%)"
    )

    # Test 2: Response Diversity
    print("\n2. RESPONSE DIVERSITY TESTING")
    print("-" * 40)

    narrative_message = ChatMessage(
        session_id="comprehensive_test_session",
        user_id="test_user",
        message_type=MessageType.USER_MESSAGE,
        content="I want to share my story about finding strength",
    )

    # Generate multiple responses to test diversity
    responses = []
    for _ in range(10):
        response = chat_interface._get_framework_response_template(
            TherapeuticFramework.NARRATIVE
        )
        responses.append(response)

    unique_responses = len(set(responses))
    diversity_score = unique_responses / len(responses) * 100

    print(
        f"Generated {len(responses)} responses, {unique_responses} unique ({diversity_score:.1f}% diversity)"
    )
    print("Sample responses:")
    unique_responses_list = list(set(responses))[:3]
    for i, response in enumerate(unique_responses_list, 1):
        print(f"  {i}. '{response[:80]}...'")

    # Test 3: Story Context Detection and Engagement
    print("\n3. STORY CONTEXT DETECTION TESTING")
    print("-" * 40)

    story_test_cases = [
        {
            "content": "When I was growing up, my mother always told me I was special",
            "should_detect": True,
            "expected_type": "personal_history",
        },
        {
            "content": "The anxiety keeps telling me I'm not good enough",
            "should_detect": True,
            "expected_type": "problem_externalization",
        },
        {
            "content": "I'm trying to figure out who I really am",
            "should_detect": True,
            "expected_type": "identity_narrative",
        },
        {
            "content": "There was this one time when I felt truly confident",
            "should_detect": True,
            "expected_type": "exception_story",
        },
        {
            "content": "I think I need help with my thoughts",
            "should_detect": False,
            "expected_type": None,
        },
    ]

    story_detection_success = 0
    for i, test_case in enumerate(story_test_cases, 1):
        message = ChatMessage(
            session_id="comprehensive_test_session",
            user_id="test_user",
            message_type=MessageType.USER_MESSAGE,
            content=test_case["content"],
        )

        story_context = chat_interface._detect_story_context(message)
        detected = story_context["has_narrative_elements"]
        story_type = story_context.get("story_type")

        detection_correct = detected == test_case["should_detect"]
        type_correct = (
            story_type == test_case["expected_type"]
            if test_case["should_detect"]
            else True
        )

        print(f"  {i}. '{test_case['content'][:50]}...'")
        print(
            f"     Detected: {detected} (expected: {test_case['should_detect']}) {'✓' if detection_correct else '✗'}"
        )
        if test_case["should_detect"]:
            print(
                f"     Type: {story_type} (expected: {test_case['expected_type']}) {'✓' if type_correct else '✗'}"
            )

        if detection_correct and type_correct:
            story_detection_success += 1

    story_success_rate = story_detection_success / len(story_test_cases) * 100
    print(
        f"\nStory Detection Success Rate: {story_detection_success}/{len(story_test_cases)} ({story_success_rate:.1f}%)"
    )

    # Test 4: Interactive Storytelling Features
    print("\n4. INTERACTIVE STORYTELLING TESTING")
    print("-" * 40)

    # Test enhanced narrative response generation
    narrative_message = ChatMessage(
        session_id="comprehensive_test_session",
        user_id="test_user",
        message_type=MessageType.USER_MESSAGE,
        content="I want to tell you about a transformative experience in my life",
    )

    try:
        enhanced_response = await chat_interface._generate_narrative_response(
            narrative_message, context, None
        )
        print(f"Enhanced Narrative Response: '{enhanced_response[:100]}...'")
        interactive_features_working = True
    except Exception as e:
        print(f"Enhanced Narrative Response Error: {e}")
        interactive_features_working = False

    # Test story continuity - initialize tracking first
    chat_interface._enhance_narrative_state_management("comprehensive_test_session")

    if hasattr(chat_interface, "narrative_tracking"):
        continuity_response = chat_interface._generate_continuity_aware_response(
            "comprehensive_test_session", {"story_type": "personal_history"}
        )
        print(f"Continuity Response: '{continuity_response[:100]}...'")
        continuity_working = True
    else:
        print("Continuity tracking not available")
        continuity_working = False

    # Overall Results
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST RESULTS:")
    print(f"Framework Selection: {framework_success_rate:.1f}% success")
    print(f"Response Diversity: {diversity_score:.1f}% unique responses")
    print(f"Story Detection: {story_success_rate:.1f}% accuracy")
    print(f"Interactive Features: {'✓' if interactive_features_working else '✗'}")
    print(f"Story Continuity: {'✓' if continuity_working else '✗'}")

    # Success criteria
    overall_success = (
        framework_success_rate >= 90
        and diversity_score >= 50
        and story_success_rate >= 80
        and interactive_features_working
        and continuity_working
    )

    if overall_success:
        print("\n✓ COMPREHENSIVE NARRATIVE THERAPY TEST: PASSED")
        print("All critical narrative therapy gaps have been successfully addressed!")
    else:
        print("\n✗ COMPREHENSIVE NARRATIVE THERAPY TEST: NEEDS IMPROVEMENT")

    return overall_success


async def main():
    success = await test_comprehensive_narrative_therapy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
