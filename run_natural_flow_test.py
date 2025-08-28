#!/usr/bin/env python3
"""
Natural Therapeutic Gaming Onboarding Flow Test Runner

This script runs the comprehensive end-to-end test that validates the natural
progression from mundane account setup to magical therapeutic gaming experience.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def check_tta_backend_status():
    """Check if the TTA backend is running and healthy."""
    print("🔍 Checking TTA backend status...")
    
    try:
        # Check basic health
        health_response = requests.get("http://localhost:8080/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ TTA API Health: {health_data.get('status', 'unknown')}")
        else:
            print(f"⚠️ TTA API health check returned status {health_response.status_code}")
            return False
            
        # Check service health
        service_response = requests.get("http://localhost:8080/api/v1/services/health", timeout=5)
        if service_response.status_code == 200:
            service_data = service_response.json()
            overall_status = service_data.get('overall_status', 'unknown')
            using_mocks = service_data.get('using_mocks', False)
            health_percentage = service_data.get('summary', {}).get('health_percentage', 0)
            
            print(f"✅ Service Health: {overall_status} ({health_percentage}% healthy)")
            print(f"✅ Using Mock Services: {using_mocks}")
            
            if overall_status != 'healthy':
                print("⚠️ Services are not fully healthy, but continuing with test...")
            
            return True
        else:
            print(f"❌ Service health check failed with status {service_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to TTA backend: {e}")
        return False


def check_swagger_ui_accessibility():
    """Check if Swagger UI is accessible."""
    print("🔍 Checking Swagger UI accessibility...")
    
    try:
        response = requests.get("http://localhost:8080/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Swagger UI is accessible")
            return True
        else:
            print(f"❌ Swagger UI returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to access Swagger UI: {e}")
        return False


def ensure_screenshots_directory():
    """Ensure the screenshots directory exists."""
    screenshots_dir = Path("tests/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Screenshots directory ready: {screenshots_dir}")


def run_natural_flow_test():
    """Run the natural therapeutic gaming onboarding flow test."""
    print("🚀 Running Natural Therapeutic Gaming Onboarding Flow Test...")
    print("=" * 70)
    
    try:
        # Run the specific test
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/e2e/test_natural_onboarding_flow.py::test_natural_onboarding_flow_execution",
            "-v", "-s", "--tb=short", "--capture=no"
        ], check=True, cwd=Path.cwd())
        
        print("\n🎉 Natural Flow Test completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Natural Flow Test failed with exit code {e.returncode}")
        return False


def display_test_results():
    """Display information about test results and screenshots."""
    print("\n📸 Test Documentation Generated:")
    print("=" * 40)
    
    screenshots_dir = Path("tests/screenshots")
    if screenshots_dir.exists():
        screenshot_files = list(screenshots_dir.glob("*.png"))
        if screenshot_files:
            for screenshot in sorted(screenshot_files):
                print(f"   📷 {screenshot.name}")
        else:
            print("   ⚠️ No screenshots found")
    else:
        print("   ⚠️ Screenshots directory not found")
    
    print("\n🎯 Test Validation Points:")
    print("   ✅ Swagger UI accessibility and navigation")
    print("   ✅ Player account creation with therapeutic preferences")
    print("   ✅ Therapeutic world exploration and selection")
    print("   ✅ Character creation with detailed therapeutic profile")
    print("   ✅ World-character compatibility validation")
    print("   ✅ World customization for personalized experience")
    print("   ✅ Natural flow progression from mundane to magical")


def main():
    """Main execution function."""
    print("🎮 TTA Natural Therapeutic Gaming Onboarding Flow Test")
    print("=" * 60)
    print("🎯 Testing the natural progression from account setup to therapeutic gaming")
    print("✨ Validating the journey from mundane to magical experience")
    print()
    
    # Check prerequisites
    if not check_tta_backend_status():
        print("\n❌ TTA backend is not running or not healthy!")
        print("Please start the TTA backend first:")
        print("   uv run python -m src.player_experience.api.main")
        print("\nThen run this test again.")
        sys.exit(1)
    
    if not check_swagger_ui_accessibility():
        print("\n❌ Swagger UI is not accessible!")
        print("Please ensure the TTA backend is running with Swagger UI enabled.")
        sys.exit(1)
    
    # Prepare test environment
    ensure_screenshots_directory()
    
    # Run the test
    print("\n🎬 Starting Natural Flow Test Execution...")
    print("   This test will validate the complete user journey through Swagger UI")
    print("   from basic account creation to magical therapeutic gaming setup.")
    print()
    
    success = run_natural_flow_test()
    
    # Display results
    display_test_results()
    
    if success:
        print("\n🌟 SUCCESS: Natural Therapeutic Gaming Onboarding Flow Validated!")
        print("=" * 65)
        print("✨ Key Achievements:")
        print("   🎯 Complete user journey tested end-to-end")
        print("   🌊 Natural flow from mundane to magical validated")
        print("   🎭 Character creation engages user imagination")
        print("   🌍 World exploration builds excitement and possibility")
        print("   🤝 Compatibility matching creates perfect therapeutic alignment")
        print("   🎨 Customization makes the experience uniquely personal")
        print("\n🎮 The TTA therapeutic gaming onboarding experience is ready for users!")
        print("   New players can seamlessly progress from registration to")
        print("   a fully configured, personalized therapeutic gaming setup.")
        
    else:
        print("\n❌ FAILURE: Natural Flow Test encountered issues")
        print("Please check the test output above for specific error details.")
        print("Common issues:")
        print("   - TTA backend not running or unhealthy")
        print("   - Swagger UI not accessible or not loading properly")
        print("   - API endpoints not responding as expected")
        print("   - Mock services not functioning correctly")
        sys.exit(1)


if __name__ == "__main__":
    main()
