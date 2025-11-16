#!/usr/bin/env python3
"""
Example Usage of TTA Extended Session Quality Evaluation Framework

This script demonstrates how to use the extended evaluation framework
for comprehensive testing of TTA storytelling system quality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from testing.extended_evaluation.analysis_reporting import QualityAnalysisReporter
from testing.extended_evaluation.extended_session_framework import (
    ExtendedSessionTestFramework,
)
from testing.extended_evaluation.simulated_user_profiles import (
    DecisionMakingStyle,
    InteractionStyle,
    NarrativePreference,
    SimulatedUserProfile,
    UserBehaviorPattern,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_single_extended_test():
    """Example: Run a single extended test with custom configuration."""

    # Initialize framework
    framework = ExtendedSessionTestFramework()

    try:
        await framework.initialize_connections()

        # Create a custom user profile for testing
        custom_profile = SimulatedUserProfile(
            name="Example Test User",
            description="Custom profile for demonstration",
            age_range="25-35",
            gaming_experience="medium",
            tech_comfort="high",
            time_availability="medium",
            primary_concerns=["stress_management"],
            comfort_zones=["fantasy_settings"],
            challenge_areas=["decision_making"],
            preferred_intensity="medium",
            therapeutic_goals=["confidence_building"],
            behavior_pattern=UserBehaviorPattern(
                decision_making_style=DecisionMakingStyle.ANALYTICAL,
                interaction_style=InteractionStyle.ACTIVE_PARTICIPANT,
                narrative_preference=NarrativePreference.CHARACTER_DRIVEN,
                min_thinking_time=3.0,
                max_thinking_time=25.0,
                risk_tolerance=0.6,
                creativity_level=0.7,
            ),
        )

        # Get first available model and scenario
        first_model = next(iter(framework.models.values()))
        first_scenario = next(iter(framework.extended_scenarios.values()))

        # Run the test
        result = await framework._run_single_extended_test(
            first_model, custom_profile, first_scenario
        )

        # Display results

        if result.overall_quality_score:
            pass

        if result.strengths:
            pass

        if result.recommendations:
            pass

    except Exception as e:
        logger.error(f"Single test failed: {e}")
    finally:
        await framework.cleanup_connections()


async def example_custom_scenario_test():
    """Example: Create and test a custom scenario."""

    from testing.extended_evaluation.extended_session_framework import (
        ExtendedSessionScenario,
    )

    # Create a custom scenario
    ExtendedSessionScenario(
        name="Custom Mystery Scenario",
        description="A custom mystery scenario for testing",
        target_turns=20,
        max_duration_minutes=90,
        story_genre="mystery",
        world_type="contemporary",
        initial_setup={
            "setting": "small_town",
            "character_role": "detective",
            "mystery_type": "disappearance",
        },
        key_decision_points=[
            {"turn": 7, "type": "investigation_choice", "impact": "moderate"},
            {"turn": 14, "type": "confrontation", "impact": "major"},
        ],
        narrative_milestones=[
            {"turn": 10, "milestone": "first_clue"},
            {"turn": 20, "milestone": "resolution"},
        ],
        primary_metrics=["narrative_coherence", "user_engagement"],
        success_criteria={"narrative_coherence": 7.5, "user_engagement": 7.0},
        interaction_style="mixed",
        decision_complexity="moderate",
        pacing_preference="moderate",
    )

    # This scenario could be added to a framework and tested


async def example_data_analysis():
    """Example: Analyze existing evaluation data."""

    try:
        # Initialize reporter
        reporter = QualityAnalysisReporter()

        # Load existing data
        await reporter.load_evaluation_data()

        # Generate data summary
        summary = await reporter.generate_data_summary()

        if summary["total_sessions"] > 0:
            # Generate comprehensive report
            report = await reporter.generate_comprehensive_report()

            if report.key_findings:
                for _finding in report.key_findings[:2]:
                    pass

            # Generate visualizations
            await reporter.generate_visualizations(report)

        else:
            pass

    except Exception as e:
        logger.error(f"Data analysis failed: {e}")


async def example_user_behavior_simulation():
    """Example: Demonstrate user behavior simulation."""

    # Create different user profiles
    profiles = [
        SimulatedUserProfile(
            name="Speed Runner",
            description="Fast-paced gamer who makes quick decisions",
            age_range="18-25",
            gaming_experience="high",
            tech_comfort="high",
            time_availability="high",
            primary_concerns=["efficiency"],
            comfort_zones=["action_sequences"],
            challenge_areas=["patience"],
            preferred_intensity="high",
            therapeutic_goals=["impulse_control"],
            behavior_pattern=UserBehaviorPattern(
                decision_making_style=DecisionMakingStyle.IMPULSIVE,
                interaction_style=InteractionStyle.GOAL_ORIENTED,
                narrative_preference=NarrativePreference.ACTION_ORIENTED,
                min_thinking_time=1.0,
                max_thinking_time=10.0,
                risk_tolerance=0.9,
                creativity_level=0.4,
            ),
        ),
        SimulatedUserProfile(
            name="Thoughtful Explorer",
            description="Careful player who enjoys deep exploration",
            age_range="30-45",
            gaming_experience="medium",
            tech_comfort="medium",
            time_availability="medium",
            primary_concerns=["anxiety"],
            comfort_zones=["exploration"],
            challenge_areas=["time_pressure"],
            preferred_intensity="low",
            therapeutic_goals=["confidence_building"],
            behavior_pattern=UserBehaviorPattern(
                decision_making_style=DecisionMakingStyle.CAUTIOUS,
                interaction_style=InteractionStyle.EXPLORATORY,
                narrative_preference=NarrativePreference.WORLD_EXPLORATION,
                min_thinking_time=10.0,
                max_thinking_time=60.0,
                risk_tolerance=0.3,
                creativity_level=0.8,
            ),
        ),
    ]

    # Simulate behavior for each profile
    for profile in profiles:
        # Simulate thinking time for different decision complexities
        for complexity in ["simple", "moderate", "complex"]:
            profile.get_thinking_time(complexity)

        # Simulate response generation
        context = {
            "location": "mysterious_forest",
            "character": "wise_elder",
            "choices": ["investigate", "retreat", "ask_questions"],
        }

        profile.generate_response(context, turn=5)


async def main():
    """Run all examples."""

    # Run examples
    await example_single_extended_test()
    await example_custom_scenario_test()
    await example_data_analysis()
    await example_user_behavior_simulation()


if __name__ == "__main__":
    asyncio.run(main())
