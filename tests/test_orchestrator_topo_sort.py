# Logseq: [[TTA.dev/Tests/Test_orchestrator_topo_sort]]
import sys
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAOrchestrator


class TestOrchestratorTopoSort(unittest.TestCase):
    """Test the topological sort in TTA Orchestrator."""

    def setUp(self):
        """
        Set up the test.
        """
        # Create the orchestrator
        self.orchestrator = TTAOrchestrator()

    def test_topological_sort_simple(self):
        """
        Test topological sort with a simple graph.
        """
        graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
        sorted_order = self.orchestrator._topological_sort(graph)
        self.assertEqual(len(sorted_order), 4)
        self.assertEqual(sorted_order[0], "d")
        self.assertIn(sorted_order[1], ["b", "c"])
        self.assertIn(sorted_order[2], ["b", "c"])
        self.assertEqual(sorted_order[3], "a")

    def test_topological_sort_complex(self):
        """
        Test topological sort with a more complex graph.
        """
        graph = {
            "a": ["b", "c"],
            "b": ["d", "e"],
            "c": ["f"],
            "d": [],
            "e": ["f"],
            "f": [],
        }
        sorted_order = self.orchestrator._topological_sort(graph)
        self.assertEqual(len(sorted_order), 6)
        self.assertEqual(sorted_order[0], "d")
        self.assertEqual(sorted_order[1], "f")
        self.assertIn(sorted_order[2], ["b", "c", "e"])
        self.assertIn(sorted_order[3], ["b", "c", "e"])
        self.assertIn(sorted_order[4], ["b", "c", "e"])
        self.assertEqual(sorted_order[5], "a")

    def test_topological_sort_circular_dependency(self):
        """
        Test topological sort with a circular dependency.
        """
        graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
        sorted_order = self.orchestrator._topological_sort(graph)
        # The exact output can vary, but it should not hang and should return a partial sort
        self.assertIn(len(sorted_order), [0, 1, 2, 3])

    def test_topological_sort_empty_graph(self):
        """
        Test topological sort with an empty graph.
        """
        graph = {}
        sorted_order = self.orchestrator._topological_sort(graph)
        self.assertEqual(sorted_order, [])

    def test_topological_sort_disconnected_components(self):
        """
        Test topological sort with disconnected components.
        """
        graph = {"a": ["b"], "b": [], "c": ["d"], "d": []}
        sorted_order = self.orchestrator._topological_sort(graph)
        self.assertEqual(len(sorted_order), 4)
        self.assertIn("b", sorted_order)
        self.assertIn("d", sorted_order)
        self.assertIn("a", sorted_order)
        self.assertIn("c", sorted_order)
        self.assertLess(sorted_order.index("b"), sorted_order.index("a"))
        self.assertLess(sorted_order.index("d"), sorted_order.index("c"))


if __name__ == "__main__":
    unittest.main()
