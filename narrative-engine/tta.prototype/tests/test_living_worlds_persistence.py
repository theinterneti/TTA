"""
Integration tests for Living Worlds persistence layer.

This module contains comprehensive tests for the Living Worlds Neo4j schema,
persistence operations, and data consistency. These tests require a running
Neo4j instance and will create/modify data.
"""

import logging
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from models.living_worlds_models import (
        EntityType,
        EventType,
        FamilyRelationship,
        FamilyTree,
        RelationshipType,
        Timeline,
        TimelineEvent,
        ValidationError,
        WorldState,
        WorldStateFlag,
    )

    from database.living_worlds_migrations import (
        LivingWorldsMigrationManager,
        TimelineDataSeeder,
        run_living_worlds_migrations,
    )
    from database.living_worlds_persistence import (
        LivingWorldsPersistence,
        PersistenceError,
        TimelinePersistence,
        WorldStatePersistence,
    )
    from database.living_worlds_schema import (
        LivingWorldsQueryHelper,
        LivingWorldsSchemaManager,
    )
    LIVING_WORLDS_AVAILABLE = True
except ImportError as e:
    print(f"Living Worlds components not available for testing: {e}")
    LIVING_WORLDS_AVAILABLE = False

# Test configuration
TEST_NEO4J_URI = os.getenv("TEST_NEO4J_URI", "bolt://localhost:7688")
TEST_NEO4J_USERNAME = os.getenv("TEST_NEO4J_USERNAME", "neo4j")
TEST_NEO4J_PASSWORD = os.getenv("TEST_NEO4J_PASSWORD", "password")

logger = logging.getLogger(__name__)


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestLivingWorldsSchemaManager(unittest.TestCase):
    """Test cases for LivingWorldsSchemaManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.schema_manager = LivingWorldsSchemaManager(
            uri=TEST_NEO4J_URI,
            username=TEST_NEO4J_USERNAME,
            password=TEST_NEO4J_PASSWORD
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'schema_manager') and self.schema_manager.driver:
            self.schema_manager.disconnect()

    @patch('database.living_worlds_schema.GraphDatabase')
    def test_living_worlds_schema_manager_creation(self, mock_graph_db):
        """Test creating Living Worlds schema manager instance."""
        manager = LivingWorldsSchemaManager()
        self.assertEqual(manager.uri, "bolt://localhost:7688")
        self.assertEqual(manager.username, "neo4j")
        self.assertEqual(manager.password, "password")
        self.assertEqual(manager.current_schema_version, "1.1.0")

    @patch('database.living_worlds_schema.GraphDatabase')
    def test_create_living_worlds_constraints(self, mock_graph_db):
        """Test creating Living Worlds specific constraints."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.create_living_worlds_constraints()

        self.assertTrue(result)
        # Verify that session.run was called multiple times for Living Worlds constraints
        self.assertGreater(mock_session.run.call_count, 8)

    @patch('database.living_worlds_schema.GraphDatabase')
    def test_create_living_worlds_indexes(self, mock_graph_db):
        """Test creating Living Worlds specific indexes."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        result = self.schema_manager.create_living_worlds_indexes()

        self.assertTrue(result)
        # Verify that session.run was called multiple times for Living Worlds indexes
        self.assertGreater(mock_session.run.call_count, 15)

    @patch('database.living_worlds_schema.GraphDatabase')
    def test_setup_living_worlds_schema(self, mock_graph_db):
        """Test complete Living Worlds schema setup."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver
        self.schema_manager.driver = mock_driver

        # Mock the base schema setup
        with patch.object(self.schema_manager, 'setup_schema', return_value=True):
            result = self.schema_manager.setup_living_worlds_schema()

        self.assertTrue(result)
        # Verify that both Living Worlds constraints and indexes were created
        self.assertGreater(mock_session.run.call_count, 20)


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestLivingWorldsQueryHelper(unittest.TestCase):
    """Test cases for LivingWorldsQueryHelper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock()
        self.query_helper = LivingWorldsQueryHelper(self.mock_driver)

    def test_create_timeline(self):
        """Test creating a timeline."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"timeline_id": "test_timeline"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_timeline("test_timeline", "test_entity", "character")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("Timeline", call_args[0][0])

    def test_create_timeline_event(self):
        """Test creating a timeline event."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"event_id": "test_event"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_timeline_event(
            "test_event", "test_timeline", "meeting", "Test Event", "Test Description"
        )

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("TimelineEvent", call_args[0][0])
        self.assertIn("CONTAINS_EVENT", call_args[0][0])

    def test_create_world_state(self):
        """Test creating a world state."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"world_id": "test_world"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_world_state("test_world", "Test World")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("World", call_args[0][0])

    def test_create_family_tree(self):
        """Test creating a family tree."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"tree_id": "test_tree"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_family_tree("test_tree", "test_character")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("FamilyTree", call_args[0][0])
        self.assertIn("CENTERED_ON", call_args[0][0])

    def test_create_family_relationship(self):
        """Test creating a family relationship."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"relationship_id": "test_rel"}
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.query_helper.create_family_relationship(
            "test_rel", "char1", "char2", "parent", 0.8
        )

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        self.assertIn("CREATE", call_args[0][0])
        self.assertIn("FamilyRelationship", call_args[0][0])
        self.assertIn("HAS_FAMILY_RELATIONSHIP", call_args[0][0])

    def test_get_timeline_events(self):
        """Test getting timeline events."""
        mock_session = MagicMock()
        mock_result = [
            {"e": {"event_id": "event1", "title": "Event 1", "timestamp": datetime.now()}},
            {"e": {"event_id": "event2", "title": "Event 2", "timestamp": datetime.now()}}
        ]
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        events = self.query_helper.get_timeline_events("test_timeline", limit=10, min_significance=5)

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_id"], "event1")
        mock_session.run.assert_called_once()

    def test_get_character_family_relationships(self):
        """Test getting character family relationships."""
        mock_session = MagicMock()
        mock_result = [
            {
                "r": {"relationship_id": "rel1", "relationship_type": "parent", "strength": 0.9},
                "related_character": {"character_id": "parent1", "name": "Parent"}
            }
        ]
        mock_session.run.return_value = mock_result
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        relationships = self.query_helper.get_character_family_relationships("test_character")

        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]["relationship_id"], "rel1")
        self.assertIsNotNone(relationships[0]["related_character"])
        mock_session.run.assert_called_once()


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestTimelinePersistence(unittest.TestCase):
    """Test cases for TimelinePersistence class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_query_helper = MagicMock()
        self.mock_cache = MagicMock()
        self.timeline_persistence = TimelinePersistence(self.mock_query_helper, self.mock_cache)

        # Create test timeline
        self.test_timeline = Timeline(
            timeline_id="test_timeline",
            entity_id="test_entity",
            entity_type=EntityType.CHARACTER
        )

        # Create test event
        self.test_event = TimelineEvent(
            event_id="test_event",
            event_type=EventType.MEETING,
            title="Test Event",
            description="A test event",
            participants=["test_entity"],
            significance_level=7,
            emotional_impact=0.5
        )
        self.test_timeline.add_event(self.test_event)

    def test_save_timeline_success(self):
        """Test successful timeline save."""
        self.mock_query_helper.create_timeline.return_value = True
        self.mock_query_helper.create_timeline_event.return_value = True

        result = self.timeline_persistence.save_timeline(self.test_timeline)

        self.assertTrue(result)
        self.mock_query_helper.create_timeline.assert_called_once()
        self.mock_query_helper.create_timeline_event.assert_called_once()
        self.mock_cache.set.assert_called_once()

    def test_save_timeline_validation_failure(self):
        """Test timeline save with validation failure."""
        # Create invalid timeline
        invalid_timeline = Timeline(
            timeline_id="",  # Invalid empty ID
            entity_id="test_entity",
            entity_type=EntityType.CHARACTER
        )

        result = self.timeline_persistence.save_timeline(invalid_timeline)

        self.assertFalse(result)
        self.mock_query_helper.create_timeline.assert_not_called()

    def test_load_timeline_from_cache(self):
        """Test loading timeline from cache."""
        cached_data = self.test_timeline.to_dict()
        self.mock_cache.get.return_value = cached_data

        result = self.timeline_persistence.load_timeline("test_timeline")

        self.assertIsNotNone(result)
        self.assertEqual(result.timeline_id, "test_timeline")
        self.mock_cache.get.assert_called_once()

    def test_load_timeline_from_neo4j(self):
        """Test loading timeline from Neo4j when not in cache."""
        self.mock_cache.get.return_value = None

        # Mock Neo4j data loading
        with patch.object(self.timeline_persistence, '_load_timeline_from_neo4j') as mock_load:
            mock_load.return_value = self.test_timeline.to_dict()

            result = self.timeline_persistence.load_timeline("test_timeline")

            self.assertIsNotNone(result)
            self.assertEqual(result.timeline_id, "test_timeline")
            mock_load.assert_called_once()
            self.mock_cache.set.assert_called_once()

    def test_save_timeline_event_success(self):
        """Test successful timeline event save."""
        self.mock_query_helper.create_timeline_event.return_value = True

        result = self.timeline_persistence.save_timeline_event("test_timeline", self.test_event)

        self.assertTrue(result)
        self.mock_query_helper.create_timeline_event.assert_called_once()
        self.mock_cache.delete.assert_called_once()  # Cache invalidation

    def test_get_timeline_events_from_cache(self):
        """Test getting timeline events from cache."""
        cached_events = [self.test_event.to_dict()]
        self.mock_cache.get.return_value = cached_events

        result = self.timeline_persistence.get_timeline_events("test_timeline")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].event_id, "test_event")
        self.mock_cache.get.assert_called_once()

    def test_get_timeline_events_from_neo4j(self):
        """Test getting timeline events from Neo4j when not in cache."""
        self.mock_cache.get.return_value = None

        # Mock Neo4j event data
        neo4j_event_data = {
            "event_id": "test_event",
            "event_type": "meeting",
            "title": "Test Event",
            "description": "A test event",
            "timestamp": datetime.now(),
            "significance_level": 7,
            "emotional_impact": 0.5,
            "participants": ["test_entity"],
            "consequences": [],
            "tags": [],
            "created_at": datetime.now()
        }
        self.mock_query_helper.get_timeline_events.return_value = [neo4j_event_data]

        result = self.timeline_persistence.get_timeline_events("test_timeline")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].event_id, "test_event")
        self.mock_query_helper.get_timeline_events.assert_called_once()
        self.mock_cache.set.assert_called_once()

    def test_delete_timeline(self):
        """Test timeline deletion."""
        mock_session = MagicMock()
        self.mock_query_helper.driver.session.return_value.__enter__.return_value = mock_session

        result = self.timeline_persistence.delete_timeline("test_timeline")

        self.assertTrue(result)
        mock_session.run.assert_called_once()
        self.mock_cache.delete.assert_called()


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestWorldStatePersistence(unittest.TestCase):
    """Test cases for WorldStatePersistence class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_query_helper = MagicMock()
        self.mock_cache = MagicMock()
        self.world_state_persistence = WorldStatePersistence(self.mock_query_helper, self.mock_cache)

        # Create test world state
        self.test_world_state = WorldState(
            world_id="test_world",
            world_name="Test World",
            world_status=WorldStateFlag.ACTIVE
        )
        self.test_world_state.set_flag("test_flag", "test_value")

    def test_save_world_state_success(self):
        """Test successful world state save."""
        self.mock_query_helper.create_world_state.return_value = True

        result = self.world_state_persistence.save_world_state(self.test_world_state)

        self.assertTrue(result)
        self.mock_query_helper.create_world_state.assert_called_once()
        self.mock_cache.set.assert_called_once()

    def test_save_world_state_update_existing(self):
        """Test updating existing world state."""
        self.mock_query_helper.create_world_state.return_value = False
        self.mock_query_helper.update_world_state.return_value = True

        result = self.world_state_persistence.save_world_state(self.test_world_state)

        self.assertTrue(result)
        self.mock_query_helper.create_world_state.assert_called_once()
        self.mock_query_helper.update_world_state.assert_called_once()
        self.mock_cache.set.assert_called_once()

    def test_load_world_state_from_cache(self):
        """Test loading world state from cache."""
        cached_data = self.test_world_state.to_dict()
        self.mock_cache.get.return_value = cached_data

        result = self.world_state_persistence.load_world_state("test_world")

        self.assertIsNotNone(result)
        self.assertEqual(result.world_id, "test_world")
        self.mock_cache.get.assert_called_once()

    def test_load_world_state_from_neo4j(self):
        """Test loading world state from Neo4j when not in cache."""
        self.mock_cache.get.return_value = None

        # Mock Neo4j world state data
        neo4j_world_data = {
            "world_id": "test_world",
            "world_name": "Test World",
            "current_time": datetime.now(),
            "world_status": "active",
            "last_evolution": datetime.now(),
            "player_last_visit": None,
            "world_flags": "{}",
            "evolution_schedule": "[]",
            "active_characters": "{}",
            "active_locations": "{}",
            "active_objects": "{}",
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "metadata": "{}"
        }
        self.mock_query_helper.get_world_state.return_value = neo4j_world_data

        result = self.world_state_persistence.load_world_state("test_world")

        self.assertIsNotNone(result)
        self.assertEqual(result.world_id, "test_world")
        self.mock_query_helper.get_world_state.assert_called_once()
        self.mock_cache.set.assert_called_once()

    def test_update_world_state(self):
        """Test updating world state properties."""
        self.mock_query_helper.update_world_state.return_value = True

        updates = {"test_property": "test_value"}
        result = self.world_state_persistence.update_world_state("test_world", updates)

        self.assertTrue(result)
        self.mock_query_helper.update_world_state.assert_called_once()
        self.mock_cache.delete.assert_called_once()  # Cache invalidation


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestLivingWorldsPersistence(unittest.TestCase):
    """Test cases for LivingWorldsPersistence main interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the schema manager and query helper
        with patch('database.living_worlds_persistence.LivingWorldsSchemaManager') as mock_schema_manager_class:
            with patch('database.living_worlds_persistence.RedisCache') as mock_redis_cache_class:
                self.persistence = LivingWorldsPersistence()
                self.mock_schema_manager = mock_schema_manager_class.return_value
                self.mock_cache = mock_redis_cache_class.return_value

    def test_persistence_initialization(self):
        """Test persistence initialization."""
        self.assertIsNotNone(self.persistence.schema_manager)
        self.assertIsNone(self.persistence.query_helper)  # Not connected yet
        self.assertIsNone(self.persistence.timeline_persistence)
        self.assertIsNone(self.persistence.world_state_persistence)

    @patch('database.living_worlds_persistence.LivingWorldsQueryHelper')
    @patch('database.living_worlds_persistence.TimelinePersistence')
    @patch('database.living_worlds_persistence.WorldStatePersistence')
    def test_connect_success(self, mock_world_state_persistence, mock_timeline_persistence, mock_query_helper):
        """Test successful connection."""
        self.mock_schema_manager.connect.return_value = None
        self.mock_schema_manager.driver = MagicMock()

        result = self.persistence.connect()

        self.assertTrue(result)
        self.mock_schema_manager.connect.assert_called_once()
        mock_query_helper.assert_called_once()
        mock_timeline_persistence.assert_called_once()
        mock_world_state_persistence.assert_called_once()

    def test_context_manager(self):
        """Test using persistence as context manager."""
        with patch.object(self.persistence, 'connect', return_value=True) as mock_connect:
            with patch.object(self.persistence, 'disconnect') as mock_disconnect:
                with self.persistence as p:
                    self.assertEqual(p, self.persistence)

                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    def test_save_timeline_not_connected(self):
        """Test save timeline when not connected."""
        timeline = Timeline(
            timeline_id="test",
            entity_id="test",
            entity_type=EntityType.CHARACTER
        )

        with self.assertRaises(PersistenceError):
            self.persistence.save_timeline(timeline)

    def test_save_family_tree_success(self):
        """Test successful family tree save."""
        # Mock connection
        self.persistence.query_helper = MagicMock()
        self.persistence.query_helper.create_family_tree.return_value = True
        self.persistence.query_helper.create_family_relationship.return_value = True

        # Create test family tree
        family_tree = FamilyTree(
            tree_id="test_tree",
            root_character_id="test_character"
        )

        # Add a relationship
        FamilyRelationship(
            from_character_id="parent",
            to_character_id="test_character",
            relationship_type=RelationshipType.PARENT
        )
        family_tree.add_relationship("parent", "test_character", RelationshipType.PARENT)

        result = self.persistence.save_family_tree(family_tree)

        self.assertTrue(result)
        self.persistence.query_helper.create_family_tree.assert_called_once()


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestLivingWorldsMigrations(unittest.TestCase):
    """Test cases for Living Worlds migration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_schema_manager = MagicMock()
        self.mock_driver = MagicMock()
        self.mock_schema_manager.driver = self.mock_driver
        self.migration_manager = LivingWorldsMigrationManager(self.mock_schema_manager)

    def test_migrate_timeline_data(self):
        """Test migrating timeline data."""
        timeline_data = [
            {
                "timeline_id": "test_timeline",
                "entity_id": "test_entity",
                "entity_type": "character",
                "events": [
                    {
                        "event_id": "test_event",
                        "event_type": "meeting",
                        "title": "Test Event",
                        "description": "A test event"
                    }
                ]
            }
        ]

        # Mock the query helper
        mock_query_helper = MagicMock()
        mock_query_helper.create_timeline.return_value = True
        mock_query_helper.create_timeline_event.return_value = True
        self.migration_manager.living_worlds_query_helper = mock_query_helper

        result = self.migration_manager.migrate_timeline_data(timeline_data)

        self.assertTrue(result)
        mock_query_helper.create_timeline.assert_called_once()
        mock_query_helper.create_timeline_event.assert_called_once()

    def test_migrate_family_tree_data(self):
        """Test migrating family tree data."""
        family_tree_data = [
            {
                "tree_id": "test_tree",
                "root_character_id": "test_character",
                "relationships": [
                    {
                        "relationship_id": "test_rel",
                        "from_character_id": "parent",
                        "to_character_id": "test_character",
                        "relationship_type": "parent"
                    }
                ],
                "family_events": []
            }
        ]

        # Mock the query helper
        mock_query_helper = MagicMock()
        mock_query_helper.create_family_tree.return_value = True
        mock_query_helper.create_family_relationship.return_value = True
        mock_query_helper.create_timeline.return_value = True
        self.migration_manager.living_worlds_query_helper = mock_query_helper

        result = self.migration_manager.migrate_family_tree_data(family_tree_data)

        self.assertTrue(result)
        mock_query_helper.create_family_tree.assert_called_once()
        mock_query_helper.create_family_relationship.assert_called_once()

    def test_migrate_world_state_data(self):
        """Test migrating world state data."""
        world_state_data = [
            {
                "world_id": "test_world",
                "world_name": "Test World",
                "active_characters": {"char1": {"status": "active"}},
                "active_locations": {"loc1": {"status": "accessible"}},
                "active_objects": {"obj1": {"condition": "good"}}
            }
        ]

        # Mock the query helper
        mock_query_helper = MagicMock()
        mock_query_helper.create_world_state.return_value = True
        self.migration_manager.living_worlds_query_helper = mock_query_helper

        # Mock the session for linking entities
        mock_session = MagicMock()
        self.mock_driver.session.return_value.__enter__.return_value = mock_session

        result = self.migration_manager.migrate_world_state_data(world_state_data)

        self.assertTrue(result)
        mock_query_helper.create_world_state.assert_called_once()
        # Verify that entity linking queries were run
        self.assertGreater(mock_session.run.call_count, 0)


@unittest.skipUnless(LIVING_WORLDS_AVAILABLE, "Living Worlds components not available")
class TestTimelineDataSeeder(unittest.TestCase):
    """Test cases for TimelineDataSeeder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_migration_manager = MagicMock()
        self.data_seeder = TimelineDataSeeder(self.mock_migration_manager)

    def test_seed_sample_timelines(self):
        """Test seeding sample timelines."""
        self.mock_migration_manager.migrate_timeline_data.return_value = True

        result = self.data_seeder.seed_sample_timelines()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_timeline_data.assert_called_once()

        # Check that timeline data was passed
        call_args = self.mock_migration_manager.migrate_timeline_data.call_args
        timeline_data = call_args[0][0]
        self.assertIsInstance(timeline_data, list)
        self.assertGreater(len(timeline_data), 0)

        # Check that timelines have required fields
        for timeline in timeline_data:
            self.assertIn("timeline_id", timeline)
            self.assertIn("entity_id", timeline)
            self.assertIn("entity_type", timeline)
            self.assertIn("events", timeline)

    def test_seed_sample_family_trees(self):
        """Test seeding sample family trees."""
        self.mock_migration_manager.migrate_family_tree_data.return_value = True

        result = self.data_seeder.seed_sample_family_trees()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_family_tree_data.assert_called_once()

        # Check that family tree data was passed
        call_args = self.mock_migration_manager.migrate_family_tree_data.call_args
        family_tree_data = call_args[0][0]
        self.assertIsInstance(family_tree_data, list)
        self.assertGreater(len(family_tree_data), 0)

        # Check that family trees have required fields
        for tree in family_tree_data:
            self.assertIn("tree_id", tree)
            self.assertIn("root_character_id", tree)
            self.assertIn("relationships", tree)

    def test_seed_sample_world_states(self):
        """Test seeding sample world states."""
        self.mock_migration_manager.migrate_world_state_data.return_value = True

        result = self.data_seeder.seed_sample_world_states()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_world_state_data.assert_called_once()

        # Check that world state data was passed
        call_args = self.mock_migration_manager.migrate_world_state_data.call_args
        world_state_data = call_args[0][0]
        self.assertIsInstance(world_state_data, list)
        self.assertGreater(len(world_state_data), 0)

        # Check that world states have required fields
        for world_state in world_state_data:
            self.assertIn("world_id", world_state)
            self.assertIn("world_name", world_state)
            self.assertIn("active_characters", world_state)

    def test_seed_all_living_worlds_data(self):
        """Test seeding all Living Worlds data."""
        self.mock_migration_manager.migrate_timeline_data.return_value = True
        self.mock_migration_manager.migrate_family_tree_data.return_value = True
        self.mock_migration_manager.migrate_world_state_data.return_value = True

        result = self.data_seeder.seed_all_living_worlds_data()

        self.assertTrue(result)
        self.mock_migration_manager.migrate_timeline_data.assert_called_once()
        self.mock_migration_manager.migrate_family_tree_data.assert_called_once()
        self.mock_migration_manager.migrate_world_state_data.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    @patch('database.living_worlds_migrations.LivingWorldsSchemaManager')
    def test_run_living_worlds_migrations(self, mock_schema_manager_class):
        """Test run_living_worlds_migrations utility function."""
        mock_manager = MagicMock()
        mock_manager.setup_living_worlds_schema.return_value = True
        mock_schema_manager_class.return_value.__enter__.return_value = mock_manager

        # Mock the data seeder
        with patch('database.living_worlds_migrations.TimelineDataSeeder') as mock_seeder_class:
            mock_seeder = MagicMock()
            mock_seeder.seed_all_living_worlds_data.return_value = True
            mock_seeder_class.return_value = mock_seeder

            result = run_living_worlds_migrations()

            self.assertTrue(result)
            mock_manager.setup_living_worlds_schema.assert_called_once()
            mock_seeder.seed_all_living_worlds_data.assert_called_once()


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)

    # Run tests
    unittest.main(verbosity=2)
