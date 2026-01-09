"""

# Logseq: [[TTA.dev/Player_experience/Managers/Character_avatar_manager]]
Character creation, customization, and lifecycle management.

This module provides the CharacterAvatarManager service that handles character CRUD operations,
enforces character limits, and integrates with the existing CharacterDevelopmentSystem for
therapeutic profiles.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..database.character_repository import CharacterRepository
from ..models.character import (
    Character,
    CharacterCreationData,
    CharacterUpdates,
    TherapeuticProfile,
)
from ..models.enums import IntensityLevel
from .therapeutic_profile_integration import TherapeuticProfileIntegrationService


# Mock implementations for TTA components (will be replaced with actual imports when available)
class CharacterDevelopmentSystem:
    """Mock CharacterDevelopmentSystem for testing."""

    def __init__(self):
        pass

    def initialize_character(self, character_id: str, **kwargs):
        logger.info(f"Mock: Initialized character {character_id} in development system")
        return {"character_id": character_id, "initialized": True}


class PersonalizationEngine:
    """Mock PersonalizationEngine for testing."""

    def __init__(self):
        pass

    def create_personalization_profile(self, character_id: str, **kwargs):
        logger.info(
            f"Mock: Created personalization profile for character {character_id}"
        )
        return {"character_id": character_id, "profile_created": True}

    def update_personalization_profile(self, character_id: str, **kwargs):
        logger.info(
            f"Mock: Updated personalization profile for character {character_id}"
        )
        return {"character_id": character_id, "profile_updated": True}


logger = logging.getLogger(__name__)


class CharacterLimitExceededError(Exception):
    """Raised when player tries to create more than the allowed number of characters."""

    pass


class CharacterNotFoundError(Exception):
    """Raised when a requested character is not found."""

    pass


class CharacterAvatarManager:
    """Manages character creation, customization, and lifecycle."""

    MAX_CHARACTERS_PER_PLAYER = 5

    def __init__(self, character_repository: CharacterRepository | None = None):
        """Initialize the Character Avatar Manager."""
        self.character_repository = character_repository or CharacterRepository()
        self.character_development_system = CharacterDevelopmentSystem()
        self.personalization_engine = PersonalizationEngine()
        self.therapeutic_integration_service = TherapeuticProfileIntegrationService()
        logger.info("CharacterAvatarManager initialized")

    def create_character(
        self, player_id: str, character_data: CharacterCreationData
    ) -> Character:
        """
        Create a new character for a player.

        Args:
            player_id: The ID of the player creating the character
            character_data: The character creation data

        Returns:
            The created Character object

        Raises:
            CharacterLimitExceededError: If player already has maximum characters
            ValueError: If character data is invalid
        """
        # Check character limit
        existing_characters = self.get_player_characters(player_id)
        if len(existing_characters) >= self.MAX_CHARACTERS_PER_PLAYER:
            raise CharacterLimitExceededError(
                f"Player {player_id} already has {len(existing_characters)} characters. "
                f"Maximum allowed is {self.MAX_CHARACTERS_PER_PLAYER}."
            )

        # Validate character data
        self._validate_character_creation_data(character_data)

        # Generate unique character ID
        character_id = str(uuid.uuid4())

        # Create character object with enhanced therapeutic profile
        character = Character(
            character_id=character_id,
            player_id=player_id,
            name=character_data.name,
            appearance=character_data.appearance,
            background=character_data.background,
            therapeutic_profile=character_data.therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        # Enhance therapeutic profile based on character data
        enhanced_profile = self.therapeutic_integration_service.create_therapeutic_profile_from_character(
            character
        )
        character.therapeutic_profile = enhanced_profile

        # Initialize character in the development system
        try:
            self.character_development_system.initialize_character(
                character_id,
                personality_traits=self._extract_personality_traits(character_data),
                therapeutic_goals=character_data.therapeutic_profile.therapeutic_goals,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize character in development system: {e}")

        # Create personalization profile and context
        try:
            self.personalization_engine.create_personalization_profile(
                character_id,
                therapeutic_preferences=enhanced_profile,
                background_info=character_data.background,
            )

            # Create personalization context for therapeutic integration
            self.therapeutic_integration_service.create_personalization_context(
                character
            )

            # Generate personalization recommendations
            self.therapeutic_integration_service.generate_personalization_recommendations(
                character
            )

        except Exception as e:
            logger.warning(f"Failed to create personalization profile and context: {e}")

        # Save character to repository
        saved_character = self.character_repository.create_character(character)

        logger.info(f"Created character {character_id} for player {player_id}")
        return saved_character

    def get_character(self, character_id: str) -> Character | None:
        """
        Get a character by ID.

        Args:
            character_id: The character ID

        Returns:
            The Character object if found, None otherwise
        """
        return self.character_repository.get_character(character_id)

    def get_player_characters(self, player_id: str) -> list[Character]:
        """
        Get all characters for a player.

        Args:
            player_id: The player ID

        Returns:
            List of Character objects
        """
        return self.character_repository.get_characters_by_player(player_id)

    def update_character(
        self, character_id: str, updates: CharacterUpdates
    ) -> Character:
        """
        Update an existing character.

        Args:
            character_id: The character ID
            updates: The character updates

        Returns:
            The updated Character object

        Raises:
            CharacterNotFoundError: If character is not found
            ValueError: If update data is invalid
        """
        # Get existing character
        character = self.character_repository.get_character(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Apply updates
        if updates.appearance:
            character.appearance = updates.appearance

        if updates.background:
            # Validate name consistency
            if updates.background.name != character.name:
                character.name = updates.background.name
            character.background = updates.background

        if updates.therapeutic_profile:
            character.therapeutic_profile = updates.therapeutic_profile

            # Update personalization profile
            try:
                self.personalization_engine.update_personalization_profile(
                    character_id, therapeutic_preferences=updates.therapeutic_profile
                )
            except Exception as e:
                logger.warning(f"Failed to update personalization profile: {e}")

        # Update last active timestamp
        character.last_active = datetime.now()

        # Save updated character
        updated_character = self.character_repository.update_character(character)

        logger.info(f"Updated character {character_id}")
        return updated_character

    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character.

        Args:
            character_id: The character ID

        Returns:
            True if character was deleted, False if not found
        """
        character = self.character_repository.get_character(character_id)
        if not character:
            return False

        # Mark character as inactive instead of hard delete for data integrity
        character.is_active = False
        character.last_active = datetime.now()

        self.character_repository.update_character(character)

        logger.info(f"Deleted character {character_id}")
        return True

    def get_character_therapeutic_profile(
        self, character_id: str
    ) -> TherapeuticProfile | None:
        """
        Get the therapeutic profile for a character.

        Args:
            character_id: The character ID

        Returns:
            The TherapeuticProfile if character exists, None otherwise
        """
        character = self.character_repository.get_character(character_id)
        if not character:
            return None

        return character.therapeutic_profile

    def update_character_therapeutic_profile(
        self, character_id: str, therapeutic_profile: TherapeuticProfile
    ) -> bool:
        """
        Update a character's therapeutic profile.

        Args:
            character_id: The character ID
            therapeutic_profile: The new therapeutic profile

        Returns:
            True if updated successfully, False if character not found
        """
        character = self.character_repository.get_character(character_id)
        if not character:
            return False

        character.therapeutic_profile = therapeutic_profile
        character.last_active = datetime.now()

        # Update personalization profile
        try:
            self.personalization_engine.update_personalization_profile(
                character_id, therapeutic_preferences=therapeutic_profile
            )
        except Exception as e:
            logger.warning(f"Failed to update personalization profile: {e}")

        self.character_repository.update_character(character)

        logger.info(f"Updated therapeutic profile for character {character_id}")
        return True

    def get_character_statistics(self, character_id: str) -> dict[str, Any] | None:
        """
        Get statistics for a character.

        Args:
            character_id: The character ID

        Returns:
            Dictionary with character statistics, None if character not found
        """
        character = self.character_repository.get_character(character_id)
        if not character:
            return None

        return {
            "character_id": character_id,
            "name": character.name,
            "created_at": character.created_at,
            "last_active": character.last_active,
            "total_session_time": character.total_session_time,
            "session_count": character.session_count,
            "active_worlds": len(character.active_worlds),
            "therapeutic_readiness": character.get_therapeutic_readiness(),
            "active_therapeutic_goals": len(
                character.therapeutic_profile.get_active_goals()
            ),
            "is_active": character.is_active,
        }

    def _validate_character_creation_data(
        self, character_data: CharacterCreationData
    ) -> None:
        """
        Validate character creation data.

        Args:
            character_data: The character creation data to validate

        Raises:
            ValueError: If data is invalid
        """
        if not character_data.name or len(character_data.name.strip()) < 2:
            raise ValueError("Character name must be at least 2 characters long")

        if len(character_data.name) > 50:
            raise ValueError("Character name cannot exceed 50 characters")

        # Background name is validated by CharacterBackground. No need to enforce equality to display name here.

        # Validate therapeutic profile
        if (
            character_data.therapeutic_profile.readiness_level < 0.0
            or character_data.therapeutic_profile.readiness_level > 1.0
        ):
            raise ValueError("Therapeutic readiness level must be between 0.0 and 1.0")

    def _extract_personality_traits(
        self, character_data: CharacterCreationData
    ) -> dict[str, float]:
        """
        Extract personality traits from character data for the development system.

        Args:
            character_data: The character creation data

        Returns:
            Dictionary of personality traits
        """
        # Map character background traits to personality system traits
        traits = {}

        # Extract from personality traits
        for trait in character_data.background.personality_traits:
            trait_lower = trait.lower()
            if "empathetic" in trait_lower or "caring" in trait_lower:
                traits["empathy"] = 0.7
            elif "patient" in trait_lower:
                traits["patience"] = 0.7
            elif "organized" in trait_lower:
                traits["conscientiousness"] = 0.6
            elif "outgoing" in trait_lower or "social" in trait_lower:
                traits["extraversion"] = 0.6
            elif "anxious" in trait_lower or "worried" in trait_lower:
                traits["neuroticism"] = 0.5
            elif "supportive" in trait_lower or "helpful" in trait_lower:
                traits["supportiveness"] = 0.7

        # Extract from therapeutic profile
        if (
            character_data.therapeutic_profile.preferred_intensity
            == IntensityLevel.HIGH
        ):
            traits["openness"] = traits.get("openness", 0.0) + 0.3
        elif (
            character_data.therapeutic_profile.preferred_intensity == IntensityLevel.LOW
        ):
            traits["neuroticism"] = traits.get("neuroticism", 0.0) + 0.2

        # Ensure all values are in valid range
        for trait_name in traits:
            traits[trait_name] = max(-1.0, min(1.0, traits[trait_name]))

        return traits

    def get_character_personalization_recommendations(
        self, character_id: str
    ) -> list[dict[str, Any]]:
        """
        Get personalization recommendations for a character.

        Args:
            character_id: The character ID

        Returns:
            List of personalization recommendations
        """
        recommendations = (
            self.therapeutic_integration_service.get_character_recommendations(
                character_id
            )
        )

        # Convert to dictionaries for easier API consumption
        return [
            {
                "recommendation_id": rec.recommendation_id,
                "type": rec.recommendation_type,
                "title": rec.title,
                "description": rec.description,
                "rationale": rec.rationale,
                "priority": rec.priority,
                "confidence_score": rec.confidence_score,
                "created_at": rec.created_at,
            }
            for rec in recommendations
        ]

    def adapt_therapeutic_content_for_character(
        self, character_id: str, content: str, content_type: str = "general"
    ) -> dict[str, Any] | None:
        """
        Adapt therapeutic content for a specific character.

        Args:
            character_id: The character ID
            content: The content to adapt
            content_type: Type of content

        Returns:
            Dictionary with adaptation details, None if character not found
        """
        character = self.character_repository.get_character(character_id)
        if not character:
            return None

        adaptation = self.therapeutic_integration_service.adapt_therapeutic_content(
            character, content, content_type
        )

        return {
            "adaptation_id": adaptation.adaptation_id,
            "original_content": adaptation.original_content,
            "adapted_content": adaptation.adapted_content,
            "adaptation_type": adaptation.adaptation_type,
            "reasoning": adaptation.reasoning,
            "effectiveness_score": adaptation.effectiveness_score,
            "created_at": adaptation.created_at,
        }
