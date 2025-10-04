"""
Player Experience Interface Module

This module provides the player-facing interface for the TTA system,
including character management, world selection, and therapeutic personalization.
"""

from .managers import *
from .models import *

# NOTE: Avoid importing API at package import time to prevent heavy deps during unit tests.
# Import API modules directly as needed, e.g., `from src.player_experience.api.app import create_app`

__version__ = "1.0.0"
