"""
Progress-Based Therapeutic Adaptation System for TTA Prototype

This module integrates progress tracking with therapeutic content delivery to create
an adaptive therapy system that adjusts interventions, content difficulty, and
therapeutic approaches based on user progress patterns, emotional growth, and
goal achievement metrics.

Classes:
    ProgressBasedTherapeuticAdaptation: Main integration system
    AdaptiveTherapyOrchestrator: Orchestrates therapy adaptation decisions
    TherapeuticJourneyPlanner: Plans long-term therapeutic journeys
    ProgressBasedInterventionSelector: Selects interventions based on progress
    ContentDifficultyAdapter: Adapts content difficulty based on progress
"""

import logging
import statistics

# Import system components
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Add paths for imports
core_path = Path(__file__).parent
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    # Try relative imports first (when running as part of package)
    from ..models.data_models import (
        CharacterState,
        CompletedIntervention,
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticGoal,
        TherapeuticGoalStatus,
        TherapeuticProgress,
        ValidationError,
    )
    from ..models.therapeutic_llm_client import (
        SafetyLevel,
        TherapeuticContentType,
        TherapeuticContext,
        TherapeuticLLMClient,
        TherapeuticResponse,
    )
    from .personalization_engine import (
        ContentAdaptation,
        ContentAdaptationSystem,
        PersonalizationContext,
        PersonalizationEngine,
        PersonalizedRecommendation,
        RecommendationSystem,
    )
    from .progress_tracking_personalization import (
        PersonalizationProfile,
        ProgressAnalysisResult,
        ProgressMetric,
        ProgressMetricType,
        ProgressTrackingPersonalization,
        TherapeuticProgressAnalyzer,
    )
    from .therapeutic_content_integration import (
        TherapeuticContentIntegration,
        TherapeuticOpportunityDetector,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            CharacterState,
            CompletedIntervention,
            CopingStrategy,
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticGoal,
            TherapeuticGoalStatus,
            TherapeuticProgress,
            ValidationError,
        )
        from personalization_engine import (
            ContentAdaptation,
            ContentAdaptationSystem,
            PersonalizationContext,
            PersonalizationEngine,
            PersonalizedRecommendation,
            RecommendationSystem,
        )
        from progress_tracking_personalization import (
            PersonalizationProfile,
            ProgressAnalysisResult,
            ProgressMetric,
            ProgressMetricType,
            ProgressTrackingPersonalization,
            TherapeuticProgressAnalyzer,
        )
        from therapeutic_content_integration import (
            TherapeuticContentIntegration,
            TherapeuticOpportunityDetector,
        )
        from therapeutic_llm_client import (
            SafetyLevel,
            TherapeuticContentType,
            TherapeuticContext,
            TherapeuticLLMClient,
            TherapeuticResponse,
        )
    except ImportError:
        # Final fallback - create minimal mock classes for testing
        import logging
        logging.warning("Could not import required classes, using mock implementations")

        class MockClass:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        # Set mock classes
        SessionState = MockClass
        TherapeuticProgress = MockClass
        ProgressTrackingPersonalization = MockClass
        PersonalizationEngine = MockClass
        TherapeuticContentIntegration = MockClass

logger = logging.getLogger(__name__)


class AdaptationStrategy(Enum):
    """Strategies for therapeutic adaptation based on progress."""
    ACCELERATE = "accelerate"  # Speed up for high performers
    CONSOLIDATE = "consolidate"  # Reinforce current level
    REMEDIATE = "remediate"  # Address gaps and difficulties
    DIVERSIFY = "diversify"  # Try different approaches
    INTENSIFY = "intensify"  # Increase therapeutic intensity
    SIMPLIFY = "simplify"  # Reduce complexity
    MAINTAIN = "maintain"  # Continue current approach


class TherapeuticPhase(Enum):
    """Phases of therapeutic journey."""
    ASSESSMENT = "assessment"
    FOUNDATION_BUILDING = "foundation_building"
    SKILL_DEVELOPMENT = "skill_development"
    INTEGRATION = "integration"
    MAINTENANCE = "maintenance"
    ADVANCED_WORK = "advanced_work"


@dataclass
class AdaptationDecision:
    """Represents a therapeutic adaptation decision."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    adaptation_strategy: AdaptationStrategy = AdaptationStrategy.MAINTAIN
    rationale: str = ""
    confidence_level: float = 0.8  # 0.0 to 1.0
    expected_outcomes: list[str] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    review_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(weeks=2))
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate adaptation decision."""
        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty")
        if not self.rationale.strip():
            raise ValidationError("Rationale cannot be empty")
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        return True


@dataclass
class TherapeuticJourneyPlan:
    """Represents a long-term therapeutic journey plan."""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    current_phase: TherapeuticPhase = TherapeuticPhase.ASSESSMENT
    planned_phases: list[dict[str, Any]] = field(default_factory=list)
    milestones: list[dict[str, Any]] = field(default_factory=list)
    estimated_duration: int = 12  # weeks
    progress_checkpoints: list[datetime] = field(default_factory=list)
    adaptation_history: list[AdaptationDecision] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate therapeutic journey plan."""
        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty")
        if self.estimated_duration <= 0:
            raise ValidationError("Estimated duration must be positive")
        return True


class ProgressBasedInterventionSelector:
    """Selects therapeutic interventions based on progress patterns."""

    def __init__(self):
        """Initialize the intervention selector."""
        self.intervention_effectiveness_map = self._initialize_effectiveness_map()
        self.progress_thresholds = self._initialize_progress_thresholds()
        logger.info("ProgressBasedInterventionSelector initialized")

    def _initialize_effectiveness_map(self) -> dict[ProgressMetricType, list[InterventionType]]:
        """Initialize mapping of progress metrics to effective interventions."""
        return {
            ProgressMetricType.EMOTIONAL_REGULATION: [
                InterventionType.MINDFULNESS,
                InterventionType.EMOTIONAL_REGULATION,
                InterventionType.COPING_SKILLS
            ],
            ProgressMetricType.COPING_SKILLS_USAGE: [
                InterventionType.COPING_SKILLS,
                InterventionType.BEHAVIORAL_ACTIVATION,
                InterventionType.COGNITIVE_RESTRUCTURING
            ],
            ProgressMetricType.GOAL_ACHIEVEMENT: [
                InterventionType.BEHAVIORAL_ACTIVATION,
                InterventionType.COGNITIVE_RESTRUCTURING,
                InterventionType.COPING_SKILLS
            ],
            ProgressMetricType.ENGAGEMENT_LEVEL: [
                InterventionType.BEHAVIORAL_ACTIVATION,
                InterventionType.MINDFULNESS,
                InterventionType.COPING_SKILLS
            ]
        }

    def _initialize_progress_thresholds(self) -> dict[str, float]:
        """Initialize thresholds for progress-based decisions."""
        return {
            "high_progress": 0.75,
            "moderate_progress": 0.50,
            "low_progress": 0.25,
            "stagnation_threshold": 0.05,  # Less than 5% improvement
            "regression_threshold": -0.10   # More than 10% decline
        }

    def select_interventions(self, progress_analysis: ProgressAnalysisResult,
                           current_interventions: list[InterventionType],
                           max_interventions: int = 3) -> list[InterventionType]:
        """Select interventions based on progress analysis."""
        try:
            selected_interventions = []

            # Analyze progress trends to determine intervention needs
            for metric_type, analysis in progress_analysis.metric_trends.items():
                current_value = analysis.get("current_value", 0.0)
                improvement_rate = analysis.get("improvement_rate", 0.0)
                trend_slope = analysis.get("trend_slope", 0.0)

                # Determine intervention priority based on progress
                if current_value < self.progress_thresholds["low_progress"]:
                    # Low performance - prioritize foundational interventions
                    priority_interventions = self.intervention_effectiveness_map.get(metric_type, [])
                    selected_interventions.extend(priority_interventions[:2])

                elif improvement_rate < self.progress_thresholds["stagnation_threshold"]:
                    # Stagnation - try different approaches
                    available_interventions = self.intervention_effectiveness_map.get(metric_type, [])
                    # Exclude current interventions to try something new
                    new_interventions = [i for i in available_interventions if i not in current_interventions]
                    selected_interventions.extend(new_interventions[:1])

                elif trend_slope < self.progress_thresholds["regression_threshold"]:
                    # Regression - intensify current approach or switch
                    if current_interventions:
                        # Continue with current but add support
                        selected_interventions.extend(current_interventions[:1])
                    priority_interventions = self.intervention_effectiveness_map.get(metric_type, [])
                    selected_interventions.extend(priority_interventions[:1])

            # Remove duplicates and limit to max_interventions
            unique_interventions = list(dict.fromkeys(selected_interventions))
            return unique_interventions[:max_interventions]

        except Exception as e:
            logger.error(f"Error selecting interventions: {e}")
            return current_interventions[:max_interventions]  # Fallback to current

    def assess_intervention_effectiveness(self, intervention_history: list[CompletedIntervention],
                                        progress_metrics: list[ProgressMetric]) -> dict[InterventionType, float]:
        """Assess the effectiveness of different interventions."""
        effectiveness_scores = defaultdict(list)

        # Group interventions by type and collect effectiveness ratings
        for intervention in intervention_history:
            effectiveness_scores[intervention.intervention_type].append(intervention.effectiveness_rating / 10.0)

        # Calculate average effectiveness for each intervention type
        avg_effectiveness = {}
        for intervention_type, scores in effectiveness_scores.items():
            avg_effectiveness[intervention_type] = statistics.mean(scores) if scores else 0.0

        return avg_effectiveness

    def recommend_intervention_adjustments(self, current_interventions: list[InterventionType],
                                         effectiveness_scores: dict[InterventionType, float],
                                         progress_analysis: ProgressAnalysisResult) -> list[dict[str, Any]]:
        """Recommend adjustments to current interventions."""
        recommendations = []

        for intervention in current_interventions:
            effectiveness = effectiveness_scores.get(intervention, 0.5)

            if effectiveness < 0.4:
                recommendations.append({
                    "intervention": intervention,
                    "action": "discontinue",
                    "reason": "Low effectiveness score",
                    "alternative": self._suggest_alternative_intervention(intervention, progress_analysis)
                })
            elif effectiveness > 0.8:
                recommendations.append({
                    "intervention": intervention,
                    "action": "intensify",
                    "reason": "High effectiveness - increase frequency or depth",
                    "suggestion": "Consider advanced techniques within this intervention type"
                })
            elif 0.4 <= effectiveness <= 0.6:
                recommendations.append({
                    "intervention": intervention,
                    "action": "modify",
                    "reason": "Moderate effectiveness - adjust approach",
                    "suggestion": "Try different techniques within this intervention type"
                })

        return recommendations

    def _suggest_alternative_intervention(self, current_intervention: InterventionType,
                                        progress_analysis: ProgressAnalysisResult) -> InterventionType:
        """Suggest an alternative intervention."""
        # Find the metric type most associated with the current intervention
        for _metric_type, interventions in self.intervention_effectiveness_map.items():
            if current_intervention in interventions:
                # Suggest the next intervention in the list
                current_index = interventions.index(current_intervention)
                if current_index < len(interventions) - 1:
                    return interventions[current_index + 1]
                else:
                    # If at the end, suggest from a different metric type
                    break

        # Default alternative based on overall progress
        if progress_analysis.overall_progress_score < 0.5:
            return InterventionType.COPING_SKILLS  # Safe, foundational choice
        else:
            return InterventionType.COGNITIVE_RESTRUCTURING  # More advanced choice


class ContentDifficultyAdapter:
    """Adapts content difficulty based on user progress."""

    def __init__(self):
        """Initialize the content difficulty adapter."""
        self.difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
        self.adaptation_rules = self._initialize_adaptation_rules()
        logger.info("ContentDifficultyAdapter initialized")

    def _initialize_adaptation_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize rules for difficulty adaptation."""
        return {
            "accelerate": {
                "progress_threshold": 0.8,
                "improvement_threshold": 0.3,
                "action": "increase_difficulty",
                "adjustment": 1  # Move up one level
            },
            "consolidate": {
                "progress_threshold": 0.6,
                "improvement_threshold": 0.1,
                "action": "maintain_difficulty",
                "adjustment": 0
            },
            "remediate": {
                "progress_threshold": 0.4,
                "improvement_threshold": -0.1,
                "action": "decrease_difficulty",
                "adjustment": -1  # Move down one level
            },
            "simplify": {
                "progress_threshold": 0.2,
                "improvement_threshold": -0.2,
                "action": "significant_decrease",
                "adjustment": -2  # Move down two levels
            }
        }

    def adapt_content_difficulty(self, current_difficulty: str, progress_analysis: ProgressAnalysisResult,
                               user_characteristics: dict[str, Any]) -> dict[str, Any]:
        """Adapt content difficulty based on progress and user characteristics."""
        try:
            # Determine current difficulty index
            current_index = self.difficulty_levels.index(current_difficulty) if current_difficulty in self.difficulty_levels else 1

            # Analyze progress to determine adaptation strategy
            overall_progress = progress_analysis.overall_progress_score

            # Calculate average improvement rate across metrics
            improvement_rates = [
                analysis.get("improvement_rate", 0.0)
                for analysis in progress_analysis.metric_trends.values()
            ]
            avg_improvement = statistics.mean(improvement_rates) if improvement_rates else 0.0

            # Determine adaptation rule
            adaptation_rule = self._select_adaptation_rule(overall_progress, avg_improvement)
            rule_config = self.adaptation_rules[adaptation_rule]

            # Calculate new difficulty level
            adjustment = rule_config["adjustment"]

            # Consider user characteristics for fine-tuning
            learning_velocity = user_characteristics.get("learning_style", {}).get("fast_paced", 0.5)
            if learning_velocity > 0.7:
                adjustment += 0.5  # Slight increase for fast learners
            elif learning_velocity < 0.3:
                adjustment -= 0.5  # Slight decrease for slow learners

            # Apply adjustment
            new_index = max(0, min(len(self.difficulty_levels) - 1, current_index + int(adjustment)))
            new_difficulty = self.difficulty_levels[new_index]

            # Generate adaptation details
            adaptation_details = {
                "previous_difficulty": current_difficulty,
                "new_difficulty": new_difficulty,
                "adaptation_strategy": adaptation_rule,
                "rationale": self._generate_adaptation_rationale(adaptation_rule, overall_progress, avg_improvement),
                "confidence": self._calculate_adaptation_confidence(progress_analysis, user_characteristics),
                "expected_impact": rule_config["action"],
                "adjustment_magnitude": abs(new_index - current_index),
                "recommendations": self._generate_difficulty_recommendations(new_difficulty, adaptation_rule)
            }

            return adaptation_details

        except Exception as e:
            logger.error(f"Error adapting content difficulty: {e}")
            return {
                "previous_difficulty": current_difficulty,
                "new_difficulty": current_difficulty,
                "adaptation_strategy": "maintain",
                "rationale": "Error in adaptation - maintaining current level",
                "confidence": 0.0
            }

    def _select_adaptation_rule(self, overall_progress: float, avg_improvement: float) -> str:
        """Select the appropriate adaptation rule."""
        if overall_progress >= 0.8 and avg_improvement >= 0.3:
            return "accelerate"
        elif overall_progress >= 0.6 and avg_improvement >= 0.1:
            return "consolidate"
        elif overall_progress >= 0.4 or avg_improvement >= -0.1:
            return "remediate"
        else:
            return "simplify"

    def _generate_adaptation_rationale(self, adaptation_rule: str, overall_progress: float,
                                     avg_improvement: float) -> str:
        """Generate rationale for the adaptation decision."""
        rationales = {
            "accelerate": f"High progress ({overall_progress:.1%}) and strong improvement ({avg_improvement:.1%}) indicate readiness for increased challenge",
            "consolidate": f"Good progress ({overall_progress:.1%}) with steady improvement ({avg_improvement:.1%}) suggests maintaining current level",
            "remediate": f"Moderate progress ({overall_progress:.1%}) with limited improvement ({avg_improvement:.1%}) requires reinforcement",
            "simplify": f"Low progress ({overall_progress:.1%}) with declining performance ({avg_improvement:.1%}) needs simplified approach"
        }

        return rationales.get(adaptation_rule, "Adaptation based on progress analysis")

    def _calculate_adaptation_confidence(self, progress_analysis: ProgressAnalysisResult,
                                       user_characteristics: dict[str, Any]) -> float:
        """Calculate confidence in the adaptation decision."""
        # Base confidence on analysis confidence and data completeness
        base_confidence = progress_analysis.confidence_level

        # Adjust based on data richness
        metric_count = len(progress_analysis.metric_trends)
        data_richness = min(1.0, metric_count / 5.0)  # Assume 5 metrics is ideal

        # Adjust based on user characteristics completeness
        char_completeness = len(user_characteristics) / 8.0  # Assume 8 characteristics

        confidence = base_confidence * 0.6 + data_richness * 0.2 + char_completeness * 0.2
        return max(0.3, min(1.0, confidence))

    def _generate_difficulty_recommendations(self, new_difficulty: str, adaptation_rule: str) -> list[str]:
        """Generate recommendations for the new difficulty level."""
        recommendations = []

        if adaptation_rule == "accelerate":
            recommendations.extend([
                f"Introduce {new_difficulty}-level concepts gradually",
                "Provide additional challenges and complex scenarios",
                "Encourage independent problem-solving"
            ])
        elif adaptation_rule == "consolidate":
            recommendations.extend([
                f"Continue with {new_difficulty}-level content",
                "Focus on deepening understanding of current concepts",
                "Provide varied practice opportunities"
            ])
        elif adaptation_rule == "remediate":
            recommendations.extend([
                f"Review foundational concepts at {new_difficulty} level",
                "Provide additional support and scaffolding",
                "Break complex tasks into smaller steps"
            ])
        elif adaptation_rule == "simplify":
            recommendations.extend([
                f"Use {new_difficulty}-level explanations and examples",
                "Increase repetition and practice time",
                "Provide more guidance and support"
            ])

        return recommendations


class TherapeuticJourneyPlanner:
    """Plans and manages long-term therapeutic journeys."""

    def __init__(self):
        """Initialize the therapeutic journey planner."""
        self.phase_progression_rules = self._initialize_phase_progression()
        self.milestone_templates = self._initialize_milestone_templates()
        logger.info("TherapeuticJourneyPlanner initialized")

    def _initialize_phase_progression(self) -> dict[TherapeuticPhase, dict[str, Any]]:
        """Initialize rules for phase progression."""
        return {
            TherapeuticPhase.ASSESSMENT: {
                "duration_weeks": 2,
                "completion_criteria": ["baseline_established", "goals_identified", "readiness_assessed"],
                "next_phase": TherapeuticPhase.FOUNDATION_BUILDING,
                "key_metrics": [ProgressMetricType.ENGAGEMENT_LEVEL]
            },
            TherapeuticPhase.FOUNDATION_BUILDING: {
                "duration_weeks": 4,
                "completion_criteria": ["basic_skills_learned", "therapeutic_alliance_established", "routine_developed"],
                "next_phase": TherapeuticPhase.SKILL_DEVELOPMENT,
                "key_metrics": [ProgressMetricType.COPING_SKILLS_USAGE, ProgressMetricType.ENGAGEMENT_LEVEL]
            },
            TherapeuticPhase.SKILL_DEVELOPMENT: {
                "duration_weeks": 6,
                "completion_criteria": ["core_skills_mastered", "progress_demonstrated", "confidence_built"],
                "next_phase": TherapeuticPhase.INTEGRATION,
                "key_metrics": [ProgressMetricType.EMOTIONAL_REGULATION, ProgressMetricType.GOAL_ACHIEVEMENT]
            },
            TherapeuticPhase.INTEGRATION: {
                "duration_weeks": 4,
                "completion_criteria": ["skills_integrated", "real_world_application", "independence_developed"],
                "next_phase": TherapeuticPhase.MAINTENANCE,
                "key_metrics": [ProgressMetricType.GOAL_ACHIEVEMENT, ProgressMetricType.RESILIENCE_BUILDING]
            },
            TherapeuticPhase.MAINTENANCE: {
                "duration_weeks": 8,
                "completion_criteria": ["stability_maintained", "relapse_prevention", "ongoing_growth"],
                "next_phase": TherapeuticPhase.ADVANCED_WORK,
                "key_metrics": [ProgressMetricType.RESILIENCE_BUILDING, ProgressMetricType.SELF_AWARENESS]
            },
            TherapeuticPhase.ADVANCED_WORK: {
                "duration_weeks": 12,
                "completion_criteria": ["advanced_insights", "complex_challenges_addressed", "mastery_achieved"],
                "next_phase": None,  # Terminal phase
                "key_metrics": [ProgressMetricType.SELF_AWARENESS, ProgressMetricType.RELATIONSHIP_QUALITY]
            }
        }

    def _initialize_milestone_templates(self) -> dict[TherapeuticPhase, list[dict[str, Any]]]:
        """Initialize milestone templates for each phase."""
        return {
            TherapeuticPhase.ASSESSMENT: [
                {"name": "Complete initial assessment", "week": 1, "type": "evaluation"},
                {"name": "Establish therapeutic goals", "week": 2, "type": "planning"}
            ],
            TherapeuticPhase.FOUNDATION_BUILDING: [
                {"name": "Learn basic coping skills", "week": 2, "type": "skill_acquisition"},
                {"name": "Establish session routine", "week": 3, "type": "habit_formation"},
                {"name": "Build therapeutic rapport", "week": 4, "type": "relationship"}
            ],
            TherapeuticPhase.SKILL_DEVELOPMENT: [
                {"name": "Master emotional regulation techniques", "week": 3, "type": "skill_mastery"},
                {"name": "Apply skills in challenging situations", "week": 5, "type": "application"},
                {"name": "Demonstrate consistent progress", "week": 6, "type": "validation"}
            ],
            TherapeuticPhase.INTEGRATION: [
                {"name": "Integrate skills into daily life", "week": 2, "type": "integration"},
                {"name": "Handle real-world challenges", "week": 3, "type": "application"},
                {"name": "Develop independence", "week": 4, "type": "autonomy"}
            ],
            TherapeuticPhase.MAINTENANCE: [
                {"name": "Maintain therapeutic gains", "week": 4, "type": "maintenance"},
                {"name": "Prevent relapse", "week": 6, "type": "prevention"},
                {"name": "Continue growth", "week": 8, "type": "development"}
            ],
            TherapeuticPhase.ADVANCED_WORK: [
                {"name": "Explore complex themes", "week": 4, "type": "exploration"},
                {"name": "Address advanced challenges", "week": 8, "type": "mastery"},
                {"name": "Achieve therapeutic mastery", "week": 12, "type": "completion"}
            ]
        }

    def create_therapeutic_journey_plan(self, user_id: str, initial_assessment: dict[str, Any],
                                      therapeutic_goals: list[TherapeuticGoal]) -> TherapeuticJourneyPlan:
        """Create a comprehensive therapeutic journey plan."""
        try:
            # Determine starting phase based on assessment
            starting_phase = self._determine_starting_phase(initial_assessment)

            # Plan phases and milestones
            planned_phases = self._plan_therapeutic_phases(starting_phase, therapeutic_goals)
            milestones = self._generate_milestones(planned_phases)

            # Calculate estimated duration
            total_duration = sum(phase["duration_weeks"] for phase in planned_phases)

            # Generate progress checkpoints
            checkpoints = self._generate_progress_checkpoints(total_duration)

            # Define success criteria
            success_criteria = self._define_success_criteria(therapeutic_goals, planned_phases)

            journey_plan = TherapeuticJourneyPlan(
                user_id=user_id,
                current_phase=starting_phase,
                planned_phases=planned_phases,
                milestones=milestones,
                estimated_duration=total_duration,
                progress_checkpoints=checkpoints,
                success_criteria=success_criteria
            )

            journey_plan.validate()
            logger.info(f"Created therapeutic journey plan for user {user_id}")
            return journey_plan

        except Exception as e:
            logger.error(f"Error creating therapeutic journey plan for user {user_id}: {e}")
            # Return minimal plan as fallback
            return TherapeuticJourneyPlan(
                user_id=user_id,
                current_phase=TherapeuticPhase.ASSESSMENT,
                estimated_duration=12
            )

    def _determine_starting_phase(self, initial_assessment: dict[str, Any]) -> TherapeuticPhase:
        """Determine the appropriate starting phase based on assessment."""
        readiness_score = initial_assessment.get("therapeutic_readiness", 0.0)
        prior_experience = initial_assessment.get("prior_therapy_experience", False)
        current_functioning = initial_assessment.get("current_functioning_level", 0.5)

        if readiness_score > 0.8 and prior_experience and current_functioning > 0.7:
            return TherapeuticPhase.SKILL_DEVELOPMENT
        elif readiness_score > 0.6 and current_functioning > 0.5:
            return TherapeuticPhase.FOUNDATION_BUILDING
        else:
            return TherapeuticPhase.ASSESSMENT

    def _plan_therapeutic_phases(self, starting_phase: TherapeuticPhase,
                               therapeutic_goals: list[TherapeuticGoal]) -> list[dict[str, Any]]:
        """Plan the sequence of therapeutic phases."""
        planned_phases = []
        current_phase = starting_phase

        while current_phase is not None:
            phase_config = self.phase_progression_rules[current_phase]

            # Customize phase based on goals
            customized_phase = {
                "phase": current_phase,
                "duration_weeks": phase_config["duration_weeks"],
                "completion_criteria": phase_config["completion_criteria"].copy(),
                "key_metrics": phase_config["key_metrics"].copy(),
                "relevant_goals": self._match_goals_to_phase(therapeutic_goals, current_phase)
            }

            # Adjust duration based on goal complexity
            goal_complexity = len(customized_phase["relevant_goals"])
            if goal_complexity > 3:
                customized_phase["duration_weeks"] += 2

            planned_phases.append(customized_phase)
            current_phase = phase_config["next_phase"]

        return planned_phases

    def _match_goals_to_phase(self, therapeutic_goals: list[TherapeuticGoal],
                            phase: TherapeuticPhase) -> list[str]:
        """Match therapeutic goals to appropriate phases."""
        # This is a simplified implementation
        # In practice, you'd have more sophisticated goal-to-phase mapping
        phase_keywords = {
            TherapeuticPhase.ASSESSMENT: ["assess", "evaluate", "baseline"],
            TherapeuticPhase.FOUNDATION_BUILDING: ["basic", "foundation", "establish"],
            TherapeuticPhase.SKILL_DEVELOPMENT: ["skill", "learn", "develop", "practice"],
            TherapeuticPhase.INTEGRATION: ["integrate", "apply", "real-world"],
            TherapeuticPhase.MAINTENANCE: ["maintain", "prevent", "sustain"],
            TherapeuticPhase.ADVANCED_WORK: ["advanced", "complex", "mastery"]
        }

        relevant_goals = []
        keywords = phase_keywords.get(phase, [])

        for goal in therapeutic_goals:
            goal_text = (goal.title + " " + goal.description).lower()
            if any(keyword in goal_text for keyword in keywords):
                relevant_goals.append(goal.title)

        return relevant_goals

    def _generate_milestones(self, planned_phases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate milestones for the therapeutic journey."""
        milestones = []
        current_week = 0

        for phase_plan in planned_phases:
            phase = phase_plan["phase"]
            phase_milestones = self.milestone_templates.get(phase, [])

            for milestone_template in phase_milestones:
                milestone = {
                    "name": milestone_template["name"],
                    "phase": phase,
                    "target_week": current_week + milestone_template["week"],
                    "type": milestone_template["type"],
                    "status": "planned",
                    "completion_criteria": phase_plan["completion_criteria"]
                }
                milestones.append(milestone)

            current_week += phase_plan["duration_weeks"]

        return milestones

    def _generate_progress_checkpoints(self, total_duration: int) -> list[datetime]:
        """Generate progress checkpoint dates."""
        checkpoints = []
        current_date = datetime.now()

        # Generate checkpoints every 2 weeks
        for week in range(2, total_duration + 1, 2):
            checkpoint_date = current_date + timedelta(weeks=week)
            checkpoints.append(checkpoint_date)

        return checkpoints

    def _define_success_criteria(self, therapeutic_goals: list[TherapeuticGoal],
                               planned_phases: list[dict[str, Any]]) -> list[str]:
        """Define overall success criteria for the journey."""
        criteria = []

        # Goal-based criteria
        for goal in therapeutic_goals:
            criteria.append(f"Achieve {goal.title} with 80% progress")

        # Phase-based criteria
        for phase_plan in planned_phases:
            phase_name = phase_plan["phase"].value.replace("_", " ").title()
            criteria.append(f"Successfully complete {phase_name} phase")

        # General criteria
        criteria.extend([
            "Demonstrate sustained improvement in key metrics",
            "Maintain therapeutic gains for at least 4 weeks",
            "Show increased self-efficacy and independence"
        ])

        return criteria

    def update_journey_progress(self, journey_plan: TherapeuticJourneyPlan,
                              progress_analysis: ProgressAnalysisResult) -> dict[str, Any]:
        """Update journey progress based on current analysis."""
        try:
            current_phase = journey_plan.current_phase
            phase_config = self.phase_progression_rules[current_phase]

            # Check if current phase completion criteria are met
            phase_completion = self._assess_phase_completion(
                current_phase, progress_analysis, journey_plan
            )

            update_result = {
                "current_phase": current_phase.value,
                "phase_completion_percentage": phase_completion["completion_percentage"],
                "criteria_met": phase_completion["criteria_met"],
                "ready_for_next_phase": phase_completion["ready_for_next_phase"],
                "recommendations": []
            }

            # Generate recommendations based on progress
            if phase_completion["ready_for_next_phase"]:
                next_phase = phase_config["next_phase"]
                if next_phase:
                    update_result["recommendations"].append(
                        f"Ready to progress to {next_phase.value.replace('_', ' ').title()} phase"
                    )
                    journey_plan.current_phase = next_phase
                else:
                    update_result["recommendations"].append("Therapeutic journey completed successfully")

            elif phase_completion["completion_percentage"] < 0.5:
                update_result["recommendations"].append(
                    f"Focus on completing {current_phase.value.replace('_', ' ')} phase requirements"
                )

            # Update journey plan
            journey_plan.last_updated = datetime.now()

            return update_result

        except Exception as e:
            logger.error(f"Error updating journey progress: {e}")
            return {"error": str(e)}

    def _assess_phase_completion(self, phase: TherapeuticPhase, progress_analysis: ProgressAnalysisResult,
                               journey_plan: TherapeuticJourneyPlan) -> dict[str, Any]:
        """Assess completion of current therapeutic phase."""
        phase_config = self.phase_progression_rules[phase]
        key_metrics = phase_config["key_metrics"]
        completion_criteria = phase_config["completion_criteria"]

        # Assess key metrics performance
        metrics_performance = []
        for metric_type in key_metrics:
            if metric_type in progress_analysis.metric_trends:
                current_value = progress_analysis.metric_trends[metric_type].get("current_value", 0.0)
                metrics_performance.append(current_value)

        avg_metrics_performance = statistics.mean(metrics_performance) if metrics_performance else 0.0

        # Simple completion assessment (in practice, this would be more sophisticated)
        completion_percentage = min(100.0, avg_metrics_performance * 100)
        criteria_met = len([c for c in completion_criteria if completion_percentage > 70])
        ready_for_next_phase = completion_percentage > 75 and criteria_met >= len(completion_criteria) * 0.8

        return {
            "completion_percentage": completion_percentage,
            "criteria_met": criteria_met,
            "total_criteria": len(completion_criteria),
            "ready_for_next_phase": ready_for_next_phase,
            "metrics_performance": avg_metrics_performance
        }


class AdaptiveTherapyOrchestrator:
    """Orchestrates adaptive therapy decisions based on progress."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the adaptive therapy orchestrator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.intervention_selector = ProgressBasedInterventionSelector()
        self.difficulty_adapter = ContentDifficultyAdapter()
        self.journey_planner = TherapeuticJourneyPlanner()

        # Decision history for learning and improvement
        self.adaptation_history: dict[str, list[AdaptationDecision]] = defaultdict(list)

        logger.info("AdaptiveTherapyOrchestrator initialized")

    def make_adaptation_decision(self, user_id: str, progress_analysis: ProgressAnalysisResult,
                               current_session: SessionState, personalization_profile: PersonalizationProfile,
                               journey_plan: TherapeuticJourneyPlan | None = None) -> AdaptationDecision:
        """Make a comprehensive adaptation decision."""
        try:
            # Analyze current situation
            situation_analysis = self._analyze_current_situation(
                progress_analysis, current_session, personalization_profile
            )

            # Determine adaptation strategy
            adaptation_strategy = self._determine_adaptation_strategy(situation_analysis)

            # Generate implementation steps
            implementation_steps = self._generate_implementation_steps(
                adaptation_strategy, situation_analysis, journey_plan
            )

            # Define success metrics
            success_metrics = self._define_success_metrics(adaptation_strategy, progress_analysis)

            # Create adaptation decision
            decision = AdaptationDecision(
                user_id=user_id,
                adaptation_strategy=adaptation_strategy,
                rationale=self._generate_adaptation_rationale(adaptation_strategy, situation_analysis),
                confidence_level=self._calculate_decision_confidence(situation_analysis),
                expected_outcomes=self._predict_outcomes(adaptation_strategy, situation_analysis),
                implementation_steps=implementation_steps,
                success_metrics=success_metrics
            )

            decision.validate()

            # Store decision in history
            self.adaptation_history[user_id].append(decision)

            logger.info(f"Made adaptation decision for user {user_id}: {adaptation_strategy.value}")
            return decision

        except Exception as e:
            logger.error(f"Error making adaptation decision for user {user_id}: {e}")
            # Return safe default decision
            return AdaptationDecision(
                user_id=user_id,
                adaptation_strategy=AdaptationStrategy.MAINTAIN,
                rationale="Error in decision making - maintaining current approach",
                confidence_level=0.0
            )

    def _analyze_current_situation(self, progress_analysis: ProgressAnalysisResult,
                                 current_session: SessionState,
                                 personalization_profile: PersonalizationProfile) -> dict[str, Any]:
        """Analyze the current therapeutic situation."""
        situation = {
            "overall_progress": progress_analysis.overall_progress_score,
            "progress_trend": self._calculate_progress_trend(progress_analysis),
            "engagement_level": self._assess_engagement_level(current_session),
            "learning_velocity": personalization_profile.learning_velocity,
            "session_consistency": self._assess_session_consistency(personalization_profile),
            "goal_achievement_rate": self._calculate_goal_achievement_rate(progress_analysis),
            "intervention_effectiveness": self._assess_intervention_effectiveness(progress_analysis),
            "emotional_stability": self._assess_emotional_stability(current_session),
            "time_in_therapy": self._calculate_time_in_therapy(current_session)
        }

        return situation

    def _determine_adaptation_strategy(self, situation_analysis: dict[str, Any]) -> AdaptationStrategy:
        """Determine the most appropriate adaptation strategy."""
        overall_progress = situation_analysis["overall_progress"]
        progress_trend = situation_analysis["progress_trend"]
        learning_velocity = situation_analysis["learning_velocity"]
        engagement_level = situation_analysis["engagement_level"]

        # High performance and positive trend
        if overall_progress > 0.8 and progress_trend > 0.2 and learning_velocity > 0.7:
            return AdaptationStrategy.ACCELERATE

        # Good performance but stagnating
        elif overall_progress > 0.6 and abs(progress_trend) < 0.1:
            return AdaptationStrategy.DIVERSIFY

        # Declining performance
        elif progress_trend < -0.1:
            if overall_progress > 0.5:
                return AdaptationStrategy.REMEDIATE
            else:
                return AdaptationStrategy.SIMPLIFY

        # Low engagement
        elif engagement_level < 0.4:
            return AdaptationStrategy.INTENSIFY

        # Steady progress
        elif 0.4 <= overall_progress <= 0.7 and progress_trend >= 0:
            return AdaptationStrategy.CONSOLIDATE

        # Default to maintain
        else:
            return AdaptationStrategy.MAINTAIN

    def _generate_implementation_steps(self, strategy: AdaptationStrategy,
                                     situation_analysis: dict[str, Any],
                                     journey_plan: TherapeuticJourneyPlan | None) -> list[str]:
        """Generate specific implementation steps for the adaptation strategy."""
        steps = []

        if strategy == AdaptationStrategy.ACCELERATE:
            steps.extend([
                "Increase content difficulty level",
                "Introduce advanced therapeutic techniques",
                "Reduce scaffolding and increase independence",
                "Set more challenging goals"
            ])

        elif strategy == AdaptationStrategy.CONSOLIDATE:
            steps.extend([
                "Maintain current difficulty level",
                "Focus on deepening understanding",
                "Provide varied practice opportunities",
                "Reinforce successful strategies"
            ])

        elif strategy == AdaptationStrategy.REMEDIATE:
            steps.extend([
                "Review foundational concepts",
                "Identify and address knowledge gaps",
                "Provide additional support and guidance",
                "Break complex tasks into smaller steps"
            ])

        elif strategy == AdaptationStrategy.DIVERSIFY:
            steps.extend([
                "Try alternative therapeutic approaches",
                "Introduce new intervention types",
                "Vary content presentation methods",
                "Explore different engagement strategies"
            ])

        elif strategy == AdaptationStrategy.INTENSIFY:
            steps.extend([
                "Increase session frequency",
                "Add more interactive elements",
                "Provide immediate feedback",
                "Enhance motivational components"
            ])

        elif strategy == AdaptationStrategy.SIMPLIFY:
            steps.extend([
                "Reduce content complexity",
                "Increase explanation detail",
                "Provide more examples and practice",
                "Slow down pacing"
            ])

        else:  # MAINTAIN
            steps.extend([
                "Continue current approach",
                "Monitor progress closely",
                "Make minor adjustments as needed",
                "Maintain consistent support level"
            ])

        return steps

    def _calculate_progress_trend(self, progress_analysis: ProgressAnalysisResult) -> float:
        """Calculate overall progress trend."""
        if not progress_analysis.metric_trends:
            return 0.0

        trend_slopes = [
            analysis.get("trend_slope", 0.0)
            for analysis in progress_analysis.metric_trends.values()
        ]

        return statistics.mean(trend_slopes) if trend_slopes else 0.0

    def _assess_engagement_level(self, current_session: SessionState) -> float:
        """Assess current engagement level."""
        # Simple engagement assessment based on session activity
        engagement_indicators = [
            min(1.0, current_session.narrative_position / 10.0),
            min(1.0, len(current_session.character_states) / 3.0),
            min(1.0, len(current_session.user_inventory) / 5.0)
        ]

        return statistics.mean(engagement_indicators)

    def _assess_session_consistency(self, personalization_profile: PersonalizationProfile) -> float:
        """Assess session consistency."""
        engagement_history = personalization_profile.engagement_patterns.get("engagement", [])

        if len(engagement_history) < 2:
            return 0.5  # Neutral consistency

        consistency = 1.0 - statistics.stdev(engagement_history)
        return max(0.0, min(1.0, consistency))

    def _calculate_goal_achievement_rate(self, progress_analysis: ProgressAnalysisResult) -> float:
        """Calculate goal achievement rate."""
        goal_metric = progress_analysis.metric_trends.get(ProgressMetricType.GOAL_ACHIEVEMENT)
        if goal_metric:
            return goal_metric.get("current_value", 0.0)
        return 0.0

    def _assess_intervention_effectiveness(self, progress_analysis: ProgressAnalysisResult) -> float:
        """Assess intervention effectiveness."""
        intervention_metric = progress_analysis.metric_trends.get(ProgressMetricType.INTERVENTION_EFFECTIVENESS)
        if intervention_metric:
            return intervention_metric.get("current_value", 0.0)
        return 0.0

    def _assess_emotional_stability(self, current_session: SessionState) -> float:
        """Assess emotional stability."""
        if current_session.emotional_state:
            # Higher stability for positive emotions with moderate intensity
            if current_session.emotional_state.primary_emotion in [
                EmotionalStateType.CALM, EmotionalStateType.HOPEFUL
            ]:
                return 1.0 - current_session.emotional_state.intensity * 0.5
            else:
                return 1.0 - current_session.emotional_state.intensity

        return 0.5  # Neutral stability

    def _calculate_time_in_therapy(self, current_session: SessionState) -> int:
        """Calculate time in therapy (days)."""
        return (datetime.now() - current_session.created_at).days

    def _generate_adaptation_rationale(self, strategy: AdaptationStrategy,
                                     situation_analysis: dict[str, Any]) -> str:
        """Generate rationale for the adaptation decision."""
        overall_progress = situation_analysis["overall_progress"]
        progress_trend = situation_analysis["progress_trend"]

        rationales = {
            AdaptationStrategy.ACCELERATE: f"High progress ({overall_progress:.1%}) with positive trend ({progress_trend:+.1%}) indicates readiness for acceleration",
            AdaptationStrategy.CONSOLIDATE: f"Steady progress ({overall_progress:.1%}) suggests consolidation of current gains",
            AdaptationStrategy.REMEDIATE: f"Progress challenges ({overall_progress:.1%}) with declining trend ({progress_trend:+.1%}) require remediation",
            AdaptationStrategy.DIVERSIFY: f"Stagnant progress ({progress_trend:+.1%}) despite adequate performance ({overall_progress:.1%}) suggests need for diversification",
            AdaptationStrategy.INTENSIFY: "Low engagement with current approach requires intensification",
            AdaptationStrategy.SIMPLIFY: f"Low progress ({overall_progress:.1%}) with negative trend ({progress_trend:+.1%}) requires simplification",
            AdaptationStrategy.MAINTAIN: "Current approach is working well - maintaining course"
        }

        return rationales.get(strategy, "Adaptation based on comprehensive situation analysis")

    def _calculate_decision_confidence(self, situation_analysis: dict[str, Any]) -> float:
        """Calculate confidence in the adaptation decision."""
        # Base confidence on data completeness and consistency
        data_completeness = len([v for v in situation_analysis.values() if v is not None]) / len(situation_analysis)

        # Higher confidence for clear patterns
        overall_progress = situation_analysis["overall_progress"]
        progress_trend = situation_analysis["progress_trend"]

        pattern_clarity = 0.5
        if overall_progress > 0.8 or overall_progress < 0.2:
            pattern_clarity += 0.2  # Clear high or low performance
        if abs(progress_trend) > 0.2:
            pattern_clarity += 0.2  # Clear trend direction

        confidence = data_completeness * 0.6 + pattern_clarity * 0.4
        return max(0.3, min(1.0, confidence))

    def _predict_outcomes(self, strategy: AdaptationStrategy,
                        situation_analysis: dict[str, Any]) -> list[str]:
        """Predict expected outcomes of the adaptation strategy."""
        outcomes = []

        if strategy == AdaptationStrategy.ACCELERATE:
            outcomes.extend([
                "Increased learning velocity",
                "Higher engagement with challenging content",
                "Accelerated skill development",
                "Enhanced self-efficacy"
            ])

        elif strategy == AdaptationStrategy.CONSOLIDATE:
            outcomes.extend([
                "Strengthened foundational skills",
                "Improved retention of learned concepts",
                "Increased confidence in current abilities",
                "Stable progress maintenance"
            ])

        elif strategy == AdaptationStrategy.REMEDIATE:
            outcomes.extend([
                "Improved understanding of core concepts",
                "Reduced knowledge gaps",
                "Increased success rate in activities",
                "Restored confidence and motivation"
            ])

        elif strategy == AdaptationStrategy.DIVERSIFY:
            outcomes.extend([
                "Renewed engagement and interest",
                "Discovery of more effective approaches",
                "Breakthrough in stagnant areas",
                "Expanded therapeutic toolkit"
            ])

        elif strategy == AdaptationStrategy.INTENSIFY:
            outcomes.extend([
                "Increased engagement and participation",
                "More frequent therapeutic interactions",
                "Accelerated progress through increased exposure",
                "Enhanced therapeutic alliance"
            ])

        elif strategy == AdaptationStrategy.SIMPLIFY:
            outcomes.extend([
                "Reduced cognitive load and overwhelm",
                "Increased success and positive experiences",
                "Rebuilt confidence and motivation",
                "Clearer understanding of concepts"
            ])

        else:  # MAINTAIN
            outcomes.extend([
                "Continued steady progress",
                "Maintained engagement levels",
                "Consistent therapeutic gains",
                "Stable therapeutic relationship"
            ])

        return outcomes

    def _define_success_metrics(self, strategy: AdaptationStrategy,
                              progress_analysis: ProgressAnalysisResult) -> list[str]:
        """Define success metrics for the adaptation strategy."""
        metrics = []

        # Common metrics for all strategies
        metrics.extend([
            "Overall progress score improvement",
            "Engagement level maintenance or increase",
            "Goal achievement progress"
        ])

        # Strategy-specific metrics
        if strategy == AdaptationStrategy.ACCELERATE:
            metrics.extend([
                "Successful completion of advanced content",
                "Increased learning velocity metrics",
                "Higher difficulty tolerance"
            ])

        elif strategy == AdaptationStrategy.CONSOLIDATE:
            metrics.extend([
                "Skill retention over time",
                "Consistent performance across sessions",
                "Depth of understanding measures"
            ])

        elif strategy == AdaptationStrategy.REMEDIATE:
            metrics.extend([
                "Improvement in foundational skill areas",
                "Reduced error rates",
                "Increased confidence scores"
            ])

        return metrics


class ProgressBasedTherapeuticAdaptation:
    """Main integration system for progress-based therapeutic adaptation."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the progress-based therapeutic adaptation system."""
        self.llm_client = llm_client or TherapeuticLLMClient()

        # Initialize component systems
        self.progress_tracker = ProgressTrackingPersonalization(llm_client)
        self.personalization_engine = PersonalizationEngine(llm_client)
        self.therapeutic_integration = TherapeuticContentIntegration()
        self.adaptive_orchestrator = AdaptiveTherapyOrchestrator(llm_client)

        # Storage for integration data
        self.user_journey_plans: dict[str, TherapeuticJourneyPlan] = {}
        self.adaptation_decisions: dict[str, list[AdaptationDecision]] = defaultdict(list)

        logger.info("ProgressBasedTherapeuticAdaptation system initialized")

    def integrate_progress_with_therapy(self, user_id: str, session_state: SessionState,
                                      personalization_profile: PersonalizationProfile) -> dict[str, Any]:
        """Main integration method that connects progress tracking with therapeutic content delivery."""
        try:
            # Track current progress
            progress_result = self.progress_tracker.track_therapeutic_progress(user_id, session_state)

            # Analyze user progress
            progress_analysis = self.progress_tracker._analyze_user_progress(user_id)

            # Get or create journey plan
            journey_plan = self.user_journey_plans.get(user_id)
            if not journey_plan:
                journey_plan = self._create_initial_journey_plan(user_id, session_state, progress_analysis)
                self.user_journey_plans[user_id] = journey_plan

            # Make adaptation decision
            adaptation_decision = self.adaptive_orchestrator.make_adaptation_decision(
                user_id, progress_analysis, session_state, personalization_profile, journey_plan
            )

            # Apply adaptations to therapeutic content
            adapted_content = self._apply_therapeutic_adaptations(
                user_id, session_state, adaptation_decision, progress_analysis, personalization_profile
            )

            # Update journey plan
            journey_update = self.adaptive_orchestrator.journey_planner.update_journey_progress(
                journey_plan, progress_analysis
            )

            # Generate next steps recommendations
            next_steps = self.progress_tracker.recommend_next_steps(user_id, progress_analysis)

            # Create integration result
            integration_result = {
                "progress_tracking": {
                    "metrics_recorded": progress_result.get("metrics_recorded", 0),
                    "overall_progress_score": progress_analysis.overall_progress_score,
                    "next_focus": progress_analysis.next_therapeutic_focus
                },
                "adaptation_decision": {
                    "strategy": adaptation_decision.adaptation_strategy.value,
                    "rationale": adaptation_decision.rationale,
                    "confidence": adaptation_decision.confidence_level,
                    "implementation_steps": adaptation_decision.implementation_steps
                },
                "therapeutic_content": adapted_content,
                "journey_progress": {
                    "current_phase": journey_plan.current_phase.value,
                    "completion_percentage": journey_update.get("phase_completion_percentage", 0),
                    "ready_for_next_phase": journey_update.get("ready_for_next_phase", False)
                },
                "recommendations": next_steps,
                "integration_metadata": {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "adaptation_id": adaptation_decision.decision_id
                }
            }

            # Store adaptation decision
            self.adaptation_decisions[user_id].append(adaptation_decision)

            logger.info(f"Successfully integrated progress with therapy for user {user_id}")
            return integration_result

        except Exception as e:
            logger.error(f"Error integrating progress with therapy for user {user_id}: {e}")
            return {
                "error": str(e),
                "fallback_content": self._generate_fallback_content(session_state),
                "integration_metadata": {"error": str(e)}
            }

    def _create_initial_journey_plan(self, user_id: str, session_state: SessionState,
                                   progress_analysis: ProgressAnalysisResult) -> TherapeuticJourneyPlan:
        """Create initial therapeutic journey plan."""
        # Create initial assessment based on session state
        initial_assessment = {
            "therapeutic_readiness": 0.6,  # Default moderate readiness
            "prior_therapy_experience": False,
            "current_functioning_level": progress_analysis.overall_progress_score
        }

        # Extract therapeutic goals from session
        therapeutic_goals = []
        if session_state.therapeutic_progress:
            therapeutic_goals = session_state.therapeutic_progress.therapeutic_goals

        return self.adaptive_orchestrator.journey_planner.create_therapeutic_journey_plan(
            user_id, initial_assessment, therapeutic_goals
        )

    def _apply_therapeutic_adaptations(self, user_id: str, session_state: SessionState,
                                     adaptation_decision: AdaptationDecision,
                                     progress_analysis: ProgressAnalysisResult,
                                     personalization_profile: PersonalizationProfile) -> dict[str, Any]:
        """Apply therapeutic adaptations based on the adaptation decision."""
        try:
            # Create base therapeutic content
            base_content = {
                "title": "Adaptive Therapeutic Session",
                "description": "Personalized therapeutic content based on your progress",
                "difficulty": "medium",
                "interventions": [],
                "content_elements": []
            }

            # Apply strategy-specific adaptations
            strategy = adaptation_decision.adaptation_strategy

            if strategy == AdaptationStrategy.ACCELERATE:
                base_content["difficulty"] = "advanced"
                base_content["content_elements"].append("challenging_scenarios")
                base_content["interventions"].extend([
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.BEHAVIORAL_ACTIVATION
                ])

            elif strategy == AdaptationStrategy.SIMPLIFY:
                base_content["difficulty"] = "beginner"
                base_content["content_elements"].append("basic_concepts")
                base_content["interventions"].extend([
                    InterventionType.COPING_SKILLS,
                    InterventionType.MINDFULNESS
                ])

            elif strategy == AdaptationStrategy.DIVERSIFY:
                base_content["content_elements"].append("alternative_approaches")
                base_content["interventions"] = progress_analysis.recommended_interventions

            # Apply personalization
            personalized_content = self.personalization_engine.personalize_content(
                user_id, base_content, session_state, personalization_profile, progress_analysis
            )

            # Integrate therapeutic opportunities
            therapeutic_opportunities = self._identify_therapeutic_opportunities(
                session_state, progress_analysis, adaptation_decision
            )

            personalized_content["therapeutic_opportunities"] = therapeutic_opportunities
            personalized_content["adaptation_applied"] = {
                "strategy": strategy.value,
                "rationale": adaptation_decision.rationale,
                "implementation_steps": adaptation_decision.implementation_steps
            }

            return personalized_content

        except Exception as e:
            logger.error(f"Error applying therapeutic adaptations: {e}")
            return {"error": str(e), "fallback": True}

    def _identify_therapeutic_opportunities(self, session_state: SessionState,
                                          progress_analysis: ProgressAnalysisResult,
                                          adaptation_decision: AdaptationDecision) -> list[dict[str, Any]]:
        """Identify therapeutic opportunities based on current context."""
        opportunities = []

        # Opportunity based on adaptation strategy
        strategy = adaptation_decision.adaptation_strategy

        if strategy == AdaptationStrategy.REMEDIATE:
            opportunities.append({
                "type": "skill_reinforcement",
                "description": "Opportunity to reinforce foundational therapeutic skills",
                "priority": "high",
                "intervention_suggestions": [InterventionType.COPING_SKILLS.value]
            })

        elif strategy == AdaptationStrategy.ACCELERATE:
            opportunities.append({
                "type": "advanced_challenge",
                "description": "Opportunity to tackle more complex therapeutic challenges",
                "priority": "medium",
                "intervention_suggestions": [InterventionType.COGNITIVE_RESTRUCTURING.value]
            })

        # Opportunity based on progress gaps
        for area in progress_analysis.areas_for_improvement[:2]:
            opportunities.append({
                "type": "improvement_focus",
                "description": f"Opportunity to address {area.lower()}",
                "priority": "high",
                "focus_area": area
            })

        return opportunities

    def _generate_fallback_content(self, session_state: SessionState) -> dict[str, Any]:
        """Generate fallback content when integration fails."""
        return {
            "title": "Therapeutic Session",
            "description": "Continue your therapeutic journey with supportive content",
            "difficulty": "medium",
            "interventions": [InterventionType.COPING_SKILLS.value],
            "content_elements": ["supportive_dialogue", "basic_techniques"],
            "fallback": True
        }

    def get_adaptation_insights(self, user_id: str) -> dict[str, Any]:
        """Get insights about user's adaptation patterns and effectiveness."""
        try:
            adaptations = self.adaptation_decisions.get(user_id, [])
            journey_plan = self.user_journey_plans.get(user_id)

            if not adaptations:
                return {"message": "No adaptation data available"}

            # Analyze adaptation patterns
            strategy_counts = defaultdict(int)
            confidence_scores = []

            for adaptation in adaptations:
                strategy_counts[adaptation.adaptation_strategy.value] += 1
                confidence_scores.append(adaptation.confidence_level)

            most_common_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None
            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0

            insights = {
                "total_adaptations": len(adaptations),
                "most_common_strategy": most_common_strategy,
                "strategy_distribution": dict(strategy_counts),
                "average_confidence": avg_confidence,
                "adaptation_effectiveness": self._calculate_adaptation_effectiveness(user_id),
                "journey_progress": {
                    "current_phase": journey_plan.current_phase.value if journey_plan else "unknown",
                    "estimated_completion": journey_plan.estimated_duration if journey_plan else 0
                },
                "recent_adaptations": [
                    {
                        "strategy": a.adaptation_strategy.value,
                        "confidence": a.confidence_level,
                        "timestamp": a.created_at.isoformat()
                    }
                    for a in adaptations[-5:]  # Last 5 adaptations
                ]
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting adaptation insights for user {user_id}: {e}")
            return {"error": str(e)}

    def _calculate_adaptation_effectiveness(self, user_id: str) -> float:
        """Calculate the effectiveness of adaptations for a user."""
        # This would typically involve comparing progress before and after adaptations
        # For now, return a simplified calculation based on adaptation confidence
        adaptations = self.adaptation_decisions.get(user_id, [])

        if not adaptations:
            return 0.0

        recent_adaptations = adaptations[-5:]  # Last 5 adaptations
        avg_confidence = statistics.mean([a.confidence_level for a in recent_adaptations])

        # Simple effectiveness estimate based on confidence and frequency
        effectiveness = avg_confidence * 0.8 + min(1.0, len(adaptations) / 10.0) * 0.2
        return effectiveness


# Utility functions for testing and validation
def create_sample_adaptation_context(user_id: str) -> tuple[SessionState, PersonalizationProfile, ProgressAnalysisResult]:
    """Create sample context for testing adaptation system."""
    # Create sample session state
    session_state = SessionState(
        session_id=f"session_{user_id}",
        user_id=user_id,
        narrative_position=8
    )

    # Create sample personalization profile
    profile = PersonalizationProfile(
        user_id=user_id,
        learning_velocity=0.6,
        optimal_session_length=25
    )

    # Create sample progress analysis
    progress_analysis = ProgressAnalysisResult(
        user_id=user_id,
        overall_progress_score=0.65,
        areas_for_improvement=["emotional regulation", "goal achievement"]
    )

    return session_state, profile, progress_analysis


if __name__ == "__main__":
    # Test the progress-based therapeutic adaptation system
    logging.basicConfig(level=logging.INFO)

    # Create test instance
    adaptation_system = ProgressBasedTherapeuticAdaptation()

    # Create sample context
    test_user_id = "test_user_123"
    session_state, profile, progress_analysis = create_sample_adaptation_context(test_user_id)

    # Test integration
    integration_result = adaptation_system.integrate_progress_with_therapy(
        test_user_id, session_state, profile
    )

    print("Integration Result:")
    print(f"  Adaptation Strategy: {integration_result['adaptation_decision']['strategy']}")
    print(f"  Progress Score: {integration_result['progress_tracking']['overall_progress_score']:.2f}")
    print(f"  Current Phase: {integration_result['journey_progress']['current_phase']}")
    print(f"  Recommendations: {len(integration_result['recommendations'])}")

    # Test insights
    insights = adaptation_system.get_adaptation_insights(test_user_id)
    print("\nAdaptation Insights:")
    print(f"  Total Adaptations: {insights.get('total_adaptations', 0)}")
    print(f"  Most Common Strategy: {insights.get('most_common_strategy', 'None')}")
    print(f"  Effectiveness: {insights.get('adaptation_effectiveness', 0):.2f}")

    print("\nProgress-based therapeutic adaptation test completed successfully!")
