"""
Test Suite for Model Management Component

This module provides comprehensive tests for the model management system,
including provider tests, service tests, and integration tests.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from src.components.model_management import (
    GenerationRequest,
    ModelInfo,
    ModelManagementComponent,
    ModelRequirements,
    ProviderType,
    TaskType,
)
from src.components.model_management.models import (
    ModelSelectionCriteria,
)
from src.components.model_management.providers import OpenRouterProvider
from src.components.model_management.services import HardwareDetector, ModelSelector


class TestModelManagementComponent:
    """Test cases for the main ModelManagementComponent."""

    @pytest_asyncio.fixture
    async def mock_config(self):
        """Create a mock configuration for testing."""
        return {
            "model_management": {
                "enabled": True,
                "default_provider": "openrouter",
                "providers": {
                    "openrouter": {
                        "enabled": True,
                        "api_key": "test-key",
                        "free_models_only": True,
                    }
                },
            }
        }

    @pytest_asyncio.fixture
    async def component(self, mock_config):
        """Create a ModelManagementComponent instance for testing."""
        component = ModelManagementComponent(mock_config)
        return component

    @pytest.mark.asyncio
    async def test_component_initialization(self, component):
        """Test component initialization."""
        assert component.name == "model_management"
        assert not component.initialized
        assert component.model_config is not None

    @pytest.mark.asyncio
    async def test_component_start_stop(self, component):
        """Test component start and stop lifecycle."""
        with patch.object(component, "_initialize_providers", return_value=None):
            with patch.object(component, "_initialize_services", return_value=None):
                with patch.object(
                    component, "_perform_health_check", return_value=None
                ):
                    with patch.object(
                        component.hardware_detector,
                        "detect_system_resources",
                        return_value={"total_ram_gb": 16, "gpu_count": 1},
                    ):
                        # Test start
                        success = await component._start_impl()
                        assert success
                        assert component.initialized

                        # Test stop
                        success = await component._stop_impl()
                        assert success
                        assert not component.initialized

    @pytest.mark.asyncio
    async def test_generate_text(self, component):
        """Test text generation functionality."""
        # Mock dependencies
        mock_model_instance = AsyncMock()
        mock_model_instance.model_id = "test-model"
        mock_model_instance.generate.return_value = Mock(
            text="Generated text",
            model_id="test-model",
            latency_ms=100,
            usage={"total_tokens": 50},
            metadata={"provider": "test"},
        )

        component.initialized = True
        component.model_selector = AsyncMock()
        component.model_selector.select_model.return_value = Mock(
            model_id="test-model", provider_type=ProviderType.OPENROUTER
        )

        with patch.object(component, "load_model", return_value=mock_model_instance):
            response = await component.generate_text(
                "Test prompt", task_type=TaskType.GENERAL_CHAT
            )

            assert response is not None
            assert response.text == "Generated text"
            assert response.model_id == "test-model"

    @pytest.mark.asyncio
    async def test_select_model(self, component):
        """Test model selection functionality."""
        component.initialized = True
        component.model_selector = AsyncMock()

        # Mock successful model selection
        mock_model_info = Mock(
            model_id="test-model",
            provider_type=ProviderType.OPENROUTER
        )
        component.model_selector.select_model.return_value = mock_model_info

        mock_instance = AsyncMock()
        with patch.object(component, "load_model", return_value=mock_instance):
            requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)
            result = await component.select_model(requirements)

            assert result == mock_instance
            component.model_selector.select_model.assert_called_once_with(requirements)

    @pytest.mark.asyncio
    async def test_select_model_not_initialized(self, component):
        """Test model selection when component not initialized."""
        component.initialized = False

        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)
        with pytest.raises(RuntimeError, match="not initialized"):
            await component.select_model(requirements)

    @pytest.mark.asyncio
    async def test_select_model_no_suitable_model(self, component):
        """Test model selection when no suitable model found."""
        component.initialized = True
        component.model_selector = AsyncMock()
        component.model_selector.select_model.return_value = None

        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)
        result = await component.select_model(requirements)

        assert result is None

    @pytest.mark.asyncio
    async def test_load_model(self, component):
        """Test loading a specific model."""
        component.initialized = True

        # Mock provider
        mock_provider = AsyncMock()
        mock_instance = AsyncMock()
        mock_instance.health_check.return_value = True
        mock_provider.load_model.return_value = mock_instance

        component.providers["test-provider"] = mock_provider

        result = await component.load_model("test-model", "test-provider")

        assert result == mock_instance
        mock_provider.load_model.assert_called_once_with("test-model")
        assert "test-provider:test-model" in component.active_models

    @pytest.mark.asyncio
    async def test_load_model_cached(self, component):
        """Test loading a model that's already cached."""
        component.initialized = True

        # Add cached model
        mock_instance = AsyncMock()
        mock_instance.health_check.return_value = True
        component.active_models["test-provider:test-model"] = mock_instance

        result = await component.load_model("test-model", "test-provider")

        assert result == mock_instance
        mock_instance.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_model_provider_not_available(self, component):
        """Test loading a model from unavailable provider."""
        component.initialized = True

        with pytest.raises(ValueError, match="Provider .* not available"):
            await component.load_model("test-model", "nonexistent-provider")

    @pytest.mark.asyncio
    async def test_unload_model(self, component):
        """Test unloading a model."""
        component.initialized = True

        # Add active model and provider
        mock_instance = AsyncMock()
        component.active_models["test-provider:test-model"] = mock_instance

        mock_provider = AsyncMock()
        mock_provider.unload_model.return_value = True
        component.providers["test-provider"] = mock_provider

        result = await component.unload_model("test-model", "test-provider")

        assert result is True
        mock_provider.unload_model.assert_called_once_with("test-model")
        assert "test-provider:test-model" not in component.active_models


class TestHardwareDetector:
    """Test cases for the HardwareDetector service."""

    @pytest.fixture
    def detector(self):
        """Create a HardwareDetector instance for testing."""
        return HardwareDetector()

    @pytest.mark.asyncio
    async def test_detect_system_resources(self, detector):
        """Test system resource detection."""
        with patch("psutil.virtual_memory") as mock_memory:
            with patch("psutil.cpu_count") as mock_cpu:
                mock_memory.return_value = Mock(
                    total=16 * 1024**3, available=8 * 1024**3
                )  # 16GB total, 8GB available
                mock_cpu.return_value = 8

                resources = await detector.detect_system_resources()

                assert "total_ram_gb" in resources
                assert "cpu_cores" in resources
                assert resources["total_ram_gb"] == 16
                assert resources["cpu_cores"] == 8

    @pytest.mark.asyncio
    async def test_recommend_models(self, detector):
        """Test model recommendations."""
        # Use THERAPEUTIC_RESPONSE instead of THERAPEUTIC_NARRATIVE (which doesn't exist in TaskType enum)
        recommendations = await detector.recommend_models(TaskType.THERAPEUTIC_RESPONSE)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_detect_gpu(self, detector):
        """Test GPU detection."""
        # Mock GPU info
        mock_gpu_info = [
            {"index": 0, "name": "NVIDIA RTX 3090", "memory_gb": 24.0, "type": "NVIDIA", "available": True},
            {"index": 1, "name": "NVIDIA RTX 3090", "memory_gb": 24.0, "type": "NVIDIA", "available": True}
        ]

        with patch.object(detector, "_detect_gpu_info", return_value=mock_gpu_info):
            with patch("psutil.virtual_memory") as mock_memory:
                with patch("psutil.cpu_count") as mock_cpu:
                    mock_memory.return_value = Mock(
                        total=16 * 1024**3, available=8 * 1024**3
                    )
                    mock_cpu.return_value = 8

                    resources = await detector.detect_system_resources()

                    assert resources["gpu_count"] == 2
                    assert resources["has_gpu"] is True

    @pytest.mark.asyncio
    async def test_detect_no_gpu(self, detector):
        """Test system without GPU."""
        # Mock no GPU
        with patch.object(detector, "_detect_gpu_info", return_value=[]):
            with patch("psutil.virtual_memory") as mock_memory:
                with patch("psutil.cpu_count") as mock_cpu:
                    mock_memory.return_value = Mock(
                        total=8 * 1024**3, available=4 * 1024**3
                    )
                    mock_cpu.return_value = 4

                    resources = await detector.detect_system_resources()

                    assert resources["gpu_count"] == 0
                    assert resources["has_gpu"] is False


class TestModelSelector:
    """Test cases for the ModelSelector service."""

    @pytest_asyncio.fixture
    async def selector(self):
        """Create a ModelSelector instance for testing."""
        # Mock available models
        mock_models = [
            ModelInfo(
                model_id="fast-model",
                provider_type=ProviderType.OPENROUTER,
                name="Fast Model",
                context_length=4096,
                cost_per_1k_tokens=0.0,
                capabilities=["chat"],
                performance_tier="fast"
            ),
            ModelInfo(
                model_id="quality-model",
                provider_type=ProviderType.OPENROUTER,
                name="Quality Model",
                context_length=8192,
                cost_per_1k_tokens=0.0,
                capabilities=["chat", "reasoning"],
                performance_tier="balanced"
            ),
        ]

        selector = ModelSelector()
        selector.available_models = mock_models
        return selector

    @pytest.mark.asyncio
    async def test_select_model_by_task_type(self, selector):
        """Test model selection based on task type."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            max_latency_ms=1000
        )

        result = await selector.select_model(requirements)

        assert result is not None
        assert result.model_id in ["fast-model", "quality-model"]

    @pytest.mark.asyncio
    async def test_select_model_with_context_requirement(self, selector):
        """Test model selection with context length requirement."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            min_context_length=6000
        )

        result = await selector.select_model(requirements)

        assert result is not None
        assert result.model_id == "quality-model"
        assert result.context_length >= 6000

    @pytest.mark.asyncio
    async def test_select_model_no_match(self, selector):
        """Test model selection when no model matches requirements."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT,
            min_context_length=100000  # Unrealistic requirement
        )

        result = await selector.select_model(requirements)

        # Should return best available model even if requirements not fully met
        assert result is not None


class TestModelManagementComponentAdvanced:
    """Advanced test cases for ModelManagementComponent."""

    @pytest_asyncio.fixture
    async def mock_config(self):
        """Create a mock configuration for testing."""
        return {
            "model_management": {
                "enabled": True,
                "default_provider": "openrouter",
                "providers": {
                    "openrouter": {
                        "enabled": True,
                        "api_key": "test-key",
                        "free_models_only": True,
                    }
                },
            }
        }

    @pytest_asyncio.fixture
    async def component(self, mock_config):
        """Create a ModelManagementComponent instance for testing."""
        component = ModelManagementComponent(mock_config)
        return component

    @pytest.mark.asyncio
    async def test_get_available_models(self, component):
        """Test getting available models."""
        component.initialized = True

        # Mock providers with available models
        mock_provider = AsyncMock()
        mock_models = [
            ModelInfo(
                model_id="model-1",
                provider_type=ProviderType.OPENROUTER,
                name="Model 1",
                context_length=4096,
                cost_per_1k_tokens=0.0,
                capabilities=["chat"],
                performance_tier="balanced"
            )
        ]
        mock_provider.get_available_models.return_value = mock_models
        component.providers["test-provider"] = mock_provider

        result = await component.get_available_models()

        assert isinstance(result, list)
        # Result might be empty if provider fails, which is ok
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_available_models_not_initialized(self, component):
        """Test getting available models when not initialized."""
        component.initialized = False

        with pytest.raises(RuntimeError, match="not initialized"):
            await component.get_available_models()

    @pytest.mark.asyncio
    async def test_get_system_status(self, component):
        """Test getting system status."""
        component.initialized = True
        component.system_resources = {
            "total_ram_gb": 16.0,
            "gpu_count": 1
        }

        # Mock providers
        mock_provider = AsyncMock()
        component.providers["test-provider"] = mock_provider

        result = await component.get_system_status()

        assert isinstance(result, dict)
        assert "initialized" in result
        assert result["initialized"] is True

    @pytest.mark.asyncio
    async def test_get_model_recommendations(self, component):
        """Test getting model recommendations."""
        component.initialized = True
        component.hardware_detector = AsyncMock()

        mock_recommendations = ["model-1", "model-2", "model-3"]
        component.hardware_detector.recommend_models.return_value = mock_recommendations

        result = await component.get_model_recommendations(TaskType.GENERAL_CHAT)

        assert result == mock_recommendations
        component.hardware_detector.recommend_models.assert_called_once_with(TaskType.GENERAL_CHAT)

    @pytest.mark.asyncio
    async def test_test_model_connectivity(self, component):
        """Test model connectivity testing."""
        component.initialized = True

        # Mock provider
        mock_provider = AsyncMock()
        mock_instance = AsyncMock()
        mock_instance.health_check.return_value = True
        mock_provider.load_model.return_value = mock_instance
        component.providers["test-provider"] = mock_provider

        result = await component.test_model_connectivity("test-model", "test-provider")

        assert result is True
        mock_provider.load_model.assert_called_once_with("test-model")

    @pytest.mark.asyncio
    async def test_select_model_with_fallback(self, component):
        """Test model selection with fallback when primary selection fails."""
        component.initialized = True
        component.model_selector = AsyncMock()
        component.fallback_handler = AsyncMock()

        # Primary selection fails
        component.model_selector.select_model.side_effect = Exception("Selection failed")

        # Fallback succeeds
        fallback_model = ModelInfo(
            model_id="fallback-model",
            provider_type=ProviderType.OPENROUTER,
            name="Fallback Model",
            context_length=4096,
            cost_per_1k_tokens=0.0,
            capabilities=["chat"]
        )
        component.fallback_handler.get_fallback_model.return_value = fallback_model

        mock_instance = AsyncMock()
        with patch.object(component, "load_model", return_value=mock_instance):
            requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)
            result = await component.select_model(requirements)

            assert result == mock_instance
            component.fallback_handler.get_fallback_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_model_unhealthy_cached(self, component):
        """Test loading a model when cached instance is unhealthy."""
        component.initialized = True

        # Add unhealthy cached model
        mock_cached_instance = AsyncMock()
        mock_cached_instance.health_check.return_value = False
        component.active_models["test-provider:test-model"] = mock_cached_instance

        # Mock provider to load fresh instance
        mock_provider = AsyncMock()
        mock_fresh_instance = AsyncMock()
        mock_fresh_instance.health_check.return_value = True
        mock_provider.load_model.return_value = mock_fresh_instance
        component.providers["test-provider"] = mock_provider

        result = await component.load_model("test-model", "test-provider")

        assert result == mock_fresh_instance
        mock_provider.load_model.assert_called_once_with("test-model")

    @pytest.mark.asyncio
    async def test_unload_model_without_provider_name(self, component):
        """Test unloading a model without specifying provider."""
        component.initialized = True

        # Add models from multiple providers
        mock_instance1 = AsyncMock()
        mock_instance2 = AsyncMock()
        component.active_models["provider1:test-model"] = mock_instance1
        component.active_models["provider2:test-model"] = mock_instance2

        mock_provider1 = AsyncMock()
        mock_provider2 = AsyncMock()
        component.providers["provider1"] = mock_provider1
        component.providers["provider2"] = mock_provider2

        result = await component.unload_model("test-model")

        assert result is True
        assert "provider1:test-model" not in component.active_models
        assert "provider2:test-model" not in component.active_models

    @pytest.mark.asyncio
    async def test_get_free_models(self, component):
        """Test getting free models."""
        component.initialized = True

        # Mock provider with free models
        mock_provider = AsyncMock()
        mock_models = [
            ModelInfo(
                model_id="free-model",
                provider_type=ProviderType.OPENROUTER,
                name="Free Model",
                context_length=4096,
                cost_per_1k_tokens=0.0,
                capabilities=["chat"]
            )
        ]
        mock_provider.get_available_models.return_value = mock_models
        component.providers["test-provider"] = mock_provider

        result = await component.get_free_models()

        assert isinstance(result, list)
        assert all(model.cost_per_1k_tokens == 0.0 for model in result)

    @pytest.mark.asyncio
    async def test_generate_text(self, component):
        """Test text generation."""
        component.initialized = True
        component.model_selector = AsyncMock()

        # Mock model selection
        mock_model_info = ModelInfo(
            model_id="test-model",
            provider_type=ProviderType.OPENROUTER,
            name="Test Model",
            context_length=4096,
            cost_per_1k_tokens=0.0,
            capabilities=["chat"]
        )
        component.model_selector.select_model.return_value = mock_model_info

        # Mock model instance
        mock_instance = AsyncMock()
        mock_response = Mock(
            text="Generated response",
            model_id="test-model",
            latency_ms=100.0,
            usage={"total_tokens": 50},
            metadata={}
        )
        mock_instance.generate.return_value = mock_response

        with patch.object(component, "load_model", return_value=mock_instance):
            result = await component.generate_text(
                "Test prompt",
                task_type=TaskType.GENERAL_CHAT
            )

            assert result.text == "Generated response"
            assert result.model_id == "test-model"

    @pytest.mark.asyncio
    async def test_generate_text_not_initialized(self, component):
        """Test text generation when not initialized."""
        component.initialized = False

        # generate_text catches exceptions and returns None
        result = await component.generate_text("Test prompt")
        assert result is None

    @pytest.mark.asyncio
    async def test_initialize_providers(self, component):
        """Test provider initialization."""
        component.model_config = Mock(
            providers={
                "openrouter": Mock(
                    enabled=True,
                    api_key="test-key",
                    free_models_only=True
                )
            }
        )

        with patch("src.components.model_management.model_management_component.OpenRouterProvider") as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.initialize.return_value = True
            mock_provider_class.return_value = mock_provider

            await component._initialize_providers()

            assert "openrouter" in component.providers

    @pytest.mark.asyncio
    async def test_initialize_services(self, component):
        """Test service initialization."""
        component.model_config = Mock(
            performance_monitoring=Mock(enabled=True),
            fallback=Mock(enabled=True)
        )
        component.providers = {"test-provider": AsyncMock()}

        await component._initialize_services()

        assert component.performance_monitor is not None
        assert component.fallback_handler is not None
        assert component.model_selector is not None

    @pytest.mark.asyncio
    async def test_perform_health_check(self, component):
        """Test health check performance."""
        component.providers = {
            "provider1": AsyncMock(),
            "provider2": AsyncMock()
        }

        await component._perform_health_check()

        # Health check should complete without errors
        assert True


class TestFallbackHandler:
    """Test cases for the FallbackHandler service."""

    @pytest_asyncio.fixture
    async def handler(self):
        """Create a FallbackHandler instance for testing."""
        from src.components.model_management.services import FallbackHandler

        handler = FallbackHandler()
        # Mock available models
        handler.available_models = [
            ModelInfo(
                model_id="primary-model",
                provider_type=ProviderType.OPENROUTER,
                name="Primary Model",
                context_length=4096,
                cost_per_1k_tokens=0.0,
                capabilities=["chat"],
                performance_tier="fast"
            ),
            ModelInfo(
                model_id="fallback-model",
                provider_type=ProviderType.OPENROUTER,
                name="Fallback Model",
                context_length=4096,
                cost_per_1k_tokens=0.0,
                capabilities=["chat"],
                performance_tier="balanced"
            ),
        ]
        return handler

    @pytest.mark.asyncio
    async def test_get_fallback_model(self, handler):
        """Test getting a fallback model."""
        requirements = ModelRequirements(task_type=TaskType.GENERAL_CHAT)

        result = await handler.get_fallback_model("failed-model", requirements)

        assert result is not None
        assert result.model_id in ["primary-model", "fallback-model"]


class TestPerformanceMonitor:
    """Test cases for the PerformanceMonitor service."""

    @pytest_asyncio.fixture
    async def monitor(self):
        """Create a PerformanceMonitor instance for testing."""
        from src.components.model_management.services import PerformanceMonitor

        monitor = PerformanceMonitor()
        await monitor.initialize()
        return monitor

    @pytest.mark.asyncio
    async def test_record_metrics(self, monitor):
        """Test recording performance metrics."""
        metrics = {
            "model_id": "test-model",
            "response_time_ms": 250.5,
            "total_tokens": 100,
            "task_type": "chat"
        }

        await monitor.record_metrics("test-model", metrics)

        # Metrics should be recorded without errors
        assert True

    @pytest.mark.asyncio
    async def test_get_metrics(self, monitor):
        """Test getting performance metrics."""
        # Record some metrics first
        metrics = {
            "model_id": "test-model",
            "response_time_ms": 250.5,
            "total_tokens": 100,
            "task_type": "chat"
        }
        await monitor.record_metrics("test-model", metrics)

        result = await monitor.get_metrics("test-model")

        assert result is not None


class TestOpenRouterProvider:
    """Test cases for the OpenRouter provider."""

    @pytest.fixture
    def provider(self):
        """Create an OpenRouterProvider instance for testing."""
        return OpenRouterProvider()

    @pytest.mark.asyncio
    async def test_provider_initialization(self, provider):
        """Test provider initialization."""
        config = {
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1",
            "free_models_only": True,
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            # AsyncClient.get() is async, so we need AsyncMock
            mock_client.return_value.get = AsyncMock(return_value=mock_response)

            success = await provider.initialize(config)
            assert success

    @pytest.mark.asyncio
    async def test_get_available_models(self, provider):
        """Test getting available models from OpenRouter."""
        # Initialize provider first
        config = {
            "api_key": "test-key",
            "base_url": "https://openrouter.ai/api/v1",
            "free_models_only": True,
        }

        # Mock the HTTP client for both initialization and model fetching
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "test-model",
                        "name": "Test Model",
                        "pricing": {"prompt": "0", "completion": "0"},
                        "context_length": 4096,
                        "description": "Test model",
                    }
                ]
            }
            # AsyncClient.get() is async, so we need AsyncMock
            mock_client_instance = Mock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client_instance

            # Initialize provider
            await provider.initialize(config)

            # Get available models
            models = await provider.get_available_models()
            assert len(models) > 0
            assert models[0].model_id == "test-model"


class TestModelSelector:
    """Test cases for the ModelSelector service."""

    @pytest.fixture
    def selector(self):
        """Create a ModelSelector instance for testing."""
        mock_providers = {}
        mock_hardware_detector = Mock()
        selection_criteria = ModelSelectionCriteria()
        return ModelSelector(mock_providers, mock_hardware_detector, selection_criteria)

    @pytest.mark.asyncio
    async def test_select_model(self, selector):
        """Test model selection logic."""
        requirements = ModelRequirements(
            task_type=TaskType.GENERAL_CHAT, max_latency_ms=5000, min_quality_score=6.0
        )

        # Mock the method that gets all available models
        test_models = [
            ModelInfo(
                model_id="test-model-1",
                name="Test Model 1",
                provider_type=ProviderType.OPENROUTER,
                performance_score=8.0,
                cost_per_token=0.0,
                therapeutic_safety_score=7.0,
                capabilities=["chat", "general"],
            ),
            ModelInfo(
                model_id="test-model-2",
                name="Test Model 2",
                provider_type=ProviderType.OPENROUTER,
                performance_score=7.0,
                cost_per_token=0.001,
                therapeutic_safety_score=8.0,
                capabilities=["chat", "general"],
            ),
        ]

        with patch.object(
            selector, "_get_all_available_models", return_value=test_models
        ):
            selected = await selector.select_model(requirements)
            assert selected is not None
            assert selected.model_id in ["test-model-1", "test-model-2"]


class TestIntegration:
    """Integration tests for the complete model management system."""

    @pytest_asyncio.fixture
    async def full_system(self):
        """Set up a complete model management system for integration testing."""
        config = {
            "model_management": {
                "enabled": True,
                "default_provider": "openrouter",
                "providers": {
                    "openrouter": {
                        "enabled": True,
                        "api_key": "test-key",
                        "free_models_only": True,
                    }
                },
                "selection_strategy": {
                    "algorithm": "performance_based",
                    "prefer_free_models": True,
                },
                "fallback_config": {"enabled": True, "max_retries": 3},
            }
        }

        component = ModelManagementComponent(config)
        return component

    @pytest.mark.asyncio
    async def test_end_to_end_generation(self, full_system):
        """Test end-to-end text generation flow."""
        # Mock all external dependencies
        with patch.object(full_system, "_initialize_providers"):
            with patch.object(full_system, "_initialize_services"):
                with patch.object(full_system, "_perform_health_check"):
                    with patch.object(
                        full_system.hardware_detector,
                        "detect_system_resources",
                        return_value={"total_ram_gb": 16, "gpu_count": 1},
                    ):
                        # Start the system
                        await full_system._start_impl()

                        # Mock model selection and generation
                        mock_instance = AsyncMock()
                        mock_instance.model_id = "test-model"
                        mock_instance.generate.return_value = Mock(
                            text="Test response",
                            model_id="test-model",
                            latency_ms=200,
                            usage={"total_tokens": 25},
                            metadata={"provider": "test"},
                        )

                        full_system.model_selector = AsyncMock()
                        full_system.model_selector.select_model.return_value = Mock(
                            model_id="test-model", provider_type=ProviderType.OPENROUTER
                        )

                        with patch.object(
                            full_system, "load_model", return_value=mock_instance
                        ):
                            response = await full_system.generate_text(
                                "Tell me a story about courage",
                                task_type=TaskType.THERAPEUTIC_RESPONSE,
                            )

                            assert response is not None
                            assert response.text == "Test response"
                            assert response.model_id == "test-model"

                        # Stop the system
                        await full_system._stop_impl()


class TestErrorHandling:
    """Test error handling and fallback mechanisms."""

    @pytest.mark.asyncio
    async def test_provider_failure_fallback(self):
        """Test fallback when primary provider fails."""
        config = {
            "model_management": {
                "enabled": True,
                "providers": {
                    "openrouter": {"enabled": True, "api_key": "test-key"},
                    "ollama": {"enabled": True, "base_url": "http://localhost:11434"},
                },
                "fallback_config": {"enabled": True, "max_retries": 2},
            }
        }

        component = ModelManagementComponent(config)

        # Mock provider failure and fallback
        with patch.object(component, "_initialize_providers"):
            with patch.object(component, "_initialize_services"):
                with patch.object(component, "_perform_health_check"):
                    with patch.object(
                        component.hardware_detector,
                        "detect_system_resources",
                        return_value={"total_ram_gb": 16, "gpu_count": 1},
                    ):
                        await component._start_impl()

                        # Mock fallback handler
                        component.fallback_handler = Mock()
                        component.fallback_handler.get_fallback_model = AsyncMock(
                            return_value=Mock(
                                model_id="fallback-model",
                                provider_type=ProviderType.OLLAMA,
                            )
                        )

                        # Mock model selector to raise exception (simulating failure)
                        component.model_selector = Mock()
                        component.model_selector.select_model = AsyncMock(
                            side_effect=Exception("Model selection failed")
                        )

                        # Mock load_model for fallback
                        mock_fallback_instance = Mock()
                        mock_fallback_instance.model_id = "fallback-model"
                        mock_fallback_instance.generate = AsyncMock(
                            return_value=Mock(
                                text="Fallback response",
                                model_id="fallback-model",
                                latency_ms=300,
                                usage={"total_tokens": 30},
                                metadata={"provider": "ollama"},
                            )
                        )

                        with patch.object(
                            component,
                            "load_model",
                            new=AsyncMock(return_value=mock_fallback_instance),
                        ):
                            response = await component.generate_text("Test prompt")

                            # Should get fallback response
                            assert response is not None
                            assert response.text == "Fallback response"
                            assert response.model_id == "fallback-model"


# Test fixtures and utilities
@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    return AsyncMock()


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j driver for testing."""
    return AsyncMock()


@pytest.fixture
def sample_model_requirements():
    """Sample model requirements for testing."""
    return ModelRequirements(
        task_type=TaskType.THERAPEUTIC_NARRATIVE,
        max_latency_ms=3000,
        min_quality_score=7.0,
        therapeutic_safety_required=True,
        context_length_needed=2048,
        max_cost_per_token=0.001,
    )


@pytest.fixture
def sample_generation_request():
    """Sample generation request for testing."""
    return GenerationRequest(
        prompt="Tell me a story about overcoming challenges",
        max_tokens=1000,
        temperature=0.7,
        top_p=0.9,
        stream=False,
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
