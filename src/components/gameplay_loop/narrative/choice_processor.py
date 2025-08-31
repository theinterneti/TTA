"""
Choice Processor for Narrative Engine

This module handles user choice processing, validation, and consequence
application for therapeutic narrative experiences.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.gameplay_loop.models.core import (
    ChoiceType,
    ConsequenceSet,
    UserChoice,
)
from src.components.gameplay_loop.services.session_state import SessionState

from .adaptive_difficulty_engine import AdaptiveDifficultyEngine
from .character_development_system import CharacterDevelopmentSystem, DevelopmentTrigger
from .consequence_system import ConsequenceGenerationContext, ConsequenceSystem
from .events import EventType, create_choice_event
from .therapeutic_integration_system import (
    IntegrationStrategy,
    TherapeuticIntegrationSystem,
)

logger = logging.getLogger(__name__)


class ChoiceValidationResult(str, Enum):
    """Choice validation results."""

    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    SAFETY_CONCERN = "safety_concern"
    THERAPEUTIC_MISMATCH = "therapeutic_mismatch"


@dataclass
class ChoiceContext:
    """Context for choice processing."""

    choice: UserChoice
    session_state: SessionState
    validation_result: ChoiceValidationResult = ChoiceValidationResult.VALID
    validation_issues: list[str] = field(default_factory=list)

    # Processing metadata
    processed_at: datetime | None = None
    processing_time: timedelta = field(default=timedelta())
    consequences_applied: list[str] = field(default_factory=list)

    # Therapeutic analysis
    therapeutic_alignment: float = field(default=0.0)
    skill_practice_opportunity: str | None = None
    emotional_impact: dict[str, float] = field(default_factory=dict)
    progress_impact: dict[str, float] = field(default_factory=dict)

    # Safety analysis
    safety_score: float = field(default=1.0)
    risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)


@dataclass
class ChoiceConsequence:
    """Represents the consequence of a choice."""

    consequence_id: str
    choice_id: str
    consequence_type: str  # narrative, therapeutic, emotional, progress
    description: str

    # Impact values
    narrative_impact: dict[str, Any] = field(default_factory=dict)
    therapeutic_impact: dict[str, float] = field(default_factory=dict)
    emotional_impact: dict[str, float] = field(default_factory=dict)
    progress_impact: dict[str, float] = field(default_factory=dict)

    # Conditions and triggers
    conditions: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)

    # Timing
    immediate: bool = True
    delay: timedelta = field(default=timedelta())

    def is_applicable(self, session_state: SessionState) -> bool:
        """Check if consequence is applicable given session state."""
        for condition in self.conditions:
            if not self._evaluate_condition(condition, session_state):
                return False
        return True

    def _evaluate_condition(self, condition: str, session_state: SessionState) -> bool:
        """Evaluate a consequence condition."""
        # Simple condition evaluation
        if condition.startswith("has_goal:"):
            goal = condition.split(":", 1)[1]
            return goal in session_state.therapeutic_goals

        elif condition.startswith("emotional_state:"):
            parts = condition.split(":")
            if len(parts) == 3:
                emotion, operator, threshold = (
                    parts[1],
                    parts[2][0],
                    float(parts[2][1:]),
                )
                current_value = session_state.emotional_state.get(emotion, 0.0)

                if operator == ">":
                    return current_value > threshold
                elif operator == "<":
                    return current_value < threshold

        elif condition == "safety_cleared":
            return session_state.safety_level != "crisis"

        return True


class ChoiceValidator:
    """Validates user choices for safety and therapeutic appropriateness."""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> dict[str, Any]:
        """Load choice validation rules."""
        return {
            "min_therapeutic_relevance": 0.3,
            "max_risk_tolerance": 0.7,
            "required_safety_score": 0.5,
            "blocked_choice_types": [],
            "crisis_mode_restrictions": True,
        }

    def validate_choice(
        self, choice: UserChoice, session_state: SessionState
    ) -> ChoiceContext:
        """Validate a user choice."""
        context = ChoiceContext(choice=choice, session_state=session_state)

        # Basic validation
        if not choice.choice_id or not choice.choice_text:
            context.validation_result = ChoiceValidationResult.INVALID
            context.validation_issues.append("Missing choice ID or text")
            return context

        # Safety validation
        context.safety_score = self._calculate_safety_score(choice, session_state)
        if context.safety_score < self.validation_rules["required_safety_score"]:
            context.validation_result = ChoiceValidationResult.SAFETY_CONCERN
            context.validation_issues.append("Choice has safety concerns")
            context.risk_factors.append("Low safety score")

        # Therapeutic alignment validation
        context.therapeutic_alignment = self._calculate_therapeutic_alignment(
            choice, session_state
        )
        if (
            context.therapeutic_alignment
            < self.validation_rules["min_therapeutic_relevance"]
        ):
            context.validation_result = ChoiceValidationResult.THERAPEUTIC_MISMATCH
            context.validation_issues.append("Choice not therapeutically aligned")

        # Crisis mode restrictions
        if (
            session_state.safety_level == "crisis"
            and self.validation_rules["crisis_mode_restrictions"]
        ):
            if choice.choice_type not in [ChoiceType.THERAPEUTIC]:
                context.validation_result = ChoiceValidationResult.INVALID
                context.validation_issues.append(
                    "Only therapeutic choices allowed in crisis mode"
                )

        # Blocked choice types
        if choice.choice_type in self.validation_rules["blocked_choice_types"]:
            context.validation_result = ChoiceValidationResult.INVALID
            context.validation_issues.append(
                f"Choice type {choice.choice_type} is blocked"
            )

        # Analyze therapeutic impact
        self._analyze_therapeutic_impact(context)

        # Analyze emotional impact
        self._analyze_emotional_impact(context)

        return context

    def _calculate_safety_score(
        self, choice: UserChoice, session_state: SessionState
    ) -> float:
        """Calculate safety score for a choice."""
        score = 1.0

        # Base score from choice properties
        if hasattr(choice, "safety_score"):
            score = choice.safety_score

        # Adjust based on choice type
        if choice.choice_type == ChoiceType.BEHAVIORAL:
            score *= 0.8  # Behavioral choices may have some risk
        elif choice.choice_type == ChoiceType.THERAPEUTIC:
            score = min(score * 1.1, 1.0)  # Therapeutic choices are generally safer

        # Adjust based on session safety level
        if session_state.safety_level == "crisis":
            score *= 0.8
        elif session_state.safety_level == "elevated":
            score *= 0.9

        return max(0.0, min(1.0, score))

    def _calculate_therapeutic_alignment(
        self, choice: UserChoice, session_state: SessionState
    ) -> float:
        """Calculate therapeutic alignment score."""
        alignment = choice.therapeutic_relevance

        # Bonus for choices that align with user's therapeutic goals
        # Check if choice text mentions therapeutic goals
        for goal in session_state.therapeutic_goals:
            if goal.lower() in choice.choice_text.lower():
                alignment += 0.1

        # Adjust based on choice type
        if choice.choice_type == ChoiceType.THERAPEUTIC:
            alignment = min(alignment * 1.3, 1.0)
        elif choice.choice_type == ChoiceType.NARRATIVE:
            alignment *= 0.8

        return max(0.0, min(1.0, alignment))

    def _analyze_therapeutic_impact(self, context: ChoiceContext) -> None:
        """Analyze therapeutic impact of choice."""
        choice = context.choice
        session_state = context.session_state

        # Identify skill practice opportunities
        if choice.choice_type == ChoiceType.THERAPEUTIC:
            if "anxiety" in choice.choice_text.lower():
                context.skill_practice_opportunity = "anxiety_management"
            elif "breath" in choice.choice_text.lower():
                context.skill_practice_opportunity = "deep_breathing"
            elif "ground" in choice.choice_text.lower():
                context.skill_practice_opportunity = "grounding_techniques"

        # Calculate progress impact
        for goal in session_state.therapeutic_goals:
            if goal.lower() in choice.choice_text.lower():
                context.progress_impact[goal] = choice.therapeutic_relevance * 0.1

    def _analyze_emotional_impact(self, context: ChoiceContext) -> None:
        """Analyze emotional impact of choice."""
        choice = context.choice

        # Simple emotional impact analysis based on choice content
        text_lower = choice.choice_text.lower()

        if any(word in text_lower for word in ["calm", "relax", "peace"]):
            context.emotional_impact["calm"] = 0.2
            context.emotional_impact["anxious"] = -0.1

        if any(word in text_lower for word in ["confident", "strong", "brave"]):
            context.emotional_impact["confident"] = 0.2
            context.emotional_impact["fearful"] = -0.1

        if any(word in text_lower for word in ["help", "support", "connect"]):
            context.emotional_impact["supported"] = 0.2
            context.emotional_impact["isolated"] = -0.1


class ChoiceProcessor:
    """Processes user choices and applies consequences."""

    def __init__(self, narrative_engine):
        self.narrative_engine = narrative_engine
        self.validator = ChoiceValidator()

        # Consequence system integration
        self.consequence_system = ConsequenceSystem(narrative_engine.event_bus)

        # Adaptive difficulty integration
        self.difficulty_engine = AdaptiveDifficultyEngine(narrative_engine.event_bus)

        # Therapeutic integration system
        self.therapeutic_integration = TherapeuticIntegrationSystem(
            narrative_engine.event_bus
        )

        # Character development system
        self.character_development = CharacterDevelopmentSystem(
            narrative_engine.event_bus
        )

        # Choice cache
        self.choice_cache: dict[str, UserChoice] = {}
        self.consequence_cache: dict[str, list[ChoiceConsequence]] = {}

        # Processing queue for delayed consequences
        self.delayed_consequences: list[
            tuple[datetime, ChoiceConsequence, SessionState]
        ] = []

        # Metrics
        self.metrics = {
            "choices_processed": 0,
            "choices_validated": 0,
            "validation_failures": 0,
            "consequences_applied": 0,
            "consequences_generated": 0,
            "difficulty_adjustments": 0,
            "therapeutic_integrations": 0,
            "character_developments": 0,
            "therapeutic_moments_triggered": 0,
        }

    async def initialize(self) -> None:
        """Initialize the choice processor."""
        logger.info("Initializing choice processor...")

        # Subscribe to relevant events
        self.narrative_engine.event_bus.subscribe(
            EventType.CHOICE_MADE, self._handle_choice_made
        )

        # Start delayed consequence processor
        import asyncio

        asyncio.create_task(self._process_delayed_consequences())

        logger.info("Choice processor initialized")

    async def load_choice(self, choice_id: str) -> UserChoice | None:
        """Load a choice by ID."""
        try:
            # Check cache first
            if choice_id in self.choice_cache:
                return self.choice_cache[choice_id]

            # Load from database
            choice_data = await self.narrative_engine.database_manager.narrative_manager.get_choice_by_id(
                choice_id
            )

            if not choice_data:
                logger.warning(f"Choice not found: {choice_id}")
                return None

            # Create choice object
            choice = UserChoice(
                choice_id=choice_data["choice_id"],
                scene_id=choice_data.get("scene_id", ""),
                choice_text=choice_data["choice_text"],
                choice_type=ChoiceType(
                    choice_data.get("choice_type", ChoiceType.NARRATIVE.value)
                ),
                therapeutic_relevance=choice_data.get("therapeutic_relevance", 0.0),
                emotional_weight=choice_data.get("emotional_weight", 0.0),
                difficulty_level=choice_data.get("difficulty_level", 1),
                prerequisites=choice_data.get("prerequisites", []),
                consequences=choice_data.get("consequences", []),
            )

            # Cache choice
            self.choice_cache[choice_id] = choice

            return choice

        except Exception as e:
            logger.error(f"Failed to load choice {choice_id}: {e}")
            return None

    async def process_choice(self, session_state: SessionState, choice_id: str) -> bool:
        """Process a user choice."""
        try:
            start_time = datetime.utcnow()

            # Load choice
            choice = await self.load_choice(choice_id)
            if not choice:
                logger.error(f"Choice not found: {choice_id}")
                return False

            # Validate choice
            context = self.validator.validate_choice(choice, session_state)
            context.processed_at = datetime.utcnow()
            context.processing_time = context.processed_at - start_time

            self.metrics["choices_validated"] += 1

            # Check validation result
            if context.validation_result != ChoiceValidationResult.VALID:
                logger.warning(
                    f"Choice validation failed: {choice_id} - {context.validation_issues}"
                )
                self.metrics["validation_failures"] += 1

                # Publish validation failure event
                event = create_choice_event(
                    EventType.CHOICE_VALIDATED,
                    session_state.session_id,
                    session_state.user_id,
                    choice_id,
                    choice.choice_text,
                    choice.choice_type.value,
                    choice.therapeutic_relevance,
                    data={
                        "validation_result": context.validation_result.value,
                        "validation_issues": context.validation_issues,
                    },
                )
                await self.narrative_engine.event_bus.publish(event)

                return False

            # Apply choice effects
            await self._apply_choice_effects(context)

            # Generate consequences using the new ConsequenceSystem
            consequence_context = ConsequenceGenerationContext(
                choice=choice,
                session_state=session_state,
                therapeutic_goals=session_state.therapeutic_goals,
                user_progress=session_state.progress_metrics,
                narrative_context=session_state.context,
            )

            consequence_set = await self.consequence_system.generate_consequences(
                consequence_context
            )

            # Apply the generated consequences
            await self._apply_consequence_set(consequence_set, session_state)
            context.consequences_applied.append(consequence_set.consequence_id)

            # Store consequences in choice for future reference
            choice.consequences = consequence_set

            self.metrics["consequences_generated"] += 1

            # Monitor performance for adaptive difficulty
            choice_interaction_data = {
                "response_time": (
                    context.processing_time.total_seconds()
                    if context.processing_time
                    else 30.0
                ),
                "choice_complexity": choice.difficulty_level,
                "therapeutic_relevance": choice.therapeutic_relevance,
                "emotional_weight": choice.emotional_weight,
                "interaction_type": "choice_processed",
                "choice_type": choice.choice_type.value,
                "consequences_applied": len(context.consequences_applied),
            }

            await self.difficulty_engine.monitor_performance(
                session_state, choice_interaction_data
            )

            # Integrate therapeutic concepts if relevant
            if choice.therapeutic_relevance > 0.5:  # High therapeutic relevance
                therapeutic_concept = self._identify_therapeutic_concept(
                    choice, session_state
                )
                if therapeutic_concept:
                    story_context = f"Through your choice of '{choice.text}', you encounter an opportunity to explore {therapeutic_concept}"

                    integration = await self.therapeutic_integration.integrate_therapeutic_concept(
                        session_state,
                        therapeutic_concept,
                        story_context,
                        IntegrationStrategy.EXPERIENTIAL_LEARNING,
                    )

                    # Track therapeutic progress
                    progress_data = {
                        "skill_demonstration": choice.therapeutic_relevance,
                        "practice_attempt": True,
                        "successful": len(context.consequences_applied) > 0,
                        "story_context": story_context,
                    }

                    await self.therapeutic_integration.track_therapeutic_progress(
                        session_state, therapeutic_concept, progress_data
                    )

                    # Check for resistance patterns
                    resistance_data = {
                        "engagement_level": choice_interaction_data.get(
                            "choice_complexity", 0.5
                        ),
                        "skill_demonstration": choice.therapeutic_relevance,
                        "emotional_response": session_state.emotional_state.get(
                            "primary_emotion", "neutral"
                        ),
                        "choice_pattern": (
                            "engaged"
                            if choice.therapeutic_relevance > 0.7
                            else "hesitant"
                        ),
                    }

                    await self.therapeutic_integration.detect_therapeutic_resistance(
                        session_state, therapeutic_concept, resistance_data
                    )

                    self.metrics["therapeutic_integrations"] += 1

            # Process character development based on choice and consequences
            character_development_context = {
                "description": f"Character development from choice: {choice.text}",
                "story_context": context.story_context,
                "choice_type": choice.choice_type,
                "therapeutic_relevance": choice.therapeutic_relevance,
                "consequences_applied": len(context.consequences_applied),
                "first_time": choice.choice_id
                not in session_state.context.get("previous_choices", []),
                "therapeutic_aligned": choice.therapeutic_relevance > 0.6,
                "milestone_related": any(
                    consequence.therapeutic_outcomes_count > 0
                    for consequence in context.consequences_applied
                ),
            }

            character_event = (
                await self.character_development.process_character_development(
                    session_state,
                    DevelopmentTrigger.CHOICE_CONSEQUENCE,
                    character_development_context,
                )
            )

            self.metrics["character_developments"] += 1

            # Legacy consequence handling (for backward compatibility)
            legacy_consequences = await self._load_choice_consequences(choice_id)
            for consequence in legacy_consequences:
                if consequence.is_applicable(session_state):
                    if consequence.immediate:
                        await self._apply_consequence(consequence, session_state)
                        context.consequences_applied.append(consequence.consequence_id)
                    else:
                        # Schedule delayed consequence
                        execute_at = datetime.utcnow() + consequence.delay
                        self.delayed_consequences.append(
                            (execute_at, consequence, session_state)
                        )

            # Update session state
            session_state.add_choice(choice_id)
            session_state.update_activity()

            # Publish choice processed event
            event = create_choice_event(
                EventType.CHOICE_PROCESSED,
                session_state.session_id,
                session_state.user_id,
                choice_id,
                choice.choice_text,
                choice.choice_type.value,
                choice.therapeutic_relevance,
                data={
                    "processing_time": context.processing_time.total_seconds(),
                    "consequences_applied": len(context.consequences_applied),
                    "therapeutic_alignment": context.therapeutic_alignment,
                    "safety_score": context.safety_score,
                },
            )
            await self.narrative_engine.event_bus.publish(event)

            self.metrics["choices_processed"] += 1
            self.metrics["consequences_applied"] += len(context.consequences_applied)

            # Check for therapeutic moments
            if context.skill_practice_opportunity:
                await self._trigger_therapeutic_moment(context)

            logger.debug(
                f"Processed choice {choice_id} for session {session_state.session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to process choice {choice_id}: {e}")
            return False

    async def _apply_choice_effects(self, context: ChoiceContext) -> None:
        """Apply immediate effects of a choice."""
        choice = context.choice
        session_state = context.session_state

        # Apply emotional impact
        for emotion, impact in context.emotional_impact.items():
            current_value = session_state.emotional_state.get(emotion, 0.0)
            new_value = max(0.0, min(1.0, current_value + impact))
            session_state.update_emotional_state(emotion, new_value)

        # Apply progress impact
        for goal, impact in context.progress_impact.items():
            # This would integrate with progress tracking system
            session_state.set_narrative_variable(
                f"progress_{goal}",
                session_state.get_narrative_variable(f"progress_{goal}", 0.0) + impact,
            )

        # Set choice-related narrative variables
        session_state.set_narrative_variable(
            "last_choice_type", choice.choice_type.value
        )
        session_state.set_narrative_variable(
            "last_choice_therapeutic_relevance", choice.therapeutic_relevance
        )

    async def _load_choice_consequences(
        self, choice_id: str
    ) -> list[ChoiceConsequence]:
        """Load consequences for a choice."""
        try:
            # Check cache first
            if choice_id in self.consequence_cache:
                return self.consequence_cache[choice_id]

            # Load from database
            consequences_data = await self.narrative_engine.database_manager.narrative_manager.get_choice_consequences(
                choice_id
            )

            consequences = []
            for data in consequences_data:
                consequence = ChoiceConsequence(
                    consequence_id=data["consequence_id"],
                    choice_id=choice_id,
                    consequence_type=data.get("consequence_type", "narrative"),
                    description=data.get("description", ""),
                    narrative_impact=data.get("narrative_impact", {}),
                    therapeutic_impact=data.get("therapeutic_impact", {}),
                    emotional_impact=data.get("emotional_impact", {}),
                    progress_impact=data.get("progress_impact", {}),
                    conditions=data.get("conditions", []),
                    triggers=data.get("triggers", []),
                    immediate=data.get("immediate", True),
                    delay=timedelta(seconds=data.get("delay_seconds", 0)),
                )
                consequences.append(consequence)

            # Cache consequences
            self.consequence_cache[choice_id] = consequences

            return consequences

        except Exception as e:
            logger.error(f"Failed to load consequences for choice {choice_id}: {e}")
            return []

    async def _apply_consequence(
        self, consequence: ChoiceConsequence, session_state: SessionState
    ) -> None:
        """Apply a choice consequence."""
        try:
            # Apply narrative impact
            for key, value in consequence.narrative_impact.items():
                session_state.set_narrative_variable(key, value)

            # Apply emotional impact
            for emotion, impact in consequence.emotional_impact.items():
                current_value = session_state.emotional_state.get(emotion, 0.0)
                new_value = max(0.0, min(1.0, current_value + impact))
                session_state.update_emotional_state(emotion, new_value)

            # Apply therapeutic impact
            for goal, impact in consequence.therapeutic_impact.items():
                current_progress = session_state.get_narrative_variable(
                    f"progress_{goal}", 0.0
                )
                session_state.set_narrative_variable(
                    f"progress_{goal}", current_progress + impact
                )

            logger.debug(f"Applied consequence {consequence.consequence_id}")

        except Exception as e:
            logger.error(
                f"Failed to apply consequence {consequence.consequence_id}: {e}"
            )

    async def _apply_consequence_set(
        self, consequence_set: ConsequenceSet, session_state: SessionState
    ) -> None:
        """Apply a consequence set generated by the ConsequenceSystem."""
        try:
            # Apply therapeutic outcomes
            for outcome in consequence_set.therapeutic_outcomes:
                # Update progress metrics
                current_progress = session_state.progress_metrics.get(
                    outcome.outcome_type, 0.0
                )
                new_progress = min(1.0, current_progress + outcome.therapeutic_value)
                session_state.progress_metrics[outcome.outcome_type] = new_progress

                # Log therapeutic outcome
                logger.debug(
                    f"Applied therapeutic outcome: {outcome.outcome_type} +{outcome.therapeutic_value}"
                )

            # Apply narrative impact
            for key, value in consequence_set.narrative_impact.items():
                session_state.set_narrative_variable(key, value)

            # Apply character changes
            for character, changes in consequence_set.character_changes.items():
                for attribute, change in changes.items():
                    current_value = session_state.get_narrative_variable(
                        f"character_{character}_{attribute}", 0.0
                    )
                    session_state.set_narrative_variable(
                        f"character_{character}_{attribute}", current_value + change
                    )

            # Apply emotional impact
            for emotion, impact in consequence_set.emotional_impact.items():
                current_value = session_state.emotional_state.get(emotion, 0.0)
                new_value = max(0.0, min(1.0, current_value + impact))
                session_state.update_emotional_state(emotion, new_value)

            # Store learning opportunities in session context
            if consequence_set.learning_opportunities:
                current_opportunities = session_state.context.get(
                    "learning_opportunities", []
                )
                current_opportunities.extend(consequence_set.learning_opportunities)
                session_state.context["learning_opportunities"] = current_opportunities[
                    -10:
                ]  # Keep last 10

            # Update consequence history
            consequence_history = session_state.context.get("consequence_history", [])
            consequence_history.append(
                {
                    "consequence_id": consequence_set.consequence_id,
                    "choice_id": consequence_set.choice_id,
                    "consequence_type": consequence_set.consequence_type.value,
                    "therapeutic_outcomes_count": len(
                        consequence_set.therapeutic_outcomes
                    ),
                    "learning_opportunities_count": len(
                        consequence_set.learning_opportunities
                    ),
                    "applied_at": datetime.utcnow().isoformat(),
                }
            )
            session_state.context["consequence_history"] = consequence_history[
                -20:
            ]  # Keep last 20

            self.metrics["consequences_applied"] += 1
            logger.debug(f"Applied consequence set {consequence_set.consequence_id}")

        except Exception as e:
            logger.error(
                f"Failed to apply consequence set {consequence_set.consequence_id}: {e}"
            )

    async def _trigger_therapeutic_moment(self, context: ChoiceContext) -> None:
        """Trigger a therapeutic moment based on choice."""
        event = create_choice_event(
            EventType.THERAPEUTIC_MOMENT,
            context.session_state.session_id,
            context.session_state.user_id,
            context.choice.choice_id,
            context.choice.choice_text,
            context.choice.choice_type.value,
            context.choice.therapeutic_relevance,
            data={
                "skill_practice_opportunity": context.skill_practice_opportunity,
                "therapeutic_alignment": context.therapeutic_alignment,
            },
        )
        await self.narrative_engine.event_bus.publish(event)

        self.metrics["therapeutic_moments_triggered"] += 1

    async def _process_delayed_consequences(self) -> None:
        """Process delayed consequences."""
        while True:
            try:
                current_time = datetime.utcnow()

                # Process due consequences
                due_consequences = [
                    (consequence, session_state)
                    for execute_at, consequence, session_state in self.delayed_consequences
                    if execute_at <= current_time
                ]

                for consequence, session_state in due_consequences:
                    await self._apply_consequence(consequence, session_state)

                # Remove processed consequences
                self.delayed_consequences = [
                    (execute_at, consequence, session_state)
                    for execute_at, consequence, session_state in self.delayed_consequences
                    if execute_at > current_time
                ]

                await asyncio.sleep(10)  # Check every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in delayed consequence processor: {e}")
                await asyncio.sleep(60)

    async def _handle_choice_made(self, event) -> None:
        """Handle choice made events."""
        logger.debug(
            f"Choice made: {event.context.get('choice_id')} in session {event.session_id}"
        )

    def _identify_therapeutic_concept(
        self, choice: UserChoice, session_state: SessionState
    ) -> str | None:
        """Identify relevant therapeutic concept based on choice and session context."""
        # Map choice types to therapeutic concepts
        concept_mapping = {
            ChoiceType.EMOTIONAL_REGULATION: "emotional_regulation",
            ChoiceType.COMMUNICATION: "communication_skills",
            ChoiceType.PROBLEM_SOLVING: "problem_solving",
            ChoiceType.SELF_REFLECTION: "self_awareness",
            ChoiceType.RELATIONSHIP: "relationship_skills",
            ChoiceType.COPING_STRATEGY: "coping_strategies",
        }

        # Check choice type mapping
        if choice.choice_type in concept_mapping:
            return concept_mapping[choice.choice_type]

        # Check therapeutic goals
        therapeutic_goals = session_state.therapeutic_goals

        # Map common therapeutic goals to concepts
        goal_mapping = {
            "anxiety_management": "anxiety_management",
            "depression_recovery": "depression_recovery",
            "emotional_regulation": "emotional_regulation",
            "communication_skills": "communication_skills",
            "thought_challenging": "thought_challenging",
            "behavioral_activation": "behavioral_activation",
            "mindfulness_practice": "present_moment_awareness",
            "distress_tolerance": "distress_tolerance",
        }

        # Find matching therapeutic goal
        for goal in therapeutic_goals:
            if goal in goal_mapping:
                return goal_mapping[goal]

        # Default based on high therapeutic relevance
        if choice.therapeutic_relevance > 0.8:
            return "general_therapeutic_skills"

        return None

    def get_metrics(self) -> dict[str, Any]:
        """Get choice processor metrics."""
        return {
            **self.metrics,
            "cached_choices": len(self.choice_cache),
            "cached_consequences": len(self.consequence_cache),
            "pending_delayed_consequences": len(self.delayed_consequences),
        }
