"""
Performance benchmarks for Model Management services.

Tests service initialization times, method execution times, and throughput.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from tta_ai.models import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import (
    FallbackConfiguration,
    ModelSelectionCriteria,
)
from tta_ai.models.services.fallback_handler import FallbackHandler
from tta_ai.models.services.model_selector import ModelSelector
from tta_ai.models.services.performance_monitor import (
    PerformanceMonitor,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_models():
    """Create sample models for testing."""
    return [
        ModelInfo(
            model_id=f"model-{i}",
            name=f"Test Model {i}",
            provider_type=ProviderType.OPENROUTER,
            description="Test model",
            context_length=8000,
            cost_per_token=0.001 if i % 2 == 0 else 0.0,
            is_free=i % 2 != 0,
            capabilities=["chat", "completion"],
            therapeutic_safety_score=7.5,
            performance_score=8.0,
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_requirements():
    """Create sample requirements for testing."""
    return ModelRequirements(
        task_type=TaskType.GENERAL_CHAT,
        max_latency_ms=1000,
        min_quality_score=7.0,
        context_length_needed=4000,
    )


@pytest.fixture
def sample_criteria():
    """Create sample selection criteria for testing."""
    return ModelSelectionCriteria(
        therapeutic_safety_weight=0.4,
        performance_weight=0.4,
        cost_weight=0.2,
    )


@pytest.fixture
def sample_fallback_config():
    """Create sample fallback configuration for testing."""
    return FallbackConfiguration(
        fallback_strategy="performance_based",
        max_retries=3,
        retry_delay_seconds=1.0,
    )


@pytest.fixture
def mock_hardware_detector():
    """Create a mock hardware detector."""
    detector = Mock()
    detector.has_gpu = Mock(return_value=True)
    detector.get_available_memory = Mock(return_value=16000)
    return detector


# ============================================================================
# ModelSelector Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestModelSelectorPerformance:
    """Performance benchmarks for ModelSelector service."""

    def test_model_selector_initialization(self, benchmark, mock_hardware_detector):
        """Benchmark: ModelSelector initialization time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])

        def init_selector():
            return ModelSelector(
                providers={"test": mock_provider},
                hardware_detector=mock_hardware_detector,
            )

        result = benchmark(init_selector)
        assert result is not None

    def test_select_model_execution_time(
        self,
        benchmark,
        sample_models,
        sample_requirements,
        sample_criteria,
        mock_hardware_detector,
    ):
        """Benchmark: select_model() execution time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=sample_models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=sample_criteria,
        )

        def sync_select_model():
            return asyncio.run(selector.select_model(sample_requirements))

        result = benchmark(sync_select_model)
        assert result is not None

    def test_rank_models_execution_time(
        self,
        benchmark,
        sample_models,
        sample_requirements,
        sample_criteria,
        mock_hardware_detector,
    ):
        """Benchmark: rank_models() execution time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=sample_models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=sample_criteria,
        )

        def sync_rank_models():
            return asyncio.run(selector.rank_models(sample_models, sample_requirements))

        result = benchmark(sync_rank_models)
        assert len(result) > 0

    def test_model_selection_throughput(
        self,
        benchmark,
        sample_models,
        sample_requirements,
        sample_criteria,
        mock_hardware_detector,
    ):
        """Benchmark: Model selection throughput (selections per second)."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=sample_models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=sample_criteria,
        )

        def select_multiple():
            for _ in range(10):
                asyncio.run(selector.select_model(sample_requirements))

        benchmark(select_multiple)


# ============================================================================
# FallbackHandler Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestFallbackHandlerPerformance:
    """Performance benchmarks for FallbackHandler service."""

    def test_fallback_handler_initialization(self, benchmark, sample_fallback_config):
        """Benchmark: FallbackHandler initialization time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])

        def init_handler():
            return FallbackHandler(
                providers={"test": mock_provider},
                fallback_config=sample_fallback_config,
            )

        result = benchmark(init_handler)
        assert result is not None

    def test_get_fallback_model_execution_time(
        self, benchmark, sample_models, sample_requirements, sample_fallback_config
    ):
        """Benchmark: get_fallback_model() execution time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=sample_models)

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=sample_fallback_config,
        )

        def sync_get_fallback():
            return asyncio.run(
                handler.get_fallback_model("failed-model", sample_requirements)
            )

        result = benchmark(sync_get_fallback)
        assert result is not None

    def test_handle_model_failure_execution_time(
        self, benchmark, sample_fallback_config
    ):
        """Benchmark: handle_model_failure() execution time."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=sample_fallback_config,
        )

        def sync_handle_failure():
            return asyncio.run(
                handler.handle_model_failure("test-model", Exception("Test error"))
            )

        benchmark(sync_handle_failure)

    def test_fallback_selection_throughput(
        self, benchmark, sample_models, sample_requirements, sample_fallback_config
    ):
        """Benchmark: Fallback selection throughput (selections per second)."""
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=sample_models)

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=sample_fallback_config,
        )

        def select_multiple_fallbacks():
            for i in range(10):
                asyncio.run(
                    handler.get_fallback_model(f"failed-model-{i}", sample_requirements)
                )

        benchmark(select_multiple_fallbacks)


# ============================================================================
# PerformanceMonitor Performance Benchmarks
# ============================================================================


@pytest.mark.performance
class TestPerformanceMonitorPerformance:
    """Performance benchmarks for PerformanceMonitor service."""

    def test_performance_monitor_initialization(self, benchmark):
        """Benchmark: PerformanceMonitor initialization time."""

        def init_monitor():
            return PerformanceMonitor()

        result = benchmark(init_monitor)
        assert result is not None

    def test_record_metrics_execution_time(self, benchmark):
        """Benchmark: record_metrics() execution time."""
        monitor = PerformanceMonitor()

        metrics = {
            "response_time_ms": 150.0,
            "tokens_per_second": 50.0,
            "total_tokens": 500,
            "quality_score": 8.5,
        }

        def sync_record_metrics():
            return asyncio.run(monitor.record_metrics("test-model", metrics))

        benchmark(sync_record_metrics)

    def test_get_model_performance_execution_time(self, benchmark):
        """Benchmark: get_model_performance() execution time."""
        monitor = PerformanceMonitor()

        # Record some metrics first
        for i in range(10):
            asyncio.run(
                monitor.record_metrics(
                    "test-model",
                    {
                        "response_time_ms": 100.0 + i * 10,
                        "tokens_per_second": 50.0,
                        "total_tokens": 500,
                    },
                )
            )

        def sync_get_performance():
            return asyncio.run(monitor.get_model_performance("test-model"))

        result = benchmark(sync_get_performance)
        assert isinstance(result, dict)

    def test_metrics_recording_throughput(self, benchmark):
        """Benchmark: Metrics recording throughput (records per second)."""
        monitor = PerformanceMonitor()

        metrics = {
            "response_time_ms": 150.0,
            "tokens_per_second": 50.0,
            "total_tokens": 500,
        }

        def record_multiple_metrics():
            for i in range(100):
                asyncio.run(monitor.record_metrics(f"model-{i % 10}", metrics))

        benchmark(record_multiple_metrics)
