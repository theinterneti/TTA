#!/usr/bin/env python3
"""
Knowledge Resource MCP Server (PRODUCTION READY)

This example demonstrates an MCP server that exposes resources from the TTA project's
knowledge graph. It allows LLMs to query and access information from the knowledge
graph through the MCP protocol.

NOTE: This server is designed for production or prototype use.
It provides robust tools for accessing the TTA knowledge graph.
"""

import json
import sys
from typing import Any

from fastmcp import FastMCP

# Add the project root to the Python path
sys.path.append('/app')

# Create an MCP server
mcp = FastMCP(
    "TTA Knowledge Resource Server",
    description="An MCP server for accessing the TTA knowledge graph",
    dependencies=[
        "fastmcp",
        "requests",
        "neo4j"
    ]
)

# ---- Helper Functions ----

def _get_neo4j_manager():
    """
    Get the Neo4j manager.
    This is a placeholder - in a real implementation, you would import and use
    your actual Neo4j manager.
    """
    # Placeholder for demonstration
    class MockNeo4jManager:
        def query(self, query, params=None):
            # This is a mock implementation for demonstration
            if "MATCH (l:Location)" in query:
                return [
                    {"name": "The Nexus", "description": "A central hub connecting all universes"},
                    {"name": "Emerald Forest", "description": "A lush, magical forest with emerald-colored leaves"},
                    {"name": "Crystal Caverns", "description": "A network of caves filled with glowing crystals"}
                ]
            elif "MATCH (c:Character)" in query:
                return [
                    {"name": "Elara", "description": "A wise elven guide with ancient knowledge"},
                    {"name": "Thorne", "description": "A gruff but kind-hearted dwarf warrior"},
                    {"name": "Lyra", "description": "A curious human scholar seeking knowledge"}
                ]
            elif "MATCH (i:Item)" in query:
                return [
                    {"name": "Crystal Key", "description": "A key made of crystal that unlocks hidden pathways"},
                    {"name": "Healing Potion", "description": "A potion that restores health"},
                    {"name": "Ancient Tome", "description": "A book containing forgotten knowledge"}
                ]
            return []

    return MockNeo4jManager()

# ---- Tools ----

@mcp.tool()
def query_knowledge_graph(query: str, params: dict[str, Any] | None = None) -> str:
    """
    Execute a Cypher query against the knowledge graph.

    Args:
        query: The Cypher query to execute
        params: Optional parameters for the query

    Returns:
        The results of the query in a formatted string
    """
    # In a real implementation, you would validate the query for security
    # This is just a placeholder for demonstration

    # Check for dangerous operations
    dangerous_operations = ["CREATE", "DELETE", "REMOVE", "SET", "MERGE"]
    if any(op in query.upper() for op in dangerous_operations):
        return "Error: Query contains potentially dangerous operations"

    try:
        neo4j_manager = _get_neo4j_manager()
        results = neo4j_manager.query(query, params or {})

        if not results:
            return "No results found"

        # Format the results
        formatted_results = json.dumps(results, indent=2)
        return f"Query results:\n\n{formatted_results}"
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
def get_entity_by_name(entity_type: str, name: str) -> str:
    """
    Get an entity from the knowledge graph by its name.

    Args:
        entity_type: The type of entity (Location, Character, Item)
        name: The name of the entity

    Returns:
        Information about the entity
    """
    if entity_type not in ["Location", "Character", "Item"]:
        return f"Error: Invalid entity type '{entity_type}'"

    try:
        neo4j_manager = _get_neo4j_manager()
        query = f"MATCH (e:{entity_type}) WHERE e.name = $name RETURN e"
        results = neo4j_manager.query(query, {"name": name})

        if not results:
            return f"No {entity_type} found with name '{name}'"

        # Format the results
        entity = results[0]
        return f"""
        {entity_type}: {entity['name']}

        Description: {entity['description']}
        """
    except Exception as e:
        return f"Error retrieving entity: {str(e)}"

# ---- Resources ----

@mcp.resource("knowledge://locations")
def get_locations() -> str:
    """
    Get a list of all locations in the knowledge graph.
    """
    try:
        neo4j_manager = _get_neo4j_manager()
        results = neo4j_manager.query("MATCH (l:Location) RETURN l")

        if not results:
            return "No locations found"

        # Format the results
        result = "# Locations\n\n"
        for location in results:
            result += f"## {location['name']}\n\n"
            result += f"{location['description']}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving locations: {str(e)}"

@mcp.resource("knowledge://characters")
def get_characters() -> str:
    """
    Get a list of all characters in the knowledge graph.
    """
    try:
        neo4j_manager = _get_neo4j_manager()
        results = neo4j_manager.query("MATCH (c:Character) RETURN c")

        if not results:
            return "No characters found"

        # Format the results
        result = "# Characters\n\n"
        for character in results:
            result += f"## {character['name']}\n\n"
            result += f"{character['description']}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving characters: {str(e)}"

@mcp.resource("knowledge://items")
def get_items() -> str:
    """
    Get a list of all items in the knowledge graph.
    """
    try:
        neo4j_manager = _get_neo4j_manager()
        results = neo4j_manager.query("MATCH (i:Item) RETURN i")

        if not results:
            return "No items found"

        # Format the results
        result = "# Items\n\n"
        for item in results:
            result += f"## {item['name']}\n\n"
            result += f"{item['description']}\n\n"

        return result
    except Exception as e:
        return f"Error retrieving items: {str(e)}"

@mcp.resource("knowledge://{entity_type}/{name}")
def get_entity_resource(entity_type: str, name: str) -> str:
    """
    Get an entity from the knowledge graph by its type and name.

    Args:
        entity_type: The type of entity (locations, characters, items)
        name: The name of the entity
    """
    # Map plural to singular and capitalize
    entity_type_map = {
        "locations": "Location",
        "characters": "Character",
        "items": "Item"
    }

    if entity_type not in entity_type_map:
        return f"Error: Invalid entity type '{entity_type}'"

    neo4j_entity_type = entity_type_map[entity_type]

    try:
        neo4j_manager = _get_neo4j_manager()
        query = f"MATCH (e:{neo4j_entity_type}) WHERE e.name = $name RETURN e"
        results = neo4j_manager.query(query, {"name": name})

        if not results:
            return f"No {neo4j_entity_type} found with name '{name}'"

        # Format the results
        entity = results[0]
        return f"""
        # {entity['name']}

        Type: {neo4j_entity_type}

        ## Description

        {entity['description']}
        """
    except Exception as e:
        return f"Error retrieving entity: {str(e)}"

# ---- Prompts ----

@mcp.prompt()
def knowledge_query_prompt(entity_type: str) -> str:
    """
    Create a prompt for querying the knowledge graph.

    Args:
        entity_type: The type of entity to query (locations, characters, items)
    """
    return f"""
    I'd like to explore the {entity_type} in the TTA knowledge graph.

    Please help me understand what {entity_type} are available and provide details about them.
    """

# ---- Main ----

if __name__ == "__main__":
    # Run the server
    mcp.run()
