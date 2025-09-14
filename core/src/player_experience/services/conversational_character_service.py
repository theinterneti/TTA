"""
Conversational Character Creation Service

This service manages the conversational character creation process, including
state management, conversation flow, and integration with existing character systems.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from src.components.therapeutic_safety import (
    ContentPayload,
    SafetyValidationOrchestrator,
    ValidationContext,
)

from ..database.character_repository import CharacterRepository
from ..managers.character_avatar_manager import CharacterAvatarManager
from ..models.conversation_state import (
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
from ..services.conversation_scripts import (
    ConversationScriptManager,
    ConversationStage,
)

logger = logging.getLogger(__name__)


class ConversationalCharacterService:
    """Service for managing conversational character creation."""

    def __init__(
        self,
        character_manager: CharacterAvatarManager,
        character_repository: CharacterRepository,
        safety_validator: SafetyValidationOrchestrator,
    ):
        self.character_manager = character_manager
        self.character_repository = character_repository
        self.safety_validator = safety_validator
        self.script_manager = ConversationScriptManager()

        # In-memory conversation state storage (would be Redis in production)
        self.active_conversations: dict[str, ConversationState] = {}

        logger.info("ConversationalCharacterService initialized")

    async def start_conversation(
        self, player_id: str, metadata: dict[str, Any] | None = None
    ) -> tuple[str, AssistantMessage]:
        """Start a new character creation conversation."""
        try:
            # Generate conversation ID
            conversation_id = str(uuid.uuid4())

            # Initialize conversation state
            progress = ConversationProgress(
                current_stage=ConversationStage.WELCOME,
                current_prompt_id="welcome_intro",
            )

            conversation_state = ConversationState(
                conversation_id=conversation_id,
                player_id=player_id,
                status=ConversationStatus.ACTIVE,
                progress=progress,
                collected_data=CollectedData(),
            )

            # Store conversation state
            self.active_conversations[conversation_id] = conversation_state

            # Get initial prompt
            initial_prompt = self.script_manager.scripts.prompts["welcome_intro"]

            # Create assistant message
            assistant_message = AssistantMessage(
                conversation_id=conversation_id,
                content=initial_prompt.primary_text,
                prompt_id=initial_prompt.prompt_id,
                stage=initial_prompt.stage,
                context_text=initial_prompt.context_text,
                follow_up_prompts=initial_prompt.follow_up_prompts,
            )

            # Add message to history
            conversation_state.add_message(
                "assistant", initial_prompt.primary_text, "prompt"
            )

            logger.info(
                f"Started conversation {conversation_id} for player {player_id}"
            )
            return conversation_id, assistant_message

        except Exception as e:
            logger.error(f"Failed to start conversation for player {player_id}: {e}")
            raise

    async def process_user_response(
        self, conversation_id: str, user_response: str
    ) -> list[Any]:
        """Process user response and return appropriate messages."""
        try:
            # Get conversation state
            conversation_state = self.active_conversations.get(conversation_id)
            if not conversation_state:
                return [
                    ErrorMessage(
                        conversation_id=conversation_id,
                        error_code="CONVERSATION_NOT_FOUND",
                        error_message="Conversation not found or expired",
                    )
                ]

            # Check if conversation is active
            if conversation_state.status != ConversationStatus.ACTIVE:
                return [
                    ErrorMessage(
                        conversation_id=conversation_id,
                        error_code="CONVERSATION_INACTIVE",
                        error_message=f"Conversation is {conversation_state.status.value}",
                    )
                ]

            # Add user message to history
            conversation_state.add_message("user", user_response, "response")

            # Validate response for safety
            safety_result = await self._validate_response_safety(
                user_response, conversation_state
            )
            if safety_result:
                return [safety_result]

            # Process response and extract data
            await self._extract_data_from_response(user_response, conversation_state)

            # Determine next step in conversation
            messages = await self._determine_next_step(
                conversation_state, user_response
            )

            return messages

        except Exception as e:
            logger.error(
                f"Failed to process user response for conversation {conversation_id}: {e}"
            )
            return [
                ErrorMessage(
                    conversation_id=conversation_id,
                    error_code="PROCESSING_ERROR",
                    error_message="Failed to process response",
                )
            ]

    async def get_conversation_state(
        self, conversation_id: str
    ) -> ConversationState | None:
        """Get current conversation state."""
        return self.active_conversations.get(conversation_id)

    async def pause_conversation(self, conversation_id: str) -> bool:
        """Pause a conversation."""
        conversation_state = self.active_conversations.get(conversation_id)
        if (
            conversation_state
            and conversation_state.status == ConversationStatus.ACTIVE
        ):
            conversation_state.status = ConversationStatus.PAUSED
            conversation_state.update_activity()
            logger.info(f"Paused conversation {conversation_id}")
            return True
        return False

    async def resume_conversation(
        self, conversation_id: str
    ) -> AssistantMessage | None:
        """Resume a paused conversation."""
        conversation_state = self.active_conversations.get(conversation_id)
        if (
            conversation_state
            and conversation_state.status == ConversationStatus.PAUSED
        ):
            conversation_state.status = ConversationStatus.ACTIVE
            conversation_state.update_activity()

            # Get current prompt
            current_prompt = self.script_manager.scripts.prompts.get(
                conversation_state.progress.current_prompt_id
            )

            if current_prompt:
                return AssistantMessage(
                    conversation_id=conversation_id,
                    content=f"Welcome back! Let's continue where we left off. {current_prompt.primary_text}",
                    prompt_id=current_prompt.prompt_id,
                    stage=current_prompt.stage,
                    context_text=current_prompt.context_text,
                )

        return None

    async def complete_conversation(
        self, conversation_id: str
    ) -> ConversationCompletedMessage | None:
        """Complete a conversation and create character."""
        try:
            conversation_state = self.active_conversations.get(conversation_id)
            if not conversation_state:
                return None

            # Convert collected data to character creation data
            character_data = (
                conversation_state.collected_data.to_character_creation_data()
            )

            # Validate character data completeness
            completeness_score = self._calculate_completeness_score(
                conversation_state.collected_data
            )
            if completeness_score < 0.7:  # Require 70% completeness
                return None

            # Create character using existing character manager
            character = self.character_manager.create_character(
                conversation_state.player_id, character_data
            )

            # Update conversation state
            conversation_state.status = ConversationStatus.COMPLETED
            conversation_state.completed_at = datetime.utcnow()
            conversation_state.update_activity()

            # Create completion message
            completion_message = ConversationCompletedMessage(
                conversation_id=conversation_id,
                character_preview={
                    "character_id": character.character_id,
                    "name": character.name,
                    "appearance": {
                        "age_range": character.appearance.age_range,
                        "gender_identity": character.appearance.gender_identity,
                        "physical_description": character.appearance.physical_description,
                    },
                    "therapeutic_profile": {
                        "primary_concerns": character.therapeutic_profile.primary_concerns,
                        "preferred_intensity": character.therapeutic_profile.preferred_intensity.value,
                        "readiness_level": character.therapeutic_profile.readiness_level,
                    },
                },
            )

            logger.info(
                f"Completed conversation {conversation_id}, created character {character.character_id}"
            )
            return completion_message

        except Exception as e:
            logger.error(f"Failed to complete conversation {conversation_id}: {e}")
            return None

    async def _validate_response_safety(
        self, response: str, conversation_state: ConversationState
    ) -> CrisisDetectedMessage | None:
        """Validate response for safety concerns."""
        try:
            # Create validation context
            validation_context = ValidationContext(
                user_id=conversation_state.player_id,
                session_id=conversation_state.conversation_id,
                content_type="user_response",
            )

            # Create content payload
            content_payload = ContentPayload(
                content_text=response, content_type="text", source="user_input"
            )

            # Validate with safety orchestrator
            validation_result = await self.safety_validator.validate_content(
                content_payload, validation_context
            )

            # Check for crisis indicators
            if (
                validation_result.crisis_assessment
                and validation_result.crisis_assessment.crisis_level.value
                in ["high", "emergency"]
            ):
                conversation_state.crisis_detected = True
                conversation_state.safety_notes.append(
                    f"Crisis detected: {validation_result.crisis_assessment.crisis_indicators}"
                )

                return CrisisDetectedMessage(
                    conversation_id=conversation_state.conversation_id,
                    crisis_level=validation_result.crisis_assessment.crisis_level.value,
                    support_message="I hear that you're going through something really difficult right now. Your safety is important.",
                    resources=[
                        {
                            "name": "National Suicide Prevention Lifeline",
                            "contact": "988",
                        },
                        {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                    ],
                )

            return None

        except Exception as e:
            logger.error(
                f"Safety validation failed for conversation {conversation_state.conversation_id}: {e}"
            )
            return None

    async def _extract_data_from_response(
        self, response: str, conversation_state: ConversationState
    ) -> None:
        """Extract and store data from user response."""
        current_prompt_id = conversation_state.progress.current_prompt_id
        current_prompt = self.script_manager.scripts.prompts.get(current_prompt_id)

        if not current_prompt:
            return

        # Extract data based on current prompt's data fields
        for field in current_prompt.data_fields:
            if field == "name" and not conversation_state.collected_data.name:
                conversation_state.collected_data.name = response.strip()
            elif field == "age_range":
                age_range = self._extract_age_range(response)
                if age_range:
                    conversation_state.collected_data.age_range = age_range
            elif field == "gender_identity":
                conversation_state.collected_data.gender_identity = response.strip()
            elif field == "physical_description":
                conversation_state.collected_data.physical_description = (
                    response.strip()
                )
            elif field == "backstory":
                conversation_state.collected_data.backstory = response.strip()
            elif field == "personality_traits":
                traits = self._extract_list_items(response)
                conversation_state.collected_data.personality_traits.extend(traits)
            elif field == "primary_concerns":
                concerns = self._extract_list_items(response)
                conversation_state.collected_data.primary_concerns.extend(concerns)
            elif field == "readiness_level":
                readiness = self._extract_readiness_level(response)
                if readiness is not None:
                    conversation_state.collected_data.readiness_level = readiness

    async def _determine_next_step(
        self, conversation_state: ConversationState, user_response: str
    ) -> list[Any]:
        """Determine next step in conversation flow."""
        messages = []

        # Get therapeutic response if available
        therapeutic_response = self.script_manager.get_therapeutic_response(
            conversation_state.progress.current_prompt_id, user_response
        )

        if therapeutic_response:
            # Format therapeutic response with collected data
            formatted_response = therapeutic_response.format(
                name=conversation_state.collected_data.name or "there"
            )
            conversation_state.add_message(
                "assistant", formatted_response, "therapeutic_response"
            )

        # Get next prompt
        next_prompt_id = self.script_manager.get_next_prompt(
            conversation_state.progress.current_prompt_id, user_response
        )

        if next_prompt_id:
            next_prompt = self.script_manager.scripts.prompts.get(next_prompt_id)
            if next_prompt:
                # Update progress
                conversation_state.progress.current_prompt_id = next_prompt_id
                conversation_state.progress.current_stage = next_prompt.stage

                # Format prompt with collected data
                formatted_prompt = next_prompt.primary_text.format(
                    name=conversation_state.collected_data.name or "there"
                )

                # Create assistant message
                assistant_message = AssistantMessage(
                    conversation_id=conversation_state.conversation_id,
                    content=formatted_prompt,
                    prompt_id=next_prompt.prompt_id,
                    stage=next_prompt.stage,
                    context_text=next_prompt.context_text,
                    follow_up_prompts=next_prompt.follow_up_prompts,
                )

                messages.append(assistant_message)
                conversation_state.add_message("assistant", formatted_prompt, "prompt")

        # Add progress update
        progress_message = ProgressUpdateMessage(
            conversation_id=conversation_state.conversation_id,
            progress={
                "current_stage": conversation_state.progress.current_stage.value,
                "progress_percentage": conversation_state.progress.progress_percentage,
                "completed_stages": [
                    stage.value
                    for stage in conversation_state.progress.completed_stages
                ],
            },
        )
        messages.append(progress_message)

        # Check if conversation is complete
        if conversation_state.progress.current_stage == ConversationStage.COMPLETION:
            completion_message = await self.complete_conversation(
                conversation_state.conversation_id
            )
            if completion_message:
                messages.append(completion_message)

        return messages

    def _extract_age_range(self, response: str) -> str | None:
        """Extract age range from response."""
        response_lower = response.lower()
        if any(word in response_lower for word in ["child", "kid", "young"]):
            return "child"
        elif any(word in response_lower for word in ["teen", "teenager", "adolescent"]):
            return "teen"
        elif any(word in response_lower for word in ["adult", "grown"]):
            return "adult"
        elif any(word in response_lower for word in ["elder", "senior", "older"]):
            return "elder"
        return None

    def _extract_list_items(self, response: str) -> list[str]:
        """Extract list items from response."""
        # Simple extraction - split by common delimiters
        import re

        items = re.split(r"[,;]\s*|\sand\s+|\sor\s+", response)
        return [item.strip() for item in items if item.strip()]

    def _extract_readiness_level(self, response: str) -> float | None:
        """Extract readiness level from response."""
        # Look for numbers or descriptive terms
        import re

        # Look for percentages or numbers
        numbers = re.findall(r"\d+", response)
        if numbers:
            num = int(numbers[0])
            if num <= 10:  # Scale of 1-10
                return num / 10.0
            elif num <= 100:  # Percentage
                return num / 100.0

        # Look for descriptive terms
        response_lower = response.lower()
        if any(
            word in response_lower
            for word in ["very ready", "completely ready", "fully ready"]
        ):
            return 0.9
        elif any(word in response_lower for word in ["ready", "prepared"]):
            return 0.7
        elif any(
            word in response_lower for word in ["somewhat", "partially", "kind of"]
        ):
            return 0.5
        elif any(word in response_lower for word in ["not very", "barely", "slightly"]):
            return 0.3
        elif any(word in response_lower for word in ["not ready", "unprepared"]):
            return 0.1

        return None

    def _calculate_completeness_score(self, collected_data: CollectedData) -> float:
        """Calculate completeness score for collected data."""
        total_fields = 15  # Total number of important fields
        completed_fields = 0

        # Check required fields
        if collected_data.name:
            completed_fields += 1
        if collected_data.age_range:
            completed_fields += 1
        if collected_data.gender_identity:
            completed_fields += 1
        if collected_data.physical_description:
            completed_fields += 1
        if collected_data.backstory:
            completed_fields += 1
        if collected_data.personality_traits:
            completed_fields += 1
        if collected_data.core_values:
            completed_fields += 1
        if collected_data.strengths_and_skills:
            completed_fields += 1
        if collected_data.life_goals:
            completed_fields += 1
        if collected_data.primary_concerns:
            completed_fields += 1
        if collected_data.therapeutic_goals:
            completed_fields += 1
        if collected_data.preferred_intensity:
            completed_fields += 1
        if collected_data.comfort_zones:
            completed_fields += 1
        if collected_data.challenge_areas:
            completed_fields += 1
        if collected_data.readiness_level is not None:
            completed_fields += 1

        return completed_fields / total_fields
