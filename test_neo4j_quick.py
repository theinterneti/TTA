#!/usr/bin/env python3
"""Quick Neo4j connection test."""

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
password = "dev_password_2024"

print(f"Testing Neo4j connection to {uri}")
print(f"Using password: {password}")

driver = GraphDatabase.driver(uri, auth=("neo4j", password))
try:
    driver.verify_connectivity()
    print("✅ Neo4j connection successful!")

    with driver.session() as session:
        result = session.run("RETURN 1 as num, 'Hello from Neo4j' as msg")
        record = result.single()
        print(f"✅ Query test: {record['num']}, {record['msg']}")

        # Get version
        result = session.run("CALL dbms.components() YIELD name, versions, edition")
        component = result.single()
        print(f"✅ Neo4j {component['edition']}: {component['versions'][0]}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
finally:
    driver.close()
