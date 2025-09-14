import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestOnDemandHistoryGeneration(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="history_world",
            initial_characters=[{"id": "char_hist", "name": "Historian"}],
            initial_locations=[{"id": "loc_hist", "name": "Archive"}],
            initial_objects=[{"id": "obj_hist", "name": "Relic"}],
        )
        self.world_id = "world_hist"
        self.wsm.initialize_world(self.world_id, config)

    def test_character_history_cached(self):
        h1 = self.wsm.get_character_history(self.world_id, "char_hist", detail_level=5)
        self.assertIn("character_id", h1)
        self.assertEqual(h1["character_id"], "char_hist")
        # Call again to hit cache path
        h2 = self.wsm.get_character_history(self.world_id, "char_hist", detail_level=5)
        self.assertEqual(h2["character_id"], "char_hist")

    def test_object_history_days_filter(self):
        # Add an older event and a recent event to the object's timeline
        tl = self.wsm.timeline_engine.get_timeline("obj_hist")
        from datetime import datetime, timedelta

        from models.living_worlds_models import EventType, TimelineEvent
        old_event = TimelineEvent(event_type=EventType.CREATION, title="old", description="past", timestamp=datetime.now() - timedelta(days=120))
        recent_event = TimelineEvent(event_type=EventType.OBJECT_MODIFICATION, title="recent", description="now", timestamp=datetime.now() - timedelta(days=5))
        tl.add_event(old_event)
        tl.add_event(recent_event)

        h = self.wsm.get_object_history(self.world_id, "obj_hist", detail_level=3, days=30)
        titles = [e["title"] for e in h["timeline_events"]]
        self.assertIn("recent", titles)
        self.assertNotIn("old", titles)

    def test_location_history_basic(self):
        h = self.wsm.get_location_history(self.world_id, "loc_hist", detail_level=2)
        self.assertIn("location_id", h)
        self.assertEqual(h["location_id"], "loc_hist")


if __name__ == "__main__":
    unittest.main()

