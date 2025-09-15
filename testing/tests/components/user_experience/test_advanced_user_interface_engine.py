"""
Tests for Advanced User Interface Engine

This module tests the adaptive UI/UX system including responsive design,
cross-platform compatibility, theme customization, layout adaptation,
and personalized interface optimization.
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.components.user_experience.advanced_user_interface_engine import (
    AdaptationTrigger,
    AdvancedUserInterfaceEngine,
    DeviceType,
    InteractionMode,
    InterfaceComponent,
    InterfaceConfiguration,
    InterfaceLayout,
    InterfaceTheme,
    LayoutType,
)


class TestAdvancedUserInterfaceEngine:
    """Test Advanced User Interface Engine functionality."""

    @pytest_asyncio.fixture
    async def ui_engine(self):
        """Create test UI engine instance."""
        engine = AdvancedUserInterfaceEngine()
        await engine.initialize()
        yield engine
        await engine.shutdown()

    @pytest.fixture
    def mock_accessibility_system(self):
        """Create mock accessibility system."""
        system = AsyncMock()
        system.accessibility_profiles = {
            "test_user_001": Mock(
                disability_types=["visual"],
                enabled_features={"screen_reader", "high_contrast"},
                font_size_multiplier=1.2,
                contrast_ratio=7.0
            )
        }
        return system

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()

        # Mock user profile
        mock_profile = Mock()
        mock_profile.therapeutic_preferences = {
            "focus_areas": ["anxiety", "depression"],
            "approaches": ["calm_approach"]
        }
        mock_profile.interaction_preferences = {
            "preferred_modes": ["mouse", "keyboard"]
        }
        mock_profile.engagement_metrics = {
            "overall_score": 0.7
        }
        mock_profile.learning_characteristics = {
            "learning_style": "visual"
        }

        engine.get_user_profile.return_value = mock_profile
        return engine

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
    def sample_user_preferences(self):
        """Create sample user preferences."""
        return {
            "theme": "therapeutic_calm",
            "layout_type": "standard",
            "font_family": "Inter",
            "animation_level": "standard",
            "device_type": "desktop"
        }

    @pytest.mark.asyncio
    async def test_initialization(self, ui_engine):
        """Test UI engine initialization."""
        assert ui_engine.status == "running"
        assert len(ui_engine.theme_definitions) == 5  # 5 predefined themes
        assert len(ui_engine.layout_templates) == 6  # 6 layout types
        assert len(ui_engine.component_library) == 8  # 8 component types
        assert len(ui_engine.breakpoint_system) == 6  # 6 responsive breakpoints
        assert len(ui_engine.adaptation_rules) == 5  # 5 adaptation trigger types

        # Should have background tasks running
        assert ui_engine._interface_optimization_task is not None
        assert ui_engine._adaptation_monitoring_task is not None
        assert ui_engine._performance_optimization_task is not None
        assert ui_engine._user_behavior_analysis_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, ui_engine, mock_accessibility_system, mock_personalization_engine, mock_therapeutic_systems):
        """Test system dependency injection."""
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)
        ui_engine.inject_therapeutic_systems(**mock_therapeutic_systems)
        ui_engine.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(),
            cloud_deployment_manager=AsyncMock()
        )

        # Should have all systems injected
        assert ui_engine.accessibility_system is not None
        assert ui_engine.personalization_engine is not None
        assert len(ui_engine.therapeutic_systems) == 9
        assert ui_engine.clinical_dashboard_manager is not None
        assert ui_engine.cloud_deployment_manager is not None

    @pytest.mark.asyncio
    async def test_create_interface_configuration(self, ui_engine, mock_accessibility_system, mock_personalization_engine, sample_user_preferences):
        """Test interface configuration creation."""
        # Inject dependencies
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)

        user_id = "ui_test_user_001"
        device_type = DeviceType.DESKTOP

        config = await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=device_type,
            preferences=sample_user_preferences
        )

        # Should create valid configuration
        assert isinstance(config, InterfaceConfiguration)
        assert config.user_id == user_id
        assert config.device_type == device_type
        assert config.theme == InterfaceTheme.THERAPEUTIC_CALM
        assert config.layout_type == LayoutType.THERAPEUTIC_FOCUSED  # Changed due to therapeutic focus areas
        assert config.font_family == "Inter"
        assert config.accessibility_enabled
        assert len(config.therapeutic_focus_areas) == 2  # anxiety, depression
        assert InteractionMode.MOUSE in config.interaction_modes
        assert InteractionMode.KEYBOARD in config.interaction_modes

        # Should store configuration
        assert user_id in ui_engine.interface_configurations
        assert ui_engine.ui_metrics["total_interface_configurations"] == 1

    @pytest.mark.asyncio
    async def test_adapt_interface_layout(self, ui_engine, mock_accessibility_system, mock_personalization_engine, sample_user_preferences):
        """Test interface layout adaptation."""
        # Inject dependencies and create configuration
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)

        user_id = "layout_test_user_001"

        # Create configuration first
        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.DESKTOP,
            preferences=sample_user_preferences
        )

        # Test layout adaptation
        layout_context = {
            "screen_size": {"width": 1920, "height": 1080},
            "therapeutic_session": "active",
            "user_engagement": 0.8
        }

        layout = await ui_engine.adapt_interface_layout(
            user_id=user_id,
            layout_context=layout_context,
            adaptation_trigger=AdaptationTrigger.USER_PREFERENCE
        )

        # Should create valid layout
        assert isinstance(layout, InterfaceLayout)
        assert layout.user_id == user_id
        assert len(layout.components) == 3  # navigation, session card, progress
        assert layout.fluid_layout
        assert len(layout.breakpoints) == 6  # responsive breakpoints
        assert len(layout.therapeutic_flow) == 4  # therapeutic flow steps

        # Should store layout
        assert user_id in ui_engine.interface_layouts
        assert ui_engine.ui_metrics["total_layout_adaptations"] == 1

    @pytest.mark.asyncio
    async def test_generate_responsive_component(self, ui_engine, mock_accessibility_system, sample_user_preferences):
        """Test responsive component generation."""
        # Inject dependencies and create configuration
        ui_engine.inject_accessibility_system(mock_accessibility_system)

        user_id = "component_test_user_001"

        # Add user to accessibility system profiles for proper testing
        mock_accessibility_system.accessibility_profiles[user_id] = Mock(
            disability_types=["visual"],
            enabled_features={"screen_reader"},
            font_size_multiplier=1.0,
            contrast_ratio=4.5
        )

        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.MOBILE,
            preferences=sample_user_preferences
        )

        # Test component generation
        component_context = {
            "name": "Test Button",
            "therapeutic_relevance": "high",
            "engagement_priority": "critical"
        }

        component = await ui_engine.generate_responsive_component(
            component_type="button",
            user_id=user_id,
            component_context=component_context
        )

        # Should create valid component
        assert isinstance(component, InterfaceComponent)
        assert component.component_type == "button"
        assert component.component_name == "Test Button"
        assert len(component.responsive_breakpoints) == 6  # responsive breakpoints
        assert "font_size" in component.styles
        assert "padding" in component.styles
        assert "aria_label" in component.accessibility_attributes  # Now should be present
        assert "therapeutic_relevance" in component.therapeutic_context
        assert "--primary-color" in component.styles  # theme applied

    @pytest.mark.asyncio
    async def test_optimize_interface_performance(self, ui_engine, sample_user_preferences):
        """Test interface performance optimization."""
        user_id = "performance_test_user_001"

        # Create configuration and layout
        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.MOBILE,
            preferences=sample_user_preferences
        )

        await ui_engine.adapt_interface_layout(
            user_id=user_id,
            layout_context={"screen_size": {"width": 375, "height": 667}},
            adaptation_trigger=AdaptationTrigger.DEVICE_CHANGE
        )

        # Test performance optimization
        performance_context = {
            "device_performance": "low",
            "network_speed": "3g",
            "battery_level": 0.2
        }

        result = await ui_engine.optimize_interface_performance(
            user_id=user_id,
            performance_context=performance_context
        )

        # Should apply optimizations
        assert result["optimization_applied"]
        assert "optimizations" in result
        assert "performance_score" in result
        assert result["performance_score"] > 0.0

        # Should update metrics
        assert ui_engine.ui_metrics["interface_performance_score"] > 0.0

    @pytest.mark.asyncio
    async def test_customize_interface_theme(self, ui_engine, sample_user_preferences):
        """Test interface theme customization."""
        user_id = "theme_test_user_001"

        # Create configuration
        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.DESKTOP,
            preferences=sample_user_preferences
        )

        # Test theme customization
        theme_preferences = {
            "theme": "dark",
            "colors": {
                "primary": "#ff6b6b",
                "secondary": "#4ecdc4"
            },
            "font_family": "Roboto",
            "font_size_multiplier": 1.1,
            "therapeutic_focus": ["mindfulness", "stress_reduction"]
        }

        result = await ui_engine.customize_interface_theme(
            user_id=user_id,
            theme_preferences=theme_preferences
        )

        # Should apply theme customizations
        assert result["theme_applied"]
        assert result["theme_name"] == "dark"
        assert "theme_config" in result

        # Should update configuration
        updated_config = ui_engine.interface_configurations[user_id]
        assert updated_config.theme == InterfaceTheme.DARK
        assert updated_config.custom_colors["primary"] == "#ff6b6b"
        assert updated_config.font_family == "Roboto"
        assert updated_config.font_size_multiplier == 1.1
        assert "mindfulness" in updated_config.therapeutic_focus_areas

    @pytest.mark.asyncio
    async def test_get_interface_analytics(self, ui_engine, mock_accessibility_system, mock_personalization_engine, sample_user_preferences):
        """Test interface analytics generation."""
        # Inject dependencies
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)

        user_id = "analytics_test_user_001"

        # Create configuration and layout
        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.TABLET,
            preferences=sample_user_preferences
        )

        await ui_engine.adapt_interface_layout(
            user_id=user_id,
            layout_context={"therapeutic_session": "active"},
            adaptation_trigger=AdaptationTrigger.THERAPEUTIC_PROGRESS
        )

        # Get analytics
        analytics = await ui_engine.get_interface_analytics(user_id)

        # Should return comprehensive analytics
        assert "user_id" in analytics
        assert "analysis_timestamp" in analytics
        assert "interface_configuration" in analytics
        assert "layout_analytics" in analytics
        assert "performance_metrics" in analytics
        assert "accessibility_compliance" in analytics
        assert "therapeutic_alignment" in analytics
        assert "user_engagement" in analytics
        assert "recommendations" in analytics

        # Validate configuration data
        config_data = analytics["interface_configuration"]
        assert config_data["theme"] == "therapeutic_calm"
        assert config_data["layout_type"] == "therapeutic_focused"  # Changed due to therapeutic focus areas
        assert config_data["device_type"] == "tablet"
        assert config_data["accessibility_enabled"]

        # Validate analytics scores
        assert analytics["performance_metrics"]["overall_score"] > 0.0
        assert analytics["accessibility_compliance"]["overall_score"] > 0.0
        assert analytics["therapeutic_alignment"]["overall_score"] > 0.0
        assert analytics["user_engagement"]["overall_score"] > 0.0

        # Validate recommendations
        assert isinstance(analytics["recommendations"], list)
        assert len(analytics["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, ui_engine, mock_accessibility_system, mock_personalization_engine, sample_user_preferences):
        """Test performance benchmarks for UI operations."""
        import time

        # Inject dependencies
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)

        user_id = "performance_benchmark_user"

        # Test configuration creation performance
        start_time = time.perf_counter()

        await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.DESKTOP,
            preferences=sample_user_preferences
        )

        config_time = (time.perf_counter() - start_time) * 1000
        assert config_time < 100.0  # Should be under 100ms

        # Test layout adaptation performance
        start_time = time.perf_counter()

        await ui_engine.adapt_interface_layout(
            user_id=user_id,
            layout_context={"screen_size": {"width": 1920, "height": 1080}},
            adaptation_trigger=AdaptationTrigger.USER_PREFERENCE
        )

        layout_time = (time.perf_counter() - start_time) * 1000
        assert layout_time < 100.0  # Should be under 100ms

        # Test component generation performance
        start_time = time.perf_counter()

        await ui_engine.generate_responsive_component(
            component_type="therapeutic_session_card",
            user_id=user_id,
            component_context={"name": "Session Card"}
        )

        component_time = (time.perf_counter() - start_time) * 1000
        assert component_time < 50.0  # Should be under 50ms

        # Test theme customization performance
        start_time = time.perf_counter()

        await ui_engine.customize_interface_theme(
            user_id=user_id,
            theme_preferences={"theme": "dark", "colors": {"primary": "#ff0000"}}
        )

        theme_time = (time.perf_counter() - start_time) * 1000
        assert theme_time < 50.0  # Should be under 50ms

        # Test analytics generation performance
        start_time = time.perf_counter()

        await ui_engine.get_interface_analytics(user_id)

        analytics_time = (time.perf_counter() - start_time) * 1000
        assert analytics_time < 200.0  # Should be under 200ms

    @pytest.mark.asyncio
    async def test_ui_engine_interface_compatibility(self, ui_engine, mock_accessibility_system, mock_personalization_engine, mock_therapeutic_systems, sample_user_preferences):
        """Test compatibility with UI engine interface expectations."""
        # Inject all dependencies
        ui_engine.inject_accessibility_system(mock_accessibility_system)
        ui_engine.inject_personalization_engine(mock_personalization_engine)
        ui_engine.inject_therapeutic_systems(**mock_therapeutic_systems)
        ui_engine.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(),
            cloud_deployment_manager=AsyncMock()
        )

        user_id = "interface_compatibility_user"

        # Test complete UI workflow
        config = await ui_engine.create_interface_configuration(
            user_id=user_id,
            device_type=DeviceType.DESKTOP,
            preferences=sample_user_preferences
        )

        # Should match expected configuration structure
        assert hasattr(config, "config_id")
        assert hasattr(config, "user_id")
        assert hasattr(config, "theme")
        assert hasattr(config, "layout_type")
        assert hasattr(config, "device_type")
        assert hasattr(config, "interaction_modes")
        assert hasattr(config, "accessibility_enabled")
        assert hasattr(config, "therapeutic_focus_areas")

        # Test layout adaptation
        layout = await ui_engine.adapt_interface_layout(
            user_id=user_id,
            layout_context={"therapeutic_session": "active"},
            adaptation_trigger=AdaptationTrigger.THERAPEUTIC_PROGRESS
        )

        # Should match expected layout structure
        assert hasattr(layout, "layout_id")
        assert hasattr(layout, "user_id")
        assert hasattr(layout, "components")
        assert hasattr(layout, "layout_grid")
        assert hasattr(layout, "breakpoints")
        assert hasattr(layout, "therapeutic_flow")

        # Test component generation
        component = await ui_engine.generate_responsive_component(
            component_type="button",
            user_id=user_id,
            component_context={"name": "Test Component"}
        )

        # Should match expected component structure
        assert hasattr(component, "component_id")
        assert hasattr(component, "component_type")
        assert hasattr(component, "properties")
        assert hasattr(component, "styles")
        assert hasattr(component, "accessibility_attributes")
        assert hasattr(component, "therapeutic_context")

        # Test health check
        health_check = await ui_engine.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "interface_status" in health_check
        assert "total_interface_configurations" in health_check
        assert "ui_metrics" in health_check
        assert "system_integrations" in health_check
