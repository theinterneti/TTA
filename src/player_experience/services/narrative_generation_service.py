"""
Narrative Generation Service

This service connects the existing NarrativeGeneratorAgent with the real-time chat interface
for dynamic storytelling, providing seamless integration between agent orchestration and gameplay.
"""

import asyncio
import logging
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

from .story_context_session_integration import StoryContextSessionIntegration

logger = logging.getLogger(__name__)


class NarrativeRequestType(str, Enum):
    """Types of narrative generation requests."""

    OPENING_NARRATIVE = "opening_narrative"
    PLAYER_ACTION_RESPONSE = "player_action_response"
    CHOICE_CONSEQUENCE = "choice_consequence"
    SCENE_TRANSITION = "scene_transition"
    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"
    WORLD_DESCRIPTION = "world_description"
    CHARACTER_INTERACTION = "character_interaction"


@dataclass
class NarrativeRequest:
    """Request for narrative generation."""

    request_type: NarrativeRequestType
    session_id: str
    player_id: str
    content: dict[str, Any]
    context: dict[str, Any]
    priority: int = 1  # 1=high, 2=medium, 3=low
    timeout_seconds: int = 30

    def __post_init__(self):
        self.created_at = datetime.utcnow()


@dataclass
class NarrativeResponse:
    """Response from narrative generation."""

    request_id: str
    session_id: str
    narrative_text: str
    choices: list[dict[str, Any]] | None = None
    scene_updates: dict[str, Any] | None = None
    therapeutic_elements: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    success: bool = True
    error_message: str | None = None

    def to_chat_message(self) -> dict[str, Any]:
        """Convert to chat message format."""
        content = {
            "text": self.narrative_text,
            "scene_updates": self.scene_updates or {},
            "therapeutic_elements": self.therapeutic_elements or {},
        }

        if self.choices:
            content["choices"] = self.choices

        return {
            "type": "narrative_response",
            "session_id": self.session_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": self.metadata or {},
        }


class NarrativeGenerationService:
    """
    Service for generating dynamic narratives using agent orchestration.

    Bridges the existing NarrativeGeneratorAgent, InputProcessorAgent, and WorldBuilderAgent
    with the real-time chat interface to provide contextual, therapeutic storytelling.
    """

    def __init__(
        self,
        narrative_agent: NarrativeGeneratorAgentProxy | None = None,
        input_processor: InputProcessorAgentProxy | None = None,
        world_builder: WorldBuilderAgentProxy | None = None,
        session_integration: StoryContextSessionIntegration | None = None,
    ):
        """
        Initialize the Narrative Generation Service.

        Args:
            narrative_agent: Narrative generator agent proxy
            input_processor: Input processor agent proxy
            world_builder: World builder agent proxy
            session_integration: Story context session integration service
        """
        self.narrative_agent = narrative_agent or NarrativeGeneratorAgentProxy()
        self.input_processor = input_processor or InputProcessorAgentProxy()
        self.world_builder = world_builder or WorldBuilderAgentProxy()
        self.session_integration = (
            session_integration or StoryContextSessionIntegration()
        )

        # Request queue and processing
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.active_requests: dict[str, NarrativeRequest] = {}
        self.processing_task: asyncio.Task | None = None

        # Configuration
        self.max_concurrent_requests = 5
        self.default_timeout_seconds = 30
        self.retry_attempts = 2

        # Metrics
        self.metrics = {
            "narratives_generated": 0,
            "opening_narratives_created": 0,
            "player_actions_processed": 0,
            "choices_generated": 0,
            "therapeutic_interventions": 0,
            "agent_calls_made": 0,
            "generation_failures": 0,
            "average_generation_time_ms": 0,
        }

        # Start processing
        self._start_processing()

        logger.info("NarrativeGenerationService initialized")

    async def generate_opening_narrative(
        self,
        session_id: str,
        character_id: str,
        world_id: str,
        therapeutic_goals: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """
        Generate opening narrative for a new story session.

        Args:
            session_id: Session identifier
            character_id: Character identifier
            world_id: World identifier
            therapeutic_goals: Optional therapeutic goals

        Returns:
            Narrative response dictionary or None
        """
        try:
            # Get session context
            narrative_context = (
                await self.session_integration.get_session_narrative_context(session_id)
            )
            if not narrative_context:
                logger.error(f"No narrative context found for session {session_id}")
                return None

            # Create narrative request
            request = NarrativeRequest(
                request_type=NarrativeRequestType.OPENING_NARRATIVE,
                session_id=session_id,
                player_id=narrative_context.get("player_id", ""),
                content={
                    "character_id": character_id,
                    "world_id": world_id,
                    "therapeutic_goals": therapeutic_goals or [],
                },
                context=narrative_context,
                priority=1,
            )

            # Process request
            response = await self._process_narrative_request(request)

            if response and response.success:
                # Update session with opening narrative
                await self.session_integration.update_narrative_state(
                    session_id,
                    {
                        "current_scene": "opening_complete",
                        "opening_narrative": response.narrative_text,
                        "scene_history": ["opening"],
                    },
                )

                self.metrics["opening_narratives_created"] += 1
                return response.to_chat_message()

            return None

        except Exception as e:
            logger.error(f"Error generating opening narrative: {e}")
            self.metrics["generation_failures"] += 1
            return None

    async def process_player_action(
        self, session_id: str, action_text: str, action_type: str = "narrative_input"
    ) -> dict[str, Any] | None:
        """
        Process player action and generate narrative response.

        Args:
            session_id: Session identifier
            action_text: Player action text
            action_type: Type of action

        Returns:
            Narrative response dictionary or None
        """
        try:
            # Get session context
            narrative_context = (
                await self.session_integration.get_session_narrative_context(session_id)
            )
            if not narrative_context:
                logger.error(f"No narrative context found for session {session_id}")
                return None

            # Process input through input processor agent
            processed_input = await self._process_player_input(
                action_text, action_type, narrative_context
            )

            # Create narrative request
            request = NarrativeRequest(
                request_type=NarrativeRequestType.PLAYER_ACTION_RESPONSE,
                session_id=session_id,
                player_id=narrative_context.get("player_id", ""),
                content={
                    "action_text": action_text,
                    "action_type": action_type,
                    "processed_input": processed_input,
                },
                context=narrative_context,
                priority=1,
            )

            # Process request
            response = await self._process_narrative_request(request)

            if response and response.success:
                # Update session with action and response
                await self._update_session_with_action_response(
                    session_id, action_text, response
                )

                self.metrics["player_actions_processed"] += 1
                return response.to_chat_message()

            return None

        except Exception as e:
            logger.error(f"Error processing player action: {e}")
            self.metrics["generation_failures"] += 1
            return None

    async def generate_choice_consequence(
        self, session_id: str, choice_id: str, choice_text: str
    ) -> dict[str, Any] | None:
        """
        Generate narrative consequence for a player choice.

        Args:
            session_id: Session identifier
            choice_id: Choice identifier
            choice_text: Text of the chosen option

        Returns:
            Narrative response dictionary or None
        """
        try:
            # Get session context
            narrative_context = (
                await self.session_integration.get_session_narrative_context(session_id)
            )
            if not narrative_context:
                logger.error(f"No narrative context found for session {session_id}")
                return None

            # Create narrative request
            request = NarrativeRequest(
                request_type=NarrativeRequestType.CHOICE_CONSEQUENCE,
                session_id=session_id,
                player_id=narrative_context.get("player_id", ""),
                content={"choice_id": choice_id, "choice_text": choice_text},
                context=narrative_context,
                priority=1,
            )

            # Process request
            response = await self._process_narrative_request(request)

            if response and response.success:
                # Update session with choice and consequence
                await self._update_session_with_choice_consequence(
                    session_id, choice_id, choice_text, response
                )

                self.metrics["choices_generated"] += 1
                return response.to_chat_message()

            return None

        except Exception as e:
            logger.error(f"Error generating choice consequence: {e}")
            self.metrics["generation_failures"] += 1
            return None

    async def generate_therapeutic_intervention(
        self, session_id: str, intervention_type: str, context_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Generate therapeutic intervention narrative.

        Args:
            session_id: Session identifier
            intervention_type: Type of therapeutic intervention
            context_data: Context data for the intervention

        Returns:
            Narrative response dictionary or None
        """
        try:
            # Get session context
            narrative_context = (
                await self.session_integration.get_session_narrative_context(session_id)
            )
            if not narrative_context:
                logger.error(f"No narrative context found for session {session_id}")
                return None

            # Create narrative request
            request = NarrativeRequest(
                request_type=NarrativeRequestType.THERAPEUTIC_INTERVENTION,
                session_id=session_id,
                player_id=narrative_context.get("player_id", ""),
                content={
                    "intervention_type": intervention_type,
                    "context_data": context_data,
                },
                context=narrative_context,
                priority=1,
            )

            # Process request
            response = await self._process_narrative_request(request)

            if response and response.success:
                self.metrics["therapeutic_interventions"] += 1
                return response.to_chat_message()

            return None

        except Exception as e:
            logger.error(f"Error generating therapeutic intervention: {e}")
            self.metrics["generation_failures"] += 1
            return None

    # Private methods

    async def _process_narrative_request(
        self, request: NarrativeRequest
    ) -> NarrativeResponse | None:
        """Process a narrative generation request using appropriate agents."""
        try:
            start_time = datetime.utcnow()

            # Generate narrative based on request type
            if request.request_type == NarrativeRequestType.OPENING_NARRATIVE:
                response = await self._generate_opening_narrative_content(request)
            elif request.request_type == NarrativeRequestType.PLAYER_ACTION_RESPONSE:
                response = await self._generate_action_response_content(request)
            elif request.request_type == NarrativeRequestType.CHOICE_CONSEQUENCE:
                response = await self._generate_choice_consequence_content(request)
            elif request.request_type == NarrativeRequestType.THERAPEUTIC_INTERVENTION:
                response = await self._generate_therapeutic_intervention_content(
                    request
                )
            else:
                response = await self._generate_generic_narrative_content(request)

            # Update metrics
            if response and response.success:
                self.metrics["narratives_generated"] += 1

                # Update average generation time
                generation_time = (
                    datetime.utcnow() - start_time
                ).total_seconds() * 1000
                current_avg = self.metrics["average_generation_time_ms"]
                count = self.metrics["narratives_generated"]
                new_avg = (current_avg * (count - 1) + generation_time) / count
                self.metrics["average_generation_time_ms"] = new_avg

            return response

        except Exception as e:
            logger.error(f"Error processing narrative request: {e}")
            self.metrics["generation_failures"] += 1
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="I'm having trouble generating a response right now. Please try again.",
                success=False,
                error_message=str(e),
            )

    async def _generate_opening_narrative_content(
        self, request: NarrativeRequest
    ) -> NarrativeResponse:
        """Generate opening narrative content using agents."""
        try:
            # Use world builder to get world context
            world_context = await self.world_builder.get_world_context(
                request.content["world_id"]
            )

            # Use narrative generator to create opening
            narrative_prompt = {
                "type": "opening_narrative",
                "character_id": request.content["character_id"],
                "world_context": world_context,
                "therapeutic_goals": request.content.get("therapeutic_goals", []),
                "session_context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                narrative_prompt
            )
            self.metrics["agent_calls_made"] += 1

            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text=narrative_result.get(
                    "narrative_text", "Your adventure begins..."
                ),
                scene_updates=narrative_result.get("scene_updates", {}),
                therapeutic_elements=narrative_result.get("therapeutic_elements", {}),
                metadata={"generation_type": "opening_narrative"},
            )

        except Exception as e:
            logger.error(f"Error generating opening narrative content: {e}")
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="Welcome to your therapeutic adventure. Let's begin your journey of growth and discovery.",
                success=False,
                error_message=str(e),
            )

    async def _generate_action_response_content(
        self, request: NarrativeRequest
    ) -> NarrativeResponse:
        """Generate action response content using agents."""
        try:
            # Use narrative generator to respond to action
            narrative_prompt = {
                "type": "action_response",
                "action_text": request.content["action_text"],
                "action_type": request.content["action_type"],
                "processed_input": request.content.get("processed_input", {}),
                "session_context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                narrative_prompt
            )
            self.metrics["agent_calls_made"] += 1

            # Check if choices should be generated
            choices = None
            if narrative_result.get("should_present_choices", False):
                choices = await self._generate_choices(
                    request.context, narrative_result
                )

            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text=narrative_result.get(
                    "narrative_text", "The story continues..."
                ),
                choices=choices,
                scene_updates=narrative_result.get("scene_updates", {}),
                therapeutic_elements=narrative_result.get("therapeutic_elements", {}),
                metadata={"generation_type": "action_response"},
            )

        except Exception as e:
            logger.error(f"Error generating action response content: {e}")
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="Your action has an interesting effect on the story. What would you like to do next?",
                success=False,
                error_message=str(e),
            )

    async def _generate_choice_consequence_content(
        self, request: NarrativeRequest
    ) -> NarrativeResponse:
        """Generate choice consequence content using agents."""
        try:
            narrative_prompt = {
                "type": "choice_consequence",
                "choice_id": request.content["choice_id"],
                "choice_text": request.content["choice_text"],
                "session_context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                narrative_prompt
            )
            self.metrics["agent_calls_made"] += 1

            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text=narrative_result.get(
                    "narrative_text", "Your choice leads to new developments..."
                ),
                scene_updates=narrative_result.get("scene_updates", {}),
                therapeutic_elements=narrative_result.get("therapeutic_elements", {}),
                metadata={"generation_type": "choice_consequence"},
            )

        except Exception as e:
            logger.error(f"Error generating choice consequence content: {e}")
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="Your choice has consequences that unfold in the story...",
                success=False,
                error_message=str(e),
            )

    async def _generate_therapeutic_intervention_content(
        self, request: NarrativeRequest
    ) -> NarrativeResponse:
        """Generate therapeutic intervention content using agents."""
        try:
            narrative_prompt = {
                "type": "therapeutic_intervention",
                "intervention_type": request.content["intervention_type"],
                "context_data": request.content["context_data"],
                "session_context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                narrative_prompt
            )
            self.metrics["agent_calls_made"] += 1

            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text=narrative_result.get(
                    "narrative_text",
                    "Let's take a moment to reflect on this experience...",
                ),
                therapeutic_elements=narrative_result.get("therapeutic_elements", {}),
                metadata={"generation_type": "therapeutic_intervention"},
            )

        except Exception as e:
            logger.error(f"Error generating therapeutic intervention content: {e}")
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="This is a good moment to pause and reflect on your journey so far.",
                success=False,
                error_message=str(e),
            )

    async def _generate_generic_narrative_content(
        self, request: NarrativeRequest
    ) -> NarrativeResponse:
        """Generate generic narrative content using agents."""
        try:
            narrative_prompt = {
                "type": "generic_narrative",
                "request_type": request.request_type.value,
                "content": request.content,
                "session_context": request.context,
            }

            narrative_result = await self.narrative_agent.generate_narrative(
                narrative_prompt
            )
            self.metrics["agent_calls_made"] += 1

            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text=narrative_result.get(
                    "narrative_text", "The story continues to unfold..."
                ),
                scene_updates=narrative_result.get("scene_updates", {}),
                therapeutic_elements=narrative_result.get("therapeutic_elements", {}),
                metadata={"generation_type": "generic_narrative"},
            )

        except Exception as e:
            logger.error(f"Error generating generic narrative content: {e}")
            return NarrativeResponse(
                request_id=f"req_{request.session_id}_{datetime.utcnow().timestamp()}",
                session_id=request.session_id,
                narrative_text="The narrative continues as your story unfolds...",
                success=False,
                error_message=str(e),
            )

    async def _process_player_input(
        self, action_text: str, action_type: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process player input through the input processor agent."""
        try:
            input_data = {"text": action_text, "type": action_type, "context": context}

            processed_result = await self.input_processor.process_input(input_data)
            self.metrics["agent_calls_made"] += 1

            return processed_result or {}

        except Exception as e:
            logger.error(f"Error processing player input: {e}")
            return {"raw_input": action_text, "processing_error": str(e)}

    async def _generate_choices(
        self, context: dict[str, Any], narrative_result: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate choices for the player."""
        try:
            choice_prompt = {
                "type": "choice_generation",
                "narrative_context": narrative_result,
                "session_context": context,
            }

            choice_result = await self.narrative_agent.generate_choices(choice_prompt)
            self.metrics["agent_calls_made"] += 1

            return choice_result.get("choices", [])

        except Exception as e:
            logger.error(f"Error generating choices: {e}")
            return []

    async def _update_session_with_action_response(
        self, session_id: str, action_text: str, response: NarrativeResponse
    ) -> None:
        """Update session with player action and narrative response."""
        try:
            narrative_updates = {
                "last_player_action": action_text,
                "last_narrative_response": response.narrative_text,
                "scene_updates": response.scene_updates or {},
                "choice_history": [],  # This would be updated with actual choice history
            }

            if response.scene_updates:
                narrative_updates.update(response.scene_updates)

            await self.session_integration.update_narrative_state(
                session_id, narrative_updates
            )

            # Update therapeutic progress if applicable
            if response.therapeutic_elements:
                therapeutic_updates = {
                    "last_therapeutic_elements": response.therapeutic_elements,
                    "therapeutic_interactions": [],  # This would track therapeutic interactions
                }
                await self.session_integration.update_therapeutic_progress(
                    session_id, therapeutic_updates
                )

        except Exception as e:
            logger.error(f"Error updating session with action response: {e}")

    async def _update_session_with_choice_consequence(
        self,
        session_id: str,
        choice_id: str,
        choice_text: str,
        response: NarrativeResponse,
    ) -> None:
        """Update session with choice and its consequence."""
        try:
            narrative_updates = {
                "last_choice_id": choice_id,
                "last_choice_text": choice_text,
                "last_choice_consequence": response.narrative_text,
                "scene_updates": response.scene_updates or {},
            }

            await self.session_integration.update_narrative_state(
                session_id, narrative_updates
            )

        except Exception as e:
            logger.error(f"Error updating session with choice consequence: {e}")

    def _start_processing(self) -> None:
        """Start the background processing task."""
        if not self.processing_task or self.processing_task.done():
            self.processing_task = asyncio.create_task(self._process_requests())

    async def _process_requests(self) -> None:
        """Background task to process narrative requests."""
        while True:
            try:
                # This would implement a proper request queue processing system
                await asyncio.sleep(0.1)  # Placeholder for actual processing logic
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in request processing loop: {e}")
                await asyncio.sleep(1)

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the narrative generation service."""
        return {
            **self.metrics,
            "active_requests": len(self.active_requests),
            "max_concurrent_requests": self.max_concurrent_requests,
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the narrative generation service."""
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        logger.info("NarrativeGenerationService shutdown complete")
