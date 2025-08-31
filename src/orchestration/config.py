"""
TTA Configuration

This module provides configuration management for the TTA project.

Classes:
    TTAConfig: Configuration manager for the TTA project

Example:
    ```python
    from src.orchestration.config import TTAConfig

    # Create a configuration object
    config = TTAConfig()

    # Get a configuration value
    value = config.get("tta.dev.enabled")

    # Set a configuration value
    config.set("tta.dev.enabled", True)

    # Save the configuration
    config.save()
    ```
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml

from .decorators import log_entry_exit, singleton, timing_decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@singleton
class TTAConfig:
    """
    Configuration manager for the TTA project.

    This class handles loading and managing configuration for both
    tta.dev and tta.prototype components.

    Attributes:
        root_dir: Root directory of the project
        config_path: Path to the configuration file
        config: Configuration dictionary
    """

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize the TTA Configuration.

        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        self.root_dir = Path(__file__).parent.parent.parent

        # Set default config path if not provided
        if config_path is None:
            config_path = self.root_dir / "config" / "tta_config.yaml"
        else:
            config_path = Path(config_path)

        self.config_path = config_path
        self.config: dict[str, Any] = {}

        # Load configuration
        self._load_config()

        # Load environment variables
        self._load_env_vars()

        logger.info(f"Configuration initialized from {self.config_path}")

    @log_entry_exit
    def _load_config(self) -> None:
        """
        Load configuration from the config file.

        This method loads the configuration from the specified file,
        or uses default configuration if the file is not found or invalid.
        """
        if not self.config_path.exists():
            logger.warning(
                f"Config file not found at {self.config_path}. Using default configuration."
            )
            self.config = self._get_default_config()
            return

        try:
            # Determine file format based on extension
            if self.config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(self.config_path) as f:
                    self.config = yaml.safe_load(f) or {}
            elif self.config_path.suffix.lower() == ".json":
                with open(self.config_path) as f:
                    self.config = json.load(f)
            else:
                logger.warning(
                    f"Unsupported config file format: {self.config_path.suffix}"
                )
                self.config = self._get_default_config()
                return

            logger.info(f"Loaded configuration from {self.config_path}")
            # Ensure agent_orchestration block exists for backward compatibility
            self.config.setdefault(
                "agent_orchestration", {"enabled": False, "port": 8503}
            )
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """
        Get the default configuration.

        Returns:
            Dict[str, Any]: Default configuration dictionary
        """
        return {
            "tta.dev": {
                "enabled": True,
                "components": {
                    "neo4j": {
                        "enabled": True,
                        "port": 7687,
                        "username": "neo4j",
                        "password": "password",
                    },
                    "llm": {
                        "enabled": True,
                        "model": "qwen2.5-7b-instruct",
                        "api_base": "http://localhost:1234/v1",
                    },
                },
            },
            "tta.prototype": {
                "enabled": True,
                "components": {
                    "neo4j": {
                        "enabled": True,
                        "port": 7688,
                        "username": "neo4j",
                        "password": "password",
                    },
                    "app": {"enabled": True, "port": 8501},
                },
            },
            "agent_orchestration": {
                "enabled": False,
                "port": 8503,
                "realtime": {
                    "enabled": False,
                    "websocket": {
                        "enabled": False,
                        "path": "/ws",
                        "heartbeat_interval": 30.0,
                        "connection_timeout": 60.0,
                        "max_connections": 1000,
                        "auth_required": True,
                    },
                    "events": {
                        "enabled": False,
                        "redis_channel_prefix": "ao:events",
                        "buffer_size": 1000,
                        "broadcast_agent_status": True,
                        "broadcast_workflow_progress": True,
                        "broadcast_system_metrics": False,
                    },
                    "progressive_feedback": {
                        "enabled": False,
                        "update_interval": 1.0,
                        "max_updates_per_workflow": 100,
                        "stream_intermediate_results": True,
                    },
                    "optimization": {
                        "enabled": False,
                        "response_time_monitoring": True,
                        "statistical_analysis": True,
                        "auto_parameter_adjustment": False,
                        "speed_creativity_balance": 0.5,
                        "optimization_interval": 60.0,
                        "min_data_points": 10,
                    },
                },
            },
            "docker": {
                "enabled": True,
                "use_gpu": False,
                "compose_profiles": ["default"],
                "standardize_container_names": True,
                "ensure_consistent_extensions": True,
                "ensure_consistent_env_vars": True,
                "ensure_consistent_services": True,
            },
            "carbon": {
                "enabled": True,
                "project_name": "TTA",
                "output_dir": "logs/codecarbon",
                "log_level": "info",
                "measurement_interval": 15,
                "track_components": True,
            },
            "environment": {"name": "development", "log_level": "info"},
        }

    @log_entry_exit
    def _load_env_vars(self) -> None:
        """
        Load configuration from environment variables.

        Environment variables override configuration file values.
        The format is TTA_SECTION_KEY=value, e.g., TTA_TTADEV_ENABLED=true
        """
        for key, value in os.environ.items():
            if key.startswith("TTA_"):
                # Parse the key into sections
                parts = key[4:].lower().split("_")

                if len(parts) < 2:
                    continue

                # Convert the value to the appropriate type
                typed_value: Any = value
                if value.lower() in ["true", "yes", "1"]:
                    typed_value = True
                elif value.lower() in ["false", "no", "0"]:
                    typed_value = False
                elif value.isdigit():
                    typed_value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    typed_value = float(value)

                # Update the configuration
                self._set_nested_config(parts, typed_value)
                logger.debug(f"Loaded environment variable {key}={typed_value}")

    def _set_nested_config(self, keys: list[str], value: Any) -> None:
        """
        Set a nested configuration value.

        Args:
            keys: List of keys representing the path in the configuration
            value: Value to set
        """
        config = self.config
        for key in keys[:-1]:
            if key == "ttadev":
                key = "tta.dev"
            elif key == "ttaprototype":
                key = "tta.prototype"

            if key not in config:
                config[key] = {}
            config = config[key]

        last_key = keys[-1]
        if last_key == "ttadev":
            last_key = "tta.dev"
        elif last_key == "ttaprototype":
            last_key = "tta.prototype"

        config[last_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key, can be nested using dots (e.g., "tta.dev.enabled").
                 Supports repository keys that include a dot (e.g., "tta.dev", "tta.prototype").
            default: Default value to return if the key is not found

        Returns:
            Any: Configuration value, or default if not found
        """
        keys = key.split(".")
        value: Any = self.config

        i = 0
        while i < len(keys):
            if not isinstance(value, dict):
                return default

            # Direct key lookup
            k = keys[i]
            if k in value:
                value = value[k]
                i += 1
                continue

            # Support compound repository keys like "tta.dev" or "tta.prototype"
            if i + 1 < len(keys):
                compound = f"{keys[i]}.{keys[i + 1]}"
                if compound in value:
                    value = value[compound]
                    i += 2
                    continue

            # Not found
            return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key, can be nested using dots (e.g., "tta.dev.enabled")
            value: Value to set
        """
        keys = key.split(".")
        self._set_nested_config(keys, value)
        logger.debug(f"Set configuration {key}={value}")

    @timing_decorator
    def save(self, path: str | Path | None = None) -> bool:
        """
        Save the configuration to a file.

        Args:
            path: Path to save the configuration to. If None, uses the current config path.

        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        if path is None:
            path = self.config_path
        else:
            path = Path(path)

        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Determine file format based on extension
            if path.suffix.lower() in [".yaml", ".yml"]:
                with open(path, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif path.suffix.lower() == ".json":
                with open(path, "w") as f:
                    json.dump(self.config, f, indent=2)
            else:
                logger.error(f"Unsupported config file format: {path.suffix}")
                return False

            logger.info(f"Saved configuration to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            return False

    def __str__(self) -> str:
        """
        Get a string representation of the configuration.

        Returns:
            str: String representation of the configuration
        """
        return f"TTAConfig(path={self.config_path})"

    def __repr__(self) -> str:
        """
        Get a string representation of the configuration.

        Returns:
            str: String representation of the configuration
        """
        return self.__str__()

    def validate(self, schema: dict[str, Any] | None = None) -> bool:
        """
        Validate the configuration against a schema.

        Args:
            schema: Schema to validate against. If None, uses a default schema.

        Returns:
            bool: True if the configuration is valid, False otherwise
        """
        if schema is None:
            schema = self._get_default_schema()

        try:
            self._validate_dict(self.config, schema)
            logger.info("Configuration validation successful")
            return True
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def _validate_dict(
        self, config: dict[str, Any], schema: dict[str, Any], path: str = ""
    ) -> None:
        """
        Validate a dictionary against a schema.

        Args:
            config: Dictionary to validate
            schema: Schema to validate against
            path: Path in the configuration for error reporting

        Raises:
            ValueError: If the configuration is invalid
        """
        for key, value_schema in schema.items():
            # Check if the key exists
            if key not in config:
                if value_schema.get("required", False):
                    raise ValueError(f"Required key '{path}.{key}' is missing")
                continue

            value = config[key]

            # Check the type
            expected_type = value_schema.get("type")
            if expected_type is not None:
                if expected_type == "dict" and not isinstance(value, dict):
                    raise ValueError(f"Key '{path}.{key}' must be a dictionary")
                elif expected_type == "list" and not isinstance(value, list):
                    raise ValueError(f"Key '{path}.{key}' must be a list")
                elif expected_type == "str" and not isinstance(value, str):
                    raise ValueError(f"Key '{path}.{key}' must be a string")
                elif expected_type == "int" and not isinstance(value, int):
                    raise ValueError(f"Key '{path}.{key}' must be an integer")
                elif expected_type == "float" and not isinstance(value, (int, float)):
                    raise ValueError(f"Key '{path}.{key}' must be a number")
                elif expected_type == "bool" and not isinstance(value, bool):
                    raise ValueError(f"Key '{path}.{key}' must be a boolean")

            # Check nested schema
            nested_schema = value_schema.get("schema")
            if nested_schema is not None and isinstance(value, dict):
                self._validate_dict(value, nested_schema, f"{path}.{key}")

            # Check enum values
            enum_values = value_schema.get("enum")
            if enum_values is not None and value not in enum_values:
                raise ValueError(f"Key '{path}.{key}' must be one of {enum_values}")

    def _get_default_schema(self) -> dict[str, Any]:
        """
        Get the default schema for configuration validation.

        Returns:
            Dict[str, Any]: Default schema dictionary
        """
        return {
            "tta.dev": {
                "type": "dict",
                "required": True,
                "schema": {
                    "enabled": {"type": "bool", "required": True},
                    "components": {"type": "dict", "required": True},
                },
            },
            "tta.prototype": {
                "type": "dict",
                "required": True,
                "schema": {
                    "enabled": {"type": "bool", "required": True},
                    "components": {"type": "dict", "required": True},
                },
            },
            "agent_orchestration": {
                "type": "dict",
                "required": True,
                "schema": {
                    "enabled": {"type": "bool", "required": True},
                    "port": {"type": "int", "required": True},
                    "realtime": {
                        "type": "dict",
                        "required": False,
                        "schema": {
                            "enabled": {"type": "bool", "required": False},
                            "websocket": {
                                "type": "dict",
                                "required": False,
                                "schema": {
                                    "enabled": {"type": "bool", "required": False},
                                    "path": {"type": "str", "required": False},
                                    "heartbeat_interval": {
                                        "type": "float",
                                        "required": False,
                                    },
                                    "connection_timeout": {
                                        "type": "float",
                                        "required": False,
                                    },
                                    "max_connections": {
                                        "type": "int",
                                        "required": False,
                                    },
                                    "auth_required": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                },
                            },
                            "events": {
                                "type": "dict",
                                "required": False,
                                "schema": {
                                    "enabled": {"type": "bool", "required": False},
                                    "redis_channel_prefix": {
                                        "type": "str",
                                        "required": False,
                                    },
                                    "buffer_size": {"type": "int", "required": False},
                                    "broadcast_agent_status": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                    "broadcast_workflow_progress": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                    "broadcast_system_metrics": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                },
                            },
                            "progressive_feedback": {
                                "type": "dict",
                                "required": False,
                                "schema": {
                                    "enabled": {"type": "bool", "required": False},
                                    "update_interval": {
                                        "type": "float",
                                        "required": False,
                                    },
                                    "max_updates_per_workflow": {
                                        "type": "int",
                                        "required": False,
                                    },
                                    "stream_intermediate_results": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                },
                            },
                            "optimization": {
                                "type": "dict",
                                "required": False,
                                "schema": {
                                    "enabled": {"type": "bool", "required": False},
                                    "response_time_monitoring": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                    "statistical_analysis": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                    "auto_parameter_adjustment": {
                                        "type": "bool",
                                        "required": False,
                                    },
                                    "speed_creativity_balance": {
                                        "type": "float",
                                        "required": False,
                                    },
                                    "optimization_interval": {
                                        "type": "float",
                                        "required": False,
                                    },
                                    "min_data_points": {
                                        "type": "int",
                                        "required": False,
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "docker": {
                "type": "dict",
                "required": True,
                "schema": {
                    "enabled": {"type": "bool", "required": True},
                    "use_gpu": {"type": "bool", "required": True},
                    "compose_profiles": {"type": "list", "required": True},
                    "standardize_container_names": {"type": "bool", "required": True},
                    "ensure_consistent_extensions": {"type": "bool", "required": True},
                    "ensure_consistent_env_vars": {"type": "bool", "required": True},
                    "ensure_consistent_services": {"type": "bool", "required": True},
                },
            },
            "carbon": {
                "type": "dict",
                "required": True,
                "schema": {
                    "enabled": {"type": "bool", "required": True},
                    "project_name": {"type": "str", "required": True},
                    "output_dir": {"type": "str", "required": True},
                    "log_level": {
                        "type": "str",
                        "required": True,
                        "enum": ["debug", "info", "warning", "error", "critical"],
                    },
                    "measurement_interval": {"type": "int", "required": True},
                    "track_components": {"type": "bool", "required": True},
                },
            },
            "environment": {
                "type": "dict",
                "required": True,
                "schema": {
                    "name": {
                        "type": "str",
                        "required": True,
                        "enum": ["development", "production", "testing"],
                    },
                    "log_level": {
                        "type": "str",
                        "required": True,
                        "enum": ["debug", "info", "warning", "error", "critical"],
                    },
                },
            },
        }
