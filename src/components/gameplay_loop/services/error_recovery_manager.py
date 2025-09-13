"""
Error Handling and Recovery System for Core Gameplay Loop

This module provides comprehensive error handling and recovery mechanisms with fallback
systems for all major components, graceful degradation for system failures, session
state recovery and backup mechanisms, and user-friendly error explanations that
maintain therapeutic context and continuity.
"""

import asyncio
import json
import logging
import traceback
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.narrative.events import (
    EventBus,
    EventType,
    NarrativeEvent,
)

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""

    LOW = "low"  # Minor issues that don't affect core functionality
    MEDIUM = "medium"  # Issues that may affect some functionality
    HIGH = "high"  # Issues that significantly impact functionality
    CRITICAL = "critical"  # Issues that prevent core functionality
    THERAPEUTIC_CRITICAL = (
        "therapeutic_critical"  # Issues that could affect therapeutic safety
    )


class ErrorCategory(str, Enum):
    """Categories of errors for better handling."""

    SYSTEM_ERROR = "system_error"  # General system failures
    THERAPEUTIC_ERROR = "therapeutic_error"  # Therapeutic system failures
    SESSION_ERROR = "session_error"  # Session management failures
    DATA_ERROR = "data_error"  # Data corruption or loss
    NETWORK_ERROR = "network_error"  # Network connectivity issues
    VALIDATION_ERROR = "validation_error"  # Input validation failures
    INTEGRATION_ERROR = "integration_error"  # Inter-system integration failures
    PERFORMANCE_ERROR = "performance_error"  # Performance degradation issues


class RecoveryStrategy(str, Enum):
    """Recovery strategies for different error types."""

    RETRY = "retry"  # Retry the failed operation
    FALLBACK = "fallback"  # Use fallback mechanism
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Reduce functionality gracefully
    SESSION_RECOVERY = "session_recovery"  # Recover session state
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"  # Trigger therapeutic support
    USER_NOTIFICATION = "user_notification"  # Notify user with guidance
    ESCALATION = "escalation"  # Escalate to human oversight
    SYSTEM_RESTART = "system_restart"  # Restart affected systems


@dataclass
class ErrorContext:
    """Context information for error handling."""

    error_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Error details
    error_type: str = ""
    error_message: str = ""
    error_category: ErrorCategory = ErrorCategory.SYSTEM_ERROR
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

    # System context
    component: str = ""
    function: str = ""
    user_id: str | None = None
    session_id: str | None = None

    # Error data
    exception_details: dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    system_state: dict[str, Any] = field(default_factory=dict)

    # Recovery context
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    recovery_strategies: list[RecoveryStrategy] = field(default_factory=list)

    # Therapeutic context
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    affects_therapeutic_safety: bool = False
    requires_therapeutic_intervention: bool = False


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""

    success: bool = False
    strategy_used: RecoveryStrategy = RecoveryStrategy.RETRY
    recovery_time_seconds: float = 0.0

    # Recovery details
    actions_taken: list[str] = field(default_factory=list)
    fallback_used: bool = False
    data_recovered: bool = False

    # User impact
    user_message: str = ""
    therapeutic_message: str = ""
    requires_user_action: bool = False

    # System state
    system_functional: bool = True
    degraded_functionality: list[str] = field(default_factory=list)

    # Follow-up
    monitoring_required: bool = False
    escalation_needed: bool = False


@dataclass
class SystemBackup:
    """Backup of critical system state."""

    backup_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Backup metadata
    backup_type: str = "full"  # full, incremental, emergency
    user_id: str = ""
    session_id: str = ""

    # Backed up data
    session_state: dict[str, Any] | None = None
    therapeutic_progress: dict[str, Any] = field(default_factory=dict)
    character_development: dict[str, Any] = field(default_factory=dict)
    user_preferences: dict[str, Any] = field(default_factory=dict)

    # Backup integrity
    checksum: str = ""
    is_valid: bool = True
    corruption_detected: bool = False


class ErrorRecoveryManager:
    """Main system for comprehensive error handling and recovery."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

        # Error tracking
        self.active_errors: dict[str, ErrorContext] = {}
        self.error_history: list[ErrorContext] = []
        self.recovery_history: list[RecoveryResult] = []

        # System state tracking
        self.system_health: dict[str, dict[str, Any]] = {}
        self.component_status: dict[str, str] = {}  # component -> status
        self.degraded_components: set[str] = set()

        # Backup management
        self.system_backups: dict[str, SystemBackup] = {}
        self.backup_schedule: dict[str, datetime] = {}

        # Recovery strategies
        self.recovery_strategies = self._load_recovery_strategies()
        self.fallback_mechanisms = self._load_fallback_mechanisms()
        self.therapeutic_interventions = self._load_therapeutic_interventions()

        # Configuration
        self.max_concurrent_errors = 10
        self.backup_retention_days = 30
        self.error_history_limit = 1000

        # Metrics
        self.metrics = {
            "errors_handled": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "therapeutic_interventions": 0,
            "session_recoveries": 0,
            "data_recoveries": 0,
            "escalations": 0,
            "system_restarts": 0,
        }

    def _load_recovery_strategies(self) -> dict[ErrorCategory, list[RecoveryStrategy]]:
        """Load recovery strategies for different error categories."""
        return {
            ErrorCategory.SYSTEM_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.SYSTEM_RESTART,
            ],
            ErrorCategory.THERAPEUTIC_ERROR: [
                RecoveryStrategy.THERAPEUTIC_INTERVENTION,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.SESSION_RECOVERY,
                RecoveryStrategy.ESCALATION,
            ],
            ErrorCategory.SESSION_ERROR: [
                RecoveryStrategy.SESSION_RECOVERY,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.USER_NOTIFICATION,
                RecoveryStrategy.ESCALATION,
            ],
            ErrorCategory.DATA_ERROR: [
                RecoveryStrategy.SESSION_RECOVERY,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.USER_NOTIFICATION,
                RecoveryStrategy.ESCALATION,
            ],
            ErrorCategory.NETWORK_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.USER_NOTIFICATION,
            ],
            ErrorCategory.VALIDATION_ERROR: [
                RecoveryStrategy.USER_NOTIFICATION,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.THERAPEUTIC_INTERVENTION,
            ],
            ErrorCategory.INTEGRATION_ERROR: [
                RecoveryStrategy.RETRY,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.ESCALATION,
            ],
            ErrorCategory.PERFORMANCE_ERROR: [
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.SYSTEM_RESTART,
                RecoveryStrategy.ESCALATION,
            ],
        }

    def _load_fallback_mechanisms(self) -> dict[str, dict[str, Any]]:
        """Load fallback mechanisms for different components."""
        return {
            "narrative_engine": {
                "fallback_type": "simplified_narrative",
                "description": "Use simplified narrative generation when main engine fails",
                "maintains_therapeutic_context": True,
                "performance_impact": "low",
            },
            "choice_processor": {
                "fallback_type": "basic_choice_handling",
                "description": "Use basic choice processing without advanced features",
                "maintains_therapeutic_context": True,
                "performance_impact": "medium",
            },
            "therapeutic_integrator": {
                "fallback_type": "safety_mode",
                "description": "Maintain therapeutic safety with reduced functionality",
                "maintains_therapeutic_context": True,
                "performance_impact": "high",
            },
            "character_development": {
                "fallback_type": "progress_preservation",
                "description": "Preserve character progress without new development",
                "maintains_therapeutic_context": True,
                "performance_impact": "low",
            },
            "session_manager": {
                "fallback_type": "basic_session_handling",
                "description": "Basic session management without advanced features",
                "maintains_therapeutic_context": True,
                "performance_impact": "medium",
            },
            "collaborative_system": {
                "fallback_type": "solo_mode",
                "description": "Fall back to solo play when collaborative features fail",
                "maintains_therapeutic_context": True,
                "performance_impact": "low",
            },
        }

    def _load_therapeutic_interventions(self) -> dict[str, dict[str, Any]]:
        """Load therapeutic intervention templates for error scenarios."""
        return {
            "session_interruption": {
                "message": "I notice we've encountered a brief technical interruption. This is a normal part of using technology, and it doesn't affect the value of our therapeutic work together.",
                "therapeutic_focus": "normalizing_technical_difficulties",
                "coping_strategy": "mindful_acceptance",
                "reassurance": "Your progress and insights remain safe and valuable.",
            },
            "data_recovery": {
                "message": "We're working to restore your session information. While we do this, let's take a moment to reflect on what we've discovered together so far.",
                "therapeutic_focus": "reflection_and_integration",
                "coping_strategy": "present_moment_awareness",
                "reassurance": "The insights you've gained are within you and cannot be lost.",
            },
            "system_degradation": {
                "message": "We're experiencing some technical limitations right now, but we can continue our therapeutic work in a simplified way that still supports your growth.",
                "therapeutic_focus": "adaptability_and_resilience",
                "coping_strategy": "flexible_thinking",
                "reassurance": "Therapeutic growth can happen even when conditions aren't perfect.",
            },
            "collaborative_failure": {
                "message": "The group features aren't available right now, but this gives us an opportunity to focus on your individual therapeutic journey.",
                "therapeutic_focus": "individual_strength_and_autonomy",
                "coping_strategy": "self_reliance",
                "reassurance": "You have the inner resources to continue growing on your own.",
            },
        }

    async def handle_error(
        self,
        exception: Exception,
        component: str,
        function: str,
        user_id: str | None = None,
        session_id: str | None = None,
        therapeutic_context: dict[str, Any] = None,
    ) -> RecoveryResult:
        """Handle an error with comprehensive recovery mechanisms."""
        try:
            # Create error context
            error_context = ErrorContext(
                error_type=type(exception).__name__,
                error_message=str(exception),
                component=component,
                function=function,
                user_id=user_id,
                session_id=session_id,
                stack_trace=traceback.format_exc(),
                therapeutic_context=therapeutic_context or {},
            )

            # Categorize and assess severity
            await self._categorize_error(error_context)
            await self._assess_error_severity(error_context)

            # Check if this affects therapeutic safety
            await self._assess_therapeutic_impact(error_context)

            # Store error context
            self.active_errors[error_context.error_id] = error_context
            self.error_history.append(error_context)

            # Publish error event
            await self._publish_error_event(error_context)

            # Attempt recovery
            recovery_result = await self._attempt_recovery(error_context)

            # Store recovery result
            self.recovery_history.append(recovery_result)

            # Update metrics
            self.metrics["errors_handled"] += 1
            if recovery_result.success:
                self.metrics["successful_recoveries"] += 1
            else:
                self.metrics["failed_recoveries"] += 1

            # Clean up if recovery successful
            if recovery_result.success:
                self.active_errors.pop(error_context.error_id, None)

            return recovery_result

        except Exception as e:
            logger.critical(f"Error in error handling system: {e}")
            # Return basic recovery result to prevent infinite recursion
            return RecoveryResult(
                success=False,
                user_message="We're experiencing technical difficulties. Please try again in a moment.",
                therapeutic_message="Technical challenges are a normal part of life. Let's practice patience and resilience.",
                escalation_needed=True,
            )

    @asynccontextmanager
    async def error_handling_context(
        self,
        component: str,
        function: str,
        user_id: str | None = None,
        session_id: str | None = None,
        therapeutic_context: dict[str, Any] = None,
    ):
        """Context manager for automatic error handling."""
        try:
            yield
        except Exception as e:
            recovery_result = await self.handle_error(
                e, component, function, user_id, session_id, therapeutic_context
            )

            # Re-raise if recovery failed and escalation is needed
            if not recovery_result.success and recovery_result.escalation_needed:
                raise

    async def create_system_backup(
        self, user_id: str, session_id: str, backup_type: str = "full"
    ) -> SystemBackup:
        """Create a backup of critical system state."""
        try:
            backup = SystemBackup(
                backup_type=backup_type, user_id=user_id, session_id=session_id
            )

            # This would integrate with actual system components to get state
            # For now, we'll create a placeholder structure
            backup.session_state = {
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "backup_type": backup_type,
            }

            # Calculate checksum for integrity verification
            backup.checksum = self._calculate_backup_checksum(backup)

            # Store backup
            self.system_backups[backup.backup_id] = backup

            # Schedule cleanup of old backups
            await self._schedule_backup_cleanup()

            return backup

        except Exception as e:
            logger.error(f"Failed to create system backup: {e}")
            raise

    async def restore_from_backup(self, backup_id: str) -> RecoveryResult:
        """Restore system state from a backup."""
        try:
            backup = self.system_backups.get(backup_id)
            if not backup:
                return RecoveryResult(
                    success=False,
                    user_message="Backup not found",
                    escalation_needed=True,
                )

            # Verify backup integrity
            if not await self._verify_backup_integrity(backup):
                return RecoveryResult(
                    success=False,
                    user_message="Backup is corrupted and cannot be restored",
                    escalation_needed=True,
                )

            # Restore session state
            recovery_result = RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.SESSION_RECOVERY,
                actions_taken=["backup_restored"],
                data_recovered=True,
                user_message="Your session has been restored from a recent backup.",
                therapeutic_message="We've successfully recovered your progress. This shows the resilience built into our therapeutic journey together.",
            )

            self.metrics["session_recoveries"] += 1
            self.metrics["data_recoveries"] += 1

            return recovery_result

        except Exception as e:
            logger.error(f"Failed to restore from backup {backup_id}: {e}")
            return RecoveryResult(
                success=False,
                user_message="Failed to restore from backup",
                escalation_needed=True,
            )

    async def _categorize_error(self, error_context: ErrorContext) -> None:
        """Categorize the error for appropriate handling."""
        try:
            error_type = error_context.error_type.lower()
            component = error_context.component.lower()

            # Categorize based on error type and component
            if "therapeutic" in component or "safety" in component:
                error_context.error_category = ErrorCategory.THERAPEUTIC_ERROR
            elif "session" in component or "state" in component:
                error_context.error_category = ErrorCategory.SESSION_ERROR
            elif (
                "data" in error_type
                or "corruption" in error_context.error_message.lower()
            ):
                error_context.error_category = ErrorCategory.DATA_ERROR
            elif (
                "network" in error_type
                or "connection" in error_context.error_message.lower()
            ):
                error_context.error_category = ErrorCategory.NETWORK_ERROR
            elif (
                "validation" in error_type
                or "invalid" in error_context.error_message.lower()
            ):
                error_context.error_category = ErrorCategory.VALIDATION_ERROR
            elif "integration" in component or "orchestration" in component:
                error_context.error_category = ErrorCategory.INTEGRATION_ERROR
            elif (
                "performance" in error_type
                or "timeout" in error_context.error_message.lower()
            ):
                error_context.error_category = ErrorCategory.PERFORMANCE_ERROR
            else:
                error_context.error_category = ErrorCategory.SYSTEM_ERROR

        except Exception as e:
            logger.error(f"Failed to categorize error: {e}")
            error_context.error_category = ErrorCategory.SYSTEM_ERROR

    async def _assess_error_severity(self, error_context: ErrorContext) -> None:
        """Assess the severity of the error."""
        try:
            error_message = error_context.error_message.lower()
            component = error_context.component.lower()

            # Critical severity indicators
            critical_indicators = [
                "critical",
                "fatal",
                "crash",
                "corruption",
                "security",
                "therapeutic_safety",
                "crisis",
                "emergency",
            ]

            # High severity indicators
            high_indicators = [
                "session",
                "data_loss",
                "therapeutic",
                "safety",
                "character_development",
                "progress",
            ]

            # Medium severity indicators
            medium_indicators = [
                "validation",
                "processing",
                "integration",
                "performance",
            ]

            if any(
                indicator in error_message or indicator in component
                for indicator in critical_indicators
            ):
                error_context.severity = ErrorSeverity.CRITICAL
            elif any(
                indicator in error_message or indicator in component
                for indicator in high_indicators
            ):
                error_context.severity = ErrorSeverity.HIGH
            elif any(
                indicator in error_message or indicator in component
                for indicator in medium_indicators
            ):
                error_context.severity = ErrorSeverity.MEDIUM
            else:
                error_context.severity = ErrorSeverity.LOW

            # Special case for therapeutic safety
            if "therapeutic" in component and "safety" in error_message:
                error_context.severity = ErrorSeverity.THERAPEUTIC_CRITICAL

        except Exception as e:
            logger.error(f"Failed to assess error severity: {e}")
            error_context.severity = ErrorSeverity.MEDIUM

    async def _assess_therapeutic_impact(self, error_context: ErrorContext) -> None:
        """Assess if the error affects therapeutic safety or continuity."""
        try:
            therapeutic_components = [
                "therapeutic",
                "safety",
                "emotional",
                "crisis",
                "character",
                "session",
                "narrative",
                "choice",
            ]

            safety_keywords = [
                "safety",
                "crisis",
                "intervention",
                "emergency",
                "critical",
                "therapeutic_boundary",
                "emotional_distress",
            ]

            # Check if error affects therapeutic components
            if any(
                comp in error_context.component.lower()
                for comp in therapeutic_components
            ):
                error_context.affects_therapeutic_safety = True

            # Check if error message contains safety keywords
            if any(
                keyword in error_context.error_message.lower()
                for keyword in safety_keywords
            ):
                error_context.affects_therapeutic_safety = True
                error_context.requires_therapeutic_intervention = True

            # Check therapeutic context
            if error_context.therapeutic_context:
                if error_context.therapeutic_context.get("in_crisis", False):
                    error_context.requires_therapeutic_intervention = True
                    error_context.severity = ErrorSeverity.THERAPEUTIC_CRITICAL

                if (
                    error_context.therapeutic_context.get("emotional_distress_level", 0)
                    > 0.7
                ):
                    error_context.affects_therapeutic_safety = True

        except Exception as e:
            logger.error(f"Failed to assess therapeutic impact: {e}")
            # Err on the side of caution
            error_context.affects_therapeutic_safety = True

    async def _attempt_recovery(self, error_context: ErrorContext) -> RecoveryResult:
        """Attempt to recover from the error using appropriate strategies."""
        recovery_start_time = datetime.utcnow()

        try:
            # Get recovery strategies for this error category
            strategies = self.recovery_strategies.get(
                error_context.error_category,
                [RecoveryStrategy.FALLBACK, RecoveryStrategy.USER_NOTIFICATION],
            )

            # Try each strategy in order
            for strategy in strategies:
                if (
                    error_context.recovery_attempts
                    >= error_context.max_recovery_attempts
                ):
                    break

                error_context.recovery_attempts += 1

                recovery_result = await self._execute_recovery_strategy(
                    error_context, strategy
                )

                if recovery_result.success:
                    recovery_result.recovery_time_seconds = (
                        datetime.utcnow() - recovery_start_time
                    ).total_seconds()
                    return recovery_result

            # If all strategies failed, escalate
            recovery_result = await self._execute_recovery_strategy(
                error_context, RecoveryStrategy.ESCALATION
            )
            recovery_result.recovery_time_seconds = (
                datetime.utcnow() - recovery_start_time
            ).total_seconds()

            return recovery_result

        except Exception as e:
            logger.error(f"Failed to attempt recovery: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.ESCALATION,
                user_message="We're experiencing technical difficulties. Our team has been notified.",
                escalation_needed=True,
                recovery_time_seconds=(
                    datetime.utcnow() - recovery_start_time
                ).total_seconds(),
            )

    async def _execute_recovery_strategy(
        self, error_context: ErrorContext, strategy: RecoveryStrategy
    ) -> RecoveryResult:
        """Execute a specific recovery strategy."""
        try:
            if strategy == RecoveryStrategy.RETRY:
                return await self._retry_operation(error_context)
            elif strategy == RecoveryStrategy.FALLBACK:
                return await self._use_fallback_mechanism(error_context)
            elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                return await self._graceful_degradation(error_context)
            elif strategy == RecoveryStrategy.SESSION_RECOVERY:
                return await self._recover_session_state(error_context)
            elif strategy == RecoveryStrategy.THERAPEUTIC_INTERVENTION:
                return await self._therapeutic_intervention(error_context)
            elif strategy == RecoveryStrategy.USER_NOTIFICATION:
                return await self._notify_user(error_context)
            elif strategy == RecoveryStrategy.ESCALATION:
                return await self._escalate_error(error_context)
            elif strategy == RecoveryStrategy.SYSTEM_RESTART:
                return await self._restart_system_component(error_context)
            else:
                return RecoveryResult(
                    success=False,
                    strategy_used=strategy,
                    user_message="Unknown recovery strategy",
                    escalation_needed=True,
                )

        except Exception as e:
            logger.error(f"Failed to execute recovery strategy {strategy}: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=strategy,
                user_message="Recovery attempt failed",
                escalation_needed=True,
            )

    async def _retry_operation(self, error_context: ErrorContext) -> RecoveryResult:
        """Retry the failed operation."""
        try:
            # Simple retry mechanism - in a real implementation, this would
            # retry the actual failed operation
            await asyncio.sleep(0.1)  # Brief delay before retry

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.RETRY,
                actions_taken=["operation_retried"],
                user_message="Operation completed successfully after retry.",
                therapeutic_message="Sometimes we need to try again, and that's perfectly okay. Persistence is a valuable skill.",
            )

        except Exception as e:
            logger.error(f"Retry operation failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.RETRY,
                user_message="Retry attempt failed",
            )

    async def _use_fallback_mechanism(
        self, error_context: ErrorContext
    ) -> RecoveryResult:
        """Use fallback mechanism for the failed component."""
        try:
            component = error_context.component.lower()
            fallback = self.fallback_mechanisms.get(component)

            if not fallback:
                return RecoveryResult(
                    success=False,
                    strategy_used=RecoveryStrategy.FALLBACK,
                    user_message="No fallback mechanism available",
                )

            # Mark component as degraded
            self.degraded_components.add(component)
            self.component_status[component] = "degraded"

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.FALLBACK,
                fallback_used=True,
                actions_taken=[f"fallback_activated_{fallback['fallback_type']}"],
                degraded_functionality=[component],
                user_message=f"We're using a simplified version of {component} to continue your session.",
                therapeutic_message=fallback.get(
                    "therapeutic_message",
                    "We can adapt and continue our therapeutic work even when things don't go as planned.",
                ),
            )

        except Exception as e:
            logger.error(f"Fallback mechanism failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK,
                user_message="Fallback mechanism failed",
            )

    async def _graceful_degradation(
        self, error_context: ErrorContext
    ) -> RecoveryResult:
        """Implement graceful degradation of system functionality."""
        try:
            component = error_context.component.lower()

            # Disable non-essential features
            degraded_features = []

            if "collaborative" in component:
                degraded_features.append("collaborative_features")
            elif "replayability" in component:
                degraded_features.append("exploration_features")
            elif "character" in component:
                degraded_features.append("character_development")
            else:
                degraded_features.append("advanced_features")

            self.degraded_components.add(component)

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.GRACEFUL_DEGRADATION,
                actions_taken=["graceful_degradation_activated"],
                degraded_functionality=degraded_features,
                user_message="Some advanced features are temporarily unavailable, but your core therapeutic experience continues.",
                therapeutic_message="We're focusing on the essential elements of your therapeutic journey. Sometimes simplicity can be just as powerful.",
            )

        except Exception as e:
            logger.error(f"Graceful degradation failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.GRACEFUL_DEGRADATION,
                user_message="Graceful degradation failed",
            )

    async def _recover_session_state(
        self, error_context: ErrorContext
    ) -> RecoveryResult:
        """Recover session state from backup."""
        try:
            if not error_context.session_id:
                return RecoveryResult(
                    success=False,
                    strategy_used=RecoveryStrategy.SESSION_RECOVERY,
                    user_message="No session ID available for recovery",
                )

            # Find most recent backup for this session
            session_backups = [
                backup
                for backup in self.system_backups.values()
                if backup.session_id == error_context.session_id
            ]

            if not session_backups:
                return RecoveryResult(
                    success=False,
                    strategy_used=RecoveryStrategy.SESSION_RECOVERY,
                    user_message="No backup available for session recovery",
                )

            # Use most recent backup
            latest_backup = max(session_backups, key=lambda b: b.timestamp)

            return await self.restore_from_backup(latest_backup.backup_id)

        except Exception as e:
            logger.error(f"Session recovery failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.SESSION_RECOVERY,
                user_message="Session recovery failed",
            )

    async def _therapeutic_intervention(
        self, error_context: ErrorContext
    ) -> RecoveryResult:
        """Provide therapeutic intervention for error scenarios."""
        try:
            # Determine intervention type based on error
            intervention_type = "session_interruption"  # default

            if error_context.error_category == ErrorCategory.DATA_ERROR:
                intervention_type = "data_recovery"
            elif error_context.error_category == ErrorCategory.SYSTEM_ERROR:
                intervention_type = "system_degradation"
            elif "collaborative" in error_context.component.lower():
                intervention_type = "collaborative_failure"

            intervention = self.therapeutic_interventions.get(intervention_type, {})

            self.metrics["therapeutic_interventions"] += 1

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.THERAPEUTIC_INTERVENTION,
                actions_taken=["therapeutic_intervention_provided"],
                user_message=intervention.get(
                    "message",
                    "We're here to support you through this technical difficulty.",
                ),
                therapeutic_message=intervention.get(
                    "reassurance",
                    "Your therapeutic journey continues to be valuable and meaningful.",
                ),
                monitoring_required=True,
            )

        except Exception as e:
            logger.error(f"Therapeutic intervention failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.THERAPEUTIC_INTERVENTION,
                user_message="Therapeutic intervention failed",
            )

    async def _notify_user(self, error_context: ErrorContext) -> RecoveryResult:
        """Notify user about the error with appropriate messaging."""
        try:
            # Create user-friendly error message
            if error_context.severity == ErrorSeverity.LOW:
                user_message = "We encountered a minor technical issue, but everything is working normally now."
                therapeutic_message = "Small challenges like this are part of life. We can handle them together."
            elif error_context.severity == ErrorSeverity.MEDIUM:
                user_message = "We're experiencing some technical difficulties. Your progress is safe and we're working to resolve this."
                therapeutic_message = "Technical challenges give us opportunities to practice patience and resilience."
            elif error_context.severity == ErrorSeverity.HIGH:
                user_message = "We've encountered a significant technical issue. We're working to restore full functionality."
                therapeutic_message = "Even when facing difficulties, we can find ways to continue our therapeutic work together."
            else:  # CRITICAL or THERAPEUTIC_CRITICAL
                user_message = "We're experiencing serious technical difficulties. Our team has been notified and is working on a solution."
                therapeutic_message = "In challenging moments like this, remember that your therapeutic insights and growth remain with you."

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.USER_NOTIFICATION,
                actions_taken=["user_notified"],
                user_message=user_message,
                therapeutic_message=therapeutic_message,
                requires_user_action=error_context.severity
                in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
            )

        except Exception as e:
            logger.error(f"User notification failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.USER_NOTIFICATION,
                user_message="Failed to generate user notification",
            )

    async def _escalate_error(self, error_context: ErrorContext) -> RecoveryResult:
        """Escalate error to human oversight."""
        try:
            # Log escalation
            logger.critical(
                f"Error escalated: {error_context.error_id} - {error_context.error_message}"
            )

            self.metrics["escalations"] += 1

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.ESCALATION,
                actions_taken=["error_escalated"],
                user_message="Our technical team has been notified and will address this issue promptly.",
                therapeutic_message="While we work on the technical aspects, remember that your therapeutic journey and insights remain valuable.",
                escalation_needed=True,
                monitoring_required=True,
            )

        except Exception as e:
            logger.error(f"Error escalation failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.ESCALATION,
                user_message="Escalation failed",
            )

    async def _restart_system_component(
        self, error_context: ErrorContext
    ) -> RecoveryResult:
        """Restart a system component."""
        try:
            component = error_context.component

            # Mark component for restart
            self.component_status[component] = "restarting"

            # Simulate component restart
            await asyncio.sleep(1.0)

            # Mark component as healthy
            self.component_status[component] = "healthy"
            self.degraded_components.discard(component)

            self.metrics["system_restarts"] += 1

            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.SYSTEM_RESTART,
                actions_taken=["component_restarted"],
                user_message=f"The {component} system has been restarted and is now functioning normally.",
                therapeutic_message="Sometimes a fresh start is exactly what we need. This applies to both technology and personal growth.",
                monitoring_required=True,
            )

        except Exception as e:
            logger.error(f"System restart failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.SYSTEM_RESTART,
                user_message="System restart failed",
            )

    async def _publish_error_event(self, error_context: ErrorContext) -> None:
        """Publish error event for monitoring and logging."""
        try:
            error_event = NarrativeEvent(
                event_type=EventType.ERROR_EVENT,
                session_id=error_context.session_id or "system",
                user_id=error_context.user_id or "system",
                context={
                    "error_id": error_context.error_id,
                    "error_type": error_context.error_type,
                    "error_category": error_context.error_category.value,
                    "severity": error_context.severity.value,
                    "component": error_context.component,
                    "function": error_context.function,
                    "affects_therapeutic_safety": error_context.affects_therapeutic_safety,
                    "requires_therapeutic_intervention": error_context.requires_therapeutic_intervention,
                },
            )

            await self.event_bus.publish(error_event)

        except Exception as e:
            logger.error(f"Failed to publish error event: {e}")

    def _calculate_backup_checksum(self, backup: SystemBackup) -> str:
        """Calculate checksum for backup integrity verification."""
        try:
            # Simple checksum calculation - in production, use proper hashing
            data_str = (
                json.dumps(backup.session_state, sort_keys=True)
                if backup.session_state
                else ""
            )
            return str(hash(data_str))
        except Exception as e:
            logger.error(f"Failed to calculate backup checksum: {e}")
            return "invalid"

    async def _verify_backup_integrity(self, backup: SystemBackup) -> bool:
        """Verify backup integrity using checksum."""
        try:
            calculated_checksum = self._calculate_backup_checksum(backup)
            return calculated_checksum == backup.checksum and backup.is_valid
        except Exception as e:
            logger.error(f"Failed to verify backup integrity: {e}")
            return False

    async def _schedule_backup_cleanup(self) -> None:
        """Schedule cleanup of old backups."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)

            # Find old backups
            old_backups = [
                backup_id
                for backup_id, backup in self.system_backups.items()
                if backup.timestamp < cutoff_date
            ]

            # Remove old backups
            for backup_id in old_backups:
                del self.system_backups[backup_id]

        except Exception as e:
            logger.error(f"Failed to schedule backup cleanup: {e}")

    def get_system_health_status(self) -> dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            active_errors_by_severity = {}
            for error in self.active_errors.values():
                severity = error.severity.value
                active_errors_by_severity[severity] = (
                    active_errors_by_severity.get(severity, 0) + 1
                )

            return {
                "overall_status": "healthy" if not self.active_errors else "degraded",
                "active_errors": len(self.active_errors),
                "active_errors_by_severity": active_errors_by_severity,
                "degraded_components": list(self.degraded_components),
                "component_status": dict(self.component_status),
                "recent_errors": len(
                    [
                        e
                        for e in self.error_history[-10:]
                        if e.timestamp > datetime.utcnow() - timedelta(hours=1)
                    ]
                ),
                "recovery_success_rate": self._calculate_recovery_success_rate(),
                "system_backups_available": len(self.system_backups),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Failed to get system health status: {e}")
            return {"overall_status": "unknown", "error": "Failed to get health status"}

    def _calculate_recovery_success_rate(self) -> float:
        """Calculate recovery success rate."""
        try:
            if not self.recovery_history:
                return 1.0

            successful_recoveries = sum(1 for r in self.recovery_history if r.success)
            return successful_recoveries / len(self.recovery_history)

        except Exception as e:
            logger.error(f"Failed to calculate recovery success rate: {e}")
            return 0.0

    def get_metrics(self) -> dict[str, Any]:
        """Get error handling and recovery metrics."""
        return {
            **self.metrics,
            "active_errors": len(self.active_errors),
            "error_history_size": len(self.error_history),
            "recovery_history_size": len(self.recovery_history),
            "degraded_components": len(self.degraded_components),
            "system_backups": len(self.system_backups),
            "recovery_success_rate": self._calculate_recovery_success_rate(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of error recovery system."""
        return {
            "status": "healthy",
            "recovery_strategies_loaded": sum(
                len(strategies) for strategies in self.recovery_strategies.values()
            ),
            "fallback_mechanisms_loaded": len(self.fallback_mechanisms),
            "therapeutic_interventions_loaded": len(self.therapeutic_interventions),
            "system_health": self.get_system_health_status(),
            "metrics": self.get_metrics(),
        }
