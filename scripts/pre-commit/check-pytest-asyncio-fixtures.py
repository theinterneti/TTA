#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Pre-commit/Check-pytest-asyncio-fixtures]]
Pre-commit hook to validate pytest-asyncio fixture decorators.

This hook checks that async test fixtures use @pytest_asyncio.fixture
instead of @pytest.fixture to avoid deprecation warnings and ensure
proper async fixture handling.

Exit codes:
    0: All checks passed
    1: Found async fixtures with incorrect decorator
"""

import re
import sys
from pathlib import Path


def check_file(filepath: Path) -> list[tuple[int, str]]:
    """
    Check a single Python file for async fixtures with wrong decorator.

    Args:
        filepath: Path to the Python file to check

    Returns:
        List of (line_number, line_content) tuples for violations
    """
    violations = []

    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Track if we're in an async function definition
        decorator_line = None

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Check for @pytest.fixture decorator
            if re.match(r"@pytest\.fixture(\(|$)", stripped):
                decorator_line = i

            # Check if next non-empty line is async def
            elif decorator_line and stripped.startswith("async def"):
                violations.append((decorator_line, lines[decorator_line - 1]))
                decorator_line = None

            # Reset if we hit a non-decorator, non-async-def line
            elif decorator_line and stripped and not stripped.startswith("@"):
                decorator_line = None

    except Exception:
        pass

    return violations


def main(filenames: list[str]) -> int:
    """
    Main entry point for the pre-commit hook.

    Args:
        filenames: List of filenames to check

    Returns:
        Exit code (0 for success, 1 for violations found)
    """
    exit_code = 0
    total_violations = 0

    for filename in filenames:
        filepath = Path(filename)

        # Only check Python test files
        if filepath.suffix != ".py":
            continue
        if not (
            "test" in filepath.name or filepath.parts and "tests" in filepath.parts
        ):
            continue

        violations = check_file(filepath)

        if violations:
            exit_code = 1
            total_violations += len(violations)
            for _line_num, _line_content in violations:
                pass

    if total_violations > 0:
        pass
    else:
        pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
