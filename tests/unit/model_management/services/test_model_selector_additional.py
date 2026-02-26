"""
Additional tests for ModelSelector service to cover uncovered branches.

Focuses on:
- validate_model_compatibility
- _calculate_task_bonus
- _calculate_hardware_compatibility_bonus
- _calculate_performance_history_bonus
- _is_cache_valid / update_performance_metrics / clear_cache
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.components.model_management.interfaces import (
    ModelInfo,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from src.components.model_management.models import (
    ModelSelectionCriteria,
)
from src.components.model_management.services.model_selector import ModelSelector


def _make_model(
    model_id: str = "test/model",
    provider_type: ProviderType = ProviderType.OPENROUTER,
    performance_score: float | None = 7.0,
    therapeutic_safety_score: float | None = 7.5,
    cost_per_token: float | None = 0.0,
    is_free: bool = True,
    context_length: int | None = 8192,
    capabilities: list[str] | None = None,
) -> ModelInfo:
    return ModelInfo(
        model_id=model_id,
        name=model_id,
        provider_type=provider_type,
        performance_score=performance_score,
        therapeutic_safety_score=therapeutic_safety_score,
        cost_per_token=cost_per_token,
        is_free=is_free,
        context_length=context_length,
        capabilities=capabilities or ["chat"],
    )


def _make_requirements(**kwargs) -> ModelRequirements:
    defaults = {
        "task_type": TaskType.GENERAL_CHAT,
        "therapeutic_safety_required": False,
    }
    defaults.update(kwargs)
    return ModelRequirements(**defaults)


@pytest.fixture
def mock_hardware_detector():
    detector = MagicMock()
    detector.estimate_model_requirements = AsyncMock(
        return_value={"ram_gb": 4, "vram_gb": 0}
    )
    detector.detect_system_resources = AsyncMock(
        return_value={
            "total_ram_gb": 16,
            "available_ram_gb": 12,
            "has_gpu": False,
            "total_gpu_memory_gb": 0,
            "gpu_count": 0,
        }
    )
    return detector


@pytest.fixture
def selector(mock_hardware_detector):
    return ModelSelector(
        providers={},
        hardware_detector=mock_hardware_detector,
    )


class TestValidateModelCompatibility:
    async def test_returns_true_for_compatible_model(self, selector):
        model = _make_model()
        req = _make_requirements()
        result = await selector.validate_model_compatibility(model, req)
        assert result is True

    async def test_rejects_model_exceeding_cost(self, selector):
        model = _make_model(cost_per_token=0.01)
        req = _make_requirements(max_cost_per_token=0.001)
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_rejects_model_below_quality(self, selector):
        model = _make_model(performance_score=3.0)
        req = _make_requirements(min_quality_score=7.0)
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_rejects_model_with_insufficient_context(self, selector):
        model = _make_model(context_length=1024)
        req = _make_requirements(context_length_needed=16384)
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_rejects_model_missing_capabilities(self, selector):
        model = _make_model(capabilities=["chat"])
        req = _make_requirements(required_capabilities=["code_generation"])
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_accepts_model_with_all_required_capabilities(self, selector):
        model = _make_model(capabilities=["chat", "code_generation", "analysis"])
        req = _make_requirements(required_capabilities=["chat", "code_generation"])
        result = await selector.validate_model_compatibility(model, req)
        assert result is True

    async def test_therapeutic_safety_unknown_score_openrouter_allowed(self, selector):
        model = _make_model(
            therapeutic_safety_score=None,
            provider_type=ProviderType.OPENROUTER,
        )
        req = _make_requirements(therapeutic_safety_required=True)
        result = await selector.validate_model_compatibility(model, req)
        assert result is True

    async def test_therapeutic_safety_unknown_score_custom_api_allowed(self, selector):
        model = _make_model(
            therapeutic_safety_score=None,
            provider_type=ProviderType.CUSTOM_API,
        )
        req = _make_requirements(therapeutic_safety_required=True)
        result = await selector.validate_model_compatibility(model, req)
        assert result is True

    async def test_therapeutic_safety_unknown_score_local_rejected(self, selector):
        model = _make_model(
            therapeutic_safety_score=None,
            provider_type=ProviderType.LOCAL,
        )
        req = _make_requirements(therapeutic_safety_required=True)
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_therapeutic_safety_below_threshold_rejected(self, selector):
        criteria = ModelSelectionCriteria(min_therapeutic_safety_score=7.0)
        sel = ModelSelector(
            providers={},
            hardware_detector=MagicMock(),
            selection_criteria=criteria,
        )
        model = _make_model(therapeutic_safety_score=5.0)
        req = _make_requirements(therapeutic_safety_required=True)
        result = await sel.validate_model_compatibility(model, req)
        assert result is False

    async def test_latency_constraint_rejects_slow_model(self, selector):
        # Low performance score → high estimated latency
        model = _make_model(performance_score=0.5)
        req = _make_requirements(max_latency_ms=100)
        result = await selector.validate_model_compatibility(model, req)
        assert result is False

    async def test_latency_constraint_accepts_fast_model(self, selector):
        # High performance score → low estimated latency
        model = _make_model(performance_score=9.0)
        req = _make_requirements(max_latency_ms=10000)
        result = await selector.validate_model_compatibility(model, req)
        assert result is True


class TestCalculateTaskBonus:
    async def test_task_bonus_for_chat_model(self, selector):
        model = _make_model(capabilities=["chat", "conversation"])
        bonus = await selector._calculate_task_bonus(model, TaskType.GENERAL_CHAT)
        assert bonus > 0

    async def test_task_bonus_narrative_model_with_matching_caps(self, selector):
        model = _make_model(capabilities=["creative_writing", "storytelling"])
        bonus = await selector._calculate_task_bonus(
            model, TaskType.NARRATIVE_GENERATION
        )
        assert bonus > 0

    async def test_task_bonus_model_with_no_matching_caps(self, selector):
        model = _make_model(capabilities=["unrelated_cap"])
        bonus = await selector._calculate_task_bonus(
            model, TaskType.THERAPEUTIC_RESPONSE
        )
        # Some bonus from model_task_bonuses dict may still apply
        assert bonus >= 0

    async def test_task_bonus_known_model_prefix_gets_extra(self, selector):
        model = _make_model(
            model_id="anthropic/claude-3-haiku", capabilities=[]
        )
        bonus_narrative = await selector._calculate_task_bonus(
            model, TaskType.NARRATIVE_GENERATION
        )
        # Claude gets a 2.0 bonus for narrative
        assert bonus_narrative >= 2.0

    async def test_task_bonus_therapeutic_claude_gets_highest(self, selector):
        model = _make_model(
            model_id="anthropic/claude-3-opus", capabilities=[]
        )
        bonus = await selector._calculate_task_bonus(
            model, TaskType.THERAPEUTIC_RESPONSE
        )
        assert bonus >= 2.5

    async def test_task_bonus_unknown_task_type(self, selector):
        model = _make_model(capabilities=[])
        # WORLD_BUILDING has no model_task_bonuses entry
        bonus = await selector._calculate_task_bonus(model, TaskType.WORLD_BUILDING)
        assert bonus >= 0


class TestCalculateHardwareCompatibilityBonus:
    async def test_bonus_when_plenty_of_ram(self, mock_hardware_detector):
        mock_hardware_detector.detect_system_resources = AsyncMock(
            return_value={
                "total_ram_gb": 64,
                "available_ram_gb": 48,  # >> required 4 * 1.5 = 6
                "has_gpu": False,
                "total_gpu_memory_gb": 0,
            }
        )
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            return_value={"ram_gb": 4, "vram_gb": 0}
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus >= 1.0  # Plenty of RAM bonus

    async def test_bonus_when_sufficient_but_not_plenty_ram(self, mock_hardware_detector):
        mock_hardware_detector.detect_system_resources = AsyncMock(
            return_value={
                "available_ram_gb": 5,  # >= required(4) but < 4*1.5=6
                "has_gpu": False,
                "total_gpu_memory_gb": 0,
            }
        )
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            return_value={"ram_gb": 4, "vram_gb": 0}
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus == 0.5

    async def test_bonus_when_tight_ram(self, mock_hardware_detector):
        mock_hardware_detector.detect_system_resources = AsyncMock(
            return_value={
                "available_ram_gb": 3.5,  # >= required*0.8=3.2 but < required=4
                "has_gpu": False,
                "total_gpu_memory_gb": 0,
            }
        )
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            return_value={"ram_gb": 4, "vram_gb": 0}
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus == 0.1

    async def test_no_bonus_when_insufficient_ram(self, mock_hardware_detector):
        mock_hardware_detector.detect_system_resources = AsyncMock(
            return_value={
                "available_ram_gb": 1,  # << required=4
                "has_gpu": False,
                "total_gpu_memory_gb": 0,
            }
        )
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            return_value={"ram_gb": 4, "vram_gb": 0}
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus == 0.0

    async def test_bonus_for_gpu_when_available(self, mock_hardware_detector):
        mock_hardware_detector.detect_system_resources = AsyncMock(
            return_value={
                "available_ram_gb": 12,
                "has_gpu": True,
                "total_gpu_memory_gb": 8,  # >= vram_gb(4)
            }
        )
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            return_value={"ram_gb": 4, "vram_gb": 4}
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus >= 0.5  # GPU bonus

    async def test_returns_zero_on_hardware_exception(self, mock_hardware_detector):
        mock_hardware_detector.estimate_model_requirements = AsyncMock(
            side_effect=RuntimeError("hw error")
        )
        sel = ModelSelector(providers={}, hardware_detector=mock_hardware_detector)
        model = _make_model()
        bonus = await sel._calculate_hardware_compatibility_bonus(model)
        assert bonus == 0.0


class TestCalculatePerformanceHistoryBonus:
    async def test_returns_zero_when_no_history(self, selector):
        bonus = await selector._calculate_performance_history_bonus("unknown-model")
        assert bonus == 0.0

    async def test_returns_positive_bonus_with_good_metrics(self, selector):
        from src.components.model_management.models import PerformanceMetrics

        metrics = [
            PerformanceMetrics(
                model_id="model-a",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=20,
                total_tokens=50,
                quality_score=9.0,
                success_rate=1.0,
                error_count=0,
            )
        ]
        selector._performance_cache["model-a"] = metrics
        bonus = await selector._calculate_performance_history_bonus("model-a")
        assert bonus > 0

    async def test_returns_zero_when_no_quality_scores(self, selector):
        from src.components.model_management.models import PerformanceMetrics

        metrics = [
            PerformanceMetrics(
                model_id="model-b",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=20,
                total_tokens=50,
                quality_score=None,  # No quality score
                success_rate=1.0,
                error_count=0,
            )
        ]
        selector._performance_cache["model-b"] = metrics
        bonus = await selector._calculate_performance_history_bonus("model-b")
        assert bonus == 0.0

    async def test_reliability_bonus_for_high_success_rate(self, selector):
        from src.components.model_management.models import PerformanceMetrics

        metrics = [
            PerformanceMetrics(
                model_id="model-c",
                timestamp=datetime.now(),
                response_time_ms=100,
                tokens_per_second=20,
                total_tokens=50,
                quality_score=8.0,
                success_rate=1.0,  # Perfect success rate
                error_count=0,
            )
        ]
        selector._performance_cache["model-c"] = metrics
        bonus = await selector._calculate_performance_history_bonus("model-c")
        # Quality bonus + reliability bonus both should be positive
        assert bonus > 0


class TestCacheManagement:
    def test_is_cache_valid_returns_false_when_no_entry(self, selector):
        result = selector._is_cache_valid("unknown-provider")
        assert result is False

    def test_is_cache_valid_returns_true_for_fresh_cache(self, selector):
        selector._last_cache_update["prov"] = datetime.now()
        result = selector._is_cache_valid("prov")
        assert result is True

    def test_is_cache_valid_returns_false_for_stale_cache(self, selector):
        selector._last_cache_update["prov"] = datetime.now() - timedelta(hours=2)
        result = selector._is_cache_valid("prov")
        assert result is False

    def test_update_performance_metrics_adds_to_cache(self, selector):
        from src.components.model_management.models import PerformanceMetrics

        metric = PerformanceMetrics(
            model_id="model-a",
            timestamp=datetime.now(),
            response_time_ms=100,
            tokens_per_second=10,
            total_tokens=50,
            error_count=0,
            success_rate=1.0,
        )
        selector.update_performance_metrics("model-a", metric)
        assert "model-a" in selector._performance_cache
        assert len(selector._performance_cache["model-a"]) == 1

    def test_update_performance_metrics_prunes_old_entries(self, selector):
        from src.components.model_management.models import PerformanceMetrics

        # Add 110 metrics to trigger pruning (limit is 100)
        old_time = datetime.now() - timedelta(hours=25)
        for _i in range(105):
            metric = PerformanceMetrics(
                model_id="model-a",
                timestamp=old_time,
                response_time_ms=100,
                tokens_per_second=10,
                total_tokens=50,
                error_count=0,
                success_rate=1.0,
            )
            selector._performance_cache.setdefault("model-a", []).append(metric)

        # Add one recent metric
        recent_metric = PerformanceMetrics(
            model_id="model-a",
            timestamp=datetime.now(),
            response_time_ms=100,
            tokens_per_second=10,
            total_tokens=50,
            error_count=0,
            success_rate=1.0,
        )
        selector.update_performance_metrics("model-a", recent_metric)
        # Old metrics (>24h) should be pruned
        remaining = selector._performance_cache["model-a"]
        assert all(m.timestamp > datetime.now() - timedelta(hours=24) for m in remaining)

    def test_clear_cache_empties_all_caches(self, selector):
        selector._model_cache["prov"] = [_make_model()]
        selector._last_cache_update["prov"] = datetime.now()
        selector.clear_cache()
        assert len(selector._model_cache) == 0
        assert len(selector._last_cache_update) == 0

    async def test_get_all_available_models_uses_cache_when_valid(self, selector):
        """Cache hit: models are returned from cache without calling provider."""
        cached_model = _make_model("cached-model")
        selector._model_cache["prov"] = [cached_model]
        selector._last_cache_update["prov"] = datetime.now()  # Fresh cache

        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])
        selector.providers["prov"] = mock_provider

        models = await selector._get_all_available_models()
        # Cache was used, provider was NOT called
        mock_provider.get_available_models.assert_not_called()
        assert any(m.model_id == "cached-model" for m in models)
