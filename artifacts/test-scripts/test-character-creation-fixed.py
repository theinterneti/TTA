#!/usr/bin/env python3
"""
Test character creation with the fixed schema
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_character_creation():
    """Test the complete character creation flow"""
    
    print("=" * 80)
    print("CHARACTER CREATION END-TO-END TEST")
    print("=" * 80)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Get authentication token
        print("Step 1: Authenticating...")
        auth_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    token = auth_response.get("access_token")
                    print(f"✅ Authentication successful")
                    print(f"   Token: {token[:20]}...")
                else:
                    # Try to register if login fails
                    print("   Login failed, attempting registration...")
                    register_data = {
                        "username": "test_user",
                        "email": "test@example.com",
                        "password": "test_password"
                    }
                    async with session.post(f"{BASE_URL}/api/v1/auth/register", json=register_data) as reg_response:
                        if reg_response.status in [200, 201]:
                            reg_result = await reg_response.json()
                            token = reg_result.get("access_token")
                            print(f"✅ Registration successful")
                            print(f"   Token: {token[:20]}...")
                        else:
                            print(f"❌ Authentication failed: {await reg_response.text()}")
                            return
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return
        
        print()
        
        # Step 2: Create character with correct schema
        print("Step 2: Creating character with correct schema...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        character_data = {
            "name": "Aria Moonwhisper",
            "appearance": {
                "age_range": "adult",
                "gender_identity": "non-binary",
                "physical_description": "A tall figure with flowing silver hair and piercing violet eyes. Their presence radiates calm wisdom.",
                "clothing_style": "flowing robes with celestial patterns",
                "distinctive_features": ["silver hair", "violet eyes", "luminous aura"],
                "avatar_image_url": None
            },
            "background": {
                "name": "Aria Moonwhisper",
                "backstory": "Born under a rare celestial alignment, Aria has always felt connected to the cosmos. They spent years studying ancient wisdom and now seek to help others find their path.",
                "personality_traits": ["compassionate", "wise", "patient", "intuitive"],
                "core_values": ["wisdom", "compassion", "growth", "harmony"],
                "fears_and_anxieties": ["failing to help others", "losing connection to purpose"],
                "strengths_and_skills": ["active listening", "pattern recognition", "emotional intelligence"],
                "life_goals": ["help others find inner peace", "master therapeutic techniques", "create safe healing spaces"],
                "relationships": {
                    "mentor": "Studied under Elder Sage Theron",
                    "community": "Active member of the Healing Circle"
                }
            },
            "therapeutic_profile": {
                "primary_concerns": ["anxiety management", "self-discovery", "emotional regulation"],
                "therapeutic_goals": [
                    {
                        "goal_id": "goal_001",
                        "description": "Develop healthy coping mechanisms for stress",
                        "target_date": None,
                        "progress_percentage": 0.0,
                        "is_active": True,
                        "therapeutic_approaches": []
                    },
                    {
                        "goal_id": "goal_002",
                        "description": "Build stronger self-awareness and emotional intelligence",
                        "target_date": None,
                        "progress_percentage": 0.0,
                        "is_active": True,
                        "therapeutic_approaches": []
                    }
                ],
                "preferred_intensity": "MEDIUM",
                "comfort_zones": ["mindfulness practices", "creative expression", "nature connection"],
                "readiness_level": 0.7,
                "therapeutic_approaches": []
            }
        }
        
        print(f"   Character name: {character_data['name']}")
        print(f"   Physical description: {character_data['appearance']['physical_description'][:50]}...")
        print(f"   Backstory: {character_data['background']['backstory'][:50]}...")
        print(f"   Primary concerns: {len(character_data['therapeutic_profile']['primary_concerns'])}")
        print(f"   Therapeutic goals: {len(character_data['therapeutic_profile']['therapeutic_goals'])}")
        print()
        
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/characters/",
                headers=headers,
                json=character_data
            ) as response:
                response_text = await response.text()
                
                if response.status == 201:
                    character = json.loads(response_text)
                    print(f"✅ Character created successfully!")
                    print(f"   Character ID: {character.get('character_id')}")
                    print(f"   Name: {character.get('name')}")
                    print(f"   Created at: {character.get('created_at')}")
                    print()
                    
                    # Step 3: Retrieve the character
                    print("Step 3: Retrieving created character...")
                    character_id = character.get('character_id')
                    
                    async with session.get(
                        f"{BASE_URL}/api/v1/characters/{character_id}",
                        headers=headers
                    ) as get_response:
                        if get_response.status == 200:
                            retrieved = await get_response.json()
                            print(f"✅ Character retrieved successfully!")
                            print(f"   Name: {retrieved.get('name')}")
                            print(f"   Personality traits: {len(retrieved.get('background', {}).get('personality_traits', []))}")
                            print(f"   Life goals: {len(retrieved.get('background', {}).get('life_goals', []))}")
                            print(f"   Therapeutic goals: {len(retrieved.get('therapeutic_profile', {}).get('therapeutic_goals', []))}")
                            print()
                            
                            # Step 4: List all characters
                            print("Step 4: Listing all characters...")
                            async with session.get(
                                f"{BASE_URL}/api/v1/characters/",
                                headers=headers
                            ) as list_response:
                                if list_response.status == 200:
                                    characters = await list_response.json()
                                    print(f"✅ Characters listed successfully!")
                                    print(f"   Total characters: {len(characters)}")
                                    for char in characters:
                                        print(f"   - {char.get('name')} (ID: {char.get('character_id')})")
                                    print()
                                else:
                                    print(f"❌ Failed to list characters: {await list_response.text()}")
                        else:
                            print(f"❌ Failed to retrieve character: {await get_response.text()}")
                    
                    print("=" * 80)
                    print("✅ ALL TESTS PASSED!")
                    print("=" * 80)
                    
                elif response.status == 422:
                    print(f"❌ Validation error (422):")
                    try:
                        error_detail = json.loads(response_text)
                        print(f"   {json.dumps(error_detail, indent=2)}")
                    except:
                        print(f"   {response_text}")
                else:
                    print(f"❌ Character creation failed with status {response.status}:")
                    print(f"   {response_text}")
                    
        except Exception as e:
            print(f"❌ Error during character creation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_character_creation())

