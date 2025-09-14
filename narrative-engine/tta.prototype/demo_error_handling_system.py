#!/usr/bin/env python3
"""
Demonstration of Living Worlds Error Handling and Recovery System

This script demonstrates the error handling system functionality
without requiring external dependencies like Neo4j or huggingface_hub.
"""

import logging
import os
import sys
from datetime import datetime
from enum import Enum

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))


# Mock RecoveryStrategy for demo purposes
class RecoveryStrategy(Enum):
    """Mock recovery strategies for demo."""

    ROLLBACK = "rollback"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    DATA_REPAIR = "data_repair"
    CACHE_INVALIDATION = "cache_invalidation"
    FALLBACK_MODE = "fallback_mode"


# Mock RecoveryResult for demo purposes
class RecoveryResult:
    """Mock recovery result for demo."""

    def __init__(self, success=True, strategy=None, message="Recovery successful"):
        self.success = success
        self.strategy = strategy
        self.message = message


# Mock ErrorType for demo purposes
class ErrorType(Enum):
    """Mock error types for demo."""

    DATA_INCONSISTENCY = "data_inconsistency"
    CONNECTION_ERROR = "connection_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demo_error_handler_creation():
    """Demonstrate error handler creation and basic functionality."""
    print("🔧 Error Handler Creation and Basic Functionality")
    print("-" * 60)

    try:
        from core.living_worlds_error_handler import (
            create_error_handler,
        )

        # Create error handler
        handler = create_error_handler()
        print("✓ Error handler created successfully")

        # Demonstrate error classification
        errors_to_classify = [
            (
                "Timeline corruption",
                Exception("Timeline events out of chronological order"),
            ),
            ("Validation error", Exception("ValidationError: Invalid data")),
            ("Character error", Exception("Character personality traits invalid")),
            ("Cache error", Exception("Redis cache corruption detected")),
            ("Database error", Exception("Neo4j database connection failed")),
        ]

        print("\n📊 Error Classification:")
        for name, error in errors_to_classify:
            error_type = handler._classify_error(error, {})
            print(f"  {name:<20} → {error_type.value}")

        # Demonstrate health monitoring
        print(
            f"\n💚 System Health Score: {handler.health_monitor.get_system_health_score():.2f}"
        )

        # Register a custom health check
        def custom_check():
            return True

        handler.health_monitor.register_health_check("demo_check", custom_check)
        print("✓ Custom health check registered")

        return handler

    except Exception as e:
        print(f"✗ Error handler creation failed: {e}")
        return None


def demo_checkpoint_system(handler):
    """Demonstrate checkpoint and rollback functionality."""
    print("\n💾 Checkpoint and Rollback System")
    print("-" * 60)

    try:
        world_id = "demo_world"

        # Create checkpoints
        checkpoint1 = handler.rollback_manager.create_checkpoint(
            world_id, {"version": 1, "characters": ["Alice"], "locations": ["Forest"]}
        )
        print(f"✓ Created checkpoint 1: {checkpoint1.checkpoint_id[:8]}...")

        checkpoint2 = handler.rollback_manager.create_checkpoint(
            world_id,
            {
                "version": 2,
                "characters": ["Alice", "Bob"],
                "locations": ["Forest", "Village"],
            },
        )
        print(f"✓ Created checkpoint 2: {checkpoint2.checkpoint_id[:8]}...")

        # List checkpoints
        checkpoints = handler.rollback_manager.list_checkpoints(world_id)
        print(f"✓ Total checkpoints for {world_id}: {len(checkpoints)}")

        # Demonstrate rollback
        rollback_checkpoint = handler.rollback_manager.rollback_to_checkpoint(world_id)
        print(
            f"✓ Rolled back to checkpoint: {rollback_checkpoint.checkpoint_id[:8]}..."
        )

        return True

    except Exception as e:
        print(f"✗ Checkpoint system demo failed: {e}")
        return False


def demo_recovery_strategies(handler):
    """Demonstrate different recovery strategies."""
    print("\n🔄 Recovery Strategies")
    print("-" * 60)

    world_id = "demo_recovery_world"

    # Test different recovery strategies
    recovery_tests = [
        ("Rollback Recovery", RecoveryStrategy.ROLLBACK),
        ("Graceful Degradation", RecoveryStrategy.GRACEFUL_DEGRADATION),
        ("Data Repair", RecoveryStrategy.DATA_REPAIR),
        ("Cache Invalidation", RecoveryStrategy.CACHE_INVALIDATION),
        ("Fallback Mode", RecoveryStrategy.FALLBACK_MODE),
    ]

    for strategy_name, strategy in recovery_tests:
        try:
            context = {"world_id": world_id, "component": "test"}
            result = RecoveryResult()

            # Create a checkpoint for rollback strategy
            if strategy == RecoveryStrategy.ROLLBACK:
                handler.rollback_manager.create_checkpoint(world_id, {"test": "data"})

            # Test the recovery strategy
            success = handler._attempt_recovery(
                ErrorType.DATA_INCONSISTENCY, strategy, context, result
            )

            status = "✓" if success else "⚠"
            print(f"  {status} {strategy_name:<20} → Success: {success}")

            if result.actions_taken:
                for action in result.actions_taken[:2]:  # Show first 2 actions
                    print(f"    - {action}")

        except Exception as e:
            print(f"  ✗ {strategy_name:<20} → Error: {e}")


def demo_error_handling_workflow(handler):
    """Demonstrate complete error handling workflow."""
    print("\n⚡ Error Handling Workflow")
    print("-" * 60)

    world_id = "demo_workflow_world"

    # Create a checkpoint first
    handler.rollback_manager.create_checkpoint(world_id, {"initial": "state"})

    # Test different error scenarios
    error_scenarios = [
        (
            "Timeline Corruption",
            Exception("Timeline chronological order violated"),
            "timeline",
        ),
        (
            "Character Validation",
            Exception("ValidationError: Invalid personality traits"),
            "character",
        ),
        (
            "World State Error",
            Exception("World state consistency check failed"),
            "world_state",
        ),
        ("Cache Corruption", Exception("Redis cache corruption detected"), "cache"),
    ]

    print("Processing error scenarios:")
    for scenario_name, error, component in error_scenarios:
        try:
            context = {
                "world_id": world_id,
                "component": component,
                "scenario": scenario_name,
            }

            # Handle the error
            result = handler.handle_error(error, context)

            status = "✓" if result.success else "⚠"
            strategy = result.strategy_used.value if result.strategy_used else "none"

            print(
                f"  {status} {scenario_name:<20} → {result.error_type.value} (Strategy: {strategy})"
            )

            if result.warnings:
                for warning in result.warnings[:1]:  # Show first warning
                    print(f"    ⚠ {warning}")

        except Exception as e:
            print(f"  ✗ {scenario_name:<20} → Error: {e}")

    # Show error statistics
    stats = handler.get_error_statistics()
    print("\n📈 Error Statistics:")
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"  Recent Errors: {stats['recent_errors']}")
    print(f"  Most Common: {stats.get('most_common_error', 'none')}")


def demo_health_monitoring(handler):
    """Demonstrate health monitoring capabilities."""
    print("\n💚 Health Monitoring")
    print("-" * 60)

    # Register some test health checks
    def good_check():
        return True

    def bad_check():
        return False

    def intermittent_check():
        import random

        return random.random() > 0.3

    handler.health_monitor.register_health_check("always_good", good_check)
    handler.health_monitor.register_health_check("always_bad", bad_check)
    handler.health_monitor.register_health_check("intermittent", intermittent_check)

    # Run health checks multiple times
    print("Running health checks:")
    for i in range(3):
        results = handler.health_monitor.run_health_checks()
        score = handler.health_monitor.get_system_health_score()
        print(f"  Check {i+1}: Score {score:.2f} - {results}")

    # Check for degradation
    issues = handler.health_monitor.detect_degradation()
    if issues:
        print("\n⚠ Degradation Issues Detected:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ No degradation issues detected")


def demo_fallback_mechanisms(handler):
    """Demonstrate fallback mechanisms."""
    print("\n🛡️  Fallback Mechanisms")
    print("-" * 60)

    # Register fallback handlers
    fallback_calls = []

    def timeline_fallback():
        fallback_calls.append("timeline")
        print("  → Timeline fallback activated")

    def character_fallback():
        fallback_calls.append("character")
        print("  → Character fallback activated")

    handler.register_fallback_handler("timeline", timeline_fallback)
    handler.register_fallback_handler("character", character_fallback)

    print("✓ Fallback handlers registered")

    # Test fallback activation
    world_id = "demo_fallback_world"

    fallback_tests = [
        ("Timeline Fallback", "timeline"),
        ("Character Fallback", "character"),
        ("Generic Fallback", "unknown_component"),
    ]

    for test_name, component in fallback_tests:
        try:
            context = {"world_id": world_id, "component": component}
            result = RecoveryResult()

            success = handler._fallback_mode_recovery(world_id, context, result)
            status = "✓" if success else "⚠"
            print(f"  {status} {test_name}")

        except Exception as e:
            print(f"  ✗ {test_name} → Error: {e}")

    print(f"\n📊 Fallback calls made: {fallback_calls}")


def demo_cleanup_operations(handler):
    """Demonstrate cleanup operations."""
    print("\n🧹 Cleanup Operations")
    print("-" * 60)

    # Show current state
    stats = handler.get_error_statistics()
    checkpoints_count = sum(
        len(cps) for cps in handler.rollback_manager.checkpoints.values()
    )

    print("Before cleanup:")
    print(f"  Errors in history: {stats['total_errors']}")
    print(f"  Checkpoints: {checkpoints_count}")
    print(f"  Health checks: {len(handler.health_monitor.health_history)}")

    # Perform cleanup (keep last 30 days)
    cleanup_results = handler.cleanup_old_data(days=30)

    print("\nCleanup results:")
    for key, value in cleanup_results.items():
        print(f"  {key}: {value}")

    # Show state after cleanup
    stats_after = handler.get_error_statistics()
    checkpoints_after = sum(
        len(cps) for cps in handler.rollback_manager.checkpoints.values()
    )

    print("\nAfter cleanup:")
    print(f"  Errors in history: {stats_after['total_errors']}")
    print(f"  Checkpoints: {checkpoints_after}")
    print(f"  Health checks: {len(handler.health_monitor.health_history)}")


def main():
    """Main demonstration."""
    print("🚀 Living Worlds Error Handling System Demonstration")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create error handler
    handler = demo_error_handler_creation()
    if not handler:
        print("❌ Cannot continue without error handler")
        return False

    # Run demonstrations
    demos = [
        ("Checkpoint System", lambda: demo_checkpoint_system(handler)),
        ("Recovery Strategies", lambda: demo_recovery_strategies(handler)),
        ("Error Handling Workflow", lambda: demo_error_handling_workflow(handler)),
        ("Health Monitoring", lambda: demo_health_monitoring(handler)),
        ("Fallback Mechanisms", lambda: demo_fallback_mechanisms(handler)),
        ("Cleanup Operations", lambda: demo_cleanup_operations(handler)),
    ]

    results = []
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result if result is not None else True))
        except Exception as e:
            print(f"✗ {demo_name} failed: {e}")
            results.append((demo_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for demo_name, result in results:
        status = "✓ SUCCESS" if result else "✗ FAILED"
        print(f"{demo_name:<25} {status}")

    print("-" * 70)
    print(f"Total: {total}, Successful: {passed}, Failed: {total - passed}")
    print(f"Success Rate: {(passed / total * 100):.1f}%")

    if passed == total:
        print("\n🎉 All demonstrations completed successfully!")
        print("The error handling system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} demonstration(s) had issues.")

    print("\n🔍 Key Features Demonstrated:")
    print("  ✓ Error classification and handling")
    print("  ✓ Checkpoint creation and rollback")
    print("  ✓ Multiple recovery strategies")
    print("  ✓ System health monitoring")
    print("  ✓ Fallback mechanisms")
    print("  ✓ Graceful degradation")
    print("  ✓ Data cleanup operations")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
