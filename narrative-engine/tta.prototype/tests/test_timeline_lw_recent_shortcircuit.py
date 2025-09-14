import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestTimelineLWRecentShortCircuit(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="shortcircuit_world",
            initial_characters=[{"id": "char_x", "name": "X"}],
            initial_locations=[],
            initial_objects=[],
        )
        self.world_id = "world_sc"
        self.wsm.initialize_world(self.world_id, config)

    def test_recent_short_circuit(self):
        lwc = self.wsm.lw_cache
        # seed recent events in LW keyspace
        seeded = [{"event_id": "e1", "title": "seed", "event_type": "daily_life", "timestamp": "2025-01-01T00:00:00"}]
        lwc.set_recent_timeline_events(self.world_id, "char_x", seeded, ttl=120)

        # get timeline_id for char_x
        tl = self.wsm.timeline_engine.get_timeline("char_x")
        timeline_id = tl.timeline_id
        # call through persistence facade with optional world/entity context
        events = self.wsm.persistence.get_timeline_events(timeline_id, limit=10, min_significance=1, world_id=self.world_id, entity_id="char_x")
        # Should return the seeded event without hitting Neo4j (we can't assert Neo4j access here, but we can assert correct data path)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "seed")


if __name__ == "__main__":
    unittest.main()

