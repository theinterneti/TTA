"""
Character management router for the Player Experience API.

This module provides REST endpoints for character management with
authentication, authorization (owner-only), and API documentation.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...database.character_repository import CharacterRepository
from ...managers.character_avatar_manager import (
    CharacterAvatarManager,
    CharacterLimitExceededError,
    CharacterNotFoundError,
)
from ...models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    CharacterCreationData,
    CharacterUpdates,
    TherapeuticGoal,
    TherapeuticProfile,
)
from ...models.enums import IntensityLevel, TherapeuticApproach
from ..auth import TokenData, get_current_active_player

router = APIRouter()


# Dependency to get character manager

# Use a single in-memory repository instance only in testing environment for persistence
_repository_singleton: CharacterRepository | None = None
_manager_singleton: CharacterAvatarManager | None = None


def _is_test_env() -> bool:
    try:
        # ENVIRONMENT env var is used in settings selection
        import os

        from config import settings

        return (
            os.getenv("ENVIRONMENT", "development").lower() == "test"
            or settings.debug
            and settings.app_name.endswith("(test)")
        )
    except Exception:
        import os

        return os.getenv("ENVIRONMENT", "development").lower() == "test"


def get_character_manager() -> CharacterAvatarManager:
    # Always use a module-level singleton manager instance to persist across requests in tests and dev
    global _repository_singleton, _manager_singleton
    if _repository_singleton is None:
        try:
            from ..config import get_settings

            settings = get_settings()
            _repository_singleton = CharacterRepository(
                uri=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password,
            )
        except Exception:
            # Fallback to default constructor for tests
            _repository_singleton = CharacterRepository()
    if _manager_singleton is None:
        _manager_singleton = CharacterAvatarManager(_repository_singleton)
    return _manager_singleton


# Wrapper dependency to allow runtime patching in tests


def get_character_manager_dep() -> CharacterAvatarManager:
    return get_character_manager()


# Request/Response Schemas


class CharacterAppearanceRequest(BaseModel):
    age_range: str = Field("adult", description="Age range: child, teen, adult, elder")
    gender_identity: str = Field("non-binary", min_length=1, max_length=50)
    physical_description: str = Field(
        "", min_length=1, max_length=1000, description="Physical appearance description"
    )
    clothing_style: str = Field("casual", max_length=100)
    distinctive_features: list[str] = Field(default_factory=list, max_length=10)
    avatar_image_url: str | None = Field(None, max_length=500)

    @field_validator("age_range")
    @classmethod
    def validate_age_range(cls, v):
        valid_ranges = ["child", "teen", "adult", "elder"]
        if v not in valid_ranges:
            raise ValueError(f"Age range must be one of: {valid_ranges}")
        return v

    @field_validator("distinctive_features")
    @classmethod
    def validate_distinctive_features(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 distinctive features allowed")
        for feature in v:
            if len(feature) > 100:
                raise ValueError(
                    "Each distinctive feature must be 100 characters or less"
                )
        return v


class CharacterBackgroundRequest(BaseModel):
    # Allow extra fields like age, occupation sent by tests; we'll ignore them in mapping
    model_config = ConfigDict(extra="allow")
    name: str = Field(min_length=2, max_length=50, description="Character name")
    backstory: str = Field(
        "", min_length=1, max_length=2000, description="Character background story"
    )
    personality_traits: list[str] = Field(
        default_factory=list, min_length=1, max_length=20
    )
    core_values: list[str] = Field(default_factory=list, max_length=15)
    fears_and_anxieties: list[str] = Field(default_factory=list, max_length=15)
    strengths_and_skills: list[str] = Field(default_factory=list, max_length=20)
    life_goals: list[str] = Field(default_factory=list, min_length=1, max_length=15)
    relationships: dict[str, str] = Field(default_factory=dict, max_length=10)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        import re

        if not re.match(r"^[a-zA-Z\s\-']+$", v.strip()):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )
        return v.strip()

    @field_validator(
        "personality_traits",
        "core_values",
        "fears_and_anxieties",
        "strengths_and_skills",
        "life_goals",
    )
    @classmethod
    def validate_string_lists(cls, v):
        for item in v:
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValueError("All list items must be non-empty strings")
            if len(item) > 200:
                raise ValueError("Each item must be 200 characters or less")
        return [item.strip() for item in v]

    @field_validator("relationships")
    @classmethod
    def validate_relationships(cls, v):
        for key, value in v.items():
            if len(key) > 50 or len(value) > 200:
                raise ValueError(
                    "Relationship keys must be ≤50 chars, values ≤200 chars"
                )
        return v


class TherapeuticGoalSchema(BaseModel):
    goal_id: str
    description: str
    target_date: str | None = None
    progress_percentage: float = 0.0
    is_active: bool = True
    therapeutic_approaches: list[TherapeuticApproach] = Field(default_factory=list)

    @field_validator("therapeutic_approaches", mode="before")
    @classmethod
    def _normalize_goal_approaches(cls, v):
        from ...utils.normalization import normalize_approaches

        return normalize_approaches(v)


class TherapeuticProfileSchema(BaseModel):
    primary_concerns: list[str] = Field(
        default_factory=list,
        min_length=1,
        max_length=15,
        description="Primary therapeutic concerns",
    )
    therapeutic_goals: list[TherapeuticGoalSchema] = Field(
        default_factory=list, min_length=1, max_length=10
    )
    preferred_intensity: IntensityLevel = IntensityLevel.MEDIUM
    comfort_zones: list[str] = Field(default_factory=list, max_length=15)
    readiness_level: float = Field(
        0.5, ge=0.0, le=1.0, description="Readiness level from 0.0 to 1.0"
    )
    therapeutic_approaches: list[TherapeuticApproach] = Field(
        default_factory=list, max_length=10
    )

    @field_validator("primary_concerns", "comfort_zones")
    @classmethod
    def validate_string_lists(cls, v):
        for item in v:
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValueError("All list items must be non-empty strings")
            if len(item) > 200:
                raise ValueError("Each item must be 200 characters or less")
        return [item.strip() for item in v]

    @field_validator("therapeutic_goals")
    @classmethod
    def validate_therapeutic_goals(cls, v):
        if len(v) == 0:
            raise ValueError("At least one therapeutic goal is required")
        return v

    @field_validator("preferred_intensity", mode="before")
    @classmethod
    def _normalize_intensity(cls, v):
        from ...utils.normalization import normalize_intensity

        return normalize_intensity(v)

    @field_validator("therapeutic_approaches", mode="before")
    @classmethod
    def _normalize_profile_approaches(cls, v):
        from ...utils.normalization import normalize_approaches

        return normalize_approaches(v)


class CreateCharacterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Character display name")
    appearance: CharacterAppearanceRequest
    background: CharacterBackgroundRequest
    therapeutic_profile: TherapeuticProfileSchema

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        import re

        if not re.match(r"^[a-zA-Z\s\-']+$", v.strip()):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )
        return v.strip()

    def model_post_init(self, __context):
        """Ensure character name matches background name"""
        if self.name.strip() != self.background.name.strip():
            # Sync background name with character name
            self.background.name = self.name.strip()


class UpdateCharacterRequest(BaseModel):
    appearance: CharacterAppearanceRequest | None = None
    background: CharacterBackgroundRequest | None = None
    therapeutic_profile: TherapeuticProfileSchema | None = None


class CharacterResponse(BaseModel):
    character_id: str
    player_id: str
    name: str
    appearance: CharacterAppearanceRequest
    background: CharacterBackgroundRequest
    therapeutic_profile: TherapeuticProfileSchema
    created_at: str
    last_active: str
    is_active: bool


# Converters between dataclasses and API schemas


def _goal_to_schema(goal: TherapeuticGoal) -> TherapeuticGoalSchema:
    return TherapeuticGoalSchema(
        goal_id=goal.goal_id,
        description=goal.description,
        target_date=goal.target_date.isoformat() if goal.target_date else None,
        progress_percentage=goal.progress_percentage,
        is_active=goal.is_active,
        therapeutic_approaches=goal.therapeutic_approaches,
    )


def _profile_to_schema(profile: TherapeuticProfile) -> TherapeuticProfileSchema:
    return TherapeuticProfileSchema(
        primary_concerns=profile.primary_concerns,
        therapeutic_goals=[_goal_to_schema(g) for g in profile.therapeutic_goals],
        preferred_intensity=profile.preferred_intensity,
        comfort_zones=profile.comfort_zones,
        readiness_level=profile.readiness_level,
        therapeutic_approaches=getattr(profile, "therapeutic_approaches", []),
    )


def _appearance_to_schema(app: CharacterAppearance) -> CharacterAppearanceRequest:
    return CharacterAppearanceRequest(
        age_range=app.age_range,
        gender_identity=app.gender_identity,
        physical_description=app.physical_description,
        clothing_style=app.clothing_style,
        distinctive_features=app.distinctive_features,
        avatar_image_url=app.avatar_image_url,
    )


def _background_to_schema(bg: CharacterBackground) -> CharacterBackgroundRequest:
    return CharacterBackgroundRequest(
        name=bg.name,
        backstory=bg.backstory,
        personality_traits=bg.personality_traits,
        core_values=bg.core_values,
        fears_and_anxieties=bg.fears_and_anxieties,
        strengths_and_skills=bg.strengths_and_skills,
        life_goals=bg.life_goals,
        relationships=bg.relationships,
    )


def _character_to_response(character: Character) -> CharacterResponse:
    return CharacterResponse(
        character_id=character.character_id,
        player_id=character.player_id,
        name=character.name,
        appearance=_appearance_to_schema(character.appearance),
        background=_background_to_schema(character.background),
        therapeutic_profile=_profile_to_schema(character.therapeutic_profile),
        created_at=character.created_at.isoformat(),
        last_active=character.last_active.isoformat(),
        is_active=character.is_active,
    )


def _schema_to_appearance(s: CharacterAppearanceRequest) -> CharacterAppearance:
    return CharacterAppearance(
        age_range=s.age_range,
        gender_identity=s.gender_identity,
        physical_description=s.physical_description,
        clothing_style=s.clothing_style,
        distinctive_features=s.distinctive_features,
        avatar_image_url=s.avatar_image_url,
    )


def _schema_to_background(s: CharacterBackgroundRequest) -> CharacterBackground:
    # Sanitize background name: only letters, spaces, hyphens, apostrophes per model validation
    import re

    clean_name = re.sub(r"[^a-zA-Z\s\-']+", "", (s.name or "")).strip()
    return CharacterBackground(
        name=clean_name,
        backstory=s.backstory,
        personality_traits=s.personality_traits,
        core_values=s.core_values,
        fears_and_anxieties=s.fears_and_anxieties,
        strengths_and_skills=s.strengths_and_skills,
        life_goals=s.life_goals,
        relationships=s.relationships,
    )


def _schema_to_goal(s: TherapeuticGoalSchema) -> TherapeuticGoal:
    from datetime import datetime

    return TherapeuticGoal(
        goal_id=s.goal_id,
        description=s.description,
        target_date=datetime.fromisoformat(s.target_date) if s.target_date else None,
        progress_percentage=s.progress_percentage,
        is_active=s.is_active,
        therapeutic_approaches=getattr(s, "therapeutic_approaches", []),
    )


def _schema_to_profile(s: TherapeuticProfileSchema) -> TherapeuticProfile:
    return TherapeuticProfile(
        primary_concerns=s.primary_concerns,
        therapeutic_goals=[_schema_to_goal(g) for g in s.therapeutic_goals],
        preferred_intensity=s.preferred_intensity,
        comfort_zones=s.comfort_zones,
        readiness_level=s.readiness_level,
        therapeutic_approaches=s.therapeutic_approaches,
    )


@router.get(
    "/",
    response_model=list[CharacterResponse],
    summary="List Player Characters",
    description="List all characters owned by the current player.",
)
async def list_characters(
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> list[CharacterResponse]:
    try:
        chars = manager.get_player_characters(current_player.player_id)
        return [_character_to_response(c) for c in chars]
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while listing characters"
            },
        )


@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Get Character",
    description="Get a character by ID (owner-only).",
)
async def get_character(
    character_id: str,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> CharacterResponse:
    try:
        character = manager.get_character(character_id)
        if not character:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        if character.player_id != current_player.player_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: You can only access your own characters"
                },
            )
        return _character_to_response(character)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while retrieving character"
            },
        )


@router.post(
    "/",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Character",
    description="Create a new character for the current player. Enforces max character limit.",
)
async def create_character(
    request: CreateCharacterRequest,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> CharacterResponse:
    try:
        # Convert request to domain models. Sanitize both display and background names to match model constraints.
        import re

        sanitize = lambda s: re.sub(r"[^a-zA-Z\s\-']+", "", (s or "")).strip()
        sanitized_name = sanitize(request.name)
        character = manager.create_character(
            current_player.player_id,
            CharacterCreationData(
                name=sanitized_name,
                appearance=_schema_to_appearance(request.appearance),
                background=_schema_to_background(request.background),
                therapeutic_profile=_schema_to_profile(request.therapeutic_profile),
            ),
        )
        return _character_to_response(character)
    except CharacterLimitExceededError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )
    except Exception as e:
        # Provide error detail to aid debugging in tests
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal error: {e.__class__.__name__}: {str(e)}"},
        )


@router.put(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Update Character",
    description="Update a character (owner-only).",
)
async def update_character(
    character_id: str,
    request: UpdateCharacterRequest,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> CharacterResponse:
    try:
        existing = manager.get_character(character_id)
        if not existing:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        if existing.player_id != current_player.player_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: You can only modify your own characters"
                },
            )

        updates = CharacterUpdates(
            appearance=(
                _schema_to_appearance(request.appearance)
                if request.appearance
                else None
            ),
            background=(
                _schema_to_background(request.background)
                if request.background
                else None
            ),
            therapeutic_profile=(
                _schema_to_profile(request.therapeutic_profile)
                if request.therapeutic_profile
                else None
            ),
        )
        updated = manager.update_character(character_id, updates)
        return _character_to_response(updated)
    except CharacterNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Character not found"},
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while updating character"
            },
        )


@router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Character",
    description="Delete a character (owner-only).",
)
async def delete_character(
    character_id: str,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> None:
    try:
        existing = manager.get_character(character_id)
        if not existing:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        if existing.player_id != current_player.player_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: You can only delete your own characters"
                },
            )

        success = manager.delete_character(character_id)
        if not success:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        return None
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while deleting character"
            },
        )


@router.get(
    "/{character_id}/therapeutic-profile",
    response_model=TherapeuticProfileSchema,
    summary="Get Character Therapeutic Profile",
    description="Get the therapeutic profile for a character (owner-only).",
)
async def get_character_therapeutic_profile(
    character_id: str,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> TherapeuticProfileSchema:
    try:
        character = manager.get_character(character_id)
        if not character:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        if character.player_id != current_player.player_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: You can only access your own characters"
                },
            )

        profile = manager.get_character_therapeutic_profile(character_id)
        if profile is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        return _profile_to_schema(profile)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while retrieving therapeutic profile"
            },
        )


@router.patch(
    "/{character_id}/therapeutic-profile",
    response_model=TherapeuticProfileSchema,
    summary="Update Character Therapeutic Profile",
    description="Update the therapeutic profile for a character (owner-only).",
)
async def update_character_therapeutic_profile(
    character_id: str,
    request: TherapeuticProfileSchema,
    current_player: TokenData = Depends(get_current_active_player),
    manager: CharacterAvatarManager = Depends(get_character_manager_dep),
) -> TherapeuticProfileSchema:
    try:
        character = manager.get_character(character_id)
        if not character:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )
        if character.player_id != current_player.player_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: You can only modify your own characters"
                },
            )

        updated = manager.update_character_therapeutic_profile(
            character_id, _schema_to_profile(request)
        )
        if not updated:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Character not found"},
            )

        # Return updated profile
        profile = manager.get_character_therapeutic_profile(character_id)
        return _profile_to_schema(profile)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred while updating therapeutic profile"
            },
        )
