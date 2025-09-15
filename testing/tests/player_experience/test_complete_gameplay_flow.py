"""
Comprehensive Integration Tests for Complete Gameplay Flow

This test suite covers the entire gameplay loop from character creation
through active story participation, ensuring all components work together seamlessly.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.player_experience.services.concurrent_world_state_manager import (
    ConcurrentWorldStateManager,
)
from src.player_experience.services.cross_story_character_persistence import (
    CrossStoryCharacterPersistence,
)
from src.player_experience.services.dynamic_story_generation_service import (
    DynamicStoryGenerationService,
)
from src.player_experience.services.gameplay_chat_manager import GameplayChatManager
from src.player_experience.services.multiverse_navigation_service import (
    MultiverseNavigationService,
)
from src.player_experience.services.narrative_generation_service import (
    NarrativeGenerationService,
)
from src.player_experience.services.story_branching_service import StoryBranchingService
from src.player_experience.services.story_initialization_service import (
    StoryInitializationService,
)
from src.player_experience.services.therapeutic_safety_integration import (
    TherapeuticSafetyIntegration,
)
from src.player_experience.services.therapeutic_world_selection_service import (
    TherapeuticWorldSelectionService,
)


@pytest.fixture
async def gameplay_services():
    """Create all gameplay services for testing."""
    services = {
        "chat_manager": GameplayChatManager(),
        "story_initialization": StoryInitializationService(),
        "world_selection": TherapeuticWorldSelectionService(),
        "narrative_generation": NarrativeGenerationService(),
        "dynamic_story": DynamicStoryGenerationService(),
        "world_state_manager": ConcurrentWorldStateManager(),
        "story_branching": StoryBranchingService(),
        "character_persistence": CrossStoryCharacterPersistence(),
        "multiverse_navigation": MultiverseNavigationService(),
        "safety_integration": TherapeuticSafetyIntegration(),
    }

    # Start services that need initialization
    for service in services.values():
        if hasattr(service, "start"):
            await service.start()

    yield services

    # Cleanup services
    for service in services.values():
        if hasattr(service, "stop"):
            await service.stop()


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "character_id": "test_char_001",
        "name": "Alex",
        "age": 25,
        "background": "college_student",
        "personality_traits": {
            "openness": 0.7,
            "conscientiousness": 0.6,
            "extraversion": 0.5,
            "agreeableness": 0.8,
            "neuroticism": 0.4,
        },
        "therapeutic_goals": ["anxiety_management", "social_skills", "self_esteem"],
        "preferences": {
            "story_complexity": "moderate",
            "interaction_style": "collaborative",
            "therapeutic_approach": "gentle",
        },
    }


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "player_id": "test_player_001",
        "session_id": "test_session_001",
        "therapeutic_profile": {
            "primary_goals": ["anxiety_management", "social_skills"],
            "secondary_goals": ["self_esteem"],
            "risk_factors": [],
            "strengths": ["creativity", "empathy"],
        },
    }


class TestCompleteGameplayFlow:
    """Test the complete gameplay flow integration."""

    @pytest.mark.asyncio
    async def test_character_creation_to_story_initialization(
        self, gameplay_services, sample_character_data, sample_player_data
    ):
        """Test the flow from character creation completion to story initialization."""
        story_service = gameplay_services["story_initialization"]
        gameplay_services["world_selection"]

        # Mock character creation completion
        with patch.object(
            story_service, "_detect_character_completion", return_value=True
        ):
            # Test story initialization
            story_session_id = await story_service.initialize_story_session(
                player_id=sample_player_data["player_id"],
                character_id=sample_character_data["character_id"],
                world_id="therapeutic_garden",
                therapeutic_goals=sample_character_data["therapeutic_goals"],
                story_preferences=sample_character_data["preferences"],
            )

            assert story_session_id is not None
            assert story_session_id.startswith("story_session_")

    @pytest.mark.asyncio
    async def test_world_selection_and_narrative_generation(
        self, gameplay_services, sample_character_data, sample_player_data
    ):
        """Test world selection and initial narrative generation."""
        world_selection = gameplay_services["world_selection"]
        narrative_service = gameplay_services["narrative_generation"]

        # Test world selection
        selected_world = await world_selection.select_optimal_world(
            therapeutic_goals=sample_character_data["therapeutic_goals"],
            character_data=sample_character_data,
            player_preferences=sample_character_data["preferences"],
        )

        assert selected_world.success
        assert selected_world.selected_world is not None

        # Test opening narrative generation
        opening_narrative = await narrative_service.generate_opening_narrative(
            session_id=sample_player_data["session_id"],
            character_id=sample_character_data["character_id"],
            world_id=selected_world.selected_world,
            therapeutic_goals=sample_character_data["therapeutic_goals"],
        )

        assert opening_narrative is not None
        assert "content" in opening_narrative
        assert "text" in opening_narrative["content"]

    @pytest.mark.asyncio
    async def test_real_time_chat_integration(
        self, gameplay_services, sample_player_data
    ):
        """Test real-time chat integration with story generation."""
        chat_manager = gameplay_services["chat_manager"]
        dynamic_story = gameplay_services["dynamic_story"]

        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        connection_id = await chat_manager.add_connection(
            mock_websocket,
            sample_player_data["player_id"],
            sample_player_data["session_id"],
        )

        assert connection_id is not None

        # Test player message processing
        test_message = "I want to explore the garden and find a peaceful place to sit."

        story_response = await dynamic_story.process_player_message(
            session_id=sample_player_data["session_id"],
            player_id=sample_player_data["player_id"],
            message_text=test_message,
        )

        assert story_response is not None
        assert story_response.narrative_text is not None
        assert len(story_response.narrative_text) > 0

    @pytest.mark.asyncio
    async def test_multiverse_and_branching_integration(
        self, gameplay_services, sample_character_data, sample_player_data
    ):
        """Test multiverse creation and story branching."""
        world_state_manager = gameplay_services["world_state_manager"]
        story_branching = gameplay_services["story_branching"]
        multiverse_nav = gameplay_services["multiverse_navigation"]

        # Create initial world instance
        instance_id = await world_state_manager.create_world_instance(
            world_id="therapeutic_garden",
            player_id=sample_player_data["player_id"],
            character_id=sample_character_data["character_id"],
            session_id=sample_player_data["session_id"],
        )

        assert instance_id is not None

        # Create a branch point
        branch_point_id = await story_branching.create_branch_point(
            instance_id=instance_id,
            trigger_type="player_choice",
            decision_context={"choice": "explore_deeper"},
            available_options=[
                {"option_id": "path_a", "text": "Take the peaceful path"},
                {"option_id": "path_b", "text": "Take the challenging path"},
            ],
        )

        assert branch_point_id is not None

        # Create a narrative branch
        branch_id = await story_branching.create_narrative_branch(
            branch_point_id=branch_point_id,
            selected_option={"option_id": "path_a", "text": "Take the peaceful path"},
            session_id=f"{sample_player_data['session_id']}_branch",
            therapeutic_focus=["mindfulness", "anxiety_management"],
        )

        assert branch_id is not None

        # Test multiverse navigation
        destinations = await multiverse_nav.discover_multiverse_destinations(
            sample_player_data["player_id"]
        )

        assert len(destinations) > 0

    @pytest.mark.asyncio
    async def test_character_persistence_across_stories(
        self, gameplay_services, sample_character_data, sample_player_data
    ):
        """Test character persistence across multiple story experiences."""
        character_persistence = gameplay_services["character_persistence"]
        world_state_manager = gameplay_services["world_state_manager"]

        # Create character profile
        profile_id = await character_persistence.create_character_profile(
            character_id=sample_character_data["character_id"],
            player_id=sample_player_data["player_id"],
            base_character_data=sample_character_data,
        )

        assert profile_id is not None

        # Create first story instance
        instance_id_1 = await world_state_manager.create_world_instance(
            world_id="therapeutic_garden",
            player_id=sample_player_data["player_id"],
            character_id=sample_character_data["character_id"],
            session_id=sample_player_data["session_id"],
        )

        # Create character snapshot
        snapshot_id = await character_persistence.create_character_snapshot(
            character_id=sample_character_data["character_id"],
            player_id=sample_player_data["player_id"],
            instance_id=instance_id_1,
            character_data=sample_character_data,
        )

        assert snapshot_id is not None

        # Create second story instance
        instance_id_2 = await world_state_manager.create_world_instance(
            world_id="urban_environment",
            player_id=sample_player_data["player_id"],
            character_id=sample_character_data["character_id"],
            session_id=f"{sample_player_data['session_id']}_2",
        )

        # Transfer character to new story
        transferred_data = await character_persistence.transfer_character_to_story(
            character_id=sample_character_data["character_id"],
            target_instance_id=instance_id_2,
        )

        assert transferred_data is not None
        assert "therapeutic_journey" in transferred_data

    @pytest.mark.asyncio
    async def test_therapeutic_safety_integration(
        self, gameplay_services, sample_player_data
    ):
        """Test therapeutic safety monitoring and intervention."""
        safety_integration = gameplay_services["safety_integration"]

        # Test crisis keyword detection
        crisis_message = "I feel like I can't go on anymore and want to hurt myself"

        safety_alert = await safety_integration.monitor_player_message(
            player_id=sample_player_data["player_id"],
            session_id=sample_player_data["session_id"],
            message_text=crisis_message,
        )

        assert safety_alert is not None
        assert safety_alert.alert_level.value in ["high", "critical"]
        assert safety_alert.requires_human_review

        # Test intervention execution
        intervention_result = await safety_integration.execute_safety_intervention(
            safety_alert
        )

        assert intervention_result["success"]
        assert len(safety_alert.auto_actions_taken) > 0

    @pytest.mark.asyncio
    async def test_end_to_end_gameplay_session(
        self, gameplay_services, sample_character_data, sample_player_data
    ):
        """Test a complete end-to-end gameplay session."""
        # Initialize all services
        story_service = gameplay_services["story_initialization"]
        gameplay_services["world_selection"]
        narrative_service = gameplay_services["narrative_generation"]
        dynamic_story = gameplay_services["dynamic_story"]
        chat_manager = gameplay_services["chat_manager"]

        # Step 1: Initialize story session
        with patch.object(
            story_service, "_detect_character_completion", return_value=True
        ):
            story_session_id = await story_service.initialize_story_session(
                player_id=sample_player_data["player_id"],
                character_id=sample_character_data["character_id"],
                world_id="therapeutic_garden",
                therapeutic_goals=sample_character_data["therapeutic_goals"],
            )

        assert story_session_id is not None

        # Step 2: Generate opening narrative
        opening_narrative = await narrative_service.generate_opening_narrative(
            session_id=sample_player_data["session_id"],
            character_id=sample_character_data["character_id"],
            world_id="therapeutic_garden",
            therapeutic_goals=sample_character_data["therapeutic_goals"],
        )

        assert opening_narrative is not None

        # Step 3: Simulate player interactions
        player_messages = [
            "I look around the garden and take a deep breath.",
            "I want to find a quiet place to sit and reflect.",
            "This place makes me feel peaceful and calm.",
        ]

        for message in player_messages:
            response = await dynamic_story.process_player_message(
                session_id=sample_player_data["session_id"],
                player_id=sample_player_data["player_id"],
                message_text=message,
            )

            assert response is not None
            assert response.narrative_text is not None
            assert len(response.narrative_text) > 0

        # Step 4: Verify session state
        # This would check that all components maintained proper state
        # throughout the session

        # Verify metrics were updated
        chat_metrics = chat_manager.get_metrics()
        story_metrics = dynamic_story.get_metrics()

        assert chat_metrics["messages_processed"] >= len(player_messages)
        assert story_metrics["stories_generated"] >= len(player_messages)


class TestGameplayFlowErrorHandling:
    """Test error handling throughout the gameplay flow."""

    @pytest.mark.asyncio
    async def test_service_failure_recovery(
        self, gameplay_services, sample_player_data
    ):
        """Test recovery from service failures."""
        dynamic_story = gameplay_services["dynamic_story"]

        # Test with invalid session
        response = await dynamic_story.process_player_message(
            session_id="invalid_session",
            player_id=sample_player_data["player_id"],
            message_text="Test message",
        )

        assert response is None or not response.success

    @pytest.mark.asyncio
    async def test_concurrent_session_handling(
        self, gameplay_services, sample_player_data
    ):
        """Test handling of concurrent sessions."""
        world_state_manager = gameplay_services["world_state_manager"]

        # Create multiple concurrent instances
        instance_ids = []
        for i in range(3):
            instance_id = await world_state_manager.create_world_instance(
                world_id=f"test_world_{i}",
                player_id=sample_player_data["player_id"],
                character_id=f"char_{i}",
                session_id=f"session_{i}",
            )
            if instance_id:
                instance_ids.append(instance_id)

        # Verify all instances were created
        assert len(instance_ids) == 3

        # Verify each instance is isolated
        for instance_id in instance_ids:
            instance = await world_state_manager.get_world_instance(instance_id)
            assert instance is not None
            assert instance.state.value == "active"


@pytest.mark.performance
class TestGameplayFlowPerformance:
    """Test performance characteristics of the gameplay flow."""

    @pytest.mark.asyncio
    async def test_message_processing_performance(
        self, gameplay_services, sample_player_data
    ):
        """Test message processing performance under load."""
        dynamic_story = gameplay_services["dynamic_story"]

        # Process multiple messages concurrently
        messages = [f"Test message {i}" for i in range(10)]

        start_time = datetime.utcnow()

        tasks = [
            dynamic_story.process_player_message(
                session_id=sample_player_data["session_id"],
                player_id=sample_player_data["player_id"],
                message_text=message,
            )
            for message in messages
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Verify performance (should process 10 messages in under 30 seconds)
        assert processing_time < 30

        # Verify all responses were processed
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) >= 5  # At least 50% success rate
