"""
TTA Living Worlds System

This module implements the dynamic, persistent, and therapeutically meaningful
virtual environments that respond to player actions, evolve over time, and
provide immersive therapeutic contexts.

Components:
- WorldStateManager: Main world state tracking and persistence controller
- ChoiceImpactTracker: Player choice consequence analysis and implementation
- TherapeuticWorldBuilder: Therapeutic environment creation and management
- EvolutionEngine: Real-time world evolution and dynamic updates
- PersistenceLayer: Cross-session world state storage and retrieval
"""

from .choice_impact_tracker import ChoiceImpactTracker
from .evolution_engine import EvolutionEngine
from .models import (
    ChoiceImpact,
    ChoiceImpactType,
    EvolutionEvent,
    EvolutionTrigger,
    TherapeuticWorld,
    WorldPersistenceData,
    WorldState,
    WorldStateType,
)
from .persistence_layer import PersistenceLayer
from .therapeutic_world_builder import TherapeuticWorldBuilder
from .world_state_manager import WorldStateManager

__all__ = [
    "WorldStateManager",
    "ChoiceImpactTracker",
    "TherapeuticWorldBuilder",
    "EvolutionEngine",
    "PersistenceLayer",
    "WorldState",
    "WorldStateType",
    "ChoiceImpact",
    "ChoiceImpactType",
    "TherapeuticWorld",
    "EvolutionEvent",
    "EvolutionTrigger",
    "WorldPersistenceData",
]
