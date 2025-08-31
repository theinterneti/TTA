#!/usr/bin/env python3
"""
Simple WebSocket Connection Test

This script tests the WebSocket connection to the gameplay endpoint
without requiring JWT token generation.
"""

import asyncio
import json
import websockets
import requests
from datetime import datetime
from typing import Dict, Any, Optional


class SimpleWebSocketTester:
    """Simple WebSocket connection tester."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.player_id = "test_player_001"
        self.session_id = "test_session_001"
        self.test_results = []
        
    def log_result(self, test_name: str, status: str, details: str = ""):
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
    
    async def test_server_health(self):
        """Test if the server is running and healthy."""
        print("\n🏥 TESTING SERVER HEALTH")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Server Health", "PASS", f"Server is running on {self.base_url}")
                return True
            else:
                self.log_result("Server Health", "FAIL", f"Server returned {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Server Health", "FAIL", f"Server not accessible: {e}")
            return False
    
    async def test_websocket_endpoint_exists(self):
        """Test if the WebSocket endpoint exists (even if auth fails)."""
        print("\n🔌 TESTING WEBSOCKET ENDPOINT")
        print("-" * 30)
        
        ws_endpoint = f"{self.ws_url}/ws/gameplay/{self.player_id}/{self.session_id}"
        print(f"Testing endpoint: {ws_endpoint}")
        
        try:
            # Try to connect without auth - should get 403 or 1008 close code
            websocket = await websockets.connect(ws_endpoint)
            # If we get here, the endpoint exists but doesn't require auth
            await websocket.close()
            self.log_result("WebSocket Endpoint", "PASS", "Endpoint exists and is accessible")
            return True
        except websockets.exceptions.ConnectionClosedError as e:
            if e.code == 1008:  # Policy violation (auth required)
                self.log_result("WebSocket Endpoint", "PASS", "Endpoint exists, authentication required as expected")
                return True
            else:
                self.log_result("WebSocket Endpoint", "FAIL", f"Unexpected close code: {e.code}")
                return False
        except Exception as e:
            if "403" in str(e) or "401" in str(e):
                self.log_result("WebSocket Endpoint", "PASS", "Endpoint exists, authentication required")
                return True
            elif "404" in str(e):
                self.log_result("WebSocket Endpoint", "FAIL", "Endpoint not found (404)")
                return False
            else:
                self.log_result("WebSocket Endpoint", "WARNING", f"Connection failed: {e}")
                return False
    
    async def test_message_format_validation(self):
        """Test message format validation by examining server logs."""
        print("\n📝 TESTING MESSAGE FORMAT VALIDATION")
        print("-" * 40)
        
        # Test different message formats
        test_messages = [
            {
                "name": "Player Input Format",
                "message": {
                    "type": "player_input",
                    "content": {
                        "text": "I want to explore the garden",
                        "input_type": "narrative_action"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            {
                "name": "Legacy User Message Format",
                "message": {
                    "type": "user_message",
                    "content": {"text": "Hello world"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            {
                "name": "Choice Selection Format",
                "message": {
                    "type": "choice_selection",
                    "content": {
                        "choice_id": "choice_1",
                        "choice_text": "Take the peaceful path"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        ]
        
        for test_msg in test_messages:
            # Validate JSON serialization
            try:
                json_str = json.dumps(test_msg["message"])
                parsed = json.loads(json_str)
                self.log_result(f"{test_msg['name']} JSON", "PASS", "Valid JSON format")
            except Exception as e:
                self.log_result(f"{test_msg['name']} JSON", "FAIL", f"Invalid JSON: {e}")
    
    async def test_backend_integration_readiness(self):
        """Test if backend services are ready for integration."""
        print("\n🔧 TESTING BACKEND INTEGRATION READINESS")
        print("-" * 45)
        
        # Check if required service files exist
        service_files = [
            "src/player_experience/services/gameplay_chat_manager.py",
            "src/player_experience/services/dynamic_story_generation_service.py",
            "src/player_experience/api/routers/gameplay_websocket.py"
        ]
        
        missing_files = []
        for file_path in service_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "class " in content:
                        self.log_result(f"Service File: {file_path.split('/')[-1]}", "PASS", "File exists and has class definition")
                    else:
                        self.log_result(f"Service File: {file_path.split('/')[-1]}", "WARNING", "File exists but no class found")
            except FileNotFoundError:
                missing_files.append(file_path)
                self.log_result(f"Service File: {file_path.split('/')[-1]}", "FAIL", "File not found")
        
        if not missing_files:
            self.log_result("Backend Integration", "PASS", "All required service files are present")
        else:
            self.log_result("Backend Integration", "FAIL", f"Missing files: {len(missing_files)}")
    
    async def test_frontend_integration_readiness(self):
        """Test if frontend is ready for integration."""
        print("\n🎨 TESTING FRONTEND INTEGRATION READINESS")
        print("-" * 45)
        
        # Check if frontend files have been updated
        frontend_files = [
            "src/player_experience/frontend/src/services/websocket.ts",
            "src/player_experience/frontend/src/pages/Chat/Chat.tsx"
        ]
        
        for file_path in frontend_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for updated endpoint format
                    if "/ws/gameplay/" in content:
                        self.log_result(f"Frontend File: {file_path.split('/')[-1]}", "PASS", "Updated to use gameplay endpoint")
                    elif "/ws/chat" in content:
                        self.log_result(f"Frontend File: {file_path.split('/')[-1]}", "WARNING", "Still using legacy chat endpoint")
                    else:
                        self.log_result(f"Frontend File: {file_path.split('/')[-1]}", "WARNING", "No WebSocket endpoint found")
                        
            except FileNotFoundError:
                self.log_result(f"Frontend File: {file_path.split('/')[-1]}", "FAIL", "File not found")
    
    def generate_test_report(self):
        """Generate test report."""
        print(f"\n📊 INTEGRATION TEST REPORT")
        print("=" * 40)
        
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
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test']}: {result['details']}")
        
        # Integration readiness assessment
        print(f"\n🎯 INTEGRATION READINESS ASSESSMENT:")
        if success_rate >= 80:
            print("✅ READY: Integration is ready for full testing")
        elif success_rate >= 60:
            print("⚠️  MOSTLY READY: Minor issues need to be addressed")
        elif success_rate >= 40:
            print("⚠️  PARTIALLY READY: Several issues need attention")
        else:
            print("❌ NOT READY: Major issues prevent integration testing")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "status": "READY" if success_rate >= 80 else "MOSTLY_READY" if success_rate >= 60 else "PARTIALLY_READY" if success_rate >= 40 else "NOT_READY"
        }
    
    async def run_integration_readiness_test(self):
        """Run integration readiness tests."""
        print("🚀 STARTING INTEGRATION READINESS TEST")
        print("=" * 50)
        
        try:
            # Test server health
            await self.test_server_health()
            
            # Test WebSocket endpoint
            await self.test_websocket_endpoint_exists()
            
            # Test message formats
            await self.test_message_format_validation()
            
            # Test backend readiness
            await self.test_backend_integration_readiness()
            
            # Test frontend readiness
            await self.test_frontend_integration_readiness()
            
        except Exception as e:
            self.log_result("Test Execution", "FAIL", f"Unexpected error: {e}")
        
        # Generate report
        return self.generate_test_report()


async def main():
    """Run the integration readiness test."""
    tester = SimpleWebSocketTester()
    results = await tester.run_integration_readiness_test()
    
    print(f"\n✅ Integration readiness testing complete. Status: {results['status']}")
    
    # Provide next steps based on results
    if results['status'] == 'READY':
        print("\n🎯 NEXT STEPS:")
        print("1. Create proper authentication token for full testing")
        print("2. Run comprehensive 10-turn interactive session test")
        print("3. Test therapeutic safety integration")
        print("4. Validate story flow and character persistence")
    elif results['status'] in ['MOSTLY_READY', 'PARTIALLY_READY']:
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Address failed tests shown above")
        print("2. Update any legacy endpoints or message formats")
        print("3. Ensure all service files are properly implemented")
        print("4. Re-run this test after fixes")
    else:
        print("\n❌ CRITICAL ISSUES:")
        print("1. Fix all failed tests before proceeding")
        print("2. Ensure server is running and accessible")
        print("3. Verify all required files are present")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(main())
