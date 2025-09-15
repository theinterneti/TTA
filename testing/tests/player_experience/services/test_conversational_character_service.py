"""
Unit tests for ConversationalCharacterService

Tests the core conversational character creation logic, state management,
and integration with existing character systems.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.components.therapeutic_safety import (
    CrisisAssessment,
    CrisisLevel,
    ValidationResult,
)
from src.player_experience.models.conversation_state import (
    AssistantMessage,
    CollectedData,
    ConversationCompletedMessage,
    ConversationProgress,
    ConversationState,
    ConversationStatus,
    CrisisDetectedMessage,
    ErrorMessage,
    ProgressUpdateMessage,
)
from src.player_experience.services.conversation_scripts import ConversationStage
from src.player_experience.services.conversational_character_service import (
    ConversationalCharacterService,
)


class TestConversationalCharacterService:
    """Test suite for ConversationalCharacterService."""

    @pytest.fixture
    def mock_character_manager(self):
        """Mock character avatar manager."""
        manager = Mock()
        manager.create_character = Mock(
            return_value=Mock(
                character_id="test_char_123",
                name="Test Character",
                appearance=Mock(
                    age_range="adult",
                    gender_identity="non-binary",
                    physical_description="Test description",
                ),
                therapeutic_profile=Mock(
                    primary_concerns=["anxiety"],
                    preferred_intensity="medium",
                    readiness_level=0.7,
                ),
            )
        )
        return manager

    @pytest.fixture
    def mock_character_repository(self):
        """Mock character repository."""
        return Mock()

    @pytest.fixture
    def mock_safety_validator(self):
        """Mock safety validation orchestrator."""
        validator = AsyncMock()
        validator.validate_content = AsyncMock(
            return_value=ValidationResult(
                is_safe=True,
                crisis_assessment=None,
                content_flags=[],
                therapeutic_notes=[],
            )
        )
        return validator

    @pytest.fixture
    def service(
        self, mock_character_manager, mock_character_repository, mock_safety_validator
    ):
        """Create service instance with mocked dependencies."""
        return ConversationalCharacterService(
            character_manager=mock_character_manager,
            character_repository=mock_character_repository,
            safety_validator=mock_safety_validator,
        )

    @pytest.fixture
    def sample_conversation_state(self):
        """Create a sample conversation state for testing."""
        progress = ConversationProgress(
            current_stage=ConversationStage.WELCOME, current_prompt_id="welcome_intro"
        )

        return ConversationState(
            conversation_id="test_conv_123",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=progress,
            collected_data=CollectedData(),
        )

    @pytest.mark.asyncio
    async def test_start_conversation_success(self, service):
        """Test successful conversation start."""
        player_id = "test_player_123"
        metadata = {"source": "test"}

        conversation_id, assistant_message = await service.start_conversation(
            player_id, metadata
        )

        # Verify conversation ID is generated
        assert conversation_id is not None
        assert len(conversation_id) > 0

        # Verify assistant message
        assert isinstance(assistant_message, AssistantMessage)
        assert assistant_message.conversation_id == conversation_id
        assert assistant_message.stage == ConversationStage.WELCOME
        assert assistant_message.prompt_id == "welcome_intro"
        assert len(assistant_message.content) > 0

        # Verify conversation is stored
        assert conversation_id in service.active_conversations
        conversation_state = service.active_conversations[conversation_id]
        assert conversation_state.player_id == player_id
        assert conversation_state.status == ConversationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_process_user_response_normal(
        self, service, sample_conversation_state
    ):
        """Test processing normal user response."""
        # Setup
        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state
        user_response = "My name is Alice"

        # Execute
        messages = await service.process_user_response(conversation_id, user_response)

        # Verify
        assert len(messages) > 0
        assert any(isinstance(msg, ProgressUpdateMessage) for msg in messages)

        # Check that user message was added to history
        user_messages = [
            msg
            for msg in sample_conversation_state.message_history
            if msg.sender == "user"
        ]
        assert len(user_messages) == 1
        assert user_messages[0].content == user_response

        # Check that data was extracted
        assert sample_conversation_state.collected_data.name == "Alice"

    @pytest.mark.asyncio
    async def test_process_user_response_crisis_detected(
        self, service, sample_conversation_state, mock_safety_validator
    ):
        """Test processing user response with crisis detection."""
        # Setup crisis detection
        crisis_assessment = CrisisAssessment(
            crisis_level=CrisisLevel.HIGH,
            crisis_indicators=["suicidal ideation"],
            recommended_actions=["immediate_intervention"],
            confidence_score=0.9,
        )

        mock_safety_validator.validate_content.return_value = ValidationResult(
            is_safe=False,
            crisis_assessment=crisis_assessment,
            content_flags=["crisis"],
            therapeutic_notes=["Immediate attention required"],
        )

        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state
        user_response = "I want to hurt myself"

        # Execute
        messages = await service.process_user_response(conversation_id, user_response)

        # Verify crisis message is returned
        crisis_messages = [
            msg for msg in messages if isinstance(msg, CrisisDetectedMessage)
        ]
        assert len(crisis_messages) == 1
        assert crisis_messages[0].crisis_level == "high"
        assert len(crisis_messages[0].resources) > 0

        # Verify conversation state is updated
        assert sample_conversation_state.crisis_detected is True

    @pytest.mark.asyncio
    async def test_process_user_response_conversation_not_found(self, service):
        """Test processing response for non-existent conversation."""
        messages = await service.process_user_response(
            "nonexistent_id", "test response"
        )

        assert len(messages) == 1
        assert isinstance(messages[0], ErrorMessage)
        assert messages[0].error_code == "CONVERSATION_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_process_user_response_inactive_conversation(
        self, service, sample_conversation_state
    ):
        """Test processing response for inactive conversation."""
        # Setup inactive conversation
        sample_conversation_state.status = ConversationStatus.COMPLETED
        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state

        messages = await service.process_user_response(conversation_id, "test response")

        assert len(messages) == 1
        assert isinstance(messages[0], ErrorMessage)
        assert messages[0].error_code == "CONVERSATION_INACTIVE"

    @pytest.mark.asyncio
    async def test_pause_conversation_success(self, service, sample_conversation_state):
        """Test successful conversation pause."""
        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state

        result = await service.pause_conversation(conversation_id)

        assert result is True
        assert sample_conversation_state.status == ConversationStatus.PAUSED

    @pytest.mark.asyncio
    async def test_pause_conversation_not_found(self, service):
        """Test pausing non-existent conversation."""
        result = await service.pause_conversation("nonexistent_id")
        assert result is False

    @pytest.mark.asyncio
    async def test_resume_conversation_success(
        self, service, sample_conversation_state
    ):
        """Test successful conversation resume."""
        # Setup paused conversation
        sample_conversation_state.status = ConversationStatus.PAUSED
        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state

        assistant_message = await service.resume_conversation(conversation_id)

        assert assistant_message is not None
        assert isinstance(assistant_message, AssistantMessage)
        assert sample_conversation_state.status == ConversationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_complete_conversation_success(
        self, service, sample_conversation_state, mock_character_manager
    ):
        """Test successful conversation completion."""
        # Setup conversation with sufficient data
        sample_conversation_state.collected_data.name = "Test User"
        sample_conversation_state.collected_data.age_range = "adult"
        sample_conversation_state.collected_data.gender_identity = "non-binary"
        sample_conversation_state.collected_data.physical_description = (
            "Test description"
        )
        sample_conversation_state.collected_data.backstory = "Test backstory"
        sample_conversation_state.collected_data.personality_traits = [
            "kind",
            "creative",
        ]
        sample_conversation_state.collected_data.core_values = ["honesty", "compassion"]
        sample_conversation_state.collected_data.primary_concerns = ["anxiety"]
        sample_conversation_state.collected_data.preferred_intensity = "medium"
        sample_conversation_state.collected_data.readiness_level = 0.7

        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state

        completion_message = await service.complete_conversation(conversation_id)

        assert completion_message is not None
        assert isinstance(completion_message, ConversationCompletedMessage)
        assert sample_conversation_state.status == ConversationStatus.COMPLETED
        assert sample_conversation_state.completed_at is not None

        # Verify character was created
        mock_character_manager.create_character.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_conversation_insufficient_data(
        self, service, sample_conversation_state
    ):
        """Test conversation completion with insufficient data."""
        # Setup conversation with minimal data (below 70% threshold)
        sample_conversation_state.collected_data.name = "Test User"

        conversation_id = sample_conversation_state.conversation_id
        service.active_conversations[conversation_id] = sample_conversation_state

        completion_message = await service.complete_conversation(conversation_id)

        assert completion_message is None

    def test_extract_age_range(self, service):
        """Test age range extraction from responses."""
        test_cases = [
            ("I'm a child", "child"),
            ("I'm in my teenage years", "teen"),
            ("I'm an adult", "adult"),
            ("I'm elderly", "elder"),
            ("I'm 25 years old", None),  # No clear age range keyword
        ]

        for response, expected in test_cases:
            result = service._extract_age_range(response)
            assert result == expected

    def test_extract_list_items(self, service):
        """Test list item extraction from responses."""
        test_cases = [
            ("I am kind, creative, and thoughtful", ["kind", "creative", "thoughtful"]),
            (
                "I value honesty; integrity, and compassion",
                ["honesty", "integrity", "compassion"],
            ),
            ("My goal is to be happy", ["My goal is to be happy"]),
            ("", []),
        ]

        for response, expected in test_cases:
            result = service._extract_list_items(response)
            # Sort both lists for comparison since order may vary
            assert sorted(result) == sorted(expected)

    def test_extract_readiness_level(self, service):
        """Test readiness level extraction from responses."""
        test_cases = [
            ("I'm 80% ready", 0.8),
            ("I'm very ready", 0.9),
            ("I'm somewhat ready", 0.5),
            ("I'm not ready", 0.1),
            ("I'm 7 out of 10", 0.7),
            ("I don't know", None),
        ]

        for response, expected in test_cases:
            result = service._extract_readiness_level(response)
            if expected is not None:
                assert (
                    abs(result - expected) < 0.1
                )  # Allow small floating point differences
            else:
                assert result is None

    def test_calculate_completeness_score(self, service):
        """Test completeness score calculation."""
        # Test with minimal data
        minimal_data = CollectedData()
        minimal_data.name = "Test"
        score = service._calculate_completeness_score(minimal_data)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Should be low with minimal data

        # Test with complete data
        complete_data = CollectedData()
        complete_data.name = "Test User"
        complete_data.age_range = "adult"
        complete_data.gender_identity = "non-binary"
        complete_data.physical_description = "Test description"
        complete_data.backstory = "Test backstory"
        complete_data.personality_traits = ["kind"]
        complete_data.core_values = ["honesty"]
        complete_data.strengths_and_skills = ["creativity"]
        complete_data.life_goals = ["happiness"]
        complete_data.primary_concerns = ["anxiety"]
        complete_data.therapeutic_goals = ["reduce anxiety"]
        complete_data.preferred_intensity = "medium"
        complete_data.comfort_zones = ["talking"]
        complete_data.challenge_areas = ["public speaking"]
        complete_data.readiness_level = 0.7

        score = service._calculate_completeness_score(complete_data)
        assert score == 1.0  # Should be complete


@pytest.mark.redis
class TestConversationalCharacterServiceRedis:
    """Redis-specific tests for ConversationalCharacterService."""

    @pytest.fixture
    def redis_service(
        self, mock_character_manager, mock_character_repository, mock_safety_validator
    ):
        """Create service instance with Redis backend."""
        # This would be configured to use actual Redis for integration testing
        return ConversationalCharacterService(
            character_manager=mock_character_manager,
            character_repository=mock_character_repository,
            safety_validator=mock_safety_validator,
        )

    @pytest.mark.asyncio
    async def test_conversation_persistence_redis(self, redis_service):
        """Test conversation state persistence in Redis."""
        # This test would verify that conversation state is properly
        # persisted to and retrieved from Redis
        pass

    @pytest.mark.asyncio
    async def test_conversation_recovery_redis(self, redis_service):
        """Test conversation recovery from Redis after connection loss."""
        # This test would verify that conversations can be recovered
        # from Redis after a connection interruption
        pass
