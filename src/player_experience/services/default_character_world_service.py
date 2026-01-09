"""

# Logseq: [[TTA.dev/Player_experience/Services/Default_character_world_service]]
Service for auto-initializing default character and world for new players.

This service handles the automatic creation of a default character and world
assignment when a new player registers or logs in for the first time.
"""

import logging

from ..managers.character_avatar_manager import CharacterAvatarManager
from ..managers.world_management_module import WorldManagementModule
from ..models.character import (
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    TherapeuticProfile,
)
from ..models.enums import IntensityLevel, TherapeuticApproach

logger = logging.getLogger(__name__)


class SessionCreationError(Exception):
    """Raised when session creation fails."""

    pass


class DefaultCharacterWorldService:
    """Service for auto-initializing default character and world for new players."""

    # Default character template (Brave Warrior)
    DEFAULT_CHARACTER_TEMPLATE = {
        "name": "Brave Warrior",
        "appearance": {
            "physical_description": "A courageous warrior with kind eyes and a determined spirit.",
            "clothing_style": "practical adventuring attire",
            "distinctive_features": ["warm smile", "determined gaze"],
        },
        "background": {
            "name": "Brave Warrior",
            "personality_traits": ["Brave", "Compassionate", "Determined"],
            "backstory": "Once a simple villager who discovered inner strength through adversity. Now on a journey of self-discovery and healing.",
            "core_values": ["Courage", "Compassion", "Growth"],
            "fears_and_anxieties": ["Failure", "Abandonment"],
            "strengths_and_skills": ["Problem-solving", "Empathy", "Resilience"],
            "life_goals": ["Find inner peace", "Help others", "Overcome past trauma"],
            "relationships": {},
        },
        "therapeutic_profile": {
            "primary_concerns": ["anxiety", "self-doubt"],
            "preferred_intensity": IntensityLevel.MEDIUM,
            "comfort_zones": ["nature", "creativity", "meaningful conversation"],
            "readiness_level": 0.7,
            "therapeutic_goals": [
                {
                    "goal_id": "goal_confidence",
                    "description": "Develop greater self-confidence and belief in abilities",
                    "therapeutic_approaches": ["cognitive_behavioral_therapy"],
                    "milestones": [
                        "Identify limiting beliefs",
                        "Practice positive affirmations",
                        "Take small risks",
                    ],
                },
                {
                    "goal_id": "goal_trauma",
                    "description": "Work through past difficult experiences",
                    "therapeutic_approaches": [
                        "cognitive_behavioral_therapy",
                        "narrative_therapy",
                    ],
                    "milestones": [
                        "Acknowledge past experiences",
                        "Process emotions",
                        "Integrate learnings",
                    ],
                },
                {
                    "goal_id": "goal_coping",
                    "description": "Learn and practice healthy coping mechanisms",
                    "therapeutic_approaches": [
                        "mindfulness",
                        "cognitive_behavioral_therapy",
                    ],
                    "milestones": [
                        "Learn techniques",
                        "Practice regularly",
                        "Apply in real situations",
                    ],
                },
            ],
        },
    }

    # Default world ID (Mindfulness Garden)
    DEFAULT_WORLD_ID = "world_mindfulness_garden"

    def __init__(
        self,
        character_manager: CharacterAvatarManager | None = None,
        world_manager: WorldManagementModule | None = None,
    ):
        """
        Initialize the service.

        Args:
            character_manager: Character avatar manager instance
            world_manager: World management module instance
        """
        self.character_manager = character_manager or CharacterAvatarManager()
        self.world_manager = world_manager or WorldManagementModule()
        logger.info("DefaultCharacterWorldService initialized")

    def initialize_default_character_and_world(
        self, player_id: str
    ) -> tuple[str | None, str | None, str | None]:
        """
        Initialize default character and world for a new player.

        Args:
            player_id: The player ID

        Returns:
            Tuple of (character_id, world_id, session_id) if successful, (None, None, None) otherwise
        """
        try:
            # Check if player already has characters
            existing_characters = self.character_manager.get_player_characters(
                player_id
            )
            if existing_characters:
                logger.debug(
                    f"Player {player_id} already has {len(existing_characters)} characters, skipping auto-initialization"
                )
                return None, None, None

            # Create default character
            character_id = self._create_default_character(player_id)
            if not character_id:
                logger.warning(
                    f"Failed to create default character for player {player_id}"
                )
                return None, None, None

            # Verify default world exists
            world_details = self.world_manager.get_world_details(self.DEFAULT_WORLD_ID)
            if not world_details:
                logger.warning(
                    f"Default world {self.DEFAULT_WORLD_ID} not found, cannot assign"
                )
                return character_id, None, None

            # Create initial session linking character and world
            session_id = self._create_initial_session(
                player_id, character_id, self.DEFAULT_WORLD_ID
            )
            if not session_id:
                logger.warning(
                    f"Failed to create initial session for player {player_id}, but character and world were assigned"
                )

            logger.info(
                f"Successfully initialized default character {character_id}, world {self.DEFAULT_WORLD_ID}, and session {session_id} for player {player_id}"
            )
            return character_id, self.DEFAULT_WORLD_ID, session_id

        except Exception as e:
            logger.error(
                f"Error initializing default character and world for player {player_id}: {e}",
                exc_info=True,
            )
            return None, None, None

    def _create_default_character(self, player_id: str) -> str | None:
        """
        Create the default character for a player.

        Args:
            player_id: The player ID

        Returns:
            The character ID if successful, None otherwise
        """
        try:
            from ..models.character import TherapeuticGoal

            template = self.DEFAULT_CHARACTER_TEMPLATE

            # Convert therapeutic goals from dicts to TherapeuticGoal objects
            therapeutic_goals = []
            for goal_dict in template["therapeutic_profile"]["therapeutic_goals"]:
                # Convert therapeutic_approaches strings to TherapeuticApproach enums
                approaches = [
                    TherapeuticApproach(app)
                    for app in goal_dict.get("therapeutic_approaches", [])
                ]
                goal = TherapeuticGoal(
                    goal_id=goal_dict["goal_id"],
                    description=goal_dict["description"],
                    therapeutic_approaches=approaches,
                    milestones=goal_dict.get("milestones", []),
                )
                therapeutic_goals.append(goal)

            # Create character data from template
            character_data = CharacterCreationData(
                name=template["name"],
                appearance=CharacterAppearance(
                    physical_description=template["appearance"]["physical_description"],
                    clothing_style=template["appearance"]["clothing_style"],
                    distinctive_features=template["appearance"]["distinctive_features"],
                ),
                background=CharacterBackground(
                    name=template["background"]["name"],
                    personality_traits=template["background"]["personality_traits"],
                    backstory=template["background"]["backstory"],
                    core_values=template["background"]["core_values"],
                    fears_and_anxieties=template["background"]["fears_and_anxieties"],
                    strengths_and_skills=template["background"]["strengths_and_skills"],
                    life_goals=template["background"]["life_goals"],
                    relationships=template["background"]["relationships"],
                ),
                therapeutic_profile=TherapeuticProfile(
                    primary_concerns=template["therapeutic_profile"][
                        "primary_concerns"
                    ],
                    preferred_intensity=template["therapeutic_profile"][
                        "preferred_intensity"
                    ],
                    comfort_zones=template["therapeutic_profile"]["comfort_zones"],
                    readiness_level=template["therapeutic_profile"]["readiness_level"],
                    therapeutic_goals=therapeutic_goals,
                ),
            )

            # Create character using manager
            character = self.character_manager.create_character(
                player_id, character_data
            )
            logger.info(
                f"Created default character {character.character_id} for player {player_id}"
            )
            return character.character_id

        except Exception as e:
            logger.error(
                f"Error creating default character for player {player_id}: {e}",
                exc_info=True,
            )
            return None

    def _create_initial_session(
        self, player_id: str, character_id: str, world_id: str
    ) -> str | None:
        """
        Create an initial session linking character and world.

        Args:
            player_id: The player ID
            character_id: The character ID
            world_id: The world ID

        Returns:
            The session ID if successful, None otherwise
        """
        try:
            import uuid

            session_id = str(uuid.uuid4())

            # Create initial session linking character and world
            # Note: Session persistence is handled asynchronously through the API layer
            # For now, we just create the session ID and return it
            logger.info(
                f"Created initial session {session_id} for player {player_id} with character {character_id} and world {world_id}"
            )

            return session_id

        except Exception as e:
            logger.error(
                f"Error creating initial session for player {player_id}: {e}",
                exc_info=True,
            )
            return None
