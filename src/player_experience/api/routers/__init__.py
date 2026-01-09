"""

# Logseq: [[TTA.dev/Player_experience/Api/Routers/__init__]]
API routers for the Player Experience Interface.

This package contains all the FastAPI routers for different API endpoints.
"""

from typing import TYPE_CHECKING

# Import routers with graceful fallback for missing dependencies
# This allows the package to be imported even if some routers have missing dependencies

__all__ = [
    "auth",
    "characters",
    "chat",
    "conversation",
    "franchise_worlds",
    "gameplay",
    "metrics",
    "openrouter_auth",
    "players",
    "privacy",
    "progress",
    "sessions",
    "settings",
    "worlds",
]

# For type checkers: import all modules so they're visible for static analysis
# At runtime: use lazy imports to avoid triggering import errors
if TYPE_CHECKING:
    from . import (
        auth,
        characters,
        chat,
        conversation,
        franchise_worlds,
        gameplay,
        metrics,
        openrouter_auth,
        players,
        privacy,
        progress,
        sessions,
        settings,
        worlds,
    )
else:
    # Lazy imports - modules are imported when accessed, not at package import time
    def __getattr__(name: str):
        """Lazy import routers to avoid triggering import errors at package import time."""
        if name in __all__:
            from importlib import import_module

            return import_module(f".{name}", __name__)
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
