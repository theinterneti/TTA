"""
Hardware Detection Service.

This module provides comprehensive hardware detection capabilities to
recommend appropriate AI models based on available system resources.
"""

import logging
import platform
import sys
from typing import Any

import psutil

from ..interfaces import IHardwareDetector, TaskType
from ..models import SystemResources

logger = logging.getLogger(__name__)


class HardwareDetector(IHardwareDetector):
    """Hardware detection and model recommendation service."""

    def __init__(self):
        self._cached_resources: SystemResources | None = None
        self._gpu_available = None
        self._gpu_info = []

    async def detect_system_resources(self) -> dict[str, Any]:
        """Detect available system resources."""
        try:
            # CPU information
            cpu_count = psutil.cpu_count(logical=True) or 1  # Default to 1 if None
            cpu_info = self._get_cpu_info()

            # Memory information
            memory = psutil.virtual_memory()
            total_ram_gb = memory.total / (1024**3)
            available_ram_gb = memory.available / (1024**3)

            # Disk space
            disk_usage = psutil.disk_usage("/")
            disk_space_gb = disk_usage.free / (1024**3)

            # GPU information
            gpu_info = await self._detect_gpu_info()

            # Create SystemResources object
            resources = SystemResources(
                total_ram_gb=total_ram_gb,
                available_ram_gb=available_ram_gb,
                cpu_cores=cpu_count,
                cpu_model=cpu_info,
                gpu_count=len(gpu_info),
                gpu_models=[gpu["name"] for gpu in gpu_info],
                gpu_memory_gb=[gpu["memory_gb"] for gpu in gpu_info],
                disk_space_gb=disk_space_gb,
                platform=platform.system(),
                python_version=sys.version,
            )

            self._cached_resources = resources

            return {
                "total_ram_gb": total_ram_gb,
                "available_ram_gb": available_ram_gb,
                "cpu_cores": cpu_count,
                "cpu_model": cpu_info,
                "gpu_count": len(gpu_info),
                "gpu_info": gpu_info,
                "disk_space_gb": disk_space_gb,
                "platform": platform.system(),
                "python_version": sys.version,
                "has_gpu": len(gpu_info) > 0,
                "total_gpu_memory_gb": sum(gpu["memory_gb"] for gpu in gpu_info),
            }

        except Exception as e:
            logger.error(f"Failed to detect system resources: {e}")
            raise

    async def recommend_models(self, task_type: TaskType) -> list[str]:
        """Recommend models based on available hardware and task type."""
        if not self._cached_resources:
            await self.detect_system_resources()

        resources = self._cached_resources
        if not resources:
            return []  # No resources detected

        recommendations = []

        # Base recommendations based on available RAM
        if resources.available_ram_gb >= 32:
            # High-end system - can run large models
            recommendations.extend(
                [
                    "meta-llama/llama-3.1-70b-instruct",  # If GPU available
                    "meta-llama/llama-3.1-8b-instruct",
                    "mistralai/mixtral-8x7b-instruct",
                    "qwen/qwen2.5-14b-instruct",
                ]
            )
        elif resources.available_ram_gb >= 16:
            # Mid-range system - medium models
            recommendations.extend(
                [
                    "meta-llama/llama-3.1-8b-instruct",
                    "qwen/qwen2.5-7b-instruct",
                    "microsoft/phi-3-medium-4k-instruct",
                    "mistralai/mistral-7b-instruct",
                ]
            )
        elif resources.available_ram_gb >= 8:
            # Lower-end system - small models
            recommendations.extend(
                [
                    "qwen/qwen2.5-3b-instruct",
                    "microsoft/phi-3-mini-4k-instruct",
                    "google/gemma-2b-it",
                ]
            )
        else:
            # Very limited system - cloud models only
            recommendations.extend(
                [
                    "openrouter/free-models",  # Placeholder for free cloud models
                    "meta-llama/llama-3.1-8b-instruct:free",
                ]
            )

        # GPU-specific recommendations
        if resources.has_gpu and resources.total_gpu_memory_gb >= 24:
            # High VRAM - can run large models efficiently
            recommendations.insert(0, "meta-llama/llama-3.1-70b-instruct")
        elif resources.has_gpu and resources.total_gpu_memory_gb >= 12:
            # Medium VRAM - good for 7B-13B models
            recommendations.insert(0, "meta-llama/llama-3.1-8b-instruct")
            recommendations.insert(1, "qwen/qwen2.5-14b-instruct")
        elif resources.has_gpu and resources.total_gpu_memory_gb >= 6:
            # Lower VRAM - small to medium models
            recommendations.insert(0, "qwen/qwen2.5-7b-instruct")

        # Task-specific adjustments
        if task_type == TaskType.NARRATIVE_GENERATION:
            # Prioritize models good at creative writing
            creative_models = [
                "anthropic/claude-3-haiku",
                "meta-llama/llama-3.1-8b-instruct",
                "qwen/qwen2.5-7b-instruct",
            ]
            recommendations = creative_models + [
                m for m in recommendations if m not in creative_models
            ]

        elif task_type == TaskType.THERAPEUTIC_RESPONSE:
            # Prioritize models with better safety and empathy
            therapeutic_models = [
                "anthropic/claude-3-haiku",
                "openai/gpt-4o-mini",
                "meta-llama/llama-3.1-8b-instruct",
            ]
            recommendations = therapeutic_models + [
                m for m in recommendations if m not in therapeutic_models
            ]

        elif task_type == TaskType.DIALOGUE_GENERATION:
            # Prioritize models good at conversation
            dialogue_models = [
                "meta-llama/llama-3.1-8b-instruct",
                "anthropic/claude-3-haiku",
                "qwen/qwen2.5-7b-instruct",
            ]
            recommendations = dialogue_models + [
                m for m in recommendations if m not in dialogue_models
            ]

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for model in recommendations:
            if model not in seen:
                seen.add(model)
                unique_recommendations.append(model)

        return unique_recommendations[:10]  # Return top 10 recommendations

    async def estimate_model_requirements(self, model_id: str) -> dict[str, Any]:
        """Estimate resource requirements for a specific model."""
        # Model size estimates (approximate)
        model_sizes = {
            # Llama models
            "meta-llama/llama-3.1-70b-instruct": {
                "ram_gb": 140,
                "vram_gb": 40,
                "disk_gb": 140,
            },
            "meta-llama/llama-3.1-8b-instruct": {
                "ram_gb": 16,
                "vram_gb": 8,
                "disk_gb": 16,
            },
            # Qwen models
            "qwen/qwen2.5-14b-instruct": {"ram_gb": 28, "vram_gb": 14, "disk_gb": 28},
            "qwen/qwen2.5-7b-instruct": {"ram_gb": 14, "vram_gb": 7, "disk_gb": 14},
            "qwen/qwen2.5-3b-instruct": {"ram_gb": 6, "vram_gb": 3, "disk_gb": 6},
            # Mistral models
            "mistralai/mixtral-8x7b-instruct": {
                "ram_gb": 90,
                "vram_gb": 24,
                "disk_gb": 90,
            },
            "mistralai/mistral-7b-instruct": {
                "ram_gb": 14,
                "vram_gb": 7,
                "disk_gb": 14,
            },
            # Phi models
            "microsoft/phi-3-medium-4k-instruct": {
                "ram_gb": 8,
                "vram_gb": 4,
                "disk_gb": 8,
            },
            "microsoft/phi-3-mini-4k-instruct": {
                "ram_gb": 4,
                "vram_gb": 2,
                "disk_gb": 4,
            },
            # Gemma models
            "google/gemma-2b-it": {"ram_gb": 4, "vram_gb": 2, "disk_gb": 4},
        }

        # Default estimates for unknown models
        default_requirements = {"ram_gb": 8, "vram_gb": 4, "disk_gb": 8}

        requirements: dict[str, Any] = model_sizes.get(model_id, default_requirements).copy()

        # Add additional requirements
        requirements.update(
            {
                "cpu_cores_recommended": 4,
                "python_version_min": "3.8",
                "supports_quantization": True,
                "quantization_options": ["4bit", "8bit", "16bit"],
                "estimated_load_time_seconds": (30 if requirements["ram_gb"] <= 16 else 120),
            }
        )

        return requirements

    def _get_cpu_info(self) -> str:
        """Get CPU model information."""
        try:
            import cpuinfo

            info = cpuinfo.get_cpu_info()
            return info.get("brand_raw", "Unknown CPU")
        except ImportError:
            # Fallback if py-cpuinfo not available
            return f"{platform.processor()} ({psutil.cpu_count()} cores)"

    async def _detect_gpu_info(self) -> list[dict[str, Any]]:
        """Detect GPU information."""
        gpu_info = []

        try:
            # Try NVIDIA GPUs first
            import pynvml

            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name_raw = pynvml.nvmlDeviceGetName(handle)
                name = name_raw.decode("utf-8") if isinstance(name_raw, bytes) else name_raw
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_gb = float(memory_info.total) / (1024**3)

                gpu_info.append(
                    {
                        "index": i,
                        "name": name,
                        "memory_gb": memory_gb,
                        "type": "NVIDIA",
                        "available": True,
                    }
                )

        except ImportError:
            logger.info("pynvml not available, skipping NVIDIA GPU detection")
        except Exception as e:
            logger.warning(f"Failed to detect NVIDIA GPUs: {e}")

        # Try to detect other GPUs (AMD, Intel, etc.)
        try:
            # This is a simplified detection - in practice, you might want
            # more sophisticated GPU detection for non-NVIDIA cards
            pass
        except Exception as e:
            logger.warning(f"Failed to detect other GPUs: {e}")

        return gpu_info

    def get_cached_resources(self) -> SystemResources | None:
        """Get cached system resources."""
        return self._cached_resources

    async def check_model_compatibility(self, model_id: str) -> dict[str, Any]:
        """Check if a model is compatible with current system."""
        if not self._cached_resources:
            await self.detect_system_resources()

        requirements = await self.estimate_model_requirements(model_id)
        resources = self._cached_resources

        if not resources:
            return {
                "compatible": False,
                "warnings": ["System resources not detected"],
                "requirements": requirements,
                "available_resources": {},
            }

        compatibility = {
            "compatible": True,
            "warnings": [],
            "requirements": requirements,
            "available_resources": {
                "ram_gb": resources.available_ram_gb,
                "gpu_memory_gb": resources.total_gpu_memory_gb,
                "disk_space_gb": resources.disk_space_gb,
            },
        }

        # Check RAM
        if requirements["ram_gb"] > resources.available_ram_gb:
            compatibility["compatible"] = False
            compatibility["warnings"].append(
                f"Insufficient RAM: need {requirements['ram_gb']}GB, have {resources.available_ram_gb:.1f}GB"
            )

        # Check GPU memory (if GPU required)
        if requirements["vram_gb"] > resources.total_gpu_memory_gb:
            if resources.has_gpu:
                compatibility["warnings"].append(
                    f"Insufficient VRAM: need {requirements['vram_gb']}GB, have {resources.total_gpu_memory_gb:.1f}GB. Consider CPU inference or quantization."
                )
            else:
                compatibility["warnings"].append(
                    "No GPU detected. Model will run on CPU, which may be slow."
                )

        # Check disk space
        if requirements["disk_gb"] > resources.disk_space_gb:
            compatibility["compatible"] = False
            compatibility["warnings"].append(
                f"Insufficient disk space: need {requirements['disk_gb']}GB, have {resources.disk_space_gb:.1f}GB"
            )

        return compatibility
