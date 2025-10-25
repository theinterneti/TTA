"""
Core interfaces for the Model Management System.

This module defines the fundamental interfaces and enums used throughout
the model management system.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(Enum):
    """Types of model providers supported by the system."""

    LOCAL = "local"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    CUSTOM_API = "custom_api"


class TaskType(Enum):
    """Types of tasks that models can perform."""

    NARRATIVE_GENERATION = "narrative_generation"
    DIALOGUE_GENERATION = "dialogue_generation"
    CHARACTER_DEVELOPMENT = "character_development"
    THERAPEUTIC_RESPONSE = "therapeutic_response"
    WORLD_BUILDING = "world_building"
    CHOICE_GENERATION = "choice_generation"
    CONSEQUENCE_ANALYSIS = "consequence_analysis"
    GENERAL_CHAT = "general_chat"


class ModelStatus(Enum):
    """Status of a model instance."""

    UNKNOWN = "unknown"
    AVAILABLE = "available"
    LOADING = "loading"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class ModelRequirements:
    """Requirements for model selection."""

    task_type: TaskType
    max_latency_ms: int | None = None
    min_quality_score: float | None = None
    max_cost_per_token: float | None = None
    required_capabilities: list[str] = field(default_factory=list)
    context_length_needed: int | None = None
    therapeutic_safety_required: bool = True


@dataclass
class ModelInfo:
    """Information about an available model."""

    model_id: str
    name: str
    provider_type: ProviderType
    description: str = ""
    context_length: int | None = None
    cost_per_token: float | None = None
    is_free: bool = False
    capabilities: list[str] = field(default_factory=list)
    therapeutic_safety_score: float | None = None
    performance_score: float | None = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


@dataclass
class GenerationRequest:
    """Request for text generation."""

    prompt: str
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    stop_sequences: list[str] | None = None
    stream: bool = False
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GenerationResponse:
    """Response from text generation."""

    text: str
    model_id: str
    usage: dict[str, int] | None = None
    latency_ms: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IModelInstance(ABC):
    """Interface for a model instance that can generate text."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Get the model identifier."""
        pass

    @property
    @abstractmethod
    def status(self) -> ModelStatus:
        """Get the current status of the model."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text based on the request."""
        pass

    @abstractmethod
    def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate text as a stream."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the model is healthy and responsive."""
        pass

    @abstractmethod
    async def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics for this model instance."""
        pass


class IModelProvider(ABC):
    """Interface for model providers."""

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the provider with configuration."""
        pass

    @abstractmethod
    async def get_available_models(
        self, filters: dict[str, Any] | None = None
    ) -> list[ModelInfo]:
        """Get list of available models from this provider."""
        pass

    @abstractmethod
    async def load_model(
        self, model_id: str, config: dict[str, Any] | None = None
    ) -> IModelInstance:
        """Load a specific model and return an instance."""
        pass

    @abstractmethod
    async def unload_model(self, model_id: str) -> bool:
        """Unload a specific model to free resources."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible."""
        pass

    @abstractmethod
    async def get_provider_metrics(self) -> dict[str, Any]:
        """Get metrics for this provider."""
        pass

    async def cleanup(self) -> None:
        """Cleanup provider resources. Optional method with default implementation."""
        # Default implementation: no cleanup needed
        ...

    async def get_free_models(self) -> list[ModelInfo]:
        """Get list of free models. Optional method with default implementation."""
        return []

    async def set_free_models_filter(
        self,
        show_free_only: bool = False,
        prefer_free: bool = True,
        max_cost_per_token: float = 0.001,
    ) -> None:
        """Enable/disable free models filter. Optional method with default implementation."""
        # Default implementation: no filtering
        ...

    async def get_filter_settings(self) -> dict[str, Any]:
        """Get current filter settings. Optional method with default implementation."""
        return {}


class IModelSelector(ABC):
    """Interface for model selection logic."""

    @abstractmethod
    async def select_model(self, requirements: ModelRequirements) -> ModelInfo | None:
        """Select the best model based on requirements."""
        pass

    @abstractmethod
    async def rank_models(
        self, models: list[ModelInfo], requirements: ModelRequirements
    ) -> list[ModelInfo]:
        """Rank models by suitability for the requirements."""
        pass

    @abstractmethod
    async def validate_model_compatibility(
        self, model_info: ModelInfo, requirements: ModelRequirements
    ) -> bool:
        """Check if a model is compatible with the requirements."""
        pass


class IHardwareDetector(ABC):
    """Interface for hardware detection and recommendations."""

    @abstractmethod
    async def detect_system_resources(self) -> dict[str, Any]:
        """Detect available system resources."""
        pass

    @abstractmethod
    async def recommend_models(self, task_type: TaskType) -> list[str]:
        """Recommend models based on available hardware."""
        pass

    @abstractmethod
    async def estimate_model_requirements(self, model_id: str) -> dict[str, Any]:
        """Estimate resource requirements for a specific model."""
        pass


class IPerformanceMonitor(ABC):
    """Interface for performance monitoring."""

    @abstractmethod
    async def record_metrics(self, model_id: str, metrics: dict[str, Any]) -> None:
        """Record performance metrics for a model."""
        pass

    @abstractmethod
    async def get_model_performance(
        self, model_id: str, timeframe_hours: int = 24
    ) -> dict[str, Any]:
        """Get performance metrics for a model over a timeframe."""
        pass

    @abstractmethod
    async def get_system_performance(self) -> dict[str, Any]:
        """Get overall system performance metrics."""
        pass


class IFallbackHandler(ABC):
    """Interface for fallback handling."""

    @abstractmethod
    async def get_fallback_model(
        self, failed_model_id: str, requirements: ModelRequirements
    ) -> ModelInfo | None:
        """Get a fallback model when the primary model fails."""
        pass

    @abstractmethod
    async def handle_model_failure(self, model_id: str, error: Exception) -> None:
        """Handle a model failure event."""
        pass
