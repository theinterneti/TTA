#!/usr/bin/env python3
"""
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
    print("\n" + "=" * 90)
    print("TTA EXTENDED SESSION QUALITY EVALUATION FRAMEWORK")
    print("=" * 90)
    print("Comprehensive testing of TTA storytelling system through extended sessions")
    print("Focus: Living worlds consistency, narrative coherence, user engagement")
    print("Session Length: 20-50+ turns | Duration: 2-4 hours per session")
    print("=" * 90 + "\n")


def print_framework_status(framework: ExtendedSessionTestFramework):
    """Print the status of the extended evaluation framework."""
    print("EXTENDED EVALUATION CONFIGURATION:")
    print("-" * 50)

    # Models
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    print(f"  Enabled Models: {enabled_models}")
    for _model_key, model in framework.models.items():
        if model.enabled:
            print(f"    ✓ {model.name} ({model.provider})")

    # Enhanced profiles
    print(f"  Enhanced User Profiles: {len(framework.profiles)}")
    for _profile_key, profile in framework.profiles.items():
        print(f"    • {profile.name}")

    # Extended scenarios
    print(f"  Extended Scenarios: {len(framework.extended_scenarios)}")
    for _scenario_key, scenario in framework.extended_scenarios.items():
        print(
            f"    • {scenario.name} ({scenario.target_turns} turns, {scenario.max_duration_minutes}min)"
        )

    return enabled_models > 0


def calculate_extended_test_estimates(framework: ExtendedSessionTestFramework):
    """Calculate and display extended test execution estimates."""
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    total_profiles = len(framework.profiles)
    total_scenarios = len(framework.extended_scenarios)

    total_tests = enabled_models * total_profiles * total_scenarios

    # Estimate duration based on extended scenario durations
    total_duration_minutes = (
        sum(
            scenario.max_duration_minutes
            for scenario in framework.extended_scenarios.values()
        )
        * enabled_models
        * total_profiles
    )

    print("\nEXTENDED TEST EXECUTION ESTIMATES:")
    print("-" * 50)
    print(f"  Total test combinations: {total_tests}")
    print(
        f"  Estimated duration: {total_duration_minutes} minutes ({total_duration_minutes / 60:.1f} hours)"
    )
    print(
        f"  Average turns per test: {sum(s.target_turns for s in framework.extended_scenarios.values()) / len(framework.extended_scenarios):.0f}"
    )
    print(
        f"  Total turns to execute: {sum(s.target_turns for s in framework.extended_scenarios.values()) * enabled_models * total_profiles}"
    )

    if total_duration_minutes > 480:  # 8 hours
        print(
            f"\n  ⚠️  WARNING: Extended evaluation will take {total_duration_minutes / 60:.1f} hours"
        )
        print("     Consider running with --quick-sample for initial testing")


async def run_quick_sample(framework: ExtendedSessionTestFramework):
    """Run a quick sample test with one model, profile, and scenario."""
    print("\n🚀 RUNNING QUICK SAMPLE TEST...")
    print("Testing first enabled model with first profile and shortest scenario")

    # Get first enabled model
    first_model = None
    for model in framework.models.values():
        if model.enabled:
            first_model = model
            break

    if not first_model:
        print("❌ No enabled models found!")
        return

    # Get first profile and shortest scenario
    first_profile = next(iter(framework.profiles.values()))
    shortest_scenario = min(
        framework.extended_scenarios.values(), key=lambda s: s.target_turns
    )

    print(f"  Model: {first_model.name}")
    print(f"  Profile: {first_profile.name}")
    print(
        f"  Scenario: {shortest_scenario.name} ({shortest_scenario.target_turns} turns)"
    )

    try:
        await framework.initialize_connections()

        # Run single extended test
        result = await framework._run_single_extended_test(
            first_model, first_profile, shortest_scenario
        )

        print("\n✅ QUICK SAMPLE COMPLETED")
        print(f"  Session ID: {result.session_id}")
        print(f"  Completed Turns: {result.completed_turns}/{result.total_turns}")
        print(f"  Duration: {result.session_duration_minutes:.1f} minutes")
        print(f"  Errors: {result.error_count}")

        if result.overall_quality_score:
            print(f"  Overall Quality: {result.overall_quality_score:.2f}/10")
            if result.overall_quality_score >= 7.5:
                print("  🎉 Good performance! Ready for comprehensive evaluation.")
            else:
                print("  ⚠️  Performance below target. Consider configuration review.")

        # Show quality breakdown if available
        if result.final_narrative_coherence:
            print(f"  Narrative Coherence: {result.final_narrative_coherence:.2f}/10")
        if result.final_world_consistency:
            print(f"  World Consistency: {result.final_world_consistency:.2f}/10")
        if result.final_user_engagement:
            print(f"  User Engagement: {result.final_user_engagement:.2f}/10")

    except Exception as e:
        print(f"❌ Quick sample test failed: {e}")
        logger.error(f"Quick sample test error: {e}")
    finally:
        await framework.cleanup_connections()


async def run_comprehensive_evaluation(framework: ExtendedSessionTestFramework):
    """Run the full comprehensive extended session evaluation."""
    print("\n🚀 RUNNING COMPREHENSIVE EXTENDED SESSION EVALUATION...")
    print("This will execute all model/profile/scenario combinations")

    try:
        # Run comprehensive evaluation
        analysis = await framework.run_extended_evaluation()

        print("\n✅ COMPREHENSIVE EXTENDED EVALUATION COMPLETED!")
        print("=" * 70)

        # Display summary results
        summary = analysis.get("summary", {})
        print("SUMMARY RESULTS:")
        print(f"  Total Extended Sessions: {summary.get('total_extended_sessions', 0)}")
        print(f"  Total Turns Executed: {summary.get('total_turns_executed', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1%}")
        print(
            f"  Average Narrative Coherence: {summary.get('average_narrative_coherence', 0):.2f}/10"
        )

        # Generate comprehensive analysis report
        print("\n📊 GENERATING COMPREHENSIVE ANALYSIS REPORT...")
        reporter = QualityAnalysisReporter()
        await reporter.load_evaluation_data()
        report = await reporter.generate_comprehensive_report()

        print(f"✅ ANALYSIS REPORT GENERATED: {report.report_id}")
        print("  Report saved to: testing/results/extended_evaluation/reports/")

        # Display key findings
        if report.key_findings:
            print("\nKEY FINDINGS:")
            for finding in report.key_findings[:3]:  # Top 3 findings
                print(f"  • {finding}")

        # Display model rankings
        if report.model_rankings:
            print("\nMODEL RANKINGS:")
            for ranking in report.model_rankings[:3]:  # Top 3 models
                print(
                    f"  {ranking['rank']}. {ranking['model']:<25} {ranking['overall_score']:.2f}/10"
                )

        # Display recommendations
        if report.improvement_recommendations:
            print("\nIMPROVEMENT RECOMMENDATIONS:")
            for rec in report.improvement_recommendations[:3]:  # Top 3 recommendations
                print(f"  • {rec}")

        # Generate visualizations
        print("\n📈 GENERATING VISUALIZATIONS...")
        viz_files = await reporter.generate_visualizations(report)
        if viz_files:
            print(f"  Generated {len(viz_files)} visualization files")

        print("\n📋 QUALITY BASELINES ESTABLISHED:")
        print(
            f"  Narrative Coherence Baseline: {report.narrative_coherence_baseline:.2f}/10"
        )
        print(
            f"  World Consistency Baseline: {report.world_consistency_baseline:.2f}/10"
        )
        print(f"  User Engagement Baseline: {report.user_engagement_baseline:.2f}/10")

        print("\n📁 All results saved to: testing/results/extended_evaluation/")

    except Exception as e:
        print(f"❌ Comprehensive evaluation failed: {e}")
        logger.error(f"Comprehensive evaluation error: {e}")
        raise


async def run_analysis_only():
    """Run analysis on existing evaluation data."""
    print("\n📊 RUNNING ANALYSIS ON EXISTING DATA...")

    try:
        reporter = QualityAnalysisReporter()
        await reporter.load_evaluation_data()

        # Check if data exists
        data_summary = await reporter.generate_data_summary()
        if data_summary["total_sessions"] == 0:
            print("❌ No evaluation data found!")
            print("   Run evaluation first with --mode comprehensive")
            return

        print(f"Found data for {data_summary['total_sessions']} sessions")

        # Generate comprehensive report
        report = await reporter.generate_comprehensive_report()

        print(f"✅ ANALYSIS COMPLETED: {report.report_id}")

        # Display summary
        print("\nANALYSIS SUMMARY:")
        print(f"  Sessions Analyzed: {report.total_sessions}")
        print(f"  Total Turns: {report.total_turns}")
        print(f"  Test Duration: {report.total_test_duration_hours:.1f} hours")

        if report.model_rankings:
            print("\nTOP PERFORMING MODEL:")
            top_model = report.model_rankings[0]
            print(f"  {top_model['model']}: {top_model['overall_score']:.2f}/10")

        # Generate visualizations
        viz_files = await reporter.generate_visualizations(report)
        print(f"Generated {len(viz_files)} visualization files")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
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
            print("\n✅ Extended evaluation framework loaded successfully!")
            if framework_ok:
                print("💡 Run with --mode quick-sample for a quick test")
                print("💡 Run with --mode comprehensive for full evaluation")
                print("💡 Run with --mode analysis-only to analyze existing data")
            return

        if not framework_ok:
            print("\n❌ Cannot run evaluation: No models enabled")
            return

        # Confirmation for long-running tests
        if args.mode == "comprehensive" and not args.force:
            response = input(
                "\n⚠️  This will run a comprehensive evaluation that may take several hours.\n   Continue? (y/N): "
            )
            if response.lower() != "y":
                print("Evaluation cancelled.")
                return

        # Run evaluation based on mode
        if args.mode == "quick-sample":
            asyncio.run(run_quick_sample(framework))
        elif args.mode == "comprehensive":
            asyncio.run(run_comprehensive_evaluation(framework))

    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        print(f"💡 Make sure {args.config} exists")
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main execution error: {e}")
        raise


if __name__ == "__main__":
    main()
