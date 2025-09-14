"""
Unit Tests for Living Worlds Data Models

This module contains comprehensive unit tests for all living worlds data models
including Timeline, TimelineEvent, WorldState, and FamilyTree models.
Tests cover validation, serialization, deserialization, and edge cases.
"""

import json
import unittest
from datetime import datetime, timedelta

from tta.prototype.models.living_worlds_models import (
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
    validate_all_living_worlds_models,
)


class TestTimelineEvent(unittest.TestCase):
    """Test cases for TimelineEvent model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_event_data = {
            'title': 'Test Event',
            'description': 'A test event for unit testing',
            'participants': ['char1', 'char2'],
            'location_id': 'location1',
            'event_type': EventType.CONVERSATION,
            'emotional_impact': 0.5,
            'significance_level': 7,
            'consequences': ['Character relationship improved'],
            'tags': ['test', 'conversation']
        }

    def test_create_valid_event(self):
        """Test creating a valid timeline event."""
        event = TimelineEvent(**self.valid_event_data)
        self.assertTrue(event.validate())
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.event_type, EventType.CONVERSATION)
        self.assertEqual(len(event.participants), 2)

    def test_event_validation_empty_title(self):
        """Test validation fails with empty title."""
        data = self.valid_event_data.copy()
        data['title'] = ''
        event = TimelineEvent(**data)

        with self.assertRaises(ValidationError) as context:
            event.validate()
        self.assertIn('title cannot be empty', str(context.exception))

    def test_event_validation_empty_description(self):
        """Test validation fails with empty description."""
        data = self.valid_event_data.copy()
        data['description'] = ''
        event = TimelineEvent(**data)

        with self.assertRaises(ValidationError) as context:
            event.validate()
        self.assertIn('description cannot be empty', str(context.exception))

    def test_event_validation_invalid_emotional_impact(self):
        """Test validation fails with invalid emotional impact."""
        data = self.valid_event_data.copy()
        data['emotional_impact'] = 2.0  # Should be between -1.0 and 1.0
        event = TimelineEvent(**data)

        with self.assertRaises(ValidationError) as context:
            event.validate()
        self.assertIn('Emotional impact must be between -1.0 and 1.0', str(context.exception))

    def test_event_validation_invalid_significance_level(self):
        """Test validation fails with invalid significance level."""
        data = self.valid_event_data.copy()
        data['significance_level'] = 15  # Should be between 1 and 10
        event = TimelineEvent(**data)

        with self.assertRaises(ValidationError) as context:
            event.validate()
        self.assertIn('Significance level must be between 1 and 10', str(context.exception))

    def test_event_validation_future_timestamp(self):
        """Test validation fails with far future timestamp."""
        data = self.valid_event_data.copy()
        data['timestamp'] = datetime.now() + timedelta(days=5)  # Too far in future
        event = TimelineEvent(**data)

        with self.assertRaises(ValidationError) as context:
            event.validate()
        self.assertIn('timestamp cannot be more than 1 day in the future', str(context.exception))

    def test_event_serialization(self):
        """Test event serialization to dictionary."""
        event = TimelineEvent(**self.valid_event_data)
        event_dict = event.to_dict()

        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['title'], 'Test Event')
        self.assertEqual(event_dict['event_type'], EventType.CONVERSATION.value)
        self.assertIsInstance(event_dict['timestamp'], str)

    def test_event_deserialization(self):
        """Test event deserialization from dictionary."""
        event = TimelineEvent(**self.valid_event_data)
        event_dict = event.to_dict()

        restored_event = TimelineEvent.from_dict(event_dict)
        self.assertEqual(restored_event.title, event.title)
        self.assertEqual(restored_event.event_type, event.event_type)
        self.assertEqual(restored_event.participants, event.participants)

    def test_affects_entity(self):
        """Test checking if event affects specific entity."""
        event = TimelineEvent(**self.valid_event_data)

        self.assertTrue(event.affects_entity('char1'))
        self.assertTrue(event.affects_entity('char2'))
        self.assertTrue(event.affects_entity('location1'))
        self.assertFalse(event.affects_entity('char3'))

    def test_get_consequence_for_entity(self):
        """Test getting consequence for specific entity."""
        event = TimelineEvent(**self.valid_event_data)

        consequence = event.get_consequence_for_entity('char1')
        self.assertEqual(consequence, 'Character relationship improved')

        consequence = event.get_consequence_for_entity('char3')
        self.assertIsNone(consequence)


class TestTimeline(unittest.TestCase):
    """Test cases for Timeline model."""

    def setUp(self):
        """Set up test fixtures."""
        self.timeline = Timeline(
            entity_id='test_character',
            entity_type=EntityType.CHARACTER
        )

        self.event1 = TimelineEvent(
            title='First Event',
            description='The first event',
            timestamp=datetime.now() - timedelta(hours=2)
        )

        self.event2 = TimelineEvent(
            title='Second Event',
            description='The second event',
            timestamp=datetime.now() - timedelta(hours=1)
        )

    def test_create_valid_timeline(self):
        """Test creating a valid timeline."""
        self.assertTrue(self.timeline.validate())
        self.assertEqual(self.timeline.entity_type, EntityType.CHARACTER)
        self.assertEqual(len(self.timeline.events), 0)

    def test_timeline_validation_empty_entity_id(self):
        """Test validation fails with empty entity ID."""
        timeline = Timeline(entity_id='', entity_type=EntityType.CHARACTER)

        with self.assertRaises(ValidationError) as context:
            timeline.validate()
        self.assertIn('Entity ID cannot be empty', str(context.exception))

    def test_add_event_chronological_order(self):
        """Test adding events maintains chronological order."""
        # Add events in reverse chronological order
        self.assertTrue(self.timeline.add_event(self.event2))
        self.assertTrue(self.timeline.add_event(self.event1))

        # Events should be sorted chronologically
        self.assertEqual(len(self.timeline.events), 2)
        self.assertEqual(self.timeline.events[0].title, 'First Event')
        self.assertEqual(self.timeline.events[1].title, 'Second Event')

    def test_get_events_in_range(self):
        """Test getting events within time range."""
        self.timeline.add_event(self.event1)
        self.timeline.add_event(self.event2)

        start_time = datetime.now() - timedelta(hours=1.5)
        end_time = datetime.now()

        events_in_range = self.timeline.get_events_in_range(start_time, end_time)
        self.assertEqual(len(events_in_range), 1)
        self.assertEqual(events_in_range[0].title, 'Second Event')

    def test_get_events_by_type(self):
        """Test getting events by type."""
        event1 = TimelineEvent(
            title='Conversation',
            description='A conversation event',
            event_type=EventType.CONVERSATION
        )
        event2 = TimelineEvent(
            title='Travel',
            description='A travel event',
            event_type=EventType.TRAVEL
        )

        self.timeline.add_event(event1)
        self.timeline.add_event(event2)

        conversation_events = self.timeline.get_events_by_type(EventType.CONVERSATION)
        self.assertEqual(len(conversation_events), 1)
        self.assertEqual(conversation_events[0].title, 'Conversation')

    def test_get_events_by_significance(self):
        """Test getting events by significance level."""
        event1 = TimelineEvent(
            title='Minor Event',
            description='A minor event',
            significance_level=3
        )
        event2 = TimelineEvent(
            title='Major Event',
            description='A major event',
            significance_level=8
        )

        self.timeline.add_event(event1)
        self.timeline.add_event(event2)

        significant_events = self.timeline.get_events_by_significance(5)
        self.assertEqual(len(significant_events), 1)
        self.assertEqual(significant_events[0].title, 'Major Event')

    def test_get_recent_events(self):
        """Test getting recent events."""
        old_event = TimelineEvent(
            title='Old Event',
            description='An old event',
            timestamp=datetime.now() - timedelta(days=60)
        )
        recent_event = TimelineEvent(
            title='Recent Event',
            description='A recent event',
            timestamp=datetime.now() - timedelta(days=10)
        )

        self.timeline.add_event(old_event)
        self.timeline.add_event(recent_event)

        recent_events = self.timeline.get_recent_events(30)
        self.assertEqual(len(recent_events), 1)
        self.assertEqual(recent_events[0].title, 'Recent Event')

    def test_prune_old_events(self):
        """Test pruning old, low-significance events."""
        old_minor_event = TimelineEvent(
            title='Old Minor Event',
            description='An old minor event',
            timestamp=datetime.now() - timedelta(days=400),
            significance_level=3
        )
        old_major_event = TimelineEvent(
            title='Old Major Event',
            description='An old major event',
            timestamp=datetime.now() - timedelta(days=400),
            significance_level=9
        )
        recent_event = TimelineEvent(
            title='Recent Event',
            description='A recent event',
            timestamp=datetime.now() - timedelta(days=10),
            significance_level=3
        )

        self.timeline.add_event(old_minor_event)
        self.timeline.add_event(old_major_event)
        self.timeline.add_event(recent_event)

        removed_count = self.timeline.prune_old_events(keep_days=365, min_significance=7)

        self.assertEqual(removed_count, 1)  # Only old minor event should be removed
        self.assertEqual(len(self.timeline.events), 2)

        # Check that major and recent events remain
        titles = [event.title for event in self.timeline.events]
        self.assertIn('Old Major Event', titles)
        self.assertIn('Recent Event', titles)
        self.assertNotIn('Old Minor Event', titles)

    def test_timeline_serialization(self):
        """Test timeline serialization to dictionary."""
        self.timeline.add_event(self.event1)
        timeline_dict = self.timeline.to_dict()

        self.assertIsInstance(timeline_dict, dict)
        self.assertEqual(timeline_dict['entity_id'], 'test_character')
        self.assertEqual(timeline_dict['entity_type'], EntityType.CHARACTER.value)
        self.assertEqual(len(timeline_dict['events']), 1)

    def test_timeline_deserialization(self):
        """Test timeline deserialization from dictionary."""
        self.timeline.add_event(self.event1)
        timeline_dict = self.timeline.to_dict()

        restored_timeline = Timeline.from_dict(timeline_dict)
        self.assertEqual(restored_timeline.entity_id, self.timeline.entity_id)
        self.assertEqual(restored_timeline.entity_type, self.timeline.entity_type)
        self.assertEqual(len(restored_timeline.events), 1)


class TestFamilyRelationship(unittest.TestCase):
    """Test cases for FamilyRelationship model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_relationship_data = {
            'from_character_id': 'parent1',
            'to_character_id': 'child1',
            'relationship_type': RelationshipType.PARENT,
            'strength': 0.9,
            'notes': 'Strong parent-child bond'
        }

    def test_create_valid_relationship(self):
        """Test creating a valid family relationship."""
        relationship = FamilyRelationship(**self.valid_relationship_data)
        self.assertTrue(relationship.validate())
        self.assertEqual(relationship.relationship_type, RelationshipType.PARENT)
        self.assertEqual(relationship.strength, 0.9)

    def test_relationship_validation_empty_from_character(self):
        """Test validation fails with empty from_character_id."""
        data = self.valid_relationship_data.copy()
        data['from_character_id'] = ''
        relationship = FamilyRelationship(**data)

        with self.assertRaises(ValidationError) as context:
            relationship.validate()
        self.assertIn('From character ID cannot be empty', str(context.exception))

    def test_relationship_validation_same_character(self):
        """Test validation fails when character has relationship with themselves."""
        data = self.valid_relationship_data.copy()
        data['to_character_id'] = data['from_character_id']
        relationship = FamilyRelationship(**data)

        with self.assertRaises(ValidationError) as context:
            relationship.validate()
        self.assertIn('Character cannot have relationship with themselves', str(context.exception))

    def test_relationship_validation_invalid_strength(self):
        """Test validation fails with invalid strength value."""
        data = self.valid_relationship_data.copy()
        data['strength'] = 1.5  # Should be between 0.0 and 1.0
        relationship = FamilyRelationship(**data)

        with self.assertRaises(ValidationError) as context:
            relationship.validate()
        self.assertIn('Relationship strength must be between 0.0 and 1.0', str(context.exception))

    def test_relationship_serialization(self):
        """Test relationship serialization to dictionary."""
        relationship = FamilyRelationship(**self.valid_relationship_data)
        relationship_dict = relationship.to_dict()

        self.assertIsInstance(relationship_dict, dict)
        self.assertEqual(relationship_dict['from_character_id'], 'parent1')
        self.assertEqual(relationship_dict['relationship_type'], RelationshipType.PARENT.value)

    def test_relationship_deserialization(self):
        """Test relationship deserialization from dictionary."""
        relationship = FamilyRelationship(**self.valid_relationship_data)
        relationship_dict = relationship.to_dict()

        restored_relationship = FamilyRelationship.from_dict(relationship_dict)
        self.assertEqual(restored_relationship.from_character_id, relationship.from_character_id)
        self.assertEqual(restored_relationship.relationship_type, relationship.relationship_type)


class TestFamilyTree(unittest.TestCase):
    """Test cases for FamilyTree model."""

    def setUp(self):
        """Set up test fixtures."""
        self.family_tree = FamilyTree(root_character_id='root_char')

        self.family_event = TimelineEvent(
            title='Family Reunion',
            description='Annual family gathering',
            participants=['root_char', 'parent1', 'child1'],
            event_type=EventType.FAMILY_EVENT
        )

    def test_create_valid_family_tree(self):
        """Test creating a valid family tree."""
        self.assertTrue(self.family_tree.validate())
        self.assertEqual(self.family_tree.root_character_id, 'root_char')
        self.assertEqual(len(self.family_tree.relationships), 0)

    def test_family_tree_validation_empty_root_character(self):
        """Test validation fails with empty root character ID."""
        tree = FamilyTree(root_character_id='')

        with self.assertRaises(ValidationError) as context:
            tree.validate()
        self.assertIn('Root character ID cannot be empty', str(context.exception))

    def test_add_relationship(self):
        """Test adding family relationships."""
        success = self.family_tree.add_relationship(
            'parent1', 'child1', RelationshipType.PARENT, 0.9
        )
        self.assertTrue(success)
        self.assertEqual(len(self.family_tree.relationships), 1)

        # Test adding duplicate relationship
        success = self.family_tree.add_relationship(
            'parent1', 'child1', RelationshipType.PARENT, 0.8
        )
        self.assertFalse(success)  # Should fail due to duplicate
        self.assertEqual(len(self.family_tree.relationships), 1)  # Count unchanged

    def test_get_parents(self):
        """Test getting parent character IDs."""
        self.family_tree.add_relationship('parent1', 'child1', RelationshipType.PARENT)
        self.family_tree.add_relationship('parent2', 'child1', RelationshipType.PARENT)

        parents = self.family_tree.get_parents('child1')
        self.assertEqual(len(parents), 2)
        self.assertIn('parent1', parents)
        self.assertIn('parent2', parents)

    def test_get_children(self):
        """Test getting child character IDs."""
        self.family_tree.add_relationship('parent1', 'child1', RelationshipType.PARENT)
        self.family_tree.add_relationship('parent1', 'child2', RelationshipType.PARENT)

        children = self.family_tree.get_children('parent1')
        self.assertEqual(len(children), 2)
        self.assertIn('child1', children)
        self.assertIn('child2', children)

    def test_get_siblings(self):
        """Test getting sibling character IDs."""
        self.family_tree.add_relationship('child1', 'child2', RelationshipType.SIBLING)

        siblings = self.family_tree.get_siblings('child1')
        self.assertEqual(len(siblings), 1)
        self.assertIn('child2', siblings)

        siblings = self.family_tree.get_siblings('child2')
        self.assertEqual(len(siblings), 1)
        self.assertIn('child1', siblings)

    def test_get_extended_family(self):
        """Test getting extended family members."""
        # Add grandparent relationship
        self.family_tree.add_relationship('grandparent1', 'root_char', RelationshipType.GRANDPARENT)

        # Add aunt/uncle relationship
        self.family_tree.add_relationship('root_char', 'aunt1', RelationshipType.AUNT_UNCLE)

        extended = self.family_tree.get_extended_family('root_char')

        self.assertEqual(len(extended['grandparents']), 1)
        self.assertIn('grandparent1', extended['grandparents'])

        self.assertEqual(len(extended['aunts_uncles']), 1)
        self.assertIn('aunt1', extended['aunts_uncles'])

    def test_add_family_event(self):
        """Test adding family events."""
        success = self.family_tree.add_family_event(self.family_event)
        self.assertTrue(success)
        self.assertEqual(len(self.family_tree.family_events), 1)

        # Test adding event that doesn't involve family members
        non_family_event = TimelineEvent(
            title='Non-family Event',
            description='Event not involving family',
            participants=['stranger1', 'stranger2']
        )
        success = self.family_tree.add_family_event(non_family_event)
        self.assertFalse(success)
        self.assertEqual(len(self.family_tree.family_events), 1)  # Count unchanged

    def test_get_family_history(self):
        """Test getting family history."""
        # Add old event
        old_event = TimelineEvent(
            title='Old Family Event',
            description='An old family event',
            participants=['root_char'],
            timestamp=datetime.now() - timedelta(days=365 * 60)  # 60 years ago
        )

        # Add recent event
        recent_event = TimelineEvent(
            title='Recent Family Event',
            description='A recent family event',
            participants=['root_char'],
            timestamp=datetime.now() - timedelta(days=30)
        )

        self.family_tree.add_family_event(old_event)
        self.family_tree.add_family_event(recent_event)

        # Get history for last 50 years
        history = self.family_tree.get_family_history(50)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].title, 'Recent Family Event')

    def test_family_tree_serialization(self):
        """Test family tree serialization to dictionary."""
        self.family_tree.add_relationship('parent1', 'child1', RelationshipType.PARENT)
        self.family_tree.add_family_event(self.family_event)

        tree_dict = self.family_tree.to_dict()

        self.assertIsInstance(tree_dict, dict)
        self.assertEqual(tree_dict['root_character_id'], 'root_char')
        self.assertEqual(len(tree_dict['relationships']), 1)
        self.assertEqual(len(tree_dict['family_events']), 1)

    def test_family_tree_deserialization(self):
        """Test family tree deserialization from dictionary."""
        self.family_tree.add_relationship('parent1', 'child1', RelationshipType.PARENT)
        tree_dict = self.family_tree.to_dict()

        restored_tree = FamilyTree.from_dict(tree_dict)
        self.assertEqual(restored_tree.root_character_id, self.family_tree.root_character_id)
        self.assertEqual(len(restored_tree.relationships), 1)


class TestWorldState(unittest.TestCase):
    """Test cases for WorldState model."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_state = WorldState(
            world_id='test_world',
            world_name='Test World'
        )

    def test_create_valid_world_state(self):
        """Test creating a valid world state."""
        self.assertTrue(self.world_state.validate())
        self.assertEqual(self.world_state.world_name, 'Test World')
        self.assertEqual(self.world_state.world_status, WorldStateFlag.ACTIVE)

    def test_world_state_validation_empty_world_id(self):
        """Test validation fails with empty world ID."""
        world = WorldState(world_id='', world_name='Test World')

        with self.assertRaises(ValidationError) as context:
            world.validate()
        self.assertIn('World ID cannot be empty', str(context.exception))

    def test_world_state_validation_empty_world_name(self):
        """Test validation fails with empty world name."""
        world = WorldState(world_id='test', world_name='')

        with self.assertRaises(ValidationError) as context:
            world.validate()
        self.assertIn('World name cannot be empty', str(context.exception))

    def test_world_state_validation_future_time(self):
        """Test validation fails with far future world time."""
        world = WorldState(
            world_id='test',
            world_name='Test World',
            current_time=datetime.now() + timedelta(days=5)
        )

        with self.assertRaises(ValidationError) as context:
            world.validate()
        self.assertIn('World time cannot be more than 1 day in the future', str(context.exception))

    def test_add_character(self):
        """Test adding characters to world state."""
        character_data = {'name': 'Test Character', 'level': 5}
        success = self.world_state.add_character('char1', character_data)

        self.assertTrue(success)
        self.assertIn('char1', self.world_state.active_characters)
        self.assertEqual(self.world_state.active_characters['char1']['name'], 'Test Character')

    def test_remove_character(self):
        """Test removing characters from world state."""
        self.world_state.add_character('char1', {'name': 'Test Character'})

        success = self.world_state.remove_character('char1')
        self.assertTrue(success)
        self.assertNotIn('char1', self.world_state.active_characters)

        # Test removing non-existent character
        success = self.world_state.remove_character('char2')
        self.assertFalse(success)

    def test_add_location(self):
        """Test adding locations to world state."""
        location_data = {'name': 'Test Location', 'type': 'forest'}
        success = self.world_state.add_location('loc1', location_data)

        self.assertTrue(success)
        self.assertIn('loc1', self.world_state.active_locations)
        self.assertEqual(self.world_state.active_locations['loc1']['name'], 'Test Location')

    def test_add_object(self):
        """Test adding objects to world state."""
        object_data = {'name': 'Test Object', 'durability': 100}
        success = self.world_state.add_object('obj1', object_data)

        self.assertTrue(success)
        self.assertIn('obj1', self.world_state.active_objects)
        self.assertEqual(self.world_state.active_objects['obj1']['name'], 'Test Object')

    def test_world_flags(self):
        """Test setting and getting world flags."""
        self.world_state.set_flag('weather', 'sunny')
        self.world_state.set_flag('season', 'spring')

        self.assertEqual(self.world_state.get_flag('weather'), 'sunny')
        self.assertEqual(self.world_state.get_flag('season'), 'spring')
        self.assertEqual(self.world_state.get_flag('nonexistent', 'default'), 'default')

    def test_schedule_evolution_task(self):
        """Test scheduling evolution tasks."""
        future_time = datetime.now() + timedelta(hours=1)
        task_data = {'type': 'weather_change', 'new_weather': 'rainy'}

        success = self.world_state.schedule_evolution_task(
            'weather_update', future_time, task_data
        )

        self.assertTrue(success)
        self.assertEqual(len(self.world_state.evolution_schedule), 1)

        task = self.world_state.evolution_schedule[0]
        self.assertEqual(task['task_type'], 'weather_update')
        self.assertEqual(task['task_data'], task_data)

    def test_schedule_evolution_task_past_time(self):
        """Test scheduling evolution task with past time fails."""
        past_time = datetime.now() - timedelta(hours=1)

        success = self.world_state.schedule_evolution_task(
            'weather_update', past_time, {}
        )

        self.assertFalse(success)
        self.assertEqual(len(self.world_state.evolution_schedule), 0)

    def test_get_pending_evolution_tasks(self):
        """Test getting pending evolution tasks."""
        # Schedule tasks at different times
        now = datetime.now()
        past_time = now - timedelta(minutes=30)
        future_time = now + timedelta(minutes=30)

        self.world_state.schedule_evolution_task('past_task', past_time, {})
        self.world_state.schedule_evolution_task('future_task', future_time, {})

        # Manually add past task (bypassing validation for testing)
        past_task = {
            'task_id': 'past_task_id',
            'task_type': 'past_task',
            'scheduled_time': past_time.isoformat(),
            'task_data': {},
            'created_at': now.isoformat()
        }
        self.world_state.evolution_schedule.insert(0, past_task)

        pending_tasks = self.world_state.get_pending_evolution_tasks(now)
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0]['task_type'], 'past_task')

    def test_complete_evolution_task(self):
        """Test completing evolution tasks."""
        future_time = datetime.now() + timedelta(hours=1)
        self.world_state.schedule_evolution_task('test_task', future_time, {})

        task_id = self.world_state.evolution_schedule[0]['task_id']
        success = self.world_state.complete_evolution_task(task_id)

        self.assertTrue(success)
        self.assertEqual(len(self.world_state.evolution_schedule), 0)

        # Test completing non-existent task
        success = self.world_state.complete_evolution_task('nonexistent')
        self.assertFalse(success)

    def test_advance_time(self):
        """Test advancing world time."""
        initial_time = self.world_state.current_time
        time_delta = timedelta(hours=2)

        self.world_state.advance_time(time_delta)

        expected_time = initial_time + time_delta
        self.assertEqual(self.world_state.current_time, expected_time)

    def test_record_player_visit(self):
        """Test recording player visits."""
        self.assertIsNone(self.world_state.player_last_visit)

        self.world_state.record_player_visit()

        self.assertIsNotNone(self.world_state.player_last_visit)
        self.assertIsInstance(self.world_state.player_last_visit, datetime)

    def test_get_time_since_player_visit(self):
        """Test getting time since player visit."""
        # No visit recorded yet
        time_since = self.world_state.get_time_since_player_visit()
        self.assertIsNone(time_since)

        # Record visit and check time
        self.world_state.record_player_visit()
        time_since = self.world_state.get_time_since_player_visit()

        self.assertIsNotNone(time_since)
        self.assertIsInstance(time_since, timedelta)
        self.assertLess(time_since.total_seconds(), 1)  # Should be very recent

    def test_world_state_serialization(self):
        """Test world state serialization to dictionary and JSON."""
        self.world_state.add_character('char1', {'name': 'Test Character'})
        self.world_state.set_flag('weather', 'sunny')

        # Test to_dict
        world_dict = self.world_state.to_dict()
        self.assertIsInstance(world_dict, dict)
        self.assertEqual(world_dict['world_name'], 'Test World')
        self.assertEqual(world_dict['world_status'], WorldStateFlag.ACTIVE.value)

        # Test to_json
        world_json = self.world_state.to_json()
        self.assertIsInstance(world_json, str)

        # Verify JSON can be parsed
        parsed_data = json.loads(world_json)
        self.assertEqual(parsed_data['world_name'], 'Test World')

    def test_world_state_deserialization(self):
        """Test world state deserialization from dictionary and JSON."""
        self.world_state.add_character('char1', {'name': 'Test Character'})
        self.world_state.record_player_visit()

        # Test from_dict
        world_dict = self.world_state.to_dict()
        restored_world = WorldState.from_dict(world_dict)

        self.assertEqual(restored_world.world_name, self.world_state.world_name)
        self.assertEqual(restored_world.world_status, self.world_state.world_status)
        self.assertIn('char1', restored_world.active_characters)

        # Test from_json
        world_json = self.world_state.to_json()
        restored_world_json = WorldState.from_json(world_json)

        self.assertEqual(restored_world_json.world_name, self.world_state.world_name)
        self.assertIsNotNone(restored_world_json.player_last_visit)


class TestValidationUtilities(unittest.TestCase):
    """Test cases for validation utility functions."""

    def test_validate_all_living_worlds_models(self):
        """Test the validation utility function."""
        result = validate_all_living_worlds_models()
        self.assertTrue(result)


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error conditions."""

    def test_timeline_with_many_events(self):
        """Test timeline performance with many events."""
        timeline = Timeline(entity_id='test', entity_type=EntityType.CHARACTER)

        # Add 1000 events
        base_time = datetime.now() - timedelta(days=365)
        for i in range(1000):
            event = TimelineEvent(
                title=f'Event {i}',
                description=f'Description for event {i}',
                timestamp=base_time + timedelta(hours=i)
            )
            timeline.add_event(event)

        self.assertEqual(len(timeline.events), 1000)
        self.assertTrue(timeline.validate())

        # Test pruning
        removed = timeline.prune_old_events(keep_days=30, min_significance=8)
        self.assertGreater(removed, 0)
        self.assertLess(len(timeline.events), 1000)

    def test_family_tree_complex_relationships(self):
        """Test family tree with complex relationship structures."""
        tree = FamilyTree(root_character_id='person1')

        # Create a multi-generational family
        # Grandparents
        tree.add_relationship('grandpa', 'parent1', RelationshipType.GRANDPARENT)
        tree.add_relationship('grandma', 'parent1', RelationshipType.GRANDPARENT)

        # Parents and children
        tree.add_relationship('parent1', 'person1', RelationshipType.PARENT)
        tree.add_relationship('parent2', 'person1', RelationshipType.PARENT)
        tree.add_relationship('person1', 'child1', RelationshipType.PARENT)
        tree.add_relationship('person1', 'child2', RelationshipType.PARENT)

        # Siblings
        tree.add_relationship('person1', 'sibling1', RelationshipType.SIBLING)
        tree.add_relationship('child1', 'child2', RelationshipType.SIBLING)

        # Extended family
        tree.add_relationship('person1', 'cousin1', RelationshipType.COUSIN)
        tree.add_relationship('person1', 'uncle1', RelationshipType.AUNT_UNCLE)

        self.assertTrue(tree.validate())

        # Test relationship queries
        parents = tree.get_parents('person1')
        self.assertEqual(len(parents), 2)

        children = tree.get_children('person1')
        self.assertEqual(len(children), 2)

        siblings = tree.get_siblings('person1')
        self.assertEqual(len(siblings), 1)

        extended = tree.get_extended_family('person1')
        self.assertEqual(len(extended['cousins']), 1)
        self.assertEqual(len(extended['aunts_uncles']), 1)

    def test_world_state_large_scale(self):
        """Test world state with large numbers of entities."""
        world = WorldState(world_id='large_world', world_name='Large World')

        # Add many characters, locations, and objects
        for i in range(100):
            world.add_character(f'char_{i}', {'name': f'Character {i}', 'level': i})
            world.add_location(f'loc_{i}', {'name': f'Location {i}', 'type': 'area'})
            world.add_object(f'obj_{i}', {'name': f'Object {i}', 'value': i * 10})

        # Add many evolution tasks
        base_time = datetime.now() + timedelta(minutes=1)
        for i in range(50):
            world.schedule_evolution_task(
                f'task_{i}',
                base_time + timedelta(minutes=i),
                {'data': f'task_data_{i}'}
            )

        self.assertTrue(world.validate())
        self.assertEqual(len(world.active_characters), 100)
        self.assertEqual(len(world.active_locations), 100)
        self.assertEqual(len(world.active_objects), 100)
        self.assertEqual(len(world.evolution_schedule), 50)

        # Test serialization performance
        world_dict = world.to_dict()
        self.assertIsInstance(world_dict, dict)

        world_json = world.to_json()
        self.assertIsInstance(world_json, str)

        # Test deserialization
        restored_world = WorldState.from_json(world_json)
        self.assertEqual(len(restored_world.active_characters), 100)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests

    # Run all tests
    unittest.main(verbosity=2)


class TestNeo4jSerialization(unittest.TestCase):
    """Test cases for Neo4j serialization/deserialization."""

    def test_timeline_event_neo4j_serialization(self):
        """Test TimelineEvent Neo4j serialization."""
        event = TimelineEvent(
            title='Test Event',
            description='A test event',
            participants=['char1', 'char2'],
            location_id='location1',
            event_type=EventType.CONVERSATION,
            emotional_impact=0.5,
            significance_level=7,
            consequences=['Improved relationship'],
            tags=['test', 'conversation'],
            metadata={'custom_data': 'test_value'}
        )

        # Test serialization
        props = event.to_neo4j_properties()
        self.assertIsInstance(props, dict)
        self.assertEqual(props['title'], 'Test Event')
        self.assertEqual(props['event_type'], EventType.CONVERSATION.value)
        self.assertIsInstance(props['timestamp'], str)
        self.assertIsInstance(props['metadata'], str)  # Should be JSON string

        # Test deserialization
        restored_event = TimelineEvent.from_neo4j_properties(props)
        self.assertEqual(restored_event.title, event.title)
        self.assertEqual(restored_event.event_type, event.event_type)
        self.assertEqual(restored_event.participants, event.participants)
        self.assertEqual(restored_event.metadata, event.metadata)

        # Test relationships
        relationships = event.get_neo4j_relationships()
        self.assertIsInstance(relationships, list)
        self.assertGreater(len(relationships), 0)

        # Should have relationships to participants and location
        participant_rels = [r for r in relationships if r['type'] == 'INVOLVES']
        location_rels = [r for r in relationships if r['type'] == 'OCCURRED_AT']

        self.assertEqual(len(participant_rels), 2)  # Two participants
        self.assertEqual(len(location_rels), 1)  # One location

    def test_timeline_neo4j_serialization(self):
        """Test Timeline Neo4j serialization."""
        timeline = Timeline(
            entity_id='test_character',
            entity_type=EntityType.CHARACTER,
            metadata={'custom_info': 'timeline_data'}
        )

        event = TimelineEvent(
            title='Test Event',
            description='A test event'
        )
        timeline.add_event(event)

        # Test serialization
        props = timeline.to_neo4j_properties()
        self.assertIsInstance(props, dict)
        self.assertEqual(props['entity_id'], 'test_character')
        self.assertEqual(props['entity_type'], EntityType.CHARACTER.value)
        self.assertEqual(props['event_count'], 1)
        self.assertIsInstance(props['metadata'], str)  # Should be JSON string

        # Test deserialization
        restored_timeline = Timeline.from_neo4j_properties(props)
        self.assertEqual(restored_timeline.entity_id, timeline.entity_id)
        self.assertEqual(restored_timeline.entity_type, timeline.entity_type)
        self.assertEqual(restored_timeline.metadata, timeline.metadata)

        # Test relationships
        relationships = timeline.get_neo4j_relationships()
        self.assertIsInstance(relationships, list)
        self.assertGreater(len(relationships), 0)

        # Should have relationship to entity and events
        entity_rels = [r for r in relationships if r['type'] == 'BELONGS_TO']
        event_rels = [r for r in relationships if r['type'] == 'CONTAINS']

        self.assertEqual(len(entity_rels), 1)  # One entity
        self.assertEqual(len(event_rels), 1)  # One event

    def test_family_relationship_neo4j_serialization(self):
        """Test FamilyRelationship Neo4j serialization."""
        relationship = FamilyRelationship(
            from_character_id='parent1',
            to_character_id='child1',
            relationship_type=RelationshipType.PARENT,
            strength=0.9,
            notes='Strong parent-child bond'
        )

        # Test serialization
        props = relationship.to_neo4j_properties()
        self.assertIsInstance(props, dict)
        self.assertEqual(props['from_character_id'], 'parent1')
        self.assertEqual(props['relationship_type'], RelationshipType.PARENT.value)
        self.assertEqual(props['strength'], 0.9)
        self.assertIsInstance(props['established_date'], str)

        # Test deserialization
        restored_rel = FamilyRelationship.from_neo4j_properties(props)
        self.assertEqual(restored_rel.from_character_id, relationship.from_character_id)
        self.assertEqual(restored_rel.relationship_type, relationship.relationship_type)
        self.assertEqual(restored_rel.strength, relationship.strength)

        # Test relationships
        relationships = relationship.get_neo4j_relationships()
        self.assertIsInstance(relationships, list)
        self.assertEqual(len(relationships), 2)  # FROM_CHARACTER and TO_CHARACTER

        from_rels = [r for r in relationships if r['type'] == 'FROM_CHARACTER']
        to_rels = [r for r in relationships if r['type'] == 'TO_CHARACTER']

        self.assertEqual(len(from_rels), 1)
        self.assertEqual(len(to_rels), 1)

    def test_family_tree_neo4j_serialization(self):
        """Test FamilyTree Neo4j serialization."""
        family_tree = FamilyTree(
            root_character_id='root_char',
            generations_tracked=3,
            metadata={'family_name': 'Test Family'}
        )

        # Add a relationship and event
        family_tree.add_relationship('parent1', 'child1', RelationshipType.PARENT)

        family_event = TimelineEvent(
            title='Family Event',
            description='A family gathering',
            participants=['root_char', 'parent1']
        )
        family_tree.add_family_event(family_event)

        # Test serialization
        props = family_tree.to_neo4j_properties()
        self.assertIsInstance(props, dict)
        self.assertEqual(props['root_character_id'], 'root_char')
        self.assertEqual(props['generations_tracked'], 3)
        self.assertEqual(props['relationship_count'], 1)
        self.assertEqual(props['family_event_count'], 1)
        self.assertIsInstance(props['metadata'], str)  # Should be JSON string

        # Test deserialization
        restored_tree = FamilyTree.from_neo4j_properties(props)
        self.assertEqual(restored_tree.root_character_id, family_tree.root_character_id)
        self.assertEqual(restored_tree.generations_tracked, family_tree.generations_tracked)
        self.assertEqual(restored_tree.metadata, family_tree.metadata)

        # Test relationships
        relationships = family_tree.get_neo4j_relationships()
        self.assertIsInstance(relationships, list)
        self.assertGreater(len(relationships), 0)

        # Should have relationships to root character, family relationships, and events
        root_rels = [r for r in relationships if r['type'] == 'ROOTED_AT']
        include_rels = [r for r in relationships if r['type'] == 'INCLUDES']
        record_rels = [r for r in relationships if r['type'] == 'RECORDS']

        self.assertEqual(len(root_rels), 1)  # One root character
        self.assertEqual(len(include_rels), 1)  # One relationship
        self.assertEqual(len(record_rels), 1)  # One family event

    def test_world_state_neo4j_serialization(self):
        """Test WorldState Neo4j serialization."""
        world_state = WorldState(
            world_id='test_world',
            world_name='Test World',
            world_status=WorldStateFlag.ACTIVE,
            metadata={'theme': 'fantasy'}
        )

        # Add entities
        world_state.add_character('char1', {'name': 'Test Character'})
        world_state.add_location('loc1', {'name': 'Test Location'})
        world_state.add_object('obj1', {'name': 'Test Object'})
        world_state.set_flag('weather', 'sunny')
        world_state.record_player_visit()

        # Test serialization
        props = world_state.to_neo4j_properties()
        self.assertIsInstance(props, dict)
        self.assertEqual(props['world_id'], 'test_world')
        self.assertEqual(props['world_name'], 'Test World')
        self.assertEqual(props['world_status'], WorldStateFlag.ACTIVE.value)
        self.assertEqual(props['character_count'], 1)
        self.assertEqual(props['location_count'], 1)
        self.assertEqual(props['object_count'], 1)
        self.assertIsInstance(props['world_flags'], str)  # Should be JSON string
        self.assertIsInstance(props['metadata'], str)  # Should be JSON string
        self.assertIsNotNone(props['player_last_visit'])

        # Test deserialization
        restored_world = WorldState.from_neo4j_properties(props)
        self.assertEqual(restored_world.world_id, world_state.world_id)
        self.assertEqual(restored_world.world_name, world_state.world_name)
        self.assertEqual(restored_world.world_status, world_state.world_status)
        self.assertEqual(restored_world.world_flags, world_state.world_flags)
        self.assertEqual(restored_world.metadata, world_state.metadata)
        self.assertIsNotNone(restored_world.player_last_visit)

        # Test relationships
        relationships = world_state.get_neo4j_relationships()
        self.assertIsInstance(relationships, list)
        self.assertEqual(len(relationships), 3)  # One each for character, location, object

        char_rels = [r for r in relationships if r['type'] == 'CONTAINS_CHARACTER']
        loc_rels = [r for r in relationships if r['type'] == 'CONTAINS_LOCATION']
        obj_rels = [r for r in relationships if r['type'] == 'CONTAINS_OBJECT']

        self.assertEqual(len(char_rels), 1)
        self.assertEqual(len(loc_rels), 1)
        self.assertEqual(len(obj_rels), 1)

    def test_neo4j_serialization_roundtrip(self):
        """Test complete roundtrip serialization for all models."""
        # Create complex data structure
        world_state = WorldState(world_id='complex_world', world_name='Complex World')
        world_state.add_character('char1', {'name': 'Character 1'})

        timeline = Timeline(entity_id='char1', entity_type=EntityType.CHARACTER)

        event1 = TimelineEvent(
            title='Birth',
            description='Character was born',
            event_type=EventType.BIRTH,
            significance_level=10
        )

        event2 = TimelineEvent(
            title='Meeting',
            description='Met another character',
            participants=['char1', 'char2'],
            event_type=EventType.MEETING,
            significance_level=6
        )

        timeline.add_event(event1)
        timeline.add_event(event2)

        family_tree = FamilyTree(root_character_id='char1')
        family_tree.add_relationship('parent1', 'char1', RelationshipType.PARENT)

        # Test serialization and deserialization for all models
        models_and_data = [
            (world_state, WorldState),
            (timeline, Timeline),
            (event1, TimelineEvent),
            (event2, TimelineEvent),
            (family_tree, FamilyTree)
        ]

        for original_model, model_class in models_and_data:
            with self.subTest(model=model_class.__name__):
                # Serialize to Neo4j properties
                props = original_model.to_neo4j_properties()
                self.assertIsInstance(props, dict)

                # Deserialize back to model
                restored_model = model_class.from_neo4j_properties(props)

                # Validate the restored model
                self.assertTrue(restored_model.validate())

                # Check that key properties are preserved
                if hasattr(original_model, 'world_id'):
                    self.assertEqual(restored_model.world_id, original_model.world_id)
                if hasattr(original_model, 'timeline_id'):
                    self.assertEqual(restored_model.timeline_id, original_model.timeline_id)
                if hasattr(original_model, 'event_id'):
                    self.assertEqual(restored_model.event_id, original_model.event_id)
                if hasattr(original_model, 'tree_id'):
                    self.assertEqual(restored_model.tree_id, original_model.tree_id)


class TestNeo4jSchemaUtilities(unittest.TestCase):
    """Test cases for Neo4j schema utility functions."""

    def test_get_living_worlds_neo4j_constraints(self):
        """Test getting Neo4j constraints for living worlds."""
        from tta.prototype.models.living_worlds_models import (
            get_living_worlds_neo4j_constraints,
        )

        constraints = get_living_worlds_neo4j_constraints()
        self.assertIsInstance(constraints, list)
        self.assertGreater(len(constraints), 0)

        # Check that all expected constraints are present
        constraint_text = ' '.join(constraints)
        self.assertIn('timeline_id', constraint_text)
        self.assertIn('timeline_event_id', constraint_text)
        self.assertIn('family_tree_id', constraint_text)
        self.assertIn('family_relationship_id', constraint_text)
        self.assertIn('world_state_id', constraint_text)

    def test_get_living_worlds_neo4j_indexes(self):
        """Test getting Neo4j indexes for living worlds."""
        from tta.prototype.models.living_worlds_models import (
            get_living_worlds_neo4j_indexes,
        )

        indexes = get_living_worlds_neo4j_indexes()
        self.assertIsInstance(indexes, list)
        self.assertGreater(len(indexes), 0)

        # Check that indexes cover important fields
        index_text = ' '.join(indexes)
        self.assertIn('timeline_entity_id', index_text)
        self.assertIn('timeline_event_timestamp', index_text)
        self.assertIn('family_relationship_type', index_text)
        self.assertIn('world_state_status', index_text)

    def test_validate_living_worlds_neo4j_serialization(self):
        """Test the Neo4j serialization validation utility."""
        from tta.prototype.models.living_worlds_models import (
            validate_living_worlds_neo4j_serialization,
        )

        result = validate_living_worlds_neo4j_serialization()
        self.assertTrue(result)


class TestNeo4jIntegrationScenarios(unittest.TestCase):
    """Test cases for complex Neo4j integration scenarios."""

    def test_complex_family_tree_serialization(self):
        """Test serialization of complex family tree with multiple generations."""
        # Create a multi-generational family tree
        family_tree = FamilyTree(root_character_id='person1', generations_tracked=4)

        # Add grandparents
        family_tree.add_relationship('grandpa_paternal', 'father', RelationshipType.GRANDPARENT)
        family_tree.add_relationship('grandma_paternal', 'father', RelationshipType.GRANDPARENT)
        family_tree.add_relationship('grandpa_maternal', 'mother', RelationshipType.GRANDPARENT)
        family_tree.add_relationship('grandma_maternal', 'mother', RelationshipType.GRANDPARENT)

        # Add parents
        family_tree.add_relationship('father', 'person1', RelationshipType.PARENT)
        family_tree.add_relationship('mother', 'person1', RelationshipType.PARENT)

        # Add siblings
        family_tree.add_relationship('person1', 'sibling1', RelationshipType.SIBLING)
        family_tree.add_relationship('person1', 'sibling2', RelationshipType.SIBLING)

        # Add children
        family_tree.add_relationship('person1', 'child1', RelationshipType.PARENT)
        family_tree.add_relationship('person1', 'child2', RelationshipType.PARENT)

        # Add extended family
        family_tree.add_relationship('person1', 'cousin1', RelationshipType.COUSIN)
        family_tree.add_relationship('person1', 'uncle1', RelationshipType.AUNT_UNCLE)

        # Add family events
        wedding_event = TimelineEvent(
            title='Wedding',
            description='Person1 got married',
            participants=['person1', 'spouse'],
            event_type=EventType.FAMILY_EVENT,
            significance_level=9
        )
        family_tree.add_family_event(wedding_event)

        birth_event = TimelineEvent(
            title='Child Birth',
            description='Child1 was born',
            participants=['person1', 'spouse', 'child1'],
            event_type=EventType.BIRTH,
            significance_level=10
        )
        family_tree.add_family_event(birth_event)

        # Test serialization
        props = family_tree.to_neo4j_properties()
        # Count should match the actual number of relationships added
        expected_count = len(family_tree.relationships)
        self.assertEqual(props['relationship_count'], expected_count)
        self.assertEqual(props['family_event_count'], 2)  # All events

        # Test deserialization
        restored_tree = FamilyTree.from_neo4j_properties(props)
        self.assertTrue(restored_tree.validate())
        self.assertEqual(restored_tree.root_character_id, family_tree.root_character_id)

        # Test relationships
        relationships = family_tree.get_neo4j_relationships()
        # Should have root + relationships + events
        expected_min = 1 + len(family_tree.relationships) + len(family_tree.family_events)
        self.assertGreaterEqual(len(relationships), expected_min)

    def test_world_state_with_evolution_schedule_serialization(self):
        """Test serialization of world state with complex evolution schedule."""
        world_state = WorldState(world_id='evolving_world', world_name='Evolving World')

        # Add many entities
        for i in range(5):
            world_state.add_character(f'char_{i}', {'name': f'Character {i}', 'level': i})
            world_state.add_location(f'loc_{i}', {'name': f'Location {i}', 'type': 'area'})
            world_state.add_object(f'obj_{i}', {'name': f'Object {i}', 'durability': 100 - i * 10})

        # Schedule evolution tasks
        base_time = datetime.now() + timedelta(minutes=1)
        for i in range(3):
            world_state.schedule_evolution_task(
                f'evolution_task_{i}',
                base_time + timedelta(hours=i),
                {'task_data': f'data_{i}', 'priority': i}
            )

        # Set various flags
        world_state.set_flag('weather', 'stormy')
        world_state.set_flag('season', 'winter')
        world_state.set_flag('danger_level', 7)
        world_state.set_flag('active_quests', ['quest1', 'quest2', 'quest3'])

        # Test serialization
        props = world_state.to_neo4j_properties()
        self.assertEqual(props['character_count'], 5)
        self.assertEqual(props['location_count'], 5)
        self.assertEqual(props['object_count'], 5)

        # Verify complex data is properly serialized
        world_flags = json.loads(props['world_flags'])
        self.assertEqual(world_flags['weather'], 'stormy')
        self.assertEqual(world_flags['danger_level'], 7)
        self.assertIsInstance(world_flags['active_quests'], list)

        evolution_schedule = json.loads(props['evolution_schedule'])
        self.assertEqual(len(evolution_schedule), 3)
        self.assertIn('task_data', evolution_schedule[0])

        # Test deserialization
        restored_world = WorldState.from_neo4j_properties(props)
        self.assertTrue(restored_world.validate())
        self.assertEqual(len(restored_world.evolution_schedule), 3)
        self.assertEqual(restored_world.get_flag('weather'), 'stormy')
        self.assertEqual(len(restored_world.get_flag('active_quests')), 3)

        # Test relationships
        relationships = world_state.get_neo4j_relationships()
        self.assertEqual(len(relationships), 15)  # 5 each for characters, locations, objects

    def test_timeline_with_complex_events_serialization(self):
        """Test serialization of timeline with complex events and metadata."""
        timeline = Timeline(
            entity_id='complex_character',
            entity_type=EntityType.CHARACTER,
            metadata={'character_class': 'warrior', 'origin': 'northern_kingdom'}
        )

        # Add events with complex data
        events_data = [
            {
                'title': 'Birth',
                'description': 'Born in the northern kingdom',
                'event_type': EventType.BIRTH,
                'significance_level': 10,
                'participants': ['complex_character', 'mother', 'father'],
                'location_id': 'northern_castle',
                'consequences': ['Heir to throne', 'Royal bloodline established'],
                'tags': ['birth', 'royal', 'significant'],
                'metadata': {'birth_weight': '8 lbs', 'time_of_birth': '3:33 AM'}
            },
            {
                'title': 'First Training',
                'description': 'Began warrior training',
                'event_type': EventType.LEARNING,
                'significance_level': 7,
                'participants': ['complex_character', 'trainer_marcus'],
                'location_id': 'training_grounds',
                'consequences': ['Learned basic swordplay', 'Increased strength'],
                'tags': ['training', 'combat', 'growth'],
                'metadata': {'training_duration': '6 months', 'weapons_learned': ['sword', 'shield']}
            },
            {
                'title': 'Great Battle',
                'description': 'Fought in the battle of the five armies',
                'event_type': EventType.CONFLICT,
                'significance_level': 9,
                'participants': ['complex_character', 'army_general', 'enemy_leader'],
                'location_id': 'battlefield_plains',
                'consequences': ['Victory achieved', 'Reputation as warrior established', 'Many enemies defeated'],
                'tags': ['battle', 'victory', 'heroic'],
                'metadata': {'enemies_defeated': 47, 'battle_duration': '3 days', 'wounds_received': 2}
            }
        ]

        for event_data in events_data:
            event = TimelineEvent(**event_data)
            timeline.add_event(event)

        # Test serialization
        props = timeline.to_neo4j_properties()
        self.assertEqual(props['event_count'], 3)

        metadata = json.loads(props['metadata'])
        self.assertEqual(metadata['character_class'], 'warrior')
        self.assertEqual(metadata['origin'], 'northern_kingdom')

        # Test deserialization
        restored_timeline = Timeline.from_neo4j_properties(props)
        self.assertTrue(restored_timeline.validate())
        self.assertEqual(restored_timeline.metadata['character_class'], 'warrior')

        # Test individual event serialization
        for event in timeline.events:
            event_props = event.to_neo4j_properties()
            restored_event = TimelineEvent.from_neo4j_properties(event_props)

            self.assertEqual(restored_event.title, event.title)
            self.assertEqual(restored_event.event_type, event.event_type)
            self.assertEqual(restored_event.participants, event.participants)
            self.assertEqual(restored_event.consequences, event.consequences)
            self.assertEqual(restored_event.tags, event.tags)
            self.assertEqual(restored_event.metadata, event.metadata)

            # Test relationships
            relationships = event.get_neo4j_relationships()
            participant_count = len(event.participants)
            location_count = 1 if event.location_id else 0
            expected_relationships = participant_count + location_count

            self.assertEqual(len(relationships), expected_relationships)


if __name__ == '__main__':
    # Run all tests including the new Neo4j serialization tests
    unittest.main(verbosity=2)
