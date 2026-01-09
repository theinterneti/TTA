"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Models/Providers/Ollama]]
Ollama Provider Implementation.

This module provides integration with Ollama for containerized local model
deployment and management.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import docker
import docker.errors
import docker.types
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


class OllamaModelInstance(BaseModelInstance):
    """Ollama model instance implementation."""

    def __init__(self, model_id: str, provider: "OllamaProvider", client: httpx.AsyncClient):
        super().__init__(model_id, provider)
        self._client = client
        self._status = ModelStatus.READY

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Ollama API."""
        start_time = datetime.now()

        try:
            # Prepare request payload
            payload = {
                "model": self.model_id,
                "prompt": request.prompt,
                "stream": False,
                "options": {},
            }

            # Add generation parameters
            if request.max_tokens:
                payload["options"]["num_predict"] = request.max_tokens
            if request.temperature is not None:
                payload["options"]["temperature"] = request.temperature
            if request.top_p is not None:
                payload["options"]["top_p"] = request.top_p
            if request.stop_sequences:
                payload["options"]["stop"] = request.stop_sequences

            # Make API request
            response = await self._client.post("/api/generate", json=payload, timeout=60.0)
            response.raise_for_status()

            data = response.json()

            # Extract response
            text = data.get("response", "")
            if not text:
                raise ValueError("No response from Ollama")

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Extract usage information
            usage = {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            }

            # Update metrics
            self._update_metrics(
                {
                    "last_request_latency_ms": latency_ms,
                    "last_request_tokens": usage["total_tokens"],
                    "last_request_time": start_time.isoformat(),
                    "eval_duration_ms": data.get("eval_duration", 0)
                    / 1000000,  # Convert from nanoseconds
                    "load_duration_ms": data.get("load_duration", 0) / 1000000,
                }
            )

            return GenerationResponse(
                text=text,
                model_id=self.model_id,
                usage=usage,
                latency_ms=latency_ms,
                metadata={
                    "provider": "ollama",
                    "eval_duration_ms": data.get("eval_duration", 0) / 1000000,
                    "load_duration_ms": data.get("load_duration", 0) / 1000000,
                },
            )

        except Exception as e:
            logger.error(f"Generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate text as a stream using Ollama API."""
        try:
            # Prepare request payload
            payload = {
                "model": self.model_id,
                "prompt": request.prompt,
                "stream": True,
                "options": {},
            }

            # Add generation parameters
            if request.max_tokens:
                payload["options"]["num_predict"] = request.max_tokens
            if request.temperature is not None:
                payload["options"]["temperature"] = request.temperature
            if request.top_p is not None:
                payload["options"]["top_p"] = request.top_p
            if request.stop_sequences:
                payload["options"]["stop"] = request.stop_sequences

            # Make streaming API request
            async with self._client.stream(
                "POST", "/api/generate", json=payload, timeout=120.0
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            response_text = data.get("response", "")

                            if response_text:
                                yield response_text

                            # Check if done
                            if data.get("done", False):
                                break

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Streaming generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise


class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

    def __init__(self):
        super().__init__()
        self._client: httpx.AsyncClient | None = None
        self._docker_client: docker.DockerClient | None = None
        self._ollama_host = "localhost"
        self._ollama_port = 11434
        self._use_docker = True
        self._container_name = "tta-ollama"
        self._docker_image = "ollama/ollama:latest"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate Ollama configuration."""
        self._ollama_host = config.get("host", "localhost")
        self._ollama_port = config.get("port", 11434)
        self._use_docker = config.get("use_docker", True)
        self._container_name = config.get("container_name", "tta-ollama")
        self._docker_image = config.get("docker_image", "ollama/ollama:latest")

        return True

    async def _initialize_provider(self) -> bool:
        """Initialize Ollama provider."""
        try:
            # Initialize Docker client if using Docker
            if self._use_docker:
                self._docker_client = docker.from_env()

                # Start Ollama container if not running
                if not await self._is_ollama_container_running():
                    await self._start_ollama_container()

            # Initialize HTTP client
            base_url = f"http://{self._ollama_host}:{self._ollama_port}"
            self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

            # Wait for Ollama to be ready
            await self._wait_for_ollama_ready()

            logger.info("Ollama provider initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            return False

    async def _refresh_available_models(self) -> None:
        """Refresh available models from Ollama."""
        try:
            if not self._client:
                raise RuntimeError("Ollama client not initialized")

            response = await self._client.get("/api/tags")
            response.raise_for_status()

            data = response.json()
            models = []

            for model_data in data.get("models", []):
                model_id = model_data.get("name", "")
                if not model_id:
                    continue

                # Extract model information
                name = model_id.split(":")[0]  # Remove tag
                size_bytes = model_data.get("size", 0)
                size_gb = size_bytes / (1024**3) if size_bytes else None

                # Estimate context length based on model name
                context_length = self._estimate_context_length(model_id)

                # Determine capabilities based on model name
                capabilities = self._determine_capabilities(model_id)

                model_info = ModelInfo(
                    model_id=model_id,
                    name=name,
                    provider_type=ProviderType.OLLAMA,
                    description=(
                        f"Local Ollama model ({size_gb:.1f}GB)" if size_gb else "Local Ollama model"
                    ),
                    context_length=context_length,
                    cost_per_token=0.0,  # Local models are free
                    is_free=True,
                    capabilities=capabilities,
                    therapeutic_safety_score=None,  # Would need evaluation
                )

                models.append(model_info)

            self._available_models = models
            self._last_model_refresh = datetime.now()

            logger.info(f"Refreshed {len(models)} models from Ollama")

        except Exception as e:
            logger.error(f"Failed to refresh Ollama models: {e}")
            raise

    async def _load_model_impl(self, model_id: str, config: dict[str, Any]) -> OllamaModelInstance:
        """Load an Ollama model instance."""
        if not self._client:
            raise RuntimeError("Ollama client not initialized")

        # Check if model is available locally
        available_model_ids = [m.model_id for m in self._available_models]
        if model_id not in available_model_ids:
            # Try to pull the model
            logger.info(f"Model {model_id} not found locally, attempting to pull...")
            await self._pull_model(model_id)

            # Refresh available models
            await self._refresh_available_models()

            # Check again
            available_model_ids = [m.model_id for m in self._available_models]
            if model_id not in available_model_ids:
                raise ValueError(f"Failed to pull model {model_id}")

        return OllamaModelInstance(model_id, self, self._client)

    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Unload an Ollama model instance."""
        # Ollama manages model loading/unloading automatically
        pass

    async def _provider_health_check(self) -> bool:
        """Check Ollama service health."""
        try:
            if not self._client:
                return False

            response = await self._client.get("/api/tags", timeout=5.0)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    async def _is_ollama_container_running(self) -> bool:
        """Check if Ollama container is running."""
        if not self._docker_client:
            return False

        try:
            container = self._docker_client.containers.get(self._container_name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False
        except Exception as e:
            logger.warning(f"Failed to check Ollama container status: {e}")
            return False

    async def _start_ollama_container(self) -> None:
        """Start Ollama Docker container."""
        if not self._docker_client:
            raise RuntimeError("Docker client not initialized")

        try:
            # Check if container exists
            try:
                container = self._docker_client.containers.get(self._container_name)
                if container.status != "running":
                    container.start()
                    logger.info(f"Started existing Ollama container: {self._container_name}")
                return
            except docker.errors.NotFound:
                pass

            # Create and start new container
            volumes = {"ollama_data": {"bind": "/root/.ollama", "mode": "rw"}}

            ports = {f"{self._ollama_port}/tcp": self._ollama_port}

            # Add GPU support if available
            device_requests = []
            with contextlib.suppress(Exception):
                # Check if NVIDIA runtime is available
                runtime_info = self._docker_client.info()
                if "nvidia" in runtime_info.get("Runtimes", {}):
                    device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]

            # Type ignore for docker-py API compatibility (restart_policy dict format)
            container = self._docker_client.containers.run(
                self._docker_image,
                name=self._container_name,
                ports=ports,
                volumes=volumes,
                device_requests=device_requests if device_requests else None,
                detach=True,
                restart_policy={"Name": "unless-stopped"},  # type: ignore
            )

            logger.info(f"Created and started Ollama container: {self._container_name}")

        except Exception as e:
            logger.error(f"Failed to start Ollama container: {e}")
            raise

    async def _wait_for_ollama_ready(self, timeout_seconds: int = 60) -> None:
        """Wait for Ollama service to be ready."""
        for _ in range(timeout_seconds):
            try:
                if await self._provider_health_check():
                    return
                await asyncio.sleep(1)
            except Exception:
                await asyncio.sleep(1)

        raise TimeoutError("Ollama service did not become ready within timeout")

    async def _pull_model(self, model_id: str) -> None:
        """Pull a model from Ollama registry."""
        try:
            if not self._client:
                raise RuntimeError("Ollama client not initialized")

            payload = {"name": model_id}

            # Make pull request (this can take a long time)
            async with self._client.stream(
                "POST",
                "/api/pull",
                json=payload,
                timeout=1800.0,  # 30 minutes timeout
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            status = data.get("status", "")

                            if "error" in data:
                                raise RuntimeError(f"Pull failed: {data['error']}")

                            # Log progress
                            if status:
                                logger.info(f"Pulling {model_id}: {status}")

                            # Check if completed
                            if data.get("status") == "success":
                                break

                        except json.JSONDecodeError:
                            continue

            logger.info(f"Successfully pulled model: {model_id}")

        except Exception as e:
            logger.error(f"Failed to pull model {model_id}: {e}")
            raise

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
        return 4096  # Default assumption

    def _determine_capabilities(self, model_id: str) -> list[str]:
        """Determine model capabilities based on model name."""
        capabilities = ["text_generation"]
        model_lower = model_id.lower()

        if "instruct" in model_lower or "chat" in model_lower:
            capabilities.extend(["instruction_following", "chat"])

        if "code" in model_lower:
            capabilities.append("code_generation")

        if "vision" in model_lower:
            capabilities.append("vision")

        return capabilities

    async def cleanup(self):
        """Cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

        # Note: Docker container is intentionally kept running for reuse
