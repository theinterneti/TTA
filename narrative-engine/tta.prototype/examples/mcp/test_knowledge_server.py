#!/usr/bin/env python3
"""
Test Knowledge Resource Server (DEVELOPMENT ONLY)

This script tests the knowledge resource server by running it and checking if it's operational.

NOTE: This script is intended for development and testing purposes only.
It should NOT be used in production environments.
"""

import os
import subprocess
import time


def main():
    """
    Main function to test the knowledge resource server.
    """
    print("Testing knowledge resource server...")

    try:
        # Start the server in a separate process
        server_process = subprocess.Popen(
            ["python3", "examples/mcp/knowledge_resource_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Give the server a moment to start
        time.sleep(2)

        # Check if the server is running
        if server_process.poll() is None:
            print("Knowledge resource server is running!")
            print(f"Server PID: {server_process.pid}")

            # Try to read any stderr output (non-blocking)
            stderr_data = b""
            while server_process.stderr.readable():
                try:
                    data = server_process.stderr.read(1024)
                    if not data:
                        break
                    stderr_data += data
                except Exception:
                    break

            if stderr_data:
                print(f"Server stderr: {stderr_data.decode('utf-8')}")
            else:
                print("No stderr output from server.")

            # Terminate the server
            print("Terminating server...")
            server_process.terminate()

            # Wait for the server to terminate (with timeout)
            try:
                server_process.wait(timeout=5)
                print("Server terminated gracefully.")
            except subprocess.TimeoutExpired:
                print("Server did not terminate gracefully, forcing kill...")
                server_process.kill()
                server_process.wait()
                print("Server killed.")
        else:
            print(f"Server failed to start! Exit code: {server_process.returncode}")
            stderr = server_process.stderr.read()
            if stderr:
                print(f"Server stderr: {stderr.decode('utf-8')}")

    except Exception as e:
        print(f"Error during test: {e}")

    # Make sure any lingering processes are killed
    try:
        os.system("pkill -f 'python3 examples/mcp/knowledge_resource_server.py'")
    except Exception:
        pass

    print("Test complete!")


if __name__ == "__main__":
    main()
