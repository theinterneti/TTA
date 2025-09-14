#!/usr/bin/env python3
"""
Agent Adapter Example (PRODUCTION READY AFTER CUSTOMIZATION)

This example demonstrates how to use the AgentMCPAdapter to expose a TTA agent
as an MCP server.

NOTE: This example is designed for production or prototype use after customization.
You should customize it for your specific agents before using it in production.
"""

import sys

# Add the project root to the Python path
sys.path.append('/app')

from src.agents.dynamic_agents import WorldBuildingAgent
from src.mcp.agent_adapter import create_agent_mcp_server


def main():
    """
    Main function to demonstrate the AgentMCPAdapter.
    """
    # Create a sample agent
    # In a real implementation, you would use your actual agent
    agent = WorldBuildingAgent(
        neo4j_manager=None,  # You would provide your actual Neo4j manager
        tools=None,  # You would provide your actual tools
        tools_llm_model="Qwen/Qwen2.5-0.5B-Instruct",
        narrative_llm_model="Qwen/Qwen2.5-0.5B-Instruct"
    )

    # Create an MCP server for the agent
    adapter = create_agent_mcp_server(
        agent=agent,
        server_name="World Building MCP Server",
        server_description="MCP server for the World Building Agent",
        dependencies=["fastmcp", "neo4j"]
    )

    # Run the MCP server
    adapter.run()

if __name__ == "__main__":
    main()
