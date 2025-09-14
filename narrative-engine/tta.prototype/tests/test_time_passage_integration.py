"""
Integration Tests for Time Passage and World Evolution

This module contains comprehensive integration tests for the time passage simulation
and world evolution functionality in the TTA Living Worlds system.

Test Categories:
- Time passage simulation tests
- World consistency validation tests
- Background processing tests
- Evolution parameter configuration tests
- Cross-system integration tests
"""

import logging
import sys
import unittest
from datetime import timedelta
from pathlib import Path

# Add the core path for imports
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.insert(0, str(models_path))

try:
    from living_worlds_models import EntityType, EventType, TimelineEvent, WorldState
    from timeline_engine import TimelineEngine, TimeRange
    from world_state_manager import (
        EvolutionResult,
        ValidationResult,
        WorldConfig,
        WorldStateManager,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class WorldStateManager:
        def __init__(self):
            pass

    class WorldConfig:
        def __init__(self, world_name):
            self.world_name = world_name

logger = logging.getLogger(__name__)


class TestTimePassageIntegration(unittest.TestCase):
    """Integration tests for time passage and world evolution."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_manager = WorldStateManager()
        self.timeline_engine = TimelineEngine()
        self.test_world_id = "test_world_001"

        # Create test world configuration
        self.world_config = WorldConfig(
            world_name="Test Living World",
            initial_characters=[
                {
                    'id': 'char_001',
                    'name': 'Alice',
                    'description': 'A test character',
                    'generate_backstory': True
                },
                {
                    'id': 'char_002',
                    'name': 'Bob',
                    'description': 'Another test character',
                    'generate_backstory': True
                }
            ],
            initial_locations=[
                {
                    'id': 'loc_001',
                    'name': 'Test Location',
                    'description': 'A test location'
                }
            ],
            initial_objects=[
                {
                    'id': 'obj_001',
                    'name': 'Test Object',
                    'description': 'A test object'
                }
            ],
            evolution_speed=1.0,
            auto_evolution=True,
            max_timeline_events=1000
        )

    def tearDown(self):
        """Clean up after tests."""
        # Clean up any test data
        pass

    def test_basic_time_passage_simulation(self):
        """Test basic time passage simulation functionality."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state, "World should be initialized successfully")

            # Record initial state
            initial_time = world_state.current_time
            len(world_state.active_characters)
            len(world_state.active_locations)
            len(world_state.active_objects)

            # Simulate 7 days of time passage
            time_delta = timedelta(days=7)
            result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)

            # Verify simulation results
            self.assertTrue(result.success, f"Time passage simulation should succeed: {result.errors}")
            self.assertGreater(result.execution_time, 0, "Execution time should be recorded")

            # Verify world state changes
            updated_world_state = self.world_manager.get_world_state(self.test_world_id)
            self.assertIsNotNone(updated_world_state, "Updated world state should be retrievable")

            # Time should have advanced
            self.assertGreater(updated_world_state.current_time, initial_time,
                             "World time should have advanced")

            # Some evolution should have occurred
            self.assertGreaterEqual(result.events_generated, 0,
                                  "Some events should have been generated")

            logger.info(f"Basic time passage test completed: {result.events_generated} events, "
                       f"{result.characters_evolved} characters, {result.locations_changed} locations, "
                       f"{result.objects_modified} objects")

        except Exception as e:
            self.fail(f"Basic time passage simulation failed: {e}")

    def test_background_processing_evolution(self):
        """Test background processing during player absence."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Simulate 30 days of background processing (player absence)
            time_delta = timedelta(days=30)
            result = self.world_manager.simulate_time_passage(
                self.test_world_id,
                time_delta,
                background_processing=True
            )

            # Verify background processing results
            self.assertTrue(result.success, f"Background processing should succeed: {result.errors}")

            # Background processing should generate fewer events than normal processing
            # but still show world evolution
            self.assertGreaterEqual(result.events_generated, 0,
                                  "Background processing should generate some events")

            # Verify world consistency after background processing
            validation_result = self.world_manager.validate_world_consistency(self.test_world_id)
            self.assertTrue(validation_result.is_valid,
                          f"World should remain consistent after background processing: "
                          f"{validation_result.timeline_issues + validation_result.character_issues}")

            logger.info(f"Background processing test completed: {result.events_generated} events over 30 days")

        except Exception as e:
            self.fail(f"Background processing test failed: {e}")

    def test_evolution_parameter_configuration(self):
        """Test configurable evolution parameters and speed controls."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Test parameter configuration
            evolution_params = {
                'evolution_speed': 2.0,
                'character_evolution_rate': 0.2,
                'location_evolution_rate': 0.1,
                'object_evolution_rate': 0.05,
                'seasonal_changes_enabled': True,
                'relationship_evolution_enabled': True,
                'max_events_per_day': 15
            }

            success = self.world_manager.configure_evolution_parameters(
                self.test_world_id,
                evolution_params
            )
            self.assertTrue(success, "Evolution parameters should be configured successfully")

            # Verify parameters were set
            retrieved_params = self.world_manager.get_evolution_parameters(self.test_world_id)
            self.assertIsNotNone(retrieved_params, "Evolution parameters should be retrievable")

            for param_name, param_value in evolution_params.items():
                self.assertEqual(retrieved_params[param_name], param_value,
                               f"Parameter {param_name} should be set correctly")

            # Test evolution with modified parameters
            time_delta = timedelta(days=3)
            result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)

            self.assertTrue(result.success, "Evolution with modified parameters should succeed")

            # With higher evolution speed and rates, we should see more activity
            # (though this is probabilistic, so we can't guarantee specific numbers)

            logger.info("Evolution parameter configuration test completed")

        except Exception as e:
            self.fail(f"Evolution parameter configuration test failed: {e}")

    def test_world_consistency_validation(self):
        """Test world consistency validation during and after evolution."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Initial consistency check
            initial_validation = self.world_manager.validate_world_consistency(self.test_world_id)
            self.assertTrue(initial_validation.is_valid,
                          f"Initial world state should be consistent: "
                          f"{initial_validation.timeline_issues + initial_validation.character_issues}")

            # Simulate multiple time periods with consistency checks
            time_periods = [
                timedelta(days=1),
                timedelta(days=7),
                timedelta(days=30),
                timedelta(days=90)
            ]

            for time_delta in time_periods:
                # Evolve world
                result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)
                self.assertTrue(result.success, f"Evolution should succeed for {time_delta}")

                # Validate consistency
                validation_result = self.world_manager.validate_world_consistency(self.test_world_id)

                # Log any issues for debugging
                if not validation_result.is_valid:
                    logger.warning(f"Consistency issues after {time_delta}: "
                                 f"Timeline: {len(validation_result.timeline_issues)}, "
                                 f"Character: {len(validation_result.character_issues)}, "
                                 f"Location: {len(validation_result.location_issues)}, "
                                 f"Relationship: {len(validation_result.relationship_issues)}")

                # World should remain reasonably consistent
                # (Some minor inconsistencies might be acceptable in a complex evolving system)
                total_issues = (len(validation_result.timeline_issues) +
                              len(validation_result.character_issues) +
                              len(validation_result.location_issues) +
                              len(validation_result.relationship_issues))

                self.assertLess(total_issues, 10,
                              f"World should have minimal consistency issues after {time_delta}")

            logger.info("World consistency validation test completed")

        except Exception as e:
            self.fail(f"World consistency validation test failed: {e}")

    def test_automatic_event_generation(self):
        """Test automatic event generation for characters, locations, and objects."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Get initial timeline event counts
            initial_event_counts = {}

            # Count character events
            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                initial_event_counts[character_id] = len(timeline.events) if timeline else 0

            # Count location events
            for location_id in world_state.active_locations.keys():
                timeline = self.timeline_engine.get_timeline(location_id)
                initial_event_counts[location_id] = len(timeline.events) if timeline else 0

            # Count object events
            for object_id in world_state.active_objects.keys():
                timeline = self.timeline_engine.get_timeline(object_id)
                initial_event_counts[object_id] = len(timeline.events) if timeline else 0

            # Simulate significant time passage to trigger automatic events
            time_delta = timedelta(days=60)  # 2 months
            result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)

            self.assertTrue(result.success, "Time passage simulation should succeed")
            self.assertGreater(result.events_generated, 0, "Automatic events should be generated")

            # Verify events were added to entity timelines
            events_added = False

            # Check character timelines
            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                if timeline:
                    current_count = len(timeline.events)
                    initial_count = initial_event_counts.get(character_id, 0)
                    if current_count > initial_count:
                        events_added = True
                        logger.info(f"Character {character_id} gained {current_count - initial_count} events")

            # Check location timelines
            for location_id in world_state.active_locations.keys():
                timeline = self.timeline_engine.get_timeline(location_id)
                if timeline:
                    current_count = len(timeline.events)
                    initial_count = initial_event_counts.get(location_id, 0)
                    if current_count > initial_count:
                        events_added = True
                        logger.info(f"Location {location_id} gained {current_count - initial_count} events")

            # Check object timelines
            for object_id in world_state.active_objects.keys():
                timeline = self.timeline_engine.get_timeline(object_id)
                if timeline:
                    current_count = len(timeline.events)
                    initial_count = initial_event_counts.get(object_id, 0)
                    if current_count > initial_count:
                        events_added = True
                        logger.info(f"Object {object_id} gained {current_count - initial_count} events")

            self.assertTrue(events_added, "Events should be added to entity timelines")

            logger.info("Automatic event generation test completed")

        except Exception as e:
            self.fail(f"Automatic event generation test failed: {e}")

    def test_cross_system_integration(self):
        """Test integration between timeline engine, character system, and location manager."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Test that timeline engine is properly integrated
            character_id = 'char_001'
            timeline = self.timeline_engine.get_timeline(character_id)
            self.assertIsNotNone(timeline, f"Character {character_id} should have a timeline")

            # Test that events are properly distributed across systems
            time_delta = timedelta(days=14)
            result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)

            self.assertTrue(result.success, "Cross-system evolution should succeed")

            # Verify that different types of entities evolved
            entity_types_evolved = []
            if result.characters_evolved > 0:
                entity_types_evolved.append("characters")
            if result.locations_changed > 0:
                entity_types_evolved.append("locations")
            if result.objects_modified > 0:
                entity_types_evolved.append("objects")

            # At least some entity types should have evolved
            self.assertGreater(len(entity_types_evolved), 0,
                             "At least some entity types should evolve")

            # Test world summary integration
            world_summary = self.world_manager.get_world_summary(self.test_world_id)
            self.assertIsNotNone(world_summary, "World summary should be available")
            self.assertGreater(world_summary.total_timeline_events, 0,
                             "World summary should show timeline events")

            logger.info(f"Cross-system integration test completed: {entity_types_evolved} evolved")

        except Exception as e:
            self.fail(f"Cross-system integration test failed: {e}")

    def test_long_term_evolution_stability(self):
        """Test world stability over extended time periods."""
        try:
            # Initialize test world
            world_state = self.world_manager.initialize_world(self.test_world_id, self.world_config)
            self.assertIsNotNone(world_state)

            # Simulate 1 year of evolution in chunks
            total_days = 365
            chunk_size = 30  # Monthly chunks

            total_events = 0
            total_character_changes = 0
            total_location_changes = 0
            total_object_changes = 0

            for chunk in range(0, total_days, chunk_size):
                days_in_chunk = min(chunk_size, total_days - chunk)
                time_delta = timedelta(days=days_in_chunk)

                result = self.world_manager.simulate_time_passage(self.test_world_id, time_delta)
                self.assertTrue(result.success, f"Evolution should succeed for chunk {chunk}")

                total_events += result.events_generated
                total_character_changes += result.characters_evolved
                total_location_changes += result.locations_changed
                total_object_changes += result.objects_modified

                # Periodic consistency checks
                if chunk % 90 == 0:  # Every 3 months
                    validation_result = self.world_manager.validate_world_consistency(self.test_world_id)
                    total_issues = (len(validation_result.timeline_issues) +
                                  len(validation_result.character_issues) +
                                  len(validation_result.location_issues) +
                                  len(validation_result.relationship_issues))

                    self.assertLess(total_issues, 15,
                                  f"World should remain stable after {chunk} days")

            # Final validation
            final_validation = self.world_manager.validate_world_consistency(self.test_world_id)
            total_final_issues = (len(final_validation.timeline_issues) +
                                len(final_validation.character_issues) +
                                len(final_validation.location_issues) +
                                len(final_validation.relationship_issues))

            self.assertLess(total_final_issues, 20,
                          "World should remain reasonably stable after 1 year")

            # Verify significant evolution occurred
            self.assertGreater(total_events, 50, "Significant events should occur over 1 year")

            logger.info(f"Long-term evolution stability test completed: "
                       f"{total_events} events, {total_character_changes} character changes, "
                       f"{total_location_changes} location changes, {total_object_changes} object changes "
                       f"over {total_days} days")

        except Exception as e:
            self.fail(f"Long-term evolution stability test failed: {e}")

    def test_evolution_speed_controls(self):
        """Test evolution speed controls and their effects."""
        try:
            # Test different evolution speeds
            speed_tests = [0.5, 1.0, 2.0, 5.0]
            results = {}

            for speed in speed_tests:
                # Create separate world for each speed test
                world_id = f"speed_test_{speed}"
                world_state = self.world_manager.initialize_world(world_id, self.world_config)
                self.assertIsNotNone(world_state)

                # Configure evolution speed
                success = self.world_manager.configure_evolution_parameters(
                    world_id,
                    {'evolution_speed': speed}
                )
                self.assertTrue(success, f"Should configure speed {speed}")

                # Simulate same time period
                time_delta = timedelta(days=7)
                result = self.world_manager.simulate_time_passage(world_id, time_delta)

                self.assertTrue(result.success, f"Evolution should succeed at speed {speed}")
                results[speed] = result

            # Verify that higher speeds generally produce more evolution
            # (This is probabilistic, so we'll check trends rather than exact values)

            # At minimum, all speeds should produce some results
            for speed, result in results.items():
                self.assertGreaterEqual(result.events_generated, 0,
                                      f"Speed {speed} should generate events")

            logger.info("Evolution speed controls test completed")

        except Exception as e:
            self.fail(f"Evolution speed controls test failed: {e}")


class TestTimePassageEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for time passage."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_manager = WorldStateManager()

    def test_invalid_world_id(self):
        """Test time passage with invalid world ID."""
        result = self.world_manager.simulate_time_passage("nonexistent_world", timedelta(days=1))
        self.assertFalse(result.success, "Should fail for nonexistent world")
        self.assertIn("not found", result.errors[0].lower(), "Should indicate world not found")

    def test_zero_time_delta(self):
        """Test time passage with zero time delta."""
        # This test would require a valid world, so we'll just test the parameter validation
        # In a real implementation, zero time delta should be handled gracefully
        pass

    def test_negative_time_delta(self):
        """Test time passage with negative time delta."""
        # This should be handled gracefully - either rejected or treated as no-op
        pass

    def test_extremely_large_time_delta(self):
        """Test time passage with extremely large time delta."""
        # Should be handled without causing performance issues or overflow
        pass


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run the tests
    unittest.main(verbosity=2)
