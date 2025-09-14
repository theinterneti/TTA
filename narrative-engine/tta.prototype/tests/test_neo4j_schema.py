"""
Integration tests for Neo4j schema operations.

This module contains tests for Neo4j schema setup, migration, and query operations.
These tests require a running Neo4j instance and will create/modify data.
"""

import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from database.migrations import DataSeeder, MigrationManager, run_migrations
    from database.neo4j_schema import (
        Neo4jConnectionError,
        Neo4jQueryHelper,
        Neo4jSchemaError,
        Neo4jSchemaManager,
        setup_neo4j_schema,
        validate_neo4j_schema,
    )
    NEO4J_AVAILABLE = True
except ImportError as e:
    print(f"Neo4j not available for testing: {e}")
    NEO4J_AVAILABLE = False

# Test configuration
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7688")
TEST_NEO4J_USERNAME = os.getenv("TEST_NEO4J_USERNAME", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "password")

logger = logging.getLogger(__name__)


@unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j package not available")
class TestNeo4jSchemaManager(unittest.TestCase):
    """Test cases for Neo4jSchemaManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema_manager = Neo4jSchemaManager(
            uri=TEST_NEO4J_URI,
            username=TEST_NEO4J_USERNAME,
            password=TEST_NEO4J_PASSWORD
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'schema_manager') and self.schema_manager.driver:
            self.schema_manager.disconnect()

    @patch('database.neo4j_schema.GraphDatabase')
    def test_schema_manager_creation(self, mock_graph_db):
        """Test creating schema manager instance."""
        manager = Neo4jSchemaManager()
        self.assertEqual(manager.uri, "bolt://localhost:7688")
        self.assertEqual(manager.username, "neo4j")
        self.assertEqual(manager.password, "password")
        self.assertEqual(manager.current_schema_version, "1.0.0")

    @patch('database.neo4j_schema.GraphDatabase')
    def test_connect_success(self, mock_graph_db):
        """Test successful connection to Neo4j."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        self.schema_manager.connect()

        mock_graph_db.driver.assert_called_once_with(
            TEST_NEO4J_URI,
            auth=(TEST_NEO4J_USERNAME, TEST_NEO4J_PASSWORD)
        )
        self.assertEqual(self.schema_manager.driver, mock_driver)

    @patch('database.neo4j_schema.GraphDatabase')
    def test_connect_failure(self, mock_graph_db):
        """Test connection failure handling."""
        from neo4j.exceptions import ServiceUnavailable
        mock_graph_db.driver.side_effect = ServiceUnavailable("Connection failed")

        with self.assertRaises(Neo4jConnectionError):
            self.schema_manager.connect()

    @patch('database.neo4j_schema.GraphDatabase')
    def test_context_manager(self, mock_graph_db):
        """Test using schema manager as context manager."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        with self.schema_manager as manager:
            self.assertIsNotNone(manager.driver)

        mock_driver.close.assert_called_once()

    @patch('database.neo4j_schema.GraphDatabase')
    def test_create_constraints(self, mock_graph_db):
        """Test creating database constraints."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.create_constraints()

        self.assertTrue(result)
        # Verify that session.run was called multiple times for constraints
        self.assertGreater(mock_session.run.call_count, 5)

    @patch('database.neo4j_schema.GraphDatabase')
    def test_create_indexes(self, mock_graph_db):
        """Test creating database indexes."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.create_indexes()

        self.assertTrue(result)
        # Verify that session.run was called multiple times for indexes
        self.assertGreater(mock_session.run.call_count, 5)

    @patch('database.neo4j_schema.GraphDatabase')
    def test_setup_schema(self, mock_graph_db):
        """Test complete schema setup."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.setup_schema()

        self.assertTrue(result)
        # Verify that both constraints and indexes were created
        self.assertGreater(mock_session.run.call_count, 10)

    @patch('database.neo4j_schema.GraphDatabase')
    def test_record_schema_version(self, mock_graph_db):
        """Test recording schema version."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        self.schema_manager._record_schema_version()

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("SchemaVersion", call_args[0][0])

    @patch('database.neo4j_schema.GraphDatabase')
    def test_get_schema_version(self, mock_graph_db):
        """Test getting schema version."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = "1.0.0"
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        version = self.schema_manager.get_schema_version()

        self.assertEqual(version, "1.0.0")

    @patch('database.neo4j_schema.GraphDatabase')
    def test_validate_schema(self, mock_graph_db):
        """Test schema validation."""
        mock_driver = MagicMock()
        mock_session = MagicMock()

        # Mock constraints result
        mock_constraints_result = [
            {"name": "character_id_constraint"},
            {"name": "location_id_constraint"},
            {"name": "user_id_constraint"},
            {"name": "session_id_constraint"},
            {"name": "goal_id_constraint"},
            {"name": "intervention_id_constraint"},
            {"name": "strategy_id_constraint"}
        ]

        # Mock indexes result
        mock_indexes_result = [
            {"name": "character_name_index"},
            {"name": "location_name_index"},
            {"name": "user_created_at_index"}
        ]

        mock_session.run.side_effect = [mock_constraints_result, mock_indexes_result]
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.validate_schema()

        self.assertTrue(result)


@unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j package not available")
class TestNeo4jQueryHelper(unittest.TestCase):
    """Test cases for Neo4jQueryHelper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock()
        self.query_helper = Neo4jQueryHelper(self.mock_driver)

    def test_create_user(self):
        """Test creating a user."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"user_id": "test_user"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_user("test_user", name="Test User")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("User", call_args[0][0])

    def test_create_character(self):
        """Test creating a character."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"character_id": "test_char"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_character("test_char", "Test Character")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("Character", call_args[0][0])

    def test_create_location(self):
        """Test creating a location."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"location_id": "test_location"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_location("test_location", "Test Location")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("Location", call_args[0][0])

    def test_create_session(self):
        """Test creating a session."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"session_id": "test_session"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_session("test_session", "test_user")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("Session", call_args[0][0])
        self.assertIn("HAS_SESSION", call_args[0][0])

    def test_create_therapeutic_goal(self):
        """Test creating a therapeutic goal."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"goal_id": "test_goal"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_therapeutic_goal(
            "test_goal", "test_user", "Test Goal", "Test Description"
        )

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("TherapeuticGoal", call_args[0][0])
        self.assertIn("BELONGS_TO", call_args[0][0])

    def test_get_user_sessions(self):
        """Test getting user sessions."""
        mock_session = MagicMock()
        mock_result = [
            {"s": {"session_id": "session1", "created_at": "2023-01-01"}},
            {"s": {"session_id": "session2", "created_at": "2023-01-02"}}
        ]
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        sessions = self.query_helper.get_user_sessions("test_user", limit=5)

        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0]["session_id"], "session1")
        mock_session.run.assert_called_once()

    def test_get_therapeutic_progress(self):
        """Test getting therapeutic progress."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = {
            "u": {"user_id": "test_user"},
            "goals": [{"goal_id": "goal1", "title": "Test Goal"}],
            "interventions": [{"intervention_id": "int1", "type": "CBT"}],
            "strategies": [{"strategy_id": "str1", "name": "Deep Breathing"}]
        }
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        progress = self.query_helper.get_therapeutic_progress("test_user")

        self.assertIn("user", progress)
        self.assertIn("goals", progress)
        self.assertIn("interventions", progress)
        self.assertIn("strategies", progress)


@unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j package not available")
class TestMigrationManager(unittest.TestCase):
    """Test cases for MigrationManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_schema_manager = MagicMock()
        self.mock_driver = MagicMock()
        self.mock_schema_manager.driver = self.mock_driver
        self.migration_manager = MigrationManager(self.mock_schema_manager)

    def test_migrate_character_data(self):
        """Test migrating character data."""
        character_data = [
            {
                "character_id": "char1",
                "name": "Test Character",
                "therapeutic_role": "therapist",
                "personality_traits": {"empathy": 0.8},
                "memories": [],
                "relationships": {}
            }
        ]

        # Mock the query helper
        mock_query_helper = MagicMock()
        mock_query_helper.create_character.return_value = True
        self.migration_manager.query_helper = mock_query_helper

        result = self.migration_manager.migrate_character_data(character_data)

        self.assertTrue(result)
        mock_query_helper.create_character.assert_called_once()

    def test_migrate_location_data(self):
        """Test migrating location data."""
        location_data = [
            {
                "location_id": "loc1",
                "name": "Test Location",
                "location_type": "therapeutic_space",
                "description": "A test location",
                "connections": {}
            }
        ]

        # Mock the query helper
        mock_query_helper = MagicMock()
        mock_query_helper.create_location.return_value = True
        self.migration_manager.query_helper = mock_query_helper

        result = self.migration_manager.migrate_location_data(location_data)

        self.assertTrue(result)
        mock_query_helper.create_location.assert_called_once()

    def test_migrate_therapeutic_data(self):
        """Test migrating therapeutic data."""
        therapeutic_data = {
            "coping_strategies": [
                {
                    "strategy_id": "strategy1",
                    "name": "Test Strategy",
                    "description": "A test strategy"
                }
            ],
            "intervention_templates": [],
            "therapeutic_techniques": [],
            "emotional_patterns": []
        }

        mock_session = MagicMock()
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.migration_manager.migrate_therapeutic_data(therapeutic_data)

        self.assertTrue(result)
        mock_session.run.assert_called()


@unittest.skipUnless(NEO4J_AVAILABLE, "Neo4j package not available")
class TestDataSeeder(unittest.TestCase):
    """Test cases for DataSeeder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_migration_manager = MagicMock()
        self.data_seeder = DataSeeder(self.mock_migration_manager)

    def test_seed_sample_characters(self):
        """Test seeding sample characters."""
        self.mock_migration_manager.migrate_character_data.return_value = True

        result = self.data_seeder.seed_sample_characters()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_character_data.assert_called_once()

        # Check that character data was passed
        call_args = self.mock_migration_manager.migrate_character_data.call_args
        character_data = call_args[0][0]
        self.assertIsInstance(character_data, list)
        self.assertGreater(len(character_data), 0)

        # Check that characters have required fields
        for character in character_data:
            self.assertIn("character_id", character)
            self.assertIn("name", character)
            self.assertIn("therapeutic_role", character)

    def test_seed_sample_locations(self):
        """Test seeding sample locations."""
        self.mock_migration_manager.migrate_location_data.return_value = True

        result = self.data_seeder.seed_sample_locations()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_location_data.assert_called_once()

        # Check that location data was passed
        call_args = self.mock_migration_manager.migrate_location_data.call_args
        location_data = call_args[0][0]
        self.assertIsInstance(location_data, list)
        self.assertGreater(len(location_data), 0)

        # Check that locations have required fields
        for location in location_data:
            self.assertIn("location_id", location)
            self.assertIn("name", location)
            self.assertIn("location_type", location)

    def test_seed_therapeutic_content(self):
        """Test seeding therapeutic content."""
        self.mock_migration_manager.migrate_therapeutic_data.return_value = True

        result = self.data_seeder.seed_therapeutic_content()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_therapeutic_data.assert_called_once()

        # Check that therapeutic data was passed
        call_args = self.mock_migration_manager.migrate_therapeutic_data.call_args
        therapeutic_data = call_args[0][0]
        self.assertIsInstance(therapeutic_data, dict)
        self.assertIn("coping_strategies", therapeutic_data)
        self.assertIn("intervention_templates", therapeutic_data)

    def test_seed_all_sample_data(self):
        """Test seeding all sample data."""
        self.mock_migration_manager.migrate_character_data.return_value = True
        self.mock_migration_manager.migrate_location_data.return_value = True
        self.mock_migration_manager.migrate_therapeutic_data.return_value = True

        result = self.data_seeder.seed_all_sample_data()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_character_data.assert_called_once()
        self.mock_migration_manager.migrate_location_data.assert_called_once()
        self.mock_migration_manager.migrate_therapeutic_data.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    @patch('database.neo4j_schema.Neo4jSchemaManager')
    def test_setup_neo4j_schema_utility(self, mock_schema_manager_class):
        """Test setup_neo4j_schema utility function."""
        mock_manager = MagicMock()
        mock_manager.setup_schema.return_value = True
        mock_schema_manager_class.return_value.__enter__.return_value = mock_manager

        result = setup_neo4j_schema()

        self.assertTrue(result)
        mock_manager.setup_schema.assert_called_once()

    @patch('database.neo4j_schema.Neo4jSchemaManager')
    def test_validate_neo4j_schema_utility(self, mock_schema_manager_class):
        """Test validate_neo4j_schema utility function."""
        mock_manager = MagicMock()
        mock_manager.validate_schema.return_value = True
        mock_schema_manager_class.return_value.__enter__.return_value = mock_manager

        result = validate_neo4j_schema()

        self.assertTrue(result)
        mock_manager.validate_schema.assert_called_once()

    @patch('database.migrations.Neo4jSchemaManager')
    def test_run_migrations_utility(self, mock_schema_manager_class):
        """Test run_migrations utility function."""
        mock_manager = MagicMock()
        mock_manager.setup_schema.return_value = True
        mock_schema_manager_class.return_value.__enter__.return_value = mock_manager

        # Mock the data seeder
        with patch('database.migrations.DataSeeder') as mock_seeder_class:
            mock_seeder = MagicMock()
            mock_seeder.seed_all_sample_data.return_value = True
            mock_seeder_class.return_value = mock_seeder

            result = run_migrations()

            self.assertTrue(result)
            mock_manager.setup_schema.assert_called_once()
            mock_seeder.seed_all_sample_data.assert_called_once()


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)

    # Run tests
    unittest.main(verbosity=2)
