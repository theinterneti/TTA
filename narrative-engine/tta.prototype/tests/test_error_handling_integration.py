"""
Integration tests for Living Worlds Error Handling and Recovery System

Tests the integration of error handling with the WorldStateManager and
other Living Worlds components, including real-world error scenarios
and recovery effectiveness.
"""

import logging
import os
import sys
import unittest
from unittest.mock import Mock

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.living_worlds_error_handler import (
        ErrorType,
        LivingWorldsErrorHandler,
        RecoveryStrategy,
        create_error_handler,
    )
    from core.world_state_manager import WorldConfig, WorldStateManager
    from models.living_worlds_models import (
        EntityType,
        EventType,
        TimelineEvent,
        ValidationError,
        WorldState,
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False
    # Create mock classes for testing
    WorldStateManager = Mock
    LivingWorldsErrorHandler = Mock
    WorldState = Mock
    TimelineEvent = Mock
    ValidationError = Exception

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling integration with WorldStateManager."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required imports not available")

        # Create a mock world state manager with error handling
        self.world_id = "test_world_integration"
        self.wsm = WorldStateManager()
        self.error_handler = self.wsm.error_handler

        # Create a test world
        config = WorldConfig(world_name="Test Integration World")
        try:
            self.world_state = self.wsm.initialize_world(self.world_id, config)
        except Exception:
            # If initialization fails, create a mock world state
            self.world_state = Mock()
            self.world_state.world_id = self.world_id

    def test_timeline_corruption_recovery(self):
        """Test recovery from timeline corruption errors."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Create a checkpoint before corruption
        checkpoint_created = self.wsm.create_system_checkpoint(self.world_id)
        self.assertTrue(checkpoint_created)

        # Simulate timeline corruption
        timeline_error = Exception("Timeline events out of chronological order")
        context = {
            'world_id': self.world_id,
            'component': 'timeline',
            'entity_id': 'test_character'
        }

        # Test error handling
        recovery_success = self.wsm.handle_error_with_recovery(timeline_error, context)

        # Should attempt recovery (may succeed or fail depending on implementation)
        self.assertIsInstance(recovery_success, bool)

        # Check that error was recorded
        error_stats = self.error_handler.get_error_statistics()
        self.assertGreater(error_stats['total_errors'], 0)

    def test_character_state_corruption_recovery(self):
        """Test recovery from character state corruption."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Add a test character
        character_data = {
            'name': 'Test Character',
            'personality_traits': {'openness': 0.7}
        }
        self.wsm.add_character(self.world_id, 'test_char', character_data)

        # Simulate character corruption
        character_error = ValidationError("Invalid personality trait values")
        context = {
            'world_id': self.world_id,
            'component': 'character',
            'entity_id': 'test_char'
        }

        # Test error handling
        recovery_success = self.wsm.handle_error_with_recovery(character_error, context)
        self.assertIsInstance(recovery_success, bool)

    def test_world_consistency_validation_and_recovery(self):
        """Test world consistency validation with automatic recovery."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Run consistency validation
        report = self.wsm.validate_world_consistency_with_recovery(self.world_id)

        # Check report structure
        self.assertIn('world_id', report)
        self.assertIn('overall_valid', report)
        self.assertIn('issues', report)
        self.assertEqual(report['world_id'], self.world_id)
        self.assertIsInstance(report['overall_valid'], bool)
        self.assertIsInstance(report['issues'], list)

    def test_system_health_monitoring(self):
        """Test system health monitoring integration."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Get system health status
        health_status = self.wsm.get_system_health_status()

        # Check health status structure
        self.assertIn('error_handler_available', health_status)
        self.assertIn('system_health_score', health_status)
        self.assertIn('status', health_status)

        self.assertTrue(health_status['error_handler_available'])
        self.assertIsInstance(health_status['system_health_score'], float)
        self.assertIn(health_status['status'], ['healthy', 'stable', 'degraded', 'critical', 'error'])

    def test_graceful_degradation_activation(self):
        """Test manual activation of graceful degradation."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Enable graceful degradation
        degradation_enabled = self.wsm.enable_graceful_degradation(
            self.world_id,
            "Test degradation scenario"
        )

        self.assertIsInstance(degradation_enabled, bool)

        # Check that degradation was recorded if successful
        if degradation_enabled:
            health_status = self.wsm.get_system_health_status()
            # System should still be functional but possibly degraded
            self.assertIsNotNone(health_status)

    def test_checkpoint_creation_and_rollback(self):
        """Test checkpoint creation and rollback functionality."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Create initial checkpoint
        checkpoint1_created = self.wsm.create_system_checkpoint(self.world_id)
        self.assertTrue(checkpoint1_created)

        # Make some changes to the world
        self.wsm.add_character(self.world_id, 'temp_char', {'name': 'Temporary'})

        # Create another checkpoint
        checkpoint2_created = self.wsm.create_system_checkpoint(self.world_id)
        self.assertTrue(checkpoint2_created)

        # Test that checkpoints exist
        checkpoints = self.error_handler.rollback_manager.list_checkpoints(self.world_id)
        self.assertGreaterEqual(len(checkpoints), 1)

    def test_error_statistics_collection(self):
        """Test error statistics collection and reporting."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Generate some test errors
        test_errors = [
            (ValidationError("Test validation error"), {'world_id': self.world_id}),
            (Exception("Test timeline error"), {'world_id': self.world_id, 'component': 'timeline'}),
            (Exception("Test character error"), {'world_id': self.world_id, 'component': 'character'})
        ]

        for error, context in test_errors:
            self.wsm.handle_error_with_recovery(error, context)

        # Check error statistics
        error_stats = self.error_handler.get_error_statistics()

        self.assertIn('total_errors', error_stats)
        self.assertIn('error_types', error_stats)
        self.assertIn('recent_errors', error_stats)

        self.assertGreaterEqual(error_stats['total_errors'], len(test_errors))
        self.assertIsInstance(error_stats['error_types'], dict)

    def test_cleanup_old_data(self):
        """Test cleanup of old error data and checkpoints."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Generate some test data
        self.wsm.create_system_checkpoint(self.world_id)
        self.wsm.handle_error_with_recovery(
            Exception("Test error for cleanup"),
            {'world_id': self.world_id}
        )

        # Perform cleanup
        cleanup_results = self.wsm.cleanup_error_data(days=30)

        self.assertIsInstance(cleanup_results, dict)
        # Should have cleanup statistics (even if 0)
        self.assertIn('errors_removed', cleanup_results)
        self.assertIn('checkpoints_removed', cleanup_results)


class TestErrorRecoveryScenarios(unittest.TestCase):
    """Test specific error recovery scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required imports not available")

        self.world_id = "test_recovery_scenarios"
        self.wsm = WorldStateManager()
        self.error_handler = self.wsm.error_handler

        # Initialize test world
        config = WorldConfig(world_name="Recovery Test World")
        try:
            self.world_state = self.wsm.initialize_world(self.world_id, config)
        except Exception:
            self.world_state = Mock()
            self.world_state.world_id = self.world_id

    def test_persistence_failure_recovery(self):
        """Test recovery from persistence layer failures."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Simulate persistence failure
        persistence_error = Exception("Database connection failed")
        context = {
            'world_id': self.world_id,
            'component': 'persistence'
        }

        recovery_success = self.wsm.handle_error_with_recovery(persistence_error, context)
        self.assertIsInstance(recovery_success, bool)

        # Check that fallback mode might be activated
        health_status = self.wsm.get_system_health_status()
        self.assertIsNotNone(health_status)

    def test_cache_corruption_recovery(self):
        """Test recovery from cache corruption."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Simulate cache corruption
        cache_error = Exception("Redis cache corruption detected")
        context = {
            'world_id': self.world_id,
            'component': 'cache',
            'cache_keys': ['world_state:' + self.world_id]
        }

        recovery_success = self.wsm.handle_error_with_recovery(cache_error, context)
        self.assertIsInstance(recovery_success, bool)

    def test_validation_failure_recovery(self):
        """Test recovery from data validation failures."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Simulate validation failure
        validation_error = ValidationError("World state data validation failed")
        context = {
            'world_id': self.world_id,
            'component': 'world_state'
        }

        recovery_success = self.wsm.handle_error_with_recovery(validation_error, context)
        self.assertIsInstance(recovery_success, bool)

    def test_system_overload_recovery(self):
        """Test recovery from system overload conditions."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Simulate system overload
        overload_error = Exception("System memory usage exceeded 95%")
        context = {
            'world_id': self.world_id,
            'component': 'system'
        }

        recovery_success = self.wsm.handle_error_with_recovery(overload_error, context)
        self.assertIsInstance(recovery_success, bool)

        # System should attempt graceful degradation
        health_status = self.wsm.get_system_health_status()
        self.assertIsNotNone(health_status)


class TestErrorHandlerHealthChecks(unittest.TestCase):
    """Test error handler health check functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required imports not available")

        self.wsm = WorldStateManager()
        self.error_handler = self.wsm.error_handler

    def test_custom_health_check_registration(self):
        """Test registering custom health checks."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Register a custom health check
        def custom_check():
            return True

        self.error_handler.health_monitor.register_health_check("custom_test", custom_check)

        # Run health checks
        results = self.error_handler.health_monitor.run_health_checks()
        self.assertIn("custom_test", results)
        self.assertTrue(results["custom_test"])

    def test_health_degradation_detection(self):
        """Test detection of system health degradation."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Register a failing health check
        def failing_check():
            return False

        self.error_handler.health_monitor.register_health_check("failing_test", failing_check)

        # Run checks multiple times to build history
        for _ in range(3):
            self.error_handler.health_monitor.run_health_checks()

        # Check for degradation
        issues = self.error_handler.health_monitor.detect_degradation()
        self.assertIsInstance(issues, list)

        # Should detect the consistently failing check
        failing_issues = [issue for issue in issues if "failing_test" in issue]
        self.assertGreater(len(failing_issues), 0)

    def test_system_health_score_calculation(self):
        """Test system health score calculation."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Register mixed health checks
        def passing_check():
            return True

        def failing_check():
            return False

        self.error_handler.health_monitor.register_health_check("passing", passing_check)
        self.error_handler.health_monitor.register_health_check("failing", failing_check)

        # Calculate health score
        score = self.error_handler.health_monitor.get_system_health_score()

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

        # With one passing and one failing check, score should be 0.5
        self.assertEqual(score, 0.5)


class TestErrorHandlerFallbackMechanisms(unittest.TestCase):
    """Test fallback mechanisms in error handling."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required imports not available")

        self.wsm = WorldStateManager()
        self.error_handler = self.wsm.error_handler
        self.world_id = "test_fallback_world"

    def test_fallback_handler_registration(self):
        """Test registering and using fallback handlers."""
        if not self.error_handler:
            self.skipTest("Error handler not available")

        # Register a fallback handler
        fallback_called = False

        def test_fallback():
            nonlocal fallback_called
            fallback_called = True

        self.error_handler.register_fallback_handler("test_component", test_fallback)

        # Trigger fallback mode
        context = {'world_id': self.world_id, 'component': 'test_component'}
        result = self.error_handler._fallback_mode_recovery(self.world_id, context,
                                                          self.error_handler.RecoveryResult())

        self.assertTrue(result)
        self.assertTrue(fallback_called)

    def test_graceful_degradation_without_world_state_manager(self):
        """Test graceful degradation when world state manager is not available."""
        # Create error handler without world state manager
        standalone_handler = create_error_handler(None)

        # Test graceful degradation
        context = {'world_id': self.world_id}
        result = standalone_handler._graceful_degradation(self.world_id, context,
                                                        standalone_handler.RecoveryResult())

        self.assertTrue(result)


def run_error_handling_integration_tests():
    """Run all error handling integration tests."""
    print("🧪 Running Living Worlds Error Handling Integration Tests")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestErrorHandlingIntegration,
        TestErrorRecoveryScenarios,
        TestErrorHandlerHealthChecks,
        TestErrorHandlerFallbackMechanisms
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print(f"Integration Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_error_handling_integration_tests()
    sys.exit(0 if success else 1)
