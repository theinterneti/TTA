"""
Multi-User Concurrent Testing Framework for TTA Extended Session Testing

Implements asynchronous multi-user access to shared story worlds with conflict
resolution, shared narrative consistency, and load testing capabilities.
Tests the system's ability to handle multiple concurrent users in the same
persistent world state.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .simulated_user_profiles import SimulatedUserProfile

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts between concurrent users."""

    FIRST_WINS = "first_wins"  # First user's action takes precedence
    MAJORITY_VOTE = "majority_vote"  # Most popular choice wins
    WEIGHTED_PRIORITY = "weighted_priority"  # Based on user priority/experience
    NARRATIVE_CONSISTENCY = "narrative_consistency"  # Choose most consistent option
    RANDOM_SELECTION = "random_selection"  # Random choice among conflicts


@dataclass
class SharedWorldState:
    """Represents the state of a shared story world."""

    world_id: str
    scenario_name: str
    current_turn: int = 0
    active_users: set[str] = field(default_factory=set)
    world_state: dict[str, Any] = field(default_factory=dict)
    narrative_history: list[dict[str, Any]] = field(default_factory=list)
    pending_actions: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)

    # Consistency tracking
    consistency_score: float = 10.0
    narrative_coherence: float = 10.0
    user_satisfaction_scores: dict[str, float] = field(default_factory=dict)

    # Performance metrics
    response_times: list[float] = field(default_factory=list)
    concurrent_user_count: list[int] = field(default_factory=list)
    conflict_resolution_times: list[float] = field(default_factory=list)


@dataclass
class UserAction:
    """Represents an action taken by a user in the shared world."""

    user_id: str
    action_id: str
    turn_number: int
    action_type: str
    action_content: str
    timestamp: datetime
    priority: int = 1
    dependencies: list[str] = field(default_factory=list)
    conflicts_with: list[str] = field(default_factory=list)


@dataclass
class ConflictResolution:
    """Represents the resolution of a conflict between user actions."""

    conflict_id: str
    conflicting_actions: list[UserAction]
    resolution_strategy: ConflictResolutionStrategy
    chosen_action: UserAction
    resolution_time: float
    narrative_impact: str
    user_notifications: dict[str, str] = field(default_factory=dict)


class SharedWorldManager:
    """Manages shared story worlds and handles concurrent user access."""

    def __init__(self, max_concurrent_users: int = 10):
        self.worlds: dict[str, SharedWorldState] = {}
        self.max_concurrent_users = max_concurrent_users
        self.conflict_resolver = ConflictResolver()
        self.world_locks: dict[str, asyncio.Lock] = {}
        self.user_sessions: dict[str, dict[str, Any]] = {}

    async def create_shared_world(
        self, scenario_name: str, initial_users: list[str]
    ) -> str:
        """Create a new shared world for concurrent testing."""
        world_id = f"shared_world_{uuid.uuid4().hex[:8]}"

        self.worlds[world_id] = SharedWorldState(
            world_id=world_id,
            scenario_name=scenario_name,
            active_users=set(initial_users),
        )
        self.world_locks[world_id] = asyncio.Lock()

        logger.info(f"Created shared world {world_id} with {len(initial_users)} users")
        return world_id

    async def add_user_to_world(self, world_id: str, user_id: str) -> bool:
        """Add a user to an existing shared world."""
        if world_id not in self.worlds:
            return False

        world = self.worlds[world_id]
        if len(world.active_users) >= self.max_concurrent_users:
            logger.warning(f"World {world_id} at capacity, cannot add user {user_id}")
            return False

        async with self.world_locks[world_id]:
            world.active_users.add(user_id)
            world.user_satisfaction_scores[user_id] = 10.0

        logger.info(f"Added user {user_id} to world {world_id}")
        return True

    async def submit_user_action(
        self, world_id: str, user_id: str, action_content: str
    ) -> str:
        """Submit a user action to the shared world."""
        if world_id not in self.worlds:
            raise ValueError(f"World {world_id} not found")

        world = self.worlds[world_id]
        if user_id not in world.active_users:
            raise ValueError(f"User {user_id} not in world {world_id}")

        action = UserAction(
            user_id=user_id,
            action_id=f"action_{uuid.uuid4().hex[:8]}",
            turn_number=world.current_turn,
            action_type="story_choice",
            action_content=action_content,
            timestamp=datetime.now(),
        )

        async with self.world_locks[world_id]:
            world.pending_actions.append(action)

        logger.info(f"User {user_id} submitted action in world {world_id}")
        return action.action_id

    async def process_turn(self, world_id: str) -> dict[str, Any]:
        """Process a turn in the shared world, resolving conflicts."""
        if world_id not in self.worlds:
            raise ValueError(f"World {world_id} not found")

        world = self.worlds[world_id]
        start_time = time.time()

        async with self.world_locks[world_id]:
            # Detect conflicts
            conflicts = self._detect_conflicts(world.pending_actions)

            # Resolve conflicts
            resolutions = []
            if conflicts:
                for conflict_group in conflicts:
                    resolution = await self.conflict_resolver.resolve_conflict(
                        conflict_group, ConflictResolutionStrategy.NARRATIVE_CONSISTENCY
                    )
                    resolutions.append(resolution)
                    world.conflicts.append(resolution.__dict__)

            # Apply actions
            applied_actions = self._apply_actions(world, resolutions)

            # Update world state
            world.current_turn += 1
            world.last_update = datetime.now()
            world.pending_actions.clear()

            # Track performance
            processing_time = time.time() - start_time
            world.response_times.append(processing_time)
            world.concurrent_user_count.append(len(world.active_users))

            # Update consistency scores
            self._update_consistency_scores(world, applied_actions)

        result = {
            "world_id": world_id,
            "turn_number": world.current_turn,
            "applied_actions": len(applied_actions),
            "conflicts_resolved": len(resolutions),
            "processing_time": processing_time,
            "consistency_score": world.consistency_score,
            "active_users": len(world.active_users),
        }

        logger.info(
            f"Processed turn {world.current_turn} in world {world_id}: "
            f"{len(applied_actions)} actions, {len(resolutions)} conflicts"
        )

        return result

    def _detect_conflicts(self, actions: list[UserAction]) -> list[list[UserAction]]:
        """Detect conflicting actions that cannot coexist."""
        conflicts = []

        # Group actions by type and content similarity
        action_groups = {}
        for action in actions:
            key = f"{action.action_type}_{action.turn_number}"
            if key not in action_groups:
                action_groups[key] = []
            action_groups[key].append(action)

        # Find conflicting groups
        for group in action_groups.values():
            if len(group) > 1:
                # Check for actual conflicts (simplified logic)
                conflicting = []
                for action in group:
                    if any(
                        keyword in action.action_content.lower()
                        for keyword in ["opposite", "different", "instead", "no"]
                    ):
                        conflicting.append(action)

                if len(conflicting) > 1:
                    conflicts.append(conflicting)

        return conflicts

    def _apply_actions(
        self, world: SharedWorldState, resolutions: list[ConflictResolution]
    ) -> list[UserAction]:
        """Apply resolved actions to the world state."""
        applied_actions = []

        # Apply conflict resolutions
        for resolution in resolutions:
            applied_actions.append(resolution.chosen_action)
            world.narrative_history.append(
                {
                    "turn": world.current_turn,
                    "action": resolution.chosen_action.__dict__,
                    "resolution": resolution.__dict__,
                }
            )

        # Apply non-conflicting actions
        resolved_action_ids = {res.chosen_action.action_id for res in resolutions}
        for action in world.pending_actions:
            if action.action_id not in resolved_action_ids:
                applied_actions.append(action)
                world.narrative_history.append(
                    {"turn": world.current_turn, "action": action.__dict__}
                )

        return applied_actions

    def _update_consistency_scores(
        self, world: SharedWorldState, applied_actions: list[UserAction]
    ):
        """Update world consistency scores based on applied actions."""
        # Simplified consistency scoring
        if len(applied_actions) > len(world.active_users):
            world.consistency_score *= 0.95  # Penalty for too many actions

        # Check for narrative coherence
        action_contents = [action.action_content for action in applied_actions]
        if any(
            "break" in content.lower() or "ignore" in content.lower()
            for content in action_contents
        ):
            world.narrative_coherence *= 0.9

        # Update user satisfaction (simplified)
        for user_id in world.active_users:
            user_actions = [a for a in applied_actions if a.user_id == user_id]
            if user_actions:
                world.user_satisfaction_scores[user_id] = min(
                    10.0, world.user_satisfaction_scores.get(user_id, 10.0) + 0.1
                )
            else:
                world.user_satisfaction_scores[user_id] = max(
                    0.0, world.user_satisfaction_scores.get(user_id, 10.0) - 0.2
                )


class ConflictResolver:
    """Handles conflict resolution between concurrent user actions."""

    async def resolve_conflict(
        self,
        conflicting_actions: list[UserAction],
        strategy: ConflictResolutionStrategy,
    ) -> ConflictResolution:
        """Resolve a conflict using the specified strategy."""
        start_time = time.time()

        if strategy == ConflictResolutionStrategy.FIRST_WINS:
            chosen = min(conflicting_actions, key=lambda a: a.timestamp)
        elif strategy == ConflictResolutionStrategy.MAJORITY_VOTE:
            chosen = self._resolve_by_majority(conflicting_actions)
        elif strategy == ConflictResolutionStrategy.WEIGHTED_PRIORITY:
            chosen = max(conflicting_actions, key=lambda a: a.priority)
        elif strategy == ConflictResolutionStrategy.NARRATIVE_CONSISTENCY:
            chosen = self._resolve_by_consistency(conflicting_actions)
        else:  # RANDOM_SELECTION
            chosen = conflicting_actions[0]  # Simplified

        resolution_time = time.time() - start_time

        resolution = ConflictResolution(
            conflict_id=f"conflict_{uuid.uuid4().hex[:8]}",
            conflicting_actions=conflicting_actions,
            resolution_strategy=strategy,
            chosen_action=chosen,
            resolution_time=resolution_time,
            narrative_impact="Maintained story coherence",
        )

        # Generate user notifications
        for action in conflicting_actions:
            if action.action_id == chosen.action_id:
                resolution.user_notifications[action.user_id] = (
                    "Your action was chosen!"
                )
            else:
                resolution.user_notifications[action.user_id] = (
                    "Your action was overridden by group consensus."
                )

        return resolution

    def _resolve_by_majority(self, actions: list[UserAction]) -> UserAction:
        """Resolve by finding the most similar actions (simplified)."""
        # Simplified majority logic - just return first action
        return actions[0]

    def _resolve_by_consistency(self, actions: list[UserAction]) -> UserAction:
        """Choose the action most consistent with narrative."""
        # Simplified consistency check - prefer actions without disruptive keywords
        for action in actions:
            if not any(
                keyword in action.action_content.lower()
                for keyword in ["break", "ignore", "opposite", "destroy"]
            ):
                return action
        return actions[0]


class ConcurrentTestingFramework:
    """Framework for running concurrent multi-user tests."""

    def __init__(self):
        self.world_manager = SharedWorldManager()
        self.test_results = []

    async def run_concurrent_test(
        self,
        scenario: str,
        user_profiles: list[SimulatedUserProfile],
        turns: int = 50,
        max_concurrent: int = 5,
    ) -> dict[str, Any]:
        """Run a concurrent multi-user test."""
        logger.info(
            f"Starting concurrent test with {len(user_profiles)} users for {turns} turns"
        )

        # Create shared world
        user_ids = [f"user_{i}" for i in range(len(user_profiles))]
        world_id = await self.world_manager.create_shared_world(
            scenario, user_ids[:max_concurrent]
        )

        # Add remaining users gradually
        for user_id in user_ids[max_concurrent:]:
            await self.world_manager.add_user_to_world(world_id, user_id)

        results = {
            "scenario": scenario,
            "total_users": len(user_profiles),
            "max_concurrent": max_concurrent,
            "total_turns": turns,
            "turn_results": [],
            "conflicts_resolved": 0,
            "average_response_time": 0.0,
            "final_consistency_score": 0.0,
            "user_satisfaction": {},
        }

        # Run concurrent turns
        for turn in range(turns):
            # Submit actions from active users
            active_users = list(self.world_manager.worlds[world_id].active_users)
            tasks = []

            for i, user_id in enumerate(active_users):
                if i < len(user_profiles):
                    profile = user_profiles[i]
                    action_content = f"User {user_id} takes action in turn {turn}"
                    task = self.world_manager.submit_user_action(
                        world_id, user_id, action_content
                    )
                    tasks.append(task)

            # Wait for all actions to be submitted
            if tasks:
                await asyncio.gather(*tasks)

            # Process the turn
            turn_result = await self.world_manager.process_turn(world_id)
            results["turn_results"].append(turn_result)
            results["conflicts_resolved"] += turn_result["conflicts_resolved"]

        # Calculate final metrics
        world = self.world_manager.worlds[world_id]
        results["average_response_time"] = (
            sum(world.response_times) / len(world.response_times)
            if world.response_times
            else 0
        )
        results["final_consistency_score"] = world.consistency_score
        results["user_satisfaction"] = dict(world.user_satisfaction_scores)

        logger.info(
            f"Concurrent test completed: {results['conflicts_resolved']} conflicts resolved, "
            f"consistency score: {results['final_consistency_score']:.2f}"
        )

        return results
