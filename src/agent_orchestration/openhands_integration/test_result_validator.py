"""Test result validator for validating generated tests.

This module provides functions to validate generated tests through syntax checking,
coverage verification, test execution, and convention compliance.
"""

import asyncio
import subprocess
from pathlib import Path

from .test_file_extractor import parse_coverage_percentage, verify_test_quality
from .test_generation_models import TestValidationResult


async def validate_generated_tests(
    test_file: Path,
    target_file: Path,
    coverage_threshold: float,
    workspace_path: Path,
) -> TestValidationResult:
    """Validate generated tests through comprehensive checks.
    
    Runs:
    1. Syntax check (Python compilation)
    2. Convention validation
    3. Test execution (pytest)
    4. Coverage check (pytest --cov)
    
    Args:
        test_file: Path to generated test file
        target_file: Path to target file being tested
        coverage_threshold: Minimum coverage percentage required
        workspace_path: Path to workspace root
    
    Returns:
        TestValidationResult with all validation results
    
    Example:
        >>> result = await validate_generated_tests(
        ...     Path("tests/agent_orchestration/tools/test_client.py"),
        ...     Path("src/agent_orchestration/tools/client.py"),
        ...     70.0,
        ...     Path("/home/user/project"),
        ... )
        >>> print(result.syntax_valid, result.coverage_percentage)
        True 85.5
    """
    issues = []
    
    # 1. Syntax check
    syntax_valid = await _check_syntax(test_file, workspace_path)
    if not syntax_valid:
        issues.append("Syntax errors in generated test file")
    
    # 2. Convention validation
    convention_issues = validate_test_conventions(test_file)
    conventions_followed = len(convention_issues) == 0
    issues.extend(convention_issues)
    
    # 3. Test execution
    tests_pass = False
    coverage_percentage = 0.0
    
    if syntax_valid:
        # Run tests
        test_result = await _run_tests(test_file, workspace_path)
        tests_pass = test_result.returncode == 0
        if not tests_pass:
            issues.append(f"Tests failed: {test_result.stderr[:200]}")
        
        # Run coverage
        coverage_result = await _run_coverage(test_file, target_file, workspace_path)
        coverage_percentage = parse_coverage_percentage(coverage_result.stdout)
        
        if coverage_percentage < coverage_threshold:
            issues.append(
                f"Coverage {coverage_percentage}% below threshold {coverage_threshold}%"
            )
    
    # 4. Quality verification
    quality_metrics = verify_test_quality(workspace_path / test_file)
    quality_score = quality_metrics["quality_score"]
    
    return TestValidationResult(
        syntax_valid=syntax_valid,
        coverage_percentage=coverage_percentage,
        tests_pass=tests_pass,
        conventions_followed=conventions_followed,
        issues=issues,
        quality_score=quality_score,
        test_file_path=test_file,
    )


def validate_test_conventions(test_file: Path) -> list[str]:
    """Validate test file follows TTA conventions.
    
    Checks:
    - File location (in tests/ directory)
    - File naming (test_*.py or *_test.py)
    - Imports (import pytest)
    - Anti-patterns (uvx pytest in comments/docstrings)
    
    Args:
        test_file: Path to test file
    
    Returns:
        List of convention issues (empty if all conventions followed)
    
    Example:
        >>> issues = validate_test_conventions(Path("tests/agent_orchestration/tools/test_client.py"))
        >>> print(issues)
        []
    """
    issues = []
    
    # Check file location
    if "tests" not in test_file.parts:
        issues.append(f"Test file not in tests/ directory: {test_file}")
    
    # Check file naming
    file_name = test_file.name
    if not (file_name.startswith("test_") or file_name.endswith("_test.py")):
        issues.append(f"Test file name should start with 'test_' or end with '_test.py': {file_name}")
    
    # Check file exists
    if not test_file.exists():
        issues.append(f"Test file does not exist: {test_file}")
        return issues  # Can't check content if file doesn't exist
    
    # Check imports and anti-patterns
    content = test_file.read_text()
    
    if "import pytest" not in content and "from pytest" not in content:
        issues.append("Test file should import pytest")
    
    if "uvx pytest" in content:
        issues.append("Test file contains 'uvx pytest' anti-pattern (should use 'uv run pytest')")
    
    return issues


async def _check_syntax(test_file: Path, workspace_path: Path) -> bool:
    """Check Python syntax by compiling the file.
    
    Args:
        test_file: Path to test file
        workspace_path: Path to workspace root
    
    Returns:
        True if syntax is valid, False otherwise
    """
    full_path = workspace_path / test_file
    if not full_path.exists():
        return False
    
    try:
        # Try to compile the file
        with open(full_path, "r") as f:
            compile(f.read(), str(full_path), "exec")
        return True
    except SyntaxError:
        return False


async def _run_tests(test_file: Path, workspace_path: Path) -> subprocess.CompletedProcess:
    """Run pytest on test file.
    
    Args:
        test_file: Path to test file
        workspace_path: Path to workspace root
    
    Returns:
        CompletedProcess with test results
    """
    cmd = f"uv run pytest {test_file} -v"
    return await run_command(cmd, workspace_path)


async def _run_coverage(
    test_file: Path,
    target_file: Path,
    workspace_path: Path,
) -> subprocess.CompletedProcess:
    """Run pytest with coverage on test file.
    
    Args:
        test_file: Path to test file
        target_file: Path to target file being tested
        workspace_path: Path to workspace root
    
    Returns:
        CompletedProcess with coverage results
    """
    # Get the module path for coverage (e.g., src/agent_orchestration/tools/client.py)
    cmd = f"uv run pytest {test_file} --cov={target_file.parent} --cov-report=term-missing"
    return await run_command(cmd, workspace_path)


async def run_command(command: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run shell command asynchronously.
    
    Args:
        command: Shell command to run
        cwd: Working directory
    
    Returns:
        CompletedProcess with stdout and stderr
    
    Example:
        >>> result = await run_command("echo 'hello'", Path("/tmp"))
        >>> print(result.stdout)
        hello
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd),
    )
    
    stdout, stderr = await process.communicate()
    
    return subprocess.CompletedProcess(
        args=command,
        returncode=process.returncode or 0,
        stdout=stdout.decode("utf-8", errors="replace"),
        stderr=stderr.decode("utf-8", errors="replace"),
    )

