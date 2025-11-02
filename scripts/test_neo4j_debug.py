#!/usr/bin/env python3
"""Debug Neo4j connection - check protocol support."""

import logging

from neo4j import GraphDatabase, basic_auth

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "tta_dev_neo4j_2024"

print(f"Connecting to {NEO4J_URI} as {NEO4J_USER}...")

try:
    # Try with explicit basic_auth
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
    )

    print("Driver created, verifying connectivity...")
    driver.verify_connectivity()
    print("✅ Connectivity verified!")

    # Try a simple query
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        record = result.single()
        print(f"Query result: {record['num']}")

    driver.close()
    print("\n✅ SUCCESS!")

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback

    traceback.print_exc()
