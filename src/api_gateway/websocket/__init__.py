"""
WebSocket proxying and real-time communication handling for the API Gateway.

This module provides WebSocket proxy functionality for real-time therapeutic sessions,
chat services, and narrative interactions with comprehensive connection management,
message routing, and therapeutic safety features.
"""

# WebSocket components
from .connection_manager import (
    ConnectionStatus,
    ConnectionType,
    WebSocketConnection,
    WebSocketConnectionManager,
)
from .proxy import WebSocketProxy
from .router import WebSocketRouter, create_websocket_router

__all__ = [
    "WebSocketConnectionManager",
    "WebSocketConnection",
    "ConnectionType",
    "ConnectionStatus",
    "WebSocketProxy",
    "WebSocketRouter",
    "create_websocket_router",
]
