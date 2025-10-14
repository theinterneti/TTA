"""
Character Repository for database operations.

This module provides the CharacterRepository class that handles all database
operations for character data, including CRUD operations and queries.
"""

import json
import logging
from datetime import datetime
from typing import Any

from neo4j import GraphDatabase

from ..models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    TherapeuticGoal,
    TherapeuticProfile,
)
from ..models.enums import IntensityLevel, TherapeuticApproach

logger = logging.getLogger(__name__)


class CharacterRepository:
    """Repository for character database operations."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "tta_dev_password_2024",
    ):
        """Initialize the Character Repository with Neo4j connection."""
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self._connected = False

        # Fallback in-memory storage for when Neo4j is not available
        self._characters: dict[str, Character] = {}
        self._player_characters: dict[str, list[str]] = {}

        # Try to connect to Neo4j
        try:
            self._connect()
            logger.info("CharacterRepository initialized with Neo4j persistence")
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j, using in-memory storage: {e}")
            logger.info("CharacterRepository initialized with in-memory fallback")

    def _connect(self):
        """Connect to Neo4j database."""
        self.driver = GraphDatabase.driver(
            self.uri, auth=(self.username, self.password)
        )
        # Test connection
        with self.driver.session() as session:
            session.run("RETURN 1")
        self._connected = True

    def create_character(self, character: Character) -> Character:
        """
        Create a new character in the database.

        Args:
            character: The character to create

        Returns:
            The created character
        """
        if self._connected and self.driver:
            try:
                self._create_character_neo4j(character)
                logger.debug(f"Created character {character.character_id} in Neo4j")
            except Exception as e:
                logger.error(f"Failed to create character in Neo4j: {e}")
                # Fall back to in-memory storage
                self._create_character_memory(character)
        else:
            # Use in-memory storage
            self._create_character_memory(character)

        return character

    def _create_character_neo4j(self, character: Character):
        """Create character in Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            # Serialize complex objects to JSON
            appearance_json = json.dumps(
                {
                    "age_range": character.appearance.age_range,
                    "gender_identity": character.appearance.gender_identity,
                    "physical_description": character.appearance.physical_description,
                    "clothing_style": character.appearance.clothing_style,
                    "distinctive_features": character.appearance.distinctive_features,
                    "avatar_image_url": character.appearance.avatar_image_url,
                }
            )

            background_json = json.dumps(
                {
                    "name": character.background.name,
                    "backstory": character.background.backstory,
                    "personality_traits": character.background.personality_traits,
                    "core_values": character.background.core_values,
                    "fears_and_anxieties": character.background.fears_and_anxieties,
                    "strengths_and_skills": character.background.strengths_and_skills,
                    "life_goals": character.background.life_goals,
                    "relationships": character.background.relationships,
                }
            )

            # Serialize therapeutic goals
            goals_json = json.dumps(
                [
                    {
                        "goal_id": goal.goal_id,
                        "description": goal.description,
                        "target_date": (
                            goal.target_date.isoformat() if goal.target_date else None
                        ),
                        "progress_percentage": goal.progress_percentage,
                        "therapeutic_approaches": [
                            app.value for app in goal.therapeutic_approaches
                        ],
                        "milestones": goal.milestones,
                        "is_active": goal.is_active,
                    }
                    for goal in character.therapeutic_profile.therapeutic_goals
                ]
            )

            therapeutic_profile_json = json.dumps(
                {
                    "primary_concerns": character.therapeutic_profile.primary_concerns,
                    "therapeutic_goals": goals_json,
                    "preferred_intensity": character.therapeutic_profile.preferred_intensity.value,
                    "comfort_zones": character.therapeutic_profile.comfort_zones,
                    "challenge_areas": character.therapeutic_profile.challenge_areas,
                    "coping_strategies": character.therapeutic_profile.coping_strategies,
                    "trigger_topics": character.therapeutic_profile.trigger_topics,
                    "therapeutic_history": character.therapeutic_profile.therapeutic_history,
                    "readiness_level": character.therapeutic_profile.readiness_level,
                    "therapeutic_approaches": [
                        app.value
                        for app in character.therapeutic_profile.therapeutic_approaches
                    ],
                }
            )

            query = """
            CREATE (c:Character {
                character_id: $character_id,
                player_id: $player_id,
                name: $name,
                appearance: $appearance,
                background: $background,
                therapeutic_profile: $therapeutic_profile,
                created_at: $created_at,
                last_active: $last_active,
                active_worlds: $active_worlds,
                total_session_time: $total_session_time,
                session_count: $session_count,
                is_active: $is_active
            })
            RETURN c.character_id as character_id
            """

            result = session.run(
                query,
                character_id=character.character_id,
                player_id=character.player_id,
                name=character.name,
                appearance=appearance_json,
                background=background_json,
                therapeutic_profile=therapeutic_profile_json,
                created_at=character.created_at.isoformat(),
                last_active=character.last_active.isoformat(),
                active_worlds=character.active_worlds,
                total_session_time=character.total_session_time,
                session_count=character.session_count,
                is_active=character.is_active,
            )

            record = result.single()
            if record:
                created_id = record["character_id"]
                logger.debug(f"Character {created_id} created in Neo4j")

    def _create_character_memory(self, character: Character):
        """Create character in in-memory storage."""
        # Store character
        self._characters[character.character_id] = character

        # Update player-character mapping
        if character.player_id not in self._player_characters:
            self._player_characters[character.player_id] = []

        self._player_characters[character.player_id].append(character.character_id)
        logger.debug(f"Created character {character.character_id} in memory")

    def get_character(self, character_id: str) -> Character | None:
        """
        Get a character by ID.

        Args:
            character_id: The character ID

        Returns:
            The character if found, None otherwise
        """
        if self._connected and self.driver:
            try:
                return self._get_character_neo4j(character_id)
            except Exception as e:
                logger.error(f"Failed to get character from Neo4j: {e}")
                # Fall back to in-memory storage
                self._characters.get(character_id)
        else:
            return self._characters.get(character_id)

    def _get_character_neo4j(self, character_id: str) -> Character | None:
        """Get character from Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            query = """
            MATCH (c:Character {character_id: $character_id})
            RETURN c
            """

            result = session.run(query, character_id=character_id)
            record = result.single()

            if not record:
                return None

            return self._deserialize_character(record["c"])

    def get_characters_by_player(self, player_id: str) -> list[Character]:
        """
        Get all active characters for a player.

        Args:
            player_id: The player ID

        Returns:
            List of active characters
        """
        if self._connected and self.driver:
            try:
                return self._get_characters_by_player_neo4j(player_id)
            except Exception as e:
                logger.error(f"Failed to get characters from Neo4j: {e}")
                # Fall back to in-memory storage
                return self._get_characters_by_player_memory(player_id)
        else:
            return self._get_characters_by_player_memory(player_id)

    def _get_characters_by_player_neo4j(self, player_id: str) -> list[Character]:
        """Get characters by player from Neo4j database."""
        assert self.driver is not None, "Driver must be initialized"
        with self.driver.session() as session:
            query = """
            MATCH (c:Character {player_id: $player_id, is_active: true})
            RETURN c
            ORDER BY c.created_at DESC
            """

            result = session.run(query, player_id=player_id)
            characters = []

            for record in result:
                character = self._deserialize_character(record["c"])
                if character:
                    characters.append(character)

            return characters

    def _get_characters_by_player_memory(self, player_id: str) -> list[Character]:
        """Get characters by player from in-memory storage."""
        character_ids = self._player_characters.get(player_id, [])
        characters = []

        for character_id in character_ids:
            character = self._characters.get(character_id)
            if character and character.is_active:
                characters.append(character)

        return characters

    def update_character(self, character: Character) -> Character:
        """
        Update an existing character.

        Args:
            character: The character to update

        Returns:
            The updated character
        """
        if character.character_id not in self._characters:
            raise ValueError(f"Character {character.character_id} not found")

        self._characters[character.character_id] = character

        logger.debug(f"Updated character {character.character_id} in repository")
        return character

    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character (soft delete by marking inactive).

        Args:
            character_id: The character ID

        Returns:
            True if character was found and deleted, False otherwise
        """
        character = self._characters.get(character_id)
        if not character:
            return False

        character.is_active = False
        character.last_active = datetime.now()

        logger.debug(f"Deleted character {character_id} in repository")
        return True

    def get_character_count_by_player(self, player_id: str) -> int:
        """
        Get the count of active characters for a player.

        Args:
            player_id: The player ID

        Returns:
            Number of active characters
        """
        return len(self.get_characters_by_player(player_id))

    def _deserialize_character(self, node_data: dict[str, Any]) -> Character | None:
        """Deserialize character data from Neo4j node."""
        try:
            # Parse JSON fields
            appearance_data = json.loads(node_data["appearance"])
            background_data = json.loads(node_data["background"])
            therapeutic_profile_data = json.loads(node_data["therapeutic_profile"])

            # Reconstruct appearance
            appearance = CharacterAppearance(
                age_range=appearance_data["age_range"],
                gender_identity=appearance_data["gender_identity"],
                physical_description=appearance_data["physical_description"],
                clothing_style=appearance_data["clothing_style"],
                distinctive_features=appearance_data["distinctive_features"],
                avatar_image_url=appearance_data.get("avatar_image_url"),
            )

            # Reconstruct background
            background = CharacterBackground(
                name=background_data["name"],
                backstory=background_data["backstory"],
                personality_traits=background_data["personality_traits"],
                core_values=background_data["core_values"],
                fears_and_anxieties=background_data["fears_and_anxieties"],
                strengths_and_skills=background_data["strengths_and_skills"],
                life_goals=background_data["life_goals"],
                relationships=background_data["relationships"],
            )

            # Reconstruct therapeutic goals
            goals_data = json.loads(therapeutic_profile_data["therapeutic_goals"])
            therapeutic_goals = []
            for goal_data in goals_data:
                goal = TherapeuticGoal(
                    goal_id=goal_data["goal_id"],
                    description=goal_data["description"],
                    target_date=(
                        datetime.fromisoformat(goal_data["target_date"])
                        if goal_data["target_date"]
                        else None
                    ),
                    progress_percentage=goal_data["progress_percentage"],
                    therapeutic_approaches=[
                        TherapeuticApproach(app)
                        for app in goal_data["therapeutic_approaches"]
                    ],
                    milestones=goal_data["milestones"],
                    is_active=goal_data["is_active"],
                )
                therapeutic_goals.append(goal)

            # Reconstruct therapeutic profile
            therapeutic_profile = TherapeuticProfile(
                primary_concerns=therapeutic_profile_data["primary_concerns"],
                therapeutic_goals=therapeutic_goals,
                preferred_intensity=IntensityLevel(
                    therapeutic_profile_data["preferred_intensity"]
                ),
                comfort_zones=therapeutic_profile_data["comfort_zones"],
                challenge_areas=therapeutic_profile_data["challenge_areas"],
                coping_strategies=therapeutic_profile_data["coping_strategies"],
                trigger_topics=therapeutic_profile_data["trigger_topics"],
                therapeutic_history=therapeutic_profile_data["therapeutic_history"],
                readiness_level=therapeutic_profile_data["readiness_level"],
                therapeutic_approaches=[
                    TherapeuticApproach(app)
                    for app in therapeutic_profile_data["therapeutic_approaches"]
                ],
            )

            # Reconstruct character
            return Character(
                character_id=node_data["character_id"],
                player_id=node_data["player_id"],
                name=node_data["name"],
                appearance=appearance,
                background=background,
                therapeutic_profile=therapeutic_profile,
                created_at=datetime.fromisoformat(node_data["created_at"]),
                last_active=datetime.fromisoformat(node_data["last_active"]),
                active_worlds=node_data["active_worlds"],
                total_session_time=node_data["total_session_time"],
                session_count=node_data["session_count"],
                is_active=node_data["is_active"],
            )

        except Exception as e:
            logger.error(f"Failed to deserialize character: {e}")
            return None

    def search_characters(
        self, player_id: str, name_filter: str | None = None
    ) -> list[Character]:
        """
        Search characters for a player with optional name filter.

        Args:
            player_id: The player ID
            name_filter: Optional name filter

        Returns:
            List of matching characters
        """
        characters = self.get_characters_by_player(player_id)

        if name_filter:
            name_filter_lower = name_filter.lower()
            characters = [
                char for char in characters if name_filter_lower in char.name.lower()
            ]

        return characters

    def get_all_characters(self) -> list[Character]:
        """
        Get all active characters (for admin/testing purposes).

        Returns:
            List of all active characters
        """
        return [char for char in self._characters.values() if char.is_active]

    def clear_all_characters(self) -> None:
        """
        Clear all characters (for testing purposes).
        """
        self._characters.clear()
        self._player_characters.clear()
        logger.debug("Cleared all characters from repository")
