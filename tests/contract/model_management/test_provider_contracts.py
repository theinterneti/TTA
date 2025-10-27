"""
Contract Tests for Model Provider Interfaces.

Validates that all providers (OpenRouter, Local, Ollama, etc.) conform to the
IModelProvider interface contract and return consistent response formats.
"""

import inspect
from abc import ABC
from typing import get_type_hints

import pytest
from tta_ai.models.interfaces import IModelProvider, ModelInfo
from tta_ai.models.providers.openrouter import OpenRouterProvider

# ============================================================================
# Contract Test Base Class
# ============================================================================


class ProviderContractTestBase(ABC):
    """Base class for provider contract tests."""

    provider_class = None  # Override in subclasses

    def get_provider_instance(self):
        """Get an instance of the provider for testing."""
        raise NotImplementedError("Subclasses must implement get_provider_instance")

    @pytest.mark.contract
    def test_implements_imodel_provider_interface(self):
        """Contract: Provider implements IModelProvider interface."""
        assert issubclass(self.provider_class, IModelProvider), (
            f"{self.provider_class.__name__} must implement IModelProvider"
        )

    @pytest.mark.contract
    def test_has_required_methods(self):
        """Contract: Provider has all required interface methods."""
        required_methods = [
            "get_available_models",
            "initialize",
            "load_model",
            "unload_model",
            "cleanup",
        ]

        provider_methods = [
            method for method in dir(self.provider_class) if not method.startswith("_")
        ]

        for method in required_methods:
            assert method in provider_methods, (
                f"{self.provider_class.__name__} missing required method: {method}"
            )

    @pytest.mark.contract
    def test_get_available_models_signature(self):
        """Contract: get_available_models has correct signature."""
        method = self.provider_class.get_available_models

        # Check it's a coroutine (async method)
        assert inspect.iscoroutinefunction(method), "get_available_models must be async"

        # Check return type hint
        type_hints = get_type_hints(method)
        assert "return" in type_hints, "get_available_models must have return type hint"

    @pytest.mark.contract
    def test_initialize_signature(self):
        """Contract: initialize method has correct signature."""
        method = self.provider_class.initialize

        # Check it's a coroutine (async method)
        assert inspect.iscoroutinefunction(method), "initialize must be async"

        # Check it has required parameters
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert "config" in params, "initialize must have 'config' parameter"

    @pytest.mark.contract
    def test_load_model_signature(self):
        """Contract: load_model method has correct signature."""
        method = self.provider_class.load_model

        # Check it's a coroutine (async method)
        assert inspect.iscoroutinefunction(method), "load_model must be async"

        # Check it has required parameters
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        assert "model_id" in params, "load_model must have 'model_id' parameter"

    @pytest.mark.contract
    def test_unload_model_signature(self):
        """Contract: unload_model method has correct signature."""
        method = self.provider_class.unload_model

        # Check it's a coroutine (async method)
        assert inspect.iscoroutinefunction(method), "unload_model must be async"

        # Check return type
        type_hints = get_type_hints(method)
        if "return" in type_hints:
            assert (
                type_hints["return"] == bool or str(type_hints["return"]) == "bool"
            ), "unload_model must return bool"

    @pytest.mark.contract
    @pytest.mark.asyncio
    async def test_get_available_models_returns_list(self):
        """Contract: get_available_models returns list of ModelInfo."""
        provider = self.get_provider_instance()

        try:
            models = await provider.get_available_models()

            # Should return a list
            assert isinstance(models, list), "get_available_models must return a list"

            # All items should be ModelInfo instances
            for model in models:
                assert isinstance(model, ModelInfo), (
                    f"All models must be ModelInfo instances, got {type(model)}"
                )

                # Verify required ModelInfo fields
                assert hasattr(model, "model_id"), "ModelInfo must have model_id"
                assert hasattr(model, "name"), "ModelInfo must have name"
                assert hasattr(model, "provider_type"), (
                    "ModelInfo must have provider_type"
                )

        except Exception as e:
            # If provider requires configuration or initialization, that's acceptable
            if (
                "configuration" in str(e).lower()
                or "api" in str(e).lower()
                or "not initialized" in str(e).lower()
                or "initialize" in str(e).lower()
            ):
                pytest.skip(f"Provider requires configuration/initialization: {e}")
            else:
                raise

    @pytest.mark.contract
    @pytest.mark.asyncio
    async def test_initialize_returns_bool(self):
        """Contract: initialize returns boolean."""
        provider = self.get_provider_instance()

        try:
            result = await provider.initialize({})

            assert isinstance(result, bool), "initialize must return boolean value"

        except Exception as e:
            # Some providers may require specific config
            if "configuration" in str(e).lower() or "api" in str(e).lower():
                pytest.skip(f"Provider requires configuration: {e}")
            else:
                raise


# ============================================================================
# OpenRouter Provider Contract Tests
# ============================================================================


@pytest.mark.contract
class TestOpenRouterProviderContract(ProviderContractTestBase):
    """Contract tests for OpenRouter provider."""

    provider_class = OpenRouterProvider

    def get_provider_instance(self):
        """Get OpenRouter provider instance."""
        # Create provider instance (no constructor params needed)
        return OpenRouterProvider()

    @pytest.mark.contract
    def test_openrouter_specific_attributes(self):
        """Contract: OpenRouter provider has specific attributes."""
        provider = self.get_provider_instance()

        # OpenRouter-specific attributes (private)
        assert hasattr(provider, "_api_key"), "OpenRouter must have _api_key"
        assert hasattr(provider, "_base_url"), "OpenRouter must have _base_url"
        assert hasattr(provider, "_show_free_only"), (
            "OpenRouter must have _show_free_only"
        )

    @pytest.mark.contract
    @pytest.mark.asyncio
    async def test_openrouter_model_info_format(self):
        """Contract: OpenRouter returns properly formatted ModelInfo."""
        provider = self.get_provider_instance()

        try:
            models = await provider.get_available_models()

            if models:  # If we got models
                model = models[0]

                # Verify OpenRouter-specific fields
                assert model.provider_type.value == "openrouter"
                assert model.model_id is not None
                assert len(model.model_id) > 0

        except Exception as e:
            # Skip if API key is invalid or provider not initialized (expected in testing)
            if (
                "api" in str(e).lower()
                or "auth" in str(e).lower()
                or "not initialized" in str(e).lower()
                or "initialize" in str(e).lower()
            ):
                pytest.skip(f"Provider requires initialization/authentication: {e}")
            else:
                raise


# ============================================================================
# Contract Test Suite for All Providers
# ============================================================================


@pytest.mark.contract
class TestAllProvidersConformToContract:
    """Verify all providers conform to the IModelProvider contract."""

    @pytest.mark.contract
    def test_all_providers_implement_interface(self):
        """Contract: All provider classes implement IModelProvider."""
        # List of all provider classes
        provider_classes = [
            OpenRouterProvider,
            # Add other providers as they are implemented:
            # LocalModelProvider,
            # OllamaProvider,
            # LMStudioProvider,
            # CustomAPIProvider,
        ]

        for provider_class in provider_classes:
            assert issubclass(provider_class, IModelProvider), (
                f"{provider_class.__name__} must implement IModelProvider"
            )

    @pytest.mark.contract
    def test_all_providers_have_consistent_method_signatures(self):
        """Contract: All providers have consistent method signatures."""
        provider_classes = [
            OpenRouterProvider,
            # Add other providers as they are implemented
        ]

        # Get method signatures from first provider as reference
        if not provider_classes:
            pytest.skip("No providers to test")

        reference_provider = provider_classes[0]
        reference_methods = {
            "get_available_models": inspect.signature(
                reference_provider.get_available_models
            ),
            "initialize": inspect.signature(reference_provider.initialize),
            "load_model": inspect.signature(reference_provider.load_model),
            "unload_model": inspect.signature(reference_provider.unload_model),
        }

        # Verify all other providers have matching signatures
        for provider_class in provider_classes[1:]:
            for method_name, reference_sig in reference_methods.items():
                provider_method = getattr(provider_class, method_name)
                provider_sig = inspect.signature(provider_method)

                # Compare parameter names (excluding 'self')
                ref_params = [p for p in reference_sig.parameters if p != "self"]
                prov_params = [p for p in provider_sig.parameters if p != "self"]

                assert ref_params == prov_params, (
                    f"{provider_class.__name__}.{method_name} has different parameters than reference"
                )


# ============================================================================
# Response Format Contract Tests
# ============================================================================


@pytest.mark.contract
class TestProviderResponseFormats:
    """Test that provider responses conform to expected formats."""

    @pytest.mark.contract
    @pytest.mark.asyncio
    async def test_model_info_has_required_fields(self):
        """Contract: ModelInfo objects have all required fields."""
        # Create a sample ModelInfo to verify structure
        from tta_ai.models import ProviderType

        model = ModelInfo(
            model_id="test-model",
            name="Test Model",
            provider_type=ProviderType.OPENROUTER,
            description="Test description",
            context_length=4000,
            cost_per_token=0.001,
            is_free=False,
            capabilities=["chat"],
            therapeutic_safety_score=7.5,
            performance_score=8.0,
        )

        # Verify all required fields exist
        required_fields = [
            "model_id",
            "name",
            "provider_type",
            "description",
            "context_length",
            "cost_per_token",
            "is_free",
            "capabilities",
        ]

        for field in required_fields:
            assert hasattr(model, field), f"ModelInfo must have required field: {field}"

    @pytest.mark.contract
    def test_provider_type_enum_values(self):
        """Contract: ProviderType enum has expected values."""
        from tta_ai.models import ProviderType

        expected_types = [
            "openrouter",
            "local",
            "ollama",
            "lm_studio",
            "custom_api",
        ]

        for expected_type in expected_types:
            assert any(pt.value == expected_type for pt in ProviderType), (
                f"ProviderType must include: {expected_type}"
            )
