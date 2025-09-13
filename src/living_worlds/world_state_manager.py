"""
World State Manager for TTA Living Worlds System

Main world state tracking and persistence controller that manages dynamic
world states, coordinates with other Living Worlds components, and ensures
real-time world evolution with therapeutic context integration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from .choice_impact_tracker import ChoiceImpactTracker
from .evolution_engine import EvolutionEngine
from .models import ChoiceImpact, EvolutionEvent, WorldState, WorldStateType
from .persistence_layer import PersistenceLayer

logger = logging.getLogger(__name__)


class WorldStateManager:
    """
    Main controller for world state management in the Living Worlds system.

    Coordinates world state tracking, persistence, choice impact processing,
    and real-time world evolution while maintaining therapeutic context.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

        # Component dependencies
        self.persistence_layer = PersistenceLayer(config)
        self.choice_impact_tracker = ChoiceImpactTracker(config)
        self.evolution_engine = EvolutionEngine(config)

        # Active world states
        self.active_worlds: dict[str, WorldState] = {}
        self.world_locks: dict[str, asyncio.Lock] = {}

        # Configuration
        self.max_active_worlds = config.get("max_active_worlds", 100)
        self.state_update_interval = config.get("state_update_interval", 30)  # seconds
        self.evolution_check_interval = config.get(
            "evolution_check_interval", 60
        )  # seconds

        # Background tasks
        self._state_update_task: asyncio.Task | None = None
        self._evolution_task: asyncio.Task | None = None

        # Metrics
        self.metrics = {
            "worlds_created": 0,
            "worlds_loaded": 0,
            "state_updates": 0,
            "choice_impacts_processed": 0,
            "evolution_events_processed": 0,
            "persistence_operations": 0,
        }

        logger.info("WorldStateManager initialized")

    async def initialize(self) -> bool:
        """Initialize the World State Manager."""
        try:
            # Initialize components
            await self.persistence_layer.initialize()
            await self.choice_impact_tracker.initialize()
            await self.evolution_engine.initialize()

            # Start background tasks
            self._state_update_task = asyncio.create_task(self._state_update_loop())
            self._evolution_task = asyncio.create_task(self._evolution_loop())

            logger.info("WorldStateManager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize WorldStateManager: {e}")
            return False

    async def shutdown(self):
        """Shutdown the World State Manager."""
        try:
            # Cancel background tasks
            if self._state_update_task:
                self._state_update_task.cancel()
            if self._evolution_task:
                self._evolution_task.cancel()

            # Save all active world states
            for world_id in list(self.active_worlds.keys()):
                await self.save_world_state(world_id)

            # Shutdown components
            await self.persistence_layer.shutdown()
            await self.choice_impact_tracker.shutdown()
            await self.evolution_engine.shutdown()

            logger.info("WorldStateManager shutdown complete")

        except Exception as e:
            logger.error(f"Error during WorldStateManager shutdown: {e}")

    async def create_world_state(
        self,
        world_id: str,
        session_id: str,
        player_id: str,
        therapeutic_context: dict[str, Any] | None = None,
        initial_properties: dict[str, Any] | None = None,
    ) -> bool:
        """
        Create a new world state for a player session.

        Args:
            world_id: Unique world identifier
            session_id: Session identifier
            player_id: Player identifier
            therapeutic_context: Optional therapeutic context
            initial_properties: Optional initial world properties

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if we're at capacity
            if len(self.active_worlds) >= self.max_active_worlds:
                logger.warning("Maximum active worlds reached")
                return False

            # Create world state
            world_state = WorldState(
                world_id=world_id,
                session_id=session_id,
                player_id=player_id,
                state_type=WorldStateType.ACTIVE,
                world_properties=initial_properties or {},
                therapeutic_context=therapeutic_context or {},
            )

            # Initialize world lock
            if world_id not in self.world_locks:
                self.world_locks[world_id] = asyncio.Lock()

            # Store active world state
            self.active_worlds[world_id] = world_state

            # Initialize persistence
            await self.persistence_layer.create_world_persistence(world_id, player_id)

            # Update metrics
            self.metrics["worlds_created"] += 1

            logger.info(
                f"Created world state for world {world_id}, session {session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create world state: {e}")
            return False

    async def load_world_state(
        self, world_id: str, session_id: str
    ) -> WorldState | None:
        """
        Load an existing world state.

        Args:
            world_id: World identifier
            session_id: Session identifier

        Returns:
            WorldState if found, None otherwise
        """
        try:
            # Check if already active
            if world_id in self.active_worlds:
                return self.active_worlds[world_id]

            # Load from persistence
            world_state = await self.persistence_layer.load_world_state(
                world_id, session_id
            )
            if not world_state:
                logger.warning(f"World state not found: {world_id}")
                return None

            # Initialize world lock
            if world_id not in self.world_locks:
                self.world_locks[world_id] = asyncio.Lock()

            # Store as active
            self.active_worlds[world_id] = world_state

            # Update metrics
            self.metrics["worlds_loaded"] += 1

            logger.info(f"Loaded world state for world {world_id}")
            return world_state

        except Exception as e:
            logger.error(f"Failed to load world state: {e}")
            return None

    async def update_world_state(
        self,
        world_id: str,
        state_updates: dict[str, Any],
        therapeutic_updates: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update world state with new data.

        Args:
            world_id: World identifier
            state_updates: Updates to world state
            therapeutic_updates: Optional therapeutic context updates

        Returns:
            True if successful, False otherwise
        """
        try:
            if world_id not in self.active_worlds:
                logger.error(f"World {world_id} not found in active worlds")
                return False

            async with self.world_locks[world_id]:
                world_state = self.active_worlds[world_id]

                # Update world properties
                world_state.world_properties.update(state_updates)

                # Update therapeutic context if provided
                if therapeutic_updates:
                    world_state.therapeutic_context.update(therapeutic_updates)

                # Update metadata
                world_state.last_updated = datetime.utcnow()
                world_state.version += 1

                # Update metrics
                self.metrics["state_updates"] += 1

                logger.debug(f"Updated world state for world {world_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to update world state: {e}")
            return False

    async def process_choice_impact(
        self, world_id: str, choice_id: str, choice_data: dict[str, Any]
    ) -> ChoiceImpact | None:
        """
        Process the impact of a player choice on the world.

        Args:
            world_id: World identifier
            choice_id: Choice identifier
            choice_data: Choice data and context

        Returns:
            ChoiceImpact if successful, None otherwise
        """
        try:
            if world_id not in self.active_worlds:
                logger.error(f"World {world_id} not found")
                return None

            world_state = self.active_worlds[world_id]

            # Process choice impact
            choice_impact = await self.choice_impact_tracker.process_choice(
                world_state, choice_id, choice_data
            )

            if choice_impact:
                # Apply immediate consequences
                await self._apply_choice_consequences(world_id, choice_impact)

                # Update metrics
                self.metrics["choice_impacts_processed"] += 1

                logger.info(
                    f"Processed choice impact for world {world_id}, choice {choice_id}"
                )

            return choice_impact

        except Exception as e:
            logger.error(f"Failed to process choice impact: {e}")
            return None

    async def save_world_state(self, world_id: str) -> bool:
        """
        Save world state to persistence layer.

        Args:
            world_id: World identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            if world_id not in self.active_worlds:
                logger.error(f"World {world_id} not found")
                return False

            async with self.world_locks[world_id]:
                world_state = self.active_worlds[world_id]
                success = await self.persistence_layer.save_world_state(world_state)

                if success:
                    self.metrics["persistence_operations"] += 1
                    logger.debug(f"Saved world state for world {world_id}")

                return success

        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False

    async def get_world_state(self, world_id: str) -> WorldState | None:
        """Get current world state."""
        return self.active_worlds.get(world_id)

    async def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        return {
            **self.metrics,
            "active_worlds": len(self.active_worlds),
            "world_locks": len(self.world_locks),
        }

    # Private methods

    async def _apply_choice_consequences(
        self, world_id: str, choice_impact: ChoiceImpact
    ) -> bool:
        """Apply immediate consequences of a choice impact."""
        try:
            # Apply immediate consequences to world state
            state_updates = choice_impact.immediate_consequences
            therapeutic_updates = choice_impact.therapeutic_consequences

            return await self.update_world_state(
                world_id, state_updates, therapeutic_updates
            )

        except Exception as e:
            logger.error(f"Failed to apply choice consequences: {e}")
            return False

    async def _state_update_loop(self):
        """Background task for periodic state updates."""
        while True:
            try:
                await asyncio.sleep(self.state_update_interval)

                # Save all active world states
                for world_id in list(self.active_worlds.keys()):
                    await self.save_world_state(world_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state update loop: {e}")

    async def _evolution_loop(self):
        """Background task for world evolution processing."""
        while True:
            try:
                await asyncio.sleep(self.evolution_check_interval)

                # Process evolution for all active worlds
                for world_id, world_state in list(self.active_worlds.items()):
                    evolution_events = (
                        await self.evolution_engine.check_evolution_triggers(
                            world_state
                        )
                    )

                    for event in evolution_events:
                        await self._process_evolution_event(world_id, event)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in evolution loop: {e}")

    async def _process_evolution_event(
        self, world_id: str, evolution_event: EvolutionEvent
    ) -> bool:
        """Process a single evolution event."""
        try:
            # Apply evolution changes
            state_updates = evolution_event.state_changes
            therapeutic_updates = evolution_event.therapeutic_changes

            success = await self.update_world_state(
                world_id, state_updates, therapeutic_updates
            )

            if success:
                # Mark event as processed
                evolution_event.processed = True
                evolution_event.processing_result = {"success": True}

                # Update metrics
                self.metrics["evolution_events_processed"] += 1

                logger.info(f"Processed evolution event {evolution_event.event_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to process evolution event: {e}")
            return False
