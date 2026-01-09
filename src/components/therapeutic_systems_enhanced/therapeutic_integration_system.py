"""
Logseq: [[TTA.dev/Components/Therapeutic_systems_enhanced/Therapeutic_integration_system]]

# Logseq: [[TTA/Components/Therapeutic_systems_enhanced/Therapeutic_integration_system]]
Therapeutic Integration System Implementation

This module provides production-ready therapeutic framework integration
for the TTA therapeutic platform, implementing evidence-based therapeutic
approaches and personalized therapeutic recommendations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class TherapeuticFramework(Enum):
    """8+ therapeutic frameworks supported by the integration system."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based_therapy"
    HUMANISTIC = "humanistic_therapy"
    PSYCHODYNAMIC = "psychodynamic_therapy"
    SOLUTION_FOCUSED = "solution_focused_therapy"
    NARRATIVE_THERAPY = "narrative_therapy"
    GESTALT = "gestalt_therapy"
    EMDR = "eye_movement_desensitization_reprocessing"


class IntegrationStrategy(Enum):
    """Strategies for integrating therapeutic concepts into scenarios."""

    DIRECT_TEACHING = "direct_teaching"
    EXPERIENTIAL_LEARNING = "experiential_learning"
    METAPHORICAL_EMBEDDING = "metaphorical_embedding"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION_PROMPTING = "reflection_prompting"
    MODELING_DEMONSTRATION = "modeling_demonstration"
    GRADUAL_EXPOSURE = "gradual_exposure"
    COLLABORATIVE_EXPLORATION = "collaborative_exploration"


class ScenarioType(Enum):
    """Types of therapeutic scenarios that can be generated."""

    ANXIETY_MANAGEMENT = "anxiety_management"
    DEPRESSION_SUPPORT = "depression_support"
    RELATIONSHIP_SKILLS = "relationship_skills"
    COMMUNICATION_PRACTICE = "communication_practice"
    EMOTIONAL_REGULATION = "emotional_regulation"
    CONFIDENCE_BUILDING = "confidence_building"
    STRESS_MANAGEMENT = "stress_management"
    MINDFULNESS_PRACTICE = "mindfulness_practice"
    TRAUMA_PROCESSING = "trauma_processing"
    ADDICTION_RECOVERY = "addiction_recovery"


@dataclass
class TherapeuticRecommendation:
    """Represents a personalized therapeutic recommendation."""

    recommendation_id: str
    user_id: str
    framework: TherapeuticFramework
    scenario_type: ScenarioType
    integration_strategy: IntegrationStrategy
    priority_score: float
    rationale: str
    expected_outcomes: list[str]
    estimated_duration: int  # minutes
    difficulty_level: str
    character_alignment: dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TherapeuticScenario:
    """Represents a generated therapeutic scenario."""

    scenario_id: str
    user_id: str
    framework: TherapeuticFramework
    scenario_type: ScenarioType
    title: str
    description: str
    narrative_context: str
    therapeutic_goals: list[str]
    practice_opportunities: list[str]
    reflection_prompts: list[str]
    success_criteria: list[str]
    character_involvement: dict[str, str]
    difficulty_level: str
    estimated_duration: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntegrationSession:
    """Tracks a therapeutic integration session."""

    session_id: str
    user_id: str
    scenarios_completed: list[str]
    frameworks_used: list[TherapeuticFramework]
    total_therapeutic_value: float
    character_progression: dict[str, float]
    milestones_achieved: list[str]
    session_duration: int  # minutes
    effectiveness_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class TherapeuticIntegrationSystem:
    """
    Production TherapeuticIntegrationSystem that provides evidence-based
    therapeutic framework integration and personalized recommendations.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic integration system."""
        self.config = config or {}

        # Integration tracking
        self.user_recommendations = {}  # user_id -> List[TherapeuticRecommendation]
        self.generated_scenarios = {}  # user_id -> List[TherapeuticScenario]
        self.integration_sessions = {}  # user_id -> List[IntegrationSession]

        # Framework configurations
        self.framework_configurations = self._initialize_framework_configurations()
        self.integration_strategies = self._initialize_integration_strategies()
        self.scenario_templates = self._initialize_scenario_templates()

        # Configuration parameters
        self.recommendation_refresh_hours = self.config.get(
            "recommendation_refresh_hours", 24
        )
        self.max_recommendations_per_user = self.config.get(
            "max_recommendations_per_user", 5
        )
        self.scenario_difficulty_adaptation = self.config.get(
            "scenario_difficulty_adaptation", True
        )
        self.character_alignment_weight = self.config.get(
            "character_alignment_weight", 0.3
        )

        # Performance metrics
        self.metrics = {
            "recommendations_generated": 0,
            "scenarios_created": 0,
            "frameworks_integrated": 0,
            "integration_sessions": 0,
            "therapeutic_outcomes_achieved": 0,
        }

        logger.info("TherapeuticIntegrationSystem initialized")

    async def initialize(self):
        """Initialize the therapeutic integration system."""
        # Any async initialization can go here
        logger.info("TherapeuticIntegrationSystem initialization complete")

    async def generate_personalized_recommendations(
        self,
        user_id: str,
        therapeutic_goals: list[str] | None = None,
        character_data: dict[str, Any] | None = None,
        user_progress: dict[str, Any] | None = None,
        emotional_state: dict[str, Any] | None = None,
    ) -> list[TherapeuticRecommendation]:
        """
        Generate personalized therapeutic recommendations based on user data.

        This method provides the core interface for therapeutic framework
        integration, creating personalized recommendations based on user
        therapeutic goals, character development, and current progress.

        Args:
            user_id: Unique identifier for the user
            therapeutic_goals: List of user therapeutic goals
            character_data: Character development data from CharacterDevelopmentSystem
            user_progress: Progress data from previous sessions
            emotional_state: Current emotional state from EmotionalSafetySystem

        Returns:
            List of personalized therapeutic recommendations
        """
        try:
            start_time = datetime.utcnow()

            # Analyze user context
            user_context = self._analyze_user_context(
                user_id,
                therapeutic_goals,
                character_data,
                user_progress,
                emotional_state,
            )

            # Generate framework recommendations
            framework_scores = self._calculate_framework_suitability(user_context)

            # Create personalized recommendations
            recommendations = []
            for framework, score in sorted(
                framework_scores.items(), key=lambda x: x[1], reverse=True
            ):
                if len(recommendations) >= self.max_recommendations_per_user:
                    break

                if score > 0.4:  # Minimum suitability threshold
                    recommendation = self._create_recommendation(
                        user_id, framework, score, user_context
                    )
                    recommendations.append(recommendation)

            # Store recommendations
            self.user_recommendations[user_id] = recommendations

            # Update metrics
            self.metrics["recommendations_generated"] += len(recommendations)

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Generated {len(recommendations)} recommendations for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")

            # Return fallback recommendations
            return [self._create_fallback_recommendation(user_id)]

        # If no recommendations were generated, return fallback
        if not recommendations:
            return [self._create_fallback_recommendation(user_id)]

        return recommendations

    async def create_therapeutic_scenario(
        self,
        user_id: str,
        framework: TherapeuticFramework,
        scenario_type: ScenarioType,
        difficulty_level: str | None = None,
        character_data: dict[str, Any] | None = None,
        session_context: dict[str, Any] | None = None,
    ) -> TherapeuticScenario:
        """
        Create a therapeutic scenario based on framework and user context.

        This method generates evidence-based therapeutic scenarios that
        integrate with character development and adaptive difficulty systems.

        Args:
            user_id: Unique identifier for the user
            framework: Therapeutic framework to use
            scenario_type: Type of scenario to create
            difficulty_level: Difficulty level from AdaptiveDifficultyEngine
            character_data: Character data for scenario personalization
            session_context: Current session context

        Returns:
            Generated therapeutic scenario
        """
        try:
            start_time = datetime.utcnow()

            # Get scenario template
            template = self._get_scenario_template(framework, scenario_type)

            # Personalize scenario based on character data
            personalized_scenario = self._personalize_scenario(
                template, character_data, difficulty_level, session_context
            )

            # Create scenario instance
            scenario = TherapeuticScenario(
                scenario_id=str(uuid4()),
                user_id=user_id,
                framework=framework,
                scenario_type=scenario_type,
                title=personalized_scenario["title"],
                description=personalized_scenario["description"],
                narrative_context=personalized_scenario["narrative_context"],
                therapeutic_goals=personalized_scenario["therapeutic_goals"],
                practice_opportunities=personalized_scenario["practice_opportunities"],
                reflection_prompts=personalized_scenario["reflection_prompts"],
                success_criteria=personalized_scenario["success_criteria"],
                character_involvement=personalized_scenario["character_involvement"],
                difficulty_level=difficulty_level or "moderate",
                estimated_duration=personalized_scenario["estimated_duration"],
            )

            # Store scenario
            if user_id not in self.generated_scenarios:
                self.generated_scenarios[user_id] = []
            self.generated_scenarios[user_id].append(scenario)

            # Update metrics
            self.metrics["scenarios_created"] += 1
            self.metrics["frameworks_integrated"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created {framework.value} scenario for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return scenario

        except Exception as e:
            logger.error(f"Error creating scenario for user {user_id}: {e}")

            # Return fallback scenario
            return self._create_fallback_scenario(user_id, framework, scenario_type)

    def _initialize_framework_configurations(
        self,
    ) -> dict[TherapeuticFramework, dict[str, Any]]:
        """Initialize therapeutic framework configurations."""
        return {
            TherapeuticFramework.CBT: {
                "name": "Cognitive Behavioral Therapy",
                "focus": "thought_patterns_and_behaviors",
                "techniques": [
                    "cognitive_restructuring",
                    "behavioral_activation",
                    "exposure_therapy",
                ],
                "suitable_for": ["anxiety", "depression", "phobias", "trauma"],
                "character_attributes": ["self_awareness", "wisdom", "resilience"],
                "difficulty_progression": [
                    "identify_thoughts",
                    "challenge_thoughts",
                    "behavioral_experiments",
                ],
            },
            TherapeuticFramework.DBT: {
                "name": "Dialectical Behavior Therapy",
                "focus": "emotional_regulation_and_interpersonal_skills",
                "techniques": [
                    "mindfulness",
                    "distress_tolerance",
                    "emotion_regulation",
                    "interpersonal_effectiveness",
                ],
                "suitable_for": [
                    "emotional_dysregulation",
                    "relationship_issues",
                    "self_harm",
                    "borderline_traits",
                ],
                "character_attributes": [
                    "emotional_intelligence",
                    "mindfulness",
                    "adaptability",
                ],
                "difficulty_progression": [
                    "mindfulness_basics",
                    "distress_tolerance",
                    "interpersonal_skills",
                ],
            },
            TherapeuticFramework.ACT: {
                "name": "Acceptance and Commitment Therapy",
                "focus": "psychological_flexibility_and_values",
                "techniques": [
                    "acceptance",
                    "mindfulness",
                    "values_clarification",
                    "committed_action",
                ],
                "suitable_for": [
                    "anxiety",
                    "depression",
                    "chronic_pain",
                    "substance_use",
                ],
                "character_attributes": ["courage", "integrity", "adaptability"],
                "difficulty_progression": [
                    "values_exploration",
                    "acceptance_practice",
                    "committed_action",
                ],
            },
            TherapeuticFramework.MINDFULNESS: {
                "name": "Mindfulness-Based Therapy",
                "focus": "present_moment_awareness",
                "techniques": [
                    "meditation",
                    "body_awareness",
                    "breath_work",
                    "mindful_movement",
                ],
                "suitable_for": ["stress", "anxiety", "depression", "chronic_pain"],
                "character_attributes": ["mindfulness", "self_awareness", "compassion"],
                "difficulty_progression": [
                    "breath_awareness",
                    "body_scan",
                    "mindful_daily_activities",
                ],
            },
            TherapeuticFramework.HUMANISTIC: {
                "name": "Humanistic Therapy",
                "focus": "self_actualization_and_personal_growth",
                "techniques": [
                    "unconditional_positive_regard",
                    "empathy",
                    "genuineness",
                    "self_exploration",
                ],
                "suitable_for": [
                    "self_esteem",
                    "identity_issues",
                    "personal_growth",
                    "life_transitions",
                ],
                "character_attributes": ["confidence", "empathy", "integrity"],
                "difficulty_progression": [
                    "self_exploration",
                    "values_clarification",
                    "goal_setting",
                ],
            },
            TherapeuticFramework.PSYCHODYNAMIC: {
                "name": "Psychodynamic Therapy",
                "focus": "unconscious_processes_and_past_experiences",
                "techniques": [
                    "free_association",
                    "transference_analysis",
                    "dream_work",
                    "insight_development",
                ],
                "suitable_for": [
                    "relationship_patterns",
                    "unresolved_trauma",
                    "personality_issues",
                    "depression",
                ],
                "character_attributes": [
                    "self_awareness",
                    "wisdom",
                    "emotional_intelligence",
                ],
                "difficulty_progression": [
                    "pattern_recognition",
                    "insight_development",
                    "integration",
                ],
            },
            TherapeuticFramework.SOLUTION_FOCUSED: {
                "name": "Solution-Focused Brief Therapy",
                "focus": "solutions_and_strengths",
                "techniques": [
                    "miracle_question",
                    "scaling_questions",
                    "exception_finding",
                    "goal_setting",
                ],
                "suitable_for": [
                    "goal_achievement",
                    "brief_interventions",
                    "motivation",
                    "life_changes",
                ],
                "character_attributes": ["confidence", "resilience", "adaptability"],
                "difficulty_progression": [
                    "goal_identification",
                    "resource_mapping",
                    "action_planning",
                ],
            },
            TherapeuticFramework.NARRATIVE_THERAPY: {
                "name": "Narrative Therapy",
                "focus": "personal_stories_and_meaning_making",
                "techniques": [
                    "externalization",
                    "unique_outcomes",
                    "re_authoring",
                    "definitional_ceremony",
                ],
                "suitable_for": [
                    "identity_issues",
                    "trauma",
                    "cultural_issues",
                    "life_transitions",
                ],
                "character_attributes": ["wisdom", "integrity", "empathy"],
                "difficulty_progression": [
                    "story_exploration",
                    "externalization",
                    "re_authoring",
                ],
            },
            TherapeuticFramework.GESTALT: {
                "name": "Gestalt Therapy",
                "focus": "present_moment_awareness_and_integration",
                "techniques": [
                    "here_and_now",
                    "contact_and_awareness",
                    "experiments",
                    "phenomenology",
                ],
                "suitable_for": [
                    "self_awareness",
                    "emotional_integration",
                    "relationship_issues",
                    "creativity",
                ],
                "character_attributes": [
                    "self_awareness",
                    "emotional_intelligence",
                    "adaptability",
                ],
                "difficulty_progression": [
                    "awareness_building",
                    "contact_experiments",
                    "integration",
                ],
            },
            TherapeuticFramework.EMDR: {
                "name": "EMDR Therapy",
                "focus": "trauma_processing_and_integration",
                "techniques": [
                    "bilateral_stimulation",
                    "resource_installation",
                    "trauma_processing",
                    "future_template",
                ],
                "suitable_for": ["trauma", "ptsd", "anxiety", "phobias"],
                "character_attributes": ["resilience", "courage", "self_awareness"],
                "difficulty_progression": [
                    "stabilization",
                    "processing",
                    "integration",
                ],
            },
        }

    def _initialize_integration_strategies(
        self,
    ) -> dict[IntegrationStrategy, dict[str, Any]]:
        """Initialize integration strategy configurations."""
        return {
            IntegrationStrategy.DIRECT_TEACHING: {
                "description": "Direct instruction of therapeutic concepts",
                "engagement_level": "low",
                "retention_rate": "medium",
                "suitable_for": ["psychoeducation", "skill_introduction"],
            },
            IntegrationStrategy.EXPERIENTIAL_LEARNING: {
                "description": "Learning through direct experience and practice",
                "engagement_level": "high",
                "retention_rate": "high",
                "suitable_for": ["skill_practice", "behavioral_change"],
            },
            IntegrationStrategy.METAPHORICAL_EMBEDDING: {
                "description": "Embedding concepts within narrative metaphors",
                "engagement_level": "high",
                "retention_rate": "high",
                "suitable_for": ["complex_concepts", "resistance_to_therapy"],
            },
            IntegrationStrategy.SKILL_PRACTICE: {
                "description": "Structured practice of therapeutic skills",
                "engagement_level": "medium",
                "retention_rate": "high",
                "suitable_for": ["skill_development", "behavioral_rehearsal"],
            },
            IntegrationStrategy.REFLECTION_PROMPTING: {
                "description": "Guided reflection on experiences and insights",
                "engagement_level": "medium",
                "retention_rate": "medium",
                "suitable_for": ["insight_development", "self_awareness"],
            },
            IntegrationStrategy.MODELING_DEMONSTRATION: {
                "description": "Demonstration of skills through character modeling",
                "engagement_level": "medium",
                "retention_rate": "medium",
                "suitable_for": ["social_skills", "communication"],
            },
            IntegrationStrategy.GRADUAL_EXPOSURE: {
                "description": "Gradual exposure to challenging situations",
                "engagement_level": "high",
                "retention_rate": "high",
                "suitable_for": ["anxiety", "phobias", "avoidance"],
            },
            IntegrationStrategy.COLLABORATIVE_EXPLORATION: {
                "description": "Collaborative exploration of thoughts and feelings",
                "engagement_level": "high",
                "retention_rate": "medium",
                "suitable_for": ["insight_therapy", "relationship_work"],
            },
        }

    def _initialize_scenario_templates(self) -> dict[ScenarioType, dict[str, Any]]:
        """Initialize scenario templates for different therapeutic focuses."""
        return {
            ScenarioType.ANXIETY_MANAGEMENT: {
                "title": "Facing the Challenge",
                "base_description": "Navigate an anxiety-provoking situation using therapeutic techniques",
                "therapeutic_goals": [
                    "anxiety_reduction",
                    "coping_skills",
                    "confidence_building",
                ],
                "practice_opportunities": [
                    "breathing_exercises",
                    "cognitive_restructuring",
                    "gradual_exposure",
                ],
                "reflection_prompts": [
                    "What thoughts came up?",
                    "How did your body feel?",
                    "What helped most?",
                ],
                "estimated_duration": 15,
            },
            ScenarioType.DEPRESSION_SUPPORT: {
                "title": "Finding Light in Darkness",
                "base_description": "Work through depressive thoughts and feelings with therapeutic support",
                "therapeutic_goals": [
                    "mood_improvement",
                    "behavioral_activation",
                    "hope_building",
                ],
                "practice_opportunities": [
                    "activity_scheduling",
                    "thought_challenging",
                    "self_compassion",
                ],
                "reflection_prompts": [
                    "What small step can you take?",
                    "What are you grateful for?",
                    "How can you be kind to yourself?",
                ],
                "estimated_duration": 20,
            },
            ScenarioType.RELATIONSHIP_SKILLS: {
                "title": "Building Connections",
                "base_description": "Practice interpersonal skills in relationship scenarios",
                "therapeutic_goals": [
                    "communication_improvement",
                    "boundary_setting",
                    "empathy_development",
                ],
                "practice_opportunities": [
                    "active_listening",
                    "assertiveness",
                    "conflict_resolution",
                ],
                "reflection_prompts": [
                    "How did you communicate?",
                    "What boundaries are important?",
                    "How did you show empathy?",
                ],
                "estimated_duration": 18,
            },
            ScenarioType.EMOTIONAL_REGULATION: {
                "title": "Mastering Emotions",
                "base_description": "Learn to understand and regulate emotional responses",
                "therapeutic_goals": [
                    "emotional_awareness",
                    "regulation_skills",
                    "distress_tolerance",
                ],
                "practice_opportunities": [
                    "emotion_identification",
                    "coping_strategies",
                    "mindfulness",
                ],
                "reflection_prompts": [
                    "What emotion did you feel?",
                    "What triggered it?",
                    "What helped you cope?",
                ],
                "estimated_duration": 16,
            },
            ScenarioType.CONFIDENCE_BUILDING: {
                "title": "Stepping Into Power",
                "base_description": "Build confidence through challenging but supportive scenarios",
                "therapeutic_goals": [
                    "self_efficacy",
                    "courage_development",
                    "positive_self_talk",
                ],
                "practice_opportunities": [
                    "assertiveness_training",
                    "success_visualization",
                    "strength_identification",
                ],
                "reflection_prompts": [
                    "What strengths did you use?",
                    "How did you feel afterward?",
                    "What would you tell a friend?",
                ],
                "estimated_duration": 14,
            },
        }

    def _analyze_user_context(
        self,
        user_id: str,
        therapeutic_goals: list[str] | None,
        character_data: dict[str, Any] | None,
        user_progress: dict[str, Any] | None,
        emotional_state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Analyze user context for personalized recommendations."""
        context = {
            "user_id": user_id,
            "therapeutic_goals": therapeutic_goals or [],
            "character_strengths": [],
            "character_growth_areas": [],
            "emotional_stability": 0.7,  # Default
            "crisis_risk": False,
            "preferred_frameworks": [],
            "difficulty_preference": "moderate",
        }

        # Analyze character data
        if character_data and "attributes" in character_data:
            attributes = character_data["attributes"]
            if isinstance(attributes, dict):
                # Find top 3 attributes (strengths)
                sorted_attrs = sorted(
                    attributes.items(), key=lambda x: x[1], reverse=True
                )
                context["character_strengths"] = [attr[0] for attr in sorted_attrs[:3]]

                # Find bottom 3 attributes (growth areas)
                context["character_growth_areas"] = [
                    attr[0] for attr in sorted_attrs[-3:]
                ]

        # Analyze emotional state
        if emotional_state:
            context["emotional_stability"] = emotional_state.get(
                "emotional_stability", 0.7
            )
            context["crisis_risk"] = emotional_state.get("crisis_detected", False)

        # Analyze user progress
        if user_progress:
            context["difficulty_preference"] = user_progress.get(
                "preferred_difficulty", "moderate"
            )
            context["preferred_frameworks"] = user_progress.get(
                "successful_frameworks", []
            )

        return context

    def _calculate_framework_suitability(
        self, user_context: dict[str, Any]
    ) -> dict[TherapeuticFramework, float]:
        """Calculate suitability scores for each therapeutic framework."""
        scores = {}

        for framework, config in self.framework_configurations.items():
            score = 0.5  # Base score

            # Goal alignment bonus
            therapeutic_goals = user_context.get("therapeutic_goals", [])
            for goal in therapeutic_goals:
                if goal in config["suitable_for"]:
                    score += 0.2

            # Character attribute alignment
            character_strengths = user_context.get("character_strengths", [])
            for strength in character_strengths:
                if strength in config["character_attributes"]:
                    score += 0.1

            # Crisis risk adjustment
            if user_context.get("crisis_risk", False):
                if framework in [
                    TherapeuticFramework.DBT,
                    TherapeuticFramework.MINDFULNESS,
                ]:
                    score += 0.3  # Prioritize stabilizing frameworks
                else:
                    score -= 0.2  # Deprioritize complex frameworks during crisis

            # Previous success bonus
            preferred_frameworks = user_context.get("preferred_frameworks", [])
            if framework.value in preferred_frameworks:
                score += 0.25

            # Emotional stability consideration
            emotional_stability = user_context.get("emotional_stability", 0.7)
            if emotional_stability < 0.5:
                # Prioritize stabilizing frameworks for low emotional stability
                if framework in [
                    TherapeuticFramework.DBT,
                    TherapeuticFramework.MINDFULNESS,
                    TherapeuticFramework.HUMANISTIC,
                ]:
                    score += 0.2

            scores[framework] = min(1.0, max(0.0, score))  # Clamp to 0-1 range

        return scores

    def _create_recommendation(
        self,
        user_id: str,
        framework: TherapeuticFramework,
        score: float,
        user_context: dict[str, Any],
    ) -> TherapeuticRecommendation:
        """Create a therapeutic recommendation."""
        config = self.framework_configurations[framework]

        # Determine scenario type based on therapeutic goals
        therapeutic_goals = user_context.get("therapeutic_goals", [])
        scenario_type = self._determine_scenario_type(therapeutic_goals, framework)

        # Determine integration strategy
        integration_strategy = self._determine_integration_strategy(
            user_context, framework
        )

        # Calculate character alignment
        character_alignment = self._calculate_character_alignment(
            user_context, framework
        )

        # Generate rationale
        rationale = self._generate_recommendation_rationale(
            framework, score, user_context
        )

        return TherapeuticRecommendation(
            recommendation_id=str(uuid4()),
            user_id=user_id,
            framework=framework,
            scenario_type=scenario_type,
            integration_strategy=integration_strategy,
            priority_score=score,
            rationale=rationale,
            expected_outcomes=config["techniques"][:3],  # Top 3 techniques as outcomes
            estimated_duration=self._estimate_duration(framework, scenario_type),
            difficulty_level=user_context.get("difficulty_preference", "moderate"),
            character_alignment=character_alignment,
        )

    def _determine_scenario_type(
        self, therapeutic_goals: list[str], framework: TherapeuticFramework
    ) -> ScenarioType:
        """Determine appropriate scenario type based on goals and framework."""
        # Goal to scenario type mapping
        goal_mappings = {
            "anxiety_management": ScenarioType.ANXIETY_MANAGEMENT,
            "depression_support": ScenarioType.DEPRESSION_SUPPORT,
            "confidence_building": ScenarioType.CONFIDENCE_BUILDING,
            "emotional_regulation": ScenarioType.EMOTIONAL_REGULATION,
            "communication_skills": ScenarioType.RELATIONSHIP_SKILLS,
            "social_skills": ScenarioType.RELATIONSHIP_SKILLS,
            "stress_management": ScenarioType.ANXIETY_MANAGEMENT,
        }

        # Check for direct goal matches
        for goal in therapeutic_goals:
            if goal in goal_mappings:
                return goal_mappings[goal]

        # Framework-based defaults
        framework_defaults = {
            TherapeuticFramework.CBT: ScenarioType.ANXIETY_MANAGEMENT,
            TherapeuticFramework.DBT: ScenarioType.EMOTIONAL_REGULATION,
            TherapeuticFramework.ACT: ScenarioType.CONFIDENCE_BUILDING,
            TherapeuticFramework.MINDFULNESS: ScenarioType.ANXIETY_MANAGEMENT,
            TherapeuticFramework.HUMANISTIC: ScenarioType.CONFIDENCE_BUILDING,
            TherapeuticFramework.PSYCHODYNAMIC: ScenarioType.RELATIONSHIP_SKILLS,
            TherapeuticFramework.SOLUTION_FOCUSED: ScenarioType.CONFIDENCE_BUILDING,
            TherapeuticFramework.NARRATIVE_THERAPY: ScenarioType.RELATIONSHIP_SKILLS,
        }

        return framework_defaults.get(framework, ScenarioType.CONFIDENCE_BUILDING)

    def _determine_integration_strategy(
        self, user_context: dict[str, Any], framework: TherapeuticFramework
    ) -> IntegrationStrategy:
        """Determine appropriate integration strategy."""
        # Crisis situations need direct, supportive approaches
        if user_context.get("crisis_risk", False):
            return IntegrationStrategy.DIRECT_TEACHING

        # Low emotional stability benefits from experiential learning
        if user_context.get("emotional_stability", 0.7) < 0.5:
            return IntegrationStrategy.EXPERIENTIAL_LEARNING

        # Framework-based strategy preferences
        framework_strategies = {
            TherapeuticFramework.CBT: IntegrationStrategy.SKILL_PRACTICE,
            TherapeuticFramework.DBT: IntegrationStrategy.EXPERIENTIAL_LEARNING,
            TherapeuticFramework.ACT: IntegrationStrategy.METAPHORICAL_EMBEDDING,
            TherapeuticFramework.MINDFULNESS: IntegrationStrategy.EXPERIENTIAL_LEARNING,
            TherapeuticFramework.HUMANISTIC: IntegrationStrategy.COLLABORATIVE_EXPLORATION,
            TherapeuticFramework.PSYCHODYNAMIC: IntegrationStrategy.REFLECTION_PROMPTING,
            TherapeuticFramework.SOLUTION_FOCUSED: IntegrationStrategy.SKILL_PRACTICE,
            TherapeuticFramework.NARRATIVE_THERAPY: IntegrationStrategy.METAPHORICAL_EMBEDDING,
        }

        return framework_strategies.get(
            framework, IntegrationStrategy.EXPERIENTIAL_LEARNING
        )

    def _calculate_character_alignment(
        self, user_context: dict[str, Any], framework: TherapeuticFramework
    ) -> dict[str, float]:
        """Calculate character attribute alignment with framework."""
        config = self.framework_configurations[framework]
        framework_attributes = config["character_attributes"]
        character_strengths = user_context.get("character_strengths", [])

        alignment = {}
        for attr in framework_attributes:
            if attr in character_strengths:
                alignment[attr] = 0.8  # High alignment
            else:
                alignment[attr] = 0.4  # Growth opportunity

        return alignment

    def _generate_recommendation_rationale(
        self,
        framework: TherapeuticFramework,
        score: float,
        user_context: dict[str, Any],
    ) -> str:
        """Generate human-readable rationale for recommendation."""
        config = self.framework_configurations[framework]
        framework_name = config["name"]

        rationale_parts = [f"{framework_name} is recommended (score: {score:.2f})"]

        # Add goal alignment
        therapeutic_goals = user_context.get("therapeutic_goals", [])
        matching_goals = [
            goal for goal in therapeutic_goals if goal in config["suitable_for"]
        ]
        if matching_goals:
            rationale_parts.append(
                f"aligns with your goals: {', '.join(matching_goals)}"
            )

        # Add character strengths
        character_strengths = user_context.get("character_strengths", [])
        matching_strengths = [
            strength
            for strength in character_strengths
            if strength in config["character_attributes"]
        ]
        if matching_strengths:
            rationale_parts.append(
                f"builds on your strengths: {', '.join(matching_strengths)}"
            )

        # Add crisis consideration
        if user_context.get("crisis_risk", False):
            rationale_parts.append(
                "provides stabilizing support during difficult times"
            )

        return " because it " + ", and ".join(rationale_parts[1:]) + "."

    def _estimate_duration(
        self, framework: TherapeuticFramework, scenario_type: ScenarioType
    ) -> int:
        """Estimate duration for framework and scenario combination."""
        base_durations = {
            ScenarioType.ANXIETY_MANAGEMENT: 15,
            ScenarioType.DEPRESSION_SUPPORT: 20,
            ScenarioType.RELATIONSHIP_SKILLS: 18,
            ScenarioType.EMOTIONAL_REGULATION: 16,
            ScenarioType.CONFIDENCE_BUILDING: 14,
        }

        framework_modifiers = {
            TherapeuticFramework.CBT: 1.0,
            TherapeuticFramework.DBT: 1.2,
            TherapeuticFramework.ACT: 1.1,
            TherapeuticFramework.MINDFULNESS: 0.9,
            TherapeuticFramework.HUMANISTIC: 1.1,
            TherapeuticFramework.PSYCHODYNAMIC: 1.3,
            TherapeuticFramework.SOLUTION_FOCUSED: 0.8,
            TherapeuticFramework.NARRATIVE_THERAPY: 1.2,
        }

        base_duration = base_durations.get(scenario_type, 15)
        modifier = framework_modifiers.get(framework, 1.0)

        return int(base_duration * modifier)

    def _get_scenario_template(
        self, framework: TherapeuticFramework, scenario_type: ScenarioType
    ) -> dict[str, Any]:
        """Get scenario template for framework and type combination."""
        base_template = self.scenario_templates.get(scenario_type, {})
        framework_config = self.framework_configurations.get(framework, {})

        # Merge template with framework-specific elements
        template = base_template.copy()
        template["framework"] = framework
        template["framework_techniques"] = framework_config.get("techniques", [])
        template["framework_focus"] = framework_config.get(
            "focus", "general_therapeutic_support"
        )

        return template

    def _personalize_scenario(
        self,
        template: dict[str, Any],
        character_data: dict[str, Any] | None,
        difficulty_level: str | None,
        session_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Personalize scenario based on character data and context."""
        personalized = template.copy()

        # Personalize title and description
        if character_data and "name" in character_data:
            character_data["name"]

        personalized["title"] = template.get("title", "Therapeutic Journey")
        personalized["description"] = template.get(
            "base_description", "A therapeutic scenario tailored for growth"
        )

        # Create narrative context
        personalized["narrative_context"] = self._create_narrative_context(
            template, character_data, difficulty_level
        )

        # Adapt practice opportunities based on difficulty
        base_opportunities = template.get("practice_opportunities", [])
        personalized["practice_opportunities"] = self._adapt_practice_opportunities(
            base_opportunities, difficulty_level
        )

        # Create character involvement
        personalized["character_involvement"] = self._create_character_involvement(
            character_data, template
        )

        # Set success criteria
        personalized["success_criteria"] = self._create_success_criteria(
            template, difficulty_level
        )

        # Copy other template fields
        personalized["therapeutic_goals"] = template.get("therapeutic_goals", [])
        personalized["reflection_prompts"] = template.get("reflection_prompts", [])
        personalized["estimated_duration"] = template.get("estimated_duration", 15)

        return personalized

    def _create_narrative_context(
        self,
        template: dict[str, Any],
        character_data: dict[str, Any] | None,
        difficulty_level: str | None,
    ) -> str:
        """Create narrative context for the scenario."""
        framework = template.get("framework", TherapeuticFramework.CBT)
        scenario_focus = template.get("framework_focus", "therapeutic_growth")

        context_parts = [
            f"In this therapeutic scenario, you'll explore {scenario_focus}",
            f"using {framework.value.replace('_', ' ')} approaches.",
        ]

        if character_data and "name" in character_data:
            context_parts.append(
                f"Your character {character_data['name']} will guide you through this journey."
            )

        if difficulty_level:
            difficulty_descriptions = {
                "very_easy": "with gentle, supportive guidance",
                "easy": "with supportive guidance and encouragement",
                "moderate": "with balanced challenge and support",
                "challenging": "with meaningful challenges to promote growth",
                "hard": "with significant challenges for advanced growth",
                "very_hard": "with complex challenges for deep transformation",
            }
            context_parts.append(
                difficulty_descriptions.get(
                    difficulty_level, "with appropriate support"
                )
            )

        return " ".join(context_parts)

    def _adapt_practice_opportunities(
        self, base_opportunities: list[str], difficulty_level: str | None
    ) -> list[str]:
        """Adapt practice opportunities based on difficulty level."""
        if not difficulty_level or difficulty_level in ["moderate", "challenging"]:
            return base_opportunities

        if difficulty_level in ["very_easy", "easy"]:
            # Simplify opportunities for easier levels
            simplified = []
            for opportunity in base_opportunities[:2]:  # Limit to 2 opportunities
                simplified.append(f"guided_{opportunity}")
            return simplified

        if difficulty_level in ["hard", "very_hard"]:
            # Add advanced opportunities for harder levels
            advanced = base_opportunities.copy()
            advanced.extend(
                ["advanced_integration", "complex_application", "independent_practice"]
            )
            return advanced

        return base_opportunities

    def _create_character_involvement(
        self, character_data: dict[str, Any] | None, template: dict[str, Any]
    ) -> dict[str, str]:
        """Create character involvement in the scenario."""
        involvement = {
            "role": "therapeutic_guide",
            "interaction_style": "supportive_companion",
            "guidance_level": "moderate",
        }

        if character_data and "attributes" in character_data:
            attributes = character_data["attributes"]
            if isinstance(attributes, dict):
                # Adapt involvement based on character strengths
                if attributes.get("empathy", 5.0) > 7.0:
                    involvement["interaction_style"] = "empathetic_supporter"
                if attributes.get("wisdom", 5.0) > 7.0:
                    involvement["guidance_level"] = "wise_mentor"
                if attributes.get("courage", 5.0) > 7.0:
                    involvement["role"] = "brave_companion"

        return involvement

    def _create_success_criteria(
        self, template: dict[str, Any], difficulty_level: str | None
    ) -> list[str]:
        """Create success criteria for the scenario."""
        base_criteria = [
            "Engage with therapeutic concepts",
            "Practice new skills or insights",
            "Reflect on the experience",
        ]

        if difficulty_level in ["hard", "very_hard"]:
            base_criteria.extend(
                [
                    "Demonstrate skill integration",
                    "Apply learning to personal situations",
                    "Show evidence of therapeutic growth",
                ]
            )
        elif difficulty_level in ["very_easy", "easy"]:
            base_criteria = [
                "Participate in the scenario",
                "Try one new therapeutic technique",
                "Share one insight or feeling",
            ]

        return base_criteria

    def _create_fallback_recommendation(
        self, user_id: str
    ) -> TherapeuticRecommendation:
        """Create a fallback recommendation when generation fails."""
        return TherapeuticRecommendation(
            recommendation_id=str(uuid4()),
            user_id=user_id,
            framework=TherapeuticFramework.MINDFULNESS,
            scenario_type=ScenarioType.CONFIDENCE_BUILDING,
            integration_strategy=IntegrationStrategy.EXPERIENTIAL_LEARNING,
            priority_score=0.6,
            rationale="Mindfulness-based confidence building provides a gentle, supportive therapeutic approach.",
            expected_outcomes=[
                "stress_reduction",
                "self_awareness",
                "emotional_regulation",
            ],
            estimated_duration=15,
            difficulty_level="moderate",
            character_alignment={"mindfulness": 0.7, "confidence": 0.6},
        )

    def _create_fallback_scenario(
        self, user_id: str, framework: TherapeuticFramework, scenario_type: ScenarioType
    ) -> TherapeuticScenario:
        """Create a fallback scenario when generation fails."""
        return TherapeuticScenario(
            scenario_id=str(uuid4()),
            user_id=user_id,
            framework=framework,
            scenario_type=scenario_type,
            title="Therapeutic Growth Journey",
            description="A supportive therapeutic scenario designed for personal growth and healing.",
            narrative_context="Explore therapeutic concepts in a safe, supportive environment.",
            therapeutic_goals=[
                "personal_growth",
                "self_awareness",
                "emotional_wellbeing",
            ],
            practice_opportunities=[
                "mindful_reflection",
                "gentle_exploration",
                "supportive_practice",
            ],
            reflection_prompts=[
                "How are you feeling?",
                "What did you notice?",
                "What would help you?",
            ],
            success_criteria=[
                "Participate with openness",
                "Practice self-compassion",
                "Take one small step",
            ],
            character_involvement={
                "role": "supportive_guide",
                "interaction_style": "gentle_companion",
            },
            difficulty_level="moderate",
            estimated_duration=15,
        )

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the therapeutic integration system."""
        try:
            return {
                "status": "healthy",
                "frameworks_supported": len(TherapeuticFramework),
                "integration_strategies": len(IntegrationStrategy),
                "scenario_types": len(ScenarioType),
                "users_with_recommendations": len(self.user_recommendations),
                "total_scenarios_generated": len(
                    [
                        s
                        for scenarios in self.generated_scenarios.values()
                        for s in scenarios
                    ]
                ),
                "framework_configurations": len(self.framework_configurations),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in therapeutic integration system health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get therapeutic integration system metrics."""
        # Calculate additional metrics
        total_recommendations = sum(
            len(recs) for recs in self.user_recommendations.values()
        )
        total_scenarios = sum(
            len(scenarios) for scenarios in self.generated_scenarios.values()
        )

        average_recommendation_score = 0.0
        if total_recommendations > 0:
            all_scores = [
                rec.priority_score
                for recs in self.user_recommendations.values()
                for rec in recs
            ]
            average_recommendation_score = sum(all_scores) / len(all_scores)

        return {
            **self.metrics,
            "total_recommendations": total_recommendations,
            "total_scenarios": total_scenarios,
            "average_recommendation_score": round(average_recommendation_score, 2),
            "frameworks_supported": len(TherapeuticFramework),
            "integration_strategies_available": len(IntegrationStrategy),
            "scenario_types_available": len(ScenarioType),
            "users_served": len(self.user_recommendations),
        }
