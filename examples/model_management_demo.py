#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Examples/Model_management_demo]]
Model Management System Demo

This script demonstrates the comprehensive model management system for TTA,
showcasing various providers, model selection, and generation capabilities.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from components.model_management import (
    ModelManagementComponent,
    ModelRequirements,
    TaskType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demo_basic_generation():
    """Demonstrate basic text generation with automatic model selection."""

    # Configuration for the demo
    config = {
        "model_management": {
            "enabled": True,
            "default_provider": "openrouter",
            "providers": {
                "openrouter": {
                    "enabled": True,
                    "api_key": os.getenv("OPENROUTER_API_KEY", "demo-key"),
                    "free_models_only": True,
                    "base_url": "https://openrouter.ai/api/v1",
                }
            },
            "selection_strategy": {
                "algorithm": "performance_based",
                "prefer_free_models": True,
                "therapeutic_safety_threshold": 7.0,
            },
        }
    }

    # Initialize the model management component
    component = ModelManagementComponent(config)

    try:
        # Start the component
        await component.start()

        # Generate text with automatic model selection
        response = await component.generate_text(
            prompt="Tell me a short story about someone overcoming their fear of public speaking",
            task_type=TaskType.THERAPEUTIC_NARRATIVE,
            max_tokens=500,
            temperature=0.7,
        )

        if response:
            pass
        else:
            pass

    except Exception:
        pass
    finally:
        # Stop the component
        await component.stop()


async def demo_model_selection():
    """Demonstrate intelligent model selection based on requirements."""

    config = {
        "model_management": {
            "enabled": True,
            "providers": {
                "openrouter": {
                    "enabled": True,
                    "api_key": os.getenv("OPENROUTER_API_KEY", "demo-key"),
                    "free_models_only": True,
                },
                "ollama": {
                    "enabled": True,
                    "base_url": "http://localhost:11434",
                    "docker_enabled": False,  # Assume Ollama is running locally
                },
            },
        }
    }

    component = ModelManagementComponent(config)

    try:
        await component.start()

        # Test different task types and requirements
        test_cases = [
            {
                "name": "Quick Chat Response",
                "requirements": ModelRequirements(
                    task_type=TaskType.GENERAL_CHAT,
                    max_latency_ms=2000,
                    min_quality_score=6.0,
                ),
                "prompt": "Hello, how are you today?",
            },
            {
                "name": "Therapeutic Narrative",
                "requirements": ModelRequirements(
                    task_type=TaskType.THERAPEUTIC_NARRATIVE,
                    therapeutic_safety_required=True,
                    min_quality_score=7.0,
                    context_length_needed=2048,
                ),
                "prompt": "Create a story about building self-confidence",
            },
            {
                "name": "Creative Writing",
                "requirements": ModelRequirements(
                    task_type=TaskType.CREATIVE_WRITING,
                    max_cost_per_token=0.001,
                    min_quality_score=7.5,
                ),
                "prompt": "Write a poem about the beauty of nature",
            },
        ]

        for test_case in test_cases:
            # Select model based on requirements
            model_instance = await component.select_model(test_case["requirements"])

            if model_instance:
                # Generate response
                response = await component.generate_text(
                    test_case["prompt"],
                    task_type=test_case["requirements"].task_type,
                    max_tokens=200,
                )

                if response:
                    pass
                else:
                    pass
            else:
                pass

    except Exception:
        pass
    finally:
        await component.stop()


async def demo_system_monitoring():
    """Demonstrate system monitoring and performance tracking."""

    config = {
        "model_management": {
            "enabled": True,
            "providers": {
                "openrouter": {
                    "enabled": True,
                    "api_key": os.getenv("OPENROUTER_API_KEY", "demo-key"),
                    "free_models_only": True,
                }
            },
            "performance_monitoring": {"enabled": True, "real_time_monitoring": True},
        }
    }

    component = ModelManagementComponent(config)

    try:
        await component.start()

        # Get system status
        status = await component.get_system_status()

        if status["system_resources"]:
            status["system_resources"]

        # Get available models
        models = await component.get_available_models()
        for _i, model in enumerate(models[:5]):  # Show first 5 models
            if model.therapeutic_safety_score:
                pass

        if len(models) > 5:
            pass

        # Test model connectivity
        if models:
            test_result = await component.test_model_connectivity(
                models[0].model_id, models[0].provider_type.value
            )

            if test_result.get("latency_ms"):
                pass
            if test_result.get("error"):
                pass

    except Exception:
        pass
    finally:
        await component.stop()


async def demo_hardware_detection():
    """Demonstrate hardware detection and model recommendations."""

    config = {
        "model_management": {
            "enabled": True,
            "hardware_detection": {"enabled": True, "gpu_detection": True},
        }
    }

    component = ModelManagementComponent(config)

    try:
        await component.start()

        # Get hardware information
        if component.system_resources:
            resources = component.system_resources

            if resources.get("gpus"):
                for _i, _gpu in enumerate(resources["gpus"]):
                    pass

        # Get model recommendations for different tasks
        task_types = [
            TaskType.GENERAL_CHAT,
            TaskType.THERAPEUTIC_NARRATIVE,
            TaskType.CREATIVE_WRITING,
        ]

        for task_type in task_types:
            recommendations = await component.get_model_recommendations(task_type)

            for _i, _model_id in enumerate(recommendations[:3]):  # Show top 3
                pass

    except Exception:
        pass
    finally:
        await component.stop()


async def main():
    """Run all demonstrations."""

    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        pass

    try:
        # Run demonstrations
        await demo_hardware_detection()
        await demo_system_monitoring()
        await demo_model_selection()

        # Only run generation demo if API key is available
        if os.getenv("OPENROUTER_API_KEY"):
            await demo_basic_generation()
        else:
            pass

    except KeyboardInterrupt:
        pass
    except Exception:
        logger.exception("Demo error details:")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
