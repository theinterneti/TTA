"""
Core Gameplay Loop Components

This module provides the foundational components for the therapeutic text adventure
gameplay loop system, including narrative presentation, choice architecture,
consequence systems, and adaptive difficulty management.
"""

from .base import GameplayLoopComponent
from .session_manager import SessionManager
from .narrative_engine import NarrativeEngine
from .choice_architecture import ChoiceArchitectureManager
from .consequence_system import ConsequenceSystem

__all__ = [
    "GameplayLoopComponent",
    "SessionManager", 
    "NarrativeEngine",
    "ChoiceArchitectureManager",
    "ConsequenceSystem"
]
