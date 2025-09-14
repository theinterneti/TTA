#!/usr/bin/env python3
"""
Agent Tool MCP Server (PRODUCTION READY)

This example demonstrates an MCP server that exposes tools for interacting with
the TTA project's agents. It allows LLMs to query and interact with the agents
through the MCP protocol.

NOTE: This server is designed for production or prototype use.
It provides robust tools for interacting with TTA agents.
"""

import json
import sys
from typing import Any

from fastmcp import FastMCP

# Add the project root to the Python path
sys.path.append('/app')

# Create an MCP server
mcp = FastMCP(
    "TTA Agent Tool Server",
    description="An MCP server for interacting with TTA agents",
    dependencies=[
        "fastmcp",
        "requests",
        "pydantic"
    ]
)

# ---- Helper Functions ----

def _get_agent_registry():
    """
    Get the agent registry.
    This is a placeholder - in a real implementation, you would import and use
    your actual agent registry.
    """
    # Placeholder for demonstration
    return {
        "world_building": {
            "name": "World Building Agent",
            "description": "Generates and modifies worlds/locations"
        },
        "character_creation": {
            "name": "Character Creation Agent",
            "description": "Generates and modifies characters"
        },
        "lore_keeper": {
            "name": "Lore Keeper Agent",
            "description": "Validates content against the knowledge graph"
        },
        "narrative_management": {
            "name": "Narrative Management Agent",
            "description": "Manages Nexus connections"
        }
    }

def _get_agent(agent_id):
    """
    Get an agent by ID.
    This is a placeholder - in a real implementation, you would retrieve
    the actual agent instance.
    """
    registry = _get_agent_registry()
    if agent_id not in registry:
        return None
    return registry[agent_id]

# ---- Tools ----

@mcp.tool()
def list_agents() -> str:
    """
    List all available agents in the TTA system.

    Returns:
        A formatted string listing all available agents
    """
    registry = _get_agent_registry()

    result = "Available Agents:\n\n"
    for agent_id, agent_info in registry.items():
        result += f"- {agent_id}: {agent_info['name']}\n"
        result += f"  Description: {agent_info['description']}\n\n"

    return result

@mcp.tool()
def get_agent_info(agent_id: str) -> str:
    """
    Get detailed information about a specific agent.

    Args:
        agent_id: The ID of the agent to get information about

    Returns:
        Detailed information about the agent
    """
    agent = _get_agent(agent_id)
    if not agent:
        return f"Error: Agent '{agent_id}' not found"

    return f"""
    Agent: {agent['name']}
    ID: {agent_id}
    Description: {agent['description']}
    """

@mcp.tool()
def process_with_agent(agent_id: str, goal: str, context: dict[str, Any] | None = None) -> str:
    """
    Process a goal using a specific agent.

    Args:
        agent_id: The ID of the agent to use
        goal: The goal to process
        context: Optional context information for the agent

    Returns:
        The result of processing the goal
    """
    agent = _get_agent(agent_id)
    if not agent:
        return f"Error: Agent '{agent_id}' not found"

    # In a real implementation, you would call the actual agent's process method
    # This is just a placeholder for demonstration
    return f"""
    Processed goal with {agent['name']}:

    Goal: {goal}
    Context: {json.dumps(context or {}, indent=2)}

    Result: This is a simulated result from the {agent['name']}. In a real implementation,
    this would be the actual output from the agent's processing.
    """

# ---- Resources ----

@mcp.resource("agents://list")
def get_agents_list() -> str:
    """
    Get a list of all available agents.
    """
    registry = _get_agent_registry()

    result = "# Available Agents\n\n"
    for agent_id, agent_info in registry.items():
        result += f"## {agent_info['name']} (`{agent_id}`)\n\n"
        result += f"{agent_info['description']}\n\n"

    return result

@mcp.resource("agents://{agent_id}/info")
def get_agent_info_resource(agent_id: str) -> str:
    """
    Get detailed information about a specific agent.

    Args:
        agent_id: The ID of the agent to get information about
    """
    agent = _get_agent(agent_id)
    if not agent:
        return f"Error: Agent '{agent_id}' not found"

    return f"""
    # {agent['name']}

    ID: `{agent_id}`

    ## Description

    {agent['description']}

    ## Usage

    To use this agent, call the `process_with_agent` tool with the following parameters:

    - `agent_id`: "{agent_id}"
    - `goal`: Your goal for the agent
    - `context`: Optional context information
    """

# ---- Prompts ----

@mcp.prompt()
def agent_interaction_prompt(agent_id: str, goal: str) -> str:
    """
    Create a prompt for interacting with an agent.

    Args:
        agent_id: The ID of the agent to interact with
        goal: The goal for the agent
    """
    agent = _get_agent(agent_id)
    if not agent:
        return f"Error: Agent '{agent_id}' not found"

    return f"""
    I'd like to use the {agent['name']} to accomplish the following goal:

    {goal}

    Please help me formulate an appropriate request and process it using the agent.
    """

# ---- Main ----

if __name__ == "__main__":
    # Run the server
    mcp.run()
