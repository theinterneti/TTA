"""

# Logseq: [[TTA.dev/Components/Model_management/Services/Fallback_handler]]
Fallback Handler Service

This module provides automatic fallback mechanisms for model failures,
ensuring continuous service availability in the TTA platform.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from ..interfaces import (
    IFallbackHandler,
    IModelProvider,
    ModelInfo,
    ModelRequirements,
)
from ..models import FallbackConfiguration

logger = logging.getLogger(__name__)


class FallbackHandler(IFallbackHandler):
    """Fallback handling service for model failures."""

    def __init__(
        self,
        providers: dict[str, IModelProvider],
        fallback_config: FallbackConfiguration | None = None,
    ):
        self.providers = providers
        self.config = fallback_config or FallbackConfiguration()

        # Track failed models and their failure times
        self._failed_models: dict[str, datetime] = {}
        self._failure_counts: dict[str, int] = defaultdict(int)
        self._provider_health: dict[str, bool] = {}

        # Fallback model rankings
        self._fallback_rankings: dict[str, list[str]] = {}

        # Initialize provider health tracking
        for provider_name in providers:
            self._provider_health[provider_name] = True

    async def get_fallback_model(
        self, failed_model_id: str, requirements: ModelRequirements
    ) -> ModelInfo | None:
        """Get a fallback model when the primary model fails."""
        try:
            logger.info(f"Finding fallback for failed model: {failed_model_id}")

            # Get all available models from healthy providers
            available_models = await self._get_healthy_models()

            if not available_models:
                logger.warning("No healthy models available for fallback")
                return None

            # Filter out the failed model and recently failed models
            candidate_models = self._filter_failed_models(
                available_models, failed_model_id
            )

            if not candidate_models:
                logger.warning(
                    "No candidate models available after filtering failed models"
                )
                return None

            # Filter models based on requirements
            compatible_models = await self._filter_compatible_models(
                candidate_models, requirements
            )

            if not compatible_models:
                logger.warning("No compatible fallback models found")
                return None

            # Select best fallback model based on strategy
            fallback_model = await self._select_fallback_model(
                compatible_models, failed_model_id, requirements
            )

            if fallback_model:
                logger.info(
                    f"Selected fallback model: {fallback_model.model_id} "
                    f"(provider: {fallback_model.provider_type.value})"
                )

            return fallback_model

        except Exception as e:
            logger.error(f"Failed to get fallback model for {failed_model_id}: {e}")
            return None

    async def handle_model_failure(self, model_id: str, error: Exception) -> None:
        """Handle a model failure event."""
        try:
            current_time = datetime.now()

            # Record the failure
            self._failed_models[model_id] = current_time
            self._failure_counts[model_id] += 1

            # Determine failure severity
            failure_count = self._failure_counts[model_id]
            is_critical = failure_count >= self.config.max_retries

            logger.warning(
                f"Model failure recorded: {model_id} "
                f"(count: {failure_count}, critical: {is_critical}, error: {str(error)[:100]})"
            )

            # Update provider health if this indicates a provider issue
            await self._update_provider_health(model_id, error)

            # If critical failure, mark model as temporarily unavailable
            if is_critical:
                logger.error(
                    f"Model {model_id} marked as temporarily unavailable due to repeated failures"
                )

                # Could implement additional actions here:
                # - Send alerts
                # - Update model rankings
                # - Trigger automatic model switching

        except Exception as e:
            logger.error(f"Failed to handle model failure for {model_id}: {e}")

    async def _get_healthy_models(self) -> list[ModelInfo]:
        """Get models from healthy providers."""
        healthy_models = []

        for provider_name, provider in self.providers.items():
            if not self._provider_health.get(provider_name, True):
                continue

            try:
                # Check provider health
                if not await provider.health_check():
                    self._provider_health[provider_name] = False
                    logger.warning(f"Provider {provider_name} marked as unhealthy")
                    continue

                # Get models from healthy provider
                models = await provider.get_available_models()
                healthy_models.extend(models)

            except Exception as e:
                logger.warning(
                    f"Failed to get models from provider {provider_name}: {e}"
                )
                self._provider_health[provider_name] = False

        return healthy_models

    def _filter_failed_models(
        self, models: list[ModelInfo], failed_model_id: str
    ) -> list[ModelInfo]:
        """Filter out failed models and recently failed models."""
        current_time = datetime.now()
        exclusion_period = timedelta(minutes=self.config.exclude_failed_models_minutes)

        filtered_models = []

        for model in models:
            # Skip the originally failed model
            if model.model_id == failed_model_id:
                continue

            # Skip recently failed models
            failure_time = self._failed_models.get(model.model_id)
            if failure_time and (current_time - failure_time) < exclusion_period:
                continue

            # Skip models with too many recent failures
            if self._failure_counts.get(model.model_id, 0) >= self.config.max_retries:
                continue

            filtered_models.append(model)

        return filtered_models

    async def _filter_compatible_models(
        self, models: list[ModelInfo], requirements: ModelRequirements
    ) -> list[ModelInfo]:
        """Filter models based on compatibility with requirements."""
        compatible_models = []

        for model in models:
            # Basic compatibility checks
            if (
                requirements.max_cost_per_token
                and model.cost_per_token
                and model.cost_per_token > requirements.max_cost_per_token
            ):
                continue

            if (
                requirements.context_length_needed
                and model.context_length
                and model.context_length < requirements.context_length_needed
            ):
                continue

            if requirements.required_capabilities and not all(
                cap in model.capabilities for cap in requirements.required_capabilities
            ):
                continue

            if (
                requirements.therapeutic_safety_required
                and model.therapeutic_safety_score
            ) and model.therapeutic_safety_score < 7.0:  # Minimum safety threshold
                continue

            compatible_models.append(model)

        return compatible_models

    async def _select_fallback_model(
        self,
        models: list[ModelInfo],
        _failed_model_id: str,
        requirements: ModelRequirements,
    ) -> ModelInfo | None:
        """Select the best fallback model based on strategy."""
        if not models:
            return None

        strategy = self.config.fallback_strategy

        if strategy == "performance_based":
            return self._select_by_performance(models, requirements)
        if strategy == "cost_based":
            return self._select_by_cost(models, requirements)
        if strategy == "availability_based":
            return self._select_by_availability(models, requirements)
        # Default to performance-based selection
        return self._select_by_performance(models, requirements)

    def _select_by_performance(
        self, models: list[ModelInfo], _requirements: ModelRequirements
    ) -> ModelInfo:
        """Select model based on performance scores."""
        # Sort by performance score (descending)
        sorted_models = sorted(
            models,
            key=lambda m: (
                m.performance_score or 5.0,  # Default score for unknown performance
                -self._failure_counts.get(
                    m.model_id, 0
                ),  # Prefer models with fewer failures
                m.therapeutic_safety_score or 7.0,  # Prefer safer models
            ),
            reverse=True,
        )

        # Apply provider preference if configured
        if self.config.prefer_different_provider:
            # Try to find a model from a different provider than the failed one
            failed_provider = self._get_model_provider(
                models[0].model_id
            )  # Approximate

            for model in sorted_models:
                if model.provider_type.value != failed_provider:
                    return model

        return sorted_models[0]

    def _select_by_cost(
        self, models: list[ModelInfo], _requirements: ModelRequirements
    ) -> ModelInfo:
        """Select model based on cost (prefer lower cost)."""
        # Sort by cost (ascending), then by performance
        sorted_models = sorted(
            models,
            key=lambda m: (
                m.cost_per_token or 0.0,  # Prefer lower cost
                -(m.performance_score or 5.0),  # Then by performance (descending)
                -self._failure_counts.get(
                    m.model_id, 0
                ),  # Prefer models with fewer failures
            ),
        )

        return sorted_models[0]

    def _select_by_availability(
        self, models: list[ModelInfo], _requirements: ModelRequirements
    ) -> ModelInfo:
        """Select model based on availability and reliability."""
        # Sort by failure count (ascending), then by performance
        sorted_models = sorted(
            models,
            key=lambda m: (
                self._failure_counts.get(
                    m.model_id, 0
                ),  # Prefer models with fewer failures
                -(m.performance_score or 5.0),  # Then by performance (descending)
                m.cost_per_token or 0.0,  # Then by cost (ascending)
            ),
        )

        return sorted_models[0]

    async def _update_provider_health(self, model_id: str, error: Exception) -> None:
        """Update provider health based on model failure."""
        try:
            # Determine which provider this model belongs to
            provider_name = None

            for prov_name, provider in self.providers.items():
                try:
                    models = await provider.get_available_models()
                    if any(m.model_id == model_id for m in models):
                        provider_name = prov_name
                        break
                except Exception as e:
                    logger.debug(
                        f"Skipping provider {prov_name} during model lookup: {type(e).__name__}: {e}"
                    )
                    continue

            if not provider_name:
                return

            # Check if this is a provider-level issue
            error_str = str(error).lower()
            provider_issues = [
                "connection",
                "timeout",
                "network",
                "service unavailable",
                "internal server error",
                "bad gateway",
                "service temporarily unavailable",
            ]

            is_provider_issue = any(issue in error_str for issue in provider_issues)

            if is_provider_issue:
                # Perform additional health check
                try:
                    provider = self.providers[provider_name]
                    is_healthy = await provider.health_check()
                    self._provider_health[provider_name] = is_healthy

                    if not is_healthy:
                        logger.warning(
                            f"Provider {provider_name} marked as unhealthy due to model failure"
                        )

                except Exception as e:
                    logger.error(
                        f"Failed to check health of provider {provider_name}: {e}"
                    )
                    self._provider_health[provider_name] = False

        except Exception as e:
            logger.error(f"Failed to update provider health: {e}")

    def _get_model_provider(self, model_id: str) -> str | None:
        """Get the provider name for a model (best effort)."""
        # This is a simplified implementation
        # In practice, you'd maintain a mapping of models to providers

        if "gpt" in model_id.lower() or "openai" in model_id.lower():
            return "openai"
        if "claude" in model_id.lower():
            return "anthropic"
        if "llama" in model_id.lower() or "qwen" in model_id.lower():
            return "local"
        return "unknown"

    def get_failure_statistics(self) -> dict[str, Any]:
        """Get failure statistics for monitoring."""
        current_time = datetime.now()
        recent_failures = {}

        # Count recent failures (last hour)
        one_hour_ago = current_time - timedelta(hours=1)

        for model_id, failure_time in self._failed_models.items():
            if failure_time > one_hour_ago:
                recent_failures[model_id] = {
                    "last_failure": failure_time.isoformat(),
                    "total_failures": self._failure_counts[model_id],
                    "minutes_since_failure": (
                        current_time - failure_time
                    ).total_seconds()
                    / 60,
                }

        return {
            "total_failed_models": len(self._failed_models),
            "recent_failures_1h": len(recent_failures),
            "recent_failure_details": recent_failures,
            "provider_health": self._provider_health.copy(),
            "config": {
                "max_retries": self.config.max_retries,
                "exclude_failed_models_minutes": self.config.exclude_failed_models_minutes,
                "fallback_strategy": self.config.fallback_strategy,
            },
        }

    def reset_model_failures(self, model_id: str) -> bool:
        """Reset failure count for a model (for manual recovery)."""
        try:
            if model_id in self._failed_models:
                del self._failed_models[model_id]

            if model_id in self._failure_counts:
                del self._failure_counts[model_id]

            logger.info(f"Reset failure count for model: {model_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reset failures for model {model_id}: {e}")
            return False

    def reset_provider_health(self, provider_name: str) -> bool:
        """Reset health status for a provider (for manual recovery)."""
        try:
            if provider_name in self._provider_health:
                self._provider_health[provider_name] = True
                logger.info(f"Reset health status for provider: {provider_name}")
                return True
            logger.warning(f"Provider {provider_name} not found")
            return False

        except Exception as e:
            logger.error(f"Failed to reset health for provider {provider_name}: {e}")
            return False

    async def cleanup_old_failures(self, hours: int = 24) -> int:
        """Clean up old failure records."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Remove old failure records
            old_failures = [
                model_id
                for model_id, failure_time in self._failed_models.items()
                if failure_time < cutoff_time
            ]

            for model_id in old_failures:
                del self._failed_models[model_id]
                # Reset failure count for old failures
                self._failure_counts[model_id] = 0

            logger.info(f"Cleaned up {len(old_failures)} old failure records")
            return len(old_failures)

        except Exception as e:
            logger.error(f"Failed to cleanup old failures: {e}")
            return 0
