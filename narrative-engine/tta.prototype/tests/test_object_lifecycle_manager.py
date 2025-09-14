"""
Unit Tests for Object Lifecycle Manager

This module contains comprehensive unit tests for the ObjectLifecycleManager class,
testing object creation, aging, wear simulation, interaction handling, relationship
management, and timeline integration.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

# Add the core and models paths
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
sys.path.extend([str(core_path), str(models_path)])

from living_worlds_models import (
    EntityType,
    EventType,
    ObjectHistory,
    TimelineEvent,
    ValidationError,
    WearEvent,
)
from object_lifecycle_manager import (
    Interaction,
    ObjectData,
    ObjectLifecycleManager,
    WearState,
    create_sample_interaction,
    create_sample_object_data,
)


class TestObjectLifecycleManager(unittest.TestCase):
    """Test cases for ObjectLifecycleManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = ObjectLifecycleManager()
        self.sample_object_data = ObjectData(
            object_id="test_object_1",
            name="Test Sword",
            object_type="weapon",
            description="A sharp testing sword",
            initial_condition=1.0,
            properties={"material": "steel", "weight": 2.5},
            tags=["weapon", "sword", "test"],
            location_id="test_location_1",
            owner_id="test_character_1",
            creation_context="Created for unit testing"
        )

    def test_initialization(self):
        """Test ObjectLifecycleManager initialization."""
        # Test default initialization
        manager = ObjectLifecycleManager()
        self.assertIsNone(manager.timeline_engine)
        self.assertEqual(len(manager.object_histories), 0)
        self.assertTrue(manager.wear_simulation_enabled)
        self.assertEqual(manager.aging_rate, 1.0)
        self.assertEqual(manager.interaction_wear_multiplier, 1.0)

        # Test initialization with timeline engine
        mock_timeline_engine = Mock()
        manager_with_timeline = ObjectLifecycleManager(timeline_engine=mock_timeline_engine)
        self.assertEqual(manager_with_timeline.timeline_engine, mock_timeline_engine)

    def test_create_object_with_history_success(self):
        """Test successful object creation with history."""
        object_history = self.manager.create_object_with_history(self.sample_object_data)

        # Verify object history was created
        self.assertIsInstance(object_history, ObjectHistory)
        self.assertEqual(object_history.object_id, self.sample_object_data.object_id)

        # Verify object state
        object_state = object_history.object_state
        self.assertEqual(object_state.name, self.sample_object_data.name)
        self.assertEqual(object_state.object_type, self.sample_object_data.object_type)
        self.assertEqual(object_state.current_condition, 1.0)
        self.assertEqual(object_state.wear_level, 0.0)
        self.assertTrue(object_state.is_functional)
        self.assertEqual(object_state.current_location_id, self.sample_object_data.location_id)
        self.assertEqual(object_state.current_owner_id, self.sample_object_data.owner_id)

        # Verify creation event
        self.assertIsNotNone(object_history.creation_event)
        self.assertEqual(object_history.creation_event.event_type, EventType.CREATION)
        self.assertIn(self.sample_object_data.object_id, object_history.creation_event.participants)

        # Verify ownership and location history
        self.assertIn(self.sample_object_data.owner_id, object_history.ownership_history)
        self.assertEqual(len(object_history.location_history), 1)
        self.assertEqual(object_history.location_history[0][0], self.sample_object_data.location_id)

        # Verify object is stored in manager
        self.assertIn(self.sample_object_data.object_id, self.manager.object_histories)

    def test_create_object_with_history_validation_errors(self):
        """Test object creation with validation errors."""
        # Test empty name
        invalid_data = ObjectData(name="", object_type="test")
        with self.assertRaises(ValidationError):
            self.manager.create_object_with_history(invalid_data)

        # Test invalid initial condition
        invalid_data = ObjectData(name="Test", object_type="test", initial_condition=1.5)
        with self.assertRaises(ValidationError):
            self.manager.create_object_with_history(invalid_data)

        invalid_data = ObjectData(name="Test", object_type="test", initial_condition=-0.1)
        with self.assertRaises(ValidationError):
            self.manager.create_object_with_history(invalid_data)

    def test_create_object_with_timeline_integration(self):
        """Test object creation with timeline engine integration."""
        mock_timeline_engine = Mock()
        mock_timeline = Mock()
        mock_timeline.timeline_id = "test_timeline_1"
        mock_timeline_engine.create_timeline.return_value = mock_timeline

        manager = ObjectLifecycleManager(timeline_engine=mock_timeline_engine)
        manager.create_object_with_history(self.sample_object_data)

        # Verify timeline engine was called
        mock_timeline_engine.create_timeline.assert_called_once_with(
            self.sample_object_data.object_id,
            EntityType.OBJECT
        )
        mock_timeline_engine.add_event.assert_called_once()

    def test_age_object_success(self):
        """Test successful object aging."""
        # Create object first
        object_history = self.manager.create_object_with_history(self.sample_object_data)
        initial_condition = object_history.object_state.current_condition
        initial_wear = object_history.object_state.wear_level

        # Age the object
        time_delta = timedelta(days=100)  # 100 days
        updated_state = self.manager.age_object(self.sample_object_data.object_id, time_delta)

        # Verify aging effects
        self.assertLess(updated_state.current_condition, initial_condition)
        self.assertGreater(updated_state.wear_level, initial_wear)

        # Verify wear event was added
        object_history = self.manager.object_histories[self.sample_object_data.object_id]
        self.assertGreater(len(object_history.wear_timeline), 0)

        # Check that the most recent wear event is aging
        latest_wear = object_history.wear_timeline[-1]
        self.assertEqual(latest_wear.wear_type, "aging")
        self.assertIn("aging", latest_wear.description.lower())

    def test_age_object_material_modifiers(self):
        """Test aging with different material modifiers."""
        # Test different object types
        test_materials = [
            ("metal", 0.5),
            ("wood", 1.2),
            ("fabric", 1.5),
            ("stone", 0.3),
            ("organic", 2.0)
        ]

        for material, _expected_modifier in test_materials:
            with self.subTest(material=material):
                # Create object with specific material type
                object_data = ObjectData(
                    name=f"Test {material}",
                    object_type=material,
                    initial_condition=1.0
                )

                manager = ObjectLifecycleManager()
                object_history = manager.create_object_with_history(object_data)
                initial_condition = object_history.object_state.current_condition

                # Age the object
                manager.age_object(object_data.object_id, timedelta(days=100))

                # Verify aging occurred (exact amounts depend on implementation)
                updated_history = manager.object_histories[object_data.object_id]
                self.assertLess(updated_history.object_state.current_condition, initial_condition)

    def test_age_object_not_found(self):
        """Test aging non-existent object."""
        with self.assertRaises(ValidationError):
            self.manager.age_object("non_existent_object", timedelta(days=1))

    def test_handle_object_interaction_success(self):
        """Test successful object interaction handling."""
        # Create object first
        object_history = self.manager.create_object_with_history(self.sample_object_data)
        initial_interaction_count = len(object_history.interaction_events)

        # Create interaction
        interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description="Character uses the sword in combat",
            intensity=0.8,
            duration_minutes=30,
            location_id="test_location_1",
            consequences=["Sword becomes slightly duller"]
        )

        # Handle interaction
        result = self.manager.handle_object_interaction(self.sample_object_data.object_id, interaction)

        # Verify success
        self.assertTrue(result)

        # Verify interaction event was added
        updated_history = self.manager.object_histories[self.sample_object_data.object_id]
        self.assertEqual(len(updated_history.interaction_events), initial_interaction_count + 1)

        # Verify the interaction event details
        latest_interaction = updated_history.interaction_events[-1]
        self.assertEqual(latest_interaction.event_type, EventType.PLAYER_INTERACTION)
        self.assertIn(self.sample_object_data.object_id, latest_interaction.participants)
        self.assertIn("test_character_1", latest_interaction.participants)

    def test_handle_object_interaction_wear_application(self):
        """Test that interactions apply appropriate wear."""
        # Create object first
        object_history = self.manager.create_object_with_history(self.sample_object_data)
        initial_condition = object_history.object_state.current_condition
        initial_wear_events = len(object_history.wear_timeline)

        # Create high-intensity interaction
        interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description="Intensive sword combat",
            intensity=1.0,  # Maximum intensity
            duration_minutes=120  # 2 hours
        )

        # Handle interaction
        self.manager.handle_object_interaction(self.sample_object_data.object_id, interaction)

        # Verify wear was applied
        updated_history = self.manager.object_histories[self.sample_object_data.object_id]
        self.assertLess(updated_history.object_state.current_condition, initial_condition)
        self.assertGreater(len(updated_history.wear_timeline), initial_wear_events)

    def test_handle_object_interaction_special_types(self):
        """Test handling of special interaction types (repair, damage, modify)."""
        # Create object first
        self.manager.create_object_with_history(self.sample_object_data)

        # First, damage the object
        damage_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="damage",
            description="Sword is damaged in battle",
            intensity=0.8
        )

        self.manager.handle_object_interaction(self.sample_object_data.object_id, damage_interaction)
        damaged_condition = self.manager.object_histories[self.sample_object_data.object_id].object_state.current_condition

        # Then repair the object
        repair_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="repair",
            description="Sword is repaired by blacksmith",
            intensity=0.9
        )

        self.manager.handle_object_interaction(self.sample_object_data.object_id, repair_interaction)
        repaired_condition = self.manager.object_histories[self.sample_object_data.object_id].object_state.current_condition

        # Verify repair improved condition
        self.assertGreater(repaired_condition, damaged_condition)

        # Test modification
        modify_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="modify",
            description="Sword is enchanted with magic",
            intensity=0.5
        )

        result = self.manager.handle_object_interaction(self.sample_object_data.object_id, modify_interaction)
        self.assertTrue(result)

        # Verify modification event was recorded
        updated_history = self.manager.object_histories[self.sample_object_data.object_id]
        modification_events = [e for e in updated_history.modification_events if "Modification" in e.title]
        self.assertGreater(len(modification_events), 0)

    def test_handle_object_interaction_validation_errors(self):
        """Test interaction handling with validation errors."""
        # Create object first
        self.manager.create_object_with_history(self.sample_object_data)

        # Test empty character ID
        invalid_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="",
            interaction_type="use",
            description="Test interaction"
        )
        result = self.manager.handle_object_interaction(self.sample_object_data.object_id, invalid_interaction)
        self.assertFalse(result)

        # Test empty description
        invalid_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description=""
        )
        result = self.manager.handle_object_interaction(self.sample_object_data.object_id, invalid_interaction)
        self.assertFalse(result)

        # Test invalid intensity
        invalid_interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description="Test interaction",
            intensity=1.5
        )
        result = self.manager.handle_object_interaction(self.sample_object_data.object_id, invalid_interaction)
        self.assertFalse(result)

    def test_handle_object_interaction_object_not_found(self):
        """Test interaction handling with non-existent object."""
        interaction = Interaction(
            object_id="non_existent_object",
            character_id="test_character_1",
            interaction_type="use",
            description="Test interaction"
        )

        result = self.manager.handle_object_interaction("non_existent_object", interaction)
        self.assertFalse(result)

    def test_get_object_history(self):
        """Test retrieving object history."""
        # Test non-existent object
        history = self.manager.get_object_history("non_existent_object")
        self.assertIsNone(history)

        # Create object and test retrieval
        created_history = self.manager.create_object_with_history(self.sample_object_data)
        retrieved_history = self.manager.get_object_history(self.sample_object_data.object_id)

        self.assertIsNotNone(retrieved_history)
        self.assertEqual(retrieved_history.object_id, created_history.object_id)
        self.assertEqual(retrieved_history, created_history)

    def test_update_object_relationships_add(self):
        """Test adding object relationships."""
        # Create object first
        self.manager.create_object_with_history(self.sample_object_data)

        # Add relationships
        relationships = {
            'add': [
                {
                    'to_entity_id': 'character_1',
                    'to_entity_type': 'character',
                    'relationship_type': 'ownership',
                    'strength': 1.0
                },
                {
                    'to_entity_id': 'location_1',
                    'to_entity_type': 'location',
                    'relationship_type': 'location',
                    'strength': 0.8
                }
            ]
        }

        result = self.manager.update_object_relationships(self.sample_object_data.object_id, relationships)
        self.assertTrue(result)

        # Verify relationships were added
        object_history = self.manager.object_histories[self.sample_object_data.object_id]
        self.assertEqual(len(object_history.relationships), 2)

        # Check specific relationships
        ownership_rel = object_history.get_relationship('character_1', 'ownership')
        self.assertIsNotNone(ownership_rel)
        self.assertEqual(ownership_rel.strength, 1.0)

        location_rel = object_history.get_relationship('location_1', 'location')
        self.assertIsNotNone(location_rel)
        self.assertEqual(location_rel.strength, 0.8)

    def test_update_object_relationships_remove_and_update(self):
        """Test removing and updating object relationships."""
        # Create object and add initial relationships
        self.manager.create_object_with_history(self.sample_object_data)

        initial_relationships = {
            'add': [
                {
                    'to_entity_id': 'character_1',
                    'to_entity_type': 'character',
                    'relationship_type': 'ownership',
                    'strength': 1.0
                },
                {
                    'to_entity_id': 'character_2',
                    'to_entity_type': 'character',
                    'relationship_type': 'friendship',
                    'strength': 0.5
                }
            ]
        }

        self.manager.update_object_relationships(self.sample_object_data.object_id, initial_relationships)

        # Now remove one and update another
        update_relationships = {
            'remove': [
                {
                    'to_entity_id': 'character_1',
                    'relationship_type': 'ownership'
                }
            ],
            'update': [
                {
                    'to_entity_id': 'character_2',
                    'relationship_type': 'friendship',
                    'strength': 0.9
                }
            ]
        }

        result = self.manager.update_object_relationships(self.sample_object_data.object_id, update_relationships)
        self.assertTrue(result)

        # Verify changes
        object_history = self.manager.object_histories[self.sample_object_data.object_id]

        # Check removed relationship is inactive
        ownership_rel = object_history.get_relationship('character_1', 'ownership')
        self.assertIsNone(ownership_rel)  # Should return None for inactive relationships

        # Check updated relationship
        friendship_rel = object_history.get_relationship('character_2', 'friendship')
        self.assertIsNotNone(friendship_rel)
        self.assertEqual(friendship_rel.strength, 0.9)

    def test_update_object_relationships_object_not_found(self):
        """Test updating relationships for non-existent object."""
        relationships = {
            'add': [
                {
                    'to_entity_id': 'character_1',
                    'to_entity_type': 'character',
                    'relationship_type': 'ownership',
                    'strength': 1.0
                }
            ]
        }

        result = self.manager.update_object_relationships("non_existent_object", relationships)
        self.assertFalse(result)

    def test_simulate_object_wear(self):
        """Test object wear simulation from usage events."""
        # Create object first
        self.manager.create_object_with_history(self.sample_object_data)
        initial_condition = self.manager.object_histories[self.sample_object_data.object_id].object_state.current_condition

        # Create usage events
        usage_events = [
            TimelineEvent(
                event_type=EventType.PLAYER_INTERACTION,
                title="Combat Use",
                description="Sword used in combat",
                participants=[self.sample_object_data.object_id, "character_1"],
                significance_level=6,
                emotional_impact=-0.2
            ),
            TimelineEvent(
                event_type=EventType.CONFLICT,
                title="Intense Battle",
                description="Sword used in intense battle",
                participants=[self.sample_object_data.object_id, "character_1"],
                significance_level=8,
                emotional_impact=-0.5
            ),
            TimelineEvent(
                event_type=EventType.ENVIRONMENTAL_CHANGE,
                title="Weather Exposure",
                description="Sword exposed to harsh weather",
                participants=[self.sample_object_data.object_id],
                significance_level=3,
                emotional_impact=-0.1
            )
        ]

        # Simulate wear
        wear_state = self.manager.simulate_object_wear(self.sample_object_data.object_id, usage_events)

        # Verify simulation results
        self.assertTrue(wear_state.simulation_successful)
        self.assertEqual(wear_state.object_id, self.sample_object_data.object_id)
        self.assertEqual(wear_state.previous_condition, initial_condition)
        self.assertLess(wear_state.new_condition, wear_state.previous_condition)
        self.assertGreater(wear_state.wear_applied, 0.0)
        self.assertGreater(wear_state.wear_events_applied, 0)

        # Verify wear events were added to object history
        object_history = self.manager.object_histories[self.sample_object_data.object_id]
        usage_wear_events = [w for w in object_history.wear_timeline if w.wear_type == "usage"]
        self.assertGreater(len(usage_wear_events), 0)

    def test_simulate_object_wear_object_not_found(self):
        """Test wear simulation for non-existent object."""
        usage_events = [
            TimelineEvent(
                event_type=EventType.PLAYER_INTERACTION,
                title="Test Event",
                description="Test description",
                participants=["non_existent_object"]
            )
        ]

        wear_state = self.manager.simulate_object_wear("non_existent_object", usage_events)

        self.assertFalse(wear_state.simulation_successful)
        self.assertIn("Object not found", wear_state.error_message)

    def test_get_object_summary(self):
        """Test getting object summary."""
        # Test non-existent object
        summary = self.manager.get_object_summary("non_existent_object")
        self.assertIsNone(summary)

        # Create object and add some history
        self.manager.create_object_with_history(self.sample_object_data)

        # Add some interactions and wear
        interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description="Test interaction"
        )
        self.manager.handle_object_interaction(self.sample_object_data.object_id, interaction)

        # Get summary
        summary = self.manager.get_object_summary(self.sample_object_data.object_id)

        # Verify summary contents
        self.assertIsNotNone(summary)
        self.assertEqual(summary['object_id'], self.sample_object_data.object_id)
        self.assertEqual(summary['name'], self.sample_object_data.name)
        self.assertEqual(summary['type'], self.sample_object_data.object_type)
        self.assertEqual(summary['current_location'], self.sample_object_data.location_id)
        self.assertEqual(summary['current_owner'], self.sample_object_data.owner_id)
        self.assertIsNotNone(summary['creation_date'])
        self.assertGreaterEqual(summary['total_interactions'], 1)
        self.assertIn('wear_summary', summary)
        self.assertIn('last_updated', summary)

    def test_cleanup_old_events(self):
        """Test cleanup of old events."""
        # Create object with some history
        object_history = self.manager.create_object_with_history(self.sample_object_data)

        # Add old and new events
        old_timestamp = datetime.now() - timedelta(days=400)  # Very old
        recent_timestamp = datetime.now() - timedelta(days=10)  # Recent

        # Add old interaction event (low significance)
        old_interaction = TimelineEvent(
            event_type=EventType.PLAYER_INTERACTION,
            title="Old Interaction",
            description="Old interaction event",
            participants=[self.sample_object_data.object_id],
            timestamp=old_timestamp,
            significance_level=3  # Low significance
        )
        object_history.add_interaction_event(old_interaction)

        # Add old interaction event (high significance)
        old_important_interaction = TimelineEvent(
            event_type=EventType.PLAYER_INTERACTION,
            title="Important Old Interaction",
            description="Important old interaction event",
            participants=[self.sample_object_data.object_id],
            timestamp=old_timestamp,
            significance_level=8  # High significance
        )
        object_history.add_interaction_event(old_important_interaction)

        # Add recent interaction event
        recent_interaction = TimelineEvent(
            event_type=EventType.PLAYER_INTERACTION,
            title="Recent Interaction",
            description="Recent interaction event",
            participants=[self.sample_object_data.object_id],
            timestamp=recent_timestamp,
            significance_level=3  # Low significance but recent
        )
        object_history.add_interaction_event(recent_interaction)

        # Add old wear event
        old_wear = WearEvent(
            object_id=self.sample_object_data.object_id,
            wear_type="general",
            wear_amount=0.1,
            description="Old wear event",
            timestamp=old_timestamp
        )
        object_history.add_wear_event(old_wear)

        initial_interaction_count = len(object_history.interaction_events)
        len(object_history.wear_timeline)

        # Perform cleanup
        cleanup_results = self.manager.cleanup_old_events(days_to_keep=365, min_significance=7)

        # Verify cleanup results
        self.assertGreater(cleanup_results['total_events_removed'], 0)
        self.assertEqual(cleanup_results['objects_processed'], 1)

        # Verify that high-significance old events and recent events are kept
        updated_history = self.manager.object_histories[self.sample_object_data.object_id]

        # Should keep: important old interaction (high significance) + recent interaction
        # Should remove: old low-significance interaction
        remaining_interactions = updated_history.interaction_events
        self.assertLess(len(remaining_interactions), initial_interaction_count)

        # Check that important events are preserved
        important_titles = [event.title for event in remaining_interactions]
        self.assertIn("Important Old Interaction", important_titles)
        self.assertIn("Recent Interaction", important_titles)

    def test_get_manager_statistics(self):
        """Test getting manager statistics."""
        # Get initial statistics
        initial_stats = self.manager.get_manager_statistics()
        self.assertEqual(initial_stats['total_objects'], 0)

        # Create some objects
        self.manager.create_object_with_history(self.sample_object_data)

        object2_data = ObjectData(
            name="Test Shield",
            object_type="armor",
            initial_condition=0.8  # Slightly worn
        )
        self.manager.create_object_with_history(object2_data)

        # Add some interactions
        interaction = Interaction(
            object_id=self.sample_object_data.object_id,
            character_id="test_character_1",
            interaction_type="use",
            description="Test interaction"
        )
        self.manager.handle_object_interaction(self.sample_object_data.object_id, interaction)

        # Add relationships
        relationships = {
            'add': [
                {
                    'to_entity_id': 'character_1',
                    'to_entity_type': 'character',
                    'relationship_type': 'ownership',
                    'strength': 1.0
                }
            ]
        }
        self.manager.update_object_relationships(self.sample_object_data.object_id, relationships)

        # Get updated statistics
        stats = self.manager.get_manager_statistics()

        # Verify statistics
        self.assertEqual(stats['total_objects'], 2)
        self.assertEqual(stats['functional_objects'], 2)  # Both should be functional
        self.assertEqual(stats['broken_objects'], 0)
        self.assertGreaterEqual(stats['total_interactions'], 1)
        self.assertGreaterEqual(stats['total_relationships'], 1)
        self.assertGreater(stats['average_condition'], 0.0)
        self.assertGreaterEqual(stats['average_wear_level'], 0.0)
        self.assertTrue(stats['wear_simulation_enabled'])
        self.assertEqual(stats['aging_rate'], 1.0)
        self.assertEqual(stats['interaction_wear_multiplier'], 1.0)


class TestObjectData(unittest.TestCase):
    """Test cases for ObjectData class."""

    def test_object_data_creation(self):
        """Test ObjectData creation with default and custom values."""
        # Test with defaults
        data = ObjectData(name="Test Object", object_type="test")
        self.assertEqual(data.name, "Test Object")
        self.assertEqual(data.object_type, "test")
        self.assertEqual(data.initial_condition, 1.0)
        self.assertEqual(data.properties, {})
        self.assertEqual(data.tags, [])
        self.assertIsNone(data.location_id)
        self.assertIsNone(data.owner_id)

        # Test with custom values
        custom_data = ObjectData(
            name="Custom Object",
            object_type="custom",
            description="A custom test object",
            initial_condition=0.8,
            properties={"material": "wood", "size": "large"},
            tags=["custom", "test"],
            location_id="location_1",
            owner_id="owner_1",
            creation_context="Created for testing"
        )

        self.assertEqual(custom_data.name, "Custom Object")
        self.assertEqual(custom_data.object_type, "custom")
        self.assertEqual(custom_data.description, "A custom test object")
        self.assertEqual(custom_data.initial_condition, 0.8)
        self.assertEqual(custom_data.properties["material"], "wood")
        self.assertEqual(custom_data.tags, ["custom", "test"])
        self.assertEqual(custom_data.location_id, "location_1")
        self.assertEqual(custom_data.owner_id, "owner_1")
        self.assertEqual(custom_data.creation_context, "Created for testing")


class TestWearState(unittest.TestCase):
    """Test cases for WearState class."""

    def test_wear_state_creation(self):
        """Test WearState creation and default values."""
        wear_state = WearState(object_id="test_object")

        self.assertEqual(wear_state.object_id, "test_object")
        self.assertEqual(wear_state.previous_condition, 1.0)
        self.assertEqual(wear_state.new_condition, 1.0)
        self.assertEqual(wear_state.previous_wear_level, 0.0)
        self.assertEqual(wear_state.new_wear_level, 0.0)
        self.assertEqual(wear_state.wear_applied, 0.0)
        self.assertFalse(wear_state.functionality_changed)
        self.assertTrue(wear_state.was_functional)
        self.assertTrue(wear_state.is_functional)
        self.assertEqual(wear_state.wear_events_applied, 0)
        self.assertTrue(wear_state.simulation_successful)
        self.assertEqual(wear_state.error_message, "")


class TestInteraction(unittest.TestCase):
    """Test cases for Interaction class."""

    def test_interaction_creation(self):
        """Test Interaction creation with default and custom values."""
        # Test with minimal values
        interaction = Interaction(
            object_id="test_object",
            character_id="test_character",
            description="Test interaction"
        )

        self.assertEqual(interaction.object_id, "test_object")
        self.assertEqual(interaction.character_id, "test_character")
        self.assertEqual(interaction.interaction_type, "use")  # Default
        self.assertEqual(interaction.description, "Test interaction")
        self.assertEqual(interaction.intensity, 1.0)  # Default
        self.assertEqual(interaction.duration_minutes, 1)  # Default
        self.assertIsNone(interaction.location_id)
        self.assertEqual(interaction.consequences, [])
        self.assertEqual(interaction.metadata, {})

        # Test with custom values
        custom_interaction = Interaction(
            object_id="custom_object",
            character_id="custom_character",
            interaction_type="repair",
            description="Custom repair interaction",
            intensity=0.7,
            duration_minutes=45,
            location_id="workshop",
            consequences=["Object condition improved"],
            metadata={"tool_used": "hammer", "skill_level": 8}
        )

        self.assertEqual(custom_interaction.interaction_type, "repair")
        self.assertEqual(custom_interaction.intensity, 0.7)
        self.assertEqual(custom_interaction.duration_minutes, 45)
        self.assertEqual(custom_interaction.location_id, "workshop")
        self.assertEqual(custom_interaction.consequences, ["Object condition improved"])
        self.assertEqual(custom_interaction.metadata["tool_used"], "hammer")


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_create_sample_object_data(self):
        """Test create_sample_object_data utility function."""
        sample_data = create_sample_object_data("Test Item", "tool")

        self.assertEqual(sample_data.name, "Test Item")
        self.assertEqual(sample_data.object_type, "tool")
        self.assertIn("tool", sample_data.description.lower())
        self.assertEqual(sample_data.initial_condition, 1.0)
        self.assertIn("tool", sample_data.properties["material"])
        self.assertIn("tool", sample_data.tags)
        self.assertIn("sample", sample_data.tags)

    def test_create_sample_interaction(self):
        """Test create_sample_interaction utility function."""
        sample_interaction = create_sample_interaction("object_1", "character_1", "examine")

        self.assertEqual(sample_interaction.object_id, "object_1")
        self.assertEqual(sample_interaction.character_id, "character_1")
        self.assertEqual(sample_interaction.interaction_type, "examine")
        self.assertIn("character_1", sample_interaction.description)
        self.assertIn("object_1", sample_interaction.description)
        self.assertIn("examine", sample_interaction.description)
        self.assertEqual(sample_interaction.intensity, 0.5)
        self.assertEqual(sample_interaction.duration_minutes, 10)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests

    # Run the tests
    unittest.main(verbosity=2)
