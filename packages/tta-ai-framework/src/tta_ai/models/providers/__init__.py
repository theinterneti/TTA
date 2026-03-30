"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Models/Providers/__init__]]
Model Provider Adapters

This package contains adapters for different AI model providers, enabling
unified access to various model hosting services.

Providers:
    BaseProvider: Abstract base class for all providers
    OpenRouterProvider: Cloud-based models via OpenRouter API
    LocalModelProvider: Local model management with hardware optimization
    OllamaProvider: Containerized model deployment via Ollama
    LMStudioProvider: Integration with LM Studio
    CustomAPIProvider: Support for OpenAI, Anthropic, and other APIs

Example:
    ```python
    from tta_ai.models.providers import OpenRouterProvider

    # Initialize provider
    provider = OpenRouterProvider()
    await provider.initialize({"api_key": "your-key"})

    # Get available models
    models = await provider.get_available_models({"free_only": True})

    # Load a model
    model_instance = await provider.load_model("meta-llama/llama-3.1-8b-instruct:free")
    ```
"""

from .base import BaseProvider
from .custom_api import CustomAPIProvider
from .lm_studio import LMStudioProvider
from .local import LocalModelProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider

__all__ = [
    "BaseProvider",
    "OpenRouterProvider",
    "LocalModelProvider",
    "OllamaProvider",
    "LMStudioProvider",
    "CustomAPIProvider",
]
