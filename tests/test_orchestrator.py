"""
Test the TTA Orchestrator.
"""

import sys
import unittest
from pathlib import Path

import pytest

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAConfig, TTAOrchestrator


class TestOrchestrator(unittest.TestCase):
    """Test the TTA Orchestrator."""

    @classmethod
    def setUpClass(cls):
        """Check if filesystem structure exists before running tests."""
        # Check if required directories exist
        root_dir = Path(__file__).parent.parent
        tta_dev_path = root_dir / "tta.dev"
        tta_prototype_path = root_dir / "tta.prototype"

        if not (tta_dev_path.exists() and tta_prototype_path.exists()):
            pytest.skip(
                "Skipping integration tests: tta.dev and/or tta.prototype directories not found. "
                "These tests require a complete filesystem structure."
            )

    def setUp(self):
        """Set up the test."""
        # Create a test configuration
        self.config = TTAConfig()

        # Create the orchestrator (uses FilesystemComponentLoader by default)
        self.orchestrator = TTAOrchestrator()

    def test_orchestrator_initialization(self):
        """Test that the orchestrator initializes correctly."""
        # Check that the orchestrator has the correct repositories
        self.assertTrue(self.orchestrator.tta_dev_path.exists())
        self.assertTrue(self.orchestrator.tta_prototype_path.exists())

    def test_config_initialization(self):
        """Test that the configuration initializes correctly."""
        # Check that the configuration has the correct values
        self.assertTrue(self.config.get("tta.dev.enabled"))
        self.assertTrue(self.config.get("tta.prototype.enabled"))

    def test_component_registration(self):
        """Test that components are registered correctly."""
        # Check that the orchestrator has the correct components
        self.assertIn("tta.dev_neo4j", self.orchestrator.components)
        self.assertIn("tta.dev_llm", self.orchestrator.components)
        self.assertIn("tta.prototype_neo4j", self.orchestrator.components)
        self.assertIn("tta.prototype_app", self.orchestrator.components)

    def test_component_dependencies(self):
        """Test that component dependencies are correct."""
        # Check that the app component depends on the neo4j component
        self.assertIn(
            "tta.prototype_neo4j",
            self.orchestrator.components["tta.prototype_app"].dependencies,
        )


if __name__ == "__main__":
    unittest.main()
