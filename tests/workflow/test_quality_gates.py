"""
Unit tests for quality gate validators.

Tests the InstructionsValidationGate and other quality gates.
"""

import sys
from pathlib import Path

import pytest

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.workflow.quality_gates import (
    InstructionsValidationGate,
)


class TestInstructionsValidationGate:
    """Tests for InstructionsValidationGate."""

    @pytest.fixture
    def temp_instructions_dir(self, tmp_path):
        """Create temporary instructions directory."""
        instructions_dir = tmp_path / ".augment" / "instructions"
        instructions_dir.mkdir(parents=True)
        return instructions_dir

    def test_validate_valid_instruction_file(self, temp_instructions_dir):
        """Test validation passes for valid instruction file."""
        # Create valid instruction file
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo: "**/*.py"
description: "Test instructions"
---
# Test Instructions

## Section 1

Content here.

## Section 2

More content.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is True
        assert result.gate_name == "instructions_validation"
        assert len(result.errors) == 0
        assert result.details["file_count"] == 1
        assert "test.instructions.md" in result.details["validated_files"]

    def test_validate_missing_frontmatter(self, temp_instructions_dir):
        """Test validation fails for missing frontmatter."""
        # Create instruction file without frontmatter
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """# Test Instructions

No frontmatter here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert len(result.errors) > 0
        assert any(
            "Missing or invalid YAML frontmatter" in error for error in result.errors
        )

    def test_validate_missing_apply_to(self, temp_instructions_dir):
        """Test validation fails for missing applyTo field."""
        # Create instruction file without applyTo
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
description: "Test instructions"
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "Missing required field 'applyTo'" in error for error in result.errors
        )

    def test_validate_missing_description(self, temp_instructions_dir):
        """Test validation fails for missing description field."""
        # Create instruction file without description
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo: "**/*.py"
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "Missing required field 'description'" in error for error in result.errors
        )

    def test_validate_invalid_apply_to_type(self, temp_instructions_dir):
        """Test validation fails for invalid applyTo type."""
        # Create instruction file with invalid applyTo type
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo: 123
description: "Test instructions"
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "'applyTo' must be string or list of strings" in error
            for error in result.errors
        )

    def test_validate_empty_description(self, temp_instructions_dir):
        """Test validation fails for empty description."""
        # Create instruction file with empty description
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo: "**/*.py"
description: ""
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "'description' must be non-empty string" in error for error in result.errors
        )

    def test_validate_apply_to_list(self, temp_instructions_dir):
        """Test validation passes for applyTo as list."""
        # Create instruction file with applyTo as list
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo:
  - "src/**/*.py"
  - "tests/**/*.py"
description: "Test instructions"
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_invalid_apply_to_list_items(self, temp_instructions_dir):
        """Test validation fails for invalid items in applyTo list."""
        # Create instruction file with invalid applyTo list items
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo:
  - "src/**/*.py"
  - 123
description: "Test instructions"
---
# Test Instructions

Content here.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "All items in 'applyTo' list must be strings" in error
            for error in result.errors
        )

    def test_validate_content_warnings(self, temp_instructions_dir):
        """Test content validation generates warnings."""
        # Create instruction file with minimal content
        instruction_file = temp_instructions_dir / "test.instructions.md"
        instruction_file.write_text(
            """---
applyTo: "**/*.py"
description: "Test instructions"
---
Short content.
"""
        )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        # Should pass (warnings don't fail validation)
        assert result.passed is True
        # Should have warnings about structure
        assert len(result.warnings) > 0

    def test_validate_no_instruction_files(self, temp_instructions_dir):
        """Test validation passes with warning when no instruction files found."""
        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is True
        assert result.details["file_count"] == 0
        assert any(
            "No instruction files found" in warning for warning in result.warnings
        )

    def test_validate_instructions_dir_not_found(self, tmp_path):
        """Test validation fails when instructions directory doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        gate = InstructionsValidationGate(instructions_dir=str(nonexistent_dir))
        result = gate.validate()

        assert result.passed is False
        assert any(
            "Instructions directory not found" in error for error in result.errors
        )

    def test_validate_multiple_files(self, temp_instructions_dir):
        """Test validation handles multiple instruction files."""
        # Create multiple valid instruction files
        for i in range(3):
            instruction_file = temp_instructions_dir / f"test{i}.instructions.md"
            instruction_file.write_text(
                f"""---
applyTo: "**/*.py"
description: "Test instructions {i}"
---
# Test Instructions {i}

## Section 1

Content here.
"""
            )

        gate = InstructionsValidationGate(instructions_dir=str(temp_instructions_dir))
        result = gate.validate()

        assert result.passed is True
        assert result.details["file_count"] == 3
        assert len(result.details["validated_files"]) == 3
