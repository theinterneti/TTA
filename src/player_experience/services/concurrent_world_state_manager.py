"""
Concurrent World State Manager

This service enhances the existing world state management system to support multiple
concurrent story experiences with proper state isolation and multiverse capabilities.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.gameplay_loop.services.session_integration_manager import (
    SessionIntegrationManager,
)

logger = logging.getLogger(__name__)


class WorldInstanceState(str, Enum):
    """States for world instances."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    ERROR = "error"


class StoryBranchType(str, Enum):
    """Types of story branches."""

    MAIN_TIMELINE = "main_timeline"
    ALTERNATE_CHOICE = "alternate_choice"
    THERAPEUTIC_EXPLORATION = "therapeutic_exploration"
    SKILL_PRACTICE = "skill_practice"
    MEMORY_REPLAY = "memory_replay"
    WHAT_IF_SCENARIO = "what_if_scenario"


@dataclass
class WorldInstance:
    """Represents an isolated instance of a world for concurrent story support."""

    instance_id: str
    world_id: str
    player_id: str
    character_id: str
    session_id: str
    branch_type: StoryBranchType
    parent_instance_id: str | None
    state: WorldInstanceState
    world_state: dict[str, Any]
    narrative_context: dict[str, Any]
    therapeutic_context: dict[str, Any]
    branch_point: dict[str, Any] | None
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorldInstance":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        data["state"] = WorldInstanceState(data["state"])
        data["branch_type"] = StoryBranchType(data["branch_type"])
        return cls(**data)


@dataclass
class MultiverseContext:
    """Context for a player's multiverse of story experiences."""

    player_id: str
    active_instances: list[str]
    archived_instances: list[str]
    primary_instance_id: str | None
    branch_tree: dict[str, list[str]]  # parent_id -> [child_ids]
    therapeutic_progress: dict[str, Any]
    cross_story_continuity: dict[str, Any]
    created_at: datetime
    last_updated: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MultiverseContext":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)


class ConcurrentWorldStateManager:
    """
    Enhanced world state manager supporting multiple concurrent story experiences.

    Provides state isolation, multiverse management, and cross-story continuity
    while maintaining therapeutic progress and character development.
    """

    def __init__(self, session_manager: SessionIntegrationManager | None = None):
        """
        Initialize the Concurrent World State Manager.

        Args:
            session_manager: Session integration manager for Redis operations
        """
        self.session_manager = session_manager or SessionIntegrationManager()

        # Storage key patterns
        self.world_instance_key_pattern = "world_instance:{instance_id}"
        self.multiverse_context_key_pattern = "multiverse:{player_id}"
        self.player_instances_key_pattern = "player_instances:{player_id}"
        self.world_state_key_pattern = "world_state:{instance_id}"

        # In-memory caches for performance
        self.instance_cache: dict[str, WorldInstance] = {}
        self.multiverse_cache: dict[str, MultiverseContext] = {}

        # Configuration
        self.max_concurrent_instances_per_player = 5
        self.instance_expiry_days = 30
        self.cache_ttl_minutes = 15
        self.auto_archive_inactive_days = 7

        # Background tasks
        self.cleanup_task: asyncio.Task | None = None
        self.is_running = False

        # Metrics
        self.metrics = {
            "world_instances_created": 0,
            "world_instances_active": 0,
            "world_instances_archived": 0,
            "multiverse_contexts_managed": 0,
            "state_isolations_maintained": 0,
            "cross_story_continuities_tracked": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        logger.info("ConcurrentWorldStateManager initialized")

    async def start(self) -> None:
        """Start the concurrent world state manager."""
        if self.is_running:
            logger.warning("Concurrent world state manager is already running")
            return

        self.is_running = True

        # Start background cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Concurrent world state manager started")

    async def stop(self) -> None:
        """Stop the concurrent world state manager."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel cleanup task
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Clear caches
        self.instance_cache.clear()
        self.multiverse_cache.clear()

        logger.info("Concurrent world state manager stopped")

    async def create_world_instance(
        self,
        world_id: str,
        player_id: str,
        character_id: str,
        session_id: str,
        branch_type: StoryBranchType = StoryBranchType.MAIN_TIMELINE,
        parent_instance_id: str | None = None,
        initial_state: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Create a new world instance for concurrent story support.

        Args:
            world_id: World identifier
            player_id: Player identifier
            character_id: Character identifier
            session_id: Session identifier
            branch_type: Type of story branch
            parent_instance_id: Parent instance for branching
            initial_state: Initial world state

        Returns:
            Instance ID if successful, None otherwise
        """
        try:
            # Check concurrent instance limit
            player_instances = await self._get_player_active_instances(player_id)
            if len(player_instances) >= self.max_concurrent_instances_per_player:
                logger.warning(
                    f"Player {player_id} has reached max concurrent instances limit"
                )
                return None

            # Generate instance ID
            instance_id = f"wi_{world_id}_{player_id}_{uuid.uuid4().hex[:8]}"

            # Create world instance
            instance = WorldInstance(
                instance_id=instance_id,
                world_id=world_id,
                player_id=player_id,
                character_id=character_id,
                session_id=session_id,
                branch_type=branch_type,
                parent_instance_id=parent_instance_id,
                state=WorldInstanceState.INITIALIZING,
                world_state=initial_state or {},
                narrative_context={},
                therapeutic_context={},
                branch_point=None,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
            )

            # Save instance
            await self._save_world_instance(instance)

            # Update multiverse context
            await self._update_multiverse_context(player_id, instance_id, "add")

            # Update player instances list
            await self._update_player_instances_list(player_id, instance_id, "add")

            # Set state to active
            instance.state = WorldInstanceState.ACTIVE
            await self._save_world_instance(instance)

            # Update metrics
            self.metrics["world_instances_created"] += 1
            self.metrics["world_instances_active"] += 1

            logger.info(f"Created world instance {instance_id} for player {player_id}")
            return instance_id

        except Exception as e:
            logger.error(f"Error creating world instance: {e}")
            return None

    async def get_world_instance(self, instance_id: str) -> WorldInstance | None:
        """
        Get a world instance by ID.

        Args:
            instance_id: Instance identifier

        Returns:
            WorldInstance if found, None otherwise
        """
        try:
            # Check cache first
            if instance_id in self.instance_cache:
                instance = self.instance_cache[instance_id]
                # Update last accessed
                instance.last_accessed = datetime.utcnow()
                instance.access_count += 1
                await self._save_world_instance(instance)
                self.metrics["cache_hits"] += 1
                return instance

            # Load from storage
            instance_key = self.world_instance_key_pattern.format(
                instance_id=instance_id
            )
            instance_data = await self.session_manager.get_session_data(instance_key)

            if not instance_data:
                self.metrics["cache_misses"] += 1
                return None

            if isinstance(instance_data, str):
                instance_data = json.loads(instance_data)

            instance = WorldInstance.from_dict(instance_data)

            # Update access info
            instance.last_accessed = datetime.utcnow()
            instance.access_count += 1

            # Cache the instance
            self.instance_cache[instance_id] = instance

            # Save updated access info
            await self._save_world_instance(instance)

            self.metrics["cache_misses"] += 1
            return instance

        except Exception as e:
            logger.error(f"Error getting world instance {instance_id}: {e}")
            return None

    async def update_world_state(
        self,
        instance_id: str,
        state_updates: dict[str, Any],
        narrative_updates: dict[str, Any] | None = None,
        therapeutic_updates: dict[str, Any] | None = None,
    ) -> bool:
        """
        Update world state for a specific instance.

        Args:
            instance_id: Instance identifier
            state_updates: Updates to world state
            narrative_updates: Optional narrative context updates
            therapeutic_updates: Optional therapeutic context updates

        Returns:
            True if successful, False otherwise
        """
        try:
            instance = await self.get_world_instance(instance_id)
            if not instance:
                logger.error(f"Instance {instance_id} not found")
                return False

            # Update world state
            instance.world_state.update(state_updates)

            # Update narrative context if provided
            if narrative_updates:
                instance.narrative_context.update(narrative_updates)

            # Update therapeutic context if provided
            if therapeutic_updates:
                instance.therapeutic_context.update(therapeutic_updates)

            # Update last accessed
            instance.last_accessed = datetime.utcnow()

            # Save updated instance
            await self._save_world_instance(instance)

            # Update metrics
            self.metrics["state_isolations_maintained"] += 1

            logger.debug(f"Updated world state for instance {instance_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating world state for {instance_id}: {e}")
            return False

    async def create_story_branch(
        self,
        parent_instance_id: str,
        branch_type: StoryBranchType,
        branch_point: dict[str, Any],
        session_id: str,
    ) -> str | None:
        """
        Create a new story branch from an existing instance.

        Args:
            parent_instance_id: Parent instance identifier
            branch_type: Type of story branch
            branch_point: Information about the branching point
            session_id: New session identifier

        Returns:
            New instance ID if successful, None otherwise
        """
        try:
            # Get parent instance
            parent_instance = await self.get_world_instance(parent_instance_id)
            if not parent_instance:
                logger.error(f"Parent instance {parent_instance_id} not found")
                return None

            # Create branched instance
            branch_instance_id = await self.create_world_instance(
                world_id=parent_instance.world_id,
                player_id=parent_instance.player_id,
                character_id=parent_instance.character_id,
                session_id=session_id,
                branch_type=branch_type,
                parent_instance_id=parent_instance_id,
                initial_state=parent_instance.world_state.copy(),
            )

            if not branch_instance_id:
                return None

            # Update branch instance with branch point
            branch_instance = await self.get_world_instance(branch_instance_id)
            if branch_instance:
                branch_instance.branch_point = branch_point
                branch_instance.narrative_context = (
                    parent_instance.narrative_context.copy()
                )
                branch_instance.therapeutic_context = (
                    parent_instance.therapeutic_context.copy()
                )
                await self._save_world_instance(branch_instance)

            # Update multiverse branch tree
            await self._update_branch_tree(
                parent_instance.player_id, parent_instance_id, branch_instance_id
            )

            logger.info(
                f"Created story branch {branch_instance_id} from {parent_instance_id}"
            )
            return branch_instance_id

        except Exception as e:
            logger.error(f"Error creating story branch: {e}")
            return None

    async def get_player_multiverse(self, player_id: str) -> MultiverseContext | None:
        """
        Get multiverse context for a player.

        Args:
            player_id: Player identifier

        Returns:
            MultiverseContext if found, None otherwise
        """
        try:
            # Check cache first
            if player_id in self.multiverse_cache:
                self.metrics["cache_hits"] += 1
                return self.multiverse_cache[player_id]

            # Load from storage
            multiverse_key = self.multiverse_context_key_pattern.format(
                player_id=player_id
            )
            multiverse_data = await self.session_manager.get_session_data(
                multiverse_key
            )

            if not multiverse_data:
                # Create new multiverse context
                multiverse = MultiverseContext(
                    player_id=player_id,
                    active_instances=[],
                    archived_instances=[],
                    primary_instance_id=None,
                    branch_tree={},
                    therapeutic_progress={},
                    cross_story_continuity={},
                    created_at=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                )

                await self._save_multiverse_context(multiverse)
                self.multiverse_cache[player_id] = multiverse
                self.metrics["multiverse_contexts_managed"] += 1
                return multiverse

            if isinstance(multiverse_data, str):
                multiverse_data = json.loads(multiverse_data)

            multiverse = MultiverseContext.from_dict(multiverse_data)
            self.multiverse_cache[player_id] = multiverse

            self.metrics["cache_misses"] += 1
            return multiverse

        except Exception as e:
            logger.error(f"Error getting player multiverse for {player_id}: {e}")
            return None

    async def archive_world_instance(self, instance_id: str) -> bool:
        """
        Archive a world instance.

        Args:
            instance_id: Instance identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            instance = await self.get_world_instance(instance_id)
            if not instance:
                return False

            # Update state to archived
            instance.state = WorldInstanceState.ARCHIVED
            instance.last_accessed = datetime.utcnow()

            # Save updated instance
            await self._save_world_instance(instance)

            # Update multiverse context
            await self._update_multiverse_context(
                instance.player_id, instance_id, "archive"
            )

            # Remove from cache
            if instance_id in self.instance_cache:
                del self.instance_cache[instance_id]

            # Update metrics
            self.metrics["world_instances_active"] -= 1
            self.metrics["world_instances_archived"] += 1

            logger.info(f"Archived world instance {instance_id}")
            return True

        except Exception as e:
            logger.error(f"Error archiving world instance {instance_id}: {e}")
            return False

    async def get_instance_state_isolation(self, instance_id: str) -> dict[str, Any]:
        """
        Get isolated state information for an instance.

        Args:
            instance_id: Instance identifier

        Returns:
            Isolated state information
        """
        try:
            instance = await self.get_world_instance(instance_id)
            if not instance:
                return {}

            return {
                "instance_id": instance_id,
                "world_state": instance.world_state,
                "narrative_context": instance.narrative_context,
                "therapeutic_context": instance.therapeutic_context,
                "branch_info": {
                    "branch_type": instance.branch_type.value,
                    "parent_instance_id": instance.parent_instance_id,
                    "branch_point": instance.branch_point,
                },
                "isolation_metadata": {
                    "created_at": instance.created_at.isoformat(),
                    "last_accessed": instance.last_accessed.isoformat(),
                    "access_count": instance.access_count,
                    "state": instance.state.value,
                },
            }

        except Exception as e:
            logger.error(f"Error getting instance state isolation: {e}")
            return {}

    # Private helper methods

    async def _save_world_instance(self, instance: WorldInstance) -> None:
        """Save world instance to storage."""
        try:
            instance_key = self.world_instance_key_pattern.format(
                instance_id=instance.instance_id
            )
            instance_data = json.dumps(instance.to_dict(), default=str)

            # Save with expiry
            expiry_seconds = self.instance_expiry_days * 24 * 3600
            await self.session_manager.set_session_data(
                instance_key, instance_data, expiry_seconds
            )

            # Update cache
            self.instance_cache[instance.instance_id] = instance

        except Exception as e:
            logger.error(f"Error saving world instance: {e}")
            raise

    async def _save_multiverse_context(self, multiverse: MultiverseContext) -> None:
        """Save multiverse context to storage."""
        try:
            multiverse_key = self.multiverse_context_key_pattern.format(
                player_id=multiverse.player_id
            )
            multiverse_data = json.dumps(multiverse.to_dict(), default=str)

            # Save with expiry
            expiry_seconds = self.instance_expiry_days * 24 * 3600
            await self.session_manager.set_session_data(
                multiverse_key, multiverse_data, expiry_seconds
            )

            # Update cache
            self.multiverse_cache[multiverse.player_id] = multiverse

        except Exception as e:
            logger.error(f"Error saving multiverse context: {e}")
            raise

    async def _get_player_active_instances(self, player_id: str) -> list[str]:
        """Get list of active instances for a player."""
        try:
            instances_key = self.player_instances_key_pattern.format(
                player_id=player_id
            )
            instances_data = await self.session_manager.get_session_data(instances_key)

            if not instances_data:
                return []

            if isinstance(instances_data, str):
                instances_list = json.loads(instances_data)
            else:
                instances_list = instances_data

            # Filter for active instances
            active_instances = []
            for instance_id in instances_list:
                instance = await self.get_world_instance(instance_id)
                if instance and instance.state == WorldInstanceState.ACTIVE:
                    active_instances.append(instance_id)

            return active_instances

        except Exception as e:
            logger.error(f"Error getting player active instances: {e}")
            return []

    async def _update_multiverse_context(
        self, player_id: str, instance_id: str, action: str
    ) -> None:
        """Update multiverse context with instance changes."""
        try:
            multiverse = await self.get_player_multiverse(player_id)
            if not multiverse:
                return

            if action == "add":
                if instance_id not in multiverse.active_instances:
                    multiverse.active_instances.append(instance_id)
                    if not multiverse.primary_instance_id:
                        multiverse.primary_instance_id = instance_id
            elif action == "archive":
                if instance_id in multiverse.active_instances:
                    multiverse.active_instances.remove(instance_id)
                if instance_id not in multiverse.archived_instances:
                    multiverse.archived_instances.append(instance_id)
                if multiverse.primary_instance_id == instance_id:
                    multiverse.primary_instance_id = (
                        multiverse.active_instances[0]
                        if multiverse.active_instances
                        else None
                    )

            multiverse.last_updated = datetime.utcnow()
            await self._save_multiverse_context(multiverse)

        except Exception as e:
            logger.error(f"Error updating multiverse context: {e}")

    async def _update_player_instances_list(
        self, player_id: str, instance_id: str, action: str
    ) -> None:
        """Update player instances list."""
        try:
            instances_key = self.player_instances_key_pattern.format(
                player_id=player_id
            )
            instances_data = await self.session_manager.get_session_data(instances_key)

            if instances_data:
                if isinstance(instances_data, str):
                    instances_list = json.loads(instances_data)
                else:
                    instances_list = instances_data
            else:
                instances_list = []

            if action == "add" and instance_id not in instances_list:
                instances_list.append(instance_id)
            elif action == "remove" and instance_id in instances_list:
                instances_list.remove(instance_id)

            # Save updated list
            expiry_seconds = self.instance_expiry_days * 24 * 3600
            await self.session_manager.set_session_data(
                instances_key, json.dumps(instances_list), expiry_seconds
            )

        except Exception as e:
            logger.error(f"Error updating player instances list: {e}")

    async def _update_branch_tree(
        self, player_id: str, parent_id: str, child_id: str
    ) -> None:
        """Update branch tree in multiverse context."""
        try:
            multiverse = await self.get_player_multiverse(player_id)
            if not multiverse:
                return

            if parent_id not in multiverse.branch_tree:
                multiverse.branch_tree[parent_id] = []

            if child_id not in multiverse.branch_tree[parent_id]:
                multiverse.branch_tree[parent_id].append(child_id)

            multiverse.last_updated = datetime.utcnow()
            await self._save_multiverse_context(multiverse)

        except Exception as e:
            logger.error(f"Error updating branch tree: {e}")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for expired instances."""
        logger.info("Started concurrent world state cleanup loop")

        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                # Clean up expired instances
                await self._cleanup_expired_instances()

                # Clean up cache
                await self._cleanup_cache()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)

        logger.info("Stopped concurrent world state cleanup loop")

    async def _cleanup_expired_instances(self) -> None:
        """Clean up expired and inactive instances."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.auto_archive_inactive_days
            )

            # This would need to scan all instances - simplified for now
            logger.debug("Would perform expired instance cleanup here")

        except Exception as e:
            logger.error(f"Error cleaning up expired instances: {e}")

    async def _cleanup_cache(self) -> None:
        """Clean up in-memory caches."""
        try:
            current_time = datetime.utcnow()
            cache_cutoff = current_time - timedelta(minutes=self.cache_ttl_minutes)

            # Clean instance cache
            expired_instances = []
            for instance_id, instance in self.instance_cache.items():
                if instance.last_accessed < cache_cutoff:
                    expired_instances.append(instance_id)

            for instance_id in expired_instances:
                del self.instance_cache[instance_id]

            # Clean multiverse cache
            expired_multiverses = []
            for player_id, multiverse in self.multiverse_cache.items():
                if multiverse.last_updated < cache_cutoff:
                    expired_multiverses.append(player_id)

            for player_id in expired_multiverses:
                del self.multiverse_cache[player_id]

            if expired_instances or expired_multiverses:
                logger.debug(
                    f"Cleaned {len(expired_instances)} instances and {len(expired_multiverses)} multiverses from cache"
                )

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the concurrent world state manager."""
        return {
            **self.metrics,
            "cached_instances": len(self.instance_cache),
            "cached_multiverses": len(self.multiverse_cache),
            "is_running": self.is_running,
            "max_concurrent_instances_per_player": self.max_concurrent_instances_per_player,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the concurrent world state manager."""
        try:
            return {
                "service_running": self.is_running,
                "cached_instances": len(self.instance_cache),
                "cached_multiverses": len(self.multiverse_cache),
                "cleanup_task_running": (
                    self.cleanup_task and not self.cleanup_task.done()
                    if self.cleanup_task
                    else False
                ),
                "session_manager_available": self.session_manager is not None,
                "overall_status": "healthy" if self.is_running else "stopped",
            }

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"overall_status": "error", "error": str(e)}
