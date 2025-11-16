#!/usr/bin/env python3
"""
Neo4j Character Management System
Provides safe character creation methods that work with Neo4j browser interface.
"""

import uuid

from neo4j import GraphDatabase


class Neo4jCharacterManager:
    """Manages character creation and operations in Neo4j database"""

    def __init__(
        self,
        uri="bolt://localhost:7687",
        user="tta_integration",
        password="tta_integration_password_2024",
    ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

    def create_character_safe(
        self,
        name: str,
        description: str = "",
        personality_traits: list[str] = None,
        stats: dict[str, int] = None,
    ) -> str:
        """
        Create a character using Neo4j-compatible data types.
        Returns character ID.
        """
        character_id = str(uuid.uuid4())
        personality_traits = personality_traits or []

        with self.driver.session() as session:
            # Create character with primitive types only
            query = """
            CREATE (c:Character {
                id: $character_id,
                name: $name,
                description: $description,
                personality_traits: $personality_traits,
                created_at: datetime()
            })
            RETURN c.id as character_id
            """

            result = session.run(
                query,
                character_id=character_id,
                name=name,
                description=description,
                personality_traits=personality_traits,
            )

            created_id = result.single()["character_id"]

            # Add stats as separate properties (Neo4j compatible way)
            if stats:
                self._add_character_stats(session, character_id, stats)

            print(f"✅ Character created: {name} (ID: {created_id})")
            return created_id

    def _add_character_stats(self, session, character_id: str, stats: dict[str, int]):
        """Add character stats as individual properties"""
        for stat_name, stat_value in stats.items():
            # Use safe property names
            safe_stat_name = f"stat_{stat_name.lower()}"
            query = f"""
            MATCH (c:Character {{id: $character_id}})
            SET c.{safe_stat_name} = $stat_value
            """
            session.run(query, character_id=character_id, stat_value=stat_value)

    def create_character_with_relationships(
        self, name: str, description: str = "", location_name: str = None
    ) -> str:
        """Create character with location relationship"""
        character_id = str(uuid.uuid4())

        with self.driver.session() as session:
            # Create character
            char_query = """
            CREATE (c:Character {
                id: $character_id,
                name: $name,
                description: $description,
                created_at: datetime()
            })
            RETURN c.id as character_id
            """

            result = session.run(
                char_query,
                character_id=character_id,
                name=name,
                description=description,
            )

            created_id = result.single()["character_id"]

            # Create location relationship if specified
            if location_name:
                location_id = str(uuid.uuid4())
                loc_query = """
                MATCH (c:Character {id: $character_id})
                CREATE (l:Location {
                    id: $location_id,
                    name: $location_name,
                    created_at: datetime()
                })
                CREATE (c)-[:LOCATED_AT]->(l)
                RETURN l.id as location_id
                """

                session.run(
                    loc_query,
                    character_id=character_id,
                    location_id=location_id,
                    location_name=location_name,
                )

                print(f"✅ Character with location: {name} at {location_name}")

            return created_id

    def get_character(self, character_id: str) -> dict | None:
        """Retrieve character information"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Character {id: $character_id})
            OPTIONAL MATCH (c)-[:LOCATED_AT]->(l:Location)
            RETURN c.id as id, c.name as name, c.description as description,
                   c.personality_traits as personality_traits,
                   c.stat_strength as strength, c.stat_wisdom as wisdom,
                   c.stat_charisma as charisma, c.created_at as created_at,
                   l.name as location_name
            """

            result = session.run(query, character_id=character_id)
            record = result.single()

            if record:
                return {
                    "id": record["id"],
                    "name": record["name"],
                    "description": record["description"],
                    "personality_traits": record["personality_traits"],
                    "stats": {
                        "strength": record["strength"],
                        "wisdom": record["wisdom"],
                        "charisma": record["charisma"],
                    },
                    "location": record["location_name"],
                    "created_at": record["created_at"],
                }
            return None

    def list_characters(self) -> list[dict]:
        """List all characters"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Character)
            OPTIONAL MATCH (c)-[:LOCATED_AT]->(l:Location)
            RETURN c.id as id, c.name as name, c.description as description,
                   l.name as location_name
            ORDER BY c.name
            """

            result = session.run(query)
            characters = []

            for record in result:
                characters.append(
                    {
                        "id": record["id"],
                        "name": record["name"],
                        "description": record["description"],
                        "location": record["location_name"],
                    }
                )

            return characters

    def delete_character(self, character_id: str) -> bool:
        """Delete a character and its relationships"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Character {id: $character_id})
            DETACH DELETE c
            RETURN count(c) as deleted_count
            """

            result = session.run(query, character_id=character_id)
            deleted_count = result.single()["deleted_count"]

            if deleted_count > 0:
                print(f"✅ Character deleted: {character_id}")
                return True
            print(f"❌ Character not found: {character_id}")
            return False

    def get_safe_cypher_examples(self) -> list[str]:
        """Get Neo4j browser-safe Cypher examples"""
        return [
            # Basic character creation
            """CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Hero Character',
    description: 'A brave adventurer',
    personality_traits: ['brave', 'loyal', 'curious'],
    stat_strength: 15,
    stat_wisdom: 12,
    stat_charisma: 10,
    created_at: datetime()
}) RETURN c""",
            # Character with location
            """CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Village Elder',
    description: 'Wise keeper of ancient knowledge',
    personality_traits: ['wise', 'patient', 'kind'],
    stat_wisdom: 18,
    stat_charisma: 14,
    created_at: datetime()
}),
(l:Location {
    id: 'loc_' + randomUUID(),
    name: 'Ancient Library',
    description: 'A repository of forgotten lore',
    created_at: datetime()
})
CREATE (c)-[:LOCATED_AT]->(l)
RETURN c, l""",
            # Query characters
            """MATCH (c:Character)
OPTIONAL MATCH (c)-[:LOCATED_AT]->(l:Location)
RETURN c.name as name, c.description as description,
       c.personality_traits as traits, l.name as location
ORDER BY c.name""",
            # Update character
            """MATCH (c:Character {name: 'Hero Character'})
SET c.stat_strength = c.stat_strength + 1,
    c.personality_traits = c.personality_traits + ['experienced']
RETURN c""",
        ]


def main():
    """Demo the character manager"""
    manager = Neo4jCharacterManager()

    try:
        print("🎭 NEO4J CHARACTER MANAGER DEMO")
        print("=" * 50)

        # Create test characters
        char1_id = manager.create_character_safe(
            name="Brave Knight",
            description="A valiant defender of the realm",
            personality_traits=["brave", "honorable", "protective"],
            stats={"strength": 16, "wisdom": 12, "charisma": 14},
        )

        char2_id = manager.create_character_with_relationships(
            name="Wise Sage",
            description="An ancient keeper of knowledge",
            location_name="Crystal Tower",
        )

        # List characters
        print("\n📋 All Characters:")
        characters = manager.list_characters()
        for char in characters:
            print(f"  - {char['name']}: {char['description']}")
            if char["location"]:
                print(f"    Location: {char['location']}")

        # Get detailed character info
        print(f"\n🔍 Detailed info for {char1_id}:")
        char_info = manager.get_character(char1_id)
        if char_info:
            print(f"  Name: {char_info['name']}")
            print(f"  Traits: {char_info['personality_traits']}")
            print(f"  Stats: {char_info['stats']}")

        print("\n✅ Character manager demo completed successfully!")
        print("\n🔧 Safe Cypher Examples for Neo4j Browser:")
        examples = manager.get_safe_cypher_examples()
        for i, example in enumerate(examples, 1):
            print(f"\nExample {i}:")
            print(example)

    except Exception as e:
        print(f"❌ Demo failed: {e}")

    finally:
        manager.close()


if __name__ == "__main__":
    main()
