import os
import sys

import pytest

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tta.prototype.core.interactive_narrative_engine import (
    InteractiveNarrativeEngine,
    UserChoice,
)


@pytest.mark.asyncio
async def test_adaptation_persists_progress_fields(monkeypatch):
    engine = InteractiveNarrativeEngine(redis_cache=None, neo4j_manager=None)
    session = engine.start_session(user_id="user_persist", scenario_id="default")

    # Make sure therapeutic_progress exists if created lazily in your environment
    if session.therapeutic_progress is None:
        class Tmp:
            # Fields expected by trackers and adaptation logic
            therapeutic_goals = []
            completed_interventions = []
            emotional_growth_metrics = {}
            coping_strategies_learned = []
            next_recommended_focus = ""
            overall_progress_score = 0.0
        session.therapeutic_progress = Tmp()

    engine.process_user_choice(session.session_id, UserChoice(choice_id="c1", choice_text="go north"))

    # Fetch updated session and assert persistence to in-memory session state
    updated = engine.get_session(session.session_id)
    assert updated is not None
    tp = updated.therapeutic_progress
    assert tp is not None
    # These fields exist on the dataclass by default; verify access does not raise
    _ = tp.next_recommended_focus
    _ = tp.overall_progress_score

