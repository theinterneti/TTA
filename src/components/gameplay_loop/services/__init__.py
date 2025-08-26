"""
Gameplay Loop Services

This module provides service layer components for the gameplay loop system,
including Redis session management, caching strategies, and state persistence.
"""

from .redis_manager import (
    RedisSessionManager,
    SessionCacheManager,
    NarrativeContextCache,
    ProgressCacheManager,
    SessionLifecycleManager
)

from .cache_strategies import (
    CacheStrategy,
    TTLCacheStrategy,
    LRUCacheStrategy,
    WriteBackCacheStrategy,
    WriteThroughCacheStrategy
)

from .session_state import (
    SessionState,
    SessionStateManager,
    StateTransition,
    StateValidator
)

__all__ = [
    # Redis managers
    "RedisSessionManager",
    "SessionCacheManager",
    "NarrativeContextCache", 
    "ProgressCacheManager",
    "SessionLifecycleManager",
    
    # Cache strategies
    "CacheStrategy",
    "TTLCacheStrategy",
    "LRUCacheStrategy",
    "WriteBackCacheStrategy",
    "WriteThroughCacheStrategy",
    
    # Session state management
    "SessionState",
    "SessionStateManager",
    "StateTransition",
    "StateValidator"
]
