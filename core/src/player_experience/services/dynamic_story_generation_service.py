"""
Dynamic Story Generation Service

This service translates player chat messages into agent orchestration requests and formats
agent responses for real-time delivery, enabling contextual and adaptive storytelling.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..models.gameplay_messages import GameplayMessageType
from .agent_orchestration_websocket_bridge import (
    AgentOrchestrationWebSocketBridge,
    AgentWorkflowType,
    WorkflowPriority,
)
from .narrative_generation_service import NarrativeGenerationService
from .story_context_session_integration import StoryContextSessionIntegration

logger = logging.getLogger(__name__)


class MessageIntentType(str, Enum):
    """Types of player message intents."""

    NARRATIVE_ACTION = "narrative_action"
    DIALOGUE_RESPONSE = "dialogue_response"
    EXPLORATION = "exploration"
    SKILL_PRACTICE = "skill_practice"
    REFLECTION = "reflection"
    THERAPEUTIC_EXERCISE = "therapeutic_exercise"
    QUESTION = "question"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    CHOICE_SELECTION = "choice_selection"
    SYSTEM_COMMAND = "system_command"


class ResponseComplexity(str, Enum):
    """Complexity levels for story responses."""

    SIMPLE = "simple"  # Brief acknowledgment or continuation
    MODERATE = "moderate"  # Standard narrative response
    COMPLEX = "complex"  # Multi-layered response with choices
    THERAPEUTIC = "therapeutic"  # Therapeutic intervention focus


@dataclass
class MessageAnalysis:
    """Analysis of a player message."""

    intent_type: MessageIntentType
    confidence: float
    emotional_tone: str
    therapeutic_indicators: list[str]
    narrative_elements: list[str]
    complexity_needed: ResponseComplexity
    urgency_level: int  # 1=low, 2=medium, 3=high, 4=critical
    context_requirements: list[str]

    def __post_init__(self):
        self.analyzed_at = datetime.utcnow()


@dataclass
class StoryGenerationRequest:
    """Request for dynamic story generation."""

    session_id: str
    player_id: str
    message_text: str
    message_analysis: MessageAnalysis
    session_context: dict[str, Any]
    narrative_context: dict[str, Any]
    therapeutic_context: dict[str, Any]

    def __post_init__(self):
        self.created_at = datetime.utcnow()


@dataclass
class StoryGenerationResponse:
    """Response from dynamic story generation."""

    session_id: str
    narrative_text: str
    response_type: str
    choices: list[dict[str, Any]] | None = None
    scene_updates: dict[str, Any] | None = None
    therapeutic_elements: dict[str, Any] | None = None
    follow_up_actions: list[str] | None = None
    metadata: dict[str, Any] | None = None

    def to_websocket_message(self) -> dict[str, Any]:
        """Convert to WebSocket message format."""
        content = {"text": self.narrative_text, "response_type": self.response_type}

        if self.choices:
            content["choices"] = self.choices
        if self.scene_updates:
            content["scene_updates"] = self.scene_updates
        if self.therapeutic_elements:
            content["therapeutic_elements"] = self.therapeutic_elements
        if self.follow_up_actions:
            content["follow_up_actions"] = self.follow_up_actions

        return {
            "type": GameplayMessageType.NARRATIVE_RESPONSE.value,
            "session_id": self.session_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": self.metadata or {},
        }


class DynamicStoryGenerationService:
    """
    Service for dynamic story generation with contextual agent responses.

    Analyzes player messages, determines appropriate narrative responses, and orchestrates
    multiple agents to generate contextual, therapeutic storytelling experiences.
    """

    def __init__(
        self,
        agent_bridge: AgentOrchestrationWebSocketBridge | None = None,
        session_integration: StoryContextSessionIntegration | None = None,
        narrative_service: NarrativeGenerationService | None = None,
    ):
        """
        Initialize the Dynamic Story Generation Service.

        Args:
            agent_bridge: Agent orchestration WebSocket bridge
            session_integration: Story context session integration
            narrative_service: Narrative generation service
        """
        self.agent_bridge = agent_bridge or AgentOrchestrationWebSocketBridge()
        self.session_integration = (
            session_integration or StoryContextSessionIntegration()
        )
        self.narrative_service = narrative_service or NarrativeGenerationService()

        # Message analysis patterns
        self.intent_patterns = self._build_intent_patterns()
        self.emotional_indicators = self._build_emotional_indicators()
        self.therapeutic_keywords = self._build_therapeutic_keywords()

        # Response generation strategies
        self.response_strategies = self._build_response_strategies()

        # Configuration
        self.max_response_time_seconds = 5
        self.enable_proactive_interventions = True
        self.adaptive_complexity = True

        # Metrics
        self.metrics = {
            "messages_analyzed": 0,
            "stories_generated": 0,
            "therapeutic_interventions_triggered": 0,
            "complex_responses_generated": 0,
            "average_response_time_ms": 0,
            "intent_detection_accuracy": 0.0,
            "player_engagement_score": 0.0,
        }

        logger.info("DynamicStoryGenerationService initialized")

    async def process_player_message(
        self,
        session_id: str,
        player_id: str,
        message_text: str,
        message_metadata: dict[str, Any] | None = None,
    ) -> StoryGenerationResponse | None:
        """
        Process a player message and generate dynamic story response.

        Args:
            session_id: Session identifier
            player_id: Player identifier
            message_text: Player message text
            message_metadata: Optional message metadata

        Returns:
            StoryGenerationResponse or None if processing fails
        """
        try:
            start_time = datetime.utcnow()

            # Analyze the message
            message_analysis = await self._analyze_message(message_text, session_id)
            self.metrics["messages_analyzed"] += 1

            # Get session context
            session_context = await self._get_session_context(session_id)
            if not session_context:
                logger.error(f"No session context found for {session_id}")
                return None

            # Create generation request
            generation_request = StoryGenerationRequest(
                session_id=session_id,
                player_id=player_id,
                message_text=message_text,
                message_analysis=message_analysis,
                session_context=session_context["session_context"],
                narrative_context=session_context["narrative_context"],
                therapeutic_context=session_context["therapeutic_context"],
            )

            # Generate story response
            response = await self._generate_story_response(generation_request)

            if response:
                # Update session with the interaction
                await self._update_session_with_interaction(
                    generation_request, response
                )

                # Update metrics
                processing_time = (
                    datetime.utcnow() - start_time
                ).total_seconds() * 1000
                self._update_response_time_metric(processing_time)
                self.metrics["stories_generated"] += 1

                logger.debug(
                    f"Generated story response for session {session_id} in {processing_time:.2f}ms"
                )

            return response

        except Exception as e:
            logger.error(f"Error processing player message: {e}")
            return None

    async def _analyze_message(
        self, message_text: str, session_id: str
    ) -> MessageAnalysis:
        """Analyze player message to determine intent and requirements."""
        try:
            # Detect intent type
            intent_type, confidence = await self._detect_message_intent(message_text)

            # Analyze emotional tone
            emotional_tone = await self._analyze_emotional_tone(message_text)

            # Identify therapeutic indicators
            therapeutic_indicators = await self._identify_therapeutic_indicators(
                message_text
            )

            # Extract narrative elements
            narrative_elements = await self._extract_narrative_elements(message_text)

            # Determine response complexity needed
            complexity_needed = await self._determine_response_complexity(
                message_text, intent_type, therapeutic_indicators
            )

            # Assess urgency level
            urgency_level = await self._assess_urgency_level(
                message_text, therapeutic_indicators, emotional_tone
            )

            # Determine context requirements
            context_requirements = await self._determine_context_requirements(
                intent_type, narrative_elements
            )

            return MessageAnalysis(
                intent_type=intent_type,
                confidence=confidence,
                emotional_tone=emotional_tone,
                therapeutic_indicators=therapeutic_indicators,
                narrative_elements=narrative_elements,
                complexity_needed=complexity_needed,
                urgency_level=urgency_level,
                context_requirements=context_requirements,
            )

        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            # Return default analysis
            return MessageAnalysis(
                intent_type=MessageIntentType.NARRATIVE_ACTION,
                confidence=0.5,
                emotional_tone="neutral",
                therapeutic_indicators=[],
                narrative_elements=[],
                complexity_needed=ResponseComplexity.MODERATE,
                urgency_level=2,
                context_requirements=[],
            )

    async def _generate_story_response(
        self, request: StoryGenerationRequest
    ) -> StoryGenerationResponse | None:
        """Generate story response based on analyzed message."""
        try:
            analysis = request.message_analysis

            # Select appropriate response strategy
            strategy = self.response_strategies.get(
                analysis.intent_type,
                self.response_strategies[MessageIntentType.NARRATIVE_ACTION],
            )

            # Determine workflow priority based on urgency
            priority = self._map_urgency_to_priority(analysis.urgency_level)

            # Check if therapeutic intervention is needed
            if analysis.therapeutic_indicators and self.enable_proactive_interventions:
                return await self._generate_therapeutic_response(request, priority)

            # Generate response based on complexity
            if analysis.complexity_needed == ResponseComplexity.SIMPLE:
                return await self._generate_simple_response(request, strategy)
            elif analysis.complexity_needed == ResponseComplexity.MODERATE:
                return await self._generate_moderate_response(
                    request, strategy, priority
                )
            elif analysis.complexity_needed == ResponseComplexity.COMPLEX:
                return await self._generate_complex_response(
                    request, strategy, priority
                )
            else:  # THERAPEUTIC
                return await self._generate_therapeutic_response(request, priority)

        except Exception as e:
            logger.error(f"Error generating story response: {e}")
            return None

    async def _generate_simple_response(
        self, request: StoryGenerationRequest, strategy: dict[str, Any]
    ) -> StoryGenerationResponse:
        """Generate a simple narrative response."""
        try:
            # Use narrative service for quick response
            response_data = await self.narrative_service.process_player_action(
                request.session_id,
                request.message_text,
                request.message_analysis.intent_type.value,
            )

            if response_data:
                return StoryGenerationResponse(
                    session_id=request.session_id,
                    narrative_text=response_data["content"]["text"],
                    response_type="simple_narrative",
                    scene_updates=response_data["content"].get("scene_updates"),
                    therapeutic_elements=response_data["content"].get(
                        "therapeutic_elements"
                    ),
                    metadata={
                        "generation_strategy": "simple",
                        "intent": request.message_analysis.intent_type.value,
                    },
                )

            # Fallback response
            return StoryGenerationResponse(
                session_id=request.session_id,
                narrative_text="Your action resonates through the story...",
                response_type="simple_narrative",
                metadata={"generation_strategy": "simple_fallback"},
            )

        except Exception as e:
            logger.error(f"Error generating simple response: {e}")
            return StoryGenerationResponse(
                session_id=request.session_id,
                narrative_text="The story continues...",
                response_type="simple_narrative",
            )

    async def _generate_moderate_response(
        self,
        request: StoryGenerationRequest,
        strategy: dict[str, Any],
        priority: WorkflowPriority,
    ) -> StoryGenerationResponse:
        """Generate a moderate complexity narrative response."""
        try:
            # Use agent orchestration for richer response
            workflow_id = await self.agent_bridge.execute_workflow(
                workflow_type=AgentWorkflowType.NARRATIVE_GENERATION,
                session_id=request.session_id,
                player_id=request.player_id,
                payload={
                    "narrative_type": "moderate_response",
                    "player_message": request.message_text,
                    "intent_type": request.message_analysis.intent_type.value,
                    "emotional_tone": request.message_analysis.emotional_tone,
                    "narrative_elements": request.message_analysis.narrative_elements,
                    "send_to_websocket": False,  # We'll handle WebSocket sending
                },
                context={
                    "session_context": request.session_context,
                    "narrative_context": request.narrative_context,
                    "therapeutic_context": request.therapeutic_context,
                },
                priority=priority,
            )

            # Wait for workflow completion (with timeout)
            result = await self._wait_for_workflow_completion(
                workflow_id, timeout_seconds=5
            )

            if result and result.get("success"):
                narrative_result = result["result"]["narrative_result"]

                return StoryGenerationResponse(
                    session_id=request.session_id,
                    narrative_text=narrative_result.get(
                        "narrative_text", "The story unfolds..."
                    ),
                    response_type="moderate_narrative",
                    scene_updates=narrative_result.get("scene_updates"),
                    therapeutic_elements=narrative_result.get("therapeutic_elements"),
                    metadata={
                        "generation_strategy": "moderate",
                        "workflow_id": workflow_id,
                        "intent": request.message_analysis.intent_type.value,
                    },
                )

            # Fallback to simple response
            return await self._generate_simple_response(request, strategy)

        except Exception as e:
            logger.error(f"Error generating moderate response: {e}")
            return await self._generate_simple_response(request, strategy)

    async def _generate_complex_response(
        self,
        request: StoryGenerationRequest,
        strategy: dict[str, Any],
        priority: WorkflowPriority,
    ) -> StoryGenerationResponse:
        """Generate a complex narrative response with choices."""
        try:
            # Generate narrative first
            narrative_workflow_id = await self.agent_bridge.execute_workflow(
                workflow_type=AgentWorkflowType.NARRATIVE_GENERATION,
                session_id=request.session_id,
                player_id=request.player_id,
                payload={
                    "narrative_type": "complex_response",
                    "player_message": request.message_text,
                    "intent_type": request.message_analysis.intent_type.value,
                    "complexity_level": "high",
                    "include_choices": True,
                    "send_to_websocket": False,
                },
                context={
                    "session_context": request.session_context,
                    "narrative_context": request.narrative_context,
                    "therapeutic_context": request.therapeutic_context,
                },
                priority=priority,
            )

            # Generate choices separately
            choice_workflow_id = await self.agent_bridge.execute_workflow(
                workflow_type=AgentWorkflowType.CHOICE_GENERATION,
                session_id=request.session_id,
                player_id=request.player_id,
                payload={
                    "narrative_context": request.narrative_context,
                    "therapeutic_goals": request.therapeutic_context.get("goals", []),
                    "send_to_websocket": False,
                },
                context={
                    "session_context": request.session_context,
                    "narrative_context": request.narrative_context,
                },
                priority=priority,
            )

            # Wait for both workflows
            narrative_result = await self._wait_for_workflow_completion(
                narrative_workflow_id, timeout_seconds=7
            )
            choice_result = await self._wait_for_workflow_completion(
                choice_workflow_id, timeout_seconds=5
            )

            narrative_text = "The story reaches a pivotal moment..."
            choices = None
            scene_updates = {}
            therapeutic_elements = {}

            if narrative_result and narrative_result.get("success"):
                narrative_data = narrative_result["result"]["narrative_result"]
                narrative_text = narrative_data.get("narrative_text", narrative_text)
                scene_updates = narrative_data.get("scene_updates", {})
                therapeutic_elements = narrative_data.get("therapeutic_elements", {})

            if choice_result and choice_result.get("success"):
                choice_data = choice_result["result"]["choices_result"]
                choices = choice_data.get("choices", [])

            self.metrics["complex_responses_generated"] += 1

            return StoryGenerationResponse(
                session_id=request.session_id,
                narrative_text=narrative_text,
                response_type="complex_narrative",
                choices=choices,
                scene_updates=scene_updates,
                therapeutic_elements=therapeutic_elements,
                metadata={
                    "generation_strategy": "complex",
                    "narrative_workflow_id": narrative_workflow_id,
                    "choice_workflow_id": choice_workflow_id,
                    "intent": request.message_analysis.intent_type.value,
                },
            )

        except Exception as e:
            logger.error(f"Error generating complex response: {e}")
            return await self._generate_moderate_response(request, strategy, priority)

    async def _generate_therapeutic_response(
        self, request: StoryGenerationRequest, priority: WorkflowPriority
    ) -> StoryGenerationResponse:
        """Generate a therapeutic intervention response."""
        try:
            # Determine intervention type
            intervention_type = self._determine_intervention_type(
                request.message_analysis.therapeutic_indicators,
                request.message_analysis.emotional_tone,
            )

            # Execute therapeutic intervention workflow
            workflow_id = await self.agent_bridge.execute_workflow(
                workflow_type=AgentWorkflowType.THERAPEUTIC_INTERVENTION,
                session_id=request.session_id,
                player_id=request.player_id,
                payload={
                    "intervention_type": intervention_type,
                    "therapeutic_data": {
                        "indicators": request.message_analysis.therapeutic_indicators,
                        "emotional_tone": request.message_analysis.emotional_tone,
                        "player_message": request.message_text,
                    },
                    "send_to_websocket": False,
                },
                context={
                    "session_context": request.session_context,
                    "therapeutic_context": request.therapeutic_context,
                },
                priority=WorkflowPriority.CRITICAL,  # Always high priority for therapeutic
            )

            # Wait for therapeutic response
            result = await self._wait_for_workflow_completion(
                workflow_id, timeout_seconds=8
            )

            if result and result.get("success"):
                therapeutic_data = result["result"]["therapeutic_result"]

                self.metrics["therapeutic_interventions_triggered"] += 1

                return StoryGenerationResponse(
                    session_id=request.session_id,
                    narrative_text=therapeutic_data.get(
                        "narrative_text", "Let's take a moment to reflect..."
                    ),
                    response_type="therapeutic_intervention",
                    therapeutic_elements={
                        "intervention_type": intervention_type,
                        "resources": therapeutic_data.get("resources", []),
                        "guidance": therapeutic_data.get("guidance", []),
                    },
                    metadata={
                        "generation_strategy": "therapeutic",
                        "intervention_type": intervention_type,
                        "workflow_id": workflow_id,
                    },
                )

            # Fallback therapeutic response
            return StoryGenerationResponse(
                session_id=request.session_id,
                narrative_text="I notice this might be a meaningful moment. How are you feeling about what just happened?",
                response_type="therapeutic_intervention",
                therapeutic_elements={
                    "intervention_type": "reflection_prompt",
                    "guidance": [
                        "Take your time to process",
                        "Your feelings are valid",
                    ],
                },
                metadata={"generation_strategy": "therapeutic_fallback"},
            )

        except Exception as e:
            logger.error(f"Error generating therapeutic response: {e}")
            return StoryGenerationResponse(
                session_id=request.session_id,
                narrative_text="This seems like an important moment. Let's pause and reflect together.",
                response_type="therapeutic_intervention",
            )

    # Helper methods for message analysis

    async def _detect_message_intent(
        self, message_text: str
    ) -> tuple[MessageIntentType, float]:
        """Detect the intent of a player message."""
        try:
            message_lower = message_text.lower().strip()

            # Check patterns for each intent type
            for intent_type, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message_lower):
                        confidence = 0.8  # Base confidence for pattern match
                        return MessageIntentType(intent_type), confidence

            # Default to narrative action with moderate confidence
            return MessageIntentType.NARRATIVE_ACTION, 0.6

        except Exception as e:
            logger.error(f"Error detecting message intent: {e}")
            return MessageIntentType.NARRATIVE_ACTION, 0.5

    async def _analyze_emotional_tone(self, message_text: str) -> str:
        """Analyze the emotional tone of a message."""
        try:
            message_lower = message_text.lower()

            # Check for emotional indicators
            for tone, indicators in self.emotional_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        return tone

            return "neutral"

        except Exception as e:
            logger.error(f"Error analyzing emotional tone: {e}")
            return "neutral"

    async def _identify_therapeutic_indicators(self, message_text: str) -> list[str]:
        """Identify therapeutic indicators in a message."""
        try:
            indicators = []
            message_lower = message_text.lower()

            for category, keywords in self.therapeutic_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        indicators.append(category)
                        break  # Only add category once

            return indicators

        except Exception as e:
            logger.error(f"Error identifying therapeutic indicators: {e}")
            return []

    async def _extract_narrative_elements(self, message_text: str) -> list[str]:
        """Extract narrative elements from a message."""
        try:
            elements = []
            message_lower = message_text.lower()

            # Look for action words
            action_words = [
                "go",
                "walk",
                "run",
                "look",
                "examine",
                "talk",
                "speak",
                "take",
                "use",
                "open",
                "close",
            ]
            for word in action_words:
                if word in message_lower:
                    elements.append(f"action_{word}")

            # Look for objects/locations
            if "door" in message_lower:
                elements.append("object_door")
            if "room" in message_lower:
                elements.append("location_room")
            if "person" in message_lower or "character" in message_lower:
                elements.append("character_interaction")

            return elements

        except Exception as e:
            logger.error(f"Error extracting narrative elements: {e}")
            return []

    async def _determine_response_complexity(
        self,
        message_text: str,
        intent_type: MessageIntentType,
        therapeutic_indicators: list[str],
    ) -> ResponseComplexity:
        """Determine the complexity level needed for the response."""
        try:
            # Therapeutic indicators always require therapeutic complexity
            if therapeutic_indicators:
                return ResponseComplexity.THERAPEUTIC

            # Complex intents need complex responses
            if intent_type in [
                MessageIntentType.SKILL_PRACTICE,
                MessageIntentType.REFLECTION,
            ]:
                return ResponseComplexity.COMPLEX

            # Simple acknowledgments
            if len(message_text.strip()) < 10:
                return ResponseComplexity.SIMPLE

            # Questions and explorations need moderate complexity
            if intent_type in [
                MessageIntentType.QUESTION,
                MessageIntentType.EXPLORATION,
            ]:
                return ResponseComplexity.MODERATE

            # Default to moderate
            return ResponseComplexity.MODERATE

        except Exception as e:
            logger.error(f"Error determining response complexity: {e}")
            return ResponseComplexity.MODERATE

    async def _assess_urgency_level(
        self, message_text: str, therapeutic_indicators: list[str], emotional_tone: str
    ) -> int:
        """Assess the urgency level of a message."""
        try:
            urgency = 2  # Default medium urgency

            # High urgency for therapeutic indicators
            if therapeutic_indicators:
                urgency = 3

                # Critical urgency for crisis indicators
                if (
                    "crisis" in therapeutic_indicators
                    or "safety" in therapeutic_indicators
                ):
                    urgency = 4

            # Adjust based on emotional tone
            if emotional_tone in ["distressed", "angry", "fearful"]:
                urgency = min(urgency + 1, 4)
            elif emotional_tone in ["calm", "content"]:
                urgency = max(urgency - 1, 1)

            return urgency

        except Exception as e:
            logger.error(f"Error assessing urgency level: {e}")
            return 2

    async def _determine_context_requirements(
        self, intent_type: MessageIntentType, narrative_elements: list[str]
    ) -> list[str]:
        """Determine what context is needed for the response."""
        try:
            requirements = ["session_context"]  # Always need session context

            # Add specific requirements based on intent
            if intent_type == MessageIntentType.EXPLORATION:
                requirements.extend(["world_context", "location_context"])
            elif intent_type == MessageIntentType.DIALOGUE_RESPONSE:
                requirements.append("character_context")
            elif intent_type == MessageIntentType.SKILL_PRACTICE:
                requirements.append("therapeutic_context")

            # Add requirements based on narrative elements
            if any("character" in elem for elem in narrative_elements):
                requirements.append("character_context")
            if any("location" in elem for elem in narrative_elements):
                requirements.append("location_context")

            return list(set(requirements))  # Remove duplicates

        except Exception as e:
            logger.error(f"Error determining context requirements: {e}")
            return ["session_context"]

    # Helper methods for response generation

    def _map_urgency_to_priority(self, urgency_level: int) -> WorkflowPriority:
        """Map urgency level to workflow priority."""
        if urgency_level >= 4:
            return WorkflowPriority.CRITICAL
        elif urgency_level == 3:
            return WorkflowPriority.HIGH
        elif urgency_level == 2:
            return WorkflowPriority.MEDIUM
        else:
            return WorkflowPriority.LOW

    def _determine_intervention_type(
        self, therapeutic_indicators: list[str], emotional_tone: str
    ) -> str:
        """Determine the type of therapeutic intervention needed."""
        if "crisis" in therapeutic_indicators:
            return "crisis_response"
        elif "safety" in therapeutic_indicators:
            return "safety_guidance"
        elif "anxiety" in therapeutic_indicators:
            return "anxiety_support"
        elif "depression" in therapeutic_indicators:
            return "emotional_support"
        elif emotional_tone in ["distressed", "sad"]:
            return "emotional_support"
        elif emotional_tone == "angry":
            return "anger_management"
        else:
            return "reflection_prompt"

    async def _wait_for_workflow_completion(
        self, workflow_id: str, timeout_seconds: int = 5
    ) -> dict[str, Any] | None:
        """Wait for a workflow to complete."""
        try:
            start_time = datetime.utcnow()

            while (datetime.utcnow() - start_time).total_seconds() < timeout_seconds:
                status = await self.agent_bridge.get_workflow_status(workflow_id)

                if status and status.get("status") == "completed":
                    # Return mock result for now - in real implementation would get actual result
                    return {
                        "success": True,
                        "result": {
                            "narrative_result": {
                                "narrative_text": "The story continues with your action...",
                                "scene_updates": {},
                                "therapeutic_elements": {},
                            }
                        },
                    }

                await asyncio.sleep(0.1)

            logger.warning(f"Workflow {workflow_id} timed out after {timeout_seconds}s")
            return None

        except Exception as e:
            logger.error(f"Error waiting for workflow completion: {e}")
            return None

    async def _get_session_context(self, session_id: str) -> dict[str, Any] | None:
        """Get comprehensive session context."""
        try:
            narrative_context = (
                await self.session_integration.get_session_narrative_context(session_id)
            )
            if not narrative_context:
                return None

            return {
                "session_context": narrative_context.get("session_metadata", {}),
                "narrative_context": narrative_context.get("narrative_state", {}),
                "therapeutic_context": {
                    "goals": narrative_context.get("therapeutic_goals", []),
                    "progress": {},  # Would be loaded from session integration
                },
            }

        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return None

    async def _update_session_with_interaction(
        self, request: StoryGenerationRequest, response: StoryGenerationResponse
    ) -> None:
        """Update session with the player interaction and response."""
        try:
            # Update narrative state
            narrative_updates = {
                "last_player_message": request.message_text,
                "last_response": response.narrative_text,
                "last_intent": request.message_analysis.intent_type.value,
                "last_emotional_tone": request.message_analysis.emotional_tone,
                "interaction_timestamp": datetime.utcnow().isoformat(),
            }

            if response.scene_updates:
                narrative_updates.update(response.scene_updates)

            await self.session_integration.update_narrative_state(
                request.session_id, narrative_updates
            )

            # Update therapeutic progress if applicable
            if (
                response.therapeutic_elements
                or request.message_analysis.therapeutic_indicators
            ):
                therapeutic_updates = {
                    "last_therapeutic_interaction": {
                        "indicators": request.message_analysis.therapeutic_indicators,
                        "intervention_type": (
                            response.therapeutic_elements.get("intervention_type")
                            if response.therapeutic_elements
                            else None
                        ),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                }

                await self.session_integration.update_therapeutic_progress(
                    request.session_id, therapeutic_updates
                )

        except Exception as e:
            logger.error(f"Error updating session with interaction: {e}")

    def _update_response_time_metric(self, processing_time_ms: float) -> None:
        """Update average response time metric."""
        current_avg = self.metrics["average_response_time_ms"]
        count = self.metrics["stories_generated"]
        if count > 0:
            new_avg = (current_avg * (count - 1) + processing_time_ms) / count
            self.metrics["average_response_time_ms"] = new_avg
        else:
            self.metrics["average_response_time_ms"] = processing_time_ms

    # Configuration methods

    def _build_intent_patterns(self) -> dict[str, list[str]]:
        """Build regex patterns for intent detection."""
        return {
            MessageIntentType.NARRATIVE_ACTION.value: [
                r"\b(go|walk|run|move|travel)\b",
                r"\b(look|examine|inspect|check)\b",
                r"\b(take|grab|pick up|get)\b",
                r"\b(use|try|attempt)\b",
                r"\b(open|close|push|pull)\b",
            ],
            MessageIntentType.DIALOGUE_RESPONSE.value: [
                r"\b(say|tell|ask|speak|talk)\b",
                r"\b(hello|hi|greetings)\b",
                r"\b(yes|no|maybe|sure|okay)\b",
                r'"[^"]*"',  # Quoted speech
                r"'[^']*'",  # Single quoted speech
            ],
            MessageIntentType.EXPLORATION.value: [
                r"\b(where|what|how|why|when)\b",
                r"\b(explore|discover|find|search)\b",
                r"\b(around|area|place|location)\b",
            ],
            MessageIntentType.SKILL_PRACTICE.value: [
                r"\b(practice|try|learn|improve)\b",
                r"\b(skill|ability|technique)\b",
                r"\b(breathing|meditation|mindfulness)\b",
            ],
            MessageIntentType.REFLECTION.value: [
                r"\b(think|feel|believe|remember)\b",
                r"\b(reflect|consider|ponder)\b",
                r"\b(understand|realize|recognize)\b",
            ],
            MessageIntentType.THERAPEUTIC_EXERCISE.value: [
                r"\b(exercise|activity|practice)\b",
                r"\b(therapeutic|healing|recovery)\b",
                r"\b(journal|write|express)\b",
            ],
            MessageIntentType.QUESTION.value: [
                r"\?",  # Contains question mark
                r"\b(what|where|when|why|how|who)\b",
                r"\b(can|could|would|should|will)\b.*\?",
            ],
            MessageIntentType.EMOTIONAL_EXPRESSION.value: [
                r"\b(feel|feeling|felt|emotion)\b",
                r"\b(happy|sad|angry|scared|anxious|excited)\b",
                r"\b(love|hate|like|dislike)\b",
                r"\b(worried|concerned|stressed|relaxed)\b",
            ],
            MessageIntentType.CHOICE_SELECTION.value: [
                r"\b(choose|select|pick|decide)\b",
                r"\b(option|choice|alternative)\b",
                r"\b(first|second|third|last)\b",
            ],
            MessageIntentType.SYSTEM_COMMAND.value: [
                r"\b(help|menu|settings|options)\b",
                r"\b(save|load|quit|exit)\b",
                r"\b(pause|resume|stop|start)\b",
            ],
        }

    def _build_emotional_indicators(self) -> dict[str, list[str]]:
        """Build emotional tone indicators."""
        return {
            "happy": [
                "happy",
                "joy",
                "excited",
                "cheerful",
                "glad",
                "pleased",
                "delighted",
            ],
            "sad": [
                "sad",
                "unhappy",
                "depressed",
                "down",
                "blue",
                "melancholy",
                "sorrowful",
            ],
            "angry": [
                "angry",
                "mad",
                "furious",
                "irritated",
                "annoyed",
                "frustrated",
                "rage",
            ],
            "anxious": [
                "anxious",
                "worried",
                "nervous",
                "scared",
                "afraid",
                "fearful",
                "panic",
            ],
            "calm": [
                "calm",
                "peaceful",
                "relaxed",
                "serene",
                "tranquil",
                "composed",
                "zen",
            ],
            "confused": [
                "confused",
                "puzzled",
                "bewildered",
                "lost",
                "uncertain",
                "unclear",
            ],
            "excited": [
                "excited",
                "thrilled",
                "enthusiastic",
                "eager",
                "pumped",
                "energetic",
            ],
            "distressed": [
                "distressed",
                "upset",
                "troubled",
                "disturbed",
                "distraught",
                "anguished",
            ],
            "content": ["content", "satisfied", "fulfilled", "comfortable", "at peace"],
            "fearful": [
                "fearful",
                "terrified",
                "petrified",
                "horrified",
                "spooked",
                "intimidated",
            ],
        }

    def _build_therapeutic_keywords(self) -> dict[str, list[str]]:
        """Build therapeutic indicator keywords."""
        return {
            "anxiety": [
                "anxiety",
                "anxious",
                "panic",
                "worry",
                "nervous",
                "stress",
                "overwhelmed",
            ],
            "depression": [
                "depression",
                "depressed",
                "sad",
                "hopeless",
                "empty",
                "worthless",
            ],
            "trauma": [
                "trauma",
                "traumatic",
                "flashback",
                "nightmare",
                "triggered",
                "ptsd",
            ],
            "grief": [
                "grief",
                "loss",
                "death",
                "died",
                "mourning",
                "bereaved",
                "funeral",
            ],
            "anger": [
                "anger",
                "angry",
                "rage",
                "furious",
                "mad",
                "irritated",
                "hostile",
            ],
            "self_harm": [
                "hurt myself",
                "self harm",
                "cut",
                "suicide",
                "kill myself",
                "end it",
            ],
            "crisis": [
                "crisis",
                "emergency",
                "help",
                "can't cope",
                "breaking down",
                "desperate",
            ],
            "safety": [
                "unsafe",
                "danger",
                "threatened",
                "scared",
                "protection",
                "harm",
            ],
            "substance": [
                "drink",
                "drugs",
                "alcohol",
                "high",
                "addiction",
                "substance",
            ],
            "relationship": [
                "relationship",
                "partner",
                "family",
                "friends",
                "lonely",
                "isolated",
            ],
            "self_esteem": [
                "worthless",
                "useless",
                "failure",
                "stupid",
                "ugly",
                "inadequate",
            ],
            "eating": [
                "eating",
                "food",
                "weight",
                "fat",
                "thin",
                "diet",
                "hungry",
                "starving",
            ],
        }

    def _build_response_strategies(self) -> dict[MessageIntentType, dict[str, Any]]:
        """Build response strategies for different intent types."""
        return {
            MessageIntentType.NARRATIVE_ACTION: {
                "approach": "descriptive",
                "focus": "action_consequences",
                "include_sensory": True,
                "therapeutic_integration": "subtle",
            },
            MessageIntentType.DIALOGUE_RESPONSE: {
                "approach": "conversational",
                "focus": "character_interaction",
                "include_sensory": False,
                "therapeutic_integration": "contextual",
            },
            MessageIntentType.EXPLORATION: {
                "approach": "descriptive",
                "focus": "world_building",
                "include_sensory": True,
                "therapeutic_integration": "environmental",
            },
            MessageIntentType.SKILL_PRACTICE: {
                "approach": "instructional",
                "focus": "skill_development",
                "include_sensory": True,
                "therapeutic_integration": "direct",
            },
            MessageIntentType.REFLECTION: {
                "approach": "contemplative",
                "focus": "internal_processing",
                "include_sensory": False,
                "therapeutic_integration": "direct",
            },
            MessageIntentType.THERAPEUTIC_EXERCISE: {
                "approach": "guided",
                "focus": "therapeutic_benefit",
                "include_sensory": True,
                "therapeutic_integration": "primary",
            },
            MessageIntentType.QUESTION: {
                "approach": "informative",
                "focus": "knowledge_sharing",
                "include_sensory": False,
                "therapeutic_integration": "supportive",
            },
            MessageIntentType.EMOTIONAL_EXPRESSION: {
                "approach": "empathetic",
                "focus": "emotional_validation",
                "include_sensory": False,
                "therapeutic_integration": "primary",
            },
            MessageIntentType.CHOICE_SELECTION: {
                "approach": "consequential",
                "focus": "choice_outcomes",
                "include_sensory": True,
                "therapeutic_integration": "contextual",
            },
            MessageIntentType.SYSTEM_COMMAND: {
                "approach": "functional",
                "focus": "system_response",
                "include_sensory": False,
                "therapeutic_integration": "none",
            },
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the dynamic story generation service."""
        return {
            **self.metrics,
            "intent_patterns_loaded": len(self.intent_patterns),
            "emotional_indicators_loaded": len(self.emotional_indicators),
            "therapeutic_keywords_loaded": len(self.therapeutic_keywords),
            "response_strategies_loaded": len(self.response_strategies),
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the dynamic story generation service."""
        logger.info("DynamicStoryGenerationService shutdown complete")
