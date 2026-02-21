"""

# Logseq: [[TTA.dev/Agent_orchestration/Workflow_manager]]
WorkflowManager core functionality (Task 3.1, extended for 3.2 integration points).

Provides registration, validation, and a minimal execution entrypoint for
workflow definitions. Adds optional LangGraph integration: build_graph and
execute_graph delegate to LangGraph when available via LangGraphWorkflowBuilder
and LangGraphExecutor; otherwise they return stub responses.
"""

from __future__ import annotations

import contextlib
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from .circuit_breaker import CircuitBreakerOpenError
from .circuit_breaker_registry import CircuitBreakerRegistry
from .langgraph_integration import LangGraphExecutor, LangGraphWorkflowBuilder
from .models import OrchestrationRequest
from .performance import get_step_aggregator
from .state import AgentContext
from .workflow import (
    AgentStep,
    WorkflowDefinition,
)
from .workflow import OrchestrationResponse as WorkflowOrchestrationResponse

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


class WorkflowRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepResult(BaseModel):
    step: AgentStep
    started_at: str = Field(default_factory=_utc_now)
    ended_at: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class WorkflowRunState(BaseModel):
    run_id: str
    workflow_name: str
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    current_step_index: int = 0
    started_at: str | None = None
    ended_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    request: OrchestrationRequest
    context: AgentContext = Field(default_factory=AgentContext)
    definition: WorkflowDefinition

    history: list[StepResult] = Field(default_factory=list)


class WorkflowManager:
    """Registers and executes workflows with basic validation and state tracking."""

    def __init__(
        self, circuit_breaker_registry: CircuitBreakerRegistry | None = None
    ) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._runs: dict[str, WorkflowRunState] = {}
        self._lg_builder = LangGraphWorkflowBuilder()
        self._lg_executor = LangGraphExecutor()
        # Performance aggregator
        self._aggregator = get_step_aggregator()
        # Circuit breaker registry for graceful degradation
        self._circuit_breaker_registry = circuit_breaker_registry

    # ---- Registration ----
    def register_workflow(
        self, name: str, definition: WorkflowDefinition
    ) -> tuple[bool, str | None]:
        ok, err = self._validate_workflow_definition(definition)
        if not ok:
            return False, err
        self._workflows[name] = definition
        return True, None

    def get_workflow(self, name: str) -> WorkflowDefinition | None:
        return self._workflows.get(name)

    def list_workflows(self) -> list[str]:
        return sorted(self._workflows.keys())

    # ---- Execution ----
    def execute_workflow(
        self,
        name: str,
        request: OrchestrationRequest,
        context: AgentContext | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WorkflowOrchestrationResponse | None, str | None, str | None]:
        """
        Execute a registered workflow in a minimal, synchronous manner.

        Includes circuit breaker checks for graceful degradation.

        Returns: (response, run_id, error)
        """
        definition = self._workflows.get(name)
        if not definition:
            return None, None, f"Workflow '{name}' is not registered"

        # Note: Circuit breaker integration available via execute_workflow_async method

        ok, err = self._validate_request_against_workflow(request, definition)
        if not ok:
            return None, None, err

        run_id = uuid.uuid4().hex
        run_state = WorkflowRunState(
            run_id=run_id,
            workflow_name=name,
            status=WorkflowRunStatus.RUNNING,
            current_step_index=0,
            started_at=_utc_now(),
            metadata=metadata or {},
            request=request,
            context=context or AgentContext(),
            definition=definition,
        )
        self._runs[run_id] = run_state

        try:
            # Sequentially process agent_sequence only (parallel steps may be handled by graph executor)
            for idx, step in enumerate(definition.agent_sequence):
                run_state.current_step_index = idx
                step_result = self._execute_step(step, run_state)
                run_state.history.append(step_result)
                if step_result.error:
                    run_state.status = WorkflowRunStatus.FAILED
                    run_state.ended_at = _utc_now()
                    return None, run_id, step_result.error

            # Optionally build/execute a graph (no-op if not available)
            graph = self._lg_builder.build(definition)
            self._lg_executor.execute(
                graph, {"history": [h.step.agent.value for h in run_state.history]}
            )

            # Mark complete
            run_state.status = WorkflowRunStatus.COMPLETED
            run_state.ended_at = _utc_now()

            # Compose response using context, history, and graph metadata
            # Aggregate safety findings from step results (if present)
            agg_safety: dict[str, Any] = {
                "level": "safe",
                "findings": [],
                "by_step": [],
            }
            try:
                levels = {"safe": 0, "warning": 1, "blocked": 2}
                max_level = 0
                for h in run_state.history:
                    tv = (
                        h.result.get("therapeutic_validation")
                        if isinstance(h.result, dict)
                        else None
                    )
                    if tv and isinstance(tv, dict):
                        agg_safety["by_step"].append(
                            {"agent": h.step.agent.value, "validation": tv}
                        )
                        lvl = str(tv.get("level") or "safe").lower()
                        max_level = max(max_level, levels.get(lvl, 0))
                        f = tv.get("findings") or []
                        if isinstance(f, list):
                            agg_safety["findings"].extend(f)
                inv_levels = {0: "safe", 1: "warning", 2: "blocked"}
                agg_safety["level"] = inv_levels.get(max_level, "safe")
            except Exception:
                agg_safety = None

            response = WorkflowOrchestrationResponse(
                response_text="Workflow executed",
                updated_context=run_state.context.model_dump(),
                workflow_metadata={
                    "workflow_name": name,
                    "run_id": run_id,
                    "steps_executed": len(definition.agent_sequence),
                    "status": run_state.status.value,
                    "graph": {k: v for k, v in graph.items() if k != "app"},
                },
                performance_metrics={
                    "started_at": run_state.started_at,
                    "ended_at": run_state.ended_at,
                },
                therapeutic_validation=agg_safety,
            )
            return response, run_id, None
        except Exception as e:
            run_state.status = WorkflowRunStatus.FAILED
            run_state.ended_at = _utc_now()
            return None, run_id, str(e)

    # ---- State introspection ----
    def get_run_state(self, run_id: str) -> WorkflowRunState | None:
        return self._runs.get(run_id)

    def update_run_metadata(self, run_id: str, metadata: dict[str, Any]) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.metadata.update(metadata)
        return True

    # ---- Extension points for Task 3.2 (LangGraph) ----
    def build_graph(self, definition: WorkflowDefinition) -> Any:
        return self._lg_builder.build(definition)

    def execute_graph(
        self, graph: Any, initial_state: dict[str, Any]
    ) -> WorkflowOrchestrationResponse:
        return self._lg_executor.execute(graph, initial_state)

    # ---- Internal helpers ----
    def _execute_step(self, step: AgentStep, run_state: WorkflowRunState) -> StepResult:
        # In future tasks, invoke AgentProxy implementations and update context
        result = StepResult(step=step)
        t0 = time.time()
        error: str | None = None
        try:
            # Placeholder processing logic
            result.result = {
                "agent": step.agent.value,
                "note": "Executed step (stub)",
            }
        except Exception as e:
            error = str(e)
            result.error = error
        finally:
            t1 = time.time()
            duration_ms = (t1 - t0) * 1000.0
            # Record performance per agent type key
            with contextlib.suppress(Exception):
                self._aggregator.record(
                    step.agent.value, duration_ms, success=(error is None)
                )
            result.ended_at = _utc_now()
        return result

    async def _execute_workflow_steps(
        self, definition: WorkflowDefinition, run_state: WorkflowRunState
    ) -> WorkflowOrchestrationResponse | None:
        """Execute workflow steps with error handling."""
        # Sequentially process agent_sequence only (parallel steps may be handled by graph executor)
        for idx, step in enumerate(definition.agent_sequence):
            run_state.current_step_index = idx
            step_result = self._execute_step(step, run_state)
            run_state.history.append(step_result)
            if step_result.error:
                run_state.status = WorkflowRunStatus.FAILED
                run_state.ended_at = _utc_now()
                raise Exception(step_result.error)

        # Optionally build/execute a graph (no-op if not available)
        graph = self._lg_builder.build(definition)
        graph_response = self._lg_executor.execute(
            graph, {"history": [h.step.agent.value for h in run_state.history]}
        )

        # Mark complete
        run_state.status = WorkflowRunStatus.COMPLETED
        run_state.ended_at = _utc_now()

        # Compose response using context, history, and graph metadata
        # Aggregate safety findings from step results (if present)
        agg_safety: dict[str, Any] = {"level": "safe", "findings": [], "by_step": []}
        with contextlib.suppress(Exception):
            for step_result in run_state.history:
                if "safety" in step_result.result:
                    agg_safety["by_step"].append(step_result.result["safety"])
                    if step_result.result["safety"].get("level") == "warning":
                        agg_safety["level"] = "warning"
                        agg_safety["findings"].extend(
                            step_result.result["safety"].get("findings", [])
                        )

        return WorkflowOrchestrationResponse(
            response_text=f"Workflow '{run_state.workflow_name}' completed successfully",
            updated_context=run_state.context.model_dump(),
            workflow_metadata={
                "run_id": run_state.run_id,
                "workflow_name": run_state.workflow_name,
                "steps_completed": len(run_state.history),
                "total_duration": (
                    (
                        datetime.fromisoformat(run_state.ended_at.rstrip("Z"))
                        - datetime.fromisoformat(run_state.started_at.rstrip("Z"))
                    ).total_seconds()
                    if run_state.started_at and run_state.ended_at
                    else None
                ),
                "graph_response": graph_response,
            },
            performance_metrics=(
                self._aggregator.get_metrics() if self._aggregator else {}
            ),
            therapeutic_validation=agg_safety,
        )

    def _execute_degraded_workflow(
        self,
        name: str,
        request: OrchestrationRequest,
        context: AgentContext | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WorkflowOrchestrationResponse | None, str | None, str | None]:
        """Execute workflow in degraded mode when circuit breaker is open."""
        logger.info(f"Executing workflow {name} in degraded mode")

        run_id = uuid.uuid4().hex

        # Create a simplified response for degraded mode
        degraded_response = WorkflowOrchestrationResponse(
            response_text=f"Workflow '{name}' executed in degraded mode due to service issues. Limited functionality available.",
            updated_context=(context or AgentContext()).model_dump(),
            workflow_metadata={
                "run_id": run_id,
                "workflow_name": name,
                "degraded_mode": True,
                "reason": "circuit_breaker_open",
                "steps_completed": 0,
            },
            performance_metrics={},
            therapeutic_validation={"level": "safe", "findings": [], "degraded": True},
        )

        return degraded_response, run_id, None

    async def execute_workflow_async(
        self,
        name: str,
        request: OrchestrationRequest,
        context: AgentContext | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[WorkflowOrchestrationResponse | None, str | None, str | None]:
        """
        Execute a registered workflow asynchronously with circuit breaker support.

        This is the async version that includes circuit breaker integration
        for graceful degradation and error handling.

        Returns: (response, run_id, error)
        """
        definition = self._workflows.get(name)
        if not definition:
            return None, None, f"Workflow '{name}' is not registered"

        # Check circuit breaker state before execution
        if self._circuit_breaker_registry:
            try:
                circuit_breaker = await self._circuit_breaker_registry.get_or_create(
                    f"workflow:{name}"
                )
                if not await circuit_breaker.is_call_permitted():
                    logger.warning(
                        f"Circuit breaker open for workflow {name}, attempting degraded execution"
                    )
                    return self._execute_degraded_workflow(
                        name, request, context, metadata
                    )
            except Exception as e:
                logger.warning(f"Circuit breaker check failed for workflow {name}: {e}")
                # Continue with normal execution if circuit breaker check fails

        ok, err = self._validate_request_against_workflow(request, definition)
        if not ok:
            return None, None, err

        run_id = uuid.uuid4().hex
        run_state = WorkflowRunState(
            run_id=run_id,
            workflow_name=name,
            status=WorkflowRunStatus.RUNNING,
            current_step_index=0,
            started_at=_utc_now(),
            metadata=metadata or {},
            request=request,
            context=context or AgentContext(),
            definition=definition,
        )
        self._runs[run_id] = run_state

        try:
            # Execute workflow through circuit breaker if available
            if self._circuit_breaker_registry:
                circuit_breaker = await self._circuit_breaker_registry.get_or_create(
                    f"workflow:{name}"
                )
                try:
                    response = await circuit_breaker.call(
                        lambda: self._execute_workflow_steps(definition, run_state)
                    )
                    if response:
                        return response, run_id, None
                except CircuitBreakerOpenError:
                    logger.warning(
                        f"Circuit breaker opened during workflow {name} execution"
                    )
                    return self._execute_degraded_workflow(
                        name, request, context, metadata
                    )
                except Exception as e:
                    logger.error(f"Workflow {name} execution failed: {e}")
                    run_state.status = WorkflowRunStatus.FAILED
                    run_state.ended_at = _utc_now()
                    return None, run_id, str(e)
            else:
                # Fallback to direct execution without circuit breaker
                response = await self._execute_workflow_steps(definition, run_state)
                if response:
                    return response, run_id, None

        except Exception as e:
            run_state.status = WorkflowRunStatus.FAILED
            run_state.ended_at = _utc_now()
            return None, run_id, str(e)

        # Should not reach here, but fallback
        return None, run_id, "Workflow execution completed without response"

    # ---- Circuit breaker management ----
    async def get_circuit_breaker_status(
        self, workflow_name: str
    ) -> dict[str, Any] | None:
        """Get circuit breaker status for a workflow."""
        if not self._circuit_breaker_registry:
            return None

        circuit_breaker = await self._circuit_breaker_registry.get(
            f"workflow:{workflow_name}"
        )
        if circuit_breaker:
            return await circuit_breaker.get_metrics()
        return None

    async def reset_circuit_breaker(self, workflow_name: str) -> bool:
        """Reset circuit breaker for a workflow."""
        if not self._circuit_breaker_registry:
            return False

        circuit_breaker = await self._circuit_breaker_registry.get(
            f"workflow:{workflow_name}"
        )
        if circuit_breaker:
            await circuit_breaker.reset()
            logger.info(f"Reset circuit breaker for workflow {workflow_name}")
            return True
        return False

    async def get_all_circuit_breaker_status(self) -> dict[str, Any]:
        """Get status of all workflow circuit breakers."""
        if not self._circuit_breaker_registry:
            return {}

        return await self._circuit_breaker_registry.get_all_metrics()

    def _validate_workflow_definition(
        self, definition: WorkflowDefinition
    ) -> tuple[bool, str | None]:
        try:
            WorkflowDefinition(**definition.model_dump())
        except ValidationError as e:
            return False, str(e)

        if not definition.agent_sequence and not definition.parallel_steps:
            return False, "Workflow must define at least one step"

        tc = definition.timeout_config
        for val in [tc.per_step_seconds, tc.total_seconds]:
            if val is not None and val <= 0:
                return False, "Timeouts must be positive integers"

        return True, None

    def _validate_request_against_workflow(
        self, request: OrchestrationRequest, definition: WorkflowDefinition
    ) -> tuple[bool, str | None]:
        if definition.agent_sequence:
            first_agent = definition.agent_sequence[0].agent
            if request.entrypoint != first_agent:
                return False, (
                    f"Entrypoint {request.entrypoint.value} does not match first step agent "
                    f"{first_agent.value}"
                )
        return True, None
