"""
Session Integration Manager

This module provides session integration services for the therapeutic gameplay loop,
including cross-session continuity, progress tracking, and therapeutic context management.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Context information for a therapeutic session."""
    
    session_id: str
    user_id: str
    previous_session_id: str | None = None
    therapeutic_goals: list[str] = field(default_factory=list)
    current_narrative_context: str = ""
    emotional_state: dict[str, float] = field(default_factory=dict)
    progress_markers: dict[str, Any] = field(default_factory=dict)
    session_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntegrationState:
    """State for session integration."""
    
    user_id: str
    current_session_id: str | None = None
    session_history: list[str] = field(default_factory=list)
    cross_session_progress: dict[str, Any] = field(default_factory=dict)
    therapeutic_continuity: dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class SessionIntegrationManager:
    """Manages integration between therapeutic sessions."""
    
    def __init__(self):
        self.session_contexts: dict[str, SessionContext] = {}
        self.integration_states: dict[str, IntegrationState] = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_session_context(self, session_id: str, user_id: str, **kwargs) -> SessionContext:
        """Create a new session context."""
        # Get previous session for continuity
        integration_state = await self.get_integration_state(user_id)
        previous_session_id = integration_state.current_session_id
        
        context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            previous_session_id=previous_session_id,
            **kwargs
        )
        
        self.session_contexts[session_id] = context
        
        # Update integration state
        integration_state.current_session_id = session_id
        integration_state.session_history.append(session_id)
        integration_state.last_updated = datetime.utcnow()
        
        return context
    
    async def get_session_context(self, session_id: str) -> SessionContext | None:
        """Get session context by ID."""
        return self.session_contexts.get(session_id)
    
    async def update_session_context(self, session_id: str, updates: dict[str, Any]) -> SessionContext | None:
        """Update session context."""
        context = self.session_contexts.get(session_id)
        if not context:
            return None
        
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        context.updated_at = datetime.utcnow()
        return context
    
    async def get_integration_state(self, user_id: str) -> IntegrationState:
        """Get or create integration state for user."""
        if user_id not in self.integration_states:
            self.integration_states[user_id] = IntegrationState(user_id=user_id)
        return self.integration_states[user_id]
    
    async def get_session_continuity(self, user_id: str) -> dict[str, Any]:
        """Get continuity information for next session."""
        integration_state = await self.get_integration_state(user_id)
        
        if not integration_state.current_session_id:
            return {"is_first_session": True}
        
        current_context = await self.get_session_context(integration_state.current_session_id)
        if not current_context:
            return {"is_first_session": True}
        
        return {
            "is_first_session": False,
            "previous_session_id": integration_state.current_session_id,
            "therapeutic_goals": current_context.therapeutic_goals,
            "emotional_state": current_context.emotional_state,
            "progress_markers": current_context.progress_markers,
            "narrative_context": current_context.current_narrative_context,
            "session_count": len(integration_state.session_history),
        }
    
    async def finalize_session(self, session_id: str) -> dict[str, Any]:
        """Finalize session and prepare for next session."""
        context = await self.get_session_context(session_id)
        if not context:
            return {"error": "Session context not found"}
        
        integration_state = await self.get_integration_state(context.user_id)
        
        # Update cross-session progress
        integration_state.cross_session_progress.update(context.progress_markers)
        integration_state.therapeutic_continuity = {
            "last_emotional_state": context.emotional_state,
            "last_narrative_context": context.current_narrative_context,
            "therapeutic_goals": context.therapeutic_goals,
            "session_metadata": context.session_metadata,
        }
        integration_state.last_updated = datetime.utcnow()
        
        return {
            "session_finalized": True,
            "continuity_prepared": True,
            "next_session_ready": True,
        }
    
    async def get_progress_summary(self, user_id: str) -> dict[str, Any]:
        """Get progress summary across sessions."""
        integration_state = await self.get_integration_state(user_id)
        
        return {
            "user_id": user_id,
            "total_sessions": len(integration_state.session_history),
            "cross_session_progress": integration_state.cross_session_progress,
            "therapeutic_continuity": integration_state.therapeutic_continuity,
            "last_updated": integration_state.last_updated.isoformat(),
        }
    
    async def health_check(self) -> dict[str, Any]:
        """Health check for session integration service."""
        return {
            "status": "healthy",
            "active_sessions": len(self.session_contexts),
            "active_users": len(self.integration_states),
            "service": "SessionIntegrationManager"
        }
