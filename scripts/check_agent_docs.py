#!/usr/bin/env python3
"""Check that root agent instruction files stay within the 100-line budget.

Usage:
    python scripts/check_agent_docs.py                  # check repo root
    python scripts/check_agent_docs.py --root /path     # check alternate root
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BUDGET = 100

# Hardcoded list of root files that must stay under budget.
ROOT_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".cline/instructions.md",
    ".augment/instructions.md",
]


def check(root: Path) -> list[tuple[str, int]]:
    """Return list of (filename, line_count) for files over budget."""
    violations: list[tuple[str, int]] = []
    for rel in ROOT_FILES:
        path = root / rel
        if not path.exists():
            continue
        lines = len(path.read_text().splitlines())
        if lines > BUDGET:
            violations.append((rel, lines))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd)",
    )
    args = parser.parse_args()

    violations = check(args.root)
    if not violations:
        print("check-agent-docs: all root files within 100-line budget")
        return 0

    print("check-agent-docs: BUDGET VIOLATION — root files must stay under 100 lines")
    print()
    for rel, count in violations:
        print(f"  {rel}: {count} lines (over by {count - BUDGET})")
    print()
    print("Fix: move content to docs/agents/dev/<topic>.md and add a routing row.")
    print("See docs/agents/MAINTENANCE.md for instructions.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
