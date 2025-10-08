"""
Custom API Provider Implementation.

This module provides support for custom API providers like OpenAI, Anthropic,
and other compatible APIs.
"""

import logging
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


class CustomAPIModelInstance(BaseModelInstance):
    """Custom API model instance implementation."""

    def __init__(
        self,
        model_id: str,
        provider: "CustomAPIProvider",
        client: httpx.AsyncClient,
        api_config: dict[str, Any],
    ):
        super().__init__(model_id, provider)
        self._client = client
        self._api_config = api_config
        self._status = ModelStatus.READY

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using custom API."""
        start_time = datetime.now()

        try:
            # Prepare request based on API type
            if self._api_config.get("api_type") == "anthropic":
                payload = await self._prepare_anthropic_request(request)
                endpoint = "/v1/messages"
            else:
                # Default to OpenAI-compatible format
                payload = await self._prepare_openai_request(request)
                endpoint = "/v1/chat/completions"

            # Make API request
            response = await self._client.post(endpoint, json=payload, timeout=60.0)
            response.raise_for_status()

            data = response.json()

            # Extract response based on API type
            if self._api_config.get("api_type") == "anthropic":
                text = self._extract_anthropic_response(data)
                usage = self._extract_anthropic_usage(data)
            else:
                text = self._extract_openai_response(data)
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
                metadata={
                    "provider": "custom_api",
                    "api_type": self._api_config.get("api_type", "openai"),
                },
            )

        except Exception as e:
            logger.error(f"Generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def generate_stream(
        self, request: GenerationRequest
    ) -> AsyncGenerator[str, None]:
        """Generate text as a stream using custom API."""
        try:
            # Prepare request based on API type
            if self._api_config.get("api_type") == "anthropic":
                payload = await self._prepare_anthropic_request(request, stream=True)
                endpoint = "/v1/messages"
            else:
                payload = await self._prepare_openai_request(request, stream=True)
                endpoint = "/v1/chat/completions"

            # Make streaming API request
            async with self._client.stream(
                "POST", endpoint, json=payload, timeout=120.0
            ) as response:
                response.raise_for_status()

                if self._api_config.get("api_type") == "anthropic":
                    async for chunk in self._stream_anthropic_response(response):
                        yield chunk
                else:
                    async for chunk in self._stream_openai_response(response):
                        yield chunk

        except Exception as e:
            logger.error(f"Streaming generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def _prepare_openai_request(
        self, request: GenerationRequest, stream: bool = False
    ) -> dict[str, Any]:
        """Prepare OpenAI-compatible request."""
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens or 2048,
            "temperature": request.temperature or 0.7,
            "top_p": request.top_p or 0.9,
            "stream": stream,
        }

        if request.stop_sequences:
            payload["stop"] = request.stop_sequences

        return payload

    async def _prepare_anthropic_request(
        self, request: GenerationRequest, stream: bool = False
    ) -> dict[str, Any]:
        """Prepare Anthropic-compatible request."""
        payload = {
            "model": self.model_id,
            "max_tokens": request.max_tokens or 2048,
            "messages": [{"role": "user", "content": request.prompt}],
            "stream": stream,
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop_sequences:
            payload["stop_sequences"] = request.stop_sequences

        return payload

    def _extract_openai_response(self, data: dict[str, Any]) -> str:
        """Extract text from OpenAI response."""
        if "choices" not in data or not data["choices"]:
            raise ValueError("No choices in API response")

        return data["choices"][0]["message"]["content"]

    def _extract_anthropic_response(self, data: dict[str, Any]) -> str:
        """Extract text from Anthropic response."""
        if "content" not in data or not data["content"]:
            raise ValueError("No content in Anthropic response")

        # Anthropic returns content as a list
        content_blocks = data["content"]
        if isinstance(content_blocks, list) and len(content_blocks) > 0:
            return content_blocks[0].get("text", "")

        return str(content_blocks)

    def _extract_anthropic_usage(self, data: dict[str, Any]) -> dict[str, int]:
        """Extract usage information from Anthropic response."""
        usage = data.get("usage", {})
        return {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0)
            + usage.get("output_tokens", 0),
        }

    async def _stream_openai_response(self, response) -> AsyncGenerator[str, None]:
        """Stream OpenAI response."""
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

    async def _stream_anthropic_response(self, response) -> AsyncGenerator[str, None]:
        """Stream Anthropic response."""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix

                try:
                    import json

                    data = json.loads(data_str)

                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue


class CustomAPIProvider(BaseProvider):
    """Custom API provider implementation."""

    def __init__(self):
        super().__init__()
        self._clients: dict[str, httpx.AsyncClient] = {}
        self._api_configs: dict[str, dict[str, Any]] = {}

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CUSTOM_API

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate custom API configuration."""
        custom_providers = config.get("custom_providers", {})

        for provider_name, provider_config in custom_providers.items():
            api_key = provider_config.get("api_key")
            base_url = provider_config.get("base_url")

            if not api_key or not base_url:
                logger.error(
                    f"Missing api_key or base_url for provider {provider_name}"
                )
                return False

            self._api_configs[provider_name] = provider_config

        return len(self._api_configs) > 0

    async def _initialize_provider(self) -> bool:
        """Initialize custom API clients."""
        try:
            for provider_name, config in self._api_configs.items():
                # Prepare headers
                headers = {"Content-Type": "application/json"}

                # Add authorization header based on API type
                api_type = config.get("api_type", "openai")
                api_key = config["api_key"]

                if api_type == "anthropic":
                    headers["x-api-key"] = api_key
                    headers["anthropic-version"] = "2023-06-01"
                else:
                    # Default to OpenAI-style authorization
                    headers["Authorization"] = f"Bearer {api_key}"

                # Create client
                client = httpx.AsyncClient(
                    base_url=config["base_url"], headers=headers, timeout=30.0
                )

                self._clients[provider_name] = client

                # Test connection
                await self._test_provider_connection(provider_name, config)

                logger.info(f"Initialized custom API provider: {provider_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize custom API providers: {e}")
            return False

    async def _refresh_available_models(self) -> None:
        """Refresh available models from custom APIs."""
        try:
            models = []

            for provider_name, config in self._api_configs.items():
                try:
                    provider_models = await self._get_provider_models(
                        provider_name, config
                    )
                    models.extend(provider_models)
                except Exception as e:
                    logger.warning(f"Failed to get models from {provider_name}: {e}")

            self._available_models = models
            self._last_model_refresh = datetime.now()

            logger.info(f"Refreshed {len(models)} models from custom APIs")

        except Exception as e:
            logger.error(f"Failed to refresh custom API models: {e}")
            raise

    async def _get_provider_models(
        self, provider_name: str, config: dict[str, Any]
    ) -> list[ModelInfo]:
        """Get models from a specific provider."""
        client = self._clients.get(provider_name)
        if not client:
            return []

        try:
            # Try to get models list (not all APIs support this)
            response = await client.get("/v1/models", timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                models = []

                for model_data in data.get("data", []):
                    model_id = model_data.get("id", "")
                    if not model_id:
                        continue

                    # Determine pricing and capabilities based on provider
                    cost_per_token, is_free = self._get_model_pricing(
                        provider_name, model_id
                    )
                    capabilities = self._get_model_capabilities(provider_name, model_id)
                    context_length = self._get_model_context_length(
                        provider_name, model_id
                    )

                    model_info = ModelInfo(
                        model_id=model_id,
                        name=model_data.get("object", model_id),
                        provider_type=ProviderType.CUSTOM_API,
                        description=f"{provider_name} model: {model_id}",
                        context_length=context_length,
                        cost_per_token=cost_per_token,
                        is_free=is_free,
                        capabilities=capabilities,
                        therapeutic_safety_score=self._get_therapeutic_safety_score(
                            provider_name, model_id
                        ),
                    )

                    models.append(model_info)

                return models
            # Fallback to predefined models for this provider
            return self._get_predefined_models(provider_name, config)

        except Exception as e:
            logger.warning(
                f"Failed to fetch models from {provider_name}, using predefined list: {e}"
            )
            return self._get_predefined_models(provider_name, config)

    def _get_predefined_models(
        self, provider_name: str, config: dict[str, Any]
    ) -> list[ModelInfo]:
        """Get predefined models for providers that don't support model listing."""
        api_type = config.get("api_type", "openai")

        if api_type == "anthropic":
            return [
                ModelInfo(
                    model_id="claude-3-haiku-20240307",
                    name="Claude 3 Haiku",
                    provider_type=ProviderType.CUSTOM_API,
                    description="Fast and efficient Claude model",
                    context_length=200000,
                    cost_per_token=0.00000025,  # $0.25 per million tokens
                    is_free=False,
                    capabilities=["chat", "instruction_following", "analysis"],
                    therapeutic_safety_score=9.0,
                ),
                ModelInfo(
                    model_id="claude-3-sonnet-20240229",
                    name="Claude 3 Sonnet",
                    provider_type=ProviderType.CUSTOM_API,
                    description="Balanced Claude model",
                    context_length=200000,
                    cost_per_token=0.000003,  # $3 per million tokens
                    is_free=False,
                    capabilities=[
                        "chat",
                        "instruction_following",
                        "analysis",
                        "creative_writing",
                    ],
                    therapeutic_safety_score=9.5,
                ),
            ]
        # OpenAI-compatible
        return [
            ModelInfo(
                model_id="gpt-4o-mini",
                name="GPT-4o Mini",
                provider_type=ProviderType.CUSTOM_API,
                description="Efficient GPT-4 model",
                context_length=128000,
                cost_per_token=0.00000015,  # $0.15 per million tokens
                is_free=False,
                capabilities=["chat", "instruction_following", "analysis"],
                therapeutic_safety_score=8.0,
            ),
            ModelInfo(
                model_id="gpt-4o",
                name="GPT-4o",
                provider_type=ProviderType.CUSTOM_API,
                description="Advanced GPT-4 model",
                context_length=128000,
                cost_per_token=0.000005,  # $5 per million tokens
                is_free=False,
                capabilities=[
                    "chat",
                    "instruction_following",
                    "analysis",
                    "creative_writing",
                ],
                therapeutic_safety_score=8.5,
            ),
        ]

    async def _load_model_impl(
        self, model_id: str, config: dict[str, Any]
    ) -> CustomAPIModelInstance:
        """Load a custom API model instance."""
        # Find which provider has this model
        provider_name = None
        api_config = None

        for prov_name, prov_config in self._api_configs.items():
            # Check if this provider has the model
            # For now, assume all providers can handle any model ID
            provider_name = prov_name
            api_config = prov_config
            break

        if not provider_name or not api_config:
            raise ValueError(f"No provider found for model {model_id}")

        client = self._clients.get(provider_name)
        if not client:
            raise RuntimeError(f"Client not initialized for provider {provider_name}")

        return CustomAPIModelInstance(model_id, self, client, api_config)

    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Unload a custom API model instance."""
        # API models don't need explicit unloading
        pass

    async def _provider_health_check(self) -> bool:
        """Check custom API providers health."""
        healthy_count = 0
        total_count = len(self._clients)

        for _, client in self._clients.items():
            try:
                # Simple health check - try to get models
                response = await client.get("/v1/models", timeout=5.0)
                if response.status_code == 200:
                    healthy_count += 1
            except Exception:
                pass

        # Consider healthy if at least half of providers are working
        return healthy_count >= (total_count / 2) if total_count > 0 else False

    async def _test_provider_connection(
        self, provider_name: str, config: dict[str, Any]
    ):
        """Test connection to a provider."""
        client = self._clients.get(provider_name)
        if not client:
            raise RuntimeError(f"Client not found for {provider_name}")

        try:
            response = await client.get("/v1/models", timeout=10.0)
            if response.status_code not in [
                200,
                404,
            ]:  # 404 is OK if models endpoint not supported
                raise RuntimeError(
                    f"Provider {provider_name} returned status {response.status_code}"
                )
        except httpx.TimeoutException:
            raise RuntimeError(f"Provider {provider_name} connection timeout") from None

    def _get_model_pricing(
        self, provider_name: str, model_id: str
    ) -> tuple[float | None, bool]:
        """Get pricing information for a model."""
        # This would typically be configured or fetched from the provider
        # For now, return reasonable defaults
        return 0.000001, False  # $1 per million tokens, not free

    def _get_model_capabilities(self, provider_name: str, model_id: str) -> list[str]:
        """Get capabilities for a model."""
        capabilities = ["text_generation", "chat"]

        if "instruct" in model_id.lower():
            capabilities.append("instruction_following")
        if "code" in model_id.lower():
            capabilities.append("code_generation")
        if "claude" in model_id.lower():
            capabilities.extend(["analysis", "creative_writing"])

        return capabilities

    def _get_model_context_length(
        self, provider_name: str, model_id: str
    ) -> int | None:
        """Get context length for a model."""
        # Common context lengths
        if "gpt-4" in model_id.lower():
            return 128000
        if "claude-3" in model_id.lower():
            return 200000
        return 4096  # Default

    def _get_therapeutic_safety_score(
        self, provider_name: str, model_id: str
    ) -> float | None:
        """Get therapeutic safety score for a model."""
        if "claude" in model_id.lower():
            return 9.0  # Claude models are generally very safe
        if "gpt-4" in model_id.lower():
            return 8.0  # GPT-4 models are quite safe
        return 7.0  # Default moderate safety score

    async def cleanup(self):
        """Cleanup resources."""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()
