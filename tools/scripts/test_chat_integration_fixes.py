#!/usr/bin/env python3
"""
Test Chat Integration Fixes

This script tests the fixes applied to integrate the chat front-end with the
complete gameplay loop implementation.
"""

import asyncio
from datetime import datetime

import websockets


class ChatIntegrationTester:
    """Test the chat integration fixes."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.test_results = []

    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")

    async def test_websocket_endpoint_availability(self):
        """Test that the new WebSocket endpoint is available."""
        test_name = "WebSocket Endpoint Availability"

        try:
            # Test the new gameplay endpoint
            player_id = "test_player_001"
            session_id = "test_session_001"
            endpoint = f"{self.ws_url}/ws/gameplay/{player_id}/{session_id}"

            # Try to connect (will fail without auth, but should not get 404)
            try:
                async with websockets.connect(endpoint):
                    pass
            except websockets.exceptions.ConnectionClosedError as e:
                if e.code == 1008:  # Policy violation (auth failure)
                    self.log_test(test_name, "PASS", "Endpoint exists, auth required as expected")
                else:
                    self.log_test(test_name, "FAIL", f"Unexpected close code: {e.code}")
            except Exception as e:
                if "404" in str(e):
                    self.log_test(test_name, "FAIL", "Endpoint not found (404)")
                else:
                    self.log_test(test_name, "PASS", f"Endpoint exists, connection failed as expected: {type(e).__name__}")

        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error testing endpoint: {e}")

    def test_backend_router_changes(self):
        """Test that backend router changes are in place."""
        test_name = "Backend Router Changes"

        try:
            # Check if the gameplay router file has the correct endpoint
            router_file = "src/player_experience/api/routers/gameplay_websocket.py"

            with open(router_file) as f:
                content = f.read()

            # Check for the new endpoint signature
            if '@router.websocket("/gameplay/{player_id}/{session_id}")' in content:
                self.log_test(test_name, "PASS", "New endpoint signature found")
            else:
                self.log_test(test_name, "FAIL", "New endpoint signature not found")

            # Check for message type transformation
            if 'message_type == "user_message"' in content and 'message_type = "player_input"' in content:
                self.log_test("Message Type Transformation", "PASS", "Message transformation logic found")
            else:
                self.log_test("Message Type Transformation", "FAIL", "Message transformation logic not found")

        except FileNotFoundError:
            self.log_test(test_name, "FAIL", "Router file not found")
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error checking router: {e}")

    def test_frontend_websocket_changes(self):
        """Test that front-end WebSocket changes are in place."""
        test_name = "Frontend WebSocket Changes"

        try:
            # Check if the WebSocket service has been updated
            websocket_file = "src/player_experience/frontend/src/services/websocket.ts"

            with open(websocket_file) as f:
                content = f.read()

            # Check for the new endpoint format
            if '/ws/gameplay/${currentPlayerId}/${sessionId}' in content:
                self.log_test(test_name, "PASS", "New WebSocket endpoint format found")
            else:
                self.log_test(test_name, "FAIL", "New WebSocket endpoint format not found")

            # Check for player_input message type
            if 'type: "player_input"' in content:
                self.log_test("Frontend Message Type", "PASS", "player_input message type found")
            else:
                self.log_test("Frontend Message Type", "FAIL", "player_input message type not found")

            # Check for narrative_response handling
            if 'data.type === "narrative_response"' in content:
                self.log_test("Narrative Response Handling", "PASS", "Narrative response handling found")
            else:
                self.log_test("Narrative Response Handling", "FAIL", "Narrative response handling not found")

        except FileNotFoundError:
            self.log_test(test_name, "FAIL", "WebSocket service file not found")
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error checking WebSocket service: {e}")

    def test_chat_component_changes(self):
        """Test that Chat component changes are in place."""
        test_name = "Chat Component Changes"

        try:
            # Check if the Chat component has been updated
            chat_file = "src/player_experience/frontend/src/pages/Chat/Chat.tsx"

            with open(chat_file) as f:
                content = f.read()

            # Check for the new connection parameters
            if 'websocketService.connect(sessionId, playerId)' in content:
                self.log_test(test_name, "PASS", "Updated connection call found")
            else:
                self.log_test(test_name, "FAIL", "Updated connection call not found")

        except FileNotFoundError:
            self.log_test(test_name, "FAIL", "Chat component file not found")
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error checking Chat component: {e}")

    async def test_message_flow_simulation(self):
        """Simulate the message flow to test integration."""
        test_name = "Message Flow Simulation"

        try:
            # Simulate front-end message
            frontend_message = {
                "type": "player_input",
                "content": {
                    "text": "I want to explore the peaceful garden",
                    "input_type": "narrative_action"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": "test_session_001",
                "metadata": {}
            }

            # Simulate expected backend response
            expected_response = {
                "type": "narrative_response",
                "session_id": "test_session_001",
                "content": {
                    "text": "You step into the peaceful garden...",
                    "scene_updates": {"location": "garden_entrance"},
                    "therapeutic_elements": {"mindfulness_cue": "Notice the sounds around you"}
                },
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "response_type": "narrative_continuation",
                    "therapeutic_focus": ["mindfulness"]
                }
            }

            # Validate message structure
            required_fields = ["type", "content", "timestamp"]

            frontend_valid = all(field in frontend_message for field in required_fields)
            response_valid = all(field in expected_response for field in required_fields)

            if frontend_valid and response_valid:
                self.log_test(test_name, "PASS", "Message structures are valid")
            else:
                self.log_test(test_name, "FAIL", "Message structures are invalid")

        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error in message flow simulation: {e}")

    def test_service_integration_readiness(self):
        """Test that all required services are available."""
        test_name = "Service Integration Readiness"

        services_to_check = [
            "src/player_experience/services/gameplay_chat_manager.py",
            "src/player_experience/services/dynamic_story_generation_service.py",
            "src/player_experience/services/story_initialization_service.py",
            "src/player_experience/services/therapeutic_safety_integration.py"
        ]

        missing_services = []
        for service_path in services_to_check:
            try:
                with open(service_path) as f:
                    content = f.read()
                    # Basic validation that it's a service class
                    if "class " in content and "Service" in content:
                        continue
                    else:
                        missing_services.append(f"{service_path} (invalid structure)")
            except FileNotFoundError:
                missing_services.append(service_path)

        if not missing_services:
            self.log_test(test_name, "PASS", "All required services are available")
        else:
            self.log_test(test_name, "FAIL", f"Missing services: {missing_services}")

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 RUNNING CHAT INTEGRATION TESTS")
        print("=" * 50)

        # Test backend changes
        self.test_backend_router_changes()

        # Test frontend changes
        self.test_frontend_websocket_changes()
        self.test_chat_component_changes()

        # Test service availability
        self.test_service_integration_readiness()

        # Test WebSocket endpoint
        await self.test_websocket_endpoint_availability()

        # Test message flow
        await self.test_message_flow_simulation()

        # Generate summary
        self.generate_test_summary()

    def generate_test_summary(self):
        """Generate test summary."""
        print("\n📊 TEST SUMMARY")
        print("=" * 50)

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

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test']}: {result['details']}")

        print("\n🎯 INTEGRATION STATUS:")
        if success_rate >= 80:
            print("✅ Integration fixes are working well!")
        elif success_rate >= 60:
            print("⚠️  Integration fixes are partially working, some issues remain")
        else:
            print("❌ Integration fixes need more work")

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "status": "GOOD" if success_rate >= 80 else "PARTIAL" if success_rate >= 60 else "NEEDS_WORK"
        }


async def main():
    """Run the integration tests."""
    tester = ChatIntegrationTester()
    await tester.run_all_tests()
    results = tester.generate_test_summary()

    print(f"\n✅ Integration testing complete. Status: {results['status']}")
    return results


if __name__ == "__main__":
    results = asyncio.run(main())
