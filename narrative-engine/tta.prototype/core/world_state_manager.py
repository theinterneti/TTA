"""
World State Manager for TTA Living Worlds

This module implements the WorldStateManager class that serves as the central coordinator
for all world systems. It manages world state persistence, coordinates between timeline,
character, and location systems, handles world evolution triggers, and maintains world
consistency and validation.

Classes:
    WorldStateManager: Central coordinator for all world state changes and persistence
    WorldConfig: Configuration class for world initialization
    EvolutionResult: Result class for world evolution operations
    ValidationResult: Result class for world consistency validation
    WorldSummary: Summary class for world state information
"""

import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Add models path for data models access
models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from data_models import EmotionalState
    from living_worlds_models import (
        EntityType,
        EventType,
        TimelineEvent,
        ValidationError,
        WorldState,
        WorldStateFlag,
    )
except ImportError:
    # Fallback for when running as part of package
    from ..models.data_models import EmotionalState
    from ..models.living_worlds_models import (
        EntityType,
        EventType,
        TimelineEvent,
        ValidationError,
        WorldState,
        WorldStateFlag,
    )

# Import existing systems
try:
    from character_development_system import CharacterDevelopmentSystem
    from content_safety_system import (
        ContentSafetySystem,
        ContentType,
        create_safety_system,
    )
    from timeline_engine import TimelineEngine
except ImportError:
    from .character_development_system import CharacterDevelopmentSystem
    from .content_safety_system import (
        ContentType,
        create_safety_system,
    )
    from .timeline_engine import TimelineEngine

# Import persistence layer
try:
    from database.living_worlds_cache import LivingWorldsCache
    from database.living_worlds_persistence import LivingWorldsPersistence
    from database.redis_cache import RedisCache
except ImportError:
    try:
        from ..database.living_worlds_cache import LivingWorldsCache
        from ..database.living_worlds_persistence import LivingWorldsPersistence
        from ..database.redis_cache import RedisCache
    except ImportError:
        try:
            # Try mock cache
            from database.redis_cache_mock import RedisCache

            # Mock persistence class
            class LivingWorldsPersistence:
                def __init__(self):
                    pass

                def connect(self):
                    return True

                def save_world_state(self, world_state):
                    return True

                def load_world_state(self, world_id):
                    return None

                def update_world_state(self, world_id, updates):
                    return True

        except ImportError:
            # Final fallback - create simple mock classes
            class LivingWorldsPersistence:
                def __init__(self):
                    pass

                def connect(self):
                    return True

                def save_world_state(self, world_state):
                    return True

                def load_world_state(self, world_id):
                    return None

                def update_world_state(self, world_id, updates):
                    return True

            class RedisCache:
                def __init__(self):
                    self._cache = {}

                def get(self, key):
                    return self._cache.get(key)

                def set(self, key, value, ttl=None):
                    self._cache[key] = value


class WorldAdminManager:
    """Administrative controls for world parameters and cache operations."""

    def __init__(self, wsm: "WorldStateManager"):
        self.wsm = wsm

    def set_world_flags(self, world_id: str, updates: dict[str, Any]) -> bool:
        """Set multiple world flags with minimal validation and persist changes."""
        try:
            world_state = self.wsm.get_world_state(world_id)
            if not world_state:
                return False
            # Basic validation: keys must be str
            for k in updates.keys():
                if not isinstance(k, str):
                    raise ValidationError("Flag names must be strings")
            # Apply and persist
            for k, v in updates.items():
                world_state.set_flag(k, v)
            self.wsm._save_world_state(world_state)
            # Invalidate relevant caches
            if self.wsm.lw_cache:
                self.wsm.lw_cache.invalidate_flags(world_id)
                self.wsm.lw_cache.increment_version(world_id)
            return True
        except Exception as e:
            logger.error(f"Admin set_world_flags failed for {world_id}: {e}")
            return False

    def pause_evolution(self, world_id: str, reason: str | None = None) -> bool:
        return self.set_world_flags(
            world_id,
            {"evolution_paused": True, "evolution_pause_reason": reason or "admin"},
        )

    def resume_evolution(self, world_id: str) -> bool:
        return self.set_world_flags(
            world_id, {"evolution_paused": False, "evolution_pause_reason": None}
        )

    def invalidate_caches(self, world_id: str, entity_id: str | None = None) -> None:
        try:
            if self.wsm.lw_cache:
                if entity_id:
                    self.wsm.lw_cache.invalidate_recent_timeline(world_id, entity_id)
                    # History invalidation: best-effort common variants
                    for etype in ("character", "location", "object"):
                        self.wsm.lw_cache.invalidate_history(world_id, etype, entity_id)
                else:
                    self.wsm.lw_cache.invalidate_world_state(world_id)
                    self.wsm.lw_cache.invalidate_flags(world_id)
            # Also clear legacy cache entries for world_state
            self.wsm.cache.delete(f"world_state:{world_id}")
        except Exception:
            logger.debug("invalidate_caches failed", exc_info=True)

    def trigger_evolution_tick(self, world_id: str) -> bool:
        """Stub: in future, invoke scheduler to evolve the world immediately."""
        try:
            ws = self.wsm.get_world_state(world_id)
            return ws is not None
        except Exception:
            return False


logger = logging.getLogger(__name__)


# Import player choice impact system
try:
    from narrative_branching import ChoiceOption, NarrativeBranchingChoice
    from player_choice_impact_system import PlayerChoiceImpactSystem
except ImportError:
    from .narrative_branching import ChoiceOption, NarrativeBranchingChoice
    from .player_choice_impact_system import PlayerChoiceImpactSystem

# Import error handling system
try:
    from living_worlds_error_handler import (
        create_error_handler,
    )
except ImportError:
    from .living_worlds_error_handler import (
        create_error_handler,
    )


@dataclass
class WorldConfig:
    """Configuration for world initialization."""

    world_name: str
    initial_characters: list[dict[str, Any]] = field(default_factory=list)
    initial_locations: list[dict[str, Any]] = field(default_factory=list)
    initial_objects: list[dict[str, Any]] = field(default_factory=list)

    evolution_speed: float = 1.0  # Multiplier for evolution rate
    content_boundaries: dict[str, Any] = field(default_factory=dict)
    therapeutic_focus: list[str] = field(default_factory=list)
    auto_evolution: bool = True
    max_timeline_events: int = 1000

    def validate(self) -> bool:
        """Validate world configuration."""
        if not self.world_name.strip():
            raise ValidationError("World name cannot be empty")
        if self.evolution_speed <= 0:
            raise ValidationError("Evolution speed must be positive")
        if self.max_timeline_events <= 0:
            raise ValidationError("Max timeline events must be positive")
        return True


@dataclass
class EvolutionResult:
    """Result of world evolution operation."""

    success: bool
    events_generated: int = 0
    characters_evolved: int = 0
    locations_changed: int = 0
    objects_modified: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)


@dataclass
class ValidationResult:
    """Result of world consistency validation."""

    is_valid: bool
    timeline_issues: list[str] = field(default_factory=list)
    character_issues: list[str] = field(default_factory=list)
    location_issues: list[str] = field(default_factory=list)
    relationship_issues: list[str] = field(default_factory=list)
    data_integrity_issues: list[str] = field(default_factory=list)

    def add_timeline_issue(self, issue: str) -> None:
        """Add a timeline consistency issue."""
        self.timeline_issues.append(issue)
        self.is_valid = False

    def add_character_issue(self, issue: str) -> None:
        """Add a character consistency issue."""
        self.character_issues.append(issue)
        self.is_valid = False

    def add_location_issue(self, issue: str) -> None:
        """Add a location consistency issue."""
        self.location_issues.append(issue)
        self.is_valid = False

    def add_relationship_issue(self, issue: str) -> None:
        """Add a relationship consistency issue."""
        self.relationship_issues.append(issue)
        self.is_valid = False

    def add_data_integrity_issue(self, issue: str) -> None:
        """Add a data integrity issue."""
        self.data_integrity_issues.append(issue)
        self.is_valid = False


@dataclass
class WorldSummary:
    """Summary of world state information."""

    world_id: str
    world_name: str
    current_time: datetime
    character_count: int
    location_count: int
    object_count: int
    total_timeline_events: int
    last_evolution: datetime
    player_last_visit: datetime | None
    world_status: WorldStateFlag
    pending_evolution_tasks: int
    world_flags: dict[str, Any] = field(default_factory=dict)


class WorldStateManager:
    """
    Central coordinator for all world state changes and persistence.

    This class manages world state persistence in Neo4j and Redis, coordinates
    between timeline, character, and location systems, handles world evolution
    triggers and scheduling, and maintains world consistency and validation.
    """

    def __init__(
        self,
        persistence: LivingWorldsPersistence | None = None,
        cache: RedisCache | None = None,
    ):
        """
        Initialize the World State Manager.

        Args:
            persistence: Living worlds persistence layer
            cache: Redis cache for performance optimization
        """
        self.persistence = persistence or LivingWorldsPersistence()
        self.cache = cache or RedisCache()
        # Ensure persistence and WSM share the same cache instance
        try:
            if hasattr(self.persistence, "cache") and self.cache is not None:
                self.persistence.cache = self.cache
        except Exception:
            logger.debug(
                "Failed to align persistence cache with WSM cache", exc_info=True
            )
        # High-level living worlds cache facade (wraps RedisCache)
        # Admin manager (scaffold)
        self.admin = WorldAdminManager(self)

        try:
            self.lw_cache = LivingWorldsCache(self.cache)
        except Exception:
            self.lw_cache = None

        # Initialize subsystems
        # Simple logging of LW cache metrics for observability
        def log_cache_metrics(context: str = ""):
            try:
                if not self.lw_cache:
                    return
                m = self.lw_cache.metrics
                logger.info(
                    f"LWCache[{context}] hits ws={m['world_state_hits']} flags={m['flags_hits']} recent={m['recent_hits']} | misses ws={m['world_state_misses']} flags={m['flags_misses']} recent={m['recent_misses']} | invalidations={m['invalidations']}"
                )
            except Exception:
                logger.debug("Failed to log LW cache metrics", exc_info=True)

        self.log_cache_metrics = log_cache_metrics

        self.timeline_engine = TimelineEngine()
        # Optional in-memory map to assist cache invalidation without DB lookups
        self._entity_world_map: dict[str, str] = {}

        # Combined hook: inject world_id into event metadata and invalidate cache
        def _on_event_added(entity_id, event):
            try:
                # Ensure event carries world_id in metadata
                wid = None
                if hasattr(event, "metadata"):
                    md = event.metadata or {}
                    wid = md.get("world_id") or self._entity_world_map.get(entity_id)
                    if wid:
                        md["world_id"] = wid
                        event.metadata = md
                else:
                    wid = self._entity_world_map.get(entity_id)
                # Invalidate recent cache if configured
                if self.lw_cache and wid:
                    self.lw_cache.invalidate_recent_timeline(wid, entity_id)
            except Exception:
                # Also invalidate history for affected entity if we can resolve type
                try:
                    if self.lw_cache and wid:
                        etype = None
                        md = getattr(event, "metadata", {}) or {}
                        etype = md.get("entity_type") or md.get("etype")
                        if not etype:
                            ws = self._active_worlds.get(wid)
                            if ws:
                                if entity_id in ws.active_characters:
                                    etype = "character"
                                elif entity_id in ws.active_locations:
                                    etype = "location"
                                elif entity_id in ws.active_objects:
                                    etype = "object"
                        if etype in ("character", "location", "object"):
                            self.lw_cache.invalidate_history(wid, etype, entity_id)
                except Exception:
                    logger.debug(
                        "WSM on_event_added history invalidation failed", exc_info=True
                    )

                logger.debug("WSM on_event_added hook failed", exc_info=True)

        self.timeline_engine.on_event_added = _on_event_added
        self.character_system = CharacterDevelopmentSystem()

        # Set up content validation hook for timeline engine
        def _content_validation_hook(event, entity_id):
            # Try to determine world_id from entity mapping
            world_id = self._entity_world_map.get(entity_id)
            # Try to get player_id from event metadata if available
            player_id = None
            if hasattr(event, "metadata") and event.metadata:
                player_id = event.metadata.get("player_id")

            return self._validate_and_filter_event(event, player_id, world_id)

        self.timeline_engine.content_validation_hook = _content_validation_hook

        # Initialize content safety system
        try:
            self.content_safety = create_safety_system(
                therapeutic_focus=True, trauma_sensitivity=3
            )
            logger.info("Content safety system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize content safety system: {e}")

            # Create a mock safety system that always returns safe
            class MockContentSafetySystem:
                def validate_timeline_event(self, event, player_id=None, world_id=None):
                    from content_safety_system import ContentValidationResult

                    return ContentValidationResult()

                def process_content_safely(
                    self, content, content_type, player_id=None, world_id=None
                ):
                    from content_safety_system import ContentValidationResult

                    return content, ContentValidationResult()

            self.content_safety = MockContentSafetySystem()

        # Active worlds cache
        self._active_worlds: dict[str, WorldState] = {}

        # Player comfort monitoring
        self._player_comfort_profiles: dict[str, Any] = {}

        # Initialize error handling system
        try:
            self.error_handler = create_error_handler(self)
            logger.info("Error handling system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize error handling system: {e}")
            self.error_handler = None

    def _validate_and_filter_event(
        self, event: TimelineEvent, player_id: str = None, world_id: str = None
    ) -> tuple[TimelineEvent, bool]:
        """
        Validate and filter a timeline event for content safety.

        Args:
            event: Timeline event to validate
            player_id: Optional player identifier for personalized validation
            world_id: Optional world identifier for context

        Returns:
            Tuple[TimelineEvent, bool]: (filtered_event, is_safe)
        """
        try:
            # Validate the event
            validation_result = self.content_safety.validate_timeline_event(
                event, player_id, world_id
            )

            # If content is unsafe, filter it
            if not validation_result.is_safe:
                filtered_description, _ = self.content_safety.process_content_safely(
                    event.description, ContentType.TIMELINE_EVENT, player_id, world_id
                )

                # Create a new event with filtered content
                filtered_event = TimelineEvent(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    title=event.title,
                    description=filtered_description,
                    participants=event.participants,
                    location_id=event.location_id,
                    timestamp=event.timestamp,
                    consequences=event.consequences,
                    emotional_impact=event.emotional_impact,
                    significance_level=event.significance_level,
                    metadata=event.metadata,
                )

                logger.info(f"Filtered unsafe content in event {event.event_id}")
                return filtered_event, False

            return event, True

        except Exception as e:
            logger.error(f"Error validating event content: {e}")
            # Return original event if validation fails
            return event, True

    def record_player_comfort_feedback(
        self,
        player_id: str,
        content_type: str,
        comfort_level: str,
        content_sample: str = "",
        notes: str = "",
    ) -> None:
        """
        Record player comfort feedback for adaptive content adjustment.

        Args:
            player_id: Player identifier
            content_type: Type of content (e.g., 'timeline_event', 'character_history')
            comfort_level: Player's comfort level ('comfortable', 'uncomfortable', etc.)
            content_sample: Sample of the content for analysis
            notes: Additional notes from the player
        """
        try:
            from content_safety_system import ComfortLevel

            # Convert string to ComfortLevel enum
            comfort_enum = ComfortLevel.COMFORTABLE
            if comfort_level.lower() == "uncomfortable":
                comfort_enum = ComfortLevel.UNCOMFORTABLE
            elif comfort_level.lower() == "very_uncomfortable":
                comfort_enum = ComfortLevel.VERY_UNCOMFORTABLE
            elif comfort_level.lower() == "distressed":
                comfort_enum = ComfortLevel.DISTRESSED
            elif comfort_level.lower() == "slightly_uncomfortable":
                comfort_enum = ComfortLevel.SLIGHTLY_UNCOMFORTABLE

            self.content_safety.record_player_comfort_feedback(
                player_id, content_type, comfort_enum, content_sample, notes
            )

            logger.info(
                f"Recorded comfort feedback for player {player_id}: {comfort_level}"
            )

        except Exception as e:
            logger.error(f"Error recording player comfort feedback: {e}")

    def assess_player_comfort(
        self, player_id: str, content: str, content_type: str
    ) -> tuple[str, float]:
        """
        Assess predicted player comfort level for content.

        Args:
            player_id: Player identifier
            content: Content to assess
            content_type: Type of content

        Returns:
            Tuple[str, float]: (comfort_level, confidence)
        """
        try:
            from content_safety_system import ContentType

            # Convert string to ContentType enum
            content_type_enum = ContentType.TIMELINE_EVENT
            if content_type.lower() == "character_history":
                content_type_enum = ContentType.CHARACTER_HISTORY
            elif content_type.lower() == "dialogue":
                content_type_enum = ContentType.DIALOGUE
            elif content_type.lower() == "narrative_text":
                content_type_enum = ContentType.NARRATIVE_TEXT

            comfort_level, confidence = (
                self.content_safety.get_player_comfort_assessment(
                    player_id, content, content_type_enum
                )
            )

            return comfort_level.value, confidence

        except Exception as e:
            logger.error(f"Error assessing player comfort: {e}")
            return "comfortable", 0.5

    def adapt_world_content_for_player(self, world_id: str, player_id: str) -> bool:
        """
        Adapt world content based on player comfort preferences and feedback.

        Args:
            world_id: World identifier
            player_id: Player identifier

        Returns:
            bool: True if adaptation was successful
        """
        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                return False

            # Get player comfort profile
            profile = self.content_safety.comfort_monitor.get_player_profile(player_id)

            # Adjust world flags based on player preferences
            adaptations_made = False

            # Reduce violence level if player is sensitive to violence
            violence_sensitivity = profile.adaptive_filters.get("violence", 0.5)
            if violence_sensitivity > 0.7:
                current_violence = world_state.get_flag("max_violence_level", 2)
                if current_violence > 1:
                    world_state.set_flag(
                        "max_violence_level", max(0, current_violence - 1)
                    )
                    adaptations_made = True
                    logger.info(
                        f"Reduced violence level for player {player_id} in world {world_id}"
                    )

            # Increase supportive content if player shows distress
            distress_indicators = sum(
                1
                for entry in profile.comfort_history
                if entry.get("comfort_level") in ["distressed", "very_uncomfortable"]
            )
            if distress_indicators > 2:
                world_state.set_flag("supportive_content_boost", True)
                world_state.set_flag("positive_event_multiplier", 1.5)
                adaptations_made = True
                logger.info(
                    f"Increased supportive content for player {player_id} in world {world_id}"
                )

            # Save adapted world state
            if adaptations_made:
                self.save_world_state(world_state)
                logger.info(
                    f"Adapted world content for player {player_id} in world {world_id}"
                )

            return adaptations_made

        except Exception as e:
            logger.error(f"Error adapting world content for player: {e}")
            return False

    def get_content_safety_statistics(self, world_id: str = None) -> dict[str, Any]:
        """
        Get content safety statistics for monitoring and reporting.

        Args:
            world_id: Optional world identifier for world-specific stats

        Returns:
            Dict[str, Any]: Safety statistics
        """
        try:
            stats = self.content_safety.get_safety_statistics()

            # Add world-specific information if requested
            if world_id:
                world_state = self.get_world_state(world_id)
                if world_state:
                    stats["world_id"] = world_id
                    stats["world_flags"] = dict(world_state.world_flags)
                    stats["active_players"] = len(self._player_comfort_profiles)

            return stats

        except Exception as e:
            logger.error(f"Error getting content safety statistics: {e}")
            return {"error": str(e)}

    def handle_content_escalation(
        self,
        case_id: str,
        resolution_action: str,
        resolution_notes: str = "",
        assigned_reviewer: str = None,
    ) -> bool:
        """
        Handle escalated content concerns and manual review.

        Args:
            case_id: Escalation case identifier
            resolution_action: Action taken ('approved', 'rejected', 'modified', 'escalated')
            resolution_notes: Notes about the resolution
            assigned_reviewer: Identifier of the reviewer

        Returns:
            bool: True if case was resolved successfully
        """
        try:
            success = self.content_safety.resolve_escalation_case(
                case_id, resolution_action, resolution_notes, assigned_reviewer
            )

            if success:
                logger.info(f"Resolved escalation case {case_id}: {resolution_action}")
            else:
                logger.error(f"Failed to resolve escalation case {case_id}")

            return success

        except Exception as e:
            logger.error(f"Error handling content escalation: {e}")
            return False

    def get_pending_escalations(
        self, severity_filter: int = None
    ) -> list[dict[str, Any]]:
        """
        Get pending content escalation cases.

        Args:
            severity_filter: Optional minimum severity level filter

        Returns:
            List[Dict[str, Any]]: List of pending escalation cases
        """
        try:
            cases = self.content_safety.get_escalation_cases(severity_filter)

            # Convert to dictionaries for easier handling
            case_dicts = []
            for case in cases:
                case_dict = {
                    "case_id": case.case_id,
                    "content": (
                        case.content[:200] + "..."
                        if len(case.content) > 200
                        else case.content
                    ),
                    "content_type": (
                        case.content_type.value
                        if hasattr(case.content_type, "value")
                        else str(case.content_type)
                    ),
                    "identified_risks": [
                        risk.value if hasattr(risk, "value") else str(risk)
                        for risk in case.identified_risks
                    ],
                    "player_id": case.player_id,
                    "world_id": case.world_id,
                    "severity_level": case.severity_level,
                    "status": case.status,
                    "created_at": (
                        case.created_at.isoformat()
                        if hasattr(case.created_at, "isoformat")
                        else str(case.created_at)
                    ),
                }
                case_dicts.append(case_dict)

            return case_dicts

        except Exception as e:
            logger.error(f"Error getting pending escalations: {e}")
            return []

        # Configuration
        self._cache_ttl = 1800  # 30 minutes
        self._max_active_worlds = 10

        logger.info("WorldStateManager initialized")

    def initialize_world(self, world_id: str, config: WorldConfig) -> WorldState:
        """
        Initialize a new world with the given configuration.

        Args:
            world_id: Unique identifier for the world
            config: World configuration settings

        Returns:
            WorldState: The initialized world state

        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            # Validate configuration
            config.validate()

            # Create new world state
            world_state = WorldState(
                world_id=world_id,
                world_name=config.world_name,
                current_time=datetime.now(),
                world_status=WorldStateFlag.ACTIVE,
            )

            # Initialize default characters
            for char_data in config.initial_characters:
                character_id = char_data.get("id", str(uuid.uuid4()))
                world_state.add_character(character_id, char_data)

                # Create character timeline
                self.timeline_engine.create_timeline(character_id, EntityType.CHARACTER)

                # Generate initial character backstory if requested
                if char_data.get("generate_backstory", False):
                    self._generate_character_backstory(character_id, world_state)

            # Initialize default locations
            for loc_data in config.initial_locations:
                location_id = loc_data.get("id", str(uuid.uuid4()))
                world_state.add_location(location_id, loc_data)

                # Create location timeline
                self.timeline_engine.create_timeline(location_id, EntityType.LOCATION)

                # Log metrics post-init
                try:
                    self.log_cache_metrics("post_init")
                except Exception:
                    pass

            # Initialize default objects
            for obj_data in config.initial_objects:
                object_id = obj_data.get("id", str(uuid.uuid4()))
                world_state.add_object(object_id, obj_data)
                # Create object timeline
                self.timeline_engine.create_timeline(object_id, EntityType.OBJECT)
            # Rebuild entity->world map from active sets
            try:
                self._entity_world_map.clear()
                for cid in world_state.active_characters.keys():
                    self._entity_world_map[cid] = world_id
                for lid in world_state.active_locations.keys():
                    self._entity_world_map[lid] = world_id
                for oid in world_state.active_objects.keys():
                    self._entity_world_map[oid] = world_id
            except Exception:
                logger.debug("Failed to rebuild entity->world map", exc_info=True)

            # Warm cache for newly initialized world
            if self.lw_cache:
                try:
                    self.lw_cache.warm_world(world_state)
                except Exception:
                    logger.debug("Failed to warm LW cache", exc_info=True)

            # Set configuration flags
            world_state.set_flag("evolution_speed", config.evolution_speed)
            world_state.set_flag("auto_evolution", config.auto_evolution)
            world_state.set_flag("max_timeline_events", config.max_timeline_events)
            world_state.set_flag("therapeutic_focus", config.therapeutic_focus)
            world_state.set_flag("content_boundaries", config.content_boundaries)

            # Validate the initialized world
            world_state.validate()

            # Save to persistence layer
            if not self._save_world_state(world_state):
                raise ValidationError("Failed to save initialized world state")

            # Add to active worlds cache
            self._active_worlds[world_id] = world_state

            logger.info(
                f"World '{config.world_name}' initialized successfully with ID: {world_id}"
            )
            return world_state

        except Exception as e:
            logger.error(f"Failed to initialize world: {e}")
            raise ValidationError(f"World initialization failed: {e}") from e

    def get_world_state(self, world_id: str) -> WorldState | None:
        """
        Get the current state of a world.

        Args:
            world_id: Unique identifier for the world

        Returns:
            WorldState: The current world state, or None if not found
        """
        try:
            # Check active worlds cache first
            if world_id in self._active_worlds:
                return self._active_worlds[world_id]

            # Try to load from cache (prefer new LW keyspace, fallback to legacy)
            cached_data = None
            if self.lw_cache:
                cached_data = self.lw_cache.get_world_state(world_id)
            if not cached_data:
                cached_data = self.cache.get(f"world_state:{world_id}")
            if cached_data:
                world_state = WorldState.from_json(cached_data)
                self._active_worlds[world_id] = world_state
                return world_state

            # Load from persistence layer
            world_state = self.persistence.load_world_state(world_id)
            if world_state:
                # Cache the loaded state in both spaces
                if self.lw_cache:
                    self.lw_cache.set_world_state(
                        world_id, world_state.to_json(), self._cache_ttl
                    )
                self.cache.set(
                    f"world_state:{world_id}", world_state.to_json(), self._cache_ttl
                )
                self._active_worlds[world_id] = world_state

                # Manage active worlds cache size
                self._manage_active_worlds_cache()

            return world_state
        except Exception as e:
            logger.error(f"Failed to get world state for {world_id}: {e}")
            return None

    def get_recent_events_cached(
        self,
        entity_id: str,
        limit: int = 50,
        min_significance: int = 1,
        days: int | None = None,
    ) -> list["TimelineEvent"]:
        """
        Prefer LW cache for recent events when world_id context is known; fallback to TimelineEngine data.
        If `days` is provided, filter events to those within the last N days (best-effort on cache entries).
        """
        try:
            if hasattr(self, "_entity_world_map"):
                wid = self._entity_world_map.get(entity_id)
                if wid and self.lw_cache:
                    recent = self.lw_cache.get_recent_timeline_events(wid, entity_id)
                    if recent:
                        from models.living_worlds_models import TimelineEvent as TE

                        evs = [TE.from_dict(e) for e in recent]
                        if days and days > 0:
                            cutoff = datetime.now() - timedelta(days=days)
                            evs = [e for e in evs if e.timestamp >= cutoff]
                        return evs[:limit]
        except Exception:
            logger.debug("get_recent_events_cached LW path failed", exc_info=True)
        # fallback to in-memory timeline
        try:
            tl = self.timeline_engine.get_timeline(entity_id)
            if not tl:
                return []
            evs = tl.get_events_by_significance(min_significance)
            if days and days > 0:
                cutoff = datetime.now() - timedelta(days=days)
                evs = [e for e in evs if e.timestamp >= cutoff]
            return evs[:limit]
        except Exception:
            logger.debug("get_recent_events_cached fallback failed", exc_info=True)
            return []

    # ---- Administrative helpers ----
    def get_world_summary_dict(self, world_id: str) -> dict[str, Any]:
        """Return a compact summary of a world's state for dashboards as a dict."""
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return {}
            flags = dict(ws.world_flags)
            cache_ver = None
            try:
                if self.lw_cache:
                    cache_ver = self.lw_cache.redis.get(
                        self.lw_cache._k_version(world_id)
                    )
            except Exception:
                cache_ver = None
            return {
                "world_id": ws.world_id,
                "world_name": ws.world_name,
                "last_updated": ws.last_updated.isoformat(),
                "active_characters_count": len(ws.active_characters),
                "active_locations_count": len(ws.active_locations),
                "active_objects_count": len(ws.active_objects),
                "evolution_paused": flags.get("evolution_paused", False),
                "cache_version": int(cache_ver) if cache_ver is not None else None,
            }
        except Exception:
            logger.debug("get_world_summary_dict failed", exc_info=True)
            return {}

    def export_world_state(self, world_id: str) -> str | None:
        """Export the world state as a JSON string for backup."""
        try:
            ws = self.get_world_state(world_id)
            return ws.to_json() if ws else None
        except Exception:
            logger.debug("export_world_state failed", exc_info=True)
            return None

    # ---- Administrative entity wrappers (WSM-level) ----
    def add_character(
        self, world_id: str, character_id: str, character_data: dict[str, Any]
    ) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.add_character(character_id, character_data)
            if ok:
                self._entity_world_map[character_id] = world_id
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, character_id)
                    self.lw_cache.invalidate_history(
                        world_id, "character", character_id
                    )
            return ok
        except Exception:
            logger.debug("admin.add_character failed", exc_info=True)
            return False

    def remove_character(self, world_id: str, character_id: str) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.remove_character(character_id)
            if ok:
                self._entity_world_map.pop(character_id, None)
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, character_id)
                    self.lw_cache.invalidate_history(
                        world_id, "character", character_id
                    )
            return ok
        except Exception:
            logger.debug("admin.remove_character failed", exc_info=True)
            return False

    def add_location(
        self, world_id: str, location_id: str, location_data: dict[str, Any]
    ) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.add_location(location_id, location_data)
            if ok:
                self._entity_world_map[location_id] = world_id
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, location_id)
                    self.lw_cache.invalidate_history(world_id, "location", location_id)
            return ok
        except Exception:
            logger.debug("admin.add_location failed", exc_info=True)
            return False

    def remove_location(self, world_id: str, location_id: str) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.remove_location(location_id)
            if ok:
                self._entity_world_map.pop(location_id, None)
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, location_id)
                    self.lw_cache.invalidate_history(world_id, "location", location_id)
            return ok
        except Exception:
            logger.debug("admin.remove_location failed", exc_info=True)
            return False

    def add_object(
        self, world_id: str, object_id: str, object_data: dict[str, Any]
    ) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.add_object(object_id, object_data)
            if ok:
                self._entity_world_map[object_id] = world_id
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, object_id)
                    self.lw_cache.invalidate_history(world_id, "object", object_id)
            return ok
        except Exception:
            logger.debug("admin.add_object failed", exc_info=True)
            return False

    def remove_object(self, world_id: str, object_id: str) -> bool:
        try:
            ws = self.get_world_state(world_id)
            if not ws:
                return False
            ok = ws.remove_object(object_id)
            if ok:
                self._entity_world_map.pop(object_id, None)
                self._save_world_state(ws)
                if self.lw_cache:
                    self.lw_cache.invalidate_recent_timeline(world_id, object_id)
                    self.lw_cache.invalidate_history(world_id, "object", object_id)
            return ok
        except Exception:
            logger.debug("admin.remove_object failed", exc_info=True)
            return False

    def export_world_state_to_file(self, world_id: str, file_path: str) -> bool:
        """Write the exported world JSON to a file path. Returns True on success."""
        try:
            data = self.export_world_state(world_id)
            if not data:
                return False
            import os

            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)
            return True
        except Exception:
            logger.debug("export_world_state_to_file failed", exc_info=True)
            return False

    def import_world_state_from_file(self, file_path: str) -> Optional["WorldState"]:
        """Read a world JSON from file and import it. Returns WorldState or None."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return self.import_world_state(content)
        except Exception:
            logger.debug("import_world_state_from_file failed", exc_info=True)
            return None

    def import_world_state(self, world_json: str) -> Optional["WorldState"]:
        """Import a world state from JSON and persist/cache it."""
        try:
            ws = WorldState.from_json(world_json)
            # Basic validation
            ws.validate()
            # Persist+cache
            self._save_world_state(ws)
            # Warm LW cache as well
            if self.lw_cache:
                try:
                    self.lw_cache.warm_world(ws)
                except Exception:
                    logger.debug("warm_world failed after import", exc_info=True)
            # Track in active worlds
            self._active_worlds[ws.world_id] = ws
            return ws
        except Exception:
            logger.debug("import_world_state failed", exc_info=True)
            return None

    # ---- Administrative controls and monitoring ----
    def get_debug_metrics_summary(self) -> dict[str, Any]:
        """
        Return a simple metrics summary for monitoring and admin purposes.
        Includes cache metrics, counts of active worlds, and timeline stats.
        """
        try:
            cache_metrics = dict(self.lw_cache.metrics) if self.lw_cache else {}
            return {
                "active_worlds_count": len(self._active_worlds),
                "timeline_count": self.timeline_engine.get_timeline_count(),
                "cache_metrics": cache_metrics,
            }
        except Exception:
            logger.debug("get_debug_metrics_summary failed", exc_info=True)
            return {
                "active_worlds_count": (
                    len(self._active_worlds) if hasattr(self, "_active_worlds") else 0
                ),
                "timeline_count": (
                    self.timeline_engine.get_timeline_count()
                    if hasattr(self, "timeline_engine")
                    else 0
                ),
                "cache_metrics": {},
            }

    def process_player_choice(
        self, world_id: str, choice_option: "ChoiceOption", context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a player choice through the PlayerChoiceImpactSystem and update world.

        Args:
            world_id: The world in which the choice occurs
            choice_option: The choice option selected by the player
            context: Context including player_id, characters_present, current_location, etc.

        Returns:
            Dict[str, Any]: Result including impact summary and any generated events.
        """
        # Defensive imports check
        if PlayerChoiceImpactSystem is None or NarrativeBranchingChoice is None:
            raise RuntimeError(
                "PlayerChoiceImpactSystem or NarrativeBranchingChoice not available"
            )

        # Ensure world exists
        world_state = self.get_world_state(world_id)
        if not world_state:
            raise ValidationError(f"World {world_id} not found")

        # Fill required context bits
        ctx = dict(context or {})
        ctx.setdefault("world_id", world_id)
        if "player_id" not in ctx:
            ctx["player_id"] = ctx.get("user_id", "player")
        if "current_time" not in ctx:
            ctx["current_time"] = datetime.now()

        # Instantiate system and process
        narrative = NarrativeBranchingChoice()
        pci = PlayerChoiceImpactSystem(
            timeline_engine=self.timeline_engine,
            world_state_manager=self,
            character_system=self.character_system,
            narrative_branching=narrative,
        )
        result = pci.process_player_choice(choice_option, ctx)

        # Persist preference guidance to influence evolution
        try:
            # Prefer a full influence map without thresholds
            player_id = ctx.get("player_id")
            bias_map = {}
            if player_id and hasattr(pci, "preference_tracker"):
                prefs = pci.preference_tracker.get_player_preferences(player_id)
                for category in prefs.keys():
                    influence = pci.preference_tracker.get_preference_influence(
                        player_id, category
                    )
                    bias_map[category.value] = float(influence)
            # Fallback to emphasis_areas if empty
            if not bias_map:
                guidance = result.get("world_evolution_guidance") or {}
                bias_map = guidance.get("emphasis_areas", {})
            # Store as a flag; evolution code will read and apply biases
            world_state.set_flag("evolution_preference_bias", bias_map)
        except Exception:
            logger.warning("Failed to store evolution preference bias", exc_info=True)

        # Persist world_state basic updates
        try:
            self._save_world_state(world_state)
        except Exception:
            logger.warning(
                "Failed to persist world state after processing player choice",
                exc_info=True,
            )

        return result

    def update_world_state(self, world_id: str, changes: list[dict[str, Any]]) -> bool:
        """
        Update world state with a list of changes.

        Args:
            world_id: Unique identifier for the world
            changes: List of change dictionaries with 'type', 'target', and 'data' keys

        Returns:
            bool: True if all changes were applied successfully
        """
        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                logger.error(f"World {world_id} not found for update")
                return False

            changes_applied = 0

            for change in changes:
                change_type = change.get("type")
                target = change.get("target")
                data = change.get("data", {})

                if change_type == "add_character":
                    if world_state.add_character(target, data):
                        changes_applied += 1
                        # record entity->world mapping for cache invalidation
                        try:
                            self._entity_world_map[target] = world_id
                        except Exception:
                            pass
                        # Create timeline event for character addition
                        event = TimelineEvent(
                            title=f"Character {target} joined the world",
                            metadata={"world_id": world_id},
                            description=f"New character {data.get('name', target)} was added to the world",
                            event_type=EventType.CHARACTER_INTRODUCTION,
                            participants=[target],
                            timestamp=datetime.now(),
                            significance_level=5,
                        )
                        self.timeline_engine.add_event(target, event)

                elif change_type == "update_character":
                    if target in world_state.active_characters:
                        world_state.active_characters[target].update(data)
                        world_state.last_updated = datetime.now()
                        changes_applied += 1

                    # keep entity->world for locations and objects too
                elif change_type == "add_location":
                    if world_state.add_location(target, data):
                        changes_applied += 1
                        try:
                            self._entity_world_map[target] = world_id
                        except Exception:
                            pass
                        # Create timeline for new location
                        self.timeline_engine.create_timeline(
                            target, EntityType.LOCATION
                        )

                elif change_type == "remove_character":
                    if world_state.remove_character(target):
                        changes_applied += 1

                elif change_type == "update_location":
                    if target in world_state.active_locations:
                        world_state.active_locations[target].update(data)
                        world_state.last_updated = datetime.now()
                        changes_applied += 1

                elif change_type == "remove_location":
                    if world_state.remove_location(target):
                        changes_applied += 1

                elif change_type == "add_object":
                    if world_state.add_object(target, data):
                        changes_applied += 1
                        # Create timeline for new object
                        self.timeline_engine.create_timeline(target, EntityType.OBJECT)

                elif change_type == "update_object":
                    if target in world_state.active_objects:
                        world_state.active_objects[target].update(data)
                        world_state.last_updated = datetime.now()
                        changes_applied += 1

                elif change_type == "remove_object":
                    if world_state.remove_object(target):
                        changes_applied += 1

                elif change_type == "set_flag":
                    world_state.set_flag(target, data.get("value"))
                    changes_applied += 1

                    # On flag changes, prefer to refresh flags cache and bump version
                    try:
                        if self.lw_cache and target:
                            # read current flags, update target, and set back
                            flags = (
                                world_state.world_flags
                                if hasattr(world_state, "world_flags")
                                else {}
                            )
                            if isinstance(flags, dict):
                                flags[target] = data.get("value")
                                self.lw_cache.set_flags(
                                    world_id, flags, ttl=self._cache_ttl
                                )
                                self.lw_cache.increment_version(world_id)
                    except Exception:
                        logger.debug(
                            "Failed to update flags cache on set_flag", exc_info=True
                        )

                elif change_type == "advance_time":
                    time_delta = timedelta(
                        seconds=data.get("seconds", 0),
                        minutes=data.get("minutes", 0),
                        hours=data.get("hours", 0),
                        days=data.get("days", 0),
                    )
                    world_state.advance_time(time_delta)
                    changes_applied += 1

                else:
                    logger.warning(f"Unknown change type: {change_type}")

            # Save updated world state
            if changes_applied > 0:
                success = self._save_world_state(world_state)
                if success:
                    logger.info(
                        f"Applied {changes_applied}/{len(changes)} changes to world {world_id}"
                    )
                return success

            return True

        except Exception as e:
            logger.error(f"Failed to update world state for {world_id}: {e}")
            return False

    def evolve_world(self, world_id: str, time_delta: timedelta) -> EvolutionResult:
        """
        Evolve the world state over a given time period.

        Args:
            world_id: Unique identifier for the world
            time_delta: Amount of time to simulate

        Returns:
            EvolutionResult: Result of the evolution operation
        """
        start_time = datetime.now()
        result = EvolutionResult(success=True)

        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                result.add_error(f"World {world_id} not found")
                return result

            # Check if auto evolution is enabled
            if not world_state.get_flag("auto_evolution", True):
                result.add_warning("Auto evolution is disabled for this world")
                return result

            evolution_speed = world_state.get_flag("evolution_speed", 1.0)
            effective_time_delta = timedelta(
                seconds=time_delta.total_seconds() * evolution_speed
            )

            # Advance world time
            world_state.advance_time(effective_time_delta)

            # Process pending evolution tasks
            pending_tasks = world_state.get_pending_evolution_tasks(
                world_state.current_time
            )
            for task in pending_tasks:
                if self._execute_evolution_task(world_state, task):
                    world_state.complete_evolution_task(task["task_id"])
                    result.events_generated += 1

            # Generate automatic evolution events based on time passage
            auto_events = self._generate_automatic_evolution_events(
                world_state, effective_time_delta
            )
            result.events_generated += len(auto_events)

            # Generate character evolution events
            for character_id, _character_data in world_state.active_characters.items():
                if self._evolve_character(
                    world_state, character_id, effective_time_delta
                ):
                    result.characters_evolved += 1

            # Generate location changes
            for location_id, _location_data in world_state.active_locations.items():
                if self._evolve_location(
                    world_state, location_id, effective_time_delta
                ):
                    result.locations_changed += 1

            # Generate object modifications
            for object_id, _object_data in world_state.active_objects.items():
                if self._evolve_object(world_state, object_id, effective_time_delta):
                    result.objects_modified += 1

            # Schedule future evolution tasks
            self._schedule_future_evolution_tasks(world_state, effective_time_delta)

            # Update last evolution time
            world_state.last_evolution = datetime.now()

            # Save evolved world state
            if not self._save_world_state(world_state):
                # In optional persistence mode, continue; otherwise, record error
                optional = os.getenv(
                    "LIVING_WORLDS_PERSISTENCE_OPTIONAL", "1"
                ).lower() in ("1", "true", "yes")
                if not optional:
                    result.add_error("Failed to save evolved world state")

            result.execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"World {world_id} evolved successfully: {result.events_generated} events, "
                f"{result.characters_evolved} characters, {result.locations_changed} locations, "
                f"{result.objects_modified} objects"
            )

        except Exception as e:
            result.add_error(f"Evolution failed: {e}")
            logger.error(f"Failed to evolve world {world_id}: {e}")

        return result

    def validate_world_consistency(self, world_id: str) -> ValidationResult:
        """
        Validate world consistency to ensure timeline and relationship coherence.

        Args:
            world_id: Unique identifier for the world

        Returns:
            ValidationResult: Result of the validation operation
        """
        result = ValidationResult(is_valid=True)

        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                result.add_data_integrity_issue(f"World {world_id} not found")
                return result

            # Validate world state itself
            try:
                world_state.validate()
            except ValidationError as e:
                result.add_data_integrity_issue(f"World state validation failed: {e}")

            # Log metrics post-save (after validation)
            try:
                self.log_cache_metrics("post_save")
            except Exception:
                pass

            # Validate timeline consistency
            self._validate_timeline_consistency(world_state, result)

            # Validate character consistency
            self._validate_character_consistency(world_state, result)

            # Validate location consistency
            self._validate_location_consistency(world_state, result)

            # Validate relationship consistency
            self._validate_relationship_consistency(world_state, result)

            # Check for data integrity issues
            self._validate_data_integrity(world_state, result)

            if result.is_valid:
                logger.info(f"World {world_id} passed consistency validation")
            else:
                total_issues = (
                    len(result.timeline_issues)
                    + len(result.character_issues)
                    + len(result.location_issues)
                    + len(result.relationship_issues)
                    + len(result.data_integrity_issues)
                )
                logger.warning(
                    f"World {world_id} has {total_issues} consistency issues"
                )

        except Exception as e:
            result.add_data_integrity_issue(f"Validation failed: {e}")
            logger.error(f"Failed to validate world {world_id}: {e}")

        return result

    def get_world_summary(self, world_id: str) -> WorldSummary | None:
        """
        Get a summary of the world state.

        Args:
            world_id: Unique identifier for the world

        Returns:
            WorldSummary: Summary of the world state, or None if not found
        """
        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                return None

            # Count timeline events across all entities
            total_events = 0
            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                if timeline:
                    total_events += len(timeline.events)

            for location_id in world_state.active_locations.keys():
                timeline = self.timeline_engine.get_timeline(location_id)
                if timeline:
                    total_events += len(timeline.events)

            for object_id in world_state.active_objects.keys():
                timeline = self.timeline_engine.get_timeline(object_id)
                if timeline:
                    total_events += len(timeline.events)

            return WorldSummary(
                world_id=world_state.world_id,
                world_name=world_state.world_name,
                current_time=world_state.current_time,
                character_count=len(world_state.active_characters),
                location_count=len(world_state.active_locations),
                object_count=len(world_state.active_objects),
                total_timeline_events=total_events,
                last_evolution=world_state.last_evolution,
                player_last_visit=world_state.player_last_visit,
                world_status=world_state.world_status,
                pending_evolution_tasks=len(world_state.evolution_schedule),
                world_flags=world_state.world_flags.copy(),
            )

        except Exception as e:
            logger.error(f"Failed to get world summary for {world_id}: {e}")
            return None

    # Private helper methods

    def _save_world_state(self, world_state: WorldState) -> bool:
        """Save world state to persistence layer and cache."""
        try:
            # Save to persistence layer (optional if not connected)
            persistence_ok = True
            try:
                persistence_ok = bool(self.persistence.save_world_state(world_state))
            except Exception as pe:
                # If persistence is not connected, allow cache-only mode
                logger.error(f"Failed to save world state: {pe}")
                persistence_ok = False

            # Proceed if either persistence saved or we are in cache-only mode
            if not persistence_ok:
                # If persistence is optional, continue; else treat as failure
                optional = os.getenv(
                    "LIVING_WORLDS_PERSISTENCE_OPTIONAL", "1"
                ).lower() in ("1", "true", "yes")
                if not optional:
                    return False

            # bump world version for readers
            try:
                if self.lw_cache:
                    self.lw_cache.increment_version(world_state.world_id)
            except Exception:
                logger.debug("Failed to increment world version", exc_info=True)

            # Update cache (new and legacy)
            if self.lw_cache:
                self.lw_cache.set_world_state(
                    world_state.world_id, world_state.to_json(), self._cache_ttl
                )
                # also update flags cache if present
                try:
                    flags = getattr(world_state, "world_flags", {})
                    if flags:
                        self.lw_cache.set_flags(
                            world_state.world_id, flags, ttl=self._cache_ttl
                        )
                except Exception:
                    logger.debug("Failed to set flags in cache", exc_info=True)
            self.cache.set(
                f"world_state:{world_state.world_id}",
                world_state.to_json(),
                self._cache_ttl,
            )

            # Update active worlds cache
            self._active_worlds[world_state.world_id] = world_state

            return True

        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False

    def _manage_active_worlds_cache(self) -> None:
        """Manage the size of the active worlds cache."""
        if len(self._active_worlds) > self._max_active_worlds:
            # Remove oldest accessed world
            oldest_world_id = min(
                self._active_worlds.keys(),
                key=lambda wid: self._active_worlds[wid].last_updated,
            )
            del self._active_worlds[oldest_world_id]
            logger.debug(f"Removed world {oldest_world_id} from active cache")

    def _generate_character_backstory(
        self, character_id: str, world_state: WorldState
    ) -> None:
        """Generate initial backstory for a character."""
        try:
            # Create some initial backstory events
            backstory_events = [
                TimelineEvent(
                    title=f"Character {character_id} childhood",
                    description="Formative childhood experiences",
                    event_type=EventType.PERSONAL_MILESTONE,
                    participants=[character_id],
                    timestamp=datetime.now() - timedelta(days=365 * 20),  # 20 years ago
                    significance_level=7,
                ),
                TimelineEvent(
                    title=f"Character {character_id} coming of age",
                    description="Important coming of age experience",
                    event_type=EventType.PERSONAL_MILESTONE,
                    participants=[character_id],
                    timestamp=datetime.now() - timedelta(days=365 * 5),  # 5 years ago
                    significance_level=8,
                ),
            ]

            for event in backstory_events:
                self.timeline_engine.add_event(character_id, event)

        except Exception as e:
            logger.warning(
                f"Failed to generate backstory for character {character_id}: {e}"
            )

    # ---- On-demand history generation ----
    def get_character_history(
        self,
        world_id: str,
        character_id: str,
        detail_level: int = 5,
        days: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate character history on demand with optional detail and time window.
        Caches results via LivingWorldsCache to avoid regeneration.
        """
        try:
            wid = world_id
            if self.lw_cache:
                cached = self.lw_cache.get_history(
                    wid, "character", character_id, detail_level, days
                )
                if cached:
                    return cached
            # Assemble from timeline and character development systems
            tl = self.timeline_engine.get_timeline(character_id)
            events = []
            if tl:
                events = list(tl.events)
            if days and days > 0:
                cutoff = datetime.now() - timedelta(days=days)
                events = [e for e in events if e.timestamp >= cutoff]
            # Use CharacterDevelopmentSystem for backstory context if available
            backstory = None
            try:
                raw_backstory = self.character_system.create_character_backstory(
                    character_id, min(max(detail_level, 1), 9)
                )

                # Validate and filter backstory content if it exists
                if raw_backstory and hasattr(raw_backstory, "description"):
                    validation_result = self.content_safety.validate_character_history(
                        raw_backstory.description, character_id, None, world_id
                    )

                    if not validation_result.is_safe:
                        # Filter the backstory content
                        filtered_description, _ = (
                            self.content_safety.process_content_safely(
                                raw_backstory.description,
                                ContentType.CHARACTER_HISTORY,
                                None,
                                world_id,
                            )
                        )
                        raw_backstory.description = filtered_description
                        logger.info(
                            f"Filtered character backstory content for {character_id}"
                        )

                backstory = raw_backstory
            except Exception as e:
                logger.warning(f"Error validating character backstory: {e}")
                backstory = None
            # Package history with adjustable detail
            history = {
                "character_id": character_id,
                "detail_level": detail_level,
                "period_days": days,
                "timeline_events": [
                    e.to_dict() for e in events[: max(50, detail_level * 20)]
                ],
                "backstory": (
                    backstory.to_dict()
                    if backstory and hasattr(backstory, "to_dict")
                    else None
                ),
            }
            if self.lw_cache:
                self.lw_cache.set_history(
                    wid, "character", character_id, detail_level, days, history, ttl=900
                )
            return history
        except Exception as e:
            logger.error(
                f"Failed to generate character history for {character_id}: {e}"
            )
            return {}

    def get_object_history(
        self,
        world_id: str,
        object_id: str,
        detail_level: int = 5,
        days: int | None = None,
    ) -> dict[str, Any]:
        """Generate object history on demand, cache results."""
        try:
            if self.lw_cache:
                cached = self.lw_cache.get_history(
                    world_id, "object", object_id, detail_level, days
                )
                if cached:
                    return cached
            # If object lifecycle manager exists, use its stored histories
            events = []
            tl = self.timeline_engine.get_timeline(object_id)
            if tl:
                events = list(tl.events)
            if days and days > 0:
                cutoff = datetime.now() - timedelta(days=days)
                events = [e for e in events if e.timestamp >= cutoff]
            history = {
                "object_id": object_id,
                "detail_level": detail_level,
                "period_days": days,
                "timeline_events": [
                    e.to_dict() for e in events[: max(50, detail_level * 20)]
                ],
            }
            if self.lw_cache:
                self.lw_cache.set_history(
                    world_id, "object", object_id, detail_level, days, history, ttl=900
                )
            return history
        except Exception as e:
            logger.error(f"Failed to generate object history for {object_id}: {e}")
            return {}

    def get_location_history(
        self,
        world_id: str,
        location_id: str,
        detail_level: int = 5,
        days: int | None = None,
    ) -> dict[str, Any]:
        """Generate location history on demand, cache results."""
        try:
            if self.lw_cache:
                cached = self.lw_cache.get_history(
                    world_id, "location", location_id, detail_level, days
                )
                if cached:
                    return cached
            # Prefer LocationEvolutionManager if present; otherwise use timeline only
            tl = self.timeline_engine.get_timeline(location_id)
            events = []
            if tl:
                events = list(tl.events)
            if days and days > 0:
                cutoff = datetime.now() - timedelta(days=days)
                events = [e for e in events if e.timestamp >= cutoff]
            history = {
                "location_id": location_id,
                "detail_level": detail_level,
                "period_days": days,
                "timeline_events": [
                    e.to_dict() for e in events[: max(50, detail_level * 20)]
                ],
            }
            if self.lw_cache:
                self.lw_cache.set_history(
                    world_id,
                    "location",
                    location_id,
                    detail_level,
                    days,
                    history,
                    ttl=900,
                )
            return history
        except Exception as e:
            logger.error(f"Failed to generate location history for {location_id}: {e}")
            return {}

    def _execute_evolution_task(
        self, world_state: WorldState, task: dict[str, Any]
    ) -> bool:
        """Execute a scheduled evolution task."""
        try:
            task_type = task.get("task_type")
            task_data = task.get("task_data", {})

            if task_type == "character_event":
                return self._generate_character_event(world_state, task_data)
            elif task_type == "location_change":
                return self._generate_location_change(world_state, task_data)
            elif task_type == "object_modification":
                return self._generate_object_modification(world_state, task_data)
            elif task_type == "relationship_change":
                return self._generate_relationship_change(world_state, task_data)
            else:
                logger.warning(f"Unknown evolution task type: {task_type}")
                return False

        except Exception as e:
            logger.error(f"Failed to execute evolution task: {e}")
            return False

    def _evolve_character(
        self, world_state: WorldState, character_id: str, time_delta: timedelta
    ) -> bool:
        """Evolve a character over time."""
        try:
            character_data = world_state.active_characters.get(character_id)
            if not character_data:
                return False

            # Simple character evolution - could be expanded
            # For now, just create a random event occasionally
            if (
                time_delta.days > 0
                and hash(character_id + str(world_state.current_time)) % 10 == 0
            ):
                event = TimelineEvent(
                    title=f"Daily life event for {character_id}",
                    description="Character experienced a routine daily event",
                    event_type=EventType.DAILY_LIFE,
                    participants=[character_id],
                    timestamp=world_state.current_time,
                    significance_level=3,
                )
                self.timeline_engine.add_event(character_id, event)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to evolve character {character_id}: {e}")
            return False

    def _evolve_location(
        self, world_state: WorldState, location_id: str, time_delta: timedelta
    ) -> bool:
        """Evolve a location over time."""
        try:
            location_data = world_state.active_locations.get(location_id)
            if not location_data:
                return False

            # Simple location evolution
            if time_delta.days > 7:  # Weekly changes
                event = TimelineEvent(
                    title=f"Environmental change at {location_id}",
                    description="Location experienced environmental changes",
                    event_type=EventType.ENVIRONMENTAL_CHANGE,
                    participants=[],
                    location_id=location_id,
                    timestamp=world_state.current_time,
                    significance_level=4,
                )
                self.timeline_engine.add_event(location_id, event)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to evolve location {location_id}: {e}")
            return False

    def _evolve_object(
        self, world_state: WorldState, object_id: str, time_delta: timedelta
    ) -> bool:
        """Evolve an object over time."""
        try:
            object_data = world_state.active_objects.get(object_id)
            if not object_data:
                return False

            # Simple object aging
            if time_delta.days > 30:  # Monthly aging
                event = TimelineEvent(
                    title=f"Object {object_id} shows wear",
                    description="Object shows signs of aging and wear",
                    event_type=EventType.OBJECT_MODIFICATION,
                    participants=[],
                    timestamp=world_state.current_time,
                    significance_level=2,
                )
                self.timeline_engine.add_event(object_id, event)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to evolve object {object_id}: {e}")
            return False

    def _generate_character_event(
        self, world_state: WorldState, task_data: dict[str, Any]
    ) -> bool:
        """Generate a character-specific event."""
        try:
            character_id = task_data.get("character_id")
            if not character_id or character_id not in world_state.active_characters:
                return False

            event = TimelineEvent(
                title=task_data.get("title", f"Event for {character_id}"),
                description=task_data.get(
                    "description", "Character experienced an event"
                ),
                event_type=EventType(
                    task_data.get("event_type", EventType.DAILY_LIFE.value)
                ),
                participants=[character_id],
                timestamp=world_state.current_time,
                significance_level=task_data.get("significance_level", 5),
            )

            self.timeline_engine.add_event(character_id, event)
            return True

        except Exception as e:
            logger.error(f"Failed to generate character event: {e}")
            return False

    def _generate_location_change(
        self, world_state: WorldState, task_data: dict[str, Any]
    ) -> bool:
        """Generate a location change event."""
        try:
            location_id = task_data.get("location_id")
            if not location_id or location_id not in world_state.active_locations:
                return False

            event = TimelineEvent(
                title=task_data.get("title", f"Change at {location_id}"),
                description=task_data.get(
                    "description", "Location experienced a change"
                ),
                event_type=EventType(
                    task_data.get("event_type", EventType.ENVIRONMENTAL_CHANGE.value)
                ),
                participants=[],
                location_id=location_id,
                timestamp=world_state.current_time,
                significance_level=task_data.get("significance_level", 4),
            )

            self.timeline_engine.add_event(location_id, event)
            return True

        except Exception as e:
            logger.error(f"Failed to generate location change: {e}")
            return False

    def _generate_object_modification(
        self, world_state: WorldState, task_data: dict[str, Any]
    ) -> bool:
        """Generate an object modification event."""
        try:
            object_id = task_data.get("object_id")
            if not object_id or object_id not in world_state.active_objects:
                return False

            event = TimelineEvent(
                title=task_data.get("title", f"Modification to {object_id}"),
                description=task_data.get("description", "Object was modified"),
                event_type=EventType(
                    task_data.get("event_type", EventType.OBJECT_MODIFICATION.value)
                ),
                participants=[],
                timestamp=world_state.current_time,
                significance_level=task_data.get("significance_level", 3),
            )

            self.timeline_engine.add_event(object_id, event)
            return True

        except Exception as e:
            logger.error(f"Failed to generate object modification: {e}")
            return False

    def _generate_relationship_change(
        self, world_state: WorldState, task_data: dict[str, Any]
    ) -> bool:
        """Generate a relationship change event."""
        try:
            participants = task_data.get("participants", [])
            if len(participants) < 2:
                return False

            # Verify all participants exist
            for participant in participants:
                if participant not in world_state.active_characters:
                    return False

            event = TimelineEvent(
                title=task_data.get(
                    "title", f"Relationship change between {', '.join(participants)}"
                ),
                description=task_data.get(
                    "description", "Relationship between characters changed"
                ),
                event_type=EventType(
                    task_data.get("event_type", EventType.RELATIONSHIP_CHANGE.value)
                ),
                participants=participants,
                timestamp=world_state.current_time,
                significance_level=task_data.get("significance_level", 6),
            )

            # Add event to all participants' timelines
            for participant in participants:
                self.timeline_engine.add_event(participant, event)

            return True

        except Exception as e:
            logger.error(f"Failed to generate relationship change: {e}")
            return False

    # Validation helper methods

    def _validate_timeline_consistency(
        self, world_state: WorldState, result: ValidationResult
    ) -> None:
        """Validate timeline consistency across all entities."""
        try:
            all_timelines = []

            # Collect all timelines
            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                if timeline:
                    all_timelines.append((character_id, timeline))

            for location_id in world_state.active_locations.keys():
                timeline = self.timeline_engine.get_timeline(location_id)
                if timeline:
                    all_timelines.append((location_id, timeline))

            for object_id in world_state.active_objects.keys():
                timeline = self.timeline_engine.get_timeline(object_id)
                if timeline:
                    all_timelines.append((object_id, timeline))

            # Check for timeline consistency issues
            for entity_id, timeline in all_timelines:
                # Check for chronological order
                events = sorted(timeline.events, key=lambda e: e.timestamp)
                for i in range(1, len(events)):
                    if events[i].timestamp < events[i - 1].timestamp:
                        result.add_timeline_issue(
                            f"Timeline for {entity_id} has events out of chronological order"
                        )

                # Check for future events
                now = datetime.now()
                for event in timeline.events:
                    if event.timestamp > now + timedelta(hours=1):  # Allow small buffer
                        result.add_timeline_issue(
                            f"Timeline for {entity_id} has future event: {event.title}"
                        )

                # Check for duplicate events
                event_signatures = set()
                for event in timeline.events:
                    signature = (
                        event.title,
                        event.timestamp.isoformat(),
                        event.event_type.value,
                    )
                    if signature in event_signatures:
                        result.add_timeline_issue(
                            f"Timeline for {entity_id} has duplicate event: {event.title}"
                        )
                    event_signatures.add(signature)

        except Exception as e:
            result.add_timeline_issue(f"Timeline validation failed: {e}")

    def _validate_character_consistency(
        self, world_state: WorldState, result: ValidationResult
    ) -> None:
        """Validate character consistency and relationships."""
        try:
            for character_id, character_data in world_state.active_characters.items():
                # Check for required character fields
                if not isinstance(character_data, dict):
                    result.add_character_issue(
                        f"Character {character_id} data is not a dictionary"
                    )
                    continue

                # Check for basic character information
                if "name" not in character_data:
                    result.add_character_issue(f"Character {character_id} missing name")

                # Check for valid character state if present
                if "emotional_state" in character_data:
                    try:
                        EmotionalState(character_data["emotional_state"])
                    except (ValueError, TypeError):
                        result.add_character_issue(
                            f"Character {character_id} has invalid emotional state"
                        )

                # Check for timeline existence
                timeline = self.timeline_engine.get_timeline(character_id)
                if not timeline:
                    result.add_character_issue(
                        f"Character {character_id} missing timeline"
                    )

        except Exception as e:
            result.add_character_issue(f"Character validation failed: {e}")

    def _validate_location_consistency(
        self, world_state: WorldState, result: ValidationResult
    ) -> None:
        """Validate location consistency and accessibility."""
        try:
            for location_id, location_data in world_state.active_locations.items():
                # Check for required location fields
                if not isinstance(location_data, dict):
                    result.add_location_issue(
                        f"Location {location_id} data is not a dictionary"
                    )
                    continue

                # Check for basic location information
                if "name" not in location_data:
                    result.add_location_issue(f"Location {location_id} missing name")

                if "description" not in location_data:
                    result.add_location_issue(
                        f"Location {location_id} missing description"
                    )

                # Check for timeline existence
                timeline = self.timeline_engine.get_timeline(location_id)
                if not timeline:
                    result.add_location_issue(
                        f"Location {location_id} missing timeline"
                    )

                # Check for valid connections if present
                if "connections" in location_data:
                    connections = location_data["connections"]
                    if isinstance(connections, list):
                        for connected_id in connections:
                            if connected_id not in world_state.active_locations:
                                result.add_location_issue(
                                    f"Location {location_id} connected to non-existent location {connected_id}"
                                )

        except Exception as e:
            result.add_location_issue(f"Location validation failed: {e}")

    def _validate_relationship_consistency(
        self, world_state: WorldState, result: ValidationResult
    ) -> None:
        """Validate relationship consistency between characters."""
        try:
            # Check for relationship consistency in timeline events
            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                if not timeline:
                    continue

                for event in timeline.events:
                    # Check that all participants exist
                    for participant in event.participants:
                        if (
                            participant != character_id
                            and participant not in world_state.active_characters
                        ):
                            result.add_relationship_issue(
                                f"Event '{event.title}' references non-existent character {participant}"
                            )

                    # Check location references
                    if (
                        event.location_id
                        and event.location_id not in world_state.active_locations
                    ):
                        result.add_relationship_issue(
                            f"Event '{event.title}' references non-existent location {event.location_id}"
                        )

        except Exception as e:
            result.add_relationship_issue(f"Relationship validation failed: {e}")

    def _validate_data_integrity(
        self, world_state: WorldState, result: ValidationResult
    ) -> None:
        """Validate overall data integrity."""
        try:
            # Check world state basic integrity
            if not world_state.world_id:
                result.add_data_integrity_issue("World ID is empty")

            if not world_state.world_name:
                result.add_data_integrity_issue("World name is empty")

            # Check timestamp consistency
            if world_state.last_evolution > datetime.now():
                result.add_data_integrity_issue("Last evolution time is in the future")

            if world_state.created_at > datetime.now():
                result.add_data_integrity_issue("Creation time is in the future")

            if world_state.last_updated > datetime.now():
                result.add_data_integrity_issue("Last updated time is in the future")

            # Check evolution schedule
            for task in world_state.evolution_schedule:
                if "task_id" not in task:
                    result.add_data_integrity_issue("Evolution task missing task_id")

                if "task_type" not in task:
                    result.add_data_integrity_issue("Evolution task missing task_type")

                if "scheduled_time" not in task:
                    result.add_data_integrity_issue(
                        "Evolution task missing scheduled_time"
                    )

            # Check for reasonable limits
            max_events = world_state.get_flag("max_timeline_events", 1000)
            total_events = 0

            for character_id in world_state.active_characters.keys():
                timeline = self.timeline_engine.get_timeline(character_id)
                if timeline:
                    total_events += len(timeline.events)

            if total_events > max_events * 2:  # Allow some buffer
                result.add_data_integrity_issue(
                    f"Total timeline events ({total_events}) exceeds reasonable limit"
                )

        except Exception as e:
            result.add_data_integrity_issue(f"Data integrity validation failed: {e}")

    # New methods for enhanced time passage and world evolution

    def simulate_time_passage(
        self, world_id: str, time_delta: timedelta, background_processing: bool = False
    ) -> EvolutionResult:
        """
        Simulate time passage in the world with comprehensive evolution.

        Args:
            world_id: Unique identifier for the world
            time_delta: Amount of time to simulate
            background_processing: Whether this is background processing during player absence

        Returns:
            EvolutionResult: Result of the time passage simulation
        """
        start_time = datetime.now()
        result = EvolutionResult(success=True)

        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                result.add_error(f"World {world_id} not found")
                return result

            # Check evolution parameters
            evolution_speed = world_state.get_flag("evolution_speed", 1.0)
            if background_processing:
                # Reduce evolution speed for background processing to prevent overwhelming changes
                evolution_speed *= world_state.get_flag(
                    "background_evolution_multiplier", 0.5
                )

            effective_time_delta = timedelta(
                seconds=time_delta.total_seconds() * evolution_speed
            )

            # Break down large time periods into smaller chunks for more realistic evolution
            chunk_size = timedelta(days=1)  # Process in daily chunks

            while effective_time_delta > timedelta(0):
                current_chunk = min(chunk_size, effective_time_delta)

                # Advance world time for this chunk
                world_state.advance_time(current_chunk)

                # Generate events for this time period
                chunk_events = self._generate_time_period_events(
                    world_state, current_chunk, background_processing
                )
                result.events_generated += len(chunk_events)

                # Evolve entities for this chunk
                character_changes = self._evolve_characters_for_period(
                    world_state, current_chunk
                )
                result.characters_evolved += character_changes

                location_changes = self._evolve_locations_for_period(
                    world_state, current_chunk
                )
                result.locations_changed += location_changes

                object_changes = self._evolve_objects_for_period(
                    world_state, current_chunk
                )
                result.objects_modified += object_changes

                effective_time_delta -= current_chunk

            # Update last evolution time
            world_state.last_evolution = datetime.now()

            # Save evolved world state
            if not self._save_world_state(world_state):
                result.add_error("Failed to save evolved world state")

            result.execution_time = (datetime.now() - start_time).total_seconds()

            if background_processing:
                logger.info(
                    f"Background evolution for world {world_id}: {result.events_generated} events, "
                    f"{result.characters_evolved} characters, {result.locations_changed} locations, "
                    f"{result.objects_modified} objects over {time_delta}"
                )
            else:
                logger.info(
                    f"Time passage simulation for world {world_id}: {result.events_generated} events, "
                    f"{result.characters_evolved} characters, {result.locations_changed} locations, "
                    f"{result.objects_modified} objects over {time_delta}"
                )

        except Exception as e:
            result.add_error(f"Time passage simulation failed: {e}")
            logger.error(f"Failed to simulate time passage for world {world_id}: {e}")

        return result

    def configure_evolution_parameters(
        self, world_id: str, parameters: dict[str, Any]
    ) -> bool:
        """
        Configure evolution parameters for a world.

        Args:
            world_id: Unique identifier for the world
            parameters: Dictionary of evolution parameters to set
                - evolution_speed: Multiplier for evolution rate (default 1.0)
                - auto_evolution: Whether automatic evolution is enabled (default True)
                - background_evolution_multiplier: Multiplier for background evolution (default 0.5)
                - character_evolution_rate: Rate of character evolution events (default 0.1)
                - location_evolution_rate: Rate of location evolution events (default 0.05)
                - object_evolution_rate: Rate of object evolution events (default 0.02)
                - seasonal_changes_enabled: Whether seasonal changes occur (default True)
                - relationship_evolution_enabled: Whether relationships evolve (default True)
                - max_events_per_day: Maximum events generated per day (default 10)

        Returns:
            bool: True if parameters were configured successfully
        """
        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                logger.error(f"World {world_id} not found")
                return False

            # Set evolution parameters with validation
            for param_name, param_value in parameters.items():
                if param_name == "evolution_speed":
                    if not isinstance(param_value, int | float) or param_value <= 0:
                        raise ValidationError(
                            "Evolution speed must be a positive number"
                        )
                    world_state.set_flag("evolution_speed", float(param_value))

                elif param_name == "auto_evolution":
                    if not isinstance(param_value, bool):
                        raise ValidationError("Auto evolution must be a boolean")
                    world_state.set_flag("auto_evolution", param_value)

                elif param_name == "background_evolution_multiplier":
                    if not isinstance(param_value, int | float) or param_value < 0:
                        raise ValidationError(
                            "Background evolution multiplier must be non-negative"
                        )
                    world_state.set_flag(
                        "background_evolution_multiplier", float(param_value)
                    )

                elif param_name == "character_evolution_rate":
                    if not isinstance(param_value, int | float) or param_value < 0:
                        raise ValidationError(
                            "Character evolution rate must be non-negative"
                        )
                    world_state.set_flag("character_evolution_rate", float(param_value))

                elif param_name == "location_evolution_rate":
                    if not isinstance(param_value, int | float) or param_value < 0:
                        raise ValidationError(
                            "Location evolution rate must be non-negative"
                        )
                    world_state.set_flag("location_evolution_rate", float(param_value))

                elif param_name == "object_evolution_rate":
                    if not isinstance(param_value, int | float) or param_value < 0:
                        raise ValidationError(
                            "Object evolution rate must be non-negative"
                        )
                    world_state.set_flag("object_evolution_rate", float(param_value))

                elif param_name == "seasonal_changes_enabled":
                    if not isinstance(param_value, bool):
                        raise ValidationError(
                            "Seasonal changes enabled must be a boolean"
                        )
                    world_state.set_flag("seasonal_changes_enabled", param_value)

                elif param_name == "relationship_evolution_enabled":
                    if not isinstance(param_value, bool):
                        raise ValidationError(
                            "Relationship evolution enabled must be a boolean"
                        )
                    world_state.set_flag("relationship_evolution_enabled", param_value)

                elif param_name == "max_events_per_day":
                    if not isinstance(param_value, int) or param_value < 0:
                        raise ValidationError(
                            "Max events per day must be a non-negative integer"
                        )
                    world_state.set_flag("max_events_per_day", param_value)

                else:
                    logger.warning(f"Unknown evolution parameter: {param_name}")

            # Save updated world state
            if not self._save_world_state(world_state):
                optional = os.getenv(
                    "LIVING_WORLDS_PERSISTENCE_OPTIONAL", "1"
                ).lower() in ("1", "true", "yes")
                if not optional:
                    logger.error(
                        "Failed to save world state with new evolution parameters"
                    )
                    return False

            logger.info(
                f"Configured evolution parameters for world {world_id}: {list(parameters.keys())}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to configure evolution parameters for world {world_id}: {e}"
            )
            return False

    def get_evolution_parameters(self, world_id: str) -> dict[str, Any] | None:
        """
        Get current evolution parameters for a world.

        Args:
            world_id: Unique identifier for the world

        Returns:
            Optional[Dict[str, Any]]: Evolution parameters or None if world not found
        """
        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                return None

            return {
                "evolution_speed": world_state.get_flag("evolution_speed", 1.0),
                "auto_evolution": world_state.get_flag("auto_evolution", True),
                "background_evolution_multiplier": world_state.get_flag(
                    "background_evolution_multiplier", 0.5
                ),
                "character_evolution_rate": world_state.get_flag(
                    "character_evolution_rate", 0.1
                ),
                "location_evolution_rate": world_state.get_flag(
                    "location_evolution_rate", 0.05
                ),
                "object_evolution_rate": world_state.get_flag(
                    "object_evolution_rate", 0.02
                ),
                "seasonal_changes_enabled": world_state.get_flag(
                    "seasonal_changes_enabled", True
                ),
                "relationship_evolution_enabled": world_state.get_flag(
                    "relationship_evolution_enabled", True
                ),
                "max_events_per_day": world_state.get_flag("max_events_per_day", 10),
            }

        except Exception as e:
            logger.error(
                f"Failed to get evolution parameters for world {world_id}: {e}"
            )
            return None

    def _generate_automatic_evolution_events(
        self, world_state: WorldState, time_delta: timedelta
    ) -> list[TimelineEvent]:
        """Generate automatic evolution events based on time passage."""
        events = []

        try:
            days_passed = time_delta.total_seconds() / (24 * 3600)
            max_events_per_day = world_state.get_flag("max_events_per_day", 10)
            max_events = int(days_passed * max_events_per_day)

            # Generate character evolution events
            character_rate = world_state.get_flag("character_evolution_rate", 0.1)
            for character_id in world_state.active_characters.keys():
                if len(events) >= max_events:
                    break

                # Probability of event based on time passed and evolution rate
                event_probability = min(days_passed * character_rate, 0.8)
                if (
                    hash(character_id + str(world_state.current_time)) % 100
                    < event_probability * 100
                ):
                    event = self._generate_character_evolution_event(
                        world_state, character_id, time_delta
                    )
                    if event:
                        events.append(event)

            # Generate location evolution events
            location_rate = world_state.get_flag("location_evolution_rate", 0.05)
            for location_id in world_state.active_locations.keys():
                if len(events) >= max_events:
                    break

                event_probability = min(days_passed * location_rate, 0.6)
                if (
                    hash(location_id + str(world_state.current_time)) % 100
                    < event_probability * 100
                ):
                    event = self._generate_location_evolution_event(
                        world_state, location_id, time_delta
                    )
                    if event:
                        events.append(event)

            # Generate object evolution events
            object_rate = world_state.get_flag("object_evolution_rate", 0.02)
            for object_id in world_state.active_objects.keys():
                if len(events) >= max_events:
                    break

                event_probability = min(days_passed * object_rate, 0.4)
                if (
                    hash(object_id + str(world_state.current_time)) % 100
                    < event_probability * 100
                ):
                    event = self._generate_object_evolution_event(
                        world_state, object_id, time_delta
                    )
                    if event:
                        events.append(event)

            # Generate seasonal events if enabled
            if (
                world_state.get_flag("seasonal_changes_enabled", True)
                and days_passed >= 7
            ):
                seasonal_event = self._generate_seasonal_event(world_state, time_delta)
                if seasonal_event:
                    events.append(seasonal_event)

            # Generate relationship events if enabled
            if (
                world_state.get_flag("relationship_evolution_enabled", True)
                and len(world_state.active_characters) > 1
            ):
                relationship_event = self._generate_relationship_evolution_event(
                    world_state, time_delta
                )
                if relationship_event:
                    events.append(relationship_event)

        except Exception as e:
            logger.error(f"Failed to generate automatic evolution events: {e}")

        return events

    def _generate_time_period_events(
        self,
        world_state: WorldState,
        time_delta: timedelta,
        background_processing: bool,
    ) -> list[TimelineEvent]:
        """Generate events for a specific time period."""
        events = []

        try:
            # Reduce event generation during background processing
            event_multiplier = 0.3 if background_processing else 1.0

            # Apply player preference emphasis to bias event generation
            bias = world_state.get_flag("evolution_preference_bias", {}) or {}
            # Map preference categories to event types
            social_bias = float(bias.get("social", 0.0))
            exploration_bias = float(bias.get("exploration", 0.0))
            emotional_bias = float(bias.get("emotional", 0.0))
            creative_bias = float(bias.get("creative", 0.0))
            therapeutic_bias = float(bias.get("therapeutic", 0.0))
            action_bias = float(bias.get("action", 0.0))
            reflection_bias = float(bias.get("reflection", 0.0))
            float(bias.get("analytical", 0.0))

            # Helper to compute a multiplier in [0.5, 1.5] from [-1,1] bias values
            def bias_mult(b: float) -> float:
                try:
                    b = max(-1.0, min(1.0, float(b)))
                except Exception:
                    b = 0.0
                return 1.0 + 0.5 * b

            # Generate daily life events
            days_passed = time_delta.total_seconds() / (24 * 3600)
            if days_passed >= 1.0:
                daily_events = self._generate_daily_life_events(
                    world_state,
                    int(days_passed),
                    event_multiplier * bias_mult(reflection_bias),
                )
                events.extend(daily_events)

            # Generate environmental changes (exploration/creative/action bias)
            if days_passed >= 3.0:  # Environmental changes every few days
                env_events = self._generate_environmental_change_events(
                    world_state,
                    time_delta,
                    event_multiplier
                    * bias_mult(exploration_bias or creative_bias or action_bias),
                )
                events.extend(env_events)

            # Generate social interaction events (social/emotional/therapeutic bias)
            if len(world_state.active_characters) > 1 and days_passed >= 0.5:
                social_events = self._generate_social_interaction_events(
                    world_state,
                    time_delta,
                    event_multiplier
                    * bias_mult(social_bias or emotional_bias or therapeutic_bias),
                )
                events.extend(social_events)

        except Exception as e:
            logger.error(f"Failed to generate time period events: {e}")

        return events

    def _evolve_characters_for_period(
        self, world_state: WorldState, time_delta: timedelta
    ) -> int:
        """Evolve characters for a specific time period."""
        changes = 0

        try:
            for character_id, _character_data in world_state.active_characters.items():
                # Age object using existing object lifecycle manager if available
                try:
                    from object_lifecycle_manager import ObjectLifecycleManager

                    if hasattr(self, "object_lifecycle_manager"):
                        # Character aging and development
                        if self._apply_character_development(
                            world_state, character_id, time_delta
                        ):
                            changes += 1
                except ImportError:
                    # Fallback to simple character evolution
                    if self._evolve_character(world_state, character_id, time_delta):
                        changes += 1

        except Exception as e:
            logger.error(f"Failed to evolve characters for period: {e}")

        return changes

    def _evolve_locations_for_period(
        self, world_state: WorldState, time_delta: timedelta
    ) -> int:
        """Evolve locations for a specific time period."""
        changes = 0

        try:
            # Use location evolution manager if available
            try:
                from location_evolution_manager import LocationEvolutionManager

                if hasattr(self, "location_evolution_manager"):
                    for location_id in world_state.active_locations.keys():
                        location_change = (
                            self.location_evolution_manager.evolve_location(
                                location_id, time_delta
                            )
                        )
                        if location_change:
                            changes += 1
                else:
                    # Fallback to simple location evolution
                    for location_id in world_state.active_locations.keys():
                        if self._evolve_location(world_state, location_id, time_delta):
                            changes += 1
            except ImportError:
                # Fallback to simple location evolution
                for location_id in world_state.active_locations.keys():
                    if self._evolve_location(world_state, location_id, time_delta):
                        changes += 1

        except Exception as e:
            logger.error(f"Failed to evolve locations for period: {e}")

        return changes

    def _evolve_objects_for_period(
        self, world_state: WorldState, time_delta: timedelta
    ) -> int:
        """Evolve objects for a specific time period."""
        changes = 0

        try:
            # Use object lifecycle manager if available
            try:
                from object_lifecycle_manager import ObjectLifecycleManager

                if hasattr(self, "object_lifecycle_manager"):
                    for object_id in world_state.active_objects.keys():
                        aged_state = self.object_lifecycle_manager.age_object(
                            object_id, time_delta
                        )
                        if aged_state:
                            changes += 1
                else:
                    # Fallback to simple object evolution
                    for object_id in world_state.active_objects.keys():
                        if self._evolve_object(world_state, object_id, time_delta):
                            changes += 1
            except ImportError:
                # Fallback to simple object evolution
                for object_id in world_state.active_objects.keys():
                    if self._evolve_object(world_state, object_id, time_delta):
                        changes += 1

        except Exception as e:
            logger.error(f"Failed to evolve objects for period: {e}")

        return changes

    def _schedule_future_evolution_tasks(
        self, world_state: WorldState, time_delta: timedelta
    ) -> None:
        """Schedule future evolution tasks based on current world state."""
        try:
            # Schedule character development milestones
            for character_id in world_state.active_characters.keys():
                # Schedule a character development event in the future
                future_time = world_state.current_time + timedelta(
                    days=7
                )  # Weekly character events
                task = {
                    "task_id": str(uuid.uuid4()),
                    "task_type": "character_event",
                    "scheduled_time": future_time,
                    "task_data": {
                        "character_id": character_id,
                        "title": f"Weekly development for {character_id}",
                        "description": "Character experiences personal growth",
                        "event_type": EventType.PERSONAL_MILESTONE.value,
                        "significance_level": 5,
                    },
                }
                world_state.schedule_evolution_task(task)

            # Schedule location changes
            for location_id in world_state.active_locations.keys():
                # Schedule environmental changes
                future_time = world_state.current_time + timedelta(
                    days=14
                )  # Bi-weekly location changes
                task = {
                    "task_id": str(uuid.uuid4()),
                    "task_type": "location_change",
                    "scheduled_time": future_time,
                    "task_data": {
                        "location_id": location_id,
                        "title": f"Environmental change at {location_id}",
                        "description": "Location undergoes environmental changes",
                        "event_type": EventType.ENVIRONMENTAL_CHANGE.value,
                        "significance_level": 4,
                    },
                }
                world_state.schedule_evolution_task(task)

        except Exception as e:
            logger.error(f"Failed to schedule future evolution tasks: {e}")

    def _generate_character_evolution_event(
        self, world_state: WorldState, character_id: str, time_delta: timedelta
    ) -> TimelineEvent | None:
        """Generate a character evolution event."""
        try:
            character_data = world_state.active_characters.get(character_id)
            if not character_data:
                return None

            # Generate different types of character events based on time passed
            days_passed = time_delta.total_seconds() / (24 * 3600)

            if days_passed >= 30:  # Monthly major events
                event_types = [
                    EventType.PERSONAL_MILESTONE,
                    EventType.LEARNING,
                    EventType.ACHIEVEMENT,
                ]
                significance = 7
            elif days_passed >= 7:  # Weekly moderate events
                event_types = [
                    EventType.DAILY_LIFE,
                    EventType.CONVERSATION,
                    EventType.LEARNING,
                ]
                significance = 5
            else:  # Daily minor events
                event_types = [EventType.DAILY_LIFE, EventType.CONVERSATION]
                significance = 3

            event_type = event_types[
                hash(character_id + str(world_state.current_time)) % len(event_types)
            ]

            event = TimelineEvent(
                event_type=event_type,
                title=f"Character development: {character_data.get('name', character_id)}",
                description=f"Character experienced {event_type.value} during time passage",
                participants=[character_id],
                timestamp=world_state.current_time,
                significance_level=significance,
                tags=["evolution", "character", event_type.value],
            )

            # Add event to timeline
            self.timeline_engine.add_event(character_id, event)

            return event

        except Exception as e:
            logger.error(f"Failed to generate character evolution event: {e}")
            return None

    def _generate_location_evolution_event(
        self, world_state: WorldState, location_id: str, time_delta: timedelta
    ) -> TimelineEvent | None:
        """Generate a location evolution event."""
        try:
            location_data = world_state.active_locations.get(location_id)
            if not location_data:
                return None

            days_passed = time_delta.total_seconds() / (24 * 3600)

            if days_passed >= 90:  # Seasonal changes
                event_type = EventType.SEASONAL_CHANGE
                significance = 6
            elif days_passed >= 30:  # Monthly environmental changes
                event_type = EventType.ENVIRONMENTAL_CHANGE
                significance = 5
            else:  # Minor environmental shifts
                event_type = EventType.ENVIRONMENTAL_CHANGE
                significance = 3

            event = TimelineEvent(
                event_type=event_type,
                title=f"Location evolution: {location_data.get('name', location_id)}",
                description=f"Location experienced {event_type.value} during time passage",
                location_id=location_id,
                timestamp=world_state.current_time,
                significance_level=significance,
                tags=["evolution", "location", event_type.value],
            )

            # Add event to timeline
            self.timeline_engine.add_event(location_id, event)

            return event

        except Exception as e:
            logger.error(f"Failed to generate location evolution event: {e}")
            return None

    def _generate_object_evolution_event(
        self, world_state: WorldState, object_id: str, time_delta: timedelta
    ) -> TimelineEvent | None:
        """Generate an object evolution event."""
        try:
            object_data = world_state.active_objects.get(object_id)
            if not object_data:
                return None

            days_passed = time_delta.total_seconds() / (24 * 3600)

            # Objects evolve more slowly than characters and locations
            if days_passed >= 180:  # Semi-annual major changes
                significance = 6
                description = "Object shows significant aging and wear"
            elif days_passed >= 60:  # Bi-monthly moderate changes
                significance = 4
                description = "Object shows moderate wear and aging"
            else:  # Minor wear
                significance = 2
                description = "Object shows minor signs of aging"

            event = TimelineEvent(
                event_type=EventType.OBJECT_MODIFICATION,
                title=f"Object aging: {object_data.get('name', object_id)}",
                description=description,
                participants=[object_id],
                timestamp=world_state.current_time,
                significance_level=significance,
                tags=["evolution", "object", "aging"],
            )

            # Add event to timeline
            self.timeline_engine.add_event(object_id, event)

            return event

        except Exception as e:
            logger.error(f"Failed to generate object evolution event: {e}")
            return None

    def _generate_seasonal_event(
        self, world_state: WorldState, time_delta: timedelta
    ) -> TimelineEvent | None:
        """Generate a seasonal change event."""
        try:
            days_passed = time_delta.total_seconds() / (24 * 3600)

            # Only generate seasonal events for significant time periods
            if days_passed < 30:
                return None

            # Determine season based on current time
            month = world_state.current_time.month
            if month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            elif month in [9, 10, 11]:
                season = "autumn"
            else:
                season = "winter"

            event = TimelineEvent(
                event_type=EventType.SEASONAL_CHANGE,
                title=f"Seasonal transition to {season}",
                description=f"The world transitions to {season}, bringing environmental changes",
                timestamp=world_state.current_time,
                significance_level=7,
                tags=["seasonal", season, "world"],
            )

            # Add to world timeline if it exists
            world_timeline = self.timeline_engine.get_timeline(world_state.world_id)
            if world_timeline:
                self.timeline_engine.add_event(world_state.world_id, event)

            return event

        except Exception as e:
            logger.error(f"Failed to generate seasonal event: {e}")
            return None

    def _generate_relationship_evolution_event(
        self, world_state: WorldState, time_delta: timedelta
    ) -> TimelineEvent | None:
        """Generate a relationship evolution event."""
        try:
            characters = list(world_state.active_characters.keys())
            if len(characters) < 2:
                return None

            # Select two random characters for relationship evolution
            char1 = characters[hash(str(world_state.current_time)) % len(characters)]
            char2 = characters[
                hash(str(world_state.current_time) + "2") % len(characters)
            ]

            if char1 == char2:
                return None

            event = TimelineEvent(
                event_type=EventType.RELATIONSHIP_CHANGE,
                title=f"Relationship evolution between {char1} and {char2}",
                description="Characters' relationship evolved during time passage",
                participants=[char1, char2],
                timestamp=world_state.current_time,
                significance_level=6,
                tags=["evolution", "relationship", "social"],
            )

            # Add to both characters' timelines
            self.timeline_engine.add_event(char1, event)
            self.timeline_engine.add_event(char2, event)

            return event

        except Exception as e:
            logger.error(f"Failed to generate relationship evolution event: {e}")
            return None

    def _generate_daily_life_events(
        self, world_state: WorldState, days: int, event_multiplier: float
    ) -> list[TimelineEvent]:
        """Generate daily life events for characters."""
        events = []

        try:
            max_daily_events = int(
                world_state.get_flag("max_events_per_day", 10) * event_multiplier
            )

            for day in range(days):
                daily_events = 0
                for character_id in world_state.active_characters.keys():
                    if daily_events >= max_daily_events:
                        break

                    # 30% chance of daily life event per character per day
                    if (
                        hash(character_id + str(day) + str(world_state.current_time))
                        % 100
                        < 30
                    ):
                        event = TimelineEvent(
                            event_type=EventType.DAILY_LIFE,
                            title=f"Daily routine: {character_id}",
                            description="Character went about their daily routine",
                            participants=[character_id],
                            timestamp=world_state.current_time
                            - timedelta(days=days - day),
                            significance_level=2,
                            tags=["daily", "routine"],
                        )

                        self.timeline_engine.add_event(character_id, event)
                        events.append(event)
                        daily_events += 1

        except Exception as e:
            logger.error(f"Failed to generate daily life events: {e}")

        return events

    def _generate_environmental_change_events(
        self, world_state: WorldState, time_delta: timedelta, event_multiplier: float
    ) -> list[TimelineEvent]:
        """Generate environmental change events for locations."""
        events = []

        try:
            for location_id in world_state.active_locations.keys():
                # 20% chance of environmental change per location
                if (
                    hash(location_id + str(world_state.current_time)) % 100
                    < 20 * event_multiplier * 100
                ):
                    event = TimelineEvent(
                        event_type=EventType.ENVIRONMENTAL_CHANGE,
                        title=f"Environmental shift: {location_id}",
                        description="Location experienced environmental changes",
                        location_id=location_id,
                        timestamp=world_state.current_time,
                        significance_level=4,
                        tags=["environmental", "change"],
                    )

                    self.timeline_engine.add_event(location_id, event)
                    events.append(event)

        except Exception as e:
            logger.error(f"Failed to generate environmental change events: {e}")

        return events

    def _generate_social_interaction_events(
        self, world_state: WorldState, time_delta: timedelta, event_multiplier: float
    ) -> list[TimelineEvent]:
        """Generate social interaction events between characters."""
        events = []

        try:
            characters = list(world_state.active_characters.keys())
            if len(characters) < 2:
                return events

            # Generate interactions between character pairs
            for i, char1 in enumerate(characters):
                for char2 in characters[i + 1 :]:
                    # 15% chance of interaction per character pair
                    if (
                        hash(char1 + char2 + str(world_state.current_time)) % 100
                        < 15 * event_multiplier * 100
                    ):
                        event = TimelineEvent(
                            event_type=EventType.CONVERSATION,
                            title=f"Conversation: {char1} and {char2}",
                            description="Characters had a conversation",
                            participants=[char1, char2],
                            timestamp=world_state.current_time,
                            significance_level=4,
                            tags=["social", "conversation"],
                        )

                        self.timeline_engine.add_event(char1, event)
                        self.timeline_engine.add_event(char2, event)
                        events.append(event)

        except Exception as e:
            logger.error(f"Failed to generate social interaction events: {e}")

        return events

    def _apply_character_development(
        self, world_state: WorldState, character_id: str, time_delta: timedelta
    ) -> bool:
        """Apply character development over time."""
        try:
            character_data = world_state.active_characters.get(character_id)
            if not character_data:
                return False

            # Simple character development - could be expanded with character system integration
            days_passed = time_delta.total_seconds() / (24 * 3600)

            # Characters develop skills and personality traits over time
            if days_passed >= 7:  # Weekly development
                # Add a skill or trait development
                if "skills" not in character_data:
                    character_data["skills"] = []

                if "personality_traits" not in character_data:
                    character_data["personality_traits"] = {}

                # Simple skill development
                skills = [
                    "communication",
                    "problem_solving",
                    "creativity",
                    "empathy",
                    "resilience",
                ]
                skill = skills[
                    hash(character_id + str(world_state.current_time)) % len(skills)
                ]

                if skill not in character_data["skills"]:
                    character_data["skills"].append(skill)

                    # Create development event
                    event = TimelineEvent(
                        event_type=EventType.LEARNING,
                        title=f"Skill development: {skill}",
                        description=f"Character developed {skill} skill",
                        participants=[character_id],
                        timestamp=world_state.current_time,
                        significance_level=6,
                        tags=["development", "skill", skill],
                    )

                    self.timeline_engine.add_event(character_id, event)
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to apply character development: {e}")
            return False

    # ---- Error Handling and Recovery Methods ----

    def handle_error_with_recovery(
        self, error: Exception, context: dict[str, Any] = None
    ) -> bool:
        """
        Handle an error with automatic recovery using the error handler.

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            bool: True if recovery was successful, False otherwise
        """
        if not self.error_handler:
            logger.error(f"Error handler not available, cannot recover from: {error}")
            return False

        try:
            # Ensure world_id is in context if available
            if context and "world_id" not in context:
                # Try to infer world_id from other context
                entity_id = context.get("entity_id")
                if entity_id and entity_id in self._entity_world_map:
                    context["world_id"] = self._entity_world_map[entity_id]

            result = self.error_handler.handle_error(error, context)

            if result.success:
                logger.info(
                    f"Successfully recovered from error using {result.strategy_used.value}"
                )
                return True
            else:
                logger.error(f"Failed to recover from error: {result.errors}")
                return False

        except Exception as recovery_error:
            logger.error(f"Error during error recovery: {recovery_error}")
            return False

    def create_system_checkpoint(self, world_id: str) -> bool:
        """
        Create a system checkpoint for rollback purposes.

        Args:
            world_id: ID of the world to checkpoint

        Returns:
            bool: True if checkpoint was created successfully
        """
        if not self.error_handler:
            logger.warning("Error handler not available, cannot create checkpoint")
            return False

        try:
            world_state = self.get_world_state(world_id)
            if not world_state:
                logger.error(f"Cannot create checkpoint: world {world_id} not found")
                return False

            checkpoint = self.error_handler.create_checkpoint(world_id, world_state)
            logger.info(
                f"Created checkpoint {checkpoint.checkpoint_id} for world {world_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create checkpoint for world {world_id}: {e}")
            return False

    def validate_world_consistency_with_recovery(self, world_id: str) -> dict[str, Any]:
        """
        Validate world consistency and attempt automatic recovery if issues are found.

        Args:
            world_id: ID of the world to validate

        Returns:
            Dict[str, Any]: Validation report with recovery information
        """
        if not self.error_handler:
            return {
                "world_id": world_id,
                "overall_valid": False,
                "issues": ["Error handler not available"],
                "recovery_attempted": False,
            }

        try:
            # Run consistency validation
            report = self.error_handler.validate_world_consistency(world_id)

            # If issues found, attempt recovery
            if not report["overall_valid"] and report["issues"]:
                logger.warning(
                    f"World {world_id} consistency issues found, attempting recovery"
                )

                # Create a checkpoint before attempting recovery
                self.create_system_checkpoint(world_id)

                # Attempt recovery for each issue
                recovery_results = []
                for issue in report["issues"]:
                    try:
                        # Create a synthetic error for the issue
                        synthetic_error = Exception(f"Consistency issue: {issue}")
                        context = {"world_id": world_id, "component": "world_state"}

                        recovery_result = self.error_handler.handle_error(
                            synthetic_error, context
                        )
                        recovery_results.append(
                            {
                                "issue": issue,
                                "recovery_success": recovery_result.success,
                                "strategy_used": (
                                    recovery_result.strategy_used.value
                                    if recovery_result.strategy_used
                                    else None
                                ),
                                "actions_taken": recovery_result.actions_taken,
                            }
                        )

                    except Exception as recovery_error:
                        recovery_results.append(
                            {
                                "issue": issue,
                                "recovery_success": False,
                                "error": str(recovery_error),
                            }
                        )

                report["recovery_attempted"] = True
                report["recovery_results"] = recovery_results

                # Re-validate after recovery attempts
                post_recovery_report = self.error_handler.validate_world_consistency(
                    world_id
                )
                report["post_recovery_valid"] = post_recovery_report["overall_valid"]
                report["remaining_issues"] = post_recovery_report["issues"]

            return report

        except Exception as e:
            logger.error(f"Error during world consistency validation: {e}")
            return {
                "world_id": world_id,
                "overall_valid": False,
                "issues": [f"Validation failed: {e}"],
                "recovery_attempted": False,
            }

    def get_system_health_status(self) -> dict[str, Any]:
        """
        Get comprehensive system health status including error statistics.

        Returns:
            Dict[str, Any]: System health status report
        """
        if not self.error_handler:
            return {
                "error_handler_available": False,
                "system_health_score": 0.0,
                "status": "degraded",
            }

        try:
            health_score = self.error_handler.health_monitor.get_system_health_score()
            error_stats = self.error_handler.get_error_statistics()
            degradation_issues = self.error_handler.health_monitor.detect_degradation()

            # Determine overall status
            if health_score >= 0.9 and error_stats["recent_errors"] == 0:
                status = "healthy"
            elif health_score >= 0.7 and error_stats["recent_errors"] < 5:
                status = "stable"
            elif health_score >= 0.5:
                status = "degraded"
            else:
                status = "critical"

            return {
                "error_handler_available": True,
                "system_health_score": health_score,
                "status": status,
                "error_statistics": error_stats,
                "degradation_issues": degradation_issues,
                "active_worlds_count": len(self._active_worlds),
                "timeline_count": (
                    self.timeline_engine.get_timeline_count()
                    if hasattr(self.timeline_engine, "get_timeline_count")
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting system health status: {e}")
            return {
                "error_handler_available": True,
                "system_health_score": 0.0,
                "status": "error",
                "error": str(e),
            }

    def cleanup_error_data(self, days: int = 7) -> dict[str, int]:
        """
        Clean up old error data and system checkpoints.

        Args:
            days: Number of days of data to keep

        Returns:
            Dict[str, int]: Cleanup statistics
        """
        if not self.error_handler:
            return {"error": "Error handler not available"}

        try:
            return self.error_handler.cleanup_old_data(days)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {"error": str(e)}

    def enable_graceful_degradation(
        self, world_id: str, reason: str = "manual"
    ) -> bool:
        """
        Manually enable graceful degradation mode for a world.

        Args:
            world_id: ID of the world to degrade
            reason: Reason for enabling degradation

        Returns:
            bool: True if degradation was enabled successfully
        """
        if not self.error_handler:
            logger.warning(
                "Error handler not available, cannot enable graceful degradation"
            )
            return False

        try:
            # Create a synthetic error to trigger graceful degradation
            Exception(f"Manual degradation requested: {reason}")
            context = {"world_id": world_id, "component": "system"}

            result = self.error_handler._graceful_degradation(
                world_id, context, self.error_handler.RecoveryResult()
            )

            if result:
                logger.info(
                    f"Graceful degradation enabled for world {world_id}: {reason}"
                )
                # Set world flag to indicate degraded mode
                if hasattr(self, "admin"):
                    self.admin.set_world_flags(
                        world_id,
                        {
                            "degraded_mode": True,
                            "degradation_reason": reason,
                            "degradation_timestamp": datetime.now().isoformat(),
                        },
                    )

            return result

        except Exception as e:
            logger.error(
                f"Failed to enable graceful degradation for world {world_id}: {e}"
            )
            return False


# Utility functions for testing and validation


def create_default_world_config(world_name: str) -> WorldConfig:
    """Create a default world configuration for testing."""
    return WorldConfig(
        world_name=world_name,
        initial_characters=[
            {
                "id": "char_001",
                "name": "Default Character",
                "description": "A default character for testing",
                "generate_backstory": True,
            }
        ],
        initial_locations=[
            {
                "id": "loc_001",
                "name": "Starting Location",
                "description": "The default starting location",
            }
        ],
        initial_objects=[
            {
                "id": "obj_001",
                "name": "Default Object",
                "description": "A default object for testing",
            }
        ],
        evolution_speed=1.0,
        auto_evolution=True,
        max_timeline_events=1000,
    )


def validate_world_state_manager() -> bool:
    """Validate the WorldStateManager implementation by creating a test instance."""
    try:
        # Create manager with mock dependencies
        WorldStateManager()

        # Test world configuration creation
        config = create_default_world_config("Test World")
        config.validate()

        logger.info("WorldStateManager validation completed successfully")
        return True

    except Exception as e:
        logger.error(f"WorldStateManager validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run validation when script is executed directly
    logging.basicConfig(level=logging.INFO)

    if validate_world_state_manager():
        print("✓ WorldStateManager implementation is valid")
    else:
        print("✗ WorldStateManager implementation has issues")
