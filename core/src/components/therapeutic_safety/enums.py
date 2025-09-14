"""
Enums for Therapeutic Safety Content Validation

This module defines all enumeration types used throughout the therapeutic
safety validation system.
"""

from enum import Enum, IntEnum


class CrisisLevel(IntEnum):
    """Crisis severity levels for content assessment."""

    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    SEVERE = 4
    CRITICAL = 5


class BiasType(str, Enum):
    """Types of bias that can be detected in content."""

    GENDER = "gender"
    RACIAL = "racial"
    CULTURAL = "cultural"
    RELIGIOUS = "religious"
    SOCIOECONOMIC = "socioeconomic"
    AGE = "age"
    DISABILITY = "disability"
    SEXUAL_ORIENTATION = "sexual_orientation"
    POLITICAL = "political"
    THERAPEUTIC = "therapeutic"


class ContentType(str, Enum):
    """Types of content that can be validated."""

    NARRATIVE_SCENE = "narrative_scene"
    USER_CHOICE = "user_choice"
    CONSEQUENCE = "consequence"
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"
    SYSTEM_MESSAGE = "system_message"
    USER_INPUT = "user_input"
    GENERATED_CONTENT = "generated_content"
    EDUCATIONAL_CONTENT = "educational_content"


class ValidationAction(str, Enum):
    """Actions that can be taken based on validation results."""

    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    FLAG_FOR_REVIEW = "flag_for_review"
    REQUIRE_CONFIRMATION = "require_confirmation"
    ESCALATE = "escalate"
    BLOCK = "block"
    WARN = "warn"


class SafetyLevel(str, Enum):
    """Overall safety levels for content and users."""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class TherapeuticFramework(str, Enum):
    """Therapeutic frameworks for content alignment."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    ACT = "acceptance_commitment_therapy"
    MINDFULNESS = "mindfulness_based"
    TRAUMA_INFORMED = "trauma_informed"
    HUMANISTIC = "humanistic"
    PSYCHODYNAMIC = "psychodynamic"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE_THERAPY = "narrative_therapy"
    FAMILY_SYSTEMS = "family_systems"


class ValidationStatus(str, Enum):
    """Status of validation process."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RETRY_NEEDED = "retry_needed"


class RiskCategory(str, Enum):
    """Categories of risk in therapeutic content."""

    SELF_HARM = "self_harm"
    SUICIDE = "suicide"
    VIOLENCE = "violence"
    SUBSTANCE_ABUSE = "substance_abuse"
    EATING_DISORDER = "eating_disorder"
    TRAUMA_TRIGGER = "trauma_trigger"
    PANIC_TRIGGER = "panic_trigger"
    DEPRESSION_TRIGGER = "depression_trigger"
    ANXIETY_TRIGGER = "anxiety_trigger"
    INAPPROPRIATE_CONTENT = "inappropriate_content"


class ProtectiveFactor(str, Enum):
    """Protective factors that can mitigate risks."""

    SOCIAL_SUPPORT = "social_support"
    COPING_SKILLS = "coping_skills"
    PROFESSIONAL_HELP = "professional_help"
    SAFETY_PLAN = "safety_plan"
    CRISIS_RESOURCES = "crisis_resources"
    THERAPEUTIC_RELATIONSHIP = "therapeutic_relationship"
    MINDFULNESS_PRACTICE = "mindfulness_practice"
    GROUNDING_TECHNIQUES = "grounding_techniques"
    POSITIVE_ACTIVITIES = "positive_activities"
    MEANING_PURPOSE = "meaning_purpose"


class ValidationPriority(IntEnum):
    """Priority levels for validation processing."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class ContentSource(str, Enum):
    """Source of content being validated."""

    USER_GENERATED = "user_generated"
    AI_GENERATED = "ai_generated"
    TEMPLATE_BASED = "template_based"
    CURATED = "curated"
    SYSTEM_GENERATED = "system_generated"
    EXTERNAL_API = "external_api"


class ValidationScope(str, Enum):
    """Scope of validation to be performed."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CRISIS_FOCUSED = "crisis_focused"
    THERAPEUTIC_FOCUSED = "therapeutic_focused"


class AgeGroup(str, Enum):
    """Age groups for content appropriateness."""

    CHILD = "child"  # Under 13
    TEEN = "teen"  # 13-17
    YOUNG_ADULT = "young_adult"  # 18-25
    ADULT = "adult"  # 26-64
    SENIOR = "senior"  # 65+


class MaturityLevel(IntEnum):
    """Content maturity levels."""

    ALL_AGES = 0
    TEEN = 1
    MATURE_TEEN = 2
    ADULT = 3
    MATURE_ADULT = 4


class TherapeuticGoalCategory(str, Enum):
    """Categories of therapeutic goals."""

    ANXIETY_MANAGEMENT = "anxiety_management"
    DEPRESSION_SUPPORT = "depression_support"
    TRAUMA_RECOVERY = "trauma_recovery"
    ADDICTION_RECOVERY = "addiction_recovery"
    RELATIONSHIP_SKILLS = "relationship_skills"
    EMOTIONAL_REGULATION = "emotional_regulation"
    STRESS_MANAGEMENT = "stress_management"
    SELF_ESTEEM = "self_esteem"
    GRIEF_PROCESSING = "grief_processing"
    ANGER_MANAGEMENT = "anger_management"
    SOCIAL_SKILLS = "social_skills"
    COMMUNICATION_SKILLS = "communication_skills"
    MINDFULNESS = "mindfulness"
    BEHAVIORAL_CHANGE = "behavioral_change"
    COGNITIVE_RESTRUCTURING = "cognitive_restructuring"


class InterventionType(str, Enum):
    """Types of therapeutic interventions."""

    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    PREVENTIVE = "preventive"
    CRISIS = "crisis"
    EDUCATIONAL = "educational"
    SUPPORTIVE = "supportive"
    CORRECTIVE = "corrective"


class ValidationComponent(str, Enum):
    """Components involved in validation pipeline."""

    CONTENT_SAFETY = "content_safety"
    CRISIS_DETECTION = "crisis_detection"
    BIAS_DETECTION = "bias_detection"
    THERAPEUTIC_ALIGNMENT = "therapeutic_alignment"
    AGE_APPROPRIATENESS = "age_appropriateness"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    EVIDENCE_BASED = "evidence_based"
