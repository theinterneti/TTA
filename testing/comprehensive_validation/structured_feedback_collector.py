"""
Structured User Feedback Collection System for TTA

This module provides comprehensive collection and analysis of structured
user feedback on narrative quality, therapeutic relevance, and overall
experience. It supports both automated feedback collection and manual
feedback integration for excellence-focused validation.

Key Features:
- Structured feedback collection with standardized metrics
- Multi-dimensional feedback analysis (narrative, therapeutic, experience)
- Automated feedback aggregation and trend analysis
- Excellence-focused feedback validation and reporting
- Integration with validation frameworks for comprehensive assessment
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FeedbackDimension(Enum):
    """Dimensions for structured user feedback collection."""

    NARRATIVE_QUALITY = "narrative_quality"
    THERAPEUTIC_RELEVANCE = "therapeutic_relevance"
    USER_ENGAGEMENT = "user_engagement"
    CHARACTER_CONNECTION = "character_connection"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    SAFETY_COMFORT = "safety_comfort"
    OVERALL_SATISFACTION = "overall_satisfaction"


class FeedbackType(Enum):
    """Types of feedback collection methods."""

    AUTOMATED_METRICS = "automated_metrics"
    USER_SURVEY = "user_survey"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    EXPERT_EVALUATION = "expert_evaluation"


@dataclass
class FeedbackItem:
    """Individual feedback item with structured data."""

    dimension: FeedbackDimension
    score: float  # 0-10 scale
    confidence: float  # 0-1 scale
    feedback_type: FeedbackType
    timestamp: datetime
    session_id: str
    user_id: str | None = None
    comments: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackAnalysis:
    """Analysis results for collected feedback."""

    dimension: FeedbackDimension
    mean_score: float
    median_score: float
    std_deviation: float
    confidence_weighted_score: float
    sample_size: int
    trend_direction: str  # "improving", "declining", "stable"
    excellence_achievement: bool  # Meets excellence targets
    key_insights: list[str] = field(default_factory=list)


@dataclass
class ComprehensiveFeedbackReport:
    """Comprehensive feedback report across all dimensions."""

    report_id: str
    generation_timestamp: datetime
    session_count: int
    total_feedback_items: int

    # Dimension-specific analyses
    dimension_analyses: dict[str, FeedbackAnalysis] = field(default_factory=dict)

    # Overall metrics
    overall_excellence_score: float = 0.0
    meets_excellence_standards: bool = False

    # Trends and insights
    improvement_trends: list[str] = field(default_factory=list)
    concern_areas: list[str] = field(default_factory=list)
    excellence_indicators: list[str] = field(default_factory=list)

    # Recommendations
    feedback_recommendations: list[str] = field(default_factory=list)


class StructuredFeedbackCollector:
    """
    Comprehensive structured feedback collection and analysis system.

    Collects, analyzes, and reports on user feedback across multiple
    dimensions with focus on excellence achievement and continuous improvement.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

        # Excellence targets for feedback dimensions
        self.excellence_targets = {
            FeedbackDimension.NARRATIVE_QUALITY: 8.5,
            FeedbackDimension.THERAPEUTIC_RELEVANCE: 8.0,
            FeedbackDimension.USER_ENGAGEMENT: 8.5,
            FeedbackDimension.CHARACTER_CONNECTION: 8.0,
            FeedbackDimension.EMOTIONAL_RESONANCE: 8.5,
            FeedbackDimension.SAFETY_COMFORT: 9.0,
            FeedbackDimension.OVERALL_SATISFACTION: 8.5,
        }

        # Feedback storage
        self.feedback_items: list[FeedbackItem] = []

        # Analysis cache
        self.analysis_cache: dict[str, FeedbackAnalysis] = {}
        self.last_analysis_time: datetime | None = None

    async def collect_automated_feedback(
        self,
        session_id: str,
        narrative_content: list[str],
        therapeutic_context: dict[str, Any],
        user_interactions: dict[str, Any] = None,
    ) -> list[FeedbackItem]:
        """
        Collect automated feedback based on system metrics and analysis.

        Args:
            session_id: Session identifier
            narrative_content: Narrative content to analyze
            therapeutic_context: Therapeutic context and goals
            user_interactions: User interaction data (optional)

        Returns:
            List of automated feedback items
        """
        feedback_items = []
        timestamp = datetime.utcnow()

        try:
            # Narrative quality assessment
            narrative_score = await self._assess_narrative_quality_automated(
                narrative_content
            )
            feedback_items.append(
                FeedbackItem(
                    dimension=FeedbackDimension.NARRATIVE_QUALITY,
                    score=narrative_score,
                    confidence=0.8,
                    feedback_type=FeedbackType.AUTOMATED_METRICS,
                    timestamp=timestamp,
                    session_id=session_id,
                    metadata={"content_length": len(narrative_content)},
                )
            )

            # Therapeutic relevance assessment
            therapeutic_score = await self._assess_therapeutic_relevance_automated(
                narrative_content, therapeutic_context
            )
            feedback_items.append(
                FeedbackItem(
                    dimension=FeedbackDimension.THERAPEUTIC_RELEVANCE,
                    score=therapeutic_score,
                    confidence=0.85,
                    feedback_type=FeedbackType.AUTOMATED_METRICS,
                    timestamp=timestamp,
                    session_id=session_id,
                    metadata={
                        "therapeutic_goals": therapeutic_context.get(
                            "therapeutic_goals", []
                        )
                    },
                )
            )

            # User engagement assessment (if interaction data available)
            if user_interactions:
                engagement_score = await self._assess_user_engagement_automated(
                    user_interactions
                )
                feedback_items.append(
                    FeedbackItem(
                        dimension=FeedbackDimension.USER_ENGAGEMENT,
                        score=engagement_score,
                        confidence=0.7,
                        feedback_type=FeedbackType.BEHAVIORAL_ANALYSIS,
                        timestamp=timestamp,
                        session_id=session_id,
                        metadata={
                            "interaction_count": len(
                                user_interactions.get("interactions", [])
                            )
                        },
                    )
                )

            # Safety and comfort assessment
            safety_score = await self._assess_safety_comfort_automated(
                narrative_content, therapeutic_context
            )
            feedback_items.append(
                FeedbackItem(
                    dimension=FeedbackDimension.SAFETY_COMFORT,
                    score=safety_score,
                    confidence=0.9,
                    feedback_type=FeedbackType.AUTOMATED_METRICS,
                    timestamp=timestamp,
                    session_id=session_id,
                    metadata={
                        "trigger_topics": therapeutic_context.get("trigger_topics", [])
                    },
                )
            )

            # Store feedback items
            self.feedback_items.extend(feedback_items)

            logger.info(
                f"✅ Collected {len(feedback_items)} automated feedback items for session {session_id}"
            )
            return feedback_items

        except Exception as e:
            logger.error(
                f"❌ Automated feedback collection failed for session {session_id}: {e}"
            )
            return []

    async def collect_user_survey_feedback(
        self, session_id: str, user_id: str, survey_responses: dict[str, Any]
    ) -> list[FeedbackItem]:
        """
        Collect structured user survey feedback.

        Args:
            session_id: Session identifier
            user_id: User identifier
            survey_responses: User survey responses

        Returns:
            List of user survey feedback items
        """
        feedback_items = []
        timestamp = datetime.utcnow()

        try:
            # Map survey responses to feedback dimensions
            dimension_mapping = {
                "narrative_quality": FeedbackDimension.NARRATIVE_QUALITY,
                "therapeutic_relevance": FeedbackDimension.THERAPEUTIC_RELEVANCE,
                "user_engagement": FeedbackDimension.USER_ENGAGEMENT,
                "character_connection": FeedbackDimension.CHARACTER_CONNECTION,
                "emotional_resonance": FeedbackDimension.EMOTIONAL_RESONANCE,
                "safety_comfort": FeedbackDimension.SAFETY_COMFORT,
                "overall_satisfaction": FeedbackDimension.OVERALL_SATISFACTION,
            }

            for survey_key, dimension in dimension_mapping.items():
                if survey_key in survey_responses:
                    response = survey_responses[survey_key]

                    # Extract score and comments
                    score = (
                        response.get("score", 0.0)
                        if isinstance(response, dict)
                        else float(response)
                    )
                    comments = (
                        response.get("comments") if isinstance(response, dict) else None
                    )

                    feedback_items.append(
                        FeedbackItem(
                            dimension=dimension,
                            score=score,
                            confidence=1.0,  # High confidence for direct user feedback
                            feedback_type=FeedbackType.USER_SURVEY,
                            timestamp=timestamp,
                            session_id=session_id,
                            user_id=user_id,
                            comments=comments,
                            metadata={
                                "survey_version": survey_responses.get(
                                    "survey_version", "1.0"
                                )
                            },
                        )
                    )

            # Store feedback items
            self.feedback_items.extend(feedback_items)

            logger.info(
                f"✅ Collected {len(feedback_items)} user survey feedback items for session {session_id}"
            )
            return feedback_items

        except Exception as e:
            logger.error(
                f"❌ User survey feedback collection failed for session {session_id}: {e}"
            )
            return []

    async def analyze_feedback_comprehensive(
        self, time_window_days: int = 30
    ) -> ComprehensiveFeedbackReport:
        """
        Perform comprehensive analysis of collected feedback.

        Args:
            time_window_days: Time window for analysis in days

        Returns:
            Comprehensive feedback analysis report
        """
        logger.info(f"🔍 Analyzing feedback for last {time_window_days} days")

        # Filter feedback items by time window
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        recent_feedback = [
            item for item in self.feedback_items if item.timestamp >= cutoff_date
        ]

        if not recent_feedback:
            logger.warning("⚠️ No recent feedback items found for analysis")
            return ComprehensiveFeedbackReport(
                report_id=f"feedback_report_{int(time.time())}",
                generation_timestamp=datetime.utcnow(),
                session_count=0,
                total_feedback_items=0,
                feedback_recommendations=["Increase feedback collection efforts"],
            )

        # Analyze each dimension
        dimension_analyses = {}
        for dimension in FeedbackDimension:
            dimension_feedback = [
                item for item in recent_feedback if item.dimension == dimension
            ]
            if dimension_feedback:
                analysis = await self._analyze_dimension_feedback(
                    dimension, dimension_feedback
                )
                dimension_analyses[dimension.value] = analysis

        # Calculate overall metrics
        overall_scores = []
        excellence_achievements = []

        for analysis in dimension_analyses.values():
            overall_scores.append(analysis.confidence_weighted_score)
            excellence_achievements.append(analysis.excellence_achievement)

        overall_excellence_score = (
            statistics.mean(overall_scores) if overall_scores else 0.0
        )
        meets_excellence_standards = (
            all(excellence_achievements) if excellence_achievements else False
        )

        # Identify trends and insights
        improvement_trends = self._identify_improvement_trends(dimension_analyses)
        concern_areas = self._identify_concern_areas(dimension_analyses)
        excellence_indicators = self._identify_excellence_indicators(dimension_analyses)

        # Generate recommendations
        recommendations = self._generate_feedback_recommendations(
            dimension_analyses, meets_excellence_standards
        )

        # Create comprehensive report
        report = ComprehensiveFeedbackReport(
            report_id=f"feedback_report_{int(time.time())}",
            generation_timestamp=datetime.utcnow(),
            session_count=len(set(item.session_id for item in recent_feedback)),
            total_feedback_items=len(recent_feedback),
            dimension_analyses=dimension_analyses,
            overall_excellence_score=overall_excellence_score,
            meets_excellence_standards=meets_excellence_standards,
            improvement_trends=improvement_trends,
            concern_areas=concern_areas,
            excellence_indicators=excellence_indicators,
            feedback_recommendations=recommendations,
        )

        logger.info("✅ Comprehensive feedback analysis completed")
        return report

    async def _assess_narrative_quality_automated(
        self, narrative_content: list[str]
    ) -> float:
        """Assess narrative quality using automated metrics."""
        score = 7.5  # Base score

        if not narrative_content:
            return score

        combined_narrative = " ".join(narrative_content)

        # Length and richness assessment
        if len(combined_narrative) > 500:  # Rich content
            score += 0.5

        # Descriptive language assessment
        descriptive_words = ["vivid", "clear", "detailed", "immersive", "engaging"]
        descriptive_count = sum(
            1 for word in descriptive_words if word in combined_narrative.lower()
        )
        score += min(1.0, descriptive_count * 0.2)

        # Coherence indicators
        coherence_words = ["then", "next", "meanwhile", "however", "therefore"]
        coherence_count = sum(
            1 for word in coherence_words if word in combined_narrative.lower()
        )
        score += min(0.5, coherence_count * 0.1)

        return min(10.0, score)

    async def _assess_therapeutic_relevance_automated(
        self, narrative_content: list[str], therapeutic_context: dict[str, Any]
    ) -> float:
        """Assess therapeutic relevance using automated metrics."""
        score = 7.0  # Base therapeutic score

        if not narrative_content:
            return score

        combined_narrative = " ".join(narrative_content).lower()

        # Therapeutic goal alignment
        therapeutic_goals = therapeutic_context.get("therapeutic_goals", [])
        for goal in therapeutic_goals:
            goal_keywords = self._get_therapeutic_keywords(goal)
            if any(keyword in combined_narrative for keyword in goal_keywords):
                score += 0.5

        # Therapeutic technique indicators
        technique_words = ["mindful", "breathe", "reflect", "understand", "support"]
        technique_count = sum(
            1 for word in technique_words if word in combined_narrative
        )
        score += min(1.0, technique_count * 0.2)

        # Safety indicators
        safety_words = ["safe", "secure", "comfortable", "supported"]
        safety_count = sum(1 for word in safety_words if word in combined_narrative)
        score += min(0.5, safety_count * 0.1)

        return min(10.0, score)

    def _get_therapeutic_keywords(self, goal: str) -> list[str]:
        """Get keywords associated with therapeutic goals."""
        keyword_mapping = {
            "anxiety_management": ["calm", "relax", "peaceful", "breathe", "grounding"],
            "depression_support": ["hope", "strength", "support", "care", "value"],
            "confidence_building": ["capable", "strong", "achieve", "succeed", "proud"],
            "mindfulness": ["present", "aware", "mindful", "observe", "focus"],
        }
        return keyword_mapping.get(goal, [goal.replace("_", " ")])

    async def _assess_user_engagement_automated(
        self, user_interactions: dict[str, Any]
    ) -> float:
        """Assess user engagement using behavioral metrics."""
        score = 7.0  # Base engagement score

        interactions = user_interactions.get("interactions", [])

        # Interaction frequency
        if len(interactions) > 5:
            score += 1.0
        elif len(interactions) > 2:
            score += 0.5

        # Response time analysis (quick responses indicate engagement)
        response_times = user_interactions.get("response_times", [])
        if response_times:
            avg_response_time = statistics.mean(response_times)
            if avg_response_time < 30:  # Quick responses
                score += 0.5

        # Session duration (longer sessions indicate engagement)
        session_duration = user_interactions.get("session_duration", 0)
        if session_duration > 600:  # More than 10 minutes
            score += 0.5

        return min(10.0, score)

    async def _assess_safety_comfort_automated(
        self, narrative_content: list[str], therapeutic_context: dict[str, Any]
    ) -> float:
        """Assess safety and comfort using automated metrics."""
        score = 9.0  # High baseline for safety

        if not narrative_content:
            return score

        combined_narrative = " ".join(narrative_content).lower()

        # Check for trigger topic avoidance
        trigger_topics = therapeutic_context.get("trigger_topics", [])
        for trigger in trigger_topics:
            if trigger.lower() in combined_narrative:
                score -= 1.0  # Penalty for trigger mention

        # Positive safety indicators
        safety_words = ["safe", "secure", "comfortable", "supported", "protected"]
        safety_count = sum(1 for word in safety_words if word in combined_narrative)
        score += min(0.5, safety_count * 0.1)

        # Check for crisis language
        crisis_words = ["harm", "hurt", "danger", "unsafe"]
        crisis_count = sum(1 for word in crisis_words if word in combined_narrative)
        if crisis_count > 0:
            score -= crisis_count * 0.5

        return min(10.0, max(0.0, score))

    async def _analyze_dimension_feedback(
        self, dimension: FeedbackDimension, feedback_items: list[FeedbackItem]
    ) -> FeedbackAnalysis:
        """Analyze feedback for a specific dimension."""

        scores = [item.score for item in feedback_items]
        confidences = [item.confidence for item in feedback_items]

        # Calculate basic statistics
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_deviation = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Calculate confidence-weighted score
        weighted_scores = [
            score * confidence
            for score, confidence in zip(scores, confidences, strict=False)
        ]
        total_confidence = sum(confidences)
        confidence_weighted_score = (
            sum(weighted_scores) / total_confidence
            if total_confidence > 0
            else mean_score
        )

        # Determine trend (simplified - would use historical data in real implementation)
        trend_direction = "stable"
        if confidence_weighted_score > 8.0:
            trend_direction = "improving"
        elif confidence_weighted_score < 7.0:
            trend_direction = "declining"

        # Check excellence achievement
        excellence_target = self.excellence_targets.get(dimension, 8.0)
        excellence_achievement = confidence_weighted_score >= excellence_target

        # Generate key insights
        key_insights = []
        if excellence_achievement:
            key_insights.append(f"Exceeds excellence target of {excellence_target}")
        else:
            key_insights.append(f"Below excellence target of {excellence_target}")

        if std_deviation > 2.0:
            key_insights.append("High variability in feedback scores")

        feedback_types = set(item.feedback_type for item in feedback_items)
        if len(feedback_types) > 1:
            key_insights.append("Multiple feedback sources available")

        return FeedbackAnalysis(
            dimension=dimension,
            mean_score=mean_score,
            median_score=median_score,
            std_deviation=std_deviation,
            confidence_weighted_score=confidence_weighted_score,
            sample_size=len(feedback_items),
            trend_direction=trend_direction,
            excellence_achievement=excellence_achievement,
            key_insights=key_insights,
        )

    def _identify_improvement_trends(
        self, dimension_analyses: dict[str, FeedbackAnalysis]
    ) -> list[str]:
        """Identify improvement trends across dimensions."""
        trends = []

        improving_dimensions = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.trend_direction == "improving"
        ]

        if improving_dimensions:
            trends.append(f"Improving trends in: {', '.join(improving_dimensions)}")

        high_performing = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.confidence_weighted_score >= 8.5
        ]

        if high_performing:
            trends.append(f"High performance in: {', '.join(high_performing)}")

        return trends

    def _identify_concern_areas(
        self, dimension_analyses: dict[str, FeedbackAnalysis]
    ) -> list[str]:
        """Identify areas of concern across dimensions."""
        concerns = []

        declining_dimensions = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.trend_direction == "declining"
        ]

        if declining_dimensions:
            concerns.append(f"Declining trends in: {', '.join(declining_dimensions)}")

        low_performing = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.confidence_weighted_score < 7.0
        ]

        if low_performing:
            concerns.append(f"Low performance in: {', '.join(low_performing)}")

        high_variability = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.std_deviation > 2.0
        ]

        if high_variability:
            concerns.append(f"High variability in: {', '.join(high_variability)}")

        return concerns

    def _identify_excellence_indicators(
        self, dimension_analyses: dict[str, FeedbackAnalysis]
    ) -> list[str]:
        """Identify excellence indicators across dimensions."""
        indicators = []

        excellent_dimensions = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.excellence_achievement
        ]

        if excellent_dimensions:
            indicators.append(
                f"Excellence achieved in: {', '.join(excellent_dimensions)}"
            )

        consistent_quality = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.std_deviation < 1.0
            and analysis.confidence_weighted_score >= 8.0
        ]

        if consistent_quality:
            indicators.append(
                f"Consistent high quality in: {', '.join(consistent_quality)}"
            )

        return indicators

    def _generate_feedback_recommendations(
        self,
        dimension_analyses: dict[str, FeedbackAnalysis],
        meets_excellence_standards: bool,
    ) -> list[str]:
        """Generate recommendations based on feedback analysis."""
        recommendations = []

        # Dimension-specific recommendations
        for analysis in dimension_analyses.values():
            if not analysis.excellence_achievement:
                dimension_name = analysis.dimension.value.replace("_", " ").title()
                recommendations.append(
                    f"Improve {dimension_name} to meet excellence targets"
                )

        # Overall recommendations
        if meets_excellence_standards:
            recommendations.append(
                "Maintain current excellence standards across all dimensions"
            )
            recommendations.append(
                "Continue monitoring feedback trends for sustained quality"
            )
        else:
            recommendations.append(
                "Focus on achieving excellence targets in underperforming dimensions"
            )
            recommendations.append(
                "Implement targeted improvements based on user feedback"
            )

        # Sample size recommendations
        low_sample_dimensions = [
            analysis.dimension.value
            for analysis in dimension_analyses.values()
            if analysis.sample_size < 10
        ]

        if low_sample_dimensions:
            recommendations.append(
                "Increase feedback collection for better statistical confidence"
            )

        return recommendations


async def run_structured_feedback_collection(
    session_data: list[dict[str, Any]], config: dict[str, Any] = None
) -> ComprehensiveFeedbackReport:
    """
    Run comprehensive structured feedback collection and analysis.

    Args:
        session_data: List of session data for feedback collection
        config: Configuration for feedback collection (optional)

    Returns:
        Comprehensive feedback report
    """
    if config is None:
        config = {
            "excellence_targets": {
                "narrative_quality": 8.5,
                "therapeutic_relevance": 8.0,
                "user_engagement": 8.5,
                "safety_comfort": 9.0,
            }
        }

    collector = StructuredFeedbackCollector(config)

    try:
        # Collect automated feedback for each session
        for session in session_data:
            await collector.collect_automated_feedback(
                session_id=session.get("session_id", "unknown"),
                narrative_content=session.get("narrative_content", []),
                therapeutic_context=session.get("therapeutic_context", {}),
                user_interactions=session.get("user_interactions", {}),
            )

        # Analyze collected feedback
        report = await collector.analyze_feedback_comprehensive()

        return report

    except Exception as e:
        logger.error(f"❌ Structured feedback collection failed: {e}")
        return ComprehensiveFeedbackReport(
            report_id=f"error_report_{int(time.time())}",
            generation_timestamp=datetime.utcnow(),
            session_count=0,
            total_feedback_items=0,
            feedback_recommendations=[
                "Fix feedback collection system",
                "Review session data format",
            ],
        )


if __name__ == "__main__":
    import asyncio

    async def main():
        # Example session data for testing
        test_sessions = [
            {
                "session_id": "session_001",
                "narrative_content": [
                    "You find yourself in a peaceful garden with your guide, Sage.",
                    "Sage helps you practice mindfulness techniques to manage anxiety.",
                    "The session concludes with you feeling more centered and supported.",
                ],
                "therapeutic_context": {
                    "therapeutic_goals": ["anxiety_management", "mindfulness"],
                    "trigger_topics": ["violence", "trauma"],
                },
                "user_interactions": {
                    "interactions": ["choice_1", "choice_2", "choice_3"],
                    "response_times": [15, 22, 18],
                    "session_duration": 720,
                },
            },
            {
                "session_id": "session_002",
                "narrative_content": [
                    "Your character faces a challenging situation requiring confidence.",
                    "Through supportive dialogue, you explore ways to build self-assurance.",
                    "The narrative provides opportunities for growth and empowerment.",
                ],
                "therapeutic_context": {
                    "therapeutic_goals": ["confidence_building", "self_reflection"],
                    "trigger_topics": ["failure", "criticism"],
                },
                "user_interactions": {
                    "interactions": ["choice_1", "choice_2"],
                    "response_times": [25, 30],
                    "session_duration": 480,
                },
            },
        ]

        report = await run_structured_feedback_collection(test_sessions)

        print("\n" + "=" * 80)
        print("STRUCTURED FEEDBACK COLLECTION RESULTS")
        print("=" * 80)

        print(f"\n📊 Report: {report.report_id}")
        print(f"   Sessions Analyzed: {report.session_count}")
        print(f"   Total Feedback Items: {report.total_feedback_items}")
        print(f"   Overall Excellence Score: {report.overall_excellence_score:.1f}/10")
        print(
            f"   Meets Excellence Standards: {'✅ YES' if report.meets_excellence_standards else '❌ NO'}"
        )

        print("\n🔍 Dimension Analysis:")
        for dimension_name, analysis in report.dimension_analyses.items():
            print(f"   {dimension_name.replace('_', ' ').title()}:")
            print(f"      Score: {analysis.confidence_weighted_score:.1f}/10")
            print(
                f"      Excellence: {'✅' if analysis.excellence_achievement else '❌'}"
            )
            print(f"      Trend: {analysis.trend_direction}")
            print(f"      Sample Size: {analysis.sample_size}")

        if report.improvement_trends:
            print("\n📈 Improvement Trends:")
            for trend in report.improvement_trends:
                print(f"   ✨ {trend}")

        if report.concern_areas:
            print("\n⚠️ Concern Areas:")
            for concern in report.concern_areas:
                print(f"   🔍 {concern}")

        if report.feedback_recommendations:
            print("\n💡 Recommendations:")
            for rec in report.feedback_recommendations[:5]:
                print(f"   📋 {rec}")

    asyncio.run(main())
