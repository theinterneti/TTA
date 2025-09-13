"""
Multiverse Navigation Service

This service builds the interface and logic for players to navigate between different
story experiences within their personal multiverse, enabling seamless story switching.
"""

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .concurrent_world_state_manager import (
    ConcurrentWorldStateManager,
    WorldInstance,
)
from .cross_story_character_persistence import CrossStoryCharacterPersistence
from .gameplay_chat_manager import GameplayChatManager
from .story_branching_service import StoryBranchingService

logger = logging.getLogger(__name__)


class NavigationType(str, Enum):
    """Types of multiverse navigation."""

    STORY_SWITCH = "story_switch"
    BRANCH_JUMP = "branch_jump"
    TIMELINE_TRAVEL = "timeline_travel"
    WORLD_PORTAL = "world_portal"
    MEMORY_DIVE = "memory_dive"
    THERAPEUTIC_RETURN = "therapeutic_return"


class NavigationTransition(str, Enum):
    """Types of navigation transitions."""

    INSTANT = "instant"
    FADE_TRANSITION = "fade_transition"
    PORTAL_EFFECT = "portal_effect"
    DREAM_SEQUENCE = "dream_sequence"
    THERAPEUTIC_BRIDGE = "therapeutic_bridge"
    NARRATIVE_WEAVE = "narrative_weave"


@dataclass
class MultiverseDestination:
    """Represents a destination in the multiverse."""

    destination_id: str
    destination_type: str  # "world_instance", "story_branch", "memory_point"
    instance_id: str
    world_id: str
    character_id: str
    title: str
    description: str
    thumbnail_data: dict[str, Any] | None
    navigation_metadata: dict[str, Any]
    therapeutic_context: dict[str, Any]
    accessibility: dict[str, Any]
    last_visited: datetime | None
    visit_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.last_visited:
            data["last_visited"] = self.last_visited.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MultiverseDestination":
        """Create from dictionary."""
        if data.get("last_visited"):
            data["last_visited"] = datetime.fromisoformat(data["last_visited"])
        return cls(**data)


@dataclass
class NavigationRequest:
    """Request for multiverse navigation."""

    request_id: str
    player_id: str
    current_session_id: str
    destination: MultiverseDestination
    navigation_type: NavigationType
    transition_type: NavigationTransition
    preserve_context: bool
    therapeutic_continuity: bool
    custom_parameters: dict[str, Any]
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["destination"] = self.destination.to_dict()
        return data


class MultiverseNavigationService:
    """
    Service for multiverse navigation and story switching capabilities.

    Provides seamless navigation between different story experiences within a player's
    personal multiverse, maintaining therapeutic continuity and narrative coherence.
    """

    def __init__(
        self,
        world_state_manager: ConcurrentWorldStateManager | None = None,
        story_branching_service: StoryBranchingService | None = None,
        character_persistence: CrossStoryCharacterPersistence | None = None,
        chat_manager: GameplayChatManager | None = None,
    ):
        """
        Initialize the Multiverse Navigation Service.

        Args:
            world_state_manager: Concurrent world state manager
            story_branching_service: Story branching service
            character_persistence: Cross-story character persistence
            chat_manager: Gameplay chat manager
        """
        self.world_state_manager = world_state_manager or ConcurrentWorldStateManager()
        self.story_branching_service = (
            story_branching_service or StoryBranchingService()
        )
        self.character_persistence = (
            character_persistence or CrossStoryCharacterPersistence()
        )
        self.chat_manager = chat_manager or GameplayChatManager()

        # Navigation state
        self.active_navigations: dict[str, NavigationRequest] = {}
        self.player_destinations: dict[str, list[MultiverseDestination]] = {}

        # Navigation effects and transitions
        self.transition_handlers = self._build_transition_handlers()
        self.navigation_effects = self._build_navigation_effects()

        # Configuration
        self.max_destinations_per_player = 20
        self.enable_therapeutic_guidance = True
        self.auto_save_before_navigation = True
        self.transition_duration_seconds = 3

        # Metrics
        self.metrics = {
            "navigations_completed": 0,
            "story_switches": 0,
            "branch_jumps": 0,
            "therapeutic_returns": 0,
            "destinations_discovered": 0,
            "navigation_failures": 0,
            "therapeutic_continuity_maintained": 0,
        }

        logger.info("MultiverseNavigationService initialized")

    async def discover_multiverse_destinations(
        self, player_id: str
    ) -> list[MultiverseDestination]:
        """
        Discover available destinations in a player's multiverse.

        Args:
            player_id: Player identifier

        Returns:
            List of available destinations
        """
        try:
            destinations = []

            # Get player's multiverse context
            multiverse = await self.world_state_manager.get_player_multiverse(player_id)
            if not multiverse:
                return destinations

            # Discover destinations from active instances
            for instance_id in multiverse.active_instances:
                instance = await self.world_state_manager.get_world_instance(
                    instance_id
                )
                if instance:
                    destination = await self._create_destination_from_instance(instance)
                    if destination:
                        destinations.append(destination)

            # Discover destinations from story branches
            branch_destinations = await self._discover_branch_destinations(player_id)
            destinations.extend(branch_destinations)

            # Discover therapeutic return points
            therapeutic_destinations = await self._discover_therapeutic_destinations(
                player_id
            )
            destinations.extend(therapeutic_destinations)

            # Cache destinations for player
            self.player_destinations[player_id] = destinations

            # Update metrics
            self.metrics["destinations_discovered"] += len(destinations)

            logger.info(
                f"Discovered {len(destinations)} destinations for player {player_id}"
            )
            return destinations

        except Exception as e:
            logger.error(f"Error discovering multiverse destinations: {e}")
            return []

    async def navigate_to_destination(
        self,
        player_id: str,
        current_session_id: str,
        destination_id: str,
        navigation_type: NavigationType = NavigationType.STORY_SWITCH,
        transition_type: NavigationTransition = NavigationTransition.FADE_TRANSITION,
        preserve_context: bool = True,
        therapeutic_continuity: bool = True,
    ) -> dict[str, Any] | None:
        """
        Navigate to a destination in the multiverse.

        Args:
            player_id: Player identifier
            current_session_id: Current session identifier
            destination_id: Target destination identifier
            navigation_type: Type of navigation
            transition_type: Type of transition effect
            preserve_context: Whether to preserve current context
            therapeutic_continuity: Whether to maintain therapeutic continuity

        Returns:
            Navigation result if successful, None otherwise
        """
        try:
            # Find destination
            destination = await self._find_destination(player_id, destination_id)
            if not destination:
                logger.error(
                    f"Destination {destination_id} not found for player {player_id}"
                )
                return None

            # Check accessibility
            accessibility_check = await self._check_destination_accessibility(
                player_id, destination
            )
            if not accessibility_check["accessible"]:
                logger.warning(
                    f"Destination {destination_id} not accessible: {accessibility_check['reason']}"
                )
                return {
                    "success": False,
                    "error": "destination_not_accessible",
                    "reason": accessibility_check["reason"],
                }

            # Create navigation request
            request_id = f"nav_{player_id}_{uuid.uuid4().hex[:8]}"
            navigation_request = NavigationRequest(
                request_id=request_id,
                player_id=player_id,
                current_session_id=current_session_id,
                destination=destination,
                navigation_type=navigation_type,
                transition_type=transition_type,
                preserve_context=preserve_context,
                therapeutic_continuity=therapeutic_continuity,
                custom_parameters={},
                created_at=datetime.utcnow(),
            )

            # Store active navigation
            self.active_navigations[request_id] = navigation_request

            # Execute navigation
            navigation_result = await self._execute_navigation(navigation_request)

            # Clean up navigation request
            if request_id in self.active_navigations:
                del self.active_navigations[request_id]

            # Update destination visit info
            if navigation_result and navigation_result.get("success"):
                await self._update_destination_visit_info(destination)

            return navigation_result

        except Exception as e:
            logger.error(f"Error navigating to destination: {e}")
            self.metrics["navigation_failures"] += 1
            return {"success": False, "error": "navigation_failed", "message": str(e)}

    async def get_navigation_history(self, player_id: str) -> list[dict[str, Any]]:
        """
        Get navigation history for a player.

        Args:
            player_id: Player identifier

        Returns:
            List of navigation history entries
        """
        try:
            destinations = await self.discover_multiverse_destinations(player_id)

            # Sort by last visited and visit count
            visited_destinations = [
                d for d in destinations if d.last_visited is not None
            ]
            visited_destinations.sort(
                key=lambda x: (x.last_visited, x.visit_count), reverse=True
            )

            history = []
            for destination in visited_destinations:
                history.append(
                    {
                        "destination_id": destination.destination_id,
                        "title": destination.title,
                        "description": destination.description,
                        "last_visited": (
                            destination.last_visited.isoformat()
                            if destination.last_visited
                            else None
                        ),
                        "visit_count": destination.visit_count,
                        "world_id": destination.world_id,
                        "therapeutic_context": destination.therapeutic_context,
                    }
                )

            return history

        except Exception as e:
            logger.error(f"Error getting navigation history: {e}")
            return []

    async def create_therapeutic_return_point(
        self,
        player_id: str,
        current_session_id: str,
        return_point_name: str,
        therapeutic_context: dict[str, Any],
    ) -> str | None:
        """
        Create a therapeutic return point for later navigation.

        Args:
            player_id: Player identifier
            current_session_id: Current session identifier
            return_point_name: Name for the return point
            therapeutic_context: Therapeutic context to preserve

        Returns:
            Return point ID if successful, None otherwise
        """
        try:
            # Get current world instance
            multiverse = await self.world_state_manager.get_player_multiverse(player_id)
            if not multiverse or not multiverse.primary_instance_id:
                logger.error("No primary instance found for therapeutic return point")
                return None

            instance = await self.world_state_manager.get_world_instance(
                multiverse.primary_instance_id
            )
            if not instance:
                return None

            # Create return point destination
            return_point_id = f"trp_{player_id}_{uuid.uuid4().hex[:8]}"

            destination = MultiverseDestination(
                destination_id=return_point_id,
                destination_type="therapeutic_return_point",
                instance_id=instance.instance_id,
                world_id=instance.world_id,
                character_id=instance.character_id,
                title=return_point_name,
                description=f"Therapeutic return point: {return_point_name}",
                thumbnail_data=None,
                navigation_metadata={
                    "return_point": True,
                    "session_id": current_session_id,
                    "created_at": datetime.utcnow().isoformat(),
                },
                therapeutic_context=therapeutic_context,
                accessibility={"always_accessible": True},
                last_visited=None,
                visit_count=0,
            )

            # Add to player destinations
            if player_id not in self.player_destinations:
                self.player_destinations[player_id] = []

            self.player_destinations[player_id].append(destination)

            # Update metrics
            self.metrics["therapeutic_returns"] += 1

            logger.info(f"Created therapeutic return point {return_point_id}")
            return return_point_id

        except Exception as e:
            logger.error(f"Error creating therapeutic return point: {e}")
            return None

    # Private helper methods

    async def _execute_navigation(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute a navigation request."""
        try:
            # Auto-save current state if enabled
            if self.auto_save_before_navigation:
                await self._save_current_state(
                    request.player_id, request.current_session_id
                )

            # Prepare character for transfer if needed
            character_data = None
            if request.therapeutic_continuity:
                character_data = (
                    await self.character_persistence.transfer_character_to_story(
                        request.destination.character_id,
                        request.destination.instance_id,
                    )
                )

            # Execute transition effect
            transition_result = await self._execute_transition_effect(request)

            # Switch to destination
            switch_result = await self._switch_to_destination(request, character_data)

            if switch_result.get("success"):
                # Update metrics
                self.metrics["navigations_completed"] += 1
                self._update_navigation_type_metrics(request.navigation_type)

                if request.therapeutic_continuity:
                    self.metrics["therapeutic_continuity_maintained"] += 1

                return {
                    "success": True,
                    "destination_id": request.destination.destination_id,
                    "new_session_id": switch_result.get("new_session_id"),
                    "transition_effect": transition_result,
                    "character_transferred": character_data is not None,
                    "therapeutic_continuity": request.therapeutic_continuity,
                }
            else:
                return {
                    "success": False,
                    "error": "destination_switch_failed",
                    "details": switch_result,
                }

        except Exception as e:
            logger.error(f"Error executing navigation: {e}")
            return {
                "success": False,
                "error": "navigation_execution_failed",
                "message": str(e),
            }

    async def _create_destination_from_instance(
        self, instance: WorldInstance
    ) -> MultiverseDestination | None:
        """Create a destination from a world instance."""
        try:
            destination_id = f"dest_{instance.instance_id}"

            # Generate title and description
            title = f"Story in {instance.world_id}"
            description = f"Continue your adventure in {instance.world_id}"

            # Add branch context if available
            if instance.branch_point:
                title += f" (Branch: {instance.branch_type.value})"
                description += f" - {instance.branch_type.value} branch"

            return MultiverseDestination(
                destination_id=destination_id,
                destination_type="world_instance",
                instance_id=instance.instance_id,
                world_id=instance.world_id,
                character_id=instance.character_id,
                title=title,
                description=description,
                thumbnail_data=None,
                navigation_metadata={
                    "branch_type": instance.branch_type.value,
                    "state": instance.state.value,
                    "created_at": instance.created_at.isoformat(),
                },
                therapeutic_context=instance.therapeutic_context,
                accessibility={"accessible": instance.state.value == "active"},
                last_visited=instance.last_accessed,
                visit_count=instance.access_count,
            )

        except Exception as e:
            logger.error(f"Error creating destination from instance: {e}")
            return None

    async def _discover_branch_destinations(
        self, player_id: str
    ) -> list[MultiverseDestination]:
        """Discover destinations from story branches."""
        try:
            destinations = []

            # Get player's story branches
            branches = (
                await self.story_branching_service.get_player_multiverse_branches(
                    player_id
                )
            )

            for branch_info in branches:
                destination_id = f"branch_{branch_info['branch_id']}"

                destination = MultiverseDestination(
                    destination_id=destination_id,
                    destination_type="story_branch",
                    instance_id=branch_info["instance_id"],
                    world_id="",  # Would be extracted from branch info
                    character_id="",  # Would be extracted from branch info
                    title=f"Branch: {branch_info['branch_type']}",
                    description=branch_info.get(
                        "narrative_summary", "Explore this story branch"
                    ),
                    thumbnail_data=None,
                    navigation_metadata={
                        "branch_id": branch_info["branch_id"],
                        "branch_type": branch_info["branch_type"],
                        "trigger_type": branch_info["trigger_type"],
                    },
                    therapeutic_context=branch_info.get("therapeutic_progress", {}),
                    accessibility={"accessible": True},
                    last_visited=datetime.fromisoformat(branch_info["last_updated"]),
                    visit_count=0,
                )

                destinations.append(destination)

            return destinations

        except Exception as e:
            logger.error(f"Error discovering branch destinations: {e}")
            return []

    async def _discover_therapeutic_destinations(
        self, player_id: str
    ) -> list[MultiverseDestination]:
        """Discover therapeutic return point destinations."""
        try:
            destinations = []

            # Get existing therapeutic return points for player
            if player_id in self.player_destinations:
                therapeutic_destinations = [
                    d
                    for d in self.player_destinations[player_id]
                    if d.destination_type == "therapeutic_return_point"
                ]
                destinations.extend(therapeutic_destinations)

            return destinations

        except Exception as e:
            logger.error(f"Error discovering therapeutic destinations: {e}")
            return []

    async def _find_destination(
        self, player_id: str, destination_id: str
    ) -> MultiverseDestination | None:
        """Find a destination by ID."""
        try:
            if player_id not in self.player_destinations:
                await self.discover_multiverse_destinations(player_id)

            destinations = self.player_destinations.get(player_id, [])

            for destination in destinations:
                if destination.destination_id == destination_id:
                    return destination

            return None

        except Exception as e:
            logger.error(f"Error finding destination: {e}")
            return None

    async def _check_destination_accessibility(
        self, player_id: str, destination: MultiverseDestination
    ) -> dict[str, Any]:
        """Check if a destination is accessible."""
        try:
            accessibility = destination.accessibility

            # Always accessible destinations
            if accessibility.get("always_accessible", False):
                return {"accessible": True}

            # Check basic accessibility
            if not accessibility.get("accessible", True):
                return {"accessible": False, "reason": "destination_not_available"}

            # Check therapeutic prerequisites if any
            if self.enable_therapeutic_guidance:
                therapeutic_check = await self._check_therapeutic_prerequisites(
                    player_id, destination
                )
                if not therapeutic_check["accessible"]:
                    return therapeutic_check

            return {"accessible": True}

        except Exception as e:
            logger.error(f"Error checking destination accessibility: {e}")
            return {"accessible": False, "reason": "accessibility_check_failed"}

    async def _check_therapeutic_prerequisites(
        self, player_id: str, destination: MultiverseDestination
    ) -> dict[str, Any]:
        """Check therapeutic prerequisites for destination access."""
        try:
            # This would implement therapeutic prerequisite checking
            # For now, allow all destinations
            return {"accessible": True}

        except Exception as e:
            logger.error(f"Error checking therapeutic prerequisites: {e}")
            return {"accessible": False, "reason": "therapeutic_check_failed"}

    async def _save_current_state(self, player_id: str, session_id: str) -> None:
        """Save current state before navigation."""
        try:
            # This would save current session state
            logger.debug(
                f"Would save current state for player {player_id}, session {session_id}"
            )

        except Exception as e:
            logger.error(f"Error saving current state: {e}")

    async def _execute_transition_effect(
        self, request: NavigationRequest
    ) -> dict[str, Any]:
        """Execute transition effect for navigation."""
        try:
            transition_handler = self.transition_handlers.get(request.transition_type)
            if not transition_handler:
                return {"effect": "none", "duration": 0}

            # Execute transition effect
            effect_result = await transition_handler(request)

            # Send transition effect to chat
            await self._send_transition_to_chat(request, effect_result)

            return effect_result

        except Exception as e:
            logger.error(f"Error executing transition effect: {e}")
            return {"effect": "error", "duration": 0}

    async def _switch_to_destination(
        self, request: NavigationRequest, character_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Switch to the destination."""
        try:
            destination = request.destination

            # Generate new session ID for destination
            new_session_id = f"nav_session_{request.player_id}_{uuid.uuid4().hex[:8]}"

            # Update world instance state if needed
            if destination.destination_type == "world_instance":
                instance = await self.world_state_manager.get_world_instance(
                    destination.instance_id
                )
                if instance:
                    # Update instance with navigation context
                    navigation_updates = {
                        "navigation_entry": {
                            "from_session": request.current_session_id,
                            "navigation_type": request.navigation_type.value,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    }

                    await self.world_state_manager.update_world_state(
                        destination.instance_id,
                        navigation_updates,
                        navigation_updates,
                        request.destination.therapeutic_context,
                    )

            return {
                "success": True,
                "new_session_id": new_session_id,
                "destination_type": destination.destination_type,
                "instance_id": destination.instance_id,
            }

        except Exception as e:
            logger.error(f"Error switching to destination: {e}")
            return {"success": False, "error": str(e)}

    async def _send_transition_to_chat(
        self, request: NavigationRequest, effect_result: dict[str, Any]
    ) -> None:
        """Send transition effect to chat interface."""
        try:
            transition_message = {
                "type": "multiverse_navigation",
                "session_id": request.current_session_id,
                "content": {
                    "navigation_type": request.navigation_type.value,
                    "transition_type": request.transition_type.value,
                    "destination_title": request.destination.title,
                    "destination_description": request.destination.description,
                    "effect_data": effect_result,
                    "therapeutic_context": request.destination.therapeutic_context,
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "destination_id": request.destination.destination_id,
                    "preserve_context": request.preserve_context,
                    "therapeutic_continuity": request.therapeutic_continuity,
                },
            }

            await self.chat_manager.broadcast_to_session(
                request.current_session_id, transition_message
            )

        except Exception as e:
            logger.error(f"Error sending transition to chat: {e}")

    async def _update_destination_visit_info(
        self, destination: MultiverseDestination
    ) -> None:
        """Update destination visit information."""
        try:
            destination.last_visited = datetime.utcnow()
            destination.visit_count += 1

        except Exception as e:
            logger.error(f"Error updating destination visit info: {e}")

    def _update_navigation_type_metrics(self, navigation_type: NavigationType) -> None:
        """Update metrics for specific navigation types."""
        if navigation_type == NavigationType.STORY_SWITCH:
            self.metrics["story_switches"] += 1
        elif navigation_type == NavigationType.BRANCH_JUMP:
            self.metrics["branch_jumps"] += 1
        elif navigation_type == NavigationType.THERAPEUTIC_RETURN:
            self.metrics["therapeutic_returns"] += 1

    def _build_transition_handlers(self) -> dict[NavigationTransition, callable]:
        """Build transition effect handlers."""
        return {
            NavigationTransition.INSTANT: self._instant_transition,
            NavigationTransition.FADE_TRANSITION: self._fade_transition,
            NavigationTransition.PORTAL_EFFECT: self._portal_transition,
            NavigationTransition.DREAM_SEQUENCE: self._dream_transition,
            NavigationTransition.THERAPEUTIC_BRIDGE: self._therapeutic_transition,
            NavigationTransition.NARRATIVE_WEAVE: self._narrative_transition,
        }

    def _build_navigation_effects(self) -> dict[str, Any]:
        """Build navigation effect configurations."""
        return {
            "fade_duration": 2.0,
            "portal_animation_time": 3.0,
            "dream_sequence_time": 4.0,
            "therapeutic_bridge_time": 2.5,
            "narrative_weave_time": 3.5,
        }

    async def _instant_transition(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute instant transition effect."""
        return {
            "effect": "instant",
            "duration": 0,
            "description": "You instantly find yourself in a new story...",
        }

    async def _fade_transition(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute fade transition effect."""
        return {
            "effect": "fade",
            "duration": self.navigation_effects["fade_duration"],
            "description": "The world around you gently fades as you transition to a new story...",
            "stages": ["fade_out", "transition", "fade_in"],
        }

    async def _portal_transition(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute portal transition effect."""
        return {
            "effect": "portal",
            "duration": self.navigation_effects["portal_animation_time"],
            "description": "A shimmering portal opens before you, leading to another story...",
            "visual_effects": ["portal_opening", "energy_swirl", "dimensional_shift"],
        }

    async def _dream_transition(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute dream sequence transition effect."""
        return {
            "effect": "dream_sequence",
            "duration": self.navigation_effects["dream_sequence_time"],
            "description": "Reality blurs like a dream as you drift into another narrative...",
            "atmosphere": "ethereal",
        }

    async def _therapeutic_transition(
        self, request: NavigationRequest
    ) -> dict[str, Any]:
        """Execute therapeutic bridge transition effect."""
        return {
            "effect": "therapeutic_bridge",
            "duration": self.navigation_effects["therapeutic_bridge_time"],
            "description": "You take a moment to reflect as you prepare to continue your journey...",
            "therapeutic_elements": request.destination.therapeutic_context,
        }

    async def _narrative_transition(self, request: NavigationRequest) -> dict[str, Any]:
        """Execute narrative weave transition effect."""
        return {
            "effect": "narrative_weave",
            "duration": self.navigation_effects["narrative_weave_time"],
            "description": "The threads of your story weave together as you move to a new chapter...",
            "narrative_continuity": True,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the multiverse navigation service."""
        return {
            **self.metrics,
            "active_navigations": len(self.active_navigations),
            "cached_destinations": sum(
                len(dests) for dests in self.player_destinations.values()
            ),
            "max_destinations_per_player": self.max_destinations_per_player,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the multiverse navigation service."""
        try:
            return {
                "active_navigations": len(self.active_navigations),
                "cached_destinations": sum(
                    len(dests) for dests in self.player_destinations.values()
                ),
                "world_state_manager_available": self.world_state_manager is not None,
                "story_branching_service_available": self.story_branching_service
                is not None,
                "character_persistence_available": self.character_persistence
                is not None,
                "chat_manager_available": self.chat_manager is not None,
                "overall_status": "healthy",
            }

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"overall_status": "error", "error": str(e)}
