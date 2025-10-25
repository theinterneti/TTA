#!/usr/bin/env python3
"""CLI interface for unit test generation using OpenHands.

This script provides a command-line interface for generating unit tests
for TTA's codebase using the OpenHands SDK.

Usage:
    # Single file
    python scripts/generate_tests.py src/agent_orchestration/tools/client.py --coverage 80

    # Package
    python scripts/generate_tests.py src/agent_orchestration/tools/ --package --coverage 75
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from pydantic import SecretStr

# Add src to Python path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root / "src"))

# NOTE: This script should be run with `uv run python scripts/generate_tests.py`
# to ensure proper dependencies are available.

try:
    from agent_orchestration.openhands_integration.config import OpenHandsConfig
    from agent_orchestration.openhands_integration.test_generation_models import (
        TestTaskSpecification,
    )
    from agent_orchestration.openhands_integration.test_generation_service import (
        UnitTestGenerationService,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nThis script must be run with 'uv run python scripts/generate_tests.py'")
    print("to ensure proper dependencies are available.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate unit tests using OpenHands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for a single file
  python scripts/generate_tests.py src/agent_orchestration/tools/client.py --coverage 80

  # Generate tests for an entire package
  python scripts/generate_tests.py src/agent_orchestration/tools/ --package --coverage 75

  # Increase timeout for complex files
  python scripts/generate_tests.py src/agent_orchestration/tools/client.py --timeout 900
        """,
    )

    parser.add_argument(
        "target_file",
        type=Path,
        help="File or package to generate tests for",
    )
    parser.add_argument(
        "--coverage",
        type=float,
        default=70.0,
        help="Coverage threshold percentage (default: 70.0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="Timeout in seconds (default: 600.0)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum iterations for retry (default: 5)",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Generate tests for entire package",
    )

    return parser.parse_args()


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()

    # Validate environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        logger.error("Please set it with: export OPENROUTER_API_KEY=your-api-key")
        return 1

    # Get workspace path
    workspace_path = Path(__file__).parent.parent.resolve()
    logger.info(f"Workspace path: {workspace_path}")

    # Create configuration
    config = OpenHandsConfig(
        api_key=SecretStr(api_key),
        model="deepseek/deepseek-v3:free",  # Free model
        workspace_path=workspace_path,
        timeout_seconds=args.timeout,
    )

    # Create service
    service = UnitTestGenerationService(config)

    try:
        if args.package:
            # Generate tests for package
            logger.info(f"Generating tests for package: {args.target_file}")
            results = await service.generate_package_tests(
                package_path=args.target_file,
                coverage_threshold=args.coverage,
            )

            # Display results
            print("\n" + "=" * 80)
            print("PACKAGE TEST GENERATION RESULTS")
            print("=" * 80)

            total_files = len(results)
            successful_files = sum(
                1
                for r in results.values()
                if r.syntax_valid
                and r.tests_pass
                and r.coverage_percentage >= args.coverage
            )

            for file_path, result in results.items():
                status = (
                    "✓"
                    if (
                        result.syntax_valid
                        and result.tests_pass
                        and result.coverage_percentage >= args.coverage
                    )
                    else "✗"
                )
                print(f"\n{status} {file_path}")
                print(f"  Coverage: {result.coverage_percentage:.1f}%")
                print(f"  Quality Score: {result.quality_score:.1f}/100")
                if result.issues:
                    print(f"  Issues: {len(result.issues)}")
                    for issue in result.issues[:3]:  # Show first 3 issues
                        print(f"    - {issue}")

            print("\n" + "=" * 80)
            print(f"Summary: {successful_files}/{total_files} files successful")
            print("=" * 80)

            return 0 if successful_files == total_files else 1

        # Generate tests for single file
        logger.info(f"Generating tests for file: {args.target_file}")

        spec = TestTaskSpecification(
            target_file=args.target_file,
            coverage_threshold=args.coverage,
            timeout_seconds=args.timeout,
        )

        result = await service.generate_tests(spec, max_iterations=args.max_iterations)

        # Display results
        print("\n" + "=" * 80)
        print("TEST GENERATION RESULTS")
        print("=" * 80)
        print(f"Target File: {args.target_file}")
        print(f"Test File: {result.test_file_path}")
        print(f"\nSyntax Valid: {'✓' if result.syntax_valid else '✗'}")
        print(f"Tests Pass: {'✓' if result.tests_pass else '✗'}")
        print(
            f"Coverage: {result.coverage_percentage:.1f}% (threshold: {args.coverage}%)"
        )
        print(f"Conventions Followed: {'✓' if result.conventions_followed else '✗'}")
        print(f"Quality Score: {result.quality_score:.1f}/100")

        if result.issues:
            print(f"\nIssues ({len(result.issues)}):")
            for issue in result.issues:
                print(f"  - {issue}")

        print("=" * 80)

        # Determine success
        success = (
            result.syntax_valid
            and result.tests_pass
            and result.coverage_percentage >= args.coverage
            and result.conventions_followed
        )

        if success:
            print("\n✓ Test generation successful!")
            return 0
        print("\n✗ Test generation failed or incomplete")
        return 1

    except Exception as e:
        logger.exception(f"Error during test generation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
