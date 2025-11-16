#!/usr/bin/env python3
"""
TTA System Population Script

This script creates simulated user sessions to populate the TTA system with initial
world data and character archetypes, focusing on therapeutic storytelling elements
and diverse representation.

Features:
- Creates diverse test users with different therapeutic profiles
- Generates varied character archetypes with therapeutic relevance
- Establishes sessions that demonstrate therapeutic capabilities
- Focuses on representation, accessibility, and therapeutic value
- Uses the working JWT authentication system
- Ensures data persistence in Redis fallback system
"""

import time

import requests

# Configuration
BASE_URL = "http://localhost:8080"
SIMULATION_CONFIG = {
    "num_users": 8,
    "characters_per_user": 2,
    "sessions_per_character": 1,
    "delay_between_requests": 0.5,  # seconds
}


class TTASystemPopulator:
    """Populates the TTA system with diverse therapeutic content."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.users = []
        self.characters = []
        self.sessions = []
        self.worlds = []

    def run_population(self):
        """Run the complete system population process."""
        print("🚀 Starting TTA System Population")
        print("=" * 60)

        # Step 1: Verify API health
        if not self._check_api_health():
            print("❌ API is not healthy. Exiting.")
            return False

        # Step 2: Get available worlds
        self._fetch_available_worlds()

        # Step 3: Create diverse users
        self._create_diverse_users()

        # Step 4: Create character archetypes for each user
        self._create_character_archetypes()

        # Step 5: Create therapeutic sessions
        self._create_therapeutic_sessions()

        # Step 6: Generate summary report
        self._generate_summary_report()

        print("\n🎉 TTA System Population Complete!")
        return True

    def _check_api_health(self) -> bool:
        """Check if the API is healthy and accessible."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ API is healthy and accessible")
                return True
            print(f"❌ API health check failed: {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False

    def _fetch_available_worlds(self):
        """Fetch available worlds from the system."""
        print("\n🌍 Fetching available worlds...")
        try:
            # Create a temporary user to access worlds endpoint
            temp_user = self._create_temp_user_for_worlds()
            if not temp_user:
                print("⚠️ Could not create temporary user for world access")
                return

            headers = {"Authorization": f"Bearer {temp_user['token']}"}
            response = requests.get(f"{self.base_url}/api/v1/worlds/", headers=headers)

            if response.status_code == 200:
                self.worlds = response.json()
                print(f"✅ Found {len(self.worlds)} available worlds:")
                for world in self.worlds:
                    print(f"   - {world['name']}: {world['description']}")
            else:
                print(f"⚠️ Could not fetch worlds: {response.status_code}")
                # Create mock world data for testing
                self.worlds = [
                    {
                        "world_id": "world_mindfulness_garden",
                        "name": "Mindfulness Garden",
                    },
                    {
                        "world_id": "world_anxiety_sanctuary",
                        "name": "Anxiety Sanctuary",
                    },
                ]
        except Exception as e:
            print(f"⚠️ Error fetching worlds: {e}")
            self.worlds = [
                {"world_id": "world_mindfulness_garden", "name": "Mindfulness Garden"},
                {"world_id": "world_anxiety_sanctuary", "name": "Anxiety Sanctuary"},
            ]

    def _create_temp_user_for_worlds(self) -> dict | None:
        """Create a temporary user to access protected endpoints."""
        try:
            temp_user_data = {
                "username": f"temp_world_access_{int(time.time())}",
                "email": f"temp_{int(time.time())}@tta-system.com",
                "password": "TempPassword123!",
            }

            # Register user
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=temp_user_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                return None

            # Login user
            login_response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "username": temp_user_data["username"],
                    "password": temp_user_data["password"],
                },
                headers={"Content-Type": "application/json"},
            )

            if login_response.status_code == 200:
                login_data = login_response.json()
                return {"token": login_data["access_token"]}

            return None
        except Exception:
            return None

    def _create_diverse_users(self):
        """Create diverse user profiles with different therapeutic needs."""
        print(f"\n👥 Creating {SIMULATION_CONFIG['num_users']} diverse users...")

        user_profiles = self._get_diverse_user_profiles()

        for i, profile in enumerate(user_profiles[: SIMULATION_CONFIG["num_users"]]):
            try:
                print(
                    f"   Creating user {i + 1}/{SIMULATION_CONFIG['num_users']}: {profile['username']}"
                )

                # Register user
                register_response = requests.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=profile,
                    headers={"Content-Type": "application/json"},
                )

                if register_response.status_code != 200:
                    print(
                        f"   ❌ Failed to register {profile['username']}: {register_response.text}"
                    )
                    continue

                # Login user
                login_response = requests.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={
                        "username": profile["username"],
                        "password": profile["password"],
                    },
                    headers={"Content-Type": "application/json"},
                )

                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_data = {
                        "profile": profile,
                        "token": login_data["access_token"],
                        "user_info": login_data["user_info"],
                    }
                    self.users.append(user_data)
                    print(
                        f"   ✅ Successfully created and authenticated {profile['username']}"
                    )
                else:
                    print(
                        f"   ❌ Failed to login {profile['username']}: {login_response.text}"
                    )

                time.sleep(SIMULATION_CONFIG["delay_between_requests"])

            except Exception as e:
                print(f"   ❌ Error creating user {profile['username']}: {e}")

        print(f"✅ Successfully created {len(self.users)} users")

    def _get_diverse_user_profiles(self) -> list[dict]:
        """Generate diverse user profiles representing different demographics and therapeutic needs."""
        return [
            {
                "username": "alex_mindfulness_seeker",
                "email": "alex.mindful@tta-demo.com",
                "password": "MindfulPath123!",
                "therapeutic_focus": "mindfulness and stress reduction",
                "background": "Young professional dealing with work stress",
            },
            {
                "username": "maria_anxiety_warrior",
                "email": "maria.brave@tta-demo.com",
                "password": "BraveHeart123!",
                "therapeutic_focus": "anxiety management and confidence building",
                "background": "College student managing social anxiety",
            },
            {
                "username": "jordan_trauma_survivor",
                "email": "jordan.healing@tta-demo.com",
                "password": "HealingJourney123!",
                "therapeutic_focus": "trauma processing and resilience building",
                "background": "Adult survivor working on healing and growth",
            },
            {
                "username": "sam_depression_fighter",
                "email": "sam.hope@tta-demo.com",
                "password": "HopefulDays123!",
                "therapeutic_focus": "depression recovery and behavioral activation",
                "background": "Mid-career professional overcoming depression",
            },
            {
                "username": "riley_identity_explorer",
                "email": "riley.authentic@tta-demo.com",
                "password": "TrueIdentity123!",
                "therapeutic_focus": "identity exploration and self-acceptance",
                "background": "Young adult exploring gender identity and authenticity",
            },
            {
                "username": "casey_relationship_builder",
                "email": "casey.connect@tta-demo.com",
                "password": "Connection123!",
                "therapeutic_focus": "relationship skills and communication",
                "background": "Person working on healthy relationship patterns",
            },
            {
                "username": "taylor_grief_processor",
                "email": "taylor.memory@tta-demo.com",
                "password": "RememberLove123!",
                "therapeutic_focus": "grief processing and meaning-making",
                "background": "Individual processing loss and finding new purpose",
            },
            {
                "username": "avery_neurodivergent_advocate",
                "email": "avery.unique@tta-demo.com",
                "password": "UniqueStrengths123!",
                "therapeutic_focus": "neurodivergent strengths and accommodation",
                "background": "Neurodivergent adult embracing their unique perspective",
            },
        ]

    def _create_character_archetypes(self):
        """Create diverse character archetypes for each user."""
        print("\n🎭 Creating character archetypes...")

        for user_idx, user in enumerate(self.users):
            print(f"   Creating characters for {user['profile']['username']}...")
            headers = {"Authorization": f"Bearer {user['token']}"}

            # Get character archetypes for this user's therapeutic focus
            archetypes = self._get_character_archetypes_for_user(user["profile"])

            for char_idx, archetype in enumerate(
                archetypes[: SIMULATION_CONFIG["characters_per_user"]]
            ):
                try:
                    print(
                        f"      Creating character {char_idx + 1}: {archetype['name']}"
                    )

                    response = requests.post(
                        f"{self.base_url}/api/v1/characters/",
                        json=archetype,
                        headers=headers,
                    )

                    if response.status_code in [200, 201]:
                        character_data = response.json()
                        self.characters.append(
                            {
                                "user": user,
                                "character": character_data,
                                "archetype_info": archetype,
                            }
                        )
                        print(f"      ✅ Created {archetype['name']}")
                    else:
                        print(
                            f"      ❌ Failed to create {archetype['name']}: {response.status_code}"
                        )
                        if response.status_code == 422:
                            print(f"         Validation error: {response.text}")

                    time.sleep(SIMULATION_CONFIG["delay_between_requests"])

                except Exception as e:
                    print(f"      ❌ Error creating character {archetype['name']}: {e}")

        print(f"✅ Successfully created {len(self.characters)} characters")

    def _get_character_archetypes_for_user(self, user_profile: dict) -> list[dict]:
        """Generate character archetypes based on user's therapeutic focus."""
        focus = user_profile.get("therapeutic_focus", "")
        username = user_profile.get("username", "")

        # Base archetypes that can be customized
        base_archetypes = [
            {
                "name": "The Resilient Survivor",
                "appearance": {
                    "age_range": "adult",
                    "gender_identity": "non-binary",
                    "physical_description": "A person with kind eyes that reflect both wisdom and vulnerability",
                    "clothing_style": "comfortable and practical",
                    "distinctive_features": [
                        "gentle smile",
                        "expressive hands",
                        "thoughtful posture",
                    ],
                },
                "background": {
                    "name": "The Resilient Survivor",
                    "backstory": "Someone who has faced significant challenges and is learning to rebuild their life",
                    "personality_traits": [
                        "resilient",
                        "empathetic",
                        "introspective",
                        "determined",
                    ],
                    "core_values": ["authenticity", "growth", "compassion", "courage"],
                    "fears_and_anxieties": [
                        "vulnerability",
                        "trust",
                        "overwhelming emotions",
                    ],
                    "strengths_and_skills": [
                        "emotional intelligence",
                        "problem-solving",
                        "creativity",
                    ],
                    "life_goals": [
                        "healing and integration",
                        "meaningful relationships",
                        "personal growth",
                    ],
                    "relationships": {
                        "support_network": "building healthy connections"
                    },
                },
                "therapeutic_profile": {
                    "primary_concerns": [
                        "trauma recovery",
                        "emotional regulation",
                        "self-worth",
                    ],
                    "preferred_intensity": "medium",
                    "comfort_zones": [
                        "creative expression",
                        "nature",
                        "quiet reflection",
                    ],
                    "challenge_areas": [
                        "interpersonal relationships",
                        "emotional vulnerability",
                    ],
                    "coping_strategies": [
                        "mindfulness",
                        "journaling",
                        "art therapy",
                        "nature walks",
                    ],
                    "trigger_topics": [
                        "abandonment",
                        "criticism",
                        "overwhelming situations",
                    ],
                    "readiness_level": 0.7,
                    "therapeutic_approaches": [
                        "narrative_therapy",
                        "mindfulness",
                        "cognitive_behavioral_therapy",
                    ],
                },
            },
            {
                "name": "The Anxious Achiever",
                "appearance": {
                    "age_range": "adult",
                    "gender_identity": "female",
                    "physical_description": "An accomplished-looking person with intelligent eyes, sometimes tense",
                    "clothing_style": "professional but approachable",
                    "distinctive_features": [
                        "expressive eyebrows",
                        "fidgeting hands",
                        "alert posture",
                    ],
                },
                "background": {
                    "name": "The Anxious Achiever",
                    "backstory": "A high-achieving individual who struggles with perfectionism and anxiety",
                    "personality_traits": [
                        "perfectionist",
                        "intelligent",
                        "caring",
                        "driven",
                        "self-critical",
                    ],
                    "core_values": [
                        "excellence",
                        "helping others",
                        "integrity",
                        "learning",
                    ],
                    "fears_and_anxieties": [
                        "failure",
                        "disappointing others",
                        "not being good enough",
                    ],
                    "strengths_and_skills": [
                        "analytical thinking",
                        "organization",
                        "leadership",
                    ],
                    "life_goals": [
                        "work-life balance",
                        "self-acceptance",
                        "authentic relationships",
                    ],
                    "relationships": {"colleagues": "respected but distant"},
                },
                "therapeutic_profile": {
                    "primary_concerns": [
                        "anxiety management",
                        "perfectionism",
                        "work-life balance",
                    ],
                    "preferred_intensity": "medium",
                    "comfort_zones": [
                        "structured environments",
                        "clear goals",
                        "helping others",
                    ],
                    "challenge_areas": ["uncertainty", "relaxation", "self-compassion"],
                    "coping_strategies": [
                        "planning",
                        "exercise",
                        "breathing techniques",
                    ],
                    "trigger_topics": ["criticism", "failure", "uncertainty"],
                    "readiness_level": 0.6,
                    "therapeutic_approaches": [
                        "cognitive_behavioral_therapy",
                        "mindfulness",
                    ],
                },
            },
        ]

        # Customize archetypes based on user's therapeutic focus
        customized_archetypes = []
        for archetype in base_archetypes:
            customized = self._customize_archetype_for_focus(archetype, focus, username)
            customized_archetypes.append(customized)

        return customized_archetypes

    def _customize_archetype_for_focus(
        self, archetype: dict, focus: str, username: str
    ) -> dict:
        """Customize character archetype based on user's therapeutic focus."""
        # Make a deep copy to avoid modifying the original
        import copy

        customized = copy.deepcopy(archetype)

        # Add user-specific customizations based on therapeutic focus
        if "mindfulness" in focus:
            customized["therapeutic_profile"]["therapeutic_approaches"].append(
                "mindfulness"
            )
            customized["therapeutic_profile"]["coping_strategies"].extend(
                ["meditation", "body awareness"]
            )
            customized["background"]["personality_traits"].append("contemplative")

        if "anxiety" in focus:
            customized["therapeutic_profile"]["primary_concerns"].append(
                "anxiety management"
            )
            customized["therapeutic_profile"]["coping_strategies"].extend(
                ["grounding techniques"]
            )

        if "trauma" in focus:
            customized["therapeutic_profile"]["therapeutic_approaches"].append(
                "narrative_therapy"
            )
            customized["therapeutic_profile"]["primary_concerns"].append(
                "trauma processing"
            )

        if "depression" in focus:
            customized["therapeutic_profile"]["therapeutic_approaches"].append(
                "behavioral_activation"
            )
            customized["therapeutic_profile"]["primary_concerns"].append(
                "mood regulation"
            )

        # Add unique identifier to character name
        user_suffix = username.split("_")[0] if "_" in username else username[:4]
        customized["name"] = f"{customized['name']} ({user_suffix})"
        customized["background"]["name"] = customized["name"]

        return customized

    def _create_therapeutic_sessions(self):
        """Create therapeutic sessions pairing characters with appropriate worlds."""
        print("\n🎯 Creating therapeutic sessions...")

        if not self.worlds:
            print("⚠️ No worlds available for session creation")
            return

        for char_data in self.characters:
            user = char_data["user"]
            character = char_data["character"]

            print(
                f"   Creating session for {character.get('name', 'Unknown Character')}..."
            )

            try:
                # Select appropriate world based on character's therapeutic profile
                selected_world = self._select_world_for_character(
                    character, char_data["archetype_info"]
                )

                if not selected_world:
                    print(
                        f"      ⚠️ No suitable world found for {character.get('name')}"
                    )
                    continue

                # Create session data
                session_data = {
                    "character_id": character.get("character_id"),
                    "world_id": selected_world["world_id"],
                    "therapeutic_settings": {
                        "intensity_level": "medium",
                        "preferred_approaches": char_data["archetype_info"][
                            "therapeutic_profile"
                        ]["therapeutic_approaches"],
                        "session_goals": ["personal_growth", "skill_development"],
                        "safety_monitoring": True,
                        "focus_areas": char_data["archetype_info"][
                            "therapeutic_profile"
                        ]["comfort_zones"],
                        "avoid_topics": char_data["archetype_info"][
                            "therapeutic_profile"
                        ]["trigger_topics"],
                    },
                }

                headers = {"Authorization": f"Bearer {user['token']}"}
                response = requests.post(
                    f"{self.base_url}/api/v1/sessions/",
                    json=session_data,
                    headers=headers,
                )

                if response.status_code in [200, 201]:
                    session_result = response.json()
                    self.sessions.append(
                        {
                            "user": user,
                            "character": character,
                            "world": selected_world,
                            "session": session_result,
                        }
                    )
                    print(f"      ✅ Created session in {selected_world['name']}")
                else:
                    print(f"      ❌ Failed to create session: {response.status_code}")
                    if response.status_code == 422:
                        print(f"         Validation error: {response.text}")

                time.sleep(SIMULATION_CONFIG["delay_between_requests"])

            except Exception as e:
                print(f"      ❌ Error creating session: {e}")

        print(f"✅ Successfully created {len(self.sessions)} therapeutic sessions")

    def _select_world_for_character(
        self, character: dict, archetype_info: dict
    ) -> dict | None:
        """Select the most appropriate world for a character based on therapeutic profile."""
        if not self.worlds:
            return None

        # Get character's therapeutic focus
        therapeutic_approaches = archetype_info["therapeutic_profile"][
            "therapeutic_approaches"
        ]
        primary_concerns = archetype_info["therapeutic_profile"]["primary_concerns"]

        # Simple world selection logic based on therapeutic needs
        for world in self.worlds:
            world_name = world.get("name", "").lower()

            # Match mindfulness-focused characters with mindfulness worlds
            if "mindfulness" in therapeutic_approaches and "mindfulness" in world_name:
                return world

            # Match anxiety-focused characters with anxiety/sanctuary worlds
            if "anxiety management" in primary_concerns and (
                "anxiety" in world_name or "sanctuary" in world_name
            ):
                return world

        # Default to first available world if no specific match
        return self.worlds[0] if self.worlds else None

    def _generate_summary_report(self):
        """Generate a comprehensive summary report of the population process."""
        print("\n📊 POPULATION SUMMARY REPORT")
        print("=" * 60)

        print(f"👥 Users Created: {len(self.users)}")
        if self.users:
            print("   User Profiles:")
            for user in self.users:
                profile = user["profile"]
                print(f"   - {profile['username']}: {profile['therapeutic_focus']}")

        print(f"\n🎭 Characters Created: {len(self.characters)}")
        if self.characters:
            print("   Character Archetypes:")
            for char_data in self.characters:
                character = char_data["character"]
                archetype = char_data["archetype_info"]
                user_name = char_data["user"]["profile"]["username"]
                print(f"   - {character.get('name', 'Unknown')} (User: {user_name})")
                print(
                    f"     Therapeutic Focus: {', '.join(archetype['therapeutic_profile']['primary_concerns'])}"
                )

        print(f"\n🎯 Sessions Created: {len(self.sessions)}")
        if self.sessions:
            print("   Active Sessions:")
            for session_data in self.sessions:
                character = session_data["character"]
                world = session_data["world"]
                user_name = session_data["user"]["profile"]["username"]
                print(
                    f"   - {character.get('name', 'Unknown')} in {world['name']} (User: {user_name})"
                )

        print(f"\n🌍 Available Worlds: {len(self.worlds)}")
        if self.worlds:
            print("   World Environments:")
            for world in self.worlds:
                print(
                    f"   - {world['name']}: {world.get('description', 'No description')}"
                )

        # Calculate success metrics
        total_expected_characters = (
            len(self.users) * SIMULATION_CONFIG["characters_per_user"]
        )
        character_success_rate = (
            (len(self.characters) / total_expected_characters * 100)
            if total_expected_characters > 0
            else 0
        )

        total_expected_sessions = (
            len(self.characters) * SIMULATION_CONFIG["sessions_per_character"]
        )
        session_success_rate = (
            (len(self.sessions) / total_expected_sessions * 100)
            if total_expected_sessions > 0
            else 0
        )

        print("\n📈 Success Metrics:")
        print(
            f"   User Creation: {len(self.users)}/{SIMULATION_CONFIG['num_users']} ({len(self.users) / SIMULATION_CONFIG['num_users'] * 100:.1f}%)"
        )
        print(
            f"   Character Creation: {len(self.characters)}/{total_expected_characters} ({character_success_rate:.1f}%)"
        )
        print(
            f"   Session Creation: {len(self.sessions)}/{total_expected_sessions} ({session_success_rate:.1f}%)"
        )

        print("\n🎯 Therapeutic Diversity:")
        therapeutic_focuses = [
            user["profile"]["therapeutic_focus"] for user in self.users
        ]
        unique_focuses = set(therapeutic_focuses)
        print(f"   Unique Therapeutic Focuses: {len(unique_focuses)}")
        for focus in unique_focuses:
            count = therapeutic_focuses.count(focus)
            print(f"   - {focus}: {count} user(s)")

        print("\n✨ System Readiness:")
        if len(self.users) > 0 and len(self.characters) > 0:
            print("   ✅ System populated with diverse users and characters")
            print("   ✅ Ready for therapeutic storytelling demonstrations")
            print("   ✅ Multiple therapeutic approaches represented")
            print("   ✅ Diverse character archetypes available")

            if len(self.sessions) > 0:
                print("   ✅ Active sessions created for testing")
            else:
                print("   ⚠️ No active sessions created")
        else:
            print("   ❌ System population incomplete")
            print("   ❌ Manual intervention may be required")


# Main execution
if __name__ == "__main__":
    populator = TTASystemPopulator()
    success = populator.run_population()

    if success:
        print(
            "\n🚀 TTA System is now populated and ready for therapeutic storytelling!"
        )
        print("\nNext Steps:")
        print("1. Test the frontend interface with the created users")
        print("2. Explore character-world compatibility")
        print("3. Begin therapeutic storytelling sessions")
        print("4. Monitor system performance and user engagement")
    else:
        print(
            "\n❌ Population process encountered issues. Check the logs above for details."
        )
