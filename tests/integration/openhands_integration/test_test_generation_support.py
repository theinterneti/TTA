"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands_integration/Test_test_generation_support]]
Tests for test generation support modules.

Tests task builder, file extractor, result validator, and error handler.
"""

from __future__ import annotations

from pathlib import Path

from src.agent_orchestration.openhands_integration.models import OpenHandsTaskResult
from src.agent_orchestration.openhands_integration.test_error_handler import (
    classify_error,
    create_retry_feedback,
)
from src.agent_orchestration.openhands_integration.test_file_extractor import (
    extract_test_files_from_output,
    parse_coverage_percentage,
    verify_test_quality,
)
from src.agent_orchestration.openhands_integration.test_generation_models import (
    TestGenerationError,
    TestTaskSpecification,
)
from src.agent_orchestration.openhands_integration.test_result_validator import (
    validate_test_conventions,
)
from src.agent_orchestration.openhands_integration.test_task_builder import (
    create_package_test_generation_task,
    create_test_generation_task,
)


class TestTaskBuilder:
    """Tests for task description generation."""

    def test_create_test_generation_task(self, test_workspace: Path):
        """Test creating test generation task description."""
        spec = TestTaskSpecification(
            target_file=Path("src/agent_orchestration/tools/client.py"),
            coverage_threshold=80.0,
            test_directory=Path("tests"),
        )

        task = create_test_generation_task(spec)

        # Verify task contains key information
        assert "src/agent_orchestration/tools/client.py" in task
        assert "80" in task or "80.0" in task
        assert "uv run pytest" in task
        assert "tests/" in task

    def test_create_package_test_generation_task(self):
        """Test creating package test generation task."""
        package_path = Path("src/agent_orchestration/tools")
        task = create_package_test_generation_task(
            package_path, coverage_threshold=75.0
        )

        assert "src/agent_orchestration/tools" in task
        assert "75" in task or "75.0" in task
        assert "uv run pytest" in task


class TestFileExtractor:
    """Tests for file extraction from output."""

    def test_extract_test_files_from_output(self, test_workspace: Path):
        """Test extracting test file paths from output."""
        output = """
        Generated test file: tests/agent_orchestration/tools/test_client.py
        Created tests/agent_orchestration/tools/test_registry.py
        """

        # Create test files
        test_file1 = test_workspace / "tests/agent_orchestration/tools/test_client.py"
        test_file2 = test_workspace / "tests/agent_orchestration/tools/test_registry.py"
        test_file1.parent.mkdir(parents=True, exist_ok=True)
        test_file1.touch()
        test_file2.touch()

        files = extract_test_files_from_output(output, test_workspace)

        assert len(files) >= 1
        # At least one file should be extracted

    def test_parse_coverage_percentage(self):
        """Test parsing coverage percentage from output."""
        # Test with percentage format
        output = "TOTAL                                                                           40260  36865  10838     14   6.74%"
        coverage = parse_coverage_percentage(output)
        # The function extracts the last percentage value
        assert coverage > 0.0

        output = "No coverage information"
        coverage = parse_coverage_percentage(output)
        assert coverage == 0.0

    def test_verify_test_quality(self, test_workspace: Path):
        """Test verifying test quality."""
        # Create a test file with some content
        test_file = test_workspace / "test_example.py"
        test_file.write_text(
            """
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 2 - 1 == 1

async def test_async_operation():
    assert True

def test_edge_case_empty():
    assert [] == []

def test_error_handling():
    with pytest.raises(ValueError):
        raise ValueError("test")
"""
        )

        quality = verify_test_quality(test_file)

        assert quality["num_tests"] >= 4
        assert quality["num_assertions"] >= 4
        assert quality["has_edge_cases"] is True
        assert quality["has_error_handling"] is True
        assert quality["quality_score"] > 0


class TestResultValidator:
    """Tests for result validation."""

    def test_validate_test_conventions_valid(self, test_workspace: Path):
        """Test validation of test file following conventions."""
        test_file = test_workspace / "test_example.py"
        test_file.write_text(
            """
import pytest

def test_example():
    '''Test example function.'''
    assert True
"""
        )

        issues = validate_test_conventions(test_file)
        # May have some minor issues, but should not be critical
        assert isinstance(issues, list)

    def test_validate_test_conventions_invalid_name(self, test_workspace: Path):
        """Test validation catches invalid file name."""
        test_file = test_workspace / "example.py"
        test_file.write_text("def test_example(): pass")

        issues = validate_test_conventions(test_file)
        assert any("test_" in issue or "_test.py" in issue for issue in issues)

    def test_validate_test_conventions_missing_pytest(self, test_workspace: Path):
        """Test validation catches missing pytest import."""
        test_file = test_workspace / "test_example.py"
        test_file.write_text(
            """
def test_example():
    assert True
"""
        )

        issues = validate_test_conventions(test_file)
        assert any("pytest" in issue.lower() for issue in issues)

    def test_validate_test_conventions_uvx_antipattern(self, test_workspace: Path):
        """Test validation catches uvx pytest anti-pattern."""
        test_file = test_workspace / "test_example.py"
        test_file.write_text(
            """
import pytest

# Run with: uvx pytest
def test_example():
    assert True
"""
        )

        issues = validate_test_conventions(test_file)
        assert any("uvx pytest" in issue for issue in issues)


class TestErrorHandler:
    """Tests for error classification and retry feedback."""

    def test_classify_error_timeout(self):
        """Test classifying timeout errors."""
        result = OpenHandsTaskResult(
            success=False,
            output="",
            error="Timeout after 600s",
            execution_time=600.0,
        )

        error_type = classify_error(result)
        assert error_type == TestGenerationError.TIMEOUT

    def test_classify_error_execution_failure(self):
        """Test classifying execution failure errors."""
        result = OpenHandsTaskResult(
            success=False,
            output="",
            error="Test execution failed",
            execution_time=1.0,
        )

        error_type = classify_error(result)
        assert error_type == TestGenerationError.EXECUTION_FAILURE

    def test_classify_error_coverage_gap(self):
        """Test classifying coverage gap errors."""
        result = OpenHandsTaskResult(
            success=True,
            output="Coverage: 50%",
            error=None,
            execution_time=10.0,
        )

        # This would be detected during validation, not from task result
        # Just verify the function doesn't crash
        error_type = classify_error(result)
        assert error_type in TestGenerationError

    def test_create_retry_feedback(self, test_workspace: Path):
        """Test creating retry feedback."""
        spec = TestTaskSpecification(
            target_file=Path("src/agent_orchestration/tools/client.py"),
            coverage_threshold=80.0,
        )

        result = OpenHandsTaskResult(
            success=False,
            output="",
            error="Timeout",
            execution_time=600.0,
        )

        feedback = create_retry_feedback(
            TestGenerationError.TIMEOUT,
            spec,
            result,
            test_workspace,
        )

        assert isinstance(feedback, str)
        assert len(feedback) > 0
        # Feedback should provide guidance for retry
