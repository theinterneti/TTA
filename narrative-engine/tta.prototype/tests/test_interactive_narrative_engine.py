"""
Unit tests for Interactive Narrative Engine

This module contains comprehensive unit tests for the InteractiveNarrativeEngine class,
covering session management, narrative flow control, and integration with LangGraph.
"""

# Import the classes to test
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tta.prototype.core.interactive_narrative_engine import (
    InteractiveNarrativeEngine,
    NarrativeEvent,
    NarrativeResponse,
    UserChoice,
)
from tta.prototype.models.data_models import SessionState


class TestInteractiveNarrativeEngine(unittest.TestCase):
    """Test cases for InteractiveNarrativeEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_redis_cache = Mock()
        self.mock_neo4j_manager = Mock()

        # Create engine instance
        self.engine = InteractiveNarrativeEngine(
            redis_cache=self.mock_redis_cache,
            neo4j_manager=self.mock_neo4j_manager
        )

        # Test data
        self.test_user_id = "test_user_123"
        self.test_scenario_id = "test_scenario"

    def test_start_session_success(self):
        """Test successful session creation."""
        # Act
        session_state = self.engine.start_session(self.test_user_id, self.test_scenario_id)

        # Assert
        self.assertIsNotNone(session_state)
        self.assertEqual(session_state.user_id, self.test_user_id)
        self.assertEqual(session_state.current_scenario_id, self.test_scenario_id)
        self.assertEqual(session_state.narrative_position, 0)
        self.assertIsNotNone(session_state.session_id)
        self.assertIsNotNone(session_state.narrative_context)
        self.assertIsNotNone(session_state.therapeutic_progress)
        self.assertIsNotNone(session_state.emotional_state)

        # Check that session is stored in active sessions
        self.assertIn(session_state.session_id, self.engine.active_sessions)

        # Check that Redis cache was called
        self.mock_redis_cache.set_session_state.assert_called_once()

    def test_start_session_empty_user_id(self):
        """Test session creation with empty user ID."""
        with self.assertRaises(ValueError) as context:
            self.engine.start_session("")

        self.assertIn("User ID cannot be empty", str(context.exception))

    def test_start_session_none_user_id(self):
        """Test session creation with None user ID."""
        with self.assertRaises(ValueError) as context:
            self.engine.start_session(None)

        self.assertIn("User ID cannot be empty", str(context.exception))

    def test_get_session_from_active(self):
        """Test retrieving session from active sessions."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        # Act
        retrieved_session = self.engine.get_session(session_id)

        # Assert
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session_id)
        self.assertEqual(retrieved_session.user_id, self.test_user_id)

    def test_get_session_from_redis_cache(self):
        """Test retrieving session from Redis cache."""
        # Arrange
        session_id = str(uuid.uuid4())
        cached_session = SessionState(session_id=session_id, user_id=self.test_user_id)
        self.mock_redis_cache.get_session_state.return_value = cached_session

        # Act
        retrieved_session = self.engine.get_session(session_id)

        # Assert
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session_id)
        self.assertEqual(retrieved_session.user_id, self.test_user_id)

        # Check that session is now in active sessions
        self.assertIn(session_id, self.engine.active_sessions)

        # Check that Redis was called
        self.mock_redis_cache.get_session_state.assert_called_once_with(session_id)

    def test_get_session_not_found(self):
        """Test retrieving non-existent session."""
        # Arrange
        non_existent_id = str(uuid.uuid4())
        self.mock_redis_cache.get_session_state.return_value = None

        # Act
        retrieved_session = self.engine.get_session(non_existent_id)

        # Assert
        self.assertIsNone(retrieved_session)

    def test_process_user_choice_success(self):
        """Test successful user choice processing."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        choice = UserChoice(
            choice_id="test_choice",
            choice_text="look around",
            choice_type="action"
        )

        # Act
        response = self.engine.process_user_choice(session_id, choice)

        # Assert
        self.assertIsInstance(response, NarrativeResponse)
        self.assertIsNotNone(response.content)
        self.assertEqual(response.session_id, session_id)
        self.assertGreater(len(response.content), 0)

        # Check that narrative position was incremented
        updated_session = self.engine.get_session(session_id)
        self.assertEqual(updated_session.narrative_position, 1)

    def test_process_user_choice_invalid_session(self):
        """Test processing choice with invalid session ID."""
        # Arrange
        invalid_session_id = str(uuid.uuid4())
        choice = UserChoice(choice_id="test", choice_text="test")

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.engine.process_user_choice(invalid_session_id, choice)

        self.assertIn("Session", str(context.exception))
        self.assertIn("not found", str(context.exception))

    def test_process_user_choice_empty_text(self):
        """Test processing choice with empty text."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        choice = UserChoice(choice_id="test", choice_text="")

        # Act
        response = self.engine.process_user_choice(session_id, choice)

        # Assert
        self.assertEqual(response.response_type, "error")
        self.assertIn("didn't understand", response.content)

    def test_process_choice_fallback_look_command(self):
        """Test fallback processing for look command."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        choice = UserChoice(choice_id="look", choice_text="look")

        # Act
        response = self.engine.process_user_choice(session_id, choice)

        # Assert
        self.assertIn("look around", response.content.lower())
        self.assertGreater(len(response.choices), 0)
        self.assertEqual(response.response_type, "narrative")

    def test_process_choice_fallback_help_command(self):
        """Test fallback processing for help command."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        choice = UserChoice(choice_id="help", choice_text="help")

        # Act
        response = self.engine.process_user_choice(session_id, choice)

        # Assert
        self.assertIn("can", response.content.lower())
        self.assertGreater(len(response.choices), 0)
        self.assertEqual(response.response_type, "narrative")

    def test_get_current_scenario(self):
        """Test getting current scenario state."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id, self.test_scenario_id)
        session_id = session_state.session_id

        # Act
        scenario = self.engine.get_current_scenario(session_id)

        # Assert
        self.assertIsNotNone(scenario)
        self.assertEqual(scenario["session_id"], session_id)
        self.assertEqual(scenario["scenario_id"], self.test_scenario_id)
        self.assertEqual(scenario["narrative_position"], 0)
        self.assertIn("therapeutic_progress", scenario)
        self.assertIn("emotional_state", scenario)

    def test_get_current_scenario_invalid_session(self):
        """Test getting scenario for invalid session."""
        # Arrange
        invalid_session_id = str(uuid.uuid4())

        # Act
        scenario = self.engine.get_current_scenario(invalid_session_id)

        # Assert
        self.assertIsNone(scenario)

    def test_advance_narrative_success(self):
        """Test successful narrative advancement."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        event = NarrativeEvent(
            event_id="test_event",
            event_type="location_change",
            description="Player moved to new area",
            location_id="new_location"
        )

        # Act
        success = self.engine.advance_narrative(session_id, event)

        # Assert
        self.assertTrue(success)

        # Check that session was updated
        updated_session = self.engine.get_session(session_id)
        self.assertEqual(updated_session.narrative_position, 1)
        self.assertEqual(updated_session.current_location_id, "new_location")
        self.assertIn(event.description, updated_session.narrative_context.recent_events)

    def test_advance_narrative_invalid_session(self):
        """Test narrative advancement with invalid session."""
        # Arrange
        invalid_session_id = str(uuid.uuid4())
        event = NarrativeEvent(event_id="test", event_type="test", description="test")

        # Act
        success = self.engine.advance_narrative(invalid_session_id, event)

        # Assert
        self.assertFalse(success)

    def test_end_session_success(self):
        """Test successful session termination."""
        # Arrange
        session_state = self.engine.start_session(self.test_user_id)
        session_id = session_state.session_id

        # Verify session exists
        self.assertIn(session_id, self.engine.active_sessions)

        # Act
        success = self.engine.end_session(session_id)

        # Assert
        self.assertTrue(success)
        self.assertNotIn(session_id, self.engine.active_sessions)

    def test_end_session_nonexistent(self):
        """Test ending non-existent session."""
        # Arrange
        non_existent_id = str(uuid.uuid4())

        # Act
        success = self.engine.end_session(non_existent_id)

        # Assert
        self.assertTrue(success)  # Should succeed even if session doesn't exist

    def test_get_active_session_count(self):
        """Test getting active session count."""
        # Arrange
        initial_count = self.engine.get_active_session_count()

        # Create some sessions
        session1 = self.engine.start_session("user1")
        self.engine.start_session("user2")

        # Act
        count_after_creation = self.engine.get_active_session_count()

        # End one session
        self.engine.end_session(session1.session_id)
        count_after_ending = self.engine.get_active_session_count()

        # Assert
        self.assertEqual(count_after_creation, initial_count + 2)
        self.assertEqual(count_after_ending, initial_count + 1)

    def test_cleanup_inactive_sessions(self):
        """Test cleanup of inactive sessions."""
        # Arrange
        session1 = self.engine.start_session("user1")
        session2 = self.engine.start_session("user2")

        # Make session1 appear old
        old_time = datetime.now() - timedelta(hours=25)
        session1.last_updated = old_time
        self.engine.active_sessions[session1.session_id] = session1

        # Act
        cleaned_count = self.engine.cleanup_inactive_sessions(max_age_hours=24)

        # Assert
        self.assertEqual(cleaned_count, 1)
        self.assertNotIn(session1.session_id, self.engine.active_sessions)
        self.assertIn(session2.session_id, self.engine.active_sessions)

    @patch('tta.prototype.core.interactive_narrative_engine.create_workflow')
    def test_langgraph_integration_success(self, mock_create_workflow):
        """Test successful LangGraph integration."""
        # Arrange
        mock_workflow = Mock()
        mock_tools = Mock()
        mock_create_workflow.return_value = (mock_workflow, mock_tools)

        # Mock agent state response
        mock_agent_state = Mock()
        mock_agent_state.response = "You look around the peaceful garden."
        mock_agent_state.current_agent = "nga"
        mock_agent_state.parsed_input = {"intent": "look"}
        mock_agent_state.turn_count = 1
        mock_workflow.return_value = mock_agent_state

        # Create engine with mocked LangGraph
        engine = InteractiveNarrativeEngine(neo4j_manager=self.mock_neo4j_manager)
        engine.langgraph_workflow = mock_workflow
        engine.langgraph_tools = mock_tools

        # Create session and choice
        session_state = engine.start_session(self.test_user_id)
        choice = UserChoice(choice_id="look", choice_text="look around")

        # Act
        response = engine.process_user_choice(session_state.session_id, choice)

        # Assert
        self.assertEqual(response.content, "You look around the peaceful garden.")
        self.assertEqual(response.response_type, "narrative")
        self.assertIn("agent_state", response.metadata)
        mock_workflow.assert_called_once_with("look around", "starting_location")

    def test_redis_cache_error_handling(self):
        """Test handling of Redis cache errors."""
        # Arrange
        self.mock_redis_cache.set_session_state.side_effect = Exception("Redis error")

        # Act - should not raise exception
        session_state = self.engine.start_session(self.test_user_id)

        # Assert - session should still be created
        self.assertIsNotNone(session_state)
        self.assertIn(session_state.session_id, self.engine.active_sessions)


class TestUserChoice(unittest.TestCase):
    """Test cases for UserChoice dataclass."""

    def test_user_choice_creation(self):
        """Test UserChoice creation with all fields."""
        choice = UserChoice(
            choice_id="test_id",
            choice_text="test text",
            choice_type="dialogue",
            metadata={"key": "value"}
        )

        self.assertEqual(choice.choice_id, "test_id")
        self.assertEqual(choice.choice_text, "test text")
        self.assertEqual(choice.choice_type, "dialogue")
        self.assertEqual(choice.metadata["key"], "value")
        self.assertIsInstance(choice.timestamp, datetime)

    def test_user_choice_defaults(self):
        """Test UserChoice creation with default values."""
        choice = UserChoice(choice_id="test", choice_text="test")

        self.assertEqual(choice.choice_type, "dialogue")
        self.assertIsInstance(choice.metadata, dict)
        self.assertIsInstance(choice.timestamp, datetime)


class TestNarrativeEvent(unittest.TestCase):
    """Test cases for NarrativeEvent dataclass."""

    def test_narrative_event_creation(self):
        """Test NarrativeEvent creation with all fields."""
        event = NarrativeEvent(
            event_id="test_event",
            event_type="test_type",
            description="test description",
            participants=["user", "character"],
            location_id="test_location",
            metadata={"key": "value"}
        )

        self.assertEqual(event.event_id, "test_event")
        self.assertEqual(event.event_type, "test_type")
        self.assertEqual(event.description, "test description")
        self.assertEqual(event.participants, ["user", "character"])
        self.assertEqual(event.location_id, "test_location")
        self.assertEqual(event.metadata["key"], "value")
        self.assertIsInstance(event.timestamp, datetime)

    def test_narrative_event_defaults(self):
        """Test NarrativeEvent creation with default values."""
        event = NarrativeEvent(
            event_id="test",
            event_type="test",
            description="test"
        )

        self.assertIsInstance(event.participants, list)
        self.assertEqual(event.location_id, "")
        self.assertIsInstance(event.metadata, dict)
        self.assertIsInstance(event.timestamp, datetime)


class TestNarrativeResponse(unittest.TestCase):
    """Test cases for NarrativeResponse dataclass."""

    def test_narrative_response_creation(self):
        """Test NarrativeResponse creation with all fields."""
        choices = [{"id": "1", "text": "Choice 1"}]
        response = NarrativeResponse(
            content="test content",
            response_type="narrative",
            choices=choices,
            metadata={"key": "value"},
            session_id="test_session"
        )

        self.assertEqual(response.content, "test content")
        self.assertEqual(response.response_type, "narrative")
        self.assertEqual(response.choices, choices)
        self.assertEqual(response.metadata["key"], "value")
        self.assertEqual(response.session_id, "test_session")
        self.assertIsInstance(response.timestamp, datetime)

    def test_narrative_response_defaults(self):
        """Test NarrativeResponse creation with default values."""
        response = NarrativeResponse(content="test")

        self.assertEqual(response.response_type, "narrative")
        self.assertIsInstance(response.choices, list)
        self.assertIsInstance(response.metadata, dict)
        self.assertEqual(response.session_id, "")
        self.assertIsInstance(response.timestamp, datetime)


if __name__ == '__main__':
    unittest.main()
