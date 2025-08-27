"""
WebSocket connection manager for the API Gateway.

This module provides comprehensive WebSocket connection management including
authentication, session tracking, therapeutic prioritization, and connection lifecycle.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Set, Any, Callable
from uuid import uuid4, UUID
from enum import Enum
from dataclasses import dataclass, field

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from ..models import AuthContext, ServiceInfo
from ..config import get_gateway_settings


logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """WebSocket connection types."""
    CHAT = "chat"
    NARRATIVE = "narrative"
    THERAPEUTIC_SESSION = "therapeutic_session"
    CRISIS_SUPPORT = "crisis_support"
    ADMIN = "admin"
    MONITORING = "monitoring"


class ConnectionStatus(Enum):
    """WebSocket connection status."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    IDLE = "idle"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class WebSocketConnection:
    """WebSocket connection information."""
    connection_id: str
    websocket: WebSocket
    connection_type: ConnectionType
    user_id: Optional[str] = None
    username: Optional[str] = None
    auth_context: Optional[AuthContext] = None
    therapeutic_session_id: Optional[str] = None
    crisis_mode: bool = False
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    target_service: Optional[ServiceInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_therapeutic(self) -> bool:
        """Check if this is a therapeutic connection."""
        return self.connection_type in [
            ConnectionType.THERAPEUTIC_SESSION,
            ConnectionType.CRISIS_SUPPORT
        ] or self.therapeutic_session_id is not None
    
    def is_crisis(self) -> bool:
        """Check if this is a crisis connection."""
        return (self.connection_type == ConnectionType.CRISIS_SUPPORT or 
                self.crisis_mode)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def get_connection_duration(self) -> float:
        """Get connection duration in seconds."""
        return time.time() - self.connected_at
    
    def get_idle_time(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_activity


class WebSocketConnectionManager:
    """
    WebSocket connection manager for the API Gateway.
    
    Manages WebSocket connections with authentication, session tracking,
    therapeutic prioritization, and comprehensive connection lifecycle management.
    """
    
    def __init__(self):
        """Initialize the WebSocket connection manager."""
        self.settings = get_gateway_settings()
        
        # Connection storage
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        self.service_connections: Dict[str, Set[str]] = {}  # service_name -> connection_ids
        
        # Connection limits and timeouts
        self.max_connections_per_user = 5
        self.max_total_connections = 10000
        self.idle_timeout = 300  # 5 minutes
        self.therapeutic_idle_timeout = 1800  # 30 minutes for therapeutic sessions
        self.crisis_idle_timeout = 3600  # 1 hour for crisis sessions
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_idle_connections())
    
    async def _cleanup_idle_connections(self) -> None:
        """Background task to cleanup idle connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._remove_idle_connections()
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def _remove_idle_connections(self) -> None:
        """Remove idle connections based on timeout settings."""
        current_time = time.time()
        connections_to_remove = []
        
        for connection_id, connection in self.connections.items():
            # Determine timeout based on connection type
            timeout = self.idle_timeout
            if connection.is_crisis():
                timeout = self.crisis_idle_timeout
            elif connection.is_therapeutic():
                timeout = self.therapeutic_idle_timeout
            
            # Check if connection is idle
            if current_time - connection.last_activity > timeout:
                connections_to_remove.append(connection_id)
                logger.info(
                    f"Removing idle connection {connection_id} "
                    f"(idle for {connection.get_idle_time():.1f}s)"
                )
        
        # Remove idle connections
        for connection_id in connections_to_remove:
            await self.disconnect(connection_id, reason="idle_timeout")
    
    async def connect(self, websocket: WebSocket, connection_type: ConnectionType,
                     auth_context: Optional[AuthContext] = None,
                     therapeutic_session_id: Optional[str] = None,
                     target_service: Optional[ServiceInfo] = None) -> str:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket instance
            connection_type: Type of connection
            auth_context: Authentication context if available
            therapeutic_session_id: Therapeutic session ID if applicable
            target_service: Target service for proxying
            
        Returns:
            Connection ID
            
        Raises:
            Exception: If connection cannot be established
        """
        # Check connection limits
        if len(self.connections) >= self.max_total_connections:
            await websocket.close(code=1013, reason="Server overloaded")
            raise Exception("Maximum connections exceeded")
        
        # Check per-user limits
        if auth_context and auth_context.user_id:
            user_id = str(auth_context.user_id)
            user_connection_count = len(self.user_connections.get(user_id, set()))
            if user_connection_count >= self.max_connections_per_user:
                await websocket.close(code=1013, reason="Too many connections")
                raise Exception(f"Maximum connections per user exceeded: {user_connection_count}")
        
        # Accept WebSocket connection
        await websocket.accept()
        
        # Create connection record
        connection_id = str(uuid4())
        connection = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket,
            connection_type=connection_type,
            user_id=str(auth_context.user_id) if auth_context and auth_context.user_id else None,
            username=auth_context.username if auth_context else None,
            auth_context=auth_context,
            therapeutic_session_id=therapeutic_session_id,
            crisis_mode=auth_context.crisis_mode if auth_context else False,
            status=ConnectionStatus.CONNECTED,
            client_ip=self._get_client_ip(websocket),
            user_agent=self._get_user_agent(websocket),
            target_service=target_service
        )
        
        # Store connection
        self.connections[connection_id] = connection
        
        # Index by user
        if connection.user_id:
            if connection.user_id not in self.user_connections:
                self.user_connections[connection.user_id] = set()
            self.user_connections[connection.user_id].add(connection_id)
        
        # Index by therapeutic session
        if therapeutic_session_id:
            if therapeutic_session_id not in self.session_connections:
                self.session_connections[therapeutic_session_id] = set()
            self.session_connections[therapeutic_session_id].add(connection_id)
        
        # Index by service
        if target_service:
            service_name = target_service.name
            if service_name not in self.service_connections:
                self.service_connections[service_name] = set()
            self.service_connections[service_name].add(connection_id)
        
        logger.info(
            f"WebSocket connection established: {connection_id} "
            f"(type: {connection_type.value}, user: {connection.username}, "
            f"therapeutic: {connection.is_therapeutic()})"
        )
        
        return connection_id
    
    async def disconnect(self, connection_id: str, reason: str = "normal_closure") -> None:
        """
        Disconnect and cleanup a WebSocket connection.
        
        Args:
            connection_id: Connection ID to disconnect
            reason: Reason for disconnection
        """
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Update status
        connection.status = ConnectionStatus.DISCONNECTING
        
        # Close WebSocket if still open
        if connection.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await connection.websocket.close(code=1000, reason=reason)
            except Exception as e:
                logger.warning(f"Error closing WebSocket {connection_id}: {e}")
        
        # Remove from indexes
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]
        
        if connection.therapeutic_session_id and connection.therapeutic_session_id in self.session_connections:
            self.session_connections[connection.therapeutic_session_id].discard(connection_id)
            if not self.session_connections[connection.therapeutic_session_id]:
                del self.session_connections[connection.therapeutic_session_id]
        
        if connection.target_service:
            service_name = connection.target_service.name
            if service_name in self.service_connections:
                self.service_connections[service_name].discard(connection_id)
                if not self.service_connections[service_name]:
                    del self.service_connections[service_name]
        
        # Remove connection
        connection.status = ConnectionStatus.DISCONNECTED
        del self.connections[connection_id]
        
        logger.info(
            f"WebSocket connection closed: {connection_id} "
            f"(reason: {reason}, duration: {connection.get_connection_duration():.1f}s)"
        )
    
    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection by ID."""
        return self.connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[WebSocketConnection]:
        """Get all connections for a user."""
        connection_ids = self.user_connections.get(user_id, set())
        return [self.connections[cid] for cid in connection_ids if cid in self.connections]
    
    def get_session_connections(self, session_id: str) -> List[WebSocketConnection]:
        """Get all connections for a therapeutic session."""
        connection_ids = self.session_connections.get(session_id, set())
        return [self.connections[cid] for cid in connection_ids if cid in self.connections]
    
    def get_service_connections(self, service_name: str) -> List[WebSocketConnection]:
        """Get all connections for a service."""
        connection_ids = self.service_connections.get(service_name, set())
        return [self.connections[cid] for cid in connection_ids if cid in self.connections]
    
    def get_therapeutic_connections(self) -> List[WebSocketConnection]:
        """Get all therapeutic connections."""
        return [conn for conn in self.connections.values() if conn.is_therapeutic()]
    
    def get_crisis_connections(self) -> List[WebSocketConnection]:
        """Get all crisis connections."""
        return [conn for conn in self.connections.values() if conn.is_crisis()]
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        try:
            # Update activity
            connection.update_activity()
            
            # Send message
            await connection.websocket.send_text(json.dumps(message))
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            # Connection might be broken, schedule for cleanup
            await self.disconnect(connection_id, reason="send_error")
            return False
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all connections of a user.
        
        Args:
            user_id: Target user ID
            message: Message to broadcast
            
        Returns:
            Number of connections that received the message
        """
        connections = self.get_user_connections(user_id)
        sent_count = 0
        
        for connection in connections:
            if await self.send_message(connection.connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all connections in a therapeutic session.
        
        Args:
            session_id: Target session ID
            message: Message to broadcast
            
        Returns:
            Number of connections that received the message
        """
        connections = self.get_session_connections(session_id)
        sent_count = 0
        
        for connection in connections:
            if await self.send_message(connection.connection_id, message):
                sent_count += 1
        
        return sent_count
    
    def _get_client_ip(self, websocket: WebSocket) -> Optional[str]:
        """Extract client IP from WebSocket."""
        if websocket.client:
            return websocket.client.host
        return None
    
    def _get_user_agent(self, websocket: WebSocket) -> Optional[str]:
        """Extract user agent from WebSocket headers."""
        return websocket.headers.get("user-agent")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_connections = len(self.connections)
        therapeutic_connections = len(self.get_therapeutic_connections())
        crisis_connections = len(self.get_crisis_connections())
        
        # Connection types breakdown
        type_counts = {}
        for connection in self.connections.values():
            conn_type = connection.connection_type.value
            type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
        
        # Status breakdown
        status_counts = {}
        for connection in self.connections.values():
            status = connection.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_connections": total_connections,
            "therapeutic_connections": therapeutic_connections,
            "crisis_connections": crisis_connections,
            "unique_users": len(self.user_connections),
            "active_sessions": len(self.session_connections),
            "connected_services": len(self.service_connections),
            "connection_types": type_counts,
            "connection_status": status_counts,
            "max_connections": self.max_total_connections,
            "max_per_user": self.max_connections_per_user
        }
    
    async def shutdown(self) -> None:
        """Shutdown connection manager and cleanup resources."""
        logger.info("Shutting down WebSocket connection manager")
        
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        connection_ids = list(self.connections.keys())
        for connection_id in connection_ids:
            await self.disconnect(connection_id, reason="server_shutdown")
        
        logger.info("WebSocket connection manager shutdown complete")
