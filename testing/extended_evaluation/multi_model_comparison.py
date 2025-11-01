"""
Multi-Model Comparison Framework for TTA Quality Evaluation

Provides comprehensive comparison capabilities across different AI models
including GPT-4, Claude-3.5-Sonnet, Gemini Pro, and Llama models.
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import yaml
from scipy import stats

from .extended_session_framework import (
    ExtendedSessionResult,
    ExtendedSessionTestFramework,
)

logger = logging.getLogger(__name__)


@dataclass
class ModelComparisonResult:
    """Results from comparing multiple models on identical scenarios."""

    comparison_id: str
    timestamp: datetime
    models_tested: list[str]
    scenario_name: str

    # Individual model results
    model_results: dict[str, ExtendedSessionResult] = field(default_factory=dict)

    # Comparative metrics
    quality_comparison: dict[str, dict[str, float]] = field(default_factory=dict)
    performance_comparison: dict[str, dict[str, float]] = field(default_factory=dict)
    cost_comparison: dict[str, dict[str, float]] = field(default_factory=dict)

    # Statistical analysis
    statistical_significance: dict[str, dict[str, float]] = field(default_factory=dict)
    confidence_intervals: dict[str, dict[str, tuple[float, float]]] = field(
        default_factory=dict
    )

    # Rankings
    overall_ranking: list[tuple[str, float]] = field(default_factory=list)
    metric_rankings: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    # Insights and recommendations
    key_findings: list[str] = field(default_factory=list)
    model_strengths: dict[str, list[str]] = field(default_factory=dict)
    model_weaknesses: dict[str, list[str]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class CostEffectivenessAnalysis:
    """Analysis of model cost-effectiveness."""

    model_name: str

    # Cost metrics
    total_cost: float
    cost_per_turn: float
    cost_per_quality_point: float

    # Performance metrics
    average_quality: float
    average_response_time: float
    reliability_score: float

    # Cost-effectiveness scores
    cost_effectiveness_score: float  # 0-10 scale
    roi_score: float  # Return on investment

    # Budget recommendations
    recommended_for_budgets: list[str]  # ["free", "low", "medium", "high"]


class MultiModelComparator:
    """
    Framework for comparing multiple AI models on identical TTA scenarios.

    Provides comprehensive analysis including quality metrics, performance
    benchmarks, cost-effectiveness analysis, and statistical significance testing.
    """

    def __init__(self, config_path: str | None = None):
        """Initialize the multi-model comparator."""
        self.config_path = (
            config_path or "testing/configs/multi_model_comparison_config.yaml"
        )
        self.config = self._load_config()
        self.test_framework = ExtendedSessionTestFramework()

        # Comparison tracking
        self.comparison_results: list[ModelComparisonResult] = []
        self.cost_tracking: dict[str, list[float]] = {}

        logger.info("MultiModelComparator initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load multi-model comparison configuration."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded multi-model comparison config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    async def run_model_comparison(
        self,
        models: list[str],
        scenario_name: str,
        user_profile: str,
        runs_per_model: int = 3,
    ) -> ModelComparisonResult:
        """
        Run comprehensive comparison across multiple models.

        Args:
            models: List of model names to compare
            scenario_name: Name of scenario to test
            user_profile: User profile to use for testing
            runs_per_model: Number of runs per model for statistical validity

        Returns:
            ModelComparisonResult with comprehensive analysis
        """
        logger.info(
            f"Starting model comparison: {models} on scenario '{scenario_name}'"
        )

        comparison_id = f"comparison_{int(time.time())}"
        result = ModelComparisonResult(
            comparison_id=comparison_id,
            timestamp=datetime.now(),
            models_tested=models,
            scenario_name=scenario_name,
        )

        # Run tests for each model
        for model_name in models:
            logger.info(f"Testing model: {model_name}")

            model_runs = []
            for run in range(runs_per_model):
                logger.info(f"Running test {run + 1}/{runs_per_model} for {model_name}")

                # Run extended session test
                session_result = await self._run_single_model_test(
                    model_name, scenario_name, user_profile
                )

                if session_result:
                    model_runs.append(session_result)

                    # Track costs
                    if model_name not in self.cost_tracking:
                        self.cost_tracking[model_name] = []

                    estimated_cost = self._calculate_session_cost(
                        session_result, model_name
                    )
                    self.cost_tracking[model_name].append(estimated_cost)

            # Aggregate results for this model
            if model_runs:
                aggregated_result = self._aggregate_model_runs(model_runs)
                result.model_results[model_name] = aggregated_result

        # Perform comparative analysis
        await self._perform_comparative_analysis(result)

        # Generate insights and recommendations
        self._generate_insights_and_recommendations(result)

        # Store result
        self.comparison_results.append(result)

        logger.info(f"Model comparison completed: {comparison_id}")
        return result

    async def _run_single_model_test(
        self, model_name: str, scenario_name: str, user_profile: str
    ) -> ExtendedSessionResult | None:
        """Run a single model test."""
        try:
            # Configure the test framework for this model
            await self.test_framework.configure_model(model_name)

            # Run the extended session test
            result = await self.test_framework.run_extended_session(
                model_name=model_name,
                scenario_name=scenario_name,
                user_profile=user_profile,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to run test for model {model_name}: {e}")
            return None

    def _aggregate_model_runs(
        self, runs: list[ExtendedSessionResult]
    ) -> ExtendedSessionResult:
        """Aggregate multiple runs for a single model."""
        if not runs:
            raise ValueError("No runs to aggregate")

        # Use the first run as template
        aggregated = runs[0]

        # Calculate average metrics
        if len(runs) > 1:
            # Average narrative coherence scores
            all_coherence = [
                score for run in runs for score in run.narrative_coherence_scores
            ]
            aggregated.narrative_coherence_scores = all_coherence

            # Average world consistency scores
            all_world = [
                score for run in runs for score in run.world_state_consistency_scores
            ]
            aggregated.world_state_consistency_scores = all_world

            # Average engagement scores
            all_engagement = [
                score for run in runs for score in run.user_engagement_scores
            ]
            aggregated.user_engagement_scores = all_engagement

            # Average response times
            all_response_times = [time for run in runs for time in run.response_times]
            aggregated.response_times = all_response_times

            # Sum error counts
            aggregated.error_count = sum(run.error_count for run in runs)

            # Calculate final averages
            if aggregated.narrative_coherence_scores:
                aggregated.final_narrative_coherence = statistics.mean(
                    aggregated.narrative_coherence_scores
                )
            if aggregated.world_state_consistency_scores:
                aggregated.final_world_consistency = statistics.mean(
                    aggregated.world_state_consistency_scores
                )
            if aggregated.user_engagement_scores:
                aggregated.final_user_engagement = statistics.mean(
                    aggregated.user_engagement_scores
                )

        return aggregated

    async def _perform_comparative_analysis(self, result: ModelComparisonResult):
        """Perform statistical comparative analysis."""
        models = list(result.model_results.keys())

        # Quality comparison
        for metric in ["narrative_coherence", "world_consistency", "user_engagement"]:
            result.quality_comparison[metric] = {}

            for model in models:
                model_result = result.model_results[model]

                if (
                    metric == "narrative_coherence"
                    and model_result.narrative_coherence_scores
                ):
                    result.quality_comparison[metric][model] = statistics.mean(
                        model_result.narrative_coherence_scores
                    )
                elif (
                    metric == "world_consistency"
                    and model_result.world_state_consistency_scores
                ):
                    result.quality_comparison[metric][model] = statistics.mean(
                        model_result.world_state_consistency_scores
                    )
                elif (
                    metric == "user_engagement" and model_result.user_engagement_scores
                ):
                    result.quality_comparison[metric][model] = statistics.mean(
                        model_result.user_engagement_scores
                    )

        # Performance comparison
        result.performance_comparison["response_time"] = {}
        result.performance_comparison["error_rate"] = {}

        for model in models:
            model_result = result.model_results[model]

            if model_result.response_times:
                result.performance_comparison["response_time"][model] = statistics.mean(
                    model_result.response_times
                )

            # Calculate error rate
            total_turns = model_result.total_turns or 1
            error_rate = (model_result.error_count / total_turns) * 100
            result.performance_comparison["error_rate"][model] = error_rate

        # Cost comparison
        result.cost_comparison["total_cost"] = {}
        result.cost_comparison["cost_per_turn"] = {}

        for model in models:
            if model in self.cost_tracking and self.cost_tracking[model]:
                avg_cost = statistics.mean(self.cost_tracking[model])
                result.cost_comparison["total_cost"][model] = avg_cost

                model_result = result.model_results[model]
                if model_result.total_turns > 0:
                    result.cost_comparison["cost_per_turn"][model] = (
                        avg_cost / model_result.total_turns
                    )

        # Statistical significance testing
        await self._perform_statistical_tests(result)

        # Generate rankings
        self._generate_rankings(result)

    async def _perform_statistical_tests(self, result: ModelComparisonResult):
        """Perform statistical significance tests."""
        models = list(result.model_results.keys())

        if len(models) < 2:
            return

        # T-tests for pairwise comparisons
        for metric in ["narrative_coherence", "world_consistency", "user_engagement"]:
            result.statistical_significance[metric] = {}

            for i, model1 in enumerate(models):
                for model2 in models[i + 1 :]:
                    # Get scores for both models
                    scores1 = self._get_metric_scores(
                        result.model_results[model1], metric
                    )
                    scores2 = self._get_metric_scores(
                        result.model_results[model2], metric
                    )

                    if scores1 and scores2:
                        # Perform t-test
                        t_stat, p_value = stats.ttest_ind(scores1, scores2)

                        comparison_key = f"{model1}_vs_{model2}"
                        result.statistical_significance[metric][comparison_key] = {
                            "t_statistic": t_stat,
                            "p_value": p_value,
                            "significant": p_value < 0.05,
                        }

    def _get_metric_scores(
        self, model_result: ExtendedSessionResult, metric: str
    ) -> list[float]:
        """Get scores for a specific metric from model result."""
        if metric == "narrative_coherence":
            return model_result.narrative_coherence_scores
        if metric == "world_consistency":
            return model_result.world_state_consistency_scores
        if metric == "user_engagement":
            return model_result.user_engagement_scores
        return []

    def _generate_rankings(self, result: ModelComparisonResult):
        """Generate model rankings based on weighted scoring."""
        models = list(result.model_results.keys())
        weights = (
            self.config.get("comparison_analysis", {})
            .get("ranking_methodology", {})
            .get("weights", {})
        )

        # Default weights if not configured
        default_weights = {
            "narrative_coherence": 0.25,
            "world_consistency": 0.20,
            "user_engagement": 0.20,
            "therapeutic_integration": 0.15,
            "cost_effectiveness": 0.10,
            "response_time": 0.10,
        }
        weights = {**default_weights, **weights}

        # Calculate weighted scores for each model
        model_scores = {}

        for model in models:
            score = 0.0

            # Quality metrics
            for metric in [
                "narrative_coherence",
                "world_consistency",
                "user_engagement",
            ]:
                if (
                    metric in result.quality_comparison
                    and model in result.quality_comparison[metric]
                ):
                    normalized_score = (
                        result.quality_comparison[metric][model] / 10.0
                    )  # Normalize to 0-1
                    score += normalized_score * weights.get(metric, 0.0)

            # Performance metrics (inverse for response time - lower is better)
            if (
                "response_time" in result.performance_comparison
                and model in result.performance_comparison["response_time"]
            ):
                # Normalize response time (assume 10 seconds is worst case)
                response_time = result.performance_comparison["response_time"][model]
                normalized_response_time = max(0, 1 - (response_time / 10.0))
                score += normalized_response_time * weights.get("response_time", 0.0)

            # Cost effectiveness
            if model in self.cost_tracking:
                # Simple cost effectiveness: free models get full score, others get partial
                if not self.cost_tracking[model] or all(
                    cost == 0 for cost in self.cost_tracking[model]
                ):
                    cost_effectiveness = 1.0
                else:
                    avg_cost = statistics.mean(self.cost_tracking[model])
                    # Normalize cost (assume $5 per session is expensive)
                    cost_effectiveness = max(0, 1 - (avg_cost / 5.0))

                score += cost_effectiveness * weights.get("cost_effectiveness", 0.0)

            model_scores[model] = score

        # Sort by score (descending)
        result.overall_ranking = sorted(
            model_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Generate metric-specific rankings
        for metric in ["narrative_coherence", "world_consistency", "user_engagement"]:
            if metric in result.quality_comparison:
                metric_scores = result.quality_comparison[metric]
                result.metric_rankings[metric] = sorted(
                    metric_scores.items(), key=lambda x: x[1], reverse=True
                )

    def _calculate_session_cost(
        self, session_result: ExtendedSessionResult, model_name: str
    ) -> float:
        """Calculate estimated cost for a session."""
        model_config = self.config.get("models", {}).get(model_name, {})

        input_cost_per_1k = model_config.get("cost_per_1k_input_tokens", 0.0)
        output_cost_per_1k = model_config.get("cost_per_1k_output_tokens", 0.0)

        # Estimate token usage (rough approximation)
        estimated_input_tokens = (
            session_result.total_turns * 500
        )  # ~500 tokens per turn input
        estimated_output_tokens = (
            session_result.total_turns * 300
        )  # ~300 tokens per turn output

        total_cost = (estimated_input_tokens / 1000) * input_cost_per_1k + (
            estimated_output_tokens / 1000
        ) * output_cost_per_1k

        return total_cost

    def _generate_insights_and_recommendations(self, result: ModelComparisonResult):
        """Generate insights and recommendations from comparison results."""
        models = list(result.model_results.keys())

        # Key findings
        if result.overall_ranking:
            best_model = result.overall_ranking[0][0]
            best_score = result.overall_ranking[0][1]
            result.key_findings.append(
                f"Best overall performer: {best_model} (score: {best_score:.3f})"
            )

        # Cost effectiveness insights
        free_models = []
        paid_models = []

        for model in models:
            if model in self.cost_tracking:
                avg_cost = (
                    statistics.mean(self.cost_tracking[model])
                    if self.cost_tracking[model]
                    else 0.0
                )
                if avg_cost == 0.0:
                    free_models.append(model)
                else:
                    paid_models.append((model, avg_cost))

        if free_models:
            result.key_findings.append(
                f"Free models available: {', '.join(free_models)}"
            )

        if paid_models:
            cheapest_paid = min(paid_models, key=lambda x: x[1])
            result.key_findings.append(
                f"Most cost-effective paid model: {cheapest_paid[0]} (${cheapest_paid[1]:.3f}/session)"
            )

        # Quality insights
        for metric in ["narrative_coherence", "world_consistency", "user_engagement"]:
            if metric in result.metric_rankings and result.metric_rankings[metric]:
                best_for_metric = result.metric_rankings[metric][0]
                result.key_findings.append(
                    f"Best for {metric}: {best_for_metric[0]} ({best_for_metric[1]:.2f}/10)"
                )

        # Generate recommendations
        result.recommendations.append(
            "Consider model selection based on specific use case requirements"
        )
        result.recommendations.append(
            "Balance quality requirements with budget constraints"
        )
        result.recommendations.append(
            "Monitor performance over time as models are updated"
        )

        if free_models and paid_models:
            result.recommendations.append(
                "Start with free models for development, upgrade to paid for production"
            )

    async def generate_comparison_report(
        self, comparison_result: ModelComparisonResult
    ) -> dict[str, Any]:
        """Generate comprehensive comparison report."""
        report = {
            "comparison_id": comparison_result.comparison_id,
            "timestamp": comparison_result.timestamp.isoformat(),
            "models_tested": comparison_result.models_tested,
            "scenario": comparison_result.scenario_name,
            "executive_summary": {
                "best_overall": comparison_result.overall_ranking[0]
                if comparison_result.overall_ranking
                else None,
                "key_findings": comparison_result.key_findings,
                "recommendations": comparison_result.recommendations,
            },
            "detailed_results": {
                "quality_comparison": comparison_result.quality_comparison,
                "performance_comparison": comparison_result.performance_comparison,
                "cost_comparison": comparison_result.cost_comparison,
                "statistical_significance": comparison_result.statistical_significance,
            },
            "rankings": {
                "overall": comparison_result.overall_ranking,
                "by_metric": comparison_result.metric_rankings,
            },
            "model_analysis": {
                "strengths": comparison_result.model_strengths,
                "weaknesses": comparison_result.model_weaknesses,
            },
        }

        return report
