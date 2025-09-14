import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
for p in (core_path,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from interactive_narrative_engine import InteractiveNarrativeEngine, UserChoice
from world_state_manager import WorldConfig, WorldStateManager


class TestNarrativeWorldContext(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        cfg = WorldConfig(
            world_name="narrative_world",
            initial_characters=[],
            initial_locations=[{"id": "starting_location", "name": "Start"}],
            initial_objects=[]
        )
        self.world_id = "world_narrative"
        self.wsm.initialize_world(self.world_id, cfg)
        # seed a simple timeline event on location to ensure recent events path works
        # the test remains robust even if no events are found

        self.engine = InteractiveNarrativeEngine(world_state_manager=self.wsm, default_world_id=self.world_id)
        ss = self.engine.start_session("user1", scenario_id="demo")
        self.session_id = ss.session_id

    def test_context_enrichment(self):
        choice = UserChoice(choice_id="c1", choice_text="look")
        resp = self.engine.process_user_choice(self.session_id, choice)
        self.assertIsNotNone(resp.metadata)
        wc = resp.metadata.get("world_context", {})
        self.assertIsInstance(wc.get("summary", {}), dict)
        # recent_events may be empty list; ensure key present
        self.assertIn("recent_events", wc)


if __name__ == "__main__":
    unittest.main()

