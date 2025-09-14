import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestAdminControls(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="admin_controls",
            initial_characters=[{"id": "char_ac", "name": "AC"}],
            initial_locations=[],
            initial_objects=[],
        )
        self.world_id = "world_ac"
        self.wsm.initialize_world(self.world_id, config)

    def test_set_world_flags_and_pause_resume(self):
        ok = self.wsm.admin.set_world_flags(self.world_id, {"max_npcs": 10})
        self.assertTrue(ok)
        ws = self.wsm.get_world_state(self.world_id)
        self.assertEqual(ws.get_flag("max_npcs"), 10)

        self.assertTrue(self.wsm.admin.pause_evolution(self.world_id, reason="maintenance"))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertTrue(ws.get_flag("evolution_paused"))
        self.assertEqual(ws.get_flag("evolution_pause_reason"), "maintenance")

        self.assertTrue(self.wsm.admin.resume_evolution(self.world_id))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertFalse(ws.get_flag("evolution_paused"))

    def test_invalidate_caches(self):
        # ensure world state is cached
        _ = self.wsm.get_world_state(self.world_id)
        self.wsm.admin.invalidate_caches(self.world_id)
        # should be able to still retrieve state (from persistence or active cache), but cache invalidation should not error
        ws = self.wsm.get_world_state(self.world_id)
        self.assertIsNotNone(ws)


if __name__ == "__main__":
    unittest.main()

