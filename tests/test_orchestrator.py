"""
Test the TTA Orchestrator.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAOrchestrator, TTAConfig
from src.orchestration.component import ComponentStatus


class TestOrchestrator(unittest.TestCase):
    """Test the TTA Orchestrator."""
    
    def setUp(self):
        """Set up the test."""
        # Create a test configuration
        self.config = TTAConfig()
        
        # Create the orchestrator
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
        self.assertIn("tta.prototype_neo4j", self.orchestrator.components["tta.prototype_app"].dependencies)


if __name__ == "__main__":
    unittest.main()
