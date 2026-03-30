"""NGA — Narrative Generation Agent.

Receives assembled world context and generates the narrative response
that is streamed back to the player.
"""

from .agent import NGAAgent

__all__ = ["NGAAgent"]
