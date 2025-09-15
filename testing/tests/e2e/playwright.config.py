"""
Playwright Configuration for TTA Player Interface Testing

This configuration provides optimized settings for testing the React frontend
with proper browser setup, timeouts, and test environment configuration.
"""

import os
from pathlib import Path

# Test configuration
PLAYWRIGHT_CONFIG = {
    # Browser settings
    "browser": "chromium",  # Can be changed to "firefox" or "webkit"
    "headless": False,  # Set to True for CI/CD environments
    "slow_mo": 500,  # Slow down actions for better visibility
    # Viewport settings
    "viewport": {"width": 1920, "height": 1080},
    # Timeout settings
    "timeout": 30000,  # 30 seconds default timeout
    "navigation_timeout": 30000,
    "expect_timeout": 10000,
    # Test environment URLs
    "base_url": "http://localhost:3000",
    "api_url": "http://localhost:8080",
    # Screenshot and video settings
    "screenshot_on_failure": True,
    "video_on_failure": True,
    "trace_on_failure": True,
    # Browser launch arguments
    "browser_args": [
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-gpu",
    ],
    # Test directories
    "test_dir": Path(__file__).parent,
    "screenshot_dir": Path(__file__).parent / "screenshots",
    "video_dir": Path(__file__).parent / "videos",
    "trace_dir": Path(__file__).parent / "traces",
}

# Ensure directories exist
for dir_path in [
    PLAYWRIGHT_CONFIG["screenshot_dir"],
    PLAYWRIGHT_CONFIG["video_dir"],
    PLAYWRIGHT_CONFIG["trace_dir"],
]:
    dir_path.mkdir(exist_ok=True)

# Environment-specific overrides
if os.getenv("CI"):
    PLAYWRIGHT_CONFIG.update(
        {
            "headless": True,
            "slow_mo": 0,
            "screenshot_on_failure": True,
            "video_on_failure": False,  # Disable video in CI to save space
        }
    )


# Export configuration for pytest-playwright
def pytest_configure(config):
    """Configure pytest with Playwright settings."""
    config.option.browser_name = [PLAYWRIGHT_CONFIG["browser"]]
    config.option.headed = not PLAYWRIGHT_CONFIG["headless"]
    config.option.slowmo = PLAYWRIGHT_CONFIG["slow_mo"]
