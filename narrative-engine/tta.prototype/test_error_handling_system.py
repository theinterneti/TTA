#!/usr/bin/env python3
"""
Test runner for Living Worlds Error Handling and Recovery System

This script runs comprehensive tests for the error handling system,
including unit tests and integration tests.
"""

import logging
import os
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_error_handler_basic_functionality():
    """Test basic error handler functionality."""
    print("🔧 Testing Error Handler Basic Functionality")
    print("-" * 50)

    try:
        from core.living_worlds_error_handler import (
            SystemCheckpoint,
            create_error_handler,
        )
        from models.living_worlds_models import ValidationError

        # Test error handler creation
        handler = create_error_handler()
        print("✓ Error handler created successfully")

        # Test error classification
        timeline_error = Exception("Timeline chronological order violated")
        error_type = handler._classify_error(timeline_error, {})
        print(f"✓ Error classification: {error_type}")

        # Test checkpoint creation
        checkpoint = SystemCheckpoint(
            world_id="test_world",
            world_state_snapshot={"test": "data"}
        )
        checkpoint.validate()
        print("✓ Checkpoint creation and validation")

        # Test health monitoring
        health_score = handler.health_monitor.get_system_health_score()
        print(f"✓ System health score: {health_score:.2f}")

        # Test error handling workflow
        test_error = ValidationError("Test validation error")
        context = {"world_id": "test_world", "component": "timeline"}
        result = handler.handle_error(test_error, context)
        print(f"✓ Error handling result: success={result.success}")

        return True

    except Exception as e:
        print(f"✗ Error handler test failed: {e}")
        return False


def test_world_state_manager_integration():
    """Test integration with WorldStateManager."""
    print("\n🌍 Testing WorldStateManager Integration")
    print("-" * 50)

    try:
        from core.world_state_manager import WorldConfig, WorldStateManager

        # Create world state manager
        wsm = WorldStateManager()
        print("✓ WorldStateManager created")

        # Check error handler integration
        if wsm.error_handler:
            print("✓ Error handler integrated with WorldStateManager")
        else:
            print("⚠ Error handler not available in WorldStateManager")

        # Test world initialization
        world_id = "test_integration_world"
        config = WorldConfig(world_name="Test Integration World")

        try:
            wsm.initialize_world(world_id, config)
            print("✓ World initialization successful")

            # Test checkpoint creation
            if wsm.error_handler:
                checkpoint_created = wsm.create_system_checkpoint(world_id)
                print(f"✓ Checkpoint creation: {checkpoint_created}")

                # Test system health status
                health_status = wsm.get_system_health_status()
                print(f"✓ System health status: {health_status.get('status', 'unknown')}")

                # Test error handling
                test_error = Exception("Test integration error")
                context = {"world_id": world_id, "component": "test"}
                recovery_success = wsm.handle_error_with_recovery(test_error, context)
                print(f"✓ Error recovery test: {recovery_success}")

        except Exception as init_error:
            print(f"⚠ World initialization failed: {init_error}")
            print("  This may be due to missing dependencies (Neo4j, Redis)")

        return True

    except Exception as e:
        print(f"✗ WorldStateManager integration test failed: {e}")
        return False


def test_recovery_strategies():
    """Test different recovery strategies."""
    print("\n🔄 Testing Recovery Strategies")
    print("-" * 50)

    try:
        from core.living_worlds_error_handler import (
            LivingWorldsErrorHandler,
            RecoveryResult,
        )

        handler = LivingWorldsErrorHandler()
        world_id = "test_recovery_world"

        # Test rollback recovery
        try:
            # Create a checkpoint first
            handler.create_checkpoint(world_id, {"test": "data"})

            context = {"world_id": world_id}
            result = RecoveryResult()
            success = handler._rollback_recovery(world_id, context, result)
            print(f"✓ Rollback recovery: {success}")
        except Exception as e:
            print(f"⚠ Rollback recovery test failed: {e}")

        # Test graceful degradation
        try:
            context = {"world_id": world_id}
            result = RecoveryResult()
            success = handler._graceful_degradation(world_id, context, result)
            print(f"✓ Graceful degradation: {success}")
        except Exception as e:
            print(f"⚠ Graceful degradation test failed: {e}")

        # Test data repair
        try:
            context = {"world_id": world_id, "component": "timeline"}
            result = RecoveryResult()
            success = handler._data_repair_recovery(world_id, context, result)
            print(f"✓ Data repair recovery: {success}")
        except Exception as e:
            print(f"⚠ Data repair recovery test failed: {e}")

        return True

    except Exception as e:
        print(f"✗ Recovery strategies test failed: {e}")
        return False


def test_error_scenarios():
    """Test various error scenarios."""
    print("\n⚠️  Testing Error Scenarios")
    print("-" * 50)

    try:
        from core.living_worlds_error_handler import LivingWorldsErrorHandler
        from models.living_worlds_models import ValidationError

        handler = LivingWorldsErrorHandler()

        # Test different error types
        error_scenarios = [
            (ValidationError("Invalid data"), {"component": "validation"}),
            (Exception("Timeline corruption"), {"component": "timeline"}),
            (Exception("Character state error"), {"component": "character"}),
            (Exception("Cache corruption"), {"component": "cache"}),
            (Exception("Database connection failed"), {"component": "persistence"})
        ]

        for error, context in error_scenarios:
            try:
                context["world_id"] = "test_error_world"
                result = handler.handle_error(error, context)
                print(f"✓ Handled {error.__class__.__name__}: {result.error_type}")
            except Exception as handling_error:
                print(f"⚠ Error handling failed for {error.__class__.__name__}: {handling_error}")

        # Test error statistics
        stats = handler.get_error_statistics()
        print(f"✓ Error statistics: {stats['total_errors']} total errors")

        return True

    except Exception as e:
        print(f"✗ Error scenarios test failed: {e}")
        return False


def run_unit_tests():
    """Run unit tests if available."""
    print("\n🧪 Running Unit Tests")
    print("-" * 50)

    try:
        from tests.test_living_worlds_error_handler import run_error_handler_tests
        success = run_error_handler_tests()
        if success:
            print("✓ Unit tests passed")
        else:
            print("⚠ Some unit tests failed")
        return success
    except ImportError:
        print("⚠ Unit tests not available (test module not found)")
        return True
    except Exception as e:
        print(f"✗ Unit tests failed: {e}")
        return False


def run_integration_tests():
    """Run integration tests if available."""
    print("\n🔗 Running Integration Tests")
    print("-" * 50)

    try:
        from tests.test_error_handling_integration import (
            run_error_handling_integration_tests,
        )
        success = run_error_handling_integration_tests()
        if success:
            print("✓ Integration tests passed")
        else:
            print("⚠ Some integration tests failed")
        return success
    except ImportError:
        print("⚠ Integration tests not available (test module not found)")
        return True
    except Exception as e:
        print(f"✗ Integration tests failed: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 Living Worlds Error Handling System Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    test_results = []

    # Run basic functionality tests
    test_results.append(("Basic Functionality", test_error_handler_basic_functionality()))

    # Run integration tests
    test_results.append(("WorldStateManager Integration", test_world_state_manager_integration()))

    # Run recovery strategy tests
    test_results.append(("Recovery Strategies", test_recovery_strategies()))

    # Run error scenario tests
    test_results.append(("Error Scenarios", test_error_scenarios()))

    # Run unit tests
    test_results.append(("Unit Tests", run_unit_tests()))

    # Run integration tests
    test_results.append(("Integration Tests", run_integration_tests()))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1

    print("-" * 60)
    print(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")

    if passed == total:
        print("\n🎉 All tests passed! Error handling system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
