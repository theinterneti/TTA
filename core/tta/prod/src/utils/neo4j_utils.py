"""
Neo4j utilities for TTA system.

This module provides Neo4j database connection and query utilities.
"""

import os
from typing import Any

# Neo4j connection configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    from langchain.tools import Tool
    from langchain_community.graphs import Neo4jGraph
    from neo4j import GraphDatabase

    # Initialize Neo4j graph connection
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
except ImportError:
    # Fallback for environments without Neo4j dependencies
    graph = None
    Tool = None


def execute_query(
    query: str, params: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """
    Executes a Cypher query against the Neo4j database and returns a list of dictionaries.

    This function is designed to return structured data suitable for use by the IPA
    and other agents in the TTA game. It handles potential errors and returns an empty
    list if the query fails.

    Args:
        query: The Cypher query string to execute.
        params: An optional dictionary of parameters to pass to the query.

    Returns:
        A list of dictionaries, where each dictionary represents a row in the query result.
        Keys of the dictionary are the column names from the Cypher query.
        Returns an empty list if there are no results or if an error occurs.
    """
    if graph is None:
        print("Neo4j graph connection not available")
        return []

    try:
        result = graph.query(query, params or {})
        # Ensure we return the correct type
        if isinstance(result, list):
            return result
        return []
    except Exception as e:
        print(f"Error executing query: {e}")
        return []


def run_cypher_query(query: str) -> str:
    """
    Runs a Cypher query against the Neo4j database and returns the raw string output.

    This function is primarily intended for use as a Langchain Tool, where string output
    is often required for agent interaction. For structured data, use `execute_query`.

    Args:
        query: The Cypher query string to execute.

    Returns:
        A string representation of the query result. Returns an error message string
        if the query fails.
    """
    try:
        result = graph.query(query)
        return str(result)  # Convert to string for Langchain Tool compatibility
    except Exception as e:
        return f"Error executing query: {e}"


# Create Neo4j tool if Tool class is available
neo4j_tool = None
if Tool is not None:
    neo4j_tool = Tool(
        name="Neo4j Cypher Query",
        func=run_cypher_query,
        description="Useful for executing Cypher queries against the Neo4j database. "
        "Input should be a valid Cypher query. Output is a string representing the query results.",
    )

if __name__ == "__main__":
    # Example Usage (for testing tools.py independently)
    example_query = """
    MATCH (n:Concept)
    WHERE n.name = 'Justice'
    RETURN n.name AS concept_name, n.definition AS concept_definition
    """

    results = execute_query(example_query)
    print("Structured Query Results (execute_query):")
    if results:
        for row in results:
            print(row)
    else:
        print("No results or error occurred with execute_query.")

    raw_output = run_cypher_query(example_query)
    print("\nRaw Query Output (run_cypher_query):")
    print(raw_output)
