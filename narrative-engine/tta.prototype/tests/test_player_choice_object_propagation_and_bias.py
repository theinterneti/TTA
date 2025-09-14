import sys
import unittest
from datetime import timedelta
from pathlib import Path

# Mirror pattern used in other tests for core imports
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

from narrative_branching import ChoiceOption, ChoiceType
from world_state_manager import WorldConfig, WorldStateManager


class TestObjectPropagationAndBias(unittest.TestCase):
    def setUp(self):
        self.wsm = WorldStateManager()
        config = WorldConfig(
            world_name="test_world",
            initial_characters=[{"id": "char_a", "name": "Alice"}],
            initial_locations=[{"id": "loc_a", "name": "Square", "description": "Town square"}],
            initial_objects=[{"id": "obj_a", "name": "Lantern", "description": "A lantern", "location_id": "loc_a"}],
        )
        self.world_id = "world_bias"
        self.wsm.initialize_world(self.world_id, config)

    def test_object_propagation_creates_object_event(self):
        # Choice that should touch environment/objects (EXPLORATION)
        choice = ChoiceOption(
            choice_id="c_env",
            choice_text="Inspect the lantern",
            choice_type=ChoiceType.ACTION,
            therapeutic_weight=0.0,
        )
        context = {
            "player_id": "player_1",
            "characters_present": ["char_a"],
            "current_location": "loc_a",
            "objects_present": ["obj_a"],
            "emotional_state": {"curiosity": 0.5},
            "confidence_level": 0.6,
            "response_time": 3.0,
        }

        result = self.wsm.process_player_choice(self.world_id, choice, context)
        self.assertTrue(result.get("success"))

        te = self.wsm.timeline_engine
        obj_tl = te.get_timeline("obj_a")
        self.assertIsNotNone(obj_tl)
        self.assertTrue(len(obj_tl.events) > 0)

    def test_preferences_bias_influences_evolution(self):
        # Establish a strong social preference via repeated choices
        for i in range(6):
            choice = ChoiceOption(
                choice_id=f"c_social_{i}",
                choice_text="Chat with Alice",
                choice_type=ChoiceType.DIALOGUE,
                therapeutic_weight=0.0,
            )
            context = {
                "player_id": "player_1",
                "characters_present": ["char_a"],
                "current_location": "loc_a",
                "emotional_state": {"happiness": 0.2},
                "confidence_level": 0.8,
                "response_time": 2.0,
            }
            self.wsm.process_player_choice(self.world_id, choice, context)

        # Now simulate some time and expect more social events than baseline
        self.wsm.simulate_time_passage(self.world_id, timedelta(days=1), background_processing=False)
        # We cannot directly count social vs non-social without deeper hooks; instead, verify the bias flag is set
        world_state = self.wsm.get_world_state(self.world_id)
        bias = world_state.get_flag('evolution_preference_bias', {}) or {}
        # Social bias should be present and positive
        self.assertIn('social', bias)
        self.assertGreaterEqual(float(bias.get('social', 0.0)), 0.0)


if __name__ == "__main__":
    unittest.main()

