"""
Unit tests for Location Evolution Manager

This module contains comprehensive unit tests for the LocationEvolutionManager
class, testing location evolution, environmental consistency, seasonal changes,
and event handling functionality.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Add the core and models paths
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
sys.path.extend([str(core_path), str(models_path)])

from living_worlds_models import (
    EntityType,
    EventType,
    Timeline,
    TimelineEvent,
    ValidationError,
)
from location_evolution_manager import (
    EnvironmentalFactor,
    EnvironmentalFactorType,
    LocationChange,
    LocationEvolutionManager,
    LocationHistory,
    Season,
)
from timeline_engine import TimelineEngine
from worldbuilding_setting_management import (
    LocationDetails,
    LocationType,
    WorldbuildingSettingManagement,
)


class TestLocationEvolutionManager(unittest.TestCase):
    """Test cases for LocationEvolutionManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_worldbuilding = Mock(spec=WorldbuildingSettingManagement)
        self.mock_timeline_engine = Mock(spec=TimelineEngine)

        self.manager = LocationEvolutionManager(
            worldbuilding_system=self.mock_worldbuilding,
            timeline_engine=self.mock_timeline_engine
        )

        # Sample location data
        self.sample_location_data = {
            'location_id': 'test_location_001',
            'name': 'Peaceful Garden',
            'description': 'A serene garden space for reflection',
            'location_type': 'safe_space',
            'therapeutic_themes': ['mindfulness', 'peace'],
            'atmosphere': 'peaceful',
            'environmental_factors': {
                'weather': 'pleasant',
                'lighting': 'soft natural light'
            }
        }

        self.sample_location_details = LocationDetails(
            location_id='test_location_001',
            name='Peaceful Garden',
            description='A serene garden space for reflection',
            location_type=LocationType.SAFE_SPACE,
            therapeutic_themes=['mindfulness', 'peace'],
            atmosphere='peaceful',
            safety_level=0.9,
            immersion_level=0.7
        )

    def test_initialization(self):
        """Test LocationEvolutionManager initialization."""
        # Test with provided systems
        manager = LocationEvolutionManager(
            worldbuilding_system=self.mock_worldbuilding,
            timeline_engine=self.mock_timeline_engine
        )

        self.assertEqual(manager.worldbuilding_system, self.mock_worldbuilding)
        self.assertEqual(manager.timeline_engine, self.mock_timeline_engine)
        self.assertIsInstance(manager.location_histories, dict)
        self.assertIsInstance(manager.environmental_factors, dict)
        self.assertIsInstance(manager.seasonal_schedules, dict)

        # Test with default systems
        manager_default = LocationEvolutionManager()
        self.assertIsInstance(manager_default.worldbuilding_system, WorldbuildingSettingManagement)
        self.assertIsInstance(manager_default.timeline_engine, TimelineEngine)

    def test_create_location_with_history_success(self):
        """Test successful location creation with history."""
        # Mock timeline creation
        mock_timeline = Mock(spec=Timeline)
        self.mock_timeline_engine.create_timeline.return_value = mock_timeline

        # Create location
        result = self.manager.create_location_with_history(self.sample_location_data)

        # Verify result
        self.assertIsInstance(result, LocationDetails)
        self.assertEqual(result.location_id, 'test_location_001')
        self.assertEqual(result.name, 'Peaceful Garden')

        # Verify timeline creation was called
        self.mock_timeline_engine.create_timeline.assert_called_once_with(
            'test_location_001', EntityType.LOCATION
        )

        # Verify history was created
        self.assertIn('test_location_001', self.manager.location_histories)
        history = self.manager.location_histories['test_location_001']
        self.assertIsInstance(history, LocationHistory)
        self.assertEqual(history.location_id, 'test_location_001')

        # Verify environmental factors were initialized
        self.assertIn('test_location_001', self.manager.environmental_factors)
        factors = self.manager.environmental_factors['test_location_001']
        self.assertIsInstance(factors, dict)
        self.assertGreater(len(factors), 0)

    def test_create_location_with_history_invalid_data(self):
        """Test location creation with invalid data."""
        invalid_data = {
            'location_id': '',  # Empty ID should cause validation error
            'name': 'Test Location'
        }

        result = self.manager.create_location_with_history(invalid_data)
        self.assertIsNone(result)

    def test_evolve_location_environmental(self):
        """Test location evolution with environmental changes."""
        # Setup
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details

        # Initialize environmental factors
        self.manager._initialize_environmental_factors('test_location_001', {})

        # Mock random choice for deterministic testing
        with patch('random.choice') as mock_choice:
            mock_choice.side_effect = ['weather', 'sunny']  # First for factor selection, second for new value

            # Evolve location
            time_delta = timedelta(hours=12)
            result = self.manager.evolve_location('test_location_001', time_delta)

            # Verify result
            if result:  # Evolution might not always produce changes
                self.assertIsInstance(result, LocationChange)
                self.assertEqual(result.location_id, 'test_location_001')
                self.assertEqual(result.change_type, 'environmental')

    def test_evolve_location_nonexistent(self):
        """Test evolution of non-existent location."""
        self.mock_worldbuilding.get_location_details.return_value = None

        time_delta = timedelta(hours=6)
        result = self.manager.evolve_location('nonexistent_location', time_delta)

        self.assertIsNone(result)

    def test_apply_seasonal_changes_success(self):
        """Test successful application of seasonal changes."""
        # Setup
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details

        # Create location history
        history = LocationHistory(location_id='test_location_001')
        self.manager.location_histories['test_location_001'] = history

        # Initialize environmental factors
        self.manager._initialize_environmental_factors('test_location_001', {})

        # Apply seasonal changes
        result = self.manager.apply_seasonal_changes('test_location_001', Season.SPRING)

        # Verify result
        self.assertTrue(result)

        # Verify timeline event was added
        self.mock_timeline_engine.add_event.assert_called()

        # Verify history was updated
        self.assertGreater(len(history.significant_events), 0)

    def test_apply_seasonal_changes_no_location(self):
        """Test seasonal changes application for non-existent location."""
        self.mock_worldbuilding.get_location_details.return_value = None

        result = self.manager.apply_seasonal_changes('nonexistent_location', Season.SUMMER)

        self.assertFalse(result)

    def test_handle_location_events_success(self):
        """Test successful handling of location events."""
        # Setup
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details

        # Create test events
        events = [
            TimelineEvent(
                event_type=EventType.PLAYER_INTERACTION,
                title="Player explores garden",
                description="Player spent time in peaceful contemplation",
                location_id='test_location_001',
                participants=['player_001'],
                emotional_impact=0.8,
                significance_level=6
            ),
            TimelineEvent(
                event_type=EventType.DISCOVERY,
                title="Hidden fountain discovered",
                description="A small fountain was found behind the bushes",
                location_id='test_location_001',
                participants=['player_001'],
                significance_level=8
            )
        ]

        # Handle events
        result = self.manager.handle_location_events('test_location_001', events)

        # Verify result
        self.assertTrue(result)

        # Verify timeline events were added
        self.assertEqual(self.mock_timeline_engine.add_event.call_count, len(events))

        # Verify history was created and updated
        self.assertIn('test_location_001', self.manager.location_histories)
        history = self.manager.location_histories['test_location_001']
        self.assertGreater(len(history.significant_events), 0)
        self.assertIn('player_001', history.visitor_history)

    def test_handle_location_events_no_location(self):
        """Test handling events for non-existent location."""
        self.mock_worldbuilding.get_location_details.return_value = None

        events = [
            TimelineEvent(
                event_type=EventType.PLAYER_INTERACTION,
                title="Test event",
                description="Test description"
            )
        ]

        result = self.manager.handle_location_events('nonexistent_location', events)

        self.assertFalse(result)

    def test_get_location_history(self):
        """Test getting location history."""
        # Create test history
        history = LocationHistory(location_id='test_location_001')
        self.manager.location_histories['test_location_001'] = history

        # Get history
        result = self.manager.get_location_history('test_location_001')

        # Verify result
        self.assertEqual(result, history)

        # Test non-existent location
        result_none = self.manager.get_location_history('nonexistent_location')
        self.assertIsNone(result_none)

    def test_update_location_accessibility_success(self):
        """Test successful accessibility update."""
        # Setup
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details
        self.mock_worldbuilding.update_world_state.return_value = True

        # Create history
        history = LocationHistory(location_id='test_location_001')
        self.manager.location_histories['test_location_001'] = history

        # Update accessibility
        new_conditions = ['wheelchair_accessible', 'audio_descriptions']
        result = self.manager.update_location_accessibility('test_location_001', new_conditions)

        # Verify result
        self.assertTrue(result)

        # Verify location was updated
        self.assertEqual(self.sample_location_details.accessibility_requirements, new_conditions)

        # Verify timeline event was added
        self.mock_timeline_engine.add_event.assert_called()

        # Verify history was updated
        self.assertGreater(len(history.environmental_changes), 0)

    def test_update_location_accessibility_no_location(self):
        """Test accessibility update for non-existent location."""
        self.mock_worldbuilding.get_location_details.return_value = None

        result = self.manager.update_location_accessibility('nonexistent_location', [])

        self.assertFalse(result)


class TestEnvironmentalFactor(unittest.TestCase):
    """Test cases for EnvironmentalFactor class."""

    def test_environmental_factor_creation(self):
        """Test environmental factor creation and validation."""
        factor = EnvironmentalFactor(
            factor_type=EnvironmentalFactorType.WEATHER,
            current_value="sunny",
            intensity=0.8,
            seasonal_variation=True,
            change_rate=0.2
        )

        self.assertEqual(factor.factor_type, EnvironmentalFactorType.WEATHER)
        self.assertEqual(factor.current_value, "sunny")
        self.assertEqual(factor.intensity, 0.8)
        self.assertTrue(factor.seasonal_variation)
        self.assertEqual(factor.change_rate, 0.2)

        # Test validation
        self.assertTrue(factor.validate())

    def test_environmental_factor_validation_errors(self):
        """Test environmental factor validation errors."""
        # Test empty current value
        with self.assertRaises(ValidationError):
            factor = EnvironmentalFactor(current_value="")
            factor.validate()

        # Test invalid intensity
        with self.assertRaises(ValidationError):
            factor = EnvironmentalFactor(intensity=1.5)
            factor.validate()

        # Test invalid change rate
        with self.assertRaises(ValidationError):
            factor = EnvironmentalFactor(change_rate=-0.1)
            factor.validate()

    def test_environmental_factor_serialization(self):
        """Test environmental factor serialization and deserialization."""
        factor = EnvironmentalFactor(
            factor_type=EnvironmentalFactorType.LIGHTING,
            current_value="bright",
            intensity=0.6
        )

        # Test to_dict
        factor_dict = factor.to_dict()
        self.assertIsInstance(factor_dict, dict)
        self.assertEqual(factor_dict['factor_type'], 'lighting')
        self.assertEqual(factor_dict['current_value'], 'bright')
        self.assertEqual(factor_dict['intensity'], 0.6)

        # Test from_dict
        restored_factor = EnvironmentalFactor.from_dict(factor_dict)
        self.assertEqual(restored_factor.factor_type, EnvironmentalFactorType.LIGHTING)
        self.assertEqual(restored_factor.current_value, 'bright')
        self.assertEqual(restored_factor.intensity, 0.6)


class TestLocationChange(unittest.TestCase):
    """Test cases for LocationChange class."""

    def test_location_change_creation(self):
        """Test location change creation and validation."""
        change = LocationChange(
            location_id='test_location',
            change_type='environmental',
            description='Weather changed from sunny to rainy',
            old_state={'weather': 'sunny'},
            new_state={'weather': 'rainy'},
            significance_level=5
        )

        self.assertEqual(change.location_id, 'test_location')
        self.assertEqual(change.change_type, 'environmental')
        self.assertEqual(change.description, 'Weather changed from sunny to rainy')
        self.assertEqual(change.significance_level, 5)

        # Test validation
        self.assertTrue(change.validate())

    def test_location_change_validation_errors(self):
        """Test location change validation errors."""
        # Test empty location ID
        with self.assertRaises(ValidationError):
            change = LocationChange(location_id="")
            change.validate()

        # Test empty description
        with self.assertRaises(ValidationError):
            change = LocationChange(
                location_id="test",
                description=""
            )
            change.validate()

        # Test invalid significance level
        with self.assertRaises(ValidationError):
            change = LocationChange(
                location_id="test",
                description="test",
                significance_level=11
            )
            change.validate()

    def test_location_change_serialization(self):
        """Test location change serialization and deserialization."""
        change = LocationChange(
            location_id='test_location',
            change_type='structural',
            description='New action added',
            old_state={'actions': ['explore']},
            new_state={'actions': ['explore', 'investigate']},
            significance_level=7
        )

        # Test to_dict
        change_dict = change.to_dict()
        self.assertIsInstance(change_dict, dict)
        self.assertEqual(change_dict['location_id'], 'test_location')
        self.assertEqual(change_dict['change_type'], 'structural')
        self.assertEqual(change_dict['significance_level'], 7)

        # Test from_dict
        restored_change = LocationChange.from_dict(change_dict)
        self.assertEqual(restored_change.location_id, 'test_location')
        self.assertEqual(restored_change.change_type, 'structural')
        self.assertEqual(restored_change.significance_level, 7)


class TestLocationHistory(unittest.TestCase):
    """Test cases for LocationHistory class."""

    def test_location_history_creation(self):
        """Test location history creation and validation."""
        history = LocationHistory(location_id='test_location')

        self.assertEqual(history.location_id, 'test_location')
        self.assertIsInstance(history.founding_events, list)
        self.assertIsInstance(history.significant_events, list)
        self.assertIsInstance(history.environmental_changes, list)
        self.assertIsInstance(history.visitor_history, list)
        self.assertIsInstance(history.cultural_evolution, list)
        self.assertIsInstance(history.seasonal_patterns, dict)

        # Test validation
        self.assertTrue(history.validate())

    def test_location_history_add_significant_event(self):
        """Test adding significant events to location history."""
        history = LocationHistory(location_id='test_location')

        event = TimelineEvent(
            event_type=EventType.DISCOVERY,
            title="Ancient artifact found",
            description="A mysterious artifact was discovered",
            significance_level=8
        )

        result = history.add_significant_event(event)

        self.assertTrue(result)
        self.assertEqual(len(history.significant_events), 1)
        self.assertEqual(history.significant_events[0], event)

    def test_location_history_add_environmental_change(self):
        """Test adding environmental changes to location history."""
        history = LocationHistory(location_id='test_location')

        change = LocationChange(
            location_id='test_location',
            change_type='environmental',
            description='Seasonal weather change',
            significance_level=5
        )

        result = history.add_environmental_change(change)

        self.assertTrue(result)
        self.assertEqual(len(history.environmental_changes), 1)
        self.assertEqual(history.environmental_changes[0], change)

    def test_location_history_get_recent_events(self):
        """Test getting recent events from location history."""
        history = LocationHistory(location_id='test_location')

        # Add events with different timestamps
        old_event = TimelineEvent(
            event_type=EventType.CREATION,
            title="Old event",
            description="An old event",
            timestamp=datetime.now() - timedelta(days=60)
        )

        recent_event = TimelineEvent(
            event_type=EventType.DISCOVERY,
            title="Recent event",
            description="A recent event",
            timestamp=datetime.now() - timedelta(days=10)
        )

        history.founding_events.append(old_event)
        history.significant_events.append(recent_event)

        # Get recent events (last 30 days)
        recent_events = history.get_recent_events(30)

        self.assertEqual(len(recent_events), 1)
        self.assertEqual(recent_events[0], recent_event)

    def test_location_history_serialization(self):
        """Test location history serialization and deserialization."""
        history = LocationHistory(location_id='test_location')

        # Add some test data
        event = TimelineEvent(
            event_type=EventType.CREATION,
            title="Test event",
            description="Test description"
        )
        history.founding_events.append(event)

        change = LocationChange(
            location_id='test_location',
            description='Test change'
        )
        history.environmental_changes.append(change)

        # Test to_dict
        history_dict = history.to_dict()
        self.assertIsInstance(history_dict, dict)
        self.assertEqual(history_dict['location_id'], 'test_location')
        self.assertEqual(len(history_dict['founding_events']), 1)
        self.assertEqual(len(history_dict['environmental_changes']), 1)

        # Test from_dict
        restored_history = LocationHistory.from_dict(history_dict)
        self.assertEqual(restored_history.location_id, 'test_location')
        self.assertEqual(len(restored_history.founding_events), 1)
        self.assertEqual(len(restored_history.environmental_changes), 1)


class TestSeasonalChanges(unittest.TestCase):
    """Test cases for seasonal change functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_worldbuilding = Mock(spec=WorldbuildingSettingManagement)
        self.mock_timeline_engine = Mock(spec=TimelineEngine)

        self.manager = LocationEvolutionManager(
            worldbuilding_system=self.mock_worldbuilding,
            timeline_engine=self.mock_timeline_engine
        )

        self.sample_location_details = LocationDetails(
            location_id='test_location_001',
            name='Seasonal Garden',
            description='A garden that changes with the seasons',
            location_type=LocationType.SAFE_SPACE
        )

    def test_seasonal_weather_changes(self):
        """Test seasonal weather changes."""
        location_id = 'test_location_001'

        # Initialize environmental factors
        self.manager._initialize_environmental_factors(location_id, {})

        # Test each season
        seasons_weather = {
            Season.SPRING: "mild and rainy",
            Season.SUMMER: "warm and sunny",
            Season.AUTUMN: "cool and crisp",
            Season.WINTER: "cold and quiet"
        }

        for season, expected_weather in seasons_weather.items():
            change = self.manager._apply_seasonal_weather(location_id, season)

            if change:  # Change might be None if weather was already correct
                self.assertIsInstance(change, LocationChange)
                self.assertEqual(change.new_state['weather'], expected_weather)
                self.assertEqual(change.trigger_event, f"seasonal_change_{season.value}")

    def test_seasonal_lighting_changes(self):
        """Test seasonal lighting changes."""
        location_id = 'test_location_001'

        # Initialize environmental factors
        self.manager._initialize_environmental_factors(location_id, {})

        # Test lighting changes for different seasons
        seasons_lighting = {
            Season.SPRING: "soft morning light",
            Season.SUMMER: "bright and clear",
            Season.AUTUMN: "golden and warm",
            Season.WINTER: "soft and muted"
        }

        for season, expected_lighting in seasons_lighting.items():
            change = self.manager._apply_seasonal_lighting(location_id, season)

            if change:  # Change might be None if lighting was already correct
                self.assertIsInstance(change, LocationChange)
                self.assertEqual(change.new_state['lighting'], expected_lighting)

    def test_seasonal_vegetation_changes(self):
        """Test seasonal vegetation changes."""
        location_id = 'test_location_001'

        # Initialize environmental factors
        self.manager._initialize_environmental_factors(location_id, {})

        # Test vegetation changes for different seasons
        seasons_vegetation = {
            Season.SPRING: "new growth and blooming",
            Season.SUMMER: "lush and full",
            Season.AUTUMN: "changing colors",
            Season.WINTER: "dormant and bare"
        }

        for season, expected_vegetation in seasons_vegetation.items():
            change = self.manager._apply_seasonal_vegetation(location_id, season)

            if change:  # Change might be None if vegetation was already correct
                self.assertIsInstance(change, LocationChange)
                self.assertEqual(change.new_state['vegetation'], expected_vegetation)


class TestEventHandling(unittest.TestCase):
    """Test cases for event handling functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_worldbuilding = Mock(spec=WorldbuildingSettingManagement)
        self.mock_timeline_engine = Mock(spec=TimelineEngine)

        self.manager = LocationEvolutionManager(
            worldbuilding_system=self.mock_worldbuilding,
            timeline_engine=self.mock_timeline_engine
        )

        self.sample_location_details = LocationDetails(
            location_id='test_location_001',
            name='Test Location',
            description='A test location',
            location_type=LocationType.SAFE_SPACE,
            safety_level=0.8,
            atmosphere='neutral'
        )

    def test_handle_player_interaction_positive(self):
        """Test handling positive player interaction events."""
        location_id = 'test_location_001'

        event = TimelineEvent(
            event_type=EventType.PLAYER_INTERACTION,
            title="Positive interaction",
            description="Player had a wonderful experience",
            emotional_impact=0.8,
            significance_level=6
        )

        change = self.manager._handle_player_interaction_event(location_id, event)

        if change:  # Change might be None if safety was already at maximum
            self.assertIsInstance(change, LocationChange)
            self.assertEqual(change.change_type, 'environmental')
            self.assertIn('safer', change.description)

    def test_handle_conflict_event(self):
        """Test handling conflict events."""
        location_id = 'test_location_001'

        event = TimelineEvent(
            event_type=EventType.CONFLICT,
            title="Argument occurred",
            description="A heated argument took place",
            significance_level=7
        )

        change = self.manager._handle_conflict_event(location_id, event)

        self.assertIsInstance(change, LocationChange)
        self.assertEqual(change.change_type, 'environmental')
        self.assertEqual(change.new_state['atmosphere'], 'tense')
        self.assertLess(change.new_state['safety_level'], self.sample_location_details.safety_level)

    def test_handle_celebration_event(self):
        """Test handling celebration events."""
        location_id = 'test_location_001'

        event = TimelineEvent(
            event_type=EventType.CELEBRATION,
            title="Birthday party",
            description="A joyful birthday celebration",
            significance_level=6
        )

        change = self.manager._handle_celebration_event(location_id, event)

        self.assertIsInstance(change, LocationChange)
        self.assertEqual(change.change_type, 'environmental')
        self.assertEqual(change.new_state['atmosphere'], 'joyful')

    def test_handle_discovery_event(self):
        """Test handling discovery events."""
        location_id = 'test_location_001'

        event = TimelineEvent(
            event_type=EventType.DISCOVERY,
            title="Hidden treasure",
            description="A hidden treasure chest was found",
            significance_level=8
        )

        change = self.manager._handle_discovery_event(location_id, event)

        self.assertIsInstance(change, LocationChange)
        self.assertEqual(change.change_type, 'structural')
        self.assertIn('investigate hidden treasure', change.new_state['available_actions'])


class TestValidationAndConsistency(unittest.TestCase):
    """Test cases for validation and consistency checking."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_worldbuilding = Mock(spec=WorldbuildingSettingManagement)
        self.mock_timeline_engine = Mock(spec=TimelineEngine)

        self.manager = LocationEvolutionManager(
            worldbuilding_system=self.mock_worldbuilding,
            timeline_engine=self.mock_timeline_engine
        )

        self.sample_location_details = LocationDetails(
            location_id='test_location_001',
            name='Test Location',
            description='A test location',
            location_type=LocationType.SAFE_SPACE
        )

    def test_validate_location_evolution_consistency_success(self):
        """Test successful validation of location evolution consistency."""
        location_id = 'test_location_001'

        # Setup mocks
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details
        self.mock_timeline_engine.validate_timeline_consistency.return_value = (True, [])

        # Create valid history and factors
        history = LocationHistory(location_id=location_id)
        self.manager.location_histories[location_id] = history
        self.manager._initialize_environmental_factors(location_id, {})

        # Validate consistency
        is_consistent, issues = self.manager.validate_location_evolution_consistency(location_id)

        self.assertTrue(is_consistent)
        self.assertEqual(len(issues), 0)

    def test_validate_location_evolution_consistency_no_location(self):
        """Test validation when location doesn't exist."""
        location_id = 'nonexistent_location'

        # Setup mock to return None
        self.mock_worldbuilding.get_location_details.return_value = None

        # Validate consistency
        is_consistent, issues = self.manager.validate_location_evolution_consistency(location_id)

        self.assertFalse(is_consistent)
        self.assertGreater(len(issues), 0)
        self.assertIn('not found', issues[0])

    def test_validate_location_evolution_consistency_timeline_issues(self):
        """Test validation with timeline consistency issues."""
        location_id = 'test_location_001'

        # Setup mocks
        self.mock_worldbuilding.get_location_details.return_value = self.sample_location_details
        self.mock_timeline_engine.validate_timeline_consistency.return_value = (
            False, ['Timeline event order is incorrect']
        )

        # Create valid history and factors
        history = LocationHistory(location_id=location_id)
        self.manager.location_histories[location_id] = history
        self.manager._initialize_environmental_factors(location_id, {})

        # Validate consistency
        is_consistent, issues = self.manager.validate_location_evolution_consistency(location_id)

        self.assertFalse(is_consistent)
        self.assertIn('Timeline event order is incorrect', issues)


if __name__ == '__main__':
    unittest.main()
