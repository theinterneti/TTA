from tta_narrative.orchestration.causal_graph import *  # just ensure module loads
from tta_narrative.orchestration.conflict_detection import ScaleConflict
from tta_narrative.orchestration.impact_analysis import ImpactAssessment
from tta_narrative.orchestration.resolution_engine import Resolution

# Verify narrative_arc_orchestrator facades import and names exist
from tta_narrative.orchestration.scale_manager import ScaleManager
from tta_narrative.coherence.causal_validator import CausalValidator
from tta_narrative.coherence.coherence_validator import CoherenceValidator

# Verify narrative_coherence facades import and names exist
from tta_narrative.coherence.contradiction_detector import (
    ContradictionDetector,
)
from tta_narrative.coherence.rules import (
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
