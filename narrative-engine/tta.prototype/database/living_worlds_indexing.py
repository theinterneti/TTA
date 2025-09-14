"""
Living Worlds Database Indexing and Query Optimization

This module provides advanced indexing strategies and query optimization
for Living Worlds features, focusing on efficient timeline queries,
relationship traversal, and world state operations.

Classes:
    LivingWorldsIndexManager: Manages advanced indexing for Living Worlds
    QueryOptimizer: Provides optimized queries for common operations
"""

import logging
from datetime import datetime
from typing import Any

try:
    from neo4j import Driver, Session
    from neo4j.exceptions import ClientError

    # Define Neo4jConnectionError for consistency
    class Neo4jConnectionError(Exception):
        """Exception raised when Neo4j connection fails."""

        pass

except ImportError:
    Driver = None
    Session = None
    ClientError = Exception

    class Neo4jConnectionError(Exception):
        """Exception raised when Neo4j connection fails."""

        pass


try:
    from .living_worlds_schema import LivingWorldsSchemaManager
except ImportError:
    from living_worlds_schema import LivingWorldsSchemaManager

logger = logging.getLogger(__name__)


class LivingWorldsIndexManager(LivingWorldsSchemaManager):
    """
    Manages advanced indexing strategies for Living Worlds features.

    This class extends the base schema manager to provide specialized
    indexing for timeline queries, relationship traversal, and performance
    optimization for large-scale Living Worlds data.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7688",
        username: str = "neo4j",
        password: str = "password",
    ):
        """Initialize Living Worlds index manager."""
        super().__init__(uri, username, password)

    def create_advanced_indexes(self) -> bool:
        """
        Create advanced indexes for optimal Living Worlds performance.

        Returns:
            bool: True if all advanced indexes were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        advanced_indexes = [
            # Full-text search indexes for content discovery
            "CREATE FULLTEXT INDEX timeline_event_content IF NOT EXISTS FOR (e:TimelineEvent) ON EACH [e.title, e.description]",
            "CREATE FULLTEXT INDEX character_content IF NOT EXISTS FOR (c:Character) ON EACH [c.name, c.background_story]",
            "CREATE FULLTEXT INDEX location_content IF NOT EXISTS FOR (l:Location) ON EACH [l.name, l.description]",
            # Range indexes for temporal queries
            "CREATE RANGE INDEX event_timestamp_range IF NOT EXISTS FOR (e:TimelineEvent) ON (e.timestamp)",
            "CREATE RANGE INDEX world_time_range IF NOT EXISTS FOR (w:World) ON (w.current_time)",
            "CREATE RANGE INDEX relationship_date_range IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.established_date)",
            # Point indexes for exact lookups
            "CREATE POINT INDEX event_significance_point IF NOT EXISTS FOR (e:TimelineEvent) ON (e.significance_level)",
            "CREATE POINT INDEX relationship_strength_point IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.strength)",
            # Vector indexes for similarity searches (if supported)
            # Note: These require Neo4j 5.0+ and vector support
            # "CREATE VECTOR INDEX event_embedding IF NOT EXISTS FOR (e:TimelineEvent) ON (e.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            # Composite indexes for complex queries
            "CREATE INDEX timeline_entity_time_composite IF NOT EXISTS FOR (e:TimelineEvent) ON (e.timeline_id, e.timestamp, e.significance_level)",
            "CREATE INDEX character_relationship_composite IF NOT EXISTS FOR (r:FamilyRelationship) ON (r.from_character_id, r.relationship_type, r.is_active)",
            "CREATE INDEX world_entity_status_composite IF NOT EXISTS FOR (w:World) ON (w.world_id, w.world_status, w.last_evolution)",
            # Lookup indexes for array properties
            "CREATE LOOKUP INDEX event_participants_lookup IF NOT EXISTS FOR (e:TimelineEvent) ON EACH e.participants",
            "CREATE LOOKUP INDEX event_tags_lookup IF NOT EXISTS FOR (e:TimelineEvent) ON EACH e.tags",
            "CREATE LOOKUP INDEX event_consequences_lookup IF NOT EXISTS FOR (e:TimelineEvent) ON EACH e.consequences",
        ]

        try:
            with self.driver.session() as session:
                for index in advanced_indexes:
                    try:
                        session.run(index)
                        logger.debug(f"Created advanced index: {index}")
                    except ClientError as e:
                        if (
                            "already exists" in str(e).lower()
                            or "equivalent" in str(e).lower()
                        ):
                            logger.debug(f"Advanced index already exists: {index}")
                        else:
                            logger.warning(
                                f"Failed to create advanced index: {index}, Error: {e}"
                            )
                            # Don't fail completely for advanced indexes
                            continue

            logger.info("Advanced indexes creation completed")
            return True

        except Exception as e:
            logger.error(f"Error creating advanced indexes: {e}")
            return False

    def create_performance_constraints(self) -> bool:
        """
        Create performance-oriented constraints and optimizations.

        Returns:
            bool: True if all performance constraints were created successfully
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")

        performance_constraints = [
            # Ensure timeline events are properly linked
            "CREATE CONSTRAINT timeline_event_link IF NOT EXISTS FOR ()-[r:CONTAINS_EVENT]-() REQUIRE r IS NOT NULL",
            # Ensure family relationships are bidirectional when needed
            "CREATE CONSTRAINT family_relationship_link IF NOT EXISTS FOR ()-[r:HAS_FAMILY_RELATIONSHIP]-() REQUIRE r IS NOT NULL",
            # Ensure world entities are properly linked
            "CREATE CONSTRAINT world_entity_link IF NOT EXISTS FOR ()-[r:CONTAINS_CHARACTER|CONTAINS_LOCATION|CONTAINS_OBJECT]-() REQUIRE r IS NOT NULL",
        ]

        try:
            with self.driver.session() as session:
                for constraint in performance_constraints:
                    try:
                        session.run(constraint)
                        logger.debug(f"Created performance constraint: {constraint}")
                    except ClientError as e:
                        if "already exists" in str(e).lower():
                            logger.debug(
                                f"Performance constraint already exists: {constraint}"
                            )
                        else:
                            logger.warning(
                                f"Failed to create performance constraint: {constraint}, Error: {e}"
                            )
                            continue

            logger.info("Performance constraints creation completed")
            return True

        except Exception as e:
            logger.error(f"Error creating performance constraints: {e}")
            return False

    def analyze_query_performance(self) -> dict[str, Any]:
        """
        Analyze query performance and provide optimization recommendations.

        Returns:
            Dict[str, Any]: Performance analysis results
        """
        if not self.driver:
            return {"error": "Not connected to Neo4j"}

        analysis_queries = [
            {
                "name": "Timeline Event Count",
                "query": "MATCH (e:TimelineEvent) RETURN count(e) as count",
            },
            {
                "name": "Timeline Count",
                "query": "MATCH (t:Timeline) RETURN count(t) as count",
            },
            {
                "name": "Family Relationship Count",
                "query": "MATCH (r:FamilyRelationship) RETURN count(r) as count",
            },
            {
                "name": "World State Count",
                "query": "MATCH (w:World) RETURN count(w) as count",
            },
            {
                "name": "Average Events per Timeline",
                "query": """
                MATCH (t:Timeline)-[:CONTAINS_EVENT]->(e:TimelineEvent)
                WITH t, count(e) as event_count
                RETURN avg(event_count) as avg_events_per_timeline
                """,
            },
            {
                "name": "Most Active Characters",
                "query": """
                MATCH (e:TimelineEvent)
                UNWIND e.participants as participant
                RETURN participant, count(*) as event_count
                ORDER BY event_count DESC
                LIMIT 10
                """,
            },
        ]

        results = {}

        try:
            with self.driver.session() as session:
                for analysis in analysis_queries:
                    try:
                        start_time = datetime.now()
                        result = session.run(analysis["query"])
                        records = list(result)
                        end_time = datetime.now()

                        results[analysis["name"]] = {
                            "data": [dict(record) for record in records],
                            "execution_time_ms": (end_time - start_time).total_seconds()
                            * 1000,
                            "record_count": len(records),
                        }
                    except Exception as e:
                        results[analysis["name"]] = {"error": str(e)}

            # Add recommendations based on results
            recommendations = self._generate_performance_recommendations(results)
            results["recommendations"] = recommendations

            return results

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}

    def optimize_database(self) -> bool:
        """
        Perform database optimization operations.

        Returns:
            bool: True if optimization was successful
        """
        if not self.driver:
            return False

        optimization_queries = [
            # Update statistics for query planner
            "CALL db.stats.collect()",
            # Analyze index usage
            "CALL db.indexes()",
            # Clean up unused indexes (if any)
            # Note: This would require specific logic to identify unused indexes
        ]

        try:
            with self.driver.session() as session:
                for query in optimization_queries:
                    try:
                        session.run(query)
                        logger.debug(f"Executed optimization query: {query}")
                    except ClientError as e:
                        logger.warning(
                            f"Optimization query failed: {query}, Error: {e}"
                        )
                        continue

            logger.info("Database optimization completed")
            return True

        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False

    def _generate_performance_recommendations(
        self, analysis_results: dict[str, Any]
    ) -> list[str]:
        """Generate performance recommendations based on analysis results."""
        recommendations = []

        # Check timeline event count
        if "Timeline Event Count" in analysis_results:
            event_data = analysis_results["Timeline Event Count"]["data"]
            if event_data and event_data[0].get("count", 0) > 100000:
                recommendations.append(
                    "Consider implementing event archiving for timelines with >100k events"
                )

        # Check average events per timeline
        if "Average Events per Timeline" in analysis_results:
            avg_data = analysis_results["Average Events per Timeline"]["data"]
            if avg_data and avg_data[0].get("avg_events_per_timeline", 0) > 1000:
                recommendations.append(
                    "Consider implementing timeline event pruning for timelines with >1000 events"
                )

        # Check execution times
        slow_queries = []
        for name, result in analysis_results.items():
            if isinstance(result, dict) and "execution_time_ms" in result:
                if result["execution_time_ms"] > 1000:  # > 1 second
                    slow_queries.append(name)

        if slow_queries:
            recommendations.append(
                f"Consider optimizing slow queries: {', '.join(slow_queries)}"
            )

        return recommendations

    def setup_complete_indexing(self) -> bool:
        """
        Set up complete indexing including base, Living Worlds, and advanced indexes.

        Returns:
            bool: True if complete indexing setup was successful
        """
        logger.info("Setting up complete Living Worlds indexing")

        try:
            # Set up base Living Worlds schema
            if not self.setup_living_worlds_schema():
                logger.error("Failed to set up base Living Worlds schema")
                return False

            # Create advanced indexes
            if not self.create_advanced_indexes():
                logger.warning("Some advanced indexes failed to create")
                # Don't fail completely for advanced indexes

            # Create performance constraints
            if not self.create_performance_constraints():
                logger.warning("Some performance constraints failed to create")
                # Don't fail completely for performance constraints

            # Optimize database
            self.optimize_database()

            logger.info("Complete Living Worlds indexing setup completed")
            return True

        except Exception as e:
            logger.error(f"Error setting up complete indexing: {e}")
            return False


class QueryOptimizer:
    """
    Provides optimized queries for common Living Worlds operations.

    This class contains pre-optimized Cypher queries for frequent operations
    like timeline traversal, relationship discovery, and world state queries.
    """

    def __init__(self, driver: Driver):
        """
        Initialize query optimizer.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def get_character_timeline_summary(
        self, character_id: str, days_back: int = 30
    ) -> dict[str, Any]:
        """
        Get an optimized timeline summary for a character.

        Args:
            character_id: Character identifier
            days_back: Number of days to look back

        Returns:
            Dict[str, Any]: Timeline summary data
        """
        query = """
        MATCH (t:Timeline {entity_id: $character_id, entity_type: 'character'})
        OPTIONAL MATCH (t)-[:CONTAINS_EVENT]->(e:TimelineEvent)
        WHERE e.timestamp >= datetime() - duration({days: $days_back})
        WITH t, e
        ORDER BY e.timestamp DESC
        WITH t, collect(e)[0..10] as recent_events,
             collect(e) as all_events
        RETURN t.timeline_id as timeline_id,
               t.entity_id as entity_id,
               size(all_events) as total_events,
               size(recent_events) as recent_event_count,
               recent_events,
               [event IN all_events WHERE event.significance_level >= 8 | event][0..5] as significant_events,
               avg([event IN all_events | event.emotional_impact]) as avg_emotional_impact
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, character_id=character_id, days_back=days_back
                )
                record = result.single()
                return dict(record) if record else {}
        except Exception as e:
            logger.error(f"Error getting character timeline summary: {e}")
            return {}

    def get_family_network(
        self, character_id: str, max_depth: int = 3
    ) -> dict[str, Any]:
        """
        Get an optimized family network for a character.

        Args:
            character_id: Character identifier
            max_depth: Maximum relationship depth to traverse

        Returns:
            Dict[str, Any]: Family network data
        """
        query = """
        MATCH (root:Character {character_id: $character_id})
        CALL {
            WITH root
            MATCH path = (root)-[:HAS_FAMILY_RELATIONSHIP*1..$max_depth]-(related:Character)
            WHERE all(r IN relationships(path) WHERE r.is_active = true)
            RETURN related,
                   [r IN relationships(path) | {type: r.relationship_type, strength: r.strength}] as relationship_path,
                   length(path) as distance
        }
        WITH root, related, relationship_path, distance
        ORDER BY distance, related.name
        RETURN root.character_id as root_character,
               collect({
                   character: related,
                   relationship_path: relationship_path,
                   distance: distance
               }) as family_members
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, character_id=character_id, max_depth=max_depth
                )
                record = result.single()
                return dict(record) if record else {}
        except Exception as e:
            logger.error(f"Error getting family network: {e}")
            return {}

    def get_world_activity_summary(
        self, world_id: str, hours_back: int = 24
    ) -> dict[str, Any]:
        """
        Get an optimized activity summary for a world.

        Args:
            world_id: World identifier
            hours_back: Number of hours to look back

        Returns:
            Dict[str, Any]: World activity summary
        """
        query = """
        MATCH (w:World {world_id: $world_id})
        OPTIONAL MATCH (w)-[:CONTAINS_CHARACTER]->(c:Character)
        OPTIONAL MATCH (w)-[:CONTAINS_LOCATION]->(l:Location)
        OPTIONAL MATCH (w)-[:CONTAINS_OBJECT]->(o:Object)

        // Get recent events in this world
        OPTIONAL MATCH (t:Timeline)-[:CONTAINS_EVENT]->(e:TimelineEvent)
        WHERE e.timestamp >= datetime() - duration({hours: $hours_back})
        AND (
            t.entity_id IN [c.character_id] OR
            t.entity_id IN [l.location_id] OR
            t.entity_id IN [o.object_id]
        )

        WITH w, c, l, o, e
        ORDER BY e.timestamp DESC

        RETURN w.world_id as world_id,
               w.world_name as world_name,
               w.world_status as world_status,
               count(DISTINCT c) as character_count,
               count(DISTINCT l) as location_count,
               count(DISTINCT o) as object_count,
               count(e) as recent_events,
               collect(DISTINCT e)[0..10] as latest_events,
               avg(e.emotional_impact) as avg_emotional_impact
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, world_id=world_id, hours_back=hours_back)
                record = result.single()
                return dict(record) if record else {}
        except Exception as e:
            logger.error(f"Error getting world activity summary: {e}")
            return {}

    def find_related_events(
        self, event_id: str, similarity_threshold: float = 0.7
    ) -> list[dict[str, Any]]:
        """
        Find events related to a given event based on participants and context.

        Args:
            event_id: Event identifier
            similarity_threshold: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            List[Dict[str, Any]]: List of related events
        """
        query = """
        MATCH (source:TimelineEvent {event_id: $event_id})
        MATCH (related:TimelineEvent)
        WHERE related <> source

        // Calculate similarity based on shared participants
        WITH source, related,
             size([p IN source.participants WHERE p IN related.participants]) as shared_participants,
             size(source.participants + related.participants) as total_participants

        WHERE shared_participants > 0

        // Calculate similarity score
        WITH source, related, shared_participants, total_participants,
             toFloat(shared_participants * 2) / toFloat(total_participants) as participant_similarity

        // Add temporal proximity bonus
        WITH source, related, participant_similarity,
             1.0 - (abs(duration.between(source.timestamp, related.timestamp).days) / 365.0) as temporal_proximity

        // Combine similarity scores
        WITH source, related,
             (participant_similarity * 0.7 + temporal_proximity * 0.3) as overall_similarity

        WHERE overall_similarity >= $similarity_threshold

        RETURN related,
               overall_similarity,
               shared_participants
        ORDER BY overall_similarity DESC
        LIMIT 20
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query, event_id=event_id, similarity_threshold=similarity_threshold
                )
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error finding related events: {e}")
            return []

    def get_timeline_statistics(self, timeline_id: str) -> dict[str, Any]:
        """
        Get comprehensive statistics for a timeline.

        Args:
            timeline_id: Timeline identifier

        Returns:
            Dict[str, Any]: Timeline statistics
        """
        query = """
        MATCH (t:Timeline {timeline_id: $timeline_id})
        OPTIONAL MATCH (t)-[:CONTAINS_EVENT]->(e:TimelineEvent)

        WITH t, e
        ORDER BY e.timestamp

        WITH t, collect(e) as events

        RETURN t.timeline_id as timeline_id,
               t.entity_id as entity_id,
               t.entity_type as entity_type,
               size(events) as total_events,

               // Temporal statistics
               CASE WHEN size(events) > 0
                    THEN events[0].timestamp
                    ELSE null END as earliest_event,
               CASE WHEN size(events) > 0
                    THEN events[-1].timestamp
                    ELSE null END as latest_event,

               // Significance statistics
               avg([event IN events | event.significance_level]) as avg_significance,
               max([event IN events | event.significance_level]) as max_significance,
               min([event IN events | event.significance_level]) as min_significance,

               // Emotional statistics
               avg([event IN events | event.emotional_impact]) as avg_emotional_impact,
               max([event IN events | event.emotional_impact]) as max_emotional_impact,
               min([event IN events | event.emotional_impact]) as min_emotional_impact,

               // Event type distribution
               [type IN ['meeting', 'conversation', 'achievement', 'learning', 'conflict'] |
                {type: type, count: size([event IN events WHERE event.event_type = type])}
               ] as event_type_distribution,

               // Most frequent participants
               apoc.coll.frequencies(apoc.coll.flatten([event IN events | event.participants]))[0..5] as top_participants
        """

        try:
            with self.driver.session() as session:
                result = session.run(query, timeline_id=timeline_id)
                record = result.single()
                return dict(record) if record else {}
        except Exception as e:
            logger.error(f"Error getting timeline statistics: {e}")
            return {}


# Utility functions for indexing and optimization
def setup_complete_living_worlds_indexing(
    uri: str = "bolt://localhost:7688",
    username: str = "neo4j",
    password: str = "password",
) -> bool:
    """
    Utility function to set up complete Living Worlds indexing.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        bool: True if indexing setup was successful
    """
    try:
        with LivingWorldsIndexManager(uri, username, password) as index_manager:
            return index_manager.setup_complete_indexing()
    except Exception as e:
        logger.error(f"Failed to setup complete Living Worlds indexing: {e}")
        return False


def analyze_living_worlds_performance(
    uri: str = "bolt://localhost:7688",
    username: str = "neo4j",
    password: str = "password",
) -> dict[str, Any]:
    """
    Utility function to analyze Living Worlds query performance.

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        Dict[str, Any]: Performance analysis results
    """
    try:
        with LivingWorldsIndexManager(uri, username, password) as index_manager:
            return index_manager.analyze_query_performance()
    except Exception as e:
        logger.error(f"Failed to analyze Living Worlds performance: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Setup complete indexing
    if setup_complete_living_worlds_indexing():
        print("Complete Living Worlds indexing setup completed successfully")

        # Analyze performance
        performance_results = analyze_living_worlds_performance()
        print(f"Performance analysis: {performance_results}")
    else:
        print("Complete Living Worlds indexing setup failed")
