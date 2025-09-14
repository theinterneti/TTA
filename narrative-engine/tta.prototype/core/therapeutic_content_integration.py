"""
Therapeutic Content Integration System for TTA Prototype

This module implements the core therapeutic content integration system that identifies
therapeutic opportunities within narrative contexts and generates appropriate evidence-based
interventions. It seamlessly embeds therapeutic content into the narrative flow while
maintaining story immersion and therapeutic effectiveness.

Classes:
    TherapeuticContentIntegration: Main class for therapeutic opportunity identification
    TherapeuticOpportunityDetector: Detects moments suitable for therapeutic intervention
    InterventionGenerator: Generates evidence-based therapeutic interventions
    ContentValidator: Validates therapeutic content appropriateness and safety
"""

import json
import logging
import re

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
except ImportError:
    # Fallback for direct execution
    try:
        from data_models import (
            EmotionalState,
            EmotionalStateType,
            InterventionType,
            NarrativeContext,
            SessionState,
            TherapeuticOpportunity,
            TherapeuticProgress,
            ValidationError,
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
            def generate_therapeutic_intervention(self, context, intervention_type):
                return MockTherapeuticResponse()
            def validate_therapeutic_content(self, content, content_type, goals=None):
                return MockTherapeuticResponse()

        class MockTherapeuticResponse:
            def __init__(self):
                self.content = '{"intervention": {"name": "Mock Intervention"}}'
                self.content_type = "intervention"
                self.safety_level = "safe"
                self.therapeutic_value = 0.7
                self.confidence = 0.8
                self.metadata = {}
                self.warnings = []
                self.recommendations = []

        class MockTherapeuticContext:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class MockTherapeuticContentType:
            INTERVENTION = "intervention"
            DIALOGUE = "dialogue"

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


class OpportunityType(Enum):
    """Types of therapeutic opportunities."""
    EMOTIONAL_PROCESSING = "emotional_processing"
    COGNITIVE_RESTRUCTURING = "cognitive_restructuring"
    COPING_SKILL_BUILDING = "coping_skill_building"
    RELATIONSHIP_EXPLORATION = "relationship_exploration"
    TRAUMA_PROCESSING = "trauma_processing"
    ANXIETY_MANAGEMENT = "anxiety_management"
    DEPRESSION_SUPPORT = "depression_support"
    CRISIS_INTERVENTION = "crisis_intervention"
    MINDFULNESS_PRACTICE = "mindfulness_practice"
    BEHAVIORAL_ACTIVATION = "behavioral_activation"


class InterventionUrgency(Enum):
    """Urgency levels for therapeutic interventions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRISIS = "crisis"


@dataclass
class TherapeuticOpportunityContext:
    """Context information for therapeutic opportunity detection."""
    narrative_context: NarrativeContext
    session_state: SessionState
    user_input: str = ""
    recent_choices: list[dict[str, Any]] = field(default_factory=list)
    emotional_indicators: list[str] = field(default_factory=list)
    behavioral_patterns: dict[str, Any] = field(default_factory=dict)
    environmental_factors: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate opportunity context."""
        if not self.narrative_context:
            raise ValidationError("Narrative context is required")
        if not self.session_state:
            raise ValidationError("Session state is required")
        return True


@dataclass
class DetectedOpportunity:
    """A detected therapeutic opportunity with context and recommendations."""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_type: OpportunityType = OpportunityType.EMOTIONAL_PROCESSING
    trigger_events: list[str] = field(default_factory=list)
    emotional_indicators: list[str] = field(default_factory=list)
    recommended_interventions: list[InterventionType] = field(default_factory=list)
    urgency_level: InterventionUrgency = InterventionUrgency.MEDIUM
    confidence_score: float = 0.5  # 0.0 to 1.0
    narrative_integration_points: list[str] = field(default_factory=list)
    therapeutic_rationale: str = ""
    estimated_duration: int = 10  # minutes
    prerequisites: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate detected opportunity."""
        if not self.trigger_events:
            raise ValidationError("At least one trigger event is required")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        if self.estimated_duration <= 0:
            raise ValidationError("Estimated duration must be positive")
        return True


class TherapeuticOpportunityDetector:
    """Detects therapeutic opportunities within narrative contexts."""

    def __init__(self):
        """Initialize the therapeutic opportunity detector."""
        self.opportunity_patterns = self._initialize_opportunity_patterns()
        self.emotional_triggers = self._initialize_emotional_triggers()
        self.behavioral_indicators = self._initialize_behavioral_indicators()
        logger.info("TherapeuticOpportunityDetector initialized")

    def _initialize_opportunity_patterns(self) -> dict[OpportunityType, dict[str, list[str]]]:
        """Initialize patterns for detecting different types of therapeutic opportunities."""
        return {
            OpportunityType.EMOTIONAL_PROCESSING: {
                "narrative_keywords": [
                    "feeling overwhelmed", "emotional", "upset", "confused about feelings",
                    "don't understand why", "mixed emotions", "emotional turmoil"
                ],
                "user_input_patterns": [
                    r"i feel.*but.*", r"i'm.*confused.*", r"don't know.*feel.*",
                    r"emotional.*mess", r"feelings.*everywhere"
                ],
                "choice_indicators": [
                    "avoid talking about feelings", "express emotions openly",
                    "bottle up emotions", "seek emotional support"
                ]
            },

            OpportunityType.COGNITIVE_RESTRUCTURING: {
                "narrative_keywords": [
                    "always happens to me", "never works out", "i'm terrible at",
                    "everyone thinks", "catastrophic thinking", "worst case scenario"
                ],
                "user_input_patterns": [
                    r"always.*never.*", r"everyone.*thinks.*", r"i'm.*terrible.*",
                    r"nothing.*works.*", r"worst.*happen.*"
                ],
                "choice_indicators": [
                    "assume the worst", "think negatively", "catastrophize",
                    "jump to conclusions", "all-or-nothing thinking"
                ]
            },

            OpportunityType.ANXIETY_MANAGEMENT: {
                "narrative_keywords": [
                    "anxious", "worried", "panic", "nervous", "stressed",
                    "can't stop thinking", "racing thoughts", "heart pounding"
                ],
                "user_input_patterns": [
                    r"anxious.*about.*", r"worried.*that.*", r"can't.*stop.*thinking.*",
                    r"panic.*", r"stressed.*out.*"
                ],
                "choice_indicators": [
                    "avoid the situation", "worry more", "seek reassurance",
                    "try to control everything", "escape the situation"
                ]
            },

            OpportunityType.DEPRESSION_SUPPORT: {
                "narrative_keywords": [
                    "hopeless", "worthless", "empty", "numb", "no point",
                    "tired all the time", "lost interest", "can't enjoy"
                ],
                "user_input_patterns": [
                    r"no.*point.*", r"worthless.*", r"hopeless.*",
                    r"tired.*all.*time.*", r"lost.*interest.*"
                ],
                "choice_indicators": [
                    "isolate myself", "give up", "avoid activities",
                    "stay in bed", "withdraw from others"
                ]
            },

            OpportunityType.COPING_SKILL_BUILDING: {
                "narrative_keywords": [
                    "don't know how to handle", "need help with", "struggling to cope",
                    "overwhelmed by", "can't manage", "need strategies"
                ],
                "user_input_patterns": [
                    r"don't.*know.*how.*", r"need.*help.*", r"struggling.*cope.*",
                    r"overwhelmed.*", r"can't.*manage.*"
                ],
                "choice_indicators": [
                    "ask for help", "learn new skills", "try different approach",
                    "seek guidance", "practice coping strategies"
                ]
            },

            OpportunityType.CRISIS_INTERVENTION: {
                "narrative_keywords": [
                    "want to die", "end it all", "hurt myself", "suicide",
                    "can't go on", "no way out", "better off dead"
                ],
                "user_input_patterns": [
                    r"want.*die.*", r"end.*it.*all.*", r"hurt.*myself.*",
                    r"suicide.*", r"can't.*go.*on.*", r"no.*way.*out.*"
                ],
                "choice_indicators": [
                    "harm myself", "give up on life", "end the pain",
                    "disappear forever", "stop existing"
                ]
            }
        }

    def _initialize_emotional_triggers(self) -> dict[EmotionalStateType, list[str]]:
        """Initialize emotional triggers for different emotional states."""
        return {
            EmotionalStateType.ANXIOUS: [
                "uncertainty", "unknown outcome", "performance pressure",
                "social judgment", "loss of control", "future concerns"
            ],
            EmotionalStateType.DEPRESSED: [
                "loss", "rejection", "failure", "isolation", "hopelessness",
                "meaninglessness", "guilt", "shame"
            ],
            EmotionalStateType.ANGRY: [
                "injustice", "betrayal", "frustration", "powerlessness",
                "disrespect", "boundary violation", "unfairness"
            ],
            EmotionalStateType.OVERWHELMED: [
                "too many demands", "time pressure", "multiple stressors",
                "information overload", "competing priorities", "lack of support"
            ]
        }

    def _initialize_behavioral_indicators(self) -> dict[str, list[str]]:
        """Initialize behavioral indicators for therapeutic opportunities."""
        return {
            "avoidance_patterns": [
                "avoiding difficult conversations", "procrastinating on important tasks",
                "isolating from others", "refusing help", "escaping situations"
            ],
            "maladaptive_coping": [
                "substance use", "self-harm", "aggressive behavior",
                "compulsive behaviors", "emotional eating", "excessive sleeping"
            ],
            "cognitive_distortions": [
                "all-or-nothing thinking", "catastrophizing", "mind reading",
                "fortune telling", "personalization", "emotional reasoning"
            ],
            "interpersonal_difficulties": [
                "conflict with others", "difficulty expressing needs",
                "boundary issues", "trust problems", "communication breakdown"
            ]
        }

    def detect_opportunities(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """
        Detect therapeutic opportunities within the given context.

        Args:
            context: Context information for opportunity detection

        Returns:
            List[DetectedOpportunity]: List of detected therapeutic opportunities
        """
        try:
            context.validate()
            opportunities = []

            # Analyze narrative context
            narrative_opportunities = self._analyze_narrative_context(context)
            opportunities.extend(narrative_opportunities)

            # Analyze user input patterns
            input_opportunities = self._analyze_user_input(context)
            opportunities.extend(input_opportunities)

            # Analyze emotional state
            emotional_opportunities = self._analyze_emotional_state(context)
            opportunities.extend(emotional_opportunities)

            # Analyze behavioral patterns
            behavioral_opportunities = self._analyze_behavioral_patterns(context)
            opportunities.extend(behavioral_opportunities)

            # Analyze choice patterns
            choice_opportunities = self._analyze_choice_patterns(context)
            opportunities.extend(choice_opportunities)

            # Remove duplicates and rank by confidence
            unique_opportunities = self._deduplicate_opportunities(opportunities)
            ranked_opportunities = self._rank_opportunities(unique_opportunities, context)

            logger.info(f"Detected {len(ranked_opportunities)} therapeutic opportunities")
            return ranked_opportunities

        except Exception as e:
            logger.error(f"Error detecting therapeutic opportunities: {e}")
            return []

    def _analyze_narrative_context(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Analyze narrative context for therapeutic opportunities."""
        opportunities = []
        narrative_text = " ".join(context.narrative_context.recent_events).lower()

        for opportunity_type, patterns in self.opportunity_patterns.items():
            narrative_keywords = patterns.get("narrative_keywords", [])

            # Check for keyword matches
            matches = []
            for keyword in narrative_keywords:
                if keyword.lower() in narrative_text:
                    matches.append(keyword)

            if matches:
                # Calculate confidence based on number and specificity of matches
                confidence = min(0.9, 0.3 + (len(matches) * 0.1))

                # Determine urgency based on opportunity type and matches
                urgency = self._determine_urgency(opportunity_type, matches)

                opportunity = DetectedOpportunity(
                    opportunity_type=opportunity_type,
                    trigger_events=matches,
                    recommended_interventions=self._get_recommended_interventions(opportunity_type),
                    urgency_level=urgency,
                    confidence_score=confidence,
                    narrative_integration_points=[
                        f"Character response to: {match}" for match in matches[:3]
                    ],
                    therapeutic_rationale=f"Narrative context indicates {opportunity_type.value} opportunity",
                    estimated_duration=self._estimate_intervention_duration(opportunity_type)
                )

                opportunities.append(opportunity)

        return opportunities

    def _analyze_user_input(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Analyze user input patterns for therapeutic opportunities."""
        opportunities = []
        user_input = context.user_input.lower()

        if not user_input.strip():
            return opportunities

        for opportunity_type, patterns in self.opportunity_patterns.items():
            input_patterns = patterns.get("user_input_patterns", [])

            # Check for pattern matches using regex
            matches = []
            for pattern in input_patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    matches.append(pattern)

            if matches:
                confidence = min(0.95, 0.4 + (len(matches) * 0.15))
                urgency = self._determine_urgency(opportunity_type, matches)

                opportunity = DetectedOpportunity(
                    opportunity_type=opportunity_type,
                    trigger_events=[f"User input pattern: {pattern}" for pattern in matches],
                    emotional_indicators=self._extract_emotional_indicators(user_input),
                    recommended_interventions=self._get_recommended_interventions(opportunity_type),
                    urgency_level=urgency,
                    confidence_score=confidence,
                    narrative_integration_points=[
                        "Character acknowledges user's expression",
                        "Character provides supportive response",
                        "Character guides toward therapeutic intervention"
                    ],
                    therapeutic_rationale=f"User input patterns suggest {opportunity_type.value} need",
                    estimated_duration=self._estimate_intervention_duration(opportunity_type)
                )

                opportunities.append(opportunity)

        return opportunities

    def _analyze_emotional_state(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Analyze emotional state for therapeutic opportunities."""
        opportunities = []

        if not context.session_state.emotional_state:
            return opportunities

        emotional_state = context.session_state.emotional_state
        primary_emotion = emotional_state.primary_emotion
        intensity = emotional_state.intensity

        # High intensity emotions often indicate therapeutic opportunities
        if intensity > 0.7:
            opportunity_type = self._map_emotion_to_opportunity(primary_emotion)

            if opportunity_type:
                confidence = 0.6 + (intensity * 0.3)  # Higher intensity = higher confidence
                urgency = InterventionUrgency.HIGH if intensity > 0.9 else InterventionUrgency.MEDIUM

                opportunity = DetectedOpportunity(
                    opportunity_type=opportunity_type,
                    trigger_events=[f"High intensity {primary_emotion.value} emotion"],
                    emotional_indicators=[primary_emotion.value] + [e.value for e in emotional_state.secondary_emotions],
                    recommended_interventions=self._get_recommended_interventions(opportunity_type),
                    urgency_level=urgency,
                    confidence_score=confidence,
                    narrative_integration_points=[
                        "Character notices emotional state",
                        "Character provides emotional validation",
                        "Character offers appropriate support"
                    ],
                    therapeutic_rationale=f"High intensity {primary_emotion.value} emotion indicates need for {opportunity_type.value}",
                    estimated_duration=self._estimate_intervention_duration(opportunity_type)
                )

                opportunities.append(opportunity)

        return opportunities

    def _analyze_behavioral_patterns(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Analyze behavioral patterns for therapeutic opportunities."""
        opportunities = []
        behavioral_patterns = context.behavioral_patterns

        for pattern_type, indicators in self.behavioral_indicators.items():
            pattern_matches = []

            # Check if any behavioral patterns match indicators
            for pattern_key, pattern_value in behavioral_patterns.items():
                if isinstance(pattern_value, str):
                    for indicator in indicators:
                        if indicator.lower() in pattern_value.lower():
                            pattern_matches.append(f"{pattern_key}: {indicator}")
                elif isinstance(pattern_value, list):
                    for item in pattern_value:
                        if isinstance(item, str):
                            for indicator in indicators:
                                if indicator.lower() in item.lower():
                                    pattern_matches.append(f"{pattern_key}: {indicator}")

            if pattern_matches:
                # Map pattern type to opportunity type
                opportunity_type = self._map_behavioral_pattern_to_opportunity(pattern_type)

                if opportunity_type:
                    confidence = min(0.8, 0.4 + (len(pattern_matches) * 0.1))
                    urgency = InterventionUrgency.MEDIUM

                    opportunity = DetectedOpportunity(
                        opportunity_type=opportunity_type,
                        trigger_events=pattern_matches,
                        recommended_interventions=self._get_recommended_interventions(opportunity_type),
                        urgency_level=urgency,
                        confidence_score=confidence,
                        narrative_integration_points=[
                            "Character observes behavioral pattern",
                            "Character addresses pattern gently",
                            "Character suggests alternative approaches"
                        ],
                        therapeutic_rationale=f"Behavioral pattern {pattern_type} suggests {opportunity_type.value} opportunity",
                        estimated_duration=self._estimate_intervention_duration(opportunity_type)
                    )

                    opportunities.append(opportunity)

        return opportunities

    def _analyze_choice_patterns(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Analyze user choice patterns for therapeutic opportunities."""
        opportunities = []
        recent_choices = context.recent_choices

        if not recent_choices:
            return opportunities

        # Analyze patterns in recent choices
        choice_texts = [choice.get("choice_text", "").lower() for choice in recent_choices]
        choice_pattern = " ".join(choice_texts)

        for opportunity_type, patterns in self.opportunity_patterns.items():
            choice_indicators = patterns.get("choice_indicators", [])

            matches = []
            for indicator in choice_indicators:
                if indicator.lower() in choice_pattern:
                    matches.append(indicator)

            if matches:
                confidence = min(0.85, 0.35 + (len(matches) * 0.12))
                urgency = self._determine_urgency(opportunity_type, matches)

                opportunity = DetectedOpportunity(
                    opportunity_type=opportunity_type,
                    trigger_events=[f"Choice pattern: {match}" for match in matches],
                    recommended_interventions=self._get_recommended_interventions(opportunity_type),
                    urgency_level=urgency,
                    confidence_score=confidence,
                    narrative_integration_points=[
                        "Character reflects on user's choices",
                        "Character explores choice motivations",
                        "Character suggests alternative perspectives"
                    ],
                    therapeutic_rationale=f"Choice patterns indicate {opportunity_type.value} opportunity",
                    estimated_duration=self._estimate_intervention_duration(opportunity_type)
                )

                opportunities.append(opportunity)

        return opportunities

    def _determine_urgency(self, opportunity_type: OpportunityType, matches: list[str]) -> InterventionUrgency:
        """Determine intervention urgency based on opportunity type and matches."""
        if opportunity_type == OpportunityType.CRISIS_INTERVENTION:
            return InterventionUrgency.CRISIS

        # Check for crisis-related keywords in matches
        crisis_keywords = ["suicide", "die", "hurt myself", "end it all", "no way out"]
        for match in matches:
            if any(keyword in match.lower() for keyword in crisis_keywords):
                return InterventionUrgency.CRISIS

        # High urgency conditions
        high_urgency_types = [
            OpportunityType.ANXIETY_MANAGEMENT,
            OpportunityType.DEPRESSION_SUPPORT,
            OpportunityType.TRAUMA_PROCESSING
        ]

        if opportunity_type in high_urgency_types:
            return InterventionUrgency.HIGH

        return InterventionUrgency.MEDIUM

    def _get_recommended_interventions(self, opportunity_type: OpportunityType) -> list[InterventionType]:
        """Get recommended interventions for an opportunity type."""
        intervention_mapping = {
            OpportunityType.EMOTIONAL_PROCESSING: [
                InterventionType.EMOTIONAL_REGULATION,
                InterventionType.MINDFULNESS
            ],
            OpportunityType.COGNITIVE_RESTRUCTURING: [
                InterventionType.COGNITIVE_RESTRUCTURING
            ],
            OpportunityType.ANXIETY_MANAGEMENT: [
                InterventionType.MINDFULNESS,
                InterventionType.COPING_SKILLS,
                InterventionType.COGNITIVE_RESTRUCTURING
            ],
            OpportunityType.DEPRESSION_SUPPORT: [
                InterventionType.BEHAVIORAL_ACTIVATION,
                InterventionType.COGNITIVE_RESTRUCTURING,
                InterventionType.COPING_SKILLS
            ],
            OpportunityType.COPING_SKILL_BUILDING: [
                InterventionType.COPING_SKILLS,
                InterventionType.MINDFULNESS
            ],
            OpportunityType.CRISIS_INTERVENTION: [
                InterventionType.COPING_SKILLS,
                InterventionType.EMOTIONAL_REGULATION
            ],
            OpportunityType.MINDFULNESS_PRACTICE: [
                InterventionType.MINDFULNESS
            ],
            OpportunityType.BEHAVIORAL_ACTIVATION: [
                InterventionType.BEHAVIORAL_ACTIVATION
            ]
        }

        return intervention_mapping.get(opportunity_type, [InterventionType.COPING_SKILLS])

    def _map_emotion_to_opportunity(self, emotion: EmotionalStateType) -> OpportunityType | None:
        """Map emotional state to therapeutic opportunity type."""
        emotion_mapping = {
            EmotionalStateType.ANXIOUS: OpportunityType.ANXIETY_MANAGEMENT,
            EmotionalStateType.DEPRESSED: OpportunityType.DEPRESSION_SUPPORT,
            EmotionalStateType.ANGRY: OpportunityType.EMOTIONAL_PROCESSING,
            EmotionalStateType.OVERWHELMED: OpportunityType.COPING_SKILL_BUILDING,
            EmotionalStateType.CONFUSED: OpportunityType.COGNITIVE_RESTRUCTURING
        }

        return emotion_mapping.get(emotion)

    def _map_behavioral_pattern_to_opportunity(self, pattern_type: str) -> OpportunityType | None:
        """Map behavioral pattern to therapeutic opportunity type."""
        pattern_mapping = {
            "avoidance_patterns": OpportunityType.ANXIETY_MANAGEMENT,
            "maladaptive_coping": OpportunityType.COPING_SKILL_BUILDING,
            "cognitive_distortions": OpportunityType.COGNITIVE_RESTRUCTURING,
            "interpersonal_difficulties": OpportunityType.RELATIONSHIP_EXPLORATION
        }

        return pattern_mapping.get(pattern_type)

    def _estimate_intervention_duration(self, opportunity_type: OpportunityType) -> int:
        """Estimate intervention duration in minutes."""
        duration_mapping = {
            OpportunityType.MINDFULNESS_PRACTICE: 5,
            OpportunityType.COPING_SKILL_BUILDING: 10,
            OpportunityType.EMOTIONAL_PROCESSING: 15,
            OpportunityType.COGNITIVE_RESTRUCTURING: 20,
            OpportunityType.ANXIETY_MANAGEMENT: 15,
            OpportunityType.DEPRESSION_SUPPORT: 25,
            OpportunityType.CRISIS_INTERVENTION: 30,
            OpportunityType.TRAUMA_PROCESSING: 30,
            OpportunityType.RELATIONSHIP_EXPLORATION: 20,
            OpportunityType.BEHAVIORAL_ACTIVATION: 15
        }

        return duration_mapping.get(opportunity_type, 15)

    def _extract_emotional_indicators(self, text: str) -> list[str]:
        """Extract emotional indicators from text."""
        emotional_keywords = [
            "sad", "happy", "angry", "anxious", "worried", "scared", "excited",
            "frustrated", "overwhelmed", "confused", "hopeless", "hopeful",
            "lonely", "isolated", "stressed", "calm", "peaceful", "nervous"
        ]

        indicators = []
        text_lower = text.lower()

        for keyword in emotional_keywords:
            if keyword in text_lower:
                indicators.append(keyword)

        return indicators

    def _deduplicate_opportunities(self, opportunities: list[DetectedOpportunity]) -> list[DetectedOpportunity]:
        """Remove duplicate opportunities based on type and similarity."""
        unique_opportunities = []
        seen_types = set()

        # Sort by confidence score (highest first)
        sorted_opportunities = sorted(opportunities, key=lambda x: x.confidence_score, reverse=True)

        for opportunity in sorted_opportunities:
            # Keep the highest confidence opportunity of each type
            if opportunity.opportunity_type not in seen_types:
                unique_opportunities.append(opportunity)
                seen_types.add(opportunity.opportunity_type)

        return unique_opportunities

    def _rank_opportunities(self, opportunities: list[DetectedOpportunity],
                          context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """Rank opportunities by priority and relevance."""
        def priority_score(opportunity: DetectedOpportunity) -> float:
            score = opportunity.confidence_score

            # Boost score based on urgency
            urgency_boost = {
                InterventionUrgency.CRISIS: 1.0,
                InterventionUrgency.HIGH: 0.3,
                InterventionUrgency.MEDIUM: 0.1,
                InterventionUrgency.LOW: 0.0
            }
            score += urgency_boost.get(opportunity.urgency_level, 0.0)

            # Boost score for opportunities that align with therapeutic goals
            if context.session_state.therapeutic_progress:
                goals = context.session_state.therapeutic_progress.therapeutic_goals
                for goal in goals:
                    if opportunity.opportunity_type.value in goal.description.lower():
                        score += 0.2

            return min(2.0, score)  # Cap at 2.0

        return sorted(opportunities, key=priority_score, reverse=True)


class InterventionGenerator:
    """Generates evidence-based therapeutic interventions."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the intervention generator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.intervention_templates = self._initialize_intervention_templates()
        logger.info("InterventionGenerator initialized")

    def _initialize_intervention_templates(self) -> dict[InterventionType, dict[str, Any]]:
        """Initialize templates for different intervention types."""
        return {
            InterventionType.COGNITIVE_RESTRUCTURING: {
                "name": "Cognitive Restructuring",
                "description": "Examining and challenging unhelpful thought patterns",
                "steps": [
                    "Identify the specific thought or belief",
                    "Examine the evidence for and against this thought",
                    "Consider alternative perspectives",
                    "Develop a more balanced thought",
                    "Practice the new thought pattern"
                ],
                "narrative_integration": "Character guides user through examining their thoughts about the situation",
                "evidence_base": "Cognitive Behavioral Therapy (CBT)"
            },

            InterventionType.MINDFULNESS: {
                "name": "Mindfulness Practice",
                "description": "Developing present-moment awareness and acceptance",
                "steps": [
                    "Find a comfortable position",
                    "Focus on your breathing",
                    "Notice thoughts without judgment",
                    "Return attention to breath when mind wanders",
                    "Practice acceptance of present experience"
                ],
                "narrative_integration": "Character leads user through a mindfulness exercise within the story context",
                "evidence_base": "Mindfulness-Based Stress Reduction (MBSR)"
            },

            InterventionType.EMOTIONAL_REGULATION: {
                "name": "Emotional Regulation",
                "description": "Learning to understand and manage intense emotions",
                "steps": [
                    "Identify and name the emotion",
                    "Understand the emotion's message",
                    "Use grounding techniques if needed",
                    "Choose a healthy response",
                    "Practice self-compassion"
                ],
                "narrative_integration": "Character helps user process emotions through story events",
                "evidence_base": "Dialectical Behavior Therapy (DBT)"
            },

            InterventionType.COPING_SKILLS: {
                "name": "Coping Skills Development",
                "description": "Building practical strategies for managing difficult situations",
                "steps": [
                    "Assess the current situation",
                    "Identify available resources",
                    "Choose appropriate coping strategy",
                    "Implement the strategy",
                    "Evaluate effectiveness"
                ],
                "narrative_integration": "Character teaches coping strategies through story challenges",
                "evidence_base": "Solution-Focused Brief Therapy"
            },

            InterventionType.BEHAVIORAL_ACTIVATION: {
                "name": "Behavioral Activation",
                "description": "Increasing engagement in meaningful and rewarding activities",
                "steps": [
                    "Identify valued activities",
                    "Start with small, achievable goals",
                    "Schedule activities into daily routine",
                    "Monitor mood and energy changes",
                    "Gradually increase activity level"
                ],
                "narrative_integration": "Character encourages user to engage in story activities that mirror real-life behavioral activation",
                "evidence_base": "Behavioral Activation Therapy"
            }
        }

    def generate_intervention(self, opportunity: DetectedOpportunity,
                            context: TherapeuticOpportunityContext) -> TherapeuticResponse:
        """
        Generate a therapeutic intervention for the detected opportunity.

        Args:
            opportunity: Detected therapeutic opportunity
            context: Context information

        Returns:
            TherapeuticResponse: Generated intervention
        """
        try:
            # Select the most appropriate intervention type
            intervention_type = self._select_intervention_type(opportunity, context)

            # Create therapeutic context for LLM
            therapeutic_context = self._create_therapeutic_context(opportunity, context)

            # Generate intervention using LLM
            intervention_response = self.llm_client.generate_therapeutic_intervention(
                therapeutic_context,
                intervention_type.value
            )

            # Enhance with template information
            template = self.intervention_templates.get(intervention_type, {})
            intervention_response.metadata.update({
                "opportunity_id": opportunity.opportunity_id,
                "intervention_template": template,
                "evidence_base": template.get("evidence_base", ""),
                "narrative_integration": template.get("narrative_integration", "")
            })

            return intervention_response

        except Exception as e:
            logger.error(f"Error generating intervention: {e}")
            # Return fallback intervention
            return self._create_fallback_intervention(opportunity, context)

    def _select_intervention_type(self, opportunity: DetectedOpportunity,
                                context: TherapeuticOpportunityContext) -> InterventionType:
        """Select the most appropriate intervention type."""
        recommended = opportunity.recommended_interventions

        if not recommended:
            return InterventionType.COPING_SKILLS

        # Consider user's therapeutic progress and preferences
        if context.session_state.therapeutic_progress:
            completed_interventions = context.session_state.therapeutic_progress.completed_interventions
            intervention_counts = {}

            for intervention in completed_interventions:
                intervention_type = intervention.intervention_type
                intervention_counts[intervention_type] = intervention_counts.get(intervention_type, 0) + 1

            # Prefer interventions that haven't been used as much
            for intervention_type in recommended:
                if intervention_counts.get(intervention_type, 0) < 3:  # Haven't used this type much
                    return intervention_type

        # Default to first recommended intervention
        return recommended[0]

    def _create_therapeutic_context(self, opportunity: DetectedOpportunity,
                                  context: TherapeuticOpportunityContext) -> TherapeuticContext:
        """Create therapeutic context for LLM generation."""
        # Extract therapeutic goals
        therapeutic_goals = []
        if context.session_state.therapeutic_progress:
            therapeutic_goals = [goal.title for goal in context.session_state.therapeutic_progress.therapeutic_goals]

        # Create user history summary
        user_history = {
            "recent_choices": context.recent_choices,
            "emotional_indicators": opportunity.emotional_indicators,
            "trigger_events": opportunity.trigger_events,
            "opportunity_type": opportunity.opportunity_type.value
        }

        return TherapeuticContext(
            user_id=context.session_state.user_id,
            session_id=context.session_state.session_id,
            emotional_state=context.session_state.emotional_state.primary_emotion.value if context.session_state.emotional_state else "neutral",
            therapeutic_goals=therapeutic_goals,
            narrative_context=f"Location: {context.narrative_context.current_location_id}, Recent events: {', '.join(context.narrative_context.recent_events[:3])}",
            character_context="Therapeutic companion providing evidence-based interventions",
            user_history=user_history,
            crisis_indicators=opportunity.emotional_indicators if opportunity.urgency_level == InterventionUrgency.CRISIS else []
        )

    def _create_fallback_intervention(self, opportunity: DetectedOpportunity,
                                    context: TherapeuticOpportunityContext) -> TherapeuticResponse:
        """Create a fallback intervention when generation fails."""
        fallback_content = {
            "intervention": {
                "name": "Grounding Technique",
                "description": "A simple grounding technique to help you feel more centered",
                "instructions": [
                    "Take three deep breaths",
                    "Notice 5 things you can see around you",
                    "Notice 4 things you can touch",
                    "Notice 3 things you can hear",
                    "Notice 2 things you can smell",
                    "Notice 1 thing you can taste"
                ],
                "rationale": "This technique helps bring your attention to the present moment and can reduce anxiety or overwhelming feelings",
                "expected_outcome": "You should feel more grounded and present"
            },
            "safety_considerations": "This is a safe technique for most people",
            "narrative_integration": "The character guides you through this grounding exercise",
            "follow_up": "Practice this technique whenever you feel overwhelmed"
        }

        return TherapeuticResponse(
            content=json.dumps(fallback_content, indent=2),
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.6,
            confidence=0.5,
            metadata={
                "fallback_used": True,
                "opportunity_id": opportunity.opportunity_id
            },
            warnings=["Fallback intervention used due to generation error"]
        )


class ContentValidator:
    """Validates therapeutic content appropriateness and safety."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the content validator."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.safety_keywords = self._initialize_safety_keywords()
        logger.info("ContentValidator initialized")

    def _initialize_safety_keywords(self) -> dict[str, list[str]]:
        """Initialize safety keywords for content validation."""
        return {
            "crisis_indicators": [
                "suicide", "kill myself", "end it all", "hurt myself",
                "self-harm", "die", "overdose", "jump", "hang"
            ],
            "inappropriate_advice": [
                "you should leave", "break up with", "quit your job",
                "cut contact", "never speak to", "they're toxic"
            ],
            "boundary_violations": [
                "i love you", "we should meet", "personal relationship",
                "outside of therapy", "special connection"
            ],
            "medical_advice": [
                "stop taking medication", "increase dosage", "medical diagnosis",
                "you have", "medical condition", "see a doctor immediately"
            ]
        }

    def validate_therapeutic_content(self, content: str,
                                   intervention_type: InterventionType,
                                   context: TherapeuticOpportunityContext) -> dict[str, Any]:
        """
        Validate therapeutic content for safety and appropriateness.

        Args:
            content: Content to validate
            intervention_type: Type of intervention
            context: Therapeutic context

        Returns:
            Dict[str, Any]: Validation results
        """
        try:
            validation_results = {
                "is_safe": True,
                "is_appropriate": True,
                "safety_score": 1.0,
                "therapeutic_value": 0.5,
                "warnings": [],
                "recommendations": [],
                "approval_status": "approved"
            }

            # Check for safety issues
            safety_issues = self._check_safety_keywords(content)
            if safety_issues:
                validation_results["is_safe"] = False
                validation_results["safety_score"] = 0.0
                validation_results["warnings"].extend(safety_issues)
                validation_results["approval_status"] = "rejected"

            # Check appropriateness for intervention type
            appropriateness_score = self._check_intervention_appropriateness(content, intervention_type)
            validation_results["therapeutic_value"] = appropriateness_score

            if appropriateness_score < 0.5:
                validation_results["is_appropriate"] = False
                validation_results["recommendations"].append("Content may not be appropriate for this intervention type")

            # Use LLM for additional validation if content passes basic checks
            if validation_results["is_safe"] and validation_results["is_appropriate"]:
                llm_validation = self.llm_client.validate_therapeutic_content(
                    content,
                    TherapeuticContentType.INTERVENTION,
                    [goal.title for goal in context.session_state.therapeutic_progress.therapeutic_goals] if context.session_state.therapeutic_progress else []
                )

                # Incorporate LLM validation results
                if llm_validation.safety_level in [SafetyLevel.UNSAFE, SafetyLevel.CRISIS]:
                    validation_results["is_safe"] = False
                    validation_results["approval_status"] = "rejected"

                validation_results["therapeutic_value"] = max(
                    validation_results["therapeutic_value"],
                    llm_validation.therapeutic_value
                )

                validation_results["warnings"].extend(llm_validation.warnings)
                validation_results["recommendations"].extend(llm_validation.recommendations)

            return validation_results

        except Exception as e:
            logger.error(f"Error validating therapeutic content: {e}")
            return {
                "is_safe": False,
                "is_appropriate": False,
                "safety_score": 0.0,
                "therapeutic_value": 0.0,
                "warnings": [f"Validation error: {str(e)}"],
                "recommendations": ["Manual review required"],
                "approval_status": "needs_review"
            }

    def _check_safety_keywords(self, content: str) -> list[str]:
        """Check content for safety keyword violations."""
        issues = []
        content_lower = content.lower()

        for category, keywords in self.safety_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    issues.append(f"{category}: Found '{keyword}'")

        return issues

    def _check_intervention_appropriateness(self, content: str,
                                          intervention_type: InterventionType) -> float:
        """Check if content is appropriate for the intervention type."""
        content_lower = content.lower()

        # Define expected keywords for each intervention type
        expected_keywords = {
            InterventionType.COGNITIVE_RESTRUCTURING: [
                "thought", "thinking", "belief", "perspective", "evidence", "challenge"
            ],
            InterventionType.MINDFULNESS: [
                "breath", "present", "notice", "aware", "mindful", "moment"
            ],
            InterventionType.EMOTIONAL_REGULATION: [
                "emotion", "feeling", "regulate", "manage", "cope", "accept"
            ],
            InterventionType.COPING_SKILLS: [
                "strategy", "skill", "cope", "manage", "technique", "practice"
            ],
            InterventionType.BEHAVIORAL_ACTIVATION: [
                "activity", "behavior", "action", "engage", "participate", "schedule"
            ]
        }

        keywords = expected_keywords.get(intervention_type, [])
        if not keywords:
            return 0.5  # Neutral score if no keywords defined

        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in content_lower)

        # Calculate appropriateness score
        return min(1.0, 0.3 + (matches * 0.15))


class TherapeuticContentIntegration:
    """Main class for therapeutic content integration system."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the therapeutic content integration system."""
        self.opportunity_detector = TherapeuticOpportunityDetector()
        self.intervention_generator = InterventionGenerator(llm_client)
        self.content_validator = ContentValidator(llm_client)
        self.llm_client = llm_client or TherapeuticLLMClient()

        # Initialize technique demonstration system
        try:
            from .therapeutic_technique_demonstration import TherapeuticTechniqueDemo
            self.technique_demo = TherapeuticTechniqueDemo(llm_client)
            logger.info("TherapeuticTechniqueDemo integrated successfully")
        except ImportError as e:
            try:
                # Try alternative import path
                import sys
                from pathlib import Path
                core_path = Path(__file__).parent
                if str(core_path) not in sys.path:
                    sys.path.append(str(core_path))
                from therapeutic_technique_demonstration import TherapeuticTechniqueDemo
                self.technique_demo = TherapeuticTechniqueDemo(llm_client)
                logger.info("TherapeuticTechniqueDemo integrated successfully (alternative import)")
            except ImportError:
                logger.warning(f"TherapeuticTechniqueDemo not available - technique demonstrations disabled: {e}")
                self.technique_demo = None

        logger.info("TherapeuticContentIntegration system initialized")

    def identify_therapeutic_moments(self, context: TherapeuticOpportunityContext) -> list[DetectedOpportunity]:
        """
        Identify therapeutic opportunities within the narrative context.

        Args:
            context: Context information for opportunity detection

        Returns:
            List[DetectedOpportunity]: List of detected therapeutic opportunities
        """
        return self.opportunity_detector.detect_opportunities(context)

    def generate_therapeutic_intervention(self, opportunity: DetectedOpportunity,
                                        context: TherapeuticOpportunityContext) -> TherapeuticResponse:
        """
        Generate a therapeutic intervention for the detected opportunity.

        Args:
            opportunity: Detected therapeutic opportunity
            context: Context information

        Returns:
            TherapeuticResponse: Generated intervention
        """
        return self.intervention_generator.generate_intervention(opportunity, context)

    def assess_user_emotional_state(self, user_input: str,
                                  narrative_context: NarrativeContext,
                                  session_state: SessionState) -> EmotionalState:
        """
        Assess user's emotional state based on input and context.

        Args:
            user_input: User's input text
            narrative_context: Current narrative context
            session_state: Current session state

        Returns:
            EmotionalState: Assessed emotional state
        """
        try:
            # Extract emotional indicators from user input
            emotional_indicators = self.opportunity_detector._extract_emotional_indicators(user_input)

            # Determine primary emotion based on indicators and context
            primary_emotion = self._determine_primary_emotion(emotional_indicators, user_input)

            # Calculate intensity based on language patterns
            intensity = self._calculate_emotional_intensity(user_input, emotional_indicators)

            # Identify secondary emotions
            secondary_emotions = self._identify_secondary_emotions(emotional_indicators, primary_emotion)

            # Identify triggers
            triggers = self._identify_emotional_triggers(user_input, narrative_context)

            return EmotionalState(
                primary_emotion=primary_emotion,
                intensity=intensity,
                secondary_emotions=secondary_emotions,
                triggers=triggers,
                confidence_level=0.7  # Base confidence level
            )

        except Exception as e:
            logger.error(f"Error assessing emotional state: {e}")
            # Return neutral emotional state as fallback
            return EmotionalState(
                primary_emotion=EmotionalStateType.CALM,
                intensity=0.5,
                confidence_level=0.3
            )

    def demonstrate_therapeutic_technique(self, technique_type: str,
                                        context: NarrativeContext,
                                        session_state: SessionState,
                                        user_preferences: dict[str, Any] = None) -> dict[str, Any]:
        """
        Create a therapeutic technique demonstration through narrative.

        Args:
            technique_type: Type of technique to demonstrate
            context: Current narrative context
            session_state: Current session state
            user_preferences: User preferences for demonstration

        Returns:
            Dict[str, Any]: Technique demonstration package
        """
        if not self.technique_demo:
            logger.warning("Technique demonstration not available")
            return {"error": "Technique demonstration system not available"}

        try:
            # Map string technique type to enum
            try:
                from .therapeutic_technique_demonstration import TechniqueType
            except ImportError:
                from therapeutic_technique_demonstration import TechniqueType
            technique_map = {
                "deep_breathing": TechniqueType.DEEP_BREATHING,
                "grounding_5_4_3_2_1": TechniqueType.GROUNDING_5_4_3_2_1,
                "cognitive_reframing": TechniqueType.COGNITIVE_REFRAMING,
                "mindful_observation": TechniqueType.MINDFUL_OBSERVATION,
                "progressive_muscle_relaxation": TechniqueType.PROGRESSIVE_MUSCLE_RELAXATION
            }

            technique_enum = technique_map.get(technique_type.lower())
            if not technique_enum:
                raise ValueError(f"Unknown technique type: {technique_type}")

            # Create technique demonstration
            demonstration = self.technique_demo.create_technique_demonstration(
                technique_type=technique_enum,
                context=context,
                session_state=session_state,
                user_preferences=user_preferences or {}
            )

            logger.info(f"Created technique demonstration for {technique_type}")
            return demonstration

        except Exception as e:
            logger.error(f"Error creating technique demonstration: {e}")
            return {"error": f"Failed to create technique demonstration: {str(e)}"}

    def execute_technique_step(self, demonstration_package: dict[str, Any],
                             step_number: int,
                             user_response: dict[str, Any] = None) -> dict[str, Any]:
        """
        Execute a step in a technique demonstration.

        Args:
            demonstration_package: Technique demonstration package
            step_number: Step number to execute
            user_response: User's response to previous step

        Returns:
            Dict[str, Any]: Step execution results
        """
        if not self.technique_demo:
            return {"error": "Technique demonstration system not available"}

        try:
            return self.technique_demo.execute_technique_step(
                demonstration_package=demonstration_package,
                step_number=step_number,
                user_response=user_response or {}
            )
        except Exception as e:
            logger.error(f"Error executing technique step: {e}")
            return {"error": f"Failed to execute step: {str(e)}"}

    def generate_technique_reflection(self, demonstration_package: dict[str, Any],
                                    user_experience: dict[str, Any],
                                    context: NarrativeContext) -> dict[str, Any]:
        """
        Generate reflection opportunity after technique demonstration.

        Args:
            demonstration_package: Completed demonstration package
            user_experience: User's experience data
            context: Current narrative context

        Returns:
            Dict[str, Any]: Reflection opportunity data
        """
        if not self.technique_demo:
            return {"error": "Technique demonstration system not available"}

        try:
            reflection = self.technique_demo.generate_reflection_opportunity(
                demonstration_package=demonstration_package,
                user_experience=user_experience,
                context=context
            )

            # Convert to dictionary for easier handling
            return {
                "opportunity_id": reflection.opportunity_id,
                "trigger_event": reflection.trigger_event,
                "reflection_type": reflection.reflection_type,
                "guiding_questions": reflection.guiding_questions,
                "learning_points": reflection.learning_points,
                "narrative_integration": reflection.narrative_integration,
                "character_facilitation": reflection.character_facilitation,
                "expected_insights": reflection.expected_insights,
                "follow_up_actions": reflection.follow_up_actions,
                "created_at": reflection.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating technique reflection: {e}")
            return {"error": f"Failed to generate reflection: {str(e)}"}

    def adapt_therapy_approach(self, user_profile: dict[str, Any],
                             progress: TherapeuticProgress) -> dict[str, Any]:
        """
        Adapt therapy approach based on user profile and progress.

        Args:
            user_profile: User profile information
            progress: Current therapeutic progress

        Returns:
            Dict[str, Any]: Adapted therapy strategy
        """
        try:
            strategy = {
                "preferred_interventions": [],
                "communication_style": "supportive",
                "pacing": "moderate",
                "focus_areas": [],
                "adaptations": [],
                "technique_recommendations": []
            }

            # Analyze completed interventions for effectiveness
            if progress.completed_interventions:
                intervention_effectiveness = {}
                for intervention in progress.completed_interventions:
                    intervention_type = intervention.intervention_type
                    if intervention_type not in intervention_effectiveness:
                        intervention_effectiveness[intervention_type] = []
                    intervention_effectiveness[intervention_type].append(intervention.effectiveness_rating)

                # Identify most effective interventions
                for intervention_type, ratings in intervention_effectiveness.items():
                    avg_rating = sum(ratings) / len(ratings)
                    if avg_rating >= 7.0:  # High effectiveness threshold
                        strategy["preferred_interventions"].append(intervention_type.value)

            # Recommend technique demonstrations based on progress
            if progress.overall_progress_score < 30:
                strategy["pacing"] = "slow"
                strategy["communication_style"] = "gentle"
                strategy["adaptations"].append("Focus on building rapport and safety")
                strategy["technique_recommendations"].extend([
                    "deep_breathing", "grounding_5_4_3_2_1"
                ])
            elif progress.overall_progress_score > 70:
                strategy["pacing"] = "accelerated"
                strategy["adaptations"].append("Ready for more challenging interventions")
                strategy["technique_recommendations"].extend([
                    "cognitive_reframing", "progressive_muscle_relaxation"
                ])
            else:
                strategy["technique_recommendations"].extend([
                    "deep_breathing", "mindful_observation"
                ])

            # Identify focus areas based on active goals
            for goal in progress.therapeutic_goals:
                if goal.progress_percentage < 50:
                    strategy["focus_areas"].append(goal.title)

            return strategy

        except Exception as e:
            logger.error(f"Error adapting therapy approach: {e}")
            return {
                "preferred_interventions": ["coping_skills"],
                "communication_style": "supportive",
                "pacing": "moderate",
                "focus_areas": ["general_wellbeing"],
                "adaptations": ["Standard supportive approach"],
                "technique_recommendations": ["deep_breathing"]
            }

    def validate_content_appropriateness(self, content: str,
                                       intervention_type: InterventionType,
                                       context: TherapeuticOpportunityContext) -> dict[str, Any]:
        """
        Validate therapeutic content for appropriateness and safety.

        Args:
            content: Content to validate
            intervention_type: Type of intervention
            context: Therapeutic context

        Returns:
            Dict[str, Any]: Validation results
        """
        return self.content_validator.validate_therapeutic_content(content, intervention_type, context)

    def _determine_primary_emotion(self, indicators: list[str], user_input: str) -> EmotionalStateType:
        """Determine primary emotion from indicators and input."""
        if not indicators:
            return EmotionalStateType.CALM

        # Map indicators to emotions
        emotion_mapping = {
            "anxious": EmotionalStateType.ANXIOUS,
            "worried": EmotionalStateType.ANXIOUS,
            "nervous": EmotionalStateType.ANXIOUS,
            "scared": EmotionalStateType.ANXIOUS,
            "sad": EmotionalStateType.DEPRESSED,
            "hopeless": EmotionalStateType.DEPRESSED,
            "empty": EmotionalStateType.DEPRESSED,
            "angry": EmotionalStateType.ANGRY,
            "frustrated": EmotionalStateType.ANGRY,
            "overwhelmed": EmotionalStateType.OVERWHELMED,
            "stressed": EmotionalStateType.OVERWHELMED,
            "confused": EmotionalStateType.CONFUSED,
            "excited": EmotionalStateType.EXCITED,
            "happy": EmotionalStateType.EXCITED
        }

        # Count emotion types
        emotion_counts = {}
        for indicator in indicators:
            emotion = emotion_mapping.get(indicator.lower())
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if emotion_counts:
            # Return most frequent emotion
            return max(emotion_counts.items(), key=lambda x: x[1])[0]

        return EmotionalStateType.CALM

    def _calculate_emotional_intensity(self, user_input: str, indicators: list[str]) -> float:
        """Calculate emotional intensity from input patterns."""
        intensity = 0.5  # Base intensity

        # Intensity indicators
        high_intensity_patterns = [
            r"very\s+\w+", r"extremely\s+\w+", r"so\s+\w+", r"really\s+\w+",
            r"!!+", r"completely\s+\w+", r"totally\s+\w+"
        ]

        for pattern in high_intensity_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                intensity += 0.15

        # Multiple emotional indicators suggest higher intensity
        intensity += min(0.3, len(indicators) * 0.1)

        return min(1.0, intensity)

    def _identify_secondary_emotions(self, indicators: list[str],
                                   primary_emotion: EmotionalStateType) -> list[EmotionalStateType]:
        """Identify secondary emotions from indicators."""
        emotion_mapping = {
            "anxious": EmotionalStateType.ANXIOUS,
            "worried": EmotionalStateType.ANXIOUS,
            "sad": EmotionalStateType.DEPRESSED,
            "angry": EmotionalStateType.ANGRY,
            "frustrated": EmotionalStateType.ANGRY,
            "overwhelmed": EmotionalStateType.OVERWHELMED,
            "confused": EmotionalStateType.CONFUSED
        }

        secondary_emotions = []
        for indicator in indicators:
            emotion = emotion_mapping.get(indicator.lower())
            if emotion and emotion != primary_emotion and emotion not in secondary_emotions:
                secondary_emotions.append(emotion)

        return secondary_emotions[:3]  # Limit to 3 secondary emotions

    def _identify_emotional_triggers(self, user_input: str,
                                   narrative_context: NarrativeContext) -> list[str]:
        """Identify emotional triggers from input and context."""
        triggers = []

        # Common trigger patterns
        trigger_patterns = [
            r"because of\s+(.+)", r"when\s+(.+)\s+happens?", r"(.+)\s+makes me",
            r"triggered by\s+(.+)", r"upset about\s+(.+)"
        ]

        for pattern in trigger_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            triggers.extend(matches)

        # Add narrative context triggers
        if "conflict" in " ".join(narrative_context.recent_events).lower():
            triggers.append("interpersonal conflict")

        return triggers[:5]  # Limit to 5 triggers
