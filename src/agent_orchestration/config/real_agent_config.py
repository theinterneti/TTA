"""

# Logseq: [[TTA.dev/Agent_orchestration/Config/Real_agent_config]]
Configuration for real agent communication.

This module provides configuration settings for enabling and managing
real agent communication in the orchestration system.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class RealAgentConfig:
    """Configuration for real agent communication."""

    # Enable/disable real agent communication
    enable_real_agents: bool = True
    fallback_to_mock: bool = True

    # Retry configuration
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

    # Timeout configuration
    ipa_timeout_s: float = 8.0
    wba_timeout_s: float = 12.0
    nga_timeout_s: float = 15.0

    # Batching configuration
    enable_batching: bool = True
    batch_size: int = 10
    batch_timeout_ms: int = 100
    max_concurrent_batches: int = 5

    # Workflow coordination
    max_concurrent_workflows: int = 100
    workflow_timeout_s: float = 300.0

    # Monitoring configuration
    enable_monitoring: bool = True
    enable_profiling: bool = False
    enable_alerts: bool = True

    # Performance thresholds
    high_memory_threshold_mb: float = 1500.0
    high_queue_depth_threshold: int = 100
    high_error_rate_threshold: float = 0.2
    slow_response_time_threshold_s: float = 10.0

    @classmethod
    def from_environment(cls) -> RealAgentConfig:
        """Create configuration from environment variables."""
        return cls(
            enable_real_agents=_get_env_bool("TTA_ENABLE_REAL_AGENTS", True),
            fallback_to_mock=_get_env_bool("TTA_FALLBACK_TO_MOCK", True),
            max_retries=_get_env_int("TTA_MAX_RETRIES", 3),
            base_delay=_get_env_float("TTA_BASE_DELAY", 1.0),
            max_delay=_get_env_float("TTA_MAX_DELAY", 60.0),
            exponential_base=_get_env_float("TTA_EXPONENTIAL_BASE", 2.0),
            jitter=_get_env_bool("TTA_JITTER", True),
            ipa_timeout_s=_get_env_float("TTA_IPA_TIMEOUT", 8.0),
            wba_timeout_s=_get_env_float("TTA_WBA_TIMEOUT", 12.0),
            nga_timeout_s=_get_env_float("TTA_NGA_TIMEOUT", 15.0),
            enable_batching=_get_env_bool("TTA_ENABLE_BATCHING", True),
            batch_size=_get_env_int("TTA_BATCH_SIZE", 10),
            batch_timeout_ms=_get_env_int("TTA_BATCH_TIMEOUT_MS", 100),
            max_concurrent_batches=_get_env_int("TTA_MAX_CONCURRENT_BATCHES", 5),
            max_concurrent_workflows=_get_env_int("TTA_MAX_CONCURRENT_WORKFLOWS", 100),
            workflow_timeout_s=_get_env_float("TTA_WORKFLOW_TIMEOUT", 300.0),
            enable_monitoring=_get_env_bool("TTA_ENABLE_MONITORING", True),
            enable_profiling=_get_env_bool("TTA_ENABLE_PROFILING", False),
            enable_alerts=_get_env_bool("TTA_ENABLE_ALERTS", True),
            high_memory_threshold_mb=_get_env_float(
                "TTA_HIGH_MEMORY_THRESHOLD_MB", 1500.0
            ),
            high_queue_depth_threshold=_get_env_int(
                "TTA_HIGH_QUEUE_DEPTH_THRESHOLD", 100
            ),
            high_error_rate_threshold=_get_env_float(
                "TTA_HIGH_ERROR_RATE_THRESHOLD", 0.2
            ),
            slow_response_time_threshold_s=_get_env_float(
                "TTA_SLOW_RESPONSE_TIME_THRESHOLD", 10.0
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enable_real_agents": self.enable_real_agents,
            "fallback_to_mock": self.fallback_to_mock,
            "retry_config": {
                "max_retries": self.max_retries,
                "base_delay": self.base_delay,
                "max_delay": self.max_delay,
                "exponential_base": self.exponential_base,
                "jitter": self.jitter,
            },
            "timeouts": {
                "ipa_timeout_s": self.ipa_timeout_s,
                "wba_timeout_s": self.wba_timeout_s,
                "nga_timeout_s": self.nga_timeout_s,
            },
            "batching": {
                "enable_batching": self.enable_batching,
                "batch_size": self.batch_size,
                "batch_timeout_ms": self.batch_timeout_ms,
                "max_concurrent_batches": self.max_concurrent_batches,
            },
            "workflow_coordination": {
                "max_concurrent_workflows": self.max_concurrent_workflows,
                "workflow_timeout_s": self.workflow_timeout_s,
            },
            "monitoring": {
                "enable_monitoring": self.enable_monitoring,
                "enable_profiling": self.enable_profiling,
                "enable_alerts": self.enable_alerts,
            },
            "performance_thresholds": {
                "high_memory_threshold_mb": self.high_memory_threshold_mb,
                "high_queue_depth_threshold": self.high_queue_depth_threshold,
                "high_error_rate_threshold": self.high_error_rate_threshold,
                "slow_response_time_threshold_s": self.slow_response_time_threshold_s,
            },
        }


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _get_env_int(key: str, default: int) -> int:
    """Get integer value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


# Global configuration instance
_config: RealAgentConfig | None = None


def get_real_agent_config() -> RealAgentConfig:
    """Get the global real agent configuration."""
    global _config
    if _config is None:
        _config = RealAgentConfig.from_environment()
    return _config


def set_real_agent_config(config: RealAgentConfig) -> None:
    """Set the global real agent configuration."""
    global _config
    _config = config


def reset_real_agent_config() -> None:
    """Reset the global real agent configuration to load from environment."""
    global _config
    _config = None
