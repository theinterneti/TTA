#!/usr/bin/env python3
"""Debug Neo4j connection - check protocol support."""

# Logseq: [[TTA.dev/Scripts/Test_neo4j_debug]]

import logging

from neo4j import GraphDatabase, basic_auth

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "tta_dev_neo4j_2024"


try:
    # Try with explicit basic_auth
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
    )

    driver.verify_connectivity()

    # Try a simple query
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        record = result.single()

    driver.close()

except Exception:
    import traceback

    traceback.print_exc()
