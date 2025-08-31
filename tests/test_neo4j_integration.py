"""
Neo4j Integration Tests for Gameplay Loop

This module tests Neo4j database integration for the therapeutic gameplay loop,
including schema creation, data operations, and query functionality.
"""

from datetime import datetime

import pytest
import pytest_asyncio
from testcontainers.neo4j import Neo4jContainer

from src.components.gameplay_loop.database.migrations import (
    MigrationManager,
    setup_database,
)
from src.components.gameplay_loop.database.neo4j_manager import (
    Neo4jConnectionManager,
    Neo4jGameplayManager,
)
from src.components.gameplay_loop.database.schema import (
    NodeType,
    RelationshipType,
)
from src.components.gameplay_loop.models.core import (
    ChoiceType,
    GameplaySession,
    GameplayState,
    NarrativeScene,
    SceneType,
    UserChoice,
)
from src.components.gameplay_loop.models.progress import (
    ProgressMetric,
    ProgressType,
    SkillDevelopment,
    SkillLevel,
)


@pytest.fixture(scope="session")
def neo4j_container():
    """Start Neo4j container for testing."""
    with Neo4jContainer("neo4j:5.8") as container:
        container.with_env("NEO4J_AUTH", "neo4j/testpassword")
        container.with_env("NEO4J_PLUGINS", '["apoc"]')
        yield container


@pytest_asyncio.fixture(scope="session")
async def connection_manager(neo4j_container):
    """Create Neo4j connection manager for testing."""
    uri = neo4j_container.get_connection_url()
    manager = Neo4jConnectionManager(
        uri=uri, username="neo4j", password="testpassword", database="neo4j"
    )

    # Connect and setup database
    await manager.connect()
    await setup_database(manager)

    yield manager

    await manager.disconnect()


@pytest_asyncio.fixture
async def gameplay_manager(connection_manager):
    """Create gameplay manager for testing."""
    return Neo4jGameplayManager(connection_manager)


@pytest_asyncio.fixture
async def sample_session():
    """Create sample gameplay session for testing."""
    return GameplaySession(
        user_id="test_user_123",
        character_id="test_character_456",
        therapeutic_goals=["anxiety_management", "social_skills"],
        safety_level="standard",
    )


@pytest_asyncio.fixture
async def sample_scene(sample_session):
    """Create sample narrative scene for testing."""
    return NarrativeScene(
        session_id=sample_session.session_id,
        title="Peaceful Garden",
        description="A calming garden scene for mindfulness practice",
        narrative_content="You find yourself in a peaceful garden...",
        scene_type=SceneType.THERAPEUTIC_MOMENT,
        therapeutic_focus=["mindfulness", "grounding"],
        emotional_tone={"calm": 0.8, "peaceful": 0.9},
    )


@pytest.mark.neo4j
class TestNeo4jConnection:
    """Test Neo4j connection and basic operations."""

    @pytest.mark.asyncio
    async def test_connection_health_check(self, connection_manager):
        """Test Neo4j connection health check."""
        is_healthy = await connection_manager.health_check()
        assert is_healthy

    @pytest.mark.asyncio
    async def test_connection_retry_logic(self):
        """Test connection retry logic with invalid credentials."""
        manager = Neo4jConnectionManager(
            uri="bolt://localhost:7687", username="invalid", password="invalid"
        )

        # Should fail after retries
        with pytest.raises(Exception):
            await manager.connect()


@pytest.mark.neo4j
class TestDatabaseSchema:
    """Test database schema creation and validation."""

    async def test_schema_initialization(self, gameplay_manager):
        """Test schema initialization with constraints and indexes."""
        success = await gameplay_manager.initialize_schema()
        assert success

    async def test_constraints_exist(self, connection_manager):
        """Test that required constraints are created."""
        query = "SHOW CONSTRAINTS"

        async with connection_manager.session() as session:
            result = await session.run(query)
            constraints = await result.data()

            # Check for key constraints
            constraint_names = [c.get("name", "") for c in constraints]
            assert any("session_session_id_unique" in name for name in constraint_names)
            assert any("user_user_id_unique" in name for name in constraint_names)

    async def test_indexes_exist(self, connection_manager):
        """Test that required indexes are created."""
        query = "SHOW INDEXES"

        async with connection_manager.session() as session:
            result = await session.run(query)
            indexes = await result.data()

            # Check for key indexes
            index_names = [idx.get("name", "") for idx in indexes]
            assert any("session_user_state_index" in name for name in index_names)


@pytest.mark.neo4j
class TestSessionOperations:
    """Test session-related database operations."""

    async def test_create_session_node(self, gameplay_manager, sample_session):
        """Test creating a session node."""
        success = await gameplay_manager.create_session_node(sample_session)
        assert success

        # Verify session was created
        retrieved_session = await gameplay_manager.get_session_by_id(
            sample_session.session_id
        )
        assert retrieved_session is not None
        assert retrieved_session["session_id"] == sample_session.session_id
        assert retrieved_session["user_id"] == sample_session.user_id

    async def test_update_session_state(self, gameplay_manager, sample_session):
        """Test updating session state."""
        # Create session first
        await gameplay_manager.create_session_node(sample_session)

        # Update state
        success = await gameplay_manager.update_session_state(
            sample_session.session_id, GameplayState.ACTIVE.value
        )
        assert success

        # Verify update
        retrieved_session = await gameplay_manager.get_session_by_id(
            sample_session.session_id
        )
        assert retrieved_session["session_state"] == GameplayState.ACTIVE.value

    async def test_get_user_sessions(self, gameplay_manager, sample_session):
        """Test retrieving user sessions."""
        # Create session first
        await gameplay_manager.create_session_node(sample_session)

        # Get user sessions
        sessions = await gameplay_manager.get_user_sessions(sample_session.user_id)
        assert len(sessions) >= 1
        assert any(s["session_id"] == sample_session.session_id for s in sessions)


@pytest.mark.neo4j
class TestNarrativeOperations:
    """Test narrative-related database operations."""

    async def test_create_scene_node(
        self, gameplay_manager, sample_session, sample_scene
    ):
        """Test creating a scene node."""
        # Create session first
        await gameplay_manager.create_session_node(sample_session)

        # Create scene
        success = await gameplay_manager.narrative_manager.create_scene_node(
            sample_scene
        )
        assert success

    async def test_create_choice_node(
        self, gameplay_manager, sample_session, sample_scene
    ):
        """Test creating a choice node."""
        # Create session and scene first
        await gameplay_manager.create_session_node(sample_session)
        await gameplay_manager.narrative_manager.create_scene_node(sample_scene)

        # Create choice
        choice = UserChoice(
            scene_id=sample_scene.scene_id,
            choice_text="Practice deep breathing",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_relevance=0.9,
        )

        success = await gameplay_manager.narrative_manager.create_choice_node(choice)
        assert success

        # Verify choice was created
        choices = await gameplay_manager.narrative_manager.get_scene_choices(
            sample_scene.scene_id
        )
        assert len(choices) >= 1
        assert any(c["choice_id"] == choice.choice_id for c in choices)

    async def test_create_narrative_flow(self, gameplay_manager, sample_session):
        """Test creating narrative flow between scenes."""
        # Create session first
        await gameplay_manager.create_session_node(sample_session)

        # Create two scenes
        scene1 = NarrativeScene(
            session_id=sample_session.session_id,
            title="Scene 1",
            description="First scene",
            narrative_content="Beginning...",
            scene_type=SceneType.INTRODUCTION,
        )

        scene2 = NarrativeScene(
            session_id=sample_session.session_id,
            title="Scene 2",
            description="Second scene",
            narrative_content="Continuing...",
            scene_type=SceneType.EXPLORATION,
        )

        await gameplay_manager.narrative_manager.create_scene_node(scene1)
        await gameplay_manager.narrative_manager.create_scene_node(scene2)

        # Create narrative flow
        success = await gameplay_manager.narrative_manager.create_narrative_flow(
            scene1.scene_id, scene2.scene_id
        )
        assert success

    async def test_get_narrative_path(self, gameplay_manager, sample_session):
        """Test retrieving narrative path for a session."""
        # Create session and scene first
        await gameplay_manager.create_session_node(sample_session)

        scene = NarrativeScene(
            session_id=sample_session.session_id,
            title="Test Scene",
            description="Test description",
            narrative_content="Test content",
            scene_type=SceneType.EXPLORATION,
        )

        await gameplay_manager.narrative_manager.create_scene_node(scene)

        # Get narrative path
        path = await gameplay_manager.narrative_manager.get_narrative_path(
            sample_session.session_id
        )
        assert len(path) >= 1


@pytest.mark.neo4j
class TestProgressOperations:
    """Test progress tracking database operations."""

    async def test_create_progress_metric_node(self, gameplay_manager):
        """Test creating a progress metric node."""
        metric = ProgressMetric(
            metric_name="Anxiety Level",
            progress_type=ProgressType.EMOTIONAL_GROWTH,
            current_value=0.6,
            baseline_value=0.8,
            target_value=0.3,
            measurement_method="Self-report scale",
        )

        success = await gameplay_manager.progress_manager.create_progress_metric_node(
            metric, "test_user_123"
        )
        assert success

    async def test_update_progress_metric(self, gameplay_manager):
        """Test updating a progress metric."""
        # Create metric first
        metric = ProgressMetric(
            metric_name="Test Metric",
            progress_type=ProgressType.SKILL_DEVELOPMENT,
            current_value=0.5,
            baseline_value=0.2,
            target_value=0.8,
            measurement_method="Test method",
        )

        await gameplay_manager.progress_manager.create_progress_metric_node(
            metric, "test_user_123"
        )

        # Update metric
        success = await gameplay_manager.progress_manager.update_progress_metric(
            metric.metric_id, 0.7, 0.9
        )
        assert success

    async def test_get_user_progress_metrics(self, gameplay_manager):
        """Test retrieving user progress metrics."""
        # Create metric first
        metric = ProgressMetric(
            metric_name="User Progress Test",
            progress_type=ProgressType.BEHAVIORAL_CHANGE,
            current_value=0.4,
            baseline_value=0.1,
            target_value=0.9,
            measurement_method="Behavioral observation",
        )

        await gameplay_manager.progress_manager.create_progress_metric_node(
            metric, "test_user_456"
        )

        # Get metrics
        metrics = await gameplay_manager.progress_manager.get_user_progress_metrics(
            "test_user_456"
        )
        assert len(metrics) >= 1
        assert any(m["metric_id"] == metric.metric_id for m in metrics)

    async def test_create_skill_development_node(self, gameplay_manager):
        """Test creating a skill development node."""
        skill = SkillDevelopment(
            skill_name="Deep Breathing",
            skill_category="Anxiety Management",
            current_level=SkillLevel.DEVELOPING,
            proficiency_score=0.6,
            practice_sessions=5,
        )

        success = await gameplay_manager.progress_manager.create_skill_development_node(
            skill, "test_user_789"
        )
        assert success


@pytest.mark.neo4j
class TestRelationshipOperations:
    """Test relationship management operations."""

    async def test_create_relationship(self, gameplay_manager, connection_manager):
        """Test creating relationships between nodes."""
        # Create two test nodes first
        query1 = (
            "CREATE (u:User {user_id: 'rel_test_user', id: 'rel_test_user'}) RETURN u"
        )
        query2 = "CREATE (s:Session {session_id: 'rel_test_session', id: 'rel_test_session'}) RETURN s"

        async with connection_manager.session() as session:
            await session.run(query1)
            await session.run(query2)

        # Create relationship
        success = await gameplay_manager.relationship_manager.create_relationship(
            "rel_test_user",
            NodeType.USER,
            "rel_test_session",
            NodeType.SESSION,
            RelationshipType.HAS_SESSION,
            {"created_at": datetime.utcnow().isoformat()},
        )
        assert success

    async def test_get_related_nodes(self, gameplay_manager, connection_manager):
        """Test retrieving related nodes."""
        # Create test nodes and relationship first
        query = """
        CREATE (u:User {user_id: 'related_test_user', id: 'related_test_user'})
        CREATE (s:Session {session_id: 'related_test_session', id: 'related_test_session'})
        CREATE (u)-[:HAS_SESSION {created_at: $created_at}]->(s)
        RETURN u, s
        """

        async with connection_manager.session() as session:
            await session.run(query, {"created_at": datetime.utcnow().isoformat()})

        # Get related nodes
        related = await gameplay_manager.relationship_manager.get_related_nodes(
            "related_test_user", NodeType.USER, RelationshipType.HAS_SESSION, "outgoing"
        )
        assert len(related) >= 1


@pytest.mark.neo4j
class TestMigrationSystem:
    """Test database migration system."""

    async def test_migration_manager_initialization(self, connection_manager):
        """Test migration manager initialization."""
        migration_manager = MigrationManager(connection_manager)
        assert len(migration_manager.migrations) > 0

    async def test_get_migration_status(self, connection_manager):
        """Test getting migration status."""
        migration_manager = MigrationManager(connection_manager)
        status = await migration_manager.get_migration_status()

        assert "total_migrations" in status
        assert "applied_migrations" in status
        assert "is_up_to_date" in status
        assert isinstance(status["applied_versions"], list)

    async def test_migration_recording(self, connection_manager):
        """Test recording migration application."""
        migration_manager = MigrationManager(connection_manager)

        await migration_manager.record_migration(
            "test_migration_001", "Test migration for recording", True
        )

        applied_migrations = await migration_manager.get_applied_migrations()
        assert "test_migration_001" in applied_migrations


@pytest.mark.neo4j
class TestQueryPerformance:
    """Test query performance and optimization."""

    async def test_session_query_performance(
        self, gameplay_manager, connection_manager
    ):
        """Test session query performance with multiple sessions."""
        # Create multiple sessions for performance testing
        user_id = "perf_test_user"
        sessions = []

        for i in range(10):
            session = GameplaySession(
                user_id=user_id,
                therapeutic_goals=["test_goal"],
                safety_level="standard",
            )
            sessions.append(session)
            await gameplay_manager.create_session_node(session)

        # Test query performance
        start_time = datetime.utcnow()
        user_sessions = await gameplay_manager.get_user_sessions(user_id, limit=20)
        end_time = datetime.utcnow()

        query_time = (end_time - start_time).total_seconds()

        assert len(user_sessions) == 10
        assert query_time < 1.0  # Should complete within 1 second

    async def test_complex_narrative_query(self, gameplay_manager, sample_session):
        """Test complex narrative path queries."""
        # Create session with multiple scenes
        await gameplay_manager.create_session_node(sample_session)

        scenes = []
        for i in range(5):
            scene = NarrativeScene(
                session_id=sample_session.session_id,
                title=f"Scene {i + 1}",
                description=f"Scene {i + 1} description",
                narrative_content=f"Content for scene {i + 1}",
                scene_type=SceneType.EXPLORATION,
            )
            scenes.append(scene)
            await gameplay_manager.narrative_manager.create_scene_node(scene)

        # Create narrative flows
        for i in range(len(scenes) - 1):
            await gameplay_manager.narrative_manager.create_narrative_flow(
                scenes[i].scene_id, scenes[i + 1].scene_id
            )

        # Test narrative path query
        start_time = datetime.utcnow()
        path = await gameplay_manager.narrative_manager.get_narrative_path(
            sample_session.session_id
        )
        end_time = datetime.utcnow()

        query_time = (end_time - start_time).total_seconds()

        assert len(path) >= 5
        assert query_time < 0.5  # Should complete within 0.5 seconds
