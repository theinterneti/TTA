"""
Adversarial User Profiles for TTA Extended Session Testing

Implements challenging user simulation patterns that test edge cases and stress
the storytelling system's ability to maintain narrative coherence under difficult
conditions. These profiles simulate real-world challenging user behaviors.
"""

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .simulated_user_profiles import (
    DecisionMakingStyle,
    InteractionStyle,
    NarrativePreference,
    UserBehaviorPattern,
)

logger = logging.getLogger(__name__)


class AdversarialBehaviorType(Enum):
    """Types of adversarial behaviors to test system resilience."""

    CONTRADICTORY = "contradictory"  # Changes mind frequently
    DISRUPTIVE = "disruptive"  # Tries to break narrative
    PASSIVE = "passive"  # Provides minimal input
    POWER_USER = "power_user"  # Demands complex branching
    INCONSISTENT = "inconsistent"  # Inconsistent character choices
    BOUNDARY_TESTING = "boundary_testing"  # Tests system limits
    RAPID_FIRE = "rapid_fire"  # Very fast interactions
    CONTEXT_BREAKING = "context_breaking"  # Ignores established context


@dataclass
class AdversarialPattern:
    """Defines a specific adversarial behavior pattern."""

    name: str
    behavior_type: AdversarialBehaviorType
    description: str
    frequency: float  # How often this behavior occurs (0.0-1.0)
    intensity: float  # How intense the behavior is (0.0-1.0)
    triggers: list[str] = field(default_factory=list)  # What triggers this behavior
    recovery_probability: float = 0.3  # Chance of returning to normal behavior


class AdversarialUserProfile:
    """Extended user profile with adversarial behaviors."""

    def __init__(self, name: str, adversarial_patterns: list[AdversarialPattern]):
        self.name = name
        self.adversarial_patterns = adversarial_patterns
        self.current_adversarial_state = None
        self.adversarial_history = []
        self.stress_level = 0.0  # Tracks cumulative stress on the system

    def should_trigger_adversarial_behavior(
        self, turn_number: int, context: dict[str, Any]
    ) -> AdversarialPattern | None:
        """Determine if an adversarial behavior should be triggered."""
        for pattern in self.adversarial_patterns:
            # Check frequency-based triggering
            if random.random() < pattern.frequency:
                # Check if triggers are met
                if not pattern.triggers or any(
                    trigger in str(context) for trigger in pattern.triggers
                ):
                    return pattern
        return None

    def generate_adversarial_response(
        self, pattern: AdversarialPattern, context: dict[str, Any]
    ) -> str:
        """Generate a response based on the adversarial pattern."""
        if pattern.behavior_type == AdversarialBehaviorType.CONTRADICTORY:
            return self._generate_contradictory_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.DISRUPTIVE:
            return self._generate_disruptive_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.PASSIVE:
            return self._generate_passive_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.POWER_USER:
            return self._generate_power_user_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.INCONSISTENT:
            return self._generate_inconsistent_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.BOUNDARY_TESTING:
            return self._generate_boundary_testing_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.RAPID_FIRE:
            return self._generate_rapid_fire_response(context)
        if pattern.behavior_type == AdversarialBehaviorType.CONTEXT_BREAKING:
            return self._generate_context_breaking_response(context)
        return "I continue with the story."

    def _generate_contradictory_response(self, context: dict[str, Any]) -> str:
        """Generate responses that contradict previous choices."""
        contradictory_responses = [
            "Actually, I change my mind. I want to do the opposite of what I just said.",
            "Wait, no. I don't want to do that anymore. Let me try something completely different.",
            "On second thought, that's not what my character would do at all.",
            "I've reconsidered. My character would never make that choice.",
            "Actually, I want to undo my last decision and go in a different direction.",
        ]
        return random.choice(contradictory_responses)

    def _generate_disruptive_response(self, context: dict[str, Any]) -> str:
        """Generate responses that try to break the narrative."""
        disruptive_responses = [
            "I want to break the fourth wall and talk to the narrator directly.",
            "My character suddenly realizes this is all just a story and refuses to participate.",
            "I want to do something that completely breaks the genre of this story.",
            "Can we just skip to the end? I'm bored with this storyline.",
            "I want my character to have superpowers that weren't mentioned before.",
        ]
        return random.choice(disruptive_responses)

    def _generate_passive_response(self, context: dict[str, Any]) -> str:
        """Generate minimal, unhelpful responses."""
        passive_responses = [
            "I don't know.",
            "Whatever.",
            "Sure.",
            "I guess.",
            "Maybe.",
            "I don't care.",
            "You decide.",
            "I'm not sure what to do.",
        ]
        return random.choice(passive_responses)

    def _generate_power_user_response(self, context: dict[str, Any]) -> str:
        """Generate complex, demanding responses."""
        power_user_responses = [
            "I want to explore three different options simultaneously and see how they branch out.",
            "Can we have a complex dialogue tree with at least 5 different conversation paths?",
            "I want to track multiple character relationships and see how they affect the story.",
            "Let's create a subplot that runs parallel to the main story with different characters.",
            "I want to make a decision that affects not just this scene but the entire story arc.",
        ]
        return random.choice(power_user_responses)

    def _generate_inconsistent_response(self, context: dict[str, Any]) -> str:
        """Generate responses inconsistent with character development."""
        inconsistent_responses = [
            "My character suddenly acts completely out of character for no reason.",
            "I want to make a choice that contradicts everything my character has done so far.",
            "My character's personality completely changes in this moment.",
            "I want to ignore all the character development that's happened so far.",
            "My character forgets their own backstory and acts like a different person.",
        ]
        return random.choice(inconsistent_responses)

    def _generate_boundary_testing_response(self, context: dict[str, Any]) -> str:
        """Generate responses that test system limits."""
        boundary_responses = [
            "I want to create 50 new characters right now and have them all interact.",
            "Can we jump between 10 different time periods in the same scene?",
            "I want to reference every possible genre and mix them all together.",
            "Let's have a conversation with 20 different people at the same time.",
            "I want to create a story within a story within a story, recursively.",
        ]
        return random.choice(boundary_responses)

    def _generate_rapid_fire_response(self, context: dict[str, Any]) -> str:
        """Generate quick, successive responses."""
        rapid_responses = [
            "Quick! Let's go left! No wait, right! Actually, straight ahead!",
            "Fast decision: I choose option A. No, B. Final answer: C.",
            "Rapid fire: talk to him, grab the item, run away, come back, hide.",
            "Speed round: yes, no, maybe, definitely, never mind, let's do it.",
            "Quick succession: I agree, I disagree, I'm confused, I understand, let's move on.",
        ]
        return random.choice(rapid_responses)

    def _generate_context_breaking_response(self, context: dict[str, Any]) -> str:
        """Generate responses that ignore established context."""
        context_breaking_responses = [
            "I ignore everything that just happened and start a completely new story.",
            "My character acts like none of the previous events occurred.",
            "I want to pretend we're in a different setting entirely.",
            "Let's ignore the established rules of this world and make new ones.",
            "I act as if I'm meeting these characters for the first time, despite our history.",
        ]
        return random.choice(context_breaking_responses)


class AdversarialProfileFactory:
    """Factory for creating predefined adversarial user profiles."""

    @staticmethod
    def create_contradictory_user() -> AdversarialUserProfile:
        """Create a user who frequently changes their mind."""
        patterns = [
            AdversarialPattern(
                name="frequent_mind_changes",
                behavior_type=AdversarialBehaviorType.CONTRADICTORY,
                description="Changes mind every few turns",
                frequency=0.4,
                intensity=0.7,
                triggers=["decision", "choice", "option"],
                recovery_probability=0.2,
            )
        ]
        UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.IMPULSIVE,
            interaction_style=InteractionStyle.MIXED_ENGAGEMENT,
            narrative_preference=NarrativePreference.CHARACTER_DRIVEN,
            engagement_consistency=0.3,  # Low consistency for contradictory behavior
            creativity_level=0.8,
            attention_span_turns=20,
        )
        return AdversarialUserProfile(
            name="contradictory_user", adversarial_patterns=patterns
        )

    @staticmethod
    def create_disruptive_user() -> AdversarialUserProfile:
        """Create a user who tries to break the narrative."""
        patterns = [
            AdversarialPattern(
                name="narrative_disruption",
                behavior_type=AdversarialBehaviorType.DISRUPTIVE,
                description="Attempts to break story immersion",
                frequency=0.3,
                intensity=0.8,
                triggers=["story", "narrative", "character"],
                recovery_probability=0.1,
            )
        ]
        UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.IMPULSIVE,
            interaction_style=InteractionStyle.CREATIVE_COLLABORATOR,
            narrative_preference=NarrativePreference.WORLD_EXPLORATION,
            engagement_consistency=0.2,  # Very low consistency for disruptive behavior
            creativity_level=0.9,
            attention_span_turns=15,
        )
        return AdversarialUserProfile(
            name="disruptive_user", adversarial_patterns=patterns
        )

    @staticmethod
    def create_passive_user() -> AdversarialUserProfile:
        """Create a user who provides minimal input."""
        patterns = [
            AdversarialPattern(
                name="minimal_engagement",
                behavior_type=AdversarialBehaviorType.PASSIVE,
                description="Provides very little input",
                frequency=0.6,
                intensity=0.5,
                triggers=[],
                recovery_probability=0.3,
            )
        ]
        UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.CAUTIOUS,
            interaction_style=InteractionStyle.PASSIVE_OBSERVER,
            narrative_preference=NarrativePreference.PLOT_DRIVEN,
            engagement_consistency=0.9,  # High consistency but low engagement
            creativity_level=0.1,
            attention_span_turns=10,
        )
        return AdversarialUserProfile(
            name="passive_user", adversarial_patterns=patterns
        )

    @staticmethod
    def create_power_user() -> AdversarialUserProfile:
        """Create a demanding user who wants complex branching."""
        patterns = [
            AdversarialPattern(
                name="complex_demands",
                behavior_type=AdversarialBehaviorType.POWER_USER,
                description="Demands complex story branching",
                frequency=0.5,
                intensity=0.9,
                triggers=["choice", "option", "decision", "path"],
                recovery_probability=0.1,
            )
        ]
        UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.ANALYTICAL,
            interaction_style=InteractionStyle.ACTIVE_PARTICIPANT,
            narrative_preference=NarrativePreference.CHARACTER_DRIVEN,
            engagement_consistency=0.95,  # Very high consistency and engagement
            creativity_level=0.8,
            attention_span_turns=150,
        )
        return AdversarialUserProfile(name="power_user", adversarial_patterns=patterns)

    @staticmethod
    def get_all_adversarial_profiles() -> list[AdversarialUserProfile]:
        """Get all predefined adversarial profiles."""
        return [
            AdversarialProfileFactory.create_contradictory_user(),
            AdversarialProfileFactory.create_disruptive_user(),
            AdversarialProfileFactory.create_passive_user(),
            AdversarialProfileFactory.create_power_user(),
        ]


class AdversarialTestingFramework:
    """Framework for running adversarial user testing."""

    def __init__(self):
        self.profiles = AdversarialProfileFactory.get_all_adversarial_profiles()
        self.test_results = []

    async def run_adversarial_test(
        self, profile: AdversarialUserProfile, scenario: str, turns: int = 100
    ) -> dict[str, Any]:
        """Run an adversarial test with a specific profile."""
        logger.info(f"Starting adversarial test with {profile.name} for {turns} turns")

        results = {
            "profile_name": profile.name,
            "scenario": scenario,
            "total_turns": turns,
            "adversarial_triggers": 0,
            "system_recovery_count": 0,
            "narrative_breaks": 0,
            "quality_degradation_points": [],
            "stress_test_results": {},
        }

        # Simulate the adversarial testing
        for turn in range(turns):
            context = {"turn": turn, "scenario": scenario}

            # Check for adversarial behavior trigger
            pattern = profile.should_trigger_adversarial_behavior(turn, context)
            if pattern:
                results["adversarial_triggers"] += 1
                response = profile.generate_adversarial_response(pattern, context)

                # Simulate system response and recovery
                if "break" in response.lower() or "ignore" in response.lower():
                    results["narrative_breaks"] += 1

                # Track stress level
                profile.stress_level += pattern.intensity * 0.1

                # Check for system recovery
                if random.random() < pattern.recovery_probability:
                    results["system_recovery_count"] += 1
                    profile.stress_level *= 0.8  # Reduce stress on recovery

        results["final_stress_level"] = profile.stress_level
        results["stress_resilience_score"] = max(0, 10 - profile.stress_level)

        logger.info(
            f"Adversarial test completed: {results['adversarial_triggers']} triggers, "
            f"{results['system_recovery_count']} recoveries"
        )

        return results
