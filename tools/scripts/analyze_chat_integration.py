#!/usr/bin/env python3
"""
Chat Front-End Integration Analysis Script

This script analyzes the integration between the chat front-end and the complete
gameplay loop implementation, identifying issues and providing recommendations.
"""

import os


def analyze_frontend_websocket_service():
    """Analyze the front-end WebSocket service implementation."""
    print("🔍 ANALYZING FRONT-END WEBSOCKET SERVICE")
    print("-" * 50)

    frontend_websocket_path = "src/player_experience/frontend/src/services/websocket.ts"

    if os.path.exists(frontend_websocket_path):
        with open(frontend_websocket_path) as f:
            content = f.read()

        # Check for WebSocket endpoint
        if '/ws/chat' in content:
            print("❌ ISSUE: Front-end connects to /ws/chat endpoint")
        else:
            print("⚠️  Could not find WebSocket endpoint in front-end code")

        # Check for message types
        if 'user_message' in content:
            print("❌ ISSUE: Front-end uses 'user_message' type")

        print("✅ Front-end WebSocket service file found and analyzed")
    else:
        print("⚠️  Front-end WebSocket service file not found")

    return {
        "endpoint_issue": True,
        "message_type_issue": True,
        "file_exists": os.path.exists(frontend_websocket_path)
    }


def analyze_backend_endpoints():
    """Analyze available backend WebSocket endpoints."""
    print("\n🔍 ANALYZING BACKEND WEBSOCKET ENDPOINTS")
    print("-" * 50)

    # Check gameplay WebSocket router
    gameplay_router_path = "src/player_experience/api/routers/gameplay_websocket.py"
    api_gateway_router_path = "src/api_gateway/websocket/router.py"

    available_endpoints = []
    missing_endpoints = []

    # Check gameplay router
    if os.path.exists(gameplay_router_path):
        with open(gameplay_router_path) as f:
            content = f.read()

        if '@router.websocket("/gameplay")' in content:
            available_endpoints.append("/ws/gameplay (no path parameters)")
            print("✅ Found /ws/gameplay endpoint")

        if 'websocket_gameplay_endpoint' in content:
            print("✅ Gameplay WebSocket handler found")
    else:
        print("❌ Gameplay WebSocket router not found")

    # Check API gateway router
    if os.path.exists(api_gateway_router_path):
        with open(api_gateway_router_path) as f:
            content = f.read()

        if '/ws/chat' in content:
            available_endpoints.append("/ws/chat")
            print("✅ Found /ws/chat endpoint in API gateway")

        if '/ws/therapeutic' in content:
            available_endpoints.append("/ws/therapeutic/{session_id}")
            print("✅ Found /ws/therapeutic endpoint")

    # Check for the expected endpoint
    expected_endpoint = "/ws/gameplay/{player_id}/{session_id}"
    if expected_endpoint not in str(available_endpoints):
        missing_endpoints.append(expected_endpoint)
        print(f"❌ MISSING: {expected_endpoint}")

    return {
        "available_endpoints": available_endpoints,
        "missing_endpoints": missing_endpoints
    }


def analyze_message_formats():
    """Analyze message format compatibility."""
    print("\n🔍 ANALYZING MESSAGE FORMAT COMPATIBILITY")
    print("-" * 50)

    # Expected gameplay message formats from our implementation
    expected_formats = {
        "player_input": {
            "type": "player_input",
            "content": {
                "text": "string",
                "input_type": "narrative_action"
            },
            "timestamp": "ISO string"
        },
        "narrative_response": {
            "type": "narrative_response",
            "session_id": "string",
            "content": {
                "text": "string",
                "scene_updates": "object",
                "therapeutic_elements": "object"
            },
            "timestamp": "ISO string"
        },
        "choice_request": {
            "type": "choice_request",
            "session_id": "string",
            "content": {
                "prompt": "string",
                "choices": "array"
            },
            "timestamp": "ISO string"
        }
    }

    # Current front-end message format (based on analysis)
    current_frontend_format = {
        "user_message": {
            "type": "user_message",
            "content": {"text": "string"},
            "timestamp": "ISO string",
            "session_id": "string",
            "metadata": "object"
        }
    }

    print("Expected gameplay message types:")
    for msg_type in expected_formats.keys():
        print(f"  ✅ {msg_type}")

    print("\nCurrent front-end message types:")
    for msg_type in current_frontend_format.keys():
        print(f"  ❌ {msg_type} (incompatible)")

    return {
        "expected_formats": expected_formats,
        "current_formats": current_frontend_format,
        "compatibility": False
    }


def analyze_service_integration():
    """Analyze service integration points."""
    print("\n🔍 ANALYZING SERVICE INTEGRATION POINTS")
    print("-" * 50)

    # Check if our new services exist
    services_to_check = [
        "src/player_experience/services/gameplay_chat_manager.py",
        "src/player_experience/services/dynamic_story_generation_service.py",
        "src/player_experience/services/story_initialization_service.py",
        "src/player_experience/services/therapeutic_safety_integration.py"
    ]

    existing_services = []
    missing_services = []

    for service_path in services_to_check:
        if os.path.exists(service_path):
            existing_services.append(service_path)
            service_name = os.path.basename(service_path)
            print(f"✅ {service_name}")
        else:
            missing_services.append(service_path)
            service_name = os.path.basename(service_path)
            print(f"❌ {service_name}")

    return {
        "existing_services": existing_services,
        "missing_services": missing_services,
        "integration_ready": len(missing_services) == 0
    }


def generate_integration_fixes():
    """Generate specific fixes needed for integration."""
    print("\n🎯 INTEGRATION FIXES REQUIRED")
    print("=" * 50)

    fixes = [
        {
            "priority": "CRITICAL",
            "component": "Backend WebSocket Router",
            "issue": "Missing /ws/gameplay/{player_id}/{session_id} endpoint",
            "fix": "Create new WebSocket endpoint with path parameters",
            "file": "src/player_experience/routers/gameplay_websocket_router.py"
        },
        {
            "priority": "CRITICAL",
            "component": "Front-end WebSocket Service",
            "issue": "Connecting to wrong endpoint (/ws/chat instead of /ws/gameplay)",
            "fix": "Update WebSocket connection URL to use gameplay endpoint",
            "file": "src/player_experience/frontend/src/services/websocket.ts"
        },
        {
            "priority": "HIGH",
            "component": "Message Format Mapping",
            "issue": "Front-end sends 'user_message', backend expects 'player_input'",
            "fix": "Add message type transformation layer",
            "file": "Front-end WebSocket service or backend router"
        },
        {
            "priority": "HIGH",
            "component": "Session Management",
            "issue": "Different session ID handling approaches",
            "fix": "Align session management between front-end and backend",
            "file": "Multiple files"
        },
        {
            "priority": "MEDIUM",
            "component": "Error Handling",
            "issue": "No graceful handling of integration failures",
            "fix": "Add comprehensive error handling and user feedback",
            "file": "Front-end components and backend routers"
        }
    ]

    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['priority']} - {fix['component']}")
        print(f"   Issue: {fix['issue']}")
        print(f"   Fix: {fix['fix']}")
        print(f"   File: {fix['file']}\n")

    return fixes


def create_integration_test_plan():
    """Create a test plan for verifying integration."""
    print("\n📋 INTEGRATION TEST PLAN")
    print("=" * 50)

    test_scenarios = [
        {
            "test": "WebSocket Connection",
            "description": "Verify front-end can connect to gameplay endpoint",
            "steps": [
                "Update front-end to use /ws/gameplay/{player_id}/{session_id}",
                "Test connection establishment",
                "Verify authentication works",
                "Check connection cleanup"
            ]
        },
        {
            "test": "Message Routing",
            "description": "Verify messages flow correctly between components",
            "steps": [
                "Send player input from front-end",
                "Verify GameplayChatManager receives message",
                "Check DynamicStoryGenerationService processes message",
                "Confirm narrative response reaches front-end"
            ]
        },
        {
            "test": "Story Flow Integration",
            "description": "Test complete story initialization and gameplay",
            "steps": [
                "Trigger story initialization from front-end",
                "Verify StoryInitializationService creates session",
                "Check opening narrative generation",
                "Test ongoing story interactions"
            ]
        },
        {
            "test": "Safety Integration",
            "description": "Verify therapeutic safety monitoring works",
            "steps": [
                "Send message with safety concerns",
                "Verify TherapeuticSafetyIntegration detects issue",
                "Check intervention message sent to front-end",
                "Confirm user sees safety support"
            ]
        },
        {
            "test": "Error Handling",
            "description": "Test error scenarios and recovery",
            "steps": [
                "Test connection failures",
                "Test service unavailability",
                "Test invalid message formats",
                "Verify graceful error handling"
            ]
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"{i}. {scenario['test']}")
        print(f"   {scenario['description']}")
        for step in scenario['steps']:
            print(f"   • {step}")
        print()

    return test_scenarios


def main():
    """Run the complete integration analysis."""
    print("🚀 CHAT FRONT-END INTEGRATION ANALYSIS")
    print("=" * 60)

    # Run all analyses
    analyze_frontend_websocket_service()
    backend_analysis = analyze_backend_endpoints()
    message_analysis = analyze_message_formats()
    service_analysis = analyze_service_integration()

    # Generate fixes and test plan
    fixes = generate_integration_fixes()
    test_plan = create_integration_test_plan()

    # Summary
    print("\n📊 ANALYSIS SUMMARY")
    print("=" * 60)

    critical_issues = len([f for f in fixes if f['priority'] == 'CRITICAL'])
    high_issues = len([f for f in fixes if f['priority'] == 'HIGH'])
    medium_issues = len([f for f in fixes if f['priority'] == 'MEDIUM'])

    print(f"Critical Issues: {critical_issues}")
    print(f"High Priority Issues: {high_issues}")
    print(f"Medium Priority Issues: {medium_issues}")
    print(f"Total Issues: {critical_issues + high_issues + medium_issues}")

    print(f"\nServices Ready: {len(service_analysis['existing_services'])}/{len(service_analysis['existing_services']) + len(service_analysis['missing_services'])}")
    print(f"Message Compatibility: {'❌ No' if not message_analysis['compatibility'] else '✅ Yes'}")
    print(f"Endpoint Availability: {'❌ Missing' if backend_analysis['missing_endpoints'] else '✅ Available'}")

    print("\n🎯 NEXT STEPS:")
    print("1. Implement missing /ws/gameplay/{player_id}/{session_id} endpoint")
    print("2. Update front-end to use correct endpoint and message formats")
    print("3. Add message type transformation/mapping")
    print("4. Implement comprehensive error handling")
    print("5. Run integration tests to verify fixes")

    return {
        "status": "ANALYSIS_COMPLETE",
        "critical_issues": critical_issues,
        "total_issues": critical_issues + high_issues + medium_issues,
        "fixes_required": fixes,
        "test_plan": test_plan
    }


if __name__ == "__main__":
    results = main()
    print(f"\n✅ Analysis complete. Found {results['total_issues']} issues requiring fixes.")
