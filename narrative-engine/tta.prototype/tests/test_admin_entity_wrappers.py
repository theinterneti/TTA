import sys
import unittest
from pathlib import Path

core_path = Path(__file__).parent.parent / "core"
db_path = Path(__file__).parent.parent / "database"
for p in (core_path, db_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldConfig, WorldStateManager


class TestAdminEntityWrappers(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="admin_entities",
            initial_characters=[],
            initial_locations=[],
            initial_objects=[],
        )
        self.world_id = "world_admin_entities"
        self.wsm.initialize_world(self.world_id, config)

    def test_add_remove_character(self):
        self.assertTrue(self.wsm.add_character(self.world_id, "char_new", {"name": "Newbie"}))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertIn("char_new", ws.active_characters)
        self.assertTrue(self.wsm.remove_character(self.world_id, "char_new"))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertNotIn("char_new", ws.active_characters)

    def test_add_remove_location_object(self):
        self.assertTrue(self.wsm.add_location(self.world_id, "loc_new", {"name": "Place"}))
        self.assertTrue(self.wsm.add_object(self.world_id, "obj_new", {"name": "Thing"}))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertIn("loc_new", ws.active_locations)
        self.assertIn("obj_new", ws.active_objects)
        self.assertTrue(self.wsm.remove_location(self.world_id, "loc_new"))
        self.assertTrue(self.wsm.remove_object(self.world_id, "obj_new"))
        ws = self.wsm.get_world_state(self.world_id)
        self.assertNotIn("loc_new", ws.active_locations)
        self.assertNotIn("obj_new", ws.active_objects)


if __name__ == "__main__":
    unittest.main()

