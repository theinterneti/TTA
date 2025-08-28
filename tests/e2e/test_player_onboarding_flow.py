"""
End-to-End Test for TTA AI Agent Orchestration System Player Onboarding Flow.

This test automates the complete player onboarding journey through the Swagger UI,
from initial registration through first therapeutic session creation.
"""

import json
import re
import time
from typing import Dict, Any

import pytest
from playwright.sync_api import Page, expect


# Test data for realistic onboarding scenario
TEST_USER_DATA = {
    "username": "alex_therapeutic_journey",
    "email": "alex.journey@example.com",
    "password": "SecureTherapy123!",
    "therapeutic_preferences": {
        "focus_areas": ["anxiety", "social_skills"],
        "intensity_preference": "moderate",
        "session_length_preference": "30-45 minutes"
    },
    "privacy_settings": {
        "data_sharing": "minimal",
        "progress_visibility": "private"
    }
}

PLAYER_PROFILE_DATA = {
    "username": "alex_therapeutic_journey",
    "email": "alex.journey@example.com",
    "therapeutic_preferences": {
        "primary_goals": ["stress_management", "confidence_building"],
        "preferred_interaction_style": "supportive",
        "comfort_with_challenge": "moderate",
        "session_frequency": "3-4 times per week"
    },
    "privacy_settings": {
        "share_progress_with_therapist": True,
        "anonymous_data_contribution": False,
        "marketing_communications": False
    }
}

CHARACTER_DATA = {
    "name": "Alex Journey",
    "appearance": {
        "age_range": "young_adult",
        "gender_identity": "non-binary",
        "physical_description": "Medium height, friendly demeanor, casual style",
        "clothing_style": "comfortable_casual",
        "distinctive_features": ["warm_smile", "expressive_eyes"]
    },
    "background": {
        "name": "Alex Journey",
        "backstory": "A college student exploring personal growth and building confidence in social situations",
        "personality_traits": ["curious", "empathetic", "sometimes_anxious", "determined"],
        "core_values": ["authenticity", "kindness", "personal_growth"],
        "fears_and_anxieties": ["public_speaking", "social_judgment"],
        "strengths_and_skills": ["good_listener", "creative_problem_solving", "artistic"],
        "life_goals": ["build_confidence", "develop_social_skills", "pursue_creative_career"]
    },
    "therapeutic_profile": {
        "primary_therapeutic_goals": ["anxiety_management", "social_confidence"],
        "therapeutic_readiness_level": 7,
        "preferred_coping_strategies": ["mindfulness", "gradual_exposure"],
        "trigger_topics": ["harsh_criticism", "public_failure"],
        "comfort_zones": ["creative_expression", "one_on_one_conversations"],
        "growth_areas": ["group_interactions", "assertiveness"]
    }
}

WORLD_CUSTOMIZATION = {
    "difficulty_level": "beginner",
    "therapeutic_intensity": "moderate",
    "narrative_style": "supportive",
    "session_length": "30_minutes",
    "narrative_pace": "relaxed",
    "interaction_frequency": "moderate",
    "challenge_level": "gradual",
    "focus_areas": ["social_confidence", "anxiety_management"],
    "avoid_topics": ["public_speaking_initially"],
    "session_length_preference": "30_minutes"
}


class TestPlayerOnboardingFlow:
    """Complete end-to-end test of the player onboarding flow."""

    def setup_method(self):
        """Setup test data for each test method."""
        self.access_token = None
        self.player_id = None
        self.character_id = None
        self.world_id = None
        self.session_id = None
        
    def test_complete_player_onboarding_flow(self, page: Page):
        """Test the complete player onboarding flow through Swagger UI."""
        
        # Step 1: Navigate to Swagger UI and verify it loads
        self._navigate_to_swagger_ui(page)
        
        # Step 2: Complete user registration
        self._register_new_user(page)
        
        # Step 3: Login and get access token
        self._login_user(page)
        
        # Step 4: Authorize in Swagger UI
        self._authorize_swagger_ui(page)
        
        # Step 5: Create player profile
        self._create_player_profile(page)
        
        # Step 6: Create character
        self._create_character(page)
        
        # Step 7: Browse and select world
        self._browse_and_select_world(page)
        
        # Step 8: Check world-character compatibility
        self._check_world_compatibility(page)
        
        # Step 9: Customize world (optional)
        self._customize_world(page)
        
        # Step 10: Create first therapeutic session
        self._create_first_session(page)
        
        # Step 11: Final validation
        self._validate_complete_onboarding(page)
        
        print("🎉 Complete player onboarding flow test PASSED!")

    def _navigate_to_swagger_ui(self, page: Page):
        """Navigate to Swagger UI and verify it loads correctly."""
        print("📍 Step 1: Navigating to Swagger UI...")
        
        page.goto("http://localhost:8080/docs")
        
        # Wait for Swagger UI to load completely
        page.wait_for_selector(".swagger-ui", timeout=10000)
        
        # Verify all main sections are visible (using exact match for section headers)
        expect(page.get_by_role("link", name="authentication", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="players", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="characters", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="worlds", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="sessions", exact=True)).to_be_visible()
        
        # Take screenshot for documentation
        page.screenshot(path="tests/screenshots/01_swagger_ui_loaded.png")
        print("✅ Swagger UI loaded successfully with all sections visible")

    def _register_new_user(self, page: Page):
        """Register a new user through the authentication section."""
        print("📍 Step 2: Registering new user...")
        
        # Navigate to authentication section
        auth_section = page.get_by_role("link", name="authentication", exact=True)
        auth_section.click()
        
        # Find and click the register endpoint
        register_endpoint = page.get_by_role("button", name="POST /api/v1/auth/register Register")
        register_endpoint.click()
        
        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").first.click()
        
        # Fill in the request body
        request_body_textarea = page.locator("textarea").first
        request_body_textarea.fill(json.dumps(TEST_USER_DATA, indent=2))
        
        # Execute the request
        page.locator("button:has-text('Execute')").first.click()
        
        # Wait for response and verify success
        page.wait_for_selector(".response-col_status", timeout=10000)
        
        # Check for successful response (201 or 200)
        response_status = page.locator(".response-col_status").first.inner_text()
        assert "20" in response_status, f"Registration failed with status: {response_status}"
        
        page.screenshot(path="tests/screenshots/02_user_registered.png")
        print("✅ User registration completed successfully")

    def _login_user(self, page: Page):
        """Login user and extract access token."""
        print("📍 Step 3: Logging in user...")

        # Find and click the login endpoint
        login_endpoint = page.get_by_role("button", name="POST /api/v1/auth/login Login")
        login_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").nth(1).click()

        # Fill in login credentials
        login_data = {
            "username": TEST_USER_DATA["username"],
            "password": TEST_USER_DATA["password"]
        }

        request_body_textarea = page.locator("textarea").nth(1)
        request_body_textarea.fill(json.dumps(login_data, indent=2))

        # Execute the request
        page.locator("button:has-text('Execute')").nth(1).click()

        # Wait for response and extract access token
        page.wait_for_selector(".response-col_status", timeout=10000)

        # Get response body and extract token
        response_body = page.locator(".response-col_description pre").first.inner_text()
        response_data = json.loads(response_body)

        assert "access_token" in response_data, "Login response missing access token"
        self.access_token = response_data["access_token"]

        page.screenshot(path="tests/screenshots/03_user_logged_in.png")
        print(f"✅ User logged in successfully, token obtained: {self.access_token[:20]}...")

    def _authorize_swagger_ui(self, page: Page):
        """Authorize Swagger UI with the Bearer token."""
        print("📍 Step 4: Authorizing Swagger UI...")

        # Click the Authorize button
        page.locator("button:has-text('Authorize')").first.click()

        # Wait for authorization modal
        page.wait_for_selector(".auth-container", timeout=5000)

        # Enter Bearer token
        token_input = page.locator("input[placeholder*='api_key']").first
        token_input.fill(f"Bearer {self.access_token}")

        # Click Authorize in modal
        page.locator("button:has-text('Authorize')").nth(1).click()

        # Close the modal
        page.locator("button:has-text('Close')").click()

        page.screenshot(path="tests/screenshots/04_swagger_authorized.png")
        print("✅ Swagger UI authorized with Bearer token")

    def _create_player_profile(self, page: Page):
        """Create a player profile."""
        print("📍 Step 5: Creating player profile...")

        # Navigate to players section
        players_section = page.get_by_role("link", name="players", exact=True)
        players_section.click()

        # Find and click the create player endpoint
        create_player_endpoint = page.get_by_role("button", name="POST /api/v1/players/ Create Player Profile")
        create_player_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Fill in player profile data
        request_body_textarea = page.locator("textarea")
        request_body_textarea.fill(json.dumps(PLAYER_PROFILE_DATA, indent=2))

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response and extract player_id
        page.wait_for_selector(".response-col_status", timeout=10000)

        response_body = page.locator(".response-col_description pre").first.inner_text()
        response_data = json.loads(response_body)

        assert "player_id" in response_data, "Player creation response missing player_id"
        self.player_id = response_data["player_id"]

        page.screenshot(path="tests/screenshots/05_player_profile_created.png")
        print(f"✅ Player profile created successfully, ID: {self.player_id}")

    def _create_character(self, page: Page):
        """Create a character for the player."""
        print("📍 Step 6: Creating character...")

        # Navigate to characters section
        characters_section = page.get_by_role("link", name="characters", exact=True)
        characters_section.click()

        # Find and click the create character endpoint
        create_character_endpoint = page.get_by_role("button", name="POST /api/v1/characters/ Create Character")
        create_character_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Fill in character data
        request_body_textarea = page.locator("textarea")
        request_body_textarea.fill(json.dumps(CHARACTER_DATA, indent=2))

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response and extract character_id
        page.wait_for_selector(".response-col_status", timeout=10000)

        response_body = page.locator(".response-col_description pre").first.inner_text()
        response_data = json.loads(response_body)

        assert "character_id" in response_data, "Character creation response missing character_id"
        self.character_id = response_data["character_id"]

        page.screenshot(path="tests/screenshots/06_character_created.png")
        print(f"✅ Character created successfully, ID: {self.character_id}")

    def _browse_and_select_world(self, page: Page):
        """Browse available worlds and select one."""
        print("📍 Step 7: Browsing and selecting world...")

        # Navigate to worlds section
        worlds_section = page.get_by_role("link", name="worlds", exact=True)
        worlds_section.click()

        # Find and click the list worlds endpoint
        list_worlds_endpoint = page.get_by_role("button", name="GET /api/v1/worlds/ List available worlds")
        list_worlds_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response and extract world_id
        page.wait_for_selector(".response-col_status", timeout=10000)

        response_body = page.locator(".response-col_description pre").first.inner_text()
        response_data = json.loads(response_body)

        # Select the first available world
        assert len(response_data) > 0, "No worlds available"
        self.world_id = response_data[0]["world_id"]

        page.screenshot(path="tests/screenshots/07_worlds_browsed.png")
        print(f"✅ World selected successfully, ID: {self.world_id}")

    def _check_world_compatibility(self, page: Page):
        """Check compatibility between world and character."""
        print("📍 Step 8: Checking world-character compatibility...")

        # Find and click the compatibility endpoint
        compatibility_endpoint = page.get_by_role("button", name="GET /api/v1/worlds/{world_id}/compatibility/{character_id} Check world-character compatibility")
        compatibility_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Fill in world_id and character_id parameters
        world_id_input = page.locator("input[placeholder='world_id']")
        world_id_input.fill(self.world_id)

        character_id_input = page.locator("input[placeholder='character_id']")
        character_id_input.fill(self.character_id)

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response
        page.wait_for_selector(".response-col_status", timeout=10000)

        page.screenshot(path="tests/screenshots/08_compatibility_checked.png")
        print("✅ World-character compatibility checked successfully")

    def _customize_world(self, page: Page):
        """Customize world parameters (optional step)."""
        print("📍 Step 9: Customizing world parameters...")

        # Find and click the customize world endpoint
        customize_endpoint = page.get_by_role("button", name="POST /api/v1/worlds/{world_id}/customize Customize world parameters")
        customize_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Fill in world_id parameter
        world_id_input = page.locator("input[placeholder='world_id']")
        world_id_input.fill(self.world_id)

        # Fill in customization data
        request_body_textarea = page.locator("textarea")
        request_body_textarea.fill(json.dumps(WORLD_CUSTOMIZATION, indent=2))

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response
        page.wait_for_selector(".response-col_status", timeout=10000)

        page.screenshot(path="tests/screenshots/09_world_customized.png")
        print("✅ World customized successfully")

    def _create_first_session(self, page: Page):
        """Create the first therapeutic session."""
        print("📍 Step 10: Creating first therapeutic session...")

        # Navigate to sessions section
        sessions_section = page.get_by_role("link", name="sessions", exact=True)
        sessions_section.click()

        # Find and click the create session endpoint
        create_session_endpoint = page.get_by_role("button", name="POST /api/v1/sessions/ Create Session")
        create_session_endpoint.click()

        # Click "Try it out" button
        page.locator("button:has-text('Try it out')").click()

        # Prepare session data
        session_data = {
            "character_id": self.character_id,
            "world_id": self.world_id,
            "therapeutic_settings": {
                "session_type": "exploration",
                "therapeutic_focus": ["anxiety_management", "social_skills"],
                "intensity_level": "moderate",
                "duration_minutes": 30,
                "ai_guidance_level": "supportive",
                "real_time_feedback": True,
                "progress_tracking": True
            }
        }

        # Fill in session data
        request_body_textarea = page.locator("textarea")
        request_body_textarea.fill(json.dumps(session_data, indent=2))

        # Execute the request
        page.locator("button:has-text('Execute')").click()

        # Wait for response and extract session_id
        page.wait_for_selector(".response-col_status", timeout=10000)

        response_body = page.locator(".response-col_description pre").first.inner_text()
        response_data = json.loads(response_body)

        assert "session_id" in response_data, "Session creation response missing session_id"
        self.session_id = response_data["session_id"]

        page.screenshot(path="tests/screenshots/10_session_created.png")
        print(f"✅ First therapeutic session created successfully, ID: {self.session_id}")

    def _validate_complete_onboarding(self, page: Page):
        """Final validation of the complete onboarding flow."""
        print("📍 Step 11: Validating complete onboarding flow...")

        # Verify all required IDs were obtained
        assert self.access_token is not None, "Access token not obtained"
        assert self.player_id is not None, "Player ID not obtained"
        assert self.character_id is not None, "Character ID not obtained"
        assert self.world_id is not None, "World ID not obtained"
        assert self.session_id is not None, "Session ID not obtained"

        # Take final screenshot
        page.screenshot(path="tests/screenshots/11_onboarding_complete.png")

        # Print summary
        print("\n🎉 COMPLETE ONBOARDING FLOW VALIDATION:")
        print(f"✅ Access Token: {self.access_token[:20]}...")
        print(f"✅ Player ID: {self.player_id}")
        print(f"✅ Character ID: {self.character_id}")
        print(f"✅ World ID: {self.world_id}")
        print(f"✅ Session ID: {self.session_id}")
        print("\n🎮 Player onboarding flow completed successfully!")
        print("   New player 'Alex Journey' is ready for therapeutic gaming experience!")
