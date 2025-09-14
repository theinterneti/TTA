"""
Integration tests for Prototype Component

This module contains comprehensive tests for the PrototypeComponent class,
covering component lifecycle, TTA orchestration integration, and therapeutic session management.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tta.prototype.components.prototype_component import PrototypeComponent


class TestPrototypeComponent(unittest.TestCase):
    """Test cases for PrototypeComponent."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.get.return_value = {
            "redis": {"host": "localhost", "port": 6379, "db": 0},
            "neo4j": {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"}
        }

        self.component = PrototypeComponent(self.mock_config)

    def test_component_initialization(self):
        """Test component initialization."""
        self.assertEqual(self.component.name, "tta_prototype")
        self.assertEqual(self.component.dependencies, ["neo4j", "redis"])
        self.assertIsNone(self.component.narrative_engine)
        self.assertIsNone(self.component.redis_cache)
        self.assertIsNone(self.component.neo4j_manager)
        self.assertEqual(len(self.component.active_sessions), 0)

    def test_component_start_success(self):
        """Test successful component start."""
        # Mock the initialization methods
        with patch.object(self.component, '_initialize_databases', return_value=True), \
             patch.object(self.component, '_initialize_narrative_engine', return_value=True), \
             patch.object(self.component, '_perform_health_checks', return_value=True):

            success = self.component._start_impl()
            self.assertTrue(success)

    def test_component_start_database_failure(self):
        """Test component start with database initialization failure."""
        with patch.object(self.component, '_initialize_databases', return_value=False):
            success = self.component._start_impl()
            self.assertFalse(success)

    def test_component_start_narrative_engine_failure(self):
        """Test component start with narrative engine initialization failure."""
        with patch.object(self.component, '_initialize_databases', return_value=True), \
             patch.object(self.component, '_initialize_narrative_engine', return_value=False):

            success = self.component._start_impl()
            self.assertFalse(success)

    def test_component_stop_success(self):
        """Test successful component stop."""
        # Set up some mock state
        self.component.narrative_engine = Mock()
        self.component.narrative_engine.cleanup_inactive_sessions.return_value = 2
        self.component.redis_cache = Mock()
        self.component.neo4j_manager = Mock()
        self.component.active_sessions["test_session"] = {"user_id": "test_user"}

        with patch.object(self.component, '_cleanup_active_sessions'), \
             patch.object(self.component, '_close_database_connections'):

            success = self.component._stop_impl()
            self.assertTrue(success)
            self.assertIsNone(self.component.narrative_engine)
            self.assertIsNone(self.component.redis_cache)
            self.assertIsNone(self.component.neo4j_manager)
            self.assertEqual(len(self.component.active_sessions), 0)

    def test_database_initialization(self):
        """Test database initialization."""
        # Mock the database classes
        with patch('tta.prototype.components.prototype_component.RedisCache') as mock_redis, \
             patch('tta.prototype.components.prototype_component.Neo4jManager') as mock_neo4j:

            mock_redis_instance = Mock()
            mock_neo4j_instance = Mock()
            mock_redis.return_value = mock_redis_instance
            mock_neo4j.return_value = mock_neo4j_instance

            success = self.component._initialize_databases()

            self.assertTrue(success)
            self.assertEqual(self.component.redis_cache, mock_redis_instance)
            self.assertEqual(self.component.neo4j_manager, mock_neo4j_instance)
            self.assertEqual(self.component.component_health["redis"], "healthy")
            self.assertEqual(self.component.component_health["neo4j"], "healthy")

    def test_narrative_engine_initialization(self):
        """Test narrative engine initialization."""
        with patch('tta.prototype.components.prototype_component.InteractiveNarrativeEngine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine.return_value = mock_engine_instance

            success = self.component._initialize_narrative_engine()

            self.assertTrue(success)
            self.assertEqual(self.component.narrative_engine, mock_engine_instance)
            self.assertEqual(self.component.component_health["narrative_engine"], "healthy")

    def test_health_checks(self):
        """Test health check functionality."""
        # Set up mock narrative engine
        mock_engine = Mock()
        mock_session = Mock()
        mock_session.session_id = "health_check_session"
        mock_engine.start_session.return_value = mock_session
        mock_engine.end_session.return_value = True

        self.component.narrative_engine = mock_engine
        self.component.redis_cache = Mock()
        self.component.neo4j_manager = Mock()

        success = self.component._perform_health_checks()

        self.assertTrue(success)
        self.assertEqual(self.component.component_health["narrative_engine"], "healthy")
        self.assertEqual(self.component.component_health["redis"], "healthy")
        self.assertEqual(self.component.component_health["neo4j"], "healthy")

        # Verify health check session was created and ended
        mock_engine.start_session.assert_called_once_with("health_check_user", "health_check")
        mock_engine.end_session.assert_called_once_with("health_check_session")

    def test_get_component_status(self):
        """Test component status retrieval."""
        # Set up component state
        self.component.narrative_engine = Mock()
        self.component.redis_cache = Mock()
        self.component.neo4j_manager = Mock()
        self.component.component_health = {"narrative_engine": "healthy", "redis": "healthy", "neo4j": "healthy"}
        self.component.active_sessions = {"session1": {}, "session2": {}}

        status = self.component.get_component_status()

        self.assertEqual(status["name"], "tta_prototype")
        self.assertEqual(status["dependencies"], ["neo4j", "redis"])
        self.assertEqual(status["active_sessions"], 2)
        self.assertTrue(status["narrative_engine_available"])
        self.assertTrue(status["redis_cache_available"])
        self.assertTrue(status["neo4j_manager_available"])
        self.assertEqual(status["component_health"], self.component.component_health)

    def test_create_therapeutic_session_success(self):
        """Test successful therapeutic session creation."""
        # Set up mock narrative engine
        mock_engine = Mock()
        mock_session = Mock()
        mock_session.session_id = "test_session_123"
        mock_session.created_at = "2023-01-01T00:00:00"
        mock_session.last_updated = "2023-01-01T00:00:00"
        mock_engine.start_session.return_value = mock_session

        self.component.narrative_engine = mock_engine

        session_id = self.component.create_therapeutic_session("test_user", "test_scenario")

        self.assertEqual(session_id, "test_session_123")
        self.assertIn("test_session_123", self.component.active_sessions)
        self.assertEqual(self.component.active_sessions["test_session_123"]["user_id"], "test_user")
        self.assertEqual(self.component.active_sessions["test_session_123"]["scenario_id"], "test_scenario")

        mock_engine.start_session.assert_called_once_with("test_user", "test_scenario")

    def test_create_therapeutic_session_no_engine(self):
        """Test therapeutic session creation without narrative engine."""
        self.component.narrative_engine = None

        session_id = self.component.create_therapeutic_session("test_user", "test_scenario")

        self.assertIsNone(session_id)
        self.assertEqual(len(self.component.active_sessions), 0)

    def test_process_user_interaction_success(self):
        """Test successful user interaction processing."""
        # Set up mock narrative engine and response
        mock_engine = Mock()
        mock_response = Mock()
        mock_response.content = "Test response content"
        mock_response.response_type = "narrative"
        mock_response.choices = [{"id": "choice1", "text": "Choice 1"}]
        mock_response.metadata = {"therapeutic_value": 0.7}
        mock_response.session_id = "test_session"
        mock_response.timestamp = Mock()
        mock_response.timestamp.isoformat.return_value = "2023-01-01T00:00:00"

        mock_engine.process_user_choice.return_value = mock_response
        self.component.narrative_engine = mock_engine

        # Set up active session
        self.component.active_sessions["test_session"] = {"user_id": "test_user"}

        with patch('tta.prototype.components.prototype_component.UserChoice') as mock_choice_class:
            mock_choice = Mock()
            mock_choice_class.return_value = mock_choice

            result = self.component.process_user_interaction("test_session", "Hello, I need help")

            self.assertIsNotNone(result)
            self.assertEqual(result["content"], "Test response content")
            self.assertEqual(result["response_type"], "narrative")
            self.assertEqual(result["choices"], [{"id": "choice1", "text": "Choice 1"}])
            self.assertEqual(result["metadata"], {"therapeutic_value": 0.7})

            # Check that interaction was recorded
            self.assertIn("interactions", self.component.active_sessions["test_session"])
            interactions = self.component.active_sessions["test_session"]["interactions"]
            self.assertEqual(len(interactions), 1)
            self.assertEqual(interactions[0]["user_input"], "Hello, I need help")
            self.assertEqual(interactions[0]["therapeutic_value"], 0.7)

    def test_process_user_interaction_no_engine(self):
        """Test user interaction processing without narrative engine."""
        self.component.narrative_engine = None

        result = self.component.process_user_interaction("test_session", "Hello")

        self.assertIsNone(result)

    def test_end_therapeutic_session_success(self):
        """Test successful therapeutic session termination."""
        # Set up mock narrative engine
        mock_engine = Mock()
        mock_engine.end_session.return_value = True
        self.component.narrative_engine = mock_engine

        # Set up active session
        self.component.active_sessions["test_session"] = {"user_id": "test_user"}

        success = self.component.end_therapeutic_session("test_session")

        self.assertTrue(success)
        self.assertNotIn("test_session", self.component.active_sessions)
        mock_engine.end_session.assert_called_once_with("test_session")

    def test_end_therapeutic_session_no_engine(self):
        """Test therapeutic session termination without narrative engine."""
        self.component.narrative_engine = None

        success = self.component.end_therapeutic_session("test_session")

        self.assertFalse(success)

    def test_get_session_info_success(self):
        """Test successful session info retrieval."""
        # Set up active session
        self.component.active_sessions["test_session"] = {
            "user_id": "test_user",
            "scenario_id": "test_scenario",
            "created_at": "2023-01-01T00:00:00"
        }

        # Set up mock narrative engine
        mock_engine = Mock()
        mock_scenario = {"narrative_position": 5, "location": "garden"}
        mock_engine.get_current_scenario.return_value = mock_scenario
        self.component.narrative_engine = mock_engine

        session_info = self.component.get_session_info("test_session")

        self.assertIsNotNone(session_info)
        self.assertEqual(session_info["user_id"], "test_user")
        self.assertEqual(session_info["scenario_id"], "test_scenario")
        self.assertEqual(session_info["current_scenario"], mock_scenario)

    def test_get_session_info_not_found(self):
        """Test session info retrieval for non-existent session."""
        session_info = self.component.get_session_info("non_existent_session")

        self.assertIsNone(session_info)

    def test_get_health_status_healthy(self):
        """Test health status when all components are healthy."""
        self.component.component_health = {
            "narrative_engine": "healthy",
            "redis": "healthy",
            "neo4j": "healthy"
        }
        self.component.active_sessions = {"session1": {}, "session2": {}}

        with patch.object(self.component, '_check_dependencies', return_value=True):
            health_status = self.component.get_health_status()

            self.assertEqual(health_status["overall_health"], "healthy")
            self.assertEqual(health_status["active_sessions"], 2)
            self.assertTrue(health_status["dependencies_met"])

    def test_get_health_status_degraded(self):
        """Test health status when some components are degraded."""
        self.component.component_health = {
            "narrative_engine": "healthy",
            "redis": "degraded",
            "neo4j": "healthy"
        }

        with patch.object(self.component, '_check_dependencies', return_value=True):
            health_status = self.component.get_health_status()

            self.assertEqual(health_status["overall_health"], "degraded")

    def test_get_health_status_error(self):
        """Test health status when some components have errors."""
        self.component.component_health = {
            "narrative_engine": "error",
            "redis": "healthy",
            "neo4j": "healthy"
        }

        with patch.object(self.component, '_check_dependencies', return_value=False):
            health_status = self.component.get_health_status()

            self.assertEqual(health_status["overall_health"], "error")
            self.assertFalse(health_status["dependencies_met"])

    def test_cleanup_active_sessions(self):
        """Test active session cleanup."""
        # Set up mock narrative engine
        mock_engine = Mock()
        mock_engine.get_active_session_count.return_value = 3
        mock_engine.cleanup_inactive_sessions.return_value = 2
        self.component.narrative_engine = mock_engine

        # Set up active sessions
        self.component.active_sessions = {
            "session1": {"user_id": "user1"},
            "session2": {"user_id": "user2"}
        }

        self.component._cleanup_active_sessions()

        self.assertEqual(len(self.component.active_sessions), 0)
        mock_engine.cleanup_inactive_sessions.assert_called_once_with(max_age_hours=0)

    def test_close_database_connections(self):
        """Test database connection closure."""
        # Set up mock database connections
        mock_redis = Mock()
        mock_neo4j = Mock()
        self.component.redis_cache = mock_redis
        self.component.neo4j_manager = mock_neo4j

        self.component._close_database_connections()

        # Verify close methods were called if they exist
        if hasattr(mock_redis, 'close'):
            mock_redis.close.assert_called_once()
        if hasattr(mock_neo4j, 'close'):
            mock_neo4j.close.assert_called_once()

    def test_check_dependencies(self):
        """Test dependency checking."""
        # Test with healthy dependencies
        self.component.component_health = {
            "neo4j": "healthy",
            "redis": "healthy"
        }
        self.assertTrue(self.component._check_dependencies())

        # Test with degraded dependencies
        self.component.component_health = {
            "neo4j": "degraded",
            "redis": "healthy"
        }
        self.assertTrue(self.component._check_dependencies())

        # Test with error dependencies
        self.component.component_health = {
            "neo4j": "error",
            "redis": "healthy"
        }
        self.assertFalse(self.component._check_dependencies())


if __name__ == '__main__':
    unittest.main()
