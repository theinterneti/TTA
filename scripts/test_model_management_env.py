#!/usr/bin/env python3
"""
Test Model Management Environment Integration

This script tests that the model management system can properly load
and use the new environment configuration structure.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit(1)


def test_environment_loading():
    """Test that environment variables are loaded correctly."""

    # Load environment variables
    load_dotenv()

    # Test required variables
    required_vars = [
        "ENVIRONMENT",
        "OPENROUTER_API_KEY",
        "FEATURE_MODEL_MANAGEMENT",
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            pass

    return not missing_vars


def test_model_management_config():
    """Test model management specific configuration."""

    # Test feature flags
    model_mgmt_enabled = os.getenv("FEATURE_MODEL_MANAGEMENT", "").lower() == "true"
    if not model_mgmt_enabled:
        return False

    # Test API key configuration
    api_keys = {
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }

    configured_keys = []
    for key, value in api_keys.items():
        if value and not value.startswith("your_"):
            configured_keys.append(key)
        else:
            pass

    return configured_keys


def test_model_management_import():
    """Test that the model management system can be imported."""

    try:
        # Test importing the main component
        from components.model_management import ModelManagementComponent

        # Test importing interfaces
        from components.model_management.interfaces import IModelProvider, TaskType

        # Test importing providers
        from components.model_management.providers import OpenRouterProvider

        return True

    except ImportError:
        return False


def test_provider_configuration():
    """Test that providers can be configured with environment variables."""

    try:
        from components.model_management.models import ProviderConfig
        from components.model_management.providers import OpenRouterProvider

        # Test OpenRouter provider configuration
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and not openrouter_key.startswith("your_"):
            config = ProviderConfig(
                provider_type="openrouter",
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
            )

            OpenRouterProvider(config)
            return True
        return True

    except Exception:
        return False


def main():
    """Run all tests."""

    tests = [
        ("Environment Loading", test_environment_loading),
        ("Model Management Config", test_model_management_config),
        ("Model Management Import", test_model_management_import),
        ("Provider Configuration", test_provider_configuration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception:
            results.append((test_name, False))

    # Print summary

    passed = 0
    failed = 0

    for test_name, result in results:
        if result:
            passed += 1
        else:
            failed += 1

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
