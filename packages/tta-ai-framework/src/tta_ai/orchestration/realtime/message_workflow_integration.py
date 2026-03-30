"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Realtime/Message_workflow_integration]]
Integration layer between RedisMessageCoordinator and workflow progress tracking.

This module provides integration between the existing message coordination system
and the new real-time workflow progress tracking capabilities.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from ..coordinators.redis_message_coordinator import RedisMessageCoordinator
from ..messaging import FailureType, MessageResult, ReceivedMessage
from ..models import AgentId, AgentMessage
from .progressive_feedback import ProgressiveFeedbackManager
from .workflow_progress import WorkflowProgressTracker, WorkflowStage

logger = logging.getLogger(__name__)


class WorkflowAwareMessageCoordinator:
    """
    Enhanced message coordinator with workflow progress tracking integration.

    This class wraps the existing RedisMessageCoordinator and adds workflow
    progress tracking capabilities for messages that are part of workflows.
    """

    def __init__(
        self,
        redis_coordinator: RedisMessageCoordinator,
        workflow_tracker: WorkflowProgressTracker | None = None,
        feedback_manager: ProgressiveFeedbackManager | None = None,
        track_message_workflows: bool = True,
    ):
        self.redis_coordinator = redis_coordinator
        self.workflow_tracker = workflow_tracker
        self.feedback_manager = feedback_manager
        self.track_message_workflows = track_message_workflows

        # Workflow message tracking
        self.message_to_workflow: dict[str, str] = {}  # message_id -> workflow_id
        self.workflow_messages: dict[str, set[str]] = {}  # workflow_id -> message_ids
        self.workflow_agents: dict[str, set[AgentId]] = {}  # workflow_id -> agent_ids

        # Message processing callbacks
        self.message_callbacks: dict[str, set[Callable]] = {}  # workflow_id -> callbacks

        logger.info("WorkflowAwareMessageCoordinator initialized")

    async def start_workflow_tracking(
        self,
        workflow_id: str,
        workflow_type: str,
        participating_agents: list[AgentId],
        user_id: str | None = None,
        estimated_messages: int | None = None,
    ) -> bool:
        """Start tracking a workflow with message coordination."""
        if not self.workflow_tracker:
            return False

        try:
            # Start workflow tracking
            await self.workflow_tracker.start_workflow(
                workflow_type=workflow_type,
                workflow_id=workflow_id,
                user_id=user_id,
                total_steps=estimated_messages,
            )

            # Track participating agents
            self.workflow_agents[workflow_id] = set(participating_agents)
            self.workflow_messages[workflow_id] = set()
            self.message_callbacks[workflow_id] = set()

            # Add workflow milestones based on agent sequence
            if len(participating_agents) > 1:
                for i, agent in enumerate(participating_agents):
                    milestone_name = f"Agent {agent.type.value} Processing"
                    milestone_desc = f"Processing by {agent.type.value} agent"
                    stage = WorkflowStage.EXECUTING

                    if i == 0:
                        stage = WorkflowStage.INITIALIZING
                    elif i == len(participating_agents) - 1:
                        stage = WorkflowStage.FINALIZING

                    await self.workflow_tracker.start_workflow(
                        workflow_type=workflow_type,
                        workflow_id=workflow_id,
                        milestones=[
                            {
                                "name": milestone_name,
                                "description": milestone_desc,
                                "stage": stage.value,
                                "weight": 1.0 / len(participating_agents),
                            }
                        ],
                    )

            logger.info(
                f"Started workflow tracking: {workflow_id} with {len(participating_agents)} agents"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start workflow tracking: {e}")
            return False

    async def send_workflow_message(
        self,
        sender: AgentId,
        recipient: AgentId,
        message: AgentMessage,
        workflow_id: str | None = None,
    ) -> MessageResult:
        """Send a message with workflow tracking."""
        # Send message through existing coordinator
        result = await self.redis_coordinator.send_message(sender, recipient, message)

        # Track workflow association if enabled
        if self.track_message_workflows and workflow_id and result.delivered:
            await self._track_workflow_message(workflow_id, message.message_id, sender, recipient)

        return result

    async def broadcast_workflow_message(
        self,
        sender: AgentId,
        message: AgentMessage,
        recipients: list[AgentId],
        workflow_id: str | None = None,
    ) -> list[MessageResult]:
        """Broadcast a message with workflow tracking."""
        # Send messages through existing coordinator
        results = await self.redis_coordinator.broadcast_message(sender, message, recipients)

        # Track workflow associations if enabled
        if self.track_message_workflows and workflow_id:
            for i, result in enumerate(results):
                if result.delivered and i < len(recipients):
                    await self._track_workflow_message(
                        workflow_id, message.message_id, sender, recipients[i]
                    )

        return results

    async def receive_workflow_message(
        self,
        agent_id: AgentId,
        visibility_timeout: int = 5,
    ) -> ReceivedMessage | None:
        """Receive a message with workflow progress tracking."""
        # Receive message through existing coordinator
        received_message = await self.redis_coordinator.receive(agent_id, visibility_timeout)

        if received_message and self.track_message_workflows:
            # Check if this message is part of a workflow
            workflow_id = self.message_to_workflow.get(received_message.message.message_id)
            if workflow_id:
                await self._update_workflow_on_message_received(
                    workflow_id, received_message, agent_id
                )

        return received_message

    async def ack_workflow_message(
        self,
        agent_id: AgentId,
        token: str,
        workflow_result: dict[str, Any] | None = None,
    ) -> bool:
        """Acknowledge a message with workflow progress update."""
        # Get message info before acking
        message_info = await self._get_reserved_message_info(agent_id, token)

        # Acknowledge through existing coordinator
        success = await self.redis_coordinator.ack(agent_id, token)

        if success and self.track_message_workflows and message_info:
            workflow_id = self.message_to_workflow.get(message_info.get("message_id"))
            if workflow_id:
                await self._update_workflow_on_message_ack(
                    workflow_id, message_info, agent_id, workflow_result
                )

        return success

    async def nack_workflow_message(
        self,
        agent_id: AgentId,
        token: str,
        failure: FailureType = FailureType.TRANSIENT,
        error: str | None = None,
    ) -> bool:
        """Negative acknowledge a message with workflow error tracking."""
        # Get message info before nacking
        message_info = await self._get_reserved_message_info(agent_id, token)

        # Nack through existing coordinator
        success = await self.redis_coordinator.nack(agent_id, token, failure, error)

        if success and self.track_message_workflows and message_info:
            workflow_id = self.message_to_workflow.get(message_info.get("message_id"))
            if workflow_id:
                await self._update_workflow_on_message_nack(
                    workflow_id, message_info, agent_id, failure, error
                )

        return success

    async def complete_workflow(
        self,
        workflow_id: str,
        success: bool = True,
        final_result: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> bool:
        """Complete workflow tracking."""
        if not self.workflow_tracker:
            return False

        try:
            if success:
                await self.workflow_tracker.complete_workflow(
                    workflow_id,
                    "Workflow completed successfully",
                    final_result,
                    success=True,
                )
            else:
                await self.workflow_tracker.fail_workflow(
                    workflow_id, error_message or "Workflow failed", final_result
                )

            # Clean up tracking data
            self.workflow_agents.pop(workflow_id, None)
            self.message_callbacks.pop(workflow_id, None)

            # Clean up message associations
            message_ids = self.workflow_messages.pop(workflow_id, set())
            for message_id in message_ids:
                self.message_to_workflow.pop(message_id, None)

            logger.info(f"Completed workflow: {workflow_id} ({'success' if success else 'failed'})")
            return True

        except Exception as e:
            logger.error(f"Failed to complete workflow: {e}")
            return False

    def add_workflow_callback(
        self, workflow_id: str, callback: Callable[[str, dict[str, Any]], None]
    ) -> bool:
        """Add a callback for workflow message events."""
        if workflow_id not in self.workflow_messages:
            return False

        self.message_callbacks[workflow_id].add(callback)
        return True

    def get_workflow_message_stats(self, workflow_id: str) -> dict[str, Any] | None:
        """Get message statistics for a workflow."""
        if workflow_id not in self.workflow_messages:
            return None

        message_ids = self.workflow_messages[workflow_id]
        agents = self.workflow_agents.get(workflow_id, set())

        return {
            "workflow_id": workflow_id,
            "total_messages": len(message_ids),
            "participating_agents": len(agents),
            "agent_types": [agent.type.value for agent in agents],
        }

    async def _track_workflow_message(
        self,
        workflow_id: str,
        message_id: str,
        sender: AgentId,
        recipient: AgentId,
    ) -> None:
        """Track a message as part of a workflow."""
        self.message_to_workflow[message_id] = workflow_id

        if workflow_id not in self.workflow_messages:
            self.workflow_messages[workflow_id] = set()

        self.workflow_messages[workflow_id].add(message_id)

        # Update workflow progress
        if self.workflow_tracker:
            await self.workflow_tracker.update_workflow_progress(
                workflow_id,
                current_step=f"Message sent from {sender.type.value} to {recipient.type.value}",
                metadata={
                    "last_message_id": message_id,
                    "last_sender": sender.type.value,
                    "last_recipient": recipient.type.value,
                },
            )

    async def _update_workflow_on_message_received(
        self,
        workflow_id: str,
        received_message: ReceivedMessage,
        agent_id: AgentId,
    ) -> None:
        """Update workflow progress when a message is received."""
        if self.workflow_tracker:
            await self.workflow_tracker.update_workflow_progress(
                workflow_id,
                current_step=f"Message received by {agent_id.type.value}",
                metadata={
                    "received_message_id": received_message.message.message_id,
                    "receiving_agent": agent_id.type.value,
                    "message_type": received_message.message.message_type.value,
                },
            )

    async def _update_workflow_on_message_ack(
        self,
        workflow_id: str,
        message_info: dict[str, Any],
        agent_id: AgentId,
        workflow_result: dict[str, Any] | None,
    ) -> None:
        """Update workflow progress when a message is acknowledged."""
        if self.workflow_tracker:
            # Increment completed steps
            workflow_status = self.workflow_tracker.get_workflow_status(workflow_id)
            if workflow_status:
                completed_steps = workflow_status.get("completed_steps", 0) + 1

                await self.workflow_tracker.update_workflow_progress(
                    workflow_id,
                    current_step=f"Message processed by {agent_id.type.value}",
                    completed_steps=completed_steps,
                    metadata={
                        "processed_message_id": message_info.get("message_id"),
                        "processing_agent": agent_id.type.value,
                        "workflow_result": workflow_result,
                    },
                )

        # Call workflow callbacks
        await self._call_workflow_callbacks(
            workflow_id,
            "message_ack",
            {
                "message_info": message_info,
                "agent_id": (
                    agent_id.model_dump() if hasattr(agent_id, "model_dump") else str(agent_id)
                ),
                "workflow_result": workflow_result,
            },
        )

    async def _update_workflow_on_message_nack(
        self,
        workflow_id: str,
        message_info: dict[str, Any],
        agent_id: AgentId,
        failure: FailureType,
        error: str | None,
    ) -> None:
        """Update workflow progress when a message is nacked."""
        if self.workflow_tracker:
            await self.workflow_tracker.update_workflow_progress(
                workflow_id,
                current_step=f"Message failed in {agent_id.type.value}",
                metadata={
                    "failed_message_id": message_info.get("message_id"),
                    "failing_agent": agent_id.type.value,
                    "failure_type": failure.value,
                    "error_message": error,
                },
            )

        # Call workflow callbacks
        await self._call_workflow_callbacks(
            workflow_id,
            "message_nack",
            {
                "message_info": message_info,
                "agent_id": (
                    agent_id.model_dump() if hasattr(agent_id, "model_dump") else str(agent_id)
                ),
                "failure_type": failure.value,
                "error": error,
            },
        )

    async def _get_reserved_message_info(
        self, agent_id: AgentId, token: str
    ) -> dict[str, Any] | None:
        """Get information about a reserved message."""
        try:
            # Access the Redis client from the coordinator
            redis_client = self.redis_coordinator._redis
            reserved_hash_key = self.redis_coordinator._reserved_hash(agent_id)

            payload = await redis_client.hget(reserved_hash_key, token)
            if payload:
                import json

                data = json.loads(payload if isinstance(payload, str) else payload.decode())
                return {
                    "message_id": data.get("message", {}).get("message_id"),
                    "message_type": data.get("message", {}).get("message_type"),
                    "payload": data,
                }
        except Exception as e:
            logger.error(f"Failed to get reserved message info: {e}")

        return None

    async def _call_workflow_callbacks(
        self, workflow_id: str, event_type: str, event_data: dict[str, Any]
    ) -> None:
        """Call all registered callbacks for a workflow."""
        callbacks = self.message_callbacks.get(workflow_id, set())

        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, event_data)
                else:
                    callback(event_type, event_data)
            except Exception as e:
                logger.error(f"Error in workflow callback: {e}")

    # Delegate all other methods to the underlying coordinator
    def __getattr__(self, name):
        """Delegate unknown methods to the underlying Redis coordinator."""
        return getattr(self.redis_coordinator, name)
