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
        from components.model_management.interfaces import ProviderType
        from components.model_management.models import (
            ModelManagementConfig,
            ProviderConfig,
        )

        # Check if OpenRouter API key is available
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key.startswith("your_"):
            return

        # Create model management configuration
        config = ModelManagementConfig(
            providers={
                "openrouter": ProviderConfig(
                    provider_type=ProviderType.OPENROUTER,
                    api_key=api_key,
                    base_url="https://openrouter.ai",
                )
            },
            enable_performance_monitoring=True,
            enable_fallback=True,
        )

        # Initialize model management component
        model_mgmt = ModelManagementComponent(config)

        if not await model_mgmt.start():
            return

        # Test 1: Get all available models
        all_models = await model_mgmt.get_available_models(provider_name="openrouter")

        # Show first few models as examples
        for _i, _model in enumerate(all_models[:5]):
            pass

        # Test 2: Get only free models
        free_models = await model_mgmt.get_free_models(provider_name="openrouter")

        if free_models:
            for _i, _model in enumerate(free_models[:10]):  # Show first 10
                pass
        else:
            pass

        # Test 3: Get affordable models (under $0.001 per token)
        affordable_models = await model_mgmt.get_affordable_models(
            max_cost_per_token=0.001, provider_name="openrouter"
        )

        if affordable_models:
            for _i, _model in enumerate(affordable_models[:10]):  # Show first 10
                pass

        # Test 4: Test OpenRouter-specific free models method
        await model_mgmt.get_openrouter_free_models()

        # Test 5: Demonstrate filter settings

        # Get current filter settings
        current_settings = model_mgmt.get_openrouter_filter_settings()
        if current_settings:
            for _key, _value in current_settings.items():
                pass

        # Test setting show_free_only=True
        model_mgmt.set_openrouter_filter(
            show_free_only=True, prefer_free=True, max_cost_per_token=0.0
        )

        # Get models with filter applied
        await model_mgmt.get_available_models(provider_name="openrouter")

        # Reset filter settings
        model_mgmt.set_openrouter_filter(
            show_free_only=False, prefer_free=True, max_cost_per_token=0.001
        )

        # Test 6: Cost estimation
        if all_models:
            test_model = all_models[0]
            estimated_tokens = 1000

            # Get the OpenRouter provider directly
            openrouter_provider = model_mgmt.providers.get("openrouter")
            if openrouter_provider and hasattr(openrouter_provider, "estimate_cost"):
                estimated_cost = await openrouter_provider.estimate_cost(
                    test_model.model_id, estimated_tokens
                )
                if estimated_cost is not None:
                    pass
                else:
                    pass

        # Test 7: Model categorization
        len([m for m in all_models if m.is_free])
        len([m for m in all_models if not m.is_free])

        # Categorize by cost ranges
        len([m for m in all_models if m.cost_per_token and m.cost_per_token <= 0.0001])
        len(
            [
                m
                for m in all_models
                if m.cost_per_token and 0.0001 < m.cost_per_token <= 0.001
            ]
        )
        len(
            [
                m
                for m in all_models
                if m.cost_per_token and 0.001 < m.cost_per_token <= 0.01
            ]
        )
        len([m for m in all_models if m.cost_per_token and m.cost_per_token > 0.01])

        # Cleanup
        await model_mgmt.stop()

    except ImportError:
        pass
    except Exception:
        logger.exception("Demo failed with exception")


async def demo_api_endpoints():
    """Demonstrate the API endpoints for free models filtering."""


def main():
    """Main function to run the demo."""

    # Check environment
    if not os.getenv("OPENROUTER_API_KEY"):
        pass

    # Run the async demo
    try:
        asyncio.run(demo_free_models_filter())
        asyncio.run(demo_api_endpoints())
    except KeyboardInterrupt:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()
