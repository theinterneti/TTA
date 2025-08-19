"""
Integration tests for SessionIntegrationManager with InteractiveNarrativeEngine.

Tests the integration between session management and narrative engine
to ensure session continuity works correctly.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

from src.player_experience.models.session import (
    SessionContext, TherapeuticSettings
)
from src.player_experience.models.enums import (
    SessionStatus, TherapeuticApproach
)
from src.player_experience.managers.session_integration_manager import SessionIntegrationManager


class MockInteractiveNarrativeEngine:
    """Mock Interactive Narrative Engine for testing."""
    
    def __init__(self):
        self.initialized_sessions = {}
        self.session_states = {}
        self.finalized_sessions = set()
        self.therapeutic_settings = {}
    
    async def initialize_session(self, session_id: str, character_id: str, world_id: str, therapeutic_settings):
        """Mock session initialization."""
        self.initialized_sessions[session_id] = {
            'character_id': character_id,
            'world_id': world_id,
            'therapeutic_settings': therapeutic_settings
        }
    
    async def get_session_state(self, session_id: str):
        """Mock getting session state."""
        return self.session_states.get(session_id, {
            'narrative_position': 5,
            'current_scene': 'test_scene',
            'character_states': {'char1': {'mood': 'happy'}}
        })
    
    async def restore_session_state(self, session_id: str, narrative_state):
        """Mock restoring session state."""
        self.session_states[session_id] = narrative_state
    
    async def finalize_session(self, session_id: str):
        """Mock session finalization."""
        self.finalized_sessions.add(session_id)
    
    async def update_therapeutic_settings(self, session_id: str, therapeutic_settings):
        """Mock updating therapeutic settings."""
        self.therapeutic_settings[session_id] = therapeutic_settings


class TestSessionNarrativeIntegration(unittest.TestCase):
    """Test integration between SessionIntegrationManager and InteractiveNarrativeEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = AsyncMock()
        self.mock_narrative_engine = MockInteractiveNarrativeEngine()
        
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

    def test_session_creation_with_narrative_initialization(self):
        """Test that session creation properly initializes narrative engine."""
        async def run_test():
            # Mock successful repository creation
            self.mock_repository.create_session = AsyncMock(return_value=True)
            
            # Create session
            result = await self.manager.create_session(
                self.test_player_id,
                self.test_character_id,
                self.test_world_id,
                self.test_settings
            )
            
            # Verify session was created
            self.assertIsNotNone(result)
            self.assertEqual(result.player_id, self.test_player_id)
            
            # Verify narrative engine was initialized
            self.assertIn(result.session_id, self.mock_narrative_engine.initialized_sessions)
            init_data = self.mock_narrative_engine.initialized_sessions[result.session_id]
            self.assertEqual(init_data['character_id'], self.test_character_id)
            self.assertEqual(init_data['world_id'], self.test_world_id)
            self.assertEqual(init_data['therapeutic_settings'], self.test_settings)
        
        asyncio.run(run_test())

    def test_session_pause_and_resume_with_state_preservation(self):
        """Test session pause and resume with narrative state preservation."""
        async def run_test():
            # Create and set up session
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings
            )
            
            self.manager._active_sessions[self.test_player_id] = session
            
            # Mock repository operations
            self.mock_repository.pause_session = AsyncMock(return_value=True)
            self.mock_repository.get_session = AsyncMock(return_value=session)
            self.mock_repository.resume_session = AsyncMock(return_value=True)
            
            # Test pausing session
            pause_result = await self.manager.pause_session(self.test_player_id)
            self.assertTrue(pause_result)
            
            # Verify narrative state was preserved
            self.assertIn('narrative_state', session.session_variables)
            preserved_state = session.session_variables['narrative_state']
            self.assertEqual(preserved_state['narrative_position'], 5)
            self.assertEqual(preserved_state['current_scene'], 'test_scene')
            
            # Update session status for resume test
            session.status = SessionStatus.PAUSED
            
            # Test resuming session
            resume_result = await self.manager.resume_session("test_session")
            self.assertIsNotNone(resume_result)
            self.assertEqual(resume_result.status, SessionStatus.ACTIVE)
            
            # Verify narrative state was restored
            self.assertIn("test_session", self.mock_narrative_engine.session_states)
            restored_state = self.mock_narrative_engine.session_states["test_session"]
            self.assertEqual(restored_state['narrative_position'], 5)
        
        asyncio.run(run_test())

    def test_session_ending_with_narrative_finalization(self):
        """Test session ending with proper narrative finalization."""
        async def run_test():
            # Create and set up session
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings
            )
            
            self.manager._active_sessions[self.test_player_id] = session
            
            # Mock repository operations
            self.mock_repository.end_session = AsyncMock(return_value=True)
            
            # Test ending session
            result = await self.manager.end_session(self.test_player_id)
            self.assertTrue(result)
            
            # Verify session was finalized in narrative engine
            self.assertIn("test_session", self.mock_narrative_engine.finalized_sessions)
            
            # Verify session was removed from active sessions
            self.assertNotIn(self.test_player_id, self.manager._active_sessions)
            
            # Verify session status was updated
            self.assertEqual(session.status, SessionStatus.COMPLETED)
        
        asyncio.run(run_test())

    def test_therapeutic_settings_update_with_narrative_engine(self):
        """Test therapeutic settings update propagates to narrative engine."""
        async def run_test():
            # Create and set up session
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings
            )
            
            self.manager._active_sessions[self.test_player_id] = session
            
            # Mock repository operations
            self.mock_repository.update_session = AsyncMock(return_value=True)
            
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
            
            # Verify settings were updated in session
            self.assertEqual(session.therapeutic_settings.intensity_level, 0.8)
            
            # Verify settings were updated in narrative engine
            self.assertIn("test_session", self.mock_narrative_engine.therapeutic_settings)
            engine_settings = self.mock_narrative_engine.therapeutic_settings["test_session"]
            self.assertEqual(engine_settings.intensity_level, 0.8)
            self.assertEqual(engine_settings.preferred_approaches[0], TherapeuticApproach.MINDFULNESS)
        
        asyncio.run(run_test())

    def test_context_switching_with_narrative_continuity(self):
        """Test character-world context switching maintains narrative continuity."""
        async def run_test():
            # Create current session
            current_session = SessionContext(
                session_id="current_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings
            )
            
            self.manager._active_sessions[self.test_player_id] = current_session
            
            # Mock repository operations
            self.mock_repository.get_player_active_sessions = AsyncMock(return_value=[])
            self.mock_repository.pause_session = AsyncMock(return_value=True)
            self.mock_repository.create_session = AsyncMock(return_value=True)
            
            # Test context switching
            result = await self.manager.switch_character_world_context(
                self.test_player_id,
                "new_char_456",
                "new_world_456"
            )
            
            # Verify new session was created
            self.assertIsNotNone(result)
            self.assertEqual(result.character_id, "new_char_456")
            self.assertEqual(result.world_id, "new_world_456")
            
            # Verify current session was paused and state preserved
            self.assertIn('narrative_state', current_session.session_variables)
            
            # Verify new session was initialized in narrative engine
            self.assertIn(result.session_id, self.mock_narrative_engine.initialized_sessions)
            init_data = self.mock_narrative_engine.initialized_sessions[result.session_id]
            self.assertEqual(init_data['character_id'], "new_char_456")
            self.assertEqual(init_data['world_id'], "new_world_456")
            
            # Verify therapeutic settings were preserved
            self.assertEqual(result.therapeutic_settings.intensity_level, 0.6)
        
        asyncio.run(run_test())

    def test_session_continuity_data_includes_narrative_state(self):
        """Test that session continuity data includes narrative state information."""
        async def run_test():
            # Create session with narrative state
            session = SessionContext(
                session_id="test_session",
                player_id=self.test_player_id,
                character_id=self.test_character_id,
                world_id=self.test_world_id,
                therapeutic_settings=self.test_settings
            )
            
            # Add narrative state to session variables
            session.session_variables = {
                'narrative_state': {
                    'narrative_position': 10,
                    'current_scene': 'important_scene',
                    'character_states': {'char1': {'mood': 'determined'}}
                },
                'other_data': 'test'
            }
            
            # Mock repository
            self.mock_repository.get_session = AsyncMock(return_value=session)
            
            # Get continuity data
            result = await self.manager.get_session_continuity_data("test_session")
            
            # Verify continuity data includes narrative information
            self.assertIn('session_variables', result)
            self.assertIn('narrative_state', result['session_variables'])
            
            narrative_state = result['session_variables']['narrative_state']
            self.assertEqual(narrative_state['narrative_position'], 10)
            self.assertEqual(narrative_state['current_scene'], 'important_scene')
            self.assertIn('char1', narrative_state['character_states'])
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()