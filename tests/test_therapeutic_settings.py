"""

# Logseq: [[TTA.dev/Tests/Test_therapeutic_settings]]
Unit tests for therapeutic settings models.

Tests the enhanced therapeutic settings, validation, conflict resolution,
and migration functionality.
"""

import unittest

from src.player_experience.models.enums import IntensityLevel, TherapeuticApproach
from src.player_experience.models.therapeutic_settings import (
    EnhancedTherapeuticSettings,
    SettingsConflict,
    SettingsConflictType,
    SettingsMigrationManager,
    TherapeuticBoundary,
    TherapeuticPreferencesValidator,
)


class TestTherapeuticBoundary(unittest.TestCase):
    """Test cases for TherapeuticBoundary model."""

    def test_boundary_creation(self):
        """Test creating a therapeutic boundary."""
        boundary = TherapeuticBoundary(
            boundary_id="test_boundary_1",
            boundary_type="avoid_topic",
            description="Avoid discussing family trauma",
            severity="hard",
            parameters={"topics": ["family", "trauma"]},
        )

        self.assertEqual(boundary.boundary_id, "test_boundary_1")
        self.assertEqual(boundary.boundary_type, "avoid_topic")
        self.assertEqual(boundary.severity, "hard")
        self.assertTrue(boundary.is_active)
        self.assertIn("topics", boundary.parameters)

    def test_boundary_auto_id_generation(self):
        """Test automatic ID generation for boundaries."""
        boundary = TherapeuticBoundary(
            boundary_id="",
            boundary_type="intensity_limit",
            description="Limit intensity during evening sessions",
            severity="soft",
        )

        self.assertIsNotNone(boundary.boundary_id)
        self.assertNotEqual(boundary.boundary_id, "")

    def test_boundary_invalid_severity(self):
        """Test validation of boundary severity."""
        with self.assertRaises(ValueError):
            TherapeuticBoundary(
                boundary_id="test_boundary_2",
                boundary_type="avoid_topic",
                description="Test boundary",
                severity="invalid_severity",
            )


class TestEnhancedTherapeuticSettings(unittest.TestCase):
    """Test cases for EnhancedTherapeuticSettings model."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_player_id = "test_player_123"
        self.basic_settings = EnhancedTherapeuticSettings(
            settings_id="test_settings_1",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.MEDIUM,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
        )

    def test_settings_creation(self):
        """Test creating enhanced therapeutic settings."""
        settings = self.basic_settings

        self.assertEqual(settings.settings_id, "test_settings_1")
        self.assertEqual(settings.player_id, self.test_player_id)
        self.assertEqual(settings.intensity_level, IntensityLevel.MEDIUM)
        self.assertIn(TherapeuticApproach.CBT, settings.preferred_approaches)
        self.assertIn(TherapeuticApproach.MINDFULNESS, settings.preferred_approaches)
        self.assertTrue(settings.is_active)

    def test_settings_auto_id_generation(self):
        """Test automatic ID generation for settings."""
        settings = EnhancedTherapeuticSettings(
            settings_id="", player_id=self.test_player_id
        )

        self.assertIsNotNone(settings.settings_id)
        self.assertNotEqual(settings.settings_id, "")

    def test_settings_validation(self):
        """Test validation of therapeutic settings."""
        # Test invalid intensity level
        with self.assertRaises(ValueError):
            EnhancedTherapeuticSettings(
                settings_id="test_settings_2",
                player_id=self.test_player_id,
                intensity_level="invalid_intensity",
            )

        # Test invalid feedback sensitivity
        with self.assertRaises(ValueError):
            EnhancedTherapeuticSettings(
                settings_id="test_settings_3",
                player_id=self.test_player_id,
                feedback_sensitivity=1.5,
            )

        # Test invalid session duration
        with self.assertRaises(ValueError):
            EnhancedTherapeuticSettings(
                settings_id="test_settings_4",
                player_id=self.test_player_id,
                session_duration_preference=5,  # Too short
            )

    def test_add_boundary(self):
        """Test adding therapeutic boundaries."""
        settings = self.basic_settings

        boundary = TherapeuticBoundary(
            boundary_id="boundary_1",
            boundary_type="avoid_topic",
            description="Avoid work stress topics",
            severity="soft",
        )

        settings.add_boundary(boundary)

        self.assertEqual(len(settings.boundaries), 1)
        self.assertEqual(settings.boundaries[0].boundary_id, "boundary_1")

        # Test adding duplicate boundary
        with self.assertRaises(ValueError):
            settings.add_boundary(boundary)

    def test_remove_boundary(self):
        """Test removing therapeutic boundaries."""
        settings = self.basic_settings

        boundary = TherapeuticBoundary(
            boundary_id="boundary_2",
            boundary_type="intensity_limit",
            description="Limit intensity on weekends",
            severity="hard",
        )

        settings.add_boundary(boundary)
        self.assertEqual(len(settings.boundaries), 1)

        # Remove boundary
        removed = settings.remove_boundary("boundary_2")
        self.assertTrue(removed)
        self.assertEqual(len(settings.boundaries), 0)

        # Try to remove non-existent boundary
        removed = settings.remove_boundary("non_existent")
        self.assertFalse(removed)

    def test_update_intensity(self):
        """Test updating intensity level."""
        settings = self.basic_settings
        original_updated_at = settings.updated_at

        # Wait a moment to ensure timestamp difference
        import time

        time.sleep(0.01)

        settings.update_intensity(IntensityLevel.HIGH)

        self.assertEqual(settings.intensity_level, IntensityLevel.HIGH)
        self.assertGreater(settings.updated_at, original_updated_at)

    def test_add_preferred_approach(self):
        """Test adding preferred therapeutic approaches."""
        settings = self.basic_settings
        original_count = len(settings.preferred_approaches)

        settings.add_preferred_approach(TherapeuticApproach.NARRATIVE_THERAPY)

        self.assertEqual(len(settings.preferred_approaches), original_count + 1)
        self.assertIn(
            TherapeuticApproach.NARRATIVE_THERAPY, settings.preferred_approaches
        )

        # Test adding duplicate approach (should not add)
        settings.add_preferred_approach(TherapeuticApproach.NARRATIVE_THERAPY)
        self.assertEqual(len(settings.preferred_approaches), original_count + 1)

    def test_remove_preferred_approach(self):
        """Test removing preferred therapeutic approaches."""
        settings = self.basic_settings

        # Remove existing approach
        removed = settings.remove_preferred_approach(TherapeuticApproach.CBT)
        self.assertTrue(removed)
        self.assertNotIn(TherapeuticApproach.CBT, settings.preferred_approaches)

        # Try to remove non-existent approach
        removed = settings.remove_preferred_approach(
            TherapeuticApproach.NARRATIVE_THERAPY
        )
        self.assertFalse(removed)

    def test_get_all_approaches(self):
        """Test getting all therapeutic approaches."""
        settings = self.basic_settings
        settings.secondary_approaches = [TherapeuticApproach.ACCEPTANCE_COMMITMENT]

        all_approaches = settings.get_all_approaches()

        self.assertIn(TherapeuticApproach.CBT, all_approaches)
        self.assertIn(TherapeuticApproach.MINDFULNESS, all_approaches)
        self.assertIn(TherapeuticApproach.ACCEPTANCE_COMMITMENT, all_approaches)

    def test_create_new_version(self):
        """Test creating new version of settings."""
        settings = self.basic_settings
        original_version = settings.version.version_number

        new_settings = settings.create_new_version(
            change_summary="Updated intensity level", created_by=self.test_player_id
        )

        self.assertEqual(new_settings.version.version_number, original_version + 1)
        self.assertEqual(
            new_settings.version.previous_version_id, settings.version.version_id
        )
        self.assertEqual(new_settings.version.created_by, self.test_player_id)
        self.assertEqual(
            new_settings.settings_id, settings.settings_id
        )  # Same settings ID

    def test_get_active_boundaries(self):
        """Test getting active boundaries only."""
        settings = self.basic_settings

        active_boundary = TherapeuticBoundary(
            boundary_id="active_boundary",
            boundary_type="avoid_topic",
            description="Active boundary",
            severity="soft",
            is_active=True,
        )

        inactive_boundary = TherapeuticBoundary(
            boundary_id="inactive_boundary",
            boundary_type="intensity_limit",
            description="Inactive boundary",
            severity="hard",
            is_active=False,
        )

        settings.add_boundary(active_boundary)
        settings.add_boundary(inactive_boundary)

        active_boundaries = settings.get_active_boundaries()

        self.assertEqual(len(active_boundaries), 1)
        self.assertEqual(active_boundaries[0].boundary_id, "active_boundary")


class TestTherapeuticPreferencesValidator(unittest.TestCase):
    """Test cases for TherapeuticPreferencesValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = TherapeuticPreferencesValidator()
        self.test_player_id = "test_player_456"

    def test_valid_settings(self):
        """Test validation of valid settings."""
        settings = EnhancedTherapeuticSettings(
            settings_id="valid_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.MEDIUM,
            preferred_approaches=[TherapeuticApproach.CBT],
            crisis_monitoring_enabled=True,
        )

        is_valid, conflicts = self.validator.validate_settings(settings)

        self.assertTrue(is_valid)
        self.assertEqual(len(conflicts), 0)

    def test_intensity_approach_mismatch(self):
        """Test detection of intensity-approach mismatches."""
        settings = EnhancedTherapeuticSettings(
            settings_id="mismatch_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[
                TherapeuticApproach.MINDFULNESS
            ],  # Gentle approach with high intensity
        )

        is_valid, conflicts = self.validator.validate_settings(settings)

        self.assertTrue(is_valid)  # Should be valid but with warnings
        self.assertGreater(len(conflicts), 0)

        # Check for intensity-approach mismatch conflict
        mismatch_conflicts = [
            c
            for c in conflicts
            if c.conflict_type == SettingsConflictType.INTENSITY_APPROACH_MISMATCH
        ]
        self.assertGreater(len(mismatch_conflicts), 0)

    def test_contradictory_preferences(self):
        """Test detection of contradictory preferences."""
        settings = EnhancedTherapeuticSettings(
            settings_id="contradictory_settings",
            player_id=self.test_player_id,
            comfort_topics=["family", "work"],
            avoid_topics=["family", "relationships"],  # "family" appears in both lists
        )

        is_valid, conflicts = self.validator.validate_settings(settings)

        self.assertFalse(is_valid)  # Should be invalid due to error-level conflict

        # Check for contradictory preferences conflict
        contradictory_conflicts = [
            c
            for c in conflicts
            if c.conflict_type == SettingsConflictType.CONTRADICTORY_PREFERENCES
        ]
        self.assertGreater(len(contradictory_conflicts), 0)

        conflict = contradictory_conflicts[0]
        self.assertEqual(conflict.severity, "error")
        self.assertTrue(conflict.auto_resolvable)

    def test_unsafe_combinations(self):
        """Test detection of unsafe setting combinations."""
        settings = EnhancedTherapeuticSettings(
            settings_id="unsafe_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.HIGH,
            crisis_monitoring_enabled=False,  # Unsafe combination
        )

        is_valid, conflicts = self.validator.validate_settings(settings)

        self.assertFalse(is_valid)  # Should be invalid due to critical conflict

        # Check for unsafe combination conflict
        unsafe_conflicts = [
            c
            for c in conflicts
            if c.conflict_type == SettingsConflictType.UNSAFE_COMBINATION
        ]
        self.assertGreater(len(unsafe_conflicts), 0)

        conflict = unsafe_conflicts[0]
        self.assertEqual(conflict.severity, "critical")
        self.assertTrue(conflict.auto_resolvable)

    def test_resolve_conflict(self):
        """Test automatic conflict resolution."""
        settings = EnhancedTherapeuticSettings(
            settings_id="resolvable_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.HIGH,
            crisis_monitoring_enabled=False,
        )

        is_valid, conflicts = self.validator.validate_settings(settings)
        self.assertFalse(is_valid)

        # Find the unsafe combination conflict
        unsafe_conflict = next(
            c
            for c in conflicts
            if c.conflict_type == SettingsConflictType.UNSAFE_COMBINATION
        )

        # Resolve the conflict
        resolution_option = unsafe_conflict.resolution_options[0]
        resolved_settings = self.validator.resolve_conflict(
            settings, unsafe_conflict, resolution_option
        )

        # Check that the conflict is resolved
        self.assertTrue(resolved_settings.crisis_monitoring_enabled)
        self.assertGreater(
            resolved_settings.version.version_number, settings.version.version_number
        )

    def test_non_resolvable_conflict(self):
        """Test handling of non-resolvable conflicts."""
        # Create a mock conflict that's not auto-resolvable
        conflict = SettingsConflict(
            conflict_id="non_resolvable",
            conflict_type=SettingsConflictType.THERAPEUTIC_BOUNDARY_VIOLATION,
            description="Manual review required",
            severity="error",
            conflicting_settings=["boundaries"],
            auto_resolvable=False,
        )

        settings = EnhancedTherapeuticSettings(
            settings_id="test_settings", player_id=self.test_player_id
        )

        with self.assertRaises(ValueError):
            self.validator.resolve_conflict(settings, conflict, {})


class TestSettingsMigrationManager(unittest.TestCase):
    """Test cases for SettingsMigrationManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.migration_manager = SettingsMigrationManager()
        self.test_player_id = "test_player_789"

    def test_migrate_to_v1_from_basic_settings(self):
        """Test migration from basic settings to v1 enhanced settings."""
        old_settings = {
            "settings_id": "old_settings_1",
            "player_id": self.test_player_id,
            "intensity_level": 0.7,  # Float intensity
            "preferred_approaches": [
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            "intervention_frequency": "frequent",
            "feedback_sensitivity": 0.8,
            "crisis_monitoring_enabled": True,
            "adaptive_difficulty": False,
            "session_duration_preference": 45,
            "trigger_warnings": ["loud_noises", "conflict"],
            "comfort_topics": ["nature", "music"],
            "avoid_topics": ["violence"],
        }

        migrated_settings = self.migration_manager.migrate_settings(
            old_settings, target_version=1
        )

        # Check basic migration
        self.assertEqual(migrated_settings.settings_id, "old_settings_1")
        self.assertEqual(migrated_settings.player_id, self.test_player_id)
        self.assertEqual(
            migrated_settings.intensity_level, IntensityLevel.HIGH
        )  # 0.7 -> HIGH
        self.assertEqual(
            migrated_settings.preferred_approaches,
            [TherapeuticApproach.CBT, TherapeuticApproach.MINDFULNESS],
        )
        self.assertEqual(migrated_settings.intervention_frequency, "frequent")
        self.assertEqual(migrated_settings.feedback_sensitivity, 0.8)
        self.assertTrue(migrated_settings.crisis_monitoring_enabled)
        self.assertFalse(migrated_settings.adaptive_difficulty)
        self.assertEqual(migrated_settings.session_duration_preference, 45)
        self.assertEqual(
            migrated_settings.trigger_warnings, ["loud_noises", "conflict"]
        )
        self.assertEqual(migrated_settings.comfort_topics, ["nature", "music"])
        self.assertEqual(migrated_settings.avoid_topics, ["violence"])

    def test_migrate_float_intensity_conversion(self):
        """Test conversion of float intensity levels to enums."""
        # Test low intensity
        old_settings_low = {"player_id": self.test_player_id, "intensity_level": 0.2}
        migrated_low = self.migration_manager.migrate_settings(
            old_settings_low, target_version=1
        )
        self.assertEqual(migrated_low.intensity_level, IntensityLevel.LOW)

        # Test medium intensity
        old_settings_medium = {"player_id": self.test_player_id, "intensity_level": 0.5}
        migrated_medium = self.migration_manager.migrate_settings(
            old_settings_medium, target_version=1
        )
        self.assertEqual(migrated_medium.intensity_level, IntensityLevel.MEDIUM)

        # Test high intensity
        old_settings_high = {"player_id": self.test_player_id, "intensity_level": 0.9}
        migrated_high = self.migration_manager.migrate_settings(
            old_settings_high, target_version=1
        )
        self.assertEqual(migrated_high.intensity_level, IntensityLevel.HIGH)

    def test_migrate_invalid_approaches_filtering(self):
        """Test filtering of invalid therapeutic approaches during migration."""
        old_settings = {
            "player_id": self.test_player_id,
            "preferred_approaches": [
                TherapeuticApproach.CBT,
                "invalid_approach",  # Invalid approach should be filtered out
                TherapeuticApproach.MINDFULNESS,
            ],
        }

        migrated_settings = self.migration_manager.migrate_settings(
            old_settings, target_version=1
        )

        # Should only contain valid approaches
        self.assertEqual(len(migrated_settings.preferred_approaches), 2)
        self.assertIn(TherapeuticApproach.CBT, migrated_settings.preferred_approaches)
        self.assertIn(
            TherapeuticApproach.MINDFULNESS, migrated_settings.preferred_approaches
        )

    def test_migrate_unsupported_version(self):
        """Test handling of unsupported migration versions."""
        old_settings = {"player_id": self.test_player_id}

        with self.assertRaises(ValueError):
            self.migration_manager.migrate_settings(old_settings, target_version=999)


if __name__ == "__main__":
    unittest.main()
