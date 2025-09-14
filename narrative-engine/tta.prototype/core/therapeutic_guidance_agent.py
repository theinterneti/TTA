"""
Therapeutic Guidance Agent for TTA Prototype

This module implements the Therapeutic Guidance Agent that provides evidence-based
therapeutic interventions, seamlessly embeds therapeutic content in narrative contexts,
and includes crisis detection and appropriate response mechanisms.

Classes:
    TherapeuticGuidanceAgent: Main agent for therapeutic guidance and intervention delivery
    ContentDeliverySystem: System for seamless therapeutic content embedding
    CrisisDetectionSystem: System for detecting and responding to mental health crises
    EvidenceBasedInterventions: Repository of evidence-based therapeutic interventions
"""

import json
import logging

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
        CharacterState,
        DialogueContext,
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
    from .therapeutic_content_integration import (
        DetectedOpportunity,
        OpportunityType,
        TherapeuticOpportunityContext,
    )
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            CharacterState,
            DialogueContext,
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticOpportunity,
            TherapeuticProgress,
            ValidationError,
        )
        from therapeutic_content_integration import (
            DetectedOpportunity,
            OpportunityType,
            TherapeuticOpportunityContext,
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

        class MockTherapeuticLLMClient:
            def generate_therapeutic_dialogue(self, context, character_name="Therapist", validate_content=True):
                return MockTherapeuticResponse()
            def generate_therapeutic_intervention(self, context, intervention_type):
                return MockTherapeuticResponse()

        class MockTherapeuticResponse:
            def __init__(self):
                self.content = "I'm here to support you through this."
                self.content_type = "dialogue"
                self.safety_level = "safe"
                self.therapeutic_value = 0.8
                self.confidence = 0.9
                self.metadata = {}
                self.warnings = []
                self.recommendations = []

        class MockTherapeuticContext:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class MockTherapeuticContentType:
            DIALOGUE = "dialogue"
            INTERVENTION = "intervention"
            CRISIS_SUPPORT = "crisis_support"

        class MockSafetyLevel:
            SAFE = "safe"
            CAUTION = "caution"
            UNSAFE = "unsafe"
            CRISIS = "crisis"

        # Set the mock classes
        TherapeuticLLMClient = MockTherapeuticLLMClient
        TherapeuticResponse = MockTherapeuticResponse
        TherapeuticContext = MockTherapeuticContext
        TherapeuticContentType = MockTherapeuticContentType
        SafetyLevel = MockSafetyLevel

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Levels of crisis severity."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    IMMINENT = "imminent"


class InterventionDeliveryMode(Enum):
    """Modes for delivering therapeutic interventions."""
    DIRECT = "direct"  # Direct therapeutic dialogue
    NARRATIVE_EMBEDDED = "narrative_embedded"  # Embedded in story
    CHARACTER_GUIDED = "character_guided"  # Through character interactions
    EXPERIENTIAL = "experiential"  # Through story experiences
    REFLECTIVE = "reflective"  # Through reflection prompts


@dataclass
class CrisisIndicators:
    """Indicators of potential mental health crisis."""
    crisis_level: CrisisLevel = CrisisLevel.NONE
    risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)
    immediate_concerns: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    professional_referral_needed: bool = False
    emergency_contact_needed: bool = False
    confidence_score: float = 0.5  # 0.0 to 1.0
    assessment_timestamp: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate crisis indicators."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        return True


@dataclass
class TherapeuticDeliveryContext:
    """Context for therapeutic content delivery."""
    session_state: SessionState
    narrative_context: NarrativeContext
    character_context: CharacterState | None = None
    delivery_mode: InterventionDeliveryMode = InterventionDeliveryMode.NARRATIVE_EMBEDDED
    target_audience: str = "general"
    cultural_considerations: list[str] = field(default_factory=list)
    accessibility_needs: list[str] = field(default_factory=list)
    user_preferences: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate delivery context."""
        if not self.session_state:
            raise ValidationError("Session state is required")
        if not self.narrative_context:
            raise ValidationError("Narrative context is required")
        return True


@dataclass
class DeliveredIntervention:
    """Record of a delivered therapeutic intervention."""
    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intervention_type: InterventionType = InterventionType.COPING_SKILLS
    delivery_mode: InterventionDeliveryMode = InterventionDeliveryMode.NARRATIVE_EMBEDDED
    content: str = ""
    character_name: str | None = None
    narrative_integration: str = ""
    therapeutic_rationale: str = ""
    expected_outcomes: list[str] = field(default_factory=list)
    safety_level: str = "safe"
    delivery_timestamp: datetime = field(default_factory=datetime.now)
    user_response_expected: bool = True
    follow_up_needed: bool = False
    effectiveness_metrics: dict[str, float] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate delivered intervention."""
        if not self.content.strip():
            raise ValidationError("Intervention content cannot be empty")
        return True


class CrisisDetectionSystem:
    """System for detecting and responding to mental health crises."""

    def __init__(self):
        """Initialize the crisis detection system."""
        self.crisis_keywords = self._initialize_crisis_keywords()
        self.risk_assessment_factors = self._initialize_risk_factors()
        self.protective_factors = self._initialize_protective_factors()
        self.crisis_response_protocols = self._initialize_crisis_protocols()
        logger.info("CrisisDetectionSystem initialized")

    def _initialize_crisis_keywords(self) -> dict[CrisisLevel, list[str]]:
        """Initialize crisis detection keywords by severity level."""
        return {
            CrisisLevel.LOW: [
                "feeling down", "sad", "hopeless sometimes", "struggling",
                "difficult time", "hard to cope", "overwhelmed"
            ],
            CrisisLevel.MODERATE: [
                "very depressed", "can't handle this", "want to give up",
                "no point", "worthless", "burden", "tired of living"
            ],
            CrisisLevel.HIGH: [
                "want to die", "suicide", "kill myself", "end it all",
                "hurt myself", "self-harm", "cut myself", "overdose"
            ],
            CrisisLevel.IMMINENT: [
                "going to kill myself", "have a plan", "tonight", "right now",
                "pills ready", "rope", "gun", "bridge", "goodbye"
            ]
        }

    def _initialize_risk_factors(self) -> list[str]:
        """Initialize risk factors for crisis assessment."""
        return [
            "previous suicide attempts",
            "family history of suicide",
            "mental health diagnosis",
            "substance abuse",
            "recent loss or trauma",
            "social isolation",
            "financial problems",
            "relationship breakdown",
            "chronic illness",
            "access to means",
            "impulsivity",
            "hopelessness",
            "recent discharge from hospital",
            "anniversary of loss"
        ]

    def _initialize_protective_factors(self) -> list[str]:
        """Initialize protective factors for crisis assessment."""
        return [
            "strong social support",
            "religious or spiritual beliefs",
            "sense of responsibility to family",
            "pregnancy",
            "young children at home",
            "positive therapeutic relationship",
            "effective coping skills",
            "problem-solving abilities",
            "future orientation",
            "cultural beliefs against suicide",
            "fear of death or dying",
            "moral objections",
            "pets or animals to care for",
            "treatment engagement"
        ]

    def _initialize_crisis_protocols(self) -> dict[CrisisLevel, dict[str, Any]]:
        """Initialize crisis response protocols."""
        return {
            CrisisLevel.LOW: {
                "immediate_actions": [
                    "Validate feelings and normalize experience",
                    "Explore coping strategies",
                    "Assess support system",
                    "Schedule follow-up"
                ],
                "referrals": ["Consider counseling services"],
                "safety_planning": False,
                "emergency_contact": False
            },
            CrisisLevel.MODERATE: {
                "immediate_actions": [
                    "Conduct thorough risk assessment",
                    "Develop safety plan",
                    "Identify support persons",
                    "Remove or limit access to means",
                    "Increase contact frequency"
                ],
                "referrals": ["Mental health professional", "Crisis counseling"],
                "safety_planning": True,
                "emergency_contact": False
            },
            CrisisLevel.HIGH: {
                "immediate_actions": [
                    "Immediate safety assessment",
                    "Do not leave person alone",
                    "Contact crisis hotline",
                    "Consider emergency services",
                    "Involve support system"
                ],
                "referrals": ["Emergency mental health services", "Crisis intervention team"],
                "safety_planning": True,
                "emergency_contact": True
            },
            CrisisLevel.IMMINENT: {
                "immediate_actions": [
                    "Call emergency services immediately",
                    "Stay with person until help arrives",
                    "Remove all means of self-harm",
                    "Contact emergency contacts",
                    "Document everything"
                ],
                "referrals": ["Emergency room", "Crisis intervention", "Psychiatric emergency services"],
                "safety_planning": True,
                "emergency_contact": True
            }
        }

    def assess_crisis_level(self, user_input: str, session_state: SessionState,
                          narrative_context: NarrativeContext) -> CrisisIndicators:
        """
        Assess the level of mental health crisis based on user input and context.

        Args:
            user_input: User's input text
            session_state: Current session state
            narrative_context: Current narrative context

        Returns:
            CrisisIndicators: Assessment of crisis level and indicators
        """
        try:
            user_input_lower = user_input.lower()

            # Initialize crisis indicators
            crisis_indicators = CrisisIndicators()

            # Check for crisis keywords
            detected_level = CrisisLevel.NONE
            detected_keywords = []

            for level, keywords in self.crisis_keywords.items():
                for keyword in keywords:
                    if keyword in user_input_lower:
                        detected_keywords.append(keyword)
                        if level.value > detected_level.value:
                            detected_level = level

            crisis_indicators.crisis_level = detected_level
            crisis_indicators.immediate_concerns = detected_keywords

            # Assess risk factors from session history
            risk_factors = self._assess_risk_factors(session_state, narrative_context)
            crisis_indicators.risk_factors = risk_factors

            # Assess protective factors
            protective_factors = self._assess_protective_factors(session_state, narrative_context)
            crisis_indicators.protective_factors = protective_factors

            # Calculate confidence score
            confidence = self._calculate_crisis_confidence(
                detected_keywords, risk_factors, protective_factors
            )
            crisis_indicators.confidence_score = confidence

            # Determine recommended actions
            protocol = self.crisis_response_protocols.get(detected_level, {})
            crisis_indicators.recommended_actions = protocol.get("immediate_actions", [])
            crisis_indicators.professional_referral_needed = len(protocol.get("referrals", [])) > 0
            crisis_indicators.emergency_contact_needed = protocol.get("emergency_contact", False)

            return crisis_indicators

        except Exception as e:
            logger.error(f"Error assessing crisis level: {e}")
            # Return safe default
            return CrisisIndicators(
                crisis_level=CrisisLevel.NONE,
                confidence_score=0.0,
                recommended_actions=["Manual assessment recommended due to error"]
            )

    def _assess_risk_factors(self, session_state: SessionState,
                           narrative_context: NarrativeContext) -> list[str]:
        """Assess risk factors from session context."""
        risk_factors = []

        # Check emotional state
        if session_state.emotional_state:
            if session_state.emotional_state.primary_emotion == EmotionalStateType.DEPRESSED:
                if session_state.emotional_state.intensity > 0.8:
                    risk_factors.append("severe depression")

            # Check for hopelessness indicators in emotional state
            if hasattr(session_state.emotional_state, 'secondary_emotions'):
                # Look for hopelessness-related emotions
                hopeless_emotions = ['depressed', 'overwhelmed']
                for emotion in session_state.emotional_state.secondary_emotions:
                    if hasattr(emotion, 'value') and emotion.value in hopeless_emotions:
                        risk_factors.append("hopelessness")
                        break

        # Check therapeutic progress for concerning patterns
        if session_state.therapeutic_progress:
            if session_state.therapeutic_progress.overall_progress_score < 20:
                risk_factors.append("poor treatment progress")

            # Check for concerning intervention history
            for intervention in session_state.therapeutic_progress.completed_interventions:
                if intervention.effectiveness_rating < 3.0:
                    risk_factors.append("ineffective previous interventions")
                    break

        # Check narrative context for concerning themes
        recent_events_text = " ".join(narrative_context.recent_events).lower()
        if "loss" in recent_events_text or "death" in recent_events_text:
            risk_factors.append("recent loss or trauma")

        if "alone" in recent_events_text or "isolated" in recent_events_text:
            risk_factors.append("social isolation")

        return list(set(risk_factors))  # Remove duplicates

    def _assess_protective_factors(self, session_state: SessionState,
                                 narrative_context: NarrativeContext) -> list[str]:
        """Assess protective factors from session context."""
        protective_factors = []

        # Check for positive relationships in character states
        if session_state.character_states:
            positive_relationships = 0
            for character_state in session_state.character_states.values():
                if any(score > 0.5 for score in character_state.relationship_scores.values()):
                    positive_relationships += 1

            if positive_relationships > 0:
                protective_factors.append("positive relationships")

        # Check therapeutic progress for positive indicators
        if session_state.therapeutic_progress:
            if session_state.therapeutic_progress.overall_progress_score > 50:
                protective_factors.append("positive treatment progress")

            if len(session_state.therapeutic_progress.coping_strategies_learned) > 2:
                protective_factors.append("effective coping skills")

        # Check narrative context for positive themes
        recent_events_text = " ".join(narrative_context.recent_events).lower()
        if "support" in recent_events_text or "help" in recent_events_text:
            protective_factors.append("seeking support")

        if "future" in recent_events_text or "plan" in recent_events_text:
            protective_factors.append("future orientation")

        return list(set(protective_factors))  # Remove duplicates

    def _calculate_crisis_confidence(self, keywords: list[str], risk_factors: list[str],
                                   protective_factors: list[str]) -> float:
        """Calculate confidence in crisis assessment."""
        confidence = 0.5  # Base confidence

        # Increase confidence based on explicit keywords
        confidence += min(0.3, len(keywords) * 0.1)

        # Adjust based on risk factors
        confidence += min(0.2, len(risk_factors) * 0.05)

        # Adjust based on protective factors (slightly reduce confidence if many protective factors)
        confidence -= min(0.1, len(protective_factors) * 0.02)

        return max(0.0, min(1.0, confidence))

    def generate_crisis_response(self, crisis_indicators: CrisisIndicators,
                               delivery_context: TherapeuticDeliveryContext) -> TherapeuticResponse:
        """
        Generate appropriate crisis response based on assessment.

        Args:
            crisis_indicators: Crisis assessment results
            delivery_context: Context for content delivery

        Returns:
            TherapeuticResponse: Crisis response content
        """
        try:
            crisis_level = crisis_indicators.crisis_level

            if crisis_level == CrisisLevel.NONE:
                return self._generate_supportive_response(delivery_context)

            # Get crisis protocol
            protocol = self.crisis_response_protocols.get(crisis_level, {})

            # Generate crisis-appropriate response
            if crisis_level in [CrisisLevel.HIGH, CrisisLevel.IMMINENT]:
                return self._generate_emergency_response(crisis_indicators, delivery_context, protocol)
            elif crisis_level == CrisisLevel.MODERATE:
                return self._generate_moderate_crisis_response(crisis_indicators, delivery_context, protocol)
            else:  # LOW
                return self._generate_low_crisis_response(crisis_indicators, delivery_context, protocol)

        except Exception as e:
            logger.error(f"Error generating crisis response: {e}")
            return self._generate_emergency_fallback_response()

    def _generate_emergency_response(self, crisis_indicators: CrisisIndicators,
                                   delivery_context: TherapeuticDeliveryContext,
                                   protocol: dict[str, Any]) -> TherapeuticResponse:
        """Generate emergency crisis response."""
        crisis_content = {
            "immediate_response": "I'm very concerned about your safety right now. Your life has value and there are people who want to help you.",
            "safety_message": "Please don't hurt yourself. There are people trained to help you through this crisis.",
            "immediate_resources": [
                "National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
                "Crisis Text Line: Text HOME to 741741",
                "Emergency Services: 911",
                "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
            ],
            "immediate_actions": protocol.get("immediate_actions", []),
            "safety_planning": "If you're in immediate danger, please call 911 or go to your nearest emergency room.",
            "narrative_adaptation": "The character expresses serious concern and immediately provides crisis resources while maintaining a supportive presence."
        }

        return TherapeuticResponse(
            content=json.dumps(crisis_content, indent=2),
            content_type=TherapeuticContentType.CRISIS_SUPPORT,
            safety_level=SafetyLevel.CRISIS,
            therapeutic_value=1.0,  # Maximum therapeutic value for crisis intervention
            confidence=crisis_indicators.confidence_score,
            metadata={
                "crisis_level": crisis_indicators.crisis_level.value,
                "emergency_response": True,
                "professional_referral_needed": True
            },
            warnings=["CRISIS DETECTED: Immediate professional intervention recommended"],
            recommendations=["Contact emergency services", "Do not leave person alone", "Follow crisis protocol"]
        )

    def _generate_moderate_crisis_response(self, crisis_indicators: CrisisIndicators,
                                         delivery_context: TherapeuticDeliveryContext,
                                         protocol: dict[str, Any]) -> TherapeuticResponse:
        """Generate moderate crisis response."""
        crisis_content = {
            "supportive_response": "I can hear that you're going through a really difficult time right now. I'm concerned about you and want to help.",
            "validation": "These feelings are overwhelming, but you don't have to face them alone.",
            "immediate_coping": [
                "Take slow, deep breaths",
                "Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear",
                "Reach out to someone you trust",
                "Consider calling a crisis helpline for additional support"
            ],
            "resources": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "SAMHSA National Helpline: 1-800-662-4357"
            ],
            "safety_planning": "Let's work together to create a plan to keep you safe.",
            "follow_up": "I want to check in with you regularly to make sure you're getting the support you need.",
            "narrative_integration": "The character shows deep concern and provides immediate support while helping create a safety plan."
        }

        return TherapeuticResponse(
            content=json.dumps(crisis_content, indent=2),
            content_type=TherapeuticContentType.CRISIS_SUPPORT,
            safety_level=SafetyLevel.CAUTION,
            therapeutic_value=0.9,
            confidence=crisis_indicators.confidence_score,
            metadata={
                "crisis_level": crisis_indicators.crisis_level.value,
                "safety_planning_needed": True,
                "professional_referral_recommended": True
            },
            warnings=["Moderate crisis detected: Enhanced support and monitoring needed"],
            recommendations=["Develop safety plan", "Increase contact frequency", "Consider professional referral"]
        )

    def _generate_low_crisis_response(self, crisis_indicators: CrisisIndicators,
                                    delivery_context: TherapeuticDeliveryContext,
                                    protocol: dict[str, Any]) -> TherapeuticResponse:
        """Generate low-level crisis response."""
        crisis_content = {
            "empathetic_response": "I can see that you're struggling right now, and I want you to know that what you're feeling is valid.",
            "normalization": "Many people go through difficult periods like this. You're not alone in feeling this way.",
            "coping_support": [
                "Focus on one day at a time, or even one hour at a time",
                "Reach out to friends, family, or support groups",
                "Engage in activities that usually bring you comfort",
                "Consider talking to a counselor or therapist"
            ],
            "hope_instillation": "These difficult feelings won't last forever. With support and time, things can get better.",
            "resources": [
                "National Suicide Prevention Lifeline: 988 (available 24/7)",
                "Crisis Text Line: Text HOME to 741741",
                "Local counseling services and support groups"
            ],
            "narrative_integration": "The character provides compassionate support and practical coping strategies while maintaining hope."
        }

        return TherapeuticResponse(
            content=json.dumps(crisis_content, indent=2),
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.CAUTION,
            therapeutic_value=0.8,
            confidence=crisis_indicators.confidence_score,
            metadata={
                "crisis_level": crisis_indicators.crisis_level.value,
                "supportive_intervention": True
            },
            recommendations=["Monitor for escalation", "Provide ongoing support", "Consider counseling referral"]
        )

    def _generate_supportive_response(self, delivery_context: TherapeuticDeliveryContext) -> TherapeuticResponse:
        """Generate general supportive response when no crisis is detected."""
        supportive_content = "I'm here to support you. How are you feeling right now, and what would be most helpful for you?"

        return TherapeuticResponse(
            content=supportive_content,
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.7,
            confidence=0.8,
            metadata={"supportive_response": True}
        )

    def _generate_emergency_fallback_response(self) -> TherapeuticResponse:
        """Generate emergency fallback response when other methods fail."""
        emergency_content = {
            "immediate_message": "I'm concerned about your safety. Please reach out for help immediately.",
            "crisis_resources": [
                "National Suicide Prevention Lifeline: 988",
                "Emergency Services: 911",
                "Crisis Text Line: Text HOME to 741741"
            ],
            "safety_message": "Your life has value. Please don't hurt yourself."
        }

        return TherapeuticResponse(
            content=json.dumps(emergency_content, indent=2),
            content_type=TherapeuticContentType.CRISIS_SUPPORT,
            safety_level=SafetyLevel.CRISIS,
            therapeutic_value=0.9,
            confidence=0.5,
            metadata={"emergency_fallback": True},
            warnings=["Emergency fallback response used"]
        )
class EvidenceBasedInterventions:
    """Repository of evidence-based therapeutic interventions."""

    def __init__(self):
        """Initialize evidence-based interventions repository."""
        self.interventions = self._initialize_interventions()
        self.intervention_templates = self._initialize_templates()
        logger.info("EvidenceBasedInterventions initialized")

    def _initialize_interventions(self) -> dict[InterventionType, dict[str, Any]]:
        """Initialize evidence-based therapeutic interventions."""
        return {
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "name": "Cognitive Restructuring",
                "description": "Help identify and challenge negative thought patterns",
                "techniques": [
                    "Thought challenging",
                    "Evidence examination",
                    "Alternative perspective generation",
                    "Cognitive reframing"
                ],
                "evidence_base": "CBT research shows 60-80% effectiveness for anxiety and depression",
                "contraindications": ["Active psychosis", "Severe cognitive impairment"],
                "duration_minutes": 15
            },
            InterventionType.MINDFULNESS: {
                "name": "Mindfulness Practice",
                "description": "Cultivate present-moment awareness and acceptance",
                "techniques": [
                    "Breathing exercises",
                    "Body scan meditation",
                    "Mindful observation",
                    "Acceptance practices"
                ],
                "evidence_base": "MBSR and MBCT show significant benefits for stress and depression",
                "contraindications": ["Trauma triggers", "Dissociative disorders"],
                "duration_minutes": 10
            },
            InterventionType.COPING_SKILLS: {
                "name": "Coping Skills Training",
                "description": "Develop practical strategies for managing difficult situations",
                "techniques": [
                    "Problem-solving steps",
                    "Distress tolerance skills",
                    "Grounding techniques",
                    "Self-soothing strategies"
                ],
                "evidence_base": "DBT and CBT research supports effectiveness across disorders",
                "contraindications": ["Severe impairment", "Crisis state"],
                "duration_minutes": 12
            },
            InterventionType.EMOTIONAL_REGULATION: {
                "name": "Emotional Regulation",
                "description": "Learn to understand and manage emotional responses",
                "techniques": [
                    "Emotion identification",
                    "Intensity scaling",
                    "Regulation strategies",
                    "Emotional acceptance"
                ],
                "evidence_base": "DBT emotional regulation skills show strong research support",
                "contraindications": ["Severe dissociation", "Active substance use"],
                "duration_minutes": 18
            },
            InterventionType.BEHAVIORAL_ACTIVATION: {
                "name": "Behavioral Activation",
                "description": "Increase engagement in meaningful and rewarding activities",
                "techniques": [
                    "Activity scheduling",
                    "Value identification",
                    "Behavioral experiments",
                    "Mastery and pleasure tracking"
                ],
                "evidence_base": "BA shows effectiveness comparable to CBT for depression",
                "contraindications": ["Severe physical limitations", "Manic episodes"],
                "duration_minutes": 20
            }
        }

    def _initialize_templates(self) -> dict[InterventionType, dict[str, str]]:
        """Initialize intervention delivery templates."""
        return {
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "introduction": "I notice you might be having some challenging thoughts. Let's explore them together.",
                "technique_explanation": "Sometimes our thoughts can be more negative than the situation warrants. Let's examine the evidence.",
                "practice_prompt": "Can you tell me what thoughts are going through your mind right now?",
                "integration": "The character gently guides you to examine your thoughts more objectively."
            },
            InterventionType.MINDFULNESS: {
                "introduction": "It sounds like you're feeling overwhelmed. Let's try grounding ourselves in the present moment.",
                "technique_explanation": "Mindfulness can help us step back from difficult emotions and find some peace.",
                "practice_prompt": "Let's take a few deep breaths together. Focus on the sensation of breathing.",
                "integration": "The character invites you to pause and practice mindful awareness together."
            },
            InterventionType.COPING_SKILLS: {
                "introduction": "This situation seems really challenging. Let's think about some ways to cope with it.",
                "technique_explanation": "Having a toolkit of coping strategies can help us handle difficult moments.",
                "practice_prompt": "What has helped you get through tough times before?",
                "integration": "The character helps you identify and practice effective coping strategies."
            },
            InterventionType.EMOTIONAL_REGULATION: {
                "introduction": "I can see you're experiencing some intense emotions right now.",
                "technique_explanation": "All emotions are valid, and we can learn to work with them skillfully.",
                "practice_prompt": "Can you help me understand what you're feeling and how intense it is?",
                "integration": "The character provides a safe space to explore and understand your emotions."
            },
            InterventionType.BEHAVIORAL_ACTIVATION: {
                "introduction": "It sounds like you've been feeling stuck or disconnected from things you used to enjoy.",
                "technique_explanation": "Sometimes taking small actions, even when we don't feel like it, can help shift our mood.",
                "practice_prompt": "What's one small thing you could do today that might bring you a sense of accomplishment?",
                "integration": "The character encourages you to take small, meaningful steps forward."
            }
        }

    def get_intervention_details(self, intervention_type: InterventionType) -> dict[str, Any]:
        """Get details for a specific intervention type."""
        return self.interventions.get(intervention_type, {})

    def get_intervention_template(self, intervention_type: InterventionType) -> dict[str, str]:
        """Get delivery template for a specific intervention type."""
        return self.intervention_templates.get(intervention_type, {})

    def validate_intervention_appropriateness(self, intervention_type: InterventionType,
                                            session_state: SessionState) -> tuple[bool, list[str]]:
        """
        Validate if an intervention is appropriate for the current session state.

        Args:
            intervention_type: Type of intervention to validate
            session_state: Current session state

        Returns:
            Tuple[bool, List[str]]: (is_appropriate, reasons)
        """
        intervention_details = self.interventions.get(intervention_type)
        if not intervention_details:
            return False, ["Unknown intervention type"]

        contraindications = intervention_details.get("contraindications", [])
        reasons = []

        # Check for contraindications based on session state
        if session_state.emotional_state:
            if session_state.emotional_state.intensity > 0.9:
                if "Crisis state" in contraindications:
                    reasons.append("Emotional intensity too high for this intervention")

        # Check therapeutic progress for readiness
        if session_state.therapeutic_progress:
            if session_state.therapeutic_progress.overall_progress_score < 10:
                if intervention_type == InterventionType.COGNITIVE_RESTRUCTURING:
                    reasons.append("May need basic stabilization before cognitive work")

        is_appropriate = len(reasons) == 0
        return is_appropriate, reasons


class ContentDeliverySystem:
    """System for seamless therapeutic content embedding in narrative contexts."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize content delivery system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.delivery_strategies = self._initialize_delivery_strategies()
        logger.info("ContentDeliverySystem initialized")

    def _initialize_delivery_strategies(self) -> dict[InterventionDeliveryMode, dict[str, Any]]:
        """Initialize content delivery strategies."""
        return {
            InterventionDeliveryMode.DIRECT: {
                "description": "Direct therapeutic dialogue",
                "narrative_integration": "minimal",
                "character_involvement": "therapist_role",
                "immersion_level": "low"
            },
            InterventionDeliveryMode.NARRATIVE_EMBEDDED: {
                "description": "Therapeutic content woven into story",
                "narrative_integration": "high",
                "character_involvement": "story_character",
                "immersion_level": "high"
            },
            InterventionDeliveryMode.CHARACTER_GUIDED: {
                "description": "Character guides therapeutic process",
                "narrative_integration": "medium",
                "character_involvement": "therapeutic_guide",
                "immersion_level": "medium"
            },
            InterventionDeliveryMode.EXPERIENTIAL: {
                "description": "Learn through story experiences",
                "narrative_integration": "very_high",
                "character_involvement": "story_participant",
                "immersion_level": "very_high"
            },
            InterventionDeliveryMode.REFLECTIVE: {
                "description": "Guided reflection on experiences",
                "narrative_integration": "medium",
                "character_involvement": "reflective_guide",
                "immersion_level": "medium"
            }
        }

    def embed_therapeutic_content(self, intervention: DeliveredIntervention,
                                delivery_context: TherapeuticDeliveryContext) -> TherapeuticResponse:
        """
        Embed therapeutic content seamlessly into narrative context.

        Args:
            intervention: The therapeutic intervention to embed
            delivery_context: Context for content delivery

        Returns:
            TherapeuticResponse: Embedded therapeutic content
        """
        try:
            delivery_mode = delivery_context.delivery_mode
            self.delivery_strategies.get(delivery_mode, {})

            # Create therapeutic context for LLM
            therapeutic_context = TherapeuticContext(
                intervention_type=intervention.intervention_type.value,
                delivery_mode=delivery_mode.value,
                character_name=intervention.character_name or "Guide",
                narrative_context=delivery_context.narrative_context.recent_events,
                user_emotional_state=delivery_context.session_state.emotional_state.primary_emotion.value if delivery_context.session_state.emotional_state else "neutral",
                therapeutic_goals=delivery_context.session_state.therapeutic_progress.therapeutic_goals if delivery_context.session_state.therapeutic_progress else [],
                cultural_considerations=delivery_context.cultural_considerations,
                accessibility_needs=delivery_context.accessibility_needs
            )

            # Generate embedded content based on delivery mode
            if delivery_mode == InterventionDeliveryMode.NARRATIVE_EMBEDDED:
                return self._embed_in_narrative(intervention, therapeutic_context)
            elif delivery_mode == InterventionDeliveryMode.CHARACTER_GUIDED:
                return self._embed_through_character(intervention, therapeutic_context)
            elif delivery_mode == InterventionDeliveryMode.EXPERIENTIAL:
                return self._embed_experientially(intervention, therapeutic_context)
            elif delivery_mode == InterventionDeliveryMode.REFLECTIVE:
                return self._embed_reflectively(intervention, therapeutic_context)
            else:  # DIRECT
                return self._embed_directly(intervention, therapeutic_context)

        except Exception as e:
            logger.error(f"Error embedding therapeutic content: {e}")
            return self._generate_fallback_content(intervention)

    def _embed_in_narrative(self, intervention: DeliveredIntervention,
                          context: TherapeuticContext) -> TherapeuticResponse:
        """Embed therapeutic content within narrative flow."""
        f"""
        Embed the following therapeutic intervention naturally into the ongoing story:

        Intervention: {intervention.intervention_type.value}
        Content: {intervention.content}
        Character: {context.character_name}
        Current narrative: {' '.join(context.narrative_context[-3:]) if context.narrative_context else 'Beginning of story'}

        Requirements:
        - Maintain story immersion and character voice
        - Make therapeutic content feel natural and organic
        - Preserve therapeutic value while enhancing narrative
        - Include subtle therapeutic techniques within character dialogue
        """

        return self.llm_client.generate_therapeutic_dialogue(
            context=context,
            character_name=context.character_name,
            validate_content=True
        )

    def _embed_through_character(self, intervention: DeliveredIntervention,
                               context: TherapeuticContext) -> TherapeuticResponse:
        """Embed therapeutic content through character guidance."""

        return self.llm_client.generate_therapeutic_dialogue(
            context=context,
            character_name=context.character_name,
            validate_content=True
        )

    def _embed_experientially(self, intervention: DeliveredIntervention,
                            context: TherapeuticContext) -> TherapeuticResponse:
        """Embed therapeutic content through story experiences."""

        return self.llm_client.generate_therapeutic_intervention(
            context=context,
            intervention_type=intervention.intervention_type
        )

    def _embed_reflectively(self, intervention: DeliveredIntervention,
                          context: TherapeuticContext) -> TherapeuticResponse:
        """Embed therapeutic content through guided reflection."""
        f"""
        Guide the user through reflection on their story experience:

        Intervention: {intervention.intervention_type.value}
        Recent experiences: {' '.join(context.narrative_context[-2:]) if context.narrative_context else 'Recent story events'}

        Create reflective prompts that:
        - Help the user process their story choices and experiences
        - Connect story events to real-life insights
        - Encourage therapeutic growth through reflection
        - Maintain narrative context while promoting insight
        """

        return self.llm_client.generate_therapeutic_dialogue(
            context=context,
            character_name=context.character_name,
            validate_content=True
        )

    def _embed_directly(self, intervention: DeliveredIntervention,
                      context: TherapeuticContext) -> TherapeuticResponse:
        """Embed therapeutic content directly with minimal narrative integration."""
        return TherapeuticResponse(
            content=intervention.content,
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9,
            metadata={
                "delivery_mode": "direct",
                "intervention_type": intervention.intervention_type.value
            }
        )

    def _generate_fallback_content(self, intervention: DeliveredIntervention) -> TherapeuticResponse:
        """Generate fallback content when embedding fails."""
        fallback_content = f"I'd like to share something that might be helpful: {intervention.content}"

        return TherapeuticResponse(
            content=fallback_content,
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.6,
            confidence=0.5,
            metadata={"fallback_content": True},
            warnings=["Using fallback content delivery"]
        )


class TherapeuticGuidanceAgent:
    """
    Main Therapeutic Guidance Agent for evidence-based interventions and content delivery.

    This agent orchestrates therapeutic content integration, crisis detection, and
    seamless embedding of therapeutic interventions within narrative contexts.
    """

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the Therapeutic Guidance Agent."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.evidence_based_interventions = EvidenceBasedInterventions()
        self.content_delivery_system = ContentDeliverySystem(self.llm_client)
        self.crisis_detection_system = CrisisDetectionSystem()

        # Agent state
        self.active_interventions: dict[str, DeliveredIntervention] = {}
        self.intervention_history: list[DeliveredIntervention] = []

        logger.info("TherapeuticGuidanceAgent initialized")

    def generate_therapeutic_intervention(self, opportunity: 'DetectedOpportunity',
                                        delivery_context: TherapeuticDeliveryContext) -> DeliveredIntervention:
        """
        Generate a therapeutic intervention based on detected opportunity.

        Args:
            opportunity: Detected therapeutic opportunity
            delivery_context: Context for intervention delivery

        Returns:
            DeliveredIntervention: Generated therapeutic intervention
        """
        try:
            # Validate inputs
            delivery_context.validate()
            opportunity.validate()

            # Select appropriate intervention type
            intervention_type = self._select_intervention_type(opportunity, delivery_context)

            # Validate intervention appropriateness
            is_appropriate, reasons = self.evidence_based_interventions.validate_intervention_appropriateness(
                intervention_type, delivery_context.session_state
            )

            if not is_appropriate:
                logger.warning(f"Intervention not appropriate: {reasons}")
                # Fall back to basic coping skills
                intervention_type = InterventionType.COPING_SKILLS

            # Get intervention details and template
            self.evidence_based_interventions.get_intervention_details(intervention_type)
            intervention_template = self.evidence_based_interventions.get_intervention_template(intervention_type)

            # Create therapeutic context
            therapeutic_context = TherapeuticContext(
                intervention_type=intervention_type.value,
                delivery_mode=delivery_context.delivery_mode.value,
                character_name=delivery_context.character_context.name if delivery_context.character_context else "Guide",
                narrative_context=delivery_context.narrative_context.recent_events,
                user_emotional_state=delivery_context.session_state.emotional_state.primary_emotion.value if delivery_context.session_state.emotional_state else "neutral",
                therapeutic_goals=delivery_context.session_state.therapeutic_progress.therapeutic_goals if delivery_context.session_state.therapeutic_progress else [],
                cultural_considerations=delivery_context.cultural_considerations,
                accessibility_needs=delivery_context.accessibility_needs
            )

            # Generate intervention content
            therapeutic_response = self.llm_client.generate_therapeutic_intervention(
                context=therapeutic_context,
                intervention_type=intervention_type
            )

            # Create delivered intervention record
            delivered_intervention = DeliveredIntervention(
                intervention_type=intervention_type,
                delivery_mode=delivery_context.delivery_mode,
                content=therapeutic_response.content,
                character_name=therapeutic_context.character_name,
                narrative_integration=intervention_template.get("integration", ""),
                therapeutic_rationale=opportunity.therapeutic_rationale,
                expected_outcomes=self._generate_expected_outcomes(intervention_type, opportunity),
                safety_level=therapeutic_response.safety_level,
                user_response_expected=True,
                follow_up_needed=opportunity.urgency_level.value in ["high", "crisis"],
                effectiveness_metrics={
                    "therapeutic_value": therapeutic_response.therapeutic_value,
                    "confidence": therapeutic_response.confidence,
                    "opportunity_confidence": opportunity.confidence_score
                }
            )

            # Store intervention
            self.active_interventions[delivered_intervention.intervention_id] = delivered_intervention
            self.intervention_history.append(delivered_intervention)

            logger.info(f"Generated therapeutic intervention: {intervention_type.value}")
            return delivered_intervention

        except Exception as e:
            logger.error(f"Error generating therapeutic intervention: {e}")
            return self._generate_fallback_intervention(opportunity, delivery_context)

    def deliver_therapeutic_content(self, intervention: DeliveredIntervention,
                                  delivery_context: TherapeuticDeliveryContext) -> TherapeuticResponse:
        """
        Deliver therapeutic content seamlessly embedded in narrative context.

        Args:
            intervention: The therapeutic intervention to deliver
            delivery_context: Context for content delivery

        Returns:
            TherapeuticResponse: Delivered therapeutic content
        """
        try:
            # Check for crisis indicators first
            crisis_indicators = self.crisis_detection_system.assess_crisis_level(
                user_input="",  # No specific user input for proactive delivery
                session_state=delivery_context.session_state,
                narrative_context=delivery_context.narrative_context
            )

            # If crisis detected, prioritize crisis response
            if crisis_indicators.crisis_level != CrisisLevel.NONE:
                logger.warning(f"Crisis detected during content delivery: {crisis_indicators.crisis_level.value}")
                return self.crisis_detection_system.generate_crisis_response(
                    crisis_indicators, delivery_context
                )

            # Embed therapeutic content using delivery system
            embedded_response = self.content_delivery_system.embed_therapeutic_content(
                intervention, delivery_context
            )

            # Update intervention record with delivery information
            intervention.effectiveness_metrics.update({
                "delivery_success": True,
                "embedded_therapeutic_value": embedded_response.therapeutic_value,
                "safety_level": embedded_response.safety_level
            })

            logger.info(f"Delivered therapeutic content: {intervention.intervention_type.value}")
            return embedded_response

        except Exception as e:
            logger.error(f"Error delivering therapeutic content: {e}")
            return self._generate_delivery_fallback(intervention)

    def assess_and_respond_to_crisis(self, user_input: str, session_state: SessionState,
                                   narrative_context: NarrativeContext) -> TherapeuticResponse | None:
        """
        Assess user input for crisis indicators and respond appropriately.

        Args:
            user_input: User's input text
            session_state: Current session state
            narrative_context: Current narrative context

        Returns:
            Optional[TherapeuticResponse]: Crisis response if crisis detected, None otherwise
        """
        try:
            # Assess crisis level
            crisis_indicators = self.crisis_detection_system.assess_crisis_level(
                user_input, session_state, narrative_context
            )

            # If no crisis, return None
            if crisis_indicators.crisis_level == CrisisLevel.NONE:
                return None

            # Create delivery context for crisis response
            delivery_context = TherapeuticDeliveryContext(
                session_state=session_state,
                narrative_context=narrative_context,
                delivery_mode=InterventionDeliveryMode.DIRECT  # Crisis responses should be direct
            )

            # Generate crisis response
            crisis_response = self.crisis_detection_system.generate_crisis_response(
                crisis_indicators, delivery_context
            )

            # Log crisis intervention
            crisis_intervention = DeliveredIntervention(
                intervention_type=InterventionType.COPING_SKILLS,  # Crisis interventions focus on immediate coping
                delivery_mode=InterventionDeliveryMode.DIRECT,
                content=crisis_response.content,
                therapeutic_rationale=f"Crisis intervention for {crisis_indicators.crisis_level.value} level crisis",
                safety_level=crisis_response.safety_level,
                follow_up_needed=True,
                effectiveness_metrics={
                    "crisis_level": crisis_indicators.crisis_level.value,
                    "confidence": crisis_indicators.confidence_score
                }
            )

            self.active_interventions[crisis_intervention.intervention_id] = crisis_intervention
            self.intervention_history.append(crisis_intervention)

            logger.warning(f"Crisis intervention delivered: {crisis_indicators.crisis_level.value}")
            return crisis_response

        except Exception as e:
            logger.error(f"Error in crisis assessment and response: {e}")
            return self.crisis_detection_system._generate_emergency_fallback_response()

    def _select_intervention_type(self, opportunity: 'DetectedOpportunity',
                                delivery_context: TherapeuticDeliveryContext) -> InterventionType:
        """Select the most appropriate intervention type for the opportunity."""
        # Use the first recommended intervention from the opportunity
        if opportunity.recommended_interventions:
            return opportunity.recommended_interventions[0]

        # Fall back based on opportunity type
        opportunity_to_intervention = {
            'emotional_processing': InterventionType.EMOTIONAL_REGULATION,
            'cognitive_restructuring': InterventionType.COGNITIVE_RESTRUCTURING,
            'anxiety_management': InterventionType.MINDFULNESS,
            'depression_support': InterventionType.BEHAVIORAL_ACTIVATION,
            'coping_skill_building': InterventionType.COPING_SKILLS,
            'crisis_intervention': InterventionType.COPING_SKILLS
        }

        return opportunity_to_intervention.get(
            opportunity.opportunity_type.value,
            InterventionType.COPING_SKILLS
        )

    def _generate_expected_outcomes(self, intervention_type: InterventionType,
                                  opportunity: 'DetectedOpportunity') -> list[str]:
        """Generate expected outcomes for an intervention."""
        base_outcomes = {
            InterventionType.COGNITIVE_RESTRUCTURING: [
                "Increased awareness of thought patterns",
                "Reduced negative thinking",
                "Improved emotional regulation"
            ],
            InterventionType.MINDFULNESS: [
                "Increased present-moment awareness",
                "Reduced anxiety and stress",
                "Improved emotional balance"
            ],
            InterventionType.COPING_SKILLS: [
                "Expanded coping toolkit",
                "Increased confidence in handling challenges",
                "Improved stress management"
            ],
            InterventionType.EMOTIONAL_REGULATION: [
                "Better understanding of emotions",
                "Improved emotional control",
                "Reduced emotional reactivity"
            ],
            InterventionType.BEHAVIORAL_ACTIVATION: [
                "Increased activity and engagement",
                "Improved mood and motivation",
                "Enhanced sense of accomplishment"
            ]
        }

        return base_outcomes.get(intervention_type, ["Improved coping and well-being"])

    def _generate_fallback_intervention(self, opportunity: 'DetectedOpportunity',
                                      delivery_context: TherapeuticDeliveryContext) -> DeliveredIntervention:
        """Generate a fallback intervention when primary generation fails."""
        return DeliveredIntervention(
            intervention_type=InterventionType.COPING_SKILLS,
            delivery_mode=delivery_context.delivery_mode,
            content="I can see you're going through a challenging time. Let's take a moment to breathe and think about what might help you feel more grounded right now.",
            therapeutic_rationale="Fallback supportive intervention",
            safety_level="safe",
            effectiveness_metrics={"fallback": True}
        )

    def _generate_delivery_fallback(self, intervention: DeliveredIntervention) -> TherapeuticResponse:
        """Generate fallback response when content delivery fails."""
        return TherapeuticResponse(
            content=f"I want to share something that might help: {intervention.content}",
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.6,
            confidence=0.5,
            metadata={"delivery_fallback": True},
            warnings=["Using fallback delivery method"]
        )

    def get_intervention_history(self, session_id: str | None = None) -> list[DeliveredIntervention]:
        """Get history of delivered interventions, optionally filtered by session."""
        if session_id:
            # Filter by session if session tracking is implemented
            return [i for i in self.intervention_history if hasattr(i, 'session_id') and i.session_id == session_id]
        return self.intervention_history.copy()

    def get_active_interventions(self) -> dict[str, DeliveredIntervention]:
        """Get currently active interventions."""
        return self.active_interventions.copy()

    def complete_intervention(self, intervention_id: str, effectiveness_rating: float,
                            user_feedback: str | None = None) -> bool:
        """
        Mark an intervention as complete and record effectiveness.

        Args:
            intervention_id: ID of the intervention to complete
            effectiveness_rating: User or system rating of effectiveness (0.0-1.0)
            user_feedback: Optional user feedback

        Returns:
            bool: True if intervention was found and completed
        """
        if intervention_id in self.active_interventions:
            intervention = self.active_interventions[intervention_id]
            intervention.effectiveness_metrics.update({
                "effectiveness_rating": effectiveness_rating,
                "user_feedback": user_feedback,
                "completed_at": datetime.now().isoformat()
            })

            # Remove from active interventions
            del self.active_interventions[intervention_id]

            logger.info(f"Completed intervention {intervention_id} with rating {effectiveness_rating}")
            return True

        return False
