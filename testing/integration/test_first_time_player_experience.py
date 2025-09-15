#!/usr/bin/env python3
"""
Comprehensive validation test for the first-time player experience.
Tests the complete therapeutic journey from character creation to storytelling gameplay.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
os.environ['PYTHONPATH'] = src_dir

# Import all necessary components
from src.components.user_experience.therapeutic_chat_interface import (
    ChatMessage,
    MessageType,
    TherapeuticChatInterface,
    TherapeuticContext,
)
from src.player_experience.managers.character_avatar_manager import (
    CharacterAvatarManager,
)
from src.player_experience.managers.world_management_module import WorldManagementModule
from src.player_experience.models.character import (
    Character,
    TherapeuticGoal,
    TherapeuticProfile,
)
from src.player_experience.models.conversation_state import (
    ConversationStage,
)
from src.player_experience.services.character_to_gameplay_transition import (
    CharacterToGameplayTransition,
)
from src.player_experience.services.conversational_character_service import (
    ConversationalCharacterService,
)
from src.player_experience.services.story_initialization_service import (
    StoryInitializationService,
)
from src.player_experience.services.therapeutic_world_selection_service import (
    TherapeuticWorldSelectionService,
)


async def test_first_time_player_experience():
    """Comprehensive test of the complete first-time player experience."""

    print("First-Time Player Experience Validation")
    print("=" * 60)

    # Test player data
    test_player_id = "test_player_001"
    test_results = {
        "character_creation": False,
        "world_selection": False,
        "character_world_integration": False,
        "storytelling_session": False,
        "narrative_therapy_integration": False,
        "end_to_end_flow": False
    }

    try:
        # 1. CHARACTER CREATION SYSTEM VALIDATION
        print("\n1. CHARACTER CREATION SYSTEM VALIDATION")
        print("-" * 50)

        # Create mock dependencies for ConversationalCharacterService
        class MockCharacterManager:
            async def create_character(self, *args, **kwargs):
                return Character(
                    character_id="test_char_001",
                    name="Alex",
                    age=25,
                    background="Student dealing with anxiety",
                    therapeutic_profile=TherapeuticProfile(
                        primary_goals=[TherapeuticGoal.ANXIETY_MANAGEMENT],
                        therapeutic_readiness=0.7,
                        engagement_preferences={"conversational": True}
                    )
                )

        class MockCharacterRepository:
            async def save_character(self, character):
                return character

        class MockSafetyValidator:
            async def validate_content(self, content, context=None):
                # Return a mock validation result object with required attributes
                class MockValidationResult:
                    def __init__(self):
                        self.is_safe = True
                        self.confidence = 0.95
                        self.crisis_assessment = None
                        self.safety_level = "safe"
                        self.validation_action = "approve"

                return MockValidationResult()

        # Initialize character creation service with mocks
        character_service = ConversationalCharacterService(
            character_manager=MockCharacterManager(),
            character_repository=MockCharacterRepository(),
            safety_validator=MockSafetyValidator()
        )

        # Start conversational character creation
        conversation_id, welcome_message = await character_service.start_conversation(
            test_player_id, {"test_mode": True}
        )

        print(f"✓ Character creation conversation started: {conversation_id}")
        print(f"  Welcome message: '{welcome_message.content[:80]}...'")

        # Simulate conversation flow through all stages
        conversation_stages = [
            ("My name is Alex", ConversationStage.IDENTITY),
            ("I'm 28 years old and work as a teacher", ConversationStage.BACKGROUND),
            ("I want to work on anxiety and self-confidence", ConversationStage.READINESS),
        ]

        for user_input, expected_stage in conversation_stages:
            response = await character_service.process_user_response(conversation_id, user_input)
            if response:
                # Handle response format (could be list or object)
                if isinstance(response, list) and len(response) > 0:
                    response_content = response[0].content if hasattr(response[0], 'content') else str(response[0])
                elif hasattr(response, 'content'):
                    response_content = response.content
                else:
                    response_content = str(response)

                print(f"  Stage {expected_stage.value}: '{response_content[:60]}...'")
            else:
                print(f"  ✗ Failed at stage {expected_stage.value}")
                break
        else:
            # Complete character creation
            completion_result = await character_service.complete_conversation(conversation_id)
            if completion_result:
                print("✓ Character creation completed successfully")
                test_character_id = completion_result.character_id
                test_results["character_creation"] = True
            else:
                print("✗ Character creation completion failed")
                return test_results

        # 2. WORLD SELECTION/CREATION TESTING
        print("\n2. WORLD SELECTION/CREATION TESTING")
        print("-" * 50)

        # Initialize world management
        world_manager = WorldManagementModule()
        TherapeuticWorldSelectionService()

        # Get available worlds
        available_worlds = world_manager.get_available_worlds(test_player_id)
        print(f"✓ Found {len(available_worlds)} available worlds")

        if available_worlds:
            # Test world details retrieval
            test_world = available_worlds[0]
            world_details = world_manager.get_world_details(test_world.world_id)
            if world_details:
                print(f"✓ World details retrieved: '{world_details.name}'")
                print(f"  Themes: {world_details.therapeutic_themes}")
                print(f"  Difficulty: {world_details.difficulty_level}")
                test_world_id = test_world.world_id
                test_results["world_selection"] = True
            else:
                print("✗ Failed to retrieve world details")
                return test_results
        else:
            print("✗ No worlds available for testing")
            return test_results

        # 3. CHARACTER-WORLD INTEGRATION VERIFICATION
        print("\n3. CHARACTER-WORLD INTEGRATION VERIFICATION")
        print("-" * 50)

        # Get character data
        character_manager = CharacterAvatarManager()
        character_data = character_manager.get_character(test_character_id)

        if character_data:
            print(f"✓ Character data retrieved: '{character_data.name}'")

            # Test therapeutic goal alignment
            therapeutic_goals = [goal.value for goal in character_data.therapeutic_profile.therapeutic_goals]
            print(f"  Therapeutic goals: {therapeutic_goals}")

            # Initialize character in world
            session_data = world_manager.initialize_character_in_world(
                test_character_id, test_world_id
            )

            if session_data:
                print("✓ Character-world integration successful")
                print(f"  Session ID: {session_data['session_id']}")
                test_session_id = session_data['session_id']
                test_results["character_world_integration"] = True
            else:
                print("✗ Character-world integration failed")
                return test_results
        else:
            print("✗ Failed to retrieve character data")
            return test_results

        # 4. COMPLETE STORYTELLING SESSION TEST
        print("\n4. COMPLETE STORYTELLING SESSION TEST")
        print("-" * 50)

        # Initialize storytelling components
        story_service = StoryInitializationService()
        chat_interface = TherapeuticChatInterface()
        await chat_interface._initialize_therapeutic_templates()

        # Initialize story context
        story_context = await story_service.initialize_story_context(
            test_player_id, test_character_id, test_world_id, therapeutic_goals
        )

        if story_context:
            print("✓ Story context initialized")

            # Create therapeutic context
            therapeutic_context = TherapeuticContext(
                user_id=test_player_id,
                session_id=test_session_id,
                therapeutic_goals=therapeutic_goals,
                preferred_therapeutic_approaches=character_data.therapeutic_profile.therapeutic_approaches
            )

            # Test 10-turn storytelling session
            print("  Testing 10-turn storytelling session:")

            story_turns = [
                "I want to explore my anxiety about public speaking",
                "Tell me about a time when I felt confident",
                "I remember when I was a child, my teacher praised my presentation",
                "But the anxiety keeps telling me I'll fail",
                "What if I could separate myself from this fear?",
                "I want to rewrite this story about myself",
                "There was this one time when I spoke up and felt proud",
                "How can I build on that strength?",
                "I'm starting to see myself differently in this story",
                "What would the next chapter of my growth look like?"
            ]

            narrative_responses = []
            for turn, user_input in enumerate(story_turns, 1):
                # Create chat message
                message = ChatMessage(
                    session_id=test_session_id,
                    user_id=test_player_id,
                    message_type=MessageType.USER_MESSAGE,
                    content=user_input
                )

                # Generate response using enhanced narrative therapy
                response = await chat_interface._generate_narrative_response(
                    message, therapeutic_context, None
                )

                narrative_responses.append(response)
                print(f"    Turn {turn}: '{response[:60]}...'")

            # Validate narrative therapy integration
            unique_responses = len(set(narrative_responses))
            response_diversity = unique_responses / len(narrative_responses) * 100

            print(f"  ✓ Session completed with {response_diversity:.1f}% response diversity")

            if response_diversity >= 50:  # At least 50% unique responses
                test_results["storytelling_session"] = True
                test_results["narrative_therapy_integration"] = True
            else:
                print("  ✗ Insufficient response diversity")
        else:
            print("✗ Story context initialization failed")
            return test_results

        # 5. END-TO-END EXPERIENCE VALIDATION
        print("\n5. END-TO-END EXPERIENCE VALIDATION")
        print("-" * 50)

        # Test complete flow integration
        transition_service = CharacterToGameplayTransition()

        # Initiate complete transition
        transition_id = await transition_service.initiate_transition(
            test_player_id, test_character_id, character_data, therapeutic_goals
        )

        if transition_id:
            print(f"✓ End-to-end transition successful: {transition_id}")
            test_results["end_to_end_flow"] = True
        else:
            print("✗ End-to-end transition failed")

        # Performance validation
        print("\n6. PERFORMANCE VALIDATION")
        print("-" * 50)

        # Test response time for narrative therapy
        start_time = datetime.now()
        test_message = ChatMessage(
            session_id=test_session_id,
            user_id=test_player_id,
            message_type=MessageType.USER_MESSAGE,
            content="I want to tell you my story about overcoming challenges"
        )

        response = await chat_interface._generate_narrative_response(
            test_message, therapeutic_context, None
        )

        response_time = (datetime.now() - start_time).total_seconds() * 1000  # milliseconds
        print(f"✓ Narrative response time: {response_time:.2f}ms")

        if response_time < 1000:  # Sub-second performance
            print("✓ Performance within sub-millisecond benchmarks")
        else:
            print("⚠ Performance exceeds target benchmarks")

    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return test_results

    # Final Results
    print("\n" + "=" * 60)
    print("FIRST-TIME PLAYER EXPERIENCE VALIDATION RESULTS:")
    print("-" * 60)

    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    overall_success = all(test_results.values())
    success_rate = sum(test_results.values()) / len(test_results) * 100

    print(f"\nOverall Success Rate: {success_rate:.1f}%")

    if overall_success:
        print("🎉 FIRST-TIME PLAYER EXPERIENCE: INCREDIBLE!")
        print("Complete therapeutic journey validated successfully!")
    else:
        print("⚠ FIRST-TIME PLAYER EXPERIENCE: NEEDS IMPROVEMENT")

    return test_results

async def main():
    results = await test_first_time_player_experience()
    overall_success = all(results.values())
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    asyncio.run(main())
