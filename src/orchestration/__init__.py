"""
TTA Orchestration Module

This module provides orchestration capabilities for the TTA project,
coordinating both tta.dev and tta.prototype components.
"""

from .orchestrator import TTAOrchestrator
from .config import TTAConfig

__all__ = ['TTAOrchestrator', 'TTAConfig']
