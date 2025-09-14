#!/usr/bin/env python3
"""
Basic MCP Server Example (DEVELOPMENT ONLY)

This example demonstrates a simple MCP server using FastMCP.
It provides basic tools and resources to demonstrate the core concepts.

NOTE: This server is intended for development and learning purposes only.
It should NOT be used in production environments.
"""

import os

from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP(
    "TTA Basic Server",
    description="A basic MCP server for the Therapeutic Text Adventure",
    dependencies=["fastmcp", "requests"]
)

# ---- Tools ----

@mcp.tool()
def echo(message: str) -> str:
    """
    Echo a message back to the user.

    Args:
        message: The message to echo

    Returns:
        The same message
    """
    return f"Echo: {message}"

@mcp.tool()
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A mathematical expression (e.g., "2 + 2")

    Returns:
        The result of the expression
    """
    # This is a very simple and limited calculator for demonstration
    # In a real application, you'd want more robust parsing and validation
    allowed_chars = set("0123456789+-*/() .")
    if not all(c in allowed_chars for c in expression):
        return "Error: Expression contains invalid characters"

    try:
        # Using eval is generally not recommended for user input
        # This is just for demonstration purposes
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# ---- Resources ----

@mcp.resource("info://server")
def get_server_info() -> str:
    """
    Get information about this MCP server.
    """
    return """
    TTA Basic MCP Server
    ====================

    This is a basic MCP server for the Therapeutic Text Adventure project.
    It demonstrates the core concepts of MCP servers.

    Available tools:
    - echo: Echo a message back to the user
    - calculate: Safely evaluate a mathematical expression

    Available resources:
    - info://server: Get information about this server
    - info://system: Get basic system information
    - info://environment/{var_name}: Get an environment variable
    """

@mcp.resource("info://system")
def get_system_info() -> str:
    """
    Get basic system information.
    """
    import platform

    return f"""
    System Information
    =================

    Python version: {platform.python_version()}
    Platform: {platform.platform()}
    Processor: {platform.processor()}
    """

@mcp.resource("info://environment/{var_name}")
def get_environment_variable(var_name: str) -> str:
    """
    Get an environment variable.

    Args:
        var_name: The name of the environment variable
    """
    # Only allow access to non-sensitive environment variables
    allowed_vars = {"PATH", "PYTHONPATH", "USER", "HOME", "SHELL"}

    if var_name not in allowed_vars:
        return f"Error: Access to environment variable '{var_name}' is not allowed"

    value = os.environ.get(var_name, "Not set")
    return f"{var_name}={value}"

# ---- Prompts ----

@mcp.prompt()
def help_prompt() -> str:
    """
    Create a help prompt for this server.
    """
    return """
    I'm the TTA Basic MCP Server. I can help you with:

    1. Echoing messages
    2. Calculating simple mathematical expressions
    3. Providing system information

    What would you like to do?
    """

# ---- Main ----

if __name__ == "__main__":
    import argparse
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Basic MCP Server Example")

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug logging enabled")

    # Run the server
    logging.info(f"Starting MCP server on {args.host}:{args.port}")
    # Check if the run method accepts host and port arguments
    import inspect
    run_params = inspect.signature(mcp.run).parameters
    if 'host' in run_params and 'port' in run_params:
        mcp.run(host=args.host, port=args.port)
    else:
        # Older versions of fastmcp might not accept host and port
        mcp.run()
