#!/usr/bin/env python3
# ruff: noqa: ALL
"""Validate YAML frontmatter in agentic primitive files.

This script validates that all agentic primitive files (.github/instructions/,
.github/chatmodes/, .github/prompts/, .github/specs/) have valid YAML frontmatter
that conforms to their respective schemas.

Usage:
    python scripts/validate-agentic-frontmatter.py

Exit codes:
    0: All validations passed
    1: One or more validations failed
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

try:
    import yamale
except ImportError:
    print("❌ Error: yamale is not installed. Run: uv add --dev yamale")
    sys.exit(1)


def extract_frontmatter(file_path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary of frontmatter data, or None if no frontmatter found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

    # Check for YAML frontmatter
    if not content.startswith("---\n"):
        return None

    # Find second ---
    end_idx = content.find("\n---\n", 4)
    if end_idx == -1:
        # Try alternative ending (--- at end of line)
        end_idx = content.find("\n---", 4)
        if end_idx == -1:
            return None

    frontmatter_text = content[4:end_idx]

    try:
        return yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in {file_path}: {e}")
        return None


def validate_file(file_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    """Validate a file's frontmatter against schema.

    Args:
        file_path: Path to file to validate
        schema_path: Path to Yamale schema file

    Returns:
        Tuple of (success: bool, errors: list[str])
    """
    frontmatter = extract_frontmatter(file_path)
    if frontmatter is None:
        return False, [f"No valid YAML frontmatter found in {file_path.name}"]

    # Create temporary YAML file for validation
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        yaml.dump(frontmatter, temp_file)
        temp_path = Path(temp_file.name)

    try:
        schema = yamale.make_schema(str(schema_path))
        data = yamale.make_data(str(temp_path))
        yamale.validate(schema, data)
        return True, []
    except yamale.YamaleError as e:
        errors = []
        for result in e.results:
            for error in result.errors:
                errors.append(f"{file_path.name}: {error}")
        return False, errors
    except Exception as e:
        return False, [f"{file_path.name}: Unexpected error: {e}"]
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    """Main validation function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    root = Path(__file__).parent.parent
    schemas_dir = root / ".github" / "schemas"

    # Define file patterns and their schemas
    validations = [
        (".github/instructions/*.instructions.md", "instruction.schema.yaml"),
        (".github/chatmodes/*.chatmode.md", "chatmode.schema.yaml"),
        (".github/prompts/*.prompt.md", "prompt.schema.yaml"),
        (".github/specs/*.spec.md", "spec.schema.yaml"),
    ]

    print("🔍 Validating Agentic Primitives Frontmatter...")
    print("")

    all_passed = True
    total_files = 0
    passed_files = 0

    for pattern, schema_name in validations:
        schema_path = schemas_dir / schema_name

        if not schema_path.exists():
            print(f"⚠️  Warning: Schema not found: {schema_name}")
            continue

        # Get all matching files
        files = list(root.glob(pattern))

        if not files:
            print(f"ℹ️  No files found matching: {pattern}")
            continue

        print(f"📄 Validating {len(files)} file(s) with {schema_name}:")

        for file_path in sorted(files):
            total_files += 1
            passed, errors = validate_file(file_path, schema_path)

            if passed:
                print(f"  ✅ {file_path.name}")
                passed_files += 1
            else:
                all_passed = False
                print(f"  ❌ {file_path.name}")
                for error in errors:
                    print(f"     {error}")

        print("")

    # Print summary
    print("=" * 60)
    print(f"📊 Validation Summary: {passed_files}/{total_files} files passed")
    print("=" * 60)

    if all_passed:
        print("✅ All agentic primitives frontmatter validation passed!")
        return 0
    print("❌ Some agentic primitives frontmatter validation failed")
    print("")
    print("💡 Tips:")
    print("  - Check that all required fields are present")
    print("  - Verify field values match allowed enums")
    print("  - Ensure YAML syntax is correct")
    print("  - Review schema files in .github/schemas/")
    return 1


if __name__ == "__main__":
    sys.exit(main())
