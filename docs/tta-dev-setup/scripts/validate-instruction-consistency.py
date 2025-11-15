#!/usr/bin/env python3
"""
Instruction Consistency Validator

Checks that .instructions.md files follow standards and don't conflict.
Ensures context management is clean and predictable.

Usage:
    python scripts/validate-instruction-consistency.py
"""

import re
import sys
from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Extract YAML frontmatter from markdown file."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def validate_instruction_file(file_path: Path) -> bool:
    """Validate a single instruction file."""

    content = file_path.read_text()

    # Check for frontmatter
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        return False

    # Validate applyTo field
    if "applyTo" not in frontmatter:
        return False

    apply_to = frontmatter.get("applyTo")
    if not isinstance(apply_to, (str, list)):
        return False

    # Validate tags (optional but recommended)
    if "tags" in frontmatter:
        tags = frontmatter.get("tags")
        if not isinstance(tags, list):
            pass

    # Check for required sections (basic heuristics)
    if len(content) < 100:
        pass

    # Check for markdown structure
    headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    if not headers:
        pass

    return True


def check_for_conflicts(instruction_files: list[Path]) -> bool:
    """Check for conflicting instructions across files."""

    # Build pattern → file mapping
    pattern_map: dict[str, list[Path]] = {}

    for file_path in instruction_files:
        content = file_path.read_text()
        frontmatter = parse_frontmatter(content)

        if not frontmatter:
            continue

        apply_to = frontmatter.get("applyTo", [])
        if isinstance(apply_to, str):
            apply_to = [apply_to]

        for pattern in apply_to:
            if pattern not in pattern_map:
                pattern_map[pattern] = []
            pattern_map[pattern].append(file_path)

    # Check for overlaps
    conflicts_found = False
    for pattern, files in pattern_map.items():
        if len(files) > 1:
            for _f in files:
                pass
            conflicts_found = True

    if not conflicts_found:
        pass

    return not conflicts_found


def main() -> int:
    """Main validation function."""

    # Find all instruction files
    instructions_dir = Path(".github/instructions")
    if not instructions_dir.exists():
        return 1

    instruction_files = list(instructions_dir.glob("*.instructions.md"))

    if not instruction_files:
        return 0

    # Validate each file
    all_valid = True
    for file_path in instruction_files:
        if not validate_instruction_file(file_path):
            all_valid = False

    # Check for conflicts
    if not check_for_conflicts(instruction_files):
        all_valid = False

    if all_valid:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
