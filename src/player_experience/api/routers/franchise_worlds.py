"""
Franchise Worlds API Router

Provides REST API endpoints for the franchise world system,
enabling integration with the TTA player experience interface.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...franchise_worlds.integration.PlayerExperienceIntegration import (
    FranchiseWorldAPI,
)
from ...models.player import PlayerProfile
from ..dependencies import get_current_player  # type: ignore[import-not-found]

# Initialize the franchise world API
franchise_api = FranchiseWorldAPI()

# Create the router
router = APIRouter(prefix="/franchise-worlds", tags=["franchise-worlds"])


# Pydantic models for API requests/responses
class FranchiseWorldSummary(BaseModel):
    """Summary of a franchise world for listing"""

    franchise_id: str = Field(
        ..., description="Unique identifier for the franchise world"
    )
    name: str = Field(..., description="Display name of the world")
    genre: str = Field(..., description="Genre: fantasy or sci-fi")
    inspiration_source: str = Field(..., description="What the world is inspired by")
    therapeutic_themes: list[str] = Field(
        default_factory=list, description="Main therapeutic themes"
    )
    therapeutic_approaches: list[str] = Field(
        default_factory=list, description="Supported therapeutic approaches"
    )
    difficulty_level: str = Field(
        ..., description="Difficulty level: beginner, intermediate, advanced"
    )
    estimated_duration_hours: float = Field(
        ..., description="Estimated session duration in hours"
    )
    content_ratings: list[dict[str, Any]] = Field(
        default_factory=list, description="Content rating information"
    )


class FranchiseWorldDetails(BaseModel):
    """Detailed information about a franchise world"""

    world_id: str
    name: str
    description: str
    long_description: str
    therapeutic_themes: list[str]
    therapeutic_approaches: list[str]
    difficulty_level: str
    estimated_duration_hours: float
    setting_description: str
    key_characters: list[dict[str, str]]
    main_storylines: list[str]
    therapeutic_techniques_used: list[str]
    prerequisites: list[dict[str, str]]
    recommended_therapeutic_readiness: float
    content_warnings: list[str]


class CharacterArchetype(BaseModel):
    """Character archetype information"""

    archetype_id: str
    name: str
    inspiration_source: str
    role: str
    therapeutic_function: str
    personality_traits: list[str]
    adaptation_notes: str


class WorldValidationResult(BaseModel):
    """Result of world validation for simulation"""

    world_id: str
    is_valid: bool
    message: str


class RegistrationResult(BaseModel):
    """Result of franchise world registration"""

    success: bool
    message: str
    registered_count: int | None = None


# API Endpoints


@router.on_event("startup")
async def initialize_franchise_system():
    """Initialize the franchise world system on startup"""
    try:
        success = await franchise_api.initialize()
        if not success:
            pass
    except Exception:
        pass


@router.get("/", response_model=list[FranchiseWorldSummary])
async def list_franchise_worlds(
    genre: str | None = Query(None, description="Filter by genre: fantasy or sci-fi"),
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    List all available franchise worlds, optionally filtered by genre
    """
    try:
        worlds = await franchise_api.list_franchise_worlds(genre)

        return [
            FranchiseWorldSummary(
                franchise_id=world["franchiseId"],
                name=world["name"],
                genre=world["genre"],
                inspiration_source=world["inspirationSource"],
                therapeutic_themes=world["therapeuticThemes"],
                therapeutic_approaches=world["therapeuticApproaches"],
                difficulty_level=world["difficultyLevel"],
                estimated_duration_hours=world["estimatedDuration"]["hours"],
                content_ratings=world.get("contentRatings", []),
            )
            for world in worlds
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve franchise worlds: {str(e)}"
        ) from e


@router.get("/{world_id}", response_model=FranchiseWorldDetails)
async def get_franchise_world_details(
    world_id: str, current_player: PlayerProfile = Depends(get_current_player)
):
    """
    Get detailed information about a specific franchise world
    """
    try:
        world_details = await franchise_api.get_franchise_world_details(world_id)

        if not world_details:
            raise HTTPException(
                status_code=404, detail=f"Franchise world not found: {world_id}"
            )

        return FranchiseWorldDetails(**world_details)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve world details: {str(e)}"
        ) from e


@router.post("/register", response_model=RegistrationResult)
async def register_franchise_worlds(
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    Register all franchise worlds with the TTA system

    This endpoint should typically be called during system initialization
    or when new franchise worlds are added.
    """
    try:
        result = await franchise_api.register_all_franchise_worlds()

        return RegistrationResult(success=result["success"], message=result["message"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to register franchise worlds: {str(e)}"
        ) from e


@router.get("/archetypes/", response_model=list[CharacterArchetype])
async def list_character_archetypes(
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    List all available character archetypes
    """
    try:
        archetypes = await franchise_api.get_character_archetypes()

        return [
            CharacterArchetype(
                archetype_id=archetype["archetypeId"],
                name=archetype["name"],
                inspiration_source=archetype["inspirationSource"],
                role=archetype["role"],
                therapeutic_function=archetype["therapeuticFunction"],
                personality_traits=archetype["personality"]["traits"],
                adaptation_notes=archetype["adaptationNotes"],
            )
            for archetype in archetypes
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve character archetypes: {str(e)}"
        ) from e


@router.post("/{world_id}/validate", response_model=WorldValidationResult)
async def validate_world_for_simulation(
    world_id: str, current_player: PlayerProfile = Depends(get_current_player)
):
    """
    Validate if a franchise world is suitable for simulation testing
    """
    try:
        result = await franchise_api.validate_world_for_simulation(world_id)

        return WorldValidationResult(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to validate world: {str(e)}"
        ) from e


@router.get("/genres/fantasy", response_model=list[FranchiseWorldSummary])
async def list_fantasy_worlds(
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    List all fantasy franchise worlds
    """
    return await list_franchise_worlds(genre="fantasy", current_player=current_player)


@router.get("/genres/sci-fi", response_model=list[FranchiseWorldSummary])
async def list_scifi_worlds(
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    List all sci-fi franchise worlds
    """
    return await list_franchise_worlds(genre="sci-fi", current_player=current_player)


@router.get("/stats/summary")
async def get_franchise_world_stats(
    current_player: PlayerProfile = Depends(get_current_player),
):
    """
    Get summary statistics about the franchise world system
    """
    try:
        all_worlds = await franchise_api.list_franchise_worlds()
        fantasy_worlds = await franchise_api.list_franchise_worlds("fantasy")
        scifi_worlds = await franchise_api.list_franchise_worlds("sci-fi")
        archetypes = await franchise_api.get_character_archetypes()

        # Calculate therapeutic approach coverage
        all_approaches = set()
        for world in all_worlds:
            all_approaches.update(world.get("therapeuticApproaches", []))

        # Calculate difficulty distribution
        difficulty_distribution = {}
        for world in all_worlds:
            difficulty = world.get("difficultyLevel", "unknown")
            difficulty_distribution[difficulty] = (
                difficulty_distribution.get(difficulty, 0) + 1
            )

        return {
            "total_worlds": len(all_worlds),
            "fantasy_worlds": len(fantasy_worlds),
            "scifi_worlds": len(scifi_worlds),
            "character_archetypes": len(archetypes),
            "therapeutic_approaches_covered": len(all_approaches),
            "therapeutic_approaches": list(all_approaches),
            "difficulty_distribution": difficulty_distribution,
            "system_status": "operational",
            "last_updated": "2024-01-01T00:00:00Z",  # This would be dynamic in production
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve stats: {str(e)}"
        ) from e


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the franchise world system
    """
    try:
        # Test basic functionality
        worlds = await franchise_api.list_franchise_worlds()

        return {
            "status": "healthy",
            "worlds_available": len(worlds),
            "timestamp": "2024-01-01T00:00:00Z",  # This would be dynamic in production
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z",  # This would be dynamic in production
        }
