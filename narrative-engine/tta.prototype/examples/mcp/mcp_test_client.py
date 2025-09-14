#!/usr/bin/env python3
"""
MCP Test Client (DEVELOPMENT ONLY)

This script demonstrates how to use the MCP Python SDK to interact with an MCP server.

NOTE: This script is intended for development and testing purposes only.
It should NOT be used in production environments.
"""

import asyncio
import subprocess

from mcp.client.session import ClientSession
from mcp.stdio_client import StdioClientParameters


async def main():
    """
    Main function to test MCP servers.
    """
    print("Testing MCP server...")

    # Start the server process
    server_process = subprocess.Popen(
        ["python3", "examples/mcp/basic_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Use binary mode for pipes
    )

    # Create client parameters
    params = StdioClientParameters(
        stdin=server_process.stdout,
        stdout=server_process.stdin
    )

    # Create a client session
    session = ClientSession()

    try:
        # Initialize the session
        print("Initializing session...")
        await session.initialize(params)

        # Get server info
        print("Getting server info...")
        server_info = await session.initialize_result
        print(f"Server info: {server_info}")

        # List available tools
        print("Listing tools...")
        tools_result = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools_result.tools]}")

        # Call the echo tool
        print("Calling echo tool...")
        echo_result = await session.call_tool("echo", {"message": "Hello, MCP!"})
        print(f"Echo result: {echo_result.result}")

        # Call the calculate tool
        print("Calling calculate tool...")
        calc_result = await session.call_tool("calculate", {"expression": "2 + 2"})
        print(f"Calculate result: {calc_result.result}")

        # List available resources
        print("Listing resources...")
        resources_result = await session.list_resources()
        print(f"Available resources: {resources_result.resources}")

        # Read a resource
        print("Reading server info resource...")
        resource_result = await session.read_resource("info://server")
        print(f"Resource content: {resource_result.content}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Shutdown the session
        print("Shutting down session...")
        await session.shutdown()

        # Terminate the server process
        server_process.terminate()
        server_process.wait()

    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
