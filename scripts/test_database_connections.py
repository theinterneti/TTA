# ruff: noqa: ALL
#!/usr/bin/env python3
"""
TTA Database Connection Tester

Tests connections to Redis and Neo4j databases and displays useful diagnostic info.
Works with VS Code database panel configuration.
"""

import os
import sys


def test_redis_connection() -> bool:
    """Test Redis connection and display info."""
    try:
        import redis
    except ImportError:
        print("❌ Redis library not installed. Run: uv add redis")
        return False

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print("\n🔴 Testing Redis Connection")
    print(f"   URL: {redis_url}")

    try:
        client = redis.from_url(redis_url, decode_responses=True)
        info = client.info("server")

        print("   ✅ Connected successfully!")
        print(f"   📊 Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"   💾 Used Memory: {info.get('used_memory_human', 'unknown')}")

        # Test basic operations
        client.set("test:connection", "OK", ex=60)
        value = client.get("test:connection")

        if value == "OK":
            print("   ✅ Read/Write test passed")

        # Show some stats
        db_size = client.dbsize()
        print(f"   🔢 Keys in database: {db_size}")

        # Show sample keys by namespace
        print("\n   📋 Key Namespaces:")
        all_keys = client.keys("*")
        namespaces = {}
        for key in all_keys[:100]:  # Limit to first 100
            namespace = key.split(":")[0] if ":" in key else "no-namespace"
            namespaces[namespace] = namespaces.get(namespace, 0) + 1

        for ns, count in sorted(namespaces.items(), key=lambda x: x[1], reverse=True):
            print(f"      {ns}: {count} keys")

        client.close()
        return True

    except redis.ConnectionError as e:
        print(f"   ❌ Connection failed: {e}")
        print(
            "   💡 Ensure Redis is running: docker-compose -f docker-compose.dev.yml up -d redis"
        )
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_neo4j_connection() -> bool:
    """Test Neo4j connection and display info."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("❌ Neo4j library not installed. Run: uv add neo4j")
        return False

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tta_dev_password_2024")

    print("\n🗄️  Testing Neo4j Connection")
    print(f"   URI: {uri}")
    print(f"   User: {user}")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Test connection
            result = session.run("RETURN 1 as test")
            test_value = result.single()[0]

            if test_value == 1:
                print("   ✅ Connected successfully!")

                # Get database info
                result = session.run(
                    "CALL dbms.components() YIELD name, versions, edition"
                )
                component = result.single()
                print(f"   📊 Neo4j Edition: {component['edition']}")
                print(f"   📊 Version: {component['versions'][0]}")

                # Count nodes by label
                result = session.run("""
                    MATCH (n)
                    RETURN labels(n) as labels, count(n) as count
                    ORDER BY count DESC
                    LIMIT 10
                """)

                print("\n   📋 Node Statistics:")
                records = list(result)
                if records:
                    for record in records:
                        labels = (
                            ", ".join(record["labels"])
                            if record["labels"]
                            else "no-label"
                        )
                        print(f"      {labels}: {record['count']} nodes")
                else:
                    print("      (empty database)")

                # Count relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rel_count = result.single()["count"]
                print(f"\n   🔗 Total Relationships: {rel_count}")

        driver.close()
        return True

    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print(
            "   💡 Ensure Neo4j is running: docker-compose -f docker-compose.dev.yml up -d neo4j"
        )
        print("   💡 Wait 30-40s for Neo4j to fully start")
        return False


def check_docker_services() -> None:
    """Check if Docker services are running."""
    import subprocess

    print("\n🐳 Checking Docker Services")

    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=tta-dev",
                "--format",
                "{{.Names}}\t{{.Status}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            print("   ✅ Docker services running:")
            for line in result.stdout.strip().split("\n"):
                name, status = line.split("\t")
                print(f"      {name}: {status}")
        else:
            print("   ⚠️  No TTA Docker services running")
            print(
                "   💡 Start services: docker-compose -f docker-compose.dev.yml up -d"
            )

    except subprocess.CalledProcessError:
        print("   ❌ Docker not available or error running docker ps")
    except FileNotFoundError:
        print("   ❌ Docker not installed")


def main():
    """Run all database connection tests."""
    print("=" * 60)
    print("🧪 TTA Database Connection Test")
    print("=" * 60)

    check_docker_services()

    redis_ok = test_redis_connection()
    neo4j_ok = test_neo4j_connection()

    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"   Redis:  {'✅ OK' if redis_ok else '❌ FAILED'}")
    print(f"   Neo4j:  {'✅ OK' if neo4j_ok else '❌ FAILED'}")

    if redis_ok and neo4j_ok:
        print("\n✅ All database connections are working!")
        print("   You can now use the VS Code database panels:")
        print("   - Click 🗄️  icon for Neo4j")
        print("   - Click 🔴 icon for Redis")
        return 0
    print("\n❌ Some database connections failed")
    print("   See error messages above for troubleshooting")
    return 1


if __name__ == "__main__":
    sys.exit(main())
