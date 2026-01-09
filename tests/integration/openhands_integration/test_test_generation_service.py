"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands_integration/Test_test_generation_service]]
Tests for UnitTestGenerationService.

Tests test generation workflow, iterative feedback, validation, and error handling.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.agent_orchestration.openhands_integration.client import OpenHandsClient
from src.agent_orchestration.openhands_integration.config import OpenHandsConfig
from src.agent_orchestration.openhands_integration.models import OpenHandsTaskResult
from src.agent_orchestration.openhands_integration.test_generation_models import (
    TestGenerationError,
    TestTaskSpecification,
    TestValidationResult,
)
from src.agent_orchestration.openhands_integration.test_generation_service import (
    UnitTestGenerationService,
)


@pytest.fixture
def test_spec(test_workspace: Path) -> TestTaskSpecification:
    """Create test specification."""
    return TestTaskSpecification(
        target_file=Path("src/agent_orchestration/tools/client.py"),
        coverage_threshold=70.0,
        test_directory=Path("tests"),
        timeout_seconds=300.0,
    )


@pytest.fixture
def mock_validation_result() -> TestValidationResult:
    """Create mock validation result."""
    return TestValidationResult(
        syntax_valid=True,
        conventions_followed=True,
        tests_pass=True,
        coverage_percentage=75.0,
        issues=[],
    )


class TestServiceInitialization:
    """Tests for service initialization."""

    def test_service_initialization(self, openhands_config: OpenHandsConfig):
        """Test service initialization."""
        service = UnitTestGenerationService(openhands_config)

        assert service.config == openhands_config
        assert isinstance(service.client, OpenHandsClient)
        assert service.workspace_path == openhands_config.workspace_path


class TestGenerateTests:
    """Tests for generate_tests method."""

    @pytest.mark.asyncio
    async def test_generate_tests_success(
        self,
        openhands_config: OpenHandsConfig,
        test_spec: TestTaskSpecification,
        mock_validation_result: TestValidationResult,
    ):
        """Test successful test generation."""
        service = UnitTestGenerationService(openhands_config)

        # Mock client execution
        with patch.object(
            OpenHandsClient, "execute_task", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="Generated test file: tests/agent_orchestration/tools/test_client.py\nCoverage: 75%",
                error=None,
                execution_time=10.0,
            )

            # Mock file extraction
            with patch(
                "src.agent_orchestration.openhands_integration.test_generation_service.extract_test_files_from_output"
            ) as mock_extract:
                mock_extract.return_value = [
                    Path("tests/agent_orchestration/tools/test_client.py")
                ]

                # Mock validation
                with patch(
                    "src.agent_orchestration.openhands_integration.test_generation_service.validate_generated_tests",
                    new_callable=AsyncMock,
                ) as mock_validate:
                    mock_validate.return_value = mock_validation_result

                    result = await service.generate_tests(test_spec, max_iterations=5)

                    assert result.syntax_valid is True
                    assert result.tests_pass is True
                    assert result.coverage_percentage == 75.0
                    mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tests_with_retry(
        self,
        openhands_config: OpenHandsConfig,
        test_spec: TestTaskSpecification,
    ):
        """Test test generation with iterative feedback."""
        service = UnitTestGenerationService(openhands_config)

        # First attempt: validation fails
        failed_validation = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=False,
            coverage_percentage=50.0,
            issues=["Coverage below threshold"],
        )

        # Second attempt: validation succeeds
        success_validation = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=True,
            coverage_percentage=75.0,
            issues=[],
        )

        with patch.object(
            OpenHandsClient, "execute_task", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="Generated test file: tests/agent_orchestration/tools/test_client.py",
                error=None,
                execution_time=10.0,
            )

            with patch(
                "src.agent_orchestration.openhands_integration.test_generation_service.extract_test_files_from_output"
            ) as mock_extract:
                mock_extract.return_value = [
                    Path("tests/agent_orchestration/tools/test_client.py")
                ]

                with patch(
                    "src.agent_orchestration.openhands_integration.test_generation_service.validate_generated_tests",
                    new_callable=AsyncMock,
                ) as mock_validate:
                    # First call fails, second succeeds
                    mock_validate.side_effect = [failed_validation, success_validation]

                    with patch.object(
                        service, "_create_feedback_task"
                    ) as mock_feedback:
                        mock_feedback.return_value = "Please improve coverage"

                        result = await service.generate_tests(
                            test_spec, max_iterations=5
                        )

                        # Should succeed after retry
                        assert result.coverage_percentage == 75.0
                        assert mock_execute.call_count == 2
                        mock_feedback.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tests_max_iterations(
        self,
        openhands_config: OpenHandsConfig,
        test_spec: TestTaskSpecification,
    ):
        """Test max iterations limit."""
        service = UnitTestGenerationService(openhands_config)

        # Always fail validation
        failed_validation = TestValidationResult(
            syntax_valid=True,
            conventions_followed=True,
            tests_pass=False,
            coverage_percentage=50.0,
            issues=["Coverage below threshold"],
        )

        with patch.object(
            OpenHandsClient, "execute_task", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = OpenHandsTaskResult(
                success=True,
                output="Generated test file: tests/agent_orchestration/tools/test_client.py",
                error=None,
                execution_time=10.0,
            )

            with patch(
                "src.agent_orchestration.openhands_integration.test_generation_service.extract_test_files_from_output"
            ) as mock_extract:
                mock_extract.return_value = [
                    Path("tests/agent_orchestration/tools/test_client.py")
                ]

                with patch(
                    "src.agent_orchestration.openhands_integration.test_generation_service.validate_generated_tests",
                    new_callable=AsyncMock,
                ) as mock_validate:
                    mock_validate.return_value = failed_validation

                    result = await service.generate_tests(test_spec, max_iterations=3)

                    # Should stop after max iterations
                    assert mock_execute.call_count == 3
                    assert result.coverage_percentage == 50.0

    @pytest.mark.asyncio
    async def test_generate_tests_task_execution_failure(
        self,
        openhands_config: OpenHandsConfig,
        test_spec: TestTaskSpecification,
    ):
        """Test handling of task execution failure."""
        service = UnitTestGenerationService(openhands_config)

        with patch.object(
            OpenHandsClient, "execute_task", new_callable=AsyncMock
        ) as mock_execute:
            # Task execution fails
            mock_execute.return_value = OpenHandsTaskResult(
                success=False,
                output="",
                error="SDK error",
                execution_time=1.0,
            )

            with patch(
                "src.agent_orchestration.openhands_integration.test_generation_service.classify_error"
            ) as mock_classify:
                mock_classify.return_value = TestGenerationError.EXECUTION_FAILURE

                with patch(
                    "src.agent_orchestration.openhands_integration.test_generation_service.create_retry_feedback"
                ) as mock_feedback:
                    mock_feedback.return_value = "Retry with different approach"

                    # Should retry with feedback and return failure result after max iterations
                    result = await service.generate_tests(test_spec, max_iterations=2)

                    # Should have retried twice
                    assert mock_execute.call_count == 2
                    mock_classify.assert_called()

                    # Result should indicate failure
                    assert result.syntax_valid is False
                    assert result.tests_pass is False
                    assert "All iterations failed" in result.issues[0]