"""

# Logseq: [[TTA.dev/Testing/Comprehensive_validation/Excellence_narrative_quality_assessor]]
Excellence-Focused Narrative Quality Assessment for TTA

This module enhances the existing narrative analysis systems to meet higher
quality targets: narrative coherence ≥8.5/10, therapeutic relevance ≥8.0/10,
user engagement ≥8.5/10. It provides advanced quality metrics, automated
analysis, and detailed reporting for therapeutic storytelling excellence.

Key Features:
- Advanced narrative coherence analysis with excellence targets
- Therapeutic relevance assessment with clinical validation
- User engagement measurement with behavioral indicators
- Automated quality scoring with detailed breakdowns
- Excellence-focused recommendations and improvement suggestions
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from src.components.therapeutic_systems_enhanced.therapeutic_integration_system import (
    TherapeuticIntegrationSystem,
)
from testing.extended_evaluation.living_worlds_metrics import LivingWorldsEvaluator

# Import existing narrative analysis components
from testing.extended_evaluation.narrative_analysis import (
    NarrativeAnalyzer,
)

logger = logging.getLogger(__name__)


class ExcellenceQualityDimension(Enum):
    """Excellence-focused quality dimensions for narrative assessment."""

    NARRATIVE_COHERENCE = "narrative_coherence"
    THERAPEUTIC_RELEVANCE = "therapeutic_relevance"
    USER_ENGAGEMENT = "user_engagement"
    CHARACTER_DEVELOPMENT = "character_development"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    CREATIVE_EXCELLENCE = "creative_excellence"
    THERAPEUTIC_INTEGRATION = "therapeutic_integration"


@dataclass
class ExcellenceNarrativeMetrics:
    """Comprehensive metrics for excellence-focused narrative quality assessment."""

    session_id: str
    assessment_timestamp: datetime

    # Core excellence scores (target ≥8.5/10 for coherence/engagement, ≥8.0/10 for therapeutic)
    narrative_coherence_score: float  # Target: ≥8.5/10
    therapeutic_relevance_score: float  # Target: ≥8.0/10
    user_engagement_score: float  # Target: ≥8.5/10

    # Detailed quality dimensions
    character_consistency_score: float = 0.0
    plot_logic_score: float = 0.0
    world_consistency_score: float = 0.0
    dialogue_quality_score: float = 0.0
    emotional_resonance_score: float = 0.0
    creative_excellence_score: float = 0.0
    therapeutic_integration_score: float = 0.0

    # Excellence indicators
    excellence_indicators: list[str] = field(default_factory=list)
    quality_highlights: list[str] = field(default_factory=list)
    improvement_areas: list[str] = field(default_factory=list)

    # Detailed analysis
    narrative_strengths: list[str] = field(default_factory=list)
    therapeutic_effectiveness: dict[str, float] = field(default_factory=dict)
    engagement_factors: dict[str, float] = field(default_factory=dict)

    # Excellence achievement
    meets_excellence_standards: bool = False
    excellence_score: float = 0.0  # Overall excellence rating

    # Recommendations for excellence
    excellence_recommendations: list[str] = field(default_factory=list)


@dataclass
class TherapeuticEffectivenessAnalysis:
    """Analysis of therapeutic effectiveness in narrative content."""

    therapeutic_goals_addressed: list[str]
    therapeutic_techniques_used: list[str]
    emotional_support_quality: float
    growth_opportunity_score: float
    safety_maintenance_score: float
    clinical_appropriateness: float


class ExcellenceNarrativeQualityAssessor:
    """
    Excellence-focused narrative quality assessment system.

    Enhances existing narrative analysis with higher quality targets
    and comprehensive excellence evaluation for therapeutic storytelling.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

        # Initialize existing components
        self.narrative_analyzer = NarrativeAnalyzer()
        self.living_worlds_evaluator = LivingWorldsEvaluator()
        self.therapeutic_system = TherapeuticIntegrationSystem()

        # Excellence targets (higher than existing standards)
        self.excellence_targets = {
            "narrative_coherence": 8.5,
            "therapeutic_relevance": 8.0,
            "user_engagement": 8.5,
            "character_consistency": 8.5,
            "plot_logic": 8.0,
            "world_consistency": 8.5,
            "dialogue_quality": 8.0,
            "emotional_resonance": 8.5,
            "creative_excellence": 8.0,
            "therapeutic_integration": 8.0,
        }

        # Excellence indicators
        self.excellence_indicators = {
            "narrative_coherence": [
                "seamless_plot_progression",
                "consistent_character_behavior",
                "logical_world_rules",
                "temporal_consistency",
                "causal_relationships",
            ],
            "therapeutic_relevance": [
                "clear_therapeutic_goals",
                "appropriate_interventions",
                "emotional_validation",
                "growth_opportunities",
                "safety_maintenance",
            ],
            "user_engagement": [
                "compelling_choices",
                "emotional_investment",
                "narrative_immersion",
                "character_connection",
                "continuation_desire",
            ],
        }

    async def assess_narrative_excellence(
        self,
        session_id: str,
        narrative_content: list[str],
        therapeutic_context: dict[str, Any] = None,
    ) -> ExcellenceNarrativeMetrics:
        """
        Perform comprehensive excellence-focused narrative quality assessment.

        Args:
            session_id: Session identifier
            narrative_content: List of narrative turns/content
            therapeutic_context: Therapeutic context and goals

        Returns:
            Comprehensive excellence metrics
        """
        logger.info(f"🎯 Assessing narrative excellence for session {session_id}")

        # Initialize metrics
        metrics = ExcellenceNarrativeMetrics(
            session_id=session_id,
            assessment_timestamp=datetime.utcnow(),
            narrative_coherence_score=0.0,
            therapeutic_relevance_score=0.0,
            user_engagement_score=0.0,
        )

        try:
            # Assess narrative coherence with excellence standards
            metrics.narrative_coherence_score = (
                await self._assess_excellence_narrative_coherence(
                    narrative_content, session_id
                )
            )

            # Assess therapeutic relevance with clinical standards
            metrics.therapeutic_relevance_score = (
                await self._assess_excellence_therapeutic_relevance(
                    narrative_content, therapeutic_context or {}
                )
            )

            # Assess user engagement with behavioral indicators
            metrics.user_engagement_score = (
                await self._assess_excellence_user_engagement(
                    narrative_content, session_id
                )
            )

            # Detailed quality dimension assessment
            await self._assess_detailed_quality_dimensions(
                metrics, narrative_content, therapeutic_context
            )

            # Excellence analysis
            await self._analyze_excellence_achievement(metrics)

            # Generate excellence recommendations
            metrics.excellence_recommendations = (
                self._generate_excellence_recommendations(metrics)
            )

            logger.info(f"✅ Excellence assessment completed for session {session_id}")
            return metrics

        except Exception as e:
            logger.error(
                f"❌ Excellence assessment failed for session {session_id}: {e}"
            )
            metrics.excellence_recommendations = [
                "Fix assessment system issues",
                "Review narrative content",
            ]
            return metrics

    async def _assess_excellence_narrative_coherence(
        self, narrative_content: list[str], session_id: str
    ) -> float:
        """Assess narrative coherence with excellence standards (target ≥8.5/10)."""

        # Use existing narrative analyzer as base
        base_coherence = 0.0
        for i, content in enumerate(narrative_content):
            turn_coherence = await self.narrative_analyzer.evaluate_turn_coherence(
                {"narrative_content": content, "session_id": session_id}, i + 1
            )
            base_coherence += turn_coherence

        if narrative_content:
            base_coherence /= len(narrative_content)
        else:
            base_coherence = 7.0  # Default baseline

        # Excellence enhancements
        excellence_bonus = 0.0

        # Advanced coherence analysis
        combined_narrative = " ".join(narrative_content)

        # Character consistency analysis
        character_consistency = self._analyze_character_consistency_excellence(
            combined_narrative
        )
        excellence_bonus += (character_consistency - 7.0) * 0.3

        # Plot logic analysis
        plot_logic = self._analyze_plot_logic_excellence(combined_narrative)
        excellence_bonus += (plot_logic - 7.0) * 0.3

        # Temporal consistency analysis
        temporal_consistency = self._analyze_temporal_consistency_excellence(
            combined_narrative
        )
        excellence_bonus += (temporal_consistency - 7.0) * 0.2

        # Causal relationship analysis
        causal_relationships = self._analyze_causal_relationships_excellence(
            combined_narrative
        )
        excellence_bonus += (causal_relationships - 7.0) * 0.2

        final_score = base_coherence + excellence_bonus
        return min(10.0, max(0.0, final_score))

    async def _assess_excellence_therapeutic_relevance(
        self, narrative_content: list[str], therapeutic_context: dict[str, Any]
    ) -> float:
        """Assess therapeutic relevance with clinical standards (target ≥8.0/10)."""

        combined_narrative = " ".join(narrative_content)
        score = 7.0  # Base therapeutic score

        # Therapeutic goal alignment
        therapeutic_goals = therapeutic_context.get("therapeutic_goals", [])
        for goal in therapeutic_goals:
            if self._check_therapeutic_goal_integration(combined_narrative, goal):
                score += 0.4

        # Therapeutic technique integration
        therapeutic_techniques = self._identify_therapeutic_techniques(
            combined_narrative
        )
        score += min(1.5, len(therapeutic_techniques) * 0.3)

        # Emotional validation and support
        emotional_support_score = self._assess_emotional_support_quality(
            combined_narrative
        )
        score += (emotional_support_score - 7.0) * 0.3

        # Growth opportunity provision
        growth_opportunities = self._identify_growth_opportunities(combined_narrative)
        score += min(1.0, len(growth_opportunities) * 0.2)

        # Safety and appropriateness
        safety_score = self._assess_therapeutic_safety_excellence(
            combined_narrative, therapeutic_context
        )
        score += (safety_score - 8.0) * 0.2

        return min(10.0, max(0.0, score))

    async def _assess_excellence_user_engagement(
        self, narrative_content: list[str], session_id: str
    ) -> float:
        """Assess user engagement with behavioral indicators (target ≥8.5/10)."""

        combined_narrative = " ".join(narrative_content)
        score = 7.5  # Base engagement score

        # Choice meaningfulness analysis
        choice_quality = self._analyze_choice_meaningfulness(combined_narrative)
        score += (choice_quality - 7.0) * 0.3

        # Emotional investment indicators
        emotional_investment = self._analyze_emotional_investment(combined_narrative)
        score += (emotional_investment - 7.0) * 0.25

        # Narrative immersion factors
        immersion_score = self._analyze_narrative_immersion(combined_narrative)
        score += (immersion_score - 7.0) * 0.25

        # Character connection strength
        character_connection = self._analyze_character_connection(combined_narrative)
        score += (character_connection - 7.0) * 0.2

        return min(10.0, max(0.0, score))

    async def _assess_detailed_quality_dimensions(
        self,
        metrics: ExcellenceNarrativeMetrics,
        narrative_content: list[str],
        therapeutic_context: dict[str, Any],
    ):
        """Assess detailed quality dimensions for comprehensive analysis."""

        combined_narrative = " ".join(narrative_content)

        # Character consistency
        metrics.character_consistency_score = (
            self._analyze_character_consistency_excellence(combined_narrative)
        )

        # Plot logic
        metrics.plot_logic_score = self._analyze_plot_logic_excellence(
            combined_narrative
        )

        # World consistency
        metrics.world_consistency_score = self._analyze_world_consistency_excellence(
            combined_narrative
        )

        # Dialogue quality
        metrics.dialogue_quality_score = self._analyze_dialogue_quality_excellence(
            combined_narrative
        )

        # Emotional resonance
        metrics.emotional_resonance_score = (
            self._analyze_emotional_resonance_excellence(combined_narrative)
        )

        # Creative excellence
        metrics.creative_excellence_score = self._analyze_creative_excellence(
            combined_narrative
        )

        # Therapeutic integration
        metrics.therapeutic_integration_score = (
            self._analyze_therapeutic_integration_excellence(
                combined_narrative, therapeutic_context or {}
            )
        )

    def _analyze_character_consistency_excellence(self, narrative: str) -> float:
        """Analyze character consistency with excellence standards."""
        score = 8.0  # High baseline for excellence

        # Character voice consistency
        if self._check_consistent_character_voice(narrative):
            score += 0.5

        # Behavioral consistency
        if self._check_behavioral_consistency(narrative):
            score += 0.5

        # Character development progression
        if self._check_character_development_progression(narrative):
            score += 0.5

        return min(10.0, score)

    def _analyze_plot_logic_excellence(self, narrative: str) -> float:
        """Analyze plot logic with excellence standards."""
        score = 7.5  # Base plot logic score

        # Cause and effect relationships
        if self._check_cause_effect_logic(narrative):
            score += 0.8

        # Plot progression coherence
        if self._check_plot_progression_coherence(narrative):
            score += 0.7

        # Conflict resolution logic
        if self._check_conflict_resolution_logic(narrative):
            score += 0.5

        return min(10.0, score)

    def _check_therapeutic_goal_integration(self, narrative: str, goal: str) -> bool:
        """Check if therapeutic goal is meaningfully integrated."""
        goal_keywords = {
            "anxiety_management": ["calm", "breathe", "relax", "peaceful", "grounding"],
            "depression_support": ["hope", "strength", "support", "care", "value"],
            "self_reflection": [
                "think",
                "consider",
                "reflect",
                "understand",
                "realize",
            ],
            "confidence_building": ["capable", "strong", "achieve", "succeed", "proud"],
        }

        keywords = goal_keywords.get(goal, [goal.replace("_", " ")])
        return any(keyword in narrative.lower() for keyword in keywords)

    def _identify_therapeutic_techniques(self, narrative: str) -> list[str]:
        """Identify therapeutic techniques used in narrative."""
        techniques = []
        narrative_lower = narrative.lower()

        technique_patterns = {
            "mindfulness": ["mindful", "present moment", "awareness", "observe"],
            "cognitive_restructuring": ["think differently", "perspective", "reframe"],
            "grounding": ["ground", "five senses", "here and now", "breathe"],
            "validation": ["understand", "valid", "makes sense", "hear you"],
        }

        for technique, patterns in technique_patterns.items():
            if any(pattern in narrative_lower for pattern in patterns):
                techniques.append(technique)

        return techniques

    def _assess_emotional_support_quality(self, narrative: str) -> float:
        """Assess quality of emotional support provided."""
        score = 7.0
        narrative_lower = narrative.lower()

        # Empathy indicators
        empathy_words = ["understand", "feel", "hear", "see", "know"]
        empathy_count = sum(1 for word in empathy_words if word in narrative_lower)
        score += min(1.0, empathy_count * 0.2)

        # Validation indicators
        validation_phrases = ["makes sense", "valid", "natural", "okay to feel"]
        validation_count = sum(
            1 for phrase in validation_phrases if phrase in narrative_lower
        )
        score += min(1.0, validation_count * 0.3)

        # Support indicators
        support_words = ["support", "help", "together", "here for you"]
        support_count = sum(1 for word in support_words if word in narrative_lower)
        score += min(1.0, support_count * 0.2)

        return min(10.0, score)

    def _identify_growth_opportunities(self, narrative: str) -> list[str]:
        """Identify growth opportunities presented in narrative."""
        opportunities = []
        narrative_lower = narrative.lower()

        opportunity_patterns = {
            "skill_practice": ["practice", "try", "exercise", "technique"],
            "self_discovery": ["discover", "learn about yourself", "explore"],
            "challenge_facing": ["challenge", "face", "overcome", "confront"],
            "reflection": ["reflect", "think about", "consider", "ponder"],
        }

        for opportunity, patterns in opportunity_patterns.items():
            if any(pattern in narrative_lower for pattern in patterns):
                opportunities.append(opportunity)

        return opportunities

    def _assess_therapeutic_safety_excellence(
        self, narrative: str, therapeutic_context: dict[str, Any]
    ) -> float:
        """Assess therapeutic safety with excellence standards."""
        score = 8.5  # High baseline for safety

        # Check for trigger avoidance
        trigger_topics = therapeutic_context.get("trigger_topics", [])
        for trigger in trigger_topics:
            if trigger.lower() in narrative.lower():
                score -= 1.0  # Penalty for trigger mention

        # Check for crisis indicators
        crisis_words = ["harm", "hurt", "end it all", "no point"]
        crisis_mentions = sum(1 for word in crisis_words if word in narrative.lower())
        if crisis_mentions > 0:
            score -= crisis_mentions * 0.5

        # Positive safety indicators
        safety_words = ["safe", "secure", "protected", "supported"]
        safety_count = sum(1 for word in safety_words if word in narrative.lower())
        score += min(0.5, safety_count * 0.1)

        return min(10.0, max(0.0, score))

    def _analyze_choice_meaningfulness(self, narrative: str) -> float:
        """Analyze meaningfulness of choices presented."""
        score = 7.5

        # Look for choice indicators
        choice_words = ["choose", "decide", "option", "path", "way"]
        choice_count = sum(1 for word in choice_words if word in narrative.lower())
        score += min(1.0, choice_count * 0.2)

        # Look for consequence indicators
        consequence_words = ["result", "outcome", "consequence", "effect"]
        consequence_count = sum(
            1 for word in consequence_words if word in narrative.lower()
        )
        score += min(1.0, consequence_count * 0.3)

        return min(10.0, score)

    def _analyze_emotional_investment(self, narrative: str) -> float:
        """Analyze emotional investment indicators."""
        score = 7.0

        # Emotional words
        emotion_words = ["feel", "emotion", "heart", "soul", "deeply"]
        emotion_count = sum(1 for word in emotion_words if word in narrative.lower())
        score += min(1.5, emotion_count * 0.2)

        # Personal connection words
        personal_words = ["you", "your", "yourself", "personally"]
        personal_count = sum(1 for word in personal_words if word in narrative.lower())
        score += min(1.0, personal_count * 0.1)

        return min(10.0, score)

    def _analyze_narrative_immersion(self, narrative: str) -> float:
        """Analyze narrative immersion factors."""
        score = 7.5

        # Descriptive richness
        descriptive_words = ["see", "hear", "feel", "smell", "taste", "vivid", "clear"]
        descriptive_count = sum(
            1 for word in descriptive_words if word in narrative.lower()
        )
        score += min(1.0, descriptive_count * 0.1)

        # Present tense usage (more immersive)
        present_indicators = ["now", "currently", "at this moment", "right now"]
        present_count = sum(
            1 for indicator in present_indicators if indicator in narrative.lower()
        )
        score += min(0.5, present_count * 0.2)

        return min(10.0, score)

    def _analyze_character_connection(self, narrative: str) -> float:
        """Analyze character connection strength."""
        score = 7.0

        # Character interaction words
        interaction_words = ["with you", "together", "companion", "friend", "guide"]
        interaction_count = sum(
            1 for word in interaction_words if word in narrative.lower()
        )
        score += min(1.0, interaction_count * 0.3)

        # Character empathy indicators
        empathy_words = ["understand you", "feel for you", "care about", "worry about"]
        empathy_count = sum(
            1 for phrase in empathy_words if phrase in narrative.lower()
        )
        score += min(1.0, empathy_count * 0.4)

        return min(10.0, score)

    async def _analyze_excellence_achievement(
        self, metrics: ExcellenceNarrativeMetrics
    ):
        """Analyze overall excellence achievement."""

        # Calculate excellence score
        core_scores = [
            metrics.narrative_coherence_score,
            metrics.therapeutic_relevance_score,
            metrics.user_engagement_score,
        ]

        detailed_scores = [
            metrics.character_consistency_score,
            metrics.plot_logic_score,
            metrics.world_consistency_score,
            metrics.dialogue_quality_score,
            metrics.emotional_resonance_score,
            metrics.creative_excellence_score,
            metrics.therapeutic_integration_score,
        ]

        # Weighted excellence calculation
        core_average = sum(core_scores) / len(core_scores) if core_scores else 0.0
        detailed_average = (
            sum(detailed_scores) / len(detailed_scores) if detailed_scores else 0.0
        )

        metrics.excellence_score = (core_average * 0.7) + (detailed_average * 0.3)

        # Check excellence standards
        meets_coherence = (
            metrics.narrative_coherence_score
            >= self.excellence_targets["narrative_coherence"]
        )
        meets_therapeutic = (
            metrics.therapeutic_relevance_score
            >= self.excellence_targets["therapeutic_relevance"]
        )
        meets_engagement = (
            metrics.user_engagement_score >= self.excellence_targets["user_engagement"]
        )

        metrics.meets_excellence_standards = (
            meets_coherence and meets_therapeutic and meets_engagement
        )

        # Identify excellence indicators
        if meets_coherence:
            metrics.excellence_indicators.append("Exceptional narrative coherence")
        if meets_therapeutic:
            metrics.excellence_indicators.append("Outstanding therapeutic relevance")
        if meets_engagement:
            metrics.excellence_indicators.append("Excellent user engagement")

        # Identify quality highlights
        if metrics.character_consistency_score >= 8.5:
            metrics.quality_highlights.append("Exceptional character consistency")
        if metrics.emotional_resonance_score >= 8.5:
            metrics.quality_highlights.append("Outstanding emotional resonance")
        if metrics.therapeutic_integration_score >= 8.0:
            metrics.quality_highlights.append("Excellent therapeutic integration")

    def _generate_excellence_recommendations(
        self, metrics: ExcellenceNarrativeMetrics
    ) -> list[str]:
        """Generate recommendations for achieving excellence."""
        recommendations = []

        # Narrative coherence recommendations
        if (
            metrics.narrative_coherence_score
            < self.excellence_targets["narrative_coherence"]
        ):
            recommendations.append(
                "Enhance narrative coherence through better plot structure"
            )
            recommendations.append("Improve character consistency across interactions")
            recommendations.append(
                "Strengthen causal relationships in story progression"
            )

        # Therapeutic relevance recommendations
        if (
            metrics.therapeutic_relevance_score
            < self.excellence_targets["therapeutic_relevance"]
        ):
            recommendations.append("Integrate therapeutic goals more explicitly")
            recommendations.append("Include more evidence-based therapeutic techniques")
            recommendations.append("Enhance emotional validation and support")

        # User engagement recommendations
        if metrics.user_engagement_score < self.excellence_targets["user_engagement"]:
            recommendations.append("Create more meaningful and impactful choices")
            recommendations.append(
                "Increase emotional investment through character development"
            )
            recommendations.append(
                "Enhance narrative immersion with richer descriptions"
            )

        # Excellence achievement recommendations
        if metrics.meets_excellence_standards:
            recommendations.append("Maintain current excellence standards")
            recommendations.append("Continue refining therapeutic integration")
        else:
            recommendations.append(
                "Focus on achieving excellence targets in all core areas"
            )
            recommendations.append("Implement systematic quality improvement processes")

        return recommendations


async def run_excellence_narrative_assessment(
    session_id: str,
    narrative_content: list[str],
    therapeutic_context: dict[str, Any] = None,
    config: dict[str, Any] = None,
) -> ExcellenceNarrativeMetrics:
    """
    Run excellence-focused narrative quality assessment.

    Args:
        session_id: Session identifier
        narrative_content: List of narrative content to assess
        therapeutic_context: Therapeutic context and goals
        config: Assessment configuration

    Returns:
        Excellence narrative metrics
    """
    if config is None:
        config = {
            "excellence_targets": {
                "narrative_coherence": 8.5,
                "therapeutic_relevance": 8.0,
                "user_engagement": 8.5,
            }
        }

    assessor = ExcellenceNarrativeQualityAssessor(config)

    return await assessor.assess_narrative_excellence(
        session_id=session_id,
        narrative_content=narrative_content,
        therapeutic_context=therapeutic_context,
    )


if __name__ == "__main__":
    import asyncio

    async def main():
        # Example narrative content for testing
        test_narrative = [
            "You find yourself in a peaceful garden, feeling the weight of recent stress on your shoulders. Your companion, Sage, approaches with a gentle smile.",
            "Sage notices your tension and suggests trying a mindfulness exercise together. 'Let's focus on what we can see, hear, and feel right now,' they say supportively.",
            "As you practice the grounding technique, you begin to feel more centered. Sage validates your experience: 'It's completely natural to feel overwhelmed sometimes.'",
        ]

        test_context = {
            "therapeutic_goals": ["anxiety_management", "mindfulness"],
            "emotional_state": "anxious",
            "trigger_topics": ["violence", "trauma"],
        }

        metrics = await run_excellence_narrative_assessment(
            session_id="test_session_001",
            narrative_content=test_narrative,
            therapeutic_context=test_context,
        )

        if metrics.excellence_indicators:
            for _indicator in metrics.excellence_indicators:
                pass

        if metrics.quality_highlights:
            for _highlight in metrics.quality_highlights:
                pass

        if metrics.excellence_recommendations:
            for _rec in metrics.excellence_recommendations[:5]:
                pass

    asyncio.run(main())
