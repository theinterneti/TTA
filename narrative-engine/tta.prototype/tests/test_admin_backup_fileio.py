import os
import sys
import tempfile
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestAdminBackupFileIO(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        cfg = WorldConfig(world_name="fileio", initial_characters=[], initial_locations=[], initial_objects=[])
        self.world_id = "world_fileio"
        self.wsm.initialize_world(self.world_id, cfg)

    def test_export_import_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "world.json")
            ok = self.wsm.export_world_state_to_file(self.world_id, path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(path))

            # Import into a fresh manager
            wsm2 = WorldStateManager()
            ws2 = wsm2.import_world_state_from_file(path)
            self.assertIsNotNone(ws2)
            self.assertEqual(ws2.world_id, self.world_id)


if __name__ == "__main__":
    unittest.main()

