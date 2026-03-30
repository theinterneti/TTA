#!/usr/bin/env python3
"""Quick Neo4j connection test"""

# Logseq: [[TTA.dev/Scripts/Quick_neo4j_test]]

import sys

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "dev_password_2024"


try:
    driver = GraphDatabase.driver(uri, auth=(username, password))

    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run("RETURN 'Hello from Neo4j!' AS message")
        record = result.single()

    driver.close()
    sys.exit(0)

except Exception:
    sys.exit(1)
