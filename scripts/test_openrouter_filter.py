#!/usr/bin/env python3
"""
OpenRouter Free Models Filter Validation Script

This script validates that the OpenRouter provider can be imported
and configured with free models filtering capabilities.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all required modules can be imported."""

    try:
        # Test basic imports
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import ProviderConfig
        from components.model_management.providers.openrouter import OpenRouterProvider

        return True
    except ImportError:
        return False


def test_provider_configuration():
    """Test OpenRouter provider configuration with filter settings."""

    try:
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import ProviderConfig
        from components.model_management.providers.openrouter import OpenRouterProvider

        # Create a test configuration
        config = ProviderConfig(
            provider_type=ProviderType.OPENROUTER,
            api_key="test_key",
            base_url="https://openrouter.ai",
        )

        # Create provider instance
        provider = OpenRouterProvider(config)

        # Test that the provider has the expected methods
        expected_methods = [
            "get_available_models",
            "get_free_models",
            "get_affordable_models",
            "set_free_models_filter",
            "get_filter_settings",
            "_get_bool_config",
            "_get_float_config",
        ]

        missing_methods = []
        for method in expected_methods:
            if not hasattr(provider, method):
                missing_methods.append(method)

        return not missing_methods

    except Exception:
        return False


def test_environment_configuration():
    """Test environment variable configuration."""

    # Test environment variables
    test_env_vars = {
        "OPENROUTER_SHOW_FREE_ONLY": "true",
        "OPENROUTER_PREFER_FREE_MODELS": "false",
        "OPENROUTER_MAX_COST_PER_TOKEN": "0.0005",
    }

    # Temporarily set environment variables
    original_values = {}
    for key, value in test_env_vars.items():
        original_values[key] = os.getenv(key)
        os.environ[key] = value

    try:
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import ProviderConfig
        from components.model_management.providers.openrouter import OpenRouterProvider

        # Create provider with environment configuration
        config = ProviderConfig(
            provider_type=ProviderType.OPENROUTER,
            api_key="test_key",
            base_url="https://openrouter.ai",
        )

        provider = OpenRouterProvider(config)

        # Test configuration loading methods
        show_free_only = provider._get_bool_config(
            {}, "show_free_only", "OPENROUTER_SHOW_FREE_ONLY", False
        )
        prefer_free = provider._get_bool_config(
            {}, "prefer_free_models", "OPENROUTER_PREFER_FREE_MODELS", True
        )
        max_cost = provider._get_float_config(
            {}, "max_cost_per_token", "OPENROUTER_MAX_COST_PER_TOKEN", 0.001
        )

        # Verify values
        assert show_free_only, f"Expected True, got {show_free_only}"
        assert not prefer_free, f"Expected False, got {prefer_free}"
        assert max_cost == 0.0005, f"Expected 0.0005, got {max_cost}"

        return True

    except Exception:
        return False

    finally:
        # Restore original environment values
        for key, original_value in original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def test_filter_methods():
    """Test filter methods functionality."""

    try:
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import ProviderConfig
        from components.model_management.providers.openrouter import OpenRouterProvider

        # Create provider
        config = ProviderConfig(
            provider_type=ProviderType.OPENROUTER,
            api_key="test_key",
            base_url="https://openrouter.ai",
        )

        provider = OpenRouterProvider(config)

        # Test filter settings
        provider.set_free_models_filter(
            show_free_only=True, prefer_free=False, max_cost_per_token=0.0005
        )

        # Get filter settings
        settings = provider.get_filter_settings()

        # Verify settings
        expected_settings = {
            "show_free_only": True,
            "prefer_free_models": False,
            "max_cost_per_token": 0.0005,
        }

        for key, expected_value in expected_settings.items():
            if settings.get(key) != expected_value:
                return False

        return True

    except Exception:
        return False


def test_api_integration():
    """Test API integration points."""

    try:
        # Test that API endpoints can be imported
        from components.model_management.api import router

        # Check that the router has the expected endpoints
        routes = [route.path for route in router.routes]

        expected_endpoints = [
            "/free",
            "/affordable",
            "/openrouter/free",
            "/openrouter/filter",
        ]

        missing_endpoints = []
        for endpoint in expected_endpoints:
            # Check if any route contains the endpoint
            if not any(endpoint in route for route in routes):
                missing_endpoints.append(endpoint)

        return not missing_endpoints

    except Exception:
        return False


def main():
    """Run all validation tests."""

    tests = [
        ("Imports", test_imports),
        ("Provider Configuration", test_provider_configuration),
        ("Environment Configuration", test_environment_configuration),
        ("Filter Methods", test_filter_methods),
        ("API Integration", test_api_integration),
    ]

    passed = 0
    failed = 0

    for _test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    if failed == 0:
        pass
    else:
        pass

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
