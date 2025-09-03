"""
Character Arc Interfaces Module

This module defines abstract interfaces and shared data structures for character arc
management, breaking circular dependencies between character_arc_integration and
character_arc_manager modules.

Classes:
    CharacterArcIntegrationInterface: Abstract interface for integration
    CharacterArcManagerInterface: Abstract interface for manager
    Shared data structures and enums
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class RelationshipType(Enum):
    """Types of character relationships."""
    FRIEND = "friend"
    RIVAL = "rival"
    MENTOR = "mentor"
    STUDENT = "student"
    FAMILY = "family"
    ROMANTIC = "romantic"
    NEUTRAL = "neutral"
    ENEMY = "enemy"


class ArcStage(Enum):
    """Stages of character development arc."""
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


@dataclass
class RelationshipState:
    """State of a relationship between characters."""
    character_a_id: str
    character_b_id: str
    relationship_type: RelationshipType
    strength: float = 0.5  # 0.0 to 1.0
    trust_level: float = 0.5  # 0.0 to 1.0
    conflict_level: float = 0.0  # 0.0 to 1.0
    shared_experiences: list[str] = field(default_factory=list)
    last_interaction: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterArc:
    """Character development arc data structure."""
    character_id: str
    arc_name: str
    current_stage: ArcStage
    progress: float = 0.0  # 0.0 to 1.0
    key_events: list[str] = field(default_factory=list)
    personality_changes: dict[str, float] = field(default_factory=dict)
    relationship_changes: list[RelationshipState] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionContext:
    """Context for character interactions."""
    interaction_id: str
    characters_involved: list[str]
    interaction_type: str
    location: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_context: dict[str, float] = field(default_factory=dict)
    narrative_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerInteraction:
    """Player interaction with characters."""
    interaction_id: str
    player_id: str
    character_id: str
    interaction_content: str
    player_choice: str | None = None
    character_response: str | None = None
    emotional_impact: dict[str, float] = field(default_factory=dict)
    relationship_impact: RelationshipState | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class CharacterArcIntegrationInterface(ABC):
    """Abstract interface for character arc integration."""

    @abstractmethod
    async def sync_character_data(self, character_id: str) -> bool:
        """Synchronize character data between systems."""
        pass

    @abstractmethod
    async def update_relationship_dynamics(
        self,
        character_a_id: str,
        character_b_id: str,
        interaction_context: InteractionContext
    ) -> RelationshipState:
        """Update relationship dynamics based on interaction."""
        pass

    @abstractmethod
    async def get_character_arc_progress(self, character_id: str) -> CharacterArc | None:
        """Get character arc progress."""
        pass


class CharacterArcManagerInterface(ABC):
    """Abstract interface for character arc manager."""

    @abstractmethod
    async def create_character_arc(
        self,
        character_id: str,
        arc_name: str,
        initial_stage: ArcStage = ArcStage.INTRODUCTION
    ) -> CharacterArc:
        """Create a new character arc."""
        pass

    @abstractmethod
    async def update_character_arc(
        self,
        character_id: str,
        arc_updates: dict[str, Any]
    ) -> CharacterArc | None:
        """Update character arc progress."""
        pass

    @abstractmethod
    async def process_player_interaction(
        self,
        interaction: PlayerInteraction
    ) -> InteractionContext:
        """Process player interaction and update character arcs."""
        pass

    @abstractmethod
    async def get_relationship_state(
        self,
        character_a_id: str,
        character_b_id: str
    ) -> RelationshipState | None:
        """Get current relationship state between characters."""
        pass


class IntegrationProtocol(Protocol):
    """Protocol for integration between character arc systems."""

    def register_integration(self, integration: CharacterArcIntegrationInterface) -> None:
        """Register integration interface."""
        ...

    def get_integration(self) -> CharacterArcIntegrationInterface | None:
        """Get registered integration interface."""
        ...


# Shared utility functions
def calculate_relationship_strength(
    interactions: list[PlayerInteraction],
    base_strength: float = 0.5
) -> float:
    """Calculate relationship strength based on interactions."""
    if not interactions:
        return base_strength

    # Simple calculation based on interaction frequency and emotional impact
    total_impact = sum(
        sum(interaction.emotional_impact.values())
        for interaction in interactions
    )

    # Normalize and combine with base strength
    normalized_impact = min(total_impact / len(interactions), 1.0)
    return min((base_strength + normalized_impact) / 2, 1.0)


def determine_arc_stage_progression(
    current_stage: ArcStage,
    progress: float,
    key_events: list[str]
) -> ArcStage:
    """Determine if character arc should progress to next stage."""
    if progress < 0.2:
        return ArcStage.INTRODUCTION
    elif progress < 0.4:
        return ArcStage.RISING_ACTION
    elif progress < 0.6:
        return ArcStage.CLIMAX
    elif progress < 0.8:
        return ArcStage.FALLING_ACTION
    else:
        return ArcStage.RESOLUTION


# Export all interfaces and data structures
__all__ = [
    "RelationshipType",
    "ArcStage",
    "RelationshipState",
    "CharacterArc",
    "InteractionContext",
    "PlayerInteraction",
    "CharacterArcIntegrationInterface",
    "CharacterArcManagerInterface",
    "IntegrationProtocol",
    "calculate_relationship_strength",
    "determine_arc_stage_progression",
]
