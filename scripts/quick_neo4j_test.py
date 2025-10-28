#!/usr/bin/env python3
"""Quick Neo4j connection test"""

import sys

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "dev_password_2024"

print(f"Testing connection to {uri}...")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    print("✅ Driver created")

    driver.verify_connectivity()
    print("✅ Connectivity verified")

    with driver.session() as session:
        result = session.run("RETURN 'Hello from Neo4j!' AS message")
        record = result.single()
        print(f"✅ Query result: {record['message']}")

    driver.close()
    print("✅ Connection successful!")
    sys.exit(0)

except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)
