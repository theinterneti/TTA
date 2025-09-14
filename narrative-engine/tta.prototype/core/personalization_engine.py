"""
Personalization Engine and Content Adaptation System for TTA Prototype

This module implements the personalization engine that adapts therapeutic content
and narrative experiences based on user profiles, preferences, progress patterns,
and therapeutic needs. It provides intelligent content adaptation, recommendation
systems, and personalized therapeutic interventions.

Classes:
    PersonalizationEngine: Main engine for content personalization
    ContentAdaptationSystem: Adapts content based on user characteristics
    RecommendationSystem: Generates personalized therapeutic recommendations
    UserProfileAnalyzer: Analyzes user profiles for personalization insights
    AdaptiveNarrativeGenerator: Creates personalized narrative content
"""

import logging
import statistics

# Import system components
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
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
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticGoal,
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
    from .progress_tracking_personalization import (
        PersonalizationDimension,
        PersonalizationProfile,
        ProgressAnalysisResult,
        ProgressMetric,
        ProgressMetricType,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            CharacterState,
            CopingStrategy,
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticGoal,
            TherapeuticProgress,
            ValidationError,
        )
        from progress_tracking_personalization import (
            PersonalizationDimension,
            PersonalizationProfile,
            ProgressAnalysisResult,
            ProgressMetric,
            ProgressMetricType,
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
        TherapeuticLLMClient = MockClass
        PersonalizationProfile = MockClass
        ProgressAnalysisResult = MockClass

logger = logging.getLogger(__name__)


class ContentAdaptationType(Enum):
    """Types of content adaptation."""
    DIFFICULTY_ADJUSTMENT = "difficulty_adjustment"
    PACING_MODIFICATION = "pacing_modification"
    STYLE_ADAPTATION = "style_adaptation"
    EMOTIONAL_TONE_ADJUSTMENT = "emotional_tone_adjustment"
    INTERVENTION_SELECTION = "intervention_selection"
    NARRATIVE_FOCUS = "narrative_focus"
    CHARACTER_INTERACTION = "character_interaction"
    THERAPEUTIC_APPROACH = "therapeutic_approach"


class RecommendationType(Enum):
    """Types of recommendations."""
    NEXT_INTERVENTION = "next_intervention"
    CONTENT_FOCUS = "content_focus"
    SESSION_STRUCTURE = "session_structure"
    THERAPEUTIC_GOAL = "therapeutic_goal"
    COPING_STRATEGY = "coping_strategy"
    NARRATIVE_PATH = "narrative_path"
    CHARACTER_INTERACTION = "character_interaction"
    SKILL_DEVELOPMENT = "skill_development"


@dataclass
class PersonalizationContext:
    """Context information for personalization decisions."""
    user_id: str
    session_state: SessionState
    personalization_profile: PersonalizationProfile
    progress_analysis: ProgressAnalysisResult | None = None
    current_emotional_state: EmotionalState | None = None
    recent_interactions: list[dict[str, Any]] = field(default_factory=list)
    environmental_factors: dict[str, Any] = field(default_factory=dict)
    time_context: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate personalization context."""
        if not self.user_id.strip():
            raise ValidationError("User ID cannot be empty")
        if not self.session_state:
            raise ValidationError("Session state is required")
        if not self.personalization_profile:
            raise ValidationError("Personalization profile is required")
        return True


@dataclass
class ContentAdaptation:
    """Represents a content adaptation decision."""
    adaptation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    adaptation_type: ContentAdaptationType = ContentAdaptationType.DIFFICULTY_ADJUSTMENT
    original_content: dict[str, Any] = field(default_factory=dict)
    adapted_content: dict[str, Any] = field(default_factory=dict)
    adaptation_rationale: str = ""
    confidence_score: float = 0.8  # 0.0 to 1.0
    expected_impact: str = ""
    adaptation_parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate content adaptation."""
        if not self.adaptation_rationale.strip():
            raise ValidationError("Adaptation rationale cannot be empty")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        return True


@dataclass
class PersonalizedRecommendation:
    """Represents a personalized recommendation."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recommendation_type: RecommendationType = RecommendationType.NEXT_INTERVENTION
    title: str = ""
    description: str = ""
    rationale: str = ""
    priority_score: float = 0.5  # 0.0 to 1.0
    confidence_level: float = 0.8  # 0.0 to 1.0
    expected_benefit: str = ""
    implementation_steps: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    estimated_duration: int = 15  # minutes
    success_metrics: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate personalized recommendation."""
        if not self.title.strip():
            raise ValidationError("Recommendation title cannot be empty")
        if not self.description.strip():
            raise ValidationError("Recommendation description cannot be empty")
        if not 0.0 <= self.priority_score <= 1.0:
            raise ValidationError("Priority score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        if self.estimated_duration <= 0:
            raise ValidationError("Estimated duration must be positive")
        return True


class UserProfileAnalyzer:
    """Analyzes user profiles for personalization insights."""

    def __init__(self):
        """Initialize the user profile analyzer."""
        self.analysis_weights = self._initialize_analysis_weights()
        logger.info("UserProfileAnalyzer initialized")

    def _initialize_analysis_weights(self) -> dict[str, float]:
        """Initialize weights for different analysis factors."""
        return {
            "learning_velocity": 0.25,
            "engagement_patterns": 0.20,
            "therapeutic_preferences": 0.20,
            "emotional_patterns": 0.15,
            "progress_trends": 0.10,
            "interaction_history": 0.10
        }

    def analyze_user_characteristics(self, profile: PersonalizationProfile,
                                   progress_analysis: ProgressAnalysisResult | None = None) -> dict[str, Any]:
        """Analyze user characteristics for personalization."""
        characteristics = {
            "learning_style": self._determine_learning_style(profile),
            "engagement_preferences": self._analyze_engagement_preferences(profile),
            "therapeutic_readiness": self._assess_therapeutic_readiness(profile, progress_analysis),
            "content_preferences": self._determine_content_preferences(profile),
            "interaction_style": self._analyze_interaction_style(profile),
            "pacing_preferences": self._determine_pacing_preferences(profile),
            "support_needs": self._assess_support_needs(profile, progress_analysis),
            "motivation_factors": self._identify_motivation_factors(profile)
        }

        return characteristics

    def _determine_learning_style(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Determine user's learning style preferences."""
        learning_velocity = profile.learning_velocity

        # Map learning velocity to learning style preferences
        if learning_velocity < 0.3:
            return {
                "visual": 0.8,
                "step_by_step": 0.9,
                "repetitive": 0.7,
                "interactive": 0.6,
                "self_paced": 0.8
            }
        elif learning_velocity > 0.7:
            return {
                "conceptual": 0.8,
                "exploratory": 0.9,
                "challenge_seeking": 0.8,
                "independent": 0.7,
                "fast_paced": 0.8
            }
        else:
            return {
                "balanced": 0.8,
                "adaptive": 0.7,
                "guided": 0.6,
                "moderate_pace": 0.7,
                "mixed_methods": 0.8
            }

    def _analyze_engagement_preferences(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Analyze user's engagement preferences."""
        engagement_history = profile.engagement_patterns.get("engagement", [])

        if not engagement_history:
            return {"unknown": 1.0}

        avg_engagement = statistics.mean(engagement_history)
        engagement_stability = 1.0 - (statistics.stdev(engagement_history) if len(engagement_history) > 1 else 0.0)

        preferences = {
            "high_interaction": avg_engagement,
            "consistent_engagement": engagement_stability,
            "variety_seeking": 1.0 - engagement_stability,
            "sustained_focus": min(1.0, profile.optimal_session_length / 60.0),
            "frequent_feedback": 1.0 - engagement_stability
        }

        return preferences

    def _assess_therapeutic_readiness(self, profile: PersonalizationProfile,
                                    progress_analysis: ProgressAnalysisResult | None) -> dict[str, float]:
        """Assess user's readiness for different therapeutic approaches."""
        readiness = {
            "basic_interventions": 0.8,  # Most users ready for basic interventions
            "advanced_techniques": 0.3,  # Default low readiness for advanced
            "challenging_content": 0.4,
            "self_reflection": 0.6,
            "behavioral_change": 0.5
        }

        if progress_analysis:
            overall_progress = progress_analysis.overall_progress_score

            # Adjust readiness based on progress
            readiness["advanced_techniques"] = min(1.0, overall_progress + 0.2)
            readiness["challenging_content"] = min(1.0, overall_progress + 0.1)
            readiness["behavioral_change"] = min(1.0, overall_progress + 0.3)

            # High performers ready for more challenging content
            if overall_progress > 0.7:
                readiness["self_reflection"] = 0.9
                readiness["challenging_content"] = 0.8

        # Adjust based on learning velocity
        if profile.learning_velocity > 0.6:
            readiness["advanced_techniques"] += 0.2
            readiness["challenging_content"] += 0.2

        # Clamp values to [0, 1]
        return {k: max(0.0, min(1.0, v)) for k, v in readiness.items()}

    def _determine_content_preferences(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Determine user's content preferences."""
        preferences = {
            "narrative_heavy": 0.7,
            "dialogue_focused": 0.6,
            "action_oriented": 0.5,
            "reflective": 0.6,
            "educational": 0.5,
            "emotional": 0.7,
            "practical": 0.8,
            "metaphorical": 0.4
        }

        # Adjust based on preferred interventions
        if InterventionType.MINDFULNESS in profile.preferred_intervention_types:
            preferences["reflective"] = 0.9
            preferences["emotional"] = 0.8

        if InterventionType.BEHAVIORAL_ACTIVATION in profile.preferred_intervention_types:
            preferences["action_oriented"] = 0.9
            preferences["practical"] = 0.9

        if InterventionType.COGNITIVE_RESTRUCTURING in profile.preferred_intervention_types:
            preferences["educational"] = 0.8
            preferences["reflective"] = 0.8

        return preferences

    def _analyze_interaction_style(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Analyze user's preferred interaction style."""
        base_style = {
            "formal": 0.3,
            "casual": 0.7,
            "supportive": 0.8,
            "challenging": 0.4,
            "directive": 0.5,
            "collaborative": 0.7,
            "empathetic": 0.8,
            "analytical": 0.5
        }

        # Adjust based on learning velocity
        if profile.learning_velocity < 0.4:
            base_style["supportive"] = 0.9
            base_style["directive"] = 0.7
            base_style["empathetic"] = 0.9
        elif profile.learning_velocity > 0.7:
            base_style["challenging"] = 0.7
            base_style["analytical"] = 0.8
            base_style["collaborative"] = 0.8

        return base_style

    def _determine_pacing_preferences(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Determine user's pacing preferences."""
        profile.optimal_session_length / 30.0  # Normalize to 30 min baseline
        learning_velocity = profile.learning_velocity

        return {
            "slow_paced": max(0.0, 1.0 - learning_velocity),
            "moderate_paced": 1.0 - abs(learning_velocity - 0.5) * 2,
            "fast_paced": learning_velocity,
            "variable_paced": 0.6,
            "user_controlled": 0.7,
            "structured": max(0.0, 1.0 - learning_velocity * 0.5),
            "flexible": learning_velocity * 0.8 + 0.2
        }

    def _assess_support_needs(self, profile: PersonalizationProfile,
                            progress_analysis: ProgressAnalysisResult | None) -> dict[str, float]:
        """Assess user's support needs."""
        support_needs = {
            "high_guidance": 0.6,
            "frequent_encouragement": 0.7,
            "detailed_explanations": 0.6,
            "progress_feedback": 0.8,
            "crisis_support": 0.3,
            "peer_connection": 0.4,
            "professional_referral": 0.2
        }

        # Adjust based on learning velocity
        if profile.learning_velocity < 0.3:
            support_needs["high_guidance"] = 0.9
            support_needs["frequent_encouragement"] = 0.9
            support_needs["detailed_explanations"] = 0.8

        # Adjust based on progress
        if progress_analysis:
            if progress_analysis.overall_progress_score < 0.3:
                support_needs["frequent_encouragement"] = 0.9
                support_needs["crisis_support"] = 0.6

            if len(progress_analysis.areas_for_improvement) > 3:
                support_needs["high_guidance"] = 0.8
                support_needs["detailed_explanations"] = 0.8

        return support_needs

    def _identify_motivation_factors(self, profile: PersonalizationProfile) -> dict[str, float]:
        """Identify factors that motivate the user."""
        motivation_factors = {
            "achievement": 0.7,
            "progress_tracking": 0.8,
            "social_recognition": 0.4,
            "personal_growth": 0.8,
            "skill_mastery": 0.6,
            "problem_solving": 0.6,
            "helping_others": 0.5,
            "autonomy": 0.7,
            "competence": 0.7,
            "relatedness": 0.6
        }

        # Adjust based on learning velocity and preferences
        if profile.learning_velocity > 0.6:
            motivation_factors["achievement"] = 0.9
            motivation_factors["skill_mastery"] = 0.8
            motivation_factors["problem_solving"] = 0.8

        if profile.optimal_session_length > 40:
            motivation_factors["personal_growth"] = 0.9
            motivation_factors["autonomy"] = 0.8

        return motivation_factors


class ContentAdaptationSystem:
    """Adapts content based on user characteristics and preferences."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the content adaptation system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.adaptation_strategies = self._initialize_adaptation_strategies()
        logger.info("ContentAdaptationSystem initialized")

    def _initialize_adaptation_strategies(self) -> dict[ContentAdaptationType, dict[str, Any]]:
        """Initialize adaptation strategies for different content types."""
        return {
            ContentAdaptationType.DIFFICULTY_ADJUSTMENT: {
                "parameters": ["complexity_level", "vocabulary_level", "concept_depth"],
                "methods": ["simplify", "elaborate", "provide_examples", "add_scaffolding"]
            },
            ContentAdaptationType.PACING_MODIFICATION: {
                "parameters": ["content_chunks", "pause_points", "review_frequency"],
                "methods": ["break_down", "combine", "add_breaks", "accelerate"]
            },
            ContentAdaptationType.STYLE_ADAPTATION: {
                "parameters": ["formality", "tone", "perspective", "voice"],
                "methods": ["adjust_tone", "change_perspective", "modify_voice", "adapt_style"]
            },
            ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT: {
                "parameters": ["emotional_intensity", "supportiveness", "challenge_level"],
                "methods": ["soften_tone", "increase_support", "add_encouragement", "adjust_challenge"]
            }
        }

    def adapt_content(self, content: dict[str, Any], context: PersonalizationContext) -> ContentAdaptation:
        """Adapt content based on personalization context."""
        try:
            # Analyze user characteristics
            profile_analyzer = UserProfileAnalyzer()
            user_characteristics = profile_analyzer.analyze_user_characteristics(
                context.personalization_profile, context.progress_analysis
            )

            # Determine adaptation needs
            adaptation_needs = self._assess_adaptation_needs(content, user_characteristics, context)

            # Select primary adaptation type
            primary_adaptation = self._select_primary_adaptation(adaptation_needs)

            # Apply adaptations
            adapted_content = self._apply_adaptations(content, primary_adaptation, user_characteristics, context)

            # Create adaptation record
            adaptation = ContentAdaptation(
                adaptation_type=primary_adaptation,
                original_content=content,
                adapted_content=adapted_content,
                adaptation_rationale=self._generate_adaptation_rationale(primary_adaptation, user_characteristics),
                confidence_score=self._calculate_adaptation_confidence(adaptation_needs, user_characteristics),
                expected_impact=self._predict_adaptation_impact(primary_adaptation, user_characteristics),
                adaptation_parameters=adaptation_needs
            )

            adaptation.validate()
            logger.info(f"Content adapted using {primary_adaptation.value} for user {context.user_id}")
            return adaptation

        except Exception as e:
            logger.error(f"Error adapting content for user {context.user_id}: {e}")
            # Return original content as fallback
            return ContentAdaptation(
                original_content=content,
                adapted_content=content,
                adaptation_rationale="Fallback: No adaptation applied due to error",
                confidence_score=0.0
            )

    def _assess_adaptation_needs(self, content: dict[str, Any],
                               user_characteristics: dict[str, Any],
                               context: PersonalizationContext) -> dict[ContentAdaptationType, float]:
        """Assess what types of adaptations are needed."""
        needs = {}

        # Difficulty adjustment needs
        learning_style = user_characteristics.get("learning_style", {})
        user_characteristics.get("therapeutic_readiness", {})

        if learning_style.get("step_by_step", 0) > 0.7:
            needs[ContentAdaptationType.DIFFICULTY_ADJUSTMENT] = 0.8
        elif learning_style.get("challenge_seeking", 0) > 0.7:
            needs[ContentAdaptationType.DIFFICULTY_ADJUSTMENT] = 0.6
        else:
            needs[ContentAdaptationType.DIFFICULTY_ADJUSTMENT] = 0.4

        # Pacing modification needs
        pacing_prefs = user_characteristics.get("pacing_preferences", {})
        if pacing_prefs.get("slow_paced", 0) > 0.7:
            needs[ContentAdaptationType.PACING_MODIFICATION] = 0.8
        elif pacing_prefs.get("fast_paced", 0) > 0.7:
            needs[ContentAdaptationType.PACING_MODIFICATION] = 0.7
        else:
            needs[ContentAdaptationType.PACING_MODIFICATION] = 0.3

        # Style adaptation needs
        interaction_style = user_characteristics.get("interaction_style", {})
        if interaction_style.get("formal", 0) > 0.7 or interaction_style.get("casual", 0) > 0.7:
            needs[ContentAdaptationType.STYLE_ADAPTATION] = 0.6
        else:
            needs[ContentAdaptationType.STYLE_ADAPTATION] = 0.3

        # Emotional tone adjustment needs
        support_needs = user_characteristics.get("support_needs", {})
        if support_needs.get("frequent_encouragement", 0) > 0.7:
            needs[ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT] = 0.8
        elif context.current_emotional_state and context.current_emotional_state.primary_emotion in [
            EmotionalStateType.ANXIOUS, EmotionalStateType.DEPRESSED, EmotionalStateType.OVERWHELMED
        ]:
            needs[ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT] = 0.9
        else:
            needs[ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT] = 0.4

        return needs

    def _select_primary_adaptation(self, adaptation_needs: dict[ContentAdaptationType, float]) -> ContentAdaptationType:
        """Select the primary adaptation type based on needs assessment."""
        if not adaptation_needs:
            return ContentAdaptationType.DIFFICULTY_ADJUSTMENT

        # Select the adaptation type with the highest need score
        primary_adaptation = max(adaptation_needs.items(), key=lambda x: x[1])
        return primary_adaptation[0]

    def _apply_adaptations(self, content: dict[str, Any], adaptation_type: ContentAdaptationType,
                          user_characteristics: dict[str, Any], context: PersonalizationContext) -> dict[str, Any]:
        """Apply specific adaptations to content."""
        adapted_content = content.copy()

        if adaptation_type == ContentAdaptationType.DIFFICULTY_ADJUSTMENT:
            adapted_content = self._adjust_difficulty(adapted_content, user_characteristics, context)
        elif adaptation_type == ContentAdaptationType.PACING_MODIFICATION:
            adapted_content = self._modify_pacing(adapted_content, user_characteristics, context)
        elif adaptation_type == ContentAdaptationType.STYLE_ADAPTATION:
            adapted_content = self._adapt_style(adapted_content, user_characteristics, context)
        elif adaptation_type == ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT:
            adapted_content = self._adjust_emotional_tone(adapted_content, user_characteristics, context)

        return adapted_content

    def _adjust_difficulty(self, content: dict[str, Any], user_characteristics: dict[str, Any],
                          context: PersonalizationContext) -> dict[str, Any]:
        """Adjust content difficulty based on user characteristics."""
        adapted = content.copy()

        learning_style = user_characteristics.get("learning_style", {})
        therapeutic_readiness = user_characteristics.get("therapeutic_readiness", {})

        # Simplify for users who need step-by-step approach
        if learning_style.get("step_by_step", 0) > 0.7:
            if "description" in adapted:
                adapted["description"] = self._simplify_text(adapted["description"])
            if "instructions" in adapted:
                adapted["instructions"] = self._break_into_steps(adapted["instructions"])
            adapted["complexity_level"] = "basic"

        # Increase complexity for challenge-seekers with high readiness
        elif (learning_style.get("challenge_seeking", 0) > 0.7 and
              therapeutic_readiness.get("advanced_techniques", 0) > 0.6):
            if "description" in adapted:
                adapted["description"] = self._add_depth(adapted["description"])
            adapted["complexity_level"] = "advanced"
            adapted["additional_concepts"] = self._suggest_advanced_concepts(content)

        return adapted

    def _modify_pacing(self, content: dict[str, Any], user_characteristics: dict[str, Any],
                      context: PersonalizationContext) -> dict[str, Any]:
        """Modify content pacing based on user preferences."""
        adapted = content.copy()

        pacing_prefs = user_characteristics.get("pacing_preferences", {})

        # Slow down for users who prefer slow pacing
        if pacing_prefs.get("slow_paced", 0) > 0.7:
            adapted["pacing"] = "slow"
            adapted["break_points"] = self._add_break_points(content)
            adapted["review_frequency"] = "high"

        # Speed up for fast-paced users
        elif pacing_prefs.get("fast_paced", 0) > 0.7:
            adapted["pacing"] = "fast"
            adapted["content_density"] = "high"
            adapted["review_frequency"] = "low"

        # Add user control for flexible pacing
        if pacing_prefs.get("user_controlled", 0) > 0.7:
            adapted["user_pacing_control"] = True
            adapted["skip_options"] = True

        return adapted

    def _adapt_style(self, content: dict[str, Any], user_characteristics: dict[str, Any],
                    context: PersonalizationContext) -> dict[str, Any]:
        """Adapt content style based on user preferences."""
        adapted = content.copy()

        interaction_style = user_characteristics.get("interaction_style", {})

        # Adjust formality
        if interaction_style.get("formal", 0) > 0.7:
            adapted["tone"] = "formal"
            adapted["language_style"] = "professional"
        elif interaction_style.get("casual", 0) > 0.7:
            adapted["tone"] = "casual"
            adapted["language_style"] = "conversational"

        # Adjust supportiveness
        if interaction_style.get("supportive", 0) > 0.8:
            adapted["supportive_elements"] = True
            adapted["encouragement_frequency"] = "high"

        # Adjust directiveness
        if interaction_style.get("directive", 0) > 0.7:
            adapted["guidance_level"] = "high"
            adapted["clear_instructions"] = True
        elif interaction_style.get("collaborative", 0) > 0.7:
            adapted["collaborative_elements"] = True
            adapted["user_choice_emphasis"] = True

        return adapted

    def _adjust_emotional_tone(self, content: dict[str, Any], user_characteristics: dict[str, Any],
                              context: PersonalizationContext) -> dict[str, Any]:
        """Adjust emotional tone based on user state and needs."""
        adapted = content.copy()

        support_needs = user_characteristics.get("support_needs", {})
        current_emotion = context.current_emotional_state

        # Increase support for users in distress
        if (current_emotion and current_emotion.primary_emotion in [
            EmotionalStateType.ANXIOUS, EmotionalStateType.DEPRESSED, EmotionalStateType.OVERWHELMED
        ]):
            adapted["emotional_tone"] = "highly_supportive"
            adapted["reassurance_level"] = "high"
            adapted["gentle_approach"] = True

        # Add encouragement for users who need it
        if support_needs.get("frequent_encouragement", 0) > 0.7:
            adapted["encouragement_elements"] = True
            adapted["positive_reinforcement"] = "frequent"

        # Adjust challenge level based on emotional state
        if current_emotion and current_emotion.intensity > 0.7:
            adapted["challenge_level"] = "low"
            adapted["comfort_focus"] = True

        return adapted

    def _simplify_text(self, text: str) -> str:
        """Simplify text for easier understanding."""
        # This is a simplified implementation
        # In practice, you might use NLP libraries for text simplification
        simplified = text.replace("utilize", "use").replace("demonstrate", "show")
        simplified = simplified.replace("facilitate", "help").replace("implement", "do")
        return simplified

    def _break_into_steps(self, instructions: str) -> list[str]:
        """Break instructions into clear steps."""
        # Simple implementation - split by sentences and number them
        sentences = instructions.split('. ')
        steps = [f"Step {i+1}: {sentence.strip()}" for i, sentence in enumerate(sentences) if sentence.strip()]
        return steps

    def _add_depth(self, description: str) -> str:
        """Add depth and complexity to content."""
        # Simple implementation - add analytical elements
        return f"{description} Consider the underlying mechanisms and broader implications of this approach."

    def _suggest_advanced_concepts(self, content: dict[str, Any]) -> list[str]:
        """Suggest advanced concepts related to the content."""
        # Simple implementation - return generic advanced concepts
        return [
            "Meta-cognitive awareness",
            "Systemic perspective",
            "Integration with other therapeutic modalities",
            "Long-term maintenance strategies"
        ]

    def _add_break_points(self, content: dict[str, Any]) -> list[str]:
        """Add natural break points for pacing."""
        return [
            "Take a moment to reflect on this concept",
            "Pause here and consider your own experience",
            "Let's check in - how are you feeling about this so far?",
            "This might be a good time for a brief break"
        ]

    def _generate_adaptation_rationale(self, adaptation_type: ContentAdaptationType,
                                     user_characteristics: dict[str, Any]) -> str:
        """Generate rationale for the adaptation decision."""
        rationales = {
            ContentAdaptationType.DIFFICULTY_ADJUSTMENT: "Adjusted content complexity based on user's learning style and therapeutic readiness",
            ContentAdaptationType.PACING_MODIFICATION: "Modified content pacing to match user's preferred learning speed",
            ContentAdaptationType.STYLE_ADAPTATION: "Adapted communication style to align with user's interaction preferences",
            ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT: "Adjusted emotional tone to provide appropriate support level"
        }

        return rationales.get(adaptation_type, "Content adapted based on user profile analysis")

    def _calculate_adaptation_confidence(self, adaptation_needs: dict[ContentAdaptationType, float],
                                       user_characteristics: dict[str, Any]) -> float:
        """Calculate confidence in the adaptation decision."""
        if not adaptation_needs:
            return 0.5

        # Higher confidence when needs are clear and strong
        max_need = max(adaptation_needs.values())
        need_clarity = max_need - min(adaptation_needs.values()) if len(adaptation_needs) > 1 else max_need

        # Factor in data availability
        data_completeness = len(user_characteristics) / 8.0  # Assuming 8 key characteristics

        confidence = (max_need * 0.6 + need_clarity * 0.2 + data_completeness * 0.2)
        return max(0.3, min(1.0, confidence))  # Clamp between 0.3 and 1.0

    def _predict_adaptation_impact(self, adaptation_type: ContentAdaptationType,
                                 user_characteristics: dict[str, Any]) -> str:
        """Predict the impact of the adaptation."""
        impact_predictions = {
            ContentAdaptationType.DIFFICULTY_ADJUSTMENT: "Improved comprehension and reduced cognitive load",
            ContentAdaptationType.PACING_MODIFICATION: "Better engagement and reduced overwhelm",
            ContentAdaptationType.STYLE_ADAPTATION: "Enhanced comfort and communication effectiveness",
            ContentAdaptationType.EMOTIONAL_TONE_ADJUSTMENT: "Increased emotional safety and therapeutic alliance"
        }

        return impact_predictions.get(adaptation_type, "Improved user experience and therapeutic outcomes")


class RecommendationSystem:
    """Generates personalized therapeutic recommendations."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the recommendation system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.recommendation_templates = self._initialize_recommendation_templates()
        logger.info("RecommendationSystem initialized")

    def _initialize_recommendation_templates(self) -> dict[RecommendationType, dict[str, Any]]:
        """Initialize templates for different recommendation types."""
        return {
            RecommendationType.NEXT_INTERVENTION: {
                "title_template": "Try {intervention_name}",
                "description_template": "Based on your progress, {intervention_name} could help with {target_area}",
                "priority_factors": ["current_needs", "readiness_level", "past_effectiveness"]
            },
            RecommendationType.CONTENT_FOCUS: {
                "title_template": "Focus on {content_area}",
                "description_template": "Concentrating on {content_area} aligns with your current therapeutic goals",
                "priority_factors": ["goal_alignment", "progress_gaps", "user_interest"]
            },
            RecommendationType.SESSION_STRUCTURE: {
                "title_template": "Adjust session structure",
                "description_template": "Consider {structure_change} to better match your learning style",
                "priority_factors": ["engagement_patterns", "learning_style", "session_feedback"]
            }
        }

    def generate_recommendations(self, context: PersonalizationContext,
                               max_recommendations: int = 5) -> list[PersonalizedRecommendation]:
        """Generate personalized recommendations based on context."""
        try:
            # Analyze user characteristics
            profile_analyzer = UserProfileAnalyzer()
            user_characteristics = profile_analyzer.analyze_user_characteristics(
                context.personalization_profile, context.progress_analysis
            )

            # Generate different types of recommendations
            all_recommendations = []

            # Intervention recommendations
            intervention_recs = self._generate_intervention_recommendations(context, user_characteristics)
            all_recommendations.extend(intervention_recs)

            # Content focus recommendations
            content_recs = self._generate_content_focus_recommendations(context, user_characteristics)
            all_recommendations.extend(content_recs)

            # Session structure recommendations
            structure_recs = self._generate_session_structure_recommendations(context, user_characteristics)
            all_recommendations.extend(structure_recs)

            # Goal recommendations
            goal_recs = self._generate_goal_recommendations(context, user_characteristics)
            all_recommendations.extend(goal_recs)

            # Sort by priority and return top recommendations
            all_recommendations.sort(key=lambda x: x.priority_score, reverse=True)

            # Validate all recommendations
            valid_recommendations = []
            for rec in all_recommendations[:max_recommendations]:
                try:
                    rec.validate()
                    valid_recommendations.append(rec)
                except ValidationError as e:
                    logger.warning(f"Invalid recommendation generated: {e}")

            logger.info(f"Generated {len(valid_recommendations)} recommendations for user {context.user_id}")
            return valid_recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations for user {context.user_id}: {e}")
            return []

    def _generate_intervention_recommendations(self, context: PersonalizationContext,
                                            user_characteristics: dict[str, Any]) -> list[PersonalizedRecommendation]:
        """Generate intervention recommendations."""
        recommendations = []

        therapeutic_readiness = user_characteristics.get("therapeutic_readiness", {})
        user_characteristics.get("support_needs", {})

        # Recommend mindfulness for users ready for self-reflection
        if therapeutic_readiness.get("self_reflection", 0) > 0.6:
            recommendations.append(PersonalizedRecommendation(
                recommendation_type=RecommendationType.NEXT_INTERVENTION,
                title="Practice Mindfulness Meditation",
                description="Mindfulness can help you develop greater self-awareness and emotional regulation",
                rationale="Your profile indicates readiness for reflective practices",
                priority_score=0.8,
                confidence_level=0.8,
                expected_benefit="Improved emotional regulation and self-awareness",
                implementation_steps=[
                    "Start with 5-minute guided meditations",
                    "Practice daily at a consistent time",
                    "Gradually increase duration as comfort grows"
                ],
                estimated_duration=10,
                success_metrics=["Increased mindfulness scores", "Reduced emotional reactivity"]
            ))

        # Recommend behavioral activation for users needing action-oriented approaches
        if (user_characteristics.get("content_preferences", {}).get("action_oriented", 0) > 0.7 and
            therapeutic_readiness.get("behavioral_change", 0) > 0.5):
            recommendations.append(PersonalizedRecommendation(
                recommendation_type=RecommendationType.NEXT_INTERVENTION,
                title="Try Behavioral Activation Techniques",
                description="Engaging in meaningful activities can improve mood and motivation",
                rationale="Your preference for action-oriented content suggests this approach would be effective",
                priority_score=0.7,
                confidence_level=0.7,
                expected_benefit="Increased activity level and improved mood",
                implementation_steps=[
                    "Identify valued activities",
                    "Schedule one small activity daily",
                    "Track mood before and after activities"
                ],
                estimated_duration=20,
                success_metrics=["Increased activity engagement", "Improved mood ratings"]
            ))

        return recommendations

    def _generate_content_focus_recommendations(self, context: PersonalizationContext,
                                              user_characteristics: dict[str, Any]) -> list[PersonalizedRecommendation]:
        """Generate content focus recommendations."""
        recommendations = []

        content_preferences = user_characteristics.get("content_preferences", {})

        # Recommend narrative focus for users who prefer story-based content
        if content_preferences.get("narrative_heavy", 0) > 0.7:
            recommendations.append(PersonalizedRecommendation(
                recommendation_type=RecommendationType.CONTENT_FOCUS,
                title="Explore Story-Based Therapeutic Content",
                description="Engage with therapeutic concepts through rich narrative experiences",
                rationale="Your preference for narrative content suggests story-based learning would be effective",
                priority_score=0.6,
                confidence_level=0.7,
                expected_benefit="Enhanced engagement and deeper emotional connection to therapeutic concepts",
                implementation_steps=[
                    "Choose narrative-rich therapeutic scenarios",
                    "Reflect on character experiences and choices",
                    "Connect story themes to personal experiences"
                ],
                estimated_duration=25,
                success_metrics=["Increased session engagement", "Better concept retention"]
            ))

        return recommendations

    def _generate_session_structure_recommendations(self, context: PersonalizationContext,
                                                  user_characteristics: dict[str, Any]) -> list[PersonalizedRecommendation]:
        """Generate session structure recommendations."""
        recommendations = []

        user_characteristics.get("pacing_preferences", {})
        engagement_preferences = user_characteristics.get("engagement_preferences", {})

        # Recommend shorter sessions for users with low sustained focus
        if engagement_preferences.get("sustained_focus", 0) < 0.5:
            recommendations.append(PersonalizedRecommendation(
                recommendation_type=RecommendationType.SESSION_STRUCTURE,
                title="Try Shorter, More Frequent Sessions",
                description="Breaking content into smaller chunks can improve focus and retention",
                rationale="Your engagement patterns suggest shorter sessions would be more effective",
                priority_score=0.5,
                confidence_level=0.6,
                expected_benefit="Improved focus and reduced cognitive fatigue",
                implementation_steps=[
                    "Limit sessions to 15-20 minutes",
                    "Include natural break points",
                    "Schedule multiple short sessions per week"
                ],
                estimated_duration=15,
                success_metrics=["Improved attention during sessions", "Better completion rates"]
            ))

        return recommendations

    def _generate_goal_recommendations(self, context: PersonalizationContext,
                                     user_characteristics: dict[str, Any]) -> list[PersonalizedRecommendation]:
        """Generate therapeutic goal recommendations."""
        recommendations = []

        if context.progress_analysis and len(context.progress_analysis.areas_for_improvement) > 0:
            improvement_area = context.progress_analysis.areas_for_improvement[0]

            recommendations.append(PersonalizedRecommendation(
                recommendation_type=RecommendationType.THERAPEUTIC_GOAL,
                title=f"Set Goal for {improvement_area}",
                description=f"Creating a specific goal for {improvement_area.lower()} can help focus your therapeutic work",
                rationale="Based on your progress analysis, this area needs attention",
                priority_score=0.7,
                confidence_level=0.8,
                expected_benefit="Focused progress in identified improvement area",
                implementation_steps=[
                    "Define specific, measurable objectives",
                    "Break goal into smaller milestones",
                    "Track progress regularly"
                ],
                estimated_duration=30,
                success_metrics=["Goal achievement progress", "Improved metrics in target area"]
            ))

        return recommendations


class AdaptiveNarrativeGenerator:
    """Creates personalized narrative content based on user characteristics."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the adaptive narrative generator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.narrative_templates = self._initialize_narrative_templates()
        logger.info("AdaptiveNarrativeGenerator initialized")

    def _initialize_narrative_templates(self) -> dict[str, dict[str, Any]]:
        """Initialize narrative templates for different user types."""
        return {
            "supportive": {
                "tone": "warm and encouraging",
                "character_types": ["mentor", "friend", "guide"],
                "themes": ["growth", "resilience", "hope"],
                "pacing": "gentle"
            },
            "challenging": {
                "tone": "direct and motivating",
                "character_types": ["coach", "challenger", "teacher"],
                "themes": ["achievement", "overcoming obstacles", "mastery"],
                "pacing": "dynamic"
            },
            "exploratory": {
                "tone": "curious and open",
                "character_types": ["explorer", "philosopher", "seeker"],
                "themes": ["discovery", "understanding", "wisdom"],
                "pacing": "reflective"
            }
        }

    def generate_personalized_narrative(self, context: PersonalizationContext,
                                      narrative_request: dict[str, Any]) -> dict[str, Any]:
        """Generate personalized narrative content."""
        try:
            # Analyze user characteristics
            profile_analyzer = UserProfileAnalyzer()
            user_characteristics = profile_analyzer.analyze_user_characteristics(
                context.personalization_profile, context.progress_analysis
            )

            # Select narrative approach
            narrative_approach = self._select_narrative_approach(user_characteristics)

            # Generate personalized content
            personalized_narrative = self._create_narrative_content(
                narrative_request, narrative_approach, user_characteristics, context
            )

            logger.info(f"Generated personalized narrative for user {context.user_id}")
            return personalized_narrative

        except Exception as e:
            logger.error(f"Error generating personalized narrative for user {context.user_id}: {e}")
            return narrative_request  # Return original as fallback

    def _select_narrative_approach(self, user_characteristics: dict[str, Any]) -> str:
        """Select the most appropriate narrative approach."""
        support_needs = user_characteristics.get("support_needs", {})
        interaction_style = user_characteristics.get("interaction_style", {})

        if support_needs.get("frequent_encouragement", 0) > 0.7:
            return "supportive"
        elif interaction_style.get("challenging", 0) > 0.6:
            return "challenging"
        else:
            return "exploratory"

    def _create_narrative_content(self, narrative_request: dict[str, Any], approach: str,
                                user_characteristics: dict[str, Any], context: PersonalizationContext) -> dict[str, Any]:
        """Create narrative content based on approach and user characteristics."""
        template = self.narrative_templates.get(approach, self.narrative_templates["supportive"])

        personalized_content = narrative_request.copy()

        # Adapt tone
        personalized_content["tone"] = template["tone"]

        # Select appropriate characters
        if "characters" in personalized_content:
            personalized_content["preferred_character_types"] = template["character_types"]

        # Adapt themes
        personalized_content["themes"] = template["themes"]

        # Adjust pacing
        personalized_content["pacing"] = template["pacing"]

        # Add personalization metadata
        personalized_content["personalization_applied"] = {
            "approach": approach,
            "user_id": context.user_id,
            "adaptation_timestamp": datetime.now().isoformat()
        }

        return personalized_content


class PersonalizationEngine:
    """Main engine for content personalization and adaptation."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the personalization engine."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.profile_analyzer = UserProfileAnalyzer()
        self.content_adapter = ContentAdaptationSystem(llm_client)
        self.recommendation_system = RecommendationSystem(llm_client)
        self.narrative_generator = AdaptiveNarrativeGenerator(llm_client)

        # Storage for personalization history (in production, this would be database-backed)
        self.adaptation_history: dict[str, list[ContentAdaptation]] = defaultdict(list)
        self.recommendation_history: dict[str, list[PersonalizedRecommendation]] = defaultdict(list)

        logger.info("PersonalizationEngine initialized")

    def personalize_content(self, user_id: str, content: dict[str, Any],
                          session_state: SessionState, personalization_profile: PersonalizationProfile,
                          progress_analysis: ProgressAnalysisResult | None = None) -> dict[str, Any]:
        """Main method to personalize content for a user."""
        try:
            # Create personalization context
            context = PersonalizationContext(
                user_id=user_id,
                session_state=session_state,
                personalization_profile=personalization_profile,
                progress_analysis=progress_analysis,
                current_emotional_state=session_state.emotional_state,
                time_context={"timestamp": datetime.now().isoformat()}
            )
            context.validate()

            # Adapt content
            adaptation = self.content_adapter.adapt_content(content, context)
            self.adaptation_history[user_id].append(adaptation)

            # Generate recommendations
            recommendations = self.recommendation_system.generate_recommendations(context)
            self.recommendation_history[user_id].extend(recommendations)

            # Create personalized response
            personalized_response = {
                "adapted_content": adaptation.adapted_content,
                "adaptation_info": {
                    "type": adaptation.adaptation_type.value,
                    "rationale": adaptation.adaptation_rationale,
                    "confidence": adaptation.confidence_score
                },
                "recommendations": [
                    {
                        "type": rec.recommendation_type.value,
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority_score
                    }
                    for rec in recommendations[:3]  # Top 3 recommendations
                ],
                "personalization_metadata": {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "adaptation_id": adaptation.adaptation_id
                }
            }

            logger.info(f"Content personalized for user {user_id}")
            return personalized_response

        except Exception as e:
            logger.error(f"Error personalizing content for user {user_id}: {e}")
            return {
                "adapted_content": content,
                "adaptation_info": {"error": str(e)},
                "recommendations": [],
                "personalization_metadata": {"error": str(e)}
            }

    def generate_adaptive_narrative(self, user_id: str, narrative_request: dict[str, Any],
                                  session_state: SessionState, personalization_profile: PersonalizationProfile,
                                  progress_analysis: ProgressAnalysisResult | None = None) -> dict[str, Any]:
        """Generate adaptive narrative content based on user preferences."""
        try:
            # Create personalization context
            context = PersonalizationContext(
                user_id=user_id,
                session_state=session_state,
                personalization_profile=personalization_profile,
                progress_analysis=progress_analysis,
                current_emotional_state=session_state.emotional_state
            )
            context.validate()

            # Generate personalized narrative
            personalized_narrative = self.narrative_generator.generate_personalized_narrative(
                context, narrative_request
            )

            logger.info(f"Adaptive narrative generated for user {user_id}")
            return personalized_narrative

        except Exception as e:
            logger.error(f"Error generating adaptive narrative for user {user_id}: {e}")
            return narrative_request  # Return original as fallback

    def get_personalization_insights(self, user_id: str) -> dict[str, Any]:
        """Get insights about user's personalization patterns."""
        try:
            adaptations = self.adaptation_history.get(user_id, [])
            recommendations = self.recommendation_history.get(user_id, [])

            if not adaptations and not recommendations:
                return {"message": "No personalization data available"}

            # Analyze adaptation patterns
            adaptation_types = [a.adaptation_type.value for a in adaptations]
            most_common_adaptation = max(set(adaptation_types), key=adaptation_types.count) if adaptation_types else None

            # Analyze recommendation patterns
            rec_types = [r.recommendation_type.value for r in recommendations]
            most_common_recommendation = max(set(rec_types), key=rec_types.count) if rec_types else None

            # Calculate average confidence
            avg_adaptation_confidence = statistics.mean([a.confidence_score for a in adaptations]) if adaptations else 0.0
            avg_recommendation_confidence = statistics.mean([r.confidence_level for r in recommendations]) if recommendations else 0.0

            insights = {
                "total_adaptations": len(adaptations),
                "total_recommendations": len(recommendations),
                "most_common_adaptation": most_common_adaptation,
                "most_common_recommendation": most_common_recommendation,
                "average_adaptation_confidence": avg_adaptation_confidence,
                "average_recommendation_confidence": avg_recommendation_confidence,
                "personalization_effectiveness": (avg_adaptation_confidence + avg_recommendation_confidence) / 2,
                "recent_adaptations": [
                    {
                        "type": a.adaptation_type.value,
                        "confidence": a.confidence_score,
                        "timestamp": a.created_at.isoformat()
                    }
                    for a in adaptations[-5:]  # Last 5 adaptations
                ]
            }

            return insights

        except Exception as e:
            logger.error(f"Error getting personalization insights for user {user_id}: {e}")
            return {"error": str(e)}


# Utility functions for testing and validation
def create_sample_personalization_context(user_id: str) -> PersonalizationContext:
    """Create a sample personalization context for testing."""
    # Create sample session state
    session_state = SessionState(
        session_id=f"session_{user_id}",
        user_id=user_id,
        narrative_position=5
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
        overall_progress_score=0.7
    )

    return PersonalizationContext(
        user_id=user_id,
        session_state=session_state,
        personalization_profile=profile,
        progress_analysis=progress_analysis
    )


if __name__ == "__main__":
    # Test the personalization engine
    logging.basicConfig(level=logging.INFO)

    # Create test instance
    personalization_engine = PersonalizationEngine()

    # Create sample context
    test_user_id = "test_user_123"
    context = create_sample_personalization_context(test_user_id)

    # Test content personalization
    sample_content = {
        "title": "Managing Anxiety",
        "description": "Learn techniques to manage anxiety symptoms",
        "difficulty": "medium",
        "duration": 20
    }

    personalized_result = personalization_engine.personalize_content(
        test_user_id, sample_content, context.session_state,
        context.personalization_profile, context.progress_analysis
    )

    print(f"Personalized Content: {personalized_result['adapted_content']}")
    print(f"Adaptation Type: {personalized_result['adaptation_info']['type']}")
    print(f"Recommendations: {len(personalized_result['recommendations'])}")

    # Test insights
    insights = personalization_engine.get_personalization_insights(test_user_id)
    print(f"Personalization Insights: {insights}")

    print("Personalization engine test completed successfully!")
