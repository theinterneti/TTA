"""
Neo4j Manager for Gameplay Loop

This module provides Neo4j database management functionality for the therapeutic text adventure
gameplay loop system, including session management, scene operations, and choice tracking.
"""

import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as redis
from neo4j import AsyncGraphDatabase

from ..models.core import Choice, Scene, SessionState
from .schema import GameplayLoopSchema

logger = logging.getLogger(__name__)


class Neo4jGameplayManager:
    """Manager for Neo4j operations in the gameplay loop system."""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        redis_url: str = "redis://localhost:6379",
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.redis_url = redis_url

        self._neo4j_driver = None
        self._redis_client = None
        self.schema = GameplayLoopSchema()

    async def initialize(self) -> bool:
        """Initialize database connections and schema."""
        try:
            # Initialize Neo4j
            self._neo4j_driver = AsyncGraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )

            # Test Neo4j connection
            await self._neo4j_driver.verify_connectivity()
            logger.info("Neo4j connection established")

            # Initialize Redis
            self._redis_client = redis.from_url(self.redis_url)
            await self._redis_client.ping()
            logger.info("Redis connection established")

            # Initialize schema
            await self.schema.initialize_schema(self._neo4j_driver)

            return True

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False

    async def close(self):
        """Close database connections."""
        if self._neo4j_driver:
            await self._neo4j_driver.close()
        if self._redis_client:
            await self._redis_client.close()

    # Session Management
    async def create_session(self, session_state: SessionState) -> bool:
        """Create a new gameplay session in Neo4j."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                CREATE (s:{self.schema.NODE_LABELS['SESSION']} {{
                    session_id: $session_id,
                    user_id: $user_id,
                    character_id: $character_id,
                    world_id: $world_id,
                    current_scene_id: $current_scene_id,
                    emotional_state: $emotional_state,
                    difficulty_level: $difficulty_level,
                    is_active: $is_active,
                    is_paused: $is_paused,
                    requires_therapeutic_intervention: $requires_therapeutic_intervention,
                    safety_level: $safety_level,
                    total_session_time: $total_session_time,
                    session_start_time: $session_start_time,
                    last_activity_time: $last_activity_time,
                    created_at: $created_at,
                    updated_at: $updated_at
                }})
                RETURN s.session_id as session_id
                """

                result = await session.run(
                    query,
                    {
                        "session_id": session_state.session_id,
                        "user_id": session_state.user_id,
                        "character_id": session_state.character_id,
                        "world_id": session_state.world_id,
                        "current_scene_id": session_state.current_scene_id,
                        "emotional_state": session_state.emotional_state.value,
                        "difficulty_level": session_state.difficulty_level.value,
                        "is_active": session_state.is_active,
                        "is_paused": session_state.is_paused,
                        "requires_therapeutic_intervention": session_state.requires_therapeutic_intervention,
                        "safety_level": session_state.safety_level,
                        "total_session_time": session_state.total_session_time,
                        "session_start_time": session_state.session_start_time,
                        "last_activity_time": session_state.last_activity_time,
                        "created_at": session_state.created_at,
                        "updated_at": session_state.updated_at,
                    },
                )

                record = await result.single()
                if record:
                    # Cache session state in Redis
                    await self._cache_session_state(session_state)
                    logger.info(f"Created session {session_state.session_id}")
                    return True

                return False

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False

    async def get_session(self, session_id: str) -> SessionState | None:
        """Retrieve a session state, first from Redis cache, then Neo4j."""
        try:
            # Try Redis cache first
            cached_session = await self._get_cached_session_state(session_id)
            if cached_session:
                return cached_session

            # Fallback to Neo4j
            async with self._neo4j_driver.session() as session:
                query = f"""
                MATCH (s:{self.schema.NODE_LABELS['SESSION']} {{session_id: $session_id}})
                RETURN s
                """

                result = await session.run(query, {"session_id": session_id})
                record = await result.single()

                if record:
                    session_data = dict(record["s"])
                    session_state = self._neo4j_record_to_session_state(session_data)

                    # Cache for future requests
                    await self._cache_session_state(session_state)
                    return session_state

                return None

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session(self, session_state: SessionState) -> bool:
        """Update session state in both Neo4j and Redis."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                MATCH (s:{self.schema.NODE_LABELS['SESSION']} {{session_id: $session_id}})
                SET s.current_scene_id = $current_scene_id,
                    s.emotional_state = $emotional_state,
                    s.difficulty_level = $difficulty_level,
                    s.is_active = $is_active,
                    s.is_paused = $is_paused,
                    s.requires_therapeutic_intervention = $requires_therapeutic_intervention,
                    s.safety_level = $safety_level,
                    s.total_session_time = $total_session_time,
                    s.last_activity_time = $last_activity_time,
                    s.updated_at = $updated_at
                RETURN s.session_id as session_id
                """

                result = await session.run(
                    query,
                    {
                        "session_id": session_state.session_id,
                        "current_scene_id": session_state.current_scene_id,
                        "emotional_state": session_state.emotional_state.value,
                        "difficulty_level": session_state.difficulty_level.value,
                        "is_active": session_state.is_active,
                        "is_paused": session_state.is_paused,
                        "requires_therapeutic_intervention": session_state.requires_therapeutic_intervention,
                        "safety_level": session_state.safety_level,
                        "total_session_time": session_state.total_session_time,
                        "last_activity_time": session_state.last_activity_time,
                        "updated_at": session_state.updated_at,
                    },
                )

                record = await result.single()
                if record:
                    # Update Redis cache
                    await self._cache_session_state(session_state)
                    return True

                return False

        except Exception as e:
            logger.error(f"Failed to update session {session_state.session_id}: {e}")
            return False

    # Scene Management
    async def create_scene(self, scene: Scene) -> bool:
        """Create a new scene in Neo4j."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                CREATE (sc:{self.schema.NODE_LABELS['SCENE']} {{
                    scene_id: $scene_id,
                    title: $title,
                    description: $description,
                    narrative_content: $narrative_content,
                    scene_type: $scene_type,
                    difficulty_level: $difficulty_level,
                    estimated_duration: $estimated_duration,
                    therapeutic_focus: $therapeutic_focus,
                    learning_objectives: $learning_objectives,
                    emotional_tone: $emotional_tone,
                    is_completed: $is_completed,
                    completion_time: $completion_time,
                    created_at: $created_at,
                    updated_at: $updated_at
                }})
                RETURN sc.scene_id as scene_id
                """

                result = await session.run(
                    query,
                    {
                        "scene_id": scene.scene_id,
                        "title": scene.title,
                        "description": scene.description,
                        "narrative_content": scene.narrative_content,
                        "scene_type": scene.scene_type.value,
                        "difficulty_level": scene.difficulty_level.value,
                        "estimated_duration": scene.estimated_duration,
                        "therapeutic_focus": scene.therapeutic_focus,
                        "learning_objectives": scene.learning_objectives,
                        "emotional_tone": scene.emotional_tone,
                        "is_completed": scene.is_completed,
                        "completion_time": scene.completion_time,
                        "created_at": scene.created_at,
                        "updated_at": scene.updated_at,
                    },
                )

                record = await result.single()
                return record is not None

        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return False

    async def get_scene(self, scene_id: str) -> Scene | None:
        """Retrieve a scene by ID."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                MATCH (sc:{self.schema.NODE_LABELS['SCENE']} {{scene_id: $scene_id}})
                RETURN sc
                """

                result = await session.run(query, {"scene_id": scene_id})
                record = await result.single()

                if record:
                    scene_data = dict(record["sc"])
                    return self._neo4j_record_to_scene(scene_data)

                return None

        except Exception as e:
            logger.error(f"Failed to get scene {scene_id}: {e}")
            return None

    # Redis Cache Management
    async def _cache_session_state(self, session_state: SessionState) -> None:
        """Cache session state in Redis."""
        try:
            cache_key = f"session:{session_state.session_id}"
            session_data = session_state.model_dump_json()
            await self._redis_client.setex(cache_key, 3600, session_data)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"Failed to cache session state: {e}")

    async def _get_cached_session_state(self, session_id: str) -> SessionState | None:
        """Retrieve cached session state from Redis."""
        try:
            cache_key = f"session:{session_id}"
            cached_data = await self._redis_client.get(cache_key)
            if cached_data:
                session_dict = json.loads(cached_data)
                return SessionState(**session_dict)
            return None
        except Exception as e:
            logger.warning(f"Failed to get cached session state: {e}")
            return None

    # Data Conversion Helpers
    def _neo4j_record_to_session_state(self, record: dict[str, Any]) -> SessionState:
        """Convert Neo4j record to SessionState object."""
        # Convert datetime strings back to datetime objects if needed
        if isinstance(record.get("session_start_time"), str):
            record["session_start_time"] = datetime.fromisoformat(
                record["session_start_time"]
            )
        if isinstance(record.get("last_activity_time"), str):
            record["last_activity_time"] = datetime.fromisoformat(
                record["last_activity_time"]
            )
        if isinstance(record.get("created_at"), str):
            record["created_at"] = datetime.fromisoformat(record["created_at"])
        if isinstance(record.get("updated_at"), str):
            record["updated_at"] = datetime.fromisoformat(record["updated_at"])

        return SessionState(**record)

    def _neo4j_record_to_scene(self, record: dict[str, Any]) -> Scene:
        """Convert Neo4j record to Scene object."""
        # Convert datetime strings back to datetime objects if needed
        if isinstance(record.get("created_at"), str):
            record["created_at"] = datetime.fromisoformat(record["created_at"])
        if isinstance(record.get("updated_at"), str):
            record["updated_at"] = datetime.fromisoformat(record["updated_at"])
        if record.get("completion_time") and isinstance(record["completion_time"], str):
            record["completion_time"] = datetime.fromisoformat(
                record["completion_time"]
            )

        return Scene(**record)

    # Choice Management
    async def create_choice(self, choice: Choice) -> bool:
        """Create a new choice in Neo4j."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                CREATE (c:{self.schema.NODE_LABELS['CHOICE']} {{
                    choice_id: $choice_id,
                    scene_id: $scene_id,
                    text: $text,
                    description: $description,
                    choice_type: $choice_type,
                    difficulty_level: $difficulty_level,
                    therapeutic_value: $therapeutic_value,
                    prerequisites: $prerequisites,
                    emotional_requirements: $emotional_requirements,
                    skill_requirements: $skill_requirements,
                    immediate_consequences: $immediate_consequences,
                    long_term_consequences: $long_term_consequences,
                    therapeutic_outcomes: $therapeutic_outcomes,
                    is_available: $is_available,
                    availability_reason: $availability_reason,
                    created_at: $created_at
                }})
                RETURN c.choice_id as choice_id
                """

                result = await session.run(
                    query,
                    {
                        "choice_id": choice.choice_id,
                        "scene_id": choice.scene_id,
                        "text": choice.text,
                        "description": choice.description,
                        "choice_type": choice.choice_type.value,
                        "difficulty_level": choice.difficulty_level.value,
                        "therapeutic_value": choice.therapeutic_value,
                        "prerequisites": choice.prerequisites,
                        "emotional_requirements": [
                            req.value for req in choice.emotional_requirements
                        ],
                        "skill_requirements": choice.skill_requirements,
                        "immediate_consequences": choice.immediate_consequences,
                        "long_term_consequences": choice.long_term_consequences,
                        "therapeutic_outcomes": choice.therapeutic_outcomes,
                        "is_available": choice.is_available,
                        "availability_reason": choice.availability_reason,
                        "created_at": choice.created_at,
                    },
                )

                record = await result.single()
                return record is not None

        except Exception as e:
            logger.error(f"Failed to create choice: {e}")
            return False

    async def get_scene_choices(self, scene_id: str) -> list[Choice]:
        """Get all choices for a specific scene."""
        try:
            async with self._neo4j_driver.session() as session:
                query = f"""
                MATCH (sc:{self.schema.NODE_LABELS['SCENE']} {{scene_id: $scene_id}})
                      -[:{self.schema.RELATIONSHIPS['HAS_CHOICE']}]->
                      (c:{self.schema.NODE_LABELS['CHOICE']})
                WHERE c.is_available = true
                RETURN c
                ORDER BY c.created_at
                """

                result = await session.run(query, {"scene_id": scene_id})
                choices = []

                async for record in result:
                    choice_data = dict(record["c"])
                    choice = self._neo4j_record_to_choice(choice_data)
                    choices.append(choice)

                return choices

        except Exception as e:
            logger.error(f"Failed to get scene choices: {e}")
            return []

    def _neo4j_record_to_choice(self, record: dict[str, Any]) -> Choice:
        """Convert Neo4j record to Choice object."""
        # Convert datetime strings back to datetime objects if needed
        if isinstance(record.get("created_at"), str):
            record["created_at"] = datetime.fromisoformat(record["created_at"])

        return Choice(**record)
