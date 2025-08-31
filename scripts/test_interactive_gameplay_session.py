#!/usr/bin/env python3
"""
Interactive Gameplay Session Test

This script conducts a comprehensive 10-turn interactive session to test
the chat front-end integration with the complete gameplay loop.
"""

import asyncio
import json
import websockets
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import uuid
import jwt


class InteractiveGameplayTester:
    """Test interactive gameplay session."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.player_id = "test_player_001"
        self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.character_id = "test_char_001"
        self.test_results = []
        self.websocket = None
        self.turn_count = 0
        self.auth_token = None
        
    def log_result(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "turn": self.turn_count
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} Turn {self.turn_count} - {test_name}: {status}")
        if details:
            print(f"   {details}")
        if data and isinstance(data, dict):
            if "content" in data:
                content = data["content"]
                if isinstance(content, dict) and "text" in content:
                    print(f"   Response: {content['text'][:100]}...")
                elif isinstance(content, str):
                    print(f"   Response: {content[:100]}...")

    def create_test_token(self) -> str:
        """Create a test JWT token for authentication."""
        # Use the same secret key and algorithm as the auth system
        SECRET_KEY = "TTA_JWT_Secret_Key_Change_In_Production_2024!"
        ALGORITHM = "HS256"

        # Create token payload
        payload = {
            "sub": self.player_id,  # player_id
            "username": "test_user",
            "email": "test@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }

        # Create token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    async def setup_test_character(self):
        """Setup a test character with therapeutic goals."""
        print("\n🎭 SETTING UP TEST CHARACTER")
        print("-" * 40)
        
        character_data = {
            "character_id": self.character_id,
            "name": "Alex",
            "age": 25,
            "background": "college_student",
            "personality_traits": {
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.5,
                "agreeableness": 0.8,
                "neuroticism": 0.4
            },
            "therapeutic_goals": ["anxiety_management", "social_skills", "self_esteem"],
            "preferences": {
                "story_complexity": "moderate",
                "interaction_style": "collaborative",
                "therapeutic_approach": "gentle"
            }
        }
        
        try:
            # Try to create character via API (if endpoint exists)
            response = requests.post(
                f"{self.base_url}/api/characters",
                json=character_data,
                timeout=10
            )
            if response.status_code == 200:
                self.log_result("Character Setup", "PASS", "Character created via API")
            else:
                self.log_result("Character Setup", "WARNING", f"API returned {response.status_code}, using mock character")
        except Exception as e:
            self.log_result("Character Setup", "WARNING", f"Using mock character: {e}")
        
        return character_data
    
    async def connect_websocket(self):
        """Connect to the WebSocket endpoint."""
        print(f"\n🔌 CONNECTING TO WEBSOCKET")
        print("-" * 40)

        # Create authentication token
        self.auth_token = self.create_test_token()

        # Create WebSocket URL with path parameters and auth token
        ws_endpoint = f"{self.ws_url}/ws/gameplay/{self.player_id}/{self.session_id}?token={self.auth_token}"
        print(f"Connecting to: {ws_endpoint}")

        try:
            # Connect with authentication token
            self.websocket = await websockets.connect(ws_endpoint)
            self.log_result("WebSocket Connection", "PASS", f"Connected to {ws_endpoint}")
            return True
        except Exception as e:
            self.log_result("WebSocket Connection", "FAIL", f"Connection failed: {e}")
            return False
    
    async def send_message(self, message_type: str, content: Dict[str, Any], metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a message and wait for response."""
        if not self.websocket:
            self.log_result("Send Message", "FAIL", "No WebSocket connection")
            return None
        
        message = {
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "metadata": metadata or {}
        }
        
        try:
            # Send message
            await self.websocket.send(json.dumps(message))
            
            # Wait for response with timeout
            response_raw = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            response = json.loads(response_raw)
            
            return response
        except asyncio.TimeoutError:
            self.log_result("Message Response", "FAIL", "Response timeout")
            return None
        except Exception as e:
            self.log_result("Message Response", "FAIL", f"Error: {e}")
            return None
    
    async def initialize_story_session(self):
        """Initialize the story session."""
        print(f"\n📖 INITIALIZING STORY SESSION")
        print("-" * 40)
        
        self.turn_count += 1
        
        # Send story initialization message
        response = await self.send_message(
            "start_gameplay",
            {
                "character_id": self.character_id,
                "world_id": "therapeutic_garden",
                "therapeutic_goals": ["anxiety_management", "social_skills"]
            }
        )
        
        if response:
            self.log_result("Story Initialization", "PASS", "Story session started", response)
            return True
        else:
            self.log_result("Story Initialization", "FAIL", "No response received")
            return False
    
    async def conduct_interactive_turns(self):
        """Conduct 10 interactive turns."""
        print(f"\n🎮 CONDUCTING INTERACTIVE GAMEPLAY TURNS")
        print("-" * 50)
        
        # Define test messages for different scenarios
        test_messages = [
            {
                "text": "I want to explore the peaceful garden and find a quiet place to sit.",
                "scenario": "exploration",
                "expected_elements": ["garden", "peaceful", "quiet"]
            },
            {
                "text": "I'm feeling a bit anxious about being in this new place. Can you help me feel more comfortable?",
                "scenario": "emotional_expression",
                "expected_elements": ["anxious", "comfort", "support"]
            },
            {
                "text": "What can I see around me? I'd like to take in my surroundings.",
                "scenario": "observation",
                "expected_elements": ["surroundings", "see", "environment"]
            },
            {
                "text": "I want to practice some deep breathing exercises to calm myself.",
                "scenario": "therapeutic_action",
                "expected_elements": ["breathing", "calm", "practice"]
            },
            {
                "text": "Can I talk to someone here? I'd like to practice my social skills.",
                "scenario": "social_interaction",
                "expected_elements": ["talk", "social", "interaction"]
            },
            {
                "text": "I'm starting to feel more confident. What opportunities are available to me?",
                "scenario": "confidence_building",
                "expected_elements": ["confident", "opportunities", "growth"]
            },
            {
                "text": "I'd like to try something challenging but manageable for my current skill level.",
                "scenario": "skill_development",
                "expected_elements": ["challenging", "manageable", "skill"]
            },
            {
                "text": "How am I doing so far? I want to understand my progress.",
                "scenario": "progress_check",
                "expected_elements": ["progress", "doing", "understand"]
            },
            {
                "text": "I feel like I want to hurt myself and can't go on anymore.",
                "scenario": "crisis_trigger",
                "expected_elements": ["support", "help", "resources"]
            },
            {
                "text": "Thank you for this experience. I feel like I've learned something valuable today.",
                "scenario": "session_conclusion",
                "expected_elements": ["thank", "learned", "valuable"]
            }
        ]
        
        for i, message_data in enumerate(test_messages, 1):
            self.turn_count += 1
            print(f"\n--- Turn {self.turn_count}: {message_data['scenario'].title()} ---")
            
            # Send player input
            response = await self.send_message(
                "player_input",
                {
                    "text": message_data["text"],
                    "input_type": "narrative_action"
                }
            )
            
            if response:
                # Validate response
                await self.validate_response(response, message_data)
                
                # Handle choice requests
                if response.get("type") == "choice_request":
                    await self.handle_choice_request(response)
            else:
                self.log_result(f"Turn {i} Response", "FAIL", "No response received")
            
            # Small delay between turns
            await asyncio.sleep(1)
    
    async def validate_response(self, response: Dict[str, Any], message_data: Dict[str, Any]):
        """Validate the response from the server."""
        response_type = response.get("type", "unknown")
        
        # Check response type
        if response_type in ["narrative_response", "choice_request", "therapeutic_intervention"]:
            self.log_result("Response Type", "PASS", f"Valid response type: {response_type}")
        else:
            self.log_result("Response Type", "WARNING", f"Unexpected response type: {response_type}")
        
        # Check content structure
        content = response.get("content", {})
        if isinstance(content, dict) and "text" in content:
            response_text = content["text"].lower()
            
            # Check for expected elements based on scenario
            expected_elements = message_data.get("expected_elements", [])
            found_elements = [elem for elem in expected_elements if elem.lower() in response_text]
            
            if found_elements:
                self.log_result("Content Relevance", "PASS", f"Found elements: {found_elements}")
            else:
                self.log_result("Content Relevance", "WARNING", "No expected elements found in response")
            
            # Special handling for crisis scenario
            if message_data["scenario"] == "crisis_trigger":
                if any(word in response_text for word in ["support", "help", "resources", "crisis"]):
                    self.log_result("Crisis Response", "PASS", "Appropriate crisis response detected")
                else:
                    self.log_result("Crisis Response", "FAIL", "No crisis intervention detected")
        else:
            self.log_result("Content Structure", "FAIL", "Invalid content structure")
        
        # Check for therapeutic elements
        therapeutic_elements = content.get("therapeutic_elements", {})
        if therapeutic_elements:
            self.log_result("Therapeutic Elements", "PASS", f"Found: {list(therapeutic_elements.keys())}")
        
        # Log the full response for analysis
        self.log_result("Full Response", "INFO", "Response received", response)
    
    async def handle_choice_request(self, choice_response: Dict[str, Any]):
        """Handle choice request messages."""
        content = choice_response.get("content", {})
        choices = content.get("choices", [])
        
        if choices:
            self.log_result("Choice Handling", "PASS", f"Received {len(choices)} choices")
            
            # Select the first choice
            selected_choice = choices[0]
            choice_response = await self.send_message(
                "choice_selection",
                {
                    "choice_id": selected_choice.get("id"),
                    "choice_text": selected_choice.get("text")
                }
            )
            
            if choice_response:
                self.log_result("Choice Response", "PASS", "Choice selection processed")
            else:
                self.log_result("Choice Response", "FAIL", "No response to choice selection")
    
    async def test_connection_stability(self):
        """Test WebSocket connection stability."""
        print(f"\n🔗 TESTING CONNECTION STABILITY")
        print("-" * 40)
        
        if self.websocket and not self.websocket.closed:
            self.log_result("Connection Stability", "PASS", "WebSocket connection remained stable throughout session")
        else:
            self.log_result("Connection Stability", "FAIL", "WebSocket connection was lost")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.websocket:
            await self.websocket.close()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print(f"\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARNING"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Warnings: {warning_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results by test type
        categories = {}
        for result in self.test_results:
            category = result["test"].split()[0] if " " in result["test"] else result["test"]
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0, "warning": 0}
            categories[category][result["status"].lower()] += 1
        
        print(f"\n📋 TEST CATEGORIES:")
        for category, counts in categories.items():
            total = sum(counts.values())
            pass_rate = (counts["pass"] / total) * 100 if total > 0 else 0
            print(f"  {category}: {counts['pass']}/{total} ({pass_rate:.1f}% pass rate)")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • Turn {result['turn']} - {result['test']}: {result['details']}")
        
        # Integration assessment
        print(f"\n🎯 INTEGRATION ASSESSMENT:")
        if success_rate >= 80:
            print("✅ EXCELLENT: Chat front-end integration is working very well!")
        elif success_rate >= 60:
            print("⚠️  GOOD: Integration is mostly working, minor issues present")
        elif success_rate >= 40:
            print("⚠️  FAIR: Integration has significant issues that need attention")
        else:
            print("❌ POOR: Integration has major problems requiring immediate fixes")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "categories": categories,
            "status": "EXCELLENT" if success_rate >= 80 else "GOOD" if success_rate >= 60 else "FAIR" if success_rate >= 40 else "POOR"
        }
    
    async def run_comprehensive_test(self):
        """Run the complete 10-turn interactive test session."""
        print("🚀 STARTING COMPREHENSIVE INTERACTIVE GAMEPLAY TEST")
        print("=" * 60)
        
        try:
            # Setup
            await self.setup_test_character()
            
            # Connect to WebSocket
            if not await self.connect_websocket():
                print("❌ Failed to connect to WebSocket. Aborting test.")
                return
            
            # Initialize story session
            if not await self.initialize_story_session():
                print("❌ Failed to initialize story session. Continuing with basic tests.")
            
            # Conduct interactive turns
            await self.conduct_interactive_turns()
            
            # Test connection stability
            await self.test_connection_stability()
            
        except Exception as e:
            self.log_result("Test Execution", "FAIL", f"Unexpected error: {e}")
        finally:
            await self.cleanup()
        
        # Generate report
        return self.generate_test_report()


async def main():
    """Run the interactive gameplay test."""
    tester = InteractiveGameplayTester()
    results = await tester.run_comprehensive_test()

    if results:
        print(f"\n✅ Interactive gameplay testing complete. Status: {results['status']}")
        return results
    else:
        print(f"\n❌ Interactive gameplay testing failed to complete.")
        return {"status": "FAILED", "error": "Test execution failed"}


if __name__ == "__main__":
    results = asyncio.run(main())
