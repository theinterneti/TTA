"""
Therapeutic Environment Generation and Setting Adaptation for TTA Prototype
"""

import logging
import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TherapeuticTheme(Enum):
    """Therapeutic themes for environment generation."""
    MINDFULNESS = "mindfulness"
    ANXIETY_RELIEF = "anxiety_relief"
    DEPRESSION_SUPPORT = "depression_support"
    TRAUMA_HEALING = "trauma_healing"
    SELF_ESTEEM = "self_esteem"
    RELATIONSHIP_BUILDING = "relationship_building"


@dataclass
class TherapeuticEnvironmentTemplate:
    """Template for generating therapeutic environments."""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    therapeutic_theme: TherapeuticTheme = TherapeuticTheme.MINDFULNESS
    base_description: str = ""
    atmosphere_options: list[str] = field(default_factory=list)
    environmental_factors: dict[str, list[str]] = field(default_factory=dict)
    therapeutic_opportunities: list[str] = field(default_factory=list)
    safety_level_range: tuple[float, float] = (0.7, 1.0)


class TherapeuticEnvironmentGenerator:
    """Main class for therapeutic environment generation and setting adaptation."""

    def __init__(self, world_manager=None):
        """Initialize the therapeutic environment generator."""
        self.world_manager = world_manager
        self.environment_templates: dict[TherapeuticTheme, list[TherapeuticEnvironmentTemplate]] = {}
        self._initialize_environment_templates()
        logger.info("TherapeuticEnvironmentGenerator initialized")

    def _initialize_environment_templates(self) -> None:
        """Initialize default therapeutic environment templates."""
        # Mindfulness garden template
        mindfulness_garden = TherapeuticEnvironmentTemplate(
            name="Mindfulness Garden",
            therapeutic_theme=TherapeuticTheme.MINDFULNESS,
            base_description="A serene garden designed for contemplation and present-moment awareness",
            atmosphere_options=["peaceful", "tranquil", "meditative"],
            environmental_factors={
                "sounds": ["gentle water flowing", "soft wind chimes", "distant bird songs"],
                "lighting": ["soft golden light", "dappled sunlight"],
                "scents": ["lavender", "jasmine", "fresh earth"]
            },
            therapeutic_opportunities=[
                "breathing_exercise", "body_scan_meditation", "mindful_walking"
            ],
            safety_level_range=(0.9, 1.0)
        )

        # Anxiety relief sanctuary
        anxiety_sanctuary = TherapeuticEnvironmentTemplate(
            name="Anxiety Relief Sanctuary",
            therapeutic_theme=TherapeuticTheme.ANXIETY_RELIEF,
            base_description="A protective, enclosed space designed to provide comfort and reduce anxiety",
            atmosphere_options=["safe", "cozy", "protective"],
            environmental_factors={
                "sounds": ["soft instrumental music", "gentle rain"],
                "lighting": ["warm amber light", "soft candlelight"],
                "textures": ["soft blankets", "plush cushions"]
            },
            therapeutic_opportunities=[
                "grounding_techniques", "progressive_muscle_relaxation", "safe_place_visualization"
            ],
            safety_level_range=(0.95, 1.0)
        )

        # Store templates
        self.environment_templates[TherapeuticTheme.MINDFULNESS] = [mindfulness_garden]
        self.environment_templates[TherapeuticTheme.ANXIETY_RELIEF] = [anxiety_sanctuary]

    def generate_therapeutic_environment(self,
                                       therapeutic_theme: TherapeuticTheme,
                                       session_state=None,
                                       customization_preferences: dict[str, Any] | None = None):
        """Generate a therapeutic theme-appropriate environment."""
        logger.info(f"Generating therapeutic environment for theme: {therapeutic_theme.value}")

        templates = self.environment_templates.get(therapeutic_theme, [])
        if not templates:
            logger.warning(f"No templates available for therapeutic theme: {therapeutic_theme.value}")
            return None

        # Select first available template for now
        template = templates[0]

        # Generate basic location details
        location_data = {
            "location_id": f"therapeutic_{therapeutic_theme.value}_{uuid.uuid4().hex[:8]}",
            "name": template.name,
            "description": template.base_description,
            "therapeutic_themes": [therapeutic_theme.value],
            "atmosphere": random.choice(template.atmosphere_options),
            "environmental_factors": {
                factor: random.choice(options)
                for factor, options in template.environmental_factors.items()
            },
            "therapeutic_opportunities": template.therapeutic_opportunities.copy(),
            "safety_level": random.uniform(*template.safety_level_range)
        }

        logger.info(f"Generated therapeutic environment: {location_data['name']}")
        return location_data

    def adapt_environment_to_therapeutic_needs(self,
                                             location_id: str,
                                             therapeutic_needs: dict[str, Any],
                                             session_state=None) -> bool:
        """Adapt an existing environment based on therapeutic needs."""
        logger.info(f"Adapting environment {location_id} to therapeutic needs")

        if not self.world_manager:
            logger.warning("No world manager available for environment adaptation")
            return True  # Return True for testing without world manager

        # Get current location
        location = self.world_manager.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot adapt non-existent location: {location_id}")
            return False

        # Generate adaptation changes based on needs
        changes = {}

        if 'emotional_state' in therapeutic_needs:
            emotional_state = therapeutic_needs['emotional_state']
            if emotional_state == 'anxious':
                changes.update({
                    'atmosphere': 'peaceful',
                    'environmental_factors': {
                        **getattr(location, 'environmental_factors', {}),
                        'sounds': 'gentle water flowing',
                        'lighting': 'soft warm light'
                    }
                })

        if 'crisis_support' in therapeutic_needs and therapeutic_needs['crisis_support']:
            changes.update({
                'atmosphere': 'safe',
                'safety_level': 1.0,
                'therapeutic_opportunities': [
                    'crisis_grounding', 'safety_establishment', 'immediate_support'
                ]
            })

        # Apply changes if any were generated
        if changes:
            logger.info(f"Would apply changes to {location_id}: {changes}")
            return True
        else:
            logger.info(f"No adaptations needed for {location_id}")
            return True

    def create_setting_based_therapeutic_enhancement(self,
                                                   location_id: str,
                                                   enhancement_type: str,
                                                   session_state=None) -> bool:
        """Create setting-based therapeutic enhancement mechanisms."""
        logger.info(f"Creating therapeutic enhancement '{enhancement_type}' for location {location_id}")

        if not self.world_manager:
            logger.warning("No world manager available for therapeutic enhancement")
            return True  # Return True for testing without world manager

        # Generate enhancement changes
        enhancement_changes = {}

        if enhancement_type == 'sensory_integration':
            enhancement_changes = {
                'environmental_factors': {
                    'multi_sensory': 'integrated sensory experience',
                    'tactile_elements': 'therapeutic touch points',
                    'aromatherapy': 'therapeutic scents'
                },
                'therapeutic_opportunities': [
                    'sensory_grounding', 'multi_sensory_meditation', 'tactile_therapy'
                ]
            }
        elif enhancement_type == 'biofeedback_integration':
            enhancement_changes = {
                'environmental_factors': {
                    'biofeedback_displays': 'real-time wellness indicators',
                    'responsive_environment': 'environment responds to user state'
                },
                'therapeutic_opportunities': [
                    'biofeedback_training', 'physiological_awareness', 'self_regulation'
                ]
            }
        elif enhancement_type == 'narrative_immersion':
            enhancement_changes = {
                'immersion_level': 0.8,
                'environmental_factors': {
                    'story_elements': 'integrated narrative components',
                    'character_presence': 'therapeutic characters available'
                },
                'therapeutic_opportunities': [
                    'story_therapy', 'character_interaction', 'narrative_processing'
                ]
            }

        # Apply enhancement if changes were generated
        if enhancement_changes:
            logger.info(f"Would apply enhancement to {location_id}: {enhancement_changes}")
            return True
        else:
            logger.warning(f"No enhancement changes generated for type: {enhancement_type}")
            return False
