from typing import Any

from pydantic import BaseModel, Field


class IntentSchema(BaseModel):
    """Pydantic schema for IPA output."""

    intent: str = Field(
        description="Player's intent (look, move, examine, talk to, quit, unknown)"
    )
    direction: str | None = Field(
        description="Direction of movement (north, south, east, west)", default=None
    )
    object: str | None = Field(description="Object to examine", default=None)
    npc: str | None = Field(description="NPC to talk to", default=None)
    object_details: dict[str, Any] | None = Field(
        description="Details of the examined object from KG", default=None
    )
    npc_details: dict[str, Any] | None = Field(
        description="Details of the NPC from KG", default=None
    )

    def to_json(self) -> str:
        """Returns the schema as a JSON string."""
        return self.json()

    @classmethod
    def from_json(cls, json_str: str) -> "IntentSchema":
        """Parses a JSON string and returns an IntentSchema object."""
        return cls.parse_raw(json_str)


class QueryKnowledgeGraphInput(BaseModel):
    """Pydantic schema for input to knowledge graph queries."""

    query_type: str = Field(
        description="Type of query to execute (e.g., retrieve_entity_by_name)"
    )
    entity_label: str = Field(
        description="Label of the entity to query (e.g., Item, Character)"
    )
    entity_name: str = Field(description="Name of the entity to query")
    properties: list[str] | None = Field(
        description="List of properties to retrieve for the entity", default=None
    )
    query_template: str | None = Field(
        description="Cypher query string (optional, generated internally)", default=None
    )  # Added query field
    params_config: dict[str, Any] | None = Field(
        description="Parameters for the Cypher query", default=None
    )  # Added params field

    @property
    def query(self) -> str:
        """Dynamically generates the Cypher query based on input fields."""
        if self.query_type == "retrieve_entity_by_name":
            property_str = (
                ", ".join([f"o.{prop} AS {prop}" for prop in self.properties])
                if self.properties
                else "*"
            )
            return f"""
                MATCH (o:`{self.entity_label}` {{name: $entity_name}})
                RETURN {property_str}
                LIMIT 1
            """
        else:
            raise ValueError(f"Unsupported query_type: {self.query_type}")

    @property
    def params(self) -> dict[str, Any]:
        """Returns the parameters for the Cypher query."""
        return {"entity_name": self.entity_name}


class QueryKnowledgeGraphOutput(BaseModel):
    """Pydantic schema for output from knowledge graph queries."""

    entity_data: dict[str, Any] = Field(
        description="Dictionary containing entity data from the knowledge graph"
    )

    @classmethod
    def parse_neo4j_output(
        cls, neo4j_results: list[dict[str, Any]]
    ) -> list["QueryKnowledgeGraphOutput"]:
        """
        Parses the raw output from Neo4j (list of dictionaries) into a list of QueryKnowledgeGraphOutput objects.
        Handles cases where properties are returned with node labels as prefixes (e.g., 'o.name').
        """
        output_list: list[QueryKnowledgeGraphOutput] = []
        for result_row in neo4j_results:
            entity_data = {}
            for key, value in result_row.items():
                # Remove node label prefix if present (e.g., 'o.')
                prop_name = key.split(".")[-1]
                entity_data[prop_name] = value
            output_list.append(cls(entity_data=entity_data))
        return output_list
