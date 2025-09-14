import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestWorldStateManagerCachedAccessor(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="cached_accessor",
            initial_characters=[{"id": "char_ca", "name": "CA"}],
            initial_locations=[],
            initial_objects=[],
        )
        self.world_id = "world_ca"
        self.wsm.initialize_world(self.world_id, config)

    def test_get_recent_events_cached(self):
        # seed recent via LW cache
        lwc = self.wsm.lw_cache
        seed = [{"event_id": "e1", "title": "seed", "event_type": "daily_life", "timestamp": "2025-01-01T00:00:00"}]
        lwc.set_recent_timeline_events(self.world_id, "char_ca", seed, ttl=120)

        events = self.wsm.get_recent_events_cached("char_ca", limit=5)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "seed")


if __name__ == "__main__":
    unittest.main()

