"""
Emotion-Based Therapeutic Integration for TTA Prototype

This module integrates emotional state recognition with therapeutic interventions,
providing emotion-based therapeutic content adaptation and gentle exposure therapy
opportunities within safe narrative contexts.

Classes:
    EmotionBasedTherapeuticIntegration: Main integration class
    TherapeuticInterventionSelector: Selects interventions based on emotional state
    EmotionBasedContentAdapter: Adapts therapeutic content to emotional context
    ExposureTherapyManager: Manages gentle exposure therapy in narrative contexts
"""

import logging

# Import system components
import sys
import uuid
from collections import defaultdict, deque
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
    from .adaptive_response_system import (
        AdaptiveResponse,
        AdaptiveResponseSystem,
        ResponseTone,
    )
    from .emotional_state_recognition import (
        EmotionalAnalysisResult,
        EmotionalPattern,
        EmotionalStateRecognitionResponse,
        EmotionalTrigger,
    )
    from .therapeutic_content_integration import (
        TherapeuticContentIntegration,
        TherapeuticOpportunity,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from adaptive_response_system import (
            AdaptiveResponse,
            AdaptiveResponseSystem,
            ResponseTone,
        )
        from data_models import (
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticGoal,
            TherapeuticProgress,
            ValidationError,
        )
        from emotional_state_recognition import (
            EmotionalAnalysisResult,
            EmotionalPattern,
            EmotionalStateRecognitionResponse,
            EmotionalTrigger,
        )
        from therapeutic_content_integration import (
            TherapeuticContentIntegration,
            TherapeuticOpportunity,
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

        class MockEmotionalState:
            def __init__(self, primary_emotion="calm", intensity=0.5, **kwargs):
                self.primary_emotion = primary_emotion
                self.intensity = intensity
                self.secondary_emotions = kwargs.get("secondary_emotions", [])
                self.triggers = kwargs.get("triggers", [])
                self.timestamp = datetime.now()
                self.confidence_level = kwargs.get("confidence_level", 0.7)

        class MockEmotionalStateType:
            CALM = "calm"
            ANXIOUS = "anxious"
            DEPRESSED = "depressed"
            EXCITED = "excited"
            ANGRY = "angry"
            CONFUSED = "confused"
            HOPEFUL = "hopeful"
            OVERWHELMED = "overwhelmed"

        class MockInterventionType:
            COGNITIVE_RESTRUCTURING = "cognitive_restructuring"
            MINDFULNESS = "mindfulness"
            EXPOSURE_THERAPY = "exposure_therapy"
            BEHAVIORAL_ACTIVATION = "behavioral_activation"
            COPING_SKILLS = "coping_skills"
            EMOTIONAL_REGULATION = "emotional_regulation"

        # Set the mock classes
        EmotionalState = MockEmotionalState
        EmotionalStateType = MockEmotionalStateType
        InterventionType = MockInterventionType

logger = logging.getLogger(__name__)


class ExposureIntensity(Enum):
    """Levels of exposure therapy intensity."""

    MINIMAL = "minimal"
    GENTLE = "gentle"
    MODERATE = "moderate"
    GRADUAL = "gradual"
    PROGRESSIVE = "progressive"


class TherapeuticAdaptationStrategy(Enum):
    """Strategies for adapting therapeutic content to emotional states."""

    EMOTION_MATCHED = "emotion_matched"
    INTENSITY_SCALED = "intensity_scaled"
    TRIGGER_AWARE = "trigger_aware"
    PATTERN_INFORMED = "pattern_informed"
    GROWTH_ORIENTED = "growth_oriented"
    SAFETY_PRIORITIZED = "safety_prioritized"


@dataclass
class EmotionBasedIntervention:
    """Represents a therapeutic intervention adapted to emotional state."""

    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    base_intervention_type: InterventionType = InterventionType.COPING_SKILLS
    emotional_context: EmotionalState | None = None
    adapted_content: str = ""
    adaptation_strategies: list[TherapeuticAdaptationStrategy] = field(
        default_factory=list
    )
    narrative_integration: str = ""
    safety_considerations: list[str] = field(default_factory=list)
    expected_outcomes: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    follow_up_needed: bool = False
    therapeutic_value: float = 0.5  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate emotion-based intervention data."""
        if not self.adapted_content.strip():
            raise ValidationError("Adapted content cannot be empty")
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValidationError("Therapeutic value must be between 0.0 and 1.0")
        return True


@dataclass
class ExposureTherapySession:
    """Represents a gentle exposure therapy session within narrative context."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_fear_or_anxiety: str = ""
    exposure_intensity: ExposureIntensity = ExposureIntensity.GENTLE
    narrative_scenario: str = ""
    safety_measures: list[str] = field(default_factory=list)
    coping_strategies_available: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    escape_options: list[str] = field(default_factory=list)
    emotional_monitoring: dict[str, Any] = field(default_factory=dict)
    session_duration_minutes: int = 10
    therapeutic_rationale: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate exposure therapy session data."""
        if not self.target_fear_or_anxiety.strip():
            raise ValidationError("Target fear or anxiety must be specified")
        if not self.narrative_scenario.strip():
            raise ValidationError("Narrative scenario cannot be empty")
        if self.session_duration_minutes <= 0:
            raise ValidationError("Session duration must be positive")
        return True


@dataclass
class TherapeuticContentAdaptation:
    """Represents adapted therapeutic content based on emotional state."""

    adaptation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_content: str = ""
    adapted_content: str = ""
    emotional_context: EmotionalState | None = None
    adaptation_rationale: str = ""
    therapeutic_enhancements: list[str] = field(default_factory=list)
    emotional_safety_checks: list[str] = field(default_factory=list)
    personalization_elements: list[str] = field(default_factory=list)
    effectiveness_prediction: float = 0.5  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate therapeutic content adaptation data."""
        if not self.adapted_content.strip():
            raise ValidationError("Adapted content cannot be empty")
        if not 0.0 <= self.effectiveness_prediction <= 1.0:
            raise ValidationError(
                "Effectiveness prediction must be between 0.0 and 1.0"
            )
        return True


class TherapeuticInterventionSelector:
    """Selects appropriate therapeutic interventions based on emotional state."""

    def __init__(self):
        """Initialize the therapeutic intervention selector."""
        self.emotion_intervention_mappings = (
            self._initialize_emotion_intervention_mappings()
        )
        self.intervention_protocols = self._initialize_intervention_protocols()
        logger.info("TherapeuticInterventionSelector initialized")

    def _initialize_emotion_intervention_mappings(
        self,
    ) -> dict[EmotionalStateType, dict[str, Any]]:
        """Initialize mappings between emotional states and therapeutic interventions."""
        return {
            EmotionalStateType.ANXIOUS: {
                "primary_interventions": [
                    InterventionType.MINDFULNESS,
                    InterventionType.COPING_SKILLS,
                    InterventionType.COGNITIVE_RESTRUCTURING,
                ],
                "secondary_interventions": [
                    InterventionType.EMOTIONAL_REGULATION,
                    InterventionType.EXPOSURE_THERAPY,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.COPING_SKILLS,
                        InterventionType.MINDFULNESS,
                    ],
                    "high": [
                        InterventionType.COGNITIVE_RESTRUCTURING,
                        InterventionType.COPING_SKILLS,
                    ],
                },
                "contraindications": ["high_intensity_exposure"],
                "safety_considerations": [
                    "monitor_panic_symptoms",
                    "provide_grounding_techniques",
                ],
            },
            EmotionalStateType.DEPRESSED: {
                "primary_interventions": [
                    InterventionType.BEHAVIORAL_ACTIVATION,
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.MINDFULNESS,
                ],
                "secondary_interventions": [
                    InterventionType.COPING_SKILLS,
                    InterventionType.EMOTIONAL_REGULATION,
                ],
                "intensity_thresholds": {
                    "low": [
                        InterventionType.MINDFULNESS,
                        InterventionType.BEHAVIORAL_ACTIVATION,
                    ],
                    "moderate": [
                        InterventionType.BEHAVIORAL_ACTIVATION,
                        InterventionType.COGNITIVE_RESTRUCTURING,
                    ],
                    "high": [
                        InterventionType.COGNITIVE_RESTRUCTURING,
                        InterventionType.COPING_SKILLS,
                    ],
                },
                "contraindications": ["overwhelming_activation"],
                "safety_considerations": [
                    "monitor_suicidal_ideation",
                    "gentle_activation_approach",
                ],
            },
            EmotionalStateType.ANGRY: {
                "primary_interventions": [
                    InterventionType.EMOTIONAL_REGULATION,
                    InterventionType.COPING_SKILLS,
                    InterventionType.MINDFULNESS,
                ],
                "secondary_interventions": [
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.BEHAVIORAL_ACTIVATION,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.EMOTIONAL_REGULATION,
                        InterventionType.COPING_SKILLS,
                    ],
                    "high": [
                        InterventionType.EMOTIONAL_REGULATION,
                        InterventionType.MINDFULNESS,
                    ],
                },
                "contraindications": ["confrontational_approaches"],
                "safety_considerations": [
                    "validate_anger",
                    "provide_cooling_strategies",
                ],
            },
            EmotionalStateType.OVERWHELMED: {
                "primary_interventions": [
                    InterventionType.COPING_SKILLS,
                    InterventionType.MINDFULNESS,
                    InterventionType.EMOTIONAL_REGULATION,
                ],
                "secondary_interventions": [
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.BEHAVIORAL_ACTIVATION,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.COPING_SKILLS,
                        InterventionType.MINDFULNESS,
                    ],
                    "high": [
                        InterventionType.COPING_SKILLS,
                        InterventionType.EMOTIONAL_REGULATION,
                    ],
                },
                "contraindications": ["complex_interventions"],
                "safety_considerations": ["simplify_approach", "provide_grounding"],
            },
            EmotionalStateType.CONFUSED: {
                "primary_interventions": [
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.MINDFULNESS,
                    InterventionType.COPING_SKILLS,
                ],
                "secondary_interventions": [
                    InterventionType.EMOTIONAL_REGULATION,
                    InterventionType.BEHAVIORAL_ACTIVATION,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.COGNITIVE_RESTRUCTURING,
                        InterventionType.MINDFULNESS,
                    ],
                    "high": [
                        InterventionType.COGNITIVE_RESTRUCTURING,
                        InterventionType.COPING_SKILLS,
                    ],
                },
                "contraindications": ["ambiguous_interventions"],
                "safety_considerations": ["provide_clarity", "structured_approach"],
            },
            EmotionalStateType.EXCITED: {
                "primary_interventions": [
                    InterventionType.MINDFULNESS,
                    InterventionType.EMOTIONAL_REGULATION,
                    InterventionType.BEHAVIORAL_ACTIVATION,
                ],
                "secondary_interventions": [
                    InterventionType.COPING_SKILLS,
                    InterventionType.COGNITIVE_RESTRUCTURING,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.BEHAVIORAL_ACTIVATION],
                    "moderate": [
                        InterventionType.MINDFULNESS,
                        InterventionType.BEHAVIORAL_ACTIVATION,
                    ],
                    "high": [
                        InterventionType.EMOTIONAL_REGULATION,
                        InterventionType.MINDFULNESS,
                    ],
                },
                "contraindications": ["dampening_interventions"],
                "safety_considerations": [
                    "channel_energy_positively",
                    "maintain_balance",
                ],
            },
            EmotionalStateType.HOPEFUL: {
                "primary_interventions": [
                    InterventionType.BEHAVIORAL_ACTIVATION,
                    InterventionType.COGNITIVE_RESTRUCTURING,
                    InterventionType.MINDFULNESS,
                ],
                "secondary_interventions": [
                    InterventionType.COPING_SKILLS,
                    InterventionType.EMOTIONAL_REGULATION,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.BEHAVIORAL_ACTIVATION,
                        InterventionType.COGNITIVE_RESTRUCTURING,
                    ],
                    "high": [
                        InterventionType.BEHAVIORAL_ACTIVATION,
                        InterventionType.MINDFULNESS,
                    ],
                },
                "contraindications": ["pessimistic_interventions"],
                "safety_considerations": ["nurture_hope", "realistic_expectations"],
            },
            EmotionalStateType.CALM: {
                "primary_interventions": [
                    InterventionType.MINDFULNESS,
                    InterventionType.BEHAVIORAL_ACTIVATION,
                    InterventionType.COGNITIVE_RESTRUCTURING,
                ],
                "secondary_interventions": [
                    InterventionType.COPING_SKILLS,
                    InterventionType.EMOTIONAL_REGULATION,
                ],
                "intensity_thresholds": {
                    "low": [InterventionType.MINDFULNESS],
                    "moderate": [
                        InterventionType.BEHAVIORAL_ACTIVATION,
                        InterventionType.MINDFULNESS,
                    ],
                    "high": [
                        InterventionType.COGNITIVE_RESTRUCTURING,
                        InterventionType.BEHAVIORAL_ACTIVATION,
                    ],
                },
                "contraindications": ["disruptive_interventions"],
                "safety_considerations": ["maintain_stability", "gentle_progression"],
            },
        }

    def _initialize_intervention_protocols(
        self,
    ) -> dict[InterventionType, dict[str, Any]]:
        """Initialize detailed protocols for each intervention type."""
        return {
            InterventionType.MINDFULNESS: {
                "description": "Present-moment awareness and acceptance practices",
                "techniques": [
                    "breathing_awareness",
                    "body_scan",
                    "mindful_observation",
                    "acceptance_practice",
                    "grounding_exercises",
                ],
                "duration_range": (5, 15),  # minutes
                "difficulty_levels": ["beginner", "intermediate", "advanced"],
                "emotional_benefits": [
                    "reduced_anxiety",
                    "increased_awareness",
                    "emotional_regulation",
                ],
                "narrative_integration_points": [
                    "moments_of_reflection",
                    "peaceful_settings",
                    "transition_points",
                ],
            },
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "description": "Identifying and challenging negative thought patterns",
                "techniques": [
                    "thought_challenging",
                    "evidence_examination",
                    "alternative_perspectives",
                    "cognitive_defusion",
                    "reframing_exercises",
                ],
                "duration_range": (10, 25),
                "difficulty_levels": ["beginner", "intermediate", "advanced"],
                "emotional_benefits": [
                    "reduced_negative_thinking",
                    "improved_mood",
                    "increased_flexibility",
                ],
                "narrative_integration_points": [
                    "decision_points",
                    "challenging_situations",
                    "character_interactions",
                ],
            },
            InterventionType.COPING_SKILLS: {
                "description": "Practical strategies for managing difficult emotions and situations",
                "techniques": [
                    "problem_solving",
                    "distraction_techniques",
                    "self_soothing",
                    "social_support",
                    "activity_scheduling",
                ],
                "duration_range": (5, 20),
                "difficulty_levels": ["beginner", "intermediate", "advanced"],
                "emotional_benefits": [
                    "increased_confidence",
                    "better_management",
                    "reduced_distress",
                ],
                "narrative_integration_points": [
                    "challenging_scenarios",
                    "resource_discovery",
                    "skill_practice_opportunities",
                ],
            },
            InterventionType.EMOTIONAL_REGULATION: {
                "description": "Techniques for managing emotional intensity and expression",
                "techniques": [
                    "emotion_identification",
                    "intensity_scaling",
                    "regulation_strategies",
                    "expression_techniques",
                    "containment_skills",
                ],
                "duration_range": (8, 20),
                "difficulty_levels": ["beginner", "intermediate", "advanced"],
                "emotional_benefits": [
                    "emotional_balance",
                    "reduced_reactivity",
                    "increased_control",
                ],
                "narrative_integration_points": [
                    "emotional_moments",
                    "relationship_interactions",
                    "stress_situations",
                ],
            },
            InterventionType.BEHAVIORAL_ACTIVATION: {
                "description": "Engaging in meaningful activities to improve mood and functioning",
                "techniques": [
                    "activity_scheduling",
                    "value_based_actions",
                    "mastery_activities",
                    "social_engagement",
                    "goal_setting",
                ],
                "duration_range": (15, 30),
                "difficulty_levels": ["beginner", "intermediate", "advanced"],
                "emotional_benefits": [
                    "improved_mood",
                    "increased_energy",
                    "sense_of_accomplishment",
                ],
                "narrative_integration_points": [
                    "activity_opportunities",
                    "goal_achievement",
                    "social_interactions",
                ],
            },
            InterventionType.EXPOSURE_THERAPY: {
                "description": "Gradual exposure to feared situations in a safe context",
                "techniques": [
                    "systematic_desensitization",
                    "gradual_exposure",
                    "imaginal_exposure",
                    "in_vivo_practice",
                    "response_prevention",
                ],
                "duration_range": (10, 30),
                "difficulty_levels": ["gentle", "moderate", "intensive"],
                "emotional_benefits": [
                    "reduced_avoidance",
                    "increased_confidence",
                    "fear_reduction",
                ],
                "narrative_integration_points": [
                    "challenging_scenarios",
                    "fear_facing_opportunities",
                    "safe_practice_contexts",
                ],
            },
        }

    def select_interventions(
        self,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        therapeutic_goals: list[TherapeuticGoal],
        context: NarrativeContext,
    ) -> list[EmotionBasedIntervention]:
        """Select appropriate therapeutic interventions based on emotional state."""
        try:
            selected_interventions = []

            # Get emotion-specific mappings
            emotion_mapping = self.emotion_intervention_mappings.get(
                emotional_state.primary_emotion,
                self.emotion_intervention_mappings[EmotionalStateType.CALM],
            )

            # Determine intensity level
            if emotional_state.intensity <= 0.3:
                intensity_level = "low"
            elif emotional_state.intensity <= 0.7:
                intensity_level = "moderate"
            else:
                intensity_level = "high"

            # Get appropriate interventions for intensity level
            appropriate_interventions = emotion_mapping["intensity_thresholds"].get(
                intensity_level, emotion_mapping["primary_interventions"]
            )

            # Select top interventions (limit to 3)
            for intervention_type in appropriate_interventions[:3]:
                intervention = self._create_emotion_based_intervention(
                    intervention_type, emotional_state, triggers, context
                )
                selected_interventions.append(intervention)

            # Add trigger-specific interventions if relevant
            trigger_interventions = self._select_trigger_specific_interventions(
                triggers, emotional_state, context
            )
            selected_interventions.extend(trigger_interventions)

            # Validate all interventions
            validated_interventions = []
            for intervention in selected_interventions:
                try:
                    intervention.validate()
                    validated_interventions.append(intervention)
                except ValidationError as e:
                    logger.warning(f"Invalid intervention: {e}")

            logger.info(
                f"Selected {len(validated_interventions)} therapeutic interventions"
            )
            return validated_interventions[:5]  # Limit to 5 interventions

        except Exception as e:
            logger.error(f"Error selecting therapeutic interventions: {e}")
            return []

    def _create_emotion_based_intervention(
        self,
        intervention_type: InterventionType,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        context: NarrativeContext,
    ) -> EmotionBasedIntervention:
        """Create an emotion-based intervention."""
        try:
            protocol = self.intervention_protocols.get(intervention_type, {})
            emotion_mapping = self.emotion_intervention_mappings.get(
                emotional_state.primary_emotion, {}
            )

            # Generate adapted content based on emotional state
            adapted_content = self._generate_adapted_intervention_content(
                intervention_type, emotional_state, protocol
            )

            # Determine adaptation strategies
            adaptation_strategies = [TherapeuticAdaptationStrategy.EMOTION_MATCHED]

            if emotional_state.intensity > 0.7:
                adaptation_strategies.append(
                    TherapeuticAdaptationStrategy.INTENSITY_SCALED
                )

            if triggers:
                adaptation_strategies.append(
                    TherapeuticAdaptationStrategy.TRIGGER_AWARE
                )

            # Generate narrative integration
            narrative_integration = self._generate_narrative_integration(
                intervention_type, context, protocol
            )

            # Calculate therapeutic value
            therapeutic_value = min(1.0, 0.6 + (emotional_state.confidence_level * 0.3))

            intervention = EmotionBasedIntervention(
                base_intervention_type=intervention_type,
                emotional_context=emotional_state,
                adapted_content=adapted_content,
                adaptation_strategies=adaptation_strategies,
                narrative_integration=narrative_integration,
                safety_considerations=emotion_mapping.get("safety_considerations", []),
                expected_outcomes=protocol.get("emotional_benefits", []),
                contraindications=emotion_mapping.get("contraindications", []),
                therapeutic_value=therapeutic_value,
            )

            return intervention

        except Exception as e:
            logger.error(f"Error creating emotion-based intervention: {e}")
            # Return basic fallback intervention
            return EmotionBasedIntervention(
                base_intervention_type=intervention_type,
                emotional_context=emotional_state,
                adapted_content="Take a moment to focus on your breathing and notice how you're feeling.",
                therapeutic_value=0.5,
            )

    def _generate_adapted_intervention_content(
        self,
        intervention_type: InterventionType,
        emotional_state: EmotionalState,
        protocol: dict[str, Any],
    ) -> str:
        """Generate intervention content adapted to emotional state."""
        try:
            protocol.get("techniques", [])

            if intervention_type == InterventionType.MINDFULNESS:
                if emotional_state.primary_emotion == EmotionalStateType.ANXIOUS:
                    return (
                        "Let's try a gentle breathing exercise to help calm your anxiety. "
                        "Take a slow, deep breath in through your nose for 4 counts, "
                        "hold for 4 counts, then exhale slowly through your mouth for 6 counts. "
                        "Notice how your body feels with each breath."
                    )
                elif emotional_state.primary_emotion == EmotionalStateType.OVERWHELMED:
                    return (
                        "When feeling overwhelmed, grounding can help. "
                        "Notice 5 things you can see, 4 things you can touch, "
                        "3 things you can hear, 2 things you can smell, "
                        "and 1 thing you can taste. This brings you back to the present moment."
                    )
                else:
                    return (
                        "Take a moment to simply be present with whatever you're feeling. "
                        "Notice your breath, your body, and your surroundings without trying to change anything. "
                        "Just observe with kindness and acceptance."
                    )

            elif intervention_type == InterventionType.COGNITIVE_RESTRUCTURING:
                if emotional_state.primary_emotion == EmotionalStateType.DEPRESSED:
                    return (
                        "Let's examine that thought more closely. Is this thought helpful or harmful? "
                        "What evidence supports this thought, and what evidence challenges it? "
                        "What would you tell a good friend who had this same thought?"
                    )
                elif emotional_state.primary_emotion == EmotionalStateType.ANXIOUS:
                    return (
                        "Anxiety often involves 'what if' thinking. Let's challenge these worried thoughts. "
                        "What's the worst that could realistically happen? What's most likely to happen? "
                        "How have you handled similar situations before?"
                    )
                else:
                    return (
                        "Let's look at this situation from different angles. "
                        "What other ways could you interpret what happened? "
                        "What would someone you trust and respect say about this situation?"
                    )

            elif intervention_type == InterventionType.COPING_SKILLS:
                if emotional_state.intensity > 0.7:
                    return (
                        "When emotions feel intense, having a toolkit of coping strategies helps. "
                        "Try: taking slow, deep breaths; going for a walk; calling a supportive friend; "
                        "listening to calming music; or doing something creative. "
                        "Which of these feels most helpful right now?"
                    )
                else:
                    return (
                        "Building coping skills is like building muscle - it takes practice. "
                        "Consider what has helped you before in similar situations. "
                        "What resources do you have available? What support can you access?"
                    )

            elif intervention_type == InterventionType.EMOTIONAL_REGULATION:
                return (
                    "Emotions are like waves - they rise, peak, and naturally fall. "
                    "You can ride the wave rather than being overwhelmed by it. "
                    "Try naming the emotion, rating its intensity from 1-10, "
                    "and reminding yourself that this feeling will pass."
                )

            elif intervention_type == InterventionType.BEHAVIORAL_ACTIVATION:
                if emotional_state.primary_emotion == EmotionalStateType.DEPRESSED:
                    return (
                        "When feeling down, small actions can make a big difference. "
                        "What's one small, meaningful activity you could do today? "
                        "It could be as simple as making your bed, taking a shower, "
                        "or reaching out to someone you care about."
                    )
                else:
                    return (
                        "Engaging in activities that align with your values can boost your mood. "
                        "What matters most to you? How could you take one small step "
                        "toward something meaningful today?"
                    )

            else:  # Default content
                return (
                    "Take a moment to acknowledge what you're experiencing right now. "
                    "Your feelings are valid, and you have the strength to work through this. "
                    "What would be most helpful for you in this moment?"
                )

        except Exception as e:
            logger.error(f"Error generating adapted intervention content: {e}")
            return "Take a moment to breathe and be gentle with yourself."

    def _generate_narrative_integration(
        self,
        intervention_type: InterventionType,
        context: NarrativeContext,
        protocol: dict[str, Any],
    ) -> str:
        """Generate narrative integration for the intervention."""
        try:
            integration_points = protocol.get("narrative_integration_points", [])

            if not integration_points:
                return "The intervention can be naturally woven into the current narrative moment."

            # Select most appropriate integration point based on context
            if context.recent_events:
                recent_event = context.recent_events[-1].lower()

                if "challenge" in recent_event or "difficult" in recent_event:
                    return "This challenging moment in the story provides a perfect opportunity to practice this therapeutic technique."
                elif "peaceful" in recent_event or "calm" in recent_event:
                    return "This peaceful moment allows for gentle exploration of this therapeutic approach."
                elif "decision" in recent_event or "choice" in recent_event:
                    return "This decision point in the narrative offers a chance to apply therapeutic insights."

            # Default integration
            return f"The current narrative context provides an opportunity to explore {intervention_type.value.replace('_', ' ')} techniques."

        except Exception as e:
            logger.error(f"Error generating narrative integration: {e}")
            return "This therapeutic technique can be integrated into the current story moment."

    def _select_trigger_specific_interventions(
        self,
        triggers: list[EmotionalTrigger],
        emotional_state: EmotionalState,
        context: NarrativeContext,
    ) -> list[EmotionBasedIntervention]:
        """Select interventions specific to identified triggers."""
        trigger_interventions = []

        try:
            for trigger in triggers[:2]:  # Limit to 2 trigger-specific interventions
                # Determine appropriate intervention based on trigger type
                if (
                    "work" in trigger.description.lower()
                    or "stress" in trigger.description.lower()
                ):
                    intervention_type = InterventionType.COPING_SKILLS
                elif (
                    "relationship" in trigger.description.lower()
                    or "social" in trigger.description.lower()
                ):
                    intervention_type = InterventionType.EMOTIONAL_REGULATION
                elif (
                    "performance" in trigger.description.lower()
                    or "evaluation" in trigger.description.lower()
                ):
                    intervention_type = InterventionType.COGNITIVE_RESTRUCTURING
                else:
                    intervention_type = InterventionType.MINDFULNESS

                # Create trigger-specific intervention
                intervention = EmotionBasedIntervention(
                    base_intervention_type=intervention_type,
                    emotional_context=emotional_state,
                    adapted_content=f"This technique can help you manage situations involving {trigger.description.lower()}.",
                    adaptation_strategies=[TherapeuticAdaptationStrategy.TRIGGER_AWARE],
                    therapeutic_value=0.6,
                )

                trigger_interventions.append(intervention)

        except Exception as e:
            logger.error(f"Error selecting trigger-specific interventions: {e}")

        return trigger_interventions


class EmotionBasedContentAdapter:
    """Adapts therapeutic content to emotional context and user needs."""

    def __init__(self):
        """Initialize the emotion-based content adapter."""
        self.adaptation_templates = self._initialize_adaptation_templates()
        self.personalization_strategies = self._initialize_personalization_strategies()
        logger.info("EmotionBasedContentAdapter initialized")

    def _initialize_adaptation_templates(
        self,
    ) -> dict[EmotionalStateType, dict[str, str]]:
        """Initialize templates for adapting content to different emotional states."""
        return {
            EmotionalStateType.ANXIOUS: {
                "opening": "I can sense your anxiety, and that's completely understandable.",
                "validation": "Anxiety is your mind's way of trying to protect you.",
                "guidance": "Let's work together to find some calm in this moment.",
                "closing": "Remember, you've handled difficult situations before, and you can handle this too.",
            },
            EmotionalStateType.DEPRESSED: {
                "opening": "I hear the heaviness in what you're sharing.",
                "validation": "These feelings of sadness are real and valid.",
                "guidance": "Even small steps forward can make a meaningful difference.",
                "closing": "You don't have to carry this alone - support is available.",
            },
            EmotionalStateType.ANGRY: {
                "opening": "Your anger makes complete sense given what you're experiencing.",
                "validation": "Anger often signals that something important to you has been threatened.",
                "guidance": "Let's find healthy ways to honor and express these feelings.",
                "closing": "Your feelings are valid, and there are constructive ways to address them.",
            },
            EmotionalStateType.OVERWHELMED: {
                "opening": "It sounds like you're dealing with a lot right now.",
                "validation": "Feeling overwhelmed is natural when facing multiple challenges.",
                "guidance": "Let's break this down into smaller, more manageable pieces.",
                "closing": "One step at a time - you don't have to solve everything at once.",
            },
            EmotionalStateType.CONFUSED: {
                "opening": "Confusion can be uncomfortable, but it's also a sign that you're processing something important.",
                "validation": "It's okay not to have all the answers right now.",
                "guidance": "Let's explore this together and find some clarity.",
                "closing": "Understanding often comes gradually - be patient with yourself.",
            },
            EmotionalStateType.EXCITED: {
                "opening": "I can feel your positive energy and enthusiasm!",
                "validation": "It's wonderful when we feel excited about possibilities.",
                "guidance": "Let's channel this energy in ways that serve you well.",
                "closing": "Your enthusiasm is a strength - let's use it wisely.",
            },
            EmotionalStateType.HOPEFUL: {
                "opening": "There's something beautiful about the hope I hear in your words.",
                "validation": "Hope is a powerful force for positive change.",
                "guidance": "Let's build on this hope with concrete steps forward.",
                "closing": "Your hope is well-founded - you have the capacity for growth and change.",
            },
            EmotionalStateType.CALM: {
                "opening": "I appreciate the thoughtful way you're approaching this.",
                "validation": "Your calm perspective is a valuable resource.",
                "guidance": "Let's use this clarity to explore your situation more deeply.",
                "closing": "Your balanced approach will serve you well moving forward.",
            },
        }

    def _initialize_personalization_strategies(self) -> dict[str, dict[str, Any]]:
        """Initialize strategies for personalizing therapeutic content."""
        return {
            "intensity_scaling": {
                "high_intensity": {
                    "language_style": "gentle_immediate",
                    "pacing": "slower",
                    "focus": "safety_and_stabilization",
                    "techniques": ["grounding", "breathing", "immediate_coping"],
                },
                "moderate_intensity": {
                    "language_style": "supportive_exploratory",
                    "pacing": "natural",
                    "focus": "understanding_and_coping",
                    "techniques": [
                        "exploration",
                        "skill_building",
                        "insight_development",
                    ],
                },
                "low_intensity": {
                    "language_style": "encouraging_growth_oriented",
                    "pacing": "forward_moving",
                    "focus": "growth_and_development",
                    "techniques": [
                        "skill_enhancement",
                        "goal_setting",
                        "future_planning",
                    ],
                },
            },
            "trigger_awareness": {
                "situational_triggers": {
                    "focus": "environmental_coping",
                    "techniques": [
                        "situation_management",
                        "environmental_modification",
                    ],
                },
                "interpersonal_triggers": {
                    "focus": "relationship_skills",
                    "techniques": [
                        "communication",
                        "boundary_setting",
                        "social_support",
                    ],
                },
                "cognitive_triggers": {
                    "focus": "thought_management",
                    "techniques": [
                        "cognitive_restructuring",
                        "mindfulness",
                        "acceptance",
                    ],
                },
            },
        }

    def adapt_therapeutic_content(
        self,
        original_content: str,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        user_preferences: dict[str, Any] = None,
    ) -> TherapeuticContentAdaptation:
        """Adapt therapeutic content based on emotional state and context."""
        try:
            # Get adaptation template for emotional state
            template = self.adaptation_templates.get(
                emotional_state.primary_emotion,
                self.adaptation_templates[EmotionalStateType.CALM],
            )

            # Determine personalization strategy
            personalization = self._determine_personalization_strategy(
                emotional_state, triggers, user_preferences or {}
            )

            # Apply emotional adaptation
            adapted_content = self._apply_emotional_adaptation(
                original_content, template, emotional_state
            )

            # Apply personalization
            adapted_content = self._apply_personalization(
                adapted_content, personalization, emotional_state
            )

            # Add safety considerations
            safety_checks = self._generate_safety_checks(emotional_state, triggers)

            # Calculate effectiveness prediction
            effectiveness = self._predict_effectiveness(
                emotional_state, triggers, personalization
            )

            adaptation = TherapeuticContentAdaptation(
                original_content=original_content,
                adapted_content=adapted_content,
                emotional_context=emotional_state,
                adaptation_rationale=self._generate_adaptation_rationale(
                    emotional_state, personalization
                ),
                therapeutic_enhancements=self._identify_therapeutic_enhancements(
                    template, personalization
                ),
                emotional_safety_checks=safety_checks,
                personalization_elements=list(personalization.keys()),
                effectiveness_prediction=effectiveness,
            )

            adaptation.validate()
            return adaptation

        except Exception as e:
            logger.error(f"Error adapting therapeutic content: {e}")
            # Return minimal adaptation as fallback
            return TherapeuticContentAdaptation(
                original_content=original_content,
                adapted_content=original_content,
                emotional_context=emotional_state,
                adaptation_rationale="Fallback adaptation due to processing error",
                effectiveness_prediction=0.3,
            )

    def _determine_personalization_strategy(
        self,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        user_preferences: dict[str, Any],
    ) -> dict[str, Any]:
        """Determine personalization strategy based on user context."""
        strategy = {}

        # Intensity-based personalization
        if emotional_state.intensity > 0.7:
            strategy.update(
                self.personalization_strategies["intensity_scaling"]["high_intensity"]
            )
        elif emotional_state.intensity > 0.4:
            strategy.update(
                self.personalization_strategies["intensity_scaling"][
                    "moderate_intensity"
                ]
            )
        else:
            strategy.update(
                self.personalization_strategies["intensity_scaling"]["low_intensity"]
            )

        # Trigger-based personalization
        if triggers:
            primary_trigger = triggers[0]  # Use first trigger for primary adaptation
            trigger_type = (
                primary_trigger.trigger_type.value
                if hasattr(primary_trigger, "trigger_type")
                else "situational"
            )

            if (
                f"{trigger_type}_triggers"
                in self.personalization_strategies["trigger_awareness"]
            ):
                trigger_strategy = self.personalization_strategies["trigger_awareness"][
                    f"{trigger_type}_triggers"
                ]
                strategy.update(trigger_strategy)

        # User preference integration
        if user_preferences.get("preferred_approach"):
            strategy["preferred_approach"] = user_preferences["preferred_approach"]

        return strategy

    def _apply_emotional_adaptation(
        self, content: str, template: dict[str, str], emotional_state: EmotionalState
    ) -> str:
        """Apply emotional adaptation to content using template."""
        try:
            # Start with validation and opening
            adapted_content = f"{template['opening']} {template['validation']}\n\n"

            # Add the main content with emotional framing
            adapted_content += f"{template['guidance']} {content}\n\n"

            # Add closing with emotional support
            adapted_content += template["closing"]

            return adapted_content

        except Exception as e:
            logger.error(f"Error applying emotional adaptation: {e}")
            return content

    def _apply_personalization(
        self,
        content: str,
        personalization: dict[str, Any],
        emotional_state: EmotionalState,
    ) -> str:
        """Apply personalization strategies to content."""
        try:
            adapted_content = content

            # Apply language style adjustments
            language_style = personalization.get(
                "language_style", "supportive_exploratory"
            )

            if language_style == "gentle_immediate":
                # Add immediate comfort and safety language
                adapted_content = adapted_content.replace(
                    "Let's", "Right now, let's gently"
                )
                adapted_content = adapted_content.replace(
                    "You can", "When you're ready, you can"
                )

            elif language_style == "encouraging_growth_oriented":
                # Add growth and empowerment language
                adapted_content = adapted_content.replace(
                    "try", "have the opportunity to"
                )
                adapted_content = adapted_content.replace(
                    "difficult", "challenging but manageable"
                )

            # Apply pacing adjustments
            pacing = personalization.get("pacing", "natural")

            if pacing == "slower":
                # Add pauses and breathing cues
                adapted_content = adapted_content.replace(
                    ". ", ". Take a moment to breathe. "
                )

            elif pacing == "forward_moving":
                # Add momentum and action language
                adapted_content = adapted_content.replace("Let's", "Let's actively")
                adapted_content = adapted_content.replace(
                    "consider", "explore and act on"
                )

            return adapted_content

        except Exception as e:
            logger.error(f"Error applying personalization: {e}")
            return content

    def _generate_safety_checks(
        self, emotional_state: EmotionalState, triggers: list[EmotionalTrigger]
    ) -> list[str]:
        """Generate safety checks based on emotional state and triggers."""
        safety_checks = []

        # Intensity-based safety checks
        if emotional_state.intensity > 0.8:
            safety_checks.append("Monitor for signs of emotional overwhelm")
            safety_checks.append("Ensure grounding techniques are readily available")

        # Emotion-specific safety checks
        if emotional_state.primary_emotion == EmotionalStateType.DEPRESSED:
            safety_checks.append("Monitor for suicidal ideation")
            safety_checks.append("Ensure support resources are accessible")

        elif emotional_state.primary_emotion == EmotionalStateType.ANXIOUS:
            safety_checks.append("Watch for panic symptoms")
            safety_checks.append("Have calming techniques ready")

        elif emotional_state.primary_emotion == EmotionalStateType.ANGRY:
            safety_checks.append("Ensure safe expression of anger")
            safety_checks.append("Monitor for aggressive impulses")

        # Trigger-specific safety checks
        for trigger in triggers:
            if "self-harm" in trigger.description.lower():
                safety_checks.append("Immediate safety assessment required")
            elif "trauma" in trigger.description.lower():
                safety_checks.append("Trauma-informed approach needed")

        return list(set(safety_checks))  # Remove duplicates

    def _predict_effectiveness(
        self,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        personalization: dict[str, Any],
    ) -> float:
        """Predict effectiveness of the adapted content."""
        try:
            base_effectiveness = 0.5

            # Adjust based on emotional state confidence
            base_effectiveness += emotional_state.confidence_level * 0.2

            # Adjust based on personalization depth
            personalization_score = len(personalization) / 10.0  # Normalize
            base_effectiveness += personalization_score * 0.2

            # Adjust based on trigger awareness
            if triggers:
                base_effectiveness += 0.1

            # Adjust based on emotional intensity (moderate intensity often most effective)
            if 0.4 <= emotional_state.intensity <= 0.7:
                base_effectiveness += 0.1
            elif emotional_state.intensity > 0.8:
                base_effectiveness -= 0.1  # High intensity can reduce effectiveness

            return min(1.0, max(0.0, base_effectiveness))

        except Exception as e:
            logger.error(f"Error predicting effectiveness: {e}")
            return 0.5

    def _generate_adaptation_rationale(
        self, emotional_state: EmotionalState, personalization: dict[str, Any]
    ) -> str:
        """Generate rationale for the adaptation choices made."""
        try:
            rationale_parts = []

            # Emotional state rationale
            rationale_parts.append(
                f"Content adapted for {emotional_state.primary_emotion.value} emotional state "
                f"with {emotional_state.intensity:.1f} intensity"
            )

            # Personalization rationale
            if personalization.get("language_style"):
                rationale_parts.append(
                    f"Language style adjusted to {personalization['language_style']}"
                )

            if personalization.get("pacing"):
                rationale_parts.append(
                    f"Pacing modified to {personalization['pacing']} approach"
                )

            if personalization.get("focus"):
                rationale_parts.append(
                    f"Focus directed toward {personalization['focus']}"
                )

            return ". ".join(rationale_parts) + "."

        except Exception as e:
            logger.error(f"Error generating adaptation rationale: {e}")
            return "Content adapted based on emotional context and user needs."

    def _identify_therapeutic_enhancements(
        self, template: dict[str, str], personalization: dict[str, Any]
    ) -> list[str]:
        """Identify therapeutic enhancements applied to the content."""
        enhancements = []

        # Template-based enhancements
        enhancements.append("Emotional validation and normalization")
        enhancements.append("Supportive opening and closing")

        # Personalization-based enhancements
        if personalization.get("techniques"):
            for technique in personalization["techniques"]:
                enhancements.append(
                    f"Integration of {technique.replace('_', ' ')} techniques"
                )

        if personalization.get("focus"):
            enhancements.append(
                f"Focus on {personalization['focus'].replace('_', ' ')}"
            )

        return enhancements


class ExposureTherapyManager:
    """Manages gentle exposure therapy opportunities within narrative contexts."""

    def __init__(self):
        """Initialize the exposure therapy manager."""
        self.exposure_protocols = self._initialize_exposure_protocols()
        self.safety_guidelines = self._initialize_safety_guidelines()
        logger.info("ExposureTherapyManager initialized")

    def _initialize_exposure_protocols(self) -> dict[str, dict[str, Any]]:
        """Initialize protocols for different types of exposure therapy."""
        return {
            "social_anxiety": {
                "description": "Gradual exposure to social situations",
                "intensity_levels": {
                    ExposureIntensity.MINIMAL: "Observing social interactions from a distance",
                    ExposureIntensity.GENTLE: "Brief, low-stakes social interactions",
                    ExposureIntensity.MODERATE: "Meaningful conversations with supportive characters",
                    ExposureIntensity.GRADUAL: "Group interactions with familiar characters",
                    ExposureIntensity.PROGRESSIVE: "Leadership or presentation opportunities",
                },
                "safety_measures": [
                    "Always provide escape options",
                    "Include supportive characters",
                    "Allow for breaks and processing time",
                    "Monitor anxiety levels throughout",
                ],
            },
            "performance_anxiety": {
                "description": "Gradual exposure to performance situations",
                "intensity_levels": {
                    ExposureIntensity.MINIMAL: "Watching others perform",
                    ExposureIntensity.GENTLE: "Private practice or preparation",
                    ExposureIntensity.MODERATE: "Small, supportive audience",
                    ExposureIntensity.GRADUAL: "Familiar audience with stakes",
                    ExposureIntensity.PROGRESSIVE: "Public performance with consequences",
                },
                "safety_measures": [
                    "Start with low-stakes situations",
                    "Provide preparation time",
                    "Include supportive feedback",
                    "Allow for multiple attempts",
                ],
            },
            "decision_making_anxiety": {
                "description": "Gradual exposure to decision-making situations",
                "intensity_levels": {
                    ExposureIntensity.MINIMAL: "Observing others make decisions",
                    ExposureIntensity.GENTLE: "Low-consequence personal choices",
                    ExposureIntensity.MODERATE: "Moderate-impact decisions with support",
                    ExposureIntensity.GRADUAL: "Important decisions with guidance",
                    ExposureIntensity.PROGRESSIVE: "High-stakes independent decisions",
                },
                "safety_measures": [
                    "Provide decision-making frameworks",
                    "Allow for consultation and advice",
                    "Include reversible decisions when possible",
                    "Celebrate decision-making courage",
                ],
            },
            "conflict_avoidance": {
                "description": "Gradual exposure to conflict situations",
                "intensity_levels": {
                    ExposureIntensity.MINIMAL: "Witnessing respectful disagreements",
                    ExposureIntensity.GENTLE: "Expressing mild preferences",
                    ExposureIntensity.MODERATE: "Respectful disagreement with support",
                    ExposureIntensity.GRADUAL: "Standing up for personal values",
                    ExposureIntensity.PROGRESSIVE: "Addressing significant conflicts",
                },
                "safety_measures": [
                    "Model healthy conflict resolution",
                    "Ensure psychological safety",
                    "Provide communication tools",
                    "Include repair and reconciliation opportunities",
                ],
            },
        }

    def _initialize_safety_guidelines(self) -> dict[str, list[str]]:
        """Initialize safety guidelines for exposure therapy."""
        return {
            "general_safety": [
                "Always obtain informed consent before exposure",
                "Start with the lowest possible intensity",
                "Provide multiple escape options",
                "Monitor emotional state continuously",
                "Allow for processing time after exposure",
                "Respect user's limits and boundaries",
            ],
            "narrative_safety": [
                "Maintain story coherence during exposure",
                "Provide narrative justification for challenges",
                "Include supportive characters and resources",
                "Allow for character growth and learning",
                "Ensure positive narrative outcomes are possible",
            ],
            "emotional_safety": [
                "Monitor for signs of overwhelm",
                "Provide grounding techniques readily",
                "Validate courage and effort",
                "Normalize anxiety and discomfort",
                "Celebrate progress and attempts",
            ],
        }

    def create_exposure_opportunity(
        self,
        fear_or_anxiety: str,
        emotional_state: EmotionalState,
        context: NarrativeContext,
        user_readiness: float = 0.5,
    ) -> ExposureTherapySession | None:
        """Create a gentle exposure therapy opportunity within narrative context."""
        try:
            # Determine exposure type based on fear/anxiety
            exposure_type = self._classify_exposure_type(fear_or_anxiety)

            if not exposure_type:
                logger.warning(
                    f"Could not classify exposure type for: {fear_or_anxiety}"
                )
                return None

            # Determine appropriate intensity based on emotional state and readiness
            intensity = self._determine_exposure_intensity(
                emotional_state, user_readiness
            )

            # Get protocol for this exposure type
            protocol = self.exposure_protocols.get(exposure_type, {})

            # Generate narrative scenario
            scenario = self._generate_exposure_scenario(
                exposure_type, intensity, context, protocol
            )

            # Create safety measures
            safety_measures = self._create_safety_measures(protocol, intensity)

            # Generate coping strategies
            coping_strategies = self._generate_coping_strategies(
                exposure_type, emotional_state
            )

            # Create success criteria
            success_criteria = self._define_success_criteria(exposure_type, intensity)

            # Create escape options
            escape_options = self._create_escape_options(scenario, context)

            session = ExposureTherapySession(
                target_fear_or_anxiety=fear_or_anxiety,
                exposure_intensity=intensity,
                narrative_scenario=scenario,
                safety_measures=safety_measures,
                coping_strategies_available=coping_strategies,
                success_criteria=success_criteria,
                escape_options=escape_options,
                session_duration_minutes=self._calculate_session_duration(intensity),
                therapeutic_rationale=self._generate_therapeutic_rationale(
                    exposure_type, intensity, fear_or_anxiety
                ),
            )

            session.validate()
            logger.info(f"Created exposure therapy session for {fear_or_anxiety}")
            return session

        except Exception as e:
            logger.error(f"Error creating exposure opportunity: {e}")
            return None

    def _classify_exposure_type(self, fear_or_anxiety: str) -> str | None:
        """Classify the type of exposure therapy needed."""
        fear_lower = fear_or_anxiety.lower()

        if any(
            word in fear_lower for word in ["social", "people", "judgment", "embarrass"]
        ):
            return "social_anxiety"
        elif any(
            word in fear_lower for word in ["perform", "present", "speak", "stage"]
        ):
            return "performance_anxiety"
        elif any(
            word in fear_lower for word in ["decide", "choice", "wrong", "mistake"]
        ):
            return "decision_making_anxiety"
        elif any(
            word in fear_lower for word in ["conflict", "disagree", "confront", "argue"]
        ):
            return "conflict_avoidance"
        else:
            return "social_anxiety"  # Default to social anxiety

    def _determine_exposure_intensity(
        self, emotional_state: EmotionalState, user_readiness: float
    ) -> ExposureIntensity:
        """Determine appropriate exposure intensity."""
        # Start with user readiness
        base_intensity = user_readiness

        # Adjust based on emotional state
        if emotional_state.intensity > 0.7:
            base_intensity -= 0.2  # Reduce intensity if highly emotional
        elif emotional_state.intensity < 0.3:
            base_intensity += 0.1  # Can handle slightly more if calm

        # Adjust based on confidence
        base_intensity += (emotional_state.confidence_level - 0.5) * 0.2

        # Map to intensity levels
        if base_intensity <= 0.2:
            return ExposureIntensity.MINIMAL
        elif base_intensity <= 0.4:
            return ExposureIntensity.GENTLE
        elif base_intensity <= 0.6:
            return ExposureIntensity.MODERATE
        elif base_intensity <= 0.8:
            return ExposureIntensity.GRADUAL
        else:
            return ExposureIntensity.PROGRESSIVE

    def _generate_exposure_scenario(
        self,
        exposure_type: str,
        intensity: ExposureIntensity,
        context: NarrativeContext,
        protocol: dict[str, Any],
    ) -> str:
        """Generate narrative scenario for exposure therapy."""
        try:
            intensity_descriptions = protocol.get("intensity_levels", {})
            base_scenario = intensity_descriptions.get(
                intensity, "A gentle challenge presents itself"
            )

            # Integrate with current narrative context
            if context.recent_events:
                recent_event = context.recent_events[-1]
                scenario = (
                    f"Building on recent events ({recent_event}), "
                    f"an opportunity arises that involves {base_scenario.lower()}. "
                    f"This situation allows you to practice facing your concerns about {exposure_type.replace('_', ' ')} "
                    f"in a supportive and safe environment."
                )
            else:
                scenario = (
                    f"A situation unfolds that involves {base_scenario.lower()}. "
                    f"This presents a chance to gently explore your feelings about {exposure_type.replace('_', ' ')} "
                    f"while maintaining full control over your participation."
                )

            return scenario

        except Exception as e:
            logger.error(f"Error generating exposure scenario: {e}")
            return "A gentle opportunity to face your concerns presents itself in a safe, supportive context."

    def _create_safety_measures(
        self, protocol: dict[str, Any], intensity: ExposureIntensity
    ) -> list[str]:
        """Create safety measures for the exposure session."""
        safety_measures = []

        # Add protocol-specific safety measures
        protocol_safety = protocol.get("safety_measures", [])
        safety_measures.extend(protocol_safety)

        # Add general safety measures
        safety_measures.extend(self.safety_guidelines["general_safety"])

        # Add intensity-specific measures
        if intensity in [ExposureIntensity.MINIMAL, ExposureIntensity.GENTLE]:
            safety_measures.append("Extra support and reassurance provided")
            safety_measures.append("Multiple check-ins during the experience")

        return list(set(safety_measures))  # Remove duplicates

    def _generate_coping_strategies(
        self, exposure_type: str, emotional_state: EmotionalState
    ) -> list[str]:
        """Generate coping strategies for the exposure session."""
        strategies = [
            "Deep breathing exercises",
            "Grounding techniques (5-4-3-2-1 method)",
            "Positive self-talk and affirmations",
            "Mindful awareness of thoughts and feelings",
        ]

        # Add exposure-type specific strategies
        if exposure_type == "social_anxiety":
            strategies.extend(
                [
                    "Focus on friendly faces",
                    "Remember that others are focused on themselves",
                    "Use conversation starters or topics prepared in advance",
                ]
            )
        elif exposure_type == "performance_anxiety":
            strategies.extend(
                [
                    "Visualize successful performance",
                    "Focus on the message rather than the audience",
                    "Use preparation and practice as confidence builders",
                ]
            )
        elif exposure_type == "decision_making_anxiety":
            strategies.extend(
                [
                    "Break decisions into smaller components",
                    "Consider pros and cons systematically",
                    "Remember that most decisions can be adjusted later",
                ]
            )

        return strategies

    def _define_success_criteria(
        self, exposure_type: str, intensity: ExposureIntensity
    ) -> list[str]:
        """Define success criteria for the exposure session."""
        base_criteria = [
            "Participated in the experience despite initial anxiety",
            "Used coping strategies when needed",
            "Stayed present during the challenging moment",
            "Recognized personal courage and effort",
        ]

        # Add intensity-specific criteria
        if intensity == ExposureIntensity.MINIMAL:
            base_criteria.append("Simply observed or witnessed the situation")
        elif intensity == ExposureIntensity.GENTLE:
            base_criteria.append("Engaged briefly with the challenging situation")
        elif intensity in [ExposureIntensity.MODERATE, ExposureIntensity.GRADUAL]:
            base_criteria.append("Maintained engagement despite discomfort")
        elif intensity == ExposureIntensity.PROGRESSIVE:
            base_criteria.append("Completed the challenging task successfully")

        return base_criteria

    def _create_escape_options(
        self, scenario: str, context: NarrativeContext
    ) -> list[str]:
        """Create escape options for the exposure session."""
        escape_options = [
            "Take a break to use coping strategies",
            "Ask for support from a trusted character",
            "Modify the situation to be more manageable",
            "Postpone the challenge for better preparation",
            "Exit the situation gracefully if needed",
        ]

        # Add context-specific escape options
        if context.active_characters:
            escape_options.append("Seek help from available supportive characters")

        return escape_options

    def _calculate_session_duration(self, intensity: ExposureIntensity) -> int:
        """Calculate appropriate session duration based on intensity."""
        duration_map = {
            ExposureIntensity.MINIMAL: 5,
            ExposureIntensity.GENTLE: 8,
            ExposureIntensity.MODERATE: 12,
            ExposureIntensity.GRADUAL: 15,
            ExposureIntensity.PROGRESSIVE: 20,
        }

        return duration_map.get(intensity, 10)

    def _generate_therapeutic_rationale(
        self, exposure_type: str, intensity: ExposureIntensity, fear_or_anxiety: str
    ) -> str:
        """Generate therapeutic rationale for the exposure session."""
        return (
            f"This {intensity.value} exposure to {exposure_type.replace('_', ' ')} "
            f"is designed to help you gradually build confidence in situations involving {fear_or_anxiety}. "
            f"By facing this fear in a safe, controlled environment with full support, "
            f"you can learn that you have the resources to handle challenging situations. "
            f"The goal is not to eliminate anxiety completely, but to prove to yourself "
            f"that you can cope with discomfort and still take meaningful action."
        )


class EmotionBasedTherapeuticIntegration:
    """Main integration class connecting emotional recognition with therapeutic interventions."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the emotion-based therapeutic integration system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.intervention_selector = TherapeuticInterventionSelector()
        self.content_adapter = EmotionBasedContentAdapter()
        self.exposure_manager = ExposureTherapyManager()

        # Integration history for learning and optimization
        self.integration_history = defaultdict(deque)

        logger.info("EmotionBasedTherapeuticIntegration system initialized")

    def integrate_emotional_recognition_with_therapy(
        self,
        emotional_analysis: EmotionalAnalysisResult,
        therapeutic_goals: list[TherapeuticGoal],
        context: NarrativeContext,
        session_state: SessionState,
    ) -> dict[str, Any]:
        """Integrate emotional state recognition with therapeutic interventions."""
        try:
            emotional_state = emotional_analysis.detected_emotion
            triggers = emotional_analysis.detected_triggers

            # Select appropriate therapeutic interventions
            selected_interventions = self.intervention_selector.select_interventions(
                emotional_state, triggers, therapeutic_goals, context
            )

            # Adapt therapeutic content to emotional context
            adapted_interventions = []
            for intervention in selected_interventions:
                adapted_content = self.content_adapter.adapt_therapeutic_content(
                    intervention.adapted_content,
                    emotional_state,
                    triggers,
                    self._get_user_preferences(session_state),
                )

                # Update intervention with adapted content
                intervention.adapted_content = adapted_content.adapted_content
                intervention.adaptation_strategies.extend(
                    [
                        TherapeuticAdaptationStrategy.EMOTION_MATCHED,
                        TherapeuticAdaptationStrategy.INTENSITY_SCALED,
                    ]
                )

                adapted_interventions.append(intervention)

            # Check for exposure therapy opportunities
            exposure_opportunities = self._identify_exposure_opportunities(
                emotional_state, triggers, context, session_state
            )

            # Generate integrated therapeutic response
            integrated_response = self._generate_integrated_response(
                adapted_interventions,
                exposure_opportunities,
                emotional_analysis,
                context,
            )

            # Store integration history for learning
            self._store_integration_history(
                session_state.user_id,
                emotional_analysis,
                adapted_interventions,
                integrated_response,
            )

            logger.info(
                f"Integrated {len(adapted_interventions)} therapeutic interventions with emotional recognition"
            )

            return {
                "emotional_analysis": emotional_analysis,
                "selected_interventions": adapted_interventions,
                "exposure_opportunities": exposure_opportunities,
                "integrated_response": integrated_response,
                "therapeutic_value": self._calculate_therapeutic_value(
                    adapted_interventions
                ),
                "safety_considerations": self._compile_safety_considerations(
                    adapted_interventions
                ),
                "follow_up_recommendations": self._generate_follow_up_recommendations(
                    emotional_analysis, adapted_interventions
                ),
            }

        except Exception as e:
            logger.error(f"Error integrating emotional recognition with therapy: {e}")
            return self._generate_fallback_integration(emotional_analysis, context)

    def _get_user_preferences(self, session_state: SessionState) -> dict[str, Any]:
        """Get user preferences for therapeutic content adaptation."""
        preferences = {}

        # Extract preferences from therapeutic progress
        if session_state.therapeutic_progress:
            # Analyze completed interventions for preferences
            completed = session_state.therapeutic_progress.completed_interventions
            if completed:
                # Find most effective intervention types
                effectiveness_scores = defaultdict(list)
                for intervention in completed:
                    effectiveness_scores[intervention.intervention_type].append(
                        intervention.effectiveness_rating
                    )

                # Calculate average effectiveness per type
                for intervention_type, scores in effectiveness_scores.items():
                    avg_score = sum(scores) / len(scores)
                    if avg_score >= 7.0:  # High effectiveness threshold
                        preferences["preferred_interventions"] = preferences.get(
                            "preferred_interventions", []
                        ) + [intervention_type]

        return preferences

    def _identify_exposure_opportunities(
        self,
        emotional_state: EmotionalState,
        triggers: list[EmotionalTrigger],
        context: NarrativeContext,
        session_state: SessionState,
    ) -> list[ExposureTherapySession]:
        """Identify opportunities for gentle exposure therapy."""
        opportunities = []

        try:
            # Only consider exposure if emotional state is not too intense
            if emotional_state.intensity > 0.8:
                logger.info("Emotional intensity too high for exposure therapy")
                return opportunities

            # Check for anxiety-related triggers that could benefit from exposure
            anxiety_triggers = [
                t
                for t in triggers
                if any(
                    anxiety_word in t.description.lower()
                    for anxiety_word in ["anxiety", "fear", "avoid", "worry"]
                )
            ]

            for trigger in anxiety_triggers[:2]:  # Limit to 2 exposure opportunities
                # Determine user readiness based on emotional state and confidence
                user_readiness = min(0.8, emotional_state.confidence_level * 0.7 + 0.2)

                exposure_session = self.exposure_manager.create_exposure_opportunity(
                    trigger.description, emotional_state, context, user_readiness
                )

                if exposure_session:
                    opportunities.append(exposure_session)

            # Also check for general avoidance patterns
            if (
                emotional_state.primary_emotion
                in [EmotionalStateType.ANXIOUS, EmotionalStateType.OVERWHELMED]
                and emotional_state.intensity <= 0.6
            ):

                # Create a general social/performance exposure opportunity
                general_exposure = self.exposure_manager.create_exposure_opportunity(
                    "general anxiety and avoidance patterns",
                    emotional_state,
                    context,
                    0.4,  # Conservative readiness for general exposure
                )

                if general_exposure:
                    opportunities.append(general_exposure)

            logger.info(
                f"Identified {len(opportunities)} exposure therapy opportunities"
            )
            return opportunities

        except Exception as e:
            logger.error(f"Error identifying exposure opportunities: {e}")
            return opportunities

    def _generate_integrated_response(
        self,
        interventions: list[EmotionBasedIntervention],
        exposure_opportunities: list[ExposureTherapySession],
        emotional_analysis: EmotionalAnalysisResult,
        context: NarrativeContext,
    ) -> str:
        """Generate integrated therapeutic response combining all elements."""
        try:
            response_parts = []

            # Start with emotional validation
            emotional_state = emotional_analysis.detected_emotion
            validation = self._generate_emotional_validation(emotional_state)
            response_parts.append(validation)

            # Add primary therapeutic intervention
            if interventions:
                primary_intervention = interventions[
                    0
                ]  # Use first intervention as primary
                response_parts.append(primary_intervention.adapted_content)

                # Add narrative integration if available
                if primary_intervention.narrative_integration:
                    response_parts.append(primary_intervention.narrative_integration)

            # Add exposure opportunity if appropriate and available
            if exposure_opportunities and emotional_state.intensity <= 0.6:
                exposure = exposure_opportunities[0]  # Use first exposure opportunity
                exposure_intro = (
                    f"\n\nIf you're feeling ready, there's also an opportunity to gently practice "
                    f"facing your concerns about {exposure.target_fear_or_anxiety}. "
                    f"{exposure.narrative_scenario}"
                )
                response_parts.append(exposure_intro)

            # Add supportive closing
            closing = self._generate_supportive_closing(emotional_state, interventions)
            response_parts.append(closing)

            # Combine all parts
            integrated_response = "\n\n".join(response_parts)

            return integrated_response

        except Exception as e:
            logger.error(f"Error generating integrated response: {e}")
            return "I'm here to support you through this moment. Let's work together to find helpful strategies."

    def _generate_emotional_validation(self, emotional_state: EmotionalState) -> str:
        """Generate emotional validation based on current state."""
        validation_templates = {
            EmotionalStateType.ANXIOUS: "I can sense your anxiety, and it's completely understandable to feel this way.",
            EmotionalStateType.DEPRESSED: "I hear the heaviness in what you're experiencing, and these feelings are valid.",
            EmotionalStateType.ANGRY: "Your anger makes sense given what you're going through.",
            EmotionalStateType.OVERWHELMED: "It sounds like you're dealing with a lot right now, and that's overwhelming.",
            EmotionalStateType.CONFUSED: "Confusion is natural when facing complex situations.",
            EmotionalStateType.EXCITED: "I can feel your positive energy and enthusiasm!",
            EmotionalStateType.HOPEFUL: "There's something beautiful about the hope I sense in you.",
            EmotionalStateType.CALM: "I appreciate the thoughtful way you're approaching this.",
        }

        base_validation = validation_templates.get(
            emotional_state.primary_emotion,
            "I acknowledge what you're feeling right now.",
        )

        # Add intensity acknowledgment if high
        if emotional_state.intensity > 0.7:
            base_validation += (
                " The intensity of these feelings shows how much this matters to you."
            )

        return base_validation

    def _generate_supportive_closing(
        self,
        emotional_state: EmotionalState,
        interventions: list[EmotionBasedIntervention],
    ) -> str:
        """Generate supportive closing for the integrated response."""
        closings = {
            EmotionalStateType.ANXIOUS: "Remember, you've handled difficult situations before, and you have the strength to handle this too.",
            EmotionalStateType.DEPRESSED: "You don't have to carry this alone - support is available, and small steps can lead to meaningful change.",
            EmotionalStateType.ANGRY: "Your feelings are valid, and there are constructive ways to honor and express them.",
            EmotionalStateType.OVERWHELMED: "One step at a time - you don't have to solve everything at once.",
            EmotionalStateType.CONFUSED: "Understanding often comes gradually - be patient with yourself as you work through this.",
            EmotionalStateType.EXCITED: "Your enthusiasm is a strength - let's channel it in ways that serve you well.",
            EmotionalStateType.HOPEFUL: "Your hope is well-founded - you have the capacity for growth and positive change.",
            EmotionalStateType.CALM: "Your balanced approach will serve you well as you move forward.",
        }

        base_closing = closings.get(
            emotional_state.primary_emotion,
            "You have more resources and strength than you might realize right now.",
        )

        # Add intervention-specific encouragement
        if interventions:
            base_closing += " The strategies we've explored can be powerful tools when practiced with patience and self-compassion."

        return base_closing

    def _calculate_therapeutic_value(
        self, interventions: list[EmotionBasedIntervention]
    ) -> float:
        """Calculate overall therapeutic value of the integrated approach."""
        if not interventions:
            return 0.3

        # Average therapeutic value of all interventions
        total_value = sum(
            intervention.therapeutic_value for intervention in interventions
        )
        avg_value = total_value / len(interventions)

        # Bonus for multiple complementary interventions
        if len(interventions) > 1:
            avg_value += 0.1

        # Bonus for adaptation strategies
        total_strategies = sum(
            len(intervention.adaptation_strategies) for intervention in interventions
        )
        strategy_bonus = min(0.2, total_strategies * 0.05)
        avg_value += strategy_bonus

        return min(1.0, avg_value)

    def _compile_safety_considerations(
        self, interventions: list[EmotionBasedIntervention]
    ) -> list[str]:
        """Compile safety considerations from all interventions."""
        all_safety_considerations = []

        for intervention in interventions:
            all_safety_considerations.extend(intervention.safety_considerations)

        # Remove duplicates and return
        return list(set(all_safety_considerations))

    def _generate_follow_up_recommendations(
        self,
        emotional_analysis: EmotionalAnalysisResult,
        interventions: list[EmotionBasedIntervention],
    ) -> list[str]:
        """Generate follow-up recommendations based on the integration."""
        recommendations = []

        # Add crisis-related follow-ups
        if emotional_analysis.crisis_indicators:
            recommendations.append(
                "Monitor emotional state closely for crisis indicators"
            )
            recommendations.append("Ensure access to crisis support resources")

        # Add intervention-specific follow-ups
        for intervention in interventions:
            if intervention.follow_up_needed:
                recommendations.append(
                    f"Follow up on {intervention.base_intervention_type.value.replace('_', ' ')} practice"
                )

        # Add general follow-ups based on emotional state
        emotional_state = emotional_analysis.detected_emotion
        if emotional_state.intensity > 0.7:
            recommendations.append(
                "Check in on emotional intensity and coping effectiveness"
            )

        if emotional_state.confidence_level < 0.5:
            recommendations.append("Build confidence through successful small steps")

        # Add therapeutic recommendations from analysis
        recommendations.extend(emotional_analysis.therapeutic_recommendations[:2])

        return list(set(recommendations))  # Remove duplicates

    def _store_integration_history(
        self,
        user_id: str,
        emotional_analysis: EmotionalAnalysisResult,
        interventions: list[EmotionBasedIntervention],
        integrated_response: str,
    ) -> None:
        """Store integration history for learning and optimization."""
        try:
            # Keep last 30 integrations per user
            if len(self.integration_history[user_id]) >= 30:
                self.integration_history[user_id].popleft()

            history_entry = {
                "timestamp": datetime.now(),
                "emotional_state": emotional_analysis.detected_emotion.primary_emotion.value,
                "emotional_intensity": emotional_analysis.detected_emotion.intensity,
                "interventions_used": [
                    i.base_intervention_type.value for i in interventions
                ],
                "therapeutic_value": self._calculate_therapeutic_value(interventions),
                "adaptation_strategies": list(
                    {

                            strategy.value
                            for intervention in interventions
                            for strategy in intervention.adaptation_strategies

                    }
                ),
                "response_length": len(integrated_response),
                "crisis_indicators": len(emotional_analysis.crisis_indicators) > 0,
            }

            self.integration_history[user_id].append(history_entry)

        except Exception as e:
            logger.error(f"Error storing integration history: {e}")

    def _generate_fallback_integration(
        self, emotional_analysis: EmotionalAnalysisResult, context: NarrativeContext
    ) -> dict[str, Any]:
        """Generate fallback integration when main process fails."""
        try:
            emotional_state = emotional_analysis.detected_emotion

            # Create basic intervention
            fallback_intervention = EmotionBasedIntervention(
                base_intervention_type=InterventionType.COPING_SKILLS,
                emotional_context=emotional_state,
                adapted_content="Take a moment to breathe and be gentle with yourself. You're doing the best you can right now.",
                therapeutic_value=0.4,
            )

            # Create basic response
            fallback_response = (
                f"I can see you're experiencing {emotional_state.primary_emotion.value} feelings right now. "
                f"That's completely valid. Let's take this one moment at a time and find some strategies that can help."
            )

            return {
                "emotional_analysis": emotional_analysis,
                "selected_interventions": [fallback_intervention],
                "exposure_opportunities": [],
                "integrated_response": fallback_response,
                "therapeutic_value": 0.4,
                "safety_considerations": [
                    "Monitor emotional state",
                    "Provide basic support",
                ],
                "follow_up_recommendations": ["Check in on emotional well-being"],
            }

        except Exception as e:
            logger.error(f"Error generating fallback integration: {e}")
            return {
                "error": "Unable to process therapeutic integration",
                "basic_support": "I'm here to support you. Please consider reaching out to a mental health professional if you need additional help.",
            }

    def get_integration_effectiveness_metrics(self, user_id: str) -> dict[str, Any]:
        """Get metrics on integration effectiveness for a user."""
        try:
            history = self.integration_history.get(user_id, [])

            if not history:
                return {"total_integrations": 0}

            # Calculate metrics
            total_integrations = len(history)
            avg_therapeutic_value = (
                sum(entry["therapeutic_value"] for entry in history)
                / total_integrations
            )

            # Count intervention usage
            intervention_counts = defaultdict(int)
            for entry in history:
                for intervention in entry["interventions_used"]:
                    intervention_counts[intervention] += 1

            # Count emotional state patterns
            emotion_counts = defaultdict(int)
            for entry in history:
                emotion_counts[entry["emotional_state"]] += 1

            # Calculate crisis frequency
            crisis_count = sum(1 for entry in history if entry["crisis_indicators"])
            crisis_frequency = (
                crisis_count / total_integrations if total_integrations > 0 else 0
            )

            return {
                "total_integrations": total_integrations,
                "average_therapeutic_value": avg_therapeutic_value,
                "intervention_usage": dict(intervention_counts),
                "emotional_state_distribution": dict(emotion_counts),
                "crisis_frequency": crisis_frequency,
                "recent_integrations": list(history)[-5:],  # Last 5 integrations
            }

        except Exception as e:
            logger.error(f"Error calculating integration effectiveness metrics: {e}")
            return {"error": str(e)}


# Utility functions for testing and validation
def test_emotion_based_therapeutic_integration():
    """Test the emotion-based therapeutic integration system."""
    try:
        # Initialize system
        integration_system = EmotionBasedTherapeuticIntegration()

        # Mock emotional analysis result
        from emotional_state_recognition import EmotionalAnalysisResult

        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.6,
                confidence_level=0.8,
            ),
            therapeutic_recommendations=["Practice mindfulness techniques"],
            detected_triggers=[
                EmotionalTrigger(
                    description="work-related stress",
                    associated_emotions=[EmotionalStateType.ANXIOUS],
                )
            ],
        )

        # Mock context and session
        context = NarrativeContext(session_id="test")
        session = SessionState(session_id="test", user_id="test_user")
        therapeutic_goals = [
            TherapeuticGoal(
                title="Manage anxiety",
                description="Learn to cope with anxious feelings",
            )
        ]

        # Test integration
        result = integration_system.integrate_emotional_recognition_with_therapy(
            emotional_analysis, therapeutic_goals, context, session
        )

        print("Integration completed successfully:")
        print(f"- Selected interventions: {len(result['selected_interventions'])}")
        print(f"- Therapeutic value: {result['therapeutic_value']:.2f}")
        print(f"- Exposure opportunities: {len(result['exposure_opportunities'])}")
        print(f"- Response preview: {result['integrated_response'][:100]}...")

        logger.info("Emotion-based therapeutic integration test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Emotion-based therapeutic integration test failed: {e}")
        return False


if __name__ == "__main__":
    # Run test
    test_emotion_based_therapeutic_integration()
