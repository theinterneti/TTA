"""
Core Services for Model Management

This package contains the core services that support the model management
system, including hardware detection, model selection, performance monitoring,
and fallback handling.

Services:
    HardwareDetector: System resource detection and model recommendations
    ModelSelector: Intelligent model selection based on requirements
    PerformanceMonitor: Real-time performance tracking and metrics
    FallbackHandler: Automatic fallback mechanisms for model failures

Example:
    ```python
    from src.components.model_management.services import HardwareDetector, ModelSelector

    # Detect system capabilities
    detector = HardwareDetector()
    resources = await detector.detect_system_resources()

    # Get model recommendations
    recommended_models = await detector.recommend_models(TaskType.NARRATIVE_GENERATION)

    # Select optimal model
    selector = ModelSelector(providers, detector)
    model = await selector.select_model(requirements)
    ```
"""

from .fallback_handler import FallbackHandler
from .hardware_detector import HardwareDetector
from .model_selector import ModelSelector
from .performance_monitor import PerformanceMonitor

__all__ = ["HardwareDetector", "ModelSelector", "PerformanceMonitor", "FallbackHandler"]
