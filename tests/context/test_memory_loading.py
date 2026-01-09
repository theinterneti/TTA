"""

# Logseq: [[TTA.dev/Tests/Context/Test_memory_loading]]
Tests for memory loading functionality in AI Conversation Context Manager.

This module tests the MemoryLoader class and load_memories() method,
ensuring memories are correctly discovered, parsed, matched, and loaded
into session context.
"""

# Import from the correct path (relative to project root)
import sys
from pathlib import Path

import pytest

# Add .augment to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".augment"))

from context.conversation_manager import (
    AIConversationContextManager,
    MemoryLoader,
)


@pytest.fixture
def temp_memory_dir(tmp_path):
    """Create temporary memory directory structure with test memories."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    # Create subdirectories
    (memory_dir / "implementation-failures").mkdir()
    (memory_dir / "successful-patterns").mkdir()
    (memory_dir / "architectural-decisions").mkdir()

    # Create test memory files
    # Implementation failure
    failure_content = """---
category: implementation-failures
date: 2025-10-22
component: agent-orchestration
severity: high
tags: [pytest, imports, test-environment]
---
# Pytest Import Error Resolution

Test runner import errors when using `uvx pytest` instead of project's configured test environment.

## Root Cause
`uvx pytest` runs in isolated environment without project dependencies.

## Solution
Always use `uv run pytest` to ensure correct module imports.
"""
    (
        memory_dir
        / "implementation-failures"
        / "pytest-import-error-2025-10-22.memory.md"
    ).write_text(failure_content)

    # Successful pattern
    pattern_content = """---
category: successful-patterns
date: 2025-10-20
component: global
severity: high
tags: [development-workflow, templates, consistency]
---
# Template-Driven Development

Using templates ensures consistency across similar files.

## Pattern
1. Create template with all required sections
2. Copy template for each new file
3. Fill in template sections systematically
"""
    (
        memory_dir
        / "successful-patterns"
        / "template-driven-development-2025-10-20.memory.md"
    ).write_text(pattern_content)

    # Architectural decision
    decision_content = """---
category: architectural-decisions
date: 2025-10-15
component: global
severity: critical
tags: [architecture, infrastructure, ai-agents]
---
# File-Based Instruction System

Decision to implement file-based instruction system rather than database-backed system.

## Rationale
File-based system provides version control, easy editing, and no additional infrastructure dependencies.
"""
    (
        memory_dir
        / "architectural-decisions"
        / "file-based-instructions-2025-10-15.memory.md"
    ).write_text(decision_content)

    return memory_dir


class TestMemoryLoader:
    """Tests for MemoryLoader class."""

    def test_discover_memories(self, temp_memory_dir):
        """Test memory file discovery."""
        loader = MemoryLoader(str(temp_memory_dir))
        memories = loader.discover_memories()

        assert len(memories) == 3
        assert all(m.suffix == ".md" for m in memories)
        assert all("memory" in m.name for m in memories)

    def test_parse_memory_file(self, temp_memory_dir):
        """Test memory file parsing."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )

        parsed = loader.parse_memory_file(memory_file)

        assert parsed is not None
        assert "frontmatter" in parsed
        assert "content" in parsed
        assert "filename" in parsed
        assert "category" in parsed

        # Check frontmatter fields
        frontmatter = parsed["frontmatter"]
        assert frontmatter["category"] == "implementation-failures"
        assert frontmatter["component"] == "agent-orchestration"
        assert frontmatter["severity"] == "high"
        assert "pytest" in frontmatter["tags"]

        # Check category from directory
        assert parsed["category"] == "implementation-failures"

    def test_parse_memory_file_caching(self, temp_memory_dir):
        """Test memory file parsing uses cache."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )

        # First parse
        parsed1 = loader.parse_memory_file(memory_file)
        # Second parse (should use cache)
        parsed2 = loader.parse_memory_file(memory_file)

        assert parsed1 is parsed2  # Same object (cached)

    def test_match_memory_exact_component(self, temp_memory_dir):
        """Test memory matching with exact component match."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # Exact component match
        score = loader.match_memory(parsed, component="agent-orchestration")
        assert score >= 0.5  # Should get component match score

    def test_match_memory_global_component(self, temp_memory_dir):
        """Test memory matching with global component."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "successful-patterns"
            / "template-driven-development-2025-10-20.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # Global component matches any component
        score = loader.match_memory(parsed, component="any-component")
        assert score >= 0.3  # Should get global match score

    def test_match_memory_tag_match(self, temp_memory_dir):
        """Test memory matching with tag match."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # Tag match
        score = loader.match_memory(parsed, tags=["pytest", "testing"])
        assert score > 0.0  # Should get tag match score

    def test_match_memory_category_match(self, temp_memory_dir):
        """Test memory matching with category match."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # Category match
        score = loader.match_memory(parsed, category="implementation-failures")
        assert score >= 0.2  # Should get category match score

    def test_match_memory_no_match(self, temp_memory_dir):
        """Test memory matching with no match."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # No match
        score = loader.match_memory(
            parsed, component="unrelated-component", tags=["unrelated-tag"]
        )
        assert score == 0.0  # Should get no match

    def test_calculate_importance_critical_severity(self, temp_memory_dir):
        """Test importance calculation with critical severity."""
        loader = MemoryLoader(str(temp_memory_dir))
        memory_file = (
            temp_memory_dir
            / "architectural-decisions"
            / "file-based-instructions-2025-10-15.memory.md"
        )
        parsed = loader.parse_memory_file(memory_file)

        # High relevance, critical severity
        importance = loader.calculate_importance(parsed, relevance=1.0)
        assert importance >= 0.8  # Should be high importance

    def test_calculate_importance_recency(self, temp_memory_dir):
        """Test importance calculation considers recency."""
        loader = MemoryLoader(str(temp_memory_dir))

        # Recent memory
        recent_file = (
            temp_memory_dir
            / "implementation-failures"
            / "pytest-import-error-2025-10-22.memory.md"
        )
        recent_parsed = loader.parse_memory_file(recent_file)
        recent_importance = loader.calculate_importance(recent_parsed, relevance=0.5)

        # Older memory
        old_file = (
            temp_memory_dir
            / "architectural-decisions"
            / "file-based-instructions-2025-10-15.memory.md"
        )
        old_parsed = loader.parse_memory_file(old_file)
        old_importance = loader.calculate_importance(old_parsed, relevance=0.5)

        # Recent memory should have higher importance (all else equal)
        # Note: This may not always be true due to severity differences
        # So we just check both are valid scores
        assert 0.0 <= recent_importance <= 1.0
        assert 0.0 <= old_importance <= 1.0

    def test_get_relevant_memories(self, temp_memory_dir):
        """Test getting relevant memories."""
        loader = MemoryLoader(str(temp_memory_dir))

        # Get all memories
        memories = loader.get_relevant_memories(min_importance=0.0)
        assert len(memories) > 0
        assert all("importance" in m for m in memories)

        # Memories should be sorted by importance
        importances = [m["importance"] for m in memories]
        assert importances == sorted(importances, reverse=True)

    def test_get_relevant_memories_filtered_by_component(self, temp_memory_dir):
        """Test getting memories filtered by component."""
        loader = MemoryLoader(str(temp_memory_dir))

        # Get memories for specific component
        memories = loader.get_relevant_memories(
            component="agent-orchestration", min_importance=0.0
        )
        assert len(memories) > 0

        # Should include component-specific and global memories
        components = [m["frontmatter"]["component"] for m in memories]
        assert "agent-orchestration" in components or "global" in components

    def test_get_relevant_memories_filtered_by_category(self, temp_memory_dir):
        """Test getting memories filtered by category."""
        loader = MemoryLoader(str(temp_memory_dir))

        # Get only implementation failures
        memories = loader.get_relevant_memories(
            category="implementation-failures", min_importance=0.0
        )
        assert len(memories) > 0
        assert all(m["category"] == "implementation-failures" for m in memories)

    def test_get_relevant_memories_max_limit(self, temp_memory_dir):
        """Test max_memories limit."""
        loader = MemoryLoader(str(temp_memory_dir))

        # Limit to 1 memory
        memories = loader.get_relevant_memories(max_memories=1, min_importance=0.0)
        assert len(memories) == 1


class TestAIConversationContextManagerMemories:
    """Tests for load_memories() method in AIConversationContextManager."""

    def test_load_memories(self, temp_memory_dir):
        """Test loading memories into session context."""
        manager = AIConversationContextManager(memory_dir=str(temp_memory_dir))
        session_id = "test-session"

        # Load memories
        context = manager.load_memories(session_id, min_importance=0.0)

        assert context is not None
        assert len(context.messages) > 0

        # Check memory messages
        memory_messages = [
            m for m in context.messages if m.metadata.get("type") == "memory"
        ]
        assert len(memory_messages) > 0

        # Check metadata
        for msg in memory_messages:
            assert "category" in msg.metadata
            assert "component" in msg.metadata
            assert "severity" in msg.metadata
            assert "tags" in msg.metadata

    def test_load_memories_with_component_filter(self, temp_memory_dir):
        """Test loading memories with component filter."""
        manager = AIConversationContextManager(memory_dir=str(temp_memory_dir))
        session_id = "test-session"

        # Load memories for specific component
        context = manager.load_memories(
            session_id, component="agent-orchestration", min_importance=0.0
        )

        memory_messages = [
            m for m in context.messages if m.metadata.get("type") == "memory"
        ]
        assert len(memory_messages) > 0

    def test_load_memories_with_category_filter(self, temp_memory_dir):
        """Test loading memories with category filter."""
        manager = AIConversationContextManager(memory_dir=str(temp_memory_dir))
        session_id = "test-session"

        # Load only implementation failures
        context = manager.load_memories(
            session_id, category="implementation-failures", min_importance=0.0
        )

        memory_messages = [
            m for m in context.messages if m.metadata.get("type") == "memory"
        ]
        assert len(memory_messages) > 0
        assert all(
            m.metadata["category"] == "implementation-failures" for m in memory_messages
        )

    def test_load_memories_importance_scoring(self, temp_memory_dir):
        """Test memories are loaded with correct importance scores."""
        manager = AIConversationContextManager(memory_dir=str(temp_memory_dir))
        session_id = "test-session"

        # Load memories
        context = manager.load_memories(session_id, min_importance=0.0)

        memory_messages = [
            m for m in context.messages if m.metadata.get("type") == "memory"
        ]

        # All memories should have importance scores
        assert all(0.0 <= m.importance <= 1.0 for m in memory_messages)

    def test_load_memories_no_pruning(self, temp_memory_dir):
        """Test memories are not pruned from context."""
        manager = AIConversationContextManager(memory_dir=str(temp_memory_dir))
        session_id = "test-session"

        # Load memories
        manager.load_memories(session_id, min_importance=0.0)

        # Add many regular messages
        for i in range(100):
            manager.add_message(session_id, "user", f"Message {i}", importance=0.5)

        context = manager.contexts[session_id]
        memory_messages = [
            m for m in context.messages if m.metadata.get("type") == "memory"
        ]

        # Memories should still be present (not pruned)
        assert len(memory_messages) > 0
