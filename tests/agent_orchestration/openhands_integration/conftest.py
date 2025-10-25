"""
Pytest fixtures for OpenHands integration tests.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)


@pytest.fixture
def openhands_config():
    """Provide a test OpenHands integration configuration."""
    return OpenHandsIntegrationConfig(
        api_key=SecretStr("test-api-key"),
        base_url="https://openrouter.ai/api/v1",
        model_preset="deepseek-v3",
        workspace_root=Path("/tmp/test_workspace"),
    )


@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock OpenHands LLM."""
    llm = MagicMock()
    llm.model = "deepseek/deepseek-v3:free"
    return llm


@pytest.fixture
def mock_agent() -> MagicMock:
    """Mock OpenHands Agent."""
    agent = MagicMock()
    agent.name = "test-agent"
    return agent


@pytest.fixture
def mock_conversation() -> MagicMock:
    """Mock OpenHands Conversation."""
    conversation = MagicMock()
    conversation.send_message = MagicMock()
    conversation.run = MagicMock()
    conversation.history = []
    return conversation


@pytest.fixture
def mock_openhands_sdk(
    mock_llm: MagicMock,
    mock_agent: MagicMock,
    mock_conversation: MagicMock,
) -> dict[str, Any]:
    """
    Mock the entire OpenHands SDK.

    Returns:
        Dictionary with mock components
    """
    # Mock LLM class
    mock_llm_class = MagicMock(return_value=mock_llm)

    # Mock Agent class
    mock_agent_class = MagicMock(return_value=mock_agent)

    # Mock Conversation class
    mock_conversation_class = MagicMock(return_value=mock_conversation)

    # Create mock modules
    import sys
    from types import ModuleType

    # Mock openhands.sdk module
    openhands_sdk = ModuleType("openhands.sdk")
    openhands_sdk.LLM = mock_llm_class
    openhands_sdk.Agent = mock_agent_class
    openhands_sdk.Conversation = mock_conversation_class
    sys.modules["openhands.sdk"] = openhands_sdk

    # Mock openhands module
    sys.modules["openhands"] = ModuleType("openhands")

    return {
        "llm": mock_llm,
        "agent": mock_agent,
        "conversation": mock_conversation,
        "llm_class": mock_llm_class,
        "agent_class": mock_agent_class,
        "conversation_class": mock_conversation_class,
    }


@pytest.fixture
def test_workspace(tmp_path):
    """Provide a temporary workspace directory for tests."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace
