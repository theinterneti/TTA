#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Testing/Run_enhanced_evaluation]]
Enhanced TTA Extended Session Quality Evaluation Runner

Comprehensive testing framework with all systematic improvements:
1. Extended sessions (30-50+ turns) with memory management
2. Multi-model comparison framework
3. Diversified scenario library (15+ scenarios across 7 genres)
4. Real user testing integration
5. Performance optimization and caching

Usage:
    python testing/run_enhanced_evaluation.py --mode comprehensive --models llama_3_3_8b_instruct,gpt_4_turbo
    python testing/run_enhanced_evaluation.py --mode extended_sessions --turns 50
    python testing/run_enhanced_evaluation.py --mode multi_model_comparison
    python testing/run_enhanced_evaluation.py --mode real_user_testing
    python testing/run_enhanced_evaluation.py --mode performance_benchmark
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from testing.extended_evaluation.analysis_reporting import QualityAnalysisReporter
from testing.extended_evaluation.extended_session_framework import (
    ExtendedSessionTestFramework,
)
from testing.extended_evaluation.multi_model_comparison import MultiModelComparator
from testing.extended_evaluation.performance_optimization import (
    PerformanceOptimizationFramework,
)
from testing.extended_evaluation.real_user_testing import RealUserTestingFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedEvaluationRunner:
    """
    Enhanced evaluation runner with all systematic improvements integrated.
    """

    def __init__(self):
        """Initialize enhanced evaluation runner."""
        self.extended_framework = ExtendedSessionTestFramework()
        self.multi_model_comparator = MultiModelComparator()
        self.real_user_framework = RealUserTestingFramework()
        self.performance_optimizer = PerformanceOptimizationFramework()
        self.analysis_reporter = QualityAnalysisReporter()

        logger.info("EnhancedEvaluationRunner initialized with all improvements")

    async def run_extended_sessions(self, args):
        """Run extended session testing (30-50+ turns)."""

        # Start performance optimization
        await self.performance_optimizer.start_optimization()

        try:
            # Configure extended sessions
            scenarios = [
                "fantasy_extended_30",
                "contemporary_extended_40",
                "epic_fantasy_50",
            ]
            if args.turns:
                # Filter scenarios by turn count
                if args.turns <= 30:
                    scenarios = ["fantasy_extended_30"]
                elif args.turns <= 40:
                    scenarios = ["fantasy_extended_30", "contemporary_extended_40"]

            models = (
                args.models.split(",") if args.models else ["llama_3_3_8b_instruct"]
            )
            profiles = ["typical_user", "marathon_user", "deep_explorer"]

            # Run extended session tests
            results = []
            for scenario in scenarios:
                for model in models:
                    for profile in profiles:
                        result = await self.extended_framework.run_extended_session(
                            model_name=model,
                            scenario_name=scenario,
                            user_profile=profile,
                        )

                        if result:
                            results.append(result)

                            # Calculate extended metrics
                            (result.calculate_extended_quality_metrics())

            # Generate comprehensive report
            if results:
                sum(
                    r.calculate_extended_quality_metrics().get(
                        "avg_narrative_coherence", 0
                    )
                    for r in results
                ) / len(results)
            else:
                pass

            # Save results
            datetime.now().strftime("%Y%m%d_%H%M%S")

            # Performance report
            perf_report = await self.performance_optimizer.get_performance_report()
            if "current_metrics" in perf_report:
                pass
            else:
                pass

        finally:
            await self.performance_optimizer.stop_optimization()

    async def run_multi_model_comparison(self, args):
        """Run multi-model comparison testing."""

        # Configure models for comparison
        models = (
            args.models.split(",")
            if args.models
            else ["llama_3_3_8b_instruct", "gpt_4_turbo", "claude_3_5_sonnet"]
        )

        scenarios = ["fantasy_baseline", "contemporary_baseline", "fantasy_extended_30"]
        user_profile = "typical_user"

        # Run comparisons
        comparison_results = []
        for scenario in scenarios:
            result = await self.multi_model_comparator.run_model_comparison(
                models=models,
                scenario_name=scenario,
                user_profile=user_profile,
                runs_per_model=3,
            )

            comparison_results.append(result)

            # Display results
            if result.overall_ranking:
                pass

        # Generate comprehensive comparison report
        for result in comparison_results:
            await self.multi_model_comparator.generate_comparison_report(result)
            if result.overall_ranking:
                pass

    async def run_diversified_scenarios(self, args):
        """Run testing across diversified scenario library."""

        # All available scenarios across genres
        scenarios = [
            # Sci-Fi
            "space_colony_crisis",
            "ai_consciousness_dilemma",
            # Mystery
            "small_town_secrets",
            "corporate_espionage",
            # Historical
            "civil_rights_movement",
            "wwii_resistance",
            # Horror (Psychological)
            "haunted_family_home",
            "isolation_experiment",
            # Romance
            "second_chance_love",
            "workplace_romance_ethics",
            # Edge Cases
            "moral_dilemma_cascade",
            "narrative_dead_end_recovery",
        ]

        model = args.models.split(",")[0] if args.models else "llama_3_3_8b_instruct"
        user_profile = "typical_user"

        # Run scenario tests
        results = []
        genre_results = {}

        for scenario in scenarios:
            result = await self.extended_framework.run_extended_session(
                model_name=model, scenario_name=scenario, user_profile=user_profile
            )

            if result:
                results.append(result)

                # Categorize by genre (simplified)
                genre = self._get_scenario_genre(scenario)
                if genre not in genre_results:
                    genre_results[genre] = []
                genre_results[genre].append(result)

        # Genre analysis
        for genre, genre_results_list in genre_results.items():
            sum(r.final_narrative_coherence or 0 for r in genre_results_list) / len(
                genre_results_list
            )

    def _get_scenario_genre(self, scenario_name: str) -> str:
        """Get genre for scenario name."""
        genre_mapping = {
            "space_colony_crisis": "Sci-Fi",
            "ai_consciousness_dilemma": "Sci-Fi",
            "small_town_secrets": "Mystery",
            "corporate_espionage": "Mystery",
            "civil_rights_movement": "Historical",
            "wwii_resistance": "Historical",
            "haunted_family_home": "Horror",
            "isolation_experiment": "Horror",
            "second_chance_love": "Romance",
            "workplace_romance_ethics": "Romance",
            "moral_dilemma_cascade": "Edge Case",
            "narrative_dead_end_recovery": "Edge Case",
        }
        return genre_mapping.get(scenario_name, "Unknown")

    async def run_real_user_testing_demo(self, args):
        """Run real user testing demonstration."""

        # Demonstrate participant registration
        from testing.extended_evaluation.real_user_testing import ParticipantType

        participant_id = await self.real_user_framework.register_participant(
            original_id="demo_user_001",
            participant_type=ParticipantType.BETA_TESTER,
            consent_details={
                "data_collection": True,
                "session_recording": True,
                "analysis": True,
                "follow_up": False,
                "anonymization_level": "full",
                "retention_days": 365,
                "age_range": "25-35",
                "gaming_experience": "intermediate",
                "tech_comfort": "high",
            },
        )

        # Demonstrate session start
        session_id = await self.real_user_framework.start_user_session(
            participant_id=participant_id,
            scenario_name="fantasy_baseline",
            model_name="llama_3_3_8b_instruct",
        )

        if session_id:
            # Simulate some interactions
            for turn in range(3):
                await self.real_user_framework.record_user_interaction(
                    session_id=session_id,
                    user_input=f"Demo user input for turn {turn + 1}",
                    system_response=f"Demo system response for turn {turn + 1}",
                    response_time=2.5,
                    quality_metrics={
                        "narrative_coherence": 7.8,
                        "world_consistency": 8.0,
                        "user_engagement": 7.5,
                        "user_satisfaction": 8.2,
                    },
                )

            # End session
            await self.real_user_framework.end_user_session(session_id)

        # Generate anonymized dataset
        await self.real_user_framework.generate_anonymized_research_dataset()

    async def run_performance_benchmark(self, args):
        """Run performance benchmarking."""

        # Start performance optimization
        await self.performance_optimizer.start_optimization()

        try:
            # Run a quick test to generate performance data

            result = await self.extended_framework.run_extended_session(
                model_name="llama_3_3_8b_instruct",
                scenario_name="fantasy_baseline",
                user_profile="typical_user",
            )

            if result:
                pass

            # Get performance report
            perf_report = await self.performance_optimizer.get_performance_report()

            if "current_metrics" in perf_report:
                pass
            else:
                perf_report.get("cache_stats", {})
                perf_report.get("database_stats", {})

            if perf_report.get("recommendations"):
                for _rec in perf_report["recommendations"]:
                    pass
            else:
                pass

        finally:
            await self.performance_optimizer.stop_optimization()


async def main():
    """Main entry point for enhanced evaluation."""
    parser = argparse.ArgumentParser(
        description="Enhanced TTA Extended Session Quality Evaluation"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "extended_sessions",
            "multi_model_comparison",
            "diversified_scenarios",
            "real_user_testing",
            "performance_benchmark",
            "comprehensive",
        ],
        help="Evaluation mode to run",
    )
    parser.add_argument("--models", help="Comma-separated list of models to test")
    parser.add_argument("--turns", type=int, help="Maximum turns for extended sessions")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    runner = EnhancedEvaluationRunner()

    try:
        if args.mode == "extended_sessions":
            await runner.run_extended_sessions(args)
        elif args.mode == "multi_model_comparison":
            await runner.run_multi_model_comparison(args)
        elif args.mode == "diversified_scenarios":
            await runner.run_diversified_scenarios(args)
        elif args.mode == "real_user_testing":
            await runner.run_real_user_testing_demo(args)
        elif args.mode == "performance_benchmark":
            await runner.run_performance_benchmark(args)
        elif args.mode == "comprehensive":
            # Run all modes
            await runner.run_extended_sessions(args)
            await runner.run_multi_model_comparison(args)
            await runner.run_diversified_scenarios(args)
            await runner.run_real_user_testing_demo(args)
            await runner.run_performance_benchmark(args)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
