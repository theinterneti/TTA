"""Data models for unit test generation using OpenHands.

This module provides Pydantic models for specifying test generation tasks,
validating test results, and classifying errors during the test generation process.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Test_generation_models]]

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class TestTaskSpecification(BaseModel):
    """Specification for a unit test generation task.

    This model defines all parameters needed to generate unit tests for a target file,
    including coverage requirements, testing conventions, and execution constraints.

    Attributes:
        target_file: Path to the file for which to generate tests (relative to workspace root)
        coverage_threshold: Minimum coverage percentage required (default: 70.0)
        test_framework: Test framework to use (default: "pytest")
        test_directory: Directory to place generated tests (default: Path("tests"))
        context_files: Additional context files to provide to OpenHands
        conventions: TTA-specific testing conventions (e.g., {'command': 'uv run pytest'})
        timeout_seconds: Maximum time allowed for test generation (default: 600.0)

    Example:
        >>> spec = TestTaskSpecification(
        ...     target_file=Path("src/agent_orchestration/tools/client.py"),
        ...     coverage_threshold=80.0,
        ...     timeout_seconds=900.0,
        ... )
    """

    target_file: Path = Field(
        description="Path to file for which to generate tests (relative to workspace root)"
    )
    coverage_threshold: float = Field(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Minimum coverage percentage required (0-100)",
    )
    test_framework: str = Field(
        default="pytest", description="Test framework to use (default: pytest)"
    )
    test_directory: Path = Field(
        default=Path("tests"),
        description="Directory to place generated tests (default: tests/)",
    )
    context_files: list[Path] = Field(
        default_factory=list,
        description="Additional context files to provide to OpenHands",
    )
    conventions: dict[str, str] = Field(
        default_factory=dict,
        description="TTA-specific testing conventions (e.g., {'command': 'uv run pytest'})",
    )
    timeout_seconds: float = Field(
        default=600.0,
        gt=0.0,
        description="Maximum time allowed for test generation in seconds (default: 600)",
    )

    class Config:
        """Pydantic configuration."""

        frozen = False  # Allow modification for retry logic


class TestValidationResult(BaseModel):
    """Result of test validation.

    This model aggregates the results of various validation checks performed on
    generated tests, including syntax validation, coverage verification, test
    execution, and convention compliance.

    Attributes:
        syntax_valid: Whether the generated tests have valid Python syntax
        coverage_percentage: Actual coverage percentage achieved (0-100)
        tests_pass: Whether all generated tests pass when executed
        conventions_followed: Whether tests follow TTA conventions
        issues: List of validation issues encountered
        quality_score: Overall quality score (0-100) based on test characteristics
        test_file_path: Path to the generated test file (if successful)

    Example:
        >>> result = TestValidationResult(
        ...     syntax_valid=True,
        ...     coverage_percentage=85.5,
        ...     tests_pass=True,
        ...     conventions_followed=True,
        ...     issues=[],
        ...     quality_score=92.0,
        ... )
    """

    syntax_valid: bool = Field(
        description="Whether the generated tests have valid Python syntax"
    )
    coverage_percentage: float = Field(
        ge=0.0, le=100.0, description="Actual coverage percentage achieved (0-100)"
    )
    tests_pass: bool = Field(
        description="Whether all generated tests pass when executed"
    )
    conventions_followed: bool = Field(
        description="Whether tests follow TTA conventions"
    )
    issues: list[str] = Field(
        default_factory=list, description="List of validation issues encountered"
    )
    quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall quality score (0-100) based on test characteristics",
    )
    test_file_path: Path | None = Field(
        default=None, description="Path to the generated test file (if successful)"
    )

    class Config:
        """Pydantic configuration."""

        frozen = False  # Allow modification during validation


class TestGenerationError(str, Enum):
    """Error types that can occur during test generation.

    This enum classifies different types of errors that may occur during the
    test generation process, enabling targeted error handling and retry strategies.

    Values:
        INSUFFICIENT_CONTEXT: OpenHands lacks sufficient context to generate tests
        PARTIAL_GENERATION: Some tests generated but incomplete or failing
        COVERAGE_GAP: Tests generated but coverage below threshold
        SYNTAX_ERROR: Generated tests have Python syntax errors
        TIMEOUT: Test generation exceeded time limit
        EXECUTION_FAILURE: Tests generated but fail when executed

    Example:
        >>> error_type = TestGenerationError.COVERAGE_GAP
        >>> print(f"Error: {error_type.value}")
        Error: coverage_gap
    """

    INSUFFICIENT_CONTEXT = "insufficient_context"
    PARTIAL_GENERATION = "partial_generation"
    COVERAGE_GAP = "coverage_gap"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
    EXECUTION_FAILURE = "execution_failure"
