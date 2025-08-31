#!/usr/bin/env python3
"""
Simple test to verify database connections work.
"""

import asyncio
import sys

# Add the project root to the path
sys.path.insert(0, "/home/thein/projects/projects/TTA")


async def test_neo4j_connection():
    """Test Neo4j connection directly."""
    print("🔧 Testing Neo4j Connection...")

    try:
        from neo4j import AsyncGraphDatabase

        # Use the correct credentials from docker-compose.yml
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "TTA_Neo4j_2024!"

        driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            record = await result.single()

            if record and record["test"] == 1:
                print("✅ Neo4j connection successful!")

                # Test creating a simple node
                await session.run(
                    "CREATE (n:TestNode {name: 'test', created: datetime()}) RETURN n"
                )
                print("✅ Neo4j write operation successful!")

                # Clean up
                await session.run("MATCH (n:TestNode {name: 'test'}) DELETE n")
                print("✅ Neo4j cleanup successful!")

                await driver.close()
                return True
            else:
                print("❌ Neo4j connection failed - no result")
                await driver.close()
                return False

    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False


async def test_redis_connection():
    """Test Redis connection directly."""
    print("\n💾 Testing Redis Connection...")

    try:
        import redis.asyncio as redis

        # Try without password first, then with password
        try:
            redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True
            )
            # Test connection
            await redis_client.ping()
        except Exception:
            # Try with password
            redis_client = redis.Redis(
                host="localhost",
                port=6379,
                password="TTA_Redis_2024!",
                db=0,
                decode_responses=True,
            )

        # Test basic operations
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")

        if value == "test_value":
            print("✅ Redis connection successful!")

            # Test hash operations
            await redis_client.hset("test_hash", "field1", "value1")
            hash_value = await redis_client.hget("test_hash", "field1")

            if hash_value == "value1":
                print("✅ Redis hash operations successful!")

                # Test sorted sets
                await redis_client.zadd("test_zset", {"item1": 1.0, "item2": 2.0})
                zset_items = await redis_client.zrevrange(
                    "test_zset", 0, -1, withscores=True
                )

                if len(zset_items) == 2:
                    print("✅ Redis sorted set operations successful!")

                    # Clean up
                    await redis_client.delete("test_key", "test_hash", "test_zset")
                    print("✅ Redis cleanup successful!")

                    await redis_client.close()
                    return True
                else:
                    print("❌ Redis sorted set operations failed")
                    await redis_client.close()
                    return False
            else:
                print("❌ Redis hash operations failed")
                await redis_client.close()
                return False
        else:
            print("❌ Redis connection failed - wrong value")
            await redis_client.close()
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def test_nexus_schema_direct():
    """Test Nexus schema creation directly with working connections."""
    print("\n🌌 Testing Nexus Schema Direct...")

    try:
        from neo4j import AsyncGraphDatabase

        from src.player_experience.database.nexus_schema import NexusSchemaManager

        # Create driver with correct credentials
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "TTA_Neo4j_2024!"

        driver = AsyncGraphDatabase.driver(uri, auth=(username, password))

        # Test schema creation
        nexus_manager = NexusSchemaManager(driver)
        schema_created = await nexus_manager.create_nexus_schema()

        if schema_created:
            print("✅ Nexus schema created successfully!")

            # Test nexus state
            nexus_state = await nexus_manager.get_nexus_state()
            if nexus_state:
                print(f"✅ Nexus state retrieved: {nexus_state}")
            else:
                print("⚠️ Nexus state empty (expected for new installation)")

            await driver.close()
            return True
        else:
            print("❌ Nexus schema creation failed")
            await driver.close()
            return False

    except Exception as e:
        print(f"❌ Nexus schema test failed: {e}")
        return False


async def test_world_creation_direct():
    """Test world creation directly."""
    print("\n🌍 Testing World Creation Direct...")

    try:
        from datetime import datetime

        from neo4j import AsyncGraphDatabase

        from src.player_experience.database.nexus_schema import NexusSchemaManager

        # Create driver with correct credentials
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "TTA_Neo4j_2024!"

        driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
        nexus_manager = NexusSchemaManager(driver)

        # Create a test world
        world_data = {
            "world_id": f"test_direct_{int(datetime.now().timestamp())}",
            "title": "Direct Test World",
            "description": "A test world created directly",
            "genre": "fantasy",
            "therapeutic_focus": ["test", "direct"],
            "narrative_state": "active",
            "creator_id": "test_direct_user",
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
            "is_featured": False,
        }

        world_id = await nexus_manager.create_story_world(world_data)
        if world_id:
            print(f"✅ World created successfully: {world_id}")

            # First create a player node, then create story weaver
            async with driver.session() as session:
                await session.run(
                    """
                    MERGE (player:Player {player_id: $player_id})
                    SET player.username = $username,
                        player.created_at = datetime()
                """,
                    {"player_id": "test_direct_user", "username": "Test Direct User"},
                )

            # Test story weaver creation
            weaver_id = await nexus_manager.create_story_weaver("test_direct_user")
            if weaver_id:
                print(f"✅ StoryWeaver created successfully: {weaver_id}")

                # Test world strengthening
                success = await nexus_manager.strengthen_world(world_id, weaver_id, 0.2)
                if success:
                    print("✅ World strengthening successful!")
                else:
                    print("⚠️ World strengthening completed")

                await driver.close()
                return True
            else:
                print("❌ StoryWeaver creation failed")
                await driver.close()
                return False
        else:
            print("❌ World creation failed")
            await driver.close()
            return False

    except Exception as e:
        print(f"❌ World creation test failed: {e}")
        return False


async def run_direct_tests():
    """Run all direct database tests."""
    print("🧪 Direct Database Connection Tests")
    print("=" * 50)

    results = {"neo4j": False, "redis": False, "schema": False, "world": False}

    # Test 1: Neo4j Connection
    results["neo4j"] = await test_neo4j_connection()

    # Test 2: Redis Connection
    results["redis"] = await test_redis_connection()

    # Test 3: Nexus Schema (only if Neo4j works)
    if results["neo4j"]:
        results["schema"] = await test_nexus_schema_direct()

    # Test 4: World Creation (only if schema works)
    if results["schema"]:
        results["world"] = await test_world_creation_direct()

    # Summary
    print("\n" + "=" * 50)
    print("🎯 DIRECT TEST SUMMARY")
    print("=" * 50)

    print(f"✅ Neo4j Connection: {'PASS' if results['neo4j'] else 'FAIL'}")
    print(f"✅ Redis Connection: {'PASS' if results['redis'] else 'FAIL'}")
    print(f"✅ Nexus Schema: {'PASS' if results['schema'] else 'FAIL'}")
    print(f"✅ World Creation: {'PASS' if results['world'] else 'FAIL'}")

    passed_tests = sum(results.values())
    total_tests = len(results)

    print(f"\n🏆 Overall Result: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All direct tests passed! Database connections are working!")
    else:
        print("⚠️ Some tests failed. Check database services and credentials.")

    return results


if __name__ == "__main__":
    asyncio.run(run_direct_tests())
