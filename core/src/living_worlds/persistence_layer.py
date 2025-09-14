"""
Persistence Layer for TTA Living Worlds System

Manages cross-session world state storage and retrieval using Redis and Neo4j
for real-time data and persistent narrative structures.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import WorldPersistenceData, WorldState

logger = logging.getLogger(__name__)


class PersistenceLayer:
    """
    Manages persistent storage of world states across sessions.
    
    Uses Redis for real-time session data and Neo4j for persistent
    narrative structures and long-term world evolution tracking.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Storage configuration
        self.redis_client = None
        self.neo4j_driver = None
        self.redis_key_prefix = config.get("redis_key_prefix", "tta:living_worlds:")
        self.session_ttl = config.get("session_ttl", 86400)  # 24 hours
        
        # Persistence configuration
        self.auto_save_interval = config.get("auto_save_interval", 300)  # 5 minutes
        self.max_world_history = config.get("max_world_history", 100)
        
        # Metrics
        self.metrics = {
            "worlds_saved": 0,
            "worlds_loaded": 0,
            "persistence_operations": 0,
            "redis_operations": 0,
            "neo4j_operations": 0,
        }
        
        logger.info("PersistenceLayer initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Persistence Layer."""
        try:
            # Initialize Redis connection (placeholder)
            # In a real implementation, this would connect to Redis
            self.redis_client = MockRedisClient()
            
            # Initialize Neo4j connection (placeholder)
            # In a real implementation, this would connect to Neo4j
            self.neo4j_driver = MockNeo4jDriver()
            
            logger.info("PersistenceLayer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PersistenceLayer: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Persistence Layer."""
        try:
            # Close connections
            if self.redis_client:
                await self.redis_client.close()
            if self.neo4j_driver:
                await self.neo4j_driver.close()
            
            logger.info("PersistenceLayer shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during PersistenceLayer shutdown: {e}")
    
    async def create_world_persistence(self, world_id: str, player_id: str) -> bool:
        """
        Create persistence structure for a new world.
        
        Args:
            world_id: World identifier
            player_id: Player identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create world persistence data
            persistence_data = WorldPersistenceData(
                world_id=world_id,
                player_id=player_id,
                session_ids=[],
                first_session=datetime.utcnow(),
                last_session=datetime.utcnow(),
            )
            
            # Store in Redis for quick access
            redis_key = f"{self.redis_key_prefix}world:{world_id}"
            await self.redis_client.set(
                redis_key,
                json.dumps(self._serialize_persistence_data(persistence_data)),
                ex=self.session_ttl
            )
            
            # Store in Neo4j for long-term persistence
            await self.neo4j_driver.create_world_node(world_id, player_id)
            
            # Update metrics
            self.metrics["persistence_operations"] += 1
            self.metrics["redis_operations"] += 1
            self.metrics["neo4j_operations"] += 1
            
            logger.info(f"Created persistence for world {world_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create world persistence: {e}")
            return False
    
    async def save_world_state(self, world_state: WorldState) -> bool:
        """
        Save world state to persistent storage.
        
        Args:
            world_state: World state to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            world_id = world_state.world_id
            
            # Save to Redis for real-time access
            redis_key = f"{self.redis_key_prefix}state:{world_id}"
            state_data = self._serialize_world_state(world_state)
            
            await self.redis_client.set(
                redis_key,
                json.dumps(state_data),
                ex=self.session_ttl
            )
            
            # Save to Neo4j for persistent storage
            await self.neo4j_driver.save_world_state(world_id, state_data)
            
            # Update metrics
            self.metrics["worlds_saved"] += 1
            self.metrics["redis_operations"] += 1
            self.metrics["neo4j_operations"] += 1
            
            logger.debug(f"Saved world state for world {world_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False
    
    async def load_world_state(self, world_id: str, session_id: str) -> Optional[WorldState]:
        """
        Load world state from persistent storage.
        
        Args:
            world_id: World identifier
            session_id: Session identifier
            
        Returns:
            WorldState if found, None otherwise
        """
        try:
            # Try Redis first for recent states
            redis_key = f"{self.redis_key_prefix}state:{world_id}"
            redis_data = await self.redis_client.get(redis_key)
            
            if redis_data:
                state_data = json.loads(redis_data)
                world_state = self._deserialize_world_state(state_data)
                
                # Update session ID
                world_state.session_id = session_id
                
                self.metrics["redis_operations"] += 1
                logger.debug(f"Loaded world state from Redis for world {world_id}")
                return world_state
            
            # Fall back to Neo4j for persistent states
            state_data = await self.neo4j_driver.load_world_state(world_id)
            if state_data:
                world_state = self._deserialize_world_state(state_data)
                world_state.session_id = session_id
                
                self.metrics["neo4j_operations"] += 1
                logger.debug(f"Loaded world state from Neo4j for world {world_id}")
                return world_state
            
            # Update metrics
            self.metrics["worlds_loaded"] += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load world state: {e}")
            return None
    
    async def get_world_history(self, world_id: str) -> List[Dict[str, Any]]:
        """Get world evolution history."""
        try:
            history = await self.neo4j_driver.get_world_history(world_id)
            return history or []
        except Exception as e:
            logger.error(f"Failed to get world history: {e}")
            return []
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    # Private methods
    
    def _serialize_world_state(self, world_state: WorldState) -> Dict[str, Any]:
        """Serialize world state for storage."""
        return {
            "world_id": world_state.world_id,
            "session_id": world_state.session_id,
            "player_id": world_state.player_id,
            "state_type": world_state.state_type.value,
            "world_properties": world_state.world_properties,
            "character_states": world_state.character_states,
            "location_states": world_state.location_states,
            "object_states": world_state.object_states,
            "therapeutic_context": world_state.therapeutic_context,
            "therapeutic_goals": world_state.therapeutic_goals,
            "therapeutic_progress": world_state.therapeutic_progress,
            "evolution_preference_bias": world_state.evolution_preference_bias,
            "recent_events": world_state.recent_events,
            "created_at": world_state.created_at.isoformat(),
            "last_updated": world_state.last_updated.isoformat(),
            "version": world_state.version,
        }
    
    def _deserialize_world_state(self, data: Dict[str, Any]) -> WorldState:
        """Deserialize world state from storage."""
        from .models import WorldStateType
        
        return WorldState(
            world_id=data["world_id"],
            session_id=data["session_id"],
            player_id=data["player_id"],
            state_type=WorldStateType(data["state_type"]),
            world_properties=data.get("world_properties", {}),
            character_states=data.get("character_states", {}),
            location_states=data.get("location_states", {}),
            object_states=data.get("object_states", {}),
            therapeutic_context=data.get("therapeutic_context", {}),
            therapeutic_goals=data.get("therapeutic_goals", []),
            therapeutic_progress=data.get("therapeutic_progress", {}),
            evolution_preference_bias=data.get("evolution_preference_bias", {}),
            recent_events=data.get("recent_events", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            version=data.get("version", 1),
        )
    
    def _serialize_persistence_data(self, persistence_data: WorldPersistenceData) -> Dict[str, Any]:
        """Serialize persistence data for storage."""
        return {
            "world_id": persistence_data.world_id,
            "player_id": persistence_data.player_id,
            "session_ids": persistence_data.session_ids,
            "persistent_world_state": persistence_data.persistent_world_state,
            "character_continuity": persistence_data.character_continuity,
            "narrative_continuity": persistence_data.narrative_continuity,
            "therapeutic_continuity": persistence_data.therapeutic_continuity,
            "evolution_history": persistence_data.evolution_history,
            "choice_impact_history": persistence_data.choice_impact_history,
            "first_session": persistence_data.first_session.isoformat(),
            "last_session": persistence_data.last_session.isoformat(),
            "total_sessions": persistence_data.total_sessions,
            "total_playtime": persistence_data.total_playtime,
        }


# Mock classes for development (replace with real implementations)

class MockRedisClient:
    """Mock Redis client for development."""
    
    def __init__(self):
        self.data = {}
    
    async def set(self, key: str, value: str, ex: int = None):
        self.data[key] = value
    
    async def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    async def close(self):
        pass


class MockNeo4jDriver:
    """Mock Neo4j driver for development."""
    
    def __init__(self):
        self.data = {}
    
    async def create_world_node(self, world_id: str, player_id: str):
        self.data[f"world:{world_id}"] = {"player_id": player_id}
    
    async def save_world_state(self, world_id: str, state_data: Dict[str, Any]):
        self.data[f"state:{world_id}"] = state_data
    
    async def load_world_state(self, world_id: str) -> Optional[Dict[str, Any]]:
        return self.data.get(f"state:{world_id}")
    
    async def get_world_history(self, world_id: str) -> List[Dict[str, Any]]:
        return []
    
    async def close(self):
        pass
