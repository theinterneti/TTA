import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestAdminHelpers(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="admin_helpers",
            initial_characters=[{"id": "char_h", "name": "H"}],
            initial_locations=[{"id": "loc_h", "name": "LH"}],
            initial_objects=[{"id": "obj_h", "name": "OH"}],
        )
        self.world_id = "world_h"
        self.wsm.initialize_world(self.world_id, config)

    def test_get_world_summary(self):
        summary = self.wsm.get_world_summary(self.world_id)
        if hasattr(summary, 'world_id'):
            # legacy object form
            self.assertEqual(summary.world_id, self.world_id)
        else:
            # dict form
            self.assertEqual(summary["world_id"], self.world_id)
        # also test the dict API explicitly
        sd = self.wsm.get_world_summary_dict(self.world_id)
        self.assertIn("active_characters_count", sd)
        self.assertIn("evolution_paused", sd)

    def test_export_import_world_state(self):
        exported = self.wsm.export_world_state(self.world_id)
        self.assertIsInstance(exported, str)
        # Simulate import into manager (this overwrites same world id)
        imported = self.wsm.import_world_state(exported)
        self.assertIsNotNone(imported)
        self.assertEqual(imported.world_id, self.world_id)


if __name__ == "__main__":
    unittest.main()

