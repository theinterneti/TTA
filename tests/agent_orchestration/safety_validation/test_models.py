"""Tests for safety validation models."""

from src.agent_orchestration.safety_validation.enums import SafetyLevel, ValidationType
from src.agent_orchestration.safety_validation.models import (
    SafetyRule,
    ValidationFinding,
    ValidationResult,
)


class TestValidationFinding:
    """Test ValidationFinding dataclass."""

    def test_create_basic_finding(self) -> None:
        """Test creating a basic validation finding."""
        finding = ValidationFinding(
            rule_id="test_rule",
            category="test_category",
            level=SafetyLevel.WARNING,
            priority=50,
        )
        assert finding.rule_id == "test_rule"
        assert finding.category == "test_category"
        assert finding.level == SafetyLevel.WARNING
        assert finding.priority == 50
        assert finding.validation_type == ValidationType.KEYWORD  # default


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_create_basic_result(self) -> None:
        """Test creating a basic validation result."""
        result = ValidationResult(level=SafetyLevel.SAFE)
        assert result.level == SafetyLevel.SAFE
        assert result.score == 1.0
        assert result.findings == []

    def test_to_dict(self) -> None:
        """Test converting validation result to dictionary."""
        result = ValidationResult(level=SafetyLevel.SAFE, score=0.9)
        result_dict = result.to_dict()
        assert result_dict["level"] == "safe"
        assert result_dict["score"] == 0.9
        assert isinstance(result_dict["findings"], list)


class TestSafetyRule:
    """Test SafetyRule dataclass."""

    def test_create_basic_rule(self) -> None:
        """Test creating a basic safety rule."""
        rule = SafetyRule(
            id="test_rule",
            category="test",
            priority=50,
            level=SafetyLevel.WARNING,
            pattern=r"test",
        )
        assert rule.id == "test_rule"
        assert rule.pattern == r"test"

    def test_compile_pattern(self) -> None:
        """Test compiling a regex pattern."""
        rule = SafetyRule(
            id="test_rule",
            category="test",
            priority=50,
            level=SafetyLevel.WARNING,
            pattern=r"test",
            flags="i",
        )
        compiled = rule.compile()
        assert compiled is not None
        assert compiled.match("TEST") is not None  # case insensitive
