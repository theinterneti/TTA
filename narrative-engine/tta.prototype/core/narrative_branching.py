"""
Narrative Branching and Choice Processing for TTA Prototype

This module implements choice option generation, validation logic, narrative branching
based on user choices, and choice consequence tracking with story impact calculation.

Classes:
    ChoiceOption: Represents a choice option available to the user
    ChoiceConsequence: Represents the consequences of a user's choice
    StoryImpact: Tracks the impact of choices on the overall story
    BranchingPoint: Represents a point where the narrative can branch
    NarrativeBranch: Represents a specific narrative branch
    NarrativeBranchingChoice: Main class for managing narrative branching and choices
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ChoiceType(Enum):
    """Types of choices available to users."""
    DIALOGUE = "dialogue"
    ACTION = "action"
    MOVEMENT = "movement"
    THERAPEUTIC = "therapeutic"
    EXPLORATION = "exploration"
    REFLECTION = "reflection"


class ConsequenceType(Enum):
    """Types of consequences that can result from choices."""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    CUMULATIVE = "cumulative"
    THERAPEUTIC = "therapeutic"
    RELATIONSHIP = "relationship"
    WORLD_STATE = "world_state"


class ImpactLevel(Enum):
    """Levels of story impact."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class ChoiceOption:
    """Represents a choice option available to the user."""
    choice_id: str
    choice_text: str
    choice_type: ChoiceType = ChoiceType.DIALOGUE
    therapeutic_weight: float = 0.0  # -1.0 to 1.0, therapeutic value of choice
    emotional_tone: str = "neutral"
    prerequisites: list[str] = field(default_factory=list)  # Required conditions
    consequences: list[str] = field(default_factory=list)  # Predicted consequences
    metadata: dict[str, Any] = field(default_factory=dict)
    available: bool = True

    def validate(self) -> bool:
        """Validate choice option data."""
        if not self.choice_id.strip():
            raise ValueError("Choice ID cannot be empty")
        if not self.choice_text.strip():
            raise ValueError("Choice text cannot be empty")
        if not -1.0 <= self.therapeutic_weight <= 1.0:
            raise ValueError("Therapeutic weight must be between -1.0 and 1.0")
        return True


@dataclass
class ChoiceConsequence:
    """Represents the consequences of a user's choice."""
    consequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    choice_id: str = ""
    consequence_type: ConsequenceType = ConsequenceType.IMMEDIATE
    description: str = ""
    impact_level: ImpactLevel = ImpactLevel.MINOR
    affected_entities: list[str] = field(default_factory=list)  # Characters, locations, etc.
    therapeutic_impact: float = 0.0  # -1.0 to 1.0
    emotional_impact: dict[str, float] = field(default_factory=dict)
    world_state_changes: dict[str, Any] = field(default_factory=dict)
    narrative_flags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate consequence data."""
        if not self.description.strip():
            raise ValueError("Consequence description cannot be empty")
        if not -1.0 <= self.therapeutic_impact <= 1.0:
            raise ValueError("Therapeutic impact must be between -1.0 and 1.0")
        return True


@dataclass
class StoryImpact:
    """Tracks the impact of choices on the overall story."""
    impact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    cumulative_therapeutic_score: float = 0.0
    major_decisions: list[str] = field(default_factory=list)
    character_relationships: dict[str, float] = field(default_factory=dict)
    world_state_flags: dict[str, Any] = field(default_factory=dict)
    narrative_paths_unlocked: list[str] = field(default_factory=list)
    narrative_paths_closed: list[str] = field(default_factory=list)
    emotional_journey: list[dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate story impact data."""
        if not self.session_id.strip():
            raise ValueError("Session ID cannot be empty")
        return True


@dataclass
class BranchingPoint:
    """Represents a point where the narrative can branch."""
    branching_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    narrative_position: int = 0
    location_id: str = ""
    trigger_conditions: list[str] = field(default_factory=list)
    available_branches: list[str] = field(default_factory=list)
    therapeutic_focus: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate branching point data."""
        if self.narrative_position < 0:
            raise ValueError("Narrative position cannot be negative")
        return True


@dataclass
class NarrativeBranch:
    """Represents a specific narrative branch."""
    branch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    branch_name: str = ""
    description: str = ""
    therapeutic_theme: str = ""
    required_choices: list[str] = field(default_factory=list)
    narrative_content: list[str] = field(default_factory=list)
    character_interactions: list[str] = field(default_factory=list)
    therapeutic_opportunities: list[str] = field(default_factory=list)
    completion_criteria: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate narrative branch data."""
        if not self.branch_name.strip():
            raise ValueError("Branch name cannot be empty")
        if not self.description.strip():
            raise ValueError("Branch description cannot be empty")
        return True


class NarrativeBranchingChoice:
    """
    Main class for managing narrative branching and choice processing.

    This class handles choice option generation, validation, narrative branching
    based on user choices, and choice consequence tracking with story impact calculation.
    """

    def __init__(self):
        """Initialize the narrative branching system."""
        self.active_branching_points: dict[str, list[BranchingPoint]] = {}
        self.narrative_branches: dict[str, NarrativeBranch] = {}
        self.story_impacts: dict[str, StoryImpact] = {}
        self.choice_history: dict[str, list[ChoiceConsequence]] = {}

        # Therapeutic choice templates
        self.therapeutic_choice_templates = self._initialize_therapeutic_templates()

        logger.info("NarrativeBranchingChoice system initialized")

    def _initialize_therapeutic_templates(self) -> dict[str, list[ChoiceOption]]:
        """Initialize therapeutic choice templates."""
        return {
            "anxiety_management": [
                ChoiceOption(
                    choice_id="breathing_exercise",
                    choice_text="Take a moment to focus on your breathing",
                    choice_type=ChoiceType.THERAPEUTIC,
                    therapeutic_weight=0.8,
                    emotional_tone="calming",
                    consequences=["reduced_anxiety", "increased_mindfulness"]
                ),
                ChoiceOption(
                    choice_id="grounding_technique",
                    choice_text="Use the 5-4-3-2-1 grounding technique",
                    choice_type=ChoiceType.THERAPEUTIC,
                    therapeutic_weight=0.7,
                    emotional_tone="stabilizing",
                    consequences=["improved_focus", "reduced_overwhelm"]
                )
            ],
            "emotional_regulation": [
                ChoiceOption(
                    choice_id="acknowledge_feelings",
                    choice_text="Acknowledge and name what you're feeling",
                    choice_type=ChoiceType.REFLECTION,
                    therapeutic_weight=0.6,
                    emotional_tone="accepting",
                    consequences=["emotional_awareness", "self_acceptance"]
                ),
                ChoiceOption(
                    choice_id="reframe_thought",
                    choice_text="Try to reframe this situation more positively",
                    choice_type=ChoiceType.THERAPEUTIC,
                    therapeutic_weight=0.7,
                    emotional_tone="hopeful",
                    consequences=["cognitive_flexibility", "improved_mood"]
                )
            ],
            "social_interaction": [
                ChoiceOption(
                    choice_id="express_empathy",
                    choice_text="Express understanding and empathy",
                    choice_type=ChoiceType.DIALOGUE,
                    therapeutic_weight=0.8,
                    emotional_tone="compassionate",
                    consequences=["stronger_relationship", "increased_trust"]
                ),
                ChoiceOption(
                    choice_id="set_boundary",
                    choice_text="Politely set a healthy boundary",
                    choice_type=ChoiceType.DIALOGUE,
                    therapeutic_weight=0.6,
                    emotional_tone="assertive",
                    consequences=["self_respect", "clear_communication"]
                )
            ]
        }

    def generate_choice_options(self, narrative_context: dict[str, Any]) -> list[ChoiceOption]:
        """
        Generate choice options based on the current narrative context.

        Args:
            narrative_context: Current narrative context including location, characters, etc.

        Returns:
            List[ChoiceOption]: Generated choice options
        """
        try:
            session_id = narrative_context.get("session_id", "")
            location_id = narrative_context.get("location_id", "")
            characters_present = narrative_context.get("characters", [])
            emotional_state = narrative_context.get("emotional_state", {})
            therapeutic_opportunities = narrative_context.get("therapeutic_opportunities", [])

            choices = []

            # Generate contextual choices based on location
            choices.extend(self._generate_location_choices(location_id))

            # Generate character interaction choices
            choices.extend(self._generate_character_choices(characters_present))

            # Generate therapeutic choices based on emotional state (prioritize these)
            therapeutic_choices = self._generate_therapeutic_choices(emotional_state, therapeutic_opportunities)

            # Generate exploration choices
            exploration_choices = self._generate_exploration_choices(narrative_context)

            # Combine all choices with therapeutic choices first (for prioritization)
            all_choices = therapeutic_choices + choices + exploration_choices

            # Validate and filter choices, removing duplicates
            valid_choices = []
            seen_choice_ids = set()
            for choice in all_choices:
                if choice.choice_id not in seen_choice_ids and self._validate_choice_prerequisites(choice, narrative_context):
                    choice.validate()
                    valid_choices.append(choice)
                    seen_choice_ids.add(choice.choice_id)

            # Ensure we have at least some basic choices
            if not valid_choices:
                valid_choices = self._generate_fallback_choices()

            logger.info(f"Generated {len(valid_choices)} choice options for session {session_id} (including {len(therapeutic_choices)} therapeutic)")
            return valid_choices[:6]  # Limit to 6 choices to avoid overwhelming the user

        except Exception as e:
            logger.error(f"Error generating choice options: {e}")
            return self._generate_fallback_choices()

    def _generate_location_choices(self, location_id: str) -> list[ChoiceOption]:
        """Generate choices based on current location."""
        choices = []

        if "garden" in location_id.lower():
            choices.extend([
                ChoiceOption(
                    choice_id="examine_flowers",
                    choice_text="Examine the beautiful flowers",
                    choice_type=ChoiceType.EXPLORATION,
                    therapeutic_weight=0.3,
                    emotional_tone="peaceful",
                    consequences=["appreciation", "mindfulness"]
                ),
                ChoiceOption(
                    choice_id="sit_bench",
                    choice_text="Sit on the garden bench and reflect",
                    choice_type=ChoiceType.REFLECTION,
                    therapeutic_weight=0.5,
                    emotional_tone="contemplative",
                    consequences=["self_reflection", "inner_peace"]
                )
            ])
        elif "library" in location_id.lower():
            choices.extend([
                ChoiceOption(
                    choice_id="read_book",
                    choice_text="Pick up an interesting book",
                    choice_type=ChoiceType.EXPLORATION,
                    therapeutic_weight=0.2,
                    emotional_tone="curious",
                    consequences=["knowledge_gain", "mental_stimulation"]
                ),
                ChoiceOption(
                    choice_id="quiet_study",
                    choice_text="Find a quiet corner to think",
                    choice_type=ChoiceType.REFLECTION,
                    therapeutic_weight=0.4,
                    emotional_tone="focused",
                    consequences=["clarity", "concentration"]
                )
            ])
        else:
            # Generic location choices
            choices.extend([
                ChoiceOption(
                    choice_id="look_around",
                    choice_text="Look around carefully",
                    choice_type=ChoiceType.EXPLORATION,
                    therapeutic_weight=0.1,
                    emotional_tone="observant",
                    consequences=["awareness", "discovery"]
                ),
                ChoiceOption(
                    choice_id="move_forward",
                    choice_text="Continue moving forward",
                    choice_type=ChoiceType.MOVEMENT,
                    therapeutic_weight=0.2,
                    emotional_tone="determined",
                    consequences=["progress", "momentum"]
                )
            ])

        return choices

    def _generate_character_choices(self, characters: list[str]) -> list[ChoiceOption]:
        """Generate choices for character interactions."""
        choices = []

        for character in characters:
            choices.extend([
                ChoiceOption(
                    choice_id=f"talk_to_{character}",
                    choice_text=f"Talk to {character}",
                    choice_type=ChoiceType.DIALOGUE,
                    therapeutic_weight=0.4,
                    emotional_tone="social",
                    consequences=["social_connection", "information_gain"]
                ),
                ChoiceOption(
                    choice_id=f"observe_{character}",
                    choice_text=f"Observe {character} quietly",
                    choice_type=ChoiceType.EXPLORATION,
                    therapeutic_weight=0.2,
                    emotional_tone="thoughtful",
                    consequences=["understanding", "empathy"]
                )
            ])

        return choices

    def _generate_therapeutic_choices(self, emotional_state: dict[str, Any],
                                    opportunities: list[str]) -> list[ChoiceOption]:
        """Generate therapeutic choices based on emotional state and opportunities."""
        choices = []

        primary_emotion = emotional_state.get("primary_emotion", "calm")
        intensity = emotional_state.get("intensity", 0.5)

        # High intensity emotions need more therapeutic intervention
        if intensity > 0.7:
            if primary_emotion in ["anxious", "overwhelmed"]:
                choices.extend(self.therapeutic_choice_templates.get("anxiety_management", []))
            elif primary_emotion in ["angry", "frustrated"]:
                choices.extend(self.therapeutic_choice_templates.get("emotional_regulation", []))

        # Add choices based on therapeutic opportunities
        for opportunity in opportunities:
            if "anxiety" in opportunity.lower():
                choices.extend(self.therapeutic_choice_templates.get("anxiety_management", []))
            elif "social" in opportunity.lower():
                choices.extend(self.therapeutic_choice_templates.get("social_interaction", []))
            elif "emotional" in opportunity.lower():
                choices.extend(self.therapeutic_choice_templates.get("emotional_regulation", []))

        return choices

    def _generate_exploration_choices(self, context: dict[str, Any]) -> list[ChoiceOption]:
        """Generate exploration and movement choices."""
        return [
            ChoiceOption(
                choice_id="explore_area",
                choice_text="Explore the surrounding area",
                choice_type=ChoiceType.EXPLORATION,
                therapeutic_weight=0.3,
                emotional_tone="adventurous",
                consequences=["discovery", "confidence"]
            ),
            ChoiceOption(
                choice_id="take_break",
                choice_text="Take a moment to rest and gather your thoughts",
                choice_type=ChoiceType.REFLECTION,
                therapeutic_weight=0.5,
                emotional_tone="restorative",
                consequences=["energy_restoration", "mental_clarity"]
            )
        ]

    def _generate_fallback_choices(self) -> list[ChoiceOption]:
        """Generate basic fallback choices when other generation fails."""
        return [
            ChoiceOption(
                choice_id="continue",
                choice_text="Continue your journey",
                choice_type=ChoiceType.MOVEMENT,
                therapeutic_weight=0.2,
                emotional_tone="determined",
                consequences=["progress"]
            ),
            ChoiceOption(
                choice_id="reflect",
                choice_text="Take time to reflect on your experiences",
                choice_type=ChoiceType.REFLECTION,
                therapeutic_weight=0.6,
                emotional_tone="contemplative",
                consequences=["self_awareness", "insight"]
            ),
            ChoiceOption(
                choice_id="look_around",
                choice_text="Look around your surroundings",
                choice_type=ChoiceType.EXPLORATION,
                therapeutic_weight=0.1,
                emotional_tone="observant",
                consequences=["awareness"]
            )
        ]

    def _validate_choice_prerequisites(self, choice: ChoiceOption, context: dict[str, Any]) -> bool:
        """Validate that choice prerequisites are met."""
        if not choice.prerequisites:
            return True

        # Check each prerequisite
        for prerequisite in choice.prerequisites:
            if prerequisite.startswith("emotion:"):
                required_emotion = prerequisite.split(":")[1]
                current_emotion = context.get("emotional_state", {}).get("primary_emotion", "calm")
                if current_emotion != required_emotion:
                    return False
            elif prerequisite.startswith("location:"):
                required_location = prerequisite.split(":")[1]
                current_location = context.get("location_id", "")
                if required_location not in current_location:
                    return False
            elif prerequisite.startswith("character:"):
                required_character = prerequisite.split(":")[1]
                present_characters = context.get("characters", [])
                if required_character not in present_characters:
                    return False

        return True

    def process_user_choice(self, choice: ChoiceOption, context: dict[str, Any]) -> ChoiceConsequence:
        """
        Process a user's choice and generate consequences.

        Args:
            choice: The choice made by the user
            context: Current narrative context

        Returns:
            ChoiceConsequence: Generated consequences
        """
        try:
            session_id = context.get("session_id", "")

            # Create consequence object
            consequence = ChoiceConsequence(
                choice_id=choice.choice_id,
                description=f"User chose: {choice.choice_text}",
                therapeutic_impact=choice.therapeutic_weight
            )

            # Determine consequence type based on choice type
            if choice.choice_type == ChoiceType.THERAPEUTIC:
                consequence.consequence_type = ConsequenceType.THERAPEUTIC
                consequence.impact_level = ImpactLevel.MODERATE
            elif choice.choice_type == ChoiceType.DIALOGUE:
                consequence.consequence_type = ConsequenceType.RELATIONSHIP
                consequence.impact_level = ImpactLevel.MINOR
            elif choice.choice_type == ChoiceType.MOVEMENT:
                consequence.consequence_type = ConsequenceType.WORLD_STATE
                consequence.impact_level = ImpactLevel.MINOR
            else:
                consequence.consequence_type = ConsequenceType.IMMEDIATE
                consequence.impact_level = ImpactLevel.MINOR

            # Apply specific consequences based on choice
            self._apply_choice_consequences(choice, consequence, context)

            # Update story impact
            self._update_story_impact(session_id, choice, consequence)

            # Store in choice history
            if session_id not in self.choice_history:
                self.choice_history[session_id] = []
            self.choice_history[session_id].append(consequence)

            consequence.validate()
            logger.info(f"Processed choice {choice.choice_id} for session {session_id}")
            return consequence

        except Exception as e:
            logger.error(f"Error processing user choice: {e}")
            # Return a basic consequence
            return ChoiceConsequence(
                choice_id=choice.choice_id,
                description="Choice processed with basic outcome",
                consequence_type=ConsequenceType.IMMEDIATE,
                impact_level=ImpactLevel.MINOR
            )

    def _apply_choice_consequences(self, choice: ChoiceOption, consequence: ChoiceConsequence,
                                 context: dict[str, Any]) -> None:
        """Apply specific consequences based on the choice made."""
        # Apply emotional impact
        if choice.emotional_tone == "calming":
            consequence.emotional_impact["anxiety"] = -0.3
            consequence.emotional_impact["peace"] = 0.4
        elif choice.emotional_tone == "hopeful":
            consequence.emotional_impact["depression"] = -0.2
            consequence.emotional_impact["optimism"] = 0.5
        elif choice.emotional_tone == "assertive":
            consequence.emotional_impact["confidence"] = 0.3
            consequence.emotional_impact["self_respect"] = 0.4

        # Apply world state changes
        if choice.choice_type == ChoiceType.MOVEMENT:
            consequence.world_state_changes["player_moved"] = True
            consequence.world_state_changes["exploration_count"] = context.get("exploration_count", 0) + 1
        elif choice.choice_type == ChoiceType.THERAPEUTIC:
            consequence.world_state_changes["therapeutic_action_taken"] = True
            consequence.world_state_changes["therapeutic_progress"] = context.get("therapeutic_progress", 0) + choice.therapeutic_weight

        # Set narrative flags
        for predicted_consequence in choice.consequences:
            consequence.narrative_flags.append(predicted_consequence)

        # Determine affected entities
        if choice.choice_type == ChoiceType.DIALOGUE:
            characters = context.get("characters", [])
            consequence.affected_entities.extend(characters)
        elif choice.choice_type == ChoiceType.MOVEMENT:
            consequence.affected_entities.append("player_location")

    def _update_story_impact(self, session_id: str, choice: ChoiceOption,
                           consequence: ChoiceConsequence) -> None:
        """Update the overall story impact based on the choice and its consequences."""
        if session_id not in self.story_impacts:
            self.story_impacts[session_id] = StoryImpact(session_id=session_id)

        impact = self.story_impacts[session_id]

        # Update cumulative therapeutic score
        impact.cumulative_therapeutic_score += consequence.therapeutic_impact

        # Track major decisions
        if consequence.impact_level in [ImpactLevel.MAJOR, ImpactLevel.CRITICAL]:
            impact.major_decisions.append(choice.choice_id)

        # Update emotional journey
        emotional_entry = {
            "choice_id": choice.choice_id,
            "emotional_tone": choice.emotional_tone,
            "emotional_impact": consequence.emotional_impact,
            "timestamp": consequence.timestamp.isoformat()
        }
        impact.emotional_journey.append(emotional_entry)

        # Update world state flags
        impact.world_state_flags.update(consequence.world_state_changes)

        impact.last_updated = datetime.now()

    def calculate_story_impact(self, session_id: str) -> StoryImpact | None:
        """
        Calculate the overall story impact for a session.

        Args:
            session_id: Session identifier

        Returns:
            Optional[StoryImpact]: Story impact data or None if session not found
        """
        return self.story_impacts.get(session_id)

    def create_narrative_branch(self, branching_point: BranchingPoint,
                              choice_history: list[ChoiceConsequence]) -> NarrativeBranch | None:
        """
        Create a new narrative branch based on a branching point and choice history.

        Args:
            branching_point: The point where branching occurs
            choice_history: History of choices leading to this point

        Returns:
            Optional[NarrativeBranch]: Created narrative branch or None if creation fails
        """
        try:
            branching_point.validate()

            # Analyze choice history to determine branch characteristics
            therapeutic_choices = [c for c in choice_history if c.consequence_type == ConsequenceType.THERAPEUTIC]
            social_choices = [c for c in choice_history if c.consequence_type == ConsequenceType.RELATIONSHIP]

            # Determine therapeutic theme based on choice patterns
            therapeutic_theme = "general_wellbeing"
            if len(therapeutic_choices) > len(choice_history) * 0.5:
                therapeutic_theme = "intensive_therapy"
            elif len(social_choices) > len(choice_history) * 0.4:
                therapeutic_theme = "social_connection"

            # Create the branch
            branch = NarrativeBranch(
                branch_name=f"Branch_{branching_point.narrative_position}_{therapeutic_theme}",
                description=f"Narrative branch focusing on {therapeutic_theme}",
                therapeutic_theme=therapeutic_theme,
                required_choices=[c.choice_id for c in choice_history[-3:]],  # Last 3 choices
                narrative_content=[
                    f"Your journey has led you to focus on {therapeutic_theme}.",
                    "The path ahead offers new opportunities for growth and understanding."
                ],
                completion_criteria=[
                    "complete_therapeutic_activity",
                    "demonstrate_skill_application",
                    "reflect_on_progress"
                ]
            )

            # Add therapeutic opportunities based on theme
            if therapeutic_theme == "intensive_therapy":
                branch.therapeutic_opportunities.extend([
                    "deep_emotional_processing",
                    "trauma_integration",
                    "coping_skill_development"
                ])
            elif therapeutic_theme == "social_connection":
                branch.therapeutic_opportunities.extend([
                    "relationship_building",
                    "communication_skills",
                    "empathy_development"
                ])
            else:
                branch.therapeutic_opportunities.extend([
                    "self_awareness",
                    "mindfulness_practice",
                    "goal_setting"
                ])

            branch.validate()
            self.narrative_branches[branch.branch_id] = branch

            logger.info(f"Created narrative branch: {branch.branch_name}")
            return branch

        except Exception as e:
            logger.error(f"Error creating narrative branch: {e}")
            return None

    def get_available_branches(self, session_id: str, current_context: dict[str, Any]) -> list[NarrativeBranch]:
        """
        Get available narrative branches for a session.

        Args:
            session_id: Session identifier
            current_context: Current narrative context

        Returns:
            List[NarrativeBranch]: Available narrative branches
        """
        available_branches = []
        choice_history = self.choice_history.get(session_id, [])

        # Check each branch for availability
        for branch in self.narrative_branches.values():
            if self._is_branch_available(branch, choice_history, current_context):
                available_branches.append(branch)

        return available_branches

    def _is_branch_available(self, branch: NarrativeBranch, choice_history: list[ChoiceConsequence],
                           context: dict[str, Any]) -> bool:
        """Check if a narrative branch is available based on requirements."""
        # Check if required choices have been made
        made_choices = {c.choice_id for c in choice_history}
        required_choices = set(branch.required_choices)

        if not required_choices.issubset(made_choices):
            return False

        # Additional availability checks can be added here
        # (e.g., therapeutic progress thresholds, emotional state requirements)

        return True

    def get_choice_history(self, session_id: str) -> list[ChoiceConsequence]:
        """
        Get the choice history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List[ChoiceConsequence]: Choice history
        """
        return self.choice_history.get(session_id, [])

    def clear_session_data(self, session_id: str) -> bool:
        """
        Clear all data for a session.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if data was cleared successfully
        """
        try:
            if session_id in self.choice_history:
                del self.choice_history[session_id]
            if session_id in self.story_impacts:
                del self.story_impacts[session_id]
            if session_id in self.active_branching_points:
                del self.active_branching_points[session_id]

            logger.info(f"Cleared session data for {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing session data: {e}")
            return False
