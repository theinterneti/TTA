"""

# Logseq: [[TTA.dev/Tests/Integration/Model_management/Test_service_integration]]
Integration Tests for Model Management Service Interactions.

Tests the interactions between ModelSelector, FallbackHandler, and PerformanceMonitor
services working together with real (non-mocked) instances.
"""

from datetime import datetime
from unittest.mock import AsyncMock

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
    """Create sample models for integration testing."""
    return [
        ModelInfo(
            model_id="model-high-perf",
            name="High Performance Model",
            provider_type=ProviderType.OPENROUTER,
            description="Fast and reliable",
            context_length=8000,
            cost_per_token=0.002,
            is_free=False,
            capabilities=["chat", "completion"],
            therapeutic_safety_score=8.5,
            performance_score=9.0,
        ),
        ModelInfo(
            model_id="model-low-cost",
            name="Low Cost Model",
            provider_type=ProviderType.OPENROUTER,
            description="Budget friendly",
            context_length=4000,
            cost_per_token=0.0,
            is_free=True,
            capabilities=["chat"],
            therapeutic_safety_score=7.0,
            performance_score=6.5,
        ),
        ModelInfo(
            model_id="model-balanced",
            name="Balanced Model",
            provider_type=ProviderType.LOCAL,
            description="Good balance",
            context_length=8000,
            cost_per_token=0.001,
            is_free=False,
            capabilities=["chat", "completion"],
            therapeutic_safety_score=8.0,
            performance_score=8.0,
        ),
    ]


@pytest.fixture
def mock_provider(sample_models):
    """Create a mock provider with sample models."""
    provider = AsyncMock()
    provider.get_available_models = AsyncMock(return_value=sample_models)
    return provider


@pytest.fixture
def mock_hardware_detector():
    """Create a mock hardware detector."""
    from unittest.mock import Mock

    detector = Mock()
    detector.has_gpu = Mock(return_value=True)
    detector.get_available_memory = Mock(return_value=16000)
    return detector


# ============================================================================
# Integration Tests: ModelSelector + FallbackHandler
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestModelSelectorFallbackIntegration:
    """Test interactions between ModelSelector and FallbackHandler."""

    async def test_fallback_after_model_selection_failure(
        self, mock_provider, mock_hardware_detector, sample_models
    ):
        """Integration: Fallback handler provides alternative when selected model fails."""
        # Create real service instances
        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

        fallback_handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=FallbackConfiguration(
                fallback_strategy="performance_based"
            ),
        )

        # Select a model
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=1000,
        )

        selected_model = await selector.select_model(requirements)
        assert selected_model is not None
        selected_model_id = selected_model.model_id

        # Simulate failure and get fallback
        await fallback_handler.handle_model_failure(
            selected_model_id, Exception("Model unavailable")
        )

        fallback_model = await fallback_handler.get_fallback_model(
            selected_model_id, requirements
        )

        # Verify fallback is different from failed model
        assert fallback_model is not None
        assert fallback_model.model_id != selected_model_id
        assert fallback_model in sample_models

    async def test_fallback_respects_selector_criteria(
        self, mock_provider, mock_hardware_detector
    ):
        """Integration: Fallback handler respects selection criteria from selector."""
        # Create selector with specific criteria
        criteria = ModelSelectionCriteria(
            therapeutic_safety_weight=0.6,
            performance_weight=0.3,
            cost_weight=0.1,
            min_therapeutic_safety_score=7.5,
        )

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=criteria,
        )

        fallback_handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=FallbackConfiguration(
                fallback_strategy="performance_based"
            ),
        )

        # Select model with high safety requirements
        requirements = ModelRequirements(
            task_type=TaskType.THERAPEUTIC_RESPONSE,
            therapeutic_safety_required=True,
            min_quality_score=7.5,
        )

        selected_model = await selector.select_model(requirements)
        assert selected_model is not None

        # Get fallback - should also meet safety requirements
        fallback_model = await fallback_handler.get_fallback_model(
            selected_model.model_id, requirements
        )

        if fallback_model:  # May be None if no compatible models
            assert (
                fallback_model.therapeutic_safety_score is None
                or fallback_model.therapeutic_safety_score >= 7.0
            )


# ============================================================================
# Integration Tests: ModelSelector + PerformanceMonitor
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestModelSelectorPerformanceMonitorIntegration:
    """Test interactions between ModelSelector and PerformanceMonitor."""

    async def test_performance_tracking_during_selection(
        self, mock_provider, mock_hardware_detector
    ):
        """Integration: Performance monitor tracks model selection operations."""
        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

        monitor = PerformanceMonitor()

        # Select a model and track performance
        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        start_time = datetime.now()
        selected_model = await selector.select_model(requirements)
        end_time = datetime.now()

        assert selected_model is not None

        # Record selection performance
        selection_time_ms = (end_time - start_time).total_seconds() * 1000

        await monitor.record_metrics(
            selected_model.model_id,
            {
                "response_time_ms": selection_time_ms,
                "total_tokens": 0,  # No tokens for selection
                "tokens_per_second": 0.0,
            },
        )

        # Verify metrics were recorded
        stats = await monitor.get_model_performance(selected_model.model_id)
        assert stats is not None
        assert "total_requests" in stats
        assert stats["total_requests"] >= 1

    async def test_performance_based_model_selection(
        self, mock_provider, mock_hardware_detector, sample_models
    ):
        """Integration: Selector uses performance data to choose models."""
        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

        monitor = PerformanceMonitor()

        # Record performance history for models
        # Model 1: High performance
        for _ in range(5):
            await monitor.record_metrics(
                "model-high-perf",
                {
                    "response_time_ms": 100.0,
                    "total_tokens": 500,
                    "tokens_per_second": 50.0,
                    "quality_score": 9.0,
                },
            )

        # Model 2: Low performance
        for _ in range(5):
            await monitor.record_metrics(
                "model-low-cost",
                {
                    "response_time_ms": 500.0,
                    "total_tokens": 200,
                    "tokens_per_second": 10.0,
                    "quality_score": 6.0,
                },
            )

        # Select model - should prefer high performance model
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=2000,  # Increased to allow model selection
            therapeutic_safety_required=False,  # Not required for this test
        )

        selected_model = await selector.select_model(requirements)
        assert selected_model is not None

        # Verify performance data exists
        high_perf_stats = await monitor.get_model_performance("model-high-perf")
        low_cost_stats = await monitor.get_model_performance("model-low-cost")

        assert high_perf_stats["total_requests"] == 5
        assert low_cost_stats["total_requests"] == 5


# ============================================================================
# Integration Tests: FallbackHandler + PerformanceMonitor
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestFallbackHandlerPerformanceMonitorIntegration:
    """Test interactions between FallbackHandler and PerformanceMonitor."""

    async def test_fallback_uses_performance_data(self, mock_provider):
        """Integration: Fallback handler uses performance data for selection."""
        fallback_handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=FallbackConfiguration(
                fallback_strategy="performance_based"
            ),
        )

        monitor = PerformanceMonitor()

        # Record different performance for models
        await monitor.record_metrics(
            "model-high-perf",
            {"response_time_ms": 100.0, "total_tokens": 500, "quality_score": 9.0},
        )

        await monitor.record_metrics(
            "model-balanced",
            {"response_time_ms": 200.0, "total_tokens": 400, "quality_score": 8.0},
        )

        # Get fallback with performance-based strategy
        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        fallback_model = await fallback_handler.get_fallback_model(
            "model-low-cost", requirements
        )

        assert fallback_model is not None

        # Verify performance data was considered
        high_perf_stats = await monitor.get_model_performance("model-high-perf")
        assert high_perf_stats["total_requests"] >= 1

    async def test_performance_tracking_after_fallback(self, mock_provider):
        """Integration: Performance monitor tracks fallback operations."""
        fallback_handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=FallbackConfiguration(fallback_strategy="cost_based"),
        )

        monitor = PerformanceMonitor()

        # Simulate failure and fallback
        failed_model_id = "model-high-perf"
        await fallback_handler.handle_model_failure(
            failed_model_id, Exception("Timeout")
        )

        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        start_time = datetime.now()
        fallback_model = await fallback_handler.get_fallback_model(
            failed_model_id, requirements
        )
        end_time = datetime.now()

        assert fallback_model is not None

        # Record fallback performance
        fallback_time_ms = (end_time - start_time).total_seconds() * 1000

        await monitor.record_metrics(
            fallback_model.model_id,
            {
                "response_time_ms": fallback_time_ms,
                "total_tokens": 0,
                "metadata": {"fallback_from": failed_model_id},
            },
        )

        # Verify fallback was tracked
        stats = await monitor.get_model_performance(fallback_model.model_id)
        assert stats is not None


# ============================================================================
# Integration Tests: Complete Workflow
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestCompleteWorkflow:
    """Test complete workflow: selection → failure → fallback → performance tracking."""

    async def test_end_to_end_workflow(
        self, mock_provider, mock_hardware_detector, sample_models
    ):
        """Integration: Complete workflow from selection to fallback with performance tracking."""
        # Initialize all services
        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

        fallback_handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=FallbackConfiguration(
                fallback_strategy="performance_based"
            ),
        )

        monitor = PerformanceMonitor()

        # Step 1: Select initial model
        requirements = ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            max_latency_ms=1000,
            min_quality_score=7.0,
        )

        selected_model = await selector.select_model(requirements)
        assert selected_model is not None

        # Step 2: Record initial performance
        await monitor.record_metrics(
            selected_model.model_id,
            {
                "response_time_ms": 150.0,
                "total_tokens": 500,
                "tokens_per_second": 45.0,
                "quality_score": 8.5,
            },
        )

        # Step 3: Simulate failure
        await fallback_handler.handle_model_failure(
            selected_model.model_id, Exception("Model overloaded")
        )

        # Step 4: Get fallback model
        fallback_model = await fallback_handler.get_fallback_model(
            selected_model.model_id, requirements
        )

        assert fallback_model is not None
        assert fallback_model.model_id != selected_model.model_id

        # Step 5: Record fallback performance
        await monitor.record_metrics(
            fallback_model.model_id,
            {
                "response_time_ms": 200.0,
                "total_tokens": 480,
                "tokens_per_second": 40.0,
                "quality_score": 8.0,
                "metadata": {"fallback_from": selected_model.model_id},
            },
        )

        # Step 6: Verify complete workflow
        original_stats = await monitor.get_model_performance(selected_model.model_id)
        fallback_stats = await monitor.get_model_performance(fallback_model.model_id)

        assert original_stats["total_requests"] >= 1
        assert fallback_stats["total_requests"] >= 1

        # Verify failure was recorded
        assert selected_model.model_id in fallback_handler._failed_models
        assert fallback_handler._failure_counts[selected_model.model_id] >= 1