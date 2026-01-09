"""

# Logseq: [[TTA.dev/Tests/Context/Test_instruction_loading]]
Unit tests for instruction loading in AI Conversation Context Manager.

Tests the InstructionLoader class and load_instructions() method.
"""

import sys
from pathlib import Path

import pytest

# Add .augment to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".augment"))

from context.conversation_manager import (
    AIConversationContextManager,
    InstructionLoader,
    create_tta_session,
)


class TestInstructionLoader:
    """Tests for InstructionLoader class."""

    def test_discover_instructions(self):
        """Test instruction file discovery."""
        loader = InstructionLoader()
        instructions = loader.discover_instructions()

        # Should find at least global.instructions.md
        assert len(instructions) > 0
        assert any("global.instructions.md" in str(f) for f in instructions)

    def test_parse_instruction_file_valid(self):
        """Test parsing valid instruction file."""
        loader = InstructionLoader()
        global_file = Path(".augment/instructions/global.instructions.md")

        if not global_file.exists():
            pytest.skip("global.instructions.md not found")

        parsed = loader.parse_instruction_file(global_file)

        assert parsed is not None
        assert "frontmatter" in parsed
        assert "content" in parsed
        assert "filename" in parsed
        assert "applyTo" in parsed["frontmatter"]
        assert "description" in parsed["frontmatter"]

    def test_parse_instruction_file_caching(self):
        """Test that instruction files are cached."""
        loader = InstructionLoader()
        global_file = Path(".augment/instructions/global.instructions.md")

        if not global_file.exists():
            pytest.skip("global.instructions.md not found")

        # Parse twice
        parsed1 = loader.parse_instruction_file(global_file)
        parsed2 = loader.parse_instruction_file(global_file)

        # Should return same cached object
        assert parsed1 is parsed2

    def test_match_file_path_global(self):
        """Test glob pattern matching for global patterns."""
        loader = InstructionLoader()

        # Global pattern should match any .py file
        assert loader.match_file_path("src/test.py", "**/*.py")
        assert loader.match_file_path("tests/unit/test_foo.py", "**/*.py")

        # None should match global patterns
        assert loader.match_file_path(None, "**/*.py")

    def test_match_file_path_scoped(self):
        """Test glob pattern matching for scoped patterns."""
        loader = InstructionLoader()

        # Scoped pattern should match only specific paths
        assert loader.match_file_path(
            "src/player_experience/service.py", "src/player_experience/**/*.py"
        )
        assert not loader.match_file_path(
            "src/agent_orchestration/service.py", "src/player_experience/**/*.py"
        )

        # None should not match scoped patterns
        assert not loader.match_file_path(None, "src/player_experience/**/*.py")

    def test_match_file_path_multiple_patterns(self):
        """Test glob pattern matching with multiple patterns."""
        loader = InstructionLoader()

        patterns = ["src/player_experience/**/*.py", "tests/player_experience/**/*.py"]

        assert loader.match_file_path("src/player_experience/service.py", patterns)
        assert loader.match_file_path(
            "tests/player_experience/test_service.py", patterns
        )
        assert not loader.match_file_path(
            "src/agent_orchestration/service.py", patterns
        )

    def test_get_relevant_instructions_global(self):
        """Test getting global instructions (no file specified)."""
        loader = InstructionLoader()
        instructions = loader.get_relevant_instructions()

        # Should get at least global.instructions.md
        assert len(instructions) > 0
        assert any("global.instructions.md" in i["filename"] for i in instructions)

    def test_get_relevant_instructions_scoped(self):
        """Test getting scoped instructions for specific file."""
        loader = InstructionLoader()

        # Get instructions for player experience file
        instructions = loader.get_relevant_instructions(
            "src/player_experience/service.py"
        )

        # Should get global + player-experience instructions
        filenames = [i["filename"] for i in instructions]
        assert "global.instructions.md" in filenames
        assert "player-experience.instructions.md" in filenames

        # Should NOT get agent-orchestration instructions
        assert "agent-orchestration.instructions.md" not in filenames


class TestLoadInstructions:
    """Tests for load_instructions() method."""

    def test_load_global_instructions(self):
        """Test loading global instructions."""
        manager = AIConversationContextManager()
        session_id = "test-session-global"
        manager.create_session(session_id)

        # Load instructions
        context = manager.load_instructions(session_id)

        # Should have system messages with instructions
        system_messages = [m for m in context.messages if m.role == "system"]
        assert len(system_messages) > 0

        # Should have global.instructions.md
        instruction_messages = [
            m for m in system_messages if m.metadata.get("type") == "instruction"
        ]
        assert len(instruction_messages) > 0
        assert any(
            "global.instructions.md" in m.metadata.get("source", "")
            for m in instruction_messages
        )

    def test_load_scoped_instructions(self):
        """Test loading scoped instructions for specific file."""
        manager = AIConversationContextManager()
        session_id = "test-session-scoped"
        manager.create_session(session_id)

        # Load instructions for player experience file
        context = manager.load_instructions(
            session_id, "src/player_experience/service.py"
        )

        # Should have instruction messages
        instruction_messages = [
            m
            for m in context.messages
            if m.role == "system" and m.metadata.get("type") == "instruction"
        ]
        assert len(instruction_messages) > 0

        # Should have both global and player-experience instructions
        sources = [m.metadata.get("source", "") for m in instruction_messages]
        assert "global.instructions.md" in sources
        assert "player-experience.instructions.md" in sources

    def test_instruction_importance_scoring(self):
        """Test that instructions have correct importance scores."""
        manager = AIConversationContextManager()
        session_id = "test-session-importance"
        manager.create_session(session_id)

        # Load instructions
        context = manager.load_instructions(
            session_id, "src/player_experience/service.py"
        )

        # Get instruction messages
        instruction_messages = [
            m
            for m in context.messages
            if m.role == "system" and m.metadata.get("type") == "instruction"
        ]

        # Global instructions should have importance 0.9
        global_msgs = [
            m for m in instruction_messages if m.metadata.get("scope") == "global"
        ]
        assert all(m.importance == 0.9 for m in global_msgs)

        # Scoped instructions should have importance 0.8
        scoped_msgs = [
            m for m in instruction_messages if m.metadata.get("scope") == "scoped"
        ]
        assert all(m.importance == 0.8 for m in scoped_msgs)

    def test_instruction_metadata(self):
        """Test that instruction messages have correct metadata."""
        manager = AIConversationContextManager()
        session_id = "test-session-metadata"
        manager.create_session(session_id)

        # Load instructions
        context = manager.load_instructions(session_id)

        # Get instruction messages
        instruction_messages = [
            m
            for m in context.messages
            if m.role == "system" and m.metadata.get("type") == "instruction"
        ]

        # All instruction messages should have required metadata
        for msg in instruction_messages:
            assert msg.metadata.get("type") == "instruction"
            assert "source" in msg.metadata
            assert "scope" in msg.metadata
            assert "description" in msg.metadata


class TestCreateTTASession:
    """Tests for create_tta_session() with instruction loading."""

    def test_create_session_loads_global_instructions(self):
        """Test that create_tta_session() loads global instructions."""
        manager, session_id = create_tta_session()

        context = manager.contexts[session_id]

        # Should have architecture context
        arch_msgs = [
            m
            for m in context.messages
            if m.metadata.get("type") == "architecture_context"
        ]
        assert len(arch_msgs) == 1

        # Should have instruction messages
        instruction_msgs = [
            m for m in context.messages if m.metadata.get("type") == "instruction"
        ]
        assert len(instruction_msgs) > 0

    def test_create_session_with_current_file(self):
        """Test that create_tta_session() loads scoped instructions."""
        manager, session_id = create_tta_session(
            current_file="src/player_experience/service.py"
        )

        context = manager.contexts[session_id]

        # Should have instruction messages
        instruction_msgs = [
            m for m in context.messages if m.metadata.get("type") == "instruction"
        ]

        # Should have both global and player-experience instructions
        sources = [m.metadata.get("source", "") for m in instruction_msgs]
        assert "global.instructions.md" in sources
        assert "player-experience.instructions.md" in sources

    def test_create_session_backward_compatible(self):
        """Test that create_tta_session() is backward compatible."""
        # Should work without current_file parameter
        manager, session_id = create_tta_session()

        assert manager is not None
        assert session_id is not None
        assert session_id in manager.contexts
