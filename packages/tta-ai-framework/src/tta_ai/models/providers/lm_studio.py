"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Models/Providers/Lm_studio]]
LM Studio Provider Implementation.

This module provides integration with LM Studio for local model hosting.
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


class LMStudioModelInstance(BaseModelInstance):
    """LM Studio model instance implementation."""

    def __init__(self, model_id: str, provider: "LMStudioProvider", client: httpx.AsyncClient):
        super().__init__(model_id, provider)
        self._client = client
        self._status = ModelStatus.READY

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using LM Studio API."""
        start_time = datetime.now()

        try:
            # Prepare request payload (OpenAI-compatible format)
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
            response = await self._client.post("/v1/chat/completions", json=payload, timeout=60.0)
            response.raise_for_status()

            data = response.json()

            # Extract response
            if "choices" not in data or not data["choices"]:
                raise ValueError("No choices in LM Studio response")

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
                metadata={"provider": "lm_studio"},
            )

        except Exception as e:
            logger.error(f"Generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate text as a stream using LM Studio API."""
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
                "POST", "/v1/chat/completions", json=payload, timeout=120.0
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


class LMStudioProvider(BaseProvider):
    """LM Studio provider implementation."""

    def __init__(self):
        super().__init__()
        self._client: httpx.AsyncClient | None = None
        self._base_url = "http://localhost:1234"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LM_STUDIO

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate LM Studio configuration."""
        self._base_url = config.get("base_url", "http://localhost:1234")
        return True

    async def _initialize_provider(self) -> bool:
        """Initialize LM Studio client."""
        try:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

            # Test connection
            response = await self._client.get("/v1/models")
            response.raise_for_status()

            logger.info("LM Studio client initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LM Studio client: {e}")
            return False

    async def _refresh_available_models(self) -> None:
        """Refresh available models from LM Studio."""
        try:
            if not self._client:
                raise RuntimeError("LM Studio client not initialized")

            response = await self._client.get("/v1/models")
            response.raise_for_status()

            data = response.json()
            models = []

            for model_data in data.get("data", []):
                model_id = model_data.get("id", "")
                if not model_id:
                    continue

                # Extract model information
                name = model_data.get("object", model_id)

                # Estimate context length based on model name
                context_length = self._estimate_context_length(model_id)

                # Determine capabilities
                capabilities = ["text_generation", "chat"]
                if "instruct" in model_id.lower():
                    capabilities.append("instruction_following")
                if "code" in model_id.lower():
                    capabilities.append("code_generation")

                model_info = ModelInfo(
                    model_id=model_id,
                    name=name,
                    provider_type=ProviderType.LM_STUDIO,
                    description=f"Local LM Studio model: {model_id}",
                    context_length=context_length,
                    cost_per_token=0.0,  # Local models are free
                    is_free=True,
                    capabilities=capabilities,
                    therapeutic_safety_score=None,  # Would need evaluation
                )

                models.append(model_info)

            self._available_models = models
            self._last_model_refresh = datetime.now()

            logger.info(f"Refreshed {len(models)} models from LM Studio")

        except Exception as e:
            logger.error(f"Failed to refresh LM Studio models: {e}")
            raise

    async def _load_model_impl(
        self, model_id: str, config: dict[str, Any]
    ) -> LMStudioModelInstance:
        """Load an LM Studio model instance."""
        if not self._client:
            raise RuntimeError("LM Studio client not initialized")

        # Verify model exists
        available_model_ids = [m.model_id for m in self._available_models]
        if model_id not in available_model_ids:
            raise ValueError(f"Model {model_id} not available in LM Studio")

        return LMStudioModelInstance(model_id, self, self._client)

    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Unload an LM Studio model instance."""
        # LM Studio manages model loading/unloading automatically
        pass

    async def _provider_health_check(self) -> bool:
        """Check LM Studio service health."""
        try:
            if not self._client:
                return False

            response = await self._client.get("/v1/models", timeout=5.0)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"LM Studio health check failed: {e}")
            return False

    def _estimate_context_length(self, model_id: str) -> int | None:
        """Estimate context length based on model name."""
        model_lower = model_id.lower()

        # Common context lengths for known models
        if "llama" in model_lower:
            if "3.1" in model_lower or "3.2" in model_lower:
                return 128000  # Llama 3.1/3.2 has 128k context
            return 4096  # Older Llama models
        if "qwen" in model_lower:
            return 32768  # Qwen models typically have 32k context
        if "mistral" in model_lower:
            return 32768  # Mistral models
        if "phi" in model_lower:
            return 4096  # Phi models
        if "gemma" in model_lower:
            return 8192  # Gemma models
        return 4096  # Default assumption

    async def cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
