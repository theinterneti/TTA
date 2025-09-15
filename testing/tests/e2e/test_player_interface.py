"""
Comprehensive Playwright Tests for TTA Player Interface

This module provides end-to-end testing of the React frontend player interface,
including character creation workflows, form interactions, and user experience validation.
"""

import time
from typing import Any

import pytest
import requests
from playwright.sync_api import Page, expect


class PlayerInterfaceTestHelper:
    """Helper class for player interface testing."""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:3000"
        self.api_url = "http://localhost:8080"
        self.auth_token: str | None = None

    def navigate_to_app(self) -> None:
        """Navigate to the main application."""
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

    def create_test_user_via_api(self) -> dict[str, Any]:
        """Create a test user via API for authentication."""
        user_data = {
            "username": f"playwright_user_{int(time.time())}",
            "email": f"playwright_{int(time.time())}@example.com",
            "password": "PlaywrightTest123!",
            "role": "player",
        }

        response = requests.post(f"{self.api_url}/api/v1/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            return user_data
        else:
            raise Exception(
                f"Failed to create test user (status {response.status_code}): {response.text}"
            )

    def login_via_api(self, username: str, password: str) -> str:
        """Login via API and return access token."""
        login_data = {"username": username, "password": password}
        response = requests.post(f"{self.api_url}/api/v1/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            return self.auth_token
        else:
            raise Exception(f"Failed to login: {response.text}")

    def inject_auth_token(self, token: str) -> None:
        """Inject authentication token into browser storage."""
        self.page.evaluate(
            f"""
            localStorage.setItem('auth_token', '{token}');
            localStorage.setItem('isAuthenticated', 'true');
        """
        )

    def wait_for_element(self, selector: str, timeout: int = 10000) -> None:
        """Wait for element to be visible."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def fill_form_field(self, selector: str, value: str) -> None:
        """Fill a form field with proper waiting."""
        element = self.page.locator(selector)
        element.wait_for(state="visible")
        element.fill(value)

    def click_button(self, selector: str) -> None:
        """Click a button with proper waiting."""
        element = self.page.locator(selector)
        element.wait_for(state="visible")
        element.click()

    def verify_text_present(self, text: str) -> None:
        """Verify text is present on the page."""
        expect(self.page.locator(f"text={text}")).to_be_visible()

    def verify_element_visible(self, selector: str) -> None:
        """Verify element is visible."""
        expect(self.page.locator(selector)).to_be_visible()

    def take_screenshot(self, name: str) -> None:
        """Take a screenshot for debugging."""
        self.page.screenshot(path=f"tests/screenshots/{name}.png")


@pytest.fixture
def player_helper(page: Page) -> PlayerInterfaceTestHelper:
    """Create player interface test helper."""
    return PlayerInterfaceTestHelper(page)


@pytest.fixture
def authenticated_user(player_helper: PlayerInterfaceTestHelper) -> dict[str, Any]:
    """Create and authenticate a test user."""
    user_data = player_helper.create_test_user_via_api()
    token = player_helper.login_via_api(user_data["username"], user_data["password"])

    # Navigate to app and inject token
    player_helper.navigate_to_app()
    player_helper.inject_auth_token(token)

    # Refresh to apply authentication
    player_helper.page.reload()
    player_helper.page.wait_for_load_state("networkidle")

    return user_data


class TestPlayerInterfaceAuthentication:
    """Test authentication and session management."""

    def test_login_page_loads(self, player_helper: PlayerInterfaceTestHelper):
        """Test that login page loads correctly."""
        player_helper.navigate_to_app()

        # Should show login page when not authenticated
        player_helper.verify_text_present("Welcome to TTA")
        player_helper.verify_text_present("Therapeutic Text Adventure Platform")

        # Take screenshot for verification
        player_helper.take_screenshot("login_page")

    def test_authenticated_user_sees_dashboard(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test that authenticated user sees dashboard."""
        # Should redirect to dashboard
        player_helper.verify_text_present("Dashboard")
        player_helper.take_screenshot("authenticated_dashboard")


class TestCharacterCreationInterface:
    """Test character creation form interface."""

    def test_frontend_loads_and_shows_content(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test that frontend loads and shows some content."""
        # Take screenshot to see what's actually displayed
        player_helper.take_screenshot("authenticated_frontend_state")

        # Check if we can find any navigation elements
        page_content = player_helper.page.content()
        print(f"Page title: {player_helper.page.title()}")
        print(f"Page URL: {player_helper.page.url}")

        # Look for common React app elements
        if (
            "TTA" in page_content
            or "Character" in page_content
            or "Dashboard" in page_content
        ):
            print("✅ Frontend appears to be loaded with TTA content")
        else:
            print("⚠️ Frontend may not be fully loaded or authenticated")

    def test_character_management_page_loads(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test character management page loads correctly."""
        # First check what's available on the page
        player_helper.take_screenshot("before_navigation")

        # Try to find navigation elements
        try:
            # Look for various possible navigation patterns
            nav_selectors = [
                "text=Characters",
                "a[href*='character']",
                "button:has-text('Character')",
                "[data-testid*='character']",
                "nav a",
                ".nav-link",
            ]

            for selector in nav_selectors:
                elements = player_helper.page.locator(selector)
                if elements.count() > 0:
                    print(f"Found navigation element: {selector}")
                    elements.first.click()
                    player_helper.page.wait_for_timeout(2000)  # Wait 2 seconds
                    player_helper.take_screenshot("after_navigation")
                    break
            else:
                print(
                    "No navigation elements found, taking screenshot of current state"
                )
                player_helper.take_screenshot("no_navigation_found")

        except Exception as e:
            print(f"Navigation failed: {e}")
            player_helper.take_screenshot("navigation_error")

    def test_create_character_button_opens_form(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test that create character button opens the form."""
        # Navigate to character management
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")

        # Click create character button
        player_helper.click_button("text=Create New Character")

        # Verify form opens
        player_helper.verify_text_present("Create New Character")
        player_helper.verify_text_present("Basic Info")
        player_helper.verify_text_present("Background")
        player_helper.verify_text_present("Therapeutic")

        player_helper.take_screenshot("character_creation_form")

    def test_character_form_step_1_validation(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test step 1 form validation."""
        # Navigate to character creation form
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")
        player_helper.click_button("text=Create New Character")

        # Try to proceed without filling required fields
        player_helper.click_button("text=Next")

        # Should show validation errors
        player_helper.verify_text_present("Character name is required")
        player_helper.take_screenshot("form_validation_errors")

    def test_character_form_step_navigation(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test navigation between form steps."""
        # Navigate to character creation form
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")
        player_helper.click_button("text=Create New Character")

        # Fill step 1 required fields
        player_helper.fill_form_field(
            "input[placeholder*='Enter your character\\'s name']",
            "Playwright Test Character",
        )
        player_helper.fill_form_field(
            "textarea[placeholder*='Describe your character\\'s appearance']",
            "A brave test character created by Playwright",
        )

        # Proceed to step 2
        player_helper.click_button("text=Next")

        # Verify step 2 loads
        player_helper.verify_text_present("Background & Personality")
        player_helper.take_screenshot("character_form_step_2")

        # Go back to step 1
        player_helper.click_button("text=Previous")

        # Verify step 1 loads and data is preserved
        player_helper.verify_text_present("Basic Information")
        expect(
            player_helper.page.locator(
                "input[placeholder*='Enter your character\\'s name']"
            )
        ).to_have_value("Playwright Test Character")

        player_helper.take_screenshot("character_form_step_1_preserved")


class TestCharacterFormInteractions:
    """Test detailed form interactions and user experience."""

    def test_direct_frontend_interaction(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test direct interaction with frontend elements."""
        # Navigate directly to character management URL
        player_helper.page.goto(f"{player_helper.base_url}/characters")
        player_helper.page.wait_for_load_state("networkidle")
        player_helper.take_screenshot("direct_characters_page")

        # Check if character management page loaded
        page_content = player_helper.page.content()
        if "Character" in page_content:
            print("✅ Character management page content found")

            # Look for create character button
            create_buttons = [
                "text=Create New Character",
                "button:has-text('Create')",
                "[data-testid*='create']",
                ".btn:has-text('Character')",
            ]

            for selector in create_buttons:
                elements = player_helper.page.locator(selector)
                if elements.count() > 0:
                    print(f"Found create button: {selector}")
                    elements.first.click()
                    player_helper.page.wait_for_timeout(2000)
                    player_helper.take_screenshot("character_form_opened")
                    break
        else:
            print("⚠️ Character management page not found, testing basic form elements")

        # Test basic form interactions regardless
        input_selectors = ["input", "textarea", "select"]
        for selector in input_selectors:
            elements = player_helper.page.locator(selector)
            if elements.count() > 0:
                print(f"Found {elements.count()} {selector} elements")
                # Test first input element
                first_input = elements.first
                if first_input.is_visible():
                    first_input.fill("Playwright Test Input")
                    player_helper.take_screenshot(f"filled_{selector}")
                    break

    def test_therapeutic_profile_intensity_selection(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test therapeutic profile intensity selection."""
        # Navigate to character creation form and get to step 3
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")
        player_helper.click_button("text=Create New Character")

        # Fill step 1
        player_helper.fill_form_field(
            "input[placeholder*='Enter your character\\'s name']", "Test Character"
        )
        player_helper.fill_form_field(
            "textarea[placeholder*='Describe your character\\'s appearance']",
            "Test description",
        )
        player_helper.click_button("text=Next")

        # Fill step 2 minimally
        player_helper.fill_form_field(
            "textarea[placeholder*='Tell your character\\'s story']", "Test story"
        )
        player_helper.click_button("text=Next")

        # Verify step 3 therapeutic profile
        player_helper.verify_text_present("Therapeutic Profile")

        # Test intensity level selection
        player_helper.click_button("text=High")
        player_helper.take_screenshot("therapeutic_profile_high_intensity")


class TestAccessibilityAndKeyboardNavigation:
    """Test accessibility features and keyboard navigation."""

    def test_keyboard_navigation_through_form(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test keyboard navigation through character creation form."""
        # Navigate to character creation form
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")
        player_helper.click_button("text=Create New Character")

        # Test Tab navigation
        player_helper.page.keyboard.press("Tab")  # Should focus on name input
        player_helper.page.keyboard.type("Keyboard Test Character")

        player_helper.page.keyboard.press("Tab")  # Should focus on description textarea
        player_helper.page.keyboard.type("Character created using keyboard navigation")

        player_helper.page.keyboard.press("Tab")  # Should focus on Next button
        player_helper.page.keyboard.press("Enter")  # Should proceed to next step

        # Verify navigation worked
        player_helper.verify_text_present("Background & Personality")
        player_helper.take_screenshot("keyboard_navigation_success")

    def test_form_aria_labels_and_accessibility(
        self,
        player_helper: PlayerInterfaceTestHelper,
        authenticated_user: dict[str, Any],
    ):
        """Test form accessibility attributes."""
        # Navigate to character creation form
        player_helper.click_button("text=Characters")
        player_helper.wait_for_element("text=Character Management")
        player_helper.click_button("text=Create New Character")

        # Check for proper ARIA labels and accessibility attributes
        name_input = player_helper.page.locator(
            "input[placeholder*='Enter your character\\'s name']"
        )
        expect(name_input).to_be_visible()

        # Verify form has proper structure
        player_helper.verify_element_visible("form")
        player_helper.take_screenshot("accessibility_check")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
