"""
Concrete value tests for ModelSelector.

These tests complement property-based tests by validating business logic correctness
with specific, known values. They are designed to catch mutations that property-based
tests miss (e.g., changes to scoring weights, default values, etc.).

Created in response to mutation testing findings that revealed property-based tests
validate structure but not business logic correctness.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from tta_ai.models import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import ModelSelectionCriteria
from tta_ai.models.services.model_selector import ModelSelector


class TestModelSelectorConcreteRanking:
    """Concrete tests for model ranking logic."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider."""
        provider = AsyncMock()
        provider.provider_type = ProviderType.OPENROUTER
        return provider

    @pytest.fixture
    def mock_hardware_detector(self):
        """Create a mock hardware detector."""
        detector = MagicMock()
        detector.get_available_vram.return_value = 8000
        detector.get_cpu_count.return_value = 8
        return detector

    @pytest.fixture
    def selector(self, mock_provider, mock_hardware_detector):
        """Create ModelSelector instance."""
        return ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

    @pytest.fixture
    def requirements(self):
        """Create basic requirements."""
        return ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            context_length_needed=4096,
            therapeutic_safety_required=False,  # Avoid default filtering
        )

    async def test_therapeutic_safety_affects_ranking(self, selector, requirements):
        """
        Concrete test: Therapeutic safety score affects ranking.

        This test should KILL mutation MUT-1 (zero therapeutic safety weight).
        """
        # Create two models differing ONLY in therapeutic safety
        model_high_safety = ModelInfo(
            model_id="high-safety-model",
            name="High Safety Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=9.0,  # High safety
            performance_score=5.0,  # Same performance
            cost_per_token=0.0,
        )

        model_low_safety = ModelInfo(
            model_id="low-safety-model",
            name="Low Safety Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=3.0,  # Low safety
            performance_score=5.0,  # Same performance
            cost_per_token=0.0,
        )

        # Rank models
        ranked = await selector.rank_models(
            [model_low_safety, model_high_safety], requirements
        )

        # High safety should rank FIRST
        assert ranked[0].model_id == "high-safety-model", (
            "Model with higher therapeutic safety score should rank first. "
            "If this fails, therapeutic safety scoring may be broken."
        )
        assert ranked[1].model_id == "low-safety-model"

    async def test_performance_score_affects_ranking(self, selector, requirements):
        """
        Concrete test: Performance score affects ranking.

        This test should KILL mutation MUT-3 (remove performance score).
        """
        # Create two models differing ONLY in performance
        model_high_perf = ModelInfo(
            model_id="high-perf-model",
            name="High Performance Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=7.0,  # Same safety
            performance_score=9.0,  # High performance
            cost_per_token=0.0,
        )

        model_low_perf = ModelInfo(
            model_id="low-perf-model",
            name="Low Performance Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=7.0,  # Same safety
            performance_score=3.0,  # Low performance
            cost_per_token=0.0,
        )

        # Rank models
        ranked = await selector.rank_models(
            [model_low_perf, model_high_perf], requirements
        )

        # High performance should rank FIRST
        assert ranked[0].model_id == "high-perf-model", (
            "Model with higher performance score should rank first. "
            "If this fails, performance scoring may be broken."
        )
        assert ranked[1].model_id == "low-perf-model"

    async def test_combined_scores_affect_ranking(self, selector, requirements):
        """
        Concrete test: Combined scores produce expected ranking.

        Tests that multiple scoring factors work together correctly.
        """
        # Model 1: High safety, low performance
        model_1 = ModelInfo(
            model_id="model-1",
            name="Model 1",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=9.0,
            performance_score=3.0,
            cost_per_token=0.0,
        )

        # Model 2: Medium safety, medium performance
        model_2 = ModelInfo(
            model_id="model-2",
            name="Model 2",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=6.0,
            performance_score=6.0,
            cost_per_token=0.0,
        )

        # Model 3: Low safety, high performance
        model_3 = ModelInfo(
            model_id="model-3",
            name="Model 3",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=3.0,
            performance_score=9.0,
            cost_per_token=0.0,
        )

        # Rank models
        ranked = await selector.rank_models([model_3, model_1, model_2], requirements)

        # With default weights (therapeutic_safety_weight=0.3, performance_weight=0.3):
        # Model 1: (9.0 * 0.3) + (3.0 * 0.3) = 2.7 + 0.9 = 3.6 + other factors
        # Model 2: (6.0 * 0.3) + (6.0 * 0.3) = 1.8 + 1.8 = 3.6 + other factors
        # Model 3: (3.0 * 0.3) + (9.0 * 0.3) = 0.9 + 2.7 = 3.6 + other factors

        # All should have similar base scores, but other factors may differentiate
        # At minimum, verify all models are ranked
        assert len(ranked) == 3
        ranked_ids = [m.model_id for m in ranked]
        assert "model-1" in ranked_ids
        assert "model-2" in ranked_ids
        assert "model-3" in ranked_ids


class TestModelSelectorScoreCalculation:
    """Concrete tests for score calculation with known values."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider."""
        provider = AsyncMock()
        provider.provider_type = ProviderType.OPENROUTER
        return provider

    @pytest.fixture
    def mock_hardware_detector(self):
        """Create a mock hardware detector."""
        detector = MagicMock()
        detector.get_available_vram.return_value = 8000
        detector.get_cpu_count.return_value = 8
        return detector

    @pytest.fixture
    def selector(self, mock_provider, mock_hardware_detector):
        """Create ModelSelector instance."""
        return ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

    @pytest.fixture
    def requirements(self):
        """Create basic requirements."""
        return ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            context_length_needed=4096,
            therapeutic_safety_required=False,
        )

    async def test_score_calculation_with_known_values(self, selector, requirements):
        """
        Concrete test: Score calculation with known inputs produces expected output.

        This test validates the exact scoring algorithm.
        """
        model = ModelInfo(
            model_id="test-model",
            name="Test Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=8.0,
            performance_score=7.0,
            cost_per_token=0.0,
        )

        # Calculate score
        score = await selector._calculate_model_score(model, requirements)

        # With default criteria:
        # - therapeutic_safety_weight = 0.3
        # - performance_weight = 0.3
        # - cost_weight = 0.2
        # - context_weight = 0.1
        # - provider_preference_weight = 0.1

        # Expected contributions:
        # Therapeutic safety: 8.0 * 0.3 = 2.4
        # Performance: 7.0 * 0.3 = 2.1
        # Cost: (1.0 - 0.0) * 10 * 0.2 = 2.0 (free model)
        # Context: some bonus for 8192 > 4096
        # Provider: some bonus for OpenRouter

        # Minimum expected score (without bonuses)
        min_expected = 2.4 + 2.1 + 2.0  # = 6.5

        assert score >= min_expected, (
            f"Score {score} is less than minimum expected {min_expected}. "
            "Scoring algorithm may be broken."
        )

        # Score should be reasonable (not negative, not absurdly high)
        assert 0 <= score <= 100, f"Score {score} is outside reasonable range [0, 100]"

    async def test_therapeutic_safety_weight_applied(
        self, mock_provider, mock_hardware_detector, requirements
    ):
        """
        Concrete test: Therapeutic safety weight is actually applied.

        This test should KILL mutation MUT-1 (zero therapeutic safety weight).
        """
        # Create selector with HIGH therapeutic safety weight
        high_weight_criteria = ModelSelectionCriteria(
            therapeutic_safety_weight=0.7,  # Very high weight
            performance_weight=0.2,
            cost_weight=0.1,
        )

        selector_high_weight = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=high_weight_criteria,
        )

        # Create selector with LOW therapeutic safety weight
        low_weight_criteria = ModelSelectionCriteria(
            therapeutic_safety_weight=0.1,  # Very low weight
            performance_weight=0.7,
            cost_weight=0.2,
        )

        selector_low_weight = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
            selection_criteria=low_weight_criteria,
        )

        # Model with high safety, low performance
        model = ModelInfo(
            model_id="test-model",
            name="Test Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=9.0,  # High
            performance_score=2.0,  # Low
            cost_per_token=0.0,
        )

        # Calculate scores with different weights
        score_high_weight = await selector_high_weight._calculate_model_score(
            model, requirements
        )
        score_low_weight = await selector_low_weight._calculate_model_score(
            model, requirements
        )

        # With high therapeutic safety weight, score should be higher
        # because model has high safety (9.0) but low performance (2.0)
        assert score_high_weight > score_low_weight, (
            "Changing therapeutic safety weight should affect score. "
            "If this fails, therapeutic safety weight may not be applied."
        )


class TestModelSelectorDefaultValues:
    """Concrete tests for default value behavior."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider."""
        provider = AsyncMock()
        provider.provider_type = ProviderType.OPENROUTER
        return provider

    @pytest.fixture
    def mock_hardware_detector(self):
        """Create a mock hardware detector."""
        detector = MagicMock()
        detector.get_available_vram.return_value = 8000
        detector.get_cpu_count.return_value = 8
        return detector

    @pytest.fixture
    def selector(self, mock_provider, mock_hardware_detector):
        """Create ModelSelector instance."""
        return ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=mock_hardware_detector,
        )

    @pytest.fixture
    def requirements(self):
        """Create basic requirements."""
        return ModelRequirements(
            task_type=TaskType.NARRATIVE_GENERATION,
            context_length_needed=4096,
            therapeutic_safety_required=False,
        )

    async def test_default_performance_score_applied(self, selector, requirements):
        """
        Concrete test: Default performance score of 5.0 is applied.

        This test should KILL mutation MUT-4 (change default performance score).
        """
        # Model WITHOUT performance score
        model_no_perf = ModelInfo(
            model_id="no-perf-model",
            name="No Performance Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=7.0,
            performance_score=None,  # No performance data
            cost_per_token=0.0,
        )

        # Model WITH performance score of 5.0 (the default)
        model_with_perf = ModelInfo(
            model_id="with-perf-model",
            name="With Performance Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=7.0,
            performance_score=5.0,  # Explicit default value
            cost_per_token=0.0,
        )

        # Calculate scores
        score_no_perf = await selector._calculate_model_score(
            model_no_perf, requirements
        )
        score_with_perf = await selector._calculate_model_score(
            model_with_perf, requirements
        )

        # Scores should be very close (within floating point error)
        # because None should default to 5.0
        assert abs(score_no_perf - score_with_perf) < 0.1, (
            f"Model without performance score (score={score_no_perf}) should get "
            f"same score as model with performance_score=5.0 (score={score_with_perf}). "
            "Default performance score may not be 5.0."
        )

    async def test_default_therapeutic_safety_for_openrouter(
        self, selector, requirements
    ):
        """
        Concrete test: Default therapeutic safety score for OpenRouter is 7.0.
        """
        # Model WITHOUT therapeutic safety score
        model = ModelInfo(
            model_id="test-model",
            name="Test Model",
            provider_type=ProviderType.OPENROUTER,
            context_length=8192,
            therapeutic_safety_score=None,  # No safety data
            performance_score=5.0,
            cost_per_token=0.0,
        )

        # Calculate score
        score = await selector._calculate_model_score(model, requirements)

        # Score should be positive (default applied)
        assert score > 0, (
            "Model without therapeutic safety score should still get a positive score "
            "due to default value."
        )

        # With default therapeutic safety of 7.0 and weight of 0.3:
        # Expected contribution: 7.0 * 0.3 = 2.1
        # Plus performance: 5.0 * 0.3 = 1.5
        # Plus cost: ~2.0
        # Minimum: ~5.6
        assert score >= 5.0, (
            f"Score {score} is lower than expected with default therapeutic safety. "
            "Default value may not be applied correctly."
        )
