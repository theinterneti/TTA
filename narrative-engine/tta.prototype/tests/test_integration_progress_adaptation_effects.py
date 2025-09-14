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
async def test_adaptation_influences_response_choices(monkeypatch):
    engine = InteractiveNarrativeEngine(redis_cache=None, neo4j_manager=None)
    session = engine.start_session(user_id="user_effects", scenario_id="default")

    # Process a choice
    response = engine.process_user_choice(session.session_id, UserChoice(choice_id="c1", choice_text="explore"))

    # Ensure adaptation metadata exists
    assert isinstance(response.metadata, dict)
    adaptation = response.metadata.get("adaptation")
    assert adaptation is not None

    # Either choices are tagged with next_focus, or hints contain adaptation strategy
    tagged = any(isinstance(c, dict) and any(isinstance(t, dict) and "next_focus" in t for t in c.get("tags", [])) for c in response.choices)
    hints = response.metadata.get("hints", {})

    assert tagged or ("adaptation_strategy" in hints)

