"""

# Logseq: [[TTA.dev/Tests/Test_causal_graph_coverage]]
Coverage tests for causal_graph module to reach 70%+ coverage.

This module contains tests specifically designed to cover previously
untested code paths in causal_graph.py.
"""

from tta_narrative.orchestration.causal_graph import (
    add_edge,
    detect_simple_cycles,
    remove_weak_link,
)


class TestCausalGraphCycleDetection:
    """Tests for detect_simple_cycles function (lines 13-21)."""

    def test_detect_cycle_simple_bidirectional(self):
        """Test detection of simple bidirectional cycle."""
        graph = {"A": {"B"}, "B": {"A"}}

        cycles = detect_simple_cycles(graph)

        assert len(cycles) == 2  # Both directions detected
        assert "Cycle between A and B" in cycles
        assert "Cycle between B and A" in cycles

    def test_detect_cycle_multiple_nodes(self):
        """Test detection of cycles with multiple nodes."""
        graph = {
            "A": {"B", "C"},
            "B": {"A"},  # Cycle with A
            "C": {"D"},
            "D": set(),
        }

        cycles = detect_simple_cycles(graph)

        assert len(cycles) == 2
        assert "Cycle between A and B" in cycles
        assert "Cycle between B and A" in cycles

    def test_no_cycle_linear_graph(self):
        """Test that no cycles detected in linear graph."""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"D"}, "D": set()}

        cycles = detect_simple_cycles(graph)

        assert cycles == []

    def test_no_cycle_empty_graph(self):
        """Test that no cycles detected in empty graph."""
        graph = {}

        cycles = detect_simple_cycles(graph)

        assert cycles == []

    def test_no_cycle_single_node(self):
        """Test that no cycles detected with single node."""
        graph = {"A": set()}

        cycles = detect_simple_cycles(graph)

        assert cycles == []

    def test_detect_cycle_complex_graph(self):
        """Test cycle detection in complex graph."""
        graph = {
            "A": {"B", "C"},
            "B": {"D"},
            "C": {"A"},  # Cycle with A
            "D": {"E"},
            "E": {"D"},  # Cycle with D
        }

        cycles = detect_simple_cycles(graph)

        # Should detect A-C and D-E cycles
        assert len(cycles) == 4  # Both directions for each cycle
        assert "Cycle between A and C" in cycles
        assert "Cycle between C and A" in cycles
        assert "Cycle between D and E" in cycles
        assert "Cycle between E and D" in cycles


class TestCausalGraphWeakLinkRemoval:
    """Tests for remove_weak_link function (lines 24-29)."""

    def test_remove_weak_link_single_destination(self):
        """Test removing weak link when each node has single destination."""
        graph = {"A": {"B"}, "C": {"D"}, "E": {"F"}}

        remove_weak_link(graph)

        # Each node should have one destination removed
        assert len(graph["A"]) == 0
        assert len(graph["C"]) == 0
        assert len(graph["E"]) == 0

    def test_remove_weak_link_multiple_destinations(self):
        """Test removing weak link when nodes have multiple destinations."""
        graph = {"A": {"B", "C", "D"}, "E": {"F", "G"}}

        remove_weak_link(graph)

        # Each node should have one destination removed
        assert len(graph["A"]) == 2  # Was 3, now 2
        assert len(graph["E"]) == 1  # Was 2, now 1

    def test_remove_weak_link_empty_destinations(self):
        """Test that empty destination sets are skipped."""
        graph = {"A": set(), "B": {"C"}, "D": set()}

        remove_weak_link(graph)

        # Empty sets should remain empty
        assert len(graph["A"]) == 0
        assert len(graph["B"]) == 0  # C removed
        assert len(graph["D"]) == 0

    def test_remove_weak_link_empty_graph(self):
        """Test remove_weak_link on empty graph."""
        graph = {}

        remove_weak_link(graph)

        assert graph == {}

    def test_remove_weak_link_preserves_graph_structure(self):
        """Test that remove_weak_link preserves graph structure."""
        graph = {"A": {"B", "C"}, "D": {"E"}}

        # Store original keys
        original_keys = set(graph.keys())

        remove_weak_link(graph)

        # Keys should remain the same
        assert set(graph.keys()) == original_keys


class TestCausalGraphAddEdge:
    """Tests for add_edge function (lines 9-10)."""

    def test_add_edge_new_source(self):
        """Test adding edge with new source node."""
        graph = {}

        add_edge(graph, "A", "B")

        assert "A" in graph
        assert "B" in graph["A"]

    def test_add_edge_existing_source(self):
        """Test adding edge to existing source node."""
        graph = {"A": {"B"}}

        add_edge(graph, "A", "C")

        assert "A" in graph
        assert "B" in graph["A"]
        assert "C" in graph["A"]
        assert len(graph["A"]) == 2

    def test_add_edge_multiple_edges(self):
        """Test adding multiple edges."""
        graph = {}

        add_edge(graph, "A", "B")
        add_edge(graph, "A", "C")
        add_edge(graph, "B", "D")

        assert len(graph["A"]) == 2
        assert len(graph["B"]) == 1
        assert "B" in graph["A"]
        assert "C" in graph["A"]
        assert "D" in graph["B"]

    def test_add_edge_duplicate(self):
        """Test that adding duplicate edge doesn't create duplicates."""
        graph = {"A": {"B"}}

        add_edge(graph, "A", "B")

        # Set should prevent duplicates
        assert len(graph["A"]) == 1
        assert "B" in graph["A"]
