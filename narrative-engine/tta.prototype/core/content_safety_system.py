"""
Content Safety System for TTA Living Worlds

This module implements comprehensive content appropriateness and safety systems
for generated timeline events, character histories, and world content. It provides
content validation, safety filtering, player comfort monitoring, and escalation
procedures for content concerns.

Classes:
    ContentSafetySystem: Main system for content validation and safety
    ContentValidator: Validates content against safety guidelines
    SafetyFilter: Filters potentially inappropriate content
    ComfortMonitor: Monitors player comfort and adapts content
    EscalationManager: Handles content concerns and manual review
"""

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


# Define ValidationError at module level for consistent imports
class ValidationError(Exception):
    pass


try:
    from ..models.data_models import EmotionalState, EmotionalStateType
    from ..models.living_worlds_models import TimelineEvent
    from ..models.therapeutic_llm_client import SafetyLevel, TherapeuticContentValidator
except ImportError:
    try:
        from data_models import EmotionalState, EmotionalStateType
        from living_worlds_models import TimelineEvent
        from therapeutic_llm_client import SafetyLevel, TherapeuticContentValidator
    except ImportError:
        # Mock classes for testing
        class SafetyLevel:
            SAFE = "safe"
            CAUTION = "caution"
            UNSAFE = "unsafe"
            CRISIS = "crisis"

        class TherapeuticContentValidator:
            def validate_content(self, content, content_type, context=None):
                return {"safety_level": SafetyLevel.SAFE, "warnings": []}


logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content that can be validated."""

    TIMELINE_EVENT = "timeline_event"
    CHARACTER_HISTORY = "character_history"
    LOCATION_DESCRIPTION = "location_description"
    OBJECT_DESCRIPTION = "object_description"
    DIALOGUE = "dialogue"
    NARRATIVE_TEXT = "narrative_text"


class SafetyRisk(Enum):
    """Types of safety risks in content."""

    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SUBSTANCE_ABUSE = "substance_abuse"
    SEXUAL_CONTENT = "sexual_content"
    HATE_SPEECH = "hate_speech"
    TRAUMA_TRIGGERS = "trauma_triggers"
    CRISIS_INDICATORS = "crisis_indicators"
    INAPPROPRIATE_THERAPEUTIC = "inappropriate_therapeutic"
    HARMFUL_STEREOTYPES = "harmful_stereotypes"
    PRIVACY_VIOLATION = "privacy_violation"


class ComfortLevel(Enum):
    """Player comfort levels."""

    COMFORTABLE = "comfortable"
    SLIGHTLY_UNCOMFORTABLE = "slightly_uncomfortable"
    UNCOMFORTABLE = "uncomfortable"
    VERY_UNCOMFORTABLE = "very_uncomfortable"
    DISTRESSED = "distressed"


@dataclass
class SafetyGuidelines:
    """Configuration for content safety guidelines."""

    max_violence_level: int = 2  # 0-5 scale
    allow_mild_language: bool = True
    therapeutic_content_only: bool = True
    crisis_detection_enabled: bool = True
    trauma_sensitivity_level: int = 3  # 1-5 scale, higher = more sensitive
    age_appropriate_content: bool = True
    cultural_sensitivity_required: bool = True

    def validate(self) -> bool:
        """Validate safety guidelines."""
        if not 0 <= self.max_violence_level <= 5:
            raise ValidationError("Violence level must be between 0 and 5")
        if not 1 <= self.trauma_sensitivity_level <= 5:
            raise ValidationError("Trauma sensitivity level must be between 1 and 5")
        return True


@dataclass
class ContentValidationResult:
    """Result of content validation."""

    is_safe: bool = True
    safety_level: SafetyLevel = SafetyLevel.SAFE
    identified_risks: list[SafetyRisk] = field(default_factory=list)
    risk_scores: dict[SafetyRisk, float] = field(default_factory=dict)  # 0.0-1.0
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    filtered_content: str | None = None
    requires_manual_review: bool = False
    confidence_score: float = 0.8  # 0.0-1.0
    validation_timestamp: datetime = field(default_factory=datetime.now)

    def add_risk(self, risk: SafetyRisk, score: float, warning: str = None) -> None:
        """Add a safety risk to the validation result."""
        self.identified_risks.append(risk)
        self.risk_scores[risk] = score
        if warning:
            self.warnings.append(warning)

        # Update safety level based on highest risk score (check highest first)
        if score >= 0.9:
            self.safety_level = SafetyLevel.CRISIS
            self.is_safe = False
            self.requires_manual_review = True
        elif score >= 0.8:
            self.safety_level = SafetyLevel.UNSAFE
            self.is_safe = False
        elif score >= 0.6:
            self.safety_level = SafetyLevel.CAUTION


@dataclass
class PlayerComfortProfile:
    """Profile tracking player comfort preferences and reactions."""

    player_id: str
    comfort_preferences: dict[str, Any] = field(default_factory=dict)
    trigger_words: set[str] = field(default_factory=set)
    sensitive_topics: set[str] = field(default_factory=set)
    comfort_history: list[dict[str, Any]] = field(default_factory=list)
    adaptive_filters: dict[str, float] = field(
        default_factory=dict
    )  # Topic -> sensitivity level
    last_updated: datetime = field(default_factory=datetime.now)

    def add_comfort_feedback(
        self,
        content_type: str,
        comfort_level: ComfortLevel,
        content_sample: str = "",
        notes: str = "",
    ) -> None:
        """Add comfort feedback from player."""
        feedback = {
            "content_type": content_type,
            "comfort_level": comfort_level.value,
            "content_sample": content_sample[:100],  # Store sample for analysis
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }
        self.comfort_history.append(feedback)
        self.last_updated = datetime.now()

        # Update adaptive filters based on feedback
        if comfort_level in [
            ComfortLevel.UNCOMFORTABLE,
            ComfortLevel.VERY_UNCOMFORTABLE,
            ComfortLevel.DISTRESSED,
        ]:
            current_sensitivity = self.adaptive_filters.get(content_type, 0.5)
            self.adaptive_filters[content_type] = min(1.0, current_sensitivity + 0.1)


@dataclass
class EscalationCase:
    """Case for manual review and escalation."""

    case_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    content_type: ContentType = ContentType.TIMELINE_EVENT
    identified_risks: list[SafetyRisk] = field(default_factory=list)
    player_id: str | None = None
    world_id: str | None = None
    severity_level: int = 1  # 1-5 scale
    status: str = "pending"  # pending, under_review, resolved, escalated
    created_at: datetime = field(default_factory=datetime.now)
    assigned_reviewer: str | None = None
    resolution_notes: str = ""
    resolution_action: str = ""  # approved, rejected, modified, escalated

    def validate(self) -> bool:
        """Validate escalation case."""
        if not self.content.strip():
            raise ValidationError("Content cannot be empty")
        if not 1 <= self.severity_level <= 5:
            raise ValidationError("Severity level must be between 1 and 5")
        return True


class ContentValidator:
    """Validates content against safety guidelines."""

    def __init__(self, guidelines: SafetyGuidelines = None):
        """Initialize content validator."""
        self.guidelines = guidelines or SafetyGuidelines()
        self.therapeutic_validator = TherapeuticContentValidator()
        self._initialize_risk_patterns()
        logger.info("ContentValidator initialized")

    def _initialize_risk_patterns(self) -> None:
        """Initialize patterns for detecting different types of risks."""
        self.risk_patterns = {
            SafetyRisk.VIOLENCE: {
                "keywords": [
                    "kill",
                    "murder",
                    "assault",
                    "attack",
                    "fight",
                    "punch",
                    "kick",
                    "stab",
                    "shoot",
                    "gun",
                    "knife",
                    "weapon",
                    "blood",
                    "injury",
                    "hurt",
                    "pain",
                    "violence",
                    "aggressive",
                    "hostile",
                    "attacked",
                    "killed",
                    "stabbed",
                    "shot",
                ],
                "patterns": [
                    r"\b(kill|murder|assault|attack)\b.*\b(someone|person|people)\b",
                    r"\b(gun|knife|weapon)\b.*\b(use|point|threaten|with)\b",
                    r"\b(blood|injury|wound)\b.*\b(severe|serious|bad)\b",
                    r"\battacked someone with\b",
                    r"\bcaused.*injury\b",
                    r"\bwanted to kill someone\b",
                    r"\bgoing to kill\b",
                    r"\bplan to kill\b",
                ],
                "severity_multipliers": {
                    "graphic": 1.5,
                    "detailed": 1.3,
                    "serious": 1.4,
                    "threatened": 1.2,
                    "implied": 0.8,
                },
            },
            SafetyRisk.SELF_HARM: {
                "keywords": [
                    "self-harm",
                    "cut myself",
                    "hurt myself",
                    "suicide",
                    "kill myself",
                    "end it all",
                    "not worth living",
                    "better off dead",
                    "self-injury",
                    "cutting",
                    "burning",
                    "overdose",
                    "pills",
                    "hurt themselves",
                    "cut themselves",
                    "harm themselves",
                    "kill themselves",
                ],
                "patterns": [
                    r"\b(want to|going to|plan to)\b.*\b(die|kill myself|end it)\b",
                    r"\b(cut|hurt|harm)\b.*\b(myself|themselves)\b",
                    r"\b(suicide|overdose)\b.*\b(plan|method|way)\b",
                    r"\bwanted to\b.*\b(hurt|kill) themselves\b",
                    r"\bcut their\b.*\b(arm|wrist|leg)\b",
                    r"\bkill themselves\b",
                ],
                "severity_multipliers": {
                    "immediate": 2.0,
                    "planned": 1.8,
                    "ideation": 1.5,
                    "historical": 1.0,
                },
            },
            SafetyRisk.SUBSTANCE_ABUSE: {
                "keywords": [
                    "drugs",
                    "alcohol",
                    "drinking",
                    "high",
                    "drunk",
                    "addiction",
                    "overdose",
                    "cocaine",
                    "heroin",
                    "meth",
                    "pills",
                    "prescription abuse",
                ],
                "patterns": [
                    r"\b(using|taking|doing)\b.*\b(drugs|cocaine|heroin)\b",
                    r"\b(drinking|drunk)\b.*\b(problem|too much|addiction)\b",
                    r"\b(overdose|pills)\b.*\b(take|swallow|consume)\b",
                ],
                "severity_multipliers": {
                    "active_use": 1.5,
                    "seeking": 1.3,
                    "recovery": 0.8,
                    "educational": 0.5,
                },
            },
            SafetyRisk.TRAUMA_TRIGGERS: {
                "keywords": [
                    "abuse",
                    "rape",
                    "assault",
                    "trauma",
                    "ptsd",
                    "flashback",
                    "nightmare",
                    "panic",
                    "trigger",
                    "victim",
                    "survivor",
                    "domestic violence",
                    "sexual assault",
                    "child abuse",
                ],
                "patterns": [
                    r"\b(abuse|assault|rape)\b.*\b(victim|survivor|experience)\b",
                    r"\b(flashback|nightmare|panic)\b.*\b(attack|episode)\b",
                    r"\b(trigger|triggered)\b.*\b(memory|feeling|response)\b",
                ],
                "severity_multipliers": {
                    "graphic": 1.8,
                    "personal": 1.5,
                    "therapeutic": 1.0,
                    "educational": 0.7,
                },
            },
            SafetyRisk.CRISIS_INDICATORS: {
                "keywords": [
                    "crisis",
                    "emergency",
                    "help me",
                    "can't cope",
                    "overwhelmed",
                    "breaking down",
                    "losing control",
                    "desperate",
                    "hopeless",
                    "no way out",
                    "can't go on",
                    "feels hopeless",
                    "anymore",
                ],
                "patterns": [
                    r"\b(can't|cannot)\b.*\b(cope|handle|go on)\b",
                    r"\b(help|need)\b.*\b(immediately|now|urgent)\b",
                    r"\b(losing|lost)\b.*\b(control|hope|will)\b",
                    r"\bfeels hopeless\b.*\babout everything\b",
                    r"\bcan't cope anymore\b",
                ],
                "severity_multipliers": {
                    "immediate": 2.0,
                    "escalating": 1.5,
                    "anymore": 1.3,
                    "everything": 1.2,
                    "chronic": 1.2,
                    "managed": 0.8,
                },
            },
            SafetyRisk.INAPPROPRIATE_THERAPEUTIC: {
                "keywords": [
                    "medical advice",
                    "diagnosis",
                    "medication",
                    "prescribe",
                    "cure",
                    "treatment plan",
                    "therapy session",
                    "professional advice",
                ],
                "patterns": [
                    r"\b(you should|must|need to)\b.*\b(take|stop|start)\b.*\b(medication|pills)\b",
                    r"\b(diagnosis|diagnose)\b.*\b(you|yourself)\b",
                    r"\b(professional|medical)\b.*\b(advice|opinion|recommendation)\b",
                ],
                "severity_multipliers": {
                    "medical": 1.8,
                    "diagnostic": 1.5,
                    "prescriptive": 1.3,
                    "suggestive": 1.0,
                },
            },
        }

    def validate_content(
        self,
        content: str,
        content_type: ContentType,
        player_profile: PlayerComfortProfile | None = None,
        context: dict[str, Any] = None,
    ) -> ContentValidationResult:
        """
        Validate content for safety and appropriateness.

        Args:
            content: Content to validate
            content_type: Type of content being validated
            player_profile: Optional player comfort profile
            context: Additional context for validation

        Returns:
            ContentValidationResult: Validation results
        """
        try:
            result = ContentValidationResult()
            content_lower = content.lower()

            # Check each risk type
            for risk_type, risk_config in self.risk_patterns.items():
                risk_score = self._calculate_risk_score(content_lower, risk_config)

                if risk_score > 0.3:  # Threshold for considering a risk
                    warning = (
                        f"Detected {risk_type.value} content (score: {risk_score:.2f})"
                    )
                    result.add_risk(risk_type, risk_score, warning)

            # Apply player-specific filters if profile provided
            if player_profile:
                self._apply_player_filters(result, content, player_profile)

            # Check therapeutic appropriateness
            if self.guidelines.therapeutic_content_only:
                therapeutic_result = self.therapeutic_validator.validate_content(
                    content, "narrative", context
                )
                if therapeutic_result.get("safety_level") == "unsafe":
                    result.add_risk(
                        SafetyRisk.INAPPROPRIATE_THERAPEUTIC,
                        0.8,
                        "Content not therapeutically appropriate",
                    )

            # Determine if manual review is needed
            result.requires_manual_review = result.safety_level in [
                SafetyLevel.UNSAFE,
                SafetyLevel.CRISIS,
            ] or any(score > 0.7 for score in result.risk_scores.values())

            # Generate recommendations
            self._generate_recommendations(result, content_type)

            return result

        except Exception as e:
            logger.error(f"Error validating content: {e}")
            # Return safe default with error
            result = ContentValidationResult()
            result.warnings.append(f"Validation error: {e}")
            result.confidence_score = 0.3
            return result

    def _calculate_risk_score(self, content: str, risk_config: dict[str, Any]) -> float:
        """Calculate risk score for a specific risk type."""
        score = 0.0

        # Check keywords
        keywords = risk_config.get("keywords", [])
        keyword_matches = sum(1 for keyword in keywords if keyword in content)
        if keyword_matches > 0:
            score += min(keyword_matches * 0.2, 0.6)  # Max 0.6 from keywords

        # Check patterns
        patterns = risk_config.get("patterns", [])
        pattern_matches = 0
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_matches += 1

        if pattern_matches > 0:
            score += min(pattern_matches * 0.3, 0.7)  # Max 0.7 from patterns

        # Apply severity multipliers
        multipliers = risk_config.get("severity_multipliers", {})
        for severity_key, multiplier in multipliers.items():
            if severity_key in content:
                score *= multiplier
                break

        return min(score, 1.0)  # Cap at 1.0

    def _apply_player_filters(
        self,
        result: ContentValidationResult,
        content: str,
        player_profile: PlayerComfortProfile,
    ) -> None:
        """Apply player-specific content filters."""
        # Check trigger words
        for trigger_word in player_profile.trigger_words:
            if trigger_word.lower() in content.lower():
                result.add_risk(
                    SafetyRisk.TRAUMA_TRIGGERS,
                    0.8,
                    f"Content contains player trigger word: {trigger_word}",
                )

        # Check sensitive topics
        for topic in player_profile.sensitive_topics:
            if topic.lower() in content.lower():
                sensitivity = player_profile.adaptive_filters.get(topic, 0.5)
                result.add_risk(
                    SafetyRisk.TRAUMA_TRIGGERS,
                    sensitivity,
                    f"Content contains sensitive topic: {topic}",
                )

    def _generate_recommendations(
        self, result: ContentValidationResult, content_type: ContentType
    ) -> None:
        """Generate recommendations based on validation results."""
        if not result.is_safe:
            result.recommendations.append("Content requires modification before use")

            if SafetyRisk.CRISIS_INDICATORS in result.identified_risks:
                result.recommendations.append(
                    "Immediate crisis support protocols should be activated"
                )

            if SafetyRisk.SELF_HARM in result.identified_risks:
                result.recommendations.append(
                    "Content should be reviewed by mental health professional"
                )

            if SafetyRisk.VIOLENCE in result.identified_risks:
                result.recommendations.append(
                    "Consider removing or softening violent content"
                )

            if SafetyRisk.TRAUMA_TRIGGERS in result.identified_risks:
                result.recommendations.append(
                    "Add content warnings or provide alternative content"
                )

        if result.safety_level == SafetyLevel.CAUTION:
            result.recommendations.append("Monitor player response to this content")
            result.recommendations.append("Have support resources readily available")


class SafetyFilter:
    """Filters potentially inappropriate content."""

    def __init__(self, guidelines: SafetyGuidelines = None):
        """Initialize safety filter."""
        self.guidelines = guidelines or SafetyGuidelines()
        self._initialize_filter_rules()
        logger.info("SafetyFilter initialized")

    def _initialize_filter_rules(self) -> None:
        """Initialize content filtering rules."""
        self.filter_rules = {
            "violence_reduction": {
                "replacements": {
                    r"\bkill\b": "stop",
                    r"\bkilled\b": "stopped",
                    r"\bmurder\b": "conflict with",
                    r"\bassault\b": "confront",
                    r"\battack\b": "challenge",
                    r"\battacked\b": "challenged",
                    r"\bstab\b": "poke",
                    r"\bshoot\b": "point at",
                    r"\bblood\b": "red liquid",
                    r"\bweapon\b": "tool",
                    r"\bknife\b": "tool",
                }
            },
            "self_harm_mitigation": {
                "replacements": {
                    r"\bkill myself\b": "feel very sad",
                    r"\bkill themselves\b": "feel very sad",
                    r"\bhurt myself\b": "feel pain",
                    r"\bhurt themselves\b": "feel pain",
                    r"\bcut myself\b": "feel hurt",
                    r"\bcut themselves\b": "feel hurt",
                    r"\bend it all\b": "take a break",
                    r"\bnot worth living\b": "feeling down",
                }
            },
            "substance_softening": {
                "replacements": {
                    r"\bdrugs\b": "substances",
                    r"\baddiction\b": "dependency",
                    r"\boverdose\b": "too much",
                    r"\bdrunk\b": "affected",
                }
            },
            "trauma_sensitivity": {
                "replacements": {
                    r"\babuse\b": "mistreatment",
                    r"\bassault\b": "harmful incident",
                    r"\bvictim\b": "person affected",
                    r"\btrauma\b": "difficult experience",
                }
            },
        }

    def filter_content(
        self, content: str, validation_result: ContentValidationResult
    ) -> str:
        """
        Filter content based on validation results.

        Args:
            content: Original content
            validation_result: Results from content validation

        Returns:
            str: Filtered content
        """
        try:
            filtered_content = content

            # Apply filters based on identified risks
            for risk in validation_result.identified_risks:
                risk_score = validation_result.risk_scores.get(risk, 0.0)

                if risk_score > 0.5:  # Apply filtering for moderate to high risks
                    filtered_content = self._apply_risk_filter(filtered_content, risk)

            # Ensure filtered content maintains meaning and flow
            filtered_content = self._improve_readability(filtered_content)

            return filtered_content

        except Exception as e:
            logger.error(f"Error filtering content: {e}")
            return content  # Return original if filtering fails

    def _apply_risk_filter(self, content: str, risk: SafetyRisk) -> str:
        """Apply specific filter for a risk type."""
        filter_key = {
            SafetyRisk.VIOLENCE: "violence_reduction",
            SafetyRisk.SELF_HARM: "self_harm_mitigation",
            SafetyRisk.SUBSTANCE_ABUSE: "substance_softening",
            SafetyRisk.TRAUMA_TRIGGERS: "trauma_sensitivity",
        }.get(risk)

        if not filter_key or filter_key not in self.filter_rules:
            return content

        filtered_content = content
        replacements = self.filter_rules[filter_key]["replacements"]

        for pattern, replacement in replacements.items():
            filtered_content = re.sub(
                pattern, replacement, filtered_content, flags=re.IGNORECASE
            )

        return filtered_content

    def _improve_readability(self, content: str) -> str:
        """Improve readability of filtered content."""
        # Fix common issues from filtering
        content = re.sub(r"\s+", " ", content)  # Remove extra spaces
        content = re.sub(
            r"([.!?])\s*([a-z])", r"\1 \2", content
        )  # Fix sentence spacing
        content = content.strip()

        return content


class ComfortMonitor:
    """Monitors player comfort and adapts content accordingly."""

    def __init__(self):
        """Initialize comfort monitor."""
        self.player_profiles: dict[str, PlayerComfortProfile] = {}
        self.comfort_thresholds = {
            ComfortLevel.DISTRESSED: 0.0,
            ComfortLevel.VERY_UNCOMFORTABLE: 0.2,
            ComfortLevel.UNCOMFORTABLE: 0.4,
            ComfortLevel.SLIGHTLY_UNCOMFORTABLE: 0.6,
            ComfortLevel.COMFORTABLE: 0.8,
        }
        logger.info("ComfortMonitor initialized")

    def get_player_profile(self, player_id: str) -> PlayerComfortProfile:
        """Get or create player comfort profile."""
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerComfortProfile(player_id=player_id)
        return self.player_profiles[player_id]

    def record_comfort_feedback(
        self,
        player_id: str,
        content_type: str,
        comfort_level: ComfortLevel,
        content_sample: str = "",
        notes: str = "",
    ) -> None:
        """Record player comfort feedback."""
        profile = self.get_player_profile(player_id)
        profile.add_comfort_feedback(content_type, comfort_level, content_sample, notes)

        # Update adaptive filters based on feedback
        self._update_adaptive_filters(profile, content_type, comfort_level)

        logger.info(
            f"Recorded comfort feedback for player {player_id}: {comfort_level.value}"
        )

    def _update_adaptive_filters(
        self,
        profile: PlayerComfortProfile,
        content_type: str,
        comfort_level: ComfortLevel,
    ) -> None:
        """Update adaptive filters based on comfort feedback."""
        current_filter = profile.adaptive_filters.get(content_type, 0.5)

        # Adjust filter based on comfort level
        if comfort_level == ComfortLevel.DISTRESSED:
            profile.adaptive_filters[content_type] = min(1.0, current_filter + 0.3)
        elif comfort_level == ComfortLevel.VERY_UNCOMFORTABLE:
            profile.adaptive_filters[content_type] = min(1.0, current_filter + 0.2)
        elif comfort_level == ComfortLevel.UNCOMFORTABLE:
            profile.adaptive_filters[content_type] = min(1.0, current_filter + 0.1)
        elif comfort_level == ComfortLevel.COMFORTABLE:
            profile.adaptive_filters[content_type] = max(0.0, current_filter - 0.05)

    def assess_content_comfort(
        self, player_id: str, content: str, content_type: ContentType
    ) -> tuple[ComfortLevel, float]:
        """
        Assess likely player comfort level with content.

        Args:
            player_id: Player identifier
            content: Content to assess
            content_type: Type of content

        Returns:
            Tuple[ComfortLevel, float]: Predicted comfort level and confidence
        """
        profile = self.get_player_profile(player_id)

        # Base comfort score
        comfort_score = 0.8  # Start optimistic

        # Check against player's trigger words
        for trigger_word in profile.trigger_words:
            if trigger_word.lower() in content.lower():
                comfort_score -= 0.3

        # Check against sensitive topics
        for topic in profile.sensitive_topics:
            if topic.lower() in content.lower():
                sensitivity = profile.adaptive_filters.get(topic, 0.5)
                comfort_score -= sensitivity * 0.4

        # Apply content type specific adjustments
        type_filter = profile.adaptive_filters.get(content_type.value, 0.5)
        comfort_score -= (type_filter - 0.5) * 0.2

        # Check adaptive filters for content keywords (more intelligent matching)
        for filter_key, sensitivity in profile.adaptive_filters.items():
            # Extract keywords from filter key and check if they appear in content
            filter_keywords = filter_key.replace("_", " ").split()
            for keyword in filter_keywords:
                if keyword.lower() in content.lower() and sensitivity > 0.5:
                    comfort_score -= (sensitivity - 0.5) * 0.3

        # Determine comfort level (find the highest threshold the score meets)
        comfort_level = ComfortLevel.DISTRESSED  # Start with worst case
        for level, threshold in sorted(
            self.comfort_thresholds.items(), key=lambda x: x[1], reverse=True
        ):
            if comfort_score >= threshold:
                comfort_level = level
                break

        confidence = 0.7  # Base confidence in assessment

        # Increase confidence if we have historical data
        relevant_history = [
            entry
            for entry in profile.comfort_history
            if entry["content_type"] == content_type.value
        ]
        if len(relevant_history) > 5:
            confidence = min(0.9, confidence + 0.1)

        return comfort_level, confidence

    def should_adapt_content(
        self, player_id: str, predicted_comfort: ComfortLevel
    ) -> bool:
        """Determine if content should be adapted based on predicted comfort."""
        return predicted_comfort in [
            ComfortLevel.UNCOMFORTABLE,
            ComfortLevel.VERY_UNCOMFORTABLE,
            ComfortLevel.DISTRESSED,
        ]


class EscalationManager:
    """Handles content concerns and manual review procedures."""

    def __init__(self):
        """Initialize escalation manager."""
        self.pending_cases: dict[str, EscalationCase] = {}
        self.escalation_thresholds = {
            SafetyRisk.CRISIS_INDICATORS: 0.6,
            SafetyRisk.SELF_HARM: 0.7,
            SafetyRisk.VIOLENCE: 0.8,
            SafetyRisk.TRAUMA_TRIGGERS: 0.6,
            SafetyRisk.INAPPROPRIATE_THERAPEUTIC: 0.7,
        }
        logger.info("EscalationManager initialized")

    def create_escalation_case(
        self,
        content: str,
        content_type: ContentType,
        validation_result: ContentValidationResult,
        player_id: str = None,
        world_id: str = None,
    ) -> EscalationCase:
        """
        Create an escalation case for manual review.

        Args:
            content: Content requiring review
            content_type: Type of content
            validation_result: Validation results that triggered escalation
            player_id: Optional player identifier
            world_id: Optional world identifier

        Returns:
            EscalationCase: Created escalation case
        """
        try:
            # Determine severity level
            severity_level = self._calculate_severity_level(validation_result)

            case = EscalationCase(
                content=content,
                content_type=content_type,
                identified_risks=validation_result.identified_risks,
                player_id=player_id,
                world_id=world_id,
                severity_level=severity_level,
            )

            case.validate()
            self.pending_cases[case.case_id] = case

            logger.warning(
                f"Escalation case created: {case.case_id} (severity: {severity_level})"
            )
            return case

        except Exception as e:
            logger.error(f"Error creating escalation case: {e}")
            raise ValidationError(f"Failed to create escalation case: {e}") from e

    def _calculate_severity_level(
        self, validation_result: ContentValidationResult
    ) -> int:
        """Calculate severity level for escalation case."""
        max_severity = 1

        for risk, score in validation_result.risk_scores.items():
            threshold = self.escalation_thresholds.get(risk, 0.8)

            if score >= threshold:
                if risk in [SafetyRisk.CRISIS_INDICATORS, SafetyRisk.SELF_HARM]:
                    max_severity = max(max_severity, 5)
                elif risk == SafetyRisk.VIOLENCE:
                    max_severity = max(max_severity, 4)
                elif risk in [
                    SafetyRisk.TRAUMA_TRIGGERS,
                    SafetyRisk.INAPPROPRIATE_THERAPEUTIC,
                ]:
                    max_severity = max(max_severity, 3)
                else:
                    max_severity = max(max_severity, 2)

        return max_severity

    def should_escalate(self, validation_result: ContentValidationResult) -> bool:
        """Determine if content should be escalated for manual review."""
        if validation_result.safety_level == SafetyLevel.CRISIS:
            return True

        for risk, score in validation_result.risk_scores.items():
            threshold = self.escalation_thresholds.get(risk, 0.8)
            if score >= threshold:
                return True

        return validation_result.requires_manual_review

    def get_pending_cases(self, severity_filter: int = None) -> list[EscalationCase]:
        """Get pending escalation cases, optionally filtered by severity."""
        cases = list(self.pending_cases.values())

        if severity_filter is not None:
            cases = [case for case in cases if case.severity_level >= severity_filter]

        # Sort by severity (highest first) then by creation time
        cases.sort(key=lambda x: (-x.severity_level, x.created_at))

        return cases

    def resolve_case(
        self,
        case_id: str,
        resolution_action: str,
        resolution_notes: str = "",
        assigned_reviewer: str = None,
    ) -> bool:
        """
        Resolve an escalation case.

        Args:
            case_id: Case identifier
            resolution_action: Action taken (approved, rejected, modified, escalated)
            resolution_notes: Notes about the resolution
            assigned_reviewer: Who resolved the case

        Returns:
            bool: True if case was resolved successfully
        """
        try:
            if case_id not in self.pending_cases:
                logger.error(f"Escalation case not found: {case_id}")
                return False

            case = self.pending_cases[case_id]
            case.status = "resolved"
            case.resolution_action = resolution_action
            case.resolution_notes = resolution_notes
            case.assigned_reviewer = assigned_reviewer

            # Remove from pending cases
            del self.pending_cases[case_id]

            logger.info(f"Escalation case resolved: {case_id} ({resolution_action})")
            return True

        except Exception as e:
            logger.error(f"Error resolving escalation case {case_id}: {e}")
            return False


class ContentSafetySystem:
    """
    Main system for content validation and safety in TTA Living Worlds.

    This system coordinates content validation, safety filtering, player comfort
    monitoring, and escalation procedures to ensure all generated content is
    appropriate and safe for therapeutic use.
    """

    def __init__(self, guidelines: SafetyGuidelines = None):
        """
        Initialize the content safety system.

        Args:
            guidelines: Safety guidelines configuration
        """
        self.guidelines = guidelines or SafetyGuidelines()
        self.guidelines.validate()

        # Initialize subsystems
        self.validator = ContentValidator(self.guidelines)
        self.filter = SafetyFilter(self.guidelines)
        self.comfort_monitor = ComfortMonitor()
        self.escalation_manager = EscalationManager()

        # Statistics tracking
        self.validation_stats = {
            "total_validations": 0,
            "safe_content": 0,
            "filtered_content": 0,
            "escalated_cases": 0,
            "by_content_type": {},
            "by_risk_type": {},
        }

        logger.info("ContentSafetySystem initialized")

    def validate_timeline_event(
        self, event: "TimelineEvent", player_id: str = None, world_id: str = None
    ) -> ContentValidationResult:
        """
        Validate a timeline event for safety and appropriateness.

        Args:
            event: Timeline event to validate
            player_id: Optional player identifier for personalized validation
            world_id: Optional world identifier for context

        Returns:
            ContentValidationResult: Validation results
        """
        try:
            # Get player comfort profile if available
            player_profile = None
            if player_id:
                player_profile = self.comfort_monitor.get_player_profile(player_id)

            # Prepare context
            context = {
                "event_type": getattr(event, "event_type", "unknown"),
                "participants": getattr(event, "participants", []),
                "world_id": world_id,
                "player_id": player_id,
            }

            # Validate event description
            result = self.validator.validate_content(
                event.description, ContentType.TIMELINE_EVENT, player_profile, context
            )

            # Update statistics
            self._update_stats(ContentType.TIMELINE_EVENT, result)

            return result

        except Exception as e:
            logger.error(f"Error validating timeline event: {e}")
            # Return safe default
            result = ContentValidationResult()
            result.warnings.append(f"Validation error: {e}")
            result.confidence_score = 0.3
            return result

    def validate_character_history(
        self,
        history_text: str,
        character_id: str,
        player_id: str = None,
        world_id: str = None,
    ) -> ContentValidationResult:
        """
        Validate character history content for safety and appropriateness.

        Args:
            history_text: Character history text to validate
            character_id: Character identifier
            player_id: Optional player identifier
            world_id: Optional world identifier

        Returns:
            ContentValidationResult: Validation results
        """
        try:
            # Get player comfort profile if available
            player_profile = None
            if player_id:
                player_profile = self.comfort_monitor.get_player_profile(player_id)

            # Prepare context
            context = {
                "character_id": character_id,
                "world_id": world_id,
                "player_id": player_id,
                "content_purpose": "character_development",
            }

            # Validate history content
            result = self.validator.validate_content(
                history_text, ContentType.CHARACTER_HISTORY, player_profile, context
            )

            # Update statistics
            self._update_stats(ContentType.CHARACTER_HISTORY, result)

            return result

        except Exception as e:
            logger.error(f"Error validating character history: {e}")
            # Return safe default
            result = ContentValidationResult()
            result.warnings.append(f"Validation error: {e}")
            result.confidence_score = 0.3
            return result

    def process_content_safely(
        self,
        content: str,
        content_type: ContentType,
        player_id: str = None,
        world_id: str = None,
    ) -> tuple[str, ContentValidationResult]:
        """
        Process content through the complete safety pipeline.

        Args:
            content: Content to process
            content_type: Type of content
            player_id: Optional player identifier
            world_id: Optional world identifier

        Returns:
            Tuple[str, ContentValidationResult]: (processed_content, validation_result)
        """
        try:
            # Get player comfort profile if available
            player_profile = None
            if player_id:
                player_profile = self.comfort_monitor.get_player_profile(player_id)

            # Validate content
            validation_result = self.validator.validate_content(
                content, content_type, player_profile
            )

            processed_content = content

            # Apply filtering if needed
            if (
                not validation_result.is_safe
                or validation_result.safety_level == SafetyLevel.CAUTION
            ):
                processed_content = self.filter.filter_content(
                    content, validation_result
                )
                validation_result.filtered_content = processed_content
                self.validation_stats["filtered_content"] += 1

            # Check if escalation is needed
            if self.escalation_manager.should_escalate(validation_result):
                escalation_case = self.escalation_manager.create_escalation_case(
                    content, content_type, validation_result, player_id, world_id
                )
                validation_result.warnings.append(
                    f"Content escalated for review: {escalation_case.case_id}"
                )
                self.validation_stats["escalated_cases"] += 1

            # Update statistics
            self._update_stats(content_type, validation_result)

            return processed_content, validation_result

        except Exception as e:
            logger.error(f"Error processing content safely: {e}")
            # Return original content with error result
            result = ContentValidationResult()
            result.warnings.append(f"Processing error: {e}")
            result.confidence_score = 0.3
            return content, result

    def record_player_comfort_feedback(
        self,
        player_id: str,
        content_type: str,
        comfort_level: ComfortLevel,
        content_sample: str = "",
        notes: str = "",
    ) -> None:
        """Record player comfort feedback for adaptive filtering."""
        self.comfort_monitor.record_comfort_feedback(
            player_id, content_type, comfort_level, content_sample, notes
        )

    def get_player_comfort_assessment(
        self, player_id: str, content: str, content_type: ContentType
    ) -> tuple[ComfortLevel, float]:
        """Get predicted player comfort level for content."""
        return self.comfort_monitor.assess_content_comfort(
            player_id, content, content_type
        )

    def get_escalation_cases(self, severity_filter: int = None) -> list[EscalationCase]:
        """Get pending escalation cases."""
        return self.escalation_manager.get_pending_cases(severity_filter)

    def resolve_escalation_case(
        self,
        case_id: str,
        resolution_action: str,
        resolution_notes: str = "",
        assigned_reviewer: str = None,
    ) -> bool:
        """Resolve an escalation case."""
        return self.escalation_manager.resolve_case(
            case_id, resolution_action, resolution_notes, assigned_reviewer
        )

    def get_safety_statistics(self) -> dict[str, Any]:
        """Get content safety statistics."""
        stats = self.validation_stats.copy()

        # Add derived statistics
        if stats["total_validations"] > 0:
            stats["safe_percentage"] = (
                stats["safe_content"] / stats["total_validations"]
            ) * 100
            stats["filtered_percentage"] = (
                stats["filtered_content"] / stats["total_validations"]
            ) * 100
            stats["escalation_percentage"] = (
                stats["escalated_cases"] / stats["total_validations"]
            ) * 100

        # Add pending cases count
        stats["pending_escalations"] = len(self.escalation_manager.pending_cases)

        return stats

    def _update_stats(
        self, content_type: ContentType, result: ContentValidationResult
    ) -> None:
        """Update validation statistics."""
        self.validation_stats["total_validations"] += 1

        if result.is_safe:
            self.validation_stats["safe_content"] += 1

        # Update by content type
        type_key = content_type.value
        if type_key not in self.validation_stats["by_content_type"]:
            self.validation_stats["by_content_type"][type_key] = 0
        self.validation_stats["by_content_type"][type_key] += 1

        # Update by risk type
        for risk in result.identified_risks:
            risk_key = risk.value
            if risk_key not in self.validation_stats["by_risk_type"]:
                self.validation_stats["by_risk_type"][risk_key] = 0
            self.validation_stats["by_risk_type"][risk_key] += 1


# Utility functions for easy integration
def create_safety_system(
    therapeutic_focus: bool = True, trauma_sensitivity: int = 3
) -> ContentSafetySystem:
    """
    Create a content safety system with recommended settings.

    Args:
        therapeutic_focus: Whether to enforce therapeutic content guidelines
        trauma_sensitivity: Trauma sensitivity level (1-5, higher = more sensitive)

    Returns:
        ContentSafetySystem: Configured safety system
    """
    guidelines = SafetyGuidelines(
        therapeutic_content_only=therapeutic_focus,
        trauma_sensitivity_level=trauma_sensitivity,
        crisis_detection_enabled=True,
        cultural_sensitivity_required=True,
    )

    return ContentSafetySystem(guidelines)


def validate_timeline_event_safely(
    event: "TimelineEvent",
    safety_system: ContentSafetySystem,
    player_id: str = None,
    world_id: str = None,
) -> bool:
    """
    Quick validation check for timeline events.

    Args:
        event: Timeline event to validate
        safety_system: Content safety system to use
        player_id: Optional player identifier
        world_id: Optional world identifier

    Returns:
        bool: True if event is safe to use
    """
    try:
        result = safety_system.validate_timeline_event(event, player_id, world_id)
        return result.is_safe and result.safety_level != SafetyLevel.CRISIS
    except Exception as e:
        logger.error(f"Error in quick timeline event validation: {e}")
        return False


if __name__ == "__main__":
    # Example usage and testing
    safety_system = create_safety_system()

    # Test content validation
    test_content = "The character felt overwhelmed and needed support from friends."
    processed_content, result = safety_system.process_content_safely(
        test_content, ContentType.CHARACTER_HISTORY
    )

    print(f"Original: {test_content}")
    print(f"Processed: {processed_content}")
    print(f"Safety Level: {result.safety_level}")
    print(f"Warnings: {result.warnings}")
