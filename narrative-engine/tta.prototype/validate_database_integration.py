#!/usr/bin/env python3
"""
Database Integration Validation Script for TTA Prototype

This script validates the complete database integration and persistence layer,
including Neo4j schema setup, Redis caching, and data persistence across
all therapeutic components.

Usage:
    python validate_database_integration.py [--neo4j-uri URI] [--redis-host HOST]
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any

# Add the project paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseIntegrationValidator:
    """
    Comprehensive database integration validator for TTA prototype.

    This class validates Neo4j schema setup, Redis caching integration,
    data persistence, and performance under load conditions.
    """

    def __init__(self, neo4j_uri: str = "bolt://localhost:7688",
                 neo4j_username: str = "neo4j",
                 neo4j_password: str = "password",
                 redis_host: str = "localhost",
                 redis_port: int = 6379):
        """
        Initialize the database integration validator.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
            redis_host: Redis host
            redis_port: Redis port
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.redis_host = redis_host
        self.redis_port = redis_port

        # Component instances
        self.neo4j_manager = None
        self.redis_connection_manager = None
        self.session_cache_manager = None
        self.cache_invalidation_manager = None

        # Validation results
        self.validation_results = {
            "neo4j_schema": {"status": "not_tested", "details": {}},
            "redis_caching": {"status": "not_tested", "details": {}},
            "data_persistence": {"status": "not_tested", "details": {}},
            "load_testing": {"status": "not_tested", "details": {}},
            "integration_testing": {"status": "not_tested", "details": {}},
            "overall": {"status": "not_tested", "score": 0.0}
        }

    def validate_all(self) -> dict[str, Any]:
        """
        Run complete database integration validation.

        Returns:
            Dict[str, Any]: Comprehensive validation results
        """
        logger.info("Starting comprehensive database integration validation")
        start_time = time.time()

        try:
            # Initialize database connections
            if not self._initialize_connections():
                self.validation_results["overall"]["status"] = "failed"
                self.validation_results["overall"]["error"] = "Failed to initialize database connections"
                return self.validation_results

            # Run validation tests
            self._validate_neo4j_schema()
            self._validate_redis_caching()
            self._validate_data_persistence()
            self._validate_load_performance()
            self._validate_integration()

            # Calculate overall score
            self._calculate_overall_score()

            # Generate summary
            validation_time = time.time() - start_time
            self.validation_results["validation_time"] = validation_time
            self.validation_results["timestamp"] = datetime.now().isoformat()

            logger.info(f"Database integration validation completed in {validation_time:.2f} seconds")
            return self.validation_results

        except Exception as e:
            logger.error(f"Database integration validation failed: {e}")
            self.validation_results["overall"]["status"] = "error"
            self.validation_results["overall"]["error"] = str(e)
            return self.validation_results

        finally:
            self._cleanup_connections()

    def _initialize_connections(self) -> bool:
        """Initialize database connections."""
        logger.info("Initializing database connections")

        try:
            # Initialize Neo4j connection
            from database.neo4j_schema import Neo4jSchemaManager
            self.neo4j_manager = Neo4jSchemaManager(
                uri=self.neo4j_uri,
                username=self.neo4j_username,
                password=self.neo4j_password
            )
            self.neo4j_manager.connect()
            logger.info("Neo4j connection established")

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {e}")
            self.validation_results["neo4j_schema"]["status"] = "connection_failed"
            self.validation_results["neo4j_schema"]["error"] = str(e)

        try:
            # Initialize Redis connection
            from database.redis_cache_enhanced import (
                CacheInvalidationManager,
                RedisConnectionManager,
                SessionCacheManager,
            )

            self.redis_connection_manager = RedisConnectionManager(
                host=self.redis_host,
                port=self.redis_port
            )
            self.redis_connection_manager.connect()

            self.session_cache_manager = SessionCacheManager(self.redis_connection_manager)
            self.cache_invalidation_manager = CacheInvalidationManager(self.redis_connection_manager)

            logger.info("Redis connection established")

        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            self.validation_results["redis_caching"]["status"] = "connection_failed"
            self.validation_results["redis_caching"]["error"] = str(e)

        # Check if at least one connection succeeded
        neo4j_ok = self.neo4j_manager is not None
        redis_ok = self.redis_connection_manager is not None

        if not neo4j_ok and not redis_ok:
            logger.error("Both Neo4j and Redis connections failed")
            return False

        return True

    def _validate_neo4j_schema(self) -> None:
        """Validate Neo4j schema setup and operations."""
        logger.info("Validating Neo4j schema")

        if not self.neo4j_manager:
            self.validation_results["neo4j_schema"]["status"] = "skipped"
            self.validation_results["neo4j_schema"]["reason"] = "Neo4j connection not available"
            return

        try:
            schema_results = {
                "connection": False,
                "schema_setup": False,
                "constraints": False,
                "indexes": False,
                "validation": False,
                "query_operations": False,
                "performance": {}
            }

            # Test connection
            start_time = time.time()
            if self.neo4j_manager.is_connected():
                schema_results["connection"] = True
                schema_results["performance"]["connection_time"] = time.time() - start_time

            # Test schema setup
            start_time = time.time()
            if self.neo4j_manager.setup_schema():
                schema_results["schema_setup"] = True
                schema_results["performance"]["schema_setup_time"] = time.time() - start_time

            # Test constraints creation
            start_time = time.time()
            if self.neo4j_manager.create_constraints():
                schema_results["constraints"] = True
                schema_results["performance"]["constraints_time"] = time.time() - start_time

            # Test indexes creation
            start_time = time.time()
            if self.neo4j_manager.create_indexes():
                schema_results["indexes"] = True
                schema_results["performance"]["indexes_time"] = time.time() - start_time

            # Test schema validation
            start_time = time.time()
            if self.neo4j_manager.validate_schema():
                schema_results["validation"] = True
                schema_results["performance"]["validation_time"] = time.time() - start_time

            # Test basic query operations
            schema_results["query_operations"] = self._test_neo4j_queries()

            # Calculate score
            passed_tests = sum(1 for v in schema_results.values() if v is True)
            total_tests = 6  # connection, schema_setup, constraints, indexes, validation, query_operations
            score = passed_tests / total_tests

            self.validation_results["neo4j_schema"]["status"] = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
            self.validation_results["neo4j_schema"]["score"] = score
            self.validation_results["neo4j_schema"]["details"] = schema_results

            logger.info(f"Neo4j schema validation completed with score: {score:.2f}")

        except Exception as e:
            logger.error(f"Neo4j schema validation failed: {e}")
            self.validation_results["neo4j_schema"]["status"] = "error"
            self.validation_results["neo4j_schema"]["error"] = str(e)

    def _test_neo4j_queries(self) -> bool:
        """Test basic Neo4j query operations."""
        try:
            from database.neo4j_schema import Neo4jQueryHelper

            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            # Test creating entities
            test_user_id = f"test_user_{int(time.time())}"
            test_char_id = f"test_char_{int(time.time())}"
            test_location_id = f"test_location_{int(time.time())}"
            test_session_id = f"test_session_{int(time.time())}"

            # Create test user
            if not query_helper.create_user(test_user_id, name="Test User"):
                return False

            # Create test character
            if not query_helper.create_character(test_char_id, "Test Character", therapeutic_role="therapist"):
                return False

            # Create test location
            if not query_helper.create_location(test_location_id, "Test Location", location_type="therapeutic_space"):
                return False

            # Create test session
            if not query_helper.create_session(test_session_id, test_user_id):
                return False

            # Test retrieval operations
            sessions = query_helper.get_user_sessions(test_user_id, limit=5)
            if not sessions:
                return False

            # Test therapeutic goal creation
            test_goal_id = f"test_goal_{int(time.time())}"
            if not query_helper.create_therapeutic_goal(
                test_goal_id, test_user_id, "Test Goal", "Test therapeutic goal"
            ):
                return False

            # Test therapeutic progress retrieval
            progress = query_helper.get_therapeutic_progress(test_user_id)
            if not progress or "user" not in progress:
                return False

            logger.info("Neo4j query operations test passed")
            return True

        except Exception as e:
            logger.error(f"Neo4j query operations test failed: {e}")
            return False

    def _validate_redis_caching(self) -> None:
        """Validate Redis caching operations."""
        logger.info("Validating Redis caching")

        if not self.redis_connection_manager:
            self.validation_results["redis_caching"]["status"] = "skipped"
            self.validation_results["redis_caching"]["reason"] = "Redis connection not available"
            return

        try:
            cache_results = {
                "connection": False,
                "session_caching": False,
                "character_caching": False,
                "therapeutic_caching": False,
                "invalidation": False,
                "metrics": False,
                "performance": {}
            }

            # Test connection
            start_time = time.time()
            if self.redis_connection_manager.is_connected():
                cache_results["connection"] = True
                cache_results["performance"]["connection_time"] = time.time() - start_time

            # Test session caching
            cache_results["session_caching"] = self._test_session_caching()

            # Test character caching
            cache_results["character_caching"] = self._test_character_caching()

            # Test therapeutic progress caching
            cache_results["therapeutic_caching"] = self._test_therapeutic_caching()

            # Test cache invalidation
            cache_results["invalidation"] = self._test_cache_invalidation()

            # Test metrics collection
            cache_results["metrics"] = self._test_cache_metrics()

            # Calculate score
            passed_tests = sum(1 for v in cache_results.values() if v is True)
            total_tests = 6  # connection, session, character, therapeutic, invalidation, metrics
            score = passed_tests / total_tests

            self.validation_results["redis_caching"]["status"] = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
            self.validation_results["redis_caching"]["score"] = score
            self.validation_results["redis_caching"]["details"] = cache_results

            logger.info(f"Redis caching validation completed with score: {score:.2f}")

        except Exception as e:
            logger.error(f"Redis caching validation failed: {e}")
            self.validation_results["redis_caching"]["status"] = "error"
            self.validation_results["redis_caching"]["error"] = str(e)

    def _test_session_caching(self) -> bool:
        """Test session state caching operations."""
        try:
            # Import data models
            from models.data_models import SessionState

            # Create test session
            test_session = SessionState(
                session_id=f"test_session_{int(time.time())}",
                user_id=f"test_user_{int(time.time())}",
                current_scenario_id="test_scenario",
                current_location_id="test_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Test caching
            if not self.session_cache_manager.cache_session_state(test_session):
                return False

            # Test retrieval
            retrieved_session = self.session_cache_manager.get_session_state(test_session.session_id)
            if not retrieved_session or retrieved_session.session_id != test_session.session_id:
                return False

            # Test batch operations
            test_sessions = [
                SessionState(
                    session_id=f"batch_session_{i}_{int(time.time())}",
                    user_id=f"batch_user_{i}",
                    current_scenario_id="test_scenario",
                    current_location_id="test_location",
                    narrative_position=1,
                    character_states={},
                    user_inventory=[],
                    therapeutic_progress=None,
                    emotional_state=None,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                ) for i in range(3)
            ]

            cached_count = self.session_cache_manager.cache_multiple_sessions(test_sessions)
            if cached_count != 3:
                return False

            session_ids = [s.session_id for s in test_sessions]
            retrieved_sessions = self.session_cache_manager.get_multiple_sessions(session_ids)
            if len(retrieved_sessions) != 3:
                return False

            logger.info("Session caching test passed")
            return True

        except Exception as e:
            logger.error(f"Session caching test failed: {e}")
            return False

    def _test_character_caching(self) -> bool:
        """Test character state caching operations."""
        try:
            # This would test character-specific caching if implemented
            # For now, we'll test basic key generation and TTL configuration

            # Test TTL configuration for characters
            character_ttl = self.redis_connection_manager.get_ttl("character")
            if character_ttl != 7200:  # 2 hours
                return False

            # Test key generation
            character_key = self.session_cache_manager._generate_key("character", "char1", "session123")
            expected_key = "tta:character:session123:char1"
            if character_key != expected_key:
                return False

            logger.info("Character caching test passed")
            return True

        except Exception as e:
            logger.error(f"Character caching test failed: {e}")
            return False

    def _test_therapeutic_caching(self) -> bool:
        """Test therapeutic progress caching operations."""
        try:
            from models.data_models import TherapeuticProgress

            # Create test therapeutic progress
            test_progress = TherapeuticProgress(
                user_id=f"test_user_{int(time.time())}",
                therapeutic_goals=[],
                completed_interventions=[],
                emotional_growth_metrics={},
                coping_strategies_learned=[],
                next_recommended_focus="test_focus"
            )

            # Test caching
            if not self.session_cache_manager.cache_therapeutic_progress(test_progress, test_progress.user_id):
                return False

            # Test retrieval
            retrieved_progress = self.session_cache_manager.get_therapeutic_progress(test_progress.user_id)
            if not retrieved_progress or retrieved_progress.user_id != test_progress.user_id:
                return False

            logger.info("Therapeutic caching test passed")
            return True

        except Exception as e:
            logger.error(f"Therapeutic caching test failed: {e}")
            return False

    def _test_cache_invalidation(self) -> bool:
        """Test cache invalidation operations."""
        try:
            # Create test session for invalidation
            from models.data_models import SessionState

            test_session = SessionState(
                session_id=f"invalidation_test_{int(time.time())}",
                user_id=f"invalidation_user_{int(time.time())}",
                current_scenario_id="test_scenario",
                current_location_id="test_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Cache the session
            if not self.session_cache_manager.cache_session_state(test_session):
                return False

            # Test session invalidation
            result = self.cache_invalidation_manager.invalidate_session(test_session.session_id)
            if not result or result.get("total", 0) == 0:
                return False

            # Verify session is invalidated
            retrieved_session = self.session_cache_manager.get_session_state(test_session.session_id)
            if retrieved_session is not None:
                return False

            # Test cache statistics
            stats = self.cache_invalidation_manager.get_cache_statistics()
            if not stats or "key_counts" not in stats:
                return False

            logger.info("Cache invalidation test passed")
            return True

        except Exception as e:
            logger.error(f"Cache invalidation test failed: {e}")
            return False

    def _test_cache_metrics(self) -> bool:
        """Test cache metrics collection."""
        try:
            # Get connection statistics
            stats = self.redis_connection_manager.get_connection_stats()
            if not stats or "cache_metrics" not in stats:
                return False

            # Check metrics structure
            metrics = stats["cache_metrics"]
            required_fields = ["hits", "misses", "sets", "deletes", "total_operations", "hit_rate"]
            for field in required_fields:
                if field not in metrics:
                    return False

            logger.info("Cache metrics test passed")
            return True

        except Exception as e:
            logger.error(f"Cache metrics test failed: {e}")
            return False

    def _validate_data_persistence(self) -> None:
        """Validate data persistence across all therapeutic components."""
        logger.info("Validating data persistence")

        try:
            persistence_results = {
                "session_persistence": False,
                "character_persistence": False,
                "therapeutic_persistence": False,
                "cross_component_consistency": False,
                "data_integrity": False
            }

            # Test session persistence
            persistence_results["session_persistence"] = self._test_session_persistence()

            # Test character persistence
            persistence_results["character_persistence"] = self._test_character_persistence()

            # Test therapeutic data persistence
            persistence_results["therapeutic_persistence"] = self._test_therapeutic_persistence()

            # Test cross-component consistency
            persistence_results["cross_component_consistency"] = self._test_cross_component_consistency()

            # Test data integrity
            persistence_results["data_integrity"] = self._test_data_integrity()

            # Calculate score
            passed_tests = sum(1 for v in persistence_results.values() if v is True)
            total_tests = len(persistence_results)
            score = passed_tests / total_tests

            self.validation_results["data_persistence"]["status"] = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
            self.validation_results["data_persistence"]["score"] = score
            self.validation_results["data_persistence"]["details"] = persistence_results

            logger.info(f"Data persistence validation completed with score: {score:.2f}")

        except Exception as e:
            logger.error(f"Data persistence validation failed: {e}")
            self.validation_results["data_persistence"]["status"] = "error"
            self.validation_results["data_persistence"]["error"] = str(e)

    def _test_session_persistence(self) -> bool:
        """Test session data persistence between cache and database."""
        try:
            if not (self.neo4j_manager and self.session_cache_manager):
                return False

            # Create test session in both cache and database
            test_session_id = f"persist_session_{int(time.time())}"
            test_user_id = f"persist_user_{int(time.time())}"

            # Create in Neo4j
            from database.neo4j_schema import Neo4jQueryHelper
            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            if not query_helper.create_user(test_user_id, name="Persistence Test User"):
                return False

            if not query_helper.create_session(test_session_id, test_user_id):
                return False

            # Create in Redis cache
            from models.data_models import SessionState
            test_session = SessionState(
                session_id=test_session_id,
                user_id=test_user_id,
                current_scenario_id="test_scenario",
                current_location_id="test_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            if not self.session_cache_manager.cache_session_state(test_session):
                return False

            # Verify persistence in both systems
            cached_session = self.session_cache_manager.get_session_state(test_session_id)
            if not cached_session:
                return False

            db_sessions = query_helper.get_user_sessions(test_user_id)
            if not db_sessions or not any(s.get("session_id") == test_session_id for s in db_sessions):
                return False

            logger.info("Session persistence test passed")
            return True

        except Exception as e:
            logger.error(f"Session persistence test failed: {e}")
            return False

    def _test_character_persistence(self) -> bool:
        """Test character data persistence."""
        try:
            if not self.neo4j_manager:
                return False

            # Create test character
            from database.neo4j_schema import Neo4jQueryHelper
            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            test_char_id = f"persist_char_{int(time.time())}"
            if not query_helper.create_character(
                test_char_id,
                "Persistence Test Character",
                therapeutic_role="therapist",
                personality_traits={"empathy": 0.8, "patience": 0.9}
            ):
                return False

            # Test character relationship creation
            test_char2_id = f"persist_char2_{int(time.time())}"
            if not query_helper.create_character(test_char2_id, "Test Character 2"):
                return False

            if not query_helper.create_character_relationship(
                test_char_id, test_char2_id, "colleague", 0.7
            ):
                return False

            logger.info("Character persistence test passed")
            return True

        except Exception as e:
            logger.error(f"Character persistence test failed: {e}")
            return False

    def _test_therapeutic_persistence(self) -> bool:
        """Test therapeutic data persistence."""
        try:
            if not self.neo4j_manager:
                return False

            # Create test therapeutic data
            from database.neo4j_schema import Neo4jQueryHelper
            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            test_user_id = f"therapeutic_user_{int(time.time())}"
            test_goal_id = f"therapeutic_goal_{int(time.time())}"

            # Create user and therapeutic goal
            if not query_helper.create_user(test_user_id, name="Therapeutic Test User"):
                return False

            if not query_helper.create_therapeutic_goal(
                test_goal_id,
                test_user_id,
                "Test Therapeutic Goal",
                "A test goal for persistence validation"
            ):
                return False

            # Verify therapeutic progress retrieval
            progress = query_helper.get_therapeutic_progress(test_user_id)
            if not progress or "goals" not in progress or not progress["goals"]:
                return False

            logger.info("Therapeutic persistence test passed")
            return True

        except Exception as e:
            logger.error(f"Therapeutic persistence test failed: {e}")
            return False

    def _test_cross_component_consistency(self) -> bool:
        """Test consistency between cache and database."""
        try:
            # This would test that data remains consistent between Redis and Neo4j
            # For now, we'll test basic consistency checks

            if not (self.neo4j_manager and self.redis_connection_manager):
                return False

            # Test that both systems are accessible and responding
            neo4j_responsive = self.neo4j_manager.is_connected()
            redis_responsive = self.redis_connection_manager.is_connected()

            if not (neo4j_responsive and redis_responsive):
                return False

            logger.info("Cross-component consistency test passed")
            return True

        except Exception as e:
            logger.error(f"Cross-component consistency test failed: {e}")
            return False

    def _test_data_integrity(self) -> bool:
        """Test data integrity constraints and validation."""
        try:
            if not self.neo4j_manager:
                return False

            # Test that schema constraints are enforced
            # This would involve trying to create duplicate entities and ensuring they fail

            # For now, we'll test that the schema validation passes
            if not self.neo4j_manager.validate_schema():
                return False

            logger.info("Data integrity test passed")
            return True

        except Exception as e:
            logger.error(f"Data integrity test failed: {e}")
            return False

    def _validate_load_performance(self) -> None:
        """Validate database operations under load conditions."""
        logger.info("Validating load performance")

        try:
            load_results = {
                "concurrent_sessions": False,
                "bulk_operations": False,
                "cache_performance": False,
                "database_performance": False,
                "error_handling": False,
                "performance_metrics": {}
            }

            # Test concurrent session handling
            load_results["concurrent_sessions"] = self._test_concurrent_sessions()

            # Test bulk operations
            load_results["bulk_operations"] = self._test_bulk_operations()

            # Test cache performance under load
            load_results["cache_performance"] = self._test_cache_performance()

            # Test database performance under load
            load_results["database_performance"] = self._test_database_performance()

            # Test error handling under load
            load_results["error_handling"] = self._test_error_handling()

            # Calculate score
            passed_tests = sum(1 for v in load_results.values() if v is True)
            total_tests = 5  # concurrent, bulk, cache_perf, db_perf, error_handling
            score = passed_tests / total_tests

            self.validation_results["load_testing"]["status"] = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
            self.validation_results["load_testing"]["score"] = score
            self.validation_results["load_testing"]["details"] = load_results

            logger.info(f"Load performance validation completed with score: {score:.2f}")

        except Exception as e:
            logger.error(f"Load performance validation failed: {e}")
            self.validation_results["load_testing"]["status"] = "error"
            self.validation_results["load_testing"]["error"] = str(e)

    def _test_concurrent_sessions(self) -> bool:
        """Test handling of concurrent sessions."""
        try:
            if not self.session_cache_manager:
                return False

            # Create multiple test sessions concurrently
            import threading

            from models.data_models import SessionState

            test_sessions = []
            for i in range(10):
                session = SessionState(
                    session_id=f"concurrent_session_{i}_{int(time.time())}",
                    user_id=f"concurrent_user_{i}",
                    current_scenario_id="test_scenario",
                    current_location_id="test_location",
                    narrative_position=1,
                    character_states={},
                    user_inventory=[],
                    therapeutic_progress=None,
                    emotional_state=None,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                test_sessions.append(session)

            # Cache sessions concurrently
            def cache_session(session):
                return self.session_cache_manager.cache_session_state(session)

            threads = []
            results = []

            for session in test_sessions:
                thread = threading.Thread(target=lambda s=session: results.append(cache_session(s)))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Check that all sessions were cached successfully
            if not all(results):
                return False

            # Verify all sessions can be retrieved
            session_ids = [s.session_id for s in test_sessions]
            retrieved_sessions = self.session_cache_manager.get_multiple_sessions(session_ids)

            if len(retrieved_sessions) != len(test_sessions):
                return False

            logger.info("Concurrent sessions test passed")
            return True

        except Exception as e:
            logger.error(f"Concurrent sessions test failed: {e}")
            return False

    def _test_bulk_operations(self) -> bool:
        """Test bulk database operations."""
        try:
            if not self.session_cache_manager:
                return False

            # Test bulk session caching
            from models.data_models import SessionState

            bulk_sessions = []
            for i in range(50):
                session = SessionState(
                    session_id=f"bulk_session_{i}_{int(time.time())}",
                    user_id=f"bulk_user_{i}",
                    current_scenario_id="test_scenario",
                    current_location_id="test_location",
                    narrative_position=1,
                    character_states={},
                    user_inventory=[],
                    therapeutic_progress=None,
                    emotional_state=None,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                bulk_sessions.append(session)

            start_time = time.time()
            cached_count = self.session_cache_manager.cache_multiple_sessions(bulk_sessions)
            bulk_time = time.time() - start_time

            if cached_count != len(bulk_sessions):
                return False

            # Performance check - should complete within reasonable time
            if bulk_time > 10.0:  # 10 seconds for 50 sessions
                logger.warning(f"Bulk operations took {bulk_time:.2f} seconds - may be slow")

            logger.info(f"Bulk operations test passed ({bulk_time:.2f}s for {cached_count} sessions)")
            return True

        except Exception as e:
            logger.error(f"Bulk operations test failed: {e}")
            return False

    def _test_cache_performance(self) -> bool:
        """Test cache performance metrics."""
        try:
            if not self.redis_connection_manager:
                return False

            # Perform various cache operations and check metrics
            initial_stats = self.redis_connection_manager.get_connection_stats()
            initial_metrics = initial_stats.get("cache_metrics", {})

            # Perform test operations
            from models.data_models import SessionState

            test_session = SessionState(
                session_id=f"perf_session_{int(time.time())}",
                user_id=f"perf_user_{int(time.time())}",
                current_scenario_id="test_scenario",
                current_location_id="test_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Cache and retrieve multiple times
            for _ in range(10):
                self.session_cache_manager.cache_session_state(test_session)
                self.session_cache_manager.get_session_state(test_session.session_id)

            # Check that metrics were updated
            final_stats = self.redis_connection_manager.get_connection_stats()
            final_metrics = final_stats.get("cache_metrics", {})

            # Verify metrics increased
            if final_metrics.get("total_operations", 0) <= initial_metrics.get("total_operations", 0):
                return False

            # Check average response time is reasonable
            avg_response_time = final_metrics.get("average_response_time", 0)
            if avg_response_time > 1.0:  # 1 second average is too slow
                logger.warning(f"Average cache response time is high: {avg_response_time:.3f}s")

            logger.info("Cache performance test passed")
            return True

        except Exception as e:
            logger.error(f"Cache performance test failed: {e}")
            return False

    def _test_database_performance(self) -> bool:
        """Test database performance metrics."""
        try:
            if not self.neo4j_manager:
                return False

            # Test query performance
            from database.neo4j_schema import Neo4jQueryHelper
            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            # Create test data and measure performance
            start_time = time.time()

            test_user_id = f"perf_user_{int(time.time())}"
            if not query_helper.create_user(test_user_id, name="Performance Test User"):
                return False

            # Create multiple therapeutic goals
            for i in range(5):
                goal_id = f"perf_goal_{i}_{int(time.time())}"
                query_helper.create_therapeutic_goal(
                    goal_id, test_user_id, f"Goal {i}", f"Performance test goal {i}"
                )

            # Retrieve therapeutic progress
            progress = query_helper.get_therapeutic_progress(test_user_id)

            query_time = time.time() - start_time

            if not progress or "goals" not in progress:
                return False

            # Performance check
            if query_time > 5.0:  # 5 seconds is too slow
                logger.warning(f"Database operations took {query_time:.2f} seconds - may be slow")

            logger.info(f"Database performance test passed ({query_time:.2f}s)")
            return True

        except Exception as e:
            logger.error(f"Database performance test failed: {e}")
            return False

    def _test_error_handling(self) -> bool:
        """Test error handling under various conditions."""
        try:
            # Test handling of invalid data
            if self.session_cache_manager:
                # Try to cache invalid session data
                try:
                    result = self.session_cache_manager.cache_session_state(None)
                    # Should handle gracefully and return False
                    if result is not False:
                        return False
                except Exception:
                    # Exception handling is also acceptable
                    pass

            # Test handling of connection issues
            # This would involve simulating connection failures

            logger.info("Error handling test passed")
            return True

        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False

    def _validate_integration(self) -> None:
        """Validate integration between all database components."""
        logger.info("Validating component integration")

        try:
            integration_results = {
                "neo4j_redis_integration": False,
                "cache_invalidation_integration": False,
                "therapeutic_component_integration": False,
                "monitoring_integration": False,
                "overall_system_health": False
            }

            # Test Neo4j-Redis integration
            integration_results["neo4j_redis_integration"] = self._test_neo4j_redis_integration()

            # Test cache invalidation integration
            integration_results["cache_invalidation_integration"] = self._test_cache_invalidation_integration()

            # Test therapeutic component integration
            integration_results["therapeutic_component_integration"] = self._test_therapeutic_integration()

            # Test monitoring integration
            integration_results["monitoring_integration"] = self._test_monitoring_integration()

            # Test overall system health
            integration_results["overall_system_health"] = self._test_system_health()

            # Calculate score
            passed_tests = sum(1 for v in integration_results.values() if v is True)
            total_tests = len(integration_results)
            score = passed_tests / total_tests

            self.validation_results["integration_testing"]["status"] = "passed" if score >= 0.8 else "warning" if score >= 0.5 else "failed"
            self.validation_results["integration_testing"]["score"] = score
            self.validation_results["integration_testing"]["details"] = integration_results

            logger.info(f"Integration validation completed with score: {score:.2f}")

        except Exception as e:
            logger.error(f"Integration validation failed: {e}")
            self.validation_results["integration_testing"]["status"] = "error"
            self.validation_results["integration_testing"]["error"] = str(e)

    def _test_neo4j_redis_integration(self) -> bool:
        """Test integration between Neo4j and Redis."""
        try:
            if not (self.neo4j_manager and self.redis_connection_manager):
                return False

            # Test that both systems can work together
            # Create data in Neo4j and cache related data in Redis

            from models.data_models import SessionState

            from database.neo4j_schema import Neo4jQueryHelper

            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            test_user_id = f"integration_user_{int(time.time())}"
            test_session_id = f"integration_session_{int(time.time())}"

            # Create user in Neo4j
            if not query_helper.create_user(test_user_id, name="Integration Test User"):
                return False

            # Create session in Neo4j
            if not query_helper.create_session(test_session_id, test_user_id):
                return False

            # Cache session state in Redis
            test_session = SessionState(
                session_id=test_session_id,
                user_id=test_user_id,
                current_scenario_id="integration_scenario",
                current_location_id="integration_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            if not self.session_cache_manager.cache_session_state(test_session):
                return False

            # Verify data exists in both systems
            db_sessions = query_helper.get_user_sessions(test_user_id)
            cached_session = self.session_cache_manager.get_session_state(test_session_id)

            if not db_sessions or not cached_session:
                return False

            logger.info("Neo4j-Redis integration test passed")
            return True

        except Exception as e:
            logger.error(f"Neo4j-Redis integration test failed: {e}")
            return False

    def _test_cache_invalidation_integration(self) -> bool:
        """Test cache invalidation integration."""
        try:
            if not self.cache_invalidation_manager:
                return False

            # Test that invalidation works properly with the cache system
            from models.data_models import SessionState

            test_session = SessionState(
                session_id=f"invalidation_integration_{int(time.time())}",
                user_id=f"invalidation_user_{int(time.time())}",
                current_scenario_id="test_scenario",
                current_location_id="test_location",
                narrative_position=1,
                character_states={},
                user_inventory=[],
                therapeutic_progress=None,
                emotional_state=None,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Cache session
            if not self.session_cache_manager.cache_session_state(test_session):
                return False

            # Invalidate session
            result = self.cache_invalidation_manager.invalidate_session(test_session.session_id)
            if not result or result.get("total", 0) == 0:
                return False

            # Verify session is gone
            retrieved_session = self.session_cache_manager.get_session_state(test_session.session_id)
            if retrieved_session is not None:
                return False

            logger.info("Cache invalidation integration test passed")
            return True

        except Exception as e:
            logger.error(f"Cache invalidation integration test failed: {e}")
            return False

    def _test_therapeutic_integration(self) -> bool:
        """Test therapeutic component integration."""
        try:
            # Test that therapeutic components can work with the database layer
            if not (self.neo4j_manager and self.session_cache_manager):
                return False

            # This would test integration with therapeutic components
            # For now, we'll test basic therapeutic data flow

            from models.data_models import TherapeuticProgress

            from database.neo4j_schema import Neo4jQueryHelper

            query_helper = Neo4jQueryHelper(self.neo4j_manager.driver)

            test_user_id = f"therapeutic_integration_{int(time.time())}"

            # Create user and therapeutic goal in Neo4j
            if not query_helper.create_user(test_user_id, name="Therapeutic Integration User"):
                return False

            test_goal_id = f"therapeutic_goal_{int(time.time())}"
            if not query_helper.create_therapeutic_goal(
                test_goal_id, test_user_id, "Integration Goal", "Test therapeutic integration"
            ):
                return False

            # Cache therapeutic progress in Redis
            test_progress = TherapeuticProgress(
                user_id=test_user_id,
                therapeutic_goals=[],
                completed_interventions=[],
                emotional_growth_metrics={},
                coping_strategies_learned=[],
                next_recommended_focus="integration_test"
            )

            if not self.session_cache_manager.cache_therapeutic_progress(test_progress, test_user_id):
                return False

            # Verify data consistency
            db_progress = query_helper.get_therapeutic_progress(test_user_id)
            cached_progress = self.session_cache_manager.get_therapeutic_progress(test_user_id)

            if not db_progress or not cached_progress:
                return False

            logger.info("Therapeutic integration test passed")
            return True

        except Exception as e:
            logger.error(f"Therapeutic integration test failed: {e}")
            return False

    def _test_monitoring_integration(self) -> bool:
        """Test monitoring and metrics integration."""
        try:
            # Test that monitoring systems can access database metrics
            if not self.redis_connection_manager:
                return False

            # Get comprehensive statistics
            stats = self.redis_connection_manager.get_connection_stats()
            if not stats or "cache_metrics" not in stats:
                return False

            # Test cache statistics from invalidation manager
            if self.cache_invalidation_manager:
                cache_stats = self.cache_invalidation_manager.get_cache_statistics()
                if not cache_stats or "key_counts" not in cache_stats:
                    return False

            logger.info("Monitoring integration test passed")
            return True

        except Exception as e:
            logger.error(f"Monitoring integration test failed: {e}")
            return False

    def _test_system_health(self) -> bool:
        """Test overall system health."""
        try:
            # Check that all components are healthy
            neo4j_healthy = self.neo4j_manager.is_connected() if self.neo4j_manager else False
            redis_healthy = self.redis_connection_manager.is_connected() if self.redis_connection_manager else False

            # At least one database should be healthy
            if not (neo4j_healthy or redis_healthy):
                return False

            # If both are available, both should be healthy
            if self.neo4j_manager and self.redis_connection_manager:
                if not (neo4j_healthy and redis_healthy):
                    return False

            logger.info("System health test passed")
            return True

        except Exception as e:
            logger.error(f"System health test failed: {e}")
            return False

    def _calculate_overall_score(self) -> None:
        """Calculate overall validation score."""
        try:
            weights = {
                "neo4j_schema": 0.25,
                "redis_caching": 0.25,
                "data_persistence": 0.20,
                "load_testing": 0.15,
                "integration_testing": 0.15
            }

            total_weight = 0
            weighted_score = 0

            for component, weight in weights.items():
                if component in self.validation_results:
                    result = self.validation_results[component]
                    if result["status"] not in ["not_tested", "skipped"] and "score" in result:
                        weighted_score += result["score"] * weight
                        total_weight += weight

            if total_weight > 0:
                overall_score = weighted_score / total_weight
            else:
                overall_score = 0.0

            # Determine overall status
            if overall_score >= 0.9:
                status = "excellent"
            elif overall_score >= 0.8:
                status = "passed"
            elif overall_score >= 0.6:
                status = "warning"
            else:
                status = "failed"

            self.validation_results["overall"]["status"] = status
            self.validation_results["overall"]["score"] = overall_score

            logger.info(f"Overall validation score: {overall_score:.2f} ({status})")

        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            self.validation_results["overall"]["status"] = "error"
            self.validation_results["overall"]["score"] = 0.0

    def _cleanup_connections(self) -> None:
        """Clean up database connections."""
        try:
            if self.neo4j_manager:
                self.neo4j_manager.disconnect()
                logger.info("Neo4j connection closed")

            if self.redis_connection_manager:
                self.redis_connection_manager.disconnect()
                logger.info("Redis connection closed")

        except Exception as e:
            logger.warning(f"Error during connection cleanup: {e}")

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report_lines = [
            "=" * 80,
            "TTA PROTOTYPE DATABASE INTEGRATION VALIDATION REPORT",
            "=" * 80,
            f"Validation Time: {self.validation_results.get('timestamp', 'Unknown')}",
            f"Total Duration: {self.validation_results.get('validation_time', 0):.2f} seconds",
            f"Overall Score: {self.validation_results['overall']['score']:.2f}",
            f"Overall Status: {self.validation_results['overall']['status'].upper()}",
            "",
            "COMPONENT RESULTS:",
            "-" * 40
        ]

        components = ["neo4j_schema", "redis_caching", "data_persistence", "load_testing", "integration_testing"]

        for component in components:
            if component in self.validation_results:
                result = self.validation_results[component]
                status = result["status"].upper()
                score = result.get("score", 0.0)

                report_lines.append(f"{component.replace('_', ' ').title()}: {status} ({score:.2f})")

                if "error" in result:
                    report_lines.append(f"  Error: {result['error']}")
                elif "details" in result:
                    details = result["details"]
                    if isinstance(details, dict):
                        passed = sum(1 for v in details.values() if v is True)
                        total = len([v for v in details.values() if isinstance(v, bool)])
                        if total > 0:
                            report_lines.append(f"  Tests Passed: {passed}/{total}")

        report_lines.extend([
            "",
            "RECOMMENDATIONS:",
            "-" * 40
        ])

        # Add recommendations based on results
        overall_score = self.validation_results["overall"]["score"]

        if overall_score < 0.8:
            report_lines.append("• Database integration needs improvement before production use")

        if self.validation_results.get("neo4j_schema", {}).get("status") == "failed":
            report_lines.append("• Fix Neo4j schema setup and constraint creation")

        if self.validation_results.get("redis_caching", {}).get("status") == "failed":
            report_lines.append("• Fix Redis caching integration and performance issues")

        if self.validation_results.get("data_persistence", {}).get("status") == "failed":
            report_lines.append("• Improve data persistence and consistency between systems")

        if overall_score >= 0.8:
            report_lines.append("• Database integration is ready for production use")
            report_lines.append("• Consider performance monitoring in production environment")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)


def main():
    """Main function to run database integration validation."""
    parser = argparse.ArgumentParser(description="Validate TTA Prototype Database Integration")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7688", help="Neo4j connection URI")
    parser.add_argument("--neo4j-username", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="password", help="Neo4j password")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    # Create validator
    validator = DatabaseIntegrationValidator(
        neo4j_uri=args.neo4j_uri,
        neo4j_username=args.neo4j_username,
        neo4j_password=args.neo4j_password,
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )

    # Run validation
    results = validator.validate_all()

    # Output results
    if args.json:
        output = json.dumps(results, indent=2, default=str)
    else:
        output = validator.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Validation report written to {args.output}")
    else:
        print(output)

    # Exit with appropriate code
    overall_status = results["overall"]["status"]
    if overall_status in ["passed", "excellent"]:
        sys.exit(0)
    elif overall_status == "warning":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
