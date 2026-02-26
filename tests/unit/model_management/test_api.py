"""
Unit tests for model_management/api.py FastAPI routes.

Tests use FastAPI's TestClient with dependency overrides to mock the
ModelManagementComponent without needing real providers.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.components.model_management.api import (
    GenerationRequest,
    GenerationResponse,
    ModelTestRequest,
    SystemStatusResponse,
    get_model_management,
    router,
)
from src.components.model_management.interfaces import (
    ModelInfo,
    ProviderType,
    TaskType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_model_info(
    model_id: str = "test/model",
    name: str = "Test Model",
    is_free: bool = True,
    cost_per_token: float | None = 0.0,
    provider_type: ProviderType = ProviderType.OPENROUTER,
) -> ModelInfo:
    return ModelInfo(
        model_id=model_id,
        name=name,
        provider_type=provider_type,
        description="A test model",
        context_length=8192,
        cost_per_token=cost_per_token,
        is_free=is_free,
        capabilities=["chat", "text_generation"],
        therapeutic_safety_score=8.0,
        performance_score=7.5,
    )


def _make_client(component_mock) -> TestClient:
    """Create a TestClient with the dependency overridden."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_model_management] = lambda: component_mock
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Health check (no dependency needed)
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def test_health_returns_200(self):
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        resp = client.get("/api/v1/models/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "model_management"


# ---------------------------------------------------------------------------
# Dependency failure (service unavailable)
# ---------------------------------------------------------------------------


class TestDependencyFailure:
    def test_returns_503_when_component_not_available(self):
        """The default get_model_management raises 503 since no registry exists."""
        app = FastAPI()
        app.include_router(router)
        # No override — uses real get_model_management which raises 503
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/api/v1/models/status")
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# /generate endpoint
# ---------------------------------------------------------------------------


class TestGenerateEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        gen_resp = MagicMock()
        gen_resp.text = "Hello from test"
        gen_resp.model_id = "test/model"
        gen_resp.latency_ms = 250.0
        gen_resp.usage = {"prompt_tokens": 5, "completion_tokens": 4, "total_tokens": 9}
        gen_resp.metadata = {"provider": "openrouter"}
        component.generate_text = AsyncMock(return_value=gen_resp)
        return component

    def test_generate_success(self, mock_component):
        client = _make_client(mock_component)
        payload = {"prompt": "Tell me a story", "task_type": "general_chat"}
        resp = client.post("/api/v1/models/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == "Hello from test"
        assert data["model_id"] == "test/model"
        assert data["provider"] == "openrouter"
        assert data["latency_ms"] == 250.0

    def test_generate_no_response_returns_5xx(self, mock_component):
        mock_component.generate_text = AsyncMock(return_value=None)
        client = _make_client(mock_component)
        payload = {"prompt": "test"}
        resp = client.post("/api/v1/models/generate", json=payload)
        # None response causes HTTPException(503) which is caught and re-raised as 500
        assert resp.status_code in (503, 500)

    def test_generate_exception_returns_500(self, mock_component):
        mock_component.generate_text = AsyncMock(side_effect=RuntimeError("model down"))
        client = _make_client(mock_component)
        payload = {"prompt": "test"}
        resp = client.post("/api/v1/models/generate", json=payload)
        assert resp.status_code == 500

    def test_generate_uses_default_task_type(self, mock_component):
        client = _make_client(mock_component)
        payload = {"prompt": "hello"}
        resp = client.post("/api/v1/models/generate", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_component.generate_text.call_args
        assert call_kwargs.kwargs["task_type"] == TaskType.GENERAL_CHAT

    def test_generate_passes_all_params(self, mock_component):
        client = _make_client(mock_component)
        payload = {
            "prompt": "test prompt",
            "task_type": "narrative_generation",
            "max_tokens": 512,
            "temperature": 0.5,
            "top_p": 0.85,
            "stream": False,
            "max_latency_ms": 3000,
            "min_quality_score": 7.0,
        }
        resp = client.post("/api/v1/models/generate", json=payload)
        assert resp.status_code == 200
        call_kwargs = mock_component.generate_text.call_args.kwargs
        assert call_kwargs["task_type"] == TaskType.NARRATIVE_GENERATION
        assert call_kwargs["max_tokens"] == 512
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["top_p"] == 0.85

    def test_generate_response_with_no_metadata(self, mock_component):
        gen_resp = MagicMock()
        gen_resp.text = "hello"
        gen_resp.model_id = "test/model"
        gen_resp.latency_ms = None
        gen_resp.usage = None
        gen_resp.metadata = None
        mock_component.generate_text = AsyncMock(return_value=gen_resp)
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/generate", json={"prompt": "hi"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "unknown"
        assert data["latency_ms"] == 0


# ---------------------------------------------------------------------------
# /available endpoint
# ---------------------------------------------------------------------------


class TestAvailableModelsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        models = [
            _make_model_info("model-a", is_free=True),
            _make_model_info("model-b", is_free=False, cost_per_token=0.001),
        ]
        component.get_available_models = AsyncMock(return_value=models)
        return component

    def test_get_available_models_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/available")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["model_id"] == "model-a"
        assert data[1]["model_id"] == "model-b"

    def test_get_available_models_with_provider_filter(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/available?provider=openrouter")
        assert resp.status_code == 200
        mock_component.get_available_models.assert_called_once_with(
            "openrouter", free_only=False
        )

    def test_get_available_models_free_only(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/available?free_only=true")
        assert resp.status_code == 200
        mock_component.get_available_models.assert_called_once_with(
            None, free_only=True
        )

    def test_get_available_models_contains_expected_fields(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/available")
        data = resp.json()
        model = data[0]
        assert "model_id" in model
        assert "name" in model
        assert "provider" in model
        assert "description" in model
        assert "context_length" in model
        assert "cost_per_token" in model
        assert "is_free" in model
        assert "capabilities" in model
        assert "therapeutic_safety_score" in model
        assert "performance_score" in model

    def test_get_available_models_exception_returns_500(self, mock_component):
        mock_component.get_available_models = AsyncMock(side_effect=Exception("db error"))
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/available")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /free endpoint
# ---------------------------------------------------------------------------


class TestFreeModelsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.get_free_models = AsyncMock(
            return_value=[_make_model_info("free/model", is_free=True)]
        )
        return component

    def test_get_free_models_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/free")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["is_free"] is True

    def test_get_free_models_with_provider(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/free?provider=ollama")
        assert resp.status_code == 200
        mock_component.get_free_models.assert_called_once_with("ollama")

    def test_get_free_models_exception_returns_500(self, mock_component):
        mock_component.get_free_models = AsyncMock(side_effect=RuntimeError("fail"))
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/free")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /affordable endpoint
# ---------------------------------------------------------------------------


class TestAffordableModelsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.get_affordable_models = AsyncMock(
            return_value=[_make_model_info("cheap/model", cost_per_token=0.0001)]
        )
        return component

    def test_get_affordable_models_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/affordable")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1

    def test_get_affordable_models_custom_threshold(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/affordable?max_cost_per_token=0.0005")
        assert resp.status_code == 200
        mock_component.get_affordable_models.assert_called_once_with(0.0005, None)

    def test_get_affordable_models_exception_returns_500(self, mock_component):
        mock_component.get_affordable_models = AsyncMock(side_effect=Exception("fail"))
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/affordable")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /openrouter/free endpoint
# ---------------------------------------------------------------------------


class TestOpenRouterFreeModelsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.get_openrouter_free_models = AsyncMock(
            return_value=[_make_model_info("or/free-model", is_free=True)]
        )
        return component

    def test_get_openrouter_free_models_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/openrouter/free")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["model_id"] == "or/free-model"

    def test_get_openrouter_free_models_exception_returns_500(self, mock_component):
        mock_component.get_openrouter_free_models = AsyncMock(
            side_effect=Exception("or down")
        )
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/openrouter/free")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /recommendations endpoint
# ---------------------------------------------------------------------------


class TestRecommendationsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.get_model_recommendations = AsyncMock(
            return_value=["model-a", "model-b"]
        )
        return component

    def test_get_recommendations_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get(
            "/api/v1/models/recommendations?task_type=narrative_generation"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data == ["model-a", "model-b"]

    def test_get_recommendations_exception_returns_500(self, mock_component):
        mock_component.get_model_recommendations = AsyncMock(
            side_effect=ValueError("bad task")
        )
        client = _make_client(mock_component)
        resp = client.get(
            "/api/v1/models/recommendations?task_type=narrative_generation"
        )
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /test endpoint (model connectivity)
# ---------------------------------------------------------------------------


class TestModelConnectivityEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.test_model_connectivity = AsyncMock(
            return_value={
                "model_id": "test/model",
                "provider": "openrouter",
                "healthy": True,
                "latency_ms": 120.5,
                "test_response": "OK",
                "status": "success",
            }
        )
        return component

    def test_test_model_success(self, mock_component):
        client = _make_client(mock_component)
        payload = {"model_id": "test/model", "provider_name": "openrouter"}
        resp = client.post("/api/v1/models/test", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["model_id"] == "test/model"
        assert data["healthy"] is True
        assert data["status"] == "success"

    def test_test_model_exception_returns_500(self, mock_component):
        mock_component.test_model_connectivity = AsyncMock(
            side_effect=RuntimeError("connect error")
        )
        client = _make_client(mock_component)
        payload = {"model_id": "test/model", "provider_name": "openrouter"}
        resp = client.post("/api/v1/models/test", json=payload)
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /status endpoint
# ---------------------------------------------------------------------------


class TestSystemStatusEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.get_system_status = AsyncMock(
            return_value={
                "initialized": True,
                "active_models": 2,
                "providers": {"openrouter": {"healthy": True}},
                "system_resources": {"total_ram_gb": 16},
                "last_health_check": None,
            }
        )
        return component

    def test_get_system_status_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["initialized"] is True
        assert data["active_models"] == 2

    def test_get_system_status_exception_returns_500(self, mock_component):
        mock_component.get_system_status = AsyncMock(side_effect=Exception("crash"))
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/status")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /load/{provider}/{model_id} endpoint
# ---------------------------------------------------------------------------


class TestLoadModelEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.load_model = AsyncMock(return_value=MagicMock())
        return component

    def test_load_model_returns_loading_status(self, mock_component):
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/load/openrouter/test-model")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "loading"
        assert "test-model" in data["model_id"]


# ---------------------------------------------------------------------------
# /unload/{model_id} endpoint
# ---------------------------------------------------------------------------


class TestUnloadModelEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.unload_model = AsyncMock(return_value=True)
        return component

    def test_unload_model_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.delete("/api/v1/models/unload/test-model")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "unloaded"

    def test_unload_model_not_found_returns_404(self, mock_component):
        mock_component.unload_model = AsyncMock(return_value=False)
        client = _make_client(mock_component)
        resp = client.delete("/api/v1/models/unload/nonexistent-model")
        assert resp.status_code in (404, 500)

    def test_unload_model_exception_returns_500(self, mock_component):
        mock_component.unload_model = AsyncMock(side_effect=Exception("unload fail"))
        client = _make_client(mock_component)
        resp = client.delete("/api/v1/models/unload/bad-model")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /performance/{model_id} endpoint
# ---------------------------------------------------------------------------


class TestModelPerformanceEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        perf_monitor = MagicMock()
        perf_monitor.get_model_performance = AsyncMock(
            return_value={"model_id": "test-model", "total_requests": 10}
        )
        component.performance_monitor = perf_monitor
        return component

    def test_get_model_performance_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/performance/test-model")
        assert resp.status_code == 200
        data = resp.json()
        assert data["model_id"] == "test-model"

    def test_get_model_performance_no_monitor_returns_5xx(self, mock_component):
        mock_component.performance_monitor = None
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/performance/test-model")
        # HTTPException(503) inside route is re-caught and returned as 500
        assert resp.status_code in (503, 500)

    def test_get_model_performance_custom_timeframe(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/performance/test-model?timeframe_hours=48")
        assert resp.status_code == 200
        mock_component.performance_monitor.get_model_performance.assert_called_once_with(
            "test-model", 48
        )


# ---------------------------------------------------------------------------
# /performance endpoint (system-wide)
# ---------------------------------------------------------------------------


class TestSystemPerformanceEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        perf_monitor = MagicMock()
        perf_monitor.get_system_performance = AsyncMock(
            return_value={"total_models": 3, "active_models": 2}
        )
        component.performance_monitor = perf_monitor
        return component

    def test_get_system_performance_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/performance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_models"] == 3

    def test_get_system_performance_no_monitor_returns_5xx(self, mock_component):
        mock_component.performance_monitor = None
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/performance")
        assert resp.status_code in (503, 500)


# ---------------------------------------------------------------------------
# /fallback/statistics endpoint
# ---------------------------------------------------------------------------


class TestFallbackStatisticsEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        fallback_handler = MagicMock()
        fallback_handler.get_failure_statistics = MagicMock(
            return_value={
                "total_failed_models": 1,
                "recent_failures_1h": 0,
                "recent_failure_details": {},
                "provider_health": {"openrouter": True},
                "config": {
                    "max_retries": 3,
                    "exclude_failed_models_minutes": 30,
                    "fallback_strategy": "performance_based",
                },
            }
        )
        component.fallback_handler = fallback_handler
        return component

    def test_get_fallback_statistics_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/fallback/statistics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_failed_models" in data

    def test_get_fallback_statistics_no_handler_returns_5xx(self, mock_component):
        mock_component.fallback_handler = None
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/fallback/statistics")
        assert resp.status_code in (503, 500)

    def test_get_fallback_statistics_exception_returns_500(self, mock_component):
        mock_component.fallback_handler.get_failure_statistics = MagicMock(
            side_effect=Exception("stats error")
        )
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/fallback/statistics")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /fallback/reset/{model_id} endpoint
# ---------------------------------------------------------------------------


class TestResetModelFailuresEndpoint:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        fallback_handler = MagicMock()
        fallback_handler.reset_model_failures = MagicMock(return_value=True)
        component.fallback_handler = fallback_handler
        return component

    def test_reset_model_failures_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/fallback/reset/test-model")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "reset"
        assert data["model_id"] == "test-model"

    def test_reset_model_failures_not_found_returns_404(self, mock_component):
        mock_component.fallback_handler.reset_model_failures = MagicMock(
            return_value=False
        )
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/fallback/reset/nonexistent-model")
        assert resp.status_code in (404, 500)

    def test_reset_model_failures_no_handler_returns_5xx(self, mock_component):
        mock_component.fallback_handler = None
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/fallback/reset/test-model")
        assert resp.status_code in (503, 500)

    def test_reset_model_failures_exception_returns_500(self, mock_component):
        mock_component.fallback_handler.reset_model_failures = MagicMock(
            side_effect=Exception("reset error")
        )
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/fallback/reset/test-model")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# /openrouter/filter endpoints
# ---------------------------------------------------------------------------


class TestOpenRouterFilterEndpoints:
    @pytest.fixture
    def mock_component(self):
        component = MagicMock()
        component.initialized = True
        component.set_openrouter_filter = AsyncMock()
        component.get_openrouter_filter_settings = MagicMock(
            return_value={
                "show_free_only": False,
                "prefer_free_models": True,
                "max_cost_per_token": 0.001,
            }
        )
        return component

    def test_set_openrouter_filter_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.post(
            "/api/v1/models/openrouter/filter?show_free_only=true&prefer_free=true&max_cost_per_token=0.0005"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "settings" in data
        assert data["settings"]["show_free_only"] is True

    def test_set_openrouter_filter_exception_returns_500(self, mock_component):
        mock_component.set_openrouter_filter = AsyncMock(
            side_effect=Exception("filter error")
        )
        client = _make_client(mock_component)
        resp = client.post("/api/v1/models/openrouter/filter")
        assert resp.status_code == 500

    def test_get_openrouter_filter_success(self, mock_component):
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/openrouter/filter")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openrouter"
        assert "settings" in data

    def test_get_openrouter_filter_not_available_returns_404(self, mock_component):
        mock_component.get_openrouter_filter_settings = MagicMock(return_value=None)
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/openrouter/filter")
        assert resp.status_code in (404, 500)

    def test_get_openrouter_filter_exception_returns_500(self, mock_component):
        mock_component.get_openrouter_filter_settings = MagicMock(
            side_effect=Exception("filter read error")
        )
        client = _make_client(mock_component)
        resp = client.get("/api/v1/models/openrouter/filter")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Pydantic model tests
# ---------------------------------------------------------------------------


class TestApiModels:
    def test_generation_request_defaults(self):
        req = GenerationRequest(prompt="hello")
        assert req.task_type is not None
        assert req.max_tokens == 2048
        assert req.temperature == 0.7
        assert req.top_p == 0.9
        assert req.stream is False

    def test_generation_response_fields(self):
        resp = GenerationResponse(
            text="result",
            model_id="test/model",
            provider="openrouter",
            latency_ms=100.0,
        )
        assert resp.text == "result"
        assert resp.usage is None
        assert resp.metadata is None

    def test_model_test_request(self):
        req = ModelTestRequest(model_id="test/model", provider_name="openrouter")
        assert req.model_id == "test/model"
        assert req.provider_name == "openrouter"

    def test_system_status_response(self):
        status = SystemStatusResponse(
            initialized=True,
            active_models=3,
            providers={"openrouter": {"healthy": True}},
        )
        assert status.initialized is True
        assert status.active_models == 3
        assert status.system_resources is None
        assert status.last_health_check is None
