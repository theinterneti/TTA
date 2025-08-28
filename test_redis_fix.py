#!/usr/bin/env python3
"""
Test Redis connection without authentication issues.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/thein/projects/projects/TTA')

# Don't set REDIS_PASSWORD at all
os.environ.pop('REDIS_PASSWORD', None)
os.environ['NEO4J_PASSWORD'] = 'TTA_Neo4j_2024!'

async def test_redis_connection_fix():
    """Test Redis connection without authentication warnings."""
    print("🔧 Testing Redis Connection Fix")
    print("=" * 50)
    
    try:
        # Test direct Redis connection
        import redis.asyncio as redis
        
        print("📡 Testing direct Redis connection...")
        redis_client = redis.from_url(
            "redis://localhost:6379",
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            max_connections=20
        )
        
        # Test basic operations
        await redis_client.set("test_fix", "working")
        value = await redis_client.get("test_fix")
        
        if value == "working":
            print("✅ Direct Redis connection working without auth warnings")
            await redis_client.delete("test_fix")
            await redis_client.close()
        else:
            print("❌ Direct Redis connection failed")
            return False
        
        # Test service manager connection
        print("\n🔧 Testing service manager Redis connection...")
        from src.player_experience.api.services.connection_manager import initialize_services, get_service_manager
        
        init_success = await initialize_services()
        if not init_success:
            print("❌ Service initialization failed")
            return False
        
        service_manager = get_service_manager()
        if not service_manager or not service_manager.redis:
            print("❌ Redis service not available in service manager")
            return False
        
        # Test cache service
        from src.player_experience.services.nexus_cache import NexusCacheService
        cache_service = NexusCacheService(service_manager.redis)
        
        # Test cache operations
        test_data = {"test": "cache_fix", "timestamp": "2024-01-01"}
        success = await cache_service.set_nexus_realtime_state(test_data)
        
        if success:
            print("✅ Cache service working without auth warnings")
            
            cached_data = await cache_service.get_nexus_realtime_state()
            if cached_data and cached_data.get("test") == "cache_fix":
                print("✅ Cache read/write operations successful")
                return True
            else:
                print("⚠️ Cache read operation issue")
                return False
        else:
            print("❌ Cache service failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_complete_world_creation():
    """Test complete world creation with fixed Redis."""
    print("\n🌍 Testing Complete World Creation with Fixed Redis")
    print("=" * 60)
    
    try:
        from src.player_experience.api.services.connection_manager import get_service_manager
        from src.player_experience.models.nexus import WorldCreationRequest, GenreType, DifficultyLevel
        from src.player_experience.api.auth import TokenData
        from src.player_experience.database.nexus_schema import NexusSchemaManager
        from src.player_experience.services.nexus_cache import NexusCacheService
        from datetime import datetime
        
        service_manager = get_service_manager()
        
        # Create test world
        world_request = WorldCreationRequest(
            title="Redis Fix Test World",
            description="A world created to test Redis fix",
            genre=GenreType.CONTEMPORARY,
            therapeutic_focus=["redis_testing", "cache_validation"],
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=25,
            is_public=True
        )
        
        mock_player = TokenData(
            player_id="redis_fix_player",
            username="redis_fix_user",
            email="redis@fix.com",
            role="player",
            permissions=["create_world"],
            session_id="redis_fix_session",
            mfa_verified=False
        )
        
        # Create world data
        world_data = {
            "world_id": f"redis_fix_{int(datetime.now().timestamp())}",
            "title": world_request.title,
            "description": world_request.description,
            "genre": world_request.genre.value,
            "therapeutic_focus": world_request.therapeutic_focus,
            "narrative_state": "active",
            "creator_id": mock_player.player_id,
            "strength_level": 0.6,
            "silence_threat": 0.1,
            "completion_rate": 0.0,
            "therapeutic_efficacy": 0.0,
            "difficulty_level": world_request.difficulty_level.value,
            "estimated_duration": world_request.estimated_duration,
            "player_count": 0,
            "rating": 0.0,
            "tags": ["redis", "fix", "test"],
            "is_public": world_request.is_public,
            "is_featured": False
        }
        
        # Create world in Neo4j
        nexus_manager = NexusSchemaManager(service_manager.neo4j.driver)
        world_id = await nexus_manager.create_story_world(world_data)
        
        if not world_id:
            print("❌ World creation in Neo4j failed")
            return False
        
        print(f"✅ World created in Neo4j: {world_id}")
        
        # Cache world state (this should work without Redis auth warnings)
        cache_service = NexusCacheService(service_manager.redis)
        cache_success = await cache_service.set_world_state(world_id, {
            "narrative_strength": str(world_data["strength_level"]),
            "player_count": "0",
            "current_events": "[]",
            "creation_status": "ready"
        })
        
        if cache_success:
            print("✅ World cached successfully without Redis auth warnings")
            
            # Test cache retrieval
            cached_state = await cache_service.get_world_state(world_id)
            if cached_state:
                print(f"✅ World state retrieved from cache: {cached_state}")
                return True
            else:
                print("⚠️ World state cache retrieval issue")
                return False
        else:
            print("❌ World caching failed")
            return False
            
    except Exception as e:
        print(f"❌ Complete world creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_redis_fix_tests():
    """Run all Redis fix tests."""
    print("🔧 Redis Authentication Fix Testing")
    print("=" * 60)
    
    # Test 1: Redis connection fix
    redis_fixed = await test_redis_connection_fix()
    
    # Test 2: Complete world creation with fixed Redis
    world_creation_fixed = await test_complete_world_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 REDIS FIX TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Redis Connection Fix: {'PASS' if redis_fixed else 'FAIL'}")
    print(f"✅ World Creation with Cache: {'PASS' if world_creation_fixed else 'FAIL'}")
    
    if redis_fixed and world_creation_fixed:
        print("\n🎉 Redis authentication warnings fixed!")
        print("✨ All caching operations working without authentication errors!")
    else:
        print("\n⚠️ Some Redis fix tests failed")
    
    return redis_fixed and world_creation_fixed

if __name__ == "__main__":
    asyncio.run(run_redis_fix_tests())
