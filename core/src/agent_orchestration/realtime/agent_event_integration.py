"""
Real-time event integration for enhanced agent proxies.

This module provides integration between the enhanced agent proxies and the
real-time event system, enabling progress tracking and status updates.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from .event_publisher import EventPublisher
from .models import (
    AgentStatus,
    ProgressiveFeedbackEvent,
    WorkflowStatus,
    create_agent_status_event,
    create_workflow_progress_event,
)

logger = logging.getLogger(__name__)


class AgentEventIntegrator:
    """Integrates agent operations with real-time event publishing."""

    def __init__(
        self,
        event_publisher: EventPublisher | None = None,
        agent_id: str = "unknown",
        agent_type: str = "unknown",
        enabled: bool = True,
    ):
        self.event_publisher = event_publisher
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.enabled = enabled and event_publisher is not None

        # Operation tracking
        self.active_operations: dict[str, dict[str, Any]] = {}
        self.operation_counter = 0

        logger.debug(
            f"AgentEventIntegrator initialized for {agent_id}, enabled: {self.enabled}"
        )

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        self.operation_counter += 1
        return f"{self.agent_id}_op_{self.operation_counter}_{int(time.time() * 1000)}"

    async def _publish_event(self, event) -> bool:
        """Publish event if enabled."""
        if not self.enabled or not self.event_publisher:
            return False

        try:
            return await self.event_publisher.publish_event(event)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    @asynccontextmanager
    async def track_operation(
        self,
        operation_type: str,
        operation_data: dict[str, Any] | None = None,
        workflow_id: str | None = None,
    ):
        """Context manager for tracking agent operations with real-time events."""
        operation_id = self._generate_operation_id()
        start_time = time.time()

        # Initialize operation tracking
        self.active_operations[operation_id] = {
            "type": operation_type,
            "start_time": start_time,
            "workflow_id": workflow_id,
            "data": operation_data or {},
        }

        # Send start event
        start_event = create_agent_status_event(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=AgentStatus.PROCESSING,
            metadata={
                "operation_id": operation_id,
                "operation_type": operation_type,
                "workflow_id": workflow_id,
                "message": f"Started {operation_type}",
                **self.active_operations[operation_id]["data"],
            },
        )
        await self._publish_event(start_event)

        try:
            # Yield operation context
            yield {
                "operation_id": operation_id,
                "publish_progress": lambda progress, message="": self._publish_progress(
                    operation_id, progress, message, workflow_id
                ),
                "publish_feedback": lambda feedback_data: self._publish_feedback(
                    operation_id, feedback_data, workflow_id
                ),
            }

            # Send completion event
            duration = time.time() - start_time
            completion_event = create_agent_status_event(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                metadata={
                    "operation_id": operation_id,
                    "operation_type": operation_type,
                    "duration": duration,
                    "workflow_id": workflow_id,
                    "message": f"Completed {operation_type}",
                },
            )
            await self._publish_event(completion_event)

        except Exception as e:
            # Send error event
            duration = time.time() - start_time
            error_event = create_agent_status_event(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.ERROR,
                metadata={
                    "operation_id": operation_id,
                    "operation_type": operation_type,
                    "duration": duration,
                    "error": str(e),
                    "workflow_id": workflow_id,
                    "message": f"Error in {operation_type}: {str(e)}",
                },
            )
            await self._publish_event(error_event)
            raise

        finally:
            # Cleanup operation tracking
            self.active_operations.pop(operation_id, None)

    async def _publish_progress(
        self,
        operation_id: str,
        progress: float,
        message: str = "",
        workflow_id: str | None = None,
    ) -> bool:
        """Publish progress update for an operation."""
        if operation_id not in self.active_operations:
            return False

        operation = self.active_operations[operation_id]
        progress_event = ProgressiveFeedbackEvent(
            agent_id=self.agent_id,
            operation_id=operation_id,
            operation_type=operation["type"],
            stage="processing",
            progress_percentage=progress * 100,  # Convert to percentage
            message=message or f"Progress: {progress:.1%}",
            intermediate_result=None,
            metadata={"workflow_id": workflow_id},
            source=f"agent_{self.agent_id}",
        )

        return await self._publish_event(progress_event)

    async def _publish_feedback(
        self,
        operation_id: str,
        feedback_data: dict[str, Any],
        workflow_id: str | None = None,
    ) -> bool:
        """Publish progressive feedback for an operation."""
        if operation_id not in self.active_operations:
            return False

        operation = self.active_operations[operation_id]
        feedback_event = ProgressiveFeedbackEvent(
            agent_id=self.agent_id,
            operation_id=operation_id,
            progress=feedback_data.get("progress", 0.0),
            message=feedback_data.get("message", "Processing..."),
            intermediate_result=feedback_data.get("intermediate_result"),
            metadata={
                "operation_type": operation["type"],
                "workflow_id": workflow_id,
                **feedback_data.get("metadata", {}),
            },
            source=f"agent_{self.agent_id}",
        )

        return await self._publish_event(feedback_event)

    async def publish_status_change(
        self,
        status: AgentStatus,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Publish agent status change event."""
        event_metadata = metadata or {}
        if message:
            event_metadata["message"] = message
        event = create_agent_status_event(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=status,
            metadata=event_metadata,
        )
        return await self._publish_event(event)

    def get_active_operations(self) -> dict[str, dict[str, Any]]:
        """Get currently active operations."""
        return self.active_operations.copy()


class WorkflowEventIntegrator:
    """Integrates workflow operations with real-time event publishing."""

    def __init__(
        self, event_publisher: EventPublisher | None = None, enabled: bool = True
    ):
        self.event_publisher = event_publisher
        self.enabled = enabled and event_publisher is not None

        # Workflow tracking
        self.active_workflows: dict[str, dict[str, Any]] = {}

        logger.debug(f"WorkflowEventIntegrator initialized, enabled: {self.enabled}")

    async def _publish_event(self, event) -> bool:
        """Publish event if enabled."""
        if not self.enabled or not self.event_publisher:
            return False

        try:
            return await self.event_publisher.publish_event(event)
        except Exception as e:
            logger.error(f"Failed to publish workflow event: {e}")
            return False

    @asynccontextmanager
    async def track_workflow(
        self,
        workflow_id: str,
        workflow_type: str = "agent_coordination",
        total_steps: int = 3,
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager for tracking complete workflows."""
        start_time = time.time()

        # Initialize workflow tracking
        self.active_workflows[workflow_id] = {
            "type": workflow_type,
            "start_time": start_time,
            "total_steps": total_steps,
            "current_step": 0,
            "metadata": metadata or {},
        }

        # Send workflow start event
        start_event = create_workflow_progress_event(
            workflow_id=workflow_id,
            status=WorkflowStatus.IN_PROGRESS,
            progress=0.0,
            message=f"Started {workflow_type} workflow",
            metadata={
                "total_steps": total_steps,
                **self.active_workflows[workflow_id]["metadata"],
            },
        )
        await self._publish_event(start_event)

        try:
            # Yield workflow context
            yield {
                "workflow_id": workflow_id,
                "advance_step": lambda message="": self._advance_workflow_step(
                    workflow_id, message
                ),
                "update_progress": lambda progress, message="": self._update_workflow_progress(
                    workflow_id, progress, message
                ),
                "add_metadata": lambda key, value: self._add_workflow_metadata(
                    workflow_id, key, value
                ),
            }

            # Send completion event
            duration = time.time() - start_time
            completion_event = create_workflow_progress_event(
                workflow_id=workflow_id,
                status=WorkflowStatus.COMPLETED,
                progress=1.0,
                message=f"Completed {workflow_type} workflow",
                metadata={
                    "duration": duration,
                    "total_steps": self.active_workflows[workflow_id]["total_steps"],
                    **self.active_workflows[workflow_id]["metadata"],
                },
            )
            await self._publish_event(completion_event)

        except Exception as e:
            # Send error event
            duration = time.time() - start_time
            error_event = create_workflow_progress_event(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                progress=self.active_workflows[workflow_id]["current_step"]
                / max(self.active_workflows[workflow_id]["total_steps"], 1),
                message=f"Failed {workflow_type} workflow: {str(e)}",
                metadata={
                    "duration": duration,
                    "error": str(e),
                    **self.active_workflows[workflow_id]["metadata"],
                },
            )
            await self._publish_event(error_event)
            raise

        finally:
            # Cleanup workflow tracking
            self.active_workflows.pop(workflow_id, None)

    async def _advance_workflow_step(self, workflow_id: str, message: str = "") -> bool:
        """Advance workflow to next step."""
        if workflow_id not in self.active_workflows:
            return False

        workflow = self.active_workflows[workflow_id]
        workflow["current_step"] += 1

        progress = workflow["current_step"] / max(workflow["total_steps"], 1)
        step_message = (
            message or f"Step {workflow['current_step']}/{workflow['total_steps']}"
        )

        return await self._update_workflow_progress(workflow_id, progress, step_message)

    async def _update_workflow_progress(
        self, workflow_id: str, progress: float, message: str = ""
    ) -> bool:
        """Update workflow progress."""
        if workflow_id not in self.active_workflows:
            return False

        workflow = self.active_workflows[workflow_id]
        progress_event = create_workflow_progress_event(
            workflow_id=workflow_id,
            status=WorkflowStatus.IN_PROGRESS,
            progress=progress,
            message=message or f"Progress: {progress:.1%}",
            metadata=workflow["metadata"],
        )

        return await self._publish_event(progress_event)

    def _add_workflow_metadata(self, workflow_id: str, key: str, value: Any) -> None:
        """Add metadata to workflow."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["metadata"][key] = value

    def get_active_workflows(self) -> dict[str, dict[str, Any]]:
        """Get currently active workflows."""
        return self.active_workflows.copy()


# Global integrators for easy access
_agent_integrators: dict[str, AgentEventIntegrator] = {}
_workflow_integrator: WorkflowEventIntegrator | None = None


def get_agent_event_integrator(
    agent_id: str,
    agent_type: str = "unknown",
    event_publisher: EventPublisher | None = None,
    enabled: bool = True,
) -> AgentEventIntegrator:
    """Get or create agent event integrator."""
    global _agent_integrators

    if agent_id not in _agent_integrators or event_publisher is not None:
        _agent_integrators[agent_id] = AgentEventIntegrator(
            event_publisher=event_publisher,
            agent_id=agent_id,
            agent_type=agent_type,
            enabled=enabled
        )

    return _agent_integrators[agent_id]


def get_workflow_event_integrator(
    event_publisher: EventPublisher | None = None, enabled: bool = True
) -> WorkflowEventIntegrator:
    """Get or create workflow event integrator."""
    global _workflow_integrator

    if _workflow_integrator is None or event_publisher is not None:
        _workflow_integrator = WorkflowEventIntegrator(
            event_publisher=event_publisher, enabled=enabled
        )

    return _workflow_integrator


class AgentWorkflowCoordinator:
    """Coordinates complete agent workflows with real-time progress tracking."""

    def __init__(
        self,
        ipa_proxy,
        wba_proxy,
        nga_proxy,
        event_publisher: EventPublisher | None = None,
    ):
        self.ipa_proxy = ipa_proxy
        self.wba_proxy = wba_proxy
        self.nga_proxy = nga_proxy

        # Workflow event integration
        self.workflow_integrator = get_workflow_event_integrator(
            event_publisher=event_publisher, enabled=event_publisher is not None
        )

        logger.info("AgentWorkflowCoordinator initialized with real-time tracking")

    async def execute_complete_workflow(
        self,
        user_input: str,
        session_id: str,
        world_id: str | None = None,
        workflow_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute complete IPA → WBA → NGA workflow with real-time progress."""
        if workflow_id is None:
            workflow_id = f"workflow_{session_id}_{int(time.time() * 1000)}"

        # Track complete workflow
        async with self.workflow_integrator.track_workflow(
            workflow_id=workflow_id,
            workflow_type="ipa_wba_nga_chain",
            total_steps=3,
            metadata={
                "session_id": session_id,
                "world_id": world_id,
                "user_input_length": len(user_input),
            },
        ) as workflow:
            # Step 1: Input Processing
            await workflow["advance_step"]("Processing user input with IPA")
            ipa_result = await self.ipa_proxy.process({"text": user_input})

            await workflow["add_metadata"](
                "ipa_intent", ipa_result.get("routing", {}).get("intent")
            )

            # Step 2: World Building
            await workflow["advance_step"]("Updating world state with WBA")

            world_updates = {
                "user_action": ipa_result.get("routing", {}).get("intent", "unknown"),
                "normalized_input": ipa_result.get("normalized_text", user_input),
                "session_id": session_id,
            }

            if world_id:
                world_updates["world_id"] = world_id

            wba_result = await self.wba_proxy.process(world_updates)

            await workflow["add_metadata"](
                "world_state_updated", bool(wba_result.get("world_state"))
            )

            # Step 3: Narrative Generation
            await workflow["advance_step"]("Generating narrative with NGA")

            nga_input = {
                "prompt": f"Continue the story based on: {user_input}",
                "context": {
                    "session_id": session_id,
                    "world_state": wba_result.get("world_state", {}),
                    "user_intent": ipa_result.get("routing", {}).get("intent"),
                    "routing_info": ipa_result.get("routing", {}),
                },
            }

            nga_result = await self.nga_proxy.process(nga_input)

            await workflow["add_metadata"](
                "story_generated", bool(nga_result.get("story"))
            )

            # Compile final result
            final_result = {
                "workflow_id": workflow_id,
                "session_id": session_id,
                "user_input": user_input,
                "ipa_result": ipa_result,
                "wba_result": wba_result,
                "nga_result": nga_result,
                "story": nga_result.get("story", ""),
                "world_state": wba_result.get("world_state", {}),
                "therapeutic_validation": {
                    "ipa": ipa_result.get("therapeutic_validation"),
                    "nga": nga_result.get("therapeutic_validation"),
                },
                "sources": {
                    "ipa": ipa_result.get("source", "unknown"),
                    "wba": wba_result.get("source", "unknown"),
                    "nga": nga_result.get("source", "unknown"),
                },
            }

            return final_result

    async def execute_partial_workflow(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        workflow_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute partial workflow (e.g., just IPA → WBA or WBA → NGA)."""
        if workflow_id is None:
            workflow_id = f"partial_{workflow_type}_{int(time.time() * 1000)}"

        if workflow_type == "ipa_wba":
            return await self._execute_ipa_wba_workflow(workflow_id, input_data)
        elif workflow_type == "wba_nga":
            return await self._execute_wba_nga_workflow(workflow_id, input_data)
        elif workflow_type == "ipa_nga":
            return await self._execute_ipa_nga_workflow(workflow_id, input_data)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

    async def _execute_ipa_wba_workflow(
        self, workflow_id: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute IPA → WBA workflow."""
        async with self.workflow_integrator.track_workflow(
            workflow_id=workflow_id,
            workflow_type="ipa_wba_chain",
            total_steps=2,
            metadata=input_data.get("metadata", {}),
        ) as workflow:
            # Step 1: Input Processing
            await workflow["advance_step"]("Processing input with IPA")
            ipa_result = await self.ipa_proxy.process(input_data.get("ipa_input", {}))

            # Step 2: World Building
            await workflow["advance_step"]("Updating world with WBA")
            wba_input = input_data.get("wba_input", {})
            wba_input.update(
                {
                    "user_action": ipa_result.get("routing", {}).get("intent"),
                    "normalized_input": ipa_result.get("normalized_text"),
                }
            )

            wba_result = await self.wba_proxy.process(wba_input)

            return {
                "workflow_id": workflow_id,
                "ipa_result": ipa_result,
                "wba_result": wba_result,
            }

    async def _execute_wba_nga_workflow(
        self, workflow_id: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute WBA → NGA workflow."""
        async with self.workflow_integrator.track_workflow(
            workflow_id=workflow_id,
            workflow_type="wba_nga_chain",
            total_steps=2,
            metadata=input_data.get("metadata", {}),
        ) as workflow:
            # Step 1: World Building
            await workflow["advance_step"]("Processing world updates with WBA")
            wba_result = await self.wba_proxy.process(input_data.get("wba_input", {}))

            # Step 2: Narrative Generation
            await workflow["advance_step"]("Generating narrative with NGA")
            nga_input = input_data.get("nga_input", {})
            nga_input.setdefault("context", {}).update(
                {"world_state": wba_result.get("world_state", {})}
            )

            nga_result = await self.nga_proxy.process(nga_input)

            return {
                "workflow_id": workflow_id,
                "wba_result": wba_result,
                "nga_result": nga_result,
                "story": nga_result.get("story", ""),
            }

    async def _execute_ipa_nga_workflow(
        self, workflow_id: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute IPA → NGA workflow (bypassing WBA)."""
        async with self.workflow_integrator.track_workflow(
            workflow_id=workflow_id,
            workflow_type="ipa_nga_chain",
            total_steps=2,
            metadata=input_data.get("metadata", {}),
        ) as workflow:
            # Step 1: Input Processing
            await workflow["advance_step"]("Processing input with IPA")
            ipa_result = await self.ipa_proxy.process(input_data.get("ipa_input", {}))

            # Step 2: Narrative Generation
            await workflow["advance_step"]("Generating narrative with NGA")
            nga_input = input_data.get("nga_input", {})
            nga_input.setdefault("context", {}).update(
                {
                    "user_intent": ipa_result.get("routing", {}).get("intent"),
                    "routing_info": ipa_result.get("routing", {}),
                }
            )

            nga_result = await self.nga_proxy.process(nga_input)

            return {
                "workflow_id": workflow_id,
                "ipa_result": ipa_result,
                "nga_result": nga_result,
                "story": nga_result.get("story", ""),
            }
