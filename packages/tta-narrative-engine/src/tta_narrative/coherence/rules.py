"""
Rules and constraint constants used by narrative coherence validators.
Lifted from narrative_coherence_engine; currently placeholders synced with existing logic.
"""

from __future__ import annotations

# Severity weights used across scoring helpers
SEVERITY_WEIGHTS_LORE = {
    # ValidationSeverity mapped at runtime in narrative_coherence_engine scoring
    # Keep numeric weights centralized here for future cohesion
    "INFO": 0.1,
    "WARNING": 0.3,
    "ERROR": 0.7,
    "CRITICAL": 1.0,
}

SEVERITY_WEIGHTS_THERAPEUTIC = {
    "INFO": 0.2,
    "WARNING": 0.5,
    "ERROR": 0.8,
    "CRITICAL": 1.0,
}

# Overall weighting blend for component scores
OVERALL_WEIGHTS = {
    "lore": 0.3,
    "character": 0.25,
    "causal": 0.25,
    "therapeutic": 0.2,
}
