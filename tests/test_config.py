"""
Test the TTA Configuration.
"""

import os
import shutil
import sys
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration.config import TTAConfig


class TestTTAConfig(unittest.TestCase):
    """Test the TTA Configuration."""

    def setUp(self):
        """
        Set up the test.
        """
        self.root_dir = Path(__file__).parent.parent.parent
        self.test_config_dir = self.root_dir / "test_config_dir"
        self.test_config_dir.mkdir(exist_ok=True)
        self.default_config_path = self.root_dir / "config" / "tta_config.yaml"

        # Backup original config file if it exists
        self.original_config_content = None
        if self.default_config_path.exists():
            with open(self.default_config_path) as f:
                self.original_config_content = f.read()

        # Create a dummy default config file for testing
        self.dummy_default_config_path = self.test_config_dir / "dummy_tta_config.yaml"
        with open(self.dummy_default_config_path, "w") as f:
            f.write("""
agent_orchestration:
  enabled: true
  port: 8503
docker:
  enabled: true
  use_gpu: false
carbon:
  enabled: true
environment:
  name: development
  log_level: info
orchestration:
  components:
    player_experience:
      path: src.components.player_experience_component
      class_name: PlayerExperienceComponent
      dependencies: ["agent_orchestration"]
    agent_orchestration:
      path: src.components.agent_orchestration_component
      class_name: AgentOrchestrationComponent
""")

        # Clear singleton instance before each test
        if TTAConfig in TTAConfig._instances:
            TTAConfig._instances.clear()

        self.config = TTAConfig(self.dummy_default_config_path)  # Initialize here

    def tearDown(self):
        """
        Clean up after the test.
        """
        if self.test_config_dir.exists():
            shutil.rmtree(self.test_config_dir)

        # Restore original config file if it was backed up
        if self.original_config_content is not None:
            with open(self.default_config_path, "w") as f:
                f.write(self.original_config_content)

        # Clear singleton instance after each test
        if TTAConfig in TTAConfig._instances:
            TTAConfig._instances.clear()

        # Clean up environment variables
        for key in os.environ:
            if key.startswith("TTA_"):
                del os.environ[key]

    def test_init_default_path(self):
        """
        Test that TTAConfig initializes with the default path.
        """
        # self.config is already initialized in setUp with dummy_default_config_path
        self.assertEqual(self.config.config_path, self.dummy_default_config_path)
        self.assertIn(
            "agent_orchestration", self.config.get("orchestration.components")
        )

    def test_init_custom_path(self):
        """
        Test that TTAConfig initializes with a custom path.
        """
        custom_path = self.test_config_dir / "custom_config.yaml"
        with open(custom_path, "w") as f:
            f.write("custom_key: custom_value")

        # Create a new instance for this test
        new_config = TTAConfig(custom_path)
        self.assertEqual(new_config.config_path, custom_path)
        self.assertEqual(new_config.get("custom_key"), "custom_value")

    def test_load_config_non_existent_file(self):
        """
        Test loading config from a non-existent file.
        Should load default config.
        """
        non_existent_path = self.test_config_dir / "non_existent.yaml"
        config = TTAConfig(non_existent_path)
        self.assertIn("agent_orchestration", config.get("orchestration.components"))

    def test_load_config_invalid_format(self):
        """
        Test loading config from a file with an invalid format.
        Should load default config.
        """
        invalid_format_path = self.test_config_dir / "invalid.txt"
        with open(invalid_format_path, "w") as f:
            f.write("this is not yaml or json")

        config = TTAConfig(invalid_format_path)
        self.assertIn("agent_orchestration", config.get("orchestration.components"))

    def test_load_config_exception_during_loading(self):
        """
        Test loading config when an exception occurs during file reading.
        Should load default config.
        """
        # Simulate an exception during file reading by making the file unreadable
        unreadable_path = self.test_config_dir / "unreadable.yaml"
        with open(unreadable_path, "w") as f:
            f.write("key: value")
        os.chmod(unreadable_path, 0o000)  # Make file unreadable

        config = TTAConfig(unreadable_path)
        self.assertIn("agent_orchestration", config.get("orchestration.components"))
        os.chmod(unreadable_path, 0o644)  # Restore permissions for cleanup

    def test_get_default_config(self):
        """
        Test that the default configuration is correctly returned.
        """
        config = TTAConfig(self.dummy_default_config_path)
        default_config = config._get_default_config()
        self.assertIn("tta.dev", default_config)
        self.assertIn("agent_orchestration", default_config)
        self.assertIn("orchestration", default_config)

    def test_load_env_vars(self):
        """
        Test loading configuration from environment variables.
        """
        os.environ["TTA_AGENT_ORCHESTRATION_ENABLED"] = "false"
        os.environ["TTA_DOCKER_USE_GPU"] = "true"
        os.environ["TTA_NEW_SECTION_KEY"] = "env_value"
        os.environ["TTA_TTADEV_COMPONENTS_NEO4J_PORT"] = "7689"

        config = TTAConfig(self.dummy_default_config_path)
        self.assertFalse(config.get("agent_orchestration.enabled"))
        self.assertTrue(config.get("docker.use_gpu"))
        self.assertEqual(config.get("new_section.key"), "env_value")
        self.assertEqual(config.get("tta.dev.components.neo4j.port"), 7689)

    def test_set_nested_config(self):
        """
        Test setting a nested configuration value.
        """
        config = TTAConfig(self.dummy_default_config_path)
        config._set_nested_config(["new_key"], "new_value")
        self.assertEqual(config.get("new_key"), "new_value")

        config._set_nested_config(["level1", "level2", "level3"], "deep_value")
        self.assertEqual(config.get("level1.level2.level3"), "deep_value")

        config._set_nested_config(["tta.dev", "enabled"], False)
        self.assertFalse(config.get("tta.dev.enabled"))

    def test_get_method(self):
        """
        Test the get method for various scenarios.
        """
        config = TTAConfig(self.dummy_default_config_path)
        self.assertTrue(config.get("agent_orchestration.enabled"))
        self.assertEqual(config.get("agent_orchestration.port"), 8503)
        self.assertEqual(config.get("non_existent_key"), None)
        self.assertEqual(config.get("non_existent_key", "default_val"), "default_val")
        self.assertIn("player_experience", config.get("orchestration.components"))

    def test_set_method(self):
        """
        Test the set method.
        """
        config = TTAConfig(self.dummy_default_config_path)
        config.set("new_setting", "test_value")
        self.assertEqual(config.get("new_setting"), "test_value")

        config.set("agent_orchestration.port", 9000)
        self.assertEqual(config.get("agent_orchestration.port"), 9000)

    def test_save_method_yaml(self):
        """
        Test saving configuration to a YAML file.
        """
        save_path = self.test_config_dir / "saved_config.yaml"
        config = TTAConfig(self.dummy_default_config_path)
        config.set("test_save_key", "test_save_value")
        self.assertTrue(config.save(save_path))

        loaded_config = TTAConfig(save_path)
        self.assertEqual(loaded_config.get("test_save_key"), "test_save_value")

    def test_save_method_json(self):
        """
        Test saving configuration to a JSON file.
        """
        save_path = self.test_config_dir / "saved_config.json"
        config = TTAConfig(self.dummy_default_config_path)
        config.set("test_save_key_json", "test_save_value_json")
        self.assertTrue(config.save(save_path))

        loaded_config = TTAConfig(save_path)
        self.assertEqual(
            loaded_config.get("test_save_key_json"), "test_save_value_json"
        )

    def test_save_method_unsupported_format(self):
        """
        Test saving configuration to an unsupported file format.
        """
        save_path = self.test_config_dir / "unsupported.txt"
        config = TTAConfig(self.dummy_default_config_path)
        self.assertFalse(config.save(save_path))

    def test_save_method_exception_during_saving(self):
        """
        Test saving configuration when an exception occurs.
        """
        save_path = self.test_config_dir / "error_save.yaml"
        # Simulate an exception by making the directory unwriteable
        os.chmod(self.test_config_dir, 0o555)  # Make directory read-only

        config = TTAConfig(self.dummy_default_config_path)
        self.assertFalse(config.save(save_path))
        os.chmod(self.test_config_dir, 0o755)  # Restore permissions

    def test_validate_method_success(self):
        """
        Test successful configuration validation against default schema.
        """
        config = TTAConfig(self.dummy_default_config_path)
        self.assertTrue(config.validate())

    def test_validate_method_missing_required_key(self):
        """
        Test configuration validation with a missing required key.
        """
        config = TTAConfig(self.dummy_default_config_path)
        # Temporarily remove a required key to simulate failure
        original_value = config.config.pop("agent_orchestration")
        with self.assertRaisesRegex(
            ValueError, "Required key 'agent_orchestration' is missing"
        ):
            config.validate()
        config.config["agent_orchestration"] = original_value  # Restore

    def test_validate_method_type_mismatch(self):
        """
        Test configuration validation with a type mismatch.
        """
        config = TTAConfig(self.dummy_default_config_path)
        original_value = config.config["agent_orchestration"]["port"]
        config.config["agent_orchestration"]["port"] = "not_an_int"
        with self.assertRaisesRegex(
            ValueError, "Key 'agent_orchestration.port' must be an integer"
        ):
            config.validate()
        config.config["agent_orchestration"]["port"] = original_value  # Restore

    def test_validate_method_invalid_enum_value(self):
        """
        Test configuration validation with an invalid enum value.
        """
        config = TTAConfig(self.dummy_default_config_path)
        original_value = config.config["environment"]["log_level"]
        config.config["environment"]["log_level"] = "invalid_level"
        with self.assertRaisesRegex(
            ValueError,
            r"Key 'environment.log_level' must be one of \['debug', 'info', 'warning', 'error', 'critical'\]",
        ):
            config.validate()
        config.config["environment"]["log_level"] = original_value  # Restore

    def test_validate_method_nested_schema_failure(self):
        """
        Test configuration validation with a nested schema failure.
        """
        config = TTAConfig(self.dummy_default_config_path)
        original_value = config.config["docker"]["use_gpu"]
        config.config["docker"]["use_gpu"] = "not_a_bool"
        with self.assertRaisesRegex(
            ValueError, "Key 'docker.use_gpu' must be a boolean"
        ):
            config.validate()
        config.config["docker"]["use_gpu"] = original_value  # Restore


if __name__ == "__main__":
    unittest.main()
