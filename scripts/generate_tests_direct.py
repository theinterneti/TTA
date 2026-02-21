# Logseq: [[TTA.dev/Scripts/Generate_tests_direct]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Direct Test Generation using OpenHands Docker Client.

Generates unit tests for modules using OpenHands Docker runtime.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Batch 1 modules (< 50 lines)
BATCH_1_MODULES = [
    (
        "src/monitoring/metrics_collector.py",
        "tests/monitoring/test_metrics_collector.py",
    ),
    (
        "src/monitoring/performance_monitor.py",
        "tests/monitoring/test_performance_monitor.py",
    ),
    ("src/monitoring/logging_config.py", "tests/monitoring/test_logging_config.py"),
    (
        "src/agent_orchestration/validators.py",
        "tests/agent_orchestration/test_validators.py",
    ),
]


def generate_test_for_module(module_path: str, output_path: str) -> bool:
    """Generate tests for a single module using OpenHands."""
    logger.info(f"Generating tests for {module_path}...")

    # Create output directory
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create task description
    task_description = f"""
Generate comprehensive unit tests for the Python module: {module_path}

Requirements:
1. Use pytest framework
2. Target coverage: >80%
3. Test all functions and classes
4. Include edge cases and error scenarios
5. Save tests to: {output_path}
6. Use proper mocking where needed
7. Include docstrings for all test functions

Module to test:
- Path: {module_path}
- Workspace: /home/thein/recovered-tta-storytelling

Output the complete test file content.
"""

    # Use OpenHands Docker to generate tests
    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-e",
        f"OPENROUTER_API_KEY={os.getenv('OPENROUTER_API_KEY')}",
        "-e",
        "LLM_MODEL=openrouter/deepseek/deepseek-chat",
        "-v",
        "/home/thein/recovered-tta-storytelling:/workspace:rw",
        "ghcr.io/all-hands-ai/openhands:0.59",
        "-t",
        task_description,
    ]

    try:
        logger.info(f"Running: {' '.join(cmd[:8])}...")
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info(f"✓ Tests generated for {module_path}")
            return True
        logger.error(f"✗ Failed to generate tests for {module_path}")
        logger.error(f"Error: {result.stderr}")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Timeout generating tests for {module_path}")
        return False
    except Exception as e:
        logger.error(f"✗ Exception generating tests for {module_path}: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("Starting Batch 1 Test Generation (Direct)...")

    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY not set in environment")
        sys.exit(1)

    # Generate tests for each module
    results = {}
    for module_path, output_path in BATCH_1_MODULES:
        success = generate_test_for_module(module_path, output_path)
        results[module_path] = {"success": success, "output": output_path}

    # Save results
    results_file = Path("batch1_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {results_file}")

    # Summary
    successful = sum(1 for r in results.values() if r["success"])
    logger.info(f"Generated tests for {successful}/{len(results)} modules")


if __name__ == "__main__":
    main()
