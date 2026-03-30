"""WBA — World Building Agent.

Receives a ProcessedInput, queries Neo4j for relevant world context,
and assembles a WorldContext for the NGA.
"""

from .agent import WBAAgent

__all__ = ["WBAAgent"]
