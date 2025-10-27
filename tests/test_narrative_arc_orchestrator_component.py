"""
Tests for Narrative Arc Orchestrator Component

This module contains unit tests for the NarrativeArcOrchestratorComponent
to verify its functionality and integration with the TTA component system.
"""

import unittest
from datetime import datetime

from tta_narrative.orchestration_component import (
    EmergentEvent,
    NarrativeArcOrchestratorComponent,
    NarrativeResponse,
    NarrativeScale,
    NarrativeStatus,
    PlayerChoice,
)
from src.orchestration import TTAConfig


class TestNarrativeArcOrchestratorComponent(unittest.TestCase):
    """Test cases for NarrativeArcOrchestratorComponent."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = TTAConfig()
        self.component = NarrativeArcOrchestratorComponent(self.config)

    def test_component_initialization(self):
        """Test component initialization."""
        self.assertEqual(self.component.name, "narrative_arc_orchestrator")
        self.assertEqual(
            self.component.dependencies,
            ["neo4j", "redis", "interactive_narrative_engine"],
        )
        self.assertEqual(self.component.port, 8502)
        self.assertEqual(self.component.max_concurrent_sessions, 100)

    def test_component_configuration(self):
        """Test component configuration loading."""
        self.assertEqual(self.component.short_term_window, 300)
        self.assertEqual(self.component.medium_term_window, 86400)
        self.assertEqual(self.component.long_term_window, 2592000)
        self.assertEqual(self.component.epic_term_window, 31536000)
        self.assertEqual(self.component.safety_check_interval, 60)
        self.assertEqual(self.component.therapeutic_weight, 0.3)
        self.assertEqual(self.component.probability_threshold, 0.7)
        self.assertEqual(self.component.complexity_limit, 5)

    def test_component_start_stop(self):
        """Test component start and stop functionality."""
        # Test start
        result = self.component.start()
        self.assertTrue(result)
        self.assertEqual(self.component.status.value, "running")

        # Test stop
        result = self.component.stop()
        self.assertTrue(result)
        self.assertEqual(self.component.status.value, "stopped")

    def test_player_choice_creation(self):
        """Test PlayerChoice data class."""
        choice = PlayerChoice(
            choice_id="test_choice_1",
            session_id="test_session",
            choice_text="I want to explore the forest",
            choice_type="action",
        )

        self.assertEqual(choice.choice_id, "test_choice_1")
        self.assertEqual(choice.session_id, "test_session")
        self.assertEqual(choice.choice_text, "I want to explore the forest")
        self.assertEqual(choice.choice_type, "action")
        self.assertIsInstance(choice.timestamp, datetime)
        self.assertIsInstance(choice.metadata, dict)

    def test_narrative_response_creation(self):
        """Test NarrativeResponse data class."""
        response = NarrativeResponse(
            content="You venture into the mysterious forest...",
            response_type="narrative",
            session_id="test_session",
        )

        self.assertEqual(response.content, "You venture into the mysterious forest...")
        self.assertEqual(response.response_type, "narrative")
        self.assertEqual(response.session_id, "test_session")
        self.assertIsInstance(response.choices, list)
        self.assertIsInstance(response.metadata, dict)
        self.assertIsInstance(response.timestamp, datetime)

    def test_narrative_status_creation(self):
        """Test NarrativeStatus data class."""
        status = NarrativeStatus(
            session_id="test_session",
            current_scale=NarrativeScale.SHORT_TERM,
            active_threads=["thread_1", "thread_2"],
            character_arcs={"char_1": "development", "char_2": "conflict"},
            coherence_score=0.85,
            therapeutic_alignment=0.75,
        )

        self.assertEqual(status.session_id, "test_session")
        self.assertEqual(status.current_scale, NarrativeScale.SHORT_TERM)
        self.assertEqual(len(status.active_threads), 2)
        self.assertEqual(len(status.character_arcs), 2)
        self.assertEqual(status.coherence_score, 0.85)
        self.assertEqual(status.therapeutic_alignment, 0.75)

    def test_emergent_event_creation(self):
        """Test EmergentEvent data class."""
        event = EmergentEvent(
            event_id="event_1",
            event_type="character_revelation",
            description="A character reveals a secret",
            scale=NarrativeScale.MEDIUM_TERM,
            participants=["player", "npc_1"],
        )

        self.assertEqual(event.event_id, "event_1")
        self.assertEqual(event.event_type, "character_revelation")
        self.assertEqual(event.scale, NarrativeScale.MEDIUM_TERM)
        self.assertEqual(len(event.participants), 2)
        self.assertIsInstance(event.metadata, dict)
        self.assertIsInstance(event.timestamp, datetime)


class TestNarrativeArcOrchestratorAsyncMethods(unittest.IsolatedAsyncioTestCase):
    """Test cases for async methods of NarrativeArcOrchestratorComponent."""

    async def asyncSetUp(self):
        """Set up async test fixtures."""
        self.config = TTAConfig()
        self.component = NarrativeArcOrchestratorComponent(self.config)
        self.component.start()  # Start component for testing

    async def asyncTearDown(self):
        """Clean up async test fixtures."""
        self.component.stop()

    async def test_process_player_choice(self):
        """Test processing player choice."""
        choice = PlayerChoice(
            choice_id="test_choice",
            session_id="test_session",
            choice_text="I want to help the villagers",
        )

        response = await self.component.process_player_choice("test_session", choice)

        self.assertIsInstance(response, NarrativeResponse)
        self.assertEqual(response.session_id, "test_session")
        self.assertIn("You chose:", response.content)
        self.assertIsInstance(response.choices, list)
        self.assertGreater(len(response.choices), 0)

    async def test_process_invalid_choice(self):
        """Test processing invalid player choice."""
        choice = PlayerChoice(
            choice_id="invalid_choice",
            session_id="test_session",
            choice_text="",  # Empty choice text
        )

        response = await self.component.process_player_choice("test_session", choice)

        self.assertEqual(response.response_type, "error")
        self.assertIn("didn't understand", response.content)

    async def test_advance_narrative_scales(self):
        """Test advancing narrative scales."""
        # First create a session by processing a choice
        choice = PlayerChoice(
            choice_id="setup_choice",
            session_id="test_session",
            choice_text="Begin the adventure",
        )
        await self.component.process_player_choice("test_session", choice)

        # Now test scale advancement
        result = await self.component.advance_narrative_scales("test_session")
        self.assertTrue(result)

    async def test_get_narrative_status(self):
        """Test getting narrative status."""
        # First create a session by processing a choice
        choice = PlayerChoice(
            choice_id="setup_choice",
            session_id="test_session",
            choice_text="Begin the adventure",
        )
        await self.component.process_player_choice("test_session", choice)

        # Now test getting status
        status = await self.component.get_narrative_status("test_session")

        self.assertIsInstance(status, NarrativeStatus)
        self.assertEqual(status.session_id, "test_session")
        self.assertIsInstance(status.current_scale, NarrativeScale)
        self.assertIsInstance(status.active_threads, list)
        self.assertIsInstance(status.character_arcs, dict)

    async def test_get_status_nonexistent_session(self):
        """Test getting status for nonexistent session."""
        status = await self.component.get_narrative_status("nonexistent_session")
        self.assertIsNone(status)

    async def test_trigger_emergent_event(self):
        """Test triggering emergent events."""
        # First create a session
        choice = PlayerChoice(
            choice_id="setup_choice",
            session_id="test_session",
            choice_text="Begin the adventure",
        )
        await self.component.process_player_choice("test_session", choice)

        # Test emergent event triggering with high probability context
        context = {
            "recent_events": ["event1", "event2", "event3"],
            "character_interactions": 5,
            "emotional_intensity": 0.8,
        }

        event = await self.component.trigger_emergent_event("test_session", context)

        # Event may or may not be generated based on probability
        if event:
            self.assertIsInstance(event, EmergentEvent)
            self.assertIsInstance(event.scale, NarrativeScale)
            self.assertIsInstance(event.participants, list)

    async def test_emergent_event_nonexistent_session(self):
        """Test emergent event for nonexistent session."""
        context = {"test": "context"}
        event = await self.component.trigger_emergent_event(
            "nonexistent_session", context
        )
        self.assertIsNone(event)


if __name__ == "__main__":
    unittest.main()
