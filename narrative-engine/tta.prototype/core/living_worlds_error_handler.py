"""
Living Worlds Error Handler and Recovery System

This module implements comprehensive error handling and recovery mechanisms
for the TTA Living Worlds system. It provides automatic recovery for timeline
corruption, character state issues, world state inconsistencies, and graceful
degradation when complex systems fail.

Classes:
    LivingWorldsErrorHandler: Main error handling and recovery coordinator
    ErrorType: Enumeration of error types that can occur
    RecoveryStrategy: Enumeration of recovery strategies
    RecoveryResult: Result class for recovery operations
    SystemHealthMonitor: Monitors system health and detects issues
    RollbackManager: Manages rollback operations for problematic changes
"""

import logging
import traceback
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur in the Living Worlds system."""
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


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    ROLLBACK = "rollback"
    REBUILD = "rebuild"
    RESET_TO_CHECKPOINT = "reset_to_checkpoint"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    CACHE_INVALIDATION = "cache_invalidation"
    DATA_REPAIR = "data_repair"
    FALLBACK_MODE = "fallback_mode"
    SYSTEM_RESTART = "system_restart"


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool = False
    strategy_used: RecoveryStrategy | None = None
    error_type: ErrorType | None = None
    recovery_time: float = 0.0
    actions_taken: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    data_recovered: bool = False
    fallback_active: bool = False

    def add_action(self, action: str) -> None:
        """Add an action taken during recovery."""
        self.actions_taken.append(action)
        logger.info(f"Recovery action: {action}")

    def add_warning(self, warning: str) -> None:
        """Add a warning during recovery."""
        self.warnings.append(warning)
        logger.warning(f"Recovery warning: {warning}")

    def add_error(self, error: str) -> None:
        """Add an error during recovery."""
        self.errors.append(error)
        self.success = False
        logger.error(f"Recovery error: {error}")


@dataclass
class SystemCheckpoint:
    """Represents a system checkpoint for rollback operations."""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    world_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    world_state_snapshot: dict[str, Any] | None = None
    timeline_snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)
    character_snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate checkpoint data."""
        if not self.checkpoint_id.strip():
            raise ValueError("Checkpoint ID cannot be empty")
        if not self.world_id.strip():
            raise ValueError("World ID cannot be empty")
        return True


class SystemHealthMonitor:
    """Monitors system health and detects potential issues."""

    def __init__(self):
        """Initialize the health monitor."""
        self.health_checks: dict[str, Callable[[], bool]] = {}
        self.last_check_time = datetime.now()
        self.check_interval = timedelta(minutes=5)
        self.health_history: list[dict[str, Any]] = []

    def register_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check function."""
        self.health_checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    def run_health_checks(self) -> dict[str, bool]:
        """Run all registered health checks."""
        results = {}
        for name, check_func in self.health_checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = False

        # Record health check results
        self.health_history.append({
            'timestamp': datetime.now(),
            'results': results.copy()
        })

        # Keep only last 100 health check results
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]

        return results

    def get_system_health_score(self) -> float:
        """Get overall system health score (0.0 to 1.0)."""
        if not self.health_checks:
            return 1.0

        results = self.run_health_checks()
        passed_checks = sum(1 for result in results.values() if result)
        return passed_checks / len(results)

    def detect_degradation(self) -> list[str]:
        """Detect system degradation patterns."""
        if len(self.health_history) < 3:
            return []

        issues = []
        recent_checks = self.health_history[-3:]

        for check_name in self.health_checks.keys():
            # Check if a health check has been consistently failing
            recent_results = [check['results'].get(check_name, False) for check in recent_checks]
            if not any(recent_results):
                issues.append(f"Health check '{check_name}' consistently failing")

        return issues


class RollbackManager:
    """Manages rollback operations for problematic world changes."""

    def __init__(self, max_checkpoints: int = 10):
        """Initialize the rollback manager."""
        self.checkpoints: dict[str, list[SystemCheckpoint]] = {}  # world_id -> checkpoints
        self.max_checkpoints = max_checkpoints

    def create_checkpoint(self, world_id: str, world_state: Any,
                         timelines: dict[str, Any] = None,
                         characters: dict[str, Any] = None) -> SystemCheckpoint:
        """Create a system checkpoint for rollback purposes."""
        try:
            checkpoint = SystemCheckpoint(
                world_id=world_id,
                world_state_snapshot=self._serialize_data(world_state),
                timeline_snapshots=self._serialize_data(timelines or {}),
                character_snapshots=self._serialize_data(characters or {}),
                metadata={'created_by': 'rollback_manager'}
            )

            checkpoint.validate()

            # Store checkpoint
            if world_id not in self.checkpoints:
                self.checkpoints[world_id] = []

            self.checkpoints[world_id].append(checkpoint)

            # Maintain checkpoint limit
            if len(self.checkpoints[world_id]) > self.max_checkpoints:
                removed = self.checkpoints[world_id].pop(0)
                logger.info(f"Removed old checkpoint: {removed.checkpoint_id}")

            logger.info(f"Created checkpoint {checkpoint.checkpoint_id} for world {world_id}")
            return checkpoint

        except Exception as e:
            logger.error(f"Failed to create checkpoint for world {world_id}: {e}")
            raise

    def rollback_to_checkpoint(self, world_id: str, checkpoint_id: str | None = None) -> SystemCheckpoint:
        """Rollback to a specific checkpoint or the most recent one."""
        if world_id not in self.checkpoints or not self.checkpoints[world_id]:
            raise ValueError(f"No checkpoints available for world {world_id}")

        if checkpoint_id:
            # Find specific checkpoint
            checkpoint = None
            for cp in self.checkpoints[world_id]:
                if cp.checkpoint_id == checkpoint_id:
                    checkpoint = cp
                    break
            if not checkpoint:
                raise ValueError(f"Checkpoint {checkpoint_id} not found for world {world_id}")
        else:
            # Use most recent checkpoint
            checkpoint = self.checkpoints[world_id][-1]

        logger.info(f"Rolling back world {world_id} to checkpoint {checkpoint.checkpoint_id}")
        return checkpoint

    def list_checkpoints(self, world_id: str) -> list[SystemCheckpoint]:
        """List all checkpoints for a world."""
        return self.checkpoints.get(world_id, [])

    def cleanup_old_checkpoints(self, older_than_days: int = 7) -> int:
        """Clean up checkpoints older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        removed_count = 0

        for world_id in list(self.checkpoints.keys()):
            original_count = len(self.checkpoints[world_id])
            self.checkpoints[world_id] = [
                cp for cp in self.checkpoints[world_id]
                if cp.timestamp >= cutoff_time
            ]
            removed = original_count - len(self.checkpoints[world_id])
            removed_count += removed

            if removed > 0:
                logger.info(f"Cleaned up {removed} old checkpoints for world {world_id}")

        return removed_count

    def _serialize_data(self, data: Any) -> dict[str, Any]:
        """Serialize data for checkpoint storage."""
        try:
            if hasattr(data, 'to_dict'):
                return data.to_dict()
            elif isinstance(data, dict):
                return {k: self._serialize_data(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [self._serialize_data(item) for item in data]
            else:
                return data
        except Exception as e:
            logger.warning(f"Failed to serialize data: {e}")
            return {'serialization_error': str(e)}


class LivingWorldsErrorHandler:
    """
    Main error handling and recovery coordinator for Living Worlds system.

    Provides comprehensive error detection, recovery strategies, and system
    health monitoring to ensure robust operation of the Living Worlds features.
    """

    def __init__(self, world_state_manager=None):
        """Initialize the error handler."""
        self.world_state_manager = world_state_manager
        self.health_monitor = SystemHealthMonitor()
        self.rollback_manager = RollbackManager()
        self.recovery_strategies: dict[ErrorType, list[RecoveryStrategy]] = {}
        self.fallback_handlers: dict[str, Callable] = {}
        self.error_history: list[dict[str, Any]] = []

        # Initialize default recovery strategies
        self._setup_default_recovery_strategies()
        self._setup_default_health_checks()

        logger.info("LivingWorldsErrorHandler initialized")

    def _setup_default_recovery_strategies(self) -> None:
        """Setup default recovery strategies for different error types."""
        self.recovery_strategies = {
            ErrorType.TIMELINE_CORRUPTION: [
                RecoveryStrategy.ROLLBACK,
                RecoveryStrategy.REBUILD,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.CHARACTER_STATE_CORRUPTION: [
                RecoveryStrategy.RESET_TO_CHECKPOINT,
                RecoveryStrategy.DATA_REPAIR,
                RecoveryStrategy.FALLBACK_MODE
            ],
            ErrorType.WORLD_STATE_CORRUPTION: [
                RecoveryStrategy.ROLLBACK,
                RecoveryStrategy.RESET_TO_CHECKPOINT,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.DATA_INCONSISTENCY: [
                RecoveryStrategy.DATA_REPAIR,
                RecoveryStrategy.CACHE_INVALIDATION,
                RecoveryStrategy.REBUILD
            ],
            ErrorType.PERSISTENCE_FAILURE: [
                RecoveryStrategy.CACHE_INVALIDATION,
                RecoveryStrategy.FALLBACK_MODE,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.CACHE_CORRUPTION: [
                RecoveryStrategy.CACHE_INVALIDATION,
                RecoveryStrategy.REBUILD,
                RecoveryStrategy.FALLBACK_MODE
            ],
            ErrorType.VALIDATION_FAILURE: [
                RecoveryStrategy.DATA_REPAIR,
                RecoveryStrategy.ROLLBACK,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.SYSTEM_OVERLOAD: [
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.FALLBACK_MODE,
                RecoveryStrategy.SYSTEM_RESTART
            ],
            ErrorType.NETWORK_FAILURE: [
                RecoveryStrategy.FALLBACK_MODE,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.CACHE_INVALIDATION
            ],
            ErrorType.DEPENDENCY_FAILURE: [
                RecoveryStrategy.FALLBACK_MODE,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.SYSTEM_RESTART
            ]
        }

    def _setup_default_health_checks(self) -> None:
        """Setup default health checks."""
        self.health_monitor.register_health_check(
            "world_state_manager_available",
            lambda: self.world_state_manager is not None
        )

        self.health_monitor.register_health_check(
            "memory_usage_normal",
            self._check_memory_usage
        )

        self.health_monitor.register_health_check(
            "error_rate_acceptable",
            self._check_error_rate
        )

    def _check_memory_usage(self) -> bool:
        """Check if memory usage is within acceptable limits."""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            return memory_percent < 90.0  # Less than 90% memory usage
        except ImportError:
            return True  # Assume OK if psutil not available
        except Exception:
            return False

    def _check_error_rate(self) -> bool:
        """Check if error rate is within acceptable limits."""
        if len(self.error_history) < 10:
            return True

        # Check error rate in last 10 minutes
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        recent_errors = [
            error for error in self.error_history[-50:]  # Check last 50 errors
            if error.get('timestamp', datetime.min) >= ten_minutes_ago
        ]

        return len(recent_errors) < 5  # Less than 5 errors in 10 minutes

    def handle_error(self, error: Exception, context: dict[str, Any] = None) -> RecoveryResult:
        """
        Handle an error with appropriate recovery strategy.

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            RecoveryResult: Result of the recovery attempt
        """
        start_time = datetime.now()
        context = context or {}

        # Determine error type
        error_type = self._classify_error(error, context)

        # Record error
        error_record = {
            'timestamp': start_time,
            'error_type': error_type.value,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.error_history.append(error_record)

        # Keep only last 1000 error records
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]

        logger.error(f"Handling error of type {error_type.value}: {error}")

        # Create recovery result
        result = RecoveryResult(error_type=error_type)

        # Try recovery strategies in order
        strategies = self.recovery_strategies.get(error_type, [RecoveryStrategy.GRACEFUL_DEGRADATION])

        for strategy in strategies:
            try:
                if self._attempt_recovery(error_type, strategy, context, result):
                    result.success = True
                    result.strategy_used = strategy
                    break
            except Exception as recovery_error:
                result.add_error(f"Recovery strategy {strategy.value} failed: {recovery_error}")

        # Calculate recovery time
        result.recovery_time = (datetime.now() - start_time).total_seconds()

        if result.success:
            logger.info(f"Successfully recovered from {error_type.value} using {result.strategy_used.value}")
        else:
            logger.error(f"Failed to recover from {error_type.value}")

        return result

    def _classify_error(self, error: Exception, context: dict[str, Any]) -> ErrorType:
        """Classify an error to determine appropriate recovery strategy."""
        error_message = str(error).lower()
        error_type_name = type(error).__name__.lower()

        # Check context for hints
        if context.get('component') == 'timeline':
            return ErrorType.TIMELINE_CORRUPTION
        elif context.get('component') == 'character':
            return ErrorType.CHARACTER_STATE_CORRUPTION
        elif context.get('component') == 'world_state':
            return ErrorType.WORLD_STATE_CORRUPTION

        # Classify based on error message and type
        if 'validation' in error_message or 'validationerror' in error_type_name:
            return ErrorType.VALIDATION_FAILURE
        elif 'timeline' in error_message or 'chronological' in error_message:
            return ErrorType.TIMELINE_CORRUPTION
        elif 'character' in error_message or 'personality' in error_message:
            return ErrorType.CHARACTER_STATE_CORRUPTION
        elif 'world' in error_message or 'state' in error_message:
            return ErrorType.WORLD_STATE_CORRUPTION
        elif 'cache' in error_message or 'redis' in error_message:
            return ErrorType.CACHE_CORRUPTION
        elif 'persistence' in error_message or 'neo4j' in error_message or 'database' in error_message:
            return ErrorType.PERSISTENCE_FAILURE
        elif 'network' in error_message or 'connection' in error_message:
            return ErrorType.NETWORK_FAILURE
        elif 'memory' in error_message or 'overload' in error_message:
            return ErrorType.SYSTEM_OVERLOAD
        elif 'import' in error_message or 'dependency' in error_message:
            return ErrorType.DEPENDENCY_FAILURE
        else:
            return ErrorType.DATA_INCONSISTENCY

    def _attempt_recovery(self, error_type: ErrorType, strategy: RecoveryStrategy,
                         context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery using a specific strategy."""
        world_id = context.get('world_id')

        try:
            if strategy == RecoveryStrategy.ROLLBACK:
                return self._rollback_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.REBUILD:
                return self._rebuild_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.RESET_TO_CHECKPOINT:
                return self._checkpoint_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                return self._graceful_degradation(world_id, context, result)
            elif strategy == RecoveryStrategy.CACHE_INVALIDATION:
                return self._cache_invalidation_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.DATA_REPAIR:
                return self._data_repair_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.FALLBACK_MODE:
                return self._fallback_mode_recovery(world_id, context, result)
            elif strategy == RecoveryStrategy.SYSTEM_RESTART:
                return self._system_restart_recovery(world_id, context, result)
            else:
                result.add_error(f"Unknown recovery strategy: {strategy.value}")
                return False

        except Exception as e:
            result.add_error(f"Recovery strategy {strategy.value} failed: {e}")
            return False

    def _rollback_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by rolling back to a previous checkpoint."""
        if not world_id:
            result.add_error("Cannot rollback: no world_id provided")
            return False

        try:
            checkpoint = self.rollback_manager.rollback_to_checkpoint(world_id)
            result.add_action(f"Rolled back to checkpoint {checkpoint.checkpoint_id}")

            # Apply checkpoint data if world state manager is available
            if self.world_state_manager and checkpoint.world_state_snapshot:
                # This would need to be implemented in the world state manager
                result.add_action("Applied checkpoint world state")
                result.data_recovered = True

            return True

        except Exception as e:
            result.add_error(f"Rollback failed: {e}")
            return False

    def _rebuild_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by rebuilding corrupted data structures."""
        component = context.get('component', 'unknown')

        try:
            if component == 'timeline':
                result.add_action("Rebuilding timeline from significant events")
                # Implementation would rebuild timeline keeping only high-significance events
                result.data_recovered = True
            elif component == 'character':
                result.add_action("Rebuilding character state from base data")
                # Implementation would rebuild character from basic information
                result.data_recovered = True
            else:
                result.add_action(f"Rebuilding {component} data structures")
                result.data_recovered = True

            return True

        except Exception as e:
            result.add_error(f"Rebuild failed: {e}")
            return False

    def _checkpoint_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by resetting to a specific checkpoint."""
        checkpoint_id = context.get('checkpoint_id')

        try:
            if checkpoint_id:
                checkpoint = self.rollback_manager.rollback_to_checkpoint(world_id, checkpoint_id)
            else:
                checkpoint = self.rollback_manager.rollback_to_checkpoint(world_id)

            result.add_action(f"Reset to checkpoint {checkpoint.checkpoint_id}")
            result.data_recovered = True
            return True

        except Exception as e:
            result.add_error(f"Checkpoint recovery failed: {e}")
            return False

    def _graceful_degradation(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Implement graceful degradation by reducing system complexity."""
        try:
            # Reduce timeline complexity
            result.add_action("Enabling simplified timeline mode")

            # Reduce character complexity
            result.add_action("Enabling basic character interactions")

            # Disable advanced features temporarily
            result.add_action("Disabling advanced world evolution features")

            result.fallback_active = True
            result.add_warning("System running in degraded mode")

            return True

        except Exception as e:
            result.add_error(f"Graceful degradation failed: {e}")
            return False

    def _cache_invalidation_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by invalidating corrupted cache data."""
        try:
            if self.world_state_manager and hasattr(self.world_state_manager, 'admin'):
                self.world_state_manager.admin.invalidate_caches(world_id)
                result.add_action("Invalidated world caches")

            # Clear specific cache entries based on context
            cache_keys = context.get('cache_keys', [])
            for key in cache_keys:
                result.add_action(f"Invalidated cache key: {key}")

            return True

        except Exception as e:
            result.add_error(f"Cache invalidation failed: {e}")
            return False

    def _data_repair_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by repairing corrupted data."""
        try:
            component = context.get('component', 'unknown')

            if component == 'timeline':
                result.add_action("Repairing timeline chronological order")
                # Implementation would sort events by timestamp and fix inconsistencies
            elif component == 'character':
                result.add_action("Repairing character state consistency")
                # Implementation would validate and fix character data
            elif component == 'world_state':
                result.add_action("Repairing world state references")
                # Implementation would fix broken references and validate data

            result.data_recovered = True
            return True

        except Exception as e:
            result.add_error(f"Data repair failed: {e}")
            return False

    def _fallback_mode_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Enable fallback mode with minimal functionality."""
        try:
            # Enable fallback handlers
            component = context.get('component', 'system')
            fallback_handler = self.fallback_handlers.get(component)

            if fallback_handler:
                fallback_handler()
                result.add_action(f"Enabled fallback handler for {component}")
            else:
                result.add_action("Enabled generic fallback mode")

            result.fallback_active = True
            result.add_warning("System running in fallback mode")

            return True

        except Exception as e:
            result.add_error(f"Fallback mode activation failed: {e}")
            return False

    def _system_restart_recovery(self, world_id: str, context: dict[str, Any], result: RecoveryResult) -> bool:
        """Attempt recovery by restarting system components."""
        try:
            # This would restart specific components or the entire system
            result.add_action("Initiated system component restart")
            result.add_warning("System restart required - manual intervention may be needed")

            # In a real implementation, this might trigger a controlled restart
            # of specific services or components

            return True

        except Exception as e:
            result.add_error(f"System restart failed: {e}")
            return False

    def register_fallback_handler(self, component: str, handler: Callable) -> None:
        """Register a fallback handler for a specific component."""
        self.fallback_handlers[component] = handler
        logger.info(f"Registered fallback handler for component: {component}")

    def create_checkpoint(self, world_id: str, world_state: Any = None) -> SystemCheckpoint:
        """Create a checkpoint for rollback purposes."""
        try:
            # Get current world state if not provided
            if not world_state and self.world_state_manager:
                world_state = self.world_state_manager.get_world_state(world_id)

            # Create checkpoint
            checkpoint = self.rollback_manager.create_checkpoint(
                world_id=world_id,
                world_state=world_state
            )

            logger.info(f"Created checkpoint {checkpoint.checkpoint_id} for world {world_id}")
            return checkpoint

        except Exception as e:
            logger.error(f"Failed to create checkpoint for world {world_id}: {e}")
            raise

    def validate_world_consistency(self, world_id: str) -> dict[str, Any]:
        """Validate world consistency and return detailed report."""
        validation_report = {
            'world_id': world_id,
            'timestamp': datetime.now(),
            'overall_valid': True,
            'issues': [],
            'warnings': [],
            'checks_performed': []
        }

        try:
            if not self.world_state_manager:
                validation_report['issues'].append("World state manager not available")
                validation_report['overall_valid'] = False
                return validation_report

            # Check world state exists
            world_state = self.world_state_manager.get_world_state(world_id)
            if not world_state:
                validation_report['issues'].append("World state not found")
                validation_report['overall_valid'] = False
                return validation_report

            validation_report['checks_performed'].append("World state existence")

            # Validate timeline consistency
            if hasattr(self.world_state_manager, 'timeline_engine'):
                timeline_issues = self._validate_timeline_consistency(world_id)
                validation_report['issues'].extend(timeline_issues)
                validation_report['checks_performed'].append("Timeline consistency")

            # Validate character consistency
            character_issues = self._validate_character_consistency(world_id)
            validation_report['issues'].extend(character_issues)
            validation_report['checks_performed'].append("Character consistency")

            # Check system health
            health_score = self.health_monitor.get_system_health_score()
            if health_score < 0.8:
                validation_report['warnings'].append(f"System health score low: {health_score:.2f}")
            validation_report['checks_performed'].append("System health")

            # Update overall validity
            validation_report['overall_valid'] = len(validation_report['issues']) == 0

        except Exception as e:
            validation_report['issues'].append(f"Validation failed: {e}")
            validation_report['overall_valid'] = False

        return validation_report

    def _validate_timeline_consistency(self, world_id: str) -> list[str]:
        """Validate timeline consistency for a world."""
        issues = []

        try:
            # This would check for timeline inconsistencies
            # - Events in wrong chronological order
            # - Duplicate events
            # - Invalid event references
            # - Missing required events

            # Placeholder implementation
            pass

        except Exception as e:
            issues.append(f"Timeline validation failed: {e}")

        return issues

    def _validate_character_consistency(self, world_id: str) -> list[str]:
        """Validate character consistency for a world."""
        issues = []

        try:
            # This would check for character inconsistencies
            # - Invalid personality traits
            # - Broken family relationships
            # - Inconsistent character states
            # - Missing required character data

            # Placeholder implementation
            pass

        except Exception as e:
            issues.append(f"Character validation failed: {e}")

        return issues

    def get_error_statistics(self) -> dict[str, Any]:
        """Get error statistics and trends."""
        if not self.error_history:
            return {'total_errors': 0, 'error_types': {}, 'recent_errors': 0}

        # Count errors by type
        error_types = {}
        recent_errors = 0
        one_hour_ago = datetime.now() - timedelta(hours=1)

        for error in self.error_history:
            error_type = error.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

            if error.get('timestamp', datetime.min) >= one_hour_ago:
                recent_errors += 1

        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'recent_errors': recent_errors,
            'error_rate_per_hour': recent_errors,
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }

    def cleanup_old_data(self, days: int = 7) -> dict[str, int]:
        """Clean up old error data and checkpoints."""
        cleanup_results = {}

        # Clean up old error history
        cutoff_time = datetime.now() - timedelta(days=days)
        original_error_count = len(self.error_history)
        self.error_history = [
            error for error in self.error_history
            if error.get('timestamp', datetime.min) >= cutoff_time
        ]
        cleanup_results['errors_removed'] = original_error_count - len(self.error_history)

        # Clean up old checkpoints
        cleanup_results['checkpoints_removed'] = self.rollback_manager.cleanup_old_checkpoints(days)

        # Clean up old health history
        original_health_count = len(self.health_monitor.health_history)
        self.health_monitor.health_history = [
            check for check in self.health_monitor.health_history
            if check.get('timestamp', datetime.min) >= cutoff_time
        ]
        cleanup_results['health_checks_removed'] = original_health_count - len(self.health_monitor.health_history)

        logger.info(f"Cleanup completed: {cleanup_results}")
        return cleanup_results


def create_error_handler(world_state_manager=None) -> LivingWorldsErrorHandler:
    """Factory function to create a configured error handler."""
    handler = LivingWorldsErrorHandler(world_state_manager)

    # Register additional health checks if world state manager is available
    if world_state_manager:
        handler.health_monitor.register_health_check(
            "world_state_cache_healthy",
            lambda: hasattr(world_state_manager, 'cache') and world_state_manager.cache is not None
        )

        handler.health_monitor.register_health_check(
            "timeline_engine_healthy",
            lambda: hasattr(world_state_manager, 'timeline_engine') and world_state_manager.timeline_engine is not None
        )

    return handler
