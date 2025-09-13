"""
Choice Impact Tracker for TTA Living Worlds System

Analyzes and implements the consequences of player choices on the world state,
tracking both immediate and delayed impacts with therapeutic context awareness.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import ChoiceImpact, ChoiceImpactType, WorldState

logger = logging.getLogger(__name__)


class ChoiceImpactTracker:
    """
    Tracks and processes the impact of player choices on the living world.
    
    Analyzes choice consequences, implements immediate and delayed effects,
    and maintains therapeutic context throughout the impact processing.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Impact processing configuration
        self.impact_strength_threshold = config.get("impact_strength_threshold", 0.1)
        self.max_delayed_impacts = config.get("max_delayed_impacts", 10)
        self.therapeutic_weight = config.get("therapeutic_weight", 0.3)
        
        # Active impact tracking
        self.pending_impacts: Dict[str, List[ChoiceImpact]] = {}
        self.processed_impacts: Dict[str, List[ChoiceImpact]] = {}
        
        # Metrics
        self.metrics = {
            "choices_processed": 0,
            "immediate_impacts": 0,
            "delayed_impacts": 0,
            "therapeutic_impacts": 0,
            "cascading_impacts": 0,
        }
        
        logger.info("ChoiceImpactTracker initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Choice Impact Tracker."""
        try:
            logger.info("ChoiceImpactTracker initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ChoiceImpactTracker: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Choice Impact Tracker."""
        try:
            logger.info("ChoiceImpactTracker shutdown complete")
        except Exception as e:
            logger.error(f"Error during ChoiceImpactTracker shutdown: {e}")
    
    async def process_choice(
        self,
        world_state: WorldState,
        choice_id: str,
        choice_data: Dict[str, Any]
    ) -> Optional[ChoiceImpact]:
        """
        Process a player choice and determine its impact on the world.
        
        Args:
            world_state: Current world state
            choice_id: Unique choice identifier
            choice_data: Choice data and context
            
        Returns:
            ChoiceImpact if successful, None otherwise
        """
        try:
            # Create choice impact
            choice_impact = ChoiceImpact(
                choice_id=choice_id,
                player_id=world_state.player_id,
                world_id=world_state.world_id,
            )
            
            # Analyze choice impact
            await self._analyze_choice_impact(choice_impact, world_state, choice_data)
            
            # Determine impact type and strength
            await self._determine_impact_characteristics(choice_impact, choice_data)
            
            # Generate consequences
            await self._generate_consequences(choice_impact, world_state, choice_data)
            
            # Store impact
            if world_state.world_id not in self.processed_impacts:
                self.processed_impacts[world_state.world_id] = []
            self.processed_impacts[world_state.world_id].append(choice_impact)
            
            # Update metrics
            self.metrics["choices_processed"] += 1
            self._update_impact_metrics(choice_impact)
            
            logger.info(f"Processed choice {choice_id} with impact {choice_impact.impact_id}")
            return choice_impact
            
        except Exception as e:
            logger.error(f"Failed to process choice: {e}")
            return None
    
    async def get_pending_impacts(self, world_id: str) -> List[ChoiceImpact]:
        """Get pending impacts for a world."""
        return self.pending_impacts.get(world_id, [])
    
    async def get_processed_impacts(self, world_id: str) -> List[ChoiceImpact]:
        """Get processed impacts for a world."""
        return self.processed_impacts.get(world_id, [])
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    # Private methods
    
    async def _analyze_choice_impact(
        self,
        choice_impact: ChoiceImpact,
        world_state: WorldState,
        choice_data: Dict[str, Any]
    ):
        """Analyze the potential impact of a choice."""
        try:
            # Extract choice context
            choice_text = choice_data.get("text", "")
            choice_context = choice_data.get("context", {})
            
            # Analyze affected entities
            affected_characters = choice_context.get("characters", [])
            affected_locations = choice_context.get("locations", [])
            affected_objects = choice_context.get("objects", [])
            
            # Update choice impact
            choice_impact.affected_characters = affected_characters
            choice_impact.affected_locations = affected_locations
            choice_impact.affected_objects = affected_objects
            choice_impact.scope = affected_characters + affected_locations + affected_objects
            
            logger.debug(f"Analyzed choice impact: {len(choice_impact.scope)} entities affected")
            
        except Exception as e:
            logger.error(f"Failed to analyze choice impact: {e}")
    
    async def _determine_impact_characteristics(
        self,
        choice_impact: ChoiceImpact,
        choice_data: Dict[str, Any]
    ):
        """Determine impact type and strength."""
        try:
            # Determine impact type based on choice characteristics
            choice_urgency = choice_data.get("urgency", "normal")
            choice_scope = choice_data.get("scope", "local")
            
            if choice_urgency == "immediate":
                choice_impact.impact_type = ChoiceImpactType.IMMEDIATE
            elif choice_scope == "cascading":
                choice_impact.impact_type = ChoiceImpactType.CASCADING
            elif "therapeutic" in choice_data.get("tags", []):
                choice_impact.impact_type = ChoiceImpactType.THERAPEUTIC
            else:
                choice_impact.impact_type = ChoiceImpactType.DELAYED
            
            # Calculate impact strength
            base_strength = choice_data.get("strength", 0.5)
            scope_multiplier = len(choice_impact.scope) * 0.1
            therapeutic_multiplier = self.therapeutic_weight if choice_impact.impact_type == ChoiceImpactType.THERAPEUTIC else 1.0
            
            choice_impact.strength = min(1.0, base_strength + scope_multiplier) * therapeutic_multiplier
            
            logger.debug(f"Impact characteristics: type={choice_impact.impact_type.value}, strength={choice_impact.strength:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to determine impact characteristics: {e}")
    
    async def _generate_consequences(
        self,
        choice_impact: ChoiceImpact,
        world_state: WorldState,
        choice_data: Dict[str, Any]
    ):
        """Generate immediate and delayed consequences."""
        try:
            # Generate immediate consequences
            immediate_consequences = {}
            
            # Character state changes
            for character in choice_impact.affected_characters:
                immediate_consequences[f"character_{character}"] = {
                    "relationship_change": choice_data.get("relationship_impact", 0.0),
                    "emotional_state": choice_data.get("emotional_impact", "neutral"),
                }
            
            # Location state changes
            for location in choice_impact.affected_locations:
                immediate_consequences[f"location_{location}"] = {
                    "accessibility": choice_data.get("location_impact", "unchanged"),
                    "atmosphere": choice_data.get("atmosphere_change", "neutral"),
                }
            
            choice_impact.immediate_consequences = immediate_consequences
            
            # Generate delayed consequences if applicable
            if choice_impact.impact_type in [ChoiceImpactType.DELAYED, ChoiceImpactType.CASCADING]:
                delayed_consequences = {
                    "trigger_time": datetime.utcnow() + timedelta(minutes=choice_data.get("delay_minutes", 30)),
                    "consequences": {
                        "narrative_development": choice_data.get("narrative_impact", "minor"),
                        "world_evolution": choice_data.get("evolution_impact", {}),
                    }
                }
                choice_impact.delayed_consequences = delayed_consequences
            
            # Generate therapeutic consequences
            if choice_impact.impact_type == ChoiceImpactType.THERAPEUTIC:
                therapeutic_consequences = {
                    "therapeutic_progress": choice_data.get("therapeutic_progress", {}),
                    "emotional_growth": choice_data.get("emotional_growth", 0.0),
                    "coping_skill_development": choice_data.get("coping_skills", []),
                }
                choice_impact.therapeutic_consequences = therapeutic_consequences
            
            # Generate feedback summary
            choice_impact.feedback_summary = self._generate_feedback_summary(choice_impact, choice_data)
            
            logger.debug(f"Generated consequences for choice impact {choice_impact.impact_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate consequences: {e}")
    
    def _generate_feedback_summary(
        self,
        choice_impact: ChoiceImpact,
        choice_data: Dict[str, Any]
    ) -> str:
        """Generate a summary of the choice impact for feedback."""
        try:
            impact_description = f"Your choice had a {choice_impact.impact_type.value} impact "
            impact_description += f"with strength {choice_impact.strength:.1f}. "
            
            if choice_impact.affected_characters:
                impact_description += f"It affected {len(choice_impact.affected_characters)} character(s). "
            
            if choice_impact.therapeutic_consequences:
                impact_description += "This choice contributed to your therapeutic progress. "
            
            return impact_description
            
        except Exception as e:
            logger.error(f"Failed to generate feedback summary: {e}")
            return "Your choice has been processed."
    
    def _update_impact_metrics(self, choice_impact: ChoiceImpact):
        """Update metrics based on choice impact."""
        if choice_impact.impact_type == ChoiceImpactType.IMMEDIATE:
            self.metrics["immediate_impacts"] += 1
        elif choice_impact.impact_type == ChoiceImpactType.DELAYED:
            self.metrics["delayed_impacts"] += 1
        elif choice_impact.impact_type == ChoiceImpactType.THERAPEUTIC:
            self.metrics["therapeutic_impacts"] += 1
        elif choice_impact.impact_type == ChoiceImpactType.CASCADING:
            self.metrics["cascading_impacts"] += 1
