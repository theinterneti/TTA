"""
Workflow primitives for OpenHands integration.

Provides composable workflow primitives that wrap OpenHands-specific functionality
following TTA's workflow primitive system.

Primitives:
- ModelSelectionPrimitive: Selects optimal model for task
- TaskExecutionPrimitive: Executes task via OpenHands adapter
- ResultValidationPrimitive: Validates task results
- MetricsRecordingPrimitive: Records execution metrics

Example:
    ```python
    from tta_workflow_primitives import WorkflowContext
    from .primitives import (
        ModelSelectionPrimitive,
        TaskExecutionPrimitive,
        ResultValidationPrimitive,
        MetricsRecordingPrimitive,
    )

    # Compose workflow
    workflow = (
        ModelSelectionPrimitive(model_selector)
        >> TaskExecutionPrimitive(adapter)
        >> ResultValidationPrimitive(validator)
        >> MetricsRecordingPrimitive(metrics_collector)
    )

    # Execute
    context = WorkflowContext(workflow_id="test-gen-001", session_id="session-123")
    result = await workflow.execute(task_input, context)
    ```
"""

from __future__ import annotations

import logging
import time
from typing import Any

from pydantic import BaseModel, Field
from tta_workflow_primitives import WorkflowContext, WorkflowPrimitive

from .adapter import OpenHandsAdapter
from .metrics_collector import ExecutionMetrics, MetricsCollector
from .model_selector import (
    ModelCapability,
    ModelSelector,
    TaskCategory,
    TaskRequirements,
)
from .result_validator import ResultValidator, ValidationResult

logger = logging.getLogger(__name__)


class OpenHandsTaskInput(BaseModel):
    """Input data for OpenHands task execution."""

    task_id: str
    task_type: str
    description: str
    requirements: TaskRequirements | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class OpenHandsTaskOutput(BaseModel):
    """Output data from OpenHands task execution."""

    task_id: str
    task_type: str
    model: ModelCapability | None = None
    result: dict[str, Any] | None = None
    validation: ValidationResult | None = None
    metrics: ExecutionMetrics | None = None
    success: bool = False
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True


class ModelSelectionPrimitive(
    WorkflowPrimitive[OpenHandsTaskInput, OpenHandsTaskOutput]
):
    """
    Primitive for selecting optimal model for task.

    Wraps ModelSelector.select_model() in a composable workflow primitive.

    Example:
        ```python
        selector = ModelSelector()
        primitive = ModelSelectionPrimitive(selector)

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

        context = WorkflowContext(workflow_id="wf-001")
        output = await primitive.execute(task_input, context)
        ```
    """

    def __init__(self, model_selector: ModelSelector):
        """
        Initialize model selection primitive.

        Args:
            model_selector: ModelSelector instance
        """
        self.model_selector = model_selector

    async def execute(
        self, input_data: OpenHandsTaskInput, context: WorkflowContext
    ) -> OpenHandsTaskOutput:
        """
        Execute model selection.

        Args:
            input_data: Task input with requirements
            context: Workflow context

        Returns:
            Task output with selected model

        Raises:
            RuntimeError: If no suitable model found
        """
        logger.info(
            f"[ModelSelection] task_id={input_data.task_id}, "
            f"type={input_data.task_type}, workflow_id={context.workflow_id}"
        )

        try:
            # Use provided requirements or create default
            requirements = input_data.requirements
            if not requirements:
                category = TaskCategory.CODE_GENERATION
                if "test" in input_data.task_type.lower():
                    category = TaskCategory.UNIT_TEST
                elif "refactor" in input_data.task_type.lower():
                    category = TaskCategory.REFACTORING
                elif "doc" in input_data.task_type.lower():
                    category = TaskCategory.DOCUMENTATION

                requirements = TaskRequirements(
                    category=category,
                    complexity=input_data.metadata.get("complexity", "moderate"),
                    quality_threshold=input_data.metadata.get("quality_threshold", 0.7),
                )

            # Select model
            model = self.model_selector.select_model(requirements)
            if not model:
                raise RuntimeError(
                    f"No suitable model found for {input_data.task_type} "
                    f"with requirements: {requirements}"
                )

            # Store model in context for downstream primitives
            context.state["selected_model"] = model
            context.state["requirements"] = requirements

            logger.info(
                f"[ModelSelection] Selected {model.name} for {input_data.task_type}"
            )

            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=model,
                success=True,
            )

        except Exception as e:
            logger.error(f"[ModelSelection] Error: {e}", exc_info=True)
            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                success=False,
                error=str(e),
            )


class TaskExecutionPrimitive(
    WorkflowPrimitive[OpenHandsTaskOutput, OpenHandsTaskOutput]
):
    """
    Primitive for executing task via OpenHands adapter.

    Wraps OpenHandsAdapter.execute_development_task() in a composable workflow primitive.

    Example:
        ```python
        adapter = OpenHandsAdapter(client=openhands_client)
        primitive = TaskExecutionPrimitive(adapter)

        # Input from ModelSelectionPrimitive
        task_output = OpenHandsTaskOutput(
            task_id="test-001",
            task_type="unit_test",
            model=selected_model,
            success=True,
        )

        context = WorkflowContext(workflow_id="wf-001")
        context.state["selected_model"] = selected_model

        output = await primitive.execute(task_output, context)
        ```
    """

    def __init__(self, adapter: OpenHandsAdapter):
        """
        Initialize task execution primitive.

        Args:
            adapter: OpenHandsAdapter instance
        """
        self.adapter = adapter

    async def execute(
        self, input_data: OpenHandsTaskOutput, context: WorkflowContext
    ) -> OpenHandsTaskOutput:
        """
        Execute task via adapter.

        Args:
            input_data: Task output from previous primitive (with model selected)
            context: Workflow context

        Returns:
            Task output with execution result

        Raises:
            RuntimeError: If execution fails
        """
        logger.info(
            f"[TaskExecution] task_id={input_data.task_id}, "
            f"model={input_data.model.name if input_data.model else 'unknown'}, "
            f"workflow_id={context.workflow_id}"
        )

        # Check if previous primitive failed
        if not input_data.success:
            logger.warning(
                f"[TaskExecution] Skipping execution due to previous failure: "
                f"{input_data.error}"
            )
            return input_data

        try:
            start_time = time.time()

            # Get task description from context or input
            description = context.state.get("task_description", "")
            if not description:
                # Fallback: try to reconstruct from input
                description = f"Task type: {input_data.task_type}"

            # Execute task
            result = await self.adapter.execute_development_task(description)

            duration_ms = (time.time() - start_time) * 1000

            # Store result in context
            context.state["execution_result"] = result
            context.state["execution_duration_ms"] = duration_ms

            logger.info(
                f"[TaskExecution] Completed in {duration_ms:.0f}ms, "
                f"task_id={input_data.task_id}"
            )

            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=input_data.model,
                result=result,
                success=True,
            )

        except Exception as e:
            logger.error(f"[TaskExecution] Error: {e}", exc_info=True)
            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=input_data.model,
                success=False,
                error=str(e),
            )


class ResultValidationPrimitive(
    WorkflowPrimitive[OpenHandsTaskOutput, OpenHandsTaskOutput]
):
    """
    Primitive for validating task results.

    Wraps ResultValidator.validate() in a composable workflow primitive.

    Example:
        ```python
        validator = ResultValidator()
        primitive = ResultValidationPrimitive(validator)

        # Input from TaskExecutionPrimitive
        task_output = OpenHandsTaskOutput(
            task_id="test-001",
            task_type="unit_test",
            model=selected_model,
            result={"content": "test code..."},
            success=True,
        )

        context = WorkflowContext(workflow_id="wf-001")
        output = await primitive.execute(task_output, context)
        ```
    """

    def __init__(self, validator: ResultValidator):
        """
        Initialize result validation primitive.

        Args:
            validator: ResultValidator instance
        """
        self.validator = validator

    async def execute(
        self, input_data: OpenHandsTaskOutput, context: WorkflowContext
    ) -> OpenHandsTaskOutput:
        """
        Validate task result.

        Args:
            input_data: Task output from previous primitive (with execution result)
            context: Workflow context

        Returns:
            Task output with validation result

        Raises:
            RuntimeError: If validation fails critically
        """
        logger.info(
            f"[ResultValidation] task_id={input_data.task_id}, "
            f"workflow_id={context.workflow_id}"
        )

        # Check if previous primitive failed
        if not input_data.success:
            logger.warning(
                f"[ResultValidation] Skipping validation due to previous failure: "
                f"{input_data.error}"
            )
            return input_data

        try:
            # Validate result
            if not input_data.result:
                raise RuntimeError("No result to validate")

            validation = self.validator.validate(input_data.result)

            # Store validation in context
            context.state["validation_result"] = validation

            logger.info(
                f"[ResultValidation] passed={validation.passed}, "
                f"score={validation.score:.2f}, task_id={input_data.task_id}"
            )

            if validation.errors:
                logger.warning(
                    f"[ResultValidation] Errors: {', '.join(validation.errors)}"
                )

            if validation.warnings:
                logger.info(
                    f"[ResultValidation] Warnings: {', '.join(validation.warnings)}"
                )

            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=input_data.model,
                result=input_data.result,
                validation=validation,
                success=validation.passed,
                error="; ".join(validation.errors) if validation.errors else None,
            )

        except Exception as e:
            logger.error(f"[ResultValidation] Error: {e}", exc_info=True)
            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=input_data.model,
                result=input_data.result,
                success=False,
                error=str(e),
            )


class MetricsRecordingPrimitive(
    WorkflowPrimitive[OpenHandsTaskOutput, OpenHandsTaskOutput]
):
    """
    Primitive for recording execution metrics.

    Wraps MetricsCollector.record_execution() in a composable workflow primitive.

    Example:
        ```python
        metrics_collector = MetricsCollector()
        primitive = MetricsRecordingPrimitive(metrics_collector)

        # Input from ResultValidationPrimitive
        task_output = OpenHandsTaskOutput(
            task_id="test-001",
            task_type="unit_test",
            model=selected_model,
            result={"content": "test code..."},
            validation=validation_result,
            success=True,
        )

        context = WorkflowContext(workflow_id="wf-001")
        context.state["execution_duration_ms"] = 1500.0

        output = await primitive.execute(task_output, context)
        ```
    """

    def __init__(self, metrics_collector: MetricsCollector):
        """
        Initialize metrics recording primitive.

        Args:
            metrics_collector: MetricsCollector instance
        """
        self.metrics_collector = metrics_collector

    async def execute(
        self, input_data: OpenHandsTaskOutput, context: WorkflowContext
    ) -> OpenHandsTaskOutput:
        """
        Record execution metrics.

        Args:
            input_data: Task output from previous primitive (with validation result)
            context: Workflow context

        Returns:
            Task output with metrics recorded

        Note:
            This primitive always succeeds and passes through the input data.
            Metrics recording failures are logged but do not fail the workflow.
        """
        logger.info(
            f"[MetricsRecording] task_id={input_data.task_id}, "
            f"workflow_id={context.workflow_id}"
        )

        try:
            # Create execution metrics
            metrics = ExecutionMetrics(
                task_id=input_data.task_id,
                model_id=input_data.model.model_id if input_data.model else "unknown",
                task_type=input_data.task_type,
                duration_ms=context.state.get("execution_duration_ms", 0.0),
                success=input_data.success,
                error=input_data.error,
                quality_score=(
                    input_data.validation.score if input_data.validation else 0.0
                ),
                validation_passed=(
                    input_data.validation.passed if input_data.validation else False
                ),
            )

            # Record metrics
            self.metrics_collector.record_execution(metrics)

            # Store metrics in context
            context.state["recorded_metrics"] = metrics

            logger.info(
                f"[MetricsRecording] Recorded metrics for task_id={input_data.task_id}"
            )

            # Return input data with metrics attached
            return OpenHandsTaskOutput(
                task_id=input_data.task_id,
                task_type=input_data.task_type,
                model=input_data.model,
                result=input_data.result,
                validation=input_data.validation,
                metrics=metrics,
                success=input_data.success,
                error=input_data.error,
            )

        except Exception as e:
            # Metrics recording failure should not fail the workflow
            logger.error(
                f"[MetricsRecording] Error recording metrics: {e}", exc_info=True
            )
            # Return input data unchanged
            return input_data
