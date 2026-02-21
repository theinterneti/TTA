"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Models/Providers/Base]]
Base Provider Implementation

This module provides the abstract base class for all model providers,
defining common functionality and interfaces.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from ..interfaces import (
    GenerationRequest,
    IModelInstance,
    IModelProvider,
    ModelInfo,
    ModelStatus,
    ProviderType,
)

logger = logging.getLogger(__name__)


class BaseModelInstance(IModelInstance):
    """Base implementation for model instances."""

    def __init__(self, model_id: str, provider: "BaseProvider"):
        self._model_id = model_id
        self._provider = provider
        self._status = ModelStatus.UNKNOWN
        self._last_health_check = None
        self._metrics = {}

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def status(self) -> ModelStatus:
        return self._status

    async def health_check(self) -> bool:
        """Default health check implementation."""
        try:
            # Simple test generation
            test_request = GenerationRequest(prompt="Hello", max_tokens=1, temperature=0.0)
            response = await self.generate(test_request)
            self._status = ModelStatus.READY if response.text else ModelStatus.ERROR
            self._last_health_check = datetime.now()
            return self._status == ModelStatus.READY
        except Exception as e:
            logger.warning(f"Health check failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            return False

    async def get_metrics(self) -> dict[str, Any]:
        """Get basic metrics for this model instance."""
        return {
            "model_id": self.model_id,
            "status": self.status.value,
            "last_health_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "provider_type": self._provider.provider_type.value,
            **self._metrics,
        }

    def _update_metrics(self, metrics: dict[str, Any]):
        """Update internal metrics."""
        self._metrics.update(metrics)


class BaseProvider(IModelProvider, ABC):
    """Abstract base class for all model providers."""

    def __init__(self):
        self._initialized = False
        self._config = {}
        self._loaded_models: dict[str, IModelInstance] = {}
        self._available_models: list[ModelInfo] = []
        self._last_model_refresh = None
        self._health_status = True

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass

    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the provider with configuration."""
        try:
            self._config = config.copy()

            # Validate required configuration
            if not await self._validate_config(config):
                logger.error(f"Invalid configuration for {self.provider_type.value} provider")
                return False

            # Provider-specific initialization
            if not await self._initialize_provider():
                logger.error(f"Failed to initialize {self.provider_type.value} provider")
                return False

            # Initial model discovery
            await self._refresh_available_models()

            self._initialized = True
            logger.info(f"Successfully initialized {self.provider_type.value} provider")
            return True

        except Exception as e:
            logger.error(f"Error initializing {self.provider_type.value} provider: {e}")
            return False

    async def get_available_models(self, filters: dict[str, Any] | None = None) -> list[ModelInfo]:
        """Get list of available models from this provider."""
        if not self._initialized:
            raise RuntimeError(f"Provider {self.provider_type.value} not initialized")

        # Refresh models if cache is stale
        if self._should_refresh_models():
            await self._refresh_available_models()

        models = self._available_models.copy()

        # Apply filters if provided
        if filters:
            models = await self._apply_filters(models, filters)

        return models

    async def load_model(
        self, model_id: str, config: dict[str, Any] | None = None
    ) -> IModelInstance:
        """Load a specific model and return an instance."""
        if not self._initialized:
            raise RuntimeError(f"Provider {self.provider_type.value} not initialized")

        # Check if model is already loaded
        if model_id in self._loaded_models:
            instance = self._loaded_models[model_id]
            if await instance.health_check():
                return instance
            # Remove unhealthy instance
            await self.unload_model(model_id)

        # Load new model instance
        try:
            instance = await self._load_model_impl(model_id, config or {})
            self._loaded_models[model_id] = instance
            logger.info(f"Successfully loaded model {model_id} from {self.provider_type.value}")
            return instance
        except Exception as e:
            logger.error(f"Failed to load model {model_id} from {self.provider_type.value}: {e}")
            raise

    async def unload_model(self, model_id: str) -> bool:
        """Unload a specific model to free resources."""
        if model_id not in self._loaded_models:
            return True

        try:
            instance = self._loaded_models[model_id]
            await self._unload_model_impl(instance)
            del self._loaded_models[model_id]
            logger.info(f"Successfully unloaded model {model_id} from {self.provider_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload model {model_id} from {self.provider_type.value}: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible."""
        try:
            # Provider-specific health check
            provider_healthy = await self._provider_health_check()

            # Check loaded models
            unhealthy_models = []
            for model_id, instance in self._loaded_models.items():
                if not await instance.health_check():
                    unhealthy_models.append(model_id)

            # Unload unhealthy models
            for model_id in unhealthy_models:
                await self.unload_model(model_id)

            self._health_status = provider_healthy
            return provider_healthy

        except Exception as e:
            logger.error(f"Health check failed for {self.provider_type.value} provider: {e}")
            self._health_status = False
            return False

    async def get_provider_metrics(self) -> dict[str, Any]:
        """Get metrics for this provider."""
        return {
            "provider_type": self.provider_type.value,
            "initialized": self._initialized,
            "healthy": self._health_status,
            "loaded_models_count": len(self._loaded_models),
            "available_models_count": len(self._available_models),
            "last_model_refresh": (
                self._last_model_refresh.isoformat() if self._last_model_refresh else None
            ),
            "loaded_models": list(self._loaded_models.keys()),
        }

    # Abstract methods to be implemented by subclasses

    @abstractmethod
    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate provider-specific configuration."""
        pass

    @abstractmethod
    async def _initialize_provider(self) -> bool:
        """Provider-specific initialization logic."""
        pass

    @abstractmethod
    async def _refresh_available_models(self) -> None:
        """Refresh the list of available models."""
        pass

    @abstractmethod
    async def _load_model_impl(self, model_id: str, config: dict[str, Any]) -> IModelInstance:
        """Provider-specific model loading implementation."""
        pass

    @abstractmethod
    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Provider-specific model unloading implementation."""
        pass

    @abstractmethod
    async def _provider_health_check(self) -> bool:
        """Provider-specific health check."""
        pass

    # Helper methods

    def _should_refresh_models(self) -> bool:
        """Check if model list should be refreshed."""
        if not self._last_model_refresh:
            return True

        # Refresh every hour
        return datetime.now() - self._last_model_refresh > timedelta(hours=1)

    async def _apply_filters(
        self, models: list[ModelInfo], filters: dict[str, Any]
    ) -> list[ModelInfo]:
        """Apply filters to model list."""
        filtered_models = models

        # Free models only
        if filters.get("free_only", False):
            filtered_models = [m for m in filtered_models if m.is_free]

        # Maximum cost per token
        max_cost = filters.get("max_cost_per_token")
        if max_cost is not None:
            filtered_models = [
                m
                for m in filtered_models
                if m.cost_per_token is None or m.cost_per_token <= max_cost
            ]

        # Minimum context length
        min_context = filters.get("min_context_length")
        if min_context is not None:
            filtered_models = [
                m
                for m in filtered_models
                if m.context_length is None or m.context_length >= min_context
            ]

        # Required capabilities
        required_caps = filters.get("required_capabilities", [])
        if required_caps:
            filtered_models = [
                m for m in filtered_models if all(cap in m.capabilities for cap in required_caps)
            ]

        return filtered_models
