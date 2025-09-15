"""
Tests for Universal Accessibility System

This module tests the universal accessibility functionality including
WCAG 2.1 AA compliance, multi-language support, assistive technology
integration, and adaptive accessibility features.
"""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.user_experience.universal_accessibility_system import (
    AccessibilityAudit,
    AccessibilityFeature,
    AccessibilityLevel,
    AccessibilityProfile,
    DisabilityType,
    LanguageCode,
    UniversalAccessibilitySystem,
)


class TestUniversalAccessibilitySystem:
    """Test Universal Accessibility System functionality."""

    @pytest_asyncio.fixture
    async def accessibility_system(self):
        """Create test accessibility system instance."""
        system = UniversalAccessibilitySystem()
        await system.initialize()
        yield system
        await system.shutdown()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()
        engine.health_check.return_value = {"status": "healthy"}
        return engine

    @pytest.fixture
    def mock_integration_systems(self):
        """Create mock integration systems."""
        systems = {}

        for system_name in [
            "clinical_dashboard_manager",
            "cloud_deployment_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def sample_accessibility_preferences(self):
        """Create sample accessibility preferences."""
        return {
            "language": "en-US",
            "color_blind_type": "protanopia",
            "click_delay": 0.5,
            "hover_delay": 1.0,
            "reading_level": "simple",
            "memory_assistance": True,
            "screen_reader_type": "nvda",
            "voice_control": True,
            "motion_sensitivity": True
        }

    @pytest.mark.asyncio
    async def test_initialization(self, accessibility_system):
        """Test accessibility system initialization."""
        assert accessibility_system.status == "running"
        assert len(accessibility_system.wcag_guidelines) == 4  # 4 WCAG principles
        assert len(accessibility_system.assistive_technology_configs) == 4  # 4 AT categories
        assert len(accessibility_system.localization_data) == 10  # 10 supported languages
        assert len(accessibility_system.accessibility_adaptations) == 4  # 4 adaptation categories

        # Should have background tasks running
        assert accessibility_system._accessibility_monitoring_task is not None
        assert accessibility_system._compliance_checking_task is not None
        assert accessibility_system._adaptation_optimization_task is not None
        assert accessibility_system._localization_update_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, accessibility_system, mock_therapeutic_systems, mock_personalization_engine, mock_integration_systems):
        """Test system dependency injection."""
        accessibility_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        accessibility_system.inject_personalization_engine(mock_personalization_engine)
        accessibility_system.inject_integration_systems(**mock_integration_systems)

        # Should have all systems injected
        assert len(accessibility_system.therapeutic_systems) == 9
        assert accessibility_system.personalization_engine is not None
        assert accessibility_system.clinical_dashboard_manager is not None
        assert accessibility_system.cloud_deployment_manager is not None

    @pytest.mark.asyncio
    async def test_create_accessibility_profile(self, accessibility_system, sample_accessibility_preferences):
        """Test accessibility profile creation."""
        user_id = "accessibility_user_001"
        disability_types = [DisabilityType.VISUAL, DisabilityType.MOTOR, DisabilityType.COGNITIVE]

        profile = await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        # Should create valid profile
        assert isinstance(profile, AccessibilityProfile)
        assert profile.user_id == user_id
        assert profile.disability_types == disability_types
        assert profile.primary_language == LanguageCode.EN_US
        assert profile.compliance_level == AccessibilityLevel.AA

        # Should configure features based on disabilities
        assert AccessibilityFeature.SCREEN_READER in profile.enabled_features
        assert AccessibilityFeature.HIGH_CONTRAST in profile.enabled_features
        assert AccessibilityFeature.LARGE_TEXT in profile.enabled_features
        assert AccessibilityFeature.KEYBOARD_NAVIGATION in profile.enabled_features
        assert AccessibilityFeature.VOICE_CONTROL in profile.enabled_features
        assert AccessibilityFeature.SIMPLIFIED_INTERFACE in profile.enabled_features
        assert AccessibilityFeature.COGNITIVE_ASSISTANCE in profile.enabled_features
        assert AccessibilityFeature.REDUCED_MOTION in profile.enabled_features

        # Should set preferences
        assert profile.color_blind_type == "protanopia"
        assert profile.click_delay == 0.5
        assert profile.hover_delay == 1.0
        assert profile.reading_level == "simple"
        assert profile.memory_assistance
        assert profile.screen_reader_type == "nvda"
        assert profile.voice_control_enabled

        # Should store profile
        assert user_id in accessibility_system.accessibility_profiles
        assert accessibility_system.accessibility_metrics["total_users_with_profiles"] == 1

    @pytest.mark.asyncio
    async def test_adapt_interface_for_accessibility(self, accessibility_system, sample_accessibility_preferences):
        """Test interface adaptation for accessibility."""
        user_id = "adaptation_user_001"
        disability_types = [DisabilityType.VISUAL, DisabilityType.MOTOR]

        # Create accessibility profile
        await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        # Test component adaptation
        component_data = {
            "type": "button",
            "text": "Continue",
            "color": "#0066cc",
            "font_size": 16
        }

        adapted_data = await accessibility_system.adapt_interface_for_accessibility(
            user_id=user_id,
            component_type="button",
            component_data=component_data
        )

        # Should apply visual adaptations
        assert "font_size_multiplier" in adapted_data
        assert "high_contrast" in adapted_data
        assert "color_blind_filter" in adapted_data
        assert "enhanced_focus" in adapted_data

        # Should apply motor adaptations
        assert "minimum_click_size" in adapted_data
        assert "click_delay" in adapted_data
        assert "hover_delay" in adapted_data
        assert "keyboard_navigation" in adapted_data

        # Should apply localization
        assert "text_direction" in adapted_data
        assert "date_format" in adapted_data

    @pytest.mark.asyncio
    async def test_validate_wcag_compliance(self, accessibility_system):
        """Test WCAG 2.1 compliance validation."""
        component_id = "test_component_001"
        component_type = "form"

        # Test component with good compliance
        good_component_data = {
            "contrast_ratio": 7.0,
            "tab_order": "logical",
            "keyboard_handlers": True,
            "aria_labels": True,
            "semantic_markup": True,
            "focus_indicators": True,
            "focus_management": True,
            "headings": True,
            "landmarks": True
        }

        audit = await accessibility_system.validate_wcag_compliance(
            component_id=component_id,
            component_type=component_type,
            component_data=good_component_data
        )

        # Should pass all checks
        assert isinstance(audit, AccessibilityAudit)
        assert audit.component_id == component_id
        assert audit.component_type == component_type
        assert audit.wcag_level == AccessibilityLevel.AA
        assert audit.color_contrast_pass
        assert audit.keyboard_navigation_pass
        assert audit.screen_reader_pass
        assert audit.focus_management_pass
        assert audit.semantic_markup_pass
        assert audit.compliance_score == 1.0
        assert len(audit.recommendations) == 0

        # Test component with poor compliance
        poor_component_data = {
            "contrast_ratio": 2.0,  # Below WCAG AA requirement
        }

        poor_audit = await accessibility_system.validate_wcag_compliance(
            component_id="poor_component",
            component_type="button",
            component_data=poor_component_data
        )

        # Should fail checks
        assert not poor_audit.color_contrast_pass
        assert not poor_audit.keyboard_navigation_pass
        assert not poor_audit.screen_reader_pass
        assert not poor_audit.focus_management_pass
        assert not poor_audit.semantic_markup_pass
        assert poor_audit.compliance_score == 0.0
        assert len(poor_audit.recommendations) == 5

        # Should store audit results
        assert component_id in accessibility_system.audit_results
        assert len(accessibility_system.audit_results[component_id]) == 1

    @pytest.mark.asyncio
    async def test_get_localized_content(self, accessibility_system):
        """Test localized content retrieval."""
        # Test English content
        english_content = await accessibility_system.get_localized_content(
            content_key="welcome",
            language=LanguageCode.EN_US
        )
        assert english_content == "Welcome"

        # Test Spanish content
        spanish_content = await accessibility_system.get_localized_content(
            content_key="welcome",
            language=LanguageCode.ES_ES
        )
        assert spanish_content == "Bienvenido"

        # Test French content
        french_content = await accessibility_system.get_localized_content(
            content_key="welcome",
            language=LanguageCode.FR_FR
        )
        assert french_content == "Bienvenue"

        # Test missing translation (should fall back to key)
        missing_content = await accessibility_system.get_localized_content(
            content_key="missing_key",
            language=LanguageCode.EN_US
        )
        assert missing_content == "missing_key"

    @pytest.mark.asyncio
    async def test_optimize_for_assistive_technology(self, accessibility_system, sample_accessibility_preferences):
        """Test assistive technology optimization."""
        user_id = "at_user_001"
        disability_types = [DisabilityType.VISUAL, DisabilityType.MOTOR]

        # Create accessibility profile
        await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        component_data = {
            "type": "navigation",
            "items": ["Home", "About", "Contact"]
        }

        # Test screen reader optimization
        screen_reader_optimized = await accessibility_system.optimize_for_assistive_technology(
            user_id=user_id,
            assistive_tech_type="screen_reader",
            component_data=component_data
        )

        assert screen_reader_optimized["aria_labels"]
        assert screen_reader_optimized["aria_descriptions"]
        assert screen_reader_optimized["landmarks"]
        assert screen_reader_optimized["heading_structure"]
        assert screen_reader_optimized["live_regions"]

        # Test voice control optimization
        voice_control_optimized = await accessibility_system.optimize_for_assistive_technology(
            user_id=user_id,
            assistive_tech_type="voice_control",
            component_data=component_data
        )

        assert voice_control_optimized["voice_commands"]
        assert voice_control_optimized["voice_labels"]
        assert voice_control_optimized["dictation_support"]

        # Test switch navigation optimization
        switch_optimized = await accessibility_system.optimize_for_assistive_technology(
            user_id=user_id,
            assistive_tech_type="switch_navigation",
            component_data=component_data
        )

        assert switch_optimized["scanning_enabled"]
        assert switch_optimized["scan_timing"] == 0.5
        assert switch_optimized["switch_activation"]

        # Test eye tracking optimization
        eye_tracking_optimized = await accessibility_system.optimize_for_assistive_technology(
            user_id=user_id,
            assistive_tech_type="eye_tracking",
            component_data=component_data
        )

        assert eye_tracking_optimized["gaze_interaction"]
        assert eye_tracking_optimized["dwell_click"]
        assert eye_tracking_optimized["eye_tracking_zones"]

    @pytest.mark.asyncio
    async def test_get_accessibility_insights(self, accessibility_system, sample_accessibility_preferences):
        """Test accessibility insights generation."""
        user_id = "insights_user_001"
        disability_types = [DisabilityType.VISUAL, DisabilityType.COGNITIVE]

        # Create accessibility profile
        await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        # Perform some compliance audits
        await accessibility_system.validate_wcag_compliance(
            component_id="test_component",
            component_type="form",
            component_data={"contrast_ratio": 6.0, "aria_labels": True, "semantic_markup": True}
        )

        # Get insights
        insights = await accessibility_system.get_accessibility_insights(user_id)

        # Should return comprehensive insights
        assert "user_id" in insights
        assert "analysis_timestamp" in insights
        assert "accessibility_profile" in insights
        assert "adaptation_effectiveness" in insights
        assert "compliance_status" in insights
        assert "recommendations" in insights

        # Validate accessibility profile data
        profile_data = insights["accessibility_profile"]
        assert profile_data["disability_types"] == ["visual", "cognitive"]
        assert len(profile_data["enabled_features"]) > 0
        assert profile_data["primary_language"] == "en-US"
        assert profile_data["compliance_level"] == "aa"

        # Validate adaptation effectiveness
        effectiveness = insights["adaptation_effectiveness"]
        assert "effectiveness" in effectiveness
        assert "enabled_features" in effectiveness
        assert "total_features" in effectiveness

        # Validate compliance status
        compliance = insights["compliance_status"]
        assert "compliance_score" in compliance
        assert "level" in compliance

        # Validate recommendations
        recommendations = insights["recommendations"]
        assert isinstance(recommendations, list)

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, accessibility_system, sample_accessibility_preferences):
        """Test performance benchmarks for accessibility operations."""
        import time

        user_id = "performance_user_001"
        disability_types = [DisabilityType.VISUAL, DisabilityType.MOTOR, DisabilityType.COGNITIVE]

        # Test profile creation performance
        start_time = time.perf_counter()

        await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        profile_time = (time.perf_counter() - start_time) * 1000
        assert profile_time < 200.0  # Should be under 200ms

        # Test interface adaptation performance
        start_time = time.perf_counter()

        component_data = {"type": "form", "fields": ["name", "email", "message"]}
        await accessibility_system.adapt_interface_for_accessibility(
            user_id=user_id,
            component_type="form",
            component_data=component_data
        )

        adaptation_time = (time.perf_counter() - start_time) * 1000
        assert adaptation_time < 200.0  # Should be under 200ms

        # Test WCAG compliance validation performance
        start_time = time.perf_counter()

        await accessibility_system.validate_wcag_compliance(
            component_id="perf_test_component",
            component_type="button",
            component_data={"contrast_ratio": 5.0, "aria_labels": True}
        )

        validation_time = (time.perf_counter() - start_time) * 1000
        assert validation_time < 100.0  # Should be under 100ms

        # Test localized content retrieval performance
        start_time = time.perf_counter()

        await accessibility_system.get_localized_content(
            content_key="welcome",
            language=LanguageCode.ES_ES
        )

        localization_time = (time.perf_counter() - start_time) * 1000
        assert localization_time < 50.0  # Should be under 50ms

        # Test assistive technology optimization performance
        start_time = time.perf_counter()

        await accessibility_system.optimize_for_assistive_technology(
            user_id=user_id,
            assistive_tech_type="screen_reader",
            component_data=component_data
        )

        optimization_time = (time.perf_counter() - start_time) * 1000
        assert optimization_time < 100.0  # Should be under 100ms

    @pytest.mark.asyncio
    async def test_accessibility_interface_compatibility(self, accessibility_system, mock_therapeutic_systems, mock_personalization_engine, mock_integration_systems, sample_accessibility_preferences):
        """Test compatibility with accessibility interface expectations."""
        # Inject all dependencies
        accessibility_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        accessibility_system.inject_personalization_engine(mock_personalization_engine)
        accessibility_system.inject_integration_systems(**mock_integration_systems)

        user_id = "interface_test_user"
        disability_types = [DisabilityType.VISUAL, DisabilityType.MOTOR]

        # Test complete accessibility workflow
        profile = await accessibility_system.create_accessibility_profile(
            user_id=user_id,
            disability_types=disability_types,
            preferences=sample_accessibility_preferences
        )

        # Should match expected profile structure
        assert hasattr(profile, "profile_id")
        assert hasattr(profile, "user_id")
        assert hasattr(profile, "disability_types")
        assert hasattr(profile, "enabled_features")
        assert hasattr(profile, "primary_language")
        assert hasattr(profile, "compliance_level")
        assert hasattr(profile, "font_size_multiplier")
        assert hasattr(profile, "contrast_ratio")

        # Test interface adaptation
        component_data = {"type": "button", "text": "Submit"}
        adapted_data = await accessibility_system.adapt_interface_for_accessibility(
            user_id=user_id,
            component_type="button",
            component_data=component_data
        )

        # Should return adapted component data
        assert isinstance(adapted_data, dict)
        assert "type" in adapted_data

        # Test WCAG compliance validation
        audit = await accessibility_system.validate_wcag_compliance(
            component_id="interface_test_component",
            component_type="button",
            component_data=component_data
        )

        # Should match expected audit structure
        assert hasattr(audit, "audit_id")
        assert hasattr(audit, "component_id")
        assert hasattr(audit, "compliance_score")
        assert hasattr(audit, "recommendations")

        # Test health check
        health_check = await accessibility_system.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "accessibility_status" in health_check
        assert "total_accessibility_profiles" in health_check
        assert "supported_languages" in health_check
        assert "accessibility_metrics" in health_check
