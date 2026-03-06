# Logseq: [[TTA.dev/Scripts/Batch1_test_generator]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Batch 1 Test Generator - Generates tests for smallest modules.

Uses OpenHands Docker runtime to generate comprehensive unit tests.
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

WORKSPACE = "/home/thein/recovered-tta-storytelling"
DOCKER_IMAGE = "docker.all-hands.dev/all-hands-ai/openhands:0.59"

# Batch 1 modules (< 50 lines) - prioritized by size
BATCH_1_MODULES = [
    "src/monitoring/metrics_collector.py",
    "src/monitoring/performance_monitor.py",
    "src/monitoring/logging_config.py",
    "src/agent_orchestration/validators.py",
    "src/components/narrative_arc_orchestrator/resolution_engine.py",
]


def generate_test(module_path: str) -> bool:
    """Generate test for a single module."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Generating tests for: {module_path}")
    logger.info(f"{'=' * 60}")

    # Determine output path
    rel_path = module_path.replace("src/", "").replace(".py", "")
    output_path = f"tests/{rel_path}_test.py"

    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Create task
    task = f"""Generate comprehensive unit tests for {module_path}.

Requirements:
- Use pytest framework
- Target >80% code coverage
- Test all functions and classes
- Include edge cases and error scenarios
- Save to: {output_path}
- Use mocking where appropriate
- Include docstrings

Output ONLY the complete test file code."""

    # Run OpenHands
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
        f"{WORKSPACE}:/workspace:rw",
        DOCKER_IMAGE,
        "-t",
        task,
    ]

    try:
        logger.info("Executing OpenHands...")
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            logger.info("✓ Successfully generated tests")
            return True
        logger.error(f"✗ Failed with return code {result.returncode}")
        if result.stderr:
            logger.error(f"Error: {result.stderr[:500]}")
        return False

    except subprocess.TimeoutExpired:
        logger.error("✗ Timeout (10 minutes)")
        return False
    except Exception as e:
        logger.error(f"✗ Exception: {e}")
        return False


def main():
    """Main execution."""
    logger.info("Batch 1 Test Generation Starting...")

    # Verify API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)

    logger.info(f"Using Docker image: {DOCKER_IMAGE}")
    logger.info(f"Workspace: {WORKSPACE}")

    # Generate tests
    results = {}
    for i, module in enumerate(BATCH_1_MODULES, 1):
        logger.info(f"\n[{i}/{len(BATCH_1_MODULES)}] Processing {module}")
        success = generate_test(module)
        results[module] = success

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("SUMMARY")
    logger.info(f"{'=' * 60}")
    successful = sum(1 for v in results.values() if v)
    logger.info(f"Generated: {successful}/{len(results)} modules")

    for module, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"{status} {module}")

    # Save results
    with open("batch1_generation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("\nResults saved to batch1_generation_results.json")


if __name__ == "__main__":
    main()
