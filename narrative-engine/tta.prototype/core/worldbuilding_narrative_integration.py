"""
Worldbuilding and Narrative Integration for TTA Prototype

This module implements the integration between worldbuilding and narrative progression,
connecting world state changes with story progression, implementing location unlocking
and exploration mechanics, and adding world evolution based on user actions and
therapeutic progress.

Classes:
    NarrativeWorldIntegrator: Main class for integrating worldbuilding with narrative progression
    LocationUnlockCondition: Represents conditions for unlocking locations
    WorldEvolutionEvent: Represents events that cause world evolution
    ExplorationMechanic: Handles location exploration mechanics
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Import existing components
try:
    from ..models.data_models import (
        NarrativeContext,
        NarrativeEvent,
        SessionState,
        TherapeuticProgress,
        UserChoice,
    )
    from .interactive_narrative_engine import InteractiveNarrativeEngine
    from .narrative_branching import NarrativeBranchingChoice, StoryImpact
    from .worldbuilding_setting_management import (
        LocationDetails,
        LocationType,
        WorldbuildingSettingManagement,
        WorldChange,
        WorldChangeType,
    )
except ImportError:
    # Fallback for direct execution
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # Minimal fallback classes
    from dataclasses import dataclass, field
    from datetime import datetime
    from enum import Enum
    from typing import Any

    from interactive_narrative_engine import InteractiveNarrativeEngine
    from narrative_branching import NarrativeBranchingChoice
    from worldbuilding_setting_management import (
        WorldbuildingSettingManagement,
        WorldChange,
        WorldChangeType,
    )

    @dataclass
    class SessionState:
        session_id: str = ""
        user_id: str = ""
        current_location_id: str = ""
        narrative_position: int = 0
        therapeutic_progress: Any = None

    @dataclass
    class NarrativeContext:
        session_id: str = ""
        current_location_id: str = ""
        therapeutic_opportunities: list[str] = field(default_factory=list)

    @dataclass
    class TherapeuticProgress:
        user_id: str = ""
        overall_progress_score: float = 0.0
        therapeutic_goals: list = field(default_factory=list)

    @dataclass
    class UserChoice:
        choice_id: str = ""
        choice_text: str = ""
        therapeutic_weight: float = 0.0

    @dataclass
    class NarrativeEvent:
        event_id: str = ""
        event_type: str = ""
        description: str = ""

logger = logging.getLogger(__name__)


class UnlockConditionType(Enum):
    """Types of conditions for unlocking locations."""
    THERAPEUTIC_PROGRESS = "therapeutic_progress"
    STORY_MILESTONE = "story_milestone"
    CHARACTER_RELATIONSHIP = "character_relationship"
    USER_CHOICE_HISTORY = "user_choice_history"
    EMOTIONAL_STATE = "emotional_state"
    TIME_BASED = "time_based"
    EXPLORATION_COUNT = "exploration_count"


class WorldEvolutionTrigger(Enum):
    """Triggers for world evolution events."""
    USER_ACTION = "user_action"
    THERAPEUTIC_BREAKTHROUGH = "therapeutic_breakthrough"
    STORY_PROGRESSION = "story_progression"
    CHARACTER_DEVELOPMENT = "character_development"
    TIME_PASSAGE = "time_passage"
    EMOTIONAL_CHANGE = "emotional_change"


class ExplorationReward(Enum):
    """Types of rewards for exploration."""
    THERAPEUTIC_INSIGHT = "therapeutic_insight"
    CHARACTER_INTERACTION = "character_interaction"
    STORY_REVELATION = "story_revelation"
    SKILL_DEVELOPMENT = "skill_development"
    EMOTIONAL_GROWTH = "emotional_growth"


@dataclass
class LocationUnlockCondition:
    """Represents conditions for unlocking locations."""
    condition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    condition_type: UnlockConditionType = UnlockConditionType.STORY_MILESTONE
    description: str = ""
    target_value: Any = None
    current_value: Any = None
    check_function: Callable | None = None
    therapeutic_relevance: float = 0.0  # 0.0 to 1.0
    narrative_importance: float = 0.0  # 0.0 to 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_satisfied(self, session_state: SessionState, context: NarrativeContext) -> bool:
        """Check if the unlock condition is satisfied."""
        if self.check_function:
            return self.check_function(session_state, context, self)

        # Default condition checking logic
        if self.condition_type == UnlockConditionType.THERAPEUTIC_PROGRESS:
            if session_state.therapeutic_progress:
                return session_state.therapeutic_progress.overall_progress_score >= self.target_value
        elif self.condition_type == UnlockConditionType.STORY_MILESTONE:
            return session_state.narrative_position >= self.target_value
        elif self.condition_type == UnlockConditionType.EXPLORATION_COUNT:
            # Check if user has explored enough locations
            explored_count = len(getattr(session_state, 'visited_locations', []))
            return explored_count >= self.target_value

        return False


@dataclass
class WorldEvolutionEvent:
    """Represents events that cause world evolution."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger: WorldEvolutionTrigger = WorldEvolutionTrigger.USER_ACTION
    description: str = ""
    affected_locations: list[str] = field(default_factory=list)
    world_changes: list[WorldChange] = field(default_factory=list)
    narrative_consequences: list[str] = field(default_factory=list)
    therapeutic_impact: float = 0.0  # -1.0 to 1.0
    permanence: bool = True  # Whether changes are permanent
    timestamp: datetime = field(default_factory=datetime.now)

    def apply_evolution(self, world_manager: WorldbuildingSettingManagement) -> bool:
        """Apply the world evolution event."""
        try:
            success = world_manager.update_world_state(self.world_changes)
            if success:
                logger.info(f"Applied world evolution event: {self.description}")
            return success
        except Exception as e:
            logger.error(f"Failed to apply world evolution event {self.event_id}: {e}")
            return False


@dataclass
class ExplorationMechanic:
    """Handles location exploration mechanics."""
    mechanic_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    location_id: str = ""
    exploration_requirements: list[str] = field(default_factory=list)
    exploration_rewards: list[ExplorationReward] = field(default_factory=list)
    discovery_content: dict[str, Any] = field(default_factory=dict)
    therapeutic_benefits: list[str] = field(default_factory=list)
    narrative_revelations: list[str] = field(default_factory=list)
    exploration_count: int = 0
    max_explorations: int = 3  # How many times location can be explored

    def can_explore(self, session_state: SessionState) -> bool:
        """Check if location can be explored."""
        if self.exploration_count >= self.max_explorations:
            return False

        # Check requirements
        for requirement in self.exploration_requirements:
            if not self._check_requirement(requirement, session_state):
                return False

        return True

    def _check_requirement(self, requirement: str, session_state: SessionState) -> bool:
        """Check a specific exploration requirement."""
        if requirement.startswith("therapeutic_progress:"):
            min_progress = float(requirement.split(":")[1])
            if session_state.therapeutic_progress:
                return session_state.therapeutic_progress.overall_progress_score >= min_progress
        elif requirement.startswith("narrative_position:"):
            min_position = int(requirement.split(":")[1])
            return session_state.narrative_position >= min_position
        elif requirement.startswith("visited_locations:"):
            min_visited = int(requirement.split(":")[1])
            visited_count = len(getattr(session_state, 'visited_locations', []))
            return visited_count >= min_visited

        return True

    def explore(self, session_state: SessionState) -> dict[str, Any]:
        """Perform exploration and return results."""
        if not self.can_explore(session_state):
            return {"success": False, "message": "Exploration not available"}

        self.exploration_count += 1

        # Generate exploration results
        results = {
            "success": True,
            "exploration_count": self.exploration_count,
            "discoveries": [],
            "therapeutic_benefits": [],
            "narrative_content": []
        }

        # Add discoveries based on exploration count
        if self.exploration_count == 1:
            results["discoveries"] = self.discovery_content.get("first_visit", [])
        elif self.exploration_count == 2:
            results["discoveries"] = self.discovery_content.get("second_visit", [])
        else:
            results["discoveries"] = self.discovery_content.get("deeper_exploration", [])

        # Add therapeutic benefits
        results["therapeutic_benefits"] = self.therapeutic_benefits[:self.exploration_count]

        # Add narrative revelations
        results["narrative_content"] = self.narrative_revelations[:self.exploration_count]

        return results


class NarrativeWorldIntegrator:
    """
    Main class for integrating worldbuilding with narrative progression.

    This class connects world state changes with story progression, implements
    location unlocking and exploration mechanics, and manages world evolution
    based on user actions and therapeutic progress.
    """

    def __init__(self,
                 world_manager: WorldbuildingSettingManagement,
                 narrative_engine: InteractiveNarrativeEngine | None = None,
                 branching_system: NarrativeBranchingChoice | None = None):
        """
        Initialize the narrative world integrator.

        Args:
            world_manager: Worldbuilding and setting management system
            narrative_engine: Interactive narrative engine
            branching_system: Narrative branching and choice system
        """
        self.world_manager = world_manager
        self.narrative_engine = narrative_engine
        self.branching_system = branching_system

        # Integration state
        self.unlock_conditions: dict[str, list[LocationUnlockCondition]] = {}
        self.exploration_mechanics: dict[str, ExplorationMechanic] = {}
        self.evolution_events: list[WorldEvolutionEvent] = []
        self.location_progression_map: dict[str, list[str]] = {}  # location -> unlocked locations

        # Tracking
        self.user_exploration_history: dict[str, list[str]] = {}  # user_id -> explored locations
        self.world_evolution_history: list[WorldEvolutionEvent] = []

        logger.info("NarrativeWorldIntegrator initialized")

    def connect_world_state_with_story_progression(self,
                                                  session_state: SessionState,
                                                  narrative_event: NarrativeEvent) -> list[WorldChange]:
        """
        Connect world state changes with story progression.

        Args:
            session_state: Current session state
            narrative_event: Narrative event that occurred

        Returns:
            List[WorldChange]: World changes triggered by story progression
        """
        logger.info(f"Connecting world state with story progression for event: {narrative_event.event_type}")

        world_changes = []

        # Analyze narrative event for world impact
        if narrative_event.event_type == "therapeutic_breakthrough":
            world_changes.extend(self._handle_therapeutic_breakthrough(session_state, narrative_event))
        elif narrative_event.event_type == "character_interaction":
            world_changes.extend(self._handle_character_interaction(session_state, narrative_event))
        elif narrative_event.event_type == "story_milestone":
            world_changes.extend(self._handle_story_milestone(session_state, narrative_event))
        elif narrative_event.event_type == "emotional_change":
            world_changes.extend(self._handle_emotional_change(session_state, narrative_event))
        elif narrative_event.event_type == "location_visit":
            world_changes.extend(self._handle_location_visit(session_state, narrative_event))

        # Apply world changes
        if world_changes:
            success = self.world_manager.update_world_state(world_changes)
            if success:
                logger.info(f"Applied {len(world_changes)} world changes from story progression")
            else:
                logger.error("Failed to apply world changes from story progression")

        return world_changes

    def _handle_therapeutic_breakthrough(self,
                                       session_state: SessionState,
                                       narrative_event: NarrativeEvent) -> list[WorldChange]:
        """Handle world changes from therapeutic breakthroughs."""
        world_changes = []

        # Therapeutic breakthroughs can unlock new areas or modify existing ones
        current_location = self.world_manager.get_location_details(session_state.current_location_id)
        if current_location:
            # Enhance therapeutic opportunities in current location
            change = WorldChange(
                change_type=WorldChangeType.LOCATION_MODIFY,
                target_location_id=session_state.current_location_id,
                description="Enhanced therapeutic opportunities after breakthrough",
                changes={
                    "therapeutic_opportunities": current_location.therapeutic_opportunities + [
                        "breakthrough_reflection",
                        "progress_celebration",
                        "skill_reinforcement"
                    ]
                },
                therapeutic_impact="Positive therapeutic breakthrough integration",
                narrative_justification="User's therapeutic progress opens new possibilities"
            )
            world_changes.append(change)

        # Check for location unlocks based on therapeutic progress
        unlocked_locations = self._check_therapeutic_unlocks(session_state)
        for location_id in unlocked_locations:
            unlock_change = WorldChange(
                change_type=WorldChangeType.LOCATION_UNLOCK,
                target_location_id=location_id,
                description="Location unlocked due to therapeutic breakthrough",
                changes={"unlock_conditions": []},
                therapeutic_impact="Therapeutic progress enables exploration",
                narrative_justification="Personal growth opens new paths"
            )
            world_changes.append(unlock_change)

        return world_changes

    def _handle_character_interaction(self,
                                    session_state: SessionState,
                                    narrative_event: NarrativeEvent) -> list[WorldChange]:
        """Handle world changes from character interactions."""
        world_changes = []

        # Character interactions can modify the environment
        current_location = self.world_manager.get_location_details(session_state.current_location_id)
        if current_location:
            # Add character presence to location
            change = WorldChange(
                change_type=WorldChangeType.ENVIRONMENT_SHIFT,
                target_location_id=session_state.current_location_id,
                description="Environment influenced by character interaction",
                changes={
                    "environmental_factors": {
                        **current_location.environmental_factors,
                        "character_presence": narrative_event.description,
                        "social_energy": "enhanced"
                    }
                },
                therapeutic_impact="Social interaction enhances environment",
                narrative_justification="Character interactions leave lasting impressions"
            )
            world_changes.append(change)

        return world_changes

    def _handle_story_milestone(self,
                              session_state: SessionState,
                              narrative_event: NarrativeEvent) -> list[WorldChange]:
        """Handle world changes from story milestones."""
        world_changes = []

        # Story milestones can unlock new areas and modify world state
        milestone_unlocks = self._check_milestone_unlocks(session_state, narrative_event)
        for location_id in milestone_unlocks:
            unlock_change = WorldChange(
                change_type=WorldChangeType.LOCATION_UNLOCK,
                target_location_id=location_id,
                description=f"Location unlocked by story milestone: {narrative_event.description}",
                changes={"unlock_conditions": []},
                therapeutic_impact="Story progress enables new experiences",
                narrative_justification=f"Milestone achievement: {narrative_event.description}"
            )
            world_changes.append(unlock_change)

        return world_changes

    def _handle_emotional_change(self,
                               session_state: SessionState,
                               narrative_event: NarrativeEvent) -> list[WorldChange]:
        """Handle world changes from emotional state changes."""
        world_changes = []

        # Emotional changes can affect environmental perception
        current_location = self.world_manager.get_location_details(session_state.current_location_id)
        if current_location:
            # Modify atmosphere based on emotional state
            new_atmosphere = self._determine_atmosphere_from_emotion(narrative_event.description)
            if new_atmosphere != current_location.atmosphere:
                change = WorldChange(
                    change_type=WorldChangeType.ENVIRONMENT_SHIFT,
                    target_location_id=session_state.current_location_id,
                    description="Atmosphere shifted due to emotional change",
                    changes={"atmosphere": new_atmosphere},
                    therapeutic_impact="Environment reflects emotional state",
                    narrative_justification="Emotional state influences perception of surroundings"
                )
                world_changes.append(change)

        return world_changes

    def _handle_location_visit(self,
                             session_state: SessionState,
                             narrative_event: NarrativeEvent) -> list[WorldChange]:
        """Handle world changes from location visits."""
        world_changes = []

        # Track user exploration
        user_id = session_state.user_id
        if user_id not in self.user_exploration_history:
            self.user_exploration_history[user_id] = []

        if session_state.current_location_id not in self.user_exploration_history[user_id]:
            self.user_exploration_history[user_id].append(session_state.current_location_id)

            # First visit to location might trigger changes
            first_visit_changes = self._get_first_visit_changes(session_state.current_location_id)
            world_changes.extend(first_visit_changes)

        return world_changes

    def implement_location_unlocking_mechanics(self,
                                             location_id: str,
                                             unlock_conditions: list[LocationUnlockCondition]) -> bool:
        """
        Implement location unlocking mechanics.

        Args:
            location_id: Location to set unlock conditions for
            unlock_conditions: List of conditions that must be met to unlock

        Returns:
            bool: True if mechanics were implemented successfully
        """
        logger.info(f"Implementing unlock mechanics for location: {location_id}")

        try:
            # Validate location exists
            location = self.world_manager.get_location_details(location_id)
            if not location:
                logger.error(f"Cannot implement unlock mechanics for non-existent location: {location_id}")
                return False

            # Store unlock conditions
            self.unlock_conditions[location_id] = unlock_conditions

            # Update location with unlock conditions
            condition_descriptions = [condition.description for condition in unlock_conditions]
            world_change = WorldChange(
                change_type=WorldChangeType.LOCATION_MODIFY,
                target_location_id=location_id,
                description="Added unlock conditions to location",
                changes={"unlock_conditions": condition_descriptions},
                therapeutic_impact="Structured progression supports therapeutic goals",
                narrative_justification="Certain areas require preparation before exploration"
            )

            success = self.world_manager.update_world_state([world_change])
            if success:
                logger.info(f"Successfully implemented unlock mechanics for {location_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to implement unlock mechanics for {location_id}: {e}")
            return False

    def implement_exploration_mechanics(self,
                                      location_id: str,
                                      exploration_mechanic: ExplorationMechanic) -> bool:
        """
        Implement exploration mechanics for a location.

        Args:
            location_id: Location to add exploration mechanics to
            exploration_mechanic: Exploration mechanic configuration

        Returns:
            bool: True if mechanics were implemented successfully
        """
        logger.info(f"Implementing exploration mechanics for location: {location_id}")

        try:
            # Validate location exists
            location = self.world_manager.get_location_details(location_id)
            if not location:
                logger.error(f"Cannot implement exploration mechanics for non-existent location: {location_id}")
                return False

            # Store exploration mechanics
            exploration_mechanic.location_id = location_id
            self.exploration_mechanics[location_id] = exploration_mechanic

            # Update location with exploration opportunities
            world_change = WorldChange(
                change_type=WorldChangeType.LOCATION_MODIFY,
                target_location_id=location_id,
                description="Added exploration mechanics to location",
                changes={
                    "available_actions": location.available_actions + ["explore", "investigate", "discover"],
                    "exploration_opportunities": len(exploration_mechanic.exploration_rewards)
                },
                therapeutic_impact="Exploration opportunities support discovery and growth",
                narrative_justification="Deeper exploration reveals hidden aspects of the location"
            )

            success = self.world_manager.update_world_state([world_change])
            if success:
                logger.info(f"Successfully implemented exploration mechanics for {location_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to implement exploration mechanics for {location_id}: {e}")
            return False

    def add_world_evolution_based_on_user_actions(self,
                                                session_state: SessionState,
                                                user_choice: UserChoice,
                                                therapeutic_progress: TherapeuticProgress) -> list[WorldEvolutionEvent]:
        """
        Add world evolution based on user actions and therapeutic progress.

        Args:
            session_state: Current session state
            user_choice: User's recent choice
            therapeutic_progress: Current therapeutic progress

        Returns:
            List[WorldEvolutionEvent]: Evolution events triggered by user actions
        """
        logger.info("Evaluating world evolution based on user actions and therapeutic progress")

        evolution_events = []

        # Analyze user choice for world impact
        if user_choice.therapeutic_weight > 0.5:
            # Positive therapeutic choice can improve environments
            evolution_event = self._create_positive_evolution_event(session_state, user_choice)
            if evolution_event:
                evolution_events.append(evolution_event)
        elif user_choice.therapeutic_weight < -0.5:
            # Negative therapeutic choice might create challenges
            evolution_event = self._create_challenge_evolution_event(session_state, user_choice)
            if evolution_event:
                evolution_events.append(evolution_event)

        # Check therapeutic progress milestones
        if therapeutic_progress.overall_progress_score > 0.7:
            # High progress unlocks advanced areas
            evolution_event = self._create_progress_evolution_event(session_state, therapeutic_progress)
            if evolution_event:
                evolution_events.append(evolution_event)

        # Apply evolution events
        for event in evolution_events:
            success = event.apply_evolution(self.world_manager)
            if success:
                self.world_evolution_history.append(event)
                logger.info(f"Applied world evolution event: {event.description}")

        return evolution_events

    def check_location_unlock_conditions(self,
                                       session_state: SessionState,
                                       context: NarrativeContext) -> list[str]:
        """
        Check which locations can be unlocked based on current conditions.

        Args:
            session_state: Current session state
            context: Current narrative context

        Returns:
            List[str]: List of location IDs that can be unlocked
        """
        unlockable_locations = []

        for location_id, conditions in self.unlock_conditions.items():
            # Check if all conditions are satisfied
            all_satisfied = True
            for condition in conditions:
                if not condition.is_satisfied(session_state, context):
                    all_satisfied = False
                    break

            if all_satisfied:
                unlockable_locations.append(location_id)
                logger.info(f"Location {location_id} can be unlocked")

        return unlockable_locations

    def perform_location_exploration(self,
                                   location_id: str,
                                   session_state: SessionState) -> dict[str, Any]:
        """
        Perform location exploration and return results.

        Args:
            location_id: Location to explore
            session_state: Current session state

        Returns:
            Dict[str, Any]: Exploration results
        """
        logger.info(f"Performing exploration of location: {location_id}")

        if location_id not in self.exploration_mechanics:
            return {
                "success": False,
                "message": "No exploration mechanics available for this location"
            }

        exploration_mechanic = self.exploration_mechanics[location_id]
        results = exploration_mechanic.explore(session_state)

        if results["success"]:
            # Track exploration in user history
            user_id = session_state.user_id
            if user_id not in self.user_exploration_history:
                self.user_exploration_history[user_id] = []

            exploration_key = f"{location_id}:exploration_{exploration_mechanic.exploration_count}"
            if exploration_key not in self.user_exploration_history[user_id]:
                self.user_exploration_history[user_id].append(exploration_key)

            logger.info(f"Successful exploration of {location_id} (count: {exploration_mechanic.exploration_count})")

        return results

    def get_world_evolution_summary(self, user_id: str) -> dict[str, Any]:
        """
        Get a summary of world evolution for a specific user.

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: World evolution summary
        """
        user_events = [event for event in self.world_evolution_history
                      if any(change.target_location_id in self.user_exploration_history.get(user_id, [])
                            for change in event.world_changes)]

        summary = {
            "total_evolution_events": len(user_events),
            "locations_affected": len({change.target_location_id
                                        for event in user_events
                                        for change in event.world_changes}),
            "therapeutic_impact_total": sum(event.therapeutic_impact for event in user_events),
            "exploration_count": len(self.user_exploration_history.get(user_id, [])),
            "recent_events": [
                {
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat(),
                    "therapeutic_impact": event.therapeutic_impact
                }
                for event in user_events[-5:]  # Last 5 events
            ]
        }

        return summary

    # Helper methods
    def _check_therapeutic_unlocks(self, session_state: SessionState) -> list[str]:
        """Check for locations unlocked by therapeutic progress."""
        unlocked = []

        if session_state.therapeutic_progress:
            progress_score = session_state.therapeutic_progress.overall_progress_score

            # Example unlock logic based on therapeutic progress
            if progress_score >= 0.3 and "mindfulness_garden" not in self.user_exploration_history.get(session_state.user_id, []):
                unlocked.append("mindfulness_garden")
            if progress_score >= 0.6 and "courage_mountain" not in self.user_exploration_history.get(session_state.user_id, []):
                unlocked.append("courage_mountain")
            if progress_score >= 0.8 and "wisdom_library" not in self.user_exploration_history.get(session_state.user_id, []):
                unlocked.append("wisdom_library")

        return unlocked

    def _check_milestone_unlocks(self, session_state: SessionState, narrative_event: NarrativeEvent) -> list[str]:
        """Check for locations unlocked by story milestones."""
        unlocked = []

        # Example milestone unlock logic
        if "first_therapeutic_breakthrough" in narrative_event.description:
            unlocked.append("reflection_sanctuary")
        elif "character_bond_formed" in narrative_event.description:
            unlocked.append("friendship_grove")
        elif "major_challenge_overcome" in narrative_event.description:
            unlocked.append("victory_peak")

        return unlocked

    def _determine_atmosphere_from_emotion(self, emotion_description: str) -> str:
        """Determine location atmosphere based on emotional state."""
        emotion_lower = emotion_description.lower()

        if "calm" in emotion_lower or "peaceful" in emotion_lower:
            return "peaceful"
        elif "anxious" in emotion_lower or "worried" in emotion_lower:
            return "tense"
        elif "excited" in emotion_lower or "hopeful" in emotion_lower:
            return "welcoming"
        elif "sad" in emotion_lower or "depressed" in emotion_lower:
            return "melancholy"
        elif "angry" in emotion_lower or "frustrated" in emotion_lower:
            return "stormy"
        else:
            return "neutral"

    def _get_first_visit_changes(self, location_id: str) -> list[WorldChange]:
        """Get world changes triggered by first visit to a location."""
        changes = []

        # Example: First visit might reveal hidden aspects
        change = WorldChange(
            change_type=WorldChangeType.LORE_UPDATE,
            target_location_id=location_id,
            description="First visit reveals location history",
            changes={
                "lore_elements": [
                    "You sense the history of this place as you explore it for the first time.",
                    "This location holds memories of others who have walked this path."
                ]
            },
            therapeutic_impact="Discovery enhances connection to the therapeutic journey",
            narrative_justification="First impressions reveal deeper truths about places"
        )
        changes.append(change)

        return changes

    def _create_positive_evolution_event(self, session_state: SessionState, user_choice: UserChoice) -> WorldEvolutionEvent | None:
        """Create a positive world evolution event based on therapeutic choice."""
        current_location = self.world_manager.get_location_details(session_state.current_location_id)
        if not current_location:
            return None

        # Positive choices can enhance the environment
        world_change = WorldChange(
            change_type=WorldChangeType.ENVIRONMENT_SHIFT,
            target_location_id=session_state.current_location_id,
            description="Environment enhanced by positive therapeutic choice",
            changes={
                "environmental_factors": {
                    **current_location.environmental_factors,
                    "positive_energy": "enhanced",
                    "therapeutic_resonance": "strengthened"
                },
                "safety_level": min(1.0, current_location.safety_level + 0.1)
            },
            therapeutic_impact="Positive choices create supportive environments",
            narrative_justification="Your positive actions ripple through the environment"
        )

        return WorldEvolutionEvent(
            trigger=WorldEvolutionTrigger.USER_ACTION,
            description=f"Positive therapeutic choice enhanced {current_location.name}",
            affected_locations=[session_state.current_location_id],
            world_changes=[world_change],
            therapeutic_impact=user_choice.therapeutic_weight,
            permanence=True
        )

    def _create_challenge_evolution_event(self, session_state: SessionState, user_choice: UserChoice) -> WorldEvolutionEvent | None:
        """Create a challenge evolution event based on difficult choice."""
        current_location = self.world_manager.get_location_details(session_state.current_location_id)
        if not current_location:
            return None

        # Challenging choices might create learning opportunities
        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_MODIFY,
            target_location_id=session_state.current_location_id,
            description="Challenge created by difficult choice",
            changes={
                "therapeutic_opportunities": current_location.therapeutic_opportunities + [
                    "reflection_on_choices",
                    "learning_from_difficulty",
                    "growth_through_challenge"
                ]
            },
            therapeutic_impact="Challenges create opportunities for growth",
            narrative_justification="Difficult choices reveal new paths for learning"
        )

        return WorldEvolutionEvent(
            trigger=WorldEvolutionTrigger.USER_ACTION,
            description=f"Challenging choice created growth opportunity in {current_location.name}",
            affected_locations=[session_state.current_location_id],
            world_changes=[world_change],
            therapeutic_impact=abs(user_choice.therapeutic_weight),  # Convert negative to positive learning
            permanence=True
        )

    def _create_progress_evolution_event(self, session_state: SessionState, therapeutic_progress: TherapeuticProgress) -> WorldEvolutionEvent | None:
        """Create evolution event based on therapeutic progress milestone."""
        # High progress can unlock advanced therapeutic environments
        advanced_location_id = "advanced_therapeutic_space"

        world_change = WorldChange(
            change_type=WorldChangeType.LOCATION_UNLOCK,
            target_location_id=advanced_location_id,
            description="Advanced therapeutic space unlocked by progress",
            changes={"unlock_conditions": []},
            therapeutic_impact="Progress unlocks advanced therapeutic opportunities",
            narrative_justification="Your growth has prepared you for deeper therapeutic work"
        )

        return WorldEvolutionEvent(
            trigger=WorldEvolutionTrigger.THERAPEUTIC_BREAKTHROUGH,
            description="Therapeutic progress unlocked advanced therapeutic space",
            affected_locations=[advanced_location_id],
            world_changes=[world_change],
            therapeutic_impact=0.8,
            permanence=True
        )


# Utility functions for creating common unlock conditions and exploration mechanics

def create_therapeutic_progress_condition(min_progress: float, description: str) -> LocationUnlockCondition:
    """Create a therapeutic progress unlock condition."""
    return LocationUnlockCondition(
        condition_type=UnlockConditionType.THERAPEUTIC_PROGRESS,
        description=description,
        target_value=min_progress,
        therapeutic_relevance=1.0,
        narrative_importance=0.8
    )

def create_story_milestone_condition(min_position: int, description: str) -> LocationUnlockCondition:
    """Create a story milestone unlock condition."""
    return LocationUnlockCondition(
        condition_type=UnlockConditionType.STORY_MILESTONE,
        description=description,
        target_value=min_position,
        therapeutic_relevance=0.6,
        narrative_importance=1.0
    )

def create_exploration_condition(min_explorations: int, description: str) -> LocationUnlockCondition:
    """Create an exploration count unlock condition."""
    return LocationUnlockCondition(
        condition_type=UnlockConditionType.EXPLORATION_COUNT,
        description=description,
        target_value=min_explorations,
        therapeutic_relevance=0.7,
        narrative_importance=0.9
    )

def create_basic_exploration_mechanic(location_id: str,
                                    therapeutic_themes: list[str],
                                    max_explorations: int = 3) -> ExplorationMechanic:
    """Create a basic exploration mechanic for a location."""
    return ExplorationMechanic(
        location_id=location_id,
        exploration_requirements=[],
        exploration_rewards=[
            ExplorationReward.THERAPEUTIC_INSIGHT,
            ExplorationReward.STORY_REVELATION,
            ExplorationReward.EMOTIONAL_GROWTH
        ],
        discovery_content={
            "first_visit": [f"You discover the peaceful nature of this {location_id}"],
            "second_visit": ["Deeper exploration reveals hidden therapeutic opportunities"],
            "deeper_exploration": ["You find profound insights in the depths of this space"]
        },
        therapeutic_benefits=therapeutic_themes,
        narrative_revelations=[
            "This place holds significance in your therapeutic journey",
            "The environment here supports your personal growth",
            "You feel a deep connection to this therapeutic space"
        ],
        max_explorations=max_explorations
    )


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    # This would normally be integrated with the full TTA system
    print("NarrativeWorldIntegrator module loaded successfully")
    print("This module provides integration between worldbuilding and narrative progression")
