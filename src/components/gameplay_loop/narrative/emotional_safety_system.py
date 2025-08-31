"""
Emotional Safety System for Therapeutic Narrative Engine

This module provides real-time emotional state monitoring, trigger detection,
intervention mechanisms, and emotional regulation support for therapeutic gameplay.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.services.session_state import SessionState

from .events import EventBus, EventType, create_safety_event

logger = logging.getLogger(__name__)


class EmotionalState(str, Enum):
    """Primary emotional states for monitoring."""

    CALM = "calm"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    ANGRY = "angry"
    FEARFUL = "fearful"
    EXCITED = "excited"
    CONFUSED = "confused"
    OVERWHELMED = "overwhelmed"
    HOPEFUL = "hopeful"
    FRUSTRATED = "frustrated"


class DistressLevel(IntEnum):
    """Levels of emotional distress."""

    NONE = 0
    MILD = 1
    MODERATE = 2
    HIGH = 3
    SEVERE = 4
    CRITICAL = 5


class InterventionType(str, Enum):
    """Types of emotional safety interventions."""

    GROUNDING_TECHNIQUE = "grounding_technique"
    BREATHING_EXERCISE = "breathing_exercise"
    CONTENT_WARNING = "content_warning"
    PAUSE_SUGGESTION = "pause_suggestion"
    RESOURCE_PROVISION = "resource_provision"
    CRISIS_PROTOCOL = "crisis_protocol"
    EMOTIONAL_VALIDATION = "emotional_validation"
    COPING_STRATEGY = "coping_strategy"


class TriggerCategory(str, Enum):
    """Categories of emotional triggers."""

    TRAUMA_RELATED = "trauma_related"
    ANXIETY_INDUCING = "anxiety_inducing"
    DEPRESSION_TRIGGERING = "depression_triggering"
    ANGER_PROVOKING = "anger_provoking"
    OVERWHELMING_CONTENT = "overwhelming_content"
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    LOSS_GRIEF = "loss_grief"
    IDENTITY_CHALLENGE = "identity_challenge"


@dataclass
class EmotionalStateSnapshot:
    """Snapshot of user's emotional state at a point in time."""

    snapshot_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""

    # Emotional state data
    primary_emotions: dict[EmotionalState, float] = field(default_factory=dict)
    distress_level: DistressLevel = DistressLevel.NONE
    emotional_stability: float = 0.5  # 0.0 = very unstable, 1.0 = very stable

    # Context
    trigger_indicators: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)
    recent_interactions: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0

    def get_dominant_emotion(self) -> tuple[EmotionalState, float]:
        """Get the dominant emotion and its intensity."""
        if not self.primary_emotions:
            return EmotionalState.CALM, 0.0

        dominant = max(self.primary_emotions.items(), key=lambda x: x[1])
        return dominant[0], dominant[1]

    def is_distressed(self) -> bool:
        """Check if user is experiencing significant distress."""
        return self.distress_level >= DistressLevel.MODERATE


@dataclass
class EmotionalTrigger:
    """Detected emotional trigger."""

    trigger_id: str = field(default_factory=lambda: str(uuid4()))
    category: TriggerCategory = TriggerCategory.ANXIETY_INDUCING
    content: str = ""
    intensity: float = 0.0
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)

    # Associated emotional responses
    triggered_emotions: list[EmotionalState] = field(default_factory=list)
    expected_distress_level: DistressLevel = DistressLevel.MILD

    # Mitigation
    suggested_interventions: list[InterventionType] = field(default_factory=list)
    warning_message: str | None = None


@dataclass
class SafetyIntervention:
    """Safety intervention for emotional support."""

    intervention_id: str = field(default_factory=lambda: str(uuid4()))
    intervention_type: InterventionType = InterventionType.EMOTIONAL_VALIDATION

    # Content
    title: str = ""
    description: str = ""
    instructions: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)

    # Targeting
    target_emotions: list[EmotionalState] = field(default_factory=list)
    target_distress_levels: list[DistressLevel] = field(default_factory=list)

    # Effectiveness
    estimated_effectiveness: float = 0.0
    duration_minutes: int = 5

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    used_count: int = 0
    success_rate: float = 0.0


class EmotionalSafetySystem:
    """Main system for emotional safety monitoring and intervention."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

        # Emotional state tracking
        self.emotional_snapshots: dict[str, list[EmotionalStateSnapshot]] = {}
        self.trigger_patterns: dict[str, list[EmotionalTrigger]] = {}

        # Intervention library
        self.interventions = self._load_safety_interventions()
        self.grounding_techniques = self._load_grounding_techniques()
        self.coping_strategies = self._load_coping_strategies()

        # Monitoring configuration
        self.monitoring_enabled = True
        self.intervention_threshold = DistressLevel.MODERATE
        self.snapshot_frequency = timedelta(minutes=2)

        # Metrics
        self.metrics = {
            "emotional_snapshots_created": 0,
            "triggers_detected": 0,
            "interventions_triggered": 0,
            "crisis_protocols_activated": 0,
            "successful_interventions": 0,
        }

    def _load_safety_interventions(
        self,
    ) -> dict[InterventionType, list[SafetyIntervention]]:
        """Load safety intervention library."""
        interventions = {
            InterventionType.GROUNDING_TECHNIQUE: [
                SafetyIntervention(
                    intervention_type=InterventionType.GROUNDING_TECHNIQUE,
                    title="5-4-3-2-1 Grounding Technique",
                    description="A simple grounding exercise to help you feel more present and calm.",
                    instructions=[
                        "Notice 5 things you can see around you",
                        "Notice 4 things you can touch",
                        "Notice 3 things you can hear",
                        "Notice 2 things you can smell",
                        "Notice 1 thing you can taste",
                    ],
                    target_emotions=[
                        EmotionalState.ANXIOUS,
                        EmotionalState.OVERWHELMED,
                    ],
                    target_distress_levels=[DistressLevel.MODERATE, DistressLevel.HIGH],
                    estimated_effectiveness=0.8,
                    duration_minutes=3,
                ),
                SafetyIntervention(
                    intervention_type=InterventionType.GROUNDING_TECHNIQUE,
                    title="Body Scan Grounding",
                    description="Focus on your body to ground yourself in the present moment.",
                    instructions=[
                        "Take a comfortable position",
                        "Start at the top of your head and slowly scan down",
                        "Notice any sensations without trying to change them",
                        "Continue down to your toes",
                        "Take three deep breaths when finished",
                    ],
                    target_emotions=[EmotionalState.ANXIOUS, EmotionalState.FEARFUL],
                    target_distress_levels=[DistressLevel.MILD, DistressLevel.MODERATE],
                    estimated_effectiveness=0.7,
                    duration_minutes=5,
                ),
            ],
            InterventionType.BREATHING_EXERCISE: [
                SafetyIntervention(
                    intervention_type=InterventionType.BREATHING_EXERCISE,
                    title="4-7-8 Breathing",
                    description="A calming breathing technique to reduce anxiety and stress.",
                    instructions=[
                        "Inhale through your nose for 4 counts",
                        "Hold your breath for 7 counts",
                        "Exhale through your mouth for 8 counts",
                        "Repeat 3-4 times",
                    ],
                    target_emotions=[EmotionalState.ANXIOUS, EmotionalState.ANGRY],
                    target_distress_levels=[
                        DistressLevel.MILD,
                        DistressLevel.MODERATE,
                        DistressLevel.HIGH,
                    ],
                    estimated_effectiveness=0.85,
                    duration_minutes=2,
                ),
                SafetyIntervention(
                    intervention_type=InterventionType.BREATHING_EXERCISE,
                    title="Box Breathing",
                    description="A structured breathing pattern to promote calm and focus.",
                    instructions=[
                        "Inhale for 4 counts",
                        "Hold for 4 counts",
                        "Exhale for 4 counts",
                        "Hold empty for 4 counts",
                        "Repeat 4-6 times",
                    ],
                    target_emotions=[
                        EmotionalState.OVERWHELMED,
                        EmotionalState.FRUSTRATED,
                    ],
                    target_distress_levels=[DistressLevel.MODERATE, DistressLevel.HIGH],
                    estimated_effectiveness=0.8,
                    duration_minutes=3,
                ),
            ],
            InterventionType.EMOTIONAL_VALIDATION: [
                SafetyIntervention(
                    intervention_type=InterventionType.EMOTIONAL_VALIDATION,
                    title="Emotional Acknowledgment",
                    description="Validation and normalization of your emotional experience.",
                    instructions=[
                        "Your feelings are valid and understandable",
                        "It's normal to have strong emotions in challenging situations",
                        "You're showing courage by engaging with difficult content",
                        "Take your time - there's no rush to feel differently",
                    ],
                    target_emotions=[EmotionalState.DEPRESSED, EmotionalState.CONFUSED],
                    target_distress_levels=[DistressLevel.MILD, DistressLevel.MODERATE],
                    estimated_effectiveness=0.6,
                    duration_minutes=1,
                )
            ],
            InterventionType.RESOURCE_PROVISION: [
                SafetyIntervention(
                    intervention_type=InterventionType.RESOURCE_PROVISION,
                    title="Support Resources",
                    description="Professional support resources available to you.",
                    resources=[
                        "National Suicide Prevention Lifeline: 988",
                        "Crisis Text Line: Text HOME to 741741",
                        "SAMHSA National Helpline: 1-800-662-4357",
                        "Your local mental health services",
                        "Trusted friends, family, or support network",
                    ],
                    target_distress_levels=[
                        DistressLevel.HIGH,
                        DistressLevel.SEVERE,
                        DistressLevel.CRITICAL,
                    ],
                    estimated_effectiveness=0.9,
                    duration_minutes=0,
                )
            ],
        }

        return interventions

    def _load_grounding_techniques(self) -> list[dict[str, Any]]:
        """Load grounding technique library."""
        return [
            {
                "name": "Progressive Muscle Relaxation",
                "description": "Tense and release muscle groups to reduce physical tension",
                "steps": [
                    "Start with your toes - tense for 5 seconds, then release",
                    "Move up to your calves, thighs, abdomen",
                    "Continue with hands, arms, shoulders, face",
                    "Notice the contrast between tension and relaxation",
                ],
                "duration_minutes": 10,
                "effectiveness": 0.8,
            },
            {
                "name": "Mindful Observation",
                "description": "Focus intently on a single object to anchor your attention",
                "steps": [
                    "Choose an object you can see clearly",
                    "Observe its color, texture, shape, size",
                    "Notice details you hadn't seen before",
                    "If your mind wanders, gently return to the object",
                ],
                "duration_minutes": 3,
                "effectiveness": 0.7,
            },
        ]

    def _load_coping_strategies(self) -> dict[EmotionalState, list[str]]:
        """Load coping strategies for different emotional states."""
        return {
            EmotionalState.ANXIOUS: [
                "Practice deep breathing exercises",
                "Use grounding techniques to stay present",
                "Challenge anxious thoughts with evidence",
                "Engage in gentle physical movement",
                "Listen to calming music or sounds",
            ],
            EmotionalState.DEPRESSED: [
                "Acknowledge your feelings without judgment",
                "Engage in small, manageable activities",
                "Connect with supportive people",
                "Practice self-compassion",
                "Consider professional support if needed",
            ],
            EmotionalState.ANGRY: [
                "Take slow, deep breaths",
                "Count to ten before responding",
                "Express feelings through writing or art",
                "Engage in physical exercise",
                "Practice assertive communication",
            ],
            EmotionalState.OVERWHELMED: [
                "Break tasks into smaller, manageable steps",
                "Prioritize what's most important right now",
                "Take regular breaks",
                "Ask for help when needed",
                "Practice saying no to additional demands",
            ],
        }

    async def monitor_emotional_state(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> EmotionalStateSnapshot:
        """Monitor and analyze user's emotional state."""
        try:
            # Create emotional state snapshot
            snapshot = await self._create_emotional_snapshot(
                session_state, interaction_data
            )

            # Store snapshot
            user_id = session_state.user_id
            if user_id not in self.emotional_snapshots:
                self.emotional_snapshots[user_id] = []

            self.emotional_snapshots[user_id].append(snapshot)

            # Keep only recent snapshots (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.emotional_snapshots[user_id] = [
                s
                for s in self.emotional_snapshots[user_id]
                if s.created_at > cutoff_time
            ]

            # Check for triggers and interventions
            if snapshot.is_distressed():
                await self._handle_emotional_distress(session_state, snapshot)

            # Detect patterns
            await self._analyze_emotional_patterns(session_state, snapshot)

            self.metrics["emotional_snapshots_created"] += 1

            return snapshot

        except Exception as e:
            logger.error(
                f"Failed to monitor emotional state for user {session_state.user_id}: {e}"
            )
            # Return minimal snapshot
            return EmotionalStateSnapshot(
                user_id=session_state.user_id,
                session_id=session_state.session_id,
                distress_level=DistressLevel.NONE,
            )

    async def _create_emotional_snapshot(
        self, session_state: SessionState, interaction_data: dict[str, Any]
    ) -> EmotionalStateSnapshot:
        """Create emotional state snapshot from session data."""
        snapshot = EmotionalStateSnapshot(
            user_id=session_state.user_id, session_id=session_state.session_id
        )

        # Analyze emotional state from session data
        emotional_state = session_state.emotional_state

        # Map session emotional state to our enum
        emotion_mapping = {
            "anxious": EmotionalState.ANXIOUS,
            "calm": EmotionalState.CALM,
            "depressed": EmotionalState.DEPRESSED,
            "angry": EmotionalState.ANGRY,
            "fearful": EmotionalState.FEARFUL,
            "excited": EmotionalState.EXCITED,
            "confused": EmotionalState.CONFUSED,
            "overwhelmed": EmotionalState.OVERWHELMED,
            "hopeful": EmotionalState.HOPEFUL,
            "frustrated": EmotionalState.FRUSTRATED,
        }

        # Convert emotional state
        for emotion_name, intensity in emotional_state.items():
            if emotion_name in emotion_mapping:
                emotion_enum = emotion_mapping[emotion_name]
                snapshot.primary_emotions[emotion_enum] = intensity

        # Calculate distress level
        snapshot.distress_level = self._calculate_distress_level(
            snapshot.primary_emotions
        )

        # Calculate emotional stability
        snapshot.emotional_stability = self._calculate_emotional_stability(
            session_state
        )

        # Analyze interaction data for triggers
        snapshot.trigger_indicators = self._detect_trigger_indicators(interaction_data)

        # Identify protective factors
        snapshot.protective_factors = self._identify_protective_factors(session_state)

        # Store recent interactions
        if "recent_choice" in interaction_data:
            snapshot.recent_interactions.append(interaction_data["recent_choice"])

        # Calculate confidence
        snapshot.confidence = self._calculate_confidence(snapshot)

        return snapshot

    def _calculate_distress_level(
        self, emotions: dict[EmotionalState, float]
    ) -> DistressLevel:
        """Calculate overall distress level from emotional state."""
        if not emotions:
            return DistressLevel.NONE

        # Define distressing emotions and their weights
        distressing_emotions = {
            EmotionalState.ANXIOUS: 1.0,
            EmotionalState.DEPRESSED: 1.0,
            EmotionalState.ANGRY: 0.8,
            EmotionalState.FEARFUL: 1.0,
            EmotionalState.OVERWHELMED: 1.2,
            EmotionalState.FRUSTRATED: 0.6,
        }

        # Calculate weighted distress score
        total_distress = 0.0
        total_weight = 0.0

        for emotion, intensity in emotions.items():
            if emotion in distressing_emotions:
                weight = distressing_emotions[emotion]
                total_distress += intensity * weight
                total_weight += weight

        if total_weight == 0:
            return DistressLevel.NONE

        average_distress = total_distress / total_weight

        # Map to distress levels
        if average_distress >= 0.9:
            return DistressLevel.CRITICAL
        elif average_distress >= 0.7:
            return DistressLevel.SEVERE
        elif average_distress >= 0.5:
            return DistressLevel.HIGH
        elif average_distress >= 0.3:
            return DistressLevel.MODERATE
        elif average_distress >= 0.1:
            return DistressLevel.MILD
        else:
            return DistressLevel.NONE

    def _calculate_emotional_stability(self, session_state: SessionState) -> float:
        """Calculate emotional stability based on recent patterns."""
        user_id = session_state.user_id

        if user_id not in self.emotional_snapshots:
            return 0.5  # Default neutral stability

        recent_snapshots = self.emotional_snapshots[user_id][-10:]  # Last 10 snapshots

        if len(recent_snapshots) < 2:
            return 0.5

        # Calculate variance in distress levels
        distress_levels = [float(s.distress_level) for s in recent_snapshots]
        mean_distress = sum(distress_levels) / len(distress_levels)
        variance = sum((d - mean_distress) ** 2 for d in distress_levels) / len(
            distress_levels
        )

        # Convert variance to stability (lower variance = higher stability)
        stability = max(0.0, min(1.0, 1.0 - (variance / 5.0)))  # Normalize to 0-1

        return stability

    def _detect_trigger_indicators(self, interaction_data: dict[str, Any]) -> list[str]:
        """Detect potential emotional triggers in interaction data."""
        indicators = []

        # Check for trigger keywords in recent content
        if "content" in interaction_data:
            content = interaction_data["content"].lower()

            trigger_keywords = {
                "trauma": ["trauma", "abuse", "violence", "assault", "attack"],
                "loss": ["death", "died", "loss", "grief", "funeral", "goodbye"],
                "anxiety": ["panic", "fear", "scared", "terrified", "worried"],
                "depression": ["hopeless", "worthless", "empty", "numb", "suicide"],
                "anger": ["rage", "fury", "hate", "angry", "mad"],
                "overwhelm": ["too much", "can't handle", "overwhelming", "stressed"],
            }

            for category, keywords in trigger_keywords.items():
                if any(keyword in content for keyword in keywords):
                    indicators.append(f"potential_{category}_trigger")

        # Check for rapid emotional changes
        if "emotional_change" in interaction_data:
            change_magnitude = interaction_data["emotional_change"]
            if change_magnitude > 0.3:  # Significant emotional shift
                indicators.append("rapid_emotional_change")

        return indicators

    def _identify_protective_factors(self, session_state: SessionState) -> list[str]:
        """Identify protective factors in user's current state."""
        factors = []

        # Check therapeutic progress
        progress_metrics = session_state.progress_metrics
        if any(progress > 0.5 for progress in progress_metrics.values()):
            factors.append("therapeutic_progress")

        # Check for positive emotions
        emotional_state = session_state.emotional_state
        positive_emotions = ["calm", "hopeful", "confident", "excited"]
        if any(emotional_state.get(emotion, 0) > 0.5 for emotion in positive_emotions):
            factors.append("positive_emotional_state")

        # Check for coping skills usage
        if "coping_skills_used" in session_state.context:
            factors.append("active_coping")

        # Check for support system engagement
        if "support_system_active" in session_state.context:
            factors.append("social_support")

        return factors

    def _calculate_confidence(self, snapshot: EmotionalStateSnapshot) -> float:
        """Calculate confidence in emotional state assessment."""
        confidence = 0.5  # Base confidence

        # Higher confidence with more emotional data
        if len(snapshot.primary_emotions) > 3:
            confidence += 0.2

        # Higher confidence with clear dominant emotion
        if snapshot.primary_emotions:
            max_intensity = max(snapshot.primary_emotions.values())
            if max_intensity > 0.7:
                confidence += 0.2

        # Lower confidence with conflicting indicators
        if (
            len(snapshot.trigger_indicators) > 0
            and len(snapshot.protective_factors) > 0
        ):
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    async def _handle_emotional_distress(
        self, session_state: SessionState, snapshot: EmotionalStateSnapshot
    ) -> None:
        """Handle detected emotional distress."""
        try:
            # Determine appropriate interventions
            interventions = await self._select_interventions(snapshot)

            # Apply interventions based on distress level
            if snapshot.distress_level >= DistressLevel.CRITICAL:
                await self._activate_crisis_protocol(session_state, snapshot)
            elif snapshot.distress_level >= DistressLevel.HIGH:
                await self._provide_immediate_support(
                    session_state, snapshot, interventions
                )
            elif snapshot.distress_level >= DistressLevel.MODERATE:
                await self._offer_coping_support(session_state, snapshot, interventions)

            # Publish safety event
            await self._publish_safety_event(session_state, snapshot, interventions)

            self.metrics["interventions_triggered"] += 1

        except Exception as e:
            logger.error(
                f"Failed to handle emotional distress for user {session_state.user_id}: {e}"
            )

    async def _select_interventions(
        self, snapshot: EmotionalStateSnapshot
    ) -> list[SafetyIntervention]:
        """Select appropriate interventions for emotional state."""
        selected_interventions = []

        # Get dominant emotion
        dominant_emotion, intensity = snapshot.get_dominant_emotion()

        # Select interventions based on emotion and distress level
        for intervention_type, interventions in self.interventions.items():
            for intervention in interventions:
                # Check if intervention targets the dominant emotion
                if dominant_emotion in intervention.target_emotions:
                    # Check if intervention targets the distress level
                    if snapshot.distress_level in intervention.target_distress_levels:
                        selected_interventions.append(intervention)

        # Sort by estimated effectiveness
        selected_interventions.sort(
            key=lambda x: x.estimated_effectiveness, reverse=True
        )

        # Return top 3 interventions
        return selected_interventions[:3]

    async def _activate_crisis_protocol(
        self, session_state: SessionState, snapshot: EmotionalStateSnapshot
    ) -> None:
        """Activate crisis intervention protocol."""
        logger.warning(f"Crisis protocol activated for user {session_state.user_id}")

        # Provide immediate resources
        crisis_resources = self.interventions[InterventionType.RESOURCE_PROVISION]

        # Store crisis intervention in session
        session_state.context["crisis_intervention_active"] = True
        session_state.context["crisis_intervention_time"] = (
            datetime.utcnow().isoformat()
        )
        session_state.context["crisis_resources_provided"] = [
            resource
            for intervention in crisis_resources
            for resource in intervention.resources
        ]

        # Pause narrative progression
        session_state.context["narrative_paused_for_safety"] = True

        self.metrics["crisis_protocols_activated"] += 1

    async def _provide_immediate_support(
        self,
        session_state: SessionState,
        snapshot: EmotionalStateSnapshot,
        interventions: list[SafetyIntervention],
    ) -> None:
        """Provide immediate emotional support."""
        # Store support interventions in session
        session_state.context["immediate_support_provided"] = True
        session_state.context["support_interventions"] = [
            {
                "type": intervention.intervention_type.value,
                "title": intervention.title,
                "description": intervention.description,
                "instructions": intervention.instructions,
            }
            for intervention in interventions
        ]

        # Suggest content warning for upcoming content
        session_state.context["content_warning_suggested"] = True

    async def _offer_coping_support(
        self,
        session_state: SessionState,
        snapshot: EmotionalStateSnapshot,
        interventions: list[SafetyIntervention],
    ) -> None:
        """Offer coping support and strategies."""
        dominant_emotion, _ = snapshot.get_dominant_emotion()

        # Get coping strategies for dominant emotion
        coping_strategies = self.coping_strategies.get(dominant_emotion, [])

        # Store coping support in session
        session_state.context["coping_support_offered"] = True
        session_state.context["coping_strategies"] = coping_strategies[
            :3
        ]  # Top 3 strategies
        session_state.context["available_interventions"] = [
            {
                "type": intervention.intervention_type.value,
                "title": intervention.title,
                "description": intervention.description,
            }
            for intervention in interventions
        ]

    async def _publish_safety_event(
        self,
        session_state: SessionState,
        snapshot: EmotionalStateSnapshot,
        interventions: list[SafetyIntervention],
    ) -> None:
        """Publish emotional safety event."""
        dominant_emotion, intensity = snapshot.get_dominant_emotion()

        event = create_safety_event(
            EventType.SAFETY_CHECK_TRIGGERED,
            session_state.session_id,
            session_state.user_id,
            safety_level=f"distress_level_{snapshot.distress_level}",
            risk_factors=snapshot.trigger_indicators,
            protective_factors=snapshot.protective_factors,
            intervention_needed=snapshot.distress_level >= DistressLevel.MODERATE,
            data={
                "dominant_emotion": dominant_emotion.value,
                "emotion_intensity": intensity,
                "emotional_stability": snapshot.emotional_stability,
                "interventions_provided": len(interventions),
                "snapshot_id": snapshot.snapshot_id,
            },
        )

        await self.event_bus.publish(event)

    async def _analyze_emotional_patterns(
        self, session_state: SessionState, snapshot: EmotionalStateSnapshot
    ) -> None:
        """Analyze emotional patterns for trend detection."""
        user_id = session_state.user_id

        if user_id not in self.emotional_snapshots:
            return

        recent_snapshots = self.emotional_snapshots[user_id][-5:]  # Last 5 snapshots

        if len(recent_snapshots) < 3:
            return  # Need at least 3 snapshots for pattern analysis

        # Analyze distress level trends
        distress_trend = self._analyze_distress_trend(recent_snapshots)
        if distress_trend == "increasing":
            session_state.context["emotional_pattern_alert"] = "increasing_distress"
        elif distress_trend == "decreasing":
            session_state.context["emotional_pattern_alert"] = "improving_mood"

        # Analyze emotional stability trends
        stability_trend = self._analyze_stability_trend(recent_snapshots)
        if stability_trend == "decreasing":
            session_state.context["stability_alert"] = "decreasing_stability"

    def _analyze_distress_trend(self, snapshots: list[EmotionalStateSnapshot]) -> str:
        """Analyze trend in distress levels."""
        if len(snapshots) < 3:
            return "insufficient_data"

        distress_levels = [float(s.distress_level) for s in snapshots]

        # Simple trend analysis
        recent_avg = sum(distress_levels[-2:]) / 2
        earlier_avg = sum(distress_levels[:-2]) / (len(distress_levels) - 2)

        if recent_avg > earlier_avg + 0.5:
            return "increasing"
        elif recent_avg < earlier_avg - 0.5:
            return "decreasing"
        else:
            return "stable"

    def _analyze_stability_trend(self, snapshots: list[EmotionalStateSnapshot]) -> str:
        """Analyze trend in emotional stability."""
        if len(snapshots) < 3:
            return "insufficient_data"

        stability_levels = [s.emotional_stability for s in snapshots]

        # Simple trend analysis
        recent_avg = sum(stability_levels[-2:]) / 2
        earlier_avg = sum(stability_levels[:-2]) / (len(stability_levels) - 2)

        if recent_avg < earlier_avg - 0.1:
            return "decreasing"
        elif recent_avg > earlier_avg + 0.1:
            return "increasing"
        else:
            return "stable"

    async def detect_triggers(
        self, content: str, context: dict[str, Any]
    ) -> list[EmotionalTrigger]:
        """Detect potential emotional triggers in content."""
        triggers = []

        content_lower = content.lower()

        # Define trigger patterns
        trigger_patterns = {
            TriggerCategory.TRAUMA_RELATED: {
                "keywords": [
                    "trauma",
                    "abuse",
                    "violence",
                    "assault",
                    "attack",
                    "hurt",
                    "pain",
                ],
                "intensity_base": 0.8,
            },
            TriggerCategory.ANXIETY_INDUCING: {
                "keywords": [
                    "panic",
                    "fear",
                    "scared",
                    "terrified",
                    "worried",
                    "anxious",
                    "stress",
                ],
                "intensity_base": 0.6,
            },
            TriggerCategory.DEPRESSION_TRIGGERING: {
                "keywords": [
                    "hopeless",
                    "worthless",
                    "empty",
                    "numb",
                    "suicide",
                    "death",
                    "end",
                ],
                "intensity_base": 0.9,
            },
            TriggerCategory.ANGER_PROVOKING: {
                "keywords": [
                    "rage",
                    "fury",
                    "hate",
                    "angry",
                    "mad",
                    "unfair",
                    "injustice",
                ],
                "intensity_base": 0.5,
            },
            TriggerCategory.OVERWHELMING_CONTENT: {
                "keywords": [
                    "too much",
                    "can't handle",
                    "overwhelming",
                    "stressed",
                    "pressure",
                ],
                "intensity_base": 0.7,
            },
            TriggerCategory.RELATIONSHIP_CONFLICT: {
                "keywords": [
                    "fight",
                    "argument",
                    "conflict",
                    "betrayal",
                    "rejection",
                    "abandoned",
                ],
                "intensity_base": 0.6,
            },
            TriggerCategory.LOSS_GRIEF: {
                "keywords": [
                    "loss",
                    "grief",
                    "died",
                    "death",
                    "funeral",
                    "goodbye",
                    "miss",
                ],
                "intensity_base": 0.8,
            },
        }

        # Check for trigger patterns
        for category, pattern_data in trigger_patterns.items():
            keywords = pattern_data["keywords"]
            intensity_base = pattern_data["intensity_base"]

            matched_keywords = [kw for kw in keywords if kw in content_lower]

            if matched_keywords:
                # Calculate intensity based on number of matches and context
                intensity = min(1.0, intensity_base + (len(matched_keywords) - 1) * 0.1)

                # Determine expected distress level
                if intensity >= 0.8:
                    expected_distress = DistressLevel.HIGH
                elif intensity >= 0.6:
                    expected_distress = DistressLevel.MODERATE
                else:
                    expected_distress = DistressLevel.MILD

                # Create trigger
                trigger = EmotionalTrigger(
                    category=category,
                    content=content,
                    intensity=intensity,
                    confidence=0.7,  # Rule-based detection has moderate confidence
                    expected_distress_level=expected_distress,
                    suggested_interventions=self._get_interventions_for_trigger(
                        category
                    ),
                )

                triggers.append(trigger)
                self.metrics["triggers_detected"] += 1

        return triggers

    def _get_interventions_for_trigger(
        self, category: TriggerCategory
    ) -> list[InterventionType]:
        """Get suggested interventions for trigger category."""
        intervention_mapping = {
            TriggerCategory.TRAUMA_RELATED: [
                InterventionType.GROUNDING_TECHNIQUE,
                InterventionType.BREATHING_EXERCISE,
                InterventionType.RESOURCE_PROVISION,
            ],
            TriggerCategory.ANXIETY_INDUCING: [
                InterventionType.BREATHING_EXERCISE,
                InterventionType.GROUNDING_TECHNIQUE,
                InterventionType.COPING_STRATEGY,
            ],
            TriggerCategory.DEPRESSION_TRIGGERING: [
                InterventionType.EMOTIONAL_VALIDATION,
                InterventionType.RESOURCE_PROVISION,
                InterventionType.COPING_STRATEGY,
            ],
            TriggerCategory.ANGER_PROVOKING: [
                InterventionType.BREATHING_EXERCISE,
                InterventionType.COPING_STRATEGY,
                InterventionType.PAUSE_SUGGESTION,
            ],
            TriggerCategory.OVERWHELMING_CONTENT: [
                InterventionType.GROUNDING_TECHNIQUE,
                InterventionType.PAUSE_SUGGESTION,
                InterventionType.BREATHING_EXERCISE,
            ],
            TriggerCategory.RELATIONSHIP_CONFLICT: [
                InterventionType.EMOTIONAL_VALIDATION,
                InterventionType.COPING_STRATEGY,
                InterventionType.GROUNDING_TECHNIQUE,
            ],
            TriggerCategory.LOSS_GRIEF: [
                InterventionType.EMOTIONAL_VALIDATION,
                InterventionType.RESOURCE_PROVISION,
                InterventionType.COPING_STRATEGY,
            ],
        }

        return intervention_mapping.get(
            category, [InterventionType.EMOTIONAL_VALIDATION]
        )

    async def provide_emotional_regulation_support(
        self, session_state: SessionState, emotion: EmotionalState, intensity: float
    ) -> dict[str, Any]:
        """Provide targeted emotional regulation support."""
        support_response = {
            "emotion": emotion.value,
            "intensity": intensity,
            "support_provided": [],
            "techniques_offered": [],
            "resources": [],
        }

        # Get appropriate interventions
        matching_interventions = []
        for intervention_type, interventions in self.interventions.items():
            for intervention in interventions:
                if emotion in intervention.target_emotions:
                    matching_interventions.append(intervention)

        # Sort by effectiveness
        matching_interventions.sort(
            key=lambda x: x.estimated_effectiveness, reverse=True
        )

        # Provide top interventions
        for intervention in matching_interventions[:2]:
            support_response["support_provided"].append(
                {
                    "type": intervention.intervention_type.value,
                    "title": intervention.title,
                    "description": intervention.description,
                    "instructions": intervention.instructions,
                    "duration_minutes": intervention.duration_minutes,
                }
            )

        # Add coping strategies
        if emotion in self.coping_strategies:
            support_response["techniques_offered"] = self.coping_strategies[emotion][:3]

        # Add grounding techniques for high-intensity emotions
        if intensity > 0.7:
            support_response["grounding_techniques"] = self.grounding_techniques[:2]

        # Store support in session
        session_state.context["emotional_regulation_support"] = support_response

        return support_response

    def get_emotional_history(
        self, user_id: str, hours: int = 24
    ) -> list[EmotionalStateSnapshot]:
        """Get emotional history for a user."""
        if user_id not in self.emotional_snapshots:
            return []

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return [
            snapshot
            for snapshot in self.emotional_snapshots[user_id]
            if snapshot.created_at > cutoff_time
        ]

    def get_trigger_history(
        self, user_id: str, hours: int = 24
    ) -> list[EmotionalTrigger]:
        """Get trigger history for a user."""
        if user_id not in self.trigger_patterns:
            return []

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return [
            trigger
            for trigger in self.trigger_patterns[user_id]
            if trigger.detected_at > cutoff_time
        ]

    def get_metrics(self) -> dict[str, Any]:
        """Get emotional safety system metrics."""
        return {
            **self.metrics,
            "active_users_monitored": len(self.emotional_snapshots),
            "total_snapshots_stored": sum(
                len(snapshots) for snapshots in self.emotional_snapshots.values()
            ),
            "interventions_available": sum(
                len(interventions) for interventions in self.interventions.values()
            ),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of emotional safety system."""
        return {
            "status": "healthy" if self.monitoring_enabled else "disabled",
            "monitoring_enabled": self.monitoring_enabled,
            "intervention_threshold": self.intervention_threshold.value,
            "interventions_loaded": sum(
                len(interventions) for interventions in self.interventions.values()
            ),
            "grounding_techniques_loaded": len(self.grounding_techniques),
            "coping_strategies_loaded": len(self.coping_strategies),
            "metrics": self.get_metrics(),
        }

    def enable_monitoring(self) -> None:
        """Enable emotional state monitoring."""
        self.monitoring_enabled = True
        logger.info("Emotional safety monitoring enabled")

    def disable_monitoring(self) -> None:
        """Disable emotional state monitoring."""
        self.monitoring_enabled = False
        logger.info("Emotional safety monitoring disabled")

    def set_intervention_threshold(self, threshold: DistressLevel) -> None:
        """Set the threshold for automatic interventions."""
        self.intervention_threshold = threshold
        logger.info(f"Intervention threshold set to {threshold.name}")
