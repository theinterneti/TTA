"""Knowledge package for the TTA project.

This package exposes submodules without importing heavy dependencies at package import time.
Import specific submodules directly, e.g.:
    from tta.prod.src.knowledge.neo4j_manager import Neo4jManager, get_neo4j_manager
"""

__all__ = [
    # Intentionally empty; import from submodules directly to avoid import-time side effects
]
