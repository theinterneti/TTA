#!/usr/bin/env python3
"""
Setup Neo4j databases for different environments.

Creates separate databases within a single Neo4j instance for:
- Development (tta_dev)
- Staging (tta_staging)
- Testing (tta_test)

Usage:
    uv run python scripts/setup_neo4j_databases.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from neo4j import GraphDatabase


def setup_databases():
    """Create separate databases for each environment."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "tta_password_2024")

    print(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(username, password))

    try:
        # Must use system database to create new databases
        with driver.session(database="system") as session:
            databases = ["tta_dev", "tta_staging", "tta_test"]

            for db_name in databases:
                try:
                    print(f"\nCreating database: {db_name}")
                    session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
                    print(f"✅ Database '{db_name}' created successfully")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"ℹ️  Database '{db_name}' already exists")
                    else:
                        print(f"❌ Error creating database '{db_name}': {e}")

            # Show all databases
            print("\n" + "=" * 60)
            print("Available databases:")
            print("=" * 60)
            result = session.run("SHOW DATABASES")
            for record in result:
                name = record["name"]
                status = record["currentStatus"]
                print(f"  {name:20} - {status}")

        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print("\nUsage examples:")
        print("\nPython:")
        print('  session = driver.session(database="tta_dev")')
        print('  session = driver.session(database="tta_staging")')
        print("\nCypher (in Neo4j Browser):")
        print("  :use tta_dev")
        print("  :use tta_staging")

    finally:
        driver.close()


if __name__ == "__main__":
    setup_databases()
