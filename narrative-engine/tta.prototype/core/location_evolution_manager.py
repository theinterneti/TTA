"""
Location Evolution Manager for TTA Living Worlds

This module implements the LocationEvolutionManager class that handles dynamic
changes to locations over time. It manages location state changes, environmental
evolution, seasonal changes, location history generation, and significant event
tracking.

Classes:
    LocationEvolutionManager: Manages location evolution and environmental changes
    LocationChange: Represents a change to a location's state
    LocationHistory: Tracks location-specific historical events
    Season: Enumeration of seasonal states
    EnvironmentalFactor: Represents environmental conditions
"""

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Add models path for data models access
models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from living_worlds_models import (
        EntityType,
        EventType,
        Timeline,
        TimelineEvent,
        ValidationError,
    )
except ImportError:
    from ..models.living_worlds_models import (
        EntityType,
        EventType,
        TimelineEvent,
        ValidationError,
    )

# Import existing worldbuilding system
try:
    from timeline_engine import TimelineEngine
    from worldbuilding_setting_management import (
        LocationDetails,
        LocationType,
        ValidationResult,
        WorldbuildingSettingManagement,
        WorldChange,
        WorldChangeType,
    )
except ImportError:
    from .timeline_engine import TimelineEngine
    from .worldbuilding_setting_management import (
        LocationDetails,
        LocationType,
        WorldbuildingSettingManagement,
        WorldChange,
        WorldChangeType,
    )

logger = logging.getLogger(__name__)


class Season(Enum):
    """Seasonal states for environmental changes."""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class EnvironmentalFactorType(Enum):
    """Types of environmental factors."""
    WEATHER = "weather"
    LIGHTING = "lighting"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VEGETATION = "vegetation"
    WILDLIFE = "wildlife"
    SOUNDS = "sounds"
    ATMOSPHERE = "atmosphere"


@dataclass
class EnvironmentalFactor:
    """Represents environmental conditions affecting a location."""
    factor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    factor_type: EnvironmentalFactorType = EnvironmentalFactorType.WEATHER
    current_value: str = ""
    intensity: float = 0.5  # 0.0 to 1.0
    seasonal_variation: bool = True
    change_rate: float = 0.1  # How quickly this factor changes
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate environmental factor data."""
        if not self.factor_id.strip():
            raise ValidationError("Factor ID cannot be empty")

        if not self.current_value.strip():
            raise ValidationError("Current value cannot be empty")

        if not 0.0 <= self.intensity <= 1.0:
            raise ValidationError("Intensity must be between 0.0 and 1.0")

        if not 0.0 <= self.change_rate <= 1.0:
            raise ValidationError("Change rate must be between 0.0 and 1.0")

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'factor_id': self.factor_id,
            'factor_type': self.factor_type.value,
            'current_value': self.current_value,
            'intensity': self.intensity,
            'seasonal_variation': self.seasonal_variation,
            'change_rate': self.change_rate,
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'EnvironmentalFactor':
        """Create from dictionary."""
        if 'factor_type' in data:
            data['factor_type'] = EnvironmentalFactorType(data['factor_type'])
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


@dataclass
class LocationChange:
    """Represents a change to a location's state."""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    location_id: str = ""
    change_type: str = "environmental"  # environmental, structural, accessibility
    description: str = ""
    old_state: dict[str, Any] = field(default_factory=dict)
    new_state: dict[str, Any] = field(default_factory=dict)
    trigger_event: str | None = None  # Event that caused this change
    timestamp: datetime = field(default_factory=datetime.now)
    reversible: bool = True
    significance_level: int = 5  # 1-10

    def validate(self) -> bool:
        """Validate location change data."""
        if not self.change_id.strip():
            raise ValidationError("Change ID cannot be empty")

        if not self.location_id.strip():
            raise ValidationError("Location ID cannot be empty")

        if not self.description.strip():
            raise ValidationError("Change description cannot be empty")

        if not 1 <= self.significance_level <= 10:
            raise ValidationError("Significance level must be between 1 and 10")

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'change_id': self.change_id,
            'location_id': self.location_id,
            'change_type': self.change_type,
            'description': self.description,
            'old_state': self.old_state,
            'new_state': self.new_state,
            'trigger_event': self.trigger_event,
            'timestamp': self.timestamp.isoformat(),
            'reversible': self.reversible,
            'significance_level': self.significance_level
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LocationChange':
        """Create from dictionary."""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class LocationHistory:
    """Tracks location-specific historical events and changes."""
    location_id: str = ""
    founding_events: list[TimelineEvent] = field(default_factory=list)
    significant_events: list[TimelineEvent] = field(default_factory=list)
    environmental_changes: list[LocationChange] = field(default_factory=list)
    visitor_history: list[str] = field(default_factory=list)  # Character IDs
    cultural_evolution: list[TimelineEvent] = field(default_factory=list)
    seasonal_patterns: dict[str, dict[str, Any]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate location history data."""
        if not self.location_id.strip():
            raise ValidationError("Location ID cannot be empty")

        # Validate all events
        for event in self.founding_events + self.significant_events + self.cultural_evolution:
            event.validate()

        # Validate all changes
        for change in self.environmental_changes:
            change.validate()

        return True

    def add_significant_event(self, event: TimelineEvent) -> bool:
        """Add a significant event to the location's history."""
        try:
            event.validate()
            self.significant_events.append(event)
            self.last_updated = datetime.now()
            return True
        except ValidationError as e:
            logger.error(f"Failed to add significant event: {e}")
            return False

    def add_environmental_change(self, change: LocationChange) -> bool:
        """Add an environmental change to the location's history."""
        try:
            change.validate()
            self.environmental_changes.append(change)
            self.last_updated = datetime.now()
            return True
        except ValidationError as e:
            logger.error(f"Failed to add environmental change: {e}")
            return False

    def get_recent_events(self, days: int = 30) -> list[TimelineEvent]:
        """Get recent events for this location."""
        cutoff_time = datetime.now() - timedelta(days=days)
        all_events = self.founding_events + self.significant_events + self.cultural_evolution
        return [event for event in all_events if event.timestamp >= cutoff_time]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'location_id': self.location_id,
            'founding_events': [event.to_dict() for event in self.founding_events],
            'significant_events': [event.to_dict() for event in self.significant_events],
            'environmental_changes': [change.to_dict() for change in self.environmental_changes],
            'visitor_history': self.visitor_history,
            'cultural_evolution': [event.to_dict() for event in self.cultural_evolution],
            'seasonal_patterns': self.seasonal_patterns,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LocationHistory':
        """Create from dictionary."""
        if 'founding_events' in data:
            data['founding_events'] = [TimelineEvent.from_dict(event_data) for event_data in data['founding_events']]
        if 'significant_events' in data:
            data['significant_events'] = [TimelineEvent.from_dict(event_data) for event_data in data['significant_events']]
        if 'environmental_changes' in data:
            data['environmental_changes'] = [LocationChange.from_dict(change_data) for change_data in data['environmental_changes']]
        if 'cultural_evolution' in data:
            data['cultural_evolution'] = [TimelineEvent.from_dict(event_data) for event_data in data['cultural_evolution']]
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


class LocationEvolutionManager:
    """
    Manages location evolution and environmental changes over time.

    This class extends the existing worldbuilding system to handle dynamic
    location changes, seasonal variations, environmental evolution, and
    location history tracking.
    """

    def __init__(self, worldbuilding_system: WorldbuildingSettingManagement | None = None,
                 timeline_engine: TimelineEngine | None = None):
        """
        Initialize the Location Evolution Manager.

        Args:
            worldbuilding_system: Existing worldbuilding system to extend
            timeline_engine: Timeline engine for event tracking
        """
        self.worldbuilding_system = worldbuilding_system or WorldbuildingSettingManagement()
        self.timeline_engine = timeline_engine or TimelineEngine()

        # Location-specific data
        self.location_histories: dict[str, LocationHistory] = {}
        self.environmental_factors: dict[str, dict[str, EnvironmentalFactor]] = {}  # location_id -> factor_type -> factor
        self.seasonal_schedules: dict[str, list[dict[str, Any]]] = {}  # location_id -> scheduled changes

        # Configuration
        self.seasonal_change_intensity = 0.7  # How much seasons affect locations
        self.environmental_change_rate = 0.1  # Base rate of environmental change
        self.history_retention_days = 365 * 5  # Keep 5 years of history

        logger.info("LocationEvolutionManager initialized")

    def create_location_with_history(self, location_data: dict[str, Any]) -> LocationDetails | None:
        """
        Create a new location with generated history and environmental factors.

        Args:
            location_data: Dictionary containing location information

        Returns:
            Optional[LocationDetails]: Created location or None if failed
        """
        try:
            location_id = location_data.get('location_id', str(uuid.uuid4()))

            # Create the base location using worldbuilding system
            location_details = LocationDetails(
                location_id=location_id,
                name=location_data.get('name', f'Location {location_id}'),
                description=location_data.get('description', ''),
                location_type=LocationType(location_data.get('location_type', 'safe_space')),
                therapeutic_themes=location_data.get('therapeutic_themes', []),
                atmosphere=location_data.get('atmosphere', 'neutral'),
                accessibility_requirements=location_data.get('accessibility_requirements', []),
                connected_locations=location_data.get('connected_locations', {}),
                available_actions=location_data.get('available_actions', []),
                environmental_factors=location_data.get('environmental_factors', {}),
                lore_elements=location_data.get('lore_elements', []),
                unlock_conditions=location_data.get('unlock_conditions', []),
                therapeutic_opportunities=location_data.get('therapeutic_opportunities', []),
                safety_level=location_data.get('safety_level', 1.0),
                immersion_level=location_data.get('immersion_level', 0.5)
            )

            location_details.validate()

            # Create timeline for the location
            self.timeline_engine.create_timeline(location_id, EntityType.LOCATION)

            # Generate location history
            history = self._generate_location_history(location_details)
            self.location_histories[location_id] = history

            # Initialize environmental factors
            self._initialize_environmental_factors(location_id, location_data.get('environmental_factors', {}))

            # Generate founding events
            self._generate_founding_events(location_details, history)

            # Schedule seasonal changes if applicable
            self._schedule_seasonal_changes(location_id)

            logger.info(f"Created location with history: {location_details.name} ({location_id})")
            return location_details

        except Exception as e:
            logger.error(f"Failed to create location with history: {e}")
            return None

    def evolve_location(self, location_id: str, time_delta: timedelta) -> LocationChange | None:
        """
        Evolve a location over a given time period.

        Args:
            location_id: Unique identifier for the location
            time_delta: Amount of time to simulate

        Returns:
            Optional[LocationChange]: The change applied, or None if no change
        """
        try:
            location_details = self.worldbuilding_system.get_location_details(location_id)
            if not location_details:
                logger.error(f"Location not found: {location_id}")
                return None

            # Calculate evolution based on time passed
            evolution_factor = min(time_delta.total_seconds() / (24 * 3600), 1.0)  # Max 1 day worth of change

            # Determine what type of evolution to apply
            change_type = self._determine_evolution_type(location_details, evolution_factor)

            if change_type == "environmental":
                return self._evolve_environmental_factors(location_id, evolution_factor)
            elif change_type == "structural":
                return self._evolve_structural_elements(location_id, evolution_factor)
            elif change_type == "accessibility":
                return self._evolve_accessibility(location_id, evolution_factor)
            elif change_type == "atmosphere":
                return self._evolve_atmosphere(location_id, evolution_factor)

            return None

        except Exception as e:
            logger.error(f"Failed to evolve location {location_id}: {e}")
            return None

    def apply_seasonal_changes(self, location_id: str, season: Season) -> bool:
        """
        Apply seasonal changes to a location.

        Args:
            location_id: Unique identifier for the location
            season: The season to apply

        Returns:
            bool: True if changes were applied successfully
        """
        try:
            location_details = self.worldbuilding_system.get_location_details(location_id)
            if not location_details:
                logger.error(f"Location not found: {location_id}")
                return False

            # Get seasonal patterns for this location
            history = self.location_histories.get(location_id)
            if not history:
                logger.warning(f"No history found for location {location_id}")
                return False

            history.seasonal_patterns.get(season.value, {})

            # Apply environmental changes based on season
            changes_applied = []

            # Weather changes
            weather_change = self._apply_seasonal_weather(location_id, season)
            if weather_change:
                changes_applied.append(weather_change)

            # Lighting changes
            lighting_change = self._apply_seasonal_lighting(location_id, season)
            if lighting_change:
                changes_applied.append(lighting_change)

            # Vegetation changes
            vegetation_change = self._apply_seasonal_vegetation(location_id, season)
            if vegetation_change:
                changes_applied.append(vegetation_change)

            # Wildlife changes
            wildlife_change = self._apply_seasonal_wildlife(location_id, season)
            if wildlife_change:
                changes_applied.append(wildlife_change)

            # Create a timeline event for the seasonal change
            if changes_applied:
                event = TimelineEvent(
                    event_type=EventType.SEASONAL_CHANGE,
                    title=f"Seasonal change to {season.value}",
                    description=f"Location {location_details.name} transitions to {season.value} with various environmental changes",
                    location_id=location_id,
                    timestamp=datetime.now(),
                    significance_level=6,
                    consequences=[f"Applied {len(changes_applied)} seasonal changes"],
                    tags=["seasonal", season.value, "environmental"]
                )

                self.timeline_engine.add_event(location_id, event)

                # Add to location history
                if history:
                    history.add_significant_event(event)
                    for change in changes_applied:
                        history.add_environmental_change(change)

            logger.info(f"Applied {len(changes_applied)} seasonal changes to location {location_id} for {season.value}")
            return len(changes_applied) > 0

        except Exception as e:
            logger.error(f"Failed to apply seasonal changes to location {location_id}: {e}")
            return False

    def handle_location_events(self, location_id: str, events: list[TimelineEvent]) -> bool:
        """
        Handle events that affect a location and update its state accordingly.

        Args:
            location_id: Unique identifier for the location
            events: List of events that affect this location

        Returns:
            bool: True if events were processed successfully
        """
        try:
            location_details = self.worldbuilding_system.get_location_details(location_id)
            if not location_details:
                logger.error(f"Location not found: {location_id}")
                return False

            history = self.location_histories.get(location_id)
            if not history:
                logger.warning(f"No history found for location {location_id}, creating new history")
                history = LocationHistory(location_id=location_id)
                self.location_histories[location_id] = history

            changes_made = []

            for event in events:
                # Process different types of events
                if event.event_type == EventType.PLAYER_INTERACTION:
                    change = self._handle_player_interaction_event(location_id, event)
                    if change:
                        changes_made.append(change)

                elif event.event_type == EventType.ENVIRONMENTAL_CHANGE:
                    change = self._handle_environmental_event(location_id, event)
                    if change:
                        changes_made.append(change)

                elif event.event_type == EventType.CONFLICT:
                    change = self._handle_conflict_event(location_id, event)
                    if change:
                        changes_made.append(change)

                elif event.event_type == EventType.CELEBRATION:
                    change = self._handle_celebration_event(location_id, event)
                    if change:
                        changes_made.append(change)

                elif event.event_type == EventType.DISCOVERY:
                    change = self._handle_discovery_event(location_id, event)
                    if change:
                        changes_made.append(change)

                # Add event to location timeline
                self.timeline_engine.add_event(location_id, event)

                # Add to location history
                if event.significance_level >= 7:
                    history.add_significant_event(event)

                # Track visitors
                for participant in event.participants:
                    if participant not in history.visitor_history:
                        history.visitor_history.append(participant)

            # Apply accumulated changes
            for change in changes_made:
                history.add_environmental_change(change)
                self._apply_location_change(location_id, change)

            logger.info(f"Processed {len(events)} events for location {location_id}, made {len(changes_made)} changes")
            return True

        except Exception as e:
            logger.error(f"Failed to handle location events for {location_id}: {e}")
            return False

    def get_location_history(self, location_id: str) -> LocationHistory | None:
        """
        Get the complete history of a location.

        Args:
            location_id: Unique identifier for the location

        Returns:
            Optional[LocationHistory]: Location history or None if not found
        """
        return self.location_histories.get(location_id)

    def update_location_accessibility(self, location_id: str, conditions: list[str]) -> bool:
        """
        Update the accessibility conditions for a location.

        Args:
            location_id: Unique identifier for the location
            conditions: List of accessibility conditions

        Returns:
            bool: True if update was successful
        """
        try:
            location_details = self.worldbuilding_system.get_location_details(location_id)
            if not location_details:
                logger.error(f"Location not found: {location_id}")
                return False

            old_conditions = location_details.accessibility_requirements.copy()
            location_details.accessibility_requirements = conditions
            location_details.last_modified = datetime.now()

            # Create a change record
            change = LocationChange(
                location_id=location_id,
                change_type="accessibility",
                description="Updated accessibility requirements",
                old_state={'accessibility_requirements': old_conditions},
                new_state={'accessibility_requirements': conditions},
                timestamp=datetime.now(),
                significance_level=6
            )

            # Add to history
            history = self.location_histories.get(location_id)
            if history:
                history.add_environmental_change(change)

            # Create timeline event
            event = TimelineEvent(
                event_type=EventType.ENVIRONMENTAL_CHANGE,
                title="Accessibility requirements updated",
                description=f"Location accessibility requirements changed from {old_conditions} to {conditions}",
                location_id=location_id,
                timestamp=datetime.now(),
                significance_level=6,
                tags=["accessibility", "administrative"]
            )

            self.timeline_engine.add_event(location_id, event)

            logger.info(f"Updated accessibility for location {location_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update location accessibility for {location_id}: {e}")
            return False

    # Private helper methods

    def _generate_location_history(self, location_details: LocationDetails) -> LocationHistory:
        """Generate initial history for a location."""
        history = LocationHistory(location_id=location_details.location_id)

        # Generate founding events based on location type
        if location_details.location_type == LocationType.SAFE_SPACE:
            founding_event = TimelineEvent(
                event_type=EventType.CREATION,
                title=f"Establishment of {location_details.name}",
                description=f"The safe space {location_details.name} was established as a place of refuge and healing",
                location_id=location_details.location_id,
                timestamp=datetime.now() - timedelta(days=365 * 2),  # 2 years ago
                significance_level=8,
                tags=["founding", "safe_space"]
            )
            history.founding_events.append(founding_event)

        elif location_details.location_type == LocationType.CHALLENGE_AREA:
            founding_event = TimelineEvent(
                event_type=EventType.CREATION,
                title=f"Formation of {location_details.name}",
                description=f"The challenge area {location_details.name} was formed to provide growth opportunities",
                location_id=location_details.location_id,
                timestamp=datetime.now() - timedelta(days=365 * 3),  # 3 years ago
                significance_level=7,
                tags=["founding", "challenge"]
            )
            history.founding_events.append(founding_event)

        # Initialize seasonal patterns
        history.seasonal_patterns = {
            Season.SPRING.value: {
                'weather': 'mild and rainy',
                'lighting': 'soft morning light',
                'vegetation': 'new growth and blooming',
                'wildlife': 'active and vocal'
            },
            Season.SUMMER.value: {
                'weather': 'warm and sunny',
                'lighting': 'bright and clear',
                'vegetation': 'lush and full',
                'wildlife': 'abundant and diverse'
            },
            Season.AUTUMN.value: {
                'weather': 'cool and crisp',
                'lighting': 'golden and warm',
                'vegetation': 'changing colors',
                'wildlife': 'preparing for winter'
            },
            Season.WINTER.value: {
                'weather': 'cold and quiet',
                'lighting': 'soft and muted',
                'vegetation': 'dormant and bare',
                'wildlife': 'scarce and hidden'
            }
        }

        return history

    def _initialize_environmental_factors(self, location_id: str, initial_factors: dict[str, Any]) -> None:
        """Initialize environmental factors for a location."""
        self.environmental_factors[location_id] = {}

        # Default environmental factors
        default_factors = {
            EnvironmentalFactorType.WEATHER: "pleasant",
            EnvironmentalFactorType.LIGHTING: "natural daylight",
            EnvironmentalFactorType.TEMPERATURE: "comfortable",
            EnvironmentalFactorType.HUMIDITY: "moderate",
            EnvironmentalFactorType.VEGETATION: "moderate growth",
            EnvironmentalFactorType.WILDLIFE: "occasional presence",
            EnvironmentalFactorType.SOUNDS: "ambient nature sounds",
            EnvironmentalFactorType.ATMOSPHERE: "peaceful"
        }

        # Create environmental factor objects
        for factor_type, default_value in default_factors.items():
            current_value = initial_factors.get(factor_type.value, default_value)

            factor = EnvironmentalFactor(
                factor_type=factor_type,
                current_value=current_value,
                intensity=0.5,
                seasonal_variation=factor_type in [
                    EnvironmentalFactorType.WEATHER,
                    EnvironmentalFactorType.LIGHTING,
                    EnvironmentalFactorType.VEGETATION,
                    EnvironmentalFactorType.WILDLIFE
                ],
                change_rate=0.1
            )

            self.environmental_factors[location_id][factor_type.value] = factor

    def _generate_founding_events(self, location_details: LocationDetails, history: LocationHistory) -> None:
        """Generate founding events and add them to the timeline."""
        for event in history.founding_events:
            self.timeline_engine.add_event(location_details.location_id, event)

    def _schedule_seasonal_changes(self, location_id: str) -> None:
        """Schedule seasonal changes for a location."""
        # This would typically be integrated with a world time system
        # For now, we'll create a simple schedule
        self.seasonal_schedules[location_id] = []

        # Schedule changes for each season (simplified)
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        for i, season in enumerate(seasons):
            # Schedule seasonal change every 3 months
            scheduled_time = datetime.now() + timedelta(days=90 * (i + 1))

            self.seasonal_schedules[location_id].append({
                'season': season.value,
                'scheduled_time': scheduled_time,
                'applied': False
            })

    def _determine_evolution_type(self, location_details: LocationDetails, evolution_factor: float) -> str:
        """Determine what type of evolution to apply based on location and time."""
        # Simple logic - can be made more sophisticated
        if evolution_factor > 0.8:
            return "structural"
        elif evolution_factor > 0.5:
            return "environmental"
        elif evolution_factor > 0.3:
            return "atmosphere"
        else:
            return "accessibility"

    def _evolve_environmental_factors(self, location_id: str, evolution_factor: float) -> LocationChange | None:
        """Evolve environmental factors for a location."""
        factors = self.environmental_factors.get(location_id, {})
        if not factors:
            return None

        # Select a random factor to evolve
        import random
        factor_key = random.choice(list(factors.keys()))
        factor = factors[factor_key]

        old_value = factor.current_value

        # Apply evolution based on factor type
        if factor.factor_type == EnvironmentalFactorType.WEATHER:
            weather_options = ["sunny", "cloudy", "rainy", "misty", "clear", "overcast"]
            factor.current_value = random.choice(weather_options)

        elif factor.factor_type == EnvironmentalFactorType.LIGHTING:
            lighting_options = ["bright", "dim", "filtered", "golden", "soft", "harsh"]
            factor.current_value = random.choice(lighting_options)

        elif factor.factor_type == EnvironmentalFactorType.VEGETATION:
            vegetation_options = ["lush", "sparse", "overgrown", "well-maintained", "wild", "cultivated"]
            factor.current_value = random.choice(vegetation_options)

        factor.last_updated = datetime.now()

        if old_value != factor.current_value:
            return LocationChange(
                location_id=location_id,
                change_type="environmental",
                description=f"{factor.factor_type.value.title()} changed from {old_value} to {factor.current_value}",
                old_state={factor.factor_type.value: old_value},
                new_state={factor.factor_type.value: factor.current_value},
                timestamp=datetime.now(),
                significance_level=4
            )

        return None

    def _evolve_structural_elements(self, location_id: str, evolution_factor: float) -> LocationChange | None:
        """Evolve structural elements of a location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Example: Add new available actions
        new_actions = ["explore hidden area", "examine ancient markings", "discover secret passage"]
        import random
        new_action = random.choice(new_actions)

        if new_action not in location_details.available_actions:
            old_actions = location_details.available_actions.copy()
            location_details.available_actions.append(new_action)
            location_details.last_modified = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="structural",
                description=f"New action available: {new_action}",
                old_state={'available_actions': old_actions},
                new_state={'available_actions': location_details.available_actions},
                timestamp=datetime.now(),
                significance_level=6
            )

        return None

    def _evolve_accessibility(self, location_id: str, evolution_factor: float) -> LocationChange | None:
        """Evolve accessibility conditions for a location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Example: Remove an unlock condition
        if location_details.unlock_conditions:
            import random
            removed_condition = random.choice(location_details.unlock_conditions)
            old_conditions = location_details.unlock_conditions.copy()
            location_details.unlock_conditions.remove(removed_condition)
            location_details.last_modified = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="accessibility",
                description=f"Unlock condition removed: {removed_condition}",
                old_state={'unlock_conditions': old_conditions},
                new_state={'unlock_conditions': location_details.unlock_conditions},
                timestamp=datetime.now(),
                significance_level=7
            )

        return None

    def _evolve_atmosphere(self, location_id: str, evolution_factor: float) -> LocationChange | None:
        """Evolve the atmosphere of a location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        atmosphere_options = ["peaceful", "mysterious", "welcoming", "tense", "inspiring", "contemplative"]
        import random
        new_atmosphere = random.choice(atmosphere_options)

        if new_atmosphere != location_details.atmosphere:
            old_atmosphere = location_details.atmosphere
            location_details.atmosphere = new_atmosphere
            location_details.last_modified = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="atmosphere",
                description=f"Atmosphere changed from {old_atmosphere} to {new_atmosphere}",
                old_state={'atmosphere': old_atmosphere},
                new_state={'atmosphere': new_atmosphere},
                timestamp=datetime.now(),
                significance_level=5
            )

        return None

    def _apply_seasonal_weather(self, location_id: str, season: Season) -> LocationChange | None:
        """Apply seasonal weather changes."""
        factors = self.environmental_factors.get(location_id, {})
        weather_factor = factors.get(EnvironmentalFactorType.WEATHER.value)

        if not weather_factor or not weather_factor.seasonal_variation:
            return None

        seasonal_weather = {
            Season.SPRING: "mild and rainy",
            Season.SUMMER: "warm and sunny",
            Season.AUTUMN: "cool and crisp",
            Season.WINTER: "cold and quiet"
        }

        old_weather = weather_factor.current_value
        new_weather = seasonal_weather[season]

        if old_weather != new_weather:
            weather_factor.current_value = new_weather
            weather_factor.last_updated = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="environmental",
                description=f"Seasonal weather change: {old_weather} to {new_weather}",
                old_state={'weather': old_weather},
                new_state={'weather': new_weather},
                trigger_event=f"seasonal_change_{season.value}",
                timestamp=datetime.now(),
                significance_level=5
            )

        return None

    def _apply_seasonal_lighting(self, location_id: str, season: Season) -> LocationChange | None:
        """Apply seasonal lighting changes."""
        factors = self.environmental_factors.get(location_id, {})
        lighting_factor = factors.get(EnvironmentalFactorType.LIGHTING.value)

        if not lighting_factor or not lighting_factor.seasonal_variation:
            return None

        seasonal_lighting = {
            Season.SPRING: "soft morning light",
            Season.SUMMER: "bright and clear",
            Season.AUTUMN: "golden and warm",
            Season.WINTER: "soft and muted"
        }

        old_lighting = lighting_factor.current_value
        new_lighting = seasonal_lighting[season]

        if old_lighting != new_lighting:
            lighting_factor.current_value = new_lighting
            lighting_factor.last_updated = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="environmental",
                description=f"Seasonal lighting change: {old_lighting} to {new_lighting}",
                old_state={'lighting': old_lighting},
                new_state={'lighting': new_lighting},
                trigger_event=f"seasonal_change_{season.value}",
                timestamp=datetime.now(),
                significance_level=4
            )

        return None

    def _apply_seasonal_vegetation(self, location_id: str, season: Season) -> LocationChange | None:
        """Apply seasonal vegetation changes."""
        factors = self.environmental_factors.get(location_id, {})
        vegetation_factor = factors.get(EnvironmentalFactorType.VEGETATION.value)

        if not vegetation_factor or not vegetation_factor.seasonal_variation:
            return None

        seasonal_vegetation = {
            Season.SPRING: "new growth and blooming",
            Season.SUMMER: "lush and full",
            Season.AUTUMN: "changing colors",
            Season.WINTER: "dormant and bare"
        }

        old_vegetation = vegetation_factor.current_value
        new_vegetation = seasonal_vegetation[season]

        if old_vegetation != new_vegetation:
            vegetation_factor.current_value = new_vegetation
            vegetation_factor.last_updated = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="environmental",
                description=f"Seasonal vegetation change: {old_vegetation} to {new_vegetation}",
                old_state={'vegetation': old_vegetation},
                new_state={'vegetation': new_vegetation},
                trigger_event=f"seasonal_change_{season.value}",
                timestamp=datetime.now(),
                significance_level=5
            )

        return None

    def _apply_seasonal_wildlife(self, location_id: str, season: Season) -> LocationChange | None:
        """Apply seasonal wildlife changes."""
        factors = self.environmental_factors.get(location_id, {})
        wildlife_factor = factors.get(EnvironmentalFactorType.WILDLIFE.value)

        if not wildlife_factor or not wildlife_factor.seasonal_variation:
            return None

        seasonal_wildlife = {
            Season.SPRING: "active and vocal",
            Season.SUMMER: "abundant and diverse",
            Season.AUTUMN: "preparing for winter",
            Season.WINTER: "scarce and hidden"
        }

        old_wildlife = wildlife_factor.current_value
        new_wildlife = seasonal_wildlife[season]

        if old_wildlife != new_wildlife:
            wildlife_factor.current_value = new_wildlife
            wildlife_factor.last_updated = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="environmental",
                description=f"Seasonal wildlife change: {old_wildlife} to {new_wildlife}",
                old_state={'wildlife': old_wildlife},
                new_state={'wildlife': new_wildlife},
                trigger_event=f"seasonal_change_{season.value}",
                timestamp=datetime.now(),
                significance_level=4
            )

        return None

    def _handle_player_interaction_event(self, location_id: str, event: TimelineEvent) -> LocationChange | None:
        """Handle player interaction events that affect the location."""
        # Example: Player interactions can make locations more welcoming
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Increase safety level slightly with positive interactions
        if event.emotional_impact > 0.5:
            old_safety = location_details.safety_level
            new_safety = min(1.0, location_details.safety_level + 0.05)

            if new_safety != old_safety:
                location_details.safety_level = new_safety
                location_details.last_modified = datetime.now()

                return LocationChange(
                    location_id=location_id,
                    change_type="environmental",
                    description="Location became safer due to positive player interaction",
                    old_state={'safety_level': old_safety},
                    new_state={'safety_level': new_safety},
                    trigger_event=event.event_id,
                    timestamp=datetime.now(),
                    significance_level=3
                )

        return None

    def _handle_environmental_event(self, location_id: str, event: TimelineEvent) -> LocationChange | None:
        """Handle environmental events that affect the location."""
        # Environmental events directly change environmental factors
        factors = self.environmental_factors.get(location_id, {})

        # Example: Storm event affects weather and lighting
        if "storm" in event.description.lower():
            weather_factor = factors.get(EnvironmentalFactorType.WEATHER.value)
            if weather_factor:
                old_weather = weather_factor.current_value
                weather_factor.current_value = "stormy and turbulent"
                weather_factor.last_updated = datetime.now()

                return LocationChange(
                    location_id=location_id,
                    change_type="environmental",
                    description="Storm changed weather conditions",
                    old_state={'weather': old_weather},
                    new_state={'weather': weather_factor.current_value},
                    trigger_event=event.event_id,
                    timestamp=datetime.now(),
                    significance_level=6
                )

        return None

    def _handle_conflict_event(self, location_id: str, event: TimelineEvent) -> LocationChange | None:
        """Handle conflict events that affect the location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Conflicts can reduce safety level and change atmosphere
        old_safety = location_details.safety_level
        old_atmosphere = location_details.atmosphere

        new_safety = max(0.0, location_details.safety_level - 0.1)
        new_atmosphere = "tense"

        location_details.safety_level = new_safety
        location_details.atmosphere = new_atmosphere
        location_details.last_modified = datetime.now()

        return LocationChange(
            location_id=location_id,
            change_type="environmental",
            description="Conflict reduced safety and created tense atmosphere",
            old_state={'safety_level': old_safety, 'atmosphere': old_atmosphere},
            new_state={'safety_level': new_safety, 'atmosphere': new_atmosphere},
            trigger_event=event.event_id,
            timestamp=datetime.now(),
            significance_level=7
        )

    def _handle_celebration_event(self, location_id: str, event: TimelineEvent) -> LocationChange | None:
        """Handle celebration events that affect the location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Celebrations can improve atmosphere and add lore
        old_atmosphere = location_details.atmosphere
        new_atmosphere = "joyful"

        location_details.atmosphere = new_atmosphere
        location_details.lore_elements.append(f"Site of celebration: {event.title}")
        location_details.last_modified = datetime.now()

        return LocationChange(
            location_id=location_id,
            change_type="environmental",
            description="Celebration created joyful atmosphere and added to location lore",
            old_state={'atmosphere': old_atmosphere},
            new_state={'atmosphere': new_atmosphere},
            trigger_event=event.event_id,
            timestamp=datetime.now(),
            significance_level=6
        )

    def _handle_discovery_event(self, location_id: str, event: TimelineEvent) -> LocationChange | None:
        """Handle discovery events that affect the location."""
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            return None

        # Discoveries can add new actions and lore
        old_actions = location_details.available_actions.copy()
        new_action = f"investigate {event.title.lower()}"

        if new_action not in location_details.available_actions:
            location_details.available_actions.append(new_action)
            location_details.lore_elements.append(f"Discovery: {event.description}")
            location_details.last_modified = datetime.now()

            return LocationChange(
                location_id=location_id,
                change_type="structural",
                description="Discovery added new investigation opportunity",
                old_state={'available_actions': old_actions},
                new_state={'available_actions': location_details.available_actions},
                trigger_event=event.event_id,
                timestamp=datetime.now(),
                significance_level=8
            )

        return None

    def _apply_location_change(self, location_id: str, change: LocationChange) -> bool:
        """Apply a location change to the worldbuilding system."""
        try:
            # Create a world change for the worldbuilding system
            world_change = WorldChange(
                change_type=WorldChangeType.LOCATION_MODIFY,
                target_location_id=location_id,
                description=change.description,
                changes=change.new_state,
                reversible=change.reversible,
                timestamp=change.timestamp
            )

            # Apply the change through the worldbuilding system
            return self.worldbuilding_system.update_world_state([world_change])

        except Exception as e:
            logger.error(f"Failed to apply location change: {e}")
            return False

    def get_environmental_factors(self, location_id: str) -> dict[str, EnvironmentalFactor]:
        """Get all environmental factors for a location."""
        return self.environmental_factors.get(location_id, {})

    def get_seasonal_schedule(self, location_id: str) -> list[dict[str, Any]]:
        """Get the seasonal change schedule for a location."""
        return self.seasonal_schedules.get(location_id, [])

    def validate_location_evolution_consistency(self, location_id: str) -> tuple[bool, list[str]]:
        """Validate the consistency of location evolution data."""
        issues = []

        # Check if location exists
        location_details = self.worldbuilding_system.get_location_details(location_id)
        if not location_details:
            issues.append(f"Location {location_id} not found")
            return False, issues

        # Check history consistency
        history = self.location_histories.get(location_id)
        if history:
            try:
                history.validate()
            except ValidationError as e:
                issues.append(f"History validation failed: {e}")

        # Check environmental factors
        factors = self.environmental_factors.get(location_id, {})
        for factor_type, factor in factors.items():
            try:
                factor.validate()
            except ValidationError as e:
                issues.append(f"Environmental factor {factor_type} validation failed: {e}")

        # Check timeline consistency
        timeline_consistent, timeline_issues = self.timeline_engine.validate_timeline_consistency(location_id)
        if not timeline_consistent:
            issues.extend(timeline_issues)

        return len(issues) == 0, issues
