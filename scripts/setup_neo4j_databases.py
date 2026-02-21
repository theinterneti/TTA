#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Setup_neo4j_databases]]
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

    driver = GraphDatabase.driver(uri, auth=(username, password))

    try:
        # Must use system database to create new databases
        with driver.session(database="system") as session:
            databases = ["tta_dev", "tta_staging", "tta_test"]

            for db_name in databases:
                try:
                    session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        pass
                    else:
                        pass

            # Show all databases
            result = session.run("SHOW DATABASES")
            for record in result:
                record["name"]
                record["currentStatus"]

    finally:
        driver.close()


if __name__ == "__main__":
    setup_databases()
