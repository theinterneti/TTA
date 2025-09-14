"""
Emotional State Recognition and Response System for TTA Prototype

This module implements comprehensive emotional state recognition using NLP-based emotion detection,
pattern analysis, and tracking over time. It provides the foundation for responsive therapeutic
interventions based on user emotional states.

Classes:
    EmotionalStateRecognitionResponse: Main class for emotional state analysis and response
    EmotionalPatternAnalyzer: Analyzes emotional patterns over time
    EmotionalTriggerDetector: Identifies emotional triggers and monitoring
    EmotionalResponseGenerator: Generates appropriate responses to emotional states
"""

import logging
import re
import statistics

# Import system components
import sys
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

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
        DialogueContext,
        EmotionalState,
        EmotionalStateType,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
        UserChoice,
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
            NarrativeContext,
            SessionState,
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
            def analyze_emotional_content(self, text, context=None):
                return {"primary_emotion": "calm", "intensity": 0.5, "confidence": 0.7}

        # Set the mock classes
        EmotionalState = MockEmotionalState
        EmotionalStateType = MockEmotionalStateType
        TherapeuticLLMClient = MockTherapeuticLLMClient

logger = logging.getLogger(__name__)


class EmotionalIntensityLevel(Enum):
    """Levels of emotional intensity."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EmotionalPatternType(Enum):
    """Types of emotional patterns."""
    ESCALATING = "escalating"
    DECLINING = "declining"
    STABLE = "stable"
    CYCLICAL = "cyclical"
    VOLATILE = "volatile"
    SUPPRESSED = "suppressed"


class TriggerType(Enum):
    """Types of emotional triggers."""
    SITUATIONAL = "situational"
    INTERPERSONAL = "interpersonal"
    COGNITIVE = "cognitive"
    PHYSIOLOGICAL = "physiological"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"


@dataclass
class EmotionalPattern:
    """Represents an identified emotional pattern."""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: EmotionalPatternType = EmotionalPatternType.STABLE
    primary_emotions: list[EmotionalStateType] = field(default_factory=list)
    duration: timedelta = field(default_factory=lambda: timedelta(hours=1))
    intensity_trend: str = "stable"  # increasing, decreasing, stable, fluctuating
    frequency: float = 1.0  # occurrences per day
    triggers: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)
    therapeutic_implications: list[str] = field(default_factory=list)
    confidence_score: float = 0.7
    first_observed: datetime = field(default_factory=datetime.now)
    last_observed: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate emotional pattern data."""
        if not self.primary_emotions:
            raise ValidationError("Pattern must have at least one primary emotion")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        if self.frequency < 0:
            raise ValidationError("Frequency cannot be negative")
        return True


@dataclass
class EmotionalTrigger:
    """Represents an identified emotional trigger."""
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType = TriggerType.SITUATIONAL
    description: str = ""
    associated_emotions: list[EmotionalStateType] = field(default_factory=list)
    intensity_impact: float = 0.5  # 0.0 to 1.0
    frequency: int = 1  # how often this trigger occurs
    contexts: list[str] = field(default_factory=list)
    coping_strategies: list[str] = field(default_factory=list)
    avoidance_behaviors: list[str] = field(default_factory=list)
    therapeutic_notes: str = ""
    first_identified: datetime = field(default_factory=datetime.now)
    last_triggered: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate emotional trigger data."""
        if not self.description.strip():
            raise ValidationError("Trigger description cannot be empty")
        if not 0.0 <= self.intensity_impact <= 1.0:
            raise ValidationError("Intensity impact must be between 0.0 and 1.0")
        if self.frequency < 0:
            raise ValidationError("Frequency cannot be negative")
        return True


@dataclass
class EmotionalAnalysisResult:
    """Result of emotional state analysis."""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detected_emotion: EmotionalState = field(default_factory=lambda: EmotionalState())
    confidence_level: float = 0.7
    analysis_method: str = "nlp_analysis"
    contributing_factors: list[str] = field(default_factory=list)
    detected_triggers: list[EmotionalTrigger] = field(default_factory=list)
    pattern_indicators: list[str] = field(default_factory=list)
    therapeutic_recommendations: list[str] = field(default_factory=list)
    crisis_indicators: list[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate analysis result."""
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        for trigger in self.detected_triggers:
            trigger.validate()
        return True


class EmotionalPatternAnalyzer:
    """Analyzes emotional patterns over time."""

    def __init__(self, history_window_days: int = 30):
        """Initialize the emotional pattern analyzer."""
        self.history_window_days = history_window_days
        self.pattern_cache = {}
        self.emotion_history = defaultdict(deque)
        logger.info(f"EmotionalPatternAnalyzer initialized with {history_window_days} day window")

    def analyze_emotional_patterns(self, user_id: str, emotional_history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Analyze emotional patterns from user's emotional history."""
        try:
            if not emotional_history:
                logger.warning(f"No emotional history provided for user {user_id}")
                return []

            # Filter recent history
            cutoff_date = datetime.now() - timedelta(days=self.history_window_days)
            recent_history = [
                state for state in emotional_history
                if state.timestamp >= cutoff_date
            ]

            if not recent_history:
                logger.info(f"No recent emotional history for user {user_id}")
                return []

            patterns = []

            # Analyze different pattern types
            patterns.extend(self._detect_intensity_patterns(recent_history))
            patterns.extend(self._detect_cyclical_patterns(recent_history))
            patterns.extend(self._detect_trigger_patterns(recent_history))
            patterns.extend(self._detect_emotional_transitions(recent_history))

            # Validate and cache patterns
            validated_patterns = []
            for pattern in patterns:
                try:
                    pattern.validate()
                    validated_patterns.append(pattern)
                except ValidationError as e:
                    logger.warning(f"Invalid pattern detected: {e}")

            self.pattern_cache[user_id] = validated_patterns
            logger.info(f"Detected {len(validated_patterns)} emotional patterns for user {user_id}")

            return validated_patterns

        except Exception as e:
            logger.error(f"Error analyzing emotional patterns for user {user_id}: {e}")
            return []

    def _detect_intensity_patterns(self, history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Detect patterns in emotional intensity over time."""
        patterns = []

        if len(history) < 3:
            return patterns

        # Group by emotion type
        emotion_groups = defaultdict(list)
        for state in history:
            emotion_groups[state.primary_emotion].append(state)

        for emotion_type, states in emotion_groups.items():
            if len(states) < 3:
                continue

            # Analyze intensity trend
            intensities = [state.intensity for state in states]

            # Calculate trend
            if len(intensities) >= 3:
                trend = self._calculate_trend(intensities)

                if abs(trend) > 0.1:  # Significant trend
                    pattern_type = EmotionalPatternType.ESCALATING if trend > 0 else EmotionalPatternType.DECLINING

                    pattern = EmotionalPattern(
                        pattern_type=pattern_type,
                        primary_emotions=[emotion_type],
                        duration=states[-1].timestamp - states[0].timestamp,
                        intensity_trend="increasing" if trend > 0 else "decreasing",
                        frequency=len(states) / max(1, (states[-1].timestamp - states[0].timestamp).days),
                        confidence_score=min(0.9, 0.5 + abs(trend)),
                        first_observed=states[0].timestamp,
                        last_observed=states[-1].timestamp,
                        therapeutic_implications=[
                            f"Emotional intensity is {'increasing' if trend > 0 else 'decreasing'} over time",
                            "Monitor for potential intervention needs" if trend > 0 else "Positive emotional regulation trend"
                        ]
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_cyclical_patterns(self, history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Detect cyclical emotional patterns."""
        patterns = []

        if len(history) < 7:  # Need at least a week of data
            return patterns

        # Group by time of day, day of week, etc.
        daily_patterns = defaultdict(list)
        for state in history:
            day_key = state.timestamp.strftime("%A")  # Day of week
            daily_patterns[day_key].append(state)

        # Look for consistent patterns
        for day, states in daily_patterns.items():
            if len(states) >= 3:
                # Check if there's a consistent emotional pattern for this day
                emotion_counts = defaultdict(int)
                for state in states:
                    emotion_counts[state.primary_emotion] += 1

                # If one emotion dominates this day
                dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                if dominant_emotion[1] >= len(states) * 0.6:  # 60% or more
                    pattern = EmotionalPattern(
                        pattern_type=EmotionalPatternType.CYCLICAL,
                        primary_emotions=[dominant_emotion[0]],
                        duration=timedelta(days=1),
                        frequency=1.0,  # Once per week
                        contexts=[f"Recurring on {day}"],
                        confidence_score=dominant_emotion[1] / len(states),
                        therapeutic_implications=[
                            f"Consistent {dominant_emotion[0]} pattern on {day}s",
                            "Consider day-specific therapeutic strategies"
                        ]
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_trigger_patterns(self, history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Detect patterns related to emotional triggers."""
        patterns = []

        # Group states by triggers
        trigger_groups = defaultdict(list)
        for state in history:
            for trigger in state.triggers:
                trigger_groups[trigger].append(state)

        for trigger, states in trigger_groups.items():
            if len(states) >= 2:
                # Analyze emotional response to this trigger
                emotions = [state.primary_emotion for state in states]
                intensities = [state.intensity for state in states]

                # Check for consistent emotional response
                emotion_counts = defaultdict(int)
                for emotion in emotions:
                    emotion_counts[emotion] += 1

                dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                if dominant_emotion[1] >= len(states) * 0.5:  # 50% or more
                    avg_intensity = statistics.mean(intensities)

                    pattern = EmotionalPattern(
                        pattern_type=EmotionalPatternType.STABLE,
                        primary_emotions=[dominant_emotion[0]],
                        triggers=[trigger],
                        frequency=len(states) / max(1, self.history_window_days),
                        confidence_score=dominant_emotion[1] / len(states),
                        therapeutic_implications=[
                            f"Consistent {dominant_emotion[0]} response to '{trigger}'",
                            f"Average intensity: {avg_intensity:.2f}",
                            "Consider trigger-specific coping strategies"
                        ]
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_emotional_transitions(self, history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Detect patterns in emotional transitions."""
        patterns = []

        if len(history) < 4:
            return patterns

        # Analyze transitions between emotional states
        transitions = []
        for i in range(len(history) - 1):
            current = history[i]
            next_state = history[i + 1]

            if current.primary_emotion != next_state.primary_emotion:
                transitions.append((current.primary_emotion, next_state.primary_emotion))

        if not transitions:
            return patterns

        # Find common transition patterns
        transition_counts = defaultdict(int)
        for transition in transitions:
            transition_counts[transition] += 1

        # Identify frequent transitions
        total_transitions = len(transitions)
        for (from_emotion, to_emotion), count in transition_counts.items():
            if count >= 2 and count / total_transitions >= 0.2:  # At least 20% of transitions
                pattern = EmotionalPattern(
                    pattern_type=EmotionalPatternType.VOLATILE if count / total_transitions > 0.4 else EmotionalPatternType.STABLE,
                    primary_emotions=[from_emotion, to_emotion],
                    frequency=count / max(1, self.history_window_days),
                    confidence_score=count / total_transitions,
                    therapeutic_implications=[
                        f"Frequent transition from {from_emotion} to {to_emotion}",
                        "Consider transition-specific interventions"
                    ]
                )
                patterns.append(pattern)

        return patterns

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend in a series of values using simple linear regression."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        # Calculate slope
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator


class EmotionalTriggerDetector:
    """Identifies emotional triggers and monitors their patterns."""

    def __init__(self):
        """Initialize the emotional trigger detector."""
        self.trigger_patterns = self._initialize_trigger_patterns()
        self.contextual_triggers = self._initialize_contextual_triggers()
        logger.info("EmotionalTriggerDetector initialized")

    def _initialize_trigger_patterns(self) -> dict[TriggerType, dict[str, list[str]]]:
        """Initialize patterns for detecting different types of triggers."""
        return {
            TriggerType.SITUATIONAL: {
                "keywords": [
                    "deadline", "pressure", "performance", "evaluation", "test",
                    "interview", "presentation", "conflict", "argument", "confrontation",
                    "loss", "rejection", "failure", "mistake", "criticism"
                ],
                "patterns": [
                    r"under.*pressure", r"deadline.*approaching", r"performance.*review",
                    r"being.*evaluated", r"conflict.*with", r"argument.*about",
                    r"lost.*", r"rejected.*", r"failed.*at", r"made.*mistake"
                ]
            },

            TriggerType.INTERPERSONAL: {
                "keywords": [
                    "relationship", "family", "friend", "partner", "colleague",
                    "betrayal", "abandonment", "isolation", "loneliness", "misunderstanding",
                    "communication", "trust", "intimacy", "boundary", "expectation"
                ],
                "patterns": [
                    r"relationship.*problem", r"family.*issue", r"friend.*betrayed",
                    r"partner.*left", r"feeling.*alone", r"misunderstood.*by",
                    r"trust.*broken", r"boundary.*crossed", r"expectation.*not.*met"
                ]
            },

            TriggerType.COGNITIVE: {
                "keywords": [
                    "thinking", "thoughts", "worry", "rumination", "catastrophizing",
                    "perfectionism", "self-criticism", "comparison", "judgment",
                    "memory", "flashback", "intrusive", "obsessive"
                ],
                "patterns": [
                    r"can't.*stop.*thinking", r"worried.*about", r"keep.*ruminating",
                    r"catastrophic.*thoughts", r"perfectionist.*tendencies", r"comparing.*myself",
                    r"judging.*myself", r"intrusive.*thoughts", r"obsessing.*over"
                ]
            },

            TriggerType.PHYSIOLOGICAL: {
                "keywords": [
                    "tired", "exhausted", "pain", "illness", "medication",
                    "sleep", "appetite", "energy", "physical", "body",
                    "headache", "nausea", "dizzy", "weak", "tense"
                ],
                "patterns": [
                    r"physically.*tired", r"exhausted.*from", r"pain.*in",
                    r"illness.*affecting", r"medication.*side.*effects", r"sleep.*problems",
                    r"appetite.*changes", r"low.*energy", r"body.*aches"
                ]
            },

            TriggerType.ENVIRONMENTAL: {
                "keywords": [
                    "noise", "crowded", "weather", "season", "location",
                    "space", "environment", "surroundings", "atmosphere",
                    "lighting", "temperature", "air", "pollution", "chaos"
                ],
                "patterns": [
                    r"noisy.*environment", r"crowded.*space", r"weather.*affecting",
                    r"seasonal.*changes", r"uncomfortable.*location", r"chaotic.*surroundings",
                    r"poor.*lighting", r"temperature.*bothering", r"air.*quality"
                ]
            },

            TriggerType.TEMPORAL: {
                "keywords": [
                    "anniversary", "birthday", "holiday", "season", "time",
                    "morning", "evening", "night", "weekend", "monday",
                    "schedule", "routine", "timing", "deadline", "calendar"
                ],
                "patterns": [
                    r"anniversary.*of", r"birthday.*approaching", r"holiday.*stress",
                    r"seasonal.*depression", r"morning.*anxiety", r"evening.*sadness",
                    r"weekend.*blues", r"monday.*dread", r"schedule.*overwhelming"
                ]
            }
        }

    def _initialize_contextual_triggers(self) -> dict[str, list[EmotionalStateType]]:
        """Initialize contextual triggers and their associated emotions."""
        return {
            "work_stress": [EmotionalStateType.ANXIOUS, EmotionalStateType.OVERWHELMED],
            "relationship_conflict": [EmotionalStateType.ANGRY, EmotionalStateType.CONFUSED],
            "social_rejection": [EmotionalStateType.DEPRESSED, EmotionalStateType.ANXIOUS],
            "performance_pressure": [EmotionalStateType.ANXIOUS, EmotionalStateType.OVERWHELMED],
            "loss_grief": [EmotionalStateType.DEPRESSED, EmotionalStateType.CONFUSED],
            "health_concerns": [EmotionalStateType.ANXIOUS, EmotionalStateType.OVERWHELMED],
            "financial_stress": [EmotionalStateType.ANXIOUS, EmotionalStateType.ANGRY],
            "family_issues": [EmotionalStateType.CONFUSED, EmotionalStateType.ANGRY],
            "academic_pressure": [EmotionalStateType.ANXIOUS, EmotionalStateType.OVERWHELMED],
            "social_anxiety": [EmotionalStateType.ANXIOUS, EmotionalStateType.CONFUSED]
        }

    def detect_triggers(self, user_input: str, context: NarrativeContext,
                       emotional_history: list[EmotionalState]) -> list[EmotionalTrigger]:
        """Detect emotional triggers from user input and context."""
        try:
            detected_triggers = []

            # Analyze user input for trigger patterns
            input_triggers = self._analyze_input_triggers(user_input)
            detected_triggers.extend(input_triggers)

            # Analyze narrative context for triggers
            context_triggers = self._analyze_context_triggers(context)
            detected_triggers.extend(context_triggers)

            # Analyze historical patterns
            if emotional_history:
                pattern_triggers = self._analyze_pattern_triggers(emotional_history)
                detected_triggers.extend(pattern_triggers)

            # Validate and deduplicate triggers
            validated_triggers = []
            seen_descriptions = set()

            for trigger in detected_triggers:
                try:
                    trigger.validate()
                    if trigger.description not in seen_descriptions:
                        validated_triggers.append(trigger)
                        seen_descriptions.add(trigger.description)
                except ValidationError as e:
                    logger.warning(f"Invalid trigger detected: {e}")

            logger.info(f"Detected {len(validated_triggers)} emotional triggers")
            return validated_triggers

        except Exception as e:
            logger.error(f"Error detecting emotional triggers: {e}")
            return []

    def _analyze_input_triggers(self, user_input: str) -> list[EmotionalTrigger]:
        """Analyze user input for trigger patterns."""
        triggers = []
        input_lower = user_input.lower()

        for trigger_type, patterns in self.trigger_patterns.items():
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in input_lower:
                    trigger = EmotionalTrigger(
                        trigger_type=trigger_type,
                        description=f"Situational trigger: {keyword}",
                        contexts=[f"User mentioned: {keyword}"],
                        therapeutic_notes=f"Detected from user input: '{keyword}'"
                    )
                    triggers.append(trigger)

            # Check regex patterns
            for pattern in patterns["patterns"]:
                matches = re.findall(pattern, input_lower)
                for match in matches:
                    trigger = EmotionalTrigger(
                        trigger_type=trigger_type,
                        description=f"Pattern-based trigger: {match}",
                        contexts=[f"Pattern match: {pattern}"],
                        therapeutic_notes=f"Detected pattern: '{match}'"
                    )
                    triggers.append(trigger)

        return triggers

    def _analyze_context_triggers(self, context: NarrativeContext) -> list[EmotionalTrigger]:
        """Analyze narrative context for potential triggers."""
        triggers = []

        # Analyze recent events for triggers
        for event in context.recent_events[-5:]:  # Last 5 events
            event_lower = event.lower()

            # Check for contextual triggers
            for context_name, associated_emotions in self.contextual_triggers.items():
                context_keywords = context_name.replace("_", " ").split()
                if any(keyword in event_lower for keyword in context_keywords):
                    trigger = EmotionalTrigger(
                        trigger_type=TriggerType.SITUATIONAL,
                        description=f"Narrative trigger: {context_name}",
                        associated_emotions=associated_emotions,
                        contexts=[f"Narrative event: {event}"],
                        therapeutic_notes=f"Triggered by narrative context: {context_name}"
                    )
                    triggers.append(trigger)

        return triggers

    def _analyze_pattern_triggers(self, emotional_history: list[EmotionalState]) -> list[EmotionalTrigger]:
        """Analyze emotional history for recurring trigger patterns."""
        triggers = []

        # Group by triggers in history
        trigger_frequency = defaultdict(list)
        for state in emotional_history[-20:]:  # Last 20 states
            for trigger in state.triggers:
                trigger_frequency[trigger].append(state)

        # Identify frequent triggers
        for trigger_desc, states in trigger_frequency.items():
            if len(states) >= 2:  # Recurring trigger
                emotions = [state.primary_emotion for state in states]
                avg_intensity = statistics.mean([state.intensity for state in states])

                # Determine most common emotion for this trigger
                emotion_counts = defaultdict(int)
                for emotion in emotions:
                    emotion_counts[emotion] += 1

                most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]

                trigger = EmotionalTrigger(
                    trigger_type=TriggerType.SITUATIONAL,  # Default type
                    description=trigger_desc,
                    associated_emotions=[most_common_emotion],
                    intensity_impact=avg_intensity,
                    frequency=len(states),
                    contexts=[f"Recurring pattern with {len(states)} occurrences"],
                    therapeutic_notes=f"Historical pattern: typically leads to {most_common_emotion}"
                )
                triggers.append(trigger)

        return triggers


class EmotionalStateRecognitionResponse:
    """Main class for emotional state recognition and response generation."""

    def __init__(self, llm_client: TherapeuticLLMClient | None = None):
        """Initialize the emotional state recognition system."""
        self.llm_client = llm_client or TherapeuticLLMClient()
        self.pattern_analyzer = EmotionalPatternAnalyzer()
        self.trigger_detector = EmotionalTriggerDetector()

        # Initialize emotion detection patterns
        self.emotion_patterns = self._initialize_emotion_patterns()
        self.intensity_indicators = self._initialize_intensity_indicators()

        logger.info("EmotionalStateRecognitionResponse system initialized")

    def _initialize_emotion_patterns(self) -> dict[EmotionalStateType, dict[str, list[str]]]:
        """Initialize patterns for detecting different emotional states."""
        return {
            EmotionalStateType.ANXIOUS: {
                "keywords": [
                    "worried", "nervous", "anxious", "scared", "afraid", "panic",
                    "stress", "tension", "uneasy", "apprehensive", "concerned"
                ],
                "patterns": [
                    r"worried.*about", r"nervous.*that", r"anxious.*over",
                    r"scared.*of", r"afraid.*might", r"panic.*when",
                    r"stressed.*out", r"feeling.*tense", r"uneasy.*about"
                ],
                "behavioral_indicators": [
                    "avoiding situations", "seeking reassurance", "overthinking",
                    "physical symptoms", "restlessness", "difficulty concentrating"
                ]
            },

            EmotionalStateType.DEPRESSED: {
                "keywords": [
                    "sad", "depressed", "down", "hopeless", "empty", "numb",
                    "worthless", "tired", "exhausted", "lonely", "isolated"
                ],
                "patterns": [
                    r"feeling.*sad", r"depressed.*lately", r"down.*about",
                    r"hopeless.*situation", r"empty.*inside", r"numb.*to",
                    r"worthless.*person", r"tired.*all.*time", r"lonely.*and"
                ],
                "behavioral_indicators": [
                    "withdrawal", "loss of interest", "sleep changes",
                    "appetite changes", "low energy", "difficulty enjoying things"
                ]
            },

            EmotionalStateType.ANGRY: {
                "keywords": [
                    "angry", "mad", "furious", "irritated", "frustrated", "rage",
                    "annoyed", "pissed", "livid", "outraged", "resentful"
                ],
                "patterns": [
                    r"angry.*at", r"mad.*about", r"furious.*with",
                    r"irritated.*by", r"frustrated.*that", r"rage.*over",
                    r"annoyed.*when", r"pissed.*off", r"outraged.*by"
                ],
                "behavioral_indicators": [
                    "aggressive behavior", "raised voice", "confrontational",
                    "blaming others", "impatience", "destructive impulses"
                ]
            },

            EmotionalStateType.OVERWHELMED: {
                "keywords": [
                    "overwhelmed", "too much", "can't handle", "drowning",
                    "overloaded", "swamped", "buried", "crushed", "suffocated"
                ],
                "patterns": [
                    r"overwhelmed.*by", r"too.*much.*to", r"can't.*handle.*all",
                    r"drowning.*in", r"overloaded.*with", r"swamped.*by",
                    r"buried.*under", r"crushed.*by", r"suffocated.*by"
                ],
                "behavioral_indicators": [
                    "procrastination", "avoidance", "difficulty prioritizing",
                    "scattered attention", "emotional outbursts", "shutdown"
                ]
            },

            EmotionalStateType.CONFUSED: {
                "keywords": [
                    "confused", "lost", "uncertain", "unclear", "mixed up",
                    "bewildered", "puzzled", "perplexed", "conflicted", "torn"
                ],
                "patterns": [
                    r"confused.*about", r"lost.*and", r"uncertain.*what",
                    r"unclear.*on", r"mixed.*up.*about", r"bewildered.*by",
                    r"puzzled.*over", r"conflicted.*between", r"torn.*about"
                ],
                "behavioral_indicators": [
                    "indecision", "seeking multiple opinions", "changing mind frequently",
                    "analysis paralysis", "asking many questions", "hesitation"
                ]
            },

            EmotionalStateType.EXCITED: {
                "keywords": [
                    "excited", "thrilled", "elated", "enthusiastic", "energetic",
                    "pumped", "stoked", "ecstatic", "overjoyed", "euphoric"
                ],
                "patterns": [
                    r"excited.*about", r"thrilled.*that", r"elated.*over",
                    r"enthusiastic.*for", r"energetic.*and", r"pumped.*up",
                    r"stoked.*about", r"ecstatic.*over", r"overjoyed.*by"
                ],
                "behavioral_indicators": [
                    "high energy", "rapid speech", "increased activity",
                    "optimistic planning", "social engagement", "impulsiveness"
                ]
            },

            EmotionalStateType.HOPEFUL: {
                "keywords": [
                    "hopeful", "optimistic", "positive", "confident", "encouraged",
                    "uplifted", "inspired", "motivated", "determined", "resilient"
                ],
                "patterns": [
                    r"hopeful.*that", r"optimistic.*about", r"positive.*outlook",
                    r"confident.*in", r"encouraged.*by", r"uplifted.*from",
                    r"inspired.*to", r"motivated.*by", r"determined.*to"
                ],
                "behavioral_indicators": [
                    "goal setting", "future planning", "seeking opportunities",
                    "helping others", "learning new things", "taking initiative"
                ]
            },

            EmotionalStateType.CALM: {
                "keywords": [
                    "calm", "peaceful", "relaxed", "serene", "tranquil",
                    "composed", "centered", "balanced", "stable", "content"
                ],
                "patterns": [
                    r"feeling.*calm", r"peaceful.*state", r"relaxed.*and",
                    r"serene.*moment", r"tranquil.*feeling", r"composed.*despite",
                    r"centered.*and", r"balanced.*approach", r"stable.*mood"
                ],
                "behavioral_indicators": [
                    "steady breathing", "clear thinking", "patient responses",
                    "mindful awareness", "gentle actions", "present focus"
                ]
            }
        }

    def _initialize_intensity_indicators(self) -> dict[EmotionalIntensityLevel, list[str]]:
        """Initialize indicators for different emotional intensity levels."""
        return {
            EmotionalIntensityLevel.VERY_LOW: [
                "slightly", "a little", "somewhat", "mildly", "barely",
                "just a bit", "hardly", "faintly", "subtly"
            ],
            EmotionalIntensityLevel.LOW: [
                "a bit", "kind of", "sort of", "moderately", "fairly",
                "reasonably", "to some degree", "partially"
            ],
            EmotionalIntensityLevel.MODERATE: [
                "quite", "pretty", "rather", "considerably", "notably",
                "significantly", "substantially", "markedly"
            ],
            EmotionalIntensityLevel.HIGH: [
                "very", "really", "extremely", "highly", "intensely",
                "strongly", "deeply", "profoundly", "severely"
            ],
            EmotionalIntensityLevel.VERY_HIGH: [
                "overwhelmingly", "unbearably", "devastatingly", "crushing",
                "paralyzing", "consuming", "all-consuming", "completely"
            ]
        }

    def analyze_emotional_state(self, user_input: str, context: NarrativeContext,
                              session_state: SessionState) -> EmotionalAnalysisResult:
        """Analyze user's emotional state from input and context."""
        try:
            # Detect primary emotion and intensity
            detected_emotion = self._detect_emotion_from_input(user_input)

            # Enhance with context analysis
            context_emotion = self._analyze_contextual_emotion(context, session_state)

            # Combine and refine emotion detection
            final_emotion = self._combine_emotion_analyses(detected_emotion, context_emotion)

            # Detect triggers
            emotional_history = self._get_emotional_history(session_state)
            detected_triggers = self.trigger_detector.detect_triggers(
                user_input, context, emotional_history
            )

            # Generate therapeutic recommendations
            recommendations = self._generate_therapeutic_recommendations(
                final_emotion, detected_triggers, context
            )

            # Check for crisis indicators
            crisis_indicators = self._detect_crisis_indicators(user_input, final_emotion)

            # Create analysis result
            result = EmotionalAnalysisResult(
                detected_emotion=final_emotion,
                confidence_level=final_emotion.confidence_level,
                analysis_method="nlp_pattern_context",
                contributing_factors=self._identify_contributing_factors(user_input, context),
                detected_triggers=detected_triggers,
                pattern_indicators=self._identify_pattern_indicators(final_emotion, emotional_history),
                therapeutic_recommendations=recommendations,
                crisis_indicators=crisis_indicators
            )

            result.validate()
            logger.info(f"Emotional analysis completed: {final_emotion.primary_emotion} (confidence: {final_emotion.confidence_level:.2f})")

            return result

        except Exception as e:
            logger.error(f"Error analyzing emotional state: {e}")
            # Return default calm state on error
            return EmotionalAnalysisResult(
                detected_emotion=EmotionalState(),
                confidence_level=0.1,
                analysis_method="error_fallback",
                therapeutic_recommendations=["Unable to analyze emotional state, consider manual assessment"]
            )

    def _detect_emotion_from_input(self, user_input: str) -> EmotionalState:
        """Detect emotion from user input using pattern matching."""
        input_lower = user_input.lower()
        emotion_scores = defaultdict(float)
        intensity_score = 0.5  # Default moderate intensity

        # Analyze for each emotion type
        for emotion_type, patterns in self.emotion_patterns.items():
            score = 0.0

            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in input_lower:
                    score += 1.0

            # Check regex patterns
            for pattern in patterns["patterns"]:
                matches = re.findall(pattern, input_lower)
                score += len(matches) * 1.5  # Patterns weighted higher

            # Check behavioral indicators
            for indicator in patterns["behavioral_indicators"]:
                if indicator.replace(" ", ".*") in input_lower:
                    score += 0.5

            if score > 0:
                emotion_scores[emotion_type] = score

        # Determine intensity
        for intensity_level, indicators in self.intensity_indicators.items():
            for indicator in indicators:
                if indicator in input_lower:
                    if intensity_level == EmotionalIntensityLevel.VERY_LOW:
                        intensity_score = 0.1
                    elif intensity_level == EmotionalIntensityLevel.LOW:
                        intensity_score = 0.3
                    elif intensity_level == EmotionalIntensityLevel.MODERATE:
                        intensity_score = 0.5
                    elif intensity_level == EmotionalIntensityLevel.HIGH:
                        intensity_score = 0.8
                    elif intensity_level == EmotionalIntensityLevel.VERY_HIGH:
                        intensity_score = 1.0
                    break

        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            confidence = min(0.9, emotion_scores[primary_emotion] / 5.0)  # Normalize confidence

            # Get secondary emotions
            secondary_emotions = [
                emotion for emotion, score in emotion_scores.items()
                if emotion != primary_emotion and score >= 1.0
            ][:3]  # Max 3 secondary emotions
        else:
            primary_emotion = EmotionalStateType.CALM
            confidence = 0.3  # Low confidence for default
            secondary_emotions = []

        return EmotionalState(
            primary_emotion=primary_emotion,
            intensity=intensity_score,
            secondary_emotions=secondary_emotions,
            confidence_level=confidence,
            timestamp=datetime.now()
        )

    def _analyze_contextual_emotion(self, context: NarrativeContext,
                                  session_state: SessionState) -> EmotionalState:
        """Analyze emotional state from narrative context."""
        # Analyze recent events for emotional content
        recent_events_text = " ".join(context.recent_events[-3:])  # Last 3 events

        if recent_events_text:
            return self._detect_emotion_from_input(recent_events_text)

        # Return neutral state if no context
        return EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.5,
            confidence_level=0.2
        )

    def _combine_emotion_analyses(self, input_emotion: EmotionalState,
                                context_emotion: EmotionalState) -> EmotionalState:
        """Combine emotion analyses from input and context."""
        # Weight input emotion higher than context
        input_weight = 0.7
        context_weight = 0.3

        # If input has high confidence, use it primarily
        if input_emotion.confidence_level >= 0.6:
            primary_emotion = input_emotion.primary_emotion
            intensity = input_emotion.intensity
            confidence = input_emotion.confidence_level
        # If context has higher confidence, blend more evenly
        elif context_emotion.confidence_level > input_emotion.confidence_level:
            primary_emotion = context_emotion.primary_emotion
            intensity = (input_emotion.intensity * input_weight +
                        context_emotion.intensity * context_weight)
            confidence = (input_emotion.confidence_level * input_weight +
                         context_emotion.confidence_level * context_weight)
        else:
            primary_emotion = input_emotion.primary_emotion
            intensity = (input_emotion.intensity * input_weight +
                        context_emotion.intensity * context_weight)
            confidence = (input_emotion.confidence_level * input_weight +
                         context_emotion.confidence_level * context_weight)

        # Combine secondary emotions
        secondary_emotions = list(set(
            input_emotion.secondary_emotions + context_emotion.secondary_emotions
        ))[:3]  # Max 3 secondary emotions

        return EmotionalState(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            confidence_level=confidence,
            timestamp=datetime.now()
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

    def _generate_therapeutic_recommendations(self, emotion: EmotionalState,
                                            triggers: list[EmotionalTrigger],
                                            context: NarrativeContext) -> list[str]:
        """Generate therapeutic recommendations based on emotional state."""
        recommendations = []

        # Emotion-specific recommendations
        if emotion.primary_emotion == EmotionalStateType.ANXIOUS:
            recommendations.extend([
                "Consider grounding techniques (5-4-3-2-1 sensory method)",
                "Practice deep breathing exercises",
                "Challenge anxious thoughts with evidence-based thinking"
            ])
            if emotion.intensity > 0.7:
                recommendations.append("Consider immediate anxiety management strategies")

        elif emotion.primary_emotion == EmotionalStateType.DEPRESSED:
            recommendations.extend([
                "Engage in behavioral activation activities",
                "Practice self-compassion techniques",
                "Consider mood monitoring and pleasant activity scheduling"
            ])
            if emotion.intensity > 0.7:
                recommendations.append("Monitor for signs of severe depression")

        elif emotion.primary_emotion == EmotionalStateType.ANGRY:
            recommendations.extend([
                "Practice anger management techniques",
                "Use 'I' statements to express feelings",
                "Consider the underlying needs behind the anger"
            ])
            if emotion.intensity > 0.7:
                recommendations.append("Take time to cool down before responding")

        elif emotion.primary_emotion == EmotionalStateType.OVERWHELMED:
            recommendations.extend([
                "Break tasks into smaller, manageable steps",
                "Practice prioritization techniques",
                "Consider stress management strategies"
            ])

        # Trigger-specific recommendations
        for trigger in triggers:
            if trigger.trigger_type == TriggerType.SITUATIONAL:
                recommendations.append(f"Develop coping strategies for: {trigger.description}")
            elif trigger.trigger_type == TriggerType.COGNITIVE:
                recommendations.append("Practice cognitive restructuring techniques")

        # Intensity-based recommendations
        if emotion.intensity > 0.8:
            recommendations.append("Consider immediate support and crisis resources")
        elif emotion.intensity < 0.3:
            recommendations.append("Explore ways to increase emotional awareness")

        return recommendations[:5]  # Limit to 5 recommendations

    def _detect_crisis_indicators(self, user_input: str, emotion: EmotionalState) -> list[str]:
        """Detect crisis indicators in user input and emotional state."""
        crisis_indicators = []
        input_lower = user_input.lower()

        # Suicide/self-harm indicators
        suicide_keywords = [
            "kill myself", "end it all", "suicide", "want to die",
            "better off dead", "hurt myself", "self-harm", "no point living"
        ]

        for keyword in suicide_keywords:
            if keyword in input_lower:
                crisis_indicators.append(f"Suicide/self-harm indicator: {keyword}")

        # Severe emotional distress
        if emotion.intensity > 0.9:
            crisis_indicators.append(f"Severe emotional intensity: {emotion.primary_emotion}")

        # Hopelessness indicators
        hopelessness_patterns = [
            r"no.*hope", r"hopeless.*situation", r"nothing.*will.*change",
            r"no.*way.*out", r"can't.*go.*on", r"give.*up.*everything"
        ]

        for pattern in hopelessness_patterns:
            if re.search(pattern, input_lower):
                crisis_indicators.append(f"Hopelessness indicator: {pattern}")

        return crisis_indicators

    def _identify_contributing_factors(self, user_input: str, context: NarrativeContext) -> list[str]:
        """Identify factors contributing to the emotional state."""
        factors = []

        # Analyze user input for contributing factors
        input_lower = user_input.lower()

        factor_keywords = {
            "stress": ["stress", "pressure", "deadline", "overwhelmed"],
            "relationships": ["relationship", "family", "friend", "partner"],
            "work": ["work", "job", "career", "boss", "colleague"],
            "health": ["health", "illness", "pain", "tired", "sick"],
            "finances": ["money", "financial", "debt", "bills", "income"],
            "academic": ["school", "study", "exam", "grade", "assignment"]
        }

        for factor_type, keywords in factor_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                factors.append(f"{factor_type.title()} related factors")

        # Analyze narrative context
        if context.recent_events:
            factors.append("Recent narrative events")

        return factors

    def _identify_pattern_indicators(self, emotion: EmotionalState,
                                   history: list[EmotionalState]) -> list[str]:
        """Identify patterns in emotional states."""
        indicators = []

        if not history or len(history) < 2:
            return indicators

        # Check for emotional consistency
        recent_emotions = [state.primary_emotion for state in history[-5:]]
        if len(set(recent_emotions)) == 1:
            indicators.append(f"Consistent {emotion.primary_emotion} pattern")

        # Check for intensity trends
        recent_intensities = [state.intensity for state in history[-3:]]
        if len(recent_intensities) >= 2:
            if recent_intensities[-1] > recent_intensities[0] + 0.2:
                indicators.append("Increasing emotional intensity")
            elif recent_intensities[-1] < recent_intensities[0] - 0.2:
                indicators.append("Decreasing emotional intensity")

        return indicators

    def detect_emotional_patterns(self, user_id: str,
                                emotional_history: list[EmotionalState]) -> list[EmotionalPattern]:
        """Detect emotional patterns over time."""
        return self.pattern_analyzer.analyze_emotional_patterns(user_id, emotional_history)

    def monitor_emotional_triggers(self, user_input: str, context: NarrativeContext,
                                 emotional_history: list[EmotionalState]) -> list[EmotionalTrigger]:
        """Monitor and identify emotional triggers."""
        return self.trigger_detector.detect_triggers(user_input, context, emotional_history)


# Utility functions for testing and validation
def test_emotional_recognition():
    """Test the emotional recognition system."""
    try:
        # Initialize system
        recognition_system = EmotionalStateRecognitionResponse()

        # Test inputs
        test_inputs = [
            "I'm feeling really anxious about the upcoming presentation",
            "I'm so overwhelmed with everything going on",
            "I feel hopeless and don't know what to do",
            "I'm excited about the new opportunities ahead",
            "I'm angry about how I was treated"
        ]

        # Mock context
        from data_models import NarrativeContext, SessionState
        context = NarrativeContext(session_id="test")
        session = SessionState(session_id="test", user_id="test_user")

        for test_input in test_inputs:
            result = recognition_system.analyze_emotional_state(test_input, context, session)
            print(f"Input: {test_input}")
            print(f"Detected: {result.detected_emotion.primary_emotion} (confidence: {result.confidence_level:.2f})")
            print(f"Recommendations: {result.therapeutic_recommendations[:2]}")
            print("---")

        logger.info("Emotional recognition test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Emotional recognition test failed: {e}")
        return False


if __name__ == "__main__":
    # Run test
    test_emotional_recognition()
