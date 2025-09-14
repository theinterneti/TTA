#!/usr/bin/env python3
"""
Test client for MCP servers (DEVELOPMENT ONLY)

This script demonstrates how to interact with an MCP server programmatically.

NOTE: This script is intended for development and testing purposes only.
It should NOT be used in production environments.
"""

import json
import subprocess
import time


def main():
    """
    Main function to test MCP servers.
    """
    print("Testing MCP server...")

    # Start the server in a separate process
    server_process = subprocess.Popen(
        ["python3", "examples/mcp/basic_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give the server a moment to start
    time.sleep(1)

    # Send a handshake message
    handshake = {
        "type": "handshake",
        "version": "2025-03-26",
        "capabilities": {
            "transports": ["stdio"]
        }
    }

    print("Sending handshake...")
    server_process.stdin.write(json.dumps(handshake) + "\n")
    server_process.stdin.flush()

    # Read the response
    response = server_process.stdout.readline()
    print(f"Received: {response}")

    # Parse the response
    try:
        response_data = json.loads(response)
        if response_data.get("type") == "handshake_response":
            print("Handshake successful!")

            # Get server info
            info_request = {
                "type": "server_info_request",
                "request_id": "1"
            }

            print("Requesting server info...")
            server_process.stdin.write(json.dumps(info_request) + "\n")
            server_process.stdin.flush()

            # Read the response
            response = server_process.stdout.readline()
            print(f"Received: {response}")

            # Try calling a tool
            tool_request = {
                "type": "tool_call_request",
                "request_id": "2",
                "tool": "echo",
                "parameters": {
                    "message": "Hello, MCP!"
                }
            }

            print("Calling echo tool...")
            server_process.stdin.write(json.dumps(tool_request) + "\n")
            server_process.stdin.flush()

            # Read the response
            response = server_process.stdout.readline()
            print(f"Received: {response}")
        else:
            print("Handshake failed!")
    except json.JSONDecodeError:
        print("Failed to parse response!")

    # Clean up
    server_process.terminate()
    print("Test complete!")

if __name__ == "__main__":
    main()
