#!/usr/bin/env python3
"""
Optimized test generation for Tier 1 modules using OpenHands integration.

Generates comprehensive unit tests with:
- Simplified task descriptions (minimal context overhead)
- Single-module generation (one at a time)
- Automatic model rotation (DeepSeek Chat primary, fallback chain)
- Rate limit detection and recovery

Usage:
    uv run python scripts/generate_tier1_tests.py [--module messaging|models|adapters]
    uv run python scripts/generate_tier1_tests.py  # Generates all in sequence
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=False)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Tier 1 modules - ordered by size (smallest first for proof-of-concept)
TIER1_MODULES = [
    {
        "name": "messaging",
        "file": "src/agent_orchestration/messaging.py",
        "lines": 48,
        "coverage": 0,
        "description": "Message passing models",
    },
    {
        "name": "models",
        "file": "src/agent_orchestration/models.py",
        "lines": 338,
        "coverage": 5,
        "description": "Core data models and enums",
    },
    {
        "name": "adapters",
        "file": "src/agent_orchestration/adapters.py",
        "lines": 419,
        "coverage": 0,
        "description": "Agent adapter implementations (IPA, WBA, NGA)",
    },
]


async def generate_for_module(service, module: dict) -> dict:
    """Generate tests for a single module with optimized task description.

    Uses minimal task description to reduce context overhead.
    OpenHands already knows pytest conventions.
    """
    from agent_orchestration.openhands_integration.test_generation_models import (
        TestTaskSpecification,
    )

    logger.info(f"\n{'='*80}")
    logger.info(f"Generating tests for: {module['name']}")
    logger.info(f"File: {module['file']} ({module['lines']} lines)")
    logger.info(f"Current coverage: {module['coverage']}%")
    logger.info(f"{'='*80}")

    try:
        # OPTIMIZED: Minimal task description
        # Only provide essential info: target file, coverage threshold, output path
        spec = TestTaskSpecification(
            target_file=Path(module["file"]),
            coverage_threshold=70.0,
            test_framework="pytest",
            test_directory=Path("tests"),
            timeout_seconds=900.0,
            # Minimal description - let OpenHands use its default knowledge
            description=f"Generate pytest unit tests for {module['file']} with ≥70% coverage. Test all public APIs, edge cases, and error conditions.",
        )

        logger.info(f"Executing test generation (max_iterations=5)...")
        logger.info(f"Model: DeepSeek Chat (primary) with automatic fallback")

        # Generate tests
        result = await service.generate_tests(spec, max_iterations=5)

        # Prepare result
        module_result = {
            "module": module["name"],
            "file": module["file"],
            "status": "SUCCESS" if result.syntax_valid and result.tests_pass else "FAILED",
            "timestamp": datetime.now().isoformat(),
            "syntax_valid": result.syntax_valid,
            "tests_pass": result.tests_pass,
            "coverage_percentage": result.coverage_percentage,
            "conventions_followed": result.conventions_followed,
            "test_file_path": str(result.test_file_path) if result.test_file_path else None,
            "issues": result.issues,
        }

        logger.info(f"✓ Generation completed for {module['name']}")
        logger.info(f"  Syntax valid: {result.syntax_valid}")
        logger.info(f"  Tests pass: {result.tests_pass}")
        logger.info(f"  Coverage: {result.coverage_percentage}%")

        return module_result

    except Exception as e:
        logger.error(f"✗ Generation failed for {module['name']}: {e}", exc_info=True)
        return {
            "module": module["name"],
            "file": module["file"],
            "status": "ERROR",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


async def main():
    """Generate tests for all Tier 1 modules with optimized strategy."""
    logger.info("\n" + "╔" + "="*78 + "╗")
    logger.info("║" + " "*78 + "║")
    logger.info("║" + "Tier 1 Test Generation - Optimized Strategy".center(78) + "║")
    logger.info("║" + " "*78 + "║")
    logger.info("╚" + "="*78 + "╝")

    logger.info(f"\nStrategy: Single-module generation with automatic model rotation")
    logger.info(f"Primary model: DeepSeek Chat (100% success rate)")
    logger.info(f"Fallback chain: Mistral Small → Google Gemini 2.0 Flash")
    logger.info(f"Rate limit detection: Enabled (429 errors trigger model rotation)")
    logger.info(f"\nGenerating tests for {len(TIER1_MODULES)} modules (smallest first)...")
    logger.info(f"Target coverage: 70% for each module")

    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.test_generation_service import (
            UnitTestGenerationService,
        )

        # Initialize service once
        config = OpenHandsIntegrationConfig.from_env()
        service = UnitTestGenerationService(config)

        results = []
        for module in TIER1_MODULES:
            result = await generate_for_module(service, module)
            results.append(result)

        # Summary
        logger.info("\n" + "="*80)
        logger.info("GENERATION SUMMARY")
        logger.info("="*80)

        successful = sum(1 for r in results if r["status"] == "SUCCESS")
        failed = sum(1 for r in results if r["status"] in ("FAILED", "ERROR"))

        logger.info(f"Total modules: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        for result in results:
            status_icon = "✓" if result["status"] == "SUCCESS" else "✗"
            logger.info(f"{status_icon} {result['module']}: {result['status']}")
            if result["status"] == "SUCCESS":
                logger.info(f"  Coverage: {result['coverage_percentage']}%")
                logger.info(f"  Test file: {result['test_file_path']}")

        # Save results
        results_file = Path("tier1_generation_results_optimized.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"\nResults saved to {results_file}")
        logger.info("="*80)

        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

