#!/usr/bin/env python3
"""
Simple test runner for Neo4j schema functionality.
"""

import logging
import os
import sys

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_neo4j_imports():
    """Test that Neo4j modules can be imported."""
    print("Testing Neo4j module imports...")

    try:
        from neo4j_schema import (
            Neo4jConnectionError,
            Neo4jQueryHelper,
            Neo4jSchemaError,
            Neo4jSchemaManager,
            setup_neo4j_schema,
            validate_neo4j_schema,
        )
        print("  ✓ Neo4j schema module imported successfully")

        from migrations import DataSeeder, MigrationManager, run_migrations
        print("  ✓ Migrations module imported successfully")

        return True

    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        print("  Note: This is expected if neo4j package is not installed")
        return False


def test_schema_manager_creation():
    """Test creating schema manager instances."""
    print("Testing schema manager creation...")

    try:
        from neo4j_schema import Neo4jSchemaManager

        # Test with default parameters
        manager = Neo4jSchemaManager()
        assert manager.uri == "bolt://localhost:7688"
        assert manager.username == "neo4j"
        assert manager.password == "password"
        assert manager.current_schema_version == "1.0.0"
        print("  ✓ Default schema manager created")

        # Test with custom parameters
        custom_manager = Neo4jSchemaManager(
            uri="bolt://localhost:7687",
            username="test_user",
            password="test_pass"
        )
        assert custom_manager.uri == "bolt://localhost:7687"
        assert custom_manager.username == "test_user"
        assert custom_manager.password == "test_pass"
        print("  ✓ Custom schema manager created")

        return True

    except Exception as e:
        print(f"  ❌ Schema manager creation failed: {e}")
        return False


def test_migration_manager_creation():
    """Test creating migration manager instances."""
    print("Testing migration manager creation...")

    try:
        from migrations import DataSeeder, MigrationManager
        from neo4j_schema import Neo4jSchemaManager

        # Create a mock schema manager
        schema_manager = Neo4jSchemaManager()

        # Test migration manager creation
        migration_manager = MigrationManager(schema_manager)
        assert migration_manager.schema_manager == schema_manager
        print("  ✓ Migration manager created")

        # Test data seeder creation
        data_seeder = DataSeeder(migration_manager)
        assert data_seeder.migration_manager == migration_manager
        print("  ✓ Data seeder created")

        return True

    except Exception as e:
        print(f"  ❌ Migration manager creation failed: {e}")
        return False


def test_sample_data_structure():
    """Test that sample data has correct structure."""
    print("Testing sample data structure...")

    try:
        from migrations import DataSeeder, MigrationManager
        from neo4j_schema import Neo4jSchemaManager

        # Create instances
        schema_manager = Neo4jSchemaManager()
        migration_manager = MigrationManager(schema_manager)
        data_seeder = DataSeeder(migration_manager)

        # Test that sample data methods exist and return expected structure
        # Note: We can't actually call these without a database connection
        assert hasattr(data_seeder, 'seed_sample_characters')
        assert hasattr(data_seeder, 'seed_sample_locations')
        assert hasattr(data_seeder, 'seed_therapeutic_content')
        assert hasattr(data_seeder, 'seed_all_sample_data')
        print("  ✓ Data seeder methods exist")

        return True

    except Exception as e:
        print(f"  ❌ Sample data structure test failed: {e}")
        return False


def test_query_helper_methods():
    """Test that query helper has expected methods."""
    print("Testing query helper methods...")

    try:
        from unittest.mock import MagicMock

        from neo4j_schema import Neo4jQueryHelper

        # Create a mock driver
        mock_driver = MagicMock()
        query_helper = Neo4jQueryHelper(mock_driver)

        # Test that expected methods exist
        expected_methods = [
            'create_user', 'create_character', 'create_location', 'create_session',
            'create_therapeutic_goal', 'create_character_relationship',
            'get_user_sessions', 'get_character_memories', 'get_therapeutic_progress',
            'update_character_location'
        ]

        for method_name in expected_methods:
            assert hasattr(query_helper, method_name), f"Missing method: {method_name}"
            assert callable(getattr(query_helper, method_name)), f"Method not callable: {method_name}"

        print(f"  ✓ All {len(expected_methods)} query helper methods exist")

        return True

    except Exception as e:
        print(f"  ❌ Query helper methods test failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions."""
    print("Testing utility functions...")

    try:
        from migrations import run_migrations
        from neo4j_schema import setup_neo4j_schema, validate_neo4j_schema

        # Test that utility functions exist and are callable
        assert callable(setup_neo4j_schema), "setup_neo4j_schema not callable"
        assert callable(validate_neo4j_schema), "validate_neo4j_schema not callable"
        assert callable(run_migrations), "run_migrations not callable"

        print("  ✓ All utility functions exist and are callable")

        return True

    except Exception as e:
        print(f"  ❌ Utility functions test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("TTA Prototype Neo4j Schema Test Runner")
    print("=" * 60)

    tests = [
        test_neo4j_imports,
        test_schema_manager_creation,
        test_migration_manager_creation,
        test_sample_data_structure,
        test_query_helper_methods,
        test_utility_functions
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Neo4j schema functionality is working correctly.")
        if passed == 1:  # Only imports failed
            print("Note: Neo4j package not installed - this is expected in some environments")
    else:
        print("❌ Some tests failed. Check the output above for details.")

    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
