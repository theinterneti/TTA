"""Test file extractor for parsing OpenHands output.

This module provides functions to extract test files, parse coverage percentages,
and verify test quality from OpenHands task output.
"""

import re
from pathlib import Path


def extract_test_files_from_output(output: str, workspace_path: Path) -> list[Path]:
    """Extract generated test file paths from OpenHands output.
    
    Looks for patterns like:
    - "Generated test file: tests/agent_orchestration/tools/test_client.py"
    - "Created tests/agent_orchestration/tools/test_client.py"
    - File paths in output
    
    Args:
        output: OpenHands task output string
        workspace_path: Path to workspace root
    
    Returns:
        List of test file paths found in output
    
    Example:
        >>> output = "Generated test file: tests/agent_orchestration/tools/test_client.py"
        >>> workspace = Path("/home/user/project")
        >>> files = extract_test_files_from_output(output, workspace)
        >>> print(files)
        [Path('tests/agent_orchestration/tools/test_client.py')]
    """
    test_files = []
    
    # Pattern 1: Explicit "Generated test file:" or "Created" or "Test file:"
    patterns = [
        r"Generated test file:\s+(.+\.py)",
        r"Created\s+(.+\.py)",
        r"Test file:\s+(.+\.py)",
        r"Writing to\s+(.+\.py)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE)
        for match in matches:
            # Clean up the path (remove quotes, backticks, etc.)
            clean_path = match.strip().strip("`'\"")
            test_path = workspace_path / clean_path
            
            # Verify file exists and is in tests/ directory
            if test_path.exists() and "tests" in test_path.parts:
                test_files.append(Path(clean_path))
    
    # Pattern 2: Look for test file paths in output (tests/.../*.py)
    test_path_pattern = r"(tests/[^\s]+\.py)"
    matches = re.findall(test_path_pattern, output)
    for match in matches:
        clean_path = match.strip().strip("`'\"")
        test_path = workspace_path / clean_path
        if test_path.exists():
            test_files.append(Path(clean_path))
    
    # Deduplicate and return
    return list(set(test_files))


def parse_coverage_percentage(pytest_output: str) -> float:
    """Parse coverage percentage from pytest output.
    
    Example pytest output:
    ----------- coverage: platform linux, python 3.12.0-final-0 -----------
    Name                                      Stmts   Miss  Cover
    -------------------------------------------------------------
    src/agent_orchestration/tools/client.py     150     30    80%
    -------------------------------------------------------------
    TOTAL                                        150     30    80%
    
    Args:
        pytest_output: Output from pytest --cov command
    
    Returns:
        Coverage percentage as float (0.0-100.0), or 0.0 if not found
    
    Example:
        >>> output = "TOTAL                                        150     30    80%"
        >>> coverage = parse_coverage_percentage(output)
        >>> print(coverage)
        80.0
    """
    # Look for "TOTAL" line with coverage percentage
    total_pattern = r"TOTAL\s+\d+\s+\d+\s+(\d+)%"
    match = re.search(total_pattern, pytest_output)
    if match:
        return float(match.group(1))
    
    # Fallback: Look for any percentage in coverage output
    coverage_pattern = r"(\d+)%\s*$"
    matches = re.findall(coverage_pattern, pytest_output, re.MULTILINE)
    if matches:
        # Return the last percentage found (usually the total)
        return float(matches[-1])
    
    return 0.0


def verify_test_quality(test_file: Path) -> dict[str, any]:
    """Verify quality of generated tests.
    
    Checks:
    - Number of test functions
    - Assertion count
    - Edge case coverage
    - Error handling tests
    
    Args:
        test_file: Path to test file
    
    Returns:
        Dictionary with quality metrics:
        - num_tests: Number of test functions
        - num_assertions: Number of assert statements
        - has_edge_cases: Whether edge case tests are present
        - has_error_handling: Whether error handling tests are present
        - quality_score: Overall quality score (0-100)
    
    Example:
        >>> test_file = Path("tests/agent_orchestration/tools/test_client.py")
        >>> quality = verify_test_quality(test_file)
        >>> print(quality['quality_score'])
        85.0
    """
    if not test_file.exists():
        return {
            "num_tests": 0,
            "num_assertions": 0,
            "has_edge_cases": False,
            "has_error_handling": False,
            "quality_score": 0.0,
        }
    
    content = test_file.read_text()
    
    # Count test functions (def test_* or async def test_*)
    test_functions = re.findall(r"(?:async\s+)?def\s+test_\w+\(", content)
    num_tests = len(test_functions)
    
    # Count assertions
    assertions = re.findall(r"\bassert\s+", content)
    num_assertions = len(assertions)
    
    # Check for edge case tests
    edge_case_keywords = [
        "empty", "none", "null", "zero", "negative",
        "max", "min", "boundary", "edge", "invalid"
    ]
    has_edge_cases = any(
        keyword in content.lower() for keyword in edge_case_keywords
    )
    
    # Check for error handling tests
    error_keywords = ["raises", "exception", "error", "invalid", "pytest.raises"]
    has_error_handling = any(
        keyword in content.lower() for keyword in error_keywords
    )
    
    # Calculate quality score
    quality_score = calculate_quality_score(
        num_tests, num_assertions, has_edge_cases, has_error_handling
    )
    
    return {
        "num_tests": num_tests,
        "num_assertions": num_assertions,
        "has_edge_cases": has_edge_cases,
        "has_error_handling": has_error_handling,
        "quality_score": quality_score,
    }


def calculate_quality_score(
    num_tests: int,
    num_assertions: int,
    has_edge_cases: bool,
    has_error_handling: bool,
) -> float:
    """Calculate quality score (0-100) based on test characteristics.
    
    Scoring:
    - Test count: max 40 points (4 points per test, up to 10 tests)
    - Assertion count: max 30 points (2 points per assertion, up to 15 assertions)
    - Edge cases: 15 points
    - Error handling: 15 points
    
    Args:
        num_tests: Number of test functions
        num_assertions: Number of assert statements
        has_edge_cases: Whether edge case tests are present
        has_error_handling: Whether error handling tests are present
    
    Returns:
        Quality score (0-100)
    
    Example:
        >>> score = calculate_quality_score(8, 12, True, True)
        >>> print(score)
        86.0
    """
    score = 0.0
    
    # Test count (max 40 points)
    score += min(num_tests * 4, 40)
    
    # Assertion count (max 30 points)
    score += min(num_assertions * 2, 30)
    
    # Edge cases (15 points)
    score += 15 if has_edge_cases else 0
    
    # Error handling (15 points)
    score += 15 if has_error_handling else 0
    
    return min(score, 100.0)

