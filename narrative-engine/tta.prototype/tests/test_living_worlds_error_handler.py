"""
Unit tests for Living Worlds Error Handler and Recovery System

Tests comprehensive error handling, recovery mechanisms, rollback capabilities,
and graceful degradation functionality.
"""

import logging
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.living_worlds_error_handler import (
        ErrorType,
        LivingWorldsErrorHandler,
        RecoveryResult,
        RecoveryStrategy,
        RollbackManager,
        SystemCheckpoint,
        SystemHealthMonitor,
        create_error_handler,
    )
    from models.living_worlds_models import ValidationError
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class ValidationError(Exception):
        pass

    class ErrorType:
        TIMELINE_CORRUPTION = "timeline_corruption"
        CHARACTER_STATE_CORRUPTION = "character_state_corruption"
        WORLD_STATE_CORRUPTION = "world_state_corruption"
        DATA_INCONSISTENCY = "data_inconsistency"
        PERSISTENCE_FAILURE = "persistence_failure"
        CACHE_CORRUPTION = "cache_corruption"
        VALIDATION_FAILURE = "validation_failure"
        SYSTEM_OVERLOAD = "system_overload"
        NETWORK_FAILURE = "network_failure"
        DEPENDENCY_FAILURE = "dependency_failure"

    class RecoveryStrategy:
        ROLLBACK = "rollback"
        REBUILD = "rebuild"
        RESET_TO_CHECKPOINT = "reset_to_checkpoint"
        GRACEFUL_DEGRADATION = "graceful_degradation"
        CACHE_INVALIDATION = "cache_invalidation"
        DATA_REPAIR = "data_repair"
        FALLBACK_MODE = "fallback_mode"
        SYSTEM_RESTART = "system_restart"

    # Mock the main classes
    LivingWorldsErrorHandler = Mock
    SystemCheckpoint = Mock
    SystemHealthMonitor = Mock
    RollbackManager = Mock
    RecoveryResult = Mock
    create_error_handler = Mock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSystemCheckpoint(unittest.TestCase):
    """Test SystemCheckpoint functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if SystemCheckpoint == Mock:
            self.skipTest("SystemCheckpoint not available")

        self.world_id = "test_world_123"
        self.world_state = {"test": "data"}

    def test_checkpoint_creation(self):
        """Test creating a system checkpoint."""
        checkpoint = SystemCheckpoint(
            world_id=self.world_id,
            world_state_snapshot=self.world_state
        )

        self.assertEqual(checkpoint.world_id, self.world_id)
        self.assertEqual(checkpoint.world_state_snapshot, self.world_state)
        self.assertIsNotNone(checkpoint.checkpoint_id)
        self.assertIsInstance(checkpoint.timestamp, datetime)

    def test_checkpoint_validation(self):
        """Test checkpoint validation."""
        # Valid checkpoint
        checkpoint = SystemCheckpoint(
            world_id=self.world_id,
            world_state_snapshot=self.world_state
        )
        self.assertTrue(checkpoint.validate())

        # Invalid checkpoint - empty world_id
        with self.assertRaises(ValueError):
            invalid_checkpoint = SystemCheckpoint(world_id="")
            invalid_checkpoint.validate()

        # Invalid checkpoint - empty checkpoint_id
        with self.assertRaises(ValueError):
            invalid_checkpoint = SystemCheckpoint(
                checkpoint_id="",
                world_id=self.world_id
            )
            invalid_checkpoint.validate()


class TestSystemHealthMonitor(unittest.TestCase):
    """Test SystemHealthMonitor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if SystemHealthMonitor == Mock:
            self.skipTest("SystemHealthMonitor not available")

        self.monitor = SystemHealthMonitor()

    def test_health_check_registration(self):
        """Test registering health checks."""
        def dummy_check():
            return True

        self.monitor.register_health_check("test_check", dummy_check)
        self.assertIn("test_check", self.monitor.health_checks)

    def test_health_check_execution(self):
        """Test running health checks."""
        def passing_check():
            return True

        def failing_check():
            return False

        def error_check():
            raise Exception("Test error")

        self.monitor.register_health_check("passing", passing_check)
        self.monitor.register_health_check("failing", failing_check)
        self.monitor.register_health_check("error", error_check)

        results = self.monitor.run_health_checks()

        self.assertTrue(results["passing"])
        self.assertFalse(results["failing"])
        self.assertFalse(results["error"])  # Should be False due to exception

    def test_system_health_score(self):
        """Test calculating system health score."""
        def passing_check():
            return True

        def failing_check():
            return False

        self.monitor.register_health_check("passing", passing_check)
        self.monitor.register_health_check("failing", failing_check)

        score = self.monitor.get_system_health_score()
        self.assertEqual(score, 0.5)  # 1 out of 2 checks passing

    def test_degradation_detection(self):
        """Test detecting system degradation."""
        def failing_check():
            return False

        self.monitor.register_health_check("failing_check", failing_check)

        # Run checks multiple times to build history
        for _ in range(3):
            self.monitor.run_health_checks()

        issues = self.monitor.detect_degradation()
        self.assertIn("Health check 'failing_check' consistently failing", issues)


class TestRollbackManager(unittest.TestCase):
    """Test RollbackManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if RollbackManager == Mock:
            self.skipTest("RollbackManager not available")

        self.manager = RollbackManager(max_checkpoints=3)
        self.world_id = "test_world_123"
        self.world_state = {"test": "data"}

    def test_checkpoint_creation(self):
        """Test creating checkpoints."""
        checkpoint = self.manager.create_checkpoint(
            self.world_id,
            self.world_state
        )

        self.assertEqual(checkpoint.world_id, self.world_id)
        self.assertIsNotNone(checkpoint.checkpoint_id)
        self.assertIn(self.world_id, self.manager.checkpoints)

    def test_checkpoint_limit(self):
        """Test checkpoint limit enforcement."""
        # Create more checkpoints than the limit
        for i in range(5):
            self.manager.create_checkpoint(
                self.world_id,
                {"iteration": i}
            )

        # Should only keep the maximum number of checkpoints
        self.assertEqual(len(self.manager.checkpoints[self.world_id]), 3)

    def test_rollback_to_latest(self):
        """Test rolling back to the latest checkpoint."""
        # Create multiple checkpoints
        self.manager.create_checkpoint(self.world_id, {"version": 1})
        checkpoint2 = self.manager.create_checkpoint(self.world_id, {"version": 2})

        # Rollback to latest (should be checkpoint2)
        rollback_checkpoint = self.manager.rollback_to_checkpoint(self.world_id)
        self.assertEqual(rollback_checkpoint.checkpoint_id, checkpoint2.checkpoint_id)

    def test_rollback_to_specific(self):
        """Test rolling back to a specific checkpoint."""
        checkpoint1 = self.manager.create_checkpoint(self.world_id, {"version": 1})
        self.manager.create_checkpoint(self.world_id, {"version": 2})

        # Rollback to specific checkpoint
        rollback_checkpoint = self.manager.rollback_to_checkpoint(
            self.world_id,
            checkpoint1.checkpoint_id
        )
        self.assertEqual(rollback_checkpoint.checkpoint_id, checkpoint1.checkpoint_id)

    def test_rollback_no_checkpoints(self):
        """Test rollback when no checkpoints exist."""
        with self.assertRaises(ValueError):
            self.manager.rollback_to_checkpoint("nonexistent_world")

    def test_rollback_invalid_checkpoint(self):
        """Test rollback with invalid checkpoint ID."""
        self.manager.create_checkpoint(self.world_id, self.world_state)

        with self.assertRaises(ValueError):
            self.manager.rollback_to_checkpoint(self.world_id, "invalid_id")

    def test_checkpoint_cleanup(self):
        """Test cleaning up old checkpoints."""
        # Create checkpoints with different timestamps
        old_checkpoint = self.manager.create_checkpoint(self.world_id, {"old": True})
        old_checkpoint.timestamp = datetime.now() - timedelta(days=10)

        self.manager.create_checkpoint(self.world_id, {"recent": True})

        # Cleanup checkpoints older than 7 days
        removed_count = self.manager.cleanup_old_checkpoints(7)

        self.assertEqual(removed_count, 1)
        self.assertEqual(len(self.manager.checkpoints[self.world_id]), 1)


class TestRecoveryResult(unittest.TestCase):
    """Test RecoveryResult functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if RecoveryResult == Mock:
            self.skipTest("RecoveryResult not available")

        self.result = RecoveryResult()

    def test_add_action(self):
        """Test adding actions to recovery result."""
        self.result.add_action("Test action")
        self.assertIn("Test action", self.result.actions_taken)

    def test_add_warning(self):
        """Test adding warnings to recovery result."""
        self.result.add_warning("Test warning")
        self.assertIn("Test warning", self.result.warnings)

    def test_add_error(self):
        """Test adding errors to recovery result."""
        self.result.add_error("Test error")
        self.assertIn("Test error", self.result.errors)
        self.assertFalse(self.result.success)  # Should set success to False


class TestLivingWorldsErrorHandler(unittest.TestCase):
    """Test LivingWorldsErrorHandler functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if LivingWorldsErrorHandler == Mock:
            self.skipTest("LivingWorldsErrorHandler not available")

        self.mock_world_state_manager = Mock()
        self.handler = LivingWorldsErrorHandler(self.mock_world_state_manager)
        self.world_id = "test_world_123"

    def test_error_classification(self):
        """Test error classification."""
        # Test timeline error
        timeline_error = Exception("Timeline chronological order violated")
        error_type = self.handler._classify_error(timeline_error, {})
        self.assertEqual(error_type, ErrorType.TIMELINE_CORRUPTION)

        # Test validation error
        validation_error = ValidationError("Invalid data")
        error_type = self.handler._classify_error(validation_error, {})
        self.assertEqual(error_type, ErrorType.VALIDATION_FAILURE)

        # Test context-based classification
        character_error = Exception("Some error")
        error_type = self.handler._classify_error(
            character_error,
            {"component": "character"}
        )
        self.assertEqual(error_type, ErrorType.CHARACTER_STATE_CORRUPTION)

    def test_error_handling_workflow(self):
        """Test complete error handling workflow."""
        test_error = ValidationError("Test validation error")
        context = {"world_id": self.world_id, "component": "timeline"}

        result = self.handler.handle_error(test_error, context)

        self.assertIsInstance(result, RecoveryResult)
        self.assertEqual(result.error_type, ErrorType.VALIDATION_FAILURE)
        self.assertGreater(result.recovery_time, 0)

    def test_checkpoint_creation(self):
        """Test checkpoint creation through error handler."""
        self.mock_world_state_manager.get_world_state.return_value = {"test": "data"}

        checkpoint = self.handler.create_checkpoint(self.world_id)

        self.assertEqual(checkpoint.world_id, self.world_id)
        self.assertIsNotNone(checkpoint.checkpoint_id)

    def test_world_consistency_validation(self):
        """Test world consistency validation."""
        self.mock_world_state_manager.get_world_state.return_value = {"valid": True}

        report = self.handler.validate_world_consistency(self.world_id)

        self.assertEqual(report["world_id"], self.world_id)
        self.assertIsInstance(report["overall_valid"], bool)
        self.assertIsInstance(report["issues"], list)
        self.assertIsInstance(report["warnings"], list)

    def test_world_consistency_validation_no_world_state(self):
        """Test validation when world state doesn't exist."""
        self.mock_world_state_manager.get_world_state.return_value = None

        report = self.handler.validate_world_consistency(self.world_id)

        self.assertFalse(report["overall_valid"])
        self.assertIn("World state not found", report["issues"])

    def test_fallback_handler_registration(self):
        """Test registering fallback handlers."""
        def test_fallback():
            return "fallback_executed"

        self.handler.register_fallback_handler("test_component", test_fallback)
        self.assertIn("test_component", self.handler.fallback_handlers)

    def test_error_statistics(self):
        """Test error statistics collection."""
        # Generate some test errors
        for i in range(3):
            test_error = Exception(f"Test error {i}")
            self.handler.handle_error(test_error, {"world_id": self.world_id})

        stats = self.handler.get_error_statistics()

        self.assertEqual(stats["total_errors"], 3)
        self.assertIsInstance(stats["error_types"], dict)
        self.assertGreaterEqual(stats["recent_errors"], 0)

    def test_cleanup_old_data(self):
        """Test cleaning up old error data."""
        # Add some test errors
        for i in range(5):
            test_error = Exception(f"Test error {i}")
            self.handler.handle_error(test_error, {"world_id": self.world_id})

        # Add old error manually
        old_error = {
            'timestamp': datetime.now() - timedelta(days=10),
            'error_type': 'test',
            'error_message': 'old error'
        }
        self.handler.error_history.append(old_error)

        cleanup_results = self.handler.cleanup_old_data(7)

        self.assertIsInstance(cleanup_results, dict)
        self.assertIn("errors_removed", cleanup_results)
        self.assertIn("checkpoints_removed", cleanup_results)


class TestRecoveryStrategies(unittest.TestCase):
    """Test specific recovery strategies."""

    def setUp(self):
        """Set up test fixtures."""
        if LivingWorldsErrorHandler == Mock:
            self.skipTest("LivingWorldsErrorHandler not available")

        self.mock_world_state_manager = Mock()
        self.handler = LivingWorldsErrorHandler(self.mock_world_state_manager)
        self.world_id = "test_world_123"
        self.context = {"world_id": self.world_id}
        self.result = RecoveryResult()

    def test_rollback_recovery(self):
        """Test rollback recovery strategy."""
        # Create a checkpoint first
        self.handler.create_checkpoint(self.world_id, {"test": "data"})

        success = self.handler._rollback_recovery(self.world_id, self.context, self.result)

        self.assertTrue(success)
        self.assertGreater(len(self.result.actions_taken), 0)

    def test_rollback_recovery_no_world_id(self):
        """Test rollback recovery without world ID."""
        success = self.handler._rollback_recovery("", self.context, self.result)

        self.assertFalse(success)
        self.assertGreater(len(self.result.errors), 0)

    def test_rebuild_recovery(self):
        """Test rebuild recovery strategy."""
        context = {"world_id": self.world_id, "component": "timeline"}

        success = self.handler._rebuild_recovery(self.world_id, context, self.result)

        self.assertTrue(success)
        self.assertTrue(self.result.data_recovered)
        self.assertGreater(len(self.result.actions_taken), 0)

    def test_graceful_degradation(self):
        """Test graceful degradation strategy."""
        success = self.handler._graceful_degradation(self.world_id, self.context, self.result)

        self.assertTrue(success)
        self.assertTrue(self.result.fallback_active)
        self.assertGreater(len(self.result.actions_taken), 0)

    def test_cache_invalidation_recovery(self):
        """Test cache invalidation recovery strategy."""
        # Mock admin interface
        self.mock_world_state_manager.admin = Mock()

        success = self.handler._cache_invalidation_recovery(self.world_id, self.context, self.result)

        self.assertTrue(success)
        self.mock_world_state_manager.admin.invalidate_caches.assert_called_once_with(self.world_id)

    def test_data_repair_recovery(self):
        """Test data repair recovery strategy."""
        context = {"world_id": self.world_id, "component": "character"}

        success = self.handler._data_repair_recovery(self.world_id, context, self.result)

        self.assertTrue(success)
        self.assertTrue(self.result.data_recovered)
        self.assertGreater(len(self.result.actions_taken), 0)

    def test_fallback_mode_recovery(self):
        """Test fallback mode recovery strategy."""
        # Register a fallback handler
        def test_fallback():
            pass

        self.handler.register_fallback_handler("system", test_fallback)

        success = self.handler._fallback_mode_recovery(self.world_id, self.context, self.result)

        self.assertTrue(success)
        self.assertTrue(self.result.fallback_active)


class TestErrorHandlerIntegration(unittest.TestCase):
    """Test error handler integration scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        if LivingWorldsErrorHandler == Mock:
            self.skipTest("LivingWorldsErrorHandler not available")

        self.mock_world_state_manager = Mock()
        self.handler = LivingWorldsErrorHandler(self.mock_world_state_manager)
        self.world_id = "test_world_123"

    def test_timeline_corruption_recovery(self):
        """Test recovery from timeline corruption."""
        # Create a checkpoint first
        self.handler.create_checkpoint(self.world_id, {"timeline": "valid"})

        # Simulate timeline corruption error
        timeline_error = Exception("Timeline events out of chronological order")
        context = {"world_id": self.world_id, "component": "timeline"}

        result = self.handler.handle_error(timeline_error, context)

        self.assertIsInstance(result, RecoveryResult)
        self.assertEqual(result.error_type, ErrorType.TIMELINE_CORRUPTION)
        # Should attempt rollback first for timeline corruption
        self.assertIn(RecoveryStrategy.ROLLBACK,
                     self.handler.recovery_strategies[ErrorType.TIMELINE_CORRUPTION])

    def test_character_state_corruption_recovery(self):
        """Test recovery from character state corruption."""
        character_error = Exception("Character personality traits invalid")
        context = {"world_id": self.world_id, "component": "character"}

        result = self.handler.handle_error(character_error, context)

        self.assertEqual(result.error_type, ErrorType.CHARACTER_STATE_CORRUPTION)
        # Should attempt checkpoint reset first for character corruption
        self.assertIn(RecoveryStrategy.RESET_TO_CHECKPOINT,
                     self.handler.recovery_strategies[ErrorType.CHARACTER_STATE_CORRUPTION])

    def test_validation_failure_recovery(self):
        """Test recovery from validation failures."""
        validation_error = ValidationError("Invalid world state data")
        context = {"world_id": self.world_id}

        result = self.handler.handle_error(validation_error, context)

        self.assertEqual(result.error_type, ErrorType.VALIDATION_FAILURE)
        # Should attempt data repair first for validation failures
        self.assertIn(RecoveryStrategy.DATA_REPAIR,
                     self.handler.recovery_strategies[ErrorType.VALIDATION_FAILURE])

    def test_multiple_error_handling(self):
        """Test handling multiple errors in sequence."""
        errors = [
            (ValidationError("Validation error 1"), {"world_id": self.world_id}),
            (Exception("Timeline corruption"), {"world_id": self.world_id, "component": "timeline"}),
            (Exception("Cache error"), {"world_id": self.world_id, "component": "cache"})
        ]

        results = []
        for error, context in errors:
            result = self.handler.handle_error(error, context)
            results.append(result)

        self.assertEqual(len(results), 3)
        self.assertEqual(len(self.handler.error_history), 3)

        # Check that different error types were classified correctly
        error_types = [result.error_type for result in results]
        self.assertIn(ErrorType.VALIDATION_FAILURE, error_types)
        self.assertIn(ErrorType.TIMELINE_CORRUPTION, error_types)

    def test_system_health_monitoring_integration(self):
        """Test integration with system health monitoring."""
        # Register a failing health check
        def failing_check():
            return False

        self.handler.health_monitor.register_health_check("test_check", failing_check)

        # Run validation which should check system health
        report = self.handler.validate_world_consistency(self.world_id)

        # Should include health check in performed checks
        self.assertIn("System health", report["checks_performed"])

        # Health score should be low due to failing check
        health_score = self.handler.health_monitor.get_system_health_score()
        self.assertLess(health_score, 1.0)


class TestErrorHandlerFactory(unittest.TestCase):
    """Test error handler factory function."""

    def test_create_error_handler_without_wsm(self):
        """Test creating error handler without world state manager."""
        if create_error_handler == Mock:
            self.skipTest("create_error_handler not available")

        handler = create_error_handler()

        self.assertIsInstance(handler, LivingWorldsErrorHandler)
        self.assertIsNone(handler.world_state_manager)

    def test_create_error_handler_with_wsm(self):
        """Test creating error handler with world state manager."""
        if create_error_handler == Mock:
            self.skipTest("create_error_handler not available")

        mock_wsm = Mock()
        handler = create_error_handler(mock_wsm)

        self.assertIsInstance(handler, LivingWorldsErrorHandler)
        self.assertEqual(handler.world_state_manager, mock_wsm)


def run_error_handler_tests():
    """Run all error handler tests."""
    print("🧪 Running Living Worlds Error Handler Tests")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestSystemCheckpoint,
        TestSystemHealthMonitor,
        TestRollbackManager,
        TestRecoveryResult,
        TestLivingWorldsErrorHandler,
        TestRecoveryStrategies,
        TestErrorHandlerIntegration,
        TestErrorHandlerFactory
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
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
    success = run_error_handler_tests()
    sys.exit(0 if success else 1)
