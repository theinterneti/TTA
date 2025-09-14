#!/usr/bin/env python3
"""
Example script for dynamic knowledge graph generation.

This script demonstrates how to use the dynamic knowledge graph generation
to extract entities and relationships from text and update the Neo4j database.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the knowledge graph components
from src.knowledge import (
    get_dynamic_graph_manager,
    get_graph_visualizer,
    get_neo4j_manager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def extract_from_text(text: str) -> None:
    """
    Extract entities and relationships from text and update the Neo4j database.

    Args:
        text: Text to process
    """
    # Get the dynamic graph manager
    graph_manager = get_dynamic_graph_manager()

    # Process the text
    logger.info("Processing text...")
    result = await graph_manager.process_text(text)

    # Print the results
    logger.info("Extraction complete!")

    # Print entities
    for entity_type, entities in result["entities"].items():
        logger.info(f"Extracted {len(entities)} {entity_type} entities")
        for entity in entities:
            logger.info(f"  - {entity['properties'].get('name', entity['id'])}")

    # Print relationships
    for relationship_type, relationships in result["relationships"].items():
        logger.info(f"Extracted {len(relationships)} {relationship_type} relationships")
        for relationship in relationships:
            source_id = relationship["source_id"]
            target_id = relationship["target_id"]
            logger.info(f"  - {source_id} -> {target_id}")


async def analyze_and_extract(text: str) -> None:
    """
    Analyze text to determine what to extract and update the Neo4j database.

    Args:
        text: Text to process
    """
    # Get the dynamic graph manager
    graph_manager = get_dynamic_graph_manager()

    # Analyze the text
    logger.info("Analyzing text...")
    result = await graph_manager.analyze_text_for_graph_updates(text)

    # Print the analysis
    logger.info("Analysis complete!")

    if "analysis" in result:
        analysis = result["analysis"]

        # Print entity types
        entity_types = analysis.get("entity_types", [])
        logger.info(f"Identified {len(entity_types)} entity types to extract:")
        for item in entity_types:
            logger.info(f"  - {item['type']}: {item['reason']}")

        # Print relationship types
        relationship_types = analysis.get("relationship_types", [])
        logger.info(f"Identified {len(relationship_types)} relationship types to extract:")
        for item in relationship_types:
            logger.info(f"  - {item['type']}: {item['reason']}")

    # Print extraction results
    logger.info("Extraction complete!")

    # Print entities
    for entity_type, entities in result.get("entities", {}).items():
        logger.info(f"Extracted {len(entities)} {entity_type} entities")
        for entity in entities:
            logger.info(f"  - {entity['properties'].get('name', entity['id'])}")

    # Print relationships
    for relationship_type, relationships in result.get("relationships", {}).items():
        logger.info(f"Extracted {len(relationships)} {relationship_type} relationships")
        for relationship in relationships:
            source_id = relationship["source_id"]
            target_id = relationship["target_id"]
            logger.info(f"  - {source_id} -> {target_id}")


async def visualize_graph() -> None:
    """Visualize the knowledge graph."""
    # Get the graph visualizer
    visualizer = get_graph_visualizer()

    # Visualize the full graph
    logger.info("Generating visualization...")
    output_file = visualizer.visualize_full_graph(limit=100)

    logger.info(f"Visualization saved to {output_file}")


async def main() -> None:
    """Main function."""
    # Sample text for extraction
    sample_text = """
    The Enchanted Forest is a mystical location filled with ancient trees and magical creatures.
    It has a peaceful atmosphere and serves as a place for reflection and mindfulness.

    At the edge of the forest, there's a small clearing called the Meditation Glade.
    This serene spot has a small pond and is perfect for quiet contemplation.

    The Wise Elder is an elderly character who lives in a small cottage near the Meditation Glade.
    He is known for his wisdom and patience, and he often guides visitors through mindfulness exercises.

    The Elder carries a Reflective Journal, which is a special item that helps users process their emotions.
    The journal has magical properties that make writing in it especially therapeutic.

    There's a path leading from the Meditation Glade to the Crystal Cave, which is a location deep in the forest.
    The cave is filled with glowing crystals and has a calming energy that helps with anxiety reduction.

    A young woman named Maya frequently visits the Meditation Glade. She knows the Wise Elder well and trusts him deeply.
    Maya is working on a quest called "Path to Mindfulness" which involves practicing mindfulness in different locations.

    The Wise Elder has assigned this quest to Maya and is tracking her progress. So far, she has completed about one-third of the exercises.

    Maya carries a Worry Stone, a small item that she can hold when feeling anxious. The stone was given to her by the Elder.

    Maya has a memory of her first successful meditation session in the glade, which was a significant positive experience for her.
    The Elder helped her recall this memory during a recent session when she was feeling discouraged.
    """

    # Check if Neo4j is available
    neo4j_manager = get_neo4j_manager()
    if neo4j_manager._using_mock_db:
        logger.warning("Neo4j is not available. Using mock database.")

    # Clear the database
    logger.info("Clearing the database...")
    neo4j_manager.clear_database()

    # Extract from text
    await extract_from_text(sample_text)

    # Visualize the graph
    await visualize_graph()

    # Try the analysis approach with a new text
    new_text = """
    The Mountain Retreat is a secluded location high in the mountains, offering breathtaking views and crisp, clean air.
    It has a rejuvenating atmosphere and serves as a place for building confidence and overcoming fears.

    Near the summit, there's an open area called the Courage Plateau where visitors can face their fears of heights in a safe environment.

    Coach Alex is an experienced mountain guide who specializes in helping people overcome their anxieties.
    He is energetic, supportive, and has a knack for knowing when to push and when to step back.

    Alex carries a Safety Rope, which is both a practical tool and a symbol of the support that's always available.

    There's a challenging path from the Courage Plateau to the Inner Sanctuary, a sheltered cave-like space where visitors can reflect on their achievements.

    A man named Thomas is currently working with Coach Alex on a quest called "Heights of Courage" to overcome his fear of heights.

    Thomas has a vivid memory of freezing on a ladder as a child, which is the root of his fear. Alex has helped him process this memory.

    Thomas carries a Achievement Medal that he earned after his first successful climb to the Courage Plateau.
    """

    # Analyze and extract from the new text
    await analyze_and_extract(new_text)

    # Visualize the updated graph
    await visualize_graph()


if __name__ == "__main__":
    asyncio.run(main())
