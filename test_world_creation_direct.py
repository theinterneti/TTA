#!/usr/bin/env python3
"""
Direct test of world creation functionality.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/thein/projects/projects/TTA')

# Set environment variables
os.environ['NEO4J_PASSWORD'] = 'TTA_Neo4j_2024!'
os.environ['REDIS_PASSWORD'] = ''

async def test_world_creation_direct():
    """Test world creation by calling the endpoint function directly."""
    print("🧪 Direct World Creation Test")
    print("=" * 50)
    
    try:
        # Import required modules
        from src.player_experience.api.services.connection_manager import initialize_services, get_service_manager
        from src.player_experience.models.nexus import WorldCreationRequest, GenreType, DifficultyLevel
        from src.player_experience.api.auth import TokenData
        from src.player_experience.database.nexus_schema import NexusSchemaManager
        
        # Initialize services
        print("🔧 Initializing services...")
        init_success = await initialize_services()
        if not init_success:
            print("❌ Failed to initialize services")
            return False
        
        service_manager = get_service_manager()
        print("✅ Services initialized")
        
        # Create a mock TokenData for testing
        mock_player = TokenData(
            player_id="test_direct_player_123",
            username="direct_test_user",
            email="direct@test.com",
            role="player",
            permissions=["create_world"],
            session_id="test_session",
            mfa_verified=False
        )
        
        # Create WorldCreationRequest
        world_request = WorldCreationRequest(
            title="Direct Test World",
            description="A world created through direct testing",
            genre=GenreType.FANTASY,
            therapeutic_focus=["direct_testing", "validation"],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_duration=30,
            is_public=True
        )
        
        print(f"✅ World request created: {world_request.title}")
        
        # Test the world creation logic directly
        nexus_manager = NexusSchemaManager(service_manager.neo4j.driver)
        
        # Prepare world data (similar to what the endpoint does)
        from datetime import datetime
        world_data = {
            "world_id": f"direct_test_{int(datetime.now().timestamp())}",
            "title": world_request.title,
            "description": world_request.description,
            "genre": world_request.genre.value,
            "therapeutic_focus": world_request.therapeutic_focus,
            "narrative_state": "active",
            "creator_id": mock_player.player_id,
            "strength_level": 0.5,
            "silence_threat": 0.1,
            "completion_rate": 0.0,
            "therapeutic_efficacy": 0.0,
            "difficulty_level": world_request.difficulty_level.value,
            "estimated_duration": world_request.estimated_duration,
            "player_count": 0,
            "rating": 0.0,
            "tags": [],
            "is_public": world_request.is_public,
            "is_featured": False
        }
        
        # Create the world
        world_id = await nexus_manager.create_story_world(world_data)
        
        if world_id:
            print(f"✅ World created successfully: {world_id}")
            
            # Test caching
            from src.player_experience.services.nexus_cache import NexusCacheService
            cache_service = NexusCacheService(service_manager.redis)
            
            await cache_service.set_world_state(world_id, {
                "narrative_strength": str(world_data["strength_level"]),
                "player_count": "0",
                "current_events": "[]",
                "creation_status": "ready"
            })
            print("✅ World cached successfully")
            
            # Test world retrieval
            async with service_manager.neo4j.driver.session() as session:
                result = await session.run("""
                    MATCH (world:StoryWorld {world_id: $world_id})
                    RETURN world.title as title, world.genre as genre, world.creator_id as creator
                """, {"world_id": world_id})
                
                record = await result.single()
                if record:
                    print(f"✅ World retrieved: {record['title']} ({record['genre']}) by {record['creator']}")
                else:
                    print("⚠️ World not found in database")
            
            return world_id
        else:
            print("❌ World creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Direct world creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_endpoint_simulation():
    """Simulate the actual endpoint call."""
    print("\n🌐 Endpoint Simulation Test")
    print("=" * 50)
    
    try:
        # Import the actual endpoint function
        from src.player_experience.api.routers.nexus import create_world
        from src.player_experience.api.services.connection_manager import get_service_manager
        from src.player_experience.models.nexus import WorldCreationRequest, GenreType, DifficultyLevel
        from src.player_experience.api.auth import TokenData
        
        # Create test data
        world_request = WorldCreationRequest(
            title="Endpoint Simulation World",
            description="A world created through endpoint simulation",
            genre=GenreType.SCI_FI,
            therapeutic_focus=["endpoint_testing", "simulation"],
            difficulty_level=DifficultyLevel.ADVANCED,
            estimated_duration=45,
            is_public=True
        )
        
        mock_player = TokenData(
            player_id="endpoint_test_player_456",
            username="endpoint_test_user",
            email="endpoint@test.com",
            role="player",
            permissions=["create_world"],
            session_id="endpoint_test_session",
            mfa_verified=False
        )
        
        service_manager = get_service_manager()
        
        # Call the endpoint function directly
        result = await create_world(world_request, mock_player, service_manager)
        
        if result and result.get("world_id"):
            print(f"✅ Endpoint simulation successful: {result['world_id']}")
            print(f"   - Title: {result.get('title')}")
            print(f"   - Creator: {result.get('creator_id')}")
            print(f"   - Status: {result.get('creation_status')}")
            return result["world_id"]
        else:
            print(f"❌ Endpoint simulation failed: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Endpoint simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_comprehensive_world_test():
    """Run comprehensive world creation tests."""
    print("🚀 Comprehensive World Creation Testing")
    print("=" * 60)
    
    # Test 1: Direct world creation
    direct_world_id = await test_world_creation_direct()
    
    # Test 2: Endpoint simulation
    endpoint_world_id = await test_endpoint_simulation()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 WORLD CREATION TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Direct Creation: {'PASS' if direct_world_id else 'FAIL'}")
    print(f"✅ Endpoint Simulation: {'PASS' if endpoint_world_id else 'FAIL'}")
    
    if direct_world_id and endpoint_world_id:
        print("\n🎉 All world creation tests passed!")
        print("✨ World creation functionality is working correctly!")
        print(f"\n📋 Created Worlds:")
        print(f"   - Direct: {direct_world_id}")
        print(f"   - Endpoint: {endpoint_world_id}")
    else:
        print("\n⚠️ Some world creation tests failed")
    
    return direct_world_id and endpoint_world_id

if __name__ == "__main__":
    asyncio.run(run_comprehensive_world_test())
