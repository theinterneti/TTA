#!/usr/bin/env python3
"""
Extract docstrings from Python source files for documentation generation.

Usage:
    python scripts/extract_docstrings.py src/agent_orchestration/circuit_breaker.py
    python scripts/extract_docstrings.py src/agent_orchestration/ --output docs/generated/
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Any


def extract_docstrings(file_path: Path) -> dict[str, Any]:
    """Extract all docstrings from a Python file.

    Args:
        file_path: Path to Python source file

    Returns:
        Dictionary mapping node names to their docstrings and metadata
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}", file=sys.stderr)
        return {}

    docstrings = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings["__module__"] = {
                    "type": "module",
                    "docstring": docstring,
                    "lineno": 1,
                }

        elif isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = {
                    "type": "class",
                    "docstring": docstring,
                    "lineno": node.lineno,
                    "bases": [ast.unparse(base) for base in node.bases],
                }

        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            docstring = ast.get_docstring(node)
            if docstring:
                # Extract function signature
                args = []
                for arg in node.args.args:
                    arg_annotation = (
                        ast.unparse(arg.annotation) if arg.annotation else "Any"
                    )
                    args.append(f"{arg.arg}: {arg_annotation}")

                return_annotation = (
                    ast.unparse(node.returns) if node.returns else "None"
                )

                is_async = isinstance(node, ast.AsyncFunctionDef)
                signature = f"{'async ' if is_async else ''}def {node.name}({', '.join(args)}) -> {return_annotation}"

                docstrings[node.name] = {
                    "type": "function" if not is_async else "async_function",
                    "docstring": docstring,
                    "signature": signature,
                    "lineno": node.lineno,
                    "is_async": is_async,
                }

    return docstrings


def generate_markdown(docstrings: dict[str, Any], file_path: Path) -> str:
    """Generate markdown documentation from extracted docstrings.

    Args:
        docstrings: Extracted docstrings dictionary
        file_path: Original source file path

    Returns:
        Markdown formatted documentation
    """
    module_name = file_path.stem
    lines = [
        f"# {module_name}",
        "",
        f"**Source**: `{file_path}`",
        "",
    ]

    # Module docstring
    if "__module__" in docstrings:
        lines.extend(["## Overview", "", docstrings["__module__"]["docstring"], ""])

    # Classes
    classes = {
        name: info for name, info in docstrings.items() if info["type"] == "class"
    }
    if classes:
        lines.append("## Classes")
        lines.append("")
        for name, info in classes.items():
            lines.extend(
                [
                    f"### `{name}`",
                    "",
                    f"**Line**: {info['lineno']}",
                    "",
                    info["docstring"],
                    "",
                ]
            )

    # Functions
    functions = {
        name: info
        for name, info in docstrings.items()
        if info["type"] in ["function", "async_function"]
    }
    if functions:
        lines.append("## Functions")
        lines.append("")
        for name, info in functions.items():
            lines.extend(
                [
                    f"### `{info['signature']}`",
                    "",
                    f"**Line**: {info['lineno']}",
                    "",
                    info["docstring"],
                    "",
                ]
            )

    # Footer
    lines.extend(
        [
            "---",
            "",
            f"**Generated from**: {file_path}",
            "**Last Updated**: (timestamp will be added by docs-agent)",
        ]
    )

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract docstrings from Python files")
    parser.add_argument("path", help="Python file or directory to process")
    parser.add_argument(
        "--output", help="Output file or directory for generated docs", default=None
    )
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Process single file
    if path.is_file():
        if not path.suffix == ".py":
            print(f"❌ Not a Python file: {path}", file=sys.stderr)
            sys.exit(1)

        docstrings = extract_docstrings(path)

        if not docstrings:
            print(f"⚠️  No docstrings found in {path}", file=sys.stderr)
            sys.exit(0)

        markdown = generate_markdown(docstrings, path)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown)
            print(f"✅ Generated documentation: {output_path}")
        else:
            print(markdown)

    # Process directory
    elif path.is_dir():
        py_files = list(path.rglob("*.py"))
        print(f"📂 Processing {len(py_files)} Python files in {path}")

        for py_file in py_files:
            docstrings = extract_docstrings(py_file)
            if docstrings:
                markdown = generate_markdown(docstrings, py_file)

                if args.output:
                    output_dir = Path(args.output)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / f"{py_file.stem}.md"
                    output_file.write_text(markdown)
                    print(f"✅ {py_file.stem}.md")
                else:
                    print(f"\n{'=' * 60}\n{py_file}\n{'=' * 60}\n")
                    print(markdown)

    else:
        print(f"❌ Invalid path: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
