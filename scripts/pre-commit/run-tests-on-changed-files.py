#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Pre-commit/Run-tests-on-changed-files]]
Pre-commit hook to run tests for changed source files.

This hook runs tests only for the source files that have been changed,
providing fast feedback without running the entire test suite.

Usage:
    python scripts/pre-commit/run-tests-on-changed-files.py <file1> <file2> ...

Exit codes:
    0: All tests passed
    1: Tests failed or error occurred
    2: No tests found for changed files (passes by default)

Examples:
    # Run tests for a single changed file
    python scripts/pre-commit/run-tests-on-changed-files.py src/main.py

    # Run tests for multiple changed files
    python scripts/pre-commit/run-tests-on-changed-files.py src/main.py src/utils.py

Skip this hook:
    SKIP=run-tests-on-changed-files git commit -m "message"
"""

import subprocess
import sys
from pathlib import Path


def map_source_to_test_files(source_file: Path) -> list[Path]:
    """
    Map a source file to its corresponding test file(s).

    Args:
        source_file: Path to source file (e.g., src/module/file.py)

    Returns:
        List of potential test file paths
    """
    test_files = []

    # Only process Python files in src/
    if source_file.suffix != ".py":
        return test_files
    if not source_file.parts or "src" not in source_file.parts:
        return test_files

    # Get the relative path from src/
    try:
        src_index = source_file.parts.index("src")
        relative_parts = source_file.parts[src_index + 1 :]
    except (ValueError, IndexError):
        return test_files

    # Build test file name
    if relative_parts:
        # Get the file name without extension
        file_stem = source_file.stem

        # Build directory path (everything except the file name)
        if len(relative_parts) > 1:
            dir_path = Path(*relative_parts[:-1])
        else:
            dir_path = Path()

        # Pattern 1: tests/unit/module/test_file.py
        unit_test = Path("tests/unit") / dir_path / f"test_{file_stem}.py"
        if unit_test.exists():
            test_files.append(unit_test)

        # Pattern 2: tests/integration/module/test_file.py
        integration_test = Path("tests/integration") / dir_path / f"test_{file_stem}.py"
        if integration_test.exists():
            test_files.append(integration_test)

        # Pattern 3: tests/module/test_file.py (flat structure)
        flat_test = Path("tests") / dir_path / f"test_{file_stem}.py"
        if flat_test.exists() and flat_test not in test_files:
            test_files.append(flat_test)

        # Pattern 4: tests/test_file.py (root level)
        root_test = Path("tests") / f"test_{file_stem}.py"
        if root_test.exists() and root_test not in test_files:
            test_files.append(root_test)

    return test_files


def collect_test_files(changed_files: list[str]) -> set[Path]:
    """
    Collect all test files for the changed source files.

    Args:
        changed_files: List of changed file paths

    Returns:
        Set of test file paths to run
    """
    test_files = set()

    for file_path in changed_files:
        source_file = Path(file_path)
        tests = map_source_to_test_files(source_file)
        test_files.update(tests)

    return test_files


def run_tests(test_files: set[Path], timeout: int = 60) -> int:
    """
    Run pytest on the collected test files.

    Args:
        test_files: Set of test file paths to run
        timeout: Maximum time to run tests (seconds)

    Returns:
        Exit code from pytest (0 = success, non-zero = failure)
    """
    if not test_files:
        return 0

    # Convert to sorted list for consistent output
    test_file_list = sorted(str(f) for f in test_files)

    for _test_file in test_file_list:
        pass

    # Build pytest command
    cmd = ["uv", "run", "pytest"] + test_file_list + ["-v", "--tb=short"]

    try:
        # Run pytest with timeout
        result = subprocess.run(
            cmd,
            check=False,
            timeout=timeout,
            capture_output=False,  # Show output in real-time
            text=True,
        )
        return result.returncode

    except subprocess.TimeoutExpired:
        return 1

    except FileNotFoundError:
        return 1

    except Exception:
        return 1


def main(filenames: list[str]) -> int:
    """
    Main entry point for the pre-commit hook.

    Args:
        filenames: List of changed file paths

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if not filenames:
        return 0

    # Collect test files for changed source files
    test_files = collect_test_files(filenames)

    # Run tests
    exit_code = run_tests(test_files)

    if exit_code == 0:
        pass
    else:
        pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
