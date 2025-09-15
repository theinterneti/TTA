#!/usr/bin/env python3
"""
Player Interface Test Runner

This script runs comprehensive Playwright tests for the TTA player interface,
including setup verification, test execution, and result reporting.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests


class PlayerInterfaceTestRunner:
    """Test runner for player interface Playwright tests."""

    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8080"
        self.test_dir = Path(__file__).parent

    def check_service_health(self, url: str, service_name: str) -> bool:
        """Check if a service is running and healthy."""
        try:
            response = requests.get(
                f"{url}/health" if "8080" in url else url, timeout=5
            )
            if response.status_code == 200:
                print(f"✅ {service_name} is running and healthy")
                return True
            else:
                print(f"❌ {service_name} returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name} is not accessible: {e}")
            return False

    def verify_prerequisites(self) -> bool:
        """Verify all prerequisites are met before running tests."""
        print("🔍 Verifying test prerequisites...")

        # Check backend service
        backend_healthy = self.check_service_health(self.backend_url, "Backend API")

        # Check frontend service
        frontend_healthy = self.check_service_health(self.frontend_url, "Frontend App")

        if not backend_healthy or not frontend_healthy:
            print(
                "\n❌ Prerequisites not met. Please ensure both services are running:"
            )
            print(f"   - Backend API: {self.backend_url}")
            print(f"   - Frontend App: {self.frontend_url}")
            return False

        print("✅ All prerequisites verified")
        return True

    def install_playwright_browsers(self) -> bool:
        """Install Playwright browsers if needed."""
        try:
            print("🔧 Installing Playwright browsers...")
            result = subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                print("✅ Playwright browsers installed successfully")
                return True
            else:
                print(f"❌ Failed to install Playwright browsers: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Playwright browser installation timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing Playwright browsers: {e}")
            return False

    def run_tests(
        self, test_pattern: str = "test_player_interface.py"
    ) -> dict[str, Any]:
        """Run Playwright tests and return results."""
        print(f"🚀 Running Playwright tests: {test_pattern}")

        # Prepare test command
        cmd = [
            "python",
            "-m",
            "pytest",
            str(self.test_dir / test_pattern),
            "-v",
            "--tb=short",
        ]

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                cwd=Path(__file__).parent.parent.parent,  # Run from project root
            )

            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": "Test execution timed out after 10 minutes",
                "return_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "stdout": "",
                "stderr": f"Error running tests: {e}",
                "return_code": -1,
            }

    def generate_report(self, results: dict[str, Any]) -> None:
        """Generate and display test results report."""
        print("\n" + "=" * 60)
        print("🎭 PLAYWRIGHT PLAYER INTERFACE TEST RESULTS")
        print("=" * 60)

        if results["success"]:
            print("✅ Status: PASSED")
        else:
            print("❌ Status: FAILED")

        print(f"⏱️  Duration: {results['duration']:.2f} seconds")
        print(f"🔢 Return Code: {results['return_code']}")

        if results["stdout"]:
            print("\n📊 Test Output:")
            print("-" * 40)
            print(results["stdout"])

        if results["stderr"]:
            print("\n⚠️  Error Output:")
            print("-" * 40)
            print(results["stderr"])

        # Check for generated artifacts
        screenshots_dir = self.test_dir / "screenshots"
        if screenshots_dir.exists() and list(screenshots_dir.glob("*.png")):
            print(f"\n📸 Screenshots saved to: {screenshots_dir}")

        reports_dir = self.test_dir / "reports"
        if (
            reports_dir.exists()
            and (reports_dir / "player_interface_report.html").exists()
        ):
            print(f"📋 HTML Report: {reports_dir / 'player_interface_report.html'}")

        print("=" * 60)

    def run_full_test_suite(self) -> bool:
        """Run the complete test suite with all checks."""
        print("🎭 Starting Playwright Player Interface Test Suite")
        print("=" * 60)

        # Step 1: Verify prerequisites
        if not self.verify_prerequisites():
            return False

        # Step 2: Install browsers if needed
        if not self.install_playwright_browsers():
            print(
                "⚠️  Warning: Browser installation failed, but continuing with tests..."
            )

        # Step 3: Create necessary directories
        (self.test_dir / "screenshots").mkdir(exist_ok=True)
        (self.test_dir / "reports").mkdir(exist_ok=True)
        (self.test_dir / "videos").mkdir(exist_ok=True)

        # Step 4: Run tests
        results = self.run_tests()

        # Step 5: Generate report
        self.generate_report(results)

        return results["success"]


def main():
    """Main entry point for test runner."""
    runner = PlayerInterfaceTestRunner()
    success = runner.run_full_test_suite()

    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
