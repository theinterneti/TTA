"""
Unit tests for model_management providers.

Tests cover:
- BaseModelInstance / BaseProvider shared logic
- OllamaProvider: config, context-length estimation, capabilities
- LMStudioProvider: config, context-length estimation
- OpenRouterProvider: config helpers, filter settings, affordable/free models
- CustomAPIProvider: config validation, helper methods
- OllamaModelInstance.generate / LMStudioModelInstance.generate
- OpenRouterModelInstance.generate
- CustomAPIModelInstance: request preparation, response extraction
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.components.model_management.interfaces import (
    GenerationRequest,
    GenerationResponse,
    ModelInfo,
    ModelStatus,
    ProviderType,
)
from src.components.model_management.providers.base import (
    BaseModelInstance,
    BaseProvider,
)
from src.components.model_management.providers.custom_api import (
    CustomAPIModelInstance,
    CustomAPIProvider,
)
from src.components.model_management.providers.lm_studio import (
    LMStudioModelInstance,
    LMStudioProvider,
)
from src.components.model_management.providers.ollama import (
    OllamaModelInstance,
    OllamaProvider,
)
from src.components.model_management.providers.openrouter import (
    OpenRouterModelInstance,
    OpenRouterProvider,
)

# ---------------------------------------------------------------------------
# Helpers / concrete BaseProvider subclass for testing abstract methods
# ---------------------------------------------------------------------------


class ConcreteProvider(BaseProvider):
    """Minimal concrete provider for testing BaseProvider methods."""

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER

    async def _validate_config(self, config: dict[str, Any]) -> bool:
        return True

    async def _initialize_provider(self) -> bool:
        return True

    async def _refresh_available_models(self) -> None:
        self._available_models = []
        self._last_model_refresh = datetime.now()

    async def _load_model_impl(self, model_id: str, config: dict[str, Any]):
        raise NotImplementedError

    async def _unload_model_impl(self, instance) -> None:
        pass

    async def _provider_health_check(self) -> bool:
        return True


class ConcreteModelInstance(BaseModelInstance):
    """Minimal concrete model instance for testing BaseModelInstance methods."""

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text="ok", model_id=self.model_id, latency_ms=1.0)

    async def generate_stream(self, request: GenerationRequest):
        yield "ok"


# ---------------------------------------------------------------------------
# BaseProvider tests
# ---------------------------------------------------------------------------


class TestBaseProvider:
    @pytest.fixture
    def provider(self):
        return ConcreteProvider()

    async def test_initialize_sets_initialized_flag(self, provider):
        result = await provider.initialize({})
        assert result is True
        assert provider._initialized is True

    async def test_get_available_models_raises_if_not_initialized(self, provider):
        with pytest.raises(RuntimeError, match="not initialized"):
            await provider.get_available_models()

    async def test_get_available_models_returns_list_when_initialized(self, provider):
        await provider.initialize({})
        models = await provider.get_available_models()
        assert isinstance(models, list)

    async def test_get_available_models_applies_free_only_filter(self, provider):
        await provider.initialize({})
        provider._available_models = [
            ModelInfo("free-m", "Free", ProviderType.OPENROUTER, is_free=True),
            ModelInfo("paid-m", "Paid", ProviderType.OPENROUTER, is_free=False),
        ]
        models = await provider.get_available_models(filters={"free_only": True})
        assert len(models) == 1
        assert models[0].model_id == "free-m"

    async def test_get_available_models_applies_max_cost_filter(self, provider):
        await provider.initialize({})
        provider._available_models = [
            ModelInfo(
                "cheap", "Cheap", ProviderType.OPENROUTER, cost_per_token=0.0001
            ),
            ModelInfo(
                "expensive", "Expensive", ProviderType.OPENROUTER, cost_per_token=0.01
            ),
        ]
        models = await provider.get_available_models(
            filters={"max_cost_per_token": 0.001}
        )
        assert len(models) == 1
        assert models[0].model_id == "cheap"

    async def test_get_available_models_applies_min_context_filter(self, provider):
        await provider.initialize({})
        provider._available_models = [
            ModelInfo(
                "large", "Large", ProviderType.OPENROUTER, context_length=32000
            ),
            ModelInfo(
                "small", "Small", ProviderType.OPENROUTER, context_length=1024
            ),
        ]
        models = await provider.get_available_models(
            filters={"min_context_length": 8192}
        )
        assert len(models) == 1
        assert models[0].model_id == "large"

    async def test_get_available_models_applies_capabilities_filter(self, provider):
        await provider.initialize({})
        provider._available_models = [
            ModelInfo(
                "cap-model",
                "Cap",
                ProviderType.OPENROUTER,
                capabilities=["chat", "code"],
            ),
            ModelInfo(
                "no-cap",
                "No cap",
                ProviderType.OPENROUTER,
                capabilities=["chat"],
            ),
        ]
        models = await provider.get_available_models(
            filters={"required_capabilities": ["code"]}
        )
        assert len(models) == 1
        assert models[0].model_id == "cap-model"

    async def test_unload_model_returns_true_if_not_loaded(self, provider):
        result = await provider.unload_model("nonexistent-model")
        assert result is True

    async def test_unload_model_removes_loaded_model(self, provider):
        await provider.initialize({})
        instance = ConcreteModelInstance("test-model", provider)
        provider._loaded_models["test-model"] = instance
        result = await provider.unload_model("test-model")
        assert result is True
        assert "test-model" not in provider._loaded_models

    async def test_get_provider_metrics_returns_dict(self, provider):
        await provider.initialize({})
        metrics = await provider.get_provider_metrics()
        assert metrics["provider_type"] == ProviderType.OPENROUTER.value
        assert metrics["initialized"] is True
        assert "loaded_models_count" in metrics
        assert "available_models_count" in metrics

    def test_should_refresh_models_when_never_refreshed(self, provider):
        provider._last_model_refresh = None
        assert provider._should_refresh_models() is True

    def test_should_not_refresh_models_when_recently_refreshed(self, provider):
        provider._last_model_refresh = datetime.now()
        assert provider._should_refresh_models() is False

    def test_should_refresh_models_when_stale(self, provider):
        provider._last_model_refresh = datetime.now() - timedelta(hours=2)
        assert provider._should_refresh_models() is True

    async def test_health_check_returns_true_when_healthy(self, provider):
        result = await provider.health_check()
        assert result is True

    async def test_health_check_removes_unhealthy_models(self, provider):
        """Unhealthy loaded models are unloaded during health check."""
        await provider.initialize({})
        bad_instance = AsyncMock()
        bad_instance.health_check = AsyncMock(return_value=False)
        provider._loaded_models["bad-model"] = bad_instance
        await provider.health_check()
        assert "bad-model" not in provider._loaded_models


# ---------------------------------------------------------------------------
# BaseModelInstance tests
# ---------------------------------------------------------------------------


class TestBaseModelInstance:
    @pytest.fixture
    def provider(self):
        return ConcreteProvider()

    @pytest.fixture
    def instance(self, provider):
        return ConcreteModelInstance("test-model", provider)

    def test_model_id_property(self, instance):
        assert instance.model_id == "test-model"

    def test_initial_status_is_unknown(self, instance):
        assert instance.status == ModelStatus.UNKNOWN

    async def test_health_check_sets_status_ready_on_success(self, instance):
        result = await instance.health_check()
        assert result is True
        assert instance.status == ModelStatus.READY

    async def test_get_metrics_returns_dict_with_model_id(self, instance):
        metrics = await instance.get_metrics()
        assert metrics["model_id"] == "test-model"
        assert "status" in metrics
        assert "provider_type" in metrics

    def test_update_metrics_persists_values(self, instance):
        instance._update_metrics({"latency_ms": 100})
        assert instance._metrics["latency_ms"] == 100


# ---------------------------------------------------------------------------
# OllamaProvider tests
# ---------------------------------------------------------------------------


class TestOllamaProvider:
    @pytest.fixture
    def provider(self):
        return OllamaProvider()

    def test_provider_type_is_ollama(self, provider):
        assert provider.provider_type == ProviderType.OLLAMA

    async def test_validate_config_sets_defaults(self, provider):
        result = await provider._validate_config({})
        assert result is True
        assert provider._ollama_host == "localhost"
        assert provider._ollama_port == 11434
        assert provider._use_docker is True

    async def test_validate_config_uses_provided_values(self, provider):
        config = {
            "host": "192.168.1.10",
            "port": 11435,
            "use_docker": False,
            "container_name": "my-ollama",
        }
        result = await provider._validate_config(config)
        assert result is True
        assert provider._ollama_host == "192.168.1.10"
        assert provider._ollama_port == 11435
        assert provider._use_docker is False
        assert provider._container_name == "my-ollama"

    def test_estimate_context_length_llama31(self, provider):
        assert provider._estimate_context_length("llama3.1:8b") == 128000

    def test_estimate_context_length_llama32(self, provider):
        assert provider._estimate_context_length("llama3.2:3b") == 128000

    def test_estimate_context_length_old_llama(self, provider):
        assert provider._estimate_context_length("llama2:13b") == 4096

    def test_estimate_context_length_qwen(self, provider):
        assert provider._estimate_context_length("qwen2.5:7b") == 32768

    def test_estimate_context_length_mistral(self, provider):
        assert provider._estimate_context_length("mistral:7b") == 32768

    def test_estimate_context_length_phi(self, provider):
        assert provider._estimate_context_length("phi3:mini") == 4096

    def test_estimate_context_length_unknown(self, provider):
        assert provider._estimate_context_length("unknown-model") == 4096

    def test_determine_capabilities_basic(self, provider):
        caps = provider._determine_capabilities("gemma3:4b")
        assert "text_generation" in caps

    def test_determine_capabilities_instruct_chat(self, provider):
        caps = provider._determine_capabilities("llama3.1:8b-instruct")
        assert "instruction_following" in caps
        assert "chat" in caps

    def test_determine_capabilities_chat_model(self, provider):
        caps = provider._determine_capabilities("mistral-chat:7b")
        assert "chat" in caps

    def test_determine_capabilities_code_model(self, provider):
        caps = provider._determine_capabilities("deepseek-coder:1.3b")
        assert "code_generation" in caps

    def test_determine_capabilities_vision_model(self, provider):
        caps = provider._determine_capabilities("llava:vision-7b")
        assert "vision" in caps

    async def test_provider_health_check_returns_false_without_client(self, provider):
        provider._client = None
        result = await provider._provider_health_check()
        assert result is False

    async def test_provider_health_check_returns_true_on_200(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        result = await provider._provider_health_check()
        assert result is True

    async def test_provider_health_check_returns_false_on_error(self, provider):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider._client = mock_client
        result = await provider._provider_health_check()
        assert result is False

    async def test_refresh_available_models_parses_response(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.1:8b", "size": 4_000_000_000},
                {"name": "qwen2.5:7b", "size": 3_000_000_000},
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 2
        ids = [m.model_id for m in provider._available_models]
        assert "llama3.1:8b" in ids
        assert "qwen2.5:7b" in ids

    async def test_refresh_available_models_skips_empty_names(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {"name": ""},  # empty — should be skipped
                {"name": "qwen2.5:7b"},
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 1

    async def test_refresh_available_models_raises_without_client(self, provider):
        with pytest.raises(RuntimeError, match="not initialized"):
            await provider._refresh_available_models()

    async def test_unload_model_impl_does_nothing(self, provider):
        # OllamaProvider._unload_model_impl is a no-op
        instance = MagicMock()
        await provider._unload_model_impl(instance)  # Should not raise

    async def test_cleanup_closes_client(self, provider):
        mock_client = AsyncMock()
        provider._client = mock_client
        await provider.cleanup()
        mock_client.aclose.assert_called_once()
        assert provider._client is None


# ---------------------------------------------------------------------------
# OllamaModelInstance.generate tests
# ---------------------------------------------------------------------------


class TestOllamaModelInstanceGenerate:
    def _make_instance(self, response_json: dict) -> OllamaModelInstance:
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = OllamaProvider()
        return OllamaModelInstance("test/model", provider, mock_client)

    async def test_generate_returns_text_from_response(self):
        instance = self._make_instance(
            {
                "response": "Hello!",
                "prompt_eval_count": 5,
                "eval_count": 3,
                "eval_duration": 1_000_000_000,
                "load_duration": 500_000_000,
            }
        )
        request = GenerationRequest(prompt="Hi", max_tokens=50, temperature=0.7)
        response = await instance.generate(request)
        assert response.text == "Hello!"
        assert response.model_id == "test/model"
        assert response.usage["prompt_tokens"] == 5
        assert response.usage["completion_tokens"] == 3
        assert response.usage["total_tokens"] == 8

    async def test_generate_raises_on_empty_response(self):
        instance = self._make_instance({"response": "", "eval_count": 0})
        request = GenerationRequest(prompt="Hi")
        with pytest.raises(ValueError, match="No response"):
            await instance.generate(request)

    async def test_generate_sets_error_status_on_exception(self):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider = OllamaProvider()
        instance = OllamaModelInstance("test/model", provider, mock_client)
        request = GenerationRequest(prompt="Hi")
        with pytest.raises(httpx.ConnectError):
            await instance.generate(request)
        assert instance.status == ModelStatus.ERROR

    async def test_generate_with_stop_sequences(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "ok", "eval_count": 1}
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = OllamaProvider()
        instance = OllamaModelInstance("test/model", provider, mock_client)
        request = GenerationRequest(prompt="Hi", stop_sequences=["STOP", "END"])
        response = await instance.generate(request)
        assert response.text == "ok"
        # Verify stop was passed in payload
        call_kwargs = mock_client.post.call_args.kwargs
        payload = call_kwargs["json"]
        assert payload["options"]["stop"] == ["STOP", "END"]

    async def test_generate_metadata_has_provider_key(self):
        instance = self._make_instance({"response": "answer", "eval_count": 2})
        request = GenerationRequest(prompt="test")
        response = await instance.generate(request)
        assert response.metadata["provider"] == "ollama"


# ---------------------------------------------------------------------------
# LMStudioProvider tests
# ---------------------------------------------------------------------------


class TestLMStudioProvider:
    @pytest.fixture
    def provider(self):
        return LMStudioProvider()

    def test_provider_type_is_lm_studio(self, provider):
        assert provider.provider_type == ProviderType.LM_STUDIO

    async def test_validate_config_uses_default_url(self, provider):
        result = await provider._validate_config({})
        assert result is True
        assert provider._base_url == "http://localhost:1234"

    async def test_validate_config_uses_provided_url(self, provider):
        result = await provider._validate_config({"base_url": "http://192.168.1.5:1234"})
        assert result is True
        assert provider._base_url == "http://192.168.1.5:1234"

    def test_estimate_context_length_llama31(self, provider):
        assert provider._estimate_context_length("llama-3.1-8b-instruct") == 128000

    def test_estimate_context_length_llama32(self, provider):
        assert provider._estimate_context_length("llama-3.2-3b") == 128000

    def test_estimate_context_length_old_llama(self, provider):
        assert provider._estimate_context_length("llama-2-13b") == 4096

    def test_estimate_context_length_qwen(self, provider):
        assert provider._estimate_context_length("qwen-2.5-7b") == 32768

    def test_estimate_context_length_mistral(self, provider):
        assert provider._estimate_context_length("mistral-7b") == 32768

    def test_estimate_context_length_phi(self, provider):
        assert provider._estimate_context_length("phi-3-mini") == 4096

    def test_estimate_context_length_gemma(self, provider):
        assert provider._estimate_context_length("gemma-2-9b") == 8192

    def test_estimate_context_length_default(self, provider):
        assert provider._estimate_context_length("unknown-model-5b") == 4096

    async def test_provider_health_check_returns_false_without_client(self, provider):
        provider._client = None
        result = await provider._provider_health_check()
        assert result is False

    async def test_provider_health_check_returns_true_on_200(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        result = await provider._provider_health_check()
        assert result is True

    async def test_provider_health_check_returns_false_on_exception(self, provider):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider._client = mock_client
        result = await provider._provider_health_check()
        assert result is False

    async def test_refresh_available_models_parses_response(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "llama-3.1-8b-instruct", "object": "model"},
                {"id": "gemma-2-9b-instruct", "object": "model"},
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 2
        assert all(m.is_free for m in provider._available_models)

    async def test_refresh_available_models_skips_empty_ids(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": ""},  # empty — should be skipped
                {"id": "valid-model"},
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 1

    async def test_load_model_impl_raises_if_model_not_available(self, provider):
        provider._available_models = []
        provider._client = AsyncMock()
        with pytest.raises(ValueError, match="not available"):
            await provider._load_model_impl("nonexistent-model", {})

    async def test_load_model_impl_returns_instance_when_available(self, provider):
        provider._available_models = [
            ModelInfo("available/model", "Avail", ProviderType.LM_STUDIO)
        ]
        provider._client = AsyncMock()
        instance = await provider._load_model_impl("available/model", {})
        assert instance.model_id == "available/model"

    async def test_cleanup_closes_client(self, provider):
        mock_client = AsyncMock()
        provider._client = mock_client
        await provider.cleanup()
        mock_client.aclose.assert_called_once()
        assert provider._client is None


# ---------------------------------------------------------------------------
# LMStudioModelInstance.generate tests
# ---------------------------------------------------------------------------


class TestLMStudioModelInstanceGenerate:
    def _make_instance(self, response_json: dict) -> LMStudioModelInstance:
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = LMStudioProvider()
        return LMStudioModelInstance("lms-model", provider, mock_client)

    async def test_generate_returns_text(self):
        instance = self._make_instance(
            {
                "choices": [{"message": {"content": "LMS response"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            }
        )
        req = GenerationRequest(prompt="Hello")
        resp = await instance.generate(req)
        assert resp.text == "LMS response"
        assert resp.model_id == "lms-model"
        assert resp.metadata["provider"] == "lm_studio"

    async def test_generate_raises_on_empty_choices(self):
        instance = self._make_instance({"choices": []})
        req = GenerationRequest(prompt="Hello")
        with pytest.raises(ValueError, match="No choices"):
            await instance.generate(req)

    async def test_generate_raises_on_missing_choices_key(self):
        instance = self._make_instance({})
        req = GenerationRequest(prompt="Hello")
        with pytest.raises((ValueError, KeyError)):
            await instance.generate(req)

    async def test_generate_sets_error_status_on_exception(self):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider = LMStudioProvider()
        instance = LMStudioModelInstance("lms-model", provider, mock_client)
        with pytest.raises(httpx.ConnectError):
            await instance.generate(GenerationRequest(prompt="hi"))
        assert instance.status == ModelStatus.ERROR

    async def test_generate_with_stop_sequences(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "ok"}}],
            "usage": {},
        }
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = LMStudioProvider()
        instance = LMStudioModelInstance("lms-model", provider, mock_client)
        req = GenerationRequest(prompt="hi", stop_sequences=["END"])
        resp = await instance.generate(req)
        assert resp.text == "ok"
        payload = mock_client.post.call_args.kwargs["json"]
        assert payload["stop"] == ["END"]


# ---------------------------------------------------------------------------
# OpenRouterProvider tests
# ---------------------------------------------------------------------------


class TestOpenRouterProvider:
    @pytest.fixture
    def provider(self):
        return OpenRouterProvider()

    def test_provider_type_is_openrouter(self, provider):
        assert provider.provider_type == ProviderType.OPENROUTER

    async def test_validate_config_requires_api_key(self, provider):
        result = await provider._validate_config({})
        assert result is False

    async def test_validate_config_sets_api_key(self, provider):
        result = await provider._validate_config({"api_key": "sk-test-123"})
        assert result is True
        assert provider._api_key == "sk-test-123"

    async def test_validate_config_sets_base_url(self, provider):
        await provider._validate_config(
            {"api_key": "sk-123", "base_url": "https://custom.openrouter.ai"}
        )
        assert provider._base_url == "https://custom.openrouter.ai"

    def test_get_bool_config_from_bool_value(self, provider):
        provider._config = {"show_free_only": True}
        result = provider._get_bool_config("show_free_only", "NOPE_ENV", False)
        assert result is True

    def test_get_bool_config_from_string_true(self, provider):
        provider._config = {"show_free_only": "yes"}
        result = provider._get_bool_config("show_free_only", "NOPE_ENV", False)
        assert result is True

    def test_get_bool_config_from_string_false(self, provider):
        provider._config = {"show_free_only": "false"}
        result = provider._get_bool_config("show_free_only", "NOPE_ENV", True)
        assert result is False

    def test_get_bool_config_falls_back_to_default(self, provider):
        provider._config = {}
        result = provider._get_bool_config("missing_key", "NOPE_ENV_99999", True)
        assert result is True

    def test_get_bool_config_reads_env_var(self, provider, monkeypatch):
        provider._config = {}
        monkeypatch.setenv("OPENROUTER_SHOW_FREE_ONLY", "1")
        result = provider._get_bool_config(
            "show_free_only", "OPENROUTER_SHOW_FREE_ONLY", False
        )
        assert result is True

    def test_get_float_config_from_config(self, provider):
        provider._config = {"max_cost_per_token": 0.005}
        result = provider._get_float_config("max_cost_per_token", "NOPE", 0.001)
        assert result == 0.005

    def test_get_float_config_falls_back_to_default(self, provider):
        provider._config = {}
        result = provider._get_float_config("missing", "NOPE_ENV_99999", 0.999)
        assert result == 0.999

    def test_get_float_config_from_env_var(self, provider, monkeypatch):
        provider._config = {}
        monkeypatch.setenv("OPENROUTER_MAX_COST_PER_TOKEN", "0.0025")
        result = provider._get_float_config(
            "max_cost_per_token", "OPENROUTER_MAX_COST_PER_TOKEN", 0.001
        )
        assert result == 0.0025

    async def test_set_free_models_filter_updates_settings(self, provider):
        await provider.set_free_models_filter(
            show_free_only=True, prefer_free=False, max_cost_per_token=0.002
        )
        assert provider._show_free_only is True
        assert provider._prefer_free_models is False
        assert provider._max_cost_per_token == 0.002

    async def test_get_filter_settings_returns_dict(self, provider):
        settings = await provider.get_filter_settings()
        assert "show_free_only" in settings
        assert "prefer_free_models" in settings
        assert "max_cost_per_token" in settings

    async def test_provider_health_check_returns_false_without_client(self, provider):
        provider._client = None
        result = await provider._provider_health_check()
        assert result is False

    async def test_provider_health_check_returns_true_on_200(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        result = await provider._provider_health_check()
        assert result is True

    async def test_get_available_models_show_free_only(self, provider):
        """When show_free_only=True, only free models are returned."""
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._show_free_only = True
        provider._available_models = [
            ModelInfo("free/m", "Free", ProviderType.OPENROUTER, is_free=True),
            ModelInfo("paid/m", "Paid", ProviderType.OPENROUTER, is_free=False),
        ]
        # Prevent stale-refresh
        provider._last_model_refresh = datetime.now()
        models = await provider.get_available_models()
        assert all(m.is_free for m in models)
        assert len(models) == 1

    async def test_get_available_models_prefer_free_sorts_first(self, provider):
        """When prefer_free=True, free models appear before paid."""
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._show_free_only = False
        provider._prefer_free_models = True
        provider._max_cost_per_token = 0.01  # allow paid
        provider._available_models = [
            ModelInfo(
                "paid/m", "Paid", ProviderType.OPENROUTER, is_free=False, cost_per_token=0.001
            ),
            ModelInfo("free/m", "Free", ProviderType.OPENROUTER, is_free=True),
        ]
        provider._last_model_refresh = datetime.now()
        models = await provider.get_available_models()
        # Free models should come first
        assert models[0].is_free is True

    async def test_get_free_models_filters_correctly(self, provider):
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._available_models = [
            ModelInfo("free/m", "Free", ProviderType.OPENROUTER, is_free=True),
            ModelInfo("paid/m", "Paid", ProviderType.OPENROUTER, is_free=False),
        ]
        provider._last_model_refresh = datetime.now()
        models = await provider.get_free_models()
        assert all(m.is_free for m in models)

    async def test_get_affordable_models_includes_free_and_cheap(self, provider):
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._available_models = [
            ModelInfo("free/m", "Free", ProviderType.OPENROUTER, is_free=True),
            ModelInfo(
                "cheap/m", "Cheap", ProviderType.OPENROUTER, cost_per_token=0.0001
            ),
            ModelInfo(
                "expensive/m", "Expensive", ProviderType.OPENROUTER, cost_per_token=0.01
            ),
        ]
        provider._last_model_refresh = datetime.now()
        models = await provider.get_affordable_models(max_cost_per_token=0.001)
        ids = [m.model_id for m in models]
        assert "free/m" in ids
        assert "cheap/m" in ids
        assert "expensive/m" not in ids

    async def test_estimate_cost_returns_none_for_unknown_model(self, provider):
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._available_models = []
        provider._last_model_refresh = datetime.now()
        cost = await provider.estimate_cost("nonexistent", 1000)
        assert cost is None

    async def test_estimate_cost_returns_value_for_known_model(self, provider):
        await provider._validate_config({"api_key": "sk-test"})
        provider._initialized = True
        provider._available_models = [
            ModelInfo(
                "known/m",
                "Known",
                ProviderType.OPENROUTER,
                cost_per_token=0.001,
            )
        ]
        provider._last_model_refresh = datetime.now()
        cost = await provider.estimate_cost("known/m", 1000)
        assert cost == pytest.approx(1.0)

    async def test_load_model_impl_raises_if_not_available(self, provider):
        provider._client = AsyncMock()
        provider._available_models = []
        with pytest.raises(ValueError, match="not available"):
            await provider._load_model_impl("nonexistent", {})

    async def test_cleanup_closes_client(self, provider):
        mock_client = AsyncMock()
        provider._client = mock_client
        await provider.cleanup()
        mock_client.aclose.assert_called_once()
        assert provider._client is None

    async def test_refresh_available_models_parses_pricing(self, provider):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "free-model",
                    "name": "Free Model",
                    "description": "free",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "context_length": 8192,
                },
                {
                    "id": "paid-model",
                    "name": "Paid Model",
                    "description": "paid",
                    "pricing": {"prompt": "5", "completion": "5"},
                    "context_length": 16384,
                },
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 2
        free_model = next(m for m in provider._available_models if m.model_id == "free-model")
        paid_model = next(m for m in provider._available_models if m.model_id == "paid-model")
        assert free_model.cost_per_token == pytest.approx(0.0)
        assert paid_model.cost_per_token is not None and paid_model.cost_per_token > 0


# ---------------------------------------------------------------------------
# OpenRouterModelInstance.generate tests
# ---------------------------------------------------------------------------


class TestOpenRouterModelInstanceGenerate:
    def _make_instance(self, response_json: dict) -> OpenRouterModelInstance:
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = OpenRouterProvider()
        return OpenRouterModelInstance("or/model", provider, mock_client)

    async def test_generate_returns_text(self):
        instance = self._make_instance(
            {
                "choices": [{"message": {"content": "OR response"}}],
                "usage": {"total_tokens": 10},
            }
        )
        req = GenerationRequest(prompt="Hello")
        resp = await instance.generate(req)
        assert resp.text == "OR response"
        assert resp.metadata["provider"] == "openrouter"

    async def test_generate_raises_on_empty_choices(self):
        instance = self._make_instance({"choices": []})
        with pytest.raises(ValueError, match="No choices"):
            await instance.generate(GenerationRequest(prompt="Hi"))

    async def test_generate_sets_error_status_on_exception(self):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        provider = OpenRouterProvider()
        instance = OpenRouterModelInstance("or/model", provider, mock_client)
        with pytest.raises(httpx.TimeoutException):
            await instance.generate(GenerationRequest(prompt="Hi"))
        assert instance.status == ModelStatus.ERROR


# ---------------------------------------------------------------------------
# CustomAPIProvider tests
# ---------------------------------------------------------------------------


class TestCustomAPIProvider:
    @pytest.fixture
    def provider(self):
        return CustomAPIProvider()

    def test_provider_type_is_custom_api(self, provider):
        assert provider.provider_type == ProviderType.CUSTOM_API

    async def test_validate_config_fails_if_no_providers(self, provider):
        result = await provider._validate_config({})
        assert result is False

    async def test_validate_config_fails_if_missing_api_key(self, provider):
        config = {
            "custom_providers": {
                "my-api": {"base_url": "https://api.example.com"}
            }
        }
        result = await provider._validate_config(config)
        assert result is False

    async def test_validate_config_fails_if_missing_base_url(self, provider):
        config = {
            "custom_providers": {
                "my-api": {"api_key": "sk-123"}
            }
        }
        result = await provider._validate_config(config)
        assert result is False

    async def test_validate_config_succeeds_with_valid_provider(self, provider):
        config = {
            "custom_providers": {
                "my-api": {
                    "api_key": "sk-123",
                    "base_url": "https://api.example.com",
                }
            }
        }
        result = await provider._validate_config(config)
        assert result is True
        assert "my-api" in provider._api_configs

    def test_get_model_pricing_returns_defaults(self, provider):
        cost, is_free = provider._get_model_pricing("openai", "gpt-4o-mini")
        assert cost == 0.000001
        assert is_free is False

    def test_get_model_capabilities_base(self, provider):
        caps = provider._get_model_capabilities("any", "regular-model")
        assert "text_generation" in caps
        assert "chat" in caps

    def test_get_model_capabilities_instruct(self, provider):
        caps = provider._get_model_capabilities("any", "instruct-model")
        assert "instruction_following" in caps

    def test_get_model_capabilities_code(self, provider):
        caps = provider._get_model_capabilities("any", "code-model")
        assert "code_generation" in caps

    def test_get_model_capabilities_claude(self, provider):
        caps = provider._get_model_capabilities("any", "claude-3-haiku")
        assert "analysis" in caps
        assert "creative_writing" in caps

    def test_get_model_context_length_gpt4(self, provider):
        assert provider._get_model_context_length("any", "gpt-4o-mini") == 128000

    def test_get_model_context_length_claude(self, provider):
        assert provider._get_model_context_length("any", "claude-3-haiku-20240307") == 200000

    def test_get_model_context_length_default(self, provider):
        assert provider._get_model_context_length("any", "unknown-model") == 4096

    def test_get_therapeutic_safety_score_claude(self, provider):
        score = provider._get_therapeutic_safety_score("any", "claude-3-haiku")
        assert score == 9.0

    def test_get_therapeutic_safety_score_gpt4(self, provider):
        score = provider._get_therapeutic_safety_score("any", "gpt-4o")
        assert score == 8.0

    def test_get_therapeutic_safety_score_default(self, provider):
        score = provider._get_therapeutic_safety_score("any", "random-model")
        assert score == 7.0

    def test_get_predefined_models_anthropic(self, provider):
        config = {"api_type": "anthropic"}
        models = provider._get_predefined_models("anthropic", config)
        assert len(models) >= 2
        model_ids = [m.model_id for m in models]
        assert any("claude" in mid for mid in model_ids)

    def test_get_predefined_models_openai(self, provider):
        config = {"api_type": "openai"}
        models = provider._get_predefined_models("openai", config)
        assert len(models) >= 1
        model_ids = [m.model_id for m in models]
        assert any("gpt" in mid for mid in model_ids)

    async def test_provider_health_check_no_clients(self, provider):
        result = await provider._provider_health_check()
        assert result is False

    async def test_cleanup_closes_all_clients(self, provider):
        mock_client1 = AsyncMock()
        mock_client2 = AsyncMock()
        provider._clients = {"api1": mock_client1, "api2": mock_client2}
        await provider.cleanup()
        mock_client1.aclose.assert_called_once()
        mock_client2.aclose.assert_called_once()
        assert len(provider._clients) == 0

    async def test_load_model_impl_raises_if_no_providers(self, provider):
        with pytest.raises(ValueError, match="No provider"):
            await provider._load_model_impl("some-model", {})

    async def test_unload_model_impl_does_nothing(self, provider):
        instance = MagicMock()
        await provider._unload_model_impl(instance)  # Should not raise


# ---------------------------------------------------------------------------
# CustomAPIModelInstance tests
# ---------------------------------------------------------------------------


class TestCustomAPIModelInstance:
    def _make_instance(
        self, response_json: dict, api_type: str = "openai"
    ) -> CustomAPIModelInstance:
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        provider = CustomAPIProvider()
        return CustomAPIModelInstance(
            "custom/model",
            provider,
            mock_client,
            {"api_type": api_type},
        )

    async def test_generate_openai_format(self):
        instance = self._make_instance(
            {
                "choices": [{"message": {"content": "OpenAI response"}}],
                "usage": {"total_tokens": 7},
            }
        )
        resp = await instance.generate(GenerationRequest(prompt="hello"))
        assert resp.text == "OpenAI response"
        assert resp.metadata["api_type"] == "openai"

    async def test_generate_anthropic_format(self):
        instance = self._make_instance(
            {
                "content": [{"text": "Anthropic response"}],
                "usage": {"input_tokens": 5, "output_tokens": 3},
            },
            api_type="anthropic",
        )
        resp = await instance.generate(GenerationRequest(prompt="hello"))
        assert resp.text == "Anthropic response"
        assert resp.metadata["api_type"] == "anthropic"

    async def test_generate_sets_error_status_on_exception(self):
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "openai"}
        )
        with pytest.raises(httpx.ConnectError):
            await instance.generate(GenerationRequest(prompt="hi"))
        assert instance.status == ModelStatus.ERROR

    async def test_prepare_openai_request(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "openai"}
        )
        req = GenerationRequest(
            prompt="hello",
            max_tokens=100,
            temperature=0.5,
            top_p=0.8,
            stop_sequences=["STOP"],
        )
        payload = await instance._prepare_openai_request(req)
        assert payload["model"] == "custom/model"
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.5
        assert payload["stop"] == ["STOP"]
        assert payload["stream"] is False

    async def test_prepare_anthropic_request(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "anthropic"}
        )
        req = GenerationRequest(
            prompt="hello",
            max_tokens=200,
            temperature=0.3,
            stop_sequences=["END"],
        )
        payload = await instance._prepare_anthropic_request(req)
        assert payload["model"] == "custom/model"
        assert payload["max_tokens"] == 200
        assert payload["stop_sequences"] == ["END"]

    def test_extract_openai_response(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {}
        )
        data = {"choices": [{"message": {"content": "hello"}}]}
        assert instance._extract_openai_response(data) == "hello"

    def test_extract_openai_response_raises_on_no_choices(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {}
        )
        with pytest.raises(ValueError, match="No choices"):
            instance._extract_openai_response({"choices": []})

    def test_extract_anthropic_response_list_content(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {}
        )
        data = {"content": [{"text": "anthropic reply"}]}
        assert instance._extract_anthropic_response(data) == "anthropic reply"

    def test_extract_anthropic_response_raises_on_empty_content(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {}
        )
        with pytest.raises(ValueError, match="No content"):
            instance._extract_anthropic_response({"content": []})

    def test_extract_anthropic_usage(self):
        mock_client = AsyncMock()
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {}
        )
        data = {"usage": {"input_tokens": 10, "output_tokens": 5}}
        usage = instance._extract_anthropic_usage(data)
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 5
        assert usage["total_tokens"] == 15
