"""
Unified Authentication API

FastAPI routers and endpoints for the consolidated TTA authentication system.
"""

from .unified_auth_router import router as unified_auth_router

__all__ = [
    "unified_auth_router",
]
