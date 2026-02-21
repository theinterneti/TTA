"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Circuit_breaker_config]]
Circuit breaker configuration schema and validation.

Provides configuration loading, validation, and default value handling
for circuit breaker settings in the agent orchestration system.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .circuit_breaker import CircuitBreakerConfig

logger = logging.getLogger(__name__)


class CircuitBreakerConfigSchema(BaseModel):
    """Pydantic schema for circuit breaker configuration validation."""

    enabled: bool = Field(default=True, description="Enable circuit breaker functionality")
    failure_threshold: int = Field(
        default=5, ge=1, le=100, description="Number of failures before opening circuit"
    )
    timeout_seconds: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="Timeout before transitioning from OPEN to HALF_OPEN",
    )
    recovery_timeout_seconds: int = Field(
        default=300, ge=1, le=7200, description="Maximum time to wait for recovery"
    )
    half_open_max_calls: int = Field(
        default=3, ge=1, le=20, description="Maximum calls allowed in HALF_OPEN state"
    )
    success_threshold: int = Field(
        default=2, ge=1, le=10, description="Successful calls needed to close circuit"
    )

    @field_validator("success_threshold")
    @classmethod
    def success_threshold_must_be_less_than_half_open_max_calls(cls, v, info):
        """Ensure success threshold is reasonable compared to half-open max calls."""
        if info.data:
            half_open_max = info.data.get("half_open_max_calls", 3)
            if v > half_open_max:
                raise ValueError(
                    f"success_threshold ({v}) must be <= half_open_max_calls ({half_open_max})"
                )
        return v

    @field_validator("recovery_timeout_seconds")
    @classmethod
    def recovery_timeout_must_be_greater_than_timeout(cls, v, info):
        """Ensure recovery timeout is greater than regular timeout."""
        if info.data:
            timeout = info.data.get("timeout_seconds", 60)
            if v <= timeout:
                raise ValueError(
                    f"recovery_timeout_seconds ({v}) must be > timeout_seconds ({timeout})"
                )
        return v


class WorkflowErrorHandlingConfigSchema(BaseModel):
    """Schema for workflow error handling configuration."""

    enabled: bool = Field(default=True, description="Enable workflow error handling")
    timeout_seconds: int = Field(default=300, ge=1, le=3600, description="Default workflow timeout")
    step_timeout_seconds: int = Field(default=60, ge=1, le=600, description="Default step timeout")
    rollback_retention_days: int = Field(
        default=30, ge=1, le=365, description="Rollback history retention"
    )

    circuit_breaker: CircuitBreakerConfigSchema = Field(
        default_factory=CircuitBreakerConfigSchema,
        description="Circuit breaker configuration",
    )

    resource_monitoring: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "memory_threshold_percent": 80,
            "cpu_threshold_percent": 90,
            "disk_threshold_percent": 90,
            "early_warning_percent": 75,
        },
        description="Resource monitoring thresholds",
    )

    notifications: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "websocket_enabled": True,
            "redis_pubsub_enabled": True,
            "log_notifications": True,
        },
        description="Notification system configuration",
    )


@dataclass
class CircuitBreakerConfigManager:
    """Manages circuit breaker configuration loading and validation."""

    config_data: dict[str, Any] = field(default_factory=dict)
    validated_config: WorkflowErrorHandlingConfigSchema | None = None

    def load_from_dict(self, config_dict: dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        self.config_data = config_dict
        self._validate_config()

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_config = {}

        # Circuit breaker settings
        if os.getenv("TTA_CIRCUIT_BREAKER_ENABLED"):
            env_config["circuit_breaker"] = env_config.get("circuit_breaker", {})
            env_config["circuit_breaker"]["enabled"] = os.getenv(
                "TTA_CIRCUIT_BREAKER_ENABLED", "true"
            ).lower() in ("true", "1", "yes")

        if os.getenv("TTA_CIRCUIT_BREAKER_FAILURE_THRESHOLD"):
            env_config["circuit_breaker"] = env_config.get("circuit_breaker", {})
            env_config["circuit_breaker"]["failure_threshold"] = int(
                os.getenv("TTA_CIRCUIT_BREAKER_FAILURE_THRESHOLD")
            )

        if os.getenv("TTA_CIRCUIT_BREAKER_TIMEOUT_SECONDS"):
            env_config["circuit_breaker"] = env_config.get("circuit_breaker", {})
            env_config["circuit_breaker"]["timeout_seconds"] = int(
                os.getenv("TTA_CIRCUIT_BREAKER_TIMEOUT_SECONDS")
            )

        if os.getenv("TTA_CIRCUIT_BREAKER_RECOVERY_TIMEOUT_SECONDS"):
            env_config["circuit_breaker"] = env_config.get("circuit_breaker", {})
            env_config["circuit_breaker"]["recovery_timeout_seconds"] = int(
                os.getenv("TTA_CIRCUIT_BREAKER_RECOVERY_TIMEOUT_SECONDS")
            )

        # Workflow error handling settings
        if os.getenv("TTA_WORKFLOW_ERROR_HANDLING_ENABLED"):
            env_config["enabled"] = os.getenv(
                "TTA_WORKFLOW_ERROR_HANDLING_ENABLED", "true"
            ).lower() in ("true", "1", "yes")

        if os.getenv("TTA_WORKFLOW_TIMEOUT_SECONDS"):
            env_config["timeout_seconds"] = int(os.getenv("TTA_WORKFLOW_TIMEOUT_SECONDS"))

        if os.getenv("TTA_WORKFLOW_STEP_TIMEOUT_SECONDS"):
            env_config["step_timeout_seconds"] = int(os.getenv("TTA_WORKFLOW_STEP_TIMEOUT_SECONDS"))

        # Resource monitoring settings
        if os.getenv("TTA_RESOURCE_MEMORY_THRESHOLD"):
            env_config["resource_monitoring"] = env_config.get("resource_monitoring", {})
            env_config["resource_monitoring"]["memory_threshold_percent"] = int(
                os.getenv("TTA_RESOURCE_MEMORY_THRESHOLD")
            )

        if os.getenv("TTA_RESOURCE_CPU_THRESHOLD"):
            env_config["resource_monitoring"] = env_config.get("resource_monitoring", {})
            env_config["resource_monitoring"]["cpu_threshold_percent"] = int(
                os.getenv("TTA_RESOURCE_CPU_THRESHOLD")
            )

        self.config_data.update(env_config)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration using Pydantic schema."""
        try:
            self.validated_config = WorkflowErrorHandlingConfigSchema(**self.config_data)
            logger.info("Circuit breaker configuration validated successfully")
        except Exception as e:
            logger.error(f"Circuit breaker configuration validation failed: {e}")
            # Use default configuration on validation failure
            self.validated_config = WorkflowErrorHandlingConfigSchema()
            logger.info("Using default circuit breaker configuration")

    def get_circuit_breaker_config(self, name: str | None = None) -> CircuitBreakerConfig:
        """Get CircuitBreakerConfig instance for a specific circuit breaker."""
        if not self.validated_config:
            self._validate_config()

        cb_config = self.validated_config.circuit_breaker

        return CircuitBreakerConfig(
            failure_threshold=cb_config.failure_threshold,
            timeout_seconds=cb_config.timeout_seconds,
            recovery_timeout_seconds=cb_config.recovery_timeout_seconds,
            half_open_max_calls=cb_config.half_open_max_calls,
            success_threshold=cb_config.success_threshold,
        )

    def is_circuit_breaker_enabled(self) -> bool:
        """Check if circuit breaker functionality is enabled."""
        if not self.validated_config:
            self._validate_config()
        return self.validated_config.enabled and self.validated_config.circuit_breaker.enabled

    def get_workflow_timeout_config(self) -> dict[str, int]:
        """Get workflow timeout configuration."""
        if not self.validated_config:
            self._validate_config()

        return {
            "timeout_seconds": self.validated_config.timeout_seconds,
            "step_timeout_seconds": self.validated_config.step_timeout_seconds,
        }

    def get_resource_monitoring_config(self) -> dict[str, Any]:
        """Get resource monitoring configuration."""
        if not self.validated_config:
            self._validate_config()
        return self.validated_config.resource_monitoring

    def get_notifications_config(self) -> dict[str, Any]:
        """Get notifications configuration."""
        if not self.validated_config:
            self._validate_config()
        return self.validated_config.notifications

    def get_rollback_retention_days(self) -> int:
        """Get rollback retention period in days."""
        if not self.validated_config:
            self._validate_config()
        return self.validated_config.rollback_retention_days

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        if not self.validated_config:
            self._validate_config()
        return self.validated_config.dict()

    def get_config_summary(self) -> dict[str, Any]:
        """Get a summary of current configuration."""
        if not self.validated_config:
            self._validate_config()

        return {
            "error_handling_enabled": self.validated_config.enabled,
            "circuit_breaker_enabled": self.validated_config.circuit_breaker.enabled,
            "circuit_breaker": {
                "failure_threshold": self.validated_config.circuit_breaker.failure_threshold,
                "timeout_seconds": self.validated_config.circuit_breaker.timeout_seconds,
                "recovery_timeout_seconds": self.validated_config.circuit_breaker.recovery_timeout_seconds,
            },
            "timeouts": {
                "workflow_timeout_seconds": self.validated_config.timeout_seconds,
                "step_timeout_seconds": self.validated_config.step_timeout_seconds,
            },
            "resource_monitoring": self.validated_config.resource_monitoring,
            "notifications": self.validated_config.notifications,
            "rollback_retention_days": self.validated_config.rollback_retention_days,
        }


# Global configuration manager instance
_global_config_manager = CircuitBreakerConfigManager()


def load_circuit_breaker_config(
    config_dict: dict[str, Any] | None = None,
) -> CircuitBreakerConfigManager:
    """Load circuit breaker configuration from dictionary or environment."""
    if config_dict:
        _global_config_manager.load_from_dict(config_dict)
    else:
        _global_config_manager.load_from_env()
    return _global_config_manager


def get_circuit_breaker_config_manager() -> CircuitBreakerConfigManager:
    """Get global circuit breaker configuration manager."""
    return _global_config_manager


def create_circuit_breaker_config_from_dict(
    config_dict: dict[str, Any],
) -> CircuitBreakerConfig:
    """Create CircuitBreakerConfig from dictionary (convenience function)."""
    manager = CircuitBreakerConfigManager()
    manager.load_from_dict(config_dict)
    return manager.get_circuit_breaker_config()


def validate_circuit_breaker_config(config_dict: dict[str, Any]) -> list[str]:
    """Validate circuit breaker configuration and return list of errors."""
    errors = []
    try:
        WorkflowErrorHandlingConfigSchema(**config_dict)
    except Exception as e:
        if hasattr(e, "errors"):
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                errors.append(f"{field}: {error['msg']}")
        else:
            errors.append(str(e))
    return errors
