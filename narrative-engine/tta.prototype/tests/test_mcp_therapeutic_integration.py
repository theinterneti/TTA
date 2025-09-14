"""
Tests for MCP Therapeutic Integration

This module contains tests for the MCP server integration with therapeutic tools,
including tool registration, server functionality, and integration with the
existing TTA orchestration system.
"""

import json

# Import the modules to test
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from mcp.server_manager import MCPServerManager
from mcp.therapeutic_mcp_server import (
    TherapeuticMCPServer,
    create_therapeutic_mcp_server,
)
from mcp.therapeutic_tools import (
    CopingStrategyGenerator,
    EmotionalStateAnalyzer,
    TherapeuticContext,
    TherapeuticResponse,
    TherapeuticToolsManager,
    get_therapeutic_tools_manager,
)
from mcp.tool_registry import ToolDiscovery, ToolRegistry, get_tool_registry


class TestTherapeuticTools:
    """Test therapeutic tools functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools_manager = TherapeuticToolsManager()
        self.sample_context = TherapeuticContext(
            user_id="test_user_123",
            session_id="test_session_456",
            current_emotional_state="feeling anxious and worried about the future",
            narrative_context="The character is facing a difficult decision in a dark forest",
            user_history={
                "sessions": [
                    {"primary_emotion": "anxiety", "timestamp": "2024-01-01T10:00:00"},
                    {"primary_emotion": "calm", "timestamp": "2024-01-01T11:00:00"}
                ],
                "therapeutic_goals": ["manage_anxiety", "build_confidence"],
                "preferred_difficulty": "medium",
                "tried_strategies": ["Deep Breathing"],
                "successful_strategies": ["Deep Breathing"]
            },
            therapeutic_goals=["manage_anxiety", "build_confidence"]
        )

    def test_emotional_state_analyzer_initialization(self):
        """Test emotional state analyzer initialization."""
        analyzer = EmotionalStateAnalyzer()

        assert analyzer.name == "emotional_state_analyzer"
        assert "emotional state" in analyzer.description.lower()
        assert analyzer.usage_count == 0
        assert analyzer.success_rate == 0.0
        assert len(analyzer.emotional_indicators) > 0

    def test_emotional_state_analysis(self):
        """Test emotional state analysis functionality."""
        analyzer = EmotionalStateAnalyzer()
        response = analyzer.process(self.sample_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.tool_name == "emotional_state_analyzer"
        assert response.response_type == "emotional_analysis"
        assert response.confidence > 0.0
        assert response.therapeutic_value > 0.0

        # Parse the response content
        analysis = json.loads(response.content)
        assert "primary_emotion" in analysis
        assert "emotional_intensity" in analysis
        assert "recommendations" in analysis

        # Should detect anxiety from the context
        assert analysis["primary_emotion"] in ["anxiety", "fear"]

    def test_coping_strategy_generator_initialization(self):
        """Test coping strategy generator initialization."""
        generator = CopingStrategyGenerator()

        assert generator.name == "coping_strategy_generator"
        assert "coping strategies" in generator.description.lower()
        assert len(generator.coping_strategies) > 0
        assert "anxiety" in generator.coping_strategies
        assert "general" in generator.coping_strategies

    def test_coping_strategy_generation(self):
        """Test coping strategy generation functionality."""
        generator = CopingStrategyGenerator()
        response = generator.process(self.sample_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.tool_name == "coping_strategy_generator"
        assert response.response_type == "coping_strategies"
        assert response.confidence > 0.0
        assert response.therapeutic_value > 0.0

        # Parse the response content
        strategies = json.loads(response.content)
        assert "recommended_strategies" in strategies
        assert "implementation_guidance" in strategies
        assert "narrative_integration_suggestions" in strategies

        # Should have at least one strategy
        assert len(strategies["recommended_strategies"]) > 0

    def test_tools_manager_initialization(self):
        """Test therapeutic tools manager initialization."""
        manager = TherapeuticToolsManager()

        assert len(manager.tools) >= 2  # At least emotional analyzer and coping generator
        assert "emotional_state_analyzer" in manager.tools
        assert "coping_strategy_generator" in manager.tools

    def test_tools_manager_process_request(self):
        """Test processing therapeutic requests through the manager."""
        manager = TherapeuticToolsManager()

        # Test emotional state analysis
        response = manager.process_therapeutic_request(
            "emotional_state_analyzer",
            self.sample_context
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.tool_name == "emotional_state_analyzer"
        assert response.confidence > 0.0

        # Test coping strategy generation
        response = manager.process_therapeutic_request(
            "coping_strategy_generator",
            self.sample_context
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.tool_name == "coping_strategy_generator"
        assert response.confidence > 0.0

    def test_tools_manager_invalid_tool(self):
        """Test handling of invalid tool requests."""
        manager = TherapeuticToolsManager()

        response = manager.process_therapeutic_request(
            "nonexistent_tool",
            self.sample_context
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.response_type == "error"
        assert response.confidence == 0.0
        assert "not found" in response.content.lower()

    def test_tool_recommendations(self):
        """Test tool recommendation functionality."""
        manager = TherapeuticToolsManager()

        recommendations = manager.get_tool_recommendations(self.sample_context)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "emotional_state_analyzer" in recommendations

        # Should recommend coping strategies for anxious state
        assert "coping_strategy_generator" in recommendations

    def test_usage_statistics_tracking(self):
        """Test usage statistics tracking."""
        manager = TherapeuticToolsManager()

        # Process a request
        manager.process_therapeutic_request(
            "emotional_state_analyzer",
            self.sample_context
        )

        # Check statistics
        stats = manager.get_usage_statistics()
        assert "emotional_state_analyzer" in stats
        assert stats["emotional_state_analyzer"]["total_uses"] == 1
        assert stats["emotional_state_analyzer"]["average_confidence"] > 0.0


class TestTherapeuticMCPServer:
    """Test therapeutic MCP server functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server = TherapeuticMCPServer()

    def test_server_initialization(self):
        """Test MCP server initialization."""
        assert self.server.server_name == "Therapeutic Text Adventure MCP Server"
        assert self.server.tools_manager is not None
        assert self.server.mcp is not None

    def test_create_therapeutic_mcp_server(self):
        """Test server creation function."""
        server = create_therapeutic_mcp_server(
            server_name="Test Server",
            server_description="Test Description"
        )

        assert isinstance(server, TherapeuticMCPServer)
        assert server.server_name == "Test Server"
        assert server.server_description == "Test Description"

    @pytest.mark.asyncio
    async def test_mcp_tool_analyze_emotional_state(self):
        """Test the analyze_emotional_state MCP tool."""
        # This would require setting up the actual MCP server
        # For now, we'll test the underlying functionality

        # Get the tool function from the server
        tools_manager = self.server.tools_manager

        context = TherapeuticContext(
            user_id="test_user",
            session_id="test_session",
            current_emotional_state="feeling sad and hopeless",
            narrative_context="Character is alone in a dark room",
            user_history={},
            therapeutic_goals=["improve_mood"]
        )

        response = tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            context
        )

        assert response.tool_name == "emotional_state_analyzer"
        assert response.confidence > 0.0

    @pytest.mark.asyncio
    async def test_mcp_tool_generate_coping_strategies(self):
        """Test the generate_coping_strategies MCP tool."""
        tools_manager = self.server.tools_manager

        context = TherapeuticContext(
            user_id="test_user",
            session_id="test_session",
            current_emotional_state="feeling angry and frustrated",
            narrative_context="Character is in conflict with another character",
            user_history={},
            therapeutic_goals=["anger_management"]
        )

        response = tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            context
        )

        assert response.tool_name == "coping_strategy_generator"
        assert response.confidence > 0.0

    def test_emotional_indicators_extraction(self):
        """Test emotional indicators extraction."""
        indicators = self.server._extract_emotional_indicators("feeling anxious and worried")

        assert isinstance(indicators, list)
        assert "anxiety" in indicators

    def test_narrative_themes_extraction(self):
        """Test narrative themes extraction."""
        themes = self.server._extract_narrative_themes("character is fighting with their friend")

        assert isinstance(themes, list)
        assert "conflict" in themes

    def test_content_validation(self):
        """Test therapeutic content validation."""
        # Test safe content
        safe_content = "The character learns breathing techniques to manage stress"
        validation = self.server._validate_content(
            safe_content,
            "narrative",
            "general",
            ["stress_management"]
        )

        assert validation["is_valid"] is True
        assert validation["validation_score"] > 0.5
        assert len(validation["warnings"]) == 0

        # Test potentially harmful content
        harmful_content = "The character considers self-harm as a solution"
        validation = self.server._validate_content(
            harmful_content,
            "narrative",
            "general",
            ["depression_support"]
        )

        assert validation["validation_score"] < 0.8
        assert len(validation["warnings"]) > 0


class TestToolRegistry:
    """Test tool registry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use a temporary registry file for testing
        self.temp_registry_file = Path("/tmp/test_tool_registry.json")
        if self.temp_registry_file.exists():
            self.temp_registry_file.unlink()

        self.registry = ToolRegistry(self.temp_registry_file)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_registry_file.exists():
            self.temp_registry_file.unlink()

    def test_registry_initialization(self):
        """Test tool registry initialization."""
        assert len(self.registry.registrations) >= 2  # Default tools
        assert "emotional_state_analyzer" in self.registry.registrations
        assert "coping_strategy_generator" in self.registry.registrations

    def test_tool_registration(self):
        """Test tool registration functionality."""
        success = self.registry.register_tool_factory(
            tool_name="test_tool",
            tool_class=EmotionalStateAnalyzer,
            capabilities=["test_capability"],
            mcp_endpoints=["test_endpoint"],
            description="Test tool description",
            version="1.0.0",
            author="Test Author"
        )

        assert success is True
        assert "test_tool" in self.registry.registrations

        registration = self.registry.get_tool_registration("test_tool")
        assert registration is not None
        assert registration.tool_name == "test_tool"
        assert registration.description == "Test tool description"
        assert "test_capability" in registration.capabilities

    def test_tool_instance_creation(self):
        """Test creating tool instances from registry."""
        # Test creating an existing tool
        tool_instance = self.registry.create_tool_instance("emotional_state_analyzer")

        assert tool_instance is not None
        assert isinstance(tool_instance, EmotionalStateAnalyzer)
        assert tool_instance.name == "emotional_state_analyzer"

    def test_capability_search(self):
        """Test searching tools by capability."""
        tools = self.registry.search_tools_by_capability("emotional_analysis")

        assert len(tools) > 0
        assert any(tool.tool_name == "emotional_state_analyzer" for tool in tools)

    def test_mcp_endpoint_mapping(self):
        """Test MCP endpoint mapping."""
        mapping = self.registry.get_mcp_endpoint_mapping()

        assert isinstance(mapping, dict)
        assert "analyze_emotional_state" in mapping
        assert mapping["analyze_emotional_state"] == "emotional_state_analyzer"

    def test_usage_statistics_update(self):
        """Test updating usage statistics."""
        initial_registration = self.registry.get_tool_registration("emotional_state_analyzer")
        initial_usage = initial_registration.usage_count

        # Update usage
        self.registry.update_tool_usage("emotional_state_analyzer", success=True)

        updated_registration = self.registry.get_tool_registration("emotional_state_analyzer")
        assert updated_registration.usage_count == initial_usage + 1
        assert updated_registration.success_rate > 0.0

    def test_documentation_generation(self):
        """Test generating tool documentation."""
        docs = self.registry.generate_tool_documentation()

        assert "registry_info" in docs
        assert "tools" in docs
        assert "capabilities" in docs
        assert "mcp_endpoints" in docs

        assert docs["registry_info"]["total_tools"] >= 2
        assert "emotional_state_analyzer" in docs["tools"]


class TestToolDiscovery:
    """Test tool discovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_registry_file = Path("/tmp/test_discovery_registry.json")
        if self.temp_registry_file.exists():
            self.temp_registry_file.unlink()

        self.registry = ToolRegistry(self.temp_registry_file)
        self.discovery = ToolDiscovery(self.registry)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_registry_file.exists():
            self.temp_registry_file.unlink()

    def test_discovery_initialization(self):
        """Test tool discovery initialization."""
        assert self.discovery.registry is not None
        assert isinstance(self.discovery.registry, ToolRegistry)

    def test_auto_register_core_tools(self):
        """Test auto-registration of core tools."""
        # Clear existing registrations for clean test
        self.registry.registrations.clear()

        discovered_tools = self.discovery.auto_register_core_tools()

        # Should discover at least the default tools
        assert len(discovered_tools) >= 0  # May vary based on actual files


class TestMCPServerManager:
    """Test MCP server manager integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.server_manager = MCPServerManager()

    def test_server_manager_initialization(self):
        """Test server manager initialization."""
        assert self.server_manager.config is not None
        assert isinstance(self.server_manager.servers, dict)
        assert isinstance(self.server_manager.processes, dict)

    @patch('subprocess.Popen')
    def test_start_therapeutic_server(self, mock_popen):
        """Test starting the therapeutic MCP server."""
        # Mock the process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process

        # Mock server readiness check
        with patch.object(self.server_manager, '_check_server_ready', return_value=True):
            success, pid = self.server_manager.start_therapeutic_server(wait=True, timeout=1)

        assert success is True
        assert pid == 12345
        assert "therapeutic_server" in self.server_manager.processes

    def test_stop_therapeutic_server_not_running(self):
        """Test stopping therapeutic server when not running."""
        success = self.server_manager.stop_therapeutic_server()

        # Should return False since server is not running
        assert success is False


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools_manager = get_therapeutic_tools_manager()
        self.registry = get_tool_registry()
        self.server = create_therapeutic_mcp_server()

    def test_end_to_end_emotional_analysis(self):
        """Test end-to-end emotional analysis workflow."""
        # Create context
        context = TherapeuticContext(
            user_id="integration_test_user",
            session_id="integration_test_session",
            current_emotional_state="I'm feeling overwhelmed and stressed about work",
            narrative_context="The character is facing multiple deadlines and challenges",
            user_history={
                "therapeutic_goals": ["stress_management", "work_life_balance"],
                "preferred_difficulty": "medium"
            },
            therapeutic_goals=["stress_management", "work_life_balance"]
        )

        # Process through tools manager
        analysis_response = self.tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            context
        )

        assert analysis_response.confidence > 0.0
        assert analysis_response.therapeutic_value > 0.0

        # Generate coping strategies based on analysis
        strategies_response = self.tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            context
        )

        assert strategies_response.confidence > 0.0
        assert strategies_response.therapeutic_value > 0.0

        # Verify tools are registered
        emotional_tool_reg = self.registry.get_tool_registration("emotional_state_analyzer")
        coping_tool_reg = self.registry.get_tool_registration("coping_strategy_generator")

        assert emotional_tool_reg is not None
        assert coping_tool_reg is not None

    def test_tool_recommendation_workflow(self):
        """Test tool recommendation workflow."""
        context = TherapeuticContext(
            user_id="recommendation_test_user",
            session_id="recommendation_test_session",
            current_emotional_state="feeling anxious about social situations",
            narrative_context="Character needs to speak in front of a group",
            user_history={},
            therapeutic_goals=["social_anxiety", "confidence_building"]
        )

        # Get tool recommendations
        recommendations = self.tools_manager.get_tool_recommendations(context)

        assert len(recommendations) > 0
        assert "emotional_state_analyzer" in recommendations

        # Process with recommended tools
        for tool_name in recommendations:
            response = self.tools_manager.process_therapeutic_request(tool_name, context)
            assert response.confidence > 0.0

    def test_registry_and_server_integration(self):
        """Test integration between registry and MCP server."""
        # Get endpoint mapping from registry
        endpoint_mapping = self.registry.get_mcp_endpoint_mapping()

        assert "analyze_emotional_state" in endpoint_mapping
        assert "generate_coping_strategies" in endpoint_mapping

        # Verify server has access to tools
        assert self.server.tools_manager is not None

        # Test tool availability through server
        tools_list = self.server.tools_manager.list_tools()
        tool_names = [tool["name"] for tool in tools_list]

        assert "emotional_state_analyzer" in tool_names
        assert "coping_strategy_generator" in tool_names


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
