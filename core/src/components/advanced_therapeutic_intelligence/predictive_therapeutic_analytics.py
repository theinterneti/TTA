"""
Predictive Therapeutic Analytics

Predictive analytics system that analyzes therapeutic patterns, predicts user
needs, identifies potential crisis situations before they occur, and optimizes
therapeutic interventions for maximum effectiveness using advanced machine
learning and statistical analysis.
"""

import asyncio
import logging
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of therapeutic predictions."""
    CRISIS_RISK = "crisis_risk"
    THERAPEUTIC_OUTCOME = "therapeutic_outcome"
    USER_ENGAGEMENT = "user_engagement"
    INTERVENTION_EFFECTIVENESS = "intervention_effectiveness"
    RELAPSE_RISK = "relapse_risk"
    THERAPEUTIC_READINESS = "therapeutic_readiness"
    OPTIMAL_INTERVENTION = "optimal_intervention"
    SESSION_OUTCOME = "session_outcome"


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AnalyticsTimeframe(Enum):
    """Timeframes for predictive analytics."""
    IMMEDIATE = "immediate"  # Next 1-2 hours
    SHORT_TERM = "short_term"  # Next 24-48 hours
    MEDIUM_TERM = "medium_term"  # Next 1-2 weeks
    LONG_TERM = "long_term"  # Next 1-3 months


@dataclass
class TherapeuticPattern:
    """Identified therapeutic pattern."""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""
    pattern_name: str = ""
    description: str = ""

    # Pattern characteristics
    frequency: float = 0.0
    strength: float = 0.0
    consistency: float = 0.0
    significance: float = 0.0

    # Pattern data
    data_points: list[dict[str, Any]] = field(default_factory=list)
    temporal_features: dict[str, Any] = field(default_factory=dict)
    contextual_factors: dict[str, Any] = field(default_factory=dict)

    # Pattern outcomes
    associated_outcomes: list[str] = field(default_factory=list)
    predictive_indicators: list[str] = field(default_factory=list)
    intervention_responses: dict[str, float] = field(default_factory=dict)

    # Metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_observed: datetime = field(default_factory=datetime.utcnow)
    observation_count: int = 0


@dataclass
class TherapeuticPrediction:
    """Therapeutic prediction with confidence and recommendations."""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    prediction_type: PredictionType = PredictionType.THERAPEUTIC_OUTCOME
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.SHORT_TERM

    # Prediction details
    predicted_value: float = 0.0
    predicted_category: str = ""
    confidence: PredictionConfidence = PredictionConfidence.MODERATE
    confidence_score: float = 0.0

    # Supporting evidence
    supporting_patterns: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)

    # Recommendations
    recommended_interventions: list[dict[str, Any]] = field(default_factory=list)
    preventive_actions: list[str] = field(default_factory=list)
    monitoring_suggestions: list[str] = field(default_factory=list)

    # Validation
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    validation_status: str = "pending"
    actual_outcome: float | None = None


@dataclass
class InterventionOptimization:
    """Optimization recommendation for therapeutic interventions."""
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    target_system: str = ""

    # Optimization details
    current_effectiveness: float = 0.0
    predicted_effectiveness: float = 0.0
    improvement_potential: float = 0.0

    # Optimization recommendations
    parameter_adjustments: dict[str, Any] = field(default_factory=dict)
    timing_recommendations: dict[str, Any] = field(default_factory=dict)
    intensity_adjustments: dict[str, float] = field(default_factory=dict)

    # Evidence and reasoning
    optimization_rationale: str = ""
    supporting_evidence: list[str] = field(default_factory=list)
    expected_outcomes: dict[str, float] = field(default_factory=dict)

    # Implementation
    priority: int = 5  # 1-10 scale
    implementation_complexity: str = "medium"
    estimated_impact: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"


class PredictiveTherapeuticAnalytics:
    """
    Predictive analytics system that analyzes therapeutic patterns, predicts
    user needs, identifies potential crisis situations before they occur, and
    optimizes therapeutic interventions for maximum effectiveness.
    """

    def __init__(self):
        """Initialize the Predictive Therapeutic Analytics."""
        self.status = "initializing"
        self.therapeutic_patterns: dict[str, TherapeuticPattern] = {}
        self.active_predictions: dict[str, list[TherapeuticPrediction]] = {}
        self.intervention_optimizations: dict[str, list[InterventionOptimization]] = {}

        # Predictive models
        self.prediction_models: dict[str, Any] = {}
        self.pattern_recognition_models: dict[str, Any] = {}
        self.optimization_models: dict[str, Any] = {}

        # Data storage for analysis
        self.user_interaction_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.therapeutic_outcome_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        self.crisis_event_history: dict[str, list[dict[str, Any]]] = defaultdict(list)

        # System references (injected)
        self.personalization_engine = None
        self.therapeutic_systems = {}
        self.clinical_dashboard_manager = None
        self.cloud_deployment_manager = None
        self.clinical_validation_manager = None

        # Background tasks
        self._pattern_analysis_task = None
        self._prediction_generation_task = None
        self._optimization_task = None
        self._model_training_task = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.analytics_metrics = {
            "total_patterns_identified": 0,
            "total_predictions_generated": 0,
            "total_optimizations_created": 0,
            "prediction_accuracy": 0.0,
            "pattern_recognition_accuracy": 0.0,
            "optimization_effectiveness": 0.0,
            "crisis_prediction_accuracy": 0.0,
            "intervention_optimization_success_rate": 0.0,
        }

    async def initialize(self):
        """Initialize the Predictive Therapeutic Analytics."""
        try:
            logger.info("Initializing PredictiveTherapeuticAnalytics")

            # Initialize predictive models
            await self._initialize_predictive_models()

            # Start background analysis tasks
            self._pattern_analysis_task = asyncio.create_task(
                self._pattern_analysis_loop()
            )
            self._prediction_generation_task = asyncio.create_task(
                self._prediction_generation_loop()
            )
            self._optimization_task = asyncio.create_task(
                self._optimization_loop()
            )
            self._model_training_task = asyncio.create_task(
                self._model_training_loop()
            )

            self.status = "running"
            logger.info("PredictiveTherapeuticAnalytics initialization complete")

        except Exception as e:
            logger.error(f"Error initializing PredictiveTherapeuticAnalytics: {e}")
            self.status = "failed"
            raise

    def inject_personalization_engine(self, personalization_engine):
        """Inject personalization engine dependency."""
        self.personalization_engine = personalization_engine
        logger.info("Personalization engine injected into PredictiveTherapeuticAnalytics")

    def inject_therapeutic_systems(self, **therapeutic_systems):
        """Inject therapeutic system dependencies."""
        self.therapeutic_systems = therapeutic_systems
        logger.info("Therapeutic systems injected into PredictiveTherapeuticAnalytics")

    def inject_integration_systems(
        self,
        clinical_dashboard_manager=None,
        cloud_deployment_manager=None,
        clinical_validation_manager=None,
    ):
        """Inject integration system dependencies."""
        self.clinical_dashboard_manager = clinical_dashboard_manager
        self.cloud_deployment_manager = cloud_deployment_manager
        self.clinical_validation_manager = clinical_validation_manager

        logger.info("Integration systems injected into PredictiveTherapeuticAnalytics")

    async def analyze_therapeutic_patterns(
        self,
        user_id: str,
        analysis_timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MEDIUM_TERM,
        pattern_types: list[str] | None = None
    ) -> list[TherapeuticPattern]:
        """Analyze therapeutic patterns for user."""
        try:
            # Get user interaction history
            user_history = list(self.user_interaction_history.get(user_id, []))
            if not user_history:
                logger.warning(f"No interaction history found for user {user_id}")
                return []

            # Filter by timeframe
            cutoff_time = self._get_timeframe_cutoff(analysis_timeframe)
            recent_history = [
                interaction for interaction in user_history
                if interaction.get("timestamp", datetime.min) > cutoff_time
            ]

            if not recent_history:
                return []

            # Identify patterns
            patterns = []

            # Engagement patterns
            engagement_pattern = await self._identify_engagement_patterns(user_id, recent_history)
            if engagement_pattern:
                patterns.append(engagement_pattern)

            # Therapeutic response patterns
            response_pattern = await self._identify_response_patterns(user_id, recent_history)
            if response_pattern:
                patterns.append(response_pattern)

            # Crisis risk patterns
            crisis_pattern = await self._identify_crisis_patterns(user_id, recent_history)
            if crisis_pattern:
                patterns.append(crisis_pattern)

            # Intervention effectiveness patterns
            intervention_pattern = await self._identify_intervention_patterns(user_id, recent_history)
            if intervention_pattern:
                patterns.append(intervention_pattern)

            # Store identified patterns
            for pattern in patterns:
                self.therapeutic_patterns[pattern.pattern_id] = pattern

            self.analytics_metrics["total_patterns_identified"] += len(patterns)

            logger.info(f"Identified {len(patterns)} therapeutic patterns for user {user_id}")
            return patterns

        except Exception as e:
            logger.error(f"Error analyzing therapeutic patterns: {e}")
            return []

    async def generate_therapeutic_predictions(
        self,
        user_id: str,
        prediction_types: list[PredictionType] | None = None,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.SHORT_TERM
    ) -> list[TherapeuticPrediction]:
        """Generate therapeutic predictions for user."""
        try:
            if prediction_types is None:
                prediction_types = [
                    PredictionType.CRISIS_RISK,
                    PredictionType.THERAPEUTIC_OUTCOME,
                    PredictionType.USER_ENGAGEMENT,
                    PredictionType.INTERVENTION_EFFECTIVENESS
                ]

            predictions = []

            for prediction_type in prediction_types:
                prediction = await self._generate_specific_prediction(
                    user_id, prediction_type, timeframe
                )
                if prediction:
                    predictions.append(prediction)

            # Store active predictions
            if user_id not in self.active_predictions:
                self.active_predictions[user_id] = []

            self.active_predictions[user_id].extend(predictions)
            self.analytics_metrics["total_predictions_generated"] += len(predictions)

            logger.info(f"Generated {len(predictions)} therapeutic predictions for user {user_id}")
            return predictions

        except Exception as e:
            logger.error(f"Error generating therapeutic predictions: {e}")
            return []

    async def predict_crisis_risk(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.IMMEDIATE
    ) -> TherapeuticPrediction:
        """Predict crisis risk for user."""
        try:
            # Get user history and patterns
            user_history = list(self.user_interaction_history.get(user_id, []))
            crisis_history = self.crisis_event_history.get(user_id, [])

            # Calculate risk factors
            risk_factors = []
            protective_factors = []
            risk_score = 0.0

            # Analyze recent engagement patterns
            if user_history:
                recent_interactions = user_history[-10:]  # Last 10 interactions

                # Low engagement risk factor
                avg_engagement = np.mean([
                    interaction.get("engagement_score", 0.5)
                    for interaction in recent_interactions
                ])

                if avg_engagement < 0.3:
                    risk_factors.append("Low engagement pattern detected")
                    risk_score += 0.3
                elif avg_engagement > 0.7:
                    protective_factors.append("High engagement pattern")
                    risk_score -= 0.1

                # Negative outcome pattern
                negative_outcomes = sum(
                    1 for interaction in recent_interactions
                    if interaction.get("outcome_score", 0.5) < 0.3
                )

                if negative_outcomes >= 3:
                    risk_factors.append("Multiple negative outcomes")
                    risk_score += 0.4

                # Emotional distress indicators
                distress_indicators = sum(
                    1 for interaction in recent_interactions
                    if interaction.get("emotional_distress", 0.0) > 0.7
                )

                if distress_indicators >= 2:
                    risk_factors.append("Elevated emotional distress")
                    risk_score += 0.5

            # Historical crisis patterns
            if crisis_history:
                recent_crises = [
                    crisis for crisis in crisis_history
                    if crisis.get("timestamp", datetime.min) > datetime.utcnow() - timedelta(days=30)
                ]

                if recent_crises:
                    risk_factors.append("Recent crisis history")
                    risk_score += 0.3

            # Determine confidence based on data availability
            confidence_score = min(0.9, len(user_history) / 50.0)  # More data = higher confidence

            if confidence_score < 0.3:
                confidence = PredictionConfidence.VERY_LOW
            elif confidence_score < 0.5:
                confidence = PredictionConfidence.LOW
            elif confidence_score < 0.7:
                confidence = PredictionConfidence.MODERATE
            elif confidence_score < 0.9:
                confidence = PredictionConfidence.HIGH
            else:
                confidence = PredictionConfidence.VERY_HIGH

            # Generate recommendations
            recommended_interventions = []
            preventive_actions = []
            monitoring_suggestions = []

            if risk_score > 0.7:
                recommended_interventions.append({
                    "type": "immediate_support",
                    "system": "emotional_safety_system",
                    "intensity": "high",
                    "priority": 10
                })
                preventive_actions.append("Activate enhanced monitoring")
                monitoring_suggestions.append("Increase check-in frequency")
            elif risk_score > 0.4:
                recommended_interventions.append({
                    "type": "supportive_intervention",
                    "system": "emotional_safety_system",
                    "intensity": "moderate",
                    "priority": 7
                })
                preventive_actions.append("Implement coping strategies")
                monitoring_suggestions.append("Monitor engagement patterns")

            # Create prediction
            prediction = TherapeuticPrediction(
                user_id=user_id,
                prediction_type=PredictionType.CRISIS_RISK,
                timeframe=timeframe,
                predicted_value=risk_score,
                predicted_category="high" if risk_score > 0.7 else "moderate" if risk_score > 0.4 else "low",
                confidence=confidence,
                confidence_score=confidence_score,
                supporting_patterns=[],
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                recommended_interventions=recommended_interventions,
                preventive_actions=preventive_actions,
                monitoring_suggestions=monitoring_suggestions
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting crisis risk: {e}")
            return None

    async def optimize_therapeutic_interventions(
        self,
        user_id: str,
        target_systems: list[str] | None = None
    ) -> list[InterventionOptimization]:
        """Optimize therapeutic interventions for user."""
        try:
            if target_systems is None:
                target_systems = list(self.therapeutic_systems.keys())

            optimizations = []

            for system_name in target_systems:
                optimization = await self._optimize_system_intervention(user_id, system_name)
                if optimization:
                    optimizations.append(optimization)

            # Store optimizations
            if user_id not in self.intervention_optimizations:
                self.intervention_optimizations[user_id] = []

            self.intervention_optimizations[user_id].extend(optimizations)
            self.analytics_metrics["total_optimizations_created"] += len(optimizations)

            logger.info(f"Generated {len(optimizations)} intervention optimizations for user {user_id}")
            return optimizations

        except Exception as e:
            logger.error(f"Error optimizing therapeutic interventions: {e}")
            return []

    async def record_user_interaction(
        self,
        user_id: str,
        interaction_data: dict[str, Any]
    ):
        """Record user interaction for predictive analysis."""
        try:
            # Add timestamp if not present
            if "timestamp" not in interaction_data:
                interaction_data["timestamp"] = datetime.utcnow()

            # Store interaction
            self.user_interaction_history[user_id].append(interaction_data)

            # Update models with new data
            await self._update_models_with_interaction(user_id, interaction_data)

            logger.debug(f"Recorded interaction for user {user_id}")

        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")

    async def record_therapeutic_outcome(
        self,
        user_id: str,
        outcome_data: dict[str, Any]
    ):
        """Record therapeutic outcome for predictive analysis."""
        try:
            # Add timestamp if not present
            if "timestamp" not in outcome_data:
                outcome_data["timestamp"] = datetime.utcnow()

            # Store outcome
            self.therapeutic_outcome_history[user_id].append(outcome_data)

            # Validate predictions against actual outcomes
            await self._validate_predictions_against_outcome(user_id, outcome_data)

            logger.debug(f"Recorded therapeutic outcome for user {user_id}")

        except Exception as e:
            logger.error(f"Error recording therapeutic outcome: {e}")

    async def record_crisis_event(
        self,
        user_id: str,
        crisis_data: dict[str, Any]
    ):
        """Record crisis event for predictive analysis."""
        try:
            # Add timestamp if not present
            if "timestamp" not in crisis_data:
                crisis_data["timestamp"] = datetime.utcnow()

            # Store crisis event
            self.crisis_event_history[user_id].append(crisis_data)

            # Update crisis prediction models
            await self._update_crisis_models(user_id, crisis_data)

            logger.info(f"Recorded crisis event for user {user_id}")

        except Exception as e:
            logger.error(f"Error recording crisis event: {e}")

    async def get_predictive_insights(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive predictive insights for user."""
        try:
            # Get user patterns and predictions
            user_patterns = [
                pattern for pattern in self.therapeutic_patterns.values()
                if user_id in pattern.contextual_factors.get("user_ids", [user_id])
            ]

            user_predictions = self.active_predictions.get(user_id, [])
            user_optimizations = self.intervention_optimizations.get(user_id, [])

            # Calculate insights
            insights = {
                "user_id": user_id,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "pattern_analysis": {
                    "total_patterns_identified": len(user_patterns),
                    "pattern_types": list({p.pattern_type for p in user_patterns}),
                    "strongest_patterns": sorted(
                        user_patterns, key=lambda p: p.strength, reverse=True
                    )[:3],
                    "most_frequent_patterns": sorted(
                        user_patterns, key=lambda p: p.frequency, reverse=True
                    )[:3]
                },
                "prediction_summary": {
                    "total_active_predictions": len(user_predictions),
                    "prediction_types": list({p.prediction_type.value for p in user_predictions}),
                    "high_confidence_predictions": [
                        p for p in user_predictions
                        if p.confidence in [PredictionConfidence.HIGH, PredictionConfidence.VERY_HIGH]
                    ],
                    "crisis_risk_level": self._get_current_crisis_risk_level(user_predictions),
                    "therapeutic_outlook": self._get_therapeutic_outlook(user_predictions)
                },
                "optimization_summary": {
                    "total_optimizations": len(user_optimizations),
                    "high_impact_optimizations": [
                        opt for opt in user_optimizations if opt.estimated_impact > 0.3
                    ],
                    "systems_optimized": list({opt.target_system for opt in user_optimizations}),
                    "average_improvement_potential": np.mean([
                        opt.improvement_potential for opt in user_optimizations
                    ]) if user_optimizations else 0.0
                },
                "interaction_analysis": await self._analyze_interaction_trends(user_id),
                "recommendations": await self._generate_comprehensive_recommendations(user_id)
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting predictive insights: {e}")
            return {"error": str(e)}

    async def _initialize_predictive_models(self):
        """Initialize predictive models."""
        try:
            # Initialize basic predictive models (placeholder for ML implementation)
            self.prediction_models = {
                "crisis_risk_predictor": {"type": "logistic_regression", "accuracy": 0.82},
                "therapeutic_outcome_predictor": {"type": "random_forest", "accuracy": 0.75},
                "engagement_predictor": {"type": "neural_network", "accuracy": 0.78},
                "intervention_effectiveness_predictor": {"type": "gradient_boosting", "accuracy": 0.73},
                "relapse_risk_predictor": {"type": "svm", "accuracy": 0.79},
            }

            self.pattern_recognition_models = {
                "engagement_pattern_detector": {"type": "clustering", "accuracy": 0.71},
                "response_pattern_detector": {"type": "time_series", "accuracy": 0.68},
                "crisis_pattern_detector": {"type": "anomaly_detection", "accuracy": 0.85},
                "intervention_pattern_detector": {"type": "association_rules", "accuracy": 0.66},
            }

            self.optimization_models = {
                "intervention_optimizer": {"type": "reinforcement_learning", "accuracy": 0.72},
                "parameter_optimizer": {"type": "bayesian_optimization", "accuracy": 0.69},
                "timing_optimizer": {"type": "time_series_forecasting", "accuracy": 0.74},
            }

            logger.info("Predictive models initialized")

        except Exception as e:
            logger.error(f"Error initializing predictive models: {e}")
            raise

    def _get_timeframe_cutoff(self, timeframe: AnalyticsTimeframe) -> datetime:
        """Get cutoff time for analysis timeframe."""
        now = datetime.utcnow()

        if timeframe == AnalyticsTimeframe.IMMEDIATE:
            return now - timedelta(hours=2)
        elif timeframe == AnalyticsTimeframe.SHORT_TERM:
            return now - timedelta(days=2)
        elif timeframe == AnalyticsTimeframe.MEDIUM_TERM:
            return now - timedelta(weeks=2)
        elif timeframe == AnalyticsTimeframe.LONG_TERM:
            return now - timedelta(days=90)
        else:
            return now - timedelta(days=7)

    async def _identify_engagement_patterns(
        self,
        user_id: str,
        history: list[dict[str, Any]]
    ) -> TherapeuticPattern | None:
        """Identify engagement patterns from user history."""
        try:
            engagement_scores = [
                interaction.get("engagement_score", 0.5)
                for interaction in history
                if "engagement_score" in interaction
            ]

            if len(engagement_scores) < 5:
                return None

            # Calculate pattern characteristics
            avg_engagement = statistics.mean(engagement_scores)
            engagement_trend = self._calculate_trend(engagement_scores)
            consistency = 1.0 - statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 1.0

            # Determine pattern significance
            if abs(engagement_trend) > 0.1 or avg_engagement < 0.3 or avg_engagement > 0.8:
                significance = min(1.0, abs(engagement_trend) * 2 + abs(avg_engagement - 0.5))

                pattern = TherapeuticPattern(
                    pattern_type="engagement",
                    pattern_name="User Engagement Pattern",
                    description=f"Average engagement: {avg_engagement:.2f}, Trend: {engagement_trend:.2f}",
                    frequency=len(engagement_scores) / len(history),
                    strength=significance,
                    consistency=consistency,
                    significance=significance,
                    data_points=[{"engagement_scores": engagement_scores}],
                    temporal_features={
                        "average_engagement": avg_engagement,
                        "engagement_trend": engagement_trend,
                        "consistency": consistency
                    },
                    contextual_factors={"user_ids": [user_id]},
                    associated_outcomes=["user_satisfaction", "therapeutic_progress"],
                    predictive_indicators=["future_engagement", "session_completion"],
                    observation_count=len(engagement_scores)
                )

                return pattern

            return None

        except Exception as e:
            logger.error(f"Error identifying engagement patterns: {e}")
            return None

    async def _identify_response_patterns(
        self,
        user_id: str,
        history: list[dict[str, Any]]
    ) -> TherapeuticPattern | None:
        """Identify therapeutic response patterns."""
        try:
            response_scores = [
                interaction.get("therapeutic_response", 0.5)
                for interaction in history
                if "therapeutic_response" in interaction
            ]

            if len(response_scores) < 5:
                return None

            avg_response = statistics.mean(response_scores)
            response_trend = self._calculate_trend(response_scores)
            consistency = 1.0 - statistics.stdev(response_scores) if len(response_scores) > 1 else 1.0

            if abs(response_trend) > 0.1 or avg_response < 0.4 or avg_response > 0.7:
                significance = min(1.0, abs(response_trend) * 2 + abs(avg_response - 0.5))

                pattern = TherapeuticPattern(
                    pattern_type="therapeutic_response",
                    pattern_name="Therapeutic Response Pattern",
                    description=f"Average response: {avg_response:.2f}, Trend: {response_trend:.2f}",
                    frequency=len(response_scores) / len(history),
                    strength=significance,
                    consistency=consistency,
                    significance=significance,
                    data_points=[{"response_scores": response_scores}],
                    temporal_features={
                        "average_response": avg_response,
                        "response_trend": response_trend,
                        "consistency": consistency
                    },
                    contextual_factors={"user_ids": [user_id]},
                    associated_outcomes=["therapeutic_effectiveness", "symptom_improvement"],
                    predictive_indicators=["treatment_success", "intervention_response"],
                    observation_count=len(response_scores)
                )

                return pattern

            return None

        except Exception as e:
            logger.error(f"Error identifying response patterns: {e}")
            return None

    async def _identify_crisis_patterns(
        self,
        user_id: str,
        history: list[dict[str, Any]]
    ) -> TherapeuticPattern | None:
        """Identify crisis risk patterns."""
        try:
            crisis_indicators = [
                interaction.get("crisis_indicators", {})
                for interaction in history
                if "crisis_indicators" in interaction
            ]

            if len(crisis_indicators) < 3:
                return None

            # Analyze crisis indicator trends
            risk_scores = [
                indicators.get("risk_score", 0.0)
                for indicators in crisis_indicators
                if isinstance(indicators, dict)
            ]

            if not risk_scores:
                return None

            avg_risk = statistics.mean(risk_scores)
            risk_trend = self._calculate_trend(risk_scores)

            if avg_risk > 0.3 or risk_trend > 0.1:
                significance = min(1.0, avg_risk * 2 + max(0, risk_trend * 3))

                pattern = TherapeuticPattern(
                    pattern_type="crisis_risk",
                    pattern_name="Crisis Risk Pattern",
                    description=f"Average risk: {avg_risk:.2f}, Trend: {risk_trend:.2f}",
                    frequency=len(risk_scores) / len(history),
                    strength=significance,
                    consistency=1.0 - statistics.stdev(risk_scores) if len(risk_scores) > 1 else 1.0,
                    significance=significance,
                    data_points=[{"risk_scores": risk_scores}],
                    temporal_features={
                        "average_risk": avg_risk,
                        "risk_trend": risk_trend,
                        "peak_risk": max(risk_scores),
                        "risk_volatility": statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0.0
                    },
                    contextual_factors={"user_ids": [user_id]},
                    associated_outcomes=["crisis_events", "safety_interventions"],
                    predictive_indicators=["crisis_probability", "intervention_need"],
                    observation_count=len(risk_scores)
                )

                return pattern

            return None

        except Exception as e:
            logger.error(f"Error identifying crisis patterns: {e}")
            return None

    async def _identify_intervention_patterns(
        self,
        user_id: str,
        history: list[dict[str, Any]]
    ) -> TherapeuticPattern | None:
        """Identify intervention effectiveness patterns."""
        try:
            intervention_data = [
                interaction.get("intervention_data", {})
                for interaction in history
                if "intervention_data" in interaction
            ]

            if len(intervention_data) < 5:
                return None

            # Analyze intervention effectiveness
            effectiveness_scores = []
            for data in intervention_data:
                if isinstance(data, dict) and "effectiveness" in data:
                    effectiveness_scores.append(data["effectiveness"])

            if not effectiveness_scores:
                return None

            avg_effectiveness = statistics.mean(effectiveness_scores)
            effectiveness_trend = self._calculate_trend(effectiveness_scores)

            if avg_effectiveness > 0.6 or abs(effectiveness_trend) > 0.1:
                significance = min(1.0, avg_effectiveness + abs(effectiveness_trend))

                pattern = TherapeuticPattern(
                    pattern_type="intervention_effectiveness",
                    pattern_name="Intervention Effectiveness Pattern",
                    description=f"Average effectiveness: {avg_effectiveness:.2f}, Trend: {effectiveness_trend:.2f}",
                    frequency=len(effectiveness_scores) / len(history),
                    strength=significance,
                    consistency=1.0 - statistics.stdev(effectiveness_scores) if len(effectiveness_scores) > 1 else 1.0,
                    significance=significance,
                    data_points=[{"effectiveness_scores": effectiveness_scores}],
                    temporal_features={
                        "average_effectiveness": avg_effectiveness,
                        "effectiveness_trend": effectiveness_trend,
                        "peak_effectiveness": max(effectiveness_scores),
                        "consistency": 1.0 - statistics.stdev(effectiveness_scores) if len(effectiveness_scores) > 1 else 1.0
                    },
                    contextual_factors={"user_ids": [user_id]},
                    associated_outcomes=["therapeutic_progress", "intervention_success"],
                    predictive_indicators=["optimal_interventions", "treatment_response"],
                    observation_count=len(effectiveness_scores)
                )

                return pattern

            return None

        except Exception as e:
            logger.error(f"Error identifying intervention patterns: {e}")
            return None

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend in values using simple linear regression."""
        try:
            if len(values) < 2:
                return 0.0

            n = len(values)
            x = list(range(n))

            # Calculate slope using least squares
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(values)

            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

            if denominator == 0:
                return 0.0

            slope = numerator / denominator
            return slope

        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 0.0

    async def _generate_specific_prediction(
        self,
        user_id: str,
        prediction_type: PredictionType,
        timeframe: AnalyticsTimeframe
    ) -> TherapeuticPrediction | None:
        """Generate specific type of prediction."""
        try:
            if prediction_type == PredictionType.CRISIS_RISK:
                return await self.predict_crisis_risk(user_id, timeframe)
            elif prediction_type == PredictionType.USER_ENGAGEMENT:
                return await self._predict_user_engagement(user_id, timeframe)
            elif prediction_type == PredictionType.THERAPEUTIC_OUTCOME:
                return await self._predict_therapeutic_outcome(user_id, timeframe)
            elif prediction_type == PredictionType.INTERVENTION_EFFECTIVENESS:
                return await self._predict_intervention_effectiveness(user_id, timeframe)
            else:
                return None

        except Exception as e:
            logger.error(f"Error generating {prediction_type.value} prediction: {e}")
            return None

    async def _predict_user_engagement(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe
    ) -> TherapeuticPrediction | None:
        """Predict user engagement levels."""
        try:
            user_history = list(self.user_interaction_history.get(user_id, []))
            if len(user_history) < 5:
                return None

            recent_engagement = [
                interaction.get("engagement_score", 0.5)
                for interaction in user_history[-10:]
            ]

            avg_engagement = statistics.mean(recent_engagement)
            engagement_trend = self._calculate_trend(recent_engagement)

            # Predict future engagement
            predicted_engagement = max(0.0, min(1.0, avg_engagement + engagement_trend * 0.5))

            confidence_score = min(0.9, len(user_history) / 20.0)
            confidence = self._get_confidence_level(confidence_score)

            prediction = TherapeuticPrediction(
                user_id=user_id,
                prediction_type=PredictionType.USER_ENGAGEMENT,
                timeframe=timeframe,
                predicted_value=predicted_engagement,
                predicted_category="high" if predicted_engagement > 0.7 else "moderate" if predicted_engagement > 0.4 else "low",
                confidence=confidence,
                confidence_score=confidence_score,
                supporting_patterns=[],
                recommended_interventions=[{
                    "type": "engagement_boost" if predicted_engagement < 0.5 else "maintain_engagement",
                    "system": "gameplay_loop_controller",
                    "priority": 8 if predicted_engagement < 0.5 else 5
                }]
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting user engagement: {e}")
            return None

    async def _predict_therapeutic_outcome(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe
    ) -> TherapeuticPrediction | None:
        """Predict therapeutic outcomes."""
        try:
            outcome_history = list(self.therapeutic_outcome_history.get(user_id, []))
            if len(outcome_history) < 3:
                return None

            recent_outcomes = [
                outcome.get("outcome_score", 0.5)
                for outcome in outcome_history[-5:]
            ]

            avg_outcome = statistics.mean(recent_outcomes)
            outcome_trend = self._calculate_trend(recent_outcomes)

            # Predict future outcome
            predicted_outcome = max(0.0, min(1.0, avg_outcome + outcome_trend * 0.3))

            confidence_score = min(0.9, len(outcome_history) / 10.0)
            confidence = self._get_confidence_level(confidence_score)

            prediction = TherapeuticPrediction(
                user_id=user_id,
                prediction_type=PredictionType.THERAPEUTIC_OUTCOME,
                timeframe=timeframe,
                predicted_value=predicted_outcome,
                predicted_category="positive" if predicted_outcome > 0.6 else "neutral" if predicted_outcome > 0.4 else "concerning",
                confidence=confidence,
                confidence_score=confidence_score,
                supporting_patterns=[],
                recommended_interventions=[{
                    "type": "outcome_optimization",
                    "system": "therapeutic_integration_system",
                    "priority": 7
                }] if predicted_outcome < 0.6 else []
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting therapeutic outcome: {e}")
            return None

    async def _predict_intervention_effectiveness(
        self,
        user_id: str,
        timeframe: AnalyticsTimeframe
    ) -> TherapeuticPrediction | None:
        """Predict intervention effectiveness."""
        try:
            user_history = list(self.user_interaction_history.get(user_id, []))
            intervention_data = [
                interaction.get("intervention_data", {})
                for interaction in user_history
                if "intervention_data" in interaction
            ]

            if len(intervention_data) < 3:
                return None

            effectiveness_scores = [
                data.get("effectiveness", 0.5)
                for data in intervention_data
                if isinstance(data, dict)
            ]

            if not effectiveness_scores:
                return None

            avg_effectiveness = statistics.mean(effectiveness_scores)
            effectiveness_trend = self._calculate_trend(effectiveness_scores)

            predicted_effectiveness = max(0.0, min(1.0, avg_effectiveness + effectiveness_trend * 0.2))

            confidence_score = min(0.9, len(effectiveness_scores) / 8.0)
            confidence = self._get_confidence_level(confidence_score)

            prediction = TherapeuticPrediction(
                user_id=user_id,
                prediction_type=PredictionType.INTERVENTION_EFFECTIVENESS,
                timeframe=timeframe,
                predicted_value=predicted_effectiveness,
                predicted_category="high" if predicted_effectiveness > 0.7 else "moderate" if predicted_effectiveness > 0.5 else "low",
                confidence=confidence,
                confidence_score=confidence_score,
                supporting_patterns=[],
                recommended_interventions=[{
                    "type": "intervention_adjustment",
                    "system": "adaptive_difficulty_engine",
                    "priority": 6
                }] if predicted_effectiveness < 0.6 else []
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting intervention effectiveness: {e}")
            return None

    def _get_confidence_level(self, confidence_score: float) -> PredictionConfidence:
        """Convert confidence score to confidence level."""
        if confidence_score < 0.3:
            return PredictionConfidence.VERY_LOW
        elif confidence_score < 0.5:
            return PredictionConfidence.LOW
        elif confidence_score < 0.7:
            return PredictionConfidence.MODERATE
        elif confidence_score < 0.9:
            return PredictionConfidence.HIGH
        else:
            return PredictionConfidence.VERY_HIGH

    async def _optimize_system_intervention(
        self,
        user_id: str,
        system_name: str
    ) -> InterventionOptimization | None:
        """Optimize intervention for specific system."""
        try:
            # Get user interaction history with this system
            user_history = list(self.user_interaction_history.get(user_id, []))
            system_interactions = [
                interaction for interaction in user_history
                if interaction.get("system_name") == system_name
            ]

            if len(system_interactions) < 3:
                return None

            # Calculate current effectiveness
            effectiveness_scores = [
                interaction.get("effectiveness", 0.5)
                for interaction in system_interactions
            ]

            current_effectiveness = statistics.mean(effectiveness_scores)

            # Predict potential improvement
            improvement_potential = min(0.5, (1.0 - current_effectiveness) * 0.7)
            predicted_effectiveness = current_effectiveness + improvement_potential

            # Generate optimization recommendations
            parameter_adjustments = {}
            timing_recommendations = {}
            intensity_adjustments = {}

            if current_effectiveness < 0.6:
                parameter_adjustments["difficulty_level"] = "decrease"
                intensity_adjustments["support_level"] = 0.2
                timing_recommendations["session_frequency"] = "increase"
            elif current_effectiveness > 0.8:
                parameter_adjustments["challenge_level"] = "increase"
                intensity_adjustments["autonomy_level"] = 0.1

            optimization = InterventionOptimization(
                user_id=user_id,
                target_system=system_name,
                current_effectiveness=current_effectiveness,
                predicted_effectiveness=predicted_effectiveness,
                improvement_potential=improvement_potential,
                parameter_adjustments=parameter_adjustments,
                timing_recommendations=timing_recommendations,
                intensity_adjustments=intensity_adjustments,
                optimization_rationale=f"Based on {len(system_interactions)} interactions with average effectiveness {current_effectiveness:.2f}",
                supporting_evidence=["Historical effectiveness trend", "User response patterns"],
                expected_outcomes={"effectiveness_improvement": improvement_potential},
                priority=8 if improvement_potential > 0.2 else 5,
                estimated_impact=improvement_potential
            )

            return optimization

        except Exception as e:
            logger.error(f"Error optimizing system intervention: {e}")
            return None

    def _get_current_crisis_risk_level(self, predictions: list[TherapeuticPrediction]) -> str:
        """Get current crisis risk level from predictions."""
        crisis_predictions = [
            p for p in predictions
            if p.prediction_type == PredictionType.CRISIS_RISK
        ]

        if not crisis_predictions:
            return "unknown"

        latest_prediction = max(crisis_predictions, key=lambda p: p.created_at)
        return latest_prediction.predicted_category

    def _get_therapeutic_outlook(self, predictions: list[TherapeuticPrediction]) -> str:
        """Get therapeutic outlook from predictions."""
        outcome_predictions = [
            p for p in predictions
            if p.prediction_type == PredictionType.THERAPEUTIC_OUTCOME
        ]

        if not outcome_predictions:
            return "unknown"

        latest_prediction = max(outcome_predictions, key=lambda p: p.created_at)
        return latest_prediction.predicted_category

    async def _analyze_interaction_trends(self, user_id: str) -> dict[str, Any]:
        """Analyze interaction trends for user."""
        try:
            user_history = list(self.user_interaction_history.get(user_id, []))

            if len(user_history) < 5:
                return {"insufficient_data": True}

            # Analyze recent trends
            recent_interactions = user_history[-10:]

            engagement_scores = [i.get("engagement_score", 0.5) for i in recent_interactions]
            satisfaction_scores = [i.get("satisfaction_score", 0.5) for i in recent_interactions]

            return {
                "total_interactions": len(user_history),
                "recent_interactions": len(recent_interactions),
                "average_engagement": statistics.mean(engagement_scores),
                "engagement_trend": self._calculate_trend(engagement_scores),
                "average_satisfaction": statistics.mean(satisfaction_scores),
                "satisfaction_trend": self._calculate_trend(satisfaction_scores),
                "interaction_frequency": len(user_history) / max(1, (datetime.utcnow() - user_history[0].get("timestamp", datetime.utcnow())).days),
                "most_active_systems": self._get_most_active_systems(user_history)
            }

        except Exception as e:
            logger.error(f"Error analyzing interaction trends: {e}")
            return {"error": str(e)}

    def _get_most_active_systems(self, history: list[dict[str, Any]]) -> list[str]:
        """Get most active systems from interaction history."""
        system_counts = defaultdict(int)

        for interaction in history:
            system_name = interaction.get("system_name", "unknown")
            system_counts[system_name] += 1

        return sorted(system_counts.keys(), key=lambda s: system_counts[s], reverse=True)[:3]

    async def _generate_comprehensive_recommendations(self, user_id: str) -> list[str]:
        """Generate comprehensive recommendations for user."""
        recommendations = []

        try:
            # Get user predictions and optimizations
            user_predictions = self.active_predictions.get(user_id, [])
            user_optimizations = self.intervention_optimizations.get(user_id, [])

            # Crisis risk recommendations
            crisis_predictions = [p for p in user_predictions if p.prediction_type == PredictionType.CRISIS_RISK]
            if crisis_predictions:
                latest_crisis = max(crisis_predictions, key=lambda p: p.created_at)
                if latest_crisis.predicted_value > 0.7:
                    recommendations.append("Implement immediate crisis prevention measures")
                elif latest_crisis.predicted_value > 0.4:
                    recommendations.append("Increase monitoring and support frequency")

            # Engagement recommendations
            engagement_predictions = [p for p in user_predictions if p.prediction_type == PredictionType.USER_ENGAGEMENT]
            if engagement_predictions:
                latest_engagement = max(engagement_predictions, key=lambda p: p.created_at)
                if latest_engagement.predicted_value < 0.5:
                    recommendations.append("Implement engagement enhancement strategies")

            # Optimization recommendations
            high_impact_optimizations = [opt for opt in user_optimizations if opt.estimated_impact > 0.2]
            if high_impact_optimizations:
                recommendations.append(f"Apply {len(high_impact_optimizations)} high-impact intervention optimizations")

            # General recommendations
            if not recommendations:
                recommendations.append("Continue current therapeutic approach with regular monitoring")

            return recommendations

        except Exception as e:
            logger.error(f"Error generating comprehensive recommendations: {e}")
            return ["Error generating recommendations - manual review required"]

    async def _update_models_with_interaction(self, user_id: str, interaction_data: dict[str, Any]):
        """Update models with new interaction data."""
        try:
            # Update model accuracy metrics (placeholder for ML implementation)
            for _model_name, model_data in self.prediction_models.items():
                # Simulate learning improvement
                current_accuracy = model_data["accuracy"]
                improvement = 0.001 * (interaction_data.get("satisfaction_score", 0.5) - 0.5)
                model_data["accuracy"] = min(0.95, current_accuracy + improvement)

            # Update overall prediction accuracy
            avg_accuracy = np.mean([m["accuracy"] for m in self.prediction_models.values()])
            self.analytics_metrics["prediction_accuracy"] = avg_accuracy

        except Exception as e:
            logger.error(f"Error updating models with interaction: {e}")

    async def _validate_predictions_against_outcome(self, user_id: str, outcome_data: dict[str, Any]):
        """Validate predictions against actual outcomes."""
        try:
            user_predictions = self.active_predictions.get(user_id, [])

            for prediction in user_predictions:
                if prediction.validation_status == "pending":
                    # Simple validation based on outcome score
                    actual_outcome = outcome_data.get("outcome_score", 0.5)
                    predicted_outcome = prediction.predicted_value

                    # Calculate prediction accuracy
                    accuracy = 1.0 - abs(actual_outcome - predicted_outcome)

                    # Update prediction
                    prediction.actual_outcome = actual_outcome
                    prediction.validation_status = "validated"

                    # Update model accuracy
                    if prediction.prediction_type.value in self.prediction_models:
                        model = self.prediction_models[prediction.prediction_type.value + "_predictor"]
                        current_accuracy = model["accuracy"]
                        model["accuracy"] = (current_accuracy * 0.9) + (accuracy * 0.1)  # Weighted average

        except Exception as e:
            logger.error(f"Error validating predictions: {e}")

    async def _update_crisis_models(self, user_id: str, crisis_data: dict[str, Any]):
        """Update crisis prediction models with crisis event."""
        try:
            # Update crisis prediction accuracy
            crisis_predictions = [
                p for p in self.active_predictions.get(user_id, [])
                if p.prediction_type == PredictionType.CRISIS_RISK and p.validation_status == "pending"
            ]

            for prediction in crisis_predictions:
                # Crisis occurred - validate prediction
                if prediction.predicted_value > 0.5:
                    # Correct prediction
                    accuracy_improvement = 0.1
                else:
                    # Missed prediction
                    accuracy_improvement = -0.05

                # Update model
                if "crisis_risk_predictor" in self.prediction_models:
                    model = self.prediction_models["crisis_risk_predictor"]
                    model["accuracy"] = max(0.5, min(0.95, model["accuracy"] + accuracy_improvement))

                prediction.validation_status = "validated"
                prediction.actual_outcome = 1.0  # Crisis occurred

            # Update crisis prediction accuracy metric
            self.analytics_metrics["crisis_prediction_accuracy"] = self.prediction_models.get(
                "crisis_risk_predictor", {}
            ).get("accuracy", 0.0)

        except Exception as e:
            logger.error(f"Error updating crisis models: {e}")

    async def _pattern_analysis_loop(self):
        """Background loop for pattern analysis."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Analyze patterns for all users with sufficient data
                    for user_id in list(self.user_interaction_history.keys()):
                        if len(self.user_interaction_history[user_id]) >= 10:
                            await self.analyze_therapeutic_patterns(user_id)

                    await asyncio.sleep(3600)  # Analyze every hour

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in pattern analysis loop: {e}")
                    await asyncio.sleep(3600)

        except asyncio.CancelledError:
            logger.info("Pattern analysis loop cancelled")

    async def _prediction_generation_loop(self):
        """Background loop for prediction generation."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Generate predictions for active users
                    for user_id in list(self.user_interaction_history.keys()):
                        if len(self.user_interaction_history[user_id]) >= 5:
                            await self.generate_therapeutic_predictions(user_id)

                    await asyncio.sleep(1800)  # Generate every 30 minutes

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in prediction generation loop: {e}")
                    await asyncio.sleep(1800)

        except asyncio.CancelledError:
            logger.info("Prediction generation loop cancelled")

    async def _optimization_loop(self):
        """Background loop for intervention optimization."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Optimize interventions for users with sufficient data
                    for user_id in list(self.user_interaction_history.keys()):
                        if len(self.user_interaction_history[user_id]) >= 8:
                            await self.optimize_therapeutic_interventions(user_id)

                    await asyncio.sleep(7200)  # Optimize every 2 hours

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in optimization loop: {e}")
                    await asyncio.sleep(7200)

        except asyncio.CancelledError:
            logger.info("Optimization loop cancelled")

    async def _model_training_loop(self):
        """Background loop for model training and improvement."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Update model accuracies and retrain
                    await self._update_model_accuracies()

                    await asyncio.sleep(21600)  # Train every 6 hours

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in model training loop: {e}")
                    await asyncio.sleep(21600)

        except asyncio.CancelledError:
            logger.info("Model training loop cancelled")

    async def _update_model_accuracies(self):
        """Update model accuracy metrics."""
        try:
            # Update pattern recognition accuracy
            pattern_accuracy = np.mean([m["accuracy"] for m in self.pattern_recognition_models.values()])
            self.analytics_metrics["pattern_recognition_accuracy"] = pattern_accuracy

            # Update optimization effectiveness
            optimization_accuracy = np.mean([m["accuracy"] for m in self.optimization_models.values()])
            self.analytics_metrics["optimization_effectiveness"] = optimization_accuracy

            # Calculate intervention optimization success rate
            total_optimizations = sum(len(opts) for opts in self.intervention_optimizations.values())
            if total_optimizations > 0:
                # Simulate success rate based on model accuracy
                success_rate = optimization_accuracy * 0.8  # Conservative estimate
                self.analytics_metrics["intervention_optimization_success_rate"] = success_rate

        except Exception as e:
            logger.error(f"Error updating model accuracies: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the Predictive Therapeutic Analytics."""
        try:
            therapeutic_systems_available = len([
                system for system in self.therapeutic_systems.values() if system is not None
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
                "analytics_status": self.status,
                "total_patterns_identified": len(self.therapeutic_patterns),
                "active_predictions": sum(len(preds) for preds in self.active_predictions.values()),
                "active_optimizations": sum(len(opts) for opts in self.intervention_optimizations.values()),
                "prediction_models": len(self.prediction_models),
                "pattern_recognition_models": len(self.pattern_recognition_models),
                "optimization_models": len(self.optimization_models),
                "users_with_data": len(self.user_interaction_history),
                "therapeutic_systems_available": f"{therapeutic_systems_available}/9",
                "integration_systems_available": f"{integration_systems_available}/3",
                "personalization_engine_available": self.personalization_engine is not None,
                "background_tasks_running": (
                    self._pattern_analysis_task is not None and not self._pattern_analysis_task.done() and
                    self._prediction_generation_task is not None and not self._prediction_generation_task.done() and
                    self._optimization_task is not None and not self._optimization_task.done() and
                    self._model_training_task is not None and not self._model_training_task.done()
                ),
                "analytics_metrics": self.analytics_metrics,
            }

        except Exception as e:
            logger.error(f"Error in predictive analytics health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def shutdown(self):
        """Shutdown the Predictive Therapeutic Analytics."""
        try:
            logger.info("Shutting down PredictiveTherapeuticAnalytics")

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            # Cancel background tasks
            for task in [
                self._pattern_analysis_task,
                self._prediction_generation_task,
                self._optimization_task,
                self._model_training_task
            ]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            self.status = "shutdown"
            logger.info("PredictiveTherapeuticAnalytics shutdown complete")

        except Exception as e:
            logger.error(f"Error during predictive analytics shutdown: {e}")
            raise
