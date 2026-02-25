"""Error handler for test generation with retry logic.

This module provides functions to handle test generation errors and implement
retry strategies based on error classification.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Test_error_handler]]

import logging
import re
from pathlib import Path

from ..openhands_integration.models import OpenHandsTaskResult
from .test_generation_models import TestGenerationError, TestTaskSpecification

logger = logging.getLogger(__name__)


def classify_error(result: OpenHandsTaskResult) -> TestGenerationError:  # noqa: PLR0911
    """Classify error from OpenHands task result.

    Analyzes error message and output to determine error type.

    Args:
        result: OpenHands task result with error

    Returns:
        TestGenerationError enum value

    Example:
        >>> result = OpenHandsTaskResult(success=False, error="Timeout after 600s")
        >>> error_type = classify_error(result)
        >>> print(error_type)
        TestGenerationError.TIMEOUT
    """
    error_msg = (result.error or "").lower()
    output = (result.output or "").lower()
    combined = f"{error_msg} {output}"

    # Rate limit errors (429, rate-limited, rate limiting)
    if (
        "429" in combined
        or "rate limit" in combined
        or "rate-limited" in combined
        or "rate limiting" in combined
        or "temporarily rate-limited" in combined
    ):
        logger.warning(f"Rate limit error detected: {error_msg[:100]}")
        return TestGenerationError.EXECUTION_FAILURE  # Will trigger model fallback

    # Timeout errors
    if "timeout" in combined or "timed out" in combined:
        return TestGenerationError.TIMEOUT

    # Syntax errors
    if "syntaxerror" in combined or "invalid syntax" in combined:
        return TestGenerationError.SYNTAX_ERROR

    # Coverage gaps
    if "coverage" in combined and ("below" in combined or "insufficient" in combined):
        return TestGenerationError.COVERAGE_GAP

    # Execution failures
    if "failed" in combined or "error" in combined or "exception" in combined:
        return TestGenerationError.EXECUTION_FAILURE

    # Partial generation
    if "partial" in combined or "incomplete" in combined:
        return TestGenerationError.PARTIAL_GENERATION

    # Default to insufficient context
    return TestGenerationError.INSUFFICIENT_CONTEXT


def discover_related_files(target_file: Path, workspace_path: Path) -> list[Path]:
    """Discover related files (imports, dependencies) for context.

    Analyzes target file to find imported modules and related files.

    Args:
        target_file: Path to target file
        workspace_path: Path to workspace root

    Returns:
        List of related file paths

    Example:
        >>> related = discover_related_files(
        ...     Path("src/agent_orchestration/tools/client.py"),
        ...     Path("/home/user/project"),
        ... )
        >>> print(related)
        [Path('src/agent_orchestration/tools/models.py'), ...]
    """
    related_files = []
    full_path = workspace_path / target_file

    if not full_path.exists():
        return related_files

    content = full_path.read_text()

    # Find relative imports (from . import X, from .module import Y)
    relative_imports = re.findall(r"from\s+\.(\w+)\s+import", content)
    for module in relative_imports:
        module_file = target_file.parent / f"{module}.py"
        if (workspace_path / module_file).exists():
            related_files.append(module_file)

    # Find absolute imports within same package
    package_pattern = r"from\s+(\w+(?:\.\w+)*)\s+import"
    absolute_imports = re.findall(package_pattern, content)

    for import_path in absolute_imports:
        # Convert import path to file path (e.g., agent_orchestration.tools.models -> src/agent_orchestration/tools/models.py)
        parts = import_path.split(".")
        potential_file = Path("src") / "/".join(parts) / "__init__.py"
        if (workspace_path / potential_file).exists():
            related_files.append(potential_file)

        potential_file = Path("src") / "/".join(parts[:-1]) / f"{parts[-1]}.py"
        if (workspace_path / potential_file).exists():
            related_files.append(potential_file)

    return list(set(related_files))


def extract_failing_tests(output: str) -> list[str]:
    """Extract failing test names from pytest output.

    Args:
        output: Pytest output string

    Returns:
        List of failing test names

    Example:
        >>> output = "FAILED tests/test_client.py::test_execute - AssertionError"
        >>> failing = extract_failing_tests(output)
        >>> print(failing)
        ['test_execute']
    """
    failing_tests = []

    # Pattern: FAILED tests/path/to/test.py::test_name - Error
    pattern = r"FAILED\s+[\w/]+\.py::(\w+)"
    matches = re.findall(pattern, output)
    failing_tests.extend(matches)

    return list(set(failing_tests))


def extract_uncovered_lines(output: str) -> list[str]:
    """Extract uncovered line ranges from coverage output.

    Args:
        output: Coverage output string

    Returns:
        List of uncovered line ranges (e.g., ["10-15", "20-25"])

    Example:
        >>> output = "src/client.py    150     30    80%   10-15, 20-25"
        >>> uncovered = extract_uncovered_lines(output)
        >>> print(uncovered)
        ['10-15', '20-25']
    """
    uncovered_lines = []

    # Pattern: filename.py    stmts   miss   cover   missing_lines
    pattern = r"\.py\s+\d+\s+\d+\s+\d+%\s+([\d\-,\s]+)"
    matches = re.findall(pattern, output)

    for match in matches:
        # Split by comma and clean up
        ranges = [r.strip() for r in match.split(",") if r.strip()]
        uncovered_lines.extend(ranges)

    return uncovered_lines


def extract_syntax_errors(output: str) -> list[str]:
    """Extract syntax error messages from output.

    Args:
        output: Output string with syntax errors

    Returns:
        List of syntax error messages

    Example:
        >>> output = "SyntaxError: invalid syntax at line 10"
        >>> errors = extract_syntax_errors(output)
        >>> print(errors)
        ['SyntaxError: invalid syntax at line 10']
    """
    syntax_errors = []

    # Pattern: SyntaxError: message
    pattern = r"SyntaxError:\s*(.+?)(?:\n|$)"
    matches = re.findall(pattern, output, re.MULTILINE)
    syntax_errors.extend(matches)

    # Pattern: File "...", line X (syntax error context)
    pattern = r'File\s+"[^"]+",\s+line\s+\d+.*?(?:\n|$)'
    matches = re.findall(pattern, output, re.MULTILINE)
    syntax_errors.extend(matches)

    return syntax_errors


def create_retry_feedback(  # noqa: PLR0911
    error_type: TestGenerationError,
    spec: TestTaskSpecification,
    result: OpenHandsTaskResult,
    workspace_path: Path,
) -> str:
    """Create feedback message for retry based on error type.

    Args:
        error_type: Classified error type
        spec: Original task specification
        result: Failed task result
        workspace_path: Path to workspace root

    Returns:
        Feedback message for retry

    Example:
        >>> feedback = create_retry_feedback(
        ...     TestGenerationError.COVERAGE_GAP,
        ...     spec,
        ...     result,
        ...     Path("/home/user/project"),
        ... )
        >>> print(feedback[:50])
        The previous test generation had insufficient cov...
    """
    if error_type == TestGenerationError.INSUFFICIENT_CONTEXT:
        # Add related files as context
        related_files = discover_related_files(spec.target_file, workspace_path)
        context_list = "\n".join(f"- `{f}`" for f in related_files)
        return f"""
The previous test generation lacked sufficient context. Please retry with these additional context files:

{context_list}

Review these files to understand dependencies and usage patterns before generating tests.
""".strip()

    if error_type == TestGenerationError.PARTIAL_GENERATION:
        # Focus on failing tests
        failing_tests = extract_failing_tests(result.output or "")
        if failing_tests:
            tests_list = "\n".join(f"- {t}" for t in failing_tests)
            return f"""
The previous test generation was incomplete. These tests are failing:

{tests_list}

Please fix these failing tests and ensure all tests pass.
""".strip()
        return "The previous test generation was incomplete. Please complete all tests and ensure they pass."

    if error_type == TestGenerationError.COVERAGE_GAP:
        # Add coverage requirements
        uncovered_lines = extract_uncovered_lines(result.output or "")
        if uncovered_lines:
            lines_list = "\n".join(
                f"- Lines {ln}" for ln in uncovered_lines[:10]
            )  # Limit to 10
            return f"""
The previous test generation had insufficient coverage. These lines are not covered:

{lines_list}

Please add tests to cover these lines and achieve ≥{spec.coverage_threshold}% coverage.
""".strip()
        return f"The previous test generation had insufficient coverage. Please add more tests to achieve ≥{spec.coverage_threshold}% coverage."

    if error_type == TestGenerationError.SYNTAX_ERROR:
        # Add syntax validation
        syntax_errors = extract_syntax_errors(result.output or "")
        if syntax_errors:
            errors_list = "\n".join(f"- {e}" for e in syntax_errors[:5])  # Limit to 5
            return f"""
The previous test generation had syntax errors:

{errors_list}

Please fix these syntax errors and ensure the test file is valid Python.
""".strip()
        return "The previous test generation had syntax errors. Please fix them and ensure valid Python syntax."

    if error_type == TestGenerationError.TIMEOUT:
        return f"""
The previous test generation timed out after {spec.timeout_seconds}s.

Please:
1. Generate simpler, more focused tests
2. Avoid complex test setups
3. Focus on essential test cases first
""".strip()

    if error_type == TestGenerationError.EXECUTION_FAILURE:
        return f"""
The previous test generation produced tests that fail when executed.

Error details:
{result.error or result.output[:500]}

Please fix the test implementation to ensure all tests pass.
""".strip()

    return "The previous test generation failed. Please retry with improvements."
