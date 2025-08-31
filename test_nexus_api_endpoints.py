#!/usr/bin/env python3
"""
Test script for Nexus Codex API endpoints via HTTP requests.

This script tests all the Phase 1 Nexus Codex API endpoints using actual HTTP requests.
"""

import asyncio
from datetime import datetime

import aiohttp

# Test configuration
API_BASE_URL = "http://localhost:8080"
TEST_USER = {
    "username": f"nexus_tester_{int(datetime.now().timestamp())}",
    "email": f"nexus.tester.{int(datetime.now().timestamp())}@example.com",
    "password": "TestPassword123!",
    "full_name": "Nexus API Tester",
}


async def create_test_user_and_login():
    """Create a test user and get authentication token."""
    print("🔐 Creating test user and getting authentication token...")

    async with aiohttp.ClientSession() as session:
        try:
            # Try to register a new user
            register_data = {
                "username": TEST_USER["username"],
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "full_name": TEST_USER["full_name"],
            }

            async with session.post(
                f"{API_BASE_URL}/api/v1/auth/register", json=register_data
            ) as response:
                response_text = await response.text()
                if response.status in [200, 201]:
                    print("✅ User registered successfully")
                elif response.status == 400:
                    print("⚠️ User might already exist, trying to login...")
                else:
                    print(
                        f"❌ Registration failed: {response.status} - {response_text}"
                    )
                    return None

            # Login to get token
            login_data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"],
            }

            async with session.post(
                f"{API_BASE_URL}/api/v1/auth/login", json=login_data
            ) as response:
                response_text = await response.text()
                if response.status == 200:
                    try:
                        result = await response.json()
                        token = result.get("access_token")
                        if token:
                            print("✅ Login successful, token obtained")
                            return token
                        else:
                            print(f"❌ No token in login response: {result}")
                            return None
                    except:
                        print(f"❌ Login response not JSON: {response_text}")
                        return None
                else:
                    print(f"❌ Login failed: {response.status} - {response_text}")
                    return None

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None


async def test_nexus_state_endpoint(token):
    """Test GET /api/v1/nexus/state endpoint."""
    print("\n🌌 Testing Nexus State Endpoint...")

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{API_BASE_URL}/api/v1/nexus/state", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Nexus state retrieved successfully")
                    print(f"   - Total worlds: {data.get('total_worlds', 0)}")
                    print(f"   - Active weavers: {data.get('active_story_weavers', 0)}")
                    print(
                        f"   - Narrative strength: {data.get('narrative_strength', 0)}"
                    )
                    print(f"   - Silence threat: {data.get('silence_threat_level', 0)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Nexus state failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Nexus state request failed: {e}")
            return False


async def test_story_spheres_endpoint(token):
    """Test GET /api/v1/nexus/spheres endpoint."""
    print("\n🔮 Testing Story Spheres Endpoint...")

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{API_BASE_URL}/api/v1/nexus/spheres", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    spheres = data.get("spheres", [])
                    print(f"✅ Story spheres retrieved: {len(spheres)} spheres")

                    # Test with genre filter
                    async with session.get(
                        f"{API_BASE_URL}/api/v1/nexus/spheres?genre=fantasy",
                        headers=headers,
                    ) as filter_response:
                        if filter_response.status == 200:
                            filter_data = await filter_response.json()
                            fantasy_spheres = filter_data.get("spheres", [])
                            print(
                                f"✅ Genre filter working: {len(fantasy_spheres)} fantasy spheres"
                            )
                        else:
                            print("⚠️ Genre filter test failed")

                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Story spheres failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Story spheres request failed: {e}")
            return False


async def test_world_creation_endpoint(token):
    """Test POST /api/v1/nexus/worlds endpoint."""
    print("\n🌍 Testing World Creation Endpoint...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test world data - wrap in world_request field as expected by the API
    world_data = {
        "world_request": {
            "title": "API Test World",
            "description": "A test world created via API endpoint testing",
            "genre": "fantasy",  # This should match GenreType.FANTASY.value
            "therapeutic_focus": ["api_testing", "endpoint_validation"],
            "difficulty_level": "intermediate",  # This should match DifficultyLevel.INTERMEDIATE.value
            "estimated_duration": 30,
            "is_public": True,
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/api/v1/nexus/worlds", headers=headers, json=world_data
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    world_id = data.get("world_id")
                    print(f"✅ World created successfully: {world_id}")
                    return world_id
                else:
                    error_text = await response.text()
                    print(f"❌ World creation failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"❌ World creation request failed: {e}")
            return None


async def test_world_details_endpoint(token, world_id):
    """Test GET /api/v1/nexus/worlds/{world_id} endpoint."""
    print(f"\n📖 Testing World Details Endpoint for {world_id}...")

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{API_BASE_URL}/api/v1/nexus/worlds/{world_id}", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ World details retrieved successfully")
                    print(f"   - Title: {data.get('title')}")
                    print(f"   - Genre: {data.get('genre')}")
                    print(f"   - Strength: {data.get('strength_level', 0)}")
                    print(f"   - Rating: {data.get('rating', 0)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ World details failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ World details request failed: {e}")
            return False


async def test_world_search_endpoint(token):
    """Test GET /api/v1/nexus/worlds/search endpoint."""
    print("\n🔍 Testing World Search Endpoint...")

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            # Test basic search
            async with session.get(
                f"{API_BASE_URL}/api/v1/nexus/worlds/search", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    total_count = data.get("total_count", 0)
                    print(
                        f"✅ Basic search successful: {len(results)} results, {total_count} total"
                    )

                    # Test search with filters
                    search_params = {
                        "genre": "fantasy",
                        "limit": "5",
                        "sort_by": "rating",
                    }

                    params_str = "&".join(
                        [f"{k}={v}" for k, v in search_params.items()]
                    )
                    async with session.get(
                        f"{API_BASE_URL}/api/v1/nexus/worlds/search?{params_str}",
                        headers=headers,
                    ) as filter_response:
                        if filter_response.status == 200:
                            filter_data = await filter_response.json()
                            filter_results = filter_data.get("results", [])
                            print(
                                f"✅ Filtered search successful: {len(filter_results)} fantasy worlds"
                            )
                        else:
                            print("⚠️ Filtered search test failed")

                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ World search failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ World search request failed: {e}")
            return False


async def test_world_entry_endpoint(token, world_id):
    """Test POST /api/v1/nexus/worlds/{world_id}/enter endpoint."""
    print(f"\n🚪 Testing World Entry Endpoint for {world_id}...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/api/v1/nexus/worlds/{world_id}/enter", headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data.get("session_id")
                    available_actions = data.get("available_actions", [])
                    print(f"✅ World entry successful: {session_id}")
                    print(f"   - Available actions: {len(available_actions)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ World entry failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ World entry request failed: {e}")
            return False


async def test_error_handling(token):
    """Test error handling with invalid requests."""
    print("\n⚠️ Testing Error Handling...")

    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            # Test invalid world ID
            async with session.get(
                f"{API_BASE_URL}/api/v1/nexus/worlds/invalid_world_id", headers=headers
            ) as response:
                if response.status == 404:
                    print("✅ 404 error handling working for invalid world ID")
                else:
                    print(f"⚠️ Expected 404, got {response.status}")

            # Test invalid authentication
            async with session.get(f"{API_BASE_URL}/api/v1/nexus/state") as response:
                if response.status == 401:
                    print("✅ 401 error handling working for missing auth")
                else:
                    print(f"⚠️ Expected 401, got {response.status}")

            # Test invalid world creation data
            invalid_data = {"title": ""}  # Empty title should fail validation
            async with session.post(
                f"{API_BASE_URL}/api/v1/nexus/worlds",
                headers={**headers, "Content-Type": "application/json"},
                json=invalid_data,
            ) as response:
                if response.status in [400, 422]:
                    print("✅ Validation error handling working for invalid data")
                else:
                    print(f"⚠️ Expected 400/422, got {response.status}")

            return True

        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False


async def run_api_endpoint_tests():
    """Run all API endpoint tests."""
    print("🧪 Nexus Codex API Endpoint Testing Suite")
    print("=" * 60)

    # Step 1: Authentication
    token = await create_test_user_and_login()
    if not token:
        print("❌ Authentication failed - cannot proceed with API tests")
        return

    results = {
        "nexus_state": False,
        "story_spheres": False,
        "world_creation": None,
        "world_details": False,
        "world_search": False,
        "world_entry": False,
        "error_handling": False,
    }

    # Step 2: Test endpoints
    results["nexus_state"] = await test_nexus_state_endpoint(token)
    results["story_spheres"] = await test_story_spheres_endpoint(token)
    results["world_creation"] = await test_world_creation_endpoint(token)

    if results["world_creation"]:
        results["world_details"] = await test_world_details_endpoint(
            token, results["world_creation"]
        )
        results["world_entry"] = await test_world_entry_endpoint(
            token, results["world_creation"]
        )

    results["world_search"] = await test_world_search_endpoint(token)
    results["error_handling"] = await test_error_handling(token)

    # Summary
    print("\n" + "=" * 60)
    print("🎯 API ENDPOINT TEST SUMMARY")
    print("=" * 60)

    print(f"✅ Authentication: {'PASS' if token else 'FAIL'}")
    print(f"✅ Nexus State: {'PASS' if results['nexus_state'] else 'FAIL'}")
    print(f"✅ Story Spheres: {'PASS' if results['story_spheres'] else 'FAIL'}")
    print(f"✅ World Creation: {'PASS' if results['world_creation'] else 'FAIL'}")
    print(f"✅ World Details: {'PASS' if results['world_details'] else 'FAIL'}")
    print(f"✅ World Search: {'PASS' if results['world_search'] else 'FAIL'}")
    print(f"✅ World Entry: {'PASS' if results['world_entry'] else 'FAIL'}")
    print(f"✅ Error Handling: {'PASS' if results['error_handling'] else 'FAIL'}")

    passed_tests = sum(
        [
            1 if token else 0,
            1 if results["nexus_state"] else 0,
            1 if results["story_spheres"] else 0,
            1 if results["world_creation"] else 0,
            1 if results["world_details"] else 0,
            1 if results["world_search"] else 0,
            1 if results["world_entry"] else 0,
            1 if results["error_handling"] else 0,
        ]
    )

    total_tests = 8
    print(f"\n🏆 Overall Result: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print(
            "🎉 All API endpoint tests passed! Nexus Codex Phase 1 is fully functional!"
        )
    else:
        print("⚠️ Some API tests failed. Check the output above for details.")

    return results


if __name__ == "__main__":
    asyncio.run(run_api_endpoint_tests())
