#!/usr/bin/env python3
"""
Comprehensive Free Model Validation Script for TTA Enhanced Extended Session Quality Evaluation Framework

This script validates all 7 free models available through OpenRouter API:
1. Meta Llama 3.3 8B Instruct (baseline)
2. Meta Llama 3.1 8B Instruct (comparison)
3. Meta Llama 3.2 11B Vision Instruct (enhanced reasoning)
4. Qwen 2.5 72B Instruct (largest free model)
5. Qwen 3 4B (speed testing)
6. Google Gemma 2 9B IT (Google architecture)
7. Google Gemma 3n 2B (ultra-fast inference)

Usage:
    python testing/run_comprehensive_free_model_validation.py [--quick] [--extended] [--full]

    --quick: Run basic comparison tests only (~15 minutes)
    --extended: Run extended session tests (~45 minutes)
    --full: Run complete validation suite (~2 hours)
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from testing.run_enhanced_evaluation import EnhancedEvaluationRunner


class ComprehensiveFreeModelValidator:
    """Comprehensive validation of all free models available through OpenRouter."""

    def __init__(self):
        self.runner = None
        self.free_models = [
            "llama_3_3_8b_instruct",  # Best overall free model
            "qwen_2_5_72b_instruct",  # Largest free model
            "llama_3_2_11b_vision_instruct",  # Enhanced reasoning
            "gemma_2_9b_it",  # Google architecture
            "llama_3_1_8b_instruct",  # Baseline comparison
            "qwen_3_4b",  # Speed testing
            "gemma_3n_2b",  # Ultra-fast inference
        ]

        self.test_scenarios = {
            "basic": ["fantasy_baseline", "contemporary_baseline"],
            "extended": [
                "fantasy_extended_30",
                "contemporary_extended_40",
                "epic_fantasy_50",
            ],
            "diversified": [
                "space_colony_crisis",
                "ai_consciousness_dilemma",
                "small_town_secrets",
                "corporate_espionage",
                "civil_rights_movement",
                "wwii_resistance",
                "haunted_family_home",
                "isolation_experiment",
                "second_chance_love",
                "workplace_romance_ethics",
                "moral_dilemma_cascade",
                "narrative_dead_end_recovery",
            ],
        }

        self.results = {}

    async def initialize(self):
        """Initialize the enhanced evaluation runner."""
        self.runner = EnhancedEvaluationRunner()

    async def run_quick_validation(self):
        """Run quick validation tests (~15 minutes)."""

        start_time = time.time()

        # Test top 3 models on basic scenarios
        top_models = self.free_models[:3]
        models_str = ",".join(top_models)

        # Create mock args object
        class MockArgs:
            def __init__(self):
                self.models = models_str

        args = MockArgs()

        await self.runner.run_multi_model_comparison(args)

        duration = time.time() - start_time

        return {
            "test_type": "quick",
            "models_tested": len(top_models),
            "scenarios_tested": 3,
            "duration_seconds": duration,
            "api_cost": 0.0,
        }

    async def run_extended_validation(self):
        """Run extended session validation tests (~45 minutes)."""

        start_time = time.time()

        # Test all models on extended sessions
        models_str = ",".join(self.free_models)

        class MockArgs:
            def __init__(self):
                self.models = models_str
                self.turns = 50

        args = MockArgs()

        await self.runner.run_extended_sessions(args)

        duration = time.time() - start_time

        return {
            "test_type": "extended",
            "models_tested": len(self.free_models),
            "scenarios_tested": 3,
            "duration_seconds": duration,
            "api_cost": 0.0,
        }

    async def run_full_validation(self):
        """Run complete validation suite (~2 hours)."""

        start_time = time.time()

        # 1. Multi-model comparison
        models_str = ",".join(self.free_models)

        class MockArgs:
            def __init__(self):
                self.models = models_str

        args = MockArgs()
        await self.runner.run_multi_model_comparison(args)

        # 2. Extended session testing
        args.turns = 50
        await self.runner.run_extended_sessions(args)

        # 3. Diversified scenario testing for top 3 models
        top_models = self.free_models[:3]
        for model in top_models:
            args.models = model
            await self.runner.run_diversified_scenarios(args)

        # 4. Performance benchmarking
        await self.runner.run_performance_benchmark(args)

        duration = time.time() - start_time

        return {
            "test_type": "full",
            "models_tested": len(self.free_models),
            "scenarios_tested": len(self.test_scenarios["basic"])
            + len(self.test_scenarios["extended"])
            + len(self.test_scenarios["diversified"]),
            "duration_seconds": duration,
            "api_cost": 0.0,
        }

    def generate_summary_report(self, results):
        """Generate a comprehensive summary report."""


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Free Model Validation for TTA Framework"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run quick validation tests (~15 minutes)"
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Run extended session tests (~45 minutes)",
    )
    parser.add_argument(
        "--full", action="store_true", help="Run complete validation suite (~2 hours)"
    )

    args = parser.parse_args()

    # Default to quick if no option specified
    if not any([args.quick, args.extended, args.full]):
        args.quick = True

    validator = ComprehensiveFreeModelValidator()
    await validator.initialize()

    try:
        if args.quick:
            results = await validator.run_quick_validation()
        elif args.extended:
            results = await validator.run_extended_validation()
        elif args.full:
            results = await validator.run_full_validation()

        validator.generate_summary_report(results)

    except Exception:
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
