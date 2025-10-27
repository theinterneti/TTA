# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Automatically fix B904 errors by adding exception chaining to raise statements.

This script uses AST parsing to accurately identify raise statements within
except blocks that lack proper exception chaining (` from e`), then uses
line-based text replacement to preserve formatting.

Usage:
    python scripts/fix_b904_exception_chaining.py [--dry-run] [files...]

Examples:
    # Dry run on specific files
    python scripts/fix_b904_exception_chaining.py --dry-run src/player_experience/api/*.py

    # Apply fixes to all files with B904 errors
    python scripts/fix_b904_exception_chaining.py src/**/*.py
"""

import argparse
import ast
import sys
from pathlib import Path


class ExceptionChainingAnalyzer(ast.NodeVisitor):
    """AST visitor that identifies raise statements needing exception chaining."""

    def __init__(self):
        self.fixes = []
        self.in_except_handler = False
        self.current_exception_var = None
        self.exception_stack = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Visit except handler and track exception variable name."""
        # Save current state
        self.exception_stack.append(
            (self.in_except_handler, self.current_exception_var)
        )

        self.in_except_handler = True
        self.current_exception_var = node.name  # e.g., 'e', 'exc', 'error'

        # Visit children
        self.generic_visit(node)

        # Restore state
        self.in_except_handler, self.current_exception_var = self.exception_stack.pop()

    def visit_Raise(self, node: ast.Raise):
        """Visit raise statement and record if it needs exception chaining."""
        # Only process raises inside except handlers
        if not self.in_except_handler:
            return

        # Skip if already has exception chaining (cause is set)
        if node.cause is not None:
            return

        # Skip bare raises (re-raising)
        if node.exc is None:
            return

        # Skip if no exception variable available
        if not self.current_exception_var:
            return

        # Record the fix needed
        self.fixes.append(
            {
                "line": node.lineno,
                "col": node.col_offset,
                "end_line": node.end_lineno,
                "end_col": node.end_col_offset,
                "exception_var": self.current_exception_var,
            }
        )

        # Continue visiting
        self.generic_visit(node)


def fix_file(
    filepath: Path, dry_run: bool = False
) -> tuple[bool, int, str, list[dict]]:
    """
    Fix B904 errors in a single file using line-based replacement.

    Args:
        filepath: Path to the Python file
        dry_run: If True, don't write changes

    Returns:
        Tuple of (changed, num_fixes, error_message, fixes_list)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        # Parse the file
        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            return False, 0, f"Syntax error: {e}", []

        # Analyze and find fixes
        analyzer = ExceptionChainingAnalyzer()
        analyzer.visit(tree)

        # If no fixes, return early
        if not analyzer.fixes:
            return False, 0, "", []

        # Apply fixes in reverse order (bottom to top) to preserve line numbers
        fixes_applied = []
        for fix in sorted(analyzer.fixes, key=lambda f: f["line"], reverse=True):
            line_idx = fix["line"] - 1  # Convert to 0-based
            end_line_idx = fix["end_line"] - 1

            # Handle multi-line raise statements
            if line_idx == end_line_idx:
                # Single line raise
                line = lines[line_idx]
                # Find the closing paren or end of raise statement
                # Add ' from <var>' before the newline
                line = line.rstrip("\n\r")
                if line.rstrip().endswith(")"):
                    line = line.rstrip() + f" from {fix['exception_var']}\n"
                else:
                    line = line.rstrip() + f" from {fix['exception_var']}\n"
                lines[line_idx] = line
            else:
                # Multi-line raise - add to the last line
                last_line = lines[end_line_idx]
                last_line = last_line.rstrip("\n\r")
                if last_line.rstrip().endswith(")"):
                    last_line = last_line.rstrip() + f" from {fix['exception_var']}\n"
                else:
                    last_line = last_line.rstrip() + f" from {fix['exception_var']}\n"
                lines[end_line_idx] = last_line

            fixes_applied.append(
                {
                    "file": str(filepath),
                    "line": fix["line"],
                    "exception_var": fix["exception_var"],
                }
            )

        # Write changes if not dry run
        if not dry_run:
            new_content = "".join(lines)
            filepath.write_text(new_content, encoding="utf-8")

        return True, len(fixes_applied), "", fixes_applied

    except Exception as e:
        return False, 0, f"Error processing file: {e}", []


def main():
    parser = argparse.ArgumentParser(
        description="Fix B904 errors by adding exception chaining"
    )
    parser.add_argument("files", nargs="+", type=Path, help="Python files to process")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    total_files = 0
    total_fixes = 0
    changed_files = []
    errors = []
    all_fixes = []

    print(f"{'DRY RUN: ' if args.dry_run else ''}Processing {len(args.files)} files...")
    print()

    for filepath in args.files:
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        if filepath.suffix != ".py":
            continue

        total_files += 1
        changed, num_fixes, error, fixes = fix_file(filepath, args.dry_run)

        if error:
            errors.append((filepath, error))
            print(f"❌ {filepath}: {error}")
        elif changed:
            changed_files.append(filepath)
            total_fixes += num_fixes
            all_fixes.extend(fixes)
            print(f"✅ {filepath}: {num_fixes} fix(es)")
        else:
            print(f"⏭️  {filepath}: No changes needed")

    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Files processed: {total_files}")
    print(f"  Files changed: {len(changed_files)}")
    print(f"  Total fixes: {total_fixes}")
    print(f"  Errors: {len(errors)}")

    if args.dry_run:
        print()
        print("⚠️  DRY RUN: No files were modified")
        print("   Run without --dry-run to apply changes")

    if errors:
        print()
        print("Errors encountered:")
        for filepath, error in errors:
            print(f"  {filepath}: {error}")
        return 1

    # Save detailed report
    if all_fixes and not args.dry_run:
        report_path = Path("B904_FIXES_REPORT.txt")
        with open(report_path, "w") as f:
            f.write("B904 Exception Chaining Fixes Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total fixes: {len(all_fixes)}\n")
            f.write(f"Files changed: {len(changed_files)}\n\n")
            f.write("Detailed fixes:\n")
            for fix in all_fixes:
                f.write(
                    f"  {fix['file']}:{fix['line']} - Added 'from {fix['exception_var']}'\n"
                )
        print(f"\n📝 Detailed report saved to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
