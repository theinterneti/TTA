"""
Tests for OpenHandsAdapter.

Tests adapter initialization, task execution, retry logic, fallback mechanism,
and error propagation.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_orchestration.adapters import RetryConfig
from src.agent_orchestration.openhands_integration.adapter import OpenHandsAdapter
from src.agent_orchestration.openhands_integration.client import OpenHandsClient
from src.agent_orchestration.openhands_integration.config import OpenHandsConfig
from src.agent_orchestration.openhands_integration.models import OpenHandsTaskResult


@pytest.fixture
def retry_config() -> RetryConfig:
    """Create test retry configuration."""
    return RetryConfig(
        max_retries=3,
        base_delay=0.1,  # Short delay for tests
        max_delay=1.0,
        exponential_base=2.0,
        jitter=False,  # Disable jitter for predictable tests
    )


@pytest.fixture
def adapter(retry_config: RetryConfig, openhands_config: OpenHandsConfig) -> OpenHandsAdapter:
    """Create test adapter instance."""
    client = OpenHandsClient(openhands_config)
    return OpenHandsAdapter(
        client=client,
        fallback_to_mock=True,
        retry_config=retry_config,
    )


@pytest.fixture
def adapter_no_fallback(retry_config: RetryConfig, openhands_config: OpenHandsConfig) -> OpenHandsAdapter:
    """Create test adapter instance without fallback."""
    client = OpenHandsClient(openhands_config)
    return OpenHandsAdapter(
        client=client,
        fallback_to_mock=False,
        retry_config=retry_config,
    )


class TestOpenHandsAdapter:
    """Tests for OpenHandsAdapter."""

    def test_adapter_initialization(self, adapter: OpenHandsAdapter, retry_config: RetryConfig):
        """Test adapter initialization with retry config."""
        assert adapter.fallback_to_mock is True
        assert adapter.retry_config == retry_config
        assert adapter.retry_config.max_retries == 3
        assert adapter.retry_config.base_delay == 0.1

    def test_adapter_initialization_no_fallback(self, adapter_no_fallback: OpenHandsAdapter):
        """Test adapter initialization without fallback."""
        assert adapter_no_fallback.fallback_to_mock is False

    @pytest.mark.asyncio
    async def test_execute_task_success(
        self,
        adapter: OpenHandsAdapter,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test successful task execution."""
        task = "Write a Python function to calculate fibonacci numbers"

        # Mock client to return success
        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="def fibonacci(n): ...",
                error=None,
                execution_time=1.5,
            )

            result = await adapter.execute_development_task(
                task_description=task,
            )

            assert result["success"] is True
            assert result["output"] == "def fibonacci(n): ..."
            assert result["error"] is None
            assert mock_execute.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_task_with_retry(
        self,
        adapter: OpenHandsAdapter,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test task execution with retry on transient failure."""
        task = "Write a Python function"

        # Mock client to fail first (exception), then succeed
        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [
                # First attempt raises exception (triggers retry)
                Exception("Connection timeout"),
                # Second attempt succeeds
                OpenHandsTaskResult(
                    success=True,
                    output="def function(): pass",
                    error=None,
                    execution_time=1.0,
                ),
            ]

            result = await adapter.execute_development_task(
                task_description=task,
            )

            # Should succeed after retry
            assert result["success"] is True
            assert result["output"] == "def function(): pass"
            assert mock_execute.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_task_fallback_to_mock(
        self,
        adapter: OpenHandsAdapter,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test fallback to mock response when client fails."""
        task = "Write a Python function"

        # Mock client to always fail
        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("SDK error")

            result = await adapter.execute_development_task(
                task_description=task,
            )

            # Should fallback to mock response
            assert result["success"] is True
            assert "MOCK" in result["output"] or "mock" in result["output"].lower()
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_execute_task_error_propagation(
        self,
        adapter_no_fallback: OpenHandsAdapter,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test error propagation when fallback is disabled."""
        task = "Write a Python function"

        # Mock client to fail
        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("SDK error")

            # Should raise exception when fallback is disabled
            with pytest.raises(Exception):
                await adapter_no_fallback.execute_development_task(
                    task_description=task,
                )

    @pytest.mark.asyncio
    async def test_execute_task_retry_exhaustion(
        self,
        adapter_no_fallback: OpenHandsAdapter,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test retry exhaustion and final failure."""
        task = "Write a Python function"

        # Mock client to always raise exception (triggers retry until exhaustion)
        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Persistent error")

            # Should raise AgentCommunicationError after all retries exhausted (no fallback)
            with pytest.raises(Exception):
                await adapter_no_fallback.execute_development_task(
                    task_description=task,
                )

            # Should have tried max_retries + 1 times (initial + retries)
            assert mock_execute.call_count == 4  # 1 initial + 3 retries

    @pytest.mark.asyncio
    async def test_execute_task_with_custom_timeout(
        self,
        adapter: OpenHandsAdapter,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test task execution with custom timeout."""
        task = "Write a Python function"
        custom_timeout = 120.0

        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="def function(): pass",
                error=None,
                execution_time=1.0,
            )

            result = await adapter.execute_development_task(
                task_description=task,
                context={"timeout": custom_timeout},
            )

            assert result["success"] is True
            # Verify timeout was passed to client
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args.kwargs
            assert call_kwargs.get('timeout') == custom_timeout

    @pytest.mark.asyncio
    async def test_execute_task_with_workspace(
        self,
        adapter: OpenHandsAdapter,
        test_workspace,
    ):
        """Test task execution with custom workspace."""
        task = "Write a Python function"
        custom_workspace = test_workspace / "custom"
        custom_workspace.mkdir()

        with patch.object(OpenHandsClient, 'execute_task', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="def function(): pass",
                error=None,
                execution_time=1.0,
            )

            result = await adapter.execute_development_task(
                task_description=task,
                context={"workspace_path": custom_workspace},
            )

            assert result["success"] is True
            # Verify workspace was passed to client
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args.kwargs
            assert call_kwargs.get('workspace_path') == custom_workspace

