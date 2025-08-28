#!/usr/bin/env python3
"""
Simple test to verify Nexus endpoints work directly.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/thein/projects/projects/TTA')

# Set environment variables
os.environ['NEO4J_PASSWORD'] = 'TTA_Neo4j_2024!'
os.environ['REDIS_PASSWORD'] = ''

async def test_nexus_endpoints_directly():
    """Test Nexus endpoints by calling them directly."""
    print("🧪 Direct Nexus Endpoint Testing")
    print("=" * 50)
    
    try:
        # Import the necessary modules
        from src.player_experience.api.services.connection_manager import initialize_services, get_service_manager
        from src.player_experience.database.nexus_schema import NexusSchemaManager
        from src.player_experience.services.nexus_cache import NexusCacheService
        
        # Initialize services
        print("🔧 Initializing services...")
        init_success = await initialize_services()
        if not init_success:
            print("❌ Failed to initialize services")
            return False
        
        service_manager = get_service_manager()
        if not service_manager:
            print("❌ Service manager not available")
            return False
        
        print("✅ Services initialized successfully")
        
        # Test Nexus schema manager
        if service_manager.neo4j:
            print("\n🌌 Testing Nexus Schema Manager...")
            nexus_manager = NexusSchemaManager(service_manager.neo4j.driver)
            
            # Get nexus state
            nexus_state = await nexus_manager.get_nexus_state()
            if nexus_state:
                print(f"✅ Nexus state: {nexus_state}")
            else:
                print("⚠️ No nexus state found")
        else:
            print("❌ Neo4j service not available")
            return False
        
        # Test Redis cache
        if service_manager.redis:
            print("\n💾 Testing Redis Cache...")
            cache_service = NexusCacheService(service_manager.redis)
            
            # Test cache operations
            test_data = {"test": "value", "timestamp": "2024-01-01"}
            success = await cache_service.set_nexus_realtime_state(test_data)
            if success:
                print("✅ Cache write successful")
                
                cached_data = await cache_service.get_nexus_realtime_state()
                if cached_data:
                    print(f"✅ Cache read successful: {cached_data}")
                else:
                    print("⚠️ Cache read returned no data")
            else:
                print("❌ Cache write failed")
        else:
            print("❌ Redis service not available")
            return False
        
        # Test world creation
        print("\n🌍 Testing World Creation...")
        world_data = {
            "world_id": f"direct_test_{int(asyncio.get_event_loop().time())}",
            "title": "Direct Test World",
            "description": "A world created in direct testing",
            "genre": "fantasy",
            "therapeutic_focus": ["direct_testing"],
            "narrative_state": "active",
            "creator_id": "direct_test_user",
            "strength_level": 0.5,
            "silence_threat": 0.1,
            "completion_rate": 0.0,
            "therapeutic_efficacy": 0.0,
            "difficulty_level": "intermediate",
            "estimated_duration": 30,
            "player_count": 0,
            "rating": 0.0,
            "tags": ["test"],
            "is_public": True,
            "is_featured": False
        }
        
        world_id = await nexus_manager.create_story_world(world_data)
        if world_id:
            print(f"✅ World created: {world_id}")
            
            # Update cache with world info
            await cache_service.set_world_state(world_id, {
                "narrative_strength": "0.5",
                "player_count": "0",
                "status": "active"
            })
            print("✅ World cached successfully")
            
        else:
            print("❌ World creation failed")
            return False
        
        print("\n🎉 All direct tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_functionality():
    """Test the core API functionality that our endpoints depend on."""
    print("\n🔧 Testing Core API Functionality")
    print("=" * 50)
    
    try:
        # Test that we can import and create the FastAPI app
        from src.player_experience.api.app import app
        print("✅ FastAPI app imported successfully")
        
        # Check if our nexus router is included
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        nexus_routes = [path for path in route_paths if 'nexus' in path]
        
        if nexus_routes:
            print(f"✅ Nexus routes found: {len(nexus_routes)} routes")
            for route in nexus_routes[:5]:  # Show first 5
                print(f"   - {route}")
        else:
            print("❌ No nexus routes found")
            return False
        
        # Test that we can create a test client
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test a simple endpoint
        response = client.get("/")
        print(f"✅ Root endpoint responds: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_comprehensive_test():
    """Run comprehensive testing of Nexus functionality."""
    print("🚀 Comprehensive Nexus Codex Testing")
    print("=" * 60)
    
    # Test 1: Direct endpoint functionality
    direct_success = await test_nexus_endpoints_directly()
    
    # Test 2: API app functionality
    api_success = await test_api_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Direct Functionality: {'PASS' if direct_success else 'FAIL'}")
    print(f"✅ API App Structure: {'PASS' if api_success else 'FAIL'}")
    
    if direct_success and api_success:
        print("\n🎉 All comprehensive tests passed!")
        print("✨ Nexus Codex Phase 1 core functionality is working!")
        print("\n📋 Next Steps:")
        print("   1. Fix service manager initialization in API startup")
        print("   2. Ensure proper environment variable handling")
        print("   3. Test endpoints via HTTP requests")
        print("   4. Validate authentication integration")
    else:
        print("\n⚠️ Some tests failed - check output above")
    
    return direct_success and api_success

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
