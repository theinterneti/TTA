#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Setup_neo4j_schema]]
Setup Neo4j Schema for TTA Living Worlds

This script sets up the required Neo4j constraints and indexes for the TTA system.
"""

import logging
import os
import sys

# Add the tta.prototype path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "tta.prototype"))

from database.neo4j_schema import Neo4jSchemaManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_schema():
    """Set up Neo4j schema constraints and indexes."""
    try:
        # Use the correct port from docker-compose.yml
        schema_manager = Neo4jSchemaManager(
            uri="bolt://localhost:7687", username="neo4j", password="password"
        )

        logger.info("Connecting to Neo4j...")
        schema_manager.connect()

        logger.info("Creating constraints...")
        constraints_created = schema_manager.create_constraints()

        if constraints_created:
            logger.info("✓ All constraints created successfully")
        else:
            logger.error("✗ Failed to create some constraints")
            return False

        logger.info("Creating indexes...")
        indexes_created = schema_manager.create_indexes()

        if indexes_created:
            logger.info("✓ All indexes created successfully")
        else:
            logger.error("✗ Failed to create some indexes")
            return False

        logger.info("Schema setup completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Schema setup failed: {e}")
        return False
    finally:
        if "schema_manager" in locals():
            schema_manager.disconnect()


if __name__ == "__main__":
    success = setup_schema()
    sys.exit(0 if success else 1)
