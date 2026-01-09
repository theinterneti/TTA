"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands_integration/Test_client]]
Tests for OpenHands client wrapper.

Tests:
- Client initialization
- SDK component initialization
- Task execution
- Timeout handling
- Error handling
- Resource cleanup
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from src.agent_orchestration.openhands_integration.client import OpenHandsClient
from src.agent_orchestration.openhands_integration.config import OpenHandsConfig


class TestOpenHandsClient:
    """Tests for OpenHandsClient."""

    def test_client_initialization(self, openhands_config: OpenHandsConfig):
        """Test client initialization."""
        client = OpenHandsClient(openhands_config)

        assert client.config == openhands_config
        assert client._llm is None  # Lazy initialization
        assert client._agent is None
        assert client._conversation is None

    @pytest.mark.asyncio
    async def test_execute_task_mock(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test task execution with mocked SDK."""
        client = OpenHandsClient(openhands_config)

        result = await client.execute_task("Write a Python function")

        # Verify SDK was initialized
        assert client._llm is not None
        assert client._agent is not None
        assert client._conversation is not None

        # Verify result
        assert result.success is True
        assert result.execution_time > 0
        assert "workspace" in result.metadata

    @pytest.mark.asyncio
    async def test_execute_task_with_custom_workspace(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
        test_workspace,
    ):
        """Test task execution with custom workspace."""
        client = OpenHandsClient(openhands_config)
        custom_workspace = test_workspace / "custom"
        custom_workspace.mkdir()

        result = await client.execute_task(
            "Write a Python function", workspace_path=custom_workspace
        )

        assert result.success is True
        assert str(custom_workspace) in str(result.metadata.get("workspace"))

    @pytest.mark.asyncio
    async def test_execute_task_with_custom_timeout(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test task execution with custom timeout."""
        client = OpenHandsClient(openhands_config)

        result = await client.execute_task("Write a Python function", timeout=120.0)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_task_error_handling(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test error handling during task execution."""
        client = OpenHandsClient(openhands_config)

        # Make conversation.run() raise an error
        mock_openhands_sdk["conversation"].run.side_effect = RuntimeError("SDK error")

        result = await client.execute_task("Write a Python function")

        # Should return failed result, not raise
        assert result.success is False
        assert result.error is not None
        assert "SDK error" in result.error

    @pytest.mark.asyncio
    async def test_cleanup(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test resource cleanup."""
        client = OpenHandsClient(openhands_config)

        # Initialize SDK
        await client.execute_task("Write a Python function")
        assert client._llm is not None

        # Cleanup
        await client.cleanup()
        assert client._llm is None
        assert client._agent is None
        assert client._conversation is None

    @pytest.mark.asyncio
    async def test_multiple_tasks(
        self,
        openhands_config: OpenHandsConfig,
        mock_openhands_sdk: dict[str, Any],
    ):
        """Test executing multiple tasks with same client."""
        client = OpenHandsClient(openhands_config)

        # Execute first task
        result1 = await client.execute_task("Task 1")
        assert result1.success is True

        # Execute second task (should reuse SDK components)
        result2 = await client.execute_task("Task 2")
        assert result2.success is True

        # Verify SDK was initialized only once
        assert mock_openhands_sdk["llm_class"].call_count == 1
        assert mock_openhands_sdk["agent_class"].call_count == 1

    @pytest.mark.asyncio
    async def test_execute_task_with_conversation_history(
        self, openhands_config, mock_openhands_sdk
    ):
        """Test task execution with conversation history extraction."""
        # Create mock conversation with history
        mock_conversation = MagicMock()

        # Create mock events with different attributes
        mock_event1 = MagicMock()
        mock_event1.source = "agent"
        mock_event1.message = "First agent message"

        mock_event2 = MagicMock()
        mock_event2.source = "agent"
        mock_event2.content = "Second agent message (content)"
        delattr(mock_event2, "message")  # Remove message attribute

        mock_event3 = MagicMock()
        mock_event3.source = "user"
        mock_event3.message = "User message (should be ignored)"

        mock_conversation.history = [mock_event3, mock_event2, mock_event1]
        mock_conversation.send_message = MagicMock()
        mock_conversation.run = MagicMock()

        # Update SDK mock to return our conversation
        mock_openhands_sdk["conversation_class"].return_value = mock_conversation

        client = OpenHandsClient(openhands_config)
        result = await client.execute_task("Test task")

        assert result.success is True
        # Output should contain agent messages (in reverse order)
        assert (
            "First agent message" in result.output
            or "Second agent message" in result.output
        )


@pytest.mark.skip(reason="Requires --run-real-api flag and OPENROUTER_API_KEY")
class TestOpenHandsClientRealAPI:
    """Tests with real OpenRouter API (requires API key)."""

    @pytest.mark.asyncio
    async def test_real_api_execution(self, openhands_config: OpenHandsConfig):
        """Test execution with real OpenRouter API."""
        # This test requires a real API key
        client = OpenHandsClient(openhands_config)

        result = await client.execute_task(
            "Write a simple Python function that adds two numbers"
        )

        assert result.success is True
        assert result.execution_time > 0
        assert result.output  # Should have output