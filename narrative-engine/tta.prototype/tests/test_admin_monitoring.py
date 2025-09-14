import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestAdminMonitoring(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="admin_world",
            initial_characters=[{"id": "char_admin", "name": "Admin"}],
            initial_locations=[],
            initial_objects=[],
        )
        self.world_id = "world_admin"
        self.wsm.initialize_world(self.world_id, config)

    def test_get_debug_metrics_summary(self):
        summary = self.wsm.get_debug_metrics_summary()
        self.assertIn("active_worlds_count", summary)
        self.assertIn("timeline_count", summary)
        self.assertIn("cache_metrics", summary)
        self.assertGreaterEqual(summary["active_worlds_count"], 1)
        self.assertGreaterEqual(summary["timeline_count"], 1)


if __name__ == "__main__":
    unittest.main()

