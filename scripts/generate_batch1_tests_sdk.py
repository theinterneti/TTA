# Logseq: [[TTA.dev/Scripts/Generate_batch1_tests_sdk]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Generate tests using OpenHands SDK directly.
"""

import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BATCH_1_MODULES = [
    "src/monitoring/metrics_collector.py",
    "src/monitoring/performance_monitor.py",
    "src/monitoring/logging_config.py",
    "src/agent_orchestration/validators.py",
]


def generate_test_for_module(client: DockerOpenHandsClient, module_path: str) -> bool:
    """Generate test for a single module."""
    logger.info(f"Generating tests for {module_path}...")

    rel_path = module_path.replace("src/", "").replace(".py", "")
    output_path = f"tests/{rel_path}_test.py"

    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    task = f"""Generate comprehensive unit tests for the Python module: {module_path}

Requirements:
1. Use pytest framework
2. Target coverage: >80%
3. Test all functions and classes
4. Include edge cases and error scenarios
5. Save tests to: {output_path}
6. Use proper mocking where needed
7. Include docstrings for all test functions

Output ONLY the complete test file code."""

    try:
        logger.info(f"Executing task for {module_path}...")
        result = client.execute_task(
            task=task,
            timeout=300,
        )

        if result.get("success"):
            logger.info(f"✓ Generated tests for {module_path}")
            return True
        logger.error(f"✗ Failed to generate tests for {module_path}")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
        return False

    except Exception as e:
        logger.error(f"✗ Exception for {module_path}: {e}")
        return False


def main():
    """Main execution."""
    logger.info("Starting Batch 1 Test Generation (SDK)...")

    # Load configuration
    try:
        config = OpenHandsIntegrationConfig.from_env()
        logger.info(f"Configuration loaded: {config.model_name}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Create client
    try:
        client = DockerOpenHandsClient(config.to_client_config())
        logger.info("Docker client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        sys.exit(1)

    # Generate tests
    results = {}
    for module in BATCH_1_MODULES:
        success = generate_test_for_module(client, module)
        results[module] = success

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    successful = sum(1 for v in results.values() if v)
    logger.info(f"Generated: {successful}/{len(results)} modules")

    for module, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"{status} {module}")

    # Save results
    with open("batch1_sdk_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("\nResults saved to batch1_sdk_results.json")


if __name__ == "__main__":
    main()
