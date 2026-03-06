#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Validate_free_model_test_generation]]
Free Model Test Generation Validation Script

Validates that verified free models (DeepSeek Chat) can successfully generate
tests through our OpenHands integration. Tests the complete pipeline:
1. Model configuration
2. Test generation task execution
3. Code quality evaluation

Target: src/agent_orchestration/tools/response_utils.py (307 lines, no existing tests)

Usage:
    uv run python scripts/validate_free_model_test_generation.py

Output:
    - Console: Detailed execution log
    - File: test_generation_output.txt (captured output for manual evaluation)
"""

import asyncio
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv

    from src.agent_orchestration.openhands_integration.config import (
        OpenHandsIntegrationConfig,
    )
    from src.agent_orchestration.openhands_integration.helpers import (
        generate_tests_for_file,
    )
    from src.agent_orchestration.openhands_integration.test_generation_models import (
        TestValidationResult,
    )
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error(
        "Make sure you run this script with: uv run python scripts/validate_free_model_test_generation.py"
    )
    sys.exit(1)

# Load environment variables
load_dotenv()


async def main():
    """Main validation workflow."""
    output_file = Path("test_generation_output.txt")
    start_time = datetime.now()

    logger.info("=" * 80)
    logger.info("FREE MODEL TEST GENERATION VALIDATION")
    logger.info("=" * 80)
    logger.info(f"Start Time: {start_time}")
    logger.info("Target File: src/agent_orchestration/tools/response_utils.py")
    logger.info("Model: openrouter/deepseek/deepseek-chat (verified working)")
    logger.info(f"Output File: {output_file}")
    logger.info("=" * 80)

    # Step 1: Configure OpenHands with verified free model
    logger.info("\n[Step 1/4] Configuring OpenHands with DeepSeek Chat...")
    try:
        config = OpenHandsIntegrationConfig.from_env()
        # Override model to use verified DeepSeek Chat
        config.custom_model_id = "openrouter/deepseek/deepseek-chat"
        # ENABLE DOCKER MODE for full tool access (file creation, bash, etc.)
        config.use_docker_runtime = True
        config.docker_timeout = 600.0  # Longer timeout for Docker mode
        logger.info("✓ Configuration loaded")
        logger.info(f"  Model: {config.custom_model_id}")
        logger.info(f"  Workspace: {config.workspace_root}")
        logger.info(f"  Timeout: {config.default_timeout_seconds}s")
        logger.info(f"  Docker Mode: {config.use_docker_runtime}")
    except Exception as e:
        logger.error(f"✗ Configuration failed: {e}")
        logger.error(traceback.format_exc())
        return

    # Step 2: Execute test generation
    logger.info("\n[Step 2/4] Executing test generation...")
    logger.info("  Target: src/agent_orchestration/tools/response_utils.py")
    logger.info("  Coverage Threshold: 70%")
    logger.info("  Max Iterations: 3")
    logger.info("\n  NOTE: Docker mode enabled - AI has full tool access.")
    logger.info("  The model can create files, execute bash commands, etc.")
    logger.info("  Generated tests will be written to the workspace.\n")

    result: TestValidationResult | None = None
    error_message: str | None = None

    try:
        result = await generate_tests_for_file(
            file_path="src/agent_orchestration/tools/response_utils.py",
            coverage_threshold=70.0,
            max_iterations=3,  # Reduced iterations for faster validation
            config=config,
        )
        logger.info("✓ Test generation completed")
    except Exception as e:
        error_message = str(e)
        logger.error(f"✗ Test generation failed: {e}")
        logger.error(traceback.format_exc())

    # Step 3: Capture and save output
    logger.info("\n[Step 3/4] Capturing output...")

    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("FREE MODEL TEST GENERATION VALIDATION OUTPUT")
    output_lines.append("=" * 80)
    output_lines.append(f"Timestamp: {datetime.now()}")
    output_lines.append("Model: openrouter/deepseek/deepseek-chat")
    output_lines.append("Target: src/agent_orchestration/tools/response_utils.py")
    output_lines.append("=" * 80)
    output_lines.append("")

    if result:
        output_lines.append("RESULT SUMMARY")
        output_lines.append("-" * 80)
        output_lines.append(f"Syntax Valid: {result.syntax_valid}")
        output_lines.append(f"Tests Pass: {result.tests_pass}")
        output_lines.append(f"Coverage: {result.coverage_percentage:.1f}%")
        output_lines.append(f"Conventions Followed: {result.conventions_followed}")
        output_lines.append(f"Quality Score: {result.quality_score:.1f}/100")
        output_lines.append(f"Test File Path: {result.test_file_path}")
        output_lines.append("")

        if result.issues:
            output_lines.append(f"ISSUES ({len(result.issues)})")
            output_lines.append("-" * 80)
            for i, issue in enumerate(result.issues, 1):
                output_lines.append(f"{i}. {issue}")
            output_lines.append("")

        # Note: Generated code is in the test file at result.test_file_path
        if result.test_file_path:
            output_lines.append("GENERATED TEST FILE")
            output_lines.append("-" * 80)
            output_lines.append(f"Path: {result.test_file_path}")
            output_lines.append("(Review the file directly for generated code)")
            output_lines.append("")

    if error_message:
        output_lines.append("ERROR")
        output_lines.append("-" * 80)
        output_lines.append(error_message)
        output_lines.append("")
        output_lines.append("FULL TRACEBACK")
        output_lines.append("-" * 80)
        output_lines.append(traceback.format_exc())
        output_lines.append("")

    # Write to file
    output_content = "\n".join(output_lines)
    output_file.write_text(output_content)
    logger.info(f"✓ Output saved to {output_file}")

    # Step 4: Display summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("\n[Step 4/4] Validation Summary")
    logger.info("=" * 80)
    logger.info(f"Execution Time: {duration:.1f}s")

    if result:
        logger.info("\n✓ Test generation completed")
        logger.info(f"  Syntax Valid: {'✓' if result.syntax_valid else '✗'}")
        logger.info(f"  Tests Pass: {'✓' if result.tests_pass else '✗'}")
        logger.info(f"  Coverage: {result.coverage_percentage:.1f}% (threshold: 70%)")
        logger.info(f"  Quality Score: {result.quality_score:.1f}/100")

        if result.issues:
            logger.info(f"\n  Issues ({len(result.issues)}):")
            for issue in result.issues[:5]:  # Show first 5 issues
                logger.info(f"    - {issue}")
            if len(result.issues) > 5:
                logger.info(
                    f"    ... and {len(result.issues) - 5} more (see output file)"
                )

        # Evaluation guidance
        logger.info("\n" + "=" * 80)
        logger.info("NEXT STEPS: Manual Evaluation")
        logger.info("=" * 80)
        logger.info(f"1. Review output file: {output_file}")
        logger.info("2. Evaluate generated test code for:")
        logger.info("   - Syntax correctness (valid Python)")
        logger.info("   - Semantic meaning (tests actually test functionality)")
        logger.info("   - Coverage (tests cover main functions)")
        logger.info("   - Code quality (assertions, edge cases, error handling)")
        logger.info("   - Pytest compatibility (follows pytest conventions)")
        logger.info("3. Categorize any issues:")
        logger.info("   - Model capability limitation")
        logger.info("   - Integration problem")
        logger.info("   - Prompt engineering issue")
        logger.info("   - Configuration problem")

        # Decision point
        if result.syntax_valid and result.quality_score >= 70:
            logger.info("\n✓ PRELIMINARY ASSESSMENT: Tests appear high quality")
            logger.info("  Recommendation: Free models are viable for test generation")
            logger.info(
                "  Action: Fix file creation limitation (runtime configuration)"
            )
        elif result.syntax_valid and result.quality_score >= 50:
            logger.info(
                "\n⚠ PRELIMINARY ASSESSMENT: Tests are acceptable but not great"
            )
            logger.info("  Recommendation: Consider hybrid approach")
            logger.info("  Action: Use free models for simple tasks, paid for complex")
        else:
            logger.info("\n✗ PRELIMINARY ASSESSMENT: Tests are poor quality")
            logger.info("  Recommendation: Free models may lack capability")
            logger.info("  Action: Consider paid models or redesign integration")

    else:
        logger.error("\n✗ Test generation failed")
        logger.error(f"  Error: {error_message}")
        logger.error("\n  Diagnosis needed:")
        logger.error("    - Check if error is due to file creation limitation")
        logger.error("    - Check if error is due to model capability")
        logger.error("    - Check if error is due to integration problem")
        logger.error(f"    - Review full traceback in {output_file}")

    logger.info("\n" + "=" * 80)
    logger.info(f"Validation complete. See {output_file} for full details.")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nUnexpected error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
