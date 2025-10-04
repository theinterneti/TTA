"""
Player Experience Integration for Franchise World System

This module provides the bridge between the TypeScript franchise world system
and the existing Python-based TTA player experience API, enabling seamless
integration of franchise worlds into the TTA platform.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from ..managers.world_management_module import (  # type: ignore[import-not-found]
    WorldManagementModule,
)
from ..models.enums import (  # type: ignore[import-not-found]
    DifficultyLevel,
    TherapeuticApproach,
)
from ..models.world import (  # type: ignore[import-not-found]
    WorldDetails,
    WorldParameters,
)


class FranchiseWorldBridge:
    """
    Bridge between TypeScript franchise world system and Python TTA API
    """

    def __init__(self, franchise_world_path: str | None = None):
        self.franchise_world_path = franchise_world_path or str(
            Path(__file__).parent.parent
        )
        self.world_manager = WorldManagementModule()
        self._franchise_integration = None

    async def initialize_franchise_system(self) -> bool:
        """
        Initialize the TypeScript franchise world system
        """
        try:
            # Run the franchise world integration initialization
            result = await self._run_node_script("initialize-system.js")
            return result.get("success", False)
        except Exception as e:
            print(f"Failed to initialize franchise system: {e}")
            return False

    async def get_franchise_worlds(
        self, genre: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get franchise worlds from the TypeScript system

        Args:
            genre: Optional genre filter ('fantasy' or 'sci-fi')

        Returns:
            List of franchise world configurations
        """
        try:
            script_args = {"genre": genre} if genre else {}
            result = await self._run_node_script("get-worlds.js", script_args)
            return result.get("worlds", [])
        except Exception as e:
            print(f"Failed to get franchise worlds: {e}")
            return []

    async def convert_franchise_world_to_tta(
        self, franchise_world_id: str
    ) -> WorldDetails | None:
        """
        Convert a franchise world to TTA WorldDetails format

        Args:
            franchise_world_id: ID of the franchise world to convert

        Returns:
            WorldDetails object or None if conversion fails
        """
        try:
            result = await self._run_node_script(
                "convert-world.js", {"worldId": franchise_world_id}
            )

            if not result.get("success"):
                return None

            world_data = result.get("worldDetails")
            if not world_data:
                return None

            # Convert to TTA WorldDetails
            return self._convert_to_world_details(world_data)

        except Exception as e:
            print(f"Failed to convert franchise world {franchise_world_id}: {e}")
            return None

    async def register_franchise_worlds_with_tta(self) -> bool:
        """
        Register all franchise worlds with the TTA world management system
        """
        try:
            franchise_worlds = await self.get_franchise_worlds()

            for world_config in franchise_worlds:
                franchise_id = world_config.get("franchiseId")
                if not franchise_id:
                    continue

                world_details = await self.convert_franchise_world_to_tta(franchise_id)

                if world_details:
                    # Register with TTA world manager
                    self.world_manager.register_world(world_details)
                    print(f"Registered franchise world: {world_details.name}")

            return True

        except Exception as e:
            print(f"Failed to register franchise worlds: {e}")
            return False

    async def get_character_archetypes(self) -> list[dict[str, Any]]:
        """
        Get character archetypes from the franchise system
        """
        try:
            result = await self._run_node_script("get-archetypes.js")
            return result.get("archetypes", [])
        except Exception as e:
            print(f"Failed to get character archetypes: {e}")
            return []

    async def adapt_archetype_for_world(
        self, archetype_id: str, world_genre: str, world_context: str
    ) -> dict[str, Any] | None:
        """
        Adapt a character archetype for a specific world
        """
        try:
            result = await self._run_node_script(
                "adapt-archetype.js",
                {
                    "archetypeId": archetype_id,
                    "worldGenre": world_genre,
                    "worldContext": world_context,
                },
            )
            return result.get("adaptedArchetype")
        except Exception as e:
            print(f"Failed to adapt archetype: {e}")
            return None

    async def validate_franchise_world_for_simulation(self, world_id: str) -> bool:
        """
        Validate if a franchise world is suitable for simulation testing
        """
        try:
            result = await self._run_node_script(
                "validate-world.js", {"worldId": world_id}
            )
            return result.get("isValid", False)
        except Exception as e:
            print(f"Failed to validate world for simulation: {e}")
            return False

    async def create_customized_world_parameters(
        self, world_id: str, player_preferences: dict[str, Any]
    ) -> WorldParameters | None:
        """
        Create customized world parameters based on player preferences
        """
        try:
            result = await self._run_node_script(
                "create-parameters.js",
                {"worldId": world_id, "playerPreferences": player_preferences},
            )

            if not result.get("success"):
                return None

            params_data = result.get("parameters")
            if not params_data:
                return None

            return self._convert_to_world_parameters(params_data)

        except Exception as e:
            print(f"Failed to create customized parameters: {e}")
            return None

    async def _run_node_script(
        self, script_name: str, args: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Run a Node.js script in the franchise world system
        """
        script_path = Path(self.franchise_world_path) / "scripts" / script_name

        # Prepare command
        cmd = ["node", str(script_path)]

        # Add arguments as JSON if provided
        if args:
            cmd.append(json.dumps(args))

        # Run the script
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.franchise_world_path,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Script failed: {stderr.decode()}")

        # Parse JSON response
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}") from e

    def _convert_to_world_details(self, world_data: dict[str, Any]) -> WorldDetails:
        """
        Convert franchise world data to TTA WorldDetails
        """
        from datetime import timedelta

        return WorldDetails(
            world_id=world_data.get("world_id"),
            name=world_data.get("name"),
            description=world_data.get("description"),
            long_description=world_data.get("long_description"),
            therapeutic_themes=world_data.get("therapeutic_themes", []),
            therapeutic_approaches=[
                TherapeuticApproach(approach)
                for approach in world_data.get("therapeutic_approaches", [])
            ],
            difficulty_level=DifficultyLevel(
                world_data.get("difficulty_level", "intermediate")
            ),
            estimated_duration=timedelta(
                hours=world_data.get("estimated_duration", {}).get("hours", 2)
            ),
            setting_description=world_data.get("setting_description", ""),
            key_characters=world_data.get("key_characters", []),
            main_storylines=world_data.get("main_storylines", []),
            therapeutic_techniques_used=world_data.get(
                "therapeutic_techniques_used", []
            ),
            prerequisites=world_data.get("prerequisites", []),
            recommended_therapeutic_readiness=world_data.get(
                "recommended_therapeutic_readiness", 0.5
            ),
            content_warnings=world_data.get("content_warnings", []),
        )

    def _convert_to_world_parameters(
        self, params_data: dict[str, Any]
    ) -> WorldParameters:
        """
        Convert parameters data to TTA WorldParameters
        """
        return WorldParameters(
            therapeutic_intensity=params_data.get("therapeutic_intensity", 0.5),
            narrative_pace=params_data.get("narrative_pace", "medium"),
            interaction_frequency=params_data.get("interaction_frequency", "balanced"),
            challenge_level=DifficultyLevel(
                params_data.get("challenge_level", "intermediate")
            ),
            focus_areas=params_data.get("focus_areas", []),
            avoid_topics=params_data.get("avoid_topics", []),
            session_length_preference=params_data.get("session_length_preference", 60),
        )


class FranchiseWorldAPI:
    """
    API endpoints for franchise world integration
    """

    def __init__(self):
        self.bridge = FranchiseWorldBridge()

    async def initialize(self) -> bool:
        """Initialize the franchise world system"""
        return await self.bridge.initialize_franchise_system()

    async def list_franchise_worlds(
        self, genre: str | None = None
    ) -> list[dict[str, Any]]:
        """List available franchise worlds"""
        return await self.bridge.get_franchise_worlds(genre)

    async def get_franchise_world_details(self, world_id: str) -> dict[str, Any] | None:
        """Get detailed information about a specific franchise world"""
        world_details = await self.bridge.convert_franchise_world_to_tta(world_id)
        if world_details:
            return {
                "world_id": world_details.world_id,
                "name": world_details.name,
                "description": world_details.description,
                "long_description": world_details.long_description,
                "therapeutic_themes": world_details.therapeutic_themes,
                "therapeutic_approaches": [
                    approach.value for approach in world_details.therapeutic_approaches
                ],
                "difficulty_level": world_details.difficulty_level.value,
                "estimated_duration_hours": world_details.estimated_duration.total_seconds()
                / 3600,
                "setting_description": world_details.setting_description,
                "key_characters": world_details.key_characters,
                "main_storylines": world_details.main_storylines,
                "therapeutic_techniques_used": world_details.therapeutic_techniques_used,
                "prerequisites": world_details.prerequisites,
                "recommended_therapeutic_readiness": world_details.recommended_therapeutic_readiness,
                "content_warnings": world_details.content_warnings,
            }
        return None

    async def register_all_franchise_worlds(self) -> dict[str, Any]:
        """Register all franchise worlds with TTA"""
        success = await self.bridge.register_franchise_worlds_with_tta()
        return {
            "success": success,
            "message": (
                "Franchise worlds registered successfully"
                if success
                else "Registration failed"
            ),
        }

    async def get_character_archetypes(self) -> list[dict[str, Any]]:
        """Get available character archetypes"""
        return await self.bridge.get_character_archetypes()

    async def validate_world_for_simulation(self, world_id: str) -> dict[str, Any]:
        """Validate world for simulation testing"""
        is_valid = await self.bridge.validate_franchise_world_for_simulation(world_id)
        return {
            "world_id": world_id,
            "is_valid": is_valid,
            "message": (
                "World is suitable for simulation"
                if is_valid
                else "World needs additional configuration"
            ),
        }
