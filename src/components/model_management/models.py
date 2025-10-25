"""
Data models for the Model Management System.

This module contains the core data structures used throughout the model
management system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .interfaces import ModelStatus, ProviderType, TaskType


@dataclass
class SystemResources:
    """System resource information."""

    total_ram_gb: float
    available_ram_gb: float
    cpu_cores: int
    cpu_model: str
    gpu_count: int
    gpu_models: list[str] = field(default_factory=list)
    gpu_memory_gb: list[float] = field(default_factory=list)
    disk_space_gb: float = 0.0
    platform: str = ""
    python_version: str = ""

    @property
    def has_gpu(self) -> bool:
        """Check if system has GPU."""
        return self.gpu_count > 0

    @property
    def total_gpu_memory_gb(self) -> float:
        """Get total GPU memory across all GPUs."""
        return sum(self.gpu_memory_gb)


@dataclass
class ModelConfiguration:
    """Configuration for a specific model."""

    model_id: str
    provider_type: ProviderType
    name: str = ""
    enabled: bool = True

    # Provider-specific configuration
    api_key: str | None = None
    api_base: str | None = None
    model_path: str | None = None

    # Security configuration for local models
    # Git revision (commit hash or tag) to pin when using trust_remote_code=True
    # This prevents arbitrary code execution from Hugging Face Hub
    revision: str | None = None
    trust_remote_code: bool = False

    # Generation parameters
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int | None = None

    # Resource limits
    max_memory_gb: float | None = None
    max_gpu_memory_gb: float | None = None
    quantization: str | None = None

    # Capabilities and metadata
    supported_tasks: list[TaskType] = field(default_factory=list)
    context_length: int | None = None
    cost_per_token: float | None = None
    is_free: bool = False
    therapeutic_safety_score: float | None = None

    # Fallback configuration
    fallback_models: list[str] = field(default_factory=list)
    priority: int = 0  # Higher priority = preferred

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a model."""

    model_id: str
    timestamp: datetime

    # Response metrics
    response_time_ms: float
    tokens_per_second: float
    total_tokens: int

    # Quality metrics
    quality_score: float | None = None
    therapeutic_safety_score: float | None = None

    # Resource usage
    memory_usage_mb: float | None = None
    gpu_memory_usage_mb: float | None = None
    cpu_usage_percent: float | None = None

    # Error tracking
    error_count: int = 0
    success_rate: float = 1.0

    # Task-specific metrics
    task_type: TaskType | None = None
    context_length_used: int | None = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelHealth:
    """Health status of a model."""

    model_id: str
    status: ModelStatus
    last_check: datetime

    # Health indicators
    is_responsive: bool = True
    response_time_ms: float | None = None
    error_rate: float = 0.0

    # Resource status
    memory_usage_percent: float | None = None
    gpu_usage_percent: float | None = None

    # Error information
    last_error: str | None = None
    error_count_24h: int = 0

    # Availability
    uptime_hours: float = 0.0
    availability_percent: float = 100.0


@dataclass
class ProviderConfiguration:
    """Configuration for a model provider."""

    provider_type: ProviderType
    enabled: bool = True

    # Authentication
    api_key: str | None = None
    api_base: str | None = None

    # Provider-specific settings
    prefer_free_models: bool = True
    max_cost_per_million_tokens: float | None = None
    rate_limit_buffer: float = 0.8

    # Local provider settings
    models_cache_dir: str | None = None
    max_concurrent_models: int = 2
    auto_quantization: bool = True
    gpu_memory_fraction: float = 0.8

    # Security settings for local models
    # Map of model_id to trusted git revision (commit hash or tag)
    # Required when trust_remote_code=True to prevent arbitrary code execution
    trusted_model_revisions: dict[str, str] = field(default_factory=dict)
    # Require revision pinning for all models with trust_remote_code=True
    require_revision_pinning: bool = True

    # Ollama settings
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    use_docker: bool = True
    docker_image: str = "ollama/ollama:latest"

    # Custom API settings
    custom_providers: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Additional configuration
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSelectionCriteria:
    """Criteria for model selection."""

    primary_criteria: str = (
        "cost_effectiveness"  # cost_effectiveness, performance, availability
    )
    fallback_criteria: str = "availability"

    # Weights for selection scoring (should sum to 1.0)
    therapeutic_safety_weight: float = 0.4
    performance_weight: float = 0.3
    cost_weight: float = 0.3

    # Thresholds
    min_therapeutic_safety_score: float = 7.0
    max_acceptable_latency_ms: int = 5000
    max_cost_per_token: float | None = None

    # Preferences
    prefer_local_models: bool = False
    prefer_free_models: bool = True
    require_streaming: bool = False


@dataclass
class FallbackConfiguration:
    """Configuration for fallback behavior."""

    enabled: bool = True
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    # Fallback strategy
    fallback_strategy: str = (
        "performance_based"  # performance_based, cost_based, availability_based
    )

    # Automatic fallback triggers
    max_response_time_ms: int = 10000
    max_error_rate: float = 0.1
    min_availability_percent: float = 95.0

    # Fallback model selection
    exclude_failed_models_minutes: int = 30
    prefer_different_provider: bool = True


@dataclass
class ModelManagementConfig:
    """Complete configuration for the model management system."""

    enabled: bool = True
    default_provider: str = "openrouter"

    # Provider configurations
    providers: dict[str, ProviderConfiguration] = field(default_factory=dict)

    # Model configurations
    models: dict[str, ModelConfiguration] = field(default_factory=dict)

    # Selection and fallback
    selection_strategy: ModelSelectionCriteria = field(
        default_factory=ModelSelectionCriteria
    )
    fallback_config: FallbackConfiguration = field(
        default_factory=FallbackConfiguration
    )

    # Monitoring and caching
    performance_monitoring_enabled: bool = True
    cache_ttl_seconds: int = 3600
    health_check_interval_seconds: int = 300

    # Resource management
    max_total_memory_gb: float | None = None
    max_gpu_memory_percent: float = 80.0
    cleanup_interval_minutes: int = 60


@dataclass
class ModelUsageStats:
    """Usage statistics for a model."""

    model_id: str
    period_start: datetime
    period_end: datetime

    # Usage counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Token usage
    total_tokens_generated: int = 0
    average_tokens_per_request: float = 0.0

    # Performance
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    average_quality_score: float | None = None

    # Costs (if applicable)
    total_cost: float | None = None
    cost_per_request: float | None = None

    # Resource usage
    peak_memory_usage_mb: float | None = None
    average_cpu_usage_percent: float | None = None
