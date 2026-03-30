"""Unit tests for ModelSelector timeout migration (#304).

Verifies that ModelSelector.select_model() uses TimeoutPrimitive with
WorkflowContext, that the timeout is driven by selection_timeout_seconds,
and that timeouts degrade gracefully to None (default model selection).
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("tta_ai")

from tta_ai.models.models import ModelSelectionCriteria  # noqa: E402
from tta_ai.models.services.model_selector import (  # noqa: E402
    ModelSelector,
    _ModelSelectCall,
    _ModelSelectFallback,
)

try:
    from ttadev.primitives import WorkflowContext
except ImportError:
    try:
        from tta_dev_primitives import WorkflowContext  # type: ignore[no-redef]
    except ImportError:
        pytest.skip("ttadev.primitives not available", allow_module_level=True)

from tta_ai.models import ModelInfo, ModelRequirements, ProviderType, TaskType  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_selector(timeout_seconds: float = 30.0) -> ModelSelector:
    provider = AsyncMock()
    provider.provider_type = ProviderType.OPENROUTER
    detector = MagicMock()
    criteria = ModelSelectionCriteria(selection_timeout_seconds=timeout_seconds)
    return ModelSelector(
        providers={"test": provider},
        hardware_detector=detector,
        selection_criteria=criteria,
    )


def _make_model(model_id: str = "test/model-1") -> ModelInfo:
    return ModelInfo(
        model_id=model_id,
        name="Test Model",
        provider_type=ProviderType.OPENROUTER,
        context_length=4096,
        capabilities=["chat"],
    )


def _make_requirements() -> ModelRequirements:
    return ModelRequirements(task_type=TaskType.NARRATIVE_GENERATION)


# ---------------------------------------------------------------------------
# ModelSelectionCriteria: selection_timeout_seconds field
# ---------------------------------------------------------------------------


class TestModelSelectionCriteriaTimeout:
    def test_default_timeout_is_30s(self) -> None:
        criteria = ModelSelectionCriteria()
        assert criteria.selection_timeout_seconds == 30.0

    def test_custom_timeout_stored(self) -> None:
        criteria = ModelSelectionCriteria(selection_timeout_seconds=10.0)
        assert criteria.selection_timeout_seconds == 10.0

    def test_timeout_is_numeric(self) -> None:
        """selection_timeout_seconds accepts int or float (plain dataclass)."""
        criteria = ModelSelectionCriteria(selection_timeout_seconds=5)
        assert criteria.selection_timeout_seconds == 5


# ---------------------------------------------------------------------------
# _ModelSelectCall primitive
# ---------------------------------------------------------------------------


class TestModelSelectCall:
    @pytest.mark.asyncio
    async def test_execute_calls_run_selection(self) -> None:
        selector = _make_selector()
        expected_model = _make_model()
        selector._run_selection = AsyncMock(return_value=expected_model)  # type: ignore[method-assign]
        requirements = _make_requirements()

        ctx = WorkflowContext(workflow_id="sel-001")
        primitive = _ModelSelectCall()
        result = await primitive.execute(
            {"selector": selector, "requirements": requirements}, ctx
        )

        selector._run_selection.assert_awaited_once_with(requirements)
        assert result["model"] is expected_model

    @pytest.mark.asyncio
    async def test_execute_returns_none_when_no_model(self) -> None:
        selector = _make_selector()
        selector._run_selection = AsyncMock(return_value=None)  # type: ignore[method-assign]

        ctx = WorkflowContext(workflow_id="s")
        primitive = _ModelSelectCall()
        result = await primitive.execute(
            {"selector": selector, "requirements": _make_requirements()}, ctx
        )
        assert result["model"] is None

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self) -> None:
        selector = _make_selector()
        selector._run_selection = AsyncMock(side_effect=RuntimeError("db error"))  # type: ignore[method-assign]

        ctx = WorkflowContext(workflow_id="s")
        primitive = _ModelSelectCall()
        with pytest.raises(RuntimeError, match="db error"):
            await primitive.execute(
                {"selector": selector, "requirements": _make_requirements()}, ctx
            )


# ---------------------------------------------------------------------------
# _ModelSelectFallback primitive
# ---------------------------------------------------------------------------


class TestModelSelectFallback:
    @pytest.mark.asyncio
    async def test_returns_none_model(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        primitive = _ModelSelectFallback()
        result = await primitive.execute({}, ctx)
        assert result["model"] is None

    @pytest.mark.asyncio
    async def test_always_returns_dict_with_model_key(self) -> None:
        ctx = WorkflowContext(workflow_id="s")
        result = await _ModelSelectFallback().execute({"any": "data"}, ctx)
        assert "model" in result


# ---------------------------------------------------------------------------
# ModelSelector.select_model — happy path
# ---------------------------------------------------------------------------


class TestModelSelectorSelectModelTimeout:
    @pytest.mark.asyncio
    async def test_returns_model_on_success(self) -> None:
        selector = _make_selector()
        model = _make_model()
        selector._run_selection = AsyncMock(return_value=model)  # type: ignore[method-assign]

        result = await selector.select_model(_make_requirements())
        assert result is model

    @pytest.mark.asyncio
    async def test_returns_none_when_no_models(self) -> None:
        selector = _make_selector()
        selector._run_selection = AsyncMock(return_value=None)  # type: ignore[method-assign]

        result = await selector.select_model(_make_requirements())
        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_value_from_criteria(self) -> None:
        """TimeoutPrimitive receives timeout_seconds from criteria."""
        selector = _make_selector(timeout_seconds=5.0)
        assert selector.selection_criteria.selection_timeout_seconds == 5.0

        selector._run_selection = AsyncMock(return_value=_make_model())  # type: ignore[method-assign]
        result = await selector.select_model(_make_requirements())
        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_on_timeout(self) -> None:
        """When selection times out, fallback returns None."""
        selector = _make_selector(timeout_seconds=0.01)  # 10ms — will timeout

        async def slow_selection(req: Any) -> ModelInfo:
            await asyncio.sleep(1.0)  # far longer than timeout
            return _make_model()

        selector._run_selection = slow_selection  # type: ignore[method-assign]
        result = await selector.select_model(_make_requirements())
        assert result is None

    @pytest.mark.asyncio
    async def test_exception_in_selection_returns_none(self) -> None:
        """Unhandled exception in _run_selection → select_model returns None."""
        selector = _make_selector()
        selector._run_selection = AsyncMock(side_effect=RuntimeError("crash"))  # type: ignore[method-assign]

        result = await selector.select_model(_make_requirements())
        assert result is None

    @pytest.mark.asyncio
    async def test_select_model_uses_timeout_primitive(self) -> None:
        """TimeoutPrimitive.execute is called with correct timeout."""
        try:
            from ttadev.primitives import TimeoutPrimitive
        except ImportError:
            from tta_dev_primitives import TimeoutPrimitive  # type: ignore[no-redef]

        selector = _make_selector(timeout_seconds=15.0)
        model = _make_model()
        selector._run_selection = AsyncMock(return_value=model)  # type: ignore[method-assign]

        captured: list[float] = []
        original_init = TimeoutPrimitive.__init__

        def patched_init(
            self_tp: Any, primitive: Any, timeout_seconds: float, **kwargs: Any
        ) -> None:
            captured.append(timeout_seconds)
            original_init(self_tp, primitive, timeout_seconds, **kwargs)

        with patch.object(TimeoutPrimitive, "__init__", patched_init):
            await selector.select_model(_make_requirements())

        assert captured == [15.0]


# ---------------------------------------------------------------------------
# _run_selection — integration with full pipeline
# ---------------------------------------------------------------------------


class TestRunSelectionPipeline:
    @pytest.mark.asyncio
    async def test_run_selection_returns_best_model(self) -> None:
        """_run_selection performs full provider → filter → rank pipeline."""
        model = _make_model("anthropic/claude-3")
        provider = AsyncMock()
        provider.get_available_models = AsyncMock(return_value=[model])
        detector = MagicMock()
        detector.estimate_model_requirements = AsyncMock(return_value={"ram_gb": 1})
        detector.detect_system_resources = AsyncMock(
            return_value={"available_ram_gb": 16, "has_gpu": False}
        )
        selector = ModelSelector(
            providers={"openrouter": provider},
            hardware_detector=detector,
        )

        result = await selector._run_selection(_make_requirements())
        assert result is model

    @pytest.mark.asyncio
    async def test_run_selection_returns_none_when_no_providers(self) -> None:
        selector = ModelSelector(
            providers={},
            hardware_detector=MagicMock(),
        )
        result = await selector._run_selection(_make_requirements())
        assert result is None
