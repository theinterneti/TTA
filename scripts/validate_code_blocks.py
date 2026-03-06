#!/usr/bin/env python3
"""
Validate that code blocks in documentation are valid Python.

Usage:
    python scripts/validate_code_blocks.py docs/
    python scripts/validate_code_blocks.py docs/architecture/circuit-breaker-api.md
"""

import argparse
import ast
import re
import sys
from pathlib import Path


def extract_code_blocks(markdown_content: str) -> list[tuple[int, str]]:
    """Extract Python code blocks from markdown.

    Args:
        markdown_content: Markdown file content

    Returns:
        List of (line_number, code) tuples
    """
    code_blocks = []
    in_code_block = False
    current_block = []
    block_start_line = 0
    line_num = 0

    for line in markdown_content.split("\n"):
        line_num += 1

        # Detect code block start
        if line.strip().startswith("```python"):
            in_code_block = True
            block_start_line = line_num + 1
            current_block = []
            continue

        # Detect code block end
        if line.strip().startswith("```") and in_code_block:
            in_code_block = False
            if current_block:
                code_blocks.append((block_start_line, "\n".join(current_block)))
            continue

        # Collect code block lines
        if in_code_block:
            current_block.append(line)

    return code_blocks


def validate_python_code(code: str, allow_ellipsis: bool = True) -> tuple[bool, str]:
    """Validate Python code compiles.

    Args:
        code: Python code string
        allow_ellipsis: Allow ... for placeholder code

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Skip validation for incomplete examples
    if allow_ellipsis and "..." in code:
        return True, "Skipped (contains ellipsis placeholder)"

    # Skip validation for examples with comments indicating incompleteness
    if "# ..." in code or "# (incomplete)" in code.lower():
        return True, "Skipped (marked as incomplete)"

    try:
        ast.parse(code)
        return True, "Valid"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"


def validate_file(file_path: Path, allow_ellipsis: bool = True) -> bool:
    """Validate all code blocks in a markdown file.

    Args:
        file_path: Path to markdown file
        allow_ellipsis: Allow ... placeholder code

    Returns:
        True if all code blocks are valid
    """
    content = file_path.read_text()
    code_blocks = extract_code_blocks(content)

    if not code_blocks:
        print(f"ℹ️  {file_path.name}: No Python code blocks found")
        return True

    all_valid = True
    invalid_count = 0

    for line_num, code in code_blocks:
        is_valid, message = validate_python_code(code, allow_ellipsis)

        if not is_valid:
            all_valid = False
            invalid_count += 1
            print(f"❌ {file_path.name}:{line_num} - {message}")
            print(f"   Code preview: {code[:100]}...")

    if all_valid:
        print(f"✅ {file_path.name}: All {len(code_blocks)} code blocks valid")
    else:
        print(
            f"❌ {file_path.name}: {invalid_count}/{len(code_blocks)} code blocks invalid"
        )

    return all_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Python code blocks in markdown documentation"
    )
    parser.add_argument("path", help="Markdown file or directory to validate")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on ellipsis placeholders (no incomplete examples)",
    )
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    allow_ellipsis = not args.strict
    all_valid = True

    # Process single file
    if path.is_file():
        if path.suffix != ".md":
            print(f"⚠️  Not a markdown file: {path}", file=sys.stderr)
            sys.exit(0)

        all_valid = validate_file(path, allow_ellipsis)

    # Process directory
    elif path.is_dir():
        md_files = list(path.rglob("*.md"))
        print(f"📂 Validating {len(md_files)} markdown files in {path}\n")

        for md_file in md_files:
            if not validate_file(md_file, allow_ellipsis):
                all_valid = False

    else:
        print(f"❌ Invalid path: {path}", file=sys.stderr)
        sys.exit(1)

    if all_valid:
        print("\n✅ All code blocks are valid")
        sys.exit(0)
    else:
        print("\n❌ Some code blocks are invalid")
        sys.exit(1)


if __name__ == "__main__":
    main()
