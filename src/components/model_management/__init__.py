"""
Model Management System for TTA

This package provides comprehensive AI model management capabilities including:
- Multiple provider support (OpenRouter, Local, Ollama, LM Studio, Custom APIs)
- Hardware detection and model recommendations
- Performance monitoring and fallback mechanisms
- Unified configuration interface

Components:
    ModelManagementComponent: Main component for model lifecycle management
    ModelSelector: Intelligent model selection service
    HardwareDetector: System resource detection and recommendations
    PerformanceMonitor: Model performance tracking
    FallbackHandler: Automatic fallback mechanisms

Providers:
    OpenRouterProvider: Cloud-based models via OpenRouter API
    LocalModelProvider: Local model management with hardware optimization
    OllamaProvider: Containerized model deployment via Ollama
    LMStudioProvider: Integration with LM Studio
    CustomAPIProvider: Support for OpenAI, Anthropic, and other APIs

Example:
    ```python
    from src.components.model_management import ModelManagementComponent
    from src.orchestration import TTAConfig
    
    # Initialize model management
    config = TTAConfig()
    model_manager = ModelManagementComponent(config)
    
    # Start the service
    await model_manager.start()
    
    # Select optimal model for task
    model = await model_manager.select_model(
        task_type="narrative_generation",
        requirements={"max_latency_ms": 2000, "min_quality_score": 7.5}
    )
    ```
"""

from .model_management_component import ModelManagementComponent
from .interfaces import (
    IModelProvider,
    IModelInstance,
    TaskType,
    ModelRequirements,
    ModelInfo,
    ProviderType,
    GenerationRequest
)
from .models import (
    ModelConfiguration,
    PerformanceMetrics,
    SystemResources,
    ModelStatus
)

__all__ = [
    "ModelManagementComponent",
    "IModelProvider",
    "IModelInstance",
    "TaskType",
    "ModelRequirements",
    "ModelInfo",
    "ProviderType",
    "GenerationRequest",
    "ModelConfiguration",
    "PerformanceMetrics",
    "SystemResources",
    "ModelStatus"
]
