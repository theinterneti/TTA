"""
Emotion-Intervention Integration System for TTA Prototype

This module implements the integration between emotional state recognition and therapeutic
interventions, providing emotion-based therapeutic content adaptation and gentle exposure
therapy opportunities within safe narrative contexts.

Classes:
    EmotionInterventionIntegrator: Main class for emotion-intervention integration
    EmotionBasedInterventionSelector: Selects interventions based on emotional state
    SafeExposureTherapyManager: Manages gentle exposure therapy within narrative
    EmotionalAdaptationEngine: Adapts therapeutic content based on emotional state
"""

import logging
import statistics

# Import system components
import sys
import uuid
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
        TherapeuticOpportunity,
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
        AdaptiveResponseSystem,
        CrisisLevel,
        ResponseTone,
    )
    from .emotional_state_recognition import (
        EmotionalAnalysisResult,
        EmotionalPattern,
        EmotionalStateRecognitionResponse,
        EmotionalTrigger,
    )
    from .therapeutic_content_integration import (
        DetectedOpportunity,
        OpportunityType,
        TherapeuticContentIntegration,
    )
    from .therapeutic_guidance_agent import CrisisIndicators, TherapeuticGuidanceAgent
except ImportError:
    # Fallback for direct execution - create minimal mock classes
    logging.warning("Could not import required classes, using mock implementations")

    class MockEmotionalState:
        def __init__(self, primary_emotion="calm", intensity=0.5, **kwargs):
            self.primary_emotion = primary_emotion
            self.intensity = intensity
            self.secondary_emotions = kwargs.get('secondary_emotions', [])
            self.triggers = kwargs.get('triggers', [])
            self.timestamp = datetime.now()
            self.confidence_level = kwargs.get('confidence_level', 0.7)

    class MockEmotionalStateType:
        CALM = "calm"
        ANXIOUS = "anxious"
        DEPRESSED = "depressed"
        EXCITED = "excited"
        ANGRY = "angry"
        CONFUSED = "confused"
        HOPEFUL = "hopeful"
        OVERWHELMED = "overwhelmed"
        WORRIED = "worried"
        HOPELESS = "hopeless"

    class MockInterventionType:
        MINDFULNESS = "mindfulness"
        COPING_SKILLS = "coping_skills"
        COGNITIVE_RESTRUCTURING = "cognitive_restructuring"
        BEHAVIORAL_ACTIVATION = "behavioral_activation"
        EXPOSURE_THERAPY = "exposure_therapy"
        EMOTIONAL_REGULATION = "emotional_regulation"
        TRAUMA_PROCESSING = "trauma_processing"

    class MockValidationError(Exception):
        pass

    class MockSessionState:
        def __init__(self):
            self.therapeutic_progress = None
            self.character_states = {}
            self.emotional_state = MockEmotionalState()

    class MockNarrativeContext:
        def __init__(self):
            self.recent_events = []
            self.active_characters = []

    class MockTherapeuticProgress:
        def __init__(self):
            self.overall_progress_score = 50
            self.completed_interventions = []
            self.coping_strategies_learned = []

    class MockEmotionalAnalysisResult:
        def __init__(self):
            self.detected_emotion = MockEmotionalState()
            self.confidence_level = 0.7
            self.crisis_indicators = []
            self.detected_triggers = []

    # Set the mock classes
    EmotionalState = MockEmotionalState
    EmotionalStateType = MockEmotionalStateType
    InterventionType = MockInterventionType
    ValidationError = MockValidationError
    SessionState = MockSessionState
    NarrativeContext = MockNarrativeContext
    TherapeuticProgress = MockTherapeuticProgress
    EmotionalAnalysisResult = MockEmotionalAnalysisResult

logger = logging.getLogger(__name__)


class ExposureTherapyType(Enum):
    """Types of exposure therapy approaches."""
    IMAGINAL = "imaginal"  # Through narrative imagination
    IN_VIVO = "in_vivo"  # Through story experiences
    SYSTEMATIC = "systematic"  # Gradual systematic exposure
    FLOODING = "flooding"  # Intensive exposure (used carefully)
    VIRTUAL = "virtual"  # Through narrative virtual environments


class SafetyValidationLevel(Enum):
    """Levels of safety validation for interventions."""
    MINIMAL = "minimal"  # Basic safety checks
    STANDARD = "standard"  # Standard therapeutic safety
    ENHANCED = "enhanced"  # Enhanced safety for vulnerable users
    MAXIMUM = "maximum"  # Maximum safety for crisis situations


@dataclass
class EmotionInterventionMapping:
    """Mapping between emotional states and therapeutic interventions."""
    emotion_type: EmotionalStateType
    intensity_range: tuple[float, float]  # Min, max intensity
    primary_interventions: list[InterventionType] = field(default_factory=list)
    secondary_interventions: list[InterventionType] = field(default_factory=list)
    contraindicated_interventions: list[InterventionType] = field(default_factory=list)
    safety_considerations: list[str] = field(default_factory=list)
    adaptation_strategies: list[str] = field(default_factory=list)
    exposure_therapy_suitability: bool = False
    crisis_threshold: float = 0.8  # Intensity above which crisis protocols activate

    def validate(self) -> bool:
        """Validate emotion-intervention mapping."""
        if not 0.0 <= self.intensity_range[0] <= self.intensity_range[1] <= 1.0:
            raise ValidationError("Invalid intensity range")
        if not 0.0 <= self.crisis_threshold <= 1.0:
            raise ValidationError("Crisis threshold must be between 0.0 and 1.0")
        return True


@dataclass
class AdaptedIntervention:
    """A therapeutic intervention adapted for specific emotional state."""
    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    base_intervention_type: InterventionType = InterventionType.COPING_SKILLS
    emotional_context: EmotionalState = field(default_factory=lambda: MockEmotionalState())
    adapted_content: str = ""
    adaptation_rationale: str = ""
    safety_level: SafetyValidationLevel = SafetyValidationLevel.STANDARD
    exposure_therapy_elements: list[str] = field(default_factory=list)
    narrative_integration_points: list[str] = field(default_factory=list)
    expected_emotional_outcomes: list[str] = field(default_factory=list)
    contraindications_checked: bool = False
    safety_validations_passed: list[str] = field(default_factory=list)
    therapeutic_effectiveness_score: float = 0.7
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate adapted intervention."""
        if not self.adapted_content.strip():
            raise ValidationError("Adapted content cannot be empty")
        if not 0.0 <= self.therapeutic_effectiveness_score <= 1.0:
            raise ValidationError("Effectiveness score must be between 0.0 and 1.0")
        return True


@dataclass
class ExposureTherapySession:
    """A gentle exposure therapy session within narrative context."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exposure_type: ExposureTherapyType = ExposureTherapyType.IMAGINAL
    target_fear_or_trigger: str = ""
    exposure_intensity: float = 0.3  # Start low for safety
    narrative_scenario: str = ""
    safety_measures: list[str] = field(default_factory=list)
    escape_mechanisms: list[str] = field(default_factory=list)
    grounding_techniques: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    termination_criteria: list[str] = field(default_factory=list)
    emotional_monitoring: dict[str, float] = field(default_factory=dict)
    session_duration_minutes: int = 10  # Start with short sessions
    therapist_guidance: str = ""
    post_session_processing: str = ""

    def validate(self) -> bool:
        """Validate exposure therapy session."""
        if not self.target_fear_or_trigger.strip():
            raise ValidationError("Target fear or trigger must be specified")
        if not 0.0 <= self.exposure_intensity <= 1.0:
            raise ValidationError("Exposure intensity must be between 0.0 and 1.0")
        if self.session_duration_minutes <= 0:
            raise ValidationError("Session duration must be positive")
        return True


class EmotionBasedInterventionSelector:
    """Selects therapeutic interventions based on emotional state analysis."""

    def __init__(self):
        """Initialize the emotion-based intervention selector."""
        self.emotion_intervention_mappings = self._initialize_emotion_mappings()
        self.intervention_effectiveness_history = {}
        self.safety_protocols = self._initialize_safety_protocols()
        logger.info("EmotionBasedInterventionSelector initialized")

    def _initialize_emotion_mappings(self) -> dict[EmotionalStateType, list[EmotionInterventionMapping]]:
        """Initialize mappings between emotions and interventions."""
        mappings = {}

        # Anxiety mappings
        mappings[EmotionalStateType.ANXIOUS] = [
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.ANXIOUS,
                intensity_range=(0.0, 0.4),
                primary_interventions=[InterventionType.MINDFULNESS, InterventionType.COPING_SKILLS],
                secondary_interventions=[InterventionType.COGNITIVE_RESTRUCTURING],
                safety_considerations=["Monitor for escalation", "Provide grounding techniques"],
                adaptation_strategies=["Use calming tone", "Focus on present moment"],
                exposure_therapy_suitability=True
            ),
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.ANXIOUS,
                intensity_range=(0.4, 0.7),
                primary_interventions=[InterventionType.COPING_SKILLS, InterventionType.MINDFULNESS],
                secondary_interventions=[InterventionType.COGNITIVE_RESTRUCTURING],
                safety_considerations=["Assess panic risk", "Provide immediate coping tools"],
                adaptation_strategies=["Slower pacing", "More support", "Clear instructions"],
                exposure_therapy_suitability=True
            ),
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.ANXIOUS,
                intensity_range=(0.7, 1.0),
                primary_interventions=[InterventionType.COPING_SKILLS],
                contraindicated_interventions=[InterventionType.EXPOSURE_THERAPY],
                safety_considerations=["Crisis assessment", "Immediate stabilization"],
                adaptation_strategies=["Crisis-focused", "Immediate relief", "Safety first"],
                exposure_therapy_suitability=False,
                crisis_threshold=0.8
            )
        ]

        # Depression mappings
        mappings[EmotionalStateType.DEPRESSED] = [
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.DEPRESSED,
                intensity_range=(0.0, 0.5),
                primary_interventions=[InterventionType.BEHAVIORAL_ACTIVATION, InterventionType.COGNITIVE_RESTRUCTURING],
                secondary_interventions=[InterventionType.COPING_SKILLS],
                safety_considerations=["Monitor hopelessness", "Encourage activity"],
                adaptation_strategies=["Gentle encouragement", "Small steps", "Hope instillation"],
                exposure_therapy_suitability=False
            ),
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.DEPRESSED,
                intensity_range=(0.5, 0.8),
                primary_interventions=[InterventionType.COGNITIVE_RESTRUCTURING, InterventionType.COPING_SKILLS],
                secondary_interventions=[InterventionType.BEHAVIORAL_ACTIVATION],
                safety_considerations=["Suicide risk assessment", "Support system activation"],
                adaptation_strategies=["Validate feelings", "Challenge negative thoughts", "Provide hope"],
                exposure_therapy_suitability=False
            ),
            EmotionInterventionMapping(
                emotion_type=EmotionalStateType.DEPRESSED,
                intensity_range=(0.8, 1.0),
                primary_interventions=[InterventionType.COPING_SKILLS],
                contraindicated_interventions=[InterventionType.EXPOSURE_THERAPY, InterventionType.BEHAVIORAL_ACTIVATION],
                safety_considerations=["Immediate suicide risk assessment", "Crisis intervention"],
                adaptation_strategies=["Crisis support", "Safety planning", "Professional referral"],
                exposure_therapy_suitability=False,
                crisis_threshold=0.8
            )
        ]

        return mappings

    def _initialize_safety_protocols(self) -> dict[SafetyValidationLevel, dict[str, Any]]:
        """Initialize safety protocols for different validation levels."""
        return {
            SafetyValidationLevel.MINIMAL: {
                "required_checks": ["basic_content_safety", "no_harmful_instructions"],
                "crisis_threshold": 0.9,
                "intervention_restrictions": []
            },
            SafetyValidationLevel.STANDARD: {
                "required_checks": [
                    "content_appropriateness", "therapeutic_value", "contraindication_check",
                    "emotional_state_compatibility", "crisis_risk_assessment"
                ],
                "crisis_threshold": 0.8,
                "intervention_restrictions": ["no_flooding_exposure", "no_intensive_processing"]
            },
            SafetyValidationLevel.ENHANCED: {
                "required_checks": [
                    "comprehensive_safety_assessment", "trauma_sensitivity_check",
                    "vulnerability_assessment", "support_system_verification",
                    "professional_oversight_recommended"
                ],
                "crisis_threshold": 0.7,
                "intervention_restrictions": [
                    "no_exposure_therapy", "no_intensive_interventions",
                    "gentle_approaches_only", "frequent_check_ins"
                ]
            },
            SafetyValidationLevel.MAXIMUM: {
                "required_checks": [
                    "crisis_protocol_activation", "immediate_safety_assessment",
                    "professional_intervention_required", "emergency_contact_verification"
                ],
                "crisis_threshold": 0.6,
                "intervention_restrictions": [
                    "crisis_interventions_only", "no_exploratory_work",
                    "stabilization_focus", "immediate_support_only"
                ]
            }
        }

    def select_interventions(self, emotional_state: EmotionalState,
                           session_state: SessionState,
                           narrative_context: NarrativeContext) -> list[AdaptedIntervention]:
        """
        Select and adapt therapeutic interventions based on emotional state.

        Args:
            emotional_state: Current emotional state
            session_state: Current session state
            narrative_context: Current narrative context

        Returns:
            List[AdaptedIntervention]: List of adapted interventions
        """
        try:
            # Get emotion-intervention mappings
            mappings = self.emotion_intervention_mappings.get(emotional_state.primary_emotion, [])

            if not mappings:
                logger.warning(f"No mappings found for emotion: {emotional_state.primary_emotion}")
                return self._get_default_interventions(emotional_state)

            # Find appropriate mapping based on intensity
            selected_mapping = None
            for mapping in mappings:
                min_intensity, max_intensity = mapping.intensity_range
                if min_intensity <= emotional_state.intensity <= max_intensity:
                    selected_mapping = mapping
                    break

            if not selected_mapping:
                logger.warning(f"No mapping found for intensity {emotional_state.intensity}")
                return self._get_default_interventions(emotional_state)

            # Determine safety level
            safety_level = self._determine_safety_level(emotional_state, session_state)

            # Check for crisis conditions
            if emotional_state.intensity >= selected_mapping.crisis_threshold:
                return self._handle_crisis_intervention(emotional_state, session_state, safety_level)

            # Select primary interventions
            adapted_interventions = []

            for intervention_type in selected_mapping.primary_interventions:
                # Check contraindications
                if intervention_type in selected_mapping.contraindicated_interventions:
                    continue

                # Check safety restrictions
                if not self._is_intervention_safe(intervention_type, safety_level):
                    continue

                # Create adapted intervention
                adapted_intervention = self._adapt_intervention(
                    intervention_type, emotional_state, selected_mapping,
                    session_state, narrative_context, safety_level
                )

                if adapted_intervention:
                    adapted_interventions.append(adapted_intervention)

            # Add secondary interventions if needed
            if len(adapted_interventions) < 2:
                for intervention_type in selected_mapping.secondary_interventions:
                    if intervention_type in selected_mapping.contraindicated_interventions:
                        continue

                    if not self._is_intervention_safe(intervention_type, safety_level):
                        continue

                    adapted_intervention = self._adapt_intervention(
                        intervention_type, emotional_state, selected_mapping,
                        session_state, narrative_context, safety_level
                    )

                    if adapted_intervention:
                        adapted_interventions.append(adapted_intervention)
                        if len(adapted_interventions) >= 3:  # Limit to 3 interventions
                            break

            logger.info(f"Selected {len(adapted_interventions)} interventions for {emotional_state.primary_emotion}")
            return adapted_interventions

        except Exception as e:
            logger.error(f"Error selecting interventions: {e}")
            return self._get_default_interventions(emotional_state)

    def _determine_safety_level(self, emotional_state: EmotionalState,
                              session_state: SessionState) -> SafetyValidationLevel:
        """Determine appropriate safety validation level."""
        # Check for crisis indicators
        if emotional_state.intensity >= 0.9:
            return SafetyValidationLevel.MAXIMUM

        # Check for high-risk emotions
        high_risk_emotions = [EmotionalStateType.DEPRESSED, EmotionalStateType.HOPELESS]
        if emotional_state.primary_emotion in high_risk_emotions and emotional_state.intensity >= 0.7:
            return SafetyValidationLevel.ENHANCED

        # Check session history for vulnerability indicators
        if session_state.therapeutic_progress:
            if session_state.therapeutic_progress.overall_progress_score < 30:
                return SafetyValidationLevel.ENHANCED

        # Check for trauma indicators
        trauma_triggers = ["trauma", "abuse", "violence", "loss", "death"]
        for trigger in emotional_state.triggers:
            if any(trauma_word in trigger.lower() for trauma_word in trauma_triggers):
                return SafetyValidationLevel.ENHANCED

        return SafetyValidationLevel.STANDARD

    def _is_intervention_safe(self, intervention_type: InterventionType,
                            safety_level: SafetyValidationLevel) -> bool:
        """Check if intervention is safe for given safety level."""
        protocol = self.safety_protocols.get(safety_level, {})
        restrictions = protocol.get("intervention_restrictions", [])

        # Map intervention types to restriction categories
        restriction_mappings = {
            "no_exposure_therapy": [InterventionType.EXPOSURE_THERAPY],
            "no_intensive_interventions": [InterventionType.TRAUMA_PROCESSING],
            "no_flooding_exposure": [InterventionType.EXPOSURE_THERAPY],
            "crisis_interventions_only": [
                InterventionType.COPING_SKILLS, InterventionType.EMOTIONAL_REGULATION
            ]
        }

        for restriction in restrictions:
            if restriction == "crisis_interventions_only":
                # Only allow crisis-appropriate interventions
                allowed_interventions = restriction_mappings.get(restriction, [])
                if intervention_type not in allowed_interventions:
                    return False
            else:
                # Check if intervention is restricted
                restricted_interventions = restriction_mappings.get(restriction, [])
                if intervention_type in restricted_interventions:
                    return False

        return True

    def _adapt_intervention(self, intervention_type: InterventionType,
                          emotional_state: EmotionalState,
                          mapping: EmotionInterventionMapping,
                          session_state: SessionState,
                          narrative_context: NarrativeContext,
                          safety_level: SafetyValidationLevel) -> AdaptedIntervention | None:
        """Adapt intervention for specific emotional context."""
        try:
            # Generate base intervention content
            base_content = self._generate_base_intervention_content(intervention_type, emotional_state)

            # Apply emotional adaptations
            adapted_content = self._apply_emotional_adaptations(
                base_content, emotional_state, mapping.adaptation_strategies
            )

            # Apply narrative integration
            narrative_integration = self._generate_narrative_integration(
                adapted_content, narrative_context, emotional_state
            )

            # Perform safety validation
            safety_validations = self._perform_safety_validation(
                adapted_content, intervention_type, emotional_state, safety_level
            )

            if not safety_validations["passed"]:
                logger.warning(f"Safety validation failed for {intervention_type}")
                return None

            # Calculate effectiveness score
            effectiveness_score = self._calculate_intervention_effectiveness(
                intervention_type, emotional_state, session_state
            )

            adapted_intervention = AdaptedIntervention(
                base_intervention_type=intervention_type,
                emotional_context=emotional_state,
                adapted_content=adapted_content,
                adaptation_rationale=f"Adapted for {emotional_state.primary_emotion} at intensity {emotional_state.intensity:.2f}",
                safety_level=safety_level,
                narrative_integration_points=narrative_integration,
                expected_emotional_outcomes=self._predict_emotional_outcomes(intervention_type, emotional_state),
                contraindications_checked=True,
                safety_validations_passed=safety_validations["validations"],
                therapeutic_effectiveness_score=effectiveness_score
            )

            adapted_intervention.validate()
            return adapted_intervention

        except Exception as e:
            logger.error(f"Error adapting intervention {intervention_type}: {e}")
            return None

    def _generate_base_intervention_content(self, intervention_type: InterventionType,
                                          emotional_state: EmotionalState) -> str:
        """Generate base content for intervention type."""
        content_templates = {
            InterventionType.MINDFULNESS: {
                "anxious": "Let's take a moment to ground ourselves. Notice your breathing - in and out, naturally and calmly.",
                "depressed": "Sometimes when we're feeling low, connecting with the present moment can provide a gentle anchor.",
                "angry": "When emotions feel intense, mindful breathing can help create space between feeling and reaction.",
                "default": "Let's practice being present in this moment, observing without judgment."
            },
            InterventionType.COPING_SKILLS: {
                "anxious": "Here are some techniques that can help when anxiety feels overwhelming: deep breathing, grounding exercises, and positive self-talk.",
                "depressed": "When depression makes everything feel difficult, small coping strategies can make a big difference.",
                "angry": "Managing anger effectively involves recognizing triggers and having healthy outlets for intense emotions.",
                "default": "Let's explore some coping strategies that can help you navigate difficult emotions."
            },
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "anxious": "Anxiety often comes with thoughts that predict the worst. Let's examine these thoughts and consider alternatives.",
                "depressed": "Depression can create a filter that makes everything seem hopeless. Let's look at this more objectively.",
                "default": "Sometimes our thoughts can be more harsh or extreme than the situation warrants. Let's explore this together."
            }
        }

        emotion_key = emotional_state.primary_emotion.value if hasattr(emotional_state.primary_emotion, 'value') else str(emotional_state.primary_emotion)
        intervention_templates = content_templates.get(intervention_type, {})

        return intervention_templates.get(emotion_key, intervention_templates.get("default", "Let's work together on this."))

    def _apply_emotional_adaptations(self, base_content: str, emotional_state: EmotionalState,
                                   adaptation_strategies: list[str]) -> str:
        """Apply emotional adaptations to intervention content."""
        adapted_content = base_content

        # Apply intensity-based adaptations
        if emotional_state.intensity > 0.7:
            # High intensity - more supportive, slower pacing
            adapted_content = f"I can see you're experiencing intense emotions right now. {adapted_content} We'll take this slowly and gently."
        elif emotional_state.intensity < 0.3:
            # Low intensity - more engaging, encouraging exploration
            adapted_content = f"{adapted_content} This might be a good time to explore this more deeply."

        # Apply strategy-specific adaptations
        for strategy in adaptation_strategies:
            if strategy == "use_calming_tone":
                adapted_content = adapted_content.replace("Let's", "Let's gently").replace("We can", "We can calmly")
            elif strategy == "slower_pacing":
                adapted_content = f"Take your time with this. {adapted_content} There's no rush."
            elif strategy == "more_support":
                adapted_content = f"You're not alone in this. {adapted_content} I'm here to support you."
            elif strategy == "crisis_focused":
                adapted_content = f"Right now, let's focus on keeping you safe. {adapted_content}"

        return adapted_content

    def _generate_narrative_integration(self, content: str, narrative_context: NarrativeContext,
                                      emotional_state: EmotionalState) -> list[str]:
        """Generate narrative integration points for intervention."""
        integration_points = []

        # Character-based integration
        if narrative_context.active_characters:
            main_character = narrative_context.active_characters[0].name if narrative_context.active_characters else "Guide"
            integration_points.append(f"{main_character} notices your emotional state and offers gentle guidance")
            integration_points.append(f"Through {main_character}'s wisdom, you learn new ways to cope")

        # Setting-based integration
        if hasattr(narrative_context, 'current_location') and narrative_context.current_location:
            integration_points.append(f"The peaceful environment of {narrative_context.current_location} supports your healing process")

        # Emotional state integration
        emotion_name = emotional_state.primary_emotion.value if hasattr(emotional_state.primary_emotion, 'value') else str(emotional_state.primary_emotion)
        integration_points.append(f"The story acknowledges your {emotion_name} feelings and provides a safe space to explore them")

        return integration_points

    def _perform_safety_validation(self, content: str, intervention_type: InterventionType,
                                 emotional_state: EmotionalState,
                                 safety_level: SafetyValidationLevel) -> dict[str, Any]:
        """Perform safety validation for adapted intervention."""
        validations = []
        passed = True

        protocol = self.safety_protocols.get(safety_level, {})
        required_checks = protocol.get("required_checks", [])

        for check in required_checks:
            if check == "basic_content_safety":
                # Check for harmful content
                harmful_keywords = ["hurt yourself", "give up", "hopeless", "end it all"]
                if any(keyword in content.lower() for keyword in harmful_keywords):
                    passed = False
                else:
                    validations.append("basic_content_safety")

            elif check == "therapeutic_value":
                # Ensure content has therapeutic value
                therapeutic_keywords = ["support", "help", "cope", "manage", "understand", "explore"]
                if any(keyword in content.lower() for keyword in therapeutic_keywords):
                    validations.append("therapeutic_value")
                else:
                    passed = False

            elif check == "crisis_risk_assessment":
                # Check if intervention is appropriate for crisis level
                if emotional_state.intensity >= 0.8:
                    crisis_appropriate = intervention_type in [InterventionType.COPING_SKILLS, InterventionType.EMOTIONAL_REGULATION]
                    if crisis_appropriate:
                        validations.append("crisis_risk_assessment")
                    else:
                        passed = False
                else:
                    validations.append("crisis_risk_assessment")

        return {"passed": passed, "validations": validations}

    def _calculate_intervention_effectiveness(self, intervention_type: InterventionType,
                                            emotional_state: EmotionalState,
                                            session_state: SessionState) -> float:
        """Calculate expected effectiveness of intervention."""
        base_effectiveness = 0.7  # Base effectiveness score

        # Adjust based on emotional state intensity
        if emotional_state.intensity > 0.8:
            base_effectiveness -= 0.1  # High intensity may reduce effectiveness
        elif emotional_state.intensity < 0.3:
            base_effectiveness += 0.1  # Low intensity may increase effectiveness

        # Adjust based on intervention history
        if session_state.therapeutic_progress:
            for completed_intervention in session_state.therapeutic_progress.completed_interventions:
                if completed_intervention.intervention_type == intervention_type:
                    # Use historical effectiveness
                    historical_effectiveness = completed_intervention.effectiveness_rating / 5.0  # Convert to 0-1 scale
                    base_effectiveness = (base_effectiveness + historical_effectiveness) / 2
                    break

        return max(0.0, min(1.0, base_effectiveness))

    def _predict_emotional_outcomes(self, intervention_type: InterventionType,
                                  emotional_state: EmotionalState) -> list[str]:
        """Predict expected emotional outcomes from intervention."""

        emotion_name = emotional_state.primary_emotion.value if hasattr(emotional_state.primary_emotion, 'value') else str(emotional_state.primary_emotion)

        outcome_mappings = {
            InterventionType.MINDFULNESS: [
                f"Reduced {emotion_name} intensity",
                "Increased present-moment awareness",
                "Greater emotional regulation"
            ],
            InterventionType.COPING_SKILLS: [
                f"Better management of {emotion_name} feelings",
                "Increased sense of control",
                "Improved emotional resilience"
            ],
            InterventionType.COGNITIVE_RESTRUCTURING: [
                "More balanced thinking patterns",
                f"Reduced {emotion_name} intensity",
                "Increased emotional flexibility"
            ]
        }

        return outcome_mappings.get(intervention_type, ["Improved emotional well-being"])

    def _get_default_interventions(self, emotional_state: EmotionalState) -> list[AdaptedIntervention]:
        """Get default interventions when specific mappings aren't available."""
        default_intervention = AdaptedIntervention(
            base_intervention_type=InterventionType.COPING_SKILLS,
            emotional_context=emotional_state,
            adapted_content="I'm here to support you. Let's work together to find ways to help you feel better.",
            adaptation_rationale="Default supportive intervention",
            safety_level=SafetyValidationLevel.STANDARD,
            contraindications_checked=True,
            safety_validations_passed=["basic_safety"],
            therapeutic_effectiveness_score=0.6
        )

        return [default_intervention]

    def _handle_crisis_intervention(self, emotional_state: EmotionalState,
                                  session_state: SessionState,
                                  safety_level: SafetyValidationLevel) -> list[AdaptedIntervention]:
        """Handle crisis-level emotional states."""
        crisis_intervention = AdaptedIntervention(
            base_intervention_type=InterventionType.COPING_SKILLS,
            emotional_context=emotional_state,
            adapted_content="I'm very concerned about how you're feeling right now. Let's focus on keeping you safe. You don't have to go through this alone.",
            adaptation_rationale="Crisis intervention for high emotional intensity",
            safety_level=SafetyValidationLevel.MAXIMUM,
            narrative_integration_points=[
                "Character expresses immediate concern and care",
                "Story shifts to focus on safety and support",
                "Crisis resources are provided within narrative context"
            ],
            expected_emotional_outcomes=["Immediate emotional stabilization", "Increased sense of safety"],
            contraindications_checked=True,
            safety_validations_passed=["crisis_protocol_activated"],
            therapeutic_effectiveness_score=0.9
        )

        return [crisis_intervention]


class SafeExposureTherapyManager:
    """Manages gentle exposure therapy opportunities within safe narrative contexts."""

    def __init__(self):
        """Initialize the safe exposure therapy manager."""
        self.exposure_protocols = self._initialize_exposure_protocols()
        self.safety_guidelines = self._initialize_safety_guidelines()
        self.grounding_techniques = self._initialize_grounding_techniques()
        logger.info("SafeExposureTherapyManager initialized")

    def _initialize_exposure_protocols(self) -> dict[ExposureTherapyType, dict[str, Any]]:
        """Initialize exposure therapy protocols."""
        return {
            ExposureTherapyType.IMAGINAL: {
                "description": "Gentle exposure through narrative imagination",
                "intensity_range": (0.1, 0.4),
                "session_duration": 5,  # minutes
                "safety_measures": [
                    "Constant emotional monitoring",
                    "Immediate escape options",
                    "Grounding techniques available",
                    "Therapist guidance throughout"
                ],
                "contraindications": ["active_crisis", "severe_trauma", "dissociation_risk"]
            },
            ExposureTherapyType.SYSTEMATIC: {
                "description": "Gradual systematic exposure through story progression",
                "intensity_range": (0.1, 0.6),
                "session_duration": 10,
                "safety_measures": [
                    "Hierarchical approach",
                    "User-controlled pacing",
                    "Regular check-ins",
                    "Mastery before progression"
                ],
                "contraindications": ["crisis_state", "severe_anxiety", "trauma_triggers"]
            }
        }

    def _initialize_safety_guidelines(self) -> dict[str, list[str]]:
        """Initialize safety guidelines for exposure therapy."""
        return {
            "pre_session": [
                "Assess current emotional state",
                "Verify user consent and readiness",
                "Establish safety signals and escape plans",
                "Ensure grounding techniques are available",
                "Set clear session boundaries"
            ],
            "during_session": [
                "Monitor emotional intensity continuously",
                "Respect user's pace and comfort level",
                "Provide immediate support if needed",
                "Use grounding techniques as necessary",
                "Maintain therapeutic alliance"
            ],
            "post_session": [
                "Process the experience thoroughly",
                "Validate user's courage and effort",
                "Assess emotional state and provide support",
                "Plan follow-up and next steps",
                "Document session outcomes"
            ]
        }

    def _initialize_grounding_techniques(self) -> dict[str, list[str]]:
        """Initialize grounding techniques for exposure sessions."""
        return {
            "sensory_grounding": [
                "5-4-3-2-1 technique (5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste)",
                "Focus on physical sensations (feet on ground, hands on surface)",
                "Deep breathing with focus on breath sensations",
                "Progressive muscle relaxation"
            ],
            "cognitive_grounding": [
                "Remind yourself: 'This is just a story, I am safe'",
                "Count backwards from 100 by 7s",
                "Name categories (colors, animals, countries)",
                "Recite a familiar poem or song"
            ],
            "emotional_grounding": [
                "Self-compassion phrases: 'This is difficult, but I'm being brave'",
                "Remind yourself of your support system",
                "Visualize a safe, peaceful place",
                "Connect with your values and reasons for healing"
            ]
        }

    def assess_exposure_readiness(self, emotional_state: EmotionalState,
                                session_state: SessionState,
                                target_fear: str) -> dict[str, Any]:
        """
        Assess if user is ready for exposure therapy.

        Args:
            emotional_state: Current emotional state
            session_state: Current session state
            target_fear: The fear or trigger to address

        Returns:
            Dict containing readiness assessment
        """
        try:
            assessment = {
                "ready": False,
                "readiness_score": 0.0,
                "recommended_type": None,
                "safety_concerns": [],
                "prerequisites": [],
                "contraindications": []
            }

            # Check basic readiness criteria
            readiness_score = 0.0

            # Emotional stability check
            if emotional_state.intensity < 0.7:
                readiness_score += 0.3
            else:
                assessment["safety_concerns"].append("High emotional intensity")

            # Check for crisis indicators
            crisis_emotions = [EmotionalStateType.DEPRESSED, EmotionalStateType.HOPELESS]
            if emotional_state.primary_emotion in crisis_emotions and emotional_state.intensity > 0.8:
                assessment["contraindications"].append("Crisis-level emotional state")
                return assessment

            # Check therapeutic progress
            if session_state.therapeutic_progress:
                if session_state.therapeutic_progress.overall_progress_score > 40:
                    readiness_score += 0.2
                else:
                    assessment["prerequisites"].append("Build more therapeutic foundation")

                # Check coping skills
                if len(session_state.therapeutic_progress.coping_strategies_learned) >= 2:
                    readiness_score += 0.2
                else:
                    assessment["prerequisites"].append("Learn more coping strategies")

            # Check for trauma indicators
            trauma_keywords = ["trauma", "abuse", "violence", "assault"]
            if any(keyword in target_fear.lower() for keyword in trauma_keywords):
                assessment["safety_concerns"].append("Trauma-related content requires extra caution")
                readiness_score -= 0.1

            # Determine readiness
            assessment["readiness_score"] = max(0.0, min(1.0, readiness_score))
            assessment["ready"] = readiness_score >= 0.5

            # Recommend exposure type
            if assessment["ready"]:
                if readiness_score >= 0.7:
                    assessment["recommended_type"] = ExposureTherapyType.SYSTEMATIC
                else:
                    assessment["recommended_type"] = ExposureTherapyType.IMAGINAL

            logger.info(f"Exposure readiness assessment: {assessment['readiness_score']:.2f}")
            return assessment

        except Exception as e:
            logger.error(f"Error assessing exposure readiness: {e}")
            return {
                "ready": False,
                "readiness_score": 0.0,
                "safety_concerns": ["Assessment error - manual evaluation needed"]
            }

    def create_exposure_session(self, exposure_type: ExposureTherapyType,
                              target_fear: str,
                              emotional_state: EmotionalState,
                              narrative_context: NarrativeContext) -> ExposureTherapySession | None:
        """
        Create a safe exposure therapy session within narrative context.

        Args:
            exposure_type: Type of exposure therapy
            target_fear: The fear or trigger to address
            emotional_state: Current emotional state
            narrative_context: Current narrative context

        Returns:
            ExposureTherapySession or None if not safe
        """
        try:
            protocol = self.exposure_protocols.get(exposure_type, {})

            if not protocol:
                logger.error(f"No protocol found for exposure type: {exposure_type}")
                return None

            # Check contraindications
            contraindications = protocol.get("contraindications", [])
            if self._check_contraindications(contraindications, emotional_state):
                logger.warning("Contraindications present for exposure therapy")
                return None

            # Determine appropriate intensity
            min_intensity, max_intensity = protocol.get("intensity_range", (0.1, 0.3))
            exposure_intensity = min_intensity + (emotional_state.intensity * 0.1)  # Start very low
            exposure_intensity = max(min_intensity, min(max_intensity, exposure_intensity))

            # Create narrative scenario
            narrative_scenario = self._create_exposure_scenario(
                target_fear, exposure_intensity, narrative_context
            )

            # Set up safety measures
            safety_measures = protocol.get("safety_measures", [])
            escape_mechanisms = [
                "Say 'I need to stop' to immediately end the exposure",
                "Take three deep breaths to pause and ground yourself",
                "Remind yourself 'This is just a story, I am safe'",
                "Focus on the supportive character who is with you"
            ]

            # Select appropriate grounding techniques
            grounding_techniques = []
            for _category, techniques in self.grounding_techniques.items():
                grounding_techniques.extend(techniques[:2])  # Take 2 from each category

            session = ExposureTherapySession(
                exposure_type=exposure_type,
                target_fear_or_trigger=target_fear,
                exposure_intensity=exposure_intensity,
                narrative_scenario=narrative_scenario,
                safety_measures=safety_measures,
                escape_mechanisms=escape_mechanisms,
                grounding_techniques=grounding_techniques,
                success_criteria=[
                    "Complete the scenario without overwhelming distress",
                    "Use coping strategies effectively",
                    "Maintain sense of safety throughout"
                ],
                termination_criteria=[
                    "Emotional intensity exceeds 0.8",
                    "User requests to stop",
                    "Signs of dissociation or panic",
                    "Loss of therapeutic alliance"
                ],
                session_duration_minutes=protocol.get("session_duration", 5),
                therapist_guidance=f"I'll be with you throughout this gentle exploration of {target_fear}. We'll go slowly and you're in complete control.",
                post_session_processing="After we finish, we'll talk about how that felt and what you learned about your strength and resilience."
            )

            session.validate()
            logger.info(f"Created exposure session for {target_fear} at intensity {exposure_intensity:.2f}")
            return session

        except Exception as e:
            logger.error(f"Error creating exposure session: {e}")
            return None

    def _check_contraindications(self, contraindications: list[str],
                               emotional_state: EmotionalState) -> bool:
        """Check if any contraindications are present."""
        for contraindication in contraindications:
            if contraindication == "active_crisis" and emotional_state.intensity > 0.8:
                return True
            elif contraindication == "severe_trauma" and "trauma" in str(emotional_state.triggers):
                return True
            elif contraindication == "crisis_state" and emotional_state.intensity > 0.9:
                return True

        return False

    def _create_exposure_scenario(self, target_fear: str, intensity: float,
                                narrative_context: NarrativeContext) -> str:
        """Create a narrative scenario for exposure therapy."""
        # Get current setting
        setting = "a peaceful, safe space"
        if hasattr(narrative_context, 'current_location') and narrative_context.current_location:
            setting = narrative_context.current_location

        # Get supportive character
        character_name = "your wise guide"
        if narrative_context.active_characters:
            character_name = narrative_context.active_characters[0].name

        # Create gentle exposure scenario based on fear type
        if "social" in target_fear.lower():
            scenario = f"In {setting}, {character_name} gently suggests practicing a brief, comfortable social interaction. You feel supported and safe, knowing you can stop at any time."
        elif "performance" in target_fear.lower():
            scenario = f"Within the safety of {setting}, {character_name} invites you to imagine sharing something small about yourself. The environment feels completely supportive."
        elif "abandonment" in target_fear.lower():
            scenario = f"In {setting}, {character_name} helps you explore the feeling of connection and security, knowing that healthy relationships can weather temporary separations."
        else:
            scenario = f"In the safety of {setting}, with {character_name} by your side, you gently approach the edge of your comfort zone regarding {target_fear}, knowing you're completely in control."

        # Adjust intensity
        if intensity < 0.2:
            scenario += " This feels very manageable and safe."
        elif intensity < 0.4:
            scenario += " You notice some mild nervousness, but feel supported and capable."
        else:
            scenario += " While this feels challenging, you have all the tools and support you need."

        return scenario


class EmotionInterventionIntegrator:
    """Main class for integrating emotional recognition with therapeutic interventions."""

    def __init__(self):
        """Initialize the emotion-intervention integrator."""
        self.intervention_selector = EmotionBasedInterventionSelector()
        self.exposure_manager = SafeExposureTherapyManager()
        self.integration_history = {}
        self.safety_monitor = self._initialize_safety_monitor()
        logger.info("EmotionInterventionIntegrator initialized")

    def _initialize_safety_monitor(self) -> dict[str, Any]:
        """Initialize safety monitoring system."""
        return {
            "crisis_thresholds": {
                "emotional_intensity": 0.8,
                "intervention_failure_rate": 0.7,
                "session_distress_level": 0.8
            },
            "safety_protocols": {
                "mandatory_checks": ["crisis_assessment", "contraindication_review", "safety_validation"],
                "escalation_triggers": ["repeated_intervention_failures", "increasing_distress", "crisis_indicators"],
                "emergency_procedures": ["immediate_stabilization", "professional_referral", "crisis_resources"]
            }
        }

    def integrate_emotion_with_interventions(self, emotional_analysis: EmotionalAnalysisResult,
                                           session_state: SessionState,
                                           narrative_context: NarrativeContext) -> dict[str, Any]:
        """
        Main integration method that connects emotional recognition with therapeutic interventions.

        Args:
            emotional_analysis: Results from emotional state recognition
            session_state: Current session state
            narrative_context: Current narrative context

        Returns:
            Dict containing integrated intervention recommendations
        """
        try:
            integration_result = {
                "selected_interventions": [],
                "exposure_therapy_session": None,
                "safety_assessment": {},
                "adaptation_metadata": {},
                "crisis_response": None,
                "integration_success": False
            }

            # Perform comprehensive safety assessment
            safety_assessment = self._perform_comprehensive_safety_assessment(
                emotional_analysis, session_state, narrative_context
            )
            integration_result["safety_assessment"] = safety_assessment

            # Handle crisis situations first
            if safety_assessment["crisis_detected"]:
                crisis_response = self._handle_crisis_integration(
                    emotional_analysis, session_state, safety_assessment
                )
                integration_result["crisis_response"] = crisis_response
                integration_result["integration_success"] = True
                return integration_result

            # Select appropriate interventions based on emotional state
            selected_interventions = self.intervention_selector.select_interventions(
                emotional_analysis.detected_emotion, session_state, narrative_context
            )
            integration_result["selected_interventions"] = selected_interventions

            # Assess exposure therapy opportunities
            if self._should_consider_exposure_therapy(emotional_analysis, session_state):
                exposure_session = self._create_safe_exposure_opportunity(
                    emotional_analysis, session_state, narrative_context
                )
                integration_result["exposure_therapy_session"] = exposure_session

            # Generate adaptation metadata
            adaptation_metadata = self._generate_adaptation_metadata(
                emotional_analysis, selected_interventions, session_state
            )
            integration_result["adaptation_metadata"] = adaptation_metadata

            # Validate final integration
            integration_validation = self._validate_integration(integration_result, safety_assessment)
            integration_result["integration_success"] = integration_validation["success"]

            if not integration_validation["success"]:
                integration_result["fallback_interventions"] = self._generate_fallback_interventions(
                    emotional_analysis.detected_emotion
                )

            # Record integration for learning
            self._record_integration_attempt(emotional_analysis, integration_result)

            logger.info(f"Emotion-intervention integration completed: {integration_result['integration_success']}")
            return integration_result

        except Exception as e:
            logger.error(f"Error in emotion-intervention integration: {e}")
            return self._generate_emergency_integration_response(emotional_analysis)

    def _perform_comprehensive_safety_assessment(self, emotional_analysis: EmotionalAnalysisResult,
                                                session_state: SessionState,
                                                narrative_context: NarrativeContext) -> dict[str, Any]:
        """Perform comprehensive safety assessment before intervention selection."""
        assessment = {
            "crisis_detected": False,
            "crisis_level": "none",
            "safety_concerns": [],
            "protective_factors": [],
            "intervention_restrictions": [],
            "monitoring_requirements": []
        }

        # Check emotional intensity
        if emotional_analysis.detected_emotion.intensity >= self.safety_monitor["crisis_thresholds"]["emotional_intensity"]:
            assessment["crisis_detected"] = True
            assessment["crisis_level"] = "high"
            assessment["safety_concerns"].append("High emotional intensity detected")

        # Check for crisis indicators in analysis
        if emotional_analysis.crisis_indicators:
            assessment["crisis_detected"] = True
            assessment["crisis_level"] = "severe"
            assessment["safety_concerns"].extend(emotional_analysis.crisis_indicators)

        # Check therapeutic progress for concerning patterns
        if session_state.therapeutic_progress:
            failure_rate = self._calculate_intervention_failure_rate(session_state.therapeutic_progress)
            if failure_rate >= self.safety_monitor["crisis_thresholds"]["intervention_failure_rate"]:
                assessment["safety_concerns"].append("High intervention failure rate")
                assessment["intervention_restrictions"].append("avoid_complex_interventions")

        # Identify protective factors
        protective_factors = []
        if session_state.therapeutic_progress:
            if len(session_state.therapeutic_progress.coping_strategies_learned) > 0:
                protective_factors.append("Has learned coping strategies")
            if session_state.therapeutic_progress.overall_progress_score > 30:
                protective_factors.append("Positive therapeutic progress")

        if session_state.character_states:
            positive_relationships = sum(1 for char_state in session_state.character_states.values()
                                       if any(score > 0.5 for score in char_state.relationship_scores.values()))
            if positive_relationships > 0:
                protective_factors.append("Positive therapeutic relationships")

        assessment["protective_factors"] = protective_factors

        # Determine monitoring requirements
        if assessment["crisis_detected"]:
            assessment["monitoring_requirements"] = ["continuous_emotional_monitoring", "immediate_support_availability"]
        elif len(assessment["safety_concerns"]) > 0:
            assessment["monitoring_requirements"] = ["enhanced_monitoring", "regular_check_ins"]
        else:
            assessment["monitoring_requirements"] = ["standard_monitoring"]

        return assessment

    def _calculate_intervention_failure_rate(self, therapeutic_progress: TherapeuticProgress) -> float:
        """Calculate the failure rate of recent interventions."""
        if not therapeutic_progress.completed_interventions:
            return 0.0

        recent_interventions = therapeutic_progress.completed_interventions[-5:]  # Last 5 interventions
        failed_interventions = sum(1 for intervention in recent_interventions
                                 if intervention.effectiveness_rating < 3.0)

        return failed_interventions / len(recent_interventions)

    def _handle_crisis_integration(self, emotional_analysis: EmotionalAnalysisResult,
                                 session_state: SessionState,
                                 safety_assessment: dict[str, Any]) -> dict[str, Any]:
        """Handle integration when crisis is detected."""
        crisis_response = {
            "intervention_type": "crisis_intervention",
            "immediate_actions": [
                "Provide immediate emotional support",
                "Ensure user safety",
                "Activate crisis resources",
                "Maintain therapeutic connection"
            ],
            "adapted_content": "I'm very concerned about how you're feeling right now. Your safety is the most important thing. Let's focus on getting you the support you need.",
            "safety_resources": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Emergency Services: 911"
            ],
            "narrative_adaptation": "The story immediately shifts to focus on safety and support, with characters expressing deep concern and providing immediate help.",
            "follow_up_required": True,
            "professional_referral_needed": True
        }

        return crisis_response

    def _should_consider_exposure_therapy(self, emotional_analysis: EmotionalAnalysisResult,
                                        session_state: SessionState) -> bool:
        """Determine if exposure therapy should be considered."""
        # Don't consider exposure therapy in crisis situations
        if emotional_analysis.detected_emotion.intensity > 0.8:
            return False

        # Check if user has sufficient coping skills
        if session_state.therapeutic_progress:
            if len(session_state.therapeutic_progress.coping_strategies_learned) < 2:
                return False

        # Check for appropriate emotional states
        suitable_emotions = [EmotionalStateType.ANXIOUS, EmotionalStateType.WORRIED]
        if emotional_analysis.detected_emotion.primary_emotion not in suitable_emotions:
            return False

        # Check for identifiable triggers
        if not emotional_analysis.detected_triggers:
            return False

        return True

    def _create_safe_exposure_opportunity(self, emotional_analysis: EmotionalAnalysisResult,
                                        session_state: SessionState,
                                        narrative_context: NarrativeContext) -> ExposureTherapySession | None:
        """Create a safe exposure therapy opportunity if appropriate."""
        if not emotional_analysis.detected_triggers:
            return None

        # Select the most appropriate trigger to address
        primary_trigger = emotional_analysis.detected_triggers[0]
        target_fear = primary_trigger.description

        # Assess readiness for exposure
        readiness_assessment = self.exposure_manager.assess_exposure_readiness(
            emotional_analysis.detected_emotion, session_state, target_fear
        )

        if not readiness_assessment["ready"]:
            logger.info(f"User not ready for exposure therapy: {readiness_assessment['safety_concerns']}")
            return None

        # Create exposure session
        exposure_session = self.exposure_manager.create_exposure_session(
            readiness_assessment["recommended_type"],
            target_fear,
            emotional_analysis.detected_emotion,
            narrative_context
        )

        return exposure_session

    def _generate_adaptation_metadata(self, emotional_analysis: EmotionalAnalysisResult,
                                    selected_interventions: list[AdaptedIntervention],
                                    session_state: SessionState) -> dict[str, Any]:
        """Generate metadata about the adaptation process."""
        metadata = {
            "emotional_context": {
                "primary_emotion": emotional_analysis.detected_emotion.primary_emotion.value if hasattr(emotional_analysis.detected_emotion.primary_emotion, 'value') else str(emotional_analysis.detected_emotion.primary_emotion),
                "intensity": emotional_analysis.detected_emotion.intensity,
                "confidence": emotional_analysis.confidence_level,
                "triggers_identified": len(emotional_analysis.detected_triggers)
            },
            "intervention_selection": {
                "total_interventions": len(selected_interventions),
                "intervention_types": [intervention.base_intervention_type.value if hasattr(intervention.base_intervention_type, 'value') else str(intervention.base_intervention_type) for intervention in selected_interventions],
                "average_effectiveness": statistics.mean([intervention.therapeutic_effectiveness_score for intervention in selected_interventions]) if selected_interventions else 0.0,
                "safety_level": selected_interventions[0].safety_level.value if selected_interventions and hasattr(selected_interventions[0].safety_level, 'value') else "standard"
            },
            "adaptation_strategies": {
                "narrative_integration": any("narrative" in str(intervention.narrative_integration_points) for intervention in selected_interventions),
                "emotional_adaptation": True,
                "safety_validation": all(intervention.contraindications_checked for intervention in selected_interventions)
            },
            "session_context": {
                "therapeutic_progress_score": session_state.therapeutic_progress.overall_progress_score if session_state.therapeutic_progress else 0,
                "coping_strategies_available": len(session_state.therapeutic_progress.coping_strategies_learned) if session_state.therapeutic_progress else 0,
                "character_relationships": len(session_state.character_states) if session_state.character_states else 0
            }
        }

        return metadata

    def _validate_integration(self, integration_result: dict[str, Any],
                            safety_assessment: dict[str, Any]) -> dict[str, Any]:
        """Validate the final integration result."""
        validation = {
            "success": True,
            "validation_checks": [],
            "concerns": []
        }

        # Check if interventions were selected
        if not integration_result["selected_interventions"] and not integration_result["crisis_response"]:
            validation["success"] = False
            validation["concerns"].append("No interventions selected")

        # Validate safety compliance
        if safety_assessment["crisis_detected"] and not integration_result["crisis_response"]:
            validation["success"] = False
            validation["concerns"].append("Crisis detected but no crisis response generated")

        # Check intervention safety
        for intervention in integration_result["selected_interventions"]:
            if not intervention.contraindications_checked:
                validation["success"] = False
                validation["concerns"].append("Intervention safety not validated")
                break

        # Validate exposure therapy safety
        if integration_result["exposure_therapy_session"]:
            exposure_session = integration_result["exposure_therapy_session"]
            if exposure_session.exposure_intensity > 0.5:
                validation["concerns"].append("Exposure intensity may be too high")

        validation["validation_checks"] = [
            "intervention_selection_validated",
            "safety_assessment_completed",
            "crisis_handling_appropriate",
            "exposure_therapy_safety_checked"
        ]

        return validation

    def _generate_fallback_interventions(self, emotional_state: EmotionalState) -> list[AdaptedIntervention]:
        """Generate safe fallback interventions when primary integration fails."""
        fallback_intervention = AdaptedIntervention(
            base_intervention_type=InterventionType.COPING_SKILLS,
            emotional_context=emotional_state,
            adapted_content="I want to make sure you feel supported right now. Let's focus on some gentle coping strategies that can help you feel more grounded and safe.",
            adaptation_rationale="Safe fallback intervention when primary integration failed",
            safety_level=SafetyValidationLevel.ENHANCED,
            narrative_integration_points=[
                "Character provides immediate comfort and support",
                "Story creates a safe, nurturing environment",
                "Focus shifts to user's immediate well-being"
            ],
            expected_emotional_outcomes=["Increased sense of safety", "Emotional stabilization"],
            contraindications_checked=True,
            safety_validations_passed=["fallback_safety_protocol"],
            therapeutic_effectiveness_score=0.7
        )

        return [fallback_intervention]

    def _record_integration_attempt(self, emotional_analysis: EmotionalAnalysisResult,
                                  integration_result: dict[str, Any]) -> None:
        """Record integration attempt for learning and improvement."""
        user_id = "current_user"  # Would be extracted from session in real implementation

        if user_id not in self.integration_history:
            self.integration_history[user_id] = []

        record = {
            "timestamp": datetime.now(),
            "emotional_state": {
                "emotion": emotional_analysis.detected_emotion.primary_emotion.value if hasattr(emotional_analysis.detected_emotion.primary_emotion, 'value') else str(emotional_analysis.detected_emotion.primary_emotion),
                "intensity": emotional_analysis.detected_emotion.intensity
            },
            "interventions_selected": len(integration_result["selected_interventions"]),
            "integration_success": integration_result["integration_success"],
            "crisis_detected": integration_result["safety_assessment"].get("crisis_detected", False),
            "exposure_therapy_used": integration_result["exposure_therapy_session"] is not None
        }

        self.integration_history[user_id].append(record)

        # Keep only last 50 records per user
        if len(self.integration_history[user_id]) > 50:
            self.integration_history[user_id] = self.integration_history[user_id][-50:]

    def _generate_emergency_integration_response(self, emotional_analysis: EmotionalAnalysisResult) -> dict[str, Any]:
        """Generate emergency response when integration fails."""
        return {
            "selected_interventions": [],
            "exposure_therapy_session": None,
            "safety_assessment": {"crisis_detected": True, "crisis_level": "unknown"},
            "adaptation_metadata": {},
            "crisis_response": {
                "intervention_type": "emergency_support",
                "adapted_content": "I'm here to support you. If you're in crisis, please reach out for immediate help. Your safety and well-being are the most important things right now.",
                "safety_resources": [
                    "National Suicide Prevention Lifeline: 988",
                    "Crisis Text Line: Text HOME to 741741",
                    "Emergency Services: 911"
                ],
                "immediate_actions": ["Ensure user safety", "Provide crisis resources", "Seek professional help"]
            },
            "integration_success": False,
            "error_handled": True
        }
