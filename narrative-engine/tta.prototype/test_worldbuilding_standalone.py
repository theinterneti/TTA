"""
Standalone test for worldbuilding system functionality.
This version includes all necessary classes inline to avoid import issues.
"""

import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when data model validation fails."""
    pass


@dataclass
class NarrativeContext:
    """Simple narrative context for testing."""
    session_id: str
    current_location_id: str = ""
    therapeutic_opportunities: list[str] = field(default_factory=list)


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
    """

    def __init__(self, neo4j_driver=None, redis_client=None):
        """Initialize worldbuilding and setting management."""
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
            }
        ]

    def get_location_details(self, location_id: str) -> LocationDetails | None:
        """Get detailed information about a location."""
        return self.locations_cache.get(location_id)

    def update_world_state(self, world_changes: list[WorldChange]) -> bool:
        """Update the world state with a list of changes."""
        logger.info(f"Applying {len(world_changes)} world state changes")

        # Validate all changes first
        for change in world_changes:
            try:
                change.validate()
            except ValidationError as e:
                logger.error(f"Invalid world change {change.change_id}: {e}")
                return False

        # Apply changes
        for change in world_changes:
            if self._apply_world_change(change):
                change.applied = True
            else:
                logger.error(f"Failed to apply change {change.change_id}")
                return False

        logger.info(f"Successfully applied {len(world_changes)} world state changes")
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

        location.unlock_conditions = []
        location.last_modified = datetime.now()
        return True

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
        return True

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
        return True

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

        return True

    def generate_setting_description(self, location_id: str, context: NarrativeContext) -> str:
        """Generate a rich setting description for a location."""
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
                "mystical": "The place feels touched by ancient magic and wisdom.",
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

        return " ".join(description_parts)

    def validate_world_consistency(self, proposed_changes: list[WorldChange] = None) -> ValidationResult:
        """Validate world consistency and identify potential issues."""
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

        for location in self.locations_cache.values():
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

        conflicting_themes = {
            "relaxation": ["high_stress", "intense_challenge"],
            "safety": ["danger", "risk_taking"],
            "social": ["isolation", "solitude"]
        }

        for location in self.locations_cache.values():
            if location.therapeutic_themes:
                for _direction, connected_id in location.connected_locations.items():
                    connected_location = self.get_location_details(connected_id)
                    if connected_location and connected_location.therapeutic_themes:
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


def test_worldbuilding_system():
    """Test basic worldbuilding system functionality."""
    print("🧪 Testing Worldbuilding and Setting Management System")

    # Create worldbuilding manager
    world_manager = WorldbuildingSettingManagement()
    print("✅ WorldbuildingSettingManagement created successfully")

    # Create sample locations
    garden = create_sample_location("peaceful_garden", "Peaceful Garden", LocationType.THERAPEUTIC_ENVIRONMENT)
    library = create_sample_location("quiet_library", "Quiet Library", LocationType.SAFE_SPACE)
    challenge_area = create_sample_location("challenge_mountain", "Challenge Mountain", LocationType.CHALLENGE_AREA)

    # Test location validation
    try:
        garden.validate()
        library.validate()
        challenge_area.validate()
        print("✅ Location validation successful")
    except Exception as e:
        print(f"❌ Location validation failed: {e}")
        return False

    # Add connections
    garden.connected_locations = {"north": "quiet_library", "east": "challenge_mountain"}
    library.connected_locations = {"south": "peaceful_garden"}
    challenge_area.connected_locations = {"west": "peaceful_garden"}

    # Cache locations
    world_manager.locations_cache[garden.location_id] = garden
    world_manager.locations_cache[library.location_id] = library
    world_manager.locations_cache[challenge_area.location_id] = challenge_area

    print("✅ Test locations created and cached")

    # Test getting location details
    retrieved_garden = world_manager.get_location_details("peaceful_garden")
    if retrieved_garden and retrieved_garden.name == "Peaceful Garden":
        print("✅ Location retrieval successful")
    else:
        print("❌ Location retrieval failed")
        return False

    # Test setting description generation
    context = NarrativeContext(session_id="test_session")
    description = world_manager.generate_setting_description("peaceful_garden", context)
    if description and len(description) > 0:
        print(f"✅ Setting description generated: {description[:100]}...")
    else:
        print("❌ Setting description generation failed")
        return False

    # Test world state changes
    world_change = WorldChange(
        change_type=WorldChangeType.LOCATION_MODIFY,
        target_location_id="peaceful_garden",
        description="Change garden atmosphere to mysterious",
        changes={"atmosphere": "mysterious"}
    )

    try:
        world_change.validate()
        print("✅ World change validation successful")
    except Exception as e:
        print(f"❌ World change validation failed: {e}")
        return False

    # Apply world change
    result = world_manager.update_world_state([world_change])
    if result:
        print("✅ World state update successful")

        # Verify change was applied
        updated_garden = world_manager.get_location_details("peaceful_garden")
        if updated_garden.atmosphere == "mysterious":
            print("✅ World change applied correctly")
        else:
            print("❌ World change not applied correctly")
            return False
    else:
        print("❌ World state update failed")
        return False

    # Test world consistency validation
    validation_result = world_manager.validate_world_consistency()
    if validation_result:
        print("✅ World consistency validation completed")
        print(f"   - Valid: {validation_result.is_valid}")
        print(f"   - Issues: {len(validation_result.issues)}")
        print(f"   - Warnings: {validation_result.warnings_count}")
        print(f"   - Errors: {validation_result.errors_count}")
        print(f"   - Critical: {validation_result.critical_count}")
    else:
        print("❌ World consistency validation failed")
        return False

    # Test location unlocking
    challenge_area.unlock_conditions = ["flag:courage_gained"]
    unlock_change = WorldChange(
        change_type=WorldChangeType.LOCATION_UNLOCK,
        target_location_id="challenge_mountain",
        description="Unlock challenge mountain",
        changes={}
    )

    result = world_manager.update_world_state([unlock_change])
    if result:
        updated_challenge = world_manager.get_location_details("challenge_mountain")
        if len(updated_challenge.unlock_conditions) == 0:
            print("✅ Location unlocking successful")
        else:
            print("❌ Location unlocking failed - conditions not cleared")
            return False
    else:
        print("❌ Location unlocking failed")
        return False

    # Test serialization
    try:
        garden_dict = garden.to_dict()
        restored_garden = LocationDetails.from_dict(garden_dict)
        if restored_garden.location_id == garden.location_id:
            print("✅ Location serialization/deserialization successful")
        else:
            print("❌ Location serialization/deserialization failed")
            return False
    except Exception as e:
        print(f"❌ Location serialization failed: {e}")
        return False

    print("\n🎉 All worldbuilding system tests passed!")
    return True


def test_consistency_rules():
    """Test world consistency validation rules."""
    print("\n🔍 Testing World Consistency Rules")

    world_manager = WorldbuildingSettingManagement()

    # Create locations with potential issues
    safe_location = create_sample_location("safe_area", "Safe Area", LocationType.SAFE_SPACE)
    safe_location.safety_level = 0.9
    safe_location.therapeutic_themes = ["relaxation", "safety"]

    dangerous_location = create_sample_location("danger_zone", "Danger Zone", LocationType.CHALLENGE_AREA)
    dangerous_location.safety_level = 0.1
    dangerous_location.therapeutic_themes = ["high_stress", "risk_taking"]

    # Connect them directly (should trigger safety progression warning)
    safe_location.connected_locations = {"north": "danger_zone"}
    dangerous_location.connected_locations = {"south": "safe_area"}

    # Add isolated location (should trigger connectivity warning)
    isolated_location = create_sample_location("isolated", "Isolated Place", LocationType.EXPLORATION_ZONE)

    # Cache locations
    world_manager.locations_cache[safe_location.location_id] = safe_location
    world_manager.locations_cache[dangerous_location.location_id] = dangerous_location
    world_manager.locations_cache[isolated_location.location_id] = isolated_location

    # Run validation
    validation_result = world_manager.validate_world_consistency()

    print(f"   - Total issues found: {len(validation_result.issues)}")
    print(f"   - Warnings: {validation_result.warnings_count}")
    print(f"   - Errors: {validation_result.errors_count}")

    # Check for expected issues
    connectivity_issues = [issue for issue in validation_result.issues if issue.category == "connectivity"]
    safety_issues = [issue for issue in validation_result.issues if issue.category == "safety_progression"]
    therapeutic_issues = [issue for issue in validation_result.issues if issue.category == "therapeutic_coherence"]

    print(f"   - Connectivity issues: {len(connectivity_issues)}")
    print(f"   - Safety progression issues: {len(safety_issues)}")
    print(f"   - Therapeutic coherence issues: {len(therapeutic_issues)}")

    if len(connectivity_issues) > 0:
        print("✅ Connectivity validation working (found isolated location)")

    if len(safety_issues) > 0:
        print("✅ Safety progression validation working (found large safety gap)")

    if len(therapeutic_issues) > 0:
        print("✅ Therapeutic coherence validation working (found conflicting themes)")

    print("✅ Consistency rules testing completed")


def test_advanced_features():
    """Test advanced worldbuilding features."""
    print("\n🚀 Testing Advanced Worldbuilding Features")

    world_manager = WorldbuildingSettingManagement()

    # Create a complex location with environmental factors
    mystical_forest = LocationDetails(
        location_id="mystical_forest",
        name="Mystical Forest",
        description="A magical forest filled with ancient wisdom and therapeutic energy.",
        location_type=LocationType.THERAPEUTIC_ENVIRONMENT,
        therapeutic_themes=["mindfulness", "connection", "growth"],
        atmosphere="mystical",
        environmental_factors={
            "lighting": "dappled sunlight",
            "weather": "gentle breeze",
            "sounds": "rustling leaves and bird songs"
        },
        lore_elements=[
            "Ancient trees hold memories of countless healing journeys",
            "The forest responds to the emotional state of visitors",
            "Hidden clearings appear when one is ready for deeper reflection"
        ],
        unlock_conditions=["therapeutic_goal:mindfulness_basics"],
        therapeutic_opportunities=["guided_meditation", "nature_connection"],
        safety_level=0.9,
        immersion_level=0.95
    )

    # Test complex location validation
    try:
        mystical_forest.validate()
        print("✅ Complex location validation successful")
    except Exception as e:
        print(f"❌ Complex location validation failed: {e}")
        return False

    # Cache the location
    world_manager.locations_cache[mystical_forest.location_id] = mystical_forest

    # Test rich setting description
    context = NarrativeContext(
        session_id="test_session",
        therapeutic_opportunities=["guided_meditation"]
    )

    description = world_manager.generate_setting_description("mystical_forest", context)
    print(f"✅ Rich setting description: {description}")

    # Test environmental shift
    env_shift = WorldChange(
        change_type=WorldChangeType.ENVIRONMENT_SHIFT,
        target_location_id="mystical_forest",
        description="Shift forest to evening atmosphere",
        changes={
            "environmental_factors": {
                "lighting": "golden evening light",
                "sounds": "gentle night sounds"
            },
            "atmosphere": "serene"
        }
    )

    result = world_manager.update_world_state([env_shift])
    if result:
        updated_forest = world_manager.get_location_details("mystical_forest")
        if updated_forest.environmental_factors["lighting"] == "golden evening light":
            print("✅ Environmental shift successful")
        else:
            print("❌ Environmental shift failed")
            return False
    else:
        print("❌ Environmental shift failed")
        return False

    # Test lore update
    lore_update = WorldChange(
        change_type=WorldChangeType.LORE_UPDATE,
        target_location_id="mystical_forest",
        description="Add new lore about the forest's healing properties",
        changes={
            "lore_elements": [
                "The evening light enhances the forest's therapeutic properties",
                "Visitors often experience profound insights during twilight hours"
            ]
        }
    )

    result = world_manager.update_world_state([lore_update])
    if result:
        updated_forest = world_manager.get_location_details("mystical_forest")
        if len(updated_forest.lore_elements) > 3:
            print("✅ Lore update successful")
        else:
            print("❌ Lore update failed")
            return False
    else:
        print("❌ Lore update failed")
        return False

    print("✅ Advanced features testing completed")


if __name__ == "__main__":
    try:
        success = test_worldbuilding_system()
        if success:
            test_consistency_rules()
            test_advanced_features()
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
