"""
WorkflowManager core functionality (Task 3.1, extended for 3.2 integration points).

Provides registration, validation, and a minimal execution entrypoint for
workflow definitions. Adds optional LangGraph integration: build_graph and
execute_graph delegate to LangGraph when available via LangGraphWorkflowBuilder
and LangGraphExecutor; otherwise they return stub responses.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

from .workflow import (
    WorkflowDefinition,
    AgentStep,
    WorkflowType,
    ErrorHandlingStrategy,
    OrchestrationResponse as WorkflowOrchestrationResponse,
)
from .state import AgentContext
from .models import OrchestrationRequest
from .langgraph_integration import LangGraphWorkflowBuilder, LangGraphExecutor
from .performance import get_step_aggregator
import time


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
    ended_at: Optional[str] = None
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class WorkflowRunState(BaseModel):
    run_id: str
    workflow_name: str
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    current_step_index: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    request: OrchestrationRequest
    context: AgentContext = Field(default_factory=AgentContext)
    definition: WorkflowDefinition

    history: List[StepResult] = Field(default_factory=list)


class WorkflowManager:
    """Registers and executes workflows with basic validation and state tracking."""

    def __init__(self) -> None:
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._runs: Dict[str, WorkflowRunState] = {}
        self._lg_builder = LangGraphWorkflowBuilder()
        self._lg_executor = LangGraphExecutor()
        # Performance aggregator
        self._aggregator = get_step_aggregator()

    # ---- Registration ----
    def register_workflow(self, name: str, definition: WorkflowDefinition) -> Tuple[bool, Optional[str]]:
        ok, err = self._validate_workflow_definition(definition)
        if not ok:
            return False, err
        self._workflows[name] = definition
        return True, None

    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]:
        return self._workflows.get(name)

    def list_workflows(self) -> List[str]:
        return sorted(self._workflows.keys())

    # ---- Execution ----
    def execute_workflow(
        self,
        name: str,
        request: OrchestrationRequest,
        context: Optional[AgentContext] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[WorkflowOrchestrationResponse], Optional[str], Optional[str]]:
        """
        Execute a registered workflow in a minimal, synchronous manner.

        Returns: (response, run_id, error)
        """
        definition = self._workflows.get(name)
        if not definition:
            return None, None, f"Workflow '{name}' is not registered"

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
            graph_response = self._lg_executor.execute(graph, {"history": [h.step.agent.value for h in run_state.history]})

            # Mark complete
            run_state.status = WorkflowRunStatus.COMPLETED
            run_state.ended_at = _utc_now()

            # Compose response using context, history, and graph metadata
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
                therapeutic_validation=None,
            )
            return response, run_id, None
        except Exception as e:
            run_state.status = WorkflowRunStatus.FAILED
            run_state.ended_at = _utc_now()
            return None, run_id, str(e)

    # ---- State introspection ----
    def get_run_state(self, run_id: str) -> Optional[WorkflowRunState]:
        return self._runs.get(run_id)

    def update_run_metadata(self, run_id: str, metadata: Dict[str, Any]) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        run.metadata.update(metadata)
        return True

    # ---- Extension points for Task 3.2 (LangGraph) ----
    def build_graph(self, definition: WorkflowDefinition) -> Any:
        return self._lg_builder.build(definition)

    def execute_graph(self, graph: Any, initial_state: Dict[str, Any]) -> WorkflowOrchestrationResponse:
        return self._lg_executor.execute(graph, initial_state)

    # ---- Internal helpers ----
    def _execute_step(self, step: AgentStep, run_state: WorkflowRunState) -> StepResult:
        # In future tasks, invoke AgentProxy implementations and update context
        result = StepResult(step=step)
        t0 = time.time()
        error: Optional[str] = None
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
            try:
                self._aggregator.record(step.agent.value, duration_ms, success=(error is None))
            except Exception:
                pass
            result.ended_at = _utc_now()
        return result

    def _validate_workflow_definition(self, definition: WorkflowDefinition) -> Tuple[bool, Optional[str]]:
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
    ) -> Tuple[bool, Optional[str]]:
        if definition.agent_sequence:
            first_agent = definition.agent_sequence[0].agent
            if request.entrypoint != first_agent:
                return False, (
                    f"Entrypoint {request.entrypoint.value} does not match first step agent "
                    f"{first_agent.value}"
                )
        return True, None

