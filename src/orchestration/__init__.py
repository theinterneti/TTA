"""
TTA Orchestration Module

This module provides orchestration capabilities for the TTA project,
coordinating both tta.dev and tta.prototype components.

Classes:
    TTAOrchestrator: Main orchestrator for the TTA project
    TTAConfig: Configuration manager for the TTA project
    Component: Base class for TTA components
    ComponentStatus: Enum representing the status of a component

Decorators:
    log_entry_exit: Decorator to log function entry and exit
    timing_decorator: Decorator to measure and log execution time
    retry: Decorator to retry a function on failure
    validate_args: Decorator to validate function arguments
    singleton: Decorator to implement the Singleton pattern
    require_config: Decorator to check if required configuration keys are present
    deprecated: Decorator to mark functions as deprecated
"""

from .orchestrator import TTAOrchestrator
from .config import TTAConfig
from .component import Component, ComponentStatus
from .decorators import (
    log_entry_exit, timing_decorator, retry, validate_args,
    singleton, require_config, deprecated
)

__all__ = [
    'TTAOrchestrator', 'TTAConfig', 'Component', 'ComponentStatus',
    'log_entry_exit', 'timing_decorator', 'retry', 'validate_args',
    'singleton', 'require_config', 'deprecated'
]
