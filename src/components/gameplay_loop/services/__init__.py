"""
Gameplay Loop Services

This module provides service layer components for the gameplay loop system,
including Redis session management, caching strategies, and state persistence.
"""

from .cache_strategies import (
    CacheStrategy,
    LRUCacheStrategy,
    TTLCacheStrategy,
    WriteBackCacheStrategy,
    WriteThroughCacheStrategy,
)
from .error_recovery_manager import (
    ErrorCategory,
    ErrorContext,
    ErrorRecoveryManager,
    ErrorSeverity,
    RecoveryResult,
    RecoveryStrategy,
    SystemBackup,
)
from .redis_manager import (
    NarrativeContextCache,
    ProgressCacheManager,
    RedisSessionManager,
    SessionCacheManager,
    SessionLifecycleManager,
)
from .session_state import (
    SessionState,
    SessionStateManager,
    StateTransition,
    StateValidator,
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
    "StateValidator",
    # Error handling and recovery
    "ErrorRecoveryManager",
    "ErrorContext",
    "RecoveryResult",
    "SystemBackup",
    "ErrorSeverity",
    "ErrorCategory",
    "RecoveryStrategy",
]
