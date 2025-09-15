#!/usr/bin/env python3
"""
Script to automatically fix B904 exception chaining issues.
This script adds proper 'from e' or 'from None' to raise statements in except blocks.
"""

import re
import sys
from pathlib import Path


def fix_b904_in_file(file_path: Path) -> int:
    """Fix B904 issues in a single file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        fixes_applied = 0

        # Pattern to match raise statements in except blocks that need chaining
        # This is a simplified approach - we'll be conservative and only fix obvious cases

        # We'll use a more targeted approach - look for specific patterns
        lines = content.split('\n')
        modified_lines = []
        in_except_block = False
        except_var = None

        for _i, line in enumerate(lines):
            # Check if we're entering an except block
            except_match = re.match(r'(\s*)except\s+\w+\s+as\s+(\w+):', line)
            if except_match:
                in_except_block = True
                except_var = except_match.group(2)
                modified_lines.append(line)
                continue

            # Check if we're leaving the except block (dedent)
            if in_except_block and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                in_except_block = False
                except_var = None

            # Fix raise statements in except blocks
            if in_except_block and 'raise ' in line and ' from ' not in line:
                # Only fix if the exception variable is referenced in the raise
                if except_var and except_var in line:
                    if not line.rstrip().endswith(f' from {except_var}'):
                        line = line.rstrip() + f' from {except_var}'
                        fixes_applied += 1
                # Or if it's a generic error that should chain
                elif re.search(r'raise\s+\w*Error\(', line):
                    if not line.rstrip().endswith(' from e') and not line.rstrip().endswith(' from None'):
                        # Be conservative - only add 'from e' if 'e' is the exception variable
                        if except_var == 'e':
                            line = line.rstrip() + ' from e'
                            fixes_applied += 1

            modified_lines.append(line)

        if fixes_applied > 0:
            new_content = '\n'.join(modified_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {fixes_applied} B904 issues in {file_path}")

        return fixes_applied

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to fix B904 issues across the codebase."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("src directory not found")
        return 1

    total_fixes = 0
    files_processed = 0

    # Process all Python files in src/
    for py_file in src_dir.rglob("*.py"):
        if py_file.is_file():
            fixes = fix_b904_in_file(py_file)
            total_fixes += fixes
            files_processed += 1

    print(f"\nProcessed {files_processed} files")
    print(f"Applied {total_fixes} B904 fixes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
