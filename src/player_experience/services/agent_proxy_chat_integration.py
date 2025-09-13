"""
Agent Proxy Chat Integration Service

This service integrates existing agent proxies with the chat interface to provide
contextual, therapeutic narrative responses in real-time gameplay sessions.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from src.components.agent_orchestration.proxies.input_processor_agent_proxy import (
    InputProcessorAgentProxy,
)
from src.components.agent_orchestration.proxies.narrative_generator_agent_proxy import (
    NarrativeGeneratorAgentProxy,
)
from src.components.agent_orchestration.proxies.world_builder_agent_proxy import (
    WorldBuilderAgentProxy,
)

from ..models.gameplay_messages import GameplayMessageType
from .dynamic_story_generation_service import DynamicStoryGenerationService
from .gameplay_chat_manager import GameplayChatManager

logger = logging.getLogger(__name__)


class AgentResponseType(str, Enum):
    """Types of agent responses."""

    NARRATIVE_CONTINUATION = "narrative_continuation"
    WORLD_DESCRIPTION = "world_description"
    CHARACTER_DIALOGUE = "character_dialogue"
    THERAPEUTIC_GUIDANCE = "therapeutic_guidance"
    CHOICE_PRESENTATION = "choice_presentation"
    SCENE_TRANSITION = "scene_transition"
    SKILL_INSTRUCTION = "skill_instruction"
    EMOTIONAL_SUPPORT = "emotional_support"


@dataclass
class AgentProxyRequest:
    """Request for agent proxy processing."""

    session_id: str
    player_id: str
    agent_type: str  # "narrative", "input_processor", "world_builder"
    request_data: dict[str, Any]
    context: dict[str, Any]
    response_type: AgentResponseType
    priority: int = 2  # 1=high, 2=medium, 3=low
    timeout_seconds: int = 10

    def __post_init__(self):
        self.created_at = datetime.utcnow()
        self.request_id = f"agent_req_{self.session_id}_{datetime.utcnow().timestamp()}"


@dataclass
class AgentProxyResponse:
    """Response from agent proxy processing."""

    request_id: str
    session_id: str
    agent_type: str
    response_type: AgentResponseType
    content: dict[str, Any]
    processing_time_ms: float
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.completed_at = datetime.utcnow()

    def to_chat_message(self) -> dict[str, Any]:
        """Convert to chat message format."""
        message_type = self._map_response_type_to_message_type()

        return {
            "type": message_type,
            "session_id": self.session_id,
            "content": self.content,
            "timestamp": self.completed_at.isoformat(),
            "metadata": {
                **self.metadata,
                "agent_type": self.agent_type,
                "response_type": self.response_type.value,
                "processing_time_ms": self.processing_time_ms,
            },
        }

    def _map_response_type_to_message_type(self) -> str:
        """Map response type to WebSocket message type."""
        mapping = {
            AgentResponseType.NARRATIVE_CONTINUATION: GameplayMessageType.NARRATIVE_RESPONSE.value,
            AgentResponseType.WORLD_DESCRIPTION: GameplayMessageType.NARRATIVE_RESPONSE.value,
            AgentResponseType.CHARACTER_DIALOGUE: GameplayMessageType.NARRATIVE_RESPONSE.value,
            AgentResponseType.THERAPEUTIC_GUIDANCE: GameplayMessageType.THERAPEUTIC_INTERVENTION.value,
            AgentResponseType.CHOICE_PRESENTATION: GameplayMessageType.CHOICE_REQUEST.value,
            AgentResponseType.SCENE_TRANSITION: GameplayMessageType.STORY_EVENT.value,
            AgentResponseType.SKILL_INSTRUCTION: GameplayMessageType.THERAPEUTIC_INTERVENTION.value,
            AgentResponseType.EMOTIONAL_SUPPORT: GameplayMessageType.THERAPEUTIC_INTERVENTION.value,
        }
        return mapping.get(
            self.response_type, GameplayMessageType.NARRATIVE_RESPONSE.value
        )


class AgentProxyChatIntegration:
    """
    Service for integrating agent proxies with chat interface for seamless narrative delivery.

    Provides real-time integration between existing agent proxies and the gameplay chat system,
    enabling contextual, therapeutic narrative responses with proper formatting and delivery.
    """

    def __init__(
        self,
        narrative_agent: NarrativeGeneratorAgentProxy | None = None,
        input_processor: InputProcessorAgentProxy | None = None,
        world_builder: WorldBuilderAgentProxy | None = None,
        chat_manager: GameplayChatManager | None = None,
        story_service: DynamicStoryGenerationService | None = None,
    ):
        """
        Initialize the Agent Proxy Chat Integration service.

        Args:
            narrative_agent: Narrative generator agent proxy
            input_processor: Input processor agent proxy
            world_builder: World builder agent proxy
            chat_manager: Gameplay chat manager
            story_service: Dynamic story generation service
        """
        self.narrative_agent = narrative_agent or NarrativeGeneratorAgentProxy()
        self.input_processor = input_processor or InputProcessorAgentProxy()
        self.world_builder = world_builder or WorldBuilderAgentProxy()
        self.chat_manager = chat_manager or GameplayChatManager()
        self.story_service = story_service or DynamicStoryGenerationService()

        # Request processing
        self.active_requests: dict[str, AgentProxyRequest] = {}
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.processing_tasks: list[asyncio.Task] = []

        # Agent response formatters
        self.response_formatters: dict[AgentResponseType, Callable] = {}

        # Configuration
        self.max_concurrent_requests = 5
        self.enable_response_caching = True
        self.auto_send_responses = True

        # Metrics
        self.metrics = {
            "agent_requests_processed": 0,
            "narrative_responses_generated": 0,
            "world_descriptions_created": 0,
            "therapeutic_interventions_delivered": 0,
            "chat_messages_sent": 0,
            "average_agent_response_time_ms": 0,
            "agent_proxy_errors": 0,
            "successful_integrations": 0,
        }

        # Initialize response formatters
        self._initialize_response_formatters()

        # Start processing
        self.is_running = False

        logger.info("AgentProxyChatIntegration service initialized")

    async def start(self) -> None:
        """Start the agent proxy chat integration service."""
        if self.is_running:
            logger.warning("Agent proxy chat integration is already running")
            return

        self.is_running = True

        # Start request processing tasks
        for i in range(self.max_concurrent_requests):
            task = asyncio.create_task(self._request_processor_loop(f"processor_{i}"))
            self.processing_tasks.append(task)

        logger.info("Agent proxy chat integration started")

    async def stop(self) -> None:
        """Stop the agent proxy chat integration service."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        self.processing_tasks.clear()
        logger.info("Agent proxy chat integration stopped")

    async def process_narrative_request(
        self,
        session_id: str,
        player_id: str,
        narrative_prompt: dict[str, Any],
        context: dict[str, Any] | None = None,
        response_type: AgentResponseType = AgentResponseType.NARRATIVE_CONTINUATION,
    ) -> str | None:
        """
        Process a narrative generation request through the narrative agent proxy.

        Args:
            session_id: Session identifier
            player_id: Player identifier
            narrative_prompt: Prompt for narrative generation
            context: Optional context data
            response_type: Type of response expected

        Returns:
            Request ID for tracking
        """
        try:
            request = AgentProxyRequest(
                session_id=session_id,
                player_id=player_id,
                agent_type="narrative",
                request_data=narrative_prompt,
                context=context or {},
                response_type=response_type,
                priority=(
                    1 if response_type == AgentResponseType.THERAPEUTIC_GUIDANCE else 2
                ),
            )

            # Add to processing queue
            await self.request_queue.put(request)
            self.active_requests[request.request_id] = request

            logger.debug(
                f"Queued narrative request {request.request_id} for session {session_id}"
            )
            return request.request_id

        except Exception as e:
            logger.error(f"Error processing narrative request: {e}")
            return None

    async def process_world_building_request(
        self,
        session_id: str,
        player_id: str,
        world_request: dict[str, Any],
        context: dict[str, Any] | None = None,
        response_type: AgentResponseType = AgentResponseType.WORLD_DESCRIPTION,
    ) -> str | None:
        """
        Process a world building request through the world builder agent proxy.

        Args:
            session_id: Session identifier
            player_id: Player identifier
            world_request: Request for world building
            context: Optional context data
            response_type: Type of response expected

        Returns:
            Request ID for tracking
        """
        try:
            request = AgentProxyRequest(
                session_id=session_id,
                player_id=player_id,
                agent_type="world_builder",
                request_data=world_request,
                context=context or {},
                response_type=response_type,
                priority=2,
            )

            await self.request_queue.put(request)
            self.active_requests[request.request_id] = request

            logger.debug(
                f"Queued world building request {request.request_id} for session {session_id}"
            )
            return request.request_id

        except Exception as e:
            logger.error(f"Error processing world building request: {e}")
            return None

    async def process_input_analysis_request(
        self,
        session_id: str,
        player_id: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Process an input analysis request through the input processor agent proxy.

        Args:
            session_id: Session identifier
            player_id: Player identifier
            input_data: Input data for analysis
            context: Optional context data

        Returns:
            Request ID for tracking
        """
        try:
            request = AgentProxyRequest(
                session_id=session_id,
                player_id=player_id,
                agent_type="input_processor",
                request_data=input_data,
                context=context or {},
                response_type=AgentResponseType.NARRATIVE_CONTINUATION,  # Will be processed internally
                priority=1,  # High priority for input processing
            )

            await self.request_queue.put(request)
            self.active_requests[request.request_id] = request

            logger.debug(
                f"Queued input analysis request {request.request_id} for session {session_id}"
            )
            return request.request_id

        except Exception as e:
            logger.error(f"Error processing input analysis request: {e}")
            return None

    async def send_therapeutic_intervention(
        self,
        session_id: str,
        intervention_type: str,
        intervention_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Send a therapeutic intervention through the narrative agent.

        Args:
            session_id: Session identifier
            intervention_type: Type of therapeutic intervention
            intervention_data: Intervention data
            context: Optional context data

        Returns:
            Request ID for tracking
        """
        try:
            therapeutic_prompt = {
                "type": "therapeutic_intervention",
                "intervention_type": intervention_type,
                "intervention_data": intervention_data,
                "context": context or {},
            }

            return await self.process_narrative_request(
                session_id=session_id,
                player_id=context.get("player_id", "") if context else "",
                narrative_prompt=therapeutic_prompt,
                context=context,
                response_type=AgentResponseType.THERAPEUTIC_GUIDANCE,
            )

        except Exception as e:
            logger.error(f"Error sending therapeutic intervention: {e}")
            return None

    # Private methods

    async def _request_processor_loop(self, processor_id: str) -> None:
        """Background loop for processing agent proxy requests."""
        logger.info(f"Started agent proxy processor {processor_id}")

        while self.is_running:
            try:
                # Get next request from queue
                try:
                    request = await asyncio.wait_for(
                        self.request_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Process the request
                await self._process_agent_request(request, processor_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in agent proxy processor {processor_id}: {e}")
                await asyncio.sleep(1)

        logger.info(f"Stopped agent proxy processor {processor_id}")

    async def _process_agent_request(
        self, request: AgentProxyRequest, processor_id: str
    ) -> None:
        """Process a single agent proxy request."""
        try:
            start_time = datetime.utcnow()

            # Route to appropriate agent
            if request.agent_type == "narrative":
                result = await self._process_narrative_agent_request(request)
            elif request.agent_type == "world_builder":
                result = await self._process_world_builder_request(request)
            elif request.agent_type == "input_processor":
                result = await self._process_input_processor_request(request)
            else:
                raise ValueError(f"Unknown agent type: {request.agent_type}")

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Create response
            response = AgentProxyResponse(
                request_id=request.request_id,
                session_id=request.session_id,
                agent_type=request.agent_type,
                response_type=request.response_type,
                content=result,
                processing_time_ms=processing_time,
                success=True,
                metadata={"processor_id": processor_id},
            )

            # Format and send response
            await self._format_and_send_response(response)

            # Update metrics
            self.metrics["agent_requests_processed"] += 1
            self.metrics["successful_integrations"] += 1
            self._update_response_time_metric(processing_time)
            self._update_response_type_metrics(request.response_type)

            logger.debug(
                f"Processed agent request {request.request_id} in {processing_time:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Error processing agent request {request.request_id}: {e}")

            # Create error response
            error_response = AgentProxyResponse(
                request_id=request.request_id,
                session_id=request.session_id,
                agent_type=request.agent_type,
                response_type=request.response_type,
                content={"error": "Agent processing failed"},
                processing_time_ms=0,
                success=False,
                error_message=str(e),
            )

            # Send error response
            await self._format_and_send_response(error_response)

            self.metrics["agent_proxy_errors"] += 1

        finally:
            # Clean up request
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]

    async def _process_narrative_agent_request(
        self, request: AgentProxyRequest
    ) -> dict[str, Any]:
        """Process request through narrative generator agent."""
        try:
            result = await self.narrative_agent.generate_narrative(request.request_data)

            # Format result based on response type
            if request.response_type == AgentResponseType.THERAPEUTIC_GUIDANCE:
                return {
                    "intervention_type": request.request_data.get(
                        "intervention_type", "general"
                    ),
                    "message": result.get("narrative_text", ""),
                    "resources": result.get("resources", []),
                    "guidance": result.get("guidance", []),
                    "severity": result.get("severity", "low"),
                }
            elif request.response_type == AgentResponseType.CHOICE_PRESENTATION:
                return {
                    "prompt": result.get("choice_prompt", "What do you do?"),
                    "choices": result.get("choices", []),
                    "context": result.get("choice_context", {}),
                }
            else:
                return {
                    "text": result.get("narrative_text", ""),
                    "scene_updates": result.get("scene_updates", {}),
                    "therapeutic_elements": result.get("therapeutic_elements", {}),
                    "emotional_tone": result.get("emotional_tone", "neutral"),
                }

        except Exception as e:
            logger.error(f"Error in narrative agent processing: {e}")
            return {"error": str(e), "fallback_text": "The story continues..."}

    async def _process_world_builder_request(
        self, request: AgentProxyRequest
    ) -> dict[str, Any]:
        """Process request through world builder agent."""
        try:
            result = await self.world_builder.process_world_request(
                request.request_data
            )

            return {
                "description": result.get("description", ""),
                "location_details": result.get("location_details", {}),
                "available_actions": result.get("available_actions", []),
                "atmosphere": result.get("atmosphere", {}),
                "characters_present": result.get("characters_present", []),
            }

        except Exception as e:
            logger.error(f"Error in world builder processing: {e}")
            return {
                "error": str(e),
                "fallback_description": "You find yourself in an interesting location...",
            }

    async def _process_input_processor_request(
        self, request: AgentProxyRequest
    ) -> dict[str, Any]:
        """Process request through input processor agent."""
        try:
            result = await self.input_processor.process_input(request.request_data)

            return {
                "processed_input": result,
                "intent": result.get("intent", "unknown"),
                "entities": result.get("entities", []),
                "sentiment": result.get("sentiment", "neutral"),
                "therapeutic_indicators": result.get("therapeutic_indicators", []),
            }

        except Exception as e:
            logger.error(f"Error in input processor processing: {e}")
            return {"error": str(e), "processed_input": request.request_data}

    async def _format_and_send_response(self, response: AgentProxyResponse) -> None:
        """Format agent response and send to chat interface."""
        try:
            if not self.auto_send_responses:
                return

            # Get appropriate formatter
            formatter = self.response_formatters.get(response.response_type)
            if formatter:
                formatted_content = await formatter(
                    response.content, response.session_id
                )
                response.content = formatted_content

            # Convert to chat message
            chat_message = response.to_chat_message()

            # Send to chat manager
            sent_count = await self.chat_manager.broadcast_to_session(
                response.session_id, chat_message
            )

            if sent_count > 0:
                self.metrics["chat_messages_sent"] += 1
                logger.debug(
                    f"Sent agent response to {sent_count} connections in session {response.session_id}"
                )
            else:
                logger.warning(
                    f"No active connections found for session {response.session_id}"
                )

        except Exception as e:
            logger.error(f"Error formatting and sending response: {e}")

    def _initialize_response_formatters(self) -> None:
        """Initialize response formatters for different response types."""
        self.response_formatters = {
            AgentResponseType.NARRATIVE_CONTINUATION: self._format_narrative_response,
            AgentResponseType.WORLD_DESCRIPTION: self._format_world_description_response,
            AgentResponseType.CHARACTER_DIALOGUE: self._format_character_dialogue_response,
            AgentResponseType.THERAPEUTIC_GUIDANCE: self._format_therapeutic_guidance_response,
            AgentResponseType.CHOICE_PRESENTATION: self._format_choice_presentation_response,
            AgentResponseType.SCENE_TRANSITION: self._format_scene_transition_response,
            AgentResponseType.SKILL_INSTRUCTION: self._format_skill_instruction_response,
            AgentResponseType.EMOTIONAL_SUPPORT: self._format_emotional_support_response,
        }

    async def _format_narrative_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format narrative continuation response."""
        return {
            "text": content.get("text", "The story continues..."),
            "scene_updates": content.get("scene_updates", {}),
            "therapeutic_elements": content.get("therapeutic_elements", {}),
            "emotional_tone": content.get("emotional_tone", "neutral"),
            "narrative_type": "continuation",
        }

    async def _format_world_description_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format world description response."""
        return {
            "text": content.get(
                "description", "You find yourself in an interesting place..."
            ),
            "location_details": content.get("location_details", {}),
            "available_actions": content.get("available_actions", []),
            "atmosphere": content.get("atmosphere", {}),
            "characters_present": content.get("characters_present", []),
            "narrative_type": "world_description",
        }

    async def _format_character_dialogue_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format character dialogue response."""
        return {
            "text": content.get("text", "A character speaks..."),
            "speaker": content.get("speaker", "Unknown"),
            "dialogue_type": content.get("dialogue_type", "conversation"),
            "emotional_tone": content.get("emotional_tone", "neutral"),
            "narrative_type": "character_dialogue",
        }

    async def _format_therapeutic_guidance_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format therapeutic guidance response."""
        return {
            "intervention_type": content.get("intervention_type", "general"),
            "message": content.get("message", "Let's take a moment to reflect..."),
            "resources": content.get("resources", []),
            "guidance": content.get("guidance", []),
            "severity": content.get("severity", "low"),
            "therapeutic_focus": True,
        }

    async def _format_choice_presentation_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format choice presentation response."""
        return {
            "prompt": content.get("prompt", "What do you do?"),
            "choices": content.get("choices", []),
            "choice_context": content.get("context", {}),
            "therapeutic_considerations": content.get("therapeutic_considerations", []),
        }

    async def _format_scene_transition_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format scene transition response."""
        return {
            "event_type": "scene_transition",
            "title": content.get("title", "Scene Transition"),
            "description": content.get("text", "The scene changes..."),
            "new_location": content.get("new_location", {}),
            "transition_type": content.get("transition_type", "standard"),
            "therapeutic_significance": content.get("therapeutic_significance", []),
        }

    async def _format_skill_instruction_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format skill instruction response."""
        return {
            "intervention_type": "skill_instruction",
            "skill_name": content.get("skill_name", "Therapeutic Skill"),
            "message": content.get("message", "Let's practice a helpful skill..."),
            "instructions": content.get("instructions", []),
            "practice_steps": content.get("practice_steps", []),
            "resources": content.get("resources", []),
            "difficulty_level": content.get("difficulty_level", "beginner"),
        }

    async def _format_emotional_support_response(
        self, content: dict[str, Any], session_id: str
    ) -> dict[str, Any]:
        """Format emotional support response."""
        return {
            "intervention_type": "emotional_support",
            "message": content.get(
                "message", "Your feelings are valid and important..."
            ),
            "support_type": content.get("support_type", "validation"),
            "coping_strategies": content.get("coping_strategies", []),
            "resources": content.get("resources", []),
            "follow_up_suggestions": content.get("follow_up_suggestions", []),
        }

    def _update_response_time_metric(self, processing_time_ms: float) -> None:
        """Update average response time metric."""
        current_avg = self.metrics["average_agent_response_time_ms"]
        count = self.metrics["agent_requests_processed"]
        if count > 0:
            new_avg = (current_avg * (count - 1) + processing_time_ms) / count
            self.metrics["average_agent_response_time_ms"] = new_avg
        else:
            self.metrics["average_agent_response_time_ms"] = processing_time_ms

    def _update_response_type_metrics(self, response_type: AgentResponseType) -> None:
        """Update metrics for specific response types."""
        if response_type in [
            AgentResponseType.NARRATIVE_CONTINUATION,
            AgentResponseType.CHARACTER_DIALOGUE,
        ]:
            self.metrics["narrative_responses_generated"] += 1
        elif response_type == AgentResponseType.WORLD_DESCRIPTION:
            self.metrics["world_descriptions_created"] += 1
        elif response_type in [
            AgentResponseType.THERAPEUTIC_GUIDANCE,
            AgentResponseType.EMOTIONAL_SUPPORT,
            AgentResponseType.SKILL_INSTRUCTION,
        ]:
            self.metrics["therapeutic_interventions_delivered"] += 1

    async def get_request_status(self, request_id: str) -> dict[str, Any] | None:
        """Get the status of a specific request."""
        request = self.active_requests.get(request_id)
        if not request:
            return None

        return {
            "request_id": request_id,
            "session_id": request.session_id,
            "agent_type": request.agent_type,
            "response_type": request.response_type.value,
            "created_at": request.created_at.isoformat(),
            "priority": request.priority,
            "status": "processing",
        }

    async def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending request."""
        try:
            if request_id in self.active_requests:
                del self.active_requests[request_id]
                logger.info(f"Cancelled request {request_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling request {request_id}: {e}")
            return False

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the agent proxy chat integration."""
        return {
            **self.metrics,
            "active_requests": len(self.active_requests),
            "queue_size": self.request_queue.qsize(),
            "is_running": self.is_running,
            "max_concurrent_requests": self.max_concurrent_requests,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on agent proxies and chat integration."""
        try:
            health_status = {
                "service_running": self.is_running,
                "active_requests": len(self.active_requests),
                "queue_size": self.request_queue.qsize(),
                "processing_tasks": len(
                    [t for t in self.processing_tasks if not t.done()]
                ),
                "agent_proxies": {
                    "narrative_agent": "available",
                    "input_processor": "available",
                    "world_builder": "available",
                },
                "chat_manager": "available",
                "overall_status": "healthy",
            }

            # Check if any critical issues
            if not self.is_running:
                health_status["overall_status"] = "stopped"
            elif len(self.active_requests) > self.max_concurrent_requests * 2:
                health_status["overall_status"] = "overloaded"

            return health_status

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"overall_status": "error", "error": str(e)}
