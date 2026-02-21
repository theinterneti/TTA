# Logseq: [[TTA.dev/Scripts/Test_database_connections]]
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
        return False

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        client = redis.from_url(redis_url, decode_responses=True)
        client.info("server")

        # Test basic operations
        client.set("test:connection", "OK", ex=60)
        value = client.get("test:connection")

        if value == "OK":
            pass

        # Show some stats
        client.dbsize()

        # Show sample keys by namespace
        all_keys = client.keys("*")
        namespaces = {}
        for key in all_keys[:100]:  # Limit to first 100
            namespace = key.split(":")[0] if ":" in key else "no-namespace"
            namespaces[namespace] = namespaces.get(namespace, 0) + 1

        for _ns, _count in sorted(namespaces.items(), key=lambda x: x[1], reverse=True):
            pass

        client.close()
        return True

    except redis.ConnectionError:
        return False
    except Exception:
        return False


def test_neo4j_connection() -> bool:
    """Test Neo4j connection and display info."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        return False

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tta_dev_password_2024")

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Test connection
            result = session.run("RETURN 1 as test")
            test_value = result.single()[0]

            if test_value == 1:
                # Get database info
                result = session.run(
                    "CALL dbms.components() YIELD name, versions, edition"
                )
                result.single()

                # Count nodes by label
                result = session.run("""
                    MATCH (n)
                    RETURN labels(n) as labels, count(n) as count
                    ORDER BY count DESC
                    LIMIT 10
                """)

                records = list(result)
                if records:
                    for record in records:
                        (
                            ", ".join(record["labels"])
                            if record["labels"]
                            else "no-label"
                        )
                else:
                    pass

                # Count relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                result.single()["count"]

        driver.close()
        return True

    except Exception:
        return False


def check_docker_services() -> None:
    """Check if Docker services are running."""
    import subprocess

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
            for line in result.stdout.strip().split("\n"):
                name, status = line.split("\t")
        else:
            pass

    except subprocess.CalledProcessError:
        pass
    except FileNotFoundError:
        pass


def main():
    """Run all database connection tests."""

    check_docker_services()

    redis_ok = test_redis_connection()
    neo4j_ok = test_neo4j_connection()

    if redis_ok and neo4j_ok:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
