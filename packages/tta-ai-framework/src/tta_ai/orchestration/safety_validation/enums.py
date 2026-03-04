"""Safety validation enumerations."""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Safety_validation/Enums]]

from enum import StrEnum


class SafetyLevel(StrEnum):
    """Safety level for content validation."""

    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class ValidationType(StrEnum):
    """Types of validation algorithms available."""

    KEYWORD = "keyword"
    SENTIMENT = "sentiment"
    CONTEXT_AWARE = "context_aware"
    CRISIS_DETECTION = "crisis_detection"
    THERAPEUTIC_BOUNDARY = "therapeutic_boundary"
