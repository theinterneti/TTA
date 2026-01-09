"""

# Logseq: [[TTA.dev/Testing/Extended_evaluation/Analysis_reporting]]
Analysis and Reporting System for Extended Session Quality Evaluation

Provides comprehensive analysis, pattern recognition, and reporting
capabilities for TTA storytelling system evaluation results.
"""

import json
import logging
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    plt = None
    pd = None
    np = None

logger = logging.getLogger(__name__)


@dataclass
class QualityTrend:
    """Analysis of quality trends over time."""

    metric_name: str
    values: list[float]
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0-1, how strong the trend is
    average_value: float
    min_value: float
    max_value: float
    variance: float

    # Trend analysis
    improvement_points: list[int] = field(default_factory=list)
    degradation_points: list[int] = field(default_factory=list)
    stability_periods: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class ModelPerformanceAnalysis:
    """Comprehensive analysis of a model's performance."""

    model_name: str
    total_sessions: int
    total_turns: int

    # Quality metrics
    avg_narrative_coherence: float = 0.0
    avg_world_consistency: float = 0.0
    avg_user_engagement: float = 0.0
    overall_quality_score: float = 0.0

    # Performance metrics
    avg_response_time: float = 0.0
    avg_memory_usage: float = 0.0
    error_rate: float = 0.0

    # Trend analyses
    coherence_trend: QualityTrend = None
    consistency_trend: QualityTrend = None
    engagement_trend: QualityTrend = None

    # Strengths and weaknesses
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ProfilePerformanceAnalysis:
    """Analysis of performance across different user profiles."""

    profile_name: str
    sessions_tested: int

    # Performance by model
    model_performances: dict[str, dict[str, float]] = field(default_factory=dict)

    # Best performing aspects
    best_narrative_model: str = ""
    best_consistency_model: str = ""
    best_engagement_model: str = ""

    # Profile-specific insights
    profile_strengths: list[str] = field(default_factory=list)
    profile_challenges: list[str] = field(default_factory=list)


@dataclass
class ComprehensiveAnalysisReport:
    """Complete analysis report for extended session evaluation."""

    report_id: str
    generation_timestamp: datetime

    # Summary statistics
    total_sessions: int = 0
    total_turns: int = 0
    total_test_duration_hours: float = 0.0

    # Model analyses
    model_analyses: dict[str, ModelPerformanceAnalysis] = field(default_factory=dict)
    model_rankings: list[dict[str, Any]] = field(default_factory=list)

    # Profile analyses
    profile_analyses: dict[str, ProfilePerformanceAnalysis] = field(
        default_factory=dict
    )

    # Cross-cutting insights
    key_findings: list[str] = field(default_factory=list)
    system_limitations: list[str] = field(default_factory=list)
    improvement_recommendations: list[str] = field(default_factory=list)

    # Quality baselines established
    narrative_coherence_baseline: float = 0.0
    world_consistency_baseline: float = 0.0
    user_engagement_baseline: float = 0.0


class QualityAnalysisReporter:
    """
    Comprehensive analysis and reporting system for extended session evaluation.

    Analyzes collected data to identify patterns, trends, and insights about
    TTA storytelling system performance and quality over extended sessions.
    """

    def __init__(self, data_dir: str = "testing/results/extended_evaluation"):
        self.data_dir = Path(data_dir)
        self.output_dir = self.data_dir / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Analysis data
        self.session_data: dict[str, Any] = {}
        self.model_data: dict[str, list[Any]] = {}
        self.profile_data: dict[str, list[Any]] = {}

        logger.info(
            f"QualityAnalysisReporter initialized with data dir: {self.data_dir}"
        )

    async def load_evaluation_data(self) -> None:
        """Load all evaluation data from the data directory."""
        logger.info("Loading evaluation data for analysis")

        # Load session data
        for session_dir in self.data_dir.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith("session_"):
                session_id = session_dir.name
                await self._load_session_data(session_id, session_dir)

        # Organize data by model and profile
        self._organize_data_by_model_and_profile()

        logger.info(f"Loaded data for {len(self.session_data)} sessions")

    async def _load_session_data(self, session_id: str, session_dir: Path) -> None:
        """Load data for a single session."""
        try:
            # Load session summary
            summary_file = session_dir / "session_summary.json"
            if summary_file.exists():
                with open(summary_file) as f:
                    session_data = json.load(f)
                    self.session_data[session_id] = session_data

            # Load detailed turn data if needed
            turns_file = session_dir / "detailed_turns.jsonl"
            if turns_file.exists():
                turns_data = []
                with open(turns_file) as f:
                    for line in f:
                        turns_data.append(json.loads(line))
                self.session_data[session_id]["detailed_turns"] = turns_data

        except Exception as e:
            logger.error(f"Failed to load session data for {session_id}: {e}")

    def _organize_data_by_model_and_profile(self) -> None:
        """Organize session data by model and profile for analysis."""
        for session_data in self.session_data.values():
            model_name = session_data.get("model_name", "unknown")
            profile_name = session_data.get("profile_name", "unknown")

            # Organize by model
            if model_name not in self.model_data:
                self.model_data[model_name] = []
            self.model_data[model_name].append(session_data)

            # Organize by profile
            if profile_name not in self.profile_data:
                self.profile_data[profile_name] = []
            self.profile_data[profile_name].append(session_data)

    async def generate_comprehensive_report(self) -> ComprehensiveAnalysisReport:
        """Generate comprehensive analysis report."""
        logger.info("Generating comprehensive analysis report")

        report = ComprehensiveAnalysisReport(
            report_id=f"extended_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generation_timestamp=datetime.now(),
        )

        # Calculate summary statistics
        await self._calculate_summary_statistics(report)

        # Analyze model performance
        await self._analyze_model_performance(report)

        # Analyze profile performance
        await self._analyze_profile_performance(report)

        # Generate cross-cutting insights
        await self._generate_insights(report)

        # Establish quality baselines
        await self._establish_quality_baselines(report)

        # Save report
        await self._save_report(report)

        logger.info(f"Generated comprehensive report: {report.report_id}")
        return report

    async def _calculate_summary_statistics(
        self, report: ComprehensiveAnalysisReport
    ) -> None:
        """Calculate overall summary statistics."""
        report.total_sessions = len(self.session_data)

        total_turns = 0
        total_duration = 0.0

        for session_data in self.session_data.values():
            total_turns += session_data.get("completed_turns", 0)
            total_duration += session_data.get("session_duration_minutes", 0.0)

        report.total_turns = total_turns
        report.total_test_duration_hours = total_duration / 60.0

    async def _analyze_model_performance(
        self, report: ComprehensiveAnalysisReport
    ) -> None:
        """Analyze performance for each model."""
        for model_name, sessions in self.model_data.items():
            analysis = await self._analyze_single_model(model_name, sessions)
            report.model_analyses[model_name] = analysis

        # Create model rankings
        report.model_rankings = self._create_model_rankings(report.model_analyses)

    async def _analyze_single_model(
        self, model_name: str, sessions: list[dict[str, Any]]
    ) -> ModelPerformanceAnalysis:
        """Analyze performance for a single model."""
        analysis = ModelPerformanceAnalysis(
            model_name=model_name,
            total_sessions=len(sessions),
            total_turns=sum(s.get("completed_turns", 0) for s in sessions),
        )

        # Collect quality metrics
        coherence_scores = []
        consistency_scores = []
        engagement_scores = []
        response_times = []
        memory_usages = []
        error_counts = []

        for session in sessions:
            # Quality metrics
            if session.get("avg_narrative_coherence"):
                coherence_scores.append(session["avg_narrative_coherence"])
            if session.get("avg_world_consistency"):
                consistency_scores.append(session["avg_world_consistency"])
            if session.get("avg_user_engagement"):
                engagement_scores.append(session["avg_user_engagement"])

            # Performance metrics
            if session.get("avg_response_time"):
                response_times.append(session["avg_response_time"])
            if session.get("peak_memory_usage_mb"):
                memory_usages.append(session["peak_memory_usage_mb"])

            error_counts.append(session.get("total_errors", 0))

        # Calculate averages
        if coherence_scores:
            analysis.avg_narrative_coherence = statistics.mean(coherence_scores)
        if consistency_scores:
            analysis.avg_world_consistency = statistics.mean(consistency_scores)
        if engagement_scores:
            analysis.avg_user_engagement = statistics.mean(engagement_scores)
        if response_times:
            analysis.avg_response_time = statistics.mean(response_times)
        if memory_usages:
            analysis.avg_memory_usage = statistics.mean(memory_usages)

        # Calculate error rate
        total_turns = sum(s.get("completed_turns", 0) for s in sessions)
        total_errors = sum(error_counts)
        analysis.error_rate = total_errors / total_turns if total_turns > 0 else 0.0

        # Calculate overall quality score
        quality_scores = [
            s
            for s in [
                analysis.avg_narrative_coherence,
                analysis.avg_world_consistency,
                analysis.avg_user_engagement,
            ]
            if s > 0
        ]
        if quality_scores:
            analysis.overall_quality_score = statistics.mean(quality_scores)

        # Analyze trends
        analysis.coherence_trend = self._analyze_quality_trend(
            "narrative_coherence", coherence_scores
        )
        analysis.consistency_trend = self._analyze_quality_trend(
            "world_consistency", consistency_scores
        )
        analysis.engagement_trend = self._analyze_quality_trend(
            "user_engagement", engagement_scores
        )

        # Generate insights
        analysis.strengths = self._identify_model_strengths(analysis)
        analysis.weaknesses = self._identify_model_weaknesses(analysis)
        analysis.recommendations = self._generate_model_recommendations(analysis)

        return analysis

    def _analyze_quality_trend(
        self, metric_name: str, values: list[float]
    ) -> QualityTrend:
        """Analyze trend for a quality metric."""
        if not values or len(values) < 2:
            return QualityTrend(
                metric_name=metric_name,
                values=values,
                trend_direction="stable",
                trend_strength=0.0,
                average_value=values[0] if values else 0.0,
                min_value=values[0] if values else 0.0,
                max_value=values[0] if values else 0.0,
                variance=0.0,
            )

        # Calculate basic statistics
        avg_value = statistics.mean(values)
        min_value = min(values)
        max_value = max(values)
        variance = statistics.variance(values) if len(values) > 1 else 0.0

        # Analyze trend direction
        trend_direction = "stable"
        trend_strength = 0.0

        if len(values) >= 3:
            # Simple linear trend analysis
            x = list(range(len(values)))
            correlation = np.corrcoef(x, values)[0, 1] if len(values) > 1 else 0.0

            if correlation > 0.3:
                trend_direction = "improving"
                trend_strength = abs(correlation)
            elif correlation < -0.3:
                trend_direction = "declining"
                trend_strength = abs(correlation)

        return QualityTrend(
            metric_name=metric_name,
            values=values,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            average_value=avg_value,
            min_value=min_value,
            max_value=max_value,
            variance=variance,
        )

    def _create_model_rankings(
        self, model_analyses: dict[str, ModelPerformanceAnalysis]
    ) -> list[dict[str, Any]]:
        """Create rankings of models by performance."""
        rankings = []

        for model_name, analysis in model_analyses.items():
            rankings.append(
                {
                    "model": model_name,
                    "overall_score": analysis.overall_quality_score,
                    "narrative_coherence": analysis.avg_narrative_coherence,
                    "world_consistency": analysis.avg_world_consistency,
                    "user_engagement": analysis.avg_user_engagement,
                    "response_time": analysis.avg_response_time,
                    "error_rate": analysis.error_rate,
                }
            )

        # Sort by overall score
        rankings.sort(key=lambda x: x["overall_score"], reverse=True)

        # Add rank numbers
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1

        return rankings

    async def _analyze_profile_performance(
        self, report: ComprehensiveAnalysisReport
    ) -> None:
        """Analyze performance across different user profiles."""
        for profile_name, sessions in self.profile_data.items():
            analysis = ProfilePerformanceAnalysis(
                profile_name=profile_name, sessions_tested=len(sessions)
            )

            # Analyze performance by model for this profile
            model_sessions = {}
            for session in sessions:
                model_name = session.get("model_name", "unknown")
                if model_name not in model_sessions:
                    model_sessions[model_name] = []
                model_sessions[model_name].append(session)

            # Calculate performance metrics for each model
            for model_name, model_sessions_list in model_sessions.items():
                coherence_scores = [
                    s.get("avg_narrative_coherence", 0)
                    for s in model_sessions_list
                    if s.get("avg_narrative_coherence")
                ]
                consistency_scores = [
                    s.get("avg_world_consistency", 0)
                    for s in model_sessions_list
                    if s.get("avg_world_consistency")
                ]
                engagement_scores = [
                    s.get("avg_user_engagement", 0)
                    for s in model_sessions_list
                    if s.get("avg_user_engagement")
                ]

                analysis.model_performances[model_name] = {
                    "narrative_coherence": statistics.mean(coherence_scores)
                    if coherence_scores
                    else 0.0,
                    "world_consistency": statistics.mean(consistency_scores)
                    if consistency_scores
                    else 0.0,
                    "user_engagement": statistics.mean(engagement_scores)
                    if engagement_scores
                    else 0.0,
                }

            # Identify best performing models for each metric
            if analysis.model_performances:
                best_narrative = max(
                    analysis.model_performances.items(),
                    key=lambda x: x[1]["narrative_coherence"],
                )
                analysis.best_narrative_model = best_narrative[0]

                best_consistency = max(
                    analysis.model_performances.items(),
                    key=lambda x: x[1]["world_consistency"],
                )
                analysis.best_consistency_model = best_consistency[0]

                best_engagement = max(
                    analysis.model_performances.items(),
                    key=lambda x: x[1]["user_engagement"],
                )
                analysis.best_engagement_model = best_engagement[0]

            report.profile_analyses[profile_name] = analysis

    async def _generate_insights(self, report: ComprehensiveAnalysisReport) -> None:
        """Generate cross-cutting insights from the analysis."""
        insights = []
        limitations = []
        recommendations = []

        # Analyze overall performance
        if report.model_analyses:
            avg_coherence = statistics.mean(
                [
                    a.avg_narrative_coherence
                    for a in report.model_analyses.values()
                    if a.avg_narrative_coherence > 0
                ]
            )
            avg_consistency = statistics.mean(
                [
                    a.avg_world_consistency
                    for a in report.model_analyses.values()
                    if a.avg_world_consistency > 0
                ]
            )
            avg_engagement = statistics.mean(
                [
                    a.avg_user_engagement
                    for a in report.model_analyses.values()
                    if a.avg_user_engagement > 0
                ]
            )

            if avg_coherence > 8.0:
                insights.append(
                    "Excellent narrative coherence maintained across extended sessions"
                )
            elif avg_coherence < 6.0:
                limitations.append(
                    "Narrative coherence degrades over extended sessions"
                )
                recommendations.append(
                    "Implement stronger narrative consistency tracking"
                )

            if avg_consistency > 8.5:
                insights.append("Living worlds system maintains excellent consistency")
            elif avg_consistency < 7.0:
                limitations.append(
                    "World state consistency issues in extended sessions"
                )
                recommendations.append(
                    "Enhance world state validation and correction mechanisms"
                )

            if avg_engagement > 7.5:
                insights.append(
                    "Strong user engagement maintained throughout extended sessions"
                )
            elif avg_engagement < 6.5:
                limitations.append("User engagement drops in longer sessions")
                recommendations.append(
                    "Implement dynamic pacing and engagement recovery mechanisms"
                )

        # Analyze model performance spread
        if len(report.model_analyses) > 1:
            quality_scores = [
                a.overall_quality_score
                for a in report.model_analyses.values()
                if a.overall_quality_score > 0
            ]
            if quality_scores:
                score_range = max(quality_scores) - min(quality_scores)
                if score_range > 2.0:
                    insights.append(
                        "Significant performance differences between models"
                    )
                    recommendations.append(
                        "Focus development on top-performing model characteristics"
                    )

        report.key_findings = insights
        report.system_limitations = limitations
        report.improvement_recommendations = recommendations

    async def _establish_quality_baselines(
        self, report: ComprehensiveAnalysisReport
    ) -> None:
        """Establish quality baselines from the evaluation."""
        if report.model_analyses:
            coherence_scores = [
                a.avg_narrative_coherence
                for a in report.model_analyses.values()
                if a.avg_narrative_coherence > 0
            ]
            consistency_scores = [
                a.avg_world_consistency
                for a in report.model_analyses.values()
                if a.avg_world_consistency > 0
            ]
            engagement_scores = [
                a.avg_user_engagement
                for a in report.model_analyses.values()
                if a.avg_user_engagement > 0
            ]

            if coherence_scores:
                report.narrative_coherence_baseline = statistics.mean(coherence_scores)
            if consistency_scores:
                report.world_consistency_baseline = statistics.mean(consistency_scores)
            if engagement_scores:
                report.user_engagement_baseline = statistics.mean(engagement_scores)

    def _identify_model_strengths(
        self, analysis: ModelPerformanceAnalysis
    ) -> list[str]:
        """Identify strengths for a model."""
        strengths = []

        if analysis.avg_narrative_coherence > 8.0:
            strengths.append("Excellent narrative coherence")
        if analysis.avg_world_consistency > 8.5:
            strengths.append("Outstanding world state consistency")
        if analysis.avg_user_engagement > 7.5:
            strengths.append("Strong user engagement")
        if analysis.avg_response_time < 2.0:
            strengths.append("Fast response times")
        if analysis.error_rate < 0.05:
            strengths.append("Low error rate")

        return strengths

    def _identify_model_weaknesses(
        self, analysis: ModelPerformanceAnalysis
    ) -> list[str]:
        """Identify weaknesses for a model."""
        weaknesses = []

        if analysis.avg_narrative_coherence < 6.0:
            weaknesses.append("Poor narrative coherence")
        if analysis.avg_world_consistency < 7.0:
            weaknesses.append("World consistency issues")
        if analysis.avg_user_engagement < 6.5:
            weaknesses.append("Low user engagement")
        if analysis.avg_response_time > 5.0:
            weaknesses.append("Slow response times")
        if analysis.error_rate > 0.1:
            weaknesses.append("High error rate")

        return weaknesses

    def _generate_model_recommendations(
        self, analysis: ModelPerformanceAnalysis
    ) -> list[str]:
        """Generate recommendations for a model."""
        recommendations = []

        if analysis.avg_narrative_coherence < 7.0:
            recommendations.append("Improve narrative consistency tracking")
        if analysis.avg_world_consistency < 7.5:
            recommendations.append("Enhance world state management")
        if analysis.avg_user_engagement < 7.0:
            recommendations.append("Implement engagement recovery mechanisms")
        if analysis.avg_response_time > 3.0:
            recommendations.append("Optimize response generation speed")

        return recommendations

    async def _save_report(self, report: ComprehensiveAnalysisReport) -> None:
        """Save the comprehensive report to file."""
        report_file = self.output_dir / f"{report.report_id}.json"

        # Convert to dictionary for JSON serialization
        report_dict = asdict(report)
        report_dict["generation_timestamp"] = report.generation_timestamp.isoformat()

        with open(report_file, "w") as f:
            json.dump(report_dict, f, indent=2)

        logger.info(f"Saved comprehensive report to {report_file}")

    async def generate_visualizations(
        self, report: ComprehensiveAnalysisReport
    ) -> list[str]:
        """Generate visualization charts for the report."""
        viz_files = []

        if not VISUALIZATION_AVAILABLE:
            logger.warning(
                "Visualization libraries not available. Install matplotlib, pandas, numpy for charts."
            )
            return viz_files

        try:
            # Model performance comparison
            viz_files.append(await self._create_model_comparison_chart(report))

            # Quality trends over time
            viz_files.append(await self._create_quality_trends_chart(report))

            # Profile performance analysis
            viz_files.append(await self._create_profile_analysis_chart(report))

        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")

        return viz_files

    async def _create_model_comparison_chart(
        self, report: ComprehensiveAnalysisReport
    ) -> str:
        """Create model performance comparison chart."""
        if not report.model_rankings:
            return ""

        models = [r["model"] for r in report.model_rankings]
        coherence_scores = [r["narrative_coherence"] for r in report.model_rankings]
        consistency_scores = [r["world_consistency"] for r in report.model_rankings]
        engagement_scores = [r["user_engagement"] for r in report.model_rankings]

        fig, ax = plt.subplots(figsize=(12, 8))

        x = np.arange(len(models))
        width = 0.25

        ax.bar(x - width, coherence_scores, width, label="Narrative Coherence")
        ax.bar(x, consistency_scores, width, label="World Consistency")
        ax.bar(x + width, engagement_scores, width, label="User Engagement")

        ax.set_xlabel("Models")
        ax.set_ylabel("Quality Scores")
        ax.set_title("Model Performance Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)

        chart_file = self.output_dir / f"{report.report_id}_model_comparison.png"
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    async def _create_quality_trends_chart(
        self, report: ComprehensiveAnalysisReport
    ) -> str:
        """Create quality trends over time chart."""
        # This would create trend charts for each model
        # Simplified implementation for now
        chart_file = self.output_dir / f"{report.report_id}_quality_trends.png"

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(
            0.5,
            0.5,
            "Quality Trends Chart\n(Implementation pending)",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=16,
        )
        ax.set_title("Quality Trends Over Extended Sessions")

        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    async def _create_profile_analysis_chart(
        self, report: ComprehensiveAnalysisReport
    ) -> str:
        """Create profile performance analysis chart."""
        # This would create profile-specific performance charts
        # Simplified implementation for now
        chart_file = self.output_dir / f"{report.report_id}_profile_analysis.png"

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(
            0.5,
            0.5,
            "Profile Analysis Chart\n(Implementation pending)",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=16,
        )
        ax.set_title("Performance Across User Profiles")

        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)
