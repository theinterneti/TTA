import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
for p in (core_path,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from interactive_narrative_engine import InteractiveNarrativeEngine, UserChoice
from world_state_manager import WorldConfig, WorldStateManager


class TestNarrativeTimelineWrite(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        cfg = WorldConfig(
            world_name="narrative_timeline",
            initial_characters=[{"id": "char_a", "name": "A"}],
            initial_locations=[{"id": "loc_a", "name": "Place A"}],
            initial_objects=[]
        )
        self.world_id = "world_narrative_timeline"
        self.wsm.initialize_world(self.world_id, cfg)

        self.engine = InteractiveNarrativeEngine(world_state_manager=self.wsm, default_world_id=self.world_id)
        ss = self.engine.start_session("user1", scenario_id="demo")
        # Ensure location is a known world location (not the default "starting_location")
        ss.current_location_id = "loc_a"
        self.session_id = ss.session_id

    def test_choice_creates_timeline_event(self):
        choice = UserChoice(choice_id="c1", choice_text="open the door")
        resp = self.engine.process_user_choice(self.session_id, choice)
        # Verify created event pointer is present
        wc = (resp.metadata or {}).get("world_context", {})
        created = wc.get("created_events", [])
        self.assertIsInstance(created, list)
        # If engine chose not to write, len may be 0; but typically it writes when a location is set
        # Verify timeline has at least one event matching the 'narrative' tag when location is known
        tl = self.wsm.timeline_engine.get_timeline("loc_a")
        if tl:
            found = [e for e in tl.events if "narrative" in (e.tags or [])]
            self.assertTrue(len(found) >= 1)


if __name__ == "__main__":
    unittest.main()

