"""
Tool validators for naming conventions and description quality (Phase 3 Tool Optimization).

Provides validation for:
- Tool naming convention: {action}_{resource}_{scope?}
- Description quality scoring (1-5 scale)
- Anthropic best practices compliance
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(str, Enum):
    """Severity level for validation findings."""

    ERROR = "error"  # Blocks tool registration
    WARNING = "warning"  # Should be fixed but not blocking
    INFO = "info"  # Informational only


@dataclass
class ValidationFinding:
    """Single validation finding."""

    severity: ValidationSeverity
    message: str
    field: str | None = None
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """Result of validation check."""

    is_valid: bool
    score: float  # 0.0-1.0 for overall quality, or 1-5 for description quality
    findings: list[ValidationFinding] = field(default_factory=list)
    details: dict[str, any] = field(default_factory=dict)


class ToolNameValidator:
    """
    Validates tool names against naming convention.

    Convention: {action}_{resource}_{scope?}
    - action: get, list, create, update, delete, search, query, execute, validate, etc.
    - resource: player, character, world, session, story, agent, workflow, etc.
    - scope: optional qualifier (e.g., active, recent, summary)

    Examples:
        - get_player_profile ✓
        - list_active_sessions ✓
        - create_character ✓
        - update_world_state ✓
        - search_available_worlds ✓
    """

    # Approved actions (can be extended)
    APPROVED_ACTIONS = {
        "get",
        "list",
        "create",
        "update",
        "delete",
        "search",
        "query",
        "execute",
        "validate",
        "start",
        "stop",
        "pause",
        "resume",
        "cancel",
        "retry",
        "check",
        "verify",
        "generate",
        "process",
        "analyze",
        "calculate",
        "compute",
        "fetch",
        "load",
        "save",
        "export",
        "import",
    }

    # Approved resources (can be extended)
    APPROVED_RESOURCES = {
        "player",
        "character",
        "world",
        "session",
        "story",
        "agent",
        "workflow",
        "context",
        "metrics",
        "trace",
        "tool",
        "config",
        "preference",
        "progress",
        "achievement",
        "inventory",
        "quest",
        "dialogue",
        "scene",
        "choice",
        "outcome",
        "state",
        "event",
        "notification",
        "message",
        "log",
        "report",
        "summary",
        "detail",
        "status",
        "health",
        "performance",
    }

    # Pattern: {action}_{resource}_{scope?}
    NAME_PATTERN = re.compile(r"^[a-z]+(_[a-z]+){1,2}$")

    def validate(self, name: str) -> ValidationResult:
        """
        Validate tool name against naming convention.

        Args:
            name: Tool name to validate

        Returns:
            ValidationResult with is_valid, score, and findings

        Example:
            >>> validator = ToolNameValidator()
            >>> result = validator.validate("get_player_profile")
            >>> result.is_valid
            True
        """
        findings: list[ValidationFinding] = []
        score = 1.0  # Start with perfect score

        # Check length
        if len(name) < 3:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message="Tool name too short (minimum 3 characters)",
                    field="name",
                )
            )
            score = 0.0

        if len(name) > 64:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message="Tool name too long (maximum 64 characters)",
                    field="name",
                )
            )
            score = 0.0

        # Check pattern
        if not self.NAME_PATTERN.match(name):
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message="Tool name must match pattern: {action}_{resource}_{scope?}",
                    field="name",
                    suggestion="Use lowercase letters and underscores only, with 2-3 segments",
                )
            )
            score = 0.0

        # Parse segments
        segments = name.split("_")
        if len(segments) < 2:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message="Tool name must have at least 2 segments (action_resource)",
                    field="name",
                )
            )
            score = 0.0
        elif len(segments) > 3:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.WARNING,
                    message="Tool name has more than 3 segments (action_resource_scope recommended)",
                    field="name",
                )
            )
            score *= 0.9

        # Validate action
        if segments:
            action = segments[0]
            if action not in self.APPROVED_ACTIONS:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.WARNING,
                        message=f"Action '{action}' not in approved list",
                        field="name",
                        suggestion=f"Consider using: {', '.join(sorted(list(self.APPROVED_ACTIONS)[:10]))}...",
                    )
                )
                score *= 0.8

        # Validate resource
        if len(segments) >= 2:
            resource = segments[1]
            if resource not in self.APPROVED_RESOURCES:
                findings.append(
                    ValidationFinding(
                        severity=ValidationSeverity.INFO,
                        message=f"Resource '{resource}' not in approved list (may be valid domain-specific term)",
                        field="name",
                    )
                )
                score *= 0.95

        is_valid = score > 0.0 and not any(
            f.severity == ValidationSeverity.ERROR for f in findings
        )

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            findings=findings,
            details={"segments": segments, "action": segments[0] if segments else None},
        )


class ToolDescriptionValidator:
    """
    Validates tool description quality.

    Scores descriptions on 1-5 scale based on:
    - Clarity (clear, unambiguous language)
    - Completeness (what, why, when to use)
    - Specificity (concrete examples, not vague)
    - Structure (well-organized, scannable)
    - Length (not too short, not too long)

    Scoring:
    - 5: Excellent - Clear, complete, specific, well-structured
    - 4: Good - Minor improvements needed
    - 3: Adequate - Meets minimum requirements
    - 2: Poor - Significant issues
    - 1: Very Poor - Major rewrite needed
    """

    MIN_LENGTH = 20  # Minimum description length
    MAX_LENGTH = 2048  # Maximum description length
    IDEAL_MIN_LENGTH = 50  # Ideal minimum for good descriptions
    IDEAL_MAX_LENGTH = 500  # Ideal maximum for concise descriptions

    def validate(self, description: str) -> ValidationResult:
        """
        Validate description quality and assign 1-5 score.

        Args:
            description: Tool description to validate

        Returns:
            ValidationResult with score (1-5) and findings

        Example:
            >>> validator = ToolDescriptionValidator()
            >>> result = validator.validate("Retrieves player profile data including preferences and progress.")
            >>> result.score >= 3.0
            True
        """
        findings: list[ValidationFinding] = []
        score = 5.0  # Start with perfect score

        # Check length
        desc_len = len(description)

        if desc_len < self.MIN_LENGTH:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message=f"Description too short ({desc_len} chars, minimum {self.MIN_LENGTH})",
                    field="description",
                )
            )
            score = 1.0

        if desc_len > self.MAX_LENGTH:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.ERROR,
                    message=f"Description too long ({desc_len} chars, maximum {self.MAX_LENGTH})",
                    field="description",
                )
            )
            score = 1.0

        # Ideal length range
        if desc_len < self.IDEAL_MIN_LENGTH:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.WARNING,
                    message=f"Description could be more detailed ({desc_len} chars, ideal minimum {self.IDEAL_MIN_LENGTH})",
                    field="description",
                    suggestion="Add more context about what the tool does and when to use it",
                )
            )
            score -= 1.0

        if desc_len > self.IDEAL_MAX_LENGTH:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.INFO,
                    message=f"Description is verbose ({desc_len} chars, ideal maximum {self.IDEAL_MAX_LENGTH})",
                    field="description",
                    suggestion="Consider making description more concise",
                )
            )
            score -= 0.5

        # Check for vague language
        vague_terms = ["thing", "stuff", "something", "various", "etc", "and so on"]
        found_vague = [term for term in vague_terms if term in description.lower()]
        if found_vague:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.WARNING,
                    message=f"Description contains vague terms: {', '.join(found_vague)}",
                    field="description",
                    suggestion="Use specific, concrete language",
                )
            )
            score -= 0.5

        # Check for action verbs (good descriptions start with verbs)
        first_word = description.split()[0].lower() if description.split() else ""
        action_verbs = {
            "retrieves",
            "fetches",
            "gets",
            "lists",
            "creates",
            "updates",
            "deletes",
            "searches",
            "queries",
            "executes",
            "validates",
            "generates",
            "processes",
            "analyzes",
            "calculates",
            "computes",
        }
        if first_word not in action_verbs:
            findings.append(
                ValidationFinding(
                    severity=ValidationSeverity.INFO,
                    message="Description should start with an action verb",
                    field="description",
                    suggestion=f"Consider starting with: {', '.join(list(action_verbs)[:5])}...",
                )
            )
            score -= 0.3

        # Ensure score is in 1-5 range
        score = max(1.0, min(5.0, score))

        is_valid = score >= 3.0  # Minimum acceptable score

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            findings=findings,
            details={"length": desc_len, "first_word": first_word},
        )

