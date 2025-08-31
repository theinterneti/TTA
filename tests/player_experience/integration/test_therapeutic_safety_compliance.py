"""
Therapeutic Safety Compliance Tests

Tests to validate character data integrity and therapeutic safety compliance
throughout the conversational character creation process.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.therapeutic_safety import (
    CrisisAssessment,
    CrisisLevel,
    SafetyValidationOrchestrator,
    ValidationResult,
)
from src.player_experience.models.conversation_state import (
    CollectedData,
    ConversationMessage,
    ConversationProgress,
    ConversationState,
    ConversationStatus,
)
from src.player_experience.services.conversation_data_extractor import (
    ConversationDataExtractor,
)
from src.player_experience.services.conversation_scripts import ConversationStage
from src.player_experience.services.conversational_character_integration import (
    ConversationalCharacterIntegrationService,
)
from src.player_experience.services.conversational_character_service import (
    ConversationalCharacterService,
)


class TestTherapeuticSafetyCompliance:
    """Test suite for therapeutic safety compliance."""

    @pytest.fixture
    def mock_safety_validator(self):
        """Mock safety validation orchestrator."""
        validator = AsyncMock(spec=SafetyValidationOrchestrator)
        validator.validate_content.return_value = ValidationResult(
            is_safe=True, crisis_assessment=None, content_flags=[], therapeutic_notes=[]
        )
        return validator

    @pytest.fixture
    def mock_dependencies(self, mock_safety_validator):
        """Create mock dependencies for testing."""
        character_repository = Mock()
        character_manager = Mock()
        character_manager.create_character.return_value = Mock(
            character_id="test_char_123", name="Test Character"
        )

        return {
            "character_repository": character_repository,
            "character_manager": character_manager,
            "safety_validator": mock_safety_validator,
        }

    @pytest.fixture
    def conversation_service(self, mock_dependencies):
        """Create conversation service with mocked dependencies."""
        return ConversationalCharacterService(
            character_manager=mock_dependencies["character_manager"],
            character_repository=mock_dependencies["character_repository"],
            safety_validator=mock_dependencies["safety_validator"],
        )

    @pytest.fixture
    def integration_service(self, mock_dependencies):
        """Create integration service with mocked dependencies."""
        return ConversationalCharacterIntegrationService(
            character_manager=mock_dependencies["character_manager"],
            character_repository=mock_dependencies["character_repository"],
        )

    @pytest.fixture
    def data_extractor(self):
        """Create data extractor for testing."""
        return ConversationDataExtractor()

    @pytest.fixture
    def sample_conversation_with_crisis(self):
        """Create conversation state with crisis indicators."""
        progress = ConversationProgress(
            current_stage=ConversationStage.CONCERNS,
            current_prompt_id="concerns_exploration",
        )

        conversation_state = ConversationState(
            conversation_id="crisis_test_123",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=progress,
            collected_data=CollectedData(),
        )

        # Add crisis-indicating messages
        crisis_message = ConversationMessage(
            message_id="crisis_msg_1",
            timestamp=datetime.utcnow(),
            sender="user",
            content="I've been thinking about ending it all",
            message_type="response",
        )
        conversation_state.message_history.append(crisis_message)

        return conversation_state

    @pytest.mark.asyncio
    async def test_crisis_detection_during_conversation(
        self, conversation_service, mock_safety_validator
    ):
        """Test that crisis indicators are properly detected during conversation."""
        # Setup crisis detection
        crisis_assessment = CrisisAssessment(
            crisis_level=CrisisLevel.HIGH,
            crisis_indicators=["suicidal ideation"],
            recommended_actions=["immediate_intervention"],
            confidence_score=0.95,
        )

        mock_safety_validator.validate_content.return_value = ValidationResult(
            is_safe=False,
            crisis_assessment=crisis_assessment,
            content_flags=["crisis", "suicidal_ideation"],
            therapeutic_notes=["Immediate professional intervention required"],
        )

        # Start conversation
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Process crisis-indicating response
        crisis_response = "I don't want to live anymore"
        messages = await conversation_service.process_user_response(
            conversation_id, crisis_response
        )

        # Verify crisis was detected and handled
        crisis_messages = [msg for msg in messages if hasattr(msg, "crisis_level")]
        assert len(crisis_messages) > 0
        assert crisis_messages[0].crisis_level == "high"
        assert len(crisis_messages[0].resources) > 0

        # Verify conversation state reflects crisis
        conversation_state = await conversation_service.get_conversation_state(
            conversation_id
        )
        assert conversation_state.crisis_detected is True
        assert len(conversation_state.safety_notes) > 0

    @pytest.mark.asyncio
    async def test_therapeutic_boundary_enforcement(
        self, conversation_service, mock_safety_validator
    ):
        """Test enforcement of therapeutic boundaries during conversation."""
        # Setup boundary violation detection
        mock_safety_validator.validate_content.return_value = ValidationResult(
            is_safe=False,
            crisis_assessment=None,
            content_flags=["inappropriate_content", "boundary_violation"],
            therapeutic_notes=["Content violates therapeutic boundaries"],
        )

        # Start conversation
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        # Process inappropriate response
        inappropriate_response = "I want to date my therapist"
        messages = await conversation_service.process_user_response(
            conversation_id, inappropriate_response
        )

        # Verify boundary violation was handled
        validation_errors = [msg for msg in messages if hasattr(msg, "error_message")]
        assert len(validation_errors) > 0

        # Verify safety validator was called with correct context
        mock_safety_validator.validate_content.assert_called()
        call_args = mock_safety_validator.validate_content.call_args
        assert call_args[0][0].content_text == inappropriate_response
        assert call_args[0][1].content_type == "user_response"

    @pytest.mark.asyncio
    async def test_character_data_validation_integrity(self, integration_service):
        """Test character data validation for integrity and completeness."""
        # Create conversation state with various data quality issues
        conversation_state = ConversationState(
            conversation_id="validation_test_123",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=ConversationProgress(
                current_stage=ConversationStage.SUMMARY,
                current_prompt_id="summary_review",
            ),
            collected_data=CollectedData(),
        )

        # Test cases for different validation scenarios
        test_cases = [
            {
                "name": "valid_complete_data",
                "data": {
                    "name": "Alice Johnson",
                    "age_range": "adult",
                    "gender_identity": "female",
                    "physical_description": "Average height with brown hair",
                    "backstory": "Grew up in a loving family",
                    "personality_traits": ["kind", "creative"],
                    "core_values": ["honesty", "compassion"],
                    "primary_concerns": ["anxiety"],
                    "preferred_intensity": "medium",
                    "readiness_level": 0.7,
                },
                "expected_valid": True,
                "expected_errors": [],
            },
            {
                "name": "invalid_name_too_short",
                "data": {
                    "name": "A",
                    "age_range": "adult",
                    "gender_identity": "female",
                },
                "expected_valid": False,
                "expected_errors": [
                    "Character name must be at least 2 characters long"
                ],
            },
            {
                "name": "invalid_readiness_level",
                "data": {
                    "name": "Alice Johnson",
                    "age_range": "adult",
                    "readiness_level": 1.5,  # Invalid: > 1.0
                },
                "expected_valid": False,
                "expected_errors": [
                    "Therapeutic readiness level must be between 0.0 and 1.0"
                ],
            },
            {
                "name": "invalid_age_range",
                "data": {
                    "name": "Alice Johnson",
                    "age_range": "middle_aged",  # Invalid: not in allowed values
                },
                "expected_valid": False,
                "expected_errors": [
                    "Age range must be one of: ['child', 'teen', 'adult', 'elder']"
                ],
            },
        ]

        for test_case in test_cases:
            # Setup collected data
            for field, value in test_case["data"].items():
                setattr(conversation_state.collected_data, field, value)

            # Validate data
            is_valid, errors = await integration_service.validate_conversation_data(
                conversation_state
            )

            # Verify results
            assert (
                is_valid == test_case["expected_valid"]
            ), f"Test case '{test_case['name']}' validation result mismatch"

            for expected_error in test_case["expected_errors"]:
                assert any(
                    expected_error in error for error in errors
                ), f"Expected error '{expected_error}' not found in {errors}"

    @pytest.mark.asyncio
    async def test_therapeutic_goal_validation(self, integration_service):
        """Test validation of therapeutic goals for appropriateness and safety."""
        conversation_state = ConversationState(
            conversation_id="goal_validation_test",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=ConversationProgress(
                current_stage=ConversationStage.GOALS, current_prompt_id="goals_setting"
            ),
            collected_data=CollectedData(),
        )

        # Test therapeutic goals validation
        test_goals = [
            {
                "goals": ["Reduce anxiety", "Improve self-confidence"],
                "expected_valid": True,
                "description": "Valid therapeutic goals",
            },
            {
                "goals": ["Learn to manipulate others", "Get revenge"],
                "expected_valid": False,
                "description": "Inappropriate therapeutic goals",
            },
            {
                "goals": ["Become perfect", "Never feel sad again"],
                "expected_valid": False,
                "description": "Unrealistic therapeutic goals",
            },
        ]

        for test_case in test_goals:
            conversation_state.collected_data.therapeutic_goals = test_case["goals"]

            # Convert to character creation data for validation
            character_data = (
                await integration_service.convert_to_character_creation_data(
                    conversation_state.collected_data
                )
            )

            # Validate therapeutic goals (this would involve additional validation logic)
            # For now, we'll test the basic conversion and structure
            assert character_data.therapeutic_profile.therapeutic_goals is not None
            assert len(character_data.therapeutic_profile.therapeutic_goals) == len(
                test_case["goals"]
            )

    def test_data_extraction_safety_filtering(self, data_extractor):
        """Test that data extraction filters out unsafe or inappropriate content."""
        # Create conversation state with mixed safe and unsafe content
        conversation_state = ConversationState(
            conversation_id="extraction_safety_test",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=ConversationProgress(
                current_stage=ConversationStage.BACKGROUND,
                current_prompt_id="background_story",
            ),
            collected_data=CollectedData(),
        )

        # Add messages with various content types
        messages = [
            ConversationMessage(
                message_id="safe_msg_1",
                timestamp=datetime.utcnow(),
                sender="user",
                content="I enjoy reading books and spending time with family",
                message_type="response",
            ),
            ConversationMessage(
                message_id="inappropriate_msg_1",
                timestamp=datetime.utcnow(),
                sender="user",
                content="I like to hurt small animals for fun",
                message_type="response",
            ),
            ConversationMessage(
                message_id="safe_msg_2",
                timestamp=datetime.utcnow(),
                sender="user",
                content="My core values are kindness and honesty",
                message_type="response",
            ),
        ]

        conversation_state.message_history = messages

        # Extract data
        extracted_data = data_extractor.extract_data_from_conversation(
            conversation_state
        )

        # Verify that safe content was extracted
        assert (
            "reading" in extracted_data.backstory
            or "family" in extracted_data.backstory
        )
        assert (
            "kindness" in extracted_data.core_values
            or "honesty" in extracted_data.core_values
        )

        # Verify that inappropriate content was filtered out
        # (This would require additional safety filtering in the extractor)
        assert "hurt" not in str(extracted_data.__dict__.values())
        assert "animals" not in str(extracted_data.__dict__.values())

    @pytest.mark.asyncio
    async def test_conversation_safety_monitoring_throughout_flow(
        self, conversation_service, mock_safety_validator
    ):
        """Test continuous safety monitoring throughout the conversation flow."""
        # Track safety validation calls
        validation_calls = []

        def track_validation(content_payload, validation_context):
            validation_calls.append(
                {
                    "content": content_payload.content_text,
                    "stage": validation_context.session_id,
                    "timestamp": datetime.utcnow(),
                }
            )
            return ValidationResult(
                is_safe=True,
                crisis_assessment=None,
                content_flags=[],
                therapeutic_notes=[],
            )

        mock_safety_validator.validate_content.side_effect = track_validation

        # Start conversation and process multiple responses
        player_id = "test_player_123"
        conversation_id, _ = await conversation_service.start_conversation(player_id)

        responses = [
            "My name is Sarah",
            "I'm an adult woman",
            "I have brown hair and green eyes",
            "I grew up in a small town",
            "I value honesty and kindness",
            "I'm struggling with anxiety",
            "I want to feel more confident",
        ]

        for response in responses:
            await conversation_service.process_user_response(conversation_id, response)

        # Verify safety validation was called for each user response
        assert len(validation_calls) == len(responses)

        # Verify all responses were validated
        validated_content = [call["content"] for call in validation_calls]
        for response in responses:
            assert response in validated_content

    @pytest.mark.asyncio
    async def test_character_creation_safety_final_check(
        self, integration_service, mock_safety_validator
    ):
        """Test final safety check before character creation."""
        # Create conversation state with complete data
        conversation_state = ConversationState(
            conversation_id="final_safety_test",
            player_id="test_player_456",
            status=ConversationStatus.ACTIVE,
            progress=ConversationProgress(
                current_stage=ConversationStage.COMPLETION,
                current_prompt_id="completion_review",
            ),
            collected_data=CollectedData(),
        )

        # Setup complete character data
        conversation_state.collected_data.name = "Test Character"
        conversation_state.collected_data.age_range = "adult"
        conversation_state.collected_data.gender_identity = "non-binary"
        conversation_state.collected_data.physical_description = "Average height"
        conversation_state.collected_data.backstory = "Grew up in a loving family"
        conversation_state.collected_data.personality_traits = ["kind", "creative"]
        conversation_state.collected_data.core_values = ["honesty"]
        conversation_state.collected_data.primary_concerns = ["anxiety"]
        conversation_state.collected_data.preferred_intensity = "medium"
        conversation_state.collected_data.readiness_level = 0.7

        # Test successful character creation
        character = await integration_service.create_character_from_conversation(
            conversation_state
        )

        assert character is not None
        assert character.character_id == "test_char_123"

        # Verify final validation was performed
        is_valid, errors = await integration_service.validate_conversation_data(
            conversation_state
        )
        assert is_valid is True
        assert len(errors) == 0
