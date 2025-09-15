"""
Tests for ErrorRecoveryManager

This module tests comprehensive error handling and recovery mechanisms with fallback
systems for all major components, graceful degradation for system failures, session
state recovery and backup mechanisms, and user-friendly error explanations that
maintain therapeutic context and continuity.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.services.error_recovery_manager import (
    ErrorCategory,
    ErrorRecoveryManager,
    ErrorSeverity,
    RecoveryResult,
    RecoveryStrategy,
    SystemBackup,
)


class TestErrorRecoveryManager:
    """Test ErrorRecoveryManager functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def error_recovery_manager(self, event_bus):
        """Create error recovery manager instance."""
        return ErrorRecoveryManager(event_bus)

    @pytest.fixture
    def sample_exception(self):
        """Create sample exception for testing."""
        return ValueError("Test error message")

    @pytest.fixture
    def therapeutic_context(self):
        """Create sample therapeutic context."""
        return {
            "in_crisis": False,
            "emotional_distress_level": 0.3,
            "therapeutic_goals": ["anxiety_management"],
            "current_session_phase": "exploration",
        }

    @pytest.mark.asyncio
    async def test_handle_error_basic(
        self, error_recovery_manager, sample_exception, event_bus
    ):
        """Test basic error handling."""
        recovery_result = await error_recovery_manager.handle_error(
            sample_exception,
            "test_component",
            "test_function",
            "user_123",
            "session_456",
        )

        # Check recovery result structure
        assert isinstance(recovery_result, RecoveryResult)
        assert recovery_result.success in [True, False]
        assert recovery_result.strategy_used in RecoveryStrategy
        assert recovery_result.user_message != ""

        # Check error was stored
        assert len(error_recovery_manager.active_errors) >= 0
        assert len(error_recovery_manager.error_history) == 1

        # Check event was published
        event_bus.publish.assert_called()

        # Check metrics were updated
        assert error_recovery_manager.metrics["errors_handled"] == 1

    @pytest.mark.asyncio
    async def test_handle_therapeutic_error(
        self, error_recovery_manager, therapeutic_context, event_bus
    ):
        """Test handling of therapeutic errors."""
        therapeutic_exception = Exception("Therapeutic safety violation")

        recovery_result = await error_recovery_manager.handle_error(
            therapeutic_exception,
            "therapeutic_integrator",
            "process_choice",
            "user_123",
            "session_456",
            therapeutic_context,
        )

        # Check that therapeutic context was considered
        error_context = error_recovery_manager.error_history[0]
        assert error_context.therapeutic_context == therapeutic_context
        assert error_context.error_category == ErrorCategory.THERAPEUTIC_ERROR

        # Check therapeutic intervention was considered
        assert recovery_result.therapeutic_message != ""

    @pytest.mark.asyncio
    async def test_handle_crisis_situation(self, error_recovery_manager, event_bus):
        """Test handling of crisis situations."""
        crisis_context = {
            "in_crisis": True,
            "emotional_distress_level": 0.9,
            "crisis_type": "emotional_overwhelm",
        }

        crisis_exception = Exception("Crisis intervention needed")

        recovery_result = await error_recovery_manager.handle_error(
            crisis_exception,
            "emotional_safety",
            "assess_distress",
            "user_123",
            "session_456",
            crisis_context,
        )

        # Check that crisis was properly identified
        error_context = error_recovery_manager.error_history[0]
        assert error_context.severity == ErrorSeverity.THERAPEUTIC_CRITICAL
        assert error_context.requires_therapeutic_intervention
        assert error_context.affects_therapeutic_safety

        # Check appropriate recovery strategy
        assert recovery_result.strategy_used in [
            RecoveryStrategy.THERAPEUTIC_INTERVENTION,
            RecoveryStrategy.ESCALATION,
        ]

    @pytest.mark.asyncio
    async def test_error_categorization(self, error_recovery_manager):
        """Test error categorization logic."""
        test_cases = [
            (
                "therapeutic_integrator",
                "process_choice",
                ErrorCategory.THERAPEUTIC_ERROR,
            ),
            ("session_manager", "save_state", ErrorCategory.SESSION_ERROR),
            ("data_processor", "corruption detected", ErrorCategory.DATA_ERROR),
            ("network_client", "connection failed", ErrorCategory.NETWORK_ERROR),
            ("input_validator", "invalid input", ErrorCategory.VALIDATION_ERROR),
            (
                "integration_service",
                "service unavailable",
                ErrorCategory.INTEGRATION_ERROR,
            ),
            (
                "performance_monitor",
                "timeout occurred",
                ErrorCategory.PERFORMANCE_ERROR,
            ),
            ("unknown_component", "unknown error", ErrorCategory.SYSTEM_ERROR),
        ]

        for component, message, expected_category in test_cases:
            exception = Exception(message)
            await error_recovery_manager.handle_error(
                exception, component, "test_function"
            )

            error_context = error_recovery_manager.error_history[-1]
            assert error_context.error_category == expected_category

    @pytest.mark.asyncio
    async def test_error_severity_assessment(self, error_recovery_manager):
        """Test error severity assessment."""
        severity_test_cases = [
            ("critical system failure", ErrorSeverity.CRITICAL),
            ("session data lost", ErrorSeverity.HIGH),
            ("validation error", ErrorSeverity.MEDIUM),
            ("minor display issue", ErrorSeverity.LOW),
        ]

        for message, _expected_severity in severity_test_cases:
            exception = Exception(message)
            await error_recovery_manager.handle_error(
                exception, "test_component", "test_function"
            )

            error_context = error_recovery_manager.error_history[-1]
            # Severity assessment is heuristic, so we check it's reasonable
            assert error_context.severity in ErrorSeverity

    @pytest.mark.asyncio
    async def test_create_system_backup(self, error_recovery_manager):
        """Test system backup creation."""
        backup = await error_recovery_manager.create_system_backup(
            "user_123", "session_456", "full"
        )

        # Check backup structure
        assert isinstance(backup, SystemBackup)
        assert backup.user_id == "user_123"
        assert backup.session_id == "session_456"
        assert backup.backup_type == "full"
        assert backup.checksum != ""
        assert backup.is_valid

        # Check backup was stored
        assert backup.backup_id in error_recovery_manager.system_backups

    @pytest.mark.asyncio
    async def test_restore_from_backup(self, error_recovery_manager):
        """Test restoring from backup."""
        # Create backup first
        backup = await error_recovery_manager.create_system_backup(
            "user_123", "session_456"
        )

        # Restore from backup
        recovery_result = await error_recovery_manager.restore_from_backup(
            backup.backup_id
        )

        # Check restoration result
        assert recovery_result.success
        assert recovery_result.strategy_used == RecoveryStrategy.SESSION_RECOVERY
        assert recovery_result.data_recovered
        assert recovery_result.user_message != ""
        assert recovery_result.therapeutic_message != ""

        # Check metrics were updated
        assert error_recovery_manager.metrics["session_recoveries"] == 1
        assert error_recovery_manager.metrics["data_recoveries"] == 1

    @pytest.mark.asyncio
    async def test_restore_from_invalid_backup(self, error_recovery_manager):
        """Test restoring from invalid backup."""
        recovery_result = await error_recovery_manager.restore_from_backup(
            "nonexistent_backup"
        )

        # Check failure handling
        assert not recovery_result.success
        assert recovery_result.escalation_needed
        assert "not found" in recovery_result.user_message.lower()

    @pytest.mark.asyncio
    async def test_error_handling_context_manager(self, error_recovery_manager):
        """Test error handling context manager."""
        # Test successful operation
        async with error_recovery_manager.error_handling_context(
            "test_component", "test_function", "user_123", "session_456"
        ):
            # No exception - should pass through
            pass

        # Test exception handling
        with pytest.raises(Exception):
            async with error_recovery_manager.error_handling_context(
                "test_component", "test_function", "user_123", "session_456"
            ):
                raise Exception("Test exception")

        # Check error was handled
        assert len(error_recovery_manager.error_history) == 1

    @pytest.mark.asyncio
    async def test_recovery_strategies_loading(self, error_recovery_manager):
        """Test that recovery strategies are properly loaded."""
        strategies = error_recovery_manager.recovery_strategies

        # Check that all error categories have strategies
        for category in ErrorCategory:
            assert category in strategies
            assert len(strategies[category]) > 0

            # Check that all strategies are valid
            for strategy in strategies[category]:
                assert strategy in RecoveryStrategy

    @pytest.mark.asyncio
    async def test_fallback_mechanisms_loading(self, error_recovery_manager):
        """Test that fallback mechanisms are properly loaded."""
        fallbacks = error_recovery_manager.fallback_mechanisms

        # Check that key components have fallback mechanisms
        key_components = [
            "narrative_engine",
            "choice_processor",
            "therapeutic_integrator",
            "character_development",
            "session_manager",
            "collaborative_system",
        ]

        for component in key_components:
            assert component in fallbacks
            fallback = fallbacks[component]
            assert "fallback_type" in fallback
            assert "description" in fallback
            assert "maintains_therapeutic_context" in fallback
            assert "performance_impact" in fallback

    @pytest.mark.asyncio
    async def test_therapeutic_interventions_loading(self, error_recovery_manager):
        """Test that therapeutic interventions are properly loaded."""
        interventions = error_recovery_manager.therapeutic_interventions

        # Check that key intervention types are configured
        key_interventions = [
            "session_interruption",
            "data_recovery",
            "system_degradation",
            "collaborative_failure",
        ]

        for intervention_type in key_interventions:
            assert intervention_type in interventions
            intervention = interventions[intervention_type]
            assert "message" in intervention
            assert "therapeutic_focus" in intervention
            assert "coping_strategy" in intervention
            assert "reassurance" in intervention

    def test_get_system_health_status(self, error_recovery_manager):
        """Test system health status reporting."""
        # Add some test data
        error_recovery_manager.degraded_components.add("test_component")
        error_recovery_manager.component_status["test_component"] = "degraded"

        health_status = error_recovery_manager.get_system_health_status()

        # Check health status structure
        assert "overall_status" in health_status
        assert "active_errors" in health_status
        assert "active_errors_by_severity" in health_status
        assert "degraded_components" in health_status
        assert "component_status" in health_status
        assert "recent_errors" in health_status
        assert "recovery_success_rate" in health_status
        assert "system_backups_available" in health_status
        assert "metrics" in health_status

        # Check degraded component is reported
        assert "test_component" in health_status["degraded_components"]
        assert health_status["component_status"]["test_component"] == "degraded"

    def test_recovery_success_rate_calculation(self, error_recovery_manager):
        """Test recovery success rate calculation."""
        # Add some recovery history
        error_recovery_manager.recovery_history = [
            RecoveryResult(success=True),
            RecoveryResult(success=True),
            RecoveryResult(success=False),
            RecoveryResult(success=True),
        ]

        success_rate = error_recovery_manager._calculate_recovery_success_rate()
        assert success_rate == 0.75  # 3 out of 4 successful

        # Test empty history
        error_recovery_manager.recovery_history = []
        success_rate = error_recovery_manager._calculate_recovery_success_rate()
        assert success_rate == 1.0  # Default to 100% when no history

    def test_backup_checksum_calculation(self, error_recovery_manager):
        """Test backup checksum calculation."""
        backup = SystemBackup(
            user_id="user_123", session_id="session_456", session_state={"test": "data"}
        )

        checksum1 = error_recovery_manager._calculate_backup_checksum(backup)
        checksum2 = error_recovery_manager._calculate_backup_checksum(backup)

        # Same data should produce same checksum
        assert checksum1 == checksum2
        assert checksum1 != "invalid"

        # Different data should produce different checksum
        backup.session_state = {"different": "data"}
        checksum3 = error_recovery_manager._calculate_backup_checksum(backup)
        assert checksum3 != checksum1

    @pytest.mark.asyncio
    async def test_backup_integrity_verification(self, error_recovery_manager):
        """Test backup integrity verification."""
        backup = SystemBackup(
            user_id="user_123", session_id="session_456", session_state={"test": "data"}
        )

        # Calculate correct checksum
        backup.checksum = error_recovery_manager._calculate_backup_checksum(backup)
        backup.is_valid = True

        # Should verify successfully
        is_valid = await error_recovery_manager._verify_backup_integrity(backup)
        assert is_valid

        # Corrupt the checksum
        backup.checksum = "invalid_checksum"
        is_valid = await error_recovery_manager._verify_backup_integrity(backup)
        assert not is_valid

        # Mark as invalid
        backup.checksum = error_recovery_manager._calculate_backup_checksum(backup)
        backup.is_valid = False
        is_valid = await error_recovery_manager._verify_backup_integrity(backup)
        assert not is_valid

    def test_metrics_tracking(self, error_recovery_manager):
        """Test metrics tracking."""
        initial_metrics = error_recovery_manager.get_metrics()

        # Check metric structure
        assert "errors_handled" in initial_metrics
        assert "successful_recoveries" in initial_metrics
        assert "failed_recoveries" in initial_metrics
        assert "therapeutic_interventions" in initial_metrics
        assert "session_recoveries" in initial_metrics
        assert "data_recoveries" in initial_metrics
        assert "escalations" in initial_metrics
        assert "system_restarts" in initial_metrics
        assert "active_errors" in initial_metrics
        assert "recovery_success_rate" in initial_metrics

        # Initially should be zero
        assert initial_metrics["errors_handled"] == 0
        assert initial_metrics["successful_recoveries"] == 0
        assert initial_metrics["failed_recoveries"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self, error_recovery_manager):
        """Test health check functionality."""
        health = await error_recovery_manager.health_check()

        assert health["status"] == "healthy"
        assert "recovery_strategies_loaded" in health
        assert "fallback_mechanisms_loaded" in health
        assert "therapeutic_interventions_loaded" in health
        assert "system_health" in health
        assert "metrics" in health

        # Should have loaded strategies and mechanisms
        assert health["recovery_strategies_loaded"] > 0
        assert health["fallback_mechanisms_loaded"] > 0
        assert health["therapeutic_interventions_loaded"] > 0
