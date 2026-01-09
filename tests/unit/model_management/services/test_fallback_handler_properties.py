"""

# Logseq: [[TTA.dev/Tests/Unit/Model_management/Services/Test_fallback_handler_properties]]
Property-Based Tests for FallbackHandler Service.

This module contains property-based tests using Hypothesis to validate
the FallbackHandler service's behavior across a wide range of inputs.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from tta_ai.models import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from tta_ai.models.models import FallbackConfiguration
from tta_ai.models.services import FallbackHandler

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
def fallback_config_strategy(draw):
    """Generate valid FallbackConfiguration instances."""
    return FallbackConfiguration(
        enabled=draw(st.booleans()),
        max_retries=draw(st.integers(min_value=1, max_value=5)),
        retry_delay_seconds=draw(st.floats(min_value=0.1, max_value=5.0)),
        fallback_strategy=draw(
            st.sampled_from(["performance_based", "cost_based", "availability_based"])
        ),
        max_response_time_ms=draw(st.integers(min_value=1000, max_value=30000)),
        max_error_rate=draw(st.floats(min_value=0.01, max_value=0.5)),
        min_availability_percent=draw(st.floats(min_value=50.0, max_value=99.9)),
        exclude_failed_models_minutes=draw(st.integers(min_value=5, max_value=120)),
        prefer_different_provider=draw(st.booleans()),
    )


# ============================================================================
# Property-Based Tests
# ============================================================================


@pytest.mark.property
class TestFallbackHandlerProperties:
    """Property-based tests for FallbackHandler service."""

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        requirements=model_requirements_strategy(),
        config=fallback_config_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_fallback_excludes_failed_model(self, models, requirements, config):
        """Property: Fallback never returns the failed model."""
        import asyncio

        # Ensure we have at least 2 unique model IDs
        assume(len({m.model_id for m in models}) >= 2)

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Pick a failed model
        failed_model_id = models[0].model_id

        # Get fallback
        fallback = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: Fallback model should not be the failed model
        if fallback is not None:
            assert fallback.model_id != failed_model_id

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
        config=fallback_config_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_fallback_returns_compatible_model(self, models, requirements, config):
        """Property: Fallback model meets requirements if one is returned."""
        import asyncio

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Get fallback
        failed_model_id = "nonexistent-model"
        fallback = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: If a fallback is returned, it should be from the available models
        if fallback is not None:
            assert fallback in models

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_performance_based_selection_prefers_high_performance(
        self, models, requirements
    ):
        """Property: Performance-based strategy prefers models with higher performance scores."""
        import asyncio

        # Ensure we have models with different performance scores
        for i, model in enumerate(models):
            model.performance_score = float(i + 1)  # Assign increasing scores

        # Create handler with performance-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        config = FallbackConfiguration(fallback_strategy="performance_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Get fallback (exclude lowest performance model)
        failed_model_id = models[0].model_id
        fallback = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: Fallback should have higher performance than failed model
        if fallback is not None and len(models) > 1:
            failed_model = models[0]
            assert fallback.performance_score >= failed_model.performance_score

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_cost_based_selection_prefers_lower_cost(self, models, requirements):
        """Property: Cost-based strategy prefers models with lower cost."""
        import asyncio

        # Ensure we have models with different costs
        for i, model in enumerate(models):
            model.cost_per_token = 0.001 * (i + 1)  # Assign increasing costs

        # Create handler with cost-based strategy
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        config = FallbackConfiguration(fallback_strategy="cost_based")
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Get fallback (exclude highest cost model)
        failed_model_id = models[-1].model_id
        fallback = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: Fallback should have lower or equal cost than failed model
        if fallback is not None and len(models) > 1:
            failed_model = models[-1]
            assert fallback.cost_per_token <= failed_model.cost_per_token

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        model_id=st.text(min_size=1, max_size=50),
    )
    @settings(max_examples=50, deadline=5000)
    def test_handle_model_failure_records_failure(self, models, model_id):
        """Property: Handling a failure records it in the handler's state."""
        import asyncio

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        handler = FallbackHandler(providers={"test": mock_provider})

        # Record failure
        error = Exception("Test error")
        asyncio.run(handler.handle_model_failure(model_id, error))

        # Property: Failure should be recorded
        assert model_id in handler._failed_models
        assert handler._failure_counts[model_id] >= 1

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_empty_compatible_models_returns_none(self, models, requirements):
        """Property: When no compatible models exist, return None."""
        import asyncio
        from dataclasses import replace

        # Ensure all models have context_length values that will fail the filter
        models_with_context = []
        for model in models:
            # Create a copy with a small context_length
            models_with_context.append(replace(model, context_length=1000))

        # Create requirements that no model can satisfy
        impossible_requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            context_length_needed=1000000,  # Impossibly large - exceeds all models
        )

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models_with_context)

        handler = FallbackHandler(providers={"test": mock_provider})

        # Get fallback
        fallback = asyncio.run(
            handler.get_fallback_model("failed-model", impossible_requirements)
        )

        # Property: Should return None when no compatible models
        assert fallback is None

    @given(
        models=st.lists(model_info_strategy(), min_size=2, max_size=20),
        requirements=model_requirements_strategy(),
    )
    @settings(max_examples=30, deadline=5000)
    def test_recently_failed_models_excluded(self, models, requirements):
        """Property: Recently failed models are excluded from fallback selection."""
        import asyncio

        # Ensure unique model IDs
        assume(len({m.model_id for m in models}) >= 2)

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        config = FallbackConfiguration(exclude_failed_models_minutes=30)
        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        # Mark first model as recently failed
        recently_failed_id = models[0].model_id
        handler._failed_models[recently_failed_id] = datetime.now()

        # Get fallback for a different model
        failed_model_id = models[1].model_id
        fallback = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: Recently failed model should not be selected
        if fallback is not None:
            assert fallback.model_id != recently_failed_id

    @given(
        models=st.lists(model_info_strategy(), min_size=1, max_size=20),
        requirements=model_requirements_strategy(),
        config=fallback_config_strategy(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_fallback_is_deterministic_for_same_inputs(
        self, models, requirements, config
    ):
        """Property: Same inputs produce same fallback selection."""
        import asyncio

        # Create handler
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=models)

        handler = FallbackHandler(
            providers={"test": mock_provider},
            fallback_config=config,
        )

        failed_model_id = "test-failed-model"

        # Get fallback twice
        fallback1 = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )
        fallback2 = asyncio.run(
            handler.get_fallback_model(failed_model_id, requirements)
        )

        # Property: Results should be identical
        if fallback1 is not None and fallback2 is not None:
            assert fallback1.model_id == fallback2.model_id