import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
for p in (core_path,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from interactive_narrative_engine import InteractiveNarrativeEngine, UserChoice
from world_state_manager import WorldConfig, WorldStateManager


class TestNarrativeE2EWorldIntegration(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        cfg = WorldConfig(
            world_name="narrative_e2e",
            initial_characters=[{"id": "char_e", "name": "E"}],
            initial_locations=[{"id": "loc_e", "name": "Place E"}],
            initial_objects=[]
        )
        self.world_id = "world_narrative_e2e"
        self.wsm.initialize_world(self.world_id, cfg)
        self.engine = InteractiveNarrativeEngine(world_state_manager=self.wsm, default_world_id=self.world_id)
        ss = self.engine.start_session("userX", scenario_id="demo")
        ss.current_location_id = "loc_e"
        self.session_id = ss.session_id

    def test_e2e_flow(self):
        # First: process choice, expect world_context summary and possibly empty recent events
        resp1 = self.engine.process_user_choice(self.session_id, UserChoice(choice_id="c1", choice_text="look around"))
        wc1 = (resp1.metadata or {}).get("world_context", {})
        self.assertIn("summary", wc1)
        self.assertIn("recent_events", wc1)

        # Confirm a timeline event was created for the location
        tl = self.wsm.timeline_engine.get_timeline("loc_e")
        self.assertIsNotNone(tl)
        before_count = len(tl.events)

        # Second: another choice should create another timeline event
        self.engine.process_user_choice(self.session_id, UserChoice(choice_id="c2", choice_text="move on"))
        tl2 = self.wsm.timeline_engine.get_timeline("loc_e")
        self.assertGreaterEqual(len(tl2.events), before_count + 1)

        # Third: context should include recent events (now non-empty)
        resp3 = self.engine.process_user_choice(self.session_id, UserChoice(choice_id="c3", choice_text="reflect"))
        wc3 = (resp3.metadata or {}).get("world_context", {})
        recents = wc3.get("recent_events", [])
        self.assertIsInstance(recents, list)
        self.assertGreaterEqual(len(recents), 1)


if __name__ == "__main__":
    unittest.main()

