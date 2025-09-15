from src.components.narrative_arc_orchestrator.conflict_detection import ScaleConflict
from src.components.narrative_arc_orchestrator.impact_analysis import ImpactAssessment
from src.components.narrative_arc_orchestrator.resolution_engine import Resolution

# Verify narrative_arc_orchestrator facades import and names exist
from src.components.narrative_arc_orchestrator.scale_manager import ScaleManager
from src.components.narrative_coherence.causal_validator import CausalValidator
from src.components.narrative_coherence.coherence_validator import CoherenceValidator

# Verify narrative_coherence facades import and names exist
from src.components.narrative_coherence.contradiction_detector import (
    ContradictionDetector,
)
from src.components.narrative_coherence.rules import (
    OVERALL_WEIGHTS,
    SEVERITY_WEIGHTS_LORE,
)


def test_facades_importable():
    assert ContradictionDetector is not None
    assert CoherenceValidator is not None
    assert CausalValidator is not None
    assert isinstance(SEVERITY_WEIGHTS_LORE["ERROR"], float)
    assert OVERALL_WEIGHTS["lore"] > 0


def test_arc_facades_importable():
    assert ScaleManager is not None
    assert ImpactAssessment is not None
    # Modules causal_graph loads
    assert ScaleConflict is not None
    assert Resolution is not None
