"""Unit tests for the UniversalLLMPrimitive integration in ModelManagementComponent.

Tests verify:
- guarded import availability flag
- _build_universal_llm() mapping logic
- _generate_via_universal_llm() response bridging
- generate_text() fast-path routing
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_component(config_dict: dict | None = None):
    """Return a minimal ModelManagementComponent without real providers."""
    from tta_ai.models.model_management_component import ModelManagementComponent

    cfg = MagicMock()
    cfg.get = lambda key, default=None: (config_dict or {}).get(key, default)
    comp = ModelManagementComponent.__new__(ModelManagementComponent)
    comp.config = cfg
    # We build model_config manually to avoid side-effects
    comp.model_config = comp._load_model_config()
    return comp


# ---------------------------------------------------------------------------
# Guarded import
# ---------------------------------------------------------------------------


class TestGuardedImport:
    def test_flag_type_is_bool(self):
        import tta_ai.models.model_management_component as m

        assert isinstance(m._UNIVERSAL_LLM_AVAILABLE, bool)


# ---------------------------------------------------------------------------
# _build_universal_llm
# ---------------------------------------------------------------------------


class TestBuildUniversalLlm:
    def test_returns_none_when_not_available(self):
        with patch(
            "tta_ai.models.model_management_component._UNIVERSAL_LLM_AVAILABLE",
            False,
        ):
            comp = _make_component()
            assert comp._build_universal_llm() is None

    def test_returns_primitive_when_available(self):
        """When available flag is True and provider configured, constructs UniversalLLMPrimitive."""
        comp = _make_component()
        # Provide a mock provider config so the provider-guard passes
        comp.model_config.providers = {"openrouter": MagicMock()}
        with patch(
            "tta_ai.models.model_management_component._UNIVERSAL_LLM_AVAILABLE",
            True,
        ), patch(
            "tta_ai.models.model_management_component.UniversalLLMPrimitive",
            autospec=True,
            create=True,
        ) as mock_primitive:
            primitive_instance = mock_primitive.return_value
            result = comp._build_universal_llm()

        assert result is primitive_instance
        mock_primitive.assert_called_once()

    def test_returns_none_when_provider_not_configured(self):
        """Returns None when the default provider has no configuration entry."""
        comp = _make_component()
        # providers dict is empty by default from _load_model_config fallback
        with patch(
            "tta_ai.models.model_management_component._UNIVERSAL_LLM_AVAILABLE",
            True,
        ):
            result = comp._build_universal_llm()
        assert result is None

    def test_returns_none_when_provider_disabled(self):
        """Returns None when the provider config exists but is disabled."""
        comp = _make_component()
        disabled_cfg = MagicMock()
        disabled_cfg.enabled = False
        comp.model_config.providers = {"openrouter": disabled_cfg}
        with patch(
            "tta_ai.models.model_management_component._UNIVERSAL_LLM_AVAILABLE",
            True,
        ):
            result = comp._build_universal_llm()
        assert result is None

    def test_returns_none_on_build_error(self):
        """Returns None and logs a warning when construction raises."""
        comp = _make_component()
        comp.model_config.providers = {"openrouter": MagicMock()}
        with patch(
            "tta_ai.models.model_management_component._UNIVERSAL_LLM_AVAILABLE",
            True,
        ), patch(
            "tta_ai.models.model_management_component.UniversalLLMPrimitive",
            side_effect=RuntimeError("bad config"),
            create=True,
        ):
            result = comp._build_universal_llm()
        assert result is None


# ---------------------------------------------------------------------------
# _generate_via_universal_llm
# ---------------------------------------------------------------------------


class TestGenerateViaUniversalLlm:
    @pytest.mark.asyncio
    async def test_returns_none_when_primitive_is_none(self):
        comp = _make_component()
        comp._universal_llm = None
        result = await comp._generate_via_universal_llm("hello")
        assert result is None

    @pytest.mark.asyncio
    async def test_bridges_response_fields(self):
        from tta_ai.models.interfaces import GenerationResponse

        fake_response = MagicMock()
        fake_response.content = "hello world"
        fake_response.model = "openai/gpt-4.1-mini"
        fake_response.usage = {"total_tokens": 12}

        mock_primitive = MagicMock()
        mock_primitive.execute = AsyncMock(return_value=fake_response)

        comp = _make_component()
        comp._universal_llm = mock_primitive

        result = await comp._generate_via_universal_llm("test prompt", temperature=0.5)

        assert isinstance(result, GenerationResponse)
        assert result.text == "hello world"
        assert result.model_id == "openai/gpt-4.1-mini"
        assert result.usage == {"total_tokens": 12}
        assert result.metadata is not None
        assert result.metadata.get("provider") == "openrouter"

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self):
        mock_primitive = MagicMock()
        mock_primitive.execute = AsyncMock(side_effect=RuntimeError("network error"))

        comp = _make_component()
        comp._universal_llm = mock_primitive

        result = await comp._generate_via_universal_llm("test prompt")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolves_model_id_by_task_type(self):
        """Picks the model whose supported_tasks includes the requested task_type."""
        from tta_ai.models.interfaces import GenerationResponse

        fake_response = MagicMock()
        fake_response.content = "ok"
        fake_response.model = "openai/story-model"
        fake_response.usage = {}

        story_model = MagicMock()
        story_model.model_id = "openai/story-model"
        story_model.supported_tasks = ["story_generation"]

        chat_model = MagicMock()
        chat_model.model_id = "openai/chat-model"
        chat_model.supported_tasks = ["general_chat"]

        comp = _make_component()
        comp.model_config.models = {"story": story_model, "chat": chat_model}
        comp._universal_llm = MagicMock()
        comp._universal_llm.execute = AsyncMock(return_value=fake_response)

        result = await comp._generate_via_universal_llm(
            "tell a story", task_type="story_generation"
        )

        assert isinstance(result, GenerationResponse)
        assert result.model_id == "openai/story-model"

    @pytest.mark.asyncio
    async def test_falls_back_to_first_model_when_no_task_match(self):
        """Falls back to first model in config dict when no task_type match."""
        from tta_ai.models.interfaces import GenerationResponse

        fake_response = MagicMock()
        fake_response.content = "ok"
        fake_response.model = "openai/first-model"
        fake_response.usage = {}

        first_model = MagicMock()
        first_model.model_id = "openai/first-model"
        first_model.supported_tasks = ["summarization"]

        comp = _make_component()
        comp.model_config.models = {"first": first_model}
        comp._universal_llm = MagicMock()
        comp._universal_llm.execute = AsyncMock(return_value=fake_response)

        result = await comp._generate_via_universal_llm(
            "chat message", task_type="general_chat"  # no match → fall back to first
        )

        assert isinstance(result, GenerationResponse)
        assert result.model_id == "openai/first-model"


# ---------------------------------------------------------------------------
# generate_text fast-path routing
# ---------------------------------------------------------------------------


class TestGenerateTextRouting:
    @pytest.mark.asyncio
    async def test_uses_universal_llm_when_available(self):
        from tta_ai.models.interfaces import GenerationResponse, TaskType

        expected = GenerationResponse(
            text="generated", model_id="openai/gpt-4.1-mini"
        )

        comp = _make_component()
        comp.initialized = True  # lifecycle guard: UniversalLLM only runs when initialized
        comp._universal_llm = MagicMock()
        comp._generate_via_universal_llm = AsyncMock(return_value=expected)

        result = await comp.generate_text("prompt", TaskType.GENERAL_CHAT)
        assert result is expected
        comp._generate_via_universal_llm.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_falls_back_to_legacy_when_universal_returns_none(self):
        """When UniversalLLM returns None, generate_text falls through to legacy path."""
        comp = _make_component()
        comp.initialized = True  # lifecycle guard
        comp._universal_llm = MagicMock()
        comp._generate_via_universal_llm = AsyncMock(return_value=None)
        # Legacy path: select_model returns None → generate_text returns None
        comp.select_model = AsyncMock(return_value=None)

        from tta_ai.models.interfaces import TaskType

        result = await comp.generate_text("prompt", TaskType.GENERAL_CHAT)
        assert result is None
        comp.select_model.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uses_legacy_when_no_universal_llm(self):
        comp = _make_component()
        comp._universal_llm = None
        comp.select_model = AsyncMock(return_value=None)

        from tta_ai.models.interfaces import TaskType

        result = await comp.generate_text("prompt", TaskType.GENERAL_CHAT)
        assert result is None
        comp.select_model.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_universal_llm_when_not_initialized(self):
        """UniversalLLM path is skipped when component hasn't been started yet."""
        from tta_ai.models.interfaces import TaskType

        comp = _make_component()
        comp.initialized = False  # not started
        comp._universal_llm = MagicMock()
        comp._generate_via_universal_llm = AsyncMock()
        comp.select_model = AsyncMock(return_value=None)

        result = await comp.generate_text("prompt", TaskType.GENERAL_CHAT)
        assert result is None
        comp._generate_via_universal_llm.assert_not_awaited()
        comp.select_model.assert_awaited_once()
