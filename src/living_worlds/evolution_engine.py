"""
Evolution Engine for TTA Living Worlds System

Manages real-time world evolution and dynamic updates based on player actions,
time passage, therapeutic milestones, and narrative requirements.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import EvolutionEvent, EvolutionTrigger, WorldState

logger = logging.getLogger(__name__)


class EvolutionEngine:
    """
    Manages real-time world evolution and dynamic content updates.
    
    Processes evolution triggers, generates evolution events, and coordinates
    world changes to maintain engaging and therapeutically meaningful experiences.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Evolution configuration
        self.evolution_frequency = config.get("evolution_frequency", 300)  # seconds
        self.max_evolution_events = config.get("max_evolution_events", 5)
        self.therapeutic_evolution_weight = config.get("therapeutic_evolution_weight", 0.4)
        
        # Evolution tracking
        self.pending_events: Dict[str, List[EvolutionEvent]] = {}
        self.processed_events: Dict[str, List[EvolutionEvent]] = {}
        self.last_evolution_check: Dict[str, datetime] = {}
        
        # Metrics
        self.metrics = {
            "evolution_checks": 0,
            "events_generated": 0,
            "player_action_triggers": 0,
            "time_passage_triggers": 0,
            "therapeutic_triggers": 0,
            "narrative_triggers": 0,
        }
        
        logger.info("EvolutionEngine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Evolution Engine."""
        try:
            logger.info("EvolutionEngine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize EvolutionEngine: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the Evolution Engine."""
        try:
            logger.info("EvolutionEngine shutdown complete")
        except Exception as e:
            logger.error(f"Error during EvolutionEngine shutdown: {e}")
    
    async def check_evolution_triggers(self, world_state: WorldState) -> List[EvolutionEvent]:
        """
        Check for evolution triggers and generate evolution events.
        
        Args:
            world_state: Current world state
            
        Returns:
            List of evolution events to process
        """
        try:
            evolution_events = []
            world_id = world_state.world_id
            
            # Update last check time
            current_time = datetime.utcnow()
            self.last_evolution_check[world_id] = current_time
            
            # Check time passage triggers
            time_events = await self._check_time_passage_triggers(world_state)
            evolution_events.extend(time_events)
            
            # Check player action triggers
            action_events = await self._check_player_action_triggers(world_state)
            evolution_events.extend(action_events)
            
            # Check therapeutic milestone triggers
            therapeutic_events = await self._check_therapeutic_triggers(world_state)
            evolution_events.extend(therapeutic_events)
            
            # Check narrative requirement triggers
            narrative_events = await self._check_narrative_triggers(world_state)
            evolution_events.extend(narrative_events)
            
            # Store pending events
            if world_id not in self.pending_events:
                self.pending_events[world_id] = []
            self.pending_events[world_id].extend(evolution_events)
            
            # Update metrics
            self.metrics["evolution_checks"] += 1
            self.metrics["events_generated"] += len(evolution_events)
            
            logger.debug(f"Generated {len(evolution_events)} evolution events for world {world_id}")
            return evolution_events
            
        except Exception as e:
            logger.error(f"Failed to check evolution triggers: {e}")
            return []
    
    async def get_pending_events(self, world_id: str) -> List[EvolutionEvent]:
        """Get pending evolution events for a world."""
        return self.pending_events.get(world_id, [])
    
    async def get_processed_events(self, world_id: str) -> List[EvolutionEvent]:
        """Get processed evolution events for a world."""
        return self.processed_events.get(world_id, [])
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    # Private methods
    
    async def _check_time_passage_triggers(self, world_state: WorldState) -> List[EvolutionEvent]:
        """Check for time passage evolution triggers."""
        try:
            events = []
            world_id = world_state.world_id
            current_time = datetime.utcnow()
            
            # Check if enough time has passed since last evolution
            last_check = self.last_evolution_check.get(world_id, world_state.created_at)
            time_since_last = (current_time - last_check).total_seconds()
            
            if time_since_last >= self.evolution_frequency:
                # Generate time-based evolution event
                event = EvolutionEvent(
                    world_id=world_id,
                    trigger=EvolutionTrigger.TIME_PASSAGE,
                    event_type="ambient_evolution",
                    event_description="World evolves naturally over time",
                    state_changes={
                        "ambient_changes": {
                            "weather": self._generate_weather_change(),
                            "npc_activities": self._generate_npc_activities(),
                            "environmental_shifts": self._generate_environmental_shifts(),
                        }
                    }
                )
                events.append(event)
                self.metrics["time_passage_triggers"] += 1
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to check time passage triggers: {e}")
            return []
    
    async def _check_player_action_triggers(self, world_state: WorldState) -> List[EvolutionEvent]:
        """Check for player action evolution triggers."""
        try:
            events = []
            
            # Check recent player actions from world state
            recent_events = world_state.recent_events[-5:]  # Last 5 events
            
            for event_id in recent_events:
                # Generate evolution based on player action
                if self._should_trigger_action_evolution(event_id, world_state):
                    event = EvolutionEvent(
                        world_id=world_state.world_id,
                        trigger=EvolutionTrigger.PLAYER_ACTION,
                        event_type="action_consequence",
                        event_description=f"World responds to player action {event_id}",
                        affected_entities=self._get_affected_entities_for_action(event_id),
                        state_changes=self._generate_action_consequences(event_id, world_state)
                    )
                    events.append(event)
                    self.metrics["player_action_triggers"] += 1
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to check player action triggers: {e}")
            return []
    
    async def _check_therapeutic_triggers(self, world_state: WorldState) -> List[EvolutionEvent]:
        """Check for therapeutic milestone evolution triggers."""
        try:
            events = []
            
            # Check therapeutic progress
            therapeutic_progress = world_state.therapeutic_progress
            
            for goal, progress in therapeutic_progress.items():
                if progress >= 0.8 and self._should_trigger_therapeutic_evolution(goal, world_state):
                    # Generate therapeutic milestone event
                    event = EvolutionEvent(
                        world_id=world_state.world_id,
                        trigger=EvolutionTrigger.THERAPEUTIC_MILESTONE,
                        event_type="therapeutic_milestone",
                        event_description=f"Therapeutic milestone reached: {goal}",
                        therapeutic_changes={
                            "milestone_achieved": goal,
                            "new_opportunities": self._generate_therapeutic_opportunities(goal),
                            "world_adaptation": self._generate_therapeutic_world_changes(goal),
                        }
                    )
                    events.append(event)
                    self.metrics["therapeutic_triggers"] += 1
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to check therapeutic triggers: {e}")
            return []
    
    async def _check_narrative_triggers(self, world_state: WorldState) -> List[EvolutionEvent]:
        """Check for narrative requirement evolution triggers."""
        try:
            events = []
            
            # Check narrative requirements based on world properties
            narrative_state = world_state.world_properties.get("narrative_state", {})
            
            # Check for story progression needs
            if self._needs_story_progression(narrative_state):
                event = EvolutionEvent(
                    world_id=world_state.world_id,
                    trigger=EvolutionTrigger.NARRATIVE_REQUIREMENT,
                    event_type="story_progression",
                    event_description="Story requires progression",
                    narrative_changes={
                        "story_advancement": self._generate_story_advancement(),
                        "new_plot_elements": self._generate_plot_elements(),
                        "character_developments": self._generate_character_developments(),
                    }
                )
                events.append(event)
                self.metrics["narrative_triggers"] += 1
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to check narrative triggers: {e}")
            return []
    
    # Helper methods for evolution generation
    
    def _generate_weather_change(self) -> Dict[str, Any]:
        """Generate weather changes for ambient evolution."""
        weather_options = ["sunny", "cloudy", "rainy", "foggy", "windy"]
        return {
            "current_weather": weather_options[hash(str(datetime.utcnow())) % len(weather_options)],
            "weather_intensity": 0.5,
        }
    
    def _generate_npc_activities(self) -> Dict[str, Any]:
        """Generate NPC activities for ambient evolution."""
        return {
            "market_activity": "moderate",
            "social_gatherings": "few",
            "work_activities": "normal",
        }
    
    def _generate_environmental_shifts(self) -> Dict[str, Any]:
        """Generate environmental shifts for ambient evolution."""
        return {
            "lighting": "natural",
            "sounds": "ambient",
            "crowd_density": "normal",
        }
    
    def _should_trigger_action_evolution(self, event_id: str, world_state: WorldState) -> bool:
        """Determine if a player action should trigger evolution."""
        # Simple heuristic - trigger evolution for significant actions
        return hash(event_id) % 3 == 0  # Trigger for ~33% of actions
    
    def _get_affected_entities_for_action(self, event_id: str) -> List[str]:
        """Get entities affected by a player action."""
        # Placeholder implementation
        return [f"entity_{hash(event_id) % 5}"]
    
    def _generate_action_consequences(self, event_id: str, world_state: WorldState) -> Dict[str, Any]:
        """Generate consequences for a player action."""
        return {
            "reputation_changes": {"local_reputation": 0.1},
            "relationship_changes": {"npc_relationships": {}},
            "world_state_changes": {"minor_adjustments": True},
        }
    
    def _should_trigger_therapeutic_evolution(self, goal: str, world_state: WorldState) -> bool:
        """Determine if therapeutic progress should trigger evolution."""
        return True  # Always trigger for therapeutic milestones
    
    def _generate_therapeutic_opportunities(self, goal: str) -> List[str]:
        """Generate new therapeutic opportunities."""
        return [f"advanced_{goal}_practice", f"{goal}_integration_challenge"]
    
    def _generate_therapeutic_world_changes(self, goal: str) -> Dict[str, Any]:
        """Generate world changes for therapeutic milestones."""
        return {
            "new_areas_unlocked": [f"{goal}_practice_area"],
            "character_interactions": f"enhanced_{goal}_dialogues",
        }
    
    def _needs_story_progression(self, narrative_state: Dict[str, Any]) -> bool:
        """Determine if story needs progression."""
        current_act = narrative_state.get("current_act", 1)
        scenes_in_act = narrative_state.get("scenes_in_current_act", 0)
        return scenes_in_act >= 5  # Progress after 5 scenes
    
    def _generate_story_advancement(self) -> Dict[str, Any]:
        """Generate story advancement elements."""
        return {
            "act_progression": True,
            "new_story_threads": ["mystery_deepens", "character_revelation"],
        }
    
    def _generate_plot_elements(self) -> List[str]:
        """Generate new plot elements."""
        return ["unexpected_visitor", "hidden_message", "mysterious_event"]
    
    def _generate_character_developments(self) -> Dict[str, Any]:
        """Generate character development events."""
        return {
            "character_growth": {"main_character": "confidence_boost"},
            "relationship_changes": {"ally_trust": 0.2},
        }
