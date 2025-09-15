#!/usr/bin/env python3
"""
Script to run the TTA AI Agent Orchestration System E2E Player Onboarding Test.

This script ensures the TTA server is running and executes the complete
end-to-end test of the player onboarding flow through Playwright.
"""

import subprocess
import sys
from pathlib import Path

import requests


def check_server_status():
    """Check if the TTA server is running."""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ TTA server is running and ready")
            return True
    except requests.exceptions.RequestException:
        pass
    return False


def install_playwright():
    """Install Playwright browsers if needed."""
    print("🔧 Installing Playwright browsers...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
        print("✅ Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False
    return True


def run_e2e_test():
    """Run the E2E test."""
    print("🚀 Running TTA Player Onboarding E2E Test...")

    # Ensure screenshots directory exists
    Path("tests/screenshots").mkdir(parents=True, exist_ok=True)

    try:
        # Run the specific E2E test
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/e2e/test_player_onboarding_flow.py::TestPlayerOnboardingFlow::test_complete_player_onboarding_flow",
                "-v",
                "-s",
                "--tb=short",
            ],
            check=True,
        )

        print("\n🎉 E2E Test completed successfully!")
        print("📸 Screenshots saved in tests/screenshots/")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ E2E Test failed: {e}")
        return False


def main():
    """Main execution function."""
    print("🎮 TTA AI Agent Orchestration System - E2E Player Onboarding Test")
    print("=" * 70)

    # Check if server is running
    if not check_server_status():
        print("❌ TTA server is not running!")
        print("Please start the server first:")
        print("   uv run python -m src.player_experience.api.main")
        print("\nThen run this script again.")
        sys.exit(1)

    # Install Playwright if needed
    if not install_playwright():
        sys.exit(1)

    # Run the E2E test
    if run_e2e_test():
        print(
            "\n✅ All tests passed! The TTA player onboarding flow is working correctly."
        )
        print(
            "🎯 New players can successfully complete the full therapeutic gaming onboarding experience."
        )
    else:
        print("\n❌ Tests failed. Please check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
