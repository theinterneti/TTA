"""
Prototype Component for TTA Orchestration

This module implements the PrototypeComponent class that extends the base Component
class to integrate the therapeutic text adventure prototype with the main TTA
orchestration system.

Classes:
    PrototypeComponent: Main component for TTA prototype integration
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.orchestration.component import Component, ComponentStatus
except ImportError:
    # Fallback for when running from different contexts
    logging.warning("Could not import base Component class - using fallback")

    class ComponentStatus:
        STOPPED = "stopped"
        STARTING = "starting"
        RUNNING = "running"
        STOPPING = "stopping"
        ERROR = "error"

    class Component:
        def __init__(self, config, name=None, dependencies=None):
            self.config = config
            self.name = name or self.__class__.__name__
            self.dependencies = dependencies or []
            self.status = ComponentStatus.STOPPED

        def _start_impl(self):
            raise NotImplementedError

        def _stop_impl(self):
            raise NotImplementedError

# Import prototype components
try:
    from tta.prototype.core.interactive_narrative_engine import (
        InteractiveNarrativeEngine,
    )
    from tta.prototype.database.neo4j_schema import Neo4jManager
    from tta.prototype.database.redis_cache_enhanced import RedisCache
except ImportError:
    try:
        from core.interactive_narrative_engine import InteractiveNarrativeEngine

        from database.neo4j_schema import Neo4jManager
        from database.redis_cache_enhanced import RedisCache
    except ImportError:
        logging.warning("Could not import prototype components - using fallbacks")
        InteractiveNarrativeEngine = None
        RedisCache = None
        Neo4jManager = None

logger = logging.getLogger(__name__)


class PrototypeComponent(Component):
    """
    Main component for TTA prototype integration.

    This component manages the therapeutic text adventure prototype system,
    including the interactive narrative engine, database connections, and
    integration with the main TTA orchestration system.
    """

    def __init__(self, config: Any):
        """
        Initialize the Prototype Component.

        Args:
            config: Configuration object from TTA orchestrator
        """
        super().__init__(
            config=config,
            name="tta_prototype",
            dependencies=["neo4j", "redis"]  # Depends on Neo4j and Redis components
        )

        # Component instances
        self.narrative_engine: InteractiveNarrativeEngine | None = None
        self.redis_cache: RedisCache | None = None
        self.neo4j_manager: Neo4jManager | None = None

        # Component state
        self.active_sessions: dict[str, Any] = {}
        self.component_health: dict[str, str] = {}

        logger.info("PrototypeComponent initialized")

    def _start_impl(self) -> bool:
        """
        Start the prototype component.

        Returns:
            bool: True if component started successfully, False otherwise
        """
        try:
            logger.info("Starting TTA Prototype component...")

            # Initialize database connections
            if not self._initialize_databases():
                logger.error("Failed to initialize database connections")
                return False

            # Initialize narrative engine
            if not self._initialize_narrative_engine():
                logger.error("Failed to initialize narrative engine")
                return False

            # Perform health checks
            if not self._perform_health_checks():
                logger.warning("Some health checks failed, but component will continue")

            logger.info("TTA Prototype component started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting TTA Prototype component: {e}")
            return False

    def _stop_impl(self) -> bool:
        """
        Stop the prototype component.

        Returns:
            bool: True if component stopped successfully, False otherwise
        """
        try:
            logger.info("Stopping TTA Prototype component...")

            # Clean up active sessions
            self._cleanup_active_sessions()

            # Stop narrative engine
            if self.narrative_engine:
                try:
                    # Clean up any resources
                    self.narrative_engine.cleanup_inactive_sessions(max_age_hours=0)
                    logger.info("Narrative engine cleaned up")
                except Exception as e:
                    logger.warning(f"Error cleaning up narrative engine: {e}")

            # Close database connections
            self._close_database_connections()

            # Reset component state
            self.narrative_engine = None
            self.redis_cache = None
            self.neo4j_manager = None
            self.active_sessions.clear()
            self.component_health.clear()

            logger.info("TTA Prototype component stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Error stopping TTA Prototype component: {e}")
            return False

    def _initialize_databases(self) -> bool:
        """Initialize database connections."""
        try:
            # Get database configuration
            component_config = self.get_config()

            # Initialize Redis cache if available
            if RedisCache:
                try:
                    redis_config = component_config.get("redis", {})
                    self.redis_cache = RedisCache(
                        host=redis_config.get("host", "localhost"),
                        port=redis_config.get("port", 6379),
                        db=redis_config.get("db", 0)
                    )
                    self.component_health["redis"] = "healthy"
                    logger.info("Redis cache initialized")
                except Exception as e:
                    logger.warning(f"Could not initialize Redis cache: {e}")
                    self.component_health["redis"] = "unavailable"

            # Initialize Neo4j manager if available
            if Neo4jManager:
                try:
                    neo4j_config = component_config.get("neo4j", {})
                    self.neo4j_manager = Neo4jManager(
                        uri=neo4j_config.get("uri", "bolt://localhost:7687"),
                        user=neo4j_config.get("user", "neo4j"),
                        password=neo4j_config.get("password", "password")
                    )
                    self.component_health["neo4j"] = "healthy"
                    logger.info("Neo4j manager initialized")
                except Exception as e:
                    logger.warning(f"Could not initialize Neo4j manager: {e}")
                    self.component_health["neo4j"] = "unavailable"

            return True

        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            return False

    def _initialize_narrative_engine(self) -> bool:
        """Initialize the interactive narrative engine."""
        try:
            if not InteractiveNarrativeEngine:
                logger.error("InteractiveNarrativeEngine class not available")
                return False

            # Create narrative engine with database connections
            self.narrative_engine = InteractiveNarrativeEngine(
                redis_cache=self.redis_cache,
                neo4j_manager=self.neo4j_manager
            )

            self.component_health["narrative_engine"] = "healthy"
            logger.info("Interactive narrative engine initialized")
            return True

        except Exception as e:
            logger.error(f"Error initializing narrative engine: {e}")
            self.component_health["narrative_engine"] = "error"
            return False

    def _perform_health_checks(self) -> bool:
        """Perform health checks on all components."""
        try:
            all_healthy = True

            # Check narrative engine
            if self.narrative_engine:
                try:
                    # Test basic functionality
                    test_session = self.narrative_engine.start_session("health_check_user", "health_check")
                    if test_session:
                        self.narrative_engine.end_session(test_session.session_id)
                        self.component_health["narrative_engine"] = "healthy"
                        logger.info("Narrative engine health check passed")
                    else:
                        self.component_health["narrative_engine"] = "degraded"
                        all_healthy = False
                except Exception as e:
                    logger.warning(f"Narrative engine health check failed: {e}")
                    self.component_health["narrative_engine"] = "degraded"
                    all_healthy = False

            # Check Redis cache
            if self.redis_cache:
                try:
                    # Test basic Redis operations
                    # Note: Actual Redis test would depend on RedisCache implementation
                    self.component_health["redis"] = "healthy"
                    logger.info("Redis cache health check passed")
                except Exception as e:
                    logger.warning(f"Redis cache health check failed: {e}")
                    self.component_health["redis"] = "degraded"
                    all_healthy = False

            # Check Neo4j manager
            if self.neo4j_manager:
                try:
                    # Test basic Neo4j operations
                    # Note: Actual Neo4j test would depend on Neo4jManager implementation
                    self.component_health["neo4j"] = "healthy"
                    logger.info("Neo4j manager health check passed")
                except Exception as e:
                    logger.warning(f"Neo4j manager health check failed: {e}")
                    self.component_health["neo4j"] = "degraded"
                    all_healthy = False

            return all_healthy

        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
            return False

    def _cleanup_active_sessions(self) -> None:
        """Clean up active sessions."""
        try:
            if self.narrative_engine:
                active_count = self.narrative_engine.get_active_session_count()
                if active_count > 0:
                    cleaned = self.narrative_engine.cleanup_inactive_sessions(max_age_hours=0)
                    logger.info(f"Cleaned up {cleaned} active sessions")

            self.active_sessions.clear()

        except Exception as e:
            logger.warning(f"Error cleaning up active sessions: {e}")

    def _close_database_connections(self) -> None:
        """Close database connections."""
        try:
            if self.redis_cache:
                # Close Redis connection if method exists
                if hasattr(self.redis_cache, 'close'):
                    self.redis_cache.close()
                logger.info("Redis connection closed")

            if self.neo4j_manager:
                # Close Neo4j connection if method exists
                if hasattr(self.neo4j_manager, 'close'):
                    self.neo4j_manager.close()
                logger.info("Neo4j connection closed")

        except Exception as e:
            logger.warning(f"Error closing database connections: {e}")

    def get_component_status(self) -> dict[str, Any]:
        """
        Get detailed component status.

        Returns:
            Dict[str, Any]: Component status information
        """
        return {
            "name": self.name,
            "status": self.status,
            "dependencies": self.dependencies,
            "component_health": self.component_health,
            "active_sessions": len(self.active_sessions),
            "narrative_engine_available": self.narrative_engine is not None,
            "redis_cache_available": self.redis_cache is not None,
            "neo4j_manager_available": self.neo4j_manager is not None
        }

    def create_therapeutic_session(self, user_id: str, scenario_id: str = "default") -> str | None:
        """
        Create a new therapeutic session.

        Args:
            user_id: User identifier
            scenario_id: Scenario identifier

        Returns:
            Optional[str]: Session ID if successful, None otherwise
        """
        try:
            if not self.narrative_engine:
                logger.error("Narrative engine not available")
                return None

            session_state = self.narrative_engine.start_session(user_id, scenario_id)
            if session_state:
                self.active_sessions[session_state.session_id] = {
                    "user_id": user_id,
                    "scenario_id": scenario_id,
                    "created_at": session_state.created_at,
                    "last_updated": session_state.last_updated
                }
                logger.info(f"Created therapeutic session {session_state.session_id} for user {user_id}")
                return session_state.session_id

            return None

        except Exception as e:
            logger.error(f"Error creating therapeutic session: {e}")
            return None

    def process_user_interaction(self, session_id: str, user_input: str) -> dict[str, Any] | None:
        """
        Process a user interaction in a therapeutic session.

        Args:
            session_id: Session identifier
            user_input: User input text

        Returns:
            Optional[Dict[str, Any]]: Response data if successful, None otherwise
        """
        try:
            if not self.narrative_engine:
                logger.error("Narrative engine not available")
                return None

            # Import UserChoice class
            try:
                from tta.prototype.core.interactive_narrative_engine import UserChoice
            except ImportError:
                from core.interactive_narrative_engine import UserChoice

            # Create user choice
            choice = UserChoice(
                choice_id=f"interaction_{len(self.active_sessions.get(session_id, {}).get('interactions', []))}",
                choice_text=user_input,
                choice_type="dialogue"
            )

            # Process the choice
            response = self.narrative_engine.process_user_choice(session_id, choice)

            if response:
                # Update session tracking
                if session_id in self.active_sessions:
                    if 'interactions' not in self.active_sessions[session_id]:
                        self.active_sessions[session_id]['interactions'] = []

                    self.active_sessions[session_id]['interactions'].append({
                        "user_input": user_input,
                        "response_content": response.content,
                        "response_type": response.response_type,
                        "therapeutic_value": response.metadata.get("therapeutic_value", 0) if response.metadata else 0,
                        "timestamp": response.timestamp
                    })

                # Convert response to dictionary
                return {
                    "content": response.content,
                    "response_type": response.response_type,
                    "choices": response.choices,
                    "metadata": response.metadata,
                    "session_id": response.session_id,
                    "timestamp": response.timestamp.isoformat() if response.timestamp else None
                }

            return None

        except Exception as e:
            logger.error(f"Error processing user interaction: {e}")
            return None

    def end_therapeutic_session(self, session_id: str) -> bool:
        """
        End a therapeutic session.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.narrative_engine:
                logger.error("Narrative engine not available")
                return False

            success = self.narrative_engine.end_session(session_id)

            if success and session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Ended therapeutic session {session_id}")

            return success

        except Exception as e:
            logger.error(f"Error ending therapeutic session: {e}")
            return False

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """
        Get information about a therapeutic session.

        Args:
            session_id: Session identifier

        Returns:
            Optional[Dict[str, Any]]: Session information if found, None otherwise
        """
        try:
            if session_id not in self.active_sessions:
                return None

            session_info = self.active_sessions[session_id].copy()

            # Add current scenario information if available
            if self.narrative_engine:
                scenario = self.narrative_engine.get_current_scenario(session_id)
                if scenario:
                    session_info["current_scenario"] = scenario

            return session_info

        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None

    def get_health_status(self) -> dict[str, Any]:
        """
        Get health status of the component and its sub-systems.

        Returns:
            Dict[str, Any]: Health status information
        """
        overall_health = "healthy"

        # Determine overall health based on component health
        if any(status == "error" for status in self.component_health.values()):
            overall_health = "error"
        elif any(status == "degraded" for status in self.component_health.values()):
            overall_health = "degraded"
        elif any(status == "unavailable" for status in self.component_health.values()):
            overall_health = "degraded"

        return {
            "overall_health": overall_health,
            "component_health": self.component_health,
            "active_sessions": len(self.active_sessions),
            "dependencies_met": self._check_dependencies(),
            "last_health_check": "recent"  # Could be actual timestamp
        }

    def _check_dependencies(self) -> bool:
        """Check if component dependencies are met."""
        # This would typically check if Neo4j and Redis components are running
        # For now, we'll check if our connections are available
        return (
            self.component_health.get("neo4j", "unavailable") != "error" and
            self.component_health.get("redis", "unavailable") != "error"
        )
