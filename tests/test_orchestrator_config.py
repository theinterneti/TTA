"""

# Logseq: [[TTA.dev/Tests/Test_orchestrator_config]]
Tests for TTAConfig configuration management.

This module tests the TTAConfig class to achieve comprehensive coverage
of configuration loading, getting, setting, and saving functionality.
"""

import json

import pytest
import yaml

from src.orchestration.config import TTAConfig


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset TTAConfig singleton before each test."""
    # Patch the singleton decorator to return the class directly
    # This allows each test to create a fresh instance
    from src.orchestration import decorators

    original_singleton = decorators.singleton

    # Replace singleton with a pass-through decorator
    decorators.singleton = lambda cls: cls

    # Reload TTAConfig to apply the patched decorator
    import importlib

    from src.orchestration import config

    importlib.reload(config)

    yield

    # Restore original singleton decorator
    decorators.singleton = original_singleton
    importlib.reload(config)


class TestTTAConfigLoading:
    """Test suite for TTAConfig loading functionality."""

    def test_init_with_default_path(self, tmp_path, monkeypatch):
        """Test TTAConfig initialization with default config path."""
        # Change to tmp directory to avoid loading real config
        monkeypatch.chdir(tmp_path)

        # Create config directory and file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "tta_config.yaml"

        # Write minimal config
        config_data = {"tta.dev": {"enabled": True}}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create TTAConfig (should use default path)
        # Note: Due to singleton, we need to clear the instance
        TTAConfig._instances = {}
        config = TTAConfig()

        assert config.config is not None
        assert isinstance(config.config, dict)

    def test_init_with_custom_path_yaml(self, tmp_path):
        """Test TTAConfig initialization with custom YAML path."""
        config_file = tmp_path / "custom_config.yaml"
        config_data = {
            "tta.dev": {"enabled": True},
            "tta.prototype": {"enabled": False},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Verify config was loaded from file
        assert "tta.dev" in config.config
        assert config.config["tta.dev"]["enabled"] is True
        assert config.config["tta.prototype"]["enabled"] is False

    def test_init_with_custom_path_json(self, tmp_path):
        """Test TTAConfig initialization with custom JSON path."""
        config_file = tmp_path / "custom_config.json"
        config_data = {"tta.dev": {"enabled": True}, "docker": {"enabled": False}}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Verify config was loaded from file
        assert "tta.dev" in config.config
        assert config.config["tta.dev"]["enabled"] is True
        assert config.config["docker"]["enabled"] is False

    def test_load_config_missing_file(self, tmp_path):
        """Test loading config when file doesn't exist (should use defaults)."""
        config_file = tmp_path / "nonexistent.yaml"

        TTAConfig._instances = {}
        config = TTAConfig(config_path=config_file)

        # Should have default config
        assert config.config is not None
        assert "tta.dev" in config.config
        assert "tta.prototype" in config.config

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading config with invalid YAML (should use defaults)."""
        config_file = tmp_path / "invalid.yaml"

        # Write invalid YAML
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content: [")

        TTAConfig._instances = {}
        config = TTAConfig(config_path=config_file)

        # Should fall back to default config
        assert config.config is not None

    def test_load_config_invalid_json(self, tmp_path):
        """Test loading config with invalid JSON (should use defaults)."""
        config_file = tmp_path / "invalid.json"

        # Write invalid JSON
        with open(config_file, "w") as f:
            f.write('{"invalid": json}')

        TTAConfig._instances = {}
        config = TTAConfig(config_path=config_file)

        # Should fall back to default config
        assert config.config is not None

    def test_get_default_config(self, tmp_path):
        """Test _get_default_config returns complete default configuration."""
        config_file = tmp_path / "test.yaml"

        TTAConfig._instances = {}
        config = TTAConfig(config_path=config_file)

        default_config = config._get_default_config()

        # Verify default config structure
        assert "tta.dev" in default_config
        assert "tta.prototype" in default_config
        assert "agent_orchestration" in default_config
        assert "docker" in default_config
        assert "carbon" in default_config
        assert "environment" in default_config

        # Verify nested structure
        assert "components" in default_config["tta.dev"]
        assert "neo4j" in default_config["tta.dev"]["components"]


class TestTTAConfigGetSet:
    """Test suite for TTAConfig get/set functionality."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a TTAConfig instance for testing."""
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            "tta.dev": {
                "enabled": True,
                "components": {"neo4j": {"enabled": True, "port": 7687}},
            },
            "docker": {"enabled": False},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        return TTAConfig(config_path=config_file)

    def test_get_simple_key(self, config):
        """Test getting a simple configuration key."""
        assert config.get("docker.enabled") is False

    def test_get_nested_key(self, config):
        """Test getting a nested configuration key."""
        assert config.get("tta.dev.components.neo4j.port") == 7687

    def test_get_compound_repository_key(self, config):
        """Test getting a compound repository key (tta.dev, tta.prototype)."""
        assert config.get("tta.dev.enabled") is True

    def test_get_missing_key_with_default(self, config):
        """Test getting a missing key returns default value."""
        assert config.get("nonexistent.key", "default_value") == "default_value"

    def test_get_missing_key_without_default(self, config):
        """Test getting a missing key without default returns None."""
        assert config.get("nonexistent.key") is None

    def test_set_simple_key(self, config):
        """Test setting a simple configuration key."""
        config.set("docker.enabled", True)
        assert config.get("docker.enabled") is True

    def test_set_nested_key(self, config):
        """Test setting a nested configuration key."""
        config.set("tta.dev.components.neo4j.port", 7688)
        assert config.get("tta.dev.components.neo4j.port") == 7688

    def test_set_new_key(self, config):
        """Test setting a new configuration key."""
        config.set("new.section.key", "value")
        assert config.get("new.section.key") == "value"

    def test_set_creates_nested_structure(self, config):
        """Test that set creates nested dictionaries as needed."""
        config.set("deeply.nested.new.key", 42)
        assert config.get("deeply.nested.new.key") == 42


class TestTTAConfigSave:
    """Test suite for TTAConfig save functionality."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a TTAConfig instance for testing."""
        config_file = tmp_path / "test_config.yaml"
        config_data = {"tta.dev": {"enabled": True}}

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        TTAConfig._instances = {}
        return TTAConfig(config_path=config_file)

    def test_save_to_yaml(self, config, tmp_path):
        """Test saving configuration to YAML file."""
        save_path = tmp_path / "saved_config.yaml"

        config.set("docker.enabled", True)
        result = config.save(path=save_path)

        assert result is True
        assert save_path.exists()

        # Verify saved content
        with open(save_path) as f:
            saved_data = yaml.safe_load(f)

        assert saved_data["docker"]["enabled"] is True

    def test_save_to_json(self, config, tmp_path):
        """Test saving configuration to JSON file."""
        save_path = tmp_path / "saved_config.json"

        config.set("docker.enabled", True)
        result = config.save(path=save_path)

        assert result is True
        assert save_path.exists()

        # Verify saved content
        with open(save_path) as f:
            saved_data = json.load(f)

        assert saved_data["docker"]["enabled"] is True

    def test_save_creates_parent_directories(self, config, tmp_path):
        """Test that save creates parent directories if they don't exist."""
        save_path = tmp_path / "nested" / "dir" / "config.yaml"

        result = config.save(path=save_path)

        assert result is True
        assert save_path.exists()
        assert save_path.parent.exists()

    def test_save_to_default_path(self, config):
        """Test saving to default config path (no path argument)."""
        result = config.save()

        assert result is True
        assert config.config_path.exists()

    def test_save_with_io_error(self, config, tmp_path):
        """Test save handles I/O errors gracefully."""
        # Try to save to a read-only location
        save_path = tmp_path / "readonly" / "config.yaml"
        save_path.parent.mkdir()
        save_path.parent.chmod(0o444)  # Read-only

        try:
            result = config.save(path=save_path)
            # Should return False on error
            assert result is False
        finally:
            # Restore permissions for cleanup
            save_path.parent.chmod(0o755)


class TestTTAConfigEnvironmentVariables:
    """Test suite for environment variable loading."""

    def test_load_env_vars_boolean_true(self, tmp_path, monkeypatch):
        """Test loading boolean true from environment variable."""
        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"docker": {"enabled": False}}, f)

        monkeypatch.setenv("TTA_DOCKER_ENABLED", "true")

        TTAConfig._instances = {}
        config = TTAConfig(config_path=config_file)

        assert config.get("docker.enabled") is True

    def test_load_env_vars_boolean_false(self, tmp_path, monkeypatch):
        """Test loading boolean false from environment variable."""
        # Set env var BEFORE creating config
        monkeypatch.setenv("TTA_DOCKER_ENABLED", "false")

        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"docker": {"enabled": True}}, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Env var should override file config
        assert config.config["docker"]["enabled"] is False

    def test_load_env_vars_integer(self, tmp_path, monkeypatch):
        """Test loading integer from environment variable."""
        # Set env var BEFORE creating config
        monkeypatch.setenv("TTA_TTADEV_COMPONENTS_NEO4J_PORT", "7688")

        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"tta.dev": {"components": {"neo4j": {"port": 7687}}}}, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Env var should override file config
        assert config.config["tta.dev"]["components"]["neo4j"]["port"] == 7688

    def test_load_env_vars_float(self, tmp_path, monkeypatch):
        """Test loading float from environment variable."""
        # Set env var BEFORE creating config
        monkeypatch.setenv("TTA_TEST_VALUE", "2.5")

        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"test": {"value": 1.0}}, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Env var should override file config
        assert config.config["test"]["value"] == 2.5

    def test_load_env_vars_string(self, tmp_path, monkeypatch):
        """Test loading string from environment variable."""
        # Set env var BEFORE creating config
        monkeypatch.setenv("TTA_ENVIRONMENT_NAME", "production")

        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"environment": {"name": "development"}}, f)

        # Clear singleton instances
        if hasattr(TTAConfig, "_instances"):
            TTAConfig._instances.clear()

        config = TTAConfig(config_path=config_file)

        # Env var should override file config
        assert config.config["environment"]["name"] == "production"


class TestTTAConfigSingleton:
    """Test suite for singleton pattern behavior."""

    def test_singleton_returns_same_instance(self, tmp_path):
        """Test that TTAConfig returns the same instance (singleton pattern)."""
        config_file = tmp_path / "test.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"test": "value"}, f)

        TTAConfig._instances = {}
        config1 = TTAConfig(config_path=config_file)
        config2 = TTAConfig(config_path=config_file)

        assert config1 is config2
