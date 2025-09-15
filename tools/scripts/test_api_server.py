#!/usr/bin/env python3
"""
Test script to verify the FastAPI server can start and respond to requests.

This script starts the server briefly and makes a few test requests to verify
that the basic functionality is working.
"""

import os
import subprocess
import sys
import time

import requests


def start_server():
    """Start the FastAPI server in a subprocess."""
    env = os.environ.copy()
    env["ENVIRONMENT"] = "test"

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.player_experience.api.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8081",  # Use different port to avoid conflicts
            "--log-level",
            "warning",
        ],
        env=env,
    )


def test_server_endpoints():
    """Test the server endpoints."""
    base_url = "http://127.0.0.1:8081"

    print("Testing server endpoints...")

    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        assert response.status_code == 200
        assert (
            "Player Experience Interface API is running" in response.json()["message"]
        )
        print("✓ Root endpoint working")

        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✓ Health endpoint working")

        # Test OpenAPI docs
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        assert response.status_code == 200
        openapi_spec = response.json()
        assert openapi_spec["info"]["title"] == "Player Experience Interface API"
        print("✓ OpenAPI documentation available")

        # Test authentication endpoint
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"username": "test", "password": "test"},
            timeout=5,
        )
        assert response.status_code == 401  # Expected for invalid credentials
        print("✓ Authentication endpoint working")

        # Test protected endpoint without auth
        response = requests.get(f"{base_url}/api/v1/players/", timeout=5)
        assert response.status_code == 401  # Expected without authentication
        print("✓ Protected endpoints require authentication")

        print("\n🎉 All tests passed! FastAPI server is working correctly.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test assertion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main test function."""
    print("Starting FastAPI server test...")

    # Start the server
    server_process = start_server()

    try:
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)

        # Check if server is running
        if server_process.poll() is not None:
            print("❌ Server failed to start")
            return False

        # Test the endpoints
        success = test_server_endpoints()

        return success

    finally:
        # Clean up: terminate the server
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()
        print("Server shut down.")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
