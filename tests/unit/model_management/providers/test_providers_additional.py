"""
Additional provider tests targeting uncovered code paths.

Focuses on:
- CustomAPIProvider: _initialize_provider, _refresh_available_models,
  _provider_health_check with active clients, _get_provider_models
- OllamaProvider: _is_ollama_container_running, _wait_for_ollama_ready,
  _load_model_impl when model is already available
- OpenRouterProvider: _refresh_available_models edge cases
- generate_stream methods for Ollama, LMStudio, OpenRouter
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.components.model_management.interfaces import (
    GenerationRequest,
    ModelInfo,
    ModelStatus,
    ProviderType,
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
# Ollama: model loading
# ---------------------------------------------------------------------------


class TestOllamaLoadModelImpl:
    async def test_load_model_impl_returns_instance_when_available(self):
        provider = OllamaProvider()
        provider._available_models = [
            ModelInfo("llama3.1:8b", "Llama", ProviderType.OLLAMA)
        ]
        provider._client = AsyncMock()
        instance = await provider._load_model_impl("llama3.1:8b", {})
        assert instance.model_id == "llama3.1:8b"

    async def test_load_model_impl_pulls_when_not_available(self):
        provider = OllamaProvider()
        provider._available_models = []  # Model not there yet

        # After pull, we need it to appear
        pulled_model = ModelInfo("new-model:7b", "New", ProviderType.OLLAMA)

        async def fake_pull(model_id):
            # Simulate pull by adding to available models
            provider._available_models = [pulled_model]

        async def fake_refresh():
            pass  # already set by fake_pull

        provider._pull_model = fake_pull
        provider._refresh_available_models = fake_refresh
        provider._client = AsyncMock()

        instance = await provider._load_model_impl("new-model:7b", {})
        assert instance.model_id == "new-model:7b"

    async def test_load_model_impl_raises_if_pull_fails(self):
        provider = OllamaProvider()
        provider._available_models = []

        async def fake_pull(model_id):
            pass  # pull "succeeds" but model still not available

        async def fake_refresh():
            pass  # doesn't add any models

        provider._pull_model = fake_pull
        provider._refresh_available_models = fake_refresh
        provider._client = AsyncMock()

        with pytest.raises(ValueError, match="Failed to pull"):
            await provider._load_model_impl("nonexistent:latest", {})

    async def test_load_model_impl_raises_without_client(self):
        provider = OllamaProvider()
        provider._client = None
        with pytest.raises(RuntimeError, match="not initialized"):
            await provider._load_model_impl("llama:7b", {})


# ---------------------------------------------------------------------------
# Ollama: _is_ollama_container_running
# ---------------------------------------------------------------------------


class TestOllamaContainerStatus:
    async def test_container_not_running_when_no_docker_client(self):
        provider = OllamaProvider()
        provider._docker_client = None
        result = await provider._is_ollama_container_running()
        assert result is False

    async def test_container_running_when_status_is_running(self):
        provider = OllamaProvider()
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_docker.containers.get = MagicMock(return_value=mock_container)
        provider._docker_client = mock_docker
        result = await provider._is_ollama_container_running()
        assert result is True

    async def test_container_not_running_when_status_is_exited(self):
        provider = OllamaProvider()
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "exited"
        mock_docker.containers.get = MagicMock(return_value=mock_container)
        provider._docker_client = mock_docker
        result = await provider._is_ollama_container_running()
        assert result is False

    async def test_container_not_found_returns_false(self):
        import docker.errors

        provider = OllamaProvider()
        mock_docker = MagicMock()
        mock_docker.containers.get = MagicMock(
            side_effect=docker.errors.NotFound("not found")
        )
        provider._docker_client = mock_docker
        result = await provider._is_ollama_container_running()
        assert result is False

    async def test_exception_during_container_check_returns_false(self):
        provider = OllamaProvider()
        mock_docker = MagicMock()
        mock_docker.containers.get = MagicMock(side_effect=RuntimeError("docker error"))
        provider._docker_client = mock_docker
        result = await provider._is_ollama_container_running()
        assert result is False


# ---------------------------------------------------------------------------
# Ollama: _wait_for_ollama_ready
# ---------------------------------------------------------------------------


class TestOllamaWaitForReady:
    async def test_wait_for_ollama_returns_when_healthy(self):
        provider = OllamaProvider()
        provider._provider_health_check = AsyncMock(return_value=True)
        # Should return immediately
        await provider._wait_for_ollama_ready(timeout_seconds=5)

    async def test_wait_for_ollama_raises_on_timeout(self):
        provider = OllamaProvider()
        provider._provider_health_check = AsyncMock(return_value=False)
        with pytest.raises(TimeoutError):
            await provider._wait_for_ollama_ready(timeout_seconds=1)


# ---------------------------------------------------------------------------
# Ollama generate_stream
# ---------------------------------------------------------------------------


class TestOllamaModelInstanceGenerateStream:
    async def test_generate_stream_yields_chunks(self):
        # Mock streaming response with 3 chunks
        chunks = [
            json.dumps({"response": "Hello", "done": False}),
            json.dumps({"response": " World", "done": False}),
            json.dumps({"response": "", "done": True}),
        ]

        async def mock_aiter_lines():
            for chunk in chunks:
                yield chunk

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = OllamaProvider()
        instance = OllamaModelInstance("test/model", provider, mock_client)
        request = GenerationRequest(prompt="Hello")

        collected = [chunk async for chunk in instance.generate_stream(request)]

        assert "Hello" in collected
        assert " World" in collected
        assert "" not in collected  # Empty strings skipped

    async def test_generate_stream_sets_error_status_on_exception(self):
        mock_client = MagicMock()
        mock_client.stream = MagicMock(side_effect=httpx.ConnectError("refused"))
        provider = OllamaProvider()
        instance = OllamaModelInstance("test/model", provider, mock_client)

        with pytest.raises(httpx.ConnectError):
            async for _ in instance.generate_stream(GenerationRequest(prompt="hi")):
                pass

        assert instance.status == ModelStatus.ERROR


# ---------------------------------------------------------------------------
# LMStudio generate_stream
# ---------------------------------------------------------------------------


class TestLMStudioModelInstanceGenerateStream:
    async def test_generate_stream_yields_sse_content(self):
        sse_lines = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "Hi"}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": " there"}}]}),
            "data: [DONE]",
        ]

        async def mock_aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = LMStudioProvider()
        instance = LMStudioModelInstance("lms-model", provider, mock_client)

        collected = [chunk async for chunk in instance.generate_stream(GenerationRequest(prompt="hi"))]

        assert "Hi" in collected
        assert " there" in collected

    async def test_generate_stream_skips_non_data_lines(self):
        sse_lines = [
            "event: update",  # non-data line
            "data: " + json.dumps({"choices": [{"delta": {"content": "text"}}]}),
            "data: [DONE]",
        ]

        async def mock_aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = LMStudioProvider()
        instance = LMStudioModelInstance("lms-model", provider, mock_client)

        collected = [chunk async for chunk in instance.generate_stream(GenerationRequest(prompt="hi"))]

        assert "text" in collected


# ---------------------------------------------------------------------------
# OpenRouter generate_stream
# ---------------------------------------------------------------------------


class TestOpenRouterModelInstanceGenerateStream:
    async def test_generate_stream_yields_sse_content(self):
        sse_lines = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "OR chunk 1"}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": " OR chunk 2"}}]}),
            "data: [DONE]",
        ]

        async def mock_aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = OpenRouterProvider()
        instance = OpenRouterModelInstance("or/model", provider, mock_client)

        collected = [chunk async for chunk in instance.generate_stream(GenerationRequest(prompt="hi"))]

        assert "OR chunk 1" in collected
        assert " OR chunk 2" in collected


# ---------------------------------------------------------------------------
# CustomAPIProvider: _initialize_provider
# ---------------------------------------------------------------------------


class TestCustomAPIProviderInitialize:
    async def test_initialize_provider_with_openai_type(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "my-openai": {
                "api_key": "sk-test",
                "base_url": "https://api.openai.com",
                "api_type": "openai",
            }
        }

        # Mock connection test
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider._initialize_provider()

        assert result is True
        assert "my-openai" in provider._clients

    async def test_initialize_provider_with_anthropic_type(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "my-anthropic": {
                "api_key": "sk-ant-test",
                "base_url": "https://api.anthropic.com",
                "api_type": "anthropic",
            }
        }

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider._initialize_provider()

        assert result is True

    async def test_initialize_provider_handles_exception(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "bad-api": {
                "api_key": "sk-123",
                "base_url": "https://bad.api.example.com",
                "api_type": "openai",
            }
        }

        with patch(
            "httpx.AsyncClient", side_effect=RuntimeError("connection refused")
        ):
            result = await provider._initialize_provider()

        assert result is False


# ---------------------------------------------------------------------------
# CustomAPIProvider: _provider_health_check with clients
# ---------------------------------------------------------------------------


class TestCustomAPIProviderHealthCheck:
    async def test_health_check_all_clients_healthy(self):
        provider = CustomAPIProvider()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._clients = {"api1": mock_client, "api2": mock_client}

        result = await provider._provider_health_check()
        assert result is True

    async def test_health_check_half_healthy(self):
        provider = CustomAPIProvider()
        healthy_response = MagicMock()
        healthy_response.status_code = 200
        healthy_client = AsyncMock()
        healthy_client.get = AsyncMock(return_value=healthy_response)

        unhealthy_client = AsyncMock()
        unhealthy_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

        provider._clients = {"good": healthy_client, "bad": unhealthy_client}
        result = await provider._provider_health_check()
        # 1 out of 2 = 50%, which is >= 50% threshold
        assert result is True

    async def test_health_check_no_healthy_clients(self):
        provider = CustomAPIProvider()
        bad_client = AsyncMock()
        bad_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider._clients = {"bad1": bad_client, "bad2": bad_client}
        result = await provider._provider_health_check()
        assert result is False


# ---------------------------------------------------------------------------
# CustomAPIProvider: _refresh_available_models
# ---------------------------------------------------------------------------


class TestCustomAPIProviderRefreshModels:
    async def test_refresh_available_models_from_api(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "my-api": {
                "api_key": "sk-test",
                "base_url": "https://api.example.com",
                "api_type": "openai",
            }
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(
            return_value={
                "data": [
                    {"id": "model-1", "object": "model"},
                    {"id": "model-2", "object": "model"},
                ]
            }
        )
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._clients = {"my-api": mock_client}

        await provider._refresh_available_models()
        assert len(provider._available_models) == 2

    async def test_refresh_falls_back_to_predefined_on_error(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "my-api": {
                "api_key": "sk-test",
                "base_url": "https://api.example.com",
                "api_type": "openai",
            }
        }

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        provider._clients = {"my-api": mock_client}

        await provider._refresh_available_models()
        # Should have fallen back to predefined models (gpt-4o-mini, gpt-4o)
        assert len(provider._available_models) >= 2

    async def test_refresh_uses_predefined_when_api_returns_non_200(self):
        provider = CustomAPIProvider()
        provider._api_configs = {
            "my-api": {
                "api_key": "sk-test",
                "base_url": "https://api.example.com",
                "api_type": "anthropic",
            }
        }

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._clients = {"my-api": mock_client}

        await provider._refresh_available_models()
        # Anthropic predefined models
        assert any("claude" in m.model_id for m in provider._available_models)


# ---------------------------------------------------------------------------
# CustomAPIModelInstance: generate_stream
# ---------------------------------------------------------------------------


class TestCustomAPIModelInstanceGenerateStream:
    async def test_generate_stream_openai_format(self):
        sse_lines = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "Hello"}}]}),
            "data: [DONE]",
        ]

        async def mock_aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "openai"}
        )

        collected = [chunk async for chunk in instance.generate_stream(GenerationRequest(prompt="hi"))]

        assert "Hello" in collected

    async def test_generate_stream_anthropic_format(self):
        sse_lines = [
            "data: " + json.dumps({"type": "content_block_delta", "delta": {"text": "Ant chunk"}}),
            "data: " + json.dumps({"type": "message_stop"}),
        ]

        async def mock_aiter_lines():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_ctx)

        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "anthropic"}
        )

        collected = [chunk async for chunk in instance.generate_stream(GenerationRequest(prompt="hi"))]

        assert "Ant chunk" in collected

    async def test_generate_stream_sets_error_status_on_exception(self):
        mock_client = MagicMock()
        mock_client.stream = MagicMock(side_effect=httpx.ConnectError("refused"))
        provider = CustomAPIProvider()
        instance = CustomAPIModelInstance(
            "custom/model", provider, mock_client, {"api_type": "openai"}
        )
        with pytest.raises(httpx.ConnectError):
            async for _ in instance.generate_stream(GenerationRequest(prompt="hi")):
                pass
        assert instance.status == ModelStatus.ERROR


# ---------------------------------------------------------------------------
# OpenRouterProvider: _refresh_available_models edge cases
# ---------------------------------------------------------------------------


class TestOpenRouterRefreshModels:
    async def test_refresh_handles_models_with_string_zero_pricing(self):
        provider = OpenRouterProvider()
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "free/model",
                    "name": "Free Model",
                    "description": "free",
                    "pricing": {"prompt": "0", "completion": "0"},
                    "context_length": 8192,
                }
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 1
        model = provider._available_models[0]
        assert model.is_free is True

    async def test_refresh_handles_models_with_no_pricing(self):
        provider = OpenRouterProvider()
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "unknown/model",
                    "name": "Unknown",
                    "description": "",
                    "pricing": {},
                    "context_length": None,
                }
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        assert len(provider._available_models) == 1
        model = provider._available_models[0]
        assert model.cost_per_token is None

    async def test_refresh_infers_chat_capabilities_from_name(self):
        provider = OpenRouterProvider()
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "org/instruct-model",
                    "name": "Instruct",
                    "description": "",
                    "pricing": {"prompt": "1", "completion": "1"},
                    "context_length": 4096,
                }
            ]
        }
        mock_client.get = AsyncMock(return_value=mock_response)
        provider._client = mock_client
        await provider._refresh_available_models()
        model = provider._available_models[0]
        assert "instruction_following" in model.capabilities

    async def test_refresh_raises_without_client(self):
        provider = OpenRouterProvider()
        provider._client = None
        with pytest.raises(RuntimeError, match="not initialized"):
            await provider._refresh_available_models()


# ---------------------------------------------------------------------------
# BaseProvider load_model with unhealthy cached instance
# ---------------------------------------------------------------------------


class TestBaseProviderLoadModel:
    async def test_load_model_reloads_if_existing_unhealthy(self):
        from src.components.model_management.providers.base import BaseProvider

        class MinimalProvider(BaseProvider):
            @property
            def provider_type(self):
                return ProviderType.OPENROUTER

            async def _validate_config(self, config):
                return True

            async def _initialize_provider(self):
                return True

            async def _refresh_available_models(self):
                self._available_models = []
                from datetime import datetime
                self._last_model_refresh = datetime.now()

            async def _load_model_impl(self, model_id, config):
                from src.components.model_management.interfaces import (
                    GenerationResponse,
                )
                instance = MagicMock()
                instance.model_id = model_id
                instance.health_check = AsyncMock(return_value=True)
                instance.generate = AsyncMock(
                    return_value=GenerationResponse(text="ok", model_id=model_id, latency_ms=1.0)
                )
                return instance

            async def _unload_model_impl(self, instance):
                pass

            async def _provider_health_check(self):
                return True

        provider = MinimalProvider()
        await provider.initialize({})

        # Pre-load an unhealthy instance
        unhealthy = MagicMock()
        unhealthy.health_check = AsyncMock(return_value=False)
        provider._loaded_models["test-model"] = unhealthy

        # Load should detect unhealthy, unload, then reload
        instance = await provider.load_model("test-model")
        assert instance is not None
        assert instance.model_id == "test-model"

    async def test_load_model_raises_if_not_initialized(self):
        from src.components.model_management.providers.base import BaseProvider

        class MinimalProvider(BaseProvider):
            @property
            def provider_type(self):
                return ProviderType.OPENROUTER

            async def _validate_config(self, config):
                return True

            async def _initialize_provider(self):
                return True

            async def _refresh_available_models(self):
                pass

            async def _load_model_impl(self, model_id, config):
                pass

            async def _unload_model_impl(self, instance):
                pass

            async def _provider_health_check(self):
                return True

        provider = MinimalProvider()
        # NOT initialized
        with pytest.raises(RuntimeError, match="not initialized"):
            await provider.load_model("test-model")
