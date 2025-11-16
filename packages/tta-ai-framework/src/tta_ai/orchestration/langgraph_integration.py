"""
LangGraph integration (Task 3.2).

This module provides optional integration with LangGraph. If LangGraph is not
installed, the builder/executor gracefully degrade to stubs so the overall
system remains functional without the dependency.
"""

from __future__ import annotations

from typing import Any

try:  # Optional dependency
    from langgraph.graph import END, START, StateGraph  # type: ignore

    _LANGGRAPH_AVAILABLE = True
except Exception:  # pragma: no cover - runtime optional
    StateGraph = None  # type: ignore
    START = "START"  # type: ignore
    END = "END"  # type: ignore
    _LANGGRAPH_AVAILABLE = False

from .workflow import OrchestrationResponse as WorkflowOrchestrationResponse
from .workflow import (
    WorkflowDefinition,
)


class LangGraphWorkflowBuilder:
    """Builds a LangGraph graph from a WorkflowDefinition when available."""

    def build(self, definition: WorkflowDefinition) -> dict[str, Any]:
        if not _LANGGRAPH_AVAILABLE:
            return {
                "type": "graph_stub",
                "reason": "LangGraph not available",
                "nodes": [s.agent.value for s in definition.agent_sequence],
            }

        # Create a minimal StateGraph where each step is a node that appends to history
        sg = StateGraph(dict)

        def _node_fn_factory(agent_name: str):
            def _fn(state: dict[str, Any]) -> dict[str, Any]:
                history: list[str] = state.get("history", [])
                history = list(history) + [agent_name]
                state["history"] = history
                return state

            return _fn

        # Add nodes for sequential steps
        for step in definition.agent_sequence:
            sg.add_node(step.agent.value, _node_fn_factory(step.agent.value))

        # Wire edges for the sequence
        if definition.agent_sequence:
            first = definition.agent_sequence[0].agent.value
            sg.add_edge(START, first)
            for a, b in zip(definition.agent_sequence, definition.agent_sequence[1:], strict=False):
                sg.add_edge(a.agent.value, b.agent.value)
            sg.add_edge(definition.agent_sequence[-1].agent.value, END)

        app = sg.compile()
        return {
            "type": "langgraph",
            "app": app,
            "nodes": [s.agent.value for s in definition.agent_sequence],
        }


class LangGraphExecutor:
    """Executes a previously built LangGraph graph."""

    def execute(
        self, graph: dict[str, Any], initial_state: dict[str, Any]
    ) -> WorkflowOrchestrationResponse:
        if graph.get("type") != "langgraph" or not _LANGGRAPH_AVAILABLE:
            # Fallback: behave like a stub
            return WorkflowOrchestrationResponse(
                response_text="Graph executed (stub)",
                updated_context=initial_state,
                workflow_metadata={"graph": graph},
                performance_metrics={},
                therapeutic_validation=None,
            )

        app = graph.get("app")
        if app is None:
            return WorkflowOrchestrationResponse(
                response_text="Graph missing 'app' - executed as stub",
                updated_context=initial_state,
                workflow_metadata={"graph": graph},
                performance_metrics={},
                therapeutic_validation=None,
            )

        result_state: dict[str, Any] = app.invoke(initial_state)
        return WorkflowOrchestrationResponse(
            response_text="Graph executed (langgraph)",
            updated_context=result_state,
            workflow_metadata={"graph": {k: v for k, v in graph.items() if k != "app"}},
            performance_metrics={},
            therapeutic_validation=None,
        )
