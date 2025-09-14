#!/usr/bin/env python3
"""
Complete validation for Task 7: Develop Worldbuilding and Setting Management

This script validates that all components of task 7 (7.1, 7.2, 7.3) are properly implemented.
"""

import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_task_7_1():
    """Validate Task 7.1: World state management and consistency validation."""
    logger.info("🔍 Validating Task 7.1: World state management and consistency validation")

    try:
        # Test worldbuilding setting management
        result = os.system("python3 tta.prototype/test_worldbuilding_standalone.py > /dev/null 2>&1")
        if result == 0:
            logger.info("✅ Task 7.1: World state management and consistency validation - COMPLETED")
            return True
        else:
            logger.error("❌ Task 7.1: World state management test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Task 7.1 validation failed: {e}")
        return False

def validate_task_7_2():
    """Validate Task 7.2: Therapeutic environment generation and setting adaptation."""
    logger.info("🔍 Validating Task 7.2: Therapeutic environment generation and setting adaptation")

    try:
        # Test therapeutic environment generator
        result = os.system("python3 tta.prototype/test_therapeutic_environment_generator.py > /dev/null 2>&1")
        if result == 0:
            logger.info("✅ Task 7.2: Therapeutic environment generation and setting adaptation - COMPLETED")
            return True
        else:
            logger.error("❌ Task 7.2: Therapeutic environment generator test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Task 7.2 validation failed: {e}")
        return False

def validate_task_7_3():
    """Validate Task 7.3: Integrate worldbuilding with narrative progression."""
    logger.info("🔍 Validating Task 7.3: Integrate worldbuilding with narrative progression")

    try:
        # Test worldbuilding narrative integration
        result = os.system("python3 tta.prototype/validate_task_7_3_complete.py > /dev/null 2>&1")
        if result == 0:
            logger.info("✅ Task 7.3: Integrate worldbuilding with narrative progression - COMPLETED")
            return True
        else:
            logger.error("❌ Task 7.3: Worldbuilding narrative integration test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Task 7.3 validation failed: {e}")
        return False

def validate_integration():
    """Validate that all components work together."""
    logger.info("🔍 Validating overall integration")

    try:
        # Test basic integration without full dependency stack
        sys.path.append(str(Path(__file__).parent))

        # Test that therapeutic environment generator works
        from core.therapeutic_environment_generator import (
            TherapeuticEnvironmentGenerator,
            TherapeuticTheme,
        )

        env_generator = TherapeuticEnvironmentGenerator()
        environment = env_generator.generate_therapeutic_environment(TherapeuticTheme.MINDFULNESS)

        if environment and environment.get('name'):
            logger.info(f"✅ Generated therapeutic environment: {environment['name']}")
        else:
            logger.error("❌ Failed to generate therapeutic environment")
            return False

        # Test adaptation functionality
        result = env_generator.adapt_environment_to_therapeutic_needs(
            environment['location_id'],
            {'emotional_state': 'anxious'}
        )

        if result:
            logger.info("✅ Environment adaptation functionality working")
        else:
            logger.error("❌ Environment adaptation failed")
            return False

        # Test enhancement functionality
        result = env_generator.create_setting_based_therapeutic_enhancement(
            environment['location_id'],
            'sensory_integration'
        )

        if result:
            logger.info("✅ Therapeutic enhancement functionality working")
        else:
            logger.error("❌ Therapeutic enhancement failed")
            return False

        logger.info("✅ All worldbuilding components working together")
        return True

    except Exception as e:
        logger.error(f"❌ Integration validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation function."""
    logger.info("🚀 Starting Task 7 Complete Validation")
    logger.info("Task 7: Develop Worldbuilding and Setting Management")

    validation_steps = [
        ("Task 7.1: World state management and consistency validation", validate_task_7_1),
        ("Task 7.2: Therapeutic environment generation and setting adaptation", validate_task_7_2),
        ("Task 7.3: Integrate worldbuilding with narrative progression", validate_task_7_3),
        ("Overall Integration", validate_integration)
    ]

    results = {}
    for step_name, validation_func in validation_steps:
        logger.info(f"\n{'='*60}")
        logger.info(f"Validating: {step_name}")
        logger.info(f"{'='*60}")

        try:
            results[step_name] = validation_func()
        except Exception as e:
            logger.error(f"❌ Validation failed for {step_name}: {e}")
            results[step_name] = False

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TASK 7 VALIDATION SUMMARY")
    logger.info(f"{'='*60}")

    passed_validations = sum(results.values())
    total_validations = len(results)

    for step_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{step_name}: {status}")

    success_rate = passed_validations / total_validations
    logger.info(f"\nValidation Score: {passed_validations}/{total_validations} ({success_rate:.2f})")

    if success_rate >= 1.0:
        logger.info("🎉 TASK 7 VALIDATION COMPLETE - ALL REQUIREMENTS MET")
        logger.info("\n📋 Task 7: Develop Worldbuilding and Setting Management - COMPLETED")
        logger.info("✅ 7.1 Implement world state management and consistency validation")
        logger.info("✅ 7.2 Build therapeutic environment generation and setting adaptation")
        logger.info("✅ 7.3 Integrate worldbuilding with narrative progression")
        logger.info("\n🎯 All worldbuilding and setting management functionality is now complete!")
        logger.info("   - World state tracking and consistency validation")
        logger.info("   - Therapeutic environment generation and adaptation")
        logger.info("   - Worldbuilding integration with narrative progression")
        logger.info("   - Location unlocking and exploration mechanics")
        logger.info("   - World evolution based on user actions and therapeutic progress")
        return True
    else:
        logger.warning("❌ TASK 7 VALIDATION INCOMPLETE")
        logger.warning("Some requirements are not fully implemented")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
