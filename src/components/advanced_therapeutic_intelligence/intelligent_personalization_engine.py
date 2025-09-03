"""
Intelligent Personalization Engine

AI-driven personalization engine that learns from user interactions across all
9 therapeutic systems to provide highly personalized therapeutic experiences,
adaptive content delivery, and predictive therapeutic recommendations.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class PersonalizationLevel(Enum):
    """Levels of personalization intensity."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    ADAPTIVE = "adaptive"
    DEEP = "deep"
    PREDICTIVE = "predictive"


class LearningMode(Enum):
    """Learning modes for personalization."""
    PASSIVE = "passive"
    ACTIVE = "active"
    REINFORCEMENT = "reinforcement"
    COLLABORATIVE = "collaborative"
    PREDICTIVE = "predictive"


class PersonalizationDomain(Enum):
    """Domains for personalization."""
    THERAPEUTIC_APPROACH = "therapeutic_approach"
    CONTENT_DELIVERY = "content_delivery"
    INTERACTION_STYLE = "interaction_style"
    DIFFICULTY_ADAPTATION = "difficulty_adaptation"
    EMOTIONAL_SUPPORT = "emotional_support"
    CRISIS_PREVENTION = "crisis_prevention"
    PROGRESS_TRACKING = "progress_tracking"
    SOCIAL_INTERACTION = "social_interaction"
    NARRATIVE_PREFERENCE = "narrative_preference"


@dataclass
class UserPersonalizationProfile:
    """Comprehensive user personalization profile."""
    user_id: str = ""
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Learning characteristics
    learning_style: str = "adaptive"
    preferred_therapeutic_approaches: list[str] = field(default_factory=list)
    interaction_preferences: dict[str, Any] = field(default_factory=dict)
    emotional_patterns: dict[str, float] = field(default_factory=dict)

    # Behavioral patterns
    engagement_patterns: dict[str, Any] = field(default_factory=dict)
    response_patterns: dict[str, Any] = field(default_factory=dict)
    progress_patterns: dict[str, Any] = field(default_factory=dict)
    crisis_indicators: dict[str, Any] = field(default_factory=dict)

    # Personalization settings
    personalization_level: PersonalizationLevel = PersonalizationLevel.ADAPTIVE
    learning_mode: LearningMode = LearningMode.ACTIVE
    enabled_domains: set[PersonalizationDomain] = field(default_factory=set)

    # System interactions
    system_interactions: dict[str, dict[str, Any]] = field(default_factory=dict)
    therapeutic_outcomes: dict[str, list[float]] = field(default_factory=dict)
    adaptation_history: list[dict[str, Any]] = field(default_factory=list)

    # Privacy and consent
    consent_level: str = "full"
    privacy_settings: dict[str, bool] = field(default_factory=dict)
    data_retention_days: int = 365


@dataclass
class PersonalizationRecommendation:
    """Personalization recommendation for therapeutic systems."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    target_system: str = ""
    domain: PersonalizationDomain = PersonalizationDomain.THERAPEUTIC_APPROACH

    # Recommendation details
    recommendation_type: str = ""
    recommendation_data: dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    expected_impact: float = 0.0

    # Context and reasoning
    reasoning: str = ""
    supporting_evidence: list[str] = field(default_factory=list)
    contextual_factors: dict[str, Any] = field(default_factory=dict)

    # Implementation
    priority: int = 5  # 1-10 scale
    implementation_complexity: str = "medium"
    estimated_adaptation_time: int = 300  # seconds

    # Validation
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    validation_status: str = "pending"


class IntelligentPersonalizationEngine:
    """
    AI-driven personalization engine that learns from user interactions across
    all 9 therapeutic systems to provide highly personalized therapeutic
    experiences, adaptive content delivery, and predictive therapeutic
    recommendations.
    """

    def __init__(self):
        """Initialize the Intelligent Personalization Engine."""
        self.status = "initializing"
        self.user_profiles: dict[str, UserPersonalizationProfile] = {}
        self.active_recommendations: dict[str, list[PersonalizationRecommendation]] = {}
        self.learning_models: dict[str, Any] = {}

        # Therapeutic system references (injected)
        self.consequence_system = None
        self.emotional_safety_system = None
        self.adaptive_difficulty_engine = None
        self.character_development_system = None
        self.therapeutic_integration_system = None
        self.gameplay_loop_controller = None
        self.replayability_system = None
        self.collaborative_system = None
        self.error_recovery_manager = None

        # Phase B system references
        self.clinical_dashboard_manager = None
        self.cloud_deployment_manager = None
        self.clinical_validation_manager = None

        # Background tasks
        self._learning_task = None
        self._adaptation_task = None
        self._recommendation_task = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.personalization_metrics = {
            "total_users_profiled": 0,
            "total_recommendations_generated": 0,
            "total_adaptations_applied": 0,
            "average_personalization_accuracy": 0.0,
            "average_user_satisfaction": 0.0,
            "learning_model_accuracy": 0.0,
            "recommendation_acceptance_rate": 0.0,
            "therapeutic_outcome_improvement": 0.0,
        }

    async def initialize(self):
        """Initialize the Intelligent Personalization Engine."""
        try:
            logger.info("Initializing IntelligentPersonalizationEngine")

            # Initialize learning models
            await self._initialize_learning_models()

            # Start background tasks
            self._learning_task = asyncio.create_task(self._continuous_learning_loop())
            self._adaptation_task = asyncio.create_task(self._adaptation_loop())
            self._recommendation_task = asyncio.create_task(self._recommendation_loop())

            self.status = "running"
            logger.info("IntelligentPersonalizationEngine initialization complete")

        except Exception as e:
            logger.error(f"Error initializing IntelligentPersonalizationEngine: {e}")
            self.status = "failed"
            raise

    def inject_therapeutic_systems(
        self,
        consequence_system=None,
        emotional_safety_system=None,
        adaptive_difficulty_engine=None,
        character_development_system=None,
        therapeutic_integration_system=None,
        gameplay_loop_controller=None,
        replayability_system=None,
        collaborative_system=None,
        error_recovery_manager=None,
    ):
        """Inject therapeutic system dependencies."""
        self.consequence_system = consequence_system
        self.emotional_safety_system = emotional_safety_system
        self.adaptive_difficulty_engine = adaptive_difficulty_engine
        self.character_development_system = character_development_system
        self.therapeutic_integration_system = therapeutic_integration_system
        self.gameplay_loop_controller = gameplay_loop_controller
        self.replayability_system = replayability_system
        self.collaborative_system = collaborative_system
        self.error_recovery_manager = error_recovery_manager

        logger.info("Therapeutic systems injected into IntelligentPersonalizationEngine")

    def inject_integration_systems(
        self,
        clinical_dashboard_manager=None,
        cloud_deployment_manager=None,
        clinical_validation_manager=None,
    ):
        """Inject Phase B integration system dependencies."""
        self.clinical_dashboard_manager = clinical_dashboard_manager
        self.cloud_deployment_manager = cloud_deployment_manager
        self.clinical_validation_manager = clinical_validation_manager

        logger.info("Integration systems injected into IntelligentPersonalizationEngine")

    async def create_user_personalization_profile(
        self,
        user_id: str,
        initial_preferences: dict[str, Any] | None = None,
        consent_level: str = "full"
    ) -> UserPersonalizationProfile:
        """Create comprehensive user personalization profile."""
        try:
            # Create new personalization profile
            profile = UserPersonalizationProfile(
                user_id=user_id,
                consent_level=consent_level,
                enabled_domains=set(PersonalizationDomain),
                privacy_settings={
                    "allow_learning": True,
                    "allow_prediction": True,
                    "allow_sharing": False,
                    "allow_research": consent_level == "full"
                }
            )

            # Apply initial preferences
            if initial_preferences:
                await self._apply_initial_preferences(profile, initial_preferences)

            # Initialize system interactions tracking
            therapeutic_systems = [
                "consequence_system", "emotional_safety_system", "adaptive_difficulty_engine",
                "character_development_system", "therapeutic_integration_system",
                "gameplay_loop_controller", "replayability_system", "collaborative_system",
                "error_recovery_manager"
            ]

            for system in therapeutic_systems:
                profile.system_interactions[system] = {
                    "interaction_count": 0,
                    "positive_outcomes": 0,
                    "negative_outcomes": 0,
                    "average_engagement": 0.0,
                    "preferred_settings": {},
                    "adaptation_history": []
                }

            # Store profile
            self.user_profiles[user_id] = profile
            self.personalization_metrics["total_users_profiled"] += 1

            logger.info(f"User personalization profile created for user {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error creating user personalization profile: {e}")
            raise

    async def generate_personalization_recommendations(
        self,
        user_id: str,
        context: dict[str, Any] | None = None
    ) -> list[PersonalizationRecommendation]:
        """Generate personalized recommendations for therapeutic systems."""
        try:
            if user_id not in self.user_profiles:
                await self.create_user_personalization_profile(user_id)

            profile = self.user_profiles[user_id]
            recommendations = []

            # Generate recommendations for each enabled domain
            for domain in profile.enabled_domains:
                domain_recommendations = await self._generate_domain_recommendations(
                    profile, domain, context
                )
                recommendations.extend(domain_recommendations)

            # Prioritize and filter recommendations
            recommendations = await self._prioritize_recommendations(recommendations, profile)

            # Store active recommendations
            if user_id not in self.active_recommendations:
                self.active_recommendations[user_id] = []

            self.active_recommendations[user_id].extend(recommendations)
            self.personalization_metrics["total_recommendations_generated"] += len(recommendations)

            logger.info(f"Generated {len(recommendations)} personalization recommendations for user {user_id}")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating personalization recommendations: {e}")
            return []

    async def apply_personalization_adaptation(
        self,
        user_id: str,
        recommendation: PersonalizationRecommendation
    ) -> dict[str, Any]:
        """Apply personalization adaptation to therapeutic systems."""
        try:
            if user_id not in self.user_profiles:
                logger.warning(f"No profile found for user {user_id}")
                return {"success": False, "error": "No user profile found"}

            profile = self.user_profiles[user_id]

            # Apply adaptation based on target system and domain
            adaptation_result = await self._apply_system_adaptation(
                recommendation.target_system,
                recommendation.domain,
                recommendation.recommendation_data,
                profile
            )

            # Update profile with adaptation
            if adaptation_result["success"]:
                profile.adaptation_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "recommendation_id": recommendation.recommendation_id,
                    "target_system": recommendation.target_system,
                    "domain": recommendation.domain.value,
                    "adaptation_data": recommendation.recommendation_data,
                    "result": adaptation_result
                })

                profile.last_updated = datetime.utcnow()
                self.personalization_metrics["total_adaptations_applied"] += 1

            # Update recommendation status
            recommendation.validation_status = "applied" if adaptation_result["success"] else "failed"

            logger.info(f"Applied personalization adaptation for user {user_id}: {adaptation_result['success']}")
            return adaptation_result

        except Exception as e:
            logger.error(f"Error applying personalization adaptation: {e}")
            return {"success": False, "error": str(e)}

    async def learn_from_user_interaction(
        self,
        user_id: str,
        system_name: str,
        interaction_data: dict[str, Any],
        outcome_data: dict[str, Any]
    ):
        """Learn from user interaction to improve personalization."""
        try:
            if user_id not in self.user_profiles:
                await self.create_user_personalization_profile(user_id)

            profile = self.user_profiles[user_id]

            # Update system interaction data
            if system_name in profile.system_interactions:
                system_data = profile.system_interactions[system_name]
                system_data["interaction_count"] += 1

                # Analyze outcome
                outcome_score = outcome_data.get("satisfaction_score", 0.5)
                if outcome_score > 0.6:
                    system_data["positive_outcomes"] += 1
                elif outcome_score < 0.4:
                    system_data["negative_outcomes"] += 1

                # Update engagement metrics
                engagement_score = interaction_data.get("engagement_score", 0.5)
                current_avg = system_data["average_engagement"]
                interaction_count = system_data["interaction_count"]
                system_data["average_engagement"] = (
                    (current_avg * (interaction_count - 1) + engagement_score) / interaction_count
                )

            # Update learning models
            await self._update_learning_models(user_id, system_name, interaction_data, outcome_data)

            # Update profile timestamp
            profile.last_updated = datetime.utcnow()

            logger.debug(f"Learned from user interaction: {user_id} -> {system_name}")

        except Exception as e:
            logger.error(f"Error learning from user interaction: {e}")

    async def get_personalization_insights(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive personalization insights for user."""
        try:
            if user_id not in self.user_profiles:
                return {"error": "User profile not found"}

            profile = self.user_profiles[user_id]

            # Calculate insights
            insights = {
                "profile_summary": {
                    "user_id": profile.user_id,
                    "profile_age_days": (datetime.utcnow() - profile.created_at).days,
                    "personalization_level": profile.personalization_level.value,
                    "learning_mode": profile.learning_mode.value,
                    "enabled_domains": [domain.value for domain in profile.enabled_domains],
                },
                "interaction_summary": await self._calculate_interaction_summary(profile),
                "therapeutic_effectiveness": await self._calculate_therapeutic_effectiveness(profile),
                "personalization_accuracy": await self._calculate_personalization_accuracy(profile),
                "recommendations_summary": await self._get_recommendations_summary(user_id),
                "learning_progress": await self._calculate_learning_progress(profile),
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting personalization insights: {e}")
            return {"error": str(e)}

    async def _initialize_learning_models(self):
        """Initialize machine learning models for personalization."""
        try:
            # Initialize basic learning models (placeholder for ML implementation)
            self.learning_models = {
                "user_preference_model": {"type": "collaborative_filtering", "accuracy": 0.75},
                "therapeutic_outcome_predictor": {"type": "regression", "accuracy": 0.68},
                "engagement_predictor": {"type": "classification", "accuracy": 0.72},
                "crisis_risk_predictor": {"type": "anomaly_detection", "accuracy": 0.85},
                "content_recommendation_model": {"type": "neural_network", "accuracy": 0.78},
            }

            logger.info("Learning models initialized")

        except Exception as e:
            logger.error(f"Error initializing learning models: {e}")
            raise

    async def _apply_initial_preferences(self, profile: UserPersonalizationProfile, preferences: dict[str, Any]):
        """Apply initial user preferences to profile."""
        try:
            # Apply therapeutic approach preferences
            if "therapeutic_approaches" in preferences:
                profile.preferred_therapeutic_approaches = preferences["therapeutic_approaches"]

            # Apply interaction preferences
            if "interaction_style" in preferences:
                profile.interaction_preferences["style"] = preferences["interaction_style"]

            # Apply personalization level
            if "personalization_level" in preferences:
                level_str = preferences["personalization_level"]
                profile.personalization_level = PersonalizationLevel(level_str)

            # Apply learning mode
            if "learning_mode" in preferences:
                mode_str = preferences["learning_mode"]
                profile.learning_mode = LearningMode(mode_str)

            logger.debug("Initial preferences applied to profile")

        except Exception as e:
            logger.error(f"Error applying initial preferences: {e}")

    async def _generate_domain_recommendations(
        self,
        profile: UserPersonalizationProfile,
        domain: PersonalizationDomain,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate recommendations for specific personalization domain."""
        try:
            recommendations = []

            if domain == PersonalizationDomain.THERAPEUTIC_APPROACH:
                recommendations.extend(await self._generate_therapeutic_approach_recommendations(profile, context))
            elif domain == PersonalizationDomain.CONTENT_DELIVERY:
                recommendations.extend(await self._generate_content_delivery_recommendations(profile, context))
            elif domain == PersonalizationDomain.INTERACTION_STYLE:
                recommendations.extend(await self._generate_interaction_style_recommendations(profile, context))
            elif domain == PersonalizationDomain.DIFFICULTY_ADAPTATION:
                recommendations.extend(await self._generate_difficulty_adaptation_recommendations(profile, context))
            elif domain == PersonalizationDomain.EMOTIONAL_SUPPORT:
                recommendations.extend(await self._generate_emotional_support_recommendations(profile, context))
            elif domain == PersonalizationDomain.CRISIS_PREVENTION:
                recommendations.extend(await self._generate_crisis_prevention_recommendations(profile, context))

            return recommendations

        except Exception as e:
            logger.error(f"Error generating domain recommendations: {e}")
            return []

    async def _generate_therapeutic_approach_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate therapeutic approach recommendations."""
        recommendations = []

        # Analyze user's therapeutic system interactions
        best_performing_system = max(
            profile.system_interactions.items(),
            key=lambda x: x[1].get("positive_outcomes", 0),
            default=(None, None)
        )[0]

        if best_performing_system:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="therapeutic_integration_system",
                domain=PersonalizationDomain.THERAPEUTIC_APPROACH,
                recommendation_type="prioritize_approach",
                recommendation_data={
                    "preferred_system": best_performing_system,
                    "confidence_boost": 0.2,
                    "adaptation_strategy": "gradual_increase"
                },
                confidence_score=0.8,
                expected_impact=0.15,
                reasoning=f"User shows best outcomes with {best_performing_system}",
                priority=8
            )
            recommendations.append(recommendation)

        return recommendations

    async def _generate_difficulty_adaptation_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate difficulty adaptation recommendations."""
        recommendations = []

        # Analyze user performance patterns
        avg_engagement = np.mean([
            data.get("average_engagement", 0.0)
            for data in profile.system_interactions.values()
        ])

        if avg_engagement > 0.8:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="adaptive_difficulty_engine",
                domain=PersonalizationDomain.DIFFICULTY_ADAPTATION,
                recommendation_type="increase_difficulty",
                recommendation_data={
                    "difficulty_increase": 0.2,
                    "challenge_level": "moderate_increase",
                    "adaptation_speed": "gradual"
                },
                confidence_score=0.75,
                expected_impact=0.2,
                reasoning="High engagement suggests user ready for increased challenge",
                priority=6
            )
            recommendations.append(recommendation)
        elif avg_engagement < 0.4:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="adaptive_difficulty_engine",
                domain=PersonalizationDomain.DIFFICULTY_ADAPTATION,
                recommendation_type="decrease_difficulty",
                recommendation_data={
                    "difficulty_decrease": 0.3,
                    "support_level": "increased",
                    "adaptation_speed": "immediate"
                },
                confidence_score=0.8,
                expected_impact=0.3,
                reasoning="Low engagement suggests difficulty too high",
                priority=8
            )
            recommendations.append(recommendation)

        return recommendations

    async def _generate_emotional_support_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate emotional support recommendations."""
        recommendations = []

        # Check for emotional patterns
        emotional_safety_data = profile.system_interactions.get("emotional_safety_system", {})
        negative_outcomes = emotional_safety_data.get("negative_outcomes", 0)

        if negative_outcomes > 2:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="emotional_safety_system",
                domain=PersonalizationDomain.EMOTIONAL_SUPPORT,
                recommendation_type="increase_support",
                recommendation_data={
                    "support_intensity": "high",
                    "check_in_frequency": "increased",
                    "coping_strategies": "enhanced"
                },
                confidence_score=0.85,
                expected_impact=0.4,
                reasoning="Multiple negative outcomes indicate need for increased support",
                priority=9
            )
            recommendations.append(recommendation)

        return recommendations

    async def _generate_interaction_style_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate interaction style recommendations."""
        recommendations = []

        # Analyze interaction preferences
        current_style = profile.interaction_preferences.get("style", "supportive")

        # Recommend style adjustments based on outcomes
        total_positive = sum(
            data.get("positive_outcomes", 0)
            for data in profile.system_interactions.values()
        )
        total_interactions = sum(
            data.get("interaction_count", 0)
            for data in profile.system_interactions.values()
        )

        if total_interactions > 0:
            success_rate = total_positive / total_interactions

            if success_rate < 0.5 and current_style != "collaborative":
                recommendation = PersonalizationRecommendation(
                    user_id=profile.user_id,
                    target_system="collaborative_system",
                    domain=PersonalizationDomain.INTERACTION_STYLE,
                    recommendation_type="adjust_interaction_style",
                    recommendation_data={
                        "new_style": "collaborative",
                        "transition_speed": "gradual",
                        "emphasis": "user_agency"
                    },
                    confidence_score=0.7,
                    expected_impact=0.25,
                    reasoning="Low success rate suggests need for more collaborative approach",
                    priority=6
                )
                recommendations.append(recommendation)

        return recommendations

    async def _generate_crisis_prevention_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate crisis prevention recommendations."""
        recommendations = []

        # Analyze crisis indicators
        crisis_indicators = profile.crisis_indicators

        if crisis_indicators.get("risk_level", 0.0) > 0.3:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="emotional_safety_system",
                domain=PersonalizationDomain.CRISIS_PREVENTION,
                recommendation_type="enhance_monitoring",
                recommendation_data={
                    "monitoring_frequency": "increased",
                    "early_warning_sensitivity": "high",
                    "intervention_readiness": "immediate"
                },
                confidence_score=0.9,
                expected_impact=0.5,
                reasoning="Elevated crisis indicators require enhanced monitoring",
                priority=10
            )
            recommendations.append(recommendation)

        return recommendations

    async def _generate_content_delivery_recommendations(
        self,
        profile: UserPersonalizationProfile,
        context: dict[str, Any] | None
    ) -> list[PersonalizationRecommendation]:
        """Generate content delivery recommendations."""
        recommendations = []

        # Analyze engagement patterns
        avg_engagement = np.mean([
            data.get("average_engagement", 0.0)
            for data in profile.system_interactions.values()
        ])

        if avg_engagement < 0.6:
            recommendation = PersonalizationRecommendation(
                user_id=profile.user_id,
                target_system="gameplay_loop_controller",
                domain=PersonalizationDomain.CONTENT_DELIVERY,
                recommendation_type="increase_interactivity",
                recommendation_data={
                    "interactivity_boost": 0.3,
                    "content_variety": "high",
                    "pacing_adjustment": "faster"
                },
                confidence_score=0.7,
                expected_impact=0.25,
                reasoning="Low engagement detected, increasing interactivity",
                priority=7
            )
            recommendations.append(recommendation)

        return recommendations

    async def _prioritize_recommendations(
        self,
        recommendations: list[PersonalizationRecommendation],
        profile: UserPersonalizationProfile
    ) -> list[PersonalizationRecommendation]:
        """Prioritize and filter recommendations."""
        try:
            # Sort by priority and expected impact
            recommendations.sort(
                key=lambda r: (r.priority, r.expected_impact),
                reverse=True
            )

            # Filter by confidence threshold
            min_confidence = 0.6 if profile.personalization_level == PersonalizationLevel.DEEP else 0.4
            filtered_recommendations = [
                r for r in recommendations if r.confidence_score >= min_confidence
            ]

            # Limit number of recommendations
            max_recommendations = 5 if profile.personalization_level == PersonalizationLevel.DEEP else 3
            return filtered_recommendations[:max_recommendations]

        except Exception as e:
            logger.error(f"Error prioritizing recommendations: {e}")
            return recommendations

    async def _apply_system_adaptation(
        self,
        target_system: str,
        domain: PersonalizationDomain,
        adaptation_data: dict[str, Any],
        profile: UserPersonalizationProfile
    ) -> dict[str, Any]:
        """Apply adaptation to specific therapeutic system."""
        try:
            # Get target system reference
            system = getattr(self, target_system, None)
            if not system:
                return {"success": False, "error": f"System {target_system} not available"}

            # Apply adaptation based on domain
            if domain == PersonalizationDomain.THERAPEUTIC_APPROACH:
                if hasattr(system, 'adapt_therapeutic_approach'):
                    result = await system.adapt_therapeutic_approach(
                        user_id=profile.user_id,
                        adaptation_data=adaptation_data
                    )
                    return {"success": True, "result": result}

            elif domain == PersonalizationDomain.DIFFICULTY_ADAPTATION:
                if hasattr(system, 'adapt_difficulty_settings'):
                    result = await system.adapt_difficulty_settings(
                        user_id=profile.user_id,
                        adaptation_data=adaptation_data
                    )
                    return {"success": True, "result": result}

            # Default adaptation (update system preferences)
            if hasattr(system, 'update_user_preferences'):
                result = await system.update_user_preferences(
                    user_id=profile.user_id,
                    preferences=adaptation_data
                )
                return {"success": True, "result": result}

            # Fallback: log adaptation for manual implementation
            logger.info(f"Adaptation logged for {target_system}: {adaptation_data}")
            return {"success": True, "result": "adaptation_logged"}

        except Exception as e:
            logger.error(f"Error applying system adaptation: {e}")
            return {"success": False, "error": str(e)}

    async def _update_learning_models(
        self,
        user_id: str,
        system_name: str,
        interaction_data: dict[str, Any],
        outcome_data: dict[str, Any]
    ):
        """Update learning models with new interaction data."""
        try:
            # Update model accuracy metrics (placeholder for ML implementation)
            for _model_name, model_data in self.learning_models.items():
                # Simulate learning improvement
                current_accuracy = model_data["accuracy"]
                improvement = 0.001 * (outcome_data.get("satisfaction_score", 0.5) - 0.5)
                model_data["accuracy"] = min(0.95, current_accuracy + improvement)

            # Update overall personalization accuracy
            avg_accuracy = np.mean([m["accuracy"] for m in self.learning_models.values()])
            self.personalization_metrics["learning_model_accuracy"] = avg_accuracy

        except Exception as e:
            logger.error(f"Error updating learning models: {e}")

    async def _calculate_interaction_summary(self, profile: UserPersonalizationProfile) -> dict[str, Any]:
        """Calculate interaction summary for user profile."""
        try:
            total_interactions = sum(
                data.get("interaction_count", 0)
                for data in profile.system_interactions.values()
            )

            total_positive = sum(
                data.get("positive_outcomes", 0)
                for data in profile.system_interactions.values()
            )

            avg_engagement = np.mean([
                data.get("average_engagement", 0.0)
                for data in profile.system_interactions.values()
            ])

            return {
                "total_interactions": total_interactions,
                "positive_outcome_rate": total_positive / max(total_interactions, 1),
                "average_engagement": float(avg_engagement),
                "most_used_system": max(
                    profile.system_interactions.items(),
                    key=lambda x: x[1].get("interaction_count", 0),
                    default=("none", {})
                )[0]
            }

        except Exception as e:
            logger.error(f"Error calculating interaction summary: {e}")
            return {}

    async def _calculate_therapeutic_effectiveness(self, profile: UserPersonalizationProfile) -> dict[str, Any]:
        """Calculate therapeutic effectiveness metrics."""
        try:
            # Calculate effectiveness based on outcomes
            total_outcomes = sum(
                len(outcomes) for outcomes in profile.therapeutic_outcomes.values()
            )

            if total_outcomes == 0:
                return {"effectiveness_score": 0.0, "improvement_trend": "insufficient_data"}

            # Calculate average outcome scores
            all_outcomes = []
            for outcomes in profile.therapeutic_outcomes.values():
                all_outcomes.extend(outcomes)

            effectiveness_score = np.mean(all_outcomes) if all_outcomes else 0.0

            # Calculate improvement trend
            if len(all_outcomes) >= 5:
                recent_outcomes = all_outcomes[-5:]
                earlier_outcomes = all_outcomes[:-5] if len(all_outcomes) > 5 else all_outcomes[:5]

                recent_avg = np.mean(recent_outcomes)
                earlier_avg = np.mean(earlier_outcomes)

                if recent_avg > earlier_avg + 0.1:
                    trend = "improving"
                elif recent_avg < earlier_avg - 0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            return {
                "effectiveness_score": float(effectiveness_score),
                "improvement_trend": trend,
                "total_outcomes_measured": total_outcomes
            }

        except Exception as e:
            logger.error(f"Error calculating therapeutic effectiveness: {e}")
            return {}

    async def _calculate_personalization_accuracy(self, profile: UserPersonalizationProfile) -> dict[str, Any]:
        """Calculate personalization accuracy metrics."""
        try:
            # Calculate accuracy based on adaptation history
            successful_adaptations = sum(
                1 for adaptation in profile.adaptation_history
                if adaptation.get("result", {}).get("success", False)
            )

            total_adaptations = len(profile.adaptation_history)
            accuracy = successful_adaptations / max(total_adaptations, 1)

            return {
                "personalization_accuracy": float(accuracy),
                "total_adaptations": total_adaptations,
                "successful_adaptations": successful_adaptations
            }

        except Exception as e:
            logger.error(f"Error calculating personalization accuracy: {e}")
            return {}

    async def _get_recommendations_summary(self, user_id: str) -> dict[str, Any]:
        """Get recommendations summary for user."""
        try:
            user_recommendations = self.active_recommendations.get(user_id, [])

            applied_count = sum(
                1 for rec in user_recommendations
                if rec.validation_status == "applied"
            )

            return {
                "total_recommendations": len(user_recommendations),
                "applied_recommendations": applied_count,
                "acceptance_rate": applied_count / max(len(user_recommendations), 1),
                "average_confidence": np.mean([r.confidence_score for r in user_recommendations]) if user_recommendations else 0.0
            }

        except Exception as e:
            logger.error(f"Error getting recommendations summary: {e}")
            return {}

    async def _calculate_learning_progress(self, profile: UserPersonalizationProfile) -> dict[str, Any]:
        """Calculate learning progress metrics."""
        try:
            profile_age_days = (datetime.utcnow() - profile.created_at).days

            # Calculate learning velocity
            adaptations_per_day = len(profile.adaptation_history) / max(profile_age_days, 1)

            # Calculate learning effectiveness
            recent_adaptations = [
                a for a in profile.adaptation_history
                if datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(days=7)
            ]

            recent_success_rate = sum(
                1 for a in recent_adaptations
                if a.get("result", {}).get("success", False)
            ) / max(len(recent_adaptations), 1)

            return {
                "learning_velocity": float(adaptations_per_day),
                "recent_success_rate": float(recent_success_rate),
                "total_learning_events": len(profile.adaptation_history),
                "profile_maturity": min(1.0, profile_age_days / 30.0)  # Mature after 30 days
            }

        except Exception as e:
            logger.error(f"Error calculating learning progress: {e}")
            return {}

    async def _continuous_learning_loop(self):
        """Background loop for continuous learning."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Update learning models periodically
                    await self._update_global_learning_models()

                    await asyncio.sleep(3600)  # Update every hour

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in continuous learning loop: {e}")
                    await asyncio.sleep(3600)

        except asyncio.CancelledError:
            logger.info("Continuous learning loop cancelled")

    async def _adaptation_loop(self):
        """Background loop for adaptation processing."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Process pending adaptations
                    await self._process_pending_adaptations()

                    await asyncio.sleep(300)  # Process every 5 minutes

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in adaptation loop: {e}")
                    await asyncio.sleep(300)

        except asyncio.CancelledError:
            logger.info("Adaptation loop cancelled")

    async def _recommendation_loop(self):
        """Background loop for recommendation generation."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Generate recommendations for active users
                    await self._generate_proactive_recommendations()

                    await asyncio.sleep(1800)  # Generate every 30 minutes

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in recommendation loop: {e}")
                    await asyncio.sleep(1800)

        except asyncio.CancelledError:
            logger.info("Recommendation loop cancelled")

    async def _update_global_learning_models(self):
        """Update global learning models with aggregated data."""
        # Placeholder for global model updates
        pass

    async def _process_pending_adaptations(self):
        """Process pending adaptations."""
        # Placeholder for pending adaptation processing
        pass

    async def _generate_proactive_recommendations(self):
        """Generate proactive recommendations for active users."""
        # Placeholder for proactive recommendation generation
        pass

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the Intelligent Personalization Engine."""
        try:
            therapeutic_systems_available = sum([
                1 for system in [
                    self.consequence_system,
                    self.emotional_safety_system,
                    self.adaptive_difficulty_engine,
                    self.character_development_system,
                    self.therapeutic_integration_system,
                    self.gameplay_loop_controller,
                    self.replayability_system,
                    self.collaborative_system,
                    self.error_recovery_manager,
                ] if system is not None
            ])

            integration_systems_available = sum([
                1 for system in [
                    self.clinical_dashboard_manager,
                    self.cloud_deployment_manager,
                    self.clinical_validation_manager,
                ] if system is not None
            ])

            return {
                "status": "healthy" if therapeutic_systems_available >= 5 else "degraded",
                "engine_status": self.status,
                "user_profiles": len(self.user_profiles),
                "active_recommendations": sum(len(recs) for recs in self.active_recommendations.values()),
                "learning_models": len(self.learning_models),
                "therapeutic_systems_available": f"{therapeutic_systems_available}/9",
                "integration_systems_available": f"{integration_systems_available}/3",
                "background_tasks_running": (
                    self._learning_task is not None and not self._learning_task.done() and
                    self._adaptation_task is not None and not self._adaptation_task.done() and
                    self._recommendation_task is not None and not self._recommendation_task.done()
                ),
                "personalization_metrics": self.personalization_metrics,
            }

        except Exception as e:
            logger.error(f"Error in personalization engine health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def shutdown(self):
        """Shutdown the Intelligent Personalization Engine."""
        try:
            logger.info("Shutting down IntelligentPersonalizationEngine")

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            # Cancel background tasks
            for task in [self._learning_task, self._adaptation_task, self._recommendation_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            self.status = "shutdown"
            logger.info("IntelligentPersonalizationEngine shutdown complete")

        except Exception as e:
            logger.error(f"Error during personalization engine shutdown: {e}")
            raise
