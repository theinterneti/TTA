
from src.components.narrative_arc_orchestrator.models import (
    NarrativeScale,
    PlayerChoice,
)
from src.components.narrative_arc_orchestrator.scale_manager import ScaleManager


def test_scale_manager_evaluate_choice_impact_smoke():
    sm = ScaleManager(config={})
    choice = PlayerChoice(
        choice_id="c1", session_id="s1", choice_text="Test", metadata={}
    )
    res = sm.get_scale_window(NarrativeScale.SHORT_TERM)
    assert isinstance(res, int)


def test_scale_manager_creates_event_when_magnitude_threshold(monkeypatch):
    sm = ScaleManager(config={})
    choice = PlayerChoice(
        choice_id="c2", session_id="s1", choice_text="Test", metadata={}
    )

    async def fake_assess(choice, scale):
        from src.components.narrative_arc_orchestrator.models import ImpactAssessment

        return ImpactAssessment(scale=scale, magnitude=0.9)

    monkeypatch.setattr(sm, "_assess_scale_impact", fake_assess)

    import asyncio

    events_before = len(sm.get_active_events())
    asyncio.get_event_loop().run_until_complete(
        sm.evaluate_choice_impact(choice, [NarrativeScale.SHORT_TERM])
    )
    events_after = len(sm.get_active_events())
    assert events_after == events_before + 1
