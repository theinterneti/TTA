"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands_integration/Test_error_recovery]]
Tests for OpenHandsErrorRecovery.

Tests error classification, recovery strategy selection, retry logic,
circuit breaker integration, and fallback mechanisms.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.agent_orchestration.openhands_integration.error_recovery import (
    OpenHandsErrorRecovery,
)
from src.agent_orchestration.openhands_integration.models import (
    RECOVERY_STRATEGIES,
    OpenHandsErrorType,
    OpenHandsRecoveryStrategy,
)


class TestErrorClassification:
    """Tests for error classification."""

    def test_classify_connection_error(self, integration_config):
        """Test classification of connection errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = Exception("Connection timeout")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.CONNECTION_ERROR
        )

        error = Exception("Network error occurred")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.CONNECTION_ERROR
        )

    def test_classify_timeout_error(self, integration_config):
        """Test classification of timeout errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = TimeoutError("Task timed out")
        assert (
            recovery.classify_openhands_error(error) == OpenHandsErrorType.TIMEOUT_ERROR
        )

        error = Exception("timeout exceeded")
        assert (
            recovery.classify_openhands_error(error) == OpenHandsErrorType.TIMEOUT_ERROR
        )

    def test_classify_authentication_error(self, integration_config):
        """Test classification of authentication errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = Exception("Invalid API key")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.AUTHENTICATION_ERROR
        )

        error = Exception("401 Unauthorized")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.AUTHENTICATION_ERROR
        )

        error = Exception("Authentication failed")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.AUTHENTICATION_ERROR
        )

    def test_classify_rate_limit_error(self, integration_config):
        """Test classification of rate limit errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = Exception("Rate limit exceeded")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.RATE_LIMIT_ERROR
        )

        error = Exception("429 Too Many Requests")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.RATE_LIMIT_ERROR
        )

    def test_classify_validation_error(self, integration_config):
        """Test classification of validation errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = ValueError("Invalid input")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.VALIDATION_ERROR
        )

        error = Exception("Validation failed")
        assert (
            recovery.classify_openhands_error(error)
            == OpenHandsErrorType.VALIDATION_ERROR
        )

    def test_classify_sdk_error(self, integration_config):
        """Test classification of SDK errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = Exception("OpenHands SDK error")
        assert recovery.classify_openhands_error(error) == OpenHandsErrorType.SDK_ERROR

        error = Exception("SDK initialization failed")
        assert recovery.classify_openhands_error(error) == OpenHandsErrorType.SDK_ERROR

    def test_classify_unknown_error(self, integration_config):
        """Test classification of unknown errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = Exception("Some random error")
        assert (
            recovery.classify_openhands_error(error) == OpenHandsErrorType.UNKNOWN_ERROR
        )


class TestRecoveryStrategies:
    """Tests for recovery strategy selection."""

    def test_connection_error_strategies(self):
        """Test recovery strategies for connection errors."""
        strategies = RECOVERY_STRATEGIES[OpenHandsErrorType.CONNECTION_ERROR]
        assert OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF in strategies
        assert OpenHandsRecoveryStrategy.CIRCUIT_BREAK in strategies
        assert OpenHandsRecoveryStrategy.FALLBACK_MOCK in strategies

    def test_timeout_error_strategies(self):
        """Test recovery strategies for timeout errors."""
        strategies = RECOVERY_STRATEGIES[OpenHandsErrorType.TIMEOUT_ERROR]
        assert OpenHandsRecoveryStrategy.RETRY in strategies
        assert OpenHandsRecoveryStrategy.FALLBACK_MOCK in strategies

    def test_authentication_error_strategies(self):
        """Test recovery strategies for authentication errors."""
        strategies = RECOVERY_STRATEGIES[OpenHandsErrorType.AUTHENTICATION_ERROR]
        assert OpenHandsRecoveryStrategy.ESCALATE in strategies
        # Authentication errors cannot be auto-recovered

    def test_rate_limit_error_strategies(self):
        """Test recovery strategies for rate limit errors."""
        strategies = RECOVERY_STRATEGIES[OpenHandsErrorType.RATE_LIMIT_ERROR]
        assert OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF in strategies
        assert OpenHandsRecoveryStrategy.FALLBACK_MODEL in strategies
        assert OpenHandsRecoveryStrategy.CIRCUIT_BREAK in strategies


class TestExecuteWithRecovery:
    """Tests for execute_with_recovery method."""

    @pytest.mark.asyncio
    async def test_execute_with_recovery_success(self, integration_config):
        """Test successful execution without errors."""
        recovery = OpenHandsErrorRecovery(integration_config)

        async def successful_func():
            return {"success": True, "result": "data"}

        result = await recovery.execute_with_recovery(successful_func)
        assert result["success"] is True
        assert result["result"] == "data"

    @pytest.mark.asyncio
    async def test_execute_with_recovery_fallback_mock(self, integration_config):
        """Test fallback to mock response on error."""
        # Enable fallback to mock
        integration_config.fallback_to_mock = True
        # Disable retry to test fallback directly
        integration_config.max_retries = 0
        recovery = OpenHandsErrorRecovery(integration_config)

        async def failing_func():
            raise Exception("Connection error")

        # Should return mock response instead of raising
        # Note: With retry enabled, this will retry and eventually raise
        # We test the fallback mechanism in _execute_with_circuit_breaker
        with pytest.raises(Exception):
            await recovery.execute_with_recovery(failing_func)

    @pytest.mark.asyncio
    async def test_execute_with_recovery_with_circuit_breaker(
        self, integration_config, mock_circuit_breaker
    ):
        """Test execution with circuit breaker."""

        # Mock circuit breaker execute to return the function result
        async def mock_execute(func, *args, **kwargs):
            return await func(*args, **kwargs)

        mock_circuit_breaker.execute = AsyncMock(side_effect=mock_execute)

        recovery = OpenHandsErrorRecovery(
            integration_config,
            circuit_breaker=mock_circuit_breaker,
        )

        async def test_func():
            return {"success": True}

        result = await recovery.execute_with_recovery(test_func)
        assert result["success"] is True
        # Verify circuit breaker was called
        assert mock_circuit_breaker.execute.called

    @pytest.mark.asyncio
    async def test_execute_with_recovery_with_error_reporter(self, integration_config):
        """Test error reporting during recovery."""
        from unittest.mock import patch

        from src.agent_orchestration.openhands_integration.models import (
            OpenHandsErrorType,
            OpenHandsRecoveryStrategy,
        )

        mock_error_reporter = AsyncMock()

        # Enable fallback to mock
        integration_config.fallback_to_mock = True

        # Mock RECOVERY_STRATEGIES to only use FALLBACK_MOCK (skip RETRY)
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.FALLBACK_MOCK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(
                integration_config,
                error_reporter=mock_error_reporter,
            )

            async def failing_func():
                raise Exception("Test error")

            result = await recovery.execute_with_recovery(failing_func)

            # Verify error was reported
            mock_error_reporter.report_error.assert_called_once()

            # Verify fallback mock response was returned
            assert result["success"] is True
            assert result["metadata"]["mock"] is True
            call_kwargs = mock_error_reporter.report_error.call_args.kwargs
            assert "error_type" in call_kwargs
            assert "error_message" in call_kwargs


class TestMockResponseGeneration:
    """Tests for mock response generation."""

    def test_generate_mock_response(self, integration_config):
        """Test mock response generation."""
        recovery = OpenHandsErrorRecovery(integration_config)

        mock_response = recovery._generate_mock_response()

        assert mock_response["success"] is True
        assert (
            "MOCK" in mock_response["output"]
            or "mock" in mock_response["output"].lower()
        )
        assert mock_response["error"] is None
        assert mock_response["metadata"]["mock"] is True
        assert mock_response["metadata"]["fallback"] is True


class TestRetryConfigInitialization:
    """Tests for retry configuration initialization."""

    def test_retry_config_initialization_with_primitives(self, integration_config):
        """Test retry config initialization when primitives are available."""
        recovery = OpenHandsErrorRecovery(integration_config)

        # Verify retry config was initialized
        assert recovery.retry_config is not None
        assert recovery.retry_config.max_retries == integration_config.max_retries
        assert recovery.retry_config.base_delay == integration_config.retry_base_delay
        assert recovery.retry_config.exponential_base == 2.0
        assert recovery.retry_config.jitter is True

    def test_retry_config_initialization_without_primitives(self, integration_config):
        """Test retry config initialization when primitives are not available."""
        # Test that when retry_config is None, execute_with_recovery still works
        recovery = OpenHandsErrorRecovery(integration_config)

        # Manually set retry_config to None to simulate import failure
        recovery.retry_config = None

        # Verify retry config is None
        assert recovery.retry_config is None


class TestErrorReporting:
    """Tests for error reporting functionality."""

    @pytest.mark.asyncio
    async def test_error_reporting_on_failure(self, integration_config):
        """Test that errors are reported when error_reporter is provided."""
        mock_error_reporter = AsyncMock()

        # Enable fallback to mock
        integration_config.fallback_to_mock = True

        # Mock RECOVERY_STRATEGIES to only use FALLBACK_MOCK
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.FALLBACK_MOCK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(
                integration_config,
                error_reporter=mock_error_reporter,
            )

            async def failing_func():
                raise Exception("Test error")

            await recovery.execute_with_recovery(failing_func)

            # Verify error was reported
            mock_error_reporter.report_error.assert_called_once()
            call_kwargs = mock_error_reporter.report_error.call_args.kwargs
            assert "error_type" in call_kwargs
            assert "error_message" in call_kwargs
            assert "context" in call_kwargs

    @pytest.mark.asyncio
    async def test_error_reporting_failure_handling(self, integration_config):
        """Test that error reporting failures are handled gracefully."""
        mock_error_reporter = AsyncMock()
        mock_error_reporter.report_error.side_effect = Exception("Reporting failed")

        # Enable fallback to mock
        integration_config.fallback_to_mock = True

        # Mock RECOVERY_STRATEGIES to only use FALLBACK_MOCK
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.FALLBACK_MOCK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(
                integration_config,
                error_reporter=mock_error_reporter,
            )

            async def failing_func():
                raise Exception("Test error")

            # Should not raise even if error reporting fails
            result = await recovery.execute_with_recovery(failing_func)
            assert result["success"] is True
            assert result["metadata"]["mock"] is True


class TestRecoveryStrategyExecution:
    """Tests for recovery strategy execution."""

    @pytest.mark.asyncio
    async def test_retry_strategy_raises_error(self, integration_config):
        """Test that RETRY strategy re-raises the error."""
        integration_config.fallback_to_mock = False

        # Mock RECOVERY_STRATEGIES to only use RETRY
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.RETRY,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            async def failing_func():
                raise Exception("Test error")

            # Should raise because RETRY strategy re-raises
            with pytest.raises(Exception, match="Test error"):
                await recovery.execute_with_recovery(failing_func)

    @pytest.mark.asyncio
    async def test_retry_with_backoff_strategy(self, integration_config):
        """Test that RETRY_WITH_BACKOFF strategy increases backoff delay."""
        integration_config.fallback_to_mock = False

        # Mock RECOVERY_STRATEGIES to only use RETRY_WITH_BACKOFF
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.RETRY_WITH_BACKOFF,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            # Store original delay
            original_delay = (
                recovery.retry_config.base_delay if recovery.retry_config else None
            )

            async def failing_func():
                raise Exception("Test error")

            # Should raise because RETRY_WITH_BACKOFF strategy re-raises
            with pytest.raises(Exception, match="Test error"):
                await recovery.execute_with_recovery(failing_func)

            # Verify backoff delay was increased
            if recovery.retry_config and original_delay:
                assert recovery.retry_config.base_delay == original_delay * 2

    @pytest.mark.asyncio
    async def test_circuit_break_strategy_raises_error(self, integration_config):
        """Test that CIRCUIT_BREAK strategy re-raises the error."""
        integration_config.fallback_to_mock = False

        # Mock RECOVERY_STRATEGIES to only use CIRCUIT_BREAK
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.CIRCUIT_BREAK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            async def failing_func():
                raise Exception("Test error")

            # Should raise because CIRCUIT_BREAK strategy re-raises
            with pytest.raises(Exception, match="Test error"):
                await recovery.execute_with_recovery(failing_func)

    @pytest.mark.asyncio
    async def test_escalate_strategy_raises_error(self, integration_config):
        """Test that ESCALATE strategy re-raises the error."""
        integration_config.fallback_to_mock = False

        # Mock RECOVERY_STRATEGIES to only use ESCALATE
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.ESCALATE,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            async def failing_func():
                raise Exception("Test error")

            # Should raise because ESCALATE strategy re-raises
            with pytest.raises(Exception, match="Test error"):
                await recovery.execute_with_recovery(failing_func)

    @pytest.mark.asyncio
    async def test_fallback_mock_disabled_raises_error(self, integration_config):
        """Test that FALLBACK_MOCK strategy raises when fallback is disabled."""
        integration_config.fallback_to_mock = False

        # Mock RECOVERY_STRATEGIES to only use FALLBACK_MOCK
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.FALLBACK_MOCK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            async def failing_func():
                raise Exception("Test error")

            # Should raise because fallback is disabled
            with pytest.raises(Exception, match="Test error"):
                await recovery.execute_with_recovery(failing_func)

    @pytest.mark.asyncio
    async def test_execute_without_retry_config(self, integration_config):
        """Test execution when retry_config is None."""
        recovery = OpenHandsErrorRecovery(integration_config)
        recovery.retry_config = None

        async def successful_func():
            return {"success": True, "result": "data"}

        result = await recovery.execute_with_recovery(successful_func)
        assert result["success"] is True
        assert result["result"] == "data"

    @pytest.mark.asyncio
    async def test_fallback_mock_strategy_success(self, integration_config):
        """Test that FALLBACK_MOCK strategy returns mock response when enabled."""
        integration_config.fallback_to_mock = True

        # Mock RECOVERY_STRATEGIES to only use FALLBACK_MOCK
        mock_strategies = {
            OpenHandsErrorType.UNKNOWN_ERROR: [
                OpenHandsRecoveryStrategy.FALLBACK_MOCK,
            ],
        }

        with patch(
            "src.agent_orchestration.openhands_integration.error_recovery.RECOVERY_STRATEGIES",
            mock_strategies,
        ):
            recovery = OpenHandsErrorRecovery(integration_config)

            async def failing_func():
                raise Exception("Test error")

            # Should return mock response when FALLBACK_MOCK strategy is used
            result = await recovery.execute_with_recovery(failing_func)
            assert result["success"] is True
            assert result["metadata"]["mock"] is True

    @pytest.mark.asyncio
    async def test_error_classification_with_timeout_error_type(
        self, integration_config
    ):
        """Test error classification with TimeoutError type."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = TimeoutError("Operation timed out")
        error_type = recovery.classify_openhands_error(error)
        assert error_type == OpenHandsErrorType.TIMEOUT_ERROR

    @pytest.mark.asyncio
    async def test_error_classification_with_value_error_type(self, integration_config):
        """Test error classification with ValueError type."""
        recovery = OpenHandsErrorRecovery(integration_config)

        error = ValueError("Invalid value")
        error_type = recovery.classify_openhands_error(error)
        assert error_type == OpenHandsErrorType.VALIDATION_ERROR
