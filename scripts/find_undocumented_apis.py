#!/usr/bin/env python3
"""
Find public APIs in source code that lack documentation.

Usage:
    python scripts/find_undocumented_apis.py src/
    python scripts/find_undocumented_apis.py src/agent_orchestration/
"""

import argparse
import ast
import sys
from pathlib import Path


def is_public_api(name: str) -> bool:
    """Check if a name represents a public API (not private/internal).

    Args:
        name: Function or class name

    Returns:
        True if public API
    """
    return not name.startswith("_")


def find_undocumented(file_path: Path) -> list[dict[str, any]]:
    """Find undocumented public APIs in a Python file.

    Args:
        file_path: Path to Python source file

    Returns:
        List of undocumented API definitions
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}", file=sys.stderr)
        return []

    undocumented = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if is_public_api(node.name) and not ast.get_docstring(node):
                undocumented.append(
                    {
                        "type": "class",
                        "name": node.name,
                        "line": node.lineno,
                        "file": str(file_path),
                    }
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if is_public_api(node.name) and not ast.get_docstring(node):
                undocumented.append(
                    {
                        "type": "function"
                        if isinstance(node, ast.FunctionDef)
                        else "async_function",
                        "name": node.name,
                        "line": node.lineno,
                        "file": str(file_path),
                    }
                )

    return undocumented


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Find undocumented public APIs in Python source"
    )
    parser.add_argument("path", help="Python file or directory to analyze")
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    all_undocumented = []

    # Process single file
    if path.is_file():
        if path.suffix != ".py":
            print(f"⚠️  Not a Python file: {path}", file=sys.stderr)
            sys.exit(0)

        all_undocumented = find_undocumented(path)

    # Process directory
    elif path.is_dir():
        py_files = [f for f in path.rglob("*.py") if not f.name.startswith("test_")]
        print(f"📂 Analyzing {len(py_files)} Python files in {path}\n")

        for py_file in py_files:
            undocumented = find_undocumented(py_file)
            all_undocumented.extend(undocumented)

    else:
        print(f"❌ Invalid path: {path}", file=sys.stderr)
        sys.exit(1)

    # Report results
    if not all_undocumented:
        print("✅ All public APIs are documented")
        sys.exit(0)

    print(f"❌ Found {len(all_undocumented)} undocumented public APIs:\n")

    # Group by file
    by_file = {}
    for item in all_undocumented:
        file_path = item["file"]
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(item)

    for file_path, items in sorted(by_file.items()):
        print(f"\n{file_path}:")
        for item in items:
            print(f"  Line {item['line']}: {item['type']} {item['name']}")

    sys.exit(1)


if __name__ == "__main__":
    main()
