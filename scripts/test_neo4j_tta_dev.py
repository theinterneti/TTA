#!/usr/bin/env python3
"""Quick Neo4j connection test with correct TTA dev credentials."""

# Logseq: [[TTA.dev/Scripts/Test_neo4j_tta_dev]]

import sys

from neo4j import GraphDatabase

# TTA Dev credentials from docker-compose.tta-dev.yml
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "tta_dev_neo4j_2024"  # Correct password from .env.tta-dev


try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    # Verify connection
    with driver.session() as session:
        result = session.run("RETURN 'Hello, Neo4j!' AS message, 1 AS number")
        record = result.single()

        # Get version
        version_result = session.run(
            "CALL dbms.components() YIELD versions RETURN versions[0] AS version"
        )
        version = version_result.single()["version"]

        # Count nodes
        count_result = session.run("MATCH (n) RETURN count(n) AS nodeCount")
        node_count = count_result.single()["nodeCount"]

    driver.close()
    sys.exit(0)

except Exception:
    sys.exit(1)
