"""
Simple Neo4j Integration Tests

Basic tests to verify Neo4j integration is working correctly.
"""

import pytest
from datetime import datetime

from src.components.gameplay_loop.database.schema import GraphSchema, NodeType, RelationshipType
from src.components.gameplay_loop.models.core import GameplaySession, GameplayState


@pytest.mark.neo4j
def test_graph_schema_creation():
    """Test that graph schema can be created."""
    constraints = GraphSchema.get_node_constraints()
    indexes = GraphSchema.get_node_indexes()
    
    assert len(constraints) > 0
    assert len(indexes) > 0
    
    # Check that we have constraints for key node types
    constraint_text = " ".join(constraints)
    assert "Session" in constraint_text
    assert "User" in constraint_text
    assert "Scene" in constraint_text


@pytest.mark.neo4j
def test_node_types_enum():
    """Test NodeType enum values."""
    assert NodeType.SESSION == "Session"
    assert NodeType.USER == "User"
    assert NodeType.SCENE == "Scene"
    assert NodeType.CHOICE == "Choice"


@pytest.mark.neo4j
def test_relationship_types_enum():
    """Test RelationshipType enum values."""
    assert RelationshipType.HAS_SESSION == "HAS_SESSION"
    assert RelationshipType.LEADS_TO == "LEADS_TO"
    assert RelationshipType.MADE_CHOICE == "MADE_CHOICE"


@pytest.mark.neo4j
def test_gameplay_session_model():
    """Test GameplaySession model creation."""
    session = GameplaySession(
        user_id="test_user",
        therapeutic_goals=["anxiety_management"],
        safety_level="standard"
    )
    
    assert session.user_id == "test_user"
    assert session.session_state == GameplayState.INITIALIZING
    assert len(session.therapeutic_goals) == 1
    assert session.safety_level == "standard"
    assert session.session_id is not None
    assert session.created_at is not None


@pytest.mark.neo4j
def test_schema_statements_format():
    """Test that schema statements are properly formatted."""
    statements = GraphSchema.get_all_schema_statements()
    
    for statement in statements:
        if statement.strip() and not statement.startswith("//"):
            # Should be valid Cypher syntax
            assert "CREATE" in statement.upper() or "DROP" in statement.upper()
            assert statement.strip().endswith(")") or "IF NOT EXISTS" in statement or "IF EXISTS" in statement


@pytest.mark.neo4j
def test_node_properties_definition():
    """Test node properties are properly defined."""
    session_props = GraphSchema.NODE_PROPERTIES.get(NodeType.SESSION)
    
    assert session_props is not None
    assert "session_id" in session_props.required
    assert "user_id" in session_props.required
    assert "session_id" in session_props.unique
    assert "session_id" in session_props.indexed


@pytest.mark.neo4j
def test_relationship_properties_definition():
    """Test relationship properties are properly defined."""
    leads_to_props = GraphSchema.RELATIONSHIP_PROPERTIES.get(RelationshipType.LEADS_TO)
    
    assert leads_to_props is not None
    assert "created_at" in leads_to_props.required
    assert "created_at" in leads_to_props.indexed
