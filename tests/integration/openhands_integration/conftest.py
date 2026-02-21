"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands_integration/Conftest]]
Pytest fixtures for OpenHands integration tests.

Provides:
- Mock OpenHands SDK components
- Test configurations
- Temporary workspaces
- Mock API responses
- Docker runtime fixtures
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from src.agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
)


@pytest.fixture
def test_api_key() -> str:
    """Test API key for OpenRouter."""
    return os.getenv("OPENROUTER_API_KEY", "test-api-key-12345")


@pytest.fixture
def test_workspace(tmp_path: Path) -> Path:
    """Create temporary workspace for tests."""
    workspace = tmp_path / "openhands_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def openhands_config(test_api_key: str, test_workspace: Path) -> OpenHandsConfig:
    """Create test OpenHandsConfig."""
    return OpenHandsConfig(
        api_key=SecretStr(test_api_key),
        model="deepseek/deepseek-v3:free",
        base_url="https://openrouter.ai/api/v1",
        workspace_path=test_workspace,
        timeout_seconds=60.0,
    )


@pytest.fixture
def integration_config(
    test_api_key: str, test_workspace: Path
) -> OpenHandsIntegrationConfig:
    """Create test OpenHandsIntegrationConfig."""
    return OpenHandsIntegrationConfig(
        api_key=SecretStr(test_api_key),
        model_preset="deepseek-v3",
        workspace_root=test_workspace,
        default_timeout_seconds=60.0,
        enable_real_agent=False,  # Disable real agent for tests
        fallback_to_mock=True,
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
    return conversation


@pytest.fixture
def mock_openhands_sdk(
    monkeypatch: pytest.MonkeyPatch,
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

    # Mock get_default_agent function
    mock_get_default_agent = MagicMock(return_value=mock_agent)

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

    # Mock openhands.tools.preset.default module
    openhands_tools = ModuleType("openhands.tools")
    openhands_tools_preset = ModuleType("openhands.tools.preset")
    openhands_tools_preset_default = ModuleType("openhands.tools.preset.default")
    openhands_tools_preset_default.get_default_agent = mock_get_default_agent

    sys.modules["openhands"] = ModuleType("openhands")
    sys.modules["openhands.tools"] = openhands_tools
    sys.modules["openhands.tools.preset"] = openhands_tools_preset
    sys.modules["openhands.tools.preset.default"] = openhands_tools_preset_default

    return {
        "llm": mock_llm,
        "agent": mock_agent,
        "conversation": mock_conversation,
        "llm_class": mock_llm_class,
        "agent_class": mock_agent_class,
        "get_default_agent": mock_get_default_agent,
        "conversation_class": mock_conversation_class,
    }


@pytest.fixture
def mock_circuit_breaker() -> AsyncMock:
    """Mock circuit breaker."""
    circuit_breaker = AsyncMock()
    circuit_breaker.execute = AsyncMock(
        side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)
    )
    return circuit_breaker


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    """Mock event publisher."""
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def mock_agent_registry() -> MagicMock:
    """Mock agent registry."""
    registry = MagicMock()
    registry.register = MagicMock()
    return registry
