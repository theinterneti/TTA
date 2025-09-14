#!/usr/bin/env python3
"""
MCP Test Client for Running Server

This script demonstrates how to use the MCP Python SDK to interact with a running MCP server.
"""

import requests


def main():
    """
    Main function to test a running MCP server.
    """
    print("Testing running MCP server...")

    # Use a simple HTTP request to test the server
    try:
        # Make a request to the server
        print("Making a request to the server at localhost:8000...")
        response = requests.get("http://localhost:8000", timeout=5)

        # Check if the server is responding
        if response.status_code == 200:
            print("Server is responding!")
            print(f"Response: {response.text}")
        else:
            print(f"Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server. Make sure it's running on localhost:8000.")
    except Exception as e:
        print(f"Error: {e}")

    print("Test complete!")

if __name__ == "__main__":
    main()
