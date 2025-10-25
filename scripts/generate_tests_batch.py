#!/usr/bin/env python3
"""
Batch test generation for multiple modules with comprehensive reporting.

Generates tests for:
1. protocol_bridge.py (385 lines, 0% coverage)
2. capability_matcher.py (482 lines, 0% coverage)
3. circuit_breaker.py (443 lines, 21.79% coverage)
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('batch_test_generation.log'),
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


MODULES = [
    {
        "name": "protocol_bridge",
        "file": "src/agent_orchestration/protocol_bridge.py",
        "lines": 385,
        "coverage": 0,
    },
    {
        "name": "capability_matcher",
        "file": "src/agent_orchestration/capability_matcher.py",
        "lines": 482,
        "coverage": 0,
    },
    {
        "name": "circuit_breaker",
        "file": "src/agent_orchestration/circuit_breaker.py",
        "lines": 443,
        "coverage": 21.79,
    },
]


async def generate_for_module(module: dict, model_preset: str = "deepseek-chat") -> dict:
    """Generate tests for a single module with explicit model selection."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Generating tests for: {module['name']}")
    logger.info(f"Model: {model_preset}")
    logger.info(f"{'='*80}")

    result = {
        "module": module["name"],
        "file": module["file"],
        "status": "PENDING",
        "timestamp": datetime.now().isoformat(),
        "details": {},
        "model_used": model_preset,
    }

    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.test_generation_models import (
            TestTaskSpecification,
        )
        from agent_orchestration.openhands_integration.test_generation_service import (
            UnitTestGenerationService,
        )

        # Create specification
        logger.info(f"Creating specification for {module['name']}...")
        spec = TestTaskSpecification(
            target_file=Path(module["file"]),
            coverage_threshold=70.0,
            test_framework="pytest",
            test_directory=Path("tests"),
            timeout_seconds=600.0,
        )

        # Initialize service with explicit model
        logger.info(f"Initializing test generation service with model: {model_preset}...")
        config = OpenHandsIntegrationConfig.from_env()
        # Override model preset to use DeepSeek (verified model with 100% success)
        config.model_preset = model_preset
        service = UnitTestGenerationService(config)

        # Generate tests
        logger.info("Executing test generation (max_iterations=3)...")
        gen_result = await service.generate_tests(spec, max_iterations=3)

        # Capture results
        result["status"] = "SUCCESS" if gen_result.syntax_valid else "PARTIAL"
        result["details"] = {
            "syntax_valid": gen_result.syntax_valid,
            "tests_pass": gen_result.tests_pass,
            "coverage_percentage": gen_result.coverage_percentage,
            "quality_score": gen_result.quality_score,
            "conventions_followed": gen_result.conventions_followed,
            "test_file_path": str(gen_result.test_file_path) if gen_result.test_file_path else None,
            "issues": gen_result.issues,
        }

        logger.info(f"✓ Test generation completed for {module['name']}")
        logger.info(f"  - Syntax valid: {gen_result.syntax_valid}")
        logger.info(f"  - Tests pass: {gen_result.tests_pass}")
        logger.info(f"  - Coverage: {gen_result.coverage_percentage}%")
        logger.info(f"  - Quality score: {gen_result.quality_score}")

    except Exception as e:
        result["status"] = "FAILED"
        result["details"]["error"] = str(e)
        logger.error(f"✗ Test generation failed for {module['name']}: {e}", exc_info=True)

    return result


async def main():
    """Generate tests for all modules."""
    logger.info("\n" + "╔" + "="*78 + "╗")
    logger.info("║" + " "*78 + "║")
    logger.info("║" + "Batch Test Generation - Multiple Modules".center(78) + "║")
    logger.info("║" + " "*78 + "║")
    logger.info("╚" + "="*78 + "╝")

    logger.info(f"\nGenerating tests for {len(MODULES)} modules...")
    logger.info(f"Target coverage: 70% for each module")

    results = []
    # Use DeepSeek Chat (verified model with 100% success rate)
    model_preset = "deepseek-chat"
    logger.info(f"\nUsing model preset: {model_preset}")
    logger.info("(DeepSeek Chat has 100% success rate in free model registry)")

    for module in MODULES:
        result = await generate_for_module(module, model_preset=model_preset)
        results.append(result)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("BATCH GENERATION SUMMARY")
    logger.info("="*80)

    for result in results:
        status_icon = "✓" if result["status"] == "SUCCESS" else "⚠" if result["status"] == "PARTIAL" else "✗"
        logger.info(f"{status_icon} {result['module']}: {result['status']}")
        if result["details"]:
            logger.info(f"    Coverage: {result['details'].get('coverage_percentage', 'N/A')}%")
            logger.info(f"    Quality: {result['details'].get('quality_score', 'N/A')}")

    # Save results
    report_file = Path("batch_test_generation_report.json")
    with report_file.open("w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n✓ Report saved to: {report_file}")

    # Return exit code
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    logger.info(f"\nTotal: {success_count}/{len(MODULES)} modules completed successfully")

    return 0 if success_count == len(MODULES) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

