"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/Test_primitives]]
Unit tests for OpenHands workflow primitives.

Tests:
- ModelSelectionPrimitive
- TaskExecutionPrimitive
- ResultValidationPrimitive
- MetricsRecordingPrimitive
- Primitive composition
"""

from unittest.mock import AsyncMock, Mock

import pytest
from tta_dev_primitives.core.base import WorkflowContext

from .adapter import OpenHandsAdapter
from .metrics_collector import ExecutionMetrics, MetricsCollector
from .model_selector import (
    ModelCapability,
    ModelSelector,
    ModelSpecialization,
    TaskCategory,
    TaskRequirements,
)
from .primitives import (
    MetricsRecordingPrimitive,
    ModelSelectionPrimitive,
    OpenHandsTaskInput,
    OpenHandsTaskOutput,
    ResultValidationPrimitive,
    TaskExecutionPrimitive,
)
from .result_validator import ResultValidator, ValidationResult


@pytest.fixture
def model_selector():
    """Create a ModelSelector instance."""
    return ModelSelector()


@pytest.fixture
def mock_adapter():
    """Create a mock OpenHandsAdapter."""
    adapter = Mock(spec=OpenHandsAdapter)
    adapter.execute_development_task = AsyncMock(
        return_value={
            "content": "def test_example():\n    assert True\n",
            "output_file": "test_example.py",
        }
    )
    return adapter


@pytest.fixture
def result_validator():
    """Create a ResultValidator instance."""
    return ResultValidator()


@pytest.fixture
def metrics_collector():
    """Create a MetricsCollector instance."""
    return MetricsCollector()


@pytest.fixture
def workflow_context():
    """Create a WorkflowContext instance."""
    return WorkflowContext(workflow_id="test-wf-001", session_id="test-session-001")


@pytest.mark.asyncio
async def test_model_selection_primitive(model_selector, workflow_context):
    """Test ModelSelectionPrimitive."""
    primitive = ModelSelectionPrimitive(model_selector)

    task_input = OpenHandsTaskInput(
        task_id="test-001",
        task_type="unit_test",
        description="Generate tests for auth.py",
        requirements=TaskRequirements(
            category=TaskCategory.UNIT_TEST,
            complexity="moderate",
            quality_threshold=0.8,
        ),
    )

    output = await primitive.execute(task_input, workflow_context)

    assert output.success is True
    assert output.model is not None
    assert output.model.model_id in model_selector.models
    assert "selected_model" in workflow_context.state
    assert "requirements" in workflow_context.state


@pytest.mark.asyncio
async def test_model_selection_primitive_default_requirements(
    model_selector, workflow_context
):
    """Test ModelSelectionPrimitive with default requirements."""
    primitive = ModelSelectionPrimitive(model_selector)

    task_input = OpenHandsTaskInput(
        task_id="test-002",
        task_type="unit_test",
        description="Generate tests for auth.py",
        # No requirements provided
    )

    output = await primitive.execute(task_input, workflow_context)

    assert output.success is True
    assert output.model is not None


@pytest.mark.asyncio
async def test_task_execution_primitive(mock_adapter, workflow_context):
    """Test TaskExecutionPrimitive."""
    primitive = TaskExecutionPrimitive(mock_adapter)

    # Simulate input from ModelSelectionPrimitive
    task_output = OpenHandsTaskOutput(
        task_id="test-001",
        task_type="unit_test",
        model=ModelCapability(
            model_id="test-model",
            name="Test Model",
            specialization=ModelSpecialization.BALANCED,
            avg_latency_ms=1000,
            quality_score=4.5,
            success_rate=0.95,
            cost_per_1k_tokens=0.1,
            max_tokens=4000,
            supported_categories=[TaskCategory.UNIT_TEST],
        ),
        success=True,
    )

    # Set task description in context
    workflow_context.state["task_description"] = "Generate tests for auth.py"

    output = await primitive.execute(task_output, workflow_context)

    assert output.success is True
    assert output.result is not None
    assert "content" in output.result
    assert "execution_result" in workflow_context.state
    assert "execution_duration_ms" in workflow_context.state


@pytest.mark.asyncio
async def test_result_validation_primitive(result_validator, workflow_context):
    """Test ResultValidationPrimitive."""
    primitive = ResultValidationPrimitive(result_validator)

    # Simulate input from TaskExecutionPrimitive
    task_output = OpenHandsTaskOutput(
        task_id="test-001",
        task_type="unit_test",
        model=ModelCapability(
            model_id="test-model",
            name="Test Model",
            specialization=ModelSpecialization.BALANCED,
            avg_latency_ms=1000,
            quality_score=4.5,
            success_rate=0.95,
            cost_per_1k_tokens=0.1,
            max_tokens=4000,
            supported_categories=[TaskCategory.UNIT_TEST],
        ),
        result={
            "content": "def test_example():\n    assert True\n" * 10,
            "output_file": "test_example.py",
        },
        success=True,
    )

    output = await primitive.execute(task_output, workflow_context)

    assert output.validation is not None
    assert isinstance(output.validation, ValidationResult)
    assert "validation_result" in workflow_context.state


@pytest.mark.asyncio
async def test_metrics_recording_primitive(metrics_collector, workflow_context):
    """Test MetricsRecordingPrimitive."""
    primitive = MetricsRecordingPrimitive(metrics_collector)

    # Simulate input from ResultValidationPrimitive
    task_output = OpenHandsTaskOutput(
        task_id="test-001",
        task_type="unit_test",
        model=ModelCapability(
            model_id="test-model",
            name="Test Model",
            specialization=ModelSpecialization.BALANCED,
            avg_latency_ms=1000,
            quality_score=4.5,
            success_rate=0.95,
            cost_per_1k_tokens=0.1,
            max_tokens=4000,
            supported_categories=[TaskCategory.UNIT_TEST],
        ),
        result={"content": "def test_example():\n    assert True\n"},
        validation=ValidationResult(
            passed=True,
            errors=[],
            warnings=[],
            details={},
            score=0.9,
        ),
        success=True,
    )

    # Set execution duration in context
    workflow_context.state["execution_duration_ms"] = 1500.0

    output = await primitive.execute(task_output, workflow_context)

    assert output.metrics is not None
    assert isinstance(output.metrics, ExecutionMetrics)
    assert "recorded_metrics" in workflow_context.state
    assert len(metrics_collector.executions) == 1


@pytest.mark.asyncio
async def test_primitive_composition(
    model_selector, mock_adapter, result_validator, metrics_collector, workflow_context
):
    """Test composing all primitives together."""
    # Compose workflow using >> operator
    workflow = (
        ModelSelectionPrimitive(model_selector)
        >> TaskExecutionPrimitive(mock_adapter)
        >> ResultValidationPrimitive(result_validator)
        >> MetricsRecordingPrimitive(metrics_collector)
    )

    task_input = OpenHandsTaskInput(
        task_id="test-001",
        task_type="unit_test",
        description="Generate tests for auth.py",
        requirements=TaskRequirements(
            category=TaskCategory.UNIT_TEST,
            complexity="moderate",
            quality_threshold=0.8,
        ),
    )

    # Set task description in context for TaskExecutionPrimitive
    workflow_context.state["task_description"] = task_input.description

    output = await workflow.execute(task_input, workflow_context)

    # Verify final output
    assert output.task_id == "test-001"
    assert output.model is not None
    assert output.result is not None
    assert output.validation is not None
    assert output.metrics is not None

    # Verify context state
    assert "selected_model" in workflow_context.state
    assert "execution_result" in workflow_context.state
    assert "validation_result" in workflow_context.state
    assert "recorded_metrics" in workflow_context.state

    # Verify metrics were recorded
    assert len(metrics_collector.executions) == 1


@pytest.mark.asyncio
async def test_primitive_error_propagation(model_selector, workflow_context):
    """Test that errors propagate correctly through primitives."""
    # Create a primitive that will fail
    primitive = ModelSelectionPrimitive(model_selector)

    task_input = OpenHandsTaskInput(
        task_id="test-001",
        task_type="unknown_type",
        description="Unknown task",
        requirements=TaskRequirements(
            category=TaskCategory.CODE_GENERATION,
            complexity="complex",
            quality_threshold=1.0,  # Impossible threshold
            max_latency_ms=1,  # Impossible latency
        ),
    )

    output = await primitive.execute(task_input, workflow_context)

    # Should fail gracefully
    assert output.success is False
    assert output.error is not None
