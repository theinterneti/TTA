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
