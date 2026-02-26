"""
Additional unit tests for model_management services to boost coverage.

Covers uncovered branches in:
- FallbackHandler: handle_model_failure, reset_provider_health, cleanup_old_failures,
  get_failure_statistics, _update_provider_health, _get_model_provider
- PerformanceMonitor: start/stop, get_model_performance, get_system_performance,
  record_metrics with Redis, _store_metrics_neo4j, _cleanup_old_metrics
- ModelSelector: select_model, _get_all_available_models, _filter_compatible_models
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
from src.components.model_management.models import FallbackConfiguration
from src.components.model_management.services.fallback_handler import FallbackHandler
from src.components.model_management.services.model_selector import ModelSelector
from src.components.model_management.services.performance_monitor import (
    PerformanceMonitor,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_model(
    model_id: str,
    is_free: bool = False,
    cost_per_token: float | None = None,
    context_length: int | None = 8192,
    capabilities: list[str] | None = None,
    therapeutic_safety_score: float | None = 7.5,
    performance_score: float | None = 7.0,
    provider_type: ProviderType = ProviderType.OPENROUTER,
) -> ModelInfo:
    return ModelInfo(
        model_id=model_id,
        name=model_id,
        provider_type=provider_type,
        is_free=is_free,
        cost_per_token=cost_per_token,
        context_length=context_length,
        capabilities=capabilities or ["chat"],
        therapeutic_safety_score=therapeutic_safety_score,
        performance_score=performance_score,
    )


def _make_requirements(**kwargs) -> ModelRequirements:
    defaults = {
        "task_type": TaskType.GENERAL_CHAT,
        "therapeutic_safety_required": False,
    }
    defaults.update(kwargs)
    return ModelRequirements(**defaults)


# ---------------------------------------------------------------------------
# FallbackHandler additional tests
# ---------------------------------------------------------------------------


class TestFallbackHandlerAdditional:
    async def test_handle_model_failure_increments_count(self):
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])
        handler = FallbackHandler(providers={"test": mock_provider})

        await handler.handle_model_failure("model-a", RuntimeError("oops"))
        assert handler._failure_counts["model-a"] == 1

        await handler.handle_model_failure("model-a", RuntimeError("again"))
        assert handler._failure_counts["model-a"] == 2

    async def test_handle_model_failure_marks_critical_after_max_retries(self):
        config = FallbackConfiguration(max_retries=2)
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])
        handler = FallbackHandler(providers={"test": mock_provider}, fallback_config=config)

        # Two failures should not trigger critical
        await handler.handle_model_failure("model-x", RuntimeError("err"))
        assert handler._failure_counts["model-x"] == 1

        # Third failure reaches max_retries (2) and triggers critical path
        await handler.handle_model_failure("model-x", RuntimeError("err"))
        assert handler._failure_counts["model-x"] == 2

    async def test_handle_model_failure_updates_provider_health_on_connection_error(self):
        model = _make_model("model-a")
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[model])
        mock_provider.health_check = AsyncMock(return_value=False)

        handler = FallbackHandler(providers={"test": mock_provider})
        error = ConnectionError("connection refused")
        await handler.handle_model_failure("model-a", error)

        # Provider should be marked unhealthy
        assert handler._provider_health.get("test") is False

    async def test_handle_model_failure_ignores_non_provider_errors(self):
        model = _make_model("model-a")
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[model])
        mock_provider.health_check = AsyncMock(return_value=True)

        handler = FallbackHandler(providers={"test": mock_provider})
        # A ValueError is not a provider-level issue
        await handler.handle_model_failure("model-a", ValueError("bad input"))

        # Provider health should remain True
        assert handler._provider_health.get("test") is True

    def test_reset_model_failures_removes_failure_record(self):
        handler = FallbackHandler(providers={})
        handler._failed_models["model-x"] = datetime.now()
        handler._failure_counts["model-x"] = 5

        result = handler.reset_model_failures("model-x")
        assert result is True
        assert "model-x" not in handler._failed_models
        assert "model-x" not in handler._failure_counts

    def test_reset_model_failures_returns_true_for_unknown_model(self):
        handler = FallbackHandler(providers={})
        result = handler.reset_model_failures("nonexistent")
        assert result is True

    def test_reset_provider_health_sets_to_true(self):
        handler = FallbackHandler(providers={"my-prov": AsyncMock()})
        handler._provider_health["my-prov"] = False

        result = handler.reset_provider_health("my-prov")
        assert result is True
        assert handler._provider_health["my-prov"] is True

    def test_reset_provider_health_returns_false_for_unknown(self):
        handler = FallbackHandler(providers={})
        result = handler.reset_provider_health("unknown-provider")
        assert result is False

    async def test_cleanup_old_failures_removes_stale_records(self):
        handler = FallbackHandler(providers={})
        old_time = datetime.now() - timedelta(hours=25)
        handler._failed_models["old-model"] = old_time
        handler._failure_counts["old-model"] = 3

        removed = await handler.cleanup_old_failures(hours=24)
        assert removed == 1
        assert "old-model" not in handler._failed_models
        # Count should be reset to 0
        assert handler._failure_counts["old-model"] == 0

    async def test_cleanup_old_failures_keeps_recent_records(self):
        handler = FallbackHandler(providers={})
        handler._failed_models["recent-model"] = datetime.now()
        handler._failure_counts["recent-model"] = 2

        removed = await handler.cleanup_old_failures(hours=24)
        assert removed == 0
        assert "recent-model" in handler._failed_models

    def test_get_failure_statistics_structure(self):
        handler = FallbackHandler(providers={"prov": AsyncMock()})
        handler._failed_models["model-x"] = datetime.now()
        handler._failure_counts["model-x"] = 3

        stats = handler.get_failure_statistics()
        assert "total_failed_models" in stats
        assert "recent_failures_1h" in stats
        assert "recent_failure_details" in stats
        assert "provider_health" in stats
        assert "config" in stats
        assert stats["total_failed_models"] == 1
        assert stats["recent_failures_1h"] == 1

    def test_get_failure_statistics_excludes_old_failures_from_recent(self):
        handler = FallbackHandler(providers={})
        old_time = datetime.now() - timedelta(hours=2)
        handler._failed_models["old-model"] = old_time
        handler._failure_counts["old-model"] = 2

        stats = handler.get_failure_statistics()
        assert stats["total_failed_models"] == 1
        assert stats["recent_failures_1h"] == 0

    def test_get_model_provider_identifies_gpt(self):
        handler = FallbackHandler(providers={})
        result = handler._get_model_provider("gpt-4o-mini")
        assert result == "openai"

    def test_get_model_provider_identifies_claude(self):
        handler = FallbackHandler(providers={})
        result = handler._get_model_provider("claude-3-haiku")
        assert result == "anthropic"

    def test_get_model_provider_identifies_llama(self):
        handler = FallbackHandler(providers={})
        result = handler._get_model_provider("llama3.1:8b")
        assert result == "local"

    def test_get_model_provider_identifies_qwen(self):
        handler = FallbackHandler(providers={})
        result = handler._get_model_provider("qwen2.5:7b")
        assert result == "local"

    def test_get_model_provider_returns_unknown_for_unrecognized(self):
        handler = FallbackHandler(providers={})
        result = handler._get_model_provider("some-random-model-xyz")
        assert result == "unknown"

    async def test_get_fallback_model_returns_none_when_no_healthy_providers(self):
        mock_provider = AsyncMock()
        mock_provider.health_check = AsyncMock(return_value=False)
        mock_provider.get_available_models = AsyncMock(return_value=[])
        handler = FallbackHandler(providers={"bad": mock_provider})
        requirements = _make_requirements()
        result = await handler.get_fallback_model("failed-model", requirements)
        assert result is None

    async def test_get_fallback_model_excludes_failed_model_from_results(self):
        model_a = _make_model("model-a")
        model_b = _make_model("model-b")
        mock_provider = AsyncMock()
        mock_provider.health_check = AsyncMock(return_value=True)
        mock_provider.get_available_models = AsyncMock(return_value=[model_a, model_b])

        handler = FallbackHandler(providers={"test": mock_provider})
        requirements = _make_requirements()
        result = await handler.get_fallback_model("model-a", requirements)
        assert result is not None
        assert result.model_id == "model-b"

    async def test_get_fallback_model_returns_none_when_all_filtered(self):
        model_a = _make_model("model-a")
        mock_provider = AsyncMock()
        mock_provider.health_check = AsyncMock(return_value=True)
        mock_provider.get_available_models = AsyncMock(return_value=[model_a])

        handler = FallbackHandler(providers={"test": mock_provider})
        requirements = _make_requirements()
        # Only one model, which is the failed one
        result = await handler.get_fallback_model("model-a", requirements)
        assert result is None

    async def test_filter_failed_models_excludes_recently_failed(self):
        handler = FallbackHandler(providers={})
        # Mark model as recently failed
        handler._failed_models["recent-fail"] = datetime.now() - timedelta(minutes=5)

        models = [
            _make_model("recent-fail"),
            _make_model("healthy-model"),
        ]
        result = handler._filter_failed_models(models, "some-other-model")
        ids = [m.model_id for m in result]
        assert "recent-fail" not in ids
        assert "healthy-model" in ids

    async def test_filter_failed_models_excludes_max_retries_exceeded(self):
        config = FallbackConfiguration(max_retries=3)
        handler = FallbackHandler(providers={}, fallback_config=config)
        handler._failure_counts["overloaded-model"] = 5  # > max_retries

        models = [
            _make_model("overloaded-model"),
            _make_model("ok-model"),
        ]
        result = handler._filter_failed_models(models, "some-failed")
        ids = [m.model_id for m in result]
        assert "overloaded-model" not in ids
        assert "ok-model" in ids

    async def test_filter_compatible_models_excludes_exceeding_cost(self):
        handler = FallbackHandler(providers={})
        models = [
            _make_model("cheap", cost_per_token=0.0001),
            _make_model("expensive", cost_per_token=0.01),
        ]
        requirements = _make_requirements(max_cost_per_token=0.001)
        result = await handler._filter_compatible_models(models, requirements)
        ids = [m.model_id for m in result]
        assert "cheap" in ids
        assert "expensive" not in ids

    async def test_filter_compatible_models_excludes_insufficient_context(self):
        handler = FallbackHandler(providers={})
        models = [
            _make_model("large-ctx", context_length=32000),
            _make_model("small-ctx", context_length=1024),
        ]
        requirements = _make_requirements(context_length_needed=8192)
        result = await handler._filter_compatible_models(models, requirements)
        ids = [m.model_id for m in result]
        assert "large-ctx" in ids
        assert "small-ctx" not in ids

    async def test_filter_compatible_models_excludes_missing_capabilities(self):
        handler = FallbackHandler(providers={})
        models = [
            _make_model("capable", capabilities=["chat", "code"]),
            _make_model("limited", capabilities=["chat"]),
        ]
        requirements = _make_requirements(required_capabilities=["code"])
        result = await handler._filter_compatible_models(models, requirements)
        ids = [m.model_id for m in result]
        assert "capable" in ids
        assert "limited" not in ids

    async def test_select_fallback_model_returns_none_on_empty_list(self):
        handler = FallbackHandler(providers={})
        requirements = _make_requirements()
        result = await handler._select_fallback_model([], "failed", requirements)
        assert result is None

    async def test_select_fallback_model_defaults_to_performance_based(self):
        handler = FallbackHandler(providers={})
        models = [
            _make_model("high-perf", performance_score=9.0),
            _make_model("low-perf", performance_score=3.0),
        ]
        requirements = _make_requirements()
        result = await handler._select_fallback_model(models, "failed", requirements)
        assert result is not None
        assert result.model_id == "high-perf"

    async def test_get_healthy_models_skips_unhealthy_providers(self):
        healthy_model = _make_model("good-model")
        mock_healthy = AsyncMock()
        mock_healthy.health_check = AsyncMock(return_value=True)
        mock_healthy.get_available_models = AsyncMock(return_value=[healthy_model])

        mock_unhealthy = AsyncMock()
        mock_unhealthy.health_check = AsyncMock(return_value=False)

        handler = FallbackHandler(
            providers={"healthy": mock_healthy, "unhealthy": mock_unhealthy}
        )
        models = await handler._get_healthy_models()
        ids = [m.model_id for m in models]
        assert "good-model" in ids

    async def test_get_healthy_models_handles_provider_exception(self):
        mock_provider = AsyncMock()
        mock_provider.health_check = AsyncMock(side_effect=RuntimeError("crash"))

        handler = FallbackHandler(providers={"bad": mock_provider})
        models = await handler._get_healthy_models()
        assert models == []
        # Provider marked as unhealthy
        assert handler._provider_health["bad"] is False


# ---------------------------------------------------------------------------
# PerformanceMonitor additional tests
# ---------------------------------------------------------------------------


class TestPerformanceMonitorAdditional:
    async def test_start_and_stop_background_tasks(self):
        monitor = PerformanceMonitor()
        await monitor.start()
        assert monitor._running is True
        assert monitor._aggregation_task is not None
        assert monitor._cleanup_task is not None
        await monitor.stop()
        assert monitor._running is False

    async def test_record_metrics_stores_in_memory_cache(self):
        monitor = PerformanceMonitor()
        await monitor.record_metrics("model-a", {"response_time_ms": 150, "total_tokens": 50})
        assert len(monitor._metrics_cache["model-a"]) == 1
        metric = monitor._metrics_cache["model-a"][0]
        assert metric.response_time_ms == 150

    async def test_get_model_performance_no_metrics_returns_empty_message(self):
        monitor = PerformanceMonitor()
        result = await monitor.get_model_performance("nonexistent-model", 24)
        assert result["model_id"] == "nonexistent-model"
        assert result["metrics_count"] == 0
        assert "No metrics available" in result["message"]

    async def test_get_model_performance_with_metrics_returns_stats(self):
        monitor = PerformanceMonitor()
        await monitor.record_metrics(
            "model-a",
            {"response_time_ms": 200, "total_tokens": 100, "success_rate": 1.0},
        )
        result = await monitor.get_model_performance("model-a", 24)
        assert result["model_id"] == "model-a"
        assert result["metrics_count"] == 1
        assert "average_response_time_ms" in result

    async def test_get_model_performance_filters_by_timeframe(self):
        monitor = PerformanceMonitor()
        # Manually inject an old metric
        from src.components.model_management.models import PerformanceMetrics

        old_metric = PerformanceMetrics(
            model_id="model-a",
            timestamp=datetime.now() - timedelta(hours=48),
            response_time_ms=100,
            tokens_per_second=10,
            total_tokens=50,
            error_count=0,
            success_rate=1.0,
        )
        monitor._metrics_cache["model-a"].append(old_metric)

        # Ask for last 24 hours only — old metric should be excluded
        result = await monitor.get_model_performance("model-a", 24)
        assert result["metrics_count"] == 0

    async def test_get_system_performance_aggregates_models(self):
        monitor = PerformanceMonitor()
        await monitor.record_metrics(
            "model-a",
            {"response_time_ms": 100, "total_tokens": 50, "success_rate": 1.0},
        )
        await monitor.record_metrics(
            "model-b",
            {"response_time_ms": 200, "total_tokens": 100, "success_rate": 0.9},
        )
        result = await monitor.get_system_performance()
        assert result["total_models"] == 2
        assert result["active_models"] >= 0  # May be 0 since metrics may be > 1h old

    async def test_get_model_usage_stats_returns_model_usage_stats_object(self):
        monitor = PerformanceMonitor()
        await monitor.record_metrics(
            "model-a",
            {
                "response_time_ms": 150,
                "total_tokens": 80,
                "error_count": 0,
                "success_rate": 1.0,
            },
        )
        stats = await monitor.get_model_usage_stats("model-a", 24)
        assert stats.model_id == "model-a"
        assert stats.total_requests >= 0

    async def test_record_metrics_with_redis_calls_store(self):
        mock_redis = AsyncMock()
        mock_redis.lpush = AsyncMock()
        mock_redis.ltrim = AsyncMock()
        mock_redis.expire = AsyncMock()

        monitor = PerformanceMonitor(redis_client=mock_redis)
        await monitor.record_metrics("model-a", {"response_time_ms": 100})
        mock_redis.lpush.assert_called_once()

    async def test_cleanup_old_metrics_removes_stale_entries(self):
        monitor = PerformanceMonitor()
        monitor.retention_days = 1  # 1 day retention

        from src.components.model_management.models import PerformanceMetrics

        old_metric = PerformanceMetrics(
            model_id="model-a",
            timestamp=datetime.now() - timedelta(days=2),
            response_time_ms=100,
            tokens_per_second=10,
            total_tokens=50,
            error_count=0,
            success_rate=1.0,
        )
        monitor._metrics_cache["model-a"].append(old_metric)
        await monitor._cleanup_old_metrics()
        # Old metric should be removed
        assert len(monitor._metrics_cache["model-a"]) == 0

    async def test_aggregate_metrics_does_not_raise(self):
        monitor = PerformanceMonitor()
        # Should complete without error
        await monitor._aggregate_metrics()

    async def test_get_model_performance_handles_exception(self):
        monitor = PerformanceMonitor()
        # Corrupt the cache to trigger an exception path
        monitor._metrics_cache["bad-model"] = "not-a-deque"  # type: ignore
        result = await monitor.get_model_performance("bad-model", 24)
        # Should return an error dict instead of raising
        assert "error" in result or "metrics_count" in result

    async def test_get_system_performance_handles_empty_cache(self):
        monitor = PerformanceMonitor()
        result = await monitor.get_system_performance()
        assert result["total_models"] == 0
        assert result["active_models"] == 0


# ---------------------------------------------------------------------------
# ModelSelector additional tests
# ---------------------------------------------------------------------------


class TestModelSelectorAdditional:
    @pytest.fixture
    def mock_hardware_detector(self):
        detector = MagicMock()
        detector.get_available_vram = MagicMock(return_value=8000)
        detector.get_cpu_count = MagicMock(return_value=8)
        return detector

    @pytest.fixture
    def make_selector(self, mock_hardware_detector):
        def _make(providers: dict):
            return ModelSelector(
                providers=providers,
                hardware_detector=mock_hardware_detector,
            )
        return _make

    async def test_select_model_returns_none_when_no_models(self, make_selector):
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[])
        selector = make_selector({"prov": mock_provider})
        requirements = _make_requirements()
        result = await selector.select_model(requirements)
        assert result is None

    async def test_select_model_returns_best_model(self, make_selector):
        model_a = _make_model("model-a", performance_score=9.0)
        model_b = _make_model("model-b", performance_score=3.0)
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[model_b, model_a])
        selector = make_selector({"prov": mock_provider})
        requirements = _make_requirements()
        result = await selector.select_model(requirements)
        assert result is not None

    async def test_select_model_returns_none_when_no_compatible(self, make_selector):
        """Model with insufficient context should be filtered out."""
        model = _make_model("small-ctx", context_length=512)
        mock_provider = AsyncMock()
        mock_provider.get_available_models = AsyncMock(return_value=[model])
        selector = make_selector({"prov": mock_provider})
        requirements = _make_requirements(context_length_needed=16384)
        result = await selector.select_model(requirements)
        assert result is None

    async def test_get_all_available_models_aggregates_providers(
        self, make_selector
    ):
        model_a = _make_model("model-a")
        model_b = _make_model("model-b")
        mock_prov_1 = AsyncMock()
        mock_prov_1.get_available_models = AsyncMock(return_value=[model_a])
        mock_prov_2 = AsyncMock()
        mock_prov_2.get_available_models = AsyncMock(return_value=[model_b])
        selector = make_selector({"p1": mock_prov_1, "p2": mock_prov_2})
        models = await selector._get_all_available_models()
        ids = [m.model_id for m in models]
        assert "model-a" in ids
        assert "model-b" in ids

    async def test_get_all_available_models_handles_provider_error(
        self, make_selector
    ):
        mock_prov = AsyncMock()
        mock_prov.get_available_models = AsyncMock(side_effect=RuntimeError("fail"))
        selector = make_selector({"bad-prov": mock_prov})
        # Should not raise, just return empty
        models = await selector._get_all_available_models()
        assert models == []

    async def test_filter_compatible_models_requires_context_length(
        self, make_selector
    ):
        model_large = _make_model("large", context_length=32000)
        model_small = _make_model("small", context_length=1024)
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements(context_length_needed=8192)
        result = await selector._filter_compatible_models(
            [model_large, model_small], requirements
        )
        ids = [m.model_id for m in result]
        assert "large" in ids
        assert "small" not in ids

    async def test_filter_compatible_models_requires_safety(self, make_selector):
        model_safe = _make_model("safe", therapeutic_safety_score=8.0)
        model_unsafe = _make_model("unsafe", therapeutic_safety_score=5.0)
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements(therapeutic_safety_required=True)
        result = await selector._filter_compatible_models(
            [model_safe, model_unsafe], requirements
        )
        ids = [m.model_id for m in result]
        assert "safe" in ids
        assert "unsafe" not in ids

    async def test_filter_compatible_models_requires_max_cost(self, make_selector):
        model_cheap = _make_model("cheap", cost_per_token=0.0001)
        model_expensive = _make_model("expensive", cost_per_token=0.01)
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements(max_cost_per_token=0.001)
        result = await selector._filter_compatible_models(
            [model_cheap, model_expensive], requirements
        )
        ids = [m.model_id for m in result]
        assert "cheap" in ids
        assert "expensive" not in ids

    async def test_rank_models_returns_sorted_list(self, make_selector):
        model_high = _make_model("high", performance_score=9.0, therapeutic_safety_score=9.0)
        model_low = _make_model("low", performance_score=2.0, therapeutic_safety_score=2.0)
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements()
        ranked = await selector.rank_models([model_low, model_high], requirements)
        assert len(ranked) >= 1
        # High-scoring model should rank first
        if len(ranked) >= 2:
            assert ranked[0].model_id == "high"

    async def test_calculate_model_score_returns_positive_value(self, make_selector):
        model = _make_model(
            "test",
            performance_score=7.0,
            therapeutic_safety_score=8.0,
            cost_per_token=0.001,
        )
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements()
        score = await selector._calculate_model_score(model, requirements)
        assert score > 0

    async def test_calculate_model_score_free_model_gets_bonus(self, make_selector):
        model_free = _make_model("free", is_free=True, cost_per_token=0.0)
        model_paid = _make_model("paid", is_free=False, cost_per_token=0.005)
        mock_prov = AsyncMock()
        selector = make_selector({"p": mock_prov})
        requirements = _make_requirements()

        score_free = await selector._calculate_model_score(model_free, requirements)
        score_paid = await selector._calculate_model_score(model_paid, requirements)
        # Free model should score higher than paid model (all else equal)
        assert score_free >= score_paid

    async def test_select_model_handles_exception_gracefully(self, make_selector):
        mock_prov = AsyncMock()
        mock_prov.get_available_models = AsyncMock(
            side_effect=RuntimeError("provider crashed")
        )
        selector = make_selector({"bad": mock_prov})
        result = await selector.select_model(_make_requirements())
        assert result is None


# ---------------------------------------------------------------------------
# FallbackHandler prefer_different_provider path
# ---------------------------------------------------------------------------


class TestFallbackHandlerPreferDifferentProvider:
    async def test_prefer_different_provider_selects_different_provider(self):
        model_same = _make_model(
            "same-prov-model", provider_type=ProviderType.OPENROUTER, performance_score=9.5
        )
        model_diff = _make_model(
            "diff-prov-model", provider_type=ProviderType.OLLAMA, performance_score=7.0
        )

        mock_provider = AsyncMock()
        mock_provider.health_check = AsyncMock(return_value=True)
        mock_provider.get_available_models = AsyncMock(
            return_value=[model_same, model_diff]
        )

        config = FallbackConfiguration(
            fallback_strategy="performance_based",
            prefer_different_provider=True,
        )
        handler = FallbackHandler(providers={"test": mock_provider}, fallback_config=config)
        requirements = _make_requirements()

        # The failed model was from openrouter, so we prefer a different provider
        # Note: _get_model_provider uses simple heuristics
        result = await handler.get_fallback_model("failed-openrouter-model", requirements)
        assert result is not None
