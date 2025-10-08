#!/usr/bin/env python3
"""
OpenRouter Free Models Filter Demo

This script demonstrates the free models filtering functionality
in the TTA model management system.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_free_models_filter():
    """Demonstrate the free models filtering functionality."""
    try:
        # Import required modules
        from components.model_management import ModelManagementComponent
        from components.model_management.models import ModelManagementConfig, ProviderConfig
        from components.model_management.interfaces import ProviderType

        print("🚀 OpenRouter Free Models Filter Demo")
        print("=" * 50)

        # Check if OpenRouter API key is available
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.startswith("your_"):
            print("❌ OpenRouter API key not configured!")
            print("Please set OPENROUTER_API_KEY environment variable")
            print("Get a free key at: https://openrouter.ai")
            return

        print(f"✅ OpenRouter API key configured: {api_key[:20]}...")

        # Create model management configuration
        config = ModelManagementConfig(
            providers={
                "openrouter": ProviderConfig(
                    provider_type=ProviderType.OPENROUTER,
                    api_key=api_key,
                    base_url="https://openrouter.ai"
                )
            },
            enable_performance_monitoring=True,
            enable_fallback=True
        )

        # Initialize model management component
        print("\n🔧 Initializing Model Management Component...")
        model_mgmt = ModelManagementComponent(config)

        if not await model_mgmt.start():
            print("❌ Failed to start model management component")
            return

        print("✅ Model Management Component initialized successfully")

        # Test 1: Get all available models
        print("\n📋 Test 1: Getting all available models...")
        all_models = await model_mgmt.get_available_models(provider_name="openrouter")
        print(f"Found {len(all_models)} total models from OpenRouter")

        # Show first few models as examples
        print("\nFirst 5 models:")
        for i, model in enumerate(all_models[:5]):
            cost_info = f"${model.cost_per_token:.6f}/token" if model.cost_per_token else "Free"
            print(f"  {i+1}. {model.name} ({model.model_id}) - {cost_info}")

        # Test 2: Get only free models
        print("\n🆓 Test 2: Getting only free models...")
        free_models = await model_mgmt.get_free_models(provider_name="openrouter")
        print(f"Found {len(free_models)} free models from OpenRouter")

        if free_models:
            print("\nFree models:")
            for i, model in enumerate(free_models[:10]):  # Show first 10
                print(f"  {i+1}. {model.name} ({model.model_id}) - FREE")
        else:
            print("No free models found")

        # Test 3: Get affordable models (under $0.001 per token)
        print("\n💰 Test 3: Getting affordable models (max $0.001/token)...")
        affordable_models = await model_mgmt.get_affordable_models(
            max_cost_per_token=0.001,
            provider_name="openrouter"
        )
        print(f"Found {len(affordable_models)} affordable models")

        if affordable_models:
            print("\nAffordable models:")
            for i, model in enumerate(affordable_models[:10]):  # Show first 10
                cost_info = f"${model.cost_per_token:.6f}/token" if model.cost_per_token else "FREE"
                print(f"  {i+1}. {model.name} ({model.model_id}) - {cost_info}")

        # Test 4: Test OpenRouter-specific free models method
        print("\n🎯 Test 4: Using OpenRouter-specific free models method...")
        openrouter_free = await model_mgmt.get_openrouter_free_models()
        print(f"Found {len(openrouter_free)} free models using OpenRouter-specific method")

        # Test 5: Demonstrate filter settings
        print("\n⚙️  Test 5: Testing filter settings...")

        # Get current filter settings
        current_settings = model_mgmt.get_openrouter_filter_settings()
        if current_settings:
            print("Current filter settings:")
            for key, value in current_settings.items():
                print(f"  {key}: {value}")

        # Test setting show_free_only=True
        print("\n🔧 Setting filter to show free models only...")
        model_mgmt.set_openrouter_filter(show_free_only=True, prefer_free=True, max_cost_per_token=0.0)

        # Get models with filter applied
        filtered_models = await model_mgmt.get_available_models(provider_name="openrouter")
        print(f"With free_only filter: {len(filtered_models)} models")

        # Reset filter settings
        print("\n🔄 Resetting filter to show all models with free preference...")
        model_mgmt.set_openrouter_filter(show_free_only=False, prefer_free=True, max_cost_per_token=0.001)

        # Test 6: Cost estimation
        print("\n💵 Test 6: Testing cost estimation...")
        if all_models:
            test_model = all_models[0]
            estimated_tokens = 1000

            # Get the OpenRouter provider directly
            openrouter_provider = model_mgmt.providers.get("openrouter")
            if openrouter_provider and hasattr(openrouter_provider, 'estimate_cost'):
                estimated_cost = await openrouter_provider.estimate_cost(test_model.model_id, estimated_tokens)
                if estimated_cost is not None:
                    print(f"Estimated cost for {estimated_tokens} tokens with {test_model.name}: ${estimated_cost:.6f}")
                else:
                    print(f"Cost estimation not available for {test_model.name}")

        # Test 7: Model categorization
        print("\n📊 Test 7: Model categorization summary...")
        free_count = len([m for m in all_models if m.is_free])
        paid_count = len([m for m in all_models if not m.is_free])

        # Categorize by cost ranges
        very_cheap = len([m for m in all_models if m.cost_per_token and m.cost_per_token <= 0.0001])
        cheap = len([m for m in all_models if m.cost_per_token and 0.0001 < m.cost_per_token <= 0.001])
        moderate = len([m for m in all_models if m.cost_per_token and 0.001 < m.cost_per_token <= 0.01])
        expensive = len([m for m in all_models if m.cost_per_token and m.cost_per_token > 0.01])

        print(f"Model categorization:")
        print(f"  Free models: {free_count}")
        print(f"  Paid models: {paid_count}")
        print(f"  Very cheap (≤$0.0001/token): {very_cheap}")
        print(f"  Cheap ($0.0001-$0.001/token): {cheap}")
        print(f"  Moderate ($0.001-$0.01/token): {moderate}")
        print(f"  Expensive (>$0.01/token): {expensive}")

        print("\n✅ Free Models Filter Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  • Get all available models")
        print("  • Filter to show only free models")
        print("  • Get affordable models within cost threshold")
        print("  • Dynamic filter settings management")
        print("  • Cost estimation for model usage")
        print("  • Model categorization by cost")

        # Cleanup
        await model_mgmt.stop()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo failed with exception")

async def demo_api_endpoints():
    """Demonstrate the API endpoints for free models filtering."""
    print("\n🌐 API Endpoints Demo")
    print("=" * 30)

    print("The following API endpoints are available for free models filtering:")
    print()
    print("1. Get all models with optional free filter:")
    print("   GET /api/v1/models/available?free_only=true")
    print()
    print("2. Get only free models:")
    print("   GET /api/v1/models/free")
    print()
    print("3. Get affordable models:")
    print("   GET /api/v1/models/affordable?max_cost_per_token=0.001")
    print()
    print("4. Get OpenRouter free models:")
    print("   GET /api/v1/models/openrouter/free")
    print()
    print("5. Set OpenRouter filter settings:")
    print("   POST /api/v1/models/openrouter/filter")
    print("   Body: {\"show_free_only\": true, \"prefer_free\": true, \"max_cost_per_token\": 0.001}")
    print()
    print("6. Get OpenRouter filter settings:")
    print("   GET /api/v1/models/openrouter/filter")
    print()
    print("💡 Example curl commands:")
    print("curl -X GET 'http://localhost:8080/api/v1/models/free'")
    print("curl -X GET 'http://localhost:8080/api/v1/models/affordable?max_cost_per_token=0.001'")
    print("curl -X POST 'http://localhost:8080/api/v1/models/openrouter/filter' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"show_free_only\": true}'")

def main():
    """Main function to run the demo."""
    print("🎯 TTA OpenRouter Free Models Filter Demo")
    print("This demo shows how to use the free models filtering functionality")
    print()

    # Check environment
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Warning: OPENROUTER_API_KEY not set")
        print("Some features may not work without a valid API key")
        print("Get a free key at: https://openrouter.ai")
        print()

    # Run the async demo
    try:
        asyncio.run(demo_free_models_filter())
        asyncio.run(demo_api_endpoints())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
