"""
Concrete Value Tests for FallbackHandler Service.

This module contains concrete value tests that validate business logic correctness
with specific inputs and expected outputs. These tests complement property-based
tests to achieve high mutation testing scores.
"""

from unittest.mock import AsyncMock

import pytest
from tta_ai.models import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import FallbackConfiguration
from tta_ai.models.services import FallbackHandler

# ============================================================================
# Concrete Value Tests - Selection Strategies
# ============================================================================


@pytest.mark.concrete
class TestFallbackHandlerConcreteSelectionStrategies:
    """Concrete tests for fallback selection strategies."""

    @pytest.fixture
    def requirements(self):
        """Standard requirements for testing."""
        return ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            therapeutic_safety_required=False,
        )

    @pytest.mark.asyncio
    async def test_performance_based_selection_with_known_ranking(self, requirements):
        """Concrete: Performance-based selection ranks by performance score."""
        # Arrange - Create models with specific performance scores
        model_high_perf = ModelInfo(
            model_id="high-perf-model",
            name="High Performance Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=9.0,  # Highest
            therapeutic_safety_score=7.0,
            context_length=8000,
        )
        model_mid_perf = ModelInfo(
            model_id="mid-perf-model",
            name="Mid Performance Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=6.0,  # Middle
            therapeutic_safety_score=7.0,
            context_length=8000,
        )
        model_low_perf = ModelInfo(
            model_id="low-perf-model",
            name="Low Performance Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=3.0,  # Lowest
            therapeutic_safety_score=7.0,
            context_length=8000,
        )

        # Create handler with performance-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_low_perf, model_mid_perf, model_high_perf]
        )

        config = FallbackConfiguration(fallback_strategy="performance_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Act - Get fallback (exclude low-perf model)
        fallback = await handler.get_fallback_model("low-perf-model", requirements)

        # Assert - Should select high-perf model (highest performance)
        assert fallback is not None
        assert fallback.model_id == "high-perf-model"

    @pytest.mark.asyncio
    async def test_cost_based_selection_with_known_costs(self, requirements):
        """Concrete: Cost-based selection ranks by cost (lower is better)."""
        # Arrange - Create models with specific costs
        model_expensive = ModelInfo(
            model_id="expensive-model",
            name="Expensive Model",
            provider_type=ProviderType.OPENROUTER,
            cost_per_token=0.005,  # Highest cost
            performance_score=8.0,
            context_length=8000,
        )
        model_moderate = ModelInfo(
            model_id="moderate-model",
            name="Moderate Model",
            provider_type=ProviderType.OPENROUTER,
            cost_per_token=0.002,  # Middle cost
            performance_score=7.0,
            context_length=8000,
        )
        model_cheap = ModelInfo(
            model_id="cheap-model",
            name="Cheap Model",
            provider_type=ProviderType.OPENROUTER,
            cost_per_token=0.0001,  # Lowest cost
            performance_score=6.0,
            context_length=8000,
        )

        # Create handler with cost-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_expensive, model_moderate, model_cheap]
        )

        config = FallbackConfiguration(fallback_strategy="cost_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Act - Get fallback (exclude expensive model)
        fallback = await handler.get_fallback_model("expensive-model", requirements)

        # Assert - Should select cheap model (lowest cost)
        assert fallback is not None
        assert fallback.model_id == "cheap-model"

    @pytest.mark.asyncio
    async def test_availability_based_selection_with_failure_counts(self, requirements):
        """Concrete: Availability-based selection ranks by failure count."""
        # Arrange - Create models
        model_unreliable = ModelInfo(
            model_id="unreliable-model",
            name="Unreliable Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=9.0,
            context_length=8000,
        )
        model_moderate = ModelInfo(
            model_id="moderate-model",
            name="Moderate Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=7.0,
            context_length=8000,
        )
        model_reliable = ModelInfo(
            model_id="reliable-model",
            name="Reliable Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=8.0,
            context_length=8000,
        )

        # Create handler with availability-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_unreliable, model_moderate, model_reliable]
        )

        config = FallbackConfiguration(fallback_strategy="availability_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Set specific failure counts
        handler._failure_counts["unreliable-model"] = 10  # Most failures
        handler._failure_counts["moderate-model"] = 3  # Some failures
        handler._failure_counts["reliable-model"] = 0  # No failures

        # Act - Get fallback (exclude unreliable model)
        fallback = await handler.get_fallback_model("unreliable-model", requirements)

        # Assert - Should select reliable model (fewest failures)
        assert fallback is not None
        assert fallback.model_id == "reliable-model"


# ============================================================================
# Concrete Value Tests - Filtering Logic
# ============================================================================


@pytest.mark.concrete
class TestFallbackHandlerConcreteFiltering:
    """Concrete tests for filtering logic."""

    @pytest.mark.asyncio
    async def test_therapeutic_safety_threshold_enforced(self):
        """Concrete: Models with safety score < 7.0 are excluded when safety required."""
        # Arrange - Create models with specific safety scores
        model_safe = ModelInfo(
            model_id="safe-model",
            name="Safe Model",
            provider_type=ProviderType.OPENROUTER,
            therapeutic_safety_score=8.5,  # Above threshold
            performance_score=7.0,
            context_length=8000,
        )
        model_unsafe = ModelInfo(
            model_id="unsafe-model",
            name="Unsafe Model",
            provider_type=ProviderType.OPENROUTER,
            therapeutic_safety_score=5.0,  # Below 7.0 threshold
            performance_score=9.0,  # Higher performance but unsafe
            context_length=8000,
        )

        # Requirements with safety required
        requirements = ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            therapeutic_safety_required=True,  # Safety is required
        )

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_unsafe, model_safe]
        )

        handler = FallbackHandler(providers={"test": mock_provider})

        # Act - Get fallback
        fallback = await handler.get_fallback_model("failed-model", requirements)

        # Assert - Should select safe model (unsafe excluded due to safety < 7.0)
        assert fallback is not None
        assert fallback.model_id == "safe-model"

    @pytest.mark.asyncio
    async def test_context_length_filtering_works(self):
        """Concrete: Models with insufficient context length are excluded."""
        # Arrange - Create models with specific context lengths
        model_large_context = ModelInfo(
            model_id="large-context-model",
            name="Large Context Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=32000,  # Sufficient
            performance_score=7.0,
        )
        model_small_context = ModelInfo(
            model_id="small-context-model",
            name="Small Context Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=4000,  # Insufficient
            performance_score=9.0,  # Higher performance but insufficient context
        )

        # Requirements with specific context length needed
        requirements = ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            context_length_needed=16000,  # Requires 16k context
        )

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_small_context, model_large_context]
        )

        handler = FallbackHandler(providers={"test": mock_provider})

        # Act - Get fallback
        fallback = await handler.get_fallback_model("failed-model", requirements)

        # Assert - Should select large-context model (small excluded)
        assert fallback is not None
        assert fallback.model_id == "large-context-model"


# ============================================================================
# Concrete Value Tests - Default Values
# ============================================================================


@pytest.mark.concrete
class TestFallbackHandlerConcreteDefaults:
    """Concrete tests for default value handling."""

    @pytest.fixture
    def requirements(self):
        """Standard requirements for testing."""
        return ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            therapeutic_safety_required=False,
        )

    @pytest.mark.asyncio
    async def test_default_performance_score_applied(self, requirements):
        """Concrete: Default performance score of 5.0 is used when not specified."""
        # Arrange - Create models, one without performance score
        model_with_score = ModelInfo(
            model_id="scored-model",
            name="Scored Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=4.0,  # Explicitly lower than default 5.0
            context_length=8000,
        )
        model_without_score = ModelInfo(
            model_id="unscored-model",
            name="Unscored Model",
            provider_type=ProviderType.OPENROUTER,
            performance_score=None,  # Will use default 5.0
            context_length=8000,
        )

        # Create handler with performance-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_with_score, model_without_score]
        )

        config = FallbackConfiguration(fallback_strategy="performance_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Act - Get fallback (exclude scored model)
        fallback = await handler.get_fallback_model("scored-model", requirements)

        # Assert - Should select unscored model (default 5.0 > explicit 4.0)
        assert fallback is not None
        assert fallback.model_id == "unscored-model"

    @pytest.mark.asyncio
    async def test_default_cost_zero_applied(self, requirements):
        """Concrete: Default cost of 0.0 is used when not specified."""
        # Arrange - Create models, one without cost
        model_with_cost = ModelInfo(
            model_id="paid-model",
            name="Paid Model",
            provider_type=ProviderType.OPENROUTER,
            cost_per_token=0.001,  # Has cost
            performance_score=8.0,
            context_length=8000,
        )
        model_without_cost = ModelInfo(
            model_id="free-model",
            name="Free Model",
            provider_type=ProviderType.OPENROUTER,
            cost_per_token=None,  # Will use default 0.0
            performance_score=7.0,
            context_length=8000,
        )

        # Create handler with cost-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_with_cost, model_without_cost]
        )

        config = FallbackConfiguration(fallback_strategy="cost_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Act - Get fallback (exclude paid model)
        fallback = await handler.get_fallback_model("paid-model", requirements)

        # Assert - Should select free model (default 0.0 < 0.001)
        assert fallback is not None
        assert fallback.model_id == "free-model"
