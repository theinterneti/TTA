"""
Enhanced Progress Tracking and Personalization System for TTA Prototype

This module provides enhanced progress tracking with clinical-grade analytics,
comprehensive personalization, and integration with worldbuilding systems.
It builds upon the existing progress tracking to meet clinical standards.

Classes:
    EnhancedProgressTrackingPersonalization: Clinical-grade progress tracking
    ClinicalProgressAnalyzer: Advanced therapeutic progress analysis
    PersonalizationEngineAdvanced: Enhanced content personalization
    TherapeuticGoalManager: Comprehensive goal management system
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
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))

try:
    from emotional_state_recognition import (
        EmotionalPattern,
        EmotionalStateRecognitionResponse,
    )
    from progress_tracking_personalization import (
        EmotionalGrowthTracker,
        GoalAchievementMonitor,
        PersonalizationProfile,
        ProgressMetric,
        ProgressMetricType,
        ProgressTrackingPersonalization,
        TherapeuticProgressAnalyzer,
    )
    from worldbuilding_setting_management import (
        LocationDetails,
        WorldbuildingSettingManagement,
    )
except ImportError as e:
    logging.warning(f"Could not import progress tracking components: {e}")
    # Create minimal mock classes for testing
    class ProgressTrackingPersonalization:
        def __init__(self): pass
    class WorldbuildingSettingManagement:
        def __init__(self): pass
    class EmotionalStateRecognitionResponse:
        def __init__(self): pass

logger = logging.getLogger(__name__)


class ClinicalProgressMetric(Enum):
    """Clinical-grade progress metrics for therapeutic assessment."""
    SYMPTOM_SEVERITY_REDUCTION = "symptom_severity_reduction"
    FUNCTIONAL_IMPROVEMENT = "functional_improvement"
    QUALITY_OF_LIFE_ENHANCEMENT = "quality_of_life_enhancement"
    THERAPEUTIC_ALLIANCE_STRENGTH = "therapeutic_alliance_strength"
    TREATMENT_ADHERENCE = "treatment_adherence"
    RELAPSE_PREVENTION_SKILLS = "relapse_prevention_skills"
    SOCIAL_FUNCTIONING = "social_functioning"
    OCCUPATIONAL_FUNCTIONING = "occupational_functioning"
    CRISIS_MANAGEMENT_SKILLS = "crisis_management_skills"
    INSIGHT_DEVELOPMENT = "insight_development"


class PersonalizationStrategy(Enum):
    """Advanced personalization strategies."""
    ADAPTIVE_DIFFICULTY = "adaptive_difficulty"
    LEARNING_STYLE_OPTIMIZATION = "learning_style_optimization"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    TRAUMA_INFORMED_ADAPTATION = "trauma_informed_adaptation"
    MOTIVATIONAL_ALIGNMENT = "motivational_alignment"
    COGNITIVE_LOAD_MANAGEMENT = "cognitive_load_management"
    EMOTIONAL_REGULATION_SUPPORT = "emotional_regulation_support"
    SOCIAL_PREFERENCE_ACCOMMODATION = "social_preference_accommodation"


@dataclass
class ClinicalProgressAssessment:
    """Comprehensive clinical progress assessment."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    assessment_period: tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now() - timedelta(days=30), datetime.now()))
    overall_clinical_improvement: float = 0.0  # -1.0 to 1.0
    symptom_severity_change: float = 0.0  # Negative = improvement
    functional_status_score: float = 0.0  # 0.0 to 1.0
    treatment_response_category: str = "partial_response"  # no_response, partial_response, good_response, excellent_response
    clinical_significance_achieved: bool = False
    reliable_change_index: float = 0.0
    therapeutic_milestones_achieved: list[str] = field(default_factory=list)
    areas_of_concern: list[str] = field(default_factory=list)
    clinical_recommendations: list[str] = field(default_factory=list)
    next_assessment_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    clinician_notes: str = ""
    assessment_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AdvancedPersonalizationProfile:
    """Advanced personalization profile with clinical considerations."""
    user_id: str
    learning_preferences: dict[str, float] = field(default_factory=dict)
    cognitive_processing_style: str = "balanced"  # visual, auditory, kinesthetic, balanced
    emotional_regulation_capacity: float = 0.5  # 0.0 to 1.0
    trauma_sensitivity_level: float = 0.0  # 0.0 to 1.0
    cultural_considerations: dict[str, Any] = field(default_factory=dict)
    motivational_drivers: list[str] = field(default_factory=list)
    optimal_challenge_level: float = 0.5  # 0.0 to 1.0
    social_interaction_preference: str = "moderate"  # minimal, moderate, high
    therapeutic_relationship_style: str = "collaborative"  # directive, collaborative, supportive
    content_sensitivity_flags: list[str] = field(default_factory=list)
    adaptation_history: list[dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class ClinicalProgressAnalyzer:
    """Advanced clinical progress analysis with evidence-based metrics."""

    def __init__(self):
        """Initialize the clinical progress analyzer."""
        self.clinical_cutoffs = self._initialize_clinical_cutoffs()
        self.reliable_change_indices = self._initialize_reliable_change_indices()
        self.therapeutic_milestones = self._initialize_therapeutic_milestones()
        logger.info("ClinicalProgressAnalyzer initialized")

    def _initialize_clinical_cutoffs(self) -> dict[str, dict[str, float]]:
        """Initialize clinical significance cutoffs."""
        return {
            "depression": {
                "mild": 0.3,
                "moderate": 0.5,
                "severe": 0.7,
                "clinical_significance": 0.5
            },
            "anxiety": {
                "mild": 0.25,
                "moderate": 0.45,
                "severe": 0.65,
                "clinical_significance": 0.45
            },
            "trauma": {
                "mild": 0.2,
                "moderate": 0.4,
                "severe": 0.6,
                "clinical_significance": 0.4
            }
        }

    def _initialize_reliable_change_indices(self) -> dict[str, float]:
        """Initialize reliable change index thresholds."""
        return {
            "depression": 1.96,  # Standard RCI threshold
            "anxiety": 1.96,
            "trauma": 2.58,  # Higher threshold for trauma measures
            "general_distress": 1.96
        }

    def _initialize_therapeutic_milestones(self) -> dict[str, list[str]]:
        """Initialize therapeutic milestone definitions."""
        return {
            "early_stage": [
                "therapeutic_alliance_established",
                "treatment_goals_identified",
                "baseline_assessment_completed",
                "safety_plan_developed"
            ],
            "middle_stage": [
                "symptom_reduction_initiated",
                "coping_skills_acquired",
                "insight_development_begun",
                "behavioral_changes_implemented"
            ],
            "late_stage": [
                "significant_symptom_improvement",
                "functional_improvement_achieved",
                "relapse_prevention_skills_developed",
                "treatment_goals_substantially_met"
            ]
        }

    async def conduct_clinical_progress_assessment(
        self,
        user_id: str,
        progress_metrics: list[ProgressMetric],
        clinical_context: dict[str, Any],
    ) -> ClinicalProgressAssessment:
        """
        Conduct comprehensive clinical progress assessment.

        Args:
            user_id: User identifier
            progress_metrics: List of progress metrics
            clinical_context: Clinical context and history

        Returns:
            ClinicalProgressAssessment: Comprehensive clinical assessment
        """
        try:
            assessment = ClinicalProgressAssessment(user_id=user_id)

            # Calculate overall clinical improvement
            assessment.overall_clinical_improvement = self._calculate_overall_improvement(
                progress_metrics, clinical_context
            )

            # Assess symptom severity change
            assessment.symptom_severity_change = self._assess_symptom_severity_change(
                progress_metrics, clinical_context
            )

            # Calculate functional status
            assessment.functional_status_score = self._calculate_functional_status(
                progress_metrics, clinical_context
            )

            # Determine treatment response category
            assessment.treatment_response_category = self._determine_treatment_response(
                assessment.overall_clinical_improvement,
                assessment.symptom_severity_change
            )

            # Check clinical significance
            assessment.clinical_significance_achieved = self._assess_clinical_significance(
                assessment.symptom_severity_change, clinical_context
            )

            # Calculate reliable change index
            assessment.reliable_change_index = self._calculate_reliable_change_index(
                progress_metrics, clinical_context
            )

            # Identify achieved milestones
            assessment.therapeutic_milestones_achieved = self._identify_achieved_milestones(
                progress_metrics, clinical_context
            )

            # Identify areas of concern
            assessment.areas_of_concern = self._identify_areas_of_concern(
                progress_metrics, clinical_context
            )

            # Generate clinical recommendations
            assessment.clinical_recommendations = self._generate_clinical_recommendations(
                assessment, clinical_context
            )

            logger.info(f"Clinical progress assessment completed for user {user_id}")
            return assessment

        except Exception as e:
            logger.error(f"Error conducting clinical progress assessment: {e}")
            # Return minimal assessment with error indication
            assessment = ClinicalProgressAssessment(user_id=user_id)
            assessment.areas_of_concern.append(f"Assessment error: {str(e)}")
            assessment.clinical_recommendations.append("Conduct manual clinical review")
            return assessment

    def _calculate_overall_improvement(
        self, metrics: list[ProgressMetric], context: dict[str, Any]
    ) -> float:
        """Calculate overall clinical improvement score."""
        if not metrics:
            return 0.0

        # Weight different metric types by clinical importance
        clinical_weights = {
            ProgressMetricType.EMOTIONAL_REGULATION: 0.25,
            ProgressMetricType.COPING_SKILLS_USAGE: 0.20,
            ProgressMetricType.GOAL_ACHIEVEMENT: 0.15,
            ProgressMetricType.INTERVENTION_EFFECTIVENESS: 0.15,
            ProgressMetricType.RESILIENCE_BUILDING: 0.10,
            ProgressMetricType.SELF_AWARENESS: 0.10,
            ProgressMetricType.RELATIONSHIP_QUALITY: 0.05
        }

        weighted_improvement = 0.0
        total_weight = 0.0

        # Group metrics by type and calculate improvement
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_type].append(metric)

        for metric_type, metric_list in metric_groups.items():
            if len(metric_list) < 2:
                continue

            # Calculate improvement trend
            values = [m.value for m in sorted(metric_list, key=lambda x: x.timestamp)]
            if len(values) >= 2:
                improvement = values[-1] - values[0]  # Latest - earliest
                weight = clinical_weights.get(metric_type, 0.05)
                weighted_improvement += improvement * weight
                total_weight += weight

        return weighted_improvement / total_weight if total_weight > 0 else 0.0

    def _assess_symptom_severity_change(self, metrics: list[ProgressMetric],
                                      context: dict[str, Any]) -> float:
        """Assess change in symptom severity (negative = improvement)."""
        # Look for symptom-related metrics
        symptom_metrics = [
            m for m in metrics
            if m.metric_type in [ProgressMetricType.EMOTIONAL_REGULATION,
                               ProgressMetricType.COPING_SKILLS_USAGE]
        ]

        if not symptom_metrics:
            return 0.0

        # Calculate severity change based on emotional regulation improvement
        regulation_metrics = [m for m in symptom_metrics if m.metric_type == ProgressMetricType.EMOTIONAL_REGULATION]
        if regulation_metrics:
            values = [m.value for m in sorted(regulation_metrics, key=lambda x: x.timestamp)]
            if len(values) >= 2:
                # Higher emotional regulation = lower symptom severity
                return -(values[-1] - values[0])  # Negative for improvement

        return 0.0

    def _calculate_functional_status(self, metrics: list[ProgressMetric],
                                   context: dict[str, Any]) -> float:
        """Calculate functional status score."""
        functional_metrics = [
            m for m in metrics
            if m.metric_type in [ProgressMetricType.GOAL_ACHIEVEMENT,
                               ProgressMetricType.RELATIONSHIP_QUALITY,
                               ProgressMetricType.ENGAGEMENT_LEVEL]
        ]

        if not functional_metrics:
            return 0.5  # Neutral functional status

        # Average recent functional metrics
        recent_values = [m.value for m in functional_metrics[-10:]]  # Last 10 measurements
        return statistics.mean(recent_values) if recent_values else 0.5

    def _determine_treatment_response(self, overall_improvement: float,
                                    symptom_change: float) -> str:
        """Determine treatment response category."""
        if overall_improvement >= 0.7 and symptom_change <= -0.5:
            return "excellent_response"
        elif overall_improvement >= 0.5 and symptom_change <= -0.3:
            return "good_response"
        elif overall_improvement >= 0.2 and symptom_change <= -0.1:
            return "partial_response"
        else:
            return "no_response"

    def _assess_clinical_significance(self, symptom_change: float,
                                    context: dict[str, Any]) -> bool:
        """Assess whether clinical significance has been achieved."""
        primary_condition = context.get("primary_diagnosis", "general_distress")
        cutoffs = self.clinical_cutoffs.get(primary_condition, self.clinical_cutoffs["general_distress"])

        # Clinical significance achieved if symptom reduction exceeds threshold
        return abs(symptom_change) >= cutoffs.get("clinical_significance", 0.5)

    def _calculate_reliable_change_index(self, metrics: list[ProgressMetric],
                                       context: dict[str, Any]) -> float:
        """Calculate reliable change index."""
        if len(metrics) < 2:
            return 0.0

        # Use emotional regulation as primary outcome measure
        regulation_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.EMOTIONAL_REGULATION]
        if len(regulation_metrics) < 2:
            return 0.0

        # Sort by timestamp
        regulation_metrics.sort(key=lambda x: x.timestamp)

        # Calculate change
        initial_score = regulation_metrics[0].value
        final_score = regulation_metrics[-1].value
        change = final_score - initial_score

        # Estimate standard error (simplified)
        values = [m.value for m in regulation_metrics]
        if len(values) > 2:
            std_error = statistics.stdev(values) / (len(values) ** 0.5)
        else:
            std_error = 0.1  # Default estimate

        # Calculate RCI
        if std_error > 0:
            return change / (std_error * (2 ** 0.5))
        else:
            return 0.0

    def _identify_achieved_milestones(self, metrics: list[ProgressMetric],
                                    context: dict[str, Any]) -> list[str]:
        """Identify therapeutic milestones that have been achieved."""
        achieved = []

        # Check early stage milestones
        if len(metrics) >= 5:  # Baseline assessment completed
            achieved.append("baseline_assessment_completed")

        # Check for therapeutic alliance (engagement metrics)
        engagement_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.ENGAGEMENT_LEVEL]
        if engagement_metrics and statistics.mean([m.value for m in engagement_metrics]) >= 0.7:
            achieved.append("therapeutic_alliance_established")

        # Check for symptom reduction
        regulation_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.EMOTIONAL_REGULATION]
        if len(regulation_metrics) >= 2:
            values = [m.value for m in sorted(regulation_metrics, key=lambda x: x.timestamp)]
            if values[-1] > values[0] + 0.2:  # 20% improvement
                achieved.append("symptom_reduction_initiated")

        # Check for coping skills acquisition
        coping_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.COPING_SKILLS_USAGE]
        if coping_metrics and statistics.mean([m.value for m in coping_metrics]) >= 0.6:
            achieved.append("coping_skills_acquired")

        return achieved

    def _identify_areas_of_concern(self, metrics: list[ProgressMetric],
                                 context: dict[str, Any]) -> list[str]:
        """Identify areas requiring clinical attention."""
        concerns = []

        # Check for declining trends
        for metric_type in ProgressMetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if len(type_metrics) >= 3:
                values = [m.value for m in sorted(type_metrics, key=lambda x: x.timestamp)]
                recent_trend = values[-1] - values[-3]  # Last vs. third-to-last
                if recent_trend < -0.2:  # Significant decline
                    concerns.append(f"Declining trend in {metric_type.value}")

        # Check for low engagement
        engagement_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.ENGAGEMENT_LEVEL]
        if engagement_metrics and statistics.mean([m.value for m in engagement_metrics]) < 0.4:
            concerns.append("Low therapeutic engagement")

        # Check for stagnation
        if len(metrics) >= 10:
            recent_metrics = metrics[-5:]
            older_metrics = metrics[-10:-5]

            recent_avg = statistics.mean([m.value for m in recent_metrics])
            older_avg = statistics.mean([m.value for m in older_metrics])

            if abs(recent_avg - older_avg) < 0.05:  # Less than 5% change
                concerns.append("Progress stagnation detected")

        return concerns

    def _generate_clinical_recommendations(self, assessment: ClinicalProgressAssessment,
                                         context: dict[str, Any]) -> list[str]:
        """Generate clinical recommendations based on assessment."""
        recommendations = []

        # Response-based recommendations
        if assessment.treatment_response_category == "no_response":
            recommendations.extend([
                "Consider treatment modification or intensification",
                "Evaluate for comorbid conditions",
                "Assess treatment adherence and barriers"
            ])
        elif assessment.treatment_response_category == "partial_response":
            recommendations.extend([
                "Continue current treatment with possible augmentation",
                "Monitor progress closely",
                "Consider additional therapeutic modalities"
            ])

        # Milestone-based recommendations
        if "therapeutic_alliance_established" not in assessment.therapeutic_milestones_achieved:
            recommendations.append("Focus on strengthening therapeutic alliance")

        if "coping_skills_acquired" not in assessment.therapeutic_milestones_achieved:
            recommendations.append("Emphasize coping skills development")

        # Concern-based recommendations
        for concern in assessment.areas_of_concern:
            if "declining" in concern.lower():
                recommendations.append("Investigate factors contributing to decline")
            elif "engagement" in concern.lower():
                recommendations.append("Address engagement barriers and motivation")
            elif "stagnation" in concern.lower():
                recommendations.append("Consider treatment approach modification")

        return recommendations


class PersonalizationEngineAdvanced:
    """Advanced personalization engine with clinical considerations."""

    def __init__(self):
        """Initialize the advanced personalization engine."""
        self.personalization_strategies = self._initialize_personalization_strategies()
        self.adaptation_algorithms = self._initialize_adaptation_algorithms()
        logger.info("PersonalizationEngineAdvanced initialized")

    def _initialize_personalization_strategies(self) -> dict[PersonalizationStrategy, dict[str, Any]]:
        """Initialize personalization strategies."""
        return {
            PersonalizationStrategy.ADAPTIVE_DIFFICULTY: {
                "parameters": ["user_skill_level", "recent_performance", "confidence_level"],
                "adjustment_range": (0.1, 1.0),
                "adaptation_rate": 0.1
            },
            PersonalizationStrategy.LEARNING_STYLE_OPTIMIZATION: {
                "parameters": ["visual_preference", "auditory_preference", "kinesthetic_preference"],
                "content_adaptations": ["visual_aids", "audio_descriptions", "interactive_elements"],
                "effectiveness_threshold": 0.7
            },
            PersonalizationStrategy.TRAUMA_INFORMED_ADAPTATION: {
                "parameters": ["trauma_sensitivity", "trigger_history", "safety_needs"],
                "safety_protocols": ["content_warnings", "pacing_control", "exit_strategies"],
                "monitoring_frequency": "continuous"
            }
        }

    def _initialize_adaptation_algorithms(self) -> dict[str, callable]:
        """Initialize adaptation algorithms."""
        return {
            "difficulty_adjustment": self._adjust_difficulty_level,
            "content_style_adaptation": self._adapt_content_style,
            "pacing_optimization": self._optimize_pacing,
            "cultural_adaptation": self._apply_cultural_adaptations
        }

    async def generate_personalized_content_plan(self, user_profile: AdvancedPersonalizationProfile,
                                               progress_assessment: ClinicalProgressAssessment,
                                               world_context: dict[str, Any]) -> dict[str, Any]:
        """
        Generate comprehensive personalized content plan.

        Args:
            user_profile: Advanced personalization profile
            progress_assessment: Clinical progress assessment
            world_context: Current world context

        Returns:
            Dict[str, Any]: Personalized content plan
        """
        try:
            content_plan = {
                "personalization_strategies": [],
                "content_adaptations": {},
                "difficulty_adjustments": {},
                "cultural_adaptations": {},
                "trauma_informed_modifications": {},
                "motivational_enhancements": {},
                "world_integration_preferences": {}
            }

            # Apply adaptive difficulty
            difficulty_plan = await self._plan_adaptive_difficulty(user_profile, progress_assessment)
            content_plan["difficulty_adjustments"] = difficulty_plan

            # Apply learning style optimization
            learning_plan = await self._plan_learning_style_optimization(user_profile)
            content_plan["content_adaptations"] = learning_plan

            # Apply trauma-informed adaptations
            trauma_plan = await self._plan_trauma_informed_adaptations(user_profile)
            content_plan["trauma_informed_modifications"] = trauma_plan

            # Apply cultural adaptations
            cultural_plan = await self._plan_cultural_adaptations(user_profile, world_context)
            content_plan["cultural_adaptations"] = cultural_plan

            # Apply motivational enhancements
            motivational_plan = await self._plan_motivational_enhancements(user_profile, progress_assessment)
            content_plan["motivational_enhancements"] = motivational_plan

            # Integrate with world context
            world_plan = await self._plan_world_integration(user_profile, world_context)
            content_plan["world_integration_preferences"] = world_plan

            logger.info(f"Personalized content plan generated for user {user_profile.user_id}")
            return content_plan

        except Exception as e:
            logger.error(f"Error generating personalized content plan: {e}")
            return {"error": str(e)}

    async def _plan_adaptive_difficulty(self, profile: AdvancedPersonalizationProfile,
                                      assessment: ClinicalProgressAssessment) -> dict[str, Any]:
        """Plan adaptive difficulty adjustments."""
        current_level = profile.optimal_challenge_level

        # Adjust based on progress
        if assessment.treatment_response_category == "excellent_response":
            target_level = min(1.0, current_level + 0.1)
        elif assessment.treatment_response_category == "no_response":
            target_level = max(0.1, current_level - 0.2)
        else:
            target_level = current_level

        return {
            "current_level": current_level,
            "target_level": target_level,
            "adjustment_rationale": f"Based on {assessment.treatment_response_category}",
            "implementation_strategy": "gradual_adjustment"
        }

    async def _plan_learning_style_optimization(self, profile: AdvancedPersonalizationProfile) -> dict[str, Any]:
        """Plan learning style optimizations."""
        style = profile.cognitive_processing_style

        adaptations = {
            "visual": {
                "content_modifications": ["add_visual_aids", "use_diagrams", "color_coding"],
                "presentation_style": "visual_emphasis",
                "interaction_methods": ["visual_feedback", "graphical_progress"]
            },
            "auditory": {
                "content_modifications": ["add_audio_descriptions", "verbal_explanations", "sound_cues"],
                "presentation_style": "auditory_emphasis",
                "interaction_methods": ["voice_feedback", "audio_progress"]
            },
            "kinesthetic": {
                "content_modifications": ["interactive_elements", "hands_on_activities", "movement_integration"],
                "presentation_style": "activity_based",
                "interaction_methods": ["tactile_feedback", "action_based_progress"]
            },
            "balanced": {
                "content_modifications": ["multimodal_approach", "varied_presentation", "flexible_options"],
                "presentation_style": "adaptive_mixed",
                "interaction_methods": ["multiple_feedback_types", "choice_based_interaction"]
            }
        }

        return adaptations.get(style, adaptations["balanced"])

    async def _plan_trauma_informed_adaptations(self, profile: AdvancedPersonalizationProfile) -> dict[str, Any]:
        """Plan trauma-informed adaptations."""
        sensitivity_level = profile.trauma_sensitivity_level

        if sensitivity_level < 0.3:
            return {"adaptations": "minimal", "monitoring": "standard"}
        elif sensitivity_level < 0.7:
            return {
                "adaptations": "moderate",
                "content_warnings": True,
                "pacing_control": "user_controlled",
                "exit_strategies": "always_available",
                "monitoring": "enhanced"
            }
        else:
            return {
                "adaptations": "extensive",
                "content_warnings": True,
                "pacing_control": "user_controlled",
                "exit_strategies": "always_available",
                "safety_checks": "frequent",
                "professional_oversight": "recommended",
                "monitoring": "continuous"
            }

    async def _plan_cultural_adaptations(self, profile: AdvancedPersonalizationProfile,
                                       world_context: dict[str, Any]) -> dict[str, Any]:
        """Plan cultural adaptations."""
        cultural_factors = profile.cultural_considerations

        adaptations = {}

        # Language and communication style
        if "communication_style" in cultural_factors:
            style = cultural_factors["communication_style"]
            adaptations["communication"] = {
                "direct": {"style": "straightforward", "feedback": "explicit"},
                "indirect": {"style": "contextual", "feedback": "subtle"},
                "high_context": {"style": "relationship_focused", "feedback": "implicit"}
            }.get(style, {"style": "adaptive", "feedback": "flexible"})

        # Family and social considerations
        if "family_involvement" in cultural_factors:
            involvement = cultural_factors["family_involvement"]
            adaptations["social_context"] = {
                "high": {"include_family_perspectives", "collective_decision_making"},
                "moderate": {"acknowledge_family_influence", "balanced_approach"},
                "low": {"individual_focus", "personal_autonomy_emphasis"}
            }.get(involvement, {"balanced_approach"})

        return adaptations

    async def _plan_motivational_enhancements(self, profile: AdvancedPersonalizationProfile,
                                            assessment: ClinicalProgressAssessment) -> dict[str, Any]:
        """Plan motivational enhancements."""
        drivers = profile.motivational_drivers

        enhancements = {}

        for driver in drivers:
            if driver == "achievement":
                enhancements["achievement"] = {
                    "progress_visualization": "detailed_metrics",
                    "goal_setting": "specific_measurable",
                    "feedback": "performance_focused"
                }
            elif driver == "connection":
                enhancements["connection"] = {
                    "social_elements": "peer_support_integration",
                    "relationship_focus": "therapeutic_alliance_emphasis",
                    "feedback": "relationship_based"
                }
            elif driver == "autonomy":
                enhancements["autonomy"] = {
                    "choice_provision": "maximum_user_control",
                    "self_direction": "user_led_exploration",
                    "feedback": "self_assessment_tools"
                }

        return enhancements

    async def _plan_world_integration(self, profile: AdvancedPersonalizationProfile,
                                    world_context: dict[str, Any]) -> dict[str, Any]:
        """Plan integration with world context."""
        return {
            "immersion_level": profile.social_interaction_preference,
            "character_interaction_style": profile.therapeutic_relationship_style,
            "world_complexity": "adaptive_to_cognitive_load",
            "narrative_pacing": "user_controlled",
            "therapeutic_integration": "seamless_embedding"
        }


class EnhancedProgressTrackingPersonalization:
    """
    Enhanced progress tracking and personalization with clinical-grade capabilities.

    This class builds upon the existing progress tracking to provide clinical-grade
    analytics, advanced personalization, and comprehensive therapeutic assessment.
    """

    def __init__(self, worldbuilding_manager: WorldbuildingSettingManagement | None = None,
                 emotion_recognizer: EmotionalStateRecognitionResponse | None = None):
        """Initialize enhanced progress tracking and personalization."""
        # Initialize base components
        self.base_tracker = ProgressTrackingPersonalization()
        self.clinical_analyzer = ClinicalProgressAnalyzer()
        self.personalization_engine = PersonalizationEngineAdvanced()

        # Initialize enhanced components
        self.worldbuilding_manager = worldbuilding_manager or WorldbuildingSettingManagement()
        self.emotion_recognizer = emotion_recognizer or EmotionalStateRecognitionResponse()

        # Storage for enhanced profiles and assessments
        self.advanced_profiles: dict[str, AdvancedPersonalizationProfile] = {}
        self.clinical_assessments: dict[str, list[ClinicalProgressAssessment]] = defaultdict(list)

        logger.info("EnhancedProgressTrackingPersonalization initialized with clinical capabilities")

    async def conduct_comprehensive_assessment(self, user_id: str,
                                             progress_metrics: list[ProgressMetric],
                                             clinical_context: dict[str, Any]) -> dict[str, Any]:
        """
        Conduct comprehensive clinical and personalization assessment.

        Args:
            user_id: User identifier
            progress_metrics: List of progress metrics
            clinical_context: Clinical context and history

        Returns:
            Dict[str, Any]: Comprehensive assessment results
        """
        try:
            # Conduct clinical progress assessment
            clinical_assessment = await self.clinical_analyzer.conduct_clinical_progress_assessment(
                user_id, progress_metrics, clinical_context
            )

            # Store assessment
            self.clinical_assessments[user_id].append(clinical_assessment)

            # Get or create advanced personalization profile
            if user_id not in self.advanced_profiles:
                self.advanced_profiles[user_id] = await self._create_advanced_profile(
                    user_id, progress_metrics, clinical_context
                )

            profile = self.advanced_profiles[user_id]

            # Update profile based on assessment
            await self._update_profile_from_assessment(profile, clinical_assessment)

            # Generate personalized content plan
            world_context = await self._get_world_context(user_id)
            content_plan = await self.personalization_engine.generate_personalized_content_plan(
                profile, clinical_assessment, world_context
            )

            return {
                "clinical_assessment": clinical_assessment,
                "personalization_profile": profile,
                "content_plan": content_plan,
                "recommendations": self._generate_comprehensive_recommendations(
                    clinical_assessment, profile, content_plan
                )
            }

        except Exception as e:
            logger.error(f"Error conducting comprehensive assessment: {e}")
            return {"error": str(e)}

    async def _create_advanced_profile(self, user_id: str, metrics: list[ProgressMetric],
                                     context: dict[str, Any]) -> AdvancedPersonalizationProfile:
        """Create advanced personalization profile."""
        profile = AdvancedPersonalizationProfile(user_id=user_id)

        # Infer learning preferences from metrics
        if metrics:
            engagement_metrics = [m for m in metrics if m.metric_type == ProgressMetricType.ENGAGEMENT_LEVEL]
            if engagement_metrics:
                avg_engagement = statistics.mean([m.value for m in engagement_metrics])
                profile.learning_preferences["engagement_level"] = avg_engagement

        # Set defaults based on context
        profile.cognitive_processing_style = context.get("learning_style", "balanced")
        profile.emotional_regulation_capacity = context.get("emotional_regulation", 0.5)
        profile.trauma_sensitivity_level = context.get("trauma_sensitivity", 0.0)
        profile.cultural_considerations = context.get("cultural_factors", {})
        profile.motivational_drivers = context.get("motivational_drivers", ["achievement", "connection"])

        return profile

    async def _update_profile_from_assessment(self, profile: AdvancedPersonalizationProfile,
                                            assessment: ClinicalProgressAssessment) -> None:
        """Update profile based on clinical assessment."""
        # Adjust optimal challenge level based on treatment response
        if assessment.treatment_response_category == "excellent_response":
            profile.optimal_challenge_level = min(1.0, profile.optimal_challenge_level + 0.1)
        elif assessment.treatment_response_category == "no_response":
            profile.optimal_challenge_level = max(0.1, profile.optimal_challenge_level - 0.1)

        # Update emotional regulation capacity
        if assessment.functional_status_score > 0.7:
            profile.emotional_regulation_capacity = min(1.0, profile.emotional_regulation_capacity + 0.1)

        # Record adaptation
        profile.adaptation_history.append({
            "timestamp": datetime.now(),
            "assessment_id": assessment.assessment_id,
            "adaptations_made": ["challenge_level", "emotional_regulation_capacity"],
            "rationale": f"Based on {assessment.treatment_response_category}"
        })

        profile.last_updated = datetime.now()

    async def _get_world_context(self, user_id: str) -> dict[str, Any]:
        """Get world context for user."""
        # This would integrate with the worldbuilding system
        return {
            "current_world": "therapeutic_adventure",
            "user_preferences": {},
            "world_state": {},
            "available_locations": []
        }

    def _generate_comprehensive_recommendations(self, assessment: ClinicalProgressAssessment,
                                              profile: AdvancedPersonalizationProfile,
                                              content_plan: dict[str, Any]) -> list[str]:
        """Generate comprehensive recommendations."""
        recommendations = []

        # Clinical recommendations
        recommendations.extend(assessment.clinical_recommendations)

        # Personalization recommendations
        if profile.trauma_sensitivity_level > 0.5:
            recommendations.append("Implement trauma-informed content adaptations")

        if profile.optimal_challenge_level < 0.3:
            recommendations.append("Gradually increase challenge level to build confidence")

        # Content plan recommendations
        if "error" in content_plan:
            recommendations.append("Review and adjust personalization parameters")

        return recommendations

    def get_clinical_summary(self, user_id: str, days: int = 30) -> dict[str, Any]:
        """Get clinical summary for user."""
        if user_id not in self.clinical_assessments:
            return {"error": "No clinical assessments found"}

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_assessments = [
            a for a in self.clinical_assessments[user_id]
            if a.assessment_timestamp >= cutoff_date
        ]

        if not recent_assessments:
            return {"error": "No recent assessments found"}

        latest_assessment = max(recent_assessments, key=lambda x: x.assessment_timestamp)

        return {
            "latest_assessment": latest_assessment,
            "assessment_count": len(recent_assessments),
            "progress_trend": self._calculate_progress_trend(recent_assessments),
            "clinical_status": latest_assessment.treatment_response_category,
            "areas_of_concern": latest_assessment.areas_of_concern,
            "recommendations": latest_assessment.clinical_recommendations
        }

    def _calculate_progress_trend(self, assessments: list[ClinicalProgressAssessment]) -> str:
        """Calculate overall progress trend."""
        if len(assessments) < 2:
            return "insufficient_data"

        improvements = [a.overall_clinical_improvement for a in assessments]

        if len(improvements) >= 2:
            recent_avg = statistics.mean(improvements[-2:])
            earlier_avg = statistics.mean(improvements[:-2]) if len(improvements) > 2 else improvements[0]

            if recent_avg > earlier_avg + 0.1:
                return "improving"
            elif recent_avg < earlier_avg - 0.1:
                return "declining"
            else:
                return "stable"

        return "stable"


# Export main classes
__all__ = [
    'EnhancedProgressTrackingPersonalization',
    'ClinicalProgressAnalyzer',
    'PersonalizationEngineAdvanced',
    'ClinicalProgressAssessment',
    'AdvancedPersonalizationProfile',
    'ClinicalProgressMetric',
    'PersonalizationStrategy'
]
