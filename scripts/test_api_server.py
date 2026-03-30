# Logseq: [[TTA.dev/Scripts/Test_api_server]]
# ruff: noqa: ALL
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

    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        assert response.status_code == 200
        assert (
            "Player Experience Interface API is running" in response.json()["message"]
        )

        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Test OpenAPI docs
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        assert response.status_code == 200
        openapi_spec = response.json()
        assert openapi_spec["info"]["title"] == "Player Experience Interface API"

        # Test authentication endpoint
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"username": "test", "password": "test"},
            timeout=5,
        )
        assert response.status_code == 401  # Expected for invalid credentials

        # Test protected endpoint without auth
        response = requests.get(f"{base_url}/api/v1/players/", timeout=5)
        assert response.status_code == 401  # Expected without authentication

        return True

    except requests.exceptions.RequestException:
        return False
    except AssertionError:
        return False
    except Exception:
        return False


def main():
    """Main test function."""

    # Start the server
    server_process = start_server()

    try:
        # Wait for server to start
        time.sleep(3)

        # Check if server is running
        if server_process.poll() is not None:
            return False

        # Test the endpoints
        return test_server_endpoints()

    finally:
        # Clean up: terminate the server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
