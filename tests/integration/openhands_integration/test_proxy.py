"""
Tests for OpenHandsAgentProxy.

Tests proxy initialization, agent registration, task execution,
event integration, circuit breaker protection, and capability advertisement.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from src.agent_orchestration.openhands_integration.proxy import OpenHandsAgentProxy


class TestProxyInitialization:
    """Tests for proxy initialization."""

    def test_proxy_initialization_with_config(
        self,
        integration_config: OpenHandsIntegrationConfig,
        mock_agent_registry: MagicMock,
    ):
        """Test proxy initialization with provided config."""
        proxy = OpenHandsAgentProxy(
            instance="test-1",
            openhands_config=integration_config,
            agent_registry=mock_agent_registry,
            enable_real_agent=False,
        )

        assert proxy.agent_id.instance == "test-1"
        assert proxy.name == "openhands:test-1"
        assert proxy.enable_real_agent is False
        assert proxy.openhands_config == integration_config

        # Verify registration was attempted
        mock_agent_registry.register.assert_called_once_with(proxy)

    def test_proxy_initialization_without_config(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Test proxy initialization without config (loads from env)."""
        # Set a test API key in the environment
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key-12345")
        # Disable real agent for testing
        monkeypatch.setenv("OPENHANDS_ENABLE_REAL_AGENT", "false")

        proxy = OpenHandsAgentProxy(instance="test-2")

        # Should use config loaded from environment
        assert proxy.openhands_config.api_key.get_secret_value() == "test-api-key-12345"
        assert proxy.enable_real_agent is False

    def test_proxy_initialization_with_real_agent(
        self, integration_config: OpenHandsIntegrationConfig
    ):
        """Test proxy initialization with real agent enabled."""
        integration_config.enable_real_agent = True

        proxy = OpenHandsAgentProxy(
            instance="test-3",
            openhands_config=integration_config,
            enable_real_agent=True,
        )

        assert proxy.enable_real_agent is True
        assert proxy.adapter is not None

    def test_proxy_initialization_with_event_publisher(
        self, integration_config: OpenHandsIntegrationConfig, mock_event_publisher
    ):
        """Test proxy initialization with event publisher."""
        # Event publisher is passed as parameter
        proxy = OpenHandsAgentProxy(
            instance="test-4",
            openhands_config=integration_config,
            event_publisher=mock_event_publisher,
            enable_real_agent=False,
        )

        assert proxy.openhands_config == integration_config
        assert proxy.enable_real_agent is False


class TestTaskExecution:
    """Tests for task execution."""

    @pytest.mark.asyncio
    async def test_execute_development_task_mock(
        self, integration_config: OpenHandsIntegrationConfig
    ):
        """Test task execution with mock (real agent disabled)."""
        proxy = OpenHandsAgentProxy(
            instance="test-5",
            openhands_config=integration_config,
            enable_real_agent=False,
        )

        result = await proxy.execute_development_task("Write a Python function")

        assert result["success"] is True
        assert "MOCK" in result["output"]
        assert result["metadata"]["mock"] is True

    @pytest.mark.asyncio
    async def test_execute_development_task_with_adapter(
        self, integration_config: OpenHandsIntegrationConfig, mock_openhands_sdk
    ):
        """Test task execution with real adapter."""
        integration_config.enable_real_agent = True

        with patch(
            "src.agent_orchestration.openhands_integration.proxy.OpenHandsClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch(
                "src.agent_orchestration.openhands_integration.proxy.OpenHandsAdapter"
            ) as mock_adapter_class:
                mock_adapter = AsyncMock()
                mock_adapter.execute_development_task = AsyncMock(
                    return_value={
                        "success": True,
                        "output": "def add(a, b): return a + b",
                        "error": None,
                        "execution_time": 1.5,
                        "metadata": {},
                    }
                )
                mock_adapter_class.return_value = mock_adapter

                proxy = OpenHandsAgentProxy(
                    instance="test-6",
                    openhands_config=integration_config,
                    enable_real_agent=True,
                )

                result = await proxy.execute_development_task("Write a Python function")

                assert result["success"] is True
                assert "def add" in result["output"]
                mock_adapter.execute_development_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_development_task_with_circuit_breaker(
        self, integration_config: OpenHandsIntegrationConfig, mock_circuit_breaker
    ):
        """Test task execution with circuit breaker."""
        integration_config.enable_real_agent = True

        with patch(
            "src.agent_orchestration.openhands_integration.proxy.OpenHandsClient"
        ):
            with patch(
                "src.agent_orchestration.openhands_integration.proxy.OpenHandsAdapter"
            ) as mock_adapter_class:
                mock_adapter = AsyncMock()
                mock_adapter.execute_development_task = AsyncMock(
                    return_value={"success": True, "output": "result"}
                )
                mock_adapter_class.return_value = mock_adapter

                proxy = OpenHandsAgentProxy(
                    instance="test-7",
                    openhands_config=integration_config,
                    enable_real_agent=True,
                    circuit_breaker=mock_circuit_breaker,
                )

                await proxy.execute_development_task("Write a Python function")

                # Verify circuit breaker was used
                mock_circuit_breaker.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_development_task_with_events(
        self, integration_config: OpenHandsIntegrationConfig
    ):
        """Test task execution with event publishing."""
        integration_config.enable_real_agent = True

        mock_event_integrator = AsyncMock()

        with patch(
            "src.agent_orchestration.openhands_integration.proxy.OpenHandsClient"
        ):
            with patch(
                "src.agent_orchestration.openhands_integration.proxy.OpenHandsAdapter"
            ) as mock_adapter_class:
                mock_adapter = AsyncMock()
                mock_adapter.execute_development_task = AsyncMock(
                    return_value={"success": True, "output": "result"}
                )
                mock_adapter_class.return_value = mock_adapter

                proxy = OpenHandsAgentProxy(
                    instance="test-8",
                    openhands_config=integration_config,
                    enable_real_agent=True,
                    event_publisher=mock_event_integrator,
                )

                await proxy.execute_development_task("Write a Python function")

                # Verify adapter was called
                assert mock_adapter.execute_development_task.called


class TestCapabilities:
    """Tests for capability advertisement."""

    @pytest.mark.asyncio
    async def test_get_capabilities(
        self, integration_config: OpenHandsIntegrationConfig
    ):
        """Test capability advertisement."""
        proxy = OpenHandsAgentProxy(
            instance="test-9",
            openhands_config=integration_config,
            enable_real_agent=False,
        )

        capabilities = await proxy.get_capabilities()

        assert capabilities["agent_type"] == "OPENHANDS"
        assert "code_generation" in capabilities["capabilities"]
        assert "code_debugging" in capabilities["capabilities"]
        assert "file_editing" in capabilities["capabilities"]
        assert "python" in capabilities["supported_languages"]
        assert "javascript" in capabilities["supported_languages"]
        assert capabilities["timeout_seconds"] == proxy._default_timeout_s

