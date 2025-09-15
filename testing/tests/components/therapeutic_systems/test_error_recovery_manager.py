"""
Tests for TherapeuticErrorRecoveryManager

This module tests the production error recovery manager implementation
including comprehensive error handling, graceful degradation, and therapeutic continuity maintenance.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.components.therapeutic_systems.error_recovery_manager import (
    ErrorContext,
    ErrorSeverity,
    RecoveryResult,
    RecoveryStrategy,
    SystemStatus,
    TherapeuticErrorRecoveryManager,
)


class TestTherapeuticErrorRecoveryManager:
    """Test TherapeuticErrorRecoveryManager functionality."""

    @pytest.fixture
    def error_recovery_manager(self):
        """Create error recovery manager instance."""
        return TherapeuticErrorRecoveryManager()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        return {
            "consequence_system": AsyncMock(),
            "emotional_safety_system": AsyncMock(),
            "adaptive_difficulty_engine": AsyncMock(),
            "character_development_system": AsyncMock(),
            "therapeutic_integration_system": AsyncMock(),
            "gameplay_loop_controller": AsyncMock(),
            "replayability_system": AsyncMock(),
            "collaborative_system": AsyncMock(),
        }

    @pytest.mark.asyncio
    async def test_initialization(self, error_recovery_manager):
        """Test system initialization."""
        await error_recovery_manager.initialize()

        # Should have empty error tracking
        assert len(error_recovery_manager.active_errors) == 0
        assert len(error_recovery_manager.error_history) == 0
        assert len(error_recovery_manager.recovery_history) == 0
        assert len(error_recovery_manager.system_health) == 0

        # Should have default configuration
        assert error_recovery_manager.max_recovery_attempts == 3
        assert error_recovery_manager.health_check_interval_seconds == 30
        assert error_recovery_manager.error_retention_days == 7
        assert error_recovery_manager.critical_error_escalation_enabled is True

        # Should have initialized metrics
        assert "errors_handled" in error_recovery_manager.metrics
        assert "successful_recoveries" in error_recovery_manager.metrics
        assert error_recovery_manager.metrics["errors_handled"] == 0

        # Should have health monitoring task
        assert error_recovery_manager._health_monitoring_task is not None

        # Clean up
        await error_recovery_manager.shutdown()

    def test_therapeutic_system_injection(self, error_recovery_manager, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all systems injected
        assert error_recovery_manager.consequence_system is not None
        assert error_recovery_manager.emotional_safety_system is not None
        assert error_recovery_manager.adaptive_difficulty_engine is not None
        assert error_recovery_manager.character_development_system is not None
        assert error_recovery_manager.therapeutic_integration_system is not None
        assert error_recovery_manager.gameplay_loop_controller is not None
        assert error_recovery_manager.replayability_system is not None
        assert error_recovery_manager.collaborative_system is not None

        # Should have initialized system health tracking
        assert len(error_recovery_manager.system_health) == 8
        for system_name in mock_therapeutic_systems.keys():
            assert system_name in error_recovery_manager.system_health
            assert error_recovery_manager.system_health[system_name].status == SystemStatus.HEALTHY

    def test_error_severity_assessment(self, error_recovery_manager):
        """Test error severity assessment."""
        # Create custom exception classes for testing
        class CriticalError(Exception):
            pass

        class SystemOverload(Exception):
            pass

        class ValidationError(Exception):
            pass

        # Test critical errors
        critical_error = CriticalError("Critical system failure")
        severity = error_recovery_manager._assess_error_severity(
            critical_error, "emotional_safety_system", None
        )
        assert severity == ErrorSeverity.CRITICAL

        # Test high severity errors
        high_error = SystemOverload("System overload")
        severity = error_recovery_manager._assess_error_severity(
            high_error, "consequence_system", None
        )
        assert severity == ErrorSeverity.HIGH

        # Test medium severity errors
        medium_error = ValidationError("Validation failed")
        severity = error_recovery_manager._assess_error_severity(
            medium_error, "adaptive_difficulty_engine", None
        )
        assert severity == ErrorSeverity.MEDIUM

        # Test therapeutic context influence
        context_error = Exception("Regular error")
        severity = error_recovery_manager._assess_error_severity(
            context_error, "character_development_system", {"crisis_detected": True}
        )
        assert severity == ErrorSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_therapeutic_impact_assessment(self, error_recovery_manager):
        """Test therapeutic impact assessment."""
        # Test error affecting therapeutic continuity
        error_context = ErrorContext(
            component="consequence_system",
            therapeutic_context={"therapeutic_session_active": True}
        )

        await error_recovery_manager._assess_therapeutic_impact(error_context)

        assert error_context.affects_therapeutic_continuity is True

        # Test error affecting user safety
        safety_error_context = ErrorContext(
            component="emotional_safety_system",
            therapeutic_context={"crisis_detected": True}
        )

        await error_recovery_manager._assess_therapeutic_impact(safety_error_context)

        assert safety_error_context.affects_user_safety is True
        assert safety_error_context.requires_immediate_attention is True

    @pytest.mark.asyncio
    async def test_handle_error_comprehensive(self, error_recovery_manager, mock_therapeutic_systems):
        """Test comprehensive error handling."""
        await error_recovery_manager.initialize()
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test error handling
        test_exception = Exception("Test error for comprehensive handling")

        recovery_result = await error_recovery_manager.handle_error(
            exception=test_exception,
            component="consequence_system",
            function="process_choice_consequence",
            user_id="test_user_001",
            session_id="test_session_001",
            therapeutic_context={"therapeutic_session_active": True}
        )

        # Should return valid recovery result
        assert isinstance(recovery_result, RecoveryResult)
        assert recovery_result.success is True  # Retry strategy should succeed
        assert recovery_result.strategy_used == RecoveryStrategy.RETRY
        assert recovery_result.recovery_time_seconds > 0

        # Should track error and recovery
        assert len(error_recovery_manager.error_history) == 1
        assert len(error_recovery_manager.recovery_history) == 1

        # Should update metrics
        assert error_recovery_manager.metrics["errors_handled"] == 1
        assert error_recovery_manager.metrics["successful_recoveries"] == 1

        # Should update system health
        assert "consequence_system" in error_recovery_manager.system_health
        health_status = error_recovery_manager.system_health["consequence_system"]
        assert health_status.recent_errors == 1

        # Clean up
        await error_recovery_manager.shutdown()

    @pytest.mark.asyncio
    async def test_retry_recovery_strategy(self, error_recovery_manager):
        """Test retry recovery strategy."""
        error_context = ErrorContext(
            error_type="ConnectionError",
            component="therapeutic_integration_system",
            function="generate_recommendations"
        )

        recovery_result = await error_recovery_manager._execute_retry_strategy(error_context)

        assert recovery_result.success is True
        assert recovery_result.strategy_used == RecoveryStrategy.RETRY
        assert "operation_retried" in recovery_result.actions_taken

    @pytest.mark.asyncio
    async def test_fallback_recovery_strategy(self, error_recovery_manager):
        """Test fallback recovery strategy."""
        error_context = ErrorContext(
            error_type="ServiceUnavailable",
            component="consequence_system",
            function="process_choice_consequence"
        )

        recovery_result = await error_recovery_manager._execute_fallback_strategy(error_context)

        assert recovery_result.success is True
        assert recovery_result.strategy_used == RecoveryStrategy.FALLBACK
        assert "consequence_system" in recovery_result.fallback_systems_activated
        assert "consequence_system" in recovery_result.degraded_functionality
        assert "simplified_consequences" in recovery_result.actions_taken[0]

        # Should mark system as degraded
        assert "consequence_system" in error_recovery_manager.degraded_systems

    @pytest.mark.asyncio
    async def test_graceful_degradation_strategy(self, error_recovery_manager):
        """Test graceful degradation recovery strategy."""
        error_context = ErrorContext(
            error_type="SystemOverload",
            component="adaptive_difficulty_engine",
            function="adjust_difficulty"
        )

        recovery_result = await error_recovery_manager._execute_graceful_degradation_strategy(error_context)

        assert recovery_result.success is True
        assert recovery_result.strategy_used == RecoveryStrategy.GRACEFUL_DEGRADATION
        assert "graceful_degradation_activated" in recovery_result.actions_taken
        assert len(recovery_result.degraded_functionality) > 0
        assert recovery_result.monitoring_required is True

    @pytest.mark.asyncio
    async def test_therapeutic_intervention_strategy(self, error_recovery_manager):
        """Test therapeutic intervention recovery strategy."""
        error_context = ErrorContext(
            error_type="ValidationError",
            component="emotional_safety_system",
            function="assess_crisis_risk"
        )

        recovery_result = await error_recovery_manager._execute_therapeutic_intervention_strategy(error_context)

        assert recovery_result.success is True
        assert recovery_result.strategy_used == RecoveryStrategy.THERAPEUTIC_INTERVENTION
        assert "therapeutic_intervention_provided" in recovery_result.actions_taken
        assert recovery_result.user_message is not None
        assert recovery_result.therapeutic_message is not None
        assert recovery_result.requires_user_notification is True
        assert recovery_result.monitoring_required is True

    @pytest.mark.asyncio
    async def test_system_restart_strategy(self, error_recovery_manager):
        """Test system restart recovery strategy."""
        error_recovery_manager.inject_therapeutic_systems(consequence_system=AsyncMock())

        error_context = ErrorContext(
            error_type="CriticalError",
            component="consequence_system",
            function="initialize"
        )

        recovery_result = await error_recovery_manager._execute_system_restart_strategy(error_context)

        assert recovery_result.success is True
        assert recovery_result.strategy_used == RecoveryStrategy.SYSTEM_RESTART
        assert "system_restart_initiated_consequence_system" in recovery_result.actions_taken
        assert recovery_result.monitoring_required is True

        # Should update system status
        assert error_recovery_manager.system_health["consequence_system"].status == SystemStatus.RECOVERING

    @pytest.mark.asyncio
    async def test_escalation_strategy(self, error_recovery_manager):
        """Test escalation recovery strategy."""
        error_context = ErrorContext(
            error_type="UnknownError",
            component="unknown_system",
            function="unknown_function"
        )

        recovery_result = await error_recovery_manager._execute_escalation_strategy(error_context)

        assert recovery_result.success is False
        assert recovery_result.strategy_used == RecoveryStrategy.ESCALATION
        assert "error_escalated_to_support" in recovery_result.actions_taken
        assert recovery_result.escalation_needed is True
        assert recovery_result.manual_intervention_required is True

    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, error_recovery_manager, mock_therapeutic_systems):
        """Test system health monitoring."""
        await error_recovery_manager.initialize()
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Mock health check responses
        for system in mock_therapeutic_systems.values():
            system.health_check.return_value = {"status": "healthy"}

        # Perform health checks
        await error_recovery_manager._perform_health_checks()

        # Should update system health
        for system_name in mock_therapeutic_systems.keys():
            assert system_name in error_recovery_manager.system_health
            health_status = error_recovery_manager.system_health[system_name]
            assert health_status.last_health_check is not None
            assert health_status.response_time_ms >= 0

        # Should update metrics
        assert error_recovery_manager.metrics["health_checks_performed"] == 1

        # Clean up
        await error_recovery_manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_system_health_status(self, error_recovery_manager, mock_therapeutic_systems):
        """Test system health status retrieval."""
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Add some test data
        error_recovery_manager.active_errors["test_error"] = ErrorContext()
        error_recovery_manager.degraded_systems.add("consequence_system")

        health_status = await error_recovery_manager.get_system_health_status()

        assert isinstance(health_status, dict)
        assert "overall_status" in health_status
        assert "total_systems" in health_status
        assert "healthy_systems" in health_status
        assert "degraded_systems" in health_status
        assert "active_errors" in health_status
        assert "system_details" in health_status

        assert health_status["total_systems"] == 8
        assert health_status["degraded_systems"] == 1
        assert health_status["active_errors"] == 1

    @pytest.mark.asyncio
    async def test_health_check(self, error_recovery_manager, mock_therapeutic_systems):
        """Test error recovery manager health check."""
        await error_recovery_manager.initialize()
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        health = await error_recovery_manager.health_check()

        assert "status" in health
        assert health["status"] == "healthy"  # All 8 systems available
        assert "error_severities" in health
        assert health["error_severities"] == 4
        assert "recovery_strategies" in health
        assert health["recovery_strategies"] == 6
        assert "system_statuses" in health
        assert health["system_statuses"] == 5
        assert "therapeutic_systems" in health
        assert health["systems_available"] == "8/8"
        assert health["health_monitoring_active"] is True

        # Clean up
        await error_recovery_manager.shutdown()

    @pytest.mark.asyncio
    async def test_health_check_degraded(self, error_recovery_manager):
        """Test health check with missing systems."""
        await error_recovery_manager.initialize()
        # Don't inject all systems - only inject a few
        error_recovery_manager.inject_therapeutic_systems(
            consequence_system=AsyncMock(),
            emotional_safety_system=AsyncMock()
        )

        health = await error_recovery_manager.health_check()

        assert health["status"] == "degraded"  # Less than 6 systems available
        assert health["systems_available"] == "2/8"

        # Clean up
        await error_recovery_manager.shutdown()

    def test_get_metrics(self, error_recovery_manager):
        """Test metrics collection."""
        # Add some test data
        error_recovery_manager.metrics["errors_handled"] = 5
        error_recovery_manager.metrics["successful_recoveries"] = 4
        error_recovery_manager.error_history.append(ErrorContext(severity=ErrorSeverity.HIGH))
        error_recovery_manager.error_history.append(ErrorContext(severity=ErrorSeverity.MEDIUM))
        error_recovery_manager.recovery_history.append(RecoveryResult(success=True, strategy_used=RecoveryStrategy.RETRY))

        metrics = error_recovery_manager.get_metrics()

        assert isinstance(metrics, dict)
        assert "errors_handled" in metrics
        assert "successful_recoveries" in metrics
        assert "total_errors" in metrics
        assert "error_by_severity" in metrics
        assert "recovery_by_strategy" in metrics
        assert "recovery_success_rate" in metrics

        assert metrics["errors_handled"] == 5
        assert metrics["successful_recoveries"] == 4
        assert metrics["total_errors"] == 2
        assert metrics["error_by_severity"]["high"] == 1
        assert metrics["error_by_severity"]["medium"] == 1

    @pytest.mark.asyncio
    async def test_error_cleanup(self, error_recovery_manager):
        """Test automatic error cleanup."""
        # Add old errors
        old_error = ErrorContext(timestamp=datetime.utcnow() - timedelta(days=10))
        recent_error = ErrorContext(timestamp=datetime.utcnow() - timedelta(hours=1))

        error_recovery_manager.error_history = [old_error, recent_error]
        error_recovery_manager.active_errors["old"] = old_error
        error_recovery_manager.active_errors["recent"] = recent_error

        # Cleanup old errors
        await error_recovery_manager._cleanup_old_errors()

        # Should keep recent errors, remove old ones
        assert len(error_recovery_manager.error_history) == 1
        assert error_recovery_manager.error_history[0] == recent_error
        assert "old" not in error_recovery_manager.active_errors
        assert "recent" in error_recovery_manager.active_errors

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, error_recovery_manager, mock_therapeutic_systems):
        """Test compatibility with E2E test interface expectations."""
        await error_recovery_manager.initialize()
        error_recovery_manager.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Test error handling (E2E interface)
        test_exception = Exception("E2E test error")

        recovery_result = await error_recovery_manager.handle_error(
            exception=test_exception,
            component="demo_system",
            function="demo_function",
            user_id="demo_user_001",
            session_id="demo_session_001"
        )

        # Should match expected structure
        assert hasattr(recovery_result, "success")
        assert hasattr(recovery_result, "strategy_used")
        assert hasattr(recovery_result, "recovery_time_seconds")
        assert hasattr(recovery_result, "user_message")
        assert hasattr(recovery_result, "escalation_needed")

        # Test health check (E2E interface)
        health = await error_recovery_manager.health_check()

        # Should match expected structure
        assert "status" in health
        assert "systems_available" in health
        assert "metrics" in health

        # Clean up
        await error_recovery_manager.shutdown()
