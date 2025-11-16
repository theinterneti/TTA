"""
Performance Benchmarks for Model Selection.

This module contains performance benchmarks for the Model Management component,
focusing on model selection latency and fallback activation performance.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from tta_ai.models import (
    ModelInfo,
    ModelManagementComponent,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import (
    FallbackConfiguration,
    ModelSelectionCriteria,
)
from tta_ai.models.services import FallbackHandler, ModelSelector

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_config():
    """Create a mock configuration for benchmarking."""
    return {
        "model_management": {
            "enabled": True,
            "default_provider": "openrouter",
            "providers": {
                "openrouter": {
                    "enabled": True,
                    "api_key": "test-key-for-benchmarking",
                    "free_models_only": True,
                }
            },
        }
    }


@pytest.fixture
def mock_models():
    """Create a list of mock models for benchmarking."""
    return [
        ModelInfo(
            model_id=f"test-model-{i}",
            name=f"Test Model {i}",
            provider_type=ProviderType.OPENROUTER,
            description=f"Test model {i} for benchmarking",
            context_length=8192,
            cost_per_token=0.0 if i % 2 == 0 else 0.001,
            is_free=i % 2 == 0,
            capabilities=["chat", "completion"],
            therapeutic_safety_score=7.0 + (i % 3),
            performance_score=6.0 + (i % 4),
        )
        for i in range(20)
    ]


@pytest.fixture
def model_selector(mock_models):
    """Create a ModelSelector instance for benchmarking."""
    # Create mock provider that returns our test models
    mock_provider = AsyncMock()
    mock_provider.get_available_models = AsyncMock(return_value=mock_models)

    return ModelSelector(
        providers={"test_provider": mock_provider},
        hardware_detector=Mock(),
        selection_criteria=ModelSelectionCriteria(
            prefer_free_models=True,
            min_therapeutic_safety_score=7.0,
        ),
    )


@pytest.fixture
def fallback_handler(mock_models):
    """Create a FallbackHandler instance for benchmarking."""
    # Create mock provider that returns our test models
    mock_provider = AsyncMock()
    mock_provider.get_available_models = AsyncMock(return_value=mock_models)

    return FallbackHandler(
        providers={"test_provider": mock_provider},
        fallback_config=FallbackConfiguration(
            enabled=True,
            fallback_strategy="performance_based",
        ),
    )


# ============================================================================
# Model Selection Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestModelSelectionPerformance:
    """Performance benchmarks for model selection."""

    def test_model_selection_latency_simple(self, benchmark, model_selector):
        """Benchmark: Simple model selection should complete in < 500ms."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=5000,
            min_quality_score=7.0,
        )

        # Create synchronous wrapper for async method
        def sync_select_model():
            return asyncio.run(model_selector.select_model(requirements))

        # Benchmark the selection
        result = benchmark(sync_select_model)

        # Verify correctness
        assert result is not None
        assert result.model_id.startswith("test-model-")

        # Performance assertion
        stats = benchmark.stats
        mean_time = stats["mean"]
        assert mean_time < 0.5, f"Model selection took {mean_time}s, expected < 0.5s"

    def test_model_selection_with_filtering(self, benchmark, model_selector):
        """Benchmark: Model selection with complex filtering."""
        requirements = ModelRequirements(
            task_type=TaskType.THERAPEUTIC_RESPONSE,
            max_latency_ms=3000,
            min_quality_score=8.0,
            max_cost_per_token=0.0,  # Free models only
            required_capabilities=["chat"],
            therapeutic_safety_required=True,
        )

        # Create synchronous wrapper for async method
        def sync_select_model():
            return asyncio.run(model_selector.select_model(requirements))

        # Benchmark the selection
        result = benchmark(sync_select_model)

        # Verify correctness
        assert result is not None

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 0.5, (
            f"Filtered selection took {stats['mean']}s, expected < 0.5s"
        )

    def test_model_ranking_performance(self, benchmark, model_selector, mock_models):
        """Benchmark: Model ranking algorithm performance."""
        requirements = ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            min_quality_score=6.0,
        )

        # Create synchronous wrapper for async method
        def sync_rank_models():
            return asyncio.run(model_selector.rank_models(mock_models, requirements))

        # Benchmark the ranking
        result = benchmark(sync_rank_models)

        # Verify correctness
        assert len(result) > 0
        assert all(isinstance(m, ModelInfo) for m in result)

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 0.1, f"Ranking took {stats['mean']}s, expected < 0.1s"


# ============================================================================
# Fallback Mechanism Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestFallbackPerformance:
    """Performance benchmarks for fallback mechanisms."""

    def test_fallback_activation_latency(self, benchmark, fallback_handler):
        """Benchmark: Fallback activation should complete in < 1s."""
        failed_model_id = "test-model-0"
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=5000,
        )

        # Create synchronous wrapper for async method
        def sync_get_fallback():
            return asyncio.run(
                fallback_handler.get_fallback_model(failed_model_id, requirements)
            )

        # Benchmark fallback selection
        result = benchmark(sync_get_fallback)

        # Verify correctness
        assert result is not None
        assert result.model_id != failed_model_id

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 1.0, f"Fallback took {stats['mean']}s, expected < 1s"

    def test_fallback_strategy_selection(self, benchmark, fallback_handler):
        """Benchmark: Fallback strategy selection performance."""
        failed_model_id = "test-model-5"
        requirements = ModelRequirements(
            task_type=TaskType.DIALOGUE_GENERATION,
            max_cost_per_token=0.001,
        )

        # Create synchronous wrapper for async method
        def sync_get_fallback():
            return asyncio.run(
                fallback_handler.get_fallback_model(failed_model_id, requirements)
            )

        # Benchmark strategy-based fallback
        result = benchmark(sync_get_fallback)

        # Verify correctness
        assert result is not None

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 1.0, (
            f"Strategy fallback took {stats['mean']}s, expected < 1s"
        )


# ============================================================================
# End-to-End Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestEndToEndPerformance:
    """End-to-end performance benchmarks."""

    @pytest.mark.asyncio
    async def test_component_initialization_performance(self, benchmark, mock_config):
        """Benchmark: Component initialization performance."""

        def create_component():
            return ModelManagementComponent(mock_config)

        # Benchmark component creation
        component = benchmark(create_component)

        # Verify correctness
        assert component is not None
        assert component.name == "model_management"

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 0.1, (
            f"Initialization took {stats['mean']}s, expected < 0.1s"
        )

    def test_model_info_creation_performance(self, benchmark):
        """Benchmark: ModelInfo object creation performance."""

        def create_model_info():
            return ModelInfo(
                model_id="benchmark-model",
                name="Benchmark Model",
                provider_type=ProviderType.OPENROUTER,
                description="Model for benchmarking",
                context_length=8192,
                cost_per_token=0.0,
                is_free=True,
                capabilities=["chat", "completion"],
                therapeutic_safety_score=8.0,
                performance_score=7.5,
            )

        # Benchmark object creation
        model = benchmark(create_model_info)

        # Verify correctness
        assert model.model_id == "benchmark-model"

        # Performance assertion
        stats = benchmark.stats
        assert stats["mean"] < 0.001, (
            f"Object creation took {stats['mean']}s, expected < 0.001s"
        )


# ============================================================================
# Throughput Benchmarks
# ============================================================================


@pytest.mark.performance
class TestThroughputBenchmarks:
    """Throughput benchmarks for model management operations."""

    def test_model_filtering_throughput(self, benchmark, mock_models):
        """Benchmark: Model filtering throughput."""

        def filter_free_models():
            return [m for m in mock_models if m.is_free]

        # Benchmark filtering
        result = benchmark(filter_free_models)

        # Verify correctness
        assert len(result) > 0
        assert all(m.is_free for m in result)

        # Calculate throughput
        ops_per_second = 1 / benchmark.stats["mean"]
        assert ops_per_second > 1000, (
            f"Throughput: {ops_per_second} ops/s, expected > 1000 ops/s"
        )

    def test_model_scoring_throughput(self, benchmark, mock_models):
        """Benchmark: Model scoring throughput."""

        def score_models():
            return sorted(
                [m for m in mock_models if m.performance_score is not None],
                key=lambda m: m.performance_score,
                reverse=True,
            )

        # Benchmark scoring
        result = benchmark(score_models)

        # Verify correctness
        assert len(result) > 0

        # Calculate throughput
        ops_per_second = 1 / benchmark.stats["mean"]
        assert ops_per_second > 500, (
            f"Throughput: {ops_per_second} ops/s, expected > 500 ops/s"
        )
