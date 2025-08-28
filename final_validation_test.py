#!/usr/bin/env python3
"""
Final TTA Therapeutic Gaming Live Database Validation Test
This script executes the complete 10-turn validation with fixed authentication.
"""

import requests
import json
import time
from datetime import datetime
import uuid

# API Configuration
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1"

class FinalValidationTest:
    def __init__(self):
        self.session = requests.Session()
        self.user_data = None
        self.auth_token = None
        self.character_id = None
        self.world_id = None
        self.session_id = None
        self.results = []
        self.unique_id = str(uuid.uuid4())[:8]

    def log_result(self, turn, description, success, response_data=None, error=None):
        """Log the result of each validation turn."""
        result = {
            "turn": turn,
            "description": description,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error": str(error) if error else None
        }
        self.results.append(result)
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"Turn {turn}: {description} - {status}")
        if error:
            print(f"  Error: {error}")

    def turn_1_register_user(self):
        """Turn 1: Register new user account with therapeutic preferences."""
        try:
            user_data = {
                "username": f"validation_user_{self.unique_id}",
                "email": f"validation_{self.unique_id}@therapeutic.example",
                "password": "SecureValidationPassword2024!",
                "therapeutic_preferences": {
                    "focus_areas": ["anxiety", "social_skills"],
                    "intensity_preference": "moderate",
                    "session_length_preference": "30-45 minutes",
                    "primary_goals": ["stress_management", "confidence_building"],
                    "comfort_with_challenge": "moderate"
                },
                "privacy_settings": {
                    "data_sharing": "minimal",
                    "progress_visibility": "private",
                    "share_progress_with_therapist": True
                }
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code in [200, 201]:
                self.user_data = response.json()
                self.log_result(1, "User Registration", True, self.user_data)
                return True
            else:
                self.log_result(1, "User Registration", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(1, "User Registration", False, error=e)
            return False

    def turn_2_login_user(self):
        """Turn 2: Login and verify JWT token receipt."""
        try:
            login_data = {
                "username": f"validation_user_{self.unique_id}",
                "password": "SecureValidationPassword2024!"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                self.auth_token = auth_response.get("access_token")
                
                if self.auth_token:
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result(2, "User Login & JWT Token", True, {"token_received": True, "user_info": auth_response.get("user_info")})
                    return True
                else:
                    self.log_result(2, "User Login & JWT Token", False, auth_response, "No access token in response")
                    return False
            else:
                self.log_result(2, "User Login & JWT Token", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(2, "User Login & JWT Token", False, error=e)
            return False

    def turn_3_create_character(self):
        """Turn 3: Create detailed therapeutic character with correct validation."""
        try:
            character_data = {
                "name": "Alex Journey",
                "appearance": {
                    "age_range": "adult",  # Fixed: use valid age range
                    "gender_identity": "non-binary",
                    "physical_description": "Thoughtful individual with expressive eyes",
                    "clothing_style": "casual_comfortable",
                    "distinctive_features": ["expressive_eyes", "calm_presence"]
                },
                "background": {
                    "name": "Alex Journey",
                    "backstory": "Graduate student working through anxiety while helping others",
                    "personality_traits": ["introspective", "empathetic", "curious"],
                    "core_values": ["authenticity", "personal_growth", "helping_others"],
                    "fears_and_anxieties": ["social_judgment", "public_speaking"],
                    "strengths_and_skills": ["active_listening", "emotional_intelligence"],
                    "life_goals": ["overcome_social_anxiety", "help_others_heal"]
                },
                "therapeutic_profile": {
                    "primary_therapeutic_goals": ["anxiety_management", "social_confidence"],
                    "therapeutic_readiness_level": 7,
                    "preferred_coping_strategies": ["mindfulness", "cognitive_reframing"],
                    "trigger_topics": ["harsh_criticism", "public_failure"],
                    "comfort_zones": ["one_on_one_conversations", "helping_others"],
                    "growth_areas": ["group_interactions", "assertiveness"],
                    "therapeutic_approaches": ["CBT", "mindfulness"]  # Added required field
                }
            }
            
            response = self.session.post(f"{API_BASE}/characters/", json=character_data)
            
            if response.status_code in [200, 201]:
                character_response = response.json()
                self.character_id = character_response.get("character_id") or character_response.get("id")
                self.log_result(3, "Character Creation", True, character_response)
                return True
            else:
                self.log_result(3, "Character Creation", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(3, "Character Creation", False, error=e)
            return False

    def turn_4_browse_worlds(self):
        """Turn 4: Browse available therapeutic worlds."""
        try:
            response = self.session.get(f"{API_BASE}/worlds/")
            
            if response.status_code == 200:
                worlds_response = response.json()
                worlds = worlds_response if isinstance(worlds_response, list) else worlds_response.get("worlds", [])
                
                # Select first available world
                if worlds:
                    self.world_id = worlds[0].get("world_id") or worlds[0].get("id")
                
                self.log_result(4, "Browse Therapeutic Worlds", True, {"worlds_count": len(worlds), "selected_world": self.world_id})
                return True
            else:
                self.log_result(4, "Browse Therapeutic Worlds", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(4, "Browse Therapeutic Worlds", False, error=e)
            return False

    def turn_5_check_compatibility(self):
        """Turn 5: Check world-character compatibility."""
        if not self.world_id or not self.character_id:
            self.log_result(5, "World-Character Compatibility", False, error="Missing world_id or character_id")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/worlds/{self.world_id}/compatibility/{self.character_id}")
            
            if response.status_code == 200:
                compatibility_data = response.json()
                self.log_result(5, "World-Character Compatibility", True, compatibility_data)
                return True
            else:
                self.log_result(5, "World-Character Compatibility", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(5, "World-Character Compatibility", False, error=e)
            return False

    def turn_6_customize_world(self):
        """Turn 6: Customize world parameters for anxiety management."""
        if not self.world_id:
            self.log_result(6, "World Customization", False, error="Missing world_id")
            return False
            
        try:
            customization_data = {
                "parameters": {
                    "session_length": "30_minutes",
                    "guidance_level": "supportive",
                    "challenge_intensity": "low",
                    "interaction_frequency": "moderate"
                },
                "therapeutic_focus": ["anxiety_management", "stress_reduction"],
                "customization_notes": "Configured for anxiety management with supportive guidance"
            }
            
            response = self.session.post(f"{API_BASE}/worlds/{self.world_id}/customize", json=customization_data)
            
            if response.status_code in [200, 201]:
                customization_response = response.json()
                self.log_result(6, "World Customization", True, customization_response)
                return True
            else:
                self.log_result(6, "World Customization", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(6, "World Customization", False, error=e)
            return False

    def turn_7_create_session(self):
        """Turn 7: Create therapeutic session."""
        if not self.character_id or not self.world_id:
            self.log_result(7, "Session Creation", False, error="Missing character_id or world_id")
            return False
            
        try:
            session_data = {
                "character_id": self.character_id,
                "world_id": self.world_id,
                "therapeutic_settings": {
                    "intensity_level": "moderate",
                    "preferred_approaches": ["CBT", "mindfulness"],
                    "session_goals": ["anxiety_management", "social_confidence"],
                    "safety_monitoring": True
                }
            }
            
            response = self.session.post(f"{API_BASE}/sessions/", json=session_data)
            
            if response.status_code in [200, 201]:
                session_response = response.json()
                self.session_id = session_response.get("session_id") or session_response.get("id")
                self.log_result(7, "Session Creation", True, session_response)
                return True
            else:
                self.log_result(7, "Session Creation", False, response.json(), f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(7, "Session Creation", False, error=e)
            return False

    def turn_8_update_progress(self):
        """Turn 8: Update session progress."""
        if not self.session_id:
            self.log_result(8, "Session Progress Update", False, error="Missing session_id")
            return False

        try:
            progress_data = {
                "therapeutic_progress": {
                    "anxiety_level_reduction": 0.3,
                    "confidence_increase": 0.25,
                    "coping_skills_practiced": ["deep_breathing", "cognitive_reframing"],
                    "milestones_achieved": ["first_social_interaction", "anxiety_management_technique"]
                },
                "session_metrics": {
                    "engagement_level": 0.85,
                    "completion_percentage": 0.75,
                    "therapeutic_goals_progress": {
                        "anxiety_management": 0.4,
                        "social_confidence": 0.3
                    }
                },
                "notes": "Significant progress in anxiety management techniques"
            }

            response = self.session.put(f"{API_BASE}/sessions/{self.session_id}/progress", json=progress_data)

            if response.status_code == 200:
                progress_response = response.json()
                self.log_result(8, "Session Progress Update", True, progress_response)
                return True
            else:
                self.log_result(8, "Session Progress Update", False, response.json(), f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_result(8, "Session Progress Update", False, error=e)
            return False

    def turn_9_pause_resume_session(self):
        """Turn 9: Test session pause and resume."""
        if not self.session_id:
            self.log_result(9, "Session Pause/Resume", False, error="Missing session_id")
            return False

        try:
            # Pause session
            pause_response = self.session.post(f"{API_BASE}/sessions/{self.session_id}/pause")

            if pause_response.status_code != 200:
                self.log_result(9, "Session Pause/Resume", False, pause_response.json(), f"Pause failed: HTTP {pause_response.status_code}")
                return False

            # Wait briefly
            time.sleep(1)

            # Resume session
            resume_response = self.session.post(f"{API_BASE}/sessions/{self.session_id}/resume")

            if resume_response.status_code == 200:
                resume_data = resume_response.json()
                self.log_result(9, "Session Pause/Resume", True, {"pause_success": True, "resume_data": resume_data})
                return True
            else:
                self.log_result(9, "Session Pause/Resume", False, resume_response.json(), f"Resume failed: HTTP {resume_response.status_code}")
                return False

        except Exception as e:
            self.log_result(9, "Session Pause/Resume", False, error=e)
            return False

    def turn_10_export_character(self):
        """Turn 10: Export character data."""
        if not self.character_id:
            self.log_result(10, "Character Data Export", False, error="Missing character_id")
            return False

        try:
            response = self.session.get(f"{API_BASE}/characters/{self.character_id}/export")

            if response.status_code == 200:
                export_data = response.json()
                # Verify the export contains the complete journey
                has_character_data = "character" in export_data or "name" in export_data
                has_session_data = "sessions" in export_data or "therapeutic_progress" in export_data

                self.log_result(10, "Character Data Export", True, {
                    "export_size": len(str(export_data)),
                    "has_character_data": has_character_data,
                    "has_session_data": has_session_data,
                    "complete_journey": has_character_data and has_session_data
                })
                return True
            else:
                self.log_result(10, "Character Data Export", False, response.json(), f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_result(10, "Character Data Export", False, error=e)
            return False

    def run_validation(self):
        """Execute the complete 10-turn validation sequence."""
        print("🎮 Starting TTA Therapeutic Gaming Live Database Validation")
        print("=" * 60)

        # Execute all 10 turns
        turns = [
            self.turn_1_register_user,
            self.turn_2_login_user,
            self.turn_3_create_character,
            self.turn_4_browse_worlds,
            self.turn_5_check_compatibility,
            self.turn_6_customize_world,
            self.turn_7_create_session,
            self.turn_8_update_progress,
            self.turn_9_pause_resume_session,
            self.turn_10_export_character,
        ]

        success_count = 0
        for turn_func in turns:
            if turn_func():
                success_count += 1

        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 Validation Summary: {success_count}/10 turns completed successfully")

        # Check service health
        try:
            health_response = self.session.get(f"{API_BASE}/services/health", headers={})
            if health_response.status_code == 200:
                health_data = health_response.json()
                using_mocks = health_data.get("using_mocks", True)
                print(f"📊 Database Status: {'Mock Services' if using_mocks else 'Live Databases'}")
        except:
            print("📊 Database Status: Unable to determine")

        return self.results

if __name__ == "__main__":
    validator = FinalValidationTest()
    results = validator.run_validation()
    
    # Save results to file
    with open("final_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to final_validation_results.json")
