import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
models_path = Path(__file__).parent.parent / "models"
for p in (core_path, db_path, models_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from living_worlds_models import EventType
from world_state_manager import WorldConfig, WorldStateManager


class TestRedisCachingLayer(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="cache_world",
            initial_characters=[{"id": "char_a", "name": "Alice"}],
            initial_locations=[{"id": "loc_a", "name": "Square"}],
        )
        self.world_id = "cache_world_id"
        self.wsm.initialize_world(self.world_id, config)

    def test_world_state_cached_and_warmed(self):
        lwc = self.wsm.lw_cache
        self.assertIsNotNone(lwc)
        cached = lwc.get_world_state(self.world_id)
        self.assertIsNotNone(cached)

    def test_timeline_event_invalidation(self):
        # Create an event with world_id in metadata so hook can invalidate
        ev = self.wsm.timeline_engine.create_and_add_event(
            "char_a",
            event_type=EventType.PLAYER_INTERACTION,
            title="Chat",
            description="Quick chat",
            metadata={"world_id": self.world_id},
        )
        self.assertIsNotNone(ev)
        # Setting recent and verifying invalidation increments counter when we add another
        lwc = self.wsm.lw_cache
        lwc.set_recent_timeline_events(self.world_id, "char_a", [{"id": "old"}], ttl=60)
        # Now add another event and expect invalidation
        ev2 = self.wsm.timeline_engine.create_and_add_event(
            "char_a",
            event_type=EventType.PLAYER_INTERACTION,
            title="Chat 2",
            description="Second chat",
            metadata={"world_id": self.world_id},
        )
        self.assertIsNotNone(ev2)
        # recent cache should be empty (miss) now
        recent = lwc.get_recent_timeline_events(self.world_id, "char_a")
        self.assertEqual(recent, [])


if __name__ == "__main__":
    unittest.main()

