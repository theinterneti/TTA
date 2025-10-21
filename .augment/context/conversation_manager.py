"""
AI Conversation Context Manager for TTA Development.

This module provides context management for AI-assisted development sessions,
implementing the agentic primitive of context window management at the meta-level
(development process) before integrating into the product.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
import json
import logging

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using approximate token counting")

logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """A message in the AI conversation."""
    
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens: int = 0
    importance: float = 1.0  # 0.0 to 1.0, higher = more important
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tokens": self.tokens,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationMessage":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            tokens=data.get("tokens", 0),
            importance=data.get("importance", 1.0)
        )


@dataclass
class ConversationContext:
    """Managed conversation context for AI sessions."""
    
    session_id: str
    messages: list[ConversationMessage]
    max_tokens: int = 8000
    current_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def utilization(self) -> float:
        """Return context window utilization (0.0 to 1.0)."""
        return self.current_tokens / self.max_tokens if self.max_tokens > 0 else 0.0
    
    @property
    def remaining_tokens(self) -> int:
        """Return remaining token capacity."""
        return max(0, self.max_tokens - self.current_tokens)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
            "max_tokens": self.max_tokens,
            "current_tokens": self.current_tokens,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationContext":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            messages=[ConversationMessage.from_dict(m) for m in data["messages"]],
            max_tokens=data.get("max_tokens", 8000),
            current_tokens=data.get("current_tokens", 0),
            metadata=data.get("metadata", {})
        )


class AIConversationContextManager:
    """
    Manages conversation context for AI-assisted development.
    
    Features:
    - Token counting and tracking
    - Intelligent message pruning
    - Context summarization
    - Important message preservation
    - Session persistence
    
    This is a meta-level implementation of the context window management
    primitive, applied to our development process before integrating into TTA.
    """
    
    def __init__(self, max_tokens: int = 8000, sessions_dir: str = ".augment/context/sessions"):
        """
        Initialize the conversation context manager.
        
        Args:
            max_tokens: Maximum tokens per context window
            sessions_dir: Directory to store session files
        """
        self.max_tokens = max_tokens
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize token counter
        if TIKTOKEN_AVAILABLE:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None
        
        self.contexts: dict[str, ConversationContext] = {}
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Approximate: ~4 characters per token
            return len(text) // 4
    
    def create_session(self, session_id: str) -> ConversationContext:
        """Create a new conversation session."""
        context = ConversationContext(
            session_id=session_id,
            messages=[],
            max_tokens=self.max_tokens,
            current_tokens=0
        )
        self.contexts[session_id] = context
        logger.info(f"Created new session: {session_id}")
        return context
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        importance: float = 1.0,
        metadata: dict | None = None,
        auto_prune: bool = True
    ) -> ConversationContext:
        """
        Add a message to the conversation, pruning if necessary.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            importance: Importance score (0.0 to 1.0)
            metadata: Optional metadata
            auto_prune: Whether to auto-prune when threshold exceeded
        
        Returns:
            Updated conversation context
        """
        context = self.contexts.get(session_id)
        if not context:
            context = self.create_session(session_id)
        
        # Count tokens
        tokens = self.count_tokens(content)
        
        # Create message
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            tokens=tokens,
            importance=importance
        )
        
        # Check if pruning needed (at 80% capacity)
        if auto_prune and (context.current_tokens + tokens) / context.max_tokens > 0.8:
            logger.info(f"Context window at {context.utilization:.1%}, pruning...")
            context = self._prune_context(context, tokens)
        
        # Add message
        context.messages.append(message)
        context.current_tokens += tokens
        
        logger.debug(
            f"Added {role} message ({tokens} tokens) to {session_id}. "
            f"Utilization: {context.utilization:.1%}"
        )
        
        return context
    
    def _prune_context(
        self,
        context: ConversationContext,
        needed_tokens: int
    ) -> ConversationContext:
        """
        Prune context to make room for new message.
        
        Strategy: Keep high-importance messages and recent messages.
        """
        # Always keep system messages
        system_msgs = [m for m in context.messages if m.role == "system"]
        
        # Keep high-importance messages (importance > 0.8)
        important_msgs = [
            m for m in context.messages 
            if m.importance > 0.8 and m.role != "system"
        ]
        
        # Keep most recent messages
        recent_msgs = [
            m for m in context.messages[-5:] 
            if m not in system_msgs and m not in important_msgs
        ]
        
        # Combine and deduplicate
        preserved = []
        seen_ids = set()
        for msg in system_msgs + important_msgs + recent_msgs:
            msg_id = id(msg)
            if msg_id not in seen_ids:
                preserved.append(msg)
                seen_ids.add(msg_id)
        
        # Sort by timestamp to maintain order
        preserved.sort(key=lambda m: m.timestamp)
        
        # Update context
        old_count = len(context.messages)
        old_tokens = context.current_tokens
        
        context.messages = preserved
        context.current_tokens = sum(m.tokens for m in preserved)
        
        logger.info(
            f"Pruned context: {old_count} → {len(preserved)} messages, "
            f"{old_tokens} → {context.current_tokens} tokens"
        )
        
        return context
    
    def get_context_summary(self, session_id: str) -> str:
        """Get a summary of the conversation context."""
        context = self.contexts.get(session_id)
        if not context:
            return f"No context available for session: {session_id}"
        
        summary = f"Session: {session_id}\n"
        summary += f"Messages: {len(context.messages)}\n"
        summary += f"Tokens: {context.current_tokens:,}/{context.max_tokens:,}\n"
        summary += f"Utilization: {context.utilization:.1%}\n"
        summary += f"Remaining: {context.remaining_tokens:,} tokens\n"
        
        # Message breakdown
        role_counts = {}
        for msg in context.messages:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1
        
        summary += "\nMessage Breakdown:\n"
        for role, count in role_counts.items():
            summary += f"  {role}: {count}\n"
        
        return summary
    
    def save_session(self, session_id: str, filepath: str | None = None) -> Path:
        """
        Save conversation session to file.
        
        Args:
            session_id: Session identifier
            filepath: Optional custom filepath (defaults to sessions_dir/<session_id>.json)
        
        Returns:
            Path to saved file
        """
        context = self.contexts.get(session_id)
        if not context:
            raise ValueError(f"No context found for session: {session_id}")
        
        if filepath is None:
            filepath = self.sessions_dir / f"{session_id}.json"
        else:
            filepath = Path(filepath)
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(context.to_dict(), f, indent=2)
        
        logger.info(f"Saved session {session_id} to {filepath}")
        return filepath
    
    def load_session(self, filepath: str | Path) -> ConversationContext:
        """
        Load conversation session from file.
        
        Args:
            filepath: Path to session file
        
        Returns:
            Loaded conversation context
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Session file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        context = ConversationContext.from_dict(data)
        self.contexts[context.session_id] = context
        
        logger.info(f"Loaded session {context.session_id} from {filepath}")
        return context
    
    def list_sessions(self) -> list[str]:
        """List all saved session files."""
        return [f.stem for f in self.sessions_dir.glob("*.json")]
    
    def get_architecture_context(self) -> str:
        """
        Get standard TTA architecture context for new sessions.
        
        This provides consistent architectural context across AI sessions.
        """
        return """
TTA (Therapeutic Text Adventure) Architecture Context:

**Core Components:**
- Multi-agent system: IPA (Input Processor), WBA (World Builder), NGA (Narrative Generator)
- State Management: Redis (session state), Neo4j (knowledge graphs)
- Workflow Orchestration: LangGraph integration for complex workflows
- Component System: Base Component class with lifecycle management

**Key Directories:**
- src/agent_orchestration/ - Multi-agent coordination and workflows
- src/player_experience/ - User-facing APIs and session management
- src/components/ - Reusable components (Neo4j, Redis, LLM, etc.)
- src/ai_components/ - AI-specific components (prompts, RAG, etc.)

**Development Principles:**
- Therapeutic Safety: All content validated for therapeutic appropriateness
- Appropriate Complexity: YAGNI/KISS, avoid gold-plating
- Component Maturity: Development → Staging → Production workflow
- Solo Developer Focus: Optimized for WSL2, single-GPU constraints

**Testing Strategy:**
- Unit tests: Development stage validation
- Integration tests: Staging stage validation
- E2E tests: Production readiness validation
- Component-specific test organization

**Current Focus:**
- Implementing agentic primitives (context management, error recovery, observability)
- Phase 1: Meta-level (development process)
- Phase 2: Product-level (TTA application)
"""


# Convenience function for quick session creation
def create_tta_session(session_id: str | None = None) -> tuple[AIConversationContextManager, str]:
    """
    Create a new TTA development session with standard architecture context.
    
    Args:
        session_id: Optional session ID (auto-generated if not provided)
    
    Returns:
        Tuple of (context manager, session ID)
    """
    if session_id is None:
        session_id = f"tta-dev-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    manager = AIConversationContextManager()
    context = manager.create_session(session_id)
    
    # Add architecture context
    manager.add_message(
        session_id=session_id,
        role="system",
        content=manager.get_architecture_context(),
        importance=1.0,
        metadata={"type": "architecture_context"}
    )
    
    logger.info(f"Created TTA development session: {session_id}")
    return manager, session_id

