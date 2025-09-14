"""
Therapeutic Tool Registry for MCP Integration

This module provides a registry system for therapeutic tools that can be
discovered and used by MCP servers and external clients.

Classes:
    ToolRegistry: Registry for therapeutic tools
    ToolDiscovery: Tool discovery and registration mechanisms
"""

import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .therapeutic_tools import TherapeuticTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolRegistration:
    """Registration information for a therapeutic tool."""
    tool_name: str
    tool_class: str
    description: str
    capabilities: list[str]
    mcp_endpoints: list[str]
    version: str
    author: str
    registration_date: datetime
    last_updated: datetime
    usage_count: int = 0
    success_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["registration_date"] = self.registration_date.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data


class ToolRegistry:
    """
    Registry for therapeutic tools and their MCP integrations.

    This class manages the registration, discovery, and metadata
    of therapeutic tools available through MCP servers.
    """

    def __init__(self, registry_file: Path | None = None):
        """
        Initialize the tool registry.

        Args:
            registry_file: Path to the registry file for persistence
        """
        self.registry_file = registry_file or Path(__file__).parent / "tool_registry.json"
        self.registrations: dict[str, ToolRegistration] = {}
        self.tool_factories: dict[str, Callable[[], TherapeuticTool]] = {}

        # Load existing registrations
        self._load_registry()

        # Register default tools
        self._register_default_tools()

        logger.info(f"ToolRegistry initialized with {len(self.registrations)} tools")

    def _load_registry(self):
        """Load tool registrations from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file) as f:
                    data = json.load(f)

                for tool_name, tool_data in data.items():
                    # Convert datetime strings back to datetime objects
                    tool_data["registration_date"] = datetime.fromisoformat(tool_data["registration_date"])
                    tool_data["last_updated"] = datetime.fromisoformat(tool_data["last_updated"])

                    self.registrations[tool_name] = ToolRegistration(**tool_data)

                logger.info(f"Loaded {len(self.registrations)} tool registrations from {self.registry_file}")

            except Exception as e:
                logger.error(f"Error loading tool registry: {e}")

    def _save_registry(self):
        """Save tool registrations to file."""
        try:
            # Convert registrations to serializable format
            data = {name: reg.to_dict() for name, reg in self.registrations.items()}

            # Ensure directory exists
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved tool registry to {self.registry_file}")

        except Exception as e:
            logger.error(f"Error saving tool registry: {e}")

    def _register_default_tools(self):
        """Register default therapeutic tools."""
        from .therapeutic_tools import CopingStrategyGenerator, EmotionalStateAnalyzer

        # Register emotional state analyzer
        self.register_tool_factory(
            "emotional_state_analyzer",
            EmotionalStateAnalyzer,
            capabilities=["emotional_analysis", "pattern_detection", "mood_tracking"],
            mcp_endpoints=["analyze_emotional_state"],
            description="Analyzes user emotional state from text input and narrative choices",
            version="1.0.0",
            author="TTA Therapeutic Team"
        )

        # Register coping strategy generator
        self.register_tool_factory(
            "coping_strategy_generator",
            CopingStrategyGenerator,
            capabilities=["strategy_generation", "personalization", "narrative_integration"],
            mcp_endpoints=["generate_coping_strategies"],
            description="Generates personalized coping strategies based on emotional state and context",
            version="1.0.0",
            author="TTA Therapeutic Team"
        )

    def register_tool_factory(
        self,
        tool_name: str,
        tool_class: type,
        capabilities: list[str],
        mcp_endpoints: list[str],
        description: str,
        version: str = "1.0.0",
        author: str = "Unknown"
    ) -> bool:
        """
        Register a tool factory for creating therapeutic tools.

        Args:
            tool_name: Name of the tool
            tool_class: Class that implements the tool
            capabilities: List of capabilities the tool provides
            mcp_endpoints: List of MCP endpoints that expose this tool
            description: Description of the tool
            version: Version of the tool
            author: Author of the tool

        Returns:
            bool: True if registration was successful
        """
        try:
            # Create tool factory
            def tool_factory():
                return tool_class()

            self.tool_factories[tool_name] = tool_factory

            # Create or update registration
            now = datetime.now()

            if tool_name in self.registrations:
                # Update existing registration
                registration = self.registrations[tool_name]
                registration.description = description
                registration.capabilities = capabilities
                registration.mcp_endpoints = mcp_endpoints
                registration.version = version
                registration.author = author
                registration.last_updated = now
            else:
                # Create new registration
                registration = ToolRegistration(
                    tool_name=tool_name,
                    tool_class=tool_class.__name__,
                    description=description,
                    capabilities=capabilities,
                    mcp_endpoints=mcp_endpoints,
                    version=version,
                    author=author,
                    registration_date=now,
                    last_updated=now
                )
                self.registrations[tool_name] = registration

            # Save registry
            self._save_registry()

            logger.info(f"Registered therapeutic tool: {tool_name}")
            return True

        except Exception as e:
            logger.error(f"Error registering tool {tool_name}: {e}")
            return False

    def get_tool_registration(self, tool_name: str) -> ToolRegistration | None:
        """
        Get registration information for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Optional[ToolRegistration]: Registration if found, None otherwise
        """
        return self.registrations.get(tool_name)

    def list_registered_tools(self) -> list[ToolRegistration]:
        """
        List all registered tools.

        Returns:
            List[ToolRegistration]: List of all tool registrations
        """
        return list(self.registrations.values())

    def create_tool_instance(self, tool_name: str) -> TherapeuticTool | None:
        """
        Create an instance of a registered tool.

        Args:
            tool_name: Name of the tool to create

        Returns:
            Optional[TherapeuticTool]: Tool instance if successful, None otherwise
        """
        if tool_name not in self.tool_factories:
            logger.error(f"Tool factory not found for {tool_name}")
            return None

        try:
            tool_instance = self.tool_factories[tool_name]()
            logger.debug(f"Created instance of tool: {tool_name}")
            return tool_instance
        except Exception as e:
            logger.error(f"Error creating tool instance {tool_name}: {e}")
            return None

    def update_tool_usage(self, tool_name: str, success: bool):
        """
        Update usage statistics for a tool.

        Args:
            tool_name: Name of the tool
            success: Whether the tool usage was successful
        """
        if tool_name not in self.registrations:
            return

        registration = self.registrations[tool_name]
        registration.usage_count += 1

        # Update success rate
        if registration.usage_count == 1:
            registration.success_rate = 1.0 if success else 0.0
        else:
            # Calculate running average
            old_successes = registration.success_rate * (registration.usage_count - 1)
            new_successes = old_successes + (1 if success else 0)
            registration.success_rate = new_successes / registration.usage_count

        registration.last_updated = datetime.now()

        # Save updated registry
        self._save_registry()

    def search_tools_by_capability(self, capability: str) -> list[ToolRegistration]:
        """
        Search for tools by capability.

        Args:
            capability: Capability to search for

        Returns:
            List[ToolRegistration]: List of tools with the specified capability
        """
        matching_tools = []

        for registration in self.registrations.values():
            if capability.lower() in [cap.lower() for cap in registration.capabilities]:
                matching_tools.append(registration)

        return matching_tools

    def get_mcp_endpoint_mapping(self) -> dict[str, str]:
        """
        Get mapping of MCP endpoints to tool names.

        Returns:
            Dict[str, str]: Mapping of endpoint names to tool names
        """
        endpoint_mapping = {}

        for tool_name, registration in self.registrations.items():
            for endpoint in registration.mcp_endpoints:
                endpoint_mapping[endpoint] = tool_name

        return endpoint_mapping

    def generate_tool_documentation(self) -> dict[str, Any]:
        """
        Generate comprehensive documentation for all registered tools.

        Returns:
            Dict[str, Any]: Documentation data
        """
        documentation = {
            "registry_info": {
                "total_tools": len(self.registrations),
                "registry_file": str(self.registry_file),
                "last_updated": max(
                    (reg.last_updated for reg in self.registrations.values()),
                    default=datetime.now()
                ).isoformat()
            },
            "tools": {},
            "capabilities": {},
            "mcp_endpoints": {}
        }

        # Document each tool
        for tool_name, registration in self.registrations.items():
            documentation["tools"][tool_name] = {
                "description": registration.description,
                "capabilities": registration.capabilities,
                "mcp_endpoints": registration.mcp_endpoints,
                "version": registration.version,
                "author": registration.author,
                "usage_stats": {
                    "usage_count": registration.usage_count,
                    "success_rate": registration.success_rate
                },
                "registration_date": registration.registration_date.isoformat(),
                "last_updated": registration.last_updated.isoformat()
            }

        # Group tools by capability
        for registration in self.registrations.values():
            for capability in registration.capabilities:
                if capability not in documentation["capabilities"]:
                    documentation["capabilities"][capability] = []
                documentation["capabilities"][capability].append(registration.tool_name)

        # Map MCP endpoints
        documentation["mcp_endpoints"] = self.get_mcp_endpoint_mapping()

        return documentation


class ToolDiscovery:
    """
    Tool discovery and auto-registration mechanisms.

    This class provides mechanisms for automatically discovering
    and registering therapeutic tools from various sources.
    """

    def __init__(self, registry: ToolRegistry):
        """
        Initialize tool discovery.

        Args:
            registry: Tool registry to register discovered tools
        """
        self.registry = registry
        logger.info("ToolDiscovery initialized")

    def discover_tools_in_module(self, module_path: str) -> list[str]:
        """
        Discover therapeutic tools in a Python module.

        Args:
            module_path: Path to the module to scan

        Returns:
            List[str]: List of discovered tool names
        """
        discovered_tools = []

        try:
            import importlib.util
            import inspect

            # Load the module
            spec = importlib.util.spec_from_file_location("discovery_module", module_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load module from {module_path}")
                return discovered_tools

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find TherapeuticTool subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, TherapeuticTool) and
                    obj is not TherapeuticTool and
                    hasattr(obj, '__module__') and
                    obj.__module__ == module.__name__):

                    # Auto-register the tool
                    tool_name = name.lower().replace('therapeutictool', '').replace('tool', '')
                    if not tool_name:
                        tool_name = name.lower()

                    # Try to get tool metadata
                    description = getattr(obj, '__doc__', f"Therapeutic tool: {name}")
                    capabilities = getattr(obj, 'CAPABILITIES', ['general_therapy'])
                    mcp_endpoints = getattr(obj, 'MCP_ENDPOINTS', [tool_name])
                    version = getattr(obj, 'VERSION', '1.0.0')
                    author = getattr(obj, 'AUTHOR', 'Auto-discovered')

                    # Register the tool
                    success = self.registry.register_tool_factory(
                        tool_name=tool_name,
                        tool_class=obj,
                        capabilities=capabilities,
                        mcp_endpoints=mcp_endpoints,
                        description=description.strip() if description else f"Therapeutic tool: {name}",
                        version=version,
                        author=author
                    )

                    if success:
                        discovered_tools.append(tool_name)
                        logger.info(f"Auto-registered tool: {tool_name} from {name}")

        except Exception as e:
            logger.error(f"Error discovering tools in {module_path}: {e}")

        return discovered_tools

    def discover_tools_in_directory(self, directory_path: Path) -> list[str]:
        """
        Discover therapeutic tools in a directory.

        Args:
            directory_path: Path to the directory to scan

        Returns:
            List[str]: List of discovered tool names
        """
        discovered_tools = []

        if not directory_path.exists() or not directory_path.is_dir():
            logger.warning(f"Directory not found: {directory_path}")
            return discovered_tools

        # Scan Python files in the directory
        for python_file in directory_path.glob("*.py"):
            if python_file.name.startswith("__"):
                continue

            tools_in_file = self.discover_tools_in_module(str(python_file))
            discovered_tools.extend(tools_in_file)

        logger.info(f"Discovered {len(discovered_tools)} tools in {directory_path}")
        return discovered_tools

    def auto_register_core_tools(self) -> list[str]:
        """
        Auto-register core therapeutic tools.

        Returns:
            List[str]: List of registered tool names
        """
        # Get the therapeutic tools module directory
        tools_dir = Path(__file__).parent

        # Discover tools in the current directory
        discovered_tools = self.discover_tools_in_directory(tools_dir)

        logger.info(f"Auto-registered {len(discovered_tools)} core therapeutic tools")
        return discovered_tools


# Singleton instances
_TOOL_REGISTRY = None
_TOOL_DISCOVERY = None

def get_tool_registry() -> ToolRegistry:
    """
    Get the singleton instance of the ToolRegistry.

    Returns:
        ToolRegistry: Singleton instance
    """
    global _TOOL_REGISTRY
    if _TOOL_REGISTRY is None:
        _TOOL_REGISTRY = ToolRegistry()
    return _TOOL_REGISTRY

def get_tool_discovery() -> ToolDiscovery:
    """
    Get the singleton instance of the ToolDiscovery.

    Returns:
        ToolDiscovery: Singleton instance
    """
    global _TOOL_DISCOVERY
    if _TOOL_DISCOVERY is None:
        registry = get_tool_registry()
        _TOOL_DISCOVERY = ToolDiscovery(registry)
    return _TOOL_DISCOVERY
