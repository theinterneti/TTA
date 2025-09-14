import sys
import unittest
from pathlib import Path

# Add the core path for imports (mirror integration tests pattern)
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

from narrative_branching import ChoiceOption, ChoiceType
from world_state_manager import WorldConfig, WorldStateManager


class TestWorldStateManagerPlayerChoice(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="test_world",
            initial_characters=[{"id": "char_a", "name": "Alice"}],
            initial_locations=[{"id": "loc_a", "name": "Square", "description": "Town square"}],
        )
        self.world_id = "world_choice"
        self.wsm.initialize_world(self.world_id, config)

    def test_process_player_choice_creates_timeline_events(self):
        # Prepare a dialogue choice
        choice = ChoiceOption(
            choice_id="c1",
            choice_text="Greet the character",
            choice_type=ChoiceType.DIALOGUE,
            therapeutic_weight=0.1,
        )
        context = {
            "player_id": "player_1",
            "characters_present": ["char_a"],
            "current_location": "loc_a",
            "emotional_state": {"happiness": 0.3},
            "confidence_level": 0.7,
            "response_time": 2.0,
        }

        result = self.wsm.process_player_choice(self.world_id, choice, context)

        # Basic assertions about result structure
        self.assertTrue(result.get("success"))
        self.assertIn("choice_id", result)
        self.assertIn("impact", result)
        self.assertIn("feedback", result)

        # Verify at least one timeline event added to char_a or loc_a
        te = self.wsm.timeline_engine
        char_tl = te.get_timeline("char_a")
        loc_tl = te.get_timeline("loc_a")
        self.assertIsNotNone(char_tl)
        self.assertIsNotNone(loc_tl)

        any_new = len(char_tl.events) > 0 or len(loc_tl.events) > 0
        self.assertTrue(any_new)


if __name__ == "__main__":
    unittest.main()

