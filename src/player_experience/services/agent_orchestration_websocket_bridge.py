"""
Agent Orchestration WebSocket Bridge

This service connects the existing agent orchestration system (IPA, WBA, NGA) with WebSocket
communication for real-time narrative generation and seamless player interaction.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from src.agent_orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)

from .gameplay_chat_manager import GameplayChatManager
from .narrative_generation_service import NarrativeGenerationService

logger = logging.getLogger(__name__)


class AgentWorkflowType(str, Enum):
    """Types of agent orchestration workflows."""

    NARRATIVE_GENERATION = "narrative_generation"
    INPUT_PROCESSING = "input_processing"
    WORLD_BUILDING = "world_building"
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"
    CHOICE_GENERATION = "choice_generation"
    SCENE_TRANSITION = "scene_transition"


class WorkflowPriority(int, Enum):
    """Priority levels for agent workflows."""

    CRITICAL = 1  # Therapeutic interventions, safety concerns
    HIGH = 2  # Player actions, choice responses
    MEDIUM = 3  # Narrative generation, scene updates
    LOW = 4  # Background world building, optimization


@dataclass
class AgentWorkflowRequest:
    """Request for agent orchestration workflow."""

    workflow_id: str
    workflow_type: AgentWorkflowType
    session_id: str
    player_id: str
    priority: WorkflowPriority
    payload: dict[str, Any]
    context: dict[str, Any]
    timeout_seconds: int = 30
    retry_count: int = 0
    max_retries: int = 2

    def __post_init__(self):
        self.created_at = datetime.utcnow()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None


@dataclass
class AgentWorkflowResponse:
    """Response from agent orchestration workflow."""

    workflow_id: str
    session_id: str
    success: bool
    result: dict[str, Any]
    agent_calls_made: list[str]
    processing_time_ms: float
    error_message: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AgentOrchestrationWebSocketBridge:
    """
    Bridge service connecting agent orchestration with WebSocket communication.

    Orchestrates multiple agents (IPA, WBA, NGA) to provide real-time narrative generation
    and seamless integration with the gameplay chat interface.
    """

    def __init__(
        self,
        narrative_agent: NarrativeGeneratorAgentProxy | None = None,
        input_processor: InputProcessorAgentProxy | None = None,
        world_builder: WorldBuilderAgentProxy | None = None,
        chat_manager: GameplayChatManager | None = None,
        narrative_service: NarrativeGenerationService | None = None,
    ):
        """
        Initialize the Agent Orchestration WebSocket Bridge.

        Args:
            narrative_agent: Narrative generator agent proxy
            input_processor: Input processor agent proxy
            world_builder: World builder agent proxy
            chat_manager: Gameplay chat manager
            narrative_service: Narrative generation service
        """
        self.narrative_agent = narrative_agent or NarrativeGeneratorAgentProxy()
        self.input_processor = input_processor or InputProcessorAgentProxy()
        self.world_builder = world_builder or WorldBuilderAgentProxy()
        self.chat_manager = chat_manager or GameplayChatManager()
        self.narrative_service = narrative_service or NarrativeGenerationService()

        # Workflow management
        self.active_workflows: dict[str, AgentWorkflowRequest] = {}
        self.workflow_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.workflow_processors: dict[AgentWorkflowType, Callable] = {}

        # Real-time messaging
        self.session_subscriptions: dict[str, list[str]] = (
            {}
        )  # session_id -> workflow_ids
        self.websocket_callbacks: dict[str, list[Callable]] = (
            {}
        )  # session_id -> callbacks

        # Configuration
        self.max_concurrent_workflows = 10
        self.workflow_timeout_seconds = 30
        self.enable_real_time_updates = True

        # Background processing
        self.processing_tasks: list[asyncio.Task] = []
        self.is_running = False

        # Metrics
        self.metrics = {
            "workflows_processed": 0,
            "narrative_workflows": 0,
            "input_processing_workflows": 0,
            "world_building_workflows": 0,
            "therapeutic_workflows": 0,
            "real_time_messages_sent": 0,
            "workflow_failures": 0,
            "average_processing_time_ms": 0,
            "concurrent_workflows_peak": 0,
        }

        # Initialize workflow processors
        self._initialize_workflow_processors()

        logger.info("AgentOrchestrationWebSocketBridge initialized")

    async def start(self) -> None:
        """Start the bridge service and background processing."""
        if self.is_running:
            logger.warning("Bridge service is already running")
            return

        self.is_running = True

        # Start workflow processing tasks
        for i in range(self.max_concurrent_workflows):
            task = asyncio.create_task(self._workflow_processor_loop(f"processor_{i}"))
            self.processing_tasks.append(task)

        # Start real-time update task
        if self.enable_real_time_updates:
            update_task = asyncio.create_task(self._real_time_update_loop())
            self.processing_tasks.append(update_task)

        logger.info("Agent orchestration WebSocket bridge started")

    async def stop(self) -> None:
        """Stop the bridge service and cleanup."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        self.processing_tasks.clear()
        logger.info("Agent orchestration WebSocket bridge stopped")

    async def execute_workflow(
        self,
        workflow_type: AgentWorkflowType,
        session_id: str,
        player_id: str,
        payload: dict[str, Any],
        context: dict[str, Any] | None = None,
        priority: WorkflowPriority = WorkflowPriority.MEDIUM,
    ) -> str:
        """
        Execute an agent orchestration workflow.

        Args:
            workflow_type: Type of workflow to execute
            session_id: Session identifier
            player_id: Player identifier
            payload: Workflow payload data
            context: Optional context data
            priority: Workflow priority

        Returns:
            Workflow ID for tracking
        """
        try:
            # Create workflow request
            workflow_id = (
                f"wf_{workflow_type.value}_{session_id}_{datetime.utcnow().timestamp()}"
            )

            request = AgentWorkflowRequest(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                session_id=session_id,
                player_id=player_id,
                priority=priority,
                payload=payload,
                context=context or {},
                timeout_seconds=self.workflow_timeout_seconds,
            )

            # Add to active workflows
            self.active_workflows[workflow_id] = request

            # Add to processing queue
            await self.workflow_queue.put((priority.value, request))

            # Subscribe session to workflow updates
            await self._subscribe_session_to_workflow(session_id, workflow_id)

            logger.debug(f"Queued workflow {workflow_id} for session {session_id}")
            return workflow_id

        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
        """
        Get the status of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow status dictionary or None if not found
        """
        request = self.active_workflows.get(workflow_id)
        if not request:
            return None

        return {
            "workflow_id": workflow_id,
            "workflow_type": request.workflow_type.value,
            "session_id": request.session_id,
            "priority": request.priority.value,
            "created_at": request.created_at.isoformat(),
            "started_at": (
                request.started_at.isoformat() if request.started_at else None
            ),
            "completed_at": (
                request.completed_at.isoformat() if request.completed_at else None
            ),
            "retry_count": request.retry_count,
            "status": (
                "completed"
                if request.completed_at
                else "processing" if request.started_at else "queued"
            ),
        }

    # Private methods

    def _initialize_workflow_processors(self) -> None:
        """Initialize workflow processors for different workflow types."""
        self.workflow_processors = {
            AgentWorkflowType.NARRATIVE_GENERATION: self._process_narrative_generation_workflow,
            AgentWorkflowType.INPUT_PROCESSING: self._process_input_processing_workflow,
            AgentWorkflowType.WORLD_BUILDING: self._process_world_building_workflow,
            AgentWorkflowType.THERAPEUTIC_INTERVENTION: self._process_therapeutic_intervention_workflow,
            AgentWorkflowType.CHOICE_GENERATION: self._process_choice_generation_workflow,
            AgentWorkflowType.SCENE_TRANSITION: self._process_scene_transition_workflow,
        }

    async def _workflow_processor_loop(self, processor_id: str) -> None:
        """Background loop for processing workflows."""
        logger.info(f"Started workflow processor {processor_id}")

        while self.is_running:
            try:
                # Get next workflow from queue
                try:
                    priority, request = await asyncio.wait_for(
                        self.workflow_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Process the workflow
                await self._process_workflow(request, processor_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in workflow processor {processor_id}: {e}")
                await asyncio.sleep(1)

        logger.info(f"Stopped workflow processor {processor_id}")

    async def _process_workflow(
        self, request: AgentWorkflowRequest, processor_id: str
    ) -> None:
        """Process a single workflow request."""
        try:
            request.started_at = datetime.utcnow()
            start_time = datetime.utcnow()

            # Update concurrent workflows peak
            current_active = len(
                [
                    r
                    for r in self.active_workflows.values()
                    if r.started_at and not r.completed_at
                ]
            )
            if current_active > self.metrics["concurrent_workflows_peak"]:
                self.metrics["concurrent_workflows_peak"] = current_active

            # Get appropriate processor
            processor = self.workflow_processors.get(request.workflow_type)
            if not processor:
                raise ValueError(
                    f"No processor found for workflow type {request.workflow_type}"
                )

            # Process the workflow
            result = await processor(request)

            # Create response
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            response = AgentWorkflowResponse(
                workflow_id=request.workflow_id,
                session_id=request.session_id,
                success=True,
                result=result,
                agent_calls_made=result.get("agent_calls_made", []),
                processing_time_ms=processing_time,
            )

            # Send real-time update
            await self._send_workflow_update(request.session_id, response)

            # Update metrics
            self.metrics["workflows_processed"] += 1
            self._update_workflow_type_metrics(request.workflow_type)
            self._update_average_processing_time(processing_time)

            request.completed_at = datetime.utcnow()

            logger.debug(
                f"Completed workflow {request.workflow_id} in {processing_time:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Error processing workflow {request.workflow_id}: {e}")

            # Handle retry logic
            if request.retry_count < request.max_retries:
                request.retry_count += 1
                await self.workflow_queue.put((request.priority.value, request))
                logger.info(
                    f"Retrying workflow {request.workflow_id} (attempt {request.retry_count})"
                )
            else:
                # Create error response
                response = AgentWorkflowResponse(
                    workflow_id=request.workflow_id,
                    session_id=request.session_id,
                    success=False,
                    result={},
                    agent_calls_made=[],
                    processing_time_ms=0,
                    error_message=str(e),
                )

                # Send error update
                await self._send_workflow_update(request.session_id, response)

                self.metrics["workflow_failures"] += 1
                request.completed_at = datetime.utcnow()

        finally:
            # Clean up completed workflow
            if request.completed_at:
                await self._cleanup_completed_workflow(request.workflow_id)

    async def _process_narrative_generation_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process narrative generation workflow."""
        try:
            payload = request.payload
            context = request.context

            # Use narrative agent to generate content
            narrative_prompt = {
                "type": payload.get("narrative_type", "general"),
                "context": context,
                "payload": payload,
            }

            result = await self.narrative_agent.generate_narrative(narrative_prompt)

            # Send narrative to WebSocket if requested
            if payload.get("send_to_websocket", True):
                await self._send_narrative_to_websocket(request.session_id, result)

            self.metrics["narrative_workflows"] += 1

            return {
                "narrative_result": result,
                "agent_calls_made": ["narrative_generator_agent"],
                "workflow_type": "narrative_generation",
            }

        except Exception as e:
            logger.error(f"Error in narrative generation workflow: {e}")
            raise

    async def _process_input_processing_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process input processing workflow."""
        try:
            payload = request.payload

            # Use input processor agent
            input_data = {
                "text": payload.get("input_text", ""),
                "type": payload.get("input_type", "text"),
                "context": request.context,
            }

            result = await self.input_processor.process_input(input_data)

            self.metrics["input_processing_workflows"] += 1

            return {
                "processed_input": result,
                "agent_calls_made": ["input_processor_agent"],
                "workflow_type": "input_processing",
            }

        except Exception as e:
            logger.error(f"Error in input processing workflow: {e}")
            raise

    async def _process_world_building_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process world building workflow."""
        try:
            payload = request.payload

            # Use world builder agent
            world_request = {
                "world_id": payload.get("world_id"),
                "action": payload.get("action", "get_context"),
                "context": request.context,
            }

            result = await self.world_builder.process_world_request(world_request)

            self.metrics["world_building_workflows"] += 1

            return {
                "world_result": result,
                "agent_calls_made": ["world_builder_agent"],
                "workflow_type": "world_building",
            }

        except Exception as e:
            logger.error(f"Error in world building workflow: {e}")
            raise

    async def _process_therapeutic_intervention_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process therapeutic intervention workflow."""
        try:
            payload = request.payload

            # Use narrative agent for therapeutic content
            therapeutic_prompt = {
                "type": "therapeutic_intervention",
                "intervention_type": payload.get("intervention_type"),
                "context": request.context,
                "therapeutic_data": payload.get("therapeutic_data", {}),
            }

            result = await self.narrative_agent.generate_narrative(therapeutic_prompt)

            # Send therapeutic intervention to WebSocket
            await self._send_therapeutic_intervention_to_websocket(
                request.session_id, result
            )

            self.metrics["therapeutic_workflows"] += 1

            return {
                "therapeutic_result": result,
                "agent_calls_made": ["narrative_generator_agent"],
                "workflow_type": "therapeutic_intervention",
            }

        except Exception as e:
            logger.error(f"Error in therapeutic intervention workflow: {e}")
            raise

    async def _process_choice_generation_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process choice generation workflow."""
        try:
            payload = request.payload

            # Use narrative agent to generate choices
            choice_prompt = {
                "type": "choice_generation",
                "narrative_context": payload.get("narrative_context", {}),
                "context": request.context,
            }

            result = await self.narrative_agent.generate_choices(choice_prompt)

            # Send choices to WebSocket
            await self._send_choices_to_websocket(request.session_id, result)

            return {
                "choices_result": result,
                "agent_calls_made": ["narrative_generator_agent"],
                "workflow_type": "choice_generation",
            }

        except Exception as e:
            logger.error(f"Error in choice generation workflow: {e}")
            raise

    async def _process_scene_transition_workflow(
        self, request: AgentWorkflowRequest
    ) -> dict[str, Any]:
        """Process scene transition workflow."""
        try:
            payload = request.payload

            # Use multiple agents for scene transition
            agent_calls = []

            # Get world context
            world_context = await self.world_builder.get_world_context(
                payload.get("world_id")
            )
            agent_calls.append("world_builder_agent")

            # Generate transition narrative
            transition_prompt = {
                "type": "scene_transition",
                "from_scene": payload.get("from_scene"),
                "to_scene": payload.get("to_scene"),
                "world_context": world_context,
                "context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                transition_prompt
            )
            agent_calls.append("narrative_generator_agent")

            # Send scene transition to WebSocket
            await self._send_scene_transition_to_websocket(
                request.session_id, narrative_result
            )

            return {
                "transition_result": narrative_result,
                "world_context": world_context,
                "agent_calls_made": agent_calls,
                "workflow_type": "scene_transition",
            }

        except Exception as e:
            logger.error(f"Error in scene transition workflow: {e}")
            raise

    async def _send_workflow_update(
        self, session_id: str, response: AgentWorkflowResponse
    ) -> None:
        """Send workflow update to WebSocket."""
        try:
            if not self.enable_real_time_updates:
                return

            update_message = {
                "type": "workflow_update",
                "session_id": session_id,
                "workflow_id": response.workflow_id,
                "success": response.success,
                "processing_time_ms": response.processing_time_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if response.error_message:
                update_message["error"] = response.error_message

            await self.chat_manager.broadcast_to_session(session_id, update_message)
            self.metrics["real_time_messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending workflow update: {e}")

    async def _send_narrative_to_websocket(
        self, session_id: str, narrative_result: dict[str, Any]
    ) -> None:
        """Send narrative result to WebSocket."""
        try:
            narrative_message = {
                "type": "narrative_response",
                "session_id": session_id,
                "content": {
                    "text": narrative_result.get("narrative_text", ""),
                    "scene_updates": narrative_result.get("scene_updates", {}),
                    "therapeutic_elements": narrative_result.get(
                        "therapeutic_elements", {}
                    ),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"source": "agent_orchestration"},
            }

            await self.chat_manager.broadcast_to_session(session_id, narrative_message)
            self.metrics["real_time_messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending narrative to WebSocket: {e}")

    async def _send_therapeutic_intervention_to_websocket(
        self, session_id: str, therapeutic_result: dict[str, Any]
    ) -> None:
        """Send therapeutic intervention to WebSocket."""
        try:
            intervention_message = {
                "type": "therapeutic_intervention",
                "session_id": session_id,
                "content": {
                    "intervention_type": therapeutic_result.get("intervention_type"),
                    "message": therapeutic_result.get("narrative_text", ""),
                    "resources": therapeutic_result.get("resources", []),
                    "severity": therapeutic_result.get("severity", "low"),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"source": "agent_orchestration"},
            }

            await self.chat_manager.broadcast_to_session(
                session_id, intervention_message
            )
            self.metrics["real_time_messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending therapeutic intervention to WebSocket: {e}")

    async def _send_choices_to_websocket(
        self, session_id: str, choices_result: dict[str, Any]
    ) -> None:
        """Send choices to WebSocket."""
        try:
            choices_message = {
                "type": "choice_request",
                "session_id": session_id,
                "content": {
                    "prompt": choices_result.get("prompt", "What do you do?"),
                    "choices": choices_result.get("choices", []),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"source": "agent_orchestration"},
            }

            await self.chat_manager.broadcast_to_session(session_id, choices_message)
            self.metrics["real_time_messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending choices to WebSocket: {e}")

    async def _send_scene_transition_to_websocket(
        self, session_id: str, transition_result: dict[str, Any]
    ) -> None:
        """Send scene transition to WebSocket."""
        try:
            transition_message = {
                "type": "scene_transition",
                "session_id": session_id,
                "content": {
                    "transition_text": transition_result.get("narrative_text", ""),
                    "new_scene": transition_result.get("new_scene", {}),
                    "scene_updates": transition_result.get("scene_updates", {}),
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"source": "agent_orchestration"},
            }

            await self.chat_manager.broadcast_to_session(session_id, transition_message)
            self.metrics["real_time_messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending scene transition to WebSocket: {e}")

    async def _subscribe_session_to_workflow(
        self, session_id: str, workflow_id: str
    ) -> None:
        """Subscribe a session to workflow updates."""
        if session_id not in self.session_subscriptions:
            self.session_subscriptions[session_id] = []

        if workflow_id not in self.session_subscriptions[session_id]:
            self.session_subscriptions[session_id].append(workflow_id)

    async def _cleanup_completed_workflow(self, workflow_id: str) -> None:
        """Clean up completed workflow."""
        try:
            # Remove from active workflows
            if workflow_id in self.active_workflows:
                request = self.active_workflows[workflow_id]
                del self.active_workflows[workflow_id]

                # Remove from session subscriptions
                session_id = request.session_id
                if session_id in self.session_subscriptions:
                    if workflow_id in self.session_subscriptions[session_id]:
                        self.session_subscriptions[session_id].remove(workflow_id)

                    # Clean up empty subscription lists
                    if not self.session_subscriptions[session_id]:
                        del self.session_subscriptions[session_id]

        except Exception as e:
            logger.error(f"Error cleaning up workflow {workflow_id}: {e}")

    async def _real_time_update_loop(self) -> None:
        """Background loop for sending real-time updates."""
        logger.info("Started real-time update loop")

        while self.is_running:
            try:
                # Send periodic status updates
                await asyncio.sleep(5)  # Update every 5 seconds

                # This could send periodic status updates to active sessions
                # For now, we'll just maintain the loop structure

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in real-time update loop: {e}")
                await asyncio.sleep(1)

        logger.info("Stopped real-time update loop")

    def _update_workflow_type_metrics(self, workflow_type: AgentWorkflowType) -> None:
        """Update metrics for specific workflow types."""
        if workflow_type == AgentWorkflowType.NARRATIVE_GENERATION:
            self.metrics["narrative_workflows"] += 1
        elif workflow_type == AgentWorkflowType.INPUT_PROCESSING:
            self.metrics["input_processing_workflows"] += 1
        elif workflow_type == AgentWorkflowType.WORLD_BUILDING:
            self.metrics["world_building_workflows"] += 1
        elif workflow_type == AgentWorkflowType.THERAPEUTIC_INTERVENTION:
            self.metrics["therapeutic_workflows"] += 1

    def _update_average_processing_time(self, processing_time_ms: float) -> None:
        """Update average processing time metric."""
        current_avg = self.metrics["average_processing_time_ms"]
        count = self.metrics["workflows_processed"]
        new_avg = (current_avg * (count - 1) + processing_time_ms) / count
        self.metrics["average_processing_time_ms"] = new_avg

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the bridge service."""
        return {
            **self.metrics,
            "active_workflows": len(self.active_workflows),
            "queued_workflows": self.workflow_queue.qsize(),
            "session_subscriptions": len(self.session_subscriptions),
            "is_running": self.is_running,
        }
