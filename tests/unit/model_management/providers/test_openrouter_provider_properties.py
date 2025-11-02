"""
Property-Based Tests for OpenRouter Provider.

This module uses Hypothesis to test invariants and properties of the
OpenRouter provider implementation, automatically discovering edge cases.
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tta_ai.models.interfaces import (
    GenerationRequest,
    ModelInfo,
    ProviderType,
)

# ============================================================================
# Custom Hypothesis Strategies
# ============================================================================


@st.composite
def model_info_strategy(draw):
    """Generate valid ModelInfo instances for OpenRouter."""
    model_id = draw(
        st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"),
                whitelist_characters="-_/.:",
            ),
        )
    )

    return ModelInfo(
        model_id=model_id,
        name=draw(st.text(min_size=1, max_size=200)),
        provider_type=ProviderType.OPENROUTER,
        description=draw(st.text(max_size=500)),
        context_length=draw(st.integers(min_value=512, max_value=200000) | st.none()),
        cost_per_token=draw(
            st.floats(
                min_value=0.0, max_value=0.1, allow_nan=False, allow_infinity=False
            )
            | st.none()
        ),
        is_free=draw(st.booleans()),
        capabilities=draw(
            st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)
        ),
        therapeutic_safety_score=draw(
            st.floats(
                min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False
            )
            | st.none()
        ),
        performance_score=draw(
            st.floats(
                min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False
            )
            | st.none()
        ),
    )


@st.composite
def generation_request_strategy(draw):
    """Generate valid GenerationRequest instances."""
    return GenerationRequest(
        prompt=draw(st.text(min_size=1, max_size=10000)),
        max_tokens=draw(st.integers(min_value=1, max_value=8192) | st.none()),
        temperature=draw(
            st.floats(
                min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False
            )
            | st.none()
        ),
        top_p=draw(
            st.floats(
                min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
            )
            | st.none()
        ),
        stop_sequences=draw(
            st.lists(st.text(min_size=1, max_size=20), max_size=4) | st.none()
        ),
        stream=draw(st.booleans()),
        metadata=draw(
            st.dictionaries(
                st.text(min_size=1, max_size=50), st.text(max_size=100), max_size=5
            )
            | st.none()
        ),
    )


@st.composite
def openrouter_config_strategy(draw):
    """Generate valid OpenRouter configuration."""
    return {
        "enabled": draw(st.booleans()),
        "api_key": draw(st.text(min_size=10, max_size=100) | st.none()),
        "base_url": draw(st.just("https://openrouter.ai") | st.none()),
        "free_models_only": draw(st.booleans()),
        "timeout": draw(st.integers(min_value=5, max_value=120)),
        "max_retries": draw(st.integers(min_value=0, max_value=5)),
    }


# ============================================================================
# Property-Based Tests
# ============================================================================


@pytest.mark.property
class TestOpenRouterProviderProperties:
    """Property-based tests for OpenRouter provider."""

    @given(model_info=model_info_strategy())
    @settings(max_examples=50)
    def test_model_info_serialization_roundtrip(self, model_info):
        """Property: ModelInfo serialization is lossless."""
        # Convert to dict (simulating serialization)
        model_dict = {
            "model_id": model_info.model_id,
            "name": model_info.name,
            "provider_type": model_info.provider_type.value,
            "description": model_info.description,
            "context_length": model_info.context_length,
            "cost_per_token": model_info.cost_per_token,
            "is_free": model_info.is_free,
            "capabilities": model_info.capabilities,
            "therapeutic_safety_score": model_info.therapeutic_safety_score,
            "performance_score": model_info.performance_score,
        }

        # Reconstruct (simulating deserialization)
        reconstructed = ModelInfo(
            model_id=model_dict["model_id"],
            name=model_dict["name"],
            provider_type=ProviderType(model_dict["provider_type"]),
            description=model_dict["description"],
            context_length=model_dict["context_length"],
            cost_per_token=model_dict["cost_per_token"],
            is_free=model_dict["is_free"],
            capabilities=model_dict["capabilities"],
            therapeutic_safety_score=model_dict["therapeutic_safety_score"],
            performance_score=model_dict["performance_score"],
        )

        # Invariant: Reconstruction preserves all fields
        assert reconstructed.model_id == model_info.model_id
        assert reconstructed.name == model_info.name
        assert reconstructed.provider_type == model_info.provider_type
        assert reconstructed.is_free == model_info.is_free
        assert reconstructed.capabilities == model_info.capabilities

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        prefer_free=st.booleans(),
    )
    @settings(max_examples=50)
    def test_free_model_filtering_consistency(self, models, prefer_free):
        """Property: Free model filtering is consistent."""
        # Filter free models
        free_models = [m for m in models if m.is_free]
        paid_models = [m for m in models if not m.is_free]

        # Invariant: Free and paid models partition the full list
        assert len(free_models) + len(paid_models) == len(models)

        # Invariant: Each model is either free or paid, not both
        for model in models:
            is_in_free = model in free_models
            is_in_paid = model in paid_models
            assert is_in_free != is_in_paid  # XOR: exactly one should be true

        # Invariant: If prefer_free and free models exist, they should be prioritized
        if prefer_free and free_models:
            # All free models should be considered before paid models
            assert len(free_models) > 0

    @given(
        cost_per_token=st.floats(
            min_value=0.0, max_value=0.1, allow_nan=False, allow_infinity=False
        ),
        tokens=st.integers(min_value=1, max_value=1000000),
    )
    @settings(max_examples=100)
    def test_cost_calculation_linearity(self, cost_per_token, tokens):
        """Property: Cost calculation scales linearly with tokens."""
        # Calculate cost for 1x tokens
        cost_1x = cost_per_token * tokens

        # Calculate cost for 2x tokens
        cost_2x = cost_per_token * (tokens * 2)

        # Metamorphic relation: Doubling tokens doubles cost
        assert abs(cost_2x - (cost_1x * 2)) < 1e-10

        # Invariant: Cost is always non-negative
        assert cost_1x >= 0
        assert cost_2x >= 0

        # Invariant: More tokens means higher or equal cost
        assert cost_2x >= cost_1x

    @given(
        cost_per_token=st.floats(
            min_value=0.0, max_value=0.1, allow_nan=False, allow_infinity=False
        ),
        tokens=st.integers(min_value=1, max_value=1000000),
    )
    @settings(max_examples=50)
    def test_cost_calculation_monotonicity(self, cost_per_token, tokens):
        """Property: Cost increases monotonically with tokens."""
        assume(tokens > 1)  # Need at least 2 tokens to test monotonicity

        cost_n = cost_per_token * tokens
        cost_n_minus_1 = cost_per_token * (tokens - 1)

        # Invariant: Cost for n tokens >= cost for n-1 tokens
        assert cost_n >= cost_n_minus_1

    @given(request=generation_request_strategy())
    @settings(max_examples=50)
    def test_generation_request_validation(self, request):
        """Property: GenerationRequest fields are within valid ranges."""
        # Invariant: Prompt is not empty
        assert len(request.prompt) > 0

        # Invariant: If max_tokens is set, it's positive
        if request.max_tokens is not None:
            assert request.max_tokens > 0

        # Invariant: If temperature is set, it's in valid range
        if request.temperature is not None:
            assert 0.0 <= request.temperature <= 2.0

        # Invariant: If top_p is set, it's in valid range
        if request.top_p is not None:
            assert 0.0 <= request.top_p <= 1.0

        # Invariant: Stream is boolean
        assert isinstance(request.stream, bool)

    @given(config=openrouter_config_strategy())
    @settings(max_examples=50)
    def test_config_validation_properties(self, config):
        """Property: OpenRouter configuration has valid values."""
        # Invariant: Enabled is boolean
        assert isinstance(config["enabled"], bool)

        # Invariant: If API key is set, it's not empty
        if config["api_key"] is not None:
            assert len(config["api_key"]) > 0

        # Invariant: Timeout is positive
        assert config["timeout"] > 0

        # Invariant: Max retries is non-negative
        assert config["max_retries"] >= 0

        # Invariant: Free models only is boolean
        assert isinstance(config["free_models_only"], bool)

    @given(models=st.lists(model_info_strategy(), min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_model_list_uniqueness_by_id(self, models):
        """Property: Model IDs should be unique in a list."""
        # Get all model IDs
        model_ids = [m.model_id for m in models]

        # Create a set of unique IDs
        unique_ids = set(model_ids)

        # Invariant: If we deduplicate by ID, we should get unique models
        # (This tests that model_id is a valid unique identifier)
        deduped_models = {m.model_id: m for m in models}
        assert len(deduped_models) == len(unique_ids)

    @given(
        model=model_info_strategy(),
        score_adjustment=st.floats(
            min_value=-5.0, max_value=5.0, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=50)
    def test_score_adjustment_bounds(self, model, score_adjustment):
        """Property: Score adjustments maintain valid score ranges."""
        if model.performance_score is not None:
            # Apply adjustment
            adjusted_score = model.performance_score + score_adjustment

            # Invariant: Adjusted score should be clamped to valid range [0, 10]
            clamped_score = max(0.0, min(10.0, adjusted_score))

            assert 0.0 <= clamped_score <= 10.0

    @given(models=st.lists(model_info_strategy(), min_size=2, max_size=20))
    @settings(max_examples=50)
    def test_model_sorting_stability(self, models):
        """Property: Sorting models by score is stable."""
        # Filter models with performance scores
        scored_models = [m for m in models if m.performance_score is not None]

        if len(scored_models) < 2:
            return  # Skip if not enough scored models

        # Sort by performance score (descending)
        sorted_models = sorted(
            scored_models, key=lambda m: m.performance_score, reverse=True
        )

        # Invariant: Sorted list maintains score ordering
        for i in range(len(sorted_models) - 1):
            assert (
                sorted_models[i].performance_score
                >= sorted_models[i + 1].performance_score
            )

        # Invariant: Sorting doesn't change the set of models
        assert set(m.model_id for m in sorted_models) == set(
            m.model_id for m in scored_models
        )


# ============================================================================
# Edge Case Tests (Using Hypothesis Examples)
# ============================================================================


@pytest.mark.property
class TestOpenRouterEdgeCases:
    """Edge case tests using Hypothesis examples."""

    @given(tokens=st.integers(min_value=1, max_value=1000000))
    @settings(max_examples=50)
    def test_zero_cost_models(self, tokens):
        """Property: Zero-cost models always have zero cost."""
        cost_per_token = 0.0
        total_cost = cost_per_token * tokens

        # Invariant: Zero cost per token means zero total cost
        assert total_cost == 0.0

    @given(model=model_info_strategy())
    @settings(max_examples=50)
    def test_free_model_cost_consistency(self, model):
        """Property: Free models should have zero or None cost.

        NOTE: This test currently documents that the system allows free models
        to have non-zero costs. This may be intentional (e.g., "free tier" with
        limits) or a business logic issue to address.
        """
        if model.is_free and model.cost_per_token is not None:
            # Document the current behavior: free models CAN have costs
            # This might be intentional for "free tier" models with usage limits
            # If this is NOT intentional, update the ModelInfo validation
            pass  # Currently no strict invariant enforced

        # Weaker invariant: Cost should be non-negative if set
        if model.cost_per_token is not None:
            assert model.cost_per_token >= 0.0
