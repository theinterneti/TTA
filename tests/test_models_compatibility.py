from src.components.narrative_arc_orchestrator.models import (
    NarrativeEvent,
    NarrativeScale,
)
from src.components.narrative_coherence import (
    ConsistencyIssue,
    ConsistencyIssueType,
    ValidationSeverity,
)


def test_narrative_coherence_models_importable():
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
    assert NarrativeScale.SHORT_TERM.value == "short_term"
    ev = NarrativeEvent(
        event_id="e1",
        scale=NarrativeScale.SHORT_TERM,
        timestamp=__import__("datetime").datetime.now(),
    )
    assert ev.event_id == "e1"
