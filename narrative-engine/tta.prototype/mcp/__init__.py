"""
MCP package for the TTA project.

This package provides MCP (Model Context Protocol) server implementations
and utilities for the Therapeutic Text Adventure project.
"""

from .agent_adapter import AgentMCPAdapter, create_agent_mcp_server
from .config import MCPConfig
from .server_manager import MCPServerManager
from .server_types import MCPServerType

__all__ = [
    'AgentMCPAdapter',
    'create_agent_mcp_server',
    'MCPServerType',
    'MCPConfig',
    'MCPServerManager'
]
