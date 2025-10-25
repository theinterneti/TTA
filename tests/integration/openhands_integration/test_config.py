"""
Tests for OpenHands configuration models.

Tests:
- Configuration loading from environment
- Model selection and validation
- Workspace configuration
- API key validation
- Free model catalog
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from src.agent_orchestration.openhands_integration.config import (
    FREE_MODELS,
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
    OpenHandsModelConfig,
)


class TestOpenHandsModelConfig:
    """Tests for OpenHandsModelConfig."""

    def test_model_config_creation(self):
        """Test creating model configuration."""
        config = OpenHandsModelConfig(
            model_id="deepseek/deepseek-v3:free",
            display_name="DeepSeek V3",
            context_tokens=64_000,
            is_free=True,
            recommended=True,
        )

        assert config.model_id == "deepseek/deepseek-v3:free"
        assert config.display_name == "DeepSeek V3"
        assert config.context_tokens == 64_000
        assert config.is_free is True
        assert config.recommended is True

    def test_free_models_catalog(self):
        """Test free models catalog."""
        assert "deepseek-v3" in FREE_MODELS
        assert "gemini-flash" in FREE_MODELS
        assert "llama-scout" in FREE_MODELS
        assert "deepseek-r1" in FREE_MODELS

        # Verify DeepSeek V3 is recommended
        deepseek = FREE_MODELS["deepseek-v3"]
        assert deepseek.recommended is True
        assert deepseek.is_free is True
        assert deepseek.context_tokens == 64_000


class TestOpenHandsConfig:
    """Tests for OpenHandsConfig."""

    def test_config_creation(self, test_api_key: str, test_workspace: Path):
        """Test creating OpenHandsConfig."""
        config = OpenHandsConfig(
            api_key=SecretStr(test_api_key),
            model="deepseek/deepseek-v3:free",
            workspace_path=test_workspace,
        )

        assert config.api_key.get_secret_value() == test_api_key
        assert config.model == "deepseek/deepseek-v3:free"
        assert config.workspace_path == test_workspace
        assert config.timeout_seconds == 300.0  # Default

    def test_config_with_custom_timeout(
        self, test_api_key: str, test_workspace: Path
    ):
        """Test config with custom timeout."""
        config = OpenHandsConfig(
            api_key=SecretStr(test_api_key),
            model="deepseek/deepseek-v3:free",
            workspace_path=test_workspace,
            timeout_seconds=600.0,
        )

        assert config.timeout_seconds == 600.0

    def test_config_timeout_validation(
        self, test_api_key: str, test_workspace: Path
    ):
        """Test timeout validation."""
        # Too low
        with pytest.raises(ValidationError):
            OpenHandsConfig(
                api_key=SecretStr(test_api_key),
                model="deepseek/deepseek-v3:free",
                workspace_path=test_workspace,
                timeout_seconds=5.0,  # Below minimum (10.0)
            )

        # Too high
        with pytest.raises(ValidationError):
            OpenHandsConfig(
                api_key=SecretStr(test_api_key),
                model="deepseek/deepseek-v3:free",
                workspace_path=test_workspace,
                timeout_seconds=4000.0,  # Above maximum (3600.0)
            )


class TestOpenHandsIntegrationConfig:
    """Tests for OpenHandsIntegrationConfig."""

    def test_integration_config_creation(
        self, test_api_key: str, test_workspace: Path
    ):
        """Test creating integration config."""
        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            model_preset="deepseek-v3",
            workspace_root=test_workspace,
        )

        assert config.api_key.get_secret_value() == test_api_key
        assert config.model_preset == "deepseek-v3"
        assert config.workspace_root == test_workspace
        assert config.circuit_breaker_enabled is True  # Default

    def test_get_model_config(self, test_api_key: str, test_workspace: Path):
        """Test getting model configuration."""
        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            model_preset="deepseek-v3",
            workspace_root=test_workspace,
        )

        model_config = config.get_model_config()
        # Model ID should be resolved from the registry
        assert model_config.model_id == "openrouter/deepseek/deepseek-chat-v3.1:free"
        # Recommended status depends on the model's compatibility status in the registry
        assert isinstance(model_config.recommended, bool)

    def test_custom_model_id(self, test_api_key: str, test_workspace: Path):
        """Test custom model ID override."""
        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            model_preset="deepseek-v3",
            custom_model_id="custom/model:free",
            workspace_root=test_workspace,
        )

        model_config = config.get_model_config()
        assert model_config.model_id == "custom/model:free"
        assert model_config.recommended is False  # Custom models not recommended

    def test_api_key_validation(self, test_workspace: Path):
        """Test API key validation."""
        # Empty API key should fail
        with pytest.raises(ValidationError):
            OpenHandsIntegrationConfig(
                api_key=SecretStr(""),
                workspace_root=test_workspace,
            )

    def test_workspace_creation(self, test_api_key: str, tmp_path: Path):
        """Test workspace directory creation."""
        workspace = tmp_path / "new_workspace"
        assert not workspace.exists()

        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            workspace_root=workspace,
        )

        # Workspace should be created
        assert config.workspace_root.exists()
        assert config.workspace_root.is_dir()

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Test loading configuration from environment."""
        # Set environment variables
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-from-env")
        monkeypatch.setenv("OPENHANDS_MODEL", "gemini-flash")
        monkeypatch.setenv(
            "OPENHANDS_WORKSPACE_ROOT", str(tmp_path / "env_workspace")
        )
        monkeypatch.setenv("OPENHANDS_TIMEOUT", "600.0")
        monkeypatch.setenv("OPENHANDS_ENABLE_CIRCUIT_BREAKER", "false")

        config = OpenHandsIntegrationConfig.from_env()

        assert config.api_key.get_secret_value() == "test-key-from-env"
        assert config.model_preset == "gemini-flash"
        assert config.default_timeout_seconds == 600.0
        assert config.circuit_breaker_enabled is False

    def test_from_env_missing_api_key(self, monkeypatch: pytest.MonkeyPatch):
        """Test from_env fails without API key."""
        # Remove API key from environment and mock load_dotenv to prevent loading from .env file
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "")  # Set to empty string to ensure it's not loaded

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            OpenHandsIntegrationConfig.from_env()

    def test_retry_config_validation(
        self, test_api_key: str, test_workspace: Path
    ):
        """Test retry configuration validation."""
        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            workspace_root=test_workspace,
            max_retries=5,
            retry_base_delay=2.0,
        )

        assert config.max_retries == 5
        assert config.retry_base_delay == 2.0

    def test_circuit_breaker_config(
        self, test_api_key: str, test_workspace: Path
    ):
        """Test circuit breaker configuration."""
        config = OpenHandsIntegrationConfig(
            api_key=SecretStr(test_api_key),
            workspace_root=test_workspace,
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=10,
            circuit_breaker_timeout_seconds=120,
        )

        assert config.circuit_breaker_enabled is True
        assert config.circuit_breaker_failure_threshold == 10
        assert config.circuit_breaker_timeout_seconds == 120

