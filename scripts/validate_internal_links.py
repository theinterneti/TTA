#!/usr/bin/env python3
"""
Validate internal links in markdown documentation.

Usage:
    python scripts/validate_internal_links.py docs/
    grep -r "\\](" docs/ --include="*.md" | python scripts/validate_internal_links.py
"""

import re
import sys
from pathlib import Path


def extract_links_from_line(line: str) -> list[str]:
    """Extract markdown links from a line.

    Args:
        line: Line of text

    Returns:
        List of link targets
    """
    # Match markdown links: [text](path)
    pattern = r"\]\(([^)]+)\)"
    matches = re.findall(pattern, line)
    return matches


def is_internal_link(link: str) -> bool:
    """Check if link is internal (relative path).

    Args:
        link: Link target

    Returns:
        True if internal link
    """
    return not link.startswith(("http://", "https://", "#", "mailto:"))


def validate_link(link: str, source_file: Path) -> bool:
    """Validate a link target exists.

    Args:
        link: Link target (relative path)
        source_file: Source markdown file containing the link

    Returns:
        True if link target exists
    """
    # Resolve relative to source file
    link_path = (source_file.parent / link).resolve()

    # Check if target exists
    return link_path.exists()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Read from stdin (piped from grep)
        lines = sys.stdin.readlines()
        process_grep_output(lines)
    else:
        # Process directory
        path = Path(sys.argv[1])
        process_directory(path)


def process_grep_output(lines: list[str]):
    """Process grep output (file:line format).

    Args:
        lines: Lines from grep output
    """
    broken_links = []

    for line in lines:
        if ":" not in line:
            continue

        parts = line.split(":", 1)
        file_path = Path(parts[0].strip())
        content = parts[1].strip()

        links = extract_links_from_line(content)

        for link in links:
            if is_internal_link(link):
                if not validate_link(link, file_path):
                    broken_links.append((file_path, link))

    report_results(broken_links)


def process_directory(path: Path):
    """Process all markdown files in directory.

    Args:
        path: Directory to process
    """
    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    md_files = list(path.rglob("*.md"))
    print(f"📂 Validating links in {len(md_files)} markdown files\n")

    broken_links = []

    for md_file in md_files:
        content = md_file.read_text()
        line_num = 0

        for line in content.split("\n"):
            line_num += 1
            links = extract_links_from_line(line)

            for link in links:
                if is_internal_link(link):
                    if not validate_link(link, md_file):
                        broken_links.append((f"{md_file}:{line_num}", link))

    report_results(broken_links)


def report_results(broken_links: list[tuple[str, str]]):
    """Report validation results.

    Args:
        broken_links: List of (source, link) tuples
    """
    if not broken_links:
        print("✅ All internal links are valid")
        sys.exit(0)

    print(f"❌ Found {len(broken_links)} broken links:\n")

    for source, link in broken_links:
        print(f"  {source}")
        print(f"    → {link}")

    sys.exit(1)


if __name__ == "__main__":
    main()
