# ruff: noqa: ALL
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
    print("❌ python-dotenv not installed. Install with: pip install python-dotenv")
    sys.exit(1)


def test_environment_loading():
    """Test that environment variables are loaded correctly."""
    print("🔍 Testing environment variable loading...")

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
            print(f"✅ {var}: {'*' * min(len(value), 8)}...")

    if missing_vars:
        print(f"❌ Missing required variables: {missing_vars}")
        return False

    print("✅ All required environment variables loaded successfully")
    return True


def test_model_management_config():
    """Test model management specific configuration."""
    print("\n🔍 Testing model management configuration...")

    # Test feature flags
    model_mgmt_enabled = os.getenv("FEATURE_MODEL_MANAGEMENT", "").lower() == "true"
    if not model_mgmt_enabled:
        print("❌ Model management feature is disabled")
        return False

    print("✅ Model management feature is enabled")

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
            print(f"✅ {key} is configured")
        else:
            print(f"⚠️  {key} is not configured (optional)")

    if not configured_keys:
        print("❌ No AI model API keys are configured")
        return False

    print(f"✅ {len(configured_keys)} API key(s) configured")
    return True


def test_model_management_import():
    """Test that the model management system can be imported."""
    print("\n🔍 Testing model management system import...")

    try:
        # Test importing the main component
        from components.model_management import ModelManagementComponent

        print("✅ ModelManagementComponent imported successfully")

        # Test importing interfaces
        from components.model_management.interfaces import IModelProvider, TaskType

        print("✅ Model management interfaces imported successfully")

        # Test importing providers
        from components.model_management.providers import OpenRouterProvider

        print("✅ Model providers imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Failed to import model management system: {e}")
        return False


def test_provider_configuration():
    """Test that providers can be configured with environment variables."""
    print("\n🔍 Testing provider configuration...")

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

            provider = OpenRouterProvider(config)
            print("✅ OpenRouter provider configured successfully")
            return True
        print("⚠️  OpenRouter API key not configured, skipping provider test")
        return True

    except Exception as e:
        print(f"❌ Failed to configure providers: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing TTA Model Management Environment Integration\n")

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
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} tests, {passed} passed, {failed} failed")

    if failed == 0:
        print(
            "\n🎉 All tests passed! Model management environment integration is working correctly."
        )
        return True
    print(f"\n❌ {failed} test(s) failed. Please check your environment configuration.")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
