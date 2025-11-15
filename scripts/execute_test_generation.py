#!/usr/bin/env python3
"""
Execute OpenHands test generation workflow for adapters.py.

This script:
1. Creates TestTaskSpecification for src/agent_orchestration/adapters.py
2. Initializes UnitTestGenerationService with OpenHandsIntegrationConfig
3. Executes generate_tests() with max_iterations=3
4. Monitors model selection, fallback chain, and error recovery
5. Captures all output and logs
"""

import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file before anything else
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=False)
else:
    pass

# Setup logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("test_generation_execution.log"),
    ],
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def execute_test_generation():
    """Execute test generation workflow."""
    logger.info("=" * 80)
    logger.info("PHASE 3: TEST GENERATION EXECUTION")
    logger.info("=" * 80)

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

        logger.info("\n[1/4] Creating TestTaskSpecification...")

        # Create specification for adapters.py
        spec = TestTaskSpecification(
            target_file=Path("src/agent_orchestration/adapters.py"),
            coverage_threshold=70.0,
            test_framework="pytest",
            test_directory=Path("tests"),
            timeout_seconds=600.0,
        )

        logger.info("✓ Specification created:")
        logger.info(f"  - Target file: {spec.target_file}")
        logger.info(f"  - Coverage threshold: {spec.coverage_threshold}%")
        logger.info(f"  - Test framework: {spec.test_framework}")
        logger.info(f"  - Timeout: {spec.timeout_seconds}s")

        logger.info("\n[2/4] Initializing UnitTestGenerationService...")

        # Create config from environment
        # Note: OPENROUTER_API_KEY may not be set, which will trigger fallback
        config = OpenHandsIntegrationConfig.from_env()

        logger.info("✓ Configuration loaded:")
        logger.info(f"  - Model: {config.model}")
        logger.info(f"  - Max retries: {config.max_retries}")
        logger.info(f"  - Retry base delay: {config.retry_base_delay}s")
        logger.info(f"  - Fallback to mock: {config.fallback_to_mock}")

        # Initialize service
        service = UnitTestGenerationService(config)
        logger.info("✓ Service initialized")

        logger.info("\n[3/4] Executing test generation (max_iterations=3)...")
        logger.info("Monitoring for:")
        logger.info("  - Model selection from free_models_registry")
        logger.info("  - Fallback chain activation")
        logger.info("  - Error recovery handling")
        logger.info("  - Rate limit detection")

        # Execute test generation
        result = await service.generate_tests(spec, max_iterations=3)

        logger.info("\n[4/4] Test generation completed")
        logger.info("=" * 80)
        logger.info("EXECUTION RESULTS")
        logger.info("=" * 80)

        logger.info("\nValidation Results:")
        logger.info(f"  - Syntax valid: {result.syntax_valid}")
        logger.info(f"  - Tests pass: {result.tests_pass}")
        logger.info(f"  - Coverage: {result.coverage_percentage}%")
        logger.info(f"  - Conventions followed: {result.conventions_followed}")
        logger.info(f"  - Quality score: {result.quality_score}")

        if result.issues:
            logger.info(f"\nIssues found ({len(result.issues)}):")
            for issue in result.issues:
                logger.info(f"  - {issue}")
        else:
            logger.info("\n✓ No issues found")

        if result.test_file_path:
            logger.info(f"\nGenerated test file: {result.test_file_path}")

        logger.info("\n" + "=" * 80)
        if (
            result.syntax_valid
            and result.tests_pass
            and result.coverage_percentage >= spec.coverage_threshold
            and result.conventions_followed
        ):
            logger.info("✓ TEST GENERATION SUCCESSFUL")
        else:
            logger.warning("⚠ TEST GENERATION COMPLETED WITH ISSUES")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"✗ Test generation failed: {e}", exc_info=True)
        raise


async def main():
    """Run test generation."""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + "OpenHands Test Generation - Execution".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "=" * 78 + "╝")

    try:
        await execute_test_generation()
        logger.info("\n✓ Execution completed successfully")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
