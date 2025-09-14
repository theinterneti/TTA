"""
Therapeutic World Builder for TTA Living Worlds System

Creates and manages therapeutically designed world environments that support
specific therapeutic approaches, techniques, and patient needs.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import TherapeuticWorld

logger = logging.getLogger(__name__)


class TherapeuticWorldBuilder:
    """
    Creates and manages therapeutically designed world environments.
    
    Builds worlds that support specific therapeutic approaches, integrate
    evidence-based techniques, and adapt to individual patient needs and progress.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Therapeutic configuration
        self.supported_approaches = config.get("supported_approaches", [
            "CBT", "DBT", "ACT", "Mindfulness", "Humanistic", 
            "Psychodynamic", "Solution-Focused", "Narrative"
        ])
        self.safety_protocols = config.get("safety_protocols", {})
        self.crisis_thresholds = config.get("crisis_thresholds", {})
        
        # World templates
        self.world_templates = self._initialize_world_templates()
        
        # Active worlds
        self.active_therapeutic_worlds: Dict[str, TherapeuticWorld] = {}
        
        # Metrics
        self.metrics = {
            "worlds_created": 0,
            "worlds_customized": 0,
            "therapeutic_adaptations": 0,
            "safety_interventions": 0,
        }
        
        logger.info("TherapeuticWorldBuilder initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Therapeutic World Builder."""
        try:
            logger.info("TherapeuticWorldBuilder initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize TherapeuticWorldBuilder: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Therapeutic World Builder."""
        try:
            logger.info("TherapeuticWorldBuilder shutdown complete")
        except Exception as e:
            logger.error(f"Error during TherapeuticWorldBuilder shutdown: {e}")
    
    async def create_therapeutic_world(
        self,
        world_name: str,
        therapeutic_approaches: List[str],
        patient_profile: Dict[str, Any],
        customization_options: Optional[Dict[str, Any]] = None
    ) -> Optional[TherapeuticWorld]:
        """
        Create a new therapeutic world tailored to specific approaches and patient needs.
        
        Args:
            world_name: Name for the therapeutic world
            therapeutic_approaches: List of therapeutic approaches to integrate
            patient_profile: Patient profile and therapeutic needs
            customization_options: Optional world customization settings
            
        Returns:
            TherapeuticWorld if successful, None otherwise
        """
        try:
            world_id = str(uuid.uuid4())
            
            # Validate therapeutic approaches
            valid_approaches = [
                approach for approach in therapeutic_approaches 
                if approach in self.supported_approaches
            ]
            
            if not valid_approaches:
                logger.error("No valid therapeutic approaches provided")
                return None
            
            # Create therapeutic world
            therapeutic_world = TherapeuticWorld(
                world_id=world_id,
                name=world_name,
                description=f"Therapeutic world integrating {', '.join(valid_approaches)}",
                therapeutic_themes=self._extract_therapeutic_themes(valid_approaches),
                therapeutic_approaches=valid_approaches,
                therapeutic_techniques=self._select_therapeutic_techniques(valid_approaches),
                created_by="therapeutic_world_builder",
            )
            
            # Build world structure
            await self._build_world_structure(therapeutic_world, patient_profile)
            
            # Configure therapeutic elements
            await self._configure_therapeutic_elements(therapeutic_world, patient_profile)
            
            # Apply customizations
            if customization_options:
                await self._apply_customizations(therapeutic_world, customization_options)
            
            # Set up safety protocols
            await self._configure_safety_protocols(therapeutic_world, patient_profile)
            
            # Store active world
            self.active_therapeutic_worlds[world_id] = therapeutic_world
            
            # Update metrics
            self.metrics["worlds_created"] += 1
            
            logger.info(f"Created therapeutic world {world_id}: {world_name}")
            return therapeutic_world
            
        except Exception as e:
            logger.error(f"Failed to create therapeutic world: {e}")
            return None
    
    async def customize_world_for_patient(
        self,
        world_id: str,
        patient_profile: Dict[str, Any],
        therapeutic_goals: List[str]
    ) -> bool:
        """
        Customize an existing therapeutic world for a specific patient.
        
        Args:
            world_id: World identifier
            patient_profile: Patient profile and needs
            therapeutic_goals: Specific therapeutic goals
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if world_id not in self.active_therapeutic_worlds:
                logger.error(f"Therapeutic world {world_id} not found")
                return False
            
            therapeutic_world = self.active_therapeutic_worlds[world_id]
            
            # Customize world elements
            await self._customize_locations_for_patient(therapeutic_world, patient_profile)
            await self._customize_characters_for_patient(therapeutic_world, patient_profile)
            await self._customize_narratives_for_goals(therapeutic_world, therapeutic_goals)
            
            # Update progress milestones
            therapeutic_world.progress_milestones = self._create_progress_milestones(
                therapeutic_goals, patient_profile
            )
            
            # Update metrics
            self.metrics["worlds_customized"] += 1
            
            logger.info(f"Customized therapeutic world {world_id} for patient")
            return True
            
        except Exception as e:
            logger.error(f"Failed to customize therapeutic world: {e}")
            return False
    
    async def adapt_world_for_progress(
        self,
        world_id: str,
        therapeutic_progress: Dict[str, float],
        session_feedback: Dict[str, Any]
    ) -> bool:
        """
        Adapt therapeutic world based on patient progress and feedback.
        
        Args:
            world_id: World identifier
            therapeutic_progress: Current therapeutic progress metrics
            session_feedback: Feedback from recent sessions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if world_id not in self.active_therapeutic_worlds:
                logger.error(f"Therapeutic world {world_id} not found")
                return False
            
            therapeutic_world = self.active_therapeutic_worlds[world_id]
            
            # Analyze progress and determine adaptations
            adaptations = self._analyze_required_adaptations(
                therapeutic_progress, session_feedback
            )
            
            # Apply adaptations
            for adaptation in adaptations:
                await self._apply_therapeutic_adaptation(therapeutic_world, adaptation)
            
            # Update metrics
            self.metrics["therapeutic_adaptations"] += len(adaptations)
            
            logger.info(f"Applied {len(adaptations)} adaptations to world {world_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to adapt therapeutic world: {e}")
            return False
    
    async def get_therapeutic_world(self, world_id: str) -> Optional[TherapeuticWorld]:
        """Get therapeutic world by ID."""
        return self.active_therapeutic_worlds.get(world_id)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            **self.metrics,
            "active_worlds": len(self.active_therapeutic_worlds),
        }
    
    # Private methods
    
    def _initialize_world_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize therapeutic world templates."""
        return {
            "CBT": {
                "themes": ["cognitive_restructuring", "behavioral_activation", "exposure"],
                "locations": ["therapy_office", "challenge_scenarios", "practice_environments"],
                "techniques": ["thought_records", "behavioral_experiments", "graded_exposure"],
            },
            "DBT": {
                "themes": ["distress_tolerance", "emotion_regulation", "interpersonal_effectiveness"],
                "locations": ["mindfulness_garden", "crisis_scenarios", "relationship_contexts"],
                "techniques": ["mindfulness_exercises", "distress_tolerance_skills", "DEAR_MAN"],
            },
            "ACT": {
                "themes": ["psychological_flexibility", "values_clarification", "mindful_acceptance"],
                "locations": ["values_exploration_space", "mindfulness_environments", "commitment_challenges"],
                "techniques": ["values_exercises", "defusion_techniques", "mindfulness_practices"],
            },
            "Mindfulness": {
                "themes": ["present_moment_awareness", "non_judgmental_observation", "acceptance"],
                "locations": ["meditation_spaces", "nature_environments", "daily_life_contexts"],
                "techniques": ["breathing_exercises", "body_scans", "walking_meditation"],
            },
        }
    
    def _extract_therapeutic_themes(self, approaches: List[str]) -> List[str]:
        """Extract therapeutic themes from approaches."""
        themes = []
        for approach in approaches:
            template = self.world_templates.get(approach, {})
            themes.extend(template.get("themes", []))
        return list(set(themes))  # Remove duplicates
    
    def _select_therapeutic_techniques(self, approaches: List[str]) -> List[str]:
        """Select therapeutic techniques for approaches."""
        techniques = []
        for approach in approaches:
            template = self.world_templates.get(approach, {})
            techniques.extend(template.get("techniques", []))
        return list(set(techniques))  # Remove duplicates
    
    async def _build_world_structure(
        self, therapeutic_world: TherapeuticWorld, patient_profile: Dict[str, Any]
    ):
        """Build the basic structure of the therapeutic world."""
        # Create key locations based on therapeutic approaches
        locations = []
        for approach in therapeutic_world.therapeutic_approaches:
            template = self.world_templates.get(approach, {})
            approach_locations = template.get("locations", [])
            
            for location_type in approach_locations:
                location = {
                    "id": f"{location_type}_{len(locations)}",
                    "name": location_type.replace("_", " ").title(),
                    "type": location_type,
                    "therapeutic_approach": approach,
                    "accessibility": "available",
                    "safety_level": "safe",
                }
                locations.append(location)
        
        therapeutic_world.key_locations = locations
        
        # Create key characters (therapeutic guides, practice partners, etc.)
        characters = [
            {
                "id": "therapeutic_guide",
                "name": "Therapeutic Guide",
                "role": "guide",
                "approaches": therapeutic_world.therapeutic_approaches,
                "personality": "supportive_professional",
            },
            {
                "id": "practice_partner",
                "name": "Practice Partner",
                "role": "peer",
                "approaches": ["general"],
                "personality": "encouraging_peer",
            },
        ]
        therapeutic_world.key_characters = characters
    
    async def _configure_therapeutic_elements(
        self, therapeutic_world: TherapeuticWorld, patient_profile: Dict[str, Any]
    ):
        """Configure therapeutic elements based on patient profile."""
        # Create narrative elements that support therapeutic goals
        narrative_elements = []
        
        for theme in therapeutic_world.therapeutic_themes:
            element = {
                "id": f"narrative_{theme}",
                "theme": theme,
                "scenarios": self._create_therapeutic_scenarios(theme),
                "progression_levels": ["beginner", "intermediate", "advanced"],
                "safety_considerations": self._get_safety_considerations(theme),
            }
            narrative_elements.append(element)
        
        therapeutic_world.narrative_elements = narrative_elements
    
    async def _apply_customizations(
        self, therapeutic_world: TherapeuticWorld, customization_options: Dict[str, Any]
    ):
        """Apply customization options to the therapeutic world."""
        # Apply visual customizations
        if "visual_theme" in customization_options:
            for location in therapeutic_world.key_locations:
                location["visual_theme"] = customization_options["visual_theme"]
        
        # Apply difficulty customizations
        if "difficulty_level" in customization_options:
            difficulty = customization_options["difficulty_level"]
            for element in therapeutic_world.narrative_elements:
                element["default_difficulty"] = difficulty
    
    async def _configure_safety_protocols(
        self, therapeutic_world: TherapeuticWorld, patient_profile: Dict[str, Any]
    ):
        """Configure safety protocols for the therapeutic world."""
        safety_guidelines = {
            "crisis_detection": {
                "enabled": True,
                "sensitivity": patient_profile.get("crisis_sensitivity", "medium"),
                "escalation_triggers": ["severe_distress", "self_harm_ideation", "dissociation"],
            },
            "content_filtering": {
                "enabled": True,
                "blocked_themes": patient_profile.get("trigger_themes", []),
                "intensity_limits": patient_profile.get("intensity_limits", {}),
            },
            "session_limits": {
                "max_session_duration": patient_profile.get("max_session_duration", 60),
                "break_reminders": True,
                "fatigue_detection": True,
            },
        }
        
        crisis_protocols = {
            "immediate_response": {
                "pause_session": True,
                "activate_support": True,
                "provide_resources": True,
            },
            "escalation_procedures": {
                "notify_clinician": patient_profile.get("has_clinician", False),
                "emergency_contacts": patient_profile.get("emergency_contacts", []),
                "crisis_hotlines": True,
            },
        }
        
        therapeutic_world.safety_guidelines = safety_guidelines
        therapeutic_world.crisis_protocols = crisis_protocols
    
    def _create_therapeutic_scenarios(self, theme: str) -> List[Dict[str, Any]]:
        """Create therapeutic scenarios for a theme."""
        scenario_templates = {
            "cognitive_restructuring": [
                {"name": "Thought Challenge", "description": "Practice identifying and challenging negative thoughts"},
                {"name": "Evidence Examination", "description": "Examine evidence for and against thoughts"},
            ],
            "emotion_regulation": [
                {"name": "Emotion Identification", "description": "Practice identifying and naming emotions"},
                {"name": "Coping Skills Practice", "description": "Apply emotion regulation techniques"},
            ],
            "mindfulness": [
                {"name": "Present Moment Awareness", "description": "Practice staying present and aware"},
                {"name": "Non-Judgmental Observation", "description": "Observe thoughts and feelings without judgment"},
            ],
        }
        
        return scenario_templates.get(theme, [
            {"name": f"{theme.title()} Practice", "description": f"Practice {theme} skills"}
        ])
    
    def _get_safety_considerations(self, theme: str) -> List[str]:
        """Get safety considerations for a therapeutic theme."""
        safety_map = {
            "exposure": ["gradual_progression", "escape_options", "support_availability"],
            "trauma_processing": ["grounding_techniques", "titration", "stabilization_first"],
            "emotion_regulation": ["distress_tolerance", "safety_planning", "crisis_resources"],
        }
        
        return safety_map.get(theme, ["general_safety", "progress_monitoring"])
    
    async def _customize_locations_for_patient(
        self, therapeutic_world: TherapeuticWorld, patient_profile: Dict[str, Any]
    ):
        """Customize locations based on patient preferences and needs."""
        preferences = patient_profile.get("environment_preferences", {})
        
        for location in therapeutic_world.key_locations:
            # Apply visual preferences
            if "preferred_settings" in preferences:
                location["customization"] = preferences["preferred_settings"]
            
            # Apply accessibility needs
            if "accessibility_needs" in patient_profile:
                location["accessibility_features"] = patient_profile["accessibility_needs"]
    
    async def _customize_characters_for_patient(
        self, therapeutic_world: TherapeuticWorld, patient_profile: Dict[str, Any]
    ):
        """Customize characters based on patient preferences."""
        preferences = patient_profile.get("interaction_preferences", {})
        
        for character in therapeutic_world.key_characters:
            # Apply communication style preferences
            if "communication_style" in preferences:
                character["communication_style"] = preferences["communication_style"]
            
            # Apply cultural considerations
            if "cultural_background" in patient_profile:
                character["cultural_awareness"] = patient_profile["cultural_background"]
    
    async def _customize_narratives_for_goals(
        self, therapeutic_world: TherapeuticWorld, therapeutic_goals: List[str]
    ):
        """Customize narrative elements for specific therapeutic goals."""
        for element in therapeutic_world.narrative_elements:
            # Align scenarios with therapeutic goals
            relevant_goals = [goal for goal in therapeutic_goals if goal in element["theme"]]
            if relevant_goals:
                element["goal_alignment"] = relevant_goals
                element["priority"] = "high"
    
    def _create_progress_milestones(
        self, therapeutic_goals: List[str], patient_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create progress milestones for therapeutic goals."""
        milestones = []
        
        for goal in therapeutic_goals:
            milestone = {
                "goal": goal,
                "milestones": [
                    {"level": "initial", "description": f"Begin working on {goal}", "threshold": 0.2},
                    {"level": "progress", "description": f"Show progress in {goal}", "threshold": 0.5},
                    {"level": "proficiency", "description": f"Demonstrate proficiency in {goal}", "threshold": 0.8},
                    {"level": "mastery", "description": f"Master {goal} skills", "threshold": 0.95},
                ],
            }
            milestones.append(milestone)
        
        return milestones
    
    def _analyze_required_adaptations(
        self, therapeutic_progress: Dict[str, float], session_feedback: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze what adaptations are needed based on progress and feedback."""
        adaptations = []
        
        # Check for areas needing more support
        for goal, progress in therapeutic_progress.items():
            if progress < 0.3:  # Low progress
                adaptations.append({
                    "type": "increase_support",
                    "target": goal,
                    "action": "add_scaffolding",
                })
            elif progress > 0.8:  # High progress
                adaptations.append({
                    "type": "increase_challenge",
                    "target": goal,
                    "action": "advance_difficulty",
                })
        
        # Check session feedback for needed adjustments
        if session_feedback.get("difficulty") == "too_easy":
            adaptations.append({
                "type": "increase_difficulty",
                "target": "general",
                "action": "raise_challenge_level",
            })
        elif session_feedback.get("difficulty") == "too_hard":
            adaptations.append({
                "type": "decrease_difficulty",
                "target": "general",
                "action": "lower_challenge_level",
            })
        
        return adaptations
    
    async def _apply_therapeutic_adaptation(
        self, therapeutic_world: TherapeuticWorld, adaptation: Dict[str, Any]
    ):
        """Apply a specific therapeutic adaptation to the world."""
        adaptation_type = adaptation["type"]
        target = adaptation["target"]
        action = adaptation["action"]
        
        if adaptation_type == "increase_support":
            # Add more supportive elements
            for element in therapeutic_world.narrative_elements:
                if target in element["theme"]:
                    element["support_level"] = "high"
                    element["guidance_frequency"] = "frequent"
        
        elif adaptation_type == "increase_challenge":
            # Increase challenge level
            for element in therapeutic_world.narrative_elements:
                if target in element["theme"]:
                    element["challenge_level"] = "advanced"
                    element["complexity"] = "high"
        
        elif adaptation_type == "increase_difficulty":
            # Raise overall difficulty
            for location in therapeutic_world.key_locations:
                location["difficulty_modifier"] = 1.2
        
        elif adaptation_type == "decrease_difficulty":
            # Lower overall difficulty
            for location in therapeutic_world.key_locations:
                location["difficulty_modifier"] = 0.8
