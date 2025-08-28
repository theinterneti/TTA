"""
Nexus Codex Redis Caching Service.

This module provides Redis-based caching for real-time features in The Nexus Codex,
including world state management, player sessions, and community activity.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import redis.asyncio as redis

from ..models.nexus import (
    StoryWorld, StorySphere, StoryWeaver, ActivityEvent,
    NexusStateResponse, VisualState
)

logger = logging.getLogger(__name__)


class NexusCacheService:
    """Redis caching service for Nexus Codex real-time features."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize with Redis client."""
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour default TTL
    
    # World State Management
    async def set_world_state(self, world_id: str, state_data: Dict[str, Any], ttl: int = None) -> bool:
        """Set current state for a world."""
        try:
            key = f"world:{world_id}:state"
            ttl = ttl or self.default_ttl
            
            # Add timestamp to state data
            state_data["last_updated"] = datetime.now().isoformat()
            
            await self.redis.hset(key, mapping=state_data)
            await self.redis.expire(key, ttl)
            
            logger.debug(f"Set world state for {world_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set world state for {world_id}: {e}")
            return False
    
    async def get_world_state(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Get current state for a world."""
        try:
            key = f"world:{world_id}:state"
            state_data = await self.redis.hgetall(key)
            
            if not state_data:
                return None
            
            # Convert bytes to strings
            return {k.decode(): v.decode() for k, v in state_data.items()}
            
        except Exception as e:
            logger.error(f"Failed to get world state for {world_id}: {e}")
            return None
    
    async def update_world_strength(self, world_id: str, new_strength: float) -> bool:
        """Update world strength level in cache."""
        try:
            key = f"world:{world_id}:state"
            await self.redis.hset(key, "narrative_strength", str(new_strength))
            await self.redis.hset(key, "last_interaction", datetime.now().isoformat())
            
            # Update world rankings
            await self.redis.zadd("nexus:world_rankings:strength", {world_id: new_strength})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update world strength for {world_id}: {e}")
            return False
    
    # Player Session Management
    async def set_player_session(self, player_id: str, session_data: Dict[str, Any]) -> bool:
        """Set player session data."""
        try:
            key = f"player:{player_id}:session"
            session_data["session_start"] = session_data.get("session_start", datetime.now().isoformat())
            session_data["last_activity"] = datetime.now().isoformat()
            
            await self.redis.hset(key, mapping=session_data)
            await self.redis.expire(key, 86400)  # 24 hours
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set player session for {player_id}: {e}")
            return False
    
    async def get_player_session(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player session data."""
        try:
            key = f"player:{player_id}:session"
            session_data = await self.redis.hgetall(key)
            
            if not session_data:
                return None
            
            return {k.decode(): v.decode() for k, v in session_data.items()}
            
        except Exception as e:
            logger.error(f"Failed to get player session for {player_id}: {e}")
            return None
    
    async def update_player_world_progress(self, player_id: str, world_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update player's progress in a specific world."""
        try:
            session_key = f"player:{player_id}:session"
            progress_key = f"world_progress.{world_id}"
            
            progress_json = json.dumps(progress_data)
            await self.redis.hset(session_key, progress_key, progress_json)
            await self.redis.hset(session_key, "last_activity", datetime.now().isoformat())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update world progress for {player_id} in {world_id}: {e}")
            return False
    
    # Nexus Real-time State
    async def set_nexus_realtime_state(self, state_data: Dict[str, Any]) -> bool:
        """Set real-time Nexus Codex state."""
        try:
            key = "nexus:realtime"
            state_data["timestamp"] = datetime.now().isoformat()
            
            await self.redis.hset(key, mapping=state_data)
            await self.redis.expire(key, 300)  # 5 minutes
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set nexus realtime state: {e}")
            return False
    
    async def get_nexus_realtime_state(self) -> Optional[Dict[str, Any]]:
        """Get real-time Nexus Codex state."""
        try:
            key = "nexus:realtime"
            state_data = await self.redis.hgetall(key)
            
            if not state_data:
                return None
            
            return {k.decode(): v.decode() for k, v in state_data.items()}
            
        except Exception as e:
            logger.error(f"Failed to get nexus realtime state: {e}")
            return None
    
    async def increment_active_players(self, world_id: Optional[str] = None) -> int:
        """Increment active player count."""
        try:
            # Global active players
            global_count = await self.redis.incr("nexus:active_players")
            await self.redis.expire("nexus:active_players", 300)
            
            # World-specific active players
            if world_id:
                world_key = f"world:{world_id}:active_players"
                await self.redis.incr(world_key)
                await self.redis.expire(world_key, 300)
            
            return global_count
            
        except Exception as e:
            logger.error(f"Failed to increment active players: {e}")
            return 0
    
    async def decrement_active_players(self, world_id: Optional[str] = None) -> int:
        """Decrement active player count."""
        try:
            # Global active players
            global_count = await self.redis.decr("nexus:active_players")
            if global_count < 0:
                await self.redis.set("nexus:active_players", 0)
                global_count = 0
            
            # World-specific active players
            if world_id:
                world_key = f"world:{world_id}:active_players"
                world_count = await self.redis.decr(world_key)
                if world_count < 0:
                    await self.redis.set(world_key, 0)
            
            return global_count
            
        except Exception as e:
            logger.error(f"Failed to decrement active players: {e}")
            return 0
    
    # World Rankings and Discovery
    async def update_world_ranking(self, world_id: str, category: str, score: float) -> bool:
        """Update world ranking in a specific category."""
        try:
            key = f"nexus:world_rankings:{category}"
            await self.redis.zadd(key, {world_id: score})
            await self.redis.expire(key, 3600)  # 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update world ranking for {world_id} in {category}: {e}")
            return False
    
    async def get_top_worlds(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-ranked worlds in a category."""
        try:
            key = f"nexus:world_rankings:{category}"
            results = await self.redis.zrevrange(key, 0, limit - 1, withscores=True)
            
            top_worlds = []
            for world_id, score in results:
                top_worlds.append({
                    "world_id": world_id.decode(),
                    "score": score,
                    "category": category
                })
            
            return top_worlds
            
        except Exception as e:
            logger.error(f"Failed to get top worlds for {category}: {e}")
            return []
    
    # Real-time Events
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Publish real-time event to subscribers."""
        try:
            channel = f"nexus:events:{event_type}"
            event_data["timestamp"] = datetime.now().isoformat()
            event_json = json.dumps(event_data)
            
            await self.redis.publish(channel, event_json)
            
            # Also add to event stream for persistence
            stream_key = f"events:{event_type}"
            await self.redis.xadd(stream_key, event_data, maxlen=1000)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False
    
    async def get_recent_events(self, event_type: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent events of a specific type."""
        try:
            stream_key = f"events:{event_type}"
            events = await self.redis.xrevrange(stream_key, count=count)
            
            recent_events = []
            for event_id, event_data in events:
                event_dict = {k.decode(): v.decode() for k, v in event_data.items()}
                event_dict["event_id"] = event_id.decode()
                recent_events.append(event_dict)
            
            return recent_events
            
        except Exception as e:
            logger.error(f"Failed to get recent events for {event_type}: {e}")
            return []
    
    # Search and Recommendations
    async def cache_search_results(self, query_hash: str, results: List[Dict[str, Any]], ttl: int = 900) -> bool:
        """Cache search results for faster retrieval."""
        try:
            key = f"search_results:{query_hash}"
            results_json = json.dumps(results, default=str)
            
            await self.redis.set(key, results_json, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache search results: {e}")
            return False
    
    async def get_cached_search_results(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        try:
            key = f"search_results:{query_hash}"
            results_json = await self.redis.get(key)
            
            if not results_json:
                return None
            
            return json.loads(results_json.decode())
            
        except Exception as e:
            logger.error(f"Failed to get cached search results: {e}")
            return None
    
    async def cache_user_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]], ttl: int = 1800) -> bool:
        """Cache personalized recommendations for a user."""
        try:
            key = f"user_recommendations:{user_id}"
            recommendations_json = json.dumps(recommendations, default=str)
            
            await self.redis.set(key, recommendations_json, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache user recommendations: {e}")
            return False
    
    async def get_cached_user_recommendations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached personalized recommendations."""
        try:
            key = f"user_recommendations:{user_id}"
            recommendations_json = await self.redis.get(key)
            
            if not recommendations_json:
                return None
            
            return json.loads(recommendations_json.decode())
            
        except Exception as e:
            logger.error(f"Failed to get cached user recommendations: {e}")
            return None
    
    # Utility Methods
    async def clear_world_cache(self, world_id: str) -> bool:
        """Clear all cached data for a specific world."""
        try:
            keys_to_delete = [
                f"world:{world_id}:state",
                f"world:{world_id}:active_players",
            ]
            
            # Remove from rankings
            ranking_categories = ["strength", "popularity", "rating", "therapeutic_efficacy"]
            for category in ranking_categories:
                await self.redis.zrem(f"nexus:world_rankings:{category}", world_id)
            
            # Delete keys
            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear world cache for {world_id}: {e}")
            return False
    
    async def clear_user_cache(self, user_id: str) -> bool:
        """Clear all cached data for a specific user."""
        try:
            keys_to_delete = [
                f"player:{user_id}:session",
                f"user_recommendations:{user_id}",
            ]
            
            await self.redis.delete(*keys_to_delete)
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear user cache for {user_id}: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health information."""
        try:
            info = await self.redis.info()
            
            # Count keys by pattern
            world_keys = len(await self.redis.keys("world:*"))
            player_keys = len(await self.redis.keys("player:*"))
            nexus_keys = len(await self.redis.keys("nexus:*"))
            
            return {
                "redis_info": {
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                },
                "nexus_cache_stats": {
                    "world_keys": world_keys,
                    "player_keys": player_keys,
                    "nexus_keys": nexus_keys,
                    "total_nexus_keys": world_keys + player_keys + nexus_keys,
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
