"""
Conversational Character Creation Integration Service

This module provides integration between conversational character creation
and existing character storage and validation systems, ensuring data consistency
and proper validation throughout the conversational process.
"""

import logging
from typing import Any

from ..database.character_repository import CharacterRepository
from ..managers.character_avatar_manager import (
    CharacterAvatarManager,
    CharacterLimitExceededError,
)
from ..models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    IntensityLevel,
    TherapeuticApproach,
    TherapeuticGoal,
    TherapeuticProfile,
)
from ..models.conversation_state import CollectedData, ConversationState
from ..services.conversation_scripts import ConversationStage

logger = logging.getLogger(__name__)


class ConversationalCharacterIntegrationService:
    """Service for integrating conversational character creation with existing systems."""

    def __init__(
        self,
        character_manager: CharacterAvatarManager,
        character_repository: CharacterRepository,
    ):
        self.character_manager = character_manager
        self.character_repository = character_repository

        logger.info("ConversationalCharacterIntegrationService initialized")

    async def validate_conversation_data(
        self, conversation_state: ConversationState
    ) -> tuple[bool, list[str]]:
        """
        Validate collected conversation data against character creation requirements.

        Args:
            conversation_state: Current conversation state with collected data

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        collected_data = conversation_state.collected_data

        try:
            # Validate basic information
            if not collected_data.name or len(collected_data.name.strip()) < 2:
                errors.append("Character name must be at least 2 characters long")
            elif len(collected_data.name) > 50:
                errors.append("Character name cannot exceed 50 characters")
            else:
                # Validate name format
                import re

                if not re.match(r"^[a-zA-Z\s\-']+$", collected_data.name.strip()):
                    errors.append(
                        "Character name can only contain letters, spaces, hyphens, and apostrophes"
                    )

            # Validate age range
            valid_age_ranges = ["child", "teen", "adult", "elder"]
            if (
                collected_data.age_range
                and collected_data.age_range not in valid_age_ranges
            ):
                errors.append(f"Age range must be one of: {valid_age_ranges}")

            # Validate readiness level
            if collected_data.readiness_level is not None:
                if (
                    collected_data.readiness_level < 0.0
                    or collected_data.readiness_level > 1.0
                ):
                    errors.append(
                        "Therapeutic readiness level must be between 0.0 and 1.0"
                    )

            # Validate intensity level
            if collected_data.preferred_intensity:
                valid_intensities = ["low", "medium", "high"]
                if collected_data.preferred_intensity not in valid_intensities:
                    errors.append(
                        f"Preferred intensity must be one of: {valid_intensities}"
                    )

            # Check character limit for player
            existing_characters = self.character_manager.get_player_characters(
                conversation_state.player_id
            )
            if (
                len(existing_characters)
                >= self.character_manager.MAX_CHARACTERS_PER_PLAYER
            ):
                errors.append(
                    f"Player already has maximum number of characters ({self.character_manager.MAX_CHARACTERS_PER_PLAYER})"
                )

            return len(errors) == 0, errors

        except Exception as e:
            logger.error(f"Error validating conversation data: {e}")
            errors.append("Validation error occurred")
            return False, errors

    async def convert_to_character_creation_data(
        self, collected_data: CollectedData
    ) -> CharacterCreationData:
        """
        Convert collected conversation data to CharacterCreationData with proper validation.

        Args:
            collected_data: Data collected from conversation

        Returns:
            CharacterCreationData object

        Raises:
            ValueError: If data cannot be converted or is invalid
        """
        try:
            # Create appearance with defaults for missing data
            appearance = CharacterAppearance(
                age_range=collected_data.age_range or "adult",
                gender_identity=collected_data.gender_identity or "non-binary",
                physical_description=collected_data.physical_description or "",
                clothing_style=collected_data.clothing_style or "casual",
                distinctive_features=collected_data.distinctive_features or [],
            )

            # Create background with collected data
            background = CharacterBackground(
                name=collected_data.name or "",
                backstory=collected_data.backstory or "",
                personality_traits=collected_data.personality_traits or [],
                core_values=collected_data.core_values or [],
                fears_and_anxieties=collected_data.fears_and_anxieties or [],
                strengths_and_skills=collected_data.strengths_and_skills or [],
                life_goals=collected_data.life_goals or [],
                relationships=collected_data.relationships or {},
            )

            # Convert therapeutic goals from strings to TherapeuticGoal objects
            therapeutic_goals = []
            for i, goal_text in enumerate(collected_data.therapeutic_goals or []):
                therapeutic_goal = TherapeuticGoal(
                    goal_id=f"conv_goal_{i}",
                    description=goal_text,
                    target_outcome=goal_text,  # Use same text for now
                    priority=min(i + 1, 5),  # Priority 1-5
                    timeline_weeks=12,  # Default 12 weeks
                    success_metrics=[],
                )
                therapeutic_goals.append(therapeutic_goal)

            # Map intensity level
            intensity_mapping = {
                "gentle": IntensityLevel.LOW,
                "low": IntensityLevel.LOW,
                "balanced": IntensityLevel.MEDIUM,
                "medium": IntensityLevel.MEDIUM,
                "intensive": IntensityLevel.HIGH,
                "high": IntensityLevel.HIGH,
            }

            intensity_level = intensity_mapping.get(
                collected_data.preferred_intensity or "medium", IntensityLevel.MEDIUM
            )

            # Create therapeutic profile
            therapeutic_profile = TherapeuticProfile(
                primary_concerns=collected_data.primary_concerns or [],
                therapeutic_goals=therapeutic_goals,
                preferred_intensity=intensity_level,
                therapeutic_approaches=[
                    TherapeuticApproach.COGNITIVE_BEHAVIORAL
                ],  # Default approach
                comfort_zones=collected_data.comfort_zones or [],
                challenge_areas=collected_data.challenge_areas or [],
                readiness_level=collected_data.readiness_level or 0.5,
            )

            # Create and return character creation data
            character_data = CharacterCreationData(
                name=collected_data.name or "",
                appearance=appearance,
                background=background,
                therapeutic_profile=therapeutic_profile,
            )

            logger.info(
                "Successfully converted conversation data to CharacterCreationData"
            )
            return character_data

        except Exception as e:
            logger.error(f"Failed to convert conversation data: {e}")
            raise ValueError(f"Failed to convert conversation data: {str(e)}")

    async def create_character_from_conversation(
        self, conversation_state: ConversationState
    ) -> Character:
        """
        Create a character from conversation state using existing character creation systems.

        Args:
            conversation_state: Completed conversation state

        Returns:
            Created Character object

        Raises:
            ValueError: If conversation data is invalid
            CharacterLimitExceededError: If player has too many characters
        """
        try:
            # Validate conversation data first
            is_valid, errors = await self.validate_conversation_data(conversation_state)
            if not is_valid:
                raise ValueError(f"Invalid conversation data: {'; '.join(errors)}")

            # Convert to character creation data
            character_data = await self.convert_to_character_creation_data(
                conversation_state.collected_data
            )

            # Create character using existing character manager
            character = self.character_manager.create_character(
                conversation_state.player_id, character_data
            )

            logger.info(
                f"Successfully created character {character.character_id} from conversation {conversation_state.conversation_id}"
            )
            return character

        except CharacterLimitExceededError:
            logger.warning(
                f"Character limit exceeded for player {conversation_state.player_id}"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to create character from conversation: {e}")
            raise ValueError(f"Failed to create character: {str(e)}")

    async def get_character_preview(
        self, conversation_state: ConversationState
    ) -> dict[str, Any]:
        """
        Generate a character preview from current conversation state.

        Args:
            conversation_state: Current conversation state

        Returns:
            Dictionary containing character preview data
        """
        try:
            collected_data = conversation_state.collected_data

            # Calculate completeness score
            completeness_score = self._calculate_completeness_score(collected_data)

            # Identify missing required fields
            missing_fields = self._identify_missing_fields(collected_data)

            # Create preview data
            preview = {
                "conversation_id": conversation_state.conversation_id,
                "completeness_score": completeness_score,
                "ready_for_creation": completeness_score >= 0.7
                and len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "character_preview": {
                    "name": collected_data.name or "Unnamed Character",
                    "appearance": {
                        "age_range": collected_data.age_range or "adult",
                        "gender_identity": collected_data.gender_identity
                        or "non-binary",
                        "physical_description": collected_data.physical_description
                        or "No description provided",
                        "clothing_style": collected_data.clothing_style or "casual",
                        "distinctive_features": collected_data.distinctive_features
                        or [],
                    },
                    "background": {
                        "backstory": collected_data.backstory
                        or "No backstory provided",
                        "personality_traits": collected_data.personality_traits or [],
                        "core_values": collected_data.core_values or [],
                        "strengths_and_skills": collected_data.strengths_and_skills
                        or [],
                        "life_goals": collected_data.life_goals or [],
                    },
                    "therapeutic_profile": {
                        "primary_concerns": collected_data.primary_concerns or [],
                        "therapeutic_goals": collected_data.therapeutic_goals or [],
                        "preferred_intensity": collected_data.preferred_intensity
                        or "medium",
                        "comfort_zones": collected_data.comfort_zones or [],
                        "challenge_areas": collected_data.challenge_areas or [],
                        "readiness_level": collected_data.readiness_level or 0.5,
                    },
                },
            }

            return preview

        except Exception as e:
            logger.error(f"Failed to generate character preview: {e}")
            return {
                "conversation_id": conversation_state.conversation_id,
                "completeness_score": 0.0,
                "ready_for_creation": False,
                "missing_fields": ["error_generating_preview"],
                "character_preview": {},
            }

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

    def _identify_missing_fields(self, collected_data: CollectedData) -> list[str]:
        """Identify missing required fields."""
        missing = []

        # Required fields for character creation
        required_fields = {
            "name": collected_data.name,
            "age_range": collected_data.age_range,
            "gender_identity": collected_data.gender_identity,
            "physical_description": collected_data.physical_description,
            "backstory": collected_data.backstory,
            "personality_traits": collected_data.personality_traits,
            "core_values": collected_data.core_values,
            "primary_concerns": collected_data.primary_concerns,
            "preferred_intensity": collected_data.preferred_intensity,
            "readiness_level": collected_data.readiness_level,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                missing.append(field_name)

        return missing

    async def get_conversation_stage_requirements(
        self, stage: ConversationStage
    ) -> dict[str, Any]:
        """
        Get data requirements for a specific conversation stage.

        Args:
            stage: Conversation stage

        Returns:
            Dictionary containing stage requirements
        """
        stage_requirements = {
            ConversationStage.WELCOME: {
                "required_fields": ["name"],
                "optional_fields": [],
                "validation_rules": ["name_format", "name_length"],
            },
            ConversationStage.IDENTITY: {
                "required_fields": ["age_range", "gender_identity"],
                "optional_fields": [],
                "validation_rules": ["age_range_valid"],
            },
            ConversationStage.APPEARANCE: {
                "required_fields": ["physical_description"],
                "optional_fields": ["clothing_style", "distinctive_features"],
                "validation_rules": ["non_empty"],
            },
            ConversationStage.BACKGROUND: {
                "required_fields": ["backstory", "personality_traits"],
                "optional_fields": ["relationships"],
                "validation_rules": ["non_empty", "list_format"],
            },
            ConversationStage.VALUES: {
                "required_fields": ["core_values", "strengths_and_skills"],
                "optional_fields": ["life_goals"],
                "validation_rules": ["list_format"],
            },
            ConversationStage.CONCERNS: {
                "required_fields": ["primary_concerns"],
                "optional_fields": [],
                "validation_rules": ["list_format", "crisis_check"],
            },
            ConversationStage.GOALS: {
                "required_fields": ["therapeutic_goals"],
                "optional_fields": [],
                "validation_rules": ["list_format"],
            },
            ConversationStage.PREFERENCES: {
                "required_fields": ["preferred_intensity", "comfort_zones"],
                "optional_fields": ["challenge_areas"],
                "validation_rules": ["intensity_valid", "list_format"],
            },
            ConversationStage.READINESS: {
                "required_fields": ["readiness_level"],
                "optional_fields": [],
                "validation_rules": ["readiness_scale"],
            },
        }

        return stage_requirements.get(
            stage,
            {"required_fields": [], "optional_fields": [], "validation_rules": []},
        )
