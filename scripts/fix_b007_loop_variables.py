# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Fix B007: Loop control variable not used within loop body

This script uses AST parsing to identify loop control variables that are not
used within the loop body and replaces them with '_' (underscore).

Usage:
    python scripts/fix_b007_loop_variables.py --dry-run <files>  # Test mode
    python scripts/fix_b007_loop_variables.py <files>            # Apply fixes
"""

import ast
import sys
from pathlib import Path


class LoopVariableAnalyzer(ast.NodeVisitor):
    """Analyze loop control variables and their usage within loop bodies."""

    def __init__(self):
        self.fixes: list[dict] = []
        self.current_loop_var: str | None = None
        self.current_loop_line: int | None = None
        self.loop_body_vars: set[str] = set()
        self.in_loop_body = False

    def visit_For(self, node: ast.For):
        """Visit for loop and check if loop variable is used in body."""
        loop_line = node.lineno
        loop_vars = []

        # Get loop variable name(s)
        if isinstance(node.target, ast.Name):
            loop_vars = [node.target.id]
        elif isinstance(node.target, ast.Tuple):
            # Handle tuple unpacking: for key, value in items()
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    loop_vars.append(elt.id)

        if not loop_vars:
            self.generic_visit(node)
            return

        # Save current state
        prev_loop_var = self.current_loop_var
        prev_loop_line = self.current_loop_line
        prev_loop_body_vars = self.loop_body_vars.copy()
        prev_in_loop_body = self.in_loop_body

        # Analyze loop body for each variable
        for loop_var in loop_vars:
            self.current_loop_var = loop_var
            self.current_loop_line = loop_line
            self.loop_body_vars = set()
            self.in_loop_body = True

            # Visit loop body to collect used variables
            for stmt in node.body:
                self.visit(stmt)

            # Check if loop variable is used in body
            if loop_var not in self.loop_body_vars and loop_var != "_":
                self.fixes.append(
                    {
                        "line": loop_line,
                        "old_var": loop_var,
                        "new_var": "_",
                        "type": "for_loop_tuple" if len(loop_vars) > 1 else "for_loop",
                        "is_tuple": len(loop_vars) > 1,
                    }
                )

        # Restore previous state
        self.current_loop_var = prev_loop_var
        self.current_loop_line = prev_loop_line
        self.loop_body_vars = prev_loop_body_vars
        self.in_loop_body = prev_in_loop_body

        # Continue visiting (for nested loops)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        """Track variable usage in loop body."""
        if self.in_loop_body and isinstance(node.ctx, ast.Load):
            self.loop_body_vars.add(node.id)
        self.generic_visit(node)


def analyze_file(file_path: Path) -> list[dict]:
    """Analyze a Python file for B007 errors."""
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        analyzer = LoopVariableAnalyzer()
        analyzer.visit(tree)

        return analyzer.fixes
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        return []


def apply_fixes(file_path: Path, fixes: list[dict], dry_run: bool = False) -> int:
    """Apply fixes to a file using line-based replacement."""
    if not fixes:
        return 0

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        changes_made = 0
        # Group fixes by line to handle multiple variables on same line
        fixes_by_line = {}
        for fix in fixes:
            line_num = fix["line"]
            if line_num not in fixes_by_line:
                fixes_by_line[line_num] = []
            fixes_by_line[line_num].append(fix)

        for line_num, line_fixes in fixes_by_line.items():
            line_idx = line_num - 1  # Convert to 0-based index
            if line_idx >= len(lines):
                continue

            line = lines[line_idx]
            new_line = line

            # Apply all fixes for this line
            for fix in line_fixes:
                old_var = fix["old_var"]
                new_var = fix["new_var"]

                # Handle tuple unpacking: for key, value in items()
                if fix.get("is_tuple", False):
                    # Replace variable in tuple context
                    # Pattern: "for key, value in" -> "for _, value in"
                    new_line = new_line.replace(f"{old_var},", f"{new_var},", 1)
                    new_line = new_line.replace(f", {old_var} in", f", {new_var} in", 1)
                # Simple loop variable
                # Pattern: "for <var> in" -> "for _ in"
                elif f"for {old_var} in" in new_line:
                    new_line = new_line.replace(
                        f"for {old_var} in", f"for {new_var} in", 1
                    )

            if new_line != line:
                lines[line_idx] = new_line
                changes_made += 1

        if changes_made > 0 and not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

        return changes_made
    except Exception as e:
        print(f"Error applying fixes to {file_path}: {e}", file=sys.stderr)
        return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/fix_b007_loop_variables.py [--dry-run] <files>")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    file_args = [arg for arg in sys.argv[1:] if arg != "--dry-run"]

    if not file_args:
        print("Error: No files specified")
        sys.exit(1)

    total_fixes = 0
    total_files = 0
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("B007 Loop Variable Fixes Report")
    report_lines.append("=" * 80)
    report_lines.append(f"Mode: {'DRY RUN' if dry_run else 'APPLY FIXES'}")
    report_lines.append("")

    for file_arg in file_args:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}", file=sys.stderr)
            continue

        if not file_path.suffix == ".py":
            continue

        fixes = analyze_file(file_path)
        if fixes:
            changes = apply_fixes(file_path, fixes, dry_run)
            if changes > 0:
                total_fixes += changes
                total_files += 1

                report_lines.append(f"File: {file_path}")
                report_lines.append(f"  Fixes: {changes}")
                for fix in fixes:
                    report_lines.append(
                        f"    Line {fix['line']}: {fix['old_var']} -> {fix['new_var']}"
                    )
                report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append(f"Total files changed: {total_files}")
    report_lines.append(f"Total fixes applied: {total_fixes}")
    report_lines.append("=" * 80)

    # Print report
    report = "\n".join(report_lines)
    print(report)

    # Save report to file
    if not dry_run and total_fixes > 0:
        report_file = Path("B007_FIXES_REPORT.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

    return 0 if total_fixes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
