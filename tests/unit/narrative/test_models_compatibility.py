# Logseq: [[TTA.dev/Tests/Test_models_compatibility]]
import pytest

pytest.importorskip("tta_narrative")
from tta_narrative.coherence import (
    ConsistencyIssue,
    ConsistencyIssueType,
    ValidationSeverity,
)
from tta_narrative.orchestration.models import (
    NarrativeEvent,
    NarrativeScale,
)

pytestmark = pytest.mark.unit


def test_narrative_coherence_models_importable():
    """Narrative coherence models importable."""
    assert ValidationSeverity.ERROR.value == "error"
    assert ConsistencyIssueType.LORE_VIOLATION.value == "lore_violation"
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.ERROR,
        description="",
    )
    assert issue.issue_id == "i1"


def test_narrative_arc_models_importable():
    """Narrative arc models importable."""
    assert NarrativeScale.SHORT_TERM.value == "short_term"
    ev = NarrativeEvent(
        event_id="e1",
        scale=NarrativeScale.SHORT_TERM,
        timestamp=__import__("datetime").datetime.now(),
    )
    assert ev.event_id == "e1"
