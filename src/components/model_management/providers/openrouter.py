"""

# Logseq: [[TTA.dev/Components/Model_management/Providers/Openrouter]]
OpenRouter Provider Implementation.

This module provides integration with OpenRouter API for accessing
cloud-based AI models with free model filtering capabilities.
"""

import logging
import os
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import httpx

from ..interfaces import (
    GenerationRequest,
    GenerationResponse,
    IModelInstance,
    ModelInfo,
    ModelStatus,
    ProviderType,
)
from .base import BaseModelInstance, BaseProvider

logger = logging.getLogger(__name__)


class OpenRouterModelInstance(BaseModelInstance):
    """OpenRouter model instance implementation."""

    def __init__(
        self, model_id: str, provider: "OpenRouterProvider", client: httpx.AsyncClient
    ):
        super().__init__(model_id, provider)
        self._client = client
        self._status = ModelStatus.READY

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using OpenRouter API."""
        start_time = datetime.now()

        try:
            # Prepare request payload
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or 2048,
                "temperature": request.temperature or 0.7,
                "top_p": request.top_p or 0.9,
                "stream": False,
            }

            if request.stop_sequences:
                payload["stop"] = request.stop_sequences

            # Make API request
            response = await self._client.post(
                "/api/v1/chat/completions", json=payload, timeout=30.0
            )
            response.raise_for_status()

            data = response.json()

            # Extract response
            if "choices" not in data or not data["choices"]:
                raise ValueError("No choices in OpenRouter response")

            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Update metrics
            self._update_metrics(
                {
                    "last_request_latency_ms": latency_ms,
                    "last_request_tokens": usage.get("total_tokens", 0),
                    "last_request_time": start_time.isoformat(),
                }
            )

            return GenerationResponse(
                text=text,
                model_id=self.model_id,
                usage=usage,
                latency_ms=latency_ms,
                metadata={"provider": "openrouter"},
            )

        except Exception as e:
            logger.error(f"Generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def generate_stream(
        self, request: GenerationRequest
    ) -> AsyncGenerator[str, None]:
        """Generate text as a stream using OpenRouter API."""
        try:
            # Prepare request payload
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or 2048,
                "temperature": request.temperature or 0.7,
                "top_p": request.top_p or 0.9,
                "stream": True,
            }

            if request.stop_sequences:
                payload["stop"] = request.stop_sequences

            # Make streaming API request
            async with self._client.stream(
                "POST", "/api/v1/chat/completions", json=payload, timeout=60.0
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str.strip() == "[DONE]":
                            break

                        try:
                            import json

                            data = json.loads(data_str)

                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Streaming generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider implementation with free models filtering."""

    def __init__(self):
        super().__init__()
        self._client: httpx.AsyncClient | None = None
        self._api_key: str | None = None
        self._base_url = "https://openrouter.ai"

        # Free models filter configuration
        self._show_free_only = False
        self._prefer_free_models = True
        self._max_cost_per_token = 0.001

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate OpenRouter configuration."""
        api_key = config.get("api_key")
        if not api_key:
            logger.error("OpenRouter API key is required")
            return False

        self._api_key = api_key
        self._base_url = config.get("base_url", "https://openrouter.ai")

        # Load free models filter configuration from environment or config
        self._show_free_only = self._get_bool_config(
            "show_free_only", "OPENROUTER_SHOW_FREE_ONLY", False
        )
        self._prefer_free_models = self._get_bool_config(
            "prefer_free_models", "OPENROUTER_PREFER_FREE_MODELS", True
        )
        self._max_cost_per_token = self._get_float_config(
            "max_cost_per_token", "OPENROUTER_MAX_COST_PER_TOKEN", 0.001
        )

        logger.info(
            f"OpenRouter free models filter: show_free_only={self._show_free_only}, "
            f"prefer_free={self._prefer_free_models}, max_cost={self._max_cost_per_token}"
        )

        return True

    def _get_bool_config(self, config_key: str, env_key: str, default: bool) -> bool:
        """Get boolean configuration from config or environment."""
        # First check the config dict
        if hasattr(self, "_config") and config_key in self._config:
            value = self._config[config_key]
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")

        # Then check environment variables
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes", "on")

        return default

    def _get_float_config(self, config_key: str, env_key: str, default: float) -> float:
        """Get float configuration from config or environment."""
        # First check the config dict
        if hasattr(self, "_config") and config_key in self._config:
            try:
                return float(self._config[config_key])
            except (ValueError, TypeError):
                pass

        # Then check environment variables
        env_value = os.getenv(env_key)
        if env_value is not None:
            try:
                return float(env_value)
            except (ValueError, TypeError):
                pass

        return default

    async def _initialize_provider(self) -> bool:
        """Initialize OpenRouter client."""
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://tta-platform.com",  # Optional: your site URL
                "X-Title": "TTA Platform",  # Optional: your app name
            }

            self._client = httpx.AsyncClient(
                base_url=self._base_url, headers=headers, timeout=30.0
            )

            # Test connection
            response = await self._client.get("/api/v1/models")
            response.raise_for_status()

            logger.info("OpenRouter client initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {e}")
            return False

    async def _refresh_available_models(self) -> None:
        """Refresh available models from OpenRouter."""
        try:
            if not self._client:
                raise RuntimeError("OpenRouter client not initialized")

            response = await self._client.get("/api/v1/models")
            response.raise_for_status()

            data = response.json()
            models = []

            for model_data in data.get("data", []):
                # Extract model information
                model_id = model_data.get("id", "")
                name = model_data.get("name", model_id)
                description = model_data.get("description", "")

                # Pricing information
                pricing = model_data.get("pricing", {})
                prompt_cost = pricing.get("prompt")
                completion_cost = pricing.get("completion")

                # Calculate average cost per token (if available)
                cost_per_token = None
                is_free = False

                if prompt_cost is not None and completion_cost is not None:
                    # Convert from cost per million tokens to cost per token
                    cost_per_token = (
                        float(prompt_cost) + float(completion_cost)
                    ) / 2000000
                    is_free = cost_per_token == 0.0
                elif prompt_cost == "0" and completion_cost == "0":
                    is_free = True
                    cost_per_token = 0.0

                # Context length
                context_length = model_data.get("context_length")

                # Capabilities (inferred from model name/description)
                capabilities = []
                if "chat" in model_id.lower() or "instruct" in model_id.lower():
                    capabilities.extend(["chat", "instruction_following"])
                if "code" in model_id.lower():
                    capabilities.append("code_generation")

                model_info = ModelInfo(
                    model_id=model_id,
                    name=name,
                    provider_type=ProviderType.OPENROUTER,
                    description=description,
                    context_length=context_length,
                    cost_per_token=cost_per_token,
                    is_free=is_free,
                    capabilities=capabilities,
                    therapeutic_safety_score=None,  # Would need separate evaluation
                )

                models.append(model_info)

            self._available_models = models
            self._last_model_refresh = datetime.now()

            logger.info(f"Refreshed {len(models)} models from OpenRouter")

        except Exception as e:
            logger.error(f"Failed to refresh OpenRouter models: {e}")
            raise

    async def _load_model_impl(
        self, model_id: str, config: dict[str, Any]
    ) -> OpenRouterModelInstance:
        """Load an OpenRouter model instance."""
        if not self._client:
            raise RuntimeError("OpenRouter client not initialized")

        # Verify model exists
        available_model_ids = [m.model_id for m in self._available_models]
        if model_id not in available_model_ids:
            raise ValueError(f"Model {model_id} not available in OpenRouter")

        return OpenRouterModelInstance(model_id, self, self._client)

    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Unload an OpenRouter model instance."""
        # OpenRouter models don't need explicit unloading
        pass

    async def _provider_health_check(self) -> bool:
        """Check OpenRouter API health."""
        try:
            if not self._client:
                return False

            response = await self._client.get("/api/v1/models", timeout=5.0)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"OpenRouter health check failed: {e}")
            return False

    async def get_available_models(
        self, filters: dict[str, Any] | None = None
    ) -> list[ModelInfo]:
        """Get available models with optional free models filtering."""
        # Get all models from base implementation
        all_models = await super().get_available_models(filters)

        # Apply free models filter if enabled
        if self._show_free_only:
            filtered_models = [model for model in all_models if model.is_free]
            logger.info(
                f"Filtered to {len(filtered_models)} free models out of {len(all_models)} total"
            )
            return filtered_models

        # If prefer_free_models is enabled, sort free models first
        if self._prefer_free_models:
            free_models = [model for model in all_models if model.is_free]
            paid_models = [model for model in all_models if not model.is_free]

            # Further filter paid models by max cost if specified
            if self._max_cost_per_token > 0:
                affordable_paid_models = [
                    model
                    for model in paid_models
                    if model.cost_per_token is not None
                    and model.cost_per_token <= self._max_cost_per_token
                ]
                logger.info(
                    f"Filtered paid models: {len(affordable_paid_models)} affordable out of {len(paid_models)} total"
                )
                paid_models = affordable_paid_models

            # Return free models first, then affordable paid models
            sorted_models = free_models + paid_models
            logger.info(
                f"Sorted models: {len(free_models)} free + {len(paid_models)} paid = {len(sorted_models)} total"
            )
            return sorted_models

        return all_models

    async def get_free_models(self) -> list[ModelInfo]:
        """Get only free models from OpenRouter."""
        all_models = await super().get_available_models()
        return [model for model in all_models if model.is_free]

    async def get_affordable_models(
        self, max_cost_per_token: float | None = None
    ) -> list[ModelInfo]:
        """Get models within the specified cost threshold."""
        if max_cost_per_token is None:
            max_cost_per_token = self._max_cost_per_token

        all_models = await super().get_available_models()
        affordable_models = []

        for model in all_models:
            if model.is_free or (
                model.cost_per_token is not None
                and model.cost_per_token <= max_cost_per_token
            ):
                affordable_models.append(model)

        return affordable_models

    async def set_free_models_filter(
        self,
        show_free_only: bool = False,
        prefer_free: bool = True,
        max_cost_per_token: float = 0.001,
    ) -> None:
        """Dynamically update free models filter settings."""
        self._show_free_only = show_free_only
        self._prefer_free_models = prefer_free
        self._max_cost_per_token = max_cost_per_token

        logger.info(
            f"Updated free models filter: show_free_only={show_free_only}, "
            f"prefer_free={prefer_free}, max_cost={max_cost_per_token}"
        )

    async def get_filter_settings(self) -> dict[str, Any]:
        """Get current filter settings."""
        return {
            "show_free_only": self._show_free_only,
            "prefer_free_models": self._prefer_free_models,
            "max_cost_per_token": self._max_cost_per_token,
        }

    async def estimate_cost(self, model_id: str, estimated_tokens: int) -> float | None:
        """Estimate cost for using a specific model."""
        models = await self.get_available_models()

        for model in models:
            if model.model_id == model_id:
                if model.cost_per_token is not None:
                    return model.cost_per_token * estimated_tokens
                break

        return None

    async def cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
