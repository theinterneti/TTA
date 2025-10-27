"""
Tests for AI Conversation Context Manager

Tests cover:
- Session creation and management
- Message addition with importance scoring
- Token counting and pruning logic
- Session save/load functionality
- Context summarization
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import from .augment/context/
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".augment" / "context"))

from conversation_manager import (
    AIConversationContextManager,
    ConversationMessage,
    ConversationContext,
)


class TestSessionManagement:
    """Test session creation and management."""
    
    def test_create_session(self):
        """Test creating a new session."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        
        context = manager.create_session(session_id)
        
        assert context.session_id == session_id
        assert context.max_tokens == 1000
        assert len(context.messages) == 0
        assert context.current_tokens == 0
    
    def test_create_session_custom_tokens(self):
        """Test creating session with custom token limit."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        
        context = manager.create_session(session_id, max_tokens=2000)
        
        assert context.max_tokens == 2000
    
    def test_get_nonexistent_session(self):
        """Test getting a session that doesn't exist."""
        manager = AIConversationContextManager()
        
        context = manager.contexts.get("nonexistent")
        
        assert context is None


class TestMessageAddition:
    """Test adding messages to context."""
    
    def test_add_message_basic(self):
        """Test adding a basic message."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(
            session_id=session_id,
            role="user",
            content="Hello, world!",
            importance=0.9
        )
        
        context = manager.contexts[session_id]
        assert len(context.messages) == 1
        assert context.messages[0].role == "user"
        assert context.messages[0].content == "Hello, world!"
        assert context.messages[0].importance == 0.9
    
    def test_add_message_with_metadata(self):
        """Test adding message with metadata."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(
            session_id=session_id,
            role="user",
            content="Test",
            importance=1.0,
            metadata={"type": "test", "key": "value"}
        )
        
        context = manager.contexts[session_id]
        assert context.messages[0].metadata == {"type": "test", "key": "value"}
    
    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        for i in range(5):
            manager.add_message(
                session_id=session_id,
                role="user",
                content=f"Message {i}",
                importance=0.5
            )
        
        context = manager.contexts[session_id]
        assert len(context.messages) == 5


class TestTokenCounting:
    """Test token counting functionality."""
    
    def test_token_counting(self):
        """Test that tokens are counted for messages."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(
            session_id=session_id,
            role="user",
            content="Hello, world!",
            importance=0.9
        )
        
        context = manager.contexts[session_id]
        assert context.current_tokens > 0
        assert context.messages[0].tokens > 0
    
    def test_token_accumulation(self):
        """Test that tokens accumulate across messages."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(session_id, "user", "First message", 0.5)
        tokens_after_first = manager.contexts[session_id].current_tokens
        
        manager.add_message(session_id, "user", "Second message", 0.5)
        tokens_after_second = manager.contexts[session_id].current_tokens
        
        assert tokens_after_second > tokens_after_first


class TestPruning:
    """Test context pruning logic."""
    
    def test_pruning_preserves_system_messages(self):
        """Test that system messages are always preserved."""
        manager = AIConversationContextManager(max_tokens=100)
        session_id = "test-session"
        manager.create_session(session_id)
        
        # Add system message
        manager.add_message(session_id, "system", "System context", importance=1.0)
        
        # Add many low-importance messages to trigger pruning
        for i in range(20):
            manager.add_message(session_id, "user", f"Message {i}" * 10, importance=0.3)
        
        context = manager.contexts[session_id]
        system_messages = [m for m in context.messages if m.role == "system"]
        assert len(system_messages) > 0
    
    def test_pruning_preserves_high_importance(self):
        """Test that high-importance messages are preserved."""
        manager = AIConversationContextManager(max_tokens=100)
        session_id = "test-session"
        manager.create_session(session_id)
        
        # Add high-importance message
        manager.add_message(session_id, "user", "Important decision", importance=1.0)
        
        # Add many low-importance messages to trigger pruning
        for i in range(20):
            manager.add_message(session_id, "user", f"Message {i}" * 10, importance=0.3)
        
        context = manager.contexts[session_id]
        important_messages = [m for m in context.messages if m.importance == 1.0]
        assert len(important_messages) > 0
    
    def test_pruning_preserves_recent_messages(self):
        """Test that recent messages are preserved."""
        manager = AIConversationContextManager(max_tokens=100)
        session_id = "test-session"
        manager.create_session(session_id)
        
        # Add many messages to trigger pruning
        for i in range(20):
            manager.add_message(session_id, "user", f"Message {i}" * 10, importance=0.3)
        
        context = manager.contexts[session_id]
        # Should have at least the last 5 messages
        assert len(context.messages) >= 5
    
    def test_pruning_respects_token_limit(self):
        """Test that pruning keeps context under token limit."""
        manager = AIConversationContextManager(max_tokens=100)
        session_id = "test-session"
        manager.create_session(session_id)
        
        # Add many messages
        for i in range(20):
            manager.add_message(session_id, "user", f"Message {i}" * 10, importance=0.3)
        
        context = manager.contexts[session_id]
        assert context.current_tokens <= context.max_tokens


class TestSessionPersistence:
    """Test session save/load functionality."""
    
    def test_save_session(self):
        """Test saving a session to file."""
        manager = AIConversationContextManager()
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(session_id, "user", "Test message", importance=0.9)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            manager.save_session(session_id, filepath)
            
            # Verify file exists and contains data
            assert Path(filepath).exists()
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert data["session_id"] == session_id
            assert len(data["messages"]) == 1
            assert data["messages"][0]["content"] == "Test message"
        finally:
            Path(filepath).unlink()
    
    def test_load_session(self):
        """Test loading a session from file."""
        manager = AIConversationContextManager()
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(session_id, "user", "Test message", importance=0.9)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            # Save session
            manager.save_session(session_id, filepath)
            
            # Load in new manager
            new_manager = AIConversationContextManager()
            loaded_context = new_manager.load_session(filepath)
            
            assert loaded_context.session_id == session_id
            assert len(loaded_context.messages) == 1
            assert loaded_context.messages[0].content == "Test message"
            assert loaded_context.messages[0].importance == 0.9
        finally:
            Path(filepath).unlink()
    
    def test_save_load_preserves_metadata(self):
        """Test that save/load preserves message metadata."""
        manager = AIConversationContextManager()
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(
            session_id,
            "user",
            "Test",
            importance=0.9,
            metadata={"type": "test", "key": "value"}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            manager.save_session(session_id, filepath)
            
            new_manager = AIConversationContextManager()
            loaded_context = new_manager.load_session(filepath)
            
            assert loaded_context.messages[0].metadata == {"type": "test", "key": "value"}
        finally:
            Path(filepath).unlink()


class TestContextSummary:
    """Test context summarization."""
    
    def test_get_context_summary(self):
        """Test getting context summary."""
        manager = AIConversationContextManager(max_tokens=1000)
        session_id = "test-session"
        manager.create_session(session_id)
        
        manager.add_message(session_id, "user", "Test message", importance=0.9)
        
        summary = manager.get_context_summary(session_id)
        
        assert "test-session" in summary
        assert "Messages: 1" in summary
        assert "Tokens:" in summary
        assert "Utilization:" in summary
    
    def test_summary_nonexistent_session(self):
        """Test summary for nonexistent session."""
        manager = AIConversationContextManager()
        
        summary = manager.get_context_summary("nonexistent")
        
        assert "not found" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

