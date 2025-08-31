"""
Cross-Story Character Persistence Service

This service implements character data persistence across multiple story experiences,
maintaining therapeutic progress and character development throughout the multiverse.
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

from .concurrent_world_state_manager import ConcurrentWorldStateManager

logger = logging.getLogger(__name__)


class CharacterEvolutionType(str, Enum):
    """Types of character evolution across stories."""

    SKILL_DEVELOPMENT = "skill_development"
    PERSONALITY_GROWTH = "personality_growth"
    THERAPEUTIC_PROGRESS = "therapeutic_progress"
    RELATIONSHIP_LEARNING = "relationship_learning"
    EMOTIONAL_MATURITY = "emotional_maturity"
    COPING_STRATEGIES = "coping_strategies"
    SELF_AWARENESS = "self_awareness"
    RESILIENCE_BUILDING = "resilience_building"


class PersistenceScope(str, Enum):
    """Scope of character data persistence."""

    GLOBAL = "global"  # Persists across all stories
    WORLD_SPECIFIC = "world_specific"  # Persists within world type
    BRANCH_SPECIFIC = "branch_specific"  # Persists within story branch
    SESSION_ONLY = "session_only"  # Only for current session


@dataclass
class CharacterSnapshot:
    """Snapshot of character state at a specific point."""

    snapshot_id: str
    character_id: str
    player_id: str
    instance_id: str
    character_data: dict[str, Any]
    therapeutic_progress: dict[str, Any]
    skills_learned: list[str]
    personality_traits: dict[str, Any]
    emotional_state: dict[str, Any]
    relationships: dict[str, Any]
    story_context: dict[str, Any]
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterSnapshot":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class CharacterEvolution:
    """Tracks character evolution across stories."""

    evolution_id: str
    character_id: str
    player_id: str
    evolution_type: CharacterEvolutionType
    from_snapshot_id: str
    to_snapshot_id: str
    changes: dict[str, Any]
    story_context: dict[str, Any]
    therapeutic_significance: dict[str, Any]
    persistence_scope: PersistenceScope
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterEvolution":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["evolution_type"] = CharacterEvolutionType(data["evolution_type"])
        data["persistence_scope"] = PersistenceScope(data["persistence_scope"])
        return cls(**data)


@dataclass
class CrossStoryCharacterProfile:
    """Comprehensive character profile across all stories."""

    profile_id: str
    character_id: str
    player_id: str
    base_character_data: dict[str, Any]
    accumulated_skills: set[str]
    personality_evolution: dict[str, Any]
    therapeutic_journey: dict[str, Any]
    relationship_patterns: dict[str, Any]
    story_experiences: list[str]
    character_snapshots: list[str]
    evolution_history: list[str]
    continuity_markers: dict[str, Any]
    created_at: datetime
    last_updated: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        data["accumulated_skills"] = list(self.accumulated_skills)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrossStoryCharacterProfile":
        """Create from dictionary loaded from storage."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        data["accumulated_skills"] = set(data["accumulated_skills"])
        return cls(**data)


class CrossStoryCharacterPersistence:
    """
    Service for character data persistence across multiple story experiences.

    Maintains therapeutic progress and character development throughout the multiverse,
    ensuring continuity while allowing for story-specific adaptations.
    """

    def __init__(
        self,
        session_manager: SessionIntegrationManager | None = None,
        world_state_manager: ConcurrentWorldStateManager | None = None,
    ):
        """
        Initialize the Cross-Story Character Persistence service.

        Args:
            session_manager: Session integration manager for Redis operations
            world_state_manager: Concurrent world state manager
        """
        self.session_manager = session_manager or SessionIntegrationManager()
        self.world_state_manager = world_state_manager or ConcurrentWorldStateManager()

        # Storage key patterns
        self.character_profile_key_pattern = "cross_story_profile:{character_id}"
        self.character_snapshot_key_pattern = "character_snapshot:{snapshot_id}"
        self.character_evolution_key_pattern = "character_evolution:{evolution_id}"
        self.player_characters_key_pattern = "player_characters:{player_id}"

        # In-memory caches
        self.profile_cache: dict[str, CrossStoryCharacterProfile] = {}
        self.snapshot_cache: dict[str, CharacterSnapshot] = {}

        # Configuration
        self.max_snapshots_per_character = 50
        self.snapshot_retention_days = 90
        self.auto_snapshot_frequency_minutes = 30
        self.enable_therapeutic_continuity = True

        # Persistence rules
        self.persistence_rules = self._build_persistence_rules()
        self.continuity_markers = self._build_continuity_markers()

        # Background tasks
        self.snapshot_task: asyncio.Task | None = None
        self.is_running = False

        # Metrics
        self.metrics = {
            "character_profiles_managed": 0,
            "snapshots_created": 0,
            "evolutions_tracked": 0,
            "therapeutic_continuity_maintained": 0,
            "cross_story_transfers": 0,
            "skill_persistences": 0,
            "personality_evolutions": 0,
        }

        logger.info("CrossStoryCharacterPersistence service initialized")

    async def start(self) -> None:
        """Start the cross-story character persistence service."""
        if self.is_running:
            logger.warning("Cross-story character persistence is already running")
            return

        self.is_running = True

        # Start background snapshot task
        self.snapshot_task = asyncio.create_task(self._auto_snapshot_loop())

        logger.info("Cross-story character persistence started")

    async def stop(self) -> None:
        """Stop the cross-story character persistence service."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel snapshot task
        if self.snapshot_task and not self.snapshot_task.done():
            self.snapshot_task.cancel()
            try:
                await self.snapshot_task
            except asyncio.CancelledError:
                pass

        # Clear caches
        self.profile_cache.clear()
        self.snapshot_cache.clear()

        logger.info("Cross-story character persistence stopped")

    async def create_character_profile(
        self, character_id: str, player_id: str, base_character_data: dict[str, Any]
    ) -> str | None:
        """
        Create a cross-story character profile.

        Args:
            character_id: Character identifier
            player_id: Player identifier
            base_character_data: Base character data

        Returns:
            Profile ID if successful, None otherwise
        """
        try:
            # Generate profile ID
            profile_id = f"csp_{character_id}_{player_id}_{uuid.uuid4().hex[:8]}"

            # Create character profile
            profile = CrossStoryCharacterProfile(
                profile_id=profile_id,
                character_id=character_id,
                player_id=player_id,
                base_character_data=base_character_data,
                accumulated_skills=set(),
                personality_evolution={},
                therapeutic_journey={},
                relationship_patterns={},
                story_experiences=[],
                character_snapshots=[],
                evolution_history=[],
                continuity_markers={},
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
            )

            # Save profile
            await self._save_character_profile(profile)

            # Update player characters list
            await self._update_player_characters_list(player_id, character_id, "add")

            # Update metrics
            self.metrics["character_profiles_managed"] += 1

            logger.info(f"Created cross-story character profile {profile_id}")
            return profile_id

        except Exception as e:
            logger.error(f"Error creating character profile: {e}")
            return None

    async def create_character_snapshot(
        self,
        character_id: str,
        player_id: str,
        instance_id: str,
        character_data: dict[str, Any],
        story_context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Create a snapshot of character state.

        Args:
            character_id: Character identifier
            player_id: Player identifier
            instance_id: World instance identifier
            character_data: Current character data
            story_context: Optional story context

        Returns:
            Snapshot ID if successful, None otherwise
        """
        try:
            # Generate snapshot ID
            snapshot_id = f"cs_{character_id}_{datetime.utcnow().timestamp()}"

            # Extract character components
            therapeutic_progress = character_data.get("therapeutic_progress", {})
            skills_learned = character_data.get("skills_learned", [])
            personality_traits = character_data.get("personality_traits", {})
            emotional_state = character_data.get("emotional_state", {})
            relationships = character_data.get("relationships", {})

            # Create snapshot
            snapshot = CharacterSnapshot(
                snapshot_id=snapshot_id,
                character_id=character_id,
                player_id=player_id,
                instance_id=instance_id,
                character_data=character_data,
                therapeutic_progress=therapeutic_progress,
                skills_learned=skills_learned,
                personality_traits=personality_traits,
                emotional_state=emotional_state,
                relationships=relationships,
                story_context=story_context or {},
                created_at=datetime.utcnow(),
            )

            # Save snapshot
            await self._save_character_snapshot(snapshot)

            # Update character profile
            await self._update_profile_with_snapshot(character_id, snapshot_id)

            # Update metrics
            self.metrics["snapshots_created"] += 1

            logger.debug(f"Created character snapshot {snapshot_id}")
            return snapshot_id

        except Exception as e:
            logger.error(f"Error creating character snapshot: {e}")
            return None

    async def track_character_evolution(
        self,
        character_id: str,
        player_id: str,
        evolution_type: CharacterEvolutionType,
        from_snapshot_id: str,
        to_snapshot_id: str,
        changes: dict[str, Any],
        story_context: dict[str, Any],
        persistence_scope: PersistenceScope = PersistenceScope.GLOBAL,
    ) -> str | None:
        """
        Track character evolution between snapshots.

        Args:
            character_id: Character identifier
            player_id: Player identifier
            evolution_type: Type of evolution
            from_snapshot_id: Starting snapshot
            to_snapshot_id: Ending snapshot
            changes: Changes that occurred
            story_context: Story context for the evolution
            persistence_scope: Scope of persistence

        Returns:
            Evolution ID if successful, None otherwise
        """
        try:
            # Generate evolution ID
            evolution_id = (
                f"ce_{character_id}_{evolution_type.value}_{uuid.uuid4().hex[:8]}"
            )

            # Analyze therapeutic significance
            therapeutic_significance = await self._analyze_therapeutic_significance(
                evolution_type, changes, story_context
            )

            # Create evolution record
            evolution = CharacterEvolution(
                evolution_id=evolution_id,
                character_id=character_id,
                player_id=player_id,
                evolution_type=evolution_type,
                from_snapshot_id=from_snapshot_id,
                to_snapshot_id=to_snapshot_id,
                changes=changes,
                story_context=story_context,
                therapeutic_significance=therapeutic_significance,
                persistence_scope=persistence_scope,
                created_at=datetime.utcnow(),
            )

            # Save evolution
            await self._save_character_evolution(evolution)

            # Update character profile
            await self._update_profile_with_evolution(character_id, evolution)

            # Update metrics
            self.metrics["evolutions_tracked"] += 1
            self._update_evolution_type_metrics(evolution_type)

            logger.info(f"Tracked character evolution {evolution_id}")
            return evolution_id

        except Exception as e:
            logger.error(f"Error tracking character evolution: {e}")
            return None

    async def get_character_profile(
        self, character_id: str
    ) -> CrossStoryCharacterProfile | None:
        """
        Get cross-story character profile.

        Args:
            character_id: Character identifier

        Returns:
            Character profile if found, None otherwise
        """
        try:
            # Check cache first
            if character_id in self.profile_cache:
                return self.profile_cache[character_id]

            # Load from storage
            profile_key = self.character_profile_key_pattern.format(
                character_id=character_id
            )
            profile_data = await self.session_manager.get_session_data(profile_key)

            if not profile_data:
                return None

            if isinstance(profile_data, str):
                profile_data = json.loads(profile_data)

            profile = CrossStoryCharacterProfile.from_dict(profile_data)

            # Cache the profile
            self.profile_cache[character_id] = profile

            return profile

        except Exception as e:
            logger.error(f"Error getting character profile: {e}")
            return None

    async def transfer_character_to_story(
        self,
        character_id: str,
        target_instance_id: str,
        transfer_scope: PersistenceScope = PersistenceScope.GLOBAL,
    ) -> dict[str, Any] | None:
        """
        Transfer character data to a new story instance.

        Args:
            character_id: Character identifier
            target_instance_id: Target world instance
            transfer_scope: Scope of data to transfer

        Returns:
            Transferred character data if successful, None otherwise
        """
        try:
            # Get character profile
            profile = await self.get_character_profile(character_id)
            if not profile:
                logger.error(f"Character profile {character_id} not found")
                return None

            # Build transferred character data based on scope
            transferred_data = await self._build_transferred_character_data(
                profile, transfer_scope
            )

            # Apply continuity markers
            transferred_data = await self._apply_continuity_markers(
                transferred_data, profile.continuity_markers
            )

            # Create snapshot for the transfer
            snapshot_id = await self.create_character_snapshot(
                character_id=character_id,
                player_id=profile.player_id,
                instance_id=target_instance_id,
                character_data=transferred_data,
                story_context={
                    "transfer_type": "cross_story",
                    "scope": transfer_scope.value,
                },
            )

            # Update metrics
            self.metrics["cross_story_transfers"] += 1

            logger.info(
                f"Transferred character {character_id} to instance {target_instance_id}"
            )
            return transferred_data

        except Exception as e:
            logger.error(f"Error transferring character to story: {e}")
            return None

    async def get_character_therapeutic_journey(
        self, character_id: str
    ) -> dict[str, Any]:
        """
        Get therapeutic journey across all stories for a character.

        Args:
            character_id: Character identifier

        Returns:
            Therapeutic journey data
        """
        try:
            profile = await self.get_character_profile(character_id)
            if not profile:
                return {}

            return {
                "character_id": character_id,
                "therapeutic_journey": profile.therapeutic_journey,
                "accumulated_skills": list(profile.accumulated_skills),
                "personality_evolution": profile.personality_evolution,
                "story_experiences": profile.story_experiences,
                "continuity_markers": profile.continuity_markers,
                "journey_timeline": await self._build_therapeutic_timeline(
                    character_id
                ),
                "progress_summary": await self._summarize_therapeutic_progress(profile),
            }

        except Exception as e:
            logger.error(f"Error getting therapeutic journey: {e}")
            return {}

    # Private helper methods

    async def _save_character_profile(
        self, profile: CrossStoryCharacterProfile
    ) -> None:
        """Save character profile to storage."""
        try:
            profile_key = self.character_profile_key_pattern.format(
                character_id=profile.character_id
            )
            profile_data = json.dumps(profile.to_dict(), default=str)

            # Save with long expiry
            expiry_seconds = 365 * 24 * 3600  # 1 year
            await self.session_manager.set_session_data(
                profile_key, profile_data, expiry_seconds
            )

            # Update cache
            self.profile_cache[profile.character_id] = profile

        except Exception as e:
            logger.error(f"Error saving character profile: {e}")
            raise

    async def _save_character_snapshot(self, snapshot: CharacterSnapshot) -> None:
        """Save character snapshot to storage."""
        try:
            snapshot_key = self.character_snapshot_key_pattern.format(
                snapshot_id=snapshot.snapshot_id
            )
            snapshot_data = json.dumps(snapshot.to_dict(), default=str)

            # Save with retention period
            expiry_seconds = self.snapshot_retention_days * 24 * 3600
            await self.session_manager.set_session_data(
                snapshot_key, snapshot_data, expiry_seconds
            )

            # Update cache
            self.snapshot_cache[snapshot.snapshot_id] = snapshot

        except Exception as e:
            logger.error(f"Error saving character snapshot: {e}")
            raise

    async def _save_character_evolution(self, evolution: CharacterEvolution) -> None:
        """Save character evolution to storage."""
        try:
            evolution_key = self.character_evolution_key_pattern.format(
                evolution_id=evolution.evolution_id
            )
            evolution_data = json.dumps(evolution.to_dict(), default=str)

            # Save with long expiry
            expiry_seconds = 365 * 24 * 3600  # 1 year
            await self.session_manager.set_session_data(
                evolution_key, evolution_data, expiry_seconds
            )

        except Exception as e:
            logger.error(f"Error saving character evolution: {e}")
            raise

    async def _update_profile_with_snapshot(
        self, character_id: str, snapshot_id: str
    ) -> None:
        """Update character profile with new snapshot."""
        try:
            profile = await self.get_character_profile(character_id)
            if not profile:
                return

            # Add snapshot to profile
            profile.character_snapshots.append(snapshot_id)

            # Limit number of snapshots
            if len(profile.character_snapshots) > self.max_snapshots_per_character:
                # Remove oldest snapshots
                profile.character_snapshots = profile.character_snapshots[
                    -self.max_snapshots_per_character :
                ]

            profile.last_updated = datetime.utcnow()
            await self._save_character_profile(profile)

        except Exception as e:
            logger.error(f"Error updating profile with snapshot: {e}")

    async def _update_profile_with_evolution(
        self, character_id: str, evolution: CharacterEvolution
    ) -> None:
        """Update character profile with evolution data."""
        try:
            profile = await self.get_character_profile(character_id)
            if not profile:
                return

            # Add evolution to history
            profile.evolution_history.append(evolution.evolution_id)

            # Update accumulated data based on evolution type
            if evolution.evolution_type == CharacterEvolutionType.SKILL_DEVELOPMENT:
                new_skills = evolution.changes.get("skills_gained", [])
                profile.accumulated_skills.update(new_skills)
                self.metrics["skill_persistences"] += len(new_skills)

            elif evolution.evolution_type == CharacterEvolutionType.PERSONALITY_GROWTH:
                personality_changes = evolution.changes.get("personality_changes", {})
                profile.personality_evolution.update(personality_changes)
                self.metrics["personality_evolutions"] += 1

            elif (
                evolution.evolution_type == CharacterEvolutionType.THERAPEUTIC_PROGRESS
            ):
                therapeutic_progress = evolution.changes.get("therapeutic_progress", {})
                profile.therapeutic_journey.update(therapeutic_progress)
                self.metrics["therapeutic_continuity_maintained"] += 1

            # Update continuity markers if this evolution has global scope
            if evolution.persistence_scope == PersistenceScope.GLOBAL:
                continuity_updates = evolution.changes.get("continuity_markers", {})
                profile.continuity_markers.update(continuity_updates)

            profile.last_updated = datetime.utcnow()
            await self._save_character_profile(profile)

        except Exception as e:
            logger.error(f"Error updating profile with evolution: {e}")

    async def _update_player_characters_list(
        self, player_id: str, character_id: str, action: str
    ) -> None:
        """Update player characters list."""
        try:
            characters_key = self.player_characters_key_pattern.format(
                player_id=player_id
            )
            characters_data = await self.session_manager.get_session_data(
                characters_key
            )

            if characters_data:
                if isinstance(characters_data, str):
                    characters_list = json.loads(characters_data)
                else:
                    characters_list = characters_data
            else:
                characters_list = []

            if action == "add" and character_id not in characters_list:
                characters_list.append(character_id)
            elif action == "remove" and character_id in characters_list:
                characters_list.remove(character_id)

            # Save updated list
            expiry_seconds = 365 * 24 * 3600  # 1 year
            await self.session_manager.set_session_data(
                characters_key, json.dumps(characters_list), expiry_seconds
            )

        except Exception as e:
            logger.error(f"Error updating player characters list: {e}")

    async def _analyze_therapeutic_significance(
        self,
        evolution_type: CharacterEvolutionType,
        changes: dict[str, Any],
        story_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze therapeutic significance of character evolution."""
        try:
            significance = {
                "therapeutic_value": "medium",
                "skill_development": [],
                "emotional_growth": [],
                "behavioral_changes": [],
                "therapeutic_goals_advanced": [],
            }

            # Analyze based on evolution type
            if evolution_type == CharacterEvolutionType.THERAPEUTIC_PROGRESS:
                significance["therapeutic_value"] = "high"
                significance["therapeutic_goals_advanced"] = changes.get(
                    "goals_advanced", []
                )

            elif evolution_type == CharacterEvolutionType.SKILL_DEVELOPMENT:
                significance["skill_development"] = changes.get("skills_gained", [])
                if len(significance["skill_development"]) > 2:
                    significance["therapeutic_value"] = "high"

            elif evolution_type == CharacterEvolutionType.EMOTIONAL_MATURITY:
                significance["emotional_growth"] = changes.get(
                    "emotional_improvements", []
                )
                significance["therapeutic_value"] = "high"

            # Add story context significance
            if story_context.get("therapeutic_focus"):
                significance["story_therapeutic_focus"] = story_context[
                    "therapeutic_focus"
                ]

            return significance

        except Exception as e:
            logger.error(f"Error analyzing therapeutic significance: {e}")
            return {"therapeutic_value": "low"}

    async def _build_transferred_character_data(
        self, profile: CrossStoryCharacterProfile, transfer_scope: PersistenceScope
    ) -> dict[str, Any]:
        """Build character data for transfer based on scope."""
        try:
            base_data = profile.base_character_data.copy()

            if transfer_scope == PersistenceScope.GLOBAL:
                # Transfer everything
                base_data.update(
                    {
                        "accumulated_skills": list(profile.accumulated_skills),
                        "personality_evolution": profile.personality_evolution,
                        "therapeutic_journey": profile.therapeutic_journey,
                        "relationship_patterns": profile.relationship_patterns,
                        "continuity_markers": profile.continuity_markers,
                    }
                )

            elif transfer_scope == PersistenceScope.WORLD_SPECIFIC:
                # Transfer world-relevant data
                base_data.update(
                    {
                        "accumulated_skills": list(profile.accumulated_skills),
                        "therapeutic_journey": profile.therapeutic_journey,
                    }
                )

            elif transfer_scope == PersistenceScope.BRANCH_SPECIFIC:
                # Transfer only therapeutic progress
                base_data.update({"therapeutic_journey": profile.therapeutic_journey})

            # SESSION_ONLY transfers only base data (no additions)

            return base_data

        except Exception as e:
            logger.error(f"Error building transferred character data: {e}")
            return profile.base_character_data.copy()

    async def _apply_continuity_markers(
        self, character_data: dict[str, Any], continuity_markers: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply continuity markers to character data."""
        try:
            # Apply markers that ensure continuity across stories
            for marker_type, marker_data in continuity_markers.items():
                if marker_type == "persistent_traits":
                    character_data.setdefault("personality_traits", {}).update(
                        marker_data
                    )
                elif marker_type == "learned_lessons":
                    character_data.setdefault("learned_lessons", []).extend(marker_data)
                elif marker_type == "therapeutic_insights":
                    character_data.setdefault("therapeutic_insights", []).extend(
                        marker_data
                    )

            return character_data

        except Exception as e:
            logger.error(f"Error applying continuity markers: {e}")
            return character_data

    async def _build_therapeutic_timeline(
        self, character_id: str
    ) -> list[dict[str, Any]]:
        """Build therapeutic timeline for a character."""
        try:
            profile = await self.get_character_profile(character_id)
            if not profile:
                return []

            timeline = []

            # Add evolution events to timeline
            for evolution_id in profile.evolution_history:
                evolution_key = self.character_evolution_key_pattern.format(
                    evolution_id=evolution_id
                )
                evolution_data = await self.session_manager.get_session_data(
                    evolution_key
                )

                if evolution_data:
                    if isinstance(evolution_data, str):
                        evolution_data = json.loads(evolution_data)

                    timeline.append(
                        {
                            "type": "evolution",
                            "evolution_type": evolution_data.get("evolution_type", ""),
                            "therapeutic_significance": evolution_data.get(
                                "therapeutic_significance", {}
                            ),
                            "created_at": evolution_data.get("created_at", ""),
                            "story_context": evolution_data.get("story_context", {}),
                        }
                    )

            # Sort by creation time
            timeline.sort(key=lambda x: x.get("created_at", ""))

            return timeline

        except Exception as e:
            logger.error(f"Error building therapeutic timeline: {e}")
            return []

    async def _summarize_therapeutic_progress(
        self, profile: CrossStoryCharacterProfile
    ) -> dict[str, Any]:
        """Summarize therapeutic progress for a character."""
        try:
            return {
                "total_skills_learned": len(profile.accumulated_skills),
                "personality_growth_areas": len(profile.personality_evolution),
                "therapeutic_milestones": len(profile.therapeutic_journey),
                "story_experiences_count": len(profile.story_experiences),
                "evolution_events_count": len(profile.evolution_history),
                "continuity_markers_count": len(profile.continuity_markers),
                "journey_duration_days": (
                    profile.last_updated - profile.created_at
                ).days,
                "most_recent_update": profile.last_updated.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error summarizing therapeutic progress: {e}")
            return {}

    async def _auto_snapshot_loop(self) -> None:
        """Background loop for automatic character snapshots."""
        logger.info("Started auto-snapshot loop")

        while self.is_running:
            try:
                await asyncio.sleep(self.auto_snapshot_frequency_minutes * 60)

                # This would implement automatic snapshot creation
                # for active characters based on activity
                logger.debug("Would perform auto-snapshot here")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-snapshot loop: {e}")
                await asyncio.sleep(60)

        logger.info("Stopped auto-snapshot loop")

    def _update_evolution_type_metrics(
        self, evolution_type: CharacterEvolutionType
    ) -> None:
        """Update metrics for specific evolution types."""
        if evolution_type == CharacterEvolutionType.SKILL_DEVELOPMENT:
            self.metrics["skill_persistences"] += 1
        elif evolution_type == CharacterEvolutionType.PERSONALITY_GROWTH:
            self.metrics["personality_evolutions"] += 1
        elif evolution_type == CharacterEvolutionType.THERAPEUTIC_PROGRESS:
            self.metrics["therapeutic_continuity_maintained"] += 1

    def _build_persistence_rules(self) -> dict[str, Any]:
        """Build persistence rules for character data."""
        return {
            "skills": {
                "scope": PersistenceScope.GLOBAL,
                "decay_rate": 0.0,  # Skills don't decay
                "transfer_priority": "high",
            },
            "personality_traits": {
                "scope": PersistenceScope.GLOBAL,
                "decay_rate": 0.1,  # Slight decay over time
                "transfer_priority": "high",
            },
            "therapeutic_progress": {
                "scope": PersistenceScope.GLOBAL,
                "decay_rate": 0.0,  # Progress doesn't decay
                "transfer_priority": "critical",
            },
            "relationships": {
                "scope": PersistenceScope.WORLD_SPECIFIC,
                "decay_rate": 0.3,  # Relationships can fade
                "transfer_priority": "medium",
            },
            "memories": {
                "scope": PersistenceScope.BRANCH_SPECIFIC,
                "decay_rate": 0.5,  # Memories can fade
                "transfer_priority": "low",
            },
            "emotional_state": {
                "scope": PersistenceScope.SESSION_ONLY,
                "decay_rate": 0.8,  # Emotions are temporary
                "transfer_priority": "low",
            },
        }

    def _build_continuity_markers(self) -> dict[str, Any]:
        """Build continuity markers for cross-story consistency."""
        return {
            "core_personality": {
                "traits": ["empathy", "resilience", "curiosity"],
                "stability": "high",
                "evolution_rate": "slow",
            },
            "therapeutic_insights": {
                "categories": [
                    "self_awareness",
                    "coping_strategies",
                    "relationship_skills",
                ],
                "persistence": "permanent",
                "transferability": "high",
            },
            "learned_skills": {
                "categories": [
                    "communication",
                    "emotional_regulation",
                    "problem_solving",
                ],
                "retention": "high",
                "application": "cross_context",
            },
            "growth_patterns": {
                "learning_style": "adaptive",
                "challenge_response": "resilient",
                "support_seeking": "proactive",
            },
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the cross-story character persistence service."""
        return {
            **self.metrics,
            "cached_profiles": len(self.profile_cache),
            "cached_snapshots": len(self.snapshot_cache),
            "is_running": self.is_running,
            "max_snapshots_per_character": self.max_snapshots_per_character,
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the cross-story character persistence service."""
        try:
            return {
                "service_running": self.is_running,
                "cached_profiles": len(self.profile_cache),
                "cached_snapshots": len(self.snapshot_cache),
                "auto_snapshot_task_running": (
                    self.snapshot_task and not self.snapshot_task.done()
                    if self.snapshot_task
                    else False
                ),
                "session_manager_available": self.session_manager is not None,
                "world_state_manager_available": self.world_state_manager is not None,
                "overall_status": "healthy" if self.is_running else "stopped",
            }

        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"overall_status": "error", "error": str(e)}

    async def cleanup_expired_snapshots(self) -> int:
        """Clean up expired character snapshots."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.snapshot_retention_days
            )

            # This would implement actual cleanup logic
            logger.debug("Would perform snapshot cleanup here")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired snapshots: {e}")
            return 0
