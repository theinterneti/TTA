# ruff: noqa: ALL
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
    print("🔍 Testing imports...")

    try:
        # Test basic imports
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import ProviderConfig
        from components.model_management.providers.openrouter import OpenRouterProvider

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_provider_configuration():
    """Test OpenRouter provider configuration with filter settings."""
    print("\n🔧 Testing provider configuration...")

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

        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False

        print("✅ Provider configuration successful")
        print("✅ All expected methods present")
        return True

    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False


def test_environment_configuration():
    """Test environment variable configuration."""
    print("\n🌍 Testing environment configuration...")

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
        assert show_free_only == True, f"Expected True, got {show_free_only}"
        assert prefer_free == False, f"Expected False, got {prefer_free}"
        assert max_cost == 0.0005, f"Expected 0.0005, got {max_cost}"

        print("✅ Environment configuration successful")
        print(f"   show_free_only: {show_free_only}")
        print(f"   prefer_free: {prefer_free}")
        print(f"   max_cost: {max_cost}")

        return True

    except Exception as e:
        print(f"❌ Environment configuration failed: {e}")
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
    print("\n🔍 Testing filter methods...")

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
                print(
                    f"❌ Setting mismatch for {key}: expected {expected_value}, got {settings.get(key)}"
                )
                return False

        print("✅ Filter methods working correctly")
        print(f"   Settings: {settings}")
        return True

    except Exception as e:
        print(f"❌ Filter methods test failed: {e}")
        return False


def test_api_integration():
    """Test API integration points."""
    print("\n🌐 Testing API integration...")

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

        if missing_endpoints:
            print(f"❌ Missing API endpoints: {missing_endpoints}")
            return False

        print("✅ API integration successful")
        print(f"   Available routes: {len(routes)}")
        return True

    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🎯 OpenRouter Free Models Filter Validation")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Provider Configuration", test_provider_configuration),
        ("Environment Configuration", test_environment_configuration),
        ("Filter Methods", test_filter_methods),
        ("API Integration", test_api_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1

    print("\n📊 Validation Results")
    print("=" * 30)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed / (passed + failed) * 100:.1f}%")

    if failed == 0:
        print("\n🎉 All validation tests passed!")
        print("The OpenRouter Free Models Filter is ready to use.")
        print("\nNext steps:")
        print("1. Set your OPENROUTER_API_KEY environment variable")
        print("2. Configure filter settings in .env file")
        print("3. Run: python examples/free_models_filter_demo.py")
    else:
        print(f"\n⚠️  {failed} validation test(s) failed.")
        print("Please check the implementation and try again.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
