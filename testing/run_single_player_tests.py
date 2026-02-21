#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Testing/Run_single_player_tests]]
TTA Single-Player Storytelling Experience Test Runner

This script provides a simple interface to run comprehensive testing
of AI models for TTA's single-player storytelling experience.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from testing.single_player_test_framework import SinglePlayerTestFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("testing/test_execution.log"),
    ],
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print the test runner banner."""


def print_model_status(framework: SinglePlayerTestFramework):
    """Print the status of configured models."""

    enabled_count = 0
    for model in framework.models.values():
        if model.enabled:
            enabled_count += 1

    return enabled_count != 0


def print_test_profiles(framework: SinglePlayerTestFramework):
    """Print the configured test profiles."""

    for profile in framework.profiles.values():
        concerns = profile.therapeutic_profile.get("primary_concerns", [])
        ", ".join(concerns[:2]) + ("..." if len(concerns) > 2 else "")


def print_test_scenarios(framework: SinglePlayerTestFramework):
    """Print the configured test scenarios."""

    for _scenario in framework.scenarios.values():
        pass


def calculate_test_estimates(framework: SinglePlayerTestFramework):
    """Calculate and display test execution estimates."""
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    total_profiles = len(framework.profiles)
    total_scenarios = len(framework.scenarios)

    enabled_models * total_profiles * total_scenarios

    # Estimate duration based on scenario durations
    (
        sum(scenario.duration_minutes for scenario in framework.scenarios.values())
        * enabled_models
        * total_profiles
    )


async def run_quick_test(framework: SinglePlayerTestFramework):
    """Run a quick test with a subset of configurations."""

    # Get first enabled model
    first_model = None
    for model in framework.models.values():
        if model.enabled:
            first_model = model
            break

    if not first_model:
        return

    # Get first profile and scenario
    first_profile = next(iter(framework.profiles.values()))
    first_scenario = next(iter(framework.scenarios.values()))

    try:
        await framework.initialize_connections()

        # Run single test
        result = await framework._run_single_test(
            first_model, first_profile, first_scenario
        )

        if result.overall_score and result.overall_score >= 7.0:
            pass
        else:
            pass

    except Exception as e:
        logger.error(f"Quick test error: {e}")
    finally:
        await framework.cleanup_connections()


async def run_comprehensive_test(framework: SinglePlayerTestFramework):
    """Run the full comprehensive test suite."""

    try:
        analysis = await framework.run_comprehensive_test()

        # Display summary results
        summary = analysis.get("summary", {})

        summary.get("average_scores", {})

        # Display recommendations
        recommendations = analysis.get("recommendations", {})
        recommendations.get("primary_recommendation", {})

        # Display model rankings
        rankings = recommendations.get("model_rankings", [])
        if rankings:
            for _ranking in rankings[:3]:  # Top 3
                pass

    except Exception as e:
        logger.error(f"Comprehensive test error: {e}")
        raise


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="TTA Single-Player Storytelling Experience Test Runner"
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "comprehensive", "status"],
        default="status",
        help="Test mode to run (default: status)",
    )
    parser.add_argument(
        "--config",
        default="testing/model_testing_config.yaml",
        help="Path to test configuration file",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print_banner()

    try:
        # Initialize framework
        framework = SinglePlayerTestFramework(config_path=args.config)

        # Display configuration status
        models_ok = print_model_status(framework)
        print_test_profiles(framework)
        print_test_scenarios(framework)
        calculate_test_estimates(framework)

        if args.mode == "status":
            if models_ok:
                pass
            return

        if not models_ok:
            return

        # Run tests based on mode
        if args.mode == "quick":
            asyncio.run(run_quick_test(framework))
        elif args.mode == "comprehensive":
            asyncio.run(run_comprehensive_test(framework))

    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        raise


if __name__ == "__main__":
    main()
