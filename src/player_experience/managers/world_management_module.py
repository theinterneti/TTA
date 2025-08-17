"""
World discovery, selection, and customization management.

This module handles world discovery, selection, and customization for the
Player Experience Interface, integrating with existing TTA therapeutic components.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from ..models.world import (
    WorldSummary, WorldDetails, WorldParameters, CompatibilityReport, 
    CompatibilityFactor, WorldPrerequisite, CustomizedWorld
)
from ..models.character import Character, TherapeuticProfile
from ..models.enums import DifficultyLevel, TherapeuticApproach
from ..utils.compatibility_checker import CompatibilityChecker

logger = logging.getLogger(__name__)


class WorldManagementModule:
    """Handles world discovery, selection, and customization."""
    
    def __init__(self, world_state_manager=None, therapeutic_environment_generator=None, 
                 compatibility_checker=None):
        """
        Initialize the World Management Module.
        
        Args:
            world_state_manager: Optional WorldStateManager from tta.prototype
            therapeutic_environment_generator: Optional TherapeuticEnvironmentGenerator
            compatibility_checker: Optional CompatibilityChecker for advanced compatibility assessment
        """
        self.world_state_manager = world_state_manager
        self.therapeutic_environment_generator = therapeutic_environment_generator
        self.compatibility_checker = compatibility_checker or CompatibilityChecker()
        self._world_cache: Dict[str, WorldDetails] = {}
        self._compatibility_threshold = 0.6
        
        # Initialize with some default worlds for testing
        self._initialize_default_worlds()
        
        logger.info("WorldManagementModule initialized")
    
    def _initialize_default_worlds(self) -> None:
        """Initialize default worlds for testing and demonstration."""
        # Mindfulness Garden World
        mindfulness_world = WorldDetails(
            world_id="world_mindfulness_garden",
            name="Mindfulness Garden",
            description="A peaceful garden environment focused on mindfulness and present-moment awareness",
            long_description="Step into a serene garden where time moves slowly and every breath brings deeper awareness. This therapeutic environment is designed to help you develop mindfulness skills through gentle exploration and contemplative activities.",
            therapeutic_themes=["mindfulness", "stress_reduction", "present_moment_awareness"],
            therapeutic_approaches=[TherapeuticApproach.MINDFULNESS, TherapeuticApproach.CBT],
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=timedelta(hours=1, minutes=30),
            setting_description="A beautiful garden with winding paths, meditation spots, and gentle water features",
            key_characters=[
                {"name": "Sage", "role": "Mindfulness Guide", "description": "A gentle guide who teaches mindfulness techniques"}
            ],
            main_storylines=[
                "Learning to observe thoughts without judgment",
                "Discovering the power of present-moment awareness",
                "Building a daily mindfulness practice"
            ],
            therapeutic_techniques_used=[
                "breathing_meditation", "body_scan", "mindful_walking", "loving_kindness"
            ],
            prerequisites=[],
            recommended_therapeutic_readiness=0.3,
            content_warnings=[],
            available_parameters=["therapeutic_intensity", "session_length_preference", "focus_areas"],
            tags=["beginner_friendly", "peaceful", "nature", "meditation"],
            therapeutic_goals_addressed=["stress_reduction", "emotional_regulation", "self_awareness"],
            success_metrics=["mindfulness_skill_development", "stress_level_reduction", "session_completion"],
            player_count=150,
            completion_rate=0.85,
            average_rating=4.7,
            average_session_count=8,
            therapeutic_effectiveness_score=0.82
        )
        
        # Anxiety Relief Sanctuary
        anxiety_world = WorldDetails(
            world_id="world_anxiety_sanctuary",
            name="Anxiety Relief Sanctuary",
            description="A safe, protective environment designed to help manage anxiety and build coping skills",
            long_description="Enter a sanctuary designed specifically for those dealing with anxiety. This safe space provides tools, techniques, and supportive characters to help you understand and manage anxious feelings.",
            therapeutic_themes=["anxiety_management", "safety", "coping_skills"],
            therapeutic_approaches=[TherapeuticApproach.CBT, TherapeuticApproach.DIALECTICAL_BEHAVIORAL],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_duration=timedelta(hours=2),
            setting_description="A cozy, enclosed sanctuary with soft lighting, comfortable seating, and calming elements",
            key_characters=[
                {"name": "Dr. Chen", "role": "Anxiety Specialist", "description": "A compassionate therapist specializing in anxiety disorders"}
            ],
            main_storylines=[
                "Understanding the nature of anxiety",
                "Learning grounding and breathing techniques",
                "Gradual exposure to anxiety triggers in a safe environment"
            ],
            therapeutic_techniques_used=[
                "grounding_techniques", "progressive_muscle_relaxation", "cognitive_restructuring", "exposure_therapy"
            ],
            prerequisites=[
                WorldPrerequisite(
                    prerequisite_type="therapeutic_readiness",
                    description="Basic understanding of anxiety symptoms",
                    required_value=0.4
                )
            ],
            recommended_therapeutic_readiness=0.5,
            content_warnings=["anxiety_triggers", "mild_exposure_exercises"],
            available_parameters=["therapeutic_intensity", "challenge_level", "avoid_topics"],
            tags=["anxiety", "coping_skills", "safe_space", "intermediate"],
            therapeutic_goals_addressed=["anxiety_reduction", "coping_skill_development", "confidence_building"],
            success_metrics=["anxiety_level_reduction", "coping_skill_usage", "exposure_tolerance"],
            player_count=89,
            completion_rate=0.72,
            average_rating=4.5,
            average_session_count=12,
            therapeutic_effectiveness_score=0.78
        )
        
        # Store in cache
        self._world_cache[mindfulness_world.world_id] = mindfulness_world
        self._world_cache[anxiety_world.world_id] = anxiety_world
    
    def get_available_worlds(self, player_id: str, character_id: Optional[str] = None) -> List[WorldSummary]:
        """
        Get list of available worlds for a player, optionally filtered by character compatibility.
        
        Args:
            player_id: ID of the player requesting worlds
            character_id: Optional character ID for compatibility filtering
            
        Returns:
            List of WorldSummary objects
        """
        logger.info(f"Getting available worlds for player {player_id}, character {character_id}")
        
        world_summaries = []
        
        for world_details in self._world_cache.values():
            # Create world summary
            summary = WorldSummary(
                world_id=world_details.world_id,
                name=world_details.name,
                description=world_details.description,
                therapeutic_themes=world_details.therapeutic_themes,
                therapeutic_approaches=world_details.therapeutic_approaches,
                difficulty_level=world_details.difficulty_level,
                estimated_duration=world_details.estimated_duration,
                preview_image=world_details.preview_images[0] if world_details.preview_images else None,
                tags=world_details.tags,
                player_count=world_details.player_count,
                average_rating=world_details.average_rating,
                is_featured=world_details.average_rating >= 4.5,
                created_at=world_details.created_at
            )
            
            # If character is specified, calculate compatibility score
            if character_id:
                # For now, use a simple compatibility calculation
                # In a real implementation, this would fetch the character and calculate compatibility
                summary.compatibility_score = self._calculate_basic_compatibility_score(world_details)
            
            world_summaries.append(summary)
        
        # Sort by compatibility score if character specified, otherwise by rating
        if character_id:
            world_summaries.sort(key=lambda w: w.compatibility_score, reverse=True)
        else:
            world_summaries.sort(key=lambda w: w.average_rating, reverse=True)
        
        logger.info(f"Found {len(world_summaries)} available worlds")
        return world_summaries
    
    def get_world_details(self, world_id: str) -> Optional[WorldDetails]:
        """
        Get detailed information about a specific world.
        
        Args:
            world_id: ID of the world to retrieve
            
        Returns:
            WorldDetails object or None if not found
        """
        logger.info(f"Getting details for world {world_id}")
        
        world_details = self._world_cache.get(world_id)
        if not world_details:
            logger.warning(f"World {world_id} not found in cache")
            return None
        
        return world_details
    
    def customize_world_parameters(self, world_id: str, parameters: WorldParameters) -> Optional[CustomizedWorld]:
        """
        Create a customized version of a world with specific parameters.
        
        Args:
            world_id: ID of the base world
            parameters: Customization parameters
            
        Returns:
            CustomizedWorld object or None if world not found
        """
        logger.info(f"Customizing world {world_id} with parameters")
        
        world_details = self.get_world_details(world_id)
        if not world_details:
            logger.error(f"Cannot customize non-existent world: {world_id}")
            return None
        
        # Validate parameters against available customization options
        if not self._validate_world_parameters(world_details, parameters):
            # Be tolerant in API layer: clamp values into allowed ranges instead of failing
            logger.warning(f"Adjusting out-of-range parameters for world {world_id}")
            try:
                parameters.therapeutic_intensity = max(0.0, min(1.0, parameters.therapeutic_intensity))
                if hasattr(parameters, 'session_length_preference') and parameters.session_length_preference is not None:
                    parameters.session_length_preference = max(10, min(120, parameters.session_length_preference))
            except Exception:
                logger.error(f"Failed to adjust parameters for world {world_id}")
                return None

        # Create customized world (character_id would be provided in real usage)
        customized_world = CustomizedWorld(
            world_id=world_id,
            character_id="",  # Will be set when used with specific character
            customized_parameters=parameters,
            compatibility_report=CompatibilityReport(
                character_id="",
                world_id=world_id,
                overall_score=0.8  # Placeholder score
            )
        )
        
        logger.info(f"Created customized world for {world_id}")
        return customized_world
    
    def check_world_compatibility(self, character: Character, world_id: str) -> Optional[CompatibilityReport]:
        """
        Check compatibility between a character and a world using advanced compatibility checking.
        
        Args:
            character: Character object to check compatibility for
            world_id: ID of the world
            
        Returns:
            CompatibilityReport object or None if world not found
        """
        logger.info(f"Checking compatibility between character {character.character_id} and world {world_id}")
        
        world_details = self.get_world_details(world_id)
        if not world_details:
            logger.error(f"World {world_id} not found for compatibility check")
            return None
        
        # Use advanced compatibility checker
        compatibility_report = self.compatibility_checker.calculate_comprehensive_compatibility(
            character, world_details
        )
        
        logger.info(f"Compatibility score: {compatibility_report.overall_score:.3f}")
        return compatibility_report
    
    def check_world_compatibility_by_id(self, character_id: str, world_id: str) -> Optional[CompatibilityReport]:
        """
        Check compatibility between a character and a world using character ID.
        
        Args:
            character_id: ID of the character
            world_id: ID of the world
            
        Returns:
            CompatibilityReport object or None if character/world not found
        """
        logger.info(f"Checking compatibility between character {character_id} and world {world_id}")
        
        world_details = self.get_world_details(world_id)
        if not world_details:
            logger.error(f"World {world_id} not found for compatibility check")
            return None
        
        # In a real implementation, this would fetch the character from the database
        # For now, we'll create a basic compatibility report using the old method
        compatibility_report = CompatibilityReport(
            character_id=character_id,
            world_id=world_id,
            overall_score=0.0
        )
        
        # Add compatibility factors using basic calculation
        factors = self._calculate_compatibility_factors(world_details)
        for factor in factors:
            compatibility_report.add_compatibility_factor(factor)
        
        # Check prerequisites (basic check without character data)
        compatibility_report.unmet_prerequisites = []
        compatibility_report.prerequisites_met = len(world_details.prerequisites) == 0
        
        # Add basic recommendations and warnings
        if compatibility_report.overall_score < self._compatibility_threshold:
            compatibility_report.recommendations.append(
                "Consider starting with a beginner-level world to build therapeutic readiness"
            )
        
        if world_details.content_warnings:
            compatibility_report.warnings.extend([
                f"This world contains: {', '.join(world_details.content_warnings)}"
            ])
        
        logger.info(f"Compatibility score: {compatibility_report.overall_score:.3f}")
        return compatibility_report
    
    def initialize_character_in_world(self, character_id: str, world_id: str, 
                                    customized_parameters: Optional[WorldParameters] = None) -> Optional[Dict[str, Any]]:
        """
        Initialize a character in a specific world, creating a new session.
        
        Args:
            character_id: ID of the character
            world_id: ID of the world
            customized_parameters: Optional world customization parameters
            
        Returns:
            Session initialization data or None if failed
        """
        logger.info(f"Initializing character {character_id} in world {world_id}")
        
        world_details = self.get_world_details(world_id)
        if not world_details:
            logger.error(f"Cannot initialize character in non-existent world: {world_id}")
            return None
        
        # Check compatibility first (using basic compatibility check since we only have character_id)
        compatibility_report = self.check_world_compatibility_by_id(character_id, world_id)
        if not compatibility_report or compatibility_report.overall_score < self._compatibility_threshold:
            logger.warning(f"Low compatibility between character {character_id} and world {world_id}")
        
        # Use customized parameters or defaults
        parameters = customized_parameters or world_details.default_parameters
        
        # Create session initialization data
        session_data = {
            "session_id": str(uuid.uuid4()),
            "character_id": character_id,
            "world_id": world_id,
            "world_parameters": parameters,
            "compatibility_report": compatibility_report,
            "initial_location": world_details.key_characters[0] if world_details.key_characters else None,
            "available_techniques": world_details.therapeutic_techniques_used,
            "session_goals": world_details.therapeutic_goals_addressed,
            "created_at": datetime.now()
        }
        
        # If we have access to world state manager, initialize the world state
        if self.world_state_manager:
            try:
                # This would integrate with the actual WorldStateManager from tta.prototype
                logger.info("Integrating with WorldStateManager for world initialization")
                # world_state = self.world_state_manager.initialize_world(world_id, character_id)
                # session_data["world_state_id"] = world_state.world_id
            except Exception as e:
                logger.warning(f"Failed to integrate with WorldStateManager: {e}")
        
        # If we have access to therapeutic environment generator, enhance the environment
        if self.therapeutic_environment_generator:
            try:
                logger.info("Integrating with TherapeuticEnvironmentGenerator")
                # This would use the actual TherapeuticEnvironmentGenerator
                # enhanced_environment = self.therapeutic_environment_generator.generate_therapeutic_environment(
                #     therapeutic_theme=world_details.therapeutic_themes[0]
                # )
                # session_data["enhanced_environment"] = enhanced_environment
            except Exception as e:
                logger.warning(f"Failed to integrate with TherapeuticEnvironmentGenerator: {e}")
        
        logger.info(f"Character {character_id} initialized in world {world_id}")
        return session_data
    
    def _calculate_basic_compatibility_score(self, world_details: WorldDetails) -> float:
        """Calculate a basic compatibility score for a world (without character data)."""
        # Simple scoring based on world characteristics
        score = 0.5  # Base score
        
        # Boost score for beginner-friendly worlds
        if world_details.difficulty_level == DifficultyLevel.BEGINNER:
            score += 0.2
        
        # Boost score for highly rated worlds
        if world_details.average_rating >= 4.5:
            score += 0.1
        
        # Boost score for high completion rate
        if world_details.completion_rate >= 0.8:
            score += 0.1
        
        # Boost score for therapeutic effectiveness
        if world_details.therapeutic_effectiveness_score >= 0.8:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_compatibility_factors(self, world_details: WorldDetails) -> List[CompatibilityFactor]:
        """Calculate compatibility factors for a world."""
        factors = []
        
        # Difficulty level factor
        factors.append(CompatibilityFactor(
            factor_name="Difficulty Level",
            score=0.8 if world_details.difficulty_level == DifficultyLevel.BEGINNER else 0.6,
            explanation=f"World difficulty is {world_details.difficulty_level.value}",
            weight=0.3
        ))
        
        # Therapeutic approach factor
        factors.append(CompatibilityFactor(
            factor_name="Therapeutic Approaches",
            score=0.7,  # Would be calculated based on character preferences
            explanation="Therapeutic approaches align with character needs",
            weight=0.4
        ))
        
        # Safety factor
        safety_score = 1.0 - (len(world_details.content_warnings) * 0.1)
        factors.append(CompatibilityFactor(
            factor_name="Content Safety",
            score=max(0.0, safety_score),
            explanation="Content safety assessment based on warnings",
            weight=0.3
        ))
        
        return factors
    
    def _validate_world_parameters(self, world_details: WorldDetails, parameters: WorldParameters) -> bool:
        """Validate that world parameters are compatible with the world."""
        # Check if requested parameters are available for customization
        available_params = set(world_details.available_parameters)
        
        # Basic validation - in a real implementation, this would be more comprehensive
        if "therapeutic_intensity" in available_params:
            if not 0.0 <= parameters.therapeutic_intensity <= 1.0:
                return False
        
        if "session_length_preference" in available_params:
            if not 10 <= parameters.session_length_preference <= 120:
                return False
        
        return True
    
    def get_world_recommendations(self, character: Character, max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized world recommendations for a character.
        
        Args:
            character: Character to get recommendations for
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of recommendation dictionaries with world details and compatibility info
        """
        logger.info(f"Getting world recommendations for character {character.character_id}")
        
        available_worlds = list(self._world_cache.values())
        recommendations = self.compatibility_checker.get_world_recommendations(
            character, available_worlds, max_recommendations
        )
        
        # Convert to dictionary format for easier API consumption
        recommendation_list = []
        for world, compatibility_report in recommendations:
            recommendation_list.append({
                "world_summary": WorldSummary(
                    world_id=world.world_id,
                    name=world.name,
                    description=world.description,
                    therapeutic_themes=world.therapeutic_themes,
                    therapeutic_approaches=world.therapeutic_approaches,
                    difficulty_level=world.difficulty_level,
                    estimated_duration=world.estimated_duration,
                    compatibility_score=compatibility_report.overall_score,
                    preview_image=world.preview_images[0] if world.preview_images else None,
                    tags=world.tags,
                    player_count=world.player_count,
                    average_rating=world.average_rating,
                    is_featured=world.average_rating >= 4.5,
                    created_at=world.created_at
                ),
                "compatibility_report": compatibility_report,
                "suitability_assessment": self.compatibility_checker.assess_world_suitability(character, world)
            })
        
        logger.info(f"Generated {len(recommendation_list)} world recommendations")
        return recommendation_list
    
    def assess_world_suitability_for_character(self, character: Character, world_id: str) -> Optional[Dict[str, Any]]:
        """
        Assess the overall suitability of a specific world for a character.
        
        Args:
            character: Character to assess suitability for
            world_id: ID of the world to assess
            
        Returns:
            Suitability assessment dictionary or None if world not found
        """
        logger.info(f"Assessing world {world_id} suitability for character {character.character_id}")
        
        world_details = self.get_world_details(world_id)
        if not world_details:
            logger.error(f"World {world_id} not found for suitability assessment")
            return None
        
        suitability_assessment = self.compatibility_checker.assess_world_suitability(character, world_details)
        
        logger.info(f"Suitability level: {suitability_assessment['suitability_level']}")
        return suitability_assessment