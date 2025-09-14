"""
Worldbuilding and Setting Management for TTA Prototype

This module provides comprehensive worldbuilding and setting management capabilities
for the therapeutic text adventure system, including world state tracking, consistency
validation, location management, and setting description generation.

Classes:
    LocationDetails: Represents detailed information about a location
    WorldChange: Represents a change to the world state
    ValidationResult: Results of world consistency validation
    WorldbuildingSettingManagement: Main class for world state management
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from neo4j import Driver
except ImportError:
    Driver = None

try:
    from ..models.data_models import NarrativeContext, ValidationError
except ImportError:
    # Fallback for direct execution
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from models.data_models import NarrativeContext, ValidationError

logger = logging.getLogger(__name__)


class LocationType(Enum):
    """Types of locations in the therapeutic world."""
    SAFE_SPACE = "safe_space"
    CHALLENGE_AREA = "challenge_area"
    THERAPEUTIC_ENVIRONMENT = "therapeutic_environment"
    SOCIAL_SPACE = "social_space"
    EXPLORATION_ZONE = "exploration_zone"
    TRANSITION_AREA = "transition_area"


class WorldChangeType(Enum):
    """Types of world state changes."""
    LOCATION_UNLOCK = "location_unlock"
    LOCATION_MODIFY = "location_modify"
    ENVIRONMENT_SHIFT = "environment_shift"
    LORE_UPDATE = "lore_update"
    ACCESS_CHANGE = "access_change"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LocationDetails:
    """Represents detailed information about a location."""
    location_id: str
    name: str
    description: str = ""
    location_type: LocationType = LocationType.SAFE_SPACE
    therapeutic_themes: list[str] = field(default_factory=list)
    atmosphere: str = "neutral"
    accessibility_requirements: list[str] = field(default_factory=list)
    connected_locations: dict[str, str] = field(default_factory=dict)  # direction -> location_id
    available_actions: list[str] = field(default_factory=list)
    environmental_factors: dict[str, Any] = field(default_factory=dict)
    lore_elements: list[str] = field(default_factory=list)
    unlock_conditions: list[str] = field(default_factory=list)
    therapeutic_opportunities: list[str] = field(default_factory=list)
    safety_level: float = 1.0  # 0.0 to 1.0, higher is safer
    immersion_level: float = 0.5  # 0.0 to 1.0, higher is more immersive
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate location details."""
        if not self.location_id.strip():
            raise ValidationError("Location ID cannot be empty")
        if not self.name.strip():
            raise ValidationError("Location name cannot be empty")
        if not 0.0 <= self.safety_level <= 1.0:
            raise ValidationError("Safety level must be between 0.0 and 1.0")
        if not 0.0 <= self.immersion_level <= 1.0:
            raise ValidationError("Immersion level must be between 0.0 and 1.0")
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['location_type'] = self.location_type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_modified'] = self.last_modified.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LocationDetails':
        """Create from dictionary."""
        # Convert datetime strings
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('last_modified'), str):
            data['last_modified'] = datetime.fromisoformat(data['last_modified'])

        # Convert enum
        if isinstance(data.get('location_type'), str):
            data['location_type'] = LocationType(data['location_type'])

        return cls(**data)


@dataclass
class WorldChange:
    """Represents a change to the world state."""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    change_type: WorldChangeType = WorldChangeType.LOCATION_MODIFY
    target_location_id: str = ""
    description: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    prerequisites: list[str] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    reversible: bool = True
    therapeutic_impact: str = ""
    narrative_justification: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False

    def validate(self) -> bool:
        """Validate world change data."""
        if not self.target_location_id.strip():
            raise ValidationError("Target location ID cannot be empty")
        if not self.description.strip():
            raise ValidationError("Change description cannot be empty")
        return True


@dataclass
class ValidationIssue:
    """Represents a validation issue found in the world state."""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: ValidationSeverity = ValidationSeverity.WARNING
    category: str = ""
    description: str = ""
    location_id: str | None = None
    suggested_fix: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Results of world consistency validation."""
    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings_count: int = 0
    errors_count: int = 0
    critical_count: int = 0
    validation_timestamp: datetime = field(default_factory=datetime.now)

    def add_issue(self, severity: ValidationSeverity, category: str, description: str,
                  location_id: str | None = None, suggested_fix: str = "") -> None:
        """Add a validation issue."""
        issue = ValidationIssue(
            severity=severity,
            category=category,
            description=description,
            location_id=location_id,
            suggested_fix=suggested_fix
        )
        self.issues.append(issue)

        # Update counts
        if severity == ValidationSeverity.WARNING:
            self.warnings_count += 1
        elif severity == ValidationSeverity.ERROR:
            self.errors_count += 1
            self.is_valid = False
        elif severity == ValidationSeverity.CRITICAL:
            self.critical_count += 1
            self.is_valid = False


class WorldbuildingSettingManagement:
    """
    Main class for worldbuilding and setting management in the therapeutic text adventure.

    This class provides comprehensive world state tracking, consistency validation,
    location management, and setting description generation capabilities.
    """

    def __init__(self, neo4j_driver: Driver | None = None, redis_client: Any | None = None):
        """
        Initialize worldbuilding and setting management.

        Args:
            neo4j_driver: Neo4j driver for persistent storage
            redis_client: Redis client for caching
        """
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client
        self.locations_cache: dict[str, LocationDetails] = {}
        self.world_state_flags: dict[str, Any] = {}
        self.lore_database: dict[str, list[str]] = {}
        self.consistency_rules: list[dict[str, Any]] = []

        # Initialize default consistency rules
        self._initialize_consistency_rules()

        logger.info("WorldbuildingSettingManagement initialized")

    def _initialize_consistency_rules(self) -> None:
        """Initialize default world consistency rules."""
        self.consistency_rules = [
            {
                "rule_id": "location_connectivity",
                "description": "All locations must have valid connections",
                "check_function": self._check_location_connectivity
            },
            {
                "rule_id": "therapeutic_coherence",
                "description": "Therapeutic themes must be consistent across connected areas",
                "check_function": self._check_therapeutic_coherence
            },
            {
                "rule_id": "safety_progression",
                "description": "Safety levels should progress logically",
                "check_function": self._check_safety_progression
            },
            {
                "rule_id": "lore_consistency",
                "description": "Lore elements must not contradict each other",
                "check_function": self._check_lore_consistency
            },
            {
                "rule_id": "unlock_dependencies",
                "description": "Location unlock conditions must be satisfiable",
                "check_function": self._check_unlock_dependencies
            }
        ]

    def get_location_details(self, location_id: str) -> LocationDetails | None:
        """
        Get detailed information about a location.

        Args:
            location_id: Unique location identifier

        Returns:
            Optional[LocationDetails]: Location details or None if not found
        """
        # Check cache first
        if location_id in self.locations_cache:
            return self.locations_cache[location_id]

        # Try Redis cache
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(f"location:{location_id}")
                if cached_data:
                    location_data = json.loads(cached_data)
                    location = LocationDetails.from_dict(location_data)
                    self.locations_cache[location_id] = location
                    return location
            except Exception as e:
                logger.warning(f"Failed to get location from Redis cache: {e}")

        # Try Neo4j database
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (l:Location {location_id: $location_id})
                    RETURN l
                    """
                    result = session.run(query, location_id=location_id)
                    record = result.single()

                    if record:
                        location_data = dict(record["l"])
                        location = LocationDetails.from_dict(location_data)

                        # Cache the result
                        self.locations_cache[location_id] = location
                        if self.redis_client:
                            self.redis_client.setex(
                                f"location:{location_id}",
                                3600,  # 1 hour TTL
                                json.dumps(location.to_dict())
                            )

                        return location
            except Exception as e:
                logger.error(f"Failed to get location from Neo4j: {e}")

        logger.warning(f"Location not found: {location_id}")
        return None

    def update_world_state(self, world_changes: list[WorldChange]) -> bool:
        """
        Update the world state with a list of changes.

        Args:
            world_changes: List of world changes to apply

        Returns:
            bool: True if all changes were applied successfully
        """
        logger.info(f"Applying {len(world_changes)} world state changes")

        # Validate all changes first
        for change in world_changes:
            try:
                change.validate()
            except ValidationError as e:
                logger.error(f"Invalid world change {change.change_id}: {e}")
                return False

        # Check prerequisites
        for change in world_changes:
            if not self._check_change_prerequisites(change):
                logger.error(f"Prerequisites not met for change {change.change_id}")
                return False

        # Apply changes
        applied_changes = []
        try:
            for change in world_changes:
                if self._apply_world_change(change):
                    applied_changes.append(change)
                    change.applied = True
                else:
                    logger.error(f"Failed to apply change {change.change_id}")
                    # Rollback applied changes
                    self._rollback_changes(applied_changes)
                    return False

            logger.info(f"Successfully applied {len(applied_changes)} world state changes")
            return True

        except Exception as e:
            logger.error(f"Error applying world changes: {e}")
            # Rollback applied changes
            self._rollback_changes(applied_changes)
            return False

    def _check_change_prerequisites(self, change: WorldChange) -> bool:
        """Check if prerequisites for a world change are met."""
        for prerequisite in change.prerequisites:
            if not self._evaluate_prerequisite(prerequisite):
                logger.debug(f"Prerequisite not met: {prerequisite}")
                return False
        return True

    def _evaluate_prerequisite(self, prerequisite: str) -> bool:
        """Evaluate a single prerequisite condition."""
        # Simple prerequisite evaluation - can be extended
        if prerequisite.startswith("flag:"):
            flag_name = prerequisite[5:]
            return self.world_state_flags.get(flag_name, False)
        elif prerequisite.startswith("location_exists:"):
            location_id = prerequisite[16:]
            return self.get_location_details(location_id) is not None
        elif prerequisite.startswith("location_unlocked:"):
            location_id = prerequisite[18:]
            location = self.get_location_details(location_id)
            return location is not None and len(location.unlock_conditions) == 0

        # Default: assume prerequisite is met
        return True

    def _apply_world_change(self, change: WorldChange) -> bool:
        """Apply a single world change."""
        try:
            if change.change_type == WorldChangeType.LOCATION_UNLOCK:
                return self._unlock_location(change.target_location_id, change.changes)
            elif change.change_type == WorldChangeType.LOCATION_MODIFY:
                return self._modify_location(change.target_location_id, change.changes)
            elif change.change_type == WorldChangeType.ENVIRONMENT_SHIFT:
                return self._shift_environment(change.target_location_id, change.changes)
            elif change.change_type == WorldChangeType.LORE_UPDATE:
                return self._update_lore(change.target_location_id, change.changes)
            elif change.change_type == WorldChangeType.ACCESS_CHANGE:
                return self._change_access(change.target_location_id, change.changes)
            else:
                logger.error(f"Unknown change type: {change.change_type}")
                return False
        except Exception as e:
            logger.error(f"Error applying world change: {e}")
            return False

    def _unlock_location(self, location_id: str, changes: dict[str, Any]) -> bool:
        """Unlock a location by removing unlock conditions."""
        location = self.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot unlock non-existent location: {location_id}")
            return False

        # Clear unlock conditions
        location.unlock_conditions = []
        location.last_modified = datetime.now()

        # Update cache and database
        return self._save_location(location)

    def _modify_location(self, location_id: str, changes: dict[str, Any]) -> bool:
        """Modify location properties."""
        location = self.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot modify non-existent location: {location_id}")
            return False

        # Apply changes
        for key, value in changes.items():
            if hasattr(location, key):
                setattr(location, key, value)

        location.last_modified = datetime.now()

        # Update cache and database
        return self._save_location(location)

    def _shift_environment(self, location_id: str, changes: dict[str, Any]) -> bool:
        """Shift environmental factors of a location."""
        location = self.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot shift environment of non-existent location: {location_id}")
            return False

        # Update environmental factors
        location.environmental_factors.update(changes.get('environmental_factors', {}))
        location.atmosphere = changes.get('atmosphere', location.atmosphere)
        location.last_modified = datetime.now()

        # Update cache and database
        return self._save_location(location)

    def _update_lore(self, location_id: str, changes: dict[str, Any]) -> bool:
        """Update lore elements for a location."""
        location = self.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot update lore of non-existent location: {location_id}")
            return False

        # Add new lore elements
        new_lore = changes.get('lore_elements', [])
        location.lore_elements.extend(new_lore)
        location.last_modified = datetime.now()

        # Update global lore database
        if location_id not in self.lore_database:
            self.lore_database[location_id] = []
        self.lore_database[location_id].extend(new_lore)

        # Update cache and database
        return self._save_location(location)

    def _change_access(self, location_id: str, changes: dict[str, Any]) -> bool:
        """Change access conditions for a location."""
        location = self.get_location_details(location_id)
        if not location:
            logger.error(f"Cannot change access of non-existent location: {location_id}")
            return False

        # Update accessibility requirements
        new_requirements = changes.get('accessibility_requirements', [])
        location.accessibility_requirements = new_requirements
        location.last_modified = datetime.now()

        # Update cache and database
        return self._save_location(location)

    def _save_location(self, location: LocationDetails) -> bool:
        """Save location to cache and database."""
        try:
            # Update cache
            self.locations_cache[location.location_id] = location

            # Update Redis cache
            if self.redis_client:
                self.redis_client.setex(
                    f"location:{location.location_id}",
                    3600,  # 1 hour TTL
                    json.dumps(location.to_dict())
                )

            # Update Neo4j database
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MERGE (l:Location {location_id: $location_id})
                    SET l += $properties
                    """
                    session.run(query,
                               location_id=location.location_id,
                               properties=location.to_dict())

            return True

        except Exception as e:
            logger.error(f"Failed to save location {location.location_id}: {e}")
            return False

    def _rollback_changes(self, applied_changes: list[WorldChange]) -> None:
        """Rollback applied world changes."""
        logger.warning(f"Rolling back {len(applied_changes)} world changes")

        for change in reversed(applied_changes):
            if change.reversible:
                try:
                    self._reverse_world_change(change)
                except Exception as e:
                    logger.error(f"Failed to rollback change {change.change_id}: {e}")
            else:
                logger.warning(f"Cannot rollback irreversible change {change.change_id}")

    def _reverse_world_change(self, change: WorldChange) -> bool:
        """Reverse a single world change."""
        # Implementation depends on change type
        # For now, we'll implement basic reversal logic
        if change.change_type == WorldChangeType.LOCATION_MODIFY:
            # This would require storing original values
            logger.warning(f"Cannot reverse location modification {change.change_id} without original values")
            return False

        # Other change types would have specific reversal logic
        return True

    def generate_setting_description(self, location_id: str, context: NarrativeContext) -> str:
        """
        Generate a rich setting description for a location.

        Args:
            location_id: Location identifier
            context: Current narrative context

        Returns:
            str: Generated setting description
        """
        location = self.get_location_details(location_id)
        if not location:
            return f"You find yourself in an unknown place (location: {location_id})."

        # Base description
        description_parts = [location.description]

        # Add atmospheric details
        if location.atmosphere != "neutral":
            atmosphere_descriptions = {
                "peaceful": "A sense of calm pervades the area.",
                "tense": "There's an underlying tension in the air.",
                "mysterious": "An air of mystery surrounds this place.",
                "welcoming": "The environment feels warm and inviting.",
                "challenging": "This place seems to present opportunities for growth."
            }
            if location.atmosphere in atmosphere_descriptions:
                description_parts.append(atmosphere_descriptions[location.atmosphere])

        # Add environmental factors
        if location.environmental_factors:
            for factor, value in location.environmental_factors.items():
                if factor == "lighting" and value:
                    description_parts.append(f"The area is {value}.")
                elif factor == "weather" and value:
                    description_parts.append(f"The weather is {value}.")
                elif factor == "sounds" and value:
                    description_parts.append(f"You can hear {value}.")

        # Add therapeutic context if relevant
        if location.therapeutic_themes and context.therapeutic_opportunities:
            theme_descriptions = {
                "mindfulness": "This seems like a perfect place for quiet reflection.",
                "courage": "Something about this place encourages facing challenges.",
                "connection": "The space feels designed for meaningful interactions.",
                "growth": "There's a sense of potential and possibility here."
            }
            for theme in location.therapeutic_themes:
                if theme in theme_descriptions:
                    description_parts.append(theme_descriptions[theme])

        # Add available actions context
        if location.available_actions:
            action_count = len(location.available_actions)
            if action_count > 3:
                description_parts.append("There are many things you could do here.")
            elif action_count > 1:
                description_parts.append("Several options are available to you.")

        return " ".join(description_parts)

    def validate_world_consistency(self, proposed_changes: list[WorldChange] = None) -> ValidationResult:
        """
        Validate world consistency and identify potential issues.

        Args:
            proposed_changes: Optional list of proposed changes to validate

        Returns:
            ValidationResult: Validation results with any issues found
        """
        logger.info("Validating world consistency")
        result = ValidationResult()

        # Run all consistency rules
        for rule in self.consistency_rules:
            try:
                rule_issues = rule["check_function"](proposed_changes)
                result.issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Error running consistency rule {rule['rule_id']}: {e}")
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "rule_execution",
                    f"Failed to execute consistency rule: {rule['rule_id']}",
                    suggested_fix="Check rule implementation"
                )

        # Update counts
        for issue in result.issues:
            if issue.severity == ValidationSeverity.WARNING:
                result.warnings_count += 1
            elif issue.severity == ValidationSeverity.ERROR:
                result.errors_count += 1
                result.is_valid = False
            elif issue.severity == ValidationSeverity.CRITICAL:
                result.critical_count += 1
                result.is_valid = False

        logger.info(f"World consistency validation completed: "
                   f"{result.warnings_count} warnings, "
                   f"{result.errors_count} errors, "
                   f"{result.critical_count} critical issues")

        return result

    def _check_location_connectivity(self, proposed_changes: list[WorldChange] = None) -> list[ValidationIssue]:
        """Check that all locations have valid connections."""
        issues = []

        # Get all locations
        all_locations = list(self.locations_cache.values())

        # Add locations from database if not in cache
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    query = "MATCH (l:Location) RETURN l.location_id as location_id"
                    result = session.run(query)
                    for record in result:
                        location_id = record["location_id"]
                        if location_id not in self.locations_cache:
                            location = self.get_location_details(location_id)
                            if location:
                                all_locations.append(location)
            except Exception as e:
                logger.warning(f"Could not check database locations: {e}")

        # Check connectivity
        for location in all_locations:
            # Check if location has connections
            if not location.connected_locations:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="connectivity",
                    description=f"Location '{location.name}' has no connections",
                    location_id=location.location_id,
                    suggested_fix="Add connections to other locations"
                ))

            # Check if connected locations exist
            for _direction, connected_id in location.connected_locations.items():
                connected_location = self.get_location_details(connected_id)
                if not connected_location:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="connectivity",
                        description=f"Location '{location.name}' connects to non-existent location '{connected_id}'",
                        location_id=location.location_id,
                        suggested_fix=f"Create location '{connected_id}' or remove connection"
                    ))

        return issues

    def _check_therapeutic_coherence(self, proposed_changes: list[WorldChange] = None) -> list[ValidationIssue]:
        """Check therapeutic theme consistency across connected areas."""
        issues = []

        # This is a simplified check - in practice, you'd have more sophisticated rules
        for location in self.locations_cache.values():
            if location.therapeutic_themes:
                for _direction, connected_id in location.connected_locations.items():
                    connected_location = self.get_location_details(connected_id)
                    if connected_location and connected_location.therapeutic_themes:
                        # Check for conflicting themes
                        conflicting_themes = {
                            "relaxation": ["high_stress", "intense_challenge"],
                            "safety": ["danger", "risk_taking"],
                            "social": ["isolation", "solitude"]
                        }

                        for theme in location.therapeutic_themes:
                            if theme in conflicting_themes:
                                for connected_theme in connected_location.therapeutic_themes:
                                    if connected_theme in conflicting_themes[theme]:
                                        issues.append(ValidationIssue(
                                            severity=ValidationSeverity.WARNING,
                                            category="therapeutic_coherence",
                                            description=f"Conflicting therapeutic themes: '{theme}' in '{location.name}' conflicts with '{connected_theme}' in '{connected_location.name}'",
                                            location_id=location.location_id,
                                            suggested_fix="Consider adding transition area or adjusting themes"
                                        ))

        return issues

    def _check_safety_progression(self, proposed_changes: list[WorldChange] = None) -> list[ValidationIssue]:
        """Check that safety levels progress logically."""
        issues = []

        for location in self.locations_cache.values():
            for _direction, connected_id in location.connected_locations.items():
                connected_location = self.get_location_details(connected_id)
                if connected_location:
                    safety_diff = abs(location.safety_level - connected_location.safety_level)
                    if safety_diff > 0.5:  # Large safety level jump
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="safety_progression",
                            description=f"Large safety level difference between '{location.name}' ({location.safety_level}) and '{connected_location.name}' ({connected_location.safety_level})",
                            location_id=location.location_id,
                            suggested_fix="Consider adding intermediate location or adjusting safety levels"
                        ))

        return issues

    def _check_lore_consistency(self, proposed_changes: list[WorldChange] = None) -> list[ValidationIssue]:
        """Check for contradictions in lore elements."""
        issues = []

        # Collect all lore elements
        all_lore = []
        for location in self.locations_cache.values():
            for lore_element in location.lore_elements:
                all_lore.append((location.location_id, lore_element))

        # Simple contradiction detection (can be enhanced with NLP)
        contradiction_keywords = [
            ("always", "never"),
            ("impossible", "possible"),
            ("forbidden", "allowed"),
            ("ancient", "new"),
            ("destroyed", "intact")
        ]

        for i, (loc1, lore1) in enumerate(all_lore):
            for _j, (loc2, lore2) in enumerate(all_lore[i+1:], i+1):
                for keyword1, keyword2 in contradiction_keywords:
                    if keyword1 in lore1.lower() and keyword2 in lore2.lower():
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="lore_consistency",
                            description=f"Potential lore contradiction between locations '{loc1}' and '{loc2}'",
                            location_id=loc1,
                            suggested_fix="Review lore elements for consistency"
                        ))

        return issues

    def _check_unlock_dependencies(self, proposed_changes: list[WorldChange] = None) -> list[ValidationIssue]:
        """Check that location unlock conditions are satisfiable."""
        issues = []

        for location in self.locations_cache.values():
            for condition in location.unlock_conditions:
                if not self._is_condition_satisfiable(condition):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="unlock_dependencies",
                        description=f"Unsatisfiable unlock condition in '{location.name}': {condition}",
                        location_id=location.location_id,
                        suggested_fix="Review and fix unlock condition"
                    ))

        return issues

    def _is_condition_satisfiable(self, condition: str) -> bool:
        """Check if an unlock condition can be satisfied."""
        # Simple condition checking - can be enhanced
        if condition.startswith("flag:"):
            return True  # Flags can be set
        elif condition.startswith("location_visited:"):
            location_id = condition[17:]
            return self.get_location_details(location_id) is not None
        elif condition.startswith("therapeutic_goal:"):
            return True  # Goals can be achieved

        # Default: assume condition is satisfiable
        return True


# Utility functions
def create_sample_location(location_id: str, name: str, location_type: LocationType = LocationType.SAFE_SPACE) -> LocationDetails:
    """Create a sample location for testing."""
    return LocationDetails(
        location_id=location_id,
        name=name,
        description=f"A {location_type.value.replace('_', ' ')} called {name}.",
        location_type=location_type,
        therapeutic_themes=["mindfulness", "safety"],
        atmosphere="peaceful",
        safety_level=0.8,
        immersion_level=0.6
    )


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)

    # Create worldbuilding manager
    world_manager = WorldbuildingSettingManagement()

    # Create sample locations
    garden = create_sample_location("peaceful_garden", "Peaceful Garden", LocationType.THERAPEUTIC_ENVIRONMENT)
    library = create_sample_location("quiet_library", "Quiet Library", LocationType.SAFE_SPACE)

    # Add connections
    garden.connected_locations = {"north": "quiet_library"}
    library.connected_locations = {"south": "peaceful_garden"}

    # Cache locations
    world_manager.locations_cache[garden.location_id] = garden
    world_manager.locations_cache[library.location_id] = library

    # Test validation
    validation_result = world_manager.validate_world_consistency()
    print(f"Validation result: {validation_result.is_valid}")
    print(f"Issues found: {len(validation_result.issues)}")

    # Test setting description
    from ..models.data_models import NarrativeContext
    context = NarrativeContext(session_id="test")
    description = world_manager.generate_setting_description("peaceful_garden", context)
    print(f"Setting description: {description}")
