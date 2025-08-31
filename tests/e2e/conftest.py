"""
Configuration for End-to-End tests using Playwright.

This module provides fixtures and configuration for E2E testing of the
TTA AI Agent Orchestration system through the web interface.
"""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for E2E tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Browser:
    """Launch browser for E2E tests."""
    browser = playwright.chromium.launch(
        headless=False,  # Set to True for CI/CD
        slow_mo=500,  # Slow down for better visibility
        args=[
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
        ],
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    """Create browser context for each test."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Create page for each test."""
    page = context.new_page()

    # Set longer timeouts for API operations
    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)

    yield page
    page.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure TTA server is running
    import time

    import requests

    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ TTA server is running and ready for E2E tests")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                pytest.skip(
                    "TTA server is not running. Please start the server with: uv run python -m src.player_experience.api.main"
                )
            time.sleep(2)

    yield

    # Cleanup after test if needed
    pass
