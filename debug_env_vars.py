#!/usr/bin/env python3
"""
Debug script to check environment variables and mock service logic.
"""

import os


def debug_environment():
    """Debug environment variables and mock service logic."""
    print("🔍 Environment Variables Debug")
    print("=" * 50)

    # Check key environment variables
    env_vars = [
        "TTA_USE_MOCKS",
        "TTA_DEVELOPMENT_MODE",
        "TTA_USE_NEO4J",
        "TTA_USE_REDIS",
        "NEO4J_URI",
        "REDIS_URL",
        "JWT_SECRET_KEY",
    ]

    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        print(f"   {var}: {value}")

    print("\n🧪 Mock Service Logic Test:")

    # Test is_development_mode
    dev_mode = os.getenv("TTA_DEVELOPMENT_MODE", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    print(f"   is_development_mode(): {dev_mode}")

    # Test TTA_USE_MOCKS
    use_mocks_env = os.getenv("TTA_USE_MOCKS", "false").lower() in ("true", "1", "yes")
    print(f"   TTA_USE_MOCKS check: {use_mocks_env}")

    # Test TTA_USE_NEO4J
    use_neo4j = os.getenv("TTA_USE_NEO4J", "0") == "1"
    print(f"   TTA_USE_NEO4J == '1': {use_neo4j}")

    # Test should_use_mocks logic
    should_use_mocks = dev_mode or use_mocks_env or not use_neo4j
    print(f"   should_use_mocks(): {should_use_mocks}")

    print("\n🔧 Recommendations:")
    if should_use_mocks:
        print("   ❌ System will use mock services")
        if dev_mode:
            print("   - TTA_DEVELOPMENT_MODE is true")
        if use_mocks_env:
            print("   - TTA_USE_MOCKS is true")
        if not use_neo4j:
            print("   - TTA_USE_NEO4J is not '1'")
    else:
        print("   ✅ System should use live databases")

    # Test database connectivity
    print("\n🔌 Database Connectivity Test:")
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, password="TTA_Redis_2024!")
        ping_result = r.ping()
        print(f"   Redis connection: {'✅ SUCCESS' if ping_result else '❌ FAILED'}")
    except Exception as e:
        print(f"   Redis connection: ❌ FAILED - {e}")

    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "TTA_Neo4j_2024!")
        )
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_result = result.single()
        driver.close()
        print(f"   Neo4j connection: {'✅ SUCCESS' if test_result else '❌ FAILED'}")
    except Exception as e:
        print(f"   Neo4j connection: ❌ FAILED - {e}")


if __name__ == "__main__":
    debug_environment()
