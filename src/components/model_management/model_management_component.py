"""

# Logseq: [[TTA.dev/Components/Model_management/Model_management_component]]
Model Management Component.

This module provides the main component for comprehensive AI model management
within the TTA platform, coordinating multiple providers and services.
"""

import logging
from datetime import datetime
from typing import Any

from src.orchestration.component import Component
from src.orchestration.decorators import log_entry_exit, timing_decorator

from .interfaces import (
    GenerationRequest,
    GenerationResponse,
    IModelInstance,
    IModelProvider,
    ModelInfo,
    ModelRequirements,
    TaskType,
)
from .models import ModelManagementConfig, PerformanceMetrics
from .providers import (
    OllamaProvider,
    OpenRouterProvider,
)
from .services import (
    FallbackHandler,
    HardwareDetector,
    ModelSelector,
    PerformanceMonitor,
)

logger = logging.getLogger(__name__)


class ModelManagementComponent(Component):
    """
    Main component for AI model management.

    This component coordinates multiple model providers, handles model selection,
    monitors performance, and provides fallback mechanisms for the TTA platform.
    """

    def __init__(self, config: Any, name: str = "model_management"):
        super().__init__(config, name=name, dependencies=["redis", "neo4j"])

        # Configuration
        self.model_config = self._load_model_config()

        # Core services
        self.hardware_detector = HardwareDetector()
        self.performance_monitor: PerformanceMonitor | None = None
        self.fallback_handler: FallbackHandler | None = None
        self.model_selector: ModelSelector | None = None

        # Providers
        self.providers: dict[str, IModelProvider] = {}
        self.active_models: dict[str, IModelInstance] = {}

        # State
        self.initialized = False
        self.last_health_check = None
        self.system_resources = None

    @log_entry_exit
    @timing_decorator
    async def _start_impl(self) -> bool:  # type: ignore[override]
        """Start the model management component (async implementation)."""
        try:
            logger.info("Starting Model Management Component")

            # Detect system resources
            logger.info("Detecting system resources...")
            self.system_resources = (
                await self.hardware_detector.detect_system_resources()
            )
            logger.info(
                f"System resources: {self.system_resources['total_ram_gb']:.1f}GB RAM, "
                f"{self.system_resources['gpu_count']} GPUs"
            )

            # Initialize providers
            await self._initialize_providers()

            # Initialize services
            await self._initialize_services()

            # Perform initial health check
            await self._perform_health_check()

            self.initialized = True
            logger.info("Model Management Component started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start Model Management Component: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    async def _stop_impl(self) -> bool:  # type: ignore[override]
        """Stop the model management component (async implementation)."""
        try:
            logger.info("Stopping Model Management Component")

            # Unload all active models
            for model_id in list(self.active_models.keys()):
                await self.unload_model(model_id)

            # Cleanup providers
            for provider in self.providers.values():
                if hasattr(provider, "cleanup"):
                    await provider.cleanup()

            self.initialized = False
            logger.info("Model Management Component stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop Model Management Component: {e}")
            return False

    async def select_model(
        self, requirements: ModelRequirements
    ) -> IModelInstance | None:
        """Select and load the best model for the given requirements."""
        if not self.initialized:
            raise RuntimeError("Model Management Component not initialized")

        try:
            # Use model selector to find the best model
            if not self.model_selector:
                raise RuntimeError("Model selector not initialized")
            selected_model_info = await self.model_selector.select_model(requirements)

            if not selected_model_info:
                logger.warning(
                    f"No suitable model found for requirements: {requirements}"
                )
                return None

            # Load the selected model
            model_instance = await self.load_model(
                selected_model_info.model_id, selected_model_info.provider_type.value
            )

            logger.info(f"Selected and loaded model: {selected_model_info.model_id}")
            return model_instance

        except Exception as e:
            logger.error(f"Model selection failed: {e}")

            # Try fallback if available
            if self.fallback_handler:
                fallback_model = await self.fallback_handler.get_fallback_model(
                    "", requirements
                )
                if fallback_model:
                    return await self.load_model(
                        fallback_model.model_id, fallback_model.provider_type.value
                    )

            return None

    async def load_model(self, model_id: str, provider_name: str) -> IModelInstance:
        """Load a specific model from a provider."""
        if not self.initialized:
            raise RuntimeError("Model Management Component not initialized")

        # Check if model is already loaded
        cache_key = f"{provider_name}:{model_id}"
        if cache_key in self.active_models:
            instance = self.active_models[cache_key]
            if await instance.health_check():
                return instance
            # Remove unhealthy instance
            del self.active_models[cache_key]

        # Load model from provider
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")

        provider = self.providers[provider_name]
        instance = await provider.load_model(model_id)

        # Cache the instance
        self.active_models[cache_key] = instance

        logger.info(f"Loaded model {model_id} from provider {provider_name}")
        return instance

    async def unload_model(
        self, model_id: str, provider_name: str | None = None
    ) -> bool:
        """Unload a specific model."""
        try:
            # Find the model to unload
            keys_to_remove = []

            if provider_name:
                cache_key = f"{provider_name}:{model_id}"
                if cache_key in self.active_models:
                    keys_to_remove.append(cache_key)
            else:
                # Find all instances of this model across providers
                for key in self.active_models:
                    if key.endswith(f":{model_id}"):
                        keys_to_remove.append(key)

            # Unload found instances
            for key in keys_to_remove:
                self.active_models[key]
                provider_name = key.split(":")[0]

                if provider_name in self.providers:
                    await self.providers[provider_name].unload_model(model_id)

                del self.active_models[key]
                logger.info(f"Unloaded model {model_id} from provider {provider_name}")

            return len(keys_to_remove) > 0

        except Exception as e:
            logger.error(f"Failed to unload model {model_id}: {e}")
            return False

    async def get_available_models(
        self, provider_name: str | None = None, free_only: bool = False
    ) -> list[ModelInfo]:
        """Get available models from all or specific providers with optional free filter."""
        if not self.initialized:
            raise RuntimeError("Model Management Component not initialized")

        all_models = []

        providers_to_check = (
            [provider_name] if provider_name else list(self.providers.keys())
        )

        for prov_name in providers_to_check:
            if prov_name in self.providers:
                try:
                    models = await self.providers[prov_name].get_available_models()
                    all_models.extend(models)
                except Exception as e:
                    logger.warning(
                        f"Failed to get models from provider {prov_name}: {e}"
                    )

        # Apply free filter if requested
        if free_only:
            all_models = [model for model in all_models if model.is_free]
            logger.info(f"Filtered to {len(all_models)} free models")

        return all_models

    async def get_free_models(
        self, provider_name: str | None = None
    ) -> list[ModelInfo]:
        """Get only free models from all or specific providers."""
        return await self.get_available_models(
            provider_name=provider_name, free_only=True
        )

    async def get_openrouter_free_models(self) -> list[ModelInfo]:
        """Get free models specifically from OpenRouter provider."""
        if "openrouter" not in self.providers:
            logger.warning("OpenRouter provider not available")
            return []

        try:
            provider = self.providers["openrouter"]
            if hasattr(provider, "get_free_models"):
                return await provider.get_free_models()
            # Fallback to general free filter
            return await self.get_available_models(
                provider_name="openrouter", free_only=True
            )
        except Exception as e:
            logger.error(f"Failed to get OpenRouter free models: {e}")
            return []

    async def get_affordable_models(
        self, max_cost_per_token: float = 0.001, provider_name: str | None = None
    ) -> list[ModelInfo]:
        """Get models within the specified cost threshold."""
        all_models = await self.get_available_models(provider_name=provider_name)

        affordable_models = []
        for model in all_models:
            if model.is_free or (
                model.cost_per_token is not None
                and model.cost_per_token <= max_cost_per_token
            ):
                affordable_models.append(model)

        logger.info(
            f"Found {len(affordable_models)} affordable models (max cost: {max_cost_per_token})"
        )
        return affordable_models

    async def set_openrouter_filter(
        self,
        show_free_only: bool = False,
        prefer_free: bool = True,
        max_cost_per_token: float = 0.001,
    ) -> None:
        """Set OpenRouter free models filter settings."""
        if "openrouter" not in self.providers:
            logger.warning("OpenRouter provider not available")
            return

        provider = self.providers["openrouter"]
        if hasattr(provider, "set_free_models_filter"):
            await provider.set_free_models_filter(
                show_free_only, prefer_free, max_cost_per_token
            )
            logger.info(
                f"Updated OpenRouter filter: free_only={show_free_only}, prefer_free={prefer_free}, max_cost={max_cost_per_token}"
            )
        else:
            logger.warning("OpenRouter provider does not support filter settings")

    async def get_openrouter_filter_settings(self) -> dict[str, Any] | None:
        """Get current OpenRouter filter settings."""
        if "openrouter" not in self.providers:
            return None

        provider = self.providers["openrouter"]
        if hasattr(provider, "get_filter_settings"):
            return await provider.get_filter_settings()

        return None

    async def get_model_recommendations(self, task_type: TaskType) -> list[str]:
        """Get model recommendations for a specific task type."""
        return await self.hardware_detector.recommend_models(task_type)

    async def test_model_connectivity(
        self, model_id: str, provider_name: str
    ) -> dict[str, Any]:
        """Test connectivity and performance of a specific model."""
        try:
            # Load the model
            instance = await self.load_model(model_id, provider_name)

            # Perform health check
            health_ok = await instance.health_check()

            # Test generation
            test_request = GenerationRequest(
                prompt="Hello, how are you?", max_tokens=10, temperature=0.0
            )

            start_time = datetime.now()
            response = await instance.generate(test_request)
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "model_id": model_id,
                "provider": provider_name,
                "healthy": health_ok,
                "response_generated": bool(response.text),
                "latency_ms": latency_ms,
                "test_response": (
                    response.text[:100] + "..."
                    if len(response.text) > 100
                    else response.text
                ),
                "status": "success",
            }

        except Exception as e:
            return {
                "model_id": model_id,
                "provider": provider_name,
                "healthy": False,
                "error": str(e),
                "status": "failed",
            }

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "initialized": self.initialized,
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "system_resources": self.system_resources,
            "providers": {},
            "active_models": len(self.active_models),
            "active_model_list": list(self.active_models.keys()),
        }

        # Get provider status
        for name, provider in self.providers.items():
            try:
                provider_metrics = await provider.get_provider_metrics()
                status["providers"][name] = provider_metrics
            except Exception as e:
                status["providers"][name] = {"error": str(e), "healthy": False}

        return status

    def _load_model_config(self) -> ModelManagementConfig:
        """Load model management configuration."""
        try:
            # Get configuration from the main config
            model_config_dict = self.config.get("model_management", {})

            # Create configuration object with defaults
            return ModelManagementConfig(
                enabled=model_config_dict.get("enabled", True),
                default_provider=model_config_dict.get(
                    "default_provider", "openrouter"
                ),
                **model_config_dict,
            )

        except Exception as e:
            logger.warning(f"Failed to load model configuration, using defaults: {e}")
            return ModelManagementConfig()

    async def _initialize_providers(self):
        """Initialize all configured providers."""
        provider_configs = self.model_config.providers

        # Initialize OpenRouter provider
        if "openrouter" in provider_configs and provider_configs["openrouter"].enabled:
            provider = OpenRouterProvider()
            config = provider_configs["openrouter"].__dict__
            if await provider.initialize(config):
                self.providers["openrouter"] = provider
                logger.info("OpenRouter provider initialized")

        # Initialize Ollama provider
        if "ollama" in provider_configs and provider_configs["ollama"].enabled:
            provider = OllamaProvider()
            config = provider_configs["ollama"].__dict__
            if await provider.initialize(config):
                self.providers["ollama"] = provider
                logger.info("Ollama provider initialized")

        # Initialize other providers as needed...

        logger.info(f"Initialized {len(self.providers)} providers")

    async def _initialize_services(self):
        """Initialize core services."""
        # Initialize performance monitor
        self.performance_monitor = PerformanceMonitor()

        # Initialize fallback handler
        self.fallback_handler = FallbackHandler(
            self.providers, self.model_config.fallback_config
        )

        # Initialize model selector
        self.model_selector = ModelSelector(
            self.providers, self.hardware_detector, self.model_config.selection_strategy
        )

        logger.info("Core services initialized")

    async def _perform_health_check(self):
        """Perform health check on all providers and models."""
        try:
            # Check provider health
            for name, provider in self.providers.items():
                healthy = await provider.health_check()
                logger.info(f"Provider {name} health: {'OK' if healthy else 'FAILED'}")

            # Check active model health
            unhealthy_models = []
            for key, instance in self.active_models.items():
                if not await instance.health_check():
                    unhealthy_models.append(key)

            # Remove unhealthy models
            for key in unhealthy_models:
                del self.active_models[key]
                logger.warning(f"Removed unhealthy model: {key}")

            self.last_health_check = datetime.now()

        except Exception as e:
            logger.error(f"Health check failed: {e}")

    # Public API methods for integration with TTA components

    async def generate_text(
        self, prompt: str, task_type: TaskType = TaskType.GENERAL_CHAT, **kwargs
    ) -> GenerationResponse | None:
        """High-level text generation method."""
        try:
            # Create requirements based on task type
            requirements = ModelRequirements(
                task_type=task_type,
                max_latency_ms=kwargs.get("max_latency_ms", 5000),
                min_quality_score=kwargs.get("min_quality_score", 6.0),
            )

            # Select and load model
            model_instance = await self.select_model(requirements)
            if not model_instance:
                return None

            # Create generation request
            request = GenerationRequest(
                prompt=prompt,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                stop_sequences=kwargs.get("stop_sequences"),
                stream=kwargs.get("stream", False),
            )

            # Generate response
            response = await model_instance.generate(request)

            # Record performance metrics
            if self.performance_monitor:
                metrics = PerformanceMetrics(
                    model_id=model_instance.model_id,
                    timestamp=datetime.now(),
                    response_time_ms=response.latency_ms or 0,
                    tokens_per_second=0,  # Would need to calculate
                    total_tokens=(
                        response.usage.get("total_tokens", 0) if response.usage else 0
                    ),
                    task_type=task_type,
                )
                await self.performance_monitor.record_metrics(
                    model_instance.model_id, metrics.__dict__
                )

            return response

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return None
