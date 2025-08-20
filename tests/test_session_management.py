"""
Unit tests for session management functionality.

Tests session creation, lifecycle management, context switching,
and integration with the Interactive Narrative Engine.
"""

import unittest
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime, timedelta

from src.player_experience.models.session import (
    SessionContext, TherapeuticSettings, ProgressMarker, SessionSummary
)
from src.player_experience.models.enums import (
    SessionStatus, TherapeuticApproach, ProgressMarkerType
)
from src.player_experience.database.session_repository import SessionRepository
from src.player_experience.managers.session_integration_manager import SessionIntegrationManager


class TestSessionRepository(unittest.TestCase):
    """Test session repository functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis = AsyncMock()
        self.mock_neo4j_driver = AsyncMock()
        self.repository = SessionRepository(
            redis_client=self.mock_redis,
            neo4j_driver=self.mock_neo4j_driver
        )

        # Create test session context
        self.test_settings = TherapeuticSettings(
            intensity_level=0.6,
            preferred_approaches=[TherapeuticApproach.CBT],
            intervention_frequency="balanced"
        )

        self.test_session = SessionContext(
            session_id="test_session_123",
            player_id="player_123",
            character_id="char_123",
            world_id="world_123",
            therapeutic_settings=self.test_settings
        )

    def test_serialize_session_context(self):
        """Test serializing session context for storage."""
        serialized = self.repository._serialize_session_context(self.test_session)

        self.assertEqual(serialized['session_id'], "test_session_123")
        self.assertEqual(serialized['player_id'], "player_123")
        self.assertEqual(serialized['status'], SessionStatus.ACTIVE.value)
        self.assertIsInstance(serialized['created_at'], str)
        self.assertIsInstance(serialized['last_interaction'], str)

    def test_deserialize_session_context(self):
        """Test deserializing session context from storage."""
        # First serialize
        serialized = self.repository._serialize_session_context(self.test_session)

        # Then deserialize
        deserialized = self.repository._deserialize_session_context(serialized)

        self.assertEqual(deserialized.session_id, self.test_session.session_id)
        self.assertEqual(deserialized.player_id, self.test_session.player_id)
        self.assertEqual(deserialized.status, self.test_session.status)
        self.assertEqual(
            deserialized.therapeutic_settings.intensity_level,
            self.test_session.therapeutic_settings.intensity_level
        )

    async def _async_create_session(self):
        """Test creating a session in the repository."""
        # Mock Redis and Neo4j operations
        self.mock_redis.setex = AsyncMock(return_value=True)

        mock_neo4j_session = AsyncMock()
        mock_neo4j_session.run = AsyncMock()

        # Create a proper async context manager mock
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_neo4j_session)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        self.mock_neo4j_driver.session.return_value = async_context_manager

        # Test session creation
        result = await self.repository.create_session(self.test_session)

        self.assertTrue(result)
        self.mock_redis.setex.assert_called_once()
        mock_neo4j_session.run.assert_called_once()

    async def _async_get_session_from_cache(self):
        """Test retrieving session from Redis cache."""
        # Mock Redis response
        serialized_data = self.repository._serialize_session_context(self.test_session)
        import json
        self.mock_redis.get = AsyncMock(return_value=json.dumps(serialized_data))

        # Test session retrieval
        result = await self.repository.get_session("test_session_123")

        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, "test_session_123")
        self.assertEqual(result.player_id, "player_123")

    async def _async_pause_session(self):
        """Test pausing an active session."""
        # Mock getting session
        self.mock_redis.get = AsyncMock(return_value=None)

        mock_neo4j_session = AsyncMock()
        mock_record = MagicMock()
        mock_record.__getitem__.side_effect = lambda key: {
            'session_id': 'test_session_123',
            'player_id': 'player_123',
            'character_id': 'char_123',
            'world_id': 'world_123',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_interaction': datetime.now().isoformat(),
            'therapeutic_settings': '{"intensity_level": 0.6, "preferred_approaches": [], "intervention_frequency": "balanced", "feedback_sensitivity": 0.5, "crisis_monitoring_enabled": true, "adaptive_difficulty": true}'
        }[key]

        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value={'s': mock_record})
        mock_neo4j_session.run = AsyncMock(return_value=mock_result)

        # Create a proper async context manager mock
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_neo4j_session)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        self.mock_neo4j_driver.session.return_value = async_context_manager

        # Test pausing session
        result = await self.repository.pause_session("test_session_123")

        self.assertTrue(result)

    async def _async_end_session(self):
        """Test ending an active session."""
        # Mock getting session
        self.mock_redis.get = AsyncMock(return_value=None)

        mock_neo4j_session = AsyncMock()
        mock_record = MagicMock()
        mock_record.__getitem__.side_effect = lambda key: {
            'session_id': 'test_session_123',
            'player_id': 'player_123',
            'character_id': 'char_123',
            'world_id': 'world_123',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_interaction': datetime.now().isoformat(),
            'therapeutic_settings': '{"intensity_level": 0.6, "preferred_approaches": [], "intervention_frequency": "balanced", "feedback_sensitivity": 0.5, "crisis_monitoring_enabled": true, "adaptive_difficulty": true}'
        }[key]

        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value={'s': mock_record})
        mock_neo4j_session.run = AsyncMock(return_value=mock_result)

        # Create a proper async context manager mock
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_neo4j_session)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        self.mock_neo4j_driver.session.return_value = async_context_manager

        # Test ending session
        result = await self.repository.end_session("test_session_123")

        self.assertTrue(result)


class TestSessionIntegrationManager(unittest.TestCase):
    """Test session integration manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = AsyncMock(spec=SessionRepository)
        self.mock_narrative_engine = AsyncMock()

        self.manager = SessionIntegrationManager(
            session_repository=self.mock_repository,
            interactive_narrative_engine=self.mock_narrative_engine
        )

        # Test data
        self.test_player_id = "player_123"
        self.test_character_id = "char_123"
        self.test_world_id = "world_123"

        self.test_settings = TherapeuticSettings(
            intensity_level=0.6,
            preferred_approaches=[TherapeuticApproach.CBT]
        )

    async def _async_create_session(self):
        """Test creating a new session."""
        # Mock repository response
        self.mock_repository.create_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.initialize_session = AsyncMock()

        # Test session creation
        result = await self.manager.create_session(
            self.test_player_id,
            self.test_character_id,
            self.test_world_id,
            self.test_settings
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.player_id, self.test_player_id)
        self.assertEqual(result.character_id, self.test_character_id)
        self.assertEqual(result.world_id, self.test_world_id)
        self.assertEqual(result.status, SessionStatus.ACTIVE)

        # Verify repository and narrative engine were called
        self.mock_repository.create_session.assert_called_once()
        self.mock_narrative_engine.initialize_session.assert_called_once()

    async def _async_switch_character_world_context_new_session(self):
        """Test switching to new character-world combination."""
        # Mock no existing session found
        self.mock_repository.get_player_active_sessions = AsyncMock(return_value=[])
        self.mock_repository.create_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.initialize_session = AsyncMock()

        # Test context switching
        result = await self.manager.switch_character_world_context(
            self.test_player_id,
            "new_char_456",
            "new_world_456"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.character_id, "new_char_456")
        self.assertEqual(result.world_id, "new_world_456")

    async def _async_switch_character_world_context_existing_session(self):
        """Test switching to existing paused session."""
        # Create existing paused session
        existing_session = SessionContext(
            session_id="existing_session",
            player_id=self.test_player_id,
            character_id="new_char_456",
            world_id="new_world_456",
            therapeutic_settings=self.test_settings,
            status=SessionStatus.PAUSED
        )

        # Mock finding existing session
        self.mock_repository.get_player_active_sessions = AsyncMock(
            return_value=[existing_session]
        )
        self.mock_repository.get_session = AsyncMock(return_value=existing_session)
        self.mock_repository.resume_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.restore_session_state = AsyncMock()

        # Test context switching
        result = await self.manager.switch_character_world_context(
            self.test_player_id,
            "new_char_456",
            "new_world_456"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, "existing_session")
        self.assertEqual(result.status, SessionStatus.ACTIVE)

    async def _async_pause_session(self):
        """Test pausing an active session."""
        # Create active session
        active_session = SessionContext(
            session_id="active_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Set up manager state
        self.manager._active_sessions[self.test_player_id] = active_session

        # Mock repository and narrative engine
        self.mock_repository.pause_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.get_session_state = AsyncMock(
            return_value={"current_scene": "scene_1"}
        )

        # Test pausing session
        result = await self.manager.pause_session(self.test_player_id)

        self.assertTrue(result)
        self.assertEqual(active_session.status, SessionStatus.PAUSED)
        self.mock_repository.pause_session.assert_called_once()
        self.mock_narrative_engine.get_session_state.assert_called_once()

    async def _async_resume_session(self):
        """Test resuming a paused session."""
        # Create paused session
        paused_session = SessionContext(
            session_id="paused_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings,
            status=SessionStatus.PAUSED
        )
        paused_session.session_variables['narrative_state'] = {"current_scene": "scene_1"}

        # Mock repository and narrative engine
        self.mock_repository.get_session = AsyncMock(return_value=paused_session)
        self.mock_repository.resume_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.restore_session_state = AsyncMock()

        # Test resuming session
        result = await self.manager.resume_session("paused_session")

        self.assertIsNotNone(result)
        self.assertEqual(result.status, SessionStatus.ACTIVE)
        self.assertEqual(result.session_id, "paused_session")
        self.mock_repository.resume_session.assert_called_once()
        self.mock_narrative_engine.restore_session_state.assert_called_once()

    async def _async_end_session(self):
        """Test ending an active session."""
        # Create active session
        active_session = SessionContext(
            session_id="active_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Set up manager state
        self.manager._active_sessions[self.test_player_id] = active_session

        # Mock repository and narrative engine
        self.mock_repository.end_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.finalize_session = AsyncMock()

        # Test ending session
        result = await self.manager.end_session(self.test_player_id)

        self.assertTrue(result)
        self.assertEqual(active_session.status, SessionStatus.COMPLETED)
        self.assertNotIn(self.test_player_id, self.manager._active_sessions)
        self.mock_repository.end_session.assert_called_once()
        self.mock_narrative_engine.finalize_session.assert_called_once()

    async def _async_update_session_interaction(self):
        """Test updating session with interaction data."""
        # Create active session
        active_session = SessionContext(
            session_id="active_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Set up manager state
        self.manager._active_sessions[self.test_player_id] = active_session

        # Mock repository
        self.mock_repository.update_session = AsyncMock(return_value=True)

        # Test interaction data
        interaction_data = {
            'therapeutic_intervention': 'mindfulness_exercise',
            'emotional_state': {'mood': 'calm', 'anxiety_level': 0.3},
            'session_variables': {'current_exercise': 'breathing'},
            'current_scene_id': 'scene_2'
        }

        # Test updating interaction
        result = await self.manager.update_session_interaction(
            self.test_player_id,
            interaction_data
        )

        self.assertTrue(result)
        self.assertEqual(active_session.interaction_count, 1)
        self.assertIn('mindfulness_exercise', active_session.therapeutic_interventions_used)
        self.assertEqual(active_session.current_scene_id, 'scene_2')
        self.assertEqual(active_session.session_variables['current_exercise'], 'breathing')

    async def _async_add_progress_marker(self):
        """Test adding progress marker to session."""
        # Create active session
        active_session = SessionContext(
            session_id="active_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Set up manager state
        self.manager._active_sessions[self.test_player_id] = active_session

        # Mock repository
        self.mock_repository.update_session = AsyncMock(return_value=True)

        # Create progress marker
        marker = ProgressMarker(
            marker_id="marker_1",
            marker_type=ProgressMarkerType.MILESTONE,
            description="Completed first exercise",
            achieved_at=datetime.now(),
            therapeutic_value=0.8
        )

        # Test adding progress marker
        result = await self.manager.add_progress_marker(self.test_player_id, marker)

        self.assertTrue(result)
        self.assertEqual(len(active_session.progress_markers), 1)
        self.assertEqual(active_session.progress_markers[0].marker_id, "marker_1")

    async def _async_update_therapeutic_settings(self):
        """Test updating therapeutic settings for active session."""
        # Create active session
        active_session = SessionContext(
            session_id="active_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Set up manager state
        self.manager._active_sessions[self.test_player_id] = active_session

        # Mock repository and narrative engine
        self.mock_repository.update_session = AsyncMock(return_value=True)
        self.mock_narrative_engine.update_therapeutic_settings = AsyncMock()

        # New therapeutic settings
        new_settings = TherapeuticSettings(
            intensity_level=0.8,
            preferred_approaches=[TherapeuticApproach.MINDFULNESS],
            intervention_frequency="frequent"
        )

        # Test updating settings
        result = await self.manager.update_therapeutic_settings(
            self.test_player_id,
            new_settings
        )

        self.assertTrue(result)
        self.assertEqual(active_session.therapeutic_settings.intensity_level, 0.8)
        self.assertEqual(
            active_session.therapeutic_settings.preferred_approaches[0],
            TherapeuticApproach.MINDFULNESS
        )
        self.mock_narrative_engine.update_therapeutic_settings.assert_called_once()

    def test_get_session_continuity_data(self):
        """Test getting session continuity data."""
        # Create session with data
        session = SessionContext(
            session_id="test_session",
            player_id=self.test_player_id,
            character_id=self.test_character_id,
            world_id=self.test_world_id,
            therapeutic_settings=self.test_settings
        )

        # Add some data
        session.session_variables = {'key': 'value'}
        session.therapeutic_interventions_used = ['intervention1']
        session.interaction_count = 5
        session.total_duration_minutes = 30

        # Mock repository
        self.mock_repository.get_session = AsyncMock(return_value=session)

        # Test getting continuity data
        async def run_test():
            result = await self.manager.get_session_continuity_data("test_session")

            self.assertIn('therapeutic_settings', result)
            self.assertIn('session_variables', result)
            self.assertIn('therapeutic_interventions_used', result)
            self.assertEqual(result['interaction_count'], 5)
            self.assertEqual(result['total_duration_minutes'], 30)

        asyncio.run(run_test())


class TestSessionLifecycleIntegration(unittest.TestCase):
    """Test complete session lifecycle integration."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.mock_redis = AsyncMock()
        self.mock_neo4j_driver = AsyncMock()
        self.mock_narrative_engine = AsyncMock()

        self.repository = SessionRepository(
            redis_client=self.mock_redis,
            neo4j_driver=self.mock_neo4j_driver
        )

        self.manager = SessionIntegrationManager(
            session_repository=self.repository,
            interactive_narrative_engine=self.mock_narrative_engine
        )

    async def _async_complete_session_lifecycle(self):
        """Test complete session lifecycle from creation to completion."""
        # Mock all external dependencies
        self.mock_redis.setex = AsyncMock(return_value=True)
        self.mock_redis.get = AsyncMock(return_value=None)

        mock_neo4j_session = AsyncMock()
        mock_neo4j_session.run = AsyncMock()

        # Create a proper async context manager mock
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_neo4j_session)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        self.mock_neo4j_driver.session.return_value = async_context_manager

        self.mock_narrative_engine.initialize_session = AsyncMock()
        self.mock_narrative_engine.get_session_state = AsyncMock(return_value={})
        self.mock_narrative_engine.finalize_session = AsyncMock()

        # 1. Create session
        session = await self.manager.create_session(
            "player_123", "char_123", "world_123"
        )
        self.assertIsNotNone(session)
        self.assertEqual(session.status, SessionStatus.ACTIVE)

        # 2. Update with interaction
        interaction_result = await self.manager.update_session_interaction(
            "player_123",
            {'therapeutic_intervention': 'test_intervention'}
        )
        self.assertTrue(interaction_result)

        # 3. Add progress marker
        marker = ProgressMarker(
            marker_id="test_marker",
            marker_type=ProgressMarkerType.MILESTONE,
            description="Test milestone",
            achieved_at=datetime.now()
        )
        marker_result = await self.manager.add_progress_marker("player_123", marker)
        self.assertTrue(marker_result)

        # 4. Pause session
        pause_result = await self.manager.pause_session("player_123")
        self.assertTrue(pause_result)

        # 5. Resume session
        resume_result = await self.manager.resume_session(session.session_id)
        self.assertIsNotNone(resume_result)

        # 6. End session
        end_result = await self.manager.end_session("player_123")
        self.assertTrue(end_result)

        # Verify all narrative engine methods were called
        self.mock_narrative_engine.initialize_session.assert_called_once()
        self.mock_narrative_engine.get_session_state.assert_called_once()
        self.mock_narrative_engine.finalize_session.assert_called_once()




# --- Pytest-style async tests converted from unittest async methods ---

@pytest.mark.asyncio
async def test_repo_create_session_pytest():
    t = TestSessionRepository()
    t.setUp()
    await t._async_create_session()


@pytest.mark.asyncio
async def test_repo_get_session_from_cache_pytest():
    t = TestSessionRepository()
    t.setUp()
    await t._async_get_session_from_cache()


@pytest.mark.asyncio
async def test_repo_pause_session_pytest():
    t = TestSessionRepository()
    t.setUp()
    await t._async_pause_session()


@pytest.mark.asyncio
async def test_repo_end_session_pytest():
    t = TestSessionRepository()
    t.setUp()
    await t._async_end_session()


@pytest.mark.asyncio
async def test_mgr_create_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_create_session()


@pytest.mark.asyncio
async def test_mgr_switch_context_new_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_switch_character_world_context_new_session()


@pytest.mark.asyncio
async def test_mgr_switch_context_existing_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_switch_character_world_context_existing_session()


@pytest.mark.asyncio
async def test_mgr_pause_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_pause_session()


@pytest.mark.asyncio
async def test_mgr_resume_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_resume_session()


@pytest.mark.asyncio
async def test_mgr_end_session_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_end_session()


@pytest.mark.asyncio
async def test_mgr_update_session_interaction_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_update_session_interaction()


@pytest.mark.asyncio
async def test_mgr_add_progress_marker_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_add_progress_marker()


@pytest.mark.asyncio
async def test_mgr_update_therapeutic_settings_pytest():
    t = TestSessionIntegrationManager()
    t.setUp()
    await t._async_update_therapeutic_settings()


@pytest.mark.asyncio
async def test_integration_complete_session_lifecycle_pytest():
    t = TestSessionLifecycleIntegration()
    t.setUp()
    await t._async_complete_session_lifecycle()
