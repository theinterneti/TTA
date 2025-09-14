#!/usr/bin/env python3
"""
Verify MCP Integration

This script verifies that the MCP integration is working correctly.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the script."""
    logger.info("Verifying MCP integration...")

    # Check if the MCP module is available
    try:
        import mcp

        logger.info(f"MCP module found: {mcp.__file__}")
    except ImportError:
        logger.error(
            "MCP module not found. Please install it with 'pip install fastmcp'."
        )
        return False

    # Check if the MCP configuration file exists
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config",
        "mcp_config.json",
    )
    if os.path.exists(config_path):
        logger.info(f"MCP configuration file found: {config_path}")
    else:
        logger.error(f"MCP configuration file not found: {config_path}")
        return False

    # Check if the MCP server scripts exist
    server_scripts = [
        os.path.join(os.path.dirname(__file__), "basic_server.py"),
        os.path.join(os.path.dirname(__file__), "agent_tool_server.py"),
        os.path.join(os.path.dirname(__file__), "knowledge_resource_server.py"),
    ]

    for script in server_scripts:
        if os.path.exists(script):
            logger.info(f"MCP server script found: {script}")
        else:
            logger.error(f"MCP server script not found: {script}")
            return False

    # Check if the MCP server manager is available
    try:
        from src.mcp import MCPConfig, MCPServerManager

        logger.info("MCP server manager found")
    except ImportError:
        logger.error("MCP server manager not found")
        return False

    # Try to create an MCP server manager
    try:
        config = MCPConfig()
        MCPServerManager(config=config)
        logger.info("MCP server manager created successfully")
    except Exception as e:
        logger.error(f"Error creating MCP server manager: {e}")
        return False

    logger.info("MCP integration verification complete")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
