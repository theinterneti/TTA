"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Result_validator]]
Result validator for OpenHands task outputs.

Provides:
- ResultValidator: Validates task results
- ValidationRule: Validation rule definition
- ValidationResult: Validation result with details
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ValidationLevel(StrEnum):
    """Validation severity levels."""

    ERROR = "error"  # Must pass
    WARNING = "warning"  # Should pass
    INFO = "info"  # Nice to have


@dataclass
class ValidationRule:
    """Validation rule definition."""

    name: str
    description: str
    validator: Callable[[Any], bool]
    level: ValidationLevel = ValidationLevel.ERROR
    error_message: str = ""


@dataclass
class ValidationResult:
    """Validation result with details."""

    passed: bool
    errors: list[str]
    warnings: list[str]
    details: dict[str, Any]
    score: float  # 0-1 scale


class ResultValidator:
    """Validates OpenHands task results."""

    def __init__(self):
        """Initialize result validator."""
        self.rules: dict[str, ValidationRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default validation rules."""
        # File existence rule
        self.register_rule(
            ValidationRule(
                name="file_exists",
                description="Output file exists",
                validator=lambda result: (
                    "output_file" in result and Path(result["output_file"]).exists()
                ),
                level=ValidationLevel.ERROR,
                error_message="Output file does not exist",
            )
        )

        # Content not empty rule
        self.register_rule(
            ValidationRule(
                name="content_not_empty",
                description="Output content is not empty",
                validator=lambda result: (
                    "content" in result and len(result["content"]) > 0
                ),
                level=ValidationLevel.ERROR,
                error_message="Output content is empty",
            )
        )

        # Valid Python syntax rule
        self.register_rule(
            ValidationRule(
                name="valid_python",
                description="Output is valid Python",
                validator=self._validate_python_syntax,
                level=ValidationLevel.ERROR,
                error_message="Output contains invalid Python syntax",
            )
        )

        # Test file naming rule
        self.register_rule(
            ValidationRule(
                name="test_naming",
                description="Test file follows naming convention",
                validator=self._validate_test_naming,
                level=ValidationLevel.WARNING,
                error_message="Test file does not follow naming convention",
            )
        )

    def register_rule(self, rule: ValidationRule) -> None:
        """Register validation rule.

        Args:
            rule: Validation rule
        """
        self.rules[rule.name] = rule
        logger.debug(f"Registered validation rule: {rule.name}")

    def validate(self, result: dict[str, Any]) -> ValidationResult:
        """Validate task result.

        Args:
            result: Task result to validate

        Returns:
            Validation result
        """
        errors = []
        warnings = []
        details = {}

        for rule_name, rule in self.rules.items():
            try:
                passed = rule.validator(result)
                details[rule_name] = {"passed": passed, "message": rule.description}

                if not passed:
                    message = rule.error_message or f"Rule '{rule_name}' failed"
                    if rule.level == ValidationLevel.ERROR:
                        errors.append(message)
                    elif rule.level == ValidationLevel.WARNING:
                        warnings.append(message)

            except Exception as e:
                logger.error(f"Error validating rule {rule_name}: {e}")
                details[rule_name] = {"passed": False, "error": str(e)}
                if rule.level == ValidationLevel.ERROR:
                    errors.append(f"Validation error in {rule_name}: {e}")

        # Calculate score
        total_rules = len(self.rules)
        passed_rules = sum(1 for d in details.values() if d.get("passed", False))
        score = passed_rules / total_rules if total_rules > 0 else 0.0

        passed = len(errors) == 0

        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            details=details,
            score=score,
        )

    def _validate_python_syntax(self, result: dict[str, Any]) -> bool:
        """Validate Python syntax.

        Args:
            result: Task result

        Returns:
            True if valid Python syntax
        """
        if "content" not in result:
            return False

        try:
            compile(result["content"], "<string>", "exec")
            return True
        except SyntaxError:
            return False

    def _validate_test_naming(self, result: dict[str, Any]) -> bool:
        """Validate test file naming convention.

        Args:
            result: Task result

        Returns:
            True if follows naming convention
        """
        if "output_file" not in result:
            return False

        filename = Path(result["output_file"]).name
        # Check if filename starts with test_ or ends with _test.py
        return filename.startswith("test_") or filename.endswith("_test.py")

    def validate_coverage(
        self, result: dict[str, Any], min_coverage: float = 0.7
    ) -> bool:
        """Validate test coverage.

        Args:
            result: Task result
            min_coverage: Minimum coverage threshold (0-1)

        Returns:
            True if coverage meets threshold
        """
        if "coverage" not in result:
            return False

        coverage = result["coverage"]
        if isinstance(coverage, str):
            # Parse percentage string
            match = re.search(r"(\d+(?:\.\d+)?)", coverage)
            if match:
                coverage = float(match.group(1)) / 100
            else:
                return False

        return coverage >= min_coverage

    def validate_execution(self, result: dict[str, Any]) -> bool:
        """Validate test execution.

        Args:
            result: Task result

        Returns:
            True if tests executed successfully
        """
        if "execution_result" not in result:
            return False

        exec_result = result["execution_result"]
        if isinstance(exec_result, dict):
            return exec_result.get("passed", False)

        return str(exec_result).lower() in ["passed", "success", "true"]
