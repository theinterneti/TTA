"""
Model Selection Service

This module provides intelligent model selection based on task requirements,
system capabilities, and performance metrics.
"""

import logging
from datetime import datetime, timedelta

from ..interfaces import (
    IHardwareDetector,
    IModelProvider,
    IModelSelector,
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from ..models import ModelSelectionCriteria, PerformanceMetrics

logger = logging.getLogger(__name__)


class ModelSelector(IModelSelector):
    """Intelligent model selection service."""

    def __init__(
        self,
        providers: dict[str, IModelProvider],
        hardware_detector: IHardwareDetector,
        selection_criteria: ModelSelectionCriteria | None = None,
    ):
        self.providers = providers
        self.hardware_detector = hardware_detector
        self.selection_criteria = selection_criteria or ModelSelectionCriteria()
        self._performance_cache: dict[str, list[PerformanceMetrics]] = {}
        self._model_cache: dict[str, list[ModelInfo]] = {}
        self._cache_ttl = timedelta(hours=1)
        self._last_cache_update = {}

    async def select_model(self, requirements: ModelRequirements) -> ModelInfo | None:
        """Select the best model based on requirements."""
        try:
            # Get all available models
            available_models = await self._get_all_available_models()

            if not available_models:
                logger.warning("No models available for selection")
                return None

            # Filter models based on requirements
            compatible_models = await self._filter_compatible_models(
                available_models, requirements
            )

            if not compatible_models:
                logger.warning(
                    f"No compatible models found for requirements: {requirements}"
                )
                return None

            # Rank models by suitability
            ranked_models = await self.rank_models(compatible_models, requirements)

            if not ranked_models:
                logger.warning("No models passed ranking criteria")
                return None

            selected_model = ranked_models[0]
            logger.info(
                f"Selected model: {selected_model.model_id} (provider: {selected_model.provider_type.value})"
            )

            return selected_model

        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return None

    async def rank_models(
        self, models: list[ModelInfo], requirements: ModelRequirements
    ) -> list[ModelInfo]:
        """Rank models by suitability for the requirements."""
        try:
            scored_models = []

            for model in models:
                score = await self._calculate_model_score(model, requirements)
                if score > 0:  # Only include models with positive scores
                    scored_models.append((model, score))

            # Sort by score (descending)
            scored_models.sort(key=lambda x: x[1], reverse=True)

            # Return ranked models
            ranked_models = [model for model, score in scored_models]

            logger.info(
                f"Ranked {len(ranked_models)} models for task {requirements.task_type.value}"
            )

            return ranked_models

        except Exception as e:
            logger.error(f"Model ranking failed: {e}")
            return models  # Return unranked models as fallback

    async def validate_model_compatibility(
        self, model_info: ModelInfo, requirements: ModelRequirements
    ) -> bool:
        """Check if a model is compatible with the requirements."""
        try:
            # Check basic requirements
            if requirements.max_latency_ms and model_info.performance_score:
                # Estimate latency based on performance score (simplified)
                estimated_latency = 5000 / max(model_info.performance_score, 1.0)
                if estimated_latency > requirements.max_latency_ms:
                    return False

            # Check cost requirements
            if requirements.max_cost_per_token and model_info.cost_per_token:
                if model_info.cost_per_token > requirements.max_cost_per_token:
                    return False

            # Check quality requirements
            if requirements.min_quality_score and model_info.performance_score:
                if model_info.performance_score < requirements.min_quality_score:
                    return False

            # Check therapeutic safety
            if requirements.therapeutic_safety_required:
                if model_info.therapeutic_safety_score is None:
                    # Unknown safety score - be conservative
                    return model_info.provider_type in [
                        ProviderType.OPENROUTER,
                        ProviderType.CUSTOM_API,
                    ]
                if (
                    model_info.therapeutic_safety_score
                    < self.selection_criteria.min_therapeutic_safety_score
                ):
                    return False

            # Check context length
            if requirements.context_length_needed and model_info.context_length:
                if model_info.context_length < requirements.context_length_needed:
                    return False

            # Check required capabilities
            if requirements.required_capabilities:
                for capability in requirements.required_capabilities:
                    if capability not in model_info.capabilities:
                        return False

            return True

        except Exception as e:
            logger.error(f"Compatibility check failed for {model_info.model_id}: {e}")
            return False

    async def _get_all_available_models(self) -> list[ModelInfo]:
        """Get all available models from all providers."""
        all_models = []

        for provider_name, provider in self.providers.items():
            try:
                # Check cache first
                if self._is_cache_valid(provider_name):
                    models = self._model_cache.get(provider_name, [])
                else:
                    # Refresh cache
                    models = await provider.get_available_models()
                    self._model_cache[provider_name] = models
                    self._last_cache_update[provider_name] = datetime.now()

                all_models.extend(models)

            except Exception as e:
                logger.warning(
                    f"Failed to get models from provider {provider_name}: {e}"
                )
                continue

        return all_models

    async def _filter_compatible_models(
        self, models: list[ModelInfo], requirements: ModelRequirements
    ) -> list[ModelInfo]:
        """Filter models based on compatibility with requirements."""
        compatible_models = []

        for model in models:
            if await self.validate_model_compatibility(model, requirements):
                compatible_models.append(model)

        return compatible_models

    async def _calculate_model_score(
        self, model: ModelInfo, requirements: ModelRequirements
    ) -> float:
        """Calculate a suitability score for a model."""
        try:
            score = 0.0

            # Base score from model performance
            if model.performance_score:
                score += (
                    model.performance_score * self.selection_criteria.performance_weight
                )
            else:
                # Default score for unknown performance
                score += 5.0 * self.selection_criteria.performance_weight

            # Therapeutic safety score
            if model.therapeutic_safety_score:
                score += (
                    model.therapeutic_safety_score
                    * self.selection_criteria.therapeutic_safety_weight
                )
            # Conservative default for unknown safety
            elif model.provider_type in [
                ProviderType.OPENROUTER,
                ProviderType.CUSTOM_API,
            ]:
                score += 7.0 * self.selection_criteria.therapeutic_safety_weight
            else:
                score += 5.0 * self.selection_criteria.therapeutic_safety_weight

            # Cost score (lower cost = higher score)
            cost_score = 10.0  # Max score for free models
            if model.cost_per_token and model.cost_per_token > 0:
                # Normalize cost (assuming max acceptable cost of $0.01 per token)
                max_cost = 0.01
                cost_score = max(
                    0, 10.0 * (1 - min(model.cost_per_token / max_cost, 1.0))
                )

            score += cost_score * self.selection_criteria.cost_weight

            # Bonus for task-specific capabilities
            task_bonus = await self._calculate_task_bonus(model, requirements.task_type)
            score += task_bonus

            # Bonus for preferred characteristics
            if self.selection_criteria.prefer_free_models and model.is_free:
                score += 1.0

            if (
                self.selection_criteria.prefer_local_models
                and model.provider_type == ProviderType.LOCAL
            ):
                score += 1.0

            # Hardware compatibility bonus
            hardware_bonus = await self._calculate_hardware_compatibility_bonus(model)
            score += hardware_bonus

            # Performance history bonus
            performance_bonus = await self._calculate_performance_history_bonus(
                model.model_id
            )
            score += performance_bonus

            return max(0.0, score)  # Ensure non-negative score

        except Exception as e:
            logger.error(f"Score calculation failed for {model.model_id}: {e}")
            return 0.0

    async def _calculate_task_bonus(
        self, model: ModelInfo, task_type: TaskType
    ) -> float:
        """Calculate bonus score based on task-specific model suitability."""
        bonus = 0.0

        # Task-specific capability bonuses
        task_capabilities = {
            TaskType.NARRATIVE_GENERATION: [
                "creative_writing",
                "storytelling",
                "long_form",
            ],
            TaskType.DIALOGUE_GENERATION: ["conversation", "chat", "dialogue"],
            TaskType.THERAPEUTIC_RESPONSE: ["empathy", "safety", "therapeutic"],
            TaskType.CHARACTER_DEVELOPMENT: ["character", "personality", "psychology"],
            TaskType.WORLD_BUILDING: [
                "creative_writing",
                "world_building",
                "description",
            ],
            TaskType.CHOICE_GENERATION: ["decision_making", "options", "branching"],
            TaskType.CONSEQUENCE_ANALYSIS: ["analysis", "reasoning", "logic"],
            TaskType.GENERAL_CHAT: ["chat", "conversation", "general"],
        }

        relevant_capabilities = task_capabilities.get(task_type, [])

        for capability in relevant_capabilities:
            if capability in model.capabilities:
                bonus += 0.5

        # Model-specific bonuses based on known strengths
        model_task_bonuses = {
            TaskType.NARRATIVE_GENERATION: {
                "anthropic/claude": 2.0,
                "meta-llama/llama-3.1": 1.5,
                "qwen/qwen2.5": 1.0,
            },
            TaskType.THERAPEUTIC_RESPONSE: {
                "anthropic/claude": 2.5,
                "openai/gpt-4": 2.0,
                "meta-llama/llama-3.1": 1.0,
            },
            TaskType.DIALOGUE_GENERATION: {
                "meta-llama/llama-3.1": 2.0,
                "anthropic/claude": 1.5,
                "qwen/qwen2.5": 1.0,
            },
        }

        task_bonuses = model_task_bonuses.get(task_type, {})
        for model_pattern, bonus_value in task_bonuses.items():
            if model_pattern.lower() in model.model_id.lower():
                bonus += bonus_value
                break

        return bonus

    async def _calculate_hardware_compatibility_bonus(self, model: ModelInfo) -> float:
        """Calculate bonus based on hardware compatibility."""
        try:
            # Get hardware requirements for the model
            requirements = await self.hardware_detector.estimate_model_requirements(
                model.model_id
            )

            # Get system resources
            system_resources = await self.hardware_detector.detect_system_resources()

            bonus = 0.0

            # RAM compatibility bonus
            required_ram = requirements.get("ram_gb", 8)
            available_ram = system_resources.get("available_ram_gb", 0)

            if available_ram >= required_ram * 1.5:  # Plenty of RAM
                bonus += 1.0
            elif available_ram >= required_ram:  # Sufficient RAM
                bonus += 0.5
            elif available_ram >= required_ram * 0.8:  # Tight but possible
                bonus += 0.1
            # No bonus if insufficient RAM

            # GPU compatibility bonus
            if system_resources.get("has_gpu", False):
                required_vram = requirements.get("vram_gb", 0)
                available_vram = system_resources.get("total_gpu_memory_gb", 0)

                if available_vram >= required_vram:
                    bonus += 0.5

            return bonus

        except Exception as e:
            logger.warning(f"Hardware compatibility calculation failed: {e}")
            return 0.0

    async def _calculate_performance_history_bonus(self, model_id: str) -> float:
        """Calculate bonus based on historical performance."""
        try:
            # Get recent performance metrics
            recent_metrics = self._performance_cache.get(model_id, [])

            if not recent_metrics:
                return 0.0  # No history available

            # Calculate average performance over recent history
            total_score = 0.0
            count = 0

            for metric in recent_metrics:
                if metric.quality_score:
                    total_score += metric.quality_score
                    count += 1

            if count == 0:
                return 0.0

            average_quality = total_score / count

            # Bonus based on quality (0-2 points)
            quality_bonus = max(0, (average_quality - 5.0) / 5.0 + 2.0)

            # Reliability bonus based on success rate
            success_rates = [
                m.success_rate for m in recent_metrics if m.success_rate is not None
            ]
            if success_rates:
                avg_success_rate = sum(success_rates) / len(success_rates)
                reliability_bonus = max(
                    0, (avg_success_rate - 0.9) * 10
                )  # Bonus for >90% success rate
            else:
                reliability_bonus = 0.0

            return quality_bonus + reliability_bonus

        except Exception as e:
            logger.warning(f"Performance history calculation failed: {e}")
            return 0.0

    def _is_cache_valid(self, provider_name: str) -> bool:
        """Check if the model cache is still valid."""
        last_update = self._last_cache_update.get(provider_name)
        if not last_update:
            return False

        return datetime.now() - last_update < self._cache_ttl

    def update_performance_metrics(self, model_id: str, metrics: PerformanceMetrics):
        """Update performance metrics for a model."""
        if model_id not in self._performance_cache:
            self._performance_cache[model_id] = []

        self._performance_cache[model_id].append(metrics)

        # Keep only recent metrics (last 100 entries or 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self._performance_cache[model_id] = [
            m
            for m in self._performance_cache[model_id][-100:]
            if m.timestamp > cutoff_time
        ]

    def clear_cache(self):
        """Clear all caches."""
        self._model_cache.clear()
        self._last_cache_update.clear()
        self._performance_cache.clear()
