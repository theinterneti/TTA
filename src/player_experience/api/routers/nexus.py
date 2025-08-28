"""
Nexus Codex API Router.

This module provides API endpoints for The Nexus Codex therapeutic gaming platform,
including world management, story weaver profiles, and community features.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import JSONResponse

from ..auth import TokenData, get_current_active_player
from ..services.connection_manager import get_service_manager
from ...models.nexus import (
    NexusStateResponse, StoryWorld, StoryWeaver, WorldTemplate,
    WorldCreationRequest, WorldSearchRequest, ActivityEvent,
    GenreType, DifficultyLevel, NarrativeState
)
from ...database.nexus_schema import NexusSchemaManager
from ...services.nexus_cache import NexusCacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nexus", tags=["nexus"])


@router.get("/state", response_model=NexusStateResponse)
async def get_nexus_state(
    service_manager: object = Depends(get_service_manager)
) -> NexusStateResponse:
    """
    Get current state of the Nexus Codex.
    
    Returns comprehensive information about the central hub including
    world count, active users, threat levels, and recent activity.
    """
    try:
        # Get Neo4j connection
        neo4j_manager = NexusSchemaManager(service_manager.neo4j.driver)
        nexus_state = await neo4j_manager.get_nexus_state()
        
        if not nexus_state:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve Nexus state"
            )
        
        # Get real-time data from cache
        cache_service = NexusCacheService(service_manager.redis)
        realtime_state = await cache_service.get_nexus_realtime_state()
        
        # Get recent activity
        recent_events = await cache_service.get_recent_events("world_activity", count=5)
        activity_events = [
            ActivityEvent(
                event_id=event.get("event_id", ""),
                event_type=event.get("event_type", ""),
                user_id=event.get("user_id", ""),
                user_name=event.get("user_name", ""),
                world_id=event.get("world_id"),
                world_title=event.get("world_title"),
                description=event.get("description", ""),
                timestamp=datetime.fromisoformat(event.get("timestamp", datetime.now().isoformat()))
            )
            for event in recent_events
        ]
        
        # Get featured worlds
        featured_worlds = await cache_service.get_top_worlds("featured", limit=3)
        
        return NexusStateResponse(
            codex_id=nexus_state["codex_id"],
            total_worlds=nexus_state["total_worlds"],
            active_story_weavers=int(realtime_state.get("active_players", 0)) if realtime_state else 0,
            silence_threat_level=nexus_state["silence_threat_level"],
            narrative_strength=nexus_state["narrative_strength"],
            featured_worlds=featured_worlds,
            recent_activity=activity_events,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to get Nexus state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Nexus state: {str(e)}"
        )


@router.get("/spheres")
async def get_story_spheres(
    genre: Optional[GenreType] = Query(None, description="Filter spheres by genre"),
    threat_level: Optional[str] = Query(None, description="Filter by threat level"),
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: object = Depends(get_service_manager)
):
    """
    Get visual data for story spheres in the Nexus.
    
    Returns positioning, visual state, and metadata for all story spheres
    that the user can see, with optional filtering by genre or threat level.
    """
    try:
        # Build Neo4j query with filters
        query_parts = ["MATCH (world:StoryWorld)-[:VISUALIZED_BY]->(sphere:StorySphere)"]
        params = {}
        
        if genre:
            query_parts.append("WHERE world.genre = $genre")
            params["genre"] = genre.value
        
        if threat_level:
            threat_filter = {
                "low": "world.silence_threat < 0.3",
                "medium": "world.silence_threat >= 0.3 AND world.silence_threat < 0.7",
                "high": "world.silence_threat >= 0.7"
            }
            if threat_level in threat_filter:
                filter_clause = threat_filter[threat_level]
                if "WHERE" in query_parts[-1]:
                    query_parts.append(f"AND {filter_clause}")
                else:
                    query_parts.append(f"WHERE {filter_clause}")
        
        query_parts.append("""
        RETURN {
            sphere_id: sphere.sphere_id,
            world_id: sphere.world_id,
            world_title: world.title,
            visual_state: sphere.visual_state,
            pulse_frequency: sphere.pulse_frequency,
            position: {
                x: sphere.position_x,
                y: sphere.position_y,
                z: sphere.position_z
            },
            color_primary: sphere.color_primary,
            color_secondary: sphere.color_secondary,
            size_scale: sphere.size_scale,
            connection_strength: sphere.connection_strength,
            world_genre: world.genre,
            world_rating: world.rating,
            world_player_count: world.player_count
        } as sphere_data
        """)
        
        query = " ".join(query_parts)
        
        async with service_manager.neo4j.driver.session() as session:
            result = await session.run(query, params)
            spheres = [record["sphere_data"] async for record in result]
        
        return {"spheres": spheres, "total_count": len(spheres)}
        
    except Exception as e:
        logger.error(f"Failed to get story spheres: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve story spheres: {str(e)}"
        )


@router.post("/worlds", status_code=status.HTTP_201_CREATED)
async def create_world(
    world_request: WorldCreationRequest = Body(...),
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: object = Depends(get_service_manager)
):
    """
    Create a new therapeutic world.
    
    Creates a new StoryWorld with the specified parameters, connects it to
    the Nexus Codex, and creates a corresponding StorySphere for visualization.
    """
    try:
        # Validate user permissions (basic check - can be extended)
        if not current_player.player_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication required"
            )
        
        # Prepare world data
        world_data = {
            "world_id": f"world_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_player.player_id[:8]}",
            "title": world_request.title,
            "description": world_request.description,
            "genre": world_request.genre.value,
            "therapeutic_focus": world_request.therapeutic_focus,
            "narrative_state": NarrativeState.ACTIVE.value,
            "creator_id": current_player.player_id,
            "strength_level": 0.5,  # Default starting strength
            "silence_threat": 0.1,  # Low initial threat
            "completion_rate": 0.0,
            "therapeutic_efficacy": 0.0,
            "difficulty_level": world_request.difficulty_level.value,
            "estimated_duration": world_request.estimated_duration,
            "player_count": 0,
            "rating": 0.0,
            "tags": [],
            "is_public": world_request.is_public,
            "is_featured": False
        }
        
        # Create world in Neo4j
        neo4j_manager = NexusSchemaManager(service_manager.neo4j.driver)
        world_id = await neo4j_manager.create_story_world(world_data)
        
        if not world_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create world in database"
            )
        
        # Cache initial world state
        cache_service = NexusCacheService(service_manager.redis)
        await cache_service.set_world_state(world_id, {
            "narrative_strength": str(world_data["strength_level"]),
            "player_count": "0",
            "current_events": "[]",
            "creation_status": "ready"
        })
        
        # Update world rankings
        await cache_service.update_world_ranking(world_id, "recent", datetime.now().timestamp())
        
        # Publish creation event
        await cache_service.publish_event("world_created", {
            "world_id": world_id,
            "world_title": world_request.title,
            "creator_id": current_player.player_id,
            "creator_name": current_player.username or "Unknown",
            "genre": world_request.genre.value
        })
        
        return {
            "world_id": world_id,
            "title": world_request.title,
            "creator_id": current_player.player_id,
            "creation_status": "ready",
            "message": "World created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create world: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create world: {str(e)}"
        )


@router.get("/worlds/search")
async def search_worlds(
    query: Optional[str] = Query(None, description="Text search in title, description, tags"),
    genre: Optional[GenreType] = Query(None, description="Filter by genre"),
    therapeutic_focus: Optional[List[str]] = Query(None, description="Filter by therapeutic goals"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    rating_min: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    sort_by: str = Query("rating", description="Sort criteria"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: object = Depends(get_service_manager)
):
    """
    Search for worlds based on criteria.

    Provides comprehensive search functionality with filtering, sorting,
    and pagination. Results include compatibility scores when possible.
    """
    try:
        # Build search query
        query_parts = ["MATCH (world:StoryWorld)"]
        where_conditions = ["world.is_public = true"]
        params = {}

        if genre:
            where_conditions.append("world.genre = $genre")
            params["genre"] = genre.value

        if difficulty:
            where_conditions.append("world.difficulty_level = $difficulty")
            params["difficulty"] = difficulty.value

        if rating_min is not None:
            where_conditions.append("world.rating >= $rating_min")
            params["rating_min"] = rating_min

        if therapeutic_focus:
            where_conditions.append("ANY(focus IN $therapeutic_focus WHERE focus IN world.therapeutic_focus)")
            params["therapeutic_focus"] = therapeutic_focus

        if query:
            where_conditions.append("""
                (toLower(world.title) CONTAINS toLower($search_query) OR
                 toLower(world.description) CONTAINS toLower($search_query) OR
                 ANY(tag IN world.tags WHERE toLower(tag) CONTAINS toLower($search_query)))
            """)
            params["search_query"] = query

        # Always add WHERE clause, even if it's just the default condition
        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))
        else:
            # Add default WHERE clause to make query valid
            query_parts.append("WHERE world.is_public = true")

        # Add RETURN clause (must come before ORDER BY)
        query_parts.append("""
        RETURN {
            world_id: world.world_id,
            title: world.title,
            description: world.description,
            genre: world.genre,
            therapeutic_focus: world.therapeutic_focus,
            difficulty_level: world.difficulty_level,
            estimated_duration: world.estimated_duration,
            player_count: world.player_count,
            rating: world.rating,
            therapeutic_efficacy: world.therapeutic_efficacy,
            strength_level: world.strength_level,
            tags: world.tags,
            is_featured: world.is_featured,
            created_at: world.created_at
        } as world_summary
        """)

        # Add sorting
        sort_mapping = {
            "rating": "world_summary.rating DESC",
            "popularity": "world_summary.player_count DESC",
            "recent": "world_summary.created_at DESC",
            "therapeutic_efficacy": "world_summary.therapeutic_efficacy DESC",
            "title": "world_summary.title ASC"
        }

        order_by = sort_mapping.get(sort_by, "world_summary.rating DESC")
        query_parts.append(f"ORDER BY {order_by}")

        # Add pagination
        query_parts.append("SKIP $offset LIMIT $limit")
        params["offset"] = offset
        params["limit"] = limit

        search_query = " ".join(query_parts)

        async with service_manager.neo4j.driver.session() as session:
            result = await session.run(search_query, params)
            worlds = [record["world_summary"] async for record in result]

        # Get total count for pagination
        # Build count query with MATCH and WHERE clauses only
        count_parts = []
        count_parts.append("MATCH (world:StoryWorld)")

        # Add the same WHERE conditions
        if where_conditions:
            count_parts.append("WHERE " + " AND ".join(where_conditions))
        else:
            count_parts.append("WHERE world.is_public = true")

        count_parts.append("RETURN count(world) as total")
        count_query = " ".join(count_parts)

        async with service_manager.neo4j.driver.session() as session:
            result = await session.run(count_query, {k: v for k, v in params.items() if k not in ["offset", "limit"]})
            record = await result.single()
            total_count = record["total"] if record else 0

        return {
            "results": worlds,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(worlds) < total_count
        }

    except Exception as e:
        logger.error(f"Failed to search worlds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search worlds: {str(e)}"
        )


@router.get("/worlds/{world_id}")
async def get_world(
    world_id: str = Path(..., description="World ID"),
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: object = Depends(get_service_manager)
):
    """
    Get detailed information about a specific world.
    
    Returns comprehensive world data including narrative structure,
    therapeutic elements, statistics, and user-specific compatibility.
    """
    try:
        query = """
        MATCH (world:StoryWorld {world_id: $world_id})
        OPTIONAL MATCH (world)<-[:CREATED_BY]-(creator:StoryWeaver)
        OPTIONAL MATCH (creator)<-[:STORY_WEAVER]-(creator_player:Player)
        
        RETURN {
            world_id: world.world_id,
            title: world.title,
            description: world.description,
            genre: world.genre,
            therapeutic_focus: world.therapeutic_focus,
            creator_id: world.creator_id,
            creator_name: COALESCE(creator_player.username, 'Unknown'),
            strength_level: world.strength_level,
            completion_rate: world.completion_rate,
            therapeutic_efficacy: world.therapeutic_efficacy,
            difficulty_level: world.difficulty_level,
            estimated_duration: world.estimated_duration,
            player_count: world.player_count,
            rating: world.rating,
            tags: world.tags,
            is_public: world.is_public,
            is_featured: world.is_featured,
            narrative_state: world.narrative_state,
            silence_threat: world.silence_threat,
            created_at: world.created_at,
            last_updated: world.last_updated
        } as world_data
        """
        
        async with service_manager.neo4j.driver.session() as session:
            result = await session.run(query, {"world_id": world_id})
            record = await result.single()
            
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"World {world_id} not found"
                )
            
            world_data = record["world_data"]
        
        # Get real-time state from cache
        cache_service = NexusCacheService(service_manager.redis)
        cached_state = await cache_service.get_world_state(world_id)
        
        if cached_state:
            world_data["current_players"] = int(cached_state.get("player_count", 0))
            world_data["last_activity"] = cached_state.get("last_interaction")
        
        return world_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get world {world_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve world: {str(e)}"
        )


@router.post("/worlds/{world_id}/enter")
async def enter_world(
    world_id: str = Path(..., description="World ID"),
    current_player: TokenData = Depends(get_current_active_player),
    service_manager: object = Depends(get_service_manager)
):
    """
    Enter a world and start therapeutic journey.
    
    Initializes a new session in the specified world, sets up player state,
    and returns initial world context and available actions.
    """
    try:
        # Verify world exists and is accessible
        query = """
        MATCH (world:StoryWorld {world_id: $world_id})
        WHERE world.is_public = true OR world.creator_id = $user_id
        RETURN world.title as title, world.narrative_state as state
        """
        
        async with service_manager.neo4j.driver.session() as session:
            result = await session.run(query, {
                "world_id": world_id,
                "user_id": current_player.player_id
            })
            record = await result.single()
            
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="World not found or not accessible"
                )
        
        # Create or get StoryWeaver profile
        neo4j_manager = NexusSchemaManager(service_manager.neo4j.driver)
        weaver_id = await neo4j_manager.create_story_weaver(current_player.player_id)
        
        # Set up player session
        cache_service = NexusCacheService(service_manager.redis)
        session_data = {
            "current_world": world_id,
            "world_title": record["title"],
            "session_start": datetime.now().isoformat(),
            "world_progress": "{}",
            "therapeutic_state": "{}",
            "achievements_pending": "[]"
        }
        
        await cache_service.set_player_session(current_player.player_id, session_data)
        
        # Update world active player count
        await cache_service.increment_active_players(world_id)
        
        # Publish enter event
        await cache_service.publish_event("player_entered", {
            "world_id": world_id,
            "world_title": record["title"],
            "player_id": current_player.player_id,
            "player_name": current_player.username or "Unknown"
        })
        
        return {
            "session_id": f"{current_player.player_id}_{world_id}_{int(datetime.now().timestamp())}",
            "world_id": world_id,
            "world_title": record["title"],
            "world_state": "initialized",
            "available_actions": [
                {"action": "explore", "description": "Begin exploring the world"},
                {"action": "reflect", "description": "Set therapeutic intentions"},
                {"action": "customize", "description": "Adjust world parameters"}
            ],
            "therapeutic_guidance": {
                "welcome_message": f"Welcome to {record['title']}! Take a moment to set your therapeutic intentions for this journey.",
                "suggested_focus": "Consider what you hope to learn or practice in this world."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enter world {world_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enter world: {str(e)}"
        )



