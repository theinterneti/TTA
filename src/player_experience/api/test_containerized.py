#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Player_experience/Api/Test_containerized]]
Test script for containerized TTA API connectivity
"""

import asyncio
import os
import sys

import psycopg2  # type: ignore[import-untyped]
import redis
from neo4j import GraphDatabase


async def test_database_connections():
    """Test connections to all database services"""
    results = {}

    # Test PostgreSQL
    try:
        postgres_conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "tta-staging-postgres"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "tta_staging"),
            user=os.getenv("POSTGRES_USER", "tta_staging_user"),
            password=os.getenv(
                "POSTGRES_PASSWORD", "staging_postgres_secure_pass_2024"
            ),
        )
        postgres_conn.close()
        results["postgresql"] = "✅ Connected successfully"
    except Exception as e:
        results["postgresql"] = f"❌ Connection failed: {e}"

    # Test Redis
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "tta-staging-redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", "staging_redis_secure_pass_2024"),
            decode_responses=True,
        )
        redis_client.ping()
        redis_client.close()
        results["redis"] = "✅ Connected successfully"
    except Exception as e:
        results["redis"] = f"❌ Connection failed: {e}"

    # Test Neo4j
    try:
        neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://tta-staging-neo4j:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "staging_neo4j_secure_pass_2024"),
            ),
        )
        neo4j_driver.verify_connectivity()
        neo4j_driver.close()
        results["neo4j"] = "✅ Connected successfully"
    except Exception as e:
        results["neo4j"] = f"❌ Connection failed: {e}"

    return results


async def test_app_import():
    """Test if the app can be imported without errors"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, "/app")

        # Try to import the app
        from app import app

        return f"✅ App imported successfully: {app}"
    except Exception as e:
        return f"❌ App import failed: {e}"


async def main():
    """Main test function"""

    # Test app import
    app_result = await test_app_import()

    # Test database connections
    db_results = await test_database_connections()

    for _service, _result in db_results.items():
        pass

    # Summary
    all_success = all(
        "✅" in result for result in [app_result] + list(db_results.values())
    )

    if all_success:
        return 0
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
