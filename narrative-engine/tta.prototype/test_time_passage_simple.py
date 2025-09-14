#!/usr/bin/env python3
"""
Simple test runner for time passage and world evolution functionality.

This script provides a basic test of the time passage implementation
to verify that the core functionality works correctly.
"""

import logging
import sys
from datetime import timedelta
from pathlib import Path

# Add the core path for imports
core_path = Path(__file__).parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

models_path = Path(__file__).parent / "models"
if str(models_path) not in sys.path:
    sys.path.insert(0, str(models_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_basic_time_passage():
    """Test basic time passage functionality."""
    try:
        from world_state_manager import WorldConfig, WorldStateManager

        logger.info("Starting basic time passage test...")

        # Create world manager
        world_manager = WorldStateManager()

        # Create test world configuration
        world_config = WorldConfig(
            world_name="Test Time Passage World",
            initial_characters=[
                {
                    'id': 'char_001',
                    'name': 'Alice',
                    'description': 'Test character for time passage',
                    'generate_backstory': True
                }
            ],
            initial_locations=[
                {
                    'id': 'loc_001',
                    'name': 'Test Location',
                    'description': 'Test location for time passage'
                }
            ],
            initial_objects=[
                {
                    'id': 'obj_001',
                    'name': 'Test Object',
                    'description': 'Test object for time passage'
                }
            ],
            evolution_speed=1.0,
            auto_evolution=True
        )

        # Initialize world
        world_id = "test_time_passage_world"
        logger.info(f"Initializing world: {world_id}")

        world_state = world_manager.initialize_world(world_id, world_config)
        if not world_state:
            logger.error("Failed to initialize world")
            return False

        logger.info(f"World initialized successfully: {world_state.world_name}")
        logger.info(f"Initial time: {world_state.current_time}")
        logger.info(f"Characters: {len(world_state.active_characters)}")
        logger.info(f"Locations: {len(world_state.active_locations)}")
        logger.info(f"Objects: {len(world_state.active_objects)}")

        # Test evolution parameter configuration
        logger.info("Configuring evolution parameters...")
        evolution_params = {
            'evolution_speed': 2.0,
            'character_evolution_rate': 0.3,
            'location_evolution_rate': 0.2,
            'object_evolution_rate': 0.1,
            'max_events_per_day': 5
        }

        success = world_manager.configure_evolution_parameters(world_id, evolution_params)
        if not success:
            logger.error("Failed to configure evolution parameters")
            return False

        logger.info("Evolution parameters configured successfully")

        # Test time passage simulation
        logger.info("Testing time passage simulation...")

        time_delta = timedelta(days=7)  # Simulate 1 week
        result = world_manager.simulate_time_passage(world_id, time_delta)

        if not result.success:
            logger.error(f"Time passage simulation failed: {result.errors}")
            return False

        logger.info("Time passage simulation completed successfully!")
        logger.info(f"Execution time: {result.execution_time:.2f} seconds")
        logger.info(f"Events generated: {result.events_generated}")
        logger.info(f"Characters evolved: {result.characters_evolved}")
        logger.info(f"Locations changed: {result.locations_changed}")
        logger.info(f"Objects modified: {result.objects_modified}")

        # Get updated world state
        updated_world_state = world_manager.get_world_state(world_id)
        if not updated_world_state:
            logger.error("Failed to retrieve updated world state")
            return False

        logger.info(f"Updated world time: {updated_world_state.current_time}")
        logger.info(f"Last evolution: {updated_world_state.last_evolution}")

        # Test world consistency validation
        logger.info("Validating world consistency...")
        validation_result = world_manager.validate_world_consistency(world_id)

        if validation_result.is_valid:
            logger.info("World consistency validation passed!")
        else:
            logger.warning("World consistency issues found:")
            if validation_result.timeline_issues:
                logger.warning(f"Timeline issues: {len(validation_result.timeline_issues)}")
            if validation_result.character_issues:
                logger.warning(f"Character issues: {len(validation_result.character_issues)}")
            if validation_result.location_issues:
                logger.warning(f"Location issues: {len(validation_result.location_issues)}")
            if validation_result.relationship_issues:
                logger.warning(f"Relationship issues: {len(validation_result.relationship_issues)}")

        # Test background processing
        logger.info("Testing background processing...")

        background_time_delta = timedelta(days=30)  # Simulate 1 month of absence
        background_result = world_manager.simulate_time_passage(
            world_id,
            background_time_delta,
            background_processing=True
        )

        if not background_result.success:
            logger.error(f"Background processing failed: {background_result.errors}")
            return False

        logger.info("Background processing completed successfully!")
        logger.info(f"Background events generated: {background_result.events_generated}")
        logger.info(f"Background characters evolved: {background_result.characters_evolved}")
        logger.info(f"Background locations changed: {background_result.locations_changed}")
        logger.info(f"Background objects modified: {background_result.objects_modified}")

        # Get world summary
        logger.info("Getting world summary...")
        world_summary = world_manager.get_world_summary(world_id)

        if world_summary:
            logger.info("World summary:")
            logger.info(f"  Total timeline events: {world_summary.total_timeline_events}")
            logger.info(f"  Character count: {world_summary.character_count}")
            logger.info(f"  Location count: {world_summary.location_count}")
            logger.info(f"  Object count: {world_summary.object_count}")
            logger.info(f"  World status: {world_summary.world_status}")
        else:
            logger.warning("Failed to get world summary")

        logger.info("Basic time passage test completed successfully!")
        return True

    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("This is expected if running without full dependencies")
        return False
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evolution_parameters():
    """Test evolution parameter configuration."""
    try:
        from world_state_manager import WorldConfig, WorldStateManager

        logger.info("Testing evolution parameter configuration...")

        world_manager = WorldStateManager()
        world_config = WorldConfig(world_name="Parameter Test World")
        world_id = "param_test_world"

        # Initialize world
        world_state = world_manager.initialize_world(world_id, world_config)
        if not world_state:
            logger.error("Failed to initialize world for parameter test")
            return False

        # Test various parameter configurations
        test_params = [
            {'evolution_speed': 0.5},
            {'evolution_speed': 2.0, 'auto_evolution': True},
            {'character_evolution_rate': 0.5, 'location_evolution_rate': 0.3},
            {'seasonal_changes_enabled': False, 'relationship_evolution_enabled': True},
            {'max_events_per_day': 20}
        ]

        for i, params in enumerate(test_params):
            logger.info(f"Testing parameter set {i+1}: {params}")

            success = world_manager.configure_evolution_parameters(world_id, params)
            if not success:
                logger.error(f"Failed to configure parameters: {params}")
                return False

            # Verify parameters were set
            retrieved_params = world_manager.get_evolution_parameters(world_id)
            if not retrieved_params:
                logger.error("Failed to retrieve evolution parameters")
                return False

            for param_name, param_value in params.items():
                if retrieved_params.get(param_name) != param_value:
                    logger.error(f"Parameter {param_name} not set correctly: "
                               f"expected {param_value}, got {retrieved_params.get(param_name)}")
                    return False

            logger.info(f"Parameter set {i+1} configured successfully")

        logger.info("Evolution parameter configuration test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Evolution parameter test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting time passage and world evolution tests...")

    tests = [
        ("Basic Time Passage", test_basic_time_passage),
        ("Evolution Parameters", test_evolution_parameters)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")

        try:
            if test_func():
                logger.info(f"✓ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"✗ {test_name} FAILED")
                failed += 1
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            failed += 1

    logger.info(f"\n{'='*50}")
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info(f"{'='*50}")

    if failed == 0:
        logger.info("All tests passed! Time passage implementation is working correctly.")
        return True
    else:
        logger.error(f"{failed} tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
