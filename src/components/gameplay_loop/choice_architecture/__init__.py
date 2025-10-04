"""
Choice Architecture System for Therapeutic Text Adventure

This module implements the choice architecture system that generates meaningful choices,
validates therapeutic relevance, and protects player agency while supporting
therapeutic goals and narrative progression.
"""

from .agency_protector import AgencyProtector
from .generator import ChoiceGenerator, ChoiceTemplate
from .manager import ChoiceArchitectureManager
from .validator import ChoiceValidator

__all__ = [
    "ChoiceArchitectureManager",
    "ChoiceGenerator",
    "ChoiceTemplate",
    "ChoiceValidator",
    "AgencyProtector",
]
