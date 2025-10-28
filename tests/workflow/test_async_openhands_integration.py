"""
Tests for async OpenHands workflow integration (Phase 2).

Tests:
- AsyncOpenHandsTestGenerationStage task submission
- AsyncOpenHandsTestGenerationStage result collection
- WorkflowOrchestrator async workflow execution
- Parallel stage execution while OpenHands tasks run
- Performance measurement and timing instrumentation
- Error handling and graceful degradation
"""

import logging
from unittest.mock import AsyncMock, patch

import pytest

from scripts.workflow.openhands_stage import (
    AsyncOpenHandsStageResult,
    AsyncOpenHandsTestGenerationStage,
)
from scripts.workflow.spec_to_production import WorkflowOrchestrator, WorkflowResult

logger = logging.getLogger(__name__)


class TestAsyncOpenHandsStageResult:
    """Tests for AsyncOpenHandsStageResult dataclass."""

    def test_initialization(self):
        """Test result initialization."""
        result = AsyncOpenHandsStageResult()
        assert result.success is False  # Default is False until tasks complete
        assert result.submitted_tasks == {}
        assert result.completed_tasks == {}
        assert result.failed_tasks == {}
        assert result.errors == []
        assert result.total_execution_time_ms == 0.0

    def test_with_tasks(self):
        """Test result with tasks."""
        result = AsyncOpenHandsStageResult()
        result.submitted_tasks = {"module1.py": "task-123", "module2.py": "task-456"}
        result.completed_tasks = {"task-123": {"success": True}}
        result.failed_tasks = {"task-456": "Timeout"}
        result.total_execution_time_ms = 1500.0

        assert len(result.submitted_tasks) == 2
        assert len(result.completed_tasks) == 1
        assert len(result.failed_tasks) == 1
        assert result.total_execution_time_ms == 1500.0


class TestAsyncOpenHandsTestGenerationStage:
    """Tests for AsyncOpenHandsTestGenerationStage."""

    @pytest.fixture
    def component_path(self, tmp_path):
        """Create test component directory."""
        component = tmp_path / "test_component"
        component.mkdir()
        (component / "module1.py").write_text("def func1(): pass")
        (component / "module2.py").write_text("def func2(): pass")
        return component

    @pytest.fixture
    def stage(self, component_path):
        """Create async test stage."""
        return AsyncOpenHandsTestGenerationStage(
            component_path,
            config={"coverage_threshold": 80, "timeout_seconds": 60},
        )

    def test_initialization(self, stage, component_path):
        """Test stage initialization."""
        assert stage.component_path == component_path
        assert stage.coverage_threshold == 80
        assert stage.timeout == 60
        assert stage.poll_interval == 2.0
        assert stage.generator is None

    @pytest.mark.asyncio
    async def test_submit_tasks_mock(self, stage):
        """Test async task submission with mock generator."""
        # Mock the generator
        mock_generator = AsyncMock()
        mock_generator.start = AsyncMock()
        mock_generator.submit_test_generation_task = AsyncMock(
            side_effect=["task-1", "task-2"]
        )

        # Mock OpenHandsTestGenerator.from_env
        with patch(
            "scripts.workflow.openhands_stage.OpenHandsTestGenerator.from_env",
            return_value=mock_generator,
        ):
            result = await stage.submit_tasks()

            # Verify generator was started
            mock_generator.start.assert_called_once()

            # Verify tasks were submitted
            assert len(result.submitted_tasks) == 2
            assert "module1.py" in str(result.submitted_tasks)
            assert "module2.py" in str(result.submitted_tasks)
            assert result.success is True
            assert result.total_execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_collect_results_mock(self, stage):
        """Test async result collection with mock generator."""
        # Mock the generator
        mock_generator = AsyncMock()
        mock_generator.get_test_generation_results = AsyncMock(
            return_value={"success": True, "test_file": "test_module1.py"}
        )

        stage.generator = mock_generator

        submitted_tasks = {"module1.py": "task-1", "module2.py": "task-2"}
        result = await stage.collect_results(submitted_tasks)

        # Verify results were collected
        assert len(result.completed_tasks) == 2
        assert result.success is True
        assert result.total_execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_collect_results_with_failures(self, stage):
        """Test result collection with some failures."""
        # Mock the generator with mixed results
        mock_generator = AsyncMock()

        async def mock_get_results(task_id, **kwargs):
            if task_id == "task-1":
                return {"success": True, "test_file": "test_module1.py"}
            return {"success": False, "error": "Timeout"}

        mock_generator.get_test_generation_results = mock_get_results

        stage.generator = mock_generator

        submitted_tasks = {"module1.py": "task-1", "module2.py": "task-2"}
        result = await stage.collect_results(submitted_tasks)

        # Verify mixed results
        assert len(result.completed_tasks) == 1
        assert len(result.failed_tasks) == 1
        assert result.success is True  # Partial success is still success

    @pytest.mark.asyncio
    async def test_submit_tasks_no_modules(self, tmp_path):
        """Test task submission with no modules."""
        stage = AsyncOpenHandsTestGenerationStage(tmp_path)

        # Mock the generator to avoid starting real OpenHands
        mock_generator = AsyncMock()
        with patch(
            "scripts.workflow.openhands_stage.OpenHandsTestGenerator.from_env",
            return_value=mock_generator,
        ):
            result = await stage.submit_tasks()

            assert result.success is False
            assert len(result.errors) > 0
            assert "No Python modules found" in result.errors[0]


class TestWorkflowOrchestratorAsync:
    """Tests for WorkflowOrchestrator async methods."""

    @pytest.fixture
    def spec_file(self, tmp_path):
        """Create test specification file."""
        spec = tmp_path / "test_spec.md"
        spec.write_text(
            """
# Test Component Specification

## Overview
Test component for async workflow testing.

## Requirements
- Requirement 1
- Requirement 2
"""
        )
        return spec

    @pytest.fixture
    def component_path(self, tmp_path):
        """Create test component directory."""
        component = tmp_path / "test_component"
        component.mkdir()
        (component / "module1.py").write_text("def func1(): pass")
        return component

    @pytest.fixture
    def orchestrator(self, spec_file, component_path):
        """Create test orchestrator."""
        orchestrator = WorkflowOrchestrator(
            spec_file=spec_file,
            component_name="test_component",
            target_stage="development",
            config={"enable_openhands_test_generation": True},
        )
        # Override component_path for testing
        orchestrator.component_path = component_path
        return orchestrator

    @pytest.mark.asyncio
    async def test_run_async_openhands_test_generation_stage(self, orchestrator):
        """Test async OpenHands task submission."""
        # Mock the stage at the import location (inline import in the method)
        with patch(
            "scripts.workflow.openhands_stage.AsyncOpenHandsTestGenerationStage"
        ) as MockStage:
            mock_stage = AsyncMock()
            mock_result = AsyncOpenHandsStageResult()
            mock_result.success = True  # Set success to True
            mock_result.submitted_tasks = {"module1.py": "task-1"}
            mock_result.total_execution_time_ms = 100.0
            mock_stage.submit_tasks = AsyncMock(return_value=mock_result)
            MockStage.return_value = mock_stage

            (
                submitted_tasks,
                time_ms,
            ) = await orchestrator._run_async_openhands_test_generation_stage()

            assert len(submitted_tasks) == 1
            assert time_ms == 100.0

    @pytest.mark.asyncio
    async def test_collect_async_openhands_results(self, orchestrator):
        """Test async OpenHands result collection."""
        # Mock the stage at the import location (inline import in the method)
        with patch(
            "scripts.workflow.openhands_stage.AsyncOpenHandsTestGenerationStage"
        ) as MockStage:
            mock_stage = AsyncMock()
            mock_result = AsyncOpenHandsStageResult()
            mock_result.success = True  # Set success to True
            mock_result.completed_tasks = {"task-1": {"success": True}}
            mock_result.total_execution_time_ms = 500.0
            mock_stage.collect_results = AsyncMock(return_value=mock_result)
            MockStage.return_value = mock_stage

            submitted_tasks = {"module1.py": "task-1"}
            success, time_ms = await orchestrator._collect_async_openhands_results(
                submitted_tasks
            )

            assert success is True
            assert time_ms == 500.0


class TestPerformanceMeasurement:
    """Tests for performance measurement features."""

    def test_workflow_result_timing_fields(self):
        """Test WorkflowResult has timing fields."""
        result = WorkflowResult(
            success=True,
            component_name="test",
            target_stage="development",
            execution_mode="async",
        )

        assert result.execution_mode == "async"
        assert result.stage_timings == {}
        assert result.openhands_submission_time_ms == 0.0
        assert result.openhands_collection_time_ms == 0.0

    def test_workflow_result_with_timings(self):
        """Test WorkflowResult with timing data."""
        result = WorkflowResult(
            success=True,
            component_name="test",
            target_stage="development",
            execution_mode="async",
        )

        result.stage_timings = {
            "specification": 100.0,
            "testing": 500.0,
            "openhands_submission": 50.0,
            "refactoring": 300.0,
            "openhands_collection": 1000.0,
        }
        result.openhands_submission_time_ms = 50.0
        result.openhands_collection_time_ms = 1000.0

        assert len(result.stage_timings) == 5
        assert result.openhands_submission_time_ms == 50.0
        assert result.openhands_collection_time_ms == 1000.0
