"""
Adaptive Response System and Crisis Support for TTA Prototype

This module implements an adaptive response system that adjusts narrative tone and support
based on user emotional states. It includes crisis detection mechanisms, immediate support
systems, and emotional growth acknowledgment and reinforcement.

Classes:
    AdaptiveResponseSystem: Main class for adaptive narrative responses
    CrisisDetectionSystem: Specialized crisis detection and intervention
    EmotionalGrowthTracker: Tracks and reinforces emotional progress
    NarrativeToneAdapter: Adapts narrative tone based on emotional state
"""

import logging
import re

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
        CharacterState,
        DialogueContext,
        EmotionalState,
        EmotionalStateType,
        NarrativeContext,
        SessionState,
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
    from .emotional_state_recognition import (
        EmotionalAnalysisResult,
        EmotionalPattern,
        EmotionalStateRecognitionResponse,
        EmotionalTrigger,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            CharacterState,
            DialogueContext,
            EmotionalState,
            EmotionalStateType,
            NarrativeContext,
            SessionState,
            TherapeuticProgress,
            ValidationError,
        )
        from emotional_state_recognition import (
            EmotionalAnalysisResult,
            EmotionalPattern,
            EmotionalStateRecognitionResponse,
            EmotionalTrigger,
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

        class MockTherapeuticLLMClient:
            def generate_adaptive_response(self, context, emotional_state):
                return {"response": "Mock adaptive response", "tone": "supportive"}

        class MockEmotionalAnalysisResult:
            def __init__(self):
                self.detected_emotion = MockEmotionalState()
                self.crisis_indicators = []
                self.therapeutic_recommendations = []

        # Set the mock classes
        EmotionalState = MockEmotionalState
        EmotionalStateType = MockEmotionalStateType
        TherapeuticLLMClient = MockTherapeuticLLMClient
        EmotionalAnalysisResult = MockEmotionalAnalysisResult

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Levels of crisis severity."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    EMERGENCY = "emergency"


class ResponseTone(Enum):
    """Types of narrative response tones."""
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    CALMING = "calming"
    ENERGIZING = "energizing"
    VALIDATING = "validating"
    GROUNDING = "grounding"
    EMPOWERING = "empowering"
    CRISIS_FOCUSED = "crisis_focused"


class AdaptationStrategy(Enum):
    """Strategies for adaptive responses."""
    TONE_ADJUSTMENT = "tone_adjustment"
    PACING_MODIFICATION = "pacing_modification"
    CONTENT_FILTERING = "content_filtering"
    SUPPORT_ESCALATION = "support_escalation"
    CRISIS_INTERVENTION = "crisis_intervention"
    GROWTH_REINFORCEMENT = "growth_reinforcement"


@dataclass
class CrisisIndicator:
    """Represents a detected crisis indicator."""
    indicator_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    indicator_type: str = ""
    severity_level: CrisisLevel = CrisisLevel.LOW
    description: str = ""
    detected_text: str = ""
    confidence_score: float = 0.5  # 0.0 to 1.0
    immediate_action_required: bool = False
    recommended_interventions: list[str] = field(default_factory=list)
    professional_referral_needed: bool = False
    safety_resources: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate crisis indicator data."""
        if not self.description.strip():
            raise ValidationError("Crisis indicator description cannot be empty")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        return True


@dataclass
class AdaptiveResponse:
    """Represents an adaptive response to user emotional state."""
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_content: str = ""
    adapted_content: str = ""
    response_tone: ResponseTone = ResponseTone.SUPPORTIVE
    adaptation_strategies: list[AdaptationStrategy] = field(default_factory=list)
    emotional_context: EmotionalState | None = None
    crisis_level: CrisisLevel = CrisisLevel.NONE
    support_elements: list[str] = field(default_factory=list)
    therapeutic_value: float = 0.5  # 0.0 to 1.0
    safety_considerations: list[str] = field(default_factory=list)
    follow_up_needed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate adaptive response data."""
        if not self.adapted_content.strip():
            raise ValidationError("Adapted content cannot be empty")
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValidationError("Therapeutic value must be between 0.0 and 1.0")
        return True


@dataclass
class EmotionalGrowthMoment:
    """Represents a moment of emotional growth to be acknowledged."""
    moment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    growth_type: str = ""
    description: str = ""
    previous_state: EmotionalState | None = None
    current_state: EmotionalState | None = None
    improvement_indicators: list[str] = field(default_factory=list)
    coping_strategies_used: list[str] = field(default_factory=list)
    reinforcement_message: str = ""
    celebration_level: str = "moderate"  # subtle, moderate, enthusiastic
    therapeutic_significance: float = 0.5  # 0.0 to 1.0
    detected_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate emotional growth moment data."""
        if not self.description.strip():
            raise ValidationError("Growth moment description cannot be empty")
        if not 0.0 <= self.therapeutic_significance <= 1.0:
            raise ValidationError("Therapeutic significance must be between 0.0 and 1.0")
        return True


class CrisisDetectionSystem:
    """Specialized system for detecting and responding to crisis situations."""

    def __init__(self):
        """Initialize the crisis detection system."""
        self.crisis_patterns = self._initialize_crisis_patterns()
        self.safety_resources = self._initialize_safety_resources()
        self.intervention_protocols = self._initialize_intervention_protocols()
        logger.info("CrisisDetectionSystem initialized")

    def _initialize_crisis_patterns(self) -> dict[CrisisLevel, dict[str, list[str]]]:
        """Initialize patterns for detecting different crisis levels."""
        return {
            CrisisLevel.MODERATE: {
                "keywords": [
                    "hopeless", "worthless", "pointless", "give up", "can't go on",
                    "no way out", "trapped", "desperate", "overwhelmed completely"
                ],
                "patterns": [
                    r"feel.*hopeless", r"completely.*worthless", r"no.*point.*living",
                    r"give.*up.*everything", r"can't.*go.*on", r"no.*way.*out",
                    r"trapped.*situation", r"desperate.*help"
                ]
            },

            CrisisLevel.HIGH: {
                "keywords": [
                    "hurt myself", "self-harm", "cut myself", "end the pain",
                    "better off dead", "disappear forever", "stop existing"
                ],
                "patterns": [
                    r"hurt.*myself", r"self.*harm", r"cut.*myself", r"end.*the.*pain",
                    r"better.*off.*dead", r"disappear.*forever", r"stop.*existing",
                    r"harm.*myself", r"injure.*myself"
                ]
            },

            CrisisLevel.SEVERE: {
                "keywords": [
                    "kill myself", "commit suicide", "end it all", "take my life",
                    "suicide plan", "want to die", "end my life"
                ],
                "patterns": [
                    r"kill.*myself", r"commit.*suicide", r"end.*it.*all",
                    r"take.*my.*life", r"suicide.*plan", r"want.*to.*die",
                    r"end.*my.*life", r"planning.*suicide"
                ]
            },

            CrisisLevel.EMERGENCY: {
                "keywords": [
                    "going to kill myself", "suicide tonight", "pills ready",
                    "rope ready", "gun ready", "goodbye forever", "final message"
                ],
                "patterns": [
                    r"going.*to.*kill.*myself", r"suicide.*tonight", r"pills.*ready",
                    r"rope.*ready", r"gun.*ready", r"goodbye.*forever",
                    r"final.*message", r"tonight.*is.*the.*night"
                ]
            }
        }

    def _initialize_safety_resources(self) -> dict[str, list[str]]:
        """Initialize safety resources for different crisis levels."""
        return {
            "immediate_support": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Emergency Services: 911",
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
            ],
            "professional_help": [
                "Contact your therapist or counselor immediately",
                "Visit your nearest emergency room",
                "Call your doctor or mental health provider",
                "Reach out to a trusted friend or family member"
            ],
            "coping_resources": [
                "Remove any means of self-harm from your immediate environment",
                "Stay with someone you trust",
                "Use grounding techniques: 5-4-3-2-1 method",
                "Practice deep breathing exercises",
                "Engage in physical activity or movement"
            ],
            "online_support": [
                "Crisis Chat: https://suicidepreventionlifeline.org/chat/",
                "7 Cups: https://www.7cups.com/",
                "BetterHelp Crisis Support: https://www.betterhelp.com/",
                "SAMHSA National Helpline: 1-800-662-4357"
            ]
        }

    def _initialize_intervention_protocols(self) -> dict[CrisisLevel, dict[str, Any]]:
        """Initialize intervention protocols for different crisis levels."""
        return {
            CrisisLevel.MODERATE: {
                "immediate_actions": [
                    "Acknowledge the person's pain and validate their feelings",
                    "Provide hope and remind them that feelings can change",
                    "Offer coping strategies and grounding techniques",
                    "Encourage professional support"
                ],
                "response_tone": ResponseTone.VALIDATING,
                "follow_up_required": True,
                "professional_referral": False
            },

            CrisisLevel.HIGH: {
                "immediate_actions": [
                    "Express concern and care for the person's safety",
                    "Ask directly about self-harm intentions",
                    "Provide immediate safety resources",
                    "Encourage removal of means of self-harm",
                    "Suggest staying with someone trusted"
                ],
                "response_tone": ResponseTone.CRISIS_FOCUSED,
                "follow_up_required": True,
                "professional_referral": True
            },

            CrisisLevel.SEVERE: {
                "immediate_actions": [
                    "Take immediate action to ensure safety",
                    "Provide crisis hotline numbers immediately",
                    "Encourage immediate professional help",
                    "Ask about suicide plan and means",
                    "Stay with the person if possible"
                ],
                "response_tone": ResponseTone.CRISIS_FOCUSED,
                "follow_up_required": True,
                "professional_referral": True
            },

            CrisisLevel.EMERGENCY: {
                "immediate_actions": [
                    "Call emergency services immediately",
                    "Do not leave the person alone",
                    "Remove any means of self-harm",
                    "Contact emergency contacts",
                    "Prepare for immediate professional intervention"
                ],
                "response_tone": ResponseTone.CRISIS_FOCUSED,
                "follow_up_required": True,
                "professional_referral": True
            }
        }

    def detect_crisis_level(self, user_input: str, emotional_state: EmotionalState,
                           context: NarrativeContext) -> tuple[CrisisLevel, list[CrisisIndicator]]:
        """Detect crisis level from user input and emotional state."""
        try:
            detected_indicators = []
            max_crisis_level = CrisisLevel.NONE

            input_lower = user_input.lower()

            # Check for crisis patterns
            for crisis_level, patterns in self.crisis_patterns.items():
                # Check keywords
                for keyword in patterns["keywords"]:
                    if keyword in input_lower:
                        indicator = CrisisIndicator(
                            indicator_type="keyword_match",
                            severity_level=crisis_level,
                            description=f"Crisis keyword detected: {keyword}",
                            detected_text=keyword,
                            confidence_score=0.8,
                            immediate_action_required=crisis_level.value in ["high", "severe", "emergency"]
                        )
                        detected_indicators.append(indicator)

                        if crisis_level.value > max_crisis_level.value:
                            max_crisis_level = crisis_level

                # Check regex patterns
                for pattern in patterns["patterns"]:
                    matches = re.findall(pattern, input_lower)
                    for match in matches:
                        indicator = CrisisIndicator(
                            indicator_type="pattern_match",
                            severity_level=crisis_level,
                            description=f"Crisis pattern detected: {pattern}",
                            detected_text=match,
                            confidence_score=0.9,
                            immediate_action_required=crisis_level.value in ["high", "severe", "emergency"]
                        )
                        detected_indicators.append(indicator)

                        if crisis_level.value > max_crisis_level.value:
                            max_crisis_level = crisis_level

            # Check emotional state for crisis indicators
            if emotional_state.intensity > 0.9:
                if emotional_state.primary_emotion in [EmotionalStateType.DEPRESSED, EmotionalStateType.HOPELESS]:
                    indicator = CrisisIndicator(
                        indicator_type="emotional_intensity",
                        severity_level=CrisisLevel.MODERATE,
                        description=f"Very high {emotional_state.primary_emotion} intensity",
                        confidence_score=emotional_state.confidence_level,
                        immediate_action_required=True
                    )
                    detected_indicators.append(indicator)

                    if CrisisLevel.MODERATE.value > max_crisis_level.value:
                        max_crisis_level = CrisisLevel.MODERATE

            # Add safety resources and interventions to indicators
            for indicator in detected_indicators:
                indicator.safety_resources = self.safety_resources["immediate_support"]

                if indicator.severity_level in self.intervention_protocols:
                    protocol = self.intervention_protocols[indicator.severity_level]
                    indicator.recommended_interventions = protocol["immediate_actions"]
                    indicator.professional_referral_needed = protocol["professional_referral"]

                indicator.validate()

            logger.info(f"Crisis detection completed: Level {max_crisis_level.value}, {len(detected_indicators)} indicators")
            return max_crisis_level, detected_indicators

        except Exception as e:
            logger.error(f"Error in crisis detection: {e}")
            return CrisisLevel.NONE, []

    def generate_crisis_response(self, crisis_level: CrisisLevel,
                               indicators: list[CrisisIndicator],
                               context: NarrativeContext) -> AdaptiveResponse:
        """Generate appropriate crisis response."""
        try:
            if crisis_level == CrisisLevel.NONE:
                return AdaptiveResponse(
                    adapted_content="I'm here to support you through this conversation.",
                    response_tone=ResponseTone.SUPPORTIVE
                )

            protocol = self.intervention_protocols.get(crisis_level, {})

            # Generate crisis-appropriate content
            if crisis_level == CrisisLevel.EMERGENCY:
                content = (
                    "I'm very concerned about your safety right now. Please reach out for immediate help:\n\n"
                    "🚨 Emergency: Call 911\n"
                    "📞 Crisis Hotline: 988 (Suicide & Crisis Lifeline)\n"
                    "💬 Crisis Text: Text HOME to 741741\n\n"
                    "You don't have to go through this alone. Help is available right now."
                )
            elif crisis_level == CrisisLevel.SEVERE:
                content = (
                    "I hear that you're in tremendous pain right now, and I'm deeply concerned about you. "
                    "Your life has value, and there are people who want to help:\n\n"
                    "📞 National Suicide Prevention Lifeline: 988\n"
                    "💬 Crisis Text Line: Text HOME to 741741\n\n"
                    "Please reach out to someone you trust or a mental health professional. "
                    "These feelings can change with proper support."
                )
            elif crisis_level == CrisisLevel.HIGH:
                content = (
                    "I can hear how much pain you're experiencing, and I want you to know that you're not alone. "
                    "It's important that we make sure you're safe right now.\n\n"
                    "If you're thinking about hurting yourself, please:\n"
                    "• Remove any means of self-harm from your area\n"
                    "• Stay with someone you trust\n"
                    "• Call 988 for immediate support\n\n"
                    "Your feelings are valid, and with help, they can improve."
                )
            else:  # MODERATE
                content = (
                    "I can sense that you're going through a really difficult time right now. "
                    "These feelings of hopelessness are painful, but they don't have to be permanent.\n\n"
                    "Some things that might help:\n"
                    "• Reach out to a trusted friend, family member, or counselor\n"
                    "• Try grounding techniques like deep breathing\n"
                    "• Remember that feelings change, even when they feel overwhelming\n\n"
                    "Would you like to talk about what's making you feel this way?"
                )

            # Collect safety resources
            safety_resources = []
            for indicator in indicators:
                safety_resources.extend(indicator.safety_resources)

            response = AdaptiveResponse(
                adapted_content=content,
                response_tone=protocol.get("response_tone", ResponseTone.CRISIS_FOCUSED),
                adaptation_strategies=[AdaptationStrategy.CRISIS_INTERVENTION],
                crisis_level=crisis_level,
                support_elements=protocol.get("immediate_actions", []),
                therapeutic_value=0.9,  # High therapeutic value for crisis intervention
                safety_considerations=list(set(safety_resources)),  # Remove duplicates
                follow_up_needed=protocol.get("follow_up_required", True)
            )

            response.validate()
            return response

        except Exception as e:
            logger.error(f"Error generating crisis response: {e}")
            # Return safe fallback response
            return AdaptiveResponse(
                adapted_content="I'm concerned about you. Please consider reaching out to a mental health professional or crisis hotline for support.",
                response_tone=ResponseTone.SUPPORTIVE,
                crisis_level=crisis_level,
                safety_considerations=self.safety_resources["immediate_support"]
            )


class EmotionalGrowthTracker:
    """Tracks and reinforces emotional progress and growth."""

    def __init__(self):
        """Initialize the emotional growth tracker."""
        self.growth_patterns = self._initialize_growth_patterns()
        self.reinforcement_messages = self._initialize_reinforcement_messages()
        self.growth_history = defaultdict(deque)
        logger.info("EmotionalGrowthTracker initialized")

    def _initialize_growth_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize patterns for detecting emotional growth."""
        return {
            "intensity_improvement": {
                "description": "Emotional intensity has decreased",
                "detection_threshold": 0.2,  # Minimum improvement to detect
                "significance_multiplier": 1.0
            },
            "coping_strategy_use": {
                "description": "User is applying coping strategies",
                "keywords": [
                    "breathing", "grounding", "mindfulness", "taking a break",
                    "talking to someone", "using techniques", "practicing"
                ],
                "significance_multiplier": 1.2
            },
            "emotional_awareness": {
                "description": "Increased emotional self-awareness",
                "keywords": [
                    "I notice", "I realize", "I'm aware", "I understand",
                    "I recognize", "I see that", "I'm learning"
                ],
                "significance_multiplier": 1.1
            },
            "positive_reframing": {
                "description": "Positive cognitive reframing",
                "keywords": [
                    "on the other hand", "but also", "I could try", "maybe",
                    "perhaps", "another way", "different perspective"
                ],
                "significance_multiplier": 1.3
            },
            "help_seeking": {
                "description": "Seeking help and support",
                "keywords": [
                    "asking for help", "talking to", "reaching out",
                    "getting support", "seeking advice", "consulting"
                ],
                "significance_multiplier": 1.4
            },
            "emotional_regulation": {
                "description": "Improved emotional regulation",
                "keywords": [
                    "calming down", "managing", "controlling", "regulating",
                    "staying calm", "keeping perspective", "balanced"
                ],
                "significance_multiplier": 1.2
            }
        }

    def _initialize_reinforcement_messages(self) -> dict[str, dict[str, list[str]]]:
        """Initialize reinforcement messages for different types of growth."""
        return {
            "intensity_improvement": {
                "subtle": [
                    "I notice you seem a bit more settled now.",
                    "There's a sense of calm in your words.",
                    "You sound more centered than before."
                ],
                "moderate": [
                    "I can really hear the positive shift in how you're feeling.",
                    "It's wonderful to see you finding some peace in this moment.",
                    "You've made some real progress in managing these difficult feelings."
                ],
                "enthusiastic": [
                    "What an incredible transformation! You've really worked through those intense emotions.",
                    "I'm so proud of how you've navigated through that difficult emotional space.",
                    "This is exactly the kind of emotional growth that leads to lasting change!"
                ]
            },

            "coping_strategy_use": {
                "subtle": [
                    "I see you're putting some helpful strategies into practice.",
                    "It's good that you're using tools to help yourself.",
                    "You're taking positive steps to manage this situation."
                ],
                "moderate": [
                    "I'm really impressed by how you're applying coping strategies!",
                    "You're showing great self-care by using these techniques.",
                    "This is exactly what healthy coping looks like."
                ],
                "enthusiastic": [
                    "Fantastic! You're becoming your own best advocate by using these strategies!",
                    "This is incredible growth - you're actively taking charge of your emotional well-being!",
                    "You're developing real mastery over these coping techniques!"
                ]
            },

            "emotional_awareness": {
                "subtle": [
                    "Your self-awareness is really developing.",
                    "I appreciate how thoughtful you're being about your emotions.",
                    "You're showing good insight into your feelings."
                ],
                "moderate": [
                    "Your emotional intelligence is really shining through here.",
                    "This level of self-awareness is a real strength.",
                    "You're developing a much deeper understanding of yourself."
                ],
                "enthusiastic": [
                    "Your emotional awareness has grown tremendously!",
                    "This kind of deep self-understanding is transformative!",
                    "You're becoming an expert on your own emotional landscape!"
                ]
            },

            "positive_reframing": {
                "subtle": [
                    "I like how you're considering different angles.",
                    "You're showing flexibility in your thinking.",
                    "That's a more balanced way to look at it."
                ],
                "moderate": [
                    "What a great example of positive reframing!",
                    "You're really challenging those negative thought patterns.",
                    "This shift in perspective is so healthy and productive."
                ],
                "enthusiastic": [
                    "Brilliant reframing! You're becoming a master at shifting perspectives!",
                    "This is cognitive flexibility at its finest!",
                    "You're completely transforming how you approach challenges!"
                ]
            },

            "help_seeking": {
                "subtle": [
                    "It's good that you're reaching out for support.",
                    "Asking for help shows real wisdom.",
                    "You're building a strong support network."
                ],
                "moderate": [
                    "I'm so glad you're prioritizing getting the support you need.",
                    "Reaching out for help is a sign of strength, not weakness.",
                    "You're showing real courage by asking for support."
                ],
                "enthusiastic": [
                    "What courage it takes to reach out! You're showing incredible strength!",
                    "This is exactly what resilient people do - they build strong support systems!",
                    "You're becoming a champion at advocating for your own needs!"
                ]
            }
        }

    def detect_emotional_growth(self, current_state: EmotionalState,
                              previous_states: list[EmotionalState],
                              user_input: str,
                              context: NarrativeContext) -> list[EmotionalGrowthMoment]:
        """Detect moments of emotional growth."""
        try:
            growth_moments = []

            if not previous_states:
                return growth_moments

            # Compare with most recent previous state
            previous_state = previous_states[-1]

            # Check for intensity improvement
            if (previous_state.intensity - current_state.intensity >=
                self.growth_patterns["intensity_improvement"]["detection_threshold"]):

                growth_moment = EmotionalGrowthMoment(
                    growth_type="intensity_improvement",
                    description="Emotional intensity has decreased significantly",
                    previous_state=previous_state,
                    current_state=current_state,
                    improvement_indicators=[
                        f"Intensity decreased from {previous_state.intensity:.2f} to {current_state.intensity:.2f}"
                    ],
                    therapeutic_significance=min(1.0, (previous_state.intensity - current_state.intensity) * 2)
                )
                growth_moments.append(growth_moment)

            # Check user input for growth indicators
            input_lower = user_input.lower()

            for growth_type, pattern_info in self.growth_patterns.items():
                if growth_type == "intensity_improvement":
                    continue  # Already handled above

                keywords = pattern_info.get("keywords", [])
                for keyword in keywords:
                    if keyword in input_lower:
                        growth_moment = EmotionalGrowthMoment(
                            growth_type=growth_type,
                            description=pattern_info["description"],
                            current_state=current_state,
                            improvement_indicators=[f"Used language indicating: {keyword}"],
                            coping_strategies_used=[keyword] if "coping" in growth_type else [],
                            therapeutic_significance=min(1.0, 0.5 * pattern_info["significance_multiplier"])
                        )
                        growth_moments.append(growth_moment)
                        break  # Only add one moment per growth type

            # Generate reinforcement messages
            for moment in growth_moments:
                moment.reinforcement_message = self._generate_reinforcement_message(moment)
                moment.validate()

            logger.info(f"Detected {len(growth_moments)} emotional growth moments")
            return growth_moments

        except Exception as e:
            logger.error(f"Error detecting emotional growth: {e}")
            return []

    def _generate_reinforcement_message(self, growth_moment: EmotionalGrowthMoment) -> str:
        """Generate appropriate reinforcement message for growth moment."""
        try:
            growth_type = growth_moment.growth_type
            significance = growth_moment.therapeutic_significance

            # Determine celebration level based on significance
            if significance >= 0.8:
                celebration_level = "enthusiastic"
            elif significance >= 0.5:
                celebration_level = "moderate"
            else:
                celebration_level = "subtle"

            growth_moment.celebration_level = celebration_level

            # Get appropriate messages
            if growth_type in self.reinforcement_messages:
                messages = self.reinforcement_messages[growth_type].get(celebration_level, [])
                if messages:
                    return messages[0]  # Return first message for now

            # Fallback generic messages
            fallback_messages = {
                "subtle": "I notice the positive changes you're making.",
                "moderate": "You're showing real growth and progress here.",
                "enthusiastic": "This is fantastic progress! You should be proud of yourself!"
            }

            return fallback_messages.get(celebration_level, "You're making positive progress.")

        except Exception as e:
            logger.error(f"Error generating reinforcement message: {e}")
            return "You're making positive progress."


class NarrativeToneAdapter:
    """Adapts narrative tone based on emotional state."""

    def __init__(self):
        """Initialize the narrative tone adapter."""
        self.tone_mappings = self._initialize_tone_mappings()
        self.adaptation_strategies = self._initialize_adaptation_strategies()
        logger.info("NarrativeToneAdapter initialized")

    def _initialize_tone_mappings(self) -> dict[EmotionalStateType, dict[str, Any]]:
        """Initialize tone mappings for different emotional states."""
        return {
            EmotionalStateType.ANXIOUS: {
                "primary_tone": ResponseTone.CALMING,
                "secondary_tones": [ResponseTone.GROUNDING, ResponseTone.SUPPORTIVE],
                "pacing": "slower",
                "language_style": "gentle_reassuring",
                "avoid_elements": ["time_pressure", "uncertainty", "complex_choices"]
            },

            EmotionalStateType.DEPRESSED: {
                "primary_tone": ResponseTone.VALIDATING,
                "secondary_tones": [ResponseTone.ENCOURAGING, ResponseTone.SUPPORTIVE],
                "pacing": "patient",
                "language_style": "warm_accepting",
                "avoid_elements": ["overwhelming_positivity", "minimizing_feelings", "pressure_to_change"]
            },

            EmotionalStateType.ANGRY: {
                "primary_tone": ResponseTone.VALIDATING,
                "secondary_tones": [ResponseTone.GROUNDING, ResponseTone.CALMING],
                "pacing": "steady",
                "language_style": "respectful_acknowledging",
                "avoid_elements": ["dismissive_language", "confrontation", "blame"]
            },

            EmotionalStateType.OVERWHELMED: {
                "primary_tone": ResponseTone.GROUNDING,
                "secondary_tones": [ResponseTone.SUPPORTIVE, ResponseTone.CALMING],
                "pacing": "simplified",
                "language_style": "clear_structured",
                "avoid_elements": ["information_overload", "multiple_options", "complexity"]
            },

            EmotionalStateType.CONFUSED: {
                "primary_tone": ResponseTone.SUPPORTIVE,
                "secondary_tones": [ResponseTone.GROUNDING, ResponseTone.ENCOURAGING],
                "pacing": "clarifying",
                "language_style": "clear_patient",
                "avoid_elements": ["ambiguity", "rushed_explanations", "assumptions"]
            },

            EmotionalStateType.EXCITED: {
                "primary_tone": ResponseTone.ENERGIZING,
                "secondary_tones": [ResponseTone.ENCOURAGING, ResponseTone.SUPPORTIVE],
                "pacing": "matching_energy",
                "language_style": "enthusiastic_positive",
                "avoid_elements": ["dampening_energy", "over_caution", "negativity"]
            },

            EmotionalStateType.HOPEFUL: {
                "primary_tone": ResponseTone.ENCOURAGING,
                "secondary_tones": [ResponseTone.EMPOWERING, ResponseTone.SUPPORTIVE],
                "pacing": "forward_moving",
                "language_style": "optimistic_realistic",
                "avoid_elements": ["pessimism", "doubt", "discouragement"]
            },

            EmotionalStateType.CALM: {
                "primary_tone": ResponseTone.SUPPORTIVE,
                "secondary_tones": [ResponseTone.ENCOURAGING, ResponseTone.EMPOWERING],
                "pacing": "natural",
                "language_style": "balanced_neutral",
                "avoid_elements": ["artificial_drama", "unnecessary_intensity"]
            }
        }

    def _initialize_adaptation_strategies(self) -> dict[ResponseTone, dict[str, Any]]:
        """Initialize adaptation strategies for different response tones."""
        return {
            ResponseTone.CALMING: {
                "language_adjustments": [
                    "Use slower, more deliberate pacing",
                    "Include grounding elements (sensory details)",
                    "Avoid time pressure or urgency",
                    "Use reassuring, stable language"
                ],
                "content_modifications": [
                    "Reduce complexity of choices",
                    "Include breathing or relaxation cues",
                    "Focus on present moment",
                    "Provide predictable structure"
                ]
            },

            ResponseTone.VALIDATING: {
                "language_adjustments": [
                    "Acknowledge feelings explicitly",
                    "Use 'I hear you' or 'That makes sense' phrases",
                    "Avoid minimizing language",
                    "Reflect emotions back"
                ],
                "content_modifications": [
                    "Include emotional validation",
                    "Normalize the experience",
                    "Show understanding of difficulty",
                    "Avoid rushing to solutions"
                ]
            },

            ResponseTone.GROUNDING: {
                "language_adjustments": [
                    "Use concrete, specific language",
                    "Include sensory details",
                    "Focus on immediate environment",
                    "Use present-tense descriptions"
                ],
                "content_modifications": [
                    "Include grounding exercises",
                    "Focus on physical sensations",
                    "Describe immediate surroundings",
                    "Provide anchoring elements"
                ]
            },

            ResponseTone.ENCOURAGING: {
                "language_adjustments": [
                    "Use positive, forward-looking language",
                    "Include strength-based observations",
                    "Highlight progress and capabilities",
                    "Use hopeful, optimistic tone"
                ],
                "content_modifications": [
                    "Emphasize user strengths",
                    "Highlight past successes",
                    "Focus on possibilities",
                    "Include motivational elements"
                ]
            },

            ResponseTone.EMPOWERING: {
                "language_adjustments": [
                    "Use action-oriented language",
                    "Emphasize user agency and choice",
                    "Include capability-building language",
                    "Focus on user strengths"
                ],
                "content_modifications": [
                    "Provide meaningful choices",
                    "Highlight user control",
                    "Include skill-building opportunities",
                    "Focus on self-efficacy"
                ]
            }
        }

    def adapt_narrative_tone(self, content: str, emotional_state: EmotionalState,
                           context: NarrativeContext) -> AdaptiveResponse:
        """Adapt narrative tone based on emotional state."""
        try:
            # Get tone mapping for emotional state
            emotion_mapping = self.tone_mappings.get(
                emotional_state.primary_emotion,
                self.tone_mappings[EmotionalStateType.CALM]
            )

            primary_tone = emotion_mapping["primary_tone"]
            adaptation_strategy = self.adaptation_strategies.get(primary_tone, {})

            # Apply tone adaptations
            adapted_content = self._apply_tone_adaptations(
                content, primary_tone, adaptation_strategy, emotional_state
            )

            # Determine adaptation strategies used
            strategies_used = [AdaptationStrategy.TONE_ADJUSTMENT]

            if emotion_mapping["pacing"] != "natural":
                strategies_used.append(AdaptationStrategy.PACING_MODIFICATION)

            if emotional_state.intensity > 0.7:
                strategies_used.append(AdaptationStrategy.SUPPORT_ESCALATION)

            # Calculate therapeutic value
            therapeutic_value = min(1.0, 0.5 + (emotional_state.confidence_level * 0.3))

            response = AdaptiveResponse(
                original_content=content,
                adapted_content=adapted_content,
                response_tone=primary_tone,
                adaptation_strategies=strategies_used,
                emotional_context=emotional_state,
                therapeutic_value=therapeutic_value,
                support_elements=adaptation_strategy.get("content_modifications", [])
            )

            response.validate()
            return response

        except Exception as e:
            logger.error(f"Error adapting narrative tone: {e}")
            # Return original content as fallback
            return AdaptiveResponse(
                original_content=content,
                adapted_content=content,
                response_tone=ResponseTone.SUPPORTIVE,
                emotional_context=emotional_state
            )

    def _apply_tone_adaptations(self, content: str, tone: ResponseTone,
                              strategy: dict[str, Any], emotional_state: EmotionalState) -> str:
        """Apply specific tone adaptations to content."""
        try:
            adapted_content = content

            # Apply language adjustments based on tone
            if tone == ResponseTone.CALMING:
                adapted_content = self._apply_calming_adaptations(adapted_content)
            elif tone == ResponseTone.VALIDATING:
                adapted_content = self._apply_validating_adaptations(adapted_content, emotional_state)
            elif tone == ResponseTone.GROUNDING:
                adapted_content = self._apply_grounding_adaptations(adapted_content)
            elif tone == ResponseTone.ENCOURAGING:
                adapted_content = self._apply_encouraging_adaptations(adapted_content)
            elif tone == ResponseTone.EMPOWERING:
                adapted_content = self._apply_empowering_adaptations(adapted_content)

            return adapted_content

        except Exception as e:
            logger.error(f"Error applying tone adaptations: {e}")
            return content

    def _apply_calming_adaptations(self, content: str) -> str:
        """Apply calming tone adaptations."""
        # Add calming elements
        calming_phrases = [
            "Take a moment to breathe.",
            "There's no rush here.",
            "You're in a safe space.",
            "Let's take this one step at a time."
        ]

        # Add a calming phrase if content seems rushed or intense
        if any(word in content.lower() for word in ["quickly", "hurry", "urgent", "immediately"]):
            content = calming_phrases[0] + " " + content

        # Replace urgent language with calmer alternatives
        content = content.replace("quickly", "at your own pace")
        content = content.replace("hurry", "take your time")
        content = content.replace("urgent", "important")

        return content

    def _apply_validating_adaptations(self, content: str, emotional_state: EmotionalState) -> str:
        """Apply validating tone adaptations."""
        # Add validation based on emotional state
        validation_phrases = {
            EmotionalStateType.ANXIOUS: "I can understand why you'd feel anxious about this.",
            EmotionalStateType.DEPRESSED: "These feelings of sadness are completely understandable.",
            EmotionalStateType.ANGRY: "Your anger makes complete sense given the situation.",
            EmotionalStateType.OVERWHELMED: "It's natural to feel overwhelmed when facing so much.",
            EmotionalStateType.CONFUSED: "Confusion is a normal response to complex situations."
        }

        validation = validation_phrases.get(emotional_state.primary_emotion, "Your feelings are valid.")

        # Add validation at the beginning if not already present
        if not any(phrase in content.lower() for phrase in ["understand", "makes sense", "valid", "natural"]):
            content = validation + " " + content

        return content

    def _apply_grounding_adaptations(self, content: str) -> str:
        """Apply grounding tone adaptations."""
        # Add grounding elements
        grounding_elements = [
            "Notice the ground beneath your feet.",
            "Feel the air around you.",
            "Take note of what you can see and hear right now.",
            "Focus on your breathing for a moment."
        ]

        # Add grounding if content lacks concrete details
        if len(content.split()) > 20 and not any(sense in content.lower() for sense in ["see", "hear", "feel", "touch", "smell"]):
            content = grounding_elements[0] + " " + content

        return content

    def _apply_encouraging_adaptations(self, content: str) -> str:
        """Apply encouraging tone adaptations."""
        # Add encouraging elements
        encouraging_phrases = [
            "You're doing great by working through this.",
            "You have the strength to handle this.",
            "This is a positive step forward.",
            "You're showing real courage here."
        ]

        # Add encouragement if content seems neutral or negative
        if not any(word in content.lower() for word in ["great", "good", "positive", "strength", "capable"]):
            content = encouraging_phrases[0] + " " + content

        return content

    def _apply_empowering_adaptations(self, content: str) -> str:
        """Apply empowering tone adaptations."""
        # Add empowering language
        empowering_phrases = [
            "You have the power to choose how to respond.",
            "This is your decision to make.",
            "You're in control of your next steps.",
            "You have everything you need within you."
        ]

        # Add empowerment if content lacks agency language
        if not any(word in content.lower() for word in ["choose", "decide", "control", "power", "your"]):
            content = empowering_phrases[0] + " " + content

        return content


class AdaptiveResponseSystem:
    """Main class for adaptive narrative responses based on emotional state."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the adaptive response system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.crisis_detector = CrisisDetectionSystem()
        self.growth_tracker = EmotionalGrowthTracker()
        self.tone_adapter = NarrativeToneAdapter()

        # Response history for learning and adaptation
        self.response_history = defaultdict(deque)

        logger.info("AdaptiveResponseSystem initialized")

    def generate_adaptive_response(self, original_content: str,
                                 emotional_analysis: EmotionalAnalysisResult,
                                 context: NarrativeContext,
                                 session_state: SessionState) -> AdaptiveResponse:
        """Generate adaptive response based on emotional state and context."""
        try:
            emotional_state = emotional_analysis.detected_emotion

            # Check for crisis first
            crisis_level, crisis_indicators = self.crisis_detector.detect_crisis_level(
                original_content, emotional_state, context
            )

            # If crisis detected, prioritize crisis response
            if crisis_level != CrisisLevel.NONE:
                return self.crisis_detector.generate_crisis_response(
                    crisis_level, crisis_indicators, context
                )

            # Check for emotional growth
            previous_states = self._get_emotional_history(session_state)
            growth_moments = self.growth_tracker.detect_emotional_growth(
                emotional_state, previous_states, original_content, context
            )

            # Adapt narrative tone
            tone_adapted_response = self.tone_adapter.adapt_narrative_tone(
                original_content, emotional_state, context
            )

            # Enhance response with growth acknowledgment if present
            if growth_moments:
                tone_adapted_response = self._enhance_with_growth_acknowledgment(
                    tone_adapted_response, growth_moments
                )

            # Add therapeutic recommendations if appropriate
            if emotional_analysis.therapeutic_recommendations:
                tone_adapted_response = self._integrate_therapeutic_recommendations(
                    tone_adapted_response, emotional_analysis.therapeutic_recommendations
                )

            # Store response in history for learning
            self._store_response_history(session_state.user_id, tone_adapted_response)

            logger.info(f"Generated adaptive response with tone: {tone_adapted_response.response_tone.value}")
            return tone_adapted_response

        except Exception as e:
            logger.error(f"Error generating adaptive response: {e}")
            # Return safe fallback response
            return AdaptiveResponse(
                original_content=original_content,
                adapted_content=original_content,
                response_tone=ResponseTone.SUPPORTIVE,
                emotional_context=emotional_analysis.detected_emotion
            )

    def _get_emotional_history(self, session_state: SessionState) -> list[EmotionalState]:
        """Get emotional history from session state."""
        history = []

        # Add current emotional state if available
        if session_state.emotional_state:
            history.append(session_state.emotional_state)

        # In a real implementation, this would fetch from database
        # For now, return the current state as history
        return history

    def _enhance_with_growth_acknowledgment(self, response: AdaptiveResponse,
                                          growth_moments: list[EmotionalGrowthMoment]) -> AdaptiveResponse:
        """Enhance response with emotional growth acknowledgment."""
        try:
            if not growth_moments:
                return response

            # Select the most significant growth moment
            most_significant = max(growth_moments, key=lambda m: m.therapeutic_significance)

            # Add growth acknowledgment to the response
            growth_acknowledgment = most_significant.reinforcement_message

            # Integrate growth acknowledgment naturally
            if response.adapted_content:
                response.adapted_content = f"{growth_acknowledgment}\n\n{response.adapted_content}"
            else:
                response.adapted_content = growth_acknowledgment

            # Update response properties
            response.adaptation_strategies.append(AdaptationStrategy.GROWTH_REINFORCEMENT)
            response.therapeutic_value = min(1.0, response.therapeutic_value + 0.2)
            response.support_elements.append(f"Growth acknowledgment: {most_significant.growth_type}")

            return response

        except Exception as e:
            logger.error(f"Error enhancing response with growth acknowledgment: {e}")
            return response

    def _integrate_therapeutic_recommendations(self, response: AdaptiveResponse,
                                            recommendations: list[str]) -> AdaptiveResponse:
        """Integrate therapeutic recommendations into response."""
        try:
            if not recommendations or len(recommendations) == 0:
                return response

            # Select most relevant recommendation (first one for now)
            primary_recommendation = recommendations[0]

            # Integrate recommendation naturally based on response tone
            if response.response_tone == ResponseTone.CRISIS_FOCUSED:
                # Don't add recommendations to crisis responses
                return response
            elif response.response_tone in [ResponseTone.SUPPORTIVE, ResponseTone.ENCOURAGING]:
                # Add as gentle suggestion
                suggestion = f"\n\nYou might find it helpful to {primary_recommendation.lower()}."
                response.adapted_content += suggestion
            elif response.response_tone == ResponseTone.EMPOWERING:
                # Frame as empowering choice
                suggestion = f"\n\nOne option you have is to {primary_recommendation.lower()}."
                response.adapted_content += suggestion

            # Update response properties
            response.therapeutic_value = min(1.0, response.therapeutic_value + 0.1)
            response.support_elements.extend(recommendations[:3])  # Add up to 3 recommendations

            return response

        except Exception as e:
            logger.error(f"Error integrating therapeutic recommendations: {e}")
            return response

    def _store_response_history(self, user_id: str, response: AdaptiveResponse) -> None:
        """Store response in history for learning and adaptation."""
        try:
            # Keep last 50 responses per user
            if len(self.response_history[user_id]) >= 50:
                self.response_history[user_id].popleft()

            self.response_history[user_id].append({
                "response_id": response.response_id,
                "tone": response.response_tone.value,
                "strategies": [s.value for s in response.adaptation_strategies],
                "therapeutic_value": response.therapeutic_value,
                "timestamp": response.created_at
            })

        except Exception as e:
            logger.error(f"Error storing response history: {e}")

    def get_response_effectiveness_metrics(self, user_id: str) -> dict[str, Any]:
        """Get metrics on response effectiveness for a user."""
        try:
            history = self.response_history.get(user_id, [])

            if not history:
                return {"total_responses": 0}

            # Calculate metrics
            total_responses = len(history)
            avg_therapeutic_value = sum(r["therapeutic_value"] for r in history) / total_responses

            # Count tone usage
            tone_counts = defaultdict(int)
            for response in history:
                tone_counts[response["tone"]] += 1

            # Count strategy usage
            strategy_counts = defaultdict(int)
            for response in history:
                for strategy in response["strategies"]:
                    strategy_counts[strategy] += 1

            return {
                "total_responses": total_responses,
                "average_therapeutic_value": avg_therapeutic_value,
                "tone_distribution": dict(tone_counts),
                "strategy_usage": dict(strategy_counts),
                "recent_responses": list(history)[-10:]  # Last 10 responses
            }

        except Exception as e:
            logger.error(f"Error calculating response effectiveness metrics: {e}")
            return {"error": str(e)}


# Utility functions for testing and validation
def test_adaptive_response_system():
    """Test the adaptive response system."""
    try:
        # Initialize system
        adaptive_system = AdaptiveResponseSystem()

        # Mock emotional analysis result
        from emotional_state_recognition import EmotionalAnalysisResult

        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.7,
                confidence_level=0.8
            ),
            therapeutic_recommendations=["Practice deep breathing exercises"]
        )

        # Mock context and session
        context = NarrativeContext(session_id="test")
        session = SessionState(session_id="test", user_id="test_user")

        # Test adaptive response
        original_content = "You face a challenging situation that requires immediate action."

        response = adaptive_system.generate_adaptive_response(
            original_content, emotional_analysis, context, session
        )

        print(f"Original: {original_content}")
        print(f"Adapted: {response.adapted_content}")
        print(f"Tone: {response.response_tone.value}")
        print(f"Strategies: {[s.value for s in response.adaptation_strategies]}")
        print(f"Therapeutic Value: {response.therapeutic_value:.2f}")

        logger.info("Adaptive response system test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Adaptive response system test failed: {e}")
        return False


if __name__ == "__main__":
    # Run test
    test_adaptive_response_system()
