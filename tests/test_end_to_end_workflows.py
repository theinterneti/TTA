"""
End-to-end integration tests for complete user workflows.

This module tests complete user journeys from character creation through therapeutic interaction,
including performance tests for concurrent user scenarios.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.player_experience.api.app import create_app
from src.player_experience.api.auth import ALGORITHM, SECRET_KEY
from src.player_experience.api.config import TestingSettings


@pytest.fixture
def client():
    """Create a test FastAPI application client."""
    import src.player_experience.api.config as config_module

    config_module.settings = TestingSettings()
    app = create_app()
    return TestClient(app)


def create_auth_token(
    player_id: str = "test-player",
    username: str = "testuser",
    email: str = "test@example.com",
) -> str:
    """Create a JWT token for testing."""
    payload = {
        "sub": player_id,
        "username": username,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_test_character_data(name: str = "Test Character") -> dict[str, Any]:
    """Create test character creation data."""
    return {
        "name": name,
        "appearance": {
            "physical_description": "A thoughtful person with kind eyes",
            "clothing_style": "casual",
            "distinctive_features": ["warm smile"],
        },
        "background": {
            "name": name,
            "age": 25,
            "occupation": "student",
            "personality_traits": ["empathetic", "curious", "patient"],
            "backstory": "A student exploring personal growth through therapeutic adventures",
        },
        "therapeutic_profile": {
            "readiness_level": 0.7,
            "preferred_intensity": "medium",
            "therapeutic_approaches": ["cbt", "narrative_therapy"],
            "therapeutic_goals": [
                {
                    "goal_id": "goal-1",
                    "description": "Improve emotional regulation",
                    "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
                    "priority": "high",
                    "is_active": True,
                }
            ],
            "comfort_topics": ["relationships", "personal_growth"],
            "avoid_topics": ["trauma", "violence"],
            "trigger_warnings": ["loud_noises"],
        },
    }


class TestEndToEndUserWorkflows:
    """Test complete user workflows from start to finish."""

    def test_complete_new_user_journey(self, client):
        """Test complete journey for a new user from registration to therapeutic interaction."""
        player_id = "new-user-123"
        token = create_auth_token(player_id, "newuser", "newuser@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Create player profile
        profile_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "therapeutic_preferences": {
                "intensity_level": "medium",
                "preferred_approaches": ["cbt", "mindfulness"],
                "trigger_warnings": ["violence"],
                "comfort_topics": ["relationships"],
                "avoid_topics": ["trauma"],
            },
            "privacy_settings": {
                "data_sharing_consent": True,
                "research_participation": False,
                "contact_preferences": ["email"],
            },
        }

        response = client.post("/api/v1/players/", json=profile_data, headers=headers)
        assert response.status_code == 201
        player_profile = response.json()
        assert player_profile["player_id"] == player_id

        # Step 2: Create first character
        character_data = create_test_character_data("Alex")
        response = client.post(
            "/api/v1/characters/", json=character_data, headers=headers
        )
        assert response.status_code == 201
        character = response.json()
        character_id = character["character_id"]
        assert character["name"] == "Alex"

        # Step 3: Browse available worlds
        response = client.get("/api/v1/worlds/", headers=headers)
        assert response.status_code == 200
        worlds = response.json()
        assert len(worlds) > 0

        # Select first compatible world
        world_id = worlds[0]["world_id"]

        # Step 4: Check world compatibility
        response = client.get(
            f"/api/v1/worlds/{world_id}/compatibility/{character_id}", headers=headers
        )
        assert response.status_code == 200
        compatibility = response.json()
        assert compatibility["is_compatible"] is True

        # Step 5: Customize world parameters
        world_params = {
            "difficulty_level": "medium",
            "therapeutic_intensity": "medium",
            "narrative_style": "collaborative",
            "session_length": "standard",
        }
        response = client.post(
            f"/api/v1/worlds/{world_id}/customize", json=world_params, headers=headers
        )
        assert response.status_code == 200

        # Step 6: Create therapeutic session
        session_data = {
            "character_id": character_id,
            "world_id": world_id,
            "therapeutic_settings": {
                "intensity_level": "medium",
                "preferred_approaches": ["cbt"],
                "session_goals": ["emotional_regulation"],
                "safety_monitoring": True,
            },
        }
        response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
        assert response.status_code == 201
        session = response.json()
        session_id = session["session_id"]

        # Step 7: Connect to WebSocket chat
        with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
            # Receive welcome message
            welcome_msg = json.loads(websocket.receive_text())
            assert welcome_msg["role"] == "system"
            assert "Connected to therapeutic chat" in welcome_msg["content"]["text"]

            # Send initial message
            user_message = {
                "type": "user_message",
                "content": {
                    "text": "Hello, I'm ready to start my therapeutic journey."
                },
                "metadata": {
                    "character_id": character_id,
                    "world_id": world_id,
                    "session_id": session_id,
                },
            }
            websocket.send_text(json.dumps(user_message))

            # Receive therapeutic response
            response_msg = json.loads(websocket.receive_text())
            assert response_msg["role"] == "assistant"
            assert "text" in response_msg["content"]
            assert response_msg["metadata"]["safety"]["crisis"] is False

            # Send feedback
            feedback = {
                "type": "feedback",
                "content": {
                    "rating": 5,
                    "text": "This is very helpful",
                    "helpful_aspects": ["empathetic_response", "clear_guidance"],
                },
            }
            websocket.send_text(json.dumps(feedback))

            # Receive feedback acknowledgment
            feedback_ack = json.loads(websocket.receive_text())
            assert feedback_ack["role"] == "system"
            assert "Feedback processed" in feedback_ack["content"]["text"]

        # Step 8: Check progress tracking
        response = client.get(f"/api/v1/players/{player_id}/progress", headers=headers)
        assert response.status_code == 200
        progress = response.json()
        assert progress["player_id"] == player_id
        assert progress["total_sessions"] >= 1

        # Step 9: Get player dashboard
        response = client.get(f"/api/v1/players/{player_id}/dashboard", headers=headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert dashboard["player_id"] == player_id
        assert len(dashboard["active_characters"]) == 1
        assert len(dashboard["recommendations"]) > 0

    def test_multi_character_workflow(self, client):
        """Test workflow with multiple characters and world switching."""
        player_id = "multi-char-user"
        token = create_auth_token(player_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Create player profile
        profile_data = {
            "username": "multiuser",
            "email": "multi@example.com",
            "therapeutic_preferences": {
                "intensity_level": "medium",
                "preferred_approaches": ["cbt", "narrative_therapy"],
                "trigger_warnings": [],
                "comfort_topics": ["personal_growth"],
                "avoid_topics": [],
            },
        }
        client.post("/api/v1/players/", json=profile_data, headers=headers)

        # Create multiple characters
        characters = []
        for i, name in enumerate(["Character1", "Character2", "Character3"]):
            char_data = create_test_character_data(name)
            # Vary therapeutic approaches
            char_data["therapeutic_profile"]["therapeutic_approaches"] = [
                ["cbt"],
                ["narrative_therapy"],
                ["mindfulness"],
            ][i]

            response = client.post(
                "/api/v1/characters/", json=char_data, headers=headers
            )
            assert response.status_code == 201
            characters.append(response.json())

        assert len(characters) == 3

        # Get available worlds
        response = client.get("/api/v1/worlds/", headers=headers)
        worlds = response.json()

        # Create sessions for each character in different worlds
        sessions = []
        for i, character in enumerate(characters):
            world_id = worlds[i % len(worlds)]["world_id"]

            session_data = {
                "character_id": character["character_id"],
                "world_id": world_id,
                "therapeutic_settings": {
                    "intensity_level": "medium",
                    "preferred_approaches": character["therapeutic_profile"][
                        "therapeutic_approaches"
                    ],
                    "session_goals": ["personal_growth"],
                    "safety_monitoring": True,
                },
            }

            response = client.post(
                "/api/v1/sessions/", json=session_data, headers=headers
            )
            assert response.status_code == 201
            sessions.append(response.json())

        # Test character switching via WebSocket
        with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
            websocket.receive_text()  # Welcome message

            # Interact with each character
            for _i, (character, session) in enumerate(
                zip(characters, sessions, strict=False)
            ):
                switch_message = {
                    "type": "switch_context",
                    "metadata": {
                        "character_id": character["character_id"],
                        "world_id": session["world_id"],
                        "session_id": session["session_id"],
                    },
                }
                websocket.send_text(json.dumps(switch_message))

                # Receive context switch confirmation
                switch_response = json.loads(websocket.receive_text())
                assert switch_response["role"] == "system"
                assert "context switched" in switch_response["content"]["text"].lower()

                # Send message as this character
                user_message = {
                    "type": "user_message",
                    "content": {"text": f"Hello from {character['name']}"},
                    "metadata": {
                        "character_id": character["character_id"],
                        "world_id": session["world_id"],
                        "session_id": session["session_id"],
                    },
                }
                websocket.send_text(json.dumps(user_message))

                # Receive response
                response_msg = json.loads(websocket.receive_text())
                assert response_msg["role"] == "assistant"
                assert "text" in response_msg["content"]

        # Verify dashboard shows all characters
        response = client.get(f"/api/v1/players/{player_id}/dashboard", headers=headers)
        dashboard = response.json()
        assert len(dashboard["active_characters"]) == 3

    def test_therapeutic_settings_adaptation_workflow(self, client):
        """Test workflow where therapeutic settings are adapted based on user feedback."""
        player_id = "adaptive-user"
        token = create_auth_token(player_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Create player and character
        profile_data = {
            "username": "adaptiveuser",
            "email": "adaptive@example.com",
            "therapeutic_preferences": {
                "intensity_level": "low",  # Start with low intensity
                "preferred_approaches": ["mindfulness"],
                "trigger_warnings": ["anxiety"],
                "comfort_topics": ["relaxation"],
                "avoid_topics": ["stress"],
            },
        }
        client.post("/api/v1/players/", json=profile_data, headers=headers)

        char_data = create_test_character_data("Adaptive Character")
        char_data["therapeutic_profile"]["preferred_intensity"] = "low"
        response = client.post("/api/v1/characters/", json=char_data, headers=headers)
        character = response.json()
        character_id = character["character_id"]

        # Create session
        worlds = client.get("/api/v1/worlds/", headers=headers).json()
        world_id = worlds[0]["world_id"]

        session_data = {
            "character_id": character_id,
            "world_id": world_id,
            "therapeutic_settings": {
                "intensity_level": "low",
                "preferred_approaches": ["mindfulness"],
                "session_goals": ["relaxation"],
                "safety_monitoring": True,
            },
        }
        response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
        session = response.json()

        # Simulate therapeutic interaction with adaptation
        with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
            websocket.receive_text()  # Welcome

            # Initial interaction
            user_message = {
                "type": "user_message",
                "content": {
                    "text": "I'm feeling ready for more challenging exercises."
                },
                "metadata": {
                    "character_id": character_id,
                    "world_id": world_id,
                    "session_id": session["session_id"],
                },
            }
            websocket.send_text(json.dumps(user_message))
            websocket.receive_text()  # Response

            # Provide positive feedback indicating readiness for higher intensity
            feedback = {
                "type": "feedback",
                "content": {
                    "rating": 5,
                    "text": "I feel ready for more challenging content",
                    "adaptation_request": "increase_intensity",
                    "confidence_level": "high",
                },
            }
            websocket.send_text(json.dumps(feedback))
            websocket.receive_text()  # Feedback ack

            # Request therapeutic settings update
            settings_update = {
                "type": "update_settings",
                "content": {
                    "intensity_level": "medium",
                    "preferred_approaches": ["mindfulness", "cbt"],
                    "session_goals": ["emotional_regulation", "coping_skills"],
                },
            }
            websocket.send_text(json.dumps(settings_update))

            # Receive settings update confirmation
            settings_response = json.loads(websocket.receive_text())
            assert settings_response["role"] == "system"
            assert "settings updated" in settings_response["content"]["text"].lower()

            # Continue interaction with updated settings
            follow_up_message = {
                "type": "user_message",
                "content": {"text": "How can I better handle stressful situations?"},
                "metadata": {
                    "character_id": character_id,
                    "world_id": world_id,
                    "session_id": session["session_id"],
                },
            }
            websocket.send_text(json.dumps(follow_up_message))

            response_msg = json.loads(websocket.receive_text())
            assert response_msg["role"] == "assistant"
            # Response should reflect updated intensity and approaches
            assert "text" in response_msg["content"]

        # Verify settings were persisted
        response = client.get(f"/api/v1/characters/{character_id}", headers=headers)
        updated_character = response.json()
        # Settings should be updated in character's therapeutic profile
        assert (
            updated_character["therapeutic_profile"]["preferred_intensity"] == "medium"
        )


class TestConcurrentUserScenarios:
    """Test performance and behavior under concurrent user load."""

    def test_concurrent_websocket_connections(self, client):
        """Test multiple concurrent WebSocket connections."""
        num_users = 10
        connection_results = []

        def create_user_connection(user_id: int):
            """Create a WebSocket connection for a user and perform basic interaction."""
            try:
                player_id = f"concurrent-user-{user_id}"
                token = create_auth_token(player_id)

                start_time = time.time()

                with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
                    # Receive welcome message
                    welcome_msg = json.loads(websocket.receive_text())
                    assert welcome_msg["role"] == "system"

                    # Send test message
                    user_message = {
                        "type": "user_message",
                        "content": {"text": f"Hello from user {user_id}"},
                        "metadata": {
                            "character_id": f"char-{user_id}",
                            "world_id": "world-1",
                        },
                    }
                    websocket.send_text(json.dumps(user_message))

                    # Receive response
                    response_msg = json.loads(websocket.receive_text())
                    assert response_msg["role"] == "assistant"

                    connection_time = time.time() - start_time

                    return {
                        "user_id": user_id,
                        "success": True,
                        "connection_time": connection_time,
                        "response_received": True,
                    }

            except Exception as e:
                return {
                    "user_id": user_id,
                    "success": False,
                    "error": str(e),
                    "connection_time": None,
                }

        # Execute concurrent connections
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [
                executor.submit(create_user_connection, i) for i in range(num_users)
            ]

            for future in as_completed(futures):
                result = future.result()
                connection_results.append(result)

        # Analyze results
        successful_connections = [r for r in connection_results if r["success"]]
        failed_connections = [r for r in connection_results if not r["success"]]

        # Assert performance requirements
        assert len(successful_connections) >= num_users * 0.9  # 90% success rate
        assert len(failed_connections) <= num_users * 0.1  # Max 10% failure rate

        # Check response times
        response_times = [
            r["connection_time"] for r in successful_connections if r["connection_time"]
        ]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)

            # Performance assertions
            assert avg_response_time < 2.0  # Average under 2 seconds
            assert max_response_time < 5.0  # Max under 5 seconds

    def test_concurrent_api_requests(self, client):
        """Test concurrent API requests performance."""
        num_requests = 20
        request_results = []

        def make_api_request(request_id: int):
            """Make a concurrent API request."""
            try:
                player_id = f"api-user-{request_id}"
                token = create_auth_token(player_id)
                headers = {"Authorization": f"Bearer {token}"}

                start_time = time.time()

                # Test different endpoints
                endpoints = [
                    ("/api/v1/worlds/", "GET"),
                    ("/health", "GET"),
                    ("/", "GET"),
                ]

                endpoint, method = endpoints[request_id % len(endpoints)]

                if method == "GET":
                    response = client.get(
                        endpoint,
                        headers=headers if endpoint.startswith("/api/") else None,
                    )

                request_time = time.time() - start_time

                return {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "request_time": request_time,
                }

            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                    "request_time": None,
                }

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(make_api_request, i) for i in range(num_requests)
            ]

            for future in as_completed(futures):
                result = future.result()
                request_results.append(result)

        # Analyze results
        successful_requests = [r for r in request_results if r["success"]]
        failed_requests = [r for r in request_results if not r["success"]]

        # Performance assertions
        assert len(successful_requests) >= num_requests * 0.95  # 95% success rate
        assert len(failed_requests) <= num_requests * 0.05  # Max 5% failure rate

        # Check response times
        response_times = [
            r["request_time"] for r in successful_requests if r["request_time"]
        ]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)

            # Performance requirements from design doc
            assert avg_response_time < 0.2  # Average under 200ms for UI interactions
            assert max_response_time < 1.0  # Max under 1 second

    def test_session_state_consistency_under_load(self, client):
        """Test that session state remains consistent under concurrent access."""
        player_id = "consistency-test-user"
        token = create_auth_token(player_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Create player and character
        profile_data = {
            "username": "consistencyuser",
            "email": "consistency@example.com",
            "therapeutic_preferences": {
                "intensity_level": "medium",
                "preferred_approaches": ["cbt"],
                "trigger_warnings": [],
                "comfort_topics": ["personal_growth"],
                "avoid_topics": [],
            },
        }
        client.post("/api/v1/players/", json=profile_data, headers=headers)

        char_data = create_test_character_data("Consistency Character")
        response = client.post("/api/v1/characters/", json=char_data, headers=headers)
        character = response.json()
        character_id = character["character_id"]

        # Create session
        worlds = client.get("/api/v1/worlds/", headers=headers).json()
        world_id = worlds[0]["world_id"]

        session_data = {
            "character_id": character_id,
            "world_id": world_id,
            "therapeutic_settings": {
                "intensity_level": "medium",
                "preferred_approaches": ["cbt"],
                "session_goals": ["personal_growth"],
                "safety_monitoring": True,
            },
        }
        response = client.post("/api/v1/sessions/", json=session_data, headers=headers)
        session = response.json()
        session_id = session["session_id"]

        # Perform concurrent operations on the same session
        def concurrent_session_operation(operation_id: int):
            """Perform concurrent operations on the same session."""
            try:
                if operation_id % 3 == 0:
                    # Get session details
                    response = client.get(
                        f"/api/v1/sessions/{session_id}", headers=headers
                    )
                    return {
                        "operation": "get_session",
                        "success": response.status_code == 200,
                    }

                elif operation_id % 3 == 1:
                    # Update session settings
                    update_data = {
                        "therapeutic_settings": {
                            "intensity_level": "medium",
                            "preferred_approaches": ["cbt", "mindfulness"],
                            "session_goals": [
                                "personal_growth",
                                "emotional_regulation",
                            ],
                            "safety_monitoring": True,
                        }
                    }
                    response = client.put(
                        f"/api/v1/sessions/{session_id}",
                        json=update_data,
                        headers=headers,
                    )
                    return {
                        "operation": "update_session",
                        "success": response.status_code == 200,
                    }

                else:
                    # Get progress for session
                    response = client.get(
                        f"/api/v1/sessions/{session_id}/progress", headers=headers
                    )
                    return {
                        "operation": "get_progress",
                        "success": response.status_code == 200,
                    }

            except Exception as e:
                return {
                    "operation": f"operation_{operation_id}",
                    "success": False,
                    "error": str(e),
                }

        # Execute concurrent operations
        num_operations = 15
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(concurrent_session_operation, i)
                for i in range(num_operations)
            ]
            results = [future.result() for future in as_completed(futures)]

        # Verify consistency
        successful_operations = [r for r in results if r["success"]]
        assert len(successful_operations) >= num_operations * 0.9  # 90% success rate

        # Verify final session state is consistent
        final_response = client.get(f"/api/v1/sessions/{session_id}", headers=headers)
        assert final_response.status_code == 200
        final_session = final_response.json()
        assert final_session["session_id"] == session_id
        assert final_session["character_id"] == character_id
        assert final_session["world_id"] == world_id


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios in end-to-end workflows."""

    def test_network_interruption_recovery(self, client):
        """Test recovery from network interruptions during WebSocket sessions."""
        player_id = "network-test-user"
        token = create_auth_token(player_id)

        # Simulate network interruption by closing and reopening connection
        with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
            websocket.receive_text()  # Welcome message

            # Send initial message
            user_message = {
                "type": "user_message",
                "content": {"text": "Testing network recovery"},
                "metadata": {"character_id": "char-1", "world_id": "world-1"},
            }
            websocket.send_text(json.dumps(user_message))
            websocket.receive_text()  # Response

        # Reconnect (simulating network recovery)
        with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
            welcome_msg = json.loads(websocket.receive_text())
            assert welcome_msg["role"] == "system"
            assert "Connected to therapeutic chat" in welcome_msg["content"]["text"]

            # Verify session can continue
            continuation_message = {
                "type": "user_message",
                "content": {"text": "Continuing after reconnection"},
                "metadata": {"character_id": "char-1", "world_id": "world-1"},
            }
            websocket.send_text(json.dumps(continuation_message))

            response_msg = json.loads(websocket.receive_text())
            assert response_msg["role"] == "assistant"
            assert "text" in response_msg["content"]

    def test_invalid_data_handling(self, client):
        """Test handling of invalid data in end-to-end workflows."""
        player_id = "invalid-data-user"
        token = create_auth_token(player_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Test invalid character creation data
        invalid_char_data = {
            "name": "",  # Invalid: empty name
            "appearance": {"physical_description": ""},
            "background": {
                "name": "Different Name",  # Invalid: doesn't match character name
                "age": -5,  # Invalid: negative age
                "personality_traits": [],
            },
            "therapeutic_profile": {
                "readiness_level": 2.0,  # Invalid: out of range
                "preferred_intensity": "invalid_intensity",
                "therapeutic_approaches": ["invalid_approach"],
            },
        }

        response = client.post(
            "/api/v1/characters/", json=invalid_char_data, headers=headers
        )
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail

    def test_authentication_failure_recovery(self, client):
        """Test recovery from authentication failures."""
        # Test with expired token
        expired_payload = {
            "sub": "expired-user",
            "username": "expireduser",
            "email": "expired@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Should fail with expired token
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/worlds/", headers=headers)
        assert response.status_code == 401

        # Should succeed with valid token
        valid_token = create_auth_token("valid-user")
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/v1/worlds/", headers=headers)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
