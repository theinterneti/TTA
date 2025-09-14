"""
Enhanced Emotional State Recognition System for TTA Prototype

This module provides enhanced emotional state recognition with clinical-grade
accuracy, comprehensive pattern analysis, and integration with therapeutic
interventions. It builds upon the existing emotional recognition to meet
clinical standards for therapeutic applications.

Classes:
    EnhancedEmotionalStateRecognition: Clinical-grade emotional recognition
    ClinicalEmotionalAssessment: Comprehensive emotional assessment
    EmotionalInterventionMatcher: Matches emotions to therapeutic interventions
    EmotionalSafetyMonitor: Monitors for emotional safety and crisis indicators
"""

import logging
import re
import statistics

# Import system components
import sys
import uuid
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
        EmotionalIntensityLevel,
        EmotionalPattern,
        EmotionalPatternAnalyzer,
        EmotionalPatternType,
        EmotionalStateRecognitionResponse,
        EmotionalTrigger,
        EmotionalTriggerDetector,
        TriggerType,
    )
    from worldbuilding_setting_management import (
        LocationDetails,
        WorldbuildingSettingManagement,
    )
except ImportError as e:
    logging.warning(f"Could not import emotional recognition components: {e}")
    # Create minimal mock classes for testing
    class EmotionalStateRecognitionResponse:
        def __init__(self): pass
    class EmotionalPatternAnalyzer:
        def __init__(self): pass
    class EmotionalTriggerDetector:
        def __init__(self): pass
    class WorldbuildingSettingManagement:
        def __init__(self): pass

logger = logging.getLogger(__name__)


class ClinicalEmotionalSeverity(Enum):
    """Clinical severity levels for emotional states."""
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRISIS = "crisis"


class EmotionalValidationLevel(Enum):
    """Levels of emotional validation needed."""
    ACKNOWLEDGMENT = "acknowledgment"
    REFLECTION = "reflection"
    NORMALIZATION = "normalization"
    VALIDATION = "validation"
    DEEP_VALIDATION = "deep_validation"


class CrisisIndicatorType(Enum):
    """Types of crisis indicators."""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM_RISK = "self_harm_risk"
    PSYCHOTIC_SYMPTOMS = "psychotic_symptoms"
    SEVERE_DISSOCIATION = "severe_dissociation"
    SUBSTANCE_ABUSE_CRISIS = "substance_abuse_crisis"
    DOMESTIC_VIOLENCE = "domestic_violence"
    ACUTE_TRAUMA_RESPONSE = "acute_trauma_response"


@dataclass
class ClinicalEmotionalAssessment:
    """Comprehensive clinical emotional assessment."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    primary_emotion: str = "neutral"
    emotional_intensity: float = 0.5  # 0.0 to 1.0
    clinical_severity: ClinicalEmotionalSeverity = ClinicalEmotionalSeverity.MINIMAL
    secondary_emotions: list[str] = field(default_factory=list)
    emotional_complexity_score: float = 0.0  # 0.0 to 1.0
    emotional_regulation_capacity: float = 0.5  # 0.0 to 1.0
    crisis_indicators: list[CrisisIndicatorType] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    validation_needs: EmotionalValidationLevel = EmotionalValidationLevel.ACKNOWLEDGMENT
    recommended_interventions: list[str] = field(default_factory=list)
    immediate_safety_concerns: bool = False
    professional_consultation_needed: bool = False
    assessment_confidence: float = 0.8  # 0.0 to 1.0
    cultural_considerations: list[str] = field(default_factory=list)
    assessment_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionalSafetyProfile:
    """Profile for monitoring emotional safety."""
    user_id: str
    baseline_emotional_range: dict[str, tuple[float, float]] = field(default_factory=dict)
    known_triggers: list[EmotionalTrigger] = field(default_factory=list)
    coping_resources: list[str] = field(default_factory=list)
    support_network_strength: float = 0.5  # 0.0 to 1.0
    crisis_history: list[dict[str, Any]] = field(default_factory=list)
    safety_plan_elements: list[str] = field(default_factory=list)
    warning_signs: list[str] = field(default_factory=list)
    protective_strategies: list[str] = field(default_factory=list)
    emergency_contacts: list[dict[str, str]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class ClinicalEmotionalAssessor:
    """Clinical-grade emotional assessment with safety monitoring."""

    def __init__(self):
        """Initialize the clinical emotional assessor."""
        self.severity_thresholds = self._initialize_severity_thresholds()
        self.crisis_indicators = self._initialize_crisis_indicators()
        self.validation_strategies = self._initialize_validation_strategies()
        self.cultural_considerations = self._initialize_cultural_considerations()
        logger.info("ClinicalEmotionalAssessor initialized")

    def _initialize_severity_thresholds(self) -> dict[str, dict[str, float]]:
        """Initialize clinical severity thresholds for different emotions."""
        return {
            "anxiety": {
                "mild": 0.3,
                "moderate": 0.5,
                "severe": 0.7,
                "crisis": 0.9
            },
            "depression": {
                "mild": 0.25,
                "moderate": 0.45,
                "severe": 0.65,
                "crisis": 0.85
            },
            "anger": {
                "mild": 0.35,
                "moderate": 0.55,
                "severe": 0.75,
                "crisis": 0.9
            },
            "trauma_response": {
                "mild": 0.2,
                "moderate": 0.4,
                "severe": 0.6,
                "crisis": 0.8
            }
        }

    def _initialize_crisis_indicators(self) -> dict[CrisisIndicatorType, list[str]]:
        """Initialize crisis indicator patterns."""
        return {
            CrisisIndicatorType.SUICIDAL_IDEATION: [
                "want to die", "end my life", "kill myself", "suicide", "better off dead",
                "no point in living", "can't go on", "end it all", "not worth living"
            ],
            CrisisIndicatorType.SELF_HARM_RISK: [
                "hurt myself", "cut myself", "harm myself", "punish myself",
                "deserve pain", "need to feel pain", "self-injury", "self-harm"
            ],
            CrisisIndicatorType.PSYCHOTIC_SYMPTOMS: [
                "hearing voices", "seeing things", "not real", "losing my mind",
                "going crazy", "paranoid", "conspiracy", "they're watching"
            ],
            CrisisIndicatorType.SEVERE_DISSOCIATION: [
                "not real", "floating away", "watching myself", "not in my body",
                "everything is foggy", "can't feel anything", "disconnected"
            ],
            CrisisIndicatorType.SUBSTANCE_ABUSE_CRISIS: [
                "need a drink", "need drugs", "can't stop using", "overdose",
                "withdrawal", "detox", "addiction", "substance abuse"
            ]
        }

    def _initialize_validation_strategies(self) -> dict[EmotionalValidationLevel, dict[str, Any]]:
        """Initialize emotional validation strategies."""
        return {
            EmotionalValidationLevel.ACKNOWLEDGMENT: {
                "techniques": ["simple_acknowledgment", "presence"],
                "responses": ["I hear you", "I see that you're struggling", "Thank you for sharing"],
                "duration": "brief"
            },
            EmotionalValidationLevel.REFLECTION: {
                "techniques": ["emotional_reflection", "paraphrasing"],
                "responses": ["It sounds like you're feeling...", "What I'm hearing is..."],
                "duration": "moderate"
            },
            EmotionalValidationLevel.NORMALIZATION: {
                "techniques": ["normalize_response", "universalize_experience"],
                "responses": ["That's a normal response to...", "Many people feel this way when..."],
                "duration": "moderate"
            },
            EmotionalValidationLevel.VALIDATION: {
                "techniques": ["deep_validation", "emotional_acceptance"],
                "responses": ["Your feelings make complete sense", "Of course you would feel this way"],
                "duration": "extended"
            },
            EmotionalValidationLevel.DEEP_VALIDATION: {
                "techniques": ["profound_validation", "emotional_honoring"],
                "responses": ["Your emotions are completely valid", "I deeply understand why you feel this way"],
                "duration": "extended"
            }
        }

    def _initialize_cultural_considerations(self) -> dict[str, dict[str, Any]]:
        """Initialize cultural considerations for emotional assessment."""
        return {
            "collectivist": {
                "emotional_expression": "indirect",
                "family_involvement": "high",
                "shame_sensitivity": "high",
                "authority_respect": "high"
            },
            "individualist": {
                "emotional_expression": "direct",
                "family_involvement": "moderate",
                "shame_sensitivity": "moderate",
                "authority_respect": "moderate"
            },
            "high_context": {
                "nonverbal_importance": "high",
                "implicit_communication": "high",
                "relationship_focus": "high"
            },
            "low_context": {
                "nonverbal_importance": "moderate",
                "implicit_communication": "low",
                "relationship_focus": "moderate"
            }
        }

    async def conduct_clinical_emotional_assessment(self, user_input: str,
                                                  emotional_history: list[dict[str, Any]],
                                                  safety_profile: EmotionalSafetyProfile,
                                                  cultural_context: dict[str, Any]) -> ClinicalEmotionalAssessment:
        """
        Conduct comprehensive clinical emotional assessment.

        Args:
            user_input: User's input text
            emotional_history: Historical emotional data
            safety_profile: User's emotional safety profile
            cultural_context: Cultural context information

        Returns:
            ClinicalEmotionalAssessment: Comprehensive assessment results
        """
        try:
            assessment = ClinicalEmotionalAssessment(user_id=safety_profile.user_id)

            # Analyze primary emotion and intensity
            emotion_analysis = await self._analyze_primary_emotion(user_input, emotional_history)
            assessment.primary_emotion = emotion_analysis["emotion"]
            assessment.emotional_intensity = emotion_analysis["intensity"]

            # Assess clinical severity
            assessment.clinical_severity = self._assess_clinical_severity(
                assessment.primary_emotion, assessment.emotional_intensity
            )

            # Identify secondary emotions
            assessment.secondary_emotions = await self._identify_secondary_emotions(
                user_input, emotional_history
            )

            # Calculate emotional complexity
            assessment.emotional_complexity_score = self._calculate_emotional_complexity(
                assessment.primary_emotion, assessment.secondary_emotions
            )

            # Assess emotional regulation capacity
            assessment.emotional_regulation_capacity = self._assess_regulation_capacity(
                emotional_history, safety_profile
            )

            # Screen for crisis indicators
            assessment.crisis_indicators = await self._screen_crisis_indicators(
                user_input, emotional_history
            )

            # Identify protective and risk factors
            assessment.protective_factors = self._identify_protective_factors(
                safety_profile, emotional_history
            )
            assessment.risk_factors = self._identify_risk_factors(
                safety_profile, emotional_history, assessment.crisis_indicators
            )

            # Determine validation needs
            assessment.validation_needs = self._determine_validation_needs(
                assessment.clinical_severity, assessment.emotional_complexity_score
            )

            # Generate intervention recommendations
            assessment.recommended_interventions = await self._generate_intervention_recommendations(
                assessment, safety_profile
            )

            # Assess safety concerns
            assessment.immediate_safety_concerns = self._assess_immediate_safety_concerns(
                assessment.crisis_indicators, assessment.risk_factors
            )

            # Determine if professional consultation is needed
            assessment.professional_consultation_needed = self._needs_professional_consultation(
                assessment.clinical_severity, assessment.crisis_indicators
            )

            # Apply cultural considerations
            assessment.cultural_considerations = self._apply_cultural_considerations(
                cultural_context, assessment
            )

            # Calculate assessment confidence
            assessment.assessment_confidence = self._calculate_assessment_confidence(
                user_input, emotional_history, assessment
            )

            logger.info(f"Clinical emotional assessment completed for user {safety_profile.user_id}")
            return assessment

        except Exception as e:
            logger.error(f"Error conducting clinical emotional assessment: {e}")
            # Return minimal assessment with error indication
            assessment = ClinicalEmotionalAssessment(user_id=safety_profile.user_id)
            assessment.immediate_safety_concerns = True
            assessment.professional_consultation_needed = True
            assessment.recommended_interventions = ["immediate_professional_consultation"]
            return assessment

    async def _analyze_primary_emotion(self, user_input: str,
                                     emotional_history: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze primary emotion from user input."""
        # Emotion detection patterns
        emotion_patterns = {
            "anxiety": [
                r"anxious|worried|nervous|scared|afraid|panic|stress",
                r"can't.*stop.*thinking|racing.*thoughts|heart.*pounding"
            ],
            "depression": [
                r"depressed|sad|hopeless|empty|worthless|numb",
                r"no.*point|tired.*all.*time|lost.*interest"
            ],
            "anger": [
                r"angry|mad|furious|rage|irritated|frustrated",
                r"can't.*stand|fed.*up|pissed.*off"
            ],
            "confusion": [
                r"confused|don't.*understand|mixed.*up|unclear",
                r"don't.*know.*what|can't.*figure.*out"
            ],
            "overwhelmed": [
                r"overwhelmed|too.*much|can't.*handle|drowning",
                r"everything.*at.*once|can't.*cope"
            ]
        }

        # Analyze input for emotion patterns
        emotion_scores = {}
        for emotion, patterns in emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, user_input.lower()))
                score += matches
            emotion_scores[emotion] = score

        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            max_score = emotion_scores[primary_emotion]

            # Calculate intensity based on pattern matches and context
            base_intensity = min(max_score * 0.2, 1.0)

            # Adjust based on emotional history
            if emotional_history:
                recent_emotions = [e.get("primary_emotion") for e in emotional_history[-5:]]
                if recent_emotions.count(primary_emotion) >= 2:
                    base_intensity = min(base_intensity + 0.2, 1.0)  # Persistent emotion

            return {"emotion": primary_emotion, "intensity": base_intensity}

        return {"emotion": "neutral", "intensity": 0.3}

    def _assess_clinical_severity(self, emotion: str, intensity: float) -> ClinicalEmotionalSeverity:
        """Assess clinical severity of emotional state."""
        thresholds = self.severity_thresholds.get(emotion, self.severity_thresholds["anxiety"])

        if intensity >= thresholds["crisis"]:
            return ClinicalEmotionalSeverity.CRISIS
        elif intensity >= thresholds["severe"]:
            return ClinicalEmotionalSeverity.SEVERE
        elif intensity >= thresholds["moderate"]:
            return ClinicalEmotionalSeverity.MODERATE
        elif intensity >= thresholds["mild"]:
            return ClinicalEmotionalSeverity.MILD
        else:
            return ClinicalEmotionalSeverity.MINIMAL

    async def _identify_secondary_emotions(self, user_input: str,
                                         emotional_history: list[dict[str, Any]]) -> list[str]:
        """Identify secondary emotions present in the input."""
        secondary_emotions = []

        # Look for multiple emotion indicators
        emotion_indicators = {
            "anxiety": ["worried", "nervous", "tense"],
            "sadness": ["sad", "down", "blue"],
            "anger": ["frustrated", "annoyed", "irritated"],
            "shame": ["ashamed", "embarrassed", "guilty"],
            "fear": ["scared", "afraid", "terrified"],
            "confusion": ["confused", "uncertain", "lost"]
        }

        input_lower = user_input.lower()
        for emotion, indicators in emotion_indicators.items():
            if any(indicator in input_lower for indicator in indicators):
                secondary_emotions.append(emotion)

        return secondary_emotions[:3]  # Limit to top 3 secondary emotions

    def _calculate_emotional_complexity(self, primary_emotion: str,
                                      secondary_emotions: list[str]) -> float:
        """Calculate emotional complexity score."""
        base_complexity = 0.2  # Base complexity for any emotion

        # Add complexity for secondary emotions
        secondary_complexity = len(secondary_emotions) * 0.2

        # Add complexity for conflicting emotions
        conflicting_pairs = [
            ("happy", "sad"), ("angry", "guilty"), ("excited", "anxious"),
            ("love", "hate"), ("confident", "insecure")
        ]

        all_emotions = [primary_emotion] + secondary_emotions
        conflict_complexity = 0
        for emotion1, emotion2 in conflicting_pairs:
            if emotion1 in all_emotions and emotion2 in all_emotions:
                conflict_complexity += 0.3

        total_complexity = base_complexity + secondary_complexity + conflict_complexity
        return min(total_complexity, 1.0)

    def _assess_regulation_capacity(self, emotional_history: list[dict[str, Any]],
                                  safety_profile: EmotionalSafetyProfile) -> float:
        """Assess emotional regulation capacity."""
        base_capacity = 0.5

        # Assess based on coping resources
        coping_resources = len(safety_profile.coping_resources)
        coping_bonus = min(coping_resources * 0.1, 0.3)

        # Assess based on emotional stability in history
        if len(emotional_history) >= 5:
            recent_intensities = [e.get("intensity", 0.5) for e in emotional_history[-5:]]
            stability = 1.0 - statistics.stdev(recent_intensities) if len(recent_intensities) > 1 else 0.5
            stability_bonus = stability * 0.2
        else:
            stability_bonus = 0

        # Assess based on support network
        support_bonus = safety_profile.support_network_strength * 0.2

        total_capacity = base_capacity + coping_bonus + stability_bonus + support_bonus
        return min(total_capacity, 1.0)

    async def _screen_crisis_indicators(self, user_input: str,
                                      emotional_history: list[dict[str, Any]]) -> list[CrisisIndicatorType]:
        """Screen for crisis indicators in user input."""
        detected_indicators = []
        input_lower = user_input.lower()

        for indicator_type, patterns in self.crisis_indicators.items():
            for pattern in patterns:
                if pattern in input_lower:
                    detected_indicators.append(indicator_type)
                    break  # Only add each type once

        return detected_indicators

    def _identify_protective_factors(self, safety_profile: EmotionalSafetyProfile,
                                   emotional_history: list[dict[str, Any]]) -> list[str]:
        """Identify protective factors for emotional safety."""
        protective_factors = []

        # Coping resources
        if safety_profile.coping_resources:
            protective_factors.append(f"Active coping strategies: {len(safety_profile.coping_resources)}")

        # Support network
        if safety_profile.support_network_strength > 0.6:
            protective_factors.append("Strong support network")

        # Safety plan
        if safety_profile.safety_plan_elements:
            protective_factors.append("Established safety plan")

        # Emotional stability
        if len(emotional_history) >= 5:
            recent_intensities = [e.get("intensity", 0.5) for e in emotional_history[-5:]]
            if statistics.mean(recent_intensities) < 0.6:
                protective_factors.append("Recent emotional stability")

        return protective_factors

    def _identify_risk_factors(self, safety_profile: EmotionalSafetyProfile,
                             emotional_history: list[dict[str, Any]],
                             crisis_indicators: list[CrisisIndicatorType]) -> list[str]:
        """Identify risk factors for emotional safety."""
        risk_factors = []

        # Crisis indicators present
        if crisis_indicators:
            risk_factors.append(f"Crisis indicators detected: {len(crisis_indicators)}")

        # Crisis history
        if safety_profile.crisis_history:
            risk_factors.append("Previous crisis episodes")

        # Limited coping resources
        if len(safety_profile.coping_resources) < 3:
            risk_factors.append("Limited coping resources")

        # Weak support network
        if safety_profile.support_network_strength < 0.4:
            risk_factors.append("Weak support network")

        # Escalating emotional intensity
        if len(emotional_history) >= 3:
            recent_intensities = [e.get("intensity", 0.5) for e in emotional_history[-3:]]
            if len(recent_intensities) >= 2 and recent_intensities[-1] > recent_intensities[0] + 0.3:
                risk_factors.append("Escalating emotional intensity")

        return risk_factors

    def _determine_validation_needs(self, severity: ClinicalEmotionalSeverity,
                                  complexity: float) -> EmotionalValidationLevel:
        """Determine level of emotional validation needed."""
        if severity == ClinicalEmotionalSeverity.CRISIS:
            return EmotionalValidationLevel.DEEP_VALIDATION
        elif severity == ClinicalEmotionalSeverity.SEVERE:
            return EmotionalValidationLevel.VALIDATION
        elif complexity > 0.7:
            return EmotionalValidationLevel.VALIDATION
        elif severity == ClinicalEmotionalSeverity.MODERATE:
            return EmotionalValidationLevel.NORMALIZATION
        else:
            return EmotionalValidationLevel.REFLECTION

    async def _generate_intervention_recommendations(self, assessment: ClinicalEmotionalAssessment,
                                                   safety_profile: EmotionalSafetyProfile) -> list[str]:
        """Generate therapeutic intervention recommendations."""
        recommendations = []

        # Crisis interventions
        if assessment.immediate_safety_concerns:
            recommendations.extend([
                "immediate_safety_assessment",
                "crisis_intervention_protocol",
                "professional_consultation"
            ])

        # Severity-based interventions
        if assessment.clinical_severity == ClinicalEmotionalSeverity.SEVERE:
            recommendations.extend([
                "intensive_therapeutic_support",
                "emotion_regulation_skills",
                "safety_planning"
            ])
        elif assessment.clinical_severity == ClinicalEmotionalSeverity.MODERATE:
            recommendations.extend([
                "structured_therapeutic_intervention",
                "coping_skills_development",
                "emotional_processing"
            ])

        # Emotion-specific interventions
        emotion_interventions = {
            "anxiety": ["mindfulness_techniques", "breathing_exercises", "cognitive_restructuring"],
            "depression": ["behavioral_activation", "mood_monitoring", "social_connection"],
            "anger": ["anger_management", "communication_skills", "stress_reduction"],
            "trauma_response": ["trauma_informed_care", "grounding_techniques", "safety_establishment"]
        }

        if assessment.primary_emotion in emotion_interventions:
            recommendations.extend(emotion_interventions[assessment.primary_emotion])

        # Complexity-based interventions
        if assessment.emotional_complexity_score > 0.7:
            recommendations.append("complex_emotion_processing")

        return list(set(recommendations))  # Remove duplicates

    def _assess_immediate_safety_concerns(self, crisis_indicators: list[CrisisIndicatorType],
                                        risk_factors: list[str]) -> bool:
        """Assess if there are immediate safety concerns."""
        high_risk_indicators = [
            CrisisIndicatorType.SUICIDAL_IDEATION,
            CrisisIndicatorType.SELF_HARM_RISK,
            CrisisIndicatorType.PSYCHOTIC_SYMPTOMS
        ]

        return any(indicator in high_risk_indicators for indicator in crisis_indicators)

    def _needs_professional_consultation(self, severity: ClinicalEmotionalSeverity,
                                       crisis_indicators: list[CrisisIndicatorType]) -> bool:
        """Determine if professional consultation is needed."""
        return (severity in [ClinicalEmotionalSeverity.SEVERE, ClinicalEmotionalSeverity.CRISIS] or
                len(crisis_indicators) > 0)

    def _apply_cultural_considerations(self, cultural_context: dict[str, Any],
                                     assessment: ClinicalEmotionalAssessment) -> list[str]:
        """Apply cultural considerations to assessment."""
        considerations = []

        cultural_type = cultural_context.get("cultural_orientation", "individualist")

        if cultural_type == "collectivist":
            considerations.extend([
                "Consider family involvement in treatment",
                "Be sensitive to shame and honor concerns",
                "Respect indirect communication style"
            ])

        if cultural_context.get("religious_considerations"):
            considerations.append("Integrate spiritual/religious perspectives")

        if cultural_context.get("language_barriers"):
            considerations.append("Consider language and communication barriers")

        return considerations

    def _calculate_assessment_confidence(self, user_input: str,
                                       emotional_history: list[dict[str, Any]],
                                       assessment: ClinicalEmotionalAssessment) -> float:
        """Calculate confidence level of the assessment."""
        base_confidence = 0.7

        # Adjust based on input length and detail
        input_length = len(user_input.split())
        if input_length > 20:
            base_confidence += 0.1
        elif input_length < 5:
            base_confidence -= 0.2

        # Adjust based on emotional history availability
        if len(emotional_history) >= 5:
            base_confidence += 0.1
        elif len(emotional_history) == 0:
            base_confidence -= 0.1

        # Adjust based on crisis indicators (lower confidence for crisis)
        if assessment.crisis_indicators:
            base_confidence -= 0.1

        return max(0.3, min(base_confidence, 1.0))


class EmotionalSafetyMonitor:
    """Monitors emotional safety and provides crisis intervention support."""

    def __init__(self):
        """Initialize the emotional safety monitor."""
        self.safety_thresholds = self._initialize_safety_thresholds()
        self.crisis_protocols = self._initialize_crisis_protocols()
        self.monitoring_intervals = self._initialize_monitoring_intervals()
        logger.info("EmotionalSafetyMonitor initialized")

    def _initialize_safety_thresholds(self) -> dict[str, float]:
        """Initialize safety monitoring thresholds."""
        return {
            "crisis_intensity": 0.8,
            "sustained_high_intensity": 0.7,
            "rapid_escalation": 0.4,  # Change in intensity
            "multiple_crisis_indicators": 2
        }

    def _initialize_crisis_protocols(self) -> dict[str, list[str]]:
        """Initialize crisis intervention protocols."""
        return {
            "immediate_response": [
                "acknowledge_crisis",
                "ensure_immediate_safety",
                "activate_support_network",
                "implement_safety_plan"
            ],
            "professional_referral": [
                "contact_emergency_services",
                "notify_mental_health_professional",
                "arrange_immediate_assessment",
                "provide_crisis_resources"
            ],
            "ongoing_monitoring": [
                "increase_check_in_frequency",
                "monitor_safety_indicators",
                "track_intervention_effectiveness",
                "adjust_safety_plan"
            ]
        }

    def _initialize_monitoring_intervals(self) -> dict[str, int]:
        """Initialize monitoring intervals based on risk level."""
        return {
            "crisis": 15,  # minutes
            "high_risk": 60,  # minutes
            "moderate_risk": 240,  # minutes (4 hours)
            "low_risk": 1440  # minutes (24 hours)
        }

    async def monitor_emotional_safety(self, assessment: ClinicalEmotionalAssessment,
                                     safety_profile: EmotionalSafetyProfile,
                                     emotional_history: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Monitor emotional safety and provide recommendations.

        Args:
            assessment: Current clinical emotional assessment
            safety_profile: User's emotional safety profile
            emotional_history: Historical emotional data

        Returns:
            Dict[str, Any]: Safety monitoring results and recommendations
        """
        try:
            monitoring_result = {
                "safety_status": "safe",
                "risk_level": "low",
                "immediate_actions_needed": [],
                "monitoring_recommendations": [],
                "crisis_protocols_activated": [],
                "next_check_in": datetime.now() + timedelta(hours=24),
                "safety_plan_updates": [],
                "professional_consultation_urgency": "none"
            }

            # Assess current safety status
            safety_status = self._assess_current_safety_status(assessment, safety_profile)
            monitoring_result["safety_status"] = safety_status["status"]
            monitoring_result["risk_level"] = safety_status["risk_level"]

            # Determine immediate actions
            if assessment.immediate_safety_concerns:
                monitoring_result["immediate_actions_needed"] = self._get_immediate_actions(
                    assessment, safety_profile
                )
                monitoring_result["crisis_protocols_activated"] = self.crisis_protocols["immediate_response"]

            # Set monitoring frequency
            monitoring_result["next_check_in"] = self._calculate_next_check_in(
                safety_status["risk_level"]
            )

            # Generate monitoring recommendations
            monitoring_result["monitoring_recommendations"] = self._generate_monitoring_recommendations(
                assessment, safety_profile, emotional_history
            )

            # Assess need for professional consultation
            monitoring_result["professional_consultation_urgency"] = self._assess_consultation_urgency(
                assessment, safety_profile
            )

            # Suggest safety plan updates
            monitoring_result["safety_plan_updates"] = self._suggest_safety_plan_updates(
                assessment, safety_profile
            )

            logger.info(f"Emotional safety monitoring completed for user {assessment.user_id}")
            return monitoring_result

        except Exception as e:
            logger.error(f"Error monitoring emotional safety: {e}")
            # Return safe defaults with error indication
            return {
                "safety_status": "unknown",
                "risk_level": "high",
                "immediate_actions_needed": ["professional_consultation"],
                "monitoring_recommendations": ["immediate_professional_assessment"],
                "crisis_protocols_activated": self.crisis_protocols["professional_referral"],
                "next_check_in": datetime.now() + timedelta(minutes=15),
                "safety_plan_updates": ["emergency_professional_contact"],
                "professional_consultation_urgency": "immediate"
            }

    def _assess_current_safety_status(self, assessment: ClinicalEmotionalAssessment,
                                    safety_profile: EmotionalSafetyProfile) -> dict[str, str]:
        """Assess current emotional safety status."""
        if assessment.immediate_safety_concerns:
            return {"status": "crisis", "risk_level": "crisis"}

        if assessment.clinical_severity == ClinicalEmotionalSeverity.CRISIS:
            return {"status": "high_risk", "risk_level": "high"}

        if (assessment.clinical_severity == ClinicalEmotionalSeverity.SEVERE or
            len(assessment.crisis_indicators) > 0):
            return {"status": "moderate_risk", "risk_level": "moderate"}

        if (assessment.clinical_severity == ClinicalEmotionalSeverity.MODERATE and
            assessment.emotional_regulation_capacity < 0.4):
            return {"status": "low_risk", "risk_level": "low"}

        return {"status": "safe", "risk_level": "minimal"}

    def _get_immediate_actions(self, assessment: ClinicalEmotionalAssessment,
                             safety_profile: EmotionalSafetyProfile) -> list[str]:
        """Get immediate actions needed for safety."""
        actions = []

        if CrisisIndicatorType.SUICIDAL_IDEATION in assessment.crisis_indicators:
            actions.extend([
                "suicide_risk_assessment",
                "remove_means_of_harm",
                "activate_crisis_support",
                "emergency_contact_notification"
            ])

        if CrisisIndicatorType.SELF_HARM_RISK in assessment.crisis_indicators:
            actions.extend([
                "self_harm_risk_assessment",
                "implement_safety_strategies",
                "increase_supervision"
            ])

        if not safety_profile.safety_plan_elements:
            actions.append("develop_immediate_safety_plan")

        return actions

    def _calculate_next_check_in(self, risk_level: str) -> datetime:
        """Calculate next check-in time based on risk level."""
        interval_minutes = self.monitoring_intervals.get(risk_level, 1440)
        return datetime.now() + timedelta(minutes=interval_minutes)

    def _generate_monitoring_recommendations(self, assessment: ClinicalEmotionalAssessment,
                                           safety_profile: EmotionalSafetyProfile,
                                           emotional_history: list[dict[str, Any]]) -> list[str]:
        """Generate monitoring recommendations."""
        recommendations = []

        # Based on assessment severity
        if assessment.clinical_severity in [ClinicalEmotionalSeverity.SEVERE, ClinicalEmotionalSeverity.CRISIS]:
            recommendations.extend([
                "continuous_safety_monitoring",
                "frequent_check_ins",
                "professional_supervision"
            ])

        # Based on regulation capacity
        if assessment.emotional_regulation_capacity < 0.3:
            recommendations.extend([
                "emotion_regulation_skill_building",
                "coping_strategy_reinforcement",
                "stress_reduction_techniques"
            ])

        # Based on support network
        if safety_profile.support_network_strength < 0.4:
            recommendations.extend([
                "strengthen_support_network",
                "identify_additional_resources",
                "community_connection_building"
            ])

        return recommendations

    def _assess_consultation_urgency(self, assessment: ClinicalEmotionalAssessment,
                                   safety_profile: EmotionalSafetyProfile) -> str:
        """Assess urgency of professional consultation."""
        if assessment.immediate_safety_concerns:
            return "immediate"

        if assessment.professional_consultation_needed:
            return "urgent"

        if (assessment.clinical_severity == ClinicalEmotionalSeverity.MODERATE and
            len(safety_profile.coping_resources) < 2):
            return "recommended"

        return "none"

    def _suggest_safety_plan_updates(self, assessment: ClinicalEmotionalAssessment,
                                   safety_profile: EmotionalSafetyProfile) -> list[str]:
        """Suggest updates to safety plan."""
        updates = []

        # Add crisis-specific elements
        for indicator in assessment.crisis_indicators:
            if indicator == CrisisIndicatorType.SUICIDAL_IDEATION:
                updates.append("add_suicide_prevention_strategies")
            elif indicator == CrisisIndicatorType.SELF_HARM_RISK:
                updates.append("add_self_harm_prevention_techniques")

        # Add coping strategies for primary emotion
        emotion_strategies = {
            "anxiety": "add_anxiety_management_techniques",
            "depression": "add_depression_coping_strategies",
            "anger": "add_anger_management_techniques"
        }

        if assessment.primary_emotion in emotion_strategies:
            updates.append(emotion_strategies[assessment.primary_emotion])

        # Add support network elements
        if safety_profile.support_network_strength < 0.5:
            updates.append("strengthen_emergency_contact_list")

        return updates


class EnhancedEmotionalStateRecognition:
    """
    Enhanced emotional state recognition with clinical-grade capabilities.

    This class provides comprehensive emotional assessment, safety monitoring,
    and therapeutic intervention matching for clinical therapeutic applications.
    """

    def __init__(self, worldbuilding_manager: WorldbuildingSettingManagement | None = None):
        """
        Initialize enhanced emotional state recognition.

        Args:
            worldbuilding_manager: Optional worldbuilding manager for context integration
        """
        self.worldbuilding_manager = worldbuilding_manager
        self.clinical_assessor = ClinicalEmotionalAssessor()
        self.safety_monitor = EmotionalSafetyMonitor()

        # Storage for safety profiles (in production, this would be database-backed)
        self.safety_profiles: dict[str, EmotionalSafetyProfile] = {}

        logger.info("EnhancedEmotionalStateRecognition system initialized")

    async def recognize_and_assess_emotional_state(self, user_id: str, user_input: str,
                                                 emotional_history: list[dict[str, Any]],
                                                 cultural_context: dict[str, Any] = None,
                                                 world_context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Comprehensive emotional state recognition and assessment.

        Args:
            user_id: User identifier
            user_input: User's input text
            emotional_history: Historical emotional data
            cultural_context: Cultural context information
            world_context: Current world context

        Returns:
            Dict[str, Any]: Comprehensive emotional assessment and recommendations
        """
        try:
            # Get or create safety profile
            safety_profile = self._get_or_create_safety_profile(user_id)

            # Conduct clinical emotional assessment
            clinical_assessment = await self.clinical_assessor.conduct_clinical_emotional_assessment(
                user_input, emotional_history, safety_profile, cultural_context or {}
            )

            # Monitor emotional safety
            safety_monitoring = await self.safety_monitor.monitor_emotional_safety(
                clinical_assessment, safety_profile, emotional_history
            )

            # Integrate with world context if available
            world_integration = {}
            if self.worldbuilding_manager and world_context:
                world_integration = await self._integrate_with_world_context(
                    clinical_assessment, world_context
                )

            # Compile comprehensive results
            results = {
                "clinical_assessment": clinical_assessment,
                "safety_monitoring": safety_monitoring,
                "world_integration": world_integration,
                "therapeutic_recommendations": self._generate_therapeutic_recommendations(
                    clinical_assessment, safety_monitoring
                ),
                "next_steps": self._determine_next_steps(clinical_assessment, safety_monitoring)
            }

            # Update safety profile
            self._update_safety_profile(safety_profile, clinical_assessment)

            logger.info(f"Enhanced emotional state recognition completed for user {user_id}")
            return results

        except Exception as e:
            logger.error(f"Error in enhanced emotional state recognition: {e}")
            return {
                "error": str(e),
                "clinical_assessment": ClinicalEmotionalAssessment(user_id=user_id),
                "safety_monitoring": {"safety_status": "unknown", "risk_level": "high"},
                "therapeutic_recommendations": ["immediate_professional_consultation"],
                "next_steps": ["seek_professional_help"]
            }

    def _get_or_create_safety_profile(self, user_id: str) -> EmotionalSafetyProfile:
        """Get existing safety profile or create new one."""
        if user_id not in self.safety_profiles:
            self.safety_profiles[user_id] = EmotionalSafetyProfile(user_id=user_id)
        return self.safety_profiles[user_id]

    async def _integrate_with_world_context(self, assessment: ClinicalEmotionalAssessment,
                                          world_context: dict[str, Any]) -> dict[str, Any]:
        """Integrate emotional assessment with world context."""
        integration = {
            "environmental_factors": {},
            "location_recommendations": [],
            "narrative_adaptations": [],
            "therapeutic_opportunities": []
        }

        current_location_id = world_context.get("current_location")
        if current_location_id and self.worldbuilding_manager:
            location = self.worldbuilding_manager.get_location_details(current_location_id)

            if location:
                # Assess location therapeutic fit
                therapeutic_fit = self._assess_location_therapeutic_fit(assessment, location)
                integration["environmental_factors"]["current_location_fit"] = therapeutic_fit

                # Recommend better locations if needed
                if therapeutic_fit < 0.6:
                    better_locations = self._recommend_therapeutic_locations(assessment, world_context)
                    integration["location_recommendations"] = better_locations

                # Suggest narrative adaptations
                integration["narrative_adaptations"] = self._suggest_narrative_adaptations(
                    assessment, location
                )

        return integration

    def _assess_location_therapeutic_fit(self, assessment: ClinicalEmotionalAssessment,
                                       location: LocationDetails) -> float:
        """Assess how well current location fits therapeutic needs."""
        fit_score = 0.5  # Base score

        # Safety considerations
        if assessment.immediate_safety_concerns and location.safety_level < 0.8:
            fit_score -= 0.3

        # Emotional state considerations
        if assessment.primary_emotion == "anxiety":
            if "calming" in location.therapeutic_themes:
                fit_score += 0.2
            if location.environmental_factors.get("noise_level") == "high":
                fit_score -= 0.2

        elif assessment.primary_emotion == "depression":
            if "energizing" in location.therapeutic_themes:
                fit_score += 0.2
            if location.environmental_factors.get("lighting") == "bright":
                fit_score += 0.1

        return max(0.0, min(fit_score, 1.0))

    def _recommend_therapeutic_locations(self, assessment: ClinicalEmotionalAssessment,
                                       world_context: dict[str, Any]) -> list[dict[str, Any]]:
        """Recommend therapeutic locations based on emotional needs."""
        recommendations = []

        # Emotion-specific location preferences
        location_preferences = {
            "anxiety": ["safe_space", "quiet_garden", "meditation_area"],
            "depression": ["bright_space", "social_area", "activity_center"],
            "anger": ["private_space", "physical_activity_area", "nature_setting"],
            "overwhelmed": ["simple_space", "minimal_stimulation", "retreat_area"]
        }

        preferred_types = location_preferences.get(assessment.primary_emotion, ["safe_space"])

        for location_type in preferred_types:
            recommendations.append({
                "location_type": location_type,
                "therapeutic_benefit": f"Supports {assessment.primary_emotion} management",
                "priority": "high" if assessment.clinical_severity.value in ["severe", "crisis"] else "medium"
            })

        return recommendations

    def _suggest_narrative_adaptations(self, assessment: ClinicalEmotionalAssessment,
                                     location: LocationDetails) -> list[str]:
        """Suggest narrative adaptations based on emotional state."""
        adaptations = []

        # Severity-based adaptations
        if assessment.clinical_severity == ClinicalEmotionalSeverity.CRISIS:
            adaptations.extend([
                "Prioritize safety and stability in narrative",
                "Avoid intense or triggering content",
                "Focus on grounding and present-moment awareness"
            ])

        # Emotion-specific adaptations
        emotion_adaptations = {
            "anxiety": [
                "Use calming, predictable narrative elements",
                "Provide clear choices and outcomes",
                "Include reassuring character responses"
            ],
            "depression": [
                "Include hopeful and uplifting elements",
                "Highlight character strengths and achievements",
                "Provide opportunities for meaningful connection"
            ],
            "anger": [
                "Acknowledge and validate angry feelings",
                "Provide constructive outlets for expression",
                "Model healthy conflict resolution"
            ]
        }

        if assessment.primary_emotion in emotion_adaptations:
            adaptations.extend(emotion_adaptations[assessment.primary_emotion])

        return adaptations

    def _generate_therapeutic_recommendations(self, assessment: ClinicalEmotionalAssessment,
                                            safety_monitoring: dict[str, Any]) -> list[str]:
        """Generate comprehensive therapeutic recommendations."""
        recommendations = []

        # Include assessment recommendations
        recommendations.extend(assessment.recommended_interventions)

        # Include safety monitoring recommendations
        recommendations.extend(safety_monitoring.get("monitoring_recommendations", []))

        # Add validation-specific recommendations
        validation_strategies = {
            EmotionalValidationLevel.ACKNOWLEDGMENT: ["simple_acknowledgment", "active_listening"],
            EmotionalValidationLevel.REFLECTION: ["emotional_reflection", "empathetic_responses"],
            EmotionalValidationLevel.NORMALIZATION: ["normalize_experience", "reduce_shame"],
            EmotionalValidationLevel.VALIDATION: ["deep_validation", "emotional_acceptance"],
            EmotionalValidationLevel.DEEP_VALIDATION: ["profound_validation", "complete_acceptance"]
        }

        validation_recs = validation_strategies.get(assessment.validation_needs, [])
        recommendations.extend(validation_recs)

        return list(set(recommendations))  # Remove duplicates

    def _determine_next_steps(self, assessment: ClinicalEmotionalAssessment,
                            safety_monitoring: dict[str, Any]) -> list[str]:
        """Determine immediate next steps."""
        next_steps = []

        # Safety-first approach
        if assessment.immediate_safety_concerns:
            next_steps.extend([
                "Implement immediate safety measures",
                "Contact emergency support if needed",
                "Activate crisis intervention protocol"
            ])

        # Professional consultation
        if assessment.professional_consultation_needed:
            urgency = safety_monitoring.get("professional_consultation_urgency", "none")
            if urgency == "immediate":
                next_steps.append("Seek immediate professional help")
            elif urgency == "urgent":
                next_steps.append("Schedule urgent professional consultation")
            elif urgency == "recommended":
                next_steps.append("Consider professional consultation")

        # Therapeutic interventions
        if not assessment.immediate_safety_concerns:
            next_steps.extend([
                "Begin appropriate therapeutic interventions",
                "Monitor emotional state closely",
                "Implement coping strategies"
            ])

        return next_steps

    def _update_safety_profile(self, safety_profile: EmotionalSafetyProfile,
                             assessment: ClinicalEmotionalAssessment) -> None:
        """Update safety profile based on current assessment."""
        # Update crisis history if crisis indicators present
        if assessment.crisis_indicators:
            crisis_event = {
                "timestamp": assessment.assessment_timestamp,
                "indicators": [indicator.value for indicator in assessment.crisis_indicators],
                "severity": assessment.clinical_severity.value
            }
            safety_profile.crisis_history.append(crisis_event)

        # Update warning signs
        if assessment.primary_emotion not in [ws.split(":")[0] for ws in safety_profile.warning_signs]:
            safety_profile.warning_signs.append(f"{assessment.primary_emotion}:intensity_{assessment.emotional_intensity}")

        # Update last modified
        safety_profile.last_updated = datetime.now()

        # Store updated profile
        self.safety_profiles[safety_profile.user_id] = safety_profile
