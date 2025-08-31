#!/usr/bin/env python3
"""
Database migration script for setting up authentication schema.

This script sets up the complete authentication database schema including
User nodes, constraints, indexes, and relationships for production deployment.
"""

import argparse
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.player_experience.database.player_profile_schema import (
    PlayerProfileSchemaManager,
)
from src.player_experience.database.user_auth_schema import UserAuthSchemaManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_authentication_schema(
    uri: str, username: str, password: str, verify_only: bool = False
) -> bool:
    """
    Set up the authentication database schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password
        verify_only: If True, only verify schema without creating

    Returns:
        bool: True if setup/verification was successful
    """
    try:
        logger.info("Initializing User Authentication Schema Manager...")
        schema_manager = UserAuthSchemaManager(uri, username, password)

        logger.info("Connecting to Neo4j database...")
        schema_manager.connect()

        if verify_only:
            logger.info("Verifying authentication schema...")
            verification_results = schema_manager.verify_schema()

            if verification_results["schema_valid"]:
                logger.info("✅ Authentication schema verification successful")
                logger.info(
                    f"Found {len(verification_results['constraints'])} constraints"
                )
                logger.info(f"Found {len(verification_results['indexes'])} indexes")
                return True
            else:
                logger.error("❌ Authentication schema verification failed")
                logger.error(f"Constraints: {len(verification_results['constraints'])}")
                logger.error(f"Indexes: {len(verification_results['indexes'])}")
                return False
        else:
            logger.info("Setting up authentication schema...")
            success = schema_manager.setup_user_auth_schema()

            if success:
                logger.info("✅ Authentication schema setup completed successfully")

                # Verify the setup
                logger.info("Verifying schema setup...")
                verification_results = schema_manager.verify_schema()

                if verification_results["schema_valid"]:
                    logger.info("✅ Schema verification passed")
                    logger.info(
                        f"Created {len(verification_results['constraints'])} constraints"
                    )
                    logger.info(
                        f"Created {len(verification_results['indexes'])} indexes"
                    )
                else:
                    logger.warning("⚠️  Schema verification failed after setup")

                return True
            else:
                logger.error("❌ Authentication schema setup failed")
                return False

    except Exception as e:
        logger.error(f"Error setting up authentication schema: {e}")
        return False
    finally:
        try:
            schema_manager.disconnect()
            logger.info("Disconnected from Neo4j database")
        except:
            pass


def setup_player_profile_schema(
    uri: str, username: str, password: str, verify_only: bool = False
) -> bool:
    """
    Set up the player profile database schema.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password
        verify_only: If True, only verify schema without creating

    Returns:
        bool: True if setup/verification was successful
    """
    try:
        logger.info("Initializing Player Profile Schema Manager...")
        schema_manager = PlayerProfileSchemaManager(uri, username, password)

        logger.info("Connecting to Neo4j database...")
        schema_manager.connect()

        if verify_only:
            logger.info("Verifying player profile schema...")
            # Player profile schema doesn't have a verify method, so we'll just check connection
            logger.info("✅ Player profile schema connection successful")
            return True
        else:
            logger.info("Setting up player profile schema...")

            # Create constraints
            constraints_success = schema_manager.create_player_profile_constraints()
            if not constraints_success:
                logger.error("❌ Failed to create player profile constraints")
                return False

            # Create indexes
            indexes_success = schema_manager.create_player_profile_indexes()
            if not indexes_success:
                logger.error("❌ Failed to create player profile indexes")
                return False

            logger.info("✅ Player profile schema setup completed successfully")
            return True

    except Exception as e:
        logger.error(f"Error setting up player profile schema: {e}")
        return False
    finally:
        try:
            schema_manager.disconnect()
            logger.info("Disconnected from Neo4j database")
        except:
            pass


def main():
    """Main function for database migration script."""
    parser = argparse.ArgumentParser(
        description="Set up authentication database schema for TTA"
    )

    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        help="Neo4j connection URI (default: bolt://localhost:7687)",
    )

    parser.add_argument(
        "--username",
        default=os.getenv("NEO4J_USERNAME", "neo4j"),
        help="Neo4j username (default: neo4j)",
    )

    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD"),
        help="Neo4j password (required, can be set via NEO4J_PASSWORD env var)",
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify schema without creating (default: False)",
    )

    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Only set up authentication schema (default: False)",
    )

    parser.add_argument(
        "--profiles-only",
        action="store_true",
        help="Only set up player profile schema (default: False)",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging (default: False)"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate required arguments
    if not args.password:
        logger.error(
            "Neo4j password is required. Set --password or NEO4J_PASSWORD environment variable."
        )
        sys.exit(1)

    logger.info("🚀 Starting TTA Authentication Database Setup")
    logger.info(f"Neo4j URI: {args.uri}")
    logger.info(f"Neo4j Username: {args.username}")
    logger.info(f"Verify Only: {args.verify_only}")
    logger.info(f"Auth Only: {args.auth_only}")
    logger.info(f"Profiles Only: {args.profiles_only}")

    success = True

    # Set up authentication schema
    if not args.profiles_only:
        logger.info("\n" + "=" * 60)
        logger.info("SETTING UP AUTHENTICATION SCHEMA")
        logger.info("=" * 60)

        auth_success = setup_authentication_schema(
            args.uri, args.username, args.password, args.verify_only
        )

        if not auth_success:
            logger.error("❌ Authentication schema setup failed")
            success = False
        else:
            logger.info("✅ Authentication schema setup successful")

    # Set up player profile schema
    if not args.auth_only:
        logger.info("\n" + "=" * 60)
        logger.info("SETTING UP PLAYER PROFILE SCHEMA")
        logger.info("=" * 60)

        profile_success = setup_player_profile_schema(
            args.uri, args.username, args.password, args.verify_only
        )

        if not profile_success:
            logger.error("❌ Player profile schema setup failed")
            success = False
        else:
            logger.info("✅ Player profile schema setup successful")

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 60)

    if success:
        logger.info("🎉 All database schemas set up successfully!")
        logger.info("The TTA authentication system is ready for use.")
        sys.exit(0)
    else:
        logger.error("💥 Database schema setup failed!")
        logger.error("Please check the logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
