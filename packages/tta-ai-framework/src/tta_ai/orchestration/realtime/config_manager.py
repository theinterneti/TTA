"""
Real-time configuration management for WebSocket and event systems.

This module provides dynamic configuration management for real-time features,
including validation, feature flags, and environment-based controls.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RealtimeEnvironment(str, Enum):
    """Environment types for real-time configuration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class WebSocketConfig:
    """WebSocket-specific configuration."""

    enabled: bool = False
    path: str = "/ws"
    heartbeat_interval: float = 30.0
    connection_timeout: float = 60.0
    max_connections: int = 1000
    auth_required: bool = True
    cors_origins: list[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class EventConfig:
    """Event broadcasting configuration."""

    enabled: bool = False
    redis_channel_prefix: str = "ao:events"
    buffer_size: int = 1000
    broadcast_agent_status: bool = True
    broadcast_workflow_progress: bool = True
    broadcast_system_metrics: bool = False
    event_retention_hours: int = 24


@dataclass
class ProgressiveFeedbackConfig:
    """Progressive feedback configuration."""

    enabled: bool = False
    update_interval: float = 1.0
    max_updates_per_workflow: int = 100
    stream_intermediate_results: bool = True
    batch_updates: bool = True
    batch_size: int = 10


@dataclass
class OptimizationConfig:
    """Performance optimization configuration."""

    enabled: bool = False
    response_time_monitoring: bool = True
    statistical_analysis: bool = True
    auto_parameter_adjustment: bool = False
    speed_creativity_balance: float = 0.5


@dataclass
class RealtimeConfig:
    """Complete real-time configuration."""

    enabled: bool = False
    environment: RealtimeEnvironment = RealtimeEnvironment.DEVELOPMENT
    websocket: WebSocketConfig = None
    events: EventConfig = None
    progressive_feedback: ProgressiveFeedbackConfig = None
    optimization: OptimizationConfig = None

    def __post_init__(self):
        if self.websocket is None:
            self.websocket = WebSocketConfig()
        if self.events is None:
            self.events = EventConfig()
        if self.progressive_feedback is None:
            self.progressive_feedback = ProgressiveFeedbackConfig()
        if self.optimization is None:
            self.optimization = OptimizationConfig()


class RealtimeConfigManager:
    """Manager for real-time configuration with validation and feature flags."""

    def __init__(self, base_config: dict[str, Any] | None = None):
        self.base_config = base_config or {}
        self._config: RealtimeConfig | None = None
        self._feature_flags: dict[str, bool] = {}
        self._environment = self._detect_environment()

    def _detect_environment(self) -> RealtimeEnvironment:
        """Detect the current environment."""
        env_name = os.getenv("TTA_ENVIRONMENT", "development").lower()

        try:
            return RealtimeEnvironment(env_name)
        except ValueError:
            logger.warning(
                f"Unknown environment '{env_name}', defaulting to development"
            )
            return RealtimeEnvironment.DEVELOPMENT

    def load_config(self) -> RealtimeConfig:
        """Load and validate real-time configuration."""
        if self._config is not None:
            return self._config

        # Extract real-time config from base config
        realtime_config = self.base_config.get("agent_orchestration", {}).get(
            "realtime", {}
        )

        # Create configuration with environment-specific defaults
        config = RealtimeConfig(
            enabled=self._get_bool_config(
                "enabled", realtime_config, self._get_default_enabled()
            ),
            environment=self._environment,
            websocket=self._load_websocket_config(realtime_config.get("websocket", {})),
            events=self._load_event_config(realtime_config.get("events", {})),
            progressive_feedback=self._load_progressive_feedback_config(
                realtime_config.get("progressive_feedback", {})
            ),
            optimization=self._load_optimization_config(
                realtime_config.get("optimization", {})
            ),
        )

        # Validate configuration
        self._validate_config(config)

        # Apply feature flags
        self._apply_feature_flags(config)

        self._config = config
        logger.info(
            f"Real-time configuration loaded for environment: {self._environment}"
        )
        return config

    def _get_default_enabled(self) -> bool:
        """Get default enabled state based on environment."""
        if self._environment in [
            RealtimeEnvironment.DEVELOPMENT,
            RealtimeEnvironment.TESTING,
        ]:
            return True  # Enable by default in dev/test
        return False  # Disabled by default in staging/production

    def _load_websocket_config(self, ws_config: dict[str, Any]) -> WebSocketConfig:
        """Load WebSocket configuration."""
        return WebSocketConfig(
            enabled=self._get_bool_config(
                "enabled", ws_config, self._get_default_enabled()
            ),
            path=ws_config.get("path", "/ws"),
            heartbeat_interval=float(ws_config.get("heartbeat_interval", 30.0)),
            connection_timeout=float(ws_config.get("connection_timeout", 60.0)),
            max_connections=int(ws_config.get("max_connections", 1000)),
            auth_required=self._get_bool_config("auth_required", ws_config, True),
            cors_origins=ws_config.get("cors_origins", ["*"]),
        )

    def _load_event_config(self, event_config: dict[str, Any]) -> EventConfig:
        """Load event configuration."""
        return EventConfig(
            enabled=self._get_bool_config(
                "enabled", event_config, self._get_default_enabled()
            ),
            redis_channel_prefix=event_config.get("redis_channel_prefix", "ao:events"),
            buffer_size=int(event_config.get("buffer_size", 1000)),
            broadcast_agent_status=self._get_bool_config(
                "broadcast_agent_status", event_config, True
            ),
            broadcast_workflow_progress=self._get_bool_config(
                "broadcast_workflow_progress", event_config, True
            ),
            broadcast_system_metrics=self._get_bool_config(
                "broadcast_system_metrics", event_config, False
            ),
            event_retention_hours=int(event_config.get("event_retention_hours", 24)),
        )

    def _load_progressive_feedback_config(
        self, pf_config: dict[str, Any]
    ) -> ProgressiveFeedbackConfig:
        """Load progressive feedback configuration."""
        return ProgressiveFeedbackConfig(
            enabled=self._get_bool_config(
                "enabled", pf_config, self._get_default_enabled()
            ),
            update_interval=float(pf_config.get("update_interval", 1.0)),
            max_updates_per_workflow=int(
                pf_config.get("max_updates_per_workflow", 100)
            ),
            stream_intermediate_results=self._get_bool_config(
                "stream_intermediate_results", pf_config, True
            ),
            batch_updates=self._get_bool_config("batch_updates", pf_config, True),
            batch_size=int(pf_config.get("batch_size", 10)),
        )

    def _load_optimization_config(
        self, opt_config: dict[str, Any]
    ) -> OptimizationConfig:
        """Load optimization configuration."""
        return OptimizationConfig(
            enabled=self._get_bool_config("enabled", opt_config, False),
            response_time_monitoring=self._get_bool_config(
                "response_time_monitoring", opt_config, True
            ),
            statistical_analysis=self._get_bool_config(
                "statistical_analysis", opt_config, True
            ),
            auto_parameter_adjustment=self._get_bool_config(
                "auto_parameter_adjustment", opt_config, False
            ),
            speed_creativity_balance=float(
                opt_config.get("speed_creativity_balance", 0.5)
            ),
        )

    def _get_bool_config(self, key: str, config: dict[str, Any], default: bool) -> bool:
        """Get boolean configuration value with environment variable override."""
        # Check environment variable first
        env_key = f"TTA_REALTIME_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes", "on")

        # Fall back to config value
        return config.get(key, default)

    def _validate_config(self, config: RealtimeConfig) -> None:
        """Validate configuration consistency."""
        errors = []

        # WebSocket validation
        if config.websocket.enabled and config.websocket.heartbeat_interval <= 0:
            errors.append("WebSocket heartbeat_interval must be positive")

        if config.websocket.enabled and config.websocket.connection_timeout <= 0:
            errors.append("WebSocket connection_timeout must be positive")

        if config.websocket.enabled and config.websocket.max_connections <= 0:
            errors.append("WebSocket max_connections must be positive")

        # Event validation
        if config.events.enabled and config.events.buffer_size <= 0:
            errors.append("Event buffer_size must be positive")

        if config.events.enabled and config.events.event_retention_hours <= 0:
            errors.append("Event retention_hours must be positive")

        # Progressive feedback validation
        if (
            config.progressive_feedback.enabled
            and config.progressive_feedback.update_interval <= 0
        ):
            errors.append("Progressive feedback update_interval must be positive")

        if (
            config.progressive_feedback.enabled
            and config.progressive_feedback.max_updates_per_workflow <= 0
        ):
            errors.append(
                "Progressive feedback max_updates_per_workflow must be positive"
            )

        # Optimization validation
        if config.optimization.enabled:
            if not (0.0 <= config.optimization.speed_creativity_balance <= 1.0):
                errors.append(
                    "Optimization speed_creativity_balance must be between 0.0 and 1.0"
                )

        # Dependency validation
        if config.websocket.enabled and not config.events.enabled:
            logger.warning(
                "WebSocket enabled but events disabled - limited functionality"
            )

        if config.progressive_feedback.enabled and not config.events.enabled:
            errors.append("Progressive feedback requires events to be enabled")

        if errors:
            error_msg = "Configuration validation failed: " + "; ".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _apply_feature_flags(self, config: RealtimeConfig) -> None:
        """Apply feature flags to configuration."""
        # Apply global feature flags
        for flag_name, flag_value in self._feature_flags.items():
            if flag_name == "realtime_disabled" and flag_value:
                config.enabled = False
                config.websocket.enabled = False
                config.events.enabled = False
                config.progressive_feedback.enabled = False
                config.optimization.enabled = False
                logger.info("Real-time features disabled by feature flag")

    def set_feature_flag(self, flag_name: str, enabled: bool) -> None:
        """Set a feature flag."""
        self._feature_flags[flag_name] = enabled
        self._config = None  # Force reload on next access
        logger.info(f"Feature flag '{flag_name}' set to {enabled}")

    def get_config(self) -> RealtimeConfig:
        """Get the current configuration."""
        return self.load_config()

    def reload_config(self) -> RealtimeConfig:
        """Reload configuration from base config."""
        self._config = None
        return self.load_config()

    def is_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        config = self.get_config()

        if feature == "realtime":
            return config.enabled
        if feature == "websocket":
            return config.enabled and config.websocket.enabled
        if feature == "events":
            return config.enabled and config.events.enabled
        if feature == "progressive_feedback":
            return config.enabled and config.progressive_feedback.enabled
        if feature == "optimization":
            return config.enabled and config.optimization.enabled
        return False

    def get_environment(self) -> RealtimeEnvironment:
        """Get the current environment."""
        return self._environment


# Global configuration manager instance
_config_manager: RealtimeConfigManager | None = None


def get_realtime_config_manager(
    base_config: dict[str, Any] | None = None,
) -> RealtimeConfigManager:
    """Get the global real-time configuration manager."""
    global _config_manager
    if _config_manager is None or base_config is not None:
        _config_manager = RealtimeConfigManager(base_config)
    return _config_manager


def get_realtime_config(base_config: dict[str, Any] | None = None) -> RealtimeConfig:
    """Get the current real-time configuration."""
    return get_realtime_config_manager(base_config).get_config()
