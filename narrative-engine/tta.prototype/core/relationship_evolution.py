"""
Advanced Relationship Evolution System for TTA Prototype

This module implements sophisticated relationship tracking and character evolution algorithms
that go beyond basic relationship scoring to include complex relationship dynamics,
character growth patterns, and personality consistency validation.

Classes:
    RelationshipEvolutionEngine: Advanced relationship evolution algorithms
    CharacterGrowthTracker: Tracks character development over time
    PersonalityConsistencyValidator: Validates character personality maintenance
    RelationshipDynamics: Models complex relationship interactions
"""

import logging

# Import system components
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Add paths for imports
core_path = Path(__file__).parent
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from character_development_system import Interaction
    from data_models import CharacterState, ValidationError
except ImportError:
    # Fallback for when running as part of package
    from ..models.data_models import CharacterState, ValidationError
    from .character_development_system import Interaction

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of relationships between characters."""
    THERAPEUTIC = "therapeutic"  # Therapist-patient relationship
    FRIENDSHIP = "friendship"    # Mutual friendship
    MENTORSHIP = "mentorship"    # Mentor-mentee relationship
    ROMANTIC = "romantic"        # Romantic relationship
    FAMILIAL = "familial"        # Family relationship
    PROFESSIONAL = "professional" # Work colleagues
    ADVERSARIAL = "adversarial"  # Conflict/opposition
    NEUTRAL = "neutral"          # No specific relationship


class GrowthPattern(Enum):
    """Patterns of character growth over time."""
    STEADY_IMPROVEMENT = "steady_improvement"
    BREAKTHROUGH_MOMENTS = "breakthrough_moments"
    CYCLICAL_PROGRESS = "cyclical_progress"
    PLATEAU_PERIODS = "plateau_periods"
    REGRESSION_RECOVERY = "regression_recovery"


@dataclass
class RelationshipMetrics:
    """Detailed metrics for a relationship between two characters."""
    relationship_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    character1_id: str = ""
    character2_id: str = ""
    relationship_type: RelationshipType = RelationshipType.NEUTRAL
    trust_level: float = 0.0  # -1.0 to 1.0
    intimacy_level: float = 0.0  # 0.0 to 1.0
    conflict_level: float = 0.0  # 0.0 to 1.0
    communication_quality: float = 0.5  # 0.0 to 1.0
    mutual_understanding: float = 0.5  # 0.0 to 1.0
    therapeutic_alliance: float = 0.0  # 0.0 to 1.0 (for therapeutic relationships)
    interaction_frequency: float = 0.0  # Interactions per day
    relationship_stability: float = 0.5  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate relationship metrics."""
        metrics_to_check = [
            ("trust_level", -1.0, 1.0),
            ("intimacy_level", 0.0, 1.0),
            ("conflict_level", 0.0, 1.0),
            ("communication_quality", 0.0, 1.0),
            ("mutual_understanding", 0.0, 1.0),
            ("therapeutic_alliance", 0.0, 1.0),
            ("relationship_stability", 0.0, 1.0)
        ]

        for metric_name, min_val, max_val in metrics_to_check:
            value = getattr(self, metric_name)
            if not min_val <= value <= max_val:
                raise ValidationError(f"{metric_name} must be between {min_val} and {max_val}")

        if self.interaction_frequency < 0:
            raise ValidationError("Interaction frequency cannot be negative")

        return True

    def calculate_overall_relationship_score(self) -> float:
        """Calculate overall relationship score from individual metrics."""
        # Weight different aspects of the relationship
        weights = {
            "trust_level": 0.25,
            "communication_quality": 0.20,
            "mutual_understanding": 0.20,
            "intimacy_level": 0.15,
            "therapeutic_alliance": 0.10,
            "relationship_stability": 0.10
        }

        # Conflict reduces overall score
        conflict_penalty = self.conflict_level * 0.3

        weighted_score = 0.0
        for metric, weight in weights.items():
            value = getattr(self, metric)
            # Normalize trust_level from [-1,1] to [0,1] for scoring
            if metric == "trust_level":
                value = (value + 1.0) / 2.0
            weighted_score += value * weight

        # Apply conflict penalty
        final_score = max(-1.0, min(1.0, (weighted_score * 2.0 - 1.0) - conflict_penalty))
        return final_score


@dataclass
class CharacterGrowthMetrics:
    """Tracks character growth and development over time."""
    character_id: str
    growth_pattern: GrowthPattern = GrowthPattern.STEADY_IMPROVEMENT
    personality_stability: dict[str, float] = field(default_factory=dict)
    growth_rate: float = 0.1  # Rate of personality change
    therapeutic_progress: float = 0.0  # 0.0 to 1.0
    emotional_resilience: float = 0.5  # 0.0 to 1.0
    social_competence: float = 0.5  # 0.0 to 1.0
    self_awareness: float = 0.5  # 0.0 to 1.0
    coping_effectiveness: float = 0.5  # 0.0 to 1.0
    growth_milestones: list[str] = field(default_factory=list)
    regression_events: list[str] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate character growth metrics."""
        metrics_to_check = [
            ("growth_rate", 0.0, 1.0),
            ("therapeutic_progress", 0.0, 1.0),
            ("emotional_resilience", 0.0, 1.0),
            ("social_competence", 0.0, 1.0),
            ("self_awareness", 0.0, 1.0),
            ("coping_effectiveness", 0.0, 1.0)
        ]

        for metric_name, min_val, max_val in metrics_to_check:
            value = getattr(self, metric_name)
            if not min_val <= value <= max_val:
                raise ValidationError(f"{metric_name} must be between {min_val} and {max_val}")

        # Validate personality stability values
        for trait, stability in self.personality_stability.items():
            if not 0.0 <= stability <= 1.0:
                raise ValidationError(f"Personality stability for {trait} must be between 0.0 and 1.0")

        return True


class RelationshipEvolutionEngine:
    """Advanced relationship evolution algorithms."""

    def __init__(self):
        self.relationship_metrics = {}  # character_pair -> RelationshipMetrics
        self.evolution_history = {}     # character_pair -> List[RelationshipMetrics]
        self.relationship_patterns = self._initialize_relationship_patterns()

    def _initialize_relationship_patterns(self) -> dict[RelationshipType, dict[str, float]]:
        """Initialize relationship evolution patterns for different relationship types."""
        return {
            RelationshipType.THERAPEUTIC: {
                "trust_growth_rate": 0.15,
                "intimacy_growth_rate": 0.05,
                "conflict_tolerance": 0.3,
                "communication_importance": 0.9,
                "stability_factor": 0.8
            },
            RelationshipType.FRIENDSHIP: {
                "trust_growth_rate": 0.10,
                "intimacy_growth_rate": 0.12,
                "conflict_tolerance": 0.4,
                "communication_importance": 0.7,
                "stability_factor": 0.6
            },
            RelationshipType.MENTORSHIP: {
                "trust_growth_rate": 0.12,
                "intimacy_growth_rate": 0.08,
                "conflict_tolerance": 0.2,
                "communication_importance": 0.8,
                "stability_factor": 0.7
            },
            RelationshipType.PROFESSIONAL: {
                "trust_growth_rate": 0.08,
                "intimacy_growth_rate": 0.03,
                "conflict_tolerance": 0.5,
                "communication_importance": 0.6,
                "stability_factor": 0.5
            }
        }

    def get_relationship_key(self, char1_id: str, char2_id: str) -> str:
        """Generate consistent key for character pair."""
        return f"{min(char1_id, char2_id)}_{max(char1_id, char2_id)}"

    def initialize_relationship(self, char1_id: str, char2_id: str,
                              relationship_type: RelationshipType = RelationshipType.NEUTRAL) -> RelationshipMetrics:
        """Initialize a new relationship between two characters."""
        key = self.get_relationship_key(char1_id, char2_id)

        metrics = RelationshipMetrics(
            character1_id=char1_id,
            character2_id=char2_id,
            relationship_type=relationship_type
        )

        # Set initial values based on relationship type
        if relationship_type == RelationshipType.THERAPEUTIC:
            metrics.therapeutic_alliance = 0.3  # Start with basic therapeutic alliance
            metrics.communication_quality = 0.6  # Professional communication
        elif relationship_type == RelationshipType.PROFESSIONAL:
            metrics.communication_quality = 0.5
            metrics.trust_level = 0.1

        metrics.validate()
        self.relationship_metrics[key] = metrics
        self.evolution_history[key] = [metrics]

        logger.info(f"Initialized {relationship_type.value} relationship between {char1_id} and {char2_id}")
        return metrics

    def update_relationship_from_interaction(self, char1_id: str, char2_id: str,
                                           interaction: Interaction) -> RelationshipMetrics:
        """Update relationship metrics based on an interaction."""
        key = self.get_relationship_key(char1_id, char2_id)

        if key not in self.relationship_metrics:
            # Auto-detect relationship type from interaction
            relationship_type = self._detect_relationship_type(interaction)
            self.initialize_relationship(char1_id, char2_id, relationship_type)

        metrics = self.relationship_metrics[key]
        patterns = self.relationship_patterns.get(metrics.relationship_type, {})

        # Update metrics based on interaction
        self._update_trust_level(metrics, interaction, patterns)
        self._update_intimacy_level(metrics, interaction, patterns)
        self._update_conflict_level(metrics, interaction, patterns)
        self._update_communication_quality(metrics, interaction, patterns)
        self._update_mutual_understanding(metrics, interaction, patterns)
        self._update_therapeutic_alliance(metrics, interaction, patterns)

        # Update interaction frequency
        self._update_interaction_frequency(metrics)

        # Update relationship stability
        self._update_relationship_stability(metrics, patterns)

        metrics.last_updated = datetime.now()
        metrics.validate()

        # Store in history
        self.evolution_history[key].append(metrics)

        logger.debug(f"Updated relationship between {char1_id} and {char2_id}")
        return metrics

    def _detect_relationship_type(self, interaction: Interaction) -> RelationshipType:
        """Detect relationship type from interaction characteristics."""
        if interaction.interaction_type == "therapeutic":
            return RelationshipType.THERAPEUTIC
        elif interaction.therapeutic_value > 0.5:
            return RelationshipType.MENTORSHIP
        elif interaction.emotional_impact > 0.6:
            return RelationshipType.FRIENDSHIP
        else:
            return RelationshipType.PROFESSIONAL

    def _update_trust_level(self, metrics: RelationshipMetrics, interaction: Interaction,
                           patterns: dict[str, float]) -> None:
        """Update trust level based on interaction."""
        growth_rate = patterns.get("trust_growth_rate", 0.1)

        # Positive interactions build trust
        if interaction.emotional_impact > 0:
            trust_change = interaction.emotional_impact * growth_rate
            if interaction.interaction_type == "therapeutic":
                trust_change *= 1.2  # Therapeutic interactions build trust faster
        else:
            # Negative interactions damage trust more severely
            trust_change = interaction.emotional_impact * growth_rate * 1.5

        # Apply diminishing returns for high trust
        if metrics.trust_level > 0.7:
            trust_change *= (1.0 - metrics.trust_level * 0.3)

        metrics.trust_level = max(-1.0, min(1.0, metrics.trust_level + trust_change))

    def _update_intimacy_level(self, metrics: RelationshipMetrics, interaction: Interaction,
                              patterns: dict[str, float]) -> None:
        """Update intimacy level based on interaction."""
        growth_rate = patterns.get("intimacy_growth_rate", 0.08)

        # Intimacy grows with positive emotional interactions
        if interaction.emotional_impact > 0.3:
            intimacy_change = (interaction.emotional_impact - 0.3) * growth_rate

            # Personal sharing increases intimacy
            if "personal" in interaction.content.lower() or "feel" in interaction.content.lower():
                intimacy_change *= 1.3
        else:
            intimacy_change = 0

        # Intimacy has natural decay over time without positive interactions
        time_since_update = (datetime.now() - metrics.last_updated).days
        decay = min(0.01 * time_since_update, 0.1)

        metrics.intimacy_level = max(0.0, min(1.0, metrics.intimacy_level + intimacy_change - decay))

    def _update_conflict_level(self, metrics: RelationshipMetrics, interaction: Interaction,
                              patterns: dict[str, float]) -> None:
        """Update conflict level based on interaction."""
        patterns.get("conflict_tolerance", 0.4)

        if interaction.interaction_type == "conflict":
            conflict_increase = abs(interaction.emotional_impact) * 0.3
            metrics.conflict_level = min(1.0, metrics.conflict_level + conflict_increase)
        elif interaction.emotional_impact < -0.3:
            # Negative interactions increase conflict
            conflict_increase = abs(interaction.emotional_impact) * 0.2
            metrics.conflict_level = min(1.0, metrics.conflict_level + conflict_increase)
        else:
            # Positive interactions reduce conflict
            if interaction.emotional_impact > 0.2:
                conflict_reduction = interaction.emotional_impact * 0.15
                metrics.conflict_level = max(0.0, metrics.conflict_level - conflict_reduction)

        # Natural conflict decay over time
        time_since_update = (datetime.now() - metrics.last_updated).days
        decay = min(0.02 * time_since_update, 0.2)
        metrics.conflict_level = max(0.0, metrics.conflict_level - decay)

    def _update_communication_quality(self, metrics: RelationshipMetrics, interaction: Interaction,
                                     patterns: dict[str, float]) -> None:
        """Update communication quality based on interaction."""
        importance = patterns.get("communication_importance", 0.7)

        # Good communication improves with successful interactions
        if interaction.therapeutic_value > 0.5 or interaction.emotional_impact > 0.4:
            comm_improvement = 0.05 * importance
            metrics.communication_quality = min(1.0, metrics.communication_quality + comm_improvement)
        elif interaction.interaction_type == "conflict":
            # Conflicts can damage communication
            comm_damage = 0.08 * importance
            metrics.communication_quality = max(0.0, metrics.communication_quality - comm_damage)

    def _update_mutual_understanding(self, metrics: RelationshipMetrics, interaction: Interaction,
                                    patterns: dict[str, float]) -> None:
        """Update mutual understanding based on interaction."""
        # Understanding grows with meaningful interactions
        if interaction.therapeutic_value > 0.3:
            understanding_growth = interaction.therapeutic_value * 0.06
            metrics.mutual_understanding = min(1.0, metrics.mutual_understanding + understanding_growth)

        # Misunderstandings reduce mutual understanding
        if interaction.emotional_impact < -0.4:
            understanding_loss = abs(interaction.emotional_impact) * 0.04
            metrics.mutual_understanding = max(0.0, metrics.mutual_understanding - understanding_loss)

    def _update_therapeutic_alliance(self, metrics: RelationshipMetrics, interaction: Interaction,
                                    patterns: dict[str, float]) -> None:
        """Update therapeutic alliance for therapeutic relationships."""
        if metrics.relationship_type != RelationshipType.THERAPEUTIC:
            return

        if interaction.interaction_type == "therapeutic":
            # Strong therapeutic interactions build alliance
            alliance_growth = interaction.therapeutic_value * 0.08
            metrics.therapeutic_alliance = min(1.0, metrics.therapeutic_alliance + alliance_growth)
        elif interaction.emotional_impact < -0.3:
            # Negative experiences can damage therapeutic alliance
            alliance_damage = abs(interaction.emotional_impact) * 0.05
            metrics.therapeutic_alliance = max(0.0, metrics.therapeutic_alliance - alliance_damage)

    def _update_interaction_frequency(self, metrics: RelationshipMetrics) -> None:
        """Update interaction frequency tracking."""
        # This is a simplified version - in full implementation would track actual frequency
        current_time = datetime.now()
        time_diff = (current_time - metrics.last_updated).total_seconds() / 86400  # days

        if time_diff > 0:
            # Exponential moving average of interaction frequency
            new_frequency = 1.0 / max(time_diff, 0.1)  # Interactions per day
            alpha = 0.3  # Smoothing factor
            metrics.interaction_frequency = (alpha * new_frequency +
                                           (1 - alpha) * metrics.interaction_frequency)

    def _update_relationship_stability(self, metrics: RelationshipMetrics,
                                      patterns: dict[str, float]) -> None:
        """Update relationship stability based on consistency of interactions."""
        stability_factor = patterns.get("stability_factor", 0.6)

        # High trust and low conflict increase stability
        stability_boost = (metrics.trust_level + 1.0) / 2.0 * 0.1 - metrics.conflict_level * 0.1
        stability_boost *= stability_factor

        metrics.relationship_stability = max(0.0, min(1.0,
                                           metrics.relationship_stability + stability_boost))

    def evolve_relationship_over_time(self, char1_id: str, char2_id: str,
                                     time_period: timedelta) -> RelationshipMetrics:
        """Evolve relationship over a time period without specific interactions."""
        key = self.get_relationship_key(char1_id, char2_id)

        if key not in self.relationship_metrics:
            logger.warning(f"No relationship found between {char1_id} and {char2_id}")
            return None

        metrics = self.relationship_metrics[key]
        days = time_period.days

        # Natural relationship decay without interaction
        if days > 7:  # After a week without interaction
            decay_factor = min(0.02 * (days - 7), 0.3)

            # Trust and intimacy decay
            metrics.trust_level *= (1.0 - decay_factor * 0.5)
            metrics.intimacy_level *= (1.0 - decay_factor)

            # Conflict naturally reduces over time
            metrics.conflict_level *= (1.0 - decay_factor * 2.0)
            metrics.conflict_level = max(0.0, metrics.conflict_level)

            # Communication quality slowly degrades
            metrics.communication_quality *= (1.0 - decay_factor * 0.3)

            # Therapeutic alliance is more stable but still decays
            if metrics.relationship_type == RelationshipType.THERAPEUTIC:
                metrics.therapeutic_alliance *= (1.0 - decay_factor * 0.2)

        metrics.last_updated = datetime.now()
        metrics.validate()

        logger.debug(f"Evolved relationship between {char1_id} and {char2_id} over {days} days")
        return metrics

    def get_relationship_analysis(self, char1_id: str, char2_id: str) -> dict[str, Any]:
        """Get detailed analysis of a relationship."""
        key = self.get_relationship_key(char1_id, char2_id)

        if key not in self.relationship_metrics:
            return {"error": "Relationship not found"}

        metrics = self.relationship_metrics[key]
        history = self.evolution_history.get(key, [])

        # Calculate trends
        trends = {}
        if len(history) > 1:
            recent = history[-1]
            previous = history[-2]

            trends = {
                "trust_trend": recent.trust_level - previous.trust_level,
                "intimacy_trend": recent.intimacy_level - previous.intimacy_level,
                "conflict_trend": recent.conflict_level - previous.conflict_level,
                "communication_trend": recent.communication_quality - previous.communication_quality
            }

        return {
            "relationship_type": metrics.relationship_type.value,
            "overall_score": metrics.calculate_overall_relationship_score(),
            "metrics": {
                "trust_level": metrics.trust_level,
                "intimacy_level": metrics.intimacy_level,
                "conflict_level": metrics.conflict_level,
                "communication_quality": metrics.communication_quality,
                "mutual_understanding": metrics.mutual_understanding,
                "therapeutic_alliance": metrics.therapeutic_alliance,
                "relationship_stability": metrics.relationship_stability
            },
            "trends": trends,
            "interaction_frequency": metrics.interaction_frequency,
            "history_length": len(history),
            "last_updated": metrics.last_updated
        }


class CharacterGrowthTracker:
    """Tracks character development and growth over time."""

    def __init__(self):
        self.growth_metrics = {}  # character_id -> CharacterGrowthMetrics
        self.growth_history = {}  # character_id -> List[CharacterGrowthMetrics]

    def initialize_character_growth(self, character_id: str,
                                   initial_pattern: GrowthPattern = GrowthPattern.STEADY_IMPROVEMENT) -> CharacterGrowthMetrics:
        """Initialize growth tracking for a character."""
        metrics = CharacterGrowthMetrics(
            character_id=character_id,
            growth_pattern=initial_pattern
        )

        metrics.validate()
        self.growth_metrics[character_id] = metrics
        self.growth_history[character_id] = [metrics]

        logger.info(f"Initialized growth tracking for character {character_id}")
        return metrics

    def update_character_growth(self, character_id: str, character_state: CharacterState,
                               interactions: list[Interaction]) -> CharacterGrowthMetrics:
        """Update character growth based on recent interactions and state changes."""
        if character_id not in self.growth_metrics:
            self.initialize_character_growth(character_id)

        metrics = self.growth_metrics[character_id]

        # Analyze recent interactions for growth indicators
        therapeutic_interactions = [i for i in interactions if i.interaction_type == "therapeutic"]
        positive_interactions = [i for i in interactions if i.emotional_impact > 0.3]

        # Update therapeutic progress
        if therapeutic_interactions:
            avg_therapeutic_value = sum(i.therapeutic_value for i in therapeutic_interactions) / len(therapeutic_interactions)
            progress_change = avg_therapeutic_value * 0.05
            metrics.therapeutic_progress = min(1.0, metrics.therapeutic_progress + progress_change)

        # Update emotional resilience based on handling of negative interactions
        negative_interactions = [i for i in interactions if i.emotional_impact < -0.2]
        if negative_interactions:
            # If character maintains stability despite negative interactions, resilience grows
            if character_state.current_mood not in ["troubled", "melancholy"]:
                resilience_boost = len(negative_interactions) * 0.02
                metrics.emotional_resilience = min(1.0, metrics.emotional_resilience + resilience_boost)

        # Update social competence based on relationship quality
        if character_state.relationship_scores:
            avg_relationship = sum(character_state.relationship_scores.values()) / len(character_state.relationship_scores)
            if avg_relationship > 0.3:
                competence_boost = 0.03
                metrics.social_competence = min(1.0, metrics.social_competence + competence_boost)

        # Update self-awareness based on therapeutic interactions and reflection
        reflection_indicators = sum(1 for i in interactions
                                  if "understand" in i.content.lower() or "realize" in i.content.lower())
        if reflection_indicators > 0:
            awareness_boost = reflection_indicators * 0.04
            metrics.self_awareness = min(1.0, metrics.self_awareness + awareness_boost)

        # Update coping effectiveness based on positive outcomes from difficult situations
        if negative_interactions and positive_interactions:
            if len(positive_interactions) >= len(negative_interactions):
                coping_boost = 0.05
                metrics.coping_effectiveness = min(1.0, metrics.coping_effectiveness + coping_boost)

        # Update personality stability
        self._update_personality_stability(metrics, character_state)

        # Detect growth milestones
        self._detect_growth_milestones(metrics, character_state)

        metrics.last_assessment = datetime.now()
        metrics.validate()

        # Store in history
        self.growth_history[character_id].append(metrics)

        logger.debug(f"Updated growth metrics for character {character_id}")
        return metrics

    def _update_personality_stability(self, metrics: CharacterGrowthMetrics,
                                     character_state: CharacterState) -> None:
        """Update personality stability tracking."""
        for trait, value in character_state.personality_traits.items():
            if trait not in metrics.personality_stability:
                metrics.personality_stability[trait] = 0.5

            # Calculate stability based on how much the trait has changed
            # This is simplified - in full implementation would track historical changes
            current_stability = metrics.personality_stability[trait]

            # Extreme values are less stable
            if abs(value) > 0.8:
                stability_change = -0.02
            else:
                stability_change = 0.01

            metrics.personality_stability[trait] = max(0.0, min(1.0,
                                                              current_stability + stability_change))

    def _detect_growth_milestones(self, metrics: CharacterGrowthMetrics,
                                 character_state: CharacterState) -> None:
        """Detect and record significant growth milestones."""
        milestones = []

        # Therapeutic progress milestones
        if metrics.therapeutic_progress > 0.25 and "25% therapeutic progress" not in metrics.growth_milestones:
            milestones.append("25% therapeutic progress")
        if metrics.therapeutic_progress > 0.5 and "50% therapeutic progress" not in metrics.growth_milestones:
            milestones.append("50% therapeutic progress")
        if metrics.therapeutic_progress > 0.75 and "75% therapeutic progress" not in metrics.growth_milestones:
            milestones.append("75% therapeutic progress")

        # Emotional resilience milestones
        if metrics.emotional_resilience > 0.7 and "high emotional resilience" not in metrics.growth_milestones:
            milestones.append("high emotional resilience")

        # Social competence milestones
        if metrics.social_competence > 0.8 and "strong social skills" not in metrics.growth_milestones:
            milestones.append("strong social skills")

        # Self-awareness milestones
        if metrics.self_awareness > 0.8 and "high self-awareness" not in metrics.growth_milestones:
            milestones.append("high self-awareness")

        # Add new milestones
        for milestone in milestones:
            if milestone not in metrics.growth_milestones:
                metrics.growth_milestones.append(milestone)
                logger.info(f"Character {metrics.character_id} achieved milestone: {milestone}")

    def get_character_growth_analysis(self, character_id: str) -> dict[str, Any]:
        """Get detailed analysis of character growth."""
        if character_id not in self.growth_metrics:
            return {"error": "Character growth not tracked"}

        metrics = self.growth_metrics[character_id]
        history = self.growth_history.get(character_id, [])

        # Calculate growth trends
        trends = {}
        if len(history) > 1:
            recent = history[-1]
            previous = history[-2]

            trends = {
                "therapeutic_progress_trend": recent.therapeutic_progress - previous.therapeutic_progress,
                "emotional_resilience_trend": recent.emotional_resilience - previous.emotional_resilience,
                "social_competence_trend": recent.social_competence - previous.social_competence,
                "self_awareness_trend": recent.self_awareness - previous.self_awareness,
                "coping_effectiveness_trend": recent.coping_effectiveness - previous.coping_effectiveness
            }

        # Calculate overall growth score
        growth_components = [
            metrics.therapeutic_progress,
            metrics.emotional_resilience,
            metrics.social_competence,
            metrics.self_awareness,
            metrics.coping_effectiveness
        ]
        overall_growth = sum(growth_components) / len(growth_components)

        return {
            "character_id": character_id,
            "growth_pattern": metrics.growth_pattern.value,
            "overall_growth_score": overall_growth,
            "metrics": {
                "therapeutic_progress": metrics.therapeutic_progress,
                "emotional_resilience": metrics.emotional_resilience,
                "social_competence": metrics.social_competence,
                "self_awareness": metrics.self_awareness,
                "coping_effectiveness": metrics.coping_effectiveness
            },
            "personality_stability": metrics.personality_stability,
            "growth_milestones": metrics.growth_milestones,
            "regression_events": metrics.regression_events,
            "trends": trends,
            "last_assessment": metrics.last_assessment,
            "history_length": len(history)
        }


class PersonalityConsistencyValidator:
    """Validates character personality maintenance and consistency."""

    def __init__(self):
        self.consistency_thresholds = {
            "major_change": 0.3,      # Significant personality change
            "moderate_change": 0.15,   # Moderate personality change
            "minor_change": 0.05       # Minor personality change
        }

    def validate_personality_consistency(self, character_state: CharacterState,
                                       historical_states: list[CharacterState],
                                       time_period: timedelta) -> tuple[bool, list[str]]:
        """Validate that personality changes are consistent and realistic."""
        if not historical_states:
            return True, []

        issues = []
        recent_state = historical_states[-1]

        # Check for unrealistic personality changes
        for trait, current_value in character_state.personality_traits.items():
            if trait in recent_state.personality_traits:
                historical_value = recent_state.personality_traits[trait]
                change = abs(current_value - historical_value)

                # Determine if change is too rapid for the time period
                days = max(1, time_period.days)
                change_rate = change / days

                if change_rate > 0.1:  # More than 0.1 change per day is unrealistic
                    issues.append(f"Unrealistic change rate for {trait}: {change_rate:.3f} per day")
                elif change > self.consistency_thresholds["major_change"]:
                    if days < 7:  # Major changes shouldn't happen in less than a week
                        issues.append(f"Major personality change in {trait} too rapid: {change:.3f} in {days} days")

        # Check for mood consistency with personality
        mood_personality_consistency = self._validate_mood_personality_consistency(character_state)
        if not mood_personality_consistency[0]:
            issues.extend(mood_personality_consistency[1])

        # Check for dialogue style consistency
        dialogue_consistency = self._validate_dialogue_style_consistency(character_state, historical_states)
        if not dialogue_consistency[0]:
            issues.extend(dialogue_consistency[1])

        is_consistent = len(issues) == 0
        return is_consistent, issues

    def _validate_mood_personality_consistency(self, character_state: CharacterState) -> tuple[bool, list[str]]:
        """Validate that current mood is consistent with personality traits."""
        issues = []
        traits = character_state.personality_traits
        mood = character_state.current_mood

        # Check for mood-personality mismatches
        if mood == "cheerful" and traits.get("neuroticism", 0) > 0.7:
            issues.append("Cheerful mood inconsistent with high neuroticism")

        if mood == "troubled" and traits.get("emotional_resilience", 0.5) > 0.8:
            issues.append("Troubled mood inconsistent with high emotional resilience")

        if mood == "melancholy" and traits.get("extraversion", 0) > 0.6:
            issues.append("Melancholy mood inconsistent with high extraversion")

        return len(issues) == 0, issues

    def _validate_dialogue_style_consistency(self, character_state: CharacterState,
                                           historical_states: list[CharacterState]) -> tuple[bool, list[str]]:
        """Validate that dialogue style changes are consistent."""
        if not historical_states:
            return True, []

        issues = []
        current_style = character_state.dialogue_style
        recent_style = historical_states[-1].dialogue_style

        # Check for major dialogue style changes
        style_changes = {
            "formality_level": abs(current_style.formality_level - recent_style.formality_level),
            "empathy_level": abs(current_style.empathy_level - recent_style.empathy_level),
            "directness": abs(current_style.directness - recent_style.directness),
            "humor_usage": abs(current_style.humor_usage - recent_style.humor_usage)
        }

        for aspect, change in style_changes.items():
            if change > 0.3:  # Major change in dialogue style
                issues.append(f"Major change in dialogue {aspect}: {change:.3f}")

        return len(issues) == 0, issues

    def suggest_personality_adjustments(self, character_state: CharacterState,
                                      target_consistency: float = 0.8) -> dict[str, float]:
        """Suggest personality adjustments to improve consistency."""
        suggestions = {}
        traits = character_state.personality_traits

        # Suggest adjustments based on current mood
        if character_state.current_mood == "cheerful":
            if traits.get("neuroticism", 0) > 0.5:
                suggestions["neuroticism"] = max(-1.0, traits["neuroticism"] - 0.2)
            if traits.get("extraversion", 0) < 0.3:
                suggestions["extraversion"] = min(1.0, traits["extraversion"] + 0.15)

        elif character_state.current_mood == "troubled":
            if traits.get("emotional_resilience", 0.5) > 0.7:
                suggestions["emotional_resilience"] = traits["emotional_resilience"] - 0.1
            if traits.get("neuroticism", 0) < 0.2:
                suggestions["neuroticism"] = min(1.0, traits["neuroticism"] + 0.15)

        # Suggest adjustments based on therapeutic role
        if character_state.therapeutic_role == "therapist":
            if traits.get("empathy", 0.5) < 0.7:
                suggestions["empathy"] = min(1.0, traits["empathy"] + 0.1)
            if traits.get("patience", 0.5) < 0.6:
                suggestions["patience"] = min(1.0, traits["patience"] + 0.1)

        return suggestions


# Integration functions
def create_advanced_relationship_system() -> tuple[RelationshipEvolutionEngine, CharacterGrowthTracker, PersonalityConsistencyValidator]:
    """Create and return all advanced relationship system components."""
    evolution_engine = RelationshipEvolutionEngine()
    growth_tracker = CharacterGrowthTracker()
    consistency_validator = PersonalityConsistencyValidator()

    logger.info("Advanced relationship system components created")
    return evolution_engine, growth_tracker, consistency_validator


def validate_relationship_evolution_system() -> bool:
    """Validate the relationship evolution system functionality."""
    try:
        # Create system components
        evolution_engine, growth_tracker, validator = create_advanced_relationship_system()

        # Test relationship initialization
        metrics = evolution_engine.initialize_relationship(
            "therapist_001", "patient_001", RelationshipType.THERAPEUTIC
        )
        assert metrics.validate()

        # Test interaction processing
        interaction = Interaction(
            participants=["therapist_001", "patient_001"],
            interaction_type="therapeutic",
            content="Discussed coping strategies",
            emotional_impact=0.6,
            therapeutic_value=0.8
        )

        updated_metrics = evolution_engine.update_relationship_from_interaction(
            "therapist_001", "patient_001", interaction
        )
        assert updated_metrics.therapeutic_alliance > metrics.therapeutic_alliance

        # Test character growth tracking
        from data_models import CharacterState
        character_state = CharacterState(
            character_id="patient_001",
            name="Test Patient",
            personality_traits={"empathy": 0.5, "neuroticism": 0.6}
        )

        growth_metrics = growth_tracker.update_character_growth(
            "patient_001", character_state, [interaction]
        )
        assert growth_metrics.validate()

        # Test consistency validation
        is_consistent, issues = validator.validate_personality_consistency(
            character_state, [], timedelta(days=1)
        )
        assert is_consistent

        logger.info("Relationship evolution system validation successful")
        return True

    except Exception as e:
        logger.error(f"Relationship evolution system validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run validation
    validate_relationship_evolution_system()
