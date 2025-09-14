import os
import sys

import pytest

# Ensure repository root is on sys.path so `import tta.prototype` works under pytest
# tests/ is under repo/tta.prototype/tests -> go two levels up to repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tta.prototype.core.interactive_narrative_engine import (
    InteractiveNarrativeEngine,
    UserChoice,
)


@pytest.mark.asyncio
async def test_progress_adaptation_metadata_attached(monkeypatch):
    # Create engine with minimal deps
    engine = InteractiveNarrativeEngine(redis_cache=None, neo4j_manager=None)

    # Start session
    session = engine.start_session(user_id="user_meta_test", scenario_id="default")

    # Ensure progress adaptation is available
    assert engine.progress_adaptation is not None

    # Process a simple choice
    choice = UserChoice(choice_id="c1", choice_text="look around")
    response = engine.process_user_choice(session.session_id, choice)

    # Validate adaptation metadata is present
    assert isinstance(response.metadata, dict)
    adaptation = response.metadata.get("adaptation")
    assert adaptation is not None
    assert "strategy" in adaptation
    assert "journey_phase" in adaptation

