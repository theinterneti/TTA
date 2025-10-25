"""
Local Model Provider Implementation.

This module provides local model management with hardware optimization
using Hugging Face Transformers.
"""

import asyncio
import gc
import logging
import os
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import psutil
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

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


class LocalModelInstance(BaseModelInstance):
    """Local model instance implementation."""

    def __init__(
        self,
        model_id: str,
        provider: "LocalModelProvider",
        model,
        tokenizer,
        device: str,
    ):
        super().__init__(model_id, provider)
        self._model = model
        self._tokenizer = tokenizer
        self._device = device
        self._status = ModelStatus.READY
        self._pipeline = None

        # Create text generation pipeline
        try:
            self._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=device,
                torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            )
        except Exception as e:
            logger.warning(f"Failed to create pipeline for {model_id}: {e}")

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using local model."""
        start_time = datetime.now()

        try:
            # Prepare generation parameters
            generation_kwargs = {
                "max_new_tokens": request.max_tokens or 2048,
                "temperature": request.temperature or 0.7,
                "top_p": request.top_p or 0.9,
                "do_sample": True,
                "pad_token_id": self._tokenizer.eos_token_id,
                "return_full_text": False,
            }

            if request.stop_sequences:
                # Note: Transformers doesn't directly support stop sequences
                # This would need custom implementation
                pass

            # Generate text
            if self._pipeline:
                # Use pipeline for generation
                pipeline_fn = self._pipeline
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: pipeline_fn(request.prompt, **generation_kwargs)
                )

                if result and len(result) > 0:
                    generated_text = result[0]["generated_text"]
                else:
                    generated_text = ""
            else:
                # Direct model generation
                inputs = self._tokenizer.encode(request.prompt, return_tensors="pt").to(
                    self._device
                )

                with torch.no_grad():
                    outputs = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: self._model.generate(inputs, **generation_kwargs)
                    )

                generated_text = self._tokenizer.decode(
                    outputs[0][inputs.shape[1] :], skip_special_tokens=True
                )

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Estimate token usage
            prompt_tokens = len(self._tokenizer.encode(request.prompt))
            completion_tokens = len(self._tokenizer.encode(generated_text))
            total_tokens = prompt_tokens + completion_tokens

            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }

            # Update metrics
            self._update_metrics(
                {
                    "last_request_latency_ms": latency_ms,
                    "last_request_tokens": total_tokens,
                    "last_request_time": start_time.isoformat(),
                    "device": self._device,
                }
            )

            return GenerationResponse(
                text=generated_text,
                model_id=self.model_id,
                usage=usage,
                latency_ms=latency_ms,
                metadata={"provider": "local", "device": self._device},
            )

        except Exception as e:
            logger.error(f"Generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise

    async def generate_stream(self, request: GenerationRequest) -> AsyncGenerator[str, None]:
        """Generate text as a stream (simplified implementation)."""
        try:
            # For now, generate full text and yield in chunks
            # A proper streaming implementation would require custom generation loop
            response = await self.generate(request)

            # Yield text in chunks
            text = response.text
            chunk_size = 10  # Characters per chunk

            for i in range(0, len(text), chunk_size):
                chunk = text[i : i + chunk_size]
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to simulate streaming

        except Exception as e:
            logger.error(f"Streaming generation failed for {self.model_id}: {e}")
            self._status = ModelStatus.ERROR
            raise


class LocalModelProvider(BaseProvider):
    """Local model provider implementation."""

    def __init__(self):
        super().__init__()
        self._models_cache_dir = "./models"
        self._max_concurrent_models = 2
        self._auto_quantization = True
        self._gpu_memory_fraction = 0.8
        self._device_map = None
        self._loaded_model_count = 0

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LOCAL

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        """Validate local model configuration."""
        self._models_cache_dir = config.get("models_cache_dir", "./models")
        self._max_concurrent_models = config.get("max_concurrent_models", 2)
        self._auto_quantization = config.get("auto_quantization", True)
        self._gpu_memory_fraction = config.get("gpu_memory_fraction", 0.8)

        # Create cache directory if it doesn't exist
        os.makedirs(self._models_cache_dir, exist_ok=True)

        return True

    async def _initialize_provider(self) -> bool:
        """Initialize local model provider."""
        try:
            # Check PyTorch installation
            if not torch.cuda.is_available():
                logger.info("CUDA not available, will use CPU for local models")
            else:
                gpu_count = torch.cuda.device_count()
                logger.info(f"CUDA available with {gpu_count} GPU(s)")

            # Set up device mapping
            self._setup_device_mapping()

            logger.info("Local model provider initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize local model provider: {e}")
            return False

    async def _refresh_available_models(self) -> None:
        """Refresh available local models."""
        try:
            # For now, return a curated list of recommended local models
            # In a full implementation, this could scan the cache directory
            # or query Hugging Face Hub for compatible models

            models = [
                ModelInfo(
                    model_id="microsoft/DialoGPT-medium",
                    name="DialoGPT Medium",
                    provider_type=ProviderType.LOCAL,
                    description="Conversational AI model optimized for dialogue",
                    context_length=1024,
                    cost_per_token=0.0,
                    is_free=True,
                    capabilities=["chat", "dialogue_generation"],
                    therapeutic_safety_score=6.0,
                ),
                ModelInfo(
                    model_id="microsoft/DialoGPT-small",
                    name="DialoGPT Small",
                    provider_type=ProviderType.LOCAL,
                    description="Lightweight conversational AI model",
                    context_length=1024,
                    cost_per_token=0.0,
                    is_free=True,
                    capabilities=["chat", "dialogue_generation"],
                    therapeutic_safety_score=6.0,
                ),
                ModelInfo(
                    model_id="gpt2",
                    name="GPT-2",
                    provider_type=ProviderType.LOCAL,
                    description="Classic text generation model",
                    context_length=1024,
                    cost_per_token=0.0,
                    is_free=True,
                    capabilities=["text_generation"],
                    therapeutic_safety_score=5.0,
                ),
                ModelInfo(
                    model_id="gpt2-medium",
                    name="GPT-2 Medium",
                    provider_type=ProviderType.LOCAL,
                    description="Medium-sized text generation model",
                    context_length=1024,
                    cost_per_token=0.0,
                    is_free=True,
                    capabilities=["text_generation"],
                    therapeutic_safety_score=5.0,
                ),
            ]

            self._available_models = models
            self._last_model_refresh = datetime.now()

            logger.info(f"Refreshed {len(models)} local models")

        except Exception as e:
            logger.error(f"Failed to refresh local models: {e}")
            raise

    async def _load_model_impl(self, model_id: str, config: dict[str, Any]) -> LocalModelInstance:
        """Load a local model instance."""
        try:
            # Check if we can load another model
            if self._loaded_model_count >= self._max_concurrent_models:
                raise RuntimeError(
                    f"Maximum concurrent models ({self._max_concurrent_models}) reached"
                )

            # Determine device
            device = self._get_best_device()

            # Security: Get trust_remote_code and revision from config
            trust_remote_code = config.get("trust_remote_code", False)
            revision = config.get("revision")

            # Security validation: Require revision when trust_remote_code=True
            if trust_remote_code and not revision:
                raise ValueError(
                    f"Security Error: Model '{model_id}' requires trust_remote_code=True "
                    "but no revision is pinned. This allows arbitrary code execution. "
                    "Please specify a trusted revision (commit hash or tag) in the model configuration."
                )

            # Load tokenizer
            logger.info(f"Loading tokenizer for {model_id}...")
            tokenizer_kwargs = {
                "cache_dir": self._models_cache_dir,
                "trust_remote_code": trust_remote_code,
            }
            if revision:
                tokenizer_kwargs["revision"] = revision
                logger.info(f"Using pinned revision: {revision}")

            tokenizer = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: AutoTokenizer.from_pretrained(model_id, **tokenizer_kwargs),  # nosec B615 - revision validated above
            )

            # Set pad token if not present
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Load model
            logger.info(f"Loading model {model_id} on {device}...")

            model_kwargs = {
                "cache_dir": self._models_cache_dir,
                "trust_remote_code": trust_remote_code,
                "torch_dtype": torch.float16 if device != "cpu" else torch.float32,
                "low_cpu_mem_usage": True,
            }

            # Security: Add revision pinning
            if revision:
                model_kwargs["revision"] = revision

            # Add quantization if enabled and supported
            if self._auto_quantization and device != "cpu":
                try:
                    model_kwargs["load_in_8bit"] = True
                except Exception:
                    logger.warning("8-bit quantization not available")

            # Set device map for multi-GPU setups
            if self._device_map and device != "cpu":
                model_kwargs["device_map"] = self._device_map

            loaded_model = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs),  # nosec B615 - revision validated above
            )

            # Move to device if not using device_map
            if not self._device_map and loaded_model:
                model = loaded_model.to(device)  # type: ignore
            else:
                model = loaded_model

            self._loaded_model_count += 1

            logger.info(f"Successfully loaded {model_id} on {device}")
            return LocalModelInstance(model_id, self, model, tokenizer, device)

        except Exception as e:
            logger.error(f"Failed to load local model {model_id}: {e}")
            raise

    async def _unload_model_impl(self, instance: IModelInstance) -> None:
        """Unload a local model instance."""
        try:
            # Cast to concrete type for attribute access
            if not isinstance(instance, LocalModelInstance):
                logger.warning(f"Expected LocalModelInstance, got {type(instance)}")
                return

            # Clear model from memory
            if hasattr(instance, "_model"):
                del instance._model  # type: ignore
            if hasattr(instance, "_tokenizer"):
                del instance._tokenizer  # type: ignore
            if hasattr(instance, "_pipeline"):
                del instance._pipeline  # type: ignore

            # Force garbage collection
            gc.collect()

            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self._loaded_model_count = max(0, self._loaded_model_count - 1)

            logger.info(f"Unloaded local model {instance.model_id}")

        except Exception as e:
            logger.error(f"Failed to unload local model {instance.model_id}: {e}")

    async def _provider_health_check(self) -> bool:
        """Check local model provider health."""
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning("System memory usage is high (>90%)")
                return False

            # Check GPU memory if available
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    memory_allocated = torch.cuda.memory_allocated(i)
                    memory_cached = torch.cuda.memory_reserved(i)
                    total_memory = torch.cuda.get_device_properties(i).total_memory

                    usage_percent = (memory_allocated + memory_cached) / total_memory * 100
                    if usage_percent > 95:
                        logger.warning(f"GPU {i} memory usage is high ({usage_percent:.1f}%)")
                        return False

            return True

        except Exception as e:
            logger.warning(f"Local model health check failed: {e}")
            return False

    def _setup_device_mapping(self):
        """Set up device mapping for multi-GPU systems."""
        if not torch.cuda.is_available():
            return

        gpu_count = torch.cuda.device_count()
        if gpu_count > 1:
            # Simple device mapping for multi-GPU
            self._device_map = "auto"
            logger.info(f"Using automatic device mapping for {gpu_count} GPUs")

    def _get_best_device(self) -> str:
        """Get the best available device for model loading."""
        if not torch.cuda.is_available():
            return "cpu"

        # Find GPU with most free memory
        best_gpu = 0
        max_free_memory = 0

        for i in range(torch.cuda.device_count()):
            free_memory = torch.cuda.get_device_properties(
                i
            ).total_memory - torch.cuda.memory_allocated(i)
            if free_memory > max_free_memory:
                max_free_memory = free_memory
                best_gpu = i

        return f"cuda:{best_gpu}"

    async def get_model_size_estimate(self, model_id: str) -> dict[str, Any]:
        """Estimate the size and requirements of a model."""
        # This would typically query the model's config or use heuristics
        # For now, return basic estimates

        size_estimates = {
            "gpt2": {"parameters": "124M", "disk_gb": 0.5, "ram_gb": 1},
            "gpt2-medium": {"parameters": "355M", "disk_gb": 1.4, "ram_gb": 2},
            "gpt2-large": {"parameters": "774M", "disk_gb": 3.0, "ram_gb": 4},
            "microsoft/DialoGPT-small": {
                "parameters": "117M",
                "disk_gb": 0.5,
                "ram_gb": 1,
            },
            "microsoft/DialoGPT-medium": {
                "parameters": "345M",
                "disk_gb": 1.4,
                "ram_gb": 2,
            },
        }

        return size_estimates.get(model_id, {"parameters": "Unknown", "disk_gb": 2, "ram_gb": 4})
