"""Task builder for unit test generation using OpenHands.

This module provides functions to build natural language task descriptions
for OpenHands, following TTA's testing conventions and patterns.
"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Test_task_builder]]

from pathlib import Path

from .test_generation_models import TestTaskSpecification


def create_test_generation_task(spec: TestTaskSpecification) -> str:
    """Create natural language task description for OpenHands.

    Builds a comprehensive task description that includes:
    - Target file and coverage requirements
    - TTA testing conventions (uv run pytest, fixtures, markers)
    - Step-by-step instructions for test generation
    - Validation and verification steps

    Args:
        spec: Test task specification with all parameters

    Returns:
        Natural language task description string

    Example:
        >>> spec = TestTaskSpecification(
        ...     target_file=Path("src/agent_orchestration/tools/client.py"),
        ...     coverage_threshold=80.0,
        ... )
        >>> task = create_test_generation_task(spec)
        >>> print(task[:100])
        Generate comprehensive unit tests for `src/agent_orchestration/tools/client.py` with the following...
    """
    # Determine test file path
    test_file_path = get_test_file_path(spec.target_file, spec.test_directory)

    # Build context files section
    context_section = ""
    if spec.context_files:
        context_section = "\n**Context Files:**\n" + "\n".join(
            f"- `{f}`" for f in spec.context_files
        )

    # Build conventions section
    conventions = {
        "command": "uv run pytest",
        "coverage_threshold": f"≥{spec.coverage_threshold}%",
        "directory_structure": "mirror src/ in tests/",
        "fixtures": "tests/conftest.py",
        "markers": "unit, integration, asyncio",
        **spec.conventions,
    }

    return f"""
Generate comprehensive unit tests for `{spec.target_file}` with the following requirements:

**Target File:** `{spec.target_file}`
**Test File:** `{test_file_path}`
**Coverage Threshold:** ≥{spec.coverage_threshold}%
**Test Framework:** {spec.test_framework}
**Test Directory:** `{spec.test_directory}/`

**Testing Conventions:**
- Use `{conventions["command"]}` to run tests (NOT `uvx pytest`)
- Follow TTA's test directory structure ({conventions["directory_structure"]})
- Use pytest fixtures from `{conventions["fixtures"]}`
- Aim for {conventions["coverage_threshold"]} coverage
- Include unit tests for all public methods/functions
- Include edge cases and error handling tests
- Use appropriate markers: {conventions["markers"]}
{context_section}

**Steps:**
1. Analyze `{spec.target_file}` to identify all testable units (classes, methods, functions)
2. Review existing test patterns in `{spec.test_directory}/` directory
3. Generate comprehensive unit tests in `{test_file_path}`
4. Ensure tests follow TTA conventions (pytest, fixtures, markers)
5. Run `{conventions["command"]} {test_file_path} --cov={spec.target_file.parent} --cov-report=term-missing`
6. Verify coverage ≥{spec.coverage_threshold}%
7. Fix any failing tests or coverage gaps

**Output:**
- Generated test file path: `{test_file_path}`
- Coverage percentage achieved
- Number of tests generated
- Any issues encountered

**Important:**
- DO NOT use `uvx pytest` - always use `{conventions["command"]}`
- Follow TTA's test directory structure exactly
- Include docstrings for all test functions
- Test both success and failure cases
- Test edge cases (empty inputs, None, invalid values, etc.)
""".strip()


def create_package_test_generation_task(
    package_path: Path,
    coverage_threshold: float = 70.0,
) -> str:
    """Create task for generating tests for entire package.

    Builds a task description for generating comprehensive tests for all
    Python files in a package, following TTA conventions.

    Args:
        package_path: Path to package directory
        coverage_threshold: Minimum coverage percentage required (default: 70.0)

    Returns:
        Natural language task description string

    Example:
        >>> task = create_package_test_generation_task(
        ...     Path("src/agent_orchestration/tools"),
        ...     coverage_threshold=75.0,
        ... )
        >>> print(task[:100])
        Generate comprehensive unit tests for all files in package `src/agent_orchestration/tools/` with...
    """
    return f"""
Generate comprehensive unit tests for all files in package `{package_path}/` with ≥{coverage_threshold}% coverage.

**Package:** `{package_path}/`
**Coverage Threshold:** ≥{coverage_threshold}%
**Test Framework:** pytest

**Steps:**
1. List all Python files in `{package_path}/` (excluding `__init__.py`, `__pycache__`)
2. For each file, generate comprehensive unit tests following TTA conventions:
   - Use `uv run pytest` to run tests (NOT `uvx pytest`)
   - Place tests in `tests/{package_path}/` (mirroring package structure)
   - Use pytest fixtures from `tests/conftest.py`
   - Include edge cases and error handling tests
   - Use appropriate markers (unit, integration, asyncio)
3. Run `uv run pytest tests/{package_path}/ --cov={package_path} --cov-report=term-missing`
4. Verify overall package coverage ≥{coverage_threshold}%
5. Fix any failing tests or coverage gaps

**Output:**
- List of generated test files
- Overall package coverage percentage
- Number of tests generated per file
- Any issues encountered

**Important:**
- DO NOT use `uvx pytest` - always use `uv run pytest`
- Follow TTA's test directory structure exactly
- Test both success and failure cases
- Test edge cases for all functions
""".strip()


def get_test_file_path(
    target_file: Path,
    test_directory: Path = Path("tests"),
) -> Path:
    """Determine test file path following TTA conventions.

    TTA convention: tests/ directory mirrors src/ structure.
    Example: src/agent_orchestration/tools/client.py → tests/agent_orchestration/tools/test_client.py

    Args:
        target_file: Path to file for which to generate tests
        test_directory: Base test directory (default: Path("tests"))

    Returns:
        Path to test file following TTA conventions

    Example:
        >>> path = get_test_file_path(Path("src/agent_orchestration/tools/client.py"))
        >>> print(path)
        tests/agent_orchestration/tools/test_client.py

        >>> path = get_test_file_path(Path("agent_orchestration/tools/client.py"))
        >>> print(path)
        tests/agent_orchestration/tools/test_client.py
    """
    # Remove 'src/' prefix if present
    if target_file.parts and target_file.parts[0] == "src":
        relative_path = Path(*target_file.parts[1:])
    else:
        relative_path = target_file

    # Convert to test file name (test_*.py)
    test_file_name = f"test_{relative_path.stem}.py"

    # Construct full test path
    return test_directory / relative_path.parent / test_file_name
