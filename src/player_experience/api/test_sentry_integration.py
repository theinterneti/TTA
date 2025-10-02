"""
Test script to verify Sentry integration is working correctly.

This script can be run to test that Sentry is properly configured
and can capture errors and performance data.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.player_experience.api.config import get_settings
from src.player_experience.api.sentry_config import (
    capture_therapeutic_error,
    capture_therapeutic_message,
    init_sentry,
)


def test_sentry_configuration():
    """Test that Sentry is properly configured."""
    print("🔧 Testing Sentry Configuration...")

    # Set up test environment
    # Note: In production, set SENTRY_DSN as an environment variable or GitHub secret
    # For testing, you can set it here temporarily or via environment
    if not os.getenv("SENTRY_DSN"):
        print("⚠️  SENTRY_DSN not set. Please set it as an environment variable.")
        print("   Example: export SENTRY_DSN='https://your-dsn@sentry.io/project-id'")
        return None

    os.environ["SENTRY_ENVIRONMENT"] = "development"
    os.environ["ENVIRONMENT"] = "development"

    # Get settings and initialize Sentry
    settings = get_settings()
    print(f"✅ Settings loaded: environment={settings.sentry_environment}")
    print(f"✅ Sentry DSN configured: {settings.sentry_dsn is not None}")

    # Initialize Sentry
    init_sentry(settings)
    print("✅ Sentry initialized successfully")

    return settings


def test_error_capture():
    """Test error capture functionality."""
    print("\n🚨 Testing Error Capture...")

    try:
        # Create a test error
        raise ValueError("This is a test error for Sentry integration")
    except Exception as e:
        # Capture with therapeutic context
        capture_therapeutic_error(
            e,
            context={
                "test_type": "integration_test",
                "component": "sentry_config",
                "safe_data": "This is safe to send",
                "therapeutic_content": "This should be filtered out",
            },
            user_id="test_user_123",
            session_id="test_session_456",
        )
        print("✅ Error captured with therapeutic filtering")


def test_message_capture():
    """Test message capture functionality."""
    print("\n📝 Testing Message Capture...")

    # Test info message
    capture_therapeutic_message(
        "Test info message from TTA integration test",
        level="info",
        context={"test_phase": "message_capture", "message_type": "info"},
    )
    print("✅ Info message captured")

    # Test warning message
    capture_therapeutic_message(
        "Test warning message from TTA integration test",
        level="warning",
        context={"test_phase": "message_capture", "message_type": "warning"},
    )
    print("✅ Warning message captured")


def test_data_filtering():
    """Test that sensitive data is properly filtered."""
    print("\n🔒 Testing Data Filtering...")

    try:
        # Create an error with sensitive data
        sensitive_data = {
            "user_password": "secret123",
            "therapeutic_notes": "Patient expressed anxiety about...",
            "api_key": "sk-1234567890",
            "safe_metric": "response_time_ms",
        }
        raise RuntimeError(f"Error with sensitive data: {sensitive_data}")
    except Exception as e:
        capture_therapeutic_error(
            e,
            context={
                "request_data": sensitive_data,
                "endpoint": "/api/v1/test",
                "method": "POST",
            },
        )
        print("✅ Error with sensitive data captured (should be filtered)")


def test_performance_tracking():
    """Test performance tracking functionality."""
    print("\n⚡ Testing Performance Tracking...")

    import time

    import sentry_sdk

    # Test transaction tracking
    with sentry_sdk.start_transaction(
        op="test", name="sentry_integration_test"
    ) as transaction:
        # Simulate some work
        with sentry_sdk.start_span(op="db.query", description="Test database query"):
            time.sleep(0.1)  # Simulate DB query time

        with sentry_sdk.start_span(op="http.request", description="Test API call"):
            time.sleep(0.05)  # Simulate API call time

        transaction.set_tag("test_type", "performance")
        transaction.set_data("test_data", "integration_test")

    print("✅ Performance transaction captured")


def main():
    """Run all Sentry integration tests."""
    print("🎯 TTA Sentry Integration Test")
    print("=" * 50)

    try:
        # Test configuration
        settings = test_sentry_configuration()
        if settings is None:
            print("❌ Sentry configuration failed. Exiting.")
            sys.exit(1)

        # Test error capture
        test_error_capture()

        # Test message capture
        test_message_capture()

        # Test data filtering
        test_data_filtering()

        # Test performance tracking
        test_performance_tracking()

        print("\n" + "=" * 50)
        print("🎉 All Sentry integration tests completed successfully!")
        print("\n📊 Check your Sentry dashboard at:")
        print("   https://sentry.io/organizations/your-org/projects/")
        print("\n💡 You should see:")
        print("   - Test errors with filtered sensitive data")
        print("   - Info and warning messages")
        print("   - Performance transaction data")
        print("   - Proper environment tagging")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
