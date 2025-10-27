#!/usr/bin/env python3
"""
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
from typing import List, Tuple


def check_file(filepath: Path) -> List[Tuple[int, str]]:
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
        in_async_def = False
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

    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

    return violations


def main(filenames: List[str]) -> int:
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
        if not filepath.suffix == ".py":
            continue
        if not ("test" in filepath.name or filepath.parts and "tests" in filepath.parts):
            continue

        violations = check_file(filepath)

        if violations:
            exit_code = 1
            total_violations += len(violations)
            print(f"\n❌ {filepath}:")
            for line_num, line_content in violations:
                print(f"  Line {line_num}: {line_content.strip()}")
                print(
                    f"    → Should use @pytest_asyncio.fixture for async functions"
                )

    if total_violations > 0:
        print(
            f"\n⚠️  Found {total_violations} async fixture(s) with incorrect decorator."
        )
        print("   Use @pytest_asyncio.fixture instead of @pytest.fixture for async functions.")
        print("   Add 'import pytest_asyncio' at the top of the file if needed.")
    else:
        print("✅ All async fixtures use correct decorators.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
