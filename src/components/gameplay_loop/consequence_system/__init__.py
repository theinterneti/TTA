"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Consequence_system/__init__]]

# Logseq: [[TTA/Components/Gameplay_loop/Consequence_system/__init__]]
Consequence System for Therapeutic Text Adventure

This module implements the consequence system that generates logical, meaningful
outcomes from player choices while framing them as therapeutic learning
opportunities and providing clear causality explanations for player growth.

The consequence system consists of:

1. ConsequenceSystem: Main orchestrator for generating and managing consequences
2. OutcomeGenerator: Generates logical outcomes based on choice analysis
3. TherapeuticFramer: Frames consequences as learning opportunities
4. CausalityExplainer: Provides clear explanations of cause-and-effect relationships
5. ProgressTracker: Tracks therapeutic progress through consequences

Key Features:
- Logical consequence generation based on choice analysis
- Therapeutic framing of all outcomes as learning opportunities
- Clear causality explanations to support player understanding
- Progress tracking through consequence patterns
- Integration with narrative flow and character development
"""

from .causality_explainer import CausalityExplainer
from .outcome_generator import OutcomeGenerator
from .progress_tracker import ProgressTracker
from .system import ConsequenceSystem
from .therapeutic_framer import TherapeuticFramer

__all__ = [
    "ConsequenceSystem",
    "OutcomeGenerator",
    "TherapeuticFramer",
    "CausalityExplainer",
    "ProgressTracker",
]
