#!/usr/bin/env python3
"""
Test for Therapeutic Environment Generator

This script tests the therapeutic environment generation and adaptation functionality.
"""

import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_therapeutic_environment_generator():
    """Test the therapeutic environment generator functionality."""
    logger.info("🧪 Testing Therapeutic Environment Generator")

    try:
        # Import the generator
        sys.path.append(str(Path(__file__).parent))
        from core.therapeutic_environment_generator import (
            TherapeuticEnvironmentGenerator,
            TherapeuticTheme,
        )

        # Create generator
        generator = TherapeuticEnvironmentGenerator()
        logger.info("✅ TherapeuticEnvironmentGenerator created successfully")

        # Test environment generation for different themes
        themes_to_test = [
            TherapeuticTheme.MINDFULNESS,
            TherapeuticTheme.ANXIETY_RELIEF
        ]

        generated_environments = []
        for theme in themes_to_test:
            environment = generator.generate_therapeutic_environment(theme)
            if environment:
                generated_environments.append(environment)
                logger.info(f"✅ Generated environment for {theme.value}: {environment['name']}")
                logger.info(f"   Description: {environment['description'][:100]}...")
                logger.info(f"   Atmosphere: {environment['atmosphere']}")
                logger.info(f"   Safety Level: {environment['safety_level']:.2f}")
                logger.info(f"   Therapeutic Opportunities: {len(environment['therapeutic_opportunities'])}")
            else:
                logger.error(f"❌ Failed to generate environment for {theme.value}")
                return False

        # Test environment adaptation (without world manager)
        if generated_environments:
            test_environment = generated_environments[0]
            location_id = test_environment['location_id']

            # Test adaptation for different therapeutic needs
            therapeutic_needs = {
                'emotional_state': 'anxious',
                'crisis_support': False
            }

            # This will log a warning about no world manager, but should still return True
            result = generator.adapt_environment_to_therapeutic_needs(
                location_id, therapeutic_needs
            )
            if result:
                logger.info("✅ Environment adaptation test completed (no world manager)")
            else:
                logger.warning("⚠️ Environment adaptation returned False (expected without world manager)")

        # Test therapeutic enhancement (without world manager)
        if generated_environments:
            test_environment = generated_environments[0]
            location_id = test_environment['location_id']

            # Test different enhancement types
            enhancement_types = ['sensory_integration', 'biofeedback_integration', 'narrative_immersion']

            for enhancement_type in enhancement_types:
                result = generator.create_setting_based_therapeutic_enhancement(
                    location_id, enhancement_type
                )
                if result:
                    logger.info(f"✅ Therapeutic enhancement test completed for {enhancement_type}")
                else:
                    logger.warning(f"⚠️ Enhancement {enhancement_type} returned False (expected without world manager)")

        logger.info("🎉 All therapeutic environment generator tests completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_mock_world_manager():
    """Test with a mock world manager to verify full functionality."""
    logger.info("\n🧪 Testing with Mock World Manager")

    try:
        # Create a simple mock world manager
        class MockWorldManager:
            def __init__(self):
                self.locations = {}

            def get_location_details(self, location_id):
                return self.locations.get(location_id)

            def update_world_state(self, world_changes):
                logger.info(f"Mock: Applying {len(world_changes)} world changes")
                return True

        # Import components
        sys.path.append(str(Path(__file__).parent))
        from core.therapeutic_environment_generator import (
            TherapeuticEnvironmentGenerator,
            TherapeuticTheme,
        )

        # Create generator with mock world manager
        mock_world_manager = MockWorldManager()
        generator = TherapeuticEnvironmentGenerator(mock_world_manager)

        # Generate an environment
        environment = generator.generate_therapeutic_environment(TherapeuticTheme.MINDFULNESS)
        if not environment:
            logger.error("❌ Failed to generate environment")
            return False

        # Add environment to mock world manager
        class MockLocation:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

        mock_location = MockLocation(environment)
        mock_world_manager.locations[environment['location_id']] = mock_location

        # Test adaptation with mock world manager
        therapeutic_needs = {
            'emotional_state': 'anxious',
            'crisis_support': True
        }

        result = generator.adapt_environment_to_therapeutic_needs(
            environment['location_id'], therapeutic_needs
        )

        if result:
            logger.info("✅ Environment adaptation with mock world manager successful")
        else:
            logger.error("❌ Environment adaptation with mock world manager failed")
            return False

        # Test enhancement with mock world manager
        result = generator.create_setting_based_therapeutic_enhancement(
            environment['location_id'], 'sensory_integration'
        )

        if result:
            logger.info("✅ Therapeutic enhancement with mock world manager successful")
        else:
            logger.error("❌ Therapeutic enhancement with mock world manager failed")
            return False

        logger.info("🎉 Mock world manager tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Mock test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    logger.info("🚀 Starting Therapeutic Environment Generator Tests")

    test_results = []

    # Run basic tests
    test_results.append(("Basic Functionality", test_therapeutic_environment_generator()))

    # Run mock world manager tests
    test_results.append(("Mock World Manager", test_with_mock_world_manager()))

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")

    success_rate = passed_tests / total_tests
    logger.info(f"\nTest Score: {passed_tests}/{total_tests} ({success_rate:.2f})")

    if success_rate >= 1.0:
        logger.info("🎉 ALL THERAPEUTIC ENVIRONMENT GENERATOR TESTS PASSED")
        return True
    else:
        logger.warning("❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
