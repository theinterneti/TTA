"""
Character to Gameplay Transition Service

This service handles the seamless transition from conversational character creation
to active story participation, ensuring continuity and therapeutic integration.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..database.character_repository import CharacterRepository
from ..models.character import Character
from ..models.gameplay_messages import (
    GameplayMessageType,
)
from .gameplay_chat_manager import GameplayChatManager
from .story_initialization_service import StoryInitializationService

logger = logging.getLogger(__name__)


class TransitionStage(str, Enum):
    """Stages of the character to gameplay transition."""

    CHARACTER_COMPLETION_DETECTED = "character_completion_detected"
    THERAPEUTIC_GOALS_GATHERED = "therapeutic_goals_gathered"
    WORLD_SELECTION_INITIATED = "world_selection_initiated"
    STORY_INITIALIZATION_STARTED = "story_initialization_started"
    GAMEPLAY_SESSION_CREATED = "gameplay_session_created"
    NARRATIVE_INTRODUCTION_SENT = "narrative_introduction_sent"
    TRANSITION_COMPLETED = "transition_completed"
    TRANSITION_FAILED = "transition_failed"


@dataclass
class TransitionContext:
    """Context for managing the transition process."""

    player_id: str
    character_id: str
    character_data: Character | None = None
    therapeutic_goals: list[str] | None = None
    world_preferences: dict[str, Any] | None = None
    session_id: str | None = None
    current_stage: TransitionStage = TransitionStage.CHARACTER_COMPLETION_DETECTED
    transition_start_time: datetime | None = None
    error_message: str | None = None

    def __post_init__(self):
        if self.therapeutic_goals is None:
            self.therapeutic_goals = []
        if self.world_preferences is None:
            self.world_preferences = {}
        if self.transition_start_time is None:
            self.transition_start_time = datetime.utcnow()


class CharacterToGameplayTransition:
    """
    Service for managing seamless transitions from character creation to active gameplay.

    Handles the complete workflow including:
    - Detection of character creation completion
    - Therapeutic goal integration
    - Story world selection and initialization
    - Gameplay session creation
    - Narrative introduction delivery
    """

    def __init__(
        self,
        story_initialization_service: StoryInitializationService | None = None,
        character_repository: CharacterRepository | None = None,
        chat_manager: GameplayChatManager | None = None,
    ):
        """
        Initialize the Character to Gameplay Transition service.

        Args:
            story_initialization_service: Service for story initialization
            character_repository: Repository for character data
            chat_manager: Manager for gameplay chat connections
        """
        self.story_service = (
            story_initialization_service or StoryInitializationService()
        )
        self.character_repository = character_repository or CharacterRepository()
        self.chat_manager = chat_manager or GameplayChatManager()

        # Active transitions
        self.active_transitions: dict[str, TransitionContext] = (
            {}
        )  # player_id -> context

        # Transition callbacks
        self.stage_callbacks: dict[TransitionStage, list[Callable]] = {}

        # Configuration
        self.auto_transition_enabled = True
        self.transition_timeout_minutes = 10
        self.require_explicit_consent = True

        # Metrics
        self.metrics = {
            "transitions_initiated": 0,
            "transitions_completed": 0,
            "transitions_failed": 0,
            "average_transition_time_seconds": 0,
            "character_completions_detected": 0,
            "therapeutic_goals_collected": 0,
        }

        logger.info("CharacterToGameplayTransition service initialized")

    async def detect_character_completion(
        self, player_id: str, character_id: str
    ) -> bool:
        """
        Detect when a character creation is completed and ready for gameplay transition.

        Args:
            player_id: Player identifier
            character_id: Character identifier

        Returns:
            True if character is complete and ready for transition
        """
        try:
            # Get character data
            character_data = await self.character_repository.get_character(character_id)
            if not character_data:
                logger.warning(f"Character {character_id} not found")
                return False

            # Check if character is complete
            if not character_data.is_complete:
                logger.debug(f"Character {character_id} is not yet complete")
                return False

            # Check if transition is already in progress
            if player_id in self.active_transitions:
                logger.debug(f"Transition already in progress for player {player_id}")
                return False

            self.metrics["character_completions_detected"] += 1
            logger.info(
                f"Character completion detected for player {player_id}, character {character_id}"
            )

            # Initiate transition if auto-transition is enabled
            if self.auto_transition_enabled:
                await self.initiate_transition(player_id, character_id, character_data)

            return True

        except Exception as e:
            logger.error(f"Error detecting character completion: {e}")
            return False

    async def initiate_transition(
        self,
        player_id: str,
        character_id: str,
        character_data: Character | None = None,
        therapeutic_goals: list[str] | None = None,
        world_preferences: dict[str, Any] | None = None,
    ) -> str:
        """
        Initiate the transition from character creation to gameplay.

        Args:
            player_id: Player identifier
            character_id: Character identifier
            character_data: Optional character data (will be fetched if not provided)
            therapeutic_goals: Optional therapeutic goals
            world_preferences: Optional world preferences

        Returns:
            Transition ID for tracking
        """
        try:
            # Get character data if not provided
            if not character_data:
                character_data = await self.character_repository.get_character(
                    character_id
                )
                if not character_data:
                    raise ValueError(f"Character {character_id} not found")

            # Create transition context
            transition_context = TransitionContext(
                player_id=player_id,
                character_id=character_id,
                character_data=character_data,
                therapeutic_goals=therapeutic_goals or [],
                world_preferences=world_preferences or {},
            )

            # Register active transition
            self.active_transitions[player_id] = transition_context

            # Update metrics
            self.metrics["transitions_initiated"] += 1

            # Execute transition workflow
            transition_id = f"transition_{player_id}_{datetime.utcnow().timestamp()}"
            asyncio.create_task(self._execute_transition_workflow(transition_context))

            logger.info(f"Initiated transition {transition_id} for player {player_id}")
            return transition_id

        except Exception as e:
            logger.error(f"Error initiating transition for player {player_id}: {e}")
            self.metrics["transitions_failed"] += 1
            raise

    async def _execute_transition_workflow(self, context: TransitionContext) -> None:
        """Execute the complete transition workflow."""
        try:
            # Stage 1: Gather therapeutic goals if not provided
            if not context.therapeutic_goals:
                await self._gather_therapeutic_goals(context)

            # Stage 2: Initialize story session
            await self._initialize_story_session(context)

            # Stage 3: Create gameplay session
            await self._create_gameplay_session(context)

            # Stage 4: Send narrative introduction
            await self._send_narrative_introduction(context)

            # Stage 5: Complete transition
            await self._complete_transition(context)

        except Exception as e:
            logger.error(
                f"Error in transition workflow for player {context.player_id}: {e}"
            )
            context.current_stage = TransitionStage.TRANSITION_FAILED
            context.error_message = str(e)
            await self._handle_transition_failure(context)

    async def _gather_therapeutic_goals(self, context: TransitionContext) -> None:
        """Gather therapeutic goals from character data or prompt user."""
        try:
            context.current_stage = TransitionStage.THERAPEUTIC_GOALS_GATHERED

            # Ensure therapeutic_goals is initialized
            if context.therapeutic_goals is None:
                context.therapeutic_goals = []

            # Extract therapeutic goals from character attributes
            character_attributes = {}
            if context.character_data and hasattr(context.character_data, "attributes"):
                character_attributes = (
                    getattr(context.character_data, "attributes", {}) or {}
                )

            # Look for explicit therapeutic goals
            if "therapeutic_goals" in character_attributes:
                goals = character_attributes["therapeutic_goals"]
                if isinstance(goals, list):
                    context.therapeutic_goals.extend(goals)

            # Infer goals from character background and attributes
            background = character_attributes.get("background", "")
            if isinstance(background, str):
                background = background.lower()
            if "anxiety" in background:
                context.therapeutic_goals.append("anxiety_management")
            if "social" in background or "relationship" in background:
                context.therapeutic_goals.append("social_skills")
            if "confidence" in background or "self-esteem" in background:
                context.therapeutic_goals.append("self_esteem")

            # Default therapeutic goals if none found
            if not context.therapeutic_goals:
                context.therapeutic_goals = ["emotional_regulation", "self_awareness"]

            self.metrics["therapeutic_goals_collected"] += 1
            await self._notify_stage_completion(
                context, TransitionStage.THERAPEUTIC_GOALS_GATHERED
            )

        except Exception as e:
            logger.error(f"Error gathering therapeutic goals: {e}")
            raise

    async def _initialize_story_session(self, context: TransitionContext) -> None:
        """Initialize the story session using the story initialization service."""
        try:
            context.current_stage = TransitionStage.STORY_INITIALIZATION_STARTED

            # Initialize story session
            session_id = await self.story_service.initialize_story_session(
                player_id=context.player_id,
                character_id=context.character_id,
                therapeutic_goals=context.therapeutic_goals,
                story_preferences=context.world_preferences,
            )

            if not session_id:
                raise Exception("Failed to initialize story session")

            context.session_id = session_id
            await self._notify_stage_completion(
                context, TransitionStage.STORY_INITIALIZATION_STARTED
            )

        except Exception as e:
            logger.error(f"Error initializing story session: {e}")
            raise

    async def _create_gameplay_session(self, context: TransitionContext) -> None:
        """Create the gameplay session and associate with WebSocket connections."""
        try:
            context.current_stage = TransitionStage.GAMEPLAY_SESSION_CREATED

            # The session should already be created by story initialization
            if not context.session_id:
                raise Exception("No session ID available for gameplay session creation")

            # Find active WebSocket connections for the player
            player_connections = self.chat_manager.get_player_connections(
                context.player_id
            )

            # Associate connections with the gameplay session
            for connection_info in player_connections:
                connection_id = connection_info["connection_id"]
                # This would be handled by the WebSocket integration service
                logger.info(
                    f"Associated connection {connection_id} with session {context.session_id}"
                )

            await self._notify_stage_completion(
                context, TransitionStage.GAMEPLAY_SESSION_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating gameplay session: {e}")
            raise

    async def _send_narrative_introduction(self, context: TransitionContext) -> None:
        """Send the narrative introduction to begin active gameplay."""
        try:
            context.current_stage = TransitionStage.NARRATIVE_INTRODUCTION_SENT

            # Create welcome message for the transition
            welcome_message = {
                "type": GameplayMessageType.NARRATIVE_RESPONSE.value,
                "session_id": context.session_id,
                "content": {
                    "text": f"Welcome to your therapeutic adventure, {context.character_data.name if context.character_data else 'adventurer'}! Your character creation journey has prepared you for this moment. Let's begin your story...",
                    "transition_complete": True,
                    "character_name": (
                        context.character_data.name
                        if context.character_data
                        else "Unknown"
                    ),
                    "therapeutic_goals": context.therapeutic_goals,
                    "scene_type": "transition_introduction",
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "source": "transition_service",
                    "transition_stage": "narrative_introduction",
                },
            }

            # Broadcast to all player connections
            sent_count = await self.chat_manager.broadcast_to_player(
                context.player_id, welcome_message
            )

            if sent_count == 0:
                logger.warning(
                    f"No active connections found for player {context.player_id}"
                )
            else:
                logger.info(f"Sent narrative introduction to {sent_count} connections")

            await self._notify_stage_completion(
                context, TransitionStage.NARRATIVE_INTRODUCTION_SENT
            )

        except Exception as e:
            logger.error(f"Error sending narrative introduction: {e}")
            raise

    async def _complete_transition(self, context: TransitionContext) -> None:
        """Complete the transition process."""
        try:
            context.current_stage = TransitionStage.TRANSITION_COMPLETED

            # Calculate transition duration
            if context.transition_start_time:
                duration = (
                    datetime.utcnow() - context.transition_start_time
                ).total_seconds()

                # Update average transition time
                current_avg = self.metrics["average_transition_time_seconds"]
                completed_count = self.metrics["transitions_completed"]
                new_avg = (current_avg * completed_count + duration) / (
                    completed_count + 1
                )
                self.metrics["average_transition_time_seconds"] = new_avg

            # Update metrics
            self.metrics["transitions_completed"] += 1

            # Send completion notification
            completion_message = {
                "type": GameplayMessageType.SYSTEM_MESSAGE.value,
                "session_id": context.session_id,
                "content": {
                    "text": "Transition to gameplay complete! Your therapeutic adventure has begun.",
                    "type": "transition_complete",
                    "session_id": context.session_id,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.chat_manager.broadcast_to_player(
                context.player_id, completion_message
            )

            # Clean up transition context
            if context.player_id in self.active_transitions:
                del self.active_transitions[context.player_id]

            await self._notify_stage_completion(
                context, TransitionStage.TRANSITION_COMPLETED
            )

            logger.info(
                f"Successfully completed transition for player {context.player_id}"
            )

        except Exception as e:
            logger.error(f"Error completing transition: {e}")
            raise

    async def _handle_transition_failure(self, context: TransitionContext) -> None:
        """Handle transition failure and cleanup."""
        try:
            self.metrics["transitions_failed"] += 1

            # Send failure notification to player
            failure_message = {
                "type": GameplayMessageType.ERROR.value,
                "content": {
                    "error": "Transition to gameplay failed",
                    "code": "TRANSITION_FAILED",
                    "details": context.error_message
                    or "Unknown error occurred during transition",
                    "retry_available": True,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.chat_manager.broadcast_to_player(
                context.player_id, failure_message
            )

            # Clean up transition context
            if context.player_id in self.active_transitions:
                del self.active_transitions[context.player_id]

            logger.error(
                f"Transition failed for player {context.player_id}: {context.error_message}"
            )

        except Exception as e:
            logger.error(f"Error handling transition failure: {e}")

    async def _notify_stage_completion(
        self, context: TransitionContext, stage: TransitionStage
    ) -> None:
        """Notify registered callbacks about stage completion."""
        try:
            # Execute stage callbacks if any are registered
            if stage in self.stage_callbacks:
                for callback in self.stage_callbacks[stage]:
                    try:
                        await callback(context, stage)
                    except Exception as e:
                        logger.error(f"Error in stage callback for {stage}: {e}")

            logger.debug(
                f"Completed transition stage {stage.value} for player {context.player_id}"
            )

        except Exception as e:
            logger.error(f"Error notifying stage completion: {e}")

    def register_stage_callback(
        self, stage: TransitionStage, callback: Callable
    ) -> None:
        """Register a callback for a specific transition stage."""
        if stage not in self.stage_callbacks:
            self.stage_callbacks[stage] = []
        self.stage_callbacks[stage].append(callback)
        logger.info(f"Registered callback for transition stage {stage.value}")

    def get_transition_status(self, player_id: str) -> dict[str, Any] | None:
        """Get the current transition status for a player."""
        context = self.active_transitions.get(player_id)
        if not context:
            return None

        return {
            "player_id": player_id,
            "character_id": context.character_id,
            "current_stage": context.current_stage.value,
            "session_id": context.session_id,
            "transition_start_time": (
                context.transition_start_time.isoformat()
                if context.transition_start_time
                else None
            ),
            "therapeutic_goals": context.therapeutic_goals,
            "error_message": context.error_message,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the transition service."""
        return {**self.metrics, "active_transitions": len(self.active_transitions)}
