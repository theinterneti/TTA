#!/usr/bin/env python3
"""
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
    print("\n" + "=" * 80)
    print("TTA SINGLE-PLAYER STORYTELLING EXPERIENCE TESTING FRAMEWORK")
    print("=" * 80)
    print("Testing AI models for user enjoyment and game-first presentation")
    print("with subtle therapeutic integration")
    print("=" * 80 + "\n")


def print_model_status(framework: SinglePlayerTestFramework):
    """Print the status of configured models."""
    print("CONFIGURED MODELS:")
    print("-" * 40)

    enabled_count = 0
    for _model_key, model in framework.models.items():
        status = "✓ ENABLED" if model.enabled else "✗ DISABLED"
        provider = f"({model.provider})"
        print(f"  {model.name:<30} {provider:<12} {status}")
        if model.enabled:
            enabled_count += 1

    print(f"\nTotal enabled models: {enabled_count}")

    if enabled_count == 0:
        print("\n⚠️  WARNING: No models are enabled!")
        print(
            "   Please configure at least one model in testing/model_testing_config.yaml"
        )
        return False

    return True


def print_test_profiles(framework: SinglePlayerTestFramework):
    """Print the configured test profiles."""
    print("\nTEST PROFILES:")
    print("-" * 40)

    for _profile_key, profile in framework.profiles.items():
        concerns = profile.therapeutic_profile.get("primary_concerns", [])
        concerns_str = ", ".join(concerns[:2]) + ("..." if len(concerns) > 2 else "")
        print(f"  {profile.name:<35} [{concerns_str}]")

    print(f"\nTotal test profiles: {len(framework.profiles)}")


def print_test_scenarios(framework: SinglePlayerTestFramework):
    """Print the configured test scenarios."""
    print("\nTEST SCENARIOS:")
    print("-" * 40)

    for _scenario_key, scenario in framework.scenarios.items():
        duration = f"{scenario.duration_minutes}min"
        sessions = f"{scenario.sessions} session{'s' if scenario.sessions > 1 else ''}"
        print(f"  {scenario.name:<35} [{duration}, {sessions}]")

    print(f"\nTotal test scenarios: {len(framework.scenarios)}")


def calculate_test_estimates(framework: SinglePlayerTestFramework):
    """Calculate and display test execution estimates."""
    enabled_models = sum(1 for model in framework.models.values() if model.enabled)
    total_profiles = len(framework.profiles)
    total_scenarios = len(framework.scenarios)

    total_tests = enabled_models * total_profiles * total_scenarios

    # Estimate duration based on scenario durations
    total_duration_minutes = (
        sum(scenario.duration_minutes for scenario in framework.scenarios.values())
        * enabled_models
        * total_profiles
    )

    print("\nTEST EXECUTION ESTIMATES:")
    print("-" * 40)
    print(f"  Total test combinations: {total_tests}")
    print(
        f"  Estimated duration: {total_duration_minutes} minutes ({total_duration_minutes / 60:.1f} hours)"
    )
    print(f"  Models to test: {enabled_models}")
    print(f"  Profiles per model: {total_profiles}")
    print(f"  Scenarios per profile: {total_scenarios}")


async def run_quick_test(framework: SinglePlayerTestFramework):
    """Run a quick test with a subset of configurations."""
    print("\n🚀 RUNNING QUICK TEST...")
    print("Testing first enabled model with first profile and first scenario")

    # Get first enabled model
    first_model = None
    for model in framework.models.values():
        if model.enabled:
            first_model = model
            break

    if not first_model:
        print("❌ No enabled models found!")
        return

    # Get first profile and scenario
    first_profile = next(iter(framework.profiles.values()))
    first_scenario = next(iter(framework.scenarios.values()))

    print(f"  Model: {first_model.name}")
    print(f"  Profile: {first_profile.name}")
    print(f"  Scenario: {first_scenario.name}")

    try:
        await framework.initialize_connections()

        # Run single test
        result = await framework._run_single_test(
            first_model, first_profile, first_scenario
        )

        print("\n✅ QUICK TEST COMPLETED")
        print(f"  Overall Score: {result.overall_score:.2f}/10")
        print(f"  Duration: {result.duration_seconds:.1f} seconds")
        print(f"  Errors: {result.error_count}")

        if result.overall_score and result.overall_score >= 7.0:
            print("  🎉 Good performance! Ready for comprehensive testing.")
        else:
            print("  ⚠️  Performance below target. Consider model configuration review.")

    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        logger.error(f"Quick test error: {e}")
    finally:
        await framework.cleanup_connections()


async def run_comprehensive_test(framework: SinglePlayerTestFramework):
    """Run the full comprehensive test suite."""
    print("\n🚀 RUNNING COMPREHENSIVE TEST SUITE...")

    try:
        analysis = await framework.run_comprehensive_test()

        print("\n✅ COMPREHENSIVE TESTING COMPLETED!")
        print("=" * 60)

        # Display summary results
        summary = analysis.get("summary", {})
        print("SUMMARY RESULTS:")
        print(f"  Total Tests: {summary.get('total_tests', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"  Duration: {summary.get('total_duration_hours', 0):.1f} hours")

        avg_scores = summary.get("average_scores", {})
        print("\nAVERAGE SCORES:")
        print(f"  Overall: {avg_scores.get('overall', 0):.2f}/10")
        print(f"  Narrative Quality: {avg_scores.get('narrative_quality', 0):.2f}/10")
        print(f"  User Engagement: {avg_scores.get('user_engagement', 0):.2f}/10")
        print(
            f"  Therapeutic Integration: {avg_scores.get('therapeutic_integration', 0):.2f}/10"
        )
        print(
            f"  Technical Performance: {avg_scores.get('technical_performance', 0):.2f}/10"
        )

        # Display recommendations
        recommendations = analysis.get("recommendations", {})
        primary_rec = recommendations.get("primary_recommendation", {})
        print("\nPRIMARY RECOMMENDATION:")
        print(f"  Best Model: {primary_rec.get('model', 'N/A')}")
        print(f"  Score: {primary_rec.get('overall_score', 0):.2f}/10")
        print(f"  Rationale: {primary_rec.get('rationale', 'N/A')}")

        # Display model rankings
        rankings = recommendations.get("model_rankings", [])
        if rankings:
            print("\nMODEL RANKINGS:")
            for ranking in rankings[:3]:  # Top 3
                print(
                    f"  {ranking['rank']}. {ranking['model']:<25} {ranking['average_score']:.2f}/10"
                )

        print("\n📊 Detailed results saved to: testing/results/")
        print("📋 Generate report using the model comparison matrix template")

    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
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
            print("\n✅ Configuration loaded successfully!")
            if models_ok:
                print("💡 Run with --mode quick for a quick test")
                print("💡 Run with --mode comprehensive for full testing")
            return

        if not models_ok:
            print("\n❌ Cannot run tests: No models enabled")
            return

        # Run tests based on mode
        if args.mode == "quick":
            asyncio.run(run_quick_test(framework))
        elif args.mode == "comprehensive":
            asyncio.run(run_comprehensive_test(framework))

    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        print(f"💡 Make sure {args.config} exists")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Main execution error: {e}")
        raise


if __name__ == "__main__":
    main()
