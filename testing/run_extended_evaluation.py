#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Testing/Run_extended_evaluation]]
TTA Extended Session Quality Evaluation Runner

Comprehensive testing framework for evaluating TTA storytelling system
through extended sessions (20-50+ turns) with focus on living worlds
consistency, narrative coherence, and user engagement over time.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from testing.extended_evaluation.analysis_reporting import QualityAnalysisReporter
from testing.extended_evaluation.extended_session_framework import (
    ExtendedSessionTestFramework,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("testing/extended_evaluation_execution.log"),
    ],
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print the extended evaluation banner."""


def print_framework_status(framework: ExtendedSessionTestFramework):
    """Print the status of the extended evaluation framework."""

    # Models
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    for model in framework.models.values():
        if model.enabled:
            pass

    # Enhanced profiles
    for _profile_key, _profile in framework.profiles.items():
        pass

    # Extended scenarios
    for _scenario_key, _scenario in framework.extended_scenarios.items():
        pass

    return enabled_models > 0


def calculate_extended_test_estimates(framework: ExtendedSessionTestFramework):
    """Calculate and display extended test execution estimates."""
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    total_profiles = len(framework.profiles)
    total_scenarios = len(framework.extended_scenarios)

    enabled_models * total_profiles * total_scenarios

    # Estimate duration based on extended scenario durations
    total_duration_minutes = (
        sum(
            scenario.max_duration_minutes
            for scenario in framework.extended_scenarios.values()
        )
        * enabled_models
        * total_profiles
    )

    if total_duration_minutes > 480:  # 8 hours
        pass


async def run_quick_sample(framework: ExtendedSessionTestFramework):
    """Run a quick sample test with one model, profile, and scenario."""

    # Get first enabled model
    first_model = None
    for model in framework.models.values():
        if model.enabled:
            first_model = model
            break

    if not first_model:
        return

    # Get first profile and shortest scenario
    first_profile = next(iter(framework.profiles.values()))
    shortest_scenario = min(
        framework.extended_scenarios.values(), key=lambda s: s.target_turns
    )

    try:
        await framework.initialize_connections()

        # Run single extended test
        result = await framework._run_single_extended_test(
            first_model, first_profile, shortest_scenario
        )

        if result.overall_quality_score:
            if result.overall_quality_score >= 7.5:
                pass
            else:
                pass

        # Show quality breakdown if available
        if result.final_narrative_coherence:
            pass
        if result.final_world_consistency:
            pass
        if result.final_user_engagement:
            pass

    except Exception as e:
        logger.error(f"Quick sample test error: {e}")
    finally:
        await framework.cleanup_connections()


async def run_comprehensive_evaluation(framework: ExtendedSessionTestFramework):
    """Run the full comprehensive extended session evaluation."""

    try:
        # Run comprehensive evaluation
        analysis = await framework.run_extended_evaluation()

        # Display summary results
        analysis.get("summary", {})

        # Generate comprehensive analysis report
        reporter = QualityAnalysisReporter()
        await reporter.load_evaluation_data()
        report = await reporter.generate_comprehensive_report()

        # Display key findings
        if report.key_findings:
            for _finding in report.key_findings[:3]:  # Top 3 findings
                pass

        # Display model rankings
        if report.model_rankings:
            for _ranking in report.model_rankings[:3]:  # Top 3 models
                pass

        # Display recommendations
        if report.improvement_recommendations:
            for _rec in report.improvement_recommendations[:3]:  # Top 3 recommendations
                pass

        # Generate visualizations
        viz_files = await reporter.generate_visualizations(report)
        if viz_files:
            pass

    except Exception as e:
        logger.error(f"Comprehensive evaluation error: {e}")
        raise


async def run_analysis_only():
    """Run analysis on existing evaluation data."""

    try:
        reporter = QualityAnalysisReporter()
        await reporter.load_evaluation_data()

        # Check if data exists
        data_summary = await reporter.generate_data_summary()
        if data_summary["total_sessions"] == 0:
            return

        # Generate comprehensive report
        report = await reporter.generate_comprehensive_report()

        # Display summary

        if report.model_rankings:
            report.model_rankings[0]

        # Generate visualizations
        await reporter.generate_visualizations(report)

    except Exception as e:
        logger.error(f"Analysis error: {e}")


def main():
    """Main entry point for the extended evaluation runner."""
    parser = argparse.ArgumentParser(
        description="TTA Extended Session Quality Evaluation Runner"
    )
    parser.add_argument(
        "--mode",
        choices=["status", "quick-sample", "comprehensive", "analysis-only"],
        default="status",
        help="Evaluation mode to run (default: status)",
    )
    parser.add_argument(
        "--config",
        default="testing/configs/extended_evaluation_config.yaml",
        help="Path to extended evaluation configuration file",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force execution without confirmation prompts",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print_banner()

    try:
        if args.mode == "analysis-only":
            asyncio.run(run_analysis_only())
            return

        # Initialize framework
        framework = ExtendedSessionTestFramework(config_path=args.config)

        # Display configuration status
        framework_ok = print_framework_status(framework)
        calculate_extended_test_estimates(framework)

        if args.mode == "status":
            if framework_ok:
                pass
            return

        if not framework_ok:
            return

        # Confirmation for long-running tests
        if args.mode == "comprehensive" and not args.force:
            response = input(
                "\n⚠️  This will run a comprehensive evaluation that may take several hours.\n   Continue? (y/N): "
            )
            if response.lower() != "y":
                return

        # Run evaluation based on mode
        if args.mode == "quick-sample":
            asyncio.run(run_quick_sample(framework))
        elif args.mode == "comprehensive":
            asyncio.run(run_comprehensive_evaluation(framework))

    except FileNotFoundError:
        pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        raise


if __name__ == "__main__":
    main()
