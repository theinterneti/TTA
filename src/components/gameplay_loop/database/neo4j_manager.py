"""
Neo4j Database Manager for Gameplay Loop

This module provides comprehensive Neo4j database management for the therapeutic
gameplay loop, including connection management, query execution, and data operations.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from neo4j import AsyncGraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from src.components.gameplay_loop.database.queries import (
    NarrativeQueries,
    ProgressQueries,
    SessionQueries,
)
from src.components.gameplay_loop.database.schema import (
    GraphSchema,
    NodeType,
    RelationshipType,
)
from src.components.gameplay_loop.models.core import (
    GameplaySession,
    NarrativeScene,
    UserChoice,
)
from src.components.gameplay_loop.models.progress import (
    ProgressMetric,
    SkillDevelopment,
)

logger = logging.getLogger(__name__)


class Neo4jConnectionManager:
    """Manages Neo4j database connections with retry logic and health monitoring."""

    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = None
        self._connection_attempts = 0
        self._max_retries = 5
        self._retry_delays = [0.5, 1, 2, 4, 8]  # Exponential backoff

    async def connect(self) -> bool:
        """Connect to Neo4j with retry logic and exponential backoff."""
        for attempt in range(self._max_retries):
            try:
                logger.debug(
                    f"Neo4j connection attempt {attempt + 1}/{self._max_retries}"
                )

                self.driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60,
                )

                # Test connection
                async with self.driver.session(database=self.database) as session:
                    result = await session.run("RETURN 1 as test")
                    await result.consume()

                logger.info("Successfully connected to Neo4j")
                self._connection_attempts = 0
                return True

            except (ServiceUnavailable, AuthError) as e:
                self._connection_attempts += 1
                logger.warning(f"Neo4j connection attempt {attempt + 1} failed: {e}")

                if attempt < self._max_retries - 1:
                    delay = self._retry_delays[
                        min(attempt, len(self._retry_delays) - 1)
                    ]
                    logger.debug(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Failed to connect to Neo4j after {self._max_retries} attempts"
                    )
                    raise e

            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                raise e

        return False

    async def disconnect(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Disconnected from Neo4j")

    @asynccontextmanager
    async def session(self, **kwargs):
        """Context manager for Neo4j sessions."""
        if not self.driver:
            await self.connect()

        async with self.driver.session(database=self.database, **kwargs) as session:
            yield session

    async def health_check(self) -> bool:
        """Check Neo4j connection health."""
        try:
            async with self.session() as session:
                result = await session.run("RETURN 1 as health_check")
                await result.consume()
                return True
        except Exception as e:
            logger.warning(f"Neo4j health check failed: {e}")
            return False


class Neo4jGameplayManager:
    """Main manager for Neo4j gameplay loop operations."""

    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager
        self.narrative_manager = NarrativeGraphManager(connection_manager)
        self.progress_manager = ProgressGraphManager(connection_manager)
        self.relationship_manager = RelationshipManager(connection_manager)

    async def initialize_schema(self) -> bool:
        """Initialize the Neo4j schema with constraints and indexes."""
        try:
            schema_statements = GraphSchema.get_all_schema_statements()

            async with self.connection_manager.session() as session:
                for statement in schema_statements:
                    if statement.strip() and not statement.startswith("//"):
                        logger.debug(f"Executing schema statement: {statement}")
                        await session.run(statement)

            logger.info("Neo4j schema initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j schema: {e}")
            return False

    async def create_session_node(self, session: GameplaySession) -> bool:
        """Create a session node in the graph."""
        try:
            query = SessionQueries.CREATE_SESSION
            parameters = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "character_id": session.character_id,
                "world_id": session.world_id,
                "session_state": session.session_state.value,
                "therapeutic_goals": session.therapeutic_goals,
                "safety_level": session.safety_level,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "session_metrics": (
                    session.session_metrics.dict() if session.session_metrics else {}
                ),
            }

            async with self.connection_manager.session() as neo4j_session:
                await neo4j_session.run(query, parameters)

            logger.debug(f"Created session node: {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create session node: {e}")
            return False

    async def update_session_state(
        self, session_id: str, new_state: str, completed_at: datetime | None = None
    ) -> bool:
        """Update session state in the graph."""
        try:
            query = SessionQueries.UPDATE_SESSION_STATE
            parameters = {
                "session_id": session_id,
                "new_state": new_state,
                "last_activity": datetime.utcnow().isoformat(),
                "completed_at": completed_at.isoformat() if completed_at else None,
            }

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                summary = await result.consume()

                if (
                    summary.counters.nodes_created == 0
                    and summary.counters.properties_set == 0
                ):
                    logger.warning(f"No session found with ID: {session_id}")
                    return False

            logger.debug(f"Updated session state: {session_id} -> {new_state}")
            return True

        except Exception as e:
            logger.error(f"Failed to update session state: {e}")
            return False

    async def get_session_by_id(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID."""
        try:
            query = SessionQueries.GET_SESSION_BY_ID
            parameters = {"session_id": session_id}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                record = await result.single()

                if record:
                    return dict(record["session"])
                return None

        except Exception as e:
            logger.error(f"Failed to get session by ID: {e}")
            return None

    async def get_user_sessions(
        self, user_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent sessions for a user."""
        try:
            query = SessionQueries.GET_USER_SESSIONS
            parameters = {"user_id": user_id, "limit": limit}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()

                return [dict(record["session"]) for record in records]

        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []


class NarrativeGraphManager:
    """Manages narrative-related graph operations."""

    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager

    async def create_scene_node(self, scene: NarrativeScene) -> bool:
        """Create a scene node and link it to its session."""
        try:
            query = NarrativeQueries.CREATE_SCENE
            parameters = {
                "scene_id": scene.scene_id,
                "session_id": scene.session_id,
                "title": scene.title,
                "description": scene.description,
                "narrative_content": scene.narrative_content,
                "scene_type": scene.scene_type.value,
                "therapeutic_focus": scene.therapeutic_focus,
                "emotional_tone": scene.emotional_tone,
                "scene_objectives": scene.scene_objectives,
                "completion_criteria": scene.completion_criteria,
                "safety_considerations": scene.safety_considerations,
                "created_at": scene.created_at.isoformat(),
                "completed_at": (
                    scene.completed_at.isoformat() if scene.completed_at else None
                ),
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

            logger.debug(f"Created scene node: {scene.scene_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create scene node: {e}")
            return False

    async def create_choice_node(self, choice: UserChoice) -> bool:
        """Create a choice node and link it to its scene."""
        try:
            query = NarrativeQueries.CREATE_CHOICE
            parameters = {
                "choice_id": choice.choice_id,
                "scene_id": choice.scene_id,
                "choice_text": choice.choice_text,
                "choice_type": choice.choice_type.value,
                "therapeutic_relevance": choice.therapeutic_relevance,
                "emotional_weight": choice.emotional_weight,
                "difficulty_level": choice.difficulty_level,
                "prerequisites": choice.prerequisites,
                "metadata": choice.metadata,
                "timestamp": choice.timestamp.isoformat(),
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

            logger.debug(f"Created choice node: {choice.choice_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create choice node: {e}")
            return False

    async def create_narrative_flow(
        self,
        from_scene_id: str,
        to_scene_id: str,
        choice_id: str | None = None,
        flow_properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create narrative flow relationship between scenes."""
        try:
            query = NarrativeQueries.CREATE_NARRATIVE_FLOW
            parameters = {
                "from_scene_id": from_scene_id,
                "to_scene_id": to_scene_id,
                "choice_id": choice_id,
                "created_at": datetime.utcnow().isoformat(),
                "flow_properties": flow_properties or {},
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

            logger.debug(f"Created narrative flow: {from_scene_id} -> {to_scene_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create narrative flow: {e}")
            return False

    async def get_scene_choices(self, scene_id: str) -> list[dict[str, Any]]:
        """Get all choices available in a scene."""
        try:
            query = NarrativeQueries.GET_SCENE_CHOICES
            parameters = {"scene_id": scene_id}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()

                return [dict(record["choice"]) for record in records]

        except Exception as e:
            logger.error(f"Failed to get scene choices: {e}")
            return []

    async def get_narrative_path(self, session_id: str) -> list[dict[str, Any]]:
        """Get the narrative path taken in a session."""
        try:
            query = NarrativeQueries.GET_NARRATIVE_PATH
            parameters = {"session_id": session_id}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()

                return records

        except Exception as e:
            logger.error(f"Failed to get narrative path: {e}")
            return []


class ProgressGraphManager:
    """Manages progress tracking graph operations."""

    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager

    async def create_progress_metric_node(
        self, metric: ProgressMetric, user_id: str
    ) -> bool:
        """Create a progress metric node and link it to the user."""
        try:
            query = ProgressQueries.CREATE_PROGRESS_METRIC
            parameters = {
                "metric_id": metric.metric_id,
                "user_id": user_id,
                "metric_name": metric.metric_name,
                "progress_type": metric.progress_type.value,
                "current_value": metric.current_value,
                "baseline_value": metric.baseline_value,
                "target_value": metric.target_value,
                "measurement_unit": metric.measurement_unit,
                "measurement_method": metric.measurement_method,
                "confidence_level": metric.confidence_level,
                "last_updated": metric.last_updated.isoformat(),
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

            logger.debug(f"Created progress metric node: {metric.metric_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create progress metric node: {e}")
            return False

    async def update_progress_metric(
        self, metric_id: str, new_value: float, confidence_level: float | None = None
    ) -> bool:
        """Update a progress metric value."""
        try:
            query = ProgressQueries.UPDATE_PROGRESS_METRIC
            parameters = {
                "metric_id": metric_id,
                "new_value": new_value,
                "confidence_level": confidence_level,
                "last_updated": datetime.utcnow().isoformat(),
            }

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                summary = await result.consume()

                if summary.counters.properties_set == 0:
                    logger.warning(f"No progress metric found with ID: {metric_id}")
                    return False

            logger.debug(f"Updated progress metric: {metric_id} -> {new_value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update progress metric: {e}")
            return False

    async def get_user_progress_metrics(
        self, user_id: str, progress_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get progress metrics for a user."""
        try:
            query = ProgressQueries.GET_USER_PROGRESS_METRICS
            parameters = {"user_id": user_id, "progress_type": progress_type}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()

                return [dict(record["metric"]) for record in records]

        except Exception as e:
            logger.error(f"Failed to get user progress metrics: {e}")
            return []

    async def create_skill_development_node(
        self, skill: SkillDevelopment, user_id: str
    ) -> bool:
        """Create a skill development node and link it to the user."""
        try:
            query = ProgressQueries.CREATE_SKILL_DEVELOPMENT
            parameters = {
                "skill_id": skill.skill_id,
                "user_id": user_id,
                "skill_name": skill.skill_name,
                "skill_category": skill.skill_category,
                "current_level": skill.current_level.value,
                "proficiency_score": skill.proficiency_score,
                "practice_sessions": skill.practice_sessions,
                "successful_applications": skill.successful_applications,
                "learning_objectives": skill.learning_objectives,
                "completed_objectives": skill.completed_objectives,
                "created_at": skill.created_at.isoformat(),
                "last_practiced": (
                    skill.last_practiced.isoformat() if skill.last_practiced else None
                ),
            }

            async with self.connection_manager.session() as session:
                await session.run(query, parameters)

            logger.debug(f"Created skill development node: {skill.skill_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create skill development node: {e}")
            return False


class RelationshipManager:
    """Manages graph relationships and connections."""

    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager

    async def create_relationship(
        self,
        from_node_id: str,
        from_node_type: NodeType,
        to_node_id: str,
        to_node_type: NodeType,
        relationship_type: RelationshipType,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create a relationship between two nodes."""
        try:
            query = f"""
            MATCH (from:{from_node_type.value} {{id: $from_node_id}})
            MATCH (to:{to_node_type.value} {{id: $to_node_id}})
            CREATE (from)-[r:{relationship_type.value}]->(to)
            SET r += $properties
            SET r.created_at = $created_at
            RETURN r
            """

            parameters = {
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "properties": properties or {},
                "created_at": datetime.utcnow().isoformat(),
            }

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                record = await result.single()

                if not record:
                    logger.warning("Failed to create relationship: nodes not found")
                    return False

            logger.debug(
                f"Created relationship: {from_node_id} -[{relationship_type.value}]-> {to_node_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    async def get_related_nodes(
        self,
        node_id: str,
        node_type: NodeType,
        relationship_type: RelationshipType,
        direction: str = "outgoing",
    ) -> list[dict[str, Any]]:
        """Get nodes related to a given node."""
        try:
            if direction == "outgoing":
                query = f"""
                MATCH (n:{node_type.value} {{id: $node_id}})-[r:{relationship_type.value}]->(related)
                RETURN related, r
                ORDER BY r.created_at DESC
                """
            elif direction == "incoming":
                query = f"""
                MATCH (related)-[r:{relationship_type.value}]->(n:{node_type.value} {{id: $node_id}})
                RETURN related, r
                ORDER BY r.created_at DESC
                """
            else:  # both
                query = f"""
                MATCH (n:{node_type.value} {{id: $node_id}})-[r:{relationship_type.value}]-(related)
                RETURN related, r
                ORDER BY r.created_at DESC
                """

            parameters = {"node_id": node_id}

            async with self.connection_manager.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()

                return records

        except Exception as e:
            logger.error(f"Failed to get related nodes: {e}")
            return []
