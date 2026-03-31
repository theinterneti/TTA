"""Tests for safety validation enums."""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Safety_validation/Test_enums]]

from src.agent_orchestration.safety_validation.enums import SafetyLevel, ValidationType


class TestSafetyLevel:
    """Test SafetyLevel enum."""

    def test_safety_level_values(self) -> None:
        """Test SafetyLevel enum has correct values."""
        assert SafetyLevel.SAFE.value == "safe"
        assert SafetyLevel.WARNING.value == "warning"
        assert SafetyLevel.BLOCKED.value == "blocked"

    def test_safety_level_is_string(self) -> None:
        """Test SafetyLevel enum values are strings."""
        assert isinstance(SafetyLevel.SAFE, str)
        assert isinstance(SafetyLevel.WARNING, str)
        assert isinstance(SafetyLevel.BLOCKED, str)


class TestValidationType:
    """Test ValidationType enum."""

    def test_validation_type_values(self) -> None:
        """Test ValidationType enum has correct values."""
        assert ValidationType.KEYWORD.value == "keyword"
        assert ValidationType.SENTIMENT.value == "sentiment"
        assert ValidationType.CONTEXT_AWARE.value == "context_aware"
        assert ValidationType.CRISIS_DETECTION.value == "crisis_detection"
        assert ValidationType.THERAPEUTIC_BOUNDARY.value == "therapeutic_boundary"

    def test_validation_type_is_string(self) -> None:
        """Test ValidationType enum values are strings."""
        assert isinstance(ValidationType.KEYWORD, str)
        assert isinstance(ValidationType.SENTIMENT, str)
