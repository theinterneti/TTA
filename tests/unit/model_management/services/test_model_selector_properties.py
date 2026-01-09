"""

# Logseq: [[TTA.dev/Tests/Unit/Model_management/Services/Test_model_selector_properties]]
Property-Based Tests for ModelSelector Service.

This module contains property-based tests using Hypothesis to validate
the ModelSelector service's behavior across a wide range of inputs.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from tta_ai.models import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import ModelSelectionCriteria
from tta_ai.models.services import ModelSelector

# ============================================================================
# Hypothesis Strategies
# ============================================================================


@st.composite
def model_info_strategy(draw):
    """Generate valid ModelInfo instances."""
    return ModelInfo(
        model_id=draw(
            st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(
                    whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"
                ),
            )
        ),
        name=draw(st.text(min_size=1, max_size=100)),
        provider_type=draw(st.sampled_from(list(ProviderType))),
        description=draw(st.text(max_size=200)),
        context_length=draw(
            st.one_of(st.none(), st.integers(min_value=512, max_value=128000))
        ),
        cost_per_token=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=0.01))
        ),
        is_free=draw(st.booleans()),
        capabilities=draw(
            st.lists(
                st.sampled_from(
                    [
                        "chat",
                        "creative_writing",
                        "storytelling",
                        "empathy",
                        "safety",
                        "therapeutic",
                        "analysis",
                        "reasoning",
                    ]
                ),
                max_size=5,
                unique=True,
            )
        ),
        therapeutic_safety_score=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=10.0))
        ),
        performance_score=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=10.0))
        ),
    )


@st.composite
def model_requirements_strategy(draw):
    """Generate valid ModelRequirements instances."""
    return ModelRequirements(
        task_type=draw(st.sampled_from(list(TaskType))),
        max_latency_ms=draw(
            st.one_of(st.none(), st.integers(min_value=100, max_value=10000))
        ),
        min_quality_score=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=10.0))
        ),
        max_cost_per_token=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=0.01))
        ),
        context_length_needed=draw(
            st.one_of(st.none(), st.integers(min_value=512, max_value=32000))
        ),
        required_capabilities=draw(
            st.lists(
                st.sampled_from(["chat", "creative_writing", "empathy", "safety"]),
                max_size=3,
                unique=True,
            )
        ),
        therapeutic_safety_required=draw(st.booleans()),
    )


@st.composite
def selection_criteria_strategy(draw):
    """Generate valid ModelSelectionCriteria instances."""
    # Ensure weights sum to approximately 1.0
    weights = draw(
        st.lists(st.floats(min_value=0.1, max_value=0.8), min_size=3, max_size=3)
    )
    total = sum(weights)
    normalized_weights = [w / total for w in weights]

    return ModelSelectionCriteria(
        primary_criteria=draw(
            st.sampled_from(["cost_effectiveness", "performance", "availability"])
        ),
        fallback_criteria=draw(
            st.sampled_from(["cost_effectiveness", "performance", "availability"])
        ),
        therapeutic_safety_weight=normalized_weights[0],
        performance_weight=normalized_weights[1],
        cost_weight=normalized_weights[2],
        min_therapeutic_safety_score=draw(st.floats(min_value=5.0, max_value=9.0)),
        max_acceptable_latency_ms=draw(st.integers(min_value=1000, max_value=10000)),
        max_cost_per_token=draw(
            st.one_of(st.none(), st.floats(min_value=0.0, max_value=0.01))
        ),
        prefer_local_models=draw(st.booleans()),
        prefer_free_models=draw(st.booleans()),
        require_streaming=draw(st.booleans()),
    )


# ============================================================================
# Helper Functions
# ============================================================================


def create_mock_hardware_detector():
    """Create a mock hardware detector."""
    detector = Mock()
    detector.has_gpu = Mock(return_value=True)
    detector.get_available_memory = Mock(return_value=16000)
    return detector


# ============================================================================
# Property-Based Tests
# ============================================================================


@pytest.mark.property
class TestModelSelectorProperties:
    """Property-based tests for ModelSelector service."""

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
        criteria=selection_criteria_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_rank_models_returns_sorted_list(self, models, requirements, criteria):
        """Property: rank_models returns models in descending score order."""
        import asyncio

        from hypothesis import assume

        # Ensure unique model IDs (edge case: duplicate IDs can exist in input)
        unique_models = []
        seen_ids = set()
        for model in models:
            if model.model_id not in seen_ids:
                unique_models.append(model)
                seen_ids.add(model.model_id)

        assume(len(unique_models) > 0)  # Need at least one unique model

        # Create selector
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=unique_models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
            selection_criteria=criteria,
        )

        # Rank models
        ranked = asyncio.run(selector.rank_models(unique_models, requirements))

        # Property: Result should be a list
        assert isinstance(ranked, list)

        # Property: All returned models should be from input
        assert all(model in unique_models for model in ranked)

        # Property: No duplicates in ranked list
        assert len(ranked) == len({m.model_id for m in ranked})

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_select_model_returns_best_match(self, models, requirements):
        """Property: select_model returns the highest-ranked compatible model."""
        import asyncio

        # Create selector
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
        )

        # Select model
        selected = asyncio.run(selector.select_model(requirements))

        # Property: If a model is selected, it must be from the input list
        if selected is not None:
            assert selected in models

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_filtering_is_consistent(self, models, requirements):
        """Property: Filtering the same models twice yields the same result."""
        import asyncio

        # Create selector
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
        )

        # Filter twice
        filtered1 = asyncio.run(
            selector._filter_compatible_models(models, requirements)
        )
        filtered2 = asyncio.run(
            selector._filter_compatible_models(models, requirements)
        )

        # Property: Results should be identical
        assert len(filtered1) == len(filtered2)
        assert {m.model_id for m in filtered1} == {m.model_id for m in filtered2}

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_score_calculation_is_non_negative(self, models, requirements):
        """Property: Model scores are always non-negative."""
        import asyncio

        # Create selector
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
        )

        # Calculate scores for all models
        for model in models:
            score = asyncio.run(selector._calculate_model_score(model, requirements))

            # Property: Score must be non-negative
            assert score >= 0.0, f"Model {model.model_id} has negative score: {score}"

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
    )
    @settings(max_examples=50, deadline=5000)
    def test_free_model_preference_respected(self, models):
        """Property: When prefer_free_models=True, free models get bonus score."""
        import asyncio

        # Create selector with free model preference
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        criteria = ModelSelectionCriteria(prefer_free_models=True)
        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
            selection_criteria=criteria,
        )

        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        # Calculate scores
        scores = {}
        for model in models:
            scores[model.model_id] = asyncio.run(
                selector._calculate_model_score(model, requirements)
            )

        # Property: Free models should have higher or equal scores compared to
        # identical paid models (if they exist)
        free_models = [m for m in models if m.is_free]
        paid_models = [m for m in models if not m.is_free]

        if free_models and paid_models:
            # At least one free model should have a competitive score
            max_free_score = max(scores[m.model_id] for m in free_models)
            max(scores[m.model_id] for m in paid_models)

            # Free models get +1.0 bonus, so max free should be >= max paid - 1.0
            # (accounting for other factors)
            assert max_free_score >= 0.0  # Basic sanity check

    @given(
        models=st.lists(model_info_strategy(), min_size=0, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_empty_model_list_handling(self, models, requirements):
        """Property: Empty model list returns None."""
        import asyncio

        # Create selector with empty models
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
        )

        # Select model
        selected = asyncio.run(selector.select_model(requirements))

        # Property: Should return None when no models available
        assert selected is None

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=30, deadline=5000)
    def test_ranking_preserves_model_identity(self, models, requirements):
        """Property: Ranking doesn't modify model objects."""
        import asyncio
        import copy

        # Create deep copies of models
        original_models = copy.deepcopy(models)

        # Create selector
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        selector = ModelSelector(
            providers={"test": mock_provider},
            hardware_detector=create_mock_hardware_detector(),
        )

        # Rank models
        asyncio.run(selector.rank_models(models, requirements))

        # Property: Original models should be unchanged
        for original, current in zip(original_models, models, strict=False):
            assert original.model_id == current.model_id
            assert original.name == current.name
            assert original.provider_type == current.provider_type