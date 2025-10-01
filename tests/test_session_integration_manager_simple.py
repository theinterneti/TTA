"""
Simplified unit tests for SessionIntegrationManager functionality.

Tests the core session management and context switching functionality
without complex async database mocking.
"""

import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock

from src.player_experience.managers.session_integration_manager import (
    SessionIntegrationManager,
)
from src.player_experience.models.enums import (
    ProgressMarkerType,
    SessionStatus,
    TherapeuticApproach,
)
from src.player_experience.models.session import (
    ProgressMarker,
    SessionContext,
    TherapeuticSettings,
)


class TestSessionIntegrationManagerCore(unittest.TestCase):
    """Test core SessionIntegrationManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = AsyncMock()
        self.mock_narrative_engine = AsyncMock()

        self.manager = SessionIntegrationManager(
            session_repository=self.mock_repository,
            interactive_narrative_engine=self.mock_narrative_engine,
        )

        # Test data
        self.test_player_id = "player_123"
        self.test_character_id = "char_123"
        self.test_world_id = "world_123"

        self.test_settings = TherapeuticSettings(
            intensity_level=0.6, preferred_approaches=[TherapeuticApproach.CBT]
        )

    def test_session_creation_data_structure(self):
        """Test that session creation produces correct data structure."""

        async def run_test():
            # Mock successful repository creation
            self.mock_repository.create_session = AsyncMock(return_value=True)
            self.mock_narrative_engine.initialize_session = AsyncMock()

            # Test session creation
            result = await self.manager.create_session(
                self.test_player_id,
                self.test_character_id,
                self.test_world_id,
                self.test_settings,
            )

            # Verify session structure
            self.assertIsNotNone(result)
            self.assertEqual(result.player_id, self.test_player_id)
            self.assertEqual(result.character_id, self.test_character_id)
            self.assertEqual(result.world_id, self.test_world_id)
            self.assertEqual(result.status, SessionStatus.ACTIVE)
            self.assertEqual(result.therapeutic_settings.intensity_level, 0.6)

            # Verify repository was called with correct session
            self.mock_repository.create_session.assert_called_once()
            call_args = self.mock_repository.create_session.call_args[0][0]
            self.assertEqual(call_args.player_id, self.test_player_id)

            # Verify narrative engine initialization
            self.mock_narrative_engine.initialize_session.assert_called_once()

        asyncio.run(run_test())

    def test_context_switching_logic(self):
        """Test character-world context switching logic."""

        async def run_test():
            # Create current session
            current_session = SessionContext(
                session_id="current_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Set up manager state
            self.manager._active_sessions[self.test_player_id] = current_session

            # Mock no existing session for new combination
            self.mock_repository.get_player_active_sessions = AsyncMock(return_value=[])
            self.mock_repository.pause_session = AsyncMock(return_value=True)
            self.mock_repository.create_session = AsyncMock(return_value=True)
            self.mock_narrative_engine.get_session_state = AsyncMock(return_value={})
            self.mock_narrative_engine.initialize_session = AsyncMock()

            # Test context switching
            result = await self.manager.switch_character_world_context(
                self.test_player_id, "new_char_456", "new_world_456"
            )

            # Verify new session was created
            self.assertIsNotNone(result)
            self.assertEqual(result.character_id, "new_char_456")
            self.assertEqual(result.world_id, "new_world_456")

            # Verify current session was paused
            self.mock_repository.pause_session.assert_called_once()

            # Verify new session was created
            self.mock_repository.create_session.assert_called()

        asyncio.run(run_test())

    def test_session_state_preservation(self):
        """Test session state preservation during context switches."""

        async def run_test():
            # Create session with state
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Add some state data
            session.session_variables = {"key": "value"}
            session.interaction_count = 5
            session.therapeutic_interventions_used = ["intervention1"]

            # Set up manager state
            self.manager._active_sessions[self.test_player_id] = session

            # Mock repository and narrative engine
            self.mock_repository.pause_session = AsyncMock(return_value=True)
            self.mock_narrative_engine.get_session_state = AsyncMock(
                return_value={"narrative_position": 10, "current_scene": "scene_1"}
            )

            # Test pausing session
            result = await self.manager.pause_session(self.test_player_id)

            # Verify session was paused successfully
            self.assertTrue(result)
            self.assertEqual(session.status, SessionStatus.PAUSED)

            # Verify narrative state was preserved
            self.mock_narrative_engine.get_session_state.assert_called_once_with(
                session.session_id
            )

            # Verify session variables contain narrative state
            self.assertIn("narrative_state", session.session_variables)
            self.assertEqual(
                session.session_variables["narrative_state"]["narrative_position"], 10
            )

        asyncio.run(run_test())

    def test_session_interaction_updates(self):
        """Test session interaction updates."""

        async def run_test():
            # Create active session
            session = SessionContext(
                session_id="active_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Set up manager state
            self.manager._active_sessions[self.test_player_id] = session

            # Mock repository
            self.mock_repository.update_session = AsyncMock(return_value=True)

            # Test interaction data
            interaction_data = {
                "therapeutic_intervention": "mindfulness_exercise",
                "emotional_state": {"mood": "calm", "anxiety_level": 0.3},
                "session_variables": {"current_exercise": "breathing"},
                "current_scene_id": "scene_2",
            }

            # Test updating interaction
            result = await self.manager.update_session_interaction(
                self.test_player_id, interaction_data
            )

            # Verify update was successful
            self.assertTrue(result)

            # Verify session was updated correctly
            self.assertEqual(session.interaction_count, 1)
            self.assertIn(
                "mindfulness_exercise", session.therapeutic_interventions_used
            )
            self.assertEqual(session.current_scene_id, "scene_2")
            self.assertEqual(session.session_variables["current_exercise"], "breathing")
            self.assertEqual(len(session.emotional_state_history), 1)

            # Verify repository was called
            self.mock_repository.update_session.assert_called_once_with(session)

        asyncio.run(run_test())

    def test_progress_marker_addition(self):
        """Test adding progress markers to sessions."""

        async def run_test():
            # Create active session
            session = SessionContext(
                session_id="active_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Set up manager state
            self.manager._active_sessions[self.test_player_id] = session

            # Mock repository
            self.mock_repository.update_session = AsyncMock(return_value=True)

            # Create progress marker
            marker = ProgressMarker(
                marker_id="marker_1",
                marker_type=ProgressMarkerType.MILESTONE,
                description="Completed first exercise",
                achieved_at=datetime.now(),
                therapeutic_value=0.8,
            )

            # Test adding progress marker
            result = await self.manager.add_progress_marker(self.test_player_id, marker)

            # Verify marker was added
            self.assertTrue(result)
            self.assertEqual(len(session.progress_markers), 1)
            self.assertEqual(session.progress_markers[0].marker_id, "marker_1")
            self.assertEqual(session.progress_markers[0].therapeutic_value, 0.8)

            # Verify repository was called
            self.mock_repository.update_session.assert_called_once_with(session)

        asyncio.run(run_test())

    def test_therapeutic_settings_update(self):
        """Test updating therapeutic settings."""

        async def run_test():
            # Create active session
            session = SessionContext(
                session_id="active_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Set up manager state
            self.manager._active_sessions[self.test_player_id] = session

            # Mock repository and narrative engine
            self.mock_repository.update_session = AsyncMock(return_value=True)
            self.mock_narrative_engine.update_therapeutic_settings = AsyncMock()

            # New therapeutic settings
            new_settings = TherapeuticSettings(
                intensity_level=0.8,
                preferred_approaches=[TherapeuticApproach.MINDFULNESS],
                intervention_frequency="frequent",
            )

            # Test updating settings
            result = await self.manager.update_therapeutic_settings(
                self.test_player_id, new_settings
            )

            # Verify settings were updated
            self.assertTrue(result)
            self.assertEqual(session.therapeutic_settings.intensity_level, 0.8)
            self.assertEqual(
                session.therapeutic_settings.preferred_approaches[0],
                TherapeuticApproach.MINDFULNESS,
            )
            self.assertEqual(
                session.therapeutic_settings.intervention_frequency, "frequent"
            )

            # Verify narrative engine was updated
            self.mock_narrative_engine.update_therapeutic_settings.assert_called_once_with(
                session.session_id, new_settings
            )

            # Verify repository was called
            self.mock_repository.update_session.assert_called_once_with(session)

        asyncio.run(run_test())

    def test_session_continuity_data(self):
        """Test getting session continuity data."""

        async def run_test():
            # Create session with data
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings,
            )

            # Add some data
            session.session_variables = {"key": "value"}
            session.therapeutic_interventions_used = ["intervention1"]
            session.interaction_count = 5
            session.total_duration_minutes = 30
            session.emotional_state_history = [
                {"timestamp": datetime.now(), "data": {"mood": "calm"}},
                {"timestamp": datetime.now(), "data": {"mood": "happy"}},
            ]

            # Mock repository
            self.mock_repository.get_session = AsyncMock(return_value=session)

            # Test getting continuity data
            result = await self.manager.get_session_continuity_data("test_session")

            # Verify continuity data structure
            self.assertIn("therapeutic_settings", result)
            self.assertIn("session_variables", result)
            self.assertIn("therapeutic_interventions_used", result)
            self.assertEqual(result["interaction_count"], 5)
            self.assertEqual(result["total_duration_minutes"], 30)
            self.assertEqual(len(result["emotional_state_history"]), 2)

            # Verify repository was called
            self.mock_repository.get_session.assert_called_once_with("test_session")

        asyncio.run(run_test())

    def test_error_handling(self):
        """Test error handling in session operations."""

        async def run_test():
            # Test session creation with repository failure
            self.mock_repository.create_session = AsyncMock(return_value=False)
            self.mock_narrative_engine.initialize_session = AsyncMock()

            result = await self.manager.create_session(
                self.test_player_id,
                self.test_character_id,
                self.test_world_id,
                self.test_settings,
            )

            # Verify None is returned on failure
            self.assertIsNone(result)

            # Test operations on non-existent session
            result = await self.manager.pause_session("non_existent_player")
            self.assertFalse(result)

            # Mock get_player_active_sessions to return empty list (no active sessions)
            self.mock_repository.get_player_active_sessions = AsyncMock(return_value=[])

            result = await self.manager.update_session_interaction(
                "non_existent_player", {"test": "data"}
            )
            self.assertFalse(result)

            result = await self.manager.add_progress_marker(
                "non_existent_player",
                ProgressMarker(
                    marker_id="test",
                    marker_type=ProgressMarkerType.MILESTONE,
                    description="Test",
                    achieved_at=datetime.now(),
                ),
            )
            self.assertFalse(result)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
